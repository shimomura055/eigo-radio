# ============================================================
# er012_editorial_b_family_production_phase1_test_01.py
# 管理ID: EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01
# ============================================================
# Gate 3/4向け単体テスト(API呼び出し無し)。
#   1. registryのvoice_assignmentが実際のTTS呼び出し引数(fallback含む)と
#      一致すること。
#   2. split_five_voice_sections()が5見出し以外(想定外構造)でNoneを
#      返すこと(ガードの単体テスト)。
#   3. build_b1_voices_timeline()が既存asm.build_b1_timeline()を一切
#      呼ばず、Tension slotをseq内に含むこと(契約テスト、モック使用)。
#   4. resolve_voice_names()のfallback分岐(API不可時にSchedar/Sulafat
#      へ切替)の単体テスト。
#   5. 修正指示1回目(OPEN-121/OPEN-122安全機構の本文segmentへの適用):
#      本文相当segment呼び出しで、A-Family既存Production
#      (er003_v1_n3_01_tts_generate.py 745-754行目)と同一規約に基づき
#      enable_connected_speech_equivalence_layer/enable_repetition_qaが
#      有効になること、かつA-Familyでも対象外のsegment(Tension・Closing)
#      には適用しないこと(対称性維持)の契約テスト。
from __future__ import annotations

import unittest
from unittest import mock

import er003_v1_n3_01_assemble as asm
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_production_runner_01 as runner
import er012_b_family_voices_production_01 as b1prod

ARTICLE_FIVE_SECTIONS = """# Title Here

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

ARTICLE_WRONG_SECTION_COUNT = """# Title Here

## Only One Heading

