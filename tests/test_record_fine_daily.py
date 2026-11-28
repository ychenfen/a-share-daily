import csv
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import record_archive  # noqa: E402
import record_fine_daily as rfd  # noqa: E402


class RecordFineDailyTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.out = Path(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_fmt_hhmmss_and_changes_and_ticks_parsing(self):
        self.assertEqual(rfd.fmt_hhmmss(91503), "09:15:03")
        self.assertEqual(rfd.fmt_hhmmss(150000), "15:00:00")

        changes_payload = json.dumps({
            "data": {
                "tc": 2,
                "allstock": [
                    {"tm": 93105, "c": "603960", "m": 1, "n": "克来机电", "t": 8201, "i": "21.88,0.069"},
                    {"tm": 93212, "c": "603960", "m": 1, "n": "克来机电", "t": 4, "i": "22.51,0.100"},
                ],
            }
        })
        ticks_payload = json.dumps({
            "data": {
                "c": "603960",
                "data": [
                    {"t": 91500, "p": 22510, "v": 3629, "bs": 4},
                    {"t": 93003, "p": 21630, "v": 11665, "bs": 2},
                ],
            }
        })
        with patch.object(rfd.rff, "http_get", return_value=changes_payload):
            changes, tc = rfd.fetch_all_market_changes("2026-11-27")
        self.assertEqual(tc, 2)
        self.assertEqual(changes[0]["type_name"], "火箭发射")
        self.assertEqual(changes[1]["type_name"], "封涨停板")

        with patch.object(rfd.rff, "http_get", return_value=ticks_payload):
            ticks = rfd.fetch_stock_ticks_em("603960")
        self.assertEqual(len(ticks), 2)
        self.assertEqual(ticks[0]["time"], "09:15:00")
        self.assertEqual(ticks[0]["price"], "22.51")
        self.assertEqual(ticks[1]["bs"], 2)

    def test_lhb_seats_fetch_deduplicates_buy_and_sell(self):
        fake_buy = json.dumps({
            "result": {
                "pages": 1,
                "data": [
                    {"SECURITY_CODE": "000530", "OPERATEDEPT_NAME": "机构专用",
                     "BUY": 1000, "SELL": 0, "NET": 1000, "EXPLANATION": "日涨幅偏离值达7%"},
                ],
            }
        })
        fake_sell = json.dumps({
            "result": {
                "pages": 1,
                "data": [
                    {"SECURITY_CODE": "000530", "OPERATEDEPT_NAME": "拉萨团结路",
                     "BUY": 100, "SELL": 900, "NET": -800, "EXPLANATION": "日涨幅偏离值达7%"},
                ],
            }
        })
        with patch.object(record_archive, "fast_fetch", side_effect=[fake_buy, fake_sell]):
            rows = record_archive.fetch_lhb_seats_rows("2026-11-27")
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["side"] for r in rows}, {"buy", "sell"})

    def test_run_record_produces_valid_gz_and_manifest(self):
        fake_changes = (
            [{"date": "2026-11-27", "time": "09:31:00", "code": "603960", "market": 1,
              "name": "克来机电", "type_code": "4", "type_name": "封涨停板", "info": "22.51"}],
            1,
        )
        fake_ticks = [
            {"code": "603960", "time": "09:15:00", "price": "22.51", "vol": 100, "bs": 4},
        ]
        with (
            patch.object(rfd, "fetch_all_market_changes", return_value=fake_changes),
            patch.object(rfd, "select_core_tick_codes", return_value=["603960"]),
            patch.object(rfd, "fetch_stock_ticks_em", return_value=fake_ticks),
        ):
            rc = rfd.run_record("2026-11-27", self.out, max_symbols=10, workers=2)
        self.assertEqual(rc, 0)
        manifest = json.loads((self.out / "fine_2026-11-27.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["changes"]["rows"], 1)
        self.assertEqual(manifest["ticks_core"]["recorded_symbols"], 1)
        with gzip.open(self.out / "ticks_core_2026-11-27.csv.gz", "rt", encoding="utf-8") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 1)


if __name__ == "__main__":
    unittest.main()
