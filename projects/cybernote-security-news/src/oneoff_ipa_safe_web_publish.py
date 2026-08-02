#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import math
import os
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from wp_auto_post import WordPressClient, env_required, safe_str  # noqa: E402

JST = ZoneInfo("Asia/Tokyo")
TARGET_NO = "17"
TARGET_DATE = "2026-08-03"
SLUG = "ipa-safe-web-development-guide"
TITLE = "【保存版】IPA「安全なウェブサイトの作り方」とは？11の脆弱性と対策を解説"
LEDGER = REPO_ROOT / "projects/cybernote-security-news/data/news_ledger.csv"
ARTICLES_DIR = REPO_ROOT / "projects/cybernote-security-news/articles"
IMAGES_DIR = REPO_ROOT / "projects/cybernote-security-news/eyecatches"
RESULTS_DIR = REPO_ROOT / "projects/cybernote-security-news/results"
IMAGE_PATH = IMAGES_DIR / f"{SLUG}.png"
ARTICLE_PATH = ARTICLES_DIR / f"{SLUG}.md"


def read_ledger() -> tuple[list[str], list[dict[str, str]]]:
    with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_ledger(fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with LEDGER.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def ensure_ledger_row() -> tuple[list[str], list[dict[str, str]], dict[str, str]]:
    fieldnames, rows = read_ledger()
    values = {
        "No": TARGET_NO,
        "収集日": TARGET_DATE,
        "公開予定日": TARGET_DATE,
        "記事分類": "ウェブセキュリティ",
        "指定KW": "IPA 安全なウェブサイトの作り方",
        "話題性スコア": "90",
        "記事タイトル案": TITLE,
        "記事タイトル": TITLE,
        "スラッグ": SLUG,
        "メタディスクリプション": "IPA「安全なウェブサイトの作り方」を初心者向けに解説。11種類の脆弱性、根本的な対策、公開後の運用、開発時の確認手順をまとめます。",
        "WPカテゴリ": "サイバーセキュリティ",
        "タグ案": "IPA,ウェブセキュリティ,脆弱性,安全なウェブサイトの作り方,Web開発",
        "記事ファイル": str(ARTICLE_PATH.relative_to(REPO_ROOT)),
        "画像ファイル名": str(IMAGE_PATH.relative_to(REPO_ROOT)),
        "主な出典URL": "https://www.ipa.go.jp/security/vuln/websecurity/about.html",
        "内部リンクURL": "https://www.cybernote.click/wp-security-checker-guide/",
        "目標文字数": "7205",
        "生成ステータス": "生成済み",
        "レビュー判定": "未確認",
        "公開停止": "",
    }
    target = next((row for row in rows if str(row.get("No", "")).strip() == TARGET_NO), None)
    if target is None:
        target = {name: "" for name in fieldnames}
        target.update(values)
        rows.append(target)
        print(f"管理簿にNo.{TARGET_NO}を追加しました。")
    else:
        preserved = {
            key: target.get(key, "")
            for key in ("WP投稿ID", "WP投稿URL", "投稿ステータス", "最終更新日時", "エラー内容")
        }
        target.update(values)
        target.update(preserved)
        print(f"管理簿のNo.{TARGET_NO}を再利用します。")
    write_ledger(fieldnames, rows)
    return fieldnames, rows, target


def font_path(patterns: tuple[str, ...]) -> str:
    root = Path("/usr/share/fonts/opentype/noto")
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        if matches:
            return str(matches[0])
    raise RuntimeError(f"Noto Sans CJK font was not found: {patterns}")


def generate_eyecatch() -> None:
    width, height = 1200, 800
    image = Image.new("RGB", (width, height), "#071A2D")
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            glow = max(0.0, 1.0 - math.hypot(x - 930, y - 250) / 760)
            pixels[x, y] = (
                int(7 + 7 * glow),
                int(26 + 35 * glow),
                int(45 + 46 * glow),
            )

    draw = ImageDraw.Draw(image)
    bold = font_path(("NotoSansCJK-Bold.ttc", "*Sans*CJK*Bold*"))
    regular = font_path(("NotoSansCJK-Regular.ttc", "*Sans*CJK*Regular*"))
    badge_font = ImageFont.truetype(bold, 28)
    title_font = ImageFont.truetype(bold, 63)
    subtitle_font = ImageFont.truetype(bold, 39)
    body_font = ImageFont.truetype(regular, 25)
    footer_font = ImageFont.truetype(bold, 23)

    for offset in range(0, 900, 110):
        x0 = 650 + offset // 3
        draw.line((x0, 50, x0 + 260, 310), fill="#173B55", width=2)
        draw.ellipse((x0 + 253, 303, x0 + 267, 317), outline="#22D3EE", width=2)

    draw.rounded_rectangle((680, 135, 1110, 560), radius=28, fill="#0D2940", outline="#3A6078", width=3)
    draw.rounded_rectangle((700, 157, 1090, 540), radius=20, fill="#F4F8FB")
    draw.rectangle((700, 157, 1090, 215), fill="#DCE8EF")
    for i, color in enumerate(("#F43F5E", "#F59E0B", "#34D399")):
        cx = 730 + i * 31
        draw.ellipse((cx - 8, 170, cx + 8, 186), fill=color)
    draw.rounded_rectangle((825, 172, 1058, 194), radius=10, fill="#B7CBD7")
    draw.rounded_rectangle((735, 255, 1055, 287), radius=12, fill="#D9E4EA")
    draw.rounded_rectangle((735, 312, 1005, 337), radius=10, fill="#D9E4EA")
    draw.rounded_rectangle((735, 367, 1035, 392), radius=10, fill="#D9E4EA")
    draw.rounded_rectangle((735, 422, 940, 469), radius=14, fill="#22D3EE")

    shield = [(955, 300), (1055, 335), (1040, 445), (1005, 500), (955, 535), (905, 500), (870, 445), (855, 335)]
    draw.polygon(shield, fill="#0B1F33", outline="#34D399")
    draw.line((903, 412, 940, 449), fill="#34D399", width=18)
    draw.line((940, 449, 1012, 370), fill="#34D399", width=18)

    draw.rounded_rectangle((76, 75, 330, 124), radius=20, fill="#123A55", outline="#22D3EE", width=2)
    draw.text((99, 85), "保存版・IPA解説", font=badge_font, fill="#D8F7FF")
    draw.text((74, 174), "安全なウェブサイト", font=title_font, fill="#F7FAFC")
    draw.text((74, 255), "の作り方", font=title_font, fill="#F7FAFC")
    draw.text((76, 365), "11の脆弱性と対策", font=subtitle_font, fill="#22D3EE")
    draw.text((77, 430), "設計・実装・運用の要点", font=body_font, fill="#C5D6E0")

    draw.rounded_rectangle((68, 650, 1132, 732), radius=22, fill="#0B2539", outline="#28516A", width=2)
    footer = "入力を信用しない  ×  命令とデータを分ける"
    bbox = draw.textbbox((0, 0), footer, font=footer_font)
    draw.text(((width - (bbox[2] - bbox[0])) // 2, 675), footer, font=footer_font, fill="#EAF5F8")

    IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(IMAGE_PATH, format="PNG", optimize=True)
    with Image.open(IMAGE_PATH) as checked:
        if checked.format != "PNG" or checked.size != (1200, 800):
            raise RuntimeError(f"Invalid eyecatch: {checked.format} {checked.size}")
    print(f"Eyecatch generated: {IMAGE_PATH.relative_to(REPO_ROOT)} ({IMAGE_PATH.stat().st_size} bytes)")


def quality_gate() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "article_quality_check.py"),
            "--input", str(LEDGER),
            "--articles-dir", str(ARTICLES_DIR),
            "--results", str(RESULTS_DIR / "article_quality_results.csv"),
            "--nos", TARGET_NO,
            "--include-unstarted",
            "--mode", "geo",
            "--fail-on-error",
        ],
        cwd=REPO_ROOT,
        check=True,
    )


