#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPEN-256 是正後 (b) runtime evidence(少額・実API)。

Production retry経路 er003_v1_crosslevel_audio_02_common._local_rewrite_recovery_for_english_segment_with_fallback
(= run_local_rewrite_recovery を呼ぶ実経路) を、METAコメント2原稿逐語1 segmentに対し、隔離out dirで実行する。
TTS backend=speech_metadata_flash_lite(Production既定)。Ledger/記事/既存音声は読み取りのみ。
usage: .venv/Scripts/python.exe er053_family_x_open256_runtime_01.py <run_no>
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

import er005_cost_logger as cost_logger

RUN = sys.argv[1] if len(sys.argv) > 1 else "1"
BASE = os.path.join("er053_output", "family_x_tts_asr_rootcause_01", "open256_runtime_01", f"run{RUN}")
THEME, LEVEL = f"open256_runtime_run{RUN}", "b1b"
OUT_PATH = f"{BASE}/{THEME}/{LEVEL}/narration/comment_2.wav".replace("\\", "/")
TEXT = ("Some Muse calls were handed over to human workers, but not all of them. "
        "Were people told when a worker took over, and what did Meta change after the test?")
LAST_ASR = ("Some use calls were handed over to human workers, but not all of them. "
            "Were people told when a worker took over? And what did Meta change after the test?")
BUDGET_JPY = 15.0
USD_JPY = 160.0
PRICES_USD_PER_M = {  # er005_output/cost_baseline_01/pricing_snapshot.json (Standard)
    "gemini-3.8-flash-lite-tts": (0.5, 6.0), "gpt-6-luna": (0.1, 0.5),
    "gpt-5.6-luna": (0.2, 1.2), "gemini-3.5-flash-lite": (0.3, 2.5),
}
WATCH = ("er011_output/attempt_history.jsonl", "er011_output/human_review_queue.jsonl",
         "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
         "er006_output/master_audio_store_01/manifest.json",
         "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
         "er006_output/pronunciation_ledger_01/ledger.json",
         "er030_output/kp_backend_telemetry_01/telemetry.jsonl",
         "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl")


