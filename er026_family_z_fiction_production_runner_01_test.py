# ============================================================
# er026_family_z_fiction_production_runner_01_test.py
# 管理ID: FICTION-FAMILY-Z-PRODUCTION-E2E-01 (Phase 1)
# ============================================================
# 本委任(Phase 1)の新規テストファイル単独実行を正式根拠とする(全体
# regressionは並走Agent[読み解決Phase2/Family X Stage3c]のTTS実行と
# 並行のため本委任では未実施、次Phaseで実施)。¥0(API呼び出しなし、
# dry-run/純粋関数のみを対象とする)。
# ============================================================
import os
import shutil
import unittest

import er020_tts_retry_local_rewrite_01 as tts_role
import er026_family_z_fiction_production_runner_01 as runner


class RightsGateTest(unittest.TestCase):
    def test_positive_melos_rights_block_passes(self):
        runner.check_rights_gate(runner.MELOS_RIGHTS_BLOCK)  # raiseしなければPASS

    def test_negative_missing_field_fails_closed(self):
        broken = dict(runner.MELOS_RIGHTS_BLOCK)
        broken["jp_public_domain_basis"] = ""
        with self.assertRaises(runner.RightsGateError):
            runner.check_rights_gate(broken)

    def test_negative_missing_multiple_fields(self):
        broken = {"author": "x"}
        with self.assertRaises(runner.RightsGateError):
            runner.check_rights_gate(broken)


class CanonicalTextTest(unittest.TestCase):
    def test_trial_text_fails_name_rule_before_edit(self):
        loaded = runner.load_trial_seed_and_story("melos")
        _title, body = runner.strip_markdown_title(loaded["raw_trial_text"])
        ok, missing = runner.check_character_name_rule(body)
        self.assertFalse(ok)
        self.assertIn("Selinuntius", missing)
        self.assertIn("Dionysius", missing)

    def test_resolve_canonical_text_restores_names_and_passes_gates(self):
        result = runner.resolve_canonical_text("melos")
        self.assertTrue(result["word_count_ok"], result["word_count"])
        self.assertTrue(result["character_name_rule_ok"], result["missing_names_after"])
        self.assertIn("Selinuntius", result["body"])
        self.assertIn("Dionysius", result["body"])
        self.assertEqual(len(result["edits"]), 1)
        self.assertEqual(result["edits"][0]["method"], "deterministic_text_substitution_no_llm")
        # 語数はほぼ変わらない(名前の付記のみ、+数語程度)
        self.assertTrue(280 <= result["word_count"] <= 420)

    def test_word_count_range_boundaries(self):
        ok, n = runner.check_word_count(" ".join(["word"] * 280))
        self.assertTrue(ok)
        ok, n = runner.check_word_count(" ".join(["word"] * 279))
        self.assertFalse(ok)
        ok, n = runner.check_word_count(" ".join(["word"] * 420))
        self.assertTrue(ok)
        ok, n = runner.check_word_count(" ".join(["word"] * 421))
        self.assertFalse(ok)


class SegmentPlanConnectedSpeechMappingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical = runner.resolve_canonical_text("melos")
        cls.plan = runner.build_segment_plan(
            cls.canonical["body"], runner.STORY_REGISTRY["melos"]["voice_keywords"])

    def test_reconstruction_matches_canonical_text(self):
        self.assertTrue(self.plan["reconstruction_matches_canonical_text"])

    def test_first_three_positions_map_to_full_story_role(self):
        rows = {r["position"]: r for r in self.plan["segment_id_role_map"]}
        for pos in (1, 2, 3):
            self.assertIn(pos, rows)
            self.assertEqual(rows[pos]["proposed_segment_id"], f"full_story_part{pos}")
            self.assertEqual(rows[pos]["resolved_role"], "FULL_STORY")
            self.assertTrue(rows[pos]["connected_speech_enabled"])

    def test_positions_beyond_three_have_no_resolved_role(self):
        rows = [r for r in self.plan["segment_id_role_map"] if r["position"] > 3]
        self.assertTrue(len(rows) > 0, "このrunでは8segmentある想定(4件以上がposition>3)")
        for r in rows:
            self.assertIsNone(r["resolved_role"])
            self.assertFalse(r["connected_speech_enabled"])
            self.assertEqual(r["proposed_segment_id"], r["raw_segment_id"])

    def test_known_gap_resolved_by_er020_family_z_clip_pattern(self):
        # 委任_05: 新仕様。委任_03のer020 _FAMILY_Z_STORY_CLIP_PATTERN により full_story_part{1-3}_c{k} が
        # FULL_STORY(connected speech=True)と解決されるため、旧known_gap(position>3が未解決)は解消扱い。
        self.assertIsNone(self.plan["known_gap"])
        self.assertTrue(self.plan["known_gap_status"].startswith("RESOLVED_BY_ER020_FAMILY_Z_CLIP_PATTERN"))
        for i in ("full_story_part1_c1", "full_story_part2_c9", "full_story_part3_c30"):
            self.assertEqual(tts_role.resolve_narrative_role(i), "FULL_STORY")
            self.assertTrue(tts_role.connected_speech_enabled_for(i))
        # 旧命名(story_XXX)は引き続き未解決(旧mappingの事実記録は残す)
        self.assertIsNone(tts_role.resolve_narrative_role("story_004"))

    def test_resolve_narrative_role_import_is_read_only_reference(self):
        # er020側の挙動を直接確認する(本テストはer020を一切編集しない、
        # importのみのread-only参照であることの確認)。
        self.assertEqual(tts_role.resolve_narrative_role("full_story_part1"), "FULL_STORY")
        self.assertIsNone(tts_role.resolve_narrative_role("story_004"))


