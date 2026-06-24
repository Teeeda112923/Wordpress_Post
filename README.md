# WordPress 自動投稿 GitHub Actions キット

すでに作成済みの **記事本文（Markdown）** と **アイキャッチ画像** を、制作管理表（Excel）に沿って WordPress へ下書き投稿するためのテンプレートです。
記事執筆・画像生成・SEO構成は対象外（別工程）で、本キットは「投稿の自動化」だけを担当します。

## 重要（セキュリティ）

WordPress のアプリケーションパスワードは、**絶対にリポジトリへ直接書かないでください。**
必ず GitHub Secrets に保存します。チャット等に貼ってしまったパスワードは漏洩扱いとし、WordPress 管理画面で無効化して再発行してください。

## できること

- 制作管理表（XLSX / CSV）を読み込み、列名のブレを吸収して取得
- `articles/` 配下の本文 Markdown を読み込み、HTML へ変換
- `eyecatches/` 配下の画像を WordPress メディアへアップロードし `featured_media` に設定
- カテゴリ・タグが無ければ自動作成
- 投稿ステータスを `draft` / `pending` / `publish` から選択
- `dry-run` で事前確認
- 実行結果 CSV を出力（GitHub Actions では Artifact 保存）
- 1 件失敗しても全体は止めず、失敗内容を CSV に記録
- 同一 slug の既存投稿はスキップして二重投稿を防止

## リポジトリ構成

```text
.
├─ .github/workflows/wp-auto-post.yml
├─ articles/        # 001.md / slug.md など（本文 Markdown）
├─ eyecatches/      # 001.webp / slug.webp など（アイキャッチ）
├─ data/seo_80kw_production_management.xlsx
├─ wp_auto_post.py
├─ requirements.txt
└─ README.md
```

## 1. GitHub Secrets の設定手順

`Settings` → `Secrets and variables` → `Actions` → `New repository secret` で以下を登録します。

| Secret 名 | 内容 | 例 |
|---|---|---|
| `WP_BASE_URL` | WordPress サイト URL（末尾スラッシュ不要） | `https://example.com` |
| `WP_USERNAME` | WordPress ユーザー名 | `editor_user` |
| `WP_APP_PASSWORD` | 再発行したアプリケーションパスワード | `xxxx xxxx xxxx xxxx xxxx xxxx` |

アプリケーションパスワードは WordPress 管理画面の `ユーザー` → `プロフィール` → `アプリケーションパスワード` から発行します（スペースはそのまま貼り付けてOK。スクリプト側で除去します）。

## 2. 制作管理表の列名（自動判定）

完全一致 → 部分一致の順で柔軟に判定します。

| 用途 | 対応列名の例 |
|---|---|
| No | `No`, `番号`, `記事No`, `ID` |
| KW | `指定KW`, `管理KW`, `KW`, `キーワード`, `親KW` |
| タイトル | `記事タイトル案`, `記事タイトル`, `タイトル`, `H1` |
| スラッグ | `スラッグ`, `slug` |
| メタディスクリプション | `メタディスクリプション案`, `メタディスクリプション`, `description` |
| カテゴリ | `WPカテゴリ`, `カテゴリ`, `記事カテゴリ` |
| タグ | `タグ案`, `タグ`, `WPタグ` |
| 画像ファイル名 | `画像ファイル名`, `アイキャッチファイル名` |
| 画像alt | `画像alt`, `アイキャッチalt`, `代替テキスト`, `alt` |

カテゴリ・タグは `、` `,` `/` `|` `改行` で区切って複数指定できます。

## 3. 本文・画像の置き方と探索順

**本文（`articles/`）**

1. `articles/{slug}.md`
2. `articles/{Noを3桁ゼロ埋め}.md`（例 `001.md`）
3. `articles/{No}.md`（例 `1.md`）

本文先頭が `# タイトル` の場合、WordPress の投稿タイトルと二重になるため既定で除去します（`--keep-h1` で無効化）。

**画像（`eyecatches/`）**

1. 管理表の「画像ファイル名」列の値
2. `eyecatches/{slug}.webp / .jpg / .jpeg / .png`
3. `eyecatches/{Noを3桁ゼロ埋め}.webp / .jpg / ...`
4. `eyecatches/{No}.webp / .jpg`

画像が無くても本文があれば投稿します。その場合は結果 CSV の `image_file` に「（画像なし）」と記録されます。

## 4. GitHub Actions での実行

`Actions` → `WordPress Auto Post` → `Run workflow`

| 入力 | 内容 |
|---|---|
| `mode` | `dry-run`（確認のみ）/ `post`（投稿） |
| `limit` | 投稿件数。`0` で全件 |
| `post_status` | `draft` / `pending` / `publish` |
| `input_file` | 制作管理表のパス |
| `sheet_name` | Excel シート名 |

実行後、`results/results_YYYYMMDD_HHMMSS.csv` が Artifact `wp-auto-post-results` として保存されます。

### 初回テスト手順

1. **dry-run で確認**
   `mode=dry-run`, `limit=1`, `post_status=draft`, `sheet_name=制作管理表`
   → 列マッピングと「投稿準備OK」をログ・CSV で確認。
2. **1 件だけ実投稿**
   `mode=post`, `limit=1`, `post_status=draft`
   → WordPress 管理画面で下書き・アイキャッチ・カテゴリ/タグを目視確認。

### 80 記事投稿時の安全な運用手順

1. まず `mode=dry-run`, `limit=0` で全 80 件を確認（本文・画像の有無を CSV でチェック）。
2. `mode=post`, `limit=1`, `post_status=draft` で 1 件投稿し目視確認。
3. 問題なければ `mode=post`, `limit=10`, `draft` で小ロット投稿し確認。
4. 最後に `mode=post`, `limit=0`, `draft` で残り全件。
   - 同一 slug の既存投稿は自動スキップされるため、再実行しても二重投稿になりません。
5. 内容に問題がなければ WordPress 側で個別に公開、または `post_status=publish` を使用。

## 5. ローカル実行（任意）

```bash
pip install -r requirements.txt

export WP_BASE_URL="https://example.com"
export WP_USERNAME="your_user"
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

python wp_auto_post.py \
  --input data/seo_80kw_production_management.xlsx \
  --sheet 制作管理表 \
  --articles-dir articles \
  --images-dir eyecatches \
  --post-status draft \
  --dry-run \
  --limit 1
```

主なオプション: `--limit`（0で全件） / `--dry-run` / `--sleep`（投稿間待機秒） / `--keep-h1` / `--allow-duplicate`（既存slugを上書き更新） / `--output-dir`。

## 6. 結果 CSV の列

`no, kw, title, slug, article_file, image_file, status, post_id, post_link, message`

`status` は `posted` / `dry-run` / `skipped` / `error`。失敗行は `error` と `message`（API のエラー内容）で追跡できます。

## トラブル時の確認ポイント

- **401 / 403**: `WP_USERNAME` / `WP_APP_PASSWORD` の誤り、またはセキュリティプラグインが REST API / Basic 認証を制限。アプリケーションパスワードを再発行し、REST API を許可。
- **rest_no_route / 404**: REST API が無効、もしくは `WP_BASE_URL` が誤り。
- **画像なしと記録される**: ファイル名が slug / No と一致しているか、`画像ファイル名`列の値を確認。
- **タグ・カテゴリが付かない**: 管理表の列名と区切り文字を確認（dry-run ログの「列マッピング結果」で判定結果を確認可能）。
- **二重投稿が心配**: 既定で同一 slug はスキップ。意図的に上書きする場合のみ `--allow-duplicate`。
