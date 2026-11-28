#!/usr/bin/env python3
"""更细粒度盘口录制器（零第三方依赖，传按月 GitHub Release，不占 Git 历史）。

每日收盘后录制两类“过时即清空”的高频客观盘面数据：
1. changes_all_YYYY-MM-DD.csv.gz: 全市场秒级盘口异动流水（封涨停/开板/火箭发射/大笔买卖等，约 2 万条/天，~400KB）
2. ticks_core_YYYY-MM-DD.csv.gz:  核心活跃股池（今日连板+昨日连板+炸板+跌停+前排首板，默认上限 150 只）
                                  全天 3 秒级分笔成交（含 09:15-09:25 3 秒竞价切片，带 B/S 方向，~4-6MB）
3. fine_YYYY-MM-DD.manifest.json: 条数、覆盖标的数与 SHA-256 校验清单。

注意：东财 getAllStockChanges 与 getStockFenShi 仅保留最近一个交易日，
      因此只应在 target_date == 最新交易日 时运行。
"""

import argparse
import csv
import gzip
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import record_archive  # noqa: E402
import record_fenshi_full as rff  # noqa: E402

CHANGE_TYPES = {
    "8201": "火箭发射",
    "8202": "快速反弹",
    "8193": "大笔买入",
    "4": "封涨停板",
    "32": "打开跌停板",
    "64": "有大买盘",
    "8207": "竞价上涨",
    "8209": "高开5日线",
    "8211": "向上缺口",
    "8213": "60日新高",
    "8215": "60日大幅上涨",
    "8204": "加速下跌",
    "8203": "高台跳水",
    "8194": "大笔卖出",
    "8": "封跌停板",
    "16": "打开涨停板",
    "128": "有大卖盘",
    "8208": "竞价下跌",
    "8210": "低开5日线",
    "8212": "向下缺口",
    "8214": "60日新低",
    "8216": "60日大幅下跌",
}

CHANGES_HEADER = ["date", "time", "code", "market", "name", "type_code", "type_name", "info"]
TICKS_HEADER = ["code", "time", "price", "vol", "bs"]


def fmt_hhmmss(raw):
    s = str(raw).zfill(6)
    return f"{s[:2]}:{s[2:4]}:{s[4:6]}" if len(s) == 6 else s


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_all_market_changes(date_str):
    """分页拉取全市场当日秒级盘口异动流水。"""
    type_param = ",".join(CHANGE_TYPES.keys())
    rows = []
    seen = set()
    page = 0
    pagesize = 1000
    total_reported = None
    while page < 60:
        url = (
            "https://push2ex.eastmoney.com/getAllStockChanges"
            f"?type={type_param}&pageindex={page}&pagesize={pagesize}"
            "&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzchanges"
        )
        try:
            j = json.loads(rff.http_get(url, timeout=12, retries=2))
        except Exception as e:
            print(f"  [fine] 盘口异动第 {page} 页失败: {e}", file=sys.stderr)
            break
        data = j.get("data") or {}
        if total_reported is None:
            total_reported = int(data.get("tc") or 0)
        items = data.get("allstock") or []
        if not items:
            break
        for x in items:
            tm = fmt_hhmmss(x.get("tm", ""))
            code = str(x.get("c", "")).zfill(6)
            tcode = str(x.get("t", ""))
            info = str(x.get("i", ""))
            key = (tm, code, tcode, info)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "date": date_str,
                "time": tm,
                "code": code,
                "market": x.get("m", ""),
                "name": x.get("n", ""),
                "type_code": tcode,
                "type_name": CHANGE_TYPES.get(tcode, tcode),
                "info": info,
            })
        if len(items) < pagesize or (total_reported and (page + 1) * pagesize >= total_reported):
            break
        page += 1
        time.sleep(0.15)
    rows.sort(key=lambda r: (r["time"], r["code"], r["type_code"]))
    return rows, total_reported or len(rows)


def fetch_stock_ticks_em(code):
    """东财 3 秒级全天分笔成交（单次请求，含 09:15 起 3 秒集合竞价切片）。"""
    c = str(code).zfill(6)
    market = 1 if c.startswith(("6", "9")) else 0
    # 东财 id 规则：沪市 code + "1"，深市/北交 code + "2"
    id_suffix = "1" if market == 1 else "2"
    url = (
        "https://push2ex.eastmoney.com/getStockFenShi"
        f"?pagesize=5000&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzfscj"
        f"&pageindex=0&id={c}{id_suffix}&sort=1&ft=1&code={c}&market={market}"
    )
    try:
        j = json.loads(rff.http_get(url, timeout=12, retries=1))
    except Exception:
        return []
    items = (j.get("data") or {}).get("data") or []
    rows = []
    for x in items:
        p = x.get("p")
        rows.append({
            "code": c,
            "time": fmt_hhmmss(x.get("t", "")),
            "price": f"{p / 1000.0:.2f}" if isinstance(p, (int, float)) else "",
            "vol": int(x.get("v") or 0),
            "bs": int(x.get("bs") or 0),
        })
    return rows


