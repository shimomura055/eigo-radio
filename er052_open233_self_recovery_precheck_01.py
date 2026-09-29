# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_precheck_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1, 委任_06)
# ============================================================
# 目的: design_open233_self_recovery_flow_01.md §3-1/§4-3/§14-4で確定した
# 「deterministic pre-check」(¥0、機械照合のみ、Stage 1 LLM判定に依存しない
# 追加検出層)のTrial実装。
#
# 重要な設計制約:
# - Production code(er003_v1_en_direct_vfl_01_generate.py等)は一切変更
#   しない。本ファイルは他モジュールに依存しない自己完結スクリプト
#   (Ledger textとarticle textの2つの文字列を受け取るだけ)。
# - Production非接続。呼び出し元はTrial harness(次回委任以降)のみ。
# - API呼び出しなし(¥0)。regex/文字列照合のみ。
#
# 設計原則(委任文§3): FPを出しにくい保守的ルールから始める。
# - 言い換え(20%↔one-fifth等)・日付表記差(2026-07-13↔July 13/Sunday)・
#   敬称差(Trump↔President Trump)は「一致」扱いにする正規化辞書を持つ。
# - 複数の数値が並ぶFact(例: 日次OHLC四本値)は、どれが「主要な値」かを
#   機械的に一意特定できないため、number_mismatch判定の対象外とする
#   (単一の主要数値を持つFactに限定して判定することでFPを抑える)。
# - actor_missing/number_mismatch/date_mismatchは「Ledger値が本文に一切
#   現れない」かつ「別の値が本文の同種文脈に現れる」の両方を要求する
#   (単なる省略[Ledgerに書かれているが記事では触れられていないだけ]を
#   誤ってmismatch扱いしない)。
# - changed_scopeのような意味的逸脱(例: hormuz_run03_standardのHF-009
#   「Brent先物→石油市場全体」)は機械照合の対象外であり、本precheckは
#   検出できない(既知の限界、design書§14-4に明記済み)。
#
# 出力: precheck_findings(list[dict])。各dictは
# {field: fact_id, ledger_value: str, article_evidence: str,
#  kind: "actor_missing"|"number_mismatch"|"date_mismatch"|
#        "negation_marker"|"comparison_marker",
#  detected_by: "precheck"}
from __future__ import annotations

import re

# ------------------------------------------------------------
# 1. Ledger text パーサ
# ------------------------------------------------------------
# vfl01.build_verified_ledger_text()が生成する形式:
#   "[VERIFIED] HF-009: <claim>\n  scope: ...\n  numeric_value: ... "
#   "(numeric_scope: ...)\n  date_or_period: ...\n  notes_for_writer: ...\n"
# (fact block間は空行区切り、negative_claim_candidates_open233_01.md/
# er051_open233_checker_trial_variant_01.pyのfilter_ledger_notes_by_
# classification()と同じ前提)。
#
# 別家系(ER-006 pool pipeline等)の"[F-002] <日本語説明>\n  numeric_value: "
# 形式(verdictタグ無し)も緩く受理する(下記FACT_HEADER_V2)。この形式は
# date_or_period/conditionsタグを持たないことが多く、その分だけ本
# precheckのカバレッジが下がることを既知の限界として明記する。

FACT_HEADER_V1 = re.compile(
    r"^\[(VERIFIED|AMBIGUOUS[^\]]*)\]\s*([A-Za-z0-9_\-]+):\s*(.*)$"
)
FACT_HEADER_V2 = re.compile(r"^\[([A-Za-z0-9_\-]+)\]\s*(.*)$")
TAG_LINE = re.compile(r"^\s+([A-Za-z_][A-Za-z_ ]*):\s*(.*)$")

NON_FACT_ID_PREFIXES = ("SRC", "SOURCE")


