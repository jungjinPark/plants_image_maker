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
    "evergreen",
    "plant_type",
    "growth_form",
    "branching_structure",
    "leaf_shape",
    "flower_character",
    "flowering_season",
    "autumn_color",
    "winter_silhouette",
    "mature_height_cm",
    "mature_width_cm",
    "visual_keywords",
    "seasonal_characteristics",
]


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
        "evergreen": None,
        "plant_type": "shrub",
        "growth_form": "자연스러운 수형, 예상 성숙 크기 반영",
        "branching_structure": "중심 줄기 및 자연 분지 구조",
        "leaf_shape": "종 특성에 맞는 일반적인 잎 형태",
        "flower_character": "종 특성 기반 개화 양상",
        "flowering_season": "spring_to_summer",
        "autumn_color": "자연스러운 계절 색 변화",
        "winter_silhouette": "가지 실루엣 또는 상록 질감",
        "mature_height_cm": int(max_h_cm),
        "mature_width_cm": int(max_w_cm),
        "visual_keywords": [
            korean_name,
            "realistic landscape architecture botanical rendering",
            "actual shrub proportions",
            "transparent background",
        ],
        "seasonal_characteristics": {
            "spring": "새순 발아 및 연한 잎 전개",
            "early_summer": "생장 활발, 잎 밀도 증가",
            "summer": "최대 잎량과 안정적인 수형",
            "autumn": "단풍 및 생장 둔화",
            "winter": "낙엽 후 골격 또는 상록 유지",
        },
    }


def merge_with_db_profile(base_profile: Dict[str, Any], db_record: Dict[str, Any] | None) -> Dict[str, Any]:
    if not db_record:
        return base_profile

    merged = dict(base_profile)
    overrides = {
        "korean_name": db_record.get("korean_name"),
        "scientific_name": db_record.get("scientific_name"),
        "evergreen": db_record.get("evergreen"),
        "flower_character": db_record.get("flower_color"),
        "autumn_color": db_record.get("autumn_color"),
        "winter_silhouette": db_record.get("winter_interest"),
        "growth_form": db_record.get("form_features"),
    }
    for k, v in overrides.items():
        if v is not None and v != "":
            merged[k] = v

    if db_record.get("flowering_months"):
        months = db_record["flowering_months"]
        merged["flowering_season"] = f"{min(months)}~{max(months)}월"

    return merged


def _normalize_profile(raw: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(fallback)
    for key in REQUIRED_KEYS:
        value = raw.get(key)
        if value is not None and value != "":
            normalized[key] = value

    if not isinstance(normalized.get("seasonal_characteristics"), dict):
        normalized["seasonal_characteristics"] = fallback["seasonal_characteristics"]

    if not isinstance(normalized.get("visual_keywords"), list):
        normalized["visual_keywords"] = fallback["visual_keywords"]

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
            "다음 식물 정보를 바탕으로 조경용 계절 일러스트 생성에 필요한 식물 프로필 JSON을 작성하세요. "
            "모르면 추정하되 보수적으로 작성하세요.\n"
            f"- 국명: {korean_name}\n"
            f"- 학명: {scientific_name or '미입력'}\n"
            f"- 최대크기: H {max_height_cm}cm, W {max_width_cm}cm\n"
            f"- {ref_hint}\n\n"
            "반드시 아래 키를 포함한 JSON 객체만 반환:\n"
            + ", ".join(REQUIRED_KEYS)
            + "\n"
            "seasonal_characteristics는 spring/early_summer/summer/autumn/winter 키를 가진 객체로 작성. "
            "식물형은 tree/shrub/grass/perennial/groundcover 중 하나. "
            "반드시 strict JSON object만 반환."
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
