# 委任_05: Melos含有clipごとに Melo(benign単複)/Mello(M1)の現行判定と文長依存を実測(read-only・API 0・Production無変更)
# 実行: .venv\Scripts\python.exe -X utf8 <this> --out <json>  (cwd=repo root)。P1は既にREJECTEDであり、ここでの p1_ok は「何が起きるか」の事実確認のみ(実装しない)。
import sys, os, json, argparse, re
sys.path.insert(0, os.getcwd())
import er021_en_asr_semantic_equivalence_production_01 as se
se.append_telemetry_log = lambda *a, **k: None
import er006_m1_multi_candidate_01 as m1
import er006_preprod_hardening_01_validation as val
import er006_pronunciation_ledger_01 as pl

ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
AUD = "er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2/audit/tts_generation_results.json"
d = json.load(open(AUD, encoding="utf8"))
found = {}
def walk(o):
    if isinstance(o, dict):
        t = o.get("canonical_text")
        if isinstance(t, str) and re.search(r"\bMelos\b", t):
            found[o.get("segment_id") or o.get("clip_id") or "?"] = t
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(d)
snap = pl._load()
rows = []
for k, t in sorted(found.items(), key=lambda x: len(x[1].split())):
    frozen = m1.freeze_candidates(t, ledger_snapshot=snap, segment_started_at="2026-10-19T12:00:00")
    toks = len(val.tokenize(t))
    row = {"segment": k, "tokens": toks, "text_head": t[:50]}
    for w in ("Melo", "Mello", "Mellow", "Mellows"):
        asr = t.replace("Melos", w)
        cls = val.classify_asr_match(t, asr)
        r = m1.m1_multi_candidate_judge(t, asr, frozen, base_cls=cls)
        row[w] = {"cls": cls.classification, "ratio": round(cls.normalized_ratio, 4), "pass_native": cls.should_pass,
                  "m1": r.accepted, "m1_reason": r.reason}
    rows.append(row)
json.dump(rows, open(a.out, "w", encoding="utf8"), ensure_ascii=False, indent=1)
for r in rows:
    print(r["tokens"], r["segment"], "Melo:", r["Melo"]["cls"], r["Melo"]["ratio"], "| Mello:", r["Mello"]["cls"], "m1", r["Mello"]["m1"], r["Mello"]["m1_reason"], "| Mellows m1", r["Mellows"]["m1_reason"])
