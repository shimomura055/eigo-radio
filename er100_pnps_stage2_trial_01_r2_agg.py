# -*- coding: utf-8 -*-
"""第2巡 集計(0円): 新規生成音声(現行TTS)30 segment(+take2)と負例(確認済み誤読)へ全armを適用。"""
import collections, json, os, sys
sys.path.insert(0, os.getcwd())
from pathlib import Path
from er100_pnps_stage2_trial_01_common import *
import er100_pnps_stage2_trial_01_r2_arms as AR
import er100_pnps_stage2_trial_01_r2_replay as RPL

R2 = Path(OUT) / "r2"
HEADLINE = os.environ.get("R2_HEADLINE", "N5_UND")


def spans(item, w):
    obs = {}
    ac = item.get("api_canon") or item["canon"]
    for k in ("primary", "azure"):
        obs[k] = asr_span(ac, item.get(k), w) if item.get(k) is not None else None
    for k in ("whisper_small", "whisper_medium"):
        obs[k] = asr_span(item["canon"], item.get(k), w) if item.get(k) is not None else None
    return obs


def plausible_sets(ARMD, w):
    s = set(ARMD[w]["R1_EXT"]) | set(ARMD[w]["n3"]) | set(ARMD[w]["sup2"])
    for k in ("E2", "E3"):
        s |= {tuple(x.split()) for x in ARMD[w]["sources"][k]}
    return s


def deviating_engines(w, canon, obs, plaus):
    o = dict(AR.OPTS["N4_ASRG2P"])
    nf = AR.nextfirst_of(canon, w)
    dev = []
    for k, v in obs.items():
        if v is None:
            continue
        lab, _ = AR.obs_label(w, v, plaus, nf, o)
        if lab in ("MISMATCH", "NEAR_VOWEL"):
            dev.append(k)
    return dev


def load_gen():
    out = {}
    for ph in ("take1", "take2", "neg"):
        p = R2 / f"gen_{ph}.json"
        if p.exists():
            out[ph] = json.load(open(p, encoding="utf-8"))
    return out


