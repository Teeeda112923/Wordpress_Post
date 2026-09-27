---
answer: "ENISAは、ランサムウェアの影響と行政機関へのDDoS集中を2026年版の主要論点に挙げました。"
cve: ""
faq:
  - q: "ENISA Threat Landscape 2026とは何ですか？"
    a: "EUのサイバーセキュリティ機関ENISAが、2025年中に観測・分析した脅威をまとめた年次報告書です。2026年9月22日に公開されました。"
  - q: "日本の企業もENISAの報告を参考にできますか？"
    a: "統計は主にEUを対象としており、そのまま日本へ当てはめることはできません。ただし、ランサムウェア、DDoS、サプライチェーンなど共通する脅威の優先順位付けに役立ちます。"
  - q: "最初に見直すべき対策は何ですか？"
    a: "重要システムのバックアップと復旧訓練、外部公開サービスのDDoS対策、委託先を含む連絡・復旧手順の確認を優先してください。"
sources:
  - title: "ENISA Threat Landscape 2026"
    url: "https://www.enisa.europa.eu/publications/enisa-threat-landscape-2026"
    publisher: "European Union Agency for Cybersecurity (ENISA)"
  - title: "Threat Landscape"
    url: "https://www.enisa.europa.eu/topics/cyber-threats/threat-landscape"
    publisher: "European Union Agency for Cybersecurity (ENISA)"
  - title: "StopRansomware Guide"
    url: "https://www.cisa.gov/stopransomware/ransomware-guide"
    publisher: "CISA"
---

# ENISA脅威レポート2026、ランサムウェアとDDoSが主要脅威

EUのサイバーセキュリティ機関ENISAは2026年9月22日、「ENISA Threat Landscape 2026」を公開しました。2025年1月から12月までの事象を分析し、短期的に最も大きな影響を与える脅威としてランサムウェアを挙げています。標的となった組織の73％は、EUのNIS2指令で重要または不可欠と位置づけられる組織でした。日本の被害統計ではありませんが、行政、交通、製造、金融など日本にも直結する分野で何を優先して備えるべきかを考える材料になります。身近なサービスの停止にも関わる内容です。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ ENISA公式レポート</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.enisa.europa.eu/publications/enisa-threat-landscape-2026"} /--></div>
<!-- /wp:group -->

## ランサムウェアは短期的な影響が最大

ENISAは今回も、ランサムウェアを短期的に最も影響の大きいインシデントの種類と評価しました。データ暗号化だけでなく、窃取した情報を公開すると脅す二重脅迫や、業務停止を伴う点が企業や生活者へ直接響きます。

重要なのは、感染を完全に防ぐことだけを目標にしないことです。バックアップを本番環境から分離し、復元に必要な時間を実測し、取引先や顧客への連絡手順まで決めておく必要があります。[ランサムウェアの主な感染経路](https://www.cybernote.click/2026/09/14/ransomware-infection-routes/)も確認し、VPN、認証情報、メール、委託先のどこから侵入されても復旧できる設計にします。

## 行政機関への攻撃はDDoSが82％

業種別では行政機関が標的の32％を占め、最も多く狙われました。その行政機関で記録された事象の82％はDDoS攻撃です。ENISAは、地政学的な動きがサイバー活動に影響し、ハクティビストによるDDoSが重要組織へ向けられていると説明しています。

DDoSは情報を盗む攻撃とは限りませんが、オンライン申請、予約、決済、情報提供を止めれば社会的な影響が生じます。日本の自治体や公共サービスでも、回線やCDNの防御だけでなく、停止時の代替窓口、広報手段、事業者との連絡経路を事前に決めることが大切です。

## 重要インフラとサプライチェーンを一体で考える

標的の73％がNIS2の重要・不可欠組織だったことは、攻撃者が社会への波及効果が大きい対象を選んでいることを示します。行政に続き、ビジネスサービスと交通が各8％、製造が7％、金融・銀行が6％でした。業種をまたぐ備えが必要です。

ただし、この比率を日本の被害割合として使うのは不適切です。国内向けの記事では、EUの観測結果と明記したうえで、[サプライチェーン攻撃のCrowdSec事例](https://www.cybernote.click/2026/09/24/supply-chain-attack-npm-crowdsec/)や[国内のセキュリティ対策評価制度](https://www.cybernote.click/2026/09/14/scs-security-assessment-2026/)と結び付けると、委託先を含めた備えを具体化できます。

## AIは攻撃の補助役として警戒

ENISAは、生成AIや新しいAIモデルが悪意ある活動をさらに支援すると見込んでいます。一方で、報告書の要点は「AIがすべて自律的に攻撃する」という断定ではありません。文章作成、調査、コード作成、反復作業を高速化し、従来型の攻撃を低コストで広げる可能性に注意が必要です。

対策側も、AIという言葉だけで新しい製品を追加するのではなく、多要素認証、更新、ログ監視、バックアップ、DDoS対策など基本を優先します。AI利用を始めた組織は、入力してよい情報、外部ツールとの接続範囲、出力の確認者を決めておきましょう。

## まとめ

ENISA Threat Landscape 2026は、ランサムウェアを短期的に最も影響の大きい脅威とし、行政機関では記録された事象の82％をDDoSが占めたと報告しました。また、標的の73％はNIS2で重要・不可欠とされる組織です。数値はEUの観測であり、日本へそのまま当てはめるべきではありません。それでも、行政、交通、製造、金融など社会を支える組織が、復旧訓練、DDoS時の代替手段、委託先を含む連絡体制を優先すべきことは共通しています。まずは「止めない」だけでなく「止まっても戻せるか」を確認してください。