def parse_ledger_text(ledger_text: str) -> list[dict]:
    """Ledger textをfact block単位(fact_id/verdict/claim/tag値)へ分解する。
    未知形式のblock(Source一覧見出し等)はスキップする(fail-safe、
    誤ってfactとして扱わない)。"""
    facts: list[dict] = []
    blocks = (ledger_text or "").split("\n\n")
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip() != ""]
        if not lines:
            continue
        header = lines[0]
        m1 = FACT_HEADER_V1.match(header)
        fact_id = None
        verdict = "UNKNOWN"
        claim = ""
        if m1:
            verdict = m1.group(1).split(" ")[0].split("-")[0].strip()
            fact_id = m1.group(2)
            claim = m1.group(3)
        else:
            m2 = FACT_HEADER_V2.match(header)
            if m2:
                fact_id = m2.group(1)
                claim = m2.group(2)
        if not fact_id or fact_id.upper().startswith(NON_FACT_ID_PREFIXES):
            continue
        rec = {"fact_id": fact_id, "verdict": verdict, "claim": claim.strip()}
        for ln in lines[1:]:
            tm = TAG_LINE.match(ln)
            if not tm:
                continue
            key = tm.group(1).strip().lower().replace(" ", "_")
            val = tm.group(2).strip()
            # 既存キーの重複(同じタグが複数行に現れることはない前提だが、
            # 念のため上書きせず先勝ちにする)
            rec.setdefault(key, val)
        facts.append(rec)
    return facts


# ------------------------------------------------------------
# 2. 正規化辞書(言い換え・日付表記差・敬称差を「一致」扱いにする)
# ------------------------------------------------------------
FRACTION_WORD_TO_PERCENT = {
    "half": 50.0, "a half": 50.0, "one half": 50.0,
    "one-fifth": 20.0, "a fifth": 20.0, "one fifth": 20.0,
    "one-quarter": 25.0, "a quarter": 25.0, "one quarter": 25.0,
    "one-third": 33.3, "a third": 33.3, "one third": 33.3,
    "two-thirds": 66.7, "two thirds": 66.7,
    "three-quarters": 75.0, "three quarters": 75.0,
    "one-tenth": 10.0, "a tenth": 10.0, "one tenth": 10.0,
}

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
]
MONTH_ABBREV = [m[:3] for m in MONTH_NAMES]
WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]

# 敬称差(Trump ↔ President Trump 等)を吸収するための除去リスト。
HONORIFIC_PREFIXES = [
    "President", "Mr.", "Mr", "Ms.", "Ms", "Mrs.", "Mrs", "Dr.", "Dr",
    "Prime Minister", "Secretary", "Senator", "Governor", "CEO", "Chairman",
]


# ------------------------------------------------------------
# 3. 数値抽出・比較
# ------------------------------------------------------------
PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent|％)")
COUNT_WORD_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*(million|billion|thousand)", re.IGNORECASE)
JP_MAN_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*万")
JP_OKU_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*億")

_COUNT_MULT = {"million": 1e6, "billion": 1e9, "thousand": 1e3}


def _to_float(s: str) -> float:
    return float(s.replace(",", ""))


def extract_percentages(text: str) -> set:
    out = set()
    for m in PERCENT_RE.finditer(text or ""):
        out.add(round(_to_float(m.group(1)), 2))
    for phrase, pct in FRACTION_WORD_TO_PERCENT.items():
        if re.search(r"\b" + re.escape(phrase) + r"\b", text or "", re.IGNORECASE):
            out.add(round(pct, 2))
    return out


def extract_counts(text: str) -> set:
    out = set()
    for m in COUNT_WORD_RE.finditer(text or ""):
        out.add(_to_float(m.group(1)) * _COUNT_MULT[m.group(2).lower()])
    for m in JP_MAN_RE.finditer(text or ""):
        out.add(_to_float(m.group(1)) * 1e4)
    for m in JP_OKU_RE.finditer(text or ""):
        out.add(_to_float(m.group(1)) * 1e8)
    return out


def _numbers_close(a: float, b: float, rel_tol: float = 0.05) -> bool:
    if a == b:
        return True
    return abs(a - b) <= rel_tol * max(abs(a), abs(b), 1.0)


def _any_close(expected: set, observed: set, rel_tol: float = 0.05) -> bool:
    return any(_numbers_close(a, b, rel_tol) for a in expected for b in observed)


