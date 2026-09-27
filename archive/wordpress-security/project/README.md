# WordPressセキュリティ 50記事プロジェクト

CyberNote Security Checkerのインストール獲得を目的とする、WordPressセキュリティ記事群です。記事PVだけでなく、検索意図、内部リンク、CTA強度、GEOでの引用しやすさを設計に含めます。

## ディレクトリ

```text
data/wordpress-security-production.xlsx
projects/wordpress-security/
├─ articles/      # 001.md、006.mdなど
├─ eyecatches/    # 001.png、006.pngなど（1200×800px）
└─ results/       # 品質検査・画像生成・投稿結果CSV
```

制作管理表には次のシートがあります。

- `制作管理表`
- `画像生成共通プロンプト`
- `画像生成プロンプト一覧`
- `KWデータ`
- `執筆・QAルール`
- `進捗サマリー`

## 第1バッチ

設計書の優先順に、以下の5記事から制作します。

1. `006.md` WordPressのセキュリティチェック方法
2. `023.md` CyberNote Security Checkerの使い方
3. `015.md` セキュリティプラグインの複数導入
4. `012.md` 無料セキュリティプラグイン8選
5. `024.md` WordPressの脆弱性とは

## 記事品質検査

文字数は制作管理表の設計値に対して原則±3％で判定します。CTA部分は次のマーカーで囲むと、本文コア文字数と分離して集計できます。

```markdown
<!-- CTA_START -->
CTA本文
<!-- CTA_END -->
```

実行例:

```bash
python article_quality_check.py \
  --input data/wordpress-security-production.xlsx \
  --sheet 制作管理表 \
  --articles-dir projects/wordpress-security/articles \
  --results projects/wordpress-security/results/article_quality_results.csv \
  --nos "6,12,15,23,24" \
  --tolerance 0.03 \
  --fail-on-error
```

## アイキャッチ生成

`画像生成プロンプト一覧`の`完成プロンプト`を使います。共通デザインはダークネイビー基調、Noto Sans JP想定、1200×800pxのPNGです。

GitHub Actionsの`WordPress Security Eyecatches`を実行します。最初は次の設定で対象だけ確認してください。

- `start`: `006`
- `end`: `024`
- `limit`: `1`
- `dry_run`: `true`
- `commit`: `false`

実生成にはGitHub Secretsの`OPENAI_API_KEY`が必要です。

## WordPress下書き投稿

GitHub Actionsの`WordPress Auto Post`で次の値を指定します。

```text
input_file: data/wordpress-security-production.xlsx
sheet_name: 制作管理表
articles_dir: projects/wordpress-security/articles
images_dir: projects/wordpress-security/eyecatches
results_dir: projects/wordpress-security/results
quality_gate: true
quality_tolerance: 0.03
post_status: draft
```

初回は`mode=dry-run`、`limit=1`で確認し、その後も下書きへ小ロットで投稿します。
