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
> **⚪ 休市 / 未开盘** · 目标日未开市或尚未产生行情，最近交易日 2026-09-22 · 最后检查 `2026-09-23 08:31`（北京时间）

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

> **风险温度 -3 · 中性等待**（置信度：中）
> 多空线索接近平衡，等待价格、宽度或宏观压力出现更清晰方向。

| 市场 | 地区 | 收盘 | 涨跌幅 |
| --- | --- | ---: | ---: |
| 标普 500 | 美国 | 7764.64 | +0.00% |
| 纳斯达克 | 美国 | 27244.28 | +0.45% |
| 道琼斯 | 美国 | 51863.69 | -0.36% |
| 恒生指数 | 中国香港 | 25087.75 | +0.18% |
| 欧洲股票 ETF | 欧洲（美股代理） | 89.43 | +0.21% |
| 日经 225 | 日本 | 65018.95 | +1.38% |

### 跨资产先行带

> A50 与美元/人民币组合仅作低权重评分；黄金和原油只提供风险背景，不直接加减分。

| 资产 | 角色 | 最新值 | 涨跌幅 | 状态 |
| --- | --- | ---: | ---: | --- |
| 富时中国 A50 期货 | 低权重计分 | 14,703.88 | +0.34% | 最新 |
| 美元兑离岸人民币 | 低权重计分 | 6.6964 | -0.03% | 最新 |
| 美元指数 | 低权重计分 | 100.56 | +0.03% | 最新 |
| COMEX 黄金 | 背景观察 | 4,397.94 | +0.49% | 最新 |
| WTI 原油 | 背景观察 | 89.90 | -0.68% | 最新 |

> ⚠️ 数据降级：全球指数、VIX、美债10Y本轮未完全刷新，已尽量保留最近有效值。

### 风险温度拆解

| 信号 | 当前值 | 分数贡献 | 解释 |
| --- | --- | ---: | --- |
| A股动量 | 上证 +0.06% | +0.5 | 反映本地市场价格强弱 |
| 市场宽度 | 涨 2391 / 跌 3077 | -2.5 | 上涨家数占优时提高风险偏好 |
| 短线情绪 | 涨停 63 / 跌停 3 / 炸板率 22.2% | +7.2 | 涨停扩散加分，炸板率过高扣分 |
| 外围股市 | 6 个市场均值 +0.31% | +2.2 | 衡量隔夜风险偏好共振 |
| A50 先行 | 富时 A50 +0.34% | +2.0 | 离岸期货只作低权重先行确认，避免重复计算 A 股现货动量 |
| 美元与人民币 | USD/CNH 6.6964 (-0.03%) / DXY 100.56 (+0.03%) | +0.3 | 美元走弱与人民币走强通常缓解外部流动性压力 |
| 波动压力 | VIX 15.44 | +0.0 | VIX 越高，全球避险需求通常越强 |
| 利率压力 | 美债 10Y 4.94% | -5.0 | 长端利率偏高时压制高估值资产 |
| 新闻语气 | 正向词 4 / 风险词 8 | -8.0 | 标题关键词只做低权重提示，不代替事实核验 |

### 事件传导链

> 去重标题只作为待验证线索；分类数量不是已确认事件，传导链也不直接参与评分。

| 事件线索 | 宏观传导 | A 股映射 | 观察指标 | 失效条件 |
| --- | --- | --- | --- | --- |
| 央行与利率（5 条） | 政策利率预期 → 美债收益率与美元 → 全球流动性 | 高估值成长、券商、地产与人民币敏感资产 | 美债10Y 4.94%（最近有效值） / 美元指数 100.56 / +0.03%（最新） / USD/CNH 6.6964 / -0.03%（最新） | 失效条件：若美债利率、美元与人民币没有同向确认，标题冲击可能只是短期噪音。 |
| 地缘与贸易（1 条） | 地缘风险 → 油金与波动率 → 通胀预期和风险偏好 | 黄金、能源、军工、航运与出口链风险敞口 | VIX 15.44（最近有效值） / 黄金 4,397.94 / +0.49%（最新） / 原油 89.90 / -0.68%（最新） | 失效条件：若 VIX、黄金和原油没有共振，事件尚未形成可交易的跨资产冲击。 |
| 商品与成本（1 条） | 商品价格 → 输入成本与通胀预期 → 企业利润分配 | 能源、化工、有色、航空运输与中下游成本敏感行业 | 原油 89.90 / -0.68%（最新） / 黄金 4,397.94 / +0.49%（最新） / 美债10Y 4.94%（最近有效值） | 失效条件：若现货代理价格未确认标题方向，暂不推断产业链利润迁移。 |
| 美元与人民币（1 条） | 美元与人民币 → 跨境流动性及进口成本 → 外资风险偏好 | 外资敏感权重、航空造纸、出口链与离岸中国资产 | 美元指数 100.56 / +0.03%（最新） / USD/CNH 6.6964 / -0.03%（最新） / 富时A50 14,703.88 / +0.34%（最新） | 失效条件：若 DXY 与 USD/CNH 背离，不能把单一汇率波动解释成统一资金方向。 |

