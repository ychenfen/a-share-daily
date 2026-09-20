# 数据字典

[English](DATA_SCHEMA.en.md) · 简体中文

仓库同时提供适合表格分析的 CSV 和适合程序消费的 JSON。金额统一使用亿元，
涨跌幅和炸板率使用百分数值（例如 `1.25` 表示 `1.25%`）。缺失值表示该字段在
历史回填时不可得，不代表数值为零。

## `data/YYYY.csv`

每个交易日一行，日期升序。同一天重复运行会覆盖旧行。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `date` | `YYYY-MM-DD` | 交易日 |
| `*_close` | number | 五大指数收盘点位 |
| `*_pct` | number | 五大指数当日涨跌幅（%） |
| `amount_yi` | number | 沪深两市成交额（亿元） |
| `up/down/flat` | integer | 沪深北上涨/下跌/平盘家数 |
| `limit_up/limit_down` | integer | 涨停/跌停家数 |
| `broken` | integer | 炸板家数 |
| `broken_rate` | number | `炸板 / (涨停 + 炸板) × 100` |
| `max_streak` | integer | 当日最高连板高度 |
| `streak_2plus` | integer | 2 板及以上股票数 |

## `data/pulses/YYYY-MM.csv`

盘中观察表。在日线字段前增加：

| 字段 | 说明 |
| --- | --- |
| `captured_at` | 北京时间 `YYYY-MM-DD HH:MM` |
| `slot` | `overnight`、`open`、`midday`、`close` 或 `night` |

开盘与午间时段只抓取指数、成交额和涨跌家数；涨跌停池和行业排行只在收盘与
夜间校验时请求，以降低公开接口压力。

## `data/sectors.csv`

每个有效交易日保存行业领涨和领跌各 5 行。`rank_type` 为 `up` 或 `down`，
`net_inflow_yi` 为主力净流入亿元数。

## `data/latest.json`

聚合最新日线、最近一次 pulse、行业排行和任务状态。顶层包含
`schema_version`；消费者应先检查该值，目前版本为 `1`。

## `data/global.json`

最近的跨市场快照：标普 500、纳斯达克、道琼斯、日经 225、恒生指数和欧洲
股票 ETF 代理，以及 FRED 的 VIX 与美国 10 年期国债收益率。`cross_assets`
另外记录富时中国 A50 期货、美元兑离岸人民币、美元指数、COMEX 黄金和 WTI
原油；前三者是有上限的评分证据，黄金与原油只作背景，不直接加减分。每个市场记录
`close`、`pct`、`previous_close` 和源端报价时间；代理品种会在 `kind` 和
`region` 中明确标注。`health` 记录各数据源是 `fresh`、`partial`、`stale`
还是 `missing`；上游临时失败时保留最近有效值，并通过 `stale` 显式标记。

## `data/analysis.json`

透明规则生成的跨市场风险温度，范围 `-100` 到 `+100`。组成项包括 A 股动量、
市场宽度、涨跌停情绪、外围市场均值、A50 先行、美元与人民币、VIX、美债 10Y
和低权重新闻标题语气。
`signals` 保留每项贡献，`advice` 是通用研究观察，不是个性化买卖指令。
`news` 是确定性去重后的标题线索；`events` 按央行利率、通胀就业、地缘贸易、
科技产业、商品成本、美元人民币和国内政策需求分类。每个事件簇包含
`macro_path`、`a_share_lens`、`watch`、`invalidation` 和最多两条标题例证。
`watch.state` 为 `fresh`、`stale` 或 `missing`。同一标题可以命中多个传导渠道；
分类数量不是已确认事件，事件链也不直接改变风险评分。

## `data/signals/YYYY.csv`

每次自动任务保存一条当时可见的风险信号，包括时段、评分、置信度、上证参考点、
外围均值、A50 涨跌幅、USD/CNH、美元指数、VIX、美债 10Y 和数据健康状态。记录按 `captured_at` 唯一且升序，
只保存真实运行结果，不使用事后信息回填信号。

## `data/scorecard.json`

信号的前向验证成绩单。开盘和午间信号以当日收盘为第一观察点，收盘和夜间信号
以下一交易日为第一观察点；同时结算 3 日、5 日复合收益。方向性样本未达到 20 条
时状态为 `collecting`，避免用极小样本宣传命中率。

## `data/status.json`

每次 Action 都会刷新。`market_state` 可能为：

- `live`：盘中 pulse 已更新；
- `closed`：正式日线已更新；
- `non_trading`：休市或目标日尚无行情；
- `unavailable`：数据源暂不可用，仓库保留上一份有效行情；
- `checking`：任务仍在检查中。

## 兼容性

历史年表可能缺少后来加入的情绪列，读取端应把缺失字段当作 `null`。新增字段
只追加在 CSV 尾部；JSON 的破坏性结构变化会提升 `schema_version`。
