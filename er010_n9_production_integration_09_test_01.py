# ============================================================
# er010_n9_production_integration_09_test_01.py
# ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09
# ============================================================
# ユーザーが正式採用したLocal Rewrite / Hook-aware Deviation Checker /
# Evidence-bounded Interpretationの3仕様について、実LLM呼び出しを行わず
# (mockのみ)、Production配線の制御フロー・プロンプト内容を検証する。
# Numeric Compression(Case A、既存PRODUCTION_WIRED)については新規実装を
# 行っていないため、本ファイルではテストしない。

import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er010_ledger_local_rewrite_09 as local_rewrite


# ============================================================
# Evidence-bounded Interpretation: prompt内容テスト
# ============================================================
class EvidenceBoundedInterpretationPromptTests(unittest.TestCase):
    def test_instruction_present_in_common_block_template(self):
        self.assertIn("Evidence-bounded Interpretation", gen.COMMON_BLOCK_TEMPLATE)
        self.assertIn("scope", gen.COMMON_BLOCK_TEMPLATE)
        self.assertIn("causality", gen.COMMON_BLOCK_TEMPLATE)
        self.assertIn("certainty", gen.COMMON_BLOCK_TEMPLATE)

    def test_coexists_with_storytelling_first_and_no_jargon(self):
        self.assertIn("Storytelling First", gen.COMMON_BLOCK_TEMPLATE)
        self.assertIn("No Jargon", gen.COMMON_BLOCK_TEMPLATE)
        idx_story = gen.COMMON_BLOCK_TEMPLATE.index("Storytelling First")
        idx_jargon = gen.COMMON_BLOCK_TEMPLATE.index("No Jargon")
        idx_ebi = gen.COMMON_BLOCK_TEMPLATE.index("Evidence-bounded Interpretation")
        idx_structure = gen.COMMON_BLOCK_TEMPLATE.index("記事構成(重要)")
        self.assertLess(idx_story, idx_jargon)
        self.assertLess(idx_jargon, idx_ebi)
        self.assertLess(idx_ebi, idx_structure)

    def test_template_still_formats_without_error(self):
        rendered = gen.COMMON_BLOCK_TEMPLATE.format(
            hanshin_master_full_text="MASTER", topic="TOPIC",
            verified_ledger_text="LEDGER", shared_point_blueprint_block="",
            evidence_compression_block="")
        self.assertIn("Evidence-bounded Interpretation", rendered)


# ============================================================
# Hook-aware Deviation Checker: 既定はFalse、明示的にTrueで新schema/promptを使う
# ============================================================
def _fake_response(payload: dict):
    resp = mock.Mock()
    resp.output_text = json.dumps(payload)
    resp.model = "fake-model"
    resp.id = "fake-response-id"
    return resp


