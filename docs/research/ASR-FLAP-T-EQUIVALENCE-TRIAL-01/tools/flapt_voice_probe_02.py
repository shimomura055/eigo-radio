# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_02 Phase 2: Voice probe(Trial専用・Production無変更)。
# Production leaf(er003_b1_p9a_audio.generate_narration_snippet + gclient.voice_override)で各Voice x flap環境語を生成し、
# 本番ASR系統(OpenAI gpt-4o-mini-transcribe / Azure / ローカルWhisper small)で転写する。判定はflapt_equivalence_proto_01(API 0)。
# 実行: PYTHONUTF8=1 <venv python> docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/tools/flapt_voice_probe_02.py --combos Aoede:fl,Charon:fl,Zephyr:pro --slow-voices Aoede --cap-jpy 30
import argparse, hashlib, json, math, os, sys, time

sys.path.insert(0, ".")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT = "docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/probe_02"
ITEMS = ["latter", "metal", "betting", "atom", "waiting", "coating", "water", "writer", "little", "better", "city", "the latter one"]
AZURE_USD_PER_HOUR, JPY_PER_USD = 1.0, 160.0
OPENAI_USD_PER_MIN = 0.003   # gpt-4o-mini-transcribe(秒換算の概算)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_env():
    from dotenv import dotenv_values
    for k, v in dotenv_values("C:/Users/tensh/eigo-radio/.env").items():
        os.environ.setdefault(k, v or "")


def asr_all(wav, fns):
    out = {}
    for name, fn in fns:
        try:
            t, err = fn(wav)
        except Exception as e:  # noqa
            t, err = None, str(e)[:200]
        out[name] = {"text": t, "error": err}
    return out


def classify(proto, canonical, asr_text):
    """EXACT=t綴り一致 / FLAP_D=d綴り語へ転写(flap実証) / AY_AMBIG / OTHER / EMPTY。"""
    if not asr_text:
        return "EMPTY"
    ct, at = proto.tokens(canonical), proto.tokens(asr_text)
    if [x.lower() for x in ct] == [x.lower() for x in at]:
        return "EXACT"
    r = proto.evaluate(canonical, asr_text)
    dec = getattr(r, "decision", None) or getattr(r, "verdict", None)
    return {"RESCUE": "FLAP_D", "REQUIRES_EXTRA_EVIDENCE": "AY_AMBIG"}.get(dec, "OTHER")


