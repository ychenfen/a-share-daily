import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scorecard  # noqa: E402


class ScorecardTests(unittest.TestCase):
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
