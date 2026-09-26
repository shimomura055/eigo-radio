# ============================================================
# er019_family_x_b3_production_wiring_01_test_01.py
# NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01
# ============================================================
# オフラインunit test(実API呼び出しは一切行わない、LLM呼び出しはmock)。
# 対象:
#   - er019_family_x_storyline_b3_fact_selection_01.py(JSON schema検証、
#     Fact ID整合、Fact数>=6時のrecheck_note分岐、Selected Brief生成)
#   - er019_family_x_ja_writer_o_r1_r2_01.py(P7 Prompt verbatim一致、
#     Storyline行差し替え、Selected Fact Brief接続)
#   - er019_family_x_entertainment_production_runner_01.py(stage順序、
#     Full Ledger/Selected Briefのファイル分離、後工程[scaffold/tts/
#     assemble/player]が未実装であること)
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_b3_production_wiring_01_test_01 -v
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er015_news_iterative_entertainment_trial_01 as trial01
import er015_news_original_baseline_repro_01 as repro01
import er019_family_x_entertainment_production_runner_01 as runner
import er019_family_x_ja_writer_o_r1_r2_01 as jaw
import er019_family_x_storyline_b3_fact_selection_01 as b3

SAMPLE_LEDGER_TEXT = """[VERIFIED] FACT-001: Sample claim one.
  scope: global

[VERIFIED] FACT-002: Sample claim two.
  scope: global

[AMBIGUOUS - 断定禁止、曖昧さを保持すること] FACT-003: Sample claim three.
"""


def _make_parsed(selected_ids, all_ids, recheck_note=None, storyline="Sample storyline."):
    fact_tests = []
    for fid in all_ids:
        decision = "selected" if fid in selected_ids else "excluded"
        fact_tests.append({
            "fact_id": fid, "test1_answer": "NO" if decision == "selected" else "YES",
            "test2_answer": "YES" if decision == "selected" else "NO",
            "test3_answer": "YES" if decision == "selected" else "NO",
            "test4_answer": "NO" if decision == "selected" else "YES",
            "decision": decision, "reason": f"reason for {fid}",
        })
    return {
        "selected_storyline": storyline,
        "fact_tests": fact_tests,
        "selected_fact_ids": list(selected_ids),
        "selected_fact_brief": "Brief text referencing " + ", ".join(selected_ids),
        "recheck_note": recheck_note,
    }


class FactIdExtractionTests(unittest.TestCase):
    def test_extract_fact_ids_from_ledger(self):
        ids = b3.extract_fact_ids_from_ledger(SAMPLE_LEDGER_TEXT)
        self.assertEqual(ids, ["FACT-001", "FACT-002", "FACT-003"])


class ValidateSelectionOutputTests(unittest.TestCase):
    def setUp(self):
        self.ledger_ids = ["FACT-001", "FACT-002", "FACT-003"]

    def test_valid_output_no_errors(self):
        parsed = _make_parsed(["FACT-001"], self.ledger_ids)
        errors = b3.validate_selection_output(parsed, self.ledger_ids)
        self.assertEqual(errors, [])

    def test_unknown_fact_id_in_selected_flagged(self):
        parsed = _make_parsed(["FACT-001"], self.ledger_ids)
        parsed["selected_fact_ids"] = ["FACT-999"]
        errors = b3.validate_selection_output(parsed, self.ledger_ids)
        self.assertTrue(any("UNKNOWN_FACT_ID_IN_SELECTED" in e for e in errors))

    def test_unknown_fact_id_in_fact_tests_flagged(self):
        parsed = _make_parsed(["FACT-001"], self.ledger_ids)
        parsed["fact_tests"].append({
            "fact_id": "FACT-GHOST", "test1_answer": "YES", "test2_answer": "NO",
            "test3_answer": "NO", "test4_answer": "YES", "decision": "excluded", "reason": "n/a",
        })
        errors = b3.validate_selection_output(parsed, self.ledger_ids)
        self.assertTrue(any("UNKNOWN_FACT_ID_IN_FACT_TESTS" in e for e in errors))

    def test_missing_ledger_fact_not_tested_flagged(self):
        parsed = _make_parsed(["FACT-001"], ["FACT-001"])  # FACT-002/003を検査していない
        errors = b3.validate_selection_output(parsed, self.ledger_ids)
        self.assertTrue(any("LEDGER_FACT_ID_NOT_TESTED" in e for e in errors))

    def test_selected_fact_ids_mismatch_with_decisions_flagged(self):
        parsed = _make_parsed(["FACT-001"], self.ledger_ids)
        parsed["selected_fact_ids"] = ["FACT-001", "FACT-002"]  # fact_testsのdecisionと不一致
        errors = b3.validate_selection_output(parsed, self.ledger_ids)
        self.assertTrue(any("SELECTED_FACT_IDS_MISMATCH" in e for e in errors))

    def test_six_or_more_selected_without_recheck_note_flagged_as_soft_warning(self):
        many_ids = [f"FACT-{i:03d}" for i in range(1, 7)]
        parsed = _make_parsed(many_ids, many_ids, recheck_note=None)
        errors = b3.validate_selection_output(parsed, many_ids)
        self.assertTrue(any("RECHECK_NOTE_MISSING" in e for e in errors))

    def test_six_or_more_selected_with_recheck_note_not_flagged(self):
        many_ids = [f"FACT-{i:03d}" for i in range(1, 7)]
        parsed = _make_parsed(many_ids, many_ids, recheck_note="All 6 are load-bearing.")
        errors = b3.validate_selection_output(parsed, many_ids)
        self.assertFalse(any("RECHECK_NOTE_MISSING" in e for e in errors))


