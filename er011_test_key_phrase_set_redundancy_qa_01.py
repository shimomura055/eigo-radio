# ============================================================
# er011_test_key_phrase_set_redundancy_qa_01.py
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Key Phrase相互重複QAのテスト
# ============================================================
import json
import unittest

import er011_key_phrase_set_redundancy_qa_01 as rqa

RANKS = [1, 2, 3, 4, 5]


def _all_pass_pairs():
    pairs = []
    import itertools
    for a, b in itertools.combinations(RANKS, 2):
        pairs.append({
            "rank_a": a, "rank_b": b, "meaning_overlap": "PASS", "usage_context_overlap": "PASS",
            "grammatical_teaching_value_overlap": "PASS", "conceptual_role_overlap": "PASS",
            "is_near_duplicate": False, "reasoning": "異なる概念を扱っている。",
        })
    return pairs


class PromptBuilderTests(unittest.TestCase):
    def test_build_user_message_lists_all_pairs_count(self):
        items = [{"rank": r, "key_phrase": f"phrase {r}", "japanese_gloss": "gloss", "source_sentence": "s"}
                 for r in RANKS]
        msg = rqa.build_user_message(items, "ARTICLE_TEXT_MARKER")
        self.assertIn("ARTICLE_TEXT_MARKER", msg)
        self.assertIn("10組", msg)
        self.assertIn("phrase 1", msg)


class ValidateRedundancyResponseTests(unittest.TestCase):
    def test_all_pass_yields_pass_status(self):
        result = rqa.validate_redundancy_response({"pairs": _all_pass_pairs()}, RANKS)
        self.assertEqual(result["status"], "REDUNDANCY_PASS", result)
        self.assertEqual(result["duplicate_pairs"], [])

    def test_missing_pair_yields_invalid(self):
        pairs = _all_pass_pairs()[:-1]  # 1組欠落
        result = rqa.validate_redundancy_response({"pairs": pairs}, RANKS)
        self.assertEqual(result["status"], "REDUNDANCY_INVALID")

    def test_near_duplicate_true_yields_ng_and_lists_pair(self):
        pairs = _all_pass_pairs()
        pairs[0]["is_near_duplicate"] = True
        pairs[0]["meaning_overlap"] = "FAIL"
        pairs[0]["reasoning"] = "どちらも注意を引く/奪うという同じ概念。"
        result = rqa.validate_redundancy_response({"pairs": pairs}, RANKS)
        self.assertEqual(result["status"], "REDUNDANCY_NG")
        self.assertEqual(len(result["duplicate_pairs"]), 1)
        self.assertEqual(result["duplicate_pairs"][0]["rank_a"], pairs[0]["rank_a"])

    def test_invalid_verdict_value_yields_invalid(self):
        pairs = _all_pass_pairs()
        pairs[0]["meaning_overlap"] = "MAYBE"
        result = rqa.validate_redundancy_response({"pairs": pairs}, RANKS)
        self.assertEqual(result["status"], "REDUNDANCY_INVALID")

    def test_duplicate_pair_entry_yields_invalid(self):
        pairs = _all_pass_pairs()
        pairs.append(dict(pairs[0]))  # 同じペアを二重に含める
        result = rqa.validate_redundancy_response({"pairs": pairs}, RANKS)
        self.assertEqual(result["status"], "REDUNDANCY_INVALID")

    def test_pairs_not_a_list_yields_invalid(self):
        result = rqa.validate_redundancy_response({"pairs": "not a list"}, RANKS)
        self.assertEqual(result["status"], "REDUNDANCY_INVALID")


class RunRedundancyQaGateFakeClientTests(unittest.TestCase):
    def test_success_path_first_attempt(self):
        raw = json.dumps({"pairs": _all_pass_pairs()})

        class FakeResponse:
            model = "fake-model"
            output_text = raw
            id = "resp_fake_1"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        def make_factory():
            return rqa.make_redundancy_qa_fn("dummy", client=FakeClient(), model="fake-model")

        parsed, status, attempts, model_id, response_id = rqa.run_redundancy_qa_gate(make_factory, RANKS)
        self.assertEqual(status, "REDUNDANCY_PASS")
        self.assertEqual(len(attempts), 1)

    def test_ng_result_does_not_retry(self):
        pairs = _all_pass_pairs()
        pairs[0]["is_near_duplicate"] = True
        pairs[0]["meaning_overlap"] = "FAIL"
        raw = json.dumps({"pairs": pairs})
        call_count = {"n": 0}

        class FakeResponse:
            model = "fake-model"
            output_text = raw
            id = "resp_fake_2"

        class CountingClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    call_count["n"] += 1
                    return FakeResponse()

        def make_factory():
            return rqa.make_redundancy_qa_fn("dummy", client=CountingClient(), model="fake-model")

        parsed, status, attempts, model_id, response_id = rqa.run_redundancy_qa_gate(make_factory, RANKS, max_attempts=2)
        self.assertEqual(status, "REDUNDANCY_NG")
        self.assertEqual(call_count["n"], 1, "内容判断(NG)自体は再試行してはならない")

    def test_technical_failure_then_success_retries_once(self):
        raw = json.dumps({"pairs": _all_pass_pairs()})
        call_count = {"n": 0}

        class FakeResponse:
            model = "fake-model"
            output_text = raw
            id = "resp_fake_3"

        class FailingThenGoodClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    call_count["n"] += 1
                    if call_count["n"] == 1:
                        raise RuntimeError("simulated technical failure")
                    return FakeResponse()

        def make_factory():
            return rqa.make_redundancy_qa_fn("dummy", client=FailingThenGoodClient(), model="fake-model")

        parsed, status, attempts, model_id, response_id = rqa.run_redundancy_qa_gate(
            make_factory, RANKS, sleep_fn=lambda s: None)
        self.assertEqual(status, "REDUNDANCY_PASS")
        self.assertEqual(len(attempts), 2)


class BuildDiagnosticNoteTests(unittest.TestCase):
    def test_note_mentions_duplicate_phrases(self):
        items_by_rank = {1: {"key_phrase": "catch their attention"}, 2: {"key_phrase": "a piece of your attention"}}
        note = rqa.build_redundancy_diagnostic_note(
            [{"rank_a": 1, "rank_b": 2, "reasoning": "同じ概念。"}], items_by_rank)
        self.assertIn("catch their attention", note)
        self.assertIn("a piece of your attention", note)


if __name__ == "__main__":
    unittest.main()
