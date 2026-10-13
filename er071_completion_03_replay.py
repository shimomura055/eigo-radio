# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_03 offline dry-run(API 0円)。
記録済みCANONICALIZATION_INVALID LLM出力を案A'修正後validatorへ再投入。"""
import glob, json, os
import er003_key_words_canonicalization as kc

OUT = "er071_output/m2p0_n01_production_wiring_01/completion_03/replay_A_prime_03.json"
rows = []
for meta in sorted(glob.glob("er0*_output/**/canonicalization_runtime_metadata.json", recursive=True)):
    d = json.load(open(meta, encoding="utf-8"))
    if not any(a.get("status") == "CANONICALIZATION_INVALID" for a in d.get("attempts_detail", [])) and d.get("final_status") != "CANONICALIZATION_INVALID":
        continue
    base = os.path.dirname(meta)
    items = None
    for cand in (base + "/keywords_runtime_metadata.json",):
        if os.path.exists(cand):
            k = json.load(open(cand, encoding="utf-8"))
            for key in ("kp_backend_attempts_detail", "attempts_detail"):
                try:
                    items = k[key][-1 if key == "attempts_detail" else 0]["parsed"]["items"]
                    break
                except Exception:
                    items = None
    row = {"meta": meta, "selection_items_found": items is not None, "attempts": []}
    for a in d.get("attempts_detail", []):
        rec = {"attempt": a.get("attempt"), "recorded_status": a.get("status"), "recorded_reasons": a.get("item_reasons")}
        if items is not None and a.get("parsed"):
            r = kc.validate_canonicalization_response(a["parsed"], items)
            rec["replayed_status"] = r["status"]
            rec["replayed_reasons"] = r["item_reasons"]
            rec["windows"] = [{"rank": v["rank"], "orig": v.get("source_span_original"), "window": v["source_span"]}
                              for v in kc.canonicalization_view_items(items) if "source_span_original" in v]
        row["attempts"].append(rec)
    rows.append(row)
json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = 0
for r in rows:
    for a in r["attempts"]:
        tot += 1
        print(r["meta"].replace("er019_output/family_x_audio_production_wiring_01/", "").replace("er026_output/family_z_production_e2e_01/", "")[:70], a["attempt"], a["recorded_status"], "->", a.get("replayed_status"))
print("attempts", tot)
