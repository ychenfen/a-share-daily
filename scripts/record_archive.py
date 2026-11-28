#!/usr/bin/env python3
"""持续录制 A 股短线情绪明细档案（纯标准库，零第三方依赖）。

为什么需要持续录制：
- 东财涨停/炸板/跌停/强势股池仅保留最近约 15 个交易日，过期即无法免费回溯；
- 5 分钟分时线仅保留约 30 个交易日；
- 早盘竞价与封单变化过时不留痕。

本脚本与 snapshot.py 协同运行，把每日明细沉淀到 data/archive/：
- pools/YYYY-MM-DD_{zt,zb,dt,qs}.csv  涨停/炸板/跌停/强势股全量明细
- lhb/YYYY-MM-DD.csv                  龙虎榜（含官方异动上榜理由与买卖净额）
- prev_zt/YYYY-MM-DD.csv              昨日涨停股今日实际表现（溢价、大面、晋级）
- daily_regime.csv                    每日客观情绪读数（昨连板大面率、各板晋级率、最高板断板跌幅）
- fenshi_1m/YYYY-MM-DD.csv.gz         核心指数+连板/炸板/跌停/前排首板 1 分钟分时图（当日收盘含 09:15-09:25 竞价与分时均价）
- intraday_5m/YYYY-MM-DD.csv.gz       连板股（今日及昨日 lbc>=2）+ 指数的 5 分钟线压缩归档
- auction/YYYY-MM-DD.csv              早盘时段留痕（昨日连板开盘表现 + 今日 9:25 一字封单）
"""

import argparse
import csv
import gzip
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import snapshot  # noqa: E402

ARCHIVE_DIR = snapshot.DATA_DIR / "archive"

ZT_HEADER = [
    "date", "code", "market", "name", "price", "pct", "amount", "ltsz",
    "hs", "lbc", "zttj_days", "zttj_ct", "fbt", "lbt", "fund", "zbc", "hybk",
]
ZB_HEADER = [
    "date", "code", "market", "name", "price", "ztp", "pct", "amount",
    "ltsz", "hs", "fbt", "zbc", "hybk",
]
DT_HEADER = [
    "date", "code", "market", "name", "price", "pct", "amount", "ltsz",
    "hs", "fund", "lbc", "open_cnt", "hybk",
]
QS_HEADER = [
    "date", "code", "market", "name", "price", "pct", "amount", "ltsz",
    "hs", "zttj_days", "zttj_ct", "hybk", "cc",
]
LHB_HEADER = [
    "date", "code", "name", "close", "pct", "net_amt", "buy_amt", "sell_amt", "explanation",
]
LHB_SEATS_HEADER = [
    "date", "side", "code", "dept_name", "buy", "sell", "net", "explanation",
]
PREV_ZT_HEADER = [
    "date", "prev_date", "code", "name", "prev_lbc", "prev_hybk",
    "open", "high", "low", "close", "prev_close",
    "open_pct", "close_pct", "intraday_dd_pct", "is_big_loss", "promoted",
]
REGIME_HEADER = [
    "date", "prev_date", "zt_cnt", "zb_cnt", "dt_cnt", "max_lbc", "lbc2_cnt",
    "prev_zt_cnt", "prev_lbc2_cnt", "prev_zt_prem_pct", "prev_lbc2_prem_pct",
    "prev_lbc2_dm_rate", "promote_1to2", "promote_2to3", "promote_3to4",
    "top_lbc_prev", "top_lbc_broken", "top_lbc_avg_pct",
]
AUCTION_HEADER = [
    "captured_at", "date", "role", "code", "name", "prev_lbc", "hybk",
    "open_pct", "now_pct", "fbt", "fund_wan", "bid1_vol", "ask1_vol",
]
M5_HEADER = ["code", "time", "open", "close", "high", "low", "vol", "amount"]
FENSHI_HEADER = ["code", "time", "open", "price", "high", "low", "vol", "amount", "avg_price"]
DEFAULT_MAX_FENSHI = int(os.environ.get("ARCHIVE_MAX_FENSHI", "120"))

_LAST_FAST_REQ = 0.0


def fast_fetch(url, decode="utf-8", timeout=15, min_interval=0.25):
    """带温和限速与 curl 回落的 HTTP GET（用于档案录制，避免触发东财 RST）。"""
    global _LAST_FAST_REQ
    wait = min_interval - (time.monotonic() - _LAST_FAST_REQ)
    if wait > 0:
        time.sleep(wait)
    _LAST_FAST_REQ = time.monotonic()

    headers = {"User-Agent": snapshot.UA}
    try:
        req = urllib.request.Request(url, headers=headers)
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode(decode, errors="replace")
    except (urllib.error.URLError, OSError, ssl.SSLError) as first_err:
        out = subprocess.run(
            ["curl", "-sS", "--compressed", "--max-time", str(timeout),
             "-H", f"User-Agent: {snapshot.UA}", url],
            capture_output=True, timeout=timeout + 10, check=True,
        ).stdout
        if not out.strip():
            raise RuntimeError(f"请求返回空: {url}") from first_err
        return out.decode(decode, errors="replace")


