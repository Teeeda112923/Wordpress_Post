---
title: "【重要】WordPress 7.1.5で20件のセキュリティ修正｜Template Partブロック経由の権限昇格でコード実行の恐れ、各系統の修正版へ更新を"
slug: "wordpress-7-1-5-security-release-template-part"
date: "2026-11-26"
author: "CyberNote編集部"
description: "WordPress 7.1.5が公開され、Template Partブロックの属性を悪用した権限昇格など20件の問題が修正されました。対象の版、4.7系までの修正版、更新と確認の手順、CVE番号やCVSSなど未確認の点を整理します。"
answer: "WordPress本体の7.1.5が2026年11月18日に公開され、ログイン不要の権限昇格がコード実行につながる恐れのあるTemplate Partブロックの問題など、20件が修正されました。7.1.4以前を使う全サイトが対象です。管理者は管理画面で版数を確かめ、7.1.5か各系統の修正版へすぐ更新してください。"
cve: ""
faq:
  - q: "自動更新を有効にしていれば対応は不要ですか？"
    a: "公式告知では、自動バックグラウンド更新に対応したサイトは自動で更新が始まるとされています。ただし設定や環境で止まることもあるため、管理画面の版数が7.1.5以上か必ず確認してください。"
  - q: "古い系統のWordPressを使っている場合はどうなりますか？"
    a: "修正は4.7系までの各系統に提供され、7.0.9や6.9.12などが公開されています。4.6以前は更新の対象外で、公式は最新版だけを積極的にサポートするとしています。"
  - q: "CVE番号やCVSSの値は決まっていますか？"
    a: "WordPress公式の告知にはCVE番号もCVSSも記載がありません。セキュリティ企業のPatchstackは独自に9.6と評価していますが、CVEレコードは確認できていません。"
sources:
  - title: "WordPress 7.1.5 Release"
    url: "https://wordpress.org/news/2026/11/wordpress-7-1-5-release/"
    publisher: "WordPress.org"
  - title: "Version 7.1.5"
    url: "https://wordpress.org/documentation/wordpress-version/version-7-1-5/"
    publisher: "WordPress.org"
  - title: "WordPress Core <= 7.1.4 Unauthenticated Privilege Escalation via Template Part block attributes"
    url: "https://patchstack.com/database/wordpress/wordpress/wordpress/vulnerability/wordpress-core-7-1-4-unauthenticated-privilege-escalation-via-template-part-block-attributes"
    publisher: "Patchstack"
  - title: "WordPress 7.1.5: Template Part flaw can turn an administrator's click into code execution"
    url: "https://radar.cloudflare.com/zero-wire/wordpress-7-1-5-template-part-privilege-escalation"
    publisher: "Cloudflare Radar Zero Wire"
---

# 【重要】WordPress 7.1.5で20件のセキュリティ修正｜Template Partブロック経由の権限昇格でコード実行の恐れ、各系統の修正版へ更新を

