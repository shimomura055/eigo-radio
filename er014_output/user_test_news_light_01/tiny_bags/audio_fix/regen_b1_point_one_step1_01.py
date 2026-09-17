# ============================================================
# er014_output/user_test_news_light_01/tiny_bags/audio_fix/
#   regen_b1_point_one_step1_01.py
# 管理ID: USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02
#
# 目的: B1 tiny_bags point_one("with room for only a few essentials"の
# "only"が3attemptとも実音声で脱落、STOPPED、Human Review Lock)に対する
# ユーザー承認済みStep 1(canonical無変更、時間をあけての正式TTS->ASR
# 経路1 cycle再生成)を実行する。
#
# 対象外(意図的に一切呼ばない): 記事本文再生成、他segmentのTTS再生成、
# Assembly(Step 1完了後の判定を見てから別途実行)。generate_b1_segments()
# を丸ごと呼ぶと全segmentが再生成されるため、point_one単体のみをここで
# 複製する(generate_b1_segments()内のpoint_oneループ本体と同一の呼び出し)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er014_output/user_test_news_light_01/tiny_bags/audio_fix/regen_b1_point_one_step1_01.py
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import er003_v1_n3_01_tts_generate as ttsgen
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er005_cost_logger as cl
import er008_disfluency_qa_18 as disfluency_qa
import er011_human_review_lock_01 as review_lock

THEME_ID = "tiny_bags"
BASE_DIR = "er014_output/user_test_news_light_01/tiny_bags"
OUT_DIR = f"{BASE_DIR}/b1b"
NARRATION_DIR = f"{OUT_DIR}/narration"
OUT_PATH = f"{NARRATION_DIR}/point_one.wav"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def main() -> None:
    parts = load_json(f"{OUT_DIR}/parts.json")
    text = parts["point_one_body"]
    print(f"[REGEN][b1b/point_one] Step 1: canonical無変更で再TTS。")
    print(f"[REGEN][b1b/point_one] canonical_text={text!r}")

    # ユーザー明示決定(USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02 Step 1)に
    # 基づき、Human Review Lockを1回だけ解除する。
    approve_result = review_lock.approve_regenerate(OUT_PATH, text, approved_by="user")
    print(f"[REGEN][b1b/point_one] approve_regenerate result state={approve_result.get('state')}")

    cl.install(f"{BASE_DIR}/audio_fix/raw_usage_log_audio_fix.jsonl")
    with cl.logging_context(THEME_ID, "b1b_point_one_step1_regen"):
        with cl.segment_context("point_one"):
            result = news_tail_fix.generate_news_narration_wide_margin(
                ttsgen.tts_safe_news_en(text), OUT_PATH,
                disfluency_qa=False,
                enable_connected_speech_equivalence_layer=True,
                enable_repetition_qa=True)
    result["canonical_text"] = text

    print(f"[REGEN][b1b/point_one] status={result.get('status')}")
    for a in result.get("attempts_log", []) or []:
        print(f"  attempt={a.get('attempt')} status={a.get('status')} "
              f"classification={a.get('audio_classification')} verified={a.get('verified')}")
        print(f"    asr_text={a.get('asr_text')!r}")

    # local faster-whisper verbatim(無料)で"only"が実際に発音されたかを
    # 追加確認する(ASR分類とは独立した証跡)。
    local_verbatim_text = None
    if os.path.exists(OUT_PATH):
        try:
            words = disfluency_qa.transcribe_verbatim(OUT_PATH, language="en", model_size="small")
            local_verbatim_text = " ".join(w["text"].strip() for w in words).strip()
        except Exception as exc:  # noqa: BLE001
            print(f"[REGEN][b1b/point_one] local faster-whisper失敗: {exc}")
    print(f"[REGEN][b1b/point_one] local_faster_whisper_verbatim={local_verbatim_text!r}")
    only_present_local = bool(local_verbatim_text) and "only" in local_verbatim_text.lower()
    print(f"[REGEN][b1b/point_one] 'only' present in local verbatim: {only_present_local}")

    # tts_generation_results.json / run_summary_tts.json / review_lock_state.json
    # は generate_news_narration_wide_margin() 内部(review_lock.guarded_
    # generate decorator)が既に更新済み(record_outcomeが自動実行される)。
    # ここでは診断用サマリのみ追加保存する。
    out = {
        "step": "STEP1_NO_CANONICAL_CHANGE",
        "canonical_text": text,
        "tts_status": result.get("status"),
        "attempts_log": result.get("attempts_log"),
        "local_faster_whisper_verbatim": local_verbatim_text,
        "only_present_in_local_verbatim": only_present_local,
    }
    save_json(f"{OUT_DIR}/audit/point_one_step1_regen_summary.json", out)
    print(f"[REGEN][b1b/point_one] 完了。summary保存: {OUT_DIR}/audit/point_one_step1_regen_summary.json")


if __name__ == "__main__":
    main()
