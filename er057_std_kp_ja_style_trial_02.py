# -*- coding: utf-8 -*-
"""STANDARD-KP-JA-TTS-STYLE-TRIAL-02 委任_01 Trial専用script(Production非経由・共有state不書込)。
Trial-01 scriptのコピー。J3=Coffee完成版既存wav再利用、P5=Trial-01既存wav再利用、P6〜P10=新規。
modes: --shared-sha TAG / --dry-run / --styles P6,P7 / --asr / --analyze / --build-page"""
import os, sys, json, time, hashlib, argparse, glob, shutil
sys.path.insert(0, os.getcwd())
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_RUN = f"{ROOT}/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/a2"
BASE_RES = f"{BASE_RUN}/audit/tts_generation_results.json"
USD_JPY = 160.0
PRICE_OUT_PER_M, PRICE_IN_PER_M = 6.0, 0.5
ASR_PRICE_IN, ASR_PRICE_OUT = 1.25, 5.0
JA_MARGIN = 0.35   # Production p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS(er057_tone_trial_kp_ja_gen_01と同一)

# 委任文の6 Prompt(逐語)
PROMPTS = {
 "J3": "落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。演技がかった話し方は避けてください。",
 "P5": "落ち着いた、明瞭で自然な話し方で。短い言葉の意味を簡潔に、控えめな抑揚で読み上げてください。感情を強く込めたり、語尾を不必要に強調したりしないでください。",
 "P6": "落ち着いた、明瞭で自然な話し方で。短い言葉の意味を簡潔に、控えめながらも自然な抑揚を少し加えて読み上げてください。感情を強く込めたり、語尾を不必要に強調したりしないでください。",
 "P7": "落ち着いた、明瞭で自然な話し方で。短い言葉の意味を簡潔に伝えながら、普段の会話のような自然な抑揚と、ほんの少しの温かみを持たせてください。感情を強く込めたり、語尾を不必要に強調したりしないでください。",
 "P8": "落ち着いたニュースキャスターのように、明瞭で安定した声で読み上げてください。自然な抑揚を保ちながら、短い言葉の意味を端的に伝えてください。大げさな強調や演技的な感情表現は避けてください。",
 "P9": "落ち着いたPodcastホストのように、親しみやすく自然な会話調で読み上げてください。聞き手に意味を伝える程度の穏やかな抑揚と温かみを持たせてください。過剰な感情表現や大げさな語尾の変化は避けてください。",
 "P10": "穏やかで自然な音声ガイドのように、明瞭で聞き取りやすい声で読み上げてください。平板にならない程度の柔らかな抑揚をつけ、短い言葉の意味を落ち着いて伝えてください。感情的な演出や不必要な強調は避けてください。",
}
NAMES = {"J3": "現行Baseline", "P5": "前回P5(簡潔・淡々)", "P6": "P5+微弱な抑揚", "P7": "P5+自然な抑揚", "P8": "ニュースキャスター風", "P9": "Podcastホスト風", "P10": "穏やかな音声ガイド風"}
REUSE = ("J3", "P5")
T1 = f"{ROOT}/er057_output/std_kp_ja_style_trial_01"
EN = ["pump one's fist", "raw bean", "right away", "based on interviews", "take time"]

SHARED = ["er006_output/master_audio_store_01/manifest.json", "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
          "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", "er006_output/pronunciation_ledger_01/ledger.json",
          "er011_output/attempt_history.jsonl", "er005_output/cost_baseline_01/cost_summary.json"]
SHARED_GLOBS = ["er021_output/**/telemetry.jsonl", "er025_output/**/telemetry.jsonl", "er030_output/**/telemetry.jsonl",
                "er011_output/local_rewrite_recovery/**/*"]


