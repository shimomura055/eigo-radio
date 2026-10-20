# -*- coding: utf-8 -*-
"""FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 eval拡張(委任_02a、Trial専用、API 0)。

既存eval(er084_..._eval.py)は編集せず、次を追加する:
 (a) 他語perturbation指標: 各(wav,条件,rep)で、Azure転写とwav原稿の語単位差分のうちターゲット語以外の差分語数・内容・保護語(数値/否定)への影響
 (b) 条件別の非ターゲット差分合計とベースライン(pl_unspecified)からの増減
 (c) 負例の誤Melos件数と、負例canonical注入のProduction判定(PASS系なら誤PASS)
 (d) 設計書§3の判定基準(1)-(5)の機械評価と候補Status。閾値は criteria_thresholds_01.json から読む(ハードコードしない)
Production判定は judge_fn(既定=er084 judge adapter、判定ロジック無変更)を注入可能。
"""
import argparse
import collections
import difflib
import json
import os
import sys

import er084_azure_phraselist_weight_trial_01_lib as L

CRITERIA_PATH = os.path.join(L.ROOT, "docs", "research", "FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01", "criteria_thresholds_01.json")


def load_criteria(path: str = CRITERIA_PATH) -> dict:
    return json.load(open(path, encoding="utf-8"))


def _tok(text: str) -> list:
    import er006_preprod_hardening_01_validation as v
    return v.tokenize(text or "")


def target_tokens(confusable=None) -> set:
    t = {L.TARGET.lower(), *L.WRONG_VARIANTS}
    if confusable:
        t.add(confusable.lower())
    return t


def perturbation(ref_text: str, hyp_text: str, confusable=None) -> dict:
    """ref(wav原稿)とhyp(Azure転写)の語単位差分から、ターゲット語を含む差分を除いた「他語perturbation」を返す。
    protected_impact=数値/否定への影響(Production protected_checkを呼ぶ)。"""
    import er006_preprod_hardening_01_validation as v
    r, h = _tok(ref_text), _tok(hyp_text)
    tt = target_tokens(confusable)
    sm = difflib.SequenceMatcher(None, r, h, autojunk=False)
    other, n_other_words, n_target_diffs = [], 0, 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        rs, hs = r[i1:i2], h[j1:j2]
        if any(t in tt for t in rs + hs):
            n_target_diffs += 1
            continue
        n_other_words += max(len(rs), len(hs))
        other.append(f"{' '.join(rs) or '∅'}→{' '.join(hs) or '∅'}")
    pc = v.protected_check(r, h)
    return {"n_other_diff_words": n_other_words, "other_diffs": other, "n_target_diffs": n_target_diffs,
            "protected_impact": bool(pc.number_mismatches or pc.negation_mismatches),
            "number_mismatches": [list(x) for x in pc.number_mismatches],
            "negation_mismatches": [list(x) for x in pc.negation_mismatches]}


def perturbation_rows(rows: list, meta: dict) -> list:
    out = []
    for r in rows:
        if r.get("err") or r.get("text") is None:
            continue
        m = meta.get(r["audio_id"], {})
        ref = m.get("text") or m.get("canonical_text") or ""
        p = perturbation(ref, r["text"], m.get("confusable"))
        out.append({"audio_id": r["audio_id"], "cond": r["cond"], "rep": r["rep"], **p})
    return out


def perturbation_by_condition(prows: list, baseline: str) -> dict:
    tot = collections.OrderedDict()
    for p in prows:
        c = tot.setdefault(p["cond"], {"n_rows": 0, "other_diff_words": 0, "protected_impact_rows": 0})
        c["n_rows"] += 1
        c["other_diff_words"] += p["n_other_diff_words"]
        c["protected_impact_rows"] += 1 if p["protected_impact"] else 0
    b = tot.get(baseline)
    for k, c in tot.items():
        c["delta_vs_baseline"] = None if b is None else c["other_diff_words"] - b["other_diff_words"]
        c["rows_per_baseline_rows_adj_delta"] = None
        if b is not None and b["n_rows"] and c["n_rows"]:
            # 行数が異なる場合に備えた1行あたり差(baseline比)
            c["per_row_delta_vs_baseline"] = round(c["other_diff_words"] / c["n_rows"] - b["other_diff_words"] / b["n_rows"], 4)
    return tot


def is_pass_family(state, prefix: str) -> bool:
    return bool(state) and str(state).startswith(prefix)


