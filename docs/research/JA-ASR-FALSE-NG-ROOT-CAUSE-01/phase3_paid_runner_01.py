# -*- coding: utf-8 -*-
"""Phase 3 有料部分 runner (準備のみ。本委任では有料callを1回も実行していない)。DEV専用・Production非import(逆方向も無し)。
既定=`plan`(API 0)。`run`は PHASE3_GO.json (Fable発行) が無ければ何もせず rc=4 で終了する(副作用0: ファイル作成0・API呼出0)。
ルール(PM_GOVERNANCE 26節): stop_scope_check rc=3で停止 / 自動再試行・ラッパ禁止 / 1起動=1 stage / Cap到達で停止 / 失敗したら再起動せず報告。
使い方:
  py docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/phase3_paid_runner_01.py plan
  py docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/phase3_paid_runner_01.py run --stage A1_azure_moon
Stage: A1_azure_moon / A2_openai_moon_x3 / A3_azure_flip / N3_tts / N3_asr / O1_format_prompt
"""
from __future__ import annotations
import argparse, glob, json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MANAGED_ID = "JA-ASR-FALSE-NG-ROOT-CAUSE-01"
RD = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01"
GO_FILE = f"{RD}/PHASE3_GO.json"
RUN_DIR = f"{RD}/phase3_run"
CAP_JPY_MAX = 60.0
AZURE_JPY_PER_SEC = 0.0447     # BUDGET_PLAN_01: review_lock_state.json 実測(5.96s=0.2667円)
OPENAI_JPY_PER_SEC = 0.0008    # 公表単価ベース概算(実測はraw_usage_logで確認)
TTS_JPY_PER_CLIP = (0.3, 1.0)  # 中央0.6
STAGES = {
    "A1_azure_moon": {"desc": "月題 attempt1/3 既存wav にAzure 各1回 (B-light保留の情報取得のみ)", "n": 2, "sec": 7.0, "kind": "azure"},
    "A2_openai_moon_x3": {"desc": "月題3 wav をOpenAI(gpt-4o-mini-transcribe)で各3回再転写 (数詞崩れの再現性)", "n": 9, "sec": 7.0, "kind": "openai"},
    "A3_azure_flip": {"desc": "v1 flip集合のうちAzure転写が無いwav (P-2/P-3の推定正例確認)", "n": 3, "sec": 12.0, "kind": "azure"},
    "N3_tts": {"desc": "N-3 負例30 clipのTTS生成 (Production JA snippet経路=p9a.generate_narration_snippet speech_metadata_flash_lite)", "n": 30, "sec": 0, "kind": "tts"},
    "N3_asr": {"desc": "N-3 30 clip を OpenAI(Primary)とAzure(Secondary)で転写", "n": 30, "sec": 6.0, "kind": "asr2"},
    "O1_format_prompt": {"desc": "O1: 汎用書式prompt(原稿内容を含まない)とgpt-4o-transcribeで月題3 wavのJA数詞整形を並置 (採用判断は別)", "n": 6, "sec": 7.0, "kind": "openai"},
}


def estimate(name: str) -> tuple[float, float]:
    s = STAGES[name]
    if s["kind"] == "azure":
        v = s["n"] * s["sec"] * AZURE_JPY_PER_SEC; return v, v * 1.3
    if s["kind"] == "openai":
        v = s["n"] * s["sec"] * OPENAI_JPY_PER_SEC; return v, max(v * 2, 0.5)
    if s["kind"] == "tts":
        return s["n"] * sum(TTS_JPY_PER_CLIP) / 2, s["n"] * TTS_JPY_PER_CLIP[1]
    v = s["n"] * s["sec"] * (AZURE_JPY_PER_SEC + OPENAI_JPY_PER_SEC); return v, v * 1.3


