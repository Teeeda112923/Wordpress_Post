"""CyberNote GEO Kit（独自プラグイン）用のメタ情報を組み立てる。

プラグインは投稿メタに保存された以下の4項目を使って、結論ボックス・FAQブロック・
出典リストの表示と、JSON-LD（FAQPage / citation / about）・llms.txt を生成する。

    _cng_answer  : この記事の結論（40〜60字）
    _cng_cve     : 関連CVE / 脆弱性ID（カンマ区切り）
    _cng_faq     : FAQ [{"q": ..., "a": ...}, ...] のJSON
    _cng_sources : 出典 [{"title":..., "url":..., "publisher":...}, ...] のJSON

値の取得元は次の優先順。CyberNote短編ニュースは1のみを必須とし、2は旧記事を
手動投稿する場合の後方互換として残す。

    1. 記事Markdown先頭のフロントマター（answer / cve / faq / sources）
    2. 本文からの抽出（H2「FAQ」、H2「参考情報」、冒頭リード、CVE番号）

フロントマターを優先するのは、結論を本文から機械的に切り出すと文が途中で切れる
ためで、記事作成時に明示してもらうほうが確実なため。

WordPress 側は wp-content/mu-plugins/cng-geo-rest.php が必要（未設置だと
REST API 経由のメタ書き込みが無視される）。
"""
from __future__ import annotations

import json
import re

# プラグインの cng_primary_source_domains() と同じ一覧（一次情報の判定に使用）
PRIMARY_SOURCE_DOMAINS = (
    "jvn.jp",
    "ipa.go.jp",
    "jpcert.or.jp",
    "nisc.go.jp",
    "npa.go.jp",
    "soumu.go.jp",
    "meti.go.jp",
    "ppc.go.jp",
    "nvd.nist.gov",
    "nist.gov",
    "cisa.gov",
    "cve.org",
    "mitre.org",
    "first.org",
)

# ドメイン → 発行元の表示名（publisher 未指定時の補完に使う）
_PUBLISHER_BY_DOMAIN = (
    ("nvd.nist.gov", "NVD（米国国立標準技術研究所）"),
    ("nist.gov", "NIST"),
    ("cisa.gov", "CISA（米国サイバーセキュリティ・インフラセキュリティ庁）"),
    ("cve.org", "CVE Program"),
    ("mitre.org", "MITRE"),
    ("first.org", "FIRST"),
    ("jvn.jp", "JVN（脆弱性対策情報ポータルサイト）"),
    ("ipa.go.jp", "IPA（情報処理推進機構）"),
    ("jpcert.or.jp", "JPCERT/CC"),
    ("nisc.go.jp", "内閣サイバーセキュリティセンター"),
    ("microsoft.com", "Microsoft"),
    ("apple.com", "Apple"),
    ("google.com", "Google"),
    ("adobe.com", "Adobe"),
    ("oracle.com", "Oracle"),
    ("cisco.com", "Cisco"),
    ("checkpoint.com", "Check Point"),
    ("fortinet.com", "Fortinet"),
    ("paloaltonetworks.com", "Palo Alto Networks"),
    ("vmware.com", "VMware"),
    ("broadcom.com", "Broadcom"),
    ("redhat.com", "Red Hat"),
    ("elecom.co.jp", "エレコム"),
)

_FAQ_HEADINGS = ("FAQ", "よくある質問")
_SOURCE_HEADINGS = ("参考情報", "参考・出典", "出典元", "出典", "参考")
_PLUGIN_RENDERED_HEADINGS = ("FAQ", "よくある質問", "参考情報", "参考・出典")

_ANSWER_MIN = 40
_ANSWER_MAX = 60

# フロントマターFAQ回答の目安（geo_article_quality_check.py と同じ基準）。
# 下限は当初70字だったが、1文で簡潔に答えた回答が60台後半で落ちる例が続いたため
# 60字に緩めた（GEOプラグイン側に70字の制約があるわけではない）。
_FAQ_ANSWER_MIN = 60
_FAQ_ANSWER_MAX = 140

_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^\s)]+)\)")
_CVE_RE = re.compile(r"CVE-\d{4}-\d{4,}", re.I)
_JVN_RE = re.compile(r"JVN(?:VU)?#?\d+", re.I)
_QUESTION_PREFIX_RE = re.compile(r"^Q\s*\d*\s*[.．:：、]?\s*", re.I)


def _safe(x) -> str:
    return "" if x is None else str(x).strip()


