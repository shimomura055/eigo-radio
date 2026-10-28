# ============================================================
# er007_ja_secondary_asr_01_test.py
# Cascade構造の単体テスト(モックのみ、新規API呼び出しなし)。
# er006_secondary_asr_01_test.pyと同じ検証パターンを日本語版へ適用する。
# ============================================================
from __future__ import annotations

import er007_ja_secondary_asr_01 as ja_secondary


def test_cascade_disabled_matches_plain_classify():
    canon = "定期サービスをやめにくくする仕組み"
    asr = "定期サービスをやめにくくする仕組み"
    r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=False)
    assert r["verified"] is True
    assert r["cascade_invoked"] is False
    print("PASS: test_cascade_disabled_matches_plain_classify")


def test_non_entity_mismatch_does_not_trigger_cascade():
    canon = "150人の女性を対象とした調査"
    asr = "140人の女性を対象とした調査"
    r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=True)
    assert r["cascade_invoked"] is False, "数字違いのmismatchでCascadeを起動してはならない"
    assert r["classification"].classification == "TRUE_CONTENT_MISMATCH"
    print("PASS: test_non_entity_mismatch_does_not_trigger_cascade")


# AUW 委任_04(α更新): Primary#2(同一音声のOpenAI再転写)/Secondary#2/4段尽きHR直行は統一判定で廃止(DESIGN_01 §4-9)。
# 旧3件(Primary#2起動・Primary#2救済・4段尽きHR)は、「Primary NG -> Secondary 1回 -> 両NGなら次の再生成(HRは最終slotのみ)」
# の新フローを固定する形に置換した。誤PASS防止(Secondaryが依然不一致ならNG、障害ならPASS不可)の安全側assertは維持。
def _mock_secondary(text, calls):
    def fake(wav_path, language="ja-JP", timeout_seconds=90.0):
        calls["azure"] = calls.get("azure", 0) + 1
        return text, None
    return fake


def _forbid_primary_2():
    import er006_asr_provider_routing_01 as routing
    calls = {"p2": 0}
    orig = routing._transcribe_openai_mini

    def fake(*a, **k):
        calls["p2"] += 1
        return "SHOULD NOT BE CALLED", None
    routing._transcribe_openai_mini = fake
    return calls, lambda: setattr(routing, "_transcribe_openai_mini", orig)


def test_entity_like_mismatch_triggers_secondary_once_without_primary_2():
    calls, restore = _forbid_primary_2()
    orig_az = ja_secondary._azure_stt_strict
    ja_secondary._azure_stt_strict = _mock_secondary("解約を難しくする壁は、「スラッシ」と考えられます。", calls)  # 依然不一致
    try:
        canon = "解約を難しくする壁は、「スラッジ」と考えられます。"
        asr = "解約を難しくする壁は、「スラッシ」と考えられます。"
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=True)
        assert r["cascade_invoked"] is True
        assert calls["p2"] == 0, "Primary#2(同一音声のOpenAI再転写)は廃止"
        assert calls["azure"] == 1, "Secondaryは1回のみ"
        assert [s["step"] for s in r["steps"]] == ["primary_1", "secondary_1"]
        assert r["verified"] is False and r["stop_retrying"] is False
    finally:
        restore()
        ja_secondary._azure_stt_strict = orig_az
    print("PASS: test_entity_like_mismatch_triggers_secondary_once_without_primary_2")


def test_secondary_exact_confirms_uncertain_entity_as_pass_with_warning():
    calls, restore = _forbid_primary_2()
    orig_az = ja_secondary._azure_stt_strict
    canon = "解約を難しくする壁は、「スラッジ」と考えられます。"
    ja_secondary._azure_stt_strict = _mock_secondary(canon, calls)  # Secondaryは原稿と一致
    try:
        asr = "解約を難しくする壁は、「スラッシ」と考えられます。"
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=True)
        assert r["verified"] is True
        assert calls["azure"] == 1 and calls["p2"] == 0
        assert r["asr_judgement"]["state"] == "PASS_WITH_WARNING"
        assert "SECONDARY_CONFIRMED" in r["asr_judgement"]["warnings"]
    finally:
        restore()
        ja_secondary._azure_stt_strict = orig_az
    print("PASS: test_secondary_exact_confirms_uncertain_entity_as_pass_with_warning")


