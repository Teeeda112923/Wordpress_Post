---
answer: "EvilTokensはMicrosoft 365の認証トークンを狙う手口で、サインイン履歴や転送設定の確認が重要です。"
cve: ""
faq:
  - q: "Microsoftアカウントが乗っ取られていないか確認する方法は？"
    a: "サインイン履歴を確認するのが最も確実です。個人のアカウントは account.live.com/activity、職場のアカウントはマイ アカウントの「最近のアクティビティ」で確認できます。あわせて転送設定、受信トレイのルール、連携アプリも見てください。"
  - q: "乗っ取られたらどうすればいいですか？"
    a: "職場のアカウントなら、すぐに社内の担当者へ連絡してください。個人のアカウントは、MicrosoftがPCのウイルススキャン、パスワード変更、転送・ルールや自動応答などの設定確認を案内しています。サインインできない場合はパスワードのリセットから回復します。"
  - q: "多要素認証とは何ですか？"
    a: "異なる種類の証拠を2つ以上組み合わせて本人確認する仕組みです。パスワードに加えて、スマホアプリの承認や指紋などを求めます。"
  - q: "多要素認証の3つの要素は？"
    a: "「知識」「所持」「生体」の3つです。知識はパスワードなど本人が知っているもの、所持はスマホやセキュリティキーなど持っているもの、生体は指紋や顔です。"
  - q: "多要素認証でも危ない「AiTM攻撃」とは？"
    a: "利用者と本物のサイトの間に偽サイトを挟み、多要素認証後のログイン状態を盗む攻撃です。デバイスコード・フィッシングは偽サイトを使わない点で異なりますが、トークンを奪って多要素認証をすり抜ける点は共通しています。"
  - q: "多要素認証をしないとどうなりますか？"
    a: "パスワードが漏れた時点で、第三者がそのままログインできてしまいます。万能ではありませんが、基本の対策として有効にしておくことが大切です。"
sources:
  - title: "Microsoft Security Blog「Unmasking EvilTokens: Getting to the root of device code phishing」"
    url: "https://www.microsoft.com/en-us/security/blog/2026/09/22/unmasking-eviltokens-getting-to-the-root-of-device-code-phishing/"
    publisher: "Microsoft"
  - title: "Microsoft On the Issues「Disrupting EvilTokens: The AI Chatbot Built for Cybercrime」"
    url: "https://blogs.microsoft.com/on-the-issues/2026/09/22/disrupting-eviltokens-the-ai-chatbot-built-for-cybercrime/"
    publisher: "Microsoft"
  - title: "BleepingComputer「EvilTokens PhaaS disrupted after compromising 12,000 Microsoft accounts」"
    url: "https://www.bleepingcomputer.com/news/security/eviltokens-phaas-disrupted-after-compromising-12-000-microsoft-accounts/"
    publisher: "BleepingComputer"
  - title: "The Register「UK cops arrest 2 EvilTokens suspects, Microsoft seizes 50 phishing kit websites」"
    url: "https://www.theregister.com/security/2026/09/22/uk-cops-arrest-2-eviltokens-suspects-microsoft-seizes-50-phishing-kit-websites/5298317"
    publisher: "The Register"
  - title: "Microsoft Learn「Block authentication flows with Conditional Access policy」"
    url: "https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-block-authentication-flows"
    publisher: "Microsoft"
  - title: "Microsoft サポート「[最近のアクティビティ] ページとは」"
    url: "https://support.microsoft.com/ja-jp/accounts-billing/security/what-is-the-recent-activity-page"
    publisher: "Microsoft"
  - title: "Microsoft サポート「マイ サインインから職場または学校アカウントのサインイン アクティビティを表示する」"
    url: "https://support.microsoft.com/ja-jp/account-billing/9e7d108c-8e3f-42aa-ac3a-bca892898972"
    publisher: "Microsoft"
  - title: "Microsoft サポート「ハッキングまたは侵害された Microsoft アカウントを回復する方法」"
    url: "https://support.microsoft.com/ja-jp/office/35993ac5-ac2f-494e-aacb-5232dda453d8"
    publisher: "Microsoft"
