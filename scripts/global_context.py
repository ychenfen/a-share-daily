#!/usr/bin/env python3
"""跨市场行情、宏观压力与新闻驱动的透明分析引擎。

不调用大模型，不生成个股买卖信号。所有分数都由文件内可审计规则计算，
适合作为研究提示而不是个性化投资建议。
"""

import csv
import io
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshot import (  # noqa: E402
    DATA_DIR,
    ROOT,
    beijing_tz,
    fetch,
    load_daily_rows,
    write_latest_json,
)


TENCENT_MARKETS = {
    "usINX": {"code": "SPX", "name": "标普 500", "region": "美国", "kind": "index"},
    "usIXIC": {"code": "NDX", "name": "纳斯达克", "region": "美国", "kind": "index"},
    "usDJI": {"code": "DJIA", "name": "道琼斯", "region": "美国", "kind": "index"},
    "hkHSI": {"code": "HSI", "name": "恒生指数", "region": "中国香港", "kind": "index"},
    "usVGK": {
        "code": "VGK",
        "name": "欧洲股票 ETF",
        "region": "欧洲（美股代理）",
        "kind": "ETF proxy",
    },
}
MARKET_ORDER = [meta["code"] for meta in TENCENT_MARKETS.values()] + ["N225"]

SINA_CROSS_ASSETS = {
    "hf_CHA50CFD": {
        "code": "A50",
        "name": "富时中国 A50 期货",
        "region": "中国离岸",
        "kind": "future",
        "role": "scored",
        "format": "future",
    },
    "fx_susdcnh": {
        "code": "USDCNH",
        "name": "美元兑离岸人民币",
        "region": "中国离岸",
        "kind": "fx",
        "role": "scored",
        "format": "fx",
    },
    "DINIW": {
        "code": "DXY",
        "name": "美元指数",
        "region": "全球",
        "kind": "index",
        "role": "scored",
        "format": "fx",
    },
    "hf_GC": {
        "code": "GOLD",
        "name": "COMEX 黄金",
        "region": "全球商品",
        "kind": "future",
        "role": "context",
        "format": "future",
    },
    "hf_CL": {
        "code": "WTI",
        "name": "WTI 原油",
        "region": "全球商品",
        "kind": "future",
        "role": "context",
        "format": "future",
    },
}
CROSS_ASSET_ORDER = [meta["code"] for meta in SINA_CROSS_ASSETS.values()]

NEWS_QUERY = "A股 美股 日股 全球市场 美联储 央行 when:1d"
NEWS_RELEVANT = (
    "a股", "美股", "日股", "股市", "市场", "美联储", "央行", "利率", "通胀",
    "油价", "黄金", "债市", "科技股", "芯片", "纳指", "标普", "日经",
    "stock", "market", "fed", "inflation", "yield", "nikkei",
)
NEWS_POSITIVE = (
    "上涨", "走高", "反弹", "提振", "降息", "缓和", "利好", "增长", "创新高",
    "普涨", "补涨", "同涨", "突破",
    "gain", "rally", "cut", "boost", "ease",
)
NEWS_NEGATIVE = (
    "下跌", "急跌", "风险", "警告", "加息", "通胀", "冲突", "战争", "暴跌",
    "衰退", "高企", "抛售", "selloff", "warning", "hike", "war", "risk",
)


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def fetch_global_markets(now):
    codes = ",".join(TENCENT_MARKETS)
    raw = fetch(f"https://qt.gtimg.cn/q={codes}", decode="gbk")
    out = []
    for line in raw.split(";"):
        line = line.strip()
        if not line.startswith("v_") or "=" not in line:
            continue
        source_code = line[2 : line.index("=")]
        meta = TENCENT_MARKETS.get(source_code)
        fields = line[line.index('"') + 1 : line.rindex('"')].split("~")
        if not meta or len(fields) < 33:
            continue
        try:
            out.append({
                **meta,
                "close": float(fields[3]),
                "pct": float(fields[32]),
                "change": float(fields[31]),
                "previous_close": float(fields[4]),
                "quote_time": fields[30],
            })
        except (IndexError, ValueError):
            continue

    try:
        nikkei = fetch_fred_values("NIKKEI225", now)
        if len(nikkei) >= 2:
            date, close = nikkei[-1]
            previous = nikkei[-2][1]
            out.append({
                "code": "N225",
                "name": "日经 225",
                "region": "日本",
                "kind": "index",
                "close": close,
                "pct": (close / previous - 1) * 100,
                "change": close - previous,
                "previous_close": previous,
                "quote_time": date,
            })
    except Exception as e:
        print(f"NIKKEI225 获取失败: {e}", file=sys.stderr)
    return out


