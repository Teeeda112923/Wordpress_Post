#!/usr/bin/env python3
"""18:30に作成したWordPress下書きを、本文を上書きせず公開する。"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SOURCE_DIR))

from select_news import read_ledger, select_row, value  # noqa: E402
from wp_auto_post import (  # noqa: E402
    WordPressClient,
    env_required,
    make_slug,
    safe_str,
)

JST = ZoneInfo("Asia/Tokyo")


def result_file(results_dir: Path) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(JST).strftime("%Y%m%d_%H%M%S")
    return results_dir / f"publish_{timestamp}.csv"


def write_result(path: Path, row: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="ニュース下書きを公開する")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--articles-dir", required=True)
    parser.add_argument("--eyecatches-dir", required=True)
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--date", default="")
    parser.add_argument("--no", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    target_date = args.date.strip() or dt.datetime.now(JST).date().isoformat()
    ledger_rows = read_ledger(repo_root / args.ledger)
    row = select_row(
        ledger_rows,
        target_date,
        "publish",
        repo_root,
        repo_root / args.articles_dir,
        repo_root / args.eyecatches_dir,
        args.no,
    )

    if row is None:
        print(f"公開対象なし: date={target_date}", file=sys.stderr)
        return 0

    no = value(row, "No", "番号", "記事No", "ID")
    title = value(row, "記事タイトル", "記事タイトル案", "タイトル", "title")
    explicit_slug = value(row, "スラッグ", "slug")
    slug = explicit_slug or make_slug(title, f"cybernote-security-news-{no}")

    result: dict[str, Any] = {
        "No": no,
        "title": title,
        "slug": slug,
        "status": "",
        "post_id": "",
        "post_link": "",
        "published_at_jst": "",
        "message": "",
    }
    output = result_file(repo_root / args.results_dir)

    if args.dry_run:
        result["status"] = "dry-run"
        result["message"] = "公開予定の下書きを確認しました。WordPress APIは呼び出していません。"
        write_result(output, result)
        print(f"[DRY-RUN] No.{no} {title} -> {slug}")
        return 0

    wp = WordPressClient(
        env_required("WP_BASE_URL"),
        env_required("WP_USERNAME"),
        env_required("WP_APP_PASSWORD"),
    )
    user = wp.verify_auth()
    print(f"認証OK: {user}")

    post = wp.find_post_by_slug(slug, "draft")
    if not post:
        post = wp.find_post_by_title(title, "draft")

    if not post:
        result["status"] = "error"
        result["message"] = "18:30に作成された下書きが見つかりません。"
        write_result(output, result)
        print(f"[ERROR] No.{no} {result['message']}", file=sys.stderr)
        return 1

    post_id = int(post.get("id") or 0)
    current_status = safe_str(post.get("status"))
    result["post_id"] = post_id
    result["post_link"] = safe_str(post.get("link"))

    if current_status == "publish":
        result["status"] = "already_published"
        result["message"] = "すでに公開済みです。"
        write_result(output, result)
        print(f"[SKIP] No.{no} すでに公開済み: {result['post_link']}")
        return 0

    if current_status not in {"draft", "pending", "future", "private"}:
        result["status"] = "error"
        result["message"] = f"公開対象外の投稿ステータスです: {current_status}"
        write_result(output, result)
        print(f"[ERROR] No.{no} {result['message']}", file=sys.stderr)
        return 1

    # 本文・タイトル・画像・カテゴリーは送信せず、ステータスだけを変更する。
    # 18:30以降に管理画面で行った修正を19:00に上書きしないための処理。
    updated = wp.request("POST", f"posts/{post_id}", json={"status": "publish"})
    result["status"] = "published"
    result["post_id"] = updated.get("id", post_id)
    result["post_link"] = safe_str(updated.get("link")) or result["post_link"]
    result["published_at_jst"] = dt.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    result["message"] = "本文を上書きせず、投稿ステータスだけをpublishへ変更しました。"
    write_result(output, result)
    print(f"[PUBLISHED] No.{no} {title} -> {result['post_link']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
