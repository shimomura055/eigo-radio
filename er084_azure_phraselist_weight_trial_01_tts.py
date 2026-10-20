# -*- coding: utf-8 -*-
"""FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02a: Phase B用wav生成(Trial専用)。

Production Z narrator経路(flash-lite speech_metadata + PD06 style)と同じ低レベル関数を呼ぶ:
  er033 resolve_tts_call_and_prompt -> er002_common._call_tts_with_retry -> er003_b1_p3u_audio.trim_english_keyword_silence(0.35)
  -> er002_common.write_wav_float。入力文は er003_v1_n3_01_tts_generate.tts_safe_news_en を通す。
減速は er008_a2_postprocess_slowdown_01.apply_a2_slowdown(ffmpeg atempo 6%)のみ(ASR再検証/ログ副作用のある量産関数は使わない)。
Production run dirには書かない。Charonも設計書§2-Bどおりflash-lite+PD06(Production Charonは対話経路[Dialogue Style]で別model: 制約として記録)。
出力: <out>/<id>.wav と <out>/manifest_01.json(固定)。wavはcommitしない。
"""
import argparse
import hashlib
import json
import os
import sys
import time

import er005_cost_logger as cl
import er084_azure_phraselist_weight_trial_01_lib as L

MODEL = "gemini-3.8-flash-lite-tts"
STYLE_LABEL = "PD06"
# 負例のconfusable語 -> Melos 置換(設計書§2-B、実走前に固定)
NEG_CONFUSABLE = {"N1_mellow": "mellow", "N2_mellows": "mellows", "N3_mello": "Mello", "N4_milos": "Milos"}


def build_plan(design: dict) -> dict:
    """設計書から生成計画(TTS takeリストと減速リスト)を作る。純関数(API 0)。"""
    b = design["phases"]["B"]
    sents = [(s, "positive") for s in b["sentences_positive"]] + [(s, "negative") for s in b["sentences_negative"]]
    takes, slows = [], []
    for s, label in sents:
        canon = s["text"]
        if label == "negative":
            conf = NEG_CONFUSABLE[s["id"]]
            assert conf in canon, (s["id"], conf)
            canon = canon.replace(conf, "Melos")
        for voice in b["voices"]:
            for t in range(1, int(s["takes_per_voice"]) + 1):
                wid = f"{s['id']}_{voice}_take{t}"
                takes.append({"id": wid, "sentence_id": s["id"], "label": label, "voice": voice, "take": t,
                              "text": s["text"], "canonical_text": canon, "slow6": False,
                              "confusable": NEG_CONFUSABLE.get(s["id"]),
                              "expected_melos": len(L.RE_MELOS.findall(canon))})
                if "slow6pct" in b["speed_variants"].get(voice, []):
                    slows.append({"id": wid + "_slow6", "base_id": wid, "sentence_id": s["id"], "label": label,
                                  "voice": voice, "take": t, "text": s["text"], "canonical_text": canon, "slow6": True,
                                  "confusable": NEG_CONFUSABLE.get(s["id"]),
                                  "expected_melos": len(L.RE_MELOS.findall(canon))})
    return {"takes": takes, "slows": slows, "n_tts": len(takes), "n_slow": len(slows), "n_wav": len(takes) + len(slows)}


