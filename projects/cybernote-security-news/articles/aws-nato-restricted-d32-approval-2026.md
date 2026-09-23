---
answer: AWSはNATO RESTRICTED向けクラウド機能の全加盟国向け承認を得たと発表。個別システムの認定は別途必要です。
cve: ''
faq:
- q: AWSはNATOに承認されたのですか？
  a: AWSは、NATO全加盟国でNATO RESTRICTED級の情報を扱うクラウド機能の承認を得たと発表しました。承認されたのはクラウド機能であり、NATOがAWSを全面的に採用したという意味ではありません。
- q: AWSはNATOで何を扱えるようになったのですか？
  a: NATO加盟国内のAWSリージョンで、承認済みサービスを使いNATO RESTRICTED対応システムを構築できるようになりました。実際の運用には、各国またはNCIAによる認定が必要です。
- q: NATO RESTRICTEDとは何ですか？
  a: NATOの4段階の秘密区分のうち最も低い区分です。漏えいがNATOの利益に不利となる情報が対象で、最高機密ではありませんが、一般公開もできない情報です。
- q: AWSだけがNATOで使えるのですか？
  a: いいえ。AWSは全加盟国向け承認の初の事業者と発表していますが、GoogleやOracleもNATOの機関で採用されています。他社のクラウドがNATOで使えないという意味ではありません。
- q: NATO D32とは何ですか？
  a: パブリッククラウドでNATOの非機密情報とRESTRICTED情報を守るための技術・実装指令です。全文は一般公開されていません。
- q: 今回の承認で何が変わるのですか？
  a: 各加盟国がAWSをゼロから評価せず、共通の事前評価済みベースラインを出発点に自国の認定を進められるようになります。AWSは、時間や費用の削減につながると説明しています。
- q: NATOの機密情報をAWSに保存できるのですか？
  a: 対象はNATO RESTRICTEDまでです。NATO CONFIDENTIAL以上の区分は含まれず、システムごとの認定も別途必要になります。
- q: AzureやGoogle Cloudはどうなのですか？
  a: Microsoftは、Azure向けにD32準拠を確認するポリシーを開発中と公表しています。GoogleはNCIAとエアギャップ型クラウドの契約を結んでいます。ただし、全加盟国向けのNATO RESTRICTED承認を公表した例は確認できません。
sources:
- title: AWS becomes first cloud provider approved for NATO RESTRICTED workloads across all member nations（Amazon）
  url: https://www.aboutamazon.com/news/aws/aws-first-cloud-provider-nato-restricted-workloads
  publisher: Amazon
- title: Guidance for Trusted Secure Enclaves on AWS（AWS）
  url: https://docs.aws.amazon.com/solutions/trusted-secure-enclaves-on-aws/
  publisher: AWS
- title: 'CUI Category: NATO Restricted（米国立公文書館）'
  url: https://www.archives.gov/cui/registry/category-detail/nato-restricted.html
  publisher: 米国立公文書館
- title: NATO Security Awareness Briefing（米国防総省 CDSE）
  url: https://www.cdse.edu/Portals/124/Documents/jobaids/industrial/NATOSecurityAwarenessBriefing.pdf
  publisher: 米国防総省 CDSE
- title: Cloud Security Control Requirements（英国防省 Industry Security Notice 2024/06）
  url: https://assets.publishing.service.gov.uk/media/666171587b792ffff71a87ba/Cloud_Security_Control_Requirements.pdf
  publisher: 英国防省 Industry Security Notice 2024/06
- title: CCN-STIC-004 Manejo de información con clasificación Difusión Limitada en nube pública（スペイン国立暗号センター）
  url: https://www.ccn-cert.cni.es/es/guias-de-acceso-publico-ccn-stic/7358-ccn-stic-004-manejo-de-informacion-con-clasificacion-difusion-limitada-o-equivalente-en-nube-publica/file.html
  publisher: スペイン国立暗号センター
- title: Amazon Web Services podrá procesar información restringida de la OTAN desde sus centros de datos de Aragón（elEconomista）
  url: https://www.eleconomista.es/tecnologia/noticias/14015829/09/26/amazon-web-services-podra-procesar-informacion-restringida-de-la-otan-desde-sus-centros-de-datos-de-aragon.html
  publisher: elEconomista
