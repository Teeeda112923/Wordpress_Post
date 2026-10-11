#!/usr/bin/env python3
"""記事アイキャッチをコード（SVG）で描画し、1200×800のPNGに書き出す。

画像生成AIを使わず、JSONの指定からSVGを組み立ててChromiumで描画する。
文字はフォントで描くため、製品名・CVE番号・CVSSの誤字や文字化けは起きない。
長い文字列は枠に収まるまで自動で縮め、最小サイズでも収まらない場合や
画面外・イラストへの重なりがある場合は、保存せずに失敗させる。

使い方:
    python render_eyecatch.py spec.json projects/cybernote-security-news/eyecatches/{slug}.png

指定（spec.json）の項目:
    layout         "banner"（帯ラベル＋CVSSバッジ） / "stack"（色分けした行を縦に並べる）
                   / "panel"（事件・ニュース向け。数値と日付の行を並べる）
    tone           "alert"（赤。緊急・実悪用） / "update"（シアン。通常の更新）
    title          製品名など。文字列、または2行までの配列
    icon           monitor / browser / server / mail / cloud / phone / router /
                   database / code / document
    badge          shield / warning / none
    label          banner の帯ラベル（例: 緊急セキュリティ更新）
    cve, cvss      CVE番号とCVSS基本値（一次情報で確認した値だけを入れる）
    status         stack の状況行（例: 実悪用を確認）
    action         対応方法（例: 2026年9月の累積更新を適用）
    action_accent  action の先頭のうち強調色にする部分（例: 2026年9月）
    panel 専用     kicker_date, subtitle, figure, lead, note,
                   rows（[[項目, 値, "red"|"green"|"cyan"], ...] 最大2行）, caption, source

出力と同じ場所に {name}.png.identity.json を書く（投稿前の identity gate 用）。
描画には playwright（Chromium）と Noto Sans JP 系フォントが必要。
"""
from __future__ import annotations

import argparse
import html
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image

from eyecatch_identity import (
    manifest_path,
    verify_manifest,
    visual_hash_bytes,
    write_manifest,
)

WIDTH = 1200
HEIGHT = 800
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# 途中で切れた画像はすべて768 KiB境界で終わっていた（eyecatch_file_check.py）。
# コード描画なら通常100〜200KBに収まる。境界に近づいたら保存させない。
MAX_BYTES = 700 * 1024
SAFE_MARGIN = 24

FONT_FAMILY = '"Noto Sans JP","Noto Sans CJK JP",sans-serif'
LAYOUTS = ("banner", "stack", "panel")
TONES = ("alert", "update")
BADGES = ("shield", "warning", "none")

WHITE = "#ffffff"
CYAN = "#22d3ee"
GREEN = "#34d399"
RED = "#f43f5e"
GREY = "#9fb3c8"
PANEL = "#0e3058"
LINE = "#2b5d8f"
COLORS = {"red": RED, "green": GREEN, "cyan": CYAN, "white": WHITE}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


# ---------------------------------------------------------------- icons
# すべて 324×282 の枠に収める。右下（336, 208）にバッジを重ねる。

def _frame(extra: str) -> str:
    return f'<g fill="{PANEL}" stroke="{CYAN}" stroke-linecap="round" stroke-linejoin="round">{extra}</g>'


def icon_monitor() -> str:
    return _frame(
        '<rect x="6" y="6" width="312" height="224" rx="16" stroke-width="12"/>'
        '<rect x="76" y="50" width="112" height="84" rx="6" stroke-width="6"/>'
        '<rect x="132" y="86" width="116" height="90" rx="6" stroke-width="6"/>'
        '<path d="M166 114l18 17-18 17M216 114l-18 17 18 17" fill="none" stroke-width="6"/>'
    ) + (f'<rect x="124" y="236" width="76" height="30" fill="{CYAN}"/>'
         f'<rect x="64" y="262" width="196" height="16" rx="8" fill="{CYAN}"/>')