def code_to_secid(code):
    return f"1.{code}" if str(code).startswith(("6", "9")) else f"0.{code}"


def code_to_tencent(code):
    c = str(code)
    if c.startswith(("6", "9")):
        return f"sh{c}"
    if c.startswith(("8", "4")):
        return f"bj{c}"
    return f"sz{c}"


def write_csv_atomic(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)
    return path


def fetch_topic_pool(date_compact, endpoint, sort, pagesize=500):
    url = (
        f"https://push2ex.eastmoney.com/{endpoint}"
        "?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt"
        f"&Pageindex=0&pagesize={pagesize}&sort={sort}&date={date_compact}"
    )
    try:
        payload = json.loads(fast_fetch(url, min_interval=0.4))
    except Exception as e:
        print(f"  [archive] {endpoint} {date_compact} 获取失败: {e}", file=sys.stderr)
        return None
    data = payload.get("data")
    if data is None:
        return []
    return data.get("pool") or []


def parse_zt_rows(date_str, pool):
    rows = []
    for x in pool:
        zttj = x.get("zttj") or {}
        p = x.get("p")
        rows.append({
            "date": date_str,
            "code": str(x.get("c", "")).zfill(6),
            "market": x.get("m", ""),
            "name": x.get("n", ""),
            "price": f"{p / 1000.0:.2f}" if isinstance(p, (int, float)) else "",
            "pct": f"{x['zdp']:.2f}" if isinstance(x.get("zdp"), (int, float)) else "",
            "amount": int(x["amount"]) if isinstance(x.get("amount"), (int, float)) else "",
            "ltsz": int(x["ltsz"]) if isinstance(x.get("ltsz"), (int, float)) else "",
            "hs": f"{x['hs']:.2f}" if isinstance(x.get("hs"), (int, float)) else "",
            "lbc": int(x.get("lbc") or 1),
            "zttj_days": zttj.get("days", ""),
            "zttj_ct": zttj.get("ct", ""),
            "fbt": x.get("fbt", ""),
            "lbt": x.get("lbt", ""),
            "fund": int(x["fund"]) if isinstance(x.get("fund"), (int, float)) else "",
            "zbc": int(x.get("zbc") or 0),
            "hybk": x.get("hybk", ""),
        })
    rows.sort(key=lambda r: (-int(r["lbc"]), str(r["fbt"]), r["code"]))
    return rows


def parse_zb_rows(date_str, pool):
    rows = []
    for x in pool:
        p, ztp = x.get("p"), x.get("ztp")
        rows.append({
            "date": date_str,
            "code": str(x.get("c", "")).zfill(6),
            "market": x.get("m", ""),
            "name": x.get("n", ""),
            "price": f"{p / 1000.0:.2f}" if isinstance(p, (int, float)) else "",
            "ztp": f"{ztp / 1000.0:.2f}" if isinstance(ztp, (int, float)) else "",
            "pct": f"{x['zdp']:.2f}" if isinstance(x.get("zdp"), (int, float)) else "",
            "amount": int(x["amount"]) if isinstance(x.get("amount"), (int, float)) else "",
            "ltsz": int(x["ltsz"]) if isinstance(x.get("ltsz"), (int, float)) else "",
            "hs": f"{x['hs']:.2f}" if isinstance(x.get("hs"), (int, float)) else "",
            "fbt": x.get("fbt", ""),
            "zbc": int(x.get("zbc") or 0),
            "hybk": x.get("hybk", ""),
        })
    rows.sort(key=lambda r: (str(r["fbt"]), r["code"]))
    return rows


def parse_dt_rows(date_str, pool):
    rows = []
    for x in pool:
        p = x.get("p")
        rows.append({
            "date": date_str,
            "code": str(x.get("c", "")).zfill(6),
            "market": x.get("m", ""),
            "name": x.get("n", ""),
            "price": f"{p / 1000.0:.2f}" if isinstance(p, (int, float)) else "",
            "pct": f"{x['zdp']:.2f}" if isinstance(x.get("zdp"), (int, float)) else "",
            "amount": int(x["amount"]) if isinstance(x.get("amount"), (int, float)) else "",
            "ltsz": int(x["ltsz"]) if isinstance(x.get("ltsz"), (int, float)) else "",
            "hs": f"{x['hs']:.2f}" if isinstance(x.get("hs"), (int, float)) else "",
            "fund": int(x["fund"]) if isinstance(x.get("fund"), (int, float)) else "",
            "lbc": int(x.get("days") or x.get("lbc") or 1),
            "open_cnt": int(x.get("oc") or 0),
            "hybk": x.get("hybk", ""),
        })
    rows.sort(key=lambda r: (r["code"],))
    return rows