def _visible_len(text: str) -> int:
    """プラグインの監査（CNG_Audit::count_chars）と同じ数え方（空白を除く）。"""
    return len(re.sub(r"\s+", "", text or ""))


def _strip_inline_md(text: str) -> str:
    """強調・リンクなどのMarkdown装飾を落としてプレーンテキストにする。"""
    t = _safe(text)
    t = _MD_LINK_RE.sub(r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"^[-*+]\s+", "", t, flags=re.M)
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\s+", " ", t).strip()


def _host_of(url: str) -> str:
    m = re.match(r"^https?://([^/]+)", _safe(url), re.I)
    return m.group(1).lower() if m else ""


def is_primary_source(url: str) -> bool:
    host = _host_of(url)
    if not host:
        return False
    return any(host == d or host.endswith("." + d) for d in PRIMARY_SOURCE_DOMAINS)


def publisher_for_url(url: str) -> str:
    host = _host_of(url)
    if not host:
        return ""
    for domain, name in _PUBLISHER_BY_DOMAIN:
        if host == domain or host.endswith("." + domain):
            return name
    return ""


# --------------------------------------------------------------------------- #
# フロントマター
# --------------------------------------------------------------------------- #
def parse_front_matter(md_text: str) -> tuple[dict, str]:
    """先頭のフロントマターを (辞書, 本文) に分解する。

    PyYAML を追加せずに済むよう、記事作成ルールで定めた形だけを解釈する。

        ---
        answer: ...
        cve: ...
        faq:
          - q: ...
            a: ...
        sources:
          - title: ...
            url: ...
            publisher: ...
        ---
    """
    text = (md_text or "").lstrip("﻿")
    if not text.lstrip().startswith("---"):
        return {}, md_text

    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip() == "---"), None)
    if start is None:
        return {}, md_text
    end = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}, md_text

    data: dict = {}
    current_key = ""
    for raw in lines[start + 1 : end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        # 「- key: value」= リストの新しい要素
        m_item = re.match(r"^\s*-\s*([A-Za-z_][\w]*)\s*:\s*(.*)$", raw)
        if m_item and current_key:
            data.setdefault(current_key, [])
            if isinstance(data[current_key], list):
                data[current_key].append({m_item.group(1): _unquote(m_item.group(2))})
            continue

        # 「  key: value」= 直前のリスト要素への追加
        m_sub = re.match(r"^\s+([A-Za-z_][\w]*)\s*:\s*(.*)$", raw)
        if m_sub and current_key and isinstance(data.get(current_key), list) and data[current_key]:
            data[current_key][-1][m_sub.group(1)] = _unquote(m_sub.group(2))
            continue

        # 「key: value」= トップレベル
        m_top = re.match(r"^([A-Za-z_][\w]*)\s*:\s*(.*)$", raw)
        if m_top:
            current_key = m_top.group(1)
            value = _unquote(m_top.group(2))
            data[current_key] = value if value else []
            continue

    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return data, body


def _unquote(value: str) -> str:
    v = _safe(value)
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1].strip()
    return v


# --------------------------------------------------------------------------- #
# 本文からの抽出（フロントマターが無い記事のフォールバック）
# --------------------------------------------------------------------------- #
def _iter_h2_sections(body_md: str):
    """(見出しテキスト, セクション本文) を H2 単位で返す。"""
    lines = (body_md or "").split("\n")
    heads = [(m.group(1).strip(), i) for i, l in enumerate(lines)
             if (m := re.match(r"^##\s+(.+?)\s*$", l))]
    for n, (title, start) in enumerate(heads):
        end = heads[n + 1][1] if n + 1 < len(heads) else len(lines)
        yield title, "\n".join(lines[start + 1 : end])


def _matches_heading(title: str, candidates) -> bool:
    t = re.sub(r"\s+", "", _safe(title))
    return any(t == re.sub(r"\s+", "", c) for c in candidates)


def strip_plugin_generated_sections(body_md: str) -> tuple[str, list[str]]:
    """GEO Kitが生成するFAQ・出典と重複する本文H2を取り除く。

    品質ゲートは該当見出しをエラーにするが、チェッカーを経由しない手動実行でも
    二重表示を起こさないための投稿直前の防御として使う。
    """
    kept: list[str] = []
    removed: list[str] = []
    skipping = False
    for line in (body_md or "").splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            title = match.group(1).strip()
            if _matches_heading(title, _PLUGIN_RENDERED_HEADINGS):
                removed.append(title)
                skipping = True
                continue
            skipping = False
        if not skipping:
            kept.append(line)
    return "\n".join(kept).rstrip() + "\n", removed


