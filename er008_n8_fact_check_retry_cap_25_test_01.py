# ============================================================
# er008_n8_fact_check_retry_cap_25_test.py
# ER-008-N8-CLOSEOUT-GOVERNANCE-25 (1): Fact Checker retry capの安全性を
# 固定するregression test。
#
# 調査結果(このtaskで確認): run_fact_checker_with_gates()の再試行は
# 「Web検索が1回も使われなかった」「JSON解析/スキーマ不適合」の2条件
# (技術的失敗)でのみ発火し、verdict(PASS/REVIEW_REQUIRED/FAIL)そのものを
# 理由に再試行することは無い(MAX_FACT_CHECK_ATTEMPTS=2は技術的失敗の
# retry上限であり、"PASSが出るまで再試行"する経路は存在しない)。
# 既存test(er002_test_ja_web_research_r3.py)は技術的失敗側のretry上限は
# 確認済みだが、「verdictがREVIEW_REQUIRED/FAILでもretryしない」ことを
# 直接確認するtestが無かったため、将来の変更でこの安全性が壊れないよう
# ここへ固定する。
# ============================================================
import unittest

import er002_ja_web_research_r3 as r3
from er002_test_ja_web_research_r3 import make_fake_response, make_valid_fact_check_json


class FactCheckVerdictDoesNotTriggerRetryTests(unittest.TestCase):
    """禁止事項: 「PASSが出るまで自動的に再試行」する設計になっていないことの固定。"""

    def _run_with_verdict(self, verdict):
        call_count = {"n": 0}

        def make_checker_fn():
            call_count["n"] += 1

            def checker_fn():
                resp = make_fake_response(make_valid_fact_check_json(verdict=verdict), search_call_count=1)
                usage = r3.extract_web_search_usage(resp)
                sources = r3.extract_sources(resp)
                return resp.output_text, resp.model, resp.id, usage, sources
            return checker_fn

        parsed, status, attempts, model_id, response_id, search_usage, sources = r3.run_fact_checker_with_gates(
            make_checker_fn)
        return parsed, status, call_count["n"]

    def test_pass_verdict_calls_exactly_once(self):
        parsed, status, n_calls = self._run_with_verdict("PASS")
        self.assertEqual(status, "FACT_CHECK_COMPLETED")
        self.assertEqual(parsed["verdict"], "PASS")
        self.assertEqual(n_calls, 1)

    def test_review_required_verdict_does_not_trigger_retry(self):
        parsed, status, n_calls = self._run_with_verdict("REVIEW_REQUIRED")
        self.assertEqual(status, "FACT_CHECK_COMPLETED")
        self.assertEqual(parsed["verdict"], "REVIEW_REQUIRED")
        self.assertEqual(n_calls, 1, "REVIEW_REQUIREDでも自動retryが発火してはならない")

    def test_fail_verdict_does_not_trigger_retry(self):
        parsed, status, n_calls = self._run_with_verdict("FAIL")
        self.assertEqual(status, "FACT_CHECK_COMPLETED")
        self.assertEqual(parsed["verdict"], "FAIL")
        self.assertEqual(n_calls, 1, "FAILでも自動retryが発火してはならない")

    def test_retry_cap_still_bounded_for_technical_failure(self):
        # 既存挙動の再確認(退行防止): 技術的失敗はmax_attempts回で必ず打ち切られる。
        call_count = {"n": 0}

        def make_checker_fn():
            call_count["n"] += 1

            def checker_fn():
                raise RuntimeError("simulated technical failure")
            return checker_fn

        r3.run_fact_checker_with_gates(make_checker_fn)
        self.assertLessEqual(call_count["n"], r3.MAX_FACT_CHECK_ATTEMPTS)


if __name__ == "__main__":
    unittest.main()
