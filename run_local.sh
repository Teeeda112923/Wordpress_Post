#!/usr/bin/env bash
#
# ローカル（自分のPC / 固定IP環境）から WordPress へ投稿するためのヘルパー。
# GitHub Actions を使わず、日本の通常回線から実行することで
# CORESERVER の Imunify360 ボット保護（海外データセンターIPの遮断）を回避します。
#
# 使い方の例:
#   ./run_local.sh                       # 既定: dry-run（投稿せず確認のみ）で全件
#   MODE=dry-run NOS=1,2 ./run_local.sh  # No.1,2 だけ確認
#   MODE=post STATUS=draft NOS=3 ./run_local.sh          # No.3 を下書き投稿
#   MODE=post STATUS=publish WRITE_MODE=upsert ./run_local.sh   # 全件を公開（更新も許可）
#
# 事前準備:
#   1) python3 -m venv .venv && source .venv/bin/activate
#   2) pip install -r requirements.txt
#   3) cp .env.example .env  … .env に WP_BASE_URL / WP_USERNAME / WP_APP_PASSWORD を記入
#
set -euo pipefail
cd "$(dirname "$0")"

# ---- 調整できる項目（環境変数で上書き可能） --------------------------------
MODE="${MODE:-dry-run}"                 # dry-run | post
STATUS="${STATUS:-draft}"               # draft | pending | publish
WRITE_MODE="${WRITE_MODE:-create_only}" # create_only | update_only | upsert
NOS="${NOS:-}"                          # 例: 1,2 / 3-10 / 空なら全件
LIMIT="${LIMIT:-0}"                     # 件数上限。0で全件
CATEGORY="${CATEGORY:-}"                # 空ならExcelのWPカテゴリ列を使用

INPUT_FILE="${INPUT_FILE:-data/wordpress-security-production.xlsx}"
SHEET_NAME="${SHEET_NAME:-制作管理表}"
ARTICLES_DIR="${ARTICLES_DIR:-projects/wordpress-security/articles}"
IMAGES_DIR="${IMAGES_DIR:-projects/wordpress-security/eyecatches}"
RESULTS_DIR="${RESULTS_DIR:-projects/wordpress-security/results}"
# ---------------------------------------------------------------------------

DRY_RUN_FLAG=""
if [ "$MODE" = "dry-run" ]; then
  DRY_RUN_FLAG="--dry-run"
fi

echo "=============================================="
echo " ローカル実行"
echo "   MODE       : $MODE"
echo "   STATUS     : $STATUS"
echo "   WRITE_MODE : $WRITE_MODE"
echo "   NOS        : ${NOS:-(全件)}"
echo "   LIMIT      : $LIMIT"
echo "=============================================="

python wp_auto_post.py \
  --input "$INPUT_FILE" \
  --sheet "$SHEET_NAME" \
  --articles-dir "$ARTICLES_DIR" \
  --images-dir "$IMAGES_DIR" \
  --post-status "$STATUS" \
  --write-mode "$WRITE_MODE" \
  --category "$CATEGORY" \
  --nos "$NOS" \
  --limit "$LIMIT" \
  --output-dir "$RESULTS_DIR" \
  $DRY_RUN_FLAG
