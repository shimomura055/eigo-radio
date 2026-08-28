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


# ============================================================
# ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04
# Part C: force_secondary(fallback経由音声のSecondary ASR必須化)のtest。
# ============================================================
def test_force_secondary_false_never_calls_secondary_even_if_primary_passes():
    # standard path(force_secondary=既定False)は、Primary PASSならSecondary
    # を一切呼ばない(追加コストゼロであることの直接確認)。
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    calls = {"secondary": 0}

    def fake_secondary(*a, **k):
        calls["secondary"] += 1
        return "SHOULD NOT BE CALLED", None

    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        canon = "A desk can feel like a place."
        asr = "A desk can feel like a place."
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, [], "dummy.wav", cascade_enabled=True, force_secondary=False)
        assert r["verified"] is True
        assert calls["secondary"] == 0
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
    print("PASS: test_force_secondary_false_never_calls_secondary_even_if_primary_passes")


def test_force_secondary_true_primary_pass_secondary_pass_verified():
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list

    def fake_secondary(*a, **k):
        return "A desk can feel like a place.", None

    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        canon = "A desk can feel like a place."
        asr = "A desk can feel like a place."
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, [], "dummy.wav", cascade_enabled=True, force_secondary=True)
        assert r["verified"] is True
        assert any(s["step"] == "secondary_forced" for s in r["steps"])
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
    print("PASS: test_force_secondary_true_primary_pass_secondary_pass_verified")


def test_force_secondary_true_primary_pass_secondary_mismatch_not_auto_passed():
    # fallback + Primary PASS + Secondary mismatch -> 自動PASSしない(C-3 #3)。
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list

    def fake_secondary(*a, **k):
        return "A desk can feel LITHA.", None  # Secondaryは全く違う内容

    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        canon = "A desk can feel like a place."
        asr = "A desk can feel like a place."  # Primaryは正常認識(誤PASSの実例を再現)
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, [], "dummy.wav", cascade_enabled=True, force_secondary=True)
        assert r["verified"] is False, "SecondaryがPrimaryのPASSに同意しない場合、自動PASSしてはならない"
        assert r["human_review_required"] is True
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
    print("PASS: test_force_secondary_true_primary_pass_secondary_mismatch_not_auto_passed")


def test_force_secondary_true_primary_mismatch_preserves_existing_cascade():
    # fallback + Primary mismatch(entity-like)-> 既存のCascade安全性を維持
    # (force_secondary=Trueであっても、Primary不一致時の分岐は変更しない、C-3 #4)。
    orig_transcribe = routing.transcribe

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "A Tony and colleagues published a study.", None  # Primary#2でも不一致のまま

    routing.transcribe = fake_transcribe
    try:
        canon = "Ottoni and colleagues published a study."
        asr = "A Tony and colleagues published a study."  # 固有名詞のみの差、Primaryはmismatch
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, [], "dummy.wav", cascade_enabled=True, force_secondary=True)
        assert r["cascade_invoked"] is True
        assert any(s["step"] == "primary_2" for s in r["steps"]), \
            "force_secondary=TrueでもPrimary不一致時は既存のPrimary#2経路を通るはず"
        assert not any(s["step"] == "secondary_forced" for s in r["steps"])
    finally:
        routing.transcribe = orig_transcribe
    print("PASS: test_force_secondary_true_primary_mismatch_preserves_existing_cascade")


def test_no7_point_one_heading_fixture_caught_by_forced_secondary():
    # No.7 A2 point_one_headingで実際に起きた事故の再現fixture: Primary(OpenAI)
    # は正しく書き起こしたが、実音声はSecondary(Azure)だと全く別物に聞こえた
    # (ER-008-N7-CONTENT-AUDIO-QA-02で実際に確認した実測値そのもの)。
    # force_secondary=Trueなら、この誤PASSを素通りさせないことを確認する。
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list

    def fake_secondary(*a, **k):
        return "A desk can feel LITHA.", None  # 実際にAzureが返した書き起こし

    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        canon = "A desk can feel like a place"
        asr = "A desk can feel like a place..."  # 実際にOpenAI Primaryが返した書き起こし
        r = secondary.evaluate_attempt_with_cascade_detail(
            canon, asr, [], "dummy.wav", cascade_enabled=True, force_secondary=True)
        assert r["verified"] is False, "Primaryだけで素通りしてはならない(実際の事故の再発防止)"
        assert any(s["step"] == "secondary_forced" for s in r["steps"]), "Secondaryまで到達しなければならない"
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
    print("PASS: test_no7_point_one_heading_fixture_caught_by_forced_secondary")


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