def check_number_mismatch(fact: dict, article_text: str,
                           all_ledger_pct: set | None = None,
                           all_ledger_cnt: set | None = None) -> dict | None:
    """単一の主要数値(percentまたはcount)を持つFactに限定してmismatchを
    判定する(複数の数値が並ぶFact[OHLC四本値等]はFPリスクが高いため対象外、
    設計原則を参照)。

    `all_ledger_pct`/`all_ledger_cnt`(Ledger全体の他Factが持つ数値の
    和集合)を渡した場合、記事側で見つかった「異なる数値」が実は
    **同じLedgerの別Factの正しい値**である場合(Family X記事は複数Factの
    数値を1記事内で併記することが多い)を誤ってmismatch扱いしないよう
    除外する(FP回避、Phase 1実測で判明した必須の補正)。"""
    numeric_value = fact.get("numeric_value")
    if not numeric_value:
        return None

    ledger_pct = extract_percentages(numeric_value)
    ledger_cnt = extract_counts(numeric_value)

    # 主要数値が一意に定まる場合のみ判定(percent 1種類のみ、または
    # count 1種類のみ。両方混在・複数値はスキップ)。
    if len(ledger_pct) == 1 and len(ledger_cnt) == 0:
        expected = ledger_pct
        observed = extract_percentages(article_text)
        other_ledger_values = (all_ledger_pct or set()) - expected
        kind_label = "percent"
    elif len(ledger_cnt) == 1 and len(ledger_pct) == 0:
        expected = ledger_cnt
        observed = extract_counts(article_text)
        other_ledger_values = (all_ledger_cnt or set()) - expected
        kind_label = "count"
    else:
        return None

    if not observed:
        # 記事側に同種の数値が全く無い(=単なる省略の可能性が高い) -> 判定不能、FP回避のため何もしない
        return None
    if _any_close(expected, observed):
        return None
    # 記事側の「異なる数値」が、同じLedgerの別Factの正しい値であれば
    # このFactの取り違え証拠にはならない(除外)。
    foreign_observed = {o for o in observed if not _any_close({o}, other_ledger_values)}
    if not foreign_observed:
        return None
    # Ledger値が本文に無く、かつLedgerのどのFactにも属さない異なる同種数値が
    # 本文に存在する
    return {
        "field": fact["fact_id"],
        "ledger_value": numeric_value,
        "article_evidence": f"{kind_label} values found in article not matching any ledger fact: {sorted(foreign_observed)}",
        "kind": "number_mismatch",
        "detected_by": "precheck",
    }


# ------------------------------------------------------------
# 4. 日付抽出・比較
# ------------------------------------------------------------
ISO_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
JP_DATE_RE = re.compile(r"(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日")
_MONTH_ALT = "|".join(MONTH_NAMES + MONTH_ABBREV)
ENGLISH_DATE_RE = re.compile(
    r"\b(" + _MONTH_ALT + r")\.?\s+(\d{1,2})(?:,?\s*(\d{4}))?\b"
)
_MONTH_INDEX = {m: i + 1 for i, m in enumerate(MONTH_NAMES)}
_MONTH_INDEX.update({m: i + 1 for i, m in enumerate(MONTH_ABBREV)})


def _weekday_name(year: int, month: int, day: int) -> str | None:
    import datetime
    try:
        return WEEKDAY_NAMES[datetime.date(year, month, day).weekday()]
    except ValueError:
        return None


def extract_calendar_dates(text: str, default_year: int | None = None) -> list[tuple]:
    """text中のISO日付(YYYY-MM-DD)・和暦表記(M月D日)を(year, month, day)の
    tupleへ正規化して返す(year不明の和暦表記はdefault_yearを補う)。"""
    out = []
    for m in ISO_DATE_RE.finditer(text or ""):
        out.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    for m in JP_DATE_RE.finditer(text or ""):
        y = int(m.group(1)) if m.group(1) else default_year
        if y is None:
            continue
        out.append((y, int(m.group(2)), int(m.group(3))))
    for m in ENGLISH_DATE_RE.finditer(text or ""):
        y = int(m.group(3)) if m.group(3) else default_year
        if y is None:
            continue
        month = _MONTH_INDEX.get(m.group(1))
        if month is None:
            continue
        out.append((y, month, int(m.group(2))))
    return out


def _date_representations(year: int, month: int, day: int) -> list[str]:
    reps = []
    mn = MONTH_NAMES[month - 1]
    ma = MONTH_ABBREV[month - 1]
    reps.append(f"{mn} {day}")
    reps.append(f"{mn} {day}, {year}")
    reps.append(f"{ma} {day}")
    reps.append(f"{year}-{month:02d}-{day:02d}")
    wd = _weekday_name(year, month, day)
    if wd:
        reps.append(wd)
    return reps