def _default_judge(canonical, primary, secondary, wav_path):
    import er084_azure_phraselist_weight_trial_01_judge as J
    return J.judge_offline(canonical, primary, secondary, wav_path)


def _hits(text) -> int:
    return len(L.RE_MELOS.findall(text or ""))


def _wav_cond_stats(rows: list, meta: dict) -> dict:
    """(audio_id, cond) -> {reps:[{rep,text,hits,correct}], all_correct, none_correct}。errは除外(n_errを別記録)。"""
    out = {}
    for r in rows:
        k = (r["audio_id"], r["cond"])
        m = meta.get(r["audio_id"], {})
        exp = m.get("expected_melos", 1 if m.get("label", "positive") == "positive" else 0)
        d = out.setdefault(k, {"reps": [], "n_err": 0})
        if r.get("err") or r.get("text") is None:
            d["n_err"] += 1
            continue
        h = _hits(r["text"])
        d["reps"].append({"rep": r["rep"], "text": r["text"], "hits": h,
                          "correct": (h == exp and exp > 0) if m.get("label", "positive") == "positive" else h == 0})
    for d in out.values():
        d["all_correct"] = bool(d["reps"]) and all(x["correct"] for x in d["reps"])
        d["none_correct"] = bool(d["reps"]) and not any(x["correct"] for x in d["reps"])
    return out


def negatives_summary(rows: list, meta: dict, criteria: dict, judge_fn=None) -> dict:
    """負例の誤Melos件数と、負例canonical(confusable->Melos置換)注入のProduction判定による誤PASS件数(条件別)。"""
    judge_fn = judge_fn or _default_judge
    pf = criteria["pass_family_prefix"]
    per = collections.OrderedDict()
    cache = {}
    for r in rows:
        m = meta.get(r["audio_id"], {})
        if m.get("label") != "negative" or r.get("err") or r.get("text") is None:
            continue
        c = per.setdefault(r["cond"], {"n_rows": 0, "false_melos": 0, "false_pass": 0, "judge_unavailable": 0})
        c["n_rows"] += 1
        if _hits(r["text"]) > 0:
            c["false_melos"] += 1
            if m.get("primary_text") is None:
                c["judge_unavailable"] += 1
                continue
            k = (r["audio_id"], r["text"])
            if k not in cache:
                cache[k] = judge_fn(m["canonical_text"], m["primary_text"], r["text"], os.path.join(L.ROOT, m.get("path", "")))
            if is_pass_family(cache[k].get("state"), pf):
                c["false_pass"] += 1
    return per


