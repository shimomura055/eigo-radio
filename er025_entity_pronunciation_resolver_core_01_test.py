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


def test_split_ja_reading_sources_multiple_urls_preserved():
    # Sonnet修正1回目(Opus L2所見「ja_reading_sourcesが1件しか保存されない」
    # フォローアップ): SOURCE行に複数URLがあれば全件を個別要素として保存。
    raw = "https://example.com/a と https://example.com/b (公式サイト日本語版)"
    assert core.split_ja_reading_sources(raw) == ["https://example.com/a", "https://example.com/b"]
    # 単一(またはURLなし)の場合は既存どおり1要素のまま(fail-safe)。
    assert core.split_ja_reading_sources("日本語版Wikipedia") == ["日本語版Wikipedia"]
    assert core.split_ja_reading_sources("") == []
    print("PASS: test_split_ja_reading_sources_multiple_urls_preserved")


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


def test_resolve_and_augment_en_style_prefix_skips_cascade_unresolved_low_confidence():
    # Sonnet修正1回目(Opus L2 BLOCKER-1是正): entity_type=
    # "cascade_unresolved_entity"(Stage 2 Human Review packaging専用)の
    # low confidence entryは、pre_tts配線時の再research対象にならない
    # (無関係記事で毎回有料再researchが発火していた実害への対応)。
    def run():
        import er006_pronunciation_research_01 as en_research

        def fail_if_called(*args, **kwargs):
            raise AssertionError("cascade_unresolved_entity型は再research対象から除外されるはず")
        orig = en_research.research_pronunciations
        en_research.research_pronunciations = fail_if_called
        try:
            key = ledger.LedgerKey(surface="ganis", entity_type="cascade_unresolved_entity")
            ledger.upsert(key, {"pronunciation_hint": "GANN-iss", "confidence": "low"})
            style_prefix = "Speak naturally."
            text = "The organisation released its ganis report today."
            augmented, info = core.resolve_and_augment_en_style_prefix(style_prefix, text)
            assert info["low_confidence_retry_attempted"] is False
            assert augmented == style_prefix
        finally:
            en_research.research_pronunciations = orig
    _use_temp_ledger(run)
    print("PASS: test_resolve_and_augment_en_style_prefix_skips_cascade_unresolved_low_confidence")


def test_resolve_unknown_ja_tokens_source_context_seed_cache_hit_no_lookup():
    # Sonnet修正1回目(Opus L2 BLOCKER-2是正): seed_work_canon_reading()で
    # 事前seedした作品固有読みは、同じsource_contextで呼ぶとweb lookupを
    # 一切呼ばずcache hitすること。
    def run():
        def fail_if_called(surfaces, context="", client=None):
            raise AssertionError("seed済みのwork_canon読みはweb lookupを呼んではいけない")
        orig = core.research_ja_readings
        core.research_ja_readings = fail_if_called
        try:
            core.seed_work_canon_reading("dionysius", "ディオニス", source_context="family_z_melos",
                                          sources=["https://www.aozora.gr.jp/example"])
            text = "これはDionysiusという登場人物についての文です。"
            result = core.resolve_unknown_ja_tokens(text, source_context="family_z_melos")
            assert result["reading_dictionary"].get("dionysius") == "ディオニス"
            assert result["web_lookup_called"] is False
            assert any(r["surface"] == "Dionysius" for r in result["resolved"])
        finally:
            core.research_ja_readings = orig
    _use_temp_ledger(run)
    print("PASS: test_resolve_unknown_ja_tokens_source_context_seed_cache_hit_no_lookup")


