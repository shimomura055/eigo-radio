# ============================================================
# er011_open121_repetition_qa_production_wiring_01_test_01.py
# OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01
# ============================================================
# 監視対象: er011_open121_repetition_qa_production_01.py(判定ロジック
# 本体、Trial-01/02から無変更移植)、er003_v1_repro01_main_generate.py・
# er003_v1_crosslevel_audio_02_common.py・er003_v1_sing01_news_tail_
# fix.py・er003_v1_n3_01_tts_generate.py(Production配線・適用範囲限定)。
#
# 実行方法: .venv/Scripts/python.exe er011_open121_repetition_qa_
#   production_wiring_01_test_01.py
from __future__ import annotations

import inspect
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_b1_p9a_audio as p9a
import er003_v1_crosslevel_audio_02_common as crosslevel_common
import er003_v1_n3_01_tts_generate as n3
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er008_disfluency_qa_18 as dq18
import er011_open121_repetition_qa_production_01 as repetition_qa

TRIAL01_DIR = "er011_output/open121_tts_repetition_general_qa_trial_01"
REAL_POINT_TWO_BUGGY_WAV = f"{TRIAL01_DIR}/test_set/positives_real/real_point_two_buggy.wav"
REAL_B1_FSP1_FALSESTART_WAV = f"{TRIAL01_DIR}/test_set/positives_real/real_b1_fsp1_falsestart_partial_word.wav"
CLEAN_NEGATIVE_WAV = f"{TRIAL01_DIR}/test_set/negatives_reused/a2_point_one_clean.wav"

REAL_POINT_TWO_CANONICAL_TEXT = (
    "Young travelers are not one single market. Women aged 29 and under "
    "still showed strong interest in famous tourist places, at about 45%. "
    "Gourmet travel was even higher, at about 52%. This is not the same "
    "picture as the male interest in solo and hobby-based trips. The useful "
    "lesson is not that sightseeing is ending. Different young travelers may "
    "be looking for different kinds of value from the same holiday.")
REAL_B1_FSP1_CANONICAL_TEXT = ("As of September 2026, travel surveys in Japan tell a story with two "
                                "different speeds.")
CLEAN_NEGATIVE_CANONICAL_TEXT = (
    "Slow travel may be less about adding nights and more about choosing how "
    "to use the day. Among men aged 29 and under, solo travel was about 25%, "
    "and hobby-focused travel was about 24%. A separate survey found that "
    "about 90% of Gen Z respondents wanted free time inside an overseas tour. "
    "About 80% wanted at least half a day. A short trip can still feel more "
    "personal when the traveler has room to choose.")


# ============================================================
# Part 1: 方式A(n-gram)判定ロジック(合成データ、Trial-01/dq18テストと
# 同じ書式)
# ============================================================
class NgramRepetitionLogicTests(unittest.TestCase):
    def _words(self, tokens_with_times):
        return [{"text": t, "start": s, "end": e} for t, s, e in tokens_with_times]

    def test_flags_non_canonical_phrase_repeat(self):
        words = self._words([
            ("The", 0.0, 0.2), ("cat", 0.2, 0.4), ("sat", 0.4, 0.6), ("down.", 0.6, 0.8),
            ("Later", 9.0, 9.3), ("the", 9.3, 9.5), ("cat", 9.5, 9.7),
            ("sat", 9.7, 9.9), ("down.", 9.9, 10.1),
        ])
        r = repetition_qa.detect_ngram_repetition(words, canonical_text="The cat sat down. Later it slept.")
        self.assertTrue(r["flagged"])
        self.assertEqual(len(r["flagged_matches"]), 1)
        self.assertEqual(r["flagged_matches"][0]["n_words"], 4)

    def test_does_not_flag_intentional_canonical_repeat(self):
        canon = "Not now. Not later. Not ever. The answer stays the same no matter when you ask."
        words = self._words([(w, i * 0.3, i * 0.3 + 0.25) for i, w in enumerate(canon.split())])
        r = repetition_qa.detect_ngram_repetition(words, canonical_text=canon, min_words=1)
        # "Not"は3回canonicalに出現するため、意図的反復として非flag扱い。
        for m in r["matches"]:
            if m["span_text"].strip().lower().rstrip(".") == "not":
                self.assertFalse(m["flagged"], m)

    def test_below_min_words_not_flagged(self):
        words = self._words([
            ("Yes.", 0.0, 0.3), ("Later", 5.0, 5.3), ("yes.", 5.3, 5.6),
        ])
        r = repetition_qa.detect_ngram_repetition(words, canonical_text=None, min_words=3)
        self.assertFalse(r["flagged"])


