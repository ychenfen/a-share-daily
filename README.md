<div align="center">

# 📈 A-Share Pulse

**把 GitHub 提交图变成 A 股市场心电图。**

每天五次联动全球收盘、A 股盘中与新闻风险；零依赖、可审计、可直接 Fork。

<a href="https://github.com/ychenfen/a-share-daily/actions/workflows/daily.yml"><img alt="A-share market pulse" src="https://github.com/ychenfen/a-share-daily/actions/workflows/daily.yml/badge.svg"></a>
<img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
<img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-zero-2ea44f">
<a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>

</div>

> [!NOTE]
> **⚪ 休市 / 未开盘** · 目标日未开市或尚未产生行情，最近交易日 2026-09-18 · 最后检查 `2026-09-20 09:01`（北京时间）

[最新 JSON](data/latest.json) · [运行状态](data/status.json) · [完整历史](data/) · [数据字典](docs/DATA_SCHEMA.md) · [自动任务](https://github.com/ychenfen/a-share-daily/actions)

## 为什么值得收藏

| 能力 | 你得到什么 |
| --- | --- |
| 🫀 五段市场脉搏 | 外围收盘 + A 股开盘、午间、收盘、夜间校验，不只是日终一个点 |
| 🧠 情绪温度计 | 涨跌家数、涨停/跌停、炸板率、最高连板和行业强弱 |
| 🟩 GitHub 风格日历 | 用红绿贡献格复刻近一年市场节奏，适合截图分享 |
| 🧾 Git 原生数据湖 | 每次变化都有 diff，可追溯、可回滚，CSV/JSON 直接用于研究 |
| 🪶 零第三方依赖 | 只用 Python 标准库和 GitHub Actions，Fork 后无需服务器 |
| 🛡️ 质量门禁 | 每次推送前跑回归测试、schema 和重复日期检查 |

## 全球市场与策略雷达

![全球市场与跨市场风险温度](charts/global_dashboard.svg)

> **风险温度 +17 · 谨慎偏多**（置信度：高）
> 风险偏好略占优，但信号并未形成全面共振。

| 市场 | 地区 | 收盘 | 涨跌幅 |
| --- | --- | ---: | ---: |
| 标普 500 | 美国 | 7650.50 | +0.17% |
| 纳斯达克 | 美国 | 26522.55 | +0.39% |
| 道琼斯 | 美国 | 51682.64 | -0.18% |
| 恒生指数 | 中国香港 | 24750.78 | +0.60% |
| 欧洲股票 ETF | 欧洲（美股代理） | 88.21 | -1.05% |
| 日经 225 | 日本 | 65018.95 | +1.38% |

### 风险温度拆解

| 信号 | 当前值 | 分数贡献 | 解释 |
| --- | --- | ---: | --- |
| A股动量 | 上证 +0.94% | +7.5 | 反映本地市场价格强弱 |
| 市场宽度 | 涨 4277 / 跌 1173 | +11.4 | 上涨家数占优时提高风险偏好 |
| 短线情绪 | 涨停 78 / 跌停 0 / 炸板率 24.3% | +10.0 | 涨停扩散加分，炸板率过高扣分 |
| 外围股市 | 6 个市场均值 +0.22% | +1.5 | 衡量隔夜风险偏好共振 |
| 波动压力 | VIX 15.44 | +0.0 | VIX 越高，全球避险需求通常越强 |
| 利率压力 | 美债 10Y 4.94% | -5.0 | 长端利率偏高时压制高估值资产 |
| 新闻语气 | 正向词 3 / 风险词 7 | -8.0 | 标题关键词只做低权重提示，不代替事实核验 |

### 研究观察

- 保留进攻观察清单，同时以市场宽度和外围指数是否续强作为确认条件。

### 新闻雷达

- [盘后观察：放量普涨！沪指重回3900点，日韩股市同涨——加息落地后A股开启“补涨”行情？](https://news.google.com/rss/articles/CBMickFVX3lxTE1MeFRyS0NYQUtPdkVUX2J4WGFxUEl4V0pMVVF0RlVyNjRUcUNxTVhPYzhtRHBGUmllaS1QWElLNGhhdFpNemNMTUdCOXBzYlRyTk1iUmNoQ0t2LXFha0dLXzdSRnlDS0tjNGVNZG1KVjVYZw?oc=5) · 手机新浪网
- [【直击亚市】今晚摊牌！美联储加息概率超90%，小心美元事后走弱](https://news.google.com/rss/articles/CBMieEFVX3lxTE0xNzB3V0ZsTVRSU2xWMlNIbHBrN21FUnNrTVhtejVPUEx1cHIxOTJSUUJMNFlkRUlCM1BjeXJ4QXpPeWVzYWZtQTk3cWpVeFBYaVEyQkJGbXBjT0tNNHdySWNleTZyZU5vRnZSQjlFOWlVbS1ZYTdDaA?oc=5) · FX168财经
- [加息潮来临，每年1万亿美元AI投资直面高利率大考；特朗普称美国将获得对格陵兰岛安全“永久控制权”；Anthropic拟将IPO推迟至11月；LVMH被曝曾秘密收购爱马仕继承人股份\| 一周国际财经](https://news.google.com/rss/articles/CBMiZkFVX3lxTE1lZWV0RER6TF9nTWNiU3pIMmNIbHhLNFFnbk5GRDN2QkF0bEtVeVZ5MWNUejhsdUZxRFJ6ZXp6ZVd4em8zbV9jUDE3clVqN2lWc25EUHpsVjBBMC04UWQ5SUd6cldRUQ?oc=5) · 每日经济新闻
- [中信证券：美欧日加息落地，关注什么？\|美联储\|美国\|债券\|流动性\|现金流](https://news.google.com/rss/articles/CBMitAFBVV95cUxPbllhN3k4b2Vzd29nR3d4d3R0dlk4dDhMOFBTVTRDWVRjbnBnUE5xQkF4M0wtZ1Z4cWVJQ1FmaEp6a19fNHJlQVVub3hxODA5VFptZkJXZXZYVHRwcFVjSHFzTERyWEQ3NFJXWXFTLUx3TTd5anFaM3dVeDVsMHc4a0o3bXJNZlhUNkk1S2JrOXNGWjhEWk9hX0R2eGFhWGN5VU93ODNIWWFVcV85aUxZYW52X1k?oc=5) · 新浪财经
- [全球牛市要结束了吗 三大央行同步紧缩引发关注](https://news.google.com/rss/articles/CBMicEFVX3lxTFBwN0VPSjA3Vmc4ci1VYVFQaUNQRGpqNnU5WEo2QlVJNFk2cF9kOTdaUG82NE1qSDc1VktFVmtwVVI3YVNaNTMwSzhnQjBkM3AzbmxRamwyTmlQN2ViaGtLYlpud2hzbHFyNjRQZGJYRG8?oc=5) · 中华网
- [精读超级央行周：中东点燃全球加息潮，中国为何逆势走完全不同的路？](https://news.google.com/rss/articles/CBMiY0FVX3lxTE1qbk5HajF5UXh1WkQ3TmtaNF9VQ29VYUdGdUxZdW5yeTBOV1EzM0Jjdm5RZkJQNnRyc3lYYnNoUHF2dkpzbERubXF6Sk1uS3FtalhSbE5MbWNmTjAtYjJ5ZFg0QQ?oc=5) · 潮起网

方法：透明规则评分：A股动量、市场宽度、短线情绪、外围股市、VIX、美债10Y和新闻标题低权重语气。

> 这是可审计的通用市场研究提示，不是个性化仓位或买卖建议。

## 走势

![近一年 A 股涨跌日历](charts/market_calendar.svg)

![上证指数](charts/sh000001.svg)

![创业板指](charts/sz399006.svg)

## 最近 10 个交易日

| 日期 | 上证 | 深成 | 创业板 | 沪深300 | 科创50 | 成交额(亿) | 涨/跌/平 | 涨停 | 跌停 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-09-18 | 3911.87<br>+0.94% | 13640.87<br>+1.72% | 3372.68<br>+2.25% | 4507.39<br>+1.06% | 1652.63<br>+2.88% | 20771 | 4277/1173/180 | 78 | 0 |
| 2026-09-17 | 3875.60<br>-0.41% | 13409.91<br>-0.33% | 3298.31<br>-0.40% | 4460.16<br>-0.45% | 1606.29<br>-0.61% | 18231 | -/-/- | - | - |
| 2026-09-16 | 3891.60<br>+0.71% | 13454.74<br>+1.26% | 3311.47<br>+1.96% | 4480.27<br>+0.68% | 1616.19<br>+4.14% | 18391 | -/-/- | - | - |
| 2026-09-15 | 3864.28<br>-0.54% | 13287.97<br>-0.72% | 3247.92<br>-1.15% | 4450.04<br>-0.67% | 1551.96<br>+1.55% | 16127 | -/-/- | - | - |
| 2026-09-14 | 3885.33<br>-0.07% | 13384.57<br>-0.64% | 3285.58<br>-1.10% | 4480.08<br>-0.67% | 1528.27<br>-1.62% | 16292 | -/-/- | - | - |
| 2026-09-11 | 3888.11<br>-1.18% | 13471.26<br>-1.08% | 3322.04<br>-0.49% | 4510.16<br>-0.84% | 1553.39<br>-1.01% | 19719 | -/-/- | - | - |
| 2026-09-10 | 3934.40<br>-0.43% | 13617.67<br>-0.77% | 3338.42<br>-0.49% | 4548.39<br>-0.53% | 1569.22<br>-0.69% | 16472 | -/-/- | - | - |
| 2026-09-09 | 3951.51<br>+0.28% | 13723.32<br>+0.15% | 3354.97<br>-0.14% | 4572.60<br>+0.30% | 1580.06<br>-0.69% | 18556 | -/-/- | - | - |
| 2026-09-08 | 3940.55<br>+0.20% | 13703.21<br>-0.52% | 3359.72<br>-1.15% | 4558.74<br>-0.36% | 1591.00<br>-1.52% | 19603 | -/-/- | - | - |
| 2026-09-07 | 3932.70<br>+0.07% | 13774.91<br>+1.91% | 3398.68<br>+3.41% | 4575.02<br>+0.59% | 1615.53<br>+2.42% | 19460 | -/-/- | - | - |

完整历史在 [data/](data/) 目录，共 659 个交易日。

## 市场情绪

最新交易日 2026-09-18：

- 涨停 **78** 家，跌停 **0** 家
- 炸板 25 家，炸板率 **24.3%**（越高说明封板越不牢）
- 最高 **16** 连板，2 板及以上共 18 家

## 行业板块

2026-09-18 领涨与领跌各五个：

| | 行业 | 涨跌幅 | 主力净流入(亿) | 领涨股 |
| --- | --- | --- | --- | --- |
| 领涨 | 其他医疗服务 | +6.72% | 1.97 | 南华生物 |
|  | 房产租赁经纪 | +4.86% | 1.00 | 世联行 |
|  | 半导体设备 | +4.83% | 18.20 | 托伦斯 |
|  | 数字芯片设计 | +4.68% | 75.35 | 诚邦股份 |
|  | 集成电路制造 | +4.59% | 12.40 | 盛合晶微 |
| 领跌 | 其他养殖 | -3.47% | -0.16 | *ST福成 |
|  | 种子 | -1.52% | -2.04 | 敦煌种业 |
|  | 涂料 | -1.51% | -0.10 | 三棵树 |
|  | 汽车经销商 | -1.49% | -0.01 | 上海物贸 |
|  | 汽车服务 | -1.11% | -0.07 | 阿尔特 |

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
data/global.json         # 美股、日股、港股、VIX 与美债
data/analysis.json       # 可解释风险温度、新闻与研究观察
data/latest.json        # 程序最方便消费的聚合入口
data/status.json        # 最近任务与数据源健康状态
```

本地运行不需要安装依赖：

```bash
python3 scripts/snapshot.py
python3 scripts/global_context.py
python3 scripts/chart.py
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
```

想拥有自己的市场心电图，直接 Fork 并开启 Actions 即可。更多字段说明见 [数据字典](docs/DATA_SCHEMA.md)。

## 数据来源与边界

指数行情来自腾讯行情公开接口；市场宽度、涨跌停池和行业排行来自东方财富公开接口。接口异常时保留上一份有效数据，并在 `status.json` 明确标记，不把空响应冒充成功。

全球指数来自腾讯公开行情与 FRED，宏观压力来自 FRED；新闻区只保留Google News RSS 的标题、来源和链接，不抓取或改写正文。

指数历史由 [scripts/backfill.py](scripts/backfill.py) 一次性回填。涨跌家数、涨停跌停、连板梯队这些是盘后快照，没有历史接口可回填，只能逐日累积，所以回填日期的这几列是空的。

> 本项目仅用于数据记录与技术研究，不构成投资建议。公开接口可能调整，请以交易所和数据服务商正式口径为准。

---

如果它帮你省下了整理行情的时间，欢迎点一个 ⭐，也欢迎提交新的公开数据源适配。
