#!/usr/bin/env python3
"""Persist live risk signals and settle their forward A-share outcomes.

The scorecard is deliberately forward-only: it starts from the moment the
feature is enabled and never invents a historical hit rate from unavailable
global/news inputs.
"""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshot import DATA_DIR, ROOT, load_daily_rows, write_latest_json  # noqa: E402


SIGNAL_DIR = DATA_DIR / "signals"
SIGNAL_HEADER = [
    "captured_at",
    "slot",
    "signal_date",
    "market_asof_date",
    "score",
    "stance",
    "confidence",
    "sh_close",
    "sh_pct",
    "global_avg",
    "vix",
    "us10y",
    "health",
]
MIN_DIRECTIONAL_SAMPLES = 20


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_signal(status, analysis, global_data, daily):
    captured_at = analysis.get("generated_at")
    if not captured_at or not analysis:
        return None
    markets = [
        number(item.get("pct"))
        for item in global_data.get("markets") or []
        if number(item.get("pct")) is not None
    ]
    health = global_data.get("health") or {}
    degraded = sorted(
        key for key, item in health.items() if item.get("status") != "fresh"
    )
    macro = global_data.get("macro") or {}
    return {
        "captured_at": captured_at,
        "slot": status.get("slot") or "unknown",
        "signal_date": captured_at[:10],
        "market_asof_date": status.get("market_data_date") or (daily or {}).get("date") or "",
        "score": int(analysis.get("score") or 0),
        "stance": analysis.get("stance") or "等待数据",
        "confidence": analysis.get("confidence") or "低",
        "sh_close": (daily or {}).get("上证指数_close") or "",
        "sh_pct": (daily or {}).get("上证指数_pct") or "",
        "global_avg": round(sum(markets) / len(markets), 4) if markets else "",
        "vix": (macro.get("vix") or {}).get("value", ""),
        "us10y": (macro.get("us10y") or {}).get("value", ""),
        "health": "fresh" if not degraded else ",".join(degraded),
    }


def upsert_signal(row):
    SIGNAL_DIR.mkdir(parents=True, exist_ok=True)
    path = SIGNAL_DIR / f"{row['signal_date'][:4]}.csv"
    rows = []
    if path.exists():
        with path.open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
    key = row["captured_at"]
    rows = [item for item in rows if item.get("captured_at") != key]
    rows.append({name: row.get(name, "") for name in SIGNAL_HEADER})
    rows.sort(key=lambda item: item["captured_at"])
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SIGNAL_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def load_signals():
    rows = []
    if not SIGNAL_DIR.exists():
        return rows
    for path in sorted(SIGNAL_DIR.glob("[0-9][0-9][0-9][0-9].csv")):
        with path.open(encoding="utf-8") as stream:
            rows.extend(csv.DictReader(stream))
    return sorted(rows, key=lambda item: item["captured_at"])


def compounded_return(rows):
    value = 1.0
    for row in rows:
        pct = number(row.get("上证指数_pct"))
        if pct is None:
            return None
        value *= 1 + pct / 100
    return round((value - 1) * 100, 6)


def settle_signals(signals, daily_rows):
    dated = [
        (datetime.strptime(row["date"], "%Y-%m-%d").date(), row)
        for row in daily_rows
        if row.get("date")
    ]
    settled = []
    for signal in signals:
        signal_date = datetime.strptime(signal["signal_date"], "%Y-%m-%d").date()
        same_day_slots = {"overnight", "open", "midday"}
        include_same_day = signal.get("slot") in same_day_slots
        candidates = [
            row
            for date, row in dated
            if (date >= signal_date if include_same_day else date > signal_date)
        ]
        item = dict(signal)
        for horizon in (1, 3, 5):
            item[f"return_{horizon}d"] = (
                compounded_return(candidates[:horizon])
                if len(candidates) >= horizon
                else None
            )
        score = number(signal.get("score")) or 0
        outcome = item["return_1d"]
        direction = 1 if score >= 5 else -1 if score <= -5 else 0
        item["direction"] = direction
        item["hit_1d"] = (
            None if not direction or outcome is None else direction * outcome > 0
        )
        settled.append(item)
    return settled


def average(values):
    values = [value for value in values if value is not None]
    return round(sum(values) / len(values), 3) if values else None


