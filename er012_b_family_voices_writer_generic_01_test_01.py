# ============================================================
# er012_b_family_voices_writer_generic_01_test_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04-
# GENERALIZATION-AND-REGRESSION
# ============================================================
# `er012_b_family_voices_writer_generic_01.py`(汎用Writerテンプレート/
# パイプライン)+`er012_b_family_voices_theme_ai_screening_01.py`(テーマ
# データ)の単体テスト(API呼び出し無し、¥0)。
#   1. テンプレート組み立てのpin(ANCHOR挿入・出力の決定性)。
#   2. Voice Card→prompt注入(3枚とも本文へ現れる、Ledger evidence tag
#      traceabilityが保持される)。
#   3. 任意パターン(external_constraint)のON/OFF(3b・自己チェック・
#      Leakage QAフィールドが条件どおり出現/消失する)。
#   4. Ledger fragment一般化ルール(可視Voice数を超えるVoice番号のみ除去)。
#   5. 6区切りparserがProduction正式関数(b1prod)への委譲であること。
#   6. Dangling Reference Check相当: 旧Trialファイル
#      (`er012_editorial_b_voices_3v_person_voice_trial_02`等、"trial"を
#      含むモジュール名)をモジュールレベルでimportしていないこと。
from __future__ import annotations

import copy
import unittest

import er012_b_family_voices_theme_ai_screening_01 as theme_ai_screening
import er012_b_family_voices_writer_generic_01 as wg


class BuildFocusModuleBlockDeterminismTests(unittest.TestCase):
    def test_same_theme_config_produces_identical_block(self):
        b1 = wg.build_focus_module_block_3v(theme_ai_screening.THEME_CONFIG)
        b2 = wg.build_focus_module_block_3v(theme_ai_screening.THEME_CONFIG)
        self.assertEqual(b1, b2)

    def test_anchor_present_exactly_once_after_insertion(self):
        block = wg.build_focus_module_block_3v(theme_ai_screening.THEME_CONFIG)
        candidate = wg.build_candidate_template(block)
        self.assertEqual(candidate.count(wg.ANCHOR), 1)
        self.assertIn(block, candidate)


class VoiceCardInjectionTests(unittest.TestCase):
    def setUp(self):
        self.block = wg.build_focus_module_block_3v(theme_ai_screening.THEME_CONFIG)

    def test_all_three_voice_cards_appear_in_block(self):
        for card in theme_ai_screening.THEME_CONFIG["voice_cards"]:
            self.assertIn(card["person"], self.block)
            self.assertIn(card["stake"], self.block)

    def test_evidence_tags_preserved_verbatim_for_traceability(self):
        for card in theme_ai_screening.THEME_CONFIG["voice_cards"]:
            tags = wg.voice_card_evidence_tags(card)
            self.assertTrue(tags, f"{card['voice_key']}にLedger evidence tagが見つかりません")
            for tag in tags:
                self.assertIn(tag, self.block)

    def test_card_intro_caveat_included_when_present(self):
        card3 = theme_ai_screening.THEME_CONFIG["voice_cards"][2]
        self.assertIn(card3["card_intro_caveat"], self.block)

    def test_reference_phrases_included_in_heading_instruction(self):
        for card in theme_ai_screening.THEME_CONFIG["voice_cards"]:
            self.assertIn(card["reference_phrase"], self.block)


class ExperientialClaimGroundingPermanentPrincipleTests(unittest.TestCase):
    """ユーザー決定2026-09-12(1): 恒久原則、フラグ無しで常時含まれること。"""

    def test_grounding_block_always_present(self):
        theme_config_no_ext = copy.deepcopy(theme_ai_screening.THEME_CONFIG)
        theme_config_no_ext["external_constraint"] = None
        block = wg.build_focus_module_block_3v(theme_config_no_ext)
        self.assertIn(wg.COMMON_EXPERIENTIAL_CLAIM_GROUNDING_BLOCK, block)


