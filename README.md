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
> **⚪ 休市 / 未开盘** · 目标日未开市或尚未产生行情，最近交易日 2026-09-30 · 最后检查 `2026-10-03 15:55`（北京时间）

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

> **风险温度 +7 · 谨慎偏多**（置信度：中）
> 风险偏好略占优，但信号并未形成全面共振。

| 市场 | 地区 | 收盘 | 涨跌幅 |
| --- | --- | ---: | ---: |
| 标普 500 | 美国 | 7722.72 | +0.73% |
| 纳斯达克 | 美国 | 27190.86 | +1.19% |
| 道琼斯 | 美国 | 51176.96 | +0.49% |
| 恒生指数 | 中国香港 | 23972.29 | -2.60% |
| 欧洲股票 ETF | 欧洲（美股代理） | 86.38 | +1.04% |
| 日经 225 | 日本 | 65018.95 | +1.38% |

### 跨资产先行带

> A50 与美元/人民币组合仅作低权重评分；黄金和原油只提供风险背景，不直接加减分。

| 资产 | 角色 | 最新值 | 涨跌幅 | 状态 |
| --- | --- | ---: | ---: | --- |
| 富时中国 A50 期货 | 低权重计分 | 13,832.53 | +0.16% | 最新 |
| 美元兑离岸人民币 | 低权重计分 | 6.7061 | -0.11% | 最新 |
| 美元指数 | 低权重计分 | 101.93 | -0.09% | 最新 |
| COMEX 黄金 | 背景观察 | 4,170.09 | -0.77% | 最新 |
| WTI 原油 | 背景观察 | 91.50 | -1.48% | 最新 |

> ⚠️ 数据降级：全球指数、VIX、美债10Y本轮未完全刷新，已尽量保留最近有效值。

### 风险温度拆解

| 信号 | 当前值 | 分数贡献 | 解释 |
| --- | --- | ---: | --- |
| A股动量 | 上证 +0.31% | +2.5 | 反映本地市场价格强弱 |
| 市场宽度 | 涨 2614 / 跌 2841 | -0.8 | 上涨家数占优时提高风险偏好 |
| 短线情绪 | 涨停 52 / 跌停 9 / 炸板率 18.8% | +4.8 | 涨停扩散加分，炸板率过高扣分 |
| 外围股市 | 6 个市场均值 +0.37% | +2.6 | 衡量隔夜风险偏好共振 |
| A50 先行 | 富时 A50 +0.16% | +1.0 | 离岸期货只作低权重先行确认，避免重复计算 A 股现货动量 |
| 美元与人民币 | USD/CNH 6.7061 (-0.11%) / DXY 101.93 (-0.09%) | +1.8 | 美元走弱与人民币走强通常缓解外部流动性压力 |
| 波动压力 | VIX 15.44 | +0.0 | VIX 越高，全球避险需求通常越强 |
| 利率压力 | 美债 10Y 4.94% | -5.0 | 长端利率偏高时压制高估值资产 |
| 新闻语气 | 正向词 3 / 风险词 3 | +0.0 | 标题关键词只做低权重提示，不代替事实核验 |

### 事件传导链

> 去重标题只作为待验证线索；分类数量不是已确认事件，传导链也不直接参与评分。

| 事件线索 | 宏观传导 | A 股映射 | 观察指标 | 失效条件 |
| --- | --- | --- | --- | --- |
| 央行与利率（4 条） | 政策利率预期 → 美债收益率与美元 → 全球流动性 | 高估值成长、券商、地产与人民币敏感资产 | 美债10Y 4.94%（最近有效值） / 美元指数 101.93 / -0.09%（最新） / USD/CNH 6.7061 / -0.11%（最新） | 失效条件：若美债利率、美元与人民币没有同向确认，标题冲击可能只是短期噪音。 |
| 通胀与就业（2 条） | 通胀与就业数据 → 降息路径与实际利率 → 估值折现率 | 成长估值、可选消费、资源品与利率敏感板块 | 美债10Y 4.94%（最近有效值） / 美元指数 101.93 / -0.09%（最新） / 纳斯达克 27,190.86 / +1.19%（最新） | 失效条件：若实际利率与美元反向运行，单条数据不应直接外推为持续风格切换。 |
| 科技与产业（1 条） | 科技盈利与估值 → 全球成长风格 → 风险偏好扩散 | 半导体、算力、通信与其他高估值成长方向 | 纳斯达克 27,190.86 / +1.19%（最新） / 富时A50 13,832.53 / +0.16%（最新） / 美债10Y 4.94%（最近有效值） | 失效条件：若纳指走弱、A50 不确认或长端利率继续上行，主题热度不等于趋势。 |
| 商品与成本（1 条） | 商品价格 → 输入成本与通胀预期 → 企业利润分配 | 能源、化工、有色、航空运输与中下游成本敏感行业 | 原油 91.50 / -1.48%（最新） / 黄金 4,170.09 / -0.77%（最新） / 美债10Y 4.94%（最近有效值） | 失效条件：若现货代理价格未确认标题方向，暂不推断产业链利润迁移。 |

