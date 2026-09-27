"""当日分が無いときに、直近の未投稿をさかのぼって拾えるかの回帰テスト。

公開予定日を過ぎた記事は誰も拾わないため、放っておくと永久に投稿されずに残る。
実際に9本が取り残された。当日分を最優先しつつ、空振りする枠だけを
取りこぼしの回収に充てる、という動きを固定する。
"""
from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[3]
SELECT_NEWS = REPO_ROOT / "projects" / "cybernote-security-news" / "src" / "select_news.py"

COLUMNS = [
    "No", "公開予定日", "話題性スコア", "記事タイトル", "スラッグ",
    "記事ファイル", "画像ファイル名", "生成ステータス", "投稿ステータス",
]


class FallbackSelectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.articles = self.base / "articles"
        self.images = self.base / "eyecatches"
        self.articles.mkdir()
        self.images.mkdir()
        self.ledger = self.base / "ledger.csv"
        self.addCleanup(self._tmp.cleanup)

    def _add(self, no: str, date: str, score: str, status: str = "") -> dict[str, str]:
        """記事本文とアイキャッチを実体として置き、台帳の1行を返す。"""
        slug = f"article-{no}"
        (self.articles / f"{slug}.md").write_text("# 見出し\n本文\n", encoding="utf-8")
        Image.new("RGB", (1200, 800), "navy").save(self.images / f"{slug}.png")
        return {
            "No": no, "公開予定日": date, "話題性スコア": score,
            "記事タイトル": f"記事{no}", "スラッグ": slug,
            "記事ファイル": "", "画像ファイル名": "",
            "生成ステータス": "生成済み", "投稿ステータス": status,
        }

    def _write(self, rows: list[dict[str, str]]) -> None:
        with self.ledger.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def _select(self, date: str, fallback_days: int) -> str:
        # 品質チェックは本物の記事を必要とするため、ここでは選択の日付の動きだけを見る
        result = subprocess.run(
            [
                sys.executable, str(SELECT_NEWS),
                "--ledger", str(self.ledger),
                "--repo-root", str(self.base),
                "--articles-dir", str(self.articles),
                "--eyecatches-dir", str(self.images),
                "--date", date,
                "--stage", "draft",
                "--with-date",
                "--fallback-days", str(fallback_days),
            ],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()

    def test_当日分があればそのまま選ぶ(self) -> None:
        self._write([
            self._add("1", "2026-09-01", "90"),
            self._add("2", "2026-08-30", "99"),
        ])
        self.assertEqual(self._select("2026-09-01", 3), "1\t2026-09-01")

    def test_当日分が無ければさかのぼって拾う(self) -> None:
        self._write([self._add("2", "2026-08-30", "99")])
        self.assertEqual(self._select("2026-09-01", 3), "2\t2026-08-30")

    def test_さかのぼりは新しい日付を優先する(self) -> None:
        self._write([
            self._add("2", "2026-08-30", "50"),
            self._add("3", "2026-08-29", "99"),
        ])
        # スコアが低くても、より新しい8/30を先に拾う（鮮度を優先する）
        self.assertEqual(self._select("2026-09-01", 3), "2\t2026-08-30")

    def test_範囲外までは拾わない(self) -> None:
        self._write([self._add("4", "2026-08-20", "99")])
        self.assertEqual(self._select("2026-09-01", 3), "")

    def test_投稿済みは拾わない(self) -> None:
        self._write([self._add("5", "2026-08-31", "99", status="公開済み")])
        self.assertEqual(self._select("2026-09-01", 3), "")

    def test_さかのぼり無効なら当日だけを見る(self) -> None:
        self._write([self._add("2", "2026-08-31", "99")])
        self.assertEqual(self._select("2026-09-01", 0), "")


if __name__ == "__main__":
    unittest.main()