def latest_post_result() -> dict[str, str]:
    files = sorted(RESULTS_DIR.glob("results_*.csv"))
    if not files:
        raise RuntimeError("投稿結果CSVが見つかりません。")
    with files[-1].open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    matches = [row for row in rows if str(row.get("no", "")).strip() == TARGET_NO]
    if not matches:
        raise RuntimeError(f"No.{TARGET_NO}の投稿結果が見つかりません。")
    result = matches[-1]
    status = (result.get("status") or "").strip().lower()
    if status not in {"posted", "updated"}:
        raise RuntimeError(
            f"WordPress投稿に失敗しました: {status} / "
            f"{result.get('error_content') or result.get('message')}"
        )
    return result


def create_published_post() -> dict[str, str]:
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "wp_auto_post.py"),
            "--input", str(LEDGER),
            "--articles-dir", str(ARTICLES_DIR),
            "--images-dir", str(IMAGES_DIR),
            "--post-status", "publish",
            "--write-mode", "create_only",
            "--category", "サイバーセキュリティ",
            "--nos", TARGET_NO,
            "--limit", "1",
            "--skip-auth-check",
            "--skip-internal-link-resolution",
            "--skip-existing-check",
            "--output-dir", str(RESULTS_DIR),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    return latest_post_result()


def publish_idempotently(target: dict[str, str]) -> tuple[str, str, str]:
    if target.get("投稿ステータス") == "公開済み" and target.get("WP投稿URL"):
        print(f"管理簿上すでに公開済みです: {target['WP投稿URL']}")
        return target.get("WP投稿ID", ""), target["WP投稿URL"], "already_published"

    wp = WordPressClient(
        env_required("WP_BASE_URL"),
        env_required("WP_USERNAME"),
        env_required("WP_APP_PASSWORD"),
    )
    print("既存投稿をslugで確認します。")
    existing = wp.find_post_by_slug(SLUG, "publish")
    if existing:
        post_id = int(existing.get("id") or 0)
        status = safe_str(existing.get("status"))
        link = safe_str(existing.get("link"))
        if status != "publish":
            print(f"既存投稿を公開します: id={post_id}, status={status}")
            updated = wp.request("POST", f"posts/{post_id}", json={"status": "publish"})
            link = safe_str(updated.get("link")) or link
            post_id = int(updated.get("id") or post_id)
            return str(post_id), link, "published_existing"
        print(f"既存の公開投稿を再利用します: id={post_id}, {link}")
        return str(post_id), link, "already_published"

    print("既存投稿がないため、記事とアイキャッチを新規公開します。")
    result = create_published_post()
    return str(result.get("post_id", "")), str(result.get("post_link", "")), "published_new"


def update_published_ledger(
    fieldnames: list[str],
    rows: list[dict[str, str]],
    target: dict[str, str],
    post_id: str,
    post_link: str,
    action: str,
) -> None:
    if not post_link:
        raise RuntimeError("公開後のWordPress URLが取得できませんでした。")
    target["投稿ステータス"] = "公開済み"
    target["WP投稿ID"] = post_id
    target["WP投稿URL"] = post_link
    target["最終更新日時"] = dt.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    target["エラー内容"] = ""
    write_ledger(fieldnames, rows)
    print(f"WordPress publish: {action} / post_id={post_id} / {post_link}")


def main() -> int:
    if not ARTICLE_PATH.exists():
        raise FileNotFoundError(f"記事ファイルが見つかりません: {ARTICLE_PATH}")
    fieldnames, rows, target = ensure_ledger_row()
    generate_eyecatch()
    quality_gate()
    post_id, post_link, action = publish_idempotently(target)
    update_published_ledger(fieldnames, rows, target, post_id, post_link, action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
