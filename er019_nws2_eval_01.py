# -*- coding: utf-8 -*-
"""FAMILY-X-NEWS-2ARTICLES-E2E-02: 記事別evidence集計(read-only、API 0)。試聴ページ/Production経路外。"""
import json, sys, glob, os, collections
def rj(p): return json.load(open(p, encoding="utf-8"))
def main(slug, run="run_nws_02", out=None):
    R = f"er019_output/{slug}/{run}"; AO = f"er019_output/family_x_audio_production_wiring_01/{slug}__{run}"
    o = {"slug": slug, "run": run}
    o["ledger"] = rj(R + "/research_ledger/verdict_counts.json")
    o["b3_selected"] = rj(R + "/storyline_b3/fact_selection_evidence.json")["selected_fact_ids"]
    for k in ("cost.json",):
        if os.path.exists(f"{R}/{k}"): o["text_cost_jpy"] = rj(f"{R}/{k}")["by_stage_jpy"]; o["text_total_jpy"] = rj(f"{R}/{k}")["total_jpy"]
    o["levels"] = {}
    for l in ("a2", "b1b"):
        r = rj(f"{AO}/{l}/audit/tts_generation_results.json")
        segs = r["segments"]
        L = {"seg_status": dict(collections.Counter(v.get("status") for v in segs.values())),
             "retry_total": sum((v.get("retry_count") or 0) for v in segs.values()),
             "fallback_used": [k for k, v in segs.items() if v.get("fallback_used")],
             "asr_judgement": {k: ((v.get("asr_judgement") or {}).get("state"), (v.get("asr_judgement") or {}).get("reason_code")) for k, v in segs.items()}}
        kp = rj(f"{AO}/{l}/key_phrases/keywords_canonicalized.json")["items"]
        L["kp"] = [(i["rank"], i["key_phrase"], i["japanese_gloss"]) for i in sorted(kp, key=lambda x: x["rank"])]
        votes = []
        for n, v in r["key_phrases"].items():
            e = v.get("english") or {}
            votes.append({"kp": n, "status": e.get("status"), "vote": e.get("kp_vote") or e.get("kp_asr_vote"), "src": [k for k in e if "vote" in k.lower()]})
        L["kp_votes"] = votes
        L["kp_audio_status"] = {n: {k: (v.get(k) or {}).get("status") for k in ("english", "japanese")} for n, v in r["key_phrases"].items()}
        for nm in ("pronunciation_alarms", "pass_with_warning_listening_list", "style_profile_gate", "key_phrase_source_gate", "headroom_report"):
            p = f"{AO}/{l}/audit/{nm}.json"
            if os.path.exists(p):
                d = rj(p)
                L[nm] = {"count": d.get("count"), "entries": [e.get("entry_key") or e.get("segment_id") for e in d.get("entries", [])] if isinstance(d.get("entries"), list) else None, "status": d.get("status") or d.get("overall") or d.get("result")} if nm in ("pronunciation_alarms", "pass_with_warning_listening_list") else {k: d.get(k) for k in list(d)[:8]}
        lk = rj(f"{AO}/{l}/audit/review_lock_state.json")
        L["locks"] = dict(collections.Counter((x.get("state") or x.get("status")) for x in (lk.get("locks", lk) if isinstance(lk, dict) else lk).values())) if isinstance(lk.get("locks", lk), dict) else str(type(lk))
        tl = rj(f"{AO}/{l}/audit/timeline.json"); L["duration_s"] = round(tl[-1]["start_seconds"] + tl[-1]["duration_seconds"], 2)
        o["levels"][l] = L
    cost = collections.defaultdict(float)
    for line in open(AO + "/raw_usage_log.jsonl", encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        cost[str(d.get("stage") or d.get("process_label") or "?") + "|" + str(d.get("model_id") or d.get("model") or d.get("provider"))] += float(d.get("cost_jpy") or 0)
    o["audio_cost_by_stage_model_jpy"] = {k: round(v, 3) for k, v in sorted(cost.items())}
    o["audio_cost_total_jpy"] = round(sum(cost.values()), 3)
    s = json.dumps(o, ensure_ascii=False, indent=1)
    if out: open(out, "w", encoding="utf-8", newline="\n").write(s)
    print(s)
if __name__ == "__main__": main(*sys.argv[1:])
