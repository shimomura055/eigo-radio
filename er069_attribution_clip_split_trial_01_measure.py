# -*- coding: utf-8 -*-
"""Phase 2 計測(ASR + Production判定)。Trial隔離: 共有telemetryはno-op化、出力はer069_output/配下のみ。
python er069_..._measure.py --gen-dir <gen> --out <results_01.json> --no-telemetry [--budget-jpy 100]"""
import os, sys, json, re, time, argparse, threading, concurrent.futures as cf
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
import er065_short_clip_asr_context_trial_01_lib as A


def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", (t or "").lower().replace("’", "'")).strip()


def patch_noop_telemetry():
    import er021_en_asr_semantic_equivalence_production_01 as semeq
    semeq.append_telemetry_log = lambda record, path=None: None


_wl = threading.Lock()


def measure_one(rec, target, wav_rel, val):
    path = os.path.join(ROOT, wav_rel)
    text, name = rec["text"], rec["name"]
    oa = A.openai_asr(path, logprobs=False)
    az = A.azure_asr(path, phrases=[name])
    with _wl:
        wh = A.whisper_asr(path, "small")
    row = {"job": rec["job"], "name": name, "boundary": rec["boundary"], "length": rec["length"], "level": rec["level"],
           "take": rec["take"], "target": target, "text": text, "duration_s": round(A.wav_duration(path), 3),
           "openai": {k: oa.get(k) for k in ("ok", "text", "input_tokens", "output_tokens", "jpy", "error")},
           "azure": {k: az.get(k) for k in ("ok", "text", "audio_seconds", "jpy", "error")},
           "whisper_small": {"ok": wh.get("ok"), "text": wh.get("text")}}
    row["openai_verified"] = False
    row["openai_class"] = None
    if oa.get("ok"):
        with _wl:
            verified, _stop, cls = val.evaluate_attempt(text, oa["text"], [], segment_id=rec["job"])
        row["openai_verified"] = bool(verified)
        row["openai_class"] = cls.classification
    row["azure_pass"] = False
    row["azure_class"] = None
    if az.get("ok"):
        c = val.classify_asr_match(text, az["text"], segment_id=rec["job"])
        row["azure_pass"] = bool(c.should_pass)
        row["azure_class"] = c.classification
    row["or_pass"] = row["openai_verified"] or row["azure_pass"]
    row["hr_proxy"] = not row["or_pass"]
    nm = name.lower()
    row["spell_openai"] = nm in norm(oa.get("text")).split() if oa.get("ok") else False
    row["spell_azure"] = nm in norm(az.get("text")).split() if az.get("ok") else False
    row["spell_whisper"] = nm in norm(wh.get("text")).split()
    row["cost_jpy"] = round((oa.get("jpy") or 0) + (az.get("jpy") or 0), 5)
    return row


def agg(rows, keyf):
    out = {}
    for r in rows:
        out.setdefault(keyf(r), []).append(r)
    res = {}
    for k, v in sorted(out.items()):
        n = len(v)
        res[k] = {"n": n, "openai_pass": sum(r["openai_verified"] for r in v), "azure_pass": sum(r["azure_pass"] for r in v),
                  "or_pass": sum(r["or_pass"] for r in v), "hr_proxy": sum(r["hr_proxy"] for r in v),
                  "spell_openai": sum(r["spell_openai"] for r in v), "spell_azure": sum(r["spell_azure"] for r in v),
                  "spell_whisper": sum(r["spell_whisper"] for r in v)}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-telemetry", action="store_true")
    ap.add_argument("--budget-jpy", type=float, default=100.0)
    a = ap.parse_args()
    patch_noop_telemetry()
    import er006_preprod_hardening_01_validation as val
    recs = [json.loads(l) for l in open(os.path.join(a.gen_dir, "generation_log_01.jsonl"), encoding="utf-8")]
    recs = [r for r in recs if r.get("status") == "OK"]
    gen_jpy = sum(r["tts_cost_jpy"] for r in recs)
    jobs = []
    for r in recs:
        jobs.append((r, "raw", r["raw_wav"]))
        if r["level"] == "std":
            jobs.append((r, "slow6", r["slow_wav"]))
    print("measure jobs:", len(jobs), "gen_jpy", round(gen_jpy, 3), flush=True)
    rows = []
    spent = {"jpy": gen_jpy}
    t0 = time.time()
    with cf.ThreadPoolExecutor(4) as ex:
        futs = [ex.submit(measure_one, r, tg, w, val) for r, tg, w in jobs]
        for f in cf.as_completed(futs):
            row = f.result()
            rows.append(row)
            spent["jpy"] += row["cost_jpy"]
            if spent["jpy"] > a.budget_jpy:
                print("BUDGET exceeded; stopping new submissions", flush=True)
                for g in futs:
                    g.cancel()
                break
    rows.sort(key=lambda r: (r["job"], r["target"]))
    res = {"n_obs": len(rows), "gen_tts_jpy": round(gen_jpy, 4), "asr_jpy_openai_text_price_azure_hourly": round(sum(r["cost_jpy"] for r in rows), 4),
           "total_jpy": round(spent["jpy"], 4), "elapsed_s": round(time.time() - t0, 1),
           "by_level_target_boundary_length": agg(rows, lambda r: f"{r['level']}|{r['target']}|{r['boundary']}|{r['length']}"),
           "by_level_target_boundary_length_OOV_only": agg([r for r in rows if r["name"] != "Kallis"],
                                                              lambda r: f"{r['level']}|{r['target']}|{r['boundary']}|{r['length']}"),
           "by_name_boundary_length": agg(rows, lambda r: f"{r['name']}|{r['boundary']}|{r['length']}"),
           "rows": rows}
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cost = {"tts_calls": [{"job": r["job"], "model_requested": r["model_requested"], "model_version": r["model_version"],
                           "input_tokens": r["input_tokens"], "output_tokens": r["output_tokens"], "jpy": r["tts_cost_jpy"],
                           "price_usd_per_m": r["tts_price_usd_per_m"]} for r in recs],
            "asr_calls": [{"job": r["job"], "target": r["target"], "openai_tokens": [r["openai"]["input_tokens"], r["openai"]["output_tokens"]],
                           "openai_jpy": r["openai"]["jpy"], "azure_seconds": r["azure"]["audio_seconds"], "azure_jpy": r["azure"]["jpy"]}
                          for r in rows],
            "totals": {"tts_jpy": round(gen_jpy, 4), "asr_jpy": res["asr_jpy_openai_text_price_azure_hourly"], "total_jpy": res["total_jpy"],
                       "note": "OpenAI ASRは音声入力tokenの正式単価が未確認(text単価USD1.25/Mで計上=過小の可能性)。Azureは$1.0/h(Retail Prices)。USD_JPY=160"},
            "tts_model_versions_observed": sorted({r["model_version"] for r in recs})}
    json.dump(cost, open(os.path.join(os.path.dirname(os.path.abspath(a.out)), "cost_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done", res["n_obs"], "obs; total_jpy", res["total_jpy"], flush=True)


if __name__ == "__main__":
    main()