def parse_qs_rows(date_str, pool):
    rows = []
    for x in pool:
        zttj = x.get("zttj") or {}
        p = x.get("p")
        rows.append({
            "date": date_str,
            "code": str(x.get("c", "")).zfill(6),
            "market": x.get("m", ""),
            "name": x.get("n", ""),
            "price": f"{p / 1000.0:.2f}" if isinstance(p, (int, float)) else "",
            "pct": f"{x['zdp']:.2f}" if isinstance(x.get("zdp"), (int, float)) else "",
            "amount": int(x["amount"]) if isinstance(x.get("amount"), (int, float)) else "",
            "ltsz": int(x["ltsz"]) if isinstance(x.get("ltsz"), (int, float)) else "",
            "hs": f"{x['hs']:.2f}" if isinstance(x.get("hs"), (int, float)) else "",
            "zttj_days": zttj.get("days", ""),
            "zttj_ct": zttj.get("ct", ""),
            "hybk": x.get("hybk", ""),
            "cc": x.get("cc", ""),
        })
    rows.sort(key=lambda r: (r["code"],))
    return rows


def fetch_lhb_rows(date_str):
    """拉取当日龙虎榜（含官方 3日/10日 异动上榜理由与买卖净额）。"""
    rows = []
    seen = set()
    for page in range(1, 5):
        url = (
            "https://datacenter-web.eastmoney.com/api/data/v1/get"
            "?reportName=RPT_DAILYBILLBOARD_DETAILSNEW"
            "&columns=SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE,CLOSE_PRICE,"
            "CHANGE_RATE,BILLBOARD_NET_AMT,BILLBOARD_BUY_AMT,BILLBOARD_SELL_AMT,EXPLANATION"
            f"&pageNumber={page}&pageSize=100&filter=(TRADE_DATE%3D%27{date_str}%27)"
        )
        try:
            j = json.loads(fast_fetch(url, min_interval=0.35))
        except Exception as e:
            print(f"  [archive] 龙虎榜 {date_str} 第 {page} 页失败: {e}", file=sys.stderr)
            break
        result = j.get("result") or {}
        data = result.get("data") or []
        if not data:
            break
        for x in data:
            code = str(x.get("SECURITY_CODE", "")).zfill(6)
            expl = (x.get("EXPLANATION") or "").replace("\n", " ").strip()
            key = (code, expl)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "date": date_str,
                "code": code,
                "name": x.get("SECURITY_NAME_ABBR", ""),
                "close": x.get("CLOSE_PRICE", ""),
                "pct": x.get("CHANGE_RATE", ""),
                "net_amt": x.get("BILLBOARD_NET_AMT", ""),
                "buy_amt": x.get("BILLBOARD_BUY_AMT", ""),
                "sell_amt": x.get("BILLBOARD_SELL_AMT", ""),
                "explanation": expl,
            })
        if page >= int(result.get("pages") or 1):
            break
    rows.sort(key=lambda r: (r["code"], r["explanation"]))
    return rows


def fetch_lhb_seats_rows(date_str):
    """拉取当日龙虎榜买五/卖五营业部席位明细（区分机构/游资/拉萨席位）。"""
    rows = []
    seen = set()
    reports = (
        ("buy", "RPT_BILLBOARD_DAILYDETAILSBUY"),
        ("sell", "RPT_BILLBOARD_DAILYDETAILSSELL"),
    )
    for side, report_name in reports:
        for page in range(1, 6):
            url = (
                "https://datacenter-web.eastmoney.com/api/data/v1/get"
                f"?reportName={report_name}&columns=ALL"
                f"&pageNumber={page}&pageSize=500&filter=(TRADE_DATE%3D%27{date_str}%27)"
            )
            try:
                j = json.loads(fast_fetch(url, min_interval=0.3))
            except Exception as e:
                print(f"  [archive] 龙虎榜席位({side}) {date_str} 失败: {e}", file=sys.stderr)
                break
            result = j.get("result") or {}
            data = result.get("data") or []
            if not data:
                break
            for x in data:
                code = str(x.get("SECURITY_CODE", "")).zfill(6)
                dept = (x.get("OPERATEDEPT_NAME") or "").strip()
                expl = (x.get("EXPLANATION") or "").replace("\n", " ").strip()
                key = (side, code, dept, expl, str(x.get("BUY", "")), str(x.get("SELL", "")))
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    "date": date_str,
                    "side": side,
                    "code": code,
                    "dept_name": dept,
                    "buy": x.get("BUY", ""),
                    "sell": x.get("SELL", ""),
                    "net": x.get("NET", ""),
                    "explanation": expl,
                })
            if page >= int(result.get("pages") or 1):
                break
    rows.sort(key=lambda r: (r["code"], r["side"], r["dept_name"]))
    return rows


