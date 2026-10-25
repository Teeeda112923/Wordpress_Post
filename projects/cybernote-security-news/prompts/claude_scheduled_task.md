# CyberNoteセキュリティニュース 定期実行タスク（Claude用）

CyberNoteのセキュリティニュースを、【候補収集→事実確認→記事・画像生成→品質検査→GitHub保存→WordPress公開→結果確認】まで、1回の実行で完了する。対象は GitHub リポジトリ `Teeeda112923/Wordpress_Post` の既存運用。Asia/Tokyo の 9:00、12:00、15:00、19:00 に起動し、各回最大1記事、同日最大4記事。既存の厳格な候補基準、文章品質、重複防止、公開処理を維持する。

この文書はClaudeの定期実行タスクから毎回読み込まれる。運用を変えるときはこのファイルを直す。

## 実行環境の前提

- 無人実行。質問で止まらず、判断した内容を最後の報告に書く。判断できず取り返しがつかない操作（既存記事の削除、既存行の書き換え、結果不明のままの再投稿）は行わず、報告して終了する。
- リポジトリは書き込み権限で接続し、`main` の最新を取得して作業する。
- 外部サイトの調査は WebSearch / WebFetch で行う。シェル（curl、Pythonのrequests）からは外部サイトへ届かない。届かないサイトを別の手段で迂回しない。
- 承認待ちで止まらないよう、WebFetchで開くURLは WebSearch の検索結果か、取得済みの公式ページ内のリンクから辿ったものに限る。CVEレコードのJSONなどのURLを自分で組み立てて開かない。
- WebFetchが確認待ち・待ち時間切れ・取得不可になったURLは、待たず・再試行せずに飛ばし、別の一次情報（開発元のアドバイザリ、MSRC、CISA、JVN等）で検証する。どの一次情報でもCVSSを確認できないCVEは採用せず、記事でも個別に扱わない（CISAのKEVカタログで掲載を確認できたCVEは除く）。取得できなかったURLは候補CSVの備考と実行結果報告に書く。
- GitHubの操作は `git` と `gh api`（REST）で行う。GraphQL（`gh pr list` など）は使えない。
- 依存の導入: `pip install --break-system-packages -r requirements.txt`
- アイキャッチは画像生成AIを使わず、`render_eyecatch.py` でコード描画する（OpenAI APIキーは不要）。

## 0. 実行前確認

最新の `main`、`projects/cybernote-security-news/data/news_candidates.csv`、`news_ledger.csv`、既存記事・アイキャッチ、当日の生成・公開記事数、記事番号の最大値、`article_quality_check.py`、`geo_article_quality_check.py`、関連GitHub Actionsとその最新実行状態を確認する。

```bash
gh api "repos/Teeeda112923/Wordpress_Post/actions/runs?per_page=10" \
  --jq '.workflow_runs[] | [.name,.event,.status,.conclusion,.created_at] | @tsv'
```

既存のCSV列構成・番号・ステータス・記事仕様を確認し、書き込み競合や重複を避ける。`CyberNote Security News` が実行中なら、終わるまで台帳を触らない。当日の上限4件に達していれば新しい記事は作成しない。

当日の記事数は、CyberNote Security News（自動投稿 cybernote-security-news.yml）で公開された記事だけを数える。他の経路（個別の投稿ワークフロー等）で公開した記事は数えない。

## 1. 候補収集（毎回まず行う）

製品開発元、CISA、NVD、CVEレコード等の一次・公式情報を優先し、直近の新規脆弱性や重要更新を調べる。自動採用は次のすべてを満たすものに限る。

- 記事の主題となるCVEが、次のどちらかに当たる
  - CISAのKEV（既知の悪用された脆弱性カタログ）に掲載されている。この場合はCVSSの値を問わない
  - 公式CVSS基本値が8.0以上である
- KEV掲載はCISAのKEVカタログで、CVSSは一次情報で検証できる
- 日本の個人・企業に広く普及・認知された製品／サービスである
- 一次情報での公表日から14日以内である（14日を過ぎた未処理候補も記事化しない）

CVSS基本値は、CVEを採番したCNA（製品開発元など）の値を優先し、CNAの値がない場合はNVDの値を使う。記事と候補CSVには、採用した値の評価元（CNA名またはNVD）を書く。

