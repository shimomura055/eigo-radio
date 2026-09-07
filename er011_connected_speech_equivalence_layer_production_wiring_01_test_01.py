# ============================================================
# er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py
# OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01
# ============================================================
# 実行方法: .venv/Scripts/python.exe er011_connected_speech_equivalence_
# layer_production_wiring_01_test_01.py
#
# 監視対象: er011_connected_speech_equivalence_layer_production_01.py
# (判定ロジック本体)、er006_secondary_asr_01.py(Cascade層への配線)、
# er006_preprod_hardening_01_validation.py(VALID_CLASSIFICATIONS追加)。
from __future__ import annotations

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary
import er008_disfluency_qa_18 as disfluency_qa
import er011_connected_speech_equivalence_layer_production_01 as cs_equiv


# ------------------------------------------------------------
# Part 1: 判定ロジック本体(Trial-01/02の既存fixtureで無回帰確認)
# ------------------------------------------------------------
def test_existing_3_pattern_unchanged_pattern_a():
    r = cs_equiv.classify_connected_speech_equivalence(
        "The studies suggest that a phone can affect attention even when you do not check it.",
        "The study suggests that a phone can affect attention even when you do not check it.")
    assert r["layer_judgment"] == "CONNECTED_SPEECH_ACCEPT"
    assert r["source"] == "existing_3_pattern_unchanged"
    print("PASS: test_existing_3_pattern_unchanged_pattern_a")


def test_existing_3_pattern_unchanged_pattern_c_resegmentation():
    r = cs_equiv.classify_connected_speech_equivalence(
        "The studies and the survey suggest that a phone can affect people even when they do not check it.",
        "The studies and the surveys suggest that a phone can affect people even when they do not check it.")
    assert r["layer_judgment"] == "CONNECTED_SPEECH_RESEGMENTATION"
    assert r["source"] == "existing_3_pattern_unchanged"
    print("PASS: test_existing_3_pattern_unchanged_pattern_c_resegmentation")


def test_unrelated_mismatch_not_a_phoneme_prefix_drop():
    r = cs_equiv.classify_connected_speech_equivalence(
        "The report shows a clear increase in visits.",
        "The report shows a clear decrease in visits.")
    assert r["layer_judgment"] == "NOT_A_PHONEME_PREFIX_DROP"
    print("PASS: test_unrelated_mismatch_not_a_phoneme_prefix_drop")


def test_flagship_showed_strong_accepts_with_real_evidence():
    # OPEN-112 Theme2診断の実データ(既存保全済み、追加課金なし)。
    import json
    raw = json.load(open(
        "er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/"
        "point_two_showed_show_diag/diag_raw_evidence.json", encoding="utf-8"))
    canonical = raw["canonical_text"]
    primary1 = next(r["asr_text"] for r in raw["production_asr_full_noprompt"] if r["label"] == "attempt1")
    secondary1 = next(r["asr_text"] for r in raw["secondary_asr_full"] if r["label"] == "attempt1")
    local1 = next(r["transcript"] for r in raw["local_verbatim_full"] if r["label"] == "attempt1")
    r = cs_equiv.classify_connected_speech_equivalence(canonical, primary1, secondary1, local1)
    assert r["layer_judgment"] == "EQUIVALENCE_LAYER_ACCEPT"
    cats = {c["category"] for c in r["equivalence_layer_info"]["categories_matched"]}
    assert cats & {"A", "B", "C"}
    print("PASS: test_flagship_showed_strong_accepts_with_real_evidence")


def test_no_corroboration_insufficient_evidence():
    r = cs_equiv.classify_connected_speech_equivalence(
        "Young travelers still showed strong interest in the results.",
        "Young travelers still show strong interest in the results.",
        secondary_asr_text="Young travelers still show strong interest in the results.",
        local_asr_text="Young travelers still show strong interest in the results.")
    assert r["layer_judgment"] == "EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE"
    print("PASS: test_no_corroboration_insufficient_evidence")


