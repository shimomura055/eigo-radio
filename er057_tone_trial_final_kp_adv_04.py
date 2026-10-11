# -*- coding: utf-8 -*-
"""委任_04 Trial専用: Advanced Key Phrase英語5件へK2適用(er057_tone_trial_kp_ja_gen_01 と同一条件・Production非経由)。
Master Store/manifest/telemetry/queue/cost_loggerへ書かない。"""
import os, sys, json, time
sys.path.insert(0, os.getcwd())
import er057_tone_trial_kp_ja_gen_01 as G
OUT = f"{G.ROOT}/er057_output/coffee_final_listening_tone_trial_01/part_final"
RAW = f"{OUT}/kp_adv_k2"
os.makedirs(RAW, exist_ok=True)
G.RAW = RAW
MV = {}

def call_tts(text, style, voice):
    import er033_tts_flash_lite_backend_wiring_01 as flw
    import er006_model_routing_contract_01 as rc
    import er002_gemini_client as gclient
    import er002_common as common
    from google.genai import types
    flw.assert_sdk_supports_speech_metadata()
    model = rc.require_model(flw.FAMILY_X_FLASH_LITE_TTS_PROCESS, G.MODEL)
    if G._client is None:
        G._client = gclient.make_client()
    content = types.Content(parts=[types.Part(text=text, speech_metadata=types.SpeechMetadata(style=style))], role="user")
    resp = G._client.models.generate_content(model=model, contents=content, config=types.GenerateContentConfig(
        response_modalities=["AUDIO"], speech_config=types.SpeechConfig(language_code=common.LANGUAGE_CODE, voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))), http_options=types.HttpOptions(timeout=gclient.TTS_TIMEOUT_MS)))
    parts = resp.candidates[0].content.parts
    raw = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
    if not raw:
        raise RuntimeError("empty audio")
    MV.setdefault(text, []).append(getattr(resp, "model_version", None))
    samples, fr = flw._decode_audio_defensive(raw)
    samples = flw._resample_to_common_rate(samples, fr)
    u = getattr(resp, "usage_metadata", None)
    usage = {"prompt_tokens": getattr(u, "prompt_token_count", None), "candidates_tokens": getattr(u, "candidates_token_count", None),
             "total_tokens": getattr(u, "total_token_count", None)} if u else None
    return samples, usage
G.call_tts = call_tts

def main():
    import er003_v1_n3_01_tts_generate as n3
    k = json.load(open(f"{G.TONE}/../b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))["items"]
    k = sorted(k, key=lambda it: it["rank"])
    style = G.B_SPECS["K2"][1]
    J = [{"id": f"K2_advkp{i}", "spec": "K2", "grp": "B", "text": n3.tts_safe_kp_en(it["used_form"]), "style": style, "voice": G.VOICE_EN,
          "margin": G.KP_EN_MARGIN, "lang": "en"} for i, it in enumerate(k, start=1)]
    res = []
    for j in J:
        r = G.gen_one(j)
        r["model_version_response"] = MV.get(j["text"])
        res.append(r)
        print(r["id"], r["status"], r.get("duration_s"), r.get("call_count"), r.get("model_version_response"), r.get("reason", ""), flush=True)
    with open(f"{OUT}/generation_log_04.jsonl", "w", encoding="utf-8") as f:
        for r in res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    pt = sum(u.get("prompt_tokens") or 0 for r in res for u in (r.get("usage") or []) if u)
    ct = sum(u.get("candidates_tokens") or 0 for r in res for u in (r.get("usage") or []) if u)
    usd = ct * G.PRICE_OUT_PER_M / 1e6 + pt * G.PRICE_IN_PER_M / 1e6
    cost = {"calls_total": sum(r.get("call_count", 0) for r in res), "jobs": len(J), "ok": sum(r["status"] == "OK" for r in res),
            "model_requested": G.MODEL, "model_version_response": sorted({str(v) for r in res for v in (r.get("model_version_response") or [])}),
            "prompt_tokens": pt, "candidates_tokens": ct, "est_usd": round(usd, 5), "est_jpy": round(usd * G.USD_JPY, 2),
            "pre_estimate_jpy": 0.3, "basis": "usage_metadata実測tokens×Standard単価(出力$6/M、入力$0.5/M)、USD_JPY=160。請求画面は未確認"}
    json.dump(cost, open(f"{OUT}/cost_actual_04.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(cost)

if __name__ == "__main__":
    main()
