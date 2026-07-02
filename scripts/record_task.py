#!/usr/bin/env python3
"""Create or update one task in the Feishu Base named 个人任务看板."""

from __future__ import annotations

import argparse
import json
import subprocess

from cbtr_config import config_value, require_value

TASK_TABLE = config_value("task", "table_id", "CBTR_TASK_TABLE_ID")
STATUSES = ["未开始", "进行中", "已完成"]
CATEGORIES = ["学习", "生活", "工作"]
LABELS = ["🔥 重要紧急", "📌 重要不紧急", "🤣 不重要紧急", "👇 不重要不紧急"]


def run_lark(args: list[str]) -> dict:
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"lark-cli failed: {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


def normalize_option(value: str, valid: list[str], field: str) -> str:
    value = value.strip()
    if value in valid:
        return value
    compact = value.replace(" ", "")
    for item in valid:
        if compact == item.replace(" ", "") or compact in item.replace(" ", ""):
            return item
    raise SystemExit(f"{field} must be one of: {', '.join(valid)}")


def build_fields(args: argparse.Namespace) -> dict:
    fields = {
        "任务名称": args.name.strip(),
        "状态": normalize_option(args.status, STATUSES, "status"),
        "任务类别": normalize_option(args.category, CATEGORIES, "category"),
        "任务标签": normalize_option(args.label, LABELS, "label"),
    }
    if args.detail:
        fields["任务详情"] = args.detail
    return fields


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-token", default=None, help="Defaults to CBTR_TASK_BASE_TOKEN or config/local.json.")
    parser.add_argument("--table-id", default=TASK_TABLE)
    parser.add_argument("--record-id", default="", help="When set, update an existing task.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--status", default="未开始")
    parser.add_argument("--category", default="工作")
    parser.add_argument("--label", default="📌 重要不紧急")
    parser.add_argument("--detail", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_token = require_value(
        args.base_token or config_value("task", "base_token", "CBTR_TASK_BASE_TOKEN"),
        "task Base token",
        "CBTR_TASK_BASE_TOKEN",
    )
    table_id = require_value(args.table_id, "task table ID", "CBTR_TASK_TABLE_ID")
    fields = build_fields(args)
    payload = {"base_token": base_token, "table_id": table_id, "record_id": args.record_id, "fields": fields}
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    command = [
        "lark-cli", "base", "+record-upsert",
        "--as", "user",
        "--base-token", base_token,
        "--table-id", table_id,
        "--json", json.dumps(fields, ensure_ascii=False),
        "--format", "json",
    ]
    if args.record_id:
        command.extend(["--record-id", args.record_id])
    result = run_lark(command)
    print(json.dumps({"ok": True, "table": table_id, "record_id": args.record_id, "fields": fields, "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