def test_mixed_evidence_not_accepted():
    r = cs_equiv.classify_connected_speech_equivalence(
        "The cars turned back before reaching the bridge.",
        "The cars turn back before reaching the bridge.",
        secondary_asr_text="The cars turned back before reaching the bridge.",  # 誤支持
        local_asr_text="The cars turn back before reaching the bridge.")  # 正しく否定
    assert r["layer_judgment"] == "EQUIVALENCE_LAYER_MIXED_EVIDENCE_INSUFFICIENT"
    print("PASS: test_mixed_evidence_not_accepted")


def test_never_eligible_judgments_are_cheap_precheck_safe():
    # NEVER_ELIGIBLE_JUDGMENTSに該当する場合、secondary/local無しの
    # 事前チェックだけで安全に判定できる(コスト増を伴わない)。
    r = cs_equiv.classify_connected_speech_equivalence(
        "The report shows a clear increase in visits.",
        "The report shows a clear decrease in visits.")
    assert r["layer_judgment"] in cs_equiv.NEVER_ELIGIBLE_JUDGMENTS
    print("PASS: test_never_eligible_judgments_are_cheap_precheck_safe")


# ------------------------------------------------------------
# Part 2: Cascade層への配線(er006_secondary_asr_01.py)
# ------------------------------------------------------------
def test_disabled_by_default_no_new_asr_calls_and_no_classification_change():
    # enable_connected_speech_equivalence_layerを渡さない(既定False)
    # 既存の全呼び出し元は、TRUE_CONTENT_MISMATCHのままで、Secondary/local
    # ASRが一切呼ばれないこと(後方互換の直接確認)。
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_local_fn = disfluency_qa.transcribe_verbatim
    calls = {"secondary": 0, "local": 0}

    def fake_secondary(*a, **k):
        calls["secondary"] += 1
        return "SHOULD NOT BE CALLED", None

    def fake_local(*a, **k):
        calls["local"] += 1
        return [{"text": "SHOULD NOT BE CALLED"}]

    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    disfluency_qa.transcribe_verbatim = fake_local
    try:
        canonical = "Young travelers still showed strong interest in the results."
        primary = "Young travelers still show strong interest in the results."
        r = secondary.evaluate_attempt_with_cascade_detail(
            canonical, primary, [], "dummy.wav", cascade_enabled=True)
        assert r["classification"].classification == "TRUE_CONTENT_MISMATCH"
        assert r["connected_speech_equivalence_layer_invoked"] is False
        assert calls == {"secondary": 0, "local": 0}
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        disfluency_qa.transcribe_verbatim = orig_local_fn
    print("PASS: test_disabled_by_default_no_new_asr_calls_and_no_classification_change")


def test_enabled_but_no_category_match_skips_asr_calls():
    # enable_connected_speech_equivalence_layer=Trueでも、音韻環境
    # カテゴリに該当しない真の不一致(increase/decrease)では、追加の
    # Secondary/local ASR呼び出しを一切行わない(コストガード)。
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_local_fn = disfluency_qa.transcribe_verbatim
    calls = {"secondary": 0, "local": 0}

    def fake_secondary(*a, **k):
        calls["secondary"] += 1
        return "SHOULD NOT BE CALLED", None

    def fake_local(*a, **k):
        calls["local"] += 1
        return [{"text": "SHOULD NOT BE CALLED"}]

    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    disfluency_qa.transcribe_verbatim = fake_local
    try:
        r = secondary.evaluate_attempt_with_cascade_detail(
            "The report shows a clear increase in visits.",
            "The report shows a clear decrease in visits.",
            [], "dummy.wav", cascade_enabled=True, enable_connected_speech_equivalence_layer=True)
        assert r["classification"].classification == "TRUE_CONTENT_MISMATCH"
        assert r["connected_speech_equivalence_layer_invoked"] is False
        assert calls == {"secondary": 0, "local": 0}
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        disfluency_qa.transcribe_verbatim = orig_local_fn
    print("PASS: test_enabled_but_no_category_match_skips_asr_calls")


