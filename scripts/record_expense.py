#!/usr/bin/env python3
"""Create one expense record in the Feishu Base named 费用明细."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from cbtr_config import config_value, require_value

EXPENSE_TABLE = config_value("expense", "table_id", "CBTR_EXPENSE_TABLE_ID")
TIMEZONE = ZoneInfo("Asia/Shanghai")
PAYMENT_METHODS = ["蓝胖子", "欧易", "招商信用卡", "支付宝"]
CURRENCIES = ["¥", "$"]


def run_lark(args: list[str]) -> dict:
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"lark-cli failed: {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


def today_md() -> str:
    now = datetime.now(TIMEZONE)
    return f"{now.month}.{now.day}"


def normalize_payment(value: str) -> str:
    value = value.strip()
    if value not in PAYMENT_METHODS:
        raise SystemExit(f"payment must be one of: {', '.join(PAYMENT_METHODS)}")
    return value


def normalize_currency(value: str) -> str:
    value = value.strip()
    if value in {"人民币", "rmb", "cny", "元"}:
        return "¥"
    if value in {"usd", "美元", "美金"}:
        return "$"
    if value not in CURRENCIES:
        raise SystemExit("currency must be ¥ or $")
    return value


def build_fields(args: argparse.Namespace) -> dict:
    fields = {
        "服务/平台": args.item.strip(),
        "日期": args.date or today_md(),
        "金额": float(args.amount),
        "支付方式": normalize_payment(args.payment),
        "货币": normalize_currency(args.currency),
    }
    if args.note:
        fields["备注"] = args.note
    if args.renewal_due:
        fields["续费截止日"] = args.renewal_due
    return fields


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-token", default=None, help="Defaults to CBTR_EXPENSE_BASE_TOKEN or config/local.json.")
    parser.add_argument("--table-id", default=EXPENSE_TABLE)
    parser.add_argument("--item", required=True, help="服务/平台")
    parser.add_argument("--date", default="", help="M.D, e.g. 7.2. Defaults to today in Asia/Shanghai.")
    parser.add_argument("--amount", required=True)
    parser.add_argument("--payment", required=True, help="蓝胖子/欧易/招商信用卡/支付宝")
    parser.add_argument("--currency", default="¥")
    parser.add_argument("--note", default="")
    parser.add_argument("--renewal-due", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_token = require_value(
        args.base_token or config_value("expense", "base_token", "CBTR_EXPENSE_BASE_TOKEN"),
        "expense Base token",
        "CBTR_EXPENSE_BASE_TOKEN",
    )
    table_id = require_value(args.table_id, "expense table ID", "CBTR_EXPENSE_TABLE_ID")
    fields = build_fields(args)
    payload = {"base_token": base_token, "table_id": table_id, "fields": fields}
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    result = run_lark([
        "lark-cli", "base", "+record-upsert",
        "--as", "user",
        "--base-token", base_token,
        "--table-id", table_id,
        "--json", json.dumps(fields, ensure_ascii=False),
        "--format", "json",
    ])
    print(json.dumps({"ok": True, "table": table_id, "fields": fields, "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