def _float_or_none(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_sina_cross_assets(raw):
    """Parse Sina's two public quote layouts into one auditable schema."""
    out = []
    for line in raw.splitlines():
        line = line.strip()
        if "hq_str_" not in line or '="' not in line:
            continue
        prefix, quoted = line.split('="', 1)
        source_code = prefix.rsplit("hq_str_", 1)[-1]
        meta = SINA_CROSS_ASSETS.get(source_code)
        if not meta:
            continue
        payload = quoted.rsplit('"', 1)[0]
        if not payload:
            continue
        fields = payload.split(",")
        try:
            if meta["format"] == "future":
                close = float(fields[0])
                previous = _float_or_none(fields[7])
                pct = _float_or_none(fields[1])
                if pct is None and previous:
                    pct = (close / previous - 1) * 100
                quote_time = " ".join(part for part in (fields[12], fields[6]) if part)
            else:
                close = float(fields[1])
                previous = _float_or_none(fields[5])
                pct = (close / previous - 1) * 100 if previous else None
                quote_time = " ".join(part for part in (fields[-1], fields[0]) if part)
        except (IndexError, ValueError):
            continue
        out.append({
            key: value for key, value in meta.items() if key != "format"
        } | {
            "close": close,
            "pct": pct,
            "change": close - previous if previous is not None else None,
            "previous_close": previous,
            "quote_time": quote_time,
        })
    return out


def fetch_cross_assets():
    codes = ",".join(SINA_CROSS_ASSETS)
    raw = fetch(
        f"https://hq.sinajs.cn/list={codes}",
        decode="gb18030",
        headers={"Referer": "https://finance.sina.com.cn/"},
    )
    return parse_sina_cross_assets(raw)


def merge_market_snapshots(current, previous):
    """保留本轮有效报价，并只为缺失市场回退上一份数据。"""
    current_by_code = {item.get("code"): item for item in current}
    previous_by_code = {item.get("code"): item for item in previous}
    merged = []
    for code in MARKET_ORDER:
        item = current_by_code.get(code)
        stale = False
        if item is None:
            item = previous_by_code.get(code)
            stale = item is not None
        if item is not None:
            merged.append({**item, "stale": stale})
    return merged


def merge_cross_asset_snapshots(current, previous):
    """Merge by fixed order and make every fallback visible as stale."""
    current_by_code = {item.get("code"): item for item in current}
    previous_by_code = {item.get("code"): item for item in previous}
    merged = []
    for code in CROSS_ASSET_ORDER:
        item = current_by_code.get(code)
        stale = False
        if item is None:
            item = previous_by_code.get(code)
            stale = item is not None
        if item is not None:
            merged.append({**item, "stale": stale})
    return merged


def fetch_fred_values(series, now):
    start = (now.date() - timedelta(days=40)).isoformat()
    raw = fetch(
        f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={start}"
    )
    values = []
    for row in csv.DictReader(io.StringIO(raw)):
        value = row.get(series)
        if value not in (None, "", "."):
            values.append((row["observation_date"], float(value)))
    return values


def fetch_fred_latest(series, now):
    values = fetch_fred_values(series, now)
    if not values:
        return None
    date, value = values[-1]
    return {"date": date, "value": value}


def fetch_news():
    url = (
        "https://news.google.com/rss/search?q="
        f"{quote_plus(NEWS_QUERY)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    )
    root = ET.fromstring(fetch(url))
    news = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        source_node = item.find("source")
        source = (source_node.text or "").strip() if source_node is not None else ""
        suffix = f" - {source}"
        if source and title.endswith(suffix):
            title = title[: -len(suffix)].strip()
        lowered = title.lower()
        if not any(keyword in lowered for keyword in NEWS_RELEVANT):
            continue
        if urlparse(link).scheme not in ("http", "https"):
            continue
        news.append({
            "title": title,
            "source": source,
            "published": (item.findtext("pubDate") or "").strip(),
            "link": link,
        })
        if len(news) == 8:
            break
    return news


def news_tone(news):
    positive = negative = 0
    for item in news:
        title = item.get("title", "").lower()
        positive += sum(keyword in title for keyword in NEWS_POSITIVE)
        negative += sum(keyword in title for keyword in NEWS_NEGATIVE)
    return {
        "positive_hits": positive,
        "negative_hits": negative,
        "score": int(clamp((positive - negative) * 2, -8, 8)),
    }


def analyze(markets, macro, daily, news, generated_at, health=None, cross_assets=None):
    signals = []

    def add(label, value, contribution, note):
        signals.append({
            "label": label,
            "value": value,
            "contribution": round(contribution, 1),
            "note": note,
        })

    sh_pct = float(daily.get("上证指数_pct") or 0) if daily else 0
    a_momentum = clamp(sh_pct * 8, -20, 20)
    add("A股动量", f"上证 {sh_pct:+.2f}%", a_momentum, "反映本地市场价格强弱")

    up = int(float(daily.get("up") or 0)) if daily else 0
    down = int(float(daily.get("down") or 0)) if daily else 0
    breadth_ratio = (up - down) / (up + down) if up + down else 0
    breadth = clamp(breadth_ratio * 20, -20, 20)
    add("市场宽度", f"涨 {up} / 跌 {down}", breadth, "上涨家数占优时提高风险偏好")

    limit_up = int(float(daily.get("limit_up") or 0)) if daily else 0
    limit_down = int(float(daily.get("limit_down") or 0)) if daily else 0
    broken_rate = float(daily.get("broken_rate") or 0) if daily else 0
    sentiment = clamp((limit_up - limit_down) / 6 - broken_rate / 8, -15, 15)
    add(
        "短线情绪",
        f"涨停 {limit_up} / 跌停 {limit_down} / 炸板率 {broken_rate:.1f}%",
        sentiment,
        "涨停扩散加分，炸板率过高扣分",
    )

    equity_values = [m["pct"] for m in markets if m.get("pct") is not None]
    global_average = sum(equity_values) / len(equity_values) if equity_values else 0
    global_score = clamp(global_average * 7, -20, 20)
    add(
        "外围股市",
        f"{len(equity_values)} 个市场均值 {global_average:+.2f}%",
        global_score,
        "衡量隔夜风险偏好共振",
    )

    cross_by_code = {item.get("code"): item for item in (cross_assets or [])}
    a50 = cross_by_code.get("A50") or {}
    a50_pct = None if a50.get("stale") else _float_or_none(a50.get("pct"))
    a50_score = clamp(a50_pct * 6, -8, 8) if a50_pct is not None else 0
    add(
        "A50 先行",
        f"富时 A50 {a50_pct:+.2f}%" if a50_pct is not None else "富时 A50 缺失或陈旧",
        a50_score,
        "离岸期货只作低权重先行确认，避免重复计算 A 股现货动量",
    )

    usdcnh = cross_by_code.get("USDCNH") or {}
    dxy = cross_by_code.get("DXY") or {}
    cnh_pct = None if usdcnh.get("stale") else _float_or_none(usdcnh.get("pct"))
    dxy_pct = None if dxy.get("stale") else _float_or_none(dxy.get("pct"))
    fx_components = []
    fx_parts = []
    if cnh_pct is not None:
        fx_components.append(-cnh_pct * 12)
        fx_parts.append(f"USD/CNH {usdcnh.get('close'):.4f} ({cnh_pct:+.2f}%)")
    if dxy_pct is not None:
        fx_components.append(-dxy_pct * 5)
        fx_parts.append(f"DXY {dxy.get('close'):.2f} ({dxy_pct:+.2f}%)")
    fx_score = clamp(sum(fx_components), -8, 8) if fx_components else 0
    add(
        "美元与人民币",
        " / ".join(fx_parts) if fx_parts else "汇率数据缺失或陈旧",
        fx_score,
        "美元走弱与人民币走强通常缓解外部流动性压力",
    )

    vix = (macro.get("vix") or {}).get("value")
    if vix is None:
        vix_score = 0
        vix_text = "缺失"
    else:
        vix_score = 5 if vix < 15 else (-15 if vix >= 30 else -10 if vix >= 25 else -5 if vix >= 20 else 0)
        vix_text = f"{vix:.2f}"
    add("波动压力", f"VIX {vix_text}", vix_score, "VIX 越高，全球避险需求通常越强")

    yield_10y = (macro.get("us10y") or {}).get("value")
    if yield_10y is None:
        yield_score = 0
        yield_text = "缺失"
    else:
        yield_score = -8 if yield_10y >= 5 else -5 if yield_10y >= 4.5 else 3 if yield_10y < 3.5 else 0
        yield_text = f"{yield_10y:.2f}%"
    add("利率压力", f"美债 10Y {yield_text}", yield_score, "长端利率偏高时压制高估值资产")

    tone = news_tone(news)
    add(
        "新闻语气",
        f"正向词 {tone['positive_hits']} / 风险词 {tone['negative_hits']}",
        tone["score"],
        "标题关键词只做低权重提示，不代替事实核验",
    )

    score = int(round(clamp(sum(item["contribution"] for item in signals), -100, 100)))
    if score >= 25:
        stance, color = "积极但不追高", "#c9211e"
        summary = "A股内部强度与外围风险偏好形成正向共振，但仍需用回撤和量能确认持续性。"
        advice = [
            "关注强势行业能否在下一交易日继续获得成交额与市场宽度支持。",
            "研究执行宜分批、等待回撤确认，避免把单日普涨直接外推成趋势。",
        ]
    elif score >= 5:
        stance, color = "谨慎偏多", "#e05a47"
        summary = "风险偏好略占优，但信号并未形成全面共振。"
        advice = ["保留进攻观察清单，同时以市场宽度和外围指数是否续强作为确认条件。"]
    elif score > -5:
        stance, color = "中性等待", "#8c959f"
        summary = "多空线索接近平衡，等待价格、宽度或宏观压力出现更清晰方向。"
        advice = ["减少方向性预判，优先记录关键阈值被突破后的跟随信号。"]
    elif score > -25:
        stance, color = "谨慎防守", "#3b9b68"
        summary = "外部或内部风险信号偏多，短期更适合提高验证门槛。"
        advice = ["降低追涨优先级，重点观察 VIX、长端利率和跌停扩散是否继续恶化。"]
    else:
        stance, color = "防守优先", "#08783e"
        summary = "内部市场与外围压力形成负向共振，先控制暴露并等待风险指标回落。"
        advice = ["研究上优先压力测试与回撤控制，避免仅凭单条利好逆势下注。"]

    cross_coverage = a50_pct is not None and (cnh_pct is not None or dxy_pct is not None)
    coverage = sum([
        bool(daily),
        bool(equity_values),
        cross_coverage,
        vix is not None,
        yield_10y is not None,
        bool(news),
    ])
    source_states = [item.get("status") for item in (health or {}).values()]
    degraded = any(state != "fresh" for state in source_states)
    confidence = "高" if coverage == 6 and not degraded else "中" if coverage >= 4 else "低"
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "score": score,
        "stance": stance,
        "color": color,
        "confidence": confidence,
        "summary": summary,
        "signals": signals,
        "advice": advice,
        "news_tone": tone,
        "news": news,
        "methodology": "透明规则评分：A股动量、市场宽度、短线情绪、外围股市、A50先行、美元与人民币、VIX、美债10Y和新闻标题低权重语气；黄金与原油只作背景。",
        "disclaimer": "仅用于市场研究与风险观察，不构成个性化投资建议或收益承诺。",
    }


def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_dashboard(global_data, analysis):
    markets = global_data.get("markets") or []
    width, height = 1000, 390
    center, max_bar = 350, 150
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
        '<rect width="1000" height="390" rx="14" fill="#f6f8fa"/>',
        '<text x="28" y="32" font-size="18" font-weight="700" fill="#24292f">全球市场雷达</text>',
        f'<text x="970" y="30" font-size="11" fill="#57606a" text-anchor="end">{esc(global_data.get("generated_at", ""))} 北京时间</text>',
        f'<line x1="{center}" y1="54" x2="{center}" y2="285" stroke="#8c959f" stroke-width="1"/>',
    ]

    for i, market in enumerate(markets):
        y = 72 + i * 42
        pct = market.get("pct") or 0
        bar = min(abs(pct) / 3 * max_bar, max_bar)
        color = "#c9211e" if pct > 0 else "#08783e" if pct < 0 else "#8c959f"
        x = center if pct >= 0 else center - bar
        out += [
            f'<text x="28" y="{y + 4}" font-size="13" fill="#24292f">{esc(market["name"])}</text>',
            f'<text x="210" y="{y + 4}" font-size="12" fill="#57606a" text-anchor="end">{market["close"]:,.2f}</text>',
            f'<rect x="{x:.1f}" y="{y - 10}" width="{max(bar, 2):.1f}" height="18" rx="4" fill="{color}" opacity="0.85"/>',
            f'<text x="{center + max_bar + 14}" y="{y + 4}" font-size="13" font-weight="600" fill="{color}">{pct:+.2f}%</text>',
        ]

    score = analysis.get("score", 0)
    gauge_x, gauge_y, gauge_w = 610, 105, 320
    marker_x = gauge_x + (score + 100) / 200 * gauge_w
    color = analysis.get("color", "#8c959f")
    out += [
        '<text x="610" y="70" font-size="15" font-weight="700" fill="#24292f">跨市场风险温度</text>',
        f'<text x="930" y="70" font-size="24" font-weight="700" fill="{color}" text-anchor="end">{score:+d}</text>',
        f'<rect x="{gauge_x}" y="{gauge_y}" width="{gauge_w}" height="14" rx="7" fill="#d0d7de"/>',
        f'<rect x="{gauge_x}" y="{gauge_y}" width="{max(marker_x - gauge_x, 1):.1f}" height="14" rx="7" fill="{color}" opacity="0.75"/>',
        f'<circle cx="{marker_x:.1f}" cy="{gauge_y + 7}" r="9" fill="{color}" stroke="#ffffff" stroke-width="3"/>',
        '<text x="610" y="137" font-size="10" fill="#57606a">-100 防守</text>',
        '<text x="930" y="137" font-size="10" fill="#57606a" text-anchor="end">+100 积极</text>',
        f'<text x="610" y="175" font-size="20" font-weight="700" fill="{color}">{esc(analysis.get("stance", "等待数据"))}</text>',
        f'<text x="610" y="200" font-size="11" fill="#57606a">置信度：{esc(analysis.get("confidence", "低"))}</text>',
    ]

    macro = global_data.get("macro") or {}
    vix = (macro.get("vix") or {}).get("value")
    us10y = (macro.get("us10y") or {}).get("value")
    out += [
        '<rect x="610" y="225" width="145" height="72" rx="9" fill="#ffffff" stroke="#d0d7de"/>',
        '<text x="626" y="249" font-size="11" fill="#57606a">VIX 波动率</text>',
        f'<text x="626" y="279" font-size="24" font-weight="700" fill="#24292f">{vix if vix is not None else "-"}</text>',
        '<rect x="775" y="225" width="155" height="72" rx="9" fill="#ffffff" stroke="#d0d7de"/>',
        '<text x="791" y="249" font-size="11" fill="#57606a">美国 10Y 国债</text>',
        f'<text x="791" y="279" font-size="24" font-weight="700" fill="#24292f">{f"{us10y:.2f}%" if us10y is not None else "-"}</text>',
        f'<text x="28" y="340" font-size="12" fill="#24292f">{esc(analysis.get("summary", ""))}</text>',
        '<text x="28" y="367" font-size="10" fill="#57606a">红涨绿跌；评分是可审计研究指标，不是买卖信号。</text>',
        "</svg>",
    ]
    return "\n".join(out)


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json_or_empty(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, json.JSONDecodeError):
        return {}


