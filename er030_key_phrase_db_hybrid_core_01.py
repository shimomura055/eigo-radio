# ============================================================
# er030_key_phrase_db_hybrid_core_01.py
# KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01
# ============================================================
# Core(candidate generation / shortlist assembly)をProduction module
# として昇格する。ユーザー正式決定(2026-09-27、KEY-PHRASE-DB-HYBRID-
# TRIAL-04 VALIDATED→APPROVED_FOR_PRODUCTION、baseline commit
# `57b61273`)により、DB Hybrid方式(Primary)をFamily Xの通常記事Key
# Phrase選定へ配線する。
#
# 本ファイルは`er029_key_phrase_db_hybrid_trial_04_stage1.py`
# (Fix A: 会話文sentence segmentation一般化、Fix B: rare/technical
# single word候補生成一般化)の内容を**ロジック無変更**でそのまま複製した
# ものである(関数名から実験用の"_v4"接尾辞のみ除去し、Production module
# としての命名に揃えた。中身の実装・アルゴリズム・定数・順序はすべて
# er029_key_phrase_db_hybrid_trial_04_stage1.pyと一字一句同一)。
# `er030_key_phrase_db_hybrid_core_01_equivalence_test.py`で、同一
# fixture入力に対しer029(Trial記録、無変更のまま残す)と本ファイルが
# 完全に同一の出力を返すことを固定回帰化している。
#
# 依存(すべて既存資産、無変更のまま読み取り専用でimportする):
#   - er023_key_phrase_db_extraction / er023_key_phrase_db_ingest
#     (DB抽出・Wiktionary API呼び出しの共有基盤、Trial-01から無変更)
#   - er027_key_phrase_db_hybrid_trial_02_stage1(irregular verb rescue・
#     複合名詞候補・Wiktionary multiword lookup・shortlist組み立て等)
#   - er028_key_phrase_db_hybrid_trial_03_stage1(context mismatch検出・
#     possessive noise除去・multiword品詞再判定・compact context付与)
# これらはer029自身が既に依存していた既存資産であり、本Production
# moduleでも同じ依存関係をそのまま引き継ぐ(器029/027/028自体は
# 無変更のままTrial記録として残す)。
#
# candidate生成後のhard requirement判定(validator)は、Production
# 既存の`er003_key_words_min_unit.validate_min_unit_selection`
# (`er003_key_words_production.validate_production_selection`経由)を
# そのまま再利用する(本ファイルでは再実装しない)。
# ============================================================

from __future__ import annotations

import json
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from functools import lru_cache
from typing import Optional

import wordfreq

import er023_key_phrase_db_extraction as ext
import er023_key_phrase_db_ingest as ing
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3

_normalize_key = ext._normalize_key
_WORD_TOKEN_RE = ext._WORD_TOKEN_RE
_CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS

# Trial-04と同一のbudget既定値(RARE_WORD_LOOKUP_BUDGET=15はer029_run.py、
# WIKTIONARY_MULTIWORD_LOOKUP_BUDGET=60はer028_run.pyの既定値をそのまま踏襲)。
DEFAULT_RARE_WORD_LOOKUP_BUDGET = 15
DEFAULT_WIKTIONARY_MULTIWORD_LOOKUP_BUDGET = 60


# ============================================================
# Fix A: 引用符を閉じた発話単位を認識できる一般化した文分割
# (er029_key_phrase_db_hybrid_trial_04_stage1.QUOTE_AWARE_SENTENCE_SPLIT_RE/
#  build_sentence_units_v4を無変更のまま複製)
# ============================================================

import re  # noqa: E402 (既存ファイル構成に合わせた配置)

QUOTE_AWARE_SENTENCE_SPLIT_RE = re.compile(r'[.!?]+[)\]"\']{0,2}(?=\s|$)')


