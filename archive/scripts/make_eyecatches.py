#!/usr/bin/env python3
"""
背景画像（eyecatches_base/）に制作管理表の「画像内テキスト」を重ね、
eyecatches/ にアイキャッチ画像（webp）を生成するスクリプト。

使い方:
    python make_eyecatches.py \
        --input data/seo_80kw_production_management.xlsx \
        --sheet 制作管理表 \
        --base-dir eyecatches_base \
        --out-dir eyecatches \
        --limit 1

背景画像の選択順:
    1. eyecatches_base/{アイキャッチ型}.{webp,jpg,jpeg,png}   例: 雨漏り系.webp
    2. eyecatches_base/{slug}.{...}
    3. eyecatches_base/default.{...}
    4. 見つからなければ単色背景を自動生成

出力ファイル名の決定順:
    1. 管理表「画像ファイル名」列（拡張子は .webp に置換）
    2. {slug}.webp
    3. {Noを3桁ゼロ埋め}.webp
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------- #
# 列名候補
# --------------------------------------------------------------------------- #
COLUMN_CANDIDATES: dict[str, list[str]] = {
    "no": ["No", "番号", "記事No", "ID"],
    "slug": ["スラッグ", "slug", "Slug"],
    "text": ["画像内テキスト", "画像内文言", "アイキャッチテキスト", "画像テキスト"],
    "type": ["アイキャッチ型", "アイキャッチタイプ", "デザイン型"],
    "image_name": ["画像ファイル名", "アイキャッチファイル名", "画像名"],
}

IMAGE_EXTENSIONS = [".webp", ".jpg", ".jpeg", ".png"]

# 日本語フォントの自動探索パス（環境差を吸収）
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "C:/Windows/Fonts/meiryob.ttc",
    "C:/Windows/Fonts/YuGothB.ttc",
]


# --------------------------------------------------------------------------- #
# ユーティリティ
# --------------------------------------------------------------------------- #
def safe_str(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def find_col(columns: list[str], candidates: list[str]) -> str | None:
    norm = {str(c).strip().lower(): c for c in columns}
    for cand in candidates:
        if cand.strip().lower() in norm:
            return norm[cand.strip().lower()]
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


def row_no_to_names(no_value: str) -> list[str]:
    raw = safe_str(no_value)
    if not raw:
        return []
    try:
        number = int(float(raw))
        return [f"{number:03d}", str(number)]
    except ValueError:
        return [raw]


def first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists() and p.is_file():
            return p
    return None


def split_lines(text: str) -> list[str]:
    """実際の改行・リテラル \\n・全角スペースなどで行分割する。"""
    text = text.replace("\\n", "\n").replace("\r\n", "\n").replace("\r", "\n")
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


def detect_font(explicit: str | None) -> str:
    if explicit:
        if Path(explicit).exists():
            return explicit
        raise FileNotFoundError(f"指定フォントが見つかりません: {explicit}")
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return path
    raise RuntimeError(
        "日本語フォントが見つかりません。--font でパスを指定するか、"
        "fonts-noto-cjk / fonts-ipafont-gothic をインストールしてください。"
    )


def load_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        # .ttc で index が必要な場合に備える
        return ImageFont.truetype(font_path, size, index=0)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def fit_font(
    draw: ImageDraw.ImageDraw,
    font_path: str,
    text: str,
    max_width: int,
    start_size: int,
    min_size: int = 18,
) -> ImageFont.FreeTypeFont:
    """text が max_width に収まる最大フォントサイズを二分せず段階縮小で求める。"""
    size = start_size
    font = load_font(font_path, size)
    while size > min_size and text_width(draw, text, font) > max_width:
        size -= 2
        font = load_font(font_path, size)
    return font


# --------------------------------------------------------------------------- #
# 画像生成
# --------------------------------------------------------------------------- #
def find_base_image(base_dir: Path, type_name: str, slug: str) -> Path | None:
    candidates: list[Path] = []
    if type_name:
        candidates += [base_dir / f"{type_name}{ext}" for ext in IMAGE_EXTENSIONS]
    if slug:
        candidates += [base_dir / f"{slug}{ext}" for ext in IMAGE_EXTENSIONS]
    candidates += [base_dir / f"default{ext}" for ext in IMAGE_EXTENSIONS]
    return first_existing(candidates)


def prepare_background(base_path: Path | None, width: int, height: int, bg_color: str) -> Image.Image:
    if base_path is None:
        return Image.new("RGB", (width, height), bg_color)
    img = Image.open(base_path).convert("RGB")
    # cover: アスペクト比を保って中央クロップ
    src_ratio = img.width / img.height
    dst_ratio = width / height
    if src_ratio > dst_ratio:
        new_w = int(img.height * dst_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / dst_ratio)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))
    return img.resize((width, height), Image.LANCZOS)


def draw_overlay(img: Image.Image, opacity: int) -> Image.Image:
    """下半分に黒の半透明グラデーションを敷き、文字を読みやすくする。"""
    if opacity <= 0:
        return img
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    h = img.height
    start = int(h * 0.30)
    for y in range(start, h):
        ratio = (y - start) / max(1, (h - start))
        odraw.line([(0, y), (img.width, y)], fill=(0, 0, 0, int(opacity * ratio)))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def render_eyecatch(
    *,
    base_path: Path | None,
    lines: list[str],
    out_path: Path,
    font_path: str,
    width: int,
    height: int,
    text_color: str,
    stroke_color: str,
    bg_color: str,
    overlay_opacity: int,
    quality: int,
) -> None:
    img = prepare_background(base_path, width, height, bg_color)
    img = draw_overlay(img, overlay_opacity)
    draw = ImageDraw.Draw(img)

    margin = int(width * 0.07)
    max_width = width - margin * 2

    title = lines[0] if lines else ""
    subs = lines[1:]

    title_font = fit_font(draw, font_path, title, max_width, start_size=int(height * 0.13))
    sub_font_size = max(20, int(title_font.size * 0.52))
    sub_fonts = [fit_font(draw, font_path, s, max_width, start_size=sub_font_size) for s in subs]

    # 行の高さ合計を計算して縦中央寄せ（やや下寄り）
    line_gap = int(title_font.size * 0.25)
    blocks: list[tuple[str, ImageFont.FreeTypeFont]] = []
    if title:
        blocks.append((title, title_font))
    blocks += list(zip(subs, sub_fonts))

    heights = []
    for text, font in blocks:
        bbox = draw.textbbox((0, 0), text, font=font)
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + line_gap * max(0, len(blocks) - 1)

    y = int(height * 0.52) - total_h // 2
    if y < margin:
        y = margin

    stroke_w = max(2, int(title_font.size * 0.05))
    for (text, font), h in zip(blocks, heights):
        w = text_width(draw, text, font)
        x = (width - w) // 2
        draw.text(
            (x, y),
            text,
            font=font,
            fill=text_color,
            stroke_width=stroke_w if font is title_font else max(1, stroke_w // 2),
            stroke_fill=stroke_color,
        )
        y += h + line_gap

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "WEBP", quality=quality, method=6)


# --------------------------------------------------------------------------- #
# メイン
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="背景画像へ画像内テキストを重ねてアイキャッチを生成")
    p.add_argument("--input", required=True, help="制作管理表（XLSX/CSV）")
    p.add_argument("--sheet", default=None, help="Excel シート名")
    p.add_argument("--base-dir", default="eyecatches_base", help="背景画像ディレクトリ")
    p.add_argument("--out-dir", default="eyecatches", help="出力ディレクトリ")
    p.add_argument("--font", default=None, help="日本語フォントのパス（未指定なら自動探索）")
    p.add_argument("--width", type=int, default=1200)
    p.add_argument("--height", type=int, default=630)
    p.add_argument("--text-color", default="#FFFFFF")
    p.add_argument("--stroke-color", default="#1A1A1A")
    p.add_argument("--bg-color", default="#23395B", help="背景画像が無い場合の単色")
    p.add_argument("--overlay-opacity", type=int, default=150, help="下部の暗幕の濃さ(0-255)")
    p.add_argument("--quality", type=int, default=88, help="WebP 品質(0-100)")
    p.add_argument("--limit", type=int, default=0, help="生成件数。0 で全件")
    p.add_argument("--overwrite", action="store_true", help="既存ファイルも上書き")
    p.add_argument("--dry-run", action="store_true", help="生成せず計画だけ表示")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    limit = None if args.limit <= 0 else args.limit

    df = read_table(Path(args.input), args.sheet)
    cols = df.columns.tolist()
    col = {k: find_col(cols, c) for k, c in COLUMN_CANDIDATES.items()}

    print("=== 列マッピング ===")
    for k, v in col.items():
        print(f"  {k:11s} -> {v}")

    if col["text"] is None:
        raise RuntimeError("「画像内テキスト」列が見つかりません。列名を確認してください。")

    font_path = detect_font(args.font) if not args.dry_run else (args.font or "(dry-run: 未解決)")
    if not args.dry_run:
        print(f"使用フォント: {font_path}")

    base_dir = Path(args.base_dir)
    out_dir = Path(args.out_dir)

    made = skipped = errors = 0
    processed = 0

    for idx, row in df.iterrows():
        if limit is not None and processed >= limit:
            break

        no_value = safe_str(row.get(col["no"])) if col["no"] else str(int(idx) + 1)
        if not no_value:
            no_value = str(int(idx) + 1)
        text = safe_str(row.get(col["text"])) if col["text"] else ""
        if not text:
            continue  # テキストが無い行はスキップ（空行対策）

        slug = safe_str(row.get(col["slug"])) if col["slug"] else ""
        type_name = safe_str(row.get(col["type"])) if col["type"] else ""
        image_name = safe_str(row.get(col["image_name"])) if col["image_name"] else ""

        # 出力ファイル名
        if image_name:
            out_name = Path(image_name).stem + ".webp"
        elif slug:
            out_name = f"{slug}.webp"
        else:
            names = row_no_to_names(no_value)
            out_name = f"{names[0]}.webp" if names else f"post-{int(idx)+1:03d}.webp"
        out_path = out_dir / out_name

        base_path = find_base_image(base_dir, type_name, slug)
        lines = split_lines(text)
        base_note = base_path.name if base_path else f"（背景なし→単色{args.bg_color}）"

        if not args.overwrite and out_path.exists():
            skipped += 1
            processed += 1
            print(f"[SKIP] No.{no_value} {out_name} 既存（--overwrite で上書き可）")
            continue

        if args.dry_run:
            processed += 1
            print(f"[DRY-RUN] No.{no_value} -> {out_path}  背景:{base_note}  text:{lines}")
            continue

        try:
            render_eyecatch(
                base_path=base_path,
                lines=lines,
                out_path=out_path,
                font_path=font_path,
                width=args.width,
                height=args.height,
                text_color=args.text_color,
                stroke_color=args.stroke_color,
                bg_color=args.bg_color,
                overlay_opacity=args.overlay_opacity,
                quality=args.quality,
            )
            made += 1
            processed += 1
            print(f"[OK] No.{no_value} -> {out_path}  背景:{base_note}")
        except Exception as exc:
            errors += 1
            processed += 1
            print(f"[ERROR] No.{no_value} {out_name} -> {exc}")

    print("=== サマリ ===")
    print(f"  生成:{made}  スキップ:{skipped}  エラー:{errors}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
