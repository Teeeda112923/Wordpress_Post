---
title: "Windowsゼロデイ脆弱性2件を修正、2026年9月更新は過去最多の約970件"
description: "Microsoftは2026年9月の月例更新で過去最多規模の約970件の脆弱性を修正。悪用確認済みのWindowsゼロデイ脆弱性2件の内容と、今すぐできる確認・対策をわかりやすく解説します。"
slug: windows-zero-day-patch-tuesday-2026-09
date: 2026-09-24
main_keyword: "Windows ゼロデイ 脆弱性"
sub_keywords:
  - "ゼロデイ攻撃"
  - "ゼロデイ脆弱性"
  - "ゼロデイ脆弱性とは"
  - "ゼロデイ攻撃 対策"
  - "ゼロデイ攻撃 事例"
  - "Windows Update 2026年9月"
  - "Patch Tuesday 2026年9月"
---

# Windowsゼロデイ脆弱性2件を修正、2026年9月更新は過去最多の約970件

**この記事の要点**

- Microsoftは日本時間2026年9月9日に月例のセキュリティ更新を公開し、過去最多規模となる約970件の脆弱性を修正しました。
- そのうち2件は、修正前から攻撃に悪用されていた「ゼロデイ脆弱性」です（CVE-2026-81963、CVE-2026-85880）。
- IPAとJPCERT/CCも注意喚起を出しており、個人・企業ともにWindows Updateを早めに適用して再起動することが推奨されています。
- 確認方法は「設定」→「Windows Update」→「更新プログラムのチェック」です。

## 2026年9月のWindows Update（Patch Tuesday）の概要

2026年9月の月例更新は、米国時間9月8日（日本時間9月9日）に公開され、修正件数は報道ベースで約970件と過去最多規模です。悪用が確認された脆弱性が2件含まれています。

Microsoftは毎月第2火曜日（米国時間）に「Patch Tuesday（パッチチューズデー）」と呼ばれる定例の更新をまとめて公開しています。今月の対象はWindows 11、Windows Server、Microsoft Office、SharePoint、Exchange、SQL Serverなど幅広い製品です。

修正件数は媒体によって異なります。Tenableは964件、BleepingComputerは966件、SecurityWeekは974件と報じ、Zero Day Initiative（ZDI）はMicrosoftの新規CVE（脆弱性の識別番号）を972件、他社製ソフトやChromium（Edgeの基盤）由来を含めると997件としています。月の途中で先に修正された分や他社由来の分を含めるかどうかで数え方が違うためで、いずれにせよ過去に例のない規模です。BleepingComputerによると、7月は約570件、8月は約400件で、今月はそれを大きく上回りました。

深刻度が最も高い「緊急（Critical）」は100件を超えます（Tenableは104件、BleepingComputerは105件）。

## ゼロデイ脆弱性とは？今回の2件の仕組み

ゼロデイ脆弱性とは、修正プログラムが提供される前から攻撃者に知られ、実際に悪用されている弱点のことです。今回のWindowsゼロデイ脆弱性2件は、いずれも「特権の昇格」と呼ばれる種類です。

「ゼロデイ」は、開発元が修正に使える猶予が0日、という意味から来ています。そうした弱点を突く攻撃がゼロデイ攻撃です。一方、修正が公開された後にまだ更新していない端末を狙う攻撃は「Nデイ攻撃」と呼ばれます。

特権の昇格とは、一般ユーザーの権限しか持たない攻撃者が、パソコンを完全に操作できる最上位の権限（SYSTEM権限）を得てしまう問題です。単独で外部から侵入できる種類ではありませんが、メールの添付ファイルなどで最初の足場を作った攻撃者が、次の段階で使う「仕上げの道具」になりやすいのが特徴です。

| CVE番号 | 対象コンポーネント | 種類 | 内容（要旨） | CVSS |
|---|---|---|---|---|
| CVE-2026-81963 | Windows Update スタック | 特権の昇格 | ファイルのリンクの扱いに不備があり、ログイン済みの攻撃者がSYSTEM権限を得られる | 7.8（重要） |
| CVE-2026-85880 | Windows ALPC（プログラム同士の通信機能） | 特権の昇格 | ヒープバッファオーバーフロー（メモリ領域のあふれ）により、SYSTEM権限を得られる | 7.8（重要） |

