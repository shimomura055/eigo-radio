# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_stage2_production_01_test_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Phase 1 ④、委任_07)
# ============================================================
# ネットワーク呼び出しなし(¥0)。段落抽出・Prompt構築ロジックのread-only
# regression testのみ。
from __future__ import annotations

import unittest

import er052_open233_self_recovery_stage2_production_01 as s2p


class TestSplitParagraphs(unittest.TestCase):
    def test_basic_split(self):
        text = "para1 line\n\npara2 line\n\npara3 line"
        self.assertEqual(s2p.split_paragraphs(text), ["para1 line", "para2 line", "para3 line"])

    def test_ignores_empty_paragraphs(self):
        text = "para1\n\n\n\npara2"
        self.assertEqual(s2p.split_paragraphs(text), ["para1", "para2"])


class TestLocalContext(unittest.TestCase):
    def test_finds_target_paragraph_with_neighbors(self):
        text = "P0 intro\n\nP1 contains TARGETCLAIM here\n\nP2 outro"
        ctx, fallback = s2p.build_local_context(text, "P1 contains TARGETCLAIM here"[:20])
        self.assertFalse(fallback)
        self.assertIn("P0 intro", ctx)
        self.assertIn("TARGETCLAIM", ctx)
        self.assertIn("P2 outro", ctx)

    def test_first_paragraph_has_no_prev(self):
        text = "P0 has TARGETCLAIM\n\nP1\n\nP2"
        ctx, fallback = s2p.build_local_context(text, "P0 has TARGETCLAIM")
        self.assertFalse(fallback)
        self.assertIn("P0 has TARGETCLAIM", ctx)
        self.assertIn("P1", ctx)
        self.assertNotIn("P2", ctx)

    def test_fallback_when_not_found(self):
        text = "P0\n\nP1\n\nP2"
        ctx, fallback = s2p.build_local_context(text, "NOT_PRESENT_ANYWHERE_XYZ")
        self.assertTrue(fallback)
        self.assertEqual(ctx, text)


class TestPromptBuilders(unittest.TestCase):
    def test_per_claim_prompt_excludes_explanation_severity_flags(self):
        prompt = s2p.PER_CLAIM_PROMPT_TEMPLATE.format(
            verified_ledger_text="LEDGERX", source_article_text="(なし)",
            claim_text="CLAIMX", local_context="CTXX", origin="translation",
            related_fact_id="F001", materiality_rubric=s2p.MATERIALITY_RUBRIC,
            rewrite_hint_instruction=s2p.REWRITE_HINT_INSTRUCTION,
        )
        self.assertIn("LEDGERX", prompt)
        self.assertIn("CLAIMX", prompt)
        self.assertIn("CTXX", prompt)
        self.assertIn("BLOCKING", prompt)
        self.assertNotIn("changed_actor", prompt)
        # explanation/severity/10 flagsを「提示しない」旨の説明文自体は許容する
        # (実際のexplanation本文・changed_*フラグ値が入力に含まれないことのみ確認)。
        self.assertNotIn("severity_final", prompt)

    def test_per_claim_prompt_requires_rewrite_hint(self):
        self.assertIn("rewrite_hint", s2p.PER_CLAIM_JSON_SCHEMA["schema"]["required"])
        self.assertIn("rewrite_hint", s2p.PER_CLAIM_PROMPT_TEMPLATE)

    def test_batch_prompt_contains_claim_index(self):
        claims = [
            {"claim_text": "C0", "origin": "translation", "related_fact_id": "F1", "local_context": "CTX0"},
            {"claim_text": "C1", "origin": "ja_source", "related_fact_id": "F2", "local_context": "CTX1"},
        ]
        blocks = []
        for i, c in enumerate(claims):
            blocks.append(f"[claim_index={i}]\nclaim: {c['claim_text']}")
        claims_block = "\n\n".join(blocks)
        prompt = s2p.BATCH_PROMPT_TEMPLATE.format(
            verified_ledger_text="LEDGERX", source_article_text="(なし)",
            claims_block=claims_block, materiality_rubric=s2p.MATERIALITY_RUBRIC,
            rewrite_hint_instruction=s2p.REWRITE_HINT_INSTRUCTION,
        )
        self.assertIn("claim_index=0", prompt)
        self.assertIn("claim_index=1", prompt)
        self.assertIn("C0", prompt)
        self.assertIn("C1", prompt)

    def test_batch_json_schema_requires_rewrite_hint(self):
        item_schema = s2p.BATCH_JSON_SCHEMA["schema"]["properties"]["judgments"]["items"]
        self.assertIn("rewrite_hint", item_schema["required"])
        self.assertIn("rewrite_hint", item_schema["properties"])


class TestCostFunction(unittest.TestCase):
    def test_official_cost_jpy_zero(self):
        self.assertEqual(s2p.official_cost_jpy({}), 0.0)


if __name__ == "__main__":
    unittest.main()
