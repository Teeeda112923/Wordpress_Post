---
answer: "no-reply@accounts.google.comは正規アドレスですが、表示が本物でも偽メールはあり得ます。"
cve: ""
faq:
  - q: "no-reply@accounts.google.comからのメールは本物ですか？"
    a: "Googleが実際に使用している正規アドレスです。ただし、差出人表示が正規でも偽メールだった事例があるため、送信元とリンク先をあわせて確認してください。"
  - q: "Googleのセキュリティ通知が本物か確認する方法は？"
    a: "メールのリンクを使わずにmyaccount.google.comを直接開き、セキュリティの項目に同じ通知が記録されているかを確認してください。"
  - q: "sites.google.comはGoogleの公式サイトですか？"
    a: "Googleが運営する正規サービスですが、ページの中身は一般の利用者も作成できます。Googleアカウントのログイン画面はaccounts.google.comです。"
  - q: "パスワードを入力してしまったらどうすればよいですか？"
    a: "正規のGoogleアカウント画面からすぐにパスワードを変更し、ログイン中の端末、アプリパスワード、外部アプリ連携を確認して、心当たりのないものを削除してください。"
sources:
  - title: "VincentBounce X post reporting the phishing attempt"
    url: "https://x.com/VincentBounce/status/2105597638036881669"
    publisher: "X / VincentBounce"
  - title: "Threat analysis: Google Sites phishing that fools password managers via sites.google.com"
    url: "https://ministryofcyberaffairs.com/news/threat-analysis-google-sites-phishing-that-fools-password-managers-via-sites-google-com-ce1a94b4-6c6e-446a-91cf-1070edcb7c6e"
    publisher: "Ministry of Cyber Affairs"
  - title: "Phishers abuse Google OAuth to spoof Google in DKIM replay attack"
    url: "https://www.bleepingcomputer.com/news/security/phishers-abuse-google-oauth-to-spoof-google-in-dkim-replay-attack/"
    publisher: "BleepingComputer"
  - title: "How phishing emails are sent from no-reply@accounts.google.com"
    url: "https://www.kaspersky.com/blog/dkim-replay-attack-through-google-oauth/53392/"
    publisher: "Kaspersky"
  - title: "Gmailのメールが認証されているかどうかを確認する"
    url: "https://support.google.com/mail/answer/180707?hl=ja"
    publisher: "Google"
  - title: "Change where a login is suggested and filled"
    url: "https://support.1password.com/autofill-behavior/"
    publisher: "1Password"
  - title: "psl_matching_helper.h"
    url: "https://android.googlesource.com/platform/external/chromium_org/+/f60fc99/chrome/browser/password_manager/psl_matching_helper.h"
    publisher: "Chromium"
---

# no-reply@accounts.google.comは本物?正規アドレスでも偽物がある見分け方

Googleからセキュリティ通知が届き、差出人のno-reply@accounts.google.comは本物なのかと不安になって調べる人は少なくありません。結論からいうと、このアドレス自体はGoogleが実際に使っている正規のものです。ただし2026年10月、差出人の表示が正規アドレスのまま、リンク先までgoogle.comのドメインになっているフィッシングが報告されました。アドレスやURLの見た目だけでは判定できなくなっています。本記事では、今回の手口の仕組みと、本物と偽物を見分ける確認手順、被害を防ぐ設定までを順に解説します。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 関連記事</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/07/02/%E3%80%90%E3%82%B5%E3%82%A4%E3%83%90%E3%83%BC%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3%E3%80%91%E3%83%95%E3%82%A3%E3%83%83%E3%82%B7%E3%83%B3%E3%82%B0%E8%A9%90%E6%AC%BA%E3%81%A8%E3%81%AF/"} /--></div>
<!-- /wp:group -->

## no-reply@accounts.google.comとは?Googleセキュリティ通知の正規アドレス

no-reply@accounts.google.comは、Googleアカウントに関する通知を送るための送信専用アドレスです。新しい端末からのログイン、パスワードの変更、アプリパスワードの作成といった操作があると、このアドレスからセキュリティ通知や重大なセキュリティ通知が届きます。

つまり、このアドレスからメールが来ること自体は異常ではありません。問題は、差出人欄に正規アドレスが表示されていても本物とは限らない点です。本物かどうかは、差出人ではなく送信経路とリンク先で判断する必要があります。

## 2026年10月に報告された偽のGoogleセキュリティ通知

差出人もリンク先もGoogleに見えるフィッシングが、2026年10月に報告されました。ここでは、報告された手口の流れと想定される被害、そして過去に確認された同種の攻撃との関係を整理します。背景を知っておくと、次に届く通知を落ち着いて判断できます。

