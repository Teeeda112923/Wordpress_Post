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
├─ eyecatches/      # 001.png 〜 080.png（アイキャッチ。標準は PNG）
├─ data/seo_80kw_production_management_v2_with_image_prompt_sheet.xlsx
├─ wp_auto_post.py
├─ requirements.txt
└─ README.md
```

> **使用する Excel ファイルについて**
> 管理表は `data/seo_80kw_production_management_v2_with_image_prompt_sheet.xlsx` を使用します
> （旧 `seo_80kw_production_management.xlsx` から差し替え）。このブックには次のシートがあります。
> - **制作管理表**… WordPress 投稿処理が参照するシート（`sheet_name` は引き続き `制作管理表`）
> - **画像生成共通プロンプト** / **画像生成プロンプト一覧**… 画像生成用の管理シート。**投稿処理では参照しません**
>
> 画像生成プロンプト一覧の列: `No` / `指定KW` / `記事タイトル` / `画像ファイル名(PNG)` /
> `メインコピー` / `サブコピー` / `補助コピー` / `小見出し・チェック項目` / `背景・構図` /
> `画像の印象` / `個別プロンプト` / `完成プロンプト`

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

**画像（`eyecatches/`）— 標準は PNG**

アイキャッチ画像は `eyecatches/001.png` 〜 `eyecatches/080.png`（No と対応した 3 桁 PNG）で管理するのが標準です。
推奨サイズは **1200×800px（3:2）**。探索順は次の通り（PNG 優先、互換のため他形式も探します）。

1. 管理表の「画像ファイル名」列の値
2. `eyecatches/{Noを3桁ゼロ埋め}.png`（例 `001.png`）
3. `eyecatches/{slug}.png`
4. 互換: `{No3桁}` / `{No}` / `{slug}` の `.webp` / `.jpg` / `.jpeg`

画像が無くても本文があれば投稿します。その場合は結果 CSV の `image_file` に「（画像なし）」と記録されます。

### 画像チェック（dry-run / 投稿前 / 画像チェック専用）

dry-run・投稿時・`--check-images-only` のいずれでも、各アイキャッチを検査してログに出します。

```text
[OK]   001 eyecatches/001.png exists, PNG, 1200x800, ratio 3:2
[NG]   002 eyecatches/002.png not found
[WARN] 003 eyecatches/003.png ratio is not 3:2 (1000x800)
[WARN] 005 eyecatches/005.webp is not PNG (WEBP, 1200x800)
```

検査内容: ファイルの存在 / PNG 形式か / 画像サイズ取得可否 / 3:2 比率に近いか（推奨 1200×800）/ ファイル名が No と対応しているか。

**画像チェックだけを実行**（WordPress 投稿はしない）:

```bash
python wp_auto_post.py \
  --input data/seo_80kw_production_management_v2_with_image_prompt_sheet.xlsx \
  --sheet 制作管理表 \
  --images-dir eyecatches \
  --limit 5 \
  --check-images-only