def _window() -> str:
    return (
        '<rect x="6" y="20" width="312" height="240" rx="16" stroke-width="12"/>'
        '<path d="M6 78H318" fill="none" stroke-width="8"/>'
    )


def icon_browser() -> str:
    return _frame(_window()) + (
        f'<circle cx="40" cy="50" r="8" fill="{CYAN}"/><circle cx="66" cy="50" r="8" fill="{CYAN}"/>'
        f'<rect x="100" y="40" width="190" height="20" rx="10" fill="#17406b"/>'
        f'<rect x="40" y="112" width="150" height="18" rx="9" fill="{CYAN}"/>'
        f'<rect x="40" y="152" width="244" height="12" rx="6" fill="{LINE}"/>'
        f'<rect x="40" y="182" width="200" height="12" rx="6" fill="{LINE}"/>'
        f'<rect x="40" y="212" width="160" height="12" rx="6" fill="{LINE}"/>'
    )


def icon_code() -> str:
    return _frame(
        _window()
        + '<path d="M118 132l-38 38 38 38M206 132l38 38-38 38M180 122l-36 96" fill="none" stroke-width="12"/>'
    ) + f'<circle cx="40" cy="50" r="8" fill="{CYAN}"/><circle cx="66" cy="50" r="8" fill="{CYAN}"/>'


def icon_server() -> str:
    parts = []
    leds = []
    for y in (6, 100, 194):
        parts.append(f'<rect x="6" y="{y}" width="312" height="82" rx="12" stroke-width="10"/>')
        leds.append(
            f'<circle cx="46" cy="{y + 41}" r="9" fill="{GREEN}"/>'
            f'<circle cx="76" cy="{y + 41}" r="9" fill="{CYAN}"/>'
            f'<rect x="150" y="{y + 35}" width="130" height="12" rx="6" fill="{LINE}"/>'
        )
    return _frame("".join(parts)) + "".join(leds)


def icon_mail() -> str:
    return _frame(
        '<rect x="6" y="36" width="312" height="212" rx="16" stroke-width="12"/>'
        '<path d="M16 54L162 162L308 54" fill="none" stroke-width="10"/>'
    )


def icon_cloud() -> str:
    return _frame(
        '<path d="M92 240a66 66 0 0 1 -8 -131a90 90 0 0 1 172 -22a77 77 0 0 1 -6 153Z" stroke-width="12"/>'
    ) + (f'<rect x="112" y="150" width="100" height="12" rx="6" fill="{LINE}"/>'
         f'<rect x="112" y="180" width="140" height="12" rx="6" fill="{LINE}"/>')


def icon_phone() -> str:
    return _frame('<rect x="87" y="6" width="150" height="270" rx="24" stroke-width="12"/>') + (
        f'<rect x="137" y="24" width="50" height="8" rx="4" fill="{CYAN}"/>'
        f'<rect x="114" y="62" width="96" height="70" rx="12" fill="{CYAN}"/>'
        f'<rect x="114" y="156" width="96" height="12" rx="6" fill="{LINE}"/>'
        f'<rect x="114" y="184" width="96" height="12" rx="6" fill="{LINE}"/>'
        f'<rect x="114" y="212" width="64" height="12" rx="6" fill="{LINE}"/>'
    )


def icon_router() -> str:
    return _frame(
        '<path d="M60 172V74M264 172V74" fill="none" stroke-width="12"/>'
        '<rect x="6" y="172" width="312" height="92" rx="16" stroke-width="12"/>'
        '<path d="M112 100a70 70 0 0 1 100 0M132 126a42 42 0 0 1 60 0" fill="none" stroke-width="10"/>'
    ) + (
        f'<circle cx="162" cy="148" r="9" fill="{CYAN}"/>'
        f'<circle cx="56" cy="218" r="9" fill="{GREEN}"/><circle cx="88" cy="218" r="9" fill="{CYAN}"/>'
        f'<circle cx="120" cy="218" r="9" fill="{CYAN}"/>'
        f'<rect x="180" y="212" width="104" height="12" rx="6" fill="{LINE}"/>'
    )


