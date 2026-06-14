---
trigger: always_on
---

# 분산에너지 지식 통합 및 누적(Merge) 가이드라인

## 1. 활성화 조건
- Always On (지식 통합 및 누적 문서 생성 및 수정 시 항시 적용)

## 2. 파일 생성 및 저장 규칙

### A. 명제 노트 (Propositions)
- 명제 노트는 각 이해관계자 주체별로 단일화하여 `knowledge/propositions/` 폴더에 저장 및 누적한다. (파일명에서 "관점" 단어는 배제한다.)
  - `knowledge/propositions/국가.md`
  - `knowledge/propositions/사업자.md`
  - `knowledge/propositions/소비자.md`
  - `knowledge/propositions/정책기관.md`
- 파일 최상단 YAML Frontmatter 규격:
  ```yaml
  ---
  title: 주체명 명제 통합 (예: 국가 명제 통합)
  last_updated: YYYY-MM-DD
  tags: [태그1, 태그2]
  ---
  ```
- 명제 상세 노트는 명제의 성격(카테고리)별로 헤더 `### [성격/테마명]`를 구성하여 분류하고, 하위에 개별 명제 `#### [명제 제목]`과 상세 분석 내용을 기술한다.

### B. 사실관계 노트 (Facts)
- 사실관계는 관점이 아닌 **중요 도메인 개념/기술/정책별**로 단일화하여 `knowledge/facts/` 폴더에 저장 및 누적한다.
  - 예: `knowledge/facts/VPP.md`, `knowledge/facts/분산법.md`, `knowledge/facts/요금제.md`, `knowledge/facts/실증사업.md`, `knowledge/facts/DR.md`
- 파일 최상단 YAML Frontmatter 규격:
  ```yaml
  ---
  title: 중요 개념 사실 통합 (예: 가상발전소 VPP 사실 통합)
  last_updated: YYYY-MM-DD
  tags: [태그1, 태그2]
  ---
  ```

### C. 명제 인덱스 노트 (Indexes)
- 각 주체별 명제 노트를 요약한 인덱스 노트를 `knowledge/indexes/` 폴더에 저장한다.
  - `knowledge/indexes/국가.md`
  - `knowledge/indexes/사업자.md`
  - `knowledge/indexes/소비자.md`
  - `knowledge/indexes/정책기관.md`
- 파일 최상단 YAML Frontmatter 규격:
  ```yaml
  ---
  title: 주체명 명제 인덱스 (예: 국가 명제 인덱스)
  last_updated: YYYY-MM-DD
  tags: [태그1, 태그2]
  ---
  ```
- 인덱스 노트는 명제의 성격(카테고리)별 헤더 `### [성격/테마명]`를 구성하고, 하위에 해당 명제의 제목들만 간결한 리스트(또는 링크) 형태로 기재하여 토큰 효율성을 극대화한다.

---

## 3. 지식 연결 및 병합(Merge) 프로세스
에이전트는 새로운 기사/보고서 분석이 완료되면 다음 순서로 지식을 누적한다.

1. **지식 지도(Index 노트) 및 관점별 인덱스 조회**:
   - 분석 시작 전, 전체 지식의 요약판인 [knowledge/README.md](file:///C:/Users/dl/.gemini/antigravity/worktrees/260614_github_news/inspect-repository-files/knowledge/README.md)와 추가하려는 주체의 개별 인덱스 노트(예: `knowledge/indexes/국가.md`)를 조회한다.
2. **명제 유사도 비교 및 조기 차단 (토큰 효율화 핵심)**:
   - 기사에서 추출한 명제의 요약 제목들을 해당 주체의 인덱스 노트(`knowledge/indexes/주체.md`)에 나열된 기존 명제 제목들과 대조한다.
   - **유사 명제가 이미 존재할 경우**: 해당 명제 상세 노트(`knowledge/propositions/주체.md`)는 열어보거나 수정하지 않고 스킵한다.
   - **기존에 없던 신규 명제일 경우**: 해당 주체의 명제 상세 노트(`knowledge/propositions/주체.md`)를 열어 적절한 카테고리 헤더 아래에 명제를 추가한다.
3. **사실관계 병합**:
   - 기사에서 획득된 Facts들의 주요 개념에 해당하는 Facts 파일(`knowledge/facts/개념명.md`)을 열어 병합한다.

---

## 4. 지식 병합 세부 규칙

### A. 사실 관계 (Facts) 통합 및 그룹화
- 단순 시간 순 나열을 금지하며, **유사한 정보 단위(그룹)로 묶어 통합 관리**한다.
- 각 그룹은 `#### [유사 정보 주제명]` 형태의 중분류 헤더를 사용한다.
- 사실은 시의성이 생명이므로 각 불릿 아이템의 머리에 반드시 **일자(`-[YYYY-MM-DD]`)**를 명시한다.

### B. 명제 (Propositions) 구조화
- 명제는 주장하는 바가 명확히 드러나도록 **주요 키워드 3~5개 내외**를 사용하여 매우 간결한 제목 형태(`#### [키워드 요약 제목]`)로 작성하여 하단에 핵심을 기술한다.
- 유사한 성격의 명제는 개별적으로 늘어놓지 말고 하나의 헤더 아래 통합하거나 보완 내역으로 기술한다.
- 정책 변화 등으로 기존 명제가 수정되는 경우 이전 명제는 **취소선** 처리하고 변경 일자와 신규 명제를 추가한다.

---

## 5. 지식 문서 필수 구조 및 스타일
- **스타일 규정**: 문장은 명사형 종결 또는 간결체(예: '~함', '~임', '~됨')로 종결하며, 서술형 어미는 철저히 배제한다.

# [지식 통합] 파일명 (예: [지식 통합] 국가 명제 / [지식 통합] VPP 사실 / [지식 통합] 국가 명제 인덱스)

- **최종 갱신일:** YYYY-MM-DD
- **핵심 태그:** #태그1, #태그2

### 1. 누적 데이터 목록 (Facts의 경우 사실 목록, Propositions의 경우 명제 목록, Indexes의 경우 인덱스 목록)
- 가이드라인에 맞춘 누적 불릿 리스트


