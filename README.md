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
> **⚪ 休市 / 未开盘** · 目标日未开市或尚未产生行情，最近交易日 2026-10-22 · 最后检查 `2026-10-23 08:39`（北京时间）

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

> **风险温度 -47 · 防守优先**（置信度：中）
> 内部市场与外围压力形成负向共振，先控制暴露并等待风险指标回落。

| 市场 | 地区 | 收盘 | 涨跌幅 |
| --- | --- | ---: | ---: |
| 标普 500 | 美国 | 7663.43 | -1.21% |
| 纳斯达克 | 美国 | 26008.86 | -2.60% |
| 道琼斯 | 美国 | 52867.98 | +0.02% |
| 恒生指数 | 中国香港 | 22934.68 | -3.03% |
| 欧洲股票 ETF | 欧洲（美股代理） | 86.80 | -0.89% |
| 日经 225 | 日本 | 65018.95 | +1.38% |

### 跨资产先行带

> A50 与美元/人民币组合仅作低权重评分；黄金和原油只提供风险背景，不直接加减分。

| 资产 | 角色 | 最新值 | 涨跌幅 | 状态 |
| --- | --- | ---: | ---: | --- |
| 富时中国 A50 期货 | 低权重计分 | 12,934.01 | +0.03% | 最新 |
| 美元兑离岸人民币 | 低权重计分 | 6.6714 | -0.00% | 最新 |
| 美元指数 | 低权重计分 | 101.49 | -0.13% | 最新 |
| COMEX 黄金 | 背景观察 | 4,032.52 | -0.69% | 最新 |
| WTI 原油 | 背景观察 | 99.13 | -0.34% | 最新 |

> ⚠️ 数据降级：全球指数、VIX、美债10Y本轮未完全刷新，已尽量保留最近有效值。

### 风险温度拆解

| 信号 | 当前值 | 分数贡献 | 解释 |
| --- | --- | ---: | --- |
| A股动量 | 上证 -1.48% | -11.8 | 反映本地市场价格强弱 |
| 市场宽度 | 涨 537 / 跌 5071 | -16.2 | 上涨家数占优时提高风险偏好 |
| 短线情绪 | 涨停 33 / 跌停 49 / 炸板率 41.1% | -7.8 | 涨停扩散加分，炸板率过高扣分 |
| 外围股市 | 6 个市场均值 -1.06% | -7.4 | 衡量隔夜风险偏好共振 |
| A50 先行 | 富时 A50 +0.03% | +0.2 | 离岸期货只作低权重先行确认，避免重复计算 A 股现货动量 |
| 美元与人民币 | USD/CNH 6.6714 (-0.00%) / DXY 101.49 (-0.13%) | +0.7 | 美元走弱与人民币走强通常缓解外部流动性压力 |
| 波动压力 | VIX 15.44 | +0.0 | VIX 越高，全球避险需求通常越强 |
| 利率压力 | 美债 10Y 4.94% | -5.0 | 长端利率偏高时压制高估值资产 |
| 新闻语气 | 正向词 1 / 风险词 1 | +0.0 | 标题关键词只做低权重提示，不代替事实核验 |

### 事件传导链

> 去重标题只作为待验证线索；分类数量不是已确认事件，传导链也不直接参与评分。

| 事件线索 | 宏观传导 | A 股映射 | 观察指标 | 失效条件 |
| --- | --- | --- | --- | --- |
| 央行与利率（2 条） | 政策利率预期 → 美债收益率与美元 → 全球流动性 | 高估值成长、券商、地产与人民币敏感资产 | 美债10Y 4.94%（最近有效值） / 美元指数 101.49 / -0.13%（最新） / USD/CNH 6.6714 / -0.00%（最新） | 失效条件：若美债利率、美元与人民币没有同向确认，标题冲击可能只是短期噪音。 |
| 商品与成本（2 条） | 商品价格 → 输入成本与通胀预期 → 企业利润分配 | 能源、化工、有色、航空运输与中下游成本敏感行业 | 原油 99.13 / -0.34%（最新） / 黄金 4,032.52 / -0.69%（最新） / 美债10Y 4.94%（最近有效值） | 失效条件：若现货代理价格未确认标题方向，暂不推断产业链利润迁移。 |
| 美元与人民币（2 条） | 美元与人民币 → 跨境流动性及进口成本 → 外资风险偏好 | 外资敏感权重、航空造纸、出口链与离岸中国资产 | 美元指数 101.49 / -0.13%（最新） / USD/CNH 6.6714 / -0.00%（最新） / 富时A50 12,934.01 / +0.03%（最新） | 失效条件：若 DXY 与 USD/CNH 背离，不能把单一汇率波动解释成统一资金方向。 |