def check_date_mismatch(fact: dict, article_text: str,
                         all_ledger_dates: set | None = None) -> dict | None:
    date_field = fact.get("date_or_period")
    if not date_field:
        return None
    dates = extract_calendar_dates(date_field)
    if len(dates) != 1:
        # 複数日付・範囲(例: 会期の開始〜終了)はどれを主要日付とするか
        # 一意に定まらないためスキップ(FP回避)。
        return None
    year, month, day = dates[0]
    reps = _date_representations(year, month, day)
    if any(re.search(re.escape(rep), article_text) for rep in reps):
        return None
    # Ledger日付のいかなる正規化表現も本文に無い。ただし「別の日付が本文の
    # 同種文脈に現れる」ことを要求する(単なる日付省略との区別)。
    other_dates = extract_calendar_dates(article_text, default_year=year)
    other_dates = [d for d in other_dates if d != (year, month, day)]
    # 記事側の「異なる日付」が、同じLedgerの別Factの正しい日付であれば
    # このFactの取り違え証拠にはならない(number_mismatchと同じ補正)。
    other_ledger_dates = (all_ledger_dates or set()) - {(year, month, day)}
    other_dates = [d for d in other_dates if d not in other_ledger_dates]
    if not other_dates:
        return None
    return {
        "field": fact["fact_id"],
        "ledger_value": date_field,
        "article_evidence": f"different date(s) found in article not matching any ledger fact: {other_dates}",
        "kind": "date_mismatch",
        "detected_by": "precheck",
    }


# ------------------------------------------------------------
# 5. 主体(actor)抽出・比較
# ------------------------------------------------------------
STOPWORDS_CAP = {
    "The", "This", "That", "These", "Those", "It", "Its", "They", "Their",
    "He", "She", "We", "Our", "You", "Your", "I",
    "In", "On", "At", "As", "If", "But", "And", "Or", "So", "Even", "Also",
    "After", "Before", "When", "While", "However", "Normally", "Meanwhile",
    "Still", "Yet", "Now", "Then", "Here", "There", "One", "Some", "Many",
    "Few", "Most", "All", "Each", "Every", "No", "None", "Not", "Only",
    "According", "Because", "Since", "Although", "Though", "Unlike",
    "Instead", "Overall", "Point", "Main", "Story", "Line",
    "Spring", "Summer", "Fall", "Winter",
    # 文頭に来やすい助動詞・分詞(一般語、fixture固有ではない)。単発の
    # 文頭大文字化を固有名詞候補として誤検出しないための汎用stopword。
    "Can", "Could", "Would", "Should", "Will", "May", "Might", "Must",
    "Looking", "Considering", "Given", "Regarding", "Speaking", "Turning",
    "Moving", "Coming", "Going", "Let", "Why", "How", "What", "Who", "Which",
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
}

PROPER_NOUN_RE = re.compile(
    r"\b[A-Z][a-zA-Z]+(?:['’][A-Za-z]+)?(?:[ ]+[A-Z][a-zA-Z]+(?:['’][A-Za-z]+)?){0,3}\b"
)


def _strip_markdown_headings(text: str) -> str:
    """見出し行("#"始まり)を除去したtextを返す(見出しはTitle Case慣習で
    ほぼ全単語が大文字化されるため、proper noun抽出のノイズ源になる。
    Phase1実測[委任_06]で判明した必須の補正。actor本文中の言及検出
    [_actor_present_in_article]には適用しない、見出し内の正当な言及を
    見逃さないため)。"""
    lines = [ln for ln in (text or "").split("\n") if not ln.lstrip().startswith("#")]
    return "\n".join(lines)

ATTRIBUTIVE_VERBS = {
    "announced", "said", "stated", "found", "reported", "confirmed", "warned",
    "canceled", "cancelled", "approved", "ordered", "raised", "cut", "removed",
    "introduced", "launched", "conducted", "showed", "revealed", "studied",
    "discovered", "noted", "added", "explained", "denied", "planned",
    "proposed", "urged", "predicted", "forecast", "posted", "told", "wrote",
    "issued", "declared", "acknowledged", "requested", "demanded",
}

