# ============================================================
# er003_v1_n3_01_standard_a2_generate_test_01.py
# NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01
# ============================================================
# er003_v1_n3_01_standard_a2_generate.pyの単体テスト。実API呼び出しは
# 行わない(mock client使用、unittest.mock)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_v1_n3_01_standard_a2_generate_test_01 -v
# ============================================================
from __future__ import annotations

import hashlib
import os
import unittest
from types import SimpleNamespace
from unittest import mock

import er003_v1_n3_01_standard_a2_generate as std_a2


PROMPT_FILE = os.path.join(
    "er015_output", "news_standard_a2_vocab_6000_cutoff_trial_01",
    "prompt_standard_v5_6000.txt")

ADVANCED_TEXT = "Title Here\n\nThis is an advanced article with 12 pipes and John Smith."

GOOD_STRUCTURE_TEXT = (
    "Standard Title\n\n"
    "Main story paragraph one.\n\n"
    "Main story paragraph two.\n\n"
    "### First point heading\n"
    "First point body.\n\n"
    "### Second point heading\n"
    "Second point body.\n\n"
    "## In one line\n"
    "One closing sentence."
)


def _fake_response(text: str, model: str = "gpt-5.6-luna", response_id: str = "resp_1",
                    input_tokens: int = 100, output_tokens: int = 50):
    return SimpleNamespace(
        output_text=text,
        model=model,
        id=response_id,
        usage=SimpleNamespace(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_tokens_details=SimpleNamespace(cached_tokens=0),
            output_tokens_details=SimpleNamespace(reasoning_tokens=10),
        ),
    )


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


class PromptSha256Tests(unittest.TestCase):
    def test_prompt_equals_trial_file_plus_inserted_structure_line(self):
        # NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01 delegation D3: v5の
        # トライアルfile(旧sha256 cbb723...で確認済み)に、構造保持行1行を
        # 「Output only...」の直前へ挿入したものが、現行STANDARD_A2_PROMPT_V5
        # と一致することを確認する(v5の語彙・簡略化指示は無変更)。
        with open(PROMPT_FILE, "r", encoding="utf-8", newline=None) as f:
            trial_text = f.read()
        inserted_line = (
            'Keep the same Markdown structure (the "# " title, the two "### " '
            'sections, and the final "## In one line" section); do not add or '
            'remove sections.\n\n'
        )
        anchor = "Output only the English title and the English body."
        self.assertIn(anchor, trial_text)
        expected_text = trial_text.replace(anchor, inserted_line + anchor)
        reconstructed = std_a2.reconstruct_prompt_file_text()
        self.assertEqual(reconstructed, expected_text,
                          "reconstructed prompt text differs from trial file + inserted structure line")

    def test_prompt_sha256_matches_constant(self):
        reconstructed = std_a2.reconstruct_prompt_file_text()
        reconstructed_sha256 = hashlib.sha256(reconstructed.encode("utf-8")).hexdigest()
        self.assertEqual(reconstructed_sha256, std_a2.STANDARD_A2_PROMPT_SHA256)

    def test_module_import_time_assert_does_not_raise(self):
        # importが既に成功していること自体が_assert_prompt_sha256()のPASSを意味する。
        std_a2._assert_prompt_sha256()  # 明示的に再実行しても例外が出ないことを確認

    def test_prompt_sha256_mismatch_raises(self):
        original = std_a2.STANDARD_A2_PROMPT_SHA256
        try:
            std_a2.STANDARD_A2_PROMPT_SHA256 = "0" * 64
            with self.assertRaises(RuntimeError):
                std_a2._assert_prompt_sha256()
        finally:
            std_a2.STANDARD_A2_PROMPT_SHA256 = original


class BuildPromptTests(unittest.TestCase):
    def test_build_prompt_substitutes_article(self):
        prompt = std_a2.build_prompt("Hello world article.")
        self.assertIn("Hello world article.", prompt)
        self.assertTrue(prompt.startswith("Rewrite this entire article for CEFR A2 learners."))
        self.assertNotIn("{advanced_article}", prompt)