### 研究观察

- 保留进攻观察清单，同时以市场宽度和外围指数是否续强作为确认条件。

### 新闻雷达

- [五穷六绝？“华尔街最准分析师”盘点6月全球市场“雷区”](https://news.google.com/rss/articles/CBMiSEFVX3lxTFBkQ3JhOE1oanM5RFlIRlRLQzg0NDdNUk9WandkOEotb05LUDA4N2JoVWhRWFRwdEpKSFJ5QTJneVc4Wjc5aEdnZw?oc=5) · 财联社
- [A股节后上涨胜率超60% 机构：持股过节或更合算！外围股市上涨 股民盼着开门红](https://news.google.com/rss/articles/CBMimAFBVV95cUxQTzJiZ0U0dUlDd0U1V0l5dXBlN2tCMmpQMmQ3V0pBdmJQN0R0elZBMEhPc2FCVnJmUlhPdk8zMWhyY1ZOZmczc05STWZCMUZFVGhFVkNtTjVtd0ZEUVZITHVJR0h6SnNoM2t2Sl9uTHE4YmpfNkdYUk80a3hHQ0tyV29Od0lKaDRfYktSOU5JZENFMTI0OWxXRA?oc=5) · finance.sina.com.cn
- [疲弱就业数据缓解加息担忧，美股反弹但市场广度继续恶化](https://news.google.com/rss/articles/CBMiWkFVX3lxTFBBV1B6MU43eVpscGNQblpvQThoNGhhVXRiUEx1Q2xzR3BGSmpUdjc0elB5VXFnMXVJSnRrS1FPYzFobXB4azBpWW0tb3NyNUlfNHUxdndnSTFBZw?oc=5) · 加美财经
- [下周前瞻：美联储纪要与服务业PMI重磅来袭](https://news.google.com/rss/articles/CBMipwFBVV95cUxOOHFEM1AwOE1vRTNBVjVlVUZYLW9OSjFMSjhndk5xd3hrVGdOdFp5Zk15dDVZZWpURlhMdXJrVGJYYUhucXlCUS1SV0prUGdTRE5GZVM2QmlvakFwSGJLNzR1am9WaXJLYWtWbjlQSUNDTGF1eklnTmZtdVJDR2xWRnJEZWlnYTUyM2liYm4yeGczbmxpa2dpeDBOa1hsQ2RNeWdFUVFKaw?oc=5) · Moomoo
- [纳指、英伟达齐创新高，AI算力与科技主题上演大反攻！非农仅增2.9万+油价下行，美联储加息押注大降温](https://news.google.com/rss/articles/CBMikwFBVV95cUxNcG9CNGVfLUkwSjg2Y3k3QjB1TVA0RTRNX3dsU2pfZ21DQ2c0WkpIdlBxd0pMZVB0dllpUUwtbGtUNmhoUFI0ZDgybmxoNFJublBvdkFuS0hQWXY1emV4dUZVOVBMY1FZX2NJZ3QzaDhVQlM0aEhkcEdaSG1hTExzdURGdllzZHVFenZLdUpYMU05YVk?oc=5) · 富途牛牛
- [全球央行艰难重启加息周期，这次有什么不同](https://news.google.com/rss/articles/CBMiggFBVV95cUxQdjJ3ZHZlOWFyd1dwdl9yOUkwc2ppWk9WZnI1Skd5RDhLNXN1Q3VQYVpsdzl5UUJQMlhfWFUtQlg5ODJXWEQ5YlF4WlRfNG4zZXRhRnFvZm13MnlBeU9yNWNsRVA5amFuZDBKckZWTXp1OVhCc05QQjQ2OHNDVUtIRmFB?oc=5) · finance.sina.com.cn

方法：透明规则评分：A股动量、市场宽度、短线情绪、外围股市、A50先行、美元与人民币、VIX、美债10Y和新闻标题低权重语气；黄金与原油只作背景，事件传导链不直接计分。

> 这是可审计的通用市场研究提示，不是个性化仓位或买卖建议。

## 信号成绩单

![风险信号前向验证](charts/signal_scorecard.svg)

> 1 日方向命中率 **84.6%**，当前有效样本 **52** 条。

方法：开盘/午间信号验证当日收盘，收盘/夜间信号验证下一交易日；同时持续结算 3 日和 5 日复合收益。

> 样本不足时不输出稳定性结论，历史表现也不代表未来收益。

## 走势

![近一年 A 股涨跌日历](charts/market_calendar.svg)

![上证指数](charts/sh000001.svg)

![创业板指](charts/sz399006.svg)

## 最近 10 个交易日

| 日期 | 上证 | 深成 | 创业板 | 沪深300 | 科创50 | 成交额(亿) | 涨/跌/平 | 涨停 | 跌停 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-09-30 | 3842.19<br>+0.31% | 12887.62<br>-0.11% | 3135.28<br>-0.23% | 4357.62<br>+0.29% | 1530.01<br>-2.51% | 14380 | 2614/2841/183 | 52 | 9 |
| 2026-09-29 | 3830.45<br>+0.18% | 12901.95<br>+0.34% | 3142.56<br>+0.09% | 4345.21<br>+0.10% | 1569.34<br>+0.86% | 14092 | 3525/1944/167 | 57 | 10 |
| 2026-09-28 | 3823.62<br>-1.67% | 12858.75<br>-3.44% | 3139.82<br>-4.53% | 4340.76<br>-2.22% | 1555.98<br>-4.06% | 17028 | 910/4607/117 | 33 | 56 |
| 2026-09-24 | 3888.37<br>-1.22% | 13316.97<br>-2.34% | 3288.95<br>-2.68% | 4439.14<br>-1.73% | 1621.87<br>-2.35% | 16534 | 1134/4352/148 | 52 | 13 |
| 2026-09-23 | 3936.52<br>-0.39% | 13636.07<br>-0.64% | 3379.61<br>-0.60% | 4517.28<br>-0.60% | 1660.85<br>-0.25% | 17650 | 1910/3605/118 | 51 | 13 |
| 2026-09-22 | 3952.13<br>+0.06% | 13723.74<br>-0.05% | 3399.93<br>+0.01% | 4544.59<br>+0.11% | 1665.04<br>+0.46% | 21356 | 2391/3077/163 | 63 | 3 |
| 2026-09-21 | 3949.91<br>+0.97% | 13730.02<br>+0.65% | 3399.59<br>+0.80% | 4539.57<br>+0.71% | 1657.48<br>+0.29% | 20315 | 4583/951/96 | 103 | 2 |
| 2026-09-18 | 3911.87<br>+0.94% | 13640.87<br>+1.72% | 3372.68<br>+2.25% | 4507.39<br>+1.06% | 1652.63<br>+2.88% | 20771 | 4277/1173/180 | 78 | 0 |
| 2026-09-17 | 3875.60<br>-0.41% | 13409.91<br>-0.33% | 3298.31<br>-0.40% | 4460.16<br>-0.45% | 1606.29<br>-0.61% | 18231 | -/-/- | - | - |
| 2026-09-16 | 3891.60<br>+0.71% | 13454.74<br>+1.26% | 3311.47<br>+1.96% | 4480.27<br>+0.68% | 1616.19<br>+4.14% | 18391 | -/-/- | - | - |

完整历史在 [data/](data/) 目录，共 666 个交易日。

## 市场情绪

最新交易日 2026-09-30：

- 涨停 **52** 家，跌停 **9** 家
- 炸板 12 家，炸板率 **18.8%**（越高说明封板越不牢）
- 最高 **9** 连板，2 板及以上共 16 家

| 日期 | 涨停 | 跌停 | 炸板 | 炸板率 | 最高连板 | 连板家数 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-09-30 | 52 | 9 | 12 | 18.8% | 9 | 16 |
| 2026-09-29 | 57 | 10 | 8 | 12.3% | 13 | 18 |
| 2026-09-28 | 33 | 56 | 11 | 25.0% | 12 | 10 |
| 2026-09-24 | 52 | 13 | 10 | 16.1% | 7 | 19 |
| 2026-09-23 | 51 | 13 | 26 | 33.8% | 9 | 14 |
| 2026-09-22 | 63 | 3 | 18 | 22.2% | 9 | 27 |
| 2026-09-21 | 103 | 2 | 25 | 19.5% | 17 | 31 |
| 2026-09-18 | 78 | 0 | 25 | 24.3% | 16 | 18 |

## 行业板块

2026-09-29 领涨与领跌各五个：

| | 行业 | 涨跌幅 | 主力净流入(亿) | 领涨股 |
| --- | --- | --- | --- | --- |
| 领涨 | 燃料电池 | +7.73% | 0.15 | 亿华通-U |
|  | 锂电专用设备 | +7.17% | 7.65 | 尚水智能 |
|  | 文字媒体 | +6.77% | 1.20 | 掌阅科技 |
|  | 视频媒体 | +5.54% | 1.37 | 芒果超媒 |
|  | 印制电路板 | +5.43% | 29.51 | 依顿电子 |
| 领跌 | 其他医疗服务 | -2.84% | -1.66 | 润达医疗 |
|  | 运动服装 | -2.53% | -0.51 | 探路者 |
|  | 其他养殖 | -2.41% | -0.30 | 华英农业 |
|  | 炼油化工 | -2.32% | -3.14 | ST沈化 |
|  | 林业Ⅱ | -2.25% | -0.68 | 永安林业 |

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
