import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import backfill  # noqa: E402
import snapshot  # noqa: E402


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class DataBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.data = self.root / "data"

        daily_rows = []
        for date, close in (("2026-09-17", "3875.60"), ("2026-09-18", "3911.87")):
            row = {column: "" for column in snapshot.CSV_HEADER}
            row.update({
                "date": date,
                "上证指数_close": close,
                "上证指数_pct": "0.94",
                "amount_yi": "20771.0",
            })
            daily_rows.append(row)
        write_csv(self.data / "2026.csv", snapshot.CSV_HEADER, daily_rows)

        sectors = []
        for rank_type in ("up", "down"):
            for rank in range(1, 6):
                sectors.append({
                    "date": "2026-09-18",
                    "rank_type": rank_type,
                    "rank": rank,
                    "name": f"sector-{rank_type}-{rank}",
                    "pct": "1.00" if rank_type == "up" else "-1.00",
                    "net_inflow_yi": "1.00",
                    "leader": "示例股",
                })
        write_csv(self.data / snapshot.SECTOR_CSV, snapshot.SECTOR_HEADER, sectors)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_daily_paths_exclude_sector_sidecar(self):
        with patch.object(snapshot, "DATA_DIR", self.data):
            self.assertEqual(
                [path.name for path in snapshot.daily_csv_paths()],
                ["2026.csv"],
            )

    def test_readme_uses_only_daily_rows(self):
        with (
            patch.object(snapshot, "ROOT", self.root),
            patch.object(snapshot, "DATA_DIR", self.data),
        ):
            snapshot.render_readme("2026-09-20 09:00")

        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("共 2 个交易日", readme)
        self.assertEqual(readme.count("| 2026-09-18 |"), 1)
        self.assertIn("3911.87", readme)

    def test_backfill_does_not_replace_daily_row_with_sector_row(self):
        with (
            patch.object(snapshot, "DATA_DIR", self.data),
            patch.object(backfill, "DATA_DIR", self.data),
        ):
            rows = backfill.load_existing()

        self.assertEqual(set(rows), {"2026-09-17", "2026-09-18"})
        self.assertEqual(rows["2026-09-18"]["上证指数_close"], "3911.87")

    def test_cron_and_local_time_resolve_to_market_slots(self):
        self.assertEqual(
            snapshot.resolve_slot("35 3 * * *", datetime(2026, 9, 18, 9, 0)),
            "midday",
        )
        self.assertEqual(
            snapshot.resolve_slot("auto", datetime(2026, 9, 18, 15, 10)),
            "close",
        )

    def test_beijing_timezone_falls_back_without_tzdata(self):
        with patch.object(
            snapshot,
            "ZoneInfo",
            side_effect=snapshot.ZoneInfoNotFoundError("missing tzdata"),
        ):
            tz = snapshot.beijing_tz()
        self.assertEqual(tz.utcoffset(None), timedelta(hours=8))

    def test_pulse_is_idempotent_and_latest_json_is_numeric(self):
        row = {column: "" for column in snapshot.CSV_HEADER}
        row.update({
            "date": "2026-09-18",
            "上证指数_close": "3911.87",
            "上证指数_pct": "0.94",
            "amount_yi": "20771.0",
            "up": "4277",
        })

        with (
            patch.object(snapshot, "ROOT", self.root),
            patch.object(snapshot, "DATA_DIR", self.data),
        ):
            snapshot.append_pulse(row, "2026-09-18 10:05", "open")
            row["上证指数_close"] = "3912.00"
            path = snapshot.append_pulse(row, "2026-09-18 10:05", "open")
            snapshot.write_latest_json("2026-09-18 10:05")

        with path.open(encoding="utf-8") as f:
            pulses = list(csv.DictReader(f))
        payload = json.loads((self.data / "latest.json").read_text(encoding="utf-8"))

        self.assertEqual(len(pulses), 1)
        self.assertEqual(pulses[0]["上证指数_close"], "3912.00")
        self.assertEqual(payload["latest_daily"]["indices"]["sh000001"]["close"], 3911.87)
        self.assertEqual(payload["latest_pulse"]["slot"], "open")


if __name__ == "__main__":
    unittest.main()
