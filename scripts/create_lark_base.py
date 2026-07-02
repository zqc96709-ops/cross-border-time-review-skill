#!/usr/bin/env python3
"""Create a Feishu/Lark Base time-review system with dashboard blocks."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


CATEGORIES = [
    "选品/市场调研",
    "上架/Listing优化",
    "广告/数据分析",
    "内容素材",
    "供应链/采购",
    "客服/售后",
    "订单/物流",
    "财务/记账",
    "学习/资料整理",
    "沟通/会议",
    "行政/工具/杂事",
    "休息/生活",
    "干扰/刷信息",
]

WORK_TYPES = ["推进型", "维护型", "学习型", "杂事", "休息", "干扰"]
YES_NO = ["是", "否"]
DISTRACTIONS = ["手机/短视频", "平台消息", "客户消息", "临时想法", "工具问题", "家务/生活", "疲劳拖延", "其他"]


def option(name: str, hue: str = "Blue") -> dict:
    return {"name": name, "hue": hue, "lightness": "Lighter"}


def select_field(name: str, values: list[str], hue: str = "Blue") -> dict:
    return {"type": "select", "name": name, "multiple": False, "options": [option(v, hue) for v in values]}


TIME_FIELDS = [
    {"type": "text", "name": "记录标题"},
    {"type": "datetime", "name": "日期", "style": {"format": "yyyy-MM-dd"}},
    {"type": "text", "name": "年周", "description": "ISO week, e.g. 2026-W27. Used for weekly dashboard grouping."},
    {"type": "text", "name": "月份", "description": "YYYY-MM. Used for monthly dashboard grouping."},
    {"type": "text", "name": "开始时间"},
    {"type": "text", "name": "结束时间"},
    {"type": "number", "name": "时长", "style": {"type": "plain", "precision": 2, "percentage": False, "thousands_separator": False}},
    select_field("类别", CATEGORIES, "Blue"),
    select_field("工作类型", WORK_TYPES, "Green"),
    select_field("是否主线", YES_NO, "Orange"),
    {"type": "text", "name": "任务"},
    {"type": "text", "name": "产出"},
    {"type": "number", "name": "专注评分", "style": {"type": "rating", "icon": "star", "min": 1, "max": 5}},
    {"type": "number", "name": "精力评分", "style": {"type": "rating", "icon": "star", "min": 1, "max": 5}},
    select_field("干扰源", DISTRACTIONS, "Red"),
    select_field("非主线时长过长", YES_NO, "Red"),
    {"type": "text", "name": "备注"},
]

REVIEW_FIELDS = [
    {"type": "text", "name": "复盘标题"},
    {"type": "datetime", "name": "日期", "style": {"format": "yyyy-MM-dd"}},
    {"type": "text", "name": "年周"},
    {"type": "text", "name": "月份"},
    {"type": "text", "name": "今日主线任务"},
    {"type": "number", "name": "主线完成度", "style": {"type": "progress", "percentage": True, "color": "Blue"}},
    {"type": "text", "name": "今日产出"},
    {"type": "text", "name": "最大时间黑洞"},
    select_field("最大干扰源", DISTRACTIONS, "Red"),
    {"type": "text", "name": "明日主线任务"},
    {"type": "text", "name": "明日第一步动作"},
    {"type": "number", "name": "专注评分", "style": {"type": "rating", "icon": "star", "min": 1, "max": 5}},
    {"type": "number", "name": "能量评分", "style": {"type": "rating", "icon": "star", "min": 1, "max": 5}},
    {"type": "number", "name": "满意度", "style": {"type": "rating", "icon": "star", "min": 1, "max": 5}},
    {"type": "text", "name": "一句话结论"},
]


def run_lark(args: list[str]) -> dict:
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"lark-cli failed: {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


def command_plan(command: list[str]) -> dict:
    display = []
    skip_next = False
    for idx, item in enumerate(command):
        if skip_next:
            skip_next = False
            continue
        if item in {"--fields", "--data-config"} and idx + 1 < len(command):
            display.append(item)
            display.append(json.loads(command[idx + 1]))
            skip_next = True
        else:
            display.append(item)
    return {"command": display}


def base_create(name: str, dry_run: bool) -> dict:
    args = [
        "lark-cli", "base", "+base-create",
        "--as", "user",
        "--name", name,
        "--time-zone", "Asia/Shanghai",
        "--table-name", "时间记录",
        "--fields", json.dumps(TIME_FIELDS, ensure_ascii=False),
        "--format", "json",
    ]
    if dry_run:
        return command_plan(args + ["--dry-run"])
    return run_lark(args)


def table_create(base_token: str, dry_run: bool) -> dict:
    args = [
        "lark-cli", "base", "+table-create",
        "--as", "user",
        "--base-token", base_token,
        "--name", "每日复盘",
        "--fields", json.dumps(REVIEW_FIELDS, ensure_ascii=False),
        "--format", "json",
    ]
    if dry_run:
        return command_plan(args + ["--dry-run"])
    return run_lark(args)


def dashboard_create(base_token: str, dry_run: bool) -> dict:
    args = [
        "lark-cli", "base", "+dashboard-create",
        "--as", "user",
        "--base-token", base_token,
        "--name", "时间投入与复盘仪表盘",
        "--format", "json",
    ]
    if dry_run:
        return command_plan(args + ["--dry-run"])
    return run_lark(args)


def dashboard_block(base_token: str, dashboard_id: str, name: str, block_type: str, data_config: dict, dry_run: bool) -> dict:
    args = [
        "lark-cli", "base", "+dashboard-block-create",
        "--as", "user",
        "--base-token", base_token,
        "--dashboard-id", dashboard_id,
        "--name", name,
        "--type", block_type,
        "--data-config", json.dumps(data_config, ensure_ascii=False),
        "--format", "json",
    ]
    if dry_run:
        return command_plan(args + ["--dry-run"])
    return run_lark(args)


def arrange(base_token: str, dashboard_id: str, dry_run: bool) -> dict:
    args = [
        "lark-cli", "base", "+dashboard-arrange",
        "--as", "user",
        "--base-token", base_token,
        "--dashboard-id", dashboard_id,
        "--format", "json",
    ]
    if dry_run:
        return command_plan(args + ["--dry-run"])
    return run_lark(args)


def create_blocks(base_token: str, dashboard_id: str, dry_run: bool) -> list[dict]:
    blocks = [
        ("总投入小时", "statistics", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}]}),
        ("每天任务时间占比（按类别）", "pie", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "类别", "mode": "integrated"}]}),
        ("主线与非主线时间占比", "ring", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "是否主线", "mode": "integrated"}]}),
        ("非主线时间过长来源", "bar", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "类别", "mode": "integrated", "sort": {"type": "value", "order": "desc"}}], "filter": {"conjunction": "and", "conditions": [{"field_name": "是否主线", "operator": "is", "value": "否"}]}}),
        ("非主线过长记录占比", "bar", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "类别", "mode": "integrated", "sort": {"type": "value", "order": "desc"}}], "filter": {"conjunction": "and", "conditions": [{"field_name": "非主线时长过长", "operator": "is", "value": "是"}]}}),
        ("每日时间趋势", "line", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "日期", "mode": "integrated", "sort": {"type": "group", "order": "asc"}}]}),
        ("每日类别时间结构", "column", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "日期", "mode": "integrated", "sort": {"type": "group", "order": "asc"}}, {"field_name": "类别", "mode": "integrated"}]}),
        ("每日主线/非主线结构", "column", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "日期", "mode": "integrated", "sort": {"type": "group", "order": "asc"}}, {"field_name": "是否主线", "mode": "integrated"}]}),
        ("每周时间占比", "column", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "年周", "mode": "integrated", "sort": {"type": "group", "order": "asc"}}, {"field_name": "类别", "mode": "integrated"}]}),
        ("每月时间占比", "column", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "月份", "mode": "integrated", "sort": {"type": "group", "order": "asc"}}, {"field_name": "工作类型", "mode": "integrated"}]}),
        ("每周时间趋势", "line", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "年周", "mode": "integrated", "sort": {"type": "group", "order": "asc"}}]}),
        ("每月时间趋势", "line", {"table_name": "时间记录", "series": [{"field_name": "时长", "rollup": "SUM"}], "group_by": [{"field_name": "月份", "mode": "integrated", "sort": {"type": "group", "order": "asc"}}]}),
        ("复盘评分趋势", "line", {"table_name": "每日复盘", "series": [{"field_name": "专注评分", "rollup": "AVERAGE"}, {"field_name": "能量评分", "rollup": "AVERAGE"}, {"field_name": "满意度", "rollup": "AVERAGE"}], "group_by": [{"field_name": "日期", "mode": "integrated", "sort": {"type": "group", "order": "asc"}}]}),
        ("使用说明", "text", {"text": "# 使用方式\n\n在飞书/Hermes 中说：`记录 09:00-10:00，调研日本猫玩具竞品，产出筛出2个候选，是主线，专注4精力4`。\n\n日复盘说：`日复盘：今日主线... 完成度75% ...`。仪表盘会随 Base 记录实时聚合更新。"}),
    ]
    results = []
    for name, block_type, config in blocks:
        results.append(dashboard_block(base_token, dashboard_id, name, block_type, config, dry_run))
        if not dry_run:
            time.sleep(0.3)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="跨境电商时间管理与日复盘")
    parser.add_argument("--output", default="", help="Optional JSON file to save created identifiers.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-dashboard", action="store_true")
    return parser.parse_args()


def extract_base_token(result: dict) -> str:
    data = result.get("data", {})
    for key in ("base", "app", "bitable"):
        obj = data.get(key)
        if isinstance(obj, dict):
            token = obj.get("base_token") or obj.get("app_token") or obj.get("token")
            if token:
                return token
    token = data.get("base_token") or data.get("app_token") or data.get("token")
    if token:
        return token
    text = json.dumps(result, ensure_ascii=False)
    raise RuntimeError(f"Could not find base token in create response: {text}")


def extract_dashboard_id(result: dict) -> str:
    data = result.get("data", {})
    for key in ("dashboard", "block"):
        obj = data.get(key)
        if isinstance(obj, dict):
            dashboard_id = obj.get("dashboard_id") or obj.get("block_id")
            if dashboard_id:
                return dashboard_id
    dashboard_id = data.get("dashboard_id") or data.get("block_id")
    if dashboard_id:
        return dashboard_id
    raise RuntimeError(f"Could not find dashboard_id in response: {json.dumps(result, ensure_ascii=False)}")


def main() -> None:
    args = parse_args()
    base_result = base_create(args.name, args.dry_run)
    if args.dry_run:
        dashboard_plan = None
        block_plans = []
        arrange_plan = None
        if not args.skip_dashboard:
            dashboard_plan = dashboard_create("<base_token>", True)
            block_plans = create_blocks("<base_token>", "<dashboard_id>", True)
            arrange_plan = arrange("<base_token>", "<dashboard_id>", True)
        print(json.dumps({
            "base_create": base_result,
            "review_table_create": table_create("<base_token>", True),
            "dashboard_create": dashboard_plan,
            "dashboard_blocks": block_plans,
            "dashboard_arrange": arrange_plan,
            "note": "Dry run is local-only and does not access Feishu auth/keychain.",
        }, ensure_ascii=False, indent=2))
        return
    base_token = extract_base_token(base_result)
    review_result = table_create(base_token, False)
    dashboard_result = None
    dashboard_id = None
    block_results = []
    arrange_result = None
    if not args.skip_dashboard:
        dashboard_result = dashboard_create(base_token, False)
        dashboard_id = extract_dashboard_id(dashboard_result)
        block_results = create_blocks(base_token, dashboard_id, False)
        arrange_result = arrange(base_token, dashboard_id, False)
    result = {
        "base_token": base_token,
        "base_result": base_result,
        "review_table_result": review_result,
        "dashboard_id": dashboard_id,
        "dashboard_result": dashboard_result,
        "block_results": block_results,
        "arrange_result": arrange_result,
        "next_steps": [
            "Set CBTR_BASE_TOKEN to this base_token in the Hermes runtime.",
            "Use record_lark_time.py for chat-based time entries.",
            "Use record_lark_review.py for daily reviews.",
        ],
    }
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
