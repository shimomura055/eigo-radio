# ============================================================
# er025_entity_pronunciation_resolver_core_01_test.py
# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 (Phase 2)
# ============================================================
# 実行方法: .venv/Scripts/python.exe er025_entity_pronunciation_resolver_core_01_test.py
# API呼び出し: 0(全てmock、fail-safeパス確認含む)。
from __future__ import annotations

import os
import shutil

import er006_pronunciation_ledger_01 as ledger
import er025_entity_pronunciation_resolver_core_01 as core


def _use_temp_ledger(test_fn):
    orig_path = ledger.LEDGER_PATH
    tmp_path = "er006_output/_test_pronunciation_resolver_core_tmp/ledger.json"
    if os.path.exists(os.path.dirname(tmp_path)):
        shutil.rmtree(os.path.dirname(tmp_path))
    ledger.LEDGER_PATH = tmp_path
    core.reset_run_caches()
    try:
        test_fn()
    finally:
        ledger.LEDGER_PATH = orig_path
        core.reset_run_caches()
        if os.path.exists(os.path.dirname(tmp_path)):
            shutil.rmtree(os.path.dirname(tmp_path))


def test_confidence_gate_mapping():
    assert core.confidence_gate("high") == "AUTO_USE"
    assert core.confidence_gate("medium") == "ASR_BACKED"
    assert core.confidence_gate("low") == "HUMAN_REVIEW"
    assert core.confidence_gate(None) == "HUMAN_REVIEW"
    assert core.confidence_gate("garbage") == "HUMAN_REVIEW"
    print("PASS: test_confidence_gate_mapping")


def test_resolve_unknown_ja_tokens_high_confidence_auto_use():
    def run():
        calls = []

        def fake_research(surfaces, context="", client=None):
            calls.append(list(surfaces))
            return {
                "raw_text": "fake", "model": "fake-model", "response_id": "fake-id",
                "search_usage": {"web_search_call_count": 1}, "sources": [],
                "parsed": [{"surface": "Gloobarga", "reading": "グロバーガ",
                            "confidence": "high", "source": "https://example.com/gloobarga"}],
                "skipped": False,
            }
        orig = core.research_ja_readings
        core.research_ja_readings = fake_research
        try:
            text = "これはGloobargaという架空の企業についての文です。"
            result = core.resolve_unknown_ja_tokens(text)
            assert result["reading_dictionary"].get("gloobarga") == "グロバーガ"
            assert any(r["surface"] == "Gloobarga" for r in result["resolved"])
            assert result["unresolved_human_review"] == []
            assert len(calls) == 1

            # 2回目(同一プロセス、in-memory run cacheでweb lookup再発火なし)
            result2 = core.resolve_unknown_ja_tokens(text)
            assert result2["reading_dictionary"].get("gloobarga") == "グロバーガ"
            assert len(calls) == 1, "run内cacheにより2回目はweb lookupを呼ばないはず"

            stored = ledger.get_ja_reading_entry("gloobarga")
            assert stored is not None and stored["ja_reading_katakana"] == "グロバーガ"
        finally:
            core.research_ja_readings = orig
    _use_temp_ledger(run)
    print("PASS: test_resolve_unknown_ja_tokens_high_confidence_auto_use")


def test_resolve_unknown_ja_tokens_low_confidence_stays_human_review():
    def run():
        def fake_research(surfaces, context="", client=None):
            return {
                "raw_text": "fake", "model": "fake-model", "response_id": "fake-id",
                "search_usage": {"web_search_call_count": 1}, "sources": [],
                "parsed": [{"surface": "Zqvexx", "reading": "ズクベックス",
                            "confidence": "low", "source": "machine_approximation"}],
                "skipped": False,
            }
        orig = core.research_ja_readings
        core.research_ja_readings = fake_research
        try:
            text = "これはZqvexxという未知の語を含む文です。"
            result = core.resolve_unknown_ja_tokens(text)
            assert "zqvexx" not in result["reading_dictionary"], "low confidenceは自動使用しない(fail-safe)"
            assert "Zqvexx" in result["unresolved_human_review"]
            # ただしLedgerには記録され(次回以降の再researchを避ける)、
            # confidenceも保存されていること。
            stored = ledger.get_ja_reading_entry("zqvexx")
            assert stored is not None and stored["ja_reading_confidence"] == "low"
        finally:
            core.research_ja_readings = orig
    _use_temp_ledger(run)
    print("PASS: test_resolve_unknown_ja_tokens_low_confidence_stays_human_review")


