# ============================================================
# er030_key_phrase_db_hybrid_m2_supply_01.py
# FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02(2026-10-13)
# ============================================================
# Family X Key Phrase候補供給 M2(ユーザー正式決定: APPROVED_FOR_PRODUCTION、2026-10-13)のProduction実装。
# M2 = M1 + (a)placeholder照合 + (b2)ルール所有格3-gram + (c)予約枠(cap3、phrase枠の外側、追加LLM呼出なし)。
#   M1 = Wiktionary multiword照会予算 n2+100(n2=記事の2-gramプール数、1回照会)
#        + precision guard(demoted_allow: 現行60窓で拾えたonline hitのみphraseへ許可)
#        + U2(Tier-H: 完全包含された単語の削除+backfill、"tierH+S")
#        + U3(閉クラス語のみの句を除外[u3_exclude]、先頭が前置詞等の句にfragment_risk注釈[u3_annotate])
#        パラメータ(省略禁止): phrase_cap=20, realign=True, u2="tierH+S", r2=True, r3=True,
#        u3_exclude=True, u3_annotate=True, 照会順序=default(現行の語数昇順・内容語数降順・alphabet)。
#   M2は予約枠追加後にU2(Tier-H)を再計算し、元の候補(単語)も削る(「M1+3件」ではない)。
#   M2は`match:`注釈を付けない(M3ではない)。注釈は contains: / contained_in: / fragment_risk のみ。
# 選定Prompt(P0)は無変更(本moduleは候補供給のみ)。
#
# 構成(Opus 推奨「byte parityを2段」):
#   第1段 = 純関数は逐語copy(Trial module `er064_kp_opt_01_upstream_core` /
#           `er064_kp_idiom_trial_01_matcher` / `er064_kp_idiom_trial_01_pipeline` からの
#           `inspect.getsource`由来。Trial fileは無変更のまま残し、Productionからimportしない)。
#           逐語性はtest(`er030_key_phrase_db_hybrid_m2_supply_01_test_01.py`)でTrial定義との
#           ソース一致+sha256固定で検証する(Er028UtilByteParityTests方式)。
#   第2段 = 組立部分(下部、本moduleで新規記述)は出力一致(Trial snapshot再生で shortlist/rows/最終Prompt sha一致)。
# Trial専用の機構(Snapshot/monkeypatch `patched`/make_order_fn/V1-V3/(b1)LLM補助抽出/`match:`注釈M3)は移設しない。
# ============================================================
from __future__ import annotations

import json
import re
import time
from functools import lru_cache

import wordfreq

import er023_key_phrase_db_extraction as ext
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3
import er030_key_phrase_db_hybrid_core_01 as core

M2_SUPPLY_ID = "FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01/M2"

# ---- 定数(Trialと同値。testで固定) ----
THREEGRAM_CAP = 100          # er064_kp_opt_01_upstream_core.THREEGRAM_CAP
RESERVED_CAP = 3             # er064_kp_int_01_machine.RESERVED_CAP(= er064_kp_idiom_trial_01_pipeline.RESERVED_SLOT_CAP)
CURRENT_LOOKUP_WINDOW = 60   # 現行(M0)のWiktionary照会予算(core.DEFAULT_WIKTIONARY_MULTIWORD_LOOKUP_BUDGET)
M1_PARAMS = {"phrase_cap": 20, "realign": True, "u2": "tierH+S", "r2": True, "r3": True,
             "u3_exclude": True, "u3_annotate": True}
LABEL_CONTAINS = "contains:"
LABEL_CONTAINED = "contained_in:"
LABEL_FRAGMENT = "fragment_risk"

_TOK_RE = ext._WORD_TOKEN_RE
CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS
_CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS

FRAG_START = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "from", "by", "with", "into", "onto", "about", "as", "and", "or", "but",
              "so", "than", "that", "is", "are", "was", "were", "be", "been", "being", "do", "does", "did", "has", "have", "had", "can", "could",
              "may", "might", "must", "should", "will", "would"}
AUX_START = {"is", "are", "was", "were", "be", "been", "being", "do", "does", "did", "has", "have", "had", "can", "could", "may", "might",
             "must", "should", "will", "would"}
FRAG_START_NOAUX = FRAG_START - AUX_START

