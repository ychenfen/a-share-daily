#!/usr/bin/env python3
"""从 CSV 生成走势图 SVG，嵌进 README。

纯手写 SVG，不用 matplotlib：workflow 就不必装依赖，而且矢量图在 GitHub
上比 PNG 清晰。

颜色只用中性灰蓝和红色，在 GitHub 的亮色和暗色主题下都看得清。样式一律写成
presentation attribute（fill=/stroke=），不用 <style> 和 class——README 里的
SVG 是当图片渲染的，内嵌样式表会被剥掉。

用法：
    python3 scripts/chart.py            # 默认画最近 250 个交易日
    python3 scripts/chart.py --days 500
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshot import ROOT, daily_csv_paths, render_readme  # noqa: E402

CHART_DIR = ROOT / "charts"

W, H = 900, 380
PAD_L, PAD_R, PAD_T = 62, 16, 18
LINE_H = 230          # 折线区高度
BAR_H = 70            # 成交额柱状区高度
GAP = 26              # 两区之间留给日期标签

INK = "#57606a"       # 文字，明暗主题都可读
GRID = "#d0d7de"      # 网格
LINE = "#c9211e"      # A股习惯红色代表涨
BAR = "#8c959f"

CAL_CELL = 10
CAL_GAP = 3
CAL_LEFT = 34
CAL_TOP = 30
CAL_EMPTY = "#d0d7de"


def load_rows(days):
    rows = []
    for path in daily_csv_paths():
        with path.open(encoding="utf-8") as f:
            rows.extend(csv.DictReader(f))
    rows.sort(key=lambda r: r["date"])
    return rows[-days:]


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def scale(value, lo, hi, base, size):
    """把数值映射到 SVG 坐标。SVG 的 y 轴向下，所以要翻过来。"""
    if hi == lo:
        return base + size / 2
    return base + size - (value - lo) / (hi - lo) * size


def build_svg(rows, name, label):
    close_col, pct_col = f"{name}_close", f"{name}_pct"
    points = [
        (r["date"], float(r[close_col]), float(r.get("amount_yi") or 0))
        for r in rows
        if r.get(close_col)
    ]
    if len(points) < 2:
        return None

    closes = [p[1] for p in points]
    lo, hi = min(closes), max(closes)
    margin = (hi - lo) * 0.08 or 1
    lo, hi = lo - margin, hi + margin

    plot_w = W - PAD_L - PAD_R
    step = plot_w / (len(points) - 1)
    bar_top = PAD_T + LINE_H + GAP

    out = [
        # XML 声明不能省：GitHub 是用 <img> 加载 SVG 的，响应头不带 charset，
        # 少了这一行浏览器会按 latin-1 解析，中文标题全是乱码
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
        f'<text x="{PAD_L}" y="13" font-size="12" fill="{INK}">'
        f'{esc(label)}　{esc(points[0][0])} ~ {esc(points[-1][0])}　'
        f'共 {len(points)} 个交易日</text>',
    ]

    # 横向网格 + 价格刻度
    for i in range(5):
        value = hi - (hi - lo) * i / 4
        y = PAD_T + LINE_H * i / 4
        out.append(
            f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{W - PAD_R}" y2="{y:.1f}" '
            f'stroke="{GRID}" stroke-width="1" stroke-dasharray="3 3"/>'
        )
        out.append(
            f'<text x="{PAD_L - 6}" y="{y + 4:.1f}" font-size="11" fill="{INK}" '
            f'text-anchor="end">{value:.0f}</text>'
        )

    # 收盘价折线
    coords = [
        (PAD_L + i * step, scale(c, lo, hi, PAD_T, LINE_H))
        for i, (_, c, _) in enumerate(points)
    ]
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    out.append(
        f'<polyline points="{path}" fill="none" stroke="{LINE}" '
        f'stroke-width="1.6" stroke-linejoin="round"/>'
    )

    # 成交额柱：只在有数据时画
    amounts = [p[2] for p in points]
    peak = max(amounts)
    if peak > 0:
        out.append(
            f'<text x="{PAD_L - 6}" y="{bar_top + 10}" font-size="11" fill="{INK}" '
            f'text-anchor="end">成交额</text>'
        )
        bar_w = max(1.0, step * 0.62)
        for i, amount in enumerate(amounts):
            if amount <= 0:
                continue
            h = amount / peak * BAR_H
            x = PAD_L + i * step - bar_w / 2
            out.append(
                f'<rect x="{x:.1f}" y="{bar_top + BAR_H - h:.1f}" '
                f'width="{bar_w:.1f}" height="{h:.1f}" fill="{BAR}" opacity="0.55"/>'
            )
        out.append(
            f'<text x="{W - PAD_R}" y="{bar_top + 10}" font-size="11" fill="{INK}" '
            f'text-anchor="end">峰值 {peak:.0f} 亿</text>'
        )

    # 日期标签：首、中、尾三个就够，多了挤
    baseline = PAD_T + LINE_H + 16
    for idx, anchor in ((0, "start"), (len(points) // 2, "middle"), (len(points) - 1, "end")):
        out.append(
            f'<text x="{PAD_L + idx * step:.1f}" y="{baseline}" font-size="11" '
            f'fill="{INK}" text-anchor="{anchor}">{esc(points[idx][0])}</text>'
        )

    last_date, last_close, _ = points[-1]
    first_close = points[0][1]
    change = (last_close / first_close - 1) * 100
    out.append(
        f'<text x="{W - PAD_R}" y="13" font-size="12" fill="{INK}" text-anchor="end">'
        f'{last_close:.2f}　区间 {change:+.1f}%</text>'
    )
    out.append("</svg>")
    return "\n".join(out)


def market_color(pct):
    """A 股配色：上涨红、下跌绿，幅度越大颜色越深。"""
    if pct >= 2:
        return "#a40e26"
    if pct >= 1:
        return "#d73045"
    if pct > 0:
        return "#f29a9a"
    if pct == 0:
        return "#8c959f"
    if pct > -1:
        return "#8fd0a8"
    if pct > -2:
        return "#3b9b68"
    return "#08783e"


def build_market_calendar(rows):
    """生成 GitHub contribution graph 风格的近一年上证涨跌日历。"""
    values = {}
    for row in rows:
        date_text = row.get("date")
        pct = row.get("上证指数_pct")
        if not date_text or pct in (None, ""):
            continue
        try:
            values[datetime.strptime(date_text, "%Y-%m-%d").date()] = float(pct)
        except ValueError:
            continue
    if not values:
        return None

    last_day = max(values)
    first_day = last_day - timedelta(days=364)
    grid_start = first_day - timedelta(days=first_day.weekday())
    grid_end = last_day + timedelta(days=6 - last_day.weekday())
    weeks = (grid_end - grid_start).days // 7 + 1
    step = CAL_CELL + CAL_GAP
    width = CAL_LEFT + weeks * step + 128
    height = CAL_TOP + 7 * step + 38

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
        f'<text x="{CAL_LEFT}" y="13" font-size="12" fill="{INK}">'
        f'A 股涨跌日历　{first_day} ~ {last_day}　上证指数</text>',
    ]

    # 月份标签按每周的周一定位，避免跨月日期挤在一起。
    previous_month = None
    for week in range(weeks):
        monday = grid_start + timedelta(days=week * 7)
        if monday.month != previous_month:
            x = CAL_LEFT + week * step
            out.append(
                f'<text x="{x}" y="26" font-size="10" fill="{INK}">'
                f'{monday.month}月</text>'
            )
            previous_month = monday.month

    for label, weekday in (("一", 0), ("三", 2), ("五", 4)):
        y = CAL_TOP + weekday * step + CAL_CELL - 1
        out.append(
            f'<text x="{CAL_LEFT - 8}" y="{y}" font-size="9" fill="{INK}" '
            f'text-anchor="end">{label}</text>'
        )

    day = grid_start
    while day <= grid_end:
        week = (day - grid_start).days // 7
        x = CAL_LEFT + week * step
        y = CAL_TOP + day.weekday() * step
        pct = values.get(day)
        color = market_color(pct) if pct is not None else CAL_EMPTY
        opacity = "1" if pct is not None else "0.35"
        title = f"{day}　休市" if pct is None else f"{day}　上证 {pct:+.2f}%"
        out.append(
            f'<rect x="{x}" y="{y}" width="{CAL_CELL}" height="{CAL_CELL}" '
            f'rx="2" fill="{color}" opacity="{opacity}"><title>{title}</title></rect>'
        )
        day += timedelta(days=1)

    legend_y = CAL_TOP + 7 * step + 20
    legend_x = width - 120
    out.append(f'<text x="{legend_x - 6}" y="{legend_y + 8}" font-size="9" fill="{INK}" text-anchor="end">跌</text>')
    legend = [(-2.1, "≤-2%"), (-1.1, ""), (-0.1, ""), (0.1, ""), (1.1, ""), (2.1, "≥2%")]
    for i, (pct, _) in enumerate(legend):
        x = legend_x + i * step
        out.append(
            f'<rect x="{x}" y="{legend_y}" width="{CAL_CELL}" height="{CAL_CELL}" '
            f'rx="2" fill="{market_color(pct)}"/>'
        )
    out.append(f'<text x="{legend_x + len(legend) * step + 1}" y="{legend_y + 8}" font-size="9" fill="{INK}">涨</text>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=250, help="画最近几个交易日")
    args = parser.parse_args()

    rows = load_rows(args.days)
    if not rows:
        print("没有数据，跳过绘图")
        return 0

    CHART_DIR.mkdir(exist_ok=True)
    written = []
    for code, name in (("sh000001", "上证指数"), ("sz399006", "创业板指")):
        svg = build_svg(rows, name, name)
        if svg is None:
            print(f"  {name} 数据不足，跳过", file=sys.stderr)
            continue
        path = CHART_DIR / f"{code}.svg"
        path.write_text(svg, encoding="utf-8")
        written.append(path.name)

    calendar = build_market_calendar(rows)
    if calendar:
        path = CHART_DIR / "market_calendar.svg"
        path.write_text(calendar, encoding="utf-8")
        written.append(path.name)

    # 首次生成图表时 snapshot.py 已经跑完了，那会儿 charts/ 还不存在，
    # README 里不会有图片链接，所以这里再刷一次
    if written:
        from datetime import datetime
        from zoneinfo import ZoneInfo

        render_readme(datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M"))

    print(f"生成图表: {', '.join(written) or '无'}（{len(rows)} 个交易日）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
