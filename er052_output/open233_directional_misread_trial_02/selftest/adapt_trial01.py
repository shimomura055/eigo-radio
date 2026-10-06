"""selftest用: TRIAL-01 results_same_blind.jsonl -> TRIAL-02入力契約。truthは最小ダミー(TRIAL-01のfact_registryから生成)。"""
import json
import os

H = os.path.dirname(os.path.abspath(__file__))
T1 = os.path.join(H, "..", "..", "open233_directional_misread_trial_01")
rows = [json.loads(x) for x in open(os.path.join(T1, "run_same_blind", "results_same_blind.jsonl"), encoding="utf-8")]
reg = json.load(open(os.path.join(T1, "testset_01.json"), encoding="utf-8"))["fact_registry"]
out, cache, truth, seen = [], {}, {}, set()
for r in rows:
    reps = []
    for i, c in enumerate(r["repeat_compares"]):
        evs = r["repeat_events"][i] if i < len(r["repeat_events"]) else []
        e0 = evs[0] if evs else {}
        reps.append({"rep": i, "ledger_events_subjects": [e["subject_x"] for e in evs], "selected_subject": e0.get("subject_x"),
                     "ledger_state": e0.get("ledger_state"), "article_state": e0.get("article_state"), "compare": c,
                     "ledger_quote": "", "article_quote": e0.get("article_quote", "")})
    out.append({"id": r["id"], "fact_id": r["fact_id"], "label": r["label"], "origin": r["role"],
                "expected_compare": r["expected"]["expected_compare"], "acceptable_compare": r["expected"].get("acceptable_compare"),
                "expected_article_state": r["expected"].get("expected_article_state"), "repeats": reps,
                "final_compare_rep0": r["compare"], "final_compares": r["repeat_compares"], "cost_jpy": r["cost_jpy"]})
    fid = r["fact_id"]
    if fid in seen:
        continue
    seen.add(fid)
    subj0 = [e["subject_x"] for e in (r["repeat_events"][0] if r["repeat_events"] else [])]
    cache[fid] = {f"rep{k + 1}": [{"subject_x": (subj0[j] if j < len(subj0) else ""), "result_state": s, "quote": ""}
                                  for j, s in enumerate(st)] for k, st in enumerate(r["ledger"]["repeat_states"])}
    g = reg.get(fid, {})
    hd = bool(g.get("has_direction"))
    truth[fid] = {"has_direction": hd, "events": ([{"event_key": subj0[0], "aliases": [], "result_state": g.get("expected_ledger_state"),
                                                    "acceptable_states": g.get("acceptable_ledger_states"), "quote": ""}] if hd and subj0 else [])}
w = lambda n, o: json.dump(o, open(os.path.join(H, n), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(os.path.join(H, "results_adapted.jsonl"), "w", encoding="utf-8").write("\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n")
w("ledger_cache_adapted.json", cache)
w("ledger_truth_dummy.json", truth)
print("adapted", len(out), "items;", len(cache), "facts (truth=DUMMY from fact_registry)")
