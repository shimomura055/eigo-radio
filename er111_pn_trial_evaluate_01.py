# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 PN 委任_02: Trial用の受理判定wrapper [DEV/Trial専用・Production未配線]

er103.evaluate_alarm_eligibility の**複製**(G3だけ RET-3 厳密版、G5の証拠に位置紐づけ実体表を追加)。er103は無変更。
  * 表が None / 空 のとき、判定は er103 と**完全一致**(SC-1。test と評価scriptで固定)。
  * drift guard: 複製元 er103 の関数 source の sha256 を ORIG_SOURCE_SHA256 に固定し、変わったら test が落ちる(OF-PN2-11)。
  * 受理境界(類似度>=0.40・一般語ブロック・P-03・G3・数値/否定・KP/JA除外・slot)は er103 の関数/定数をそのまま使う。
  * RET-3(OF-PN2-02): Secondary diff の span が Primary diff の固有名詞 token に隣接する語を巻き込んだ場合(従来は不受理)に限り、
      (i) span が当該位置で連続する1実体出現(または区切り語なし隣接複数実体)とtoken単位で一致 (ii) span が重なる Primary diff を全て含む
      (iii) 合成 span にも `_noun_checks` と P-03 を適用  のすべてを満たす場合のみ許容。
"""
from __future__ import annotations

import hashlib
import inspect
import re
from dataclasses import dataclass
from typing import Callable, Optional

import er103_proper_noun_alarm_policy_01 as pol
import er111_pn_entity_table_trial_01 as ret

# 複製元の drift guard(2026-10-23 時点の er103 ソース)。変わったら本複製の再照合が必要。
GUARDED = ("evaluate_alarm_eligibility", "_noun_checks", "proper_noun_evidence", "is_general_word", "asr_all_general")
ORIG_SOURCE_SHA256 = {
    "evaluate_alarm_eligibility": "a08ce056990358a5ed35f8036f079a8bb4662fc2e57603e541b5a90502804384",
    "_noun_checks": "77a53af7be6b9717903ca57ebe140ed99eadafdc3e1172c88c31b21715d0063b",
    "proper_noun_evidence": "65c78fdcf0138e0dfbec9e80297d6f4784245cd646f95307c9c70c3f7706c074",
    "is_general_word": "e7b544d04e0a643424d3225380529002740ea6251d430e8436be2910f0f1b4c4",
    "asr_all_general": "b11a8e9ccf0559f08ade7ec2e71e556f06c6a5d55ee3d740386cd7ae95e5b06d",
}


def source_hashes() -> dict:
    return {n: hashlib.sha256(inspect.getsource(getattr(pol, n)).replace(chr(13) + chr(10), chr(10)).encode("utf-8")).hexdigest() for n in GUARDED}


R_RET3 = "RET3_SPAN_NOT_ENTITY_RUN"


def alarm_labels(diff: "pol.AlarmDiff", *, zipf: Callable = pol._default_zipf) -> dict:
    """OF-PN2-08: 区別は関門でなく、アラームのラベル(試聴優先度)にする。受理境界は変えない。"""
    sp = diff.similarity_primary
    band = "high(>=0.70)" if sp >= 0.70 else ("mid(0.50-0.70)" if sp >= 0.50 else "low(0.40-0.50)")
    same_other = bool(diff.asr_secondary) and _fold_eq(diff.asr_primary, diff.asr_secondary)
    border = False
    for tk in re.findall(r"[a-z0-9']+", pol._fold(diff.asr_primary + " " + (diff.asr_secondary or ""))):
        z = zipf(tk)
        if 3.5 <= z < 4.0:
            border = True
    return {"similarity_band": band, "both_asr_same_other_word": same_other, "asr_zipf_near_general_boundary": border}


def _fold_eq(a: str, b: str) -> bool:
    return pol._despaced(a) == pol._despaced(b)


def _ret3_check(table: "ret.EntityTable", d_sec: dict, dp: list, canonical_text: str, *, ledger_surfaces, cmu_has, zipf, max_asr_per_canon,
                min_similarity, role) -> tuple:
    """戻り値=(True, record) | (False, reason)。"""
    span_tokens = d_sec["canonical"].split()
    run = table.entity_run_for_span(canonical_text, span_tokens)
    if run is None:
        return False, "span_not_one_entity_run"
    # (ii) span と重なる Primary diff は全て span に含まれること、かつ1つ以上含まれること
    contained = []
    for p in dp:
        for (a, b) in table.phrase_positions(canonical_text, p["canonical"].split()):
            for (sa, sb) in run["positions"]:
                overlap = not (b < sa or sb < a)
                if overlap and not (sa <= a and b <= sb):
                    return False, "primary_diff_straddles_span_boundary"
                if sa <= a and b <= sb:
                    contained.append(p)
    if not contained:
        return False, "no_primary_diff_inside_span"
    # (iii) 合成 span にも _noun_checks(類似度/ASR長/数値否定/一般語)
    ls = frozenset(ledger_surfaces) | run["grant"]
    bad, info, sim = pol._noun_checks(d_sec["canonical"], d_sec["asr"], canonical_text, ledger_surfaces=ls, cmu_has=cmu_has, zipf=zipf,
                                      max_asr_per_canon=max_asr_per_canon, min_similarity=min_similarity, supply_map=None, role=role)
    if bad:
        return False, "noun_checks:%s" % bad
    # P-03: 合成 span についても Primary側ASR句・Secondary側ASR句が両方とも全token一般語なら不受理
    p_asr = " ".join(p["asr"] for p in contained)
    if pol.asr_all_general(p_asr, cmu_has=cmu_has, zipf=zipf) and pol.asr_all_general(d_sec["asr"], cmu_has=cmu_has, zipf=zipf):
        return False, "p03_both_asr_general"
    label = _relabel(d_sec["canonical"], info, frozenset(ledger_surfaces), run["grant"], {"entities": run["entities"]}, canonical_text, cmu_has, role)
    return True, {"span": d_sec["canonical"], "asr_secondary": d_sec["asr"], "similarity": sim, "entities": run["entities"], "evidence": label}


def _relabel(canon: str, info: str, base_ledger, grant, ginfo, canonical_text, cmu_has, role) -> str:
    """grant に依存して通った token の証拠ラベルを `entity_table:<grade>:<category>` へ置換する。"""
    if not grant or not isinstance(info, str) or info == "supplied_respelling":
        return info
    ents = {w: (e["grade"], e["category"]) for e in (ginfo or {}).get("entities", []) for w in e["words"]}
    evs = []
    for t in canon.split():
        ok, ev = pol.proper_noun_evidence(t, canonical_text, ledger_surfaces=base_ledger, cmu_has=cmu_has, role=role)
        if ok:
            evs.append(ev)
        else:
            g, c = ents.get(t, ("confirmed", "?"))
            evs.append("entity_table:%s:%s" % (g, c))
    return "+".join(sorted(set(evs)))


def evaluate_alarm_eligibility_pn(
        *, canonical_text: str, primary_cls, secondary_cls, primary_text: Optional[str], secondary_text: Optional[str],
        judge_state: str, judge_reason_code: str, role: Optional[str], lang: str = "en", vote_required: bool = False,
        enabled: bool = True, ledger_surfaces: frozenset = frozenset(),
        cmu_has: Callable = pol._default_cmu_has, zipf: Callable = pol._default_zipf,
        max_diffs: int = pol.MAX_DIFFS_PER_SEGMENT, max_asr_per_canon: int = pol.MAX_ASR_TOKENS_PER_CANON_TOKEN,
        min_similarity: float = pol.MIN_SPAN_SIMILARITY, supply_map: Optional[dict] = None,
        p3_entry: Optional[str] = None, max_secondary_noise: int = pol.MAX_SECONDARY_NOISE,
        table: Optional["ret.EntityTable"] = None, ret3: bool = True) -> "pol.AlarmDecision":
    """er103.evaluate_alarm_eligibility の複製(Trial)。差分は table(位置紐づけ証拠)と RET-3 のみ。table=None/空なら er103 と同値。"""
    AlarmDecision, AlarmDiff = pol.AlarmDecision, pol.AlarmDiff
    if table is not None and table.is_empty():
        table = None
    if not enabled:
        return AlarmDecision(False, pol.R_DISABLED)
    if str(lang).lower() not in ("en", "en-us"):
        return AlarmDecision(False, pol.R_LANG)
    if vote_required:
        return AlarmDecision(False, pol.R_DUAL)
    if role not in pol.APPLICABLE_ROLES:
        return AlarmDecision(False, pol.R_ROLE, detail={"role": role})
    if judge_state != pol.JUDGE_STATE_ELIGIBLE or judge_reason_code != pol.JUDGE_REASON_ELIGIBLE:
        return AlarmDecision(False, pol.R_JUDGE_STATE, detail={"judge_state": judge_state, "reason_code": judge_reason_code})
    if p3_entry != "p3_primary_ng":
        return AlarmDecision(False, pol.R_P3_ENTRY, detail={"p3_entry": p3_entry})
    if not secondary_text or secondary_cls is None:
        return AlarmDecision(False, pol.R_SECONDARY_MISSING)
    if primary_cls is None or primary_cls.classification != "ASR_VALIDATION_UNCERTAIN":
        return AlarmDecision(False, pol.R_PRIMARY_NOT_ENTITY_ONLY, detail={"classification": getattr(primary_cls, "classification", None)})
    dp = list(primary_cls.protected.content_word_diffs or [])
    if not dp:
        return AlarmDecision(False, pol.R_NO_DIFF)
    if not all(d.get("entity_like") for d in dp):
        return AlarmDecision(False, pol.R_PRIMARY_NOT_ENTITY_ONLY, detail={"diffs": [(d["canonical"], d["asr"]) for d in dp if not d.get("entity_like")]})
    if len(dp) > max_diffs:
        return AlarmDecision(False, pol.R_TOO_MANY_DIFFS, detail={"primary": len(dp)})

    ds = list(secondary_cls.protected.content_word_diffs or [])
    noun_tokens = {t for d in dp for t in d["canonical"].split()}
    p_canons = {d["canonical"] for d in dp}
    noise = []
    by_canon_s = {}
    ret3_records = []
    for d in ds:
        c_set = set(d["canonical"].split())
        if d["canonical"] in p_canons:
            if not (d.get("entity_like") or c_set <= (noun_tokens | {"s"})):
                return AlarmDecision(False, pol.R_SECONDARY_NOT_ENTITY_ONLY, detail={"canonical": d["canonical"], "asr_secondary": d["asr"]})
            by_canon_s[d["canonical"]] = d
        elif c_set & noun_tokens:
            rest = [t for t in d["canonical"].split() if t not in noun_tokens and t != "s"]
            asr_toks = d["asr"].split()
            if not all(any(pol._same_or_plural(t, a) for a in asr_toks) for t in rest):
                rescued = None
                if table is not None and ret3:                       # --- RET-3(Trial差分) ---
                    ok3, rec = _ret3_check(table, d, dp, canonical_text, ledger_surfaces=ledger_surfaces, cmu_has=cmu_has, zipf=zipf,
                                           max_asr_per_canon=max_asr_per_canon, min_similarity=min_similarity, role=role)
                    if ok3:
                        rescued = rec
                    else:
                        ret3_why = rec
                if rescued is None:
                    det = {"canonical": d["canonical"], "asr_secondary": d["asr"], "why": "adjacent_word_changed"}
                    if table is not None and ret3:
                        det["ret3_rejected"] = ret3_why
                    return AlarmDecision(False, pol.R_SECONDARY_NOT_ENTITY_ONLY, detail=det)
                ret3_records.append(rescued)
                noise.append({"canonical": d["canonical"], "asr_secondary": d["asr"], "entity_like": bool(d.get("entity_like")), "merged_with_noun": True, "ret3": True})
                continue
            noise.append({"canonical": d["canonical"], "asr_secondary": d["asr"], "entity_like": bool(d.get("entity_like")), "merged_with_noun": True})
        else:
            noise.append({"canonical": d["canonical"], "asr_secondary": d["asr"], "entity_like": bool(d.get("entity_like"))})
    n_non_proper = sum(1 for nz in noise if not nz.get("entity_like") and not nz.get("merged_with_noun") and nz["canonical"].strip() != "s")
    if n_non_proper > max_secondary_noise:
        return AlarmDecision(False, pol.R_SECONDARY_NOISE_LIMIT, detail={"non_proper_noise_count": n_non_proper, "noise_count": len(noise)})
    for nz in noise:
        ctoks = [t for t in nz["canonical"].split() if t not in pol._FUNCTION_WORDS and t != "s"]
        atoks = [t for t in nz["asr_secondary"].split() if t not in pol._FUNCTION_WORDS and t != "s"]
        if len(ctoks) - len(atoks) >= pol.MAX_SECONDARY_NOISE_DROPPED_CONTENT:
            return AlarmDecision(False, pol.R_SECONDARY_NOISE_LIMIT, detail={"dropped_content_words": ctoks, "asr_secondary": nz["asr_secondary"]})
    out = []
    table_used = []
    for d in dp:
        grant, ginfo = (frozenset(), None)
        if table is not None:
            grant, ginfo = table.grant_for_phrase(canonical_text, d["canonical"].split())     # 位置紐づけ(OF-PN2-01): このPrimary句だけに付与
        ls = frozenset(ledger_surfaces) | grant
        bad, info, sim_p = pol._noun_checks(d["canonical"], d["asr"], canonical_text, ledger_surfaces=ls, cmu_has=cmu_has,
                                            zipf=zipf, max_asr_per_canon=max_asr_per_canon, min_similarity=min_similarity, supply_map=supply_map, role=role)
        if bad:
            return AlarmDecision(False, bad, detail=info)
        sh = by_canon_s.get(d["canonical"])
        asr_s, sim_s = "", None
        if sh is not None:
            bad_s, info_s, sim_s = pol._noun_checks(d["canonical"], sh["asr"], canonical_text, ledger_surfaces=ls,
                                                    cmu_has=cmu_has, zipf=zipf, max_asr_per_canon=max_asr_per_canon, min_similarity=min_similarity, supply_map=supply_map, role=role)
            if bad_s:
                return AlarmDecision(False, bad_s, detail={"side": "secondary", **(info_s if isinstance(info_s, dict) else {})})
            asr_s = sh["asr"]
            if not (supply_map and any(t in supply_map for t in d["canonical"].split())) \
                    and pol.asr_all_general(d["asr"], cmu_has=cmu_has, zipf=zipf) and pol.asr_all_general(asr_s, cmu_has=cmu_has, zipf=zipf):
                return AlarmDecision(False, pol.R_ASR_BOTH_GENERAL_WORDS,
                                     detail={"canonical": d["canonical"], "asr_primary": d["asr"], "asr_secondary": asr_s})
        # 証拠ラベル: 表に依存して通ったtokenは entity_table:<grade>:<category>
        label = _relabel(d["canonical"], info, frozenset(ledger_surfaces), grant, ginfo, canonical_text, cmu_has, role) if grant else info
        if grant:
            table_used.append({"canonical": d["canonical"], **(ginfo or {})})
        out.append(AlarmDiff(d["canonical"], d["asr"], asr_s, label, sim_p, sim_s if sim_s is not None else 1.0))
    detail = {"secondary_only_noise": noise}
    if table is not None and (table_used or ret3_records):
        detail["entity_table"] = {"sha256": table.sha256(), "status": table.status, "per_diff": table_used, "ret3": ret3_records,
                                  "entries_used": _unique_entries(table, table_used, ret3_records)}
        detail["alarm_labels"] = [alarm_labels(x, zipf=zipf) for x in out]
    return AlarmDecision(True, "ENTITY_ONLY_ACCEPT", diffs=out, detail=detail)


def _unique_entries(table: "ret.EntityTable", table_used: list, ret3_records: list) -> list:
    """OF-PN2-06(i): 受理に使った実体entry(surface/words/category/grade/eligible/initials)を完全な形で返す(アラームblockへ保存して再判定に使う)。"""
    names = []
    for rec in table_used:
        names += [e["surface"] for e in rec.get("entities", [])]
    for rec in ret3_records:
        names += [e["surface"] for e in rec.get("entities", [])]
    seen, res = set(), []
    for e in table.entries:
        if e.surface in names and e.surface not in seen:
            seen.add(e.surface)
            res.append(e.to_dict())
    return res