Windows、Microsoft 365、Chrome、Android、Apple、WordPress、AWS、Azure、Google Cloud、Cisco、Fortinet、Palo Alto Networks、VMware、Apache、Ivanti、Citrix、SonicWall等を優先する。航空・医療・産業制御等の限定的な専門製品は自動採用しない。ただしJoomla本体と拡張機能、特にYouTube Galleryは普及度だけで除外しない（CVSS8.0以上と公式検証は必要）。複数CVEのまとめでも主題CVEがKEV掲載または8.0以上であること。KEV未掲載でCVSSが未検証または8.0未満のもの、知名度や適用範囲が不足する情報は件数合わせで採用しない。KEV掲載のCVEでも、日本で普及した製品でなければ採用しない。KEV掲載のCVEは、記事にKEVへの掲載日と、確認できたCVSSの値・評価元を書く。

### WordPressプラグインの脆弱性

WordPressプラグインの脆弱性にも、上の自動採用の条件（KEVまたはCVSS 8.0以上、14日以内）をそのまま使う。WPカタログ（wpcatalog.jp）は信頼性に不安があるため、候補の入口にも根拠にも使わない（2026-10-21 運営者の指示）。変わるのは「日本で普及した製品か」の判定だけで、プラグインでは WordPress.org のプラグインページの有効インストール数で判定する。

- 候補は、WordPress.org、Wordfence、Patchstack、CISAのKEV、報道などをWebSearchして探す
- 有効インストール数が10万以上なら、日本で普及した製品とみなす。10万未満でも、悪用の事実（CISAのKEV掲載、または開発元・公的機関・Wordfence/Patchstackの一次情報で実際の悪用を確認）があり、WordPress.orgのページで有効インストール数が1万以上なら採用してよい
- 悪用の事実があっても、KEV未掲載ならCVSS 8.0以上の条件は外さない
- 採用前に、CVSSの値・評価元、影響を受ける版、修正版、悪用の有無、対策を、開発元のアドバイザリ、WordPress.orgのプラグインページと更新履歴、CVEレコード、NVD、CISA、JVN等の一次情報で確認する。確認できなければ採用しない
- 同じプラグインで同日に複数のCVEが出ているときは、記事を1本にまとめ、主題CVEは最もCVSSが高いものにする

## 2. 重複検証と候補CSV

同一CVE・脆弱性・事象を、既存の記事・画像、`news_candidates.csv`、`news_ledger.csv` の全ステータスと突き合わせ、重複収集・二重記事化を禁止する。

突き合わせは、候補CSVと台帳だけで済ませない。採用候補の主題CVE番号とスラッグ・製品名で、`articles/` 配下の全記事（フロントマターの `cve`、本文、ファイル名）を必ず `grep` する。1件でも一致すれば、既存記事の更新扱いとなり新規記事にしない（2026-10-22に、`articles/` を照合せず同一CVEの既存記事No.192を上書きした事故が起きた。投稿ワークフローは同一CVEの既存投稿を見つけると更新するため）。一致した場合は、新しい事実があるときだけ「追記候補」として報告する。新規候補があれば、一次情報URL、公式CVSSと検証元、確認日時、概要、スコア、重複確認キーを既存形式で候補CSVの末尾にのみ追記する。既存候補行を書き換えない。

push の前に `git pull --rebase origin main` で最新を取り込み、競合したら再取得して再照合する。新規候補が0件でも既存の未処理適格候補があれば次工程へ進む。未処理適格候補がなければ記事・画像・ledgerを作らず「該当候補なし」として終了する。

## 3. 執筆対象選定

新規候補と既存未処理候補（公表から14日以内のもの）の中から、次の順で優先度を付け、1件だけ選ぶ。

1. CISAのKEV（既知の悪用された脆弱性カタログ）に掲載されている
2. 開発元・公的機関の一次情報で実際の悪用が確認されている
3. Microsoftの月例更新（Patch Tuesday）の対象である
4. 製品の需要（日本での利用者・導入企業の多さ）が大きい。WordPressプラグインは、WordPress.orgの有効インストール数の多さで比べる
5. 公表が新しい

同順位のときは、一次情報の充実度と既存記事との差分価値で決める。公開済み・下書き済み・生成済みのCVEや同一事象を二重に記事化しない。既存記事と同じCVE・事象で、修正版の追加、悪用の確認、CVSSの改定などの新しい事実が一次情報で確認できた場合は、既存記事は変更せず、実行結果報告に「追記候補」として記事番号・新しい事実・一次情報URLを書く。公式情報が未確認の攻撃・情報漏えい・PoC・悪用・犯行声明を事実として断定しない。

## 4. 記事（SEO・GEO・AIO準拠）

既存の合格記事と品質チェッカーを仕様の正とする。詳細は `prompts/work_news_generation.md` に従う。

