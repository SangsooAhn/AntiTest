---
description: 입력된 기사 및 자료(보고서 등)를 분석하고, 지식을 대시보드에 자동 갱신하여 Git 저장소에 누적하는 워크플로우입니다.
---

## Steps
1. **기사/보고서 컨텍스트 수집 및 스크래핑**
2. **콘텐츠 분석 및 규칙 검증**
   - 뉴스 기사인 경우: [기사 분석 규칙](.agents/rules/analysis-style.md) 및 [표준 태그 규칙](.agents/rules/tags.md) 참조
   - 전문 보고서/자료인 경우: [보고서 분석 규칙](.agents/rules/report-style.md) 및 [표준 태그 규칙](.agents/rules/tags.md) 참조
3. **마크다운 파일 생성**
   - 뉴스 기사: `news/YYYY-MM-DD_기사제목요약.md` 형식으로 저장
   - 전문 보고서: `reports/YYYY-MM-DD_보고서제목요약.md` 형식으로 저장
4. **인덱스 자동 갱신 스크립트 실행**
   - 파이썬 스크립트 `.agents/scripts/update_index.py`를 실행하여 대시보드(`README.md`) 자동 갱신
5. **Git 스테이징, 자동 커밋 및 원격 저장소 푸시**
   - 분석 마크다운 파일과 업데이트된 `README.md`를 스테이징(`git add`)
   - 커밋 생성 및 푸시 수행