def test_enabled_accepts_with_secondary_and_local_corroboration():
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_local_fn = disfluency_qa.transcribe_verbatim
    canonical = "Young travelers still showed strong interest in the results."
    primary = "Young travelers still show strong interest in the results."

    secondary.get_full_text_via_azure_stt_with_phrase_list = lambda *a, **k: (canonical, None)
    disfluency_qa.transcribe_verbatim = lambda *a, **k: [{"text": w} for w in canonical.split()]
    try:
        r = secondary.evaluate_attempt_with_cascade_detail(
            canonical, primary, [], "dummy.wav", cascade_enabled=True,
            enable_connected_speech_equivalence_layer=True)
        assert r["verified"] is True
        assert r["classification"].classification == "CONNECTED_SPEECH_EQUIVALENCE_ACCEPT"
        assert r["classification"].should_pass is True
        assert r["connected_speech_equivalence_layer_invoked"] is True
        assert r["classification"].classification in val.VALID_CLASSIFICATIONS
        assert any(s["step"] == "connected_speech_equivalence_secondary" for s in r["steps"])
        assert any(s["step"] == "connected_speech_equivalence_local" for s in r["steps"])
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        disfluency_qa.transcribe_verbatim = orig_local_fn
    print("PASS: test_enabled_accepts_with_secondary_and_local_corroboration")


def test_enabled_mixed_evidence_does_not_accept_but_records_diagnostic():
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_local_fn = disfluency_qa.transcribe_verbatim
    canonical = "The cars turned back before reaching the bridge."
    primary = "The cars turn back before reaching the bridge."

    # Secondaryは誤ってcanonicalを支持、localは正しく実発話を支持(MIXED)。
    secondary.get_full_text_via_azure_stt_with_phrase_list = lambda *a, **k: (canonical, None)
    disfluency_qa.transcribe_verbatim = lambda *a, **k: [{"text": w} for w in primary.split()]
    try:
        r = secondary.evaluate_attempt_with_cascade_detail(
            canonical, primary, [], "dummy.wav", cascade_enabled=True,
            enable_connected_speech_equivalence_layer=True)
        assert r["verified"] is False
        assert r["classification"].classification == "TRUE_CONTENT_MISMATCH"
        assert r["classification"].should_pass is False
        assert r["connected_speech_equivalence_layer_invoked"] is True
        # false positive疑いの事後監査用に診断情報が付与されていること
        info = r["classification"].connected_speech_info
        assert info is not None
        assert info["layer_judgment"] == "EQUIVALENCE_LAYER_MIXED_EVIDENCE_INSUFFICIENT"
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        disfluency_qa.transcribe_verbatim = orig_local_fn
    print("PASS: test_enabled_mixed_evidence_does_not_accept_but_records_diagnostic")


def test_never_fires_on_number_mismatch_even_if_enabled():
    # protected_check不合格(数字の真の不一致)は、Equivalence Layer有効
    # でも絶対に発火しない(既存protected_check gateを迂回しない)。
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_local_fn = disfluency_qa.transcribe_verbatim
    calls = {"secondary": 0, "local": 0}

    def fake_secondary(*a, **k):
        calls["secondary"] += 1
        return "SHOULD NOT BE CALLED", None

    def fake_local(*a, **k):
        calls["local"] += 1
        return [{"text": "SHOULD NOT BE CALLED"}]

    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    disfluency_qa.transcribe_verbatim = fake_local
    try:
        r = secondary.evaluate_attempt_with_cascade_detail(
            "The study followed 2 groups of participants.",
            "The study followed 3 groups of participants.",
            [], "dummy.wav", cascade_enabled=True, enable_connected_speech_equivalence_layer=True)
        assert r["classification"].classification == "TRUE_CONTENT_MISMATCH"
        assert r["classification"].protected.passed is False
        assert r["connected_speech_equivalence_layer_invoked"] is False
        assert calls == {"secondary": 0, "local": 0}
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        disfluency_qa.transcribe_verbatim = orig_local_fn
    print("PASS: test_never_fires_on_number_mismatch_even_if_enabled")


def test_never_fires_on_negation_mismatch_even_if_enabled():
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_local_fn = disfluency_qa.transcribe_verbatim
    calls = {"secondary": 0, "local": 0}

    def fake_secondary(*a, **k):
        calls["secondary"] += 1
        return "SHOULD NOT BE CALLED", None

    def fake_local(*a, **k):
        calls["local"] += 1
        return [{"text": "SHOULD NOT BE CALLED"}]

    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    disfluency_qa.transcribe_verbatim = fake_local
    try:
        r = secondary.evaluate_attempt_with_cascade_detail(
            "The visitors did not report any problems.",
            "The visitors report any problems.",
            [], "dummy.wav", cascade_enabled=True, enable_connected_speech_equivalence_layer=True)
        assert r["connected_speech_equivalence_layer_invoked"] is False
        assert calls == {"secondary": 0, "local": 0}
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        disfluency_qa.transcribe_verbatim = orig_local_fn
    print("PASS: test_never_fires_on_negation_mismatch_even_if_enabled")


