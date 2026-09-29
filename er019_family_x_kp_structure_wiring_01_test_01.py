# ============================================================
# er019_family_x_kp_structure_wiring_01_test_01.py
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W4)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe -m unittest \
#       er019_family_x_kp_structure_wiring_01_test_01 -v
#
# API呼び出し: 0(実LLM/TTS呼び出しは全てmock)。費用¥0。
#
# 対象: Key Phrase 音声構造(Standard/Advanced共通骨格、CURRENT_SPEC.md
# 「Key Phrase 音声構造」節、2026-09-29ユーザー正式決定)のProduction配線。
#   (a) Advanced(b1b)Key Phrase英語解説のtext仕様(Prompt/schema/語数上限)
#       がKEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02(er041)の逐語
#       転記であることのsha256照合
#   (b) 音声Style(Variant B)がKEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-
#       AUDIO-STYLE-TRIAL-04(er046)の逐語転記であることの照合
#   (c) text生成のQA validator(語数上限・新規Fact混入)とNG時の技術retry
#       (1回)
#   (d) Advanced(b1b)Key Phrase組立が[english, explanation, phrase_repeat
#       (=先頭と同一wav)]になり、旧"japanese"roleが存在しないこと
#   (e) 末尾Phrase再掲が先頭と同一path/同一sha256(fallback経路でも同様)
#   (f) TTS呼び出し回数(English Phraseはrankごとに1回のみ、再掲は追加
#       TTS callが0であること)
#   (g) cache hit/miss(_generate_or_reuse_kpの既存reuse機構、role
#       "explanation"でも同様に機能すること)
#   (h) player行(_row_info_family_x)がAdvancedで解説textを表示し、
#       audioの1件目・3件目が同一pathであること。Standard(a2)側は無変更
# ============================================================
from __future__ import annotations

import hashlib
import json
import unittest
from unittest import mock

import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_kp_explanation_01 as kp_explanation_gen
import er033_tts_flash_lite_family_x_styles_01 as fl_styles
import er041_key_phrase_advanced_english_explanation_trial_02 as trial02_text
import er046_key_phrase_advanced_english_explanation_audio_style_trial_04 as trial04_audio


# ============================================================
# (a)(b) Prompt/Style逐語性のsha256照合
# ============================================================
class PromptAndStyleFidelityTests(unittest.TestCase):
    def test_max_words_matches_trial_02(self):
        self.assertEqual(kp_explanation_gen.MAX_WORDS, trial02_text.MAX_WORDS)

    def test_explanation_spec_sentence_matches_trial_02(self):
        self.assertEqual(kp_explanation_gen.EXPLANATION_EN_SPEC_SENTENCE,
                          trial02_text.EXPLANATION_EN_SPEC_SENTENCE)
        self.assertIn(kp_explanation_gen.EXPLANATION_EN_SPEC_SENTENCE,
                      trial02_text.prior_trial.ADVANCED_USER_TEMPLATE)

    def test_developer_message_matches_trial_02(self):
        self.assertEqual(kp_explanation_gen.DEVELOPER_MESSAGE, trial02_text.DEVELOPER_MESSAGE)

    def test_user_template_header_matches_trial_02(self):
        self.assertEqual(kp_explanation_gen.USER_TEMPLATE_HEADER, trial02_text.USER_TEMPLATE_HEADER)

    def test_user_template_footer_matches_trial_02(self):
        self.assertEqual(kp_explanation_gen.USER_TEMPLATE_FOOTER, trial02_text.USER_TEMPLATE_FOOTER)

    def test_json_schema_matches_trial_02(self):
        self.assertEqual(kp_explanation_gen.EXPLANATION_JSON_SCHEMA, trial02_text.EXPLANATION_JSON_SCHEMA)

    def test_prompt_sha256_reproducible_from_trial_02_constants(self):
        """Prompt逐語性の機械的証拠: er041の同一定数から独立に算出した
        ハッシュが、Production module(kp_explanation_gen)のPROMPT_SHA256
        と一致すること。"""
        text_for_hash = "␟".join(
            [trial02_text.DEVELOPER_MESSAGE, trial02_text.USER_TEMPLATE_HEADER,
             trial02_text.USER_TEMPLATE_FOOTER, json.dumps(trial02_text.EXPLANATION_JSON_SCHEMA, sort_keys=True)])
        expected = hashlib.sha256(text_for_hash.encode("utf-8")).hexdigest()
        self.assertEqual(kp_explanation_gen.PROMPT_SHA256, expected)

    def test_model_matches_trial_02(self):
        self.assertEqual(kp_explanation_gen.MODEL, trial02_text.MODEL)

    def test_variant_b_style_matches_trial_04(self):
        self.assertEqual(fl_styles.KEY_PHRASE_EXPLANATION_EN, trial04_audio.VARIANT_STYLES["B"])
        self.assertEqual(fl_styles.KEY_PHRASE_EXPLANATION_EN,
                          "clear, precise, at a measured pace, without dragging")

    def test_model_routing_process_registered(self):
        import er006_model_routing_contract_01 as routing
        self.assertEqual(routing.PROCESS_MODEL_MAP[kp_explanation_gen.MODEL_ROUTING_PROCESS],
                          kp_explanation_gen.MODEL)


