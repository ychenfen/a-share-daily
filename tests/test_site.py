import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_site  # noqa: E402


class SiteBuildTests(unittest.TestCase):
    def test_build_contains_runtime_data_and_visuals(self):
        with tempfile.TemporaryDirectory() as directory:
            output = build_site.build(Path(directory) / "public")

            self.assertTrue((output / "index.html").exists())
            self.assertTrue((output / "app.js").exists())
            self.assertTrue((output / ".nojekyll").exists())
            self.assertTrue((output / "charts" / "market_calendar.svg").exists())
            analysis = json.loads((output / "data" / "analysis.json").read_text())
            scorecard = json.loads((output / "data" / "scorecard.json").read_text())
            self.assertIn("score", analysis)
            self.assertIn(scorecard["status"], ("collecting", "ready"))


if __name__ == "__main__":
    unittest.main()