def sha_b(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def sha_s(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


def shared_sha(out_dir, tag):
    d = {}
    for p in SHARED:
        fp = f"{ROOT}/{p}"; d[p] = sha_b(fp) if os.path.isfile(fp) else None
    for g in SHARED_GLOBS:
        for fp in sorted(glob.glob(f"{ROOT}/{g}", recursive=True)):
            if os.path.isfile(fp): d[os.path.relpath(fp, ROOT).replace("\\", "/")] = sha_b(fp)
    os.makedirs(f"{out_dir}/evidence", exist_ok=True)
    json.dump(d, open(f"{out_dir}/evidence/shared_state_sha_{tag}.json", "w", encoding="utf-8"), indent=1)
    print("shared sha", tag, len(d))


def baseline():
    d = json.load(open(BASE_RES, encoding="utf-8"))
    out = []
    for k in sorted(d["key_phrases"], key=int):
        j = d["key_phrases"][k]["japanese_meaning"]
        out.append({"idx": int(k), "en": EN[int(k) - 1], "canonical_text": j["canonical_text"], "tts_text": j["tts_input_text_after_reading_safety"],
                    "wav": f"{ROOT}/{j['path']}", "sha256": j["sha256"], "model": j["model"], "voice": j["voice"], "backend": j["tts_backend"],
                    "style_prefix": j["style_prefix"], "duration_s": j["duration_seconds"], "asr_text": j["asr_text"]})
    return out, d


def estimate(B):
    tot_s = sum(b["duration_s"] + 0.6 for b in B)
    tot_in = sum((len(b["tts_text"]) + len(PROMPTS["P7"])) / 2.0 + 20 for b in B)
    per = tot_s * 25 * PRICE_OUT_PER_M / 1e6 + tot_in * PRICE_IN_PER_M / 1e6
    return per * 5 * USD_JPY, per * USD_JPY  # 5 new styles


_client = None
def call_tts(text, style, voice, model_id):
    global _client
    import er033_tts_flash_lite_backend_wiring_01 as flw
    import er006_model_routing_contract_01 as rc
    import er002_gemini_client as gclient
    import er002_common as common
    from google.genai import types
    flw.assert_sdk_supports_speech_metadata()
    model = rc.require_model(flw.FAMILY_X_FLASH_LITE_TTS_PROCESS, model_id)
    if _client is None: _client = gclient.make_client()
    content = types.Content(parts=[types.Part(text=text, speech_metadata=types.SpeechMetadata(style=style))], role="user")
    resp = _client.models.generate_content(model=model, contents=content, config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(language_code=common.LANGUAGE_CODE, voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))),
        http_options=types.HttpOptions(timeout=gclient.TTS_TIMEOUT_MS)))
    parts = resp.candidates[0].content.parts
    raw = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
    if not raw: raise RuntimeError("empty audio")
    samples, fr = flw._decode_audio_defensive(raw)
    samples = flw._resample_to_common_rate(samples, fr)
    u = getattr(resp, "usage_metadata", None)
    usage = {"prompt_tokens": getattr(u, "prompt_token_count", None), "candidates_tokens": getattr(u, "candidates_token_count", None)} if u else None
    return samples, usage


def gen_style(style, out_dir, budget):
    import er002_common as common, er003_b1_p3u_audio as p3u
    B, _ = baseline()
    sd = f"{out_dir}/{style}"; os.makedirs(sd, exist_ok=True)
    rp = f"{sd}/results.jsonl"
    done = {}
    if os.path.exists(rp):
        for l in open(rp, encoding="utf-8"):
            r = json.loads(l); done[r["idx"]] = r
    spent = 0.0
    for b in B:
        if done.get(b["idx"], {}).get("status") == "OK": continue
        if spent > budget: print("BUDGET_STOP"); break
        out = f"{sd}/{style}_kp{b['idx']}.wav"; err = None; usages = []; calls = 0; rec = None
        for attempt in (1, 2):   # 技術失敗のみ最大1回retry(既存Trial script既定、合計2 call)
            calls += 1
            try:
                samples, usage = call_tts(b["tts_text"], PROMPTS[style], b["voice"], b["model"]); usages.append(usage)
                trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=JA_MARGIN)
                if trimmed is None: err = "no speech detected"; continue
                common.write_wav_float(out, trimmed, common.SAMPLE_RATE, 1)
                rec = {"idx": b["idx"], "style": style, "status": "OK", "text": b["tts_text"], "prompt_sha": sha_s(PROMPTS[style]),
                       "voice": b["voice"], "model": b["model"], "backend": b["backend"], "call_count": calls, "retry_count": calls - 1,
                       "duration_s": round(len(trimmed) / common.SAMPLE_RATE, 3), "raw_duration_s": ti["raw_duration_seconds"],
                       "usage": usages, "sha256": sha_b(out)}
                break
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
        if rec is None: rec = {"idx": b["idx"], "style": style, "status": "FAILED", "reason": err, "call_count": calls, "usage": usages}
        for u in usages:
            if u: spent += ((u.get("candidates_tokens") or 0) * PRICE_OUT_PER_M + (u.get("prompt_tokens") or 0) * PRICE_IN_PER_M) / 1e6 * USD_JPY
        done[b["idx"]] = rec
        print(style, b["idx"], rec["status"], rec.get("duration_s"), flush=True)
        with open(rp, "w", encoding="utf-8") as f:
            for i in sorted(done): f.write(json.dumps(done[i], ensure_ascii=False) + "\n")
    print(style, "spent_jpy_est", round(spent, 2))