# ============================================================
# ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15: homophone + 固有名詞
# Case A/B の regression fixture
# ============================================================
def test_homophone_wait_weight_passes_without_human_review():
    # Primary/Primary#2ともに"weight"(canonicalは"wait")でも、ARPAbet
    # 完全一致のため、Secondary Azureを呼ばずHOMOPHONE_EQUIVALENTでPASS
    # する(No.8 wait/weightで実際に無駄なTTS retryが起きていた実例への対応)。
    orig_transcribe = routing.transcribe
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    calls = {"secondary": 0}

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "A small weight can protect against a big fear.", None

    def fake_secondary(*a, **k):
        calls["secondary"] += 1
        return "SHOULD NOT BE CALLED", None

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    try:
        canon = "A small wait can protect against a big fear."
        asr = "A small weight can protect against a big fear."
        r = secondary.evaluate_attempt_with_cascade_detail(canon, asr, [], "dummy.wav", cascade_enabled=True)
        assert r["verified"] is True
        assert r["final_status"] == secondary.HOMOPHONE_EQUIVALENT
        assert r["human_review_required"] is False
        assert calls["secondary"] == 0, "Primary#2の時点でARPAbet完全一致が確認できるためSecondaryは不要"
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
    print("PASS: test_homophone_wait_weight_passes_without_human_review")


def test_homophone_requires_arpabet_match_not_string_similarity():
    # "wet"は"wait"と綴りは近いが発音が異なる(EY/EH)ため、homophone_
    # candidateにならず、固有名詞由来でもないので即TRUE_CONTENT_MISMATCH
    # (blind TTS retry対象)のまま、Cascade自体が起動しないこと。
    canon = "A small wait can protect against a big fear."
    asr = "A small wet can protect against a big fear."
    cls = val.classify_asr_match(canon, asr)
    assert cls.classification == "TRUE_CONTENT_MISMATCH"
    r = secondary.evaluate_attempt_with_cascade_detail(canon, asr, [], "dummy.wav", cascade_enabled=True)
    assert r["cascade_invoked"] is False
    print("PASS: test_homophone_requires_arpabet_match_not_string_similarity")


def test_case_a_entity_arpabet_match_passes_without_ledger_call():
    # Kristie(canonical)/Christie(ASR)はCMU辞書上代表発音が完全一致する
    # ため、Ledger/Perplexityを一切呼ばずPROPER_NOUN_ENTITY_ARPABET_
    # CONFIRMEDでPASSする(D-2'(A)、コストゼロ)。
    orig_transcribe = routing.transcribe
    orig_lookup = secondary.pronun_ledger.lookup
    orig_research = secondary.pronun_research.research_pronunciations
    calls = {"ledger": 0, "research": 0}

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "Christie is a psychologist in New York.", None

    def fake_lookup(*a, **k):
        calls["ledger"] += 1
        raise AssertionError("Case Aで解決できる場合、Ledgerを呼んではならない")

    def fake_research(*a, **k):
        calls["research"] += 1
        raise AssertionError("Case Aで解決できる場合、Perplexity researchを呼んではならない")

    routing.transcribe = fake_transcribe
    secondary.pronun_ledger.lookup = fake_lookup
    secondary.pronun_research.research_pronunciations = fake_research
    try:
        canon = "Kristie is a psychologist in New York."
        asr = "Christie is a psychologist in New York."
        r = secondary.evaluate_attempt_with_cascade_detail(canon, asr, [], "dummy.wav", cascade_enabled=True)
        assert r["verified"] is True
        assert r["final_status"] == secondary.PROPER_NOUN_ENTITY_ARPABET_CONFIRMED
        assert calls["ledger"] == 0 and calls["research"] == 0
    finally:
        routing.transcribe = orig_transcribe
        secondary.pronun_ledger.lookup = orig_lookup
        secondary.pronun_research.research_pronunciations = orig_research
    print("PASS: test_case_a_entity_arpabet_match_passes_without_ledger_call")