# ============================================================
# (c) text生成: QA validator + 技術retry(1回)
# ============================================================
_ITEMS = [
    {"rank": 1, "display_phrase": "raise privacy concerns", "source_sentence": "The plan may raise privacy concerns.",
     "japanese_gloss": "プライバシーへの懸念を引き起こす"},
    {"rank": 2, "display_phrase": "roll out", "source_sentence": "The company will roll out the new service.",
     "japanese_gloss": "展開する"},
]


def _good_call_fn(explanations_by_phrase):
    def call_fn(user_message):
        parsed = {"explanations": [{"phrase": p, "english_explanation": e}
                                    for p, e in explanations_by_phrase.items()]}
        return parsed, kp_explanation_gen.MODEL, {"input_tokens": 100, "output_tokens": 20}, "resp_1"

    return call_fn


class ValidateExplanationQaTests(unittest.TestCase):
    def test_within_max_words_passes(self):
        qa = kp_explanation_gen.validate_explanation_qa(
            "to make people worried", "raise concerns", "This may raise concerns among users.")
        self.assertTrue(qa["passed"])
        self.assertTrue(qa["within_max_words"])
        self.assertEqual(qa["new_fact_tokens"], [])

    def test_too_many_words_fails(self):
        long_explanation = " ".join(["word"] * (kp_explanation_gen.MAX_WORDS + 1))
        qa = kp_explanation_gen.validate_explanation_qa(long_explanation, "phrase", "some source sentence")
        self.assertFalse(qa["passed"])
        self.assertFalse(qa["within_max_words"])

    def test_new_fact_capitalized_token_detected(self):
        qa = kp_explanation_gen.validate_explanation_qa(
            "to move to Tokyo suddenly", "relocate", "They decided to relocate for work.")
        self.assertFalse(qa["passed"])
        self.assertIn("Tokyo", qa["new_fact_tokens"])

    def test_new_fact_number_token_detected(self):
        qa = kp_explanation_gen.validate_explanation_qa(
            "to grow by 50 percent", "increase", "Sales began to increase this year.")
        self.assertFalse(qa["passed"])
        self.assertTrue(any(tok.isdigit() for tok in qa["new_fact_tokens"]))


