---
title: "AIがサイバー攻撃を自律化する時代へ｜GLM-5.3・Claude CodeとN-day攻撃の脅威"
slug: "ai-autonomous-cyberattack-glm-5-3-2026"
date: "2026-10-07"
author: "CyberNote編集部"
description: "GLM-5.3やClaude Codeなど、AIを利用したサイバー攻撃はどこまで現実化しているのか。2026年9月以降の事例とAnthropic・Google・MITREの分析をもとに、N-day攻撃やランサムウェアの脅威、SOC・CSIRTが見るべきログと対策を解説します。"
answer: "AI攻撃は直接識別しにくい一方、攻撃行動をログで相関し、封じ込めを高速化することで対抗できます。"
cve: ""
faq:
  - q: "AIが自動で企業へサイバー攻撃することは可能ですか？"
    a: "偵察、脆弱性探索、Exploit開発、認証情報収集など複数工程の自動化はすでに確認されています。ただし標的選定や重要判断では人間が関与する事例が多く、完全自律攻撃が一般化した段階ではありません。"
  - q: "GLM-5.3が日本企業への攻撃に使われたのですか？"
    a: "タイムズカーやGyazoなど2026年秋の国内事案でGLM-5.3が使われたとする公表は確認されていません。注目点は、高度なExploit能力を持つオープンウェイトAIが利用可能になったことです。"
  - q: "AI攻撃はIPアドレスを遮断すれば防げますか？"
    a: "IP遮断は有効な対策の一つですが、それだけでは不十分です。クラウドや侵害済みサーバー、複数IPを使う攻撃では、送信元よりも認証やプロセス、内部探索などの行動を横断して見る必要があります。"
  - q: "SOCやCSIRTはAI攻撃をどう検知すればよいですか？"
    a: "AIそのものを判定するのではなく、WAF、EDR、認証、AD、クラウド、Proxy、DNSのログを時系列で結び、探索から侵入、横展開、データ持ち出しまでの攻撃チェーンとして検知します。"
sources:
  - title: "CAISI’s Assessment of Z.ai’s GLM-5.3 Cyber Capabilities"
    url: "https://www.nist.gov/news-events/news/2026/09/caisis-assessment-zais-glm-53-cyber-capabilities"
    publisher: "NIST CAISI"
  - title: "GLM-5.3 and the spread of advanced cyber capabilities"
    url: "https://www.anthropic.com/research/glm-5-3-and-the-spread-of-advanced-cyber-capabilities"
    publisher: "Anthropic"
  - title: "Detecting and countering misuse of AI: September 2026"
    url: "https://www.anthropic.com/threat-intelligence-report-september-2026?page=1"
    publisher: "Anthropic"
  - title: "GTIG AI Threat Tracker: From Prompting to Autonomy – The Evolution of Adversarial AI"
    url: "https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai"
    publisher: "Google Threat Intelligence Group"
  - title: "Vulnerability Discovery and Exploitation Trends in the AI Era"
    url: "https://cloud.google.com/blog/topics/threat-intelligence/vulnerability-discovery-and-exploitation-trends-in-the-ai-era"
    publisher: "Google Threat Intelligence Group"
  - title: "Anthropic AI-orchestrated Campaign, C0062"
    url: "https://attack.mitre.org/campaigns/C0062/"
    publisher: "MITRE ATT&CK"
  - title: "Impact of AI on cyber threat from now to 2027"
    url: "https://www.ncsc.gov.uk/report/impact-ai-cyber-threat-now-2027"
    publisher: "UK NCSC"
  - title: "タイムズカーWebシステムへの不正アクセスに関する調査結果および今後の対応について（第2報）"
    url: "https://www.park24.co.jp/news/2026/09/20260928-1.html"
    publisher: "パーク24"
  - title: "Notice Regarding Unauthorized Access to Gyazo (September 25, 2026)"
    url: "https://help.gyazo.com/Notice%20Regarding%20Unauthorized%20Access%20to%20Gyazo%20%28September%2025%2C%202026%29-6ab648b661f85ecc9543375f"
    publisher: "Gyazo"
  - title: "郵便局アプリへの不正アクセスについて"
    url: "https://www.japanpost.jp/news/pressrelease/20260929_01/"
    publisher: "日本郵政・日本郵便"
  - title: "お荷物問い合わせサービスへの不正アクセス"
    url: "https://www.sagawa-exp.co.jp/customer/"
    publisher: "佐川急便"
