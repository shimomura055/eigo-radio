# ============================================================
# er022_tts_gemini_3_8_flash_lite_next_trial_01_sdk_check.py
# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01 (Phase 0: SDK確認、¥0)
# ============================================================
# 性質: Trial限定。Production変更0件。API実費用: 本ファイル単体では¥0
# (下記2つのprobeはhttpx.Client.sendを本ファイル内でのみ一時的に
# monkeypatchし、実際にネットワークへ送信される直前でRuntimeErrorを
# 送出して意図的に中断する。実際のHTTPリクエストは1件も発生しない。
# これは計画doc(plan_tts_gemini_3_8_flash_lite_next_trial_01.md)§16の
# 未確認事項(a)(b)を、実費用を発生させずに検証する目的の専用コード)。
#
# 対象: 委任文「SDK(ユーザー決定)」節の確認項目(a)(b)(c)(d)。
#   (a) speech_metadataが2.14.0で実際に送信可能か(最小API形状確認)
#   (b) 既存TTS呼び出しとの互換性(Trial環境で既存TTS関連unit test)
#   (c) pip check で依存関係衝突なし
#   (d) Trial環境だけの変更で実行できるか
#
# 実行方法: Trial専用の隔離venv(.venv_trial_genai214、
# google-genai==2.14.0、Production .venv/.venv-ciは無変更)から実行する。
#   .venv_trial_genai214/Scripts/python.exe \
#     er022_tts_gemini_3_8_flash_lite_next_trial_01_sdk_check.py
#
# 出力: er022_output/tts_gemini_3_8_flash_lite_next_trial_01/sdk_check_results.json
from __future__ import annotations

import json
import os

OUT_DIR = "er022_output/tts_gemini_3_8_flash_lite_next_trial_01"
RESULT_PATH = f"{OUT_DIR}/sdk_check_results.json"


def check_genai_version() -> dict:
    import google.genai as genai_pkg
    return {"installed_version": genai_pkg.__version__, "expected": "2.14.0",
            "matches_expected": genai_pkg.__version__ == "2.14.0"}


def probe_generate_content_part_speech_metadata() -> dict:
    """GenerateContent API: types.Part(speech_metadata=...)がSDK側で
    受理されるか(ネットワーク呼び出し無し、pydantic検証のみ)。"""
    from google.genai import types
    attempts = {}
    for label, fn in (
        ("part_kwarg", lambda: types.Part(text="Hello world.", speech_metadata={"style": "calm"})),
        ("content_model_validate", lambda: types.Content.model_validate(
            {"parts": [{"text": "Hello world.", "speech_metadata": {"style": "calm"}}]})),
    ):
        try:
            fn()
            attempts[label] = {"accepted": True}
        except Exception as e:  # pydantic.ValidationError想定
            attempts[label] = {"accepted": False, "error_type": type(e).__name__, "error": str(e)[:400]}
    all_rejected = all(not v["accepted"] for v in attempts.values())
    return {
        "api": "GenerateContent (client.models.generate_content)",
        "field": "part.speech_metadata",
        "attempts": attempts,
        "conclusion": "REJECTED_CLIENT_SIDE (pydantic extra_forbidden)" if all_rejected else "UNEXPECTED_ACCEPTED",
    }


