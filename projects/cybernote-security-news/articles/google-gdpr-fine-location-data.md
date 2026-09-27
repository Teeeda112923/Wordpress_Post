---
answer: "Googleの位置情報処理にGDPR違反が認定され、4億300万ユーロの制裁金と是正措置が命じられました。"
cve: ""
faq:
  - q: "GDPRとは簡単に言うと何ですか？"
    a: "EU域内の人の個人データを守るためのEUの法律です。2018年5月25日から適用され、データの適法・公正・透明な扱いや、利用者の権利の尊重を企業に求めています。"
  - q: "日本企業にもGDPRは適用されますか？"
    a: "EU域内の人に商品・サービスを提供したり、その行動を監視したりする場合は適用されることがあります。EUに拠点がなくても対象になりうる点に注意が必要です（第3条2項）。"
  - q: "GDPRの制裁金の上限はいくらですか？"
    a: "重大な違反では、2,000万ユーロか全世界の年間売上高の4%のうち、高いほうが上限です。それ以外の違反では、1,000万ユーロか2%のうち高いほうが上限です（第83条）。"
  - q: "日本の個人情報保護法との違いは何ですか？"
    a: "大きな違いの一つは制裁の仕組みです。GDPRには売上高に連動する高額な制裁金があります。一方、日本の個人情報保護法では、個人情報保護委員会の勧告・命令が中心で、命令違反などに対する法人の罰金の上限は1億円です。なお、日本とEUは2019年1月23日から、互いのデータ保護制度を同等とみなす枠組みを運用しています。"
  - q: "Googleの位置情報の設定はどこで見直せますか？"
    a: "Googleアカウントの「データとプライバシー」にある「ウェブとアプリのアクティビティ」と、Googleマップの「タイムライン」で確認できます。保存済みの履歴は「マイアクティビティ」で削除できます。"
sources:
  - title: "Data Protection Commission「Data Protection Commission fines Google €403 million following Inquiry into Google's processing of location data」（2026年9月21日）"
    url: "https://www.dataprotection.ie/en/news-media/latest-news/data-protection-commission-fines-google-eu403-million-following-inquiry-googles-processing-location"
    publisher: "Data Protection Commission"
  - title: "European Data Protection Board「The Irish Data Protection Commission fines Google 403 000 000 EUR following Inquiry into Google's processing of location data」"
    url: "https://www.edpb.europa.eu/news/the-irish-data-protection-commission-fines-google-403-000-000-eur-following-inquiry_en"
    publisher: "European Data Protection Board"
  - title: "The Irish Times「Irish data protection watchdog fines Google €403m over GDPR breaches」"
    url: "https://www.irishtimes.com/business/2026/09/21/irish-data-protection-watchdog-fines-google-403m-over-gdpr-breaches/"
    publisher: "The Irish Times"
  - title: "ABC News（AP）「Google hit with $463 million fine for EU location data rule breach」"
    url: "https://abcnews.com/Technology/wireStory/google-hit-463-million-fine-eu-location-data-136616044"
    publisher: "ABC News（AP）"
  - title: "The Hacker News「Google Fined €403 Million Over GDPR Violations Tied to Location Data」"
    url: "https://thehackernews.com/2026/09/google-fined-403-million-over-gdpr.html"
    publisher: "The Hacker News"
  - title: "BleepingComputer「Google fined €403 million over location data privacy violations」"
    url: "https://www.bleepingcomputer.com/news/security/google-fined-403-million-over-location-data-privacy-violations/"
    publisher: "BleepingComputer"
  - title: "Security Affairs「Google Fined €403 Million Over Location Data Practices」"
    url: "https://securityaffairs.com/199494/laws-and-regulations/google-fined-e403-million-over-location-data-practices.html"
    publisher: "Security Affairs"
  - title: "EUR-Lex「Regulation (EU) 2016/679（GDPR）」"
    url: "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"
    publisher: "EUR-Lex"
---
# GDPR制裁金4億300万ユーロ、Googleの位置情報処理に アイルランド当局が判断

