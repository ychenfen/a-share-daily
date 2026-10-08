<div align="center">

# 📈 A-Share Pulse

**把 GitHub 提交图变成 A 股市场心电图。**

每天五次联动全球收盘、A 股盘中与新闻风险；零依赖、可审计、可直接 Fork。

<a href="https://github.com/ychenfen/a-share-daily/actions/workflows/daily.yml"><img alt="A-share market pulse" src="https://github.com/ychenfen/a-share-daily/actions/workflows/daily.yml/badge.svg"></a>
<a href="https://ychenfen.github.io/a-share-daily/"><img alt="Live dashboard" src="https://img.shields.io/badge/live-dashboard-ff5148"></a>
<img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
<img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-zero-2ea44f">
<a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>

[English](README.en.md) · 简体中文

</div>

<a href="https://ychenfen.github.io/a-share-daily/"><img alt="A-Share Pulse 市场天气台" src="assets/social-preview.png"></a>

> [!NOTE]
> **⚪ 休市 / 未开盘** · 目标日未开市或尚未产生行情，最近交易日 2026-10-08 · 最后检查 `2026-10-09 02:53`（北京时间）

[🌐 在线大屏](https://ychenfen.github.io/a-share-daily/) · [一键生成自己的版本](https://github.com/ychenfen/a-share-daily/generate) · [最新 JSON](data/latest.json) · [运行状态](data/status.json) · [完整历史](data/) · [数据字典](docs/DATA_SCHEMA.md) · [自动任务](https://github.com/ychenfen/a-share-daily/actions) · [讨论区](https://github.com/ychenfen/a-share-daily/discussions) · [路线图](ROADMAP.md) · [参与贡献](CONTRIBUTING.md)

## 为什么值得收藏

| 能力 | 你得到什么 |
| --- | --- |
| 🫀 五段市场脉搏 | 外围收盘 + A 股开盘、午间、收盘、夜间校验，不只是日终一个点 |
| 🧠 情绪温度计 | 涨跌家数、涨停/跌停、炸板率、最高连板和行业强弱 |
| 🟩 GitHub 风格日历 | 用红绿贡献格复刻近一年市场节奏，适合截图分享 |
| 🖥️ 在线研究大屏 | GitHub Pages 自动部署，手机和桌面都能直接查看 |
| 🌍 跨资产先行带 | A50、离岸人民币与美元指数低权重计分，黄金和原油保留为背景 |
| 🧭 事件传导链 | 新闻先去重分类，再映射宏观变量、A 股风格和可证伪条件 |
| 🗞️ 每日传播卡片 | 自动生成 1200×630 矢量简报，可下载、引用和转发 |
| 🧾 Git 原生数据湖 | 每次变化都有 diff，可追溯、可回滚，CSV/JSON 直接用于研究 |
| 🪶 零第三方依赖 | 只用 Python 标准库和 GitHub Actions，Fork 后无需服务器 |
| 🛡️ 质量门禁 | 每次推送前跑回归测试、schema 和重复日期检查 |

## 今日市场简报

<a href="https://ychenfen.github.io/a-share-daily/#share"><img alt="A-Share Pulse 每日市场简报" src="charts/daily_brief.svg"></a>

[打开可交互大屏](https://ychenfen.github.io/a-share-daily/) · [下载 SVG](charts/daily_brief.svg)

## 全球市场与策略雷达

![全球市场与跨市场风险温度](charts/global_dashboard.svg)

> **风险温度 -25 · 防守优先**（置信度：中）
> 内部市场与外围压力形成负向共振，先控制暴露并等待风险指标回落。

| 市场 | 地区 | 收盘 | 涨跌幅 |
| --- | --- | ---: | ---: |
| 标普 500 | 美国 | 7756.35 | -0.58% |
| 纳斯达克 | 美国 | 27164.37 | -1.36% |
| 道琼斯 | 美国 | 51178.04 | +0.00% |
| 恒生指数 | 中国香港 | 23785.79 | -1.43% |
| 欧洲股票 ETF | 欧洲（美股代理） | 85.37 | -0.23% |
| 日经 225 | 日本 | 65018.95 | +1.38% |

### 跨资产先行带

> A50 与美元/人民币组合仅作低权重评分；黄金和原油只提供风险背景，不直接加减分。

| 资产 | 角色 | 最新值 | 涨跌幅 | 状态 |
| --- | --- | ---: | ---: | --- |
| 富时中国 A50 期货 | 低权重计分 | 13,678.16 | -0.28% | 最新 |
| 美元兑离岸人民币 | 低权重计分 | 6.7038 | +0.02% | 最新 |
| 美元指数 | 低权重计分 | 102.12 | -0.16% | 最新 |
| COMEX 黄金 | 背景观察 | 4,153.41 | +0.31% | 最新 |
| WTI 原油 | 背景观察 | 91.63 | +3.79% | 最新 |

> ⚠️ 数据降级：全球指数、VIX、美债10Y本轮未完全刷新，已尽量保留最近有效值。

### 风险温度拆解

| 信号 | 当前值 | 分数贡献 | 解释 |
| --- | --- | ---: | --- |
| A股动量 | 上证 -0.79% | -6.3 | 反映本地市场价格强弱 |
| 市场宽度 | 涨 1718 / 跌 3798 | -7.5 | 上涨家数占优时提高风险偏好 |
| 短线情绪 | 涨停 43 / 跌停 13 / 炸板率 42.7% | -0.3 | 涨停扩散加分，炸板率过高扣分 |
| 外围股市 | 6 个市场均值 -0.37% | -2.6 | 衡量隔夜风险偏好共振 |
| A50 先行 | 富时 A50 -0.28% | -1.7 | 离岸期货只作低权重先行确认，避免重复计算 A 股现货动量 |
| 美元与人民币 | USD/CNH 6.7038 (+0.02%) / DXY 102.12 (-0.16%) | +0.6 | 美元走弱与人民币走强通常缓解外部流动性压力 |
| 波动压力 | VIX 15.44 | +0.0 | VIX 越高，全球避险需求通常越强 |
| 利率压力 | 美债 10Y 4.94% | -5.0 | 长端利率偏高时压制高估值资产 |
| 新闻语气 | 正向词 0 / 风险词 1 | -2.0 | 标题关键词只做低权重提示，不代替事实核验 |

### 事件传导链

> 去重标题只作为待验证线索；分类数量不是已确认事件，传导链也不直接参与评分。

| 事件线索 | 宏观传导 | A 股映射 | 观察指标 | 失效条件 |
| --- | --- | --- | --- | --- |
| 央行与利率（3 条） | 政策利率预期 → 美债收益率与美元 → 全球流动性 | 高估值成长、券商、地产与人民币敏感资产 | 美债10Y 4.94%（最近有效值） / 美元指数 102.12 / -0.16%（最新） / USD/CNH 6.7038 / +0.02%（最新） | 失效条件：若美债利率、美元与人民币没有同向确认，标题冲击可能只是短期噪音。 |
| 科技与产业（2 条） | 科技盈利与估值 → 全球成长风格 → 风险偏好扩散 | 半导体、算力、通信与其他高估值成长方向 | 纳斯达克 27,164.37 / -1.36%（最新） / 富时A50 13,678.16 / -0.28%（最新） / 美债10Y 4.94%（最近有效值） | 失效条件：若纳指走弱、A50 不确认或长端利率继续上行，主题热度不等于趋势。 |

### 研究观察

- 研究上优先压力测试与回撤控制，避免仅凭单条利好逆势下注。

### 新闻雷达

- [纳指新高、日经站上7万点，节后A股会怎么走？](https://news.google.com/rss/articles/CBMilAFBVV95cUxPT21Jb09GUTNHd3R3cDBSelNhcU9OeFRnZFNCdHg4d05iZEQwWWdldkNxcTBYQWNpNjhxbWtMLVpfSEpzV0syWEJpVG9BbF9yTTU5WFgtU3NuVlFRREJLS2tJRFd2NFRSNGRZZ2FQdkg2TUVld3RQeUJLNGVpMEdSNWdyUDZESGh1VHFUZVJGY2JLbEE4?oc=5) · 新浪网
- [申万宏源策略：A股长中期的波段定位](https://news.google.com/rss/articles/CBMiYEFVX3lxTE1IcjZZNHFJVVVVbFFOVFNnOU1CRTZ2bGFxamwtamtUazRJcXNXLTdaUWZldkNWOFZlSkVIQng3ZlM2djl3TmtEbVVJNGhBVFQybUhadldsNTJhTUQxQUIzeQ?oc=5) · 东方财富
- [股债双杀！海外市场“变脸”；中国资产，关注度不降反升；美联储，重磅信号](https://news.google.com/rss/articles/CBMickFVX3lxTE51WHZjam1MZGZCemJUQ0k4NFIyVU8xVXAybVRhRklfMWt0TWpWTFJSbnU0dldBZlQyLTJUMUF0Y29oMXdwYlo5eEFUTVF1YUUzMFVYT2tNT3FuZkNLVGZVUWNDa0Flc2NJZEx3VVU2U0ljUQ?oc=5) · 金融界
- [节后A股或迎来修复行情](https://news.google.com/rss/articles/CBMiakFVX3lxTFBmN0hvVTVPdmlVdFlEMDJDblBFd3BCb0dRUk93b2syV3JCSnlCVTJILXpkUDhYN25yR0xXdTktMTFWOXV5dXVmUjh3b3ZoTUwydzdYNjdtcHFPOU05VGpwS0F2N1VMWmUxUEE?oc=5) · 温州新闻
- [全球市场：美股三大指数收跌大型科技股涨跌不一美光科技涨超4%_证券要闻](https://news.google.com/rss/articles/CBMibkFVX3lxTE5KbjJqSnltTTNOMWRtOFVsQ3V5dF9VX2xVX2dmcFBkMHNNT2o0aUYyQ1BrZEhEVi1ZeHFGRlM5QzlyUk5XUWlLTGRoNEdtY1RjM2ZBSmRPdzBvVGY3TW9BYlVyU0ZNVlZlTEswZ3B3?oc=5) · 中金在线
- [美债已在定价危机，美股为何仍岿然不动？德银揭示五大市场结构性错位](https://news.google.com/rss/articles/CBMilwFBVV95cUxPSkszSmZ0MWlUWXJoWVhHcjY1TnlGWEpqN0JuWDMxbWhXZ2FMdGtJUS16WDBsdktHUFFLYlJPanZkQUpZOXRqSFBkZ1VWNUt3eGNSUWxQVmFnX0RYQ2phUHY5OXBRdDQ2WjZWUEVsUFFQMWFJVnpTNF9tMzdnbU42RnlDUGtKYzE3cmNWTjZsQlVwWGhJb0tV?oc=5) · 富途牛牛

方法：透明规则评分：A股动量、市场宽度、短线情绪、外围股市、A50先行、美元与人民币、VIX、美债10Y和新闻标题低权重语气；黄金与原油只作背景，事件传导链不直接计分。

> 这是可审计的通用市场研究提示，不是个性化仓位或买卖建议。

## 信号成绩单

![风险信号前向验证](charts/signal_scorecard.svg)

> 1 日方向命中率 **64.6%**，当前有效样本 **82** 条。

方法：开盘/午间信号验证当日收盘，收盘/夜间信号验证下一交易日；同时持续结算 3 日和 5 日复合收益。

> 样本不足时不输出稳定性结论，历史表现也不代表未来收益。

## 走势

![近一年 A 股涨跌日历](charts/market_calendar.svg)

![上证指数](charts/sh000001.svg)

![创业板指](charts/sz399006.svg)

## 最近 10 个交易日

| 日期 | 上证 | 深成 | 创业板 | 沪深300 | 科创50 | 成交额(亿) | 涨/跌/平 | 涨停 | 跌停 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-08 | 3811.90<br>-0.79% | 12620.90<br>-2.07% | 3036.66<br>-3.15% | 4310.28<br>-1.09% | 1456.32<br>-4.82% | 16821 | 1718/3798/118 | 43 | 13 |
| 2026-09-30 | 3842.19<br>+0.31% | 12887.62<br>-0.11% | 3135.28<br>-0.23% | 4357.62<br>+0.29% | 1530.01<br>-2.51% | 14380 | 2614/2841/183 | 52 | 9 |
| 2026-09-29 | 3830.45<br>+0.18% | 12901.95<br>+0.34% | 3142.56<br>+0.09% | 4345.21<br>+0.10% | 1569.34<br>+0.86% | 14092 | 3525/1944/167 | 57 | 10 |
| 2026-09-28 | 3823.62<br>-1.67% | 12858.75<br>-3.44% | 3139.82<br>-4.53% | 4340.76<br>-2.22% | 1555.98<br>-4.06% | 17028 | 910/4607/117 | 33 | 56 |
| 2026-09-24 | 3888.37<br>-1.22% | 13316.97<br>-2.34% | 3288.95<br>-2.68% | 4439.14<br>-1.73% | 1621.87<br>-2.35% | 16534 | 1134/4352/148 | 52 | 13 |
| 2026-09-23 | 3936.52<br>-0.39% | 13636.07<br>-0.64% | 3379.61<br>-0.60% | 4517.28<br>-0.60% | 1660.85<br>-0.25% | 17650 | 1910/3605/118 | 51 | 13 |
| 2026-09-22 | 3952.13<br>+0.06% | 13723.74<br>-0.05% | 3399.93<br>+0.01% | 4544.59<br>+0.11% | 1665.04<br>+0.46% | 21356 | 2391/3077/163 | 63 | 3 |
| 2026-09-21 | 3949.91<br>+0.97% | 13730.02<br>+0.65% | 3399.59<br>+0.80% | 4539.57<br>+0.71% | 1657.48<br>+0.29% | 20315 | 4583/951/96 | 103 | 2 |
| 2026-09-18 | 3911.87<br>+0.94% | 13640.87<br>+1.72% | 3372.68<br>+2.25% | 4507.39<br>+1.06% | 1652.63<br>+2.88% | 20771 | 4277/1173/180 | 78 | 0 |
| 2026-09-17 | 3875.60<br>-0.41% | 13409.91<br>-0.33% | 3298.31<br>-0.40% | 4460.16<br>-0.45% | 1606.29<br>-0.61% | 18231 | -/-/- | - | - |

完整历史在 [data/](data/) 目录，共 667 个交易日。

## 市场情绪

最新交易日 2026-10-08：

- 涨停 **43** 家，跌停 **13** 家
- 炸板 32 家，炸板率 **42.7%**（越高说明封板越不牢）
- 最高 **8** 连板，2 板及以上共 10 家

| 日期 | 涨停 | 跌停 | 炸板 | 炸板率 | 最高连板 | 连板家数 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-10-08 | 43 | 13 | 32 | 42.7% | 8 | 10 |
| 2026-09-30 | 52 | 9 | 12 | 18.8% | 9 | 16 |
| 2026-09-29 | 57 | 10 | 8 | 12.3% | 13 | 18 |
| 2026-09-28 | 33 | 56 | 11 | 25.0% | 12 | 10 |
| 2026-09-24 | 52 | 13 | 10 | 16.1% | 7 | 19 |
| 2026-09-23 | 51 | 13 | 26 | 33.8% | 9 | 14 |
| 2026-09-22 | 63 | 3 | 18 | 22.2% | 9 | 27 |
| 2026-09-21 | 103 | 2 | 25 | 19.5% | 17 | 31 |
| 2026-09-18 | 78 | 0 | 25 | 24.3% | 16 | 18 |

## 行业板块

2026-10-08 领涨与领跌各五个：

| | 行业 | 涨跌幅 | 主力净流入(亿) | 领涨股 |
| --- | --- | --- | --- | --- |
| 领涨 | 蓄电池及其他电池 | +5.19% | 6.19 | 雄韬股份 |
|  | 锂电专用设备 | +4.98% | 6.06 | 尚水智能 |
|  | 焦炭Ⅲ | +3.75% | 2.05 | 安泰集团 |
|  | 焦炭Ⅱ | +3.75% | 2.05 | 安泰集团 |
|  | 油气及炼化工程 | +3.71% | 1.28 | 博迈科 |
| 领跌 | 视频媒体 | -8.71% | -2.06 | 芒果超媒 |
|  | 文字媒体 | -7.95% | -2.01 | 掌阅科技 |
|  | 分立器件 | -6.36% | -10.46 | ST派瑞 |
|  | 集成电路制造 | -5.52% | -18.54 | 燧原科技-U |
|  | 模拟芯片设计 | -5.40% | -7.64 | 慧智微-U |

## 自动更新节奏

| 北京时间 | 记录内容 | 正式日线 |
| --- | --- | --- |
| 06:15 | 外围收盘：美股、日股、港股、VIX、美债与新闻 | 否 |
| 10:05 | 开盘脉搏：指数、成交额、涨跌家数 | 否 |
| 11:35 | 午间脉搏：上午收束状态 | 否 |
| 15:10 | 收盘快照：完整行情、情绪和行业排行 | 是 |
| 20:20 | 夜间校验：复核收盘数据与数据源健康 | 是 |

GitHub Actions 可能有数分钟调度延迟。休市日不会伪造行情，只刷新状态和审计日志。

## 数据与复用

```text
data/YYYY.csv          # 日线与收盘情绪，适合回测
data/pulses/YYYY-MM.csv # 日内四段观察，适合研究盘中演化
data/sectors.csv        # 行业领涨/领跌 Top 5
data/global.json         # 全球指数、A50、汇率、美元、黄金、原油、VIX 与美债
data/analysis.json       # 可解释风险温度、新闻与研究观察
data/scorecard.json      # 真实运行信号的前向验证成绩单
data/signals/YYYY.csv    # 每次风险信号的可审计原始记录
data/latest.json        # 程序最方便消费的聚合入口
data/status.json        # 最近任务与数据源健康状态
```

本地运行不需要安装依赖：

```bash
python3 scripts/snapshot.py
python3 scripts/global_context.py
python3 scripts/scorecard.py
python3 scripts/share_card.py
python3 scripts/chart.py
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
```

想拥有自己的市场心电图，直接用模板生成仓库并开启 Actions 即可。更多字段说明见 [数据字典](docs/DATA_SCHEMA.md)。

## 数据来源与边界

指数行情来自腾讯行情公开接口；市场宽度、涨跌停池和行业排行来自东方财富公开接口。接口异常时保留上一份有效数据，并在 `status.json` 明确标记，不把空响应冒充成功。

全球指数来自腾讯公开行情，A50、离岸人民币、美元指数、黄金与原油来自新浪财经公开行情，宏观压力来自 FRED；新闻区只保留Google News RSS 的标题、来源和链接，不抓取或改写正文。

指数历史由 [scripts/backfill.py](scripts/backfill.py) 一次性回填。涨跌家数、涨停跌停、连板梯队这些是盘后快照，没有历史接口可回填，只能逐日累积，所以回填日期的这几列是空的。

> 本项目仅用于数据记录与技术研究，不构成投资建议。公开接口可能调整，请以交易所和数据服务商正式口径为准。

---

如果它帮你省下了整理行情的时间，欢迎点一个 ⭐。想一起完善信号、数据源或可视化，可以先到 [讨论区](https://github.com/ychenfen/a-share-daily/discussions) 交流，或从 [贡献指南](CONTRIBUTING.md) 开始。