- title: Accelerate cloud adoption with Microsoft Cloud for Sovereignty（Microsoft）
  url: https://www.microsoft.com/en-us/microsoft-cloud/blog/government/2024/10/29/accelerate-cloud-adoption-with-microsoft-cloud-for-sovereignty/
  publisher: Microsoft
- title: NATO and Google Cloud Sign Multi-Million Dollar Deal for AI-Enabled Sovereign Cloud（Google Cloud）
  url: https://www.googlecloudpresscorner.com/2025-11-24-NATO-and-Google-Cloud-Sign-Multi-Million-Dollar-Deal-for-AI-Enabled-Sovereign-Cloud
  publisher: Google Cloud
- title: The NATO Communications and Information Agency Selects Oracle Cloud Infrastructure（Oracle）
  url: https://www.oracle.com/news/announcement/nato-communications-and-information-agency-selects-oci-2025-09-11/
  publisher: Oracle
- title: evroc builds Combat Cloud together with the Swedish Armed Forces（evroc）
  url: https://evroc.com/news/evroc-builds-combat-cloud-together-with-the-swedish-armed-forces/
  publisher: evroc
- title: Secure Cloud Services RFP Amendment 1（NATO変革連合軍 ACT）
  url: https://www.act.nato.int/wp-content/uploads/2026/07/rfp026054_amdt1.pdf
  publisher: NATO変革連合軍 ACT
- title: AWS launches AWS European Sovereign Cloud and announces expansion across Europe（Amazon）
  url: https://press.aboutamazon.com/aws/2026/1/aws-launches-aws-european-sovereign-cloud-and-announces-expansion-across-europe
  publisher: Amazon
---

# AWSはNATOから何を承認されたのか？NATO RESTRICTEDとD32をわかりやすく解説

AWSがNATO（北大西洋条約機構）から承認を得たというニュースを見て、NATOの軍事機密がAWSに保存されるようになったのかと驚いた方もいるのではないでしょうか。Amazon Web Servicesは米国時間2026年9月22日、NATO全加盟国でNATO RESTRICTEDレベルの情報を扱うクラウド機能について、承認を得た初のクラウド事業者になったと発表しました。ただし、NATO RESTRICTEDはNATOの秘密区分のうち最も低いレベルで、最高機密ではありません。本記事では、何が承認され何が対象外なのか、NATO D32の仕組み、AWSだけなのかという疑問までを整理します。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ AWS公式発表</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.aboutamazon.com/news/aws/aws-first-cloud-provider-nato-restricted-workloads"} /--></div>
<!-- /wp:group -->

## AWSのNATO RESTRICTED承認とは

結論から言うと、今回承認されたのはAWSのクラウド機能であり、NATO RESTRICTED級の情報を扱うシステムの土台として使えるという評価です。ここではまず発表の内容を確認し、そのうえで承認が及ぶ範囲を整理します。

### AWSが発表した内容

AWSの発表によると、NATO、NATOの防衛産業パートナー、全加盟国は、NATO加盟国内にあるAWSリージョンで承認済みのサービスを使い、NATO RESTRICTED対応のシステムを構築できるようになりました。AWSはNATO加盟国内に15のリージョンを持ち、うち7つが欧州大陸にあるとしています。発表の中でNATO通信情報局（NCIA）のディラン・ブラウン総局長は、NATOの要件を満たす商用製品が増えることで、同盟が使える技術の選択肢が広がるという趣旨のコメントを寄せています。

### 承認されたもの・されていないもの

今回のニュースは見出しだけを読むと、AWSがNATOのあらゆる情報を扱えるようになったかのように受け取られがちです。しかし公式発表を読むと、承認の対象は情報区分、サービス、リージョンのいずれも限定されています。発表で明示された内容と、そこに含まれない内容や確認できない点を分けて整理すると次のとおりです。

| 項目 | 承認・発表された内容 | 含まれない・確認できない内容 |
|---|---|---|
| 情報区分 | NATO RESTRICTED | NATO CONFIDENTIAL以上の区分 |
| 対象 | 承認済みのAWSサービス（クラウド機能） | 利用者がAWS上に構築した個別のシステム |
| 場所 | NATO加盟国内のAWSリージョン | 加盟国外のリージョン、対象リージョンの一覧 |
| 手続き | NATOが評価結果を全加盟国に公表 | 各国やNCIAによる個別システムの認定 |

つまり今回の承認は、AWSをNATO RESTRICTED級のシステムの土台として使ってよいという評価であり、AWS上に作ったシステムがそのまま運用を許可されるわけではありません。実際に情報を扱うには、各加盟国またはNCIAによる認定という次の段階が必要です。この二段階の仕組みについては、後半で詳しく説明します。

