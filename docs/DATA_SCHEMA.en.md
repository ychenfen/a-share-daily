# Data Schema

[简体中文](DATA_SCHEMA.md) · English

The repository exposes CSV files for spreadsheet and research workflows, plus
JSON files for programmatic consumers. Monetary values use CNY 100 million
unless noted otherwise. Percentage fields are percentage points: `1.25` means
`1.25%`, not `0.0125`. A missing value means the field was unavailable from the
historical or live source; it must not be interpreted as zero.

## `data/YYYY.csv`

One row per trading session, sorted by date. Re-running the same session
replaces that date instead of creating a duplicate.

| Field | Type | Meaning |
| --- | --- | --- |
| `date` | `YYYY-MM-DD` | Trading date |
| `*_close` | number | Close for each of the five tracked A-share indices |
| `*_pct` | number | Daily percentage change for each index |
| `amount_yi` | number | Combined Shanghai and Shenzhen turnover, in CNY 100 million |
| `up/down/flat` | integer | Advancing, declining, and unchanged listings across Shanghai, Shenzhen, and Beijing |
| `limit_up/limit_down` | integer | Limit-up and limit-down counts |
| `broken` | integer | Failed limit-up attempts |
| `broken_rate` | number | `broken / (limit_up + broken) × 100` |
| `max_streak` | integer | Highest consecutive limit-up streak |
| `streak_2plus` | integer | Listings with a streak of at least two sessions |

## `data/pulses/YYYY-MM.csv`

Intraday observations. These files prepend two fields to the daily columns:

| Field | Meaning |
| --- | --- |
| `captured_at` | Beijing time as `YYYY-MM-DD HH:MM` |
| `slot` | `overnight`, `open`, `midday`, `close`, or `night` |

The open and midday slots collect indices, turnover, and market breadth only.
Limit-up/down pools and sector rankings are requested at close and during the
evening verification run to reduce pressure on public endpoints.

## `data/sectors.csv`

Stores the five leading and five trailing industries for each valid trading
date. `rank_type` is `up` or `down`; `net_inflow_yi` is estimated main-fund net
inflow in CNY 100 million.

## `data/latest.json`

The stable aggregate entry point for the latest daily row, most recent pulse,
sector rankings, analysis, global context, scorecard, and job status. Consumers
should check the top-level `schema_version`; the current version is `1`.

## `data/global.json`

The latest cross-market snapshot covers the S&P 500, Nasdaq, Dow, Nikkei 225,
Hang Seng, a European equity ETF proxy, FRED VIX, and the US 10-year Treasury
yield. `cross_assets` adds FTSE China A50 futures, USD/CNH, DXY, COMEX gold, and
WTI crude.

A50, USD/CNH, and DXY are bounded scoring evidence. Gold and WTI remain context
only and never add or subtract points directly. Market records include `close`,
`pct`, `previous_close`, and the upstream quote time. Proxy instruments are
identified through `kind` and `region`.

`health` reports each source as `fresh`, `partial`, `stale`, or `missing`. When
an upstream request fails, the pipeline may retain the last good observation
and marks the record with `stale: true` rather than presenting it as current.

## `data/analysis.json`

A transparent rules engine produces a cross-market risk temperature from
`-100` to `+100`. Components include A-share momentum, breadth, limit-up/down
sentiment, global equity performance, A50, USD/CNH and DXY, VIX, US 10Y, and a
bounded low-weight headline tone signal.

- `signals` preserves every score contribution and its explanation.
- `advice` contains general research observations, never personalized trade or
  allocation instructions.
- `news` contains deterministically deduplicated headline clues.
- `events` groups clues into central banks and rates, inflation and employment,
  geopolitics and trade, technology and industry, commodities and costs,
  dollar and renminbi, and domestic policy and demand.

Each event cluster contains `macro_path`, `a_share_lens`, `watch`,
`invalidation`, and up to two example headlines. `watch.state` is `fresh`,
`stale`, or `missing`. One headline may match several transmission channels.
Cluster counts are clue counts, not confirmed events, and event chains do not
directly alter the risk score.

## `data/signals/YYYY.csv`

An append-only ledger of the evidence visible at each automated run. It records
the slot, score, confidence, Shanghai Composite reference, average global move,
A50 change, USD/CNH, DXY, VIX, US 10Y, and degraded source names. Rows are unique
and sorted by `captured_at`. The ledger stores real run-time observations only;
it does not backfill signals with information that became available later.

## `data/scorecard.json`

Forward-only validation for recorded signals. Open and midday signals use that
session's close as the first evaluation point; close and night signals use the
next trading session. The pipeline also settles three- and five-session
compound returns.

`status` remains `collecting` until at least 20 directional one-session samples
have matured. Until then, consumers must not present a stable hit rate or
calibration claim.

## `data/status.json`

Refreshed on every workflow run. `market_state` can be:

- `live`: an intraday pulse was updated;
- `closed`: the official daily row was updated;
- `non_trading`: the market is closed or the target date has no quote yet;
- `unavailable`: the source is unavailable and the last valid market data is
  preserved;
- `checking`: the workflow is still evaluating the current slot.

## Compatibility rules

- Historical rows may omit sentiment columns introduced later. Treat them as
  `null`, not zero.
- New CSV fields are appended to the end of a row.
- Breaking JSON changes increment `schema_version`.
- Always inspect freshness before comparing or displaying live observations.
