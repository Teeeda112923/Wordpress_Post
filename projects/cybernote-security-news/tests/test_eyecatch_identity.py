import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from eyecatch_identity import (
    hash_distance,
    visual_hash_file,
    visually_same,
    verify_manifest,
    write_manifest,
)


class EyecatchIdentityTests(unittest.TestCase):
    def _image(self, path: Path, invert: bool = False) -> None:
        image = Image.new("RGB", (1200, 800), "white" if not invert else "black")
        draw = ImageDraw.Draw(image)
        for x in range(0, 1200, 120):
            fill = "black" if ((x // 120) % 2 == 0) ^ invert else "white"
            draw.rectangle((x, 0, x + 60, 800), fill=fill)
        draw.rectangle((140, 180, 920, 360), fill="gray")
        image.save(path, "PNG")

    def test_same_design_survives_png_resave(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = root / "a.png"
            b = root / "b.png"
            self._image(a)
            with Image.open(a) as image:
                image.resize((900, 600)).resize((1200, 800)).save(b, "PNG", optimize=True)
            left = visual_hash_file(a)
            right = visual_hash_file(b)
            self.assertTrue(visually_same(left, right), hash_distance(left, right))

    def test_different_design_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = root / "a.png"
            b = root / "b.png"
            self._image(a, False)
            self._image(b, True)
            self.assertFalse(visually_same(visual_hash_file(a), visual_hash_file(b)))

    def test_manifest_detects_file_replacement(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            image = root / "article.png"
            other = root / "other.png"
            self._image(image, False)
            self._image(other, True)
            source_hash = visual_hash_file(image)
            manifest = write_manifest(image, source_visual_hash=source_hash, source_name="generated.png")
            ok, _ = verify_manifest(image, manifest)
            self.assertTrue(ok)
            image.write_bytes(other.read_bytes())
            ok, detail = verify_manifest(image, manifest)
            self.assertFalse(ok)
            self.assertIn("SHA-256", detail)


if __name__ == "__main__":
    unittest.main()
