# ============================================================
# er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01
# ============================================================
# Gate 3/4向け単体テスト(API呼び出し無し、¥0)。EDITORIAL-B-FAMILY-
# PRODUCTION-PATH-PHASE1-WIRING-01の既存
# er012_editorial_b_family_production_phase1_test_01.py(2V)と同型の
# パターンで、3V(3声Voice構成)配線の契約を検証する。
#   1. registry.build_required_structure()拡張の契約テスト
#      (voice_c省略時は既存2V出力とbyte一致、voice_c指定時は3V16segment)。
#   2. B_FAMILY_B1_3V_REQUIRED_SEGMENTSの内容検査(16 segment・
#      point_one/two/three命名がTrial側build_required_structure_3v()の
#      出力と一致すること)。
#   3. VOICE_ASSIGNMENT["voice_c"]=Schedar、VOICE_FALLBACKにvoice_cキーが
#      無いこと(専用fallback声を持たない2026-09-10決定の固定)。
#   4. Comment 2/3のVoice数非依存汎用化(役割マーカーは維持、count固有の
#      具体的言い回しは除去されていること)。
#   5. split_six_voice_sections()/build_parts_3v()の構造parserテスト。
#   6. resolve_voice_names_3v()(Voice A/Bは既存fallback再利用、Voice Cは
#      専用fallback無し、修正指示2回目以降: 解決後3声が相互に異なることを
#      検証し衝突時はRuntimeError["VOICE_COLLISION_STOP"]で明示STOP)。
#  12. run_content_integrity_check_3v()(Trialから正式移設したpure関数)の
#      入出力固定、およびrun_scaffold_3v()がこれを呼びNG時にRuntimeError
#      ["CONTENT_INTEGRITY_STOP"]で明示停止すること(修正指示2回目)。
#   7. build_b1_voices_timeline_3v()の契約テスト(既存build_b1_timeline()を
#      呼ばない、共有Key Phrase block builderを使う、Voice 1/2/3 bodyを
#      含む)。
#   8. run_tts_3v()の安全機構(OPEN-121/OPE-122)契約テスト(mock、実API
#      呼び出しなし)。
#   9. DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVELの"B1"キー拡張が既存
#      A-Family/2V B-Family判定(既存segment名)へ影響しないこと。
#  10. runner main()のlevel="b1_3v"分岐契約テスト。
#  11. Trial専用実装(er012_editorial_b_voices_3v_audio_trial_01)を
#      Production module(registry/production_01/production_runner_01)が
#      モジュールレベルでimportしていないこと(STOP条件(d)の裏付け)。
#  13. Phase 1b: Ledger Deviation Check(既存2V run_scaffold()と同一の
#      vfl01.run_deviation_check、monitoring専用)を3Vへ接続したこと、
#      Tension segment語数のrecord-only観測ログ(compute_tension_segment_
#      word_count_3v、新QA基準ではない)を記録すること。
from __future__ import annotations

import unittest
from unittest import mock

import er003_v1_n3_01_assemble as asm
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_production_runner_01 as runner
import er012_b_family_voices_production_01 as b1prod

ARTICLE_SIX_SECTIONS = """# Title Here

## Heading One

Sentence one. Sentence two.

### Voice 1 Heading

Voice 1 body text here.

### Voice 2 Heading

Voice 2 body text here.

### Voice 3 Heading

Voice 3 body text here.

## Tension Heading

Tension body text here.

## Closing Heading

Closing body text here.
"""

ARTICLE_WRONG_SECTION_COUNT_FOR_3V = """# Title Here

## Heading One

Sentence one. Sentence two.

### Voice A Heading

Voice A body text here.

### Voice B Heading

Voice B body text here.

## Tension Heading

Tension body text here.

## Closing Heading

Closing body text here.
"""


class RegistryVoiceCArgumentBackwardCompatibilityTests(unittest.TestCase):
    """voice_c省略時、build_required_structure()の出力が既存2V(修正前)と
    byte単位で同一であることを固定する(Gate 3 item1「既存2V経路は
    無変更」の裏付け)。"""

    _EXPECTED_2V_B1_SEGMENTS = (
        ("topic_intro", "Charon"), ("preview", "Charon"),
        ("comment_1", "Charon"), ("comment_2", "Charon"),
        ("comment_3", "Charon"), ("comment_4", "Charon"),
        ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
        ("point_one", "Algieba"), ("point_two", "Erinome"),
        ("full_story_part1", None), ("full_story_part2", None),
        ("tension_reflection", None), ("in_one_line", None),
    )

    def test_voice_c_omitted_matches_pre_existing_2v_b1_output(self):
        result = registry.build_required_structure("b1", "Algieba", "Erinome")
        self.assertEqual(result["segments"], self._EXPECTED_2V_B1_SEGMENTS)
        self.assertEqual(result["key_phrase_ranks"], 5)
        self.assertEqual(result["key_phrase_subkey_count"], 2)

    def test_voice_c_explicit_none_is_identical_to_omitted(self):
        with_none = registry.build_required_structure("b1", "Algieba", "Erinome", voice_c=None)
        omitted = registry.build_required_structure("b1", "Algieba", "Erinome")
        self.assertEqual(with_none, omitted)

    def test_a2_level_unaffected_by_voice_c_extension(self):
        # a2側にvoice_c指定時の3V分岐は無い(3VはB1のみ対応)。voice_c省略時の
        # 既存a2出力が変わっていないことを確認する。
        result = registry.build_required_structure("a2", "Algieba", "Erinome")
        self.assertEqual(len(result["segments"]), 15)
        names = [n for n, _ in result["segments"]]
        self.assertNotIn("point_three", names)
        self.assertNotIn("point_three_heading", names)


