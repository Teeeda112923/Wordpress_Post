---
title: "Ruby脆弱性、正規表現エンジンOnigmoでコード実行の恐れ｜4.0.9・3.4.12・3.3.13へ更新を"
slug: "ruby-onigmo-regexp-rce-gitlab-cves-update"
cve: "CVE-2026-89078, CVE-2026-93577, CVE-2026-97229, CVE-2026-110264"
date: "2026-10-23"
author: "CyberNote編集部"
description: "Rubyの正規表現エンジンOnigmoに、GitLabが見つけたメモリ破壊の不具合があり、Ruby 4.0.9・3.4.12・3.3.13で修正されました。影響を受けるアプリの条件、CVE番号、修正版と暫定対策をまとめます。"
rank_math_focus_keyword: "Ruby 脆弱性"
answer: "外部入力から正規表現を作るRubyアプリが対象です。4.0.9、3.4.12、3.3.13以降へ更新してください。"
faq:
  - q: "Rubyの正規表現エンジンOnigmoの脆弱性とは何ですか？"
    a: "細工された正規表現をRubyがコンパイルする際に、二重解放や整数オーバーフローでメモリが壊れる不具合です。GitLabではサーバー上のリモートコード実行につながるとして、CVSS 9.9〜10.0の脆弱性として公表されました。"
  - q: "自分のRubyアプリは影響を受けますか？"
    a: "Regexp.new、Regexp.union、Regexp.compileに外部入力を渡す場合や、入力を正規表現リテラルへ埋め込む場合が対象です。開発者が書いた正規表現だけを使うアプリは影響を受けないとされています。"
  - q: "どのバージョンに更新すればよいですか？"
    a: "Ruby 4.0系は4.0.9、3.4系は3.4.12、3.3系は3.3.13以降へ更新してください。3系列の修正版はいずれも、GitLabが採番した4件のCVEに関わる修正をすべて含んでいます。"
  - q: "Regexp.timeoutやパターンの長さ制限で防げますか？"
    a: "防げません。Regexp.timeoutは今回の不具合に効かず、短いパターンで起きるものもあるため長さ制限も確実ではありません。更新が難しい場合は、信頼できない入力から正規表現を作らないことが必要です。"
  - q: "脆弱性スキャナーではどのCVE番号で管理すればよいですか？"
    a: "Ruby側は現時点でCVE番号を申請していません。当面はGitLabが採番したCVE-2026-89078、CVE-2026-93577、CVE-2026-97229、CVE-2026-110264を参照するよう案内されています。"
sources:
  - title: "GitLabのCVE-2026-89078、CVE-2026-93577、CVE-2026-97229、CVE-2026-110264に関連する正規表現コンパイルの修正"
    url: "https://www.ruby-lang.org/ja/news/2026/10/23/regexp-fixes-for-gitlab-cves/"
    publisher: "Ruby"
  - title: "CVE-2026-89078 CVE Record"
    url: "https://www.cve.org/CVERecord?id=CVE-2026-89078"
    publisher: "CVE Program"
  - title: "CVE-2026-93577 CVE Record"
    url: "https://www.cve.org/CVERecord?id=CVE-2026-93577"
    publisher: "CVE Program"
  - title: "CVE-2026-97229 CVE Record"
    url: "https://www.cve.org/CVERecord?id=CVE-2026-97229"
    publisher: "CVE Program"
  - title: "CVE-2026-110264 CVE Record"
    url: "https://www.cve.org/CVERecord?id=CVE-2026-110264"
    publisher: "CVE Program"
  - title: "Ruby 3.3.13 Released"
    url: "https://www.ruby-lang.org/en/news/2026/10/23/ruby-3-3-13-released/"
    publisher: "Ruby"
---

# Ruby脆弱性、正規表現エンジンOnigmoでコード実行の恐れ｜4.0.9・3.4.12・3.3.13へ更新を

