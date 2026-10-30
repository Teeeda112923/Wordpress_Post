---
answer: "Binanceは2026年10月30日、約63億ドルの影響が見込まれるセキュリティインシデントを公表しました。DevOps担当者の端末侵害が関与した可能性は初期調査の段階で、最終損失額、侵入経路、犯行主体は確定していません。利用者は公式アプリ・公式サイトだけで入出金状況と告知を確認し、復旧を装うフィッシングに注意してください。"
cve: ""
faq:
  - q: "Binanceで約1兆円が盗まれたことは確定していますか？"
    a: "確定しているのは、Binanceが約63億ドルを推定総影響額として公表したことです。凍結額、回収額、資産価格の変動を反映した最終損失は未確定で、調査完了後の技術報告を待つ必要があります。"
  - q: "Binanceの利用者は今すぐ何を確認すべきですか？"
    a: "メールやSNSのリンクではなく、公式アプリか自分で入力した公式サイトから資産残高、入出金状況、セキュリティ通知を確認してください。復旧支援を名乗る第三者に送金、認証コード、秘密鍵を渡してはいけません。"
  - q: "北朝鮮関与はBinanceが認めた情報ですか？"
    a: "いいえ。TRM Labsは北朝鮮関連組織TraderTraitorによるものと高い確信度で評価しましたが、Binanceの公式発表は犯行主体を確定していません。分析会社の帰属判断と、当局・Binanceの確定発表は分けて読む必要があります。"
sources:
  - title: "Security Incident Update"
    url: "https://www.binance.com/zh-TC/support/announcement/detail/c5a8729a97ac486d963784d96c5642d7"
    publisher: "Binance"
  - title: "North Korea Steals USD 6.36 Billion From Binance in the Largest Hack in History"
    url: "https://www.trmlabs.com/resources/blog/north-korea-steals-usd-6-36-billion-from-binance-in-the-largest-hack-in-history"
    publisher: "TRM Labs"
  - title: "Binance $5.5B Hack: Using Advanced AI Models, Blockaid Detects the Biggest Theft in Crypto History"
    url: "https://blockaid.io/blog/binance-55b-hack-using-advanced-ai-models-blockaid-detects-the-biggest-theft-in-crypto-history"
    publisher: "Blockaid"
  - title: "Binance flags potential security incident as $6.3 billion impacted"
    url: "https://apnews.com/article/binance-cryptocurrency-security-39cda8ceb8095e036334a18549d3d20d"
    publisher: "Associated Press"
---
# Binanceの「約1兆円」セキュリティインシデントとは？確認済みの事実と未確定情報

[Binance](https://www.binance.com/)は2026年10月30日、セキュリティインシデントの推定総影響額が約63億ドルだと公表しました。1ドル＝約150〜160円で概算すれば約1兆円規模ですが、この数字は最終損失額ではありません。初期調査ではDevOps担当者のノートPC侵害が関与した可能性、サービスコンテナへのアクセス、不正な出金取引が示されています。一方で、Binanceはウォレット秘密鍵の漏えいを示す証拠はないとし、詳細な技術報告は調査完了後に出す方針です。本記事では、公式発表、オンチェーン分析、報道を区別して整理します。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 参照</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.binance.com/zh-TC/support/announcement/detail/c5a8729a97ac486d963784d96c5642d7"} /--></div>
<!-- /wp:group -->

## Binanceが公式に公表した内容

公式発表で確認できるのは、約63億ドルという推定総影響額、約30億ドルのオンチェーン凍結、入出金の一時停止です。これは利用者データの漏えいではなく、不正な出金取引を含むセキュリティ事案として説明されています。

Binanceは認可を失効させ、関係機関と資産の追跡・回収を進めると説明しています。損失はSAFU基金と自社資金で補填する方針ですが、補償の実行状況や入出金の再開時刻は未確定です。

## 「約1兆円」をそのまま被害額と呼べない理由

63億ドルはBinanceの「推定総影響額」であり、凍結済み資産や今後の回収分を控除した確定損失ではありません。円換算額も為替と暗号資産価格で変動するため、見出しだけで被害額が確定したと受け取らないことが重要です。

TRM Labsは10チェーンで約63.6億ドル、Blockaidは公開時点で少なくとも55億ドルと推計しました。集計時点と評価方法が異なるため、数字の差だけで誤りとは断定できません。[国内のサイバー事案まとめ](https://www.cybernote.click/2026/10/01/september-2026-cyber-incidents-roundup/)と同じく、更新日時と発表主体を併記して追います。

## 侵入経路と攻撃手法はどこまで分かっているか

DevOps担当者の端末が侵害された可能性はBinanceの初期調査に基づく説明で、確定した根本原因ではありません。秘密鍵漏えいが原因だったと断定する根拠も、公式発表にはありません。この段階では仮説として扱います。

TRM LabsとBlockaidは、Ethereum上でEIP-7702の認可を悪用してホットウォレットを資産回収用コントラクトへ委任した形跡や、複数チェーンの署名済み取引を分析しています。これはオンチェーン分析で、Binanceの確定説明ではありません。[不正アクセス後の対応](https://www.cybernote.click/2026/10/13/government-unauthorized-access-alert-2026-10/)と同様に、推測を確定事実として広めない姿勢が必要です。

## 犯行主体の推定と利用者が取るべき行動

TRM Labsは、オンチェーンとオフチェーンの情報を根拠に、北朝鮮関連組織TraderTraitorによるものと高い確信度で評価しました。しかしBinanceは犯行主体を公式に特定しておらず、捜査機関による公表も確認できません。

利用者は、Binanceを装うメール、DM、広告経由の「出金再開」「資産回復」案内を信用しないでください。公式アプリまたは自分で入力した公式URLから告知と残高を確認し、パスワードの使い回しをやめ、多要素認証を有効にします。[フィッシング対策](https://www.cybernote.click/2026/10/04/no-reply-accounts-google-com-honmono/)も確認してください。秘密鍵や認証コードを第三者へ渡すことはありません。

## まとめ

Binanceの約63億ドルという公表は、約1兆円規模と換算される重大なセキュリティインシデントです。ただし、これは推定総影響額であり、凍結・回収後の最終損失、根本原因、犯行主体は確定していません。公式発表で確認できるのは、DevOps担当者端末の侵害が関与した可能性、約30億ドルの凍結、入出金の一時停止、補填方針です。TRM Labsなどの分析は有用ですが、公式の技術報告や捜査機関の発表とは分けて扱うべきです。利用者は不安を利用する詐欺を避け、公式チャネルだけで状況を確認し、続報を待ってください。