class RunStorylineB3SelectionTests(unittest.TestCase):
    def _mock_client(self, parsed_sequence):
        client = mock.Mock()
        responses = []
        for parsed in parsed_sequence:
            resp = mock.Mock()
            resp.output_text = json.dumps(parsed)
            resp.model = "gpt-5.6-luna"
            resp.id = "resp_test"
            responses.append(resp)
        client.responses.create.side_effect = responses
        return client

    def test_success_on_first_attempt(self):
        ledger_ids = ["FACT-001", "FACT-002", "FACT-003"]
        parsed = _make_parsed(["FACT-001"], ledger_ids)
        client = self._mock_client([parsed])
        result = b3.run_storyline_b3_selection(
            client, "topic", SAMPLE_LEDGER_TEXT, model="gpt-5.6-luna", effort="high")
        self.assertEqual(result["attempts"], 1)
        self.assertFalse(result["retried"])
        self.assertEqual(result["parsed"]["selected_fact_ids"], ["FACT-001"])

    def test_retries_once_then_succeeds_on_invalid_fact_id(self):
        ledger_ids = ["FACT-001", "FACT-002", "FACT-003"]
        bad = _make_parsed(["FACT-001"], ledger_ids)
        bad["selected_fact_ids"] = ["FACT-999"]
        good = _make_parsed(["FACT-001"], ledger_ids)
        client = self._mock_client([bad, good])
        result = b3.run_storyline_b3_selection(
            client, "topic", SAMPLE_LEDGER_TEXT, model="gpt-5.6-luna", effort="high")
        self.assertEqual(result["attempts"], 2)
        self.assertTrue(result["retried"])

    def test_stops_after_two_failed_attempts(self):
        ledger_ids = ["FACT-001", "FACT-002", "FACT-003"]
        bad = _make_parsed(["FACT-001"], ledger_ids)
        bad["selected_fact_ids"] = ["FACT-999"]
        client = self._mock_client([bad, bad])
        with self.assertRaises(RuntimeError):
            b3.run_storyline_b3_selection(
                client, "topic", SAMPLE_LEDGER_TEXT, model="gpt-5.6-luna", effort="high")


class SelectedBriefMarkdownTests(unittest.TestCase):
    def test_build_selected_brief_markdown_contains_storyline_and_facts(self):
        selection_result = {"parsed": _make_parsed(["FACT-001"], ["FACT-001", "FACT-002"],
                                                     storyline="Storyline line here.")}
        md = b3.build_selected_brief_markdown(selection_result)
        self.assertIn("Storyline line here.", md)
        self.assertIn("Brief text referencing FACT-001", md)


class JaWriterVerbatimTests(unittest.TestCase):
    def test_r0_prompt_verbatim_matches_trial_source(self):
        self.assertEqual(jaw.R0_PROMPT, repro01.R0_PROMPT)

    def test_developer_message_verbatim_matches_trial_source(self):
        self.assertEqual(jaw.DEVELOPER_MESSAGE, repro01.DEVELOPER_MESSAGE)

    def test_revision_instructions_verbatim_match_trial_source(self):
        self.assertEqual(jaw.REVISION_INSTRUCTIONS["r1"], trial01.REVISION_INSTRUCTIONS["r1"])
        self.assertEqual(jaw.REVISION_INSTRUCTIONS["r2"], trial01.REVISION_INSTRUCTIONS["r2"])

    def test_build_original_prompt_replaces_theme_line_and_appends_material(self):
        prompt = jaw.build_original_prompt("Storyline one line.", "Brief text here.")
        self.assertIn("テーマ：Storyline one line.", prompt)
        self.assertNotIn("老朽化する下水道", prompt)
        self.assertIn("[ニュース]\nBrief text here.", prompt)
        # 他の行(長さ・出力形式の指定)は無変更で残っていること。
        self.assertIn("長さ：800～1000字", prompt)
        self.assertIn("出力はタイトルと本文のみ。", prompt)


