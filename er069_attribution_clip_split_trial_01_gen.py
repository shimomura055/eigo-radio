# -*- coding: utf-8 -*-
"""Phase 2 TTS生成(Trial隔離。Production非経由。TTS Standard同期のみ)。
Master Store/HR/attempt_history/ledger/共有telemetryへは書かない(出力はer069_output/配下のみ)。
python er069_..._gen.py --plan <plan_01.json> --out-dir <gen dir> --budget-jpy 100 --no-telemetry
技術失敗は1 taskあたり1回・全体で最大3回まで。監督ループ・自動再起動なし。"""
import os, sys, json, time, glob, argparse, threading, hashlib, concurrent.futures as cf
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
import er057_tone_trial_final_build_03 as B     # TTS呼出・単価(Standard $0.5/$6.0 per 1M tok)の既存雛形
import er063_family_z_audio_01 as Z               # Production同一Style定数(読むだけ)

STOPALL = os.path.join(ROOT, "er026_output", "family_z_production_e2e_01", "STOP_ALL")
_l = threading.Lock()
_retries = {"n": 0}
MAX_TECH_RETRY_TOTAL = 3


def stop_present(out_dir):
    return (os.path.exists(os.path.join(out_dir, "STOP")) or os.path.exists(os.path.join(out_dir, "..", "STOP"))
            or os.path.exists(STOPALL)
            or bool(glob.glob(os.path.join(ROOT, "docs", "pm", "delegation_log", "*ATTRIBUTION-CLIP-SPLIT*STOP*"))))


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def run(task, call, out_dir, budget, styles, log_path, stopflag):
    import er002_common as common, er003_b1_p3u_audio as p3u
    import er008_a2_postprocess_slowdown_01 as slowdown
    jid = task["id"]
    if stopflag["stop"] or stop_present(out_dir):
        stopflag["stop"] = True
        return {"id": jid, "status": "STOP"}
    if B._spent["jpy"] > budget:
        stopflag["stop"] = True
        return {"id": jid, "status": "BUDGET_STOP"}
    style = styles[task["level"]]
    t0 = time.time()
    samples = usage = None
    for tech in (1, 2):
        try:
            samples, usage = call(task["text"], style, B.VOICE)
            break
        except Exception as e:
            rec = {"job": jid, "event": "TTS_TECH_FAILURE", "tech_try": tech, "error": f"{type(e).__name__}: {str(e)[:200]}"}
            with _l:
                open(log_path, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
                _retries["n"] += 1
                ok = _retries["n"] <= MAX_TECH_RETRY_TOTAL
            if not ok:
                stopflag["stop"] = True
                break
    if samples is None:
        return {"id": jid, "status": "TECH_FAIL"}
    tts_jpy = ((usage["input_tokens"] or 0) * B.PRICE_IN + (usage["output_tokens"] or 0) * B.PRICE_OUT) / 1e6 * B.USD_JPY
    with B._lock:
        B._spent["jpy"] += tts_jpy
    trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE,
                                                   safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": jid, "name": task["name"], "boundary": task["boundary"],
           "length": task["length"], "level": task["level"], "take": task["take"], "text": task["text"],
           "model_requested": B.MODEL, "model_version": usage["model_version"], "voice": B.VOICE,
           "execution_mode": "STANDARD(sync, DEV Trial)", "style_sha256": sha(style),
           "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"],
           "verb": task.get("verb"), "vgroup": task.get("vgroup"), "nophrase": task.get("nophrase", False),
           "tts_cost_jpy": round(tts_jpy, 5), "tts_price_usd_per_m": [B.PRICE_IN, B.PRICE_OUT], "elapsed_s": round(time.time() - t0, 2)}
    if trimmed is None:
        rec["status"] = "NO_SPEECH"
    else:
        raw = os.path.join(out_dir, "wav", f"{jid}_raw.wav")
        common.write_wav_float(raw, trimmed, common.SAMPLE_RATE, 1)
        rec.update(status="OK", raw_wav=os.path.relpath(raw, ROOT).replace("\\", "/"), raw_sha256=B.sha_file(raw),
                   trimmed_duration_s=round(len(trimmed) / common.SAMPLE_RATE, 3))
        if task["level"] == "std":
            slow = os.path.join(out_dir, "wav", f"{jid}_slow6.wav")
            info = slowdown.apply_a2_slowdown(raw, slow)
            rec["slow_wav"] = os.path.relpath(slow, ROOT).replace("\\", "/")
            rec["slowdown"] = {k: info.get(k) for k in ("slowdown_pct_target", "slowdown_pct_actual", "src_duration_seconds", "dst_duration_seconds")}
    with _l:
        open(log_path, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {"id": jid, "status": rec["status"], "jpy": rec["tts_cost_jpy"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--budget-jpy", type=float, default=100.0)
    ap.add_argument("--no-telemetry", action="store_true", help="常時no-op(互換フラグ)。本scriptは共有telemetryへ書かない")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--run-tag", default="01", help="log/summaryファイル名のtag(委任_02は run02。既定01=委任_01互換)")
    a = ap.parse_args()
    out_dir = a.out_dir
    assert not stop_present(out_dir), "STOP present"
    os.makedirs(os.path.join(out_dir, "wav"), exist_ok=True)
    plan = json.load(open(a.plan, encoding="utf-8"))
    tasks = plan["tasks"][:a.limit] if a.limit else plan["tasks"]
    styles = {"adv": Z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_ADV"]["text"],
              "std": Z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_STD"]["text"]}
    log_path = os.path.join(out_dir, f"generation_log_{a.run_tag}.jsonl")
    done = set()
    if os.path.exists(log_path):
        for l in open(log_path, encoding="utf-8"):
            r = json.loads(l)
            if r.get("status") in ("OK", "NO_SPEECH"):
                done.add(r["job"])
    tasks = [t for t in tasks if t["id"] not in done]
    print("tasks to run:", len(tasks), "already done:", len(done), flush=True)
    call = B.make_tts_call()
    stopflag = {"stop": False}
    t0 = time.time()
    with cf.ThreadPoolExecutor(4) as ex:
        results = list(ex.map(lambda t: run(t, call, out_dir, a.budget_jpy, styles, log_path, stopflag), tasks))
    summ = {"n_tasks": len(tasks), "results": results, "tts_spent_jpy": round(B._spent["jpy"], 4),
            "retries_used": _retries["n"], "elapsed_s": round(time.time() - t0, 1)}
    json.dump(summ, open(os.path.join(out_dir, f"gen_summary_{a.run_tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r["status"] for r in results), "tts_spent_jpy", summ["tts_spent_jpy"], "elapsed", summ["elapsed_s"])


if __name__ == "__main__":
    main()