def build_sentence_units(article_markdown: str) -> list:
    """er029_key_phrase_db_hybrid_trial_04_stage1.build_sentence_units_v4
    と同一実装(Fix A、終端句読点直後に閉じ引用符・閉じ括弧が0〜2文字
    続く境界も分割対象に含める)。"""
    lines = article_markdown.splitlines()
    blocks = []
    current = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if current:
                blocks.append(" ".join(current))
                current = []
            blocks.append(stripped.lstrip("#").strip())
        else:
            current.append(stripped)
    if current:
        blocks.append(" ".join(current))

    units = []
    for block in blocks:
        joined = unicodedata.normalize("NFKC", block)
        joined = joined.translate(str.maketrans({"‘": "'", "’": "'",
                                                  "“": '"', "”": '"'}))
        for raw_sentence in QUOTE_AWARE_SENTENCE_SPLIT_RE.split(joined):
            raw_sentence = raw_sentence.strip()
            if not raw_sentence:
                continue
            if raw_sentence[0] in "\"'":
                raw_sentence = raw_sentence[1:].strip()
            if raw_sentence and raw_sentence[-1] in "\"'":
                raw_sentence = raw_sentence[:-1].strip()
            if not raw_sentence:
                continue
            toks = _WORD_TOKEN_RE.findall(raw_sentence)
            if not toks:
                continue
            units.append({"tokens": toks, "raw_text": raw_sentence})
    return units


# ============================================================
# Fix B: rare / technical single word候補(1-gram)の一般化した候補生成
# (er029_key_phrase_db_hybrid_trial_04_stage1を無変更のまま複製)
# ============================================================

_RARE_TECHNICAL_SUFFIXES = (
    "ness", "tion", "sion", "ity", "ism", "ology", "ography", "ative", "ization",
)
_RARE_WORD_ZIPF_THRESHOLD = 3.3
_MIN_RARE_WORD_LETTER_LEN = 4

_UNIGRAM_CANDIDATE_TOKEN_RE = re.compile(r"^[a-z]+(?:-[a-z]+)*$")


def _has_rare_morphology(key: str) -> bool:
    if "-" in key:
        return True
    return any(key.endswith(suf) for suf in _RARE_TECHNICAL_SUFFIXES)


def _is_frequency_rare(key: str) -> bool:
    try:
        zf = wordfreq.zipf_frequency(key, "en")
    except Exception:
        return True
    if zf <= 0:
        return True
    return zf < _RARE_WORD_ZIPF_THRESHOLD


def _iter_unigram_occurrences(sentence_units: list) -> dict:
    info: dict = {}
    for u in sentence_units:
        for tok in u["tokens"]:
            key = _normalize_key(tok)
            if not key:
                continue
            entry = info.setdefault(key, {
                "surface_variants": Counter(), "occurrence_count": 0,
                "has_lowercase_occurrence": False,
            })
            entry["surface_variants"][tok] += 1
            entry["occurrence_count"] += 1
            if tok[:1].islower():
                entry["has_lowercase_occurrence"] = True
    return info


def _unigram_candidate_reason(key: str, entry: dict, dbs: dict) -> Optional[str]:
    if key in _CLOSED:
        return None
    if not _UNIGRAM_CANDIDATE_TOKEN_RE.match(key):
        return None
    if len(key.replace("-", "")) < _MIN_RARE_WORD_LETTER_LEN:
        return None
    if not entry["has_lowercase_occurrence"]:
        return None
    ngram = {"n": 1, "surface_tokens": [key], "surface_form": key}
    core = ext.match_candidate_against_group1(ngram, dbs)
    if core["db_match_count"] > 0:
        return None
    if _has_rare_morphology(key):
        return "morphology"
    try:
        zf = wordfreq.zipf_frequency(key, "en")
    except Exception:
        zf = 0.0
    if zf <= 0:
        return "frequency_unknown"
    if zf < _RARE_WORD_ZIPF_THRESHOLD:
        return "frequency_known_rare"
    return None


def select_rare_single_word_candidates(sentence_units: list, dbs: dict,
                                        article_title: str = "", budget: int = 15) -> list:
    info = _iter_unigram_occurrences(sentence_units)
    title_keys = {_normalize_key(t) for t in _WORD_TOKEN_RE.findall(article_title or "")}

    eligible = []
    for k, e in info.items():
        reason = _unigram_candidate_reason(k, e, dbs)
        if reason is not None:
            eligible.append((k, e, reason))

    def _priority(item):
        key, entry, _reason = item
        title_related = key in title_keys
        try:
            zf = wordfreq.zipf_frequency(key, "en")
        except Exception:
            zf = 0.0
        return (0 if title_related else 1, zf, -entry["occurrence_count"], key)

    eligible.sort(key=_priority)
    return eligible[:budget]


