# ============================================================
# er006_secondary_asr_01_test.py
# ============================================================
# 実行方法: .venv/Scripts/python.exe er006_secondary_asr_01_test.py
from __future__ import annotations

import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as secondary


def test_primary_pass_skips_secondary():
    orig_transcribe = routing.transcribe
    orig_secondary = secondary.get_full_text_via_azure_stt_with_phrase_list
    calls = {"secondary": 0}

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "The bench was tilted in March.", None

    def fake_secondary(*args, **kwargs):
        calls["secondary"] += 1
        return "SHOULD NOT BE CALLED", None

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        r = secondary.evaluate_with_secondary_cascade(
            "The bench was tilted in March.", "dummy.wav", secondary_enabled=True)
        assert r["final_status"] in ("EXACT_MATCH", "NORMALIZED_MATCH")
        assert calls["secondary"] == 0, "PrimaryがPASSならSecondaryは呼ばれないはず"
        assert r["secondary"] is None
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary
    print("PASS: test_primary_pass_skips_secondary")


def test_secondary_disabled_by_flag_stays_primary_only():
    orig_transcribe = routing.transcribe
    orig_secondary = secondary.get_full_text_via_azure_stt_with_phrase_list
    calls = {"secondary": 0}

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "A completely different sentence.", None

    def fake_secondary(*args, **kwargs):
        calls["secondary"] += 1
        return "irrelevant", None

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        r = secondary.evaluate_with_secondary_cascade(
            "The bench was tilted in March.", "dummy.wav", secondary_enabled=False)
        assert calls["secondary"] == 0, "feature flag OFFならSecondaryは絶対呼ばれないはず"
        assert r["secondary"] is None
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary
    print("PASS: test_secondary_disabled_by_flag_stays_primary_only")


def test_secondary_pass_after_primary_uncertain():
    orig_transcribe = routing.transcribe
    orig_secondary = secondary.get_full_text_via_azure_stt_with_phrase_list

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "Malmo's Triangle station had a tilted bench.", None  # 固有名詞の音訳差のみ

    def fake_secondary(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
        return "Malmö's Triangeln station had a tilted bench.", None  # Phrase Listで正確に認識

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        r = secondary.evaluate_with_secondary_cascade(
            "Malmö's Triangeln station had a tilted bench.", "dummy.wav",
            ledger_phrases=["Malmö", "Triangeln"], secondary_enabled=True)
        assert r["secondary"] is not None
        assert r["final_status"] in ("EXACT_MATCH", "NORMALIZED_MATCH")
        assert r["reason"].startswith("PrimaryはFAIL")
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary
    print("PASS: test_secondary_pass_after_primary_uncertain")


def test_both_asr_agree_on_true_mismatch_recommends_retry():
    orig_transcribe = routing.transcribe
    orig_secondary = secondary.get_full_text_via_azure_stt_with_phrase_list

    # 両方のASRが同じ、canonicalと明確に異なる内容を返す(数字が変わっている)
    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "The study followed 3 groups of participants.", None

    def fake_secondary(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
        return "The study followed 3 groups of participants.", None

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        r = secondary.evaluate_with_secondary_cascade(
            "The study followed 2 groups of participants.", "dummy.wav", secondary_enabled=True)
        assert r["final_status"] == "TRUE_CONTENT_MISMATCH"
        assert r["retry_recommended"] is True
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary
    print("PASS: test_both_asr_agree_on_true_mismatch_recommends_retry")


def test_asr_disagree_on_proper_noun_does_not_recommend_retry():
    orig_transcribe = routing.transcribe
    orig_secondary = secondary.get_full_text_via_azure_stt_with_phrase_list

    # PrimaryとSecondaryが違う誤認識をする(固有名詞のtransliteration差、
    # 内容自体は変わっていない) -> 一貫した"同じ内容差"ではないため、
    # TTS retryは推奨しない(Human Review対象)。
    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "A Tony and colleagues looked at three neighborhoods.", None

    def fake_secondary(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
        return "O'Toole and colleagues looked at three neighborhoods.", None

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        r = secondary.evaluate_with_secondary_cascade(
            "Ottoni and colleagues looked at three neighborhoods.", "dummy.wav", secondary_enabled=True)
        assert r["retry_recommended"] is False, "固有名詞だけの表記差でTTS retryを推奨してはならない"
        assert r["final_status"] == "ASR_VALIDATION_UNCERTAIN"
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary
    print("PASS: test_asr_disagree_on_proper_noun_does_not_recommend_retry")


if __name__ == "__main__":
    test_primary_pass_skips_secondary()
    test_secondary_disabled_by_flag_stays_primary_only()
    test_secondary_pass_after_primary_uncertain()
    test_both_asr_agree_on_true_mismatch_recommends_retry()
    test_asr_disagree_on_proper_noun_does_not_recommend_retry()
    print("ALL TESTS PASSED")