def fetch_tencent_quotes(codes):
    """批量拉取腾讯实时/收盘行情，每次 50 只。"""
    out = {}
    code_list = list(dict.fromkeys(codes))
    for i in range(0, len(code_list), 50):
        batch = code_list[i:i + 50]
        q = ",".join(code_to_tencent(c) for c in batch)
        try:
            raw = fast_fetch(f"https://qt.gtimg.cn/q={q}", decode="gbk", min_interval=0.25)
        except Exception as e:
            print(f"  [archive] 腾讯批量行情失败: {e}", file=sys.stderr)
            continue
        for line in raw.split(";"):
            line = line.strip()
            if not line.startswith("v_") or '="' not in line:
                continue
            fields = line[line.index('"') + 1:line.rindex('"')].split("~")
            if len(fields) < 35:
                continue
            code = fields[2].zfill(6)
            try:
                prev_c = float(fields[4])
                op = float(fields[5])
                now_p = float(fields[3])
                hi = float(fields[33])
                lo = float(fields[34])
                pct = float(fields[32])
                bid1_v = int(float(fields[10])) if fields[10] else 0
                ask1_v = int(float(fields[20])) if fields[20] else 0
            except (ValueError, IndexError):
                continue
            qdate = fields[30][:8] if len(fields[30]) >= 8 else ""
            out[code] = {
                "date": f"{qdate[:4]}-{qdate[4:6]}-{qdate[6:8]}" if len(qdate) == 8 else "",
                "open": op,
                "high": hi,
                "low": lo,
                "close": now_p,
                "prev_close": prev_c,
                "pct": pct,
                "bid1_vol": bid1_v,
                "ask1_vol": ask1_v,
            }
    return out


def fetch_daily_bar_for_date(code, date_str):
    """回补历史交易日时，用东财日线接口拿指定日期的真实 OHLC。"""
    dt_c = date_str.replace("-", "")
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        f"?secid={code_to_secid(code)}&fields1=f1,f2&fields2=f51,f52,f53,f54,f55,f59"
        f"&klt=101&fqt=0&beg={dt_c}&end={dt_c}"
    )
    try:
        j = json.loads(fast_fetch(url, min_interval=0.15))
    except Exception:
        return None
    kl = (j.get("data") or {}).get("klines") or []
    if not kl:
        return None
    parts = kl[0].split(",")
    if parts[0] != date_str:
        return None
    op, cl, hi, lo, pct = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])
    prev_c = cl / (1.0 + pct / 100.0) if (1.0 + pct / 100.0) > 0 else cl
    return {
        "date": date_str,
        "open": op,
        "high": hi,
        "low": lo,
        "close": cl,
        "prev_close": prev_c,
        "pct": pct,
    }


def fetch_5m_day_bars(secid, code_label, date_str):
    """拉取指定交易日的 5 分钟线，用于本地压缩留档。"""
    dt_c = date_str.replace("-", "")
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        f"?secid={secid}&fields1=f1,f2&fields2=f51,f52,f53,f54,f55,f56,f57"
        f"&klt=5&fqt=0&beg={dt_c}&end={dt_c}"
    )
    try:
        j = json.loads(fast_fetch(url, min_interval=0.18))
    except Exception:
        return []
    kl = (j.get("data") or {}).get("klines") or []
    rows = []
    for line in kl:
        parts = line.split(",")
        if not parts[0].startswith(date_str):
            continue
        tm = parts[0].split(" ")[1] if " " in parts[0] else parts[0]
        rows.append({
            "code": code_label,
            "time": tm,
            "open": parts[1],
            "close": parts[2],
            "high": parts[3],
            "low": parts[4],
            "vol": parts[5],
            "amount": parts[6],
        })
    return rows


def find_prev_zt_file(date_str):
    pool_dir = ARCHIVE_DIR / "pools"
    if not pool_dir.exists():
        return None, []
    candidates = sorted(
        p for p in pool_dir.glob("*_zt.csv") if p.name[:10] < date_str
    )
    if not candidates:
        return None, []
    latest = candidates[-1]
    prev_date = latest.name[:10]
    with latest.open(encoding="utf-8") as f:
        return prev_date, list(csv.DictReader(f))


