# ============================================================
# er011_discovery_focus_s2_full_trial_01_test_01.py
# 管理ID: FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01
# ============================================================
# API呼び出しは一切行わない(unittest.mock.patch.objectのみ、実費¥0)。
# 本ファイルはテストのみで、Production/SSOT/Trial本体は編集しない
# (patchはこのテストファイルの中でのみ、テスト実行中だけ有効)。
#
# 検証項目:
#   A. extract_stage1_main_story(純粋関数)の構造検証(正常系/異常系3種)。
#   B. apply_evidence_compression_to_points: EC出力の安全確認(構造破壊時は
#      pre-EC本文へfallbackすること)。
#   C. run_ledger_local_rewrite_loop: MAJOR無し/解決/cycle上限到達+locus
#      分類(main_story側/points側)を、既存local_rewrite関数をmockして検証。
#   D. run_stage2_3_with_retry: retry無し成功/1回retryで成功/上限まで
#      retryしてもNGのまま、の3パターン(Main Storyが固定されたまま
#      再実行されることをmock呼び出し引数で確認)。
#   E. generate_article_stageの分岐(orchestration-level、複合関数を
#      patchして分岐条件そのものを検証): 通常成功/Stage1 QA blocking後
#      regenで成功/Stage1 regen上限到達でNG_REVIEW_REQUIRED/Stage2-3
#      exhaustion後のStage1 fallback成功/最終Ledger MAJORのmain_story
#      locusでStage1 escalation成功/points locusではStage1 escalationせず
#      NG_REVIEW_REQUIRED。
#   F. Production関数のidentity確認(コピー・再実装ではなく同一オブジェクト
#      を呼んでいることの機械確認)。
# ============================================================
from __future__ import annotations

import shutil
import unittest
from unittest import mock

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er008_directional_fact_precheck_08 as dfp
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_discovery_focus_part_a_standalone_trial_01_run as s2_prev
import er011_discovery_focus_s2_full_trial_01 as s2full
import er011_point_role_value_planning_01 as point_planning

TEST_OUT_DIR = "er011_output/discovery_focus_s2_full_trial_01_TEST_TMP"

MAIN_STORY_TEXT_FIXTURE = "This is a fixture Main Story sentence used only for testing. " * 8
TITLE_LINE_FIXTURE = "# A Fixture Title For Testing"

STAGE1_RAW_VALID = (
    f"{TITLE_LINE_FIXTURE}\n\n{MAIN_STORY_TEXT_FIXTURE}\n\n"
    "## In one line (draft)\nA draft closing line for the fixture.\n"
)

POINTS_RAW_FIXTURE = (
    "### A fixture point one heading\n"
    "Point one fixture body text with several plausible words for the automated test suite today.\n\n"
    "### A fixture point two heading\n"
    "Point two fixture body text with several plausible words for the automated test suite today.\n\n"
    "## In one line\nA quiet fixture closing line for the merged article.\n"
)

GOOD_PLAN = {
    "point_one": {"role": "a", "new_listener_takeaway": "b", "evidence_anchor": "c",
                  "why_it_matters": "d", "must_not_overlap_with_full_story": "e",
                  "must_not_overlap_with_other_point": "f"},
    "point_two": {"role": "g", "new_listener_takeaway": "h", "evidence_anchor": "i",
                  "why_it_matters": "j", "must_not_overlap_with_full_story": "k",
                  "must_not_overlap_with_other_point": "l"},
}

CLEAN_OVERLAP_REPORT = {
    "point_one": {"before_overlap": {"flagged": False, "overlap_ratio": 0.1, "shared_words": []}},
    "point_two": {"before_overlap": {"flagged": False, "overlap_ratio": 0.1, "shared_words": []}},
    "point_one_vs_point_two": {"flagged": False},
    "point_two_vs_point_one": {"flagged": False},
}
FLAGGED_OVERLAP_REPORT = {
    "point_one": {"before_overlap": {"flagged": True, "overlap_ratio": 0.9, "shared_words": ["x"]}},
    "point_two": {"before_overlap": {"flagged": False, "overlap_ratio": 0.1, "shared_words": []}},
    "point_one_vs_point_two": {"flagged": False},
    "point_two_vs_point_one": {"flagged": False},
}


def tearDownModule():
    shutil.rmtree(TEST_OUT_DIR, ignore_errors=True)


