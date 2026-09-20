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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def beijing_tz():
    """返回北京时区；系统缺少 tzdata 时退回固定 UTC+8。"""
    try:
        return ZoneInfo("Asia/Shanghai")
    except ZoneInfoNotFoundError:
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
DAILY_FILE_GLOB = "[0-9][0-9][0-9][0-9].csv"
PULSE_HEADER = ["captured_at", "slot"] + CSV_HEADER

SLOT_LABELS = {
    "overnight": "外围收盘",
    "open": "开盘脉搏",
    "midday": "午间脉搏",
    "close": "收盘快照",
    "night": "夜间校验",
}
CRON_SLOTS = {
    "15 22 * * *": "overnight",  # 06:15 Asia/Shanghai
    "5 2 * * *": "open",      # 10:05 Asia/Shanghai
    "35 3 * * *": "midday",  # 11:35 Asia/Shanghai
    "10 7 * * *": "close",   # 15:10 Asia/Shanghai
    "20 12 * * *": "night",  # 20:20 Asia/Shanghai
}
FINAL_SLOTS = {"close", "night"}


# 东财对请求密度很敏感：几秒内连打五六个就开始 RST，而每次隔一秒多就没事。
# 全脚本每天只跑一次十来个请求，多花十几秒无所谓，所以统一限速。
MIN_INTERVAL = 1.3
_last_request = 0.0


def fetch(url, decode="utf-8", timeout=20, headers=None):
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
        request_headers = {"User-Agent": UA, **(headers or {})}
        req = urllib.request.Request(url, headers=request_headers)
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode(decode, errors="replace")
    except (urllib.error.URLError, OSError, ssl.SSLError) as first_error:
        curl_headers = []
        for name, value in request_headers.items():
            curl_headers.extend(["-H", f"{name}: {value}"])
        out = subprocess.run(
            ["curl", "-sS", "--compressed", "--max-time", str(timeout),
             *curl_headers, url],
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
        print("  涨停池取不到，涨停与连板字段留空", file=sys.stderr)
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
        print("  跌停池取不到，跌停字段留空", file=sys.stderr)
    out["limit_down"] = "" if limit_down is None else limit_down

    broken, _ = fetch_pool(date_compact, "zb")
    if broken is None:
        print("  炸板池取不到，炸板与炸板率字段留空", file=sys.stderr)
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


def daily_csv_paths():
    """只返回按年份命名的行情年表，排除 sectors.csv 等旁路数据。"""
    return sorted(DATA_DIR.glob(DAILY_FILE_GLOB))


def load_daily_rows():
    """读取全部行情年表，按交易日排序。"""
    rows = []
    for path in daily_csv_paths():
        with path.open(encoding="utf-8") as f:
            rows.extend(csv.DictReader(f))
    rows.sort(key=lambda r: r["date"])
    return rows


def resolve_slot(raw, now):
    """把 workflow 的 cron/手动输入归一为四个市场时段。"""
    if raw in SLOT_LABELS:
        return raw
    if raw in CRON_SLOTS:
        return CRON_SLOTS[raw]

    minutes = now.hour * 60 + now.minute
    if minutes < 8 * 60:
        return "overnight"
    if minutes < 11 * 60:
        return "open"
    if minutes < 14 * 60:
        return "midday"
    if minutes < 18 * 60:
        return "close"
    return "night"


def append_pulse(row, captured_at, slot):
    """保存盘中观察值；同一捕获时刻重复运行时覆盖，不制造重复行。"""
    pulse_dir = DATA_DIR / "pulses"
    pulse_dir.mkdir(parents=True, exist_ok=True)
    path = pulse_dir / f"{row['date'][:7]}.csv"

    rows = []
    if path.exists():
        with path.open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["captured_at"] != captured_at]

    rows.append({"captured_at": captured_at, "slot": slot, **row})
    rows.sort(key=lambda r: r["captured_at"])
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PULSE_HEADER)
        writer.writeheader()
        writer.writerows(rows)
    return path


def latest_pulse():
    """读取最近一次盘中观察值。"""
    paths = sorted((DATA_DIR / "pulses").glob("[0-9][0-9][0-9][0-9]-[0-9][0-9].csv"))
    if not paths:
        return None
    with paths[-1].open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return max(rows, key=lambda r: r["captured_at"]) if rows else None