class HookAwareDeviationCheckerTests(unittest.TestCase):
    def test_default_hook_aware_false_uses_normal_prompt_and_schema(self):
        fake_client = mock.Mock()
        fake_client.responses.create.return_value = _fake_response({"deviations": []})
        vfl01.run_deviation_check(fake_client, "LEDGER", "ARTICLE")
        _, kwargs = fake_client.responses.create.call_args
        self.assertEqual(kwargs["text"]["format"]["name"], vfl01.DEVIATION_JSON_SCHEMA["name"])
        developer_msg = kwargs["input"][0]["content"]
        self.assertEqual(developer_msg, vfl01.DEVIATION_DEVELOPER_MESSAGE)
        user_msg = kwargs["input"][1]["content"]
        self.assertNotIn("Hook-aware", user_msg)

    def test_hook_aware_true_uses_hook_prompt_and_schema(self):
        fake_client = mock.Mock()
        fake_client.responses.create.return_value = _fake_response({"deviations": []})
        vfl01.run_deviation_check(fake_client, "LEDGER", "ARTICLE", hook_aware=True)
        _, kwargs = fake_client.responses.create.call_args
        self.assertEqual(kwargs["text"]["format"]["name"], vfl01.HOOK_AWARE_DEVIATION_JSON_SCHEMA["name"])
        user_msg = kwargs["input"][1]["content"]
        self.assertIn("Hook-aware判定", user_msg)
        self.assertIn("changed_scope と changed_comparison", user_msg)

    def test_hook_aware_schema_requires_treated_as_hook_field(self):
        required = vfl01.HOOK_AWARE_DEVIATION_JSON_SCHEMA["schema"]["properties"]["deviations"]["items"]["required"]
        self.assertIn("treated_as_hook", required)
        normal_required = vfl01.DEVIATION_JSON_SCHEMA["schema"]["properties"]["deviations"]["items"]["required"]
        self.assertNotIn("treated_as_hook", normal_required)

    def test_hook_aware_result_preserves_treated_as_hook_through_post_hoc_validation(self):
        fake_client = mock.Mock()
        fake_client.responses.create.return_value = _fake_response({"deviations": [
            {"claim_in_article": "You can always tap custom.", "issue": "certainty",
             "severity": "MAJOR", "changed_fact": False, "changed_scope": False,
             "changed_causality": False, "changed_certainty": True, "changed_number": False,
             "changed_actor": False, "changed_negation": False, "changed_comparison": False,
             "changed_time": False, "unsupported_new_claim": False,
             "explanation": "certainty強化", "treated_as_hook": True},
        ]})
        result = vfl01.run_deviation_check(fake_client, "LEDGER", "ARTICLE", hook_aware=True)
        self.assertEqual(result["parsed"]["overall_status"], "LEDGER_DEVIATION")
        self.assertTrue(result["parsed"]["deviations"][0]["treated_as_hook"])
        self.assertFalse(result["parsed"]["deviations"][0]["auto_downgraded"])
        self.assertTrue(result["hook_aware"])

    def test_hook_aware_still_auto_downgrades_major_with_no_true_flags(self):
        fake_client = mock.Mock()
        fake_client.responses.create.return_value = _fake_response({"deviations": [
            {"claim_in_article": "x", "issue": "y", "severity": "MAJOR",
             **{k: False for k in vfl01.DEVIATION_FLAG_KEYS},
             "explanation": "z", "treated_as_hook": False},
        ]})
        result = vfl01.run_deviation_check(fake_client, "LEDGER", "ARTICLE", hook_aware=True)
        self.assertEqual(result["parsed"]["deviations"][0]["severity"], "MINOR")
        self.assertTrue(result["parsed"]["deviations"][0]["auto_downgraded"])
        self.assertEqual(result["parsed"]["overall_status"], "LEDGER_COMPLIANT")


# ============================================================
# Local Rewrite module: locate_target_sentence / rewrite_ng_item / apply_rewrites
# ============================================================
class LocateTargetSentenceTests(unittest.TestCase):
    def test_exact_substring_match(self):
        article = "First sentence here. The tip rate always rises after screens appear. Last one."
        target, method = local_rewrite.locate_target_sentence(
            "The tip rate always rises after screens appear.", article)
        self.assertEqual(target, "The tip rate always rises after screens appear.")
        self.assertEqual(method, "exact_substring")

    def test_fuzzy_fallback_above_threshold(self):
        article = "Intro sentence. Tip rates always rise sharply after digital screens appear widely. End."
        target, method = local_rewrite.locate_target_sentence(
            "Tip rates always rise after screens appear.", article)
        self.assertIsNotNone(target)
        self.assertTrue(method.startswith("sentence_fallback"))

    def test_not_found_below_threshold(self):
        article = "Completely unrelated content about vegetable crispers and humidity levels."
        target, method = local_rewrite.locate_target_sentence(
            "The tip rate always rises after screens appear.", article)
        self.assertIsNone(target)
        self.assertEqual(method, "not_found")


