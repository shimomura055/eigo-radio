# ============================================================
# er003_v1_b1_p5b_generate.py
# ER-003-B1-P5B: Google Cloud TTS／Amazon Polly比較検証
# ============================================================
# P5A(Azure Speech ja-JP-NanamiNeural)はユーザー試聴で不合格(全体の
# 不自然さ、「なにがおきる」→「なんがおきる」)。本ステージでは、Azure
# への追加調整は行わず、Google Cloud TTS・Amazon Pollyの利用可否を
# 実クライアント呼び出しで確認する。いずれも認証情報が本実行環境に
# 存在しないため、実際の音声合成は実行していない(指示section5・
# section3の明記通り、勝手な代替は行わない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p5b_generate.py

from __future__ import annotations

import hashlib
import json
import os

import er003_b1_p5a_audio as p5a
import er003_b1_p5b_audio as p5b

OUT_DIR = "er003_output/b1_p5b/A01"
MANAGEMENT_ID = "ER-003-B1-P5B"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _mkdirs() -> None:
    for sub in ("source", "instruction"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


def run() -> dict:
    _mkdirs()

    p4d_input = p5a.load_p4d_input()  # P5Aと同一sha256であることを内部で保証(不一致ならここで例外)

    with open(f"{OUT_DIR}/source/source_hashes.json", "w", encoding="utf-8") as f:
        json.dump({
            "p4d_hiragana_script_path": p5a.P4D_HIRAGANA_SCRIPT_PATH,
            "p4d_hiragana_script_sha256_full": p4d_input["sha256"],
            "matches_p5a_input": p4d_input["sha256"] == p5a.P4D_EXPECTED_HIRAGANA_SHA256,
        }, f, ensure_ascii=False, indent=2)

    google_availability = p5b.check_google_cloud_tts_availability()
    aws_availability = p5b.check_aws_polly_availability()

    with open(f"{OUT_DIR}/source/availability.json", "w", encoding="utf-8") as f:
        json.dump({"google_cloud_tts": google_availability, "amazon_polly": aws_availability}, f, ensure_ascii=False, indent=2)

    results = {
        "google_cloud_tts": {"status": "NOT_EXECUTED", "availability": google_availability} if not google_availability["available"]
            else {"status": "NOT_IMPLEMENTED", "reason": "認証情報は利用可能だが、実際の合成呼び出しコードは今回未実装(応答形式を実機検証してから実装するため)"},
        "amazon_polly": {"status": "NOT_EXECUTED", "availability": aws_availability} if not aws_availability["available"]
            else {"status": "NOT_IMPLEMENTED", "reason": "認証情報は利用可能だが、実際の合成呼び出しコードは今回未実装(応答形式を実機検証してから実装するため)"},
    }

    return {"status": "OK", "p4d_input": p4d_input, "results": results}


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    for engine, r in result["results"].items():
        print(engine, "->", r["status"])
