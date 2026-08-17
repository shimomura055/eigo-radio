# ER-005-TTS-CLEAN-COST-AUDIT-01: TTS Clean-run原価分解の本体分析
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

from er005_tts_audit_extract import load_segments, SEGMENT_TYPE

LOG_PATH = "er005_output/cost_baseline_01/raw_usage_log.jsonl"
PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"

with open(LOG_PATH, encoding="utf-8") as f:
    RECORDS = [json.loads(l) for l in f]
with open(PRICING_PATH, encoding="utf-8") as f:
    PRICING = json.load(f)["prices"]

GEMINI_IN = next(p for p in PRICING if p["provider"] == "gemini" and p["meter"] == "input_tokens")
GEMINI_OUT = next(p for p in PRICING if p["provider"] == "gemini" and p["meter"] == "output_tokens")


def gemini_cost(input_tokens, output_tokens):
    return (input_tokens or 0) / 1_000_000 * GEMINI_IN["price"] + (output_tokens or 0) / 1_000_000 * GEMINI_OUT["price"]


PROGRAMS = [("akb48", "b1b", "b1_tts_asr"), ("akb48", "a2", "a2_tts_asr"),
            ("parenting", "b1b", "b1_tts_asr"), ("parenting", "a2", "a2_tts_asr")]

# ============================================================
# KEPT分類(ER-005-COST-BASELINE-01と同一ロジックを再利用: timestamp gapで
# Parentingのクォータ障害runを除外)
# ============================================================
def classify_kept(records):
    kept = [False] * len(records)
    by_group = defaultdict(list)
    for i, r in enumerate(records):
        by_group[(r["theme"], r["stage"])].append(i)
    for (theme, stage), idxs in by_group.items():
        idxs_sorted = sorted(idxs, key=lambda i: records[i]["timestamp"])
        if stage in ("b1_tts_asr", "a2_tts_asr") and theme == "parenting":
            cutoff = None
            for j in range(1, len(idxs_sorted)):
                t0 = datetime.fromisoformat(records[idxs_sorted[j - 1]]["timestamp"])
                t1 = datetime.fromisoformat(records[idxs_sorted[j]]["timestamp"])
                if (t1 - t0).total_seconds() > 3000:
                    cutoff = j
            rng = idxs_sorted[cutoff:] if cutoff is not None else idxs_sorted
            for j in rng:
                kept[j] = True
        else:
            for j in idxs_sorted:
                kept[j] = True
    return kept


KEPT = classify_kept(RECORDS)

# ============================================================
# Program別のgemini(TTS)/azure(ASR) kept records、時系列順
# ============================================================
def gemini_records_for(theme, stage):
    idxs = [i for i in range(len(RECORDS))
            if KEPT[i] and RECORDS[i]["theme"] == theme and RECORDS[i]["stage"] == stage
            and RECORDS[i]["provider"] == "gemini"]
    idxs.sort(key=lambda i: RECORDS[i]["timestamp"])
    return [RECORDS[i] for i in idxs]


def azure_records_for(theme, stage):
    idxs = [i for i in range(len(RECORDS))
            if KEPT[i] and RECORDS[i]["theme"] == theme and RECORDS[i]["stage"] == stage
            and RECORDS[i]["provider"] == "azure"]
    idxs.sort(key=lambda i: RECORDS[i]["timestamp"])
    return [RECORDS[i] for i in idxs]


def actual_gemini_cost(theme, stage):
    recs = gemini_records_for(theme, stage)
    return sum(gemini_cost(r.get("input_tokens"), r.get("output_tokens")) for r in recs if r.get("success"))


# ============================================================
# Clean-run TTS cost(segment単位の"1回目attempt"の推定コスト合計)
# ============================================================
# raw_usage_log(gemini)にはsegment名が記録されていない一方、
# segment側のattempts_logには各attemptの生成音声長(trim_info.
# raw_duration_seconds)が残っている。TTS Costはoutput token(≒音声長)が
# 全体の93-94%を占める(input/output cost split参照)ため、
# 「$/audio-second」という単位コストを、そのstageの実測output cost
# 合計÷実測音声長合計から逆算し、各attemptの音声長にその単位コストを
# 掛けてoutput cost部分を推定する。input cost部分は、instruction
# prefixがほぼ固定長でありcall数に比例するとみなし、実測input cost
# 合計をcall数で均等配分する。
# これは推定(ESTIMATED)であり、公式usage metadataそのものではない。
def build_cost_rates(theme, stage):
    recs = gemini_records_for(theme, stage)
    total_in_cost = sum((r.get("input_tokens") or 0) / 1_000_000 * GEMINI_IN["price"] for r in recs if r.get("success"))
    total_out_cost = sum((r.get("output_tokens") or 0) / 1_000_000 * GEMINI_OUT["price"] for r in recs if r.get("success"))
    n_calls = sum(1 for r in recs if r.get("success"))
    return {
        "input_cost_per_call": (total_in_cost / n_calls) if n_calls else 0.0,
        "total_in_cost": total_in_cost,
        "total_out_cost": total_out_cost,
        "n_calls": n_calls,
    }