class FixedSegmentRoleMapTest(unittest.TestCase):
    def test_preview_comment_topic_intro_in_one_line_all_resolve(self):
        rows = {r["segment_id"]: r for r in runner.build_fixed_segment_role_map()}
        expected_roles = {
            "topic_intro": "TOPIC_INTRO", "preview": "PREVIEW",
            "comment_1": "COMMENT", "in_one_line": "IN_ONE_LINE",
        }
        for seg_id, role in expected_roles.items():
            self.assertEqual(rows[seg_id]["resolved_role"], role)
            self.assertTrue(rows[seg_id]["connected_speech_enabled"])


class StoryTypeMetadataTest(unittest.TestCase):
    def test_literature_has_no_ui_label_or_audio_intro(self):
        meta = runner.build_story_type_metadata("literature")
        self.assertIsNone(meta["ui_label"])
        self.assertIsNone(meta["fixed_audio_intro_text"])

    def test_real_story_and_true_crime_have_fixed_intro(self):
        meta = runner.build_story_type_metadata("real_story")
        self.assertEqual(meta["ui_label"], "REAL STORY")
        self.assertEqual(meta["fixed_audio_intro_text"], "This is a true story.")
        meta = runner.build_story_type_metadata("true_crime")
        self.assertEqual(meta["ui_label"], "TRUE CRIME")

    def test_unknown_story_type_raises(self):
        with self.assertRaises(RuntimeError):
            runner.build_story_type_metadata("not_a_real_type")


class DryRunZeroSideEffectTest(unittest.TestCase):
    OUT_DIR = runner.out_dir_for("melos_dryrun_test", "run_test")

    def setUp(self):
        if os.path.exists(self.OUT_DIR):
            shutil.rmtree(self.OUT_DIR)

    def tearDown(self):
        if os.path.exists(self.OUT_DIR):
            shutil.rmtree(self.OUT_DIR)

    def test_dry_run_writes_no_files_and_calls_no_api(self):
        result = runner.run_text_stage("melos", "melos_dryrun_test", "run_test", dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertIsNone(result["preview"])
        self.assertIsNone(result["comment_1"])
        self.assertIsNone(result["in_one_line"])
        self.assertNotIn("budget", result)
        self.assertFalse(os.path.exists(self.OUT_DIR), "dry-runは副作用ゼロ契約のためファイルを作らない")

    def test_keyphrase_stage_dry_run_is_noop(self):
        result = runner.run_keyphrase_stage("melos", "melos_dryrun_test", "run_test", dry_run=True)
        self.assertTrue(result["dry_run"])


class TtsAssembleStagesImplementedTest(unittest.TestCase):
    """委任_05: stage_tts/stage_assemble はNotImplementedErrorスタブではなく実装済み(E2E stage)。"""

    def test_stage_tts_and_assemble_are_implemented_not_stubs(self):
        import inspect
        for fn in (runner.stage_tts, runner.stage_assemble):
            self.assertNotIn("NotImplementedError", inspect.getsource(fn))
        self.assertIn("tts_b1b", runner.E2E_STAGES)
        self.assertIn("tts_a2", runner.E2E_STAGES)
        self.assertIn("assemble", runner.E2E_STAGES)

    def test_old_name_rule_functions_are_marked_superseded(self):
        self.assertIn("SUPERSEDED", runner.check_character_name_rule.__doc__)
        self.assertIn("SUPERSEDED", runner.restore_character_names.__doc__)

    def test_run_text_stage_uses_er061_not_old_name_rule(self):
        import inspect
        src = inspect.getsource(runner.run_text_stage)
        self.assertNotIn("check_character_name_rule", src)
        self.assertNotIn("restore_character_names", src)
        self.assertIn("resolve_canonical_text_v2", src)
        v2 = runner.resolve_canonical_text_v2("melos")
        self.assertIn(v2["layer1_verdict"], ("PASS", "WARN"))
        self.assertEqual(v2["edits"], [])
        self.assertEqual(v2["trial_sha256"], v2["final_sha256"])  # Trial本文は改変しない


if __name__ == "__main__":
    unittest.main()
