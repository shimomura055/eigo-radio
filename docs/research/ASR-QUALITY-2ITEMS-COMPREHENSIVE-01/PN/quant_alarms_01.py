# -*- coding: utf-8 -*-
"""PNAP配線(2026-10-22)以降のX/Z run: tts_generation_results.json内のPASS_WITH_PRONUNCIATION_ALARM record(証拠ラベル・名詞)と
STOPPED(status!=OK)segmentのASR差を集計する。read-only/API 0。"""
import json, glob, os, sys, collections, time
sys.path.insert(0, ".")
import er103_proper_noun_alarm_policy_01 as pol
import er006_preprod_hardening_01_validation as val
CUT = time.mktime(time.strptime("2026-10-22 12:00", "%Y-%m-%d %H:%M"))
files = [f for f in glob.glob("er0*_output/**/tts_generation_results.json", recursive=True) if os.path.getmtime(f) >= CUT]
alarms, stopped = [], []
for f in files:
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    for rec in pol.derive_run_alarms(d):
        alarms.append({"file": f.replace("\\", "/"), "noun": rec["proper_noun"], "evidence": rec["mismatch"]["proper_noun_evidence"],
                       "asr_p": rec["mismatch"]["asr_primary"], "asr_s": rec["mismatch"]["asr_secondary"],
                       "sim_p": rec["mismatch"]["similarity_primary"], "family": rec.get("family"), "seg": rec.get("segment_id"), "inh": rec.get("inherited")})
    def walk(x, p):
        if isinstance(x, dict):
            if x.get("status") not in (None, "OK") and (x.get("attempts") or x.get("attempts_log")):
                at = (x.get("attempts") or x.get("attempts_log"))
                stopped.append({"file": f.replace("\\", "/"), "path": p, "status": x.get("status"), "canon": (x.get("canonical_text") or "")[:100],
                                "last_cls": (at[-1] or {}).get("audio_classification") if isinstance(at[-1], dict) else None,
                                "last_asr": ((at[-1] or {}).get("asr_text") or "")[:100] if isinstance(at[-1], dict) else None})
            for k, v in x.items():
                if k in ("attempts", "attempts_log", "asr_judgement", "asr_judgement_inherited"): continue
                if isinstance(v, (dict, list)): walk(v, p + "/" + str(k))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                if isinstance(v, (dict, list)): walk(v, p + "/" + str(i))
    walk(d, "")
print("files", len(files), "alarms", len(alarms), "stopped", len(stopped))
print("evidence", collections.Counter(a["evidence"] for a in alarms).most_common())
by = collections.defaultdict(list)
for a in alarms: by[a["noun"]].append(a)
for n, v in sorted(by.items()):
    print(n, len(v), collections.Counter(a["evidence"] for a in v).most_common(2), "|", v[0]["asr_p"], "|", v[0]["file"].split("/")[1:4])
print("--- STOPPED")
for s in stopped: print(s["file"].split("/")[1:5], s["path"], s["status"], s["last_cls"], "|", s["canon"], "=>", s["last_asr"])
json.dump({"alarms": alarms, "stopped": stopped}, open("docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/quant_alarms_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
