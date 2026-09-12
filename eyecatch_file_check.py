#!/usr/bin/env python3
"""アイキャッチ画像が壊れていないかを検査する。

Image.open() はヘッダ（PNGならIHDR）しか読まないため、画素データが途中で
切れていても形式とサイズは取得できてしまう。load() で実体まで読み切って検証する。

壊れた画像をWordPressへ送るとサムネイル生成でPHP致命的エラーになり、
投稿枠が失敗し続ける。投稿時にも wp_auto_post.check_eyecatch() で弾いているが、
それでは枠を消費するまで気づけない（実際に丸1日以上、毎枠失敗し続けた）。
コミットの時点で止めるために、この検査を単体で走らせられるようにしている。

使い方:
    python eyecatch_file_check.py                    # 既定のeyecatchesディレクトリを全部
    python eyecatch_file_check.py path/to/dir a.png  # 対象を指定
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 実測: 途中で切れたファイルはすべて 768 KiB 境界（786,432バイト）の直後で終わっていた。
# 同じ位置で切れていれば、生成側ではなく保存・転送の工程が原因だと分かる。
TRUNCATE_BOUNDARY = 768 * 1024
TRUNCATE_MARGIN = 64

# 意図的に壊れたまま残している画像。既存成果物は変更しない方針のため、
# 検査対象から外して「新しく壊れた画像」だけを検出できるようにする。
#
# この検査は、壊れた画像を投稿前に止めるためにある。常に赤いままだと
# 新しく壊れた画像が混ざっても気づけず、警報として機能しなくなる。
# 除外した枚数と名前は必ずログに出し、黙って無視しない。
KNOWN_BROKEN = {
    # 同一CVEの記事がmainにあるため重複除外された。既存成果物として保持する。
    "microsoft-entra-id-cve-2026-62916-authentication-bypass.png",
    # 使い捨てワークフローで公開済み。管理簿に行がなく、投稿処理からは参照されない。
    "m-trends-2026-cyberattack-22-seconds.png",
}


def collect(targets: list[str]) -> list[Path]:
    """検査対象のPNGを集める。指定がなければ eyecatches ディレクトリを探す。

    KNOWN_BROKEN のファイルは含めない。ファイル名だけで判定するため、
    同名のファイルを別ディレクトリに置いた場合も除外される。
    """
    paths: list[Path] = []
    if targets:
        for target in targets:
            path = Path(target)
            if path.is_dir():
                paths += sorted(path.rglob("*.png"))
            elif path.is_file():
                paths.append(path)
    else:
        for directory in sorted(Path(".").rglob("eyecatches")):
            # リポジトリ直下に同名のファイルがあるためディレクトリだけを見る
            if directory.is_dir() and ".git" not in directory.parts:
                paths += sorted(directory.rglob("*.png"))
    return [path for path in paths if path.name not in KNOWN_BROKEN]


def failure_reason(path: Path) -> str:
    """読み込めない理由を返す（問題なければ空文字）。"""
    from PIL import Image  # 遅延 import

    try:
        with Image.open(path) as image:
            image.format, image.size
        with Image.open(path) as image:
            image.load()  # 画素データまで読み切る
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="アイキャッチ画像の破損を検査する")
    parser.add_argument("targets", nargs="*", help="ファイルまたはディレクトリ")
    args = parser.parse_args()

    paths = collect(args.targets)
    if KNOWN_BROKEN:
        print(f"意図的に検査から外している画像: {len(KNOWN_BROKEN)}件")
        for name in sorted(KNOWN_BROKEN):
            print(f"  - {name}")
    if not paths:
        print("検査対象のPNGが見つかりません。")
        return 0

    broken: list[tuple[Path, int, str]] = []
    for path in paths:
        size = path.stat().st_size
        reason = failure_reason(path)
        if reason:
            broken.append((path, size, reason))
            print(f"[NG] {path} ({size:,}バイト) {reason}")

    print(f"検査: {len(paths)}件 / 破損: {len(broken)}件")
    if not broken:
        print("すべて問題ありません。")
        return 0

    print("\n壊れた画像はWordPressへ送れません。作り直してから入れ直してください。")
    if any(
        TRUNCATE_BOUNDARY <= size <= TRUNCATE_BOUNDARY + TRUNCATE_MARGIN
        for _, size, _ in broken
    ):
        print(
            f"※ 768 KiB（{TRUNCATE_BOUNDARY:,}バイト）の直後で切れています。"
            "画像そのものではなく、保存・転送の工程で切られている可能性が高いです。"
            "圧縮して768 KiB未満にすると回避できます。"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
