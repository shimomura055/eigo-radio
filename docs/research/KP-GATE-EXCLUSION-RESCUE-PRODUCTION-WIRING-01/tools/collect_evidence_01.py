# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02: X/Y/Z fresh run(KP stage限定)とreplayの証拠を evidence_01.json に集計する(読取りのみ・API 0)。
実行: .venv\\Scripts\\python.exe docs\\research\\KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01\\tools\\collect_evidence_01.py <replay_runs_root> <out.json>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er105_kp_fulltext_selector_01 as ft          # noqa: E402
import er119_kp_human_review_01 as rv               # noqa: E402
import er119_kp_prompt_2v_01 as p2v                 # noqa: E402
import er125_kp_rescue_production_01 as r125        # noqa: E402

FAMILIES = {
    "X": dict(out="er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_kprescue_ev_01", cand="{out}/{lv}/key_phrases/kp_candidates.json",
              cost="{out}/raw_usage_log.jsonl", work="{out}/{lv}/key_phrases/kp_candidates/round_1/work", article="uk_train_speaker_playback"),
    "Y": dict(out="er121_output/family_y_production_01/redelivery_fee/run_kprescue_ev_01", cand="{out}/key_phrases/{lv}/kp_candidates.json",
              cost="{out}/cost_log.jsonl", work="{out}/key_phrases/{lv}/kp_candidates/round_1/work", article="redelivery_fee"),
    "Z": dict(out="er026_output/family_z_production_e2e_01/melos/run_kprescue_ev_01", cand="{out}/key_phrases/{lv}/kp_candidates.json",
              cost="{out}/cost_log.jsonl", work="{out}/key_phrases/{lv}/kp_candidates/round_1/work", article="melos"),
}


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _cost_by_stage(path):
    import er019_family_x_audio_production_runner_01 as x
    by = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                by.setdefault(d.get("stage"), []).append(line)
    out = {}
    for st, lines in by.items():
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as t:
            t.writelines(lines)
        jpy, _ = x.compute_cost_jpy_so_far(t.name)
        os.unlink(t.name)
        out[st] = {"calls": len(lines), "cost_jpy": round(jpy, 4)}
    total, _ = x.compute_cost_jpy_so_far(path)
    models = sorted({json.loads(line).get("model_id") for line in open(path, encoding="utf-8") if line.strip()})
    return {"by_stage": out, "total_cost_jpy": round(total, 4), "models": models, "n_calls": sum(v["calls"] for v in out.values())}


def summarize_doc(doc, work=None):
    cands = doc["candidates"]
    resc = [c for c in cands if c.get("rescue")]
    s = {
        "candidates_sha256": doc.get("candidates_sha256"), "sha_self_consistent": rv.candidates_sha256(doc) == doc.get("candidates_sha256"),
        "n_candidates": len(cands), "n_auto_eligible": sum(1 for c in cands if c.get("auto_eligible")), "shortfall": doc.get("shortfall"),
        "outer_attempts": doc.get("outer_attempts"),
        "outer_retry_log": [{k: e.get(k) for k in ("outer_attempt", "n_candidates", "n_auto_eligible", "n_gate_dropped", "n_rescued", "rescued_not_auto",
                                                    "failure", "call1_status", "call2_status")} for e in doc.get("outer_retry_log") or []],
        "n_rescued": len(resc), "dropped": [{"phrase": d["phrase"], "stage": d["stage"], "reason0": (d.get("reasons") or [""])[0][:80]} for d in doc.get("dropped") or []],
        "models_selection": doc.get("model_id"), "model_requested": doc.get("model_requested"),
        "prompt_sha256": doc.get("prompt_sha256"),
        "prompt_sha256_unchanged": (doc.get("prompt_sha256") or {}) == {"call1": ft.PROMPT_2_SHA256, "call2": p2v.PROMPT_2V_SHA256},
        "rescue_provenance": doc.get("rescue_provenance"),
        "rescue_provenance_matches_current": r125.provenance_drift(doc.get("rescue_provenance")) == [],
        "src_d1_gates": sorted({(c.get("gates") or {}).get("src_d1") for c in cands}),
        "candidates": [],
    }
    for c in cands:
        rs = c.get("rescue") or {}
        sel, can = rs.get("selection"), rs.get("canonicalization")
        s["candidates"].append({
            "ai_rank": c["ai_rank"], "origin": c["origin"], "selection_phrase": c["selection_phrase"], "used_form": c["used_form"], "auto_eligible": c["auto_eligible"],
            "rescued": bool(rs), "route": ("selection" if sel else None) or ("canonicalization" if can else None) if rs else None,
            "route_both": bool(sel and can), "codes": rs.get("codes"), "original_phrase": (sel or {}).get("original_phrase") or (can or {}).get("display_phrase"),
            "llm_key_phrase": (can or {}).get("llm_key_phrase"), "gloss": (rs.get("gloss") or {}).get("status"), "qa": (rs.get("qa") or {}).get("status"),
            "qa_error": (rs.get("qa") or {}).get("error"), "gates": c.get("gates"), "idiom_exception_flag": (c.get("flags") or {}).get("idiom_exception"),
            "verify_persisted_rescue": r125.verify_persisted_rescue(c), "reverify": r125.reverify_persisted_rescue(c) if rs else None})
    if work and os.path.exists(os.path.join(work, "canonicalization_runtime_metadata.json")):
        m = _j(os.path.join(work, "canonicalization_runtime_metadata.json"))
        s["canonicalization_model_id"] = m.get("model_id")
        s["canonicalization_final_status"] = m.get("final_status")
    if work and os.path.exists(os.path.join(work, "canonicalization_prompt.txt")):
        with open(os.path.join(work, "canonicalization_prompt.txt"), "rb") as f:
            s["canonicalization_prompt_sha256_run"] = hashlib.sha256(f.read()).hexdigest()
    return s


