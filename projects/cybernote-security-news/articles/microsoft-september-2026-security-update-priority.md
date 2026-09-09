---
answer: "Microsoftの2026年9月更新では、実悪用2件を最優先で適用状況まで確認します。"
cve: "CVE-2026-85880, CVE-2026-81963, CVE-2026-72982"
faq:
  - q: "Microsoftの2026年9月更新で最初に確認する脆弱性は何ですか？"
    a: "実悪用が確認されたCVE-2026-85880とCVE-2026-81963を優先し、認証不要RCEのCVE-2026-72982も並行して確認します。"
  - q: "CVSS 7.8の脆弱性をCVSS 9.8より優先する理由は何ですか？"
    a: "CVSSは技術的な深刻度であり、実悪用の有無とは別の尺度です。攻撃で使われている2件は、数値だけで優先度を下げない判断が必要です。"
  - q: "Microsoftの9月更新は配布しただけで完了ですか？"
    a: "いいえ。更新の配布結果に加え、失敗端末、再起動待ち、オフライン端末を確認し、対象OSごとの修正後ビルドへ到達したことを照合します。"
sources:
  - title: "September 2026 Security Updates"
    url: "https://msrc.microsoft.com/update-guide/releaseNote/2026-Sep"
    publisher: "Microsoft Security Response Center"
  - title: "CISA Adds Four Known Exploited Vulnerabilities to Catalog"
    url: "https://www.cisa.gov/news-events/alerts/2026/09/08/cisa-adds-four-known-exploited-vulnerabilities-catalog"
    publisher: "CISA"
  - title: "September 8, 2026—KB5124008"
    url: "https://support.microsoft.com/en-us/servicing/os/windows-11/2026/09/kb5124008-windows-11-24h2-25h2-security-update"
    publisher: "Microsoft Support"
  - title: "September 8, 2026—KB5122878"
    url: "https://support.microsoft.com/en-us/servicing/os/windows-10/2026/09/kb5122878-windows-10-21h2-22h2-security-update"
    publisher: "Microsoft Support"
  - title: "September 8, 2026—KB5122882"
    url: "https://support.microsoft.com/en-us/servicing/os/windows-server/2026/09/kb5122882-windows-server-2022-security-update"
    publisher: "Microsoft Support"
---

# 【緊急】Microsoft 9月更新、実悪用2件を優先適用

Microsoftは2026年9月8日、Windowsなどを対象とする9月のセキュリティ更新を公開しました。Windows ALPCのCVE-2026-85880とWindows Update StackのCVE-2026-81963は、Microsoft CNAのCVSSがともに7.8ですが、CISAが実悪用を確認してKEVへ登録しています。さらにWindows Netlogonには、認証不要でコード実行につながるCVSS 9.8のCVE-2026-72982があります。組織はCVSSの大小だけで並べず、実悪用の有無、外部からの到達性、対象OS、再起動の要否を踏まえて9月更新を展開してください。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 参照</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/08/14/windows-dns-server-cve-2026-62878-rce/"} /--></div>
<!-- /wp:group -->

## Windowsの複数系列へ9月累積更新が公開

9月8日付の更新は、Windows 10、Windows 11、Windows Serverのサポート対象系列へ提供されています。Microsoftの各KBにはセキュリティ修正と品質改善がまとめられており、利用中のOSに対応するパッケージを選ぶ必要があります。

Windows 11 24H2と25H2はKB5124008で、ビルド26100.9445と26200.9445になります。Windows 10 21H2と22H2はKB5122878、Windows Server 2022はKB5122882です。OSの系列に対応するパッケージを選びます。

## 実悪用2件と認証不要RCEを分けて優先する

最優先はCISAが実悪用を確認した2件です。CVE-2026-85880はWindows 10とWindows Server 2012から2022、CVE-2026-81963はWindows 11とWindows Server 2025が中心で、どちらも低権限のローカル攻撃者による権限昇格です。

[Windows ALPCのCVE-2026-85880](https://www.cybernote.click/2026/09/09/windows-alpc-cve-2026-85880-privilege-escalation-exploited/)はメモリー処理、[Windows Update StackのCVE-2026-81963](https://www.cybernote.click/2026/09/09/windows-update-stack-cve-2026-81963-privilege-escalation-exploited/)は参照先の制御に関する不備です。CISAは両方を9月8日にKEVへ追加しました。

一方、[Windows NetlogonのCVE-2026-72982](https://www.cybernote.click/2026/09/09/windows-netlogon-cve-2026-72982-rce-update/)はCVSS 9.8で、認証も利用者操作も不要です。実悪用は未確認ですが、到達可能な認証基盤では並行して優先します。

## 配布結果ではなく適用完了を確認する

更新管理では、承認や配布指示を出した時点を完了にしないことが重要です。運用責任者は管理対象からOSビルドを必ず再収集し、配布失敗、再起動待ち、長期オフライン、サポート切れの端末を分類して残件化します。

業務影響の大きいサーバーは段階的に展開しつつ、実悪用2件を先送りしない日程を設定します。Windows 11のホットパッチ対象でも、今回は標準更新として提供されるため再起動を計画してください。

公開PoC、個別の被害組織、情報漏えい、攻撃主体、犯行声明は公式未確認です。実悪用2件の事実を、未確認の被害内容へ広げないことも必要です。

## まとめ

Microsoftの2026年9月セキュリティ更新では、CVE-2026-85880とCVE-2026-81963の実悪用が確認されています。両方ともCVSS 7.8のローカル権限昇格ですが、攻撃で使われているため最優先で適用状況を確認します。加えて、認証不要のネットワーク攻撃として評価されたCVSS 9.8のWindows Netlogon脆弱性CVE-2026-72982も並行して対応してください。Windows 10、Windows 11、Windows Serverで対象と修正後ビルドが異なります。管理者は9月累積更新を配布し、再起動、実ビルド、失敗端末、オフライン端末まで確認して完了とします。