---
# Microsoftアカウント乗っ取りの確認方法と対策｜EvilTokensで1万2,000件超が被害

Microsoftは2026年9月22日、フィッシング・アズ・ア・サービス「EvilTokens」の基盤を停止させたと発表しました。同社によると、1万以上の組織で1万2,000件を超える受信箱が侵害され、Microsoft 365の職場アカウントが狙われました。特徴は、偽のログイン画面ではなく本物のMicrosoftの認証画面を悪用し、認証トークンを得る「デバイスコード・フィッシング」です。本記事では手口を整理し、乗っ取りの確認方法と、個人・企業が取るべき対策を解説します。多要素認証を有効にしている環境でも、トークンの扱いには注意が必要です。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 関連記事</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/09/13/microsoft-september-2026-security-update-priority/"} /--></div>
<!-- /wp:group -->

## EvilTokens事件の概要
EvilTokensは、2026年2月に登場したフィッシング・アズ・ア・サービス（PhaaS、詐欺メールの仕組み一式を月額で貸し出すサービス）で、Microsoftによると1万以上の組織で1万2,000件超の受信箱が侵害されました。Microsoftは9月22日、この基盤を停止させたと公表しています。

Microsoftのセキュリティブログによると、被害が多かったのは米国、カナダ、英国、オーストラリア、インド、フランスで、業種は卸売、建設、金融、不動産、高等教育、医療などです。狙いは企業・組織のアカウントで、請求書の差し替えなどで送金をだまし取る「ビジネスメール詐欺」につなげる目的だったとみられます。公表資料に日本の被害への言及はありません。

報道によると、料金は初期費用1,500ドル、月額500ドルで、Telegramで販売されていました。Microsoftは、AIで標的の役職に合わせた文面を作ったり、奪った受信箱から財務・経営層などの重要人物を探したりする機能があったと説明しています。

| 項目 | 内容 |
|---|---|
| 登場時期 | 2026年2月 |
| 被害規模 | 1万2,000件超の受信箱、1万以上の組織 |
| 主な標的 | 企業・組織のMicrosoft 365アカウント |
| 料金（報道） | 初期1,500ドル＋月額500ドル |
| 妨害した組織 | Microsoft DCUと提携先（Health-ISAC、Cloudflare、SpyCloudなど） |
| 法執行 | 英ロンドン警視庁が9月18日に2人を逮捕（保釈中）と報道 |

The Registerによると、Microsoftは米バージニア州東部地区連邦地裁の許可を得て50のサイトを差し押さえ、関連する150超のドメインも無効化しました。

## デバイスコード・フィッシングの手口をやさしく解説
デバイスコード・フィッシングとは、テレビやゲーム機のサインインに使う「デバイスコード認証」の仕組みを悪用し、利用者自身に攻撃者の端末を承認させる手口です。偽サイトではなく本物のMicrosoftのページを使う点が特徴です。

デバイスコード認証は、キーボードのない機器で「スマホやPCで microsoft.com/devicelogin を開き、画面のコードを入力してください」と案内される方式です。EvilTokensはこれを次のように悪用しました。

| ステップ | 攻撃者の動き | 利用者から見えること |
|---|---|---|
| 1 | 請求書や共有ファイルを装ったメールを送る | 業務連絡のようなメールが届く |
| 2 | 裏でMicrosoftにサインインを申請し、コードを取得 | リンク先に「確認コード」が表示される |
| 3 | コードを入力するよう誘導 | 本物のMicrosoftのページでコードを入力し、普段どおりサインイン |
| 4 | 数秒おきに確認し、承認された瞬間にトークンを受け取る | 特に異変はない |
| 5 | メールを読み、隠しルールを作り、端末を登録して居座る | 気づかないまま被害が続く |

トークンとは「この人はサインイン済み」と示す電子的な通行証です。利用者が本物の画面で多要素認証まで済ませてしまうため、攻撃者はパスワードを知らなくても通行証を得られます。Microsoftは、多要素認証を回避するためのトークン狙いのフィッシングが「はるかに一般的で、産業化している」と指摘しています。

