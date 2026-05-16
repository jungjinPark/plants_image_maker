from __future__ import annotations

from typing import List, Dict


def build_image_prompt(base_prompt: str, plant_profile: Dict, season_label: str, season_desc: str, refs_count: int) -> str:
    keywords = ", ".join(plant_profile.get("visual_keywords") or [])
    return (
        f"{base_prompt}\n\n"
        f"식물명: {plant_profile.get('korean_name')} ({plant_profile.get('scientific_name') or '학명 미상'})\n"
        f"계절 구간: {season_label}\n"
        f"계절 설명: {season_desc}\n"
        f"낙엽/상록: {plant_profile.get('evergreen')}\n"
        f"수형: {plant_profile.get('form')}\n"
        f"가지 구조: {plant_profile.get('branch_structure')}\n"
        f"잎 형태: {plant_profile.get('leaf_shape')}\n"
        f"개화시기: {plant_profile.get('flowering_period')} / 꽃 색: {plant_profile.get('flower_color')}\n"
        f"단풍 특성: {plant_profile.get('autumn_characteristics')} / 겨울 감상: {plant_profile.get('winter_interest')}\n"
        f"visual keywords: {keywords}\n"
        f"참고 이미지 수: {refs_count}장 (전체 수형/잎/꽃/겨울줄기 반영)\n"
        "단일 식물 일러스트만 생성하고 배경 요소/텍스트/프레임은 제외."
    )
