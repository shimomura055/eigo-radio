# ============================================================
# er006_pronunciation_phase4_entity_like_test_01.py
# PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-
# LIKE-01(A-1): entity_like判定の一般化(regression fixture)
# ============================================================
# API呼び出し: 0(全てread-only。実TTS/ASR/LLM呼び出しなし。Ledgerは
# 一時ファイルへ隔離するため本番er006_output/pronunciation_ledger_01/
# ledger.jsonは読み書きしない)。
#
# 対象: er006_preprod_hardening_01_validation.py の
#   - loanword_flags()          (A-1(b): 非ASCII文字を含む小文字外来語)
#   - ledger_registered_entity_flags()
#                                (A-1(a): Ledger登録済みsurface、
#                                 同形一般語ガード付き。修正1回目で
#                                 Production既定OFFになったが、関数自体は
#                                 read-only診断ヘルパーとして残る)
#   - classify_asr_match() の entity_tokens 合流箇所
#   - protected_check() の entity_like_source(S3、provenance）
#
# 修正1回目(ユーザー判断 2026-09-28)で追加: `LedgerConditionOffTests`
# (Ledger条件が既定OFFであること・分類経路からLedgerディスク読込が
# 発生しないことの固定test)、`EntityLikeSourceProvenanceTests`
# (content_word_diffs[*].entity_like_sourceの内容確認)。
#
# 実行方法:
#   python er006_pronunciation_phase4_entity_like_test_01.py
#   .venv/Scripts/python.exe -m unittest \
#       er006_pronunciation_phase4_entity_like_test_01 -v
from __future__ import annotations

import os
import shutil
import unittest
from unittest import mock

import er006_preprod_hardening_01_validation as validation
import er006_pronunciation_ledger_01 as ledger

_TMP_LEDGER_PATH = "er006_output/_test_pronunciation_phase4_entity_like_tmp/ledger.json"


def _use_temp_ledger(test_fn):
    """PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-
    PUNCT-01のer025テストと同じ隔離パターン(本番Ledgerを一切読み書き
    しない)。ledger_registered_entity_flags()はvalidation module経由で
    同一のer006_pronunciation_ledger_01モジュールオブジェクトを参照する
    ため、ここでLEDGER_PATHを差し替えるだけで両方に反映される。"""
    orig_path = ledger.LEDGER_PATH
    if os.path.exists(os.path.dirname(_TMP_LEDGER_PATH)):
        shutil.rmtree(os.path.dirname(_TMP_LEDGER_PATH))
    ledger.LEDGER_PATH = _TMP_LEDGER_PATH
    try:
        test_fn()
    finally:
        ledger.LEDGER_PATH = orig_path
        if os.path.exists(os.path.dirname(_TMP_LEDGER_PATH)):
            shutil.rmtree(os.path.dirname(_TMP_LEDGER_PATH))


class LoanwordFlagsTests(unittest.TestCase):
    """A-1(b): 非ASCII文字を含む小文字外来語(例: minaudière)。"""

    def test_lowercase_diacritic_word_is_flagged(self):
        flags = validation.loanword_flags("Chanel's novelty minaudière was on display.")
        self.assertIn("minaudiere", flags)

    def test_pure_ascii_common_words_are_not_flagged(self):
        flags = validation.loanword_flags("The company reported a significant loss last quarter.")
        self.assertEqual(flags, set())

    def test_capitalized_ascii_proper_noun_is_not_flagged_here(self):
        # 大文字始まりのASCII固有名詞はcapitalized_flags()側の役割であり、
        # loanword_flags()は非ASCII文字の有無だけで判定する(役割分担)。
        flags = validation.loanword_flags("Altuzarra was mentioned.")
        self.assertEqual(flags, set())