def attempt_duration(a: dict):
    """2種類のschemaに対応: trim_info.raw_duration_seconds(voice01/news_tail_fix/
    point_headings系)、またはフラットなduration_seconds(Key Phrase系の
    standard/fallback attempts_log)。どちらも無ければNone(audio未生成)。"""
    ti = a.get("trim_info")
    if ti and ti.get("raw_duration_seconds") is not None:
        return ti["raw_duration_seconds"]
    if a.get("duration_seconds") is not None:
        return a["duration_seconds"]
    return None


def build_duration_rate(theme, level, stage):
    entries = load_segments(theme, level)
    total_duration = 0.0
    for name, typ, count, attempts, kind in entries:
        for a in attempts:
            d = attempt_duration(a)
            if d:
                total_duration += d
    rates = build_cost_rates(theme, stage)
    return (rates["total_out_cost"] / total_duration) if total_duration else 0.0, rates["input_cost_per_call"]


def estimate_attempt_cost(a: dict, sec_rate: float, in_cost_per_call: float) -> float:
    duration = attempt_duration(a)
    # API失敗(status==STOPPEDでduration情報無し)はaudio未生成としてoutput cost=0、
    # input costのみ計上するかは不明(providerがinput処理前に失敗した可能性もある)。
    # 保守的に、監査対象からは除外せずinput_cost_per_callの半額を計上する
    # (ESTIMATED、根拠なき精密化を避けるための単純化)。
    if duration is None:
        return in_cost_per_call * 0.5
    return duration * sec_rate + in_cost_per_call


# ============================================================
# Attempt分類: TTS_API_ERROR / ASR_EMPTY_RESPONSE / CONTENT_MISMATCH / VERIFIED
# ============================================================
def classify_attempt(a: dict) -> str:
    if a.get("verified"):
        return "VERIFIED"
    status = a.get("status")
    if status == "STOPPED" and a.get("reason"):
        return "TTS_API_ERROR"
    asr_text = a.get("asr_text")
    if asr_text == "" or asr_text is None:
        return "ASR_EMPTY_RESPONSE"
    return "CONTENT_MISMATCH"


