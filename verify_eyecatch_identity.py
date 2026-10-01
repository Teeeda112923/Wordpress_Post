#!/usr/bin/env python3
"""Verify generator->GitHub eyecatch identity for selected ledger rows."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
from pathlib import Path

from eyecatch_identity import manifest_path, verify_manifest


def parse_nos(raw: str) -> set[str]:
    values: set[str] = set()
    for part in (raw or "").replace("、", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, _, b = part.partition("-")
            if a.strip().isdigit() and b.strip().isdigit():
                values.update(str(i) for i in range(int(a), int(b) + 1))
        elif part.isdigit():
            values.add(str(int(part)))
    return values


def find_image(row: dict[str, str], images_dir: Path) -> Path | None:
    raw = (row.get("画像ファイル名") or "").strip()
    if not raw:
        return None
    p = Path(raw)
    candidates = [p, images_dir / p.name]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--images-dir", required=True)
    parser.add_argument("--nos", default="")
    parser.add_argument("--require-since", default="2026-10-01")
    args = parser.parse_args()

    wanted = parse_nos(args.nos)
    require_since = dt.date.fromisoformat(args.require_since)
    images_dir = Path(args.images_dir)
    with Path(args.ledger).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    errors = 0
    checked = 0
    for row in rows:
        no = str(row.get("No") or "").strip()
        if wanted and no not in wanted:
            continue
        raw_date = (row.get("収集日") or row.get("公開予定日") or "").strip()
        try:
            date = dt.date.fromisoformat(raw_date)
        except ValueError:
            date = dt.date.min
        image = find_image(row, images_dir)
        if image is None:
            if date >= require_since:
                print(f"[NG] No.{no}: 画像ファイルが見つかりません")
                errors += 1
            continue
        identity = manifest_path(image)
        if not identity.exists() and date < require_since:
            print(f"[LEGACY] No.{no}: identity対象導入前")
            continue
        checked += 1
        ok, detail = verify_manifest(image, identity)
        print(f"[{'OK' if ok else 'NG'}] No.{no}: {detail}")
        if not ok:
            errors += 1

    print(f"identity check: {checked}件 / errors={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