def compute_prev_zt_outcomes_and_regime(date_str, zt_rows, zb_rows, dt_rows, use_live_quotes=True):
    """根据前一日归档涨停池和今日真实行情，计算昨涨停溢价、昨连板大面率与各板晋级率。"""
    prev_date, prev_rows = find_prev_zt_file(date_str)
    today_zt_codes = {r["code"] for r in zt_rows}

    valid_today = [r for r in zt_rows if not r["code"].startswith(("8", "4", "92")) and "ST" not in r["name"]]
    max_lbc = max([int(r["lbc"]) for r in valid_today], default=0)
    lbc2_cnt = sum(1 for r in valid_today if int(r["lbc"]) >= 2)

    regime = {
        "date": date_str,
        "prev_date": prev_date or "",
        "zt_cnt": len(zt_rows),
        "zb_cnt": len(zb_rows),
        "dt_cnt": len(dt_rows),
        "max_lbc": max_lbc,
        "lbc2_cnt": lbc2_cnt,
        "prev_zt_cnt": 0,
        "prev_lbc2_cnt": 0,
        "prev_zt_prem_pct": "",
        "prev_lbc2_prem_pct": "",
        "prev_lbc2_dm_rate": "",
        "promote_1to2": "",
        "promote_2to3": "",
        "promote_3to4": "",
        "top_lbc_prev": "",
        "top_lbc_broken": "",
        "top_lbc_avg_pct": "",
    }
    if not prev_rows:
        return [], regime

    prev_valid = [
        r for r in prev_rows
        if not r["code"].startswith(("8", "4", "92")) and "ST" not in r["name"]
    ]
    quotes = {}
    if use_live_quotes:
        q_live = fetch_tencent_quotes([r["code"] for r in prev_valid])
        for c, q in q_live.items():
            if q.get("date") == date_str:
                quotes[c] = q
    # Fall back to historical daily kline for any missing codes (e.g., backfill mode)
    for r in prev_valid:
        c = r["code"]
        if c not in quotes:
            bar = fetch_daily_bar_for_date(c, date_str)
            if bar:
                quotes[c] = bar

    outcome_rows = []
    all_pcts, lbc2_pcts = [], []
    lbc2_big_loss = 0
    by_lbc = {1: [0, 0], 2: [0, 0], 3: [0, 0]}  # [promoted, total]
    prev_top_lbc = max([int(r["lbc"]) for r in prev_valid], default=0)
    top_pcts = []
    top_promoted = 0

    for r in prev_valid:
        c = r["code"]
        q = quotes.get(c)
        if not q or not q.get("prev_close"):
            continue
        prev_lbc = int(r["lbc"])
        prev_c = q["prev_close"]
        open_pct = (q["open"] / prev_c - 1.0) * 100.0
        close_pct = q["pct"]
        intraday_dd = (q["high"] - q["close"]) / prev_c * 100.0
        is_big_loss = 1 if (close_pct <= -5.0 or intraday_dd >= 10.0) else 0
        promoted = 1 if c in today_zt_codes else 0

        outcome_rows.append({
            "date": date_str,
            "prev_date": prev_date,
            "code": c,
            "name": r["name"],
            "prev_lbc": prev_lbc,
            "prev_hybk": r.get("hybk", ""),
            "open": f"{q['open']:.2f}",
            "high": f"{q['high']:.2f}",
            "low": f"{q['low']:.2f}",
            "close": f"{q['close']:.2f}",
            "prev_close": f"{prev_c:.2f}",
            "open_pct": f"{open_pct:.2f}",
            "close_pct": f"{close_pct:.2f}",
            "intraday_dd_pct": f"{intraday_dd:.2f}",
            "is_big_loss": is_big_loss,
            "promoted": promoted,
        })

        all_pcts.append(close_pct)
        if prev_lbc >= 2:
            lbc2_pcts.append(close_pct)
            lbc2_big_loss += is_big_loss
        if prev_lbc in by_lbc:
            by_lbc[prev_lbc][1] += 1
            by_lbc[prev_lbc][0] += promoted
        if prev_lbc == prev_top_lbc and prev_top_lbc >= 2:
            top_pcts.append(close_pct)
            top_promoted += promoted

    outcome_rows.sort(key=lambda r: (-int(r["prev_lbc"]), r["code"]))

    def fmt_rate(p, tot):
        return f"{100.0 * p / tot:.1f}" if tot > 0 else ""

    regime["prev_zt_cnt"] = len(all_pcts)
    regime["prev_lbc2_cnt"] = len(lbc2_pcts)
    if all_pcts:
        regime["prev_zt_prem_pct"] = f"{sum(all_pcts) / len(all_pcts):.2f}"
    if lbc2_pcts:
        regime["prev_lbc2_prem_pct"] = f"{sum(lbc2_pcts) / len(lbc2_pcts):.2f}"
        regime["prev_lbc2_dm_rate"] = f"{100.0 * lbc2_big_loss / len(lbc2_pcts):.1f}"
    regime["promote_1to2"] = fmt_rate(*by_lbc[1])
    regime["promote_2to3"] = fmt_rate(*by_lbc[2])
    regime["promote_3to4"] = fmt_rate(*by_lbc[3])
    if top_pcts:
        regime["top_lbc_prev"] = prev_top_lbc
        regime["top_lbc_broken"] = 1 if top_promoted == 0 else 0
        regime["top_lbc_avg_pct"] = f"{sum(top_pcts) / len(top_pcts):.2f}"

    return outcome_rows, regime


def upsert_regime_row(regime_row):
    path = ARCHIVE_DIR / "daily_regime.csv"
    rows = []
    if path.exists():
        with path.open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["date"] != regime_row["date"]]
    rows.append({k: str(regime_row.get(k, "")) for k in REGIME_HEADER})
    rows.sort(key=lambda r: r["date"])
    return write_csv_atomic(path, REGIME_HEADER, rows)


