import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scorecard  # noqa: E402


class ScorecardTests(unittest.TestCase):
    def test_signal_ledger_captures_scored_cross_assets(self):
        row = scorecard.build_signal(
            {"slot": "night", "market_data_date": "2026-09-18"},
            {
                "generated_at": "2026-09-20 20:20",
                "score": 18,
                "stance": "谨慎偏多",
                "confidence": "高",
            },
            {
                "markets": [{"pct": 0.5}],
                "cross_assets": [
                    {"code": "A50", "pct": 0.3, "close": 14500},
                    {"code": "USDCNH", "pct": -0.2, "close": 6.7},
                    {"code": "DXY", "pct": -0.1, "close": 100.2},
                ],
                "macro": {},
                "health": {"cross_assets": {"status": "fresh"}},
            },
            {"date": "2026-09-18", "上证指数_close": "3911", "上证指数_pct": "0.9"},
        )

        self.assertEqual(row["a50_pct"], 0.3)
        self.assertEqual(row["usdcnh"], 6.7)
        self.assertEqual(row["dxy_pct"], -0.1)
        self.assertEqual(row["health"], "fresh")

    def test_intraday_and_close_signals_use_different_first_sessions(self):
        signals = [
            {"captured_at": "2026-09-18 10:05", "signal_date": "2026-09-18", "slot": "open", "score": "20"},
            {"captured_at": "2026-09-18 15:10", "signal_date": "2026-09-18", "slot": "close", "score": "-20"},
        ]
        daily = [
            {"date": "2026-09-18", "上证指数_pct": "1.00"},
            {"date": "2026-09-21", "上证指数_pct": "-2.00"},
        ]
        settled = scorecard.settle_signals(signals, daily)

        self.assertEqual(settled[0]["return_1d"], 1.0)
        self.assertTrue(settled[0]["hit_1d"])
        self.assertEqual(settled[1]["return_1d"], -2.0)
        self.assertTrue(settled[1]["hit_1d"])

    def test_small_samples_remain_collecting(self):
        result = scorecard.summarize([], "2026-09-20 16:00")
        svg = scorecard.build_svg(result)

        self.assertEqual(result["status"], "collecting")
        self.assertIsNone(result["hit_rate_1d"])
        self.assertIn("拒绝回填假胜率", svg)


if __name__ == "__main__":
    unittest.main()