class LedgerRegisteredEntityFlagsTests(unittest.TestCase):
    """A-1(a): Ledger登録済みsurface(語境界一致)+同形一般語ガード。"""

    def test_cascade_unresolved_entity_with_capitalized_canonical_is_rescued(self):
        def run():
            ledger.upsert(ledger.LedgerKey(surface="khaite", entity_type=ledger.CASCADE_UNRESOLVED_ENTITY_TYPE),
                          {"canonical_spelling": "KHAITE", "confidence": "medium"})
            flags = validation.ledger_registered_entity_flags(
                "Its examples included Khaite's palm-sized evening clutch.")
            self.assertIn("khaite", flags)
        _use_temp_ledger(run)

    def test_tts_injection_disabled_entry_is_still_used_for_classification(self):
        # 分類目的ではtts_injection_disabledの有無に関わらず登録事実を使う
        # (タスク仕様: TTS事前注入除外とは独立のチャンネル)。
        def run():
            key = ledger.LedgerKey(surface="familymart", entity_type=ledger.CASCADE_UNRESOLVED_ENTITY_TYPE)
            ledger_id = ledger.upsert(key, {"canonical_spelling": "FamilyMart", "confidence": "medium"})
            ledger.set_tts_injection_disabled(ledger_id, "test: TTS注入は無関係")
            flags = validation.ledger_registered_entity_flags("They stopped at a familymart on the way home.")
            self.assertIn("familymart", flags)
        _use_temp_ledger(run)

    def test_word_boundary_not_lowercase_in_this_text_still_rescued(self):
        # このcanonical_textでは当該語が小文字のまま(capitalized_flagsでは
        # 拾えない)が、Ledger側のcanonical_spellingが大文字始まりのため
        # A-1(a)経由で救済されることを確認する(A-1(a)固有の効果)。
        def run():
            ledger.upsert(ledger.LedgerKey(surface="wibblotron", entity_type="product"),
                          {"canonical_spelling": "Wibblotron", "confidence": "high"})
            flags = validation.ledger_registered_entity_flags(
                "The team unveiled a new wibblotron device at the show.")
            self.assertIn("wibblotron", flags)
        _use_temp_ledger(run)

    def test_same_form_guard_excludes_known_bad_entry_us_unknown(self):
        # OPEN-207実データ再現: surface="us"/canonical_spelling="unknown"
        # (別語の発音情報が誤登録された既知の混入)。canonical_spellingが
        # 小文字一般語のため、同形一般語ガードにより除外されること。
        def run():
            ledger.upsert(ledger.LedgerKey(surface="us", entity_type=ledger.CASCADE_UNRESOLVED_ENTITY_TYPE),
                          {"canonical_spelling": "unknown", "confidence": "low"})
            flags = validation.ledger_registered_entity_flags("Please contact us for more information.")
            self.assertNotIn("us", flags)
        _use_temp_ledger(run)

    def test_same_form_guard_excludes_known_bad_entry_plus_cascade(self):
        # 実Ledger実データ(2026-09-28時点)の再現: surface="plus"/
        # canonical_spelling="cascade"(placeholder、BLOCKER-1系混入)。
        def run():
            ledger.upsert(ledger.LedgerKey(surface="plus", entity_type=ledger.CASCADE_UNRESOLVED_ENTITY_TYPE),
                          {"canonical_spelling": "cascade", "confidence": "medium"})
            flags = validation.ledger_registered_entity_flags("This model costs 5 plus tax.")
            self.assertNotIn("plus", flags)
        _use_temp_ledger(run)

    def test_same_form_guard_generic_word_mark_not_registered_stays_unflagged(self):
        # "mark"はLedgerに一切登録されていない一般語(タスク仕様の例示語)。
        # 登録が無ければ当然対象にならないことを確認する(ガードの前提)。
        def run():
            flags = validation.ledger_registered_entity_flags("Please mark this item as sold.")
            self.assertNotIn("mark", flags)
        _use_temp_ledger(run)

    def test_missing_ledger_file_fails_safe_to_empty_set(self):
        def run():
            # _use_temp_ledgerが指すディレクトリごと削除済みの状態
            # (=Ledgerファイル不在)でも例外を伝播させず空集合を返す。
            flags = validation.ledger_registered_entity_flags("Some text mentioning nothing special.")
            self.assertEqual(flags, set())
        _use_temp_ledger(run)