def fetch_fenshi_1m_day(secid, code_label, date_str):
    """拉取指定交易日 1 分钟分时图（含分时均价 avg_price）。

    优先尝试 ndays=1&iscr=1：若目标日恰为最近交易日，可完整拿到 256 条
    （含 09:15-09:25 集合竞价逐分钟轨迹 + 09:30-15:00 交易分时）。
    若目标日在最近 5 个交易日内但非最新日，自动回落到 ndays=5&iscr=1 提取当日 241 条。
    """
    for ndays in (1, 5):
        url = (
            "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
            f"?secid={secid}"
            "&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
            "&fields2=f51,f52,f53,f54,f55,f56,f57,f58"
            f"&ndays={ndays}&iscr=1"
        )
        try:
            j = json.loads(fast_fetch(url, min_interval=0.16))
        except Exception:
            continue
        trends = (j.get("data") or {}).get("trends") or []
        rows = []
        for line in trends:
            if not line.startswith(date_str):
                continue
            parts = line.split(",")
            if len(parts) < 8:
                continue
            tm = parts[0].split(" ")[1] if " " in parts[0] else parts[0]
            rows.append({
                "code": code_label,
                "time": tm,
                "open": parts[1],
                "price": parts[2],
                "high": parts[3],
                "low": parts[4],
                "vol": parts[5],
                "amount": parts[6],
                "avg_price": parts[7],
            })
        if rows:
            return rows
    return []


def select_fenshi_targets(zt_rows, prev_rows, zb_rows, dt_rows, max_symbols=DEFAULT_MAX_FENSHI):
    """按研究优先级挑选当日录制 1 分钟分时图的标的清单（含指数，去重且可控上限）。"""
    targets = [
        ("1.000001", "SH000001"),
        ("0.399006", "SZ399006"),
        ("1.000852", "CSI1000"),
    ]
    seen = set()

    def add_codes(codes):
        for c in codes:
            if len(targets) >= max_symbols + 3:
                return
            if not c or c in seen or c.startswith(("8", "4", "92")):
                continue
            seen.add(c)
            targets.append((code_to_secid(c), c))

    # 1. 今日连板 + 昨日连板（最高优先级）
    add_codes([r["code"] for r in zt_rows if int(r.get("lbc") or 1) >= 2])
    add_codes([r["code"] for r in prev_rows if int(r.get("lbc") or 1) >= 2])
    # 2. 今日炸板池 + 跌停池（分歧/回封/核按钮核心样本）
    add_codes([r["code"] for r in zb_rows])
    add_codes([r["code"] for r in dt_rows])
    # 3. 今日前排首板（按首封时间升序、成交额降序）+ 昨日首板
    first_today = sorted(
        (r for r in zt_rows if int(r.get("lbc") or 1) == 1),
        key=lambda r: (int(r.get("fbt") or 150000), -int(r.get("amount") or 0)),
    )
    add_codes([r["code"] for r in first_today])
    add_codes([r["code"] for r in prev_rows if int(r.get("lbc") or 1) == 1])
    return targets


def record_fenshi_1m(date_str, zt_rows, prev_rows, zb_rows, dt_rows, max_symbols=DEFAULT_MAX_FENSHI):
    """压缩录制当日 1 分钟分时数据（含 09:15-09:25 竞价轨迹与分时均价）。"""
    targets = select_fenshi_targets(zt_rows, prev_rows, zb_rows, dt_rows, max_symbols=max_symbols)
    all_rows = []
    ok_syms = 0
    for secid, label in targets:
        bars = fetch_fenshi_1m_day(secid, label, date_str)
        if bars:
            ok_syms += 1
            all_rows.extend(bars)

    if not all_rows:
        return None
    path = ARCHIVE_DIR / "fenshi_1m" / f"{date_str}.csv.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".gz.tmp")
    with gzip.open(tmp, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FENSHI_HEADER)
        w.writeheader()
        w.writerows(all_rows)
    tmp.replace(path)
    return path, ok_syms, len(all_rows)


def record_intraday_5m(date_str, zt_rows, prev_rows):
    """压缩录制当日及昨日连板股(lbc>=2) + 上证/中证1000 的 5 分钟线。"""
    codes = set()
    for r in zt_rows:
        if int(r["lbc"]) >= 2 and not r["code"].startswith(("8", "4", "92")):
            codes.add(r["code"])
    for r in prev_rows:
        if int(r["lbc"]) >= 2 and not r["code"].startswith(("8", "4", "92")):
            codes.add(r["code"])

    targets = [("1.000001", "SH000001"), ("1.000852", "CSI1000")] + [
        (code_to_secid(c), c) for c in sorted(codes)
    ]
    all_bars = []
    for secid, label in targets:
        all_bars.extend(fetch_5m_day_bars(secid, label, date_str))

    if not all_bars:
        return None
    path = ARCHIVE_DIR / "intraday_5m" / f"{date_str}.csv.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".gz.tmp")
    with gzip.open(tmp, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=M5_HEADER)
        w.writeheader()
        w.writerows(all_bars)
    tmp.replace(path)
    return path, len(targets), len(all_bars)


