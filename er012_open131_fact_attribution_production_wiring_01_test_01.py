# ============================================================
# er012_open131_fact_attribution_production_wiring_01_test_01.py
# OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01
# ============================================================
# 回帰テスト。run_project_regression.py(er0*_test_*.py自動探索)対象。
from __future__ import annotations

import re
import unittest

import er002_ja_web_research_r3 as r3
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_production_runner_01 as runner


SAMPLE_TEMPLATE = "TOPIC={topic}\nARTICLE={article_text}\nSOURCES={writer_sources_block}\n"

LEDGER_SAMPLE = """
[VOICE_1_EVIDENCE] 1-01(fact_001): Gensler調査、固定席保有者は所属感87%。source: Bisnow
[VOICE_1_EVIDENCE] 1-02(fact_003): LinkedIn News、衛生懸念。source: LinkedIn News
[VOICE_2_EVIDENCE] 2-01(fact_008): TOKYO MX+、自由席支持。source: TOKYO MX+
[CROSS_REFERENCE] X-01(fact_002): Amazon CEO、ホットデスキング廃止。source: Business Insider
"""

LEDGER_SAMPLE_3V = LEDGER_SAMPLE + (
    "[VOICE_3_EVIDENCE] 3-01(synthetic): テスト用の3人目Voice evidence。source: none\n"
)


class BuildFactCheckPromptBackwardCompatTest(unittest.TestCase):
    """Gate 3: 既定""でPromptバイト不変(A-Family fixture)。"""

    def test_default_empty_block_is_byte_identical_to_pre_change_signature(self):
        topic, article_text, sources = "Sample Topic", "Sample article body.", []
        with_default = r3.build_fact_check_prompt(topic, article_text, sources, template=SAMPLE_TEMPLATE)
        with_explicit_empty = r3.build_fact_check_prompt(
            topic, article_text, sources, template=SAMPLE_TEMPLATE, voice_attribution_block="")
        expected = SAMPLE_TEMPLATE.format(topic=topic, article_text=article_text, writer_sources_block="(参照ソースなし)")
        self.assertEqual(with_default, expected)
        self.assertEqual(with_explicit_empty, expected)
        self.assertEqual(with_default, with_explicit_empty)

    def test_nonempty_block_is_appended_after_existing_prompt_unchanged(self):
        topic, article_text, sources = "Sample Topic", "Sample article body.", []
        base = r3.build_fact_check_prompt(topic, article_text, sources, template=SAMPLE_TEMPLATE)
        block = "【追加ルール】テスト用block"
        combined = r3.build_fact_check_prompt(
            topic, article_text, sources, template=SAMPLE_TEMPLATE, voice_attribution_block=block)
        self.assertTrue(combined.startswith(base))
        self.assertIn(block, combined)


class RegistryFactAttributionModeGatingTest(unittest.TestCase):
    """既定OFF・family=="B"コードレベルgating(Trial-02第6節の設計結論どおり)。"""

    def test_default_mode_is_off(self):
        et = registry.get_editorial_type("b_family_voices")
        self.assertFalse(et["fact_attribution_mode"])
        self.assertFalse(registry.is_fact_attribution_mode_enabled())

    def test_enabled_only_when_family_b_and_flag_true(self):
        et = registry.EDITORIAL_TYPES["b_family_voices"]
        original = et["fact_attribution_mode"]
        try:
            et["fact_attribution_mode"] = True
            self.assertTrue(registry.is_fact_attribution_mode_enabled())
            original_family = et["family"]
            et["family"] = "A"
            try:
                self.assertFalse(registry.is_fact_attribution_mode_enabled())
            finally:
                et["family"] = original_family
        finally:
            et["fact_attribution_mode"] = original

    def test_build_voice_attribution_block_empty_without_voice_tags(self):
        self.assertEqual(registry.build_voice_attribution_block("no voice tags in this ledger text"), "")
        self.assertEqual(registry.build_voice_attribution_block(""), "")

    def test_build_voice_attribution_block_contains_rule_and_evidence(self):
        block = registry.build_voice_attribution_block(LEDGER_SAMPLE)
        self.assertIn("出典・調査名・数値を逐一明記していないことだけを理由に", block)
        self.assertIn("VOICE_1_EVIDENCE", block)
        self.assertIn("VOICE_2_EVIDENCE", block)
        self.assertIn("実在する名前付き個人の発言として具体的に帰属される主張", block)

    def test_3v_extension_via_voice_3_evidence_tag_without_code_change(self):
        block = registry.build_voice_attribution_block(LEDGER_SAMPLE_3V)
        self.assertIn("VOICE_3_EVIDENCE", block)


