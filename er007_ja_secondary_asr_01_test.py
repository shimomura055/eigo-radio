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


if __name__ == "__main__":
    test_cascade_disabled_matches_plain_classify()
    test_non_entity_mismatch_does_not_trigger_cascade()
    test_entity_like_mismatch_triggers_primary_2()
    test_primary_2_pass_stops_cascade_before_secondary()
    test_full_cascade_all_fail_routes_to_human_review()
    test_true_content_mismatch_never_rescued_by_cascade()
    print("ALL TESTS PASSED")
