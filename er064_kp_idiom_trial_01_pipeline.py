# ============================================================
# er064_kp_idiom_trial_01_pipeline.py
# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / Phase B/C Trial pipeline (Trial専用)
# V0=Production現行(core.run_stage1_and_shortlistをそのまま呼ぶ)。V1/V2/V3は
# V0のstage1結果に「追加のみ」で候補を足し、cap15の外側に予約枠を設ける。
# Production code/Template/DBは編集しない。
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import pickle
import re

import wordfreq

import er023_key_phrase_db_extraction as ext
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3
import er030_key_phrase_db_hybrid_core_01 as core
import er064_kp_idiom_trial_01_matcher as matcher

OUT_ROOT = "er064_output/kp_idiom_trial_01"
RESERVED_SLOT_CAP = 3          # 予約枠上限(cap15の外側)。M1: 5->3
LLM_EXTRACTION_CAP = 3         # (b1)の抽出件数上限(M1: 5->3)
_CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS


def article_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_base(article_text: str, cache_dir: str = None, title: str = None) -> dict:
    """V0(Production現行)のstage1+shortlist結果。Wiktionary online lookup
    (無料の公開API。Productionと同じ)の結果を含むため、結果全体をpickleで
    キャッシュし、2回目以降は決定論的にキャッシュを返す(再現性・¥0)。"""
    cache_dir = cache_dir or f"{OUT_ROOT}/phase_b/stage1_cache"
    os.makedirs(cache_dir, exist_ok=True)
    p = os.path.join(cache_dir, article_sha(article_text)[:16] + ".pkl")
    if os.path.exists(p):
        with open(p, "rb") as f:
            return pickle.load(f)
    dbs = core.load_group1_dbs()
    if title is None:
        from er030_key_phrase_db_hybrid_selector_01 import extract_article_title
        title = extract_article_title(article_text)
    r = core.run_stage1_and_shortlist(article_text, dbs, title)
    with open(p, "wb") as f:
        pickle.dump(r, f)
    return r


def min_content_zipf(surface: str) -> float:
    zs = [wordfreq.zipf_frequency(t, "en") for t in surface.lower().split() if t not in _CLOSED]
    return min(zs) if zs else 9.9


_SOURCE_PRIORITY = {"llm_noncompositional": 0, "placeholder_title": 1, "rule_poss_pattern": 1,
                    "wiktionary_multiword_cut": 2}


def reserved_sort_key(c: dict) -> tuple:
    """予約枠内の決定論的順序: (由来優先度, 内容語の最小Zipf[希少度昇順], canonical alphabet)。
    現行(alphabet順のみ)の同点処理を『希少度→alphabet』へ置換する。"""
    return (_SOURCE_PRIORITY.get(c.get("evidence"), 9), min_content_zipf(c["surface_form"]), c["canonical_form"])


def _canon_set(base_stage1: dict) -> set:
    return ({c["canonical_form"] for c in base_stage1["phrase_survivors"]} |
            {c["canonical_form"] for c in base_stage1["important_noun_candidates"]} |
            {c["canonical_form"] for c in base_stage1["word_survivors"]})


def cut_online_hits(base_stage1: dict) -> list:
    """phrase_survivorsのcap15で切られたWiktionary online lookup由来
    (db_categories==['multiword_term'])の候補(診断/任意の予約枠用)。"""
    ps = base_stage1["phrase_survivors"]
    return [c for c in ps[15:] if c.get("db_categories") == ["multiword_term"]]


def build_variant_shortlist(base: dict, variant: str, *, placeholder_cands: list = None,
                            llm_cands: list = None, rule_cands: list = None,
                            include_cut_online_hits: bool = False) -> dict:
    """variant in {V0,V1,V2,V3}。V0=Production現行そのまま(base['shortlist_info'])。
    V1=a(placeholder)+c, V2=a+b1(llm)+c, V3=b2(rule_cands)+c。
    d(guidance)は選定Prompt側で別途適用。
    不変条件: V0のshortlist(surface_form列) ⊆ Vnのshortlist。予約枠(上限5)は
    llm/placeholder(任意でcut online hits)由来のみ、cap15の外側。"""
    stage1 = base["stage1"]
    v0 = base["shortlist_info"]
    if variant == "V0":
        return {"variant": "V0", "shortlist_info": v0, "reserved": [], "reserved_overflow": [],
                "stage1_for_context": stage1}
    pool = []
    existing = _canon_set(stage1)
    seen = set(existing)
    if variant == "V3":
        for c in (rule_cands or []):
            if c["canonical_form"] not in seen:
                pool.append(dict(c)); seen.add(c["canonical_form"])
    if variant in ("V1", "V2"):
        for c in (placeholder_cands or []):
            if c["canonical_form"] not in seen:
                pool.append(dict(c)); seen.add(c["canonical_form"])
    if variant == "V2":
        for c in (llm_cands or []):
            if c["canonical_form"] not in seen:
                pool.append(dict(c)); seen.add(c["canonical_form"])
    if include_cut_online_hits:
        for c in cut_online_hits(stage1):
            d = dict(c); d["evidence"] = "wiktionary_multiword_cut"
            pool.append(d)
    pool.sort(key=reserved_sort_key)
    reserved, overflow = pool[:RESERVED_SLOT_CAP], pool[RESERVED_SLOT_CAP:]
    shortlist = list(v0["shortlist"]) + reserved
    # context(sentence ID/occurrence)付与は全体を再計算せず予約枠分のみ
    ctx = s1v3.attach_compact_context(reserved, stage1["sentence_units"]) if reserved else \
        {"shortlist": [], "sentence_reference": {}}
    sent_ref = dict(v0["sentence_reference"])
    sent_ref.update(ctx["sentence_reference"])
    sl = list(v0["shortlist"]) + ctx["shortlist"]
    info = dict(v0)
    info.update({
        "shortlist": sl, "sentence_reference": sent_ref,
        "reserved_count": len(reserved),
        "phrase_included_count": v0["phrase_included_count"] + len(reserved),
        "shortlist_total_count": len(sl),
    })
    return {"variant": variant, "shortlist_info": info, "reserved": ctx["shortlist"],
            "reserved_overflow": overflow, "stage1_for_context": stage1}


def shortlist_keys(info: dict) -> list:
    return [c["canonical_form"] for c in info["shortlist"]]