class RewriteNgItemTests(unittest.TestCase):
    def _fake_text_response(self, text):
        resp = mock.Mock()
        resp.output_text = text
        return resp

    def test_resolved_on_first_attempt(self):
        fake_client = mock.Mock()
        fake_client.responses.create.return_value = self._fake_text_response("Tip rates can rise after screens appear.")
        check_fn = mock.Mock(return_value={"overall_status": "LEDGER_COMPLIANT"})
        deviation = {"issue": "certainty強化", "explanation": "one-time finding generalized",
                     "changed_certainty": True}
        result = local_rewrite.rewrite_ng_item(
            fake_client, "fake-model", "medium", "LEDGER TEXT",
            "Tip rates always rise after screens appear.", deviation, "before.", "after.", check_fn)
        self.assertTrue(result["resolved"])
        self.assertFalse(result["human_review_required"])
        self.assertEqual(len(result["attempts"]), 1)
        self.assertEqual(fake_client.responses.create.call_count, 1)

    def test_escalates_and_flags_human_review_after_three_failed_attempts(self):
        fake_client = mock.Mock()
        fake_client.responses.create.side_effect = [
            self._fake_text_response("attempt1 text"),
            self._fake_text_response("attempt2 text"),
            self._fake_text_response("attempt3 text"),
        ]
        check_fn = mock.Mock(return_value={"overall_status": "LEDGER_DEVIATION"})
        deviation = {"issue": "certainty強化", "explanation": "explanation", "changed_certainty": True}
        result = local_rewrite.rewrite_ng_item(
            fake_client, "fake-model", "medium", "LEDGER TEXT",
            "Tip rates always rise after screens appear.", deviation, "before.", "after.", check_fn)
        self.assertFalse(result["resolved"])
        self.assertTrue(result["human_review_required"])
        self.assertEqual(len(result["attempts"]), local_rewrite.MAX_REWRITE_ATTEMPTS)
        self.assertEqual(fake_client.responses.create.call_count, 3)
        self.assertEqual(result["final_text"], "attempt3 text")

    def test_only_targets_flagged_sentence_prompt_content(self):
        fake_client = mock.Mock()
        fake_client.responses.create.return_value = self._fake_text_response("fixed sentence")
        check_fn = mock.Mock(return_value={"overall_status": "LEDGER_COMPLIANT"})
        deviation = {"issue": "certainty強化", "explanation": "explanation", "changed_certainty": True}
        local_rewrite.rewrite_ng_item(
            fake_client, "fake-model", "medium", "LEDGER TEXT",
            "Tip rates always rise.", deviation, "before.", "after.", check_fn)
        _, kwargs = fake_client.responses.create.call_args
        self.assertEqual(kwargs["input"][0]["content"], local_rewrite.REWRITE_SYSTEM_PROMPT)
        self.assertIn("Do NOT introduce a new fact", local_rewrite.REWRITE_SYSTEM_PROMPT)
        self.assertIn("Modify ONLY the flagged sentence", local_rewrite.REWRITE_SYSTEM_PROMPT)


class ApplyRewritesTests(unittest.TestCase):
    def test_replaces_original_sentence_with_final_text(self):
        article = "Intro. Tip rates always rise after screens appear. Conclusion."
        rewrite_results = [{"original_ng_sentence": "Tip rates always rise after screens appear.",
                             "final_text": "Tip rates can rise after screens appear."}]
        updated = local_rewrite.apply_rewrites(article, rewrite_results)
        self.assertIn("Tip rates can rise after screens appear.", updated)
        self.assertNotIn("Tip rates always rise after screens appear.", updated)

    def test_skips_when_final_text_missing(self):
        article = "Intro. Some sentence. Conclusion."
        rewrite_results = [{"original_ng_sentence": "Some sentence.", "final_text": None}]
        updated = local_rewrite.apply_rewrites(article, rewrite_results)
        self.assertEqual(updated, article)


