#!/usr/bin/env python3
"""Create one daily-review record in the Feishu/Lark Base version of this system."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from cbtr_config import config_value, require_value

REVIEW_TABLE = config_value("time_review", "review_table", "CBTR_REVIEW_TABLE", "每日复盘")
TIMEZONE = ZoneInfo("Asia/Shanghai")
DISTRACTIONS = ["手机/短视频", "平台消息", "客户消息", "临时想法", "工具问题", "家务/生活", "疲劳拖延", "其他", ""]


def run_lark(args: list[str]) -> dict:
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"lark-cli failed: {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


def today() -> str:
    return datetime.now(TIMEZONE).date().isoformat()


def normalize_score(value: str | None, field: str) -> int | None:
    if value in (None, ""):
        return None
    value = str(value).strip()
    if value not in {"1", "2", "3", "4", "5"}:
        raise SystemExit(f"{field} must be 1-5, got {value}")
    return int(value)


def normalize_completion(value: str | None) -> float | int | None:
    if not value:
        return None
    value = str(value).strip().replace("%", "")
    mapping = {"0": 0, "25": 0.25, "50": 0.5, "75": 0.75, "100": 1}
    if value not in mapping:
        raise SystemExit("completion must be one of 0%, 25%, 50%, 75%, 100%")
    return mapping[value]


def date_parts(date_value: str) -> tuple[str, str, str]:
    parsed = datetime.strptime(date_value, "%Y-%m-%d").date()
    iso_year, iso_week, _ = parsed.isocalendar()
    return parsed.isoformat(), f"{iso_year}-W{iso_week:02d}", parsed.strftime("%Y-%m")


def build_fields(args: argparse.Namespace) -> dict:
    date_value = args.date or today()
    day, week, month = date_parts(date_value)
    fields = {
        "复盘标题": f"{day} 日复盘",
        "日期": day,
        "年周": week,
        "月份": month,
        "今日主线任务": args.main_task,
        "今日产出": args.outputs or "",
        "最大时间黑洞": args.time_sink or "",
        "明日主线任务": args.tomorrow_main or "",
        "明日第一步动作": args.tomorrow_first_step or "",
        "一句话结论": args.conclusion or "",
    }
    completion = normalize_completion(args.completion)
    if completion is not None:
        fields["主线完成度"] = completion
    focus = normalize_score(args.focus, "focus")
    energy = normalize_score(args.energy, "energy")
    satisfaction = normalize_score(args.satisfaction, "satisfaction")
    if focus is not None:
        fields["专注评分"] = focus
    if energy is not None:
        fields["能量评分"] = energy
    if satisfaction is not None:
        fields["满意度"] = satisfaction
    if args.distraction:
        fields["最大干扰源"] = args.distraction if args.distraction in DISTRACTIONS else "其他"
    return fields


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-token", default=None, help="Feishu Base token. Defaults to CBTR_BASE_TOKEN or config/local.json.")
    parser.add_argument("--table-id", default=REVIEW_TABLE, help="Base table id or name. Defaults to 每日复盘.")
    parser.add_argument("--date", default=None)
    parser.add_argument("--main-task", required=True)
    parser.add_argument("--completion", default="")
    parser.add_argument("--outputs", default="")
    parser.add_argument("--time-sink", default="")
    parser.add_argument("--distraction", default="")
    parser.add_argument("--tomorrow-main", default="")
    parser.add_argument("--tomorrow-first-step", default="")
    parser.add_argument("--focus", default="")
    parser.add_argument("--energy", default="")
    parser.add_argument("--satisfaction", default="")
    parser.add_argument("--conclusion", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_token = require_value(
        args.base_token or config_value("time_review", "base_token", "CBTR_BASE_TOKEN"),
        "time-review Base token",
        "CBTR_BASE_TOKEN",
    )
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
