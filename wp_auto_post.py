#!/usr/bin/env python3
"""
GitHub Actions WordPress auto poster.

Environment variables:
- WP_BASE_URL
- WP_USERNAME
- WP_APP_PASSWORD
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import mimetypes
import os
import re
from pathlib import Path
from typing import Any

import markdown
import pandas as pd
import requests
from slugify import slugify


def env_required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is required.")
    return value


def normalize_url(url: str) -> str:
    return url.rstrip("/")


def basic_auth_header(username: str, app_password: str) -> dict[str, str]:
    token = base64.b64encode(f"{username}:{app_password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def safe_str(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def find_col(columns: list[str], candidates: list[str]) -> str | None:
    columns_map = {str(c).strip().lower(): c for c in columns}
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in columns_map:
            return columns_map[key]
    return None


def read_table(path: Path, sheet: str | None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    suffix = path.suffix.lower()
    if suffix in [".xlsx", ".xlsm", ".xls"]:
        df = pd.read_excel(path, sheet_name=sheet or 0)
    elif suffix == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError("Input must be .xlsx, .xlsm, .xls, or .csv")

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists() and path.is_file():
            return path
    return None


def split_terms(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[,、\n/|]+", value)
    return [p.strip() for p in parts if p.strip()]


def make_slug(text: str, fallback: str) -> str:
    value = slugify(text or fallback, lowercase=True)
    value = value[:90].strip("-")
    return value or fallback


def markdown_to_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=["extra", "tables", "sane_lists", "toc"],
        output_format="html5",
    )


def row_no_to_names(no_value: str) -> list[str]:
    raw = safe_str(no_value)
    if not raw:
        return []
    try:
        number = int(float(raw))
        return [f"{number:03d}", str(number)]
    except ValueError:
        return [raw]


def find_article_file(articles_dir: Path, slug: str, no_value: str) -> Path | None:
    candidates: list[Path] = []
    if slug:
        candidates.append(articles_dir / f"{slug}.md")
    for name in row_no_to_names(no_value):
        candidates.append(articles_dir / f"{name}.md")
    return first_existing(candidates)


def find_image_file(images_dir: Path, slug: str, no_value: str) -> Path | None:
    extensions = [".webp", ".jpg", ".jpeg", ".png"]
    candidates: list[Path] = []
    if slug:
        candidates += [images_dir / f"{slug}{ext}" for ext in extensions]
    for name in row_no_to_names(no_value):
        candidates += [images_dir / f"{name}{ext}" for ext in extensions]
    return first_existing(candidates)


class WordPressClient:
    def __init__(self, base_url: str, username: str, app_password: str) -> None:
        self.base_url = normalize_url(base_url)
        self.api_base = f"{self.base_url}/wp-json/wp/v2"
        self.session = requests.Session()
        self.session.headers.update(basic_auth_header(username, app_password))
        self.session.headers.update({"User-Agent": "GitHub-Actions-WP-Auto-Post/1.0"})

    def request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, timeout=90, **kwargs)
        if response.status_code >= 400:
            raise RuntimeError(f"WordPress API error {response.status_code}: {response.text[:1200]}")
        if not response.text:
            return None
        return response.json()

    def find_or_create_term(self, taxonomy: str, name: str) -> int:
        name = name.strip()
        if not name:
            return 0

        endpoint = "categories" if taxonomy == "category" else "tags"
        data = self.request("GET", endpoint, params={"search": name, "per_page": 100})

        for item in data:
            if item.get("name", "").strip().lower() == name.lower():
                return int(item["id"])

        created = self.request("POST", endpoint, json={"name": name})
        return int(created["id"])

    def upload_media(self, image_path: Path, alt_text: str = "") -> int:
        mime_type, _ = mimetypes.guess_type(str(image_path))
        if not mime_type:
            mime_type = "application/octet-stream"

        headers = {
            "Content-Disposition": f'attachment; filename="{image_path.name}"',
            "Content-Type": mime_type,
        }

        with image_path.open("rb") as f:
            response = self.session.post(
                f"{self.api_base}/media",
                headers=headers,
                data=f,
                timeout=180,
            )

        if response.status_code >= 400:
            raise RuntimeError(f"Media upload error {response.status_code}: {response.text[:1200]}")

        media = response.json()
        media_id = int(media["id"])

        if alt_text:
            self.request("POST", f"media/{media_id}", json={"alt_text": alt_text})

        return media_id

    def create_post(
        self,
        *,
        title: str,
        content_html: str,
        slug: str,
        excerpt: str,
        status: str,
        category_ids: list[int],
        tag_ids: list[int],
        featured_media: int | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "title": title,
            "content": content_html,
            "status": status,
            "slug": slug,
            "excerpt": excerpt,
        }
        if category_ids:
            payload["categories"] = category_ids
        if tag_ids:
            payload["tags"] = tag_ids
        if featured_media:
            payload["featured_media"] = featured_media

        return self.request("POST", "posts", json=payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to XLSX or CSV production sheet")
    parser.add_argument("--sheet", default=None, help="Excel sheet name")
    parser.add_argument("--articles-dir", default="articles")
    parser.add_argument("--images-dir", default="eyecatches")
    parser.add_argument("--post-status", default="draft", choices=["draft", "pending", "publish"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    articles_dir = Path(args.articles_dir)
    images_dir = Path(args.images_dir)

    df = read_table(input_path, args.sheet)

    no_col = find_col(df.columns.tolist(), ["No", "番号", "記事No", "ID"])
    kw_col = find_col(df.columns.tolist(), ["KW", "キーワード", "親KW", "指定KW", "管理KW"])
    title_col = find_col(df.columns.tolist(), ["記事タイトル案", "タイトル", "記事タイトル", "H1", "title"])
    slug_col = find_col(df.columns.tolist(), ["スラッグ", "slug", "Slug"])
    meta_col = find_col(df.columns.tolist(), ["メタディスクリプション案", "メタディスクリプション", "description", "概要"])
    cat_col = find_col(df.columns.tolist(), ["WPカテゴリ", "カテゴリ", "記事カテゴリ", "category"])
    tag_col = find_col(df.columns.tolist(), ["タグ", "WPタグ", "tags"])
    alt_col = find_col(df.columns.tolist(), ["alt", "画像alt", "アイキャッチalt", "代替テキスト"])

    if kw_col is None and title_col is None:
        raise RuntimeError("KW or title column is required.")

    if not args.dry_run:
        wp = WordPressClient(
            env_required("WP_BASE_URL"),
            env_required("WP_USERNAME"),
            env_required("WP_APP_PASSWORD"),
        )
    else:
        wp = None

    results: list[dict[str, Any]] = []
    processed = 0

    for idx, row in df.iterrows():
        if args.limit is not None and processed >= args.limit:
            break

        no_value = safe_str(row.get(no_col, idx + 1)) if no_col else str(idx + 1)
        kw = safe_str(row.get(kw_col, "")) if kw_col else ""
        title = safe_str(row.get(title_col, "")) if title_col else ""
        if not title:
            title = kw

        if not title:
            continue

        explicit_slug = safe_str(row.get(slug_col, "")) if slug_col else ""
        slug = make_slug(explicit_slug or title, f"post-{idx+1:03d}")
        excerpt = safe_str(row.get(meta_col, "")) if meta_col else ""

        category_names = split_terms(safe_str(row.get(cat_col, "")) if cat_col else "")
        tag_names = split_terms(safe_str(row.get(tag_col, "")) if tag_col else "")
        alt_text = safe_str(row.get(alt_col, "")) if alt_col else ""
        if not alt_text:
            alt_text = f"{title}のアイキャッチ画像"

        article_path = find_article_file(articles_dir, slug, no_value)
        image_path = find_image_file(images_dir, slug, no_value)

        result: dict[str, Any] = {
            "no": no_value,
            "kw": kw,
            "title": title,
            "slug": slug,
            "article_file": str(article_path) if article_path else "",
            "image_file": str(image_path) if image_path else "",
            "status": "",
            "post_id": "",
            "post_link": "",
            "message": "",
        }

        if article_path is None:
            result["status"] = "skipped"
            result["message"] = "Article markdown file not found."
            results.append(result)
            continue

        md_text = article_path.read_text(encoding="utf-8")
        content_html = markdown_to_html(md_text)

        if args.dry_run:
            result["status"] = "dry-run"
            result["message"] = "Ready to post."
            results.append(result)
            processed += 1
            print(f"[DRY-RUN] {no_value}: {title}")
            continue

        try:
            assert wp is not None
            category_ids = [wp.find_or_create_term("category", name) for name in category_names]
            category_ids = [term_id for term_id in category_ids if term_id]

            tag_ids = [wp.find_or_create_term("tag", name) for name in tag_names]
            tag_ids = [term_id for term_id in tag_ids if term_id]

            featured_media: int | None = None
            if image_path:
                featured_media = wp.upload_media(image_path, alt_text=alt_text)

            created = wp.create_post(
                title=title,
                content_html=content_html,
                slug=slug,
                excerpt=excerpt,
                status=args.post_status,
                category_ids=category_ids,
                tag_ids=tag_ids,
                featured_media=featured_media,
            )

            result["status"] = "posted"
            result["post_id"] = created.get("id", "")
            result["post_link"] = created.get("link", "")
            result["message"] = "Posted successfully."
            print(f"[POSTED] {no_value}: {title} -> {result['post_link']}")

        except Exception as exc:
            result["status"] = "error"
            result["message"] = str(exc)
            print(f"[ERROR] {no_value}: {title} -> {exc}")

        results.append(result)
        processed += 1

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_path = Path(f"results_{timestamp}.csv")
    pd.DataFrame(results).to_csv(result_path, index=False, encoding="utf-8-sig")
    print(f"Result CSV: {result_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
