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
> **🟢 盘中** · 外围收盘已更新 · 最后检查 `2026-11-11 09:55`（北京时间）

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

> **风险温度 +16 · 谨慎偏多**（置信度：中）
> 风险偏好略占优，但信号并未形成全面共振。

| 市场 | 地区 | 收盘 | 涨跌幅 |
| --- | --- | ---: | ---: |
| 标普 500 | 美国 | 7520.93 | -0.38% |
| 纳斯达克 | 美国 | 25065.87 | -0.74% |
| 道琼斯 | 美国 | 52231.89 | -0.30% |
| 恒生指数 | 中国香港 | 24389.38 | -0.68% |
| 欧洲股票 ETF | 欧洲（美股代理） | 89.65 | -0.38% |
| 日经 225 | 日本 | 65018.95 | +1.38% |

### 跨资产先行带

> A50 与美元/人民币组合仅作低权重评分；黄金和原油只提供风险背景，不直接加减分。

| 资产 | 角色 | 最新值 | 涨跌幅 | 状态 |
| --- | --- | ---: | ---: | --- |
| 富时中国 A50 期货 | 低权重计分 | 12,885.40 | -0.24% | 最新 |
| 美元兑离岸人民币 | 低权重计分 | 6.6735 | -0.05% | 最新 |
| 美元指数 | 低权重计分 | 102.22 | -0.04% | 最新 |
| COMEX 黄金 | 背景观察 | 4,053.13 | +0.57% | 最新 |
| WTI 原油 | 背景观察 | 86.25 | +0.24% | 最新 |

> ⚠️ 数据降级：全球指数、VIX、美债10Y、新闻本轮未完全刷新，已尽量保留最近有效值。

### 风险温度拆解

| 信号 | 当前值 | 分数贡献 | 解释 |
| --- | --- | ---: | --- |
| A股动量 | 上证 +0.08% | +0.6 | 反映本地市场价格强弱 |
| 市场宽度 | 涨 4305 / 跌 1177 | +11.4 | 上涨家数占优时提高风险偏好 |
| 短线情绪 | 涨停 93 / 跌停 0 / 炸板率 17.0% | +13.4 | 涨停扩散加分，炸板率过高扣分 |
| 外围股市 | 6 个市场均值 -0.18% | -1.3 | 衡量隔夜风险偏好共振 |
| A50 先行 | 富时 A50 -0.24% | -1.5 | 离岸期货只作低权重先行确认，避免重复计算 A 股现货动量 |
| 美元与人民币 | USD/CNH 6.6735 (-0.05%) / DXY 102.22 (-0.04%) | +0.7 | 美元走弱与人民币走强通常缓解外部流动性压力 |
| 波动压力 | VIX 15.44 | +0.0 | VIX 越高，全球避险需求通常越强 |
| 利率压力 | 美债 10Y 4.94% | -5.0 | 长端利率偏高时压制高估值资产 |
| 新闻语气 | 正向词 1 / 风险词 2 | -2.0 | 标题关键词只做低权重提示，不代替事实核验 |

### 事件传导链

> 去重标题只作为待验证线索；分类数量不是已确认事件，传导链也不直接参与评分。

| 事件线索 | 宏观传导 | A 股映射 | 观察指标 | 失效条件 |
| --- | --- | --- | --- | --- |
| 商品与成本（3 条） | 商品价格 → 输入成本与通胀预期 → 企业利润分配 | 能源、化工、有色、航空运输与中下游成本敏感行业 | 原油 86.25 / +0.24%（最新） / 黄金 4,053.13 / +0.57%（最新） / 美债10Y 4.94%（最近有效值） | 失效条件：若现货代理价格未确认标题方向，暂不推断产业链利润迁移。 |
| 央行与利率（2 条） | 政策利率预期 → 美债收益率与美元 → 全球流动性 | 高估值成长、券商、地产与人民币敏感资产 | 美债10Y 4.94%（最近有效值） / 美元指数 102.22 / -0.04%（最新） / USD/CNH 6.6735 / -0.05%（最新） | 失效条件：若美债利率、美元与人民币没有同向确认，标题冲击可能只是短期噪音。 |
| 通胀与就业（2 条） | 通胀与就业数据 → 降息路径与实际利率 → 估值折现率 | 成长估值、可选消费、资源品与利率敏感板块 | 美债10Y 4.94%（最近有效值） / 美元指数 102.22 / -0.04%（最新） / 纳斯达克 25,065.87 / -0.74%（最新） | 失效条件：若实际利率与美元反向运行，单条数据不应直接外推为持续风格切换。 |
| 美元与人民币（2 条） | 美元与人民币 → 跨境流动性及进口成本 → 外资风险偏好 | 外资敏感权重、航空造纸、出口链与离岸中国资产 | 美元指数 102.22 / -0.04%（最新） / USD/CNH 6.6735 / -0.05%（最新） / 富时A50 12,885.40 / -0.24%（最新） | 失效条件：若 DXY 与 USD/CNH 背离，不能把单一汇率波动解释成统一资金方向。 |
| 科技与产业（1 条） | 科技盈利与估值 → 全球成长风格 → 风险偏好扩散 | 半导体、算力、通信与其他高估值成长方向 | 纳斯达克 25,065.87 / -0.74%（最新） / 富时A50 12,885.40 / -0.24%（最新） / 美债10Y 4.94%（最近有效值） | 失效条件：若纳指走弱、A50 不确认或长端利率继续上行，主题热度不等于趋势。 |

