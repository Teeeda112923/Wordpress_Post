# Pixel通話スクリーニング記事：アップロード用

このフォルダへ **pixel-call-screening-cybernote-package.zip** をそのままアップロードして main ブランチへコミットすると、GitHub Actions の「Publish Pixel Call Screening Column」が自動実行されます。

以下を自動で実施します。

1. ZIP内の実画像3枚をSHA-256で照合し、画像破損と寸法を検証する。
2. 1200×800 PNGのアイキャッチを作り、元画像との一致情報を記録する。
3. スクリーンショット2枚をWordPressへアップロードし、実際の画像URLを記事に挿入する。
4. 修正版Markdownを使ってWordPressへ記事を公開し、公開URLと投稿IDを管理簿に記録する。
5. 実際の画像・記事・管理簿をGitHubへ保存する。

**誤った画像での公開を防止するため、ZIP内画像が元ファイルと一致しない場合は停止し、代替アイキャッチも使いません。** フォームの「Create a new branch」ではなく、mainブランチへ直接コミットしてください。失敗時はActionsログを確認してください。

- ワークフロー: [publish-pixel-call-screening-20261008.yml](../../../.github/workflows/publish-pixel-call-screening-20261008.yml)
- 記事下書き: [pixel-call-screening-scam-call-2026.md](../drafts/pixel-call-screening-scam-call-2026.md)