def evaluate_criteria(rows: list, meta: dict, criteria: dict, judge_fn=None) -> dict:
    """設計書§3の判定基準(1)-(5)を機械評価し候補Statusを返す。rows=Phase Bのazure rows(全行・除外なし)。"""
    judge_fn = judge_fn or _default_judge
    pf = criteria["pass_family_prefix"]
    base = criteria["baseline_cond"]
    stats = _wav_cond_stats(rows, meta)
    pos_ids = sorted({a for (a, _c) in stats if meta.get(a, {}).get("label", "positive") == "positive"})
    R = [a for a in pos_ids if stats.get((a, base), {}).get("none_correct")]
    base_ok = [a for a in pos_ids if stats.get((a, base), {}).get("all_correct")]
    unstable_base = [a for a in pos_ids if (a, base) in stats and a not in R and a not in base_ok]
    neg = negatives_summary(rows, meta, criteria, judge_fn)
    base_false = neg.get(base, {}).get("false_melos", 0)
    out = {"baseline": base, "R": len(R), "R_ids": R, "baseline_all_correct": len(base_ok),
           "baseline_unstable": unstable_base, "negatives": neg, "per_weight": {}}
    if len(R) < criteria["min_R_for_identifiability"]:
        out["status"] = "INCONCLUSIVE"
        out["reason"] = f"R={len(R)} < {criteria['min_R_for_identifiability']}: 識別不能(効果の有無を断定しない)"
    for w in criteria["candidate_conds"]:
        fixed = [a for a in R if stats.get((a, w), {}).get("all_correct")]
        unstable_w = [a for a in R if (a, w) in stats and not stats[(a, w)]["all_correct"] and not stats[(a, w)]["none_correct"]]
        degraded = [a for a in base_ok if (a, w) in stats and not stats[(a, w)]["all_correct"]]
        nf = neg.get(w, {}).get("false_melos", 0)
        c1 = len(fixed) >= criteria["fixed_min_abs"] and len(fixed) >= criteria["fixed_min_fraction_of_R"] * max(len(R), 1)
        c2 = (nf - base_false) <= criteria["negative_false_melos_increase_max"]
        c3 = len(degraded) <= criteria["degraded_max_abs"] and (
            len(degraded) < criteria["degraded_fraction_of_fixed_exclusive_upper"] * len(fixed) if fixed else len(degraded) == 0)
        fixed_ctx = {meta[a].get("sentence_id") for a in fixed}
        fixed_vs = {(meta[a].get("voice"), bool(meta[a].get("slow6"))) for a in fixed}
        c4 = len(fixed_ctx) >= criteria["min_contexts_sentences"] and len(fixed_vs) >= criteria["min_voice_speed_conditions"]
        # (5) fixed wavの全repでw=PASS系かつ baseline=非PASS系 + 負例canonical誤PASS<=上限
        c5_detail, c5_ok, c5_unavail = [], True, False
        for a in fixed:
            m = meta[a]
            if m.get("primary_text") is None:
                c5_unavail = True
                continue
            okw = True
            for cond, want_pass in ((w, True), (base, False)):
                for rp in stats[(a, cond)]["reps"]:
                    st = judge_fn(m["canonical_text"], m["primary_text"], rp["text"], os.path.join(L.ROOT, m.get("path", ""))).get("state")
                    if is_pass_family(st, pf) != want_pass:
                        okw = False
            c5_detail.append({"audio_id": a, "ng_to_pass": okw})
            c5_ok = c5_ok and okw
        fp = neg.get(w, {}).get("false_pass", 0)
        c5 = None if (c5_unavail or not fixed) else (c5_ok and fp <= criteria["negative_canonical_false_pass_max"])
        if len(R) < criteria["min_R_for_identifiability"]:
            status = "INCONCLUSIVE"
        elif not c1:
            status = "REJECTED"
        elif not c2 or not c4:
            status = "判断候補"
        elif c3 and c5:
            status = "VALIDATED候補"
        else:
            status = "判断候補"
        out["per_weight"][w] = {"fixed": len(fixed), "fixed_ids": fixed, "unstable_in_R": unstable_w, "degraded": len(degraded),
                                "degraded_ids": degraded, "neg_false_melos": nf, "neg_false_melos_baseline": base_false,
                                "neg_false_pass": fp, "criteria": {"1_fixed": c1, "2_neg_not_increased": c2, "3_degraded": c3,
                                                                   "4_reproduced": c4, "5_judge_ng_to_pass": c5},
                                "fixed_contexts": sorted(x for x in fixed_ctx if x), "fixed_voice_speed": sorted(map(str, fixed_vs)),
                                "criterion5_detail": c5_detail, "status": status}
    if "status" not in out:
        sts = [v["status"] for v in out["per_weight"].values()]
        out["status"] = ("VALIDATED候補" if "VALIDATED候補" in sts else "判断候補" if "判断候補" in sts else
                         "REJECTED" if all(s == "REJECTED" for s in sts) else "INCONCLUSIVE")
    return out


def load_meta(manifest: dict, primary_rows: list) -> dict:
    prim = {r["audio_id"]: r["text"] for r in primary_rows if not r.get("err")}
    meta = {}
    for a in manifest["audio"]:
        meta[a["id"]] = {k: a.get(k) for k in ("label", "canonical_text", "text", "expected_melos", "confusable", "voice",
                                                "slow6", "sentence_id", "path", "take")}
        meta[a["id"]]["primary_text"] = prim.get(a["id"])
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="Phase Bのraw/azure_calls.jsonl(全行)")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--primary", required=True, help="raw/primary_calls.jsonl")
    ap.add_argument("--out", required=True, help="json出力")
    a = ap.parse_args(argv)
    crit = load_criteria()
    rows = L.read_raw(a.raw)
    meta = load_meta(json.load(open(a.manifest, encoding="utf-8")), L.read_raw(a.primary))
    prows = perturbation_rows(rows, meta)
    res = {"perturbation_by_condition": perturbation_by_condition(prows, crit["baseline_cond"]), "perturbation_rows": prows,
           "criteria_eval": evaluate_criteria(rows, meta, crit)}
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"status={res['criteria_eval']['status']} rows={len(rows)} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