- 一般読者にわかる表現、2〜3文ごとの簡潔な段落、確認済みの一次ソース。事実と不明点を区別する
- フロントマター: `answer`（150〜200字。何が起きたか・誰に影響するか・今すぐ取るべき対応を2〜4文で）、`cve`、`faq`（2問以上、各回答60〜140字）、`sources`（一次情報を含む1件以上）
- 本文中に FAQ／よくある質問／参考情報／参考・出典 のH2を作らない
- 本文本体は最低1000字、目標1300〜1600字、上限1800字
- リード250〜300字。最後の `## まとめ` は1つのみで250〜300字
- 序文直後・最初のH2前にCocoon参照ブログカードを1個
- 実在するCyberNote内部リンクを重複なしで3本以上
- 本文で組織（公的機関・企業・団体）を紹介するときは、初出の1回だけ組織名にその組織の公式サイトのトップページへのリンクを付ける（2回目以降はリンクなし。個別ページのURLは出典欄に載せる）
- 脆弱性の記事は、参照ブログカードの直後の最初のH2を `## 脆弱性の概要` とし、概要を表にまとめる（2026-10-19 運営者の指示。No.207が見本）。構成は「H2直下の説明（100〜150字）→表の直前の説明（150字以上）→表→表の直後の説明（150字以上）」。表は `| 項目 | 内容 |` の2列で、CVE、種類、対象製品、影響を受ける版、修正版、CVSS（版と評価元）、回避策、悪用状況を基本とし、一次情報で確認できた項目だけを書く（未確認は「未確認」と書く）。表に入れた版番号・CVSS等を後続の段落で繰り返さず、本文の字数上限に収める。脆弱性以外の記事（事件・統計など）は必須としない
- 表や箇条書きの直前と直後には、それぞれ150字以上の説明文を置く
- 根拠のない加筆、水増し、重複記述を禁止

## 5. アイキャッチ（コード描画）

記事の事実に合う1枚を `render_eyecatch.py` で描く。1200×800px、3:2、RGB PNG、濃紺ベース、Noto Sans JP。

1. 指定を `projects/cybernote-security-news/eyecatch-src/{slug}.json` に書く
2. 描画する

```bash
python render_eyecatch.py \
  projects/cybernote-security-news/eyecatch-src/{slug}.json \
  projects/cybernote-security-news/eyecatches/{slug}.png
```

3. 出力されたPNGを画像として開き、目視で確認する

指定の例:

```json
{
  "layout": "banner",
  "tone": "alert",
  "label": "緊急セキュリティ更新",
  "title": "Windows RDS",
  "cve": "CVE-2026-69525",
  "cvss": "9.8",
  "action": "2026年9月の累積更新を適用",
  "action_accent": "2026年9月",
  "icon": "monitor",
  "badge": "shield"
}
```

| 項目 | 選び方 |
|---|---|
| `layout` | `banner`: 帯ラベル＋CVSSバッジ。製品名が短いとき。`stack`: 色分けした行を縦に並べる。製品名が長いとき、実悪用の状況行（`status`）を入れたいとき。`panel`: 脆弱性以外の事件・ニュース（件数や日付を並べる） |
| `tone` | `alert`: 実悪用あり、またはCVSS 9.0以上。`update`: それ以外の更新 |
| `title` | 製品名。長いときは2行までの配列にする。記事タイトルをそのまま入れない |
| `icon` | `monitor` `browser` `server` `mail` `cloud` `phone` `router` `database` `code` `document` から記事の対象に合うもの |
| `badge` | `warning`: 実悪用・攻撃。`shield`: 更新で防げる。`none` |
| `label` | 10字前後。例: 緊急セキュリティ更新、CISAが実悪用を確認、セキュリティ更新 |
| `action` | 対応方法を短く。`action_accent` に先頭の強調部分を入れる |

守ること:

- CVE番号、CVSS、バージョン、日付は、記事で一次情報と照合した値だけを入れる
- 同じレイアウトとアイコンの組み合わせが直近の記事と続くときは、別の組み合わせを選ぶ
- 会社ロゴ、架空ロゴ、URL、記事番号は入れない
- スクリプトがエラーで止まったとき（文字が枠に収まらない、端にかかる、イラストに重なる）は、文言を短くするかレイアウトを変えて描き直す。検査を外して保存しない
- 目視で、誤字、文字切れ、要素の重なり、記事と無関係な絵がないことを確認する

スクリプトは保存時に、PNG署名、完全デコード、サイズ、RGB、ファイルサイズを検査し、`{slug}.png.identity.json` を書く。追加で次を実行し、破損0件を確認する。

```bash
python eyecatch_file_check.py projects/cybernote-security-news/eyecatches/{slug}.png
```

## 6. 品質チェック

Pythonで本文、リード、まとめ、answer、FAQ、sources、内部リンク、参照カード、見出し・禁止H2・重複、表・箇条書き前後の説明文を実測する。文字数はWordと同じ数え方（空白と改行を除く）で数える。

