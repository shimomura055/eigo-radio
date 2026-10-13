# ============================================================
# er064_kp_int_01_machine.py  (FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 Round1 / A. 機械抽出パターン、Trial専用)
# Production code/DBは編集しない(読取・呼出のみ)。有料呼出なし。Wiktionaryはsnapshot再生のみ。
# M0=現行 / M1=guarded(予算拡大+precision guard+U2+U3) / M2=M1+(a)placeholder照合+(b2)ルール所有格3-gram+(c)予約枠(cap3、追加LLMなし)
# M3=M2+辞書一致種別(match:)注釈。
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time

sys.path.insert(0, os.getcwd())
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3  # noqa: E402
import er030_key_phrase_db_hybrid_source_reference_contract_01 as contract  # noqa: E402
import er030_key_phrase_db_hybrid_selector_01 as sel  # noqa: E402
import er064_kp_idiom_trial_01_matcher as M  # noqa: E402
import er064_kp_idiom_trial_01_pipeline as P  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402
import er064_kp_opt_01_upstream_core as U  # noqa: E402

OUT = "er064_output/kp_integrated_opt_01/round1"
RESERVED_CAP = 3
LABEL_MATCH = "match:"
PATTERNS = ("M0", "M1", "M2", "M3")
ARTICLE_KEYS = ["coffee_std", "coffee_adv", "meta_std", "meta_adv", "hormuz_std", "hormuz_adv", "smallbag_std", "smallbag_adv", "semi_std", "semi_adv"]
_pats = None


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def tok_count(s):
    p = os.environ.get("TIKTOKEN_PATH")
    if p and p not in sys.path:
        sys.path.insert(0, p)
    try:
        import tiktoken
        return len(tiktoken.get_encoding("o200k_base").encode(s))
    except Exception:
        return U.approx_tokens(s)


def match_kind(c, wk):
    """辞書一致の種別(選定側へ伝える確度)。None=辞書と無関係(ヒューリスティック/語彙表のみ)。"""
    ev = c.get("evidence")
    if ev == "placeholder_title":
        return "placeholder"
    if ev == "rule_poss_pattern":
        return "pattern"
    dbs = c.get("matched_dbs") or []
    if "wiktionary" not in dbs:
        return None
    if c.get("db_categories") == ["multiword_term"]:
        return "term"
    return "exact" if c["canonical_form"] in wk else "inflected"


def ev_text(c):
    ev = c.get("evidence")
    if ev == "placeholder_title":
        return f"placeholder_title[{c.get('matched_title')}]"
    if ev == "rule_poss_pattern":
        return "rule_poss_pattern"
    return sel._compact_evidence_string(c)


def rows_for(sl, sref, pairs, title, with_match, wk):
    wc = contract.assign_candidate_ids(sl)
    ids = {c["canonical_form"]: c["candidate_id"] for c in wc["shortlist_with_ids"]}
    contains, contained = {}, {}
    for p in pairs:
        if p["small"] in ids and p["big"] in ids:
            contains.setdefault(p["big"], []).append(ids[p["small"]])
            contained.setdefault(p["small"], []).append(ids[p["big"]])

    def ev(c):
        s = ev_text(c)
        if c["canonical_form"] in contains:
            s += " | " + U.LABEL_CONTAINS + " " + ",".join(contains[c["canonical_form"]])
        if c["canonical_form"] in contained:
            s += " | " + U.LABEL_CONTAINED + " " + ",".join(contained[c["canonical_form"]])
        if c.get("fragment_risk"):
            s += " | " + U.LABEL_FRAGMENT
        if with_match:
            k = match_kind(c, wk)
            if k:
                s += " | " + LABEL_MATCH + " " + k
        return s
    return contract.build_lightweight_user_message(title, wc["shortlist_with_ids"], sref, "", "family_x", None, ev)


def get_pats():
    global _pats
    if _pats is None:
        R._init()
        _pats = M.build_pattern_index(R._dbs)
    return _pats


_cache = {}