class ClassifyAsrMatchEntityLikeGeneralizationTests(unittest.TestCase):
    """classify_asr_match()経由でのend-to-end確認(entity_tokensの合流箇所)。"""

    def test_proper_noun_via_ledger_altuzarra(self):
        def run():
            ledger.upsert(ledger.LedgerKey(surface="altuzarra", entity_type=ledger.CASCADE_UNRESOLVED_ENTITY_TYPE),
                          {"canonical_spelling": "Altuzarra", "confidence": "low"})
            r = validation.classify_asr_match(
                "The designer Altuzarra unveiled a new bag line this season.",
                "The designer Alta Zara's unveiled a new bag line this season.")
            self.assertEqual(r.classification, "ASR_VALIDATION_UNCERTAIN")
            self.assertFalse(r.should_retry)
        _use_temp_ledger(run)

    def test_lowercase_loanword_alone_minaudiere(self):
        def run():
            r = validation.classify_asr_match(
                "Chanel showed a novelty minaudière at the event.",
                "Chanel showed a novelty minidier at the event.")
            self.assertEqual(r.classification, "ASR_VALIDATION_UNCERTAIN")
            self.assertFalse(r.should_retry)
        _use_temp_ledger(run)

    def test_non_entity_negative_control_still_true_content_mismatch(self):
        # 一般語・数値・否定を含む不一致は、A-1の変更後もTRUE_CONTENT_
        # MISMATCHのまま(retry対象)であることを確認する(安全側回帰なし)。
        def run():
            r1 = validation.classify_asr_match(
                "Prices tend to increase after the trial period.",
                "Prices tend to decrease after the trial period.")
            self.assertEqual(r1.classification, "TRUE_CONTENT_MISMATCH")
            self.assertTrue(r1.should_retry)

            r2 = validation.classify_asr_match(
                "The study followed 2 groups of participants.",
                "The study followed 3 groups of participants.")
            self.assertEqual(r2.classification, "TRUE_CONTENT_MISMATCH")
            self.assertTrue(r2.should_retry)

            r3 = validation.classify_asr_match(
                "Users can cancel the plan at any time.",
                "Users cannot cancel the plan at any time.")
            self.assertEqual(r3.classification, "TRUE_CONTENT_MISMATCH")
            self.assertTrue(r3.should_retry)
        _use_temp_ledger(run)

    def test_same_form_guard_end_to_end_us_unknown_not_rescued(self):
        # 同形一般語ガードのend-to-end確認: "us"がLedgerに誤登録されていても、
        # 無関係な一般語不一致(us<->them)はTRUE_CONTENT_MISMATCHのまま。
        def run():
            ledger.upsert(ledger.LedgerKey(surface="us", entity_type=ledger.CASCADE_UNRESOLVED_ENTITY_TYPE),
                          {"canonical_spelling": "unknown", "confidence": "low"})
            r = validation.classify_asr_match(
                "Please contact us for more information about the offer.",
                "Please contact them for more information about the offer.")
            self.assertEqual(r.classification, "TRUE_CONTENT_MISMATCH")
            self.assertTrue(r.should_retry)
        _use_temp_ledger(run)

    def test_small_bag_a2_full_story_part2_real_asr_transcript(self):
        """small_bag A2 full_story_part2のfallback(minimal instruction)
        attemptで実際に観測されたcanonical text/ASR書き起こし(Stage 3e、
        er019_output/family_x_audio_production_wiring_01/
        family_x_b3_diversity_trial_01/small_bag__run_02/a2/audit/
        tts_generation_results.json、full_story_part2セグメント、
        fallback_attempts_log[0]、2026-09-27)をそのまま使う。修正前は
        khaite/minaudièreの同時誤認識によりTRUE_CONTENT_MISMATCHへ
        格上げされ、retry予算を使い切りHUMAN_REVIEW_REQUIREDへ再Lock
        していた(RESULT_PACKET_FXD1)。修正後はentity_only扱いとなり
        ASR_VALIDATION_UNCERTAIN(安全側、retry対象から外れる)へ変わる
        ことを確認する。"""
        canonical_text = (
            "ELLE included mini bags among its fall and winter 2026 style trends. "
            "Its examples included Khaite’s palm-sized evening clutch and "
            "Chanel’s novelty minaudière. They mostly hold the basics: "
            "a phone, wallet, keys, and lip products. They cannot compete with "
            "roomy bags for storage. Their job is visual. They add a special "
            "feeling. They say, “This is today’s mood.”\n\n"
            "We see the season more clearly by looking at bags beside them.")
        asr_text = (
            "Elle included mini bags among its fall and winter 2026 style trends. "
            "Its examples included Kate's palm-sized evening clutch and Chanel's "
            "novelty minidier. They mostly hold the basics: a phone, wallet, "
            "keys, and lip products. They cannot compete with roomy bags for "
            "storage. Their job is visual. They add a special feeling. They "
            "say, this is today's mood. We see the season more clearly by "
            "looking at bags beside them.")

        def run():
            ledger.upsert(ledger.LedgerKey(surface="khaite", entity_type=ledger.CASCADE_UNRESOLVED_ENTITY_TYPE),
                          {"canonical_spelling": "KHAITE", "confidence": "medium"})
            r = validation.classify_asr_match(canonical_text, asr_text)
            self.assertEqual(r.classification, "ASR_VALIDATION_UNCERTAIN",
                              f"reason={r.reason} diffs={r.protected.content_word_diffs}")
            self.assertFalse(r.should_retry)
            entity_like_flags = {d["entity_like"] for d in r.protected.content_word_diffs}
            self.assertEqual(entity_like_flags, {True},
                              "khaite/minaudiereの両方がentity_like=Trueであるべき(片方でもFalseだと"
                              "non_entity_diffsが非空になりTRUE_CONTENT_MISMATCHへ落ちる)")
        _use_temp_ledger(run)