# ============================================================
# OPEN-127-EM-DASH-TOKEN-BOUNDARY-PRODUCTION-WIRING-01: em dash(U+2014)
# のみを空白=token境界として扱う前処理(candidate1a、
# TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01_REPORT.md
# で`VALIDATED`)。en dash(–, U+2013)・hyphen(-)は対象外。
# ============================================================
class EmDashTokenBoundaryTests(unittest.TestCase):
    def _words(self, tokens_with_times):
        return [{"text": t, "start": s, "end": e} for t, s, e in tokens_with_times]

    def test_a_voice_b_style_intentional_repeat_canonical_2_asr_2_not_flagged(self):
        # Voice B point_two実データそのもの(em dash前後に空白なし、
        # `er012_output/editorial_b_family_production_phase1_02/b1b/
        # parts.json`のpoint_two_body抜粋)。「do not need」がcanonical・
        # ASR双方で2回ずつ出現する意図的な並行構文。
        canon = ("Since working from home gave me a place of my own, I do "
                  "not need one fixed spot at the office. I value being "
                  "able to change my surroundings and choose a place that "
                  "fits my mood, my task, and the people I need—or do not "
                  "need—around me.")
        # ASR側はTTS発話由来でem dashが単語として現れず、"need" "or"
        # "do" "not" "need" "around" "me"が独立tokenとして書き起こされる
        # (「do not need」が2回出現=canonical側の意図的な並行構文と一致)。
        words = self._words([
            ("Since", 0.0, 0.3), ("working", 0.3, 0.6), ("from", 0.6, 0.8),
            ("home", 0.8, 1.0), ("gave", 1.0, 1.2), ("me", 1.2, 1.3),
            ("a", 1.3, 1.4), ("place", 1.4, 1.6), ("of", 1.6, 1.7),
            ("my", 1.7, 1.8), ("own,", 1.8, 2.0), ("I", 2.0, 2.1),
            ("do", 2.1, 2.2), ("not", 2.2, 2.3), ("need", 2.3, 2.5),
            ("one", 2.5, 2.6), ("fixed", 2.6, 2.8), ("spot", 2.8, 3.0),
            ("at", 3.0, 3.1), ("the", 3.1, 3.2), ("office.", 3.2, 3.5),
            ("I", 10.0, 10.1), ("value", 10.1, 10.3), ("being", 10.3, 10.5),
            ("able", 10.5, 10.7), ("to", 10.7, 10.8), ("change", 10.8, 11.0),
            ("my", 11.0, 11.1), ("surroundings", 11.1, 11.5), ("and", 11.5, 11.6),
            ("choose", 11.6, 11.8), ("a", 11.8, 11.9), ("place", 11.9, 12.1),
            ("that", 12.1, 12.2), ("fits", 12.2, 12.4), ("my", 12.4, 12.5),
            ("mood,", 12.5, 12.7), ("my", 12.7, 12.8), ("task,", 12.8, 13.0),
            ("and", 13.0, 13.1), ("the", 13.1, 13.2), ("people", 13.2, 13.4),
            ("I", 13.4, 13.5), ("need", 13.5, 13.7), ("or", 13.7, 13.8),
            ("do", 13.8, 13.9), ("not", 13.9, 14.0), ("need", 14.0, 14.2),
            ("around", 14.2, 14.4), ("me.", 14.4, 14.6),
        ])
        r = repetition_qa.detect_ngram_repetition(words, canonical_text=canon, min_words=3)
        do_not_need_matches = [m for m in r["matches"] if m["span_text"].strip().lower() == "do not need"]
        self.assertTrue(do_not_need_matches, r)
        for m in do_not_need_matches:
            self.assertEqual(m["canonical_repeat_count"], 2, m)
            self.assertTrue(m["intentional"], m)
            self.assertFalse(m["flagged"], m)
        self.assertFalse(r["flagged"], r)

    def test_b_true_duplicate_canonical_1_asr_2_still_flagged(self):
        # em dashが同じ台本内に存在しても(無関係箇所)、真の重複
        # (canonical側は1回のみ、ASR側で偶発的に2回出現)は引き続きflag
        # されること。
        canon = ("The people I need—or do not need—around me. "
                  "The cat sat down quietly in the corner.")
        words = self._words([
            ("The", 0.0, 0.2), ("cat", 0.2, 0.4), ("sat", 0.4, 0.6), ("down", 0.6, 0.8),
            ("quietly.", 8.0, 8.2), ("Later", 9.0, 9.3), ("the", 9.3, 9.5),
            ("cat", 9.5, 9.7), ("sat", 9.7, 9.9), ("down", 9.9, 10.1),
        ])
        r = repetition_qa.detect_ngram_repetition(words, canonical_text=canon, min_words=3)
        self.assertTrue(r["flagged"], r)
        self.assertEqual(r["flagged_matches"][0]["n_words"], 4)

    def test_c_hyphen_en_dash_percent_numeric_cases_unchanged(self):
        # ハイフン(-)・en dash(–, U+2013)・%記号・小数点数字は対象外
        # (em dashのみを空白へ置換、他の記号のtokenizationは無変更、
        # 既存dq18._normalize_tokenによる句読点除去挙動もそのまま)。
        def expected(text):
            return [dq18._normalize_token(w) for w in text.split()]

        hyphen_text = "well-known fact well-known fact"
        self.assertEqual(
            repetition_qa._normalize_tokens(hyphen_text), expected(hyphen_text),
            "ハイフンは空白へ置換されず、既存のtext.split()挙動のまま",
        )
        en_dash_text = "pages 10–12 were revised pages 10–12 were revised"
        self.assertEqual(
            repetition_qa._normalize_tokens(en_dash_text), expected(en_dash_text),
            "en dash(U+2013)は空白へ置換されない",
        )
        percent_numeric_text = "about 45% growth and 108.95 percent of respondents"
        self.assertEqual(
            repetition_qa._normalize_tokens(percent_numeric_text), expected(percent_numeric_text),
            "%記号・小数点付き数字のtokenizationは無変更",
        )

    def test_d_em_dash_with_and_without_surrounding_whitespace(self):
        # em dash前後に空白がある場合("word — word")・無い場合
        # ("word—word")の両方でtoken境界として機能すること。
        no_space = "need—or"
        with_space = "need — or"
        self.assertEqual(repetition_qa._normalize_tokens(no_space), ["need", "or"])
        self.assertEqual(repetition_qa._normalize_tokens(with_space), ["need", "or"])


