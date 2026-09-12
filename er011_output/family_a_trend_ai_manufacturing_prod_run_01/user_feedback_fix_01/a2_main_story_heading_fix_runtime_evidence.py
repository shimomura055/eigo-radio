# ============================================================
# a2_main_story_heading_fix_runtime_evidence.py
# 管理ID: FAMILY-A-TREND-AI-MANUFACTURING-USER-LISTENING-FEEDBACK-FIX-01
# ============================================================
# 目的: a2/article.md から不要な "## Main story" 見出し行を除去した後
# (このscriptの外で編集済み)、Production関数
# er003_v1_n3_01_scaffold_generate.py::split_article_text (無変更) を
# 再実行してparts.jsonを作り直し、変化した`part1`のみ、Production関数
# er003_v1_n3_01_tts_generate.py::generate_a2_segment_with_slowdown
# (無変更、既存呼び出しと同一引数の組み合わせ)でnarration/full_story_
# part1.wavのみ上書きする(他segmentは呼ばない)。
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er005_cost_logger as cl
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as n3

THEME_ID = "family_a_trend_ai_manufacturing_prod_run_01"
OUT_DIR = f"er011_output/{THEME_ID}/a2"
NARRATION_DIR = f"{OUT_DIR}/narration"
PARTS_PATH = f"{OUT_DIR}/parts.json"
TTS_RESULTS_PATH = f"{OUT_DIR}/audit/tts_generation_results.json"
COST_LOG_PATH = f"er011_output/{THEME_ID}/user_feedback_fix_01/raw_usage_log_a2_fix.jsonl"
RUN_SUMMARY_PATH = f"er011_output/{THEME_ID}/user_feedback_fix_01/a2_main_story_heading_fix_run_summary.json"

TARGET_NAME = "full_story_part1"
TARGET_FIELD = "part1"


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    assert os.environ.get("TTS_EXECUTION_MODE", "").upper() == "STANDARD", (
        "TTS_EXECUTION_MODE=STANDARD を明示的に指定して実行すること。"
    )

    with open(f"{OUT_DIR}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    assert "## Main story" not in article_text, "article.mdの見出し除去が未実施です。"

    old_parts = json.load(open(PARTS_PATH, encoding="utf-8"))
    # Production関数(無変更)を修正済みarticle.mdへ再実行する(artifact側の
    # 整形。関数コード自体は一切変更しない)。
    new_parts = sc.split_article_text(article_text)

    assert "## Main story" not in new_parts[TARGET_FIELD], "part1から見出しが除去されていません。"
    assert new_parts["part2"] == old_parts["part2"], (
        "part2の内容が変化しています(想定外、見出し除去のみのはずです)。"
    )
    for key in ("title", "point_one_heading", "point_one_body", "point_two_heading", "point_two_body",
                "in_one_line"):
        assert new_parts[key] == old_parts[key], f"{key}が意図せず変化しています。"

    with open(PARTS_PATH, "w", encoding="utf-8") as f:
        json.dump(new_parts, f, ensure_ascii=False, indent=2)

    tts_results = json.load(open(TTS_RESULTS_PATH, encoding="utf-8"))
    cl.install(COST_LOG_PATH)

    canonical_text = new_parts[TARGET_FIELD]
    tts_input = n3.tts_safe_news_en(canonical_text)
    sub = n3.first_words(canonical_text)
    out_path = f"{NARRATION_DIR}/{TARGET_NAME}.wav"
    old_sha256 = sha256_of(out_path) if os.path.exists(out_path) else None

    t0 = time.time()
    with cl.logging_context(THEME_ID, "full_story_part1_a2_heading_fix"), cl.segment_context(TARGET_NAME):
        # er003_v1_n3_01_tts_generate.py::generate_a2_segments()がfull_story_
        # part1に実際に渡している引数と同一組み合わせ(disfluency_qa=False
        # 既定、enable_connected_speech_equivalence_layer=True、
        # enable_repetition_qa=True)。
        result = n3.generate_a2_segment_with_slowdown(
            tts_input, out_path, sub,
            style_prefix_override=n3.A2_ENGLISH_STYLE_PREFIX_SLOWER,
            disfluency_qa=False,
            enable_connected_speech_equivalence_layer=True,
            enable_repetition_qa=True,
        )
    elapsed = time.time() - t0

    assert result.get("status") == "OK", (
        f"{TARGET_NAME}の生成がstatus={result.get('status')}で終了しました。"
        f"Human Review Lock等が発動した可能性があるため停止します。result={result}"
    )

    new_sha256 = sha256_of(out_path)
    result["canonical_text"] = canonical_text
    result["sha256"] = new_sha256
    result["source_note"] = (
        "FAMILY-A-TREND-AI-MANUFACTURING-USER-LISTENING-FEEDBACK-FIX-01: "
        "article.mdに混入していた不要な'## Main story'見出し行を除去した後、"
        "Production関数split_article_text(無変更)を再実行してparts.json[part1]"
        "を再生成し、Production関数generate_a2_segment_with_slowdown(無変更、"
        "既存呼び出しと同一引数)で再生成した。"
    )
    tts_results["segments"][TARGET_NAME] = result

    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)

    summary = {
        "target": TARGET_NAME,
        "old_sha256": old_sha256,
        "new_sha256": new_sha256,
        "canonical_text": canonical_text,
        "tts_input": tts_input,
        "asr_verified": result.get("asr_verified"),
        "asr_text": result.get("asr_text"),
        "status": result.get("status"),
        "slowdown_applied": result.get("slowdown_applied"),
        "elapsed_seconds": round(elapsed, 2),
    }
    os.makedirs(os.path.dirname(RUN_SUMMARY_PATH), exist_ok=True)
    with open(RUN_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
