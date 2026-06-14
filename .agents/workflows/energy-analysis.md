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
4. **지식 연결 및 병합(Merge)**
   - **인덱스 조회**: 추가하려는 관점의 개별 인덱스 노트(`knowledge/indexes/주체.md`)를 조회하여 기존 명제들의 제목과 성격별 분류를 확인함.
   - **명제 병합**: 신규 명제 중 기존 것과 유사한 명제가 이미 해당 인덱스 노트에 리스팅되어 있을 경우, 명제 상세 노트(`knowledge/propositions/주체.md`) 업데이트는 생략(Skip)함. 기존에 없던 명제일 경우에만 명제 상세 노트를 열어 해당 카테고리 헤더 아래에 대괄호 제목 형태(`#### [제목]`)와 상세 내용을 추가함.
   - **사실관계 병합**: 기사의 사실관계를 해당 중요 개념 Facts 파일(`knowledge/facts/개념명.md`)의 유사 정보 그룹 아래에 일자(`-[YYYY-MM-DD]`)를 명시해 시간순으로 병합함.
5. **Index 노트 및 지식 지도 자동 업데이트**
   - 파이썬 스크립트 `.agents/scripts/update_index.py`를 실행함.
   - 이 스크립트는 `knowledge/propositions/*.md` 파일들의 카테고리와 명제 제목 구조를 파싱하여 개별 인덱스 노트(`knowledge/indexes/*.md`)와 마스터 지식 지도([knowledge/README.md](file:///C:/Users/dl/.gemini/antigravity/worktrees/260614_github_news/inspect-repository-files/knowledge/README.md))를 자동으로 생성 및 갱신함.

6. **Git 일괄 등록 및 푸시**
   - 생성/수정된 기사 파일, 갱신된 지식 문서, `tags.md`, `knowledge/README.md`를 모두 스테이징함.
   - 커밋 생성 후 원격 저장소(`main` 브랜치)로 즉시 푸시함.