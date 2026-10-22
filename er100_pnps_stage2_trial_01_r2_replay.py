# -*- coding: utf-8 -*-
"""第2巡 保存データ(旧TTS世代)へのreplay(0円)。HR事象33行/保存attempt 86音声(95語ペア)/第1巡P2 23本へ、R1_V4/R1_EXT/N1..N6を適用。
新規生成音声(現行TTS)は r2_agg.py。"""
import collections, json, os, sys
sys.path.insert(0, os.getcwd())
from pathlib import Path
from er100_pnps_stage2_trial_01_common import *
import er100_pnps_stage2_trial_01_replay as RP
import er100_pnps_stage2_trial_01_r2_arms as AR

R2 = Path(OUT) / "r2"


def load_sets():
    est = json.load(open(f"{OUT}/est_e2_e3.json", encoding="utf-8"))
    r0 = json.load(open(f"{OUT}/r0_extractions.json", encoding="utf-8"))
    nb = json.load(open(R2 / "est_nbest.json", encoding="utf-8"))
    S = RP.build_sets(est, r0)
    A = {w: RP.accepted(w, S[w]) for w in TARGETS}
    ARM = {w: AR.build_arm_sets(w, S[w], A[w], nb) for w in TARGETS}
    return est, S, A, ARM


def stored_hr(ARM):
    rows = load_rows()
    rep = json.load(open(f"{OUT}/replay_result.json", encoding="utf-8"))
    detail = rep["detail"]
    out = []
    for d in detail:
        w, ct = d["word"], rows[d["row"]]["canonical_text"]
        obs = d["observations"]
        item = {"row": d["row"], "word": w, "ts": d["ts"], "canon": ct[:80], "strings": {k: (" ".join(v) if v else None) for k, v in obs.items()}, "verdicts": {}, "labels": {}}
        for arm in AR.ARMS:
            j = AR.judge(w, ct, obs, ARM[w], arm)
            item["verdicts"][arm] = j["verdict"]
            item["labels"][arm] = [(k, l, det) for k, l, det, _ in j["prod"] + j["wh"]]
        out.append(item)
    # 事象(行)単位の集計(R1と同じ規則: 行内の全語がPASS、他の未解決spanが無い)
    by_row = collections.defaultdict(list)
    for it in out:
        by_row[it["row"]].append(it)
    summ = {}
    for arm in AR.ARMS:
        p, n, h = [], [], []
        for r, its in by_row.items():
            unresolved = set(unresolved_spans(rows[r]))
            mine = {i["word"]: i["verdicts"][arm] for i in its}
            if not (unresolved - set(mine)) and all(v == "PASS_WITH_WARNING" for v in mine.values()):
                p.append(r)
            elif any(v == "NG" for v in mine.values()):
                n.append(r)
            else:
                h.append(r)
        summ[arm] = {"events": len(by_row), "PASS_WITH_WARNING": len(p), "NG": len(n), "HR_maintained": len(h), "pass_rows": p}
    return out, summ


def tokens_for(ct, text, w):
    return asr_span(ct, text, w)


def stored_attempts(ARM):
    items = json.load(open(f"{OUT}/o0_attempts_meta.json", encoding="utf-8"))
    wh = json.load(open(f"{OUT}/o0_attempts_whisper.json", encoding="utf-8"))
    out = []
    for it in items:
        for w in it["words"]:
            ct = it["canonical_text"]
            obs = {"primary": tokens_for(ct, it["asr_text"], w)}
            for st in (it.get("cascade_steps") or []):
                if str(st.get("step", "")).startswith("secondary"):
                    obs["secondary_" + st["step"]] = tokens_for(ct, st.get("text"), w)
            for sz in ("small", "medium"):
                if sz in wh.get(it["wav"], {}):
                    obs["whisper_" + sz] = tokens_for(ct, wh[it["wav"]][sz], w)
            rec = {"wav": it["wav"], "sha256": it["sha256"], "word": w, "model": it["model"], "verified_in_production": it["verified"],
                   "strings": {k: (" ".join(v) if v else None) for k, v in obs.items()}, "verdicts": {}, "prod_pass_proxy": AR.prod_pass_proxy(w, obs)}
            for arm in AR.ARMS:
                rec["verdicts"][arm] = AR.judge(w, ct, obs, ARM[w], arm)["verdict"]
            out.append(rec)
    return out


