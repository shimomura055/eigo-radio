# -*- coding: utf-8 -*-
"""FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_01 (Phase A) Trial専用script。Production非接続(DEV/Trial経路)。

正式Coffee E2E(coffee_prices__run_fxpw_01)のStandard日本語 Preview/Comment1〜4 の5 clipだけを、S3 Style
(Trial-04 PROMPTS_01.md、共通指示込み全文、sha256 060c08fd...)で再生成し、QA(ASR+統一judge)・音量処理(正式版と同一)・
Std再Assemblyを行う。他sectionはR2版の既存音声をProduction関数経由でそのまま読み、再生成しない。
Production code/Style profile/Master Audio Store/manifest/telemetry/HR queue/attempt_historyへは書かない。
modes: --estimate-only(API 0) / (生成+QA+Assembly+DIFF)"""
import os, sys, json, hashlib, time, argparse, re
sys.path.insert(0, os.getcwd())
import numpy as np
import soundfile as sf
from dotenv import load_dotenv
load_dotenv()
import er057_ja_support_calm_style_trial_04_gen as t4   # Trial-04のStyle定義・正式text取得・TTS呼出(Trial経路)
t = t4.t
g = t4.g

ROOT = g.ROOT
SEG = g.SEG_NAMES                      # preview, comment_1..4
S3_ID = "support_ja_s3_trial"          # Trial用ID(Production style_instruction_id/R2 keyとは別名)
R2_STYLE_SHA_EXPECT = "625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f"
S3_SHA_EXPECT = "060c08fde003cf7c2d15c654da96d3f857b8e7a9bd79eac31814ceaf7c923f33"
MAX_EXTRA = 40    # generate_a2_japanese_with_reading_safety既定 max_extra_chars=40 (er003_v1_n3_01_tts_generate.py:788)


