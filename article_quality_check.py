#!/usr/bin/env python3
"""後方互換用エントリポイント。

記事品質検査はCyberNote GEO/SEOルールを標準にする。
従来のコマンド名を残すため、このファイルから新チェッカーを呼び出す。
"""
from geo_article_quality_check import main


if __name__ == "__main__":
    raise SystemExit(main())