### 研究观察

- 研究上优先压力测试与回撤控制，避免仅凭单条利好逆势下注。

### 新闻雷达

- [安联投资：年底前美联储等多国央行将分别再加息0.25% 看好亚洲新兴股市及黄金](https://news.google.com/rss/articles/CBMivwFBVV95cUxOdk1CSlA0dkhqazlaMjJEQzhzbzhISnJCUS1WVFlLSFJ6MklaZXpTYXIydkxBZEw5WlducDN3ZjF3TDFsQnphRFdwS3ZwNEFERVVITmpwWWxnODJISDViTHo4TV9TNlU4OWtLeV8xblZqNXV1QXZNYjQxellxU3N2Z0ktdkxPcHR3V0lHVmF4UDFDMmxscjFScjNIRHhDU0Y4NlU1aDJWUzRqeEJDSmJzeExvaHJCb1ZONno4NDBUbw?oc=5) · Moomoo
- [油价狂飙，全球买单! 原油再度上破110美元，从食品到房贷全面承压 港美股资讯](https://news.google.com/rss/articles/CBMiYkFVX3lxTE9ZY2E5YWw0UlNBNnYtaEJhSC1kSXJKb1o3NXpzNXMxV3F0SjVNOGZ5eG1WWllmQ2ZubVIzZDBKNWxLWWo4Nl9ueHpQOE5OWWJYZjc4ZGptVzZISy1jV25vRmdn?oc=5) · 华盛通
- [美日利差与日本央行谨慎立场拉锯，美元兑日元维持区间震荡](https://news.google.com/rss/articles/CBMikwFBVV95cUxNTkJucTlSdmZyekwxN24zcDNMRXhySEVLSDQ1OWVCanM4SFA4LW5hWHprWG4wM3p4YUs1ZGx2LVoxTjJUMVlnRTlISkNhNUVPRy10VUhTSnFnQjltQjBnUUZrel9TMlJqNVl3SE85aGdCSVhxWk1VR3puRzd2UDhYZU9kaVV0eVpfWUh3MmJQaWpGU1k?oc=5) · 富途牛牛
- [隔夜美股上涨 亚股早盘个别发展](https://news.google.com/rss/articles/CBMi9gFBVV95cUxQT3NCc1NQTFYxYmk1UnpwMmJVcm1FOGNYZUk3bUVEQjh1eGMtUHRwbXloaGozakVYVkk3RThOWjBiRHVSNkVTa25CeEtpNXdET2xUXzlLaTNOV3lseEJXdkt0VTBQNTM5YmEwbDlub0hiMThtTnI0Qmd2eWRDX2Vkd1pFaWJMTmFJUTBrdVNETWVDbmpzSGxyZ051Q21sZ3dtTE45TC1FeEZKajVPTlBqdFBodDU5N1FSTS1Da1FaX1k1NkxCcTRobjhQMkdLVVROZXpoVERpVlRpeFdueFZRTklOTTJSaHRYVGw2SXEzTmVJbHNqTEE?oc=5) · 亚洲电视新闻

方法：透明规则评分：A股动量、市场宽度、短线情绪、外围股市、A50先行、美元与人民币、VIX、美债10Y和新闻标题低权重语气；黄金与原油只作背景，事件传导链不直接计分。

> 这是可审计的通用市场研究提示，不是个性化仓位或买卖建议。

## 信号成绩单

![风险信号前向验证](charts/signal_scorecard.svg)

> 1 日方向命中率 **61.7%**，当前有效样本 **128** 条。

方法：开盘/午间信号验证当日收盘，收盘/夜间信号验证下一交易日；同时持续结算 3 日和 5 日复合收益。

> 样本不足时不输出稳定性结论，历史表现也不代表未来收益。

## 走势

![近一年 A 股涨跌日历](charts/market_calendar.svg)

![上证指数](charts/sh000001.svg)

![创业板指](charts/sz399006.svg)

## 最近 10 个交易日

| 日期 | 上证 | 深成 | 创业板 | 沪深300 | 科创50 | 成交额(亿) | 涨/跌/平 | 涨停 | 跌停 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-22 | 3658.03<br>-1.48% | 11357.32<br>-2.96% | 2576.90<br>-4.37% | 4036.30<br>-1.84% | 1305.87<br>-2.78% | 15287 | 537/5071/39 | 33 | 49 |
| 2026-10-21 | 3713.03<br>-0.60% | 11704.35<br>-0.82% | 2694.71<br>-1.62% | 4111.93<br>-0.97% | 1343.28<br>+0.06% | 14294 | 2007/3401/237 | 50 | 5 |
| 2026-10-20 | 3735.37<br>+0.12% | 11801.29<br>-0.14% | 2739.20<br>-0.26% | 4152.11<br>-0.54% | 1342.42<br>+1.00% | 14561 | 3801/1706/138 | 54 | 6 |
| 2026-10-19 | 3730.92<br>+0.39% | 11817.42<br>+0.13% | 2746.29<br>-0.94% | 4174.53<br>+0.09% | 1329.19<br>-2.17% | 14375 | 2302/3161/178 | 46 | 22 |
| 2026-10-16 | 3716.28<br>+0.24% | 11802.46<br>-0.12% | 2772.38<br>-0.39% | 4170.61<br>+0.11% | 1358.65<br>-0.06% | 15554 | 3351/2143/150 | 61 | 10 |
| 2026-10-15 | 3707.48<br>-1.59% | 11816.79<br>-2.43% | 2783.17<br>-2.92% | 4166.01<br>-1.23% | 1359.52<br>-1.50% | 16330 | 433/5174/35 | 36 | 26 |
| 2026-10-14 | 3767.23<br>-0.88% | 12110.59<br>-1.97% | 2866.76<br>-3.10% | 4217.68<br>-1.36% | 1380.26<br>-3.29% | 14144 | 998/4545/97 | 36 | 11 |
| 2026-10-13 | 3800.86<br>+0.10% | 12353.70<br>-0.25% | 2958.34<br>-0.18% | 4275.68<br>-0.29% | 1427.18<br>+0.03% | 16759 | 2938/2515/185 | 67 | 8 |
| 2026-10-09 | 3813.79<br>+0.05% | 12641.86<br>+0.17% | 3043.33<br>+0.22% | 4317.25<br>+0.16% | 1457.27<br>+0.07% | 19006 | 3347/2159/130 | 69 | 8 |
| 2026-10-08 | 3811.90<br>-0.79% | 12620.90<br>-2.07% | 3036.66<br>-3.15% | 4310.28<br>-1.09% | 1456.32<br>-4.82% | 16821 | 1718/3798/118 | 43 | 13 |

完整历史在 [data/](data/) 目录，共 676 个交易日。

## 市场情绪

最新交易日 2026-10-22：

- 涨停 **33** 家，跌停 **49** 家
- 炸板 23 家，炸板率 **41.1%**（越高说明封板越不牢）
- 最高 **10** 连板，2 板及以上共 11 家

| 日期 | 涨停 | 跌停 | 炸板 | 炸板率 | 最高连板 | 连板家数 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-10-22 | 33 | 49 | 23 | 41.1% | 10 | 11 |
| 2026-10-21 | 50 | 5 | 19 | 27.5% | 13 | 22 |
| 2026-10-20 | 54 | 6 | 29 | 34.9% | 12 | 20 |
| 2026-10-19 | 46 | 22 | 21 | 31.3% | 21 | 14 |
| 2026-10-16 | 61 | 10 | 49 | 44.5% | 15 | 11 |
| 2026-10-15 | 36 | 26 | 7 | 16.3% | 19 | 14 |
| 2026-10-14 | 36 | 11 | 24 | 40.0% | 13 | 20 |
| 2026-10-13 | 67 | 8 | 19 | 22.1% | 17 | 13 |
| 2026-10-09 | 69 | 8 | 14 | 16.9% | 16 | 21 |
| 2026-10-08 | 43 | 13 | 32 | 42.7% | 8 | 10 |

## 行业板块

2026-10-22 领涨与领跌各五个：

| | 行业 | 涨跌幅 | 主力净流入(亿) | 领涨股 |
| --- | --- | --- | --- | --- |
| 领涨 | 电机Ⅲ | +4.13% | 10.94 | 兆威机电 |
|  | 电机Ⅱ | +4.13% | 10.94 | 兆威机电 |
|  | 医美耗材 | +2.35% | 0.63 | 锦波生物 |
|  | 医疗美容 | +1.71% | 0.60 | 锦波生物 |
|  | 电信运营商 | +1.18% | -1.79 | 中国移动 |
| 领跌 | 文字媒体 | -7.15% | -2.64 | 中文在线 |
|  | 影视动漫制作 | -6.58% | -7.41 | 中国电影 |
|  | 影视院线 | -6.55% | -7.75 | 中国电影 |
|  | 广告媒体 | -6.52% | -0.77 | 分众传媒 |
|  | 院线 | -6.46% | -0.35 | 儒意电影 |

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