[Ruby](https://www.ruby-lang.org/ja/)の開発チームは2026年10月23日（協定世界時）、正規表現エンジンOnigmoの不具合を修正したRuby 4.0.9、3.4.12、3.3.13を公開しました。細工された正規表現をコンパイルするとメモリが壊れ、最悪の場合はリモートコード実行に悪用される恐れがあります。

不具合は[GitLab](https://about.gitlab.com/)が自社製品の脆弱性として報告したもので、4件のCVE番号が割り当てられています。本記事では、影響を受けるアプリの条件、系列ごとの修正版と確認方法、すぐに更新できない場合の暫定対策を、順を追ってまとめます。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 参照</p>
<!-- /wp:paragraph -->

<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.ruby-lang.org/ja/news/2026/10/23/regexp-fixes-for-gitlab-cves/"} /--></div>
<!-- /wp:group -->

## Rubyの正規表現エンジンOnigmoに見つかった不具合

修正されたのは、Rubyが標準で使う正規表現エンジンOnigmoの、パターンを解析・コンパイルする処理の不具合です。GitLabはこれがサーバー上のコード実行につながると判断し、自社の脆弱性として公表しました。

GitLabは利用者の正規表現をコンパイルしており、[9月の修正](https://www.cybernote.click/2026/09/24/gitlab-cve-2026-93577-89078-rce-update/)以降、同梱するRubyを修正してきました。[CVE-2026-97229](https://www.cybernote.click/2026/10/13/gitlab-cve-2026-97229-ci-cd-regex-rce-update/)と[CVE-2026-110264](https://www.cybernote.click/2026/10/22/gitlab-cve-2026-110264-regex-rce-all-versions/)はCVSS 10.0です。

## 影響を受けるアプリの条件と暫定対策

影響は、外部から受け取った文字列を正規表現としてコンパイルするアプリに限られます。Rubyを使っていても、開発者自身が書いた正規表現だけを使うアプリは影響を受けないと、Ruby開発チームは説明しています。

Regexp.new、Regexp.union、Regexp.compileに利用者の入力を渡す場合や、正規表現リテラルへ埋め込む場合です。

Regexp.timeoutや長さ制限は確実な対策にならないため、更新までは正規表現を入力させる機能の停止を検討しましょう。

## 系列ごとの修正版と確認方法

Ruby開発チームは、4.0系、3.4系、3.3系の各系列の修正版へ更新するよう推奨しています。3系列の修正版は、いずれもGitLabが採番した4件のCVEの原因となった不具合の修正を、すべて含んでいます。

CVEごとに、修正が最初に入った版は系列によって異なります。たとえばCVE-2026-89078の修正は、4.0系では4.0.0から含まれていますが、3.4系と3.3系では今回の版が初めてです。稼働中のバージョンはruby -vで確認でき、次の表と照らし合わせると、どの修正が未適用なのかを判断できます。

| CVE | 原因 | 4.0系 | 3.4系 | 3.3系 |
|---|---|---|---|---|
| CVE-2026-89078 | 二重解放 | 4.0.0 | 3.4.12 | 3.3.13 |
| CVE-2026-93577／97229 | 整数オーバーフロー | 4.0.8 | 3.4.12 | 3.3.13 |
| CVE-2026-110264 | 内部IDのあふれ | 4.0.9 | 3.4.12 | 3.3.13 |

セキュリティ保守期間中の3.3系にも、今回は例外として修正が取り込まれました。OSのパッケージやコンテナイメージで導入したRubyは、提供元が修正版を配布しているかもあわせて確認しておきましょう。なお、Ruby側はCVE番号を申請しておらず、当面はGitLabのCVE番号で管理するよう案内しています。

## まとめ

Rubyの正規表現エンジンOnigmoに、細工されたパターンのコンパイル時にメモリが壊れる不具合が見つかり、Ruby 4.0.9、3.4.12、3.3.13で修正されました。GitLabではリモートコード実行につながる脆弱性として、4件のCVEが割り当てられています。

影響を受けるのは、外部入力から正規表現を作るアプリです。確認した情報には既知の悪用を示す記載はありませんが、該当する機能を持つ場合は各系列の修正版へ早めに更新し、更新までは信頼できない入力から正規表現を作らない運用に切り替えましょう。