class GenerateKpExplanationsTests(unittest.TestCase):
    def test_success_first_attempt_no_retry(self):
        call_fn = _good_call_fn({
            "raise privacy concerns": "to make people worried about their personal data",
            "roll out": "to start offering something new to everyone",
        })
        result = kp_explanation_gen.generate_kp_explanations(_ITEMS, call_fn=call_fn)
        self.assertFalse(result["audit"]["retried_for_parse"])
        self.assertFalse(result["audit"]["retried_for_qa"])
        self.assertEqual(result["items"][1]["status"], "OK")
        self.assertEqual(result["items"][2]["status"], "OK")
        self.assertEqual(result["audit"]["prompt_sha256"], kp_explanation_gen.PROMPT_SHA256)

    def test_retries_once_on_parse_failure_then_succeeds(self):
        calls = {"n": 0}

        def call_fn(user_message):
            calls["n"] += 1
            if calls["n"] == 1:
                return None, kp_explanation_gen.MODEL, {"input_tokens": 10, "output_tokens": 0}, "resp_bad"
            return ({"explanations": [
                        {"phrase": "raise privacy concerns", "english_explanation": "to make people worried"},
                        {"phrase": "roll out", "english_explanation": "to start offering something new"}]},
                    kp_explanation_gen.MODEL, {"input_tokens": 10, "output_tokens": 20}, "resp_ok")

        result = kp_explanation_gen.generate_kp_explanations(_ITEMS, call_fn=call_fn)
        self.assertEqual(calls["n"], 2)
        self.assertTrue(result["audit"]["retried_for_parse"])
        self.assertEqual(result["items"][1]["status"], "OK")

    def test_raises_after_parse_retry_exhausted(self):
        def call_fn(user_message):
            return None, kp_explanation_gen.MODEL, {"input_tokens": 10, "output_tokens": 0}, "resp_bad"

        with self.assertRaises(kp_explanation_gen.ExplanationGenerationError):
            kp_explanation_gen.generate_kp_explanations(_ITEMS, call_fn=call_fn)

    def test_retries_once_on_qa_ng_then_accepts_retry_result(self):
        calls = {"n": 0}
        too_long = " ".join(["word"] * (kp_explanation_gen.MAX_WORDS + 5))

        def call_fn(user_message):
            calls["n"] += 1
            if calls["n"] == 1:
                explanations = {"raise privacy concerns": too_long, "roll out": "to start offering something new"}
            else:
                explanations = {"raise privacy concerns": "to make people worried about their data",
                                 "roll out": "to start offering something new"}
            parsed = {"explanations": [{"phrase": p, "english_explanation": e} for p, e in explanations.items()]}
            return parsed, kp_explanation_gen.MODEL, {"input_tokens": 10, "output_tokens": 20}, f"resp_{calls['n']}"

        result = kp_explanation_gen.generate_kp_explanations(_ITEMS, call_fn=call_fn)
        self.assertEqual(calls["n"], 2)
        self.assertTrue(result["audit"]["retried_for_qa"])
        self.assertEqual(result["items"][1]["status"], "OK")

    def test_does_not_double_retry_when_parse_retry_already_used(self):
        """技術retry上限(合計1回)の遵守: parse失敗で既にretryを1回使って
        いる場合、その後にQA NGが出てもさらに追加retryはしない。"""
        calls = {"n": 0}
        too_long = " ".join(["word"] * (kp_explanation_gen.MAX_WORDS + 5))

        def call_fn(user_message):
            calls["n"] += 1
            if calls["n"] == 1:
                return None, kp_explanation_gen.MODEL, {"input_tokens": 10, "output_tokens": 0}, "resp_bad"
            explanations = {"raise privacy concerns": too_long, "roll out": "to start offering something new"}
            parsed = {"explanations": [{"phrase": p, "english_explanation": e} for p, e in explanations.items()]}
            return parsed, kp_explanation_gen.MODEL, {"input_tokens": 10, "output_tokens": 20}, "resp_2"

        result = kp_explanation_gen.generate_kp_explanations(_ITEMS, call_fn=call_fn)
        self.assertEqual(calls["n"], 2)
        self.assertTrue(result["audit"]["retried_for_parse"])
        self.assertFalse(result["audit"]["retried_for_qa"])
        self.assertEqual(result["items"][1]["status"], "NG")

    def test_model_contract_violation_raises_without_fallback(self):
        def call_fn(user_message):
            return ({"explanations": []}, "some-other-model", {"input_tokens": 1, "output_tokens": 1}, "resp_x")

        with self.assertRaises(kp_explanation_gen.ExplanationGenerationError):
            kp_explanation_gen.generate_kp_explanations(_ITEMS, call_fn=call_fn)


# ============================================================
# (d)(e)(f)(g) Advanced(b1b)Key Phrase組立の配線
# ============================================================
def _fake_en_result(rank):
    return {"status": "OK", "path": f"narration/kp{rank}_en.wav", "sha256": f"sha_en_{rank}",
            "canonical_text": f"phrase {rank}"}


