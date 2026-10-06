---
answer: "FBIはfbijobs.govへの侵害主張と職員の個人情報への影響を把握し、調査を続けています。"
cve: "CVE-2026-35273"
faq:
  - q: "FBIは求人サイトへの侵害を公式に認めていますか？"
    a: "FBIはfbijobs.govを侵害したとの犯罪グループの主張を把握し、職員の個人情報への影響を含めて積極的に調査していると発表しています。"
  - q: "原因はPeopleSoftの脆弱性だったのですか？"
    a: "ReutersはPeopleSoftの重要な更新未適用が侵害につながったと報じていますが、FBIは公開文書で具体的な侵入経路を確定していません。"
  - q: "CVE-2026-35273とは何ですか？"
    a: "Oracle PeopleSoft Enterprise PeopleToolsの重大な脆弱性で、認証なしでネットワーク経由から悪用でき、CVSS 9.8と評価されています。"
sources:
  - title: "FBI Statement on Compromise of fbijobs.gov Portal and Alleged Impact to FBI Employee PII"
    url: "https://www.fbi.gov/news/press-releases/fbi-statement-on-compromise-of-fbijobsgov-portal-and-alleged-impact-to-fbi-employee-pii"
    publisher: "FBI"
  - title: "Accenture contractor removed from FBI following damaging data breach, sources say"
    url: "https://www.reuters.com/technology/accenture-contractor-removed-fbi-following-damaging-data-breach-sources-say-2026-10-06/"
    publisher: "Reuters"
  - title: "Oracle Security Alert Advisory - CVE-2026-35273"
    url: "https://www.oracle.com/security-alerts/alert-cve-2026-35273.html"
    publisher: "Oracle"
  - title: "ShinyHunters Renewed Mass Exploitation Campaign Targeting Oracle PeopleSoft"
    url: "https://cloud.google.com/blog/topics/threat-intelligence/shinyhunters-renewed-mass-exploitation-campaign-targeting-oracle-peoplesoft"
    publisher: "Google Cloud / Mandiant"
---
# FBI求人サイトで情報侵害　職員の個人情報に影響、PeopleSoft脆弱性との関係を整理

米連邦捜査局（FBI）は2026年9月23日、サイバー犯罪グループが求人サイト「fbijobs.gov」を侵害し、FBI職員の個人情報に影響したと主張していることを把握し、調査中だと発表しました。FBIは当時、侵入口が第三者側かFBI側かは未確定としていました。その後Reutersは10月6日、外部委託先がOracle PeopleSoftの重要な更新を適用していなかったことが侵害につながったと関係者情報として報道しています。公式確認と報道内容、PeopleSoft脆弱性との関係を分けて整理します。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 関連記事</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/10/05/why-cyber-incidents-ai-patch-tuesday/"} /--></div>
<!-- /wp:group -->

## FBIが公式に確認している内容

FBIは9月23日、犯罪グループによるfbijobs.gov侵害の主張と、FBI職員の個人を識別できる情報への影響の主張を把握していると発表しました。第三者事業者とも連携し、影響の確認とリスク低減を進めています。

この時点でFBIは、侵入口が求人サイトを支援する第三者側なのか、FBIの組織内システム側なのかを特定していないと明記しました。したがって、9月23日の公式発表だけから侵入経路や悪用された製品を断定することはできません。[大規模インシデントを事実ベースで整理した9月のまとめ](https://www.cybernote.click/2026/10/01/september-2026-cyber-incidents-roundup/)と同様、確定範囲の切り分けが重要です。

## ReutersはPeopleSoftの更新未適用を報道

Reutersは10月6日、事情を知る関係者の話として、FBI求人関連システムを支援していたAccentureの担当者がOracle PeopleSoftの重要なセキュリティ更新を適用しておらず、それが侵害につながったと報じました。

同報道では、FBI職員の機微な個人情報が影響を受けたとされています。一方、この原因説明はFBIの9月23日の発表より後に出た報道であり、FBIが公開文書で技術的な侵入経路を確定したものとして扱うべきではありません。委託先を含むパッチ管理は、[大和証券の委託先を巡る事案](https://www.cybernote.click/2026/10/05/daiwa-securities-data-breach-2026/)にも通じる確認点です。

## PeopleSoftのCVE-2026-35273とは

Oracleは6月10日、PeopleSoft Enterprise PeopleToolsの脆弱性「CVE-2026-35273」を緊急情報として公開しました。対象は8.61と8.62で、ログインしていない攻撃者がネットワーク経由で悪用できる可能性があります。

Oracleの評価はCVSS 9.8で、悪用に成功すると遠隔から不正なコードを実行されるおそれがあります。GoogleのMandiantと脅威分析チームは、ShinyHuntersとして知られるUNC6240が同脆弱性を実際の攻撃で悪用したと報告しています。ただし、FBIの今回の侵害でCVE-2026-35273が使われたとFBIが公式に確定した情報はありません。

## WAFだけに頼らず修正適用を優先する

Googleは9月25日、CVE-2026-35273を狙う攻撃が再び広がり、攻撃者がWeb通信を検査する仕組み「WAF」の単純な遮断ルールを回避したと報告しました。文字列の一部を別表記に変え、同じ処理先へ到達する手法です。

これは、一時的な通信遮断だけを修正プログラムの代わりにしないことの重要性を示します。Oracleも更新の速やかな適用を推奨しています。[Citrix製品の重大脆弱性対応](https://www.cybernote.click/2026/10/05/citrix-netscaler-cve-2026-88779-saml-dos-update/)でも共通しますが、実際の悪用が確認された弱点は優先度を上げ、委託先を含めて適用状況を確認する必要があります。

## まとめ

FBIは2026年9月、fbijobs.govの侵害を主張する犯罪グループと、職員の個人情報への影響について調査を開始しました。9月23日の公式発表では侵入口は未確定です。Reutersは10月6日、外部委託先でPeopleSoftの重要な更新が適用されていなかったことが侵害につながったと報じました。一方、CVE-2026-35273がFBI侵害で使われたとFBIが公式に確定した情報はありません。同脆弱性自体はOracleがCVSS 9.8と評価し、Googleが実悪用を確認しています。企業は報道と公式確認を区別しつつ、重大な更新の適用状況を委託先まで含めて確認することが重要です。
