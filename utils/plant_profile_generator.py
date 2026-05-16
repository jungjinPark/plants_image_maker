from __future__ import annotations

import json
import base64
import os
from typing import Any, Dict, List, Optional

import streamlit as st
from openai import OpenAI


REQUIRED_KEYS = [
    "korean_name",
    "scientific_name",
    "plant_type",
    "evergreen",
    "mature_height_cm",
    "mature_width_cm",
    "growth_form",
    "flower_season_months",
    "flower_color",
    "fruit_season_months",
    "autumn_color",
    "winter_feature",
    "pruning_feature",
    "seasonal_morphology",
    "visual_keywords",
]

MORPH_KEYS = ["jan_feb", "mar_apr", "may_jun", "jul_aug", "sep_oct", "nov_dec"]


def _get_openai_api_key() -> str | None:
    try:
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return str(key)
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def _fallback_profile(
    korean_name: str,
    scientific_name: str | None,
    max_h_cm: float,
    max_w_cm: float,
) -> Dict[str, Any]:
    return {
        "korean_name": korean_name,
        "scientific_name": scientific_name or "학명 미상",
        "plant_type": "shrub",
        "evergreen": False,
        "mature_height_cm": int(max_h_cm),
        "mature_width_cm": int(max_w_cm),
        "growth_form": "자연스러운 수형, 예상 성숙 크기 반영",
        "flower_season_months": [5, 6],
        "flower_color": "종 특성 기반",
        "fruit_season_months": [],
        "autumn_color": "자연스러운 계절 색 변화",
        "winter_feature": "가지 실루엣 또는 상록 질감",
        "pruning_feature": "전정 전후 수형 안정",
        "seasonal_morphology": {
            "jan_feb": "동절기 휴면 또는 상록 잎 유지",
            "mar_apr": "봄 신초 및 잎 전개 시작",
            "may_jun": "왕성한 생장과 초기 개화 가능",
            "jul_aug": "최대 잎량 및 수형 확장",
            "sep_oct": "생장 둔화, 결실 또는 단풍 가능",
            "nov_dec": "휴면 진입, 겨울 구조 강조",
        },
        "visual_keywords": [
            korean_name,
            "realistic landscape architecture botanical rendering",
            "actual plant proportions",
            "transparent background",
        ],
    }


def merge_with_db_profile(base_profile: Dict[str, Any], db_record: Dict[str, Any] | None) -> Dict[str, Any]:
    if not db_record:
        return base_profile

    merged = dict(base_profile)
    overrides = {
        "korean_name": db_record.get("korean_name"),
        "scientific_name": db_record.get("scientific_name"),
        "evergreen": db_record.get("evergreen"),
        "flower_color": db_record.get("flower_color"),
        "autumn_color": db_record.get("autumn_color"),
        "winter_feature": db_record.get("winter_interest"),
        "growth_form": db_record.get("form_features"),
    }
    for k, v in overrides.items():
        if v is not None and v != "":
            merged[k] = v

    if db_record.get("flowering_months"):
        merged["flower_season_months"] = db_record["flowering_months"]

    return merged


def _normalize_month_list(value: Any, default: List[int]) -> List[int]:
    if isinstance(value, list):
        nums = [int(m) for m in value if str(m).isdigit() and 1 <= int(m) <= 12]
        return nums or default
    return default


def _normalize_profile(raw: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(fallback)
    for key in REQUIRED_KEYS:
        value = raw.get(key)
        if value is not None and value != "":
            normalized[key] = value

    morph = normalized.get("seasonal_morphology")
    if not isinstance(morph, dict):
        morph = {}
    normalized["seasonal_morphology"] = {
        k: str(morph.get(k) or fallback["seasonal_morphology"][k]) for k in MORPH_KEYS
    }

    if not isinstance(normalized.get("visual_keywords"), list):
        normalized["visual_keywords"] = fallback["visual_keywords"]

    normalized["flower_season_months"] = _normalize_month_list(
        normalized.get("flower_season_months"), fallback["flower_season_months"]
    )
    normalized["fruit_season_months"] = _normalize_month_list(
        normalized.get("fruit_season_months"), fallback["fruit_season_months"]
    )

    allowed_types = {"tree", "shrub", "grass", "perennial", "groundcover"}
    if normalized.get("plant_type") not in allowed_types:
        normalized["plant_type"] = fallback["plant_type"]

    return normalized


def generate_plant_profile(
    korean_name: str,
    scientific_name: str | None,
    max_height_cm: float,
    max_width_cm: float,
    reference_images: Optional[List[bytes]] = None,
    db_record: Dict[str, Any] | None = None,
    model: str = "gpt-4.1-mini",
) -> Dict[str, Any]:
    reference_images = reference_images or []
    fallback = _fallback_profile(korean_name, scientific_name, max_height_cm, max_width_cm)

    api_key = _get_openai_api_key()
    if not api_key:
        st.warning("OPENAI_API_KEY가 없어 fallback 식물 프로필을 사용합니다.")
        return merge_with_db_profile(fallback, db_record)

    try:
        client = OpenAI(api_key=api_key)
        ref_hint = f"참고 이미지 개수: {len(reference_images)}장"
        prompt = (
            "다음 식물 정보를 바탕으로 모든 식물군에 공통 적용 가능한 조경용 식물 프로필 JSON을 작성하세요. "
            "추정이 필요하면 보수적으로 작성하세요.\\n"
            f"- 국명: {korean_name}\\n"
            f"- 학명: {scientific_name or '미입력'}\\n"
            f"- 최대크기: H {max_height_cm}cm, W {max_width_cm}cm\\n"
            f"- {ref_hint}\\n\\n"
            "반드시 아래 키를 포함한 JSON 객체만 반환:\\n"
            + ", ".join(REQUIRED_KEYS)
            + "\\n"
            "제약:\\n"
            "- plant_type은 tree/shrub/grass/perennial/groundcover 중 하나\\n"
            "- flower_season_months, fruit_season_months는 월 숫자 배열(예: [4,5,6])\\n"
            "- seasonal_morphology는 jan_feb, mar_apr, may_jun, jul_aug, sep_oct, nov_dec 키를 모두 포함\\n"
            "- 반드시 strict JSON object만 반환"
        )

        user_content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for img in reference_images[:4]:
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64.b64encode(img).decode('utf-8')}"},
                }
            )

        res = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a botanical and landscape architecture expert. Output strict JSON only."},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = res.choices[0].message.content or "{}"
        ai_profile = json.loads(content)
        normalized = _normalize_profile(ai_profile, fallback)
        return merge_with_db_profile(normalized, db_record)
    except Exception as e:
        st.warning(f"식물 프로필 AI 생성 실패로 fallback 사용: {e}")
        return merge_with_db_profile(fallback, db_record)
