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
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

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
    + ["amount_yi", "up", "down", "flat", "limit_up", "limit_down"]
)


def fetch(url, decode="utf-8", timeout=20):
    """取一个 URL 的文本。

    东财会对请求太密的 IP 直接 RST，表现为连接被对端关闭。curl 偶尔
    还能过，所以 urllib 失败就再用 curl 试一次；runner 和 macOS 都自带
    curl，不引入依赖。真被封了两条都会失败，调用方按缺数据处理。
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode(decode, errors="replace")
    except (urllib.error.URLError, OSError, ssl.SSLError):
        out = subprocess.run(
            ["curl", "-sS", "--compressed", "--max-time", str(timeout),
             "-H", f"User-Agent: {UA}", url],
            capture_output=True, timeout=timeout + 10, check=True,
        ).stdout
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


def fetch_limit_count(date_compact, kind):
    """涨停/跌停家数。kind 取 'zt' 或 'dt'。取不到返回 None。"""
    endpoint = "getTopicZTPool" if kind == "zt" else "getTopicDTPool"
    dpt = "wz.ztzt" if kind == "zt" else "wz.dtzt"
    url = (
        f"http://push2ex.eastmoney.com/{endpoint}"
        "?ut=7eea3edcaed734bea9cbfc24409ed989"
        f"&dpt={dpt}&Pageindex=0&pagesize=1&sort=fbt%3Aasc&date={date_compact}"
    )
    try:
        data = json.loads(fetch(url)).get("data")
        # 当天一只涨停都没有时 data 是 null，这是 0 不是失败
        return 0 if data is None else data.get("tc")
    except Exception as e:
        print(f"  {kind} 家数获取失败: {e}", file=sys.stderr)
        return None


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
    for path in sorted(DATA_DIR.glob("*.csv")):
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

    lines += [
        "",
        f"完整历史在 [data/](data/) 目录，共 {len(rows)} 个交易日。",
        "",
        "## 说明",
        "",
        "由 GitHub Actions 在每个交易日 16:20 (北京时间) 运行 "
        "[scripts/snapshot.py](scripts/snapshot.py) 生成。",
        "非交易日不写数据，只记一行运行日志。",
        "",
    ]

    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def log(message):
    with (ROOT / "log.txt").open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def main():
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
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
    row["up"] = breadth.get("up", "")
    row["down"] = breadth.get("down", "")
    row["flat"] = breadth.get("flat", "")

    compact = today.replace("-", "")
    for key, kind in (("limit_up", "zt"), ("limit_down", "dt")):
        count = fetch_limit_count(compact, kind)
        row[key] = "" if count is None else count

    path = append_row(row)
    render_readme(stamp)

    sh = quotes.get("sh000001", {})
    print(f"已写入 {path.name}: 上证 {sh.get('close')} ({sh.get('pct'):+.2f}%), "
          f"成交 {total:.0f} 亿, 涨跌平 {row['up']}/{row['down']}/{row['flat']}, "
          f"涨停 {row['limit_up']}, 跌停 {row['limit_down']}")
    log(f"{stamp} 交易日快照已更新")
    return 0


if __name__ == "__main__":
    sys.exit(main())
