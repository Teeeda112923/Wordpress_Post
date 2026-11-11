---
title: "FortiOSの脆弱性CVE-2026-126253（CVSS 9.3）などAIが発見した欠陥の詳細をFortinetが公開"
slug: "fortinet-fortios-ai-found-vulnerabilities-hardening-release-20261022"
cve: "CVE-2026-126253, CVE-2026-126255, CVE-2026-126261, CVE-2026-126229, CVE-2026-126147, CVE-2026-126148, CVE-2026-126251, CVE-2026-126257"
date: "2026-10-22"
author: "CyberNote編集部"
description: "Fortinetが11月10日、10月の修正版で直した脆弱性のアドバイザリを公開。FortiOSのCVE-2026-126253（CVSS 9.3）のほか、FortiManager・FortiMail・FortiAuthenticatorにもCriticalがあります。対象版と修正版、移行が必要な系列を解説します。"
rank_math_focus_keyword: "FortiOS 脆弱性"
answer: "Fortinetは2026年11月10日、10月に修正版を出した脆弱性の詳細を公開しました。FortiOSのCVE-2026-126253（CVSS 9.3）のほか、FortiManager・FortiMail・FortiAuthenticatorにもCriticalの欠陥があります。悪用は確認されていませんが、FortiGateなどを使う組織は各系列の修正版へ早急に更新してください。"
faq:
  - q: "FortiOSで最も深刻な脆弱性は何ですか？"
    a: "CVE-2026-126253です。OSPFの処理で認証を回避でき、細工したLSAを送り込まれるおそれがあります。FortinetのCVSS v3は9.3で、8.0.2・7.6.8・7.4.13・7.2.14以降で修正されています。"
  - q: "今回の脆弱性は悪用されていますか？"
    a: "2026年11月10日に公開された各アドバイザリでは、悪用は確認されていないとされています。ただし詳細が公開されたことで攻撃側も修正内容を分析しやすくなるため、未更新の機器は早めに更新してください。"
  - q: "FortiManager 7.4系を使っている場合はどうすればよいですか？"
    a: "FGFMの欠陥CVE-2026-126261（CVSS 9.0）は7.4系と7.2系の全版が対象で、系列内に修正版がありません。7.6.8以降など修正済みの系列へ移行し、それまではFGFMのポートに届く範囲を絞ってください。"
sources:
  - title: "FG-IR-26-267: Authentication bypass by primary weakness (FortiOS)"
    url: "https://www.fortiguard.com/psirt/FG-IR-26-267"
    publisher: "Fortinet FortiGuard PSIRT"
  - title: "CVE-2026-126253"
    url: "https://www.cve.org/CVERecord?id=CVE-2026-126253"
    publisher: "CVE Program"
  - title: "FG-IR-26-269: Improper neutralization of special elements in output used by a downstream component in sshd"
    url: "https://www.fortiguard.com/psirt/FG-IR-26-269"
    publisher: "Fortinet FortiGuard PSIRT"
  - title: "FG-IR-26-275: FGFM elevation before registration password is verified"
    url: "https://www.fortiguard.com/psirt/FG-IR-26-275"
    publisher: "Fortinet FortiGuard PSIRT"
  - title: "FG-IR-26-199: Improper limitation of a pathname to a restricted directory (FortiMail)"
    url: "https://www.fortiguard.com/psirt/FG-IR-26-199"
    publisher: "Fortinet FortiGuard PSIRT"
  - title: "FG-IR-26-265: Incorrect authorization (FortiAuthenticator)"
    url: "https://www.fortiguard.com/psirt/FG-IR-26-265"
    publisher: "Fortinet FortiGuard PSIRT"
  - title: "Fortinet Releases Security Hardening Release for Multiple Products"
    url: "https://www.fortinet.com/blog/ciso-collective/fortinet-releases-security-hardening-release-for-multiple-products"
    publisher: "Fortinet"
  - title: "Fortinet security advisory (AV26-059)"
    url: "https://cyber.gc.ca/en/alerts-advisories/cyber-fortinet-security-advisory-av26-059"
    publisher: "カナダサイバーセキュリティセンター"