def main():
    est, S, A, ARMD = RPL.load_sets()
    plan = json.load(open(R2 / "plan.json", encoding="utf-8"))
    rows = load_rows()
    other_unres = {}
    for r in rows:
        c = r["canonical_text"]
        other_unres.setdefault(c, set()).update(set(unresolved_spans(r)) - set(TARGETS))
    gen = load_gen()
    res = {"headline": HEADLINE, "segments": [], "negatives": [], "arm_tables": {}}
    # ---- 現行TTS: segment/take別
    for ph in ("take1", "take2"):
        for it in gen.get(ph, []):
            if it.get("error") or it.get("primary") is None and it.get("azure") is None:
                res["segments"].append({"id": it["id"], "take": it["take"], "error": it.get("error", "ASRなし")})
                continue
            seg = next(s for s in plan["segments"] if s["id"] == it["id"])
            per_word = {}
            for w in it["words"]:
                obs = spans(it, w)
                dev = deviating_engines(w, it["canon"], obs, plausible_sets(ARMD, w))
                per_word[w] = {"deviating_engines": dev, "strings": {k: (" ".join(v) if v else None) for k, v in obs.items()}, "proxy_pass": AR.prod_pass_proxy(w, obs),
                               "verdicts": {a: AR.judge(w, it["canon"], obs, ARMD[w], a)["verdict"] for a in AR.ARMS},
                               "labels": {a: [(k, l, d) for k, l, d, _ in (lambda j: j["prod"] + j["wh"])(AR.judge(w, it["canon"], obs, ARMD[w], a))] for a in ("R1_EXT", HEADLINE)}}
            blocked = sorted(other_unres.get(it["canon"], set()))
            seg_proxy_pass = all(pw["proxy_pass"] for pw in per_word.values()) and not blocked
            sv = {}
            for a in AR.ARMS:
                vs = [pw["verdicts"][a] for pw in per_word.values()]
                sv[a] = "PASS_WITH_WARNING" if (all(v == "PASS_WITH_WARNING" for v in vs) and not blocked) else ("NG" if any(v == "NG" for v in vs) else "HR_MAINTAINED")
            n_dev = max(len(pw["deviating_engines"]) for pw in per_word.values())
            res["segments"].append({"id": it["id"], "take": it["take"], "likely_tts_misread": n_dev >= 2, "family": seg["family"], "words": it["words"], "hr_events_orig": seg["hr_events"], "sec": it.get("sec"), "api_scope": it.get("api_scope"),
                                    "other_unresolved_blocking": blocked, "current_prod_proxy": "PASS" if seg_proxy_pass else "HR", "per_word": per_word, "seg_verdict": sv, "wav": it["wav"], "text": it["canon"][:120]})
    # ---- 負例
    for it in gen.get("neg", []):
        if it.get("error"):
            res["negatives"].append({"id": it["id"], "error": it["error"]})
            continue
        w = it["word"]
        obs = spans(it, w)
        plaus = plausible_sets(ARMD, w)
        dev = deviating_engines(w, it["canon"], obs, plaus)
        primary_exact = bool(obs.get("primary") and len(obs["primary"]) == 1 and obs["primary"][0] == w)
        rec = {"id": it["id"], "word": w, "kind": it["kind"], "tts_text": it["tts_text"], "strings": {k: (" ".join(v) if v else None) for k, v in obs.items()}, "deviating_engines": dev,
               "misread_confirmed": len(dev) >= 2, "primary_exact": primary_exact, "wav": it["wav"], "verdicts": {a: AR.judge(w, it["canon"], obs, ARMD[w], a)["verdict"] for a in AR.ARMS}}
        res["negatives"].append(rec)
    # ---- 集計
    for take in ("t1", "t2", "all"):
        segs = [s for s in res["segments"] if "seg_verdict" in s and (take == "all" or s["take"] == take)]
        hr = [s for s in segs if s["current_prod_proxy"] == "HR"]
        t = {"n_audio": len(segs), "current_prod_proxy_HR": len(hr), "current_prod_proxy_PASS": len(segs) - len(hr), "arms": {}}
        for a in AR.ARMS:
            c = collections.Counter(s["seg_verdict"][a] for s in hr)
            t["arms"][a] = {"of_HR_PASS_WITH_WARNING": c["PASS_WITH_WARNING"], "of_HR_NG": c["NG"], "of_HR_maintained": c["HR_MAINTAINED"],
                            "pass_ids": sorted(s["id"] + "/" + s["take"] for s in hr if s["seg_verdict"][a] == "PASS_WITH_WARNING"),
                            "of_proxyPASS_changed_to_NG": sum(1 for s in segs if s["current_prod_proxy"] == "PASS" and s["seg_verdict"][a] == "NG")}
        t["of_HR_likely_tts_misread(>=2 engines deviate from every plausible reading)"] = sum(1 for s in hr if s["likely_tts_misread"])
        t["of_HR_not_misread_flagged"] = sum(1 for s in hr if not s["likely_tts_misread"])
        t["judgement_side_ceiling(<=1 engine deviates & no other unresolved span; 受理集合の有無は問わない上限)"] = sum(1 for s in hr if not s["likely_tts_misread"] and not s["other_unresolved_blocking"])
        res["arm_tables"][take] = t
    conf = [n for n in res["negatives"] if n.get("misread_confirmed")]
    unconf = [n for n in res["negatives"] if "misread_confirmed" in n and not n["misread_confirmed"]]
    res["negative_summary"] = {"n_generated": len([n for n in res["negatives"] if "misread_confirmed" in n]), "n_confirmed_misread": len(conf), "n_unconfirmed_excluded": len(unconf),
                               "false_pass_by_arm": {a: [n["id"] for n in conf if n["verdicts"][a] == "PASS_WITH_WARNING"] for a in AR.ARMS},
                               "false_pass_if_unconfirmed_included": {a: [n["id"] for n in unconf if n["verdicts"][a] == "PASS_WITH_WARNING"] for a in AR.ARMS},
                               "primary_exact_rate_confirmed": [sum(1 for n in conf if n["primary_exact"]), len(conf)],
                               "by_kind": {k: [sum(1 for n in conf if n["kind"] == k), sum(1 for n in res["negatives"] if n.get("kind") == k)] for k in ("C", "V", "S", "F", "C2", "F2")}}
    # ---- Khaite 'kite' 8事象のNG維持(保存データ)
    st = json.load(open(R2 / "replay_stored.json", encoding="utf-8"))
    kite = [h for h in st["hr_detail"] if h["word"] == "khaite" and h["verdicts"]["R1_EXT"] == "NG"]
    res["khaite_kite_events"] = {"n": len(kite), "still_NG_by_arm": {a: sum(1 for h in kite if h["verdicts"][a] == "NG") for a in AR.ARMS}}
    json.dump(res, open(R2 / "agg.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res["arm_tables"], ensure_ascii=False, indent=0)[:3500])
    print(json.dumps(res["negative_summary"], ensure_ascii=False, indent=0))
    print(json.dumps(res["khaite_kite_events"], ensure_ascii=False))


if __name__ == "__main__":
    main()
