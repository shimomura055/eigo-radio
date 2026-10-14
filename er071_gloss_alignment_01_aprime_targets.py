# -*- coding: utf-8 -*-
"""KP-GLOSS-ALIGNMENT-PRODUCTION-01 OF-231(JPY0): 記録済みcanonicalization応答(案A'の窓で再判定してPASS/REVIEW_REQUIRED
になるもの)を、記録済み選定itemとmergeし、gloss再整合の対象(selectoin_alignment_targets)になるitemを集計する。
出力: er071_output/m2p0_n01_production_wiring_01/gloss_alignment_01/aprime_targets_01.json
usage: PYTHONUTF8=1 .venv/Scripts/python.exe er071_gloss_alignment_01_aprime_targets.py"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga

OUT = "er071_output/m2p0_n01_production_wiring_01/gloss_alignment_01/aprime_targets_01.json"
rows = []
n_attempt_valid = 0
n_items_total = 0
for meta in sorted(glob.glob("er0*_output/**/canonicalization_runtime_metadata.json", recursive=True)):
    meta = meta.replace("\\", "/")
    d = json.load(open(meta, encoding="utf-8"))
    base = os.path.dirname(meta)
    kfile = base + "/keywords_runtime_metadata.json"
    if not os.path.exists(kfile):
        continue
    k = json.load(open(kfile, encoding="utf-8"))
    items = None
    for key in ("kp_backend_attempts_detail", "attempts_detail"):
        try:
            items = k[key][-1 if key == "attempts_detail" else 0]["parsed"]["items"]
            break
        except Exception:
            items = None
    if items is None:
        continue
    for a in d.get("attempts_detail", []):
        if not a.get("parsed"):
            continue
        r = kc.validate_canonicalization_response(a["parsed"], items)
        if r["status"] not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            continue
        n_attempt_valid += 1
        try:
            merged = kc.merge_canonicalization_result(items, a["parsed"]["items"])
        except Exception as e:
            continue
        n_items_total += len(merged["items"])
        for t in ga.select_alignment_targets(merged["items"]):
            rows.append({"meta": meta, "attempt": a.get("attempt"), "rank": t["rank"], "display": t.get("display_phrase"),
                         "kp": t["key_phrase"], "gloss": t.get("japanese_gloss"), "source_sentence": t.get("source_sentence"),
                         "beyond_flag": t.get("kp_extends_beyond_candidate")})
uniq = {}
for r in rows:
    uniq.setdefault((r["display"], r["kp"], r["gloss"]), r)
att_with = {(r["meta"], r["attempt"]) for r in rows}
res = {"attempts_with_target": len(att_with), "records_with_target": len({r["meta"] for r in rows}),
       "valid_replayed_attempts": n_attempt_valid, "items_total": n_items_total, "target_rows": len(rows),
       "unique_targets": list(uniq.values())}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("attempts_with_target", len(att_with), "records_with_target", len({r["meta"] for r in rows}), "valid attempts", n_attempt_valid, "items", n_items_total, "target rows", len(rows), "unique", len(uniq))
for v in uniq.values():
    print(v["display"], "->", v["kp"], "|", v["gloss"])