def write_status(status):
    """写入每次任务的健康状态，让失败/休市也有可观测结果。"""
    path = DATA_DIR / "status.json"
    DATA_DIR.mkdir(exist_ok=True)
    path.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def _number(value, integer=False):
    if value in (None, ""):
        return None
    return int(float(value)) if integer else float(value)


def write_latest_json(generated_at):
    """导出稳定、机器可读的最新行情入口。"""
    rows = load_daily_rows()
    latest = rows[-1] if rows else None
    sector_date, gainers, losers = read_latest_sectors()
    status_path = DATA_DIR / "status.json"
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else None
    global_path = DATA_DIR / "global.json"
    global_data = (
        json.loads(global_path.read_text(encoding="utf-8")) if global_path.exists() else None
    )
    analysis_path = DATA_DIR / "analysis.json"
    analysis = (
        json.loads(analysis_path.read_text(encoding="utf-8"))
        if analysis_path.exists()
        else None
    )
    scorecard_path = DATA_DIR / "scorecard.json"
    scorecard = (
        json.loads(scorecard_path.read_text(encoding="utf-8"))
        if scorecard_path.exists()
        else None
    )

    daily = None
    if latest:
        daily = {
            "date": latest["date"],
            "indices": {
                code: {
                    "name": name,
                    "close": _number(latest.get(f"{name}_close")),
                    "pct": _number(latest.get(f"{name}_pct")),
                }
                for code, name in INDEXES
            },
            "amount_yi": _number(latest.get("amount_yi")),
            "breadth": {
                key: _number(latest.get(key), integer=True)
                for key in ("up", "down", "flat")
            },
            "sentiment": {
                key: _number(latest.get(key), integer=key != "broken_rate")
                for key in (
                    "limit_up", "limit_down", "broken", "broken_rate",
                    "max_streak", "streak_2plus",
                )
            },
        }

    payload = {
        "schema_version": 1,
        "generated_at": generated_at,
        "status": status,
        "global": global_data,
        "analysis": analysis,
        "scorecard": scorecard,
        "latest_daily": daily,
        "latest_pulse": latest_pulse(),
        "sectors": {
            "date": sector_date,
            "gainers": gainers,
            "losers": losers,
        },
    }
    path = DATA_DIR / "latest.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def finalize_outputs(status, stamp):
    write_status(status)
    write_latest_json(stamp)
    render_readme(stamp)


def num(value, fmt="{:.2f}"):
    """CSV 里缺失的列显示成 -，不要显示 None。"""
    if value in (None, ""):
        return "-"
    try:
        return fmt.format(float(value))
    except (TypeError, ValueError):
        return str(value)


