import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_readmes_cross_link_and_show_the_live_product(self):
        chinese = (ROOT / "README.md").read_text(encoding="utf-8")
        english = (ROOT / "README.en.md").read_text(encoding="utf-8")
        chinese_schema = (ROOT / "docs" / "DATA_SCHEMA.md").read_text(encoding="utf-8")
        english_schema = (ROOT / "docs" / "DATA_SCHEMA.en.md").read_text(encoding="utf-8")

        self.assertIn("[English](README.en.md)", chinese)
        self.assertIn("[简体中文](README.md)", english)
        self.assertIn("https://ychenfen.github.io/a-share-daily/", english)
        self.assertIn("charts/daily_brief.svg", english)
        self.assertIn("/a-share-daily/generate", chinese)
        self.assertIn("/a-share-daily/generate", english)
        self.assertIn("/a-share-daily/discussions", chinese)
        self.assertIn("/a-share-daily/discussions", english)
        self.assertIn("[Data schema](docs/DATA_SCHEMA.en.md)", english)
        self.assertIn("[English](DATA_SCHEMA.en.md)", chinese_schema)
        self.assertIn("[简体中文](DATA_SCHEMA.md)", english_schema)

    def test_english_readme_keeps_research_boundaries_explicit(self):
        english = (ROOT / "README.en.md").read_text(encoding="utf-8").lower()

        self.assertIn("not investment advice", english)
        self.assertIn("forward-only scorecard", english)
        self.assertIn("zero runtime dependencies", english)

    def test_english_schema_preserves_machine_contracts_and_boundaries(self):
        schema = (ROOT / "docs" / "DATA_SCHEMA.en.md").read_text(encoding="utf-8").lower()

        self.assertIn("schema_version", schema)
        self.assertIn("percentage points", schema)
        self.assertIn("fresh", schema)
        self.assertIn("stale", schema)
        self.assertIn("missing", schema)
        self.assertIn("not confirmed events", schema)
        self.assertIn("directly alter the risk score", schema)
        self.assertIn("at least 20 directional", schema)


if __name__ == "__main__":
    unittest.main()