def _sha(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def _lines(path):
    try:
        with open(path, "rb") as f:
            return f.read().count(b"\n")
    except OSError:
        return None


def snapshot():
    out = subprocess.run(["git", "status", "--porcelain", "-uall"], capture_output=True, text=True,
                         encoding="utf-8").stdout.splitlines()
    snap = {}
    for line in out:
        p = line[3:].strip().strip('"')
        if p.startswith("er053_output/family_x_tts_asr_rootcause_01/open256_runtime_01"):
            continue
        snap[p] = (_sha(p), _lines(p))
    for p in WATCH:
        snap.setdefault(p, (_sha(p), _lines(p)))
    return snap


def estimate_cost(log_path):
    rows = [json.loads(l) for l in open(log_path, encoding="utf-8") if l.strip()]
    total_usd, detail = 0.0, []
    for r in rows:
        mid = r.get("model_id") or ""
        key = next((k for k in PRICES_USD_PER_M if k in mid), None)
        inp = r.get("input_tokens") or r.get("prompt_token_count") or 0
        outp = r.get("output_tokens") or r.get("candidates_token_count") or 0
        usd = None
        if key:
            pi, po = PRICES_USD_PER_M[key]
            usd = inp / 1e6 * pi + outp / 1e6 * po
        elif r.get("provider") == "azure":
            usd = (float(r.get("audio_seconds") or r.get("audio_duration_seconds") or 0) / 3600.0) * 1.0
        detail.append({"provider": r.get("provider"), "api": r.get("api"), "model_id": mid,
                       "success": r.get("success"), "input_tokens": inp, "output_tokens": outp,
                       "est_usd": usd, "raw": r})
        total_usd += usd or 0.0
    return {"n_calls": len(rows), "est_usd_known_meters": round(total_usd, 6),
            "est_jpy_known_meters": round(total_usd * USD_JPY, 3),
            "unpriced_calls": [{k: d[k] for k in ("provider", "api", "model_id")} for d in detail if d["est_usd"] is None],
            "calls": detail}


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    log_path = f"{BASE}/raw_usage_log.jsonl"
    cost_logger.install(log_path)
    import er003_v1_crosslevel_audio_02_common as cc
    before = snapshot()
    t0 = time.time()
    with cost_logger.logging_context("open256_runtime", f"run{RUN}"):
        rec = cc._local_rewrite_recovery_for_english_segment_with_fallback(
            TEXT, OUT_PATH, LAST_ASR, 60, True, False, False, [], [], [],
            tts_backend="speech_metadata_flash_lite")
    elapsed = round(time.time() - t0, 1)
    art_src = f"er011_output/local_rewrite_recovery/{THEME}/{LEVEL}"
    art = None
    if os.path.isdir(art_src):
        shutil.copytree(art_src, f"{BASE}/recovery_artifacts", dirs_exist_ok=True)
        art_json = f"{art_src}/local_rewrite_recovery_comment_2.json"
        if os.path.exists(art_json):
            art = json.load(open(art_json, encoding="utf-8"))
    after = snapshot()
    changed = {p: {"before": before.get(p), "after": after.get(p)} for p in set(before) | set(after)
               if before.get(p) != after.get(p)}
    summary = {"run": RUN, "elapsed_seconds": elapsed, "returned_none": rec is None,
               "resolved": None if rec is None else rec.get("status"),
               "shared_files_changed": sorted(changed)}
    if art:
        sel = (art.get("selection") or {}).get("selected")
        summary["recovery_status"] = art.get("status")
        summary["selection_status"] = (art.get("selection") or {}).get("status")
        summary["selected_id"] = (sel or {}).get("id")
        summary["selected_text"] = (sel or {}).get("rewritten_segment")
        summary["old_rule_would_pass_selected"] = (
            None if not sel else sel["rewritten_segment"][:15].strip().lower() == TEXT[:15].strip().lower())
        summary["new_rule_full_segment_check_selected"] = (sel or {}).get("full_segment_check")
        summary["per_candidate"] = [
            {"id": c["id"], "text": c["rewritten_segment"],
             "span": [c.get("changed_span_before"), c.get("changed_span_after")],
             "old_prefix15_rule_pass": c["rewritten_segment"][:15].strip().lower() == TEXT[:15].strip().lower(),
             "full_segment_check": c["full_segment_check"], "seven_gates": c["seven_gates"],
             "all_seven_gates_pass": c["all_seven_gates_pass"]} for c in art.get("candidates") or []]
        summary["luna_candidate_gen_model_id"] = (art.get("candidate_gen") or {}).get("_model_id")
        summary["luna_qa_model_id"] = (art.get("qa") or {}).get("_model_id")
        rt = art.get("retts_result") or {}
        summary["retts_status"] = rt.get("status")
        summary["retts_asr_text"] = rt.get("asr_text")
        summary["retts_asr_verified"] = rt.get("asr_verified")
        summary["retts_keys"] = sorted(rt.keys())
    if rec is not None:
        summary["resolved_keys"] = sorted(rec.keys())
    summary["cost"] = estimate_cost(log_path)
    summary["budget_jpy"] = BUDGET_JPY
    with open(f"{BASE}/runtime_result.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{BASE}/shared_files_changed.json", "w", encoding="utf-8") as f:
        json.dump(changed, f, indent=1)
    brief = {k: v for k, v in summary.items() if k not in ("cost", "per_candidate", "retts_keys", "resolved_keys")}
    print(json.dumps(brief, ensure_ascii=False, indent=1, default=str))
    print("COST_JPY", summary["cost"]["est_jpy_known_meters"], "n_calls", summary["cost"]["n_calls"],
          "unpriced", summary["cost"]["unpriced_calls"])


if __name__ == "__main__":
    main()
