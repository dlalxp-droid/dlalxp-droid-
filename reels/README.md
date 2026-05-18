# 보험설계사용 인스타 릴스 자동 제작

손글씨 노트풍 1080×1920 / 15초 / 30fps 릴스 영상을 자동 생성합니다.

## 구조
- `fonts/` — 한글 손글씨 폰트 3종 (Google Fonts, OFL 라이선스)
  - NanumPenScript — 본문/체크리스트
  - GamjaFlower — 대제목/CTA
  - HiMelody — 회색 부연/인용
- `frames/` — 렌더링 중간 산출물 (gitignore)
- `output/` — 완성 MP4 (gitignore)
- `scripts/` — 각 상품별 렌더 스크립트

## 의존성
- Python 3 + Pillow
- ffmpeg
