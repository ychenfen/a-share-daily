import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import share_card  # noqa: E402


class ShareCardTests(unittest.TestCase):
    def test_card_contains_market_brief_and_is_valid_xml(self):
        analysis = {
            "score": 21,
            "stance": "谨慎偏多 & 观察",
            "confidence": "中",
            "generated_at": "2026-09-20 16:15",
            "advice": ["观察外围市场是否继续增强。"],
        }
        global_data = {
            "markets": [
                {"code": "SPX", "pct": 0.17, "stale": False},
                {"code": "NDX", "pct": 0.39, "stale": False},
                {"code": "N225", "pct": 1.38, "stale": True},
                {"code": "HSI", "pct": 0.60, "stale": False},
            ],
            "health": {},
        }
        latest = {
            "latest_daily": {
                "date": "2026-09-18",
                "indices": {"sh000001": {"close": 3911.87, "pct": 0.94}},
                "amount_yi": 20771,
                "breadth": {"up": 4277, "down": 1173},
                "sentiment": {"limit_up": 78, "broken_rate": 24.3},
            }
        }

        svg = share_card.build_svg(analysis, global_data, latest)
        root = ET.fromstring(svg)

        self.assertEqual(root.attrib["width"], "1200")
        self.assertEqual(root.attrib["height"], "630")
        self.assertIn("DAILY MARKET BRIEF", svg)
        self.assertIn("+21", svg)
        self.assertIn("谨慎偏多 &amp; 观察", svg)
        self.assertIn("STALE", svg)

    def test_generate_writes_the_current_card(self):
        with tempfile.TemporaryDirectory() as directory:
            output = share_card.generate(Path(directory) / "brief.svg")
            self.assertTrue(output.exists())
            self.assertIn("ychenfen.github.io/a-share-daily", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
