# -*- coding: utf-8 -*-
"""成果物の統合(オフライン): results_01.jsonl / cost_01.json / telemetry_guard_01.json / conditions_manifest_01.json。"""
import collections
import glob
import json
import os
import sys

sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_lib as L
import er065_short_clip_asr_context_trial_01_runner as R

OUT = "er065_output/short_clip_asr_context_trial_01"
L.install_write_guard([OUT])

# results
n = 0
with open(OUT + "/results_01.jsonl", "w", encoding="utf-8") as f:
    for p in sorted(glob.glob(OUT + "/results_01_*_*.jsonl")):
        for line in open(p, encoding="utf-8"):
            f.write(line)
            n += 1

# cost
calls, by_engine, by_tag = 0, collections.defaultdict(float), {}
rows = []
for p in sorted(glob.glob(OUT + "/cost_01_*.jsonl")) + [OUT + "/smoke/cost_smoke.jsonl"]:
    tag = os.path.basename(p)[len("cost_01_"):-len(".jsonl")] if os.path.basename(p).startswith("cost_01_") else "smoke_test"
    t = 0.0
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        calls += 1
        by_engine[r["engine"]] += r["jpy"]
        t += r["jpy"]
        rows.append(r)
    by_tag[tag] = round(t, 4)
total = round(sum(by_engine.values()), 4)
audio_sec = {}
for r in rows:
    audio_sec[r["engine"]] = audio_sec.get(r["engine"], 0) + (r.get("audio_seconds") or 0)
ledger_path = "er026_output/family_z_production_e2e_01/melos/COST_LEDGER_MELOS_01.md"
ledger_tail = [ln for ln in open(ledger_path, encoding="utf-8").read().splitlines() if "累計" in ln][-3:]
json.dump({
    "trial": "FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01", "currency": "JPY", "usd_jpy": 160.0,
    "pricing_source": "er005_output/cost_baseline_01/pricing_snapshot.json (gpt-4o-mini-transcribe input $1.25/M, output $5.0/M tokens [OFFICIAL_SOURCE]; Azure STT $1.0/audio-hour [Retail Prices API])",
    "models": {"openai": "gpt-4o-mini-transcribe (Production Primary と同一。最新モデル原則の例外=比較可能性のためProduction同一モデルで評価)",
               "azure": "Azure Speech STT en-US + PhraseList(Production Secondary と同一方式)+ word timestamps(Detailed出力)",
               "whisper": "local faster-whisper small/medium (無料CPU・参照用の第三者engine、Production対象外)"},
    "total_jpy": total, "trial_cap_jpy": 40.0, "remaining_jpy": round(40.0 - total, 4),
    "by_engine_jpy": {k: round(v, 4) for k, v in by_engine.items()}, "by_process_tag_jpy": by_tag,
    "n_api_calls_logged": calls, "asr_audio_seconds_by_engine": {k: round(v, 1) for k, v in audio_sec.items()},
    "tts_regeneration_calls": 0,
    "melos_budget_note": {"ledger_path": ledger_path, "ledger_cumulative_lines_at_finalize": ledger_tail,
                          "melos_cumulative_before_this_trial_jpy": 185.4,
                          "melos_cumulative_incl_this_trial_est_jpy": round(185.4 + total, 2),
                          "cap_jpy": 300.0,
                          "note": "並行agentがledgerへ追記する可能性があるため、185.4は本Trial開始時に確認したCS監査委任_02時点の値。最新値との合算は報告時にledger再確認"},
    "calls": rows}, open(OUT + "/cost_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# telemetry guard
befores = {os.path.basename(p): json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(OUT + "/telemetry_guard_before_*.json"))}
afters = {os.path.basename(p): json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(OUT + "/telemetry_guard_after_*.json"))}
now = R.fingerprints()
first_tag = sorted(befores)[0]
first = befores[first_tag]["files"]
diff_vs_first = {p: {"first_before": first[p], "now": now[p]} for p in R.GUARDED if (first[p].get("lines"), first[p].get("sha256")) != (now[p].get("lines"), now[p].get("sha256"))}
blocked = {k: v["write_guard"]["blocked_write_attempts"] for k, v in afters.items()}
changed_in_run = {k: list(v["changed_during_run"]) for k, v in afters.items()}
json.dump({
    "purpose": "Production state(telemetry/queue/ledger/attempt_history/master store/cost_baseline/run_e2e_02 cost_log)がTrial実行で不変であることの証拠",
    "method": "(1)各runner process実行前後で対象ファイルの行数+sha256を記録(telemetry_guard_before/after_<tag>.json) (2)sys.addaudithookのwrite guardでtrial dir(+OS temp)外への書込を例外で遮断し記録 (3)Production ASR helper(telemetry/queue/ledger追記経路を持つもの)は呼ばず、lib内の読取専用ASR実装を使用 (4)Production判定関数classify_asr_matchは読取呼出しのみ、semantic_equivalence.append_telemetry_logをno-op化",
    "guarded_files": R.GUARDED,
    "files_at_first_process_start": first, "files_at_finalize": now,
    "changed_between_first_start_and_finalize": diff_vs_first,
    "changed_during_each_process_run": changed_in_run,
    "blocked_write_attempts_by_process": blocked,
    "concurrent_agent_note": "並行agent(FAMILY-Z-MELOS-FINAL-ASSEMBLY-AND-ASR-GENERALIZATION-01)がrun_e2e_02/COST_LEDGERへ書込む可能性がある。差分が出た場合は本Trialの書込ではない(本processのwrite guardはtrial dir外への書込を0件記録)ことをblocked/各process changed_during_runと併せて判断する",
}, open(OUT + "/telemetry_guard_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# manifest merge
allc, meta = [], {}
for p in sorted(glob.glob(OUT + "/conditions_manifest_*_01.json")):
    m = json.load(open(p, encoding="utf-8"))
    meta[os.path.basename(p)] = {k: m[k] for k in m if k != "conditions"}
    allc.extend(m["conditions"])
slim = []
for c in allc:
    slim.append({k: c.get(k) for k in ("cond_id", "group", "target_id", "recipe_id", "kind", "wav", "wav_sha256", "total_sec", "pre_ctx_sec", "post_ctx_sec",
                                   "n_ctx_clips", "target_span", "ctx_all_same_voice", "ctx_has_focus_word", "canonical_target", "focus_word", "gap_ms", "category", "defect", "label_hint")}
                | {"parts": [{k: p[k] for k in ("clip_id", "role", "path", "sha256", "dur", "voice", "model", "text", "span", "same_voice_as_target") if k in p} for p in c["parts"]]})
json.dump({"manifests": meta, "n_conditions": len(slim), "conditions": slim}, open(OUT + "/conditions_manifest_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("results", n, "cost", total, "conditions", len(slim), "guard blocked", {k: v for k, v in blocked.items() if v})
