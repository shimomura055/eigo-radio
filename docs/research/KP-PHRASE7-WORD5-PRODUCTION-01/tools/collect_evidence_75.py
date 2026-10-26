# -*- coding: utf-8 -*-
"""KP-PHRASE7-WORD5-PRODUCTION-01 委任_02: fresh/replay の7+5 evidence を evidence_01.json に集計する(読取りのみ・API 0)。
実行: .venv\\Scripts\\python.exe docs\\research\\KP-PHRASE7-WORD5-PRODUCTION-01\\tools\\collect_evidence_75.py
観測項目(EVIDENCE_PLAN_01 + Opus R-1/R-4/R-6): prompt_id/sha、model_id、kind/origin別件数、最終docの不変条件、used_formレベルの単語⊂フレーズ件数(R-1限界の実測)、
call1_attempts(P7)/outer_attempts、P7が1語を返した件数、overflow_kind/not_single_word、理由40字超件数(記録のみ)、補完/救済の記録、費用・所要時間。
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

D = "docs/research/KP-PHRASE7-WORD5-PRODUCTION-01"
XO = "er019_output/family_x_audio_production_wiring_01"
NEW = "run_kp75_ev_01"
# (family, article, kp_dir builder, usage log, old(3+5)比較用の過去run usage log)
TARGETS = [
    ("X", "UK列車(uk_train_speaker_playback)", f"{XO}/uk_train_speaker_playback__{NEW}", "{lv}", "raw_usage_log.jsonl",
     f"{XO}/uk_train_speaker_playback__run_kprescue_ev_01/raw_usage_log.jsonl"),
    ("X", "AI島(ai_island_temple)", f"{XO}/ai_island_temple__{NEW}", "{lv}", "raw_usage_log.jsonl",
     f"{XO}/ai_island_temple__run_kpbf_ev_01/raw_usage_log.jsonl"),
    ("Y", "再配達(redelivery_fee)", f"er121_output/family_y_production_01/redelivery_fee/{NEW}", "key_phrases/{lv}", "cost_log.jsonl",
     "er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/cost_log.jsonl"),
    ("Z", "走れメロス(melos)", f"er026_output/family_z_production_e2e_01/melos/{NEW}", "key_phrases/{lv}", "cost_log.jsonl",
     "er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01/cost_log.jsonl"),
]
REPLAYS = sorted(os.path.basename(p) for p in glob.glob(f"{D}/replay_results/*") if os.path.isdir(p))


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _words(s):
    return [t for t in (s or "").strip().split() if t]


def _key(s):
    import er119_kp_human_review_01 as rv
    return rv.phrase_key(s or "")


def invariants(doc: dict) -> dict:
    import er119_kp_candidates_01 as kc
    c = doc["candidates"]
    ph = [x for x in c if x.get("kind") == "phrase"]
    wd = [x for x in c if x.get("kind") == "word"]
    contained = []          # 単語⊂フレーズ(used_form/選定表層形のどちらかのtoken部分列)。0であるべき不変条件(M-4)
    contained_used_form_only = []   # R-1の既知限界: used_formレベルだけで見た含有(語形違いの取りこぼし)
    for w in wd:
        for p in ph:
            if kc._contains_any(w, p):
                contained.append([w["used_form"], p["used_form"]])
        wu = _key(w.get("used_form"))
        for p in ph:
            pu = _key(p.get("used_form")).split()
            if wu and wu in pu:
                contained_used_form_only.append([w["used_form"], p["used_form"]])
    return {"phrase<=7": len(ph) <= 7, "word<=5": len(wd) <= 5, "total<=12": len(c) <= 12, "n_phrase": len(ph), "n_word": len(wd),
            "word_in_phrase_pairs": contained, "word_in_phrase_used_form_exact_token_pairs": contained_used_form_only,
            "ok": len(ph) <= 7 and len(wd) <= 5 and len(c) <= 12 and not contained}


def summarize(doc: dict, kp_dir: str) -> dict:
    cands = doc["candidates"]
    bf = doc.get("backfill") or {}
    E = bf.get("E") or {}
    meta_p = f"{kp_dir}/kp_candidates/round_{doc.get('round', 1)}/work/keywords_runtime_metadata.json"
    meta = _j(meta_p) if os.path.exists(meta_p) else {}
    raw_p = f"{kp_dir}/kp_candidates/round_{doc.get('round', 1)}/work/keywords_selector_raw_attempts.json"
    p7_single = None
    p7_items_last = None
    if os.path.exists(raw_p):
        try:
            raws = _j(raw_p)
            last = [r for r in raws if r.get("raw_text")]
            if last:
                items = json.loads(last[-1]["raw_text"]).get("items") or []
                p7_items_last = len(items)
                p7_single = sum(1 for it in items if len(_words(it.get("phrase"))) == 1)
        except Exception as e:      # noqa: BLE001 集計専用
            p7_single = f"parse_error:{type(e).__name__}"
    stages = {}
    for d in doc.get("dropped") or []:
        stages[d.get("stage")] = stages.get(d.get("stage"), 0) + 1
    reasons = [(c.get("reason_ja") or "") for c in cands]
    over40 = [{"used_form": c["used_form"], "len": len(c.get("reason_ja") or "")} for c in cands if len(c.get("reason_ja") or "") > 40]
    return {
        "n_candidates": len(cands), "n_auto_eligible": sum(1 for c in cands if c.get("auto_eligible")),
        "origins": {o: sum(1 for c in cands if c.get("origin") == o) for o in ("call1", "call2", "backfill")},
        "kinds": {k: sum(1 for c in cands if c.get("kind") == k) for k in ("phrase", "word")},
        "invariants": invariants(doc),
        "prompt_ids": doc.get("prompt_ids"), "prompt_sha256": doc.get("prompt_sha256"), "model_id": doc.get("model_id"),
        "model_requested": doc.get("model_requested"),
        "call1_metadata": {k: meta.get(k) for k in ("prompt_id", "prompt_sha256", "kp_backend", "kp_backend_used", "attempts", "final_status", "shortfall",
                                                    "kp_count_max", "model_id", "model_requested")},
        "call1_attempts": meta.get("attempts"), "outer_attempts": doc.get("outer_attempts"),
        "outer_retry_log": [{k: v for k, v in e.items() if k in ("outer_attempt", "call1_status", "call2_status", "failure", "n_candidates", "n_auto_eligible",
                                                                "n_gate_dropped", "n_rescued", "stages", "backfill")} for e in (doc.get("outer_retry_log") or [])],
        "p7_last_attempt_items": p7_items_last, "p7_single_word_items": p7_single,
        "dropped_by_stage": stages, "overflow_kind": stages.get("overflow_kind", 0), "not_single_word": stages.get("not_single_word", 0),
        "backfill": {"triggered": bf.get("triggered"), "status": bf.get("status"), "reason": bf.get("reason"), "E": E, "N": bf.get("N"),
                     "added": bf.get("added"), "surplus": bf.get("surplus"), "prompts": bf.get("prompts"), "failure": bf.get("failure"),
                     "dropped_by_stage": bf.get("dropped_by_stage")},
        "rescued": [{"used_form": c["used_form"], "kind": c.get("kind"), "auto_eligible": c.get("auto_eligible")} for c in cands if (c.get("flags") or {}).get("rescued")],
        "reason_ja_over_40": over40, "reason_ja_max_len": max([len(r) for r in reasons] or [0]),
        "shortfall": doc.get("shortfall"), "shortfall_detail": doc.get("shortfall_detail"),
        "src_d1": sorted({(c.get("gates") or {}).get("src_d1") for c in cands}),
        "candidates_sha256": doc.get("candidates_sha256"),
        "candidates": [{"ai_rank": c["ai_rank"], "origin": c.get("origin"), "kind": c.get("kind"), "selection_phrase": c.get("selection_phrase"),
                        "used_form": c.get("used_form"), "japanese_gloss": c.get("japanese_gloss"), "reason_ja": c.get("reason_ja"),
                        "auto_eligible": c.get("auto_eligible")} for c in cands],
    }


def usage_stats(path: str) -> dict:
    """usage logの呼出数・合計時間・費用(JPY)。timestamp範囲(UTC)。stage別。"""
    import er019_family_x_audio_production_runner_01 as x
    if not os.path.exists(path):
        return {"missing": path}
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    total, _ = x.compute_cost_jpy_so_far(path)
    ts = sorted(r["timestamp"] for r in rows if r.get("timestamp"))
    by_stage = {}
    for r in rows:
        s = by_stage.setdefault(r.get("stage"), {"calls": 0, "elapsed_seconds": 0.0})
        s["calls"] += 1
        s["elapsed_seconds"] = round(s["elapsed_seconds"] + float(r.get("elapsed_seconds") or 0), 3)
    models = sorted({r.get("model_id") for r in rows})
    span = None
    if ts:
        a = datetime.fromisoformat(ts[0])
        b = datetime.fromisoformat(ts[-1])
        span = round((b - a).total_seconds(), 1)
    return {"path": path, "n_calls": len(rows), "cost_jpy": round(total, 4), "models": models, "first_ts": ts[0] if ts else None, "last_ts": ts[-1] if ts else None,
            "wall_span_seconds": span, "sum_call_elapsed_seconds": round(sum(float(r.get("elapsed_seconds") or 0) for r in rows), 1), "by_stage": by_stage}


def main():
    out = {"fresh": [], "replay": [], "usage": {}}
    for fam, art, base, lvdir, ulog, old_ulog in TARGETS:
        for lv in ("a2", "b1b"):
            kp_dir = f"{base}/{lv}/key_phrases" if fam == "X" else f"{base}/key_phrases/{lv}"
            cp = f"{kp_dir}/kp_candidates.json"
            if not os.path.exists(cp):
                out["fresh"].append({"family": fam, "article": art, "level": lv, "missing": cp})
                continue
            doc = _j(cp)
            s = summarize(doc, kp_dir)
            s.update(family=fam, article=art, level=lv, cand_path=cp, file_sha256=hashlib.sha256(open(cp, "rb").read()).hexdigest(),
                     candidates_mtime_utc=datetime.fromtimestamp(os.path.getmtime(cp), timezone.utc).isoformat())
            out["fresh"].append(s)
        u_new = usage_stats(f"{base}/{ulog}")
        u_old = usage_stats(old_ulog)
        out["usage"][f"{fam}:{art}"] = {"new_7plus5": u_new, "old_3plus5": u_old}
    for r in REPLAYS:
        rp = f"{D}/replay_results/{r}/replay_result.json"
        dp = f"{D}/replay_results/{r}/kp_candidates_doc.json"
        if not os.path.exists(dp):
            out["replay"].append({"case": r, "missing": dp})
            continue
        doc = _j(dp)
        s = summarize(doc, f"{D}/replay_results/{r}")
        rr = _j(rp) if os.path.exists(rp) else {}
        s.update(case=r, frozen=rr.get("frozen"), api_calls=rr.get("api_calls_logged"), api_by_stage=rr.get("api_calls_by_stage"))
        ul = f"{D}/replay_results/{r}/raw_usage_log.jsonl"
        s["usage"] = usage_stats(ul) if os.path.exists(ul) else None
        out["replay"].append(s)
    fresh_cost = sum(v["new_7plus5"].get("cost_jpy", 0) for v in out["usage"].values())
    replay_cost = sum((r.get("usage") or {}).get("cost_jpy", 0) for r in out["replay"])
    out["fresh_cost_jpy"] = round(fresh_cost, 4)
    out["replay_cost_jpy"] = round(replay_cost, 4)
    out["total_cost_jpy"] = round(fresh_cost + replay_cost, 4)
    with open(f"{D}/evidence_01.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"fresh_cost": out["fresh_cost_jpy"], "replay_cost": out["replay_cost_jpy"], "total": out["total_cost_jpy"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