# ============================================================
# run_one_pattern配線テスト(実LLM呼び出しなし、Writer/Fact Checker/
# Ledger Deviation/局所Rewriteをすべてmockし、制御フローのみ検証)
# ============================================================
ARTICLE_WITH_MAJOR = """# A Screen Before Every Tip

Digital tip screens now appear at many checkouts. The tip rate always rises after screens appear.

### Why this pattern shows up

Researchers noticed a jump right around a key price point.

### A second angle

Some customers say the pressure feels different in person.

## In one line...

A small design choice can change what people pay.
"""

REWRITTEN_ARTICLE = ARTICLE_WITH_MAJOR.replace(
    "The tip rate always rises after screens appear.",
    "In this study, the tip rate rose after screens appeared.")


def _fake_writer_result(article_text):
    return {"status": "STRUCTURE_PASS", "raw_text": article_text, "attempts": [{"status": "STRUCTURE_PASS"}]}


def _fake_fact_checker_gates():
    return ({"verdict": "PASS"}, "PASS", [], "fake-model", "fake-response-id", None, [])


def _fake_point_overlap_no_flag(*args, **kwargs):
    return {"status": "OK", "report": {
        "point_one": {"before_overlap": {"flagged": False, "overlap_ratio": 0.1}},
        "point_two": {"before_overlap": {"flagged": False, "overlap_ratio": 0.1}},
    }}


def _major_deviation_result():
    return {"parsed": {"overall_status": "LEDGER_DEVIATION", "deviations": [
        {"claim_in_article": "The tip rate always rises after screens appear.",
         "issue": "certainty強化", "explanation": "一度限りの結果をalwaysへ一般化",
         "severity": "MAJOR", "changed_certainty": True, "changed_fact": False,
         "changed_scope": False, "changed_causality": False, "changed_number": False,
         "changed_actor": False, "changed_negation": False, "changed_comparison": False,
         "changed_time": False, "unsupported_new_claim": False, "treated_as_hook": False,
         "auto_downgraded": False},
    ]}}


def _compliant_deviation_result():
    return {"parsed": {"overall_status": "LEDGER_COMPLIANT", "deviations": []}}