class LedgerConditionOffTests(unittest.TestCase):
    """修正1回目(ユーザー判断 2026-09-28): Ledger登録surface条件は
    Production既定OFF(DEFERRED/NOT_ADOPTED)であることを固定するtest。"""

    def test_flag_is_false_by_default(self):
        self.assertFalse(validation.LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION,
                          "LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATIONは既定Falseのまま"
                          "であること(Ledger surface条件のProduction再有効化は別途"
                          "ユーザー承認が必要)")

    def test_ledger_only_entity_not_rescued_end_to_end(self):
        # capitalized_flags/loanword_flagsのどちらにも該当しない(本文中で
        # 小文字・非ASCII文字を含まない)が、Ledgerにのみ大文字始まりの
        # canonical_spellingで登録済みのsurfaceは、Ledger条件OFFの間は
        # entity_like扱いされず、従来通りTRUE_CONTENT_MISMATCH(retry対象)
        # のままであることを確認する(LedgerRegisteredEntityFlagsTests.
        # test_word_boundary_not_lowercase_in_this_text_still_rescuedが
        # 関数単体では引き続き救済されることの裏返し=classify_asr_match
        # 経由では到達しないことの確認)。
        def run():
            ledger.upsert(ledger.LedgerKey(surface="wibblotron", entity_type="product"),
                          {"canonical_spelling": "Wibblotron", "confidence": "high"})
            r = validation.classify_asr_match(
                "The team unveiled a new wibblotron device at the show.",
                "The team unveiled a new wibbleatron device at the show.")
            self.assertEqual(r.classification, "TRUE_CONTENT_MISMATCH")
            self.assertTrue(r.should_retry)
        _use_temp_ledger(run)

    def test_classify_asr_match_does_not_touch_ledger_disk_when_flag_off(self):
        # フラグOFFの間、_classify_asr_match_core()のentity_tokens合流箇所は
        # ledger_registered_entity_flags()自体を呼ばない(=er006_pronunciation_
        # ledger_01.get_low_confidence_entries_for_text()経由のディスク読込
        # [_load()]が発生しない)ことを、call countで確認する(例外を
        # ledger_registered_entity_flags()自身のtry/exceptに握りつぶされない
        # よう、side_effectで例外を上げるのではなくmock呼び出し回数で判定する)。
        with mock.patch.object(ledger, "get_low_confidence_entries_for_text") as mock_fn:
            r = validation.classify_asr_match(
                "Prices tend to increase after the trial period.",
                "Prices tend to decrease after the trial period.")
            self.assertEqual(r.classification, "TRUE_CONTENT_MISMATCH")
            mock_fn.assert_not_called()

    def test_ledger_registered_entity_flags_function_itself_still_callable(self):
        # 関数自体は削除しない(将来Ledger surface条件を再検討する際に
        # 再利用できるよう残す)。フラグOFFでも直接呼び出せば従来通り動く
        # ことを確認する(read-only診断ヘルパーとしての独立性)。
        def run():
            ledger.upsert(ledger.LedgerKey(surface="khaite", entity_type=ledger.CASCADE_UNRESOLVED_ENTITY_TYPE),
                          {"canonical_spelling": "KHAITE", "confidence": "medium"})
            flags = validation.ledger_registered_entity_flags(
                "Its examples included Khaite's palm-sized evening clutch.")
            self.assertIn("khaite", flags)
        _use_temp_ledger(run)


