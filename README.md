# plant-seasonal-board (MVP)

Streamlit 기반 **식물 계절 생장 이미지 생성기**입니다.

## 설치 방법
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 실행 방법
```bash
streamlit run app.py
```

## OpenAI API KEY 설정
```bash
export OPENAI_API_KEY="your_api_key"
```
- API 키가 없거나 생성 실패 시, 앱은 중단되지 않고 placeholder 계절 이미지를 사용합니다.

## 핵심 동작 원칙
- AI는 **계절별 식물 이미지 6장만 생성**
- 최종 포스터는 `assets/blank_template.png` + 계절 이미지 + 텍스트를 **Pillow 합성**
- 전체 포스터를 AI가 한 번에 생성하지 않음

## assets 설명
- `assets/blank_template.png`: 고정 레이아웃 템플릿
- `assets/style_reference.png`: 스타일 참고
- `assets/person_silhouette.png`: 175cm 기준 사람 실루엣(없어도 앱 동작, 대체 표시)
- `assets/fonts/`: 한글 폰트(선택)

## 프로젝트 구조
- `app.py`: Streamlit UI + 전체 파이프라인 실행
- `data/plant_growth_rules.yaml`: 내부 YAML 식물 규칙 DB
- `prompts/seasonal_prompt.txt`: 계절 이미지 생성 기본 프롬프트
- `utils/image_generator.py`: OpenAI 이미지 생성(실패 시 placeholder)
- `utils/layout_renderer.py`: 고정 템플릿 기준 PIL 합성
- `utils/growth_logic.py`: 식물 DB 로드/조회
- `utils/seasonal_traits_builder.py`: 계절 설명 텍스트 생성
- `utils/prompt_builder.py`: 계절별 이미지 프롬프트 조합
- `utils/plant_info_normalizer.py`: 표준 구조 DTO
- `utils/plant_sources/*.py`: RHS/산림청/국립수목원 확장 stub
- `outputs/`: 결과 PNG, 프롬프트 로그, 히스토리

## 향후 확장 방법
1. `utils/plant_sources/`에 실제 API/크롤러 구현
2. 소스별 결과를 `plant_info_normalizer.py` 표준 스키마로 통합
3. 스타일팩(`styles/*`)별 프롬프트 프리셋 추가
4. 식물별 생성 캐시 키(국명+학명+H/W+참고이미지 해시) 적용
