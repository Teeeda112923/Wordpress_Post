# CyberNote アフィリエイト記事 定期実行タスク（Claude用・別枠）

定時のセキュリティニュース（`claude_scheduled_task.md`）とは別枠で、A8.netのアフィリエイトを1か所組み込んだ記事を1日1本、【テーマ選定→調査→執筆→画像→品質検査→GitHub保存→WordPress公開→結果確認】まで無人で完了する。Asia/Tokyo の 16:43 に起動する（2026-11-24 運営者の指示）。

この文書はClaudeの定期実行タスクから毎回読み込まれる。運用を変えるときはこのファイルを直す。記事の中身の書き方は、Claudeのスキル `cybernote-affiliate-article`（以下「スキル」）の「調査」「キーワード」「執筆ルール」「アフィリエイトのルール」「案件ごとの禁止事項」「最終チェック」に従う。スキルのうち、無人実行と合わないところは、この文書の定めが優先する。

## スキルから変えている点（無人実行のため）

- 構成案の承認、記事ごとの公開許可は取らない。代わりに、この文書の品質検査とチェックに全部合格したものだけを公開する。1つでも満たせない場合は公開せず、報告して終了する
- アイキャッチはChatGPTで作らず、`render_eyecatch.py` の `panel` レイアウトでコード描画する（画像生成AIは使わない）
- 構成と字数は、リポジトリの品質チェッカーに合わせる。本文に「よくある質問」「参考情報」「参考・出典」のH2は作らず、フロントマターの `faq`・`sources` に入れる（GEO Kitが出力する）
- 投稿はGitHub Actions（`cybernote-batch-publish.yml`）で行う。WordPress.com MCPで直接投稿しない

## 実行環境の前提

- 無人実行。質問で止まらず、判断した内容を最後の報告に書く。取り返しがつかない操作（既存記事の削除・上書き、既存行の書き換え、結果不明のままの再投稿）は行わない
- 外部サイトの調査は WebSearch / WebFetch で行う。シェルからは外部サイトへ届かない。届かないサイトを別の手段で迂回しない
- GitHubの操作は `git` と `gh api`（REST）で行う
- 依存の導入: `pip install --break-system-packages -r requirements.txt`

## 0. 実行前確認

1. 最新の `main` を取得し、`data/news_ledger.csv`、`data/news_candidates.csv`、`articles/` を確認する
2. 当日（JST）、すでにこの別枠でアフィリエイト記事を公開していれば何もせず終了する（候補CSVの備考に「アフィリエイト別枠」がある行のうち、確認日時が当日のもの）
3. `CyberNote Security News` または `CyberNote Batch Publish` が実行中なら、終わるまで（最大20分）待つ。終わらなければ台帳を触らずに終了し、報告する

## 1. テーマ選定

- 記事の役割は「成約用」（比較・選び方・やり方・処分の手順など、決める直前の読者向け）を基本にする。時事インシデントは、提携案件が直接の備えになる場合に限る
- 推す案件は、スキルの「提携中の案件」の表にあるものに限る。表にない案件のタグを推測で作らない
- 案件ごとに、記事でいちばん警戒すべき被害を直接防げるか、または読者の次の行動に直結するかで選ぶ（スキルの「商品の選び方」）
- 次のいずれかに当たるテーマは選ばない
  - `articles/` のファイル名・タイトル・本文、台帳、候補CSV、WordPress側（公開済み・下書き・予約）に、同じテーマ・同じメインKWの記事がある。WordPress側の検索は WordPress.com MCP（サイトID 226333802）の `posts.list`（`search` にメインKWと主題、`status` に publish・draft・future・pending）と `content.search` で行う。検索できなかった場合は記事化を見送る
  - 直近7日に同じ案件を推した記事が2本以上ある（同じ案件の記事を続けて量産しない）
  - 一次情報（公的機関、当事者・メーカーの公式発表）で主な事実を確認できない
- キーワードはラッコMCPの `suggest-keywords` と `question-search` で集める。クレジット不足やエラーで使えないときは、WebSearchで検索意図を確かめて進め、その旨を報告に書く
- 適当なテーマが見つからなければ、件数合わせをせず「該当テーマなし」で終了する

## 2. 調査

スキルの「調査」に従う。数字・日付・手順・制度は公的機関か当事者の公式発表で確認し、ニュースサイトを一次情報にしない。確定していることと未確定のことを分け、「〇月〇日時点」を明記する。広告主の商品の機能・保証などは、公式サイト・ストアの説明で裏を取る。

## 3. 記事

- 保存先: `projects/cybernote-security-news/articles/{slug}.md`。スラッグは英語（ローマ字可）、既存と重複しない
- フロントマター: `title`、`slug`、`date`、`author: "CyberNote編集部"`、`description`（メタディスクリプション）、`answer`（150〜200字、「。」で終える）、`cve: ""`、`faq`（3〜5問、回答60〜140字）、`sources`（一次情報を含む）
- 本文: 冒頭リード250〜300字 → 参照ブログカード1個（一次情報のページ。既存の解説記事 `tebanasu-mae-security.md` などと同じ書き方）→ H2群 → 最後に `## まとめ`（250〜300字）を1つ
- 本文は5,000〜7,000字を目安にし、下限は品質チェッカーの基準（脆弱性以外の記事は本文1,000字以上）。水増ししない
- H2直下の説明は100字以上。表・箇条書きの直前と直後に各150字以上の説明。見出しの下の本文が300字を超えたらH3で分ける
- 実在するCyberNote内部リンクを重複なしで3本以上。日付入りの正式URLを使う
- 組織の初出に公式サイトのトップページへのリンクを付ける
- アフィリエイトのH3はスキルのルールどおり（推すのは1案件、リンクは最大3か所、メインは判断材料の直後、文字のリンクを基本、無料の範囲と申し込み後に起きることを正確に、向かない人・別の方法も書く、H3本文は300字以内）。広告タグは `<div class="a8-banner">` で囲む。alt属性が空なら商品名を入れる
- スキルの禁止事項（使ったことがない商品の体験談、根拠のない「No.1」、A8のPR文の転載、価格の記載、PR表記の行、案件ごとの禁止訴求）を守る