アイルランドのデータ保護委員会（DPC）は2026年9月21日、Googleの位置情報の処理がGDPRに違反したとして、総額4億300万ユーロの制裁金と是正措置を命じました。対象は過去の「ウェブとアプリのアクティビティ」「ロケーション履歴」「位置情報の精度」などの運用で、透明性や適法性、保存期間が論点です。Googleは過去のポリシーに関する案件で、すでに更新済みとの立場を示しています。本記事では判断の内容、GDPRの基本、日本企業や個人が見直すべきポイントを整理します。EUの利用者データを扱う日本企業にも、実務上の示唆が大きい判断です。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 関連記事</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/09/14/scs-security-assessment-2026/"} /--></div>
<!-- /wp:group -->

## 概要：DPCがGoogleに4億300万ユーロの制裁金
アイルランドDPCは、Googleの位置情報の処理について、適法性・公正性・透明性などの面でGDPRに違反したと判断し、4億300万ユーロの制裁金を科しました。GoogleのEUでの主な拠点がアイルランドにあるため、DPCが「主監督機関」（EU全体の窓口となる監督当局）として調査を担当しました。

DPCの発表によると、調査は2020年2月にDPC自身の判断で始まりました（職権調査）。欧州データ保護会議（EDPB）の告知では、きっかけはBEUC（欧州消費者機構）など複数の欧州の消費者団体からの苦情だったと説明されています。調査の対象と、DPCが違反と認定した内容は次のとおりです。

- **ウェブとアプリのアクティビティ、ロケーション履歴**：位置情報処理の適法性・公正性、データの保存期間について違反
- **位置情報の精度**：適法性などを自ら証明する「説明責任」について違反
- **3機能すべて**：利用者への情報提供（透明性）について違反

EDPBの告知ページには、関連条項としてGDPR第5条（処理の原則）、第6条（処理の適法性）、第12条・第13条（透明性と情報提供）が挙げられています。DPCのグラハム・ドイル副コミッショナーは、利用者が「自分の位置情報が広告などに使われていることに気づいていなかった可能性がある」との趣旨を述べています。

金額について補足します。米AP通信などの見出しにある「4億6,300万ドル」は、本文で「4億300万ユーロ（4億6,300万ドル）」と書かれており、同じ制裁金をドルに換算した数字です。別の制裁金ではありません。

Googleは報道各社に対し、「この件は、すでに更新された過去のポリシーに関するもの」とし、2019年以降は位置情報の管理ツールや自動削除などを導入してきたと説明しています。アイリッシュ・タイムズは、Googleが決定の一部に不服を申し立てる可能性があると報じていますが、本稿執筆時点で正式な表明は確認できていません。

## GDPRとは：やさしい解説
GDPR（EU一般データ保護規則）は、EU域内の人の個人データを守るためのEUのルールで、2018年5月25日に適用が始まりました。個人データを「適法・公正・透明に」扱い、目的に必要な範囲・期間に限って使うことなどを企業に求めています。

GDPRの特徴は、違反したときの制裁金がとても高いことです。重大な違反では「2,000万ユーロ」か「全世界の年間売上高の4%」のうち高いほうが上限になります（第83条5項）。今回のDPCの制裁金も、この仕組みにもとづく判断です。

過去の主な高額制裁金と比べると、今回の規模感がわかります。

| 時期 | 対象 | 監督当局 | 制裁金 | 主な論点 |
|---|---|---|---|---|
| 2023年5月 | Meta（Facebook） | アイルランドDPC | 12億ユーロ | EUから米国へのデータ移転 |
| 2021年6月 | Amazon | ルクセンブルクCNPD | 7億4,600万ユーロ | ターゲティング広告 |
| 2025年5月 | TikTok | アイルランドDPC | 5億3,000万ユーロ | 中国へのデータ移転 |
| 2022年9月 | Instagram | アイルランドDPC | 4億500万ユーロ | 子どものデータの扱い |
| 2026年9月 | Google | アイルランドDPC | 4億300万ユーロ | 位置情報の処理 |

