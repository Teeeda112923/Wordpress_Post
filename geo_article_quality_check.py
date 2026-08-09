#!/usr/bin/env python3
"""CyberNote GEO/SEO向け記事品質チェッカー。

従来の940字上限は使わず、CyberNote GEO Kitの入力要件を検査する。
旧 article_quality_check.py からも呼び出せる互換エントリポイントを提供する。
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from urllib.parse import urlparse

PRIMARY_DOMAINS = {
    "jvn.jp", "ipa.go.jp", "jpcert.or.jp", "nisc.go.jp", "npa.go.jp",
    "soumu.go.jp", "meti.go.jp", "ppc.go.jp", "nvd.nist.gov", "nist.gov",
    "cisa.gov", "cve.org", "mitre.org", "first.org",
}

FORBIDDEN_BODY_H2 = {"FAQ", "よくある質問", "参考情報", "参考・出典"}
CORE_TARGET_MIN = 700
CORE_TARGET_MAX = 950
CORE_HARD_MAX = 1000


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def plain(value: str) -> str:
    value = re.sub(r"<!--.*?-->", "", value or "", flags=re.S)
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"https?://\S+", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"^\s{0,3}#{1,6}\s*", "", value, flags=re.M)
    value = re.sub(r"^\s*[-*+]\s+", "", value, flags=re.M)
    value = re.sub(r"^\s*\d+[.)]\s+", "", value, flags=re.M)
    value = re.sub(r"^\s*\|?[-:| ]+\|?\s*$", "", value, flags=re.M)
    value = re.sub(r"[*_~>#|]", "", value)
    return value


def chars(value: str) -> int:
    return len(compact(plain(value)))


def split_front_matter(md: str) -> tuple[str, str, list[str]]:
    lines = md.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return "", md, ["先頭にYAMLフロントマターがありません"]
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1:]), []
    return "", md, ["YAMLフロントマターの終了区切りがありません"]


def unquote(value: str) -> str:
    """YAMLの引用符を外す。

    記事のフロントマターは値を "..." で囲んでいる。外さずに検査すると、
    answer の末尾が「"」になって句点チェックに落ちる、URLの netloc が取れず
    一次情報と判定されない、本文FAQとの質問比較が一致しない、といった
    実体のないエラーになる（実際に5件中4件がこれだった）。
    """
    value = (value or "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1].strip()
    return value


def value_line(front: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*)$", front)
    return unquote(match.group(1)) if match else ""


def faq_items(front: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    question = ""
    answer = ""
    for line in front.splitlines():
        stripped = line.strip()
        if stripped.startswith("- q:"):
            if question:
                items.append((question, answer))
            question = unquote(stripped[4:])
            answer = ""
        elif question and stripped.startswith("a:"):
            answer = unquote(stripped[2:])
    if question:
        items.append((question, answer))
    return items


def source_items(front: str) -> list[tuple[str, str, str]]:
    items: list[tuple[str, str, str]] = []
    title = ""
    url = ""
    publisher = ""
    for line in front.splitlines():
        stripped = line.strip()
        if stripped.startswith("- title:"):
            if title:
                items.append((title, url, publisher))
            title = unquote(stripped[len("- title:"):])
            url = ""
            publisher = ""
        elif title and stripped.startswith("url:"):
            url = unquote(stripped[len("url:"):])
        elif title and stripped.startswith("publisher:"):
            publisher = unquote(stripped[len("publisher:"):])
    if title:
        items.append((title, url, publisher))
    return items


def urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s)\"'<>]+", text or "")


def is_primary(url: str) -> bool:
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower().split(":")[0]
    except ValueError:
        return False
    if any(host == domain or host.endswith("." + domain) for domain in PRIMARY_DOMAINS):
        return True
    # 開発元がGitHub Security Advisoryを一次情報として公開する場合に対応する。
    return host == "github.com" and "/security/advisories/" in parsed.path


def remove_reference_box(text: str) -> str:
    return re.sub(
        r"<!--\s*wp:group\b.*?-->.*?<!--\s*/wp:group\s*-->",
        "",
        text or "",
        flags=re.S | re.I,
    )


def h2_sections(body: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", body, flags=re.M))
    result: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result.append((match.group(1).strip(), body[match.end():end]))
    return result


def first_h1_body(body: str) -> str:
    match = re.search(r"^#\s+.+?$", body, flags=re.M)
    return body[match.end():] if match else body


def intro_text(body: str) -> str:
    after_h1 = first_h1_body(body)
    before_h2 = re.split(r"^##\s+", after_h1, maxsplit=1, flags=re.M)[0]
    return remove_reference_box(before_h2)


def summary_text(body: str) -> str:
    matches = list(re.finditer(r"^##\s+まとめ\s*$", body, flags=re.M))
    return body[matches[-1].end():] if matches else ""


def section_before_h3(section_body: str) -> str:
    return re.split(r"^###\s+", section_body, maxsplit=1, flags=re.M)[0]


def h2_direct_lead(section_body: str) -> str:
    """H2直下の最初の説明段落を返す（H3・表・箇条書きより前）。"""
    before_h3 = section_before_h3(section_body)
    paragraphs = re.split(r"\n\s*\n", before_h3.strip())
    for paragraph in paragraphs:
        value = paragraph.strip()
        if not value:
            continue
        # コメントやHTMLブロックは説明文として数えない。
        if value.startswith("<!--") or value.startswith("<"):
            continue
        if any(list_or_table(line) for line in value.splitlines()):
            return ""
        return value
    return ""


def list_or_table(line: str) -> bool:
    stripped = line.strip()
    return bool(
        re.match(r"^(?:[-*+]\s+|\d+[.)]\s+|\|)", stripped)
        or (stripped.startswith("|") and stripped.endswith("|"))
    )


def list_table_errors(body: str) -> list[str]:
    lines = body.splitlines()
    errors: list[str] = []
    index = 0
    while index < len(lines):
        if not list_or_table(lines[index]):
            index += 1
            continue
        start = index
        while index < len(lines) and (list_or_table(lines[index]) or not lines[index].strip()):
            index += 1
        end = index
        before: list[str] = []
        cursor = start - 1
        while cursor >= 0 and not lines[cursor].strip():
            cursor -= 1
        while cursor >= 0 and lines[cursor].strip():
            before.append(lines[cursor])
            cursor -= 1
        after: list[str] = []
        cursor = end
        while cursor < len(lines) and lines[cursor].strip():
            after.append(lines[cursor])
            cursor += 1
        before_count = chars("\n".join(reversed(before)))
        after_count = chars("\n".join(after))
        if before_count < 150:
            errors.append(f"箇条書き・表の直前の説明が150字未満です（{before_count}字）")
        if after_count < 150:
            errors.append(f"箇条書き・表の直後の説明が150字未満です（{after_count}字）")
    return errors


def geo_errors(front: str, body: str) -> tuple[list[str], list[str]]:
    """CyberNote記事の厳密な品質判定を (エラー, 警告) で返す。"""
    errors: list[str] = []
    warnings: list[str] = []

    raw = {
        "answer": value_line(front, "answer"),
        "cve": value_line(front, "cve"),
        "faq": [{"q": q, "a": a} for q, a in faq_items(front)],
        "sources": [
            {"title": t, "url": u, "publisher": p} for t, u, p in source_items(front)
        ],
    }

    def check_range(label: str, count: int, low: int, high: int, unit: str = "字") -> None:
        if not low <= count <= high:
            errors.append(f"{label}が{low}〜{high}{unit}ではありません（{count}{unit}）")

    answer = raw.get("answer", "")
    if not answer:
        errors.append("フロントマターanswerがありません")
    elif not answer.endswith("。"):
        errors.append("answerが「。」で終わっていません")
    else:
        check_range("answer", chars(answer), 40, 60)

    if re.search(r"(?m)^cve:", front) is None:
        errors.append("フロントマターcveがありません")

    front_faq = [(r.get("q", ""), r.get("a", "")) for r in raw.get("faq", [])]
    if len(front_faq) < 2:
        errors.append("フロントマターfaqが2問未満です")
    for question, answer_text in front_faq:
        if not question or not answer_text:
            errors.append("フロントマターfaqのq/aが未入力です")
        if answer_text:
            check_range("フロントマターFAQ回答", chars(answer_text), 60, 140)

    sources = [
        (r.get("title", ""), r.get("url", ""), r.get("publisher", ""))
        for r in raw.get("sources", [])
    ]
    if len(sources) < 1:
        errors.append("フロントマターsourcesが1件未満です")
    for title, url, publisher in sources:
        if not title or not url or not publisher:
            errors.append("フロントマターsourcesのtitle/url/publisherが未入力です")
    if not any(is_primary(url) for _, url, _ in sources):
        errors.append("フロントマターsourcesに一次情報ドメインがありません")

    check_range("冒頭リード", chars(intro_text(body)), 250, 300)

    core_count = chars(body)
    if core_count < CORE_TARGET_MIN:
        errors.append(f"本文コアが{CORE_TARGET_MIN}字未満です（{core_count}字）")
    elif core_count > CORE_HARD_MAX:
        errors.append(f"本文コアが{CORE_HARD_MAX}字を超えています（{core_count}字）")
    elif core_count > CORE_TARGET_MAX:
        warnings.append(
            f"本文コアが目標{CORE_TARGET_MIN}〜{CORE_TARGET_MAX}字を超えています"
            f"（{core_count}字、上限{CORE_HARD_MAX}字以内）"
        )

    sections = h2_sections(body)
    forbidden = [title for title, _ in sections if compact(title) in FORBIDDEN_BODY_H2]
    for title in forbidden:
        errors.append(f"本文に禁止見出し『## {title}』があります")

    summary_matches = list(re.finditer(r"^##\s+まとめ\s*$", body, flags=re.M))
    if len(summary_matches) != 1:
        errors.append(f"## まとめが1件ではありません（{len(summary_matches)}件）")
    if len(summary_matches) == 1:
        summary = body[summary_matches[0].end():]
        check_range("## まとめ", chars(summary), 250, 300)
        if not sections or sections[-1][0] != "まとめ":
            errors.append("## まとめが記事の最後にありません")
        if re.search(r"(?m)^\s*(?:[-*+]\s+|\d+[.)]\s+)", summary):
            errors.append("## まとめに箇条書きがあります")

    internal = {
        url.rstrip(".,。")
        for url in urls(body)
        if urlparse(url).netloc.lower().endswith("cybernote.click")
    }
    if len(internal) < 3:
        errors.append(f"CyberNote内部リンクが3本未満です（{len(internal)}本）")

    boxes = re.findall(r'<div[^>]*class="[^"]*\bis-style-information-box\b"[^>]*>', body)
    if len(boxes) != 1:
        errors.append(f"参照情報ボックスが1個ではありません（{len(boxes)}個）")

    for title, section in sections:
        if title == "まとめ" or compact(title) in FORBIDDEN_BODY_H2:
            continue
        check_range(f"H2『{title}』直下リード", chars(h2_direct_lead(section)), 100, 150)

    errors.extend(list_table_errors(body))
    return errors, warnings


def find_article(directory: Path, slug: str, no: str) -> Path | None:
    candidates = [directory / f"{slug}.md"] if slug else []
    try:
        number = int(float(no))
        candidates.extend([directory / f"{number:03d}.md", directory / f"{number}.md"])
    except ValueError:
        candidates.append(directory / f"{no}.md")
    return next((path for path in candidates if path.exists()), None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--articles-dir", default="articles")
    parser.add_argument("--results", default="results/article_quality_results.csv")
    parser.add_argument("--nos", default="")
    parser.add_argument("--fail-on-error", action="store_true")
    parser.add_argument("--include-unstarted", action="store_true")
    parser.add_argument("--mode", choices=("geo", "legacy"), default="geo")
    parser.add_argument("--sheet", default="", help=argparse.SUPPRESS)
    parser.add_argument("--tolerance", type=float, default=0.03, help=argparse.SUPPRESS)
    args = parser.parse_args()

    wanted = {part for part in re.split(r"[,、\s]+", args.nos.strip()) if part} if args.nos.strip() else None
    input_path = Path(args.input)
    if not input_path.exists():
        raise RuntimeError(f"入力ファイルが見つかりません: {input_path}")
    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    outputs: list[dict[str, str | int]] = []
    error_count = 0
    for row in rows:
        no = str(row.get("No", "")).strip()
        if not no or (wanted is not None and no not in wanted and no.lstrip("0") not in wanted):
            continue
        title = str(row.get("記事タイトル", "")).strip()
        slug = str(row.get("スラッグ", "")).strip()
        article = find_article(Path(args.articles_dir), slug, no)
        errors: list[str] = []
        warnings: list[str] = []
        core_count = 0
        intro_count = 0
        answer_count = 0
        summary_count = 0
        summary_chars = 0
        faq_count = 0
        sources_count = 0
        primary_sources_count = 0
        forbidden_h2_count = 0
        filename = str(article) if article else ""
        if article is None:
            errors.append("記事Markdownが見つかりません")
        else:
            markdown_text = article.read_text(encoding="utf-8")
            front, body, front_errors = split_front_matter(markdown_text)
            errors.extend(front_errors)
            if not front_errors:
                geo_error_list, geo_warnings = geo_errors(front, body)
                errors.extend(geo_error_list)
                warnings.extend(geo_warnings)
                answer_count = chars(value_line(front, "answer"))
                summary_count = len(re.findall(r"^##\s+まとめ\s*$", body, flags=re.M))
                summary_chars = chars(summary_text(body)) if summary_count else 0
                faq_count = len(faq_items(front))
                source_rows = source_items(front)
                sources_count = len(source_rows)
                primary_sources_count = sum(is_primary(url) for _, url, _ in source_rows)
                forbidden_h2_count = sum(
                    compact(section_title) in FORBIDDEN_BODY_H2
                    for section_title, _ in h2_sections(body)
                )
            core_count = chars(body)
            intro_count = chars(intro_text(body))
        status = "ERROR" if errors else ("WARN" if warnings else "OK")
        error_count += int(status == "ERROR")
        outputs.append({
            "No": no,
            "記事タイトル": title,
            "article_file": filename,
            "本文コア文字数": core_count,
            "序文文字数": intro_count,
            "answer文字数": answer_count,
            "まとめ文字数": summary_chars,
            "まとめ件数": summary_count,
            "faq件数": faq_count,
            "sources件数": sources_count,
            "一次情報件数": primary_sources_count,
            "禁止見出し件数": forbidden_h2_count,
            "status": status,
            "errors": " / ".join(errors),
            "warnings": " / ".join(warnings),
            "mode": args.mode,
        })

    result_path = Path(args.results)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "No", "記事タイトル", "article_file", "本文コア文字数", "序文文字数",
        "answer文字数", "まとめ文字数", "まとめ件数", "faq件数", "sources件数",
        "一次情報件数", "禁止見出し件数", "status", "errors", "warnings", "mode",
    ]
    with result_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(outputs)

    for row in outputs:
        print(f"[{row['status']}] {row['No']} core={row['本文コア文字数']} {row['記事タイトル']}")
        if row["errors"]:
            print("  ERROR:", row["errors"])
        if row["warnings"]:
            print("  WARN :", row["warnings"])
    print(f"結果CSV: {result_path}")
    return 1 if args.fail_on_error and error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
