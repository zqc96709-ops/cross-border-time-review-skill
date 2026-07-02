#!/usr/bin/env python3
"""Create one time-log record in the Feishu/Lark Base version of this system."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import date, datetime, time
from zoneinfo import ZoneInfo


TIME_TABLE = "时间记录"
TIMEZONE = ZoneInfo("Asia/Shanghai")

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

WORK_TYPE_BY_CATEGORY = {
    "选品/市场调研": "推进型",
    "上架/Listing优化": "推进型",
    "广告/数据分析": "推进型",
    "内容素材": "推进型",
    "供应链/采购": "推进型",
    "客服/售后": "维护型",
    "订单/物流": "维护型",
    "财务/记账": "维护型",
    "学习/资料整理": "学习型",
    "沟通/会议": "维护型",
    "行政/工具/杂事": "杂事",
    "休息/生活": "休息",
    "干扰/刷信息": "干扰",
}

DISTRACTIONS = ["手机/短视频", "平台消息", "客户消息", "临时想法", "工具问题", "家务/生活", "疲劳拖延", "其他", ""]

CATEGORY_KEYWORDS = [
    ("选品/市场调研", ["选品", "竞品", "市场", "调研", "利润", "关键词调研", "需求"]),
    ("上架/Listing优化", ["上架", "listing", "标题", "五点", "详情页", "关键词", "优化链接"]),
    ("广告/数据分析", ["广告", "投放", "acos", "roi", "数据", "报表", "转化", "点击"]),
    ("内容素材", ["素材", "图片", "视频", "文案", "短视频", "主图", "买家秀"]),
    ("供应链/采购", ["供应链", "采购", "工厂", "1688", "打样", "报价", "交期", "供应商"]),
    ("客服/售后", ["客服", "客户", "售后", "纠纷", "评价", "消息"]),
    ("订单/物流", ["订单", "物流", "发货", "跟踪", "仓库", "运单"]),
    ("财务/记账", ["财务", "记账", "利润", "账单", "税", "成本"]),
    ("学习/资料整理", ["学习", "课程", "资料", "笔记", "整理方法"]),
    ("沟通/会议", ["会议", "沟通", "电话", "对接"]),
    ("行政/工具/杂事", ["工具", "账号", "插件", "表格", "设置", "杂事"]),
    ("休息/生活", ["休息", "吃饭", "运动", "家务", "生活"]),
    ("干扰/刷信息", ["刷", "短视频", "信息流", "摸鱼", "分心", "拖延"]),
]


def run_lark(args: list[str]) -> dict:
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"lark-cli failed: {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


def today() -> str:
    return datetime.now(TIMEZONE).date().isoformat()


def parse_clock(value: str) -> time:
    value = value.strip()
    for fmt in ("%H:%M", "%H点%M", "%H点"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            pass
    if value.isdigit() and 0 <= int(value) <= 23:
        return time(hour=int(value))
    raise SystemExit(f"Invalid time: {value}. Use HH:MM, e.g. 09:00.")


def hours_between(start: str, end: str) -> float:
    start_t = parse_clock(start)
    end_t = parse_clock(end)
    start_minutes = start_t.hour * 60 + start_t.minute
    end_minutes = end_t.hour * 60 + end_t.minute
    if end_minutes < start_minutes:
        end_minutes += 24 * 60
    return round((end_minutes - start_minutes) / 60, 2)


def normalize_time(value: str) -> str:
    return parse_clock(value).strftime("%H:%M")


def infer_category(text: str) -> str:
    lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if any(keyword.lower() in lower for keyword in keywords):
            return category
    return "行政/工具/杂事"


def normalize_category(category: str | None, text: str) -> str:
    if not category:
        return infer_category(text)
    category = category.strip()
    if category in CATEGORIES:
        return category
    for item in CATEGORIES:
        if category in item or item in category:
            return item
    raise SystemExit(f"Unknown category: {category}. Valid categories: {', '.join(CATEGORIES)}")


def normalize_score(value: str | None, field: str) -> int | None:
    if value in (None, ""):
        return None
    value = str(value).strip()
    if value not in {"1", "2", "3", "4", "5"}:
        raise SystemExit(f"{field} must be 1-5, got {value}")
    return int(value)


def normalize_yes_no(value: str | None) -> str:
    if not value:
        return "否"
    value = value.strip().lower()
    return "是" if value in {"是", "yes", "y", "true", "1", "主线"} else "否"


def date_parts(date_value: str) -> tuple[str, str, str]:
    parsed = datetime.strptime(date_value, "%Y-%m-%d").date()
    iso_year, iso_week, _ = parsed.isocalendar()
    return parsed.isoformat(), f"{iso_year}-W{iso_week:02d}", parsed.strftime("%Y-%m")


def build_fields(args: argparse.Namespace) -> dict:
    date_value = args.date or today()
    day, week, month = date_parts(date_value)
    start = normalize_time(args.start)
    end = normalize_time(args.end)
    duration = hours_between(start, end)
    text_for_category = " ".join([args.task or "", args.output or "", args.note or ""])
    category = normalize_category(args.category, text_for_category)
    main = normalize_yes_no(args.main)
    distraction = args.distraction or ""
    if distraction and distraction not in DISTRACTIONS:
        distraction = "其他"
    title = f"{day} {start}-{end} {args.task[:32]}"
    fields = {
        "记录标题": title,
        "日期": day,
        "年周": week,
        "月份": month,
        "开始时间": start,
        "结束时间": end,
        "时长": duration,
        "类别": category,
        "工作类型": WORK_TYPE_BY_CATEGORY[category],
        "是否主线": main,
        "任务": args.task,
        "产出": args.output or "",
        "非主线时长过长": "是" if main == "否" and duration >= args.non_main_threshold else "否",
        "备注": args.note or "",
    }
    focus = normalize_score(args.focus, "focus")
    energy = normalize_score(args.energy, "energy")
    if focus is not None:
        fields["专注评分"] = focus
    if energy is not None:
        fields["精力评分"] = energy
    if distraction:
        fields["干扰源"] = distraction
    return fields


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-token", default=None, help="Feishu Base token. Defaults to CBTR_BASE_TOKEN.")
    parser.add_argument("--table-id", default=TIME_TABLE, help="Base table id or name. Defaults to 时间记录.")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD. Defaults to today in Asia/Shanghai.")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--category", default=None, choices=CATEGORIES)
    parser.add_argument("--main", default="否", help="是/否")
    parser.add_argument("--task", required=True)
    parser.add_argument("--output", default="")
    parser.add_argument("--energy", default="")
    parser.add_argument("--focus", default="")
    parser.add_argument("--distraction", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--non-main-threshold", type=float, default=1.5, help="Hours after which non-main work is flagged.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_token = args.base_token or os.environ.get("CBTR_BASE_TOKEN")
    if not base_token:
        raise SystemExit("Set --base-token or CBTR_BASE_TOKEN before writing to Feishu Base.")
    fields = build_fields(args)
    payload = {"base_token": base_token, "table_id": args.table_id, "fields": fields}
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    result = run_lark([
        "lark-cli", "base", "+record-upsert",
        "--as", "user",
        "--base-token", base_token,
        "--table-id", args.table_id,
        "--json", json.dumps(fields, ensure_ascii=False),
        "--format", "json",
    ])
    print(json.dumps({"ok": True, "table": args.table_id, "fields": fields, "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
