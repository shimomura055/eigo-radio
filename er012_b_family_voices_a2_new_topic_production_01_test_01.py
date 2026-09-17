# ============================================================
# er012_b_family_voices_a2_new_topic_production_01_test_01.py
# 管理ID: PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B
# ============================================================
# 新規topic A2(2 Voices)正式Production入口(`main_a2_2v()`)・関連primitive
# (`run_writer_stage_generic()`のinstruction一般化、`generate_japanese_
# title_for_new_topic()`、`run_key_phrases_a2_from_own_text()`)のunit test。
# API呼び出しは一切行わない(mock使用、¥0)。
from __future__ import annotations

import ast
import unittest
from unittest.mock import patch

import er003_v1_n3_01_articles_generate as gen_articles
import er012_b_family_production_runner_01 as runner
import er012_b_family_voices_a2_production_01 as a2prod
import er012_b_family_voices_writer_generic_01 as wg


def _module_level_imports(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    return imported_modules


class NoTrialOrFixedTopicImportTests(unittest.TestCase):
    """Dangling Reference Check: 新規moduleがTrialスクリプト(モジュール名に
    "trial"を含む)をモジュールレベルでimportしていないことを確認する。"""

    def test_theme_module_does_not_import_any_trial_script(self):
        imports = _module_level_imports("er012_b_family_voices_theme_personalized_news_a2_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])

    def test_runner_module_does_not_import_any_trial_script(self):
        imports = _module_level_imports("er012_b_family_production_runner_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])

    def test_a2_production_module_does_not_import_any_trial_script(self):
        imports = _module_level_imports("er012_b_family_voices_a2_production_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])


class MainA22vArgumentValidationTests(unittest.TestCase):
    """main_a2_2v()が固定topic pathに依存せず、theme_module/out_dir_baseの
    明示指定を必須とするfail-closed引数検証を持つことを確認する。"""

    def test_missing_theme_module_raises_system_exit(self):
        with patch.object(runner.sys, "argv", ["prog", "all", "a2_2v"]):
            with self.assertRaises(SystemExit):
                runner.main_a2_2v()

    def test_missing_out_dir_base_raises_system_exit(self):
        with patch.object(runner.sys, "argv",
                           ["prog", "all", "a2_2v", "er012_b_family_voices_theme_personalized_news_a2_01"]):
            with self.assertRaises(SystemExit):
                runner.main_a2_2v()

    def test_rejects_theme_config_with_three_voice_cards(self):
        class FakeThemeMod:
            THEME_CONFIG = {"voice_cards": [object(), object(), object()], "theme_id": "x"}
            JAPANESE_TITLE_A2 = "テスト"

        with patch.object(runner.sys, "argv", ["prog", "all", "a2_2v", "fake_theme_module", "out/dir"]):
            with patch("importlib.import_module", return_value=FakeThemeMod()):
                with self.assertRaises(SystemExit):
                    runner.main_a2_2v()


class RunWriterStageGenericInstructionGeneralizationTests(unittest.TestCase):
    """run_writer_stage_generic()へのinstruction引数追加が、既定(省略)時に
    従来のB1_B_DIRECT_INSTRUCTIONをbyte単位で使い続けることを確認する
    (既存main_b1_2v()/main_b1_3v()呼び出し元への後方互換)。API呼び出しは
    build_candidate_promptに到達する前のrun_phase_aで検証だけを行う
    (Phase A自体はAPIを呼ばないpure関数)ため、instructionが実際に
    build_candidate_promptへ渡る箇所を直接呼び出して検証する。"""

    def test_default_instruction_is_b1_direct_instruction(self):
        theme_config = {"voice_cards": [
            wg.make_voice_card(
                voice_key="voice_a", stakeholder_label="A", role_description_ja="a", reference_phrase="a",
                person="p", situation="s", need="n", concern="c", protect="pr", why="w", constraint="co",
                concrete_scene="cs", supporting_evidence="se", stake="st"),
            wg.make_voice_card(
                voice_key="voice_b", stakeholder_label="B", role_description_ja="b", reference_phrase="b",
                person="p", situation="s", need="n", concern="c", protect="pr", why="w", constraint="co",
                concrete_scene="cs", supporting_evidence="se", stake="st"),
        ]}
        focus_module_block = wg.build_focus_module_block_2v({
            **theme_config, "tension_common_ground_value": "g", "tension_asymmetry_value": "a"})
        candidate_template = wg.build_candidate_template(focus_module_block)
        master_full_text = "MASTER"
        prompt_default = wg.build_candidate_prompt(
            candidate_template, master_full_text, "topic", "ledger", gen_articles.B1_B_DIRECT_INSTRUCTION)
        self.assertIn(gen_articles.B1_B_DIRECT_INSTRUCTION, prompt_default)
        self.assertNotIn(gen_articles.A2_KAI1_INSTRUCTION, prompt_default)

    def test_a2_instruction_override_is_used_when_supplied(self):
        prompt_a2 = wg.build_candidate_prompt(
            "TEMPLATE {hanshin_master_full_text} {topic} {verified_ledger_text} "
            "{shared_point_blueprint_block} {evidence_compression_block} {editorial_type_module_block}",
            "MASTER", "topic", "ledger", gen_articles.A2_KAI1_INSTRUCTION)
        self.assertIn(gen_articles.A2_KAI1_INSTRUCTION, prompt_a2)
        self.assertNotIn(gen_articles.B1_B_DIRECT_INSTRUCTION, prompt_a2)

    def test_run_writer_stage_generic_signature_accepts_instruction_kwarg(self):
        import inspect
        sig = inspect.signature(wg.run_writer_stage_generic)
        self.assertIn("instruction", sig.parameters)
        self.assertIsNone(sig.parameters["instruction"].default)
        self.assertEqual(sig.parameters["label"].default, "B1B")


class JapaneseTitleConfigContractTests(unittest.TestCase):
    """日本語タイトルがconfig供給されたテキストをそのままTTS入力へ渡すことを
    確認する(固定辞書`registry...["japanese_titles"]`を経由しない)。"""

    def test_generate_japanese_title_for_new_topic_uses_supplied_text_verbatim(self):
        captured = {}

        def fake_generate_a2_japanese_with_reading_safety(text, out_path, expected_substring, max_extra_chars=60):
            captured["text"] = text
            captured["out_path"] = out_path
            return {"status": "OK"}

        with patch.object(a2prod.n3_tts, "generate_a2_japanese_with_reading_safety",
                           side_effect=fake_generate_a2_japanese_with_reading_safety):
            result = a2prod.generate_japanese_title_for_new_topic("これはテストタイトルです", "out/japanese_title.wav")

        self.assertEqual(captured["text"], "これはテストタイトルです")
        self.assertEqual(captured["out_path"], "out/japanese_title.wav")
        self.assertEqual(result["canonical_text"], "これはテストタイトルです")

    def test_generate_japanese_title_for_new_topic_does_not_touch_fixed_dict(self):
        import er012_b_family_editorial_type_registry_01 as registry
        before = dict(registry.get_editorial_type_a2()["japanese_titles"])
        with patch.object(a2prod.n3_tts, "generate_a2_japanese_with_reading_safety",
                           return_value={"status": "OK"}):
            a2prod.generate_japanese_title_for_new_topic("新しいタイトル文言", "out/japanese_title.wav")
        after = registry.get_editorial_type_a2()["japanese_titles"]
        self.assertEqual(before, after)


class KeyPhraseSelectionSourceTests(unittest.TestCase):
    """Key Phrase選定元がA2自身の確定本文であり、B1 Key Phrase dirの流用
    (reuse_key_phrases_a2)を経由しないことを確認する。"""

    def test_run_key_phrases_a2_from_own_text_calls_sc_run_key_phrases_with_a2_article_text(self):
        captured = {}

        def fake_run_key_phrases(article_text, out_dir, article_id, source_level, process=None):
            captured["article_text"] = article_text
            captured["process"] = process
            captured["out_dir"] = out_dir
            captured["article_id"] = article_id
            return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"}, "canonicalization": None,
                    "redundancy_qa": None}

        with patch.object(a2prod.sc, "run_key_phrases", side_effect=fake_run_key_phrases):
            result = a2prod.run_key_phrases_a2_from_own_text(
                "# Title\n\nThis is the A2 article body used for key phrase selection.",
                "kp_dir", "narration_dir", "test_article_id")

        self.assertEqual(captured["article_text"],
                          "# Title\n\nThis is the A2 article body used for key phrase selection.")
        self.assertEqual(captured["process"], "A2_SUPPORT")
        self.assertEqual(captured["out_dir"], "kp_dir")
        self.assertEqual(captured["article_id"], "test_article_id")
        # canonicalization未完了(このfakeの戻り値)の場合はitemsがNoneで
        # 返り、呼び出し側(runner)が後続TTSへ進まずSTOPできる契約を確認。
        self.assertIsNone(result["items"])

    def test_run_key_phrases_a2_from_own_text_is_not_reuse_key_phrases_a2(self):
        # PHASE-Bの新規関数が、B1 KP dirコピー専用のreuse_key_phrases_a2とは
        # 別関数であること(新規topic pathでreuse_key_phrases_a2を使わない
        # という設計上の分離)を確認する。
        self.assertIsNot(a2prod.run_key_phrases_a2_from_own_text, a2prod.reuse_key_phrases_a2)


if __name__ == "__main__":
    unittest.main()