class JaWriterChainTests(unittest.TestCase):
    def _mock_response(self, text, resp_id, model="gpt-5.6-luna"):
        resp = mock.Mock()
        resp.output_text = text
        resp.id = resp_id
        resp.model = model
        return resp

    def test_chain_uses_previous_response_id_by_default(self):
        client = mock.Mock()
        client.responses.create.side_effect = [
            self._mock_response("# Title\nOriginal body.", "r_o"),
            self._mock_response("Revision1 body.", "r_1"),
            self._mock_response("Revision2 body.", "r_2"),
        ]
        result = jaw.run_ja_writer_o_r1_r2(client, "Storyline.", "Brief.")
        self.assertEqual(result["final_text"], "Revision2 body.")
        self.assertEqual(result["chain_method"], "previous_response_id")
        self.assertEqual(len(client.responses.create.call_args_list), 3)
        # r1呼び出しがprevious_response_idを使っていること
        r1_kwargs = client.responses.create.call_args_list[1].kwargs
        self.assertEqual(r1_kwargs.get("previous_response_id"), "r_o")

    def test_chain_falls_back_to_full_text_on_previous_response_id_failure(self):
        client = mock.Mock()
        original_resp = self._mock_response("# Title\nOriginal body.", "r_o")
        client.responses.create.side_effect = [
            original_resp,
            RuntimeError("previous_response_id not supported"),
            self._mock_response("Revision1 body (fallback).", "r_1b"),
            self._mock_response("Revision2 body (fallback).", "r_2b"),
        ]
        result = jaw.run_ja_writer_o_r1_r2(client, "Storyline.", "Brief.")
        self.assertEqual(result["chain_method"], "fallback_full_text")
        self.assertEqual(result["stages"]["r1"]["chain_method"], "fallback_full_text")
        self.assertEqual(result["final_text"], "Revision2 body (fallback).")


class RunnerStageOrderTests(unittest.TestCase):
    def test_stage_order_constant(self):
        self.assertEqual(runner.STAGE_ORDER,
                          ["research_ledger", "storyline_b3", "writer", "advanced", "standard"])

    def test_stage_aliases_map_research_and_ledger_to_same_stage(self):
        self.assertEqual(runner.STAGE_ALIASES["research"], "research_ledger")
        self.assertEqual(runner.STAGE_ALIASES["ledger"], "research_ledger")

    def test_stop_after_choices_do_not_include_downstream_stages(self):
        parser = runner.build_arg_parser()
        stop_after_action = next(a for a in parser._actions if a.dest == "stop_after")
        self.assertEqual(set(stop_after_action.choices),
                          {"storyline_b3", "writer", "advanced", "standard"})
        for forbidden in ("scaffold", "tts", "assemble", "player"):
            self.assertNotIn(forbidden, stop_after_action.choices)


class RunnerNoDownstreamStagesTests(unittest.TestCase):
    """後工程(scaffold/tts/assemble/player)関連の関数・importが本runnerに
    一切存在しないことを確認する(構造的Mandatory STOPの根拠)。"""

    def test_runner_module_has_no_downstream_functions(self):
        for name in ("run_scaffold_stage", "run_tts_stage", "run_assemble_stage",
                     "build_player_html"):
            self.assertFalse(hasattr(runner, name),
                              f"{name} must not exist on the B3 production runner module")

    def test_runner_source_does_not_import_tts_or_assemble_modules(self):
        with open(runner.__file__, encoding="utf-8") as f:
            source = f.read()
        for forbidden_import in ("er003_v1_n3_01_tts_generate", "er003_v1_n3_01_assemble",
                                  "er003_v1_n3_01_scaffold_generate"):
            self.assertNotIn(forbidden_import, source)


class LedgerAndBriefSeparationTests(unittest.TestCase):
    """Full LedgerとSelected Fact Briefが別ファイルに保存されることを検証する。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_full_ledger_and_selected_brief_are_separate_files(self):
        client = mock.Mock()
        ledger_ids = ["FACT-001", "FACT-002", "FACT-003"]
        parsed = _make_parsed(["FACT-001", "FACT-002"], ledger_ids,
                               storyline="Storyline for separation test.")
        resp = mock.Mock()
        resp.output_text = json.dumps(parsed)
        resp.model = "gpt-5.6-luna"
        resp.id = "resp_sep"
        client.responses.create.return_value = resp

        result = runner.run_storyline_b3(client, "topic", SAMPLE_LEDGER_TEXT, self.tmp_dir)

        full_ledger_path = os.path.join(self.tmp_dir, "storyline_b3", "full_ledger.json")
        brief_path = os.path.join(self.tmp_dir, "storyline_b3", "selected_brief.md")
        self.assertTrue(os.path.exists(full_ledger_path))
        self.assertTrue(os.path.exists(brief_path))
        with open(full_ledger_path, encoding="utf-8") as f:
            full_ledger = json.load(f)
        self.assertIn("ledger_text", full_ledger)
        self.assertEqual(full_ledger["ledger_text"], SAMPLE_LEDGER_TEXT)
        with open(brief_path, encoding="utf-8") as f:
            brief_text = f.read()
        self.assertIn("Storyline for separation test.", brief_text)
        self.assertNotIn(SAMPLE_LEDGER_TEXT, brief_text)
        self.assertEqual(result["selected_storyline"], "Storyline for separation test.")


if __name__ == "__main__":
    unittest.main()