class RunOnePatternLocalRewriteWiringTests(unittest.TestCase):
    def setUp(self):
        self.out_dir = tempfile.mkdtemp(prefix="er010_local_rewrite_test_")
        self.addCleanup(shutil.rmtree, self.out_dir, ignore_errors=True)

    def test_major_deviation_triggers_local_rewrite_and_resolves(self):
        writer_mock = mock.Mock(return_value=_fake_writer_result(ARTICLE_WITH_MAJOR))
        deviation_mock = mock.Mock(side_effect=[_major_deviation_result(), _compliant_deviation_result(),
                                                 _compliant_deviation_result()])
        with mock.patch.object(gen.vfl01, "run_writer_with_technical_retry", writer_mock), \
             mock.patch.object(gen, "run_point_overlap_qa_and_regenerate", side_effect=_fake_point_overlap_no_flag), \
             mock.patch.object(gen.r3, "build_fact_check_prompt", return_value="fake-prompt"), \
             mock.patch.object(gen.r3, "run_fact_checker_with_gates", return_value=_fake_fact_checker_gates()), \
             mock.patch.object(gen.vfl01, "run_deviation_check", deviation_mock), \
             mock.patch.object(gen.local_rewrite, "rewrite_ng_item", return_value={
                 "original_ng_sentence": "The tip rate always rises after screens appear.",
                 "issue": "certainty強化", "explanation": "x", "flags": ["changed_certainty"],
                 "attempts": [{"attempt": 1, "text": "In this study, the tip rate rose after screens appeared.",
                               "ledger_status": "LEDGER_COMPLIANT"}],
                 "final_text": "In this study, the tip rate rose after screens appeared.",
                 "resolved": True, "human_review_required": False,
             }):
            result = gen.run_one_pattern(
                client=object(), theme_id="t1", label="A2",
                prompt="fake prompt", verified_ledger_text="FACT-01: some ledger fact",
                topic="tip screens", out_dir=self.out_dir,
                apply_evidence_compression=False, apply_directional_fact_precheck=False)

        self.assertEqual(result["status"], "OK")
        self.assertEqual(len(result["local_rewrite_results"]), 1)
        self.assertTrue(result["local_rewrite_results"][0]["resolved"])
        self.assertIn("In this study, the tip rate rose after screens appeared.", result["article_text"])
        self.assertNotIn("The tip rate always rises after screens appear.", result["article_text"])
        # Hook-aware判定が使われたことを確認(全deviation呼び出しでhook_aware=Trueが渡されている)
        for call in deviation_mock.call_args_list:
            self.assertTrue(call.kwargs.get("hook_aware"))

    def test_unresolved_major_after_rewrite_returns_ng_review_required_and_skips_directional_precheck(self):
        writer_mock = mock.Mock(return_value=_fake_writer_result(ARTICLE_WITH_MAJOR))
        deviation_mock = mock.Mock(side_effect=[_major_deviation_result(), _major_deviation_result()])
        directional_mock = mock.Mock()
        with mock.patch.object(gen.vfl01, "run_writer_with_technical_retry", writer_mock), \
             mock.patch.object(gen, "run_point_overlap_qa_and_regenerate", side_effect=_fake_point_overlap_no_flag), \
             mock.patch.object(gen.r3, "build_fact_check_prompt", return_value="fake-prompt"), \
             mock.patch.object(gen.r3, "run_fact_checker_with_gates", return_value=_fake_fact_checker_gates()), \
             mock.patch.object(gen.vfl01, "run_deviation_check", deviation_mock), \
             mock.patch.object(gen.dfp, "audit_article_directional_facts", directional_mock), \
             mock.patch.object(gen.local_rewrite, "rewrite_ng_item", return_value={
                 "original_ng_sentence": "The tip rate always rises after screens appear.",
                 "issue": "certainty強化", "explanation": "x", "flags": ["changed_certainty"],
                 "attempts": [{"attempt": i, "text": "still bad", "ledger_status": "LEDGER_DEVIATION"}
                              for i in range(1, 4)],
                 "final_text": "still bad", "resolved": False, "human_review_required": True,
             }):
            result = gen.run_one_pattern(
                client=object(), theme_id="t1", label="A2",
                prompt="fake prompt", verified_ledger_text="FACT-01: some ledger fact",
                topic="tip screens", out_dir=self.out_dir,
                apply_evidence_compression=False, apply_directional_fact_precheck=True)

        self.assertEqual(result["status"], "NG_REVIEW_REQUIRED")
        directional_mock.assert_not_called()
        self.assertTrue(result["local_rewrite_results"][0]["human_review_required"])

    def test_no_major_skips_local_rewrite_entirely(self):
        writer_mock = mock.Mock(return_value=_fake_writer_result(ARTICLE_WITH_MAJOR))
        deviation_mock = mock.Mock(return_value=_compliant_deviation_result())
        rewrite_mock = mock.Mock()
        with mock.patch.object(gen.vfl01, "run_writer_with_technical_retry", writer_mock), \
             mock.patch.object(gen, "run_point_overlap_qa_and_regenerate", side_effect=_fake_point_overlap_no_flag), \
             mock.patch.object(gen.r3, "build_fact_check_prompt", return_value="fake-prompt"), \
             mock.patch.object(gen.r3, "run_fact_checker_with_gates", return_value=_fake_fact_checker_gates()), \
             mock.patch.object(gen.vfl01, "run_deviation_check", deviation_mock), \
             mock.patch.object(gen.local_rewrite, "rewrite_ng_item", rewrite_mock):
            result = gen.run_one_pattern(
                client=object(), theme_id="t1", label="A2",
                prompt="fake prompt", verified_ledger_text="FACT-01: some ledger fact",
                topic="tip screens", out_dir=self.out_dir,
                apply_evidence_compression=False, apply_directional_fact_precheck=False)

        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["local_rewrite_results"], [])
        rewrite_mock.assert_not_called()
        # deviation checkはinitialの1回のみ(局所Rewriteが発火しないので最終再判定は無い)
        self.assertEqual(deviation_mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
