---
answer: 日立のWebサーバー製品に4件の脆弱性があり、対象版の確認と対策版への更新が必要です。
cve: CVE-2026-49975, CVE-2026-48913, CVE-2026-43951, CVE-2026-33523
faq:
  - q: Cosminexus HTTP Serverのどの環境が影響を受けますか？
    a: CVEごとに対象版が異なります。Linux、Windows、AIXなどの稼働版とHTTP/2の利用状況を、日立の4件の公式情報で照合してください。
  - q: HTTP/2を無効にすれば更新は不要ですか？
    a: HTTP/2無効化で回避できるのはCVE-2026-49975とCVE-2026-48913です。残る2件には当てはまらないため、対策版への更新が基本です。
  - q: Hitachi Web Serverはどのように対応すればよいですか？
    a: 対策版の発行予定がない対象版があります。利用組織はサポート窓口へ相談し、移行、公開制限、代替製品を含む対応計画を決めてください。
sources:
  - title: Cosminexus HTTP ServerにおけるCVE-2026-49975
    url: https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-128/index.html
    publisher: 日立製作所
  - title: Cosminexus HTTP ServerにおけるCVE-2026-48913
    url: https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-127/index.html
    publisher: 日立製作所
  - title: Cosminexus HTTP ServerおよびHitachi Web ServerにおけるCVE-2026-43951
    url: https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-126/index.html
    publisher: 日立製作所
  - title: JVN iPedia JVNDB-2026-026849
    url: https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-026849.html
    publisher: IPA
---

# 【重要】日立Cosminexus HTTP Serverに4件の脆弱性、対象版と更新方法を確認

日立製作所は2026年8月4日、Cosminexus HTTP ServerとHitachi Web Serverに関する4件の脆弱性情報を公開しました。最も高いCVSS基本値は7.5で、認証されていない攻撃者からネットワーク経由で悪用される可能性があります。影響はサービス停止、情報漏えい、データ改ざんなどで、CVEごとに対象製品や条件が異なります。日立はCosminexus HTTP Serverの対策版を案内する一方、Hitachi Web Serverには対策版の発行予定がない対象版も示しています。利用組織は製品名、OS、版数、HTTP/2の利用状況を照合し、更新または移行計画を確認してください。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 参照</p>
<!-- /wp:paragraph -->

<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/08/05/apache-tomcat-cve-2026-34486-encryptinterceptor-kev/"} /--></div>
<!-- /wp:group -->

## 4件の脆弱性の概要

今回の公表は単一の不具合ではなく、可用性だけに影響する問題と、機密性・完全性にも影響する問題を含みます。すべてを同じ条件で扱わず、CVE番号と稼働環境を対応付けて判断することが重要です。対象外と判断する場合も根拠を記録してください。

### CVE-2026-49975とCVE-2026-48913

CVE-2026-49975はCVSS基本値7.5で、認証不要のネットワーク攻撃によりサービス停止へつながる可能性があります。日立の環境評価は5.3です。CVE-2026-48913は基本値7.3、環境値5.6で、情報の参照・変更とサービス停止が想定されています。いずれもHTTP/2プロトコル通信機能を使用していない場合は発生しないと日立が説明しています。ただし、設定変更だけで恒久対応を終えたと判断せず、対策版を適用できるか確認してください。

### CVE-2026-43951とCVE-2026-33523

CVE-2026-43951とCVE-2026-33523のCVSS基本値はいずれも6.5で、認証されていない攻撃者がネットワーク経由で情報の参照や変更を行う可能性があります。前者について日立は攻撃条件の複雑さを環境評価で高いとしていますが、対象から外れる意味ではありません。この2件はCosminexus HTTP ServerだけでなくHitachi Web Serverも対象です。HTTP/2を無効化しても回避できるとは案内されていないため、別の2件と混同しないことが大切です。

## 影響を受ける製品と版

対象範囲はCVEごとに異なり、Cosminexus HTTP Serverを構成製品として含むuCosminexus Application Serverなどにも影響が及びます。製品台帳だけでなく、実際に組み込まれた構成部品の版まで確認してください。

### Cosminexus HTTP Serverの対象範囲

CVE-2026-49975はLinux 11-70、11-50-01から11-50-41、11-20-23から11-20-41、Windows 11-50から11-50-41、11-20-22から11-20-41などが対象です。CVE-2026-48913はLinux 11-70と11-50-01から11-50-41、Windows 11-50から11-50-41が対象です。残る2件はAIXや旧V9系列など、さらに広い版を含みます。複数のCVEに該当する環境もあるため、一つのアドバイザリだけで判定しないでください。

