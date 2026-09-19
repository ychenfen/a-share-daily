#!/usr/bin/env python3
"""A股收盘快照。

每天收盘后抓当天行情，写入 data/<年>.csv 并刷新 README。
只用标准库，不需要 pip install。

判断交易日的方式：读上证指数行情里自带的时间戳，如果不是今天，
说明今天没开盘（周末或节假日），直接跳过写数据。不用维护节假日表。
"""

import csv
import json
import os
import ssl
import time
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone, tzinfo
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def beijing_tz():
    """返回北京时区。没有系统 tzdata 时退回固定 +08:00。

    Windows 和精简容器里没有系统时区库，ZoneInfo 会抛 ZoneInfoNotFoundError，
    本地手动补数据会直接崩在第一行。
    """
    if ZoneInfo is not None:
        try:
            return ZoneInfo("Asia/Shanghai")
        except Exception:
            pass
    return timezone(timedelta(hours=8))


# 就用最朴素的这一个。带 Macintosh/AppleWebKit 的长串反而会被东财的
# clist 接口直接 RST——那种半截 UA 看着就像爬虫伪装。
UA = "Mozilla/5.0"

# 代码 -> 显示名，顺序决定 CSV 列顺序
INDEXES = [
    ("sh000001", "上证指数"),
    ("sz399001", "深证成指"),
    ("sz399006", "创业板指"),
    ("sh000300", "沪深300"),
    ("sh000688", "科创50"),
]

CSV_HEADER = (
    ["date"]
    + [f"{name}_close" for _, name in INDEXES]
    + [f"{name}_pct" for _, name in INDEXES]
    + ["amount_yi", "up", "down", "flat",
       "limit_up", "limit_down", "broken", "broken_rate",
       "max_streak", "streak_2plus"]
)

SECTOR_CSV = "sectors.csv"
SECTOR_HEADER = ["date", "rank_type", "rank", "name", "pct", "net_inflow_yi", "leader"]
SECTOR_TOP_N = 5


# 东财对请求密度很敏感：几秒内连打五六个就开始 RST，而每次隔一秒多就没事。
# 全脚本每天只跑一次十来个请求，多花十几秒无所谓，所以统一限速。
MIN_INTERVAL = 1.3
_last_request = 0.0


def fetch(url, decode="utf-8", timeout=20):
    """取一个 URL 的文本。

    东财会对请求太密的 IP 直接 RST，表现为连接被对端关闭。curl 偶尔
    还能过，所以 urllib 失败就再用 curl 试一次；runner 和 macOS 都自带
    curl，不引入依赖。真被封了两条都会失败，调用方按缺数据处理。
    """
    global _last_request
    wait = MIN_INTERVAL - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()

    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode(decode, errors="replace")
    except (urllib.error.URLError, OSError, ssl.SSLError) as first_error:
        out = subprocess.run(
            ["curl", "-sS", "--compressed", "--max-time", str(timeout),
             "-H", f"User-Agent: {UA}", url],
            capture_output=True, timeout=timeout + 10, check=True,
        ).stdout
        # 被限流时 curl 也常是 rc=0 但空 body。不拦住的话调用方会拿到
        # 空字符串，最后报成一个和真实原因无关的 JSON 解析错误。
        if not out.strip():
            raise RuntimeError(f"urllib 失败({first_error})，curl 回落也返回空") from first_error
        return out.decode(decode, errors="replace")


def fetch_indexes():
    """返回 (行情字典, 行情自带的日期 YYYY-MM-DD)。失败返回 (None, None)。"""
    codes = ",".join(code for code, _ in INDEXES)
    # 腾讯这个接口是 GBK
    raw = fetch(f"https://qt.gtimg.cn/q={codes}", decode="gbk")

    quotes, quote_date = {}, None
    for line in raw.split(";"):
        line = line.strip()
        if not line.startswith("v_"):
            continue
        code = line[2 : line.index("=")]
        fields = line[line.index('"') + 1 : line.rindex('"')].split("~")
        if len(fields) < 38:
            continue
        try:
            quotes[code] = {
                "close": float(fields[3]),
                "pct": float(fields[32]),
                # [37] 是成交额，单位万元，转成亿
                "amount_yi": float(fields[37]) / 1e4,
            }
        except (ValueError, IndexError):
            continue
        # [30] 形如 20260918161402
        if quote_date is None and len(fields[30]) >= 8:
            d = fields[30][:8]
            quote_date = f"{d[:4]}-{d[4:6]}-{d[6:8]}"

    return (quotes, quote_date) if quotes else (None, None)