class B1bKeyPhraseAssemblyWiringTests(unittest.TestCase):
    def setUp(self):
        self.kp = {"items": [
            {"rank": 1, "used_form": "raise privacy concerns", "japanese_gloss": "懸念",
             "display_phrase": "raise privacy concerns", "source_sentence": "The plan may raise privacy concerns."},
            {"rank": 2, "used_form": "roll out", "japanese_gloss": "展開する",
             "display_phrase": "roll out", "source_sentence": "The company will roll out the new service."},
        ]}
        self.explanation_bundle = {
            "items": {
                1: {"english_explanation": "to make people worried about their data",
                    "qa": {"passed": True}, "status": "OK"},
                2: {"english_explanation": "to start offering something new",
                    "qa": {"passed": True}, "status": "OK"},
            },
            "audit": {"model": kp_explanation_gen.MODEL, "prompt_sha256": kp_explanation_gen.PROMPT_SHA256},
        }

    def test_no_japanese_role_in_b1b_kp_results(self):
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=self.explanation_bundle), \
             mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=lambda *_a, **_kw: _fake_en_result(1)), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified",
                                return_value={"status": "OK", "path": "narration/kp_expl.wav",
                                              "sha256": "sha_expl"}):
            kp_results, bundle = runner._generate_key_phrase_segments_b1(self.kp, "narration")
        for rank, row in kp_results.items():
            self.assertIn("english", row)
            self.assertIn("explanation", row)
            self.assertIn("phrase_repeat", row)
            self.assertNotIn("japanese", row)

    def test_phrase_repeat_is_same_path_and_sha256_as_first(self):
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=self.explanation_bundle), \
             mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=lambda *_a, **_kw: _fake_en_result(1)), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified",
                                return_value={"status": "OK", "path": "narration/kp_expl.wav",
                                              "sha256": "sha_expl"}):
            kp_results, _ = runner._generate_key_phrase_segments_b1(self.kp, "narration")
        for rank, row in kp_results.items():
            self.assertEqual(row["phrase_repeat"]["path"], row["english"]["path"])
            self.assertEqual(row["phrase_repeat"]["sha256"], row["english"]["sha256"])
            self.assertEqual(row["phrase_repeat"]["phrase_repeat_source"], "same_as_first")

    def test_phrase_repeat_identical_even_when_explanation_stopped(self):
        """英語解説のTTSがSTOPPEDでも、先頭Phraseとその再掲(phrase_repeat)
        の同一性(付帯条件)は影響を受けない。"""
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=self.explanation_bundle), \
             mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=lambda *_a, **_kw: _fake_en_result(1)), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified",
                                return_value={"status": "STOPPED", "reason": "forced_for_test"}):
            kp_results, _ = runner._generate_key_phrase_segments_b1(self.kp, "narration")
        for rank, row in kp_results.items():
            self.assertEqual(row["phrase_repeat"]["path"], row["english"]["path"])
            self.assertEqual(row["explanation"]["status"], "STOPPED")

    def test_phrase_repeat_identical_when_english_used_fallback_path(self):
        """先頭Phrase自体がfallback(English lock等)経路で生成された場合
        でも、再掲(phrase_repeat)は単純にen_rの複製であるため、fallback
        由来のresultであっても先頭=末尾の同一性は保たれる。"""
        fallback_en_result = {"status": "OK", "path": "narration/kp1_en.wav", "sha256": "sha_en_fallback",
                               "fallback_used": True, "canonical_text": "raise privacy concerns"}
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=self.explanation_bundle), \
             mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=lambda *_a, **_kw: dict(fallback_en_result)), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified",
                                return_value={"status": "OK", "path": "narration/kp_expl.wav",
                                              "sha256": "sha_expl"}):
            kp_results, _ = runner._generate_key_phrase_segments_b1(self.kp, "narration")
        row = kp_results[1]
        self.assertEqual(row["phrase_repeat"]["path"], row["english"]["path"])
        self.assertEqual(row["phrase_repeat"]["fallback_used"], True)

    def test_explanation_uses_variant_b_style(self):
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=self.explanation_bundle), \
             mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=lambda *_a, **_kw: _fake_en_result(1)), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified",
                                return_value={"status": "OK", "path": "x", "sha256": "y"}) as expl_mock:
            runner._generate_key_phrase_segments_b1(self.kp, "narration")
        for call in expl_mock.call_args_list:
            self.assertEqual(call.kwargs.get("style_prefix_override"), fl_styles.KEY_PHRASE_EXPLANATION_EN)

    def test_english_phrase_tts_called_exactly_once_per_rank(self):
        """量産コスト(B): Phrase再掲のために追加TTS callは発生しない
        (Englishはrankごとに1回のみ生成される)。"""
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=self.explanation_bundle), \
             mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=lambda *_a, **_kw: _fake_en_result(1)) as en_mock, \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified",
                                return_value={"status": "OK", "path": "x", "sha256": "y"}) as expl_mock:
            runner._generate_key_phrase_segments_b1(self.kp, "narration")
        self.assertEqual(en_mock.call_count, len(self.kp["items"]))
        self.assertEqual(expl_mock.call_count, len(self.kp["items"]))

    def test_text_generation_called_once_for_all_ranks_not_per_rank(self):
        """5件(本testは2件)まとめて1 callで解説生成する(rank毎に別callは
        しない)。"""
        gen_mock = mock.Mock(return_value=self.explanation_bundle)
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations", gen_mock), \
             mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=lambda *_a, **_kw: _fake_en_result(1)), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified",
                                return_value={"status": "OK", "path": "x", "sha256": "y"}):
            runner._generate_key_phrase_segments_b1(self.kp, "narration")
        self.assertEqual(gen_mock.call_count, 1)


