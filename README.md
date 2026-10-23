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
> **⚪ 休市 / 未开盘** · 目标日未开市或尚未产生行情，最近交易日 2026-10-23 · 最后检查 `2026-10-24 01:16`（北京时间）

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

> **风险温度 +19 · 谨慎偏多**（置信度：中）
> 风险偏好略占优，但信号并未形成全面共振。

| 市场 | 地区 | 收盘 | 涨跌幅 |
| --- | --- | ---: | ---: |
| 标普 500 | 美国 | 7625.76 | -0.49% |
| 纳斯达克 | 美国 | 25974.80 | -0.13% |
| 道琼斯 | 美国 | 52219.86 | -1.23% |
| 恒生指数 | 中国香港 | 23093.37 | +0.69% |
| 欧洲股票 ETF | 欧洲（美股代理） | 86.13 | -0.78% |
| 日经 225 | 日本 | 65018.95 | +1.38% |

### 跨资产先行带

> A50 与美元/人民币组合仅作低权重评分；黄金和原油只提供风险背景，不直接加减分。

| 资产 | 角色 | 最新值 | 涨跌幅 | 状态 |
| --- | --- | ---: | ---: | --- |
| 富时中国 A50 期货 | 低权重计分 | 12,992.00 | -0.36% | 最新 |
| 美元兑离岸人民币 | 低权重计分 | 6.6703 | -0.02% | 最新 |
| 美元指数 | 低权重计分 | 101.83 | +0.20% | 最新 |
| COMEX 黄金 | 背景观察 | 4,006.49 | -1.33% | 最新 |
| WTI 原油 | 背景观察 | 102.94 | +3.48% | 最新 |

> ⚠️ 数据降级：全球指数、VIX、美债10Y本轮未完全刷新，已尽量保留最近有效值。

### 风险温度拆解

| 信号 | 当前值 | 分数贡献 | 解释 |
| --- | --- | ---: | --- |
| A股动量 | 上证 +0.89% | +7.1 | 反映本地市场价格强弱 |
| 市场宽度 | 涨 4568 / 跌 935 | +13.2 | 上涨家数占优时提高风险偏好 |
| 短线情绪 | 涨停 82 / 跌停 6 / 炸板率 12.8% | +11.1 | 涨停扩散加分，炸板率过高扣分 |
| 外围股市 | 6 个市场均值 -0.09% | -0.7 | 衡量隔夜风险偏好共振 |
| A50 先行 | 富时 A50 -0.36% | -2.2 | 离岸期货只作低权重先行确认，避免重复计算 A 股现货动量 |
| 美元与人民币 | USD/CNH 6.6703 (-0.02%) / DXY 101.83 (+0.20%) | -0.8 | 美元走弱与人民币走强通常缓解外部流动性压力 |
| 波动压力 | VIX 15.44 | +0.0 | VIX 越高，全球避险需求通常越强 |
| 利率压力 | 美债 10Y 4.94% | -5.0 | 长端利率偏高时压制高估值资产 |
| 新闻语气 | 正向词 1 / 风险词 3 | -4.0 | 标题关键词只做低权重提示，不代替事实核验 |

### 事件传导链

> 去重标题只作为待验证线索；分类数量不是已确认事件，传导链也不直接参与评分。

| 事件线索 | 宏观传导 | A 股映射 | 观察指标 | 失效条件 |
| --- | --- | --- | --- | --- |
| 美元与人民币（2 条） | 美元与人民币 → 跨境流动性及进口成本 → 外资风险偏好 | 外资敏感权重、航空造纸、出口链与离岸中国资产 | 美元指数 101.83 / +0.20%（最新） / USD/CNH 6.6703 / -0.02%（最新） / 富时A50 12,992.00 / -0.36%（最新） | 失效条件：若 DXY 与 USD/CNH 背离，不能把单一汇率波动解释成统一资金方向。 |
| 央行与利率（1 条） | 政策利率预期 → 美债收益率与美元 → 全球流动性 | 高估值成长、券商、地产与人民币敏感资产 | 美债10Y 4.94%（最近有效值） / 美元指数 101.83 / +0.20%（最新） / USD/CNH 6.6703 / -0.02%（最新） | 失效条件：若美债利率、美元与人民币没有同向确认，标题冲击可能只是短期噪音。 |
| 通胀与就业（1 条） | 通胀与就业数据 → 降息路径与实际利率 → 估值折现率 | 成长估值、可选消费、资源品与利率敏感板块 | 美债10Y 4.94%（最近有效值） / 美元指数 101.83 / +0.20%（最新） / 纳斯达克 25,974.80 / -0.13%（最新） | 失效条件：若实际利率与美元反向运行，单条数据不应直接外推为持续风格切换。 |
| 地缘与贸易（1 条） | 地缘风险 → 油金与波动率 → 通胀预期和风险偏好 | 黄金、能源、军工、航运与出口链风险敞口 | VIX 15.44（最近有效值） / 黄金 4,006.49 / -1.33%（最新） / 原油 102.94 / +3.48%（最新） | 失效条件：若 VIX、黄金和原油没有共振，事件尚未形成可交易的跨资产冲击。 |
| 科技与产业（1 条） | 科技盈利与估值 → 全球成长风格 → 风险偏好扩散 | 半导体、算力、通信与其他高估值成长方向 | 纳斯达克 25,974.80 / -0.13%（最新） / 富时A50 12,992.00 / -0.36%（最新） / 美债10Y 4.94%（最近有效值） | 失效条件：若纳指走弱、A50 不确认或长端利率继续上行，主题热度不等于趋势。 |
| 商品与成本（1 条） | 商品价格 → 输入成本与通胀预期 → 企业利润分配 | 能源、化工、有色、航空运输与中下游成本敏感行业 | 原油 102.94 / +3.48%（最新） / 黄金 4,006.49 / -1.33%（最新） / 美债10Y 4.94%（最近有效值） | 失效条件：若现货代理价格未确认标题方向，暂不推断产业链利润迁移。 |

