from __future__ import annotations

from typing import List, Dict


def build_image_prompt(base_prompt: str, plant: Dict, season_label: str, season_desc: str, refs_count: int) -> str:
    return (
        f"{base_prompt}\n\n"
        f"식물명: {plant.get('korean_name')} ({plant.get('scientific_name') or '학명 미상'})\n"
        f"계절 구간: {season_label}\n"
        f"계절 설명: {season_desc}\n"
        f"형태 강조: {plant.get('form_features') or '자연스러운 관목/교목 수형'}\n"
        f"꽃색: {plant.get('flower_color') or '계절 특성에 맞게 자연스럽게'}\n"
        f"참고 이미지 수: {refs_count}장 (전체 수형/잎/꽃/겨울줄기 반영)\n"
        "단일 식물 일러스트만 생성하고 배경 요소/텍스트/프레임은 제외."
    )
