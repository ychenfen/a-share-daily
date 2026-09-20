import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import global_context  # noqa: E402


def markets(pct):
    return [
        {
            "code": code,
            "name": name,
            "region": region,
            "kind": "index",
            "close": 1000.0 + i,
            "pct": pct,
            "change": 10.0,
            "previous_close": 990.0,
        }
        for i, (code, name, region) in enumerate((
            ("SPX", "标普 500", "美国"),
            ("NDX", "纳斯达克", "美国"),
            ("DJIA", "道琼斯", "美国"),
            ("N225", "日经 225", "日本"),
            ("HSI", "恒生指数", "中国香港"),
        ))
    ]


class GlobalContextTests(unittest.TestCase):
    def test_missing_markets_reuse_only_the_last_good_entries(self):
        current = markets(0.5)[:2]
        previous = markets(-0.5)
        merged = global_context.merge_market_snapshots(current, previous)

        self.assertEqual(len(merged), 5)
        self.assertFalse(merged[0]["stale"])
        self.assertFalse(merged[1]["stale"])
        self.assertTrue(merged[2]["stale"])

    def test_constructive_and_defensive_scenarios_separate(self):
        constructive = global_context.analyze(
            markets(1.5),
            {"vix": {"value": 13.0}, "us10y": {"value": 3.2}},
            {
                "上证指数_pct": "1.2",
                "up": "4200",
                "down": "900",
                "limit_up": "90",
                "limit_down": "2",
                "broken_rate": "12",
            },
            [{"title": "全球股市上涨，风险偏好提振"}],
            "2026-09-20 09:10",
        )
        defensive = global_context.analyze(
            markets(-2.5),
            {"vix": {"value": 35.0}, "us10y": {"value": 5.2}},
            {
                "上证指数_pct": "-2.0",
                "up": "500",
                "down": "4500",
                "limit_up": "8",
                "limit_down": "80",
                "broken_rate": "50",
            },
            [{"title": "市场暴跌，机构警告冲突风险"}],
            "2026-09-20 09:10",
        )

        self.assertGreaterEqual(constructive["score"], 25)
        self.assertEqual(constructive["stance"], "积极但不追高")
        self.assertLessEqual(defensive["score"], -25)
        self.assertEqual(defensive["stance"], "防守优先")

    def test_news_tone_has_bounded_low_weight(self):
        tone = global_context.news_tone([
            {"title": "市场上涨反弹并创新高"},
            {"title": "风险警告：通胀与加息压力"},
        ])
        self.assertGreaterEqual(tone["score"], -8)
        self.assertLessEqual(tone["score"], 8)
        self.assertGreater(tone["positive_hits"], 0)
        self.assertGreater(tone["negative_hits"], 0)

    def test_stale_source_lowers_confidence(self):
        result = global_context.analyze(
            markets(0.5),
            {"vix": {"value": 16.0}, "us10y": {"value": 4.0}},
            {"上证指数_pct": "0.5", "up": "3000", "down": "2000"},
            [{"title": "全球市场上涨"}],
            "2026-09-20 15:30",
            health={"markets": {"status": "fresh"}, "vix": {"status": "stale"}},
        )

        self.assertEqual(result["confidence"], "中")

    def test_dashboard_contains_cross_market_and_risk_data(self):
        global_data = {
            "generated_at": "2026-09-20 09:10",
            "markets": markets(0.5),
            "macro": {"vix": {"value": 16.2}, "us10y": {"value": 4.1}},
        }
        analysis = {
            "score": 18,
            "stance": "谨慎偏多",
            "confidence": "高",
            "color": "#e05a47",
            "summary": "测试摘要",
        }
        svg = global_context.build_dashboard(global_data, analysis)

        self.assertIn("全球市场雷达", svg)
        self.assertIn("日经 225", svg)
        self.assertIn("VIX 波动率", svg)
        self.assertIn("谨慎偏多", svg)


if __name__ == "__main__":
    unittest.main()
