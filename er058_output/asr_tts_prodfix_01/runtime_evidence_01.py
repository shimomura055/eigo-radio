# ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04A runtime evidence。
# 実行: python er058_output/asr_tts_prodfix_01/runtime_evidence_01.py <part: cap|azure> <out_dir>
# cap  : 正式Production経路(generate_a2_segment_with_slowdown -> generate_english_segment_with_fallback
#        -> strict/fallback/cascade/review_lock/実FFmpeg減速)を、TTS(Gemini)・Primary ASR(OpenAI)・
#        Secondary(Azure)だけmockして実行。課金0円。減速後再検証が常にNGになる条件で、TTS生成の
#        総回数・記録(attempt_history.jsonl)を測る。run id/出力は<out_dir>(Trial領域)に隔離。
# azure: 保存済み英語音声(約13.6秒)をAzure STTへ実際に1回だけ送り、集計関数が費用を計上するか測る。
import json
import os
import shutil
import sys
import wave

REPO = os.getcwd()
sys.path.insert(0, REPO)
SRC_WAV = "C:/Users/tensh/eigo-radio/er003_output/a2_audio_01/A02/narration/in_one_line.wav"
part, out_dir = sys.argv[1], os.path.abspath(sys.argv[2])
os.makedirs(out_dir, exist_ok=True)

import er011_human_review_lock_01 as review_lock
review_lock.ATTEMPT_HISTORY_PATH = os.path.join(out_dir, "attempt_history.jsonl")  # Production telemetryを汚さない


def run_cap():
    os.environ.setdefault("GEMINI_API_KEY", "dummy-no-network")  # 全呼び出しmock、client生成のみ満たす
    os.environ.setdefault("GOOGLE_API_KEY", "dummy-no-network")
    import er003_b1_p9a_audio as p9a
    import er003_v1_n3_01_tts_generate as tg
    import er006_asr_provider_routing_01 as routing
    import er006_secondary_asr_01 as secondary_asr
    import er006_secondary_asr_01 as sa
    import er003_v1_repro01_main_generate as repro01
    import er002_common as common
    import er008_a2_postprocess_slowdown_01 as a2s
    import er006_batch_tts_wiring_01  # noqa

    # human_review_queueの書込み先もTrial領域へ隔離
    sa.HUMAN_REVIEW_LOG_PATH = os.path.join(out_dir, "human_review_queue.jsonl")

    ENTITY = os.environ.get("EVIDENCE_ENTITY") == "1"
    TEXT = ("Some Muse calls were transferred over to the new office last week." if ENTITY else
            "Many people now work from home and use shared desks when they visit the office.")
    BAD = ("Some US calls were transferred over to the new office last week." if ENTITY else
           "completely unrelated words about sports and music")
    narration = os.path.join(out_dir, "theme_x", "a2", "narration")
    os.makedirs(narration, exist_ok=True)
    out_path = f"{narration}/full_story_part2.wav"

    counters = {"tts": 0, "azure": 0, "slowed": False, "bad_next": True, "transcribes": []}
    with wave.open(SRC_WAV, "rb") as w:
        pcm_bytes = w.readframes(w.getnframes())

    def fake_tts(text, language, out, tts_call_fn=None, safety_margin_seconds=None,
                 style_prefix_override=None, tts_backend="structured_separation"):
        counters["tts"] += 1
        counters["slowed"] = False
        counters["styles"] = counters.get("styles", []) + [style_prefix_override]
        shutil.copyfile(SRC_WAV, out)
        return {"status": "OK", "text": text, "path": out, "model": "MOCK", "voice": "MOCK", "call_count": 1,
                "retry_count": 0, "sha256": "x", "duration_seconds": 13.61,
                "trim_info": {}, "clipping_detected": False}

    real_slow = a2s.apply_a2_slowdown

    def wrapped_slow(src, dst, *a, **k):
        r = real_slow(src, dst, *a, **k)  # 実FFmpeg
        counters["slowed"] = True
        counters["bad_next"] = True  # 次の内側呼び出し(取り直し)でも最初の生成はNG
        return r
    tg.a2_slowdown.apply_a2_slowdown = wrapped_slow

    def fake_transcribe(path, language="en-US", prompt=None, timeout_seconds=None):
        if counters["slowed"]:
            txt = "the weather forecast says rain tomorrow afternoon"  # 減速後は常にNG
        elif counters["bad_next"] or os.environ.get("EVIDENCE_ALWAYS_BAD") == "1":
            counters["bad_next"] = False
            txt = BAD  # 各周の最初の生成はNG
        else:
            txt = TEXT  # 2回目のTTS生成は減速前ASRは合格
        counters["transcribes"].append({"tts_gen": counters["tts"], "slowed": counters["slowed"], "text": txt})
        return txt, None

    def fake_azure(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
        counters["azure"] += 1
        return (BAD if ENTITY else "the weather forecast says rain tomorrow afternoon (azure mock)"), None

    p9a.generate_narration_snippet = fake_tts
    routing.transcribe = fake_transcribe
    sa.get_full_text_via_azure_stt_with_phrase_list = fake_azure
    # fallback(minimal)経路のTTS呼び出し: 実コードを通しつつ、ネットワーク呼び出しだけmock
    common._call_tts_with_retry = lambda *a, **k: (pcm_bytes, 0, True, None)

    result = tg.generate_a2_segment_with_slowdown(
        TEXT, out_path, TEXT[:20], style_prefix_override=tg.A2_ENGLISH_STYLE_PREFIX_SLOWER, disfluency_qa=False)
    summary = {
        "tts_generation_calls": counters["tts"], "azure_mock_calls": counters["azure"],
        "final_status": result.get("status"), "reason": result.get("reason"),
        "tts_generations_used_field": result.get("tts_generations_used"),
        "tts_generation_cap_reached": result.get("tts_generation_cap_reached"),
        "slowdown_attempts_log": result.get("slowdown_attempts_log"),
        "transcribe_sequence": counters["transcribes"],
    }
    with open(os.path.join(out_dir, "cap_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps({k: summary[k] for k in ("tts_generation_calls", "final_status", "tts_generations_used_field",
                                                "tts_generation_cap_reached")}, ensure_ascii=False))


def run_azure():
    from dotenv import load_dotenv
    load_dotenv("C:/Users/tensh/eigo-radio/.env")  # 値は表示しない
    import er005_cost_logger as cl
    import er006_secondary_asr_01 as sa
    import er019_family_x_audio_production_runner_01 as r19
    log = os.path.join(out_dir, "raw_usage_log.jsonl")
    if os.path.exists(log):
        os.remove(log)
    cl.init_logger(log)
    text, err = sa.get_full_text_via_azure_stt_with_phrase_list(SRC_WAV, language="en-US", phrases=[])
    jpy, by = r19.compute_cost_jpy_so_far(log)
    res = {"azure_error": err, "azure_transcript": text, "aggregated_jpy": round(jpy, 4), "by_provider": by}
    with open(os.path.join(out_dir, "azure_summary.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(json.dumps({"azure_error": err, "aggregated_jpy": round(jpy, 4), "by_provider": by}, ensure_ascii=False))


# part "fallback" = cap と同じ経路で、減速前ASRが常にNG(標準2回NG->minimal fallback->Secondary(mock)->STOPPED)
if part == "fallback_entity":
    os.environ["EVIDENCE_ENTITY"] = "1"
    part = "fallback"
if part == "fallback":
    os.environ["EVIDENCE_ALWAYS_BAD"] = "1"
    part = "cap"
{"cap": run_cap, "azure": run_azure}[part]()
