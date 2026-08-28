#!/usr/bin/env python3
"""Temporary QA entrypoint for the Ceph CyberNote article."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
from PIL import Image

ARTICLE_NO = "77"
IMAGE = Path("projects/cybernote-security-news/eyecatches/ceph-cve-2026-50152-monitor-config-key-disclosure.png")
LEDGER = "projects/cybernote-security-news/data/news_ledger.csv"
ARTICLES = "projects/cybernote-security-news/articles"
RESULTS = "projects/cybernote-security-news/results"

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
    commands = [
        [sys.executable, "article_quality_check.py", "--input", LEDGER, "--articles-dir", ARTICLES,
         "--results", f"{RESULTS}/ceph_article_quality_results.csv", "--nos", ARTICLE_NO,
         "--include-unstarted", "--mode", "geo", "--fail-on-error"],
        [sys.executable, "geo_article_quality_check.py", "--input", LEDGER, "--articles-dir", ARTICLES,
         "--results", f"{RESULTS}/ceph_geo_quality_results.csv", "--nos", ARTICLE_NO,
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