# 东财按市场聚合的涨跌平家数，一次请求拿全，不用翻几十页个股列表
BREADTH_MARKETS = ["1.000001", "0.399001", "0.899050"]  # 沪市 / 深市 / 北交所


def fetch_breadth():
    """全市场涨跌平家数。取不到返回空 dict，不影响提交。

    用东财按市场聚合好的 f104/f105/f106，一次请求覆盖沪深北三市。
    合计比全 A 总数少三百只左右，差的是停牌股——停牌本来就不该算进
    涨跌，所以这个口径反而比逐只统计更贴切。
    """
    url = (
        "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2"
        f"&secids={','.join(BREADTH_MARKETS)}&fields=f12,f104,f105,f106"
    )
    try:
        diff = json.loads(fetch(url))["data"]["diff"]
    except Exception as e:
        print(f"  涨跌家数获取失败: {e}", file=sys.stderr)
        return {}

    rows = list(diff.values()) if isinstance(diff, dict) else diff
    # 缺任何一个市场就整块放弃，免得写进一个偏小的数还看不出来
    if len(rows) != len(BREADTH_MARKETS):
        print(f"  涨跌家数不完整（{len(rows)}/{len(BREADTH_MARKETS)} 个市场）", file=sys.stderr)
        return {}

    out = {"up": 0, "down": 0, "flat": 0}
    for row in rows:
        for key, field in (("up", "f104"), ("down", "f105"), ("flat", "f106")):
            value = row.get(field)
            if not isinstance(value, (int, float)):
                print(f"  {row.get('f12')} 的 {field} 异常: {value!r}", file=sys.stderr)
                return {}
            out[key] += int(value)
    return out


def fetch_sector_page(descending):
    """按涨跌幅排序取前 SECTOR_TOP_N 个行业板块。po=1 降序，po=0 升序。"""
    url = (
        "https://push2.eastmoney.com/api/qt/clist/get"
        f"?pn=1&pz={SECTOR_TOP_N}&po={1 if descending else 0}&np=1&fltt=2&fid=f3"
        "&fs=m:90+t:2&fields=f3,f12,f14,f62,f128"
    )
    try:
        diff = json.loads(fetch(url))["data"]["diff"]
    except Exception as e:
        print(f"  行业板块（{'领涨' if descending else '领跌'}）获取失败: {e}",
              file=sys.stderr)
        return []

    rows = list(diff.values()) if isinstance(diff, dict) else diff
    out = []
    for row in rows:
        pct = row.get("f3")
        if not isinstance(pct, (int, float)):
            continue
        inflow = row.get("f62")  # 主力净流入，单位元
        out.append({
            "name": row.get("f14", ""),
            "pct": f"{pct:.2f}",
            "net_inflow_yi": (
                f"{inflow / 1e8:.2f}" if isinstance(inflow, (int, float)) else ""
            ),
            "leader": row.get("f128", ""),  # 领涨股
        })
    return out


def fetch_sectors():
    """行业板块涨跌排行，返回 (领涨 top5, 领跌 top5)。取不到返回 ([], [])。

    必须分两次按不同方向排序请求。东财行业板块有近 500 个，而 clist 单页
    硬上限 100 条——想靠一次降序请求取末尾当领跌，拿到的其实是第 96~100 名。
    """
    gainers = fetch_sector_page(descending=True)
    losers = fetch_sector_page(descending=False)
    if len(gainers) < SECTOR_TOP_N or len(losers) < SECTOR_TOP_N:
        return [], []
    return gainers, losers


def write_sectors(date, gainers, losers):
    """板块排行单独存一个文件，同一天重复跑会覆盖当天的行。"""
    path = DATA_DIR / SECTOR_CSV
    rows = []
    if path.exists():
        with path.open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["date"] != date]

    for rank_type, items in (("up", gainers), ("down", losers)):
        for i, item in enumerate(items, 1):
            rows.append({"date": date, "rank_type": rank_type, "rank": i, **item})

    rows.sort(key=lambda r: (r["date"], r["rank_type"], int(r["rank"])))
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SECTOR_HEADER)
        w.writeheader()
        w.writerows(rows)
    return path