アイリッシュ・タイムズによると、今回の金額はDPCが科した制裁金として4番目の規模です。

## 影響：企業と個人にとって何が変わるか
企業にとっては、「利用者に分かる形で説明しているか」「必要以上に長く保存していないか」が、制裁金につながる論点として改めて示されました。個人にとっては、自分の位置情報がどの設定で保存・利用されているのかを見直すよいきっかけです。

企業側への影響として、今回の判断は、位置情報のように個人の行動や生活を細かく映し出すデータについて、規制当局が厳しく見ていることを示しています。DPCは3機能すべてで透明性の義務違反を認定しました。「規約のどこかに書いてある」だけでは十分とされない可能性がある、と受け止めておくのが無難です。

また、対象期間は2018〜2020年と数年前です。過去の運用でも後から責任を問われうる点は、企業にとって見落とせないポイントです。なお報道によると、アイルランドでは制裁金の確定に裁判所の確認が必要とされており、Googleが不服を申し立てた場合、最終的な結論まで時間がかかる可能性があります。

個人への影響として、今回の決定で利用者側が何かをしなければならないわけではありません。ただし、位置情報の保存設定は初期設定のまま放置されがちです。一度確認しておくと安心です。

## 日本企業・個人がとるべき対応（チェックリスト）
日本企業でも、EU域内の人に商品・サービスを提供したり、その行動を追跡・分析したりしていれば、GDPRが適用されることがあります（第3条2項）。以下は一般的な確認ポイントで、法的助言ではありません。具体的な判断は専門家にご相談ください。

**日本企業向けチェックリスト**

- EU域内の顧客・利用者のデータを扱っているかを洗い出す（EC、アプリ、Webサイトのアクセス解析を含む）
- 位置情報など、行動がわかるデータの収集目的と法的根拠（同意など）を整理する
- プライバシーポリシーや同意画面が、利用目的を具体的かつ分かりやすく説明しているか見直す
- 保存期間のルールを決め、期限を過ぎたデータを削除する仕組みがあるか確認する
- 上記の判断や手続きを記録し、後から説明できる状態にしておく（説明責任）

**個人向け：Googleの位置情報設定を確認する方法**

Googleの公式ヘルプによると、次の手順で確認できます。

1. Googleアカウントの「データとプライバシー」から「ウェブとアプリのアクティビティ」を開き、オン・オフや自動削除の設定を確認する
2. 「マイアクティビティ」（myactivity.google.com）で保存済みの履歴を確認し、不要なものを削除する
3. Googleマップの「タイムライン」（旧ロケーション履歴）の設定を開き、オン・オフや保存済みデータを確認する。タイムラインは基本的にデバイス上に保存され、必要に応じて暗号化バックアップをGoogleのサーバーに保存できます

画面の表示は端末やアプリのバージョンによって異なる場合があります。

あわせて、[セキュリティ対策評価制度](https://www.cybernote.click/2026/09/14/scs-security-assessment-2026/)、[AWSとNATO RESTRICTED](https://www.cybernote.click/2026/09/23/aws-nato-restricted-d32-approval-2026/)、[GitLabの重大脆弱性](https://www.cybernote.click/2026/09/24/gitlab-cve-2026-93577-89078-rce-update/)も確認すると、今回の論点を他のセキュリティ対策と結び付けて整理できます。

## まとめ

アイルランドDPCはGoogleの位置情報処理について、適法性・公正性・透明性や保存期間などの義務に違反したとして、4億300万ユーロの制裁金と6か月以内の是正を命じました。対象期間は2018年から2020年であり、過去の運用でも後から責任を問われる可能性があることを示す事例です。EU域内の利用者へサービスを提供したり行動を追跡したりする日本企業もGDPRの適用対象になることがあります。位置情報や行動データの収集目的、法的根拠、説明方法、保存期間、削除手順を定期的に見直し、判断の記録を残すことが重要です。