# ============================================================
# Part 2: 方式D/D'(スペクトル、統合計算)、実音声固定資産で判定
# (Trial-01保全済みfixture、読み取りのみ)
# ============================================================
@unittest.skipUnless(os.path.exists(REAL_POINT_TWO_BUGGY_WAV), "OPEN-121 Trial-01 fixture not present")
class SpectralProfilesRealFixtureTests(unittest.TestCase):
    def test_shared_bundle_reused_by_both_profiles(self):
        bundle = repetition_qa.compute_shared_self_similarity(REAL_POINT_TWO_BUGGY_WAV)
        d = repetition_qa.analyze_profile_d_long_lag(bundle)
        d_prime = repetition_qa.analyze_profile_d_prime_short_lag(bundle)
        self.assertIsNotNone(bundle["sim"])
        self.assertGreaterEqual(d["best_run_length_seconds"], 0.0)
        self.assertGreaterEqual(d_prime["best_run_length_seconds"], 0.0)

    def test_profile_d_flags_point_two_whole_span_repeat(self):
        # Point Two型(句・文まるごと反復、gap>=8秒)は方式D(long-lag)が
        # 検知する(Trial-01較正値: best_run_length_seconds=0.16秒、
        # 閾値0.12秒以上)。
        bundle = repetition_qa.compute_shared_self_similarity(REAL_POINT_TWO_BUGGY_WAV)
        d = repetition_qa.analyze_profile_d_long_lag(bundle)
        self.assertTrue(d["flagged"], d)

    def test_profile_d_prime_flags_b1_fsp1_falsestart(self):
        # false start型(語の途中で切れて即再開、lag<1.0秒)は方式D(long-lag、
        # min_lag=1.0秒)では構造的に検知できず、方式D'(short-lag、
        # 0.5-2.0秒)のみが検知する(Trial-02較正値: run_length=0.74秒、
        # 閾値0.6秒以上)。
        bundle = repetition_qa.compute_shared_self_similarity(REAL_B1_FSP1_FALSESTART_WAV)
        d = repetition_qa.analyze_profile_d_long_lag(bundle)
        d_prime = repetition_qa.analyze_profile_d_prime_short_lag(bundle)
        self.assertFalse(d["flagged"], d)
        self.assertTrue(d_prime["flagged"], d_prime)

    def test_profile_d_prime_does_not_flag_clean_negative(self):
        bundle = repetition_qa.compute_shared_self_similarity(CLEAN_NEGATIVE_WAV)
        d_prime = repetition_qa.analyze_profile_d_prime_short_lag(bundle)
        self.assertFalse(d_prime["flagged"], d_prime)

    def test_boundary_monitoring_fields_always_present_even_when_not_flagged(self):
        # 境界値monitoring: flag/非flagにかかわらず最大run長・lag・
        # similarityが常に記録されること。
        r = repetition_qa.run_spectral_checks(CLEAN_NEGATIVE_WAV)
        self.assertIn("best_run_length_seconds", r["profile_d"])
        self.assertIn("best_run_length_seconds", r["profile_d_prime"])
        self.assertIn("lag", r["profile_d_prime"])
        self.assertIn("similarity_at_start", r["profile_d_prime"])
        self.assertFalse(r["profile_d"]["flagged"])
        self.assertFalse(r["profile_d_prime"]["flagged"])