POSS = {"my", "your", "his", "her", "its", "their", "our"}
OBJ = {"me", "you", "him", "her", "it", "them", "us"}
REFL = {"myself", "yourself", "himself", "herself", "itself", "themselves", "ourselves", "oneself"}
PLACE = {"one's": "POSS", "someone's": "POSS", "somebody's": "POSS", "someone": "OBJ", "somebody": "OBJ",
         "oneself": "REFL", "something": "THING"}
_FINITE_AUX = {"is", "are", "was", "were", "has", "have", "had", "do", "does", "did", "be", "been", "being"}
_SOURCE_PRIORITY = {"llm_noncompositional": 0, "placeholder_title": 1, "rule_poss_pattern": 1,
                    "wiktionary_multiword_cut": 2}

# --- 逐語copy元: er064_kp_opt_01_upstream_core.py ---


def _stem(t):
    t = t.lower()
    t = re.sub(r"(?:'s|s')$", "", t)
    for s in ("ing", "ed", "es", "s"):
        if t.endswith(s) and len(t) - len(s) >= 3:
            return t[: -len(s)]
    return t


def stem_tokens(surface):
    return [_stem(t) for t in _TOK_RE.findall(surface)]


def occurrences(sentence_stems, seq):
    """sentence_stems: list[list[stem]]、seq: list[stem]。戻り: [(sent_idx, start)]"""
    n = len(seq)
    res = []
    if n == 0:
        return res
    for si, st in enumerate(sentence_stems):
        for i in range(0, len(st) - n + 1):
            if st[i:i + n] == seq:
                res.append((si, i))
    return res


def is_dictionary_registered(c):
    """辞書登録(Wiktionary見出し/online hit)の判定。ヒューリスティック(repeated_compound_noun等)・cefr_jのみは未登録扱い。"""
    return "wiktionary" in (c.get("matched_dbs") or [])


def compute_containment(cands, sentence_units, r2=False):
    """各候補(shortlist内)について、含む/含まれる関係と Tier-H(word整理対象)を機械算出。
    戻り: {"pairs":[{small,big,small_type,big_registered,all_small_occurrences_inside_big,tier}], }"""
    sent_stems = [[_stem(t) for t in u["tokens"]] for u in sentence_units]
    info = []
    for c in cands:
        seq = stem_tokens(c["surface_form"])
        info.append({"c": c, "seq": seq, "occ": occurrences(sent_stems, seq)})
    pairs = []
    for a in info:
        for b in info:
            if a is b or len(a["seq"]) >= len(b["seq"]) or not a["seq"]:
                continue
            # a ⊂ b (連続token列)
            inside = [(si, i) for (si, i) in b["occ"]]
            covered = set()
            for (si, i) in inside:
                for off in range(len(b["seq"])):
                    covered.add((si, i + off))
            contained_any = any(b["seq"][j:j + len(a["seq"])] == a["seq"] for j in range(len(b["seq"]) - len(a["seq"]) + 1))
            if not contained_any:
                continue
            # aの各出現がbの出現の内側に収まるか
            a_occs = a["occ"]
            # a_occs are positions in sentences of a; check coverage
            all_inside = bool(a_occs) and all(all((si, i + off) in covered for off in range(len(a["seq"]))) for (si, i) in a_occs)
            small_is_word = a["c"].get("unit_type") == "word"
            reg = is_dictionary_registered(b["c"])
            # 委任_02 R2: 長い側がimportant判定、またはdemotedでない(=名詞句判定で外れたonline hitではない)ときだけTier-H
            big_demoted = is_online_multiword_hit(b["c"]) and not b["c"].get("important_noun_phrase_candidate")
            tier = "H" if (small_is_word and reg and all_inside and not (r2 and big_demoted)) else "S"
            pairs.append({"small": a["c"]["canonical_form"], "big": b["c"]["canonical_form"], "small_unit_type": a["c"].get("unit_type"),
                          "big_registered": reg, "all_small_occurrences_inside_big": all_inside, "tier": tier})
    return pairs


def all_closed_only(surface):
    toks = [t.lower() for t in _TOK_RE.findall(surface)]
    return bool(toks) and all(t in CLOSED for t in toks)


