#!/usr/bin/env python3
"""
OpenAI 画像生成 API（gpt-image-1）で SEO 記事用アイキャッチを 1 件ずつ生成する。

入力 : data/seo_80kw_production_management_v2_with_image_prompt_sheet.xlsx
シート: 画像生成プロンプト一覧（No / 指定KW / 記事タイトル / 画像ファイル名(PNG) / 完成プロンプト）
出力 : eyecatches/001.png 〜 eyecatches/080.png（1200x800 / 3:2 / PNG）
結果 : results/eyecatch_generation_results.csv

OPENAI_API_KEY は .env から読み込みます（コードに直書きしない）。

使い方:
    python generate_eyecatches.py --start 001 --end 005
    python generate_eyecatches.py --start 001 --end 080 --skip-existing
    python generate_eyecatches.py --start 001 --end 010 --force
"""

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

# 出力の最終仕様
TARGET_WIDTH = 1200
TARGET_HEIGHT = 800  # 3:2

# 列名候補（多少のブレを吸収）
COL_NO = ["No", "番号", "記事No", "ID"]
COL_KW = ["指定KW", "管理KW", "KW", "キーワード"]
COL_TITLE = ["記事タイトル", "記事タイトル案", "タイトル"]
COL_FILENAME = ["画像ファイル名(PNG)", "画像ファイル名", "ファイル名"]
COL_PROMPT = ["完成プロンプト", "個別プロンプト", "プロンプト"]

# 日本語文字崩れ対策などの追加指示（プロンプト末尾に付与）
# 全 No 共通で付与する「厳守ルール」。対象記事の内容(完成プロンプト)に対して追加する。
PROMPT_SUFFIX = (
    "\n\n# 追加指示（厳守ルール）\n"
    "・1回につき1記事分だけ生成する\n"
    "・複数画像のコラージュ、グリッド、一覧、分割レイアウトにしない（必ず1枚の画像）\n"
    "・左上などに「001」「002」などの番号は入れない\n"
    "・3:2比率（横長）で生成する\n"
    "・PNG形式で保存する想定の高解像度・高品質にする\n"
    "・記事アイキャッチとして使える完成度にする\n"
    "・日本語文字は大きく、読みやすく、崩れないようにする（文字化け・文字切れ厳禁）\n"
    "・実写写真そのままではなく、ブログ記事サムネイル風／YouTubeサムネイル風／SEO記事アイキャッチ風にする\n"
    "・会社ロゴや架空のロゴは入れない\n"
    "・松山市版の地域感を入れる（松山城など愛媛・松山らしさを背景に少し）\n"
    "・過度にシンプルにしない。余白を残しすぎない（情報量のある強めのデザイン）\n"
    "・各記事テーマ（雨漏り・外壁・屋根・防水・塗装など）に合った背景・構図にする\n"
    "・対象No以外の内容を混ぜない。別Noの記事内容やExcelの別Noの情報を混ぜない\n"
    "\n# レイアウト方向性（参考デザインに寄せる）\n"
    "・上部に大きなメインコピーを配置し、太い縁取りで視認性を高める\n"
    "・メインコピーの下に、帯（リボン）状のサブコピーを置く\n"
    "・「松山市版」など地域ラベルを小さく目立つ位置に置く\n"
    "・補助コピーは帯やラベル、吹き出しで配置する\n"
    "・小見出し・チェック項目はチェックボックス付きのリストにして左側にまとめる\n"
    "・劣化箇所などの要素には引き出し線つきのラベルを付けて指し示す\n"
    "・必要に応じて症状写真の小さなインセット（はめ込み）を入れる\n"
    "・下部に手順やベネフィットを示す帯（ステップ表示）を入れてもよい\n"
    "・濃紺・赤・黄・白・緑などを使った高コントラスト配色にする\n"
    "・ヘルメットの職人や住宅外観など、記事テーマに合う人物・被写体を右側に配置する\n"
)


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
    """No を整数化。数値でなければ None（"使い方" などの説明行を除外）。"""
    s = safe_str(value)
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def load_api_key() -> str:
    """.env から OPENAI_API_KEY を読み込む（python-dotenv があれば利用）。"""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        # dotenv 未導入でも環境変数に直接入っていれば使う
        _load_dotenv_minimal()
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY が見つかりません。プロジェクト直下の .env に "
            "OPENAI_API_KEY=sk-... を記載してください（コードに直書きしないこと）。"
        )
    return key


