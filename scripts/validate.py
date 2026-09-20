#!/usr/bin/env python3
"""Validate repository data before an automated commit is pushed."""

import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshot import (  # noqa: E402
    CSV_HEADER,
    DATA_DIR,
    PULSE_HEADER,
    ROOT,
    SECTOR_CSV,
    SECTOR_HEADER,
    daily_csv_paths,
    load_daily_rows,
)


def valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def main():
    errors = []
    checks = 0
    seen_dates = set()

    paths = daily_csv_paths()
    if not paths:
        errors.append("没有找到 data/YYYY.csv 行情年表")

    for path in paths:
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        checks += 1
        # 历史年表可能早于新情绪列；允许它是当前 schema 的有序前缀，
        # 新写入的年份仍由 snapshot/backfill 自动使用完整表头。
        expected = CSV_HEADER[: len(reader.fieldnames or [])]
        if reader.fieldnames != expected:
            errors.append(f"{path}: 表头不是当前 CSV_HEADER 的有序前缀")
        dates = [row.get("date") for row in rows]
        if dates != sorted(dates):
            errors.append(f"{path}: 日期未按升序排列")
        for date in dates:
            if not valid_date(date):
                errors.append(f"{path}: 非法日期 {date!r}")
            if date in seen_dates:
                errors.append(f"{path}: 重复交易日 {date}")
            seen_dates.add(date)

    pulse_dir = DATA_DIR / "pulses"
    for path in sorted(pulse_dir.glob("*.csv")) if pulse_dir.exists() else []:
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        checks += 1
        if reader.fieldnames != PULSE_HEADER:
            errors.append(f"{path}: 盘中数据表头不一致")
        captured = [row.get("captured_at") for row in rows]
        if len(captured) != len(set(captured)):
            errors.append(f"{path}: 存在重复 captured_at")
        if captured != sorted(captured):
            errors.append(f"{path}: captured_at 未按升序排列")

    sector_path = DATA_DIR / SECTOR_CSV
    if sector_path.exists():
        with sector_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            sectors = list(reader)
        checks += 1
        if reader.fieldnames != SECTOR_HEADER:
            errors.append(f"{sector_path}: 表头与 SECTOR_HEADER 不一致")
        counts = Counter((row.get("date"), row.get("rank_type")) for row in sectors)
        for key, count in counts.items():
            if count != 5:
                errors.append(f"{sector_path}: {key} 应有 5 行，实际 {count} 行")

    daily_rows = load_daily_rows()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    checks += 1
    expected_count = f"共 {len(daily_rows)} 个交易日"
    if expected_count not in readme:
        errors.append(f"README 未包含正确统计：{expected_count}")
    for row in daily_rows[-10:]:
        if f"| {row['date']} |" not in readme:
            errors.append(f"README 最近 10 日缺少 {row['date']}")

    for filename in ("status.json", "latest.json"):
        path = DATA_DIR / filename
        checks += 1
        if not path.exists():
            errors.append(f"缺少 {path}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"{path}: JSON 无效（{e}）")
            continue
        if payload.get("schema_version") != 1:
            errors.append(f"{path}: schema_version 必须为 1")

    if errors:
        print("数据质量检查失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"数据质量检查通过：{checks} 组检查，{len(daily_rows)} 个交易日")
    return 0


if __name__ == "__main__":
    sys.exit(main())