GENERIC_ACTOR_WHITELIST = {
    "United States", "Gulf", "Middle East", "Middle Eastern",
}


def extract_proper_nouns(text: str) -> set:
    out = set()
    for m in PROPER_NOUN_RE.finditer(text or ""):
        phrase = m.group(0)
        words = phrase.split()
        if all(w in STOPWORDS_CAP for w in words):
            continue
        if len(words) == 1 and words[0] in STOPWORDS_CAP:
            continue
        out.add(phrase)
    return out


def _strip_honorific(phrase: str) -> str:
    for h in HONORIFIC_PREFIXES:
        if phrase.startswith(h + " "):
            return phrase[len(h) + 1:]
    return phrase


def _strip_possessive(phrase: str) -> str:
    """"Celine's"/"Celine’s" -> "Celine"(所有格差を吸収し、Ledger本文
    (bare形)と記事本文(所有格形)の表記差を誤ってactor_missingの証拠に
    しないため、Phase1実測[委任_06]で判明した必須の補正)。"""
    for suffix in ("'s", "’s"):
        if phrase.endswith(suffix):
            return phrase[: -len(suffix)]
    return phrase


def _looks_like_common_word_artifact(phrase: str, text: str) -> bool:
    """Title Case見出し・文頭の大文字化による誤検出(例: "Bags"/"Can"が
    固有名詞候補として抽出される)を除外する。phraseを構成する全単語が、
    同じtext内に小文字始まりでも出現する場合、真の固有名詞ではなく単なる
    通常語の大文字化と判断する(Phase1実測[委任_06]で判明した必須の補正)。"""
    for w in phrase.split():
        if not w:
            return False
        lw = w[0].lower() + w[1:]
        if not re.search(r"\b" + re.escape(lw) + r"\b", text):
            return False
    return True


def _actor_present_in_article(actor_phrase: str, article_text: str) -> bool:
    core = _strip_honorific(actor_phrase)
    if re.search(r"\b" + re.escape(core) + r"\b", article_text):
        return True
    last_word = core.split()[-1]
    if len(last_word) >= 3 and re.search(r"\b" + re.escape(last_word) + r"\b", article_text):
        return True
    return False


def _is_attributive_claim(claim: str) -> bool:
    lowered = claim.lower()
    return any(re.search(r"\b" + v + r"\b", lowered) for v in ATTRIBUTIVE_VERBS)


def check_actor_missing(fact: dict, article_text: str, all_ledger_actor_tokens: set) -> dict | None:
    claim = fact.get("claim") or ""
    if not _is_attributive_claim(claim):
        return None
    actor_tokens = extract_proper_nouns(claim) - GENERIC_ACTOR_WHITELIST
    if not actor_tokens:
        return None
    if any(_actor_present_in_article(a, article_text) for a in actor_tokens):
        return None
    # Ledgerが特定する主体が本文に一切現れない。別の主体固有名詞
    # (ledger全体のどのfactの主体にも属さない、記事側だけの新規名詞)が
    # 本文に現れる場合のみ、実際の取り違えの可能性が高いとみなす。
    normalized_ledger_tokens = {_strip_possessive(t) for t in all_ledger_actor_tokens}
    # 複合phrase(例: "Celine's Ultra Maxi")のうち、先頭語(所有格除去後)が
    # Ledger既知語("Celine")と一致する場合、末尾の修飾語(製品名の言い換え等)
    # が完全一致しなくても「Ledger既知の主体」として扱う(head-word一致)。
    ledger_head_words = {tok.split()[0] for tok in normalized_ledger_tokens if tok.split()}
    body_text = _strip_markdown_headings(article_text)
    article_candidates = set()
    for cand in extract_proper_nouns(body_text):
        if cand in GENERIC_ACTOR_WHITELIST:
            continue
        normalized_cand = _strip_possessive(cand)
        if normalized_cand in normalized_ledger_tokens:
            continue
        head_word = _strip_possessive(cand.split()[0])
        if head_word in ledger_head_words:
            continue
        if _looks_like_common_word_artifact(cand, body_text):
            continue
        article_candidates.add(cand)
    if not article_candidates:
        return None
    return {
        "field": fact["fact_id"],
        "ledger_value": sorted(actor_tokens),
        "article_evidence": sorted(article_candidates)[:5],
        "kind": "actor_missing",
        "detected_by": "precheck",
    }


