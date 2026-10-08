#!/usr/bin/env python3
"""Publish the reviewed Pixel Call Screening column using a verified ZIP bundle.

Runs inside GitHub Actions with the WordPress credentials in GitHub Secrets.
Does not accept unverified screenshots or substitute a generic eyecatch.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from wp_auto_post import WordPressClient  # noqa: E402

BASE = ROOT / "projects/cybernote-security-news"
LEDGER = BASE / "data/news_ledger.csv"
ARTICLES = BASE / "articles"
IMAGES = BASE / "eyecatches"
MEDIA = BASE / "media"
WORK = BASE / "results/pixel-column-bundle"
BUNDLE = BASE / "uploads/pixel-call-screening-cybernote-package.zip"
DRAFT = BASE / "drafts/pixel-call-screening-scam-call-2026.md"
SLUG = "pixel-call-screening-scam-call-2026"
ARTICLE = ARTICLES / (SLUG + ".md")
EYECATCH = IMAGES / (SLUG + ".png")
NOFILE = WORK / "target_no.txt"
TITLE = "【コラム】通話スクリーニングで詐欺電話を回避　2時間後に電話が使えなくなる自動音声をAIが受けた実例"
DESCRIPTION = "Pixelの通話スクリーニングで、2時間後に電話が使えなくなると告げる詐欺電話をAIが代わりに受けた実例を紹介。文字起こしで自動音声を見抜けた体験と、手口・設定方法・注意点を解説します。"
SOURCE_FILES = {
    "pixel-call-screening-eyecatch.png": (
        "c785f6e398cf57a578c2f2e3271edf0c134c4b9e87f1c44463afafe6bf092528", (1200, 800)
    ),
    "pixel-call-screening-case1.png": (
        "22eed262ed5d80d41e605cb907d6ac97b775963b482ac999548efb39ddd017b5", (699, 1446)
    ),
    "pixel-call-screening-case2.png": (
        "c6e8aaa9f97055cf3731c01c0c564a70021abae9b7f0c95d3f9ff28b461fe88a", (699, 1446)
    ),
}


def get_rows():
    with LEDGER.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or ()), list(reader)


def save_rows(fields, rows):
    with LEDGER.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prepare():
    if not BUNDLE.is_file():
        raise RuntimeError("指定ZIPがありません。GitHubの uploads フォルダへZIPをアップロードしてください: " + str(BUNDLE))
    WORK.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)
    ARTICLES.mkdir(parents=True, exist_ok=True)
    with ZipFile(BUNDLE) as bundle:
        names = set(bundle.namelist())
        if not set(SOURCE_FILES).issubset(names):
            raise RuntimeError("ZIP内の3枚のPNGが不足しています")
        if len(names) != len(bundle.namelist()):
            raise RuntimeError("ZIPに重複したパスが含まれています")
        for name, (expected_sha, size) in SOURCE_FILES.items():
            raw = bundle.read(name)
            digest = hashlib.sha256(raw).hexdigest()
            if digest != expected_sha:
                raise RuntimeError(name + ": 元画像とのSHA-256照合に失敗しました")
            source = WORK / name
            source.write_bytes(raw)
            with Image.open(source) as im:
                im.load()
                if im.format != "PNG" or im.size != size:
                    raise RuntimeError(name + ": PNG形式・寸法の検査に失敗しました")
            if name != "pixel-call-screening-eyecatch.png":
                shutil.copyfile(source, MEDIA / name)

    subprocess.run(
        [sys.executable, "prepare_eyecatch.py", str(WORK / "pixel-call-screening-eyecatch.png"), str(EYECATCH)],
        check=True,
    )
    if not DRAFT.is_file():
        raise RuntimeError("確認済み記事のGitHub下書きが見つかりません")
    article = DRAFT.read_text(encoding="utf-8")
    if not article.startswith("---\n"):
        raise RuntimeError("記事のYAMLフロントマターが不足しています")
    if article.count("PIXEL_CASE1_IMAGE_URL") != 1 or article.count("PIXEL_CASE2_IMAGE_URL") != 1:
        raise RuntimeError("記事の実例画像プレースホルダが不足・重複しています")
    if len(re.findall(r"https://www\\.cybernote\\.click/", article)) < 3:
        raise RuntimeError("記事のCyberNote内部リンクが3本未満です")
    # Avoid YAML string escaping problems: use json.dumps for double-quoted strings.
    import json
    fields = (
        "rank_math_title: " + json.dumps(TITLE, ensure_ascii=False) + "\n"
        "rank_math_description: " + json.dumps(DESCRIPTION, ensure_ascii=False) + "\n"
        'rank_math_focus_keyword: "通話スクリーニング"\n'
    )
    article = article.replace("---\n", "---\n" + fields, 1)
    ARTICLE.write_text(article, encoding="utf-8")
    header, rows = get_rows()
    existing = next((r for r in rows if (r.get("スラッグ") or "").strip() == SLUG), None)
    if existing is None:
        n = str(max((int(r.get("No") or "0") for r in rows if (r.get("No") or "").strip().isdigit()), default=0) + 1)
        existing = {key: "" for key in header}
        existing.update({
            "No": n,
            "収集日": "2026-10-08",
            "公開予定日": "2026-10-08",
            "記事分類": "コラム",
            "指定KW": "通話スクリーニング",
            "記事タイトル案": TITLE,
            "記事タイトル": TITLE,
            "スラッグ": SLUG,
            "メタディスクリプション": DESCRIPTION,
            "WPカテゴリ": "サイバーセキュリティ",
            "タグ案": "Google Pixel,通話スクリーニング,詐欺電話,迷惑電話,自動音声",
            "記事ファイル": "projects/cybernote-security-news/articles/" + SLUG + ".md",
            "画像ファイル名": "projects/cybernote-security-news/eyecatches/" + SLUG + ".png",
            "主な出典URL": "https://www.kokusen.go.jp/news/data/n-20241219_1.html",
            "内部リンクURL": "https://www.cybernote.click/2026/10/04/sagawa-data-breach-2026/",
            "目標文字数": "3900",
            "生成ステータス": "生成済み",
            "レビュー判定": "確認済み",
            "投稿ステータス": "未投稿",
            "候補ID": "20261008-PIXEL-CALL-SCREENING",
        })
        rows.append(existing)
    else:
        n = existing["No"]
        existing["記事ファイル"] = "projects/cybernote-security-news/articles/" + SLUG + ".md"
        existing["画像ファイル名"] = "projects/cybernote-security-news/eyecatches/" + SLUG + ".png"
        existing["生成ステータス"] = "生成済み"
        existing["公開停止"] = ""
    save_rows(header, rows)
    NOFILE.write_text(n, encoding="utf-8")
    print("PREPARED: No." + n, flush=True)


def find_matching_media(wp, image):
    # Reuse only the same screenshot, never a merely similarly named image.
    try:
        candidates = wp.request("GET", "media", params={"search":image.stem, "per_page":50})
        if isinstance(candidates, list):
            for candidate in candidates:
                ident = int(candidate.get("id") or 0)
                if not ident:
                    continue
                same, url, _ = wp.media_matches_file(ident, image)
                if same and url:
                    return url
    except Exception as exc:
        print("既存画像の検索ができませんでした: " + str(exc), flush=True)
    return ""


def embed():
    if not NOFILE.exists() or not ARTICLE.exists():
        raise RuntimeError("先に prepare を実行してください")
    wp = WordPressClient(
        os.environ["WP_BASE_URL"],
        os.environ["WP_USERNAME"],
        os.environ["WP_APP_PASSWORD"],
    )
    article = ARTICLE.read_text(encoding="utf-8")
    for name, placeholder, alt in (
        ("pixel-call-screening-case1.png", "PIXEL_CASE1_IMAGE_URL", "Pixelの通話スクリーニングでNTTを名乗る自動音声を文字にした記録"),
        ("pixel-call-screening-case2.png", "PIXEL_CASE2_IMAGE_URL", "Pixelの通話スクリーニングで相手が途中切断した記録"),
    ):
        source = MEDIA / name
        url = find_matching_media(wp, source)
        if not url:
            _, url = wp.upload_media(source, alt_text=alt)
        if not url.startswith("https://"):
            raise RuntimeError(name + ": WordPress画像URLを取得できません")
        if article.count(placeholder) != 1:
            raise RuntimeError("本文の画像挿入位置が不正: " + placeholder)
        article = article.replace(placeholder, url)
        print("SCREENSHOT_OK: " + url, flush=True)
    if "PIXEL_CASE" in article:
        raise RuntimeError("未変換の画像プレースホルダが残っています")
    ARTICLE.write_text(article, encoding="utf-8")


def finalize():
    target = NOFILE.read_text(encoding="utf-8").strip()
    result_files = list((BASE / "results").glob("results_*.csv"))
    if not result_files:
        raise RuntimeError("WordPress投稿結果ファイルが見つかりません")
    recent = max(result_files, key=lambda p: p.stat().st_mtime)
    with recent.open("r", encoding="utf-8-sig", newline="") as fh:
        matching = [r for r in csv.DictReader(fh) if (r.get("no") or "").strip() == target]
    if not matching:
        raise RuntimeError("WordPress投稿結果にNo." + target + "がありません")
    r = matching[-1]
    status = (r.get("status") or "").strip().lower()
    if status not in {"posted", "updated"} or not r.get("post_id") or not r.get("post_link"):
        raise RuntimeError("WordPress投稿失敗: " + str(r))
    if not (r["post_link"].startswith("https://www.cybernote.click/") or r["post_link"].startswith("https://cybernote.click/")):
        raise RuntimeError("投稿URLがCyberNoteのものではありません")
    header, rows = get_rows()
    matches = [row for row in rows if (row.get("No") or "").strip() == target]
    if len(matches) != 1:
        raise RuntimeError("管理簿Noに重複があります")
    record = matches[0]
    record.update({
        "WP投稿ID": r["post_id"],
        "WP投稿URL": r["post_link"],
        "投稿ステータス": "公開済み",
        "最終更新日時": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "エラー内容": "",
    })
    save_rows(header, rows)
    print("PUBLICATION_OK " + r["post_link"], flush=True)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("## Pixel通話スクリーニング\n\n公開URL: " + r["post_link"] + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "embed", "finalize"])
    args = parser.parse_args()
    {"prepare": prepare, "embed": embed, "finalize": finalize}[args.mode]()