### 報告された手口の流れ

2026年10月1日、フランスの利用者がXで、Googleを装う巧妙なフィッシングの標的になったと報告しました。投稿は約230万回表示され、海外のセキュリティ系ニュースサイトも分析記事を公開しています。報告内容と分析記事をもとに、メールの受信から認証情報の入力要求までを整理すると、次の流れになります。

1. アプリパスワードが作成されたと知らせる偽のセキュリティ通知が届く
2. 差出人はno-reply@accounts.google.comと表示され、Gmailの警告も出ない
3. 本文のリンクを開くと、sites.google.com配下のページに移動する
4. 偽のCAPTCHAによる確認画面が表示される
5. Google風のログイン画面でメールアドレスとパスワードの入力を求められる

報告者は入力の手前で不審な点に気づき、認証情報は渡していません。被害件数などの統計は現時点で公表されておらず、実際の被害規模は不明です。ただし入力してしまえば、GmailやGoogleドライブ、YouTubeなど、同じアカウントに紐づくサービス全体を乗っ取られるおそれがあります。他人事と考えず、手口を知っておくことが大切です。

### 2025年にも同種の攻撃が確認されている

同じ構図の攻撃は2025年4月にも報告されています。正規の認証基盤や利用者の操作を逆手に取る攻撃は、[Microsoft 365のデバイスコード・フィッシング事例](https://www.cybernote.click/2026/09/24/eviltokens-microsoft-account-takeover/)でも確認されています。当時はGoogleのOAuthアプリの仕組みを悪用し、Google自身が署名した正規の通知メールを第三者へ転送する、DKIMリプレイ攻撃と呼ばれる手法が使われました。偽ページの置き場所はsites.google.comで、実際の送信経路はprivateemail.comでした。今回の報告でも送信経路に同じドメインが現れており、手口が改良されながら使い回されている可能性があります。なお、今回のメールが同じ仕組みで送られたかどうかは確認されていません。

## 偽物を見破りにくい3つの理由

この手口が厄介なのは、利用者が普段頼りにしている確認方法をいくつもすり抜ける点です。URL、差出人、パスワードマネージャーの3つについて、なぜ判断材料になりにくいのかを順に説明します。仕組みを理解しておくと、見分け方の意味もつかみやすくなります。

### 偽ページが本物のgoogle.com上にある

Google Sitesは、Googleアカウントがあれば誰でもWebページを作れる無料サービスです。作成したページはsites.google.com配下で公開されるため、アドレスバーにはgoogle.comと表示されます。URLの綴りを確認するという従来の対策は、ここでは機能しません。一方で、Googleアカウントの本物のログイン画面はaccounts.google.comにあります。sites.google.com上でパスワードを求められた時点で、偽物と判断できます。

### 差出人表示と署名元だけでは判定できない

Gmailでは、メールの詳細を開くと送信元(mailed-by)と署名元(signed-by)を確認できます。2025年の事例では、偽メールにGoogleの正規の署名が付いており、署名元はaccounts.google.comと表示されていました。差出人と署名元の両方が本物に見えても、安全とは言い切れません。今回の報告で決め手になったのは送信元です。報告者が比較した本物の通知ではgoogle.comで終わるドメインが表示され、偽メールではfwd.privateemail.comと表示されていました。

### パスワードマネージャーが候補を出す場合がある

報告者はsites.google.comのログイン情報を保存しており、偽ページ上でパスワードマネージャーが入力候補を表示しました。1Passwordは初期設定で、保存したサイトと同じWebサイトのサブドメインにも候補を表示します。一方、Chromeのパスワードマネージャーは設計上、google.comについてサブドメインをまたぐ照合を行わない方針をとっています。製品や設定によって挙動が異なるため、候補が出たから本物だと判断するのは危険です。

## Googleの対応状況

2025年の攻撃について、Googleは当初、報告を仕様どおりの動作として扱いましたが、その後に方針を改め、この経路を塞ぐ保護策を導入したと説明しています。今回の件については、報告者がGoogleへ通報済みと述べているものの、2026年10月3日時点でGoogleの公式な見解は確認できていません。

Google Sitesは正規のサービスであり、ドメインごと遮断することは現実的ではありません。利用者側で見分ける手段を持っておくことが欠かせません。

## Googleセキュリティ通知が本物か偽物かを見分ける方法

届いた通知が本物かどうかは、いくつかの箇所を見れば高い確度で判断できます。確認すべきポイントと、心当たりのない通知が届いたときの具体的な対処手順を紹介します。どれもメールのリンクを押す前に行うことが前提です。

![Googleセキュリティ通知が本物か偽物かを見分ける確認ポイント]({{INLINE_IMAGE_URL}})

### 確認すべき3つのポイント

セキュリティ通知が届いたら、本文のリンクを押す前に次の3点を確認します。Gmailでは、パソコン版なら宛先の横にある下向き矢印、Androidアプリなら詳細を表示からセキュリティの詳細を開くと、送信元と署名元を確認できます。今回の報告で示された内容をもとに、本物の通知と偽メールの違いを表にまとめます。

| 確認箇所 | 本物の通知 | 今回の偽メール |
| --- | --- | --- |
| 送信元(mailed-by) | google.comで終わるドメイン | fwd.privateemail.com |
| ログイン画面のURL | accounts.google.com | sites.google.com/view/… |
| 主な導線 | 青い大きなボタン | ボタンの上に置かれたテキストリンク |

3点のうち最も確実なのは、ログイン画面のURLの確認です。送信元の表示は今後の手口で変わる可能性があり、ボタンの配置も攻撃者が修正できます。ログイン画面のアドレスがaccounts.google.comで始まっていない場合は、どれほど本物らしく見えてもパスワードを入力しないでください。迷ったら入力をやめるのが安全です。

### 心当たりがない通知が届いたときの対処

メール内のリンクは使わず、ブラウザでmyaccount.google.comを直接開き、セキュリティの項目から最近のアクティビティを確認します。本物の通知であれば、同じ内容がアカウント側にも記録されています。記録がなければ、そのメールは偽物と考えられます。すでにパスワードを入力してしまった場合は、正規の画面からただちにパスワードを変更し、ログイン中の端末、アプリパスワード、連携している外部アプリを見直してください。

## 被害を防ぐための予防策

見分け方を知っていても、急いでいるときや疲れているときには見落としが起こります。その場の判断に頼らずに済むよう、仕組みで防ぐ設定をあらかじめ済ませておくことが重要です。個人で短時間で実施でき、Googleアカウントの乗っ取り対策として効果が大きいものは次の4つです。できるものから順に進めてください。

- パスキーを設定し、パスワードを入力する場面そのものを減らす
- 2段階認証プロセスを有効にする
- パスワードマネージャーの入力候補を、保存したホストと完全に一致する場合に限定する
- Googleの通知はメールのリンクからではなく、ブックマークしたアカウント画面から確認する

パスキーは、偽サイトにパスワードを渡してしまう危険を減らせる、フィッシング耐性の高い認証方式です。1Passwordを使っている場合は、Googleのログイン項目の自動入力設定をOnly fill on this exact hostに変更しておくと、accounts.google.com以外では候補が表示されなくなります。

## 企業と業界が学ぶべき教訓

今回の事例は個人だけの問題ではありません。従業員のGoogleアカウントを業務に使っている企業にとっても、セキュリティ教育の内容と検知ルールを見直すきっかけになります。考え方と具体策の2つに分けて整理します。

### 正規ドメインを信頼の根拠にしない

今回の手口は新しいマルウェアではなく、正規サービスへの信頼を悪用したものです。Google Sitesに限らず、フォームやクラウドストレージなど、利用者がコンテンツを置ける正規サービスは同じように悪用され得ます。URLのドメインを確認するという教育だけでは不十分で、認証情報を入力してよいホスト名を具体的に決めて周知する必要があります。

### 組織で取るべき対策

企業では、フィッシング訓練や注意喚起の題材に、正規ドメイン上の偽ログイン画面を加えることが有効です。技術面では、Googleを名乗るセキュリティ通知のうち送信元がGoogleのドメインでないものを検知するルールや、sites.google.com配下のログイン風ページへのアクセス監視が考えられます。Google Workspaceを利用している組織は、パスキーやセキュリティキーなど、フィッシング耐性のある認証方式への移行を優先して進めるべきです。[ホテルWi-Fi経由でMicrosoft 365認証を狙った攻撃事例](https://www.cybernote.click/2026/07/27/hotel-free-wi-fi/)のように、ログイン画面だけでなく認証経路そのものが狙われるケースもあるためです。

## まとめ

no-reply@accounts.google.comはGoogleの正規アドレスですが、差出人の表示だけでは本物かどうかを判定できません。2026年10月に報告されたフィッシングでは、差出人表示もリンク先のドメインもgoogle.comのまま、Google Sites上の偽ログイン画面へ誘導していました。見分ける決め手は、送信元がGoogleのドメインかどうかと、ログイン画面がaccounts.google.comにあるかどうかの2点です。通知が届いたらメールのリンクは使わず、アカウント画面を直接開いて確認する習慣をつけ、パスキーの設定も済ませておきましょう。