def read_latest_sectors():
    """读出 sectors.csv 里最新那天的排行，给 README 用。"""
    path = DATA_DIR / SECTOR_CSV
    if not path.exists():
        return None, [], []
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None, [], []

    latest = max(r["date"] for r in rows)
    same_day = [r for r in rows if r["date"] == latest]

    def pick(rank_type):
        return sorted(
            (r for r in same_day if r["rank_type"] == rank_type),
            key=lambda r: int(r["rank"]),
        )

    return latest, pick("up"), pick("down")


# 三个池子的 endpoint 和排序方式。dpt 一律是 wz.ztzt——跌停池用 wz.dtzt
# 会返回 rc=206 data:null，看起来就像"今天没有跌停"，是个会静默写错数的坑。
# 跌停池还必须按 fund 排序，用 fbt（首次封板时间）排会返回空池。
POOLS = {
    "zt": ("getTopicZTPool", "fbt%3Aasc"),
    "dt": ("getTopicDTPool", "fund%3Aasc"),
    "zb": ("getTopicZBPool", "fbt%3Aasc"),
}


def fetch_pool(date_compact, kind, pagesize=1):
    """取涨停/跌停/炸板池。返回 (家数, 池内个股列表)，失败返回 (None, [])。

    返回里的 qdate 字段不可信（请求历史日期时它仍显示最新交易日），但
    date 参数本身是生效的，池内容确实是那天的，所以不拿 qdate 做校验。
    """
    endpoint, sort = POOLS[kind]
    url = (
        f"http://push2ex.eastmoney.com/{endpoint}"
        "?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt"
        f"&Pageindex=0&pagesize={pagesize}&sort={sort}&date={date_compact}"
    )
    try:
        data = json.loads(fetch(url)).get("data")
    except Exception as e:
        print(f"  {kind} 池获取失败: {e}", file=sys.stderr)
        return None, []
    if data is None:  # 一只都没有时是 null，这是 0 不是失败
        return 0, []
    return data.get("tc"), data.get("pool") or []


def fetch_sentiment(date_compact):
    """涨停/跌停/炸板数、炸板率、连板梯队。取不到的项留空。"""
    out = {}

    # 涨停池要全量拉，才能统计连板梯队
    limit_up, pool = fetch_pool(date_compact, "zt", pagesize=300)
    if limit_up is None:
        print("  涨停池取不到，涨停/连板这几列今天留空", file=sys.stderr)
    out["limit_up"] = "" if limit_up is None else limit_up

    ladder = {}
    for stock in pool:
        days = (stock.get("zttj") or {}).get("days")
        if isinstance(days, int):
            ladder[days] = ladder.get(days, 0) + 1
    if ladder:
        out["max_streak"] = max(ladder)
        # 2 板及以上才算连板，1 板是首板
        out["streak_2plus"] = sum(n for d, n in ladder.items() if d >= 2)
    else:
        out["max_streak"] = out["streak_2plus"] = ""
    out["_ladder"] = ladder

    limit_down, _ = fetch_pool(date_compact, "dt")
    if limit_down is None:
        print("  跌停池取不到，今天的跌停数留空", file=sys.stderr)
    out["limit_down"] = "" if limit_down is None else limit_down

    broken, _ = fetch_pool(date_compact, "zb")
    if broken is None:
        print("  炸板池取不到，今天的炸板数和炸板率留空", file=sys.stderr)
    out["broken"] = "" if broken is None else broken

    # 炸板率 = 炸板 / (涨停 + 炸板)，衡量当天封板的牢固程度
    if isinstance(limit_up, int) and isinstance(broken, int) and (limit_up + broken):
        out["broken_rate"] = f"{100 * broken / (limit_up + broken):.1f}"
    else:
        out["broken_rate"] = ""

    return out


def append_row(row):
    """写入当年 CSV。同一天重复运行会覆盖旧行，不会写重复。"""
    path = DATA_DIR / f"{row['date'][:4]}.csv"
    DATA_DIR.mkdir(exist_ok=True)

    rows = []
    if path.exists():
        with path.open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["date"] != row["date"]]

    rows.append(row)
    rows.sort(key=lambda r: r["date"])

    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADER)
        w.writeheader()
        w.writerows(rows)

    return path