def record_auction_snapshot(date_str, captured_at):
    """早盘时段录制昨日连板股开盘承接与今日 9:25 一字封单。"""
    date_c = date_str.replace("-", "")
    _, prev_rows = find_prev_zt_file(date_str)
    prev_lbc2 = [r for r in prev_rows if int(r["lbc"]) >= 2 and not r["code"].startswith(("8", "4", "92"))]
    zt_raw = fetch_topic_pool(date_c, "getTopicZTPool", "fbt%3Aasc", pagesize=200) or []

    rows = []
    # 1. Early 9:25 一字先锋
    for x in zt_raw:
        if int(x.get("fbt") or 150000) <= 93000:
            fund = x.get("fund") or 0
            rows.append({
                "captured_at": captured_at,
                "date": date_str,
                "role": "early_zt_pioneer",
                "code": str(x.get("c", "")).zfill(6),
                "name": x.get("n", ""),
                "prev_lbc": max(0, int(x.get("lbc") or 1) - 1),
                "hybk": x.get("hybk", ""),
                "open_pct": f"{x['zdp']:.2f}" if isinstance(x.get("zdp"), (int, float)) else "",
                "now_pct": f"{x['zdp']:.2f}" if isinstance(x.get("zdp"), (int, float)) else "",
                "fbt": x.get("fbt", ""),
                "fund_wan": f"{fund / 1e4:.1f}" if isinstance(fund, (int, float)) else "",
                "bid1_vol": "",
                "ask1_vol": "",
            })

    # 2. Prev lbc>=2 live open/bid/ask snapshot
    if prev_lbc2:
        quotes = fetch_tencent_quotes([r["code"] for r in prev_lbc2])
        for r in prev_lbc2:
            q = quotes.get(r["code"])
            if not q or not q.get("prev_close"):
                continue
            op_pct = (q["open"] / q["prev_close"] - 1.0) * 100.0
            rows.append({
                "captured_at": captured_at,
                "date": date_str,
                "role": "prev_lbc2",
                "code": r["code"],
                "name": r["name"],
                "prev_lbc": r["lbc"],
                "hybk": r.get("hybk", ""),
                "open_pct": f"{op_pct:.2f}",
                "now_pct": f"{q['pct']:.2f}",
                "fbt": "",
                "fund_wan": "",
                "bid1_vol": q.get("bid1_vol", ""),
                "ask1_vol": q.get("ask1_vol", ""),
            })

    if not rows:
        return None
    path = ARCHIVE_DIR / "auction" / f"{date_str}.csv"
    write_csv_atomic(path, AUCTION_HEADER, rows)
    return path, len(rows)


def record_close_day(date_str, skip_5m=False, skip_fenshi=False, use_live_quotes=True):
    date_c = date_str.replace("-", "")
    zt_raw = fetch_topic_pool(date_c, "getTopicZTPool", "fbt%3Aasc", pagesize=500)
    if zt_raw is None or len(zt_raw) == 0:
        print(f"  [archive] {date_str} 无涨停池数据，跳过")
        return False

    zb_raw = fetch_topic_pool(date_c, "getTopicZBPool", "fbt%3Aasc", pagesize=500) or []
    dt_raw = fetch_topic_pool(date_c, "getTopicDTPool", "fund%3Aasc", pagesize=500) or []
    qs_raw = fetch_topic_pool(date_c, "getTopicQSPool", "zdp%3Adesc", pagesize=500) or []

    zt_rows = parse_zt_rows(date_str, zt_raw)
    zb_rows = parse_zb_rows(date_str, zb_raw)
    dt_rows = parse_dt_rows(date_str, dt_raw)
    qs_rows = parse_qs_rows(date_str, qs_raw)

    write_csv_atomic(ARCHIVE_DIR / "pools" / f"{date_str}_zt.csv", ZT_HEADER, zt_rows)
    write_csv_atomic(ARCHIVE_DIR / "pools" / f"{date_str}_zb.csv", ZB_HEADER, zb_rows)
    write_csv_atomic(ARCHIVE_DIR / "pools" / f"{date_str}_dt.csv", DT_HEADER, dt_rows)
    write_csv_atomic(ARCHIVE_DIR / "pools" / f"{date_str}_qs.csv", QS_HEADER, qs_rows)

    lhb_rows = fetch_lhb_rows(date_str)
    if lhb_rows:
        write_csv_atomic(ARCHIVE_DIR / "lhb" / f"{date_str}.csv", LHB_HEADER, lhb_rows)
    lhb_seats = fetch_lhb_seats_rows(date_str)
    if lhb_seats:
        write_csv_atomic(ARCHIVE_DIR / "lhb_seats" / f"{date_str}.csv", LHB_SEATS_HEADER, lhb_seats)

    _, prev_rows = find_prev_zt_file(date_str)
    outcome_rows, regime = compute_prev_zt_outcomes_and_regime(
        date_str, zt_rows, zb_rows, dt_rows, use_live_quotes=use_live_quotes
    )
    if outcome_rows:
        write_csv_atomic(ARCHIVE_DIR / "prev_zt" / f"{date_str}.csv", PREV_ZT_HEADER, outcome_rows)
    upsert_regime_row(regime)

    fenshi_info = ""
    if not skip_fenshi:
        f_res = record_fenshi_1m(date_str, zt_rows, prev_rows, zb_rows, dt_rows)
        if f_res:
            _, fn_sym, fn_bars = f_res
            fenshi_info = f", 分时1m={fn_sym}标的/{fn_bars}点"

    m5_info = ""
    if not skip_5m:
        res = record_intraday_5m(date_str, zt_rows, prev_rows)
        if res:
            _, n_sym, n_bars = res
            m5_info = f", 5m={n_sym}标的/{n_bars}根"

    print(
        f"[archive] {date_str} 完成: ZT={len(zt_rows)}, ZB={len(zb_rows)}, DT={len(dt_rows)}, "
        f"QS={len(qs_rows)}, LHB={len(lhb_rows)}, 大面率={regime['prev_lbc2_dm_rate'] or '-'}%{fenshi_info}{m5_info}"
    )
    return True


