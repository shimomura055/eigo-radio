# ============================================================
# er023_key_phrase_db_trial_run.py
# KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
# 6本文(Meta/Hormuz/small_bag × a2/b1b)に対するオーケストレーション。
# A条件(群1DBのみ)→除外Gate観測→Wiktionary multiword targeted lookup→
# B条件(+ Oxford評価専用lookup)→不足時のみLLM fallback、という順で
# 実行し、各本文フォルダへJSON出力する。Production経路には一切書き込ま
# ない(新規ファイルのみ)。
# ============================================================

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter

import er023_key_phrase_db_ingest as ing
import er023_key_phrase_db_extraction as ext
import er023_oxford_evp_lookup as oel

OUTPUT_ROOT = os.path.join("er023_output", "key_phrase_db_trial_01")

ARTICLES = {
    "meta_a2": "er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md",
    "meta_b1b": "er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md",
    "hormuz_a2": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md",
    "hormuz_b1b": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md",
    "small_bag_a2": "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/a2/article.md",
    "small_bag_b1b": "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/b1b/article.md",
}

EXISTING_PRODUCTION_KEY_PHRASES = {
    "meta_a2": "er019_output/family_x_audio_production_wiring_01/family_x_b3_production_wiring_01__run_01/a2/key_phrases/keywords_canonicalized.json",
    "meta_b1b": "er019_output/family_x_audio_production_wiring_01/family_x_b3_production_wiring_01__run_01/b1b/key_phrases/keywords_canonicalized.json",
    "hormuz_a2": "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/a2/key_phrases/keywords_canonicalized.json",
    "hormuz_b1b": "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/b1b/key_phrases/keywords_canonicalized.json",
    "small_bag_a2": None,
    "small_bag_b1b": None,
}

WIKTIONARY_MULTIWORD_LOOKUP_BUDGET_TOTAL = 40  # 1本文あたりの照会上限目安(Oxford分と合算管理)

_CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS


def _content_word_count(surface_form: str) -> int:
    toks = [t.lower() for t in surface_form.split()]
    return sum(1 for t in toks if t not in _CLOSED)


def _is_all_closed_class(surface_form: str) -> bool:
    toks = [t.lower() for t in surface_form.split()]
    return all(t in _CLOSED for t in toks)


def _has_digit(surface_form: str) -> bool:
    return any(ch.isdigit() for ch in surface_form)