## 4. アイキャッチ（コード描画）

`eyecatch-src/{slug}.json` に `layout: "panel"` の指定を書き、次で描く。出力PNGを画像として開き、誤字・文字切れ・重なりがないことを目視で確認する。エラーで止まったら文言を短くして描き直す。検査を外さない。

```bash
python render_eyecatch.py projects/cybernote-security-news/eyecatch-src/{slug}.json projects/cybernote-security-news/eyecatches/{slug}.png
python eyecatch_file_check.py projects/cybernote-security-news/eyecatches/{slug}.png
```

会社ロゴ・商品名のロゴ・価格・URLは入れない。数字や日付は記事で一次情報と照合した値だけを入れる。

## 5. 候補CSVと台帳

- 候補CSVの末尾に1行だけ追記する。候補IDは `YYYYMMDD-AFF-{短い英字}`、採用欄は「採用」、備考の先頭に「アフィリエイト別枠」と書き、推した案件名、メインKW、重複確認の結果、一次情報で確認できなかった点を書く
- 台帳の行は、品質検査のために作業ツリー上で末尾に追記する。No.はpush直前の最新 `main` の最大値+1。記事分類=解説、指定KW=メインKW、生成ステータス=生成済み、レビュー判定=未確認、公開停止=空欄、候補ID=上の候補ID
- 台帳の1行目が `No,収集日,…` のヘッダー（先頭のBOMは可）、記事Markdownの1行目が `---` であることを確認する。台帳は末尾への1行追加だけにし、全体を書き直さない

## 6. 品質検査

```bash
python article_quality_check.py --input projects/cybernote-security-news/data/news_ledger.csv \
  --articles-dir projects/cybernote-security-news/articles \
  --results projects/cybernote-security-news/results/article_quality_results.csv \
  --nos {No} --include-unstarted --mode geo --fail-on-error
python geo_article_quality_check.py --input projects/cybernote-security-news/data/news_ledger.csv \
  --articles-dir projects/cybernote-security-news/articles \
  --results projects/cybernote-security-news/results/geo_article_quality_results.csv \
  --nos {No} --include-unstarted --fail-on-error
python -m unittest discover -s projects/cybernote-security-news/tests -p 'test_*.py'
```

エラー0件を必須とする。あわせてスキルの「最終チェック」を1項目ずつ確認し、広告タグが壊れていないこと（`a8mat` の値がスキルのタグと一致すること）をPythonで照合する。合格するまでGitHubへ保存しない。

## 7. GitHub保存

1. 記事、PNG、`{slug}.png.identity.json`、`eyecatch-src/{slug}.json`、候補CSVをコミットして `main` へ push する
2. `git fetch` 後、`origin/main` 上のファイルがローカルと一致することを確認する
3. その後に台帳の行をコミットして push する。push の前に `git pull --rebase origin main` で最新を取り込み、No.が他の行と重なったら直してから push する
4. `main` への push が拒否されたら、別ブランチへ逃がさず原因を報告して終了する

## 8. WordPressへ公開

台帳の push が成功した場合のみ、すぐに一括投稿ワークフローを、その記事のNo.だけを指定して起動する。

```bash
gh api -X POST repos/Teeeda112923/Wordpress_Post/actions/workflows/cybernote-batch-publish.yml/dispatches \
  -f ref=main -f 'inputs[nos]={No}' -f 'inputs[max_count]=1' -f 'inputs[interval_sec]=0' \
  -f 'inputs[post_status]=publish' -f 'inputs[dry_run]=false'
```

- 1分おきに確認し、最大20分待つ。完了後に `git pull` して台帳の該当行が「公開済み」になり、公開URLが入ったことを確認する
- 公開状態を WordPress.com MCP の `posts.get`（status、link、featured_media）で確認する。表示確認ができなかった場合は、その旨を報告する
- 先に `CyberNote Security News` の定時実行がこの行を拾って公開した場合は、二重に投稿せず、その結果を確認して報告する
- 結果が不明なまま投稿を再実行しない。確認できていないものを公開済みと報告しない

## 9. 実行結果報告

次を簡潔に報告する。

- 選んだテーマ・記事の役割・推した案件と理由、見送ったテーマと理由
- 記事番号、タイトル、スラッグ、公開URL
- 本文・リード・まとめ・answerの実測値、品質検査の終了コードとエラー数
- 画像の指定（レイアウト・アイコン）と検査結果
- GitHubのコミット、Actionsの結果、WordPressの公開状態
- 運営者がする作業: A8.netの「広告掲載URL管理」に記事URLを提出すること（提出しないと成果がキャンセルになる可能性がある）

該当テーマなし、品質不合格、未公開などは、工程と具体的な理由を明記する。成功したふりをしない。