def extract_faq(body_md: str, limit: int = 5) -> list[dict]:
    """H2「FAQ」配下から、H3見出しを質問・直後の段落を回答として抽出する。"""
    rows: list[dict] = []
    for title, section in _iter_h2_sections(body_md):
        if not _matches_heading(title, _FAQ_HEADINGS):
            continue
        current_q = ""
        buf: list[str] = []

        def flush():
            if current_q and buf:
                answer = _strip_inline_md(" ".join(buf))
                if answer:
                    rows.append({"q": current_q, "a": answer})

        for line in section.split("\n"):
            m = re.match(r"^#{3,4}\s+(.+?)\s*$", line)
            if m:
                flush()
                buf = []
                current_q = _QUESTION_PREFIX_RE.sub("", _strip_inline_md(m.group(1))).strip()
                continue
            if line.strip() and not line.strip().startswith("<"):
                buf.append(line.strip())
        flush()
        break
    return rows[:limit]


def is_same_site(url: str, site_host: str) -> bool:
    """自サイトへのリンクかどうか（出典ではなく内部リンクとして扱うため）。"""
    host = _host_of(url)
    site = _host_of(site_host) or _safe(site_host).lower().lstrip("www.")
    if not host or not site:
        return False
    return host == site or host.endswith("." + site) or site.endswith("." + host)


def extract_sources(body_md: str, limit: int = 6, site_host: str = "") -> list[dict]:
    """H2「参考情報」等のセクションから出典リンクを抽出する。

    自サイトへのリンクは内部リンクであって出典ではないため除外する。
    """
    rows: list[dict] = []
    seen: set = set()
    for title, section in _iter_h2_sections(body_md):
        if not _matches_heading(title, _SOURCE_HEADINGS):
            continue
        for m in _MD_LINK_RE.finditer(section):
            url = m.group(2).rstrip("）、。，")
            if url in seen or (site_host and is_same_site(url, site_host)):
                continue
            seen.add(url)
            label = _strip_inline_md(m.group(1))
            publisher = publisher_for_url(url)
            rows.append({
                "title": label or publisher or url,
                "url": url,
                "publisher": publisher,
            })
    rows.sort(key=lambda r: 0 if is_primary_source(r["url"]) else 1)
    return rows[:limit]


def extract_lead(body_md: str) -> str:
    """最初のH2より前の段落（冒頭リード）を返す。"""
    parts: list[str] = []
    for line in (body_md or "").split("\n"):
        if re.match(r"^##\s+\S", line):
            break
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("<") or s.startswith("---"):
            continue
        parts.append(s)
    return _strip_inline_md(" ".join(parts))


def extract_cves(text: str) -> list[str]:
    """本文などから CVE番号・JVN番号を重複なく抽出する。"""
    found: list[str] = []
    seen: set = set()

    def add(value: str) -> None:
        # JVN番号は「JVN#12345678」「JVN12345678」の両表記が混在するため、
        # '#' を無視して同一視する（初出の表記をそのまま採用する）。
        key = value.replace("#", "")
        if key not in seen:
            seen.add(key)
            found.append(value)

    for m in _CVE_RE.finditer(text or ""):
        add(m.group(0).upper())
    for m in _JVN_RE.finditer(text or ""):
        add(m.group(0).upper())
    return found


def build_answer(text: str, min_chars: int = _ANSWER_MIN, max_chars: int = _ANSWER_MAX) -> str:
    """説明文を結論ボックス向けに調整する（フロントマターが無い場合のみ使用）。

    句点の位置で切り、文の途中では切らない。max に収まる文が無い場合は
    先頭の一文をそのまま返す（途中で切って「…」にしない）。
    """
    t = _strip_inline_md(text)
    if not t:
        return ""
    if _visible_len(t) <= max_chars:
        return t

    # 先頭から句点単位で足していき、max に収まる最長のかたまりを探す
    best = ""
    cursor = 0
    while True:
        idx = t.find("。", cursor)
        if idx < 0:
            break
        candidate = t[: idx + 1]
        if _visible_len(candidate) > max_chars:
            break
        best = candidate
        cursor = idx + 1
    if _visible_len(best) >= min_chars:
        return best

    # 先頭の一文が長すぎる場合は、リード内で字数の範囲に収まる一文を探す
    sentences = [s + "。" for s in t.split("。") if s.strip()]
    for s in sentences:
        if min_chars <= _visible_len(s) <= max_chars:
            return s

    return sentences[0] if sentences else t


