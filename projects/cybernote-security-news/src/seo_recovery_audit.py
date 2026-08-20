#!/usr/bin/env python3
"""CyberNoteの公開REST APIを読み、SEO回復用の非破壊監査レポートを作る。"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


CVE_RE = re.compile(r"(?<![A-Z0-9-])CVE-\d{4}-\d{4,}(?![A-Z0-9-])", re.I)
WP_SUFFIX_RE = re.compile(r"^(?P<base>.+)-(?P<number>[2-9]|[1-9]\d)$")
TAG_STRIP_RE = re.compile(r"<[^>]+>")


def field_text(item: dict[str, Any], field: str) -> str:
    value = item.get(field) or ""
    if isinstance(value, dict):
        value = value.get("raw") or value.get("rendered") or ""
    return html.unescape(TAG_STRIP_RE.sub(" ", str(value)))


def normalized_title(post: dict[str, Any]) -> str:
    title = field_text(post, "title").lower()
    title = re.sub(r"^[\s　]*[【\[].*?[】\]][\s　]*", "", title)
    return re.sub(r"[^0-9a-zA-Zぁ-ゖァ-ヺ一-鿿]+", "", title)


def post_cves(post: dict[str, Any]) -> set[str]:
    # 本文まで見ると、複数CVEを扱うまとめ記事が全ての個別記事と
    # 重複扱いになる。URLの主題を表すslug/タイトル/抜粋だけで判定する。
    text = "\n".join(
        [str(post.get("slug") or ""), field_text(post, "title"), field_text(post, "excerpt")]
    )
    return {match.group(0).upper() for match in CVE_RE.finditer(text)}


def canonical_post(posts: list[dict[str, Any]], base_slug: str = "") -> dict[str, Any]:
    def key(post: dict[str, Any]):
        slug = str(post.get("slug") or "")
        suffix = WP_SUFFIX_RE.match(slug)
        return (
            0 if base_slug and slug == base_slug else 1,
            1 if suffix else 0,
            str(post.get("date_gmt") or post.get("date") or "9999"),
            int(post.get("id") or 0),
        )

    return min(posts, key=key)


def duplicate_groups(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[tuple[str, str, list[dict[str, Any]], str]] = []

    by_cve: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for post in posts:
        for cve in post_cves(post):
            by_cve[cve].append(post)
    groups.extend(
        ("cve", cve, members, "")
        for cve, members in sorted(by_cve.items())
        if len({int(post.get("id") or 0) for post in members}) > 1
    )

    by_title: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for post in posts:
        title_key = normalized_title(post)
        if title_key:
            by_title[title_key].append(post)
    groups.extend(
        ("title", title_key, members, "")
        for title_key, members in sorted(by_title.items())
        if len({int(post.get("id") or 0) for post in members}) > 1
    )

    by_base_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
    slugs = {str(post.get("slug") or "") for post in posts}
    for post in posts:
        slug = str(post.get("slug") or "")
        match = WP_SUFFIX_RE.match(slug)
        if match:
            by_base_slug[match.group("base")].append(post)
    for base_slug, suffixed in sorted(by_base_slug.items()):
        base_posts = [post for post in posts if str(post.get("slug") or "") == base_slug]
        members = base_posts + suffixed
        if base_posts or len(suffixed) > 1:
            groups.append(("slug_suffix", base_slug, members, base_slug if base_slug in slugs else ""))

    rows: list[dict[str, Any]] = []
    seen_group_members: set[tuple[str, str, int]] = set()
    for group_type, group_key, raw_members, base_slug in groups:
        members_by_id = {
            int(post.get("id") or 0): post
            for post in raw_members
            if int(post.get("id") or 0)
        }
        members = list(members_by_id.values())
        if len(members) < 2:
            continue
        canonical = canonical_post(members, base_slug)
        canonical_id = int(canonical.get("id") or 0)
        for post in sorted(members, key=lambda item: int(item.get("id") or 0)):
            post_id = int(post.get("id") or 0)
            marker = (group_type, group_key, post_id)
            if marker in seen_group_members:
                continue
            seen_group_members.add(marker)
            rows.append(
                {
                    "group_type": group_type,
                    "group_key": group_key,
                    "canonical_candidate_id": canonical_id,
                    "post_id": post_id,
                    "is_canonical_candidate": post_id == canonical_id,
                    "status": str(post.get("status") or ""),
                    "date": str(post.get("date") or ""),
                    "slug": str(post.get("slug") or ""),
                    "title": field_text(post, "title"),
                    "link": str(post.get("link") or ""),
                    "recommendation": (
                        "keep_candidate_review_required"
                        if post_id == canonical_id
                        else "merge_or_redirect_review_required"
                    ),
                }
            )
    return rows


def daily_volume(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(str(post.get("date") or "")[:10] for post in posts if post.get("date"))
    return [
        {"date": date, "published_posts": count, "over_recovery_limit": count > 1}
        for date, count in sorted(counts.items(), reverse=True)
    ]


def fetch_collection(
    session: requests.Session,
    base_url: str,
    endpoint: str,
    *,
    fields: str,
    extra: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = 1
    while True:
        params: dict[str, Any] = {
            "per_page": 100,
            "page": page,
            "_fields": fields,
            "_nocache": int(dt.datetime.now().timestamp() * 1000),
            **(extra or {}),
        }
        response = session.get(
            f"{base_url}/wp-json/wp/v2/{endpoint}", params=params, timeout=45
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise RuntimeError(f"{endpoint} APIの応答が配列ではありません")
        rows.extend(item for item in payload if isinstance(item, dict))
        total_pages = int(response.headers.get("X-WP-TotalPages") or 0)
        if not payload or (total_pages and page >= total_pages) or len(payload) < 100:
            break
        page += 1
        if page > 100:
            raise RuntimeError(f"{endpoint} APIが100ページを超えたため中止しました")
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_summary(
    posts: list[dict[str, Any]],
    duplicate_rows: list[dict[str, Any]],
    tags: list[dict[str, Any]],
    pages: list[dict[str, Any]],
    volume: list[dict[str, Any]],
) -> dict[str, Any]:
    duplicate_keys = {
        (row["group_type"], row["group_key"]) for row in duplicate_rows
    }
    duplicate_post_ids = {
        int(row["post_id"])
        for row in duplicate_rows
        if not row["is_canonical_candidate"]
    }
    thin_tags = [tag for tag in tags if int(tag.get("count") or 0) <= 1]
    sample_pages = [
        page for page in pages if str(page.get("slug") or "").lower() == "sample-page"
    ]
    return {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "published_posts": len(posts),
        "duplicate_groups": len(duplicate_keys),
        "duplicate_post_candidates": len(duplicate_post_ids),
        "tags": len(tags),
        "thin_tags_count_le_1": len(thin_tags),
        "days_over_one_post": sum(bool(row["over_recovery_limit"]) for row in volume),
        "sample_page_published": bool(sample_pages),
        "safety": "report_only_no_automatic_delete_or_redirect",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default=os.getenv("WP_BASE_URL", "https://www.cybernote.click"),
    )
    parser.add_argument("--output-dir", default="seo-recovery-report")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeError(f"base URLが不正です: {base_url}")

    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "User-Agent": os.getenv("WP_USER_AGENT", "CyberNote-SEO-Audit/1.0"),
        }
    )
    posts = fetch_collection(
        session,
        base_url,
        "posts",
        fields="id,slug,link,status,date,date_gmt,title,excerpt",
        extra={"status": "publish"},
    )
    tags = fetch_collection(
        session,
        base_url,
        "tags",
        fields="id,name,slug,count,link",
        extra={"hide_empty": "false"},
    )
    pages = fetch_collection(
        session,
        base_url,
        "pages",
        fields="id,slug,link,status,date,title",
        extra={"status": "publish"},
    )

    duplicates = duplicate_groups(posts)
    volume = daily_volume(posts)
    summary = build_summary(posts, duplicates, tags, pages, volume)
    output_dir = Path(args.output_dir)
    write_csv(
        output_dir / "duplicate_posts.csv",
        duplicates,
        [
            "group_type", "group_key", "canonical_candidate_id", "post_id",
            "is_canonical_candidate", "status", "date", "slug", "title", "link",
            "recommendation",
        ],
    )
    write_csv(
        output_dir / "thin_tags.csv",
        [tag for tag in tags if int(tag.get("count") or 0) <= 1],
        ["id", "name", "slug", "count", "link"],
    )
    write_csv(
        output_dir / "daily_volume.csv",
        volume,
        ["date", "published_posts", "over_recovery_limit"],
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary_md = (
        "# CyberNote SEO recovery audit\n\n"
        f"- 公開記事: {summary['published_posts']}\n"
        f"- 重複グループ: {summary['duplicate_groups']}\n"
        f"- 統合・リダイレクト要確認: {summary['duplicate_post_candidates']}\n"
        f"- 1記事以下のタグ: {summary['thin_tags_count_le_1']} / {summary['tags']}\n"
        f"- Sample Page公開: {'yes' if summary['sample_page_published'] else 'no'}\n\n"
        "この監査はレポートのみで、記事の削除・非公開化・リダイレクトは行いません。\n"
    )
    (output_dir / "summary.md").write_text(summary_md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