class EntityLikeSourceProvenanceTests(unittest.TestCase):
    """S3: content_word_diffs[*].entity_like_source(capitalized/loanwordの
    集合)がobservability用に正しく付与されることを確認する(分類結果
    [entity_like自体]には影響しないことも合わせて確認)。"""

    def test_capitalized_source_only(self):
        def run():
            r = validation.classify_asr_match(
                "The designer Altuzarra unveiled a new bag line this season.",
                "The designer Alta Zara's unveiled a new bag line this season.")
            entity_diffs = [d for d in r.protected.content_word_diffs if d["entity_like"]]
            self.assertTrue(entity_diffs)
            for d in entity_diffs:
                self.assertEqual(d["entity_like_source"], ["capitalized"])
        _use_temp_ledger(run)

    def test_loanword_source_only(self):
        def run():
            r = validation.classify_asr_match(
                "Chanel showed a novelty minaudière at the event.",
                "Chanel showed a novelty minidier at the event.")
            entity_diffs = [d for d in r.protected.content_word_diffs if d["entity_like"]]
            self.assertTrue(entity_diffs)
            for d in entity_diffs:
                self.assertEqual(d["entity_like_source"], ["loanword"])
        _use_temp_ledger(run)

    def test_non_entity_diff_has_empty_source(self):
        def run():
            r = validation.classify_asr_match(
                "Prices tend to increase after the trial period.",
                "Prices tend to decrease after the trial period.")
            for d in r.protected.content_word_diffs:
                if not d["entity_like"]:
                    self.assertEqual(d["entity_like_source"], [])
        _use_temp_ledger(run)

    def test_aggregate_entity_like_sources_helper(self):
        diffs = [
            {"entity_like": True, "entity_like_source": ["capitalized"]},
            {"entity_like": True, "entity_like_source": ["loanword"]},
            {"entity_like": False, "entity_like_source": []},
        ]
        self.assertEqual(validation.aggregate_entity_like_sources(diffs), ["capitalized", "loanword"])
        self.assertEqual(validation.aggregate_entity_like_sources([]), [])
        # 古い形式(entity_like_sourceキーが無い)が混ざっても例外を出さない。
        self.assertEqual(
            validation.aggregate_entity_like_sources([{"entity_like": True}]), [])


def run():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (LoanwordFlagsTests, LedgerRegisteredEntityFlagsTests,
                ClassifyAsrMatchEntityLikeGeneralizationTests,
                LedgerConditionOffTests, EntityLikeSourceProvenanceTests):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run()
