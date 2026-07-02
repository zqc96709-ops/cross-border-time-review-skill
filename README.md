# Cross-Border Time Review Skill

面向个人跨境电商卖家的时间记录、日复盘、费用记账、明日计划与飞书多维表格可视化仪表盘 Skill。

它的目标是：你不用手动打开表格，只要在 Hermes / 飞书渠道里用自然语言说“我刚才做了什么”“今天复盘”“记一笔费用”“明天要做什么”，Hermes 就能把数据写入对应的飞书多维表格，并通过 Base 仪表盘实时查看每天、每周、每月的时间花费占比和趋势。

## 适合谁

- 个人在家做跨境电商，每天被选品、上架、广告、客服、物流、供应链等事情切碎。
- 想知道每天时间到底花在了哪里。
- 想看到主线与非主线时间占比。
- 想发现哪些非主线工作占用过长。
- 想按日、周、月查看时间占比和趋势。
- 想通过聊天记录工作，而不是手动填表。
- 想把费用记账写入 `费用明细`。
- 想把明日计划和待办写入 `个人任务看板`。

## 核心能力

- 创建飞书多维表格 Base。
- 创建 `时间记录` 和 `每日复盘` 两张数据表。
- 创建 Base 仪表盘，用柱状图、饼图、环形图、折线图展示时间分析。
- 将聊天中的时间记录自动写入 Base。
- 将每日复盘自动写入 Base。
- 将项目费用自动写入 `费用明细`。
- 将明日计划和任务自动写入 `个人任务看板`。
- 自动识别跨境电商工作类别，例如选品、Listing 优化、广告、供应链、客服、物流等。
- 自动区分推进型、维护型、学习型、杂事、休息、干扰。
- 自动生成 `年周`、`月份`、`时长`、`工作类型`、`非主线时长过长` 等分析字段。

## 安装到 Hermes

把仓库克隆到 Hermes skills 目录：

```bash
git clone https://github.com/zqc96709-ops/cross-border-time-review-skill.git \
  ~/.hermes/skills/productivity/cross-border-time-review
```

然后在 Hermes 中使用：

```text
Use $cross-border-time-review to create a Feishu Base time-review dashboard.
```

## 前置条件

需要本机已经配置好：

- `hermes`
- `lark-cli`
- 飞书用户身份授权，并具备 Base 创建和读写权限

检查飞书授权：

```bash
lark-cli auth status
```

## 默认写入目标

日常使用会写入以下飞书资源。真实 Base token 和 table ID 放在本机私有配置 `config/local.json` 或环境变量里，不提交到 GitHub：

- 时间记录与日复盘：`跨境电商时间管理复盘（多维表格版）`
- 费用记账：`费用明细`
- 明日计划/任务看板：`个人任务看板`

旧飞书表格 `跨境电商时间管理复盘（在线版测试）` 只保留历史数据，不再作为新记录写入目标。

本机私有配置格式见 `config/local.example.json`。也可以用环境变量覆盖：

```bash
export CBTR_BASE_TOKEN="时间记录与日复盘 Base token"
export CBTR_EXPENSE_BASE_TOKEN="费用明细 Base token"
export CBTR_EXPENSE_TABLE_ID="费用明细 table ID"
export CBTR_TASK_BASE_TOKEN="个人任务看板 Base token"
export CBTR_TASK_TABLE_ID="个人任务看板 table ID"
```

## 创建新的飞书多维表格 Base

运行：

```bash
python3 scripts/create_lark_base.py \
  --name "跨境电商时间管理与日复盘"
```

如果你要另建一套系统，创建成功后脚本会输出 `base_token`。把它配置给 Hermes：

```bash
export CBTR_BASE_TOKEN="你的 base_token"
```

配置好 `config/local.json` 后默认不需要传 token；脚本会写入配置的生产 Base。也可以在脚本调用时传入：

```bash
python3 scripts/record_lark_time.py \
  --base-token "你的 base_token" \
  --date 2026-07-01 \
  --start 09:00 \
  --end 10:00 \
  --task "调研日本猫玩具竞品" \
  --output "筛出 2 个候选产品" \
  --main 是 \
  --focus 4 \
  --energy 4
```

## Base 会创建什么

### 数据表 1：时间记录

核心字段：

- `记录标题`
- `日期`
- `年周`
- `月份`
- `开始时间`
- `结束时间`
- `时长`
- `类别`
- `工作类型`
- `是否主线`
- `任务`
- `产出`
- `专注评分`
- `精力评分`
- `干扰源`
- `非主线时长过长`
- `备注`

### 数据表 2：每日复盘

核心字段：

- `复盘标题`
- `日期`
- `年周`
- `月份`
- `今日主线任务`
- `主线完成度`
- `今日产出`
- `最大时间黑洞`
- `最大干扰源`
- `明日主线任务`
- `明日第一步动作`
- `专注评分`
- `能量评分`
- `满意度`
- `一句话结论`

