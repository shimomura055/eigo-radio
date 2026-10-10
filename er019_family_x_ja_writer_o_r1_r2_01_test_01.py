# ============================================================
# er019_family_x_ja_writer_o_r1_r2_01_test_01.py
# NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01
# ============================================================
# er019_family_x_ja_writer_o_r1_r2_01.pyの単体テスト。実API呼び出しは
# 行わない(writer呼び出しはfake client)。C2で旧Fact Check系testを削除し、
# 維持対象の記号QA(技術QA)testと旧Checker不到達testに置換した。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_ja_writer_o_r1_r2_01_test_01 -v
# ============================================================
from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest import mock

import er019_family_x_ja_writer_o_r1_r2_01 as jaw


def _fake_response(text: str, model: str = "gpt-5.6-luna", response_id: str = "resp_1"):
    return SimpleNamespace(output_text=text, model=model, id=response_id)


class _FakeResponses:
    def __init__(self, outputs):
        self._outputs = list(outputs)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        item = self._outputs.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class _FakeClient:
    def __init__(self, outputs):
        self.responses = _FakeResponses(outputs)


class FactCheckRemovedTests(unittest.TestCase):
    """RISK-FLAGGER-PRODUCTION-WIRING-01 C2(2026-10-10): 旧Fact Checker(Original直後/R2直後の台帳照合・
    指摘起点の再生成・Fact用STOP例外)は物理削除済み。Luna連鎖(Trial互換)は3回のcallで完結する。"""

    def test_chain_makes_exactly_three_calls_and_never_calls_old_checker(self):
        client = _FakeClient([
            _fake_response("Original text", response_id="r_orig"),
            _fake_response("R1 text", response_id="r_r1"),
            _fake_response("R2 text", response_id="r_r2"),
        ])
        with mock.patch.object(jaw.vfl01, "run_deviation_check", side_effect=AssertionError("old checker")) as m_check:
            result = jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief text")
        m_check.assert_not_called()
        self.assertEqual(len(client.responses.calls), 3)
        self.assertEqual(result["final_text"], "R2 text")
        self.assertNotIn("fact_checks", result)

    def test_removed_symbols_are_gone(self):
        for name in ("build_must_fix_block", "JAFactCheckStopError", "_major_deviations", "_must_fix_from_deviations"):
            self.assertFalse(hasattr(jaw, name), name)

    def test_build_original_prompt_has_no_fact_check_args(self):
        import inspect
        params = list(inspect.signature(jaw.build_original_prompt).parameters)
        self.assertEqual(params, ["storyline_line", "selected_fact_brief_text"])
        self.assertEqual(list(inspect.signature(jaw.run_ja_writer_o_r1_r2).parameters),
                         ["client", "storyline_line", "selected_fact_brief_text"])


class SymbolQaMaintainedTests(unittest.TestCase):
    """技術QA T-01/T-02(音声化禁止記号Validator、検出時1回再生成->なお残ればSTOP)は維持(JASymbolCheckStopErrorへ分離)。"""

    BAD = "これはテスト（括弧）です。"      # 全角括弧=禁止記号
    GOOD = "これはテストです。"

    def test_original_symbol_regenerates_once_then_passes(self):
        client = _FakeClient([
            _fake_response(self.BAD, response_id="r_orig"),
            _fake_response(self.GOOD, response_id="r_orig2"),      # 記号再生成
            _fake_response("R1 text", response_id="r_r1"),
            _fake_response("R2 text", response_id="r_r2"),
        ])
        result = jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief")
        self.assertEqual(len(client.responses.calls), 4)
        self.assertTrue(result["stages"]["original"]["symbol_must_fix_applied"])
        self.assertEqual(result["stages"]["original"]["text"], self.GOOD)

    def test_original_symbol_persists_raises_symbol_stop(self):
        client = _FakeClient([_fake_response(self.BAD, response_id="a"), _fake_response(self.BAD, response_id="b")])
        with self.assertRaises(jaw.JASymbolCheckStopError) as cm:
            jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief")
        self.assertEqual(cm.exception.stage, "original_symbol")
        self.assertIn("JA_SYMBOL_CHECK_STOP", str(cm.exception))
        self.assertEqual(len(client.responses.calls), 2)           # 再生成は1回のみ(上限不変)
        self.assertTrue(cm.exception.findings)

    def test_r2_symbol_regenerates_once_then_passes(self):
        client = _FakeClient([
            _fake_response(self.GOOD, response_id="o"),
            _fake_response("R1 text", response_id="r1"),
            _fake_response(self.BAD, response_id="r2"),
            _fake_response(self.GOOD, response_id="r2b"),
        ])
        result = jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief")
        self.assertEqual(result["final_text"], self.GOOD)
        self.assertTrue(result["stages"]["r2"]["symbol_must_fix_applied"])

    def test_r2_symbol_persists_raises_symbol_stop(self):
        client = _FakeClient([
            _fake_response(self.GOOD, response_id="o"), _fake_response("R1 text", response_id="r1"),
            _fake_response(self.BAD, response_id="r2"), _fake_response(self.BAD, response_id="r2b"),
        ])
        with self.assertRaises(jaw.JASymbolCheckStopError) as cm:
            jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief")
        self.assertEqual(cm.exception.stage, "r2_symbol")


if __name__ == "__main__":
    unittest.main()
