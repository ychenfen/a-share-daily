import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import chart  # noqa: E402


class MarketCalendarTests(unittest.TestCase):
    def test_market_colors_follow_a_share_convention(self):
        self.assertEqual(chart.market_color(2.5), "#a40e26")
        self.assertEqual(chart.market_color(-2.5), "#08783e")
        self.assertNotEqual(chart.market_color(0.5), chart.market_color(-0.5))

    def test_calendar_contains_dates_values_and_legend(self):
        svg = chart.build_market_calendar([
            {"date": "2026-09-17", "上证指数_pct": "-0.41"},
            {"date": "2026-09-18", "上证指数_pct": "0.94"},
        ])

        self.assertIn("A 股涨跌日历", svg)
        self.assertIn("2026-09-18　上证 +0.94%", svg)
        self.assertIn("fill=\"#f29a9a\"", svg)
        self.assertIn(">跌</text>", svg)
        self.assertIn(">涨</text>", svg)


if __name__ == "__main__":
    unittest.main()
