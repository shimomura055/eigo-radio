# ============================================================
# er014_output/user_test_news_light_01/tiny_bags/audio_fix/
#   a2_full_story_part2_secondary_cascade_check.py
# 管理ID: USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02
#
# 目的: A2 full_story_part2(Toteme/Kallmeyer, Human Review Lock中)の
# 既存attempt音声(TTS再生成なし、attempt3=narration/full_story_part2.wav
# と同一)に対し、正式ASR cascade(er006_secondary_asr_01.
# evaluate_attempt_with_cascade_detail)をSecondary ASRまで実行する。
# OPEN-159(get_hint_for_text大文字小文字不一致バグ)によりPronunciation
# Ledger経由のPhrase Listが自動では渡らない可能性があるため、本タスク
# 委任文の指示に従いledger_phrasesを明示的に渡す(brand名一覧、confidence
# 判定はバイパスするが、これはHuman Review診断目的の1回限りのASR再評価
# であり、TTS再生成・自動PASS判定の書き換えは行わない)。
#
# 本スクリプトはProduction関数を呼ぶだけの診断スクリプトであり、
# Production module自体は一切変更しない。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import er005_cost_logger as cl
import er006_secondary_asr_01 as sec_asr
import er008_disfluency_qa_18 as disfluency_qa

OUT_DIR = "er014_output/user_test_news_light_01/tiny_bags/a2"
WAV_PATH = f"{OUT_DIR}/narration/attempts/full_story_part2_attempt3_minimalfallback.wav"
ATTEMPT_JSON = f"{OUT_DIR}/narration/attempts/full_story_part2_attempt3_minimalfallback.json"
CANONICAL_TEXT = (
    "The same pattern appeared in 2026. Small pouches appeared at Prada, Loewe, Miu Miu, and Valentino. "
    "At the same time, very large bags appeared at Celine, Altuzarra, Toteme, Stella McCartney, and Kallmeyer. "
    "Some Fall/Winter 2026 shoulder bags from Chanel, Miu Miu, and Bottega Veneta were even large enough for a laptop.\n\n"
    "Mini bags also received strong attention from fashion editors. One fashion magazine called them a major Fall 2026 "
    "styling direction. But another offered a more mixed view, saying that autumn was bringing back larger bags while "
    "still keeping smaller clutches and top-handle bags in the picture.\n\n"
    "One trend company also reported a 152% rise in retail adoption for oversized clutches in 2026. That is a company "
    "estimate, but it adds an important counterpoint.\n\n"
    "The clearest answer is this: tiny bags are gaining attention in some fashion spaces, but they are not winning "
    "everywhere. Small and large bags are appearing side by side."
)

LEDGER_PHRASES = [
    "Prada", "Loewe", "Miu Miu", "Valentino", "Celine", "Altuzarra", "Toteme",
    "Stella McCartney", "Kallmeyer", "Chanel", "Bottega Veneta",
]


def main() -> None:
    cl.install(f"{OUT_DIR}/../audio_fix/raw_usage_log_audio_fix.jsonl")
    with open(ATTEMPT_JSON, encoding="utf-8") as f:
        attempt = json.load(f)
    primary_asr_text = attempt["asr_text"]
    print(f"[CHECK] wav_path={WAV_PATH}")
    print(f"[CHECK] primary(attempt3) asr_text={primary_asr_text!r}")

    with cl.logging_context("tiny_bags", "a2_full_story_part2_secondary_cascade_check"):
        detail = sec_asr.evaluate_attempt_with_cascade_detail(
            CANONICAL_TEXT, primary_asr_text, prior_results=[], wav_path=WAV_PATH,
            language="en-US", ledger_phrases=LEDGER_PHRASES, max_same_signature=3,
            cascade_enabled=True)

        # 追加証跡: local faster-whisper verbatim(無料、実際にTTSがどう
        # 発音しているかの独立確認)。
        try:
            words = disfluency_qa.transcribe_verbatim(WAV_PATH, language="en", model_size="small")
            local_verbatim_text = " ".join(w["text"].strip() for w in words).strip()
        except Exception as exc:  # noqa: BLE001
            local_verbatim_text = None
            print(f"[CHECK] local faster-whisper失敗: {exc}")

    print("\n[CHECK] ==== cascade detail ====")
    for step in detail["steps"]:
        print(f"  step={step.get('step')} provider={step.get('provider')} "
              f"classification={step.get('classification')} phrase_list_used={step.get('phrase_list_used')}")
        print(f"    text={step.get('text')!r}")
    print(f"[CHECK] final_status={detail['final_status']} verified={detail['verified']} "
          f"cascade_invoked={detail['cascade_invoked']} human_review_required={detail['human_review_required']}")
    print(f"[CHECK] cost_guard_triggered={detail['cost_guard_triggered']}")
    print(f"[CHECK] local_faster_whisper_verbatim={local_verbatim_text!r}")

    out = {
        "wav_path": WAV_PATH,
        "canonical_text": CANONICAL_TEXT,
        "ledger_phrases_passed": LEDGER_PHRASES,
        "steps": detail["steps"],
        "final_status": detail["final_status"],
        "verified": detail["verified"],
        "cascade_invoked": detail["cascade_invoked"],
        "human_review_required": detail["human_review_required"],
        "cost_guard_triggered": detail["cost_guard_triggered"],
        "pronunciation_lookups": detail.get("pronunciation_lookups", {}),
        "local_faster_whisper_verbatim": local_verbatim_text,
    }
    out_path = f"{OUT_DIR}/audit/full_story_part2_secondary_cascade_check_with_phrase_list.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"[CHECK] 保存: {out_path}")


if __name__ == "__main__":
    main()
