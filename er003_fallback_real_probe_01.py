# FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_07 Step2: 実fallback probe(有料、上限6JPY)
# fallback関数を直接呼出し、speech_metadata.style/400・空応答/ASR合格を実測する。
# 実行: .venv/Scripts/python.exe er003_fallback_real_probe_01.py
from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

load_dotenv()

import er005_cost_logger as cl  # noqa: E402
import er006_asr_provider_routing_01 as routing  # noqa: E402
import er006_secondary_asr_01 as secondary_asr  # noqa: E402
import er007_ja_secondary_asr_01 as ja_secondary  # noqa: E402
import er019_family_x_audio_production_runner_01 as runner  # noqa: E402
import er033_tts_flash_lite_backend_wiring_01 as flw  # noqa: E402
import er033_tts_flash_lite_family_x_styles_01 as S  # noqa: E402
import er003_v1_n3_01_tts_generate as n3_tts  # noqa: E402
import er003_v1_repro01_main_generate as repro01  # noqa: E402
import er003_v1_sing01_voice01_generate as voice01  # noqa: E402

OUT = "er053_output/coffee_new_tone_e2e_01/fallback_real_probe_01"
BUDGET_JPY = 6.0
BACKEND = "speech_metadata_flash_lite"
os.makedirs(OUT, exist_ok=True)
cl.install(f"{OUT}/raw_usage_log.jsonl")


def slower(base):
    return f"{base}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"


CAPTURED = []
_orig = flw.resolve_tts_call_and_prompt


def _capturing(text, style_prefix, model_name, voice_name, out_path=None, tts_backend=flw.DEFAULT_TTS_BACKEND, **kw):
    call_fn, prompt = _orig(text, style_prefix, model_name, voice_name, out_path, tts_backend=tts_backend, **kw)
    CAPTURED.append({"text": text, "style": prompt[1] if isinstance(prompt, tuple) else None,
                     "voice": voice_name, "backend": tts_backend})
    return call_fn, prompt


flw.resolve_tts_call_and_prompt = _capturing

TEXT = {
    "J2": [
        "ロイターが取材した専門家の見積もりでは、生の豆の値段が小売価格に反映されるまで、少なくとも約9か月かかります。",
        "値札は、まだ旅の途中？",
    ],
    "E2": [
        "Reuters spoke with market experts, and they estimated that it takes about nine months for bean prices to reach store shelves.",
        "Prices will not drop for nine months.",
    ],
    "F1_5_A2": [
        "First, let's go back to when high prices caused a stir. Bad weather in Brazil and Vietnam hurt the supply. "
        "Few beans were for sale, and stocks were low. Then demand around the world was strong.",
        "US roasters keep green beans in stock. Then they roast and pack them. Reports also say price talks with stores "
        "often happen every three months. There are several steps between the beans and the store shelf.",
    ],
    "F1_5_B1B": [
        "After that, an index showing world market prices fell by twenty-five percent over seven months. The USDA links "
        "this drop to extra supplies becoming easier to get. But in the United States, the coffee part of the Consumer "
        "Price Index was still higher than in the same month a year earlier.",
        "Around the same time, ICE's arabica coffee futures hit a record high up to that point. But futures prices are "
        "not the prices of green beans for immediate sale, and they are not store prices, either.",
    ],
}


def cost_now():
    return runner.compute_cost_jpy_so_far(f"{OUT}/raw_usage_log.jsonl")


def en_asr(text, wav):
    asr_text, err = routing.transcribe(wav, language="en-US")
    ok, stop, cls = secondary_asr.evaluate_attempt_with_cascade(
        text, asr_text, [], wav, language="en-US", ledger_phrases=[],
        cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED)
    return {"asr_text": asr_text, "verified": bool(ok), "classification": cls.classification,
            "err": str(err) if err else None}


