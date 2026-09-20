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


def cross_assets(a50_pct=0.5, cnh_pct=-0.2, dxy_pct=-0.1):
    return [
        {"code": "A50", "close": 14500.0, "pct": a50_pct, "stale": False},
        {"code": "USDCNH", "close": 6.70, "pct": cnh_pct, "stale": False},
        {"code": "DXY", "close": 100.2, "pct": dxy_pct, "stale": False},
        {"code": "GOLD", "close": 4400.0, "pct": 0.8, "stale": False},
        {"code": "WTI", "close": 95.0, "pct": -1.2, "stale": False},
    ]


class GlobalContextTests(unittest.TestCase):
    def test_sina_cross_assets_are_normalized_from_two_quote_layouts(self):
        raw = "\n".join([
            'var hq_str_hf_CHA50CFD="14484.500,,14484.000,14489.000,14489.000,14437.000,05:07:06,14482.000,14484.000,832305,19,6,2026-09-19,富时中国A50期货,50913";',
            'var hq_str_fx_susdcnh="04:59:59,6.6943,6.6963,6.694400,120,6.703800,6.704400,6.692400,6.6943,离岸人民币（香港）,-0.00,-0.0001,0.00179,,6.995700,6.693400,,2026-09-19";',
            'var hq_str_DINIW="05:10:48,100.2167,100.2167,100.2304,4021,100.2222,100.5659,100.1638,100.2167,美元指数,2026-09-19";',
            'var hq_str_hf_GC="4418.560,0.43,4415.900,4416.600,4439.800,4372.200,04:59:59,4399.700,4381.600,0,2,4,2026-09-19,纽约黄金,0";',
        ])

        parsed = global_context.parse_sina_cross_assets(raw)
        by_code = {item["code"]: item for item in parsed}

        self.assertEqual(set(by_code), {"A50", "USDCNH", "DXY", "GOLD"})
        self.assertAlmostEqual(by_code["A50"]["pct"], (14484.5 / 14482.0 - 1) * 100)
        self.assertAlmostEqual(by_code["USDCNH"]["previous_close"], 6.7038)
        self.assertEqual(by_code["GOLD"]["pct"], 0.43)

    def test_missing_cross_assets_reuse_only_matching_previous_values(self):
        current = cross_assets()[:2]
        previous = cross_assets()
        merged = global_context.merge_cross_asset_snapshots(current, previous)

        self.assertEqual(len(merged), 5)
        self.assertFalse(merged[0]["stale"])
        self.assertTrue(merged[-1]["stale"])

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

    def test_a50_and_fx_are_bounded_signals_while_commodities_are_context(self):
        result = global_context.analyze(
            markets(0),
            {"vix": {"value": 16.0}, "us10y": {"value": 4.0}},
            {"上证指数_pct": "0", "up": "2500", "down": "2500"},
            [],
            "2026-09-20 15:30",
            cross_assets=cross_assets(a50_pct=3, cnh_pct=-2, dxy_pct=-2),
        )
        signals = {item["label"]: item for item in result["signals"]}

        self.assertEqual(signals["A50 先行"]["contribution"], 8)
        self.assertEqual(signals["美元与人民币"]["contribution"], 8)
        self.assertNotIn("黄金", signals)
        self.assertNotIn("原油", signals)

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