def wiktionary_unigram_lemma_lookup(candidates: list, batch_size: int = 50,
                                     sleep_sec: float = 1.5) -> dict:
    results = {}
    calls = 0
    t0 = time.time()
    unique_candidates = sorted(set(candidates))
    for i in range(0, len(unique_candidates), batch_size):
        batch = unique_candidates[i:i + batch_size]
        titles_param = "|".join(batch)
        params = {
            "action": "query", "titles": titles_param, "prop": "categories",
            "clcategories": "Category:English lemmas", "cllimit": "500",
            "format": "json",
        }
        url = ing.WIKTIONARY_API + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": ing.WIKTIONARY_USER_AGENT})
        data = None
        for retry_i in range(5):
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.load(resp)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and retry_i < 4:
                    wait = float(e.headers.get("Retry-After", 5)) if e.headers else 5
                    time.sleep(max(wait, 2 ** retry_i))
                    continue
                raise
        calls += 1
        pages = data.get("query", {}).get("pages", {})
        matched_titles = set()
        for _, page in pages.items():
            if "categories" in page and page.get("categories"):
                matched_titles.add(page.get("title"))
        for cand in batch:
            results[cand] = cand in matched_titles
        if i + batch_size < len(unique_candidates):
            time.sleep(sleep_sec)
    elapsed = time.time() - t0
    return {"results": results, "api_calls": calls, "elapsed_sec": round(elapsed, 2),
            "candidate_count": len(unique_candidates)}


def build_rare_single_word_evidences(selected: list, wiktionary_confirmed: dict) -> list:
    results = []
    dropped_unconfirmed = []
    for key, entry, reason in selected:
        confirmed = bool(wiktionary_confirmed.get(key))
        if reason == "frequency_unknown" and not confirmed:
            dropped_unconfirmed.append(key)
            continue
        surface = entry["surface_variants"].most_common(1)[0][0]
        results.append({
            "surface_form": surface,
            "canonical_form": key,
            "n": 1,
            "unit_type": ext.UNIT_TYPE_WORD,
            "matched_dbs": [],
            "db_match_count": 0,
            "db_categories": ["rare_technical_single_word_heuristic"],
            "cefr_level": None,
            "repetition_count_in_article": entry["occurrence_count"],
            "observed_surface_variants": sorted(entry["surface_variants"]),
            "source_span": surface,
            "important_noun_phrase_candidate": True,
            "rare_word_selection_reason": reason,
            "wiktionary_lemma_confirmed": confirmed,
        })
    results.sort(key=lambda r: r["canonical_form"])
    return {"evidences": results, "dropped_unconfirmed_frequency_unknown": dropped_unconfirmed}


# ============================================================
# Stage 1 メインエントリポイント
# (er029_key_phrase_db_hybrid_trial_04_stage1.run_stage1_for_article_v4
#  を無変更のまま複製)
# ============================================================