# ============================================================
# Program別サマリ
# ============================================================
results = {}
for theme, level, stage in PROGRAMS:
    prog_key = f"{theme}_{level}"
    entries = load_segments(theme, level)
    total_logical_attempts = sum(e[2] for e in entries)

    actual_calls_gemini = len(gemini_records_for(theme, stage))
    actual_calls_azure = len(azure_records_for(theme, stage))
    actual_cost = actual_gemini_cost(theme, stage)
    sec_rate, in_cost_per_call = build_duration_rate(theme, level, stage)

    n_segments = len(entries)
    clean_required_calls = n_segments

    type_counts = defaultdict(lambda: {"clean_calls": 0, "retry_calls": 0, "clean_cost": 0.0, "retry_cost": 0.0})
    cause_counts = defaultdict(lambda: {"count": 0, "cost": 0.0})
    verified_segments = 0
    stopped_segments = 0
    clean_cost_total = 0.0
    for name, typ, count, attempts, kind in entries:
        type_counts[typ]["clean_calls"] += 1
        type_counts[typ]["retry_calls"] += max(count - 1, 0)
        for idx, a in enumerate(attempts):
            est_cost = estimate_attempt_cost(a, sec_rate, in_cost_per_call)
            cause = classify_attempt(a)
            if idx == 0:
                type_counts[typ]["clean_cost"] += est_cost
                clean_cost_total += est_cost
            else:
                type_counts[typ]["retry_cost"] += est_cost
            if idx > 0 or cause != "VERIFIED":
                cause_counts[cause]["count"] += 1
                if idx > 0:
                    cause_counts[cause]["cost"] += est_cost
        if attempts and attempts[-1].get("verified"):
            verified_segments += 1
        elif count > 0 and not any(a.get("verified") for a in attempts):
            stopped_segments += 1

    # 正規化: 推定コストの合計(clean+retry)を実測actual_costへスケーリングする
    # (duration按分推定は、attempts_logに現れないhidden technical retry分を
    # 含まないため、そのままでは実測合計と一致しない。相対配分は保ちつつ
    # 既知の正確な合計へアンカーする)
    est_total = clean_cost_total + sum(v["retry_cost"] for v in type_counts.values())
    scale = (actual_cost / est_total) if est_total else 1.0
    clean_cost_total_scaled = clean_cost_total * scale
    for v in type_counts.values():
        v["clean_cost"] *= scale
        v["retry_cost"] *= scale
    for v in cause_counts.values():
        v["cost"] *= scale

    results[prog_key] = {
        "theme": theme, "level": level,
        "n_segments": n_segments,
        "clean_required_calls": clean_required_calls,
        "total_logical_attempts": total_logical_attempts,
        "actual_calls_gemini": actual_calls_gemini,
        "actual_calls_azure": actual_calls_azure,
        "call_amplification": round(actual_calls_gemini / clean_required_calls, 2) if clean_required_calls else None,
        "actual_tts_cost": round(actual_cost, 4),
        "clean_run_tts_cost_estimated": round(clean_cost_total_scaled, 4),
        "retry_waste_tts_cost_estimated": round(actual_cost - clean_cost_total_scaled, 4),
        "waste_pct": round((actual_cost - clean_cost_total_scaled) / actual_cost * 100, 1) if actual_cost else 0,
        "normalization_scale_factor": round(scale, 3),
        "segment_type_counts": {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in type_counts.items()},
        "cause_counts": {k: {"count": v["count"], "cost_estimated": round(v["cost"], 4)} for k, v in cause_counts.items()},
        "verified_segments": verified_segments,
        "stopped_segments": stopped_segments,
        "reconciliation_gap": actual_calls_gemini - total_logical_attempts,
    }

# ============================================================
# Input/Output cost split(program別、集計ベース・厳密)
# ============================================================
for theme, level, stage in PROGRAMS:
    prog_key = f"{theme}_{level}"
    recs = gemini_records_for(theme, stage)
    total_in = sum(r.get("input_tokens") or 0 for r in recs if r.get("success"))
    total_out = sum(r.get("output_tokens") or 0 for r in recs if r.get("success"))
    in_cost = total_in / 1_000_000 * GEMINI_IN["price"]
    out_cost = total_out / 1_000_000 * GEMINI_OUT["price"]
    total_cost = in_cost + out_cost
    results[prog_key]["input_tokens_total"] = total_in
    results[prog_key]["output_tokens_total"] = total_out
    results[prog_key]["input_cost_usd"] = round(in_cost, 4)
    results[prog_key]["output_cost_usd"] = round(out_cost, 4)
    results[prog_key]["output_cost_pct"] = round(out_cost / total_cost * 100, 1) if total_cost else 0
    results[prog_key]["input_cost_pct"] = round(in_cost / total_cost * 100, 1) if total_cost else 0

# ============================================================
# Theoretical consolidated-call lower bound(section 13)
# instruction input costは1 callにつきほぼ固定(in_cost_per_call)と
# みなし、これがclean_required_calls回分重複している。理論上1callへ
# 統合すればinstruction repetitionは(n-1)回分だけ削減できる
# (音声output量そのものはほぼ不変という前提、Voice分離等は無視)。
# ============================================================
for theme, level, stage in PROGRAMS:
    prog_key = f"{theme}_{level}"
    rates = build_cost_rates(theme, stage)
    n = results[prog_key]["n_segments"]
    in_per_call = rates["input_cost_per_call"]
    clean_cost = results[prog_key]["clean_run_tts_cost_estimated"]
    theoretical_min = clean_cost - in_per_call * max(n - 1, 0)
    results[prog_key]["theoretical_consolidated_cost"] = round(max(theoretical_min, 0), 4)
    results[prog_key]["theoretical_savings_vs_clean_run"] = round(clean_cost - max(theoretical_min, 0), 4)
    results[prog_key]["theoretical_savings_pct_of_clean_run"] = round(
        (clean_cost - max(theoretical_min, 0)) / clean_cost * 100, 1) if clean_cost else 0

with open("er005_output/cost_baseline_01/tts_audit_summary.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(json.dumps(results, indent=2)[:3000])
