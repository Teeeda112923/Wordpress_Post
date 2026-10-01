#!/usr/bin/env python3
"""CyberNote eyecatch identity helpers.

The goal is to preserve the visual identity of the image produced by the image
generator through resize/PNG preparation, GitHub storage, and WordPress reuse.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

IDENTITY_SUFFIX = ".identity.json"
DEFAULT_HASH_SIZE = 16
DEFAULT_DISTANCE_LIMIT = 18
MEDIA_SHA_PREFIX = "cybernote-sha256:"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def visual_hash_image(image: Image.Image, hash_size: int = DEFAULT_HASH_SIZE) -> str:
    """Difference hash resilient to PNG recompression and small resizes."""
    gray = ImageOps.exif_transpose(image).convert("L")
    resized = gray.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(resized.getdata())
    bits = []
    for y in range(hash_size):
        row = y * (hash_size + 1)
        for x in range(hash_size):
            bits.append(pixels[row + x] > pixels[row + x + 1])
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    width = (len(bits) + 3) // 4
    return f"{value:0{width}x}"


def visual_hash_bytes(data: bytes) -> str:
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        return visual_hash_image(image)


def visual_hash_file(path: Path) -> str:
    with Image.open(path) as image:
        image.load()
        return visual_hash_image(image)


def hash_distance(left: str, right: str) -> int:
    if not left or not right or len(left) != len(right):
        return 10**9
    return (int(left, 16) ^ int(right, 16)).bit_count()


def visually_same(left: str, right: str, limit: int = DEFAULT_DISTANCE_LIMIT) -> bool:
    return hash_distance(left, right) <= limit


def media_sha_marker(sha256: str) -> str:
    return f"{MEDIA_SHA_PREFIX}{sha256}"


def extract_media_sha(value: str) -> str:
    text = value or ""
    marker = text.lower().find(MEDIA_SHA_PREFIX)
    if marker < 0:
        return ""
    candidate = text[marker + len(MEDIA_SHA_PREFIX): marker + len(MEDIA_SHA_PREFIX) + 64]
    return candidate if len(candidate) == 64 and all(c in "0123456789abcdef" for c in candidate) else ""


def manifest_path(image_path: Path) -> Path:
    return image_path.with_name(image_path.name + IDENTITY_SUFFIX)


def read_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(
    image_path: Path,
    *,
    source_visual_hash: str,
    source_name: str = "",
) -> Path:
    final_visual_hash = visual_hash_file(image_path)
    payload = {
        "version": 1,
        "source_name": source_name,
        "source_visual_hash": source_visual_hash,
        "final_visual_hash": final_visual_hash,
        "final_sha256": sha256_file(image_path),
        "width": 1200,
        "height": 800,
    }
    out = manifest_path(image_path)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def verify_manifest(image_path: Path, identity_path: Path | None = None) -> tuple[bool, str]:
    identity_path = identity_path or manifest_path(image_path)
    if not identity_path.exists():
        return False, f"identity manifest がありません: {identity_path}"
    try:
        data = read_manifest(identity_path)
    except Exception as exc:
        return False, f"identity manifest を読めません: {exc}"
    actual_sha = sha256_file(image_path)
    if actual_sha != str(data.get("final_sha256") or ""):
        return False, "GitHub登録画像のSHA-256が生成時manifestと一致しません"
    actual_visual = visual_hash_file(image_path)
    if actual_visual != str(data.get("final_visual_hash") or ""):
        return False, "GitHub登録画像の視覚ハッシュが生成時manifestと一致しません"
    source_visual = str(data.get("source_visual_hash") or "")
    distance = hash_distance(source_visual, actual_visual)
    if distance > DEFAULT_DISTANCE_LIMIT:
        return False, f"生成元とGitHub登録画像のデザインが一致しません（distance={distance}）"
    try:
        with Image.open(image_path) as image:
            image.load()
            size = image.size
            fmt = image.format
    except Exception as exc:
        return False, f"画像を読めません: {exc}"
    if fmt != "PNG" or size != (1200, 800):
        return False, f"画像仕様が不正です: format={fmt} size={size}"
    return True, f"identity OK（source distance={distance}, sha256={actual_sha[:12]}…）"