---

# AIがサイバー攻撃を自律化する時代へ｜GLM-5.3・Claude CodeとN-day攻撃の脅威

2026年9月以降、日本ではタイムズカー、Gyazo、日本郵便、佐川急便などで不正アクセスや情報漏えいが相次ぎました。これらの国内事案でAI利用が確認されたわけではありません。一方、海外ではAIが脆弱性探索、Exploit開発、認証情報収集、内部探索までを担う攻撃が現実に報告されています。本記事では、最新の一次情報を基に、AIがサイバー攻撃をどう変えるのか、N-dayやランサムウェアのリスク、SOC・CSIRTが見るべきログと企業の対策まで整理します。攻撃者と防御側の時間競争という視点から、従来の常識がどこまで変わるのかも見ていきます。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 関連記事</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/10/01/september-2026-cyber-incidents-roundup/"} /--></div>
<!-- /wp:group -->

## 2026年9月以降、国内で不正アクセスや情報漏えいが相次ぐ

2026年秋は、消費者向けWebサービスやアプリを含む複数の企業・組織で不正アクセスが公表されました。ただし、近い時期に発生したことと同一の攻撃キャンペーンであることは別問題です。各社の公表内容を分けて確認する必要があります。

### タイムズカーでは約660万アカウントの情報が漏えい

パーク24は2026年9月25日、タイムズカーWebシステムへの外部からの不正アクセスを検知しました。9月28日の第2報では、約660万アカウント分の情報が第三者に取得されたことを確認しています。さらに9月29日の第3報では、運転免許証画像など本人確認書類が漏えいしたアカウントが約160万件だったと公表しました。

氏名、住所、生年月日、電話番号、メールアドレスなどに加えて本人確認書類まで含まれるため、漏えい後のなりすましやフィッシングにも注意が必要です。一方、この事案についてAIやGLM-5.3が使われたとする情報は公表されていません。国内事案とAI攻撃の議論を混同しないことが重要です。