def icon_database() -> str:
    return _frame(
        '<path d="M32 52V230a130 40 0 0 0 260 0V52" stroke-width="12"/>'
        '<path d="M32 112a130 40 0 0 0 260 0M32 172a130 40 0 0 0 260 0" fill="none" stroke-width="8"/>'
        '<ellipse cx="162" cy="52" rx="130" ry="40" stroke-width="12"/>'
    )


def icon_document() -> str:
    return _frame(
        '<path d="M60 8H208L270 70V274H60Z" stroke-width="12"/>'
        '<path d="M208 8V70H270" fill="none" stroke-width="10"/>'
    ) + "".join(
        f'<rect x="92" y="{y}" width="{w}" height="12" rx="6" fill="{LINE}"/>'
        for y, w in ((116, 146), (150, 146), (184, 108), (218, 130))
    )


ICONS = {
    "monitor": icon_monitor, "browser": icon_browser, "server": icon_server,
    "mail": icon_mail, "cloud": icon_cloud, "phone": icon_phone,
    "router": icon_router, "database": icon_database, "code": icon_code,
    "document": icon_document,
}


def badge_svg(kind: str) -> str:
    if kind == "none":
        return ""
    if kind == "warning":
        body = (
            '<path d="M0,-88L96,72H-96Z" fill="url(#red)" stroke="#ff6b85" stroke-width="12" stroke-linejoin="round"/>'
            '<rect x="-9" y="-34" width="18" height="60" rx="9" fill="#fff"/><circle cy="46" r="10" fill="#fff"/>'
        )
    else:
        body = (
            '<path d="M0,-98C28,-76 52,-68 78,-66V-4C78,50 44,84 0,104C-44,84 -78,50 -78,-4V-66C-52,-68 -28,-76 0,-98Z" fill="#1a8f68"/>'
            '<path d="M0,-82C24,-64 44,-57 64,-55V-4C64,40 36,69 0,87C-36,69 -64,40 -64,-4V-55C-44,-57 -24,-64 0,-82Z" fill="url(#grn)"/>'
            '<path d="M-17,-8V-22a17,17 0 0 1 34,0V-8" fill="none" stroke="#fff" stroke-width="9"/>'
            '<rect x="-27" y="-10" width="54" height="46" rx="7" fill="#fff"/>'
            '<circle cy="9" r="6.5" fill="#17b584"/><rect x="-3" y="10" width="6" height="14" rx="3" fill="#17b584"/>'
        )
    return f'<g transform="translate(336,208)" filter="url(#sh)"><g data-art="badge">{body}</g></g>'


def art(spec: dict[str, Any], x: int, y: int, scale: float = 1.0) -> str:
    icon = ICONS[spec["icon"]]()
    return (
        f'<g id="art" transform="translate({x},{y}) scale({scale})">'
        f'<g filter="url(#sh)"><g data-art="icon">{icon}</g></g>{badge_svg(spec["badge"])}</g>'
    )


# ---------------------------------------------------------------- text

class Texts:
    """枠に合わせて縮める文字要素を集める。"""

    def __init__(self) -> None:
        self.count = 0

    def add(self, content: str, x: float, y: float, size: int, fit: int, *,
            weight: int = 900, fill: str = WHITE, minimum: int | None = None,
            anchor: str = "start", spacing: float = 0, raw: bool = False,
            group: str = "") -> str:
        self.count += 1
        minimum = minimum if minimum is not None else max(int(size * 0.55), 16)
        body = content if raw else esc(content)
        return (
            f'<text id="t{self.count}" x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{spacing}" '
            f'data-fit="{fit}" data-min="{minimum}" data-group="{group}">{body}</text>'
        )


def accent_text(action: str, accent: str, base: str = WHITE, color: str = GREEN) -> str:
    if accent and action.startswith(accent):
        return f'<tspan fill="{color}">{esc(accent)}</tspan><tspan fill="{base}">{esc(action[len(accent):])}</tspan>'
    return f'<tspan fill="{base}">{esc(action)}</tspan>'