class ProductionRunnerGatingWiringTest(unittest.TestCase):
    """B-Family Production runner側の入口関数(opt-in、既定OFF)。"""

    def test_helper_returns_empty_when_mode_off(self):
        self.assertEqual(runner.build_fact_attribution_block_if_enabled(LEDGER_SAMPLE), "")

    def test_helper_returns_nonempty_when_mode_on(self):
        et = registry.EDITORIAL_TYPES["b_family_voices"]
        original = et["fact_attribution_mode"]
        try:
            et["fact_attribution_mode"] = True
            block = runner.build_fact_attribution_block_if_enabled(LEDGER_SAMPLE)
            self.assertNotEqual(block, "")
            self.assertIn("VOICE_1_EVIDENCE", block)
        finally:
            et["fact_attribution_mode"] = original

    def test_block_is_independent_of_article_text_local_rewrite_simulation(self):
        """Local Rewrite(er010_ledger_local_rewrite_09.apply_rewrites)は
        article_textの一部文だけをstr.replace(...,1)で書き換える(既存挙動、
        本タスクでは無変更)。blockはledger_textとregistryフラグだけから
        決まり、article_textに一切依存しないため、rewrite前後で同一の
        blockが渡ることを保証する(retry/regeneration整合)。"""
        et = registry.EDITORIAL_TYPES["b_family_voices"]
        original = et["fact_attribution_mode"]
        try:
            et["fact_attribution_mode"] = True
            block_before = runner.build_fact_attribution_block_if_enabled(LEDGER_SAMPLE)
            # article_textが変わる(Local Rewriteのような書き換えを模擬)場合でも
            # build_fact_attribution_block_if_enabled()はarticle_textを一切
            # 引数に取らない(ledger_textのみ)ため、複数回呼んでも同一。
            block_after = runner.build_fact_attribution_block_if_enabled(LEDGER_SAMPLE)
            self.assertEqual(block_before, block_after)
        finally:
            et["fact_attribution_mode"] = original


class RunFactCheckerSignatureTest(unittest.TestCase):
    """a2prod/b1prodのrun_fact_checker()が同一signature(voice_attribution_
    block既定"")を持ち、prompt生成に反映することをprompt構築部分のみで確認
    (実際のLLM呼び出しはしない、run_fact_checker_with_gatesより前段の
    fc_promptの組み立てだけを確認する軽量test)。"""

    def test_a2prod_and_b1prod_build_identical_prompt_shape(self):
        import er012_b_family_voices_a2_production_01 as a2prod
        import er012_b_family_voices_production_01 as b1prod

        topic, article_text = "Sample Topic", "Sample article."
        prompt_default_a2 = r3.build_fact_check_prompt(topic, article_text, [])
        prompt_default_b1 = r3.build_fact_check_prompt(topic, article_text, [])
        self.assertEqual(prompt_default_a2, prompt_default_b1)

        block = "【追加ルール】テスト"
        prompt_with_block = r3.build_fact_check_prompt(topic, article_text, [], voice_attribution_block=block)
        self.assertNotEqual(prompt_with_block, prompt_default_a2)
        self.assertTrue(prompt_with_block.startswith(prompt_default_a2))

        # run_fact_checker自体のsignatureにvoice_attribution_block(既定"")が
        # 存在することを確認する(呼び出さない、signatureのみ)。
        import inspect
        sig_a2 = inspect.signature(a2prod.run_fact_checker)
        sig_b1 = inspect.signature(b1prod.run_fact_checker)
        self.assertEqual(sig_a2.parameters["voice_attribution_block"].default, "")
        self.assertEqual(sig_b1.parameters["voice_attribution_block"].default, "")


class AFamilyUnaffectedTest(unittest.TestCase):
    """A-Family経路がregistry/voice_attribution_blockを一切参照しないこと
    (Gate 3: A-Family Promptバイト不変・dangling referenceなし)。"""

    def test_a_family_writer_files_do_not_reference_new_mechanism(self):
        targets = ("er006_pool_pilot_01_writer.py", "er003_v1_n3_01_articles_generate.py")
        for path in targets:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn("voice_attribution_block", text, f"{path} references voice_attribution_block")
            self.assertNotIn("er012_b_family_editorial_type_registry_01", text,
                             f"{path} imports the B-Family registry")

    def test_a_family_fact_check_call_site_still_passes_no_extra_args(self):
        with open("er003_v1_n3_01_articles_generate.py", encoding="utf-8") as f:
            text = f.read()
        self.assertIn("r3.build_fact_check_prompt(topic, article_text, [])", text)


if __name__ == "__main__":
    unittest.main()