CVSSは脆弱性の深刻さを0〜10で表す国際的な指標です。SecurityWeekによると、Windows Update スタックの脆弱性がゼロデイとして扱われるのは過去5年で初めてだといいます。

## 影響とリスク：自分や自社に関係はあるか

サポート中のWindowsを使っている人は、個人・企業を問わず対象と考えるのが安全です。すでに悪用が確認されているため、更新の後回しはリスクになります。

具体的なリスクとしては、ウイルス対策ソフトの停止、情報の窃取、ランサムウェア（データを暗号化して身代金を要求する不正プログラム）の展開などが考えられます。IPAは、悪用された場合にパソコンを制御されるなどの被害が起こり得るとしています。なお、攻撃の具体的な規模や被害組織は公表されていません。

企業のIT管理者は、ゼロデイ以外にも注意が必要です。Windows DNSサーバーの脆弱性CVE-2026-69730（CVSS 9.8）は、認証なしに遠隔から細工したデータを送るだけでコードを実行される恐れがあります。2020年に大きな話題となったDNSの脆弱性「SigRed」の後継ともいわれ、Help Net SecurityやZDIは、ネットワーク経由で自動的に広がる「ワーム」に使われ得る脆弱性が約20件あると指摘しています。現時点で悪用は確認されていませんが、社内でDNSサーバーを運用している場合は優先度を上げて対応すべきでしょう。

## 対策：今すぐできるチェックリスト

最も効果的な対策は、Windows Updateを適用して再起動することです。自動更新が有効でも、再起動が済むまで修正は完了しません。

**個人・一般社員向け（Windows 11）**

- [ ] 「スタート」→「設定」→「Windows Update」を開く
- [ ] 「更新プログラムのチェック」を押し、表示された更新をすべてインストール
- [ ] 「今すぐ再起動する」が表示されたら、作業を保存して再起動
- [ ] 同じ画面の「更新の履歴」で、9月の累積更新プログラムが「正常にインストールされました」となっているか確認
- [ ] Microsoft Officeも更新（Officeアプリの「ファイル」→「アカウント」→「更新オプション」→「今すぐ更新」）

**企業のIT管理者向け**

- [ ] ゼロデイ2件（CVE-2026-81963、CVE-2026-85880）を含む9月の更新を最優先で配布する
- [ ] Windows DNSサーバーを運用している場合は、CVE-2026-69730の修正を優先して適用する
- [ ] 配布状況を管理ツールで確認し、未適用端末を洗い出す
- [ ] サポートが終了したOS（Windows 10は2025年10月にサポート終了。延長セキュリティ更新（ESU）契約がない場合は更新が届きません）の端末を把握し、移行計画を進める

Microsoftの日本のセキュリティチームは、今月のWindows更新が再起動を必要とする「ベースライン更新プログラム」であると案内しています。業務時間外に再起動できるよう、社内への周知も合わせて行いましょう。

## よくある質問

### ゼロデイ攻撃とは何ですか？

修正プログラムがまだない、または公開直後の脆弱性を突く攻撃のことです。開発元が対策するより先に攻撃が始まるため、防ぐのが難しいのが特徴です。

### ゼロデイ攻撃の事例は？

2026年9月に修正されたCVE-2026-81963とCVE-2026-85880が最新の事例です。Microsoftが修正を公開した時点で、すでに攻撃への悪用が確認されていました。

### ゼロデイ攻撃に対する最も効果的な対策は？

修正プログラムが出たらすぐ適用することです。加えて、不審なメールや添付ファイルを開かない、ウイルス対策ソフトを最新に保つ、業務で管理者権限を常用しないといった多層的な対策で、被害を抑えられます。

### ゼロデイ攻撃とNデイ攻撃の違いは？

修正の前か後かの違いです。ゼロデイ攻撃は修正前の弱点を狙い、Nデイ攻撃は修正公開後に未更新の端末を狙います。今回の2件も、更新を放置すればNデイ攻撃の標的になり得ます。