def gear(x: int, y: int) -> str:
    teeth = "".join(
        f'<rect x="-7" y="-31" width="14" height="14" rx="3" transform="rotate({a})"/>'
        for a in range(0, 360, 45)
    )
    return (
        f'<g transform="translate({x},{y})"><circle r="46" fill="url(#grn)"/>'
        f'<g fill="#fff"><circle r="21"/>{teeth}</g><circle r="9" fill="#17b584"/></g>'
    )


# ---------------------------------------------------------------- layouts

DEFS = f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1f3a"/><stop offset="1" stop-color="#081a30"/></linearGradient>
<linearGradient id="red" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f43f5e"/><stop offset="1" stop-color="#d81e4a"/></linearGradient>
<linearGradient id="cyn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22c3e6"/><stop offset="1" stop-color="#0e93bd"/></linearGradient>
<linearGradient id="grn" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#34d399"/><stop offset="1" stop-color="#10a877"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="#1b6fa8" stop-opacity=".55"/><stop offset="1" stop-color="#1b6fa8" stop-opacity="0"/></radialGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><rect width="5" height="5" fill="#1d4470" opacity=".7"/></pattern>
<pattern id="grid" width="110" height="105" patternUnits="userSpaceOnUse"><path d="M110 0H0V105" fill="none" stroke="#16395c" stroke-width="1"/></pattern>
<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity=".35"/></filter>
</defs>"""


def title_lines(spec: dict[str, Any]) -> list[str]:
    title = spec["title"]
    return [title] if isinstance(title, str) else list(title)


def layout_banner(spec: dict[str, Any], t: Texts) -> str:
    alert = spec["tone"] == "alert"
    grad, slash = ("url(#red)", RED) if alert else ("url(#cyn)", CYAN)
    lines = title_lines(spec)
    out = [
        '<g fill="#12345c"><polygon points="1090,0 1130,0 1050,110 1010,110"/>'
        '<polygon points="1150,0 1200,0 1200,20 1125,110 1085,110"/>'
        '<polygon points="1200,640 1200,720 1150,800 1100,800"/>'
        '<polygon points="1075,800 1035,800 1105,700 1145,700"/></g>'
        '<rect x="870" y="110" width="140" height="96" fill="url(#dots)"/>'
        '<rect x="1000" y="650" width="120" height="74" fill="url(#dots)"/>'
        '<g stroke="#17406b" stroke-width="5" stroke-linecap="round">'
        '<path d="M1010 160H1180M1060 228H1180M40 772H150M0 150H40"/></g>'
    ]
    if spec.get("label"):
        out.append(
            f'<polygon points="48,70 648,70 608,140 48,140" fill="{grad}"/>'
            f'<g fill="{slash}"><polygon points="668,70 688,70 648,140 628,140"/>'
            f'<polygon points="708,70 724,70 684,140 668,140"/></g>'
        )
        out.append(t.add(spec["label"], 74, 124, 46, 500, weight=700, spacing=3))
    if len(lines) == 1:
        out.append(t.add(lines[0], 50, 284, 124, 1100, minimum=64))
        cve_y = 396
    else:
        out.append(t.add(lines[0], 50, 232, 84, 1100, minimum=52, group="title"))
        out.append(t.add(lines[1], 50, 322, 84, 660, minimum=52, group="title"))
        cve_y = 416
    box_y = cve_y + 32
    if spec.get("cve"):
        out.append(t.add(spec["cve"], 52, cve_y, 80, 670, minimum=44))
    else:
        box_y = cve_y - 60
    if spec.get("cvss"):
        cvss = str(spec["cvss"])
        box_w = 444 if len(cvss) <= 3 else 516
        out.append(
            f'<g filter="url(#sh)"><rect x="56" y="{box_y}" width="{box_w}" height="128" rx="22" '
            f'fill="{grad}" stroke="{"#ff6b85" if alert else "#67e8f9"}" stroke-width="5"/></g>'
        )
        out.append(t.add("CVSS", 92, box_y + 90, 66, 190))
        out.append(t.add(cvss, 296, box_y + 100, 104, box_w - 262))
    if spec.get("action"):
        out.append(gear(104, 676))
        out.append(t.add(accent_text(spec["action"], spec.get("action_accent", "")),
                         176, 700, 66, 826, weight=700, minimum=38, raw=True))
    out.append(art(spec, 756, 334))
    return "".join(out)


def layout_stack(spec: dict[str, Any], t: Texts) -> str:
    alert = spec["tone"] == "alert"
    rows: list[tuple[str, str, int, int]] = []
    lines = title_lines(spec)
    for line in lines:
        # タイトルはイラストより上に置くため全幅を使える。
        rows.append((line, WHITE, 80, 1100))
    if spec.get("cve"):
        rows.append((spec["cve"], CYAN, 84, 610))
    if spec.get("cvss"):
        rows.append((f'CVSS {spec["cvss"]}', RED if alert else CYAN, 84, 610))
    if spec.get("status"):
        rows.append((spec["status"], WHITE, 76, 610))
    if spec.get("action"):
        rows.append((spec["action"], GREEN, 76, 610))
    step = 104 if len(rows) <= 5 else 96
    first = 428 - (len(rows) - 1) * step / 2
    out = [
        '<rect width="1200" height="800" fill="url(#grid)" opacity=".7"/>'
        '<circle cx="930" cy="500" r="330" fill="url(#glow)"/>'
        '<g stroke="#17406b" stroke-width="5" stroke-linecap="round">'
        '<path d="M40 772H190M1010 772H1160"/></g>'
    ]
    for index, (text, color, size, fit) in enumerate(rows):
        out.append(t.add(text, 50, round(first + index * step), size, fit, fill=color, minimum=40,
                         group="title" if index < len(lines) else ""))
    art_y = round(first + step * 0.45) if len(lines) == 1 else round(first + step * 1.45)
    out.append(art(spec, 704, max(art_y, 250), 1.08))
    return "".join(out)


def layout_panel(spec: dict[str, Any], t: Texts) -> str:
    lines = title_lines(spec)
    out = [
        '<rect x="48" y="70" width="1108" height="672" fill="url(#grid)"/>',
        t.add(f'CYBERNOTE ｜ SECURITY NEWS{" ｜ " + spec["kicker_date"] if spec.get("kicker_date") else ""}',
              60, 62, 19, 700, weight=500, fill=CYAN, spacing=0.5, minimum=14),
    ]
    y = 182
    for line in lines:
        out.append(t.add(line, 60, y, 72, 620, weight=700, minimum=40, group="title"))
        y += 88
    y -= 6
    if spec.get("subtitle"):
        out.append(t.add(spec["subtitle"], 60, y, 62, 620, weight=700, fill=RED, minimum=36))
        y += 96
    if spec.get("figure"):
        out.append(t.add(spec["figure"], 60, y, 60, 620, weight=700, fill=CYAN, minimum=36))
        y += 62
    if spec.get("lead"):
        out.append(t.add(spec["lead"], 60, y, 44, 590, weight=700, minimum=28))
        y += 18
        out.append(f'<rect x="60" y="{y}" width="590" height="3" fill="{CYAN}"/>')
        y += 56
    if spec.get("note"):
        out.append(t.add(spec["note"], 62, y, 28, 590, weight=400, fill="#d3deea", minimum=20))
        y += 48
    for key, value, *rest in (spec.get("rows") or [])[:2]:
        color = COLORS.get(rest[0] if rest else "cyan", CYAN)
        out.append(
            f'<rect x="62" y="{y}" width="588" height="60" rx="10" fill="#10263f" stroke="#33506c" stroke-width="2"/>'
        )
        out.append(t.add(key, 82, y + 39, 23, 340, weight=400, fill="#d3deea", minimum=16))
        out.append(t.add(value, 630, y + 41, 29, 200, weight=700, fill=color, anchor="end", minimum=18))
        y += 74
    if y > 742:
        raise ValueError("panel の行が多すぎます。title・subtitle・figure・lead・note・rows を減らしてください")
    if spec.get("caption"):
        out.append(t.add(spec["caption"], 900, 712, 18, 360, weight=500, fill=RED, anchor="middle", minimum=13))
    if spec.get("source"):
        out.append(t.add(f'SOURCE: {spec["source"]}', 62, 764, 18, 900, weight=400, fill="#7f93a8", minimum=13))
    out.append(art(spec, 700, 232, 1.05))
    return "".join(out)


RENDERERS = {"banner": layout_banner, "stack": layout_stack, "panel": layout_panel}


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    spec = dict(spec)
    spec.setdefault("layout", "banner")
    spec.setdefault("tone", "alert")
    spec.setdefault("icon", "server")
    spec.setdefault("badge", "shield")
    if spec["layout"] not in LAYOUTS:
        raise ValueError(f'layout は {" / ".join(LAYOUTS)} のいずれかです: {spec["layout"]}')
    if spec["tone"] not in TONES:
        raise ValueError(f'tone は {" / ".join(TONES)} のいずれかです: {spec["tone"]}')
    if spec["icon"] not in ICONS:
        raise ValueError(f'icon は {" / ".join(ICONS)} のいずれかです: {spec["icon"]}')
    if spec["badge"] not in BADGES:
        raise ValueError(f'badge は {" / ".join(BADGES)} のいずれかです: {spec["badge"]}')
    lines = title_lines(spec) if spec.get("title") else []
    if not lines or not all(isinstance(x, str) and x.strip() for x in lines):
        raise ValueError("title が空です")
    if len(lines) > 2:
        raise ValueError("title は2行までです")
    return spec


def build_svg(spec: dict[str, Any]) -> str:
    spec = validate_spec(spec)
    texts = Texts()
    body = RENDERERS[spec["layout"]](spec, texts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family=\'{FONT_FAMILY}\'>{DEFS}'
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bg)"/>{body}</svg>'
    )


# ---------------------------------------------------------------- render

FIT_JS = """() => {
  const out = [];
  const all = [...document.querySelectorAll('text[data-fit]')];
  const groups = {};
  for (const t of all) {
    const max = +t.dataset.fit, min = +t.dataset.min;
    t.dataset.orig = t.getAttribute('font-size');
    let fs = parseFloat(t.dataset.orig);
    while (t.getComputedTextLength() > max && fs > min) { fs -= 1; t.setAttribute('font-size', fs); }
    const g = t.dataset.group;
    if (g) groups[g] = Math.min(groups[g] ?? fs, fs);
  }
  // 同じグループ（2行のタイトルなど）は、小さいほうの文字サイズにそろえる。
  for (const t of all) if (t.dataset.group) t.setAttribute('font-size', groups[t.dataset.group]);
  for (const t of all) {
    const max = +t.dataset.fit, orig = parseFloat(t.dataset.orig);
    const fs = parseFloat(t.getAttribute('font-size'));
    const r = t.getBoundingClientRect();
    out.push({id: t.id, text: t.textContent, orig, size: fs, width: Math.round(t.getComputedTextLength()),
              max, left: r.left, top: r.top, right: r.right, bottom: r.bottom});
  }
  // 影（filter）を含まない実体の矩形を、イラスト本体とバッジで別々に取る。
  const art = [...document.querySelectorAll('[data-art]')].map(e => {
    const a = e.getBoundingClientRect();
    return {left: a.left, top: a.top, right: a.right, bottom: a.bottom};
  });
  return {texts: out, art};
}"""


def check_font() -> str:
    """Noto Sans JP 系が入っていなければ、別フォントで描かれる前に止める。"""
    for family in ("Noto Sans JP", "Noto Sans CJK JP"):
        try:
            found = subprocess.run(
                ["fc-match", "-f", "%{family}", family],
                capture_output=True, text=True, timeout=20, check=False,
            ).stdout
        except (OSError, subprocess.SubprocessError):
            continue
        if family.lower() in found.lower():
            return family
    raise RuntimeError("Noto Sans JP / Noto Sans CJK JP が見つかりません。別フォントでは描画しません。")


def check_layout(report: dict[str, Any]) -> list[str]:
    problems = []
    for item in report["texts"]:
        name = f'「{item["text"]}」'
        if item["width"] > item["max"] + 1:
            problems.append(f'{name} が最小サイズでも枠に収まりません（{item["width"]}px > {item["max"]}px）。短くしてください')
        if (item["left"] < SAFE_MARGIN or item["top"] < SAFE_MARGIN
                or item["right"] > WIDTH - SAFE_MARGIN or item["bottom"] > HEIGHT - SAFE_MARGIN):
            problems.append(f"{name} が画面の端にかかっています")
        # 文字の矩形は行の高さ（字面より上下に広い）で返るため、その分だけ内側で判定する。
        inset = (item["bottom"] - item["top"]) * 0.14
        top, bottom = item["top"] + inset, item["bottom"] - inset
        for box in report["art"]:
            if (item["left"] < box["right"] and item["right"] > box["left"]
                    and top < box["bottom"] and bottom > box["top"]):
                problems.append(f"{name} がイラストに重なっています")
                break
    return problems


def render_png(svg: str) -> tuple[bytes, dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("playwright が必要です（pip install playwright）") from exc
    page_html = (
        '<!doctype html><html><head><meta charset="utf-8">'
        "<style>html,body{margin:0;background:#0a1c33}svg{display:block}</style></head>"
        f"<body>{svg}</body></html>"
    )
    with tempfile.TemporaryDirectory() as tmp:
        page_path = Path(tmp) / "eyecatch.html"
        page_path.write_text(page_html, encoding="utf-8")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
                page.goto(page_path.as_uri())
                page.evaluate("() => document.fonts.ready.then(() => true)")
                report = page.evaluate(FIT_JS)
                shot = page.screenshot(type="png", clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT})
            finally:
                browser.close()
    return shot, report


def validate_png_bytes(data: bytes) -> None:
    if not data.startswith(PNG_SIGNATURE):
        raise RuntimeError("PNG署名が不正です")
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        if image.format != "PNG" or image.size != (WIDTH, HEIGHT) or image.mode != "RGB":
            raise RuntimeError(f"画像仕様が不正です: format={image.format} size={image.size} mode={image.mode}")
    if len(data) > MAX_BYTES:
        raise RuntimeError(f"ファイルサイズが大きすぎます: {len(data):,}バイト")


def render(spec: dict[str, Any], output: Path, *, manifest: bool = True) -> dict[str, Any]:
    font = check_font()
    svg = build_svg(spec)
    shot, report = render_png(svg)
    problems = check_layout(report)
    if problems:
        raise RuntimeError("文字の配置に問題があるため保存しません:\n  - " + "\n  - ".join(problems))

    with Image.open(io.BytesIO(shot)) as image:
        image.load()
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, "PNG", optimize=True)
    data = buffer.getvalue()
    validate_png_bytes(data)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    validate_png_bytes(output.read_bytes())
    result = {
        "output": str(output), "bytes": len(data), "size": [WIDTH, HEIGHT], "mode": "RGB",
        "font": font, "layout": validate_spec(spec)["layout"],
        "texts": [
            {"text": item["text"], "font_size": item["size"], "shrunk": item["size"] < item["orig"]}
            for item in report["texts"]
        ],
    }
    if manifest:
        identity = write_manifest(output, source_visual_hash=visual_hash_bytes(shot),
                                  source_name="render_eyecatch.py")
        ok, detail = verify_manifest(output, identity)
        if not ok:
            output.unlink(missing_ok=True)
            manifest_path(output).unlink(missing_ok=True)
            raise RuntimeError(detail)
        result["identity"] = str(identity)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="アイキャッチをSVGで描画してPNGに書き出す")
    parser.add_argument("spec", help="指定JSONのパス")
    parser.add_argument("output", help="保存先PNGのパス")
    parser.add_argument("--no-manifest", action="store_true", help="identity manifest を書かない（試し描き用）")
    args = parser.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    try:
        result = render(spec, Path(args.output), manifest=not args.no_manifest)
    except (RuntimeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
