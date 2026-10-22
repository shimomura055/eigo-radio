# -*- coding: utf-8 -*-
"""第3巡 集計/判定replay(0円)。読み制御後の音声へ (a)原綴り比較: 第2巡の現行プロキシ(Primary/Azureが原綴り一致)とN5_UND/R1_EXT、
 (b)置換後比較(R arm、Reicher方式): 比較対象を置換語にして判定、の両方を適用し、どちらでPASSかを記録する。"""
import collections, json, os, re, sys
sys.path.insert(0, os.getcwd())
from pathlib import Path
from er100_pnps_stage2_trial_01_common import *
import er100_pnps_stage2_trial_01_r2_arms as AR
import er100_pnps_stage2_trial_01_r2_replay as RPL
import er100_pnps_stage2_trial_01_r3_gen as G3

R2 = Path(OUT) / "r2"
R3 = Path(OUT) / "r3"
HEAD = "N5_UND"
est, S, A, ARMD = RPL.load_sets()
rows = load_rows()
other_unres = {}
for r in rows:
    other_unres.setdefault(r["canonical_text"], set()).update(set(unresolved_spans(r)) - set(TARGETS))
r2agg = json.load(open(R2 / "agg.json", encoding="utf-8"))
gen = json.load(open(R3 / "gen.json", encoding="utf-8"))
if (R3 / "gen_b.json").exists():
    gen += json.load(open(R3 / "gen_b.json", encoding="utf-8"))
SEG_WORDS = {s["id"]: s["words"] for s in G3.SEGS.values()}


def swap_back(text, rep, orig):
    return re.sub(r"\b" + re.escape(rep) + r"\b", orig, text, flags=re.I) if text else text


def spans(it, w, canon_api, canon_full):
    obs = {}
    for k in ("primary", "azure"):
        obs[k] = asr_span(canon_api, it.get(k), w) if it.get(k) is not None else None
    for k in ("whisper_small", "whisper_medium"):
        obs[k] = asr_span(canon_full, it.get(k), w) if it.get(k) is not None else None
    return obs


def rep_cands(rep_l):
    vs = AR.variants([rep_l], True)
    return {tuple(AR._bare(x) for x in v) for v in (vs or [])}


def eval_item(it):
    w = it["word"]
    sid = it["sid"]
    isR = it["arm"] in ("R", "R2")
    orig = G3.SUPPLY[w]["orig"] if it["arm"] in ("R", "R2", "H") else None
    canon_full_o = it["orig_canon"]
    rep = (it.get("rep_full") or it["words"][0]).lower() if isR else None
    api_c = it.get("api_canon") or it["canon"]
    api_c_o = swap_back(api_c, (it.get("rep_full") or it["words"][0]), orig.lower()) if rep else api_c
    full_c_o = canon_full_o
    res = {"id": it["id"], "take": it["take"], "arm": it["arm"], "wrong": it["wrong"], "word": w, "sid": sid, "tier": it["tier"], "supplied": it["supplied"], "sec": it.get("sec"), "wav": it["wav"],
           "api_scope": it.get("api_scope"), "strings_raw": {k: it.get(k) for k in ("primary", "azure", "whisper_small", "whisper_medium")}}
    words = SEG_WORDS.get(sid, [w]) if sid != "alt_short" else [w]
    blocked = sorted(other_unres.get(canon_full_o, set()))
    per = {}
    for ww in words:
        obs = spans(it, ww, api_c_o, full_c_o)
        per[ww] = {"strings": {k: (" ".join(v) if v else None) for k, v in obs.items()}, "proxy_pass_orig": AR.prod_pass_proxy(ww, obs),
                   "verdicts": {a: AR.judge(ww, full_c_o, obs, ARMD[ww], a)["verdict"] for a in ("R1_EXT", HEAD)}}
    res["per_word"] = per
    tw = per[w]
    res["target_word_proxy_orig"] = tw["proxy_pass_orig"]
    res["target_word_N5"] = tw["verdicts"][HEAD]
    res["target_word_R1_EXT"] = tw["verdicts"]["R1_EXT"]
    res["blocked_other_unresolved"] = blocked
    unsupplied = sorted(x for x in words if x != w and x in TARGETS)
    res["unsupplied_target_words_in_segment"] = unsupplied
    seg_block = bool(blocked or unsupplied)
    res["seg_proxy_orig_PASS"] = all(per[x]["proxy_pass_orig"] for x in words) and not blocked
    res["seg_N5_PASS"] = all(per[x]["verdicts"][HEAD] == "PASS_WITH_WARNING" for x in words) and not blocked
    if isR:
        tgt = it["words"][0] if it.get("rep_full") is None else norm_tokens(it["rep_full"])[0]
        obs_r = spans(it, tgt, api_c, it["canon"])
        cs = rep_cands(rep)
        nf = AR.nextfirst_of(it["canon"], rep)
        labs = {}
        for k in ("primary", "azure"):
            v = obs_r.get(k)
            labs[k] = AR.obs_label(tgt, v, cs, nf, AR.OPTS["N4_ASRG2P"])[0] if v else "UNALIGNED"
        for k in ("whisper_small", "whisper_medium"):
            v = obs_r.get(k)
            labs[k] = AR.obs_label(tgt, v, cs, nf, AR.OPTS["N4_ASRG2P"])[0] if v else "UNALIGNED"
        phon = all(labs[k] in ("EXACT", "MATCH") for k in ("primary", "azure"))
        n_match4 = sum(1 for l in labs.values() if l in ("EXACT", "MATCH"))
        res["replaced"] = {"rep": rep, "strings": {k: (" ".join(v) if v else None) for k, v in obs_r.items()}, "prod_exact_any": AR.prod_pass_proxy(rep, obs_r),
                           "prod_labels": labs, "PASS_phon_all_prod": phon, "engines_match_of4": n_match4}
        res["replaced_seg_PASS_exact"] = res["replaced"]["prod_exact_any"] and not seg_block
        res["replaced_seg_PASS_phon"] = phon and not seg_block
    res["seg_blocked_by_unsupplied_or_other"] = seg_block
    return res