def test_both_ng_goes_to_next_regeneration_and_hr_only_at_last_slot():
    calls, restore = _forbid_primary_2()
    orig_az = ja_secondary._azure_stt_strict
    ja_secondary._azure_stt_strict = _mock_secondary("解約を難しくする壁は、「スラツジ」と考えられます。", calls)  # 依然不一致
    try:
        canon = "解約を難しくする壁は、「スラッジ」と考えられます。"
        asr = "解約を難しくする壁は、「スラッシ」と考えられます。"
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=True)
        assert calls["p2"] == 0 and calls["azure"] == 1
        assert r["verified"] is False and r["stop_retrying"] is False, "両NG -> 次のTTS再生成(同一音声のASR再試行/尽きでの打切りは廃止)"
        assert r["human_review_required"] is False, "HR queueは最終slot NGのみ"
        assert r["final_status"] == "ASR_VALIDATION_UNCERTAIN"
        assert [s["step"] for s in r["steps"]] == ["primary_1", "secondary_1"]
        last = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            canon, asr, "dummy.wav", cascade_enabled=True, attempt_ctx={"is_last_slot": True})
        assert last["human_review_required"] is True and last["verified"] is False
    finally:
        restore()
        ja_secondary._azure_stt_strict = orig_az
    print("PASS: test_both_ng_goes_to_next_regeneration_and_hr_only_at_last_slot")


def test_true_content_mismatch_never_rescued_by_cascade():
    """重要: 数字/否定/内容語の真の誤りは、Cascadeが起動する前に
    TRUE_CONTENT_MISMATCHとして弾かれ、誤PASSの経路自体が存在しないことを
    確認する(英語Cascadeと同じ安全性設計)。"""
    import er006_asr_provider_routing_01 as routing
    orig = routing._transcribe_openai_mini
    calls = {"n": 0}
    routing._transcribe_openai_mini = lambda *a, **k: (calls.__setitem__("n", calls["n"] + 1), ("SHOULD NOT BE CALLED", None))[1]
    try:
        canon = "解約を難しくする壁を変えるために作ったルール"
        asr = "解約を難しくする壁を変えないために作ったルール"  # 否定反転
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=True)
        assert r["cascade_invoked"] is False
        assert calls["n"] == 0, "否定反転でCascadeのPrimary#2を呼んではならない"
        assert r["classification"].classification == "TRUE_CONTENT_MISMATCH"
    finally:
        routing._transcribe_openai_mini = orig
    print("PASS: test_true_content_mismatch_never_rescued_by_cascade")


# ============================================================
# ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part G/H:
# ORTHOGRAPHIC_VARIANT_CONFIRMEDのregression fixture
# ============================================================
def test_koro_kanji_variant_confirmed_by_reading_candidates():
    # No.8実例: canonical「ころ」/ASR「頃」。「頃」の辞書上の正当な読み
    # 候補に「ころ」が含まれ、かつOpenAI(Primary)・Azure(Secondary)の
    # 異なる2エンジンがこの状態に到達するため、ORTHOGRAPHIC_VARIANT_
    # CONFIRMEDとしてPASSする(単なる「4回とも同じ表記だった」という
    # 文字列収束ではなく、読み候補の照合が根拠であることが核心)。
    import er006_asr_provider_routing_01 as routing
    import er003_b1_p4_audio as p4
    orig_openai = routing._transcribe_openai_mini
    orig_azure = p4.get_full_text_via_azure_stt_continuous

    canon = "聞き終えるころには、変化が始まっているのかが分かります。"
    asr_text = "聞き終える頃には、変化が始まっているのかがわかります。"

    routing._transcribe_openai_mini = lambda *a, **k: (asr_text, None)
    p4.get_full_text_via_azure_stt_continuous = lambda *a, **k: (asr_text, None)
    try:
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr_text, "dummy.wav", cascade_enabled=True)
        assert r["verified"] is True
        # 不変条件(委任_02A-0、R-10): 「頃↔ころ」はPASSであり、根拠は読み(形態素解析の読み候補照合)に限る。
        # 後続のVariant Layer(Candidate D-2、`CURRENT_SPEC.md:2259` APPROVED_FOR_PRODUCTION)がPrimary単独で
        # PHONETIC_MATCHへ引き上げるため、確定ラベルは2系統のどちらでも正当(いずれも読み根拠・Human Review不要)。
        assert r["final_status"] in (ja_secondary.ORTHOGRAPHIC_VARIANT_CONFIRMED, "PHONETIC_MATCH")
        assert r["classification"].should_pass is True
        assert r["human_review_required"] is False
    finally:
        routing._transcribe_openai_mini = orig_openai
        p4.get_full_text_via_azure_stt_continuous = orig_azure
    print("PASS: test_koro_kanji_variant_confirmed_by_reading_candidates")