def num(value, fmt="{:.2f}"):
    """CSV 里缺失的列显示成 -，不要显示 None。"""
    if value in (None, ""):
        return "-"
    try:
        return fmt.format(float(value))
    except (TypeError, ValueError):
        return str(value)


def render_readme(updated_at):
    """README 展示最近 10 个交易日。"""
    rows = []
    for path in sorted(DATA_DIR.glob("[0-9]*.csv")):
        with path.open(encoding="utf-8") as f:
            rows.extend(csv.DictReader(f))
    rows.sort(key=lambda r: r["date"])
    recent = rows[-10:][::-1]

    lines = [
        "# A股收盘快照",
        "",
        "每个交易日收盘后自动抓取并提交。数据来自腾讯行情和东方财富公开接口。",
        "",
        f"最后更新：{updated_at}",
        "",
    ]

    # 图表由 scripts/chart.py 生成，没生成过就不要在 README 里留坏图链接
    charts = [
        ("上证指数", "charts/sh000001.svg"),
        ("创业板指", "charts/sz399006.svg"),
    ]
    available = [(t, p) for t, p in charts if (ROOT / p).exists()]
    if available:
        lines.append("## 走势")
        lines.append("")
        for title, path in available:
            lines.append(f"![{title}]({path})")
            lines.append("")

    lines += [
        "## 最近 10 个交易日",
        "",
        "| 日期 | 上证 | 深成 | 创业板 | 沪深300 | 科创50 | 成交额(亿) | 涨/跌/平 | 涨停 | 跌停 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for r in recent:
        cells = [r["date"]]
        for _, name in INDEXES:
            close, pct = r.get(f"{name}_close"), r.get(f"{name}_pct")
            if close in (None, ""):
                cells.append("-")
            else:
                # 涨跌幅带符号，一眼能看出红绿
                cells.append(f"{num(close)}<br>{float(pct):+.2f}%" if pct else num(close))
        cells.append(num(r.get("amount_yi"), "{:.0f}"))
        cells.append(
            f"{num(r.get('up'), '{:.0f}')}/{num(r.get('down'), '{:.0f}')}/"
            f"{num(r.get('flat'), '{:.0f}')}"
        )
        cells.append(num(r.get("limit_up"), "{:.0f}"))
        cells.append(num(r.get("limit_down"), "{:.0f}"))
        lines.append("| " + " | ".join(cells) + " |")

    lines += ["", f"完整历史在 [data/](data/) 目录，共 {len(rows)} 个交易日。", ""]
    lines += render_sentiment_section(recent)
    lines += render_sector_section()
    lines += [
        "## 说明",
        "",
        "由 GitHub Actions 在每个交易日 16:20 (北京时间) 运行 "
        "[scripts/snapshot.py](scripts/snapshot.py) 生成，数据来自腾讯行情和"
        "东方财富公开接口。非交易日不写数据，只记一行运行日志。",
        "",
        "指数历史由 [scripts/backfill.py](scripts/backfill.py) 一次性回填。"
        "涨跌家数、涨停跌停、连板梯队这些是盘后快照，没有历史接口可回填，"
        "只能逐日累积，所以回填日期的这几列是空的。",
        "",
    ]

    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def render_sentiment_section(recent):
    """情绪指标：最近一天的涨停梯队，外加一张近期趋势小表。"""
    latest = next((r for r in recent if r.get("limit_up")), None)
    if latest is None:
        return []

    lines = [
        "## 市场情绪",
        "",
        f"最新交易日 {latest['date']}：",
        "",
        f"- 涨停 **{latest['limit_up']}** 家，跌停 **{latest.get('limit_down') or '-'}** 家",
    ]
    if latest.get("broken"):
        lines.append(
            f"- 炸板 {latest['broken']} 家，炸板率 **{latest.get('broken_rate', '-')}%**"
            "（越高说明封板越不牢）"
        )
    if latest.get("max_streak"):
        lines.append(
            f"- 最高 **{latest['max_streak']}** 连板，"
            f"2 板及以上共 {latest.get('streak_2plus', '-')} 家"
        )

    # 有情绪数据的日子还不多时，这张表没什么可看的，攒够两天再放
    with_sentiment = [r for r in recent if r.get("limit_up")]
    if len(with_sentiment) >= 2:
        lines += [
            "",
            "| 日期 | 涨停 | 跌停 | 炸板 | 炸板率 | 最高连板 | 连板家数 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for r in with_sentiment:
            lines.append(
                f"| {r['date']} | {r.get('limit_up') or '-'} | "
                f"{r.get('limit_down') or '-'} | {r.get('broken') or '-'} | "
                f"{r.get('broken_rate') or '-'}% | {r.get('max_streak') or '-'} | "
                f"{r.get('streak_2plus') or '-'} |"
            )
    lines.append("")
    return lines


def render_sector_section():
    """行业板块领涨领跌。"""
    date, gainers, losers = read_latest_sectors()
    if not gainers:
        return []

    lines = ["## 行业板块", "", f"{date} 领涨与领跌各五个：", "",
             "| | 行业 | 涨跌幅 | 主力净流入(亿) | 领涨股 |",
             "| --- | --- | --- | --- | --- |"]
    for label, items in (("领涨", gainers), ("领跌", losers)):
        for i, r in enumerate(items):
            tag = label if i == 0 else ""
            pct = float(r["pct"])
            lines.append(
                f"| {tag} | {r['name']} | {pct:+.2f}% | "
                f"{r.get('net_inflow_yi') or '-'} | {r.get('leader') or '-'} |"
            )
    lines.append("")
    return lines


def log(message):
    with (ROOT / "log.txt").open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def main():
    now = datetime.now(beijing_tz())
    # 手动补数据用。填的日期跟行情自带的日期对不上时，下面那道校验会
    # 直接拒掉，不会把当前行情写进某个过去的日子。
    today = os.environ.get("SNAPSHOT_DATE") or now.strftime("%Y-%m-%d")
    stamp = now.strftime("%Y-%m-%d %H:%M")
    print(f"当前北京时间 {stamp}，目标日期 {today}")

    quotes, quote_date = fetch_indexes()

    if quotes is None:
        # 数据源挂了也要 commit，格子不能断
        print("行情接口无响应，只记日志")
        log(f"{stamp} 行情接口无响应")
        return 0

    if quote_date != today:
        print(f"行情日期是 {quote_date}，{today} 不是交易日或尚未收盘")
        log(f"{stamp} 非交易日（最近交易日 {quote_date}）")
        return 0

    row = {"date": today}
    for code, name in INDEXES:
        q = quotes.get(code, {})
        row[f"{name}_close"] = f"{q['close']:.2f}" if q else ""
        row[f"{name}_pct"] = f"{q['pct']:.2f}" if q else ""

    # 两市成交额 = 上证 + 深证
    total = sum(
        quotes[c]["amount_yi"] for c in ("sh000001", "sz399001") if c in quotes
    )
    row["amount_yi"] = f"{total:.1f}" if total else ""

    breadth = fetch_breadth()
    if not breadth:
        print("  涨跌家数取不到，今天这三列留空，且不会再补", file=sys.stderr)
    row["up"] = breadth.get("up", "")
    row["down"] = breadth.get("down", "")
    row["flat"] = breadth.get("flat", "")

    sentiment = fetch_sentiment(today.replace("-", ""))
    ladder = sentiment.pop("_ladder", {})
    row.update(sentiment)

    gainers, losers = fetch_sectors()
    if gainers:
        write_sectors(today, gainers, losers)
    else:
        print("  板块排行取不到，sectors.csv 今天不写", file=sys.stderr)

    path = append_row(row)
    render_readme(stamp)

    sh = quotes.get("sh000001", {})
    print(f"已写入 {path.name}: 上证 {sh.get('close')} ({sh.get('pct'):+.2f}%), "
          f"成交 {total:.0f} 亿, 涨跌平 {row['up']}/{row['down']}/{row['flat']}")
    print(f"  涨停 {row['limit_up']}, 跌停 {row['limit_down']}, "
          f"炸板 {row['broken']}（炸板率 {row['broken_rate']}%）, "
          f"最高 {row['max_streak']} 板, 连板 {row['streak_2plus']} 家")
    if ladder:
        print("  连板梯队: " + " ".join(f"{d}板×{n}" for d, n in sorted(ladder.items())))
    if gainers:
        print(f"  领涨行业: {gainers[0]['name']} {gainers[0]['pct']}% | "
              f"领跌: {losers[0]['name']} {losers[0]['pct']}%")
    log(f"{stamp} 交易日快照已更新")
    return 0


if __name__ == "__main__":
    sys.exit(main())
