#!/usr/bin/env python3
"""Build the dependency-free GitHub Pages artifact."""

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "site"
DATA_FILES = ("analysis.json", "global.json", "latest.json", "scorecard.json", "status.json")
CHART_FILES = ("market_calendar.svg", "global_dashboard.svg", "signal_scorecard.svg")


def build(output):
    output = Path(output).resolve()
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(SOURCE, output)
    data_dir = output / "data"
    chart_dir = output / "charts"
    data_dir.mkdir()
    chart_dir.mkdir()
    for name in DATA_FILES:
        source = ROOT / "data" / name
        if not source.exists():
            raise FileNotFoundError(source)
        json.loads(source.read_text(encoding="utf-8"))
        shutil.copy2(source, data_dir / name)
    for name in CHART_FILES:
        source = ROOT / "charts" / name
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, chart_dir / name)
    (output / ".nojekyll").touch()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=ROOT / ".site-build")
    args = parser.parse_args()
    output = build(args.output)
    print(f"站点构建完成: {output}")


if __name__ == "__main__":
    main()
