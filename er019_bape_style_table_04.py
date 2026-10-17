# -*- coding: utf-8 -*-
"""FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 委任_04: 全segment Style適用表(有料APIなし、read-only)。Coffee e2e_segment_style_table.json と同形式。
expected_base_sha256 == style_base_sha256 を exp_match として全行記録。"""
import json, os, sys
RUN = "er019_output/family_x_audio_production_wiring_01/boredom_aggression__run_bape_01"
rows = []
def rj(p): return json.load(open(p, encoding="utf-8"))
def row(level, seg, d, sub=None):
    sp = d.get("style_profile") or {}
    aj = d.get("asr_judgement") or {}
    al = d.get("attempts_log") or []
    warns = list(d.get("warnings") or []) + list((aj.get("warning_labels") or []) if isinstance(aj, dict) else [])
    rows.append({"level": level, "segment": seg, "role": sp.get("role"), "profile": sp.get("profile_id"), "base_sha12": (sp.get("style_base_sha256") or "")[:12],
                 "expected_sha12": (sp.get("expected_base_sha256") or "")[:12],
                 "exp_match": (sp.get("expected_base_sha256") == sp.get("style_base_sha256")) if sp else None,
                 "instruction_type": d.get("instruction_type") or (al[0].get("instruction_type") if al else None),
                 "fallback_used": d.get("fallback_used"), "reused": d.get("reused"), "status": d.get("status"),
                 "retry": d.get("retry_count", max(0, len(al) - 1)), "asr_state": aj.get("state") if isinstance(aj, dict) else None,
                 "warnings": warns, "model": d.get("model"),
                 "slowdown": {k: d[k] for k in d if "slow" in k.lower()} or None})
for level in ("b1b", "a2"):
    p = f"{RUN}/{level}/audit/tts_generation_results.json"
    if not os.path.exists(p): continue
    r = rj(p)
    for seg, d in r["segments"].items(): row(level, seg, d)
    for n, k in sorted(r["key_phrases"].items()):
        for part, d in k.items():
            if isinstance(d, dict): row(level, f"kp{n}_{part}", d)
out = {"rows": rows, "n": len(rows), "all_styled_exp_match": all(x["exp_match"] for x in rows if x["role"]),
       "styled_rows": sum(1 for x in rows if x["role"]), "k2_fallback_count": sum(1 for x in rows if x["role"] == "KP_EN" and x["fallback_used"]),
       "s3_support_ja_segments": sum(1 for x in rows if x["role"] == "SUPPORT_JA")}
json.dump(rows, open(f"{RUN}/audit/e2e_segment_style_table_bape_04.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False))