class ExternalConstraintOptionalPatternToggleTests(unittest.TestCase):
    """ユーザー決定2026-09-12(2): 任意パターン、ON/OFFで本文・QAスキーマが
    条件どおりに変わること(恒久ルール化しない、既定は呼び出し側が選ぶ)。"""

    def setUp(self):
        self.theme_on = theme_ai_screening.THEME_CONFIG
        self.theme_off = copy.deepcopy(theme_ai_screening.THEME_CONFIG)
        self.theme_off["external_constraint"] = None

    def test_on_includes_3b_and_self_check(self):
        block = wg.build_focus_module_block_3v(self.theme_on)
        self.assertIn("外部制約の統合", block)
        self.assertIn("Tensionの自己チェック", block)
        self.assertIn("VOICE_4_EVIDENCE", block)

    def test_off_omits_3b_and_self_check(self):
        block = wg.build_focus_module_block_3v(self.theme_off)
        self.assertNotIn("外部制約の統合", block)
        self.assertNotIn("Tensionの自己チェック", block)
        self.assertNotIn("VOICE_4_EVIDENCE", block)

    def test_leakage_schema_includes_constraint_integration_field_only_when_enabled(self):
        schema_on, fields_on = wg.build_leakage_schema_3v(True)
        schema_off, fields_off = wg.build_leakage_schema_3v(False)
        self.assertIn(wg.TENSION_LEAKAGE_FIELD_CONSTRAINT_INTEGRATION, fields_on["tension"])
        self.assertNotIn(wg.TENSION_LEAKAGE_FIELD_CONSTRAINT_INTEGRATION, fields_off["tension"])
        # Voice/Closing側のfieldは有効/無効で変化しない(対象外の基準を追加/除去しない)。
        self.assertEqual(fields_on["voice_1"], fields_off["voice_1"])
        self.assertEqual(fields_on["closing"], fields_off["closing"])

    def test_leakage_prompt_mentions_constraint_field_only_when_enabled(self):
        sections = {
            "voice_1_body": "v1", "voice_2_body": "v2", "voice_3_body": "v3",
            "tension_body": "t", "closing_body": "c",
        }
        prompt_on = wg.build_leakage_check_prompt_3v(sections, True)
        prompt_off = wg.build_leakage_check_prompt_3v(sections, False)
        self.assertIn("leak_tension_constraint_integration", prompt_on)
        self.assertNotIn("leak_tension_constraint_integration", prompt_off)


class LedgerFragmentVisibleVoicesGeneralizationTests(unittest.TestCase):
    """Trial-02の`build_ledger_fragment_voices_1_2_3_only()`(VOICE_4専用
    ハードコード)を一般化したもの: 可視Voice数を超えるVoice番号のブロックの
    みを除去する(意味は変更しない)。"""

    # 実Ledgerの実際の記法(`[VOICE_n_EVIDENCE] n-xx(fact_id): ...`、閉じ
    # 角括弧の直後に半角スペース+番号が続く)に合わせる(er012_output/
    # ai_screening_ledger_trial_01/research/verified_fact_ledger.txt実物で確認済み)。
    LEDGER_TEXT = (
        "[VOICE_1_EVIDENCE] 1-01(fact_a): Applicant fact line.\n\n"
        "[VOICE_2_EVIDENCE] 2-01(fact_b): Recruiter fact line.\n\n"
        "[VOICE_4_EVIDENCE] 4-01(fact_c): External constraint fact line.\n\n"
        "[VOICE_3_EVIDENCE] 3-01(fact_d): Owner fact line.\n"
    )

    def test_default_three_visible_voices_excludes_voice_4_only(self):
        fragment = wg.build_ledger_fragment_visible_voices_only(self.LEDGER_TEXT, num_visible_voices=3)
        self.assertIn("[VOICE_1_EVIDENCE] 1-01", fragment)
        self.assertIn("[VOICE_2_EVIDENCE] 2-01", fragment)
        self.assertIn("[VOICE_3_EVIDENCE] 3-01", fragment)
        self.assertNotIn("[VOICE_4_EVIDENCE] 4-01", fragment)
        self.assertNotIn("External constraint fact line.", fragment)

    def test_two_visible_voices_excludes_voice_3_and_4(self):
        fragment = wg.build_ledger_fragment_visible_voices_only(self.LEDGER_TEXT, num_visible_voices=2)
        self.assertIn("[VOICE_1_EVIDENCE] 1-01", fragment)
        self.assertIn("[VOICE_2_EVIDENCE] 2-01", fragment)
        self.assertNotIn("[VOICE_3_EVIDENCE] 3-01", fragment)
        self.assertNotIn("[VOICE_4_EVIDENCE] 4-01", fragment)


