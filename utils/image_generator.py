from __future__ import annotations

import base64
import io
import os
from typing import List

import streamlit as st
from PIL import Image, ImageDraw
from openai import OpenAI


def _placeholder_image(size=(640, 640), label: str = "SEASON") -> Image.Image:
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((120, 100, 520, 580), fill=(129, 164, 122, 180))
    draw.text((30, 30), f"Placeholder {label}", fill=(70, 70, 70, 255))
    return img


def _get_openai_api_key() -> str | None:
    try:
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return str(key)
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def generate_season_plant_image(
    prompt: str,
    reference_images: List[bytes],
    model: str = "gpt-image-1",
) -> Image.Image:
    api_key = _get_openai_api_key()

    if not api_key:
        st.warning("OPENAI_API_KEY가 설정되지 않아 placeholder 이미지를 사용합니다.")
        return _placeholder_image(label="NO API KEY")

    try:
        client = OpenAI(api_key=api_key)

        result = client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
        )

        img_base64 = result.data[0].b64_json
        img_bytes = base64.b64decode(img_base64)
        return Image.open(io.BytesIO(img_bytes)).convert("RGBA")

    except Exception as e:
        st.error(f"이미지 생성 실패: {e}")
        return _placeholder_image(label="API ERROR")
