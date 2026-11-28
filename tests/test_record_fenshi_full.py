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

import record_fenshi_full as rff  # noqa: E402


class RecordFenshiFullTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_parse_em_trends_and_tencent_fallback(self):
        em_rows = rff.parse_em_trends_lines(
            "603960",
            [
                "2026-11-26 15:00,20.46,20.46,20.46,20.46,100,204600,20.460",
                "2026-11-27 09:20,22.49,22.10,22.49,22.00,0,0.00,20.460",
                "2026-11-27 09:30,21.11,21.11,21.11,21.11,27512,58077832.00,21.110",
            ],
            "2026-11-27",
        )
        self.assertEqual(len(em_rows), 2)
        self.assertEqual(em_rows[0]["time"], "09:20")
        self.assertEqual(em_rows[1]["avg_price"], "21.110")

        qq_payload = json.dumps({
            "data": {
                "sz002771": {
                    "data": {
                        "date": "20261127",
                        "data": [
                            "0930 10.00 100 100000.00",
                            "0931 10.20 300 304000.00",
                        ],
                    }
                }
            }
        })
        with patch.object(rff, "http_get", return_value=qq_payload):
            qq_rows = rff.fetch_fenshi_tencent("002771", "2026-11-27")
        self.assertEqual(len(qq_rows), 2)
        self.assertEqual(qq_rows[1]["time"], "09:31")
        self.assertEqual(qq_rows[1]["vol"], "200")
        self.assertEqual(qq_rows[1]["avg_price"], "10.133")

    def test_shard_fetch_and_merge_pipeline_with_integrity_gate(self):
        symbols_path = self.root / "symbols.json"
        symbols_path.write_text(
            json.dumps({
                "date": "2026-11-27",
                "latest_market_date": "2026-11-27",
                "is_latest_day": True,
                "symbols": [
                    {"code": "SH000001", "secid": "1.000001", "name": "上证指数"},
                    {"code": "603960", "secid": "1.603960", "name": "克来机电"},
                    {"code": "002771", "secid": "0.002771", "name": "真视通"},
                    {"code": "002579", "secid": "0.002579", "name": "中京电子"},
                ],
            }),
            encoding="utf-8",
        )

        def fake_fetch(item, date_str, is_latest_day=True):
            c = item["code"]
            return c, "em", [
                {"code": c, "time": "09:25", "open": "10.00", "price": "10.00",
                 "high": "10.00", "low": "10.00", "vol": "0", "amount": "0.00", "avg_price": "10.000"},
                {"code": c, "time": "09:30", "open": "10.10", "price": "10.10",
                 "high": "10.10", "low": "10.10", "vol": "100", "amount": "101000.00", "avg_price": "10.100"},
            ]

        shards_dir = self.root / "shards"
        with patch.object(rff, "fetch_one_symbol", side_effect=fake_fetch):
            for idx in range(2):
                args = type("Args", (), {
                    "symbols": str(symbols_path),
                    "shard_index": idx,
                    "shard_total": 2,
                    "date": "2026-11-27",
                    "workers": 2,
                    "out": str(shards_dir / f"s{idx}" / f"shard_{idx}.csv.gz"),
                    "stats_out": str(shards_dir / f"s{idx}" / f"shard_{idx}.stats.json"),
                })()
                self.assertEqual(rff.cmd_fetch_shard(args), 0)

        out_dir = self.root / "release"
        m_args = type("Args", (), {
            "shards_dir": str(shards_dir),
            "date": "2026-11-27",
            "out_dir": str(out_dir),
            "min_symbols": 4,
            "min_coverage": 0.9,
        })()
        self.assertEqual(rff.cmd_merge(m_args), 0)

        manifest = json.loads((out_dir / "fenshi_all_2026-11-27.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["recorded_symbols"], 4)
        self.assertEqual(manifest["total_rows"], 8)
        self.assertEqual(manifest["auction_rows_0915_0925"], 4)
        self.assertEqual(len(manifest["sha256"]), 64)

        with gzip.open(out_dir / "fenshi_all_2026-11-27.csv.gz", "rt", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 8)


if __name__ == "__main__":
    unittest.main()