def asr_cost(dur):
    return round(math.ceil(dur) * AZURE_USD_PER_HOUR / 3600 * JPY_PER_USD + dur / 60 * OPENAI_USD_PER_MIN * JPY_PER_USD, 4)


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--combos", required=True, help="Voice:path(fl|pro),...")
    ap.add_argument("--slow-voices", default="")
    ap.add_argument("--cap-jpy", type=float, default=30.0)
    ap.add_argument("--stop-margin-jpy", type=float, default=1.0)
    ap.add_argument("--items", default="", help="'|'区切りで項目を限定(校正用)")
    ap.add_argument("--out-dir", default=OUT, help="shard別出力(並列実行用。後でmerge)")
    a = ap.parse_args()
    OUT = a.out_dir
    os.makedirs(f"{OUT}/wav", exist_ok=True)
    load_env()
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er062_family_z_structure_01 as st
    st.check_stop_sentinel("flapt_voice_probe:start", OUT)
    st.record_launch_and_check_storm(OUT, sys.argv)
    st.acquire_run_lock(OUT, sys.argv)
    try:
        import er005_cost_logger as cl
        cost_log = f"{OUT}/cost_log.jsonl"
        cl.install(cost_log)
        st.install_api_stop_guard()
        import er019_family_x_audio_production_runner_01 as xr
        import er002_gemini_client as gclient
        import er003_b1_p9a_audio as p9a
        import er033_tts_flash_lite_family_x_styles_01 as fls
        import er006_asr_provider_routing_01 as route
        import er006_secondary_asr_01 as sec
        import er104_kp_three_asr_vote_01 as v3
        import er008_a2_postprocess_slowdown_01 as slow
        import flapt_equivalence_proto_01 as proto

        res_path = f"{OUT}/results.jsonl"
        done = {}
        if os.path.exists(res_path):
            for line in open(res_path, encoding="utf8"):
                r = json.loads(line)
                done[r["clip_key"]] = r
        items = [i for i in a.items.split("|") if i] or ITEMS
        combos = [c.split(":") for c in a.combos.split(",") if c]
        slow_voices = set(v for v in a.slow_voices.split(",") if v)
        fns = [("openai", lambda w: route.transcribe(w, "en")),
               ("azure", lambda w: sec.get_full_text_via_azure_stt_with_phrase_list(w, language="en-US", phrases=None)),
               ("whisper", lambda w: (v3.whisper_transcribe(w), None))]

        def spent():
            tts = xr.compute_cost_jpy_so_far(cost_log)[0]
            asr = sum(r.get("asr_cost_jpy", 0) for r in done.values())
            return tts, asr, tts + asr

        def record(r):
            done[r["clip_key"]] = r
            with open(res_path, "a", encoding="utf8") as f:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        for voice, path in combos:
            for item in items:
                key = f"{voice}|{path}|{item}|normal"
                if key in done and voice in slow_voices and f"{voice}|{path}|{item}|slow6" not in done and done[key].get("status") == "OK":
                    # 補完: 校正runで通常clipだけ作られたものに減速版(既存wavへのffmpeg atempo+ASRのみ。TTS再生成なし)を追加
                    tts, asr, tot = spent()
                    if tot >= a.cap_jpy - a.stop_margin_jpy:
                        print(f"CAP_STOP total={tot:.2f}")
                        return
                    base = done[key]
                    wav2 = base["wav"].replace(".wav", "_slow6.wav")
                    info = slow.apply_a2_slowdown(base["wav"], wav2, 6.0)
                    d2 = info["dst_duration_seconds"]
                    v = {"clip_key": f"{voice}|{path}|{item}|slow6", "voice": voice, "path": path, "item": item, "variant": "slow6", "status": "OK",
                         "wav": wav2, "clip_sha256": sha(wav2), "dur": d2, "model": base["model"], "voice_sent": base["voice_sent"], "slowdown": info,
                         "asr": asr_all(wav2, fns), "asr_cost_jpy": asr_cost(d2), "backfill": True}
                    v["class"] = {s_: classify(proto, item, o["text"]) for s_, o in v["asr"].items()}
                    record(v)
                    print("BACKFILL", v["clip_key"], v["class"], flush=True)
                    continue
                if key in done:
                    continue
                tts, asr, tot = spent()
                if tot >= a.cap_jpy - a.stop_margin_jpy:
                    print(f"CAP_STOP total={tot:.2f}")
                    return
                st.check_stop_sentinel(f"flapt_voice_probe:{key}", OUT)
                wav = f"{OUT}/wav/{voice}_{path}_{item.replace(' ', '_')}.wav"
                kw = dict(tts_backend="speech_metadata_flash_lite",
                          style_prefix_override=fls.FAMILY_X_ROLE_STYLE_EN["HEADING_READOUT"]) if path == "fl" else {}
                t0 = time.time()
                with cl.segment_context(key):
                    if voice == gclient.DEFAULT_LEAF_VOICE:
                        r = p9a.generate_narration_snippet(item, "en", wav, **kw)
                    else:
                        with gclient.voice_override(voice):
                            r = p9a.generate_narration_snippet(item, "en", wav, **kw)
                if r.get("status") != "OK":
                    record({"clip_key": key, "voice": voice, "path": path, "item": item, "variant": "normal",
                            "status": r.get("status"), "reason": str(r.get("reason"))[:200], "asr_cost_jpy": 0})
                    continue
                rec = {"clip_key": key, "voice": voice, "path": path, "item": item, "variant": "normal", "status": "OK", "wav": wav,
                       "clip_sha256": sha(wav), "dur": r["duration_seconds"], "model": r["model"], "voice_sent": r["voice"],
                       "tts_backend": r.get("tts_backend"), "language_code": "en-us", "style_prefix": r.get("style_prefix"),
                       "asr": asr_all(wav, fns), "asr_cost_jpy": asr_cost(r["duration_seconds"])}
                variants = [rec]
                if voice in slow_voices:
                    wav2 = wav.replace(".wav", "_slow6.wav")
                    info = slow.apply_a2_slowdown(wav, wav2, 6.0)
                    d2 = info["dst_duration_seconds"]
                    variants.append({"clip_key": f"{voice}|{path}|{item}|slow6", "voice": voice, "path": path, "item": item,
                                     "variant": "slow6", "status": "OK", "wav": wav2, "clip_sha256": sha(wav2), "dur": d2,
                                     "model": r["model"], "voice_sent": r["voice"], "slowdown": info,
                                     "asr": asr_all(wav2, fns), "asr_cost_jpy": asr_cost(d2)})
                for v in variants:
                    v["class"] = {s: classify(proto, item, o["text"]) for s, o in v["asr"].items()}
                    record(v)
                tts, asr, tot = spent()
                print(key, round(time.time() - t0, 1), "s", rec["class"], {s: o["text"] for s, o in rec["asr"].items()},
                      "spent", round(tot, 3), flush=True)
        tts, asr, tot = spent()
        print(json.dumps({"done": len(done), "tts_jpy": round(tts, 3), "asr_jpy": round(asr, 3), "total_jpy": round(tot, 3)}))
    finally:
        st.release_run_lock(OUT)


if __name__ == "__main__":
    main()