# ============================================================
# A. extract_stage1_main_story
# ============================================================
class ExtractStage1MainStoryTests(unittest.TestCase):
    def test_valid_structure(self):
        parsed = s2full.extract_stage1_main_story(STAGE1_RAW_VALID)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["title_line"], TITLE_LINE_FIXTURE)
        self.assertIn("fixture Main Story sentence", parsed["main_story_text"])
        self.assertIn("draft closing line", parsed["draft_in_one_line"])
        self.assertNotIn("In one line", parsed["main_story_text"])

    def test_rejects_point_headings_present(self):
        bad = STAGE1_RAW_VALID.replace("## In one line (draft)",
                                        "### A point heading\nbody\n\n## In one line (draft)")
        self.assertIsNone(s2full.extract_stage1_main_story(bad))

    def test_rejects_missing_in_one_line_heading(self):
        bad = f"{TITLE_LINE_FIXTURE}\n\n{MAIN_STORY_TEXT_FIXTURE}\n"
        self.assertIsNone(s2full.extract_stage1_main_story(bad))

    def test_rejects_too_short_main_story(self):
        bad = f"{TITLE_LINE_FIXTURE}\n\nToo short.\n\n## In one line (draft)\nDraft.\n"
        self.assertIsNone(s2full.extract_stage1_main_story(bad))


# ============================================================
# B. apply_evidence_compression_to_points
# ============================================================
class EvidenceCompressionSafetyTests(unittest.TestCase):
    def test_valid_ec_output_is_applied(self):
        with mock.patch.object(ec_editor, "run_lossless_editor",
                                return_value={"raw_text": POINTS_RAW_FIXTURE, "model": "m",
                                              "response_id": "r", "input_tokens": 1, "output_tokens": 1}):
            result = s2full.apply_evidence_compression_to_points(
                client=object(), points_raw_text=POINTS_RAW_FIXTURE, writer_model="m",
                out_dir=TEST_OUT_DIR, attempt=0)
        self.assertTrue(result["applied"])
        self.assertEqual(result["points_text"], POINTS_RAW_FIXTURE.strip())

    def test_ec_output_introducing_title_falls_back(self):
        bad_candidate = "# Unexpected Title\n\n" + POINTS_RAW_FIXTURE
        with mock.patch.object(ec_editor, "run_lossless_editor",
                                return_value={"raw_text": bad_candidate, "model": "m",
                                              "response_id": "r", "input_tokens": 1, "output_tokens": 1}):
            result = s2full.apply_evidence_compression_to_points(
                client=object(), points_raw_text=POINTS_RAW_FIXTURE, writer_model="m",
                out_dir=TEST_OUT_DIR, attempt=1)
        self.assertFalse(result["applied"])
        self.assertEqual(result["points_text"], POINTS_RAW_FIXTURE.strip())

    def test_ec_output_missing_headings_falls_back(self):
        with mock.patch.object(ec_editor, "run_lossless_editor",
                                return_value={"raw_text": "Just prose, no headings at all.", "model": "m",
                                              "response_id": "r", "input_tokens": 1, "output_tokens": 1}):
            result = s2full.apply_evidence_compression_to_points(
                client=object(), points_raw_text=POINTS_RAW_FIXTURE, writer_model="m",
                out_dir=TEST_OUT_DIR, attempt=2)
        self.assertFalse(result["applied"])


# ============================================================
# C. run_ledger_local_rewrite_loop
# ============================================================
def _deviation(major_claims):
    return {"parsed": {"overall_status": "MAJOR_FOUND" if major_claims else "LEDGER_COMPLIANT",
                        "deviations": [{"claim_in_article": c, "issue": "x", "explanation": "x",
                                        "severity": "MAJOR"} for c in major_claims]}}


