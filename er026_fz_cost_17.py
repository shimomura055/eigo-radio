# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_17: run_e2e_03 工程別費用集計(有料APIなし、read-only)。
出典=<run>/cost_log.jsonl(実測usage)。単価換算はrunnerと同じ er019_family_x_audio_production_runner_01.compute_cost_jpy_so_far を
stage/provider別に分割した一時ファイル(tempdir)へ適用(= runnerのbudget guardと同一計算)。ASR等でusage未取得の記録は『未取得』として件数を別掲。
¥300枠(run_e2e_01/02)は別枠のため参考表示のみで合算しない。"""
import argparse
import collections
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er019_family_x_audio_production_runner_01 as XR  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--run-dir", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--cap", type=float, default=100.0)
ap.add_argument("--ref-runs", nargs="*", default=["run_e2e_01", "run_e2e_02"])
A = ap.parse_args()


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def jpy_of(recs):
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "c.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return XR.compute_cost_jpy_so_far(p)[0]


recs = load(f"{A.run_dir}/cost_log.jsonl")
by_stage = collections.defaultdict(list)
for r in recs:
    by_stage[r.get("stage")].append(r)
stages = {}
for st, rs in sorted(by_stage.items(), key=lambda kv: str(kv[0])):
    prov = collections.defaultdict(list)
    for r in rs:
        prov[r.get("provider")].append(r)
    stages[str(st)] = {
        "jpy": round(jpy_of(rs), 4), "calls": len(rs),
        "by_provider": {k: {"jpy": round(jpy_of(v), 4), "calls": len(v),
                            "models": sorted({x.get("model_id") or x.get("model") or "?" for x in v})} for k, v in sorted(prov.items(), key=lambda kv: str(kv[0]))},
        "web_search_calls": sum(int(x.get("web_search_call_count") or 0) for x in rs),
        "usage_not_obtained": sum(1 for x in rs if x.get("usage_source") not in ("OFFICIAL_API_RESPONSE",) and x.get("cost_usd") is None),
        "failed_calls": sum(1 for x in rs if x.get("success") is False),
    }
total = jpy_of(recs)
kind = collections.defaultdict(float)
for r in recs:
    p = r.get("provider")
    k = {"gemini": "TTS(gemini)", "gemini_batch": "TTS(gemini batch)", "openai_asr": "ASR(openai)", "azure": "ASR(azure secondary)",
         "openai": "LLM(openai)"}.get(p, f"other({p})")
    kind[k] += jpy_of([r])
stage_log = load(f"{A.run_dir}/e2e_stage_log.jsonl")
out = {
    "source": f"{A.run_dir}/cost_log.jsonl(実測usage x pricing_snapshot単価。runner budget guardと同一関数)",
    "n_records": len(recs), "total_jpy_measured": round(total, 4), "cap_jpy": A.cap, "remaining_vs_cap_jpy": round(A.cap - total, 4),
    "stages": stages, "by_kind_jpy": {k: round(v, 4) for k, v in sorted(kind.items())},
    "web_search_calls_total": sum(s["web_search_calls"] for s in stages.values()),
    "usage_not_obtained_total": sum(s["usage_not_obtained"] for s in stages.values()),
    "failed_calls_total": sum(s["failed_calls"] for s in stages.values()),
    "runner_stage_log_spent_jpy_cumulative_last": (stage_log[-1].get("spent_jpy_cumulative") if stage_log else None),
    "classification": {"実測": "cost_log.jsonl usage(OFFICIAL_API_RESPONSE)を単価換算した値", "推定": "なし(本集計は推定値を含まない)",
                       "未取得": "usage_not_obtained_total件(0なら全件取得)"},
    "reference_other_frame_not_added": {},
}
root = os.path.dirname(A.run_dir.rstrip("/\\"))
for rn in A.ref_runs:
    rr = load(f"{root}/{rn}/cost_log.jsonl")
    out["reference_other_frame_not_added"][rn] = {"jpy": round(jpy_of(rr), 4) if rr else None, "note": "¥300枠(別枠)。本runの合計に加算しない"}
os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True)
json.dump(out, open(A.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=True, indent=1))
