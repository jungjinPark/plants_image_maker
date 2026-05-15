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


def compose_final_board(template: Image.Image, person_path: str, season_images: List[Image.Image], season_labels: List[str], season_texts: List[str], plant_h_cm: float, plant_w_cm: float) -> Image.Image:
    canvas = template.copy()
    draw = ImageDraw.Draw(canvas)

    draw.text((40, 30), "식물 계절 생장 인포그래픽", fill="black", font=_font(36))

    person = None
    if Path(person_path).exists():
        person = Image.open(person_path).convert("RGBA")
    if person:
        person = person.resize((220, 520))
        canvas.alpha_composite(person, (120, 260))
    else:
        draw.rectangle((120, 260, 340, 780), outline="gray", width=3)
        draw.text((130, 520), "person\nsilhouette\nmissing", fill="gray", font=_font(18))

    ratio = plant_h_cm / 175.0
    plant_px_h = int(520 * ratio)
    plant_px_h = max(100, min(760, plant_px_h))
    plant_px_w = max(80, int(plant_px_h * max(0.3, min(2.5, plant_w_cm / max(plant_h_cm, 1)))))
    draw.rectangle((410, 780 - plant_px_h, 410 + plant_px_w, 780), outline=(70, 140, 70), width=4)
    draw.text((410, 800), f"최대 H {plant_h_cm:.0f}cm / W {plant_w_cm:.0f}cm", fill="black", font=_font(22))

    for i, box in enumerate(SEASON_BOXES):
        x1, y1, x2, y2 = box
        draw.rectangle(box, outline=(200, 200, 200), width=2)
        img = season_images[i].copy().convert("RGBA")
        img.thumbnail((x2 - x1 - 20, y2 - y1 - 160))
        ix = x1 + ((x2 - x1 - img.width) // 2)
        canvas.alpha_composite(img, (ix, y1 + 35))
        draw.text((x1 + 10, y1 + 8), season_labels[i], fill="black", font=_font(24))
        draw.multiline_text((x1 + 10, y2 - 110), season_texts[i], fill=(30, 30, 30), font=_font(18), spacing=4)

    return canvas