class LedgerLocalRewriteLoopTests(unittest.TestCase):
    def test_no_major_no_cycle(self):
        with mock.patch.object(vfl01, "run_deviation_check", return_value=_deviation([])):
            result = s2full.run_ledger_local_rewrite_loop(
                object(), "topic", "ledger text", "# T\n\nbody\n", "model", TEST_OUT_DIR, tag="c1")
        self.assertFalse(result["blocking"])
        self.assertEqual(result["local_rewrite_cycles"], [])

    def test_major_resolved_first_cycle(self):
        calls = {"n": 0}

        def deviation_side_effect(client, ledger, article_text, model, hook_aware=True):
            calls["n"] += 1
            return _deviation(["Bad claim sentence."]) if calls["n"] == 1 else _deviation([])

        with mock.patch.object(vfl01, "run_deviation_check", side_effect=deviation_side_effect), \
             mock.patch.object(local_rewrite, "split_sentences", return_value=["Bad claim sentence."]), \
             mock.patch.object(local_rewrite, "locate_target_sentence",
                                return_value=("Bad claim sentence.", "exact")), \
             mock.patch.object(local_rewrite, "extract_point_context", return_value=None), \
             mock.patch.object(local_rewrite, "rewrite_ng_item",
                                return_value={"resolved": True, "human_review_required": False,
                                              "attempts": [], "final_text": "Fixed sentence."}), \
             mock.patch.object(local_rewrite, "apply_diff_qa_to_resolved_rewrite", side_effect=lambda r, *a, **k: r), \
             mock.patch.object(local_rewrite, "apply_rewrites", return_value="# T\n\nFixed sentence.\n"):
            result = s2full.run_ledger_local_rewrite_loop(
                object(), "topic", "ledger text", "# T\n\nBad claim sentence.\n", "model", TEST_OUT_DIR, tag="c2")
        self.assertFalse(result["blocking"])
        self.assertEqual(len(result["local_rewrite_cycles"]), 1)

    def test_major_exhausted_locus_main_story(self):
        with mock.patch.object(vfl01, "run_deviation_check",
                                return_value=_deviation(["Persistent bad claim."])), \
             mock.patch.object(local_rewrite, "split_sentences", return_value=["Persistent bad claim."]), \
             mock.patch.object(local_rewrite, "locate_target_sentence",
                                return_value=("Persistent bad claim.", "exact")), \
             mock.patch.object(local_rewrite, "extract_point_context", return_value=None), \
             mock.patch.object(local_rewrite, "rewrite_ng_item",
                                return_value={"resolved": False, "human_review_required": False,
                                              "attempts": [], "final_text": None}), \
             mock.patch.object(local_rewrite, "apply_diff_qa_to_resolved_rewrite", side_effect=lambda r, *a, **k: r), \
             mock.patch.object(local_rewrite, "apply_rewrites",
                                return_value="# T\n\nPersistent bad claim.\n"):
            result = s2full.run_ledger_local_rewrite_loop(
                object(), "topic", "ledger text", "# T\n\nPersistent bad claim.\n", "model", TEST_OUT_DIR,
                tag="c3", main_story_text_for_locus="# T\n\nPersistent bad claim.\n")
        self.assertTrue(result["blocking"])
        self.assertTrue(result["cycle_exhausted"])
        self.assertEqual(len(result["local_rewrite_cycles"]), local_rewrite.MAX_REWRITE_CYCLES)
        self.assertTrue(result["main_story_locus_unresolved"])

    def test_major_exhausted_locus_points_only(self):
        with mock.patch.object(vfl01, "run_deviation_check",
                                return_value=_deviation(["Persistent bad claim in points."])), \
             mock.patch.object(local_rewrite, "split_sentences",
                                return_value=["Persistent bad claim in points."]), \
             mock.patch.object(local_rewrite, "locate_target_sentence",
                                side_effect=lambda claim, text: (
                                    ("Persistent bad claim in points.", "exact")
                                    if "Points body" in text else (None, "not_found"))), \
             mock.patch.object(local_rewrite, "extract_point_context", return_value=None), \
             mock.patch.object(local_rewrite, "rewrite_ng_item",
                                return_value={"resolved": False, "human_review_required": False,
                                              "attempts": [], "final_text": None}), \
             mock.patch.object(local_rewrite, "apply_diff_qa_to_resolved_rewrite", side_effect=lambda r, *a, **k: r), \
             mock.patch.object(local_rewrite, "apply_rewrites",
                                return_value="# T\n\nMain story text.\n\nPoints body: Persistent bad claim in points.\n"):
            result = s2full.run_ledger_local_rewrite_loop(
                object(), "topic", "ledger text",
                "# T\n\nMain story text.\n\nPoints body: Persistent bad claim in points.\n",
                "model", TEST_OUT_DIR, tag="c4", main_story_text_for_locus="# T\n\nMain story text.\n")
        self.assertTrue(result["blocking"])
        self.assertFalse(result["main_story_locus_unresolved"])