### 研究观察

- 保留进攻观察清单，同时以市场宽度和外围指数是否续强作为确认条件。

### 新闻雷达

- [海外研选日报1110 \| 瑞银：美联储料再加息两次 但难以终结美股上涨行情](https://news.google.com/rss/articles/CBMiSEFVX3lxTFAxcXc5MEZrMUF1QmE1UUh2MjZiRllRT3VtVDA1eUw2SHRzX1VScDJaYzR2WUZoZFJBTDFrRDhuTEM1NHkyWm9oTw?oc=5) · 财联社
- [鹰派日本央行与鹰派美联储，日元的方向听谁的？](https://news.google.com/rss/articles/CBMiogFBVV95cUxOc0NxUDN1R3pVNzFMNm5rMVRXRnhjMG1xcUFSZFJtODU2TEhnRHZ3QnZmY2JZWF8zb3Q0R3ljajVUUnZKSU10RWl1UmZLeDMxXzBqQ212YU9jVGhtTTVRWVFFWHJmajBQYlA2VU5wOExaYlpqOF8ydElKUU40TUp0amJOUURxMGUwYU5PZ0dzb0xpeWhUU2drYVdKa09DVk9kWUE?oc=5) · Moomoo
- [费半大涨近7%+油价降温，AI算力反攻“再闯一关”：今晚CPI数据成试金石](https://news.google.com/rss/articles/CBMiYkFVX3lxTE9yZmk4OTh0d3NZWlFkazkyci03RGZjNlN2UW1QM0xCOV9ldTVzUXFHX2dNSWxZdnpoUGQwTTZPS2NFeUt0bTY3SFdwVDZMakhWTXVqc1JsN1g4dENRSDRSb0t3?oc=5) · 同花顺
- [一夜暴涨6.85%！美股芯片股狂欢，道指狂飙1100点，英伟达却独自蒸发1.28万亿](https://news.google.com/rss/articles/CBMiZkFVX3lxTE9TZ1QwVnp3c1g5VVJlN25iZUdGbGdnWTFRTTNJdFN1NklyWXFMOWVnMDlKWWlpMlJjTnVwWGRRcVVIaEZmdjF6dUF4QkxaOEVBTndKNTdjUVVWSndzd3Q1ZXBMdUhjUQ?oc=5) · 金融界
- [全球市场迎“通胀大考”！美元、黄金、美股与比特币关键位一览](https://news.google.com/rss/articles/CBMihAFBVV95cUxOZGFYWkx5TnpQV2pfTndHMUF1RlRzR3p4bkw1YTFvYTYzUlRHUGVrMjZPU05kWHM1MlFwaFg4clVpRU5sTm1zemRYbFJxejk2VExFcFV4dnN2RzBlNXlvYUFrRWVldFp0aHQ1b0x0LXNQdDZfOEY5eXp6ZzlqMFVENEFTWEU?oc=5) · FX168财经
- [黄金冲上4100美元后，真正的考验才开始？两股力量正激烈对撞](https://news.google.com/rss/articles/CBMibEFVX3lxTE0wdkNrOHpBSnBoa0xFOFN1ajJOVlY2bjNLbGN5OG1CSlA5TlhRdVlWQ2hFVi1FRDhVajRlaDBUOThkSWNtcjdpdkZZS3lpMk9ZV2dNSTNmTkxyMWlHNEx1V2FwZFZxNkEta3BocA?oc=5) · FX168财经

方法：透明规则评分：A股动量、市场宽度、短线情绪、外围股市、A50先行、美元与人民币、VIX、美债10Y和新闻标题低权重语气；黄金与原油只作背景，事件传导链不直接计分。

> 这是可审计的通用市场研究提示，不是个性化仓位或买卖建议。

## 信号成绩单

![风险信号前向验证](charts/signal_scorecard.svg)

> 1 日方向命中率 **57.8%**，当前有效样本 **218** 条。

方法：开盘/午间信号验证当日收盘，收盘/夜间信号验证下一交易日；同时持续结算 3 日和 5 日复合收益。

> 样本不足时不输出稳定性结论，历史表现也不代表未来收益。

## 走势

![近一年 A 股涨跌日历](charts/market_calendar.svg)

![上证指数](charts/sh000001.svg)

![创业板指](charts/sz399006.svg)

## 最近 10 个交易日

| 日期 | 上证 | 深成 | 创业板 | 沪深300 | 科创50 | 成交额(亿) | 涨/跌/平 | 涨停 | 跌停 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-10 | 3663.72<br>+0.08% | 11241.54<br>+0.86% | 2494.40<br>+1.46% | 4059.11<br>+0.07% | 1265.02<br>+0.64% | 15048 | 4305/1177/168 | 93 | 0 |
| 2026-11-06 | 3649.18<br>-1.10% | 11175.78<br>-2.57% | 2465.23<br>-3.96% | 4054.28<br>-1.44% | 1253.20<br>-2.60% | 16578 | 767/4793/90 | 32 | 15 |
| 2026-11-05 | 3689.91<br>+0.10% | 11471.09<br>+1.19% | 2566.80<br>+0.87% | 4113.41<br>+0.29% | 1286.68<br>+1.68% | 21180 | -/-/- | 84 | 0 |
| 2026-11-04 | 3686.17<br>+2.16% | 11335.69<br>+4.22% | 2544.73<br>+6.40% | 4101.34<br>+2.31% | 1265.47<br>+9.92% | 20377 | 4732/786/131 | 118 | 10 |
| 2026-11-03 | 3608.10<br>-0.82% | 10876.99<br>-1.21% | 2391.65<br>-2.73% | 4008.87<br>-0.20% | 1151.28<br>-3.81% | 17034 | 2152/3329/166 | 48 | 17 |
| 2026-10-30 | 3599.02<br>-1.44% | 10833.78<br>-2.73% | 2413.63<br>-4.13% | 3985.50<br>-1.39% | 1160.84<br>-5.48% | 16745 | 919/4642/87 | 47 | 82 |
| 2026-10-29 | 3651.43<br>-0.82% | 11138.20<br>-2.92% | 2517.59<br>-4.45% | 4041.84<br>-1.03% | 1228.09<br>-4.27% | 15565 | 789/4795/63 | 39 | 41 |
| 2026-10-28 | 3681.47<br>+0.91% | 11473.18<br>+2.02% | 2634.76<br>+3.40% | 4083.87<br>+0.85% | 1282.93<br>+2.45% | 16285 | 4189/1270/188 | 72 | 5 |
| 2026-10-27 | 3648.30<br>-1.33% | 11245.73<br>-2.50% | 2548.15<br>-3.41% | 4049.55<br>-1.32% | 1252.28<br>-4.81% | 14610 | 624/4974/49 | 41 | 22 |
| 2026-10-26 | 3697.52<br>+0.19% | 11534.38<br>-1.19% | 2638.23<br>-1.71% | 4103.54<br>-0.04% | 1315.50<br>-2.23% | 16088 | 2280/3199/168 | 55 | 26 |

完整历史在 [data/](data/) 目录，共 687 个交易日。

## 市场情绪

最新交易日 2026-11-10：

- 涨停 **93** 家，跌停 **0** 家
- 炸板 19 家，炸板率 **17.0%**（越高说明封板越不牢）
- 最高 **15** 连板，2 板及以上共 33 家

| 日期 | 涨停 | 跌停 | 炸板 | 炸板率 | 最高连板 | 连板家数 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-10 | 93 | 0 | 19 | 17.0% | 15 | 33 |
| 2026-11-06 | 32 | 15 | 14 | 30.4% | 13 | 15 |
| 2026-11-05 | 84 | 0 | 48 | 36.4% | 12 | 28 |
| 2026-11-04 | 118 | 10 | 33 | 21.9% | 8 | 22 |
| 2026-11-03 | 48 | 17 | 34 | 41.5% | 18 | 19 |
| 2026-10-30 | 47 | 82 | 31 | 39.7% | 8 | 11 |
| 2026-10-29 | 39 | 41 | 25 | 39.1% | 7 | 12 |
| 2026-10-28 | 72 | 5 | 69 | 48.9% | 14 | 12 |
| 2026-10-27 | 41 | 22 | 28 | 40.6% | 8 | 17 |
| 2026-10-26 | 55 | 26 | 23 | 29.5% | 12 | 18 |

## 行业板块

2026-11-10 领涨与领跌各五个：

| | 行业 | 涨跌幅 | 主力净流入(亿) | 领涨股 |
| --- | --- | --- | --- | --- |
| 领涨 | 其他数字媒体 | +9.80% | 2.23 | 风语筑 |
|  | 文字媒体 | +9.03% | 10.63 | 掌阅科技 |
|  | 影视动漫制作 | +8.03% | 14.22 | 慈文传媒 |
|  | 影视院线 | +7.05% | 14.65 | 慈文传媒 |
|  | 其他黑色家电 | +6.42% | 1.08 | 创维数字 |
| 领跌 | 钾肥 | -2.04% | 0.72 | 藏格矿业 |
|  | 民爆制品 | -2.02% | -3.39 | 金奥博 |
|  | 动力煤 | -1.80% | -5.09 | 郑州煤电 |
|  | 医美耗材 | -1.72% | -0.55 | 华熙生物 |
|  | 煤炭开采 | -1.56% | -5.65 | 郑州煤电 |

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