### Hitachi Web Serverと構成製品

Hitachi Web Server 10-00から10-11-01はCVE-2026-43951とCVE-2026-33523の対象として掲載されています。日立はこの製品について対策版の発行予定がないと注記しています。また、Cosminexus HTTP ServerやHitachi Web Serverを含むuCosminexus、Hitachi Application Serverも影響対象になり得ます。自社が直接Webサーバーを導入した認識がなくても、アプリケーション基盤に含まれていないか確認が必要です。[サーバー側の責任分界点](https://www.cybernote.click/2026/07/19/wordpress-server-security/)も、構成部品の管理範囲を整理する参考になります。

## 管理者が確認する対応

優先順位は、利用有無の特定、対象版との照合、対策版の適用です。更新まで時間がかかる環境では到達経路を絞り、HTTP/2条件も確認しますが、緩和策だけで完了扱いにしない運用が必要です。担当者と期限も明確にします。

### 対策版へ更新する

日立は主要な対象に対し、Linuxでは11-70-02または11-50-42、Windowsでは11-50-42などの対策版を案内しています。適用できる版は製品系列とCVEで異なるため、4件の公式ページを確認し、サポート契約がある場合は窓口へ対象版を照会してください。更新後は稼働プロセスが参照する実体の版を再確認し、冗長系、検証環境、災害対策環境に古い版が残っていないかも点検します。[月例更新後の確認手順](https://www.cybernote.click/2026/07/27/microsoft-july-2026-exploited-cves/)と同様に、適用結果まで記録することが重要です。

### HTTP/2と公開範囲を確認する

CVE-2026-49975とCVE-2026-48913はHTTP/2を使わない構成では発生しません。更新までの暫定策としてHTTP/2無効化を検討できますが、業務影響と設定反映をテストし、残る2件には効かないことを明記してください。あわせて、管理用ポートや不要なWeb公開をインターネットから切り離し、リバースプロキシやファイアウォールで到達元を制限します。[Apache Tomcatの更新記事](https://www.cybernote.click/2026/08/05/apache-tomcat-cve-2026-34486-encryptinterceptor-kev/)でも、構成条件を確認してから更新する考え方を解説しています。

### ログと異常を確認する

日立の公表情報では、既知の悪用や具体的な侵害事例は示されていません。そのため利用組織の被害を一律に断定することはできませんが、対象版を外部公開していた場合は、更新前後のアクセスログ、異常なHTTP要求、予期しない設定変更、サービス再起動、エラー増加を確認してください。疑わしい挙動があればログを保全し、影響するデータと認証情報を特定して、インシデント対応手順に沿って調査します。

## FAQ

対象判定では、4件を一括りにせず、製品名、OS、版数、HTTP/2利用の有無を順番に照合する必要があります。管理者が判断に迷いやすい点を、公式情報に基づいて整理します。作業記録に残す際の要点としても利用してください。

### Cosminexus HTTP Serverのどの環境が影響を受けますか？

CVEごとに対象版が異なります。Linux、Windows、AIXなどの稼働版とHTTP/2の利用状況を、日立の4件の公式情報で照合してください。

### HTTP/2を無効にすれば更新は不要ですか？

HTTP/2無効化で回避できるのはCVE-2026-49975とCVE-2026-48913です。残る2件には当てはまらないため、対策版への更新が基本です。

### Hitachi Web Serverはどのように対応すればよいですか？

対策版の発行予定がない対象版があります。利用組織はサポート窓口へ相談し、移行、公開制限、代替製品を含む対応計画を決めてください。

## 参考情報

対象版と対策版は更新される可能性があるため、作業時点の公式情報を確認してください。主な出典は、日立製作所の[CVE-2026-49975](https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-128/index.html)、[CVE-2026-48913](https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-127/index.html)、[CVE-2026-43951](https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-126/index.html)、[CVE-2026-33523](https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-129/index.html)です。第三者の整理情報として[JVN iPedia](https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-026849.html)も参照できます。

## まとめ

Cosminexus HTTP ServerとHitachi Web Serverでは、CVE-2026-49975、CVE-2026-48913、CVE-2026-43951、CVE-2026-33523の4件が公表されました。最も高いCVSS基本値は7.5で、サービス停止、情報漏えい、改ざんへつながる可能性があります。製品名、OS、版数とHTTP/2利用の有無を確認し、日立が示す対策版へ更新してください。対策版の予定がない環境はサポート窓口と移行計画を決め、完了まで公開範囲を制限します。既知の悪用は公表されていませんが、外部公開環境ではログと設定変更の有無も確認しましょう。