### 仪表盘

默认创建这些可视化：

- 总投入小时
- 每天任务时间占比（按类别）
- 主线与非主线时间占比
- 非主线时间过长来源
- 非主线过长记录占比
- 每日时间趋势
- 每日类别时间结构
- 每日主线/非主线结构
- 每周时间占比
- 每月时间占比
- 每周时间趋势
- 每月时间趋势
- 复盘评分趋势

## 日常怎么对 Hermes 说

最推荐的格式：

```text
记录 09:00-10:00，调研日本猫玩具竞品，产出筛出2个候选，是主线，专注4精力4
```

更完整的格式：

```text
记录时间：14:00-15:30
做了什么：优化日本站猫窝 listing 标题和五点
产出：完成 1 条 listing 优化
是否主线：是
专注/精力：4/3
干扰：平台消息
```

最低限度要告诉 Hermes：

- 时间段：例如 `09:00-10:00`
- 做了什么：例如 `调研日本猫玩具竞品`

最好再补充：

- 产出：例如 `筛出 2 个候选产品`
- 是否主线：`是主线` / `不是主线`
- 专注和精力：1-5 分
- 干扰源：例如 `手机/短视频`、`平台消息`

## 时间记录示例

```text
记录 10:00-11:30 回复客户和处理售后，产出解决3个咨询，不是主线，专注3精力4。
```

Hermes 会写入：

- 类别：`客服/售后`
- 工作类型：`维护型`
- 时长：`1.5`
- 是否主线：`否`
- 专注：`3`
- 精力：`4`

```text
记录 13:00-14:00 做1688供应商沟通，问了3家报价和交期，产出拿到2家报价，不是主线，专注3精力3，干扰源平台消息。
```

Hermes 会自动归类为：

- 类别：`供应链/采购`
- 工作类型：`推进型`

## 日复盘怎么说

```text
日复盘：
今日主线：完成5个新品调研
完成度：75%
三个产出：筛出2个候选；优化1条listing；回复完售后
最大时间黑洞：客服消息分散
明日主线：完成2个候选产品利润测算
明日第一步：09:00打开调研表补齐采购价和运费
专注/精力/满意度：4/3/4
一句话结论：今天推进了选品，但维护型事务偏多
```

日复盘写入后，Hermes 还应把 `明日主线` 拆成任务，去重后写入 `个人任务看板`。

## 费用怎么说

```text
记账，今天刻公章花了120元，蓝胖子支付
```

至少告诉 Hermes：

- 费用项目
- 金额
- 支付方式：`蓝胖子`、`欧易`、`招商信用卡`、`支付宝`

## 任务怎么说

```text
记一个待办：明天去中国银行线下拿公户，重要紧急，工作
```

Hermes 会写入 `个人任务看板`，默认状态为 `未开始`。

## 脚本说明

创建飞书 Base：

```bash
python3 scripts/create_lark_base.py \
  --name "跨境电商时间管理与日复盘"
```

写入一条 Base 时间记录：

```bash
python3 scripts/record_lark_time.py \
  --date 2026-07-01 \
  --start 09:00 \
  --end 10:00 \
  --task "调研日本猫玩具竞品" \
  --output "筛出 2 个候选产品" \
  --main 是 \
  --focus 4 \
  --energy 4
```

写入一条 Base 日复盘：

```bash
python3 scripts/record_lark_review.py \
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

写入一条费用：

```bash
python3 scripts/record_expense.py \
  --item "刻公章" \
  --amount 120 \
  --payment 蓝胖子 \
  --currency "¥" \
  --date 6.25
```

写入一条任务：

```bash
python3 scripts/record_task.py \
  --name "去中国银行线下拿公户" \
  --status 未开始 \
  --category 工作 \
  --label "🔥 重要紧急" \
  --detail "明日第一步"
```

先预览不写入：

```bash
python3 scripts/record_lark_time.py \
  --base-token "dummy" \
  --start 09:00 \
  --end 10:00 \
  --task "调研日本猫玩具竞品" \
  --dry-run
```

## 工作分类

默认类别：

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

工作类型：

- `推进型`
- `维护型`
- `学习型`
- `杂事`
- `休息`
- `干扰`

## Excel Fallback

如果暂时不用飞书 Base，也可以生成本地 Excel 模板：

```bash
python3 scripts/create_workbook.py \
  --start-date 2026-07-01 \
  --days 120 \
  --output "$HOME/Desktop/跨境电商时间管理复盘模板.xlsx"
```

## 注意事项

- 不要把个人 `base_token` 提交到 GitHub。
- 不要把真实飞书 Base token、table ID、app secret、access token 或 cookie 提交到 GitHub。
- 如果 Hermes 无法写入 Base，先确认 `lark-cli auth status` 中 user 身份可用。
- 如果缺少时间段，Hermes 应先追问，不要猜。
- 如果没有产出，可以明确说 `无明显产出`，这比空着更有复盘价值。