def sha_s(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha_f(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def s3_style_and_verify(style_sha):
    s3 = t4.S["S3"][2] + t4.COMMON
    assert sha_s(s3) == S3_SHA_EXPECT == style_sha, "S3 sha mismatch"
    md = open(f"{ROOT}/er057_output/ja_support_calm_style_trial_04/PROMPTS_01.md", encoding="utf-8").read()
    blocks = re.findall(r"```\n(.*?)\n```", md, re.S)
    assert s3 in blocks, "S3 not verbatim in PROMPTS_01.md"
    return s3


def load_formal_texts(src_run):
    t4.FORMAL = f"{src_run}/a2"
    texts = t4.load_texts()            # 正式run tts_generation_results.jsonのsegments[*].text + 再計算一致assert
    exp = {"preview": "a5e974b44e38114e194dad6615bfa2aba9f822da0be359a33d9bda8fad542eab",
           "comment_1": "f145d6c205f2d3c636984157866f2f2d2d56aea4f6f537ba1997e9b6137277b5",
           "comment_2": "8f87ec29adc42c481337dc9614ea638b3a0f189f2922104e6d62c9402c882662",
           "comment_3": "8c5755d528a110f23301759f0a5d4d0e694f814d0aec9588f46f37796938a6d8",
           "comment_4": "6f46631578e5cdd3147964fb1873465e559d658ea20be1df6ebba5562086c1f9"}
    for k, v in exp.items():
        assert texts[k]["sha256"] == v, f"text sha mismatch vs PROMPTS_01.md: {k}"
    return texts


def estimate(out_dir, texts, s3, budget):
    sec = sum(v["formal_duration_s"] + 0.3 for v in texts.values())
    out_tok = sec * 25
    in_tok = sum((len(texts[n]["tts"]) + len(s3)) / 2.0 + 20 for n in SEG)
    usd = out_tok * g.PRICE_OUT_PER_M / 1e6 + in_tok * g.PRICE_IN_PER_M / 1e6
    jpy = usd * g.USD_JPY
    asr_jpy = sec / 60.0 * 0.003 * g.USD_JPY
    md = (f"# COST_ESTIMATE_01 (S3W Phase A, 2026-10-17, API 0)\n\n"
          f"- 対象: Std Preview/Comment1〜4 の 5 clip(原稿文字数: " + ", ".join(f"{n}={len(texts[n]['tts'])}字" for n in SEG) + ")。S3 Style {len(s3)}字。\n"
          f"- 想定出力音声 約{sec:.1f}秒(正式版実尺+margin)→出力token約{out_tok:.0f}(25 tok/秒)、入力token約{in_tok:.0f}。\n"
          f"- 単価(Trial-04と同一式): 出力${g.PRICE_OUT_PER_M}/M、入力${g.PRICE_IN_PER_M}/M、USD_JPY={g.USD_JPY}。\n"
          f"- TTS概算 ${usd:.4f} = 約JPY{jpy:.2f}(技術失敗retry込み最悪 約JPY{jpy*2:.2f})。\n"
          f"- ASR(OpenAI、約{sec/60:.1f}分、$0.003/分目安) 約JPY{asr_jpy:.2f}(統一judgeのcascade[Azure等]が発火した場合は別途。通常PASSなら0)。\n"
          f"- 合計 期待約JPY{jpy+asr_jpy:.2f} / 最悪約JPY{jpy*2+asr_jpy*2:.2f}。Guardrail JPY{budget}。\n"
          f"- T-2追記4点: (1)差分再生成=5 clipのみ生成(他sectionはR2版を参照、再生成しない) (2)再利用キャッシュ=Master Audio Store等は参照・書込みしない"
          f"(新Style×同一原稿の独立生成が目的) (3)--budget-jpy={budget}明示 (4)全再生成ではない(5 clip)。\n")
    open(f"{out_dir}/COST_ESTIMATE_01.md", "w", encoding="utf-8").write(md)
    print(md)
    return jpy + asr_jpy


def generate(out_dir, texts, s3):
    raw = f"{out_dir}/raw"
    os.makedirs(raw, exist_ok=True)
    g.RAW = raw
    g.call_tts = t.call_tts_mv      # Trial-04と同一(正式版と同一request形+model_version捕捉)
    assert g.JA_MARGIN == 0.35 and g.VOICE_JA == "Aoede" and g.MODEL == "gemini-3.8-flash-lite-tts"
    import er003_b1_p3u_audio as p3u
    assert p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS == g.JA_MARGIN   # 正式版margin(er003_v1_n3_01_tts_generate.py:625)
    rp = f"{out_dir}/results_01.jsonl"
    done = {}
    if os.path.exists(rp):
        for l in open(rp, encoding="utf-8"):
            r = json.loads(l); done[r["id"]] = r
    res = dict(done)
    calls = 0
    for nm in SEG:
        jid = f"S3_{nm}"
        if done.get(jid, {}).get("status") == "OK" and os.path.exists(f"{raw}/{jid}.wav"):
            continue
        j = {"id": jid, "spec": "S3", "grp": "D", "text": texts[nm]["tts"], "style": s3, "voice": g.VOICE_JA,
             "margin": g.JA_MARGIN, "lang": "ja"}
        r = g.gen_one(j)
        r["seg"] = nm
        res[jid] = r
        calls += r.get("call_count", 0)
        print(jid, r["status"], r.get("duration_s"), r.get("reason", ""), flush=True)
        with open(rp, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        if calls > 12:
            print("RUNAWAY GUARD", flush=True); break
    return res


def qa(out_dir, texts, res):
    """正式版と同じQA: Primary ASR(routing.transcribe ja-JP)→ja_secondary.evaluate_attempt_ja_with_cascade_detail(統一judge、
    er003_v1_n3_01_tts_generate.py:730と同関数・同引数形)→unified_judge.final_length_ok。再生成・HR queue書込みはしない。"""
    import er006_asr_provider_routing_01 as routing
    import er007_ja_secondary_asr_01 as ja_secondary
    import er078_asr_unified_attempt_ctx_01 as actx
    import er078_asr_unified_judge_01 as uj
    out = {}
    asr_sec = 0.0
    qp = f"{out_dir}/qa_results.json"
    if os.path.exists(qp):   # 同一音声のASR再課金を避ける(組立の再実行時)
        out = json.load(open(qp, encoding="utf-8"))
        if all(out.get(n, {}).get("status") == "OK" for n in SEG):
            return out, sum(out[n]["duration_audio_s"] for n in SEG)
        out = {}
    for nm in SEG:
        r = res[f"S3_{nm}"]
        p = f"{out_dir}/raw/S3_{nm}.wav"
        if r["status"] != "OK":
            out[nm] = {"status": r["status"], "reason": r.get("reason")}
            continue
        text = texts[nm]["tts"]
        tx, err = routing.transcribe(p, language="ja-JP")
        dur = sf.info(p).duration
        asr_sec += dur
        max_len = len(text) + MAX_EXTRA
        length_ok = tx is not None and len(tx) <= max_len
        detail = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            text, tx, p, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI,
            length_ok=length_ok, attempt_ctx=actx.build_attempt_ctx(1, 3, max_len=max_len))
        final_len = uj.final_length_ok(length_ok, detail)
        aj = detail.get("asr_judgement") or {}
        cls = detail["classification"]
        out[nm] = {"status": "OK", "canonical_text": text, "asr_text": tx, "asr_error": err,
                   "primary_classification": cls.classification, "verified_content": bool(detail["verified"]),
                   "length_ok": bool(length_ok), "final_length_ok": bool(final_len),
                   "verified": bool(detail["verified"] and final_len),
                   "asr_judgement_state": aj.get("state"), "reason_code": aj.get("reason_code"),
                   "secondary_called": (aj.get("secondary") or {}).get("called"),
                   "human_review_required": detail.get("human_review_required"),
                   "final_status": detail.get("final_status"), "warning_labels": (aj.get("primary") or {}).get("warning_labels"),
                   "duration_audio_s": round(dur, 3), "raw_duration_s": r.get("raw_duration_s"),
                   "duration_anomaly": r.get("duration_anomaly"), "tts_call_count": r.get("call_count"),
                   "tts_retry_count": r.get("retry_count"), "regeneration": False, "fallback_used": False}
        print(nm, out[nm]["primary_classification"], out[nm]["asr_judgement_state"], out[nm]["verified"], flush=True)
    json.dump(out, open(f"{out_dir}/qa_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return out, asr_sec


def cost(out_dir, res, asr_sec, budget):
    pt = ct = calls = 0
    mv = set()
    for r in res.values():
        calls += r.get("call_count", 0)
        for u in r.get("usage", []) or []:
            if u:
                pt += u.get("prompt_tokens") or 0; ct += u.get("candidates_tokens") or 0
                if u.get("model_version"):
                    mv.add(u["model_version"])
    usd = ct * g.PRICE_OUT_PER_M / 1e6 + pt * g.PRICE_IN_PER_M / 1e6
    asr_jpy = asr_sec / 60.0 * 0.003 * g.USD_JPY
    c = {"tts_calls": calls, "clips": len(SEG), "prompt_tokens": pt, "candidates_tokens": ct,
         "tts_usd": round(usd, 5), "tts_jpy": round(usd * g.USD_JPY, 2), "asr_audio_seconds": round(asr_sec, 2),
         "asr_jpy_est": round(asr_jpy, 2), "total_jpy_est": round(usd * g.USD_JPY + asr_jpy, 2), "budget_guardrail_jpy": budget,
         "response_model_versions": sorted(mv),
         "basis": "usage_metadata実測tokens×Standard単価(出力$6/M、入力$0.5/M)、USD_JPY=160。ASRは$0.003/分目安の推定。請求画面は未確認"}
    json.dump(c, open(f"{out_dir}/cost_actual_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(c)
    return c


def assemble(src_run, out_dir, texts, s3):
    """Production関数(runner.load_family_x_a2_sources/apply_family_x_a2_gain/build_family_x_a2_timeline、asm.assemble_with_timeline)を
    importして流用。R2 sourcesからR2 partsを作り(=他section不変)、Preview/Comment1〜4のみS3音声へ差し替える。
    音量処理は正式版と同条件: Preview=無加工(gain 1.0、runner:1839)、Comment=目標RMS正規化(runner:1852-1855)。
    目標RMSはR2版gain_reportの値(0.0949)に固定(他section不変のため)。S3 Previewから再計算した場合の値は参考として併記。"""
    import er019_family_x_audio_production_runner_01 as run
    p9a, asm, common = run.p9a, run.asm, run.common
    sdir = json.load(open(f"{src_run}/entry_point.json", encoding="utf-8"))["source_dir"]   # Production assemble(runner:2676)と同じsource_dir
    src = run.load_family_x_a2_sources(src_run, source_dir=sdir)
    parts = run.apply_family_x_a2_gain(src)
    r2_gain = parts["gain_report"]
    T = r2_gain["target_rms"]
    # (検証) R2 partsのままのAssemblyが正式版wavと一致するか
    seq_r2 = run.build_family_x_a2_timeline(parts)
    res_r2 = asm.assemble_with_timeline(seq_r2)
    hr2 = asm.apply_headroom_safety_valve(res_r2["assembled"], seq_r2)
    formal_wav, fsr = sf.read(f"{src_run}/a2/assembled/Family_X_Audio_A2_COFFEE_PRICES.wav", dtype="float32")
    rep_ok = (formal_wav.shape == hr2["assembled"].shape)
    maxdiff = float(np.max(np.abs(formal_wav - hr2["assembled"]))) if rep_ok else None
    # S3差し替え
    nd = f"{src_run}/a2/narration"
    mono = {}
    for nm in SEG:
        m, sr, _, _ = common.read_wav_float(f"{out_dir}/raw/S3_{nm}.wav")
        assert sr == common.SAMPLE_RATE
        mono[nm] = m
    new_parts = dict(parts)
    new_parts["a2_segments"] = dict(parts["a2_segments"])
    new_parts["preview"] = p9a.mono_24k_to_stereo_target(mono["preview"])      # 無加工(runner:1839)
    g3 = {"target_rms": T, "target_rms_basis": "R2版gain_reportのtarget_rms固定(他section不変のため)",
          "preview": {"gain": 1.0, "rms_before": round(float(p9a.rms(mono["preview"])), 5), "note": "無加工(正式版と同一処理、runner:1839-1840)"}}
    for nm in SEG[1:]:
        gain = p9a.compute_gain_for_target_rms(mono[nm], T)
        gained = mono[nm] * gain
        new_parts["a2_segments"][nm] = p9a.mono_24k_to_stereo_target(gained)
        g3[f"a2_{nm}"] = {"gain": round(float(gain), 4), "rms_before": round(float(p9a.rms(mono[nm])), 5),
                          "rms_after": round(float(p9a.rms(gained)), 5), "peak_after": round(float(p9a.peak(gained)), 5)}
    part1_rms = float(p9a.rms(src["a2_segments"]["full_story_part1"]))
    g3["reference_if_production_recomputed_target"] = round((float(p9a.rms(mono["preview"])) + part1_rms) / 2, 5)
    g3["note_reference"] = "Production apply_family_x_a2_gainはtarget=(rms(preview)+rms(part1))/2で再計算する。S3 Previewで再計算すると全sectionのgainが微変動するため、本Phase Aは他section不変を優先しR2値固定。採用後のPhase Bで再計算仕様を確認する。"
    g3["r2_gain_report_ref"] = {k: r2_gain[k] for k in ["target_rms", "preview", "a2_comment_1", "a2_comment_2", "a2_comment_3", "a2_comment_4"]}
    seq = run.build_family_x_a2_timeline(new_parts)
    res = asm.assemble_with_timeline(seq)
    hr = asm.apply_headroom_safety_valve(res["assembled"], seq)
    assembled = hr["assembled"]
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    outp = f"{out_dir}/assembled/Family_X_Audio_A2_COFFEE_PRICES_S3.wav"
    common.write_wav_float(outp, assembled, run.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], run.SR)
    info = {"status": "OK", "out_path": outp, "duration_seconds": res["total_duration_seconds"],
            "r2_duration_seconds": res_r2["total_duration_seconds"], "clipping_detected": metrics["clipping_detected"],
            "peak": round(float(p9a.peak(assembled)), 5), "headroom_safety_valve": hr["report"],
            "replication_check_r2_vs_formal": {"shape_equal": rep_ok, "max_abs_diff": maxdiff,
                                               "note": "R2 sourcesをProduction関数でAssemblyした結果と正式版wavの一致(不変section再現性)"},
            "timeline": res["timeline"], "timeline_r2": res_r2["timeline"], "segment_order_equal_to_r2": [e["part"] for e in res["timeline"]] == [e["part"] for e in res_r2["timeline"]]}
    json.dump(g3, open(f"{out_dir}/gain_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(info, open(f"{out_dir}/assemble_std_s3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    # 不変section検証: S3 assembly内の非対象区間とR2の同区間が一致するか
    unchanged = {}
    tl, tlr = res["timeline"], res_r2["timeline"]
    for e, er in zip(tl, tlr):
        targ = e["part"].startswith("Preview") and not e["part"].startswith("Preview intro") or re.match(r"Comment \d", e["part"])
        if targ or e["part"].startswith("pause"):
            continue
        a = assembled[int(round(e["start_seconds"] * run.SR)): int(round((e["start_seconds"] + e["duration_seconds"]) * run.SR))]
        b = formal_wav[int(round(er["start_seconds"] * run.SR)): int(round((er["start_seconds"] + er["duration_seconds"]) * run.SR))]
        n = min(len(a), len(b))
        unchanged[e["part"]] = float(np.max(np.abs(a[:n] - b[:n]))) if n else None
    info["unchanged_sections_max_abs_diff"] = unchanged
    info.pop("timeline"); info.pop("timeline_r2")
    info["timeline"] = tl
    json.dump(info, open(f"{out_dir}/assemble_std_s3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("assemble", info["duration_seconds"], "r2", info["r2_duration_seconds"], "repl_maxdiff", maxdiff,
          "unchanged_max", max(v for v in unchanged.values() if v is not None))
    return g3, info


def evidence_and_diff(src_run, out_dir, texts, s3, qar, g3, info, c):
    fr = json.load(open(f"{src_run}/a2/audit/tts_generation_results.json", encoding="utf-8"))
    prof = json.load(open(f"{src_run}/audit/style_profile.json", encoding="utf-8")) if os.path.exists(f"{src_run}/audit/style_profile.json") else {}
    r2sha = None
    for nm in SEG:
        sp = (fr["segments"][nm].get("style_profile") or {})
        r2sha = sp.get("style_base_sha256")
        assert r2sha == R2_STYLE_SHA_EXPECT, ("R2 style sha mismatch", nm, r2sha)
    ev = {"style_instruction_id": S3_ID, "scope": "Coffee限定の検証用差し替え(Trial/DEV経路、Production未採用、Master Audio Store非書込)",
          "s3_style_sha256": sha_s(s3), "s3_style_chars": len(s3), "s3_style_full_text": s3,
          "s3_source": "er057_output/ja_support_calm_style_trial_04/PROMPTS_01.md L53-63(逐語一致assert済み)",
          "r2_style_sha256": r2sha, "model_requested": g.MODEL, "response_model_versions": c["response_model_versions"],
          "voice": g.VOICE_JA, "margin_s": g.JA_MARGIN, "tts_backend": "speech_metadata_flash_lite(正式版と同一request形: t.call_tts_mv)",
          "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"), "slowdown": "なし(正式版もpreview/commentは減速なし)",
          "texts": {nm: {"chars": len(texts[nm]["tts"]), "sha256": texts[nm]["sha256"], "equal_to_formal": True} for nm in SEG},
          "master_audio_store_written": False, "production_style_profile_modified": False}
    json.dump(ev, open(f"{out_dir}/style_evidence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    lines = ["# DIFF_VS_R2_01 (S3 vs R2, Std Preview/Comment1〜4)", "",
             f"- R2 Style sha256: `{r2sha}` / S3 Style sha256: `{sha_s(s3)}`", f"- Std通し尺: R2 {info['r2_duration_seconds']}秒 → S3 {info['duration_seconds']}秒",
             "", "| section | 尺R2(s) | 尺S3(s) | RMS前R2 | RMS前S3 | gain R2 | gain S3 | ASR R2 | ASR S3 | AUW S3 |", "|---|---|---|---|---|---|---|---|---|---|"]
    from er003_b1_p9a_audio import rms as _rms
    import er002_common as common
    for nm in SEG:
        rs = fr["segments"][nm]
        r2m, _, _, _ = common.read_wav_float(f"{src_run}/a2/narration/{nm}.wav")
        key = "preview" if nm == "preview" else f"a2_{nm}"
        r2g = json.load(open(f"{src_run}/a2/audit/gain_report.json", encoding="utf-8")).get(key, {})
        s3g = g3.get(key, {})
        q = qar[nm]
        lines.append(f"| {nm} | {rs['duration_seconds']} | {q.get('duration_audio_s')} | {round(float(_rms(r2m)),5)} | {s3g.get('rms_before')} | "
                     f"{r2g.get('gain')} | {s3g.get('gain')} | {rs.get('audio_classification')} | {q.get('primary_classification')} | {q.get('asr_judgement_state')} |")
    lines += ["", "ASR転写(R2 / S3):"]
    for nm in SEG:
        lines.append(f"- {nm}: R2=`{fr['segments'][nm].get('asr_text')}` / S3=`{qar[nm].get('asr_text')}`")
    open(f"{out_dir}/DIFF_VS_R2_01.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-run", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--style-sha", default=S3_SHA_EXPECT)
    ap.add_argument("--budget-jpy", type=float, default=15)
    ap.add_argument("--estimate-only", action="store_true")
    a = ap.parse_args()
    src = os.path.abspath(a.src_run); out_dir = os.path.abspath(a.out_dir)
    assert os.path.abspath(out_dir) != src and "_s3_support_" in out_dir      # R2 dirへ書かない
    os.makedirs(out_dir, exist_ok=True)
    s3 = s3_style_and_verify(a.style_sha)
    texts = load_formal_texts(src)
    est = estimate(out_dir, texts, s3, a.budget_jpy)
    if a.estimate_only:
        sys.exit(0)
    if os.environ.get("TTS_EXECUTION_MODE") != "STANDARD":
        raise SystemExit("TTS_EXECUTION_MODE=STANDARD required (T-2)")
    if est >= 100:
        raise SystemExit("estimate >= JPY100: report (7-7)")
    res = generate(out_dir, texts, s3)
    if any(res.get(f"S3_{n}", {}).get("status") != "OK" for n in SEG):
        print("GENERATION FAILED for some clip; stop and report", flush=True); sys.exit(2)
    qar, asr_sec = qa(out_dir, texts, res)
    c = cost(out_dir, res, asr_sec, a.budget_jpy)
    g3, info = assemble(src, out_dir, texts, s3)
    evidence_and_diff(src, out_dir, texts, s3, qar, g3, info, c)
    print("DONE; QA verified:", {n: qar[n].get("verified") for n in SEG})