class RegistryVoiceCArgument3VStructureTests(unittest.TestCase):
    """voice_c指定時、3V required_structure(16 segment、point_one/two/
    three命名)がTrial側build_required_structure_3v()の出力と一致すること
    (2重定義解消、registry側が正本)。"""

    _EXPECTED_3V_B1_SEGMENTS = (
        ("topic_intro", "Charon"), ("preview", "Charon"),
        ("comment_1", "Charon"), ("comment_2", "Charon"),
        ("comment_3", "Charon"), ("comment_4", "Charon"),
        ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
        ("point_three_heading", "Aoede"),
        ("point_one", "Algieba"), ("point_two", "Erinome"), ("point_three", "Schedar"),
        ("full_story_part1", None), ("full_story_part2", None),
        ("tension_reflection", None), ("in_one_line", None),
    )

    def test_voice_c_specified_returns_16_segments_in_expected_order(self):
        result = registry.build_required_structure("b1", "Algieba", "Erinome", voice_c="Schedar")
        self.assertEqual(result["segments"], self._EXPECTED_3V_B1_SEGMENTS)
        self.assertEqual(len(result["segments"]), 16)

    def test_matches_registry_b_family_b1_3v_required_segments_constant(self):
        role_names = tuple((name, role) for name, role in registry.B_FAMILY_B1_3V_REQUIRED_SEGMENTS)
        expected_role_names = (
            ("topic_intro", "narrator_charon"), ("preview", "narrator_charon"),
            ("comment_1", "narrator_charon"), ("comment_2", "narrator_charon"),
            ("comment_3", "narrator_charon"), ("comment_4", "narrator_charon"),
            ("point_one_heading", "narrator_aoede_en"), ("point_two_heading", "narrator_aoede_en"),
            ("point_three_heading", "narrator_aoede_en"),
            ("point_one", "voice_a"), ("point_two", "voice_b"), ("point_three", "voice_c"),
            ("full_story_part1", None), ("full_story_part2", None),
            (registry.EXTRA_SEGMENT_NAME, None), ("in_one_line", None),
        )
        self.assertEqual(role_names, expected_role_names)

    def test_b1_3v_config_registered_under_editorial_type(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("b1_3v", editorial_type)
        b1_3v_config = registry.get_editorial_type_b1_3v()
        self.assertIs(b1_3v_config, editorial_type["b1_3v"])
        self.assertEqual(b1_3v_config["key_phrase_ranks"], 5)
        self.assertEqual(b1_3v_config["key_phrase_subkey_count"], 2)


class BuildRequiredStructureB13vAliasAndA2VoiceCGuardTests(unittest.TestCase):
    """修正指示2回目(Fable、Opus L2レビュー指摘#3): runner CLIのlevel=
    "b1_3v"文字列を薄いaliasとして正式受理すること、level="a2"へvoice_cを
    渡した場合に従来の黙殺からValueErrorへ変わったことを固定する。"""

    def test_level_b1_3v_alias_matches_level_b1_plus_voice_c(self):
        via_alias = registry.build_required_structure("b1_3v", "Algieba", "Erinome", voice_c="Schedar")
        via_explicit = registry.build_required_structure("b1", "Algieba", "Erinome", voice_c="Schedar")
        self.assertEqual(via_alias, via_explicit)

    def test_level_b1_3v_without_voice_c_raises_value_error(self):
        with self.assertRaises(ValueError):
            registry.build_required_structure("b1_3v", "Algieba", "Erinome")

    def test_level_a2_with_voice_c_now_raises_value_error_instead_of_silently_ignoring(self):
        with self.assertRaises(ValueError):
            registry.build_required_structure("a2", "Algieba", "Erinome", voice_c="Schedar")

    def test_level_a2_without_voice_c_still_works(self):
        result = registry.build_required_structure("a2", "Algieba", "Erinome")
        self.assertEqual(len(result["segments"]), 15)


class VoiceCAssignmentAndNoFallbackTests(unittest.TestCase):
    """2026-09-10ユーザー決定: Voice 3=Schedar本採用、専用fallback声なし。"""

    def test_voice_c_is_schedar(self):
        self.assertEqual(registry.VOICE_ASSIGNMENT["voice_c"], "Schedar")

    def test_voice_fallback_has_no_dedicated_voice_c_entry(self):
        self.assertNotIn("voice_c", registry.VOICE_FALLBACK)

    def test_voice_a_b_assignment_and_fallback_unchanged(self):
        self.assertEqual(registry.VOICE_ASSIGNMENT["voice_a"], "Algieba")
        self.assertEqual(registry.VOICE_ASSIGNMENT["voice_b"], "Erinome")
        self.assertEqual(registry.VOICE_FALLBACK["voice_a"], "Schedar")
        self.assertEqual(registry.VOICE_FALLBACK["voice_b"], "Sulafat")


class CommentTwoThreeVoiceCountIndependentGeneralizationTests(unittest.TestCase):
    """Comment 2/3のVoice数非依存汎用化(2026-09-10ユーザー決定)。役割
    マーカー(意味)は維持したまま、count固有の具体的言い回し
    (「One Voice/Another Voice」「2つの声」「どちらか一方」等)を除去した
    ことを固定する。Comment 1/4は本タスクで一切変更していないことも
    合わせて確認する(既存test_comment_1_bans_the_question_phrase等と
    重複しない範囲での追加確認)。"""

    def test_comment_2_role_markers_preserved(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("Hookの問いから「ここから異なるVoiceを聞く」への橋渡し",
                      editorial_type["comment_roles"]["comment_2"])

    def test_comment_3_role_markers_preserved(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("なぜ違って感じるのか", editorial_type["comment_roles"]["comment_3"])

    def test_comment_2_no_longer_hardcodes_one_voice_another_voice_count(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        c2 = editorial_type["comment_roles"]["comment_2"]
        self.assertNotIn("One Voiceの後、続けてAnother Voice", c2)
        self.assertNotIn("One Voice・Another Voiceの具体的な内容の先取り", c2)

    def test_comment_3_no_longer_hardcodes_exactly_two_voices(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        c3 = editorial_type["comment_roles"]["comment_3"]
        self.assertNotIn("One Voice・Another Voice", c3)
        self.assertNotIn("2つの声", c3)
        self.assertNotIn("どちらか一方の声", c3)

    def test_comment_1_and_4_unchanged_by_this_task(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("Listening Focus", editorial_type["comment_roles"]["comment_1"])
        self.assertIn("一段深い問い", editorial_type["comment_roles"]["comment_4"])


class SplitSixVoiceSectionsTests(unittest.TestCase):
    def test_valid_six_section_article_parses(self):
        sections = b1prod.split_six_voice_sections(ARTICLE_SIX_SECTIONS)
        self.assertIsNotNone(sections)
        self.assertEqual(sections["voice_1_heading"], "Voice 1 Heading")
        self.assertEqual(sections["voice_2_heading"], "Voice 2 Heading")
        self.assertEqual(sections["voice_3_heading"], "Voice 3 Heading")
        self.assertIn("Tension body text here.", sections["tension_body"])
        self.assertIn("Closing body text here.", sections["closing_body"])

    def test_five_section_article_returns_none(self):
        # 既存2V(5区切り)記事は3Vパーサーでは検出失敗(Noneを返す)。
        sections = b1prod.split_six_voice_sections(ARTICLE_WRONG_SECTION_COUNT_FOR_3V)
        self.assertIsNone(sections)

    def test_no_title_returns_none(self):
        self.assertIsNone(b1prod.split_six_voice_sections("## Heading only, no title\n\nBody.\n"))

    def test_existing_five_section_parser_unaffected(self):
        # split_five_voice_sections()(2V、既存)は本タスクで無変更のまま、
        # 6区切り記事は検出失敗することを確認する(相互非干渉の裏付け)。
        self.assertIsNone(b1prod.split_five_voice_sections(ARTICLE_SIX_SECTIONS))


class BuildParts3vTests(unittest.TestCase):
    def test_build_parts_3v_extracts_point_three_fields(self):
        parts = b1prod.build_parts_3v(ARTICLE_SIX_SECTIONS)
        self.assertEqual(parts["point_three_heading"], "Voice 3 Heading.")
        self.assertIn("Voice 3 body text here.", parts["point_three_body"])
        self.assertEqual(parts["point_one_heading"], "Voice 1 Heading.")
        self.assertEqual(parts["point_two_heading"], "Voice 2 Heading.")


class ResolveVoiceNames3vTests(unittest.TestCase):
    def test_all_three_voices_available(self):
        sample_results = {"Algieba": {"status": "OK"}, "Erinome": {"status": "OK"}, "Schedar": {"status": "OK"}}
        voice_a, voice_b, voice_c, reasons = b1prod.resolve_voice_names_3v(sample_results)
        self.assertEqual((voice_a, voice_b, voice_c), ("Algieba", "Erinome", "Schedar"))
        self.assertEqual(reasons, {})

    def test_voice_a_unavailable_causes_collision_with_voice_c_and_stops(self):
        # 修正指示2回目(Opus L2レビュー指摘#1・HIGH): registry.VOICE_FALLBACK
        # ["voice_a"]とregistry.VOICE_ASSIGNMENT["voice_c"]が同一("Schedar")
        # のため、Voice Aがfallbackした場合Voice A/Cが衝突する。旧仕様
        # (衝突を許容してどちらもSchedarのまま返す)ではなく、明示STOPへ
        # 期待値を変更した。
        sample_results = {"Algieba": {"status": "ERROR", "error": "technical failure"},
                           "Erinome": {"status": "OK"}, "Schedar": {"status": "OK"}}
        with self.assertRaises(RuntimeError) as ctx:
            b1prod.resolve_voice_names_3v(sample_results)
        self.assertIn("VOICE_COLLISION_STOP", str(ctx.exception))
        self.assertIn("voice_a", str(ctx.exception))
        self.assertIn("voice_c", str(ctx.exception))
        # Fable修正指示3回目(見落とし2): 呼び出し側(runner voice_check_3v())が
        # audit/voice_resolution.jsonへ解決済み値を記録できるよう、例外へ
        # resolved/voice_reasons属性が添付されていること。
        self.assertEqual(ctx.exception.resolved["voice_a"], "Schedar")
        self.assertEqual(ctx.exception.resolved["voice_c"], "Schedar")
        self.assertIsInstance(ctx.exception.voice_reasons, dict)

    def test_voice_c_unavailable_has_no_dedicated_fallback_and_stays_schedar(self):
        sample_results = {"Algieba": {"status": "OK"}, "Erinome": {"status": "OK"},
                           "Schedar": {"status": "ERROR", "error": "technical failure"}}
        voice_a, voice_b, voice_c, reasons = b1prod.resolve_voice_names_3v(sample_results)
        self.assertEqual(voice_c, "Schedar")  # 代替声を発明しない(既存Human Review Lockへ委ねる)
        self.assertIn("voice_c", reasons)
        self.assertIn("Human Review Lock", reasons["voice_c"])


class RunContentIntegrityCheck3vTests(unittest.TestCase):
    """修正指示2回目(Opus L2レビュー指摘#2・HIGH): Trial専用だった
    run_content_integrity_check()をProduction module(b1prod)へ正式移設した
    run_content_integrity_check_3v()の入出力固定テスト(pure関数、I/Oなし)。"""

    def _parts(self):
        return {
            "point_one_body": "Voice 1 body text here.",
            "point_two_body": "Voice 2 body text here.",
            "point_three_body": "Voice 3 body text here.",
            "tension_body": "Tension body text here.",
            "in_one_line": "Closing body text here.",
            "part1": "Hook sentence one.", "part2": "Hook sentence two.",
            "sections": {"hook_body": "Hook sentence one. Hook sentence two."},
        }

    def test_all_ok_when_all_bodies_verbatim_and_key_phrase_used_form_present(self):
        article_text = ("Hook sentence one. Hook sentence two. Voice 1 body text here. "
                         "Voice 2 body text here. Voice 3 body text here. "
                         "Tension body text here. Closing body text here. some-key-phrase")
        kp_merged = {"items": [{"used_form": "some-key-phrase"}]}
        result = b1prod.run_content_integrity_check_3v(article_text, self._parts(), kp_merged)
        self.assertTrue(result["all_section_bodies_verbatim_from_article"])
        self.assertTrue(result["key_phrase_used_form_appears_in_article"]["some-key-phrase"])
        self.assertIn("point_one_body", result["section_body_substring_checks"])
        self.assertIn("point_three_body", result["section_body_substring_checks"])

    def test_not_all_ok_when_a_body_is_missing_from_article(self):
        article_text = ("Hook sentence one. Hook sentence two. Voice 1 body text here. "
                         "Voice 2 body text here. [Voice 3 body MISSING] "
                         "Tension body text here. Closing body text here.")
        kp_merged = {"items": []}
        result = b1prod.run_content_integrity_check_3v(article_text, self._parts(), kp_merged)
        self.assertFalse(result["all_section_bodies_verbatim_from_article"])
        self.assertFalse(result["section_body_substring_checks"]["point_three_body"])

    def test_key_phrase_used_form_not_in_article_is_recorded_false(self):
        article_text = ("Hook sentence one. Hook sentence two. Voice 1 body text here. "
                         "Voice 2 body text here. Voice 3 body text here. "
                         "Tension body text here. Closing body text here.")
        kp_merged = {"items": [{"used_form": "absent-phrase"}]}
        result = b1prod.run_content_integrity_check_3v(article_text, self._parts(), kp_merged)
        self.assertFalse(result["key_phrase_used_form_appears_in_article"]["absent-phrase"])

    def test_matches_trial_function_output_for_same_input(self):
        # 移設元Trialの同名ロジック(er012_editorial_b_voices_3v_audio_trial_01.
        # run_content_integrity_check())と同一入力で同一出力になることを固定
        # する(正式移設であり、ロジック改変が無いことのevidence)。テストは
        # Trialをimportしてよい(Production module自体はimportしない、
        # NoTrialScriptModuleLevelImportTests参照)。
        import er012_editorial_b_voices_3v_audio_trial_01 as trial01
        article_text = ("Hook sentence one. Hook sentence two. Voice 1 body text here. "
                         "Voice 2 body text here. Voice 3 body text here. "
                         "Tension body text here. Closing body text here. some-key-phrase")
        parts = self._parts()
        kp_merged = {"items": [{"used_form": "some-key-phrase"}]}
        production_result = b1prod.run_content_integrity_check_3v(article_text, parts, kp_merged)
        with mock.patch.object(trial01, "save_json"):
            trial_result = trial01.run_content_integrity_check(article_text, parts, kp_merged)
        self.assertEqual(production_result, trial_result)


class ComputeTensionSegmentWordCount3vTests(unittest.TestCase):
    """EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-01: Tension
    segment語数のrecord-only観測ログ(新QA基準ではない、pass/fail判定を
    伴わない)。既存Production語数計算(ab01.compute_word_count)を
    再利用するだけであることを固定する(pure関数、API呼び出し無し)。"""

    def test_returns_word_count_matching_existing_ab01_compute_word_count(self):
        parts = {"tension_body": "This is a short tension segment with eight words."}
        result = b1prod.compute_tension_segment_word_count_3v(parts)
        self.assertEqual(result["tension_body_word_count"], b1prod.ab01.compute_word_count(parts["tension_body"]))

    def test_result_has_no_pass_fail_field(self):
        parts = {"tension_body": "Another tension body text."}
        result = b1prod.compute_tension_segment_word_count_3v(parts)
        for banned_key in ("status", "pass", "gate", "overall_status"):
            self.assertNotIn(banned_key, result)


class RunScaffold3vContentIntegrityWiringTests(unittest.TestCase):
    """修正指示2回目(Opus L2レビュー指摘#2): runner run_scaffold_3v()が
    b1prod.run_content_integrity_check_3v()を呼び、結果をaudit/
    content_integrity_3v.jsonへ保存すること、NG時はRuntimeError
    ["CONTENT_INTEGRITY_STOP"]で明示停止することを、実LLM/実ファイル
    I/Oなしで検証する。"""

    def _parts(self):
        return {
            "point_one_body": "V1 body.", "point_two_body": "V2 body.",
            "point_three_body": "V3 body.", "tension_body": "Tension body.",
            "in_one_line": "Closing.", "part1": "Hook one.", "part2": "Hook two.",
            "point_one_heading": "H1.", "point_two_heading": "H2.", "point_three_heading": "H3.",
            "sections": {"hook_body": "Hook one. Hook two."},
        }

    def _sections(self):
        return {"hook_body": "Hook one. Hook two.", "tension_heading": "Tension Heading",
                "closing_heading": "Closing Heading"}

    def _ok_support(self, *_a, **_kw):
        return {"status": "OK", "text": "generated text"}

    def test_calls_integrity_check_and_returns_result_when_ok(self):
        parts = self._parts()
        sections = self._sections()
        ok_result = {"all_section_bodies_verbatim_from_article": True,
                     "section_body_substring_checks": {}, "key_phrase_used_form_appears_in_article": {}}
        deviation_result = {"parsed": {"overall_status": "LEDGER_COMPLIANT"}}
        with mock.patch.object(runner.b1s, "get_client"), \
             mock.patch.object(runner.b1s, "run_support_text", side_effect=self._ok_support), \
             mock.patch.object(runner, "load_json", return_value={"items": []}), \
             mock.patch.object(runner, "save_json") as save_mock, \
             mock.patch.object(runner.b1prod, "run_content_integrity_check_3v",
                                return_value=ok_result) as integrity_mock, \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=deviation_result) as deviation_mock, \
             mock.patch("builtins.open", mock.mock_open()), \
             mock.patch.object(runner.os, "makedirs"):
            result = runner.run_scaffold_3v(parts, "Article full text.", sections, "Ledger text.")
        integrity_mock.assert_called_once()
        deviation_mock.assert_called_once()
        self.assertEqual(result["content_integrity"], ok_result)
        self.assertEqual(result["deviation"], deviation_result["parsed"])
        self.assertIn("tension_scale", result)
        integrity_save_calls = [c for c in save_mock.call_args_list
                                 if c.args[0].endswith("content_integrity_3v.json")]
        self.assertEqual(len(integrity_save_calls), 1)
        self.assertEqual(integrity_save_calls[0].args[1], ok_result)
        deviation_save_calls = [c for c in save_mock.call_args_list
                                 if c.args[0].endswith("support_ledger_deviation_3v.json")]
        self.assertEqual(len(deviation_save_calls), 1)
        tension_save_calls = [c for c in save_mock.call_args_list
                               if c.args[0].endswith("tension_scale_3v.json")]
        self.assertEqual(len(tension_save_calls), 1)

    def test_raises_runtime_error_when_integrity_check_fails(self):
        parts = self._parts()
        sections = self._sections()
        ng_result = {"all_section_bodies_verbatim_from_article": False,
                     "section_body_substring_checks": {"point_one_body": False},
                     "key_phrase_used_form_appears_in_article": {}}
        with mock.patch.object(runner.b1s, "get_client"), \
             mock.patch.object(runner.b1s, "run_support_text", side_effect=self._ok_support), \
             mock.patch.object(runner, "load_json", return_value={"items": []}), \
             mock.patch.object(runner, "save_json"), \
             mock.patch.object(runner.b1prod, "run_content_integrity_check_3v", return_value=ng_result), \
             mock.patch("builtins.open", mock.mock_open()), \
             mock.patch.object(runner.os, "makedirs"):
            with self.assertRaises(RuntimeError) as ctx:
                runner.run_scaffold_3v(parts, "Article full text.", sections, "Ledger text.")
        self.assertIn("CONTENT_INTEGRITY_STOP", str(ctx.exception))


class BuildB1VoicesTimeline3vContractTests(unittest.TestCase):
    """既存build_b1_voices_timeline()(2V、無変更)・既存asm.build_b1_timeline()
    (A-Family)いずれも呼ばないこと、共有Key Phrase block builderは呼ぶことを
    確認する契約テスト(実TTS/実Assembly実行はしない、モックのみ)。"""

    def _fake_parts(self):
        stereo = lambda: [[0.0, 0.0]] * 10  # noqa: E731
        b1 = {name: stereo() for name in (
            "preview", "comment_1", "comment_2", "comment_3", "comment_4",
            "full_story_part1", "full_story_part2",
            "point_one_heading", "point_one", "point_two_heading", "point_two",
            "point_three_heading", "point_three",
            "in_one_line", b1prod.EXTRA_SEGMENT_NAME)}
        return {
            "intro": stereo(), "welcome": stereo(), "topic_intro": stereo(), "notification": stereo(),
            "preview_intro": stereo(), "key_phrases_intro": stereo(), "full_story_intro": stereo(),
            "point_notification": stereo(), "outro": stereo(), "kp_items": [], "b1_segments": b1,
        }

    def test_does_not_call_existing_2v_or_a_family_timeline_builders(self):
        parts = self._fake_parts()
        with mock.patch.object(asm, "build_b1_timeline") as mocked_a_family_timeline, \
             mock.patch.object(b1prod, "build_b1_voices_timeline") as mocked_2v_timeline:
            seq = b1prod.build_b1_voices_timeline_3v(parts, "Algieba", "Erinome", "Schedar")
            mocked_a_family_timeline.assert_not_called()
            mocked_2v_timeline.assert_not_called()
        labels = [name for name, _ in seq]
        self.assertTrue(any(label.startswith("Tension:") for label in labels))
        self.assertTrue(any("Voice 1 body" in label for label in labels))
        self.assertTrue(any("Voice 2 body" in label for label in labels))
        self.assertTrue(any("Voice 3 body" in label for label in labels))

    def test_uses_shared_key_phrase_block_builder(self):
        parts = self._fake_parts()
        with mock.patch.object(asm, "build_b1_key_phrase_blocks", wraps=asm.build_b1_key_phrase_blocks) as spy:
            b1prod.build_b1_voices_timeline_3v(parts, "Algieba", "Erinome", "Schedar")
            spy.assert_called_once()


class RunTts3vBodySegmentSafetyFeatureContractTests(unittest.TestCase):
    """run_tts_3v()が、本文相当segment(Hook part1/2、Voice A/B/C=point_one/
    two/three)呼び出しではOPEN-121/OPEN-122フラグを有効化し、A-Familyでも
    対象外のsegment(Tension・Closing=in_one_line)には適用しない(2V
    Phase1との対称性維持)ことを、実TTS/実API呼び出しなしで検証する。"""

    def _fake_parts(self):
        return {
            "title": "Sample Title", "part1": "Hook sentence one.", "part2": "Hook sentence two.",
            "point_one_heading": "Voice 1 Heading.", "point_one_body": "Voice 1 body text.",
            "point_two_heading": "Voice 2 Heading.", "point_two_body": "Voice 2 body text.",
            "point_three_heading": "Voice 3 Heading.", "point_three_body": "Voice 3 body text.",
            "in_one_line": "Closing line text.", "tension_body": "Tension body text.",
        }

    def _fake_support_texts(self):
        return {"preview": "Preview text.", "comment_1": "C1.", "comment_2": "C2.",
                "comment_3": "C3.", "comment_4": "C4."}

    def _ok(self, *_a, **_kw):
        return {"status": "OK", "canonical_text": "x"}

    def test_body_segments_get_safety_features_enabled_and_non_body_segments_do_not(self):
        parts = self._fake_parts()
        support = self._fake_support_texts()
        with mock.patch.object(b1prod.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(b1prod.voice01, "generate_charon_english", side_effect=self._ok), \
             mock.patch.object(b1prod.point_headings, "generate", side_effect=self._ok), \
             mock.patch.object(b1prod, "generate_voice_body_wide_margin",
                                side_effect=self._ok) as voice_body_mock, \
             mock.patch.object(b1prod.news_tail_fix, "generate_news_narration_wide_margin",
                                side_effect=self._ok) as narration_mock:
            b1prod.run_tts_3v(parts, support, "Algieba", "Erinome", "Schedar", "out/narration")

        voice_body_calls = {c.args[2]: c.kwargs for c in voice_body_mock.call_args_list}
        for voice_name in ("Algieba", "Erinome", "Schedar"):
            kwargs = voice_body_calls[voice_name]
            self.assertTrue(kwargs["enable_connected_speech_equivalence_layer"], voice_name)
            self.assertTrue(kwargs["enable_repetition_qa"], voice_name)

        narration_calls = {call.args[1].rsplit("/", 1)[-1].replace(".wav", ""): call.kwargs
                           for call in narration_mock.call_args_list}
        for name in ("full_story_part1", "full_story_part2"):
            kwargs = narration_calls[name]
            self.assertTrue(kwargs["enable_connected_speech_equivalence_layer"], name)
            self.assertTrue(kwargs["enable_repetition_qa"], name)
        for name in (b1prod.EXTRA_SEGMENT_NAME, "in_one_line"):
            kwargs = narration_calls[name]
            self.assertFalse(kwargs["enable_connected_speech_equivalence_layer"], name)
            self.assertFalse(kwargs["enable_repetition_qa"], name)
        self.assertTrue(narration_calls["in_one_line"]["disfluency_qa"])
        self.assertFalse(narration_calls[b1prod.EXTRA_SEGMENT_NAME]["disfluency_qa"])

    def test_narrator_headings_include_point_three_heading(self):
        parts = self._fake_parts()
        support = self._fake_support_texts()
        with mock.patch.object(b1prod.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(b1prod.voice01, "generate_charon_english", side_effect=self._ok), \
             mock.patch.object(b1prod.point_headings, "generate", side_effect=self._ok) as heading_mock, \
             mock.patch.object(b1prod, "generate_voice_body_wide_margin", side_effect=self._ok), \
             mock.patch.object(b1prod.news_tail_fix, "generate_news_narration_wide_margin", side_effect=self._ok):
            results = b1prod.run_tts_3v(parts, support, "Algieba", "Erinome", "Schedar", "out/narration")
        heading_paths = [c.args[1] for c in heading_mock.call_args_list]
        self.assertTrue(any("point_three_heading.wav" in p for p in heading_paths))
        self.assertIn("point_three", results)
        self.assertIn("point_three_heading", results)


class RunTts3vBudgetCheckFnContractTests(unittest.TestCase):
    """Fable修正指示3回目(Opus L2レビュー指摘E): run_tts_3v()の新規
    `budget_check_fn`引数(既定None)が、2V run_tts()
    (er012_b_family_production_runner_01.py::assert_budget_ok)と同様に
    各segment群(topic_intro/preview・comment/heading/Voice1・2・3本文/
    Hook・Tension・Closing、計5群)の生成後に呼ばれること、および
    budget_check_fnが例外を送出した場合はそこで即座にSTOPし、以降の
    segment群を生成しないことを検証する(実API呼び出しなし)。"""

    def _fake_parts(self):
        return {
            "title": "Sample Title", "part1": "Hook sentence one.", "part2": "Hook sentence two.",
            "point_one_heading": "Voice 1 Heading.", "point_one_body": "Voice 1 body text.",
            "point_two_heading": "Voice 2 Heading.", "point_two_body": "Voice 2 body text.",
            "point_three_heading": "Voice 3 Heading.", "point_three_body": "Voice 3 body text.",
            "in_one_line": "Closing line text.", "tension_body": "Tension body text.",
        }

    def _fake_support_texts(self):
        return {"preview": "Preview text.", "comment_1": "C1.", "comment_2": "C2.",
                "comment_3": "C3.", "comment_4": "C4."}

    def _ok(self, *_a, **_kw):
        return {"status": "OK", "canonical_text": "x"}

    def test_default_none_does_not_call_anything(self):
        # budget_check_fn省略時(既定None)は現行挙動のまま無変更
        # (何も呼ばれない、既存呼び出し元との後方互換)。
        parts = self._fake_parts()
        support = self._fake_support_texts()
        with mock.patch.object(b1prod.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(b1prod.voice01, "generate_charon_english", side_effect=self._ok), \
             mock.patch.object(b1prod.point_headings, "generate", side_effect=self._ok), \
             mock.patch.object(b1prod, "generate_voice_body_wide_margin", side_effect=self._ok), \
             mock.patch.object(b1prod.news_tail_fix, "generate_news_narration_wide_margin", side_effect=self._ok):
            results = b1prod.run_tts_3v(parts, support, "Algieba", "Erinome", "Schedar", "out/narration")
        self.assertIn("in_one_line", results)

    def test_budget_check_fn_called_once_per_segment_group(self):
        parts = self._fake_parts()
        support = self._fake_support_texts()
        budget_mock = mock.Mock(return_value=0.0)
        with mock.patch.object(b1prod.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(b1prod.voice01, "generate_charon_english", side_effect=self._ok), \
             mock.patch.object(b1prod.point_headings, "generate", side_effect=self._ok), \
             mock.patch.object(b1prod, "generate_voice_body_wide_margin", side_effect=self._ok), \
             mock.patch.object(b1prod.news_tail_fix, "generate_news_narration_wide_margin", side_effect=self._ok):
            b1prod.run_tts_3v(parts, support, "Algieba", "Erinome", "Schedar", "out/narration",
                               budget_check_fn=budget_mock)
        # topic_intro / preview・comment / Narrator heading / Voice A・B・C / Hook・Tension・Closing = 5群。
        self.assertEqual(budget_mock.call_count, 5)
        notes = [c.args[0] for c in budget_mock.call_args_list]
        self.assertEqual(notes, [
            "after topic_intro TTS", "after preview/comment TTS", "after Narrator heading TTS",
            "after Voice A/B/C TTS", "after Hook/Tension/Closing TTS",
        ])

    def test_budget_check_fn_raise_stops_remaining_segment_groups(self):
        # budget超過を模したRuntimeErrorが1群目直後に送出された場合、
        # 独自判断でoverrideせずそのまま伝播し、以降のTTS呼び出しを
        # 行わないこと(既存安全装置[budget guard]を回避しない)。
        parts = self._fake_parts()
        support = self._fake_support_texts()
        budget_mock = mock.Mock(side_effect=RuntimeError("[BUDGET_GUARD] cost exceeded"))
        with mock.patch.object(b1prod.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(b1prod.voice01, "generate_charon_english", side_effect=self._ok) as charon_mock, \
             mock.patch.object(b1prod.point_headings, "generate", side_effect=self._ok) as heading_mock, \
             mock.patch.object(b1prod, "generate_voice_body_wide_margin", side_effect=self._ok) as voice_body_mock, \
             mock.patch.object(b1prod.news_tail_fix, "generate_news_narration_wide_margin",
                                side_effect=self._ok) as narration_mock:
            with self.assertRaises(RuntimeError) as ctx:
                b1prod.run_tts_3v(parts, support, "Algieba", "Erinome", "Schedar", "out/narration",
                                   budget_check_fn=budget_mock)
        self.assertIn("BUDGET_GUARD", str(ctx.exception))
        budget_mock.assert_called_once_with("after topic_intro TTS")
        # topic_intro(1回)のみ呼ばれ、preview/comment以降のTTSは一切呼ばれない。
        self.assertEqual(charon_mock.call_count, 1)
        heading_mock.assert_not_called()
        voice_body_mock.assert_not_called()
        narration_mock.assert_not_called()


class DisfluencyQaMandatoryDictB1NonRegressionTests(unittest.TestCase):
    """共有Gate辞書("B1"キー)への`point_three_heading`追加が、既存A-Family/
    2V B-Family判定(既存segment名)へ影響しないこと(1エントリ追加のみで
    あることの裏付け)。"""

    def test_existing_b1_entries_still_present(self):
        b1_entries = asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]
        for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4",
                     "in_one_line", "point_one_heading", "point_two_heading"):
            self.assertIn(name, b1_entries)

    def test_point_three_heading_added_to_b1_only(self):
        self.assertIn("point_three_heading", asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"])
        self.assertNotIn("point_three_heading", asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["A2"])
        self.assertNotIn("point_three_heading", asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B_FAMILY_A2"])

    def test_a2_and_b_family_a2_entries_unchanged(self):
        self.assertEqual(
            asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["A2"],
            ("in_one_line", "point_one_heading", "point_two_heading"))
        self.assertEqual(
            asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["A2"],
            asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B_FAMILY_A2"])

    def test_b1_entry_count_grew_by_exactly_one(self):
        # 修正前(2V Phase1/A2配線完了時点)は8件だった。今回1件追加のみで9件。
        self.assertEqual(len(asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]), 9)


class VoiceCheck3vCollisionAuditTests(unittest.TestCase):
    """Fable修正指示3回目(見落とし2): Voice衝突STOP時、runner
    voice_check_3v()が保存するaudit/voice_resolution.jsonにvoice_a/
    voice_b/voice_c(解決済み値または null)・reasonsキーが含まれること
    (後続のstage="tts"単独実行がKeyErrorではなく明示メッセージでSTOPする
    ための前提)。"""

    def test_collision_stop_audit_includes_voice_keys_and_reasons(self):
        fake_results = {"Algieba": {"status": "ERROR"}, "Erinome": {"status": "OK"}, "Schedar": {"status": "OK"}}
        err = RuntimeError("[VOICE_COLLISION_STOP] resolve_voice_names_3v: ...")
        err.resolved = {"voice_a": "Schedar", "voice_b": "Erinome", "voice_c": "Schedar"}
        err.voice_reasons = {"voice_a": "fallback used"}
        saved = {}

        def fake_save_json(path, data):
            saved[path] = data

        with mock.patch.object(runner.b1prod, "first_n_sentences", return_value="sample"), \
             mock.patch.object(runner.b1prod, "run_voice_availability_check", return_value=fake_results), \
             mock.patch.object(runner.b1prod, "resolve_voice_names_3v", side_effect=err), \
             mock.patch.object(runner, "save_json", side_effect=fake_save_json):
            with self.assertRaises(RuntimeError):
                runner.voice_check_3v({"point_one_body": "Voice 1 body text here."})

        audit_path = f"{runner.OUT_DIR_3V}/audit/voice_resolution.json"
        self.assertIn(audit_path, saved)
        payload = saved[audit_path]
        self.assertEqual(payload["status"], "VOICE_COLLISION_STOP")
        self.assertEqual(payload["voice_a"], "Schedar")
        self.assertEqual(payload["voice_b"], "Erinome")
        self.assertEqual(payload["voice_c"], "Schedar")
        self.assertEqual(payload["reasons"], {"voice_a": "fallback used"})

    def test_collision_stop_audit_has_null_voice_keys_when_exception_has_no_resolved_attr(self):
        # resolve_voice_names_3v()の例外にresolved属性が無い(想定外の経路)
        # 場合でもKeyErrorで落ちず、voice_a/b/cはNoneのまま記録される。
        fake_results = {"Algieba": {"status": "OK"}, "Erinome": {"status": "OK"}, "Schedar": {"status": "OK"}}
        err = RuntimeError("[VOICE_COLLISION_STOP] unexpected path")
        saved = {}

        def fake_save_json(path, data):
            saved[path] = data

        with mock.patch.object(runner.b1prod, "first_n_sentences", return_value="sample"), \
             mock.patch.object(runner.b1prod, "run_voice_availability_check", return_value=fake_results), \
             mock.patch.object(runner.b1prod, "resolve_voice_names_3v", side_effect=err), \
             mock.patch.object(runner, "save_json", side_effect=fake_save_json):
            with self.assertRaises(RuntimeError):
                runner.voice_check_3v({"point_one_body": "Voice 1 body text here."})

        payload = saved[f"{runner.OUT_DIR_3V}/audit/voice_resolution.json"]
        self.assertIsNone(payload["voice_a"])
        self.assertIsNone(payload["voice_b"])
        self.assertIsNone(payload["voice_c"])
        self.assertEqual(payload["reasons"], {})


class MainB13vCollisionStopExplicitMessageTests(unittest.TestCase):
    """Fable修正指示3回目(見落とし2): 衝突STOP後にstage="tts"等を単独
    実行した場合、main_b1_3v()がresolution["voice_a"]でKeyErrorに落ちる
    のではなく、明示メッセージのRuntimeErrorでSTOPすること。"""

    def test_stage_tts_after_collision_stop_raises_explicit_message_not_keyerror(self):
        # stage="tts"はneeds_voice_resolution=Trueの経路のため、collision_
        # resolutionを読み込んだ直後(kp_reuse/scaffold/tts本体へ進む前)に
        # 明示RuntimeErrorでSTOPすることを検証する(以降のTTS呼び出し・
        # ファイルI/Oには到達しない)。
        collision_resolution = {"status": "VOICE_COLLISION_STOP", "error": "[VOICE_COLLISION_STOP] ...",
                                 "voice_a": None, "voice_b": "Erinome", "voice_c": None, "reasons": {}}
        with mock.patch.object(runner.sys, "argv", ["prog", "tts", "b1_3v"]), \
             mock.patch.object(runner, "cl"), \
             mock.patch("builtins.open", mock.mock_open(read_data="# Title\n")), \
             mock.patch.object(runner, "load_json", return_value=collision_resolution):
            with self.assertRaises(RuntimeError) as ctx:
                runner.main_b1_3v()
        self.assertIn("VOICE_COLLISION_STOP", str(ctx.exception))
        self.assertNotIsInstance(ctx.exception, KeyError)


class RunnerLevelB1_3VDispatchTests(unittest.TestCase):
    """runner main()のlevel="b1_3v"分岐契約テスト: main()がsys.argv[2]==
    "b1_3v"のときmain_b1_3v()を呼び、main_a2()は呼ばないこと。既存
    "a2"/既定("b1")分岐は本タスクで変更していないことも確認する。"""

    def test_level_b1_3v_dispatches_to_main_b1_3v(self):
        with mock.patch.object(runner, "main_b1_3v") as main_b1_3v_mock, \
             mock.patch.object(runner, "main_a2") as main_a2_mock, \
             mock.patch.object(runner.sys, "argv", ["prog", "all", "b1_3v"]):
            runner.main()
        main_b1_3v_mock.assert_called_once()
        main_a2_mock.assert_not_called()

    def test_level_a2_does_not_dispatch_to_main_b1_3v(self):
        with mock.patch.object(runner, "main_b1_3v") as main_b1_3v_mock, \
             mock.patch.object(runner, "main_a2") as main_a2_mock, \
             mock.patch.object(runner.sys, "argv", ["prog", "all", "a2"]):
            runner.main()
        main_a2_mock.assert_called_once()
        main_b1_3v_mock.assert_not_called()

    def test_default_level_does_not_dispatch_to_main_b1_3v_or_main_a2(self):
        fake_prep = {"article_text": "# Title\n", "parts": {"point_one_body": "x"}}
        fake_scaffold_result = {"support_status": {"preview": "OK"}, "deviation": {"overall_status": "LEDGER_COMPLIANT"}}
        with mock.patch.object(runner, "main_a2") as main_a2_mock, \
             mock.patch.object(runner, "main_b1_3v") as main_b1_3v_mock, \
             mock.patch.object(runner.sys, "argv", ["prog"]), \
             mock.patch.object(runner, "prepare", return_value=fake_prep), \
             mock.patch.object(runner, "voice_check", return_value={"voice_a": "Algieba", "voice_b": "Erinome", "reasons": {}}), \
             mock.patch.object(runner, "reuse_key_phrases"), \
             mock.patch.object(runner, "run_scaffold", return_value=fake_scaffold_result), \
             mock.patch.object(runner, "run_tts"), \
             mock.patch.object(runner, "finalize_tts_results"), \
             mock.patch.object(runner, "run_assembly", return_value={"status": "GATE_BLOCKED"}), \
             mock.patch.object(runner, "load_json", return_value={}), \
             mock.patch.object(runner, "save_json"), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0), \
             mock.patch.object(runner, "compute_cost_jpy_so_far", return_value=(0.0, {})), \
             mock.patch.object(runner.cl, "install"), \
             mock.patch("builtins.open", mock.mock_open(read_data="dummy ledger text")):
            runner.main()
        main_a2_mock.assert_not_called()
        main_b1_3v_mock.assert_not_called()


class NoTrialScriptModuleLevelImportTests(unittest.TestCase):
    """STOP条件(d)「Trial専用実装への依存が残る」の裏付け: registry・
    production_01・production_runner_01のいずれも、Trialスクリプト
    (モジュール名に"trial"を含む)をモジュールレベルでimportしていない
    ことを、実ファイルのASTを解析して確認する。"""

    def _module_level_imports(self, path: str) -> list:
        import ast
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
        return imported_modules

    def test_registry_module_does_not_import_any_trial_script(self):
        imports = self._module_level_imports("er012_b_family_editorial_type_registry_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])

    def test_voices_production_module_does_not_import_any_trial_script(self):
        imports = self._module_level_imports("er012_b_family_voices_production_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])

    def test_production_runner_module_does_not_import_any_trial_script(self):
        imports = self._module_level_imports("er012_b_family_production_runner_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])


if __name__ == "__main__":
    unittest.main()