def test_resolve_unknown_ja_tokens_no_unknown_tokens_skips_lookup():
    def run():
        calls = []

        def fake_research(surfaces, context="", client=None):
            calls.append(surfaces)
            raise AssertionError("未知語が無い場合はweb lookupを呼んではいけない")
        orig = core.research_ja_readings
        core.research_ja_readings = fake_research
        try:
            result = core.resolve_unknown_ja_tokens("これは普通の日本語の文です。")
            assert result["unresolved_human_review"] == []
            assert calls == []
        finally:
            core.research_ja_readings = orig
    _use_temp_ledger(run)
    print("PASS: test_resolve_unknown_ja_tokens_no_unknown_tokens_skips_lookup")


def test_resolve_and_augment_en_style_prefix_cache_hit_no_api_call():
    def run():
        import er006_pronunciation_research_01 as en_research

        def fail_if_called(*args, **kwargs):
            raise AssertionError("既にconfidence十分な cache hitがある場合はweb lookupを呼んではいけない")
        orig = en_research.research_pronunciations
        en_research.research_pronunciations = fail_if_called
        try:
            key = ledger.LedgerKey(surface="Ottoni", entity_type="person")
            ledger.upsert(key, {"pronunciation_hint": "oh-TOH-nee", "confidence": "high"})
            style_prefix = "Speak naturally."
            text = "We spoke with Ottoni about the plan."
            augmented, info = core.resolve_and_augment_en_style_prefix(style_prefix, text)
            assert info["hints_applied"] is True
            assert "Ottoni" in augmented and "oh-TOH-nee" in augmented
            assert style_prefix in augmented
        finally:
            en_research.research_pronunciations = orig
    _use_temp_ledger(run)
    print("PASS: test_resolve_and_augment_en_style_prefix_cache_hit_no_api_call")


def test_resolve_and_augment_en_style_prefix_low_confidence_retry_improves_and_dedupes():
    def run():
        import er006_pronunciation_research_01 as en_research

        calls = []

        def fake_research(entities, model="sonar", timeout=60.0):
            calls.append(list(entities))
            return {
                "status": "OK",
                "items": [{
                    "surface": "toteme", "entity_type": "product", "language_origin": "Swedish",
                    "canonical_spelling": "Toteme", "expected_pronunciation_ipa": "",
                    "pronunciation_hint": "toh-TEHM", "alternate_pronunciations": [],
                    "confidence": "high", "ambiguity_note": "",
                }],
                "citations": ["https://example.com/toteme"], "model": "sonar", "response_id": "fake",
                "elapsed_seconds": 0.01, "usage": {},
            }
        orig = en_research.research_pronunciations
        en_research.research_pronunciations = fake_research
        try:
            key = ledger.LedgerKey(surface="toteme", entity_type="product")
            ledger.upsert(key, {"pronunciation_hint": "", "confidence": "low"})
            style_prefix = "Speak naturally."
            text = "The brand toteme was mentioned in the article."

            augmented, info = core.resolve_and_augment_en_style_prefix(style_prefix, text)
            assert info["low_confidence_retry_attempted"] is True
            assert info["low_confidence_retry_improved"] is True
            assert info["hints_applied"] is True
            assert "toh-TEHM" in augmented
            assert len(calls) == 1

            # 2回目(同一プロセス): dedupe setにより再researchを呼ばない。
            augmented2, info2 = core.resolve_and_augment_en_style_prefix(style_prefix, text)
            assert len(calls) == 1, "同一プロセス内でのlow-confidence再researchは1回のみのはず"
            assert info2["hints_applied"] is True, "改善済みentryはcache hit経路で継続してヒントを返すはず"
        finally:
            en_research.research_pronunciations = orig
    _use_temp_ledger(run)
    print("PASS: test_resolve_and_augment_en_style_prefix_low_confidence_retry_improves_and_dedupes")


def test_resolve_and_augment_en_style_prefix_no_entity_no_change():
    def run():
        style_prefix = "Speak naturally."
        augmented, info = core.resolve_and_augment_en_style_prefix(style_prefix, "This text mentions nobody special.")
        assert augmented == style_prefix
        assert info["hints_applied"] is False
    _use_temp_ledger(run)
    print("PASS: test_resolve_and_augment_en_style_prefix_no_entity_no_change")


if __name__ == "__main__":
    test_confidence_gate_mapping()
    test_resolve_unknown_ja_tokens_high_confidence_auto_use()
    test_resolve_unknown_ja_tokens_low_confidence_stays_human_review()
    test_resolve_unknown_ja_tokens_no_unknown_tokens_skips_lookup()
    test_resolve_and_augment_en_style_prefix_cache_hit_no_api_call()
    test_resolve_and_augment_en_style_prefix_low_confidence_retry_improves_and_dedupes()
    test_resolve_and_augment_en_style_prefix_no_entity_no_change()
    print("ALL TESTS PASSED")
