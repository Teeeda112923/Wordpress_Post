#!/usr/bin/env python3
"""制作管理表とMarkdownを照合し、記事の文字数と基本構成を検査する。"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any

import pandas as pd

CANDIDATES = {
    "no": ["No", "番号", "記事No", "ID"],
    "title": ["記事タイトル案", "記事タイトル", "タイトル"],
    "slug": ["スラッグ", "slug"],
    "target": ["文字数目安", "目標文字数", "文字数"],
    "cta": ["CTA強度", "CTA"],
    "status": ["執筆ステータス", "ステータス"],
}


def text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def column(columns: list[str], names: list[str]) -> str | None:
    normalized = {str(c).strip().lower(): c for c in columns}
    for name in names:
        if name.lower() in normalized:
            return normalized[name.lower()]
    for name in names:
        for key, original in normalized.items():
            if name.lower() in key or key in name.lower():
                return original
    return None


def number(value: Any) -> int | None:
    try:
        return int(float(text(value)))
    except ValueError:
        return None


def selected_nos(spec: str) -> set[int] | None:
    if not spec.strip():
        return None
    result: set[int] = set()
    for part in re.split(r"[,、\s]+", spec.strip()):
        match = re.match(r"^(\d+)\s*[-~〜]\s*(\d+)$", part)
        if match:
            a, b = map(int, match.groups())
            result.update(range(min(a, b), max(a, b) + 1))
        elif part.isdigit():
            result.add(int(part))
    return result or None


def target_range(value: str, tolerance: float) -> tuple[int | None, int | None]:
    nums = [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", value)]
    if not nums:
        return None, None
    if len(nums) > 1:
        return min(nums), max(nums)
    center = nums[0]
    return int(center * (1 - tolerance)), int(center * (1 + tolerance) + 0.999)


def strip_front_matter(md: str) -> str:
    lines = md.lstrip("\ufeff").splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:])
    return "\n".join(lines)


def strip_h1(md: str) -> str:
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if not line.strip() or line.lstrip().startswith("<!--"):
            continue
        if re.match(r"^#\s+\S", line) and not line.startswith("##"):
            del lines[i]
        break
    return "\n".join(lines)


def plain(md: str) -> str:
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = re.sub(r"`([^`]*)`", r"\1", md)
    md = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", md)
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"https?://\S+|<[^>]+>", "", md)
    md = re.sub(r"^\s{0,3}#{1,6}\s*", "", md, flags=re.M)
    md = re.sub(r"^\s*[-*+]\s+|^\s*\d+[.)]\s+", "", md, flags=re.M)
    md = re.sub(r"^\s*\|?[-:| ]+\|?\s*$", "", md, flags=re.M)
    return re.sub(r"[*_~>#|&;]", "", md)


def chars(md: str) -> int:
    return len(re.sub(r"\s+", "", plain(md)))


def find_article(directory: Path, slug: str, no: int) -> Path | None:
    for path in (
        directory / f"{slug}.md" if slug else None,
        directory / f"{no:03d}.md",
        directory / f"{no}.md",
    ):
        if path and path.exists():
            return path
    return None


def section_warnings(md: str) -> list[str]:
    warnings: list[str] = []
    matches = list(re.finditer(r"^##\s+(.+)$", md, flags=re.M))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        body = md[match.end():end]
        direct = re.split(r"^###\s+", body, maxsplit=1, flags=re.M)[0]
        h3 = len(re.findall(r"^###\s+", body, flags=re.M))
        if chars(direct) > 240 and h3 == 0:
            warnings.append(f"H2『{match.group(1)}』直下が長いのにH3がありません")
        if chars(body) > 650 and h3 < 2:
            warnings.append(f"H2『{match.group(1)}』が長いのにH3が{h3}個です")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--sheet", default="制作管理表")
    parser.add_argument("--articles-dir", default="articles")
    parser.add_argument("--results", default="results/article_quality_results.csv")
    parser.add_argument("--tolerance", type=float, default=0.03)
    parser.add_argument("--nos", default="")
    parser.add_argument("--include-unstarted", action="store_true")
    parser.add_argument("--fail-on-error", action="store_true")
    args = parser.parse_args()

    path = Path(args.input)
    df = pd.read_csv(path, dtype=object) if path.suffix.lower() == ".csv" else pd.read_excel(
        path, sheet_name=args.sheet, dtype=object
    )
    cols = {key: column(list(df.columns), names) for key, names in CANDIDATES.items()}
    if not cols["no"] or not cols["title"] or not cols["target"]:
        raise RuntimeError("No、記事タイトル、文字数目安の列が必要です")

    wanted = selected_nos(args.nos)
    output_rows: list[dict[str, Any]] = []
    error_count = 0
    for _, row in df.dropna(how="all").iterrows():
        no = number(row.get(cols["no"]))
        if no is None or (wanted is not None and no not in wanted):
            continue
        state = text(row.get(cols["status"])) if cols["status"] else ""
        if wanted is None and not args.include_unstarted and state in {"", "未着手"}:
            continue

        title = text(row.get(cols["title"]))
        slug = text(row.get(cols["slug"])) if cols["slug"] else ""
        target = text(row.get(cols["target"]))
        cta_strength = text(row.get(cols["cta"])) if cols["cta"] else ""
        lower, upper = target_range(target, args.tolerance)
        article = find_article(Path(args.articles_dir), slug, no)
        errors: list[str] = []
        warnings: list[str] = []

        if article is None:
            errors.append("記事Markdownが見つかりません")
            core_count = total_count = cta_count = intro_count = h2 = h3 = 0
            filename = ""
        else:
            filename = str(article)
            md = strip_front_matter(article.read_text(encoding="utf-8"))
            cta_pattern = re.compile(
                r"<!--\s*CTA_START\s*-->(.*?)<!--\s*CTA_END\s*-->", re.S | re.I
            )
            ctas = cta_pattern.findall(md)
            core = strip_h1(cta_pattern.sub("", md))
            total_count = chars(strip_h1(md))
            core_count = chars(core)
            cta_count = len(ctas)
            intro_count = chars(strip_h1(re.split(r"^##\s+", md, maxsplit=1, flags=re.M)[0]))
            h2 = len(re.findall(r"^##\s+", md, flags=re.M))
            h3 = len(re.findall(r"^###\s+", md, flags=re.M))
            warnings.extend(section_warnings(md))

            if lower is not None and core_count < lower:
                errors.append(f"本文コア文字数不足（{core_count}字／下限{lower}字）")
            if upper is not None and core_count > upper:
                errors.append(f"本文コア文字数超過（{core_count}字／上限{upper}字）")
            if intro_count > 240:
                errors.append(f"序文が240字を超えています（{intro_count}字）")
            if h2 == 0:
                errors.append("H2見出しがありません")
            if cta_count > 3:
                errors.append(f"CTAが3箇所を超えています（{cta_count}箇所）")
            if cta_strength == "強" and cta_count == 0:
                warnings.append("CV型ですがCTAマーカーがありません")
            if cta_strength == "弱" and cta_count > 1:
                warnings.append("PV型でCTAが複数あります")

        status = "ERROR" if errors else ("WARN" if warnings else "OK")
        error_count += status == "ERROR"
        output_rows.append({
            "No": f"{no:03d}", "記事タイトル": title, "article_file": filename,
            "文字数目安": target, "許容下限": lower or "", "許容上限": upper or "",
            "総文字数": total_count, "本文コア文字数": core_count,
            "序文文字数": intro_count, "H2数": h2, "H3数": h3, "CTA数": cta_count,
            "status": status, "errors": " / ".join(errors),
            "warnings": " / ".join(warnings),
        })

    result_path = Path(args.results)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0].keys()) if output_rows else [
        "No", "記事タイトル", "article_file", "文字数目安", "許容下限", "許容上限",
        "総文字数", "本文コア文字数", "序文文字数", "H2数", "H3数", "CTA数",
        "status", "errors", "warnings"
    ]
    with result_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)

    for row in output_rows:
        print(f"[{row['status']}] {row['No']} core={row['本文コア文字数']} {row['記事タイトル']}")
        if row["errors"]:
            print("  ERROR:", row["errors"])
        if row["warnings"]:
            print("  WARN :", row["warnings"])
    print(f"結果CSV: {result_path}")
    return 1 if args.fail_on_error and error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