def plan() -> dict:
    rows, tot_m, tot_u = [], 0.0, 0.0
    for k, s in STAGES.items():
        m, u = estimate(k)
        rows.append({"stage": k, "desc": s["desc"], "calls": s["n"], "est_median_jpy": round(m, 2), "est_upper_jpy": round(u, 2)})
        tot_m += m; tot_u += u
    return {"managed_id": MANAGED_ID, "stages": rows, "total_median_jpy": round(tot_m, 2), "total_upper_jpy": round(tot_u, 2),
            "cap_jpy": CAP_JPY_MAX, "go_file": GO_FILE, "go_present": os.path.exists(os.path.join(ROOT, GO_FILE))}


def require_go(stage: str) -> dict:
    """GOが無い/不正なら SystemExit(4)。この関数より前に、ファイル作成・API呼出・stop check subprocessを一切行わない。"""
    p = os.path.join(ROOT, GO_FILE)
    if not os.path.exists(p):
        raise SystemExit(4)
    with open(p, encoding="utf8") as f:
        go = json.load(f)
    if go.get("managed_id") != MANAGED_ID or not go.get("cap_jpy") or float(go["cap_jpy"]) > CAP_JPY_MAX:
        raise SystemExit(4)
    if stage not in go.get("stages", []):
        raise SystemExit(4)
    return go


def stop_check() -> None:
    os.makedirs(os.path.join(ROOT, RUN_DIR), exist_ok=True)
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID, "--run-dir", RUN_DIR,
                        "--out", f"{RUN_DIR}/stop_check.json"], cwd=ROOT)
    if r.returncode == 3:
        raise SystemExit("[STOP] stop_scope_check rc=3 (新規API呼出をしない)")
    if r.returncode != 0:
        raise SystemExit(f"[STOP] stop_scope_check rc={r.returncode}")


def _spent(path: str) -> float:
    if not os.path.exists(path):
        return 0.0
    tot = 0.0
    with open(path, encoding="utf8") as f:
        for ln in f:
            try:
                tot += float(json.loads(ln).get("est_jpy", 0) or 0)
            except Exception:
                pass
    return tot


