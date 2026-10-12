# ============================================================
# er064_kp_idiom_trial_01_matcher.py
# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / Phase B (a)
# Trial専用(Production経路には配線しない)。DB(Wiktionary title)内の
# one's/someone's等のplaceholder見出しを、本文の所有格(my/your/his/...)と
# 動詞lemmaで照合する「追加のみ」の候補生成。既存ヒットは置換しない。
# 既存er023/er027/er030は読み取り専用でimportする(編集しない)。
# ============================================================
from __future__ import annotations

from functools import lru_cache

import er023_key_phrase_db_extraction as ext
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3

POSS = {"my", "your", "his", "her", "its", "their", "our"}
OBJ = {"me", "you", "him", "her", "it", "them", "us"}
REFL = {"myself", "yourself", "himself", "herself", "itself", "themselves", "ourselves", "oneself"}
# placeholder token -> slot kind。"something"はstrict版維持のため照合不能(THING)、
# 見出し自体を索引から除外する。
PLACE = {"one's": "POSS", "someone's": "POSS", "somebody's": "POSS", "someone": "OBJ", "somebody": "OBJ",
         "oneself": "REFL", "something": "THING"}
_CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS


def build_pattern_index(dbs: dict) -> list:
    """Wiktionary titleのうちplaceholderを含む見出しを索引化する。
    除外: 'something'を含む / "'s"所有を含む(placeholder以外の'sトークン) /
    カンマ入り / 2語未満 / 7語以上 / OBJ slotが見出し末尾 /
    placeholder以外の内容語(閉クラス語を除く)が2語未満。"""
    pats = []
    for key, ent in dbs["wiktionary"].items():
        toks = key.split()
        if len(toks) < 2 or len(toks) > 6 or "," in key:
            continue
        if not any(t in PLACE for t in toks):
            continue
        if "something" in toks or any(("'s" in t and t not in PLACE) for t in toks):
            continue
        if "one" in toks:  # bare 'one' は代名詞/数詞の曖昧さが大きいので除外
            continue
        if PLACE.get(toks[-1]) == "OBJ":  # 見出し末尾のOBJ slot(`know someone`型ノイズ)
            continue
        content = [t for t in toks if t not in PLACE and t not in _CLOSED]
        if len(content) < 2:
            continue
        pats.append({"title": key, "toks": toks, "cats": sorted(ent["categories"])})
    return pats


@lru_cache(maxsize=None)
def _lem(t: str) -> frozenset:
    return frozenset(ext.lemma_candidates_for_word(t)) | frozenset([s1v2.irregular_base_form(t) or ""])


def _tok_match(pt: str, t: str) -> bool:
    t = t.lower()
    k = PLACE.get(pt)
    if k == "POSS":
        return t in POSS
    if k == "OBJ":
        return t in OBJ
    if k == "REFL":
        return t in REFL
    if k == "THING":
        return False
    return t == pt or pt in _lem(t)


def match_sentence_tokens(tokens: list, pats: list) -> list:
    """1文のtoken列に対するplaceholder見出し照合。戻り値は
    {title, surface(token列をspace結合), start, n, cats}のlist。"""
    low = [t.lower() for t in tokens]
    lemset = set(low)
    for t in low:
        lemset |= _lem(t)
    hits = []
    for p in pats:
        L = len(p["toks"])
        lits = [x for x in p["toks"] if x not in PLACE]
        if not all(x in lemset for x in lits):
            continue
        for i in range(0, len(tokens) - L + 1):
            if all(_tok_match(pt, t) for pt, t in zip(p["toks"], tokens[i:i + L])):
                hits.append({"title": p["title"], "surface": " ".join(tokens[i:i + L]), "start": i, "n": L,
                             "cats": p["cats"]})
    return hits


def baseline_hit(surface: str, dbs: dict) -> bool:
    ng = {"n": len(surface.split()), "surface_tokens": surface.split(), "surface_form": surface}
    return s1v2.match_candidate_with_irregular_rescue(ng, dbs)["db_match_count"] > 0