def main(replay_root, out_path):
    ev = {"fresh": {}, "replay": {}, "r3_qa_key_match": {"REVERT_SURFACE": {"rejudged_pass": 0, "not_rejudged": 0, "rejudged_fail": 0},
                                                        "REDERIVE_M1_WINDOW": {"rejudged_pass": 0, "not_rejudged": 0, "rejudged_fail": 0}}}
    for fam, c in FAMILIES.items():
        ev["fresh"][fam] = {"out_dir": c["out"], "levels": {}}
        for lv in ("a2", "b1b"):
            p = c["cand"].format(out=c["out"], lv=lv)
            if os.path.exists(p):
                ev["fresh"][fam]["levels"][lv] = summarize_doc(_j(p), c["work"].format(out=c["out"], lv=lv))
        cp = c["cost"].format(out=c["out"])
        if os.path.exists(cp):
            ev["fresh"][fam]["cost"] = _cost_by_stage(cp)
    if replay_root and os.path.isdir(replay_root):
        for name in sorted(os.listdir(replay_root)):
            rp = os.path.join(replay_root, name, "replay_result.json")
            if os.path.exists(rp):
                r = _j(rp)
                dp = os.path.join(replay_root, name, "kp_candidates_doc.json")
                ev["replay"][name] = {"result": {k: v for k, v in r.items() if k not in ("candidates",)}, "summary": summarize_doc(_j(dp)) if os.path.exists(dp) else None}
                cp = os.path.join(replay_root, name, "raw_usage_log.jsonl")
                if os.path.exists(cp):
                    ev["replay"][name]["cost"] = _cost_by_stage(cp)
    # R3集計(fresh + replay)
    docs = [lv for f in ev["fresh"].values() for lv in f["levels"].values()] + [v["summary"] for v in ev["replay"].values() if v.get("summary")]
    for d in docs:
        for c in d["candidates"]:
            if c["rescued"] and c["qa"] and c["codes"]:
                for code in c["codes"]:
                    if code in ev["r3_qa_key_match"]:
                        k = {"PASS": "rejudged_pass", "FAIL": "rejudged_fail", "NOT_REJUDGED": "not_rejudged"}.get(c["qa"])
                        if k:
                            ev["r3_qa_key_match"][code][k] += 1
    tot = 0.0
    for f in ev["fresh"].values():
        tot += (f.get("cost") or {}).get("total_cost_jpy", 0)
    for v in ev["replay"].values():
        tot += (v.get("cost") or {}).get("total_cost_jpy", 0)
    ev["total_cost_jpy"] = round(tot, 4)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=2)
    print("written", out_path, "total_cost_jpy", ev["total_cost_jpy"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