---
**2026年11月11日更新：PSIRT公開内容を反映**

[Fortinet](https://www.fortinet.com/)は2026年11月10日、10月に修正版を出した脆弱性のアドバイザリを公開しました。
FortiOSでは、OSPFの処理で認証を回避できるCVE-2026-126253がCVSS 9.3と最も深刻です。

FortiManager・FortiAnalyzer、FortiMail、FortiAuthenticatorにもCriticalの欠陥があり、多くは同社がAIを使った社内検査で見つけたものです。
公開内容と移行が必要な系列を整理します。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 関連：FortiOSで実悪用が確認されたCVE-2025-61624</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/10/19/fortinet-fortios-cve-2025-61624-cli-path-traversal-exploited/"} /--></div>
<!-- /wp:group -->

## 脆弱性の概要

FortiGateのOSであるFortiOSで最も深刻なのは、OSPFデーモンの認証回避です。
対象は8.0・7.6・7.4・7.2の4系列すべてで、10月22日に公開された修正版へ更新すれば対処できます。

[FortiGuard PSIRT](https://www.fortiguard.com/psirt)のFG-IR-26-267によると、認証されていない攻撃者が細工したリクエストでLSA（OSPFでルーター同士が交換する経路情報）を流せるおそれがあります。
攻撃には隣接ネットワークからの到達が要りますが、経路を書き換えられると通信の改ざんや停止につながるおそれがあります。

| 項目 | 内容 |
|---|---|
| CVE | CVE-2026-126253（FG-IR-26-267） |
| 種類 | OSPFデーモンの認証回避（CWE-305） |
| 対象製品 | FortiOS（一部のFortiSASEも対象） |
| 影響を受ける版 | 8.0.0〜8.0.1、7.6.0〜7.6.7、7.4.0〜7.4.12、7.2.0〜7.2.13 |
| 修正版 | 8.0.2、7.6.8、7.4.13、7.2.14以降 |
| CVSS | v3 9.3（評価元：Fortinet） |
| 回避策 | アドバイザリに記載なし |
| 悪用状況 | 確認されていない（CISAのKEV掲載は未確認） |

10月の修正版へ更新済みなら追加作業は不要です。
SSHデーモンの欠陥CVE-2026-126255（CVSS 7.4）も同じ修正版で直りました。
対象はGoogle CloudのOS Login連携を有効にした環境だけです。
アドバイザリには、AIモデル「Claude Mythos」を使って発見したと記されています。

## FortiOS以外の製品の重大な脆弱性

同じ日に、FortiManager・FortiMail・FortiAuthenticatorでもCVSS 9以上の脆弱性が公表されました。
とくに、系列内に修正版がなく別系列へ移行が必要な版に注意してください。

FortiManager・FortiAnalyzerのCVE-2026-126261（CVSS 9.0）は、FGFMのポート経由で認証なしにコードを実行されるおそれがあり、7.4系と7.2系は移行が必要です。
FortiMailも認証不要のコード実行CVE-2026-126147（CVSS 9.8）などがあり、7.2系は移行が必要です。
FortiAuthenticatorの認証回避CVE-2026-126251（CVSS 9.1）などは、8.0.4と6.6.11で直りました。
10月の[FortiMailの実悪用](https://www.cybernote.click/2026/10/02/fortinet-fortimail-cve-2026-104286-path-traversal-mitigation/)や[FortiSandbox](https://www.cybernote.click/2026/10/19/fortinet-fortisandbox-cve-2026-107656-gui-authentication-bypass/)の例もあり、全製品の確認が必要です。

## まとめ

Fortinetは11月10日、AIを使った検査で見つかった脆弱性の詳細を公開しました。
FortiOSではCVE-2026-126253（CVSS 9.3）が最も深刻で、管理・メール・認証の製品にもCriticalがあります。

悪用は確認されていませんが、詳細の公開で攻撃側が分析しやすくなるおそれがあります。
FortiOSは修正版へ更新し、FortiManagerの7.4系・7.2系とFortiMailの7.2系は修正済みの系列へ移行してください。
更新までは管理画面やFGFMポートに届く範囲を絞りましょう。
