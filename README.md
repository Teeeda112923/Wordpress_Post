# WordPress 自動投稿 GitHub Actions キット

GitHub Actions から WordPress REST API を使って、制作管理表に沿って記事を下書き投稿するためのテンプレートです。

## 重要

WordPress のアプリケーションパスワードは、GitHub リポジトリに直接書かないでください。  
必ず GitHub Secrets に保存してください。

また、チャットやメッセージに貼ったアプリケーションパスワードは露出済みとして扱い、WordPress 管理画面で一度無効化し、新しいものを再発行してください。

## できること

- 制作管理表（XLSX / CSV）を読み込む
- `articles/` 配下の記事本文を読み込む
- `eyecatches/` 配下のアイキャッチ画像を WordPress メディアにアップロードする
- WordPress にカテゴリ・タグを自動作成する
- アイキャッチ画像を設定する
- 投稿ステータスを `draft` / `pending` / `publish` から選べる
- dry-run で事前確認できる
- 実行結果 CSV を GitHub Actions の Artifacts に保存する

## リポジトリ構成

```text
.
├─ .github/
│  └─ workflows/
│     └─ wp-auto-post.yml
├─ articles/
│  ├─ 001.md
│  ├─ 002.md
│  └─ ...
├─ eyecatches/
│  ├─ 001.webp
│  ├─ 002.webp
│  └─ ...
├─ data/
│  └─ seo_80kw_production_management.xlsx
├─ wp_auto_post.py
├─ requirements.txt
└─ .gitignore
```

## GitHub Secrets に登録する値

GitHub リポジトリで以下を登録します。

`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Secret 名 | 内容 |
|---|---|
| `WP_BASE_URL` | WordPress サイト URL。例：`https://example.com` |
| `WP_USERNAME` | WordPress ユーザー名 |
| `WP_APP_PASSWORD` | 再発行したアプリケーションパスワード |

## 記事本文の置き方

`articles/` に Markdown ファイルを置きます。

推奨は No 形式です。

```text
articles/001.md
articles/002.md
articles/003.md
```

管理表に「スラッグ」列がある場合は、以下のようなスラッグ名でも認識します。

```text
articles/matsuyama-amamori-repair.md
```

探索順は以下です。

1. `articles/{slug}.md`
2. `articles/{Noを3桁ゼロ埋め}.md`
3. `articles/{No}.md`

## アイキャッチ画像の置き方

`eyecatches/` に画像を置きます。

```text
eyecatches/001.webp
eyecatches/002.webp
```

または、

```text
eyecatches/matsuyama-amamori-repair.webp
```

対応拡張子は以下です。

- `.webp`
- `.jpg`
- `.jpeg`
- `.png`

## 制作管理表の列名

以下のような列名に対応しています。完全一致でなくても、候補名を複数見ています。

| 用途 | 対応列名の例 |
|---|---|
| No | `No`, `番号`, `記事No`, `ID` |
| KW | `KW`, `キーワード`, `親KW`, `指定KW`, `管理KW` |
| タイトル | `記事タイトル案`, `タイトル`, `記事タイトル`, `H1` |
| スラッグ | `スラッグ`, `slug`, `Slug` |
| メタディスクリプション | `メタディスクリプション案`, `メタディスクリプション`, `description` |
| カテゴリ | `WPカテゴリ`, `カテゴリ`, `記事カテゴリ` |
| タグ | `タグ`, `WPタグ` |
| 画像alt | `alt`, `画像alt`, `アイキャッチalt` |

## GitHub Actions の手動実行

GitHub のリポジトリ画面で、

`Actions` → `WordPress Auto Post` → `Run workflow`

を選択します。

最初は必ず以下で実行してください。

| 項目 | 推奨値 |
|---|---|
| `mode` | `dry-run` |
| `limit` | `1` |
| `post_status` | `draft` |

問題なければ、次に以下で1件だけ投稿テストします。

| 項目 | 推奨値 |
|---|---|
| `mode` | `post` |
| `limit` | `1` |
| `post_status` | `draft` |

その後、10件、80件と増やしてください。

## 実行時の入力項目

| 入力項目 | 内容 |
|---|---|
| `mode` | `dry-run` または `post` |
| `limit` | 投稿件数。`0` で全件 |
| `post_status` | `draft`, `pending`, `publish` |
| `input_file` | 制作管理表のパス |
| `sheet_name` | Excel のシート名 |

## 注意

- 最初から `publish` は使わず、まずは `draft` を推奨します。
- アプリケーションパスワードは絶対にコミットしないでください。
- 画像や本文が見つからない行はスキップします。
- WordPress の REST API が無効化されている場合は投稿できません。
- Basic 認証やセキュリティプラグインで REST API が制限されている場合、除外設定が必要な場合があります。