def test_resolve_unknown_ja_tokens_source_context_isolation():
    # 同じsurfaceでもsource_contextが異なれば別読みとして解決されること
    # (一般記事の史実読み vs Family Z Melosの作品固有読み)。
    def run():
        core.seed_work_canon_reading("dionysius", "ディオニュシオス", source_context="")
        core.seed_work_canon_reading("dionysius", "ディオニス", source_context="family_z_melos")
        general_text = "これはDionysiusという古代の統治者についての文です。"
        melos_text = "これはDionysiusという登場人物についての文です。"
        general_result = core.resolve_unknown_ja_tokens(general_text, source_context="")
        melos_result = core.resolve_unknown_ja_tokens(melos_text, source_context="family_z_melos")
        assert general_result["reading_dictionary"].get("dionysius") == "ディオニュシオス"
        assert melos_result["reading_dictionary"].get("dionysius") == "ディオニス"
    _use_temp_ledger(run)
    print("PASS: test_resolve_unknown_ja_tokens_source_context_isolation")


def test_resolve_unknown_ja_tokens_confidence_mirror_self_heal_on_cache_hit():
    # Sonnet修正1回目(Opus L2所見「Figma confidence不整合」是正): cache
    # hit時に鏡写しフィールドの不整合を検出したら自己修復すること。
    def run():
        ledger.upsert_ja_reading_entry("figma", {"ja_reading_katakana": "フィグマ",
                                                    "ja_reading_confidence": "high", "confidence": "low"})

        def fail_if_called(surfaces, context="", client=None):
            raise AssertionError("cache hitのはずでweb lookupを呼んではいけない")
        orig = core.research_ja_readings
        core.research_ja_readings = fail_if_called
        try:
            text = "これはFigmaというツールについての文です。"
            result = core.resolve_unknown_ja_tokens(text)
            assert result["reading_dictionary"].get("figma") == "フィグマ", "high confidenceとして自動使用されるはず"
        finally:
            core.research_ja_readings = orig
        stored = ledger.get_ja_reading_entry("figma")
        assert stored["confidence"] == "high", "cache hit時に鏡写し不整合が自己修復されるはず"
    _use_temp_ledger(run)
    print("PASS: test_resolve_unknown_ja_tokens_confidence_mirror_self_heal_on_cache_hit")


def test_resolve_unknown_ja_tokens_negative_cache_skips_repeat_lookup():
    # Sonnet修正1回目(Opus L2所見「negative cache無し」是正): web
    # lookupを実際に呼んだが対象語が解決できなかった場合、直後の別呼び出し
    # (別プロセス相当、Ledger再読込)では追加lookupなしでHUMAN_REVIEW判定
    # されること。
    def run():
        calls = []

        def fake_research(surfaces, context="", client=None):
            calls.append(list(surfaces))
            return {"raw_text": "no match", "model": "fake-model", "response_id": "fake-id",
                    "search_usage": {}, "sources": [], "parsed": [], "skipped": False}
        orig = core.research_ja_readings
        core.research_ja_readings = fake_research
        try:
            text = "これはZzznotfoundxxxという未知の語を含む文です。"
            result1 = core.resolve_unknown_ja_tokens(text)
            assert "Zzznotfoundxxx" in result1["unresolved_human_review"]
            assert len(calls) == 1
            core.reset_run_caches()  # 別プロセス相当(in-memory run cacheをクリア)
            result2 = core.resolve_unknown_ja_tokens(text)
            assert "Zzznotfoundxxx" in result2["unresolved_human_review"]
            assert len(calls) == 1, "negative cache(cooldown内)により2回目はweb lookupを呼ばないはず"
        finally:
            core.research_ja_readings = orig
    _use_temp_ledger(run)
    print("PASS: test_resolve_unknown_ja_tokens_negative_cache_skips_repeat_lookup")


def test_resolve_unknown_ja_tokens_run_lookup_cap():
    # Sonnet修正1回目(Opus L2所見「run単位lookup上限」是正): 1プロセス
    # あたりのJA web lookup API呼び出し回数がMAX_JA_WEB_LOOKUP_CALLS_PER_RUN
    # を超えたら、それ以上は呼ばずfail-safeでHUMAN_REVIEWへ倒すこと。
    def run():
        calls = []

        def fake_research(surfaces, context="", client=None):
            calls.append(list(surfaces))
            return {"raw_text": "no match", "model": "fake-model", "response_id": "fake-id",
                    "search_usage": {}, "sources": [], "parsed": [], "skipped": False}
        orig = core.research_ja_readings
        core.research_ja_readings = fake_research
        try:
            for i in range(core.MAX_JA_WEB_LOOKUP_CALLS_PER_RUN + 2):
                text = f"これはUniqxxxtoken{i}という未知の語を含む文です。"
                core.resolve_unknown_ja_tokens(text)
            assert len(calls) == core.MAX_JA_WEB_LOOKUP_CALLS_PER_RUN, (
                f"run単位上限{core.MAX_JA_WEB_LOOKUP_CALLS_PER_RUN}回を超えて呼ばれた: {len(calls)}")
        finally:
            core.research_ja_readings = orig
    _use_temp_ledger(run)
    print("PASS: test_resolve_unknown_ja_tokens_run_lookup_cap")