def test_unrelated_kanji_reading_not_confirmed():
    # 「市役所」/「死因」のように、読みの候補一覧が根本的に無関係な場合は
    # 誤PASSしない(そもそもprotected_check_jaの時点でTRUE_CONTENT_
    # MISMATCHとなりCascade自体が起動しない)。
    canon = "市役所に行きます。"
    asr = "死因を調べます。"
    r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=True)
    assert r["verified"] is False
    assert r["classification"].classification == "TRUE_CONTENT_MISMATCH"
    print("PASS: test_unrelated_kanji_reading_not_confirmed")


# ============================================================
# NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b:
# expected_readingsがCascadeの全ステップ(Primary#1〜Secondary#2)へ
# 正しく転送されることの確認(単なる転送だが、Primary#1以外のステップで
# 抜け落ちていないかを直接検証する)。
# ============================================================
def test_expected_readings_forwarded_to_secondary_step():
    """AUW 委任_04(α更新): Primary#2廃止に伴い、expected_readingsの転送先をSecondary判定(secondary_1)で固定する。
    Primary#1は辞書登録トークン(Meta->メタ)が正しく、無関係なentity_like差(スラッジ->スラッシ)だけでUNCERTAIN。
    Secondaryで辞書トークンが「メタン」に化けた場合、expected_readingsが転送されていれば当該stepはTRUE_CONTENT_MISMATCH
    (転送されていなければ従来どおりentity_like扱い)。"""
    calls = {}
    orig_az = ja_secondary._azure_stt_strict
    ja_secondary._azure_stt_strict = _mock_secondary("スラッシについて、メタンが説明しました。", calls)
    try:
        canon = "スラッジについて、Metaが説明しました。"
        asr1 = "スラッシについて、メタが説明しました。"
        r_with = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            canon, asr1, "dummy.wav", cascade_enabled=True, expected_readings={"meta": "メタ"})
        r_without = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            canon, asr1, "dummy.wav", cascade_enabled=True)
        s_with = next(s for s in r_with["steps"] if s["step"] == "secondary_1")
        s_without = next(s for s in r_without["steps"] if s["step"] == "secondary_1")
        assert s_with["classification"] == "TRUE_CONTENT_MISMATCH", s_with
        assert s_without["classification"] != "TRUE_CONTENT_MISMATCH", s_without
        assert r_with["verified"] is False and r_without["verified"] is False
    finally:
        ja_secondary._azure_stt_strict = orig_az
    print("PASS: test_expected_readings_forwarded_to_secondary_step")