def fragment_risk(surface, registered, no_aux=False):
    """U3(ii): 辞書未登録かつ先頭が閉じた語類(前置詞/冠詞/助動詞/接続詞)の複数語 -> 注釈のみ(置換しない)。
    no_aux=True(委任_02 R3): 助動詞始まりを対象から外す。"""
    toks = [t.lower() for t in _TOK_RE.findall(surface)]
    start = FRAG_START_NOAUX if no_aux else FRAG_START
    return bool(len(toks) >= 2 and toks[0] in start and not registered)


def _first_pos(cand, sentence_units):
    seq = stem_tokens(cand["surface_form"])
    for si, u in enumerate(sentence_units):
        st = [_stem(t) for t in u["tokens"]]
        n = len(seq)
        for i in range(0, len(st) - n + 1):
            if st[i:i + n] == seq:
                return (si, i)
    return (10 ** 6, 0)


def is_online_multiword_hit(c):
    return c.get("matched_dbs") == ["wiktionary"] and c.get("db_categories") == ["multiword_term"]


def assemble_shortlist(stage1_after_lookup, *, phrase_cap=15, realign=False, tiebreak_pos=False, u3_exclude=False, u3_annotate=False,
                       u2="none", dbs=None, demoted_allow=None, r1_guard=False, r2=False, r3=False):
    """run_stage1_and_shortlist(patched)が返したstage1(= demoted_to_phrase付与済み)を受けて、U2/U3/U4を適用した
    shortlist_infoを返す。u2: none / tierH+S / tierS。realign: demoted_to_phraseを含むphrase_survivorsを(-db_match_count, canonical)へ整列し直す。
    tiebreak_pos: 同値内を本文の出現順にする(U4(b))。Production関数のbuild_shortlistを再利用する。"""
    st = dict(stage1_after_lookup)
    phrases = list(st["phrase_survivors"])
    excluded_u3 = []
    r1_moved = []
    if r1_guard:
        # 委任_02 R1: 最後のtokenが閉じた語類のonline multiword hit(want to/close to/call it型)のimportant判定を外し、phrase(demoted)側へ回す。
        # take care/be wrongのように最後が内容語のものは残す。rare単語(important_noun_candidates内の1-gram)は対象外。
        keep_imp = []
        for c in st["important_noun_candidates"]:
            last = ([t.lower() for t in _TOK_RE.findall(c["surface_form"])] or [""])[-1]
            if is_online_multiword_hit(c) and last in CLOSED:
                c2 = dict(c)
                c2["important_noun_phrase_candidate"] = False
                phrases.append(c2)
                r1_moved.append(c["canonical_form"])
            else:
                keep_imp.append(c)
        st["important_noun_candidates"] = keep_imp
    if demoted_allow is not None:
        # 精度ガード(Trial比較用): 現行の照会窓(予算60)の外で新規に拾った「名詞句判定で外れたhit(demoted)」はphraseへ入れない。
        # important判定のhit(time lag等)は影響を受けない。
        phrases = [c for c in phrases if not (is_online_multiword_hit(c) and c["canonical_form"] not in demoted_allow)]
    if u3_exclude:
        keep = []
        for c in phrases:
            if all_closed_only(c["surface_form"]):
                excluded_u3.append(c["canonical_form"])
            else:
                keep.append(c)
        phrases = keep
    if realign or tiebreak_pos:
        if tiebreak_pos:
            phrases.sort(key=lambda c: (-c["db_match_count"], _first_pos(c, st["sentence_units"])))
        else:
            phrases.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))
    st["phrase_survivors"] = phrases
    info = s1v2.build_shortlist(st, phrase_cap=phrase_cap)
    sl = list(info["shortlist"])
    removed_tier_h = []
    pairs = []
    if u2 in ("tierH+S", "tierS"):
        pairs = compute_containment(sl, st["sentence_units"], r2=r2)
        if u2 == "tierH+S":
            drop = {p["small"] for p in pairs if p["tier"] == "H"}
            # backfill: wordを削った分だけ次の希少word_survivorsを補う(shortlist word枠の件数を維持)
            before_words = sum(1 for c in sl if c["unit_type"] == "word" and not c.get("important_noun_phrase_candidate"))
            sl = [c for c in sl if c["canonical_form"] not in drop]
            removed_tier_h = sorted(drop)
            in_sl = {c["canonical_form"] for c in sl}
            n_words_now = sum(1 for c in sl if c["unit_type"] == "word" and not c.get("important_noun_phrase_candidate"))
            need = before_words - n_words_now
            if need > 0:
                for c in st["word_survivors"]:
                    if need <= 0:
                        break
                    if c["canonical_form"] in in_sl or c["canonical_form"] in drop:
                        continue
                    sl.append(c)
                    in_sl.add(c["canonical_form"])
                    need -= 1
                pairs = compute_containment(sl, st["sentence_units"], r2=r2)
    ctx = core.attach_compact_context(sl, st["sentence_units"])
    sl = ctx["shortlist"]
    for c in sl:
        c = c  # 注釈(候補dictへ非破壊に付与)
    out = []
    for c in sl:
        c2 = dict(c)
        if u3_annotate:
            c2["fragment_risk"] = fragment_risk(c2["surface_form"], is_dictionary_registered(c2) or c2["canonical_form"] in (dbs or {}).get("wiktionary", {}), no_aux=r3)
        out.append(c2)
    return {"shortlist": out, "sentence_reference": ctx["sentence_reference"], "containment_pairs": pairs, "u2_removed_tier_h": removed_tier_h,
            "u3_excluded_closed_only": excluded_u3, "r1_moved_from_important": r1_moved,
            "counts": {"phrase": info["phrase_included_count"], "important": info["important_noun_included_count"],
                       "word": info["word_included_count"], "total": len(out)}}


