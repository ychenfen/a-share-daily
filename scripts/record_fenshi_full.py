#!/usr/bin/env python3
"""全市场 A 股 1 分钟分时图分片录制器（零第三方依赖，面向 GitHub Releases 归档）。

架构设计：
1. list-symbols: 拉取全市场 ~5,200+ A 股代码表（东财数据中心主源 + 腾讯排行兜底）并附核心指数。
2. fetch-shard:  在 GitHub Actions Matrix 的 N 个独立 Runner IP 上分片并行抓 1 分钟分时图：
                 - 主源：东财 trends2 (ndays=1&iscr=1 含 09:15-09:25 竞价轨迹与均价 VWAP；
                         历史回补近 5 日自动切 ndays=5&iscr=1)
                 - 兜底：腾讯 web.ifzq.gtimg.cn 分钟分时接口（单股失败自动补齐）
3. merge:        合并全部分片为一个压缩文件 fenshi_all_YYYY-MM-DD.csv.gz（约 17 MB/天），
                 校验完整率并生成带 SHA-256 校验码的 manifest.json，供上传 GitHub Releases
                 以及后续按月批量转存 Google Drive 后清理旧 Release。
"""

import argparse
import csv
import gzip
import hashlib
import json
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import snapshot  # noqa: E402

FENSHI_HEADER = ["code", "time", "open", "price", "high", "low", "vol", "amount", "avg_price"]

CORE_INDICES = [
    {"code": "SH000001", "secid": "1.000001", "name": "上证指数"},
    {"code": "SZ399001", "secid": "0.399001", "name": "深证成指"},
    {"code": "SZ399006", "secid": "0.399006", "name": "创业板指"},
    {"code": "SH000300", "secid": "1.000300", "name": "沪深300"},
    {"code": "SH000688", "secid": "1.000688", "name": "科创50"},
    {"code": "CSI1000", "secid": "1.000852", "name": "中证1000"},
]

_TLS = threading.local()


def http_get(url, decode="utf-8", timeout=12, retries=2):
    """线程安全的零依赖 HTTP GET，失败带指数退避与 curl 回落。"""
    headers = {"User-Agent": snapshot.UA}
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return resp.read().decode(decode, errors="replace")
        except (urllib.error.URLError, OSError, ssl.SSLError) as err:
            last_err = err
            if attempt == retries:
                try:
                    out = subprocess.run(
                        ["curl", "-sS", "--compressed", "--max-time", str(timeout),
                         "-H", f"User-Agent: {snapshot.UA}", url],
                        capture_output=True, timeout=timeout + 8, check=True,
                    ).stdout
                    if out.strip():
                        return out.decode(decode, errors="replace")
                except Exception as curl_err:
                    last_err = curl_err
            else:
                time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f"GET 失败: {url} ({last_err})")


def code_to_secid(code):
    c = str(code).zfill(6)
    return f"1.{c}" if c.startswith(("6", "9")) else f"0.{c}"


def code_to_qq(code):
    c = str(code)
    if c.startswith(("SH", "SZ", "CSI")):
        mapping = {
            "SH000001": "sh000001",
            "SZ399001": "sz399001",
            "SZ399006": "sz399006",
            "SH000300": "sh000300",
            "SH000688": "sh000688",
            "CSI1000": "sh000852",
        }
        return mapping.get(c, "")
    c = c.zfill(6)
    if c.startswith(("6", "9")):
        return f"sh{c}"
    if c.startswith(("8", "4")):
        return f"bj{c}"
    return f"sz{c}"


def detect_latest_trading_date():
    quotes, quote_date = snapshot.fetch_indexes()
    if not quotes or not quote_date:
        raise RuntimeError("无法获取上证指数行情日期")
    return quote_date


