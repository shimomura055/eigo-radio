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
        idx_vocab = prompt.find("Vocabulary difficulty rule:")
        idx_contract = prompt.find("Format (Markdown): start with")
        idx_section_boundary = prompt.find("Section boundary rule:")
        idx_article = prompt.find("[Japanese article]\n" + JA_TEXT)
        self.assertTrue(idx_common < idx_bullets < idx_arm3 < idx_vocab < idx_contract
                         < idx_section_boundary < idx_article)

    def test_build_prompt_does_not_contain_meta_specific_bullets(self):
        prompt = adv.build_prompt(JA_TEXT)
        self.assertNotIn("AI makes the phone call", prompt)
        self.assertNotIn("understudy", prompt)

    def test_build_prompt_without_must_fix_unchanged(self):
        # NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01: must_fix省略時、
        # 既存段落は一切変わらない(受け口追加のみ)。
        with_none = adv.build_prompt(JA_TEXT, must_fix=None)
        without_arg = adv.build_prompt(JA_TEXT)
        self.assertEqual(with_none, without_arg)

    def test_build_prompt_with_must_fix_appends_block(self):
        must_fix = [{"fact_id": "F1", "claim_in_article": "claim", "issue": "issue", "explanation": "expl"}]
        base_prompt = adv.build_prompt(JA_TEXT)
        prompt = adv.build_prompt(JA_TEXT, must_fix=must_fix)
        self.assertTrue(prompt.startswith(base_prompt))
        self.assertIn("Fact ID: F1", prompt)
        self.assertIn("claim", prompt)
        self.assertIn("issue", prompt)
        self.assertIn("expl", prompt)


class VocabRuleV2Tests(unittest.TestCase):
    """ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01: v2語彙ルールがPrompt本体に
    含まれ、v3(Trial-02、Topic Core Word例外+Metaphor専用ルール)固有の
    文言・フィールド名は一切含まれないことを確認する。"""

    def test_vocab_rule_v2_block_present_in_prompt(self):
        prompt = adv.build_prompt(JA_TEXT)
        self.assertIn(adv.ADVANCED_VOCAB_RULE_V2_BLOCK, prompt)

    def test_vocab_rule_v2_contains_12000_line_and_abcd(self):
        text = adv.ADVANCED_VOCAB_RULE_V2_BLOCK
        self.assertIn("12,000", text)
        for marker in ("A. Its meaning can easily be guessed",
                        "B. It is a word that has become well established",
                        "C. It is a proper noun",
                        "D. Replacing it with an easier word"):
            self.assertIn(marker, text)
        self.assertIn("Words that appear inside quotation marks", text)

    def test_vocab_rule_v2_does_not_contain_v3_topic_core_or_metaphor_exception(self):
        # v3固有のフィールド名・見出し(Trial-02由来)が一切含まれないこと。
        # 「central metaphor」は既存ARM3_BLOCK/一般形bulletの正規表現(記事の
        # 中心的な比喩を保持せよという既存Preserve指示)であり、v3の
        # Metaphor専用例外ルール(is_metaphor/exception_used等)とは無関係
        # なので、ここではv3固有マーカーのみを確認する。
        prompt = adv.build_prompt(JA_TEXT)
        for v3_marker in ("Topic Core", "topic_core", "is_metaphor",
                           "exception_used", "Metaphor restriction"):
            self.assertNotIn(v3_marker, prompt)

    def test_vocab_rule_v2_sha256_assert_does_not_raise(self):
        adv._assert_vocab_rule_v2_sha256()

    def test_vocab_rule_v2_sha256_mismatch_raises(self):
        original = adv.ADVANCED_VOCAB_RULE_V2_SHA256
        try:
            adv.ADVANCED_VOCAB_RULE_V2_SHA256 = "0" * 64
            with self.assertRaises(RuntimeError):
                adv._assert_vocab_rule_v2_sha256()
        finally:
            adv.ADVANCED_VOCAB_RULE_V2_SHA256 = original

    def test_standard_a2_module_self_consistent_sha256(self):
        # er003_v1_n3_01_standard_a2_generate.py(Standard v5)は本Advanced
        # Section Boundary Contract追加では一切変更しない(このファイルが
        # importするのは確認目的のみ)。同一セッション内で別管理ID
        # (NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01 Stage 2)によりStandardの
        # 語彙段落・境界維持行は正式に変更されているため、ここでは「Standard
        # モジュール自身のPrompt定数とsha256定数が整合していること」のみを
        # 確認する(Advanced側の変更がStandard側に意図せず波及していないか
        # の最低限の生存確認、逐語不変の主張はしない)。
        import er003_v1_n3_01_standard_a2_generate as std
        std._assert_prompt_sha256()  # 無エラーならOK


