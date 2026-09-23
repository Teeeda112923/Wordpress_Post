"""Create a clean, typography-led CyberNote news image (1200x800 PNG)."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 800
NAVY, PANEL, WHITE, MUTED, CYAN = "#0B1F33", "#112B42", "#F3F7FA", "#B6C8D7", "#22D3EE"

def font_path(bold=False):
    name = "NotoSansCJK-Bold.ttc" if bold else "NotoSansCJK-Regular.ttc"
    for root in (Path("/usr/share/fonts/opentype/noto"), Path("/usr/share/fonts/truetype/noto")):
        path = root / name
        if path.exists():
            return str(path)
    path = subprocess.check_output(
        ["fc-match", "-f", "%{file}", "Noto Sans JP:style=Bold" if bold else "Noto Sans JP"],
        text=True
    ).strip()
    if not path or not Path(path).exists():
        raise RuntimeError("Noto Sans JP/CJK fonts not found")
    return path

def create(path):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    reg, bold = font_path(), font_path(True)
    f = lambda n, b=False: ImageFont.truetype(bold if b else reg, n)
    d.rectangle((0, 0, 18, H), fill=CYAN)
    d.rectangle((800, 0, W, H), fill=PANEL)
    d.line((800, 0, 800, H), fill="#35556E", width=2)
    d.text((75, 61), "CyberNote", font=f(42, True), fill=WHITE)
    d.text((342, 79), "CLOUD SECURITY / 2026.09", font=f(21), fill=MUTED)
    d.line((73, 145, 738, 145), fill="#426C87", width=2)
    d.text((69, 188), "AWS × NATO", font=f(97, True), fill=WHITE)
    d.text((72, 316), "NATO RESTRICTED", font=f(48, True), fill=CYAN)
    d.rectangle((73, 398, 680, 405), fill=CYAN)
    d.text((72, 446), "全加盟国向けクラウド機能の承認", font=f(34, True), fill=WHITE)
    d.text((74, 514), "対象範囲・D32・各国の認定を解説", font=f(27), fill=MUTED)
    d.line((73, 668, 740, 668), fill="#426C87", width=2)
    d.text((74, 704), "AWS / NATO  |  CLOUD SECURITY", font=f(21), fill=MUTED)
    d.ellipse((845, 180, 1140, 475), outline="#325F79", width=2)
    d.ellipse((882, 217, 1103, 438), outline="#477489", width=2)
    d.line((991, 180, 991, 218), fill=CYAN, width=2)
    d.line((991, 438, 991, 475), fill=CYAN, width=2)
    outline = [(990, 265), (1051, 284), (1045, 356), (990, 395),
               (935, 356), (929, 284), (990, 265)]
    d.line(outline, fill=CYAN, width=6, joint="curve")
    d.line([(958, 326), (980, 347), (1024, 309)], fill=CYAN, width=8, joint="curve")
    for x, y in [(868, 160), (1128, 157), (856, 507), (1134, 511)]:
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=CYAN)
    d.line((868, 160, 1128, 157), fill="#365F79", width=2)
    d.line((856, 507, 1134, 511), fill="#365F79", width=2)
    d.text((864, 565), "D32  /  SECURITY", font=f(25, True), fill=WHITE)
    d.text((865, 615), "CLOUD  /  TRUST", font=f(19), fill=MUTED)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)
    with Image.open(path) as check:
        check.load()
        assert check.format == "PNG" and check.size == (W, H) and check.mode == "RGB"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    create(Path(ap.parse_args().output))
