# archive

終了した旧プロジェクトの退避先です。**ここにあるものは実行されません。**

現在このリポジトリで運用しているのは CyberNote のセキュリティニュース記事だけです
（[ルートのREADME](../README.md) を参照）。過去の別案件のファイルがルート直下に混在して
いたため、現役のファイルと区別できるようここへ移しました。削除はしていないので、
必要になれば元の場所へ戻せます。

| ディレクトリ | 中身 |
|---|---|
| `seo-80kw/` | 旧「SEO 80KW記事キット」。記事80件、アイキャッチ20枚、制作管理表、当時のREADME |
| `wordpress-security/` | 「WordPressセキュリティ50記事プロジェクト」一式と制作管理表 |
| `scripts/` | 上記で使っていたアイキャッチ生成スクリプト（`make_eyecatches.py`）。`generate_eyecatches.py` は現行のテストが使うためルートに残しています |
| `workflows/` | 上記のGitHub Actions定義。`.github/workflows/` の外にあるためGitHubは読み込みません |

`workflows/` の中には、一度きりの公開のために作られたもの（`publish-m-trends-2026.yml`、
`publish-ipa-trusted-ai-platform-2026.yml` など）も含みます。役目は終わっています。
