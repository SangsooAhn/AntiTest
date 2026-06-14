import os
from pathlib import Path

# 경로 설정
REPO_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = REPO_DIR / "knowledge"
PROPOSITIONS_DIR = KNOWLEDGE_DIR / "propositions"
FACTS_DIR = KNOWLEDGE_DIR / "facts"
INDEXES_DIR = KNOWLEDGE_DIR / "indexes"
KNOWLEDGE_README = KNOWLEDGE_DIR / "README.md"

CATEGORY_MAP = {
    "계통_인프라": "계통_인프라",
    "계통 및 인프라": "계통_인프라",
    "시장_제도": "시장_제도",
    "시장 및 제도": "시장_제도",
    "실증_사업": "실증_사업",
    "실증 및 시범사업": "실증_사업",
    "소비자_참여": "소비자_참여",
    "소비자 및 참여": "소비자_참여"
}

CATEGORY_NAMES = {
    "계통_인프라": "계통 및 인프라",
    "시장_제도": "시장 및 제도",
    "실증_사업": "실증 및 시범사업",
    "소비자_참여": "소비자 및 참여"
}

STANDARD_CATEGORIES = ["계통_인프라", "시장_제도", "실증_사업", "소비자_참여"]

def parse_metadata_and_lines(file_path):
    """마크다운 파일의 frontmatter와 line 리스트를 파싱함."""
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    meta = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    val = v.strip()
                    if val.startswith("[") and val.endswith("]"):
                        val = [x.strip() for x in val[1:-1].split(",") if x.strip()]
                    meta[k.strip()] = val
                    
    return meta, lines

def parse_proposition_file(file_path):
    """개별 명제 파일을 파싱하여 요약 정보를 반환함."""
    meta, lines = parse_metadata_and_lines(file_path)
    
    # 본문에서 내용 및 근거 추출
    description = ""
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("- **상세 내용**:") or line_stripped.startswith("- **내용**:"):
            parts = line_stripped.split(":", 1)
            if len(parts) >= 2:
                description = parts[1].strip()
                
    title = meta.get("title", file_path.stem)
    category = meta.get("category", "시장_제도")
    # 표준화 매핑
    category_key = CATEGORY_MAP.get(category, "시장_제도")
    
    return {
        "file_name": file_path.name,
        "title": title,
        "category_key": category_key,
        "last_updated": meta.get("last_updated", "-"),
        "tags": meta.get("tags", []),
        "description": description
    }

def parse_fact_file(file_path):
    """사실관계 마크다운 파일을 파싱하여 요약 정보를 반환함."""
    meta, lines = parse_metadata_and_lines(file_path)
    fact_count = 0
    updates = []
    
    current_section = None
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        is_h3 = line_stripped.startswith("### ") and not line_stripped.startswith("####")
        if is_h3 and ("사실" in line_stripped or "Facts" in line_stripped):
            current_section = "facts"
            continue
        elif is_h3:
            current_section = None
            continue
            
        if current_section == "facts":
            if line_stripped.startswith(("- [", "* [", "-  [", "*  [")):
                fact_count += 1
                # 날짜 및 요약 내용 추출 (최근 업데이트용)
                # 예: - [2026-06-14] 송배전 비용 반영...
                parts = line_stripped.split("]", 1)
                if len(parts) >= 2:
                    date_part = parts[0].replace("- [", "").replace("* [", "").strip()
                    text_part = parts[1].strip()
                    updates.append({
                        "date": date_part,
                        "text": text_part,
                        "concept": file_path.stem,
                        "file_name": file_path.name
                    })
                
    return {
        "file_name": file_path.name,
        "concept": file_path.stem,
        "last_updated": meta.get("last_updated", "-"),
        "fact_count": fact_count,
        "updates": updates
    }

def compile_theme_indexes(prop_docs):
    """주제별로 명제를 분류하여 indexes/ 디렉토리에 마크다운을 빌드함."""
    INDEXES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 카테고리별 명제 그룹화
    grouped = {cat: [] for cat in STANDARD_CATEGORIES}
    for doc in prop_docs:
        cat_key = doc["category_key"]
        if cat_key in grouped:
            grouped[cat_key].append(doc)
            
    # 주제별 인덱스 파일 작성
    for cat_key in STANDARD_CATEGORIES:
        index_file = INDEXES_DIR / f"{cat_key}.md"
        cat_name = CATEGORY_NAMES.get(cat_key, cat_key)
        docs = grouped[cat_key]
        
        # 최신 업데이트 일자 찾기
        latest_date = "-"
        if docs:
            dates = [d["last_updated"] for d in docs if d["last_updated"] != "-"]
            if dates:
                latest_date = max(dates)
                
        content = f"""---
title: {cat_name} 명제 인덱스
last_updated: {latest_date}
tags: [{cat_key}]
---

# [지식 통합] {cat_name} 명제 인덱스

- **최종 갱신일:** {latest_date}
- **핵심 태그:** #{cat_key}

### 1. 누적 명제 목록
"""
        if not docs:
            content += "- 등록된 명제 없음\n"
        else:
            for doc in docs:
                content += f"- [{doc['title']}](../propositions/{doc['file_name']})\n"
                
        index_file.write_text(content, encoding="utf-8")
        print(f"[Success] {index_file.name} 인덱스가 갱신되었습니다.")

