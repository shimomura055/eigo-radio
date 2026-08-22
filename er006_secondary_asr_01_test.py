# ============================================================
# er006_secondary_asr_01_test.py
# ============================================================
# 実行方法: .venv/Scripts/python.exe er006_secondary_asr_01_test.py
from __future__ import annotations

import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary


def test_cascade_disabled_matches_plain_evaluate_attempt():
    # cascade_enabled=False(既定)なら、val.evaluate_attempt()と完全に
    # 同じ挙動になること(後方互換)。
    canon = "The bench was tilted in March."
    asr = "The bench was tilted in March."
    prior = []
    r = secondary.evaluate_attempt_with_cascade_detail(
        canon, asr, prior, "dummy.wav", cascade_enabled=False)
    assert r["verified"] is True
    assert r["cascade_invoked"] is False
    print("PASS: test_cascade_disabled_matches_plain_evaluate_attempt")


def test_non_entity_mismatch_does_not_trigger_cascade():
    # 数字が変わっている等、固有名詞由来でない不一致はCascade対象外
    # (blind TTS retryへ委ねる、§8の限定条件)。
    orig_transcribe = routing.transcribe
    calls = {"n": 0}

    def fake_transcribe(*a, **k):
        calls["n"] += 1
        return "SHOULD NOT BE CALLED", None

    routing.transcribe = fake_transcribe
    try:
        canon = "The study followed 2 groups of participants."
        asr = "The study followed 3 groups of participants."
        prior = []
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, prior, "dummy.wav", cascade_enabled=True)
        assert r["cascade_invoked"] is False
        assert calls["n"] == 0, "数字違いのmismatchでCascadeのPrimary#2を呼んではならない"
    finally:
        routing.transcribe = orig_transcribe
    print("PASS: test_non_entity_mismatch_does_not_trigger_cascade")


def test_entity_like_mismatch_triggers_primary_2():
    orig_transcribe = routing.transcribe
    calls = {"n": 0}

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        calls["n"] += 1
        return "A Tony and colleagues published a study.", None  # 依然不一致

    routing.transcribe = fake_transcribe
    try:
        canon = "Ottoni and colleagues published a study."
        asr = "A Tony and colleagues published a study."  # 固有名詞のみの差
        prior = []
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, prior, "dummy.wav", cascade_enabled=True)
        assert r["cascade_invoked"] is True
        assert calls["n"] == 1, "Primary#2が1回呼ばれるはず"
        assert any(s["step"] == "primary_2" for s in r["steps"])
    finally:
        routing.transcribe = orig_transcribe
    print("PASS: test_entity_like_mismatch_triggers_primary_2")


def test_primary_2_pass_stops_cascade_before_secondary():
    orig_transcribe = routing.transcribe
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    calls = {"secondary": 0}

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "Ottoni and colleagues published a study.", None  # Primary#2で正しく認識

    def fake_secondary(*a, **k):
        calls["secondary"] += 1
        return "SHOULD NOT BE CALLED", None

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        canon = "Ottoni and colleagues published a study."
        asr = "A Tony and colleagues published a study."
        prior = []
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, prior, "dummy.wav", cascade_enabled=True)
        assert r["verified"] is True
        assert calls["secondary"] == 0, "Primary#2でPASSしたらSecondaryは呼ばれないはず"
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
    print("PASS: test_primary_2_pass_stops_cascade_before_secondary")


def test_full_cascade_all_fail_routes_to_human_review():
    orig_transcribe = routing.transcribe
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    calls = {"primary": 0, "secondary": 0}

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        calls["primary"] += 1
        return "A Tony and colleagues published a study.", None

    def fake_secondary(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
        calls["secondary"] += 1
        return "Otoni and colleagues published a study.", None  # 依然不一致(固有名詞のみ)

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        canon = "Ottoni and colleagues published a study."
        asr = "A Tony and colleagues published a study."
        prior = []
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, prior, "dummy.wav", ledger_phrases=["Ottoni"], cascade_enabled=True)
        assert calls["primary"] == 1, "Primary#2は1回のみ"
        assert calls["secondary"] == 2, "Secondary#1・#2の2回呼ばれるはず"
        assert r["human_review_required"] is True
        assert r["verified"] is False
        assert r["final_status"] == "ASR_VALIDATION_UNCERTAIN"
        step_names = [s["step"] for s in r["steps"]]
        assert step_names == ["primary_1", "primary_2", "secondary_1", "secondary_2"]
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
    print("PASS: test_full_cascade_all_fail_routes_to_human_review")