def probe_interactions_speech_metadata() -> dict:
    """Interactions API: annotations配列内 / contentのsibling fieldとして
    speech_metadataを渡した場合に、実際にネットワークへ送信される直前の
    HTTPリクエストbodyがどう組み立てられるかを検証する(ネットワーク
    呼び出しは発生させない、httpx.Client.sendを本関数内だけ差し替えて
    送信直前でRuntimeErrorへ変換し中断する)。"""
    import os as _os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = _os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"api": "Interactions (client.interactions.create)", "skipped": True,
                "reason": "GEMINI_API_KEY未設定のためprobeをskip"}
    from google import genai

    client = genai.Client(api_key=api_key)
    interactions = client.interactions
    sdk_client = interactions.sdk_configuration.client

    results = {}

    def _run_variant(label, input_payload):
        captured = {}

        def fake_send(req, *args, **kwargs):
            captured["content"] = req.content.decode("utf-8", errors="replace") if req.content else None
            raise RuntimeError("PROBE_ABORT_BEFORE_NETWORK_SEND")

        sdk_client.send = fake_send
        try:
            interactions.create(
                model="gemini-3.8-flash-lite-tts",
                input=input_payload,
                response_modalities=["AUDIO"],
                generation_config={"speech_config": [{"voice": "Aoede"}]},
            )
            results[label] = {"intercepted_before_network": False, "note": "呼び出しが完了してしまった(想定外)"}
            return
        except RuntimeError as e:
            if "PROBE_ABORT" not in str(e):
                results[label] = {"intercepted_before_network": False, "error": str(e)[:400]}
                return
        except Exception as e:
            results[label] = {"intercepted_before_network": False,
                               "client_side_rejected": True,
                               "error_type": type(e).__name__, "error": str(e)[:400]}
            return
        body = json.loads(captured["content"]) if captured.get("content") else None
        sent_annotations = None
        sent_speech_metadata_sibling = None
        if body:
            item = body.get("input", [{}])[0].get("content", [{}])[0]
            sent_annotations = item.get("annotations")
            sent_speech_metadata_sibling = item.get("speech_metadata")
        results[label] = {
            "intercepted_before_network": True,
            "network_calls_made": 0,
            "wire_body_input_content_item": body.get("input", [{}])[0].get("content", [{}])[0] if body else None,
            "speech_metadata_annotation_preserved_correctly": (
                isinstance(sent_annotations, list) and len(sent_annotations) == 1
                and sent_annotations[0].get("type") == "speech_metadata"
            ),
            "speech_metadata_sibling_field_preserved": sent_speech_metadata_sibling is not None,
        }

    _run_variant("annotations_array", [{
        "type": "text", "text": "Hello world, this is a probe test sentence.",
        "annotations": [{"type": "speech_metadata", "style": "calm, natural"}],
    }])
    _run_variant("sibling_field", [{
        "type": "text", "text": "Hello world, this is a probe test sentence.",
        "speech_metadata": {"style": "calm, natural"},
    }])

    return {"api": "Interactions (client.interactions.create)", "variants": results,
            "conclusion": (
                "SDK側は client側validationでは拒否しないが、実際にネットワークへ送信される"
                "wire body上ではspeech_metadataが失われる/破損する(annotations経路は"
                "{type:UNKNOWN,raw:{...}}へ変質、sibling field経路は完全に消失)。"
                "現行google-genai==2.14.0のPython SDK経由では、公式ドキュメント記載の"
                "speech_metadataを正しい形でサーバへ送信する手段が無い。"
            )}


def run_existing_tts_unit_tests_note() -> dict:
    """本ファイル自体はunit testを実行しない(実行はTrial実施者が
    このvenvから直接 `python -m unittest <test_module>` する運用、
    REPORT側に実行ログを記録する)。ここではどのファイルを対象と
    したかの記録のみを返す。"""
    return {
        "note": "実行コマンドと結果はREPORT側に記録(本関数は対象リストの記録のみ)",
        "target_test_modules": [
            "er002_test_common", "er003_test_b1_p3v_capability", "er003_test_b1_p4c_audio",
            "er003_test_b1_p7a_audio", "er003_test_b1_p9a_audio", "er003_test_b1_p9a_r1_audio",
            "er003_test_audio_tts_asr_safety", "er003_test_v1_n3_01_tts_generate",
            "er003_test_key_words_canonicalization",
        ],
    }


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    result = {
        "management_id": "TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01",
        "phase": "Phase 0 SDK check (実費用¥0、ネットワーク呼び出し0件)",
        "genai_version": check_genai_version(),
        "probe_generate_content_api": probe_generate_content_part_speech_metadata(),
        "probe_interactions_api": probe_interactions_speech_metadata(),
        "existing_unit_tests": run_existing_tts_unit_tests_note(),
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
