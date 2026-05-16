from __future__ import annotations

from typing import Dict

SEASON_TO_MORPH = {
    "1~2월": "jan_feb",
    "3~4월": "mar_apr",
    "5~6월": "may_jun",
    "7~8월": "jul_aug",
    "9~10월": "sep_oct",
    "11~12월": "nov_dec",
}


def build_image_prompt(base_prompt: str, plant_profile: Dict, season_label: str, season_desc: str, refs_count: int) -> str:
    keywords = ", ".join(plant_profile.get("visual_keywords") or [])
    morph_key = SEASON_TO_MORPH.get(season_label, "")
    season_morph = (plant_profile.get("seasonal_morphology") or {}).get(morph_key, season_desc)
    return (
        f"{base_prompt}\n\n"
        "realistic landscape architecture botanical rendering, Korean landscape architecture board style.\n"
        "Must represent real-world scale, mature size, realistic branching, and actual plant proportions.\n"
        f"식물명: {plant_profile.get('korean_name')} ({plant_profile.get('scientific_name') or '학명 미상'})\n"
        f"식물 유형: {plant_profile.get('plant_type')} / 상록성: {plant_profile.get('evergreen')}\n"
        f"성숙 크기: H {plant_profile.get('mature_height_cm')}cm, W {plant_profile.get('mature_width_cm')}cm\n"
        f"계절 구간: {season_label}\n"
        f"계절 morphology(필수): {season_morph}\n"
        f"계절 설명: {season_desc}\n"
        f"생장형: {plant_profile.get('growth_form')}\n"
        f"개화 월: {plant_profile.get('flower_season_months')} / 개화색: {plant_profile.get('flower_color')}\n"
        f"결실 월: {plant_profile.get('fruit_season_months')}\n"
        f"단풍색: {plant_profile.get('autumn_color')} / 겨울 특징: {plant_profile.get('winter_feature')}\n"
        f"전정 특징: {plant_profile.get('pruning_feature')}\n"
        f"visual keywords: {keywords}\n"
        f"참고 이미지 수: {refs_count}장\n"
        "출력 제약: single plant only, no ground, no shadow, no pot, no text, no frame, transparent background PNG."
    )
