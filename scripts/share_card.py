#!/usr/bin/env python3
"""Generate a dependency-free, shareable daily market brief as SVG."""

import argparse
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT = ROOT / "charts" / "daily_brief.svg"

WIDTH = 1200
HEIGHT = 630


def read_json(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def xml(value):
    return escape(str(value), quote=False)


def clip(value, limit):
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def numeric(value, digits=2, suffix=""):
    try:
        return f"{float(value):,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return "--"


def signed(value):
    try:
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return "--"


def score_color(score):
    if score >= 5:
        return "#ff5148"
    if score <= -5:
        return "#2cc17a"
    return "#e9c86f"


def change_color(value):
    try:
        change = float(value)
    except (TypeError, ValueError):
        return "#e9c86f"
    if change > 0:
        return "#ff5148"
    if change < 0:
        return "#2cc17a"
    return "#e9c86f"


def build_svg(analysis, global_data, latest):
    score = max(-100, min(100, int(analysis.get("score") or 0)))
    accent = score_color(score)
    stance = analysis.get("stance") or "等待数据"
    confidence = analysis.get("confidence") or "低"
    generated_at = analysis.get("generated_at") or latest.get("generated_at") or "--"

    daily = latest.get("latest_daily") or {}
    indices = daily.get("indices") or {}
    shanghai = indices.get("sh000001") or {}
    breadth = daily.get("breadth") or {}
    sentiment = daily.get("sentiment") or {}
    market_date = daily.get("date") or "--"

    markets = {item.get("code"): item for item in global_data.get("markets") or []}
    market_cells = []
    for code, label in (("SPX", "S&P 500"), ("NDX", "NASDAQ"), ("N225", "NIKKEI"), ("HSI", "HANG SENG")):
        item = markets.get(code) or {}
        market_cells.append((label, item.get("pct"), bool(item.get("stale"))))

    cross_assets = {item.get("code"): item for item in global_data.get("cross_assets") or []}
    cross_asset_cells = []
    for code, label in (("A50", "A50"), ("USDCNH", "CNH"), ("DXY", "DXY"), ("GOLD", "GOLD"), ("WTI", "WTI")):
        item = cross_assets.get(code) or {}
        digits = 4 if code == "USDCNH" else 2
        cross_asset_cells.append((label, numeric(item.get("close"), digits), item.get("pct"), bool(item.get("stale"))))

    health = global_data.get("health") or {}
    health_text = " · ".join(
        f"{label} {str((health.get(key) or {}).get('status') or 'missing').upper()}"
        for key, label in (("markets", "MARKETS"), ("cross_assets", "CROSS"), ("vix", "VIX"), ("us10y", "US10Y"), ("news", "NEWS"))
    )
    advice = clip((analysis.get("advice") or [analysis.get("summary") or "等待分析"])[0], 48)

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="1200" height="630" fill="#0a0d0f"/>',
        '<circle cx="1058" cy="-24" r="286" fill="#ff5148" opacity="0.07"/>',
        '<path d="M0 0H1200V630H0Z" fill="none" stroke="#273037" stroke-width="2"/>',
        '<g font-family="DIN Alternate, SFMono-Regular, Menlo, monospace">',
        '<text x="58" y="62" fill="#f2ede4" font-size="18" font-weight="700" letter-spacing="3">A-SHARE PULSE</text>',
        '<text x="1142" y="62" fill="#9aa5ad" font-size="13" text-anchor="end" letter-spacing="2">DAILY MARKET BRIEF / 每日市场简报</text>',
        '<line x1="58" y1="86" x2="1142" y2="86" stroke="#273037"/>',
        '<text x="58" y="132" fill="#9aa5ad" font-size="13" letter-spacing="2">CROSS-MARKET RISK TEMPERATURE</text>',
        f'<text x="52" y="286" fill="{accent}" font-size="168" font-weight="800" letter-spacing="-12">{score:+d}</text>',
        f'<text x="58" y="336" fill="#f2ede4" font-size="38" font-weight="700">{xml(stance)}</text>',
        f'<text x="58" y="370" fill="#9aa5ad" font-size="14">CONFIDENCE / {xml(confidence)}　UPDATED / {xml(generated_at)} CST</text>',
        '<line x1="446" y1="118" x2="446" y2="382" stroke="#273037"/>',
        '<text x="486" y="134" fill="#9aa5ad" font-size="12" letter-spacing="2">A-SHARE CLOSE</text>',
        f'<text x="486" y="184" fill="#f2ede4" font-size="39" font-weight="700">{xml(numeric(shanghai.get("close")))}</text>',
        f'<text x="727" y="184" fill="{change_color(shanghai.get("pct"))}" font-size="28" font-weight="700">{xml(signed(shanghai.get("pct")))}</text>',
        f'<text x="486" y="218" fill="#68737b" font-size="13">SHANGHAI · {xml(market_date)} · TURNOVER {xml(numeric(daily.get("amount_yi"), 0))} 亿</text>',
        '<text x="486" y="270" fill="#9aa5ad" font-size="12" letter-spacing="2">MARKET BREADTH</text>',
        f'<text x="486" y="318" fill="#ff5148" font-size="31" font-weight="700">↑ {xml(numeric(breadth.get("up"), 0))}</text>',
        f'<text x="670" y="318" fill="#2cc17a" font-size="31" font-weight="700">↓ {xml(numeric(breadth.get("down"), 0))}</text>',
        f'<text x="856" y="318" fill="#e9c86f" font-size="19" font-weight="700">涨停 {xml(numeric(sentiment.get("limit_up"), 0))}</text>',
        f'<text x="856" y="350" fill="#9aa5ad" font-size="14">炸板率 {xml(numeric(sentiment.get("broken_rate"), 1, "%"))}</text>',
        '<line x1="58" y1="408" x2="1142" y2="408" stroke="#273037"/>',
    ]

    cell_width = 256
    for index, (label, pct, stale) in enumerate(market_cells):
        x = 58 + index * 271
        color = change_color(pct)
        out.extend([
            f'<text x="{x}" y="442" fill="#9aa5ad" font-size="12" letter-spacing="1.5">{xml(label)}</text>',
            f'<text x="{x}" y="478" fill="{color}" font-size="27" font-weight="700">{xml(signed(pct))}</text>',
            f'<text x="{x + cell_width}" y="442" fill="#68737b" font-size="10" text-anchor="end">{"STALE" if stale else "LATEST"}</text>',
        ])
        if index < len(market_cells) - 1:
            out.append(f'<line x1="{x + cell_width + 7}" y1="424" x2="{x + cell_width + 7}" y2="486" stroke="#273037"/>')

    out.extend([
        '<line x1="58" y1="500" x2="1142" y2="500" stroke="#273037"/>',
        '<text x="58" y="527" fill="#9aa5ad" font-size="10" font-weight="700" letter-spacing="1.2">CROSS ASSETS</text>',
    ])
    for index, (label, close_text, pct, stale) in enumerate(cross_asset_cells):
        x = 218 + index * 184
        color = change_color(pct)
        out.extend([
            f'<text x="{x}" y="516" fill="#68737b" font-size="9" letter-spacing="1">{xml(label)}{" / STALE" if stale else ""}</text>',
            f'<text x="{x}" y="537" fill="{color}" font-size="13" font-weight="700">{xml(close_text)} / {xml(signed(pct))}</text>',
        ])

    out.extend([
        '<rect x="58" y="550" width="1084" height="34" fill="#101519" stroke="#273037"/>',
        '<text x="78" y="572" fill="#e9c86f" font-size="10" font-weight="700" letter-spacing="1.2">RESEARCH NOTE</text>',
        f'<text x="218" y="572" fill="#f2ede4" font-size="14">{xml(advice)}</text>',
        f'<text x="58" y="610" fill="#68737b" font-size="10">{xml(health_text)} · RESEARCH ONLY, NOT INVESTMENT ADVICE</text>',
        '<text x="1142" y="610" fill="#9aa5ad" font-size="11" text-anchor="end">ychenfen.github.io/a-share-daily</text>',
        '</g>',
        '</svg>',
    ])
    return "\n".join(out)


def generate(output=OUTPUT):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    svg = build_svg(read_json("analysis.json"), read_json("global.json"), read_json("latest.json"))
    output.write_text(svg, encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()
    output = generate(args.output)
    print(f"生成每日市场简报: {output}")


if __name__ == "__main__":
    main()
