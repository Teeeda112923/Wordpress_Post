#!/usr/bin/env python3
"""
GitHub Actions から WordPress REST API へ記事を自動投稿するスクリプト。

認証情報は環境変数で受け取ります（コードに直書きしない）:
- WP_BASE_URL      例: https://example.com
- WP_USERNAME      WordPress ユーザー名
- WP_APP_PASSWORD  アプリケーションパスワード（再発行したもの）

使い方:
    python wp_auto_post.py \
        --input data/seo_80kw_production_management.xlsx \
        --sheet 制作管理表 \
        --articles-dir articles \
        --images-dir eyecatches \
        --post-status draft \
        --dry-run \
        --limit 1
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import mimetypes
import os
import re
import time
from pathlib import Path
from typing import Any

import markdown
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from slugify import slugify
from urllib3.util.retry import Retry


# --------------------------------------------------------------------------- #
# 列名候補（用途 -> 候補リスト）。完全一致 -> 部分一致の順で柔軟に探索する。
# --------------------------------------------------------------------------- #
COLUMN_CANDIDATES: dict[str, list[str]] = {
    "no": ["No", "番号", "記事No", "ID"],
    "kw": ["指定KW", "管理KW", "KW", "キーワード", "親KW"],
    "title": ["記事タイトル案", "記事タイトル", "タイトル", "H1", "title"],
    "slug": ["スラッグ", "slug", "Slug"],
    "meta": ["メタディスクリプション案", "メタディスクリプション", "description", "概要"],
    "category": ["WPカテゴリ", "カテゴリ", "記事カテゴリ", "category"],
    "tag": ["タグ案", "タグ", "WPタグ", "tags"],
    "image_name": ["画像ファイル名", "アイキャッチファイル名", "画像名"],
    "alt": ["画像alt", "アイキャッチalt", "代替テキスト", "alt"],
}

IMAGE_EXTENSIONS = [".webp", ".jpg", ".jpeg", ".png"]


# --------------------------------------------------------------------------- #
# ユーティリティ
# --------------------------------------------------------------------------- #
def env_required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"環境変数 {name} が未設定です。GitHub Secrets を確認してください。")
    return value


def normalize_url(url: str) -> str:
    return url.rstrip("/")


def basic_auth_header(username: str, app_password: str) -> dict[str, str]:
    # アプリケーションパスワードのスペースは WordPress が無視するため除去しておく
    app_password = app_password.replace(" ", "")
    token = base64.b64encode(f"{username}:{app_password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def safe_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def find_col(columns: list[str], candidates: list[str]) -> str | None:
    """完全一致（大文字小文字無視）を最優先し、無ければ部分一致で探す。"""
    norm = {str(c).strip().lower(): c for c in columns}
    # 1) 完全一致
    for cand in candidates:
        key = cand.strip().lower()
        if key in norm:
            return norm[key]
    # 2) 部分一致（列名のブレ対策）
    for cand in candidates:
        key = cand.strip().lower()
        for col_key, original in norm.items():
            if key in col_key or col_key in key:
                return original
    return None


def read_table(path: Path, sheet: str | None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {path}")

    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path, sheet_name=sheet or 0, dtype=object)
    elif suffix == ".csv":
        df = pd.read_csv(path, dtype=object)
    else:
        raise ValueError("入力は .xlsx / .xlsm / .xls / .csv のいずれかにしてください。")

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists() and p.is_file():
            return p
    return None


def split_terms(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[,、\n/|｜]+", value)
    return [p.strip() for p in parts if p.strip()]


def make_slug(text: str, fallback: str) -> str:
    value = slugify(text or fallback, lowercase=True)
    value = value[:90].strip("-")
    return value or fallback


def row_no_to_names(no_value: str) -> list[str]:
    raw = safe_str(no_value)
    if not raw:
        return []
    try:
        number = int(float(raw))
        return [f"{number:03d}", str(number)]
    except ValueError:
        return [raw]


def markdown_to_html(md_text: str, *, strip_h1: bool, title: str = "") -> str:
    """Markdown -> HTML。strip_h1=True なら本文先頭の H1 を無条件で除去する。

    WordPress テーマ側が投稿タイトルを表示するため、本文先頭の H1 はタイトルと
    一致していなくても二重表示になる。よって先頭 H1（Markdown の `# ...`）は
    内容に関わらず削除する。本文中の `##` 以降（H2/H3...）は残す。
    title 引数は後方互換のため残しているが判定には使用しない。
    """
    text = md_text.lstrip("﻿").lstrip()
    if strip_h1:
        text = strip_leading_markdown_h1(text)

    html = markdown.markdown(
        text,
        extensions=["extra", "tables", "sane_lists", "toc"],
        output_format="html5",
    )

    if strip_h1:
        html = strip_leading_html_h1(html)
    return html


def strip_leading_markdown_h1(text: str) -> str:
    """本文の最初の見出しが H1（"# ..."）ならその行を削除する。

    YAML フロントマター（先頭の --- ... ---）や空行・コメントを読み飛ばし、
    最初に現れる「実体のある行」が H1 のときだけ削除する。setext 形式
    （見出しの次行が === ）の H1 にも対応する。"##" 以降は対象外。
    """
    lines = text.split("\n")
    n = len(lines)

    # 先頭の YAML フロントマター（--- ... ---）は丸ごと除去する
    if n and lines[0].strip() == "---":
        j = 1
        while j < n and lines[j].strip() != "---":
            j += 1
        if j < n:  # 閉じ --- が見つかった場合のみ除去
            del lines[: j + 1]
            n = len(lines)

    i = 0
    # 空行・HTMLコメント行を読み飛ばし、最初の実体行を探す
    while i < n and (lines[i].strip() == "" or lines[i].lstrip().startswith("<!--")):
        i += 1

    if i >= n:
        return text

    first = lines[i]
    # ATX 形式: "# 見出し"（"##" は除外）
    if re.match(r"^#\s+\S", first) and not first.lstrip().startswith("##"):
        del lines[i]
        return "\n".join(lines).lstrip("\n")

    # setext 形式: 見出しテキストの次行が "===..."（H1）
    if i + 1 < n and re.match(r"^=+\s*$", lines[i + 1]) and first.strip():
        del lines[i : i + 2]
        return "\n".join(lines).lstrip("\n")

    return text


def strip_leading_html_h1(html: str) -> str:
    """HTML 本文の最初の <h1>...</h1> を1つだけ除去する（最初の <h2> より前のもの）。

    HTML を直接本文に持つケースや、フロントマター/hr 等で先頭判定を逃した
    Markdown 変換結果に対応する。タイトル二重表示の原因となる本文冒頭の H1 は
    必ず最初の H2（節見出し）より前に現れるため、その範囲にある最初の H1 だけを
    削除する。本文後半に意図的に置かれた H1 は残す。
    """
    h1 = re.search(r"<h1\b[^>]*>.*?</h1>\s*", html, flags=re.IGNORECASE | re.DOTALL)
    if not h1:
        return html
    h2 = re.search(r"<h2\b", html, flags=re.IGNORECASE)
    if h2 and h1.start() > h2.start():
        return html  # 最初の H1 が最初の H2 より後ろなら本文見出しとみなし残す
    return (html[: h1.start()] + html[h1.end():]).lstrip()


def find_article_file(articles_dir: Path, slug: str, no_value: str) -> Path | None:
    candidates: list[Path] = []
    if slug:
        candidates.append(articles_dir / f"{slug}.md")
    for name in row_no_to_names(no_value):
        candidates.append(articles_dir / f"{name}.md")
    return first_existing(candidates)


def find_image_file(images_dir: Path, slug: str, no_value: str, image_name: str) -> Path | None:
    candidates: list[Path] = []
    # 0) 管理表に明示された画像ファイル名を最優先
    if image_name:
        candidates.append(images_dir / image_name)
        stem = Path(image_name).stem
        candidates += [images_dir / f"{stem}{ext}" for ext in IMAGE_EXTENSIONS]
    # 1) slug 起点
    if slug:
        candidates += [images_dir / f"{slug}{ext}" for ext in IMAGE_EXTENSIONS]
    # 2) No 起点（3桁ゼロ埋め / 素の No）
    for name in row_no_to_names(no_value):
        candidates += [images_dir / f"{name}{ext}" for ext in IMAGE_EXTENSIONS]
    return first_existing(candidates)


def extract_api_error(response: requests.Response) -> str:
    """WordPress REST API のエラーJSONから code/message を読みやすく抽出する。"""
    try:
        data = response.json()
        code = data.get("code", "")
        message = data.get("message", "")
        if message:
            return f"{response.status_code} {code}: {message}".strip()
    except ValueError:
        pass
    return f"{response.status_code}: {response.text[:500]}"


# --------------------------------------------------------------------------- #
# WordPress クライアント
# --------------------------------------------------------------------------- #
class WordPressClient:
    def __init__(self, base_url: str, username: str, app_password: str) -> None:
        self.base_url = normalize_url(base_url)
        self.api_base = f"{self.base_url}/wp-json/wp/v2"
        self.session = requests.Session()
        self.session.headers.update(basic_auth_header(username, app_password))
        self.session.headers.update({"User-Agent": "GitHub-Actions-WP-Auto-Post/2.0"})

        retry = Retry(
            total=4,
            backoff_factor=2,  # 2s, 4s, 8s, ...
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self._term_cache: dict[tuple[str, str], int] = {}

    def request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        kwargs.setdefault("timeout", 90)
        response = self.session.request(method, url, **kwargs)
        if response.status_code >= 400:
            raise RuntimeError(f"WordPress API エラー {extract_api_error(response)}")
        if not response.text:
            return None
        return response.json()

    def verify_auth(self) -> str:
        """認証確認。失敗時は分かりやすい例外を投げる。"""
        me = self.request("GET", "users/me", params={"context": "edit"})
        return me.get("name") or me.get("slug") or "(unknown)"

    def find_or_create_term(self, taxonomy: str, name: str) -> int:
        name = name.strip()
        if not name:
            return 0
        cache_key = (taxonomy, name.lower())
        if cache_key in self._term_cache:
            return self._term_cache[cache_key]

        endpoint = "categories" if taxonomy == "category" else "tags"
        data = self.request("GET", endpoint, params={"search": name, "per_page": 100})
        term_id = 0
        for item in data or []:
            if safe_str(item.get("name")).lower() == name.lower():
                term_id = int(item["id"])
                break
        if not term_id:
            created = self.request("POST", endpoint, json={"name": name})
            term_id = int(created["id"])

        self._term_cache[cache_key] = term_id
        return term_id

    def find_post_by_slug(self, slug: str, status: str) -> dict[str, Any] | None:
        if not slug:
            return None
        # draft/pending を検索するには context=edit と全 status 指定が必要
        params = {
            "slug": slug,
            "status": "publish,future,draft,pending,private",
            "context": "edit",
            "per_page": 10,
        }
        data = self.request("GET", "posts", params=params)
        if data:
            return data[0]
        return None

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
                f"{self.api_base}/media", headers=headers, data=f, timeout=300
            )
        if response.status_code >= 400:
            raise RuntimeError(f"メディアアップロード失敗 {extract_api_error(response)}")
        media_id = int(response.json()["id"])
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
        post_id: int | None = None,
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
        endpoint = f"posts/{post_id}" if post_id else "posts"
        return self.request("POST", endpoint, json=payload)


# --------------------------------------------------------------------------- #
# メイン
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WordPress 自動投稿スクリプト")
    parser.add_argument("--input", required=True, help="制作管理表（XLSX/CSV）のパス")
    parser.add_argument("--sheet", default=None, help="Excel シート名")
    parser.add_argument("--articles-dir", default="articles")
    parser.add_argument("--images-dir", default="eyecatches")
    parser.add_argument("--post-status", default="draft", choices=["draft", "pending", "publish"])
    parser.add_argument("--limit", type=int, default=0, help="投稿件数。0 で全件")
    parser.add_argument("--dry-run", action="store_true", help="投稿せず確認だけ行う")
    parser.add_argument("--sleep", type=float, default=1.0, help="投稿間の待機秒数")
    parser.add_argument("--keep-h1", action="store_true", help="本文先頭の H1 を除去しない")
    parser.add_argument(
        "--allow-duplicate",
        action="store_true",
        help="同一 slug の既存投稿があっても上書き更新する（既定はスキップ）",
    )
    parser.add_argument("--output-dir", default=".", help="結果 CSV の出力先")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    limit = None if args.limit is None or args.limit <= 0 else args.limit

    input_path = Path(args.input)
    articles_dir = Path(args.articles_dir)
    images_dir = Path(args.images_dir)

    df = read_table(input_path, args.sheet)
    cols = df.columns.tolist()
    col = {key: find_col(cols, cands) for key, cands in COLUMN_CANDIDATES.items()}

    print("=== 列マッピング結果 ===")
    for key, name in col.items():
        print(f"  {key:10s} -> {name}")
    print(f"  対象行数: {len(df)}  / モード: {'DRY-RUN' if args.dry_run else 'POST'}  / status: {args.post_status}")

    if col["kw"] is None and col["title"] is None:
        raise RuntimeError("KW 列・タイトル列のどちらも見つかりません。管理表の列名を確認してください。")

    wp: WordPressClient | None = None
    if not args.dry_run:
        wp = WordPressClient(
            env_required("WP_BASE_URL"),
            env_required("WP_USERNAME"),
            env_required("WP_APP_PASSWORD"),
        )
        try:
            user = wp.verify_auth()
            print(f"  認証OK: {user} としてログイン")
        except Exception as exc:
            raise RuntimeError(
                f"WordPress 認証に失敗しました。WP_BASE_URL / WP_USERNAME / WP_APP_PASSWORD を確認してください: {exc}"
            )

    results: list[dict[str, Any]] = []
    processed = 0

    for idx, row in df.iterrows():
        if limit is not None and processed >= limit:
            break

        no_value = safe_str(row.get(col["no"])) if col["no"] else str(idx + 1)
        if not no_value:
            no_value = str(idx + 1)
        kw = safe_str(row.get(col["kw"])) if col["kw"] else ""
        title = safe_str(row.get(col["title"])) if col["title"] else ""
        if not title:
            title = kw
        if not title:
            continue  # タイトルも KW も無い行はスキップ（空行対策）

        explicit_slug = safe_str(row.get(col["slug"])) if col["slug"] else ""
        slug = make_slug(explicit_slug or title, f"post-{int(idx) + 1:03d}")
        excerpt = safe_str(row.get(col["meta"])) if col["meta"] else ""
        category_names = split_terms(safe_str(row.get(col["category"])) if col["category"] else "")
        tag_names = split_terms(safe_str(row.get(col["tag"])) if col["tag"] else "")
        image_name = safe_str(row.get(col["image_name"])) if col["image_name"] else ""
        alt_text = safe_str(row.get(col["alt"])) if col["alt"] else ""
        if not alt_text:
            alt_text = f"{title}のアイキャッチ画像"

        article_path = find_article_file(articles_dir, explicit_slug, no_value)
        image_path = find_image_file(images_dir, explicit_slug, no_value, image_name)

        result: dict[str, Any] = {
            "no": no_value,
            "kw": kw,
            "title": title,
            "slug": slug,
            "article_file": str(article_path) if article_path else "",
            "image_file": str(image_path) if image_path else "（画像なし）",
            "status": "",
            "post_id": "",
            "post_link": "",
            "message": "",
        }

        if article_path is None:
            result["status"] = "skipped"
            result["message"] = "本文 Markdown が見つかりません。"
            results.append(result)
            print(f"[SKIP] No.{no_value} {title} -> 本文なし")
            continue

        md_text = article_path.read_text(encoding="utf-8")
        content_html = markdown_to_html(md_text, strip_h1=not args.keep_h1, title=title)

        if args.dry_run:
            result["status"] = "dry-run"
            img_note = "画像あり" if image_path else "画像なし"
            cat = "/".join(category_names) or "-"
            tag = "/".join(tag_names) or "-"
            result["message"] = f"投稿準備OK（{img_note} / cat:{cat} / tag:{tag}）"
            results.append(result)
            processed += 1
            print(f"[DRY-RUN] No.{no_value} {title} -> {result['message']}")
            continue

        try:
            assert wp is not None

            existing = None if args.allow_duplicate else wp.find_post_by_slug(slug, args.post_status)
            if existing:
                result["status"] = "skipped"
                result["post_id"] = existing.get("id", "")
                result["post_link"] = existing.get("link", "")
                result["message"] = "同一 slug の投稿が既に存在するためスキップ（--allow-duplicate で上書き可）"
                results.append(result)
                processed += 1
                print(f"[SKIP] No.{no_value} {title} -> 既存 slug: {slug}")
                continue

            category_ids = [i for i in (wp.find_or_create_term("category", n) for n in category_names) if i]
            tag_ids = [i for i in (wp.find_or_create_term("tag", n) for n in tag_names) if i]

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
            note = "（画像なし）" if not image_path else ""
            result["message"] = f"投稿成功 {note}".strip()
            print(f"[POSTED] No.{no_value} {title} -> {result['post_link']} {note}")

        except Exception as exc:
            result["status"] = "error"
            result["message"] = str(exc)
            print(f"[ERROR] No.{no_value} {title} -> {exc}")

        results.append(result)
        processed += 1
        if args.sleep > 0:
            time.sleep(args.sleep)

    # 結果 CSV
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_path = output_dir / f"results_{timestamp}.csv"
    pd.DataFrame(
        results,
        columns=[
            "no", "kw", "title", "slug", "article_file", "image_file",
            "status", "post_id", "post_link", "message",
        ],
    ).to_csv(result_path, index=False, encoding="utf-8-sig")

    # サマリ
    summary: dict[str, int] = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    print("=== 実行サマリ ===")
    for status, count in sorted(summary.items()):
        print(f"  {status}: {count}")
    print(f"結果CSV: {result_path}")

    # error があっても全体は完了扱い（CSV で追跡）。ただし戻り値で検知できるようにする。
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
