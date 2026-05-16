from __future__ import annotations

from typing import Dict, List

MORPH_ORDER = ["jan_feb", "mar_apr", "may_jun", "jul_aug", "sep_oct", "nov_dec"]


def build_seasonal_descriptions(plant_name: str, plant_profile: Dict) -> List[str]:
    morphology = plant_profile.get("seasonal_morphology") or {}
    result: List[str] = []
    for key in MORPH_ORDER:
        text = morphology.get(key) or "계절 형태 정보 없음"
        result.append(f"{plant_name}: {text}")
    return result
