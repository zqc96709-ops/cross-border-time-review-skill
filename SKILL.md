---
name: cross-border-time-review
description: "Create and maintain a visual time-tracking, daily review, weekly review, and Feishu/Lark Base dashboard system for solo cross-border e-commerce sellers. Use when the user wants to record hourly time use from chat, write time entries or daily reviews into Feishu Base automatically, create Base tables/dashboards with bar/pie/line charts, track main vs non-main time, analyze daily/weekly/monthly category proportions and trends, or generate an Excel fallback workbook."
---

# Cross-Border Time Review

Use this skill to help a solo cross-border e-commerce seller record time from chat and visualize focus in Feishu/Lark Base.

## Primary Workflow: Feishu Base

Prefer the Base workflow over ordinary Feishu Sheets. Base supports richer data entry, durable fields, views, and dashboards.

Create a new Base system:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/create_lark_base.py \
  --name "跨境电商时间管理与日复盘"
```

The script creates:

- Table `时间记录`
- Table `每日复盘`
- Dashboard `时间投入与复盘仪表盘`
- Dashboard blocks for category proportions, main vs non-main proportions, non-main overload, daily/weekly/monthly trends, and review score trends

After creation, set the Base token for chat logging:

```bash
export CBTR_BASE_TOKEN="<base_token>"
```

Or pass `--base-token <base_token>` to the logging scripts.

## Chat Time Logging

When the user chats from Feishu/Hermes and asks to record time, do not ask them to open Base. Parse their message, ask at most one clarification if required, then write the entry with:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/record_lark_time.py \
  --base-token "<base_token>" \
  --date 2026-07-01 \
  --start 09:00 \
  --end 10:00 \
  --task "调研日本猫玩具竞品，整理 8 个可测试方向" \
  --output "筛出 2 个候选产品" \
  --main 是 \
  --focus 4 \
  --energy 4
```

The script writes a record to Base table `时间记录` with derived fields:

- `年周`: ISO week such as `2026-W27`
- `月份`: `YYYY-MM`
- `时长`: calculated from start/end
- `类别`: inferred when missing
- `工作类型`: inferred from category
- `非主线时长过长`: `是` when non-main time exceeds the threshold

### Required Time Entry Fields

Require these fields before writing:

- `start` and `end`: time period, such as `09:00-10:00`
- `task`: what the user actually did

Strongly prefer:

- `output`: concrete result, even if it is `无明显产出`
- `main`: whether it advanced today's main task (`是` or `否`)
- `focus` and `energy`: 1-5 scores
- `distraction`: if relevant

If date is missing, default to today's date in Asia/Shanghai. If category is missing, infer it from the task text. If output is missing and the user did not explicitly say there was no output, ask: `这段有什么产出吗？可以写无明显产出。`

Natural language examples:

- `记录 9-10 点，调研日本猫玩具竞品，筛了 2 个方向，主线，专注 4，精力 4。`
- `10:00-11:30 回复客户和处理售后，产出：解决 3 个咨询，不是主线，专注 3。`
- `刚才 14-15 点刷选品视频，有点分心，没产出，干扰源手机/短视频。`

For ambiguous periods such as `刚才一小时`, infer from current time only if obvious in context; otherwise ask for the time range.

## Daily Review Logging

When the user says they want to do today's review, write to Base table `每日复盘`:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/record_lark_review.py \
  --base-token "<base_token>" \
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

If the user gives a free-form review, extract fields. If `main-task`, `completion`, and at least one of `outputs` or `conclusion` cannot be inferred, ask a concise follow-up.

## Base Dashboard Design

The Base dashboard should make these questions visible in real time:

- Today: category time proportion
- Today: main vs non-main time proportion
- Which non-main categories are taking too long
- Daily time trend
- Weekly category/time trend
- Monthly work-type/time trend
- Weekly and monthly total time trend
- Daily review score trend

The bundled `create_lark_base.py` creates dashboard blocks using Feishu Base components:

- `statistics`: total tracked hours
- `pie`: category time proportion
- `ring`: main vs non-main time proportion
- `bar`: non-main category overload
- `bar`: categories where flagged non-main work is too long
- `column`: daily category structure, daily main/non-main structure, weekly/monthly breakdowns
- `line`: daily/weekly/monthly trends
- `text`: usage note

## Ecommerce Categories

Use categories that reflect a solo seller's workflow:

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

Classify categories into work types:

- `推进型`: selection, listing, ads/data, content, supply chain
- `维护型`: customer service, orders/logistics, finance, communication
- `学习型`: learning and knowledge organization
- `杂事`: admin, tools, account maintenance
- `休息`: meals, exercise, household, rest
- `干扰`: low-intent browsing or avoidant work

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

## Excel Fallback

Keep the local Excel generator as a fallback or offline template:

```bash
python3 /Users/mac/.hermes/skills/productivity/cross-border-time-review/scripts/create_workbook.py \
  --start-date 2026-07-01 \
  --days 120 \
  --output "$HOME/Desktop/跨境电商时间管理复盘模板.xlsx"
```

Use Excel only when Feishu Base is unavailable or the user explicitly asks for a local workbook.