def run_case(kind, idx, text, expected_style):
    n0 = len(CAPTURED)
    wav = f"{OUT}/{kind}_{idx}.wav"
    rec = {"kind": kind, "idx": idx, "text": text, "expected_style": expected_style}
    t0 = time.time()
    try:
        if kind == "J2":
            r = n3_tts._generate_a2_japanese_minimal_instruction(
                text, wav, tts_backend=BACKEND, fallback_style_prefix=expected_style)
            rec["fn_status"] = r.get("status")
            rec["reason"] = r.get("reason")
            rec["style_source"] = r.get("style_source")
            rec["tts_model_id"] = r.get("tts_model_id")
            if r.get("status") == "OK":
                asr_text, err = routing.transcribe(wav, language="ja-JP")
                length_ok = asr_text is not None and len(asr_text) <= len(text) + 40
                ok, stop, cls = ja_secondary.evaluate_attempt_ja_with_cascade(
                    text, asr_text, wav, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI,
                    expected_readings=None, length_ok=length_ok)
                rec["asr"] = {"asr_text": asr_text, "verified": bool(ok and length_ok),
                              "classification": cls.classification, "scg_info": getattr(cls, "scg_info", None)}
        elif kind in ("F1_5_A2", "F1_5_B1B"):
            r = repro01.generate_english_component_minimal_instruction(
                text, wav, enable_pronunciation_resolver=True, tts_backend=BACKEND,
                fallback_style_prefix=expected_style)
            rec["fn_status"] = r.get("status")
            rec["reason"] = r.get("reason")
            rec["style_source"] = r.get("style_source")
            rec["tts_model_id"] = r.get("tts_model_id")
            if r.get("status") == "OK":
                rec["asr"] = en_asr(text, wav)
        elif kind == "E2":
            # Charon技術的fallback: 標準呼び出し(1回目)のみTTS例外にして無課金で失敗させ、fallbackは実関数を通す
            state = {"n": 0}

            def _fail_first(text_, style_prefix, model_name, voice_name, out_path=None, **kw):
                state["n"] += 1
                if state["n"] == 1:
                    def boom(prompt):
                        raise RuntimeError("probe: forced standard TTS failure (no API call)")
                    CAPTURED.append({"text": text_, "style": "<standard path, forced fail, not sent>",
                                     "voice": voice_name, "backend": kw.get("tts_backend")})
                    return boom, (text_, style_prefix)
                return _capturing(text_, style_prefix, model_name, voice_name, out_path, **kw)
            flw.resolve_tts_call_and_prompt = _fail_first
            try:
                r = voice01.generate_charon_english(
                    text, wav, max_attempts=1, tts_backend=BACKEND, style_prefix_override=expected_style,
                    fallback_style_prefix=expected_style, enable_pronunciation_resolver=True)
            finally:
                flw.resolve_tts_call_and_prompt = _capturing
            rec["fn_status"] = r.get("status")
            rec["reason"] = r.get("reason")
            rec["style_source"] = r.get("style_source")
            rec["instruction_type"] = r.get("instruction_type")
            rec["tts_model_id"] = r.get("tts_model_id")
            rec["asr"] = {"asr_text": r.get("asr_text"), "verified": bool(r.get("asr_verified")),
                          "classification": r.get("audio_classification")}
            rec["attempts_log"] = r.get("attempts_log")
    except Exception as e:  # noqa: BLE001
        rec["exception"] = f"{type(e).__name__}: {e}"[:400]
    rec["captured_calls"] = CAPTURED[n0:]
    sent = [c for c in rec["captured_calls"] if not str(c["style"]).startswith("<standard")]
    last_style = sent[-1]["style"] if sent else None
    rec["sent_style_startswith_approved"] = bool(last_style and expected_style and last_style.startswith(expected_style))
    rec["sent_voice"] = sent[-1]["voice"] if sent else None
    rec["elapsed_sec"] = round(time.time() - t0, 1)
    jpy, by = cost_now()
    rec["cumulative_jpy"] = round(jpy, 3)
    rec["by_provider_jpy"] = by
    return rec


def main():
    plan = [("J2", S.JA_J2_BRIGHT), ("E2", S.EN_COMMENT_E2_UPBEAT),
            ("F1_5_A2", slower(S.EN_FULLSTORY_F1_5)), ("F1_5_B1B", S.EN_FULLSTORY_F1_5)]
    results = []
    for kind, style in plan:
        for i, t in enumerate(TEXT[kind], 1):
            with cl.logging_context("coffee_new_tone_fb_probe", "probe"):
                rec = run_case(kind, i, t, style)
            results.append(rec)
            print(json.dumps({k: rec.get(k) for k in (
                "kind", "idx", "fn_status", "style_source", "sent_style_startswith_approved", "cumulative_jpy",
                "exception")}, ensure_ascii=False), flush=True)
            with open(f"{OUT}/probe_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=1)
            if rec["cumulative_jpy"] > BUDGET_JPY:
                print("[BUDGET STOP]")
                return


if __name__ == "__main__":
    main()
