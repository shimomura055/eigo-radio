# ============================================================
# er064_kp_int_03_b1.py  (FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 Round3 / (b1)LLM補助抽出、Trial専用・Production非接続)
# M1: Phase D抽出器 er064_kp_idiom_trial_01_extractor (v3 prompt, 2-5語, verify_span, narrow_to_core_span) をそのまま再利用する。
# 本モジュールは (1)呼出ラッパ(費用記録) (2)決定論後処理(逐語率・rank上位3・重複包含除外) (3)(b2)と同形式のappend (4)Tier H削除の記録 だけを担う。
# 評価アンカーのファイルはここから参照しない(Prompt/抽出/選別に使わない)。
# ============================================================
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3  # noqa: E402
import er030_key_phrase_db_hybrid_source_reference_contract_01 as contract  # noqa: E402
import er030_key_phrase_db_hybrid_selector_01 as sel  # noqa: E402
import er064_kp_idiom_trial_01_extractor as EX  # noqa: E402
import er064_kp_idiom_trial_01_matcher as M  # noqa: E402
import er064_kp_idiom_trial_01_pipeline as P  # noqa: E402
import er064_kp_int_01_machine as MC  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402
import er064_kp_opt_01_upstream_core as U  # noqa: E402

OUT = "er064_output/kp_integrated_opt_01/round3"
B1DIR = OUT + "/b1"
ROUND3_CAP = 3          # M4: rank上位3(逐語検証・重複・包含除外後)
PD_INPUTS = "er064_output/kp_idiom_trial_01/phase_d/inputs"
NEG_CONTROLS = {"N1": (f"{PD_INPUTS}/n1_std.md", "std"), "D6": (f"{PD_INPUTS}/d6_adv.md", "adv"),
                "D5": (f"{PD_INPUTS}/d5_std.md", "std"), "R3": (f"{PD_INPUTS}/r3_adv.md", "adv")}
DISPLAY_EVIDENCE_B1 = "rule_poss_pattern"   # R2: 行形式は(b2)と同一。`source: llm_aux`は表示しない(metadataのみ)
SHORT_EVID = "llm_noncompositional"


def level_of(key):
    return key.rsplit("_", 1)[1]


def article_text(aid):
    if aid in NEG_CONTROLS:
        return open(NEG_CONTROLS[aid][0], encoding="utf-8").read()
    return U.read_article(aid)


def level_of_id(aid):
    return NEG_CONTROLS[aid][1] if aid in NEG_CONTROLS else level_of(aid)


def is_verbatim(span, units):
    """LLM生spanが本文の1文内でtoken列として連続一致するか(大小文字無視、句読点をまたがない)。"""
    toks = [t.lower() for t in EX.ext._WORD_TOKEN_RE.findall(EX._norm_text(span))]
    if not toks:
        return False
    for u in units:
        ut = [t.lower() for t in u["tokens"]]
        for i in range(0, len(ut) - len(toks) + 1):
            if ut[i:i + len(toks)] == toks:
                return True
    return False


def guard_narrowing(parsed):
    """既知の失敗1(`in the ring`短縮)対策: core_spanによる縮約後の先頭が閉クラス語(前置詞・冠詞等)になる場合は縮約を行わず、LLMのspanをそのまま使う。"""
    out = {"items": []}
    hits = []
    for it in parsed.get("items") or []:
        it2 = dict(it)
        nar = EX.narrow_to_core_span(it.get("span", ""), it.get("core_span", ""))
        if nar["narrowed"]:
            first = EX.ext._WORD_TOKEN_RE.findall(EX._norm_text(nar["span"]))[0].lower()
            if first in EX.core._CLOSED:
                hits.append({"span": it.get("span"), "core_span": it.get("core_span"), "would_narrow_to": nar["span"]})
                it2["core_span"] = it.get("span", "")
        out["items"].append(it2)
    return out, hits


def first_pos(surface, art):
    m = re.search(r"\b" + r"\s+".join(re.escape(t) for t in surface.split()) + r"\b", art, re.I)
    return m.start() if m else 10 ** 9


