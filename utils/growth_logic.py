from __future__ import annotations

from typing import Any, Dict
import yaml


SEASON_LABELS = [
    "1~2월",
    "3~4월",
    "5~6월",
    "7~8월",
    "9~10월",
    "11~12월",
]


def load_growth_db(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def find_plant_record(db: Dict[str, Any], korean_name: str, scientific_name: str | None = None) -> Dict[str, Any] | None:
    for p in db.get("plants", []):
        if p.get("korean_name") == korean_name:
            return p
        if scientific_name and p.get("scientific_name") == scientific_name:
            return p
    return None