@unittest.skipUnless(os.path.exists(REAL_POINT_TWO_BUGGY_WAV) and os.path.exists(REAL_B1_FSP1_FALSESTART_WAV)
                      and os.path.exists(CLEAN_NEGATIVE_WAV), "OPEN-121 Trial-01 fixtures not present")
class EvaluateRepetitionQaEndToEndTests(unittest.TestCase):
    """方式A+D+D'の統合判定(evaluate_repetition_qa)。ローカルfaster-
    whisperを実行するため実行時間がやや長い(既存dq18テストと同様)。"""

    def test_flags_point_two_whole_span_repeat_via_method_a_and_d(self):
        r = repetition_qa.evaluate_repetition_qa(
            REAL_POINT_TWO_BUGGY_WAV, REAL_POINT_TWO_CANONICAL_TEXT, language="en")
        self.assertTrue(r["flagged"], r)
        self.assertTrue(r["method_a_ngram"]["flagged"])
        self.assertTrue(r["method_d_spectral_long_lag"]["flagged"])

    def test_flags_b1_fsp1_falsestart_via_method_d_prime_only(self):
        r = repetition_qa.evaluate_repetition_qa(
            REAL_B1_FSP1_FALSESTART_WAV, REAL_B1_FSP1_CANONICAL_TEXT, language="en")
        self.assertTrue(r["flagged"], r)
        self.assertFalse(r["method_a_ngram"]["flagged"])
        self.assertFalse(r["method_d_spectral_long_lag"]["flagged"])
        self.assertTrue(r["method_d_prime_spectral_short_lag"]["flagged"])

    def test_does_not_flag_clean_negative(self):
        r = repetition_qa.evaluate_repetition_qa(
            CLEAN_NEGATIVE_WAV, CLEAN_NEGATIVE_CANONICAL_TEXT, language="en")
        self.assertFalse(r["flagged"], r)