def fetch_all_a_share_symbols():
    """获取全市场 A 股列表（主源：东财数据中心；兜底：上交所+深交所/腾讯）。"""
    symbols = {}
    # 主源：datacenter-web.eastmoney.com RPT_DMSK_TS_STOCKNEW (仅需约 11 页)
    try:
        page = 1
        total_pages = 1
        while page <= total_pages and page <= 30:
            url = (
                "https://datacenter-web.eastmoney.com/api/data/v1/get"
                "?reportName=RPT_DMSK_TS_STOCKNEW"
                "&columns=SECURITY_CODE,SECURITY_NAME_ABBR"
                f"&pageNumber={page}&pageSize=500"
            )
            j = json.loads(http_get(url, timeout=15))
            res = j.get("result") or {}
            total_pages = int(res.get("pages") or 1)
            for row in res.get("data") or []:
                code = str(row.get("SECURITY_CODE") or "").strip().zfill(6)
                name = str(row.get("SECURITY_NAME_ABBR") or "").strip()
                if len(code) == 6 and code.isdigit():
                    symbols[code] = {"code": code, "secid": code_to_secid(code), "name": name}
            page += 1
            time.sleep(0.15)
    except Exception as e:
        print(f"[warn] 东财数据中心拉全市场名单异常: {e}", file=sys.stderr)

    # 若主源不足 4000 只，用腾讯排行接口兜底补齐
    if len(symbols) < 4000:
        print(f"[warn] 主源仅 {len(symbols)} 只，启用腾讯全A列表兜底", file=sys.stderr)
        try:
            offset = 0
            while offset < 6500:
                url = (
                    "https://proxy.finance.qq.com/cgi/cgi-bin/rank/hs/getBoardRankList"
                    f"?_appver=11.17.0&board_code=aStock&sort_type=price&direct=down"
                    f"&offset={offset}&count=200"
                )
                j = json.loads(http_get(url, timeout=15))
                items = (j.get("data") or {}).get("rank_list") or []
                if not items:
                    break
                for row in items:
                    raw_c = str(row.get("code") or "")
                    code = raw_c[-6:] if len(raw_c) >= 6 else ""
                    if len(code) == 6 and code.isdigit() and code not in symbols:
                        symbols[code] = {
                            "code": code,
                            "secid": code_to_secid(code),
                            "name": str(row.get("name") or ""),
                        }
                offset += 200
                time.sleep(0.1)
        except Exception as e:
            print(f"[warn] 腾讯兜底名单异常: {e}", file=sys.stderr)

    ordered = list(CORE_INDICES) + [symbols[k] for k in sorted(symbols)]
    return ordered


def parse_em_trends_lines(code, trends, date_str):
    rows = []
    for line in trends:
        if not line.startswith(date_str):
            continue
        parts = line.split(",")
        if len(parts) < 8:
            continue
        tm = parts[0].split(" ")[1] if " " in parts[0] else parts[0]
        rows.append({
            "code": code,
            "time": tm,
            "open": parts[1],
            "price": parts[2],
            "high": parts[3],
            "low": parts[4],
            "vol": parts[5],
            "amount": parts[6],
            "avg_price": parts[7],
        })
    return rows


def fetch_fenshi_eastmoney(secid, code, date_str, is_latest_day=True):
    """主源：东财 trends2 分时图（最新日含 09:15-09:25 竞价与均价）。"""
    ndays_order = (1, 5) if is_latest_day else (5,)
    for ndays in ndays_order:
        url = (
            "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
            f"?secid={secid}"
            "&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
            "&fields2=f51,f52,f53,f54,f55,f56,f57,f58"
            f"&ndays={ndays}&iscr=1"
        )
        try:
            j = json.loads(http_get(url, timeout=10, retries=1))
        except Exception:
            continue
        trends = (j.get("data") or {}).get("trends") or []
        rows = parse_em_trends_lines(code, trends, date_str)
        if rows:
            return rows
    return []


def fetch_fenshi_tencent(code, date_str):
    """兜底源：腾讯分钟分时查询（仅当返回日期严格等于目标交易日时采纳）。"""
    qq_code = code_to_qq(code)
    if not qq_code:
        return []
    url = f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?code={qq_code}"
    try:
        j = json.loads(http_get(url, timeout=10, retries=1))
    except Exception:
        return []
    block = ((j.get("data") or {}).get(qq_code) or {}).get("data") or {}
    raw_date = str(block.get("date") or "")
    if raw_date != date_str.replace("-", ""):
        return []
    lines = block.get("data") or []
    rows = []
    prev_vol = 0.0
    prev_amt = 0.0
    for line in lines:
        parts = line.split()
        if len(parts) < 4:
            continue
        hhmm = parts[0]
        if len(hhmm) != 4:
            continue
        tm = f"{hhmm[:2]}:{hhmm[2:]}"
        price = parts[1]
        try:
            cum_vol = float(parts[2])
            cum_amt = float(parts[3])
            bar_vol = max(0.0, cum_vol - prev_vol)
            bar_amt = max(0.0, cum_amt - prev_amt)
            prev_vol, prev_amt = cum_vol, cum_amt
            avg_p = f"{cum_amt / (cum_vol * 100.0):.3f}" if cum_vol > 0 else price
        except ValueError:
            continue
        rows.append({
            "code": code,
            "time": tm,
            "open": price,
            "price": price,
            "high": price,
            "low": price,
            "vol": f"{int(bar_vol)}",
            "amount": f"{bar_amt:.2f}",
            "avg_price": avg_p,
        })
    return rows