# ------------------------------------------------------------
# 6. 否定・比較マーカー(narrow rule、委任文の例には無いが出力kind enumに
# 含まれるため実装する。exact-strip一致のみを要求する非常に狭い規則
# であり、意図的に検出率よりFP回避を優先する)
# ------------------------------------------------------------
NEGATION_WORDS = ["not", "no longer", "never", "without", "did not", "does not"]
COMPARISON_ANTONYMS = [
    ("more", "less"), ("higher", "lower"), ("increase", "decrease"),
    ("rose", "fell"), ("gained", "lost"), ("up", "down"), ("rise", "fall"),
]


def check_negation_marker(fact: dict, article_text: str) -> dict | None:
    claim = fact.get("claim") or ""
    lowered = claim.lower()
    for neg in NEGATION_WORDS:
        idx = lowered.find(neg)
        if idx == -1:
            continue
        stripped = (lowered[:idx] + lowered[idx + len(neg):]).strip()
        stripped = re.sub(r"\s+", " ", stripped)
        if len(stripped) < 8:
            continue
        if stripped and stripped in article_text.lower():
            return {
                "field": fact["fact_id"],
                "ledger_value": claim,
                "article_evidence": stripped,
                "kind": "negation_marker",
                "detected_by": "precheck",
            }
    return None


def check_comparison_marker(fact: dict, article_text: str) -> dict | None:
    claim = fact.get("claim") or ""
    lowered = claim.lower()
    article_lowered = (article_text or "").lower()
    for a, b in COMPARISON_ANTONYMS:
        for word, antonym in ((a, b), (b, a)):
            if re.search(r"\b" + word + r"\b", lowered):
                stripped = re.sub(r"\b" + word + r"\b", antonym, lowered)
                if stripped in article_lowered:
                    return {
                        "field": fact["fact_id"],
                        "ledger_value": claim,
                        "article_evidence": f"antonym '{antonym}' phrase found verbatim in article",
                        "kind": "comparison_marker",
                        "detected_by": "precheck",
                    }
    return None


# ------------------------------------------------------------
# 7. 統合エントリポイント
# ------------------------------------------------------------
def run_precheck(ledger_text: str, article_text: str) -> list[dict]:
    """Ledger textと記事本文を受け取り、precheck_findings(list[dict])を
    返す。API呼び出しなし(¥0)。VERIFIEDタグのFactのみ対象とする
    (AMBIGUOUSは意図的な曖昧さを保持したFactであり、機械照合による
    FPリスクが高いため対象外、fail-safe側に倒す)。"""
    facts = parse_ledger_text(ledger_text)
    verified_facts = [f for f in facts if f.get("verdict") in ("VERIFIED", "UNKNOWN")]

    # actor語彙はclaim以外のフィールド(scope/conditions/notes_for_writer等)
    # にも現れる固有名詞(例: 地名)を含めて広めに集める(FP回避)。
    all_ledger_actor_tokens: set = set()
    all_ledger_pct: set = set()
    all_ledger_cnt: set = set()
    all_ledger_dates: set = set()
    for f in facts:
        for key in ("claim", "scope", "conditions", "notes_for_writer", "numeric_value"):
            all_ledger_actor_tokens |= extract_proper_nouns(f.get(key) or "")
        nv = f.get("numeric_value") or ""
        all_ledger_pct |= extract_percentages(nv)
        all_ledger_cnt |= extract_counts(nv)
        dop = f.get("date_or_period") or ""
        for d in extract_calendar_dates(dop):
            all_ledger_dates.add(d)

    findings = []
    for fact in verified_facts:
        for check in (
            lambda f: check_actor_missing(f, article_text, all_ledger_actor_tokens),
            lambda f: check_number_mismatch(f, article_text, all_ledger_pct, all_ledger_cnt),
            lambda f: check_date_mismatch(f, article_text, all_ledger_dates),
            lambda f: check_negation_marker(f, article_text),
            lambda f: check_comparison_marker(f, article_text),
        ):
            result = check(fact)
            if result is not None:
                findings.append(result)
    return findings
