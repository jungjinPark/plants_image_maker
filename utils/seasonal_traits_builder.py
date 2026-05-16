from __future__ import annotations

from typing import Dict, List


def build_seasonal_descriptions(plant_name: str, plant_profile: Dict, evergreen: bool | None = None) -> List[str]:
    seasonal = plant_profile.get("seasonal_characteristics") or {}
    winter_interest = plant_profile.get("winter_silhouette") or "가지 구조"
    autumn = plant_profile.get("autumn_color") or "자연스러운 가을 변화"
    leaf_state = plant_profile.get("evergreen") if evergreen is None else evergreen

    return [
        f"{plant_name}: {seasonal.get('winter', '동절기 수형 유지')} ({winter_interest})",
        f"{plant_name}: {seasonal.get('spring', '봄 새순 전개')}",
        f"{plant_name}: {seasonal.get('early_summer', '생장 활발')}",
        f"{plant_name}: {seasonal.get('summer', '수관 확장 및 녹음 형성')}",
        f"{plant_name}: {seasonal.get('autumn', autumn)}",
        (f"{plant_name}: 상록 질감 유지" if leaf_state else f"{plant_name}: {seasonal.get('winter', '낙엽 후 겨울 수형 강조')}") ,
    ]
