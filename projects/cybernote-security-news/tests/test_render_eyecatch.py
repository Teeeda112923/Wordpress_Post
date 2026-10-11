"""render_eyecatch.py のうち、ブラウザを使わない部分の検査。

描画そのもの（Chromium）はCIに入れていないため、ここではSVGの組み立てと
配置検査の判定だけを確かめる。
"""
import unittest
import xml.etree.ElementTree as ET

from render_eyecatch import ICONS, LAYOUTS, build_svg, check_layout, validate_spec

BASE = {
    "layout": "banner", "tone": "alert", "label": "緊急セキュリティ更新",
    "title": "Windows RDS", "cve": "CVE-2026-69525", "cvss": "9.8",
    "action": "2026年9月の累積更新を適用", "action_accent": "2026年9月",
    "icon": "monitor", "badge": "shield",
}


def text_of(svg: str) -> str:
    return "".join(ET.fromstring(svg).itertext())


class RenderEyecatchTests(unittest.TestCase):
    def test_every_layout_and_icon_builds_wellformed_svg(self) -> None:
        for layout in LAYOUTS:
            for icon in ICONS:
                svg = build_svg({**BASE, "layout": layout, "icon": icon})
                root = ET.fromstring(svg)
                self.assertEqual(root.get("width"), "1200")
                self.assertEqual(root.get("height"), "800")

    def test_text_is_written_exactly_as_given(self) -> None:
        text = text_of(build_svg(BASE))
        for expected in ("Windows RDS", "CVE-2026-69525", "9.8", "2026年9月の累積更新を適用"):
            self.assertIn(expected, text)

    def test_markup_in_text_is_escaped(self) -> None:
        svg = build_svg({**BASE, "title": 'A&B <script>"x"'})
        self.assertNotIn("<script>", svg)
        self.assertIn('A&B <script>"x"', text_of(svg))

    def test_invalid_spec_is_rejected(self) -> None:
        for bad in ({"layout": "collage"}, {"icon": "logo"}, {"badge": "star"},
                    {"tone": "pink"}, {"title": ""}, {"title": ["a", "b", "c"]}):
            with self.assertRaises(ValueError):
                validate_spec({**BASE, **bad})

    def test_layout_check_reports_overflow_edge_and_overlap(self) -> None:
        art = [{"left": 756, "top": 334, "right": 1080, "bottom": 616}]

        def item(**kw):
            base = {"text": "x", "width": 100, "max": 200, "left": 50, "top": 100,
                    "right": 150, "bottom": 160, "size": 60, "orig": 60}
            return {**base, **kw}

        self.assertEqual(check_layout({"texts": [item()], "art": art}), [])
        self.assertTrue(check_layout({"texts": [item(width=300)], "art": art}))
        self.assertTrue(check_layout({"texts": [item(right=1190)], "art": art}))
        self.assertTrue(check_layout({"texts": [item(left=700, right=900, top=400, bottom=470)], "art": art}))


if __name__ == "__main__":
    unittest.main()