def render_readme(updated_at):
    """生成兼顾人类浏览和项目传播的动态首页。"""
    rows = load_daily_rows()
    recent = rows[-10:][::-1]

    status = {}
    status_path = DATA_DIR / "status.json"
    if status_path.exists():
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            status = {}
    state_text = {
        "live": "🟢 盘中",
        "closed": "🔴 已收盘",
        "non_trading": "⚪ 休市 / 未开盘",
        "unavailable": "🟠 数据源暂不可用",
        "checking": "🔵 检查中",
    }.get(status.get("market_state"), "⚪ 等待首次检查")
    status_line = status.get("message") or "等待 GitHub Actions 更新"
    checked_at = status.get("checked_at") or updated_at

    lines = [
        '<div align="center">',
        "",
        "# 📈 A-Share Pulse",
        "",
        "**把 GitHub 提交图变成 A 股市场心电图。**",
        "",
        "每天五次联动全球收盘、A 股盘中与新闻风险；零依赖、可审计、可直接 Fork。",
        "",
        '<a href="https://github.com/ychenfen/a-share-daily/actions/workflows/daily.yml"><img alt="A-share market pulse" src="https://github.com/ychenfen/a-share-daily/actions/workflows/daily.yml/badge.svg"></a>',
        '<a href="https://ychenfen.github.io/a-share-daily/"><img alt="Live dashboard" src="https://img.shields.io/badge/live-dashboard-ff5148"></a>',
        '<img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">',
        '<img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-zero-2ea44f">',
        '<a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>',
        "",
        "[English](README.en.md) · 简体中文",
        "",
        "</div>",
        "",
        '<a href="https://ychenfen.github.io/a-share-daily/">'
        '<img alt="A-Share Pulse 市场天气台" src="assets/social-preview.png"></a>',
        "",
        "> [!NOTE]",
        f"> **{state_text}** · {status_line} · 最后检查 `{checked_at}`（北京时间）",
        "",
        "[🌐 在线大屏](https://ychenfen.github.io/a-share-daily/) · "
        "[一键生成自己的版本](https://github.com/ychenfen/a-share-daily/generate) · "
        "[最新 JSON](data/latest.json) · [运行状态](data/status.json) · "
        "[完整历史](data/) · [数据字典](docs/DATA_SCHEMA.md) · "
        "[自动任务](https://github.com/ychenfen/a-share-daily/actions) · "
        "[讨论区](https://github.com/ychenfen/a-share-daily/discussions) · "
        "[路线图](ROADMAP.md) · [参与贡献](CONTRIBUTING.md)",
        "",
        "## 为什么值得收藏",
        "",
        "| 能力 | 你得到什么 |",
        "| --- | --- |",
        "| 🫀 五段市场脉搏 | 外围收盘 + A 股开盘、午间、收盘、夜间校验，不只是日终一个点 |",
        "| 🧠 情绪温度计 | 涨跌家数、涨停/跌停、炸板率、最高连板和行业强弱 |",
        "| 🟩 GitHub 风格日历 | 用红绿贡献格复刻近一年市场节奏，适合截图分享 |",
        "| 🖥️ 在线研究大屏 | GitHub Pages 自动部署，手机和桌面都能直接查看 |",
        "| 🌍 跨资产先行带 | A50、离岸人民币与美元指数低权重计分，黄金和原油保留为背景 |",
        "| 🧭 事件传导链 | 新闻先去重分类，再映射宏观变量、A 股风格和可证伪条件 |",
        "| 🗞️ 每日传播卡片 | 自动生成 1200×630 矢量简报，可下载、引用和转发 |",
        "| 🧾 Git 原生数据湖 | 每次变化都有 diff，可追溯、可回滚，CSV/JSON 直接用于研究 |",
        "| 🪶 零第三方依赖 | 只用 Python 标准库和 GitHub Actions，Fork 后无需服务器 |",
        "| 🛡️ 质量门禁 | 每次推送前跑回归测试、schema 和重复日期检查 |",
        "",
    ]
    share_card = ROOT / "charts/daily_brief.svg"
    if share_card.exists():
        lines += [
            "## 今日市场简报",
            "",
            '<a href="https://ychenfen.github.io/a-share-daily/#share">'
            '<img alt="A-Share Pulse 每日市场简报" src="charts/daily_brief.svg"></a>',
            "",
            "[打开可交互大屏](https://ychenfen.github.io/a-share-daily/) · "
            "[下载 SVG](charts/daily_brief.svg)",
            "",
        ]
    lines += render_global_section()
    lines += render_scorecard_section()

    # 图表由 scripts/chart.py 生成，没生成过就不要在 README 里留坏图链接
    charts = [
        ("近一年 A 股涨跌日历", "charts/market_calendar.svg"),
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

    lines += [
        "",
        f"完整历史在 [data/](data/) 目录，共 {len(rows)} 个交易日。",
        "",
    ]
    lines += render_sentiment_section(recent)
    lines += render_sector_section()
    lines += [
        "## 自动更新节奏",
        "",
        "| 北京时间 | 记录内容 | 正式日线 |",
        "| --- | --- | --- |",
        "| 06:15 | 外围收盘：美股、日股、港股、VIX、美债与新闻 | 否 |",
        "| 10:05 | 开盘脉搏：指数、成交额、涨跌家数 | 否 |",
        "| 11:35 | 午间脉搏：上午收束状态 | 否 |",
        "| 15:10 | 收盘快照：完整行情、情绪和行业排行 | 是 |",
        "| 20:20 | 夜间校验：复核收盘数据与数据源健康 | 是 |",
        "",
        "GitHub Actions 可能有数分钟调度延迟。休市日不会伪造行情，"
        "只刷新状态和审计日志。",
        "",
        "## 数据与复用",
        "",
        "```text",
        "data/YYYY.csv          # 日线与收盘情绪，适合回测",
        "data/pulses/YYYY-MM.csv # 日内四段观察，适合研究盘中演化",
        "data/sectors.csv        # 行业领涨/领跌 Top 5",
        "data/global.json         # 全球指数、A50、汇率、美元、黄金、原油、VIX 与美债",
        "data/analysis.json       # 可解释风险温度、新闻与研究观察",
        "data/scorecard.json      # 真实运行信号的前向验证成绩单",
        "data/signals/YYYY.csv    # 每次风险信号的可审计原始记录",
        "data/latest.json        # 程序最方便消费的聚合入口",
        "data/status.json        # 最近任务与数据源健康状态",
        "```",
        "",
        "本地运行不需要安装依赖：",
        "",
        "```bash",
        "python3 scripts/snapshot.py",
        "python3 scripts/global_context.py",
        "python3 scripts/scorecard.py",
        "python3 scripts/share_card.py",
        "python3 scripts/chart.py",
        "python3 -m unittest discover -s tests -v",
        "python3 scripts/validate.py",
        "```",
        "",
        "想拥有自己的市场心电图，直接用模板生成仓库并开启 Actions 即可。"
        "更多字段说明见 [数据字典](docs/DATA_SCHEMA.md)。",
        "",
        "## 数据来源与边界",
        "",
        "指数行情来自腾讯行情公开接口；市场宽度、涨跌停池和行业排行来自"
        "东方财富公开接口。接口异常时保留上一份有效数据，并在 `status.json`"
        " 明确标记，不把空响应冒充成功。",
        "",
        "全球指数来自腾讯公开行情，A50、离岸人民币、美元指数、黄金与原油来自"
        "新浪财经公开行情，宏观压力来自 FRED；新闻区只保留"
        "Google News RSS 的标题、来源和链接，不抓取或改写正文。",
        "",
        "指数历史由 [scripts/backfill.py](scripts/backfill.py) 一次性回填。"
        "涨跌家数、涨停跌停、连板梯队这些是盘后快照，没有历史接口可回填，"
        "只能逐日累积，所以回填日期的这几列是空的。",
        "",
        "> 本项目仅用于数据记录与技术研究，不构成投资建议。公开接口可能调整，"
        "请以交易所和数据服务商正式口径为准。",
        "",
        "---",
        "",
        "如果它帮你省下了整理行情的时间，欢迎点一个 ⭐。"
        "想一起完善信号、数据源或可视化，可以先到"
        " [讨论区](https://github.com/ychenfen/a-share-daily/discussions) 交流，"
        "或从 [贡献指南](CONTRIBUTING.md) 开始。",
        "",
    ]

    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def md_escape(value):
    """把外部新闻标题作为 Markdown 文本处理，避免被解释成结构。"""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("\n", " ")
        .strip()
    )