def build_b1(parsed, units, existing_canon, art):
    """LLM生出力 -> 検証済み候補。戻り: dict(accepted<=3, 内訳)。決定論のみ(追加API呼出なし)。"""
    gp, narrow_guard = guard_narrowing(parsed)
    raw_items = parsed.get("items") or []
    verb = [{"span": it.get("span"), "verbatim": is_verbatim(it.get("span", ""), units)} for it in raw_items]
    built = EX.build_llm_candidates(gp, units, set(existing_canon), cap=8)
    acc = sorted(built["accepted"], key=lambda c: (c.get("llm_rank") if isinstance(c.get("llm_rank"), int) else 10 ** 6, first_pos(c["surface_form"], art)))
    kept, over = acc[:ROUND3_CAP], acc[ROUND3_CAP:]
    for c in kept:
        c["evidence"] = SHORT_EVID
    return {"raw_item_count": len(raw_items), "verbatim": verb, "narrow_guard_hits": narrow_guard, "accepted": kept,
            "over_cap": [c["canonical_form"] for c in over], "rejected": built["rejected"], "duplicate_of_existing": built["duplicate_of_existing"],
            "raw_items": raw_items}


def ev_text3(c):
    if c.get("evidence") == SHORT_EVID:
        return DISPLAY_EVIDENCE_B1
    return MC.ev_text(c)


def rows_for3(sl, sref, pairs, title):
    wc = contract.assign_candidate_ids(sl)
    ids = {c["canonical_form"]: c["candidate_id"] for c in wc["shortlist_with_ids"]}
    contains, contained = {}, {}
    for p in pairs:
        if p["small"] in ids and p["big"] in ids:
            contains.setdefault(p["big"], []).append(ids[p["small"]])
            contained.setdefault(p["small"], []).append(ids[p["big"]])

    def ev(c):
        s = ev_text3(c)
        if c["canonical_form"] in contains:
            s += " | " + U.LABEL_CONTAINS + " " + ",".join(contains[c["canonical_form"]])
        if c["canonical_form"] in contained:
            s += " | " + U.LABEL_CONTAINED + " " + ",".join(contained[c["canonical_form"]])
        if c.get("fragment_risk"):
            s += " | " + U.LABEL_FRAGMENT
        return s
    return contract.build_lightweight_user_message(title, wc["shortlist_with_ids"], sref, "", "family_x", None, ev)


def existing_for(key):
    base = MC.build_pattern(key, "M2")
    st0 = R._base(key)[0]
    return base, st0, ({c["canonical_form"] for c in base["shortlist"]} | P._canon_set(st0))


def build_pattern_m2b(key, accepted):
    """M2 shortlist + b1候補を(c)予約枠の直後に同形式でappend(machine.py L140-145と同手順)。Tier H削除を記録。"""
    R._init()
    base, st0, _ = existing_for(key)
    units = st0["sentence_units"]
    if not accepted:
        out = dict(base)
        out.update(tier_h_deleted_existing=[], tier_h_deleted_b1=[], tier_h_recompute_base=[], b1_added=[], noop_vs_M2=True)
        out["rows_text"] = rows_for3(base["shortlist"], base["sentence_reference"], base["pairs"], base["title"])
        return out
    ctx = s1v3.attach_compact_context([dict(c) for c in accepted], units)
    sref = dict(base["sentence_reference"])
    sref.update(ctx["sentence_reference"])
    sl = list(base["shortlist"])
    for c in ctx["shortlist"]:
        c2 = dict(c)
        registered = bool(M.baseline_hit(c2["surface_form"], R._dbs)) or c2.get("evidence") == "placeholder_title"
        c2["fragment_risk"] = U.fragment_risk(c2["surface_form"], registered, no_aux=True)
        sl.append(c2)
    pairs = U.compute_containment(sl, units, r2=True)
    drop = {p["small"] for p in pairs if p["tier"] == "H"}
    base_pairs = U.compute_containment(list(base["shortlist"]), units, r2=True)
    base_drop = {p["small"] for p in base_pairs if p["tier"] == "H"}
    b1_canon = {c["canonical_form"] for c in ctx["shortlist"]}
    sl2 = [c for c in sl if c["canonical_form"] not in drop]
    pairs2 = [p for p in pairs if p["small"] not in drop]
    out = {"shortlist": sl2, "sentence_reference": sref, "pairs": pairs2, "title": base["title"], "reserved": base["reserved"],
           "tier_h_dropped": base["tier_h_dropped"], "pool_sizes": base["pool_sizes"], "noop_vs_M2": False,
           "b1_added": [c["canonical_form"] for c in ctx["shortlist"] if c["canonical_form"] not in drop],
           "tier_h_deleted_existing": sorted(d for d in drop if d not in b1_canon),
           "tier_h_deleted_b1": sorted(d for d in drop if d in b1_canon),
           "tier_h_recompute_base": sorted(base_drop)}
    out["rows_text"] = rows_for3(sl2, sref, pairs2, base["title"])
    return out