def stored_p2(ARM):
    items = json.load(open(f"{OUT}/p2_results.json", encoding="utf-8"))
    out = []
    for it in items:
        w, ct = it["word"], it["canon"]
        obs = {}
        for k, txt in it["asr"].items():
            obs[k] = tokens_for(ct, txt, w)
        rec = {"set": it["set"], "tag": it["tag"], "word": w, "wav": it["wav"], "strings": {k: (" ".join(v) if v else None) for k, v in obs.items()}, "verdicts": {}, "prod_pass_proxy": AR.prod_pass_proxy(w, obs)}
        for arm in AR.ARMS:
            rec["verdicts"][arm] = AR.judge(w, ct, obs, ARM[w], arm)["verdict"]
        out.append(rec)
    return out


def tally(rows, key="verdicts"):
    t = {}
    for arm in AR.ARMS:
        c = collections.Counter()
        for r in rows:
            v = r[key][arm]
            c["PASS_WITH_WARNING" if v == "PASS_WITH_WARNING" else "NG" if v == "NG" else "HR_MAINTAINED"] += 1
        t[arm] = dict(c)
    return t


def main():
    est, S, A, ARM = load_sets()
    hr, hr_summ = stored_hr(ARM)
    att = stored_attempts(ARM)
    p2 = stored_p2(ARM)
    non_v = [a for a in att if not a["verified_in_production"]]
    out = {"armsets": {w: {"R1_V4": sorted(" ".join(a) for a in ARM[w]["R1_V4"]), "R1_EXT": sorted(" ".join(a) for a in ARM[w]["R1_EXT"]), "n3_accepted": sorted(" ".join(a) for a in ARM[w]["n3"]),
                           "sup2": sorted(" ".join(a) for a in ARM[w]["sup2"]), "sources": ARM[w]["sources"]} for w in TARGETS},
           "stored_hr_events": hr_summ, "stored_hr_word_tally": tally(hr),
           "stored_attempts_nonproduction_pass_tally": tally(non_v), "stored_attempts_all_tally": tally(att),
           "p2_natural_tally": tally([r for r in p2 if r["set"] == "a_natural"]), "p2_controlled_tally": tally([r for r in p2 if r["set"] == "b_controlled"]),
           "p2_controlled_wrong_only_tally": tally([r for r in p2 if r["set"] == "b_controlled" and r["tag"].startswith("wrong")]),
           "p2_controlled_reasonable_only_tally": tally([r for r in p2 if r["set"] == "b_controlled" and r["tag"] == "reasonable"]),
           "hr_detail": hr, "attempts_detail": att, "p2_detail": p2}
    json.dump(out, open(R2 / "replay_stored.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ARMSETS"); [print(w, out["armsets"][w]["n3_accepted"], "| sup2", out["armsets"][w]["sup2"]) for w in TARGETS]
    print("HR events (33 words rows -> 58 events)"); print(json.dumps(hr_summ, ensure_ascii=False))
    print("word tally HR"); print(json.dumps(out["stored_hr_word_tally"]))
    print("attempts non-prod-verified tally"); print(json.dumps(out["stored_attempts_nonproduction_pass_tally"]))
    print("p2 natural"); print(json.dumps(out["p2_natural_tally"]))
    print("p2 controlled(neg)"); print(json.dumps(out["p2_controlled_tally"]))
    print("p2 wrong only"); print(json.dumps(out["p2_controlled_wrong_only_tally"]))


if __name__ == "__main__":
    main()
