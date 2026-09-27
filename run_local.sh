#!/usr/bin/env bash
#
# ローカル（自分のPC / 日本の通常回線）から WordPress へ投稿するためのヘルパー。
# GitHub Actions を使わず手元から実行することで、CORESERVER の Imunify360
# ボット保護（海外データセンターIPの遮断）を回避します。
#
# 対象は CyberNote セキュリティニュース（projects/cybernote-security-news）です。
#
# 使い方の例:
#   ./run_local.sh                            # 既定: dry-run（投稿せず確認のみ）
#   MODE=dry-run NOS=32,33 ./run_local.sh     # No.32,33 だけ確認
#   MODE=post NOS=32 ./run_local.sh           # No.32 を公開
#   MODE=post NOS=32,33 LIMIT=2 SLEEP=600 ./run_local.sh  # 2件を10分あけて公開
#   MODE=list ./run_local.sh                  # サイト上の管理対象投稿を一覧（読み取りのみ）
#
# 事前準備:
#   1) python3 -m venv .venv && source .venv/bin/activate
#   2) pip install -r requirements.txt
#   3) cp .env.example .env  … .env に WP_BASE_URL / WP_USERNAME / WP_APP_PASSWORD を記入
#
set -euo pipefail
cd "$(dirname "$0")"

# ---- 調整できる項目（環境変数で上書き可能） --------------------------------
MODE="${MODE:-dry-run}"                 # dry-run | post | list | delete | media
STATUS="${STATUS:-publish}"             # draft | pending | publish
WRITE_MODE="${WRITE_MODE:-upsert}"      # create_only | update_only | upsert
NOS="${NOS:-}"                          # 例: 32,33 / 32-40 / 空なら全件
LIMIT="${LIMIT:-1}"                     # 件数上限。0で全件
SLEEP="${SLEEP:-600}"                   # 投稿間隔（秒）。遮断対策
CATEGORY="${CATEGORY:-サイバーセキュリティ}"

INPUT_FILE="${INPUT_FILE:-projects/cybernote-security-news/data/news_ledger.csv}"
ARTICLES_DIR="${ARTICLES_DIR:-projects/cybernote-security-news/articles}"
IMAGES_DIR="${IMAGES_DIR:-projects/cybernote-security-news/eyecatches}"
RESULTS_DIR="${RESULTS_DIR:-projects/cybernote-security-news/results}"
# ---------------------------------------------------------------------------

DRY_RUN_FLAG=""
if [ "$MODE" = "dry-run" ]; then
  DRY_RUN_FLAG="--dry-run"
fi

# 保守モード: サイト上の投稿・メディアを点検／整理する
EXTRA_FLAGS=""
case "$MODE" in
  list)   EXTRA_FLAGS="--list-managed" ;;
  delete) EXTRA_FLAGS="--delete-managed" ;;
  media)  EXTRA_FLAGS="--cleanup-media" ;;
esac

echo "=============================================="
echo " ローカル実行（CyberNote セキュリティニュース）"
echo "   MODE       : $MODE"
echo "   STATUS     : $STATUS"
echo "   WRITE_MODE : $WRITE_MODE"
echo "   NOS        : ${NOS:-(全件)}"
echo "   LIMIT      : $LIMIT"
echo "=============================================="

python wp_auto_post.py \
  --input "$INPUT_FILE" \
  --articles-dir "$ARTICLES_DIR" \
  --images-dir "$IMAGES_DIR" \
  --post-status "$STATUS" \
  --write-mode "$WRITE_MODE" \
  --category "$CATEGORY" \
  --nos "$NOS" \
  --limit "$LIMIT" \
  --sleep "$SLEEP" \
  --output-dir "$RESULTS_DIR" \
  $DRY_RUN_FLAG $EXTRA_FLAGS