def compile_recent_updates(prop_docs, fact_docs):
    """명제와 사실 갱신 내역 중 최신 5건을 추출하여 리스트로 컴파일함."""
    all_updates = []
    
    # 1. 명제 업데이트 수집
    for doc in prop_docs:
        if doc["last_updated"] != "-":
            all_updates.append({
                "date": doc["last_updated"],
                "type": "Propositions",
                "label": doc["category_key"],
                "text": doc["title"],
                "link": f"propositions/{doc['file_name']}"
            })
            
    # 2. 사실 업데이트 수집
    for doc in fact_docs:
        for upd in doc["updates"]:
            if upd["date"] != "-":
                all_updates.append({
                    "date": upd["date"],
                    "type": "Facts",
                    "label": upd["concept"],
                    "text": upd["text"],
                    "link": f"facts/{upd['file_name']}"
                })
                
    # 날짜 기준 내림차순 정렬
    all_updates.sort(key=lambda x: x["date"], reverse=True)
    recent_5 = all_updates[:5]
    
    if not recent_5:
        return "* 등록된 최근 업데이트 내역이 없습니다.\n"
        
    log_content = ""
    for item in recent_5:
        # 텍스트가 너무 길면 말줄임 처리
        short_text = item["text"][:60] + "..." if len(item["text"]) > 60 else item["text"]
        log_content += f"* [{item['date']}] [{item['type']}] [{item['label']}] {short_text} ([바로가기]({item['link']}))\n"
    return log_content

def safe_replace_section(file_path, start_marker, end_marker, new_content):
    """정규식을 쓰지 않고 슬라이싱을 이용한 안전한 주석 마커 치환."""
    content = file_path.read_text(encoding="utf-8")
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print(f"[Error] 마커를 찾을 수 없음: {start_marker} 또는 {end_marker}")
        return False
        
    updated = (
        content[:start_idx + len(start_marker)]
        + "\n"
        + new_content
        + content[end_idx:]
    )
    file_path.write_text(updated, encoding="utf-8")
    return True

def compile_index():
    """전체 지식 베이스를 스캔하여 주제별 인덱스 및 마스터 리드미를 빌드함."""
    if not KNOWLEDGE_README.exists():
        print(f"[Error] 지식 지도 파일이 없음: {KNOWLEDGE_README}")
        return
        
    # 1. propositions/ 스캔 및 인덱스 컴파일
    prop_docs = []
    if PROPOSITIONS_DIR.exists():
        for file in sorted(PROPOSITIONS_DIR.glob("*.md")):
            try:
                prop_docs.append(parse_proposition_file(file))
            except Exception as e:
                print(f"[Error] 명제 파일 {file.name} 파싱 실패: {e}")
                
    compile_theme_indexes(prop_docs)
    
    # 2. facts/ 스캔
    fact_docs = []
    if FACTS_DIR.exists():
        for file in sorted(FACTS_DIR.glob("*.md")):
            try:
                fact_docs.append(parse_fact_file(file))
            except Exception as e:
                print(f"[Error] 사실 파일 {file.name} 파싱 실패: {e}")
                
    # 3. 최근 업데이트 로그 빌드
    recent_updates_log = compile_recent_updates(prop_docs, fact_docs)
    
    # 4. README 테이블 갱신 내용 준비
    # 4-1. 명제 주제 테이블
    prop_table = "| 주제 구분 | 최종 갱신일 | 명제 인덱스 바로가기 |\n"
    prop_table += "| :--- | :--- | :--- |\n"
    for cat_key in STANDARD_CATEGORIES:
        cat_name = CATEGORY_NAMES.get(cat_key, cat_key)
        rel_path = f"indexes/{cat_key}.md"
        
        # 카테고리 최종 갱신일 확인
        docs = [d for d in prop_docs if d["category_key"] == cat_key]
        latest_date = "-"
        if docs:
            dates = [d["last_updated"] for d in docs if d["last_updated"] != "-"]
            if dates:
                latest_date = max(dates)
                
        prop_table += f"| [{cat_name}]({rel_path}) | {latest_date} | [{cat_name} 인덱스 조회]({rel_path}) |\n"
        
    # 4-2. 사실 통계 테이블
    if not fact_docs:
        fact_table = "* 축적된 사실 데이터가 없습니다.\n"
    else:
        fact_table = "| 중요 도메인 개념 | 최종 갱신일 | 누적 팩트 개수 |\n"
        fact_table += "| :--- | :--- | :---: |\n"
        for doc in fact_docs:
            concept = doc["concept"]
            rel_path = f"facts/{doc['file_name']}"
            last_updated = doc["last_updated"]
            count = f"{doc['fact_count']}개"
            fact_table += f"| [{concept}]({rel_path}) | {last_updated} | {count} |\n"
            
    # 5. README 파일 치환 3단계
    success1 = safe_replace_section(KNOWLEDGE_README, "<!-- START_UPDATES_LOG -->", "<!-- END_UPDATES_LOG -->", recent_updates_log)
    success2 = safe_replace_section(KNOWLEDGE_README, "<!-- START_PROPOSITION_INDEX -->", "<!-- END_PROPOSITION_INDEX -->", prop_table)
    success3 = safe_replace_section(KNOWLEDGE_README, "<!-- START_FACT_INDEX -->", "<!-- END_FACT_INDEX -->", fact_table)
    
    if success1 and success2 and success3:
        print("[Success] knowledge/README.md 지식 지도가 갱신되었습니다.")

if __name__ == "__main__":
    compile_index()