def process_article(article_key: str, article_path: str, dbs: dict,
                    oxford_session: oel.OxfordEvpLookupSession, run_fallback: bool = False) -> dict:
    t_start = time.time()
    article_text = open(article_path, encoding="utf-8").read()
    sentences = ext.tokenize_sentences(article_text)
    tokens = [t for sent in sentences for t in sent]
    # n-gramは文境界をまたがない(文をまたぐと"recovering The policy turn"
    # のような無意味な候補が生成されてしまうため、sentence-aware生成に
    # 切り替えた実装修正)
    ngrams = ext.generate_ngrams(sentences)

    evidences_all = [ext.build_evidence(ng, dbs) for ng in ngrams]
    matched_group1 = [e for e in evidences_all if e["db_match_count"] > 0]
    deduped_group1 = ext.dedupe_candidates_by_canonical_form(matched_group1)

    # 除外Gate(規則判定/人間判断を分けて記録、Fableレビュー論点1)
    for cand in deduped_group1:
        cand["exclusion_gate_result"] = ext.apply_exclusion_gate(cand, tokens, {})

    def _rule_excluded(cand):
        gate = cand["exclusion_gate_result"]
        return ((gate["too_easy_or_common"]["rule_determined"] and gate["too_easy_or_common"]["value"]) or
                (gate["unnatural_out_of_context"]["rule_determined"] and gate["unnatural_out_of_context"]["value"]))

    gate_a_survivors = [c for c in deduped_group1 if not _rule_excluded(c)]
    gate_a_excluded_by_rule = [c for c in deduped_group1 if _rule_excluded(c)]

    word_group = [c for c in gate_a_survivors if c["unit_type"] == "word"]
    phrase_group = [c for c in gate_a_survivors if c["unit_type"] != "word"]
    # 各群内でのみ複数DB一致→単一DB一致の順にソートする(Fableレビュー
    # 論点2: DB一致数で単語がphraseを押しのけないよう、順位はword/phrase
    # 各群内に留める)
    word_group.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))
    phrase_group.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))

    # --- Wiktionary multiword terms targeted lookup(group1未一致の
    # phrase候補のうち上位のみ、dump全体は取得しない) ---
    unmatched_phrase_ngrams = [
        ng for ng in ngrams
        if ng["n"] >= 2
        and not _is_all_closed_class(ng["surface_form"])
        and not _has_digit(ng["surface_form"])
        and ext._normalize_key(ng["surface_form"]) not in {c["canonical_form"] for c in deduped_group1}
    ]
    # 決定的ソート: content word数(多い順)→n(長い順)→アルファベット順
    unmatched_phrase_ngrams_dedup = {}
    for ng in unmatched_phrase_ngrams:
        key = ext._normalize_key(ng["surface_form"])
        if key not in unmatched_phrase_ngrams_dedup:
            unmatched_phrase_ngrams_dedup[key] = ng
    # 決定的ソート: n=2,3(実在の辞書phraseとして最も妥当なスパン長)を
    # 優先し、その中でcontent word数が多い順→アルファベット順。n=4,5は
    # 文境界内であっても辞書phraseである可能性が低いため後回しにする
    # (これは除外Gateのhard ruleではなく、Oxford/EVP lookup予算[40件
    # 目安]の中で優先的に照会する候補を選ぶための、観測用の並べ替え
    # 補助にすぎない)。
    unmatched_sorted = sorted(
        unmatched_phrase_ngrams_dedup.values(),
        key=lambda ng: (0 if ng["n"] in (2, 3) else 1, -_content_word_count(ng["surface_form"]),
                        ng["n"], ng["surface_form"].lower()),
    )

    multiword_lookup_candidates = [ng["surface_form"] for ng in unmatched_sorted[:60]]
    mw_lookup_result = ing.wiktionary_multiword_targeted_lookup(multiword_lookup_candidates)

    # multiword一致した候補をevidenceとして追加(unit_type=phrase、
    # matched_dbs=["wiktionary"], db_categories=["multiword_term"])
    multiword_hits = []
    for cand_surface, hit in mw_lookup_result["results"].items():
        if hit:
            key = ext._normalize_key(cand_surface)
            multiword_hits.append({
                "surface_form": cand_surface, "canonical_form": key, "n": len(cand_surface.split()),
                "matched_dbs": ["wiktionary"], "db_match_count": 1, "db_categories": ["multiword_term"],
                "unit_type": "phrase", "cefr_level": None, "source_span": cand_surface,
            })
    for cand in multiword_hits:
        cand["exclusion_gate_result"] = ext.apply_exclusion_gate(cand, tokens, {})
    multiword_hits_survivors = [c for c in multiword_hits if not _rule_excluded(c)]
    phrase_group_with_mw = phrase_group + multiword_hits_survivors
    phrase_group_with_mw.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))

    # --- Oxford評価専用lookup(B条件、群2、Production判定には使わない) ---
    # 実装上の解釈(REPORTで明記): 「A段階で残った候補」をgate_a_survivors
    # 全件(単語だけで100件超)とすると1本文あたり40件の目安を大幅に
    # 超えるため、本Trialでは(a)phrase系候補(group1+multiword、通常
    # 数件〜十数件、実質的にKey Phrase最終候補になり得る主要な母集団)を
    # 全件、(b)Aで拾えなかったphrase候補の上位(観測用ソート補助、
    # wordfreq等の閾値ではない)を最大10件、(c)残り予算をword群から
    # wordfreq zipf頻度が低い(=珍しい・内容語らしい)順に埋める、という
    # 3段構成でOxford lookup対象を40件目安に収める。wordfreqの使用は
    # Gate除外ルールの閾値ではなく、40件という運用上のlookup予算内で
    # どれを優先照会するかを決めるための、観測目的の並べ替え補助である。
    import wordfreq

    def _word_rarity_key(canonical_form):
        try:
            zf = wordfreq.zipf_frequency(canonical_form, "en")
        except Exception:
            zf = 0.0
        return (zf, canonical_form)

    reserve_for_unmatched_phrase = 10
    oxford_candidates_ordered = []
    oxford_candidates_seen = set()

    def _add(cands):
        for c in cands:
            if c not in oxford_candidates_seen:
                oxford_candidates_seen.add(c)
                oxford_candidates_ordered.append(c)

    _add(c["canonical_form"] for c in phrase_group_with_mw)
    remaining = max(0, WIKTIONARY_MULTIWORD_LOOKUP_BUDGET_TOTAL - len(oxford_candidates_ordered))
    unmatched_budget = min(reserve_for_unmatched_phrase, remaining)
    _add(ext._normalize_key(ng["surface_form"]) for ng in unmatched_sorted[:unmatched_budget])
    remaining = max(0, WIKTIONARY_MULTIWORD_LOOKUP_BUDGET_TOTAL - len(oxford_candidates_ordered))
    word_sorted_by_rarity = sorted((c["canonical_form"] for c in word_group), key=_word_rarity_key)
    _add(word_sorted_by_rarity[:remaining])

    oxford_budget_exceeded = len(oxford_candidates_ordered) > WIKTIONARY_MULTIWORD_LOOKUP_BUDGET_TOTAL
    oxford_candidates_final = oxford_candidates_ordered[:WIKTIONARY_MULTIWORD_LOOKUP_BUDGET_TOTAL] \
        if not oxford_budget_exceeded else oxford_candidates_ordered
    # phrase_group_with_mw単独で40件を超える場合のみ、理由付きで上限超過を許容する
    phrase_only_exceeds_budget = len(phrase_group_with_mw) > WIKTIONARY_MULTIWORD_LOOKUP_BUDGET_TOTAL

    oxford_lookups = [oxford_session.lookup(c) for c in oxford_candidates_final]

    # 既存Production Key Phraseとの重複率
    existing_path = EXISTING_PRODUCTION_KEY_PHRASES.get(article_key)
    existing_key_phrases = []
    if existing_path and os.path.exists(existing_path):
        with open(existing_path, encoding="utf-8") as f:
            existing_data = json.load(f)
        existing_key_phrases = _extract_existing_key_phrases(existing_data)

    elapsed = time.time() - t_start

    summary = {
        "article_key": article_key,
        "article_path": article_path,
        "total_tokens": len(tokens),
        "total_ngrams": len(ngrams),
        "group1_db_matched_raw": len(matched_group1),
        "group1_db_matched_deduped": len(deduped_group1),
        "gate_a_survivors": len(gate_a_survivors),
        "gate_a_excluded_by_rule": len(gate_a_excluded_by_rule),
        "gate_rule_determined_vs_human_needed": _gate_rule_vs_human_stats(deduped_group1),
        "word_group_count": len(word_group),
        "phrase_group_count_group1_only": len(phrase_group),
        "phrase_group_count_with_multiword": len(phrase_group_with_mw),
        "unit_type_counts_group1_only": dict(Counter(c["unit_type"] for c in gate_a_survivors)),
        "multi_db_match_word_count": sum(1 for c in word_group if c["db_match_count"] >= 2),
        "multi_db_match_phrase_count": sum(1 for c in phrase_group_with_mw if c["db_match_count"] >= 2),
        "single_db_match_word_count": sum(1 for c in word_group if c["db_match_count"] == 1),
        "single_db_match_phrase_count": sum(1 for c in phrase_group_with_mw if c["db_match_count"] == 1),
        "wiktionary_multiword_targeted_lookup": {
            "candidates_checked": mw_lookup_result["candidate_count"],
            "api_calls": mw_lookup_result["api_calls"],
            "elapsed_sec": mw_lookup_result["elapsed_sec"],
            "hits": len(multiword_hits),
            "hits_surviving_gate": len(multiword_hits_survivors),
        },
        "oxford_evp_lookup": {
            "candidates_looked_up": len(oxford_lookups),
            "budget_exceeded_40": oxford_budget_exceeded,
            "phrase_candidates_alone_exceed_budget": phrase_only_exceeds_budget,
            "shortlisting_method": "phrase_group_with_mw(all)+top10_unmatched_phrase(sort aid)"
                                    "+word_group_by_wordfreq_rarity(fills remaining budget)",
            "oxford_matches": sum(1 for r in oxford_lookups if r["matched"]),
            "evp_available": False,
        },
        "existing_production_key_phrase_count": len(existing_key_phrases),
        "extraction_elapsed_sec": round(elapsed, 3),
    }

    out_dir = os.path.join(OUTPUT_ROOT, article_key)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "candidates_word_group.json"), "w", encoding="utf-8") as f:
        json.dump(word_group, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "candidates_phrase_group_A.json"), "w", encoding="utf-8") as f:
        json.dump(phrase_group, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "candidates_phrase_group_B.json"), "w", encoding="utf-8") as f:
        json.dump(phrase_group_with_mw, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "gate_a_excluded_by_rule.json"), "w", encoding="utf-8") as f:
        json.dump(gate_a_excluded_by_rule, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "oxford_evp_lookups.jsonl"), "w", encoding="utf-8") as f:
        for r in oxford_lookups:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(out_dir, "wiktionary_multiword_lookup.jsonl"), "w", encoding="utf-8") as f:
        for cand, hit in mw_lookup_result["results"].items():
            f.write(json.dumps({"candidate": cand, "matched_multiword_term_category": hit,
                                "looked_up_at": "2026-09-27", "source": "wiktionary_api_targeted"},
                               ensure_ascii=False) + "\n")
    with open(os.path.join(out_dir, "existing_production_key_phrases.json"), "w", encoding="utf-8") as f:
        json.dump(existing_key_phrases, f, ensure_ascii=False, indent=2)

    fallback_result = None
    total_gate_a = len(word_group) + len(phrase_group)
    total_gate_b = len(word_group) + len(phrase_group_with_mw)
    if run_fallback and total_gate_b < 4:
        gap = 5 - total_gate_b
        existing_surface = [c["surface_form"] for c in word_group + phrase_group_with_mw]
        fallback_result = _run_fallback(article_text, existing_surface, gap)
        with open(os.path.join(out_dir, "fallback_result.json"), "w", encoding="utf-8") as f:
            json.dump(fallback_result, f, ensure_ascii=False, indent=2)

    summary["fallback_triggered"] = fallback_result is not None
    summary["fallback_status"] = fallback_result["status"] if fallback_result else None
    summary["final_candidate_count_A_before_fallback"] = total_gate_a
    summary["final_candidate_count_B_before_fallback"] = total_gate_b

    with open(os.path.join(out_dir, "extraction_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return summary


def _gate_rule_vs_human_stats(deduped_candidates: list) -> dict:
    gate_items = ["too_easy_or_common", "proper_noun", "article_specific_low_reuse",
                 "semantic_functional_duplicate_of", "unnatural_out_of_context", "low_value_as_chunk"]
    stats = {}
    for item_name in gate_items:
        rule_determined = sum(1 for c in deduped_candidates if c["exclusion_gate_result"][item_name]["rule_determined"])
        human_needed = len(deduped_candidates) - rule_determined
        stats[item_name] = {"rule_determined": rule_determined, "human_judgment_needed": human_needed}
    return stats


def _extract_existing_key_phrases(existing_data) -> list:
    if isinstance(existing_data, dict) and "items" in existing_data:
        items = existing_data["items"]
    elif isinstance(existing_data, list):
        items = existing_data
    else:
        items = []
    result = []
    for item in items:
        if isinstance(item, dict):
            kp = item.get("key_phrase") or item.get("used_form") or item.get("display_phrase")
            if kp:
                result.append(ext._normalize_key(kp))
    return result


def _run_fallback(article_text: str, existing_candidates: list, gap: int) -> dict:
    import er023_key_phrase_llm_fallback as fb
    return fb.run_fallback_gate(article_text, existing_candidates, gap)


def main(run_fallback: bool = False):
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    print("Loading group1 DBs...")
    dbs = ing.load_all_group1_dbs()
    oxford_session = oel.OxfordEvpLookupSession()
    results = {}
    for article_key, path in ARTICLES.items():
        print(f"Processing {article_key}...")
        results[article_key] = process_article(article_key, path, dbs, oxford_session, run_fallback=run_fallback)
        time.sleep(2.0)
    with open(os.path.join(OUTPUT_ROOT, "all_articles_summary.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT_ROOT, "oxford_fetch_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(oxford_session.fetch_metadata(), f, ensure_ascii=False, indent=2)
    print("Done.")
    return results


if __name__ == "__main__":
    import sys
    run_fb = "--fallback" in sys.argv
    main(run_fallback=run_fb)