def test_expected_readings_none_secondary_not_exact_is_not_auto_pass():
    """AUW 委任_04(α更新): 旧test(Primary#2が読み一致を返せば無条件PASS=偶然一致PASSの欠落挙動)は、Primary#2廃止で前提が消えた。
    新フローでは expected_readings 未指定でも、Secondary(独立エンジン)が原稿とEXACT/NORMALIZEDで一致しなければPASSしない
    (Meta->メタン のentity_like差は、Secondaryも『メタン』なら誤PASSしない=偶然一致PASSの穴が塞がる)。"""
    calls = {}
    orig_az = ja_secondary._azure_stt_strict
    ja_secondary._azure_stt_strict = _mock_secondary("メタンが説明しました。", calls)
    try:
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            "Metaが説明しました。", "メタンが説明しました。", "dummy.wav", cascade_enabled=True)
        assert r["verified"] is False, "Secondaryも原稿と不一致ならPASSしない"
        assert calls.get("azure", 0) <= 1
    finally:
        ja_secondary._azure_stt_strict = orig_az
    print("PASS: test_expected_readings_none_secondary_not_exact_is_not_auto_pass")


def test_single_engine_repetition_does_not_confirm_orthographic_variant():
    # 「同一エンジンが同じ表記を繰り返しただけ」では確定させない
    # (少なくとも2つの異なるエンジンでの裏付けを要求する)。OpenAI
    # (Primary#1・#2)だけが読み候補を満たし、Azure(Secondary)が
    # 無関係な内容誤り(TRUE_CONTENT_MISMATCH相当の差)を返す場合は
    # Human Reviewのままになることを確認する。
    import er006_asr_provider_routing_01 as routing
    import er003_b1_p4_audio as p4
    orig_openai = routing._transcribe_openai_mini
    orig_azure = p4.get_full_text_via_azure_stt_continuous

    canon = "聞き終えるころには、変化が始まっているのかが分かります。"
    openai_text = "聞き終える頃には、変化が始まっているのかがわかります。"
    azure_text = "聞き終える頃には、別の内容が始まっているのかがわかります。"  # 無関係な内容差

    routing._transcribe_openai_mini = lambda *a, **k: (openai_text, None)
    p4.get_full_text_via_azure_stt_continuous = lambda *a, **k: (azure_text, None)
    try:
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, openai_text, "dummy.wav", cascade_enabled=True)
        # 不変条件(委任_02A-0、R-10): 単一エンジン(OpenAI)の繰り返しでORTHOGRAPHIC_VARIANT_CONFIRMED(2エンジン確認ラベル)を
        # 出さない。かつ無関係な内容を返すAzure転写は、PASS根拠として採用されない。
        # 現行Productionでは、Primary転写が辞書読み一致のみの差(頃↔ころ)ならVariant Layer(Candidate D-2、
        # `CURRENT_SPEC.md:2259`)がPrimary単独でPHONETIC_MATCH PASSにするため verified=True になり得る(読み根拠であり
        # 繰り返しではない)。その場合もSecondary(Azure)の無関係転写は一切の合否根拠にならない(cascade_invoked=False)。
        assert r["final_status"] != ja_secondary.ORTHOGRAPHIC_VARIANT_CONFIRMED
        if r["verified"]:
            assert r["final_status"] == "PHONETIC_MATCH"
            assert r["cascade_invoked"] is False
            assert r["human_review_required"] is False
        else:
            assert r["human_review_required"] is True
    finally:
        routing._transcribe_openai_mini = orig_openai
        p4.get_full_text_via_azure_stt_continuous = orig_azure
    print("PASS: test_single_engine_repetition_does_not_confirm_orthographic_variant")


if __name__ == "__main__":
    test_cascade_disabled_matches_plain_classify()
    test_non_entity_mismatch_does_not_trigger_cascade()
    test_entity_like_mismatch_triggers_secondary_once_without_primary_2()
    test_secondary_exact_confirms_uncertain_entity_as_pass_with_warning()
    test_both_ng_goes_to_next_regeneration_and_hr_only_at_last_slot()
    test_true_content_mismatch_never_rescued_by_cascade()
    test_koro_kanji_variant_confirmed_by_reading_candidates()
    test_unrelated_kanji_reading_not_confirmed()
    test_single_engine_repetition_does_not_confirm_orthographic_variant()
    test_expected_readings_forwarded_to_secondary_step()
    test_expected_readings_none_secondary_not_exact_is_not_auto_pass()
    print("ALL TESTS PASSED")
