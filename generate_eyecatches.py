#!/usr/bin/env python3
"""OpenAI画像生成APIで記事アイキャッチを1件ずつ生成する。"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import io
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image

TARGET_WIDTH = 1200
TARGET_HEIGHT = 800

COL_NO = ["No", "番号", "記事No", "ID"]
COL_KW = ["指定KW", "管理KW", "KW", "キーワード"]
COL_TITLE = ["記事タイトル", "記事タイトル案", "タイトル"]
COL_FILENAME = ["画像ファイル名(PNG)", "画像ファイル名", "ファイル名"]
COL_PROMPT = ["完成プロンプト", "個別プロンプト", "プロンプト"]

PROMPT_SUFFIX = (
    "\n\n【生成時の最終確認】\n"
    "・1記事につき1枚だけ生成する\n"
    "・横長3:2、最終出力1200×800px、PNG\n"
    "・コラージュ、グリッド、分割画面、複数案の一覧にしない\n"
    "・記事番号、会社ロゴ、架空ロゴ、URLを入れない\n"
    "・日本語文字は指定どおり正確に、大きく読みやすく表示する\n"
    "・文字化け、誤字、文字切れ、画面外へのはみ出しを発生させない\n"
    "・対象記事以外の内容を混ぜない\n"
)


def find_col(columns: list[str], candidates: list[str]) -> str | None:
    normalized = {str(c).strip().lower(): c for c in columns}
    for candidate in candidates:
        key = candidate.lower()
        if key in normalized:
            return normalized[key]
    for candidate in candidates:
        key = candidate.lower()
        for column_key, original in normalized.items():
            if key in column_key or column_key in key:
                return original
    return None


def safe_str(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def parse_no(value: Any) -> int | None:
    text = safe_str(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def load_api_key() -> str:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEYが未設定です。.envまたはGitHub Secretsを確認してください。")
    return key


def to_png(image_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT
    source_ratio = image.width / image.height
    if source_ratio > target_ratio:
        new_width = int(image.height * target_ratio)
        left = (image.width - new_width) // 2
        image = image.crop((left, 0, left + new_width, image.height))
    elif source_ratio < target_ratio:
        new_height = int(image.width / target_ratio)
        top = (image.height - new_height) // 2
        image = image.crop((0, top, image.width, top + new_height))
    image = image.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
    output = io.BytesIO()
    image.save(output, "PNG")
    return output.getvalue()


def generate_one(client: Any, prompt: str, model: str, size: str,
                 quality: str, max_retries: int) -> bytes:
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.images.generate(
                model=model, prompt=prompt, size=size, n=1, quality=quality
            )
            encoded = response.data[0].b64_json
            if not encoded:
                raise RuntimeError("画像データが返されませんでした")
            return base64.b64decode(encoded)
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                wait = 2 ** (attempt + 1)
                print(f"  retry {attempt + 1}/{max_retries}: {exc}")
                time.sleep(wait)
    raise RuntimeError(str(last_error))


def article_context(md_dir: Path, no: int, max_chars: int = 3500) -> str:
    for filename in (f"{no:03d}.md", f"{no}.md"):
        path = md_dir / filename
        if path.exists():
            text = path.read_text(encoding="utf-8")
            text = __import__("re").sub(r"<[^>]+>|https?://\S+", "", text)
            return text[:max_chars]
    return ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="記事アイキャッチを1件ずつ生成する")
    parser.add_argument("--input", default="data/wordpress-security-production.xlsx")
    parser.add_argument("--sheet", default="画像生成プロンプト一覧")
    parser.add_argument("--out-dir", default="projects/wordpress-security/eyecatches")
    parser.add_argument("--results", default="projects/wordpress-security/results/eyecatch_generation_results.csv")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--model", default="gpt-image-1")
    parser.add_argument("--size", default="1536x1024")
    parser.add_argument("--quality", default="high", choices=["low","medium","high","auto"])
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--extra-instructions", default="")
    parser.add_argument("--md-priority", action="store_true")
    parser.add_argument("--md-dir", default="projects/wordpress-security/articles")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start_no = parse_no(args.start) if args.start else None
    end_no = parse_no(args.end) if args.end else None
    limit = None if args.limit <= 0 else args.limit

    df = pd.read_excel(args.input, sheet_name=args.sheet, dtype=object)
    columns = list(df.columns)
    no_col = find_col(columns, COL_NO)
    kw_col = find_col(columns, COL_KW)
    title_col = find_col(columns, COL_TITLE)
    filename_col = find_col(columns, COL_FILENAME)
    prompt_col = find_col(columns, COL_PROMPT)
    if no_col is None or prompt_col is None:
        raise RuntimeError("No列または完成プロンプト列が見つかりません")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    client = None
    if not args.dry_run:
        from openai import OpenAI
        client = OpenAI(api_key=load_api_key())

    results: list[dict[str, Any]] = []
    processed = 0
    for _, row in df.iterrows():
        no = parse_no(row.get(no_col))
        if no is None:
            continue
        if start_no is not None and no < start_no:
            continue
        if end_no is not None and no > end_no:
            continue
        if limit is not None and processed >= limit:
            break

        kw = safe_str(row.get(kw_col)) if kw_col else ""
        title = safe_str(row.get(title_col)) if title_col else ""
        prompt = safe_str(row.get(prompt_col))
        filename = safe_str(row.get(filename_col)) if filename_col else ""
        filename = Path(filename).name if filename else f"{no:03d}.png"
        if not filename.lower().endswith(".png"):
            filename = f"{Path(filename).stem}.png"
        output_path = out_dir / filename

        result = {
            "No":f"{no:03d}","指定KW":kw,"記事タイトル":title,
            "保存ファイル名":str(output_path),"status":"","width":"","height":"",
            "error":"","generated_at":""
        }
        if not prompt:
            result["status"] = "error"
            result["error"] = "完成プロンプトが空です"
            results.append(result)
            continue
        if output_path.exists() and not args.force:
            result["status"] = "skipped"
            result["error"] = "既存ファイル"
            results.append(result)
            continue

        full_prompt = prompt
        if args.md_priority:
            context = article_context(Path(args.md_dir), no)
            if context:
                full_prompt = (
                    f"【最優先の記事本文コンテキスト】\n{context}\n\n"
                    f"【同じ記事Noの画像設計】\n{prompt}"
                )
        full_prompt += PROMPT_SUFFIX
        if args.extra_instructions.strip():
            full_prompt += "\n\n【追加指示】\n" + args.extra_instructions.strip()

        if args.dry_run:
            result["status"] = "dry-run"
            print(f"[DRY-RUN] {no:03d} -> {output_path}")
        else:
            try:
                raw = generate_one(client, full_prompt, args.model, args.size,
                                   args.quality, args.max_retries)
                output_path.write_bytes(to_png(raw))
                result["status"] = "generated"
                result["width"] = TARGET_WIDTH
                result["height"] = TARGET_HEIGHT
                result["generated_at"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[OK] {no:03d} -> {output_path}")
            except Exception as exc:
                result["status"] = "error"
                result["error"] = str(exc)
                print(f"[ERROR] {no:03d} {exc}")
        results.append(result)
        processed += 1

    results_path = Path(args.results)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(results_path, index=False, encoding="utf-8-sig")
    print(f"結果CSV: {results_path}")
    return 1 if any(r["status"] == "error" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