# ============================================================
# D. run_stage2_3_with_retry
# ============================================================
class Stage23RetryTests(unittest.TestCase):
    def _patched(self, overlap_side_effect, value_side_effect=None):
        value_side_effect = value_side_effect or (lambda *a, **k: {"status": "OK"})
        return [
            mock.patch.object(s2_prev, "run_stage2_role_planning",
                               return_value={"parsed": GOOD_PLAN, "model": "m", "response_id": "r",
                                             "prompt": "role planning prompt"}),
            mock.patch.object(s2_prev, "run_stage3_points_writer",
                               return_value={"status": "STRUCTURE_PASS", "raw_text": POINTS_RAW_FIXTURE,
                                             "prompt": "stage3 prompt", "attempts": [], "model": "m",
                                             "response_id": "r"}),
            mock.patch.object(ec_editor, "run_lossless_editor",
                               return_value={"raw_text": POINTS_RAW_FIXTURE, "model": "m", "response_id": "r",
                                             "input_tokens": 1, "output_tokens": 1}),
            mock.patch.object(prod_gen, "run_point_overlap_qa_and_regenerate", side_effect=overlap_side_effect),
            mock.patch.object(point_planning, "run_point_value_qa", side_effect=value_side_effect),
            mock.patch.object(vfl01, "run_writer_with_technical_retry",
                               return_value={"status": "STRUCTURE_PASS", "raw_text": POINTS_RAW_FIXTURE,
                                             "attempts": []}),
        ]

    def test_success_without_retry(self):
        for p in self._patched(lambda *a, **k: {"status": "OK", "report": CLEAN_OVERLAP_REPORT}):
            p.start()
            self.addCleanup(p.stop)
        result = s2full.run_stage2_3_with_retry(
            object(), "topic", "ledger", MAIN_STORY_TEXT_FIXTURE, TITLE_LINE_FIXTURE, "model", TEST_OUT_DIR)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["retry_attempt"], 0)
        self.assertEqual(s2_prev.run_stage2_role_planning.call_count, 1)

    def test_success_after_one_retry(self):
        overlap_calls = {"n": 0}

        def overlap_side_effect(*a, **k):
            overlap_calls["n"] += 1
            return {"status": "OK", "report": FLAGGED_OVERLAP_REPORT if overlap_calls["n"] == 1 else CLEAN_OVERLAP_REPORT}

        for p in self._patched(overlap_side_effect):
            p.start()
            self.addCleanup(p.stop)
        result = s2full.run_stage2_3_with_retry(
            object(), "topic", "ledger", MAIN_STORY_TEXT_FIXTURE, TITLE_LINE_FIXTURE, "model", TEST_OUT_DIR)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["retry_attempt"], 1)
        self.assertEqual(s2_prev.run_stage2_role_planning.call_count, 2)
        # Main Storyは全ての呼び出しでbyte一致(固定されたまま)であることを確認
        for call in s2_prev.run_stage2_role_planning.call_args_list:
            self.assertEqual(call.args[3], MAIN_STORY_TEXT_FIXTURE)

    def test_exhausts_retries_still_ng(self):
        for p in self._patched(lambda *a, **k: {"status": "OK", "report": FLAGGED_OVERLAP_REPORT}):
            p.start()
            self.addCleanup(p.stop)
        result = s2full.run_stage2_3_with_retry(
            object(), "topic", "ledger", MAIN_STORY_TEXT_FIXTURE, TITLE_LINE_FIXTURE, "model", TEST_OUT_DIR)
        self.assertEqual(result["status"], "NG_REVIEW_REQUIRED")
        self.assertEqual(result["retry_attempt"], prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX)


# ============================================================
# E. generate_article_stage分岐(orchestration-level)
# ============================================================
def _stage1_qa_ok(**over):
    base = {"blocking": False, "fact_status": "OK", "fact_verdict": "PASS",
            "ledger_status": "LEDGER_COMPLIANT", "local_rewrite_cycles": [],
            "directional_status": "OK", "title_line": TITLE_LINE_FIXTURE,
            "main_story_text": MAIN_STORY_TEXT_FIXTURE, "article_text": STAGE1_RAW_VALID}
    base.update(over)
    return base


