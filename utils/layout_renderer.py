from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = (2200, 1100)
SEASON_BOXES = [
    (760, 90, 990, 760),
    (1010, 90, 1240, 760),
    (1260, 90, 1490, 760),
    (1510, 90, 1740, 760),
    (1760, 90, 1990, 760),
    (2010, 90, 2190, 760),
]


def load_template(path: str) -> Image.Image:
    p = Path(path)
    if p.exists():
        return Image.open(path).convert("RGBA").resize(CANVAS_SIZE)
    return Image.new("RGBA", CANVAS_SIZE, "white")


def _font(size: int):
    try:
        return ImageFont.truetype("assets/fonts/NotoSansKR-Regular.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def compose_final_board(
    template: Image.Image,
    person_path: str | None,
    season_images: List[Image.Image],
    season_labels: List[str],
    season_texts: List[str],
    plant_h_cm: float,
    plant_w_cm: float,
) -> Image.Image:
    canvas = template.copy()
    draw = ImageDraw.Draw(canvas)

    # 템플릿에 이미 사람 실루엣과 월 구분선이 포함되어 있으므로
    # 별도 제목, 사람 이미지, 사람 누락 박스는 그리지 않는다.

    ratio = plant_h_cm / 175.0
    person_px_h = 520  # 템플릿 내 1.75m 사람 기준 높이
    plant_px_h = int(person_px_h * ratio)
    plant_px_h = max(60, min(760, plant_px_h))
    plant_px_w = max(
        60,
        int(plant_px_h * max(0.3, min(2.5, plant_w_cm / max(plant_h_cm, 1))))
    )

    for i, box in enumerate(SEASON_BOXES):
        x1, y1, x2, y2 = box

        # 템플릿에 월 제목과 구분선이 이미 있으므로 박스는 다시 그리지 않는다.
        img = season_images[i].copy().convert("RGBA")

        # 식물 높이를 사람 기준으로 조정하되, 각 계절 칸 안에 들어가도록 제한
        max_w = x2 - x1 - 30
        max_h = y2 - y1 - 170
        target_h = min(plant_px_h, max_h)
        target_w = min(plant_px_w, max_w)

        img.thumbnail((target_w, target_h))

        ix = x1 + ((x2 - x1 - img.width) // 2)
        iy = y2 - 180 - img.height
        canvas.alpha_composite(img, (ix, iy))

        draw.multiline_text(
            (x1 + 10, y2 - 120),
            season_texts[i],
            fill=(30, 30, 30),
            font=_font(18),
            spacing=4,
        )

    return canvas