# ============================================================
# Part 3: apply_repetition_qa_gate(既存dq18.apply_disfluency_gateと同一
# のANDゲートパターン)
# ============================================================
class ApplyRepetitionQaGateTests(unittest.TestCase):
    def test_disabled_does_not_check_and_passes_through(self):
        result = repetition_qa.apply_repetition_qa_gate(
            True, "nonexistent_path.wav", "some canonical text", enabled=False)
        self.assertTrue(result["verified"])
        self.assertFalse(result["repetition_qa_checked"])
        self.assertIsNone(result["repetition_qa_evidence"])

    def test_not_verified_does_not_check(self):
        result = repetition_qa.apply_repetition_qa_gate(
            False, "nonexistent_path.wav", "some canonical text", enabled=True)
        self.assertFalse(result["verified"])
        self.assertFalse(result["repetition_qa_checked"])

    @unittest.skipUnless(os.path.exists(REAL_POINT_TWO_BUGGY_WAV), "OPEN-121 Trial-01 fixture not present")
    def test_enabled_and_verified_flags_known_positive(self):
        result = repetition_qa.apply_repetition_qa_gate(
            True, REAL_POINT_TWO_BUGGY_WAV, REAL_POINT_TWO_CANONICAL_TEXT, language="en", enabled=True)
        self.assertFalse(result["verified"])  # flagged -> ANDゲートでverified=False
        self.assertTrue(result["repetition_qa_checked"])
        self.assertTrue(result["repetition_qa_evidence"]["flagged"])

    @unittest.skipUnless(os.path.exists(CLEAN_NEGATIVE_WAV), "OPEN-121 Trial-01 fixture not present")
    def test_enabled_and_verified_passes_clean_negative(self):
        result = repetition_qa.apply_repetition_qa_gate(
            True, CLEAN_NEGATIVE_WAV, CLEAN_NEGATIVE_CANONICAL_TEXT, language="en", enabled=True)
        self.assertTrue(result["verified"])
        self.assertTrue(result["repetition_qa_checked"])
        self.assertFalse(result["repetition_qa_evidence"]["flagged"])


# ============================================================
# Part 4: Production配線(適用範囲限定)。TTS/ASRの外部呼び出しはすべて
# モックし、実APIは一切呼ばない(既存er011_keyphrase_en_asr_false_
# rejection_cascade_prod_wiring_01_test_01.pyと同じ方針)。
# ============================================================
class _FakeClassification:
    def __init__(self, classification: str):
        self.classification = classification
        self.connected_speech_info = None
        self.reading_resolver_info = None


def _fake_generate_narration_snippet(content: bytes = b"AUDIO"):
    def fake(text, language, out_path, tts_call_fn=None, safety_margin_seconds=None,
             style_prefix_override=None):
        with open(out_path, "wb") as f:
            f.write(content)
        return {"status": "OK", "text": text, "language": language, "path": out_path,
                "model": "fake-en-model", "voice": "Aoede", "duration_seconds": 1.0}
    return fake