def test_case_b_unresolved_entity_does_not_auto_pass_and_enriches_review():
    # "Tse"のようにCMU辞書だけでは安全に比較できない固有名詞は、Ledgerの
    # 情報を蓄積してもPASSさせない(D-2'(B))。ASR結果同士がどれだけ収束
    # していても(4ステップとも同じ誤認識)、Human Reviewへ進む。
    orig_transcribe = routing.transcribe
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_resolve = secondary._resolve_unresolved_entity_for_review

    def fake_transcribe(wav_path, language="en-US", timeout_seconds=90.0):
        return "Christy Tay links the behavior to anxiety.", None

    def fake_secondary(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
        return "Christy Tay links the behavior to anxiety.", None

    def fake_resolve(canonical_span):
        # 実際のLedger/Perplexity呼び出しをせず、既知の発音情報を返した
        # 体で、Human Reviewパッケージへの添付だけを検証する。
        return {"canonical_spelling": "Kristie Tse", "expected_pronunciation_ipa": "ˈkrɪsti tseɪ",
                "pronunciation_hint": "KRIS-tee tsay", "confidence": "medium", "sources": ["https://example.com"]}

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_secondary
    secondary._resolve_unresolved_entity_for_review = fake_resolve
    try:
        canon = "Kristie Tse links the behavior to anxiety."
        asr = "Christy Tay links the behavior to anxiety."
        r = secondary.evaluate_attempt_with_cascade_detail(canon, asr, [], "dummy.wav", cascade_enabled=True)
        assert r["verified"] is False, "ASR結果同士の収束だけでは絶対にPASSしない"
        assert r["human_review_required"] is True
        assert "kristie tse" in r.get("pronunciation_lookups", {})
        assert r["pronunciation_lookups"]["kristie tse"]["canonical_spelling"] == "Kristie Tse"
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        secondary._resolve_unresolved_entity_for_review = orig_resolve
    print("PASS: test_case_b_unresolved_entity_does_not_auto_pass_and_enriches_review")


def test_ledger_cache_key_uses_empty_source_context_for_cross_article_reuse():
    # D-2': cache keyは記事をまたいで再利用できるよう、常にsource_
    # context=""(既定)を使うこと(記事固有の値を混ぜてcache keyを割らない)。
    key = secondary.pronun_ledger.LedgerKey(
        surface="Kristie Tse", entity_type=secondary._UNRESOLVED_ENTITY_TYPE, source_context="")
    key_same_surface_different_article = secondary.pronun_ledger.LedgerKey(
        surface="Kristie Tse", entity_type=secondary._UNRESOLVED_ENTITY_TYPE, source_context="")
    assert key.ledger_id() == key_same_surface_different_article.ledger_id()
    print("PASS: test_ledger_cache_key_uses_empty_source_context_for_cross_article_reuse")


if __name__ == "__main__":
    test_cascade_disabled_matches_plain_evaluate_attempt()
    test_non_entity_mismatch_does_not_trigger_cascade()
    test_entity_like_mismatch_triggers_primary_2()
    test_primary_2_pass_stops_cascade_before_secondary()
    test_full_cascade_all_fail_routes_to_human_review()
    test_secondary_1_pass_stops_before_secondary_2()
    test_is_entity_like_mismatch_excludes_number_diffs()
    test_is_entity_like_mismatch_true_for_proper_noun_only()
    test_force_secondary_false_never_calls_secondary_even_if_primary_passes()
    test_force_secondary_true_primary_pass_secondary_pass_verified()
    test_force_secondary_true_primary_pass_secondary_mismatch_not_auto_passed()
    test_force_secondary_true_primary_mismatch_preserves_existing_cascade()
    test_no7_point_one_heading_fixture_caught_by_forced_secondary()
    test_tuple_wrapper_matches_val_evaluate_attempt_shape_and_logs_human_review()
    test_homophone_wait_weight_passes_without_human_review()
    test_homophone_requires_arpabet_match_not_string_similarity()
    test_case_a_entity_arpabet_match_passes_without_ledger_call()
    test_case_b_unresolved_entity_does_not_auto_pass_and_enriches_review()
    test_ledger_cache_key_uses_empty_source_context_for_cross_article_reuse()
    print("ALL TESTS PASSED")
