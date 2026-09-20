import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_readmes_cross_link_and_show_the_live_product(self):
        chinese = (ROOT / "README.md").read_text(encoding="utf-8")
        english = (ROOT / "README.en.md").read_text(encoding="utf-8")

        self.assertIn("[English](README.en.md)", chinese)
        self.assertIn("[简体中文](README.md)", english)
        self.assertIn("https://ychenfen.github.io/a-share-daily/", english)
        self.assertIn("charts/daily_brief.svg", english)
        self.assertIn("/a-share-daily/generate", chinese)
        self.assertIn("/a-share-daily/generate", english)
        self.assertIn("/a-share-daily/discussions", chinese)
        self.assertIn("/a-share-daily/discussions", english)

    def test_english_readme_keeps_research_boundaries_explicit(self):
        english = (ROOT / "README.en.md").read_text(encoding="utf-8").lower()

        self.assertIn("not investment advice", english)
        self.assertIn("forward-only scorecard", english)
        self.assertIn("zero runtime dependencies", english)


if __name__ == "__main__":
    unittest.main()