class SixSectionParserDelegatesToProductionTests(unittest.TestCase):
    ARTICLE = """# Title

## The Question

Hook body.

### Voice One

Voice one body.

### Voice Two

Voice two body.

### Voice Three

Voice three body.

## Tension

Tension body.

## Closing

Closing body.
"""

    def test_delegates_to_b1prod_split_six_voice_sections(self):
        import er012_b_family_voices_production_01 as b1prod
        expected = b1prod.split_six_voice_sections(self.ARTICLE)
        actual = wg.split_six_voice_sections(self.ARTICLE)
        self.assertEqual(expected, actual)

    def test_downstream_pipeline_functions_use_matching_keys_no_api(self):
        """回帰確認: `split_six_voice_sections()`が返すキー(b1prod方式の
        `voice_1_body`/`voice_2_body`/`voice_3_body`)と、`run_overlap_
        monitoring_3v()`/`build_leakage_check_prompt_3v()`が参照するキーが
        一致していること(¥0、API呼び出し無し)。過去にこの不一致で実行時
        `KeyError: 'point_one_body'`が発生した回帰の再発防止。"""
        import tempfile
        sections = wg.split_six_voice_sections(self.ARTICLE)
        with tempfile.TemporaryDirectory() as tmp:
            overlap = wg.run_overlap_monitoring_3v(sections, tmp)
        self.assertIn("directed_voice_pairs", overlap)
        prompt = wg.build_leakage_check_prompt_3v(sections, True)
        self.assertIn("Voice one body.", prompt)
        self.assertIn("Voice three body.", prompt)


class VoiceCardValidationTests(unittest.TestCase):
    def test_missing_required_field_raises(self):
        card = wg.make_voice_card(
            voice_key="voice_1", stakeholder_label="X", role_description_ja="", reference_phrase="the x",
            person="p", situation="s", need="n", concern="c", protect="pr", why="w", constraint="co",
            concrete_scene="cs", supporting_evidence="se", stake="st")
        with self.assertRaises(ValueError):
            wg.validate_voice_card(card)

    def test_theme_config_requires_exactly_three_voice_cards(self):
        with self.assertRaises(ValueError):
            wg.make_theme_config(
                theme_id="t", topic_ja="topic", ledger_path="x.txt",
                voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2],
                tension_common_ground_value="g", tension_asymmetry_value="a")


class NoTrialScriptModuleLevelImportTests(unittest.TestCase):
    """Gate 4裏付け: 汎用モジュール・テーマdataモジュールのいずれも、
    Trialスクリプト(モジュール名に"trial"を含む)をモジュールレベルで
    importしていないことを、実ファイルのASTを解析して確認する(既存
    `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`
    と同一手法)。"""

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

    def test_writer_generic_module_does_not_import_any_trial_script(self):
        imports = self._module_level_imports("er012_b_family_voices_writer_generic_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])

    def test_theme_ai_screening_module_does_not_import_any_trial_script(self):
        imports = self._module_level_imports("er012_b_family_voices_theme_ai_screening_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])

    def test_production_runner_module_still_does_not_import_any_trial_script(self):
        imports = self._module_level_imports("er012_b_family_production_runner_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])


if __name__ == "__main__":
    unittest.main()
