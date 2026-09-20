# 数据字典

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
| `slot` | `open`、`midday`、`close` 或 `night` |

开盘与午间时段只抓取指数、成交额和涨跌家数；涨跌停池和行业排行只在收盘与
夜间校验时请求，以降低公开接口压力。

## `data/sectors.csv`

每个有效交易日保存行业领涨和领跌各 5 行。`rank_type` 为 `up` 或 `down`，
`net_inflow_yi` 为主力净流入亿元数。

## `data/latest.json`

聚合最新日线、最近一次 pulse、行业排行和任务状态。顶层包含
`schema_version`；消费者应先检查该值，目前版本为 `1`。

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