class GenerateStandardA2Tests(unittest.TestCase):
    def test_success_no_retry(self):
        good = _fake_response(GOOD_STRUCTURE_TEXT)
        client = _FakeClient([good])
        with mock.patch.object(std_a2.routing, "require_model", side_effect=lambda process, model: model), \
             mock.patch.object(std_a2, "_load_pricing", return_value=(lambda provider, model, meter: 0.0)):
            result = std_a2.generate_standard_a2(ADVANCED_TEXT, client=client, model="gpt-5.6-luna")

        self.assertEqual(result.attempts, 1)
        self.assertFalse(result.retried)
        self.assertFalse(result.fallback_detected)
        self.assertEqual(result.structure_status, "STRUCTURE_PASS")
        self.assertTrue(result.text.startswith("Standard Title"))
        self.assertEqual(len(client.responses.calls), 1)
        sent = client.responses.calls[0]
        self.assertEqual(sent["input"][0]["role"], "developer")
        self.assertEqual(sent["input"][0]["content"], std_a2.STANDARD_A2_DEVELOPER)
        self.assertEqual(sent["input"][1]["role"], "user")
        self.assertIn("This is an advanced article", sent["input"][1]["content"])

    def test_retries_once_on_bad_structure_then_succeeds(self):
        bad = _fake_response("Standard Title\n\nOnly one ### section here.\n### only one\nbody")
        good = _fake_response(GOOD_STRUCTURE_TEXT)
        client = _FakeClient([bad, good])
        with mock.patch.object(std_a2.routing, "require_model", side_effect=lambda process, model: model), \
             mock.patch.object(std_a2, "_load_pricing", return_value=(lambda provider, model, meter: 0.0)), \
             mock.patch.object(std_a2.vfl01.time, "sleep", return_value=None):
            result = std_a2.generate_standard_a2(ADVANCED_TEXT, client=client, model="gpt-5.6-luna",
                                                   max_retries=1)

        self.assertEqual(result.attempts, 2)
        self.assertTrue(result.retried)
        self.assertEqual(result.structure_status, "STRUCTURE_PASS")
        self.assertEqual(len(client.responses.calls), 2)

    def test_fails_after_max_retries_structure_invalid(self):
        bad1 = _fake_response("Standard Title\n\nno sections at all")
        bad2 = _fake_response("Standard Title\n\nstill no sections")
        client = _FakeClient([bad1, bad2])
        with mock.patch.object(std_a2.routing, "require_model", side_effect=lambda process, model: model), \
             mock.patch.object(std_a2, "_load_pricing", return_value=(lambda provider, model, meter: 0.0)), \
             mock.patch.object(std_a2.vfl01.time, "sleep", return_value=None):
            with self.assertRaises(RuntimeError):
                std_a2.generate_standard_a2(ADVANCED_TEXT, client=client, model="gpt-5.6-luna",
                                             max_retries=1)
        self.assertEqual(len(client.responses.calls), 2)

    def test_fallback_detected(self):
        different_model = _fake_response(GOOD_STRUCTURE_TEXT, model="gpt-5.6-other")
        client = _FakeClient([different_model])
        with mock.patch.object(std_a2.routing, "require_model", side_effect=lambda process, model: model), \
             mock.patch.object(std_a2, "_load_pricing", return_value=(lambda provider, model, meter: 0.0)):
            result = std_a2.generate_standard_a2(ADVANCED_TEXT, client=client, model="gpt-5.6-luna")
        self.assertTrue(result.fallback_detected)
        self.assertEqual(result.model_id_actual, "gpt-5.6-other")

    def test_effort_mismatch_raises_value_error(self):
        client = _FakeClient([_fake_response("Standard Title\n\nBody.")])
        with self.assertRaises(ValueError):
            std_a2.generate_standard_a2(ADVANCED_TEXT, client=client, model="gpt-5.6-luna",
                                         effort="low")


class RunChecksTests(unittest.TestCase):
    def test_title_present_and_no_number_loss(self):
        advanced = "Advanced Title\n\nThere are 12 pipes near John Smith's house."
        standard = "Standard Title\n\nThere are 12 pipes near John's house."
        checks = std_a2.run_checks(advanced, standard)
        self.assertEqual(checks["title"], "Standard Title")
        self.assertNotIn("MISSING_TITLE", checks["checks_failed"])
        self.assertEqual(checks["numbers_missing"], [])
        self.assertEqual(checks["numbers_added"], [])

    def test_missing_title(self):
        advanced = "Advanced Title\n\nBody with 5 items."
        standard = "   \n   \n   "  # 空白のみ -> strip_title後にtitleが空文字になる
        checks = std_a2.run_checks(advanced, standard)
        self.assertIn("MISSING_TITLE", checks["checks_failed"])

    def test_number_missing_detected(self):
        advanced = "Title\n\nThere were 42 cases reported in 2019."
        standard = "Title\n\nThere were some cases reported."
        checks = std_a2.run_checks(advanced, standard)
        self.assertIn("NUMBERS_MISSING", checks["checks_failed"])
        self.assertIn("42", checks["numbers_missing"])
        self.assertIn("2019", checks["numbers_missing"])

    def test_number_added_detected(self):
        advanced = "Title\n\nThere were some cases reported."
        standard = "Title\n\nThere were 42 cases reported."
        checks = std_a2.run_checks(advanced, standard)
        self.assertIn("NUMBERS_ADDED", checks["checks_failed"])
        self.assertIn("42", checks["numbers_added"])


class StripTitleAndFactTokensTests(unittest.TestCase):
    def test_strip_title_and_extract_fact_tokens(self):
        title, body = std_a2.strip_title("My Title\n\nBody text with 7 and John.")
        self.assertEqual(title, "My Title")
        self.assertIn("Body text", body)
        tokens = std_a2.extract_fact_tokens("My Title\n\nBody text with 7 and John.")
        self.assertIn("7", tokens["numbers"])
        self.assertIn("John", tokens["proper_nouns"])


if __name__ == "__main__":
    unittest.main()