## NATO RESTRICTEDとはどんな情報か

NATO RESTRICTEDとは、NATOに4段階ある秘密区分のうち、最も低いレベルの情報区分です。漏えいするとNATOの利益に不利となる情報が対象で、軍事上の最高機密を指す言葉ではない点に注意が必要です。

### NATOの4段階の情報区分

NATOでは、情報が漏えいした場合の影響の大きさに応じて、4段階の秘密区分が定められています。米国の国防関係機関が公開している研修資料では、各区分は次のように説明されています。表の上にある区分ほど機密度が高く、今回の承認の対象は最も下にある4番目の区分です。参考として、秘密区分に含まれない情報もあわせて示します。

| 区分 | 漏えいした場合の影響 |
|---|---|
| COSMIC TOP SECRET | NATOに極めて重大な損害を与える |
| NATO SECRET | NATOに重大な損害を与える |
| NATO CONFIDENTIAL | NATOの利益を害する |
| NATO RESTRICTED | NATOの利益に不利となる |
| （参考）NATO UNCLASSIFIED | 秘密区分には当たらないNATOの公的な情報 |

この表からわかるとおり、NATO RESTRICTEDは秘密区分の中で最も低いレベルに位置づけられています。一方で、自由に公開してよい情報ではなく、正式な秘密区分の一つとして保護が求められます。最高機密ではないものの一般公開もできない、その中間にある情報と理解するとイメージしやすいでしょう。見出しの印象だけで判断しないことが大切です。

### 最高機密ではないが非公開の情報

米国立公文書館の分類では、NATO RESTRICTEDは北大西洋条約上の4番目の秘密区分とされ、保護措置と公開からの保護が必要な情報と位置づけられています。米国の研修資料によれば、保護の水準は米国の管理対象非機密情報（CUI）に近い一方、送信には秘密扱いの経路を使う必要があります。また米国では、この区分の情報に触れるのにセキュリティクリアランスは不要とされています。海外報道にはこの区分を秘密情報ではないと表現する例もありますが、正確には秘密区分の中で最も低いレベルです。

## 承認の仕組み：NATO D32・CCN・NCIAの役割

今回の承認は、NATO D32と呼ばれる技術指令への適合性を、スペインの国立暗号センター（CCN）が評価する形で進められました。ここでは関係する機関の役割と、実際の運用に至るまでの流れを順に整理します。

### NATO D32とは

NATO D32は、パブリッククラウドでNATOの情報を扱う際のセキュリティ要件を定めた技術指令です。英国防省の文書によると、D32の正式名称は、パブリッククラウド型の通信情報システムにおけるNATO情報保護のための技術・実装指令です。そして、NATO UNCLASSIFIEDとNATO RESTRICTEDの情報をクラウドに保存する場合に準拠を求めています。全文は一般公開されておらず、具体的な要件項目は公開情報からは確認できません。AWSはD32への適合性を文書化し、評価を受けました。

### スペインのCCNが評価を担当

CCNはスペインの国家情報センター（CNI）に属する機関で、同国の情報セキュリティ基準の策定や製品評価を担っています。AWSの発表によると、CCNがAWSのクラウド機能を評価し、その結果をNATOが承認して全加盟国に公表しました。スペイン国内では並行して、CCNと国家安全保障局（ONS）が、AWSのスペインリージョンに同国独自の区分とNATO RESTRICTEDの認定を与えたと現地メディアが報じています。

### NCIAと各国による最終認定

NCIAはNATOの技術・サイバー分野の中核機関で、同盟の通信網の構築や防衛を担っています。AWSの発表では、NATO RESTRICTED級のシステムの認定は、NATOが加盟国やNCIAに委任するとされています。つまりNATO全体で共有されるのはクラウドの評価結果であり、個別のシステムを運用してよいかは各国の正式な手続きで判断されます。AWSは今回の承認により、加盟国が自国の手続きでAWSを認定する道のりが短くなると説明しています。

### 土台となるTSE-SE

AWSは今回の発表の基盤として、Trusted Secure Enclave – Sensitive Edition（TSE-SE）を挙げています。TSE-SEは、国家安全保障や防衛などの機微な業務向けに、複数のAWSアカウントを組み合わせて構成する参照アーキテクチャです。アクセス管理の一元化、暗号化、ログの集中管理、ネットワークの分離などを、利用者側で設計・設定することが前提になっています。承認済みのサービスを使えば自動的に安全になるわけではありません。

