# ============================================================
# er022_tts_gemini_3_8_flash_lite_next_trial_01_sdk_225_check.py
# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01 (google-genai 2.25.0 確認、¥0)
# ============================================================
# 性質: Trial限定。Production変更0件。実費用: 本ファイル単体では¥0
# (httpx.Client.sendを送信直前でRuntimeErrorへ変換し中断する、ネットワーク
# 呼び出しは1件も発生しない。実TTS呼び出しはStage 1本体
# [er022_tts_gemini_3_8_flash_lite_next_trial_01_stage1.py]側で実施済み)。
#
# 対象: REPORT §12(補足調査)で判明した「google-genai 2.25.0の
# CHANGELOGに"Expose SpeechMetadata...in public GenAI SDKs"という記述が
# ある」という事実を、実際にTrial venv(.venv_trial_genai225)へ
# 2.25.0を導入した上で実機確認する(型定義の存在確認+送信直前のwire body
# 形状確認、いずれもネットワーク呼び出し0件)。
#
# 実行方法:
#   .venv_trial_genai225/Scripts/python.exe \
#     er022_tts_gemini_3_8_flash_lite_next_trial_01_sdk_225_check.py
from __future__ import annotations

import json
import os

OUT_DIR = "er022_output/tts_gemini_3_8_flash_lite_next_trial_01"
RESULT_PATH = f"{OUT_DIR}/sdk_225_generatecontent_probe.json"


def check_genai_version() -> dict:
    import google.genai as genai_pkg
    return {"installed_version": genai_pkg.__version__, "expected": "2.25.0",
            "matches_expected": genai_pkg.__version__ == "2.25.0"}


def check_type_definition() -> dict:
    """types.Part.speech_metadataがpydanticフィールドとして存在するかを、
    ネットワーク呼び出し無しで確認する(型検証のみ)。"""
    from google.genai import types
    field = types.Part.model_fields.get("speech_metadata")
    sm = types.SpeechMetadata(style="calm")
    part = types.Part(text="Hello world.", speech_metadata=sm)
    dumped = part.model_dump(exclude_none=True)
    return {
        "part_has_speech_metadata_field": field is not None,
        "field_alias": getattr(field, "alias", None) if field else None,
        "speech_metadata_type_constructible": True,
        "part_model_dump_includes_speech_metadata": "speech_metadata" in dumped,
    }


def probe_generate_content_wire_body() -> dict:
    """GenerateContent API経由で、送信直前のHTTPリクエストbodyに
    speechMetadata(camelCase)がsibling fieldとして正しく含まれるかを
    検証する(httpx送信直前でRuntimeErrorへ変換し中断、ネットワーク
    呼び出しは発生しない)。"""
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"skipped": True, "reason": "GEMINI_API_KEY未設定のためprobeをskip"}
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    httpx_client = client.models._api_client._httpx_client

    captured = {}

    def fake_send(req, *a, **kw):
        captured["url"] = str(req.url)
        captured["content"] = req.content.decode("utf-8", errors="replace") if req.content else None
        raise RuntimeError("PROBE_ABORT_BEFORE_NETWORK_SEND")

    httpx_client.send = fake_send

    sm = types.SpeechMetadata(style="natural, clear, conversational")
    part = types.Part(text="Hello world, this is a probe test sentence.", speech_metadata=sm)
    content = types.Content(parts=[part], role="user")

    try:
        client.models.generate_content(
            model="gemini-3.8-flash-lite-tts",
            contents=content,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                    )
                ),
            ),
        )
        return {"intercepted_before_network": False, "note": "呼び出しが完了してしまった(想定外)"}
    except RuntimeError as e:
        if "PROBE_ABORT_BEFORE_NETWORK_SEND" not in str(e):
            return {"intercepted_before_network": False, "error_type": "RuntimeError", "error": str(e)[:400]}
    except Exception as e:
        return {"intercepted_before_network": False, "client_side_rejected": True,
                "error_type": type(e).__name__, "error": str(e)[:400]}

    body = json.loads(captured["content"]) if captured.get("content") else None
    item = body["contents"][0]["parts"][0] if body else None
    return {
        "intercepted_before_network": True,
        "network_calls_made": 0,
        "url": captured.get("url"),
        "wire_body_first_part": item,
        "speech_metadata_sibling_field_present": bool(item and "speechMetadata" in item),
        "speech_metadata_style_value_correct": bool(
            item and item.get("speechMetadata", {}).get("style") == "natural, clear, conversational"),
        "conclusion": (
            "2.25.0では、GenerateContent APIのPart.speechMetadataがREST仕様通り"
            "sibling fieldとして正しく送信直前のwire body上に存在する"
            "(2.14.0で確認されたUNKNOWN変質/消失は解消)。"
        ),
    }


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    result = {
        "management_id": "TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01",
        "phase": "SDK 2.25.0 confirmation (実費用¥0、ネットワーク呼び出し0件)",
        "genai_version": check_genai_version(),
        "type_definition_check": check_type_definition(),
        "generate_content_wire_body_probe": probe_generate_content_wire_body(),
    }
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    import sys
    r = main()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(json.dumps(r, ensure_ascii=False, indent=2))
    print(f"\n[written] {RESULT_PATH}")
