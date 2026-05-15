from __future__ import annotations

import base64
import io
from typing import List
from PIL import Image, ImageDraw
from openai import OpenAI


def _placeholder_image(size=(640, 640), label: str = "SEASON") -> Image.Image:
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((120, 100, 520, 580), fill=(129, 164, 122, 180))
    draw.text((30, 30), f"Placeholder {label}", fill=(70, 70, 70, 255))
    return img


def generate_season_plant_image(prompt: str, reference_images: List[bytes], model: str = "gpt-image-1") -> Image.Image:
    try:
        client = OpenAI()
        input_items = [{"type": "input_text", "text": prompt}]
        for b in reference_images:
            input_items.append({"type": "input_image", "image_base64": base64.b64encode(b).decode("utf-8")})

        result = client.responses.create(model=model, input=[{"role": "user", "content": input_items}])
        for out in result.output:
            for c in getattr(out, "content", []):
                if getattr(c, "type", "") == "output_image":
                    img_bytes = base64.b64decode(c.image_base64)
                    return Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    except Exception:
        pass
    return _placeholder_image(label="API/KEY")