class NarrationSnippetVerifiedStrictRepetitionQaScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_open121_repqa_prod_wiring_test_")
        self.out_path = os.path.join(self.tmp_dir, "probe.wav").replace("\\", "/")
        self.orig_transcribe = repro01.routing.transcribe
        self.orig_cascade = repro01.secondary_asr.evaluate_attempt_with_cascade
        self.orig_evaluate_repetition_qa = repetition_qa.evaluate_repetition_qa

        def fake_transcribe(wav_path, language=None, timeout_seconds=90.0, prompt=None):
            return "test phrase", None

        def fake_cascade(text, asr_text, history, out_path, language=None, ledger_phrases=None,
                          cascade_enabled=None, force_secondary=False,
                          enable_non_latin_cascade=False,
                          enable_connected_speech_equivalence_layer=False, detail_out=None):
            if detail_out is not None:
                detail_out.update({"cascade_invoked": False, "non_latin_cascade_invoked": False, "steps": []})
            return True, False, _FakeClassification("exact")

        repro01.routing.transcribe = fake_transcribe
        repro01.secondary_asr.evaluate_attempt_with_cascade = fake_cascade

    def tearDown(self):
        repro01.routing.transcribe = self.orig_transcribe
        repro01.secondary_asr.evaluate_attempt_with_cascade = self.orig_cascade
        repetition_qa.evaluate_repetition_qa = self.orig_evaluate_repetition_qa
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_default_disabled_does_not_invoke_repetition_qa(self):
        calls = {"n": 0}

        def tracking_evaluate(*a, **k):
            calls["n"] += 1
            return {"flagged": True}

        repetition_qa.evaluate_repetition_qa = tracking_evaluate
        with mock.patch.object(p9a, "generate_narration_snippet",
                                side_effect=_fake_generate_narration_snippet()):
            core = repro01.generate_narration_snippet_verified_strict.__wrapped__
            result = core("test phrase", "en", self.out_path, "test phrase", max_attempts=1)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(calls["n"], 0, "enable_repetition_qaを渡さない既定呼び出しは追加計算を一切行わない")
        self.assertFalse(result["repetition_qa_checked"])
        self.assertIsNone(result["repetition_qa_evidence"])

    def test_explicit_enable_invokes_repetition_qa_and_gates_on_flagged(self):
        calls = {"n": 0}

        def tracking_evaluate(path, canonical_text, language="en"):
            calls["n"] += 1
            return {"flagged": True, "method_a_ngram": {"flagged": True},
                    "method_d_spectral_long_lag": {"flagged": False},
                    "method_d_prime_spectral_short_lag": {"flagged": False}}

        repetition_qa.evaluate_repetition_qa = tracking_evaluate
        with mock.patch.object(p9a, "generate_narration_snippet",
                                side_effect=_fake_generate_narration_snippet()):
            core = repro01.generate_narration_snippet_verified_strict.__wrapped__
            result = core("test phrase", "en", self.out_path, "test phrase", max_attempts=1,
                           enable_repetition_qa=True)
        # 3回ともflagged扱いになりretryを使い切りSTOPPEDへ到達するはず。
        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(calls["n"], 1)  # max_attempts=1指定のため1回のみ

    def test_japanese_branch_never_invokes_repetition_qa_even_if_flag_passed(self):
        calls = {"n": 0}

        def tracking_evaluate(*a, **k):
            calls["n"] += 1
            return {"flagged": False}

        repetition_qa.evaluate_repetition_qa = tracking_evaluate
        orig_ja_cascade = repro01.ja_secondary.evaluate_attempt_ja_with_cascade

        def fake_ja_cascade(text, asr_text, out_path, cascade_enabled=None):
            return True, False, _FakeClassification("exact")

        repro01.ja_secondary.evaluate_attempt_ja_with_cascade = fake_ja_cascade
        try:
            with mock.patch.object(p9a, "generate_narration_snippet",
                                    side_effect=_fake_generate_narration_snippet()):
                core = repro01.generate_narration_snippet_verified_strict.__wrapped__
                result = core("テストフレーズ", "ja", self.out_path, "テストフレーズ", max_attempts=1,
                               enable_repetition_qa=True)
        finally:
            repro01.ja_secondary.evaluate_attempt_ja_with_cascade = orig_ja_cascade
        self.assertEqual(result["status"], "OK")
        self.assertEqual(calls["n"], 0, "日本語経路はenable_repetition_qa=Trueでも一切呼ばれない")


