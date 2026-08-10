from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

import geo_article_quality_check as quality
import geo_meta
from generate_eyecatches import validate_png_bytes
from wp_auto_post import check_eyecatch


def valid_front(*, faq_count: int = 2, source_url: str = "https://nvd.nist.gov/vuln/detail/CVE-2026-12345") -> str:
    answer_text = "回" * 60
    conclusion = "結" * 39 + "。"
    faq = "\n".join(
        f'  - q: "質問{index}ですか？"\n    a: "{answer_text}"'
        for index in range(1, faq_count + 1)
    )
    return (
        f'answer: "{conclusion}"\n'
        'cve: "CVE-2026-12345"\n'
        f"faq:\n{faq}\n"
        "sources:\n"
        '  - title: "一次情報"\n'
        f'    url: "{source_url}"\n'
        '    publisher: "発行元"'
    )


def valid_body() -> str:
    links = (
        "[関連記事A](https://www.cybernote.click/a/)"
        "[関連記事B](https://www.cybernote.click/b/)"
        "[関連記事C](https://www.cybernote.click/c/)"
    )
    return (
        "# テスト記事\n\n"
        + "導" * 260
        + "\n\n"
        '<!-- wp:group {"className":"is-style-information-box"} -->\n'
        '<div class="wp-block-group is-style-information-box">参照\n'
        '<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cisa.gov/test"} /-->'
        "</div>\n"
        "<!-- /wp:group -->\n\n"
        "## 概要\n\n"
        + "影" * 110
        + links
        + "\n\n"
        + "詳" * 300
        + "\n\n"
        "## 対策\n\n"
        + "対" * 120
        + "\n\n"
        + "補" * 300
        + "\n\n"
        "## まとめ\n\n"
        + "総" * 270
    )


class QualityRuleTests(unittest.TestCase):
    def test_valid_article_passes(self) -> None:
        errors, warnings = quality.geo_errors(valid_front(), valid_body())
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_body_faq_and_reference_headings_are_rejected(self) -> None:
        body = valid_body().replace(
            "## まとめ", "## FAQ\n\n本文へ再掲したFAQです。\n\n## 参考情報\n\n本文へ再掲した出典です。\n\n## まとめ"
        )
        errors, _ = quality.geo_errors(valid_front(), body)
        self.assertIn("本文に禁止見出し『## FAQ』があります", errors)
        self.assertIn("本文に禁止見出し『## 参考情報』があります", errors)

        stripped, removed = geo_meta.strip_plugin_generated_sections(body)
        self.assertEqual(["FAQ", "参考情報"], removed)
        self.assertNotIn("## FAQ", stripped)
        self.assertNotIn("## 参考情報", stripped)
        self.assertIn("## まとめ", stripped)

    def test_summary_must_exist_exactly_once(self) -> None:
        missing = valid_body().replace("## まとめ\n\n" + "総" * 270, "")
        errors, _ = quality.geo_errors(valid_front(), missing)
        self.assertIn("## まとめが1件ではありません（0件）", errors)

        duplicate = valid_body() + "\n\n## まとめ\n\n" + "追" * 270
        errors, _ = quality.geo_errors(valid_front(), duplicate)
        self.assertIn("## まとめが1件ではありません（2件）", errors)

    def test_front_matter_requires_two_faqs_and_primary_source(self) -> None:
        errors, _ = quality.geo_errors(valid_front(faq_count=1), valid_body())
        self.assertIn("フロントマターfaqが2問未満です", errors)

        errors, _ = quality.geo_errors(
            valid_front(source_url="https://example.com/news"), valid_body()
        )
        self.assertIn("フロントマターsourcesに一次情報ドメインがありません", errors)

    def test_core_length_has_minimum_and_hard_maximum(self) -> None:
        short = valid_body().replace("詳" * 300, "詳" * 5).replace("補" * 300, "補" * 5)
        errors, _ = quality.geo_errors(valid_front(), short)
        self.assertTrue(
            any(error.startswith("本文コアが絶対最低値1000字未満") for error in errors)
        )

        long = valid_body().replace("詳" * 300, "詳" * 850)
        errors, _ = quality.geo_errors(valid_front(), long)
        self.assertTrue(
            any(error.startswith("本文コアが絶対上限1800字を超え") for error in errors)
        )

    def test_core_target_bands_warn_and_target_passes(self) -> None:
        self.assertEqual([], quality.geo_errors(valid_front(), valid_body())[1])

        below_target = valid_body().replace("詳" * 300, "詳" * 100)
        errors, warnings = quality.geo_errors(valid_front(), below_target)
        self.assertFalse(any("本文コア" in error for error in errors))
        self.assertTrue(any("目標1300〜1600字未満" in warning for warning in warnings))

        above_target = valid_body().replace("詳" * 300, "詳" * 550)
        errors, warnings = quality.geo_errors(valid_front(), above_target)
        self.assertFalse(any("本文コア" in error for error in errors))
        self.assertTrue(any("目標1300〜1600字を超え" in warning for warning in warnings))

    def test_duplicate_internal_links_are_rejected(self) -> None:
        body = valid_body().replace("https://www.cybernote.click/c/", "https://www.cybernote.click/a/")
        errors, _ = quality.geo_errors(valid_front(), body)
        self.assertTrue(any("同一CyberNote内部リンクが重複" in error for error in errors))

    def test_reference_blogcard_and_heading_rules(self) -> None:
        missing_blogcard = valid_body().replace(
            '<!-- wp:cocoon-blocks/embed-blogcard {"url":"https://www.cisa.gov/test"} /-->',
            "",
        )
        errors, _ = quality.geo_errors(valid_front(), missing_blogcard)
        self.assertIn("Cocoon参照ブログカードが1個ではありません（0個）", errors)

        duplicate_heading = valid_body().replace("## 対策", "## 概要")
        errors, _ = quality.geo_errors(valid_front(), duplicate_heading)
        self.assertIn("同じ見出しが複数あります（概要）", errors)

        summary_alias = valid_body().replace("## 対策", "## 結論")
        errors, _ = quality.geo_errors(valid_front(), summary_alias)
        self.assertIn("本文に禁止見出し『## 結論』があります", errors)


class CyberNoteImageRuleTests(unittest.TestCase):
    def test_strict_png_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            images_dir = Path(temp_dir) / "cybernote-security-news" / "eyecatches"
            images_dir.mkdir(parents=True)

            valid = images_dir / "001.png"
            Image.new("RGB", (1200, 800), "navy").save(valid, "PNG")
            validate_png_bytes(valid.read_bytes())
            self.assertEqual("OK", check_eyecatch(valid, "1", images_dir)["level"])

            wrong_size = images_dir / "002.png"
            Image.new("RGB", (900, 600), "navy").save(wrong_size, "PNG")
            self.assertEqual("NG", check_eyecatch(wrong_size, "2", images_dir)["level"])

            broken = images_dir / "003.png"
            broken.write_bytes(b"not-a-png")
            result = check_eyecatch(broken, "3", images_dir)
            self.assertEqual("NG", result["level"])
            self.assertIn("PNG署名", result["error_content"])
            with self.assertRaisesRegex(RuntimeError, "PNG署名"):
                validate_png_bytes(broken.read_bytes())


if __name__ == "__main__":
    unittest.main()