def build_pattern(key, pat):
    """戻り値: dict(shortlist, sentence_reference, pairs, rows_text, title, reserved, tier_h_dropped, secs)"""
    if (key, pat) in _cache:
        return _cache[(key, pat)]
    t0 = time.time()
    R._init()
    wk = R._dbs["wiktionary"]
    if pat in ("M0", "M1"):
        m1 = R.build_method1(key, "current" if pat == "M0" else "alt_precision_guarded")
        out = {"shortlist": m1["shortlist"], "sentence_reference": m1["sentence_reference"], "pairs": m1["pairs"], "rows_text": m1["rows_text"],
               "title": m1["title"], "reserved": [], "tier_h_dropped": [], "pool_sizes": {}}
    else:
        base = build_pattern(key, "M1")
        st0 = R._base(key)[0]
        units = st0["sentence_units"]
        existing = {c["canonical_form"] for c in base["shortlist"]} | P._canon_set(st0)
        pc = M.placeholder_candidates(units, get_pats(), R._dbs, set(existing))
        ex2 = set(existing) | {c["canonical_form"] for c in pc}
        rc = M.rule_possessive_pattern_candidates(units, R._dbs, ex2)
        art = U.read_article(key)

        def contiguous(c):  # 句読点をまたぐ3-gram(`news, your wallet`型)を除外: 本文に空白のみで連続して実在すること(Phase Dの決定論検証と同種)
            pat = r"\b" + r"\s+".join(re.escape(t) for t in c["surface_form"].split()) + r"\b"
            return re.search(pat, art, re.I) is not None
        dropped_nc = [c["canonical_form"] for c in pc + rc if not contiguous(c)]
        pc = [c for c in pc if contiguous(c)]
        rc = [c for c in rc if contiguous(c)]
        pool = sorted(pc + rc, key=P.reserved_sort_key)
        reserved, overflow = pool[:RESERVED_CAP], pool[RESERVED_CAP:]
        ctx = s1v3.attach_compact_context(reserved, units) if reserved else {"shortlist": [], "sentence_reference": {}}
        sref = dict(base["sentence_reference"])
        sref.update(ctx["sentence_reference"])
        sl = list(base["shortlist"])
        for c in ctx["shortlist"]:
            c2 = dict(c)
            registered = bool(M.baseline_hit(c2["surface_form"], R._dbs)) or c2.get("evidence") == "placeholder_title"
            c2["fragment_risk"] = U.fragment_risk(c2["surface_form"], registered, no_aux=True)
            sl.append(c2)
        pairs = U.compute_containment(sl, units, r2=True) if ctx["shortlist"] else base["pairs"]
        drop = {p["small"] for p in pairs if p["tier"] == "H"}
        sl = [c for c in sl if c["canonical_form"] not in drop]
        pairs = [p for p in pairs if p["small"] not in drop]
        out = {"shortlist": sl, "sentence_reference": sref, "pairs": pairs, "title": base["title"], "reserved": [c["canonical_form"] for c in ctx["shortlist"]],
               "tier_h_dropped": sorted(drop),
               "pool_sizes": {"dropped_non_contiguous": dropped_nc, "placeholder": len(pc), "rule_poss": len(rc), "overflow_beyond_cap": [c["canonical_form"] for c in overflow],
                              "placeholder_list": [(c["canonical_form"], c.get("matched_title")) for c in pc]}}
        out["rows_text"] = rows_for(sl, sref, pairs, base["title"], pat == "M3", wk)
    out["secs"] = round(time.time() - t0, 2)
    _cache[(key, pat)] = out
    return out


def _count(xs):
    d = {}
    for x in xs:
        d[x] = d.get(x, 0) + 1
    return d


def describe(key, pat):
    R._init()
    wk = R._dbs["wiktionary"]
    b = build_pattern(key, pat)
    m0 = build_pattern(key, "M0")
    cl = [c["canonical_form"] for c in b["shortlist"]]
    c0 = [c["canonical_form"] for c in m0["shortlist"]]
    return {"n_candidates": len(cl), "rows_tokens": tok_count(b["rows_text"]), "rows_sha256": sha(b["rows_text"]), "added_vs_M0": [c for c in cl if c not in c0],
            "removed_vs_M0": [c for c in c0 if c not in cl], "reserved": b["reserved"], "tier_h_dropped": b["tier_h_dropped"],
            "pool_sizes": b["pool_sizes"], "build_secs": b["secs"],
            "match_kind_counts": _count([match_kind(c, wk) or "-" for c in b["shortlist"] if c["unit_type"] != "word"]),
            "candidates": [{"surface_form": c["surface_form"], "canonical_form": c["canonical_form"], "unit_type": c["unit_type"],
                            "evidence": ev_text(c), "match_kind": match_kind(c, wk), "fragment_risk": bool(c.get("fragment_risk"))} for c in b["shortlist"]]}


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"purpose": "Round1 A. 機械抽出パターン M0-M3の固定shortlist(実タイトル、Trial専用)", "label_match": LABEL_MATCH,
           "snapshot_sha256": U.sha256_file(U.SNAPSHOT_PATH), "reserved_cap": RESERVED_CAP, "articles": {}}
    for key in ARTICLE_KEYS:
        ent = {"article_path": U.ARTICLES[key], "article_sha256": U.sha256_text(U.read_article(key)), "title": R.real_title(key)}
        for pat in PATTERNS:
            d = describe(key, pat)
            b = build_pattern(key, pat)
            d["rows_text"] = b["rows_text"]
            d["sentence_reference"] = b["sentence_reference"]
            ent[pat] = d
        res["articles"][key] = ent
        print(key, {p: (ent[p]["n_candidates"], ent[p]["rows_tokens"], ent[p]["reserved"]) for p in PATTERNS}, flush=True)
    body = json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True)
    open(f"{OUT}/shortlists_r1.json", "w", encoding="utf-8", newline="\n").write(body)
    open(f"{OUT}/shortlists_r1.sha256.txt", "w", encoding="utf-8", newline="\n").write(hashlib.sha256(body.encode("utf-8")).hexdigest() + "  shortlists_r1.json\n")


if __name__ == "__main__":
    main()