`article_quality_check.py` と `geo_article_quality_check.py` を、その時点の `--help` とActionsの引数に合わせて実行する。`article_quality_check.py` は台帳の行を参照するため、作業ツリー上で台帳に行を追記してから実行する（コミットの順序は7のとおり）。

```bash
python article_quality_check.py \
  --input projects/cybernote-security-news/data/news_ledger.csv \
  --articles-dir projects/cybernote-security-news/articles \
  --results projects/cybernote-security-news/results/article_quality_results.csv \
  --nos {No} --include-unstarted --mode geo --fail-on-error
python -m unittest discover -s projects/cybernote-security-news/tests -p 'test_*.py'
```

エラー0件を必須とする。字数の警告や不自然な表現は、事実確認に基づいて修正→再計測→再校正→再検査する。合格するまでGitHubへ保存しない。

## 7. GitHub保存と台帳

1. 合格した記事Markdown、PNG、`{slug}.png.identity.json`、`eyecatch-src/{slug}.json` を `main` へコミットして push する
2. `git fetch` 後、`origin/main` 上のファイルがローカルと一致すること（`git diff origin/main -- 対象パス` が空）と、PNGの署名・完全デコード・サイズ・RGBを再確認する
3. その後にのみ、`news_ledger.csv` へ新規行を既存形式で追記して push する。指定KWは主対象製品名のみ、生成ステータス=生成済み、レビュー判定=未確認、公開停止=空欄
4. 台帳・記事Markdownを保存したら、push の前に必ず次を確認する。台帳の1行目が `No,収集日,…` のヘッダー（先頭のBOMは可）で始まり、記事Markdownの1行目が `---` であること。ツールの警告文（例: `Warning: fs was declared with const…`）が先頭に混入したり、台帳の改行コードが変わったりしていたら、取り除いてから保存する（2026-10-25に台帳の先頭へ警告文が混入し、自動選択が止まった）。台帳への追記はファイル末尾への1行追加だけにし、全体を書き直さない

既存のCSV行・記事・画像、AWS障害関連記事、cron、投稿枠、無関係のワークフローは変更しない。`main` への push が拒否されたら、別ブランチへ逃がさずに原因を報告して終了する。

## 8. WordPressへ公開（同じ実行内）

記事・画像の保存と台帳更新が成功した場合のみ、投稿ワークフローを起動する。起動前に、同じslug・タイトルの投稿が既にないこと、同じワークフローが実行中でないことを確認する。

```bash
gh api -X POST \
  repos/Teeeda112923/Wordpress_Post/actions/workflows/cybernote-security-news.yml/dispatches \
  -f ref=main
```

- 実行状況を1分おきに確認し、最大20分待つ。台帳を `公開済み` にして公開URLを記録するのはワークフロー自身なので、完了後に `git pull` して該当行が更新されたことを確認する
- ワークフローは未投稿の行を1件だけ選ぶ。別の未投稿行が先に公開された場合は、その旨を報告する（今回の記事は次の枠で公開される）
- 公開URLを WebFetch で開き、表示されること、タイトル、本文、アイキャッチが意図したものであることを確認する。`https://www.cybernote.click/wp-json/wp/v2/posts?slug={slug}&_embed` でアイキャッチ画像のURLも確認する
- 失敗したら、同じ実行内でActionsログとWordPressの応答を調べ、安全に直せる範囲で修復して再確認する
- 投稿後、ワークフローの `Purge Cloudflare cache` ステップが記事URL・トップ・フィードのCloudflareキャッシュを削除する。ジョブのアノテーションやステップ結果で成否を確認し、`Cloudflareキャッシュ未削除`／`Cloudflareキャッシュ削除失敗` の警告が出ていれば報告する。削除の失敗は公開の失敗ではないため、投稿を再実行しない
- Imunify360の遮断による自動再実行（最大2時間）に入った場合は待たずに「公開処理が継続中」と報告する
- 結果が不明なまま投稿を再実行しない。確認できていないものを公開済みと記録・報告しない

## 9. 実行結果報告

次を簡潔に報告する。

- 候補の新規追加数、選定・除外理由、一次ソースとCVSS検証元（CNAかNVDか）
- 追記候補（該当があれば、既存記事番号・新しい事実・一次情報URL）
- 記事番号、タイトル、スラッグ
- 本文・リード・まとめ等の実測値、品質検査の終了コードとエラー数
- 画像の指定（レイアウト・アイコン）と検査結果
- GitHubのコミット、Actionsの結果、WordPressの公開URLと表示確認結果、Cloudflareキャッシュ削除の成否

収集失敗、候補なし、品質不合格、画像保存失敗、未公開などは、工程と具体的な理由を明記する。成功したふりをしない。