def fetch_one_symbol(item, date_str, is_latest_day=True):
    code = item["code"]
    secid = item["secid"]
    rows = fetch_fenshi_eastmoney(secid, code, date_str, is_latest_day=is_latest_day)
    if rows:
        return code, "em", rows
    if is_latest_day:
        rows = fetch_fenshi_tencent(code, date_str)
        if rows:
            return code, "qq", rows
    return code, "fail", []


def cmd_list_symbols(args):
    latest_date = detect_latest_trading_date()
    target_date = args.date or latest_date
    symbols = fetch_all_a_share_symbols()
    if args.limit and args.limit > 0:
        symbols = symbols[:args.limit]
    payload = {
        "schema_version": 1,
        "date": target_date,
        "latest_market_date": latest_date,
        "is_latest_day": (target_date == latest_date),
        "generated_at": datetime.now(snapshot.beijing_tz()).strftime("%Y-%m-%d %H:%M"),
        "count": len(symbols),
        "symbols": symbols,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[list-symbols] date={target_date} (latest={latest_date}), count={len(symbols)} -> {out_path}")
    return 0


def cmd_fetch_shard(args):
    meta = json.loads(Path(args.symbols).read_text(encoding="utf-8"))
    date_str = args.date or meta["date"]
    is_latest_day = bool(meta.get("is_latest_day", True)) and (date_str == meta.get("latest_market_date", date_str))
    all_symbols = meta["symbols"]
    shard_items = [s for idx, s in enumerate(all_symbols) if idx % args.shard_total == args.shard_index]

    t0 = time.time()
    all_rows = []
    em_ok = 0
    qq_ok = 0
    failed = []

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(fetch_one_symbol, item, date_str, is_latest_day) for item in shard_items]
        for fut in as_completed(futs):
            code, src, rows = fut.result()
            if src == "em":
                em_ok += 1
                all_rows.extend(rows)
            elif src == "qq":
                qq_ok += 1
                all_rows.extend(rows)
            else:
                failed.append(code)

    all_rows.sort(key=lambda r: (r["code"], r["time"]))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FENSHI_HEADER)
        w.writeheader()
        w.writerows(all_rows)

    stats = {
        "shard_index": args.shard_index,
        "shard_total": args.shard_total,
        "date": date_str,
        "requested": len(shard_items),
        "em_ok": em_ok,
        "qq_ok": qq_ok,
        "failed_count": len(failed),
        "failed_codes": sorted(failed)[:200],
        "rows": len(all_rows),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    stats_path = Path(args.stats_out) if args.stats_out else out_path.with_suffix(".stats.json")
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"[shard {args.shard_index}/{args.shard_total}] req={len(shard_items)} "
        f"em={em_ok} qq={qq_ok} fail={len(failed)} rows={len(all_rows)} ({stats['elapsed_sec']}s)"
    )
    return 0


