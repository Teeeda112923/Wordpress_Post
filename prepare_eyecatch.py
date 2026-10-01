#!/usr/bin/env python3
"""Prepare a generated eyecatch and bind it to an identity manifest."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

from eyecatch_identity import visual_hash_file, write_manifest, verify_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="image generator output")
    parser.add_argument("output", help="repository PNG path")
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    if not source.exists():
        raise FileNotFoundError(source)
    source_visual = visual_hash_file(source)

    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image = ImageOps.fit(image, (1200, 800), method=Image.Resampling.LANCZOS)
        image.save(output, "PNG", optimize=True)

    manifest = write_manifest(
        output,
        source_visual_hash=source_visual,
        source_name=source.name,
    )
    ok, detail = verify_manifest(output, manifest)
    print(detail)
    print(f"image: {output}")
    print(f"identity: {manifest}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
