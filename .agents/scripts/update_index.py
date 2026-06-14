import os
import re
from pathlib import Path

# 경로 설정
REPO_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = REPO_DIR / "knowledge"
KNOWLEDGE_README = KNOWLEDGE_DIR / "README.md"
ROOT_README = REPO_DIR / "README.md"

def parse_knowledge_file(file_path):
    """지식 통합 마크다운 파일의 frontmatter와 핵심 명제를 파싱함."""
    content = file_path.read_text(encoding="utf-8")
    
    # 1. Frontmatter 파싱
    meta = {}
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        for line in fm_text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    
    # 2. 사실 관계(Facts) 개수 및 내용 추출
    facts = []
    # '### 1. 누적 사실 관계 (Facts)' 이하부터 다음 헤더 전까지 추출
    facts_section_match = re.search(r"### 1\. 누적 사실 관계 \(Facts\)(.*?)(?=### 2|$)", content, re.DOTALL)
    if facts_section_match:
        facts_text = facts_section_match.group(1)
        # 불릿 아이템 추출
        facts = [line.strip().lstrip("-* ").strip() for line in facts_text.splitlines() if line.strip().startswith(("-", "*"))]

    # 3. 관점별 명제 추출
    propositions = {"국가": [], "사업자": [], "소비자": [], "정책기관": []}
    props_section_match = re.search(r"### 2\. 관점별 누적 명제 \(Propositions\)(.*)", content, re.DOTALL)
    if props_section_match:
        props_text = props_section_match.group(1)
        
        # 각 관점별 영역 분할 파싱
        # 예: - **국가 관점**: 아래에 나오는 하위 불릿 아이템들
        current_perspective = None
        for line in props_text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            
            # 관점 헤더 찾기
            header_match = re.search(r"\*\*(국가|사업자|소비자|정책기관)\s*관점\*\*", line_str)
            if header_match:
                current_perspective = header_match.group(1)
                continue
            
            # 불릿 명제 찾기
            if current_perspective and line_str.startswith(("-", "*")):
                prop_item = line_str.lstrip("-* ").strip()
                # 취소선 처리된 명제는 건너뛰거나 제외할 수 있으나, 활성화된 명제만 취합
                if not (prop_item.startswith("~~") and prop_item.endswith("~~")):
                    propositions[current_perspective].append(prop_item)
                    
    return {
        "file_name": file_path.name,
        "title": meta.get("title", file_path.stem),
        "last_updated": meta.get("last_updated", "-"),
        "tags": meta.get("tags", ""),
        "fact_count": len(facts),
        "propositions": propositions
    }

def scan_knowledge_base():
    """knowledge/ 내 지식 문서들을 스캔하여 정렬함."""
    docs = []
    if not KNOWLEDGE_DIR.exists():
        return docs
        
    for file in KNOWLEDGE_DIR.glob("*.md"):
        if file.name.lower() == "readme.md":
            continue
        try:
            doc_data = parse_knowledge_file(file)
            docs.append(doc_data)
        except Exception as e:
            print(f"[Error] {file.name} 파싱 실패: {e}")
            
    # 최종 갱신일 최신순 정렬
    docs.sort(key=lambda x: x["last_updated"], reverse=True)
    return docs

def update_knowledge_readme(docs):
    """knowledge/README.md 파일의 지식 지도 영역 업데이트."""
    if not KNOWLEDGE_README.exists():
        print(f"[Warning] 지식 지도 파일이 존재하지 않음: {KNOWLEDGE_README}")
        return
        
    if not docs:
        map_content = "* 현재 축적된 지식 통합 문서가 없습니다.\n"
    else:
        map_content = ""
        for doc in docs:
            filename = doc["file_name"]
            title = doc["title"]
            last_updated = doc["last_updated"]
            fact_count = doc["fact_count"]
            props = doc["propositions"]
            
            # 각 관점의 첫 번째 활성 명제 추출
            summary_props = []
            for k, v in props.items():
                if v:
                    summary_props.append(f"  - *{k}*: {v[0]}")
            
            summary_props_str = "\n".join(summary_props) if summary_props else "  - *등록된 명제 없음*"
            
            map_content += f"#### [{title}]({filename})\n"
            map_content += f"- **최종 갱신일**: {last_updated}\n"
            map_content += f"- **누적 사실(Facts) 수**: {fact_count}개\n"
            map_content += f"- **핵심 관점별 명제**:\n{summary_props_str}\n\n"
            
    content = KNOWLEDGE_README.read_text(encoding="utf-8")
    pattern = r"(<!--\s*START_KNOWLEDGE_MAP\s*-->).*?(<!--\s*END_KNOWLEDGE_MAP\s*-->)"
    updated_content = re.sub(
        pattern,
        rf"\g<1>\n{map_content}<!-- END_KNOWLEDGE_MAP -->",
        content,
        flags=re.DOTALL
    )
    KNOWLEDGE_README.write_text(updated_content, encoding="utf-8")
    print("[Success] knowledge/README.md 지식 지도가 업데이트됨.")

def update_root_readme(docs):
    """루트 README.md의 대시보드 요약판 업데이트."""
    if not ROOT_README.exists():
        print(f"[Warning] 루트 README.md 파일이 존재하지 않음: {ROOT_README}")
        return
        
    if not docs:
        summary_content = "* 현재 축적된 지식 통합 문서가 없습니다.\n"
    else:
        # 마크다운 표 생성
        summary_content = "| 지식 주제 | 최종 갱신일 | 누적 팩트 | 핵심 관점별 명제 요약 (국가/사업자/소비자/정책기관) |\n"
        summary_content += "| :--- | :--- | :---: | :--- |\n"
        
        for doc in docs:
            title = doc["title"]
            rel_path = f"knowledge/{doc['file_name']}"
            last_updated = doc["last_updated"]
            fact_count = f"{doc['fact_count']}개"
            props = doc["propositions"]
            
            # 요약 명제 가공
            rep_props = []
            for k, v in props.items():
                if v:
                    rep_props.append(f"**[{k}]** {v[0]}")
                    
            props_str = "<br>".join(rep_props) if rep_props else "등록된 명제 없음"
            
            summary_content += f"| [{title}]({rel_path}) | {last_updated} | {fact_count} | {props_str} |\n"
            
    content = ROOT_README.read_text(encoding="utf-8")
    pattern = r"(<!--\s*START_KNOWLEDGE_SUMMARY\s*-->).*?(<!--\s*END_KNOWLEDGE_SUMMARY\s*-->)"
    updated_content = re.sub(
        pattern,
        rf"\g<1>\n{summary_content}<!-- END_KNOWLEDGE_SUMMARY -->",
        content,
        flags=re.DOTALL
    )
    ROOT_README.write_text(updated_content, encoding="utf-8")
    print("[Success] 루트 README.md 지식 요약 현황판이 업데이트됨.")

def main():
    docs = scan_knowledge_base()
    update_knowledge_readme(docs)
    update_root_readme(docs)

if __name__ == "__main__":
    main()
