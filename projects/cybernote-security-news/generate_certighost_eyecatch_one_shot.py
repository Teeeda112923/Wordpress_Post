from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 800
BG = "#0B1F33"
PANEL = "#102A43"
PANEL2 = "#123651"
CYAN = "#22D3EE"
GREEN = "#34D399"
RED = "#F43F5E"
WHITE = "#F8FAFC"
MUTED = "#B7C7D6"
GRID = "#12304A"
FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
for x in range(0, W, 60):
    d.line((x, 0, x, H), fill=GRID, width=1)
for y in range(0, H, 60):
    d.line((0, y, W, y), fill=GRID, width=1)

d.rounded_rectangle((58, 54, 330, 112), 18, outline=CYAN, width=3, fill="#0D253A")
d.text((82, 69), "セキュリティニュース", font=font(24, True), fill=CYAN)
d.text((60, 155), "AD CSの脆弱性", font=font(62, True), fill=WHITE)
d.text((60, 240), "「Certighost」とは？", font=font(58, True), fill=CYAN)
d.line((64, 330, 235, 330), fill=CYAN, width=5)
d.text((60, 365), "CVE-2026-54121", font=font(35, True), fill=RED)
d.text((338, 370), "低権限からドメイン侵害の恐れ", font=font(27, True), fill=WHITE)

d.rounded_rectangle((60, 674, 470, 744), 18, fill="#0D253A", outline=GREEN, width=2)
d.text((90, 690), "影響・仕組み・対策を解説", font=font(28, True), fill=WHITE)

d.rounded_rectangle((665, 145, 990, 480), 24, fill=PANEL2, outline=CYAN, width=4)
d.text((762, 168), "証明書", font=font(34, True), fill=WHITE)
d.line((700, 220, 955, 220), fill=CYAN, width=2)
d.text((705, 245), "発行先", font=font(20, True), fill=MUTED)
d.text((705, 277), "CN=Domain Controller", font=font(22, True), fill=WHITE)
d.text((705, 325), "発行者", font=font(20, True), fill=MUTED)
d.text((705, 357), "Enterprise CA", font=font(22, True), fill=WHITE)
d.text((705, 405), "CVE-2026-54121", font=font(20, True), fill=RED)
d.ellipse((900, 393, 960, 453), fill=GREEN, outline=WHITE, width=2)
d.line((916, 423, 929, 436, 950, 410), fill=WHITE, width=5)

ghost = "#B9DCF0"
d.ellipse((960, 50, 1125, 235), fill=ghost)
d.polygon([(960, 145), (1125, 145), (1160, 390), (1120, 360), (1085, 395), (1050, 360), (1015, 395), (975, 360)], fill=ghost)
d.ellipse((997, 112, 1024, 151), fill=BG)
d.ellipse((1063, 112, 1090, 151), fill=BG)

d.ellipse((620, 555, 715, 650), outline=MUTED, width=3, fill=PANEL)
d.ellipse((653, 573, 682, 602), fill=MUTED)
d.pieslice((638, 596, 697, 642), 180, 360, fill=MUTED)
d.text((592, 657), "低権限ユーザー", font=font(21, True), fill=CYAN)

d.rounded_rectangle((965, 505, 1143, 721), 14, fill="#0E263C", outline="#3A6788", width=3)
d.text((983, 525), "Domain Controller", font=font(17, True), fill=WHITE)
for y in (570, 610, 650):
    d.rounded_rectangle((985, y, 1125, y + 25), 6, fill=PANEL2)
    d.ellipse((1095, y + 8, 1105, y + 18), fill=CYAN)
    d.ellipse((1110, y + 8, 1120, y + 18), fill=GREEN)

crown = [(1020, 696), (1035, 670), (1055, 690), (1073, 660), (1093, 690), (1112, 670), (1125, 696)]
d.line(crown, fill=RED, width=5)
d.line((1020, 696, 1125, 696), fill=RED, width=5)
for x in range(735, 855, 22):
    d.ellipse((x, 603, x + 8, 611), fill=CYAN)
d.polygon([(880, 565), (930, 650), (830, 650)], outline=RED, fill="#172A3E")
d.text((870, 594), "!", font=font(34, True), fill=RED)
d.line((930, 625, 1000, 590), fill=RED, width=6)
d.polygon([(1000, 590), (982, 585), (994, 606)], fill=RED)
d.text((817, 684), "権限昇格・横展開", font=font(22, True), fill=RED)
d.text((1045, 752), "CyberNote", font=font(18), fill=MUTED)

out = Path("projects/cybernote-security-news/eyecatches/ad-cs-certighost-cve-2026-54121.png")
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out, "PNG", optimize=True, compress_level=9)
with Image.open(out) as check:
    check.load()
    assert check.size == (1200, 800)
    assert check.mode == "RGB"
assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
print(f"validated {out} size=1200x800 mode=RGB bytes={out.stat().st_size}")
