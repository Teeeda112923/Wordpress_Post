# CyberNote 記事投稿

[CyberNote](https://www.cybernote.click/) へセキュリティニュース記事を投稿するためのリポジトリです。

このリポジトリでできることは、次の2つだけです。

| # | できること | 実行方法 |
|---|---|---|
| 1 | **ChatGPTで作成した記事を1件公開する**（通常運用） | ChatGPTの自動タスク → GitHub Actions `CyberNote Security News` |
| 2 | **未投稿の記事をまとめて公開する**（取りこぼしの回収） | GitHub Actions `CyberNote Batch Publish` を手動実行 |

記事の執筆と画像生成はChatGPT側（GPT「CyberNote記事生成・公開」）が行います。
このリポジトリは **記事・画像・管理簿の置き場** と **WordPressへの投稿処理** を担当します。

---

## 1. ChatGPTで作成した記事の投稿

通常運用はこの経路だけです。1回の実行で公開するのは1記事です。

```text
ChatGPT（記事Markdown＋アイキャッチPNGを生成）
  └─ GitHubへコミット（articles / eyecatches / news_ledger.csv）
       └─ workflow_dispatch で CyberNote Security News を起動
            ├─ 回帰テスト
            ├─ 投稿対象の選択（当日分。無ければ直近の未投稿をさかのぼる）
            ├─ 品質ゲート（article_quality_check.py --mode geo）
            ├─ WordPressへ公開（wp_auto_post.py）
            └─ 管理簿を「公開済み」へ更新してpush
```

- ワークフロー: [`.github/workflows/cybernote-security-news.yml`](.github/workflows/cybernote-security-news.yml)
- 起動時刻はChatGPT側の自動タスク（09:00 / 12:00 / 15:00 / 19:00 JST）で管理します。
  二重投稿を防ぐため、**GitHub Actions側のcronは設定しません**。
- 品質ゲートに落ちた日、一次情報を確認できない日は投稿しません。
- Imunify360に遮断された場合だけ、時間をおいて自動で再実行します（`ACTIONS_PAT` が必要）。

記事の書き方・満たすべき基準は [`docs/cybernote-article-prompt.md`](docs/cybernote-article-prompt.md) と
[`projects/cybernote-security-news/README.md`](projects/cybernote-security-news/README.md) にあります。

### 手動で1件だけ投稿したいとき

GitHub の `Actions` → `CyberNote Security News` → `Run workflow`。

| 入力 | 意味 |
|---|---|
| `target_date` | 対象日（空欄なら当日）。指定するとさかのぼりはしません |
| `dry_run` | WordPressへ変更せず確認だけ行う |

---

## 2. 記事のまとめ投稿（複数記事の一括公開）

公開予定日を過ぎた記事は当日枠では拾われず、そのまま残ります。
溜まった未投稿をまとめて公開するのがこのワークフローです。

GitHub の `Actions` → `CyberNote Batch Publish` → `Run workflow`。

| 入力 | 既定 | 意味 |
|---|---|---|
| `nos` | 空 | 投稿するNo（例 `32,33,53`）。**空欄なら未投稿を公開予定日の古い順に拾う** |
| `max_count` | `5` | 1回の実行で投稿する最大件数 |
| `interval_sec` | `600` | 記事と記事の間隔（秒） |
| `dry_run` | `true` | WordPressへ変更せず、対象と品質だけ確認する |

- ワークフロー: [`.github/workflows/cybernote-batch-publish.yml`](.github/workflows/cybernote-batch-publish.yml)
- **まず `dry_run: true` で対象を確認してから実行してください。** 既定がdry-runです。
- 短時間に投稿を集中させるとCORESERVERのImunify360に遮断されるため、
  既定で10分間隔・5件までに抑えています。急いで詰め込まないでください。
- 通常枠（`CyberNote Security News`）と同じ concurrency group に入るため、
  同時には動かず順番待ちになります。
- 投稿できた分は、途中で失敗しても管理簿へ反映されます。
- 対象から自動で外れるのは次の行です。
  - `公開停止` に値がある
  - `生成ステータス` が `生成済み` でない
  - 本文Markdownが見つからない

---

## リポジトリ構成

```text
.
├─ .github/workflows/
│   ├─ cybernote-security-news.yml    # ① 1記事ずつ公開（通常運用）
│   ├─ cybernote-batch-publish.yml    # ② まとめ投稿（手動）
│   ├─ check-eyecatches.yml           # 壊れたアイキャッチをコミット時に検出
│   └─ cybernote-seo-recovery-audit.yml  # 毎日07:15 JSTの非破壊SEO監査
│
├─ projects/cybernote-security-news/  # 現役の記事・画像・管理簿
│   ├─ articles/                      # 記事Markdown（<スラッグ>.md）
│   ├─ eyecatches/                    # アイキャッチPNG（1200×800px）
│   ├─ data/news_ledger.csv           # 管理簿（投稿対象・投稿結果）
│   ├─ data/news_candidates.csv       # 記事化候補
│   ├─ prompts/ src/ tests/ results/
│   └─ README.md                      # 記事仕様・運用ルール
│
├─ wp_auto_post.py                    # WordPress投稿本体
├─ geo_meta.py                        # GEO（FAQ・出典）メタの組み立て
├─ article_quality_check.py           # 品質ゲート
├─ geo_article_quality_check.py       # GEO観点の品質ゲート
├─ eyecatch_file_check.py             # 画像の破損検査
├─ generate_eyecatches.py             # アイキャッチ生成・PNG検証（テストからも使用）
├─ run_local.bat / run_local.sh       # 手元のPCから投稿するヘルパー
├─ docs/                              # 記事プロンプト・ローカル実行手順
└─ archive/                           # 終了した旧プロジェクト（実行されません）
```

## 必要な GitHub Secrets / Variables

| 種別 | 名前 | 用途 |
|---|---|---|
| Secret | `WP_BASE_URL` | WordPress サイトURL（末尾スラッシュ不要） |
| Secret | `WP_USERNAME` | WordPress ユーザー名 |
| Secret | `WP_APP_PASSWORD` | アプリケーションパスワード |
| Secret | `WP_EXTRA_HEADERS` | CDN/WAF通過用の追加ヘッダ（必要な場合のみ） |
| Secret | `ACTIONS_PAT` | 遮断後の自動再実行に使うPAT（Actions: Read and write） |
| Variable | `WP_USER_AGENT` | ボット対策に弾かれる場合のUA上書き |
| Variable | `BACKFILL_DAYS` | ①が当日分を拾えないときにさかのぼる日数（既定3） |

アプリケーションパスワードは**絶対にリポジトリへ書かないでください**。
チャット等に貼ってしまった場合は漏洩扱いとし、WordPress管理画面で無効化して再発行します。

## 手元のPCから投稿する

GitHub Actions のランナーは米国データセンターのIPのため、Imunify360に遮断されることがあります。
遮断が続くときは日本の通常回線から直接実行します。

```bat
set MODE=dry-run
set NOS=32,33
run_local.bat
```

詳しい手順は [`docs/ローカル実行手順.md`](docs/ローカル実行手順.md) を参照してください。

## archive/ について

`archive/` には、終了した旧プロジェクトを移動してあります（実行されません）。

- `archive/seo-80kw/` … 旧「SEO 80KW記事キット」の記事・画像・管理表・README
- `archive/wordpress-security/` … 「WordPressセキュリティ50記事プロジェクト」一式
- `archive/scripts/` … 上記で使っていたアイキャッチ生成スクリプト
- `archive/workflows/` … 上記のGitHub Actions定義（`.github/` の外にあるため起動しません）
