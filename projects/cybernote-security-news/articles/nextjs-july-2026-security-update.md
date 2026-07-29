# 【重要】Next.jsに9件の脆弱性、今すぐ確認したい3つの対策

Next.jsの2026年7月セキュリティ更新が公開され、High 4件とMedium 5件の脆弱性が修正されました。影響は利用機能や構成で異なりますが、Server Actionsや外部向けrewriteを使うサイトは優先して確認が必要です。修正版と対応ポイントを簡潔に解説します。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 参照</p>
<!-- /wp:paragraph -->

<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://nextjs.org/blog/july-2026-security-release"} /--></div>
<!-- /wp:group -->

## Next.jsの7月セキュリティ更新とは

### High 4件を含む9件を修正

Vercelは2026年7月20日、Next.jsのセキュリティ更新を公開しました。DoSやSSRFなど、High 4件とMedium 5件が対象です。

### 修正版は2系統

修正版はActive LTSの16.2.11とMaintenance LTSの15.5.21です。古い系列はサポート状況を確認し、保守対象の版へ移行します。

## 想定される影響

### Server Actionsで処理停止のおそれ

App RouterでServer Actionsを使う構成では、細工された要求でCPU使用率が上がり、後続の処理が止まる可能性があります。

### 構成によってSSRFが発生

外部宛先のホスト名を入力から作るrewriteやredirect、特定のカスタムサーバーでは、意図しない接続先へ通信させられるおそれがあります。影響は構成で異なり、広範な悪用も公表されていません。

## 利用者が確認したい3つの対策

### バージョンと利用機能を確認

package.jsonとロックファイルで版を確認し、Server Actions、rewrite、redirect、カスタムサーバーの利用有無を整理します。

### 修正版へ更新してテスト

15系は15.5.21、16系は16.2.11以降へ更新します。ビルド、認証、画面遷移、外部API連携を検証してから本番へ反映してください。

### 暫定対策とログ確認

更新までの間は外部宛先のホスト名を入力から作らず、HostやX-Forwarded-Hostを信頼できる値に固定します。CPU急増や不審な通信も点検します。

## 参考情報

詳細は[Next.js公式情報](https://nextjs.org/blog/july-2026-security-release)と[JPCERT/CC Weekly Report](https://www.jpcert.or.jp/wr/2026/wr260729.html)で確認できます。過去の別脆弱性は、CyberNoteの[Next.jsに深刻なセキュリティ脆弱性](https://www.cybernote.click/2026/07/02/serious-security-vulnerability-in-next-js/)も参考にしてください。