def backfill_recent(skip_5m=False, skip_fenshi=False):
    """补录东财当前仍存活的最近约 15 个交易日明细（按时间正序，确保 prev_zt 连续）。"""
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        "?secid=1.000001&fields1=f1,f2&fields2=f51&klt=101&fqt=0&beg=20261015&end=20991231"
    )
    kl = (json.loads(fast_fetch(url, min_interval=0.2)).get("data") or {}).get("klines") or []
    recent_dates = [line.split(",")[0] for line in kl][-22:]
    recorded = 0
    for dt in recent_dates:
        if record_close_day(dt, skip_5m=skip_5m, skip_fenshi=skip_fenshi, use_live_quotes=False):
            recorded += 1
    print(f"[archive] 最近区间补录完成，共 {recorded} 个交易日")


def main():
    parser = argparse.ArgumentParser(description="A股短线情绪与分时档案录制器")
    parser.add_argument("--date", help="指定交易日 YYYY-MM-DD")
    parser.add_argument("--slot", help="指定时段 open/close/night/auto")
    parser.add_argument("--backfill-recent", action="store_true", help="补录东财仍在线的最近约15个交易日")
    parser.add_argument("--backfill-lhb-seats", action="store_true", help="仅补录已归档交易日的龙虎榜营业部席位")
    parser.add_argument("--skip-5m", action="store_true", help="跳过 5 分钟线录制")
    parser.add_argument("--skip-fenshi", action="store_true", help="跳过 1 分钟分时图录制")
    args = parser.parse_args()

    if args.backfill_lhb_seats:
        lhb_dir = ARCHIVE_DIR / "lhb"
        dates = sorted(p.stem for p in lhb_dir.glob("*.csv")) if lhb_dir.exists() else []
        ok = 0
        for dt in dates:
            seats = fetch_lhb_seats_rows(dt)
            if seats:
                write_csv_atomic(ARCHIVE_DIR / "lhb_seats" / f"{dt}.csv", LHB_SEATS_HEADER, seats)
                ok += 1
                print(f"[archive] 龙虎榜席位 {dt}: {len(seats)} 条")
        print(f"[archive] 龙虎榜席位补录完成，共 {ok} 天")
        return 0

    if args.backfill_recent:
        backfill_recent(skip_5m=args.skip_5m, skip_fenshi=args.skip_fenshi)
        return 0

    now = datetime.now(snapshot.beijing_tz())
    stamp = now.strftime("%Y-%m-%d %H:%M")

    # 默认优先读取 snapshot.py 刚刚写出的 status.json（复用其交易日判定与跨零点补录结果）
    status = {}
    status_path = snapshot.DATA_DIR / "status.json"
    if status_path.exists():
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
        except Exception:
            status = {}

    target_date = args.date or status.get("target_date") or now.strftime("%Y-%m-%d")
    slot = args.slot or status.get("slot") or snapshot.resolve_slot(
        os.environ.get("SNAPSHOT_SLOT", "auto"), now
    )

    if not args.date and status.get("market_state") in ("non_trading", "unavailable"):
        print(f"[archive] status={status.get('market_state')}，跳过录制")
        return 0

    if slot == "open":
        res = record_auction_snapshot(target_date, stamp)
        if res:
            print(f"[archive] 早盘快照 {target_date} 完成: {res[1]} 行 -> {res[0].name}")
        else:
            print(f"[archive] 早盘快照 {target_date} 无可录数据")
    elif slot in snapshot.FINAL_SLOTS:
        record_close_day(
            target_date,
            skip_5m=args.skip_5m,
            skip_fenshi=args.skip_fenshi,
            use_live_quotes=(args.date is None),
        )
    else:
        print(f"[archive] 时段 {slot} 无需录制档案")
    return 0


if __name__ == "__main__":
    sys.exit(main())
