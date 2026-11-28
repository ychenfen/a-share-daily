import csv
import gzip
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import record_archive  # noqa: E402
import snapshot  # noqa: E402


class RecordArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.archive = Path(self.tempdir.name) / "archive"

    def tearDown(self):
        self.tempdir.cleanup()

    def test_should_adopt_delayed_quote_date_only_for_unrecorded_final_slot(self):
        self.assertTrue(
            snapshot.should_adopt_delayed_quote_date(
                "2026-11-28", "2026-11-27", "close", False, {"2026-11-26"}
            )
        )
        self.assertFalse(
            snapshot.should_adopt_delayed_quote_date(
                "2026-11-28", "2026-11-27", "close", False, {"2026-11-27"}
            )
        )
        self.assertFalse(
            snapshot.should_adopt_delayed_quote_date(
                "2026-11-28", "2026-11-27", "open", False, set()
            )
        )
        self.assertFalse(
            snapshot.should_adopt_delayed_quote_date(
                "2026-11-28", "2026-11-27", "close", True, set()
            )
        )

    def test_parse_zt_and_compute_regime_big_loss_and_promotions(self):
        prev_zt = record_archive.parse_zt_rows(
            "2026-11-25",
            [
                {"c": "603960", "m": 1, "n": "克来机电", "p": 20460, "zdp": 10.0,
                 "amount": 1300000000, "ltsz": 5000000000, "hs": 24.7, "lbc": 3,
                 "zttj": {"days": 3, "ct": 3}, "fbt": 93500, "lbt": 93500, "fund": 100000000, "zbc": 0, "hybk": "自动化"},
                {"c": "002685", "m": 0, "n": "华东重机", "p": 10000, "zdp": 10.0,
                 "amount": 900000000, "ltsz": 4000000000, "hs": 18.0, "lbc": 2,
                 "zttj": {"days": 2, "ct": 2}, "fbt": 100500, "lbt": 100500, "fund": 50000000, "zbc": 1, "hybk": "机械"},
                {"c": "000001", "m": 0, "n": "首板示例", "p": 10000, "zdp": 10.0,
                 "amount": 500000000, "ltsz": 3000000000, "hs": 8.0, "lbc": 1,
                 "zttj": {"days": 1, "ct": 1}, "fbt": 94500, "lbt": 94500, "fund": 30000000, "zbc": 0, "hybk": "科技"},
            ],
        )
        today_zt = record_archive.parse_zt_rows(
            "2026-11-26",
            [
                {"c": "603960", "m": 1, "n": "克来机电", "p": 22510, "zdp": 10.02,
                 "amount": 1320000000, "ltsz": 5500000000, "hs": 23.7, "lbc": 4,
                 "zttj": {"days": 4, "ct": 4}, "fbt": 93200, "lbt": 93200, "fund": 120000000, "zbc": 0, "hybk": "自动化"},
            ],
        )

        mock_quotes = {
            "603960": {"date": "2026-11-26", "open": 21.11, "high": 22.51, "low": 20.26, "close": 22.51, "prev_close": 20.46, "pct": 10.02},
            "002685": {"date": "2026-11-26", "open": 9.80, "high": 10.10, "low": 9.10, "close": 9.20, "prev_close": 10.00, "pct": -8.00},
            "000001": {"date": "2026-11-26", "open": 10.20, "high": 10.50, "low": 9.90, "close": 10.10, "prev_close": 10.00, "pct": 1.00},
        }

        with (
            patch.object(record_archive, "ARCHIVE_DIR", self.archive),
            patch.object(record_archive, "fetch_tencent_quotes", return_value=mock_quotes),
        ):
            record_archive.write_csv_atomic(
                self.archive / "pools" / "2026-11-25_zt.csv",
                record_archive.ZT_HEADER,
                prev_zt,
            )
            outcomes, regime = record_archive.compute_prev_zt_outcomes_and_regime(
                "2026-11-26", today_zt, [], [], use_live_quotes=True
            )
            regime_path = record_archive.upsert_regime_row(regime)
            # Idempotent second upsert
            record_archive.upsert_regime_row(regime)

        self.assertEqual(len(outcomes), 3)
        self.assertEqual(regime["prev_lbc2_cnt"], 2)
        self.assertEqual(regime["prev_lbc2_dm_rate"], "50.0")
        self.assertEqual(regime["promote_3to4"], "100.0")
        self.assertEqual(regime["promote_2to3"], "0.0")
        self.assertEqual(regime["promote_1to2"], "0.0")
        self.assertEqual(regime["top_lbc_broken"], 0)

        with regime_path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2026-11-26")

    def test_record_intraday_5m_writes_valid_gzip_csv(self):
        fake_bars = [
            {"code": "SH000001", "time": "09:35", "open": "3600", "close": "3605",
             "high": "3608", "low": "3598", "vol": "100", "amount": "1000"},
        ]
        with (
            patch.object(record_archive, "ARCHIVE_DIR", self.archive),
            patch.object(record_archive, "fetch_5m_day_bars", return_value=fake_bars),
        ):
            res = record_archive.record_intraday_5m("2026-11-27", [], [])

        self.assertIsNotNone(res)
        path, n_sym, n_bars = res
        self.assertEqual(n_sym, 2)
        self.assertEqual(n_bars, 2)
        with gzip.open(path, "rt", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["time"], "09:35")

    def test_record_fenshi_1m_includes_auction_and_respects_priority_cap(self):
        fake_fenshi = [
            {"code": "603960", "time": "09:20", "open": "22.49", "price": "22.10",
             "high": "22.49", "low": "22.00", "vol": "0", "amount": "0.00", "avg_price": "20.460"},
            {"code": "603960", "time": "09:30", "open": "21.11", "price": "21.11",
             "high": "21.11", "low": "21.11", "vol": "27512", "amount": "58077832.00", "avg_price": "21.110"},
        ]
        zt_rows = [
            {"code": "603960", "lbc": "4", "fbt": "93200", "amount": "1320000000"},
            {"code": "000001", "lbc": "1", "fbt": "93500", "amount": "500000000"},
            {"code": "000002", "lbc": "1", "fbt": "100000", "amount": "400000000"},
        ]
        with (
            patch.object(record_archive, "ARCHIVE_DIR", self.archive),
            patch.object(record_archive, "fetch_fenshi_1m_day", return_value=fake_fenshi),
        ):
            res = record_archive.record_fenshi_1m(
                "2026-11-27", zt_rows, [], [], [], max_symbols=2
            )

        self.assertIsNotNone(res)
        path, ok_syms, n_rows = res
        # 3 indices + 2 capped stock symbols = 5 symbols
        self.assertEqual(ok_syms, 5)
        self.assertEqual(n_rows, 10)
        with gzip.open(path, "rt", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["time"], "09:20")
        self.assertEqual(rows[0]["avg_price"], "20.460")


if __name__ == "__main__":
    unittest.main()
