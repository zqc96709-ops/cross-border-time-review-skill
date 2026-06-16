---
name: cross-border-time-review
description: "Create and maintain a visual time-tracking, daily review, and weekly review system for solo cross-border e-commerce sellers, including Excel generation and Feishu/Lark online-sheet logging. Use when the user wants to record hourly time use from chat, write time entries or daily reviews into the Feishu sheet automatically, see category proportions with charts, visualize daily reviews, track focus/main-task completion, or regenerate/customize the workbook for ecommerce operations."
---

# Cross-Border Time Review

Use this skill to help a solo cross-border e-commerce seller build or update a visual time-management and daily-review system.

## Quick Start

Generate a workbook with the bundled script:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/create_workbook.py \
  --output "$HOME/Desktop/跨境电商时间管理复盘模板.xlsx"
```

Common options:

```bash
# Start the tracker on a specific date and create 120 daily review rows
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/create_workbook.py \
  --start-date 2026-06-16 \
  --days 120 \
  --output "$HOME/Desktop/跨境电商时间管理复盘模板.xlsx"
```

If `openpyxl` is missing, use a Python environment that has it available, or install it into the active environment before running the script.

## Feishu/Lark Chat Logging

When the user chats from Feishu/Hermes and asks to record time, do not ask them to open the sheet. Parse their message, ask at most one clarification if required, then write the entry with:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/record_lark_time.py \
  --date 2026-06-16 \
  --start 09:00 \
  --end 10:00 \
  --task "调研日本猫玩具竞品，整理 8 个可测试方向" \
  --output "筛出 2 个候选产品" \
  --main 是 \
  --focus 4 \
  --energy 4
```

Configure the target Feishu spreadsheet before writing:

- Preferred: set `CBTR_SPREADSHEET_TOKEN` in the Hermes runtime environment.
- Alternative: pass `--spreadsheet-token <token>` on every script call.
- Time sheet: `时间记录`
- Review sheet: `每日复盘`

Do not hard-code personal spreadsheet tokens into the skill before publishing or sharing it.

### Required Time Entry Fields

Require these fields before writing a time entry:

- `start` and `end`: time period, such as `09:00-10:00`.
- `task`: what the user actually did.

Strongly prefer, but do not require:

- `output`: concrete result, even if it is "无明显产出".
- `main`: whether it advanced today's main task (`是` or `否`).
- `focus` and `energy`: 1-5 scores.

If date is missing, default to today's date in Asia/Shanghai. If category is missing, infer it from the task text using the ecommerce categories below. If output is missing, write an empty output only if the user's message clearly says they just want the entry recorded; otherwise ask "这段有什么产出吗？可以写无明显产出。"

### Natural Language Examples

Accept messages like:

- `记录 9-10 点，调研日本猫玩具竞品，筛了 2 个方向，主线，专注 4，精力 4。`
- `10:00-11:30 回复客户和处理售后，产出：解决 3 个咨询，不是主线，专注 3。`
- `刚才 14-15 点刷选品视频，有点分心，没产出，干扰源手机/短视频。`

For ambiguous periods such as `刚才一小时`, infer from the current time only if it is obvious in context; otherwise ask for the time range.

### Daily Review Logging

When the user says they want to do today's review, write `每日复盘` with:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/record_lark_review.py \
  --date 2026-06-16 \
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

If the user gives a free-form review, extract fields. If `main-task`, `completion`, and at least one of `outputs` or `conclusion` cannot be inferred, ask a concise follow-up.

## Workbook Design

Create workbooks with these sheets:

- `使用说明`: short usage guide for the user.
- `时间记录`: the only daytime input sheet; record date, start/end time, category, work type, main-task flag, output, focus, energy, distraction.
- `每日复盘`: the nightly review input sheet; record main task, completion rate, outputs, biggest time sink, distraction, tomorrow's main task, focus/energy/satisfaction scores.
- `可视化仪表盘`: charts driven by a selected date, including category bar chart, category pie chart, work-type doughnut chart, 14-day trend line chart, and daily review radar chart.
- `日汇总`: formula-based daily aggregation by category, work type, main-task hours, focus, energy, and review scores.
- `周复盘`: weekly battle/goal review with aggregate hours and review averages.
- `设置`: editable dropdown options for categories, work types, and distraction sources.

## Ecommerce Categories

Use categories that reflect a solo seller's real workflow:

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

Classify categories into work types so the dashboard can show whether the user is pushing the business forward:

- `推进型`: selection, listing, ads/data, content, supply chain.
- `维护型`: customer service, orders/logistics, finance, communication.
- `学习型`: learning and knowledge organization.
- `杂事`: admin, tools, account maintenance.
- `休息`: meals, exercise, household, rest.
- `干扰`: low-intent browsing or avoidant work.

## Daily Coaching

When explaining the workbook, keep the user's daily behavior simple:

1. Fill `时间记录` during the day in 30-120 minute blocks.
2. Fill `每日复盘` at night in 10 minutes.
3. Use `可视化仪表盘!B3` to select a date and inspect the charts.
4. Review `周复盘` once per week to check whether the week's main business battle moved forward.

Avoid turning this into a complex productivity system. The goal is to reveal where time goes, whether the daily main task moved, and which maintenance or distraction patterns are consuming attention.

## User Instruction Format

Teach the user this lightweight format:

```text
记录时间：09:00-10:00
做了什么：调研日本猫玩具竞品
产出：筛出 2 个候选产品
是否主线：是
专注/精力：4/4
干扰：无
```

Minimum usable version:

```text
记录 09:00-10:00，调研日本猫玩具竞品，产出筛出 2 个候选，是主线，专注4精力4
```

Daily review format:

```text
日复盘：
今日主线：完成 5 个新品调研
完成度：75%
三个产出：...
最大时间黑洞：...
明日主线：...
专注/精力/满意度：4/3/4
一句话结论：...
```