def _append(path: str, rec: dict) -> None:
    with open(path, "a", encoding="utf8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_stage(stage: str, *, azure_fn=None, openai_fn=None, tts_fn=None) -> dict:
    """azure_fn/openai_fn/tts_fn はtest用injection。本番(None)のときだけ実APIを使う。GOは常に必須。"""
    go = require_go(stage)
    live = azure_fn is None and openai_fn is None and tts_fn is None
    if live:
        stop_check()
    cap = float(go["cap_jpy"])
    os.makedirs(os.path.join(ROOT, RUN_DIR), exist_ok=True)
    log = os.path.join(ROOT, RUN_DIR, "usage_log.jsonl")
    sys.path.insert(0, ROOT)
    if live:
        from dotenv import load_dotenv
        load_dotenv()
        import er005_cost_logger as _cl
        _cl.init_logger(os.path.join(ROOT, RUN_DIR, "raw_usage_log.jsonl"))  # 委任_03: A1初回でinit未実施のRuntimeErrorを検出し追加(live経路の欠陥修正)
        import er007_ja_secondary_asr_01 as sec
        import er006_asr_provider_routing_01 as asr
        azure_fn = azure_fn or (lambda wav: sec._azure_stt_strict(wav, language="ja-JP"))
        openai_fn = openai_fn or (lambda wav, model="gpt-4o-mini-transcribe", prompt=None: asr._transcribe_openai_mini(wav, "ja", model, prompt=prompt))
        if stage == "N3_tts" and tts_fn is None:
            import er003_b1_p9a_audio as p9a
            tts_fn = lambda text, out: p9a.generate_narration_snippet(text, "ja", out, tts_backend="speech_metadata_flash_lite")
    items = _stage_items(stage)
    results = []
    for it in items:
        if _spent(log) >= cap:
            raise SystemExit(f"[STOP] Cap {cap}円到達")
        t0 = time.time()
        rec = {"stage": stage, "item": it["id"], "model": it.get("model")}
        if stage == "N3_tts":
            os.makedirs(os.path.dirname(it["out"]), exist_ok=True)  # 委任_03: n3出力dir未作成でwav書込失敗したため追加
            r = tts_fn(it["tts_input"], it["out"]); rec.update(result=str(r)[:200], est_jpy=sum(TTS_JPY_PER_CLIP) / 2)
        elif STAGES[stage]["kind"] == "azure":
            t, e = azure_fn(it["wav"]); rec.update(text=t, error=e, est_jpy=it.get("sec", 7.0) * AZURE_JPY_PER_SEC)
        elif stage == "N3_asr":
            t, e = openai_fn(it["wav"]); t2, e2 = azure_fn(it["wav"])
            rec.update(openai_text=t, openai_error=e, azure_text=t2, azure_error=e2,
                       est_jpy=6.0 * (OPENAI_JPY_PER_SEC + AZURE_JPY_PER_SEC))
        else:
            t, e = openai_fn(it["wav"], model=it.get("model", "gpt-4o-mini-transcribe"), prompt=it.get("prompt"))
            rec.update(text=t, error=e, est_jpy=7.0 * OPENAI_JPY_PER_SEC)
        rec["elapsed_s"] = round(time.time() - t0, 2)
        _append(log, rec); results.append(rec)
        if rec.get("error") or rec.get("openai_error") or rec.get("azure_error"):
            raise SystemExit(f"[STOP] {it['id']} エラー。再起動せずFableへ報告: {rec}")   # 自動再試行しない
    return {"stage": stage, "n": len(results)}


def _stage_items(stage: str) -> list:
    """stageごとの対象。wavパスは実行時にglob(月題3 wavはtts_generation_results/attempts sha一致で特定。Fableの委任で確定)。"""
    if stage.startswith("N3_"):
        clips = json.load(open(os.path.join(ROOT, RD, "n3_clips_01.json"), encoding="utf8"))
        outs = lambda c: f"{RUN_DIR}/n3/{c['id']}.wav"
        return [{"id": c["id"], "tts_input": c["tts_input"], "out": os.path.join(ROOT, outs(c)), "wav": os.path.join(ROOT, outs(c))} for c in clips]
    moon = sorted(glob.glob(os.path.join(ROOT, "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/narration/attempts/japanese_title_attempt*.wav")))
    if stage == "A1_azure_moon":
        return [{"id": os.path.basename(w), "wav": w} for w in moon if "attempt2" not in w][:2]
    if stage == "A2_openai_moon_x3":
        return [{"id": f"{os.path.basename(w)}#{k}", "wav": w} for w in moon for k in range(3)]
    if stage == "O1_format_prompt":
        gen = "数字は算用数字で書いてください。"  # 原稿内容を含まない汎用書式指示のみ
        out = []
        for w in moon:
            out.append({"id": f"{os.path.basename(w)}#fmtprompt", "wav": w, "model": "gpt-4o-mini-transcribe", "prompt": gen})
            out.append({"id": f"{os.path.basename(w)}#gpt-4o-transcribe", "wav": w, "model": "gpt-4o-transcribe"})
        return out
    if stage == "A3_azure_flip":
        o = json.load(open(os.path.join(ROOT, RD, "eval_api0_v1_01.out.json"), encoding="utf8"))
        files = sorted({f["file"].replace(".json", ".wav") for f in o["p3_flips"] + o["p4"]["flips"] if f.get("where", "primary") == "primary"})
        return [{"id": os.path.basename(f), "wav": os.path.join(ROOT, f)} for f in files if os.path.exists(os.path.join(ROOT, f))]
    return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    sp.add_parser("plan")
    r = sp.add_parser("run"); r.add_argument("--stage", required=True, choices=list(STAGES))
    a = ap.parse_args(argv)
    if a.cmd == "run":
        print(json.dumps(run_stage(a.stage), ensure_ascii=False)); return 0
    print(json.dumps(plan(), ensure_ascii=False, indent=1)); return 0


if __name__ == "__main__":
    sys.exit(main())