### ゼロデイ攻撃のリスクは？

気づかないうちに侵入や権限の乗っ取りを許すことです。今回のような特権の昇格は、情報漏えいやランサムウェア被害の足がかりになる恐れがあります。

## まとめ

2026年9月のWindows Updateは約970件という過去最多規模の修正で、悪用済みのWindowsゼロデイ脆弱性2件を含みます。個人は「設定」→「Windows Update」で更新と再起動を確認し、企業はゼロデイ2件とDNSサーバーの脆弱性を優先して、早めに適用を進めてください。次回の月例更新は米国時間2026年10月13日（日本時間10月14日）の予定です。

## 参考・出典

- 2026 年 9 月のセキュリティ更新プログラム (月例)｜Microsoft Security Response Center 日本のセキュリティチーム: https://www.microsoft.com/en-us/msrc/blog/2026/09/202609-security-update
- Microsoft 製品の脆弱性対策について(2026年9月)｜IPA: https://www.ipa.go.jp/security/security-alert/2026/0909-ms.html
- 2026年9月マイクロソフトセキュリティ更新プログラムに関する注意喚起｜JPCERT/CC: https://www.jpcert.or.jp/at/2026/at260025.html
- The September 2026 Security Update Review｜Zero Day Initiative: https://www.zerodayinitiative.com/blog/2026/9/8/the-september-2026-security-update-review
- Microsoft's September 2026 Patch Tuesday Addresses 964 CVEs｜Tenable: https://www.tenable.com/blog/microsofts-september-2026-patch-tuesday-addresses-964-cves-cve-2026-81963-cve-2026-85880
- Microsoft September 2026 Patch Tuesday fixes 966 flaws, 2 zero-days｜BleepingComputer: https://www.bleepingcomputer.com/news/microsoft/microsoft-september-2026-patch-tuesday-fixes-966-flaws-2-zero-days/
- September 2026 Patch Tuesday: zero-days, SigRed successor｜Help Net Security: https://www.helpnetsecurity.com/2026/09/09/september-2026-patch-tuesday-zero-days-sigred-successor/
- Microsoft Patches Record 974 Vulnerabilities Including Two Exploited Zero-Days｜SecurityWeek: https://www.securityweek.com/microsoft-patches-record-974-vulnerabilities-including-two-exploited-zero-days/

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "ゼロデイ攻撃とは何ですか？",
      "acceptedAnswer": {"@type": "Answer", "text": "修正プログラムがまだない、または公開直後の脆弱性を突く攻撃のことです。開発元が対策するより先に攻撃が始まるため、防ぐのが難しいのが特徴です。"}
    },
    {
      "@type": "Question",
      "name": "ゼロデイ攻撃の事例は？",
      "acceptedAnswer": {"@type": "Answer", "text": "2026年9月に修正されたCVE-2026-81963とCVE-2026-85880が最新の事例です。Microsoftが修正を公開した時点で、すでに攻撃への悪用が確認されていました。"}
    },
    {
      "@type": "Question",
      "name": "ゼロデイ攻撃に対する最も効果的な対策は？",
      "acceptedAnswer": {"@type": "Answer", "text": "修正プログラムが出たらすぐ適用することです。加えて、不審なメールや添付ファイルを開かない、ウイルス対策ソフトを最新に保つ、業務で管理者権限を常用しないといった多層的な対策で、被害を抑えられます。"}
    },
    {
      "@type": "Question",
      "name": "ゼロデイ攻撃とNデイ攻撃の違いは？",
      "acceptedAnswer": {"@type": "Answer", "text": "修正の前か後かの違いです。ゼロデイ攻撃は修正前の弱点を狙い、Nデイ攻撃は修正公開後に未更新の端末を狙います。"}
    },
    {
      "@type": "Question",
      "name": "ゼロデイ攻撃のリスクは？",
      "acceptedAnswer": {"@type": "Answer", "text": "気づかないうちに侵入や権限の乗っ取りを許すことです。特権の昇格は、情報漏えいやランサムウェア被害の足がかりになる恐れがあります。"}
    }
  ]
}
```