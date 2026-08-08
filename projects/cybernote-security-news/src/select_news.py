#!/usr/bin/env python3
"""ニュース管理簿から当日処理する記事を1件選ぶ。"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import math
import sys
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")

READY_VALUES = {
    "生成済み",
    "作成済み",
    "ready",
    "generated",
    "draft_ready",
}
BLOCKED_VALUES = {
    "停止",
    "中止",
    "除外",
    "cancel",
    "cancelled",
    "stop",
    "stopped",
    "no",
    "false",
    "0",
}
PUBLISHED_VALUES = {
    "公開済み",
    "published",
    "publish",
    "posted",
}
DRAFT_VALUES = {
    "下書き済み",
    "下書き",
    "draft",
    "drafted",
}


def value(row: dict[str, str], *names: str) -> str:
    for name in names:
        raw = row.get(name)
        if raw is not None and str(raw).strip():
            return str(raw).strip()
    return ""


def normalized(raw: Any) -> str:
    return str(raw or "").strip().lower().replace(" ", "").replace("　", "")


def is_blocked(raw: Any) -> bool:
    return normalized(raw) in {normalized(item) for item in BLOCKED_VALUES}


def is_published(raw: Any) -> bool:
    return normalized(raw) in {normalized(item) for item in PUBLISHED_VALUES}


def is_draft(raw: Any) -> bool:
    return normalized(raw) in {normalized(item) for item in DRAFT_VALUES}


def numeric_score(raw: Any) -> float:
    try:
        score = float(str(raw or "").replace(",", "").strip())
        return score if math.isfinite(score) else 0.0
    except (TypeError, ValueError):
        return 0.0


def no_key(raw: Any) -> tuple[int, str]:
    text = str(raw or "").strip()
    try:
        return int(float(text)), text
    except (TypeError, ValueError):
        return 10**9, text


def read_ledger(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"管理簿が見つかりません: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle) if any(row.values())]


def resolve_path(repo_root: Path, raw_path: str, fallback_dir: Path, filename: str) -> Path | None:
    candidates: list[Path] = []
    if raw_path:
        raw = Path(raw_path)
        candidates.append(raw if raw.is_absolute() else repo_root / raw)
        candidates.append(fallback_dir / raw.name)
    if filename:
        candidates.append(fallback_dir / filename)
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def quality_errors(repo_root: Path, article_path: Path) -> list[str]:
    """記事品質チェックでエラーになる項目を返す（判定できなければ空リスト）。

    投稿を止めるほどの不備がある記事を選んでしまうと、その枠は必ず失敗して
    1件も投稿されない。同じ日に問題のない記事があるなら、そちらを選ぶ。
    チェッカーを呼べない場合は選択を止めず、従来どおり後段の品質ゲートに任せる。
    """
    try:
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        import geo_article_quality_check as checker
    except Exception as exc:  # チェッカーが無い・読めない
        print(f"品質チェックを省略します（{exc}）", file=sys.stderr)
        return []
    try:
        front, body, front_errors = checker.split_front_matter(
            article_path.read_text(encoding="utf-8")
        )
        if front_errors:
            return front_errors
        errors, _ = checker.geo_errors(front, body)
        return errors
    except Exception as exc:
        print(f"品質チェックに失敗しました（{article_path}: {exc}）", file=sys.stderr)
        return []


def image_errors(repo_root: Path, image_path: Path) -> list[str]:
    """アイキャッチ画像が投稿できない状態かを返す（判定できなければ空リスト）。

    記事本文が整っていても画像が壊れていれば投稿は必ず失敗する。実際、記事だけを
    見て選んでいたため、画像が壊れた記事が毎枠選ばれ続けて投稿が止まった。
    判定を1か所に保つため、投稿時と同じ check_eyecatch() を使う。
    """
    try:
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from wp_auto_post import check_eyecatch
    except Exception as exc:
        print(f"画像チェックを省略します（{exc}）", file=sys.stderr)
        return []
    try:
        result = check_eyecatch(image_path, "", image_path.parent)
        return [result["error_content"]] if result["level"] == "NG" else []
    except Exception as exc:
        print(f"画像チェックに失敗しました（{image_path}: {exc}）", file=sys.stderr)
        return []


def select_row(
    rows: list[dict[str, str]],
    target_date: str,
    stage: str,
    repo_root: Path,
    articles_dir: Path,
    eyecatches_dir: Path,
    forced_no: str = "",
    skip_quality_error: bool = False,
) -> dict[str, str] | None:
    candidates: list[tuple[dict[str, str], Path, Path]] = []

    for row in rows:
        row_no = value(row, "No", "番号", "記事No", "ID")
        if forced_no and row_no.lstrip("0") != forced_no.lstrip("0"):
            continue

        if value(row, "公開予定日", "公開日", "publish_date") != target_date:
            continue

        if is_blocked(value(row, "公開停止", "停止フラグ", "stop")):
            continue
        if is_blocked(value(row, "レビュー判定", "review", "review_status")):
            continue

        generation_status = normalized(
            value(row, "生成ステータス", "記事生成ステータス", "generation_status")
        )
        if generation_status and generation_status not in {
            normalized(item) for item in READY_VALUES
        }:
            continue

        title = value(row, "記事タイトル", "記事タイトル案", "タイトル", "title")
        slug = value(row, "スラッグ", "slug")
        article_file = value(row, "記事ファイル", "article_file")
        image_file = value(row, "画像ファイル名", "画像ファイル", "image_file")
        if not title or not row_no:
            continue

        article_path = resolve_path(
            repo_root,
            article_file,
            articles_dir,
            f"{slug}.md" if slug else f"{int(float(row_no)):03d}.md",
        )
        image_path = resolve_path(
            repo_root,
            image_file,
            eyecatches_dir,
            f"{slug}.png" if slug else f"{int(float(row_no)):03d}.png",
        )
        if article_path is None or image_path is None:
            continue

        post_status = normalized(value(row, "投稿ステータス", "post_status"))
        # draft段階では、既に下書き作成済み・公開済みの行を再処理しない。
        # （2段階運用をやめたため publish段階は無くなったが、下書き済みの行が
        #   台帳に残っていても再投稿しないよう is_draft の判定は残す）
        if stage == "draft":
            if is_draft(post_status) or is_published(post_status):
                continue

        candidates.append((row, article_path, image_path))

    candidates.sort(
        key=lambda item: (
            -numeric_score(value(item[0], "話題性スコア", "topic_score")),
            no_key(value(item[0], "No", "番号", "記事No", "ID")),
        )
    )
    if not skip_quality_error:
        return candidates[0][0] if candidates else None

    # 話題性スコアの高い順に見て、記事も画像も問題ない最初の記事を選ぶ。
    # スコア1位に不備があるだけで、その枠が丸ごと落ちるのを避ける。
    for row, article_path, image_path in candidates:
        issues = quality_errors(repo_root, article_path)
        issues += image_errors(repo_root, image_path)
        if not issues:
            return row
        row_no = value(row, "No", "番号", "記事No", "ID")
        print(
            f"投稿できないためスキップ: No.{row_no}"
            f"（{len(issues)}件）{' / '.join(issues[:3])}",
            file=sys.stderr,
        )
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="当日のニュース記事を1件選択する")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--articles-dir", required=True)
    parser.add_argument("--eyecatches-dir", required=True)
    parser.add_argument("--date", default="")
    # draft は「まだ投稿していない行を選ぶ」の意味（下書き投稿という意味ではない）
    parser.add_argument("--stage", choices=["draft"], required=True)
    parser.add_argument("--no", default="")
    parser.add_argument(
        "--skip-quality-error",
        action="store_true",
        help="品質チェックでエラーになる記事は選ばず、次点の記事を選ぶ",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    target_date = args.date.strip() or dt.datetime.now(JST).date().isoformat()
    row = select_row(
        read_ledger(repo_root / args.ledger),
        target_date,
        args.stage,
        repo_root,
        repo_root / args.articles_dir,
        repo_root / args.eyecatches_dir,
        args.no,
        args.skip_quality_error,
    )
    if row is None:
        print(
            f"処理対象なし: date={target_date}, stage={args.stage}",
            file=sys.stderr,
        )
        return 0

    print(value(row, "No", "番号", "記事No", "ID"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
