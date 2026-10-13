# state不変確認(1回実行の補助): Trial/評価の前後で、Production ASR helperが追記しうる
# telemetry/queue/ledger/履歴の 行数+sha256 を記録する。評価はimportして同一プロセス内で1回だけ実行。
import glob, hashlib, io, json, os, contextlib, sys, time
sys.path.insert(0, ".")
OUT = "er066_output/ja_asr_orthographic_equivalence_01"
WATCH = [
    "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
    "er006_output/pronunciation_ledger_01/ledger.json",
    "er006_output/master_audio_store_01/manifest.json",
    "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
    "er011_output/attempt_history.jsonl",
    "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
    "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl",
    "er005_output/cost_baseline_01/cost_summary.json",
]
WATCH += sorted(glob.glob("er0*_output/**/telemetry.jsonl", recursive=True))[:200]


def snap():
    d = {}
    for p in dict.fromkeys(WATCH):
        if os.path.exists(p):
            b = open(p, "rb").read()
            d[p] = {"lines": b.count(b"\n"), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
        else:
            d[p] = None
    return d


before = snap()
t0 = time.time()
import er066_ja_asr_orthographic_equivalence_01_eval as ev
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ev.main()
after = snap()
changed = [p for p in before if before[p] != after[p]]
json.dump({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "wall_seconds": round(time.time() - t0, 2),
           "watched_files": len(before), "changed_during_run": changed,
           "note": "並行実行中の別workerによる変更が混ざりうる。changedが空なら本タスクの評価run前後で完全不変。",
           "before": before, "after": after},
          open(f"{OUT}/state_guard_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("watched", len(before), "changed", changed)