def run_stage1_for_article(article_text: str, dbs: dict) -> dict:
    sentence_units = build_sentence_units(article_text)
    sentences_tokens = [u["tokens"] for u in sentence_units]
    cefr_j = dbs["cefr_j"]

    all_evidences = []
    irregular_rescued = []

    for sent_tokens in sentences_tokens:
        ngrams_local = ext.generate_ngrams([sent_tokens])
        for ng in ngrams_local:
            core = s1v2.match_candidate_with_irregular_rescue(ng, dbs)
            if core["db_match_count"] == 0:
                continue
            if core.get("irregular_verb_rescue"):
                irregular_rescued.append(dict(core))
            mismatch_rule = s1v3.detect_context_mismatch_v3(
                ng["surface_tokens"], core["unit_type"], sent_tokens, ng["start"], cefr_j)
            core["context_mismatch_rule"] = mismatch_rule
            core["source_span"] = ng["surface_form"]
            core["final_selection_reason"] = None
            all_evidences.append(core)

    before_dedup_count = len(all_evidences)
    deduped = ext.dedupe_candidates_by_canonical_form(all_evidences)

    for cand in deduped:
        cand["exclusion_gate_result"] = ext.apply_exclusion_gate(cand, [], {})

    def _rule_excluded(cand):
        gate = cand["exclusion_gate_result"]
        return ((gate["too_easy_or_common"]["rule_determined"] and gate["too_easy_or_common"]["value"]) or
                (gate["unnatural_out_of_context"]["rule_determined"] and gate["unnatural_out_of_context"]["value"]))

    stage_a_survivors = [c for c in deduped if not _rule_excluded(c)]
    stage_a_excluded_by_existing_gate = [c for c in deduped if _rule_excluded(c)]

    context_mismatch_excluded = [c for c in stage_a_survivors if c.get("context_mismatch_rule")]
    stage_b_survivors = [c for c in stage_a_survivors if not c.get("context_mismatch_rule")]

    word_survivors_raw = [c for c in stage_b_survivors if c["unit_type"] == ext.UNIT_TYPE_WORD]
    word_survivors = s1v3.strip_possessive_noise_from_word_survivors(word_survivors_raw)
    phrase_survivors_raw = [c for c in stage_b_survivors if c["unit_type"] != ext.UNIT_TYPE_WORD]
    phrase_survivors = s1v2.merge_near_duplicates(phrase_survivors_raw)
    phrase_survivors.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))

    important_noun_candidates = s1v2.find_repeated_compound_noun_candidates(sentences_tokens, dbs)
    existing_canonicals = {c["canonical_form"] for c in phrase_survivors}
    important_noun_candidates = [c for c in important_noun_candidates
                                  if c["canonical_form"] not in existing_canonicals]

    def _word_rarity_key(c):
        try:
            zf = wordfreq.zipf_frequency(c["canonical_form"], "en")
        except Exception:
            zf = 0.0
        return (zf, c["canonical_form"])

    word_survivors_sorted = sorted(word_survivors, key=_word_rarity_key)

    return {
        "sentence_units": sentence_units,
        "tokens_total": sum(len(u["tokens"]) for u in sentence_units),
        "sentences_total": len(sentence_units),
        "before_dedup_count": before_dedup_count,
        "after_dedup_count": len(deduped),
        "stage_a_excluded_by_existing_gate_count": len(stage_a_excluded_by_existing_gate),
        "stage_a_survivors_count": len(stage_a_survivors),
        "irregular_verb_rescued_count": len(irregular_rescued),
        "context_mismatch_excluded": context_mismatch_excluded,
        "context_mismatch_excluded_count": len(context_mismatch_excluded),
        "stage_b_survivors_count": len(stage_b_survivors),
        "word_survivors": word_survivors_sorted,
        "phrase_survivors": phrase_survivors,
        "important_noun_candidates": important_noun_candidates,
    }


# attach_compact_contextはer028(v3)を無変更のまま再利用する。
attach_compact_context = s1v3.attach_compact_context


# ============================================================
# Stage 1 + Wiktionary multiword lookup + Fix B + shortlist組み立て
# (er029_key_phrase_db_hybrid_trial_04_run.run_stage1_and_shortlist_v4を
#  無変更のまま複製。Trial-04の実データ検証[12本文全件PASS]と同一の
#  orchestrationである)。
# ============================================================

