# -*- coding: utf-8 -*-
"""Step A 集計(0円): 母数3区分・語別の取得/推定/判定内訳・原因分類の根拠データを出力する。"""
import collections, hashlib, json, os, sys
sys.path.insert(0, os.getcwd())
from er100_pnps_stage2_trial_01_common import *

rep = json.load(open(f"{OUT}/replay_result.json", encoding="utf-8"))
pop = json.load(open(f"{OUT}/o0_population.json", encoding="utf-8"))
rows = load_rows()
res = {}
det = rep["detail"]
ev_rows = sorted({d["row"] for d in det})
seg = {hashlib.sha1(rows[r]["canonical_text"].encode()).hexdigest() for r in ev_rows}
res["population"] = {
    "HR_queue_rows_total": len(rows),
    "HR_events_with_target_lookup(rows)": len(ev_rows),
    "lookups(row x word)": len(det),
    "distinct_canonical_segments": len(seg),
    "distinct_(word,segment)": len({(d["word"], hashlib.sha1(rows[d["row"]]["canonical_text"].encode()).hexdigest()) for d in det}),
    "distinct_wav_paths": len({d["wav_path"] for d in det}),
    "wav_paths_existing": len({d["wav_path"] for d in det if d["wav_exists"]}),
    "wav_paths_missing_(Temp)": len({d["wav_path"] for d in det if not d["wav_exists"]}),
    "HR_events_with_audio_path_existing": len({d["row"] for d in det if d["wav_exists"]}),
    "HR_events_without_audio": len({d["row"] for d in det if not d["wav_exists"]}),
    "rows_with_other_unresolved_span": sum(1 for r in ev_rows if set(unresolved_spans(rows[r])) - set(TARGETS)),
}
if os.path.exists(f"{OUT}/attempts_replay_result.json"):
    att = json.load(open(f"{OUT}/attempts_replay_result.json", encoding="utf-8"))
    res["attempt_audio"] = {"attempt_wav_distinct_sha256": len({a["sha256"] for a in att}), "attempt_word_pairs": len(att),
                            "by_model": dict(collections.Counter({a["sha256"]: a["model"] for a in att}.values())),
                            "production_verified_true": len({a["sha256"] for a in att if a["verified_in_production"]})}
per = {}
for w in TARGETS:
    ds = [d for d in det if d["word"] == w]
    per[w] = {"HR_events": len(ds), "audio_existing_events": sum(d["wav_exists"] for d in ds),
              "V4": dict(collections.Counter(d["res"]["V4"]["verdict"].split("(")[0] for d in ds)),
              "EXT": dict(collections.Counter(d["res"]["EXT"]["verdict"].split("(")[0] for d in ds)),
              "HR_reason_EXT": dict(collections.Counter(d["res"]["EXT"]["verdict"] for d in ds)),
              "distinguish_candidates": dict(collections.Counter(d["distinguish"].split("。")[0] for d in ds)),
              "asr_strings_primary1": dict(collections.Counter(" ".join(d["observations"]["primary_1"]) if d["observations"]["primary_1"] is not None else None for d in ds))}
res["per_word"] = per
json.dump(res, open(f"{OUT}/stepA_aggregates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))

# ---- 観測の判定可能性(ASR spanがCMU収録語か/正しい綴りそのものか/OOVか)。判定の天井を測る。
import er100_pnps_stage2_trial_01_replay as RP
import itertools
def classify_span(w, sp):
    if sp is None:
        return "未観測/整列不能"
    if len(sp) == 1 and sp[0] == w:
        return "正しい綴りそのまま(EXACT)"
    if RP.tok_variants(sp) is None:
        return "CMU未収録語(OOV)=比較不能"
    return "CMU収録語(比較可能)"
cnt = {w: collections.Counter() for w in TARGETS}
for d in det:
    for k, sp in d["observations"].items():
        if k.startswith("whisperREF"):
            continue
        cnt[d["word"]][classify_span(d["word"], sp)] += 1
if os.path.exists(f"{OUT}/attempts_replay_result.json"):
    pass
p2 = json.load(open(f"{OUT}/p2_results.json", encoding="utf-8"))
cnt_p2 = {w: collections.Counter() for w in TARGETS}
for x in p2:
    if x["set"] != "a_natural":
        continue
    for k, txt in x["asr"].items():
        cnt_p2[x["word"]][classify_span(x["word"], asr_span(x["canon"], txt, x["word"]))] += 1
res["decidability_stored_events"] = {w: dict(c) for w, c in cnt.items()}
res["decidability_p2_natural"] = {w: dict(c) for w, c in cnt_p2.items()}
tot = collections.Counter()
for c in cnt.values():
    tot.update(c)
res["decidability_stored_total"] = dict(tot)
tot2 = collections.Counter()
for c in cnt_p2.values():
    tot2.update(c)
res["decidability_p2_total"] = dict(tot2)
json.dump(res, open(f"{OUT}/stepA_aggregates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DECIDABILITY", json.dumps({"stored": res["decidability_stored_total"], "p2": res["decidability_p2_total"], "stored_by_word": res["decidability_stored_events"], "p2_by_word": res["decidability_p2_natural"]}, ensure_ascii=False, indent=1))
