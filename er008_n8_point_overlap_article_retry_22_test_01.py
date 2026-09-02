# ============================================================
# er008_n8_point_overlap_article_retry_22_test_01.py
# ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22 Item 6/7:
# Point overlap NG時の「記事全体をWriterから再生成する(最大2回)」
# 正式暫定Production方式のrun_one_pattern配線テスト。実LLM呼び出しは
# 行わない(Writer/Fact Checker/Ledger Deviationをすべてmockで置き換え、
# 純粋にretryループの制御フローだけを検証する)。
# ============================================================
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_articles_generate as gen

OVERLAPPING_ARTICLE = """# A Small Habit At The Gate

Passengers have started lining up before boarding even begins. Airline staff say the
queue often forms minutes before the gate agent calls any group. A few travelers say
they simply want to avoid missing a connection.

### Why do people queue this early

Passengers queue early because they fear missing a connection before boarding even
begins. Airline staff and travelers both say the small chance of missing a connection
outweighs the minor cost of lining up minutes before the gate agent calls any group.

### A different kind of signal

Long lines can also signal distrust in how fairly boarding order will be enforced.

## In one line...

People queue early partly out of habit, and partly out of doubt.
"""

CLEAN_ARTICLE = OVERLAPPING_ARTICLE.replace(
    "Passengers queue early because they fear missing a connection before boarding even\n"
    "begins. Airline staff and travelers both say the small chance of missing a connection\n"
    "outweighs the minor cost of lining up minutes before the gate agent calls any group.",
    "Group behavior researchers note that queuing can spread through imitation alone.")


def _fake_writer_result(article_text):
    return {"status": "STRUCTURE_PASS", "raw_text": article_text, "attempts": [{"status": "STRUCTURE_PASS"}]}


def _fake_fact_checker_gates():
    return ({"verdict": "PASS"}, "PASS", [], "fake-model", "fake-response-id", None, [])


def _fake_deviation_result():
    return {"parsed": {"overall_status": "NO_DEVIATION", "deviations": []}}


# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: run_one_patternはPoint Role
# Planning(生成前)・Point Value QA(生成後)を新たに呼ぶようになったため、
# 既存の記事全体retryフロー検証テストでもこの2つをmockする(実LLM呼び出し
# はこのテストの対象外、純粋にretryループの制御フローだけを検証する趣旨は
# 変更しない)。
_FAKE_ROLE_PLAN = {
    "point_one": {f: "x" for f in ["role", "new_listener_takeaway", "evidence_anchor",
                                    "why_it_matters", "must_not_overlap_with_full_story",
                                    "must_not_overlap_with_other_point"]},
    "point_two": {f: "y" for f in ["role", "new_listener_takeaway", "evidence_anchor",
                                    "why_it_matters", "must_not_overlap_with_full_story",
                                    "must_not_overlap_with_other_point"]},
}


def _fake_role_planning_result(*args, **kwargs):
    return {"parsed": _FAKE_ROLE_PLAN, "model": "fake-model", "response_id": "fake-id", "prompt": "fake"}


def _fake_value_qa_pass(*args, **kwargs):
    good_item = {f: "PASS" for f in [
        "qa_not_caveat_only", "qa_not_full_story_paraphrase", "qa_not_other_point_paraphrase",
        "qa_explains_why_it_matters", "qa_specific_not_generic", "qa_adds_new_value"]}
    good_item["reasoning"] = "OK"
    per_point = {"point_one": {"ok": True, "fail_fields": [], "reasoning": "OK"},
                 "point_two": {"ok": True, "fail_fields": [], "reasoning": "OK"}}
    return {"status": "PASS", "per_point": per_point,
            "parsed": {"point_one": good_item, "point_two": good_item}, "model": "fake-model",
            "response_id": "fake-id", "prompt": "fake"}