class SectionBoundaryContractTests(unittest.TestCase):
    """NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01: 見出し境界
    Contract(design doc §3.1)がPrompt本体に含まれ、既存ブロック
    (CONTRACT_SUFFIX/VOCAB_RULE_V2_BLOCK)を書き換えていないこと、
    small_bag等の記事固有語を含まないことを確認する。"""

    def test_section_boundary_contract_present_in_prompt(self):
        prompt = adv.build_prompt(JA_TEXT)
        self.assertIn(adv.ADVANCED_SECTION_BOUNDARY_CONTRACT, prompt)

    def test_section_boundary_contract_contains_core_rules(self):
        text = adv.ADVANCED_SECTION_BOUNDARY_CONTRACT
        self.assertIn("Section boundary rule:", text)
        self.assertIn("belongs after that section's own heading, not before it", text)
        self.assertIn("must not name the specific source, example, figure, or quotation", text)
        self.assertIn("Self-check for every heading before you finish", text)
        self.assertIn("A heading should open its own section with a new concrete point", text)

    def test_section_boundary_contract_does_not_contain_article_specific_words(self):
        # small_bag/Vogue/ELLE/Hormuz等の記事固有語を一切含まない一般形であること。
        text = adv.ADVANCED_SECTION_BOUNDARY_CONTRACT
        for article_specific in ("Vogue", "ELLE", "mini bag", "large bag", "Hormuz",
                                   "Meta", "Muse", "small_bag"):
            self.assertNotIn(article_specific, text)

    def test_existing_contract_suffix_unchanged_by_new_block(self):
        # 既存ADVANCED_CONTRACT_SUFFIX_LINES(Format規定)は無変更のまま
        # 別ブロックとして新contractが追加されていること。
        self.assertEqual(adv.ADVANCED_CONTRACT_SUFFIX_LINES, [
            "Write in English.",
            "Length: about 280–420 words in total.",
            "Format (Markdown): start with \"# \" followed by the title; then the "
            "main story; then exactly two \"### \" subsections, each 30–60 "
            "words, with headings that describe their content in your own words "
            "(do not use labels like \"Point One\"); then a final section headed "
            "exactly \"## In one line\" containing one sentence.",
        ])

    def test_section_boundary_contract_sha256_assert_does_not_raise(self):
        adv._assert_section_boundary_contract_sha256()

    def test_section_boundary_contract_sha256_mismatch_raises(self):
        original = adv.ADVANCED_SECTION_BOUNDARY_CONTRACT_SHA256
        try:
            adv.ADVANCED_SECTION_BOUNDARY_CONTRACT_SHA256 = "0" * 64
            with self.assertRaises(RuntimeError):
                adv._assert_section_boundary_contract_sha256()
        finally:
            adv.ADVANCED_SECTION_BOUNDARY_CONTRACT_SHA256 = original


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

    def test_must_fix_passed_through_to_prompt(self):
        # NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01: must_fixが渡された
        # 場合、送信されるuser messageへFact ID/claim/issue/explanationが
        # 反映されること(受け口のみ、既存段落は無変更)。
        good = _fake_response(GOOD_STRUCTURE_TEXT)
        client = _FakeClient([good])
        must_fix = [{"fact_id": "F1", "claim_in_article": "claim-X", "issue": "issue-X",
                     "explanation": "expl-X"}]
        with mock.patch.object(adv.routing, "require_model", side_effect=lambda process, model: model), \
             mock.patch.object(adv, "_load_pricing", return_value=(lambda provider, model, meter: 0.0)):
            adv.generate_advanced_adaptation(JA_TEXT, client=client, model="gpt-5.6-luna", must_fix=must_fix)
        sent = client.responses.calls[0]
        self.assertIn("Fact ID: F1", sent["input"][1]["content"])
        self.assertIn("claim-X", sent["input"][1]["content"])


if __name__ == "__main__":
    unittest.main()
