---
name: cross-border-time-review
description: "Unified Hermes workflow for a solo cross-border e-commerce seller: record hourly time use, daily reviews, expense entries, tomorrow plans, and task-board updates from chat. Use when the user wants to write time entries or daily reviews into the Feishu Base 跨境电商时间管理复盘（多维表格版）, record expenses into the Feishu Base 费用明细, write tomorrow plans or tasks into the Feishu Base 个人任务看板, maintain Base dashboards, analyze daily/weekly/monthly time proportions and trends, or generate an Excel fallback workbook."
---

# Cross-Border Time Review

Use this skill as the single workflow for time tracking, daily review, expense logging, and tomorrow-plan/task-board updates.

## Production Targets

All normal writes should use these resources with `--as user`. Resolve private Base tokens and table IDs from `config/local.json` or environment variables; do not hard-code private Feishu IDs in public instructions.

| Purpose | Feishu resource | Config keys |
|---|---|---|
| Time records and daily reviews | `跨境电商时间管理复盘（多维表格版）` | `time_review.base_token`, `time_review.time_table`, `time_review.review_table` |
| Expense records | `费用明细` | `expense.base_token`, `expense.table_id` |
| Tomorrow plans and tasks | `个人任务看板` | `task.base_token`, `task.table_id` |

Do not write new time records or daily reviews to the old spreadsheet version of this workflow.

## Quick Routing

| User intent | Action |
|---|---|
| `记录 09:00-10:00...` / time block | Run `scripts/record_lark_time.py` |
| `日复盘...` / nightly review | Run `scripts/record_lark_review.py`, then sync tomorrow tasks to `个人任务看板` |
| `记账` / `花了...` / expense | Run `scripts/record_expense.py` |
| `记一个待办` / `加一个任务` / tomorrow plan | Run `scripts/record_task.py` after checking duplicates |
| `完成了...` / task status update | Find the task in `个人任务看板`, then update `状态` |

## Time Logging

When the user records a time block, require:

- `start` and `end`, such as `09:00-10:00`
- `task`, meaning what was actually done

Strongly prefer:

- `output`, even if `无明显产出`
- `main`, whether it advanced today's main task (`是` or `否`)
- `focus` and `energy`, 1-5
- `distraction`, if relevant

Write with:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/record_lark_time.py \
  --date 2026-07-01 \
  --start 09:00 \
  --end 10:00 \
  --task "调研日本猫玩具竞品" \
  --output "筛出 2 个候选产品" \
  --main 是 \
  --focus 4 \
  --energy 4
```

The script defaults to the configured time-review Base, table `时间记录`, and derives `年周`, `月份`, `时长`, `类别`, `工作类型`, and `非主线时长过长`.

If `output` is missing and the user did not explicitly say no output, ask: `这段有什么产出吗？可以写无明显产出。`

## Daily Review

When the user sends a daily review, write the review first:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/record_lark_review.py \
  --date 2026-07-01 \
  --main-task "完成 5 个新品调研" \
  --completion 75% \
  --outputs "调研 8 个竞品；筛出 2 个候选；优化 1 条 listing" \
  --time-sink "客服消息分散" \
  --distraction "平台消息" \
  --tomorrow-main "完成 2 个候选产品利润测算" \
  --tomorrow-first-step "09:00 打开调研表补齐采购价和运费" \
  --focus 4 \
  --energy 3 \
  --satisfaction 4 \
  --conclusion "今天推进了选品，但维护型事务偏多。"
```

The script defaults to the configured time-review Base, table `每日复盘`. Completion accepts only `0%`, `25%`, `50%`, `75%`, `100%`; if the user gives another percentage, choose the nearest lower bucket unless they clarify.

After writing the daily review, parse `明日主线任务` and `明日第一步动作` into tomorrow tasks:

1. Read existing `个人任务看板` records whose `状态` is `未开始` or `进行中`.
2. Compare by core keywords and semantic similarity.
3. Create only truly new tasks; do not duplicate similar active tasks.
4. If there are new tasks and possible overlaps, create the clearly new tasks first, then report overlaps.

Create a task with:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/record_task.py \
  --name "完成 2 个候选产品利润测算" \
  --detail "09:00 打开调研表补齐采购价和运费" \
  --status 未开始 \
  --category 工作 \
  --label "📌 重要不紧急"
```

## Expenses

When the user asks to record an expense, require item, amount, and payment method. If payment method is missing, ask which one: `蓝胖子 / 欧易 / 招商信用卡 / 支付宝`.

Write with:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/record_expense.py \
  --item "刻公章" \
  --amount 120 \
  --payment 蓝胖子 \
  --currency "¥" \
  --date 6.25
```

Defaults:

- Base: configured `费用明细`
- Table: configured expense table ID
- Date format: `M.D`
- Currency: `¥`, unless USD is explicit

## Task Board

For direct tasks or tomorrow plans, write to `个人任务看板`:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/record_task.py \
  --name "去中国银行线下拿公户" \
  --status 未开始 \
  --category 工作 \
  --label "🔥 重要紧急" \
  --detail "明日第一步"
```

Valid task options:

- `状态`: `未开始`, `进行中`, `已完成`
- `任务类别`: `学习`, `生活`, `工作`
- `任务标签`: `🔥 重要紧急`, `📌 重要不紧急`, `🤣 不重要紧急`, `👇 不重要不紧急`

When marking a task complete, first find the target record in `个人任务看板`, then update only `状态`:

```bash
lark-cli base +record-upsert --as user \
  --base-token "$CBTR_TASK_BASE_TOKEN" \
  --table-id "$CBTR_TASK_TABLE_ID" \
  --record-id <record_id> \
  --json '{"状态":"已完成"}' \
  --format json
```

## Categories

Use these ecommerce categories:

- `选品/市场调研`
- `上架/Listing优化`
- `广告/数据分析`
- `内容素材`
- `供应链/采购`
- `客服/售后`
- `订单/物流`
- `财务/记账`
- `学习/资料整理`
- `沟通/会议`
- `行政/工具/杂事`
- `休息/生活`
- `干扰/刷信息`

Classify work types:

- `推进型`: selection, listing, ads/data, content, supply chain
- `维护型`: customer service, orders/logistics, finance, communication
- `学习型`: learning and knowledge organization
- `杂事`: admin, tools, accounts
- `休息`: meals, exercise, household, rest
- `干扰`: low-intent browsing or avoidant work

Map distractions exactly:

- 看电视/刷手机/刷短视频/刷抖音/刷视频 -> `手机/短视频`
- 平台消息/群消息/通知 -> `平台消息`
- 回客户/售后/回复客户消息 -> `客户消息`
- 突然想到/临时做 -> `临时想法`
- 工具出问题/报错/调试卡住 -> `工具问题`
- 做家务/做饭/家里有事/上厕所 -> `家务/生活`
- 累了/不想动/拖延/睡过头 -> `疲劳拖延`
- otherwise -> `其他`

## Base Dashboard

The time-review Base contains dashboard `时间投入与复盘仪表盘` with:

- total tracked hours
- category proportions
- main vs non-main proportions
- non-main overload sources
- daily category structure
- daily main/non-main structure
- weekly/monthly proportions and trends
- review score trend

## Excel Fallback

Use Excel only when Feishu Base is unavailable or the user explicitly asks for a local workbook:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/create_workbook.py \
  --start-date 2026-07-01 \
  --days 120 \
  --output "$HOME/Desktop/跨境电商时间管理复盘模板.xlsx"
```