class ProductionScopeSourceInspectionTests(unittest.TestCase):
    """ソースコード直接確認による適用範囲限定の証拠(既存OPEN-122
    ...production_wiring_01_test_01.pyのPart 3と同じ方針)。"""

    def test_generate_key_phrase_component_verified_does_not_pass_flag(self):
        src = inspect.getsource(repro01.generate_key_phrase_component_verified)
        self.assertNotIn("enable_repetition_qa", src)

    def test_japanese_secondary_asr_module_independent_of_repetition_qa(self):
        import er007_ja_secondary_asr_01 as ja_secondary
        src = inspect.getsource(ja_secondary)
        self.assertNotIn("repetition_qa_production", src)
        self.assertNotIn("er011_open121_repetition_qa_production_01", src)

    def test_n3_01_a2_body_loop_scopes_flag_to_4_segments_only(self):
        src = inspect.getsource(n3.generate_a2_segments)
        # enable_repetition_qaを渡すのは本文4segmentループのみであること
        # (この関数内で1箇所だけキーワードが出現する)。
        self.assertEqual(src.count("enable_repetition_qa=("), 1)
        self.assertIn(
            'name in ("full_story_part1", "full_story_part2", "point_one", "point_two")',
            src)

    def test_n3_01_b1_body_loop_scopes_flag_to_4_segments_only(self):
        src = inspect.getsource(n3.generate_b1_segments)
        self.assertEqual(src.count("enable_repetition_qa=("), 1)
        self.assertIn(
            'name in ("full_story_part1", "full_story_part2", "point_one", "point_two")',
            src)

    def test_a2_comment_preview_calls_do_not_reference_repetition_qa(self):
        # A2のComment/Preview/日本語title(generate_a2_japanese_with_
        # reading_safety経由)はer011_open121_repetition_qa_production_01
        # を一切importしない独立経路であることを確認する。
        import er003_v1_a2_audio_02_generate as audio02
        src = inspect.getsource(audio02)
        self.assertNotIn("er011_open121_repetition_qa_production_01", src)


