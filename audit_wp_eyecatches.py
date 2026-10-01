#!/usr/bin/env python3
"""Audit published CyberNote featured images against repository eyecatches."""
from __future__ import annotations

import argparse
import base64
import csv
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from eyecatch_identity import hash_distance, visual_hash_bytes, visual_hash_file, visually_same


def auth_header(username: str, app_password: str) -> dict[str, str]:
    token = base64.b64encode(
        f"{username}:{app_password.replace(' ', '')}".encode("utf-8")
    ).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def chunks(values: list[int], size: int = 100):
    for i in range(0, len(values), size):
        yield values[i:i + size]


def extra_headers() -> dict[str, str]:
    raw = os.environ.get("WP_EXTRA_HEADERS", "")
    headers: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        if name.strip() and value.strip():
            headers[name.strip()] = value.strip()
    return headers


def api_get(session: requests.Session, api_base: str, endpoint: str, params: dict[str, Any]):
    response = session.get(f"{api_base}/{endpoint.lstrip('/')}", params=params, timeout=90)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise RuntimeError(f"{endpoint} returned non-list response")
    return data


def find_local_image(row: dict[str, str], images_dir: Path) -> Path | None:
    raw = (row.get("画像ファイル名") or "").strip()
    if not raw:
        return None
    p = Path(raw)
    for candidate in (p, images_dir / p.name):
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--images-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sleep", type=float, default=0.08)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    base_url = os.environ["WP_BASE_URL"].rstrip("/")
    api_base = f"{base_url}/wp-json/wp/v2"
    session = requests.Session()
    session.headers.update(auth_header(os.environ["WP_USERNAME"], os.environ["WP_APP_PASSWORD"]))
    session.headers.update({
        "User-Agent": os.environ.get("WP_USER_AGENT", "").strip() or "CyberNote-Eyecatch-Audit/1.0",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
    })
    session.headers.update(extra_headers())

    with Path(args.ledger).open(encoding="utf-8-sig", newline="") as handle:
        ledger_rows = list(csv.DictReader(handle))

    candidates: list[dict[str, Any]] = []
    for row in ledger_rows:
        if (row.get("投稿ステータス") or "").strip() != "公開済み":
            continue
        post_id_raw = (row.get("WP投稿ID") or "").strip()
        if not post_id_raw.isdigit():
            continue
        image = find_local_image(row, Path(args.images_dir))
        if image is None:
            continue
        candidates.append({
            "no": (row.get("No") or "").strip(),
            "title": (row.get("記事タイトル") or row.get("記事タイトル案") or "").strip(),
            "post_id": int(post_id_raw),
            "expected_image": image,
            "post_url": (row.get("WP投稿URL") or "").strip(),
        })

    if args.limit > 0:
        candidates = candidates[-args.limit:]

    post_ids = [item["post_id"] for item in candidates]
    posts: dict[int, dict[str, Any]] = {}
    for group in chunks(post_ids):
        data = api_get(
            session, api_base, "posts",
            {
                "include": ",".join(map(str, group)),
                "per_page": len(group),
                "status": "publish",
                "context": "edit",
                "_fields": "id,featured_media,slug,link",
            },
        )
        for item in data:
            posts[int(item["id"])] = item

    media_ids = sorted({
        int(posts[item["post_id"]].get("featured_media") or 0)
        for item in candidates
        if item["post_id"] in posts and int(posts[item["post_id"]].get("featured_media") or 0)
    })
    media: dict[int, dict[str, Any]] = {}
    for group in chunks(media_ids):
        data = api_get(
            session, api_base, "media",
            {
                "include": ",".join(map(str, group)),
                "per_page": len(group),
                "context": "edit",
                "_fields": "id,source_url,slug",
            },
        )
        for item in data:
            media[int(item["id"])] = item

    results: list[dict[str, Any]] = []
    mismatch_count = 0
    for item in candidates:
        no = item["no"]
        post = posts.get(item["post_id"])
        expected = item["expected_image"]
        result = {
            "no": no,
            "title": item["title"],
            "post_id": item["post_id"],
            "post_url": item["post_url"],
            "expected_image": str(expected),
            "featured_media": "",
            "media_url": "",
            "visual_distance": "",
            "status": "",
            "detail": "",
        }
        if not post:
            result["status"] = "post-missing"
            result["detail"] = "WordPress投稿を取得できません"
            mismatch_count += 1
            results.append(result)
            continue

        fm = int(post.get("featured_media") or 0)
        result["featured_media"] = fm
        if not fm:
            result["status"] = "no-featured-image"
            result["detail"] = "featured_mediaが未設定です"
            mismatch_count += 1
            results.append(result)
            continue

        media_item = media.get(fm)
        if not media_item:
            result["status"] = "media-missing"
            result["detail"] = f"media id={fm}を取得できません"
            mismatch_count += 1
            results.append(result)
            continue

        source_url = str(media_item.get("source_url") or "")
        result["media_url"] = source_url
        try:
            remote = requests.get(
                source_url,
                headers={
                    "User-Agent": session.headers.get("User-Agent", "CyberNote-Eyecatch-Audit/1.0"),
                    "Accept": "image/*",
                    "Cache-Control": "no-cache",
                },
                timeout=90,
            )
            remote.raise_for_status()
            local_hash = visual_hash_file(expected)
            remote_hash = visual_hash_bytes(remote.content)
            distance = hash_distance(local_hash, remote_hash)
            result["visual_distance"] = distance
            if visually_same(local_hash, remote_hash):
                result["status"] = "ok"
                result["detail"] = f"visual hash一致（distance={distance}）"
            else:
                result["status"] = "mismatch"
                result["detail"] = f"画像内容が不一致（distance={distance}）"
                mismatch_count += 1
        except Exception as exc:
            result["status"] = "compare-error"
            result["detail"] = f"{type(exc).__name__}: {exc}"
            mismatch_count += 1
        results.append(result)
        time.sleep(max(args.sleep, 0.0))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(output, index=False, encoding="utf-8-sig")

    print(f"監査対象: {len(results)}件 / 問題: {mismatch_count}件")
    for row in results:
        if row["status"] != "ok":
            print(
                f"[NG] No.{row['no']} post={row['post_id']} "
                f"media={row['featured_media']} {row['status']}: {row['detail']}"
            )
    print(f"監査CSV: {output}")
    return 1 if mismatch_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