## AWSだけなのか？各社の対応状況

AWSは、全加盟国を対象にNATO RESTRICTEDの承認を得た初のクラウド事業者だと発表しています。ただし、これはAWS以外のクラウドがNATOで使えないという意味ではありません。ここでは初と唯一の違いと、他社の状況を確認します。

### 初と唯一は意味が違う

初という表現はAWS自身の発表に基づくもので、NATOやNCIAによる独自の発表は2026年9月23日時点で確認できません。同様の承認を公表した他社は見当たらないものの、NATOの承認リストは公開されていないため、唯一と断定することもできません。また、承認はクラウド機能への評価、認定は個別システムの運用許可、準拠は要件を満たすための取り組みを指し、それぞれ段階が異なります。報道を読む際は、どの段階の話なのかを区別することが大切です。

### Microsoft・Google・Oracle・evrocの状況

ほかの主要なクラウド事業者も、NATOや加盟国の防衛分野で取り組みを進めています。ただし、その多くは今回のAWSのような全加盟国向けの承認ではなく、特定の機関との契約や、要件への準拠を支援するツールの提供です。2026年9月23日時点の公開情報で確認できる範囲を、段階ごとに整理すると次のとおりです。

| 事業者 | NATO関連の主な動き | 段階 |
|---|---|---|
| Microsoft | Azure向けにD32準拠を確認するポリシーを開発。NATO UNCLASSIFIED向けはプレビュー、RESTRICTED向けは作成中と公表 | 準拠支援 |
| Google | 2025年11月、NCIAがエアギャップ型のGoogle Distributed Cloudを採用。秘密区分の業務に利用 | 契約 |
| Oracle | 2025年9月、NCIAが基幹業務をOCIのソブリンクラウドへ移行すると発表 | 契約 |
| evroc（スウェーデン） | スウェーデン軍の指揮統制システム向けに、NATO RESTRICTEDの認定取得を想定した基盤を構築中 | 対応予定 |

このように、GoogleやOracleはすでにNATOの機関で採用されており、NATOが複数の事業者を用途に応じて使い分けていることがわかります。ただし、全加盟国を対象にしたNATO RESTRICTEDの承認を公表した例は、AWS以外に確認できません。他社が今後同様の承認を得る可能性もあるため、最新の発表も確認しましょう。

## 承認されてもAWSに何でも置けるわけではない

今回の承認を、NATOの軍事機密をAWSに保存できるようになったと受け取るのは誤りです。対象となる情報区分、リージョン、利用者側の手続きのそれぞれに条件があるため、ここで一つずつ順に確認していきます。

### 対象はNATO RESTRICTEDまで

今回発表されたのはNATO RESTRICTED級の承認であり、NATO CONFIDENTIAL以上の区分は含まれていません。上位の区分については、NATO変革連合軍（ACT）が2026年、NATO SECRET級までを扱うクラウドの試作を調達しています。この調達では、外部から物理的に切り離したエアギャップ型と、機密計算技術で商用クラウドを暗号的に分離する方式の2種類が検討されています。上位区分では、今回とは別の方式が前提になっていると言えます。

### リージョンによっては対象外

承認の対象は、NATO加盟国内にあるAWSリージョンです。AWSは15リージョンと説明していますが、具体的な一覧は公表されていません。注意したいのは、アイルランドとスイスはNATO加盟国ではないため、両国にあるリージョンは発表の文言上は対象外となる点です。2026年1月に提供が始まったAWS European Sovereign Cloudが15リージョンに含まれるかどうかも、現時点では確認できません。

### 最終判断は各国の認定

前述のとおり、NATO RESTRICTEDの情報を扱うシステムを実際に運用するには、各加盟国またはNCIAによる認定が必要です。承認済みのAWSサービスを使っても、アクセス権限の設定ミスや暗号化の不備があれば、システムとしての要件は満たせません。クラウド事業者と利用者の責任範囲を分ける責任共有モデルの考え方は、NATOの世界でも変わらないのです。

## 企業のIT担当者が学べること

今回のニュースは国家の防衛分野に関する話題ですが、一般企業のクラウド活用にも通じる考え方を含んでいます。ここでは、セキュリティ評価の再利用と、データ分類から始めるクラウド選定という2つの観点を紹介します。

