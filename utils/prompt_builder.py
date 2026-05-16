from __future__ import annotations

from typing import Dict


def build_image_prompt(base_prompt: str, plant_profile: Dict, season_label: str, season_desc: str, refs_count: int) -> str:
    keywords = ", ".join(plant_profile.get("visual_keywords") or [])
    return (
        f"{base_prompt}\n\n"
        "realistic landscape architecture botanical rendering, Korean landscape architecture board style.\n"
        "Must represent real-world scale, mature size, realistic branching, and actual shrub proportions.\n"
        f"식물명: {plant_profile.get('korean_name')} ({plant_profile.get('scientific_name') or '학명 미상'})\n"
        f"식물 유형: {plant_profile.get('plant_type')} / 상록성: {plant_profile.get('evergreen')}\n"
        f"성숙 크기: H {plant_profile.get('mature_height_cm')}cm, W {plant_profile.get('mature_width_cm')}cm\n"
        f"계절 구간: {season_label}\n"
        f"계절 설명: {season_desc}\n"
        f"생장형: {plant_profile.get('growth_form')}\n"
        f"가지 구조: {plant_profile.get('branching_structure')}\n"
        f"잎 형태: {plant_profile.get('leaf_shape')}\n"
        f"개화 특성: {plant_profile.get('flower_character')} / 개화 시기: {plant_profile.get('flowering_season')}\n"
        f"단풍색: {plant_profile.get('autumn_color')} / 겨울 실루엣: {plant_profile.get('winter_silhouette')}\n"
        f"visual keywords: {keywords}\n"
        f"참고 이미지 수: {refs_count}장 (종 고유 수형과 세부 형태를 최대한 반영)\n"
        "출력 제약: single plant only, no ground, no shadow, no pot, no text, no frame, transparent background PNG."
    )
