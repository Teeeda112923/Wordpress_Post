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
| `nos` | 空 | 投稿するNo。列挙 `32,33,53` と範囲 `2-10,13-15` のどちらでも書けます。**空欄なら未投稿を公開予定日の古い順に拾う** |
| `max_count` | `5` | 1回の実行で投稿する最大件数。**`0` で無制限（対象すべて）** |
| `interval_sec` | `600` | 記事と記事の間隔（秒） |
| `post_status` | `publish` | `publish` / `draft` / `pending` |
| `dry_run` | `true` | WordPressへ変更せず、対象と品質だけ確認する |

- ワークフロー: [`.github/workflows/cybernote-batch-publish.yml`](.github/workflows/cybernote-batch-publish.yml)
- **まず `dry_run: true` で対象を確認してから実行してください。** 既定がdry-runです。
- 通常枠（`CyberNote Security News`）と同じ concurrency group に入るため、
  同時には動かず順番待ちになります。
- 投稿できた分は、途中で失敗しても管理簿へ反映されます。
- `post_status` が `publish` 以外のときは、管理簿を「公開済み」ではなく
  「下書き済み」にします（公開URLの確認も行いません）。
- 次の行は対象から外し、警告として理由つきで一覧表示します。
  - `公開停止` に値がある
  - `生成ステータス` が `生成済み` でない
  - 本文Markdownが見つからない
  - 管理簿にその No の行がない

### 大量にまとめて投稿するとき

`nos` の範囲指定と `max_count: 0` を使うと、件数制限なしでまとめて投稿できます
（旧 `WordPress Auto Post` ワークフローの一括投稿と同じ使い方です）。

```text
nos          : 2-10,13-15
max_count    : 0
interval_sec : 600
dry_run      : true   ← まず確認
```

- 短時間に投稿を集中させるとCORESERVERのImunify360に遮断されるため、
  既定は10分間隔です。件数が多いときほど間隔は詰めないでください。
- ジョブの上限は350分です。**件数 × `interval_sec`** がこれを超えると途中で
  打ち切られます。超える見込みのときは実行開始時に警告が出ます。
  打ち切られても投稿できた分は管理簿に残るので、もう一度実行すれば続きから進みます。
- 例: 10分間隔なら1回の実行で最大35件程度。それ以上は複数回に分けてください。

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
| Variable | `WP_FALLBACK_MEDIA_ID` | アイキャッチが壊れているときに使う既定画像のメディアID（未設定なら `5297`） |

アプリケーションパスワードは**絶対にリポジトリへ書かないでください**。
チャット等に貼ってしまった場合は漏洩扱いとし、WordPress管理画面で無効化して再発行します。

## アイキャッチが壊れているとき

壊れたPNGをWordPressへ送ると、サムネイル生成でサーバー側が500を返し、その記事の投稿枠が失敗します。
そのため投稿処理は、送る前に画像を検査しています（PNG署名・1200×800px・完全デコード）。

検査に通らなかった場合は、**記事を落とさず既定のアイキャッチで公開します**。
サイトのメディアライブラリにある既存画像をIDで指すだけなので、再アップロードは発生しません。

- 既定のメディアID: `5297`
- 差し替えるときはリポジトリ変数 `WP_FALLBACK_MEDIA_ID` を設定します
- 手元から実行する場合は `--fallback-media-id 5297` か環境変数 `WP_FALLBACK_MEDIA_ID`
- どちらも未設定なら、従来どおりその記事はエラーになります（投稿されません）

代替画像を使ったことはログと結果CSVに残ります。気づかないまま既定画像で公開が続かないよう、
`image_status` に `代替画像`、`image_file` に使用したメディアIDを記録します。

```text
[代替] アイキャッチ画像のPNG署名が不正です -> media id=5297 を使用します
```

**代替画像はあくまで公開を止めないための措置です。** 本来のアイキャッチができたら差し替えてください。

### 壊れた画像の検出

`eyecatch_file_check.py` が、画像を追加・変更したコミットで破損を検査します（`Check Eyecatches`）。

意図的に壊れたまま残している画像は `KNOWN_BROKEN` に列挙して検査対象から外しています。
この検査が常に赤いままだと、新しく壊れた画像が混ざっても気づけなくなるためです。
除外した枚数と名前は実行のたびにログへ出します。

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
