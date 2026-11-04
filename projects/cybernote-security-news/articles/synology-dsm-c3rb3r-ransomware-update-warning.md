---
title: "Synology NASにC3RB3Rランサムウェア攻撃、古いDSMが標的に｜修正済み版へ更新を"
slug: "synology-dsm-c3rb3r-ransomware-update-warning"
date: "2026-11-05"
author: "CyberNote編集部"
description: "Synologyが2026年10月29日、古いDSMを狙うランサムウェア攻撃への注意を呼びかけました。確認できた事実、修正済みのDSMバージョン、今すぐ取る対策を一次情報から整理します。"
answer: "Synologyは2026年10月29日、2024年12月に修正済みの脆弱性を悪用し、古いバージョンのDSMを狙ってデータを暗号化するランサムウェア攻撃を確認したと発表しました。DSMを使うNASの利用者が対象です。悪用された脆弱性の番号は公表されていないため、DSMを最新版に更新し、自動更新を有効にしてください。"
cve: ""
faq:
  - q: "Synology NASのどのバージョンが狙われていますか？"
    a: "Synologyは「2024年12月に修正済みの脆弱性」を突く攻撃と説明しており、古いバージョンのDSMが標的です。具体的な版番号は発表にないため、DSMが最新かどうかを確認してください。"
  - q: "攻撃に使われた脆弱性の番号は分かっていますか？"
    a: "Synologyの発表にCVE番号の記載はなく、確認できていません。関連する勧告としてSynology-SA-24:20が案内されていますが、同じ番号の脆弱性が悪用されたとは断定できません。"
  - q: "DSMを更新できないときの応急対策はありますか？"
    a: "更新までの間は、NASをインターネットに直接公開せず、外部からの接続を止めてください。あわせて、重要なデータのバックアップをNASとは別の場所に保存しておくと、暗号化されても復旧しやすくなります。"
sources:
  - title: "Synology urges users to update DSM following ransomware attacks on outdated DSM versions"
    url: "https://www.synology.com/en-global/company/news/article/C3RB3R"
    publisher: "Synology"
  - title: "Synology-SA-24:20 DSM (PWN2OWN 2024)"
    url: "https://www.synology.com/en-af/security/advisory/Synology_SA_24_20"
    publisher: "Synology"
  - title: "CVE-2024-10441（Synology-SA-24:20に記載）"
    url: "https://www.cve.org/CVERecord?id=CVE-2024-10441"
    publisher: "CVE Program"
---

自宅や会社でSynology（シノロジー）のNASを使っている方は、一度DSMのバージョンを確認してください。Synologyは2026年10月29日、古いバージョンのDSMを狙い、データを暗号化して身代金を要求するランサムウェア攻撃を確認したと発表しました。攻撃者は、すでに修正されている脆弱性を悪用しているとされています。

発表で求められているのは、DSMの更新と自動更新の有効化です。ただし、悪用された脆弱性の番号など、現時点で公表されていない点もあります。本記事では、Synologyの発表で確認できた事実と、更新の確認方法、NASを守る基本の対策を整理します。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 関連記事</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/10/19/ransomware-japan-2026-h1-s2w-npa/"} /--></div>
<!-- /wp:group -->

## Synologyが発表した内容

[Synology](https://www.synology.com/)は、自社のNAS向けOSであるDSMについて、2024年12月に修正された脆弱性を悪用した攻撃を確認したと発表しました。狙われているのは古いバージョンのDSMで、目的はデータの暗号化と身代金の要求です。

### 発表で分かっていること

Synologyは、該当するバージョンを使うすべての利用者に、DSMを直ちに更新するよう強く求めています。自動更新の有効化も勧めています。

一方で、発表には攻撃の経路、悪用された脆弱性のCVE番号、影響を受けるバージョンの記載がありません。国内の被害件数についても、確認した情報には記載がありません。

## 参考になる勧告と修正済みのバージョン

Synologyの発表は、関連する勧告としてSynology-SA-24:20を案内しています。これは2024年11月に公開されたDSMの脆弱性に関する勧告で、含まれるCVE-2024-10441は深刻度Critical、CVSS v3.1の基本値は9.8です。

ただし、今回の攻撃で悪用された脆弱性が、この勧告のものと同じだとは、Synologyの発表から断定できません。そのため、ここでは原因の特定ではなく更新の目安として、勧告に載っている系統ごとの修正済みバージョンを、次の表にまとめます。お使いのNASのDSMが、どの系統に当たるかを確認しながら読み進めてください。

| DSMの系統 | 修正済みのバージョン |
|---|---|
| DSM 7.2.2 | 7.2.2-72806-1以上 |
| DSM 7.2.1 | 7.2.1-69057-6以上 |
| DSM 7.2 | 7.2-64570-4以上 |
| DSM 7.1 | 7.1.1-42962-7以上 |
| DSM 6.2 | 6.2.4-25556-8以上 |

この表はSynology-SA-24:20の記載を整理したものです。勧告には回避策がないと明記されているため、更新が確実な備えになります。自分のNASがどの系統かを管理画面で確認し、表の値より古い場合は早めに更新してください。更新後も、管理画面で新しい版が出ていないかを定期的に確認しておくと安心です。

## 今すぐ取りたい対策

ここでは、今日から取れる対策を、優先したい順に3つへ絞って紹介します。DSMの更新と自動更新の有効化、更新までのあいだの外部接続の停止、そしてNAS以外の場所へのバックアップです。順に確認していきましょう。

NASを狙う手口は[NASを狙うランサムウェア攻撃の解説](https://www.cybernote.click/2026/07/02/nas%e3%82%92%e7%8b%99%e3%81%86%e3%83%a9%e3%83%b3%e3%82%b5%e3%83%a0%e3%82%a6%e3%82%a7%e3%82%a2%e6%94%bb%e6%92%83%e3%81%a8%e3%81%af%ef%bc%9f%e8%a2%ab%e5%ae%b3%e4%ba%8b%e4%be%8b%e3%82%84%e5%af%be/)で、バックアップが止まった影響は[IDCフロンティアの事例](https://www.cybernote.click/2026/10/08/idc-frontier-idcf-cloud-ransomware-2026/)で紹介しています。

## まとめ

Synologyは2026年10月29日、2024年12月に修正された脆弱性を悪用し、古いバージョンのDSMを狙うランサムウェア攻撃を確認したと発表しました。目的はデータの暗号化と身代金の要求で、DSMを使うNASの利用者が対象です。悪用された脆弱性の番号は公表されていません。

今すぐ、DSMのバージョンを確認して最新版へ更新し、自動更新を有効にしてください。更新までの間は外部からの接続を止め、重要なデータはNAS以外にも保存しておきましょう。新しい情報が出たときは、Synologyの発表で確認してください。