def load_all(out_dir):
    R = {}
    for s in PROMPTS:
        if s in REUSE: continue
        p = f"{out_dir}/{s}/results.jsonl"
        R[s] = {json.loads(l)["idx"]: json.loads(l) for l in open(p, encoding="utf-8")} if os.path.exists(p) else {}
    return R


def wavpath(s, idx, out_dir, B):
    if s == "J3": return B[idx - 1]["wav"]
    if s == "P5": return f"{T1}/P5/P5_kp{idx}.wav"
    return f"{out_dir}/{s}/{s}_kp{idx}.wav"


def asr(out_dir):
    import er006_asr_provider_routing_01 as routing
    import er007_ja_asr_validator_01 as javal
    B, _ = baseline(); out = []
    for s in PROMPTS:
        if s in REUSE: continue
        for b in B:
            p = wavpath(s, b["idx"], out_dir, B)
            if not os.path.exists(p): continue
            t, err = routing.transcribe(p, language="ja-JP")
            c = javal.classify_ja_asr_match(b["tts_text"], t)
            dur = sf.info(p).duration
            cost = ((dur * 10) * ASR_PRICE_IN + (len(t or "") / 4.0) * ASR_PRICE_OUT) / 1e6 * USD_JPY
            out.append({"style": s, "idx": b["idx"], "canonical": b["tts_text"], "asr_text": t, "asr_error": err, "classification": c.classification,
                        "should_pass": bool(c.should_pass), "asr_cost_jpy_est": round(cost, 4)})
            print(s, b["idx"], c.classification, "|", t, flush=True)
    with open(f"{out_dir}/asr_results.jsonl", "w", encoding="utf-8") as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")


def metrics(x, sr):
    from scipy.signal import resample_poly, fftconvolve
    y = resample_poly(x, 16000, sr) if sr != 16000 else x
    fl, hop = 640, 160; f0, rms = [], []
    lo, hi = int(16000 / 400), int(16000 / 75)
    for i in range(0, len(y) - fl, hop):
        fr = y[i:i + fl]; r = float(np.sqrt(np.mean(fr ** 2))); rms.append(r); fr = fr - fr.mean()
        ac = fftconvolve(fr, fr[::-1])[fl - 1:]
        if ac[0] <= 0: f0.append(np.nan); continue
        ac = ac / ac[0]; k = lo + int(np.argmax(ac[lo:hi]))
        f0.append(16000 / k if ac[k] > 0.5 and r > 0.01 else np.nan)
    f0 = np.array(f0); rms = np.array(rms)
    act = rms > 0.02 * rms.max() if len(rms) and rms.max() > 0 else np.zeros(len(rms), bool)
    v = f0[~np.isnan(f0)]
    db = 20 * np.log10(rms[act] + 1e-9)
    st = 12 * np.log2(v / np.median(v)) if len(v) > 3 else np.array([np.nan])
    return {"duration_s": round(len(x) / sr, 3),
            "rms_dyn_db_p10_p90": round(float(np.percentile(db, 90) - np.percentile(db, 10)), 2) if len(db) else None,
            "silence_ratio": round(float(1 - act.mean()), 3) if len(act) else None,
            "f0_median_hz": round(float(np.median(v)), 1) if len(v) > 3 else None,
            "f0_std_st": round(float(np.nanstd(st)), 2) if len(v) > 3 else None,
            "f0_range_st_p10_p90": round(float(np.percentile(st, 90) - np.percentile(st, 10)), 2) if len(v) > 3 else None,
            "voiced_frames": int(len(v))}


