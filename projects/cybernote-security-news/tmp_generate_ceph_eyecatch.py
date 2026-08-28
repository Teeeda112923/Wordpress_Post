from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path('projects/cybernote-security-news/eyecatches/ceph-cve-2026-50152-monitor-config-key-secrets.png')
OUT.parent.mkdir(parents=True, exist_ok=True)
W, H = 1200, 800
img = Image.new('RGB', (W, H), (11, 31, 51))
d = ImageDraw.Draw(img)
font_candidates = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]
font_path = next(p for p in font_candidates if Path(p).exists())
d.rounded_rectangle((70, 70, 1130, 730), radius=28, fill=(15, 42, 65), outline=(34, 211, 238), width=3)
items = [
    ((110, 145), 'Ceph', 72, (245, 248, 250)),
    ((110, 285), 'CVE-2026-50152', 62, (34, 211, 238)),
    ((110, 410), 'CVSS 8.2 / 設定鍵ストアの秘密情報', 40, (245, 248, 250)),
    ((110, 565), '対処：20.2.4 / 19.2.6へ更新', 50, (245, 248, 250)),
]
for pos, text, size, color in items:
    font = ImageFont.truetype(font_path, size)
    bbox = d.textbbox(pos, text, font=font)
    if bbox[0] < 0 or bbox[1] < 0 or bbox[2] > W or bbox[3] > H:
        raise RuntimeError(f'text clipping: {text} {bbox}')
    d.text(pos, text, font=font, fill=color)
img.save(OUT, 'PNG', optimize=True, compress_level=9)
raw = OUT.read_bytes()
if raw[:8] != b'\x89PNG\r\n\x1a\n':
    raise RuntimeError('bad PNG signature')
with Image.open(OUT) as check:
    check.load()
    if check.format != 'PNG' or check.size != (1200, 800) or check.mode != 'RGB':
        raise RuntimeError(f'bad image: {check.format} {check.size} {check.mode}')
print(f'validated {OUT} bytes={len(raw)}')
