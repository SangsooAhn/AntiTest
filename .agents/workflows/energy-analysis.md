---
description: 입력된 기사 및 자료를 분석하고, 기존 누적 지식과 매핑·병합한 뒤 대시보드 및 지식 지도를 자동 갱신하여 Git 저장소에 반영하는 워크플로우입니다.
---

## Steps
1. **기사/보고서 정보 분석 및 요약**
   - 뉴스 기사인 경우: [기사 분석 규칙](.agents/rules/analysis-style.md)에 따라 **사실 관계(Facts)**와 **관점별 명제(Propositions)**를 추출함.
   - 전문 보고서인 경우: [보고서 분석 규칙](.agents/rules/report-style.md)에 따라 동일하게 사실/명제를 구분하여 추출함.
2. **태그 확장 검토**
   - 분석 중 기존 태그 규칙([표준 태그 규칙](.agents/rules/tags.md)) 외에 새로운 핵심 도메인 개념 태그가 필요하다고 판단되면, 스스로 `tags.md` 파일에 설명과 추가 사유를 포함하여 신규 태그를 등록함.
3. **원천 분석 마크다운 생성**
   - 뉴스 기사는 `news/YYYY-MM-DD_기사제목요약.md` 형식으로 저장함.
   - 전문 보고서는 `reports/YYYY-MM-DD_보고서제목요약.md` 형식으로 저장함.
4. **관점별 명제 노트로의 지식 연결 및 병합(Merge)**
   - 지식 지도(Index 노트) 파일([knowledge/README.md](file:///C:/Users/dl/.gemini/antigravity/worktrees/260614_github_news/inspect-repository-files/knowledge/README.md))을 열어 기존 관점별 명제 현황을 학습함.
   - 신규 기사에서 도출된 사실 관계와 명제를 해당 관점 명제 노트(`knowledge/관점명_관점.md`)에 병합함.
   - [지식 통합 가이드라인](.agents/rules/knowledge-style.md)에 따라 사실은 유사 정보 단위 그룹에 일자를 명시해 추가하고, 명제는 키워드 3~5개 내외의 짧은 제목으로 정리하여 보완함.
5. **Index 노트(지식 지도) 자동 업데이트**
   - 파이썬 스크립트 `.agents/scripts/update_index.py`를 실행함.
   - 이 스크립트는 `knowledge/*_관점.md` 파일들의 명제 제목과 최종 갱신일, 사실 개수를 추출하여 [knowledge/README.md](file:///C:/Users/dl/.gemini/antigravity/worktrees/260614_github_news/inspect-repository-files/knowledge/README.md)를 갱신함.
6. **Git 일괄 등록 및 푸시**
   - 생성/수정된 기사 파일, 갱신된 지식 문서, `tags.md`, `knowledge/README.md`를 모두 스테이징함.
   - 커밋 생성 후 원격 저장소(`main` 브랜치)로 즉시 푸시함.