def ensure_primary_source(rows: list[dict], cves: list[str]) -> list[dict]:
    """一次情報が1件も無い場合、CVEのNVD詳細ページを先頭に補う。"""
    rows = [r for r in (rows or []) if _safe(r.get("url"))]
    if any(is_primary_source(r["url"]) for r in rows):
        return rows
    cve = next((c for c in (cves or []) if c.upper().startswith("CVE-")), "")
    if not cve:
        return rows
    url = f"https://nvd.nist.gov/vuln/detail/{cve.upper()}"
    if any(r["url"] == url for r in rows):
        return rows
    return [{
        "title": f"{cve.upper()} - NVD 詳細情報",
        "url": url,
        "publisher": publisher_for_url(url),
    }] + rows


# --------------------------------------------------------------------------- #
# フロントマターの自動補正
# --------------------------------------------------------------------------- #
def normalize_front_matter(front: dict, body: str) -> tuple[dict, list[str]]:
    """フロントマターの機械的な不備を補正し、(補正後, 補正内容) を返す。

    記事はChatGPTが執筆するため、句点の抜けや本文FAQとの表記ずれといった
    「内容は正しいが形式が揃っていない」不備が混ざる。人手で直すのは手間な割に
    判断の余地がないため、ここで機械的に揃える。

    補正するのは次の3点だけで、内容そのものは作らない。
      1. answer が句点で終わっていない → 末尾を整えて「。」を付ける
      2. 本文の H2「FAQ」の質問とフロントマターの質問がずれている
         → 本文側を正として質問を合わせる（回答は本文側が長い場合のみ採用）
      3. sources に一次情報が無い → CVEのNVD詳細ページを補う

    文字数不足のように内容を書き足す必要があるものは補正しない（品質チェッカー側で
    エラーとして検出させる）。
    """
    fixed = dict(front or {})
    notes: list[str] = []

    # --- 1. answer の句点 ---------------------------------------------------
    answer = _safe(fixed.get("answer")) if isinstance(fixed.get("answer"), str) else ""
    if answer:
        # 末尾の「…」や読点を落としたうえで句点を付け直す
        trimmed = answer.rstrip("。．.…、,， 　")
        if trimmed:
            candidate = trimmed + "。"
            if candidate != answer:
                fixed["answer"] = candidate
                notes.append("answerの末尾に句点を補いました")

    # --- 2. FAQ を本文に合わせる -------------------------------------------
    body_faq = extract_faq(body)
    front_faq = [
        {"q": _safe(r.get("q")), "a": _safe(r.get("a"))}
        for r in (fixed.get("faq") or [])
        if isinstance(r, dict)
    ]
    if body_faq and front_faq:
        merged: list[dict] = []
        changed_q = False
        changed_a = False
        for index, row in enumerate(front_faq):
            question, answer_text = row["q"], row["a"]
            if index < len(body_faq):
                body_q = body_faq[index].get("q", "")
                body_a = body_faq[index].get("a", "")
                if body_q and _compact(body_q) != _compact(question):
                    question = body_q
                    changed_q = True
                # 回答は本文側のほうが目安に収まる場合だけ差し替える
                if body_a and not _in_faq_range(answer_text) and _in_faq_range(body_a):
                    answer_text = body_a
                    changed_a = True
            merged.append({"q": question, "a": answer_text})
        fixed["faq"] = merged
        if changed_q:
            notes.append("FAQの質問を本文のH3見出しに合わせました")
        if changed_a:
            notes.append("FAQの回答を本文の内容に差し替えました")

    # --- 3. 一次情報の補完 --------------------------------------------------
    sources = [
        {
            "title": _safe(r.get("title")),
            "url": _safe(r.get("url")),
            "publisher": _safe(r.get("publisher")),
        }
        for r in (fixed.get("sources") or [])
        if isinstance(r, dict) and _safe(r.get("url"))
    ]
    if sources and not any(is_primary_source(r["url"]) for r in sources):
        raw_cve = fixed.get("cve")
        cves = (
            [c.strip() for c in raw_cve.split(",") if c.strip()]
            if isinstance(raw_cve, str)
            else []
        )
        completed = ensure_primary_source(sources, cves)
        if len(completed) != len(sources):
            fixed["sources"] = completed
            notes.append("sourcesに一次情報（NVD詳細ページ）を補いました")

    return fixed, notes


