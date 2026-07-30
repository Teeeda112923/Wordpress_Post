# 【緊急】VMwareにCVSS 9.8の重大脆弱性、急ぐ3つの対策

VMware vCenterやESXなどに、認証回避やコード実行につながる脆弱性が確認されました。最大深刻度はCVSS 9.8で、回避策はありません。急ぎたい対策を解説します。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 参照</p>
<!-- /wp:paragraph -->

<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://support.broadcom.com/web/ecx/support-content-notification/-/external/content/SecurityAdvisories/0/38017"} /--></div>
<!-- /wp:group -->

## VMwareの重大脆弱性とは

### vCenterの認証回避とコード実行

CVE-2026-59309は、ネットワーク経由でvCenterの認証を回避される問題です。CVE-2026-59310は、Syslogサーバーのディレクトリトラバーサルによりコードを実行されるおそれがあります。いずれもCVSS 9.8です。

### ESXからホストへ及ぶ問題

CVE-2026-47876は、VMXNET3仮想ネットワークアダプターの境界外書き込みです。VM内の管理者がESXホストでコードを実行する可能性があり、CVSSは9.3です。

## 想定される影響

### 仮想化基盤の管理に影響

vCenterは仮想マシンやホストを集中管理するため、不正アクセスが成功すると、仮想化環境へ影響が広がるおそれがあります。ただし、公式情報では既知の悪用は確認されていません。

### 対象は複数のVMware製品

対象にはvCenter、ESX、Workstation、Fusion、Cloud Foundationなどが含まれます。製品ごとに修正版が異なるため、現在のバージョンと公式表を照合します。

## 利用組織が急ぎたい3つの対策

### 対象製品とバージョンを確認

資産管理情報や管理画面から、製品、版、ビルド番号を確認します。vCenterへ接続できる端末や管理ネットワークも整理してください。

### 修正版へ更新

回避策はないため、修正版またはパッチを適用します。vCenter 8.0は8.0 U3k、9.0系は9.0.2.0100、9.1系は9.1.0.0300が修正を含みます。

### 更新までの露出を抑える

適用までは管理画面の接続元を管理端末やVPNに限定し、外部公開を避けます。更新後は管理ログ、不審な認証、設定変更を確認してください。

## 参考情報

対象製品、修正版、注意事項は[Broadcom公式アドバイザリ](https://support.broadcom.com/web/ecx/support-content-notification/-/external/content/SecurityAdvisories/0/38017)で確認できます。基本的な確認手順は、CyberNoteの[脆弱性とは？意味や種類、悪用された場合のリスク](https://www.cybernote.click/2026/07/02/%E8%84%86%E5%BC%B1%E6%80%A7%E3%81%A8%E3%81%AF%EF%BC%9F%E6%84%8F%E5%91%B3%E3%82%84%E7%A8%AE%E9%A1%9E%E3%80%81%E6%82%AA%E7%94%A8%E3%81%95%E3%82%8C%E3%81%9F%E5%A0%B4%E5%90%88%E3%81%AE%E3%83%AA%E3%82%B9/)も参考にしてください。