# ------------------------------------------------------------
# Part 3: Key Phrase / 日本語経路が範囲外であることの証拠
# ------------------------------------------------------------
def test_key_phrase_style_call_without_flag_stays_unaffected():
    # Key Phrase経路の実際の呼び出しパターン(enable_non_latin_cascade=True)
    # を模しつつ、enable_connected_speech_equivalence_layerを渡さない
    # (既定False)。Equivalence Layerは一切発火しないこと。
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_local_fn = disfluency_qa.transcribe_verbatim
    calls = {"local": 0}
    secondary.get_full_text_via_azure_stt_with_phrase_list = lambda *a, **k: (
        "Young travelers still show strong interest in the results.", None)

    def fake_local(*a, **k):
        calls["local"] += 1
        return [{"text": "SHOULD NOT BE CALLED"}]

    disfluency_qa.transcribe_verbatim = fake_local
    try:
        r = secondary.evaluate_attempt_with_cascade_detail(
            "Young travelers still showed strong interest in the results.",
            "Young travelers still show strong interest in the results.",
            [], "dummy.wav", cascade_enabled=True, enable_non_latin_cascade=True)
        assert r["connected_speech_equivalence_layer_invoked"] is False
        assert r["classification"].classification == "TRUE_CONTENT_MISMATCH"
        assert calls["local"] == 0
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        disfluency_qa.transcribe_verbatim = orig_local_fn
    print("PASS: test_key_phrase_style_call_without_flag_stays_unaffected")


def test_generate_key_phrase_component_verified_does_not_pass_flag():
    # ソースコード上でgenerate_key_phrase_component_verified(Key Phrase
    # Production経路)がenable_connected_speech_equivalence_layerを一切
    # 渡していないことを直接確認する(静的な配線範囲の証拠)。
    import inspect
    import er003_v1_repro01_main_generate as repro01
    src = inspect.getsource(repro01.generate_key_phrase_component_verified)
    assert "enable_connected_speech_equivalence_layer" not in src
    print("PASS: test_generate_key_phrase_component_verified_does_not_pass_flag")


def test_japanese_cascade_module_independent_of_equivalence_layer():
    # 日本語経路(er007_ja_secondary_asr_01.py)はConnected Speech
    # Equivalence Layer(英語専用)を一切importしていないこと。
    import inspect
    import er007_ja_secondary_asr_01 as ja_secondary
    src = inspect.getsource(ja_secondary)
    assert "cs_equivalence" not in src
    assert "connected_speech_equivalence_layer_production" not in src
    print("PASS: test_japanese_cascade_module_independent_of_equivalence_layer")


if __name__ == "__main__":
    test_existing_3_pattern_unchanged_pattern_a()
    test_existing_3_pattern_unchanged_pattern_c_resegmentation()
    test_unrelated_mismatch_not_a_phoneme_prefix_drop()
    test_flagship_showed_strong_accepts_with_real_evidence()
    test_no_corroboration_insufficient_evidence()
    test_mixed_evidence_not_accepted()
    test_never_eligible_judgments_are_cheap_precheck_safe()
    test_disabled_by_default_no_new_asr_calls_and_no_classification_change()
    test_enabled_but_no_category_match_skips_asr_calls()
    test_enabled_accepts_with_secondary_and_local_corroboration()
    test_enabled_mixed_evidence_does_not_accept_but_records_diagnostic()
    test_never_fires_on_number_mismatch_even_if_enabled()
    test_never_fires_on_negation_mismatch_even_if_enabled()
    test_key_phrase_style_call_without_flag_stays_unaffected()
    test_generate_key_phrase_component_verified_does_not_pass_flag()
    test_japanese_cascade_module_independent_of_equivalence_layer()
    print("\nALL PASS")