def run_stage1_and_shortlist(
        article_text: str, dbs: dict, article_title: str,
        rare_word_lookup_budget: int = DEFAULT_RARE_WORD_LOOKUP_BUDGET,
        wiktionary_multiword_lookup_budget: int = DEFAULT_WIKTIONARY_MULTIWORD_LOOKUP_BUDGET) -> dict:
    stage1 = run_stage1_for_article(article_text, dbs)
    existing_canonicals = ({c["canonical_form"] for c in stage1["phrase_survivors"]} |
                            {c["canonical_form"] for c in stage1["important_noun_candidates"]} |
                            {c["canonical_form"] for c in stage1["word_survivors"]})
    sentences_tokens = [u["tokens"] for u in stage1["sentence_units"]]

    # --- 既存Wiktionary multiword lookup(2〜3-gram、bug A/B/C適用済み、無変更) ---
    lookup_candidates = s1v2.select_unmatched_ngram_candidates_for_lookup(
        sentences_tokens, existing_canonicals, budget=wiktionary_multiword_lookup_budget)
    mw_result = ing.wiktionary_multiword_targeted_lookup(lookup_candidates)
    hits = s1v2.build_multiword_hit_evidences(mw_result["results"])
    hits_survivors = s1v2.gate_and_merge_multiword_hits(hits)
    hits_survivors = [h for h in hits_survivors if h["canonical_form"] not in existing_canonicals]
    hits_survivors = s1v3.refine_multiword_hits_noun_phrase_flag(hits_survivors, dbs["cefr_j"])

    important_hits = [h for h in hits_survivors if h["important_noun_phrase_candidate"]]
    demoted_to_phrase = [h for h in hits_survivors if not h["important_noun_phrase_candidate"]]

    stage1["important_noun_candidates"] = stage1["important_noun_candidates"] + important_hits
    if demoted_to_phrase:
        stage1["phrase_survivors"] = stage1["phrase_survivors"] + demoted_to_phrase

    existing_canonicals = existing_canonicals | {h["canonical_form"] for h in important_hits} | \
        {h["canonical_form"] for h in demoted_to_phrase}

    # --- Fix B: rare single word候補(1-gram) ---
    rare_selected = select_rare_single_word_candidates(
        stage1["sentence_units"], dbs, article_title, budget=rare_word_lookup_budget)
    rare_selected = [(k, e, r) for k, e, r in rare_selected if k not in existing_canonicals]
    rare_lookup_candidates = [k for k, e, r in rare_selected]
    if rare_lookup_candidates:
        rare_mw_result = wiktionary_unigram_lemma_lookup(rare_lookup_candidates)
    else:
        rare_mw_result = {"results": {}, "api_calls": 0, "elapsed_sec": 0.0, "candidate_count": 0}
    rare_built = build_rare_single_word_evidences(rare_selected, rare_mw_result["results"])
    rare_evidences = rare_built["evidences"]

    stage1["important_noun_candidates"] = stage1["important_noun_candidates"] + rare_evidences

    stage1["wiktionary_multiword_lookup"] = {
        "candidates_checked": mw_result["candidate_count"],
        "api_calls": mw_result["api_calls"], "elapsed_sec": mw_result["elapsed_sec"],
        "hits": len(hits), "hits_surviving_gate_and_dedup": len(hits_survivors),
        "hits_important_after_pos_refine": len(important_hits),
        "hits_demoted_to_phrase_after_pos_refine": [h["canonical_form"] for h in demoted_to_phrase],
    }
    stage1["rare_single_word_lookup"] = {
        "candidates_checked": rare_mw_result["candidate_count"],
        "api_calls": rare_mw_result["api_calls"], "elapsed_sec": rare_mw_result["elapsed_sec"],
        "selected_with_reason": [(k, r) for k, e, r in rare_selected],
        "wiktionary_lemma_confirmed": rare_mw_result["results"],
        "final_included": [ev["canonical_form"] for ev in rare_evidences],
        "dropped_unconfirmed_frequency_unknown": rare_built["dropped_unconfirmed_frequency_unknown"],
    }

    shortlist_info = s1v2.build_shortlist(stage1)
    context_result = attach_compact_context(shortlist_info["shortlist"], stage1["sentence_units"])
    shortlist_info["shortlist"] = context_result["shortlist"]
    shortlist_info["sentence_reference"] = context_result["sentence_reference"]
    return {"stage1": stage1, "shortlist_info": shortlist_info}


@lru_cache(maxsize=1)
def load_group1_dbs() -> dict:
    """群1DB(CEFR-J/NGSL/Wiktionary idiom系)をprocess内で1回だけ読み込み、
    同一プロセス内の複数記事・複数レベル呼び出し(例: 同一themeのA2/B1B)で
    再利用する(API呼び出しではなくローカルファイル読み込みのみ、
    費用への影響なし)。"""
    return ing.load_all_group1_dbs()
