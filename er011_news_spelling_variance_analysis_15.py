#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
er011_news_spelling_variance_analysis_15.py
FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15
Fable修正指示1回目(¥0追加分析のみ): 既存article.mdの機械解析による
綴り揺れ(spelling variance)の直接計測。

新規API呼び出しは一切行わない。既存article.md(Trial-12/12b/14/15)を
読み取り専用で機械解析するのみ。

管理ID: PM-CLOSEOUT-CONSOLIDATION-82-JA-ASR-VARIANT-AND-LEDGER-SPELLING-
TRIALS(再現性確保のためscratchpad一時scriptをrepoへコピー、ロジック・
出力先は元scriptと完全に同一。パスのみrepo相対[スクリプト自身の場所基準]
へ修正)。
"""
import json, os, re, math
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.abspath(__file__))

# 条件 -> ディレクトリテンプレート ( {lvl} in a2/b1b, {r} in 1/2/3 )
CONDITION_DIRS = {
    "A": os.path.join(ROOT, "er011_output", "news_ledger_enrichment_ab_trial_12", "{lvl}", "current", "run{r}"),
    "B": os.path.join(ROOT, "er011_output", "news_ledger_enrichment_ab_trial_12", "{lvl}", "enriched", "run{r}"),
    "C": os.path.join(ROOT, "er011_output", "news_ledger_enrichment_ab_trial_12", "leaveout_c", "{lvl}", "run{r}"),
    "D": os.path.join(ROOT, "er011_output", "news_ledger_enrichment_ab_trial_12", "twofact_d", "{lvl}", "run{r}"),
    "E": os.path.join(ROOT, "er011_output", "news_ledger_enrichment_ab_trial_12", "twofact_e", "{lvl}", "run{r}"),
    "F": os.path.join(ROOT, "er011_output", "news_ledger_canonical_spelling_trial_15", "condition_f", "{lvl}", "run{r}"),
}
# 出典(元Trial): A/B = Trial-12, C = Trial-12b, D/E = Trial-14, F = Trial-15
CONDITION_SOURCE_TRIAL = {"A": "Trial-12", "B": "Trial-12", "C": "Trial-12b", "D": "Trial-14", "E": "Trial-14", "F": "Trial-15"}

LEVELS = ["a2", "b1b"]
RUNS = [1, 2, 3]

# Trial-15段階1で確定した公式英語表記(10件)
CANONICAL = {
    "佐藤輝明": "Teruaki Sato",
    "伊原陵人": "Takato Ihara",
    "森翔平": "Shohei Mori",
    "坂本誠志郎": "Seishiro Sakamoto",
    "伏見寅威": "Torai Fushimi",
    "森下翔太": "Shota Morishita",
    "E・モンテロ": "Elehuris Montero",
    "阪神タイガース": "Hanshin Tigers",
    "広島東洋カープ": "Hiroshima Toyo Carp",
    "マツダスタジアム": "MAZDA Zoom-Zoom Stadium Hiroshima",
}

# 抽出規則(正規表現、抽出規則を明記する):
# 人名5種(姓の直前の与えられた名トークンをキャプチャし、公式の与えられた名と比較)。
# Mori は Morishita の部分文字列になるため (?!shita) で除外。
PERSON_RULES = [
    # (japanese_key, surname_regex_capture_given_name, official_given_name, official_full)
    # 同一行内(段落・見出しをまたがない)の直前トークンのみを対象とするため
    # \s+ ではなく [ \t]+ を使用する(改行2つを挟む見出し境界の誤検出を防ぐ)。
    ("佐藤輝明", r"\b([A-Z][a-zA-Z]*)[ \t]+Sato\b", "Teruaki", "Teruaki Sato"),
    ("伊原陵人", r"\b([A-Z][a-zA-Z]*)[ \t]+Ihara\b", "Takato", "Takato Ihara"),
    ("森翔平", r"\b([A-Z][a-zA-Z]*)[ \t]+Mori\b(?!shita)", "Shohei", "Shohei Mori"),
    ("坂本誠志郎", r"\b([A-Z][a-zA-Z]*)[ \t]+Sakamoto\b", "Seishiro", "Seishiro Sakamoto"),
    ("伏見寅威", r"\b([A-Z][a-zA-Z]*)[ \t]+Fushimi\b", "Torai", "Torai Fushimi"),
    ("森下翔太", r"\b([A-Z][a-zA-Z]*)[ \t]+Morishita\b", "Shota", "Shota Morishita"),
    ("E・モンテロ", r"\b([A-Z][a-zA-Z]*)[ \t]+Montero\b", "Elehuris", "Elehuris Montero"),
]

# 文頭で偶然大文字化された非人名トークン(前置詞・接続詞等)を、姓単独言及
# (given nameなしでSato/Ihara等の姓だけで指した文)から誤って「与えられた名」
# として抽出しないための除外リスト(観測された全候補を目視確認の上で決定、
# 固有名詞らしい候補[Rito/Ryohto/Rihito/Ryoto/Taketo/Tora/Tai/Torae/Tori等]は
# 除外リストに含めていない)。
NON_NAME_STOPWORDS = {
    "After", "Before", "While", "From", "With", "But", "And", "On", "To", "In",
    "At", "By", "Of", "For", "So", "Then", "When", "As", "The", "A", "An",
    "Only", "Instead", "Behind", "Turned", "Moved", "Left", "Brought",
    "Trusted", "Was", "Hit", "Is", "It", "This", "That", "Once", "Later",
}

# 団体名/施設名3種(固定文字列としての表記ゆれをスキャン。
# 「Hanshin」「Carp」等の単独短縮形は正式名称への言及の試みとみなさず
# 除外し、2語以上のチーム名/球場名らしきパターンのみを対象とする)。
ORG_RULES = [
    ("阪神タイガース", r"\bHanshin\s+Tigers?\b", "Hanshin Tigers"),
    ("広島東洋カープ", r"\bHiroshima\s+(?:Toyo\s+)?Carps?\b", "Hiroshima Toyo Carp"),
    ("マツダスタジアム", r"\b(?:MAZDA|Mazda)\s+(?:Zoom-Zoom\s+)?Stadium(?:\s+Hiroshima)?\b", "MAZDA Zoom-Zoom Stadium Hiroshima"),
]


def load_article(cond, lvl, run):
    d = CONDITION_DIRS[cond].format(lvl=lvl, r=run)
    fp = os.path.join(d, "article.md")
    if not os.path.exists(fp):
        return None, d
    with open(fp, encoding="utf-8") as f:
        return f.read(), d


def load_analysis(cond, lvl, run):
    d = CONDITION_DIRS[cond].format(lvl=lvl, r=run)
    fp = os.path.join(d, "analysis.json")
    if not os.path.exists(fp):
        return None
    with open(fp, encoding="utf-8") as f:
        return json.load(f)


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    denom = 1 + z * z / n
    center = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    lo = (center - margin) / denom
    hi = (center + margin) / denom
    return (max(0.0, lo), min(1.0, hi))


def fisher_exact_2x2(a, b, c, d):
    """2x2 Fisher's exact test (two-sided), computed via hypergeometric pmf sum.
    Table:
        a  b
        c  d
    """
    def logfact(n):
        return math.lgamma(n + 1)

    n = a + b + c + d
    row1 = a + b
    row2 = c + d
    col1 = a + c
    col2 = b + d

    def hyper_logp(x):
        # P(a=x) given fixed margins row1,row2,col1,col2
        if x < 0 or x > row1 or (col1 - x) < 0 or (col1 - x) > row2:
            return None
        return (logfact(row1) + logfact(row2) + logfact(col1) + logfact(col2)
                - logfact(n) - logfact(x) - logfact(row1 - x)
                - logfact(col1 - x) - logfact(row2 - col1 + x))

    p_obs = hyper_logp(a)
    if p_obs is None:
        return None
    p_obs_val = math.exp(p_obs)
    total = 0.0
    lo = max(0, col1 - row2)
    hi = min(row1, col1)
    for x in range(lo, hi + 1):
        lp = hyper_logp(x)
        if lp is None:
            continue
        pv = math.exp(lp)
        if pv <= p_obs_val * (1 + 1e-9):
            total += pv
    return min(1.0, total)


def main():
    records = []  # per-occurrence records
    article_level_summary = []  # per-article per-person summary (for within-article inconsistency)
    fc_pass_with_error = []  # item 4: FC PASS articles that still had a wrong given name

    for cond in ["A", "B", "C", "D", "E", "F"]:
        for lvl in LEVELS:
            for run in RUNS:
                text, d = load_article(cond, lvl, run)
                if text is None:
                    continue
                analysis = load_analysis(cond, lvl, run)
                fact_verdict = analysis.get("fact_verdict") if analysis else None
                status = analysis.get("status") if analysis else None

                article_id = f"{cond}/{lvl}/run{run}"

                # 人名5種
                for jp_key, pattern, official_given, official_full in PERSON_RULES:
                    raw_matches = list(re.finditer(pattern, text))
                    excluded_surname_only = [m for m in raw_matches if m.group(1) in NON_NAME_STOPWORDS]
                    matches = [m for m in raw_matches if m.group(1) not in NON_NAME_STOPWORDS]
                    variants_in_article = []
                    for m in matches:
                        given = m.group(1)
                        rec = {
                            "condition": cond,
                            "source_trial": CONDITION_SOURCE_TRIAL[cond],
                            "level": lvl,
                            "run": run,
                            "article_id": article_id,
                            "entity_jp": jp_key,
                            "entity_type": "person",
                            "official_full": official_full,
                            "extracted_given_name": given,
                            "match_span_text": m.group(0),
                            "is_official_match": (given == official_given),
                            "fact_verdict": fact_verdict,
                            "status": status,
                        }
                        records.append(rec)
                        variants_in_article.append(given)
                        if fact_verdict == "PASS" and given != official_given:
                            fc_pass_with_error.append(rec)
                    if matches or excluded_surname_only:
                        article_level_summary.append({
                            "condition": cond,
                            "article_id": article_id,
                            "entity_jp": jp_key,
                            "occurrences": len(matches),
                            "distinct_variants": sorted(set(variants_in_article)),
                            "within_article_inconsistent": len(set(variants_in_article)) > 1,
                            "excluded_surname_only_mentions": [m.group(0) for m in excluded_surname_only],
                        })

                # 団体名/施設名3種
                for jp_key, pattern, official_full in ORG_RULES:
                    matches = list(re.finditer(pattern, text))
                    variants_in_article = []
                    for m in matches:
                        found = m.group(0)
                        is_match = (found == official_full) or (
                            jp_key == "マツダスタジアム" and found.strip() == "Mazda Stadium"
                        )
                        # 施設名は「Mazda Stadium」(通称・短縮形)と
                        # 「MAZDA Zoom-Zoom Stadium Hiroshima」(NPB公式フル表記)を
                        # 区別して記録する(短縮形は誤記ではなく通称のため
                        # is_official_match=Falseだが is_common_shortform=True として別集計)。
                        rec = {
                            "condition": cond,
                            "source_trial": CONDITION_SOURCE_TRIAL[cond],
                            "level": lvl,
                            "run": run,
                            "article_id": article_id,
                            "entity_jp": jp_key,
                            "entity_type": "org_or_facility",
                            "official_full": official_full,
                            "extracted_text": found,
                            "is_official_match": (found == official_full),
                            "is_common_shortform": (jp_key == "マツダスタジアム" and found.strip() == "Mazda Stadium")
                                                    or (jp_key == "広島東洋カープ" and found.strip() == "Hiroshima Carp"),
                            "fact_verdict": fact_verdict,
                            "status": status,
                        }
                        records.append(rec)
                        variants_in_article.append(found)
                    if matches:
                        article_level_summary.append({
                            "condition": cond,
                            "article_id": article_id,
                            "entity_jp": jp_key,
                            "occurrences": len(matches),
                            "distinct_variants": sorted(set(variants_in_article)),
                            "within_article_inconsistent": len(set(variants_in_article)) > 1,
                        })

    # ---- 集計: 人名5種のみ(団体名/施設名は短縮形の解釈が別なので分離集計) ----
    person_records = [r for r in records if r["entity_type"] == "person"]
    org_records = [r for r in records if r["entity_type"] == "org_or_facility"]

    def summarize_condition(cond, recs):
        n = len(recs)
        n_match = sum(1 for r in recs if r["is_official_match"])
        return {"n_occurrences": n, "n_official_match": n_match,
                "n_mismatch": n - n_match,
                "match_rate": (n_match / n) if n else None}

    per_condition_person = {}
    for cond in ["A", "B", "C", "D", "E", "F"]:
        recs = [r for r in person_records if r["condition"] == cond]
        per_condition_person[cond] = summarize_condition(cond, recs)

    # per entity per condition breakdown + distinct given-name variants
    per_entity_condition = defaultdict(lambda: defaultdict(list))
    for r in person_records:
        per_entity_condition[r["entity_jp"]][r["condition"]].append(r["extracted_given_name"])

    entity_table = {}
    for jp_key, official_given, official_full in [(x[0], x[2], x[3]) for x in PERSON_RULES]:
        entity_table[jp_key] = {"official_full": official_full, "by_condition": {}}
        for cond in ["A", "B", "C", "D", "E", "F"]:
            givens = per_entity_condition[jp_key].get(cond, [])
            n = len(givens)
            n_match = sum(1 for g in givens if g == official_given)
            entity_table[jp_key]["by_condition"][cond] = {
                "n_occurrences": n,
                "n_official_match": n_match,
                "n_mismatch": n - n_match,
                "distinct_variants": dict(Counter(givens)),
            }

    # ---- 条件A-E統合(対照群)vs F の比較(人名5種プール) ----
    pooled_AE = [r for r in person_records if r["condition"] in ("A", "B", "C", "D", "E")]
    pooled_F = [r for r in person_records if r["condition"] == "F"]

    n_ae = len(pooled_AE)
    match_ae = sum(1 for r in pooled_AE if r["is_official_match"])
    mismatch_ae = n_ae - match_ae

    n_f = len(pooled_F)
    match_f = sum(1 for r in pooled_F if r["is_official_match"])
    mismatch_f = n_f - match_f

    ci_ae = wilson_ci(match_ae, n_ae)
    ci_f = wilson_ci(match_f, n_f)

    # Fisher's exact test on match/mismatch 2x2 (AE vs F)
    p_value = fisher_exact_2x2(match_ae, mismatch_ae, match_f, mismatch_f)

    # ---- 「揺れ発生記事率」: 条件×記事単位で、人名5種のうち1つでも
    # 公式表記と不一致だった記事の割合 ----
    article_has_mismatch = defaultdict(dict)  # (cond, article_id) -> bool
    for r in person_records:
        key = (r["condition"], r["article_id"])
        cur = article_has_mismatch.get(key, False)
        article_has_mismatch[key] = cur or (not r["is_official_match"])

    variance_article_rate_by_condition = {}
    for cond in ["A", "B", "C", "D", "E", "F"]:
        keys = [k for k in article_has_mismatch if k[0] == cond]
        n_articles = len(keys)
        n_with_mismatch = sum(1 for k in keys if article_has_mismatch[k])
        variance_article_rate_by_condition[cond] = {
            "n_articles": n_articles,
            "n_articles_with_mismatch": n_with_mismatch,
            "rate": (n_with_mismatch / n_articles) if n_articles else None,
        }

    n_articles_ae = sum(1 for k in article_has_mismatch if k[0] in ("A", "B", "C", "D", "E"))
    n_articles_ae_mismatch = sum(1 for k in article_has_mismatch if k[0] in ("A", "B", "C", "D", "E") and article_has_mismatch[k])
    n_articles_f = sum(1 for k in article_has_mismatch if k[0] == "F")
    n_articles_f_mismatch = sum(1 for k in article_has_mismatch if k[0] == "F" and article_has_mismatch[k])

    # ---- 人物ごとの異表記数(条件A-E統合、条件Fで、それぞれ何種類の異なる
    # 与えられた名スペルが出現したか) ----
    variant_counts_by_entity = {}
    for jp_key, official_given, official_full in [(x[0], x[2], x[3]) for x in PERSON_RULES]:
        ae_givens = []
        f_givens = []
        for cond in ["A", "B", "C", "D", "E"]:
            ae_givens += per_entity_condition[jp_key].get(cond, [])
        f_givens = per_entity_condition[jp_key].get("F", [])
        variant_counts_by_entity[jp_key] = {
            "official_given_name": official_given,
            "AE_pooled_distinct_variants": dict(Counter(ae_givens)),
            "AE_pooled_n_distinct": len(set(ae_givens)),
            "AE_pooled_n_occurrences": len(ae_givens),
            "AE_pooled_n_match": sum(1 for g in ae_givens if g == official_given),
            "F_distinct_variants": dict(Counter(f_givens)),
            "F_n_distinct": len(set(f_givens)),
            "F_n_occurrences": len(f_givens),
            "F_n_match": sum(1 for g in f_givens if g == official_given),
        }

    # ---- 団体名/施設名の集計(短縮形と真の誤記を区別) ----
    org_table = {}
    for jp_key, _pat, official_full in ORG_RULES:
        recs = [r for r in org_records if r["entity_jp"] == jp_key]
        by_cond = {}
        for cond in ["A", "B", "C", "D", "E", "F"]:
            crecs = [r for r in recs if r["condition"] == cond]
            variants = Counter(r["extracted_text"] for r in crecs)
            by_cond[cond] = {
                "n_occurrences": len(crecs),
                "n_official_full_match": sum(1 for r in crecs if r["is_official_match"]),
                "n_common_shortform": sum(1 for r in crecs if r["is_common_shortform"]),
                "n_other": sum(1 for r in crecs if (not r["is_official_match"]) and (not r["is_common_shortform"])),
                "distinct_variants": dict(variants),
            }
        org_table[jp_key] = {"official_full": official_full, "by_condition": by_cond}

    # ---- FCがPASSした記事に含まれていた綴り誤り(item4) ----
    fc_pass_error_list = []
    for r in fc_pass_with_error:
        fc_pass_error_list.append({
            "condition": r["condition"],
            "source_trial": r["source_trial"],
            "article_id": r["article_id"],
            "entity_jp": r["entity_jp"],
            "official_full": r["official_full"],
            "extracted_given_name": r["extracted_given_name"],
            "match_span_text": r["match_span_text"],
            "fact_verdict": r["fact_verdict"],
        })

    headline = {
        "note": "最も揺れが検出された2エンティティの要約(全文詳細はentity_table_person参照)",
        "伊原陵人_given_name_Takato": {
            "AE_pooled_occurrences": variant_counts_by_entity["伊原陵人"]["AE_pooled_n_occurrences"],
            "AE_pooled_correct": variant_counts_by_entity["伊原陵人"]["AE_pooled_n_match"],
            "AE_pooled_error_rate": 1 - (variant_counts_by_entity["伊原陵人"]["AE_pooled_n_match"] / variant_counts_by_entity["伊原陵人"]["AE_pooled_n_occurrences"]) if variant_counts_by_entity["伊原陵人"]["AE_pooled_n_occurrences"] else None,
            "AE_pooled_distinct_wrong_variants": {k: v for k, v in variant_counts_by_entity["伊原陵人"]["AE_pooled_distinct_variants"].items() if k != "Takato"},
            "F_occurrences": variant_counts_by_entity["伊原陵人"]["F_n_occurrences"],
            "F_correct": variant_counts_by_entity["伊原陵人"]["F_n_match"],
        },
        "伏見寅威_given_name_Torai": {
            "AE_pooled_occurrences": variant_counts_by_entity["伏見寅威"]["AE_pooled_n_occurrences"],
            "AE_pooled_correct": variant_counts_by_entity["伏見寅威"]["AE_pooled_n_match"],
            "AE_pooled_error_rate": 1 - (variant_counts_by_entity["伏見寅威"]["AE_pooled_n_match"] / variant_counts_by_entity["伏見寅威"]["AE_pooled_n_occurrences"]) if variant_counts_by_entity["伏見寅威"]["AE_pooled_n_occurrences"] else None,
            "AE_pooled_distinct_wrong_variants": {k: v for k, v in variant_counts_by_entity["伏見寅威"]["AE_pooled_distinct_variants"].items() if k != "Torai"},
            "F_occurrences": variant_counts_by_entity["伏見寅威"]["F_n_occurrences"],
            "F_correct": variant_counts_by_entity["伏見寅威"]["F_n_match"],
        },
        "other_5_entities_(Sato/Sakamoto/Mori/Morishita/Montero)": "AE・Fともに揺れ0件(全occurrence が公式表記と完全一致)",
    }

    output = {
        "headline_metrics": headline,
        "meta": {
            "management_id": "FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15",
            "task": "Fable修正指示1回目(\u00a50追加分析、新規API呼び出しなし、既存article.md機械解析のみ)",
            "condition_to_directory_and_source_trial": {
                "A": {"dir": "news_ledger_enrichment_ab_trial_12/{a2,b1b}/current/run{1,2,3}", "source_trial": "Trial-12", "ledger": "FACT-01~07(現行Ledger)"},
                "B": {"dir": "news_ledger_enrichment_ab_trial_12/{a2,b1b}/enriched/run{1,2,3}", "source_trial": "Trial-12", "ledger": "A+FACT-08~14(拡充)"},
                "C": {"dir": "news_ledger_enrichment_ab_trial_12/leaveout_c/{a2,b1b}/run{1,2,3}", "source_trial": "Trial-12b", "ledger": "leaveout(抜き取り対照)"},
                "D": {"dir": "news_ledger_enrichment_ab_trial_12/twofact_d/{a2,b1b}/run{1,2,3}", "source_trial": "Trial-14", "ledger": "A+FACT-08/09(2件追加)"},
                "E": {"dir": "news_ledger_enrichment_ab_trial_12/twofact_e/{a2,b1b}/run{1,2,3}", "source_trial": "Trial-14", "ledger": "A+FACT-11/14(2件追加、canonical_en_spellingなし)"},
                "F": {"dir": "news_ledger_canonical_spelling_trial_15/condition_f/{a2,b1b}/run{1,2,3}", "source_trial": "Trial-15", "ledger": "E+canonical_en_spelling(10件)"},
            },
            "extraction_rules_person": [
                {"entity_jp": jp, "regex": pat, "official_given_name": og, "official_full": of}
                for jp, pat, og, of in PERSON_RULES
            ],
            "extraction_rules_org_or_facility": [
                {"entity_jp": jp, "regex": pat, "official_full": of}
                for jp, pat, of in ORG_RULES
            ],
            "extraction_note": (
                "人名5種は「姓の直前の与えられた名トークン(先頭大文字の連続英字列)」を"
                "正規表現でキャプチャし、Trial-15段階1で確定した公式のgiven nameと"
                "文字列完全一致で比較した(大文字小文字区別、部分一致は不一致扱い)。"
                "Moriは正規表現側でMorishitaの部分一致を除外する否定先読み(?!shita)を"
                "使用した。姓の直前トークンは同一行内([ \\t]+、改行をまたがない)"
                "のみに限定し(見出しと次段落が\\n\\nで連結され誤って結合される"
                "false positiveを回避)、かつ「After/In/On/While/From/With/But/"
                "The/To/At/By/Of/For/So/Then/When/As/A/An/Only/Instead/Behind/"
                "Turned/Moved/Left/Brought/Trusted/Was/Hit/Is/It/This/That/"
                "Once/Later」等の非人名ストップワード(文頭で偶然大文字化された"
                "前置詞・接続詞・動詞)は、姓単独言及(与えられた名なし)として"
                "given name occurrenceの集計から除外した"
                "(article_level_detailのexcluded_surname_only_mentionsに記録、"
                "全て条件A-E側のみで観測、条件Fでは0件)。団体名/施設名3種は"
                "完全文字列一致のみで公式表記/短縮形/"
                "その他を分類し、短縮形(Mazda Stadium・Hiroshima Carp)は誤記ではなく"
                "通称として別集計した(is_common_shortform)。"
                "佐藤輝明・坂本誠志郎・森下翔太・森翔平・E.モンテロの5種は"
                "条件A-Fすべてで検出された全occurrence(件数の詳細はentity_table_person"
                "参照)が公式表記と完全一致しており、揺れは1件も検出されなかった。"
                "表記ゆれが実際に検出されたのは伊原陵人(given name)と"
                "伏見寅威(given name)の2種のみだった。"
            ),
        },
        "entity_table_person": entity_table,
        "entity_table_org_or_facility": org_table,
        "variant_counts_by_entity_AE_pooled_vs_F": variant_counts_by_entity,
        "pooled_comparison_AE_vs_F": {
            "note": "条件A/B/C/D/E(いずれもLedgerにcanonical_en_spellingなし)を対照群として"
                    "統合し、人名5種の全occurrenceをプールした値。",
            "AE_pooled": {
                "n_occurrences": n_ae,
                "n_official_match": match_ae,
                "n_mismatch": mismatch_ae,
                "match_rate": (match_ae / n_ae) if n_ae else None,
                "match_rate_95ci_wilson": ci_ae,
            },
            "F": {
                "n_occurrences": n_f,
                "n_official_match": match_f,
                "n_mismatch": mismatch_f,
                "match_rate": (match_f / n_f) if n_f else None,
                "match_rate_95ci_wilson": ci_f,
            },
            "match_rate_difference_F_minus_AE": ((match_f / n_f) if n_f else None) - ((match_ae / n_ae) if n_ae else None) if (n_f and n_ae) else None,
            "fisher_exact_two_sided_p_value": p_value,
            "caveat": "N小(特にF=6記事)のため統計的検定は参考値。条件A-Eはそれぞれ"
                      "N=6記事(A2x3+B1Bx3)、5条件合計でも記事数は30(人名5種x30記事=最大150"
                      "occurrenceだが、Morishita/Moriは条件Eのみ・条件Fにしか出現しないfactのため"
                      "実際のoccurrence数は少ない。詳細はentity_table_person参照)。",
        },
        "variance_article_rate_by_condition": variance_article_rate_by_condition,
        "variance_article_rate_AE_pooled_vs_F": {
            "AE_pooled": {
                "n_articles": n_articles_ae,
                "n_articles_with_mismatch": n_articles_ae_mismatch,
                "rate": (n_articles_ae_mismatch / n_articles_ae) if n_articles_ae else None,
            },
            "F": {
                "n_articles": n_articles_f,
                "n_articles_with_mismatch": n_articles_f_mismatch,
                "rate": (n_articles_f_mismatch / n_articles_f) if n_articles_f else None,
            },
        },
        "article_level_detail": article_level_summary,
        "fc_pass_articles_with_missed_spelling_error": fc_pass_error_list,
        "per_condition_person_summary": per_condition_person,
        "raw_occurrence_records_person": person_records,
        "raw_occurrence_records_org_or_facility": org_records,
    }

    out_path = os.path.join(ROOT, "er011_output", "news_ledger_canonical_spelling_trial_15", "spelling_variance_analysis.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("WROTE", out_path)

    # ---- コンソールへ要約出力 ----
    print("\n=== per_condition_person_summary ===")
    for cond, v in per_condition_person.items():
        print(cond, v)
    print("\n=== pooled AE vs F ===")
    print("AE: n=%d match=%d mismatch=%d rate=%.4f CI=%s" % (n_ae, match_ae, mismatch_ae, (match_ae/n_ae if n_ae else 0), ci_ae))
    print("F : n=%d match=%d mismatch=%d rate=%.4f CI=%s" % (n_f, match_f, mismatch_f, (match_f/n_f if n_f else 0), ci_f))
    print("Fisher p-value:", p_value)
    print("\n=== variance_article_rate_by_condition ===")
    for cond, v in variance_article_rate_by_condition.items():
        print(cond, v)
    print("\n=== fc_pass_articles_with_missed_spelling_error ===")
    for r in fc_pass_error_list:
        print(r)
    print("\n=== variant_counts_by_entity (distinct variants) ===")
    for jp, v in variant_counts_by_entity.items():
        print(jp, "AE distinct:", v["AE_pooled_n_distinct"], v["AE_pooled_distinct_variants"], " | F distinct:", v["F_n_distinct"], v["F_distinct_variants"])
    print("\n=== org/facility summary (condition A vs F) ===")
    for jp, v in org_table.items():
        print(jp, "A:", v["by_condition"]["A"], "F:", v["by_condition"]["F"])


if __name__ == "__main__":
    main()
