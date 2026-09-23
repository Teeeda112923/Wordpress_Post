"""Restore the original OpenSearch post 7573 displaced by a CVE cross-link."""
import csv
import os
import subprocess
import sys
import tempfile
from pathlib import Path

results = Path(tempfile.mkdtemp(prefix="cybernote-opensearch-restore-"))
cmd = [
    sys.executable, "wp_auto_post.py",
    "--input", "projects/cybernote-security-news/data/news_ledger.csv",
    "--articles-dir", "projects/cybernote-security-news/articles",
    "--images-dir", "projects/cybernote-security-news/eyecatches",
    "--post-status", "publish",
    "--write-mode", "update_only",
    "--category", "サイバーセキュリティ",
    "--nos", "65",
    "--limit", "1",
    "--skip-auth-check",
    "--skip-internal-link-resolution",
    "--fallback-media-id", os.environ.get("FALLBACK_MEDIA_ID", "5297"),
    "--output-dir", str(results),
]
subprocess.run(cmd, check=True)
files = sorted(results.glob("results_*.csv"))
if not files:
    raise RuntimeError("OpenSearch restore result CSV missing")
with files[-1].open(encoding="utf-8-sig", newline="") as fh:
    rows = list(csv.DictReader(fh))
matches = [row for row in rows if row.get("no") == "65"]
if len(matches) != 1 or matches[0].get("status") != "updated" or str(matches[0].get("post_id")) != "7573":
    raise RuntimeError(f"OpenSearch post 7573 restoration unverified: {matches}")
print("Restored original OpenSearch article to canonical post 7573.")
