---
answer: "2026年9月のWindows更新では悪用確認済みゼロデイ2件が修正され、早期の更新と再起動が必要です。"
cve: "CVE-2026-81963, CVE-2026-85880, CVE-2026-69730"
roundup: true
faq:
  - q: "ゼロデイ攻撃とは何ですか？"
    a: "修正プログラムがまだない、または公開直後の脆弱性を突く攻撃のことです。開発元が対策するより先に攻撃が始まるため、防ぐのが難しいのが特徴です。"
  - q: "ゼロデイ攻撃の事例は？"
    a: "2026年9月に修正されたCVE-2026-81963とCVE-2026-85880が最新の事例です。Microsoftが修正を公開した時点で、すでに攻撃への悪用が確認されていました。"
  - q: "ゼロデイ攻撃に対する最も効果的な対策は？"
    a: "修正プログラムが出たらすぐ適用することです。加えて、不審なメールや添付ファイルを開かない、ウイルス対策ソフトを最新に保つ、業務で管理者権限を常用しないといった多層的な対策で、被害を抑えられます。"
  - q: "ゼロデイ攻撃とNデイ攻撃の違いは？"
    a: "修正の前か後かの違いです。ゼロデイ攻撃は修正前の弱点を狙い、Nデイ攻撃は修正公開後に未更新の端末を狙います。今回の2件も、更新を放置すればNデイ攻撃の標的になり得ます。"
  - q: "ゼロデイ攻撃のリスクは？"
    a: "気づかないうちに侵入や権限の乗っ取りを許すことです。今回のような特権の昇格は、情報漏えいやランサムウェア被害の足がかりになる恐れがあります。"
sources:
  - title: "2026 年 9 月のセキュリティ更新プログラム (月例)｜Microsoft Security Response Center 日本のセキュリティチーム"
    url: "https://www.microsoft.com/en-us/msrc/blog/2026/09/202609-security-update"
    publisher: "Microsoft"
  - title: "Microsoft 製品の脆弱性対策について(2026年9月)｜IPA"
    url: "https://www.ipa.go.jp/security/security-alert/2026/0909-ms.html"
    publisher: "IPA"
  - title: "2026年9月マイクロソフトセキュリティ更新プログラムに関する注意喚起｜JPCERT/CC"
    url: "https://www.jpcert.or.jp/at/2026/at260025.html"
    publisher: "JPCERT/CC"
  - title: "The September 2026 Security Update Review｜Zero Day Initiative"
    url: "https://www.zerodayinitiative.com/blog/2026/9/8/the-september-2026-security-update-review"
    publisher: "The September 2026 Security Update Review"
  - title: "Microsoft's September 2026 Patch Tuesday Addresses 964 CVEs｜Tenable"
    url: "https://www.tenable.com/blog/microsofts-september-2026-patch-tuesday-addresses-964-cves-cve-2026-81963-cve-2026-85880"
    publisher: "Microsoft's September 2026 Patch Tuesday Addresses 964 CVEs"
  - title: "Microsoft September 2026 Patch Tuesday fixes 966 flaws, 2 zero-days｜BleepingComputer"
    url: "https://www.bleepingcomputer.com/news/microsoft/microsoft-september-2026-patch-tuesday-fixes-966-flaws-2-zero-days/"
    publisher: "Microsoft September 2026 Patch Tuesday fixes 966 flaws, 2 zero-days"
  - title: "September 2026 Patch Tuesday: zero-days, SigRed successor｜Help Net Security"
    url: "https://www.helpnetsecurity.com/2026/09/09/september-2026-patch-tuesday-zero-days-sigred-successor/"
    publisher: "September 2026 Patch Tuesday"
  - title: "Microsoft Patches Record 974 Vulnerabilities Including Two Exploited Zero-Days｜SecurityWeek"
    url: "https://www.securityweek.com/microsoft-patches-record-974-vulnerabilities-including-two-exploited-zero-days/"
    publisher: "Microsoft Patches Record 974 Vulnerabilities Including Two Exploited Zero-Days"
---
# Windowsゼロデイ脆弱性2件を修正、2026年9月更新は過去最多の約970件

Microsoftは2026年9月の月例セキュリティ更新で、過去最多規模となる約970件の脆弱性を修正しました。その中には、修正前から実際の攻撃で悪用されていたWindowsのゼロデイ脆弱性2件が含まれています。IPAとJPCERT/CCも更新を呼びかけており、個人利用者だけでなく企業のIT管理者にも早期対応が必要です。本記事では、2件のゼロデイの仕組みと影響、今月の更新で特に注意すべき点、Windows Updateの確認方法をわかりやすく整理します。更新後の再起動まで含めて、適用完了を確認することがポイントです。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 関連記事</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/09/13/microsoft-september-2026-security-update-priority/"} /--></div>
<!-- /wp:group -->

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

あわせて、[Microsoft 9月更新の優先適用](https://www.cybernote.click/2026/09/13/microsoft-september-2026-security-update-priority/)、[Windows ALPC CVE-2026-85880](https://www.cybernote.click/2026/09/10/windows-alpc-cve-2026-85880-privilege-escalation-exploited/)、[Windows Update Stack CVE-2026-81963](https://www.cybernote.click/2026/09/10/windows-update-stack-cve-2026-81963-privilege-escalation-exploited/)も確認すると、今回の論点を他のセキュリティ対策と結び付けて整理できます。

## まとめ

2026年9月のMicrosoft月例更新では、悪用確認済みのCVE-2026-81963とCVE-2026-85880を含む過去最多規模の脆弱性が修正されました。2件はいずれも権限昇格で、単独で外部から侵入する種類ではありませんが、侵入後にSYSTEM権限を得る手段として悪用されるため優先度は高いです。個人利用者はWindows Updateを実行して再起動まで完了し、企業は配布管理ツールで未適用端末を確認してください。DNSサーバーなど高深刻度の脆弱性も同時に含まれるため、ゼロデイ2件だけでなく自社で利用しているMicrosoft製品全体を棚卸しすることが重要です。