def cmd_merge(args):
    shards_dir = Path(args.shards_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    date_str = args.date
    shard_csvs = sorted(shards_dir.rglob("shard_*.csv.gz"))
    shard_stats = sorted(shards_dir.rglob("*.stats.json"))
    if not shard_csvs:
        print("[merge] 未找到任何分片文件 shard_*.csv.gz", file=sys.stderr)
        return 1

    total_req = 0
    total_em = 0
    total_qq = 0
    total_fail = 0
    failed_sample = []
    for sp in shard_stats:
        st = json.loads(sp.read_text(encoding="utf-8"))
        if not date_str:
            date_str = st.get("date")
        total_req += int(st.get("requested") or 0)
        total_em += int(st.get("em_ok") or 0)
        total_qq += int(st.get("qq_ok") or 0)
        total_fail += int(st.get("failed_count") or 0)
        failed_sample.extend(st.get("failed_codes") or [])

    if not date_str:
        print("[merge] 无法确定目标日期", file=sys.stderr)
        return 1

    out_gz = out_dir / f"fenshi_all_{date_str}.csv.gz"
    seen_codes = set()
    total_rows = 0
    has_auction_rows = 0

    with gzip.open(out_gz, "wt", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(FENSHI_HEADER)
        for gz_path in shard_csvs:
            with gzip.open(gz_path, "rt", encoding="utf-8", newline="") as in_f:
                reader = csv.reader(in_f)
                header = next(reader, None)
                if header != FENSHI_HEADER:
                    print(f"[merge] 分片表头不匹配: {gz_path} -> {header}", file=sys.stderr)
                    return 1
                for row in reader:
                    writer.writerow(row)
                    total_rows += 1
                    seen_codes.add(row[0])
                    if len(row) > 1 and "09:15" <= row[1] <= "09:25":
                        has_auction_rows += 1

    sha256 = hashlib.sha256()
    with out_gz.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            sha256.update(chunk)

    size_bytes = out_gz.stat().st_size
    coverage = (len(seen_codes) / total_req) if total_req > 0 else 0.0
    manifest = {
        "schema_version": 1,
        "date": date_str,
        "release_tag": f"fenshi-{date_str[:7]}",
        "file": out_gz.name,
        "size_bytes": size_bytes,
        "size_mb": round(size_bytes / (1024 * 1024), 2),
        "sha256": sha256.hexdigest(),
        "requested_symbols": total_req,
        "recorded_symbols": len(seen_codes),
        "coverage_pct": round(coverage * 100.0, 2),
        "em_ok": total_em,
        "qq_fallback_ok": total_qq,
        "failed_count": total_fail,
        "failed_sample": sorted(set(failed_sample))[:100],
        "total_rows": total_rows,
        "auction_rows_0915_0925": has_auction_rows,
        "shards": len(shard_csvs),
    }
    manifest_path = out_dir / f"fenshi_all_{date_str}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"[merge] {out_gz.name}: {len(seen_codes)}/{total_req} ({manifest['coverage_pct']}%), "
        f"rows={total_rows}, auction_rows={has_auction_rows}, size={manifest['size_mb']} MB, "
        f"sha256={manifest['sha256'][:12]}..."
    )

    if len(seen_codes) < args.min_symbols or coverage < args.min_coverage:
        print(
            f"[merge] 完整性门禁未通过: recorded={len(seen_codes)} (min={args.min_symbols}), "
            f"coverage={coverage:.2%} (min={args.min_coverage:.0%})",
            file=sys.stderr,
        )
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="全市场 A 股 1 分钟分时图分片录制器")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list-symbols")
    p_list.add_argument("--date", default="", help="目标交易日 YYYY-MM-DD（留空自动取最近交易日）")
    p_list.add_argument("--out", required=True)
    p_list.add_argument("--limit", type=int, default=0, help="测试用：限制拉取前 N 只标的")

    p_shard = sub.add_parser("fetch-shard")
    p_shard.add_argument("--symbols", required=True)
    p_shard.add_argument("--shard-index", type=int, required=True)
    p_shard.add_argument("--shard-total", type=int, required=True)
    p_shard.add_argument("--date", default="")
    p_shard.add_argument("--workers", type=int, default=3)
    p_shard.add_argument("--out", required=True)
    p_shard.add_argument("--stats-out", default="")

    p_merge = sub.add_parser("merge")
    p_merge.add_argument("--shards-dir", required=True)
    p_merge.add_argument("--date", default="")
    p_merge.add_argument("--out-dir", required=True)
    p_merge.add_argument("--min-symbols", type=int, default=4500)
    p_merge.add_argument("--min-coverage", type=float, default=0.88)

    args = parser.parse_args()
    if args.cmd == "list-symbols":
        return cmd_list_symbols(args)
    if args.cmd == "fetch-shard":
        return cmd_fetch_shard(args)
    if args.cmd == "merge":
        return cmd_merge(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
