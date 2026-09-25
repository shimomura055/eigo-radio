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


def test_entity_like_mismatch_triggers_primary_2():
    import er006_asr_provider_routing_01 as routing
    orig = routing._transcribe_openai_mini
    calls = {"n": 0}

    def fake(*a, **k):
        calls["n"] += 1
        return "解約を難しくする壁は、「スラッシ」と考えられます。", None  # 依然不一致

    routing._transcribe_openai_mini = fake
    try:
        canon = "解約を難しくする壁は、「スラッジ」と考えられます。"
        asr = "解約を難しくする壁は、「スラッシ」と考えられます。"
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=True)
        assert r["cascade_invoked"] is True
        assert calls["n"] == 1, "Primary#2が1回呼ばれるはず"
        assert any(s["step"] == "primary_2" for s in r["steps"])
    finally:
        routing._transcribe_openai_mini = orig
    print("PASS: test_entity_like_mismatch_triggers_primary_2")


def test_primary_2_pass_stops_cascade_before_secondary():
    import er006_asr_provider_routing_01 as routing
    import er003_b1_p4_audio as p4
    orig_openai = routing._transcribe_openai_mini
    orig_azure = p4.get_full_text_via_azure_stt_continuous
    calls = {"azure": 0}

    def fake_openai(*a, **k):
        return "解約を難しくする壁は、「スラッジ」と考えられます。", None  # Primary#2で正しく認識

    def fake_azure(*a, **k):
        calls["azure"] += 1
        return "SHOULD NOT BE CALLED", None

    routing._transcribe_openai_mini = fake_openai
    p4.get_full_text_via_azure_stt_continuous = fake_azure
    try:
        canon = "解約を難しくする壁は、「スラッジ」と考えられます。"
        asr = "解約を難しくする壁は、「スラッシ」と考えられます。"
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=True)
        assert r["verified"] is True
        assert calls["azure"] == 0, "Primary#2でPASSしたらAzureは呼ばれないはず"
    finally:
        routing._transcribe_openai_mini = orig_openai
        p4.get_full_text_via_azure_stt_continuous = orig_azure
    print("PASS: test_primary_2_pass_stops_cascade_before_secondary")


def test_full_cascade_all_fail_routes_to_human_review():
    import er006_asr_provider_routing_01 as routing
    import er003_b1_p4_audio as p4
    orig_openai = routing._transcribe_openai_mini
    orig_azure = p4.get_full_text_via_azure_stt_continuous
    calls = {"openai": 0, "azure": 0}

    def fake_openai(*a, **k):
        calls["openai"] += 1
        return "解約を難しくする壁は、「スラッシ」と考えられます。", None

    def fake_azure(*a, **k):
        calls["azure"] += 1
        return "解約を難しくする壁は、「スラツジ」と考えられます。", None  # 依然不一致(固有名詞のみ)

    routing._transcribe_openai_mini = fake_openai
    p4.get_full_text_via_azure_stt_continuous = fake_azure
    try:
        canon = "解約を難しくする壁は、「スラッジ」と考えられます。"
        asr = "解約を難しくする壁は、「スラッシ」と考えられます。"
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, asr, "dummy.wav", cascade_enabled=True)
        assert calls["openai"] == 1, "Primary#2は1回のみ"
        assert calls["azure"] == 2, "Secondary#1・#2の2回呼ばれるはず"
        assert r["human_review_required"] is True
        assert r["verified"] is False
        assert r["final_status"] == "ASR_VALIDATION_UNCERTAIN"
        step_names = [s["step"] for s in r["steps"]]
        assert step_names == ["primary_1", "primary_2", "secondary_1", "secondary_2"]
    finally:
        routing._transcribe_openai_mini = orig_openai
        p4.get_full_text_via_azure_stt_continuous = orig_azure
    print("PASS: test_full_cascade_all_fail_routes_to_human_review")


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
        assert r["final_status"] == ja_secondary.ORTHOGRAPHIC_VARIANT_CONFIRMED
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
def test_expected_readings_forwarded_to_primary_2_step():
    """Primary#1は辞書登録トークン(Meta->メタ)が正しく、無関係な
    entity_like差(スラッジ->スラッシ)だけでCascadeが起動する。Primary#2で
    辞書トークンが「メタン」に化けた場合、expected_readingsが転送されて
    いれば直ちにTRUE_CONTENT_MISMATCHと判定されるはず(転送されていなければ
    従来通りentity_like扱いのままになる)。"""
    import er006_asr_provider_routing_01 as routing
    orig = routing._transcribe_openai_mini
    p2_text = "スラッシについて、メタンが説明しました。"
    routing._transcribe_openai_mini = lambda *a, **k: (p2_text, None)
    try:
        canon = "スラッジについて、Metaが説明しました。"
        asr1 = "スラッシについて、メタが説明しました。"
        r_with = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            canon, asr1, "dummy.wav", cascade_enabled=True, expected_readings={"meta": "メタ"})
        r_without = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            canon, asr1, "dummy.wav", cascade_enabled=True)
        p2_step_with = next(s for s in r_with["steps"] if s["step"] == "primary_2")
        p2_step_without = next(s for s in r_without["steps"] if s["step"] == "primary_2")
        assert p2_step_with["classification"] == "TRUE_CONTENT_MISMATCH", p2_step_with
        assert p2_step_without["classification"] != "TRUE_CONTENT_MISMATCH", p2_step_without
    finally:
        routing._transcribe_openai_mini = orig
    print("PASS: test_expected_readings_forwarded_to_primary_2_step")


