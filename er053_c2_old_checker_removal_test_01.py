# -*- coding: utf-8 -*-
"""RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2(2026-10-10)。旧Fact Checker撤去の静的test+技術QA維持test(API呼び出し0、費用0円)。

(1) 旧Checker不到達のstatic test: Production経路ファイル(jaw / er012_e / entertainment runner / audio runner / er053 modules)で
    旧Checker関連の識別子・環境変数・文字列が残っていないこと(AST+text)。dangling check scriptのFact Checker専用シンボル残存0。
    初回/retry/fallback/regeneration/resume の各経路でvfl01.run_deviation_checkが呼ばれないことはspy(呼ばれたら失敗)で確認:
    本ファイル(retry/fallback)と er053_c2_wiring_test_01.py(初回/regeneration/resume)。
(2) 技術QA維持: 記号QA(T-01/T-02)・段落retry(T-04)・B3 Fact ID整合(T-17)・台帳verification呼出(T-18)・予算ガード(T-06)が
    従来どおり発火すること(stub)。T-19(注記契約検証)は契約/W-1 testで担保。

実行: .venv/Scripts/python.exe -m pytest er053_c2_old_checker_removal_test_01.py -q
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import er012_e_family_entertainment_two_level_runner_01 as efam
import er019_family_x_entertainment_production_runner_01 as runner
import er019_family_x_ja_writer_o_r1_r2_01 as jaw
import er019_family_x_storyline_b3_fact_selection_01 as b3
import er053_dangling_reference_check_01 as dg

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "er053_output", "risk_flagger_production_wiring_01"))

PROD_FILES = [
    "er012_e_family_entertainment_two_level_runner_01.py",
    "er019_family_x_entertainment_production_runner_01.py",
    "er019_family_x_ja_writer_o_r1_r2_01.py",
    "er019_family_x_audio_production_runner_01.py",
    "er053_family_x_factlock_ja_writer_01.py",
    "er053_risk_flagger_production_01.py",
    "er053_review_queue_01.py",
    "er053_b3_annotation_contract_01.py",
    "er053_en_sentence_splitter_01.py",
]
# 旧Fact Checker専用の識別子(AST上のName/Attribute/関数名/引数名/クラス名として残ってはならない)
DEAD_IDENTS = {
    "run_deviation_check", "JAFactCheckStopError", "JARecheckRequiredError", "_must_fix_from_deviations", "_major_deviations",
    "build_must_fix_block", "original_must_fix", "full_ledger_text", "open243_m1_enabled", "_open243_iol",
    "open243_m1_summary_only_retry", "open243_majors_only_in_summary", "open243_g3_record_translation_minor",
    "deviation_audit_record", "DEVIATION_PROMPT_TEMPLATE", "must_fix_used", "retried_for_deviation", "deviation_overall_status",
    "fact_checks_summary", "JARecheckRequired", "reclassify",
}
DEAD_STRINGS = ["OPEN243_M1", "OPEN243_M2", "OPEN243_G3_TELEMETRY_PATH", "OPEN233_RECLASSIFY_PROTECT_FLAGS",
                "ja_original_check", "ja_r2_check", "ja_recheck", "JA_RECHECK_REQUIRED", "deviation_checks", "deviation_check.json",
                "rejected_advanced_attempt2", "rejected_advanced_m1_summary_retry"]


def _src(f):
    return open(os.path.join(HERE, f), encoding="utf-8").read()


class OldCheckerNotReachableStaticTests(unittest.TestCase):
    def test_no_dead_identifiers_in_ast_of_production_files(self):
        for f in PROD_FILES:
            tree = ast.parse(_src(f))
            found = set()
            for n in ast.walk(tree):
                if isinstance(n, ast.Name):
                    found.add(n.id)
                elif isinstance(n, ast.Attribute):
                    found.add(n.attr)
                elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
                    found.add(n.name)
                elif isinstance(n, ast.arg):
                    found.add(n.arg)
                elif isinstance(n, ast.keyword) and n.arg:
                    found.add(n.arg)
                elif isinstance(n, (ast.Import, ast.ImportFrom)):
                    for a in n.names:
                        found.add(a.name.split(".")[-1])
            self.assertEqual(found & DEAD_IDENTS, set(), f)

    def test_no_dead_strings_or_env_reads_in_production_files(self):
        for f in PROD_FILES:
            src = _src(f)
            for s in DEAD_STRINGS:
                self.assertNotIn(s, src, f"{f}: {s}")
            tree = ast.parse(src)
            for n in ast.walk(tree):
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "os" and n.attr in ("environ", "getenv"):
                    # Production経路の環境変数読取は TTS_EXECUTION_MODE の設定(書込)など既存の技術設定のみ。OPEN243/OPEN233系は無い
                    pass
            self.assertIsNone(re.search(r"environ(\.get)?\(\s*[\"']OPEN2[34]3", src), f)
            self.assertIsNone(re.search(r"getenv\(\s*[\"']OPEN2[34]3", src), f)
            consts = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
            self.assertNotIn("E2E_STUB", consts, f)      # 隠れswitch(コード上の文字列リテラルでの参照)なし(docstring内の言及は対象外)

    def test_production_files_do_not_import_vfl01_deviation_functions(self):
        """vfl01(共有module)はclient取得/ledger構築等で参照してよいが、Deviation Check関数は参照しない。"""
        for f in PROD_FILES:
            for n in ast.walk(ast.parse(_src(f))):
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "vfl01":
                    self.assertNotIn("deviation", n.attr.lower(), f"{f}: vfl01.{n.attr}")

    def test_dangling_script_fact_checker_symbols_are_zero(self):
        res = dg.scan()
        total = sum(sum(c.get(s, 0) for s in dg.SYMBOLS) for c in res["per_file"].values())
        self.assertEqual(total, 0, {f: {k: v for k, v in c.items() if k in dg.SYMBOLS} for f, c in res["per_file"].items()})

    def test_dangling_residual_words_all_classified_none_orphaned(self):
        import gen_dangling_after_c2_01 as gen
        data = gen.classify()
        self.assertEqual(data["unclassified_truly_orphaned"], 0, data["residual_lines"])
        self.assertLess(data["after_c2_total_hits_raw"], data["baseline_c1_total_hits"])
        # 分類済み残件は技術QA語彙とレビュー所見ラベルだけ
        self.assertEqual(set(data["after_c2_residual_by_category"]) - {"technical_qa_vocabulary", "review_label_not_checker",
                                                                       "trial_or_historical", "truly_orphaned"}, set())

    def test_removed_symbols_absent_from_modules(self):
        for mod, names in ((efam, ("JARecheckRequiredError", "_must_fix_from_deviations", "_major_deviations", "open243_m1_enabled",
                                   "_open243_iol", "open243_m1_summary_only_retry", "open243_majors_only_in_summary",
                                   "open243_g3_record_translation_minor", "jaw")),
                           (jaw, ("JAFactCheckStopError", "build_must_fix_block", "_must_fix_from_deviations", "_major_deviations")),
                           (runner, ("jaw",))):
            for n in names:
                self.assertFalse(hasattr(mod, n), f"{mod.__name__}.{n}")

    def test_efam_advanced_in_one_line_is_unconditional_m1a(self):
        import inspect
        self.assertTrue(hasattr(efam, "_advanced_in_one_line"))
        src = inspect.getsource(efam._advanced_in_one_line)
        self.assertIn("ja_text=ja_text", src)
        self.assertIn("ledger_text=ledger_text", src)
        self.assertNotIn("environ", src)
        self.assertNotIn("enabled", src)

    def test_no_hidden_switch_for_checker_in_cli(self):
        for f in ("er019_family_x_entertainment_production_runner_01.py", "er012_e_family_entertainment_two_level_runner_01.py"):
            for n in ast.walk(ast.parse(_src(f))):
                if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.startswith("--"):
                    self.assertIsNone(re.search(r"(checker|fact-check|fact_check|deviation|legacy|m1|m3|b1)", n.value, re.I), f"{f}: {n.value}")


# ---------------------------------------------------------------- retry / fallback の経路spy
def _boom(*a, **k):
    raise AssertionError("旧Checker(vfl01.run_deviation_check)が呼ばれた")


def fake_resp(text, rid="r1"):
    return SimpleNamespace(output_text=text, model="gpt-6-luna", id=rid)


class JawFallbackPathNoCheckerTests(unittest.TestCase):
    """fallback経路(previous_response_id不可 -> fallback_full_text)でも旧Checkerは呼ばれず、技術的fallbackは従来どおり動く(T-03)。"""

    def test_previous_response_id_failure_falls_back_without_checker(self):
        calls = []

        class Responses:
            def create(self, **kw):
                calls.append(kw)
                if "previous_response_id" in kw:
                    raise RuntimeError("previous_response_id unsupported")
                return fake_resp("本文テキストです。", f"r{len(calls)}")

        client = SimpleNamespace(responses=Responses())
        with mock.patch.object(jaw.vfl01, "run_deviation_check", side_effect=_boom):
            r = jaw.run_ja_writer_o_r1_r2(client, "S", "B")
        self.assertEqual(r["chain_method"], "fallback_full_text")
        self.assertEqual(r["stages"]["r1"]["chain_method"], "fallback_full_text")


class EfamRetryPathNoCheckerTests(unittest.TestCase):
    def test_paragraph_retry_and_model_fallback_detected_path_without_checker(self):
        tmp = tempfile.mkdtemp()
        try:
            theme = {"theme_id": "t", "out_dir": os.path.join(tmp, "o"), "topic": "x", "ledger_path": "u"}
            few = SimpleNamespace(title="T", body="one paragraph only", model_id_actual="other-model", model_id_requested="gpt-6-luna",
                                  response_id="a", usage={}, cost_usd=0.0, cost_jpy=0.0, attempts=1, retried=False,
                                  fallback_detected=True, structure_status="STRUCTURE_PASS", elapsed_seconds=0.1)
            ok = SimpleNamespace(**{**few.__dict__, "body": "p1.\n\np2.\n\np3."})
            with mock.patch.object(efam.adv_gen, "generate_family_x_faithful_translation", side_effect=[few, ok]), \
                    mock.patch.object(efam.adv_gen, "generate_family_x_in_one_line", return_value={"text": "x"}), \
                    mock.patch.object(efam.vfl01, "run_deviation_check", side_effect=_boom), \
                    mock.patch.object(efam, "assert_budget_ok", return_value=0.0):
                ev = efam.run_writer_stage(object(), theme, "JA", "L", 300.0, only="advanced")
            self.assertTrue(ev["advanced"]["paragraph_retried"])
            self.assertTrue(ev["advanced"]["fallback_detected"])       # fallback_detected記録(技術QA)は維持
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- 技術QA維持(stub)
class TechnicalQaMaintainedTests(unittest.TestCase):
    def test_T17_b3_fact_id_consistency_still_stops_after_one_retry(self):
        """T-17: B3のFact ID整合(Full Ledgerに存在しないfact_id)は1回retry後もNGならSTOP。"""
        ledger = "[VERIFIED] FACT-001: c1.\n\n[VERIFIED] FACT-002: c2.\n"
        ids = ["FACT-001", "FACT-002"]
        bad = {"selected_storyline": "s", "selected_fact_ids": ["FACT-999"], "selected_fact_brief": "b", "recheck_note": None,
               "fact_tests": [{"fact_id": i, "test1_answer": "NO", "test2_answer": "YES", "test3_answer": "YES", "test4_answer": "NO",
                               "decision": "excluded", "reason": "r"} for i in ids]}
        client = mock.Mock()
        r = mock.Mock()
        r.output_text, r.model, r.id = json.dumps(bad), "gpt-6-luna", "x"
        client.responses.create.side_effect = [r, r]
        with self.assertRaises(RuntimeError):
            b3.run_storyline_b3_selection(client, "topic", ledger, model="gpt-6-luna", effort="high")
        self.assertEqual(client.responses.create.call_count, 2)

    def test_T18_ledger_verification_still_called_in_research_ledger_stage(self):
        """T-18: Research -> Ledger Verification(台帳検証)は従来どおり呼ばれ、台帳が保存される。"""
        tmp = tempfile.mkdtemp()
        try:
            research = {"parsed": {"facts": [{"x": 1}]}, "search_usage": {"web_search_call_count": 1}, "model": "m", "response_id": "r1",
                        "prompt": "p", "raw_text": "t"}
            verification = {"parsed": {"v": 1}, "model": "m", "response_id": "r2", "prompt": "p", "raw_text": "t"}
            with mock.patch.object(runner.efam, "run_researcher_for_topic", return_value=research) as m_r, \
                    mock.patch.object(runner.efam, "run_verification_for_topic", return_value=verification) as m_v, \
                    mock.patch.object(runner.vfl01, "build_verified_ledger_text", return_value=("LEDGER-TEXT", {"VERIFIED": 1}, [1])):
                out = runner.run_research_and_ledger(object(), "topic", os.path.join(tmp, "research_ledger"))
            m_r.assert_called_once()
            m_v.assert_called_once()
            self.assertEqual(out["ledger_text"], "LEDGER-TEXT")
            self.assertTrue(os.path.exists(os.path.join(tmp, "research_ledger", "verified_fact_ledger.txt")))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_T06_budget_guard_fail_closed_and_cap_unchanged(self):
        with mock.patch.object(efam, "compute_cost_jpy_so_far", return_value=(301.0, {})):
            with self.assertRaises(RuntimeError):
                efam.assert_budget_ok("x", 300.0, "n")

    def test_T04_paragraph_retry_constant_and_limit_unchanged(self):
        self.assertEqual(len(efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX), 1)
        self.assertEqual(efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX[0]["issue"], "PARAGRAPH_COUNT_TOO_FEW")

    def test_T01_T02_symbol_qa_functions_exist_in_jaw_and_w1(self):
        import er053_family_x_factlock_ja_writer_01 as w1
        self.assertTrue(hasattr(jaw, "JASymbolCheckStopError"))
        self.assertTrue(hasattr(w1, "JASymbolCheckStopError"))


if __name__ == "__main__":
    unittest.main()