def main():
    now = datetime.now(beijing_tz())
    stamp = now.strftime("%Y-%m-%d %H:%M")
    previous_global = DATA_DIR / "global.json"
    previous_analysis = DATA_DIR / "analysis.json"
    previous_global_data = read_json_or_empty(previous_global)
    previous_analysis_data = read_json_or_empty(previous_analysis)
    health = {}

    try:
        current_markets = fetch_global_markets(now)
    except Exception as e:
        print(f"全球指数获取失败: {e}", file=sys.stderr)
        current_markets = []
    markets = merge_market_snapshots(
        current_markets, previous_global_data.get("markets") or []
    )
    fresh_markets = sum(not item.get("stale") for item in markets)
    if fresh_markets == len(MARKET_ORDER):
        health["markets"] = {"status": "fresh"}
    elif fresh_markets:
        health["markets"] = {"status": "partial"}
    else:
        health["markets"] = {"status": "stale" if markets else "missing"}

    try:
        current_cross_assets = fetch_cross_assets()
    except Exception as e:
        print(f"跨资产行情获取失败: {e}", file=sys.stderr)
        current_cross_assets = []
    cross_assets = merge_cross_asset_snapshots(
        current_cross_assets, previous_global_data.get("cross_assets") or []
    )
    fresh_cross_assets = sum(not item.get("stale") for item in cross_assets)
    if fresh_cross_assets == len(CROSS_ASSET_ORDER):
        health["cross_assets"] = {"status": "fresh"}
    elif fresh_cross_assets:
        health["cross_assets"] = {"status": "partial"}
    else:
        health["cross_assets"] = {
            "status": "stale" if cross_assets else "missing"
        }

    macro = {}
    previous_macro = previous_global_data.get("macro") or {}
    for key, series in (("vix", "VIXCLS"), ("us10y", "DGS10")):
        try:
            latest = fetch_fred_latest(series, now)
            if not latest:
                raise ValueError("没有可用观测值")
            macro[key] = {**latest, "stale": False}
            health[key] = {"status": "fresh"}
        except Exception as e:
            print(f"{series} 获取失败: {e}", file=sys.stderr)
            fallback = previous_macro.get(key)
            if fallback:
                macro[key] = {**fallback, "stale": True}
                health[key] = {"status": "stale"}
            else:
                health[key] = {"status": "missing"}

    try:
        news = fetch_news()
        if not news:
            raise ValueError("没有相关标题")
        health["news"] = {"status": "fresh"}
    except Exception as e:
        print(f"新闻 RSS 获取失败: {e}", file=sys.stderr)
        news = previous_analysis_data.get("news") or []
        health["news"] = {"status": "stale" if news else "missing"}

    global_data = {
        "schema_version": 1,
        "generated_at": stamp,
        "markets": markets,
        "cross_assets": cross_assets,
        "macro": macro,
        "health": health,
        "sources": {
            "markets": "腾讯全球行情公开接口 + FRED（日经225）",
            "cross_assets": "新浪财经公开行情（A50、汇率、美元、黄金、原油）",
            "macro": "Federal Reserve Economic Data (FRED)",
            "news": "Google News RSS（仅标题、来源和链接）",
        },
    }
    rows = load_daily_rows()
    analysis = analyze(
        markets,
        macro,
        rows[-1] if rows else None,
        news,
        stamp,
        health=health,
        cross_assets=cross_assets,
    )

    DATA_DIR.mkdir(exist_ok=True)
    write_json(previous_global, global_data)
    write_json(previous_analysis, analysis)
    chart_dir = ROOT / "charts"
    chart_dir.mkdir(exist_ok=True)
    (chart_dir / "global_dashboard.svg").write_text(
        build_dashboard(global_data, analysis), encoding="utf-8"
    )
    write_latest_json(stamp)
    print(
        f"全球市场 {len(markets)} 个，跨资产 {len(cross_assets)} 个，新闻 {len(news)} 条，"
        f"风险温度 {analysis['score']:+d}（{analysis['stance']}）"
    )
    return 0 if markets else 1


if __name__ == "__main__":
    sys.exit(main())
