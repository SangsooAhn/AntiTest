import os
from pathlib import Path

# 경로 설정
REPO_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = REPO_DIR / "knowledge"
PROPOSITIONS_DIR = KNOWLEDGE_DIR / "propositions"
FACTS_DIR = KNOWLEDGE_DIR / "facts"
INDEXES_DIR = KNOWLEDGE_DIR / "indexes"
KNOWLEDGE_README = KNOWLEDGE_DIR / "README.md"

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
    """명제 마크다운 파일을 파싱하여 요약 정보를 반환함."""
    meta, lines = parse_metadata_and_lines(file_path)
    categories = {}
    current_category = None
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # H3 감지 (H4 헤더 간섭 배제)
        is_h3 = line_stripped.startswith("### ") and not line_stripped.startswith("####")
        if is_h3:
            hdr_text = line_stripped.lstrip("#").strip()
            if hdr_text.startswith("[") and hdr_text.endswith("]"):
                current_category = hdr_text[1:-1].strip()
                categories[current_category] = []
            else:
                current_category = None
            continue
            
        if current_category:
            # H4 명제 제목 감지
            if line_stripped.startswith("####"):
                title_text = line_stripped.lstrip("#").strip()
                if title_text.startswith("[") and title_text.endswith("]"):
                    prop_title = title_text[1:-1].strip()
                    categories[current_category].append(prop_title)
                    
    subject_name = file_path.stem
    return {
        "file_name": file_path.name,
        "subject": subject_name,
        "last_updated": meta.get("last_updated", "-"),
        "tags": meta.get("tags", []),
        "categories": categories
    }

def parse_fact_file(file_path):
    """사실관계 마크다운 파일을 파싱하여 요약 정보를 반환함."""
    meta, lines = parse_metadata_and_lines(file_path)
    fact_count = 0
    
    current_section = None
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # H3 감지 (H4 헤더 간섭 배제)
        is_h3 = line_stripped.startswith("### ") and not line_stripped.startswith("####")
        if is_h3 and ("사실" in line_stripped or "Facts" in line_stripped):
            current_section = "facts"
            continue
        elif is_h3:
            current_section = None
            continue
            
        if current_section == "facts":
            # 사실 목록 개수 집계
            if line_stripped.startswith(("-", "*")):
                fact_count += 1
                
    concept_name = file_path.stem
    return {
        "file_name": file_path.name,
        "concept": concept_name,
        "last_updated": meta.get("last_updated", "-"),
        "fact_count": fact_count
    }

def scan_propositions():
    """propositions/ 내 문서를 순차 스캔함."""
    docs = []
    if not PROPOSITIONS_DIR.exists():
        return docs
    
    # 주체 순서 정의 (국가, 사업자, 소비자, 정책기관 순)
    target_subjects = ["국가", "사업자", "소비자", "정책기관"]
    for sub in target_subjects:
        file_path = PROPOSITIONS_DIR / f"{sub}.md"
        if file_path.exists():
            try:
                docs.append(parse_proposition_file(file_path))
            except Exception as e:
                print(f"[Error] 명제 파일 {sub}.md 파싱 실패: {e}")
    return docs

def scan_facts():
    """facts/ 내 문서를 사전순 스캔함."""
    docs = []
    if not FACTS_DIR.exists():
        return docs
        
    for file in sorted(FACTS_DIR.glob("*.md")):
        try:
            docs.append(parse_fact_file(file))
        except Exception as e:
            print(f"[Error] 사실 파일 {file.name} 파싱 실패: {e}")
    return docs

def write_individual_index(doc):
    """개별 관점별 Index 노드를 생성/업데이트함."""
    INDEXES_DIR.mkdir(parents=True, exist_ok=True)
    index_file = INDEXES_DIR / doc["file_name"]
    
    # frontmatter 및 헤더 구성
    tags_str = ", ".join(doc["tags"]) if isinstance(doc["tags"], list) else str(doc["tags"])
    header_tags = ", ".join([f"#{t}" for t in doc["tags"]]) if isinstance(doc["tags"], list) else ""
    
    content = f"""---
title: {doc['subject']} 명제 인덱스
last_updated: {doc['last_updated']}
tags: [{tags_str}]
---

# [지식 통합] {doc['subject']} 명제 인덱스

- **최종 갱신일:** {doc['last_updated']}
- **핵심 태그:** {header_tags}
- **원본 명제 노트:** [{doc['subject']} 명제 통합](../propositions/{doc['file_name']})
"""
    
    for cat, props in doc["categories"].items():
        content += f"\n### [{cat}]\n"
        if not props:
            content += "- 등록된 명제 없음\n"
        else:
            for p in props:
                # anchor link format: 공백은 하이픈으로 대체
                anchor = p.replace(" ", "-")
                content += f"- [{p}](../propositions/{doc['file_name']}#{anchor})\n"
                
    index_file.write_text(content, encoding="utf-8")
    print(f"[Success] {index_file.name} 인덱스가 갱신되었습니다.")

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
    """명제와 팩트 파일들을 스캔하여 Index 리드미를 빌드함."""
    if not KNOWLEDGE_README.exists():
        print(f"[Error] 지식 지도 파일이 없음: {KNOWLEDGE_README}")
        return
        
    # 1. 명제 목록 컴파일 및 개별 인덱스 빌드
    prop_docs = scan_propositions()
    for doc in prop_docs:
        write_individual_index(doc)
        
    if not prop_docs:
        prop_table = "* 축적된 명제 데이터가 없습니다.\n"
    else:
        prop_table = "| 주체 구분 | 최종 갱신일 | 명제 인덱스 바로가기 |\n"
        prop_table += "| :--- | :--- | :--- |\n"
        for doc in prop_docs:
            sub = doc["subject"]
            rel_path = f"indexes/{doc['file_name']}"
            last_updated = doc["last_updated"]
            prop_table += f"| [{sub} 명제 인덱스]({rel_path}) | {last_updated} | [{sub} 명제 인덱스 조회]({rel_path}) |\n"
            
    # 2. 사실 목록 컴파일
    fact_docs = scan_facts()
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
            
    # 3. 파일 마커 이중 치환
    success1 = safe_replace_section(KNOWLEDGE_README, "<!-- START_PROPOSITION_INDEX -->", "<!-- END_PROPOSITION_INDEX -->", prop_table)
    success2 = safe_replace_section(KNOWLEDGE_README, "<!-- START_FACT_INDEX -->", "<!-- END_FACT_INDEX -->", fact_table)
    
    if success1 and success2:
        print("[Success] knowledge/README.md 지식 지도가 갱신되었습니다.")

if __name__ == "__main__":
    compile_index()