def _compact(text: str) -> str:
    """空白を除いた比較用の文字列（品質チェッカーの compact と同じ）。"""
    return re.sub(r"\s+", "", text or "")


def _in_faq_range(text: str) -> bool:
    return _FAQ_ANSWER_MIN <= _visible_len(_strip_inline_md(text)) <= _FAQ_ANSWER_MAX


# --------------------------------------------------------------------------- #
# メタの組み立て
# --------------------------------------------------------------------------- #
def build_geo_meta(
    md_text: str, *, cve_hint: str = "", slug: str = "", site_host: str = ""
) -> dict:
    """記事Markdownから GEO Kit 用メタ（REST API 送信用）を組み立てる。

    フロントマターがあればそれを優先し、無い項目だけ本文から補う。
    句点の抜けなど機械的な不備は normalize_front_matter() で揃えてから使うため、
    品質チェッカーが通した内容とここで投稿する内容は一致する。
    """
    front, body = parse_front_matter(md_text)
    front, _ = normalize_front_matter(front, body)

    # --- 結論 -------------------------------------------------------------
    answer = _safe(front.get("answer")) if isinstance(front.get("answer"), str) else ""
    if not answer:
        answer = build_answer(extract_lead(body))

    # --- CVE --------------------------------------------------------------
    raw_cve = front.get("cve")
    cve_list: list[str] = []
    if isinstance(raw_cve, str) and raw_cve.strip():
        cve_list = [c.strip() for c in raw_cve.split(",") if c.strip()]
    if not cve_list:
        cve_list = extract_cves(f"{cve_hint} {slug} {body}")

    # --- FAQ --------------------------------------------------------------
    faq: list[dict] = []
    for row in (front.get("faq") or []):
        if isinstance(row, dict) and _safe(row.get("q")) and _safe(row.get("a")):
            faq.append({"q": _safe(row["q"]), "a": _safe(row["a"])})
    if not faq:
        faq = extract_faq(body)

    # --- 出典 -------------------------------------------------------------
    sources: list[dict] = []
    for row in (front.get("sources") or []):
        if isinstance(row, dict) and _safe(row.get("url")):
            url = _safe(row["url"])
            if site_host and is_same_site(url, site_host):
                continue
            sources.append({
                "title": _safe(row.get("title")) or publisher_for_url(url) or url,
                "url": url,
                "publisher": _safe(row.get("publisher")) or publisher_for_url(url),
            })
    if not sources:
        sources = extract_sources(body, site_host=site_host)
    sources.sort(key=lambda r: 0 if is_primary_source(r["url"]) else 1)
    sources = ensure_primary_source(sources, cve_list)

    meta: dict = {}
    if answer:
        meta["_cng_answer"] = answer
    if cve_list:
        meta["_cng_cve"] = ", ".join(dict.fromkeys(cve_list))
    if faq:
        meta["_cng_faq"] = json.dumps(faq, ensure_ascii=False)
    if sources:
        meta["_cng_sources"] = json.dumps(sources, ensure_ascii=False)
    return meta


def describe_geo_meta(meta: dict) -> str:
    """ログ表示用の要約を返す。"""
    if not meta:
        return "GEO情報なし"
    answer = meta.get("_cng_answer", "")
    faq = json.loads(meta.get("_cng_faq") or "[]")
    sources = json.loads(meta.get("_cng_sources") or "[]")
    primary = sum(1 for s in sources if is_primary_source(s.get("url", "")))
    return (
        f"結論{_visible_len(answer)}字 / CVE {meta.get('_cng_cve', '-')} / "
        f"FAQ{len(faq)}件 / 出典{len(sources)}件（一次情報{primary}件）"
    )


def check_geo_meta(sent: dict, saved: dict) -> tuple[list, list]:
    """投稿応答のメタと送信内容を照合し、(未保存, 壊れている) のキーを返す。

    JSONで保存するメタは、保存後に読み戻せる形かどうかまで確認する。
    スラッシュの二重付与などで壊れると、値は入っていても表示側の
    json_decode() が失敗し、FAQ・出典が空表示になるため。
    """
    missing: list = []
    broken: list = []
    for key, value in (sent or {}).items():
        got = _safe((saved or {}).get(key))
        if not got:
            missing.append(key)
            continue
        if _safe(value).startswith("["):
            try:
                sent_rows = json.loads(value)
                got_rows = json.loads(got)
            except Exception:
                broken.append(key)
                continue
            if not isinstance(got_rows, list) or len(got_rows) != len(sent_rows):
                broken.append(key)
    return missing, broken
