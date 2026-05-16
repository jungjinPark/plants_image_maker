from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import streamlit as st

from utils.growth_logic import load_growth_db, find_plant_record, SEASON_LABELS
from utils.seasonal_traits_builder import build_seasonal_descriptions
from utils.prompt_builder import build_image_prompt
from utils.image_generator import generate_season_plant_image
from utils.layout_renderer import compose_final_board, load_template

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="식물 계절 생장 이미지 생성기", layout="wide")
st.title("식물 계절 생장 이미지 생성기 (MVP)")

with st.sidebar:
    st.header("입력")
    plant_name = st.text_input("수목명 *")
    scientific_name = st.text_input("학명 (선택)")
    max_h = st.number_input("최대 높이 H(cm) *", min_value=1.0, value=120.0)
    max_w = st.number_input("최대 폭 W(cm) *", min_value=1.0, value=120.0)
    refs = st.file_uploader("참고 이미지 업로드 (jpg/jpeg/png, 다중 선택)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    generate = st.button("생성")

st.subheader("참고 이미지 미리보기")
if refs:
    cols = st.columns(min(4, len(refs)))
    for i, f in enumerate(refs):
        cols[i % len(cols)].image(f, caption=f.name, use_container_width=True)
else:
    st.info("참고 이미지를 업로드하면 썸네일이 표시됩니다. (drag & drop / 클릭 업로드 지원)")

if generate:
    if not plant_name.strip():
        st.error("수목명을 입력해 주세요.")
        st.stop()

    db = load_growth_db(str(ROOT / "data" / "plant_growth_rules.yaml"))
    record = find_plant_record(db, plant_name.strip(), scientific_name.strip() or None) or {}
    record.update({
        "korean_name": plant_name.strip(),
        "scientific_name": scientific_name.strip() or record.get("scientific_name"),
        "max_height_cm": max_h,
        "max_width_cm": max_w,
    })

    season_texts = build_seasonal_descriptions(plant_name.strip(), record, record.get("evergreen"))
    base_prompt = (ROOT / "prompts" / "seasonal_prompt.txt").read_text(encoding="utf-8")
    ref_bytes = [f.getvalue() for f in refs] if refs else []

    season_images = []
    prompt_log = {}
    for idx, label in enumerate(SEASON_LABELS):
        prompt = build_image_prompt(base_prompt, record, label, season_texts[idx], len(ref_bytes))
        prompt_log[f"season_{idx+1:02d}"] = prompt
        img = generate_season_plant_image(prompt, ref_bytes)
        season_images.append(img)
        img.save(OUTPUT_DIR / f"season_{idx+1:02d}.png")

    template = load_template(str(ROOT / "assets" / "blank_template.png"))
    # 사람 실루엣은 blank_template.png 안에 이미 포함되어 있으므로
# 별도 person_silhouette.png를 사용하지 않는다.
final_img = compose_final_board(
    template,
    None,
    season_images,
    SEASON_LABELS,
    season_texts,
    max_h,
    max_w,
)

ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
out_png = OUTPUT_DIR / f"seasonal_board_{ts}.png"
out_prompt = OUTPUT_DIR / f"prompts_{ts}.txt"
out_history = OUTPUT_DIR / "history.jsonl"

final_img.save(out_png)
out_prompt.write_text("\n\n".join([f"[{k}]\n{v}" for k, v in prompt_log.items()]), encoding="utf-8")

with open(out_history, "a", encoding="utf-8") as f:
    f.write(json.dumps({
        "timestamp": ts,
        "plant": record,
        "output": out_png.name
    }, ensure_ascii=False) + "\n")

st.subheader("최종 결과")
st.image(str(out_png), caption=out_png.name, use_container_width=True)

with open(out_png, "rb") as f:
    st.download_button(
        "PNG 다운로드",
        data=f,
        file_name=out_png.name,
        mime="image/png"
    )