def _stage23_ok(article_text=None):
    article_text = article_text or f"{TITLE_LINE_FIXTURE}\n\n{MAIN_STORY_TEXT_FIXTURE}\n\n{POINTS_RAW_FIXTURE}"
    sections = prod_gen.split_common_sections_for_point_qa(article_text)
    return {"status": "OK", "article_text": article_text, "sections": sections, "retry_attempt": 0,
            "overlap_retry_log": [], "stage2": {}, "stage3": {}}


class GenerateArticleStageBranchTests(unittest.TestCase):
    def _common_patches(self, fc_verdict="PASS", ledger_blocking=False, ledger_locus_unresolved=False):
        merged = f"{TITLE_LINE_FIXTURE}\n\n{MAIN_STORY_TEXT_FIXTURE}\n\n{POINTS_RAW_FIXTURE}"
        return [
            mock.patch.object(s2full, "OUT_DIR", TEST_OUT_DIR),
            mock.patch.object(s2full, "load_reused_ledger_and_topic", return_value=("ledger text", "topic")),
            mock.patch.object(vfl01, "get_client", return_value=object()),
            mock.patch.object(r3, "run_fact_checker_with_gates",
                               return_value=({"verdict": fc_verdict}, "OK", [], "m", "r", None, [])),
            mock.patch.object(dfp, "audit_article_directional_facts", return_value={"overall_status": "OK"}),
            mock.patch.object(s2full, "run_ledger_local_rewrite_loop",
                               return_value={"blocking": ledger_blocking, "article_text": merged,
                                             "ledger_status": "MAJOR_FOUND" if ledger_blocking else "LEDGER_COMPLIANT",
                                             "major_count": 1 if ledger_blocking else 0, "cycle_exhausted": ledger_blocking,
                                             "local_rewrite_cycles": [], "local_rewrite_results": [],
                                             "main_story_locus_unresolved": ledger_locus_unresolved,
                                             "remaining_major_claims": []}),
        ]

    def test_happy_path_ok(self):
        for p in self._common_patches():
            p.start()
            self.addCleanup(p.stop)
        with mock.patch.object(s2full, "run_stage1_main_story_writer",
                                return_value={"status": "STRUCTURE_PASS", "title_line": TITLE_LINE_FIXTURE,
                                              "main_story_text": MAIN_STORY_TEXT_FIXTURE, "attempts": [],
                                              "prompt": "p"}) as stage1_mock, \
             mock.patch.object(s2full, "run_stage1_qa", return_value=_stage1_qa_ok()), \
             mock.patch.object(s2full, "run_stage2_3_with_retry", return_value=_stage23_ok()):
            result = s2full.generate_article_stage("a2")
        self.assertEqual(result["status"], "OK")
        self.assertEqual(stage1_mock.call_count, 1)

    def test_stage1_blocking_then_regen_succeeds(self):
        for p in self._common_patches():
            p.start()
            self.addCleanup(p.stop)
        qa_calls = {"n": 0}

        def qa_side_effect(*a, **k):
            qa_calls["n"] += 1
            return _stage1_qa_ok(blocking=True, reason="stage1_fact_checker_fail") if qa_calls["n"] == 1 \
                else _stage1_qa_ok()

        with mock.patch.object(s2full, "run_stage1_main_story_writer",
                                return_value={"status": "STRUCTURE_PASS", "title_line": TITLE_LINE_FIXTURE,
                                              "main_story_text": MAIN_STORY_TEXT_FIXTURE, "attempts": [],
                                              "prompt": "p"}) as stage1_mock, \
             mock.patch.object(s2full, "run_stage1_qa", side_effect=qa_side_effect), \
             mock.patch.object(s2full, "run_stage2_3_with_retry", return_value=_stage23_ok()):
            result = s2full.generate_article_stage("a2")
        self.assertEqual(result["status"], "OK")
        self.assertEqual(stage1_mock.call_count, 2)

    def test_stage1_blocking_exhausted_returns_ng(self):
        for p in self._common_patches():
            p.start()
            self.addCleanup(p.stop)
        with mock.patch.object(s2full, "run_stage1_main_story_writer",
                                return_value={"status": "STRUCTURE_PASS", "title_line": TITLE_LINE_FIXTURE,
                                              "main_story_text": MAIN_STORY_TEXT_FIXTURE, "attempts": [],
                                              "prompt": "p"}) as stage1_mock, \
             mock.patch.object(s2full, "run_stage1_qa",
                                return_value=_stage1_qa_ok(blocking=True, reason="stage1_ledger_major_unresolved")):
            result = s2full.generate_article_stage("a2")
        self.assertEqual(result["status"], "NG_REVIEW_REQUIRED")
        self.assertEqual(stage1_mock.call_count, s2full.STAGE1_MAX_REGENERATIONS + 1)

    def test_stage23_exhaustion_falls_back_to_stage1_and_succeeds(self):
        for p in self._common_patches():
            p.start()
            self.addCleanup(p.stop)
        stage23_calls = {"n": 0}

        def stage23_side_effect(*a, **k):
            stage23_calls["n"] += 1
            return {"status": "NG_REVIEW_REQUIRED", "article_text": None, "stage": "overlap_value_qa",
                    "retry_attempt": prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX, "overlap_retry_log": []} \
                if stage23_calls["n"] == 1 else _stage23_ok()

        with mock.patch.object(s2full, "run_stage1_main_story_writer",
                                return_value={"status": "STRUCTURE_PASS", "title_line": TITLE_LINE_FIXTURE,
                                              "main_story_text": MAIN_STORY_TEXT_FIXTURE, "attempts": [],
                                              "prompt": "p"}) as stage1_mock, \
             mock.patch.object(s2full, "run_stage1_qa", return_value=_stage1_qa_ok()), \
             mock.patch.object(s2full, "run_stage2_3_with_retry", side_effect=stage23_side_effect):
            result = s2full.generate_article_stage("a2")
        self.assertEqual(result["status"], "OK")
        self.assertEqual(stage1_mock.call_count, 2)

    def test_final_ledger_main_story_locus_escalates_and_succeeds(self):
        merged = f"{TITLE_LINE_FIXTURE}\n\n{MAIN_STORY_TEXT_FIXTURE}\n\n{POINTS_RAW_FIXTURE}"
        loop_calls = {"n": 0}

        def loop_side_effect(*a, **k):
            loop_calls["n"] += 1
            if loop_calls["n"] == 1:
                return {"blocking": True, "article_text": merged, "ledger_status": "MAJOR_FOUND",
                        "major_count": 1, "cycle_exhausted": True, "local_rewrite_cycles": [],
                        "local_rewrite_results": [], "main_story_locus_unresolved": True,
                        "remaining_major_claims": ["x"]}
            return {"blocking": False, "article_text": merged, "ledger_status": "LEDGER_COMPLIANT",
                    "major_count": 0, "cycle_exhausted": False, "local_rewrite_cycles": [],
                    "local_rewrite_results": [], "main_story_locus_unresolved": False,
                    "remaining_major_claims": []}

        patches = [
            mock.patch.object(s2full, "OUT_DIR", TEST_OUT_DIR),
            mock.patch.object(s2full, "load_reused_ledger_and_topic", return_value=("ledger text", "topic")),
            mock.patch.object(vfl01, "get_client", return_value=object()),
            mock.patch.object(r3, "run_fact_checker_with_gates",
                               return_value=({"verdict": "PASS"}, "OK", [], "m", "r", None, [])),
            mock.patch.object(dfp, "audit_article_directional_facts", return_value={"overall_status": "OK"}),
            mock.patch.object(s2full, "run_ledger_local_rewrite_loop", side_effect=loop_side_effect),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        with mock.patch.object(s2full, "run_stage1_main_story_writer",
                                return_value={"status": "STRUCTURE_PASS", "title_line": TITLE_LINE_FIXTURE,
                                              "main_story_text": MAIN_STORY_TEXT_FIXTURE, "attempts": [],
                                              "prompt": "p"}) as stage1_mock, \
             mock.patch.object(s2full, "run_stage1_qa", return_value=_stage1_qa_ok()), \
             mock.patch.object(s2full, "run_stage2_3_with_retry", return_value=_stage23_ok()):
            result = s2full.generate_article_stage("a2")
        self.assertEqual(result["status"], "OK")
        self.assertEqual(stage1_mock.call_count, 2)

    def test_final_ledger_points_locus_does_not_escalate_stays_ng(self):
        merged = f"{TITLE_LINE_FIXTURE}\n\n{MAIN_STORY_TEXT_FIXTURE}\n\n{POINTS_RAW_FIXTURE}"
        patches = [
            mock.patch.object(s2full, "OUT_DIR", TEST_OUT_DIR),
            mock.patch.object(s2full, "load_reused_ledger_and_topic", return_value=("ledger text", "topic")),
            mock.patch.object(vfl01, "get_client", return_value=object()),
            mock.patch.object(r3, "run_fact_checker_with_gates",
                               return_value=({"verdict": "PASS"}, "OK", [], "m", "r", None, [])),
            mock.patch.object(dfp, "audit_article_directional_facts", return_value={"overall_status": "OK"}),
            mock.patch.object(s2full, "run_ledger_local_rewrite_loop",
                               return_value={"blocking": True, "article_text": merged, "ledger_status": "MAJOR_FOUND",
                                             "major_count": 1, "cycle_exhausted": True, "local_rewrite_cycles": [],
                                             "local_rewrite_results": [], "main_story_locus_unresolved": False,
                                             "remaining_major_claims": ["x"]}),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        with mock.patch.object(s2full, "run_stage1_main_story_writer",
                                return_value={"status": "STRUCTURE_PASS", "title_line": TITLE_LINE_FIXTURE,
                                              "main_story_text": MAIN_STORY_TEXT_FIXTURE, "attempts": [],
                                              "prompt": "p"}) as stage1_mock, \
             mock.patch.object(s2full, "run_stage1_qa", return_value=_stage1_qa_ok()), \
             mock.patch.object(s2full, "run_stage2_3_with_retry", return_value=_stage23_ok()):
            result = s2full.generate_article_stage("a2")
        self.assertEqual(result["status"], "NG_REVIEW_REQUIRED")
        self.assertEqual(result["stage"], "final_ledger_major_unresolved")
        self.assertEqual(stage1_mock.call_count, 1)


# ============================================================
# F. Production関数のidentity確認(コピー・再実装でないことの機械確認)
# ============================================================
class ReusedFunctionIdentityTests(unittest.TestCase):
    def test_reused_qa_functions_are_the_same_objects(self):
        self.assertIs(s2full.local_rewrite, local_rewrite)
        self.assertIs(s2full.local_rewrite.rewrite_ng_item, local_rewrite.rewrite_ng_item)
        self.assertIs(s2full.local_rewrite.apply_diff_qa_to_resolved_rewrite,
                       local_rewrite.apply_diff_qa_to_resolved_rewrite)
        self.assertIs(s2full.local_rewrite.locate_target_sentence, local_rewrite.locate_target_sentence)
        self.assertIs(s2full.local_rewrite.extract_point_context, local_rewrite.extract_point_context)
        self.assertIs(s2full.local_rewrite.apply_rewrites, local_rewrite.apply_rewrites)
        self.assertIs(s2full.prod_gen.run_point_overlap_qa_and_regenerate,
                       prod_gen.run_point_overlap_qa_and_regenerate)
        self.assertIs(s2full.prod_gen.split_common_sections_for_point_qa,
                       prod_gen.split_common_sections_for_point_qa)
        self.assertIs(s2full.prod_gen.build_diagnostic_retry_prompt, prod_gen.build_diagnostic_retry_prompt)
        self.assertIs(s2full.point_planning.run_point_value_qa, point_planning.run_point_value_qa)
        self.assertIs(s2full.point_planning.build_role_planning_block, point_planning.build_role_planning_block)
        self.assertIs(s2full.dfp.audit_article_directional_facts, dfp.audit_article_directional_facts)
        self.assertIs(s2full.r3.run_fact_checker_with_gates, r3.run_fact_checker_with_gates)
        self.assertIs(s2full.vfl01.run_deviation_check, vfl01.run_deviation_check)
        self.assertIs(s2full.ec_editor.run_lossless_editor, ec_editor.run_lossless_editor)
        self.assertIs(s2full.s2_prev.run_stage2_role_planning, s2_prev.run_stage2_role_planning)
        self.assertIs(s2full.s2_prev.run_stage3_points_writer, s2_prev.run_stage3_points_writer)
        self.assertIs(s2full.s2_prev.assemble_article, s2_prev.assemble_article)

    def test_retry_caps_match_production_values(self):
        self.assertEqual(prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX, 2)
        self.assertEqual(local_rewrite.MAX_REWRITE_CYCLES, 3)
        self.assertEqual(s2full.STAGE1_MAX_REGENERATIONS, 1)


if __name__ == "__main__":
    unittest.main()
