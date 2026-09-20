#!/usr/bin/env python3
"""回填指数历史数据。

一次性脚本，把过去 N 年的指数日线补进 data/<年>.csv，让仓库一开始就有
足够画图和回测的历史。

只回填指数收盘价、涨跌幅和两市成交额——这几项东财 K 线接口一次请求就
给全。涨跌平家数是实时快照没有历史；涨停跌停虽然能按日期查，但回填一年
要请求两百多次，必被东财限流。这两类只能从今天起逐日累积，所以历史行的
对应列是空的。

已经有数据的日期不会被覆盖，只补空列。

用法：
    python3 scripts/backfill.py           # 默认回填 2 年
    python3 scripts/backfill.py --years 5
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshot import (  # noqa: E402
    CSV_HEADER,
    DATA_DIR,
    INDEXES,
    beijing_tz,
    daily_csv_paths,
    fetch,
    render_readme,
)

# 两市成交额只算这两个，跟 snapshot.py 口径保持一致
AMOUNT_CODES = ("sh000001", "sz399001")


def to_secid(code):
    """腾讯代码转东财 secid：sh000001 -> 1.000001，sz399001 -> 0.399001。"""
    market = "1" if code.startswith("sh") else "0"
    return f"{market}.{code[2:]}"


def fetch_kline(code, beg):
    """拉单个指数的日线。返回 {日期: {close, pct, amount_yi}}。"""
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        f"?secid={to_secid(code)}&klt=101&fqt=1&beg={beg}&end=20500101"
        "&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
    )
    data = json.loads(fetch(url)).get("data")
    if not data or not data.get("klines"):
        raise RuntimeError(f"{code} 没有返回 K 线数据")

    out = {}
    for line in data["klines"]:
        f = line.split(",")
        # f51 日期, f53 收盘, f57 成交额(元), f59 涨跌幅
        out[f[0]] = {
            "close": float(f[2]),
            "pct": float(f[8]),
            "amount_yi": float(f[6]) / 1e8,
        }
    return out


def load_existing():
    """读出所有已有行，按日期索引。"""
    rows = {}
    for path in daily_csv_paths():
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows[row["date"]] = row
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", type=int, default=2, help="回填几年，默认 2")
    args = parser.parse_args()

    beg = f"{datetime.now().year - args.years}0101"
    print(f"回填 {beg} 之后的指数数据")

    klines = {}
    for code, name in INDEXES:
        try:
            klines[code] = fetch_kline(code, beg)
            print(f"  {name}: {len(klines[code])} 个交易日")
        except (
            OSError,
            json.JSONDecodeError,
            RuntimeError,
            KeyError,
            IndexError,
            ValueError,
        ) as e:
            print(f"  {name} 拉取失败: {e}", file=sys.stderr)
            return 1

    existing = load_existing()
    # 以上证的交易日历为准，它最全
    all_dates = sorted(klines["sh000001"])

    added = filled = 0
    for date in all_dates:
        row = existing.get(date)
        if row is None:
            row = {col: "" for col in CSV_HEADER}
            row["date"] = date
            existing[date] = row
            added += 1
            touched = True
        else:
            touched = False

        for code, name in INDEXES:
            bar = klines[code].get(date)
            if not bar:
                continue
            for col, value in (
                (f"{name}_close", f"{bar['close']:.2f}"),
                (f"{name}_pct", f"{bar['pct']:.2f}"),
            ):
                # 已有值一律不动，只补空的，免得覆盖当日实盘抓到的数据
                if not row.get(col):
                    row[col] = value
                    touched = True

        if not row.get("amount_yi"):
            total = sum(
                klines[c][date]["amount_yi"]
                for c in AMOUNT_CODES
                if date in klines.get(c, {})
            )
            if total:
                row["amount_yi"] = f"{total:.1f}"
                touched = True

        if touched:
            filled += 1

    # 按年份分文件写回
    by_year = {}
    for date, row in existing.items():
        by_year.setdefault(date[:4], []).append(row)

    for year, rows in sorted(by_year.items()):
        rows.sort(key=lambda r: r["date"])
        path = DATA_DIR / f"{year}.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CSV_HEADER)
            w.writeheader()
            for row in rows:
                w.writerow({col: row.get(col, "") for col in CSV_HEADER})
        print(f"  写入 {path.name}: {len(rows)} 行")

    stamp = datetime.now(beijing_tz()).strftime("%Y-%m-%d %H:%M")
    render_readme(stamp)
    print(f"完成：新增 {added} 个交易日，共更新 {filled} 行")
    return 0


if __name__ == "__main__":
    sys.exit(main())