def placeholder_candidates(sentence_units: list, pats: list, dbs: dict, existing_canonicals: set) -> list:
    """記事全体に対する追加候補(placeholder_title)を返す。既存DBヒット
    (baseline_hit)・既存shortlist候補と同一canonicalのものは除外(追加のみ)。
    候補dictは既存shortlist候補と同じキーを持つ(evidence=placeholder_title、
    matched_titleを付与)。"""
    out, seen = [], set()
    for u in sentence_units:
        for h in match_sentence_tokens(u["tokens"], pats):
            surf = h["surface"]
            key = ext._normalize_key(surf)
            if key in seen or key in existing_canonicals or baseline_hit(surf, dbs):
                continue
            cats = h["cats"]
            if "phrasal_verb" in cats:
                ut = ext.UNIT_TYPE_PHRASAL_VERB
            elif "idiom" in cats:
                ut = ext.UNIT_TYPE_IDIOM
            elif "proverb" in cats:
                ut = ext.UNIT_TYPE_DISCOURSE
            else:
                ut = ext.UNIT_TYPE_PHRASE
            surf_toks = surf.split()
            # 既存Productionと同じ文脈不一致検出(detect_context_mismatch_v3)と除外Gateを適用
            if s1v3.detect_context_mismatch_v3(surf_toks, ut, u["tokens"], h["start"], dbs["cefr_j"]):
                continue
            cand = {"surface_form": surf, "unit_type": ut}
            gate = ext.apply_exclusion_gate(cand, [], {})
            if ((gate["too_easy_or_common"]["rule_determined"] and gate["too_easy_or_common"]["value"]) or
                    (gate["unnatural_out_of_context"]["rule_determined"] and
                     gate["unnatural_out_of_context"]["value"])):
                continue
            seen.add(key)
            out.append({
                "surface_form": surf, "canonical_form": key, "n": h["n"], "matched_dbs": ["wiktionary"],
                "db_match_count": 1, "db_categories": cats, "unit_type": ut, "cefr_level": None,
                "source_span": surf, "context_mismatch_rule": None, "important_noun_phrase_candidate": False,
                "repetition_count_in_article": None, "observed_surface_variants": [surf],
                "evidence": "placeholder_title", "matched_title": h["title"],
            })
    return out


# ------------------------------------------------------------
# (b2) ルールベース代替案(V3用): [内容語][所有格][内容語]の3-gram(品詞タグなし)。
# 既存DBヒット(baseline_hit)と既存除外Gateは適用。ノイズが多い想定の比較用代替案。
# ------------------------------------------------------------
_FINITE_AUX = {"is", "are", "was", "were", "has", "have", "had", "do", "does", "did", "be", "been", "being"}


def rule_possessive_pattern_candidates(sentence_units: list, dbs: dict, existing_canonicals: set) -> list:
    out, seen = [], set()
    for u in sentence_units:
        toks = u["tokens"]
        for i in range(0, len(toks) - 2):
            a, b, c = toks[i].lower(), toks[i + 1].lower(), toks[i + 2].lower()
            if b not in POSS or a in _CLOSED or c in _CLOSED or a in _FINITE_AUX or c in _FINITE_AUX:
                continue
            surf = " ".join(toks[i:i + 3])
            key = ext._normalize_key(surf)
            if key in seen or key in existing_canonicals or baseline_hit(surf, dbs):
                continue
            seen.add(key)
            out.append({
                "surface_form": surf, "canonical_form": key, "n": 3, "matched_dbs": [], "db_match_count": 0,
                "db_categories": ["rule_poss_pattern"], "unit_type": ext.UNIT_TYPE_PHRASE, "cefr_level": None,
                "source_span": surf, "context_mismatch_rule": None, "important_noun_phrase_candidate": False,
                "repetition_count_in_article": None, "observed_surface_variants": [surf],
                "evidence": "rule_poss_pattern"})
    return out
