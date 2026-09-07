---
answer: "日立製Webサーバーの製品・OS・版数・HTTP/2利用を照合し、案内された対策版へ更新してください。"
cve: "CVE-2026-49975, CVE-2026-48913, CVE-2026-43951, CVE-2026-33523"
faq:
  - q: "Cosminexus HTTP Serverのどの環境が影響を受けますか？"
    a: "CVEごとに対象版が異なり、Linux、Windows、AIXなどの条件も分かれます。製品名とOS、実際の版数、HTTP/2の利用状況を日立の4件の公式情報で照合してください。"
  - q: "HTTP/2を無効にすれば更新は不要ですか？"
    a: "いいえ。HTTP/2を使わないことで回避できるのはCVE-2026-49975とCVE-2026-48913です。残る2件には当てはまらないため、対策版への更新を基本にします。"
  - q: "Hitachi Web Serverに対策版がない場合はどうしますか？"
    a: "日立は一部対象版について対策版の発行予定なしと案内しています。サポート窓口へ相談し、サポート対象製品への移行、公開制限、代替手段を含む計画を決めてください。"
sources:
  - title: "CVE-2026-49975に関する日立製品の影響"
    url: "https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-128/index.html"
    publisher: "日立製作所"
  - title: "CVE-2026-48913に関する日立製品の影響"
    url: "https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-127/index.html"
    publisher: "日立製作所"
  - title: "CVE-2026-43951に関する日立製品の影響"
    url: "https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-126/index.html"
    publisher: "日立製作所"
  - title: "CVE-2026-33523に関する日立製品の影響"
    url: "https://www.hitachi.co.jp/Prod/comp/soft1/security/info/vuls/hitachi-sec-2026-129/index.html"
    publisher: "日立製作所"
  - title: "CVE-2026-49975 CVE Record"
    url: "https://www.cve.org/CVERecord?id=CVE-2026-49975"
    publisher: "CVE Program / Apache CNA"
---

# 【重要】日立Cosminexus HTTP Serverに4件の脆弱性、対象版と更新方法を確認

日立製作所は、Cosminexus HTTP ServerとHitachi Web Serverに影響する4件の脆弱性情報を公開しました。対象はCVE-2026-49975、CVE-2026-48913、CVE-2026-43951、CVE-2026-33523で、最も高いCVSS v3.1基本値は7.5です。サービス停止だけでなく、条件によって情報の参照や変更につながる可能性があります。対象版は製品系列、OS、CVEごとに異なり、HTTP/2を使わないことで回避できる問題も一部に限られます。利用組織は組み込み先を含む実際の版を確認し、日立が示す対策版へ更新してください。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 参照</p>
<!-- /wp:paragraph -->
<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cybernote.click/2026/08/05/apache-tomcat-cve-2026-34486-encryptinterceptor-kev/"} /--></div>
<!-- /wp:group -->

## 4件で影響と成立条件が異なる

CVE-2026-49975は、過大なメモリー確保によりサービス停止へつながる可能性がある問題で、CVSS基本値は7.5です。CVE-2026-48913はHTTP/2処理の解放済みメモリー参照で、情報の参照・変更と停止が想定されています。

CVE-2026-43951は複数言語の応答処理における境界外読み取り、CVE-2026-33523は信頼できないバックエンドが関係するHTTPレスポンス分割です。両者のCVSS基本値は6.5です。いずれも認証されていない攻撃者からネットワーク経由で悪用される可能性がありますが、条件と影響は同じではありません。確認した一次情報では実悪用や個別組織の侵害は示されていません。

## 製品名・OS・版数を公式表と照合する

対象範囲はCosminexus HTTP Serverを直接導入した環境だけではありません。uCosminexus Application ServerやHitachi Application Serverなど、構成製品として含む環境も確認対象になります。資産台帳と実際の導入物を突き合わせてください。

日立は対象系列ごとに対策版を案内しており、例としてLinuxの11-70-02や11-50-42、Windowsの11-50-42などがあります。適用先はCVEと系列で異なるため、単一の番号だけで判断せず4件の公式ページを確認します。Hitachi Web Serverの一部には対策版の発行予定がないため、サポート窓口と移行計画を決めます。[サーバー側の責任分界点](https://www.cybernote.click/2026/07/19/wordpress-server-security/)も整理に役立ちます。

## 更新と緩和策を完了まで追跡する

CVE-2026-49975とCVE-2026-48913は、HTTP/2を使用しない構成では発生しないと日立が説明しています。更新までの暫定策として無効化を検討できますが、残る2件には効かないため、恒久対応を終えた扱いにはしません。

更新前に設定とデータを保全し、冗長系、検証環境、災害対策環境も含めて適用します。更新後は稼働プロセスが参照する実体の版を確認し、アクセスログ、異常なHTTP要求、サービス再起動、予期しない設定変更を点検してください。[月例更新後の確認手順](https://www.cybernote.click/2026/07/27/microsoft-july-2026-exploited-cves/)と同様に、対象、担当者、期限、適用結果を記録します。

## まとめ

Cosminexus HTTP ServerとHitachi Web Serverには、CVE-2026-49975、CVE-2026-48913、CVE-2026-43951、CVE-2026-33523の影響があります。最も高いCVSS基本値は7.5で、サービス停止や情報の参照・変更につながる可能性があります。製品名、組み込み先、OS、版数、HTTP/2利用を日立の公式情報と照合し、対策版へ更新してください。HTTP/2無効化は一部だけの暫定策です。対策版がない環境はサポート窓口と移行計画を決め、完了まで公開範囲を制限します。実悪用や侵害は一次情報で未確認のため、ログに基づいて判断しましょう。