def test_disable_web_lookup_for_test_prevents_real_call_and_ledger_write():
    # Sonnet修正1回目(Opus L2所見「テスト時web lookup禁止スイッチ」是正):
    # スイッチ有効時は、無mockのままresearch_ja_readings()を直接呼んでも
    # 実API呼び出し・Ledger書き込みが一切発生しない(fail-safeでskipped)。
    def run():
        ledger_path = ledger.LEDGER_PATH
        assert not os.path.exists(ledger_path)
        with core.disable_web_lookup_for_test():
            result = core.research_ja_readings(["Gloobargaxxx"], context="dummy")
            assert result["skipped"] is True
            assert result.get("web_lookup_disabled_for_test") is True
        assert not os.path.exists(ledger_path), "web lookup禁止中はLedgerへの新規書き込みが発生しないはず"
    _use_temp_ledger(run)
    print("PASS: test_disable_web_lookup_for_test_prevents_real_call_and_ledger_write")


def test_ledger_json_hash_unchanged_when_web_lookup_disabled():
    # 恒久策の回帰test: web lookup禁止スイッチ有効時、production関数を
    # 未知語入りtextで直接呼んでもLedger(このtestではtemp path)の中身が
    # 一切変化しないこと(実写証跡はREPORT側でproduction ledger.jsonの
    # sha256差分でも確認する)。
    def run():
        import hashlib

        def _hash():
            if not os.path.exists(ledger.LEDGER_PATH):
                return None
            with open(ledger.LEDGER_PATH, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()

        before = _hash()
        with core.disable_web_lookup_for_test():
            text = "これはZqxvNeverseededxxxという未知の語を含む文です。"
            result = core.resolve_unknown_ja_tokens(text)
            assert result["web_lookup_called"] is False
        after = _hash()
        assert before == after, "web lookup禁止中はledger.jsonのhashが変化してはいけない"
    _use_temp_ledger(run)
    print("PASS: test_ledger_json_hash_unchanged_when_web_lookup_disabled")


if __name__ == "__main__":
    test_split_ja_reading_sources_multiple_urls_preserved()
    test_confidence_gate_mapping()
    test_resolve_unknown_ja_tokens_high_confidence_auto_use()
    test_resolve_unknown_ja_tokens_low_confidence_stays_human_review()
    test_resolve_unknown_ja_tokens_no_unknown_tokens_skips_lookup()
    test_resolve_and_augment_en_style_prefix_cache_hit_no_api_call()
    test_resolve_and_augment_en_style_prefix_low_confidence_retry_improves_and_dedupes()
    test_resolve_and_augment_en_style_prefix_no_entity_no_change()
    test_resolve_and_augment_en_style_prefix_skips_cascade_unresolved_low_confidence()
    test_resolve_unknown_ja_tokens_source_context_seed_cache_hit_no_lookup()
    test_resolve_unknown_ja_tokens_source_context_isolation()
    test_resolve_unknown_ja_tokens_confidence_mirror_self_heal_on_cache_hit()
    test_resolve_unknown_ja_tokens_negative_cache_skips_repeat_lookup()
    test_resolve_unknown_ja_tokens_run_lookup_cap()
    test_disable_web_lookup_for_test_prevents_real_call_and_ledger_write()
    test_ledger_json_hash_unchanged_when_web_lookup_disabled()
    print("ALL TESTS PASSED")
