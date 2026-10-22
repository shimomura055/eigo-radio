# -*- coding: utf-8 -*-
"""O0(0円): 母数(独立音声/segment/延べlookup)・各行の語別ASR転写・音声保存有無。"""
import hashlib, json, os, sys
sys.path.insert(0, os.getcwd())
from er100_pnps_stage2_trial_01_common import *

rows = load_rows()
pop = []
for i, r in enumerate(rows):
    lk = r.get("pronunciation_lookups") or {}
    tg = [t for t in TARGETS if t in lk]
    if tg:
        pop.append((i, r, tg))
lookups = sum(len(tg) for _, _, tg in pop)
per_word = {t: sum(1 for _, _, tg in pop if t in tg) for t in TARGETS}
paths = {}
for i, r, tg in pop:
    paths.setdefault(r["wav_path"], []).append(i)
exist = {p: os.path.exists(p) for p in paths}
hashes = {}
for p, e in exist.items():
    if e:
        hashes[p] = hashlib.sha256(open(p, "rb").read()).hexdigest()
distinct_audio = len(set(hashes.values()))
table = []
for i, r, tg in pop:
    for t in tg:
        row = {"row": i, "ts": r["timestamp"], "word": t, "wav_path": r["wav_path"], "wav_exists": exist[r["wav_path"]],
               "final_status": r["final_status"], "all_unresolved_spans": unresolved_spans(r),
               "other_unresolved": [s for s in unresolved_spans(r) if s != t]}
        for k, (pre, n) in {"primary_1": ("primary", 0), "primary_2": ("primary", 1), "secondary_1": ("secondary", 0), "secondary_2": ("secondary", 1)}.items():
            row[k] = asr_span(r["canonical_text"], step_text(r, pre, n), t, ctx=0)
        row["classification"] = [s.get("classification") for s in r["steps"]]
        row["hint"] = (r["pronunciation_lookups"][t].get("pronunciation_hint"), r["pronunciation_lookups"][t].get("expected_pronunciation_ipa"), r["pronunciation_lookups"][t].get("confidence"))
        table.append(row)
summary = {
    "hr_queue_rows_total": len(rows), "population_rows_(segment-HR events)": len(pop),
    "population_lookups_(delta lookup count; row x word)": lookups, "per_word_lookups": per_word,
    "distinct_wav_paths": len(paths), "wav_paths_existing": sum(exist.values()), "wav_paths_missing": [p for p, e in exist.items() if not e],
    "distinct_audio_files_by_sha256_(existing)": distinct_audio,
    "rows_where_only_target_words_unresolved": sum(1 for _, r, tg in pop if set(unresolved_spans(r)) <= set(TARGETS)),
    "rows_with_other_unresolved": sum(1 for _, r, tg in pop if not set(unresolved_spans(r)) <= set(TARGETS)),
    "paths_multi_rows": {p: v for p, v in paths.items() if len(v) > 1},
}
json.dump({"summary": summary, "table": table}, open(f"{OUT}/o0_population.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
