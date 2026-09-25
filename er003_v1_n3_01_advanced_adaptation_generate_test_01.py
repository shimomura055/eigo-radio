# ============================================================
# er003_v1_n3_01_advanced_adaptation_generate_test_01.py
# NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01
# ============================================================
# er003_v1_n3_01_advanced_adaptation_generate.pyの単体テスト。実API呼び出しは
# 行わない(mock client使用、unittest.mock)。Trial script
# (er015_news_ja_to_en_adaptation_trial_01.py)のimportはこのテストファイル
# のみで行う(Production moduleは一切importしない)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_v1_n3_01_advanced_adaptation_generate_test_01 -v
# ============================================================
from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest import mock

import er003_v1_n3_01_advanced_adaptation_generate as adv
import er015_news_ja_to_en_adaptation_trial_01 as trial


JA_TEXT = "テスト記事タイトル\n\n本文段落1。\n\n本文段落2。"


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


GOOD_STRUCTURE_TEXT = (
    "# A Natural Title\n\n"
    "Main story paragraph one.\n\n"
    "Main story paragraph two.\n\n"
    "### First point heading\n"
    "First point body.\n\n"
    "### Second point heading\n"
    "Second point body.\n\n"
    "## In one line\n"
    "One closing sentence."
)


class TrialVerbatimTests(unittest.TestCase):
    """Trial(arm3)のDEVELOPER/ARM3_BLOCKが本Production moduleの定数と
    逐語一致すること、COMMON_BLOCKのPREFIX/SUFFIXがtrialの元文字列の
    前後に完全一致することを確認する(中間の6bulletのみ意図的に置換)。"""

    def test_developer_verbatim(self):
        self.assertEqual(trial.DEVELOPER, adv.ADVANCED_DEVELOPER)

    def test_arm3_block_verbatim(self):
        self.assertEqual(trial.ARM3_BLOCK, adv.ADVANCED_ARM3_BLOCK)

    def test_common_block_prefix_and_suffix_verbatim(self):
        self.assertTrue(trial.COMMON_BLOCK.startswith(adv.ADVANCED_COMMON_BLOCK_PREFIX),
                         "PREFIXがtrial.COMMON_BLOCKの先頭と一致しません")
        self.assertTrue(trial.COMMON_BLOCK.endswith(adv.ADVANCED_COMMON_BLOCK_SUFFIX),
                         "SUFFIXがtrial.COMMON_BLOCKの末尾と一致しません")

    def test_common_block_middle_is_replaced_not_identical(self):
        # 意図的な置換: 元のMeta固有6bulletはgeneral formの5bulletに置換
        # されているため、COMMON_BLOCK全体としては一致しない。
        general = (adv.ADVANCED_COMMON_BLOCK_PREFIX + adv.ADVANCED_GENERAL_PRESERVE_BULLETS +
                   adv.ADVANCED_COMMON_BLOCK_SUFFIX)
        self.assertNotEqual(trial.COMMON_BLOCK, general)

    def test_general_bullets_cover_five_concepts(self):
        text = adv.ADVANCED_GENERAL_PRESERVE_BULLETS
        for concept in ("opening expectation", "reversal", "central metaphor",
                         "order in which information", "ending"):
            self.assertIn(concept, text)

    def test_unchanged_portion_sha256_assert_does_not_raise(self):
        adv._assert_unchanged_portion_sha256()

    def test_unchanged_portion_sha256_mismatch_raises(self):
        original = adv.ADVANCED_UNCHANGED_PORTION_SHA256
        try:
            adv.ADVANCED_UNCHANGED_PORTION_SHA256 = "0" * 64
            with self.assertRaises(RuntimeError):
                adv._assert_unchanged_portion_sha256()
        finally:
            adv.ADVANCED_UNCHANGED_PORTION_SHA256 = original