### 一度の評価を共通で使う発想

AWSは、加盟国やパートナーが共通の事前評価済みセキュリティベースラインを引き継げるため、対応にかかる時間や費用を減らせると説明しています。日本のISMAP（政府情報システムのためのセキュリティ評価制度）も、事前に評価したクラウドを各機関が共通に使う制度で、発想は近いと言えます。ただし制度の仕組みは別物です。企業でも、部署ごとに同じクラウドを毎回ゼロから審査するより、全社共通の評価を作って再利用するほうが効率的です。

### データ分類から始めるクラウド選定

NATOの仕組みは、まず情報を機密度で分類し、区分ごとに必要な要件を決めたうえで、それを満たすクラウドを選ぶという順序で組み立てられています。この順序は、企業が自社の機密情報をクラウドに置くかどうかを判断する際にも十分に応用できます。具体的には、次の4つの手順で整理していくと判断しやすくなるでしょう。

1. 社内の情報を公開・社外秘・極秘などの機密度で分類する
2. 区分ごとに、暗号化やアクセス管理、保存場所などの要件を定める
3. 候補となるクラウドサービスの認証や第三者評価を、要件と照らし合わせる
4. クラウド事業者の評価で足りない部分を、自社の設定や運用で補う

重要なのは、すべての情報を一律にオンプレミスに置くか、一律にクラウドへ移すかという二択で考えないことです。情報の区分に応じて置き場所と対策を変えれば、利便性と安全性を両立しやすくなります。クラウド事業者の認証はあくまで出発点であり、自社システムの安全性を保証するものではない点も押さえておきましょう。

## 業界への示唆：機密度に応じてクラウドを使い分ける時代へ

ここからは、一次情報をもとにしたCyberNote筆者の考察です。今回の承認は、国家安全保障の分野でも、情報の機密度に応じてクラウドの形を使い分ける流れが具体化してきたことを示していると筆者は考えます。

### 秘密区分ごとにクラウドの形が分かれ始めている

筆者が注目するのは、AWSが安全と評価されたこと以上に、NATOの秘密区分で最も低いRESTRICTEDについて、1回の評価結果を全加盟国で使い回せる仕組みが商用パブリッククラウドに適用された点です。一方、秘密区分の業務にはGoogleのエアギャップ型が採用され、NATO SECRET級では別方式の試作が進んでいます。重要情報は一律にオンプレミスという考え方から、区分ごとに要件を定めて適したクラウドを選ぶ考え方へ、段階的に移りつつあると言えるでしょう。

### ソブリンクラウドやデータ主権との関係

欧州では、データの保存場所や運用主体を自国・自地域の管理下に置くデータ主権への関心が高まっています。AWSも2026年1月、EU域内で独立して運用するソブリンクラウドであるAWS European Sovereign Cloudの提供を始めました。今回の承認はこれとは別の取り組みですが、クラウドの利便性と国家の管理をどう両立させるかという同じ論点の上にあります。evrocのように欧州の事業者が防衛向けのクラウドを打ち出す動きもあり、選択肢は今後さらに広がると考えられます。


関連記事として、[AWSのクラウドセキュリティ解説](https://www.cybernote.click/2026/07/02/aws%E3%81%8C%E9%80%B2%E3%82%81%E3%82%8B%E3%82%AF%E3%83%A9%E3%82%A6%E3%83%89%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3%E3%81%AE%E5%8A%B9%E7%8E%87%E5%8C%96%E3%81%A8%E3%81%AF%EF%BC%9F2025/)、[セキュリティ対策評価制度のチェックリスト](https://www.cybernote.click/2026/09/11/scs-security-evaluation-checklist/)、[同制度の最新動向と第三者評価](https://www.cybernote.click/2026/09/14/scs-security-assessment-2026/)も紹介しています。

## まとめ

AWSは、NATO全加盟国でNATO RESTRICTED級の情報を扱うクラウド機能の承認を得た初の事業者になったと発表しました。NATO RESTRICTEDは秘密区分のうち最も低いレベルで、最高機密ではありません。また、承認されたのはクラウド機能であり、実際のシステム運用には各国やNCIAによる認定が別途必要です。AWS以外のクラウドがNATOで使えないわけでもありません。今回の本質は、1回の評価を加盟国全体で共有する仕組みが商用クラウドに適用された点にあります。企業にとっても、データ分類から始めて評価を再利用する考え方は参考になるでしょう。