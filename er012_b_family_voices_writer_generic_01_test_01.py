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

    def test_theme_config_requires_two_or_three_voice_cards(self):
        # EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01
        # (OPEN-151、2026-09-14ユーザー正式決定)によりmake_theme_config()は
        # 2件(2V)も正式に受け付けるよう一般化された。1件・4件は引き続き
        # 拒否する(2V/3V以外は不正)。2件が受理されるかどうかの契約は
        # `er012_b_family_voices_variable_voice_count_test_01.py`
        # (MakeThemeConfigVariableVoiceCountTests)で網羅的に検証する。
        with self.assertRaises(ValueError):
            wg.make_theme_config(
                theme_id="t", topic_ja="topic", ledger_path="x.txt",
                voice_cards=[theme_ai_screening.VOICE_CARD_1],
                tension_common_ground_value="g", tension_asymmetry_value="a")
        with self.assertRaises(ValueError):
            wg.make_theme_config(
                theme_id="t", topic_ja="topic", ledger_path="x.txt",
                voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2,
                             theme_ai_screening.VOICE_CARD_3, theme_ai_screening.VOICE_CARD_1],
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


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01-STAGE2:
# 保守版Fact Safetyゲート(段階1/段階2)のテスト(¥0、API呼び出し無し)。
# ============================================================
import er012_b_family_editorial_type_registry_01 as registry  # noqa: E402


class VoiceSafetyGateOptInDefaultOffTests(unittest.TestCase):
    """既定OFF・family=="B"コードレベルgating(is_fact_attribution_mode_
    enabledと同型)。"""

    def test_default_mode_is_on_for_b_family_2026_09_13(self):
        # PM-CLOSEOUT-CONSOLIDATION-105(ユーザー正式判断2026-09-13):
        # B-Family経路で既定ONへ切替(Gate 3項目4/6は次のB-Family実記事
        # 生成時の自然発火待ち、OPEN_ITEMS.md OPEN-120参照)。
        et = registry.get_editorial_type("b_family_voices")
        self.assertTrue(et["voice_fact_safety_gate_mode"])
        self.assertTrue(registry.is_voice_fact_safety_gate_mode_enabled())

    def test_enabled_only_when_family_b_and_flag_true(self):
        et = registry.EDITORIAL_TYPES["b_family_voices"]
        original = et["voice_fact_safety_gate_mode"]
        try:
            et["voice_fact_safety_gate_mode"] = True
            self.assertTrue(registry.is_voice_fact_safety_gate_mode_enabled())
            original_family = et["family"]
            et["family"] = "A"
            try:
                self.assertFalse(registry.is_voice_fact_safety_gate_mode_enabled())
            finally:
                et["family"] = original_family
        finally:
            et["voice_fact_safety_gate_mode"] = original


class VoiceSafetyGateStage1SyntheticTrueGuardTests(unittest.TestCase):
    """段階1: Stage1b-2の合成true-positive(Voice本文だがchanged_fact併発・
    第三者主語・section誤り等)6件が、いずれも降格されない(MAJOR維持)こと。"""

    CASES = [
        ("voice1_changed_fact_combo", "voice_1_body", True, {"changed_scope", "changed_fact"}),
        ("voice2_changed_number_combo", "voice_2_body", True, {"changed_certainty", "changed_number"}),
        ("voice3_changed_actor_combo", "voice_3_body", True, {"changed_scope", "changed_actor"}),
        ("voice1_third_person_subject", "voice_1_body", False, {"changed_scope"}),
        ("tension_mistagged_first_person", "tension_body", True, {"changed_scope"}),
        ("voice2_unsupported_new_claim_combo", "voice_2_body", True,
         {"changed_scope", "changed_certainty", "unsupported_new_claim"}),
    ]

    def test_all_six_synthetic_true_positives_stay_ineligible(self):
        for name, section, first_person, flagset in self.CASES:
            claim = "I have seen this happen many times." if first_person else "The applicant said this happened."
            with self.subTest(name=name):
                self.assertFalse(wg._voice_gate_stage1_eligible(section, claim, flagset))


