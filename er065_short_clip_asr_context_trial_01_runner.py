# -*- coding: utf-8 -*-
"""FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01 runner(Trial/DEV only)。

jobspec(JSON)に従い、conditions_manifestの結合音声に対して指定ASRエンジンを実行し、生結果をJSONLへ追記する。
Production ASR helper(telemetry/queue/ledger追記経路を持つもの)は呼ばず、lib内の読取専用実装を使う。
write guard(sys.addaudithook)で、trial dir外への書込は例外で遮断し、実行前後でProduction stateの行数/ハッシュを記録する。

jobspec形式: {"engine":"openai|azure|whisper","reps":2,"threads":3,
              "items":[{"manifest":"<path>","targets":"all|[ids]","recipes":"all|[ids]","reps":n,
                        "variant":"base|prompt_word|prompt_prev|prompt_glossary|nophrase","whisper_model":"small"}]}

使い方:
  python er065_short_clip_asr_context_trial_01_runner.py --jobspec <jobspec.json> --out-dir <trial dir> --cost-cap-jpy <n>
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er065_short_clip_asr_context_trial_01_lib as L

GUARDED = [
    "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
    "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl",
    "er011_output/attempt_history.jsonl",
    "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
    "er006_output/master_audio_store_01/manifest.json",
    "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
    "er006_output/pronunciation_ledger_01/ledger.json",
    "er005_output/cost_baseline_01/cost_summary.json",
    "er026_output/family_z_production_e2e_01/melos/run_e2e_02/cost_log.jsonl",
    "er026_output/family_z_production_e2e_01/melos/COST_LEDGER_MELOS_01.md",
]


def fingerprints():
    return {p: L.file_fingerprint(p) for p in GUARDED}


def check_stop(out_dir):
    for pat in ["docs/pm/delegation_log/*STOP_NOTICE*", out_dir + "/STOP", "er026_output/family_z_production_e2e_01/STOP_ALL"]:
        # STOP_NOTICEは過去runの通知(別管理ID)。本Trial固有STOPとSTOP_ALLのみ停止対象にする
        if "STOP_NOTICE" in pat:
            continue
        if glob.glob(pat):
            return pat
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobspec", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--cost-cap-jpy", type=float, required=True, help="このprocessの上限(JPY)")
    ap.add_argument("--global-cap-jpy", type=float, default=38.0, help="trial全体(cost_01_*.jsonl合計)の上限")
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()

    spec = json.load(open(a.jobspec, encoding="utf-8"))
    engine = spec["engine"]
    tag = a.tag or os.path.splitext(os.path.basename(a.jobspec))[0]
    out_dir = a.out_dir
    import tempfile
    L.install_write_guard([out_dir, tempfile.gettempdir()])  # OS tempはASRライブラリの一時ファイル用(Production stateではない)
    res_path = os.path.join(out_dir, f"results_01_{tag}.jsonl")
    cost = L.CostLog(os.path.join(out_dir, f"cost_01_{tag}.jsonl"))
    before = fingerprints()
    json.dump({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "files": before},
              open(os.path.join(out_dir, f"telemetry_guard_before_{tag}.json"), "w", encoding="utf-8"), indent=1)

    done_keys = set()
    if os.path.exists(res_path):
        for line in open(res_path, encoding="utf-8"):
            try:
                done_keys.add(json.loads(line)["job_id"])
            except Exception:
                pass

    jobs = []
    for it in spec["items"]:
        man = json.load(open(it["manifest"], encoding="utf-8"))
        for rep in range(int(it.get("rep_start", 1)), int(it.get("rep_start", 1)) + int(it.get("reps", spec.get("reps", 1)))):
            for c in man["conditions"]:
                if it.get("targets", "all") != "all" and c["target_id"] not in it["targets"]:
                    continue
                if it.get("recipes", "all") != "all" and c["recipe_id"] not in it["recipes"]:
                    continue
                variant = it.get("variant", "base")
                jid = f"{engine}|{c['cond_id']}|{variant}|{it.get('whisper_model','')}|rep{rep}"
                if jid in done_keys:
                    continue
                jobs.append((jid, c, variant, rep, it))
    print(f"[{tag}] engine={engine} jobs={len(jobs)} cap={a.cost_cap_jpy}", flush=True)

    lock = threading.Lock()
    state = {"n_done": 0, "stop": None, "consec_err": 0}
    t_start = time.time()

    def do(job):
        jid, c, variant, rep, it = job
        if state["stop"]:
            return
        why = check_stop(out_dir)
        if why:
            state["stop"] = f"STOP sentinel: {why}"
            return
        total_all = sum(L.CostLog(p).total_jpy for p in glob.glob(os.path.join(out_dir, "cost_01_*.jsonl")))
        if cost.total_jpy >= a.cost_cap_jpy or total_all >= a.global_cap_jpy:
            state["stop"] = f"cost cap reached: proc={cost.total_jpy:.2f} all={total_all:.2f}"
            return
        wav = c["wav"]
        params = {}
        if engine == "openai":
            prompt = None
            if variant == "prompt_word":
                prompt = c["focus_word"]
            elif variant == "prompt_glossary":
                prompt = f"Proper noun in this story: {c['focus_word']}."
            elif variant == "prompt_prev":
                prev = " ".join(p["text"] for p in c["parts"][:c["target_index"]]) or f"{c['focus_word']}."
                prompt = prev
            params = {"prompt": prompt}
            r = L.openai_asr(wav, prompt=prompt)
        elif engine == "azure":
            phrases = None if variant == "nophrase" else [c["focus_word"]]
            params = {"phrases": phrases}
            r = L.azure_asr(wav, phrases=phrases)
        elif engine == "whisper":
            m = it.get("whisper_model", "small")
            params = {"model": m}
            r = L.whisper_asr(wav, model=m)
        else:
            raise SystemExit("unknown engine")
        rec = {"job_id": jid, "cond_id": c["cond_id"], "target_id": c["target_id"], "recipe_id": c["recipe_id"],
               "group": c.get("group"), "engine": r.get("engine", engine), "variant": variant, "rep": rep,
               "params": params, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "total_sec": c["total_sec"], "result": r}
        with lock:
            with open(res_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            cost.add({"engine": r.get("engine", engine), "job_id": jid, "jpy": r.get("jpy", 0.0),
                      "audio_seconds": c["total_sec"], "ts": rec["ts"],
                      "tokens_in": r.get("input_tokens"), "tokens_out": r.get("output_tokens"),
                      "pricing_source": "er005_output/cost_baseline_01/pricing_snapshot.json (gpt-4o-mini-transcribe 1.25/5.0 USD per M tok; azure STT 1.0 USD/audio-hour); USD/JPY=160"})
            state["n_done"] += 1
            if not r.get("ok"):
                state["consec_err"] += 1
                if state["consec_err"] >= 4:
                    state["stop"] = f"4 consecutive ASR errors: {r.get('error')}"
            else:
                state["consec_err"] = 0
            if state["n_done"] % 20 == 0:
                print(f"[{tag}] done={state['n_done']} cost={cost.total_jpy:.3f} elapsed={time.time()-t_start:.0f}s", flush=True)

    threads = int(spec.get("threads", 1))
    if threads <= 1:
        for j in jobs:
            do(j)
    else:
        with cf.ThreadPoolExecutor(max_workers=threads) as ex:
            list(ex.map(do, jobs))

    after = fingerprints()
    changed = {p: {"before": before[p], "after": after[p]} for p in GUARDED
               if (before[p].get("lines"), before[p].get("sha256")) != (after[p].get("lines"), after[p].get("sha256"))}
    json.dump({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "files": after, "changed_during_run": changed,
               "write_guard": L.write_guard_report(), "stop_reason": state["stop"],
               "n_done": state["n_done"], "cost_jpy_this_process": round(cost.total_jpy, 4),
               "elapsed_sec": round(time.time() - t_start, 1)},
              open(os.path.join(out_dir, f"telemetry_guard_after_{tag}.json"), "w", encoding="utf-8"), indent=1)
    print(f"[{tag}] finished n_done={state['n_done']} cost={cost.total_jpy:.3f} stop={state['stop']} "
          f"changed_guarded_files={list(changed)} blocked_writes={L.write_guard_report()['blocked_write_attempts']}", flush=True)


if __name__ == "__main__":
    main()
