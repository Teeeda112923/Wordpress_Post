#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 800
BG, CYAN, GREEN, RED = "#0B1F33", "#22D3EE", "#34D399", "#F43F5E"
WHITE, MUTED, PANEL = "#F8FAFC", "#A9BDD0", "#102A43"
font_dir = Path("/usr/share/fonts/opentype/noto")
bolds = list(font_dir.glob("NotoSansCJK-Bold.ttc")) + list(font_dir.glob("NotoSansCJK-Black.ttc"))
regs = list(font_dir.glob("NotoSansCJK-Regular.ttc")) + list(font_dir.glob("NotoSansCJK-Medium.ttc"))
if not (bolds or regs):
    raise SystemExit("Noto Sans CJK font not found")
bold = str((bolds or regs)[0])
reg = str((regs or bolds)[0])
f_title = ImageFont.truetype(bold, 86)
f_sub = ImageFont.truetype(bold, 44)
f_badge = ImageFont.truetype(bold, 28)
f_small = ImageFont.truetype(reg, 23)
f_tiny = ImageFont.truetype(reg, 18)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
for x in range(0, W, 60):
    d.line((x, 0, x, H), fill="#0F2940")
for y in range(0, H, 60):
    d.line((0, y, W, y), fill="#0F2940")

d.text((62, 54), "WP2Shell 続報", font=f_title, fill=WHITE)
d.text((66, 162), "実悪用確認・攻撃試行を観測", font=f_sub, fill=CYAN)
d.rounded_rectangle((62, 235, 1138, 645), radius=28, fill=PANEL, outline="#1D4667", width=3)

shield = [(150, 310), (218, 282), (286, 310), (278, 404), (218, 466), (158, 404)]
d.polygon(shield, outline=GREEN, fill="#123A43")
d.line((183, 370, 209, 397, 258, 340), fill=GREEN, width=13)

d.text((345, 292), "WordPress REST API", font=f_badge, fill=WHITE)
d.text((345, 339), "CVE-2026-63030 / CVE-2026-60137", font=f_small, fill=MUTED)
for i, w in enumerate((650, 575, 490, 620, 540)):
    y = 400 + i * 38
    d.rounded_rectangle((345, y, 345 + w, y + 17), radius=8, fill="#163A57")
    d.rounded_rectangle((345, y, 345 + int(w * (0.58 + i * 0.055)), y + 17), radius=8, fill=CYAN if i < 3 else GREEN)

d.ellipse((1010, 392, 1040, 422), fill=RED)
d.line((930, 408, 1013, 408), fill=RED, width=4)
d.text((930, 438), "attack traffic", font=f_tiny, fill=MUTED)

for x1, x2, text, color in [
    (62, 305, "CISA KEV", RED),
    (327, 615, "実悪用確認", CYAN),
    (637, 925, "国内でも観測", GREEN),
]:
    d.rounded_rectangle((x1, 690, x2, 748), radius=18, outline=color, width=3)
    box = d.textbbox((0, 0), text, font=f_badge)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text(((x1 + x2 - tw) / 2, (690 + 748 - th) / 2 - 3), text, font=f_badge, fill=color)

d.text((957, 704), "CyberNote", font=f_small, fill=MUTED)

out = Path("projects/cybernote-security-news/eyecatches/wordpress-wp2shell-followup-exploitation-observed.png")
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out, format="PNG", optimize=True)
check = Image.open(out)
check.load()
assert check.size == (1200, 800)
assert check.mode == "RGB"
print(f"validated {out} size={check.size} mode={check.mode} bytes={out.stat().st_size}")