# --- 逐語copy元: er064_kp_idiom_trial_01_matcher.py ---


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


# --- 逐語copy元: er064_kp_idiom_trial_01_pipeline.py ---


def min_content_zipf(surface: str) -> float:
    zs = [wordfreq.zipf_frequency(t, "en") for t in surface.lower().split() if t not in _CLOSED]
    return min(zs) if zs else 9.9


def reserved_sort_key(c: dict) -> tuple:
    """予約枠内の決定論的順序: (由来優先度, 内容語の最小Zipf[希少度昇順], canonical alphabet)。
    現行(alphabet順のみ)の同点処理を『希少度→alphabet』へ置換する。"""
    return (_SOURCE_PRIORITY.get(c.get("evidence"), 9), min_content_zipf(c["surface_form"]), c["canonical_form"])


def _canon_set(base_stage1: dict) -> set:
    return ({c["canonical_form"] for c in base_stage1["phrase_survivors"]} |
            {c["canonical_form"] for c in base_stage1["important_noun_candidates"]} |
            {c["canonical_form"] for c in base_stage1["word_survivors"]})


# ============================================================
# 第2段: 組立部分(本moduleで新規記述。Trial `er064_kp_int_01_machine.build_pattern(M2)` /
# `er064_kp_opt_01_phase2_run_03.build_method1` に対応。出力一致をtestで固定)
# ============================================================
class M2LookupFailure(Exception):
    """Wiktionary照会(拡大窓、core.run_stage1_and_shortlist)の失敗。selectorは既存reason_code
    `SELECTOR_EXCEPTION`へ写す(通信失敗はM2内部例外と区別して記録する、Opus必須4)。"""


class M2SupplyInternalError(Exception):
    """M2供給の内部例外(照会成功後の本module内処理)。selectorは`M2_SUPPLY_EXCEPTION`へ写す。"""


def mw_survivors(stage1: dict) -> set:
    """er064_kp_opt_01_phase2_run_03._mw_survivors と同一ロジック。"""
    out = set()
    for lst in ("important_noun_candidates", "phrase_survivors"):
        for c in stage1[lst]:
            if c.get("db_categories") == ["multiword_term"] and c.get("matched_dbs") == ["wiktionary"]:
                out.add(c["canonical_form"])
    return out


def _is_mw_survivor(c: dict) -> bool:
    return c.get("db_categories") == ["multiword_term"] and c.get("matched_dbs") == ["wiktionary"]


def compute_lookup_plan(st0: dict) -> dict:
    """Stage1(DB照合のみ、ネットワークなし)の結果から、現行窓(60)・拡大窓(n2+100)の照会候補を算出する純関数。"""
    existing = _canon_set(st0)
    sentences_tokens = [u["tokens"] for u in st0["sentence_units"]]
    pool = s1v2.select_unmatched_ngram_candidates_for_lookup(sentences_tokens, existing, budget=10 ** 7)
    n2 = sum(1 for p in pool if len(p.split()) == 2)
    return {"existing_pre": existing, "pool": pool, "n2": n2, "expanded_budget": n2 + THREEGRAM_CAP,
            "window_current": list(pool[:CURRENT_LOOKUP_WINDOW])}