```

`--update-excel` を併用すると、制作管理表の次の列へ結果を反映します（投稿系の列は変更しません）。

| 状態 | 画像制作ステータス | エラー内容 |
|---|---|---|
| 存在・PNG・3:2 | `画像確認済み` | （空） |
| 見つからない | `画像未作成` | アイキャッチ画像が見つかりません |
| 比率が3:2でない | `要画像確認` | アイキャッチ画像の比率が3:2ではありません |
| PNG以外 | `要画像確認` | アイキャッチ画像がPNG形式ではありません |

あわせて `最終更新日時` も更新します。

## 4. GitHub Actions での実行

`Actions` → `WordPress Auto Post` → `Run workflow`

| 入力 | 内容 |
|---|---|
| `mode` | `dry-run`（確認のみ）/ `post`（投稿） |
| `limit` | 投稿件数。`0` で全件 |
| `post_status` | `draft` / `pending` / `publish` |
| `write_mode` | `create_only`（新規のみ）/ `update_only`（既存のみ更新）/ `upsert`（既存は更新・無ければ新規） |
| `input_file` | 制作管理表のパス |
| `sheet_name` | Excel シート名 |
| `update_excel` | 投稿結果を制作管理表(Excel)へ書き戻してコミットする（既定 false） |

実行後、`results/results_YYYYMMDD_HHMMSS.csv` が Artifact `wp-auto-post-results` として保存されます。

### 制作管理表(Excel)への結果書き戻し（任意）

既定では結果は **CSV のみ** 出力します。`--update-excel`（ワークフローでは `update_excel=true`）を指定すると、入力 Excel の該当シートに以下の列を **No 一致で追記・更新** します（既存列は上書き、無ければ末尾に追加。他シート・書式は保持）。

| 列 | 内容 | 書き込み方 |
|---|---|---|
| `投稿ステータス` | posted / updated / skipped / error / dry-run | 毎回上書き |
| `WP投稿ID` | WordPress 投稿 ID | 値があるときだけ更新 |
| `WP投稿URL` | 投稿 URL | 値があるときだけ更新 |
| `最終投稿日時` | 新規投稿が成功した日時 | 蓄積（更新実行では消さない） |
| `最終更新日時` | 既存投稿を更新した日時 | 蓄積（新規実行では消さない） |
| `最終実行モード` | 例 `post/upsert` `dry-run/update_only` | 毎回上書き |
| `エラー内容` | エラー/スキップ理由（成功時は空にクリア） | 毎回上書き |
| `文字数実績` | 本文の文字数（タグ・空白除外） | 値があるときだけ更新 |
| `文字数判定` | `文字数目安` と比較し `OK` / `不足(...)` / `超過(...)` | 値があるときだけ更新 |

`最終投稿日時` と `最終更新日時` は分かれており、空値で既存セルを上書きしません（過去の投稿日時を保持したまま更新日時だけ追記）。

ワークフローで `update_excel=true` のときは更新後の Excel をブランチへ自動コミットします（`contents: write` 権限を使用）。CSV 運用のみなら付ける必要はありません。

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

## アイキャッチ画像の自動生成（make_eyecatches.py）

背景画像（`eyecatches_base/`）に制作管理表の **「画像内テキスト」** を重ねて、`eyecatches/` に WebP を生成します。

**背景画像の置き方（`eyecatches_base/`）と選択順**

1. `{アイキャッチ型}.webp`（例 `雨漏り系.webp` `屋根修理系.webp` `外壁塗装系.webp` `防水系.webp` `付帯部系.webp`）
2. `{slug}.webp`（記事ごとに個別背景を使う場合）
3. `default.webp`（全記事共通の背景）
4. いずれも無ければ単色背景（`--bg-color`）で生成

**出力ファイル名**：管理表「画像ファイル名」列 → `{slug}.webp` → `{Noを3桁ゼロ埋め}.webp` の順で決定。
**テキスト**：「画像内テキスト」を改行（実改行・`\n`）で分割し、1行目を大きめのタイトル、2行目以降をサブとして中央配置（縁取り＋下部暗幕で可読性確保）。

ローカル実行例:

```bash
pip install -r requirements.txt
# 日本語フォントが必要（例: Ubuntu）
sudo apt-get install -y fonts-noto-cjk fonts-ipafont-gothic

python make_eyecatches.py \
  --input data/seo_80kw_production_management_v2_with_image_prompt_sheet.xlsx \
  --sheet 制作管理表 \
  --base-dir eyecatches_base \
  --out-dir eyecatches \
  --limit 1
```

主なオプション: `--limit`(0で全件) / `--overwrite` / `--dry-run` / `--font`（未指定なら自動探索） / `--width`/`--height`(既定1200x630) / `--text-color` / `--stroke-color` / `--bg-color` / `--overlay-opacity` / `--quality`。

GitHub Actions では `Actions → Build Eyecatches → Run workflow`。`commit=true` で生成画像をブランチへコミット、`false` なら Artifact `eyecatches` として取得できます。フォント（fonts-noto-cjk）はワークフローが自動インストールします。

> 推奨フロー: まず `Build Eyecatches` で画像を用意 → その後 `WordPress Auto Post` で投稿。

## アイキャッチを OpenAI で生成（generate_eyecatches.py）

制作管理表ブックの **「画像生成プロンプト一覧」** シートの `完成プロンプト` を使い、OpenAI の画像生成 API（`gpt-image-1`）で `eyecatches/001.png` 〜 `080.png` を **1 件ずつ** 生成します。生成画像は **1200×800px（3:2）の PNG** に整えて保存します。

### 準備

1. 依存をインストール: `pip install -r requirements.txt`
2. プロジェクト直下に `.env` を作成し、API キーを記載（**コミット禁止**。`.gitignore` 済み）:

   ```text
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
   ```

   雛形は `.env.example` を参照。`gpt-image-1` は OpenAI 側で組織の本人確認が必要な場合があります。

### 使い方

```bash
# まず 001〜005 でテスト
python generate_eyecatches.py --start 001 --end 005