def test_secondary_1_pass_stops_before_secondary_2():
    orig_transcribe = routing.transcribe
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    calls = {"secondary": 0}

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "A Tony and colleagues published a study.", None

    def fake_secondary(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
        calls["secondary"] += 1
        return "Ottoni and colleagues published a study.", None  # Secondary#1でPASS

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        canon = "Ottoni and colleagues published a study."
        asr = "A Tony and colleagues published a study."
        prior = []
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, prior, "dummy.wav", ledger_phrases=["Ottoni"], cascade_enabled=True)
        assert r["verified"] is True
        assert calls["secondary"] == 1, "Secondary#1でPASSしたら#2は呼ばれないはず"
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
    print("PASS: test_secondary_1_pass_stops_before_secondary_2")


def test_is_entity_like_mismatch_excludes_number_diffs():
    canon = "The study followed 2 groups of participants."
    asr = "The study followed 3 groups of participants."
    cls = val.classify_asr_match(canon, asr)
    assert secondary.is_entity_like_mismatch(cls) is False
    print("PASS: test_is_entity_like_mismatch_excludes_number_diffs")


def test_is_entity_like_mismatch_true_for_proper_noun_only():
    canon = "Ottoni and colleagues published a study in 2016."
    asr = "A Tony and colleagues published a study in 2016."
    cls = val.classify_asr_match(canon, asr)
    assert cls.classification == "ASR_VALIDATION_UNCERTAIN"
    assert secondary.is_entity_like_mismatch(cls) is True
    print("PASS: test_is_entity_like_mismatch_true_for_proper_noun_only")


def test_tuple_wrapper_matches_val_evaluate_attempt_shape_and_logs_human_review():
    import os
    orig_log_path = secondary.HUMAN_REVIEW_LOG_PATH
    tmp_log = "er006_output/_test_human_review_queue_tmp.jsonl"
    secondary.HUMAN_REVIEW_LOG_PATH = tmp_log
    if os.path.exists(tmp_log):
        os.remove(tmp_log)
    orig_transcribe = routing.transcribe
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "A Tony and colleagues published a study.", None

    def fake_secondary(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
        return "Otoni and colleagues published a study.", None

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        canon = "Ottoni and colleagues published a study."
        asr = "A Tony and colleagues published a study."
        prior = []
        verified, stop_retrying, cls = secondary.evaluate_attempt_with_cascade(
            canon, asr, prior, "dummy.wav", ledger_phrases=["Ottoni"], cascade_enabled=True)
        assert verified is False
        assert stop_retrying is True
        assert cls.classification == "ASR_VALIDATION_UNCERTAIN"
        assert os.path.exists(tmp_log), "Human Review queueへログが書かれるはず"
        with open(tmp_log, encoding="utf-8") as f:
            import json
            record = json.loads(f.readline())
        assert record["canonical_text"] == canon
        assert len(record["steps"]) == 4
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        secondary.HUMAN_REVIEW_LOG_PATH = orig_log_path
        if os.path.exists(tmp_log):
            os.remove(tmp_log)
    print("PASS: test_tuple_wrapper_matches_val_evaluate_attempt_shape_and_logs_human_review")


if __name__ == "__main__":
    test_cascade_disabled_matches_plain_evaluate_attempt()
    test_non_entity_mismatch_does_not_trigger_cascade()
    test_entity_like_mismatch_triggers_primary_2()
    test_primary_2_pass_stops_cascade_before_secondary()
    test_full_cascade_all_fail_routes_to_human_review()
    test_secondary_1_pass_stops_before_secondary_2()
    test_is_entity_like_mismatch_excludes_number_diffs()
    test_is_entity_like_mismatch_true_for_proper_noun_only()
    test_tuple_wrapper_matches_val_evaluate_attempt_shape_and_logs_human_review()
    print("ALL TESTS PASSED")
