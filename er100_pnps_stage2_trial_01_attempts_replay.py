# -*- coding: utf-8 -*-
"""保存attempt音声(ER-011保持。各attemptは独立したTTS生成)に対する新方式replay。0円。
母数=独立音声(sha256別)。各attemptの保存ASR(Primary + cascade secondary)とローカルWhisperを観測として使う。"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from er100_pnps_stage2_trial_01_common import *
import er100_pnps_stage2_trial_01_replay as RP

pop = json.load(open(f"{OUT}/o0_population.json", encoding="utf-8"))
est = json.load(open(f"{OUT}/est_e2_e3.json", encoding="utf-8"))
r0 = json.load(open(f"{OUT}/r0_extractions.json", encoding="utf-8"))
items = json.load(open(f"{OUT}/o0_attempts_meta.json", encoding="utf-8"))
wh = json.load(open(f"{OUT}/o0_attempts_whisper.json", encoding="utf-8"))
S = RP.build_sets(est, r0)
A = {w: RP.accepted(w, S[w]) for w in TARGETS}
out = []
for it in items:
    for w in it["words"]:
        ct = it["canonical_text"]
        obs = {"primary": asr_span(ct, it["asr_text"], w)}
        for st in (it.get("cascade_steps") or []):
            if str(st.get("step", "")).startswith("secondary"):
                obs["secondary_" + st["step"]] = asr_span(ct, st.get("text"), w)
        for sz in ("small", "medium"):
            if sz in wh.get(it["wav"], {}):
                obs["whisper_" + sz] = asr_span(ct, wh[it["wav"]][sz], w)
        res = {}
        for arm in ("V4", "EXT", "DIAG_UNION"):
            accset = A[w][arm]
            ob = [(k, *RP.obs_verdict(w, v, accset)) for k, v in obs.items() if v is not None]
            prod = [l for k, l, _ in ob if not k.startswith("whisper")]
            allx = [l for k, l, _ in ob]
            def dec(labs):
                if not accset:
                    return "HR_MAINTAINED(推定不成立)"
                if labs and all(l in ("MATCH", "EXACT") for l in labs) and "MATCH" in labs:
                    return "PASS_WITH_WARNING"
                if "MISMATCH" in labs and "OOV" not in labs:
                    return "NG"
                return "HR_MAINTAINED(判定不能)"
            res[arm] = {"prod_only": dec(prod), "prod_plus_whisper": dec(allx), "obs": ob}
        out.append({"wav": it["wav"], "sha256": it["sha256"], "word": w, "model": it["model"], "verified_in_production": it["verified"], "classification": it["classification"], "res": res,
                    "strings": {k: (" ".join(v) if v is not None else None) for k, v in obs.items()}})
json.dump(out, open(f"{OUT}/attempts_replay_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import collections
for arm in ("V4", "EXT", "DIAG_UNION"):
    for mode in ("prod_only", "prod_plus_whisper"):
        c = collections.Counter(o["res"][arm][mode] for o in out if not o["verified_in_production"])
        print(arm, mode, dict(c))
print("attempt-word pairs", len(out), "distinct audio", len({o['sha256'] for o in out}), "non-verified audio", len({o['sha256'] for o in out if not o['verified_in_production']}))
for o in out:
    if o["res"]["EXT"]["prod_only"] == "PASS_WITH_WARNING" or o["res"]["DIAG_UNION"]["prod_only"] == "PASS_WITH_WARNING":
        print("PASS", o["word"], o["wav"][-70:], o["verified_in_production"], o["strings"])
