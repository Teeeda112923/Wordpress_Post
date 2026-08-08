---
answer: "NVIDIA Dynamo利用者は構成別の修正版へ更新し、外部公開範囲とログを確認してください。"
cve: "CVE-2026-24254, CVE-2026-24253, CVE-2026-24255, CVE-2026-47612, CVE-2026-47613, CVE-2026-47614, CVE-2026-47615, CVE-2026-47616, CVE-2026-47617, CVE-2026-47618, CVE-2026-47619, CVE-2026-47620, CVE-2026-47621, CVE-2026-47622, CVE-2026-47623"
faq:
  - q: "最優先で確認する脆弱性は？"
    a: "認証不要かつネットワーク経由で悪用可能と評価されたCriticalのCVE-2026-24254を最優先で確認してください。"
  - q: "どのバージョンへ更新すればよいですか？"
    a: "CVEごとに修正版が異なるため、NVIDIAの対応表と自社構成を照合し、必要に応じて必ずv1.3.0まで更新してください。"
sources:
  - title: "Security Bulletin: NVIDIA Dynamo - August 2026"
    url: "https://nvidia.custhelp.com/app/answers/detail/a_id/5842/~/security-bulletin%3A-nvidia-dynamo---august-2026"
    publisher: "NVIDIA"
  - title: "CVE-2026-24254 Detail"
    url: "https://nvd.nist.gov/vuln/detail/CVE-2026-24254"
    publisher: "NIST NVD"
---

# 【緊急】NVIDIA Dynamoに15件の脆弱性、Criticalを含む更新を公開

NVIDIAは2026年8月4日、Linux向けAI推論フレームワーク「Dynamo」の15件の脆弱性を修正しました。最も深刻なCVE-2026-24254はCVSS 9.8のCriticalで、マルチモーダル処理を介して認証不要の遠隔攻撃者に境界外書き込みを起こされ、コード実行や権限昇格、改ざん、サービス停止、情報漏えいにつながるおそれがあります。既知の悪用や被害は公式情報で確認されていません。利用組織は稼働版と機能を特定し、該当する修正版へ更新してください。

<!-- wp:group {"className":"is-style-information-box","layout":{"type":"constrained"}} -->
<div class="wp-block-group is-style-information-box"><!-- wp:paragraph -->
<p>▼ 参照</p>
<!-- /wp:paragraph -->

<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://nvd.nist.gov/vuln/detail/CVE-2026-24254"} /--></div>
<!-- /wp:group -->

## 概要と影響

SSRFやパストラバーサルなども含まれ、修正版はCVEにより異なります。AI基盤の点検には[SGLang](https://www.cybernote.click/2026/08/03/sglang-six-vulnerabilities-no-patch/)、[IBM Langflow](https://www.cybernote.click/2026/08/05/ibm-langflow-cve-2026-9198/)、[Jupyter Enterprise Gateway](https://www.cybernote.click/2026/08/09/jupyter-enterprise-gateway-cve-2026-44180-44181-44182/)の記事も参考になります。

## 利用者が確認すること

導入版、マルチモーダル機能、外部公開APIを棚卸しし、公式表と照合してください。更新後は不審な要求、外部通信、異常終了、権限変更をログで確認し、コンテナ内の実バージョンも点検します。

## FAQ

脆弱性が多いため、最新版の有無だけでなく、利用機能と到達経路を対応付けることが重要です。公表された件数だけで全環境の侵害を推定せず、自社の構成と十分に保存したログに基づいて影響を慎重に判断してください。

### 最優先で確認する脆弱性は？

認証不要で遠隔から悪用可能なCVE-2026-24254を優先します。

### どのバージョンへ更新すればよいですか？

公式の対応表と構成を照合し、必要に応じてv1.3.0まで更新します。

## 参考情報

対象版と修正版は[NVIDIA公式情報](https://nvidia.custhelp.com/app/answers/detail/a_id/5842/~/security-bulletin%3A-nvidia-dynamo---august-2026)、評価は[NIST NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-24254)で確認できます。

## まとめ

NVIDIA Dynamoでは15件の脆弱性が修正され、CVE-2026-24254は認証不要の遠隔攻撃者によるコード実行などにつながり得るCriticalと評価されています。一方、公式情報は既知の悪用や利用組織の侵害を示していません。管理者は導入版と利用機能を特定し、CVE別の対応表に従ってv1.1.1、v1.2.0、またはv1.3.0へ更新してください。更新後も外部公開範囲、不審なAPI要求、外部通信、異常終了、権限変更、機密情報へのアクセスを確認し、コンテナや固定済み依存関係に古い版が残っていないか点検することが重要です。