def analyze(out_dir):
    B, _ = baseline(); M = {}
    for s in PROMPTS:
        for b in B:
            p = wavpath(s, b["idx"], out_dir, B)
            if not os.path.exists(p): continue
            x, sr = sf.read(p, dtype="float32"); x = x.mean(axis=1) if x.ndim > 1 else x
            M[f"{s}_kp{b['idx']}"] = metrics(x, sr)
    agg = {}
    for s in PROMPTS:
        for key in ("duration_s", "rms_dyn_db_p10_p90", "f0_std_st", "f0_range_st_p10_p90", "silence_ratio"):
            vals = [M[f"{s}_kp{i}"][key] for i in range(1, 6) if f"{s}_kp{i}" in M and M[f"{s}_kp{i}"][key] is not None]
            if vals: agg.setdefault(s, {})[key] = {"mean": round(float(np.mean(vals)), 3), "var": round(float(np.var(vals)), 4), "n": len(vals)}
    json.dump({"per_audio": M, "per_style": agg, "note": "参考値(機械指標)。合否基準ではなく、聴感評価の代替でもない。F0は自己相関法の簡易推定(pyworld/librosa未導入)"},
              open(f"{out_dir}/objective_metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("analyzed", len(M))


def build_page(out_dir, page_dir):
    import lameenc, html
    B, _ = baseline()
    au = f"{page_dir}/audio"; os.makedirs(au, exist_ok=True)
    asrr = {}
    for src in (f"{T1}/asr_results.jsonl", f"{out_dir}/asr_results.jsonl"):
        for l in open(src, encoding="utf-8"):
            r = json.loads(l); asrr[(r["style"], r["idx"])] = r
    for b in B: asrr[("J3", b["idx"])] = {"asr_text": b["asr_text"], "classification": "Production記録"}
    M = json.load(open(f"{out_dir}/objective_metrics.json", encoding="utf-8"))["per_audio"]
    reuse = {}
    def mp3(st, idx):
        dst = f"{au}/{st}_kp{idx}.mp3"
        if st in REUSE:   # 前回Trial-01のmp3をそのままcopy(sha一致を記録)
            src = f"{ROOT}/user_test/coffee_std_kp_ja_style_trial_01/audio/{st}_kp{idx}.mp3"
            shutil.copyfile(src, dst); reuse[f"{st}_kp{idx}"] = {"src": os.path.relpath(src, ROOT).replace("\\", "/"), "sha256_src": sha_b(src), "sha256_copy": sha_b(dst)}
            return
        x, sr = sf.read(wavpath(st, idx, out_dir, B), dtype="float64"); x = x.mean(axis=1) if x.ndim > 1 else x
        e = lameenc.Encoder(); e.set_bit_rate(96); e.set_in_sample_rate(sr); e.set_channels(1); e.set_quality(2)
        open(dst, "wb").write(e.encode((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()) + e.flush())
    h = ["<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
         "<title>Std Key Phrase 日本語意味 Style比較 試聴(第2弾)</title><style>body{font-family:sans-serif;max-width:1200px;margin:0 auto;padding:8px;line-height:1.5}"
         ".ph{border:1px solid #bbb;border-radius:6px;margin:14px 0;padding:8px}.row{display:flex;flex-wrap:wrap;gap:8px}"
         ".c{flex:1 1 150px;min-width:140px;border:1px solid #ddd;border-radius:4px;padding:6px;background:#fafafa}.c.base{background:#fff4d6;border-color:#d9a400}"
         ".c.re{background:#e8f1ff;border-color:#4a7bd0}.badge{display:inline-block;font-size:11px;background:#4a7bd0;color:#fff;border-radius:3px;padding:0 4px}"
         ".badge.y{background:#d9a400}audio{width:100%}.m{font-size:11px;color:#555}details{margin:6px 0}pre{white-space:pre-wrap;background:#f3f3f3;padding:6px}</style></head><body>"
         "<h1>Std Key Phrase 日本語意味 Style比較 試聴(第2弾)</h1>"
         "<p>STANDARD-KP-JA-TTS-STYLE-TRIAL-02 委任_01。試聴用の検証結果です(Productionへは未反映、採用は未決定)。まず先頭の「すぐに」の7案を聴き比べてください。"
         "前回あなたが「最も希望に近い」とした<b>P5</b>を基準に、少しだけ抑揚・温かみを足す候補(P6・P7中心、P8〜P10は比較用)です。"
         "<span class='badge y'>J3 既存音声の再利用</span>(黄)=Coffee完成版の実使用音声、<span class='badge'>P5 既存音声の再利用</span>(青)=前回Trial-01の音声そのもの。P6〜P10が今回の新規生成(各1 Take)です。"
         "同じ日本語テキスト・Aoede・gemini-3.8-flash-lite-tts・同じ後処理で、Style(読み方の指示)だけが異なります。各候補1 Takeのため、Styleの差と生成のゆらぎは厳密に分離できません。"
         "数値は参考の機械指標で、F0が大きい＝感情的、小さい＝自然、という意味ではなく、聴感評価の代替でもありません。</p>"]
    h.append("<details><summary>7 Prompt全文(逐語)</summary>")
    for st, pr in PROMPTS.items():
        tag = {"J3": "(完成版の実使用・既存音声再利用)", "P5": "(前回Trial・既存音声再利用)"}.get(st, "(今回新規)")
        h.append(f"<p><b>{st}｜{NAMES[st]}{tag}</b></p><pre>{html.escape(pr)}</pre>")
    h.append("</details>")
    order = [3, 1, 2, 4, 5]   # 「すぐに」を先頭
    for idx in order:
        b = B[idx - 1]
        h.append(f"<div class='ph'><h2>{b['idx']}. {html.escape(b['en'])} → {html.escape(b['canonical_text'])}{' ★まずここから' if idx == 3 else ''}</h2><div class='row'>")
        for st in PROMPTS:
            mp3(st, idx)
            m = M.get(f"{st}_kp{idx}", {}); a = asrr.get((st, idx))
            info = f"{m.get('duration_s','-')}秒 / F0 std={m.get('f0_std_st','-')}st / 無音比{m.get('silence_ratio','-')}"
            if a: info += f" / ASR: {html.escape(str(a['asr_text']))}({a['classification']})"
            cls = " base" if st == "J3" else (" re" if st == "P5" else "")
            bd = "<br><span class='badge y'>既存音声の再利用</span>" if st == "J3" else ("<br><span class='badge'>既存音声の再利用</span>" if st == "P5" else "")
            h.append(f"<div class='c{cls}'><b>{st}｜{NAMES[st]}</b>{bd}"
                     f"<audio controls preload='none' src='audio/{st}_kp{idx}.mp3'></audio><div class='m'>{info}</div></div>")
        h.append("</div></div>")
    h.append("</body></html>")
    open(f"{page_dir}/index.html", "w", encoding="utf-8").write(chr(10).join(h))
    os.makedirs(f"{out_dir}/J3_reuse", exist_ok=True); os.makedirs(f"{out_dir}/P5_reuse", exist_ok=True)
    json.dump({k: v for k, v in reuse.items() if k.startswith("P5")}, open(f"{out_dir}/P5_reuse/source_sha.json", "w"), indent=1)
    json.dump({"baseline": {f"J3_kp{b['idx']}": {"wav": os.path.relpath(b["wav"], ROOT).replace("\\", "/"), "wav_sha256_recorded": b["sha256"], "wav_sha256_actual": sha_b(b["wav"]),
              "style_prefix_sha": sha_s(b["style_prefix"]), "model": b["model"], "voice": b["voice"], "backend": b["backend"]} for b in B},
               "mp3": {k: v for k, v in reuse.items() if k.startswith("J3")}}, open(f"{out_dir}/J3_reuse/source_sha.json", "w"), indent=1)
    print("page built", page_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--styles"); ap.add_argument("--out-dir", required=True); ap.add_argument("--budget-jpy", type=float, default=10)
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--shared-sha"); ap.add_argument("--asr", action="store_true")
    ap.add_argument("--analyze", action="store_true"); ap.add_argument("--build-page", action="store_true"); ap.add_argument("--page-dir")
    a = ap.parse_args(); od = a.out_dir if os.path.isabs(a.out_dir) else f"{ROOT}/{a.out_dir}"
    if a.shared_sha: shared_sha(od, a.shared_sha)
    if a.dry_run:
        B, d = baseline(); tot, per = estimate(B)
        info = {"model": sorted({b["model"] for b in B}), "voice": sorted({b["voice"] for b in B}), "backend": sorted({b["backend"] for b in B}),
                "tts_backend_top": d["tts_backend"], "J3_equals_baseline_style_prefix": all(b["style_prefix"] == PROMPTS["J3"] for b in B),
                "baseline_style_prefix_sha": sha_s(B[0]["style_prefix"]), "user_J3_sha": sha_s(PROMPTS["J3"]),
                "canonical": [b["tts_text"] for b in B], "new_calls": 25, "p5_prompt_sha_in_script": sha_s(PROMPTS["P5"]), "p5_prompt_sha_trial01_results": json.loads(open(f"{T1}/P5/results.jsonl", encoding="utf-8").readline())["prompt_sha"], "est_tts_jpy_total": round(tot, 2), "est_tts_jpy_per_style": round(per, 2),
                "asr_est_jpy_30audio": round(sum(((b["duration_s"] * 10) * ASR_PRICE_IN + 4 * ASR_PRICE_OUT) / 1e6 * USD_JPY for b in B) * 5, 3)}
        print(json.dumps(info, ensure_ascii=False, indent=1))
        os.makedirs(f"{od}/evidence", exist_ok=True)
        json.dump(info, open(f"{od}/evidence/dry_run.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if a.styles:
        for st in a.styles.split(","):
            assert st in PROMPTS and st not in REUSE, st
            gen_style(st, od, a.budget_jpy)
    if a.asr: asr(od)
    if a.analyze: analyze(od)
    if a.build_page:
        build_page(od, a.page_dir if os.path.isabs(a.page_dir) else f"{ROOT}/{a.page_dir}")