CyberNoteでは[タイムズカーの不正アクセスと情報漏えい](https://www.cybernote.click/2026/09/28/timescar-unauthorized-access-data-leak-2026/)を別記事で詳しく整理しています。

▼　本件はこの文献を参考にしました  
[パーク24「タイムズカーWebシステムへの不正アクセスに関する調査結果および今後の対応について（第2報）」](https://www.park24.co.jp/news/2026/09/20260928-1.html)  
[パーク24「同（第3報）」](https://www.park24.co.jp/news/2026/09/20260929-1.html)

### Gyazoでは約2,362万ユーザーのデータが外部露出

画像共有サービスGyazoは、2026年9月に不正アクセスによる情報露出を公表しました。9月25日時点の調査では約2,362万件のユーザーレコードに加え、主に2019年1月以前の約4億9,000万件の画像メタデータ、さらに削除済み画像約1億7,400万件のメタデータが露出したとしています。

影響範囲はユーザーごとに異なりますが、メールアドレス、パスワードハッシュ、ログイン関連情報、画像ID、アクセス元IPアドレス、User-Agent、条件によってはEXIF位置情報やOCR文字列などが含まれます。大量のデータが流出した場合、その後の選別や分析にもAIを転用できる点は今後のリスクとして無視できません。

CyberNoteの[Gyazo情報流出の解説](https://www.cybernote.click/2026/10/01/gyazo-data-breach-23-million-users-2026/)では、利用者が確認したいポイントもまとめています。

▼　本件はこの文献を参考にしました  
[Gyazo「Notice Regarding Unauthorized Access to Gyazo (September 25, 2026)」](https://help.gyazo.com/Notice%20Regarding%20Unauthorized%20Access%20to%20Gyazo%20%28September%2025%2C%202026%29-6ab648b661f85ecc9543375f)

### 日本郵便や佐川急便でも不正アクセスを公表

日本郵政と日本郵便は9月29日、「郵便局アプリ」への不正アクセスを公表しました。佐川急便も9月30日、「お荷物問い合わせサービス」への不正アクセスを公表し、10月1日には個人情報流出の可能性に関する続報を出しています。

これらから分かるのは、攻撃対象が金融機関や重要インフラだけではないことです。一般利用者向けのアプリ、荷物追跡、会員サービスなど、インターネットから到達できるシステムは幅広く攻撃対象になります。AIによって探索コストが下がれば、「有名企業だから狙われる」という従来の見方はさらに弱くなります。

CyberNoteでは[郵便局アプリの不正アクセス](https://www.cybernote.click/2026/10/04/japan-post-app-data-breach-2026/)と[佐川急便の不正アクセス](https://www.cybernote.click/2026/10/04/sagawa-express-tracking-data-breach-2026/)も個別に解説しています。

▼　本件はこの文献を参考にしました  
[日本郵政・日本郵便「郵便局アプリへの不正アクセスについて」](https://www.japanpost.jp/news/pressrelease/20260929_01/)  
[佐川急便「お荷物問い合わせサービスへの不正アクセス」](https://www.sagawa-exp.co.jp/customer/)

## AIは「攻撃コード作成」から「攻撃工程の実行役」へ

AIのサイバー利用で本当に重要なのは、文章生成やコード補助だけではありません。最近の研究と脅威インテリジェンスでは、偵察、脆弱性探索、Exploit開発、認証情報収集など複数工程をAIエージェントへ任せる方向が明確になっています。

### GLM-5.3は高いサイバー能力を持つオープンウェイトAI

中国のZ.aiが2026年8月14日に公開したGLM-5.3について、米NIST傘下のCAISIは9月17日、公開済みのオープンウェイトモデルの中で最も高いサイバー能力を持つと評価しました。ただし、総合的なサイバー能力では米国の最新フロンティアモデルより低く、約4か月分の差があるとの評価も示しています。

AnthropicもGLM-5.3を検証し、高度な脆弱性を分析してエンドツーエンドのExploitを自律的に構築できる能力を確認しました。ここでいうExploitとは、ソフトウェアの脆弱性を利用して本来想定されていない処理を実行するための攻撃手法やコードを指します。

重要なのはGLM-5.3が「世界最強の攻撃AI」という意味ではなく、高度な能力を持つモデルの重みが公開され、利用者側の環境で動かせることです。クラウドAIのように提供企業のAPI監視やアカウント停止だけで利用を抑えることが難しくなります。

▼　本件はこの文献を参考にしました  
[NIST CAISI「CAISI’s Assessment of Z.ai’s GLM-5.3 Cyber Capabilities」](https://www.nist.gov/news-events/news/2026/09/caisis-assessment-zais-glm-53-cyber-capabilities)  
[Anthropic「GLM-5.3 and the spread of advanced cyber capabilities」](https://www.anthropic.com/research/glm-5-3-and-the-spread-of-advanced-cyber-capabilities)

### Claude Codeを使ったAIオーケストレーションはMITRE ATT&CKにも登録

AIエージェントを攻撃の実行役として使う構造は仮説だけではありません。MITRE ATT&CKには「Anthropic AI-orchestrated Campaign（C0062）」が登録されています。2025年9月、攻撃者はClaude CodeとModel Context Protocol（MCP）ツールを使い、約30の組織を対象に活動しました。

MITREによると、Claude CodeはIPレンジのスキャン、脆弱性探索、Exploit、横展開、認証情報収集、データ分析、持ち出しなどに利用されました。人間のオペレーターは攻撃を細かなタスクへ分け、プロンプトや役割設定を使ってAIを制御していました。

つまり現実に近い姿は「AIが勝手に標的を決めて全自動で攻撃する」よりも、人間が目的と重要判断を持ち、AIエージェントへ調査や実行を任せるHuman-in-the-loop型です。Claude CodeやCodexのようなエージェント環境を攻撃基盤に組み込み、必要な場面だけ人間が確認する構成は技術的にも現実味を増しています。

▼　本件はこの文献を参考にしました  
[MITRE ATT&CK「Anthropic AI-orchestrated Campaign, C0062」](https://attack.mitre.org/campaigns/C0062/)

### Googleは6時間未満で構築・実行されたエージェント型攻撃を確認

Google Threat Intelligence Group（GTIG）は2026年9月、侵害済みクラウド環境上に構築されたAIエージェント型の攻撃基盤を報告しました。脅威アクターはAIコーディング支援、プロンプト、エージェント向け指示を組み合わせ、脆弱性スキャン、エラー対応、認証情報収集、IPローテーションなどを自動化しました。

GTIGによれば、攻撃者がクラウド資源を侵害してから、エージェントを利用した大規模な認証情報収集キャンペーンを計画・構築・実行するまで6時間未満でした。AIが結果を見て次の行動を調整することで、人間の判断待ち時間が大幅に短くなっています。

また攻撃元には侵害された正規クラウド環境が使われていました。標的側から見れば「AIからアクセスされた」のではなく、一般的なクラウド事業者のIPアドレスから通常のHTTP通信や認証試行が届く形になります。ここがAI利用そのものをネットワーク境界で識別しにくい理由です。

▼　本件はこの文献を参考にしました  
[Google Threat Intelligence Group「From Prompting to Autonomy – The Evolution of Adversarial AI」](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai)

## AI攻撃で想定される4つの被害

AIが新しい攻撃経路を無限に発明するというより、既存の攻撃を高速化・並列化する影響が現実的です。特に企業側の猶予時間を縮めやすいN-day、未知脆弱性、認証情報窃取、ランサムウェアや恐喝の四つは優先して考える必要があります。

### 1．N-day攻撃が高速化し、パッチ適用前に狙われる

N-day攻撃とは、脆弱性の存在や修正方法がすでに公表されている一方、まだ更新されていないシステムを狙う攻撃です。英国NCSCは、脆弱性の公開から悪用までの期間がすでに「日」単位まで縮まり、AIによってさらに短くなる可能性が高いと評価しています。

Googleの2026年9月30日の分析では、実際に悪用されたHigh-Risk脆弱性は2025年の28件から、2026年1～8月だけで75件へ増加しました。GTIGはゼロデイの増加だけでは説明できず、N-day脆弱性の迅速な武器化が主要な伸びの一つだと分析しています。

AIがパッチ前後の差分、公開されたPoC、製品情報、脆弱性告知をまとめて解析し、Exploit候補を検証できるようになれば、「毎月まとめて更新する」運用では間に合わないケースが増えます。ただし、2026年のN-day悪用増加そのものをAIだけが原因と断定することはできません。

CyberNoteでは[AIで縮むPatch Tuesday後の攻撃猶予](https://www.cybernote.click/2026/10/05/why-cyber-incidents-ai-patch-tuesday/)でも、この時間競争を詳しく解説しています。

▼　本件はこの文献を参考にしました  
[UK NCSC「Impact of AI on cyber threat from now to 2027」](https://www.ncsc.gov.uk/report/impact-ai-cyber-threat-now-2027)  
[Google Threat Intelligence Group「Vulnerability Discovery and Exploitation Trends in the AI Era」](https://cloud.google.com/blog/topics/threat-intelligence/vulnerability-discovery-and-exploitation-trends-in-the-ai-era)

### 2．ゼロデイ探索とExploit開発のハードルが下がる

N-dayより難易度は高いものの、AIが未知の脆弱性を探す能力も向上しています。AnthropicのGLM-5.3検証では、ブラウザなどの複雑な対象に対して脆弱性を調べ、複数の問題を組み合わせながら動作するExploitを構築する能力が確認されています。

ゼロデイでは、攻撃時点で修正パッチが存在しない場合があります。そのため「更新を適用すれば終わり」という対策だけでは不十分です。侵入後のプロセス実行、権限昇格、認証情報へのアクセス、内部通信などをEDR/XDRやネットワーク監視で捉える多段の防御が必要になります。

AIによる脆弱性研究は防御側にも利益があります。開発者やセキュリティ研究者が先に脆弱性を発見し修正できればリスクは下がるため、AI能力の向上がそのまま攻撃者だけの優位を意味するわけではありません。攻撃側と防御側の双方が同じ高速化技術を利用する競争になります。

▼　本件はこの文献を参考にしました  
[Anthropic「GLM-5.3 and the spread of advanced cyber capabilities」](https://www.anthropic.com/research/glm-5-3-and-the-spread-of-advanced-cyber-capabilities)

### 3．盗んだ認証情報から内部へ素早く横展開する

AIエージェントにとって、毎回高度なExploitを作る必要はありません。有効なID、パスワード、APIキー、アクセストークンを取得できれば、その後は正規利用者に近い形で内部サービスへアクセスできるためです。

MITREのC0062でも、Claude Codeは侵害後のアカウント探索や認証情報収集、内部環境の調査に利用されています。AIがActive Directory、データベース、クラウドRole、コンテナ、コードリポジトリなどを調査し、価値の高い権限や次の侵入先を判断する構造が成立します。

この場合、Firewallから見えるIPアドレスだけでは判定しにくくなります。正規アカウントによる正規サービスへのログインは、一見すると通常業務に近いからです。「誰がログインしたか」に加えて、普段の端末、場所、ASN、利用アプリ、アクセス先、時間帯との違いを見るIdentityベースの検知が重要になります。

▼　本件はこの文献を参考にしました  
[MITRE ATT&CK「Anthropic AI-orchestrated Campaign, C0062」](https://attack.mitre.org/campaigns/C0062/)  
[Anthropic「Detecting and countering misuse of AI: September 2026」](https://www.anthropic.com/threat-intelligence-report-september-2026?page=1)

### 4．ランサムウェアやデータ窃取型恐喝まで効率化する

AIの強みは侵入だけではなく、大量情報の読解と分類にもあります。侵害した環境で大量のファイル、メール、データベース、クラウド情報を取得した場合、AIを使って重要情報を短時間で選別できます。

攻撃者にとっては、「何を盗めば企業への圧力が最大になるか」を調べる作業の効率化につながります。従来型ランサムウェアのようにファイルを暗号化するだけでなく、機密情報を盗み、公開を材料に金銭を要求するデータ窃取型恐喝との相性も悪いと言えます。

Anthropicの2026年9月レポートでは、AIを使ったサイバー活動で偵察、侵入、資格情報探索、データ収集などの自動化が進んでいることが示されています。AIが攻撃工程間の時間を圧縮すれば、SOCが最初のアラートを調査している間に、別のエージェントが次工程へ進む可能性も考える必要があります。

▼　本件はこの文献を参考にしました  
[Anthropic「Detecting and countering misuse of AI: September 2026」](https://www.anthropic.com/threat-intelligence-report-september-2026?page=1)

## 被害拡大の背景は「AIが賢いこと」より「人間の待ち時間が消えること」

AI時代の本質は、攻撃方法がすべて未知のものへ置き換わることではありません。既存の偵察、解析、実行、結果確認、修正という工程の間にあった人間の待ち時間が減り、一人の攻撃者がより多くの対象を処理できる点にあります。

### 実行・分析・修正のループをAIが連続して回せる

従来の自動化ツールでも高速スキャンは可能でしたが、想定外のエラーや環境差への対応では人間の判断が必要でした。AIエージェントは、実行結果やエラーメッセージを読み、次の手法を選択し、コマンドやコードを修正して再試行する役割まで担当できます。

Googleは、AIエージェントによってHuman-in-the-loopの待ち時間が大きく縮まり、防御側が対応できる時間が圧縮されると説明しています。これが従来のスクリプト型自動化との大きな違いです。同じ攻撃手法であっても、状況に応じて次の手を選ぶ部分まで自動化されれば攻撃全体の速度が上がります。

したがってAI攻撃を考える際のキーワードは「新しい魔法のExploit」だけではなく、Orchestration、つまり複数の攻撃工程を一つの目標へ向けてつなぐ能力です。

▼　本件はこの文献を参考にしました  
[Google Threat Intelligence Group「From Prompting to Autonomy – The Evolution of Adversarial AI」](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai)

### 攻撃元IPやPayloadを変えながら多数の標的へ展開できる

AIエージェント型攻撃では、送信元IPやPayloadが固定されるとは限りません。Googleが確認した事例ではIPローテーションまで自動化され、しかも侵害済みのクラウド資源が攻撃基盤に利用されました。

そのため「この悪性IPを遮断したから終わり」とは限りません。別のIPへ切り替えたり、HTTPリクエストの形を変更したり、認証情報を取得した後は正規ログインへ移行したりできます。固定されたIOCだけを追う防御は、攻撃側が変化する速度に追いつきにくくなります。

一方で、IPアドレスやシグネチャ対策が無意味になるわけではありません。既知の攻撃を低コストで止める重要な層です。問題は、それだけを最後の防波堤と考えず、端末、ID、クラウド、データへのアクセスを含む行動ベースの監視と組み合わせることです。

▼　本件はこの文献を参考にしました  
[Google Threat Intelligence Group「From Prompting to Autonomy – The Evolution of Adversarial AI」](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai)

### 攻撃コストが下がると中小企業も「採算の合う標的」になる

AIによって公開資産の調査、製品バージョンの推定、脆弱性情報の収集、攻撃候補の絞り込みを並列化できれば、攻撃者は多数の組織を安価にふるいへ掛けられます。人間が100社を一社ずつ詳しく調べる必要がなくなるからです。

NCSCは、AIによって既存の攻撃手法が効率化され、国家系だけでなく幅広い攻撃者へ能力が拡散する可能性を指摘しています。高度な攻撃者が持っていた知識をAIが完全に代替するわけではありませんが、調査やコード作成を補助することで参入障壁を下げる方向には働きます。

その結果、「当社は有名ではないから標的にならない」という前提はさらに危険になります。攻撃者が多数企業を自動調査し、脆弱だった企業や盗める情報が見つかった企業だけに人間の時間を投入できるなら、小規模組織も十分に攻撃対象になり得ます。

▼　本件はこの文献を参考にしました  
[UK NCSC「Impact of AI on cyber threat from now to 2027」](https://www.ncsc.gov.uk/report/impact-ai-cyber-threat-now-2027)

## SOC・CSIRTからAI攻撃はどう見えるのか

企業側のログに「GLM-5.3が攻撃しました」と記録されるわけではありません。AIの判断は攻撃者側で完結し、標的側には通常の通信やプロセス実行として現れます。そこでSOCはAI判定ではなく、複数ログに残る攻撃行動の連鎖を追います。

### FirewallとWAFでは「送信元」より対象資産の変化を見る

Firewallでは送信元・宛先IP、ポート、通信量、接続頻度を確認します。ただしAIエージェントが複数IPを使う場合、単一の送信元だけを集計すると一連の攻撃を別事件として扱う恐れがあります。同じ公開サーバーへ短時間に複数送信元から探索が続くなど、宛先資産を軸にした相関が重要です。

WAFではRequest URI、HTTP Method、Status Code、Rule ID、User-Agent、検知したPayloadなどを確認します。特に注目したいのは、404や403を受けた直後にパス、パラメータ、HTTP Method、Payloadが変化し、その後200や500へ遷移するといった試行錯誤です。

この動きだけでAI攻撃と断定はできません。人間や既存の高度なスキャナでも起こります。ただし、複数IPをまたぎながら短時間に探索と適応が繰り返される場合、後続するEDRや認証ログと組み合わせる価値が高いシグナルになります。

▼　本件はこの文献を参考にしました  
[Google Threat Intelligence Group「From Prompting to Autonomy – The Evolution of Adversarial AI」](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai)

### EDR/XDRでは未知のExploitでも「侵入後の手足」が見える

AIが新しいExploitを生成した場合、既知ファイルのハッシュやシグネチャでは最初の攻撃を捉えられない可能性があります。それでも侵入に成功した後は、OS上で何らかの処理を実行しなければなりません。

例えばWebサーバーのプロセスからcmd.exe、PowerShell、bash、Pythonなどのシェルが突然起動する、通常アクセスしない認証情報へプロセスが接触する、短時間に端末・ネットワーク・ユーザー情報を列挙する、といった挙動は重要な手掛かりです。

AIの「思考」は標的企業から見えなくても、AIが動かすツールの「手足」はプロセス生成、ファイルアクセス、ネットワーク接続として残ります。未知のExploitを想定するほど、既知マルウェア判定だけでなく振る舞いを追うEDR/XDRの価値が上がります。

▼　本件はこの文献を参考にしました  
[MITRE ATT&CK「Anthropic AI-orchestrated Campaign, C0062」](https://attack.mitre.org/campaigns/C0062/)

### Entra IDやActive Directoryでは「普段と違う正規利用」を追う

認証情報を盗まれた後は、攻撃者が正しいIDとパスワード、トークンを使うため、Firewallだけでは不正を判断しにくくなります。この段階ではIPそのものより、ユーザーの通常行動との差を見る必要があります。

Entra IDなどの認証基盤では、普段と異なるASN、端末、場所、アプリケーション、Token、短時間の認証失敗と成功の組み合わせが手掛かりになります。Active Directory側では、LDAPを使ったユーザー、グループ、管理者、端末、ドメイン、信頼関係の列挙などに注意します。

AIが内部ネットワークを理解して次の攻撃先を選ぶには、組織の構成を調べる必要があります。したがってDiscoveryの工程そのものが検知機会になります。正規認証だから安全と考えず、「そのIDがなぜ今その情報を調べているのか」という行動文脈を評価することが重要です。

▼　本件はこの文献を参考にしました  
[MITRE ATT&CK「Anthropic AI-orchestrated Campaign, C0062」](https://attack.mitre.org/campaigns/C0062/)

### Proxy・DNS・クラウド監査ログは攻撃チェーン後半を補強する

Proxyでは、通常利用しないWebサービスやクラウドストレージへの大容量アップロード、通常は通信しないプロセスからの外部接続などを確認します。DNSでは新規・低頻度ドメインへの問い合わせや、短時間に多数の外部ドメインへ切り替わる挙動が補助的な手掛かりになります。

クラウド環境ではさらにControl Planeの監査ログが重要です。侵害されたIDがVM、Storage、Secret、Role、Functionなどを短時間に列挙すれば、ネットワーク通信だけでは見えにくい内部探索を把握できます。AWS CloudTrail、Azure Activity Log、Google Cloud Audit LogsなどをSIEMへ集約する理由です。

単独のDNS問い合わせやAPI呼び出しは正常業務でも発生します。しかし、その直前にEDRで不審なシェル実行や認証情報探索があり、直後に大量データ送信が続けば、一つの攻撃チェーンとして意味を持ちます。

▼　本件はこの文献を参考にしました  
[MITRE ATT&CK「Anthropic AI-orchestrated Campaign, C0062」](https://attack.mitre.org/campaigns/C0062/)

### SIEMでは「速度・順序・対象」をつないで見る

AIエージェント型攻撃への対策で最も重要なのは、個別製品のアラートを別々に処理しないことです。WAFで探索が検知され、その直後にWebサーバーから不審なシェルが起動し、AD列挙、別サーバーへの認証、大量ファイルアクセス、外部送信へ進んだ場合、それぞれを一つの事件として相関させます。

攻撃側はAIによって偵察から窃取までを一つのコンテキストとして扱えるようになっています。それに対し、防御側がFirewall担当、EDR担当、ID担当、クラウド担当に分断され、各自が単独アラートだけを見ていれば、工程間の速度についていけません。

SOCでは特定IPやファイルだけをIOCとして追うことに加えて、「同一端末・同一ID・同一資産を中心に複数のATT&CK技術が短時間で連続した」というIOB、つまり行動指標を重視する必要があります。

▼　本件はこの文献を参考にしました  
[MITRE ATT&CK「Anthropic AI-orchestrated Campaign, C0062」](https://attack.mitre.org/campaigns/C0062/)  
[Google Threat Intelligence Group「From Prompting to Autonomy – The Evolution of Adversarial AI」](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai)

## AI時代に企業が取るべき対策

AI攻撃専用の万能製品を導入すれば解決するわけではありません。むしろ、公開資産、脆弱性、Identity、端末、クラウド、データという既存の守備範囲をつなぎ、検知から封じ込めまでの時間を短くすることが現実的な対策になります。

### インターネット公開資産と重大脆弱性を継続的に把握する

N-day攻撃への第一歩は、自社が外部へ何を公開しているかを把握することです。VPN、Firewall、Webサーバー、API、管理画面、検証環境など、担当者が存在を忘れている資産はパッチ管理の対象からも漏れやすくなります。

Googleの2026年分析では、実悪用された脆弱性のうちEdge／Security Applianceが14％を占めました。外部公開された管理インターフェースなどは、EDRを導入しにくい境界機器でもあり、攻撃者にとって魅力的な初期侵入経路になります。

すべてのCVEを同じ速度で処理するのではなく、インターネット公開の有無、実悪用状況、認証不要か、奪取できる権限、重要システムへの接続性を組み合わせて優先順位を決めます。AIで攻撃準備が速くなるほど、重大案件を数時間から数日で判断できる運用が重要です。

▼　本件はこの文献を参考にしました  
[Google Threat Intelligence Group「Vulnerability Discovery and Exploitation Trends in the AI Era」](https://cloud.google.com/blog/topics/threat-intelligence/vulnerability-discovery-and-exploitation-trends-in-the-ai-era)  
[UK NCSC「Impact of AI on cyber threat from now to 2027」](https://www.ncsc.gov.uk/report/impact-ai-cyber-threat-now-2027)

### 認証情報を盗まれても横展開できない構成にする

AIが攻撃を高速化しても、権限が細かく分離されていれば一度の侵入で全社へ到達することは難しくなります。フィッシング耐性の高い多要素認証、特権アカウントの分離、不要な権限の削除、APIキーやサービスアカウントの棚卸しが重要です。

さらに管理ネットワーク、一般端末、サーバー、バックアップなどの到達範囲を必要最小限にします。一つのユーザー資格情報を取得しただけで重要DBやバックアップまで到達できる設計は、AIエージェントにとって効率のよい環境になってしまいます。

防御側が目指すのは「絶対に侵入されないこと」だけではありません。侵入されても次の工程へ進むたびに別の認証、権限、監視を通過させ、攻撃チェーンを途中で切ることです。

▼　本件はこの文献を参考にしました  
[MITRE ATT&CK「Anthropic AI-orchestrated Campaign, C0062」](https://attack.mitre.org/campaigns/C0062/)

### EDR/XDRとSIEMで検知から封じ込めまでを短縮する

AI時代ではMTTD、つまり検知までの時間だけでなく、検知後に端末やアカウントを封じ込めるまでの時間が重要になります。攻撃者側で工程間の待ち時間が消えるなら、防御側が人手によるチケット回覧や会議だけに依存するほど不利になるからです。

高確度なマルウェア実行、明確な認証情報窃取、侵害済み端末からの異常な横展開などでは、自動隔離や認証セッション失効を検討できます。一方、誤検知で業務を止めるリスクが高いケースでは、AIが関連ログや証拠を整理し、人間が承認して封じ込める形が現実的です。

重要なのは「AIを検知する製品」を探すことではなく、WAF、EDR、Identity、Cloud、Proxy、DNSを横断した攻撃シナリオを作り、検知・調査・隔離までの時間を継続的に測ることです。

▼　本件はこの文献を参考にしました  
[Google Threat Intelligence Group「From Prompting to Autonomy – The Evolution of Adversarial AI」](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai)

### 防御側もAIを使い、攻撃側の速度に対抗する

大量のセキュリティログを人間だけでリアルタイムに読み切ることは難しくなっています。防御側もAIを利用して、アラートの要約、関連イベント検索、攻撃経路の仮説作成、影響範囲の整理、脆弱性の優先順位付けを高速化する必要があります。

ただし、自動化の範囲には設計が必要です。AIへ端末隔離やアカウント停止など強い権限を無条件に与えると、誤判断による業務停止リスクが生まれます。最初は調査支援から始め、十分に確度の高いシナリオだけ自動封じ込めへ移す段階的な設計が現実的です。

AI時代の構図は「AI対人間」ではありません。AIを使って攻撃速度を上げる攻撃者に対し、防御側もAIと自動化を使って判断と封じ込めを高速化する競争です。

▼　本件はこの文献を参考にしました  
[UK NCSC「Impact of AI on cyber threat from now to 2027」](https://www.ncsc.gov.uk/report/impact-ai-cyber-threat-now-2027)  
[Google Threat Intelligence Group「From Prompting to Autonomy – The Evolution of Adversarial AI」](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai)

## まとめ

2026年秋の国内事案でGLM-5.3などAIの利用が確認されたわけではありません。一方、NIST、Anthropic、Google、MITREの情報からは、AIがExploit作成だけでなく、偵察、脆弱性探索、認証情報収集、内部探索まで攻撃工程をつなぐ方向へ進んでいることが分かります。AIの判断そのものを標的側から識別するのは難しくても、通信、認証、プロセス、横展開、データ持ち出しという行動はログに残ります。企業側に必要なのは、AI専用の検知より、公開資産と脆弱性を早く把握し、WAF、EDR、Identity、クラウドなどのログを相関させ、検知から封じ込めまでの時間を短縮することです。