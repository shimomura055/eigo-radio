# 委任_10: 保存済みASR転写に対するM1(複数発音候補)の完全offline再判定。API 0 / TTS 0 / ASR 0 / LLM 0。
# 実行: .venv\Scripts\python.exe -I -X utf8 <this file>   (cwd=repo root)
import sys, json, copy, time, os
sys.path.insert(0, os.getcwd())
import er006_m1_multi_candidate_01 as m1
import er006_pronunciation_ledger_01 as led

CANON = ("He remembered the hands held out for the chains. His friend trusted him without asking for another promise. "
         "Water came slowly through a crack in the rock. Melos drank, got onto his knees, and stood up. He managed one step, "
         "then took another. At the city gates, the bell rang for his friend's death. He raced to the square, where the sword "
         "was already raised above his friend.")
def swap(a, b):
    assert a in BASE, a
    return BASE.replace(a, b)
BASE = ("He remembered the hands held out for the chains. His friend trusted him without asking for another promise. "
        "Water came slowly through a crack in the rock. Melos drank, got onto his knees, and stood up. He managed one step, "
        "then took another. At the city gates, the bell rang for his friend's death. He raced to the square where the sword "
        "was already raised above his friend.")
CASES = {
 "run04_att1_primary(Melo strained)": swap("Melos drank", "Melo strained"),
 "run04_att1_azure(Mellow Strength)": swap("Melos drank", "Mellow Strength"),
 "run04_att2_primary(Mello drank)": swap("Melos drank", "Mello drank"),
 "run04_att2_azure(Mellows drank)": swap("Melos drank", "Mellows drank"),
 "run04_att3_primary(Mello drank)": swap("Melos drank", "Mello drank"),
 "run04_att3_azure(Mellow strength)": swap("Melos drank", "Mellow strength"),
 "run03_primary(Mello drank)": swap("Melos drank", "Mello drank"),
 "run03_azure(Melos drank)": BASE,
}
snap = copy.deepcopy(led._load())
fz = m1.freeze_candidates(CANON, ledger_snapshot=snap, segment_started_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
fw = fz.word("melos")
out = {"candidate_set_hash": fz.candidate_set_hash,
       "melos_candidates": [{"pron": list(c.pron), "source": c.source, "confidence": c.confidence, "ledger_key": c.ledger_key,
                             "ipa_raw": c.ipa_raw} for c in fw.candidates] if fw else None,
       "melos_excluded": [json.loads(x) for x in fw.excluded] if fw else None,
       "melos_unconvertible": [json.loads(x) for x in fw.unconvertible] if fw else None,
       "cmu_melos": [list(v) for v in m1.default_cmu("melos")], "cases": {}}
for name, asr in CASES.items():
    r = m1.m1_multi_candidate_judge(CANON, asr, fz)
    a = dict(r.audit or {})
    out["cases"][name] = {"accepted": r.accepted, "reason": r.reason, "applicable": r.applicable,
                          "no_match_reason": getattr(r, "no_match_reason", None),
                          "no_match_reasons": a.get("no_match_reasons"), "f1_residual_kind": a.get("f1_residual_kind"),
                          "subs": [{k: s.get(k) for k in ("from", "to", "rule", "source", "confidence")} for s in (r.subs or [])]}
p = "docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/m1_offline_replay_part3c1_10_result.json"
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