class GenerateEnglishSegmentWithFallbackScopeTests(unittest.TestCase):
    """crosslevel_common.generate_english_segment_with_fallback: fallback
    (minimal instruction)経路でもenable_repetition_qa=Falseの既定では
    追加計算が発生しないこと。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_open121_repqa_fallback_test_")
        self.out_path = os.path.join(self.tmp_dir, "probe.wav").replace("\\", "/")
        self.orig_standard = crosslevel_common.generate_narration_snippet_verified_strict
        self.orig_transcribe = crosslevel_common.routing.transcribe
        self.orig_cascade = crosslevel_common.secondary_asr.evaluate_attempt_with_cascade
        self.orig_minimal = crosslevel_common.repro01.generate_english_component_minimal_instruction
        self.orig_evaluate_repetition_qa = repetition_qa.evaluate_repetition_qa

    def tearDown(self):
        crosslevel_common.generate_narration_snippet_verified_strict = self.orig_standard
        crosslevel_common.routing.transcribe = self.orig_transcribe
        crosslevel_common.secondary_asr.evaluate_attempt_with_cascade = self.orig_cascade
        crosslevel_common.repro01.generate_english_component_minimal_instruction = self.orig_minimal
        repetition_qa.evaluate_repetition_qa = self.orig_evaluate_repetition_qa
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_fallback_path_default_disabled_does_not_invoke_repetition_qa(self):
        calls = {"n": 0}

        def tracking_evaluate(*a, **k):
            calls["n"] += 1
            return {"flagged": False}

        repetition_qa.evaluate_repetition_qa = tracking_evaluate

        # standard経路を即STOPPEDにしてfallback(minimal instruction)へ
        # 強制的に進ませる。
        crosslevel_common.generate_narration_snippet_verified_strict = \
            lambda *a, **k: {"status": "STOPPED", "attempts_log": []}

        def fake_minimal(text, out_path):
            with open(out_path, "wb") as f:
                f.write(b"AUDIO")
            return {"status": "OK", "text": text, "path": out_path}

        crosslevel_common.repro01.generate_english_component_minimal_instruction = fake_minimal
        crosslevel_common.routing.transcribe = lambda *a, **k: ("test phrase", None)
        crosslevel_common.secondary_asr.evaluate_attempt_with_cascade = \
            lambda *a, **k: (True, False, _FakeClassification("exact"))

        result = crosslevel_common.generate_english_segment_with_fallback(
            "test phrase", self.out_path, "test phrase", max_attempts=2)
        self.assertEqual(result.get("status"), "OK")
        self.assertTrue(result.get("fallback_used"))
        self.assertEqual(calls["n"], 0)


class GenerateNewsNarrationWideMarginScopeTests(unittest.TestCase):
    """news_tail_fix.generate_news_narration_wide_margin(B1本文経路):
    既定enable_repetition_qa=Falseでは追加計算が発生しないこと。TTS/ASR
    外部呼び出しはすべてモックする。"""

    def setUp(self):
        import numpy as np
        self.np = np
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_open121_repqa_newstail_test_")
        self.out_path = os.path.join(self.tmp_dir, "probe.wav").replace("\\", "/")
        self.orig_call_tts = news_tail_fix.common._call_tts_with_retry
        self.orig_trim = news_tail_fix.p3u.trim_english_keyword_silence
        self.orig_anomaly = news_tail_fix.safety.detect_duration_anomaly
        self.orig_transcribe = news_tail_fix.routing.transcribe
        self.orig_cascade = news_tail_fix.secondary_asr.evaluate_attempt_with_cascade
        self.orig_evaluate_repetition_qa = repetition_qa.evaluate_repetition_qa

        fake_pcm = self.np.zeros(4000, dtype=self.np.int16).tobytes()
        news_tail_fix.common._call_tts_with_retry = lambda *a, **k: (fake_pcm, 0, True, None)
        news_tail_fix.p3u.trim_english_keyword_silence = lambda samples, sr, safety_margin_seconds=None: (
            self.np.zeros(sr, dtype=self.np.float32), {"raw_duration_seconds": 1.0})
        news_tail_fix.safety.detect_duration_anomaly = lambda *a, **k: {"is_anomaly": False}
        news_tail_fix.routing.transcribe = lambda *a, **k: ("test phrase", None)
        news_tail_fix.secondary_asr.evaluate_attempt_with_cascade = \
            lambda *a, **k: (True, False, _FakeClassification("exact"))

    def tearDown(self):
        news_tail_fix.common._call_tts_with_retry = self.orig_call_tts
        news_tail_fix.p3u.trim_english_keyword_silence = self.orig_trim
        news_tail_fix.safety.detect_duration_anomaly = self.orig_anomaly
        news_tail_fix.routing.transcribe = self.orig_transcribe
        news_tail_fix.secondary_asr.evaluate_attempt_with_cascade = self.orig_cascade
        repetition_qa.evaluate_repetition_qa = self.orig_evaluate_repetition_qa
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_default_disabled_does_not_invoke_repetition_qa(self):
        calls = {"n": 0}

        def tracking_evaluate(*a, **k):
            calls["n"] += 1
            return {"flagged": False}

        repetition_qa.evaluate_repetition_qa = tracking_evaluate
        result = news_tail_fix.generate_news_narration_wide_margin("test phrase", self.out_path, max_attempts=1)
        self.assertEqual(result.get("status"), "OK")
        self.assertEqual(calls["n"], 0)
        self.assertFalse(result.get("repetition_qa_checked"))

    def test_explicit_enable_invokes_repetition_qa(self):
        calls = {"n": 0}

        def tracking_evaluate(path, canonical_text, language="en"):
            calls["n"] += 1
            return {"flagged": False, "method_a_ngram": {"flagged": False},
                    "method_d_spectral_long_lag": {"flagged": False},
                    "method_d_prime_spectral_short_lag": {"flagged": False}}

        repetition_qa.evaluate_repetition_qa = tracking_evaluate
        result = news_tail_fix.generate_news_narration_wide_margin(
            "test phrase", self.out_path, max_attempts=1, enable_repetition_qa=True)
        self.assertEqual(result.get("status"), "OK")
        self.assertEqual(calls["n"], 1)
        self.assertTrue(result.get("repetition_qa_checked"))


if __name__ == "__main__":
    unittest.main()
