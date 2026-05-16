from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import streamlit as st
from openai import OpenAI


REQUIRED_KEYS = [
    "korean_name",
    "scientific_name",
    "evergreen",
    "form",
    "branch_structure",
    "leaf_shape",
    "flowering_period",
    "flower_color",
    "has_fruit",
    "autumn_characteristics",
    "winter_interest",
    "seasonal_growth",
    "visual_keywords",
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
        "form": f"자연스러운 수형, 예상 성숙 크기 H {int(max_h_cm)}cm / W {int(max_w_cm)}cm",
        "branch_structure": "중심 줄기와 자연 분지 구조",
        "leaf_shape": "종 특성에 맞는 일반적인 잎 형태",
        "flowering_period": "봄~여름 가능성",
        "flower_color": "식물 고유 색",
        "has_fruit": None,
        "autumn_characteristics": "계절 변화에 따른 자연스러운 색 변화",
        "winter_interest": "가지 실루엣 또는 상록 질감",
        "seasonal_growth": {
            "1_2": "휴면기 또는 생장 둔화",
            "3_4": "새순 전개 시작",
            "5_6": "생장 활발 및 개화 가능",
            "7_8": "수관 확장 및 잎 밀도 증가",
            "9_10": "가을 색 변화 및 생장 안정화",
            "11_12": "낙엽 또는 상록 질감 유지",
        },
        "visual_keywords": [
            korean_name,
            "botanical illustration",
            "single plant",
            "transparent background",
            "seasonal change",
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
        "has_fruit": db_record.get("fruit"),
        "autumn_characteristics": db_record.get("autumn_color"),
        "winter_interest": db_record.get("winter_interest"),
        "form": db_record.get("form_features"),
    }
    for k, v in overrides.items():
        if v is not None and v != "":
            merged[k] = v

    if db_record.get("flowering_months"):
        months = db_record["flowering_months"]
        merged["flowering_period"] = f"{min(months)}~{max(months)}월"

    return merged


def _normalize_profile(raw: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(fallback)
    for key in REQUIRED_KEYS:
        value = raw.get(key)
        if value is not None and value != "":
            normalized[key] = value

    if not isinstance(normalized.get("seasonal_growth"), dict):
        normalized["seasonal_growth"] = fallback["seasonal_growth"]

    if not isinstance(normalized.get("visual_keywords"), list):
        normalized["visual_keywords"] = fallback["visual_keywords"]

    return normalized


def generate_plant_profile(
    korean_name: str,
    scientific_name: str | None,
    max_h_cm: float,
    max_w_cm: float,
    reference_images: List[bytes],
    db_record: Dict[str, Any] | None = None,
    model: str = "gpt-4.1-mini",
) -> Dict[str, Any]:
    fallback = _fallback_profile(korean_name, scientific_name, max_h_cm, max_w_cm)

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
            f"- 최대크기: H {max_h_cm}cm, W {max_w_cm}cm\n"
            f"- {ref_hint}\n\n"
            "반드시 아래 키를 포함한 JSON 객체만 반환:\n"
            + ", ".join(REQUIRED_KEYS)
            + "\n"
            "seasonal_growth는 1_2,3_4,5_6,7_8,9_10,11_12 키를 가진 객체, "
            "visual_keywords는 문자열 리스트로 작성."
        )

        res = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a botanically informed landscape assistant. Return strict JSON only."},
                {"role": "user", "content": prompt},
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
