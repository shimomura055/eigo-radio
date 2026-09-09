# ============================================================
# legacy_stopped_segments_asr_reverify.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続、
# Fable修正指示2回目)
# ============================================================
# topic_intro/kp2_english(2026-08-17当時、いずれも6回試行後にstatus=
# STOPPEDで終端。ASRが一貫して canonical "crisper" を "CRISPR" と
# 書き起こしていた)を対象に、現行Production ASR Cascade
# (er006_secondary_asr_01.evaluate_attempt_with_cascade_detail、
# Primary#1/#2 -> Secondary#1/#2 Azure、entity_like/homophone Case A
# 判定含む)を、既存の音声ファイル(narration/topic_intro.wav・
# narration/kp2_en.wav、byte不変・読み取り専用)へそのまま再実行する。
# TTSは一切呼ばない(routing.transcribe/Azure ASRのみ、費用はASRのみ)。
#
# 目的: 2026-08-17当時のASR Validatorには存在しなかったCase A
# (entity_span_arpabet_match、ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15、
# 2026-08-28導入)等、その後追加された既存QA改善が、このlegacy音声を
# 今なら正しく通過させられるかどうかを、実際のASR再照合で確認する。
# 承認記録の遡及作成(human_approved_segments.json)は一切行わない。
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er003_v1_n3_01_tts_generate as n3
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr

OUT_DIR = "er003_output/n3_01/household/fact03_fix_02/b1b"
NARRATION_DIR = f"{OUT_DIR}/narration"
TTS_RESULTS_PATH = f"{OUT_DIR}/audit/tts_generation_results.json"
COST_LOG_PATH = (
    "er011_output/open138_household_fact03_b1b_minimal_fix_02/"
    "raw_usage_log_legacy_stopped_asr_reverify.jsonl"
)
RESULT_SUMMARY_PATH = (
    "er011_output/open138_household_fact03_b1b_minimal_fix_02/"
    "legacy_stopped_segments_asr_reverify_summary.json"
)


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    parts = json.load(open(OUT_DIR + "/parts.json", encoding="utf-8"))
    kp = json.load(open(f"{OUT_DIR}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
    kp2_used_form = next(it["used_form"] for it in kp["items"] if it["rank"] == 2)

    topic_intro_text = f"Today's topic is {parts['title']}."
    canonical_topic_intro = n3.tts_safe_number_words_en(n3.tts_safe_en(topic_intro_text))
    canonical_kp2 = n3.tts_safe_kp_en(kp2_used_form)

    targets = [
        {
            "name": "topic_intro", "wav_path": f"{NARRATION_DIR}/topic_intro.wav",
            "canonical_text": canonical_topic_intro, "enable_non_latin_cascade": False,
            "result_path": ("segments", "topic_intro"),
        },
        {
            "name": "kp2_english", "wav_path": f"{NARRATION_DIR}/kp2_en.wav",
            "canonical_text": canonical_kp2, "enable_non_latin_cascade": True,
            "result_path": ("key_phrases", "2", "english"),
        },
    ]

    cl.install(COST_LOG_PATH)
    tts_results = json.load(open(TTS_RESULTS_PATH, encoding="utf-8"))
    summary = {}
    all_pass = True

    for t in targets:
        name = t["name"]
        wav_path = t["wav_path"]
        assert os.path.exists(wav_path), f"wavが存在しません: {wav_path}"
        before_sha256 = sha256_of(wav_path)

        with cl.logging_context("HOUSEHOLD-FACT-03-MINIMAL-FIX-02-LEGACY-GATE",
                                 "legacy_stopped_asr_reverify"), cl.segment_context(name):
            asr_text, asr_err = routing.transcribe(wav_path, language="en-US")
            ledger_phrases = [
                h["canonical_spelling"]
                for h in pronun_ledger.get_hint_for_text(t["canonical_text"], min_confidence="low")
            ]
            detail = secondary_asr.evaluate_attempt_with_cascade_detail(
                t["canonical_text"], asr_text, [], wav_path, language="en-US",
                ledger_phrases=ledger_phrases, cascade_enabled=True,
                enable_non_latin_cascade=t["enable_non_latin_cascade"])

        after_sha256 = sha256_of(wav_path)
        assert before_sha256 == after_sha256, f"{name}: wavがASR再照合中に変化しました(禁止事項違反)"

        cls = detail["classification"]
        verified = bool(detail["verified"])
        if not verified:
            all_pass = False

        # tts_generation_results.jsonへ証跡追記(元のstatus="STOPPED"は
        # 監査のため保持し、事後再照合の結果を別フィールドへ記録する。
        # 再生成していないため、statusを勝手にOKへ書き換えることはしない
        # ——Gateが実際にPASSと扱えるかは、この証跡を見た人間/Fableが
        # 判断する)。
        node = tts_results
        for key in t["result_path"][:-1]:
            node = node[key]
        entry = node[t["result_path"][-1]]
        entry["legacy_asr_reverify"] = {
            "canonical_text": t["canonical_text"],
            "primary_1_asr_text": asr_text,
            "verified": verified,
            "final_status": detail["final_status"],
            "cascade_invoked": detail["cascade_invoked"],
            "non_latin_cascade_invoked": detail["non_latin_cascade_invoked"],
            "human_review_required": detail["human_review_required"],
            "steps": detail["steps"],
            "pronunciation_lookups": detail.get("pronunciation_lookups"),
            "note": (
                "HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続): "
                "既存wav(byte不変、TTS再生成なし)へ現行ASR Cascade "
                "(er006_secondary_asr_01.evaluate_attempt_with_cascade_detail)を"
                "事後適用した証跡。statusフィールド自体は2026-08-17当時のSTOPPED"
                "記録のまま変更していない(Gateの合否判断はこのフィールドを見た"
                "人間/Fableが行うこと、承認記録の遡及作成はしていない)。"
            ),
        }

        summary[name] = {
            "wav_path": wav_path, "wav_sha256": before_sha256,
            "canonical_text": t["canonical_text"],
            "primary_1_asr_text": asr_text,
            "verified": verified, "final_status": detail["final_status"],
            "classification": cls.classification, "should_pass": cls.should_pass,
            "reason": cls.reason,
            "content_word_diffs": cls.protected.content_word_diffs,
            "cascade_invoked": detail["cascade_invoked"],
            "steps": detail["steps"],
            "human_review_required": detail["human_review_required"],
            "pronunciation_lookups": detail.get("pronunciation_lookups"),
            "result": "PASS" if verified else "FAIL",
        }
        print(f"[legacy_stopped_asr_reverify] {name}: verified={verified} "
              f"final_status={detail['final_status']} "
              f"({'PASS' if verified else 'FAIL'})")

    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)

    with open(RESULT_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump({"all_pass": all_pass, "segments": summary}, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n[legacy_stopped_asr_reverify] all_pass={all_pass}")
    print(f"[legacy_stopped_asr_reverify] summary -> {RESULT_SUMMARY_PATH}")
    print(f"[legacy_stopped_asr_reverify] tts_generation_results.json更新 -> {TTS_RESULTS_PATH}")


if __name__ == "__main__":
    main()