def render_global_section():
    """全球市场、规则分析与新闻雷达。"""
    global_path = DATA_DIR / "global.json"
    analysis_path = DATA_DIR / "analysis.json"
    if not global_path.exists() or not analysis_path.exists():
        return []
    try:
        global_data = json.loads(global_path.read_text(encoding="utf-8"))
        analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    lines = ["## 全球市场与策略雷达", ""]
    dashboard = ROOT / "charts/global_dashboard.svg"
    if dashboard.exists():
        lines += ["![全球市场与跨市场风险温度](charts/global_dashboard.svg)", ""]

    score = int(analysis.get("score") or 0)
    lines += [
        f"> **风险温度 {score:+d} · {md_escape(analysis.get('stance', '等待数据'))}**"
        f"（置信度：{md_escape(analysis.get('confidence', '低'))}）",
        f"> {md_escape(analysis.get('summary', ''))}",
        "",
        "| 市场 | 地区 | 收盘 | 涨跌幅 |",
        "| --- | --- | ---: | ---: |",
    ]
    for market in global_data.get("markets") or []:
        pct = market.get("pct")
        pct_text = f"{pct:+.2f}%" if isinstance(pct, (int, float)) else "-"
        lines.append(
            f"| {md_escape(market.get('name', ''))} | {md_escape(market.get('region', ''))} | "
            f"{num(market.get('close'))} | {pct_text} |"
        )

    cross_assets = global_data.get("cross_assets") or []
    if cross_assets:
        lines += [
            "",
            "### 跨资产先行带",
            "",
            "> A50 与美元/人民币组合仅作低权重评分；黄金和原油只提供风险背景，不直接加减分。",
            "",
            "| 资产 | 角色 | 最新值 | 涨跌幅 | 状态 |",
            "| --- | --- | ---: | ---: | --- |",
        ]
        for asset in cross_assets:
            close = asset.get("close")
            digits = 4 if asset.get("code") == "USDCNH" else 2
            close_text = f"{float(close):,.{digits}f}" if isinstance(close, (int, float)) else "-"
            pct = asset.get("pct")
            pct_text = f"{pct:+.2f}%" if isinstance(pct, (int, float)) else "-"
            role = "背景观察" if asset.get("role") == "context" else "低权重计分"
            state = "最近有效值" if asset.get("stale") else "最新"
            lines.append(
                f"| {md_escape(asset.get('name') or asset.get('code', ''))} | {role} | "
                f"{close_text} | {pct_text} | {state} |"
            )

    health_labels = {
        "markets": "全球指数",
        "cross_assets": "跨资产",
        "vix": "VIX",
        "us10y": "美债10Y",
        "news": "新闻",
    }
    degraded = [
        health_labels.get(key, key)
        for key, item in (global_data.get("health") or {}).items()
        if item.get("status") != "fresh"
    ]
    if degraded:
        lines += [
            "",
            f"> ⚠️ 数据降级：{'、'.join(degraded)}本轮未完全刷新，已尽量保留最近有效值。",
        ]

    signals = analysis.get("signals") or []
    if signals:
        lines += [
            "",
            "### 风险温度拆解",
            "",
            "| 信号 | 当前值 | 分数贡献 | 解释 |",
            "| --- | --- | ---: | --- |",
        ]
        for signal in signals:
            contribution = float(signal.get("contribution") or 0)
            lines.append(
                f"| {md_escape(signal.get('label', ''))} | "
                f"{md_escape(signal.get('value', ''))} | {contribution:+.1f} | "
                f"{md_escape(signal.get('note', ''))} |"
            )

    events = analysis.get("events") or []
    if events:
        state_labels = {"fresh": "最新", "stale": "最近有效值", "missing": "缺失"}
        lines += [
            "",
            "### 事件传导链",
            "",
            "> 去重标题只作为待验证线索；分类数量不是已确认事件，传导链也不直接参与评分。",
            "",
            "| 事件线索 | 宏观传导 | A 股映射 | 观察指标 | 失效条件 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for event in events:
            watches = []
            for item in event.get("watch") or []:
                state = state_labels.get(item.get("state"), "缺失")
                watches.append(f"{item.get('label') or item.get('code', '')} {item.get('value', '--')}（{state}）")
            count = int(event.get("headline_count") or 0)
            lines.append(
                f"| {md_escape(event.get('label', ''))}（{count} 条） | "
                f"{md_escape(event.get('macro_path', ''))} | "
                f"{md_escape(event.get('a_share_lens', ''))} | "
                f"{md_escape(' / '.join(watches))} | "
                f"{md_escape(event.get('invalidation', ''))} |"
            )

    lines += ["", "### 研究观察", ""]
    for item in analysis.get("advice") or []:
        lines.append(f"- {md_escape(item)}")

    news = analysis.get("news") or []
    if news:
        lines += ["", "### 新闻雷达", ""]
        for item in news[:6]:
            title = md_escape(item.get("title", ""))
            source = md_escape(item.get("source", ""))
            link = item.get("link", "")
            if link.startswith("https://news.google.com/"):
                lines.append(f"- [{title}]({link}) · {source}")
            else:
                lines.append(f"- {title} · {source}")

    lines += [
        "",
        f"方法：{md_escape(analysis.get('methodology', ''))}",
        "",
        "> 这是可审计的通用市场研究提示，不是个性化仓位或买卖建议。",
        "",
    ]
    return lines


def render_scorecard_section():
    """前向验证：样本不足时也明确展示收集进度。"""
    path = DATA_DIR / "scorecard.json"
    if not path.exists():
        return []
    try:
        scorecard = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    lines = ["## 信号成绩单", ""]
    chart = ROOT / "charts/signal_scorecard.svg"
    if chart.exists():
        lines += ["![风险信号前向验证](charts/signal_scorecard.svg)", ""]
    directional = scorecard.get("directional_1d") or 0
    minimum = scorecard.get("minimum_samples") or 20
    hit_rate = scorecard.get("hit_rate_1d")
    if hit_rate is None:
        lines += [
            f"> 前向样本收集中：**{directional} / {minimum}**。",
            "> 从功能上线后真实记录，不回填缺失的全球与新闻历史来制造胜率。",
            "",
        ]
    else:
        lines += [
            f"> 1 日方向命中率 **{hit_rate:.1f}%**，"
            f"当前有效样本 **{directional}** 条。",
            "",
        ]
    lines += [
        "方法：开盘/午间信号验证当日收盘，收盘/夜间信号验证下一交易日；"
        "同时持续结算 3 日和 5 日复合收益。",
        "",
        "> 样本不足时不输出稳定性结论，历史表现也不代表未来收益。",
        "",
    ]
    return lines


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


def workflow_output(name, value):
    """把时段和结果传给 GitHub Actions 的提交步骤。"""
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")


def main():
    now = datetime.now(beijing_tz())
    today = os.environ.get("SNAPSHOT_DATE") or now.strftime("%Y-%m-%d")
    stamp = now.strftime("%Y-%m-%d %H:%M")
    slot = resolve_slot(os.environ.get("SNAPSHOT_SLOT", "auto"), now)
    slot_label = SLOT_LABELS[slot]
    workflow_output("slot", slot)
    workflow_output("slot_label", slot_label)
    print(f"当前北京时间 {stamp}，目标日期 {today}，时段 {slot_label}")

    status = {
        "schema_version": 1,
        "checked_at": stamp,
        "slot": slot,
        "slot_label": slot_label,
        "target_date": today,
        "market_data_date": None,
        "market_state": "checking",
        "pulse_updated": False,
        "daily_updated": False,
    }

    try:
        quotes, quote_date = fetch_indexes()
    except Exception as e:
        print(f"行情接口请求失败: {e}", file=sys.stderr)
        quotes, quote_date = None, None

    if quotes is None:
        status["market_state"] = "unavailable"
        status["message"] = "行情接口无响应，保留上一份有效数据"
        finalize_outputs(status, stamp)
        log(f"{stamp} {slot_label}：行情接口无响应")
        workflow_output("result", "unavailable")
        return 0

    status["market_data_date"] = quote_date
    if quote_date != today:
        status["market_state"] = "non_trading"
        status["message"] = f"目标日未开市或尚未产生行情，最近交易日 {quote_date}"
        finalize_outputs(status, stamp)
        print(status["message"])
        log(f"{stamp} {slot_label}：非交易日（最近交易日 {quote_date}）")
        workflow_output("result", "non-trading")
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
        print("  涨跌家数取不到，本次对应字段留空", file=sys.stderr)
    row["up"] = breadth.get("up", "")
    row["down"] = breadth.get("down", "")
    row["flat"] = breadth.get("flat", "")

    ladder = {}
    gainers, losers = [], []
    if slot in FINAL_SLOTS:
        sentiment = fetch_sentiment(today.replace("-", ""))
        ladder = sentiment.pop("_ladder", {})
        row.update(sentiment)
        gainers, losers = fetch_sectors()
        if not gainers:
            print("  板块排行取不到，本次不覆盖 sectors.csv", file=sys.stderr)

    pulse_path = append_pulse(row, stamp, slot)
    status["pulse_updated"] = True
    status["pulse_file"] = str(pulse_path.relative_to(ROOT))

    if slot in FINAL_SLOTS:
        if gainers:
            write_sectors(today, gainers, losers)
        daily_path = append_row(row)
        status["daily_updated"] = True
        status["daily_file"] = str(daily_path.relative_to(ROOT))

    status["market_state"] = "closed" if slot in FINAL_SLOTS else "live"
    status["message"] = f"{slot_label}已更新"
    finalize_outputs(status, stamp)

    sh = quotes.get("sh000001", {})
    print(f"已写入 {pulse_path.name}: 上证 {sh.get('close')} ({sh.get('pct'):+.2f}%), "
          f"成交 {total:.0f} 亿, 涨跌平 {row['up']}/{row['down']}/{row['flat']}")
    if slot in FINAL_SLOTS:
        print(f"  涨停 {row['limit_up']}, 跌停 {row['limit_down']}, "
              f"炸板 {row['broken']}（炸板率 {row['broken_rate']}%）, "
              f"最高 {row['max_streak']} 板, 连板 {row['streak_2plus']} 家")
    if ladder:
        print("  连板梯队: " + " ".join(f"{d}板×{n}" for d, n in sorted(ladder.items())))
    if gainers:
        print(f"  领涨行业: {gainers[0]['name']} {gainers[0]['pct']}% | "
              f"领跌: {losers[0]['name']} {losers[0]['pct']}%")
    log(f"{stamp} {slot_label}：更新成功")
    workflow_output("result", "updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
