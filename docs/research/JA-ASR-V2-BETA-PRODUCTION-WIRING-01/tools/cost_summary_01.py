# -*- coding: utf-8 -*-
# JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: runtime evidence(E1/E1b/E1c/E2/E3)の費用集計(証跡JSON+raw usage logから。API 0)。
import glob, json, os, sys, wave
D = "docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01"
OPENAI_JPY_PER_SEC = 0.045 / 6.0


def dur(p):
    with wave.open(p) as w:
        return w.getnframes() / float(w.getframerate())


tot = {"azure_audit": 0.0, "openai_asr_est": 0.0}
rows = []
for ph in ("e1", "e1b", "e1c", "e2", "e3"):
    d = json.load(open(f"{D}/runtime_evidence_{ph}_01.out.json", encoding="utf-8"))
    items = d.get("rows") or [d[k]["summary"] for k in "XYZ" if k in d]
    az = sum(r["audit_cost_est_jpy_sum"] for r in items)
    rs_mismatch = [r["label"] for r in items if r.get("run_state") and abs(r["run_state"]["est_jpy_total"] - r["audit_cost_est_jpy_sum"]) > 1e-9]
    oa = 0.0
    for r in items:
        if r.get("wav") and os.path.exists(r["wav"]):
            oa += dur(r["wav"]) * OPENAI_JPY_PER_SEC * (r.get("attempts") or 1)
    raw = [json.loads(l) for l in open(f"{D}/raw_usage_log_runtime_evidence_{ph}_01.jsonl", encoding="utf-8")]
    n = {}
    for x in raw:
        n[x["model_id"]] = n.get(x["model_id"], 0) + 1
    rows.append((ph, round(az, 4), round(oa, 4), n, rs_mismatch))
    tot["azure_audit"] += az
    tot["openai_asr_est"] += oa
for r in rows:
    print(r)
print({k: round(v, 4) for k, v in tot.items()}, "sum", round(sum(tot.values()), 4))
