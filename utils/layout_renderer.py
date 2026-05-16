from __future__ import annotations

from pathlib import Path
from typing import Dict, List
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


def _season_growth_scale(plant_profile: Dict, season_idx: int) -> float:
    plant_type = plant_profile.get("plant_type")
    evergreen = bool(plant_profile.get("evergreen"))
    flower_months = set(plant_profile.get("flower_season_months") or [])
    season_months = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)][season_idx]
    in_flower = any(m in flower_months for m in season_months)

    if plant_type == "tree":
        return 1.0
    if plant_type == "groundcover":
        return [0.8, 0.88, 0.95, 1.0, 0.95, 0.85][season_idx] if evergreen else [0.6, 0.75, 0.9, 1.0, 0.9, 0.7][season_idx]
    if plant_type == "grass":
        return [0.45, 0.6, 0.8, 0.95, 1.0, 0.6][season_idx]
    if plant_type == "perennial":
        return [0.3, 0.6, 0.9, 1.0, 0.85, 0.35][season_idx]
    # shrub (default): 낙엽관목 겨울 80~90, 봄 60~80, 개화기 100 반영
    base = [0.85, 0.7, 0.92, 0.95, 0.9, 0.82] if not evergreen else [0.9, 0.92, 0.98, 1.0, 0.97, 0.9]
    if in_flower:
        return 1.0
    return base[season_idx]


def compose_final_board(
    template: Image.Image,
    person_path: str | None,
    season_images: List[Image.Image],
    season_labels: List[str],
    season_texts: List[str],
    plant_h_cm: float,
    plant_w_cm: float,
    plant_profile: Dict,
) -> Image.Image:
    canvas = template.copy()
    draw = ImageDraw.Draw(canvas)

    ratio = plant_h_cm / 175.0
    person_px_h = 520
    plant_px_h = max(80, min(900, int(person_px_h * ratio)))
    plant_px_w = max(80, int(plant_px_h * max(0.3, min(2.5, plant_w_cm / max(plant_h_cm, 1)))))

    for i, box in enumerate(SEASON_BOXES):
        x1, y1, x2, y2 = box
        img = season_images[i].copy().convert("RGBA")

        growth_scale = _season_growth_scale(plant_profile, i)
        season_h = max(60, int(plant_px_h * growth_scale))
        season_w = max(60, int(plant_px_w * growth_scale))

        max_w = x2 - x1 - 20
        max_h = y2 - y1 - 155
        scale = min(max_w / max(season_w, 1), max_h / max(season_h, 1))
        target_w = max(60, int(season_w * scale))
        target_h = max(60, int(season_h * scale))

        img = img.resize((target_w, target_h))
        ix = x1 + ((x2 - x1 - img.width) // 2)
        iy = y2 - 180 - img.height
        canvas.alpha_composite(img, (ix, iy))

        draw.multiline_text((x1 + 10, y2 - 120), season_texts[i], fill=(30, 30, 30), font=_font(18), spacing=4)

    return canvas