def generate_take(entry: dict, out_dir: str) -> dict:
    import er002_common as common
    import er003_b1_p3u_audio as p3u
    import er003_b1_p9a_audio as p9a
    import er019_family_x_style_profile_01 as prof
    import er033_tts_flash_lite_backend_wiring_01 as flw
    import er003_v1_n3_01_tts_generate as n3
    out_path = os.path.join(out_dir, entry["id"] + ".wav")
    call_fn, prompt = flw.resolve_tts_call_and_prompt(
        n3.tts_safe_news_en(entry["text"]), prof.PD06_TEXT, MODEL, entry["voice"], out_path,
        tts_backend=flw.BACKEND_SPEECH_METADATA_FLASH_LITE)
    pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"ok": False, "err": err, "retries": retries}
    samples = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples, common.SAMPLE_RATE, safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"ok": False, "err": "発話区間を検出できませんでした", "retries": retries}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    return {"ok": True, "retries": retries, "raw_duration_seconds": trim_info.get("raw_duration_seconds")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--tts-execution-mode", required=True, choices=["STANDARD"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if os.environ.get("TTS_EXECUTION_MODE", "").strip().upper() != "STANDARD":
        print("TTS_EXECUTION_MODE=STANDARD が環境変数に必要(Batch不使用)", file=sys.stderr)
        return 2
    design = json.load(open(a.design, encoding="utf-8"))
    plan = build_plan(design)
    est = plan["n_tts"] * 0.3
    print(json.dumps({"n_tts": plan["n_tts"], "n_slow": plan["n_slow"], "n_wav": plan["n_wav"],
                      "est_tts_jpy": round(est, 2), "budget_jpy": a.budget_jpy, "dry_run": a.dry_run}))
    if est > a.budget_jpy:
        return 2
    if a.dry_run:
        return 0
    import er008_a2_postprocess_slowdown_01 as slow
    import er019_family_x_style_profile_01 as prof
    out_dir = os.path.abspath(a.out)
    os.makedirs(out_dir, exist_ok=True)
    cl.install(os.path.join(os.path.dirname(out_dir), "cost_log_phase_B_tts.jsonl"))
    consecutive_err, calls = 0, 0
    with cl.logging_context(L.THEME_TAG, "phase_B_tts"):
        for e in plan["takes"]:
            path = os.path.join(out_dir, e["id"] + ".wav")
            if os.path.exists(path):  # 既存wavは再生成しない(費用二重化防止)
                continue
            if calls >= plan["n_tts"]:
                print("呼出数上限到達 -> 停止", file=sys.stderr)
                return 4
            calls += 1
            t0 = time.time()
            r = generate_take(e, out_dir)
            print(f"[{calls}/{plan['n_tts']}] {e['id']} ok={r['ok']} retries={r.get('retries')} err={r.get('err')} "
                  f"{round(time.time() - t0, 1)}s")
            consecutive_err = 0 if r["ok"] else consecutive_err + 1
            if consecutive_err >= 2:
                print("2連続error -> STOP", file=sys.stderr)
                return 5
    slow_res = {}
    for s in plan["slows"]:
        src = os.path.join(out_dir, s["base_id"] + ".wav")
        dst = os.path.join(out_dir, s["id"] + ".wav")
        if not os.path.exists(src):
            print(f"減速元なし: {src}", file=sys.stderr)
            return 6
        slow_res[s["id"]] = slow.apply_a2_slowdown(src, dst)
    audio = []
    for e in plan["takes"] + plan["slows"]:
        p = os.path.join(out_dir, e["id"] + ".wav")
        if not os.path.exists(p):
            print(f"wav欠落: {e['id']}", file=sys.stderr)
            return 7
        info = L.wav_info(p)
        audio.append({"id": e["id"], "path": os.path.relpath(p, L.ROOT).replace("\\", "/"), **info,
                      "voice": e["voice"], "model": MODEL, "style_label": STYLE_LABEL,
                      "style_prefix_sha256": prof.PD06_SHA256, "tts_execution_mode": "STANDARD",
                      "take": e["take"], "sentence_id": e["sentence_id"], "label": e["label"], "text": e["text"],
                      "canonical_text": e["canonical_text"], "expected_melos": e["expected_melos"],
                      "confusable": e["confusable"], "slow6": e["slow6"], "base_id": e.get("base_id"),
                      "slowdown_actual_pct": (slow_res.get(e["id"]) or {}).get("slowdown_pct_actual")})
    manifest = {"trial_id": L.TRIAL_ID, "manifest_version": "01(固定。以後不変。Phase B/Cはこのmanifestのみ参照)",
                "generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "n_tts": plan["n_tts"], "n_slow": plan["n_slow"],
                "n_audio": len(audio),
                "constraint_note": ("Charonもナレーター経路(flash-lite+PD06)で生成。Production ZのCharonは対話経路"
                                    "(gemini-2.5-pro-preview-tts・Dialogue Style)のため、Charon結果はProduction対話経路の再現ではない。"),
                "audio": audio}
    json.dump(manifest, open(os.path.join(out_dir, "manifest_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"done": True, "n_audio": len(audio)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