WordPress本体のセキュリティリリース7.1.5が、2026年11月18日に公開されました。開発元の[WordPress.org](https://wordpress.org/)は、XSSやSQLインジェクションなど20件の問題を修正したと告知しています。中でも、Template Partブロックの属性を悪用し、ログインなしで権限を奪える問題は、コード実行につながる恐れがあるとされます。公式は、すぐに更新するよう呼びかけています。WordPressでサイトを運営している方は、管理画面で版数を確かめ、7.1.5か使っている系統の修正版へ更新してください。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 参照</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/11/04/wordpress-core-cve-2026-119977-upgrade-race-rce-kev/"} /--></div>
<!-- /wp:group -->

## 脆弱性の概要

7.1.5は、新機能を含まないセキュリティ修正のためのリリースです。WordPress.orgのリリース告知と版の説明ページによると、修正は20項目で、そのうち2項目は攻撃を防ぐための強化策です。告知の筆者はJeremy Felt氏です。

次の表は、WordPress.orgの告知と版の説明ページで確認できた内容を、最も重い問題であるTemplate Partブロックの件を中心にまとめたものです。公式の告知にはCVE番号やCVSSの値が書かれていないため、該当する欄は「未確認」としています。セキュリティ企業による独自の評価は、表の後で別に紹介します。

| 項目 | 内容 |
|---|---|
| CVE | 未確認（公式告知に記載なし） |
| 種類 | Template Partブロックの属性を悪用した、認証不要の権限昇格（コード実行につながる恐れ） |
| 対象製品 | WordPress本体 |
| 影響を受ける版 | 7.1.4以前 |
| 修正版 | 7.1.5、7.0.9、6.9.12、6.8.13、6.7.12ほか4.7.40までの各系統 |
| CVSS | 未確認（公式告知に記載なし） |
| 回避策 | 公式の告知に記載なし |
| 悪用状況 | 公式の告知に記載なし |

問題を報告したのは、研究者のLogan Homolka氏です。WordPress.orgは、この問題を「コード実行につながる恐れのある、認証不要の権限昇格」と説明しています。修正は4.7系までの古い系統にも反映されましたが、公式は、積極的にサポートしているのは最新版だけだとしています。4.6以前の系統には、今回の修正は提供されていません。

## Template Partブロックの問題とは

Template Partは、ヘッダーやフッターなど、サイトの共通部分をまとめるブロックです。WordPress.orgの告知は概要だけのため、セキュリティ企業[Patchstack](https://patchstack.com/)の解説から、攻撃の流れと条件を整理します。

### 攻撃が成立する条件

Patchstackによると、細工したブロックの属性値が検証されないまま、編集画面の通信先の組み立てに使われていました。その結果、編集者が細工されたコンテンツを開くと、編集者のログイン情報を使った通信が、攻撃者の狙う別の宛先へ送られる恐れがあります。攻撃者自身はログイン不要ですが、権限のある利用者が内容を開く操作が必要です。

### コード実行に至る経路

Patchstackは、管理者が開いた場合、管理者自身の権限でプラグインを導入する機能が悪用されうると説明しています。ただし、コード実行に至るという評価はWordPress側の表現で、修正内容から直接読み取れるのは通信先の書き換えまでだとも述べています。7.1.5では、通信先に使う値を検査する処理が加わりました。

### 独自評価と未確認の点

PatchstackはCVSSを9.6とし、悪用される前に対処すべき優先度の高い問題と位置づけています。これは同社による評価で、CVEレコードや公式の評価は確認できていません。実際の悪用やPoCの公開も、確認した一次情報には記載がありません。

## そのほかの主な修正

20項目には、Template Part以外にも、ログインなしで狙われうる問題が含まれます。WordPress.orgの版の説明ページに載る一覧から、影響が大きいと考えられるものを、種類ごとに選んで紹介します。

一覧には、コメントのショートコード属性を使ったログイン不要の保存型XSS、XML-RPCのピンバックを束ねたサービス拒否があります。REST APIの検索で非公開のタクソノミー（分類）の用語が漏れる問題、WP_Meta_QueryやカスタマイザーのプレビューでのSQLインジェクションも修正されました。マルチサイトでは、サイトの管理者がカスタマイザーのメニュープレビューを通じ、ネットワーク全体を管理する特権管理者のアカウントを乗っ取れる問題もあります。投稿者や寄稿者の権限で使えるXSSや、情報漏えいも複数含まれます。

## 更新の手順と確認

公式告知によると、自動バックグラウンド更新に対応したサイトでは、更新が自動で始まります。ただし、サーバーの環境や更新の設定によっては止まる場合もあるため、更新の結果を必ずご自身の目で確認してください。

### 版数の確認と更新

管理画面の「ダッシュボード」→「更新」で、現在の版数を確かめます。7.1系なら7.1.5、ほかの系統ならその系統の修正版以上になっていれば対応済みです。古いままなら、同じ画面から更新します。サーバーでWP-CLIを使える場合は、「wp core version」で版数を確認できます。

### 更新後に見ておきたい点

更新前に侵害されていた可能性を考え、身に覚えのない管理者アカウントや、見覚えのないプラグインがないか確かめてください。マルチサイトでは、特権管理者の一覧も見直します。WordPressとあわせて、[PHPの版数の確認](https://www.cybernote.click/2026/10/22/wordpress-php-version-check-update-guide/)も済ませておくと安心です。

## 国内のサイト運営者への影響

WordPressは、国内の企業サイトや個人ブログで広く使われています。Template Partの問題は、編集者や管理者が細工された内容を開くことが条件のため、複数人で記事を編集するサイトほど注意が必要です。

[Cloudflare](https://www.cloudflare.com/)の脆弱性情報フィードZero Wireも、この問題をブリーフィングとして取り上げています。フィードの見方は[Zero Wireの解説記事](https://www.cybernote.click/2026/11/05/cloudflare-zero-wire/)で紹介しています。過去の[投稿者権限でのコード実行](https://www.cybernote.click/2026/08/27/wordpress-cve-2026-65640-author-rce-update/)のように、本体の脆弱性は修正版の公開後に狙われることもあります。なお、次の大型版である7.2は、12月8日の公開が予定されています。

## まとめ

WordPress 7.1.5は、2026年11月18日に公開されたセキュリティリリースで、20項目の問題を修正しました。中でもTemplate Partブロックの属性を悪用した権限昇格は、ログイン不要で、コード実行につながる恐れがあるとされます。修正は4.7系までの各系統にも提供されています。CVE番号や公式のCVSS、実際の悪用の有無は、確認した情報には記載がありません。サイトを運営している方は、管理画面で版数を確かめて修正版へ更新し、身に覚えのない管理者やプラグインがないかもあわせて確認してください。