def _load_dotenv_minimal() -> None:
    """python-dotenv が無い場合の簡易 .env パーサ。"""
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def to_3_2_png(image_bytes: bytes, width: int, height: int) -> tuple[bytes, int, int]:
    """生成画像を 3:2 にカバークロップして width x height へ整え、PNG bytes を返す。"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    target_ratio = width / height
    src_ratio = img.width / img.height
    if src_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    elif src_ratio < target_ratio:
        new_h = int(img.width / target_ratio)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))
    img = img.resize((width, height), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, "PNG")
    return out.getvalue(), img.width, img.height


def generate_one(client: Any, prompt: str, *, model: str, size: str,
                 quality: str, max_retries: int) -> bytes:
    """1 件だけ画像を生成し、Base64 をデコードして PNG bytes を返す。最大 max_retries 回リトライ。"""
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):  # 初回 + リトライ
        try:
            resp = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                n=1,            # 複数まとめて生成しない
                quality=quality,
            )
            b64 = resp.data[0].b64_json
            if not b64:
                raise RuntimeError("API レスポンスに画像データ(b64_json)がありません。")
            return base64.b64decode(b64)
        except Exception as exc:  # noqa: BLE001 - 失敗しても次へ進めるため握る
            last_error = exc
            if attempt < max_retries:
                wait = 2 ** (attempt + 1)  # 2s, 4s, ...
                print(f"    リトライ {attempt + 1}/{max_retries}（{wait}s 後）: {exc}")
                time.sleep(wait)
    raise RuntimeError(str(last_error))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="OpenAI でアイキャッチ画像を 1 件ずつ生成する")
    p.add_argument("--input", default="data/seo_80kw_production_management_v2_with_image_prompt_sheet.xlsx")
    p.add_argument("--sheet", default="画像生成プロンプト一覧")
    p.add_argument("--out-dir", default="eyecatches")
    p.add_argument("--results", default="results/eyecatch_generation_results.csv")
    p.add_argument("--start", default=None, help="開始 No（例: 001）")
    p.add_argument("--end", default=None, help="終了 No（例: 080）")
    p.add_argument("--limit", type=int, default=0, help="生成件数の上限（0 で無制限）")
    p.add_argument("--force", action="store_true", help="既存ファイルがあっても上書き生成する")
    p.add_argument("--skip-existing", action="store_true",
                   help="既存ファイルはスキップ（既定動作。明示用）")
    p.add_argument("--model", default="gpt-image-1")
    p.add_argument("--size", default="1536x1024", help="生成サイズ（3:2 推奨。後段で1200x800へ整形）")
    p.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    p.add_argument("--max-retries", type=int, default=2, help="リトライ最大回数")
    p.add_argument("--extra-instructions", default="",
                   help="全Noのプロンプト末尾に追記する自由指示（スタイル微調整用）")
    p.add_argument("--dry-run", action="store_true", help="API を呼ばず対象と保存先だけ表示する")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    start_no = parse_no(args.start) if args.start else None
    end_no = parse_no(args.end) if args.end else None
    limit = None if args.limit <= 0 else args.limit
    skip_existing = not args.force  # 既定はスキップ。--force で上書き

    df = pd.read_excel(args.input, sheet_name=args.sheet, dtype=object)
    cols = df.columns.tolist()
    c_no = find_col(cols, COL_NO)
    c_kw = find_col(cols, COL_KW)
    c_title = find_col(cols, COL_TITLE)
    c_file = find_col(cols, COL_FILENAME)
    c_prompt = find_col(cols, COL_PROMPT)
    if c_no is None or c_prompt is None:
        raise RuntimeError("No 列または 完成プロンプト 列が見つかりません。シート/列名を確認してください。")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = None
    if not args.dry_run:
        from openai import OpenAI  # 遅延 import

        client = OpenAI(api_key=load_api_key())

    print(f"=== アイキャッチ生成 === シート:{args.sheet} / model:{args.model} / size:{args.size}"
          f" -> {TARGET_WIDTH}x{TARGET_HEIGHT}")
    if start_no or end_no:
        print(f"  範囲: {start_no or '先頭'} 〜 {end_no or '末尾'}  / limit: {limit or '無制限'}"
              f"  / {'DRY-RUN' if args.dry_run else ('FORCE上書き' if args.force else '既存はスキップ')}")

    results: list[dict[str, Any]] = []
    processed = 0

    for _, row in df.iterrows():
        no = parse_no(row.get(c_no))
        if no is None:
            continue  # "使い方" などの非数値行を除外
        if start_no is not None and no < start_no:
            continue
        if end_no is not None and no > end_no:
            continue
        if limit is not None and processed >= limit:
            break

        kw = safe_str(row.get(c_kw)) if c_kw else ""
        title = safe_str(row.get(c_title)) if c_title else ""
        prompt = safe_str(row.get(c_prompt))

        # 保存ファイル名（列の値があればその basename、無ければ {No3桁}.png）
        file_val = safe_str(row.get(c_file)) if c_file else ""
        fname = Path(file_val).name if file_val else f"{no:03d}.png"
        if not fname.lower().endswith(".png"):
            fname = f"{Path(fname).stem}.png"
        out_path = out_dir / fname

        result: dict[str, Any] = {
            "No": f"{no:03d}",
            "指定KW": kw,
            "保存ファイル名": str(out_path),
            "status": "",
            "width": "",
            "height": "",
            "error": "",
            "generated_at": "",
        }

        if not prompt:
            result["status"] = "error"
            result["error"] = "完成プロンプトが空です。"
            results.append(result)
            print(f"[ERROR] {no:03d} 完成プロンプトが空です。")
            continue

        if skip_existing and out_path.exists():
            result["status"] = "skipped"
            result["error"] = "既存ファイルのためスキップ"
            results.append(result)
            print(f"[SKIP] {no:03d} {out_path} 既存（--force で上書き）")
            continue

        full_prompt = prompt + PROMPT_SUFFIX
        if args.extra_instructions.strip():
            full_prompt += "\n\n# このバッチの追加指示\n" + args.extra_instructions.strip() + "\n"

        if args.dry_run:
            result["status"] = "dry-run"
            results.append(result)
            processed += 1
            print(f"[DRY-RUN] {no:03d} -> {out_path}（{kw} / {title[:30]}）")
            continue

        try:
            raw = generate_one(
                client, full_prompt,
                model=args.model, size=args.size,
                quality=args.quality, max_retries=args.max_retries,
            )
            png_bytes, w, h = to_3_2_png(raw, TARGET_WIDTH, TARGET_HEIGHT)
            out_path.write_bytes(png_bytes)
            result["status"] = "generated"
            result["width"] = w
            result["height"] = h
            result["generated_at"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[OK] {no:03d} -> {out_path} ({w}x{h})")
        except Exception as exc:  # noqa: BLE001 - 失敗しても次の No へ進む
            result["status"] = "error"
            result["error"] = str(exc)
            print(f"[ERROR] {no:03d} {exc}")

        results.append(result)
        processed += 1

    # 結果 CSV
    results_path = Path(args.results)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        results,
        columns=["No", "指定KW", "保存ファイル名", "status", "width", "height", "error", "generated_at"],
    ).to_csv(results_path, index=False, encoding="utf-8-sig")

    summary: dict[str, int] = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    print("=== サマリ ===")
    for status, count in sorted(summary.items()):
        print(f"  {status}: {count}")
    print(f"結果CSV: {results_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