class BuildPromptTests(unittest.TestCase):
    def test_build_prompt_contains_all_blocks_in_order(self):
        prompt = adv.build_prompt(JA_TEXT)
        idx_common = prompt.find("Adapt the Japanese article below into English.")
        idx_bullets = prompt.find("the central metaphor or storytelling device")
        idx_arm3 = prompt.find("Adaptation level: NATURAL ENGLISH.")
        idx_contract = prompt.find("Format (Markdown): start with")
        idx_article = prompt.find("[Japanese article]\n" + JA_TEXT)
        self.assertTrue(idx_common < idx_bullets < idx_arm3 < idx_contract < idx_article)

    def test_build_prompt_does_not_contain_meta_specific_bullets(self):
        prompt = adv.build_prompt(JA_TEXT)
        self.assertNotIn("AI makes the phone call", prompt)
        self.assertNotIn("understudy", prompt)


class GenerateAdvancedAdaptationTests(unittest.TestCase):
    def test_success_structure_pass_no_retry(self):
        good = _fake_response(GOOD_STRUCTURE_TEXT)
        client = _FakeClient([good])
        with mock.patch.object(adv.routing, "require_model", side_effect=lambda process, model: model), \
             mock.patch.object(adv, "_load_pricing", return_value=(lambda provider, model, meter: 0.0)):
            result = adv.generate_advanced_adaptation(JA_TEXT, client=client, model="gpt-5.6-luna")

        self.assertEqual(result.attempts, 1)
        self.assertFalse(result.retried)
        self.assertFalse(result.fallback_detected)
        self.assertEqual(result.structure_status, "STRUCTURE_PASS")
        self.assertTrue(result.text.startswith("# A Natural Title"))
        self.assertEqual(len(client.responses.calls), 1)
        sent = client.responses.calls[0]
        self.assertEqual(sent["input"][0]["role"], "developer")
        self.assertEqual(sent["input"][0]["content"], adv.ADVANCED_DEVELOPER)
        self.assertIn("[Japanese article]", sent["input"][1]["content"])

    def test_retries_once_on_bad_structure_then_succeeds(self):
        bad = _fake_response("# Title\n\nOnly one ### section here.\n### only one\nbody")
        good = _fake_response(GOOD_STRUCTURE_TEXT)
        client = _FakeClient([bad, good])
        with mock.patch.object(adv.routing, "require_model", side_effect=lambda process, model: model), \
             mock.patch.object(adv, "_load_pricing", return_value=(lambda provider, model, meter: 0.0)), \
             mock.patch.object(adv.vfl01.time, "sleep", return_value=None):
            result = adv.generate_advanced_adaptation(JA_TEXT, client=client, model="gpt-5.6-luna",
                                                        max_attempts=2)

        self.assertEqual(result.attempts, 2)
        self.assertTrue(result.retried)
        self.assertEqual(result.structure_status, "STRUCTURE_PASS")
        self.assertEqual(len(client.responses.calls), 2)

    def test_raises_after_max_attempts_structure_invalid(self):
        bad1 = _fake_response("# Title\n\nno sections at all")
        bad2 = _fake_response("# Title\n\nstill no sections")
        client = _FakeClient([bad1, bad2])
        with mock.patch.object(adv.routing, "require_model", side_effect=lambda process, model: model), \
             mock.patch.object(adv, "_load_pricing", return_value=(lambda provider, model, meter: 0.0)), \
             mock.patch.object(adv.vfl01.time, "sleep", return_value=None):
            with self.assertRaises(RuntimeError):
                adv.generate_advanced_adaptation(JA_TEXT, client=client, model="gpt-5.6-luna",
                                                  max_attempts=2)
        self.assertEqual(len(client.responses.calls), 2)

    def test_fallback_detected(self):
        different_model = _fake_response(GOOD_STRUCTURE_TEXT, model="gpt-5.6-other")
        client = _FakeClient([different_model])
        with mock.patch.object(adv.routing, "require_model", side_effect=lambda process, model: model), \
             mock.patch.object(adv, "_load_pricing", return_value=(lambda provider, model, meter: 0.0)):
            result = adv.generate_advanced_adaptation(JA_TEXT, client=client, model="gpt-5.6-luna")
        self.assertTrue(result.fallback_detected)
        self.assertEqual(result.model_id_actual, "gpt-5.6-other")


if __name__ == "__main__":
    unittest.main()