def summarize(settled, generated_at):
    matured = [item for item in settled if item.get("return_1d") is not None]
    directional = [item for item in matured if item.get("direction")]
    hits = [item for item in directional if item.get("hit_1d")]
    buckets = []
    definitions = [
        ("防守", -101, -25),
        ("谨慎防守", -25, -5),
        ("中性", -5, 5),
        ("谨慎偏多", 5, 25),
        ("积极", 25, 101),
    ]
    for label, lower, upper in definitions:
        items = [
            item for item in matured
            if lower <= (number(item.get("score")) or 0) < upper
        ]
        buckets.append({
            "label": label,
            "count": len(items),
            "avg_1d_pct": average([item.get("return_1d") for item in items]),
        })
    current = settled[-1] if settled else None
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "method": "真实运行信号的前向检验；不使用回填的全球与新闻数据伪造历史成绩。",
        "status": "ready" if len(directional) >= MIN_DIRECTIONAL_SAMPLES else "collecting",
        "minimum_samples": MIN_DIRECTIONAL_SAMPLES,
        "signal_count": len(settled),
        "matured_1d": len(matured),
        "directional_1d": len(directional),
        "hit_rate_1d": round(len(hits) / len(directional) * 100, 1) if directional else None,
        "average_return": {
            f"{horizon}d": average([item.get(f"return_{horizon}d") for item in settled])
            for horizon in (1, 3, 5)
        },
        "buckets": buckets,
        "current": {
            key: current.get(key)
            for key in ("captured_at", "slot", "score", "stance", "confidence", "health")
        } if current else None,
        "recent": settled[-20:][::-1],
        "disclaimer": "样本量不足时不展示结论；历史表现不代表未来收益。",
    }


def esc(value):
    return (
        str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def build_svg(scorecard):
    current = scorecard.get("current") or {}
    score = int(number(current.get("score")) or 0)
    stance = current.get("stance") or "等待信号"
    directional = scorecard.get("directional_1d") or 0
    minimum = scorecard.get("minimum_samples") or MIN_DIRECTIONAL_SAMPLES
    hit_rate = scorecard.get("hit_rate_1d")
    progress = min(directional / minimum, 1) * 300
    metric = f"{hit_rate:.1f}%" if hit_rate is not None else "待验证"
    color = "#ff554d" if score >= 5 else "#3bc982" if score <= -5 else "#e8d9b5"
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="300" viewBox="0 0 1000 300" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
        '<rect width="1000" height="300" rx="18" fill="#101418"/>',
        '<text x="34" y="42" font-size="13" letter-spacing="2" fill="#9aa5ad">FORWARD CHECK / 前向验证</text>',
        f'<text x="34" y="105" font-size="48" font-weight="700" fill="{color}">{score:+d}</text>',
        f'<text x="36" y="137" font-size="18" fill="#f5f0e8">{esc(stance)}</text>',
        '<text x="330" y="72" font-size="13" fill="#9aa5ad">1 日方向命中率</text>',
        f'<text x="330" y="123" font-size="38" font-weight="700" fill="#f5f0e8">{metric}</text>',
        f'<text x="650" y="72" font-size="13" fill="#9aa5ad">可信样本进度</text>',
        '<rect x="650" y="94" width="300" height="12" rx="6" fill="#293138"/>',
        f'<rect x="650" y="94" width="{progress:.1f}" height="12" rx="6" fill="#e8d9b5"/>',
        f'<text x="650" y="134" font-size="18" fill="#f5f0e8">{directional} / {minimum}</text>',
        '<line x1="34" y1="178" x2="950" y2="178" stroke="#293138"/>',
        '<text x="34" y="217" font-size="16" font-weight="600" fill="#f5f0e8">从现在开始记录，拒绝回填假胜率。</text>',
        '<text x="34" y="249" font-size="12" fill="#9aa5ad">达到 20 个方向性样本后才展示稳定结论；每条信号都可在 Git 历史中审计。</text>',
        '<text x="34" y="278" font-size="11" fill="#68737b">历史表现不代表未来收益，本项目只提供研究记录。</text>',
        '</svg>',
    ])


def main():
    status = read_json(DATA_DIR / "status.json")
    analysis = read_json(DATA_DIR / "analysis.json")
    global_data = read_json(DATA_DIR / "global.json")
    daily_rows = load_daily_rows()
    signal = build_signal(status, analysis, global_data, daily_rows[-1] if daily_rows else None)
    if signal:
        upsert_signal(signal)
    generated_at = analysis.get("generated_at") or status.get("checked_at") or ""
    scorecard = summarize(settle_signals(load_signals(), daily_rows), generated_at)
    output = DATA_DIR / "scorecard.json"
    output.write_text(json.dumps(scorecard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    chart_dir = ROOT / "charts"
    chart_dir.mkdir(exist_ok=True)
    (chart_dir / "signal_scorecard.svg").write_text(build_svg(scorecard), encoding="utf-8")
    write_latest_json(generated_at)
    print(
        f"前向信号 {scorecard['signal_count']} 条，"
        f"已结算 {scorecard['directional_1d']} 条，状态 {scorecard['status']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
