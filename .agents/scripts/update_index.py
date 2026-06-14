import os
import re
from pathlib import Path

# 경로 설정
REPO_DIR = Path(__file__).resolve().parent.parent.parent
RULES_DIR = REPO_DIR / ".agents" / "rules"
TAGS_FILE = RULES_DIR / "tags.md"
NEWS_DIR = REPO_DIR / "news"
REPORTS_DIR = REPO_DIR / "reports"
README_FILE = REPO_DIR / "README.md"

def load_allowed_tags():
    """tags.md에서 허용된 태그 목록을 파싱하여 반환함."""
    allowed_tags = set()
    if not TAGS_FILE.exists():
        print(f"[Warning] 태그 규칙 파일이 없습니다: {TAGS_FILE}")
        return allowed_tags
    
    content = TAGS_FILE.read_text(encoding="utf-8")
    # 백틱 기호로 묶인 태그 추출 (예: * `VPP`: )
    tags = re.findall(r"\*\s*`([^`]+)`", content)
    for t in tags:
        allowed_tags.add(t.strip())
    return allowed_tags

def parse_markdown_file(file_path):
    """마크다운 파일의 YAML Frontmatter를 파싱함."""
    content = file_path.read_text(encoding="utf-8")
    # Frontmatter 패턴: --- 로 둘러싸인 최상단 영역
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    
    frontmatter_text = match.group(1)
    metadata = {}
    for line in frontmatter_text.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            # tags: [A, B] 파싱
            if key == "tags":
                val = val.strip("[]")
                val = [t.strip() for t in val.split(",") if t.strip()]
            metadata[key] = val
            
    return metadata

def scan_files():
    """news/ 및 reports/ 디렉토리 내 문서를 스캔함."""
    documents = []
    allowed_tags = load_allowed_tags()
    
    # 1. 뉴스 스캔
    if NEWS_DIR.exists():
        for file in NEWS_DIR.glob("*.md"):
            meta = parse_markdown_file(file)
            if meta:
                meta["type"] = "기사"
                # 상대 경로 저장 (README.md 기준)
                meta["rel_path"] = f"news/{file.name}"
                meta["file_name"] = file.name
                documents.append(meta)
                # 태그 검증
                validate_tags(meta, allowed_tags, file.name)
                
    # 2. 보고서 스캔
    if REPORTS_DIR.exists():
        for file in REPORTS_DIR.glob("*.md"):
            meta = parse_markdown_file(file)
            if meta:
                meta["type"] = "보고서"
                meta["rel_path"] = f"reports/{file.name}"
                meta["file_name"] = file.name
                documents.append(meta)
                # 태그 검증
                validate_tags(meta, allowed_tags, file.name)
                
    # 날짜 역순(최신순) 정렬
    documents.sort(key=lambda x: x.get("date", ""), reverse=True)
    return documents

def validate_tags(meta, allowed_tags, filename):
    """허용되지 않은 태그 사용 여부 검증."""
    tags = meta.get("tags", [])
    if allowed_tags:
        for t in tags:
            if t not in allowed_tags:
                print(f"[Warning] {filename} 파일에서 허용되지 않은 태그 '{t}'가 사용됨.")

def generate_latest_table(documents):
    """최신 목록 마크다운 테이블 생성."""
    if not documents:
        return "* 등록된 분석 자료가 없음.\n"
        
    table = "| 날짜 | 구분 | 제목 | 출처/발행기관 | 태그 |\n"
    table += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    for doc in documents:
        date = doc.get("date", "-")
        dtype = doc.get("type", "-")
        title = doc.get("title", doc.get("file_name"))
        rel_path = doc.get("rel_path")
        source = doc.get("source", doc.get("author", "-"))
        tags_str = ", ".join([f"`#{t}`" for t in doc.get("tags", [])])
        
        table += f"| {date} | {dtype} | [{title}]({rel_path}) | {source} | {tags_str} |\n"
        
    return table

def generate_tag_classification(documents):
    """태그별 문서 매핑 마크다운 생성."""
    tag_map = {}
    
    # 태그별 문서 분류
    for doc in documents:
        for tag in doc.get("tags", []):
            if tag not in tag_map:
                tag_map[tag] = []
            tag_map[tag].append(doc)
            
    if not tag_map:
        return "* 분류된 태그가 없음.\n"
        
    markdown = ""
    # 가나다순/알파벳순 정렬
    for tag in sorted(tag_map.keys()):
        markdown += f"#### #{tag}\n"
        for doc in tag_map[tag]:
            date = doc.get("date", "-")
            title = doc.get("title", doc.get("file_name"))
            rel_path = doc.get("rel_path")
            markdown += f"- [{date}] [{title}]({rel_path})\n"
        markdown += "\n"
        
    return markdown

def update_readme(latest_table, tag_class):
    """README.md 파일의 특정 영역을 업데이트함."""
    if not README_FILE.exists():
        print(f"[Error] README.md 파일이 없음: {README_FILE}")
        return
        
    content = README_FILE.read_text(encoding="utf-8")
    
    # 최신 리스트 업데이트
    latest_pattern = r"(<!--\s*START_LATEST_LIST\s*-->).*?(<!--\s*END_LATEST_LIST\s*-->)"
    content = re.sub(
        latest_pattern,
        rf"\g<1>\n{latest_table}\g<2>",
        content,
        flags=re.DOTALL
    )
    
    # 태그 분류 업데이트
    tag_pattern = r"(<!--\s*START_TAG_CLASSIFICATION\s*-->).*?(<!--\s*END_TAG_CLASSIFICATION\s*-->)"
    content = re.sub(
        tag_pattern,
        rf"\g<1>\n{tag_class}\g<2>",
        content,
        flags=re.DOTALL
    )
    
    README_FILE.write_text(content, encoding="utf-8")
    print("[Success] README.md 대시보드가 정상적으로 업데이트됨.")

def main():
    docs = scan_files()
    latest_table = generate_latest_table(docs)
    tag_class = generate_tag_classification(docs)
    update_readme(latest_table, tag_class)

if __name__ == "__main__":
    main()