Some body text.
"""


class RegistryVoiceAssignmentTests(unittest.TestCase):
    def test_voice_assignment_matches_approved_names(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertEqual(editorial_type["voice_assignment"]["voice_a"], "Algieba")
        self.assertEqual(editorial_type["voice_assignment"]["voice_b"], "Erinome")
        self.assertEqual(editorial_type["voice_assignment"]["narrator"], "Aoede")
        self.assertEqual(editorial_type["voice_fallback"]["voice_a"], "Schedar")
        self.assertEqual(editorial_type["voice_fallback"]["voice_b"], "Sulafat")

    def test_comment_roles_present_for_all_four(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        for key in ("comment_1", "comment_2", "comment_3", "comment_4"):
            self.assertIn(key, editorial_type["comment_roles"])
            self.assertTrue(editorial_type["comment_roles"][key].strip())

    def test_comment_1_bans_the_question_phrase(self):
        # EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11の禁止句
        # 追加がregistry側の実体にも反映されていることを確認する。
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn('"the question"という語句そのもの', editorial_type["comment_roles"]["comment_1"])

    def test_first_person_not_mechanically_enforced_phase1(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertFalse(editorial_type["first_person_mechanically_enforced"])


class SplitFiveVoiceSectionsTests(unittest.TestCase):
    def test_valid_five_section_article_parses(self):
        sections = b1prod.split_five_voice_sections(ARTICLE_FIVE_SECTIONS)
        self.assertIsNotNone(sections)
        self.assertEqual(sections["voice_a_heading"], "Voice A Heading")
        self.assertEqual(sections["voice_b_heading"], "Voice B Heading")
        self.assertIn("Tension body text here.", sections["tension_body"])
        self.assertIn("Closing body text here.", sections["closing_body"])

    def test_wrong_section_count_returns_none(self):
        sections = b1prod.split_five_voice_sections(ARTICLE_WRONG_SECTION_COUNT)
        self.assertIsNone(sections)

    def test_no_title_returns_none(self):
        sections = b1prod.split_five_voice_sections("## Heading only, no title\n\nBody.\n")
        self.assertIsNone(sections)


class ResolveVoiceNamesFallbackTests(unittest.TestCase):
    def test_both_voices_available_uses_approved_names(self):
        sample_results = {"Algieba": {"status": "OK"}, "Erinome": {"status": "OK"}}
        voice_a, voice_b, reasons = b1prod.resolve_voice_names(sample_results)
        self.assertEqual(voice_a, "Algieba")
        self.assertEqual(voice_b, "Erinome")
        self.assertEqual(reasons, {})

    def test_voice_a_unavailable_falls_back_to_schedar(self):
        sample_results = {"Algieba": {"status": "ERROR", "error": "technical failure"},
                           "Erinome": {"status": "OK"}}
        voice_a, voice_b, reasons = b1prod.resolve_voice_names(sample_results)
        self.assertEqual(voice_a, "Schedar")
        self.assertEqual(voice_b, "Erinome")
        self.assertIn("voice_a", reasons)

    def test_voice_b_unavailable_falls_back_to_sulafat(self):
        sample_results = {"Algieba": {"status": "OK"},
                           "Erinome": {"status": "ERROR", "error": "technical failure"}}
        voice_a, voice_b, reasons = b1prod.resolve_voice_names(sample_results)
        self.assertEqual(voice_a, "Algieba")
        self.assertEqual(voice_b, "Sulafat")
        self.assertIn("voice_b", reasons)


class BuildB1VoicesTimelineContractTests(unittest.TestCase):
    """既存asm.build_b1_timeline()(11-part固定、A-Family/既存B1が使う関数)を
    一切呼ばないこと、かつ既存共有primitive(build_b1_key_phrase_blocks等)は
    呼ぶことを確認する契約テスト(実TTS/実Assembly実行はしない、モックのみ)。"""

    def _fake_parts(self):
        stereo = lambda: [[0.0, 0.0]] * 10  # noqa: E731 (テスト専用の軽量プレースホルダ)
        b1 = {name: stereo() for name in (
            "preview", "comment_1", "comment_2", "comment_3", "comment_4",
            "full_story_part1", "full_story_part2", "point_one_heading", "point_one",
            "point_two_heading", "point_two", "in_one_line", b1prod.EXTRA_SEGMENT_NAME)}
        return {
            "intro": stereo(), "welcome": stereo(), "topic_intro": stereo(), "notification": stereo(),
            "preview_intro": stereo(), "key_phrases_intro": stereo(), "full_story_intro": stereo(),
            "point_notification": stereo(), "outro": stereo(), "kp_items": [], "b1_segments": b1,
        }

    def test_build_b1_voices_timeline_does_not_call_existing_build_b1_timeline(self):
        parts = self._fake_parts()
        with mock.patch.object(asm, "build_b1_timeline") as mocked_old_timeline:
            seq = b1prod.build_b1_voices_timeline(parts, "Algieba", "Erinome")
            mocked_old_timeline.assert_not_called()
        labels = [name for name, _ in seq]
        self.assertTrue(any(label.startswith("Tension:") for label in labels))
        self.assertTrue(any("Voice A body" in label for label in labels))
        self.assertTrue(any("Voice B body" in label for label in labels))

    def test_build_b1_voices_timeline_uses_shared_key_phrase_block_builder(self):
        parts = self._fake_parts()
        with mock.patch.object(asm, "build_b1_key_phrase_blocks", wraps=asm.build_b1_key_phrase_blocks) as spy:
            b1prod.build_b1_voices_timeline(parts, "Algieba", "Erinome")
            spy.assert_called_once()


class VoiceBodySafetyFeatureDefaultsTests(unittest.TestCase):
    """修正指示1回目: generate_voice_body_wide_margin(Voice A/B本文専用
    関数)の既定値が、A-Family既存Production(OPEN-121/OPE-122対象4segment)
    と同じくTrueであることの単体テスト(実TTS呼び出しなし、シグネチャ検査)。"""

    def test_defaults_enable_connected_speech_and_repetition_qa(self):
        import inspect
        sig = inspect.signature(b1prod.generate_voice_body_wide_margin)
        self.assertIs(sig.parameters["enable_connected_speech_equivalence_layer"].default, True)
        self.assertIs(sig.parameters["enable_repetition_qa"].default, True)


class RunTtsBodySegmentSafetyFeatureContractTests(unittest.TestCase):
    """修正指示1回目の中心契約テスト: er012_b_family_production_runner_01.
    run_tts()が、本文相当segment(Hook part1/2=full_story_part1/2、
    Voice A=point_one、Voice B=point_two)呼び出しではOPEN-121/OPEN-122
    フラグを有効化し、A-Familyでも対象外のsegment(Tension・Closing=
    in_one_line)には適用しない(A-Familyとの対称性維持)ことを、実TTS/
    実API呼び出しなしで(全生成関数をモック化して)検証する。"""

    def _fake_parts(self):
        return {
            "title": "Sample Title", "part1": "Hook sentence one.", "part2": "Hook sentence two.",
            "point_one_heading": "One Voice Heading.", "point_one_body": "Voice A body text.",
            "point_two_heading": "Another Voice Heading.", "point_two_body": "Voice B body text.",
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
        with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(runner.voice01, "generate_charon_english", side_effect=self._ok), \
             mock.patch.object(runner.point_headings, "generate", side_effect=self._ok), \
             mock.patch.object(runner.b1prod, "generate_voice_body_wide_margin",
                                side_effect=self._ok) as voice_body_mock, \
             mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin",
                                side_effect=self._ok) as narration_mock:
            runner.run_tts(parts, support, "Algieba", "Erinome")

        # Voice A/B(point_one/point_two)は常にTrue(A-Familyの4segment
        # 集合の一員)。
        voice_body_calls = {c.args[2]: c.kwargs for c in voice_body_mock.call_args_list}
        for voice_name in ("Algieba", "Erinome"):
            kwargs = voice_body_calls[voice_name]
            self.assertTrue(kwargs["enable_connected_speech_equivalence_layer"])
            self.assertTrue(kwargs["enable_repetition_qa"])

        # Hook part1/2(full_story_part1/2)はTrue、Tension・Closing
        # (in_one_line)はA-Familyでも対象外のためFalse。
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
        # disfluency_qaの既存規約(in_one_lineのみTrue)が今回の変更で
        # 壊れていないことも合わせて確認する。
        self.assertTrue(narration_calls["in_one_line"]["disfluency_qa"])
        self.assertFalse(narration_calls[b1prod.EXTRA_SEGMENT_NAME]["disfluency_qa"])


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01 追加テスト
# ============================================================
import er012_b_family_voices_a2_production_01 as a2prod  # noqa: E402


class BFamilyA2RegistryTests(unittest.TestCase):
    def test_a2_config_present_under_editorial_type(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("a2", editorial_type)
        a2_config = registry.get_editorial_type_a2()
        self.assertIs(a2_config, editorial_type["a2"])

    def test_audio_gate_level_is_not_standard_a2_string(self):
        a2_config = registry.get_editorial_type_a2()
        self.assertEqual(a2_config["audio_gate_level"], "B_FAMILY_A2")
        self.assertNotEqual(a2_config["audio_gate_level"], "A2")

    def test_slowdown_target_segments_include_voice_a_and_b_and_tension(self):
        a2_config = registry.get_editorial_type_a2()
        targets = a2_config["slowdown_target_segments"]
        for name in ("point_one", "point_two", "point_one_heading", "point_two_heading",
                     "full_story_part1", "full_story_part2", "tension_reflection", "in_one_line"):
            self.assertIn(name, targets)

    def test_comment_language_and_voice_is_japanese_aoede(self):
        a2_config = registry.get_editorial_type_a2()
        self.assertEqual(a2_config["comment_language"], "ja")
        self.assertEqual(a2_config["comment_voice"], "Aoede")

    def test_japanese_title_required_and_text_present(self):
        a2_config = registry.get_editorial_type_a2()
        self.assertTrue(a2_config["japanese_title_required"])
        self.assertIn("b_voices_a2_free_address", a2_config["japanese_titles"])
        self.assertTrue(a2_config["japanese_titles"]["b_voices_a2_free_address"].strip())

    def test_required_segments_cover_all_fifteen_expected_names(self):
        a2_config = registry.get_editorial_type_a2()
        names = [n for n, _ in a2_config["required_segments"]]
        expected = ("topic_intro", "japanese_title", "preview", "comment_1", "comment_2",
                    "comment_3", "comment_4", "point_one_heading", "point_two_heading",
                    "point_one", "point_two", "full_story_part1", "full_story_part2",
                    b1prod.EXTRA_SEGMENT_NAME, "in_one_line")
        self.assertEqual(tuple(names), expected)

    def test_a2_voice_assignment_and_comment_roles_are_shared_with_b1(self):
        # A2はComment Contract(役割定義)・Voice Assignmentともに専用の
        # 別定義を持たず、B1と同一のregistryエントリを流用する(ユーザー
        # 決定B-A2-3/B-A2-6、出力言語のみa2設定側で差し替える)。
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIs(editorial_type["a2"]["comment_language"], registry.B_FAMILY_A2_COMMENT_LANGUAGE)
        self.assertEqual(editorial_type["voice_assignment"]["voice_a"], "Algieba")
        self.assertEqual(editorial_type["voice_assignment"]["voice_b"], "Erinome")


class B1PromptByteIdentityAfterA2WiringTests(unittest.TestCase):
    """Gate 3 item1「既存B1経路の挙動は不変」の裏付け: 本タスクで登録した
    A2設定追加後も、既存B1のComment Contract本文(FINALIZE-11確定版)が
    一切変更されていないことを、Fable委任文記載の固定文言(禁止句マーカー)
    でも重ねて検証する(既存test_comment_1_bans_the_question_phraseに
    加え、4件全ての非空・末尾文言が変わっていないことを確認)。"""

    def test_comment_roles_unchanged_word_markers(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("Listening Focus", editorial_type["comment_roles"]["comment_1"])
        self.assertIn("Hookの問いから「ここから異なるVoiceを聞く」への橋渡し",
                      editorial_type["comment_roles"]["comment_2"])
        self.assertIn("なぜ違って感じるのか", editorial_type["comment_roles"]["comment_3"])
        self.assertIn("一段深い問い", editorial_type["comment_roles"]["comment_4"])


class A2ProductionModuleTranscriptionByteIdentityTests(unittest.TestCase):
    """Gate 3 item1/3「Trialスクリプトをimportしない」の裏付け: A2
    Production module(er012_b_family_voices_a2_production_01.py)が
    Trial07/Trial02-Writerから全文転記した定数が、転記元と一字一句
    一致することを確認する(転記ミス・意図しない改変がないことの
    machine-checkable evidence)。"""

    def test_leakage_check_prompt_matches_trial07_verbatim(self):
        import er012_editorial_b_voices_trial_07 as trial07
        self.assertEqual(a2prod.LEAKAGE_CHECK_PROMPT_TEMPLATE, trial07.LEAKAGE_CHECK_PROMPT_TEMPLATE)
        self.assertEqual(a2prod.LEAKAGE_CHECK_DEVELOPER_MESSAGE, trial07.LEAKAGE_CHECK_DEVELOPER_MESSAGE)
        self.assertEqual(a2prod.ANALYTICAL_LEAKAGE_JSON_SCHEMA, trial07.ANALYTICAL_LEAKAGE_JSON_SCHEMA)
        self.assertEqual(a2prod.VOICE_LEAKAGE_FIELDS, trial07.VOICE_LEAKAGE_FIELDS)
        self.assertEqual(a2prod.TENSION_LEAKAGE_FIELDS, trial07.TENSION_LEAKAGE_FIELDS)
        self.assertEqual(a2prod.CLOSING_LEAKAGE_FIELDS, trial07.CLOSING_LEAKAGE_FIELDS)

    def test_writer_prompt_constants_match_trial02_writer_verbatim(self):
        import er012_editorial_b_voices_a2_trial02_writer as writer
        self.assertEqual(a2prod.A2_KAI1_INSTRUCTION_PARA1_PARA3, writer.A2_KAI1_INSTRUCTION_PARA1_PARA3)
        self.assertEqual(a2prod.CORE_EXPLANATORY_LOGIC_PRESERVATION, writer.CORE_EXPLANATORY_LOGIC_PRESERVATION)
        self.assertEqual(a2prod.A2_TABLE_PRINCIPLES_JA, writer.A2_TABLE_PRINCIPLES_JA)
        self.assertEqual(a2prod.B_FAMILY_A2_TASK_INSTRUCTIONS, writer.B_FAMILY_A2_TASK_INSTRUCTIONS)
        self.assertEqual(a2prod.build_adapt_prompt("SAMPLE"), writer.build_adapt_prompt("SAMPLE"))

    def test_module_does_not_import_any_trial_script_at_module_level(self):
        import ast
        with open("er012_b_family_voices_a2_production_01.py", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
        trial_imports = [m for m in imported_modules if "trial" in m]
        self.assertEqual(trial_imports, [])


class RequiredSegmentsCompletenessCheckTests(unittest.TestCase):
    """Gate 3 item8(OPEN-129整合): Lane B runner側完全性チェック関数の
    単体テスト(段数不足・voice不一致を検出できること)。"""

    def _all_ok_status(self):
        a2_config = registry.get_editorial_type_a2()
        return {name: "OK" for name, _ in a2_config["required_segments"]}

    def test_complete_status_returns_complete_true(self):
        result = a2prod.check_required_segments_completeness(self._all_ok_status(), "Algieba", "Erinome")
        self.assertTrue(result["complete"])
        self.assertEqual(result["missing_or_not_ok"], [])
        self.assertEqual(result["expected_segment_count"], 15)

    def test_missing_segment_is_detected(self):
        status = self._all_ok_status()
        del status["point_two"]
        result = a2prod.check_required_segments_completeness(status, "Algieba", "Erinome")
        self.assertFalse(result["complete"])
        self.assertIn("point_two", result["missing_or_not_ok"])

    def test_non_ok_status_is_detected(self):
        status = self._all_ok_status()
        status["point_one"] = "STOPPED"
        result = a2prod.check_required_segments_completeness(status, "Algieba", "Erinome")
        self.assertFalse(result["complete"])
        self.assertTrue(any("point_one" in item for item in result["missing_or_not_ok"]))


class DisfluencyQaMandatoryDictB_FamilyA2Tests(unittest.TestCase):
    """Gate 3 item7: 共有Gate辞書へのB_FAMILY_A2エントリ追加が、既存
    B1/A2エントリを変更していないこと(diffの範囲確認)を、実際にロードした
    辞書の内容で検証する。"""

    def test_existing_b1_and_standard_a2_entries_unchanged(self):
        # EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01(Fable修正指示1回目、
        # 2026-09-10): ユーザー正式決定により"B1"へ`point_three_heading`が追加された
        # (3Vに必要な最小追加、er003_v1_n3_01_assemble.py参照)。旧8要素タプルはその
        # まま部分集合として保持し、追加は`point_three_heading`1件のみであることを固定する。
        old_b1_entries = ("preview", "comment_1", "comment_2", "comment_3", "comment_4",
                           "in_one_line", "point_one_heading", "point_two_heading")
        current_b1 = asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]
        self.assertEqual(current_b1[:len(old_b1_entries)], old_b1_entries)
        self.assertEqual(current_b1[len(old_b1_entries):], ("point_three_heading",))
        self.assertEqual(
            asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["A2"],
            ("in_one_line", "point_one_heading", "point_two_heading"))

    def test_b_family_a2_entry_registered_and_matches_standard_a2(self):
        self.assertIn("B_FAMILY_A2", asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL)
        self.assertEqual(
            asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B_FAMILY_A2"],
            asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["A2"])


class GenerateVoiceBodyWithA2SlowdownContractTests(unittest.TestCase):
    """Gate 3 item1/2: Voice A/B slowdown付きTTS合成関数が、正しい
    style_prefix_override(標準A2の既存6% slowdown instruction)とOPEN-121/
    OPEN-122フラグをb1prod.generate_voice_body_wide_margin()へ渡し、その後
    標準A2のapply_a2_slowdown_postprocess()(無変更)を呼ぶことを、実TTS
    呼び出しなしで(モックで)検証する。"""

    def test_calls_wide_margin_with_slower_prefix_then_postprocess(self):
        import er003_v1_n3_01_tts_generate as n3_tts
        with mock.patch.object(a2prod.b1prod, "generate_voice_body_wide_margin",
                                return_value={"status": "OK"}) as wide_margin_mock, \
             mock.patch.object(a2prod.n3_tts, "apply_a2_slowdown_postprocess",
                                return_value={"status": "OK", "slowdown_applied": True}) as postprocess_mock:
            result = a2prod.generate_voice_body_wide_margin_with_a2_slowdown(
                "point_one", "Sample text.", "out/point_one.wav", "Algieba")
        wide_margin_mock.assert_called_once()
        _, kwargs = wide_margin_mock.call_args
        self.assertEqual(kwargs["style_prefix_override"], n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER)
        self.assertTrue(kwargs["enable_connected_speech_equivalence_layer"])
        self.assertTrue(kwargs["enable_repetition_qa"])
        postprocess_mock.assert_called_once()
        self.assertEqual(result["status"], "OK")


class RunnerLevelA2DispatchTests(unittest.TestCase):
    """Gate 3 item1「runnerにlevel="a2"分岐」の契約テスト: main()が
    sys.argv[2]=="a2"のときmain_a2()を呼び、それ以外(既定含む)では既存
    B1経路(main_a2()呼び出しなし)のままであることを確認する。"""

    def test_level_a2_dispatches_to_main_a2(self):
        with mock.patch.object(runner, "main_a2") as main_a2_mock, \
             mock.patch.object(runner.sys, "argv", ["prog", "all", "a2"]):
            runner.main()
        main_a2_mock.assert_called_once()

    def test_default_level_does_not_dispatch_to_main_a2(self):
        # 実ファイル(prepare()/save_json()等)への書き込みを一切発生させない
        # よう、main()が呼ぶ関数を全てモック化する(実際にPhase1_02の既存
        # 承認済み出力ディレクトリへ誤って書き込んでしまう事故を防ぐため、
        # save_jsonも必ずモックすること)。
        fake_prep = {"article_text": "# Title\n", "parts": {"point_one_body": "x"}}
        fake_scaffold_result = {"support_status": {"preview": "OK"}, "deviation": {"overall_status": "LEDGER_COMPLIANT"}}
        with mock.patch.object(runner, "main_a2") as main_a2_mock, \
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


if __name__ == "__main__":
    unittest.main()