class VoiceSafetyGateStage2ConservativeSyntheticTrueGuardTests(unittest.TestCase):
    """段階2(保守版): Stage1b-2の合成true-positive11件全件が降格されない
    (MAJOR維持)こと(11/11、取りこぼし0件)。"""

    CASES = [
        ("number_percent", {"changed_actor"}, "Their power is uneven: the owner cut 30% of staff last year."),
        ("propernoun_company", {"unsupported_new_claim"},
         "NBCUniversal decided to end the internal audit program."),
        ("institution_nyc", {"changed_actor"},
         "New York City's new law forced the recruiter to comply immediately."),
        ("thirdparty_lawsuit", {"unsupported_new_claim"},
         "Another applicant filed a lawsuit against the company."),
        ("changed_number_flag_no_digit", {"changed_actor", "changed_number"},
         "The owner now controls most of the hiring team's decisions."),
        ("changed_negation_flag", {"changed_actor", "changed_negation"},
         "The recruiter no longer has any say in the process."),
        ("changed_causality_flag", {"unsupported_new_claim", "changed_causality"},
         "Because the recruiter chose the tool, the owner lost all control."),
        ("changed_comparison_flag", {"changed_actor", "changed_comparison"},
         "The owner has far more power than the recruiter ever will."),
        ("changed_time_flag", {"unsupported_new_claim", "changed_time"},
         "Lately, the recruiter has run the tool without any say."),
        ("combo_number_negation", {"changed_actor", "changed_number", "changed_negation"},
         "The owner no longer approves any open positions."),
        ("wrong_section_hook", {"changed_actor"},
         "The recruiter secretly changed the process without telling anyone."),
    ]

    def test_all_eleven_synthetic_true_positives_stay_ineligible(self):
        for name, flagset, text in self.CASES:
            section = "hook_body" if name == "wrong_section_hook" else "tension_body"
            with self.subTest(name=name):
                self.assertFalse(wg._voice_gate_stage2_eligible(section, text, flagset))


class VoiceSafetyGatePositiveControlTests(unittest.TestCase):
    """安全側だけでなく、意図した対象(段階1: Voice本文hedge、段階2: Tension
    役割合成)が実際に緩和対象と判定されること(false negativeのみの
    ゲートになっていないことの確認)。"""

    def test_stage1_eligible_first_person_certainty_only(self):
        self.assertTrue(wg._voice_gate_stage1_eligible(
            "voice_2_body", "I have come to feel this is generally true for people like me.",
            {"changed_certainty"}))

    def test_stage2_eligible_role_composition_no_surface_signal(self):
        text = ("Their power is uneven: the applicant cannot choose the process; the recruiter runs "
                "it but does not choose adoption; the owner chooses and bears the consequences.")
        self.assertTrue(wg._voice_gate_stage2_eligible("tension_body", text, {"changed_actor"}))