## 影響とリスク
最大のリスクは、正規のサインインとして扱われるため気づきにくく、パスワードを変えても奪われたトークンや登録された端末が残る可能性がある点です。

Microsoftによると、侵入後にはメールの持ち出し、通信を隠すための受信トレイのルール作成、端末登録による長期的な居座りが確認されました。さらに、送金情報や未払いの請求書、経営層のやり取りを探していたといいます。取引先には本物のアドレスから偽の振込先が届くため、被害が社外へ広がるおそれがあります。

なお国内では、日本大学が9月14日、教員5名のメールアカウントが乗っ取られ、不審なメール1,333件が送信されたと公表しました（8月7日発生）。同大学は、フィッシングメール等でIDとパスワードが盗まれたと説明しており、EvilTokensとの関連は示されていません。手口は別物として捉えるのが妥当です。

## Microsoftアカウント乗っ取りの確認方法と対策
乗っ取りの確認は、サインイン履歴、メールの転送・ルール、連携アプリの3点を順に見るのが基本です。職場のアカウントで不審点があれば、自分で判断せず、すぐ社内の情報システム担当者に連絡してください。

### 乗っ取りの確認チェックリスト

- **個人のMicrosoftアカウント**：account.live.com/activity の「最近のアクティビティ」を開きます。過去30日間のサインイン日時、場所、IPアドレス、端末、ブラウザーが表示されます。覚えがなければ「これは自分ではない」を選び、案内に従ってパスワードとセキュリティ情報を更新します。
- **職場・学校のアカウント（Microsoft 365）**：マイ アカウントにサインインし、左側の「最近のアクティビティ」を開きます。サインインの成否、場所、アクセスしたアプリが確認できます。
- **受信トレイのルールと転送**：Outlookの設定で「ルール」と「転送」を開き、自分が作っていない転送先や、特定のメールを削除・移動するルールがないか見ます。自動応答や署名が書き換えられていないかも確認します。
- **連携アプリ**：職場のアカウントなら myapplications.microsoft.com（マイ アプリ）で「アプリケーションの管理」を開き、見覚えのない権限は「権限の取り消し」を選びます。

### 対策

- **不審なコード入力には応じない**：メールやチャットの指示で microsoft.com/devicelogin にコードを入力しないでください。自分が操作しているテレビやゲーム機などのサインイン以外では、まず使いません。
- **管理者はデバイスコードフローを遮断する**：Microsoftは、Entraの条件付きアクセスで「デバイスコードフロー」を原則ブロックし、どうしても必要な用途だけ例外にするよう推奨しています。
- **フィッシング耐性のある認証へ**：パスキーやFIDO2セキュリティキーの利用が推奨されています。
- **侵害時はトークンを失効させる**：Microsoftは、パスワード変更に加え、アカウントの一時停止とサインインセッションの取り消しを推奨しています。

あわせて、[Microsoft 9月更新の優先適用](https://www.cybernote.click/2026/09/13/microsoft-september-2026-security-update-priority/)、[Windows ALPC CVE-2026-85880](https://www.cybernote.click/2026/09/10/windows-alpc-cve-2026-85880-privilege-escalation-exploited/)、[セキュリティ対策評価制度](https://www.cybernote.click/2026/09/14/scs-security-assessment-2026/)も確認すると、今回の論点を他のセキュリティ対策と結び付けて整理できます。

## まとめ

EvilTokensはデバイスコード認証を悪用し、利用者自身に攻撃者側の端末を承認させることでMicrosoft 365の認証トークンを得る手口を提供していました。多要素認証そのものを破るのではなく、正規の認証後に得られるログイン状態を狙うため、MFAを有効にしているだけでは十分ではありません。利用者は不審なコード入力を避け、サインイン履歴、受信トレイのルール、転送設定、連携アプリを確認してください。企業ではデバイスコード認証の制御や条件付きアクセス、トークンの失効、監査ログの確認を組み合わせることが重要です。