def fetch_stock_ticks_qq(code):
    """腾讯 3 秒级逐笔成交分页兜底。"""
    qq_code = rff.code_to_qq(code)
    if not qq_code:
        return []
    bs_map = {"B": 2, "S": 1, "M": 4}
    rows = []
    for page in range(0, 120):
        url = f"https://stock.gtimg.cn/data/index.php?appn=detail&action=data&c={qq_code}&p={page}"
        try:
            raw = rff.http_get(url, decode="gbk", timeout=10, retries=1)
        except Exception:
            break
        if ',"' not in raw:
            break
        body = raw[raw.index(',"') + 2:raw.rindex('"')]
        if not body:
            break
        for seg in body.split("|"):
            parts = seg.split("/")
            if len(parts) < 7:
                continue
            rows.append({
                "code": str(code).zfill(6),
                "time": parts[1],
                "price": parts[2],
                "vol": parts[4],
                "bs": bs_map.get(parts[6], 0),
            })
    return rows


def select_core_tick_codes(date_str, max_symbols=150):
    """实时拉当日涨停/炸板/跌停池 + 读取本地前一日涨停池，按优先级挑核心股录 3 秒级逐笔。"""
    dt_c = date_str.replace("-", "")
    zt_raw = record_archive.fetch_topic_pool(dt_c, "getTopicZTPool", "fbt%3Aasc", pagesize=500) or []
    zb_raw = record_archive.fetch_topic_pool(dt_c, "getTopicZBPool", "fbt%3Aasc", pagesize=500) or []
    dt_raw = record_archive.fetch_topic_pool(dt_c, "getTopicDTPool", "fund%3Aasc", pagesize=500) or []

    zt_rows = record_archive.parse_zt_rows(date_str, zt_raw)
    zb_rows = record_archive.parse_zb_rows(date_str, zb_raw)
    dt_rows = record_archive.parse_dt_rows(date_str, dt_raw)
    _, prev_rows = record_archive.find_prev_zt_file(date_str)

    targets = record_archive.select_fenshi_targets(
        zt_rows, prev_rows, zb_rows, dt_rows, max_symbols=max_symbols
    )
    # 剔除指数（getStockFenShi 仅面向个股）
    return [code for _, code in targets if len(code) == 6 and code.isdigit()]


def run_record(date_str, out_dir, max_symbols=150, workers=4):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # 1. 全市场秒级盘口异动
    changes, reported_tc = fetch_all_market_changes(date_str)
    changes_gz = out_dir / f"changes_all_{date_str}.csv.gz"
    with gzip.open(changes_gz, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CHANGES_HEADER)
        w.writeheader()
        w.writerows(changes)

    # 2. 核心池 3 秒级逐笔成交
    codes = select_core_tick_codes(date_str, max_symbols=max_symbols)
    tick_rows = []
    em_ok = 0
    qq_ok = 0
    failed = []

    def _one(code):
        rows = fetch_stock_ticks_em(code)
        if rows:
            return code, "em", rows
        rows = fetch_stock_ticks_qq(code)
        if rows:
            return code, "qq", rows
        return code, "fail", []

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed([ex.submit(_one, c) for c in codes]):
            c, src, rows = fut.result()
            if src == "em":
                em_ok += 1
                tick_rows.extend(rows)
            elif src == "qq":
                qq_ok += 1
                tick_rows.extend(rows)
            else:
                failed.append(c)

    tick_rows.sort(key=lambda r: (r["code"], r["time"]))
    ticks_gz = out_dir / f"ticks_core_{date_str}.csv.gz"
    with gzip.open(ticks_gz, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=TICKS_HEADER)
        w.writeheader()
        w.writerows(tick_rows)

    manifest = {
        "schema_version": 1,
        "date": date_str,
        "release_tag": f"fenshi-{date_str[:7]}",
        "elapsed_sec": round(time.time() - t0, 1),
        "changes": {
            "file": changes_gz.name,
            "rows": len(changes),
            "reported_tc": reported_tc,
            "size_bytes": changes_gz.stat().st_size,
            "sha256": sha256_file(changes_gz),
        },
        "ticks_core": {
            "file": ticks_gz.name,
            "requested_symbols": len(codes),
            "recorded_symbols": em_ok + qq_ok,
            "em_ok": em_ok,
            "qq_fallback_ok": qq_ok,
            "failed_count": len(failed),
            "failed_codes": sorted(failed)[:50],
            "rows": len(tick_rows),
            "size_bytes": ticks_gz.stat().st_size,
            "sha256": sha256_file(ticks_gz),
        },
    }
    manifest_path = out_dir / f"fine_{date_str}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"[fine] {date_str} 完成 ({manifest['elapsed_sec']}s): "
        f"盘口异动={len(changes)}条 ({changes_gz.stat().st_size/1024:.0f}KB), "
        f"核心3秒逐笔={em_ok+qq_ok}/{len(codes)}只/{len(tick_rows)}条 ({ticks_gz.stat().st_size/1024/1024:.2f}MB)"
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description="全市场秒级盘口异动 + 核心池 3 秒级逐笔录制器")
    parser.add_argument("--date", default="", help="目标交易日 YYYY-MM-DD（留空自动取最近交易日）")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-symbols", type=int, default=150)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    latest = rff.detect_latest_trading_date()
    target_date = args.date or latest
    if target_date != latest:
        print(f"[fine] 目标日 {target_date} != 最新交易日 {latest}，东财盘口异动与逐笔仅保留最新日，跳过")
        return 0
    return run_record(target_date, args.out_dir, max_symbols=args.max_symbols, workers=args.workers)


if __name__ == "__main__":
    sys.exit(main())