def baseline():
    out = []
    ids = {x for x, _ in G3.BASE}
    for s in r2agg["segments"]:
        if "per_word" not in s or s["id"] not in ids:
            continue
        for w in ("khaite", "meink", "altuzarra"):
            if w in s["per_word"]:
                pw = s["per_word"][w]
                out.append({"id": s["id"], "take": s["take"], "word": w, "arm": "N", "proxy_orig": pw["proxy_pass"], "N5": pw["verdicts"]["N5_UND"], "R1_EXT": pw["verdicts"]["R1_EXT"],
                            "strings": pw["strings"], "seg_proxy": s["current_prod_proxy"], "src": "r2"})
    return out


def main():
    ev = [eval_item(g) for g in gen if not g.get("error")]
    errs = [g["id"] for g in gen if g.get("error")]
    base = baseline()
    for e in ev:
        if e["arm"] == "N":
            base.append({"id": e["sid"], "take": e["take"], "word": e["word"], "arm": "N", "proxy_orig": e["target_word_proxy_orig"], "N5": e["target_word_N5"], "R1_EXT": e["target_word_R1_EXT"],
                         "strings": e["per_word"][e["word"]]["strings"], "seg_proxy": "PASS" if e["seg_proxy_orig_PASS"] else "HR", "src": "r3"})
    ev_arm = [e for e in ev if e["arm"] in ("R", "R2", "H")]
    summ = collections.OrderedDict()
    for w in ("khaite", "meink", "altuzarra"):
        for arm in ("N", "R", "R2", "H"):
            if arm == "N":
                xs = [b for b in base if b["word"] == w]
                row = {"n": len(xs), "proxy_orig_PASS": sum(1 for b in xs if b["proxy_orig"]), "N5_PASS": sum(1 for b in xs if b["N5"] == "PASS_WITH_WARNING"), "N5_NG": sum(1 for b in xs if b["N5"] == "NG")}
            else:
                xs = [e for e in ev_arm if e["word"] == w and e["arm"] == arm and not e["wrong"]]
                if not xs:
                    continue
                row = {"n": len(xs), "tier": G3.SUPPLY[w]["tier"], "proxy_orig_PASS": sum(1 for e in xs if e["target_word_proxy_orig"]),
                       "N5_PASS": sum(1 for e in xs if e["target_word_N5"] == "PASS_WITH_WARNING"), "N5_NG": sum(1 for e in xs if e["target_word_N5"] == "NG"),
                       "N5_HRmaint": sum(1 for e in xs if e["target_word_N5"] not in ("PASS_WITH_WARNING", "NG"))}
                if arm in ("R", "R2"):
                    row["replaced_exact_PASS"] = sum(1 for e in xs if e["replaced"]["prod_exact_any"])
                    row["replaced_phon_PASS"] = sum(1 for e in xs if e["replaced"]["PASS_phon_all_prod"])
                row["seg_level_N5_PASS"] = sum(1 for e in xs if e["seg_N5_PASS"])
            summ[f"{w}/{arm}"] = row
    ctrl = []
    for e in ev_arm:
        if e["wrong"]:
            ctrl.append({"id": e["id"], "arm": e["arm"], "word": e["word"], "supplied_wrong": e["supplied"], "strings": e["per_word"][e["word"]]["strings"],
                         "orig_compare_proxy": e["target_word_proxy_orig"], "orig_compare_N5": e["target_word_N5"],
                         "replaced_engines_match_of4": (e["replaced"]["engines_match_of4"] if e["arm"] == "R" else None), "replaced_compare_exact_PASS": (e["replaced"]["prod_exact_any"] if e["arm"] == "R" else None),
                         "replaced_compare_phon_PASS": (e["replaced"]["PASS_phon_all_prod"] if e["arm"] == "R" else None)})
    byw = {"khaite": [], "meink": [], "altuzarra+toteme": [], "other": []}
    for s in r2agg["segments"]:
        if s.get("take") == "t1" and s.get("current_prod_proxy") == "HR":
            ws = set(s["words"])
            k = "khaite" if ws == {"khaite"} else "meink" if ws == {"meink"} else "altuzarra+toteme" if "altuzarra" in ws else "other"
            byw[k].append(s["id"])
    out = {"n_gen": len(gen), "errors": errs, "summary_by_word_arm": summ, "controls_wrong_supply": ctrl,
           "baseline_HR25": {"n": sum(len(v) for v in byw.values()), "by_group": byw}, "items": ev, "baseline_items": base}
    json.dump(out, open(R3 / "agg.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False, indent=0))
    print("CONTROLS")
    for c in ctrl:
        print(json.dumps(c, ensure_ascii=False))
    print("HR25 groups", {k: len(v) for k, v in byw.items()}, "errors", errs)


if __name__ == "__main__":
    main()
