#!/usr/bin/env python3
"""Temporary QA entrypoint for the final Ceph CyberNote article."""
from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from PIL import Image

ARTICLE_NO = "77"
ARTICLE = Path("projects/cybernote-security-news/articles/ceph-cve-2026-50152-monitor-config-key-secrets.md")
IMAGE = Path("projects/cybernote-security-news/eyecatches/ceph-cve-2026-50152-monitor-config-key-secrets.png")
LEDGER = "projects/cybernote-security-news/data/news_ledger.csv"
ARTICLES = "projects/cybernote-security-news/articles"
RESULTS = "projects/cybernote-security-news/results"

def paragraph_after_heading(lines: list[str], index: int) -> str:
    i = index + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    parts: list[str] = []
    while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
        parts.append(lines[i].strip())
        i += 1
    return "".join(parts)

def measure() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    match = re.match(r"^---\n([\s\S]*?)\n---\n([\s\S]*)$", text)
    if not match:
        raise RuntimeError("front matter not found")
    front, body = match.groups()
    answer_match = re.search(r'^answer:\s*["\'](.*?)["\']\s*$', front, re.M)
    answer = answer_match.group(1) if answer_match else ""
    faq_block = re.search(r"^faq:\n([\s\S]*?)(?=^sources:)", front, re.M)
    faq_answers = re.findall(r'^\s+a:\s*["\'](.*?)["\']\s*$', faq_block.group(1) if faq_block else "", re.M)
    source_block = re.search(r"^sources:\n([\s\S]*)$", front, re.M)
    sources = len(re.findall(r"^\s+- title:", source_block.group(1) if source_block else "", re.M))
    lines = body.splitlines()
    h1 = next(i for i, line in enumerate(lines) if line.startswith("# "))
    lead = paragraph_after_heading(lines, h1)
    h2_indexes = [i for i, line in enumerate(lines) if line.startswith("## ")]
    h2_titles = [lines[i][3:].strip() for i in h2_indexes]
    summary_i = next(i for i in h2_indexes if lines[i].strip() == "## まとめ")
    summary = paragraph_after_heading(lines, summary_i)
    direct_leads = [len(paragraph_after_heading(lines, i)) for i in h2_indexes if lines[i].strip() != "## まとめ"]
    internal = re.findall(r'https://www\.cybernote\.click/[^)"\'\s}]+', body)
    headings = [line.lstrip("#").strip() for line in lines if re.match(r"^#{2,6}\s+", line)]
    duplicate_headings = sorted(name for name, count in Counter(headings).items() if count > 1)
    forbidden = [h for h in h2_titles if h in {"FAQ", "よくある質問", "参考情報", "参考・出典"}]
    list_lines = len([line for line in lines if re.match(r"^\s*(?:[-*+]|\d+\.)\s+", line)])
    table_lines = len([line for line in lines if re.match(r"^\s*\|", line)])
    print(
        "[MEASURE] "
        f"lead={len(lead)} summary={len(summary)} answer={len(answer)} "
        f"faq={','.join(str(len(x)) for x in faq_answers)} sources={sources} "
        f"internal={len(internal)} unique_internal={len(set(internal))} "
        f"reference_boxes={body.count('<div class=\"wp-block-group is-style-information-box\">')} "
        f"blogcards={body.count('cocoon-blocks/embed-blogcard')} "
        f"forbidden_h2={len(forbidden)} summary_h2={h2_titles.count('まとめ')} "
        f"lists={list_lines} tables={table_lines} "
        f"duplicate_headings={len(duplicate_headings)} h2_direct_leads={','.join(map(str, direct_leads))}"
    )

def main() -> int:
    raw = IMAGE.read_bytes()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        print("[ERROR] PNG signature", file=sys.stderr)
        return 1
    with Image.open(IMAGE) as image:
        image.load()
        print(f"[OK] image format={image.format} size={image.size} mode={image.mode} bytes={len(raw)}")
        if image.format != "PNG" or image.size != (1200, 800) or image.mode != "RGB":
            return 1
    measure()
    commands = [
        [sys.executable, "article_quality_check.py", "--input", LEDGER, "--articles-dir", ARTICLES,
         "--results", f"{RESULTS}/ceph_final_article_quality_results.csv", "--nos", ARTICLE_NO,
         "--include-unstarted", "--mode", "geo", "--fail-on-error"],
        [sys.executable, "geo_article_quality_check.py", "--input", LEDGER, "--articles-dir", ARTICLES,
         "--results", f"{RESULTS}/ceph_final_geo_quality_results.csv", "--nos", ARTICLE_NO,
         "--include-unstarted", "--mode", "geo", "--fail-on-error"],
    ]
    for command in commands:
        print("+", " ".join(command), flush=True)
        completed = subprocess.run(command, check=False)
        if completed.returncode:
            return completed.returncode
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