def test_expected_readings_none_is_fully_backward_compatible():
    """expected_readings未指定(既定None)時、Meta->メタンのentity_like
    Cascade偶然一致挙動が変わらないこと(recon_reading_validation_
    wiring_01.md 1.2節の再現、既存artifactの挙動を壊さないことの確認)。"""
    import er006_asr_provider_routing_01 as routing
    orig = routing._transcribe_openai_mini
    # Primary#2が読みの完全一致する表記を返せば、従来どおり無条件PASS
    # (TTSの内容自体は変わらないため辞書チェック抜きでは救済されてしまう、
    # という既存の欠落挙動そのものを回帰確認する)。
    routing._transcribe_openai_mini = lambda *a, **k: ("メタが説明しました。", None)
    try:
        canon = "Metaが説明しました。"
        asr1 = "メタンが説明しました。"
        r = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            canon, asr1, "dummy.wav", cascade_enabled=True)  # expected_readings渡さない
        assert r["verified"] is True, "expected_readings未指定時は既存の挙動(偶然一致PASS)を変えない"
    finally:
        routing._transcribe_openai_mini = orig
    print("PASS: test_expected_readings_none_is_fully_backward_compatible")


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
        assert r["verified"] is False
        assert r["final_status"] != ja_secondary.ORTHOGRAPHIC_VARIANT_CONFIRMED
        assert r["human_review_required"] is True
    finally:
        routing._transcribe_openai_mini = orig_openai
        p4.get_full_text_via_azure_stt_continuous = orig_azure
    print("PASS: test_single_engine_repetition_does_not_confirm_orthographic_variant")


if __name__ == "__main__":
    test_cascade_disabled_matches_plain_classify()
    test_non_entity_mismatch_does_not_trigger_cascade()
    test_entity_like_mismatch_triggers_primary_2()
    test_primary_2_pass_stops_cascade_before_secondary()
    test_full_cascade_all_fail_routes_to_human_review()
    test_true_content_mismatch_never_rescued_by_cascade()
    test_koro_kanji_variant_confirmed_by_reading_candidates()
    test_unrelated_kanji_reading_not_confirmed()
    test_single_engine_repetition_does_not_confirm_orthographic_variant()
    test_expected_readings_forwarded_to_primary_2_step()
    test_expected_readings_none_is_fully_backward_compatible()
    print("ALL TESTS PASSED")