def compute_demoted_allow(st0: dict, plan: dict, raw_results: dict, dbs: dict) -> set:
    """B'方式(Opus必須1): 拡大照会1回の生の結果`raw_results`を現行窓(先頭60)のkeyに絞り、純関数の
    後処理(build_hits -> gate_and_merge -> 既存語除外 -> refine)を再実行して「現行60窓で照会した場合の
    online multiword survivors」を求める。それにStage1由来(オフラインWiktionary DB一致)の
    matched_dbs==["wiktionary"]かつdb_categories==["multiword_term"]の候補を足す
    (Trial `_mw_survivors(cur["stage1"])` と同値であることをsnapshot回帰で固定)。照会は追加しない。"""
    window = plan["window_current"]
    sub = {k: raw_results[k] for k in window if k in raw_results}
    hits = s1v2.build_multiword_hit_evidences(sub)
    hs = s1v2.gate_and_merge_multiword_hits(hits)
    hs = [h for h in hs if h["canonical_form"] not in plan["existing_pre"]]
    hs = s1v3.refine_multiword_hits_noun_phrase_flag(hs, dbs["cefr_j"])
    allow = {h["canonical_form"] for h in hs if _is_mw_survivor(h)}
    allow |= {c["canonical_form"] for lst in ("important_noun_candidates", "phrase_survivors")
              for c in st0[lst] if _is_mw_survivor(c)}
    return allow


def _contiguous(c: dict, article_text: str) -> bool:
    """句読点をまたぐ3-gram(`news, your wallet`型)を除外: 本文に空白のみで連続して実在すること
    (Trial `er064_kp_int_01_machine.build_pattern` 内 `contiguous` と同一ロジック)。"""
    pat = r"\b" + r"\s+".join(re.escape(t) for t in c["surface_form"].split()) + r"\b"
    return re.search(pat, article_text, re.I) is not None


def build_m2_stage1_and_shortlist(article_text: str, dbs: dict, article_title: str) -> dict:
    """M2候補供給。戻り値は`core.run_stage1_and_shortlist`と同形(`stage1`/`shortlist_info`)+
    `containment_pairs`/`m2_meta`(retry時に再照会せず注釈を同一に保つため`shortlist_cache`へそのまま保存する)。
    Wiktionary照会は拡大窓1回のみ(2回照会しない)。"""
    t0 = time.time()
    st0 = core.run_stage1_for_article(article_text, dbs)      # オフライン(DB照合のみ)
    plan = compute_lookup_plan(st0)
    try:
        exp = core.run_stage1_and_shortlist(
            article_text, dbs, article_title, wiktionary_multiword_lookup_budget=plan["expanded_budget"])
    except Exception as e:
        raise M2LookupFailure(f"{type(e).__name__}: {e}") from e
    t_lookup = round(time.time() - t0, 2)
    try:
        return _assemble_m2(article_text, dbs, st0, plan, exp, t_lookup, t0)
    except Exception as e:
        raise M2SupplyInternalError(f"{type(e).__name__}: {e}") from e


