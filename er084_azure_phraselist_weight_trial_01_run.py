# -*- coding: utf-8 -*-
"""Trial runner。条件マトリクス(design_matrix_01.json)を読み、追記型raw log(raw/azure_calls.jsonl)へ保存する。
`--phase A`のみ本委任で実走可。B/Cは委任_02(Fable照合後)で`--wav-manifest`を渡して実走する。
重みAPIはSDK PhraseListGrammar.setWeight。Production ASR設定は変更しない。
"""
import argparse
import json
import os
import sys
import time

import er005_cost_logger as cl
import er084_azure_phraselist_weight_trial_01_lib as L

ROOT = L.ROOT


def build_calls(design: dict, phase: str, wav_manifest: dict | None = None) -> list:
    """(audio_id, wav_path, cond, rep)の呼出リスト。rep外側ループ=条件を交互に回し時間ドリフトを均す。"""
    ph = design["phases"][phase]
    calls = []
    if phase == "A":
        reps = int(ph["reps"])
        for rep in range(1, reps + 1):
            for cond in design["conditions"]:
                for a in ph["audio"]:
                    calls.append({"audio_id": a["id"], "wav_path": a["path"], "cond": cond, "rep": rep,
                                  "sha256_expected": a.get("sha256")})
    else:
        if not wav_manifest:
            raise SystemExit(f"phase {phase}は--wav-manifest(委任_02で生成したwav一覧)が必要。委任_01では実走しない。")
        reps = int(wav_manifest.get("reps", 1))
        for rep in range(1, reps + 1):
            for cond in design["conditions"]:
                for a in wav_manifest["audio"]:
                    calls.append({"audio_id": a["id"], "wav_path": a["path"], "cond": cond, "rep": rep,
                                  "sha256_expected": a.get("sha256")})
    return calls


def estimate(calls: list) -> dict:
    secs = 0.0
    for c in calls:
        secs += L.wav_info(os.path.join(ROOT, c["wav_path"]))["duration_s"]
    return {"n_calls": len(calls), "audio_seconds": round(secs, 2), "est_jpy": round(L.est_jpy(secs), 3)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--phase", required=True, choices=["A", "B", "C"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--wav-manifest", default=None)
    a = ap.parse_args(argv)
    design = json.load(open(a.design, encoding="utf-8"))
    manifest = json.load(open(a.wav_manifest, encoding="utf-8")) if a.wav_manifest else None
    calls = build_calls(design, a.phase, manifest)
    est = estimate(calls)
    print(json.dumps({"phase": a.phase, "dry_run": a.dry_run, **est, "budget_jpy": a.budget_jpy}, ensure_ascii=False))
    if est["est_jpy"] > a.budget_jpy:
        print("見積がbudgetを超過 -> 実行しない", file=sys.stderr)
        return 2
    if a.dry_run:
        return 0
    out = os.path.abspath(a.out)
    raw = os.path.join(out, "raw", "azure_calls.jsonl")
    cl.init_logger(os.path.join(out, f"cost_log_phase_{a.phase}.jsonl"))
    phrases = design["phrase_list"]
    spent = 0.0
    consecutive_err = 0
    for i, c in enumerate(calls, 1):
        spec = L.cond_spec(c["cond"])
        wav_abs = os.path.join(ROOT, c["wav_path"])
        info = L.wav_info(wav_abs)
        if c.get("sha256_expected") and info["sha256"] != c["sha256_expected"]:
            print(f"sha256不一致: {c['wav_path']} -> 中止", file=sys.stderr)
            return 3
        if spent + L.est_jpy(info["duration_s"]) > a.budget_jpy:
            print(f"budget到達({spent:.3f}/{a.budget_jpy}) -> 停止", file=sys.stderr)
            return 4
        log_path = os.path.join(out, "sdk_logs", f"{a.phase}_{c['audio_id']}_{c['cond']}_r{c['rep']}.log")
        r = L.azure_transcribe(wav_abs, phrases if spec["use_pl"] else None, spec["weight"], sdk_log_path=log_path)
        ok = r["err"] is None
        spent += L.record_cost(a.phase, info, ok, r["elapsed_s"], c["cond"])
        ev = L.extract_weight_evidence(log_path)
        ev.pop("hits_head", None)
        row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "phase": a.phase, "seq": i, **c, "wav_sha256": info["sha256"],
               "duration_s": info["duration_s"], "use_pl": spec["use_pl"], "weight_requested": spec["weight"],
               "weight_call_made": r["weight_call"], "phrases": r["phrases"], "text": r["text"], "err": r["err"],
               "cls": L.classify_melos(r["text"]), "segments_json": r["segments_json"], "elapsed_s": r["elapsed_s"],
               "wire_evidence": ev, "sdk_log": os.path.relpath(log_path, ROOT)}
        L.append_raw(raw, row)
        print(f"[{i}/{len(calls)}] {c['cond']} r{c['rep']} err={r['err']} melos={row['cls']['melos']} wrong={row['cls']['wrong']} spent={spent:.3f}")
        consecutive_err = 0 if ok else consecutive_err + 1
        if consecutive_err >= 2:
            print("2連続error -> STOP", file=sys.stderr)
            return 5
    print(json.dumps({"done": True, "spent_jpy_est": round(spent, 3)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