class ApplyBFamilyVoiceSafetyGateEndToEndTests(unittest.TestCase):
    """`_apply_b_family_voice_safety_gate()`全体(section特定+ゲート適用+
    overall_status再計算)のend-to-endテスト。"""

    ARTICLE = """# Title

## The Question

Hook body.

### Voice One

Voice one body. I have come to feel this is generally true for people like me.

### Voice Two

Voice two body.

### Voice Three

Voice three body.

## Tension

Their power is uneven: the applicant cannot choose the process; the recruiter runs it but does not \
choose adoption; the owner chooses and bears the consequences.

## Closing

Closing body.
"""

    def _flags(self, true_keys):
        import er003_v1_en_direct_vfl_01_generate as vfl01
        return {k: (k in true_keys) for k in vfl01.DEVIATION_FLAG_KEYS}

    def test_stage1_and_stage2_eligible_items_downgraded_others_untouched(self):
        parsed = {
            "deviations": [
                {"claim_in_article": "I have come to feel this is generally true for people like me.",
                 "issue": "scope", "severity": "MAJOR", **self._flags({"changed_certainty"})},
                {"claim_in_article": ("Their power is uneven: the applicant cannot choose the process; "
                                       "the recruiter runs it but does not choose adoption; the owner "
                                       "chooses and bears the consequences."),
                 "issue": "actor", "severity": "MAJOR", **self._flags({"changed_actor"})},
                {"claim_in_article": "The applicant said this happened.", "issue": "not-eligible",
                 "severity": "MAJOR", **self._flags({"changed_fact", "changed_scope"})},
                {"claim_in_article": "Already minor.", "issue": "minor", "severity": "MINOR",
                 **self._flags(set())},
            ],
        }
        result = wg._apply_b_family_voice_safety_gate(parsed, self.ARTICLE)
        by_issue = {d["issue"].split("]")[-1].strip() if d["b_family_voice_gate_downgraded"] else d["issue"]:
                    d for d in result["deviations"]}
        downgraded_flags = [d["b_family_voice_gate_downgraded"] for d in result["deviations"]]
        self.assertEqual(downgraded_flags, [True, True, False, False])
        self.assertEqual(result["deviations"][0]["severity"], "MINOR")
        self.assertEqual(result["deviations"][1]["severity"], "MINOR")
        self.assertEqual(result["deviations"][0]["b_family_voice_gate_stage"], "stage1")
        self.assertEqual(result["deviations"][1]["b_family_voice_gate_stage"], "stage2")
        self.assertEqual(result["deviations"][2]["severity"], "MAJOR")
        self.assertEqual(result["deviations"][3]["severity"], "MINOR")

    def test_overall_status_compliant_when_all_major_downgraded_or_absent(self):
        parsed = {
            "deviations": [
                {"claim_in_article": "I have come to feel this is generally true for people like me.",
                 "issue": "scope", "severity": "MAJOR", **self._flags({"changed_certainty"})},
            ],
        }
        result = wg._apply_b_family_voice_safety_gate(parsed, self.ARTICLE)
        self.assertEqual(result["overall_status"], "LEDGER_COMPLIANT")

    def test_overall_status_remains_deviation_when_true_positive_present(self):
        parsed = {
            "deviations": [
                {"claim_in_article": "The applicant said this happened.", "issue": "not-eligible",
                 "severity": "MAJOR", **self._flags({"changed_fact", "changed_scope"})},
            ],
        }
        result = wg._apply_b_family_voice_safety_gate(parsed, self.ARTICLE)
        self.assertEqual(result["overall_status"], "LEDGER_DEVIATION")


