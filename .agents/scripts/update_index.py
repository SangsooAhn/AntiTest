import os
from pathlib import Path

# 경로 설정
REPO_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = REPO_DIR / "knowledge"
KNOWLEDGE_README = KNOWLEDGE_DIR / "README.md"

def parse_perspective_file(file_path):
    """관점별 지식 통합 마크다운 파일의 frontmatter, 사실 개수, 명제 제목들을 파싱함."""
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    # 1. Frontmatter 파싱 (split 기반)
    meta = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
                    
    # 2. 상태 머신 기반 본문 파서 (정규식 비사용)
    fact_count = 0
    proposition_titles = []
    
    current_section = None
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # 헤더 감지로 섹션 상태 전환 (H4 등 하위 헤더와의 간섭 차단)
        is_h3 = line_stripped.startswith("### ") and not line_stripped.startswith("####")
        if is_h3 and ("사실 관계" in line_stripped or "Facts" in line_stripped):
            current_section = "facts"
            continue
        elif is_h3 and ("명제" in line_stripped or "Propositions" in line_stripped):
            current_section = "propositions"
            continue
        elif is_h3:
            # 다른 h3 대헤더 진입 시 섹션 초기화
            current_section = None
            continue
            
        if current_section == "facts":
            # 불릿 포인트 개수를 팩트 개수로 집계
            if line_stripped.startswith(("-", "*")):
                fact_count += 1
                
        elif current_section == "propositions":
            # 명제 제목 추출 (#### [제목] 형태 탐색)
            if line_stripped.startswith("####"):
                title_text = line_stripped.lstrip("#").strip()
                if title_text.startswith("[") and title_text.endswith("]"):
                    proposition_titles.append(title_text)
                    
    # 파일명으로부터 관점 구분자 추출 (예: 국가_관점.md -> 국가)
    perspective_name = file_path.stem.split("_")[0]
    
    return {
        "file_name": file_path.name,
        "perspective": perspective_name,
        "title": meta.get("title", file_path.stem),
        "last_updated": meta.get("last_updated", "-"),
        "fact_count": fact_count,
        "proposition_titles": proposition_titles
    }

def scan_knowledge_base():
    """knowledge/ 내 관점별 지식 문서를 스캔함."""
    docs = []
    if not KNOWLEDGE_DIR.exists():
        return docs
        
    # 지정된 4개의 관점 노트를 대상으로 순차 스캔
    target_files = ["국가_관점.md", "사업자_관점.md", "소비자_관점.md", "정책기관_관점.md"]
    for filename in target_files:
        file_path = KNOWLEDGE_DIR / filename
        if file_path.exists():
            try:
                doc_data = parse_perspective_file(file_path)
                docs.append(doc_data)
            except Exception as e:
                print(f"[Error] {filename} 파싱 실패: {e}")
                
    return docs

def update_knowledge_readme(docs):
    """knowledge/README.md의 명제 현황판 업데이트 (슬라이싱 교체, re.sub 미사용)."""
    if not KNOWLEDGE_README.exists():
        print(f"[Warning] 지식 지도 파일이 존재하지 않음: {KNOWLEDGE_README}")
        return
        
    start_marker = "<!-- START_PERSPECTIVE_INDEX -->"
    end_marker = "<!-- END_PERSPECTIVE_INDEX -->"
    
    if not docs:
        table_content = "* 현재 축적된 관점별 지식 통합 문서가 없습니다.\n"
    else:
        table_content = "| 관점 구분 | 최종 갱신일 | 누적 팩트 | 축적된 핵심 명제 현황 |\n"
        table_content += "| :--- | :--- | :---: | :--- |\n"
        
        for doc in docs:
            p_name = doc["perspective"]
            filename = doc["file_name"]
            last_updated = doc["last_updated"]
            fact_count = f"{doc['fact_count']}개"
            titles = doc["proposition_titles"]
            
            # 명제 제목 리스트 가공 (줄바꿈 브라우저 대응)
            titles_str = "<br>".join([f"- {t}" for t in titles]) if titles else "등록된 명제 없음"
            
            table_content += f"| [{p_name} 관점]({filename}) | {last_updated} | {fact_count} | {titles_str} |\n"
            
    # 안전한 슬라이싱 치환 로직 (정규식 특수문자 크래시 회피)
    content = KNOWLEDGE_README.read_text(encoding="utf-8")
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("[Error] README.md 내에 인덱싱 마커를 찾을 수 없습니다.")
        return
        
    updated_content = (
        content[:start_idx + len(start_marker)]
        + "\n"
        + table_content
        + content[end_idx:]
    )
    
    KNOWLEDGE_README.write_text(updated_content, encoding="utf-8")
    print("[Success] knowledge/README.md 지식 지도가 성공적으로 업데이트됨.")

def main():
    docs = scan_knowledge_base()
    update_knowledge_readme(docs)

if __name__ == "__main__":
    main()