class RunOnePatternPointOverlapArticleRetryTests(unittest.TestCase):
    def setUp(self):
        self.out_dir = tempfile.mkdtemp(prefix="er008_article_retry_test_")
        self.addCleanup(shutil.rmtree, self.out_dir, ignore_errors=True)
        self.assertFalse(gen.POINT_ONLY_REGENERATION_ENABLED,
                          "Point-only regenerationはER-21で撤去済みのはず(前提が崩れていないか確認)")

    def test_retries_whole_article_and_succeeds_on_second_attempt(self):
        writer_mock = mock.Mock(side_effect=[
            _fake_writer_result(OVERLAPPING_ARTICLE),
            _fake_writer_result(CLEAN_ARTICLE),
        ])
        with mock.patch.object(gen.vfl01, "run_writer_with_technical_retry", writer_mock), \
             mock.patch.object(gen.r3, "build_fact_check_prompt", return_value="fake-prompt"), \
             mock.patch.object(gen.r3, "run_fact_checker_with_gates", return_value=_fake_fact_checker_gates()), \
             mock.patch.object(gen.vfl01, "run_deviation_check", return_value=_fake_deviation_result()), \
             mock.patch.object(gen.point_planning, "run_point_role_planning",
                                side_effect=_fake_role_planning_result), \
             mock.patch.object(gen.point_planning, "run_point_value_qa", side_effect=_fake_value_qa_pass):
            result = gen.run_one_pattern(
                client=object(), theme_id="t1", label="A2",
                prompt="fake prompt", verified_ledger_text="FACT-01: some ledger fact",
                topic="airport lines", out_dir=self.out_dir,
                apply_evidence_compression=False, apply_directional_fact_precheck=False)

        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["point_overlap_article_retry_attempts"], 1)
        self.assertEqual(writer_mock.call_count, 2, "overlap NGで記事全体を1回再生成したはず")
        self.assertIn("Group behavior researchers", result["article_text"])
        self.assertNotIn("outweighs the minor cost of lining up", result["article_text"])

        with open(f"{self.out_dir}/point_overlap_article_retry_log.json", encoding="utf-8") as f:
            log = json.load(f)
        self.assertEqual(len(log), 2)
        self.assertTrue(log[0]["flagged"])
        self.assertFalse(log[1]["flagged"])
        with open(f"{self.out_dir}/article.md", encoding="utf-8") as f:
            saved = f.read()
        self.assertEqual(saved.strip(), CLEAN_ARTICLE.strip(),
                          "最終的に採用された記事(overlap解消後)がarticle.mdへ保存されているはず")

    def test_ng_review_required_after_max_retries_and_skips_fact_checker(self):
        # 3回とも(初回+retry2回)overlapしたままの場合、Fact Checker/Ledger
        # Deviationは一切呼ばれず、コストが発生しないことを確認する。
        writer_mock = mock.Mock(return_value=_fake_writer_result(OVERLAPPING_ARTICLE))
        fact_checker_mock = mock.Mock(return_value=_fake_fact_checker_gates())
        deviation_mock = mock.Mock(return_value=_fake_deviation_result())
        with mock.patch.object(gen.vfl01, "run_writer_with_technical_retry", writer_mock), \
             mock.patch.object(gen.r3, "build_fact_check_prompt", return_value="fake-prompt"), \
             mock.patch.object(gen.r3, "run_fact_checker_with_gates", fact_checker_mock), \
             mock.patch.object(gen.vfl01, "run_deviation_check", deviation_mock), \
             mock.patch.object(gen.point_planning, "run_point_role_planning",
                                side_effect=_fake_role_planning_result), \
             mock.patch.object(gen.point_planning, "run_point_value_qa", side_effect=_fake_value_qa_pass):
            result = gen.run_one_pattern(
                client=object(), theme_id="t1", label="A2",
                prompt="fake prompt", verified_ledger_text="FACT-01: some ledger fact",
                topic="airport lines", out_dir=self.out_dir,
                apply_evidence_compression=False, apply_directional_fact_precheck=False)

        self.assertEqual(result["status"], "NG_REVIEW_REQUIRED")
        self.assertEqual(result["point_overlap_article_retry_attempts"], gen.POINT_OVERLAP_ARTICLE_RETRY_MAX)
        self.assertEqual(writer_mock.call_count, gen.POINT_OVERLAP_ARTICLE_RETRY_MAX + 1,
                          "初回生成+retry2回=合計3回Writerが呼ばれるはず")
        self.assertEqual(fact_checker_mock.call_count, 0, "NG確定時はFact Checkerを呼んではならない(コスト最小化)")
        self.assertEqual(deviation_mock.call_count, 0, "NG確定時はLedger Deviation Checkを呼んではならない")

        with open(f"{self.out_dir}/point_overlap_article_retry_log.json", encoding="utf-8") as f:
            log = json.load(f)
        self.assertEqual(len(log), gen.POINT_OVERLAP_ARTICLE_RETRY_MAX + 1)
        self.assertTrue(all(entry["flagged"] for entry in log))


if __name__ == "__main__":
    unittest.main()
