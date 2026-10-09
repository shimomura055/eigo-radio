import json, hashlib, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(BASE, "stage_r", "FROZEN_INPUTS_SHA256.json")
d = json.load(open(P, encoding="utf-8"))
def lf_sha(p):
    b = open(p, "rb").read().replace(b"\r\n", b"\n").replace(b"\r", b"\n"); return hashlib.sha256(b).hexdigest()
for s in ("hormuz", "streaming_price"):
    t = d["themes"][s]; t["storyline_b3_v2"] = {}
    for f in ("selected_brief.md", "fact_selection_evidence.json", "full_ledger.json"):
        rel = f"er052_output/factlock_astra_e2e_trial_01/stage_r/{s}/storyline_b3_v2/{f}"
        t["storyline_b3_v2"][f] = {"path": rel, "sha256_lf": lf_sha(os.path.join(BASE, "stage_r", s, "storyline_b3_v2", f))}
    t["storyline_b3_v2"]["note"] = "委任_09で再生成(各1回)。v1(storyline_b3)は無改変で保存。ledgerはv1と同一(再生成は凍結台帳から)。"
    # 台帳不変の確認
    assert lf_sha(os.path.join(BASE, "stage_r", s, "research_ledger", "verified_fact_ledger.txt")) == t["ledger"]["sha256_lf"]
    assert lf_sha(os.path.join(BASE, "stage_r", s, "storyline_b3", "selected_brief.md")) == t["selected_brief.md"]["sha256_lf"]
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok")
