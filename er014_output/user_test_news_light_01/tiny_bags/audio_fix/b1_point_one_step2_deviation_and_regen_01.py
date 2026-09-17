# ============================================================
# er014_output/user_test_news_light_01/tiny_bags/audio_fix/
#   b1_point_one_step2_deviation_and_regen_01.py
# 管理ID: USER-TEST-NEWS-LIGHT-TOPIC-01-RESUME-02
#
# 目的: Step 1(canonical無変更での再TTS)が3attemptとも"only"脱落だった
# ため、ユーザー承認済みStep 2を実行する。
#  (1) canonicalを"with room for only a few essentials"->"with room for
#      just a few essentials"へ最小変更(article.md/parts.jsonは別途
#      Editツールで先に同期済み)。
#  (2) B1記事全体に対してLedger Deviation Checkを1回再実行(意味変更が
#      無いことの確認、Fact Checkerは再実行しない)。
#  (3) point_oneのみTTS->ASRを正式経路で再生成(approve_regenerate ->
#      generate_news_narration_wide_margin)。
#
# 対象外: 記事全体の再生成、他segmentのTTS再生成、Fact Checker再実行。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import er003_v1_en_direct_vfl_01_generate as vfl01
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
LEDGER_TXT_PATH = f"{BASE_DIR}/research/verified_fact_ledger.txt"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def step2_deviation_recheck() -> dict:
    with open(f"{OUT_DIR}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    with open(LEDGER_TXT_PATH, encoding="utf-8") as f:
        verified_ledger_text = f.read()
    assert "with room for just a few essentials" in article_text, "canonical変更が反映されていません"
    assert "with room for only a few essentials" not in article_text

    cl.install(f"{BASE_DIR}/audio_fix/raw_usage_log_audio_fix.jsonl")
    client = vfl01.get_client()
    with cl.logging_context(THEME_ID, "b1b_point_one_step2_deviation_recheck"):
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, hook_aware=True)
    parsed = deviation_result["parsed"]
    print(f"[STEP2][deviation] overall_status={parsed['overall_status']} "
          f"deviations={len(parsed['deviations'])}")
    for d in parsed["deviations"]:
        print(f"  - severity={d['severity']} claim={d['claim_in_article'][:80]!r} issue={d['issue'][:120]!r}")

    save_json(f"{OUT_DIR}/audit/deviation_recheck_step2_only_to_just.json",
              {k: v for k, v in deviation_result.items() if k != "parsed"} | {"parsed": parsed})
    # 主SSOT(ledger_deviation.json)もStep2最新結果へ更新する(元の記録は
    # audit/deviation_full_record.json[初回]とaudit/deviation_recheck_
    # step2_only_to_just.json[今回]の両方に残る、監査履歴は消さない)。
    save_json(f"{OUT_DIR}/ledger_deviation.json", parsed)
    return parsed


def step2_regen_point_one() -> dict:
    parts = load_json(f"{OUT_DIR}/parts.json")
    text = parts["point_one_body"]
    assert "with room for just a few essentials" in text
    print(f"[STEP2][regen] canonical_text={text!r}")

    approve_result = review_lock.approve_regenerate(OUT_PATH, text, approved_by="user")
    print(f"[STEP2][regen] approve_regenerate result state={approve_result.get('state')}")

    with cl.logging_context(THEME_ID, "b1b_point_one_step2_regen"):
        with cl.segment_context("point_one"):
            result = news_tail_fix.generate_news_narration_wide_margin(
                ttsgen.tts_safe_news_en(text), OUT_PATH,
                disfluency_qa=False,
                enable_connected_speech_equivalence_layer=True,
                enable_repetition_qa=True)
    result["canonical_text"] = text

    print(f"[STEP2][regen] status={result.get('status')}")
    for a in result.get("attempts_log", []) or []:
        print(f"  attempt={a.get('attempt')} status={a.get('status')} "
              f"classification={a.get('audio_classification')} verified={a.get('verified')}")
        print(f"    asr_text={a.get('asr_text')!r}")

    local_verbatim_text = None
    if os.path.exists(OUT_PATH):
        try:
            words = disfluency_qa.transcribe_verbatim(OUT_PATH, language="en", model_size="small")
            local_verbatim_text = " ".join(w["text"].strip() for w in words).strip()
        except Exception as exc:  # noqa: BLE001
            print(f"[STEP2][regen] local faster-whisper失敗: {exc}")
    print(f"[STEP2][regen] local_faster_whisper_verbatim={local_verbatim_text!r}")
    just_present_local = bool(local_verbatim_text) and "just" in local_verbatim_text.lower()
    print(f"[STEP2][regen] 'just' present in local verbatim: {just_present_local}")

    out = {
        "step": "STEP2_ONLY_TO_JUST",
        "canonical_text": text,
        "tts_status": result.get("status"),
        "attempts_log": result.get("attempts_log"),
        "local_faster_whisper_verbatim": local_verbatim_text,
        "just_present_in_local_verbatim": just_present_local,
    }
    save_json(f"{OUT_DIR}/audit/point_one_step2_regen_summary.json", out)
    return result


def main() -> None:
    deviation_parsed = step2_deviation_recheck()
    major = [d for d in deviation_parsed["deviations"] if d["severity"] == "MAJOR"]
    if major:
        print(f"[STEP2] MAJOR deviation検出、STOP。Local Rewriteはこのタスクの範囲外のためTTSへ進まない。")
        return
    result = step2_regen_point_one()
    print(f"[STEP2] 完了。最終status={result.get('status')}")


if __name__ == "__main__":
    main()
