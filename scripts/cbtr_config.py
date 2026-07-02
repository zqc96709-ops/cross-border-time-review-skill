#!/usr/bin/env python3
"""Local private configuration helpers for cross-border-time-review scripts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _config_paths() -> list[Path]:
    paths: list[Path] = []
    env_path = os.environ.get("CBTR_CONFIG")
    if env_path:
        paths.append(Path(env_path).expanduser())
    paths.append(Path(__file__).resolve().parents[1] / "config" / "local.json")
    return paths


def load_config() -> dict[str, Any]:
    for path in _config_paths():
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise SystemExit(f"Config file must contain a JSON object: {path}")
            return data
    return {}


def config_value(section: str, key: str, env_var: str, default: str = "") -> str:
    env_value = os.environ.get(env_var)
    if env_value:
        return env_value
    section_value = load_config().get(section, {})
    if isinstance(section_value, dict):
        value = section_value.get(key)
        if value:
            return str(value)
    return default


def require_value(value: str, label: str, env_var: str) -> str:
    if value:
        return value
    raise SystemExit(
        f"Missing {label}. Set {env_var}, pass the related CLI argument, "
        "or create config/local.json from config/local.example.json."
    )