### 研究观察

- 减少方向性预判，优先记录关键阈值被突破后的跟随信号。

### 新闻雷达

- [德银宏观策略师最新警告：全球重回同步加息周期，市场或低估加息幅度](https://news.google.com/rss/articles/CBMiiwFBVV95cUxPVEd2a3A2ejNZUGU1Rkg4Rl9IazBHSXNURHVGMmhsazVhWVBSdEhkUGJjVWhzNTI5RWhjazNxUkpnLTRuX3VZZ3JCd3JqVXN4a1haQkljZGdtQWZ0bDlpSXB4ajFVSTNWdkgtdURkNmJWT2ZUbng2QXpSSUxJcXV2Q2tNd1J6VEVoUmFn?oc=5) · 新浪财经
- [三大央行同步调升利率：美元持续走强，非美货币分化几何？](https://news.google.com/rss/articles/CBMitgFBVV95cUxOSTE3Qzh3bE5OTkgwVlBvcW1IMWc5UTFxdlpEVF9ubEwzU1NvbjRSOGFJd1A1eUZzS2ZTX21ZYjZBMVJmTUZzQk40ZUQ1VnFmMWRjbFpfUndIdGVVVVpTOUpjaW5WSXlVR21OVzQyU3BneXZvRXRXdWdiU3BxajEyZzVHUjRFaEZndGFmOUlUbFBZOERrZXNFUmNhU28zTlQ3MmM1LV9idDBYajhpRWNCbHY3SVRSQQ?oc=5) · Moomoo
- [超级央行周落地：中东点燃全球加息潮，中国为何成“例外”？](https://news.google.com/rss/articles/CBMic0FVX3lxTE1OcFYyankzdEJ3VVdEQjcydzZUajR1Z05rdnRYTEV5a1RtSERKLW43WUEyUVNYQi1kSzNoVEZhRjdXMktHSTlTcUhoOU9HRUtuX010RkhSNGxmRVZheTdGTFhITF82dElMeU1hcExtWVNFbkU?oc=5) · 中华网财经
- [金金乐道·把握市场脉搏∣多资产观点：A股震荡偏多，黄金原油中性](https://news.google.com/rss/articles/CBMickFVX3lxTFBUOFM0emxXZlRJeUN2UDY4TUVocDVPeEFvbmN0bVZxUDM0WnRKU2l6WjNkbDQ1REh6ZktQZW1RUGJBOU9meHQ3eVMxeWtLTUlzWmlxbEc4RUdZdUJMTTdJMTFUZHhya09QWHhOblIwSFBMdw?oc=5) · 手机新浪网
- [资产配置报告丨加息靴子落地，市场风险偏好或修复](https://news.google.com/rss/articles/CBMibkFVX3lxTE9pUEpuclRXd2I2c3lRZVRCdlJLQkZmUzNuRzA1akM5WEJWdmdudnBBSFlLVDlocmFTczEyRk5jWk9oS1FfUF83QVMtcHotRkFCLV9FTXBGYm93dl85NEQ3dzFtZGFBaVZMUHNldmNB?oc=5) · 新浪财经
- [Crypto Stock and Sector Sentiment Barometer丨Strategy boosts its BTC holdings again after two weeks; listed companies’ net BTC purchases reach $183 million; Bitmine has increased its ETH holdings for 68 consecutive weeks (Sept. 22)](https://news.google.com/rss/articles/CBMiZEFVX3lxTE9ERXg5cFY1ZGxuMlVjYUZxdzRsSktobTkxZFNpTkNUZG5JRndMcUtYRzhrYlZSSkpOV29BbnZFRmdzSS0tengyVi1aMjJ3aUVnMzNPcmIzRWdKVFdUeFVwZXE3Ni0?oc=5) · Binance

方法：透明规则评分：A股动量、市场宽度、短线情绪、外围股市、A50先行、美元与人民币、VIX、美债10Y和新闻标题低权重语气；黄金与原油只作背景，事件传导链不直接计分。

> 这是可审计的通用市场研究提示，不是个性化仓位或买卖建议。

## 信号成绩单

![风险信号前向验证](charts/signal_scorecard.svg)

> 1 日方向命中率 **100.0%**，当前有效样本 **15** 条。

方法：开盘/午间信号验证当日收盘，收盘/夜间信号验证下一交易日；同时持续结算 3 日和 5 日复合收益。

> 样本不足时不输出稳定性结论，历史表现也不代表未来收益。

## 走势

![近一年 A 股涨跌日历](charts/market_calendar.svg)

![上证指数](charts/sh000001.svg)

![创业板指](charts/sz399006.svg)

## 最近 10 个交易日

| 日期 | 上证 | 深成 | 创业板 | 沪深300 | 科创50 | 成交额(亿) | 涨/跌/平 | 涨停 | 跌停 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-09-22 | 3952.13<br>+0.06% | 13723.74<br>-0.05% | 3399.93<br>+0.01% | 4544.59<br>+0.11% | 1665.04<br>+0.46% | 21356 | 2391/3077/163 | 63 | 3 |
| 2026-09-21 | 3949.91<br>+0.97% | 13730.02<br>+0.65% | 3399.59<br>+0.80% | 4539.57<br>+0.71% | 1657.48<br>+0.29% | 20315 | 4583/951/96 | 103 | 2 |
| 2026-09-18 | 3911.87<br>+0.94% | 13640.87<br>+1.72% | 3372.68<br>+2.25% | 4507.39<br>+1.06% | 1652.63<br>+2.88% | 20771 | 4277/1173/180 | 78 | 0 |
| 2026-09-17 | 3875.60<br>-0.41% | 13409.91<br>-0.33% | 3298.31<br>-0.40% | 4460.16<br>-0.45% | 1606.29<br>-0.61% | 18231 | -/-/- | - | - |
| 2026-09-16 | 3891.60<br>+0.71% | 13454.74<br>+1.26% | 3311.47<br>+1.96% | 4480.27<br>+0.68% | 1616.19<br>+4.14% | 18391 | -/-/- | - | - |
| 2026-09-15 | 3864.28<br>-0.54% | 13287.97<br>-0.72% | 3247.92<br>-1.15% | 4450.04<br>-0.67% | 1551.96<br>+1.55% | 16127 | -/-/- | - | - |
| 2026-09-14 | 3885.33<br>-0.07% | 13384.57<br>-0.64% | 3285.58<br>-1.10% | 4480.08<br>-0.67% | 1528.27<br>-1.62% | 16292 | -/-/- | - | - |
| 2026-09-11 | 3888.11<br>-1.18% | 13471.26<br>-1.08% | 3322.04<br>-0.49% | 4510.16<br>-0.84% | 1553.39<br>-1.01% | 19719 | -/-/- | - | - |
| 2026-09-10 | 3934.40<br>-0.43% | 13617.67<br>-0.77% | 3338.42<br>-0.49% | 4548.39<br>-0.53% | 1569.22<br>-0.69% | 16472 | -/-/- | - | - |
| 2026-09-09 | 3951.51<br>+0.28% | 13723.32<br>+0.15% | 3354.97<br>-0.14% | 4572.60<br>+0.30% | 1580.06<br>-0.69% | 18556 | -/-/- | - | - |

完整历史在 [data/](data/) 目录，共 661 个交易日。

## 市场情绪

最新交易日 2026-09-22：

- 涨停 **63** 家，跌停 **3** 家
- 炸板 18 家，炸板率 **22.2%**（越高说明封板越不牢）
- 最高 **9** 连板，2 板及以上共 27 家

| 日期 | 涨停 | 跌停 | 炸板 | 炸板率 | 最高连板 | 连板家数 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-09-22 | 63 | 3 | 18 | 22.2% | 9 | 27 |
| 2026-09-21 | 103 | 2 | 25 | 19.5% | 17 | 31 |
| 2026-09-18 | 78 | 0 | 25 | 24.3% | 16 | 18 |

## 行业板块

2026-09-22 领涨与领跌各五个：

| | 行业 | 涨跌幅 | 主力净流入(亿) | 领涨股 |
| --- | --- | --- | --- | --- |
| 领涨 | 燃料电池 | +10.78% | 0.29 | 亿华通-U |
|  | 其他家电Ⅲ | +5.00% | 0.18 | 奥佳华 |
|  | 其他家电Ⅱ | +5.00% | 0.18 | 奥佳华 |
|  | 广告媒体 | +4.20% | -0.29 | 华媒控股 |
|  | 教育出版 | +3.77% | 1.19 | 新华文轩 |
| 领跌 | 涂料 | -5.79% | -0.10 | 三棵树 |
|  | 橡胶助剂 | -2.82% | -1.30 | 阳谷华泰 |
|  | 旅游综合 | -2.62% | -0.54 | 锦旅Ｂ股 |
|  | 快递 | -2.51% | -1.44 | 顺丰控股 |
|  | 航运 | -2.38% | -6.24 | 海科B |

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