# 既存はスキップしつつ全件
python generate_eyecatches.py --start 001 --end 080 --skip-existing

# 既存を上書き再生成
python generate_eyecatches.py --start 001 --end 010 --force

# API を呼ばず対象と保存先だけ確認
python generate_eyecatches.py --start 001 --end 005 --dry-run
```

主なオプション: `--start` / `--end`（No 範囲）/ `--limit N`（件数上限）/ `--force`（上書き）/
`--skip-existing`（既定。明示用）/ `--quality low|medium|high|auto`（既定 high）/
`--size`（生成サイズ、既定 `1536x1024` を 1200×800 に整形）/ `--max-retries`（既定 2）。

### 仕様

- **1 件ずつ生成**（`n=1`、まとめ生成しない）。途中で失敗しても次の No へ進み、**最大 2 回リトライ**します。
- API レスポンスの Base64 を **PNG にデコード**して保存し、その後 **3:2 にクロップ→1200×800** へ整形。
- 既存ファイルは既定でスキップ（`--force` で上書き）。
- プロンプト末尾に「1枚のみ / 3:2 / 日本語文字は大きく読みやすく / 小さい文字を入れすぎない」を自動付与し、画像内の日本語崩れを抑えます。
- 結果は `results/eyecatch_generation_results.csv` に出力（列: `No`, `指定KW`, `保存ファイル名`, `status`, `width`, `height`, `error`, `generated_at`）。

> 運用: まず `--start 001 --end 005` でテストし、問題なければ `--start 006 --end 080` に広げます。
> 生成後は `python wp_auto_post.py --check-images-only` で PNG / 3:2 をまとめて検査できます。

## 5. ローカル実行（任意）

```bash
pip install -r requirements.txt

export WP_BASE_URL="https://example.com"
export WP_USERNAME="your_user"
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

python wp_auto_post.py \
  --input data/seo_80kw_production_management_v2_with_image_prompt_sheet.xlsx \
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

`status` は次の通り。失敗行は `error` と `message`（API のエラー内容）で追跡できます。

| status | 意味 |
|---|---|
| `posted` | 新規投稿成功 |
| `updated` | 既存投稿の更新成功 |
| `skipped` | スキップ（既存ありで create_only、既存なしで update_only、本文なし 等） |
| `error` | エラー |
| `dry-run` | dry-run（実投稿せず判定のみ） |

### 既存投稿の更新（write_mode）

記事本文やアイキャッチを修正したあと、既存の下書きを更新できます。slug で既存投稿を判定します。

| write_mode | 既存あり | 既存なし |
|---|---|---|
| `create_only`（既定） | スキップ | 新規作成 |
| `update_only` | 更新 | スキップ |
| `upsert` | 更新 | 新規作成 |

- 更新時、**画像があれば featured_media を差し替え**ます。**画像が無ければ既存のアイキャッチを保持**します（消しません）。
- dry-run でも既存有無を判定し、CSV の `message` に「更新予定 / 新規作成予定 / スキップ予定」を出力します（GitHub Actions では Secrets により dry-run でも判定可能）。
- いきなり全件更新しないよう、まず `limit=1` で試してください。

**更新テスト手順**
1. `mode=dry-run`, `write_mode=update_only`, `limit=1` → CSV で「更新予定」を確認
2. `mode=post`, `write_mode=update_only`, `limit=1`, `post_status=draft` → 既存下書きが更新され、CSV に `updated` が出る

> 旧 `--allow-duplicate` は非推奨です（`--write-mode upsert` として扱われます）。

## トラブル時の確認ポイント

- **401 / 403**: `WP_USERNAME` / `WP_APP_PASSWORD` の誤り、またはセキュリティプラグインが REST API / Basic 認証を制限。アプリケーションパスワードを再発行し、REST API を許可。
- **rest_no_route / 404**: REST API が無効、もしくは `WP_BASE_URL` が誤り。
- **画像なしと記録される**: ファイル名が slug / No と一致しているか、`画像ファイル名`列の値を確認。
- **タグ・カテゴリが付かない**: 管理表の列名と区切り文字を確認（dry-run ログの「列マッピング結果」で判定結果を確認可能）。
- **二重投稿が心配**: 既定で同一 slug はスキップ。意図的に上書きする場合のみ `--allow-duplicate`。