### 研究观察

- 保留进攻观察清单，同时以市场宽度和外围指数是否续强作为确认条件。

### 新闻雷达

- [下周前瞻：超级央行周，通胀增长与地缘扰动接受检验](https://news.google.com/rss/articles/CBMiW0FVX3lxTE0xM0Y4SzRKWVpPSU5yYUllOXZ5Uk9oTzY4emREVkpnbmhGSWMzY3Y1VVdFM0VEblF1STNhRG9zZ1pHRG9Xa08xbXNWNDlpUlJ6b1VXRWhEcFNMUDg?oc=5) · 汇通财经
- [科技股试图喘口气 原油市场又传来压力 \| 今夜看点](https://news.google.com/rss/articles/CBMiqwFBVV95cUxNWUFjNFc5N2xCSEJzTjhhVFVVOGFHX09YYXJCYmVmMHFsZlp2TFBZZFB2NHBoeXJ1Ul9nLXh4YnJwdUJvbGZWMFpRSnc1bjlLdG5xMnlUbjh6NkNqZWdNMGFyYkhyelY1cy1mQ2ZxZ29CRUVQbFBPaWhDMFhYcjBwX2RRM2pudXdlaXlaOEdnNXZoLXZ6dHlqc3p3SHB2TnBIZmFnWmRvY1J5Qmc?oc=5) · Moomoo
- [交易时刻：BTC死守8.15万美元机构成本线，韩股现“白菜价”，A股史诗级大逆转](https://news.google.com/rss/articles/CBMif0FVX3lxTFA4d3FiNDUwQnNtZHl0OVZudENiRXBqQ29pSkRCVFlsMWVFZm1ERkJWMk4wMnpzMUh2RmszMTBHVG5ha2RFQVAwUjZ4MDF5eDR4SFpkSkdtRncwVDMxc1VQNEdjV00tLUF2VlpLRG1IU2lPdFBJeV9pZ0pFTjdiTUU?oc=5) · PANews
- [全球股市下挫，A股盘中破3600点，是风险释放？还是布局窗口？](https://news.google.com/rss/articles/CBMiUkFVX3lxTFBfVVhiX1ZWOW1rRWtQYTgyQ01uYXp6U2lkYWtKQldHMmVtU1FyUFJWZHdpYWhQVFRhMlBuTmM5Y2plSEF3clYyTmVheGdPdmdsSnc?oc=5) · 文轩新闻
- [\[周度外汇展望\] 美元/日元持续疲软＝受全球股市下跌影响](https://news.google.com/rss/articles/CBMi0gFBVV95cUxQY05JSmY4RWRzUEFycHY0LXMyWDl2bU1mYTdJSnp5cU5LZS1xbXdDQUo4TmRrOVV5MjNlQ1VkV3VMR1hoN3dwbjJCOGg5eklZZWxEREhQRkVJeU56MHdzQlIzNDZvX1lnbHNEeGJwaDhmQ2pldHJCZmxrX0tkSTBrVHhWS01iSGV3bF9sVHJxWmFqdW95YlVZU3pLTlFIY1lScVZYQ1g0UXBlTzNaN1FNcGVHdDJTSTBsbldVWFRkNXYzUVR6a2o3VU16SC1haGF6b3c?oc=5) · Moomoo

方法：透明规则评分：A股动量、市场宽度、短线情绪、外围股市、A50先行、美元与人民币、VIX、美债10Y和新闻标题低权重语气；黄金与原油只作背景，事件传导链不直接计分。

> 这是可审计的通用市场研究提示，不是个性化仓位或买卖建议。

## 信号成绩单

![风险信号前向验证](charts/signal_scorecard.svg)

> 1 日方向命中率 **59.4%**，当前有效样本 **133** 条。

方法：开盘/午间信号验证当日收盘，收盘/夜间信号验证下一交易日；同时持续结算 3 日和 5 日复合收益。

> 样本不足时不输出稳定性结论，历史表现也不代表未来收益。

## 走势

![近一年 A 股涨跌日历](charts/market_calendar.svg)

![上证指数](charts/sh000001.svg)

![创业板指](charts/sz399006.svg)

## 最近 10 个交易日

| 日期 | 上证 | 深成 | 创业板 | 沪深300 | 科创50 | 成交额(亿) | 涨/跌/平 | 涨停 | 跌停 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-23 | 3690.48<br>+0.89% | 11673.83<br>+2.79% | 2684.10<br>+4.16% | 4105.33<br>+1.71% | 1345.51<br>+3.04% | 19563 | 4568/935/146 | 82 | 6 |
| 2026-10-22 | 3658.03<br>-1.48% | 11357.32<br>-2.96% | 2576.90<br>-4.37% | 4036.30<br>-1.84% | 1305.87<br>-2.78% | 15287 | 537/5071/39 | 33 | 49 |
| 2026-10-21 | 3713.03<br>-0.60% | 11704.35<br>-0.82% | 2694.71<br>-1.62% | 4111.93<br>-0.97% | 1343.28<br>+0.06% | 14294 | 2007/3401/237 | 50 | 5 |
| 2026-10-20 | 3735.37<br>+0.12% | 11801.29<br>-0.14% | 2739.20<br>-0.26% | 4152.11<br>-0.54% | 1342.42<br>+1.00% | 14561 | 3801/1706/138 | 54 | 6 |
| 2026-10-19 | 3730.92<br>+0.39% | 11817.42<br>+0.13% | 2746.29<br>-0.94% | 4174.53<br>+0.09% | 1329.19<br>-2.17% | 14375 | 2302/3161/178 | 46 | 22 |
| 2026-10-16 | 3716.28<br>+0.24% | 11802.46<br>-0.12% | 2772.38<br>-0.39% | 4170.61<br>+0.11% | 1358.65<br>-0.06% | 15554 | 3351/2143/150 | 61 | 10 |
| 2026-10-15 | 3707.48<br>-1.59% | 11816.79<br>-2.43% | 2783.17<br>-2.92% | 4166.01<br>-1.23% | 1359.52<br>-1.50% | 16330 | 433/5174/35 | 36 | 26 |
| 2026-10-14 | 3767.23<br>-0.88% | 12110.59<br>-1.97% | 2866.76<br>-3.10% | 4217.68<br>-1.36% | 1380.26<br>-3.29% | 14144 | 998/4545/97 | 36 | 11 |
| 2026-10-13 | 3800.86<br>+0.10% | 12353.70<br>-0.25% | 2958.34<br>-0.18% | 4275.68<br>-0.29% | 1427.18<br>+0.03% | 16759 | 2938/2515/185 | 67 | 8 |
| 2026-10-09 | 3813.79<br>+0.05% | 12641.86<br>+0.17% | 3043.33<br>+0.22% | 4317.25<br>+0.16% | 1457.27<br>+0.07% | 19006 | 3347/2159/130 | 69 | 8 |

完整历史在 [data/](data/) 目录，共 677 个交易日。

## 市场情绪

最新交易日 2026-10-23：

- 涨停 **82** 家，跌停 **6** 家
- 炸板 12 家，炸板率 **12.8%**（越高说明封板越不牢）
- 最高 **16** 连板，2 板及以上共 20 家

| 日期 | 涨停 | 跌停 | 炸板 | 炸板率 | 最高连板 | 连板家数 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-10-23 | 82 | 6 | 12 | 12.8% | 16 | 20 |
| 2026-10-22 | 33 | 49 | 23 | 41.1% | 10 | 11 |
| 2026-10-21 | 50 | 5 | 19 | 27.5% | 13 | 22 |
| 2026-10-20 | 54 | 6 | 29 | 34.9% | 12 | 20 |
| 2026-10-19 | 46 | 22 | 21 | 31.3% | 21 | 14 |
| 2026-10-16 | 61 | 10 | 49 | 44.5% | 15 | 11 |
| 2026-10-15 | 36 | 26 | 7 | 16.3% | 19 | 14 |
| 2026-10-14 | 36 | 11 | 24 | 40.0% | 13 | 20 |
| 2026-10-13 | 67 | 8 | 19 | 22.1% | 17 | 13 |
| 2026-10-09 | 69 | 8 | 14 | 16.9% | 16 | 21 |

## 行业板块

2026-10-23 领涨与领跌各五个：

| | 行业 | 涨跌幅 | 主力净流入(亿) | 领涨股 |
| --- | --- | --- | --- | --- |
| 领涨 | 其他数字媒体 | +15.02% | 2.06 | 凡拓数创 |
|  | 机器人 | +7.98% | 10.88 | 派斯林 |
|  | 视频媒体 | +6.56% | -0.43 | 芒果超媒 |
|  | 横向通用软件 | +5.72% | 6.92 | 绿盟科技 |
|  | 医美服务 | +5.49% | 0.27 | 朗姿股份 |
| 领跌 | 国有大型银行Ⅲ | -2.75% | -14.61 | 邮储银行 |
|  | 食用菌 | -2.60% | -0.56 | 雪榕生物 |
|  | 水力发电 | -1.87% | -7.51 | 梅雁吉祥 |
|  | 油气及炼化工程 | -0.83% | -0.01 | 潜能恒信 |
|  | 其他石化 | -0.80% | -1.41 | 桐昆股份 |

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
