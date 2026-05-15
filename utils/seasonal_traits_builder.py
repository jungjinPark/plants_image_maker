from __future__ import annotations

from typing import Dict, List


def build_seasonal_descriptions(plant_name: str, plant_record: Dict, evergreen: bool | None) -> List[str]:
    flowering = set(plant_record.get("flowering_months") or [])
    autumn_color = plant_record.get("autumn_color") or "보통"
    winter_interest = plant_record.get("winter_interest") or "가지 구조"

    texts = [
        f"{plant_name}: 동절기 수형 유지, {winter_interest} 감상",
        f"{plant_name}: 봄 새순 전개" + (", 개화 시작" if 3 in flowering or 4 in flowering else ""),
        f"{plant_name}: 생장 활발" + (", 개화 절정" if 5 in flowering or 6 in flowering else ""),
        f"{plant_name}: 수관 확장 및 녹음 형성",
        f"{plant_name}: 가을 경관 변화({autumn_color})",
        (f"{plant_name}: 상록 질감 유지" if evergreen else f"{plant_name}: 낙엽 후 {winter_interest} 강조"),
    ]
    return texts