class LedgerDeviationAndLocalRewriteGateWiringTests(unittest.TestCase):
    """`run_ledger_deviation_and_local_rewrite()`が、opt-inフラグOFF時は
    完全に無変化(現行の厳格判定のまま)、ON時のみ段階1/2ゲートが実際に
    配線されて効くことを、`vfl01.run_deviation_check`をmock化して確認する
    (¥0、API呼び出し無し)。"""

    ARTICLE = ApplyBFamilyVoiceSafetyGateEndToEndTests.ARTICLE
    TENSION_CLAIM = ("Their power is uneven: the applicant cannot choose the process; the recruiter "
                      "runs it but does not choose adoption; the owner chooses and bears the consequences.")

    def _make_fixed_parsed(self):
        import er003_v1_en_direct_vfl_01_generate as vfl01
        flags = {k: (k == "changed_actor") for k in vfl01.DEVIATION_FLAG_KEYS}
        return {
            "deviations": [{"claim_in_article": self.TENSION_CLAIM, "issue": "actor",
                             "explanation": "actor composite", "severity": "MAJOR", **flags}],
            "overall_status": "LEDGER_DEVIATION",
        }

    def _run(self, out_dir, gate_enabled):
        import unittest.mock as mock
        et = registry.EDITORIAL_TYPES["b_family_voices"]
        original = et["voice_fact_safety_gate_mode"]
        fixed_parsed = self._make_fixed_parsed()
        fake_response = {"parsed": fixed_parsed, "raw_parsed": fixed_parsed}
        try:
            et["voice_fact_safety_gate_mode"] = gate_enabled
            with mock.patch.object(wg.vfl01, "run_deviation_check",
                                    return_value=dict(fake_response)) as mocked, \
                 mock.patch.object(wg.local_rewrite, "locate_target_sentence",
                                    return_value=(None, "not_found")):
                # locate_target_sentenceをmockし、gate OFF時にLocal Rewrite
                # ループへ入っても実際のrewrite API(local_rewrite.rewrite_
                # ng_item)を一切呼ばずにhuman_review_required=Trueで
                # 完結させる(¥0、mock範囲を最小化)。
                result = wg.run_ledger_deviation_and_local_rewrite(
                    client=None, theme_id="t", label="B1B", article_text=self.ARTICLE,
                    verified_ledger_text="dummy ledger", out_dir=out_dir, ledger_model="dummy-model")
        finally:
            et["voice_fact_safety_gate_mode"] = original
        return result, mocked

    def test_gate_off_default_keeps_major_and_triggers_local_rewrite_loop(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            import os
            os.makedirs(f"{tmp}/audit", exist_ok=True)
            result, mocked = self._run(tmp, gate_enabled=False)
        # ゲートOFF: mockが返すMAJORがそのまま残り、Local Rewriteループが
        # 発火する(=API呼び出し回数がcycle上限回数まで増える、既存の
        # 厳格判定と完全に同じ挙動)。
        self.assertEqual(result["ledger_status"], "LEDGER_DEVIATION")
        self.assertGreaterEqual(result["remaining_major_count"], 1)
        self.assertGreater(mocked.call_count, 1, "gate OFF時は現行どおりLocal Rewriteが複数回呼ばれるはず")

    def test_gate_on_downgrades_and_skips_local_rewrite_loop(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            import os
            os.makedirs(f"{tmp}/audit", exist_ok=True)
            result, mocked = self._run(tmp, gate_enabled=True)
        # ゲートON: 段階2条件に一致しMINORへ降格されるため、Local Rewriteは
        # 一度も発火しない(初回の判定1回のみ)。
        self.assertEqual(result["ledger_status"], "LEDGER_COMPLIANT")
        self.assertEqual(result["remaining_major_count"], 0)
        self.assertEqual(mocked.call_count, 1, "gate ON時は初回判定のみでLocal Rewriteは発火しないはず")


class VoiceCardNumberOptionalRenderingTests(unittest.TestCase):
    """2-D: Voice内の数字「必須」要求の撤廃。上限規定(:251-256相当、
    COMMON_INTRO_AND_STRUCTURE_BLOCK_TEMPLATE)は無変更、Voice Card側の
    bulletのみ「使ってください(必須)」から「使える場合に限り」へ変更
    されていること。"""

    def test_voice_card_block_no_longer_mandates_a_number(self):
        card = theme_ai_screening.VOICE_CARD_1
        text = wg._voice_card_block_text(card)
        self.assertNotIn("を織り込んでください(詳細ルールは上記", text)
        self.assertIn("自然に人を主語にした話し言葉へ織り込める場合に限り", text)
        self.assertIn("数字を使わずにその人の実感だけで書いても構いません", text)

    def test_voice_card_block_reference_points_below_not_above(self):
        card = theme_ai_screening.VOICE_CARD_1
        text = wg._voice_card_block_text(card)
        self.assertIn("下記【Evidenceは脇役であること】参照", text)
        self.assertNotIn("上記【Evidenceは脇役であること】参照", text)

    def test_upper_bound_rule_unchanged_max_one_number(self):
        # B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01(2026-09-17、ユーザー
        # 正式承認)で、上限規定(最大1つ)自体は維持したまま、その1つの数字が
        # 「本人の経験に属する数値」に限られるという条件(候補C)を明確化する
        # 見出し・本文へ更新した(意図的な文言変更、上限規定そのものは不変)。
        block = wg.build_focus_module_block_3v(theme_ai_screening.THEME_CONFIG)
        self.assertIn("Voice内の数字は最大1つ・本人の経験に属する数字のみ(重要、", block)
        self.assertIn("最大1つだけにし、かつその数字は必ずその人物自身が実際に経験した数値", block)


if __name__ == "__main__":
    unittest.main()
