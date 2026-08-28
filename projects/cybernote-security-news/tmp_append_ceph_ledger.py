import csv
from pathlib import Path

path = Path('projects/cybernote-security-news/data/news_ledger.csv')
with path.open(encoding='utf-8-sig', newline='') as handle:
    reader = csv.DictReader(handle)
    fieldnames = reader.fieldnames or []
    rows = list(reader)

expected = ['No','収集日','公開予定日','記事分類','指定KW','話題性スコア','記事タイトル案','記事タイトル','スラッグ','メタディスクリプション','WPカテゴリ','タグ案','記事ファイル','画像ファイル名','主な出典URL','内部リンクURL','目標文字数','生成ステータス','レビュー判定','公開停止','WP投稿ID','WP投稿URL','投稿ステータス','最終更新日時','エラー内容','候補ID']
if fieldnames != expected:
    raise RuntimeError(f'ledger header mismatch: {fieldnames}')

candidate_id = '20260829-001'
slug = 'ceph-cve-2026-50152-monitor-config-key-secrets'
if any((r.get('候補ID') or '').strip() == candidate_id or (r.get('スラッグ') or '').strip() == slug for r in rows):
    print('Ceph row already exists; no duplicate append')
    raise SystemExit(0)

max_no = max(int((r.get('No') or '0').strip() or 0) for r in rows)
today_count = sum(1 for r in rows if (r.get('収集日') or '').strip() == '2026-08-29' and (r.get('生成ステータス') or '').strip() == '生成済み')
if max_no != 76:
    raise RuntimeError(f'unexpected max No before append: {max_no}')
if today_count >= 4:
    raise RuntimeError(f'daily generation limit reached: {today_count}')

row = {
    'No':'77','収集日':'2026-08-29','公開予定日':'2026-08-29','記事分類':'分散ストレージ脆弱性','指定KW':'Ceph','話題性スコア':'94',
    '記事タイトル案':'Cephの設定鍵ストアが低権限ユーザーから読取可能、CVE-2026-50152はCVSS 8.2',
    '記事タイトル':'【重要】CephにCVSS 8.2、設定鍵ストアの秘密情報が読取可能',
    'スラッグ':slug,
    'メタディスクリプション':'CephのCVE-2026-50152を解説。CVSS 8.2、影響条件、20.2.4／19.2.6への更新と秘密鍵の確認をまとめます。',
    'WPカテゴリ':'サイバーセキュリティ','タグ案':'Ceph,CVE-2026-50152,CephX,cephadm,秘密鍵',
    '記事ファイル':'projects/cybernote-security-news/articles/ceph-cve-2026-50152-monitor-config-key-secrets.md',
    '画像ファイル名':'projects/cybernote-security-news/eyecatches/ceph-cve-2026-50152-monitor-config-key-secrets.png',
    '主な出典URL':'https://github.com/ceph/ceph/security/advisories/GHSA-rg9p-5xcp-wm8h',
    '内部リンクURL':'https://www.cybernote.click/2026/08/25/amazon-opensearch-cve-2026-77811-stored-xss/',
    '目標文字数':'1500','生成ステータス':'生成済み','レビュー判定':'未確認','公開停止':'','WP投稿ID':'','WP投稿URL':'','投稿ステータス':'','最終更新日時':'','エラー内容':'','候補ID':candidate_id,
}
with path.open('a', encoding='utf-8', newline='') as handle:
    if path.stat().st_size and not path.read_bytes().endswith(b'\n'):
        handle.write('\n')
    writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator='\n')
    writer.writerow(row)
print('Appended No.77 Ceph ledger row')
