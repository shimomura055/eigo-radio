# ER-005-LLM-COST-STRUCTURE-AUDIT-01-R1
# Customized B1-only / A2-only episode cost、Scenario E(Writer=Sol維持、
# その他LLM=Luna想定)を、既存raw_usage_log.jsonl等から再集計する。
# 新規生成なし、Production変更なし。
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

from er005_tts_audit_extract import load_segments

LOG_PATH = "er005_output/cost_baseline_01/raw_usage_log.jsonl"
PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"

with open(LOG_PATH, encoding="utf-8") as f:
    RECORDS = [json.loads(l) for l in f]
with open(PRICING_PATH, encoding="utf-8") as f:
    PRICING = json.load(f)["prices"]

SOL_IN = next(p for p in PRICING if p["provider"] == "openai" and p["meter"] == "input_tokens")
SOL_CACHED = next(p for p in PRICING if p["provider"] == "openai" and p["meter"] == "cached_input_tokens")
SOL_OUT = next(p for p in PRICING if p["provider"] == "openai" and p["meter"] == "output_tokens")
SEARCH_FEE = next(p for p in PRICING if p["provider"] == "openai" and p["meter"] == "web_search_call")
GEMINI_IN = next(p for p in PRICING if p["provider"] == "gemini" and p["meter"] == "input_tokens")
GEMINI_OUT = next(p for p in PRICING if p["provider"] == "gemini" and p["meter"] == "output_tokens")
AZURE_HOUR = next(p for p in PRICING if p["provider"] == "azure" and p["meter"] == "audio_hour")

# 2026-08-18確認、developers.openai.com/api/docs/pricing(公式)
LUNA_IN = 0.20
LUNA_CACHED = 0.02
LUNA_OUT = 1.20

PROGRAMS = [("akb48", "b1b", "b1_tts_asr"), ("akb48", "a2", "a2_tts_asr"),
            ("parenting", "b1b", "b1_tts_asr"), ("parenting", "a2", "a2_tts_asr")]


def openai_cost(r, in_price=None, cached_price=None, out_price=None):
    in_price = in_price if in_price is not None else SOL_IN["price"]
    cached_price = cached_price if cached_price is not None else SOL_CACHED["price"]
    out_price = out_price if out_price is not None else SOL_OUT["price"]
    input_tokens = r.get("input_tokens") or 0
    cached = r.get("cached_input_tokens") or 0
    output_tokens = r.get("output_tokens") or 0
    billable_in = max(input_tokens - cached, 0)
    cost = billable_in / 1_000_000 * in_price + cached / 1_000_000 * cached_price + output_tokens / 1_000_000 * out_price
    search_calls = r.get("web_search_call_count") or 0
    cost += search_calls / 1000 * SEARCH_FEE["price"]
    return cost


def classify_kept_openai():
    kept = [False] * len(RECORDS)
    by_group = defaultdict(list)
    for i, r in enumerate(RECORDS):
        if r["provider"] != "openai":
            continue
        by_group[(r["theme"], r["stage"])].append(i)
    for (theme, stage), idxs in by_group.items():
        idxs_sorted = sorted(idxs, key=lambda i: RECORDS[i]["timestamp"])
        if stage.startswith("research_ledger"):
            kept[idxs_sorted[-1]] = True  # 最終(topic非依存化後)のみKEPT
        else:
            for j in idxs_sorted:
                kept[j] = True
    return kept


KEPT_OPENAI = classify_kept_openai()


def openai_records_for(theme, stage):
    idxs = [i for i in range(len(RECORDS))
            if KEPT_OPENAI[i] and RECORDS[i]["theme"] == theme and RECORDS[i]["stage"] == stage]
    idxs.sort(key=lambda i: RECORDS[i]["timestamp"])
    return [RECORDS[i] for i in idxs]


# ============================================================
# Clean-run ASR cost(TTS Auditと同じsegment attempt構造を再利用。
# 1st attemptの音声長のみを$1/hourで計上)
# ============================================================
def attempt_duration(a: dict):
    ti = a.get("trim_info")
    if ti and ti.get("raw_duration_seconds") is not None:
        return ti["raw_duration_seconds"]
    if a.get("duration_seconds") is not None:
        return a["duration_seconds"]
    return None


def clean_run_asr_cost(theme, level):
    entries = load_segments(theme, level)
    total_seconds = 0.0
    for name, typ, count, attempts, kind in entries:
        if not attempts:
            continue
        d = attempt_duration(attempts[0])
        if d:
            total_seconds += d
    return total_seconds / 3600 * AZURE_HOUR["price"]


results = {}
for theme in ["akb48", "parenting"]:
    level_map = {"b1": "b1b", "a2": "a2"}
    theme_result = {}

    research_draft = openai_records_for(theme, "research_ledger_draft")
    research_verif = openai_records_for(theme, "research_ledger_verification")
    shared_research_cost_sol = sum(openai_cost(r) for r in research_draft + research_verif if r.get("success"))

    for level_key, level_dir in level_map.items():
        wfc = openai_records_for(theme, f"{level_key}_writer_and_fact_qa")
        support = openai_records_for(theme, f"{level_key}_support")
        kp = openai_records_for(theme, f"{level_key}_key_phrase")

        writer_record = wfc[0] if wfc else None
        other_llm_records = wfc[1:] + support + kp

        writer_cost_sol = openai_cost(writer_record) if writer_record and writer_record.get("success") else 0.0
        other_llm_cost_sol = sum(openai_cost(r) for r in other_llm_records if r.get("success"))
        other_llm_cost_luna = sum(
            openai_cost(r, LUNA_IN, LUNA_CACHED, LUNA_OUT) for r in other_llm_records if r.get("success"))

        # Clean-run TTS(既存TTS Auditのestimateを再利用)
        with open("er005_output/cost_baseline_01/tts_audit_summary.json", encoding="utf-8") as f:
            tts_audit = json.load(f)
        prog_key = f"{theme}_{level_dir}"
        clean_tts = tts_audit[prog_key]["clean_run_tts_cost_estimated"]

        clean_asr = clean_run_asr_cost(theme, level_dir)

        current_episode_cost = shared_research_cost_sol + writer_cost_sol + other_llm_cost_sol + clean_tts + clean_asr
        scenario_e_cost = shared_research_cost_sol + writer_cost_sol + other_llm_cost_luna + clean_tts + clean_asr

        theme_result[level_key] = {
            "shared_research_cost": round(shared_research_cost_sol, 4),
            "writer_cost_sol": round(writer_cost_sol, 4),
            "other_llm_cost_sol": round(other_llm_cost_sol, 4),
            "other_llm_cost_luna": round(other_llm_cost_luna, 4),
            "clean_run_tts_cost": round(clean_tts, 4),
            "clean_run_asr_cost": round(clean_asr, 4),
            "current_customized_episode_cost": round(current_episode_cost, 4),
            "scenario_e_cost": round(scenario_e_cost, 4),
            "gap_to_target_x": round(current_episode_cost / 0.10, 2),
            "scenario_e_gap_to_target_x": round(scenario_e_cost / 0.10, 2),
            "tts_pct_of_target": round(clean_tts / 0.10 * 100, 1),
            "asr_pct_of_target": round(clean_asr / 0.10 * 100, 1),
        }

    results[theme] = theme_result

with open("er005_output/cost_baseline_01/llm_cost_structure_r1_summary.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(json.dumps(results, indent=2))
