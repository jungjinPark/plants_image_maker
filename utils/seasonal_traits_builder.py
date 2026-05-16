from __future__ import annotations

from typing import Dict, List


def build_seasonal_descriptions(plant_name: str, plant_profile: Dict, evergreen: bool | None = None) -> List[str]:
    seasonal = plant_profile.get("seasonal_growth") or {}
    winter_interest = plant_profile.get("winter_interest") or "가지 구조"
    autumn = plant_profile.get("autumn_characteristics") or "자연스러운 가을 변화"
    leaf_state = plant_profile.get("evergreen") if evergreen is None else evergreen

    return [
        f"{plant_name}: {seasonal.get('1_2', '동절기 수형 유지')} ({winter_interest})",
        f"{plant_name}: {seasonal.get('3_4', '봄 새순 전개')}",
        f"{plant_name}: {seasonal.get('5_6', '생장 활발')}",
        f"{plant_name}: {seasonal.get('7_8', '수관 확장 및 녹음 형성')}",
        f"{plant_name}: {seasonal.get('9_10', autumn)}",
        (f"{plant_name}: 상록 질감 유지" if leaf_state else f"{plant_name}: {seasonal.get('11_12', '낙엽 후 겨울 수형 강조')}") ,
    ]