class TextCacheReuseTests(unittest.TestCase):
    """_resolve_kp_explanations_text: run単位のtext cache reuse。"""

    def setUp(self):
        self.kp_items = [
            {"rank": 1, "display_phrase": "raise privacy concerns", "source_sentence": "s1",
             "japanese_gloss": "g1"},
            {"rank": 2, "display_phrase": "roll out", "source_sentence": "s2", "japanese_gloss": "g2"},
        ]

    def test_reuses_when_phrase_signature_unchanged(self):
        cached = {"key_phrase_explanations_text": {
            "phrases_signature": ["raise privacy concerns", "roll out"],
            "items": {1: {"english_explanation": "x", "status": "OK"}},
            "audit": {}}}
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations") as gen_mock:
            result = runner._resolve_kp_explanations_text(self.kp_items, cached)
        gen_mock.assert_not_called()
        self.assertTrue(result["reused_from_previous_run"])

    def test_regenerates_when_phrase_signature_changed(self):
        cached = {"key_phrase_explanations_text": {
            "phrases_signature": ["a different phrase", "roll out"],
            "items": {}, "audit": {}}}
        fresh = {"items": {1: {"english_explanation": "x", "status": "OK"},
                           2: {"english_explanation": "y", "status": "OK"}}, "audit": {}}
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=fresh) as gen_mock:
            result = runner._resolve_kp_explanations_text(self.kp_items, cached)
        gen_mock.assert_called_once()
        self.assertFalse(result["reused_from_previous_run"])

    def test_regenerates_when_no_cache(self):
        fresh = {"items": {1: {"english_explanation": "x", "status": "OK"},
                           2: {"english_explanation": "y", "status": "OK"}}, "audit": {}}
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=fresh) as gen_mock:
            result = runner._resolve_kp_explanations_text(self.kp_items, None)
        gen_mock.assert_called_once()
        self.assertFalse(result["reused_from_previous_run"])


class GenerateOrReuseKpRoleExplanationTests(unittest.TestCase):
    """既存の_generate_or_reuse_kp(rank/role単位cache)がrole="explanation"
    でも既存の"english"/旧"japanese"と同じcache hit/miss挙動をすること。"""

    def test_cache_hit_skips_generation(self):
        cached = {"key_phrases": {"1": {"explanation": {"status": "OK", "path": "kp1_explanation_en.wav"}}}}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK"}

        with mock.patch.object(runner.os.path, "exists", return_value=True):
            result = runner._generate_or_reuse_kp(cached, 1, "explanation", "kp1_explanation_en.wav", gen)
        self.assertEqual(calls["n"], 0)
        self.assertTrue(result.get("reused_from_previous_run"))

    def test_cache_miss_calls_generation(self):
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK"}

        result = runner._generate_or_reuse_kp(None, 1, "explanation", "kp1_explanation_en.wav", gen)
        self.assertEqual(calls["n"], 1)
        self.assertNotIn("reused_from_previous_run", result)

    def test_cache_present_but_file_missing_regenerates(self):
        cached = {"key_phrases": {"1": {"explanation": {"status": "OK", "path": "kp1_explanation_en.wav"}}}}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK"}

        with mock.patch.object(runner.os.path, "exists", return_value=False):
            runner._generate_or_reuse_kp(cached, 1, "explanation", "kp1_explanation_en.wav", gen)
        self.assertEqual(calls["n"], 1)


# ============================================================
# (h) player行(_row_info_family_x)
# ============================================================
class PlayerRowInfoTests(unittest.TestCase):
    def setUp(self):
        self.kp_by_rank = {1: {"used_form": "raise privacy concerns", "japanese_gloss": "懸念"}}

    def test_b1b_key_phrase_row_repeats_same_audio_path(self):
        kp_expl = {1: {"explanation": "to make people worried about their data"}}
        info = runner._row_info_family_x(
            "Key Phrase 1", "b1b", {}, {}, "narration", self.kp_by_rank, None,
            kp_explanations_by_rank=kp_expl)
        self.assertEqual(len(info["audio"]), 3)
        self.assertEqual(info["audio"][0], info["audio"][2])
        self.assertIn("EXPLANATION", info["text"])
        self.assertIn("to make people worried about their data", info["text"])

    def test_a2_key_phrase_row_unchanged_two_file_structure(self):
        info = runner._row_info_family_x(
            "Key Phrase 1", "a2", {}, {}, "narration", self.kp_by_rank, None)
        self.assertEqual(len(info["audio"]), 2)
        self.assertIn("JA:", info["text"])
        self.assertTrue(info["audio"][1].endswith("meaning_1.wav"))


if __name__ == "__main__":
    unittest.main()