def _assemble_m2(article_text, dbs, st0, plan, exp, t_lookup, t0) -> dict:
    allow = compute_demoted_allow(st0, plan, exp["results"], dbs)
    m1 = assemble_shortlist(exp["stage1"], dbs=dbs, demoted_allow=allow, **M1_PARAMS)
    units = st0["sentence_units"]
    existing = {c["canonical_form"] for c in m1["shortlist"]} | _canon_set(st0)
    pats = build_pattern_index(dbs)
    pc = placeholder_candidates(units, pats, dbs, set(existing))
    ex2 = set(existing) | {c["canonical_form"] for c in pc}
    rc = rule_possessive_pattern_candidates(units, dbs, ex2)
    dropped_nc = [c["canonical_form"] for c in pc + rc if not _contiguous(c, article_text)]
    pc = [c for c in pc if _contiguous(c, article_text)]
    rc = [c for c in rc if _contiguous(c, article_text)]
    pool = sorted(pc + rc, key=reserved_sort_key)
    reserved, overflow = pool[:RESERVED_CAP], pool[RESERVED_CAP:]
    ctx = s1v3.attach_compact_context(reserved, units) if reserved else {"shortlist": [], "sentence_reference": {}}
    sref = dict(m1["sentence_reference"])
    sref.update(ctx["sentence_reference"])
    sl = list(m1["shortlist"])
    for c in ctx["shortlist"]:
        c2 = dict(c)
        registered = bool(baseline_hit(c2["surface_form"], dbs)) or c2.get("evidence") == "placeholder_title"
        c2["fragment_risk"] = fragment_risk(c2["surface_form"], registered, no_aux=True)
        sl.append(c2)
    pairs = compute_containment(sl, units, r2=True) if ctx["shortlist"] else m1["containment_pairs"]
    drop = {p["small"] for p in pairs if p["tier"] == "H"}
    sl = [c for c in sl if c["canonical_form"] not in drop]
    pairs = [p for p in pairs if p["small"] not in drop]
    counts = m1["counts"]
    mw = exp["stage1"].get("wiktionary_multiword_lookup") or {}
    reserved_canon = [c["canonical_form"] for c in ctx["shortlist"]]
    shortlist_info = {
        "shortlist": sl, "sentence_reference": sref,
        "phrase_included_count": counts["phrase"] + len(reserved_canon),
        "important_noun_included_count": counts["important"],
        "word_included_count": counts["word"],
        "shortlist_total_count": len(sl),
    }
    m2_meta = {
        "supply_id": M2_SUPPLY_ID, "kp_supply": "m2",
        "n2": plan["n2"], "expanded_budget": plan["expanded_budget"], "current_window": CURRENT_LOOKUP_WINDOW,
        "demoted_allow_count": len(allow),
        "reserved": reserved_canon, "reserved_cap": RESERVED_CAP,
        "reserved_pool": {"placeholder": len(pc), "rule_poss": len(rc)},
        "overflow_beyond_cap": [c["canonical_form"] for c in overflow],
        "dropped_non_contiguous": dropped_nc,
        "tier_h_dropped_after_reserved": sorted(drop),
        "u2_removed_tier_h_m1": m1["u2_removed_tier_h"], "u3_excluded_closed_only": m1["u3_excluded_closed_only"],
        "fragment_risk_candidates": [c["canonical_form"] for c in sl if c.get("fragment_risk")],
        "wiktionary_multiword_lookup": {k: mw.get(k) for k in ("candidates_checked", "api_calls", "elapsed_sec")},
        "m2_lookup_seconds": t_lookup, "m2_total_seconds": round(time.time() - t0, 2),
        "n_candidates": len(sl),
    }
    return {"stage1": exp["stage1"], "shortlist_info": shortlist_info, "containment_pairs": pairs, "m2_meta": m2_meta}


def ev_text(c: dict, base_evidence_fn) -> str:
    """Trial `er064_kp_int_01_machine.ev_text` と同一(base_evidence_fnはselectorの`_compact_evidence_string`)。"""
    ev = c.get("evidence")
    if ev == "placeholder_title":
        return f"placeholder_title[{c.get('matched_title')}]"
    if ev == "rule_poss_pattern":
        return "rule_poss_pattern"
    return base_evidence_fn(c)


def make_annotating_evidence_fn(pairs: list, shortlist_with_ids: list, base_evidence_fn):
    """候補行末尾の注釈(contains:/contained_in:/fragment_risk)を付けるevidence_fn。candidate_idの対応表は
    span補正後の`shortlist_with_ids`から作る(Opus必須3: Trialは補正前・Productionは補正後に組み立てる差)。
    補正で除外された候補への参照は捨てる(idsに無いsmall/bigのペアは無視)。`match:`は付けない(M3ではない)。"""
    ids = {c["canonical_form"]: c["candidate_id"] for c in shortlist_with_ids}
    contains, contained = {}, {}
    for p in pairs:
        if p["small"] in ids and p["big"] in ids:
            contains.setdefault(p["big"], []).append(ids[p["small"]])
            contained.setdefault(p["small"], []).append(ids[p["big"]])

    def ev(c):
        s = ev_text(c, base_evidence_fn)
        if c["canonical_form"] in contains:
            s += " | " + LABEL_CONTAINS + " " + ",".join(contains[c["canonical_form"]])
        if c["canonical_form"] in contained:
            s += " | " + LABEL_CONTAINED + " " + ",".join(contained[c["canonical_form"]])
        if c.get("fragment_risk"):
            s += " | " + LABEL_FRAGMENT
        return s
    return ev
