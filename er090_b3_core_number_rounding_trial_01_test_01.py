# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 Trial専用overlayの単体test(API呼出0、費用0円)。
実行: .venv/Scripts/python.exe -m pytest er090_b3_core_number_rounding_trial_01_test_01.py -q
"""
from __future__ import annotations

import hashlib
import json
import os
import unittest
from decimal import Decimal

import er090_b3_core_number_rounding_trial_01_overlay as ov
import er053_family_x_factlock_ja_writer_01 as w1
import er053_b3_deterministic_producer_01 as prod
import er053_b3_annotation_contract_01 as contract

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_A = os.path.join(HERE, "er019_output", "paycheck_personality", "run_pp_01")


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


class TestRounding(unittest.TestCase):
    def test_ordinary_rounding_ok(self):
        self.assertEqual(ov.validate_surface_approx("最大134,515人", "最大約13万5千人"), [])
        self.assertEqual(ov.validate_surface_approx("134,515人", "約13万5000人"), [])
        self.assertEqual(ov.validate_surface_approx("134,515人", "約13万人"), [])       # k=2も通常の四捨五入
        self.assertEqual(ov.validate_surface_approx("1,332", "約1,300"), [])
        self.assertEqual(ov.validate_surface_approx("295億9,100万ドル", "約296億ドル"), [])

    def test_not_ordinary_rounding(self):
        self.assertTrue(any(x.startswith("V3_not_ordinary") for x in ov.validate_surface_approx("134,515人", "約13万4千人")))
        self.assertTrue(any(x.startswith("V3_not_ordinary") for x in ov.validate_surface_approx("134,515人", "約14万人")))

    def test_qualifier_unit_hedge(self):
        self.assertIn("V4_qualifier_dropped(最大)", ov.validate_surface_approx("最大134,515人", "約13万5千人"))
        self.assertTrue(any(x.startswith("V4_unit") for x in ov.validate_surface_approx("134,515人", "約13万5千件")))
        self.assertIn("V5_no_hedge_word", ov.validate_surface_approx("134,515人", "13万5千人"))
        self.assertIn("V5_approx_missing", ov.validate_surface_approx("134,515人", None))
        self.assertIn("V3_approx_equals_exact", ov.validate_surface_approx("約134,515人", "約134,515人"))

    def test_single_digit_cannot_be_rounded(self):
        self.assertNotEqual(ov.validate_surface_approx("3回以上", "約3回以上"), [])      # 1桁は丸め不能(V3違反)


class TestOverlayLogic(unittest.TestCase):
    SIDECAR = {"facts": [{"n": 1, "ledger_ids": ["F02"]}, {"n": 2, "ledger_ids": ["F04"]}],
               "numbers": [
                   {"surface": "11件", "kind": "magnitude", "class": "core", "concept": "C1", "ledger_ids": ["F04"], "role": ""},
                   {"surface": "最大134,515人", "kind": "magnitude", "class": "core", "concept": "C2", "ledger_ids": ["F04"], "role": ""},
                   {"surface": "134,515人", "kind": "magnitude", "class": "core", "concept": "C2", "ledger_ids": ["F04"], "role": ""},
                   {"surface": "0.0589", "kind": "magnitude", "class": "peripheral", "concept": "C6", "ledger_ids": ["F08"], "role": ""}]}

    def judge(self):
        return {"decisions": [
            {"concept": "C1", "decision": "EXACT_REQUIRED", "surfaces": [{"surface": "11件", "approx_surface": None}],
             "reason": "r", "basis_fact_ids": ["F04"], "approved_condition": "c"},
            {"concept": "C2", "decision": "APPROXIMATE_OK",
             "surfaces": [{"surface": "最大134,515人", "approx_surface": "最大約13万5千人"}, {"surface": "134,515人", "approx_surface": "約13万5千人"}],
             "reason": "r", "basis_fact_ids": ["F04"], "approved_condition": "c"}]}

    def test_core_only_and_order(self):
        self.assertEqual([c["concept"] for c in ov.core_concepts(self.SIDECAR)], ["C1", "C2"])
        self.assertEqual(ov.core_concepts(self.SIDECAR)[1]["surfaces"], ["最大134,515人", "134,515人"])

    def test_accept_valid(self):
        o = ov.build_overlay(self.SIDECAR, self.judge())
        self.assertEqual([e["final_decision"] for e in o["entries"]], ["EXACT_REQUIRED", "APPROXIMATE_OK"])
        self.assertEqual(o["violations"], [])
        self.assertEqual(len(ov.constraint_lines(o)), 2)
        self.assertTrue(all("事実2について：【概数表記】" in l for l in ov.constraint_lines(o)))

    def test_downgrade_invalid_rounding(self):
        j = self.judge()
        j["decisions"][1]["surfaces"][0]["approx_surface"] = "最大約14万人"
        o = ov.build_overlay(self.SIDECAR, j)
        self.assertEqual(o["entries"][1]["final_decision"], "EXACT_REQUIRED")
        self.assertTrue(o["entries"][1]["downgrade_reasons"])
        self.assertEqual(ov.constraint_lines(o), [])

    def test_concept_set_mismatch_fail_closed(self):
        j = self.judge()
        j["decisions"].append({"concept": "C9", "decision": "APPROXIMATE_OK", "surfaces": [], "reason": "", "basis_fact_ids": [], "approved_condition": ""})
        o = ov.build_overlay(self.SIDECAR, j)
        self.assertTrue(o["violations"])
        self.assertTrue(all(e["final_decision"] == "EXACT_REQUIRED" for e in o["entries"]))
        j2 = self.judge()
        j2["decisions"].reverse()
        self.assertTrue(ov.build_overlay(self.SIDECAR, j2)["violations"])      # 並べ替え禁止

    def test_no_op_when_exact_only(self):
        j = self.judge()
        j["decisions"][1]["decision"] = "EXACT_REQUIRED"
        o = ov.build_overlay(self.SIDECAR, j)
        self.assertEqual(o["n_approximate_ok"], 0)
        cons = "Writerへの注意(事実ではありません)：\n- 事実2について：x\n"
        self.assertEqual(ov.apply_to_constraints(cons, o, "H"), cons)
        self.assertEqual(ov.apply_rule8("PROMPT", o), "PROMPT")

    def test_basis_fact_id_mismatch_downgrades(self):
        j = self.judge()
        j["decisions"][1]["basis_fact_ids"] = ["F99"]
        o = ov.build_overlay(self.SIDECAR, j)
        self.assertEqual(o["entries"][1]["final_decision"], "EXACT_REQUIRED")


class TestApprovedRuleText(unittest.TestCase):
    def test_spoken_first_text_matches_current_spec(self):
        with open(os.path.join(HERE, "CURRENT_SPEC.md"), encoding="utf-8") as f:
            line = next(l for l in f if l.startswith("| Spoken-first Number Treatment |"))
        self.assertIn(ov.SPOKEN_FIRST_NUMBER_TREATMENT_TEXT, line)

    def test_judge_prompt_embeds_verbatim_rules(self):
        p = ov.build_judge_user_prompt(storyline="S", facts_text="- 【事実1】a", constraints_text="", sidecar=TestOverlayLogic.SIDECAR,
                                       ledger_records={"F04": "[VERIFIED] F04: x"})
        self.assertIn(ov.LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK, p)
        self.assertIn(ov.NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK, p)
        self.assertIn(ov.SPOKEN_FIRST_NUMBER_TREATMENT_TEXT, p)
        self.assertNotIn("期待ラベル", p)


@unittest.skipUnless(os.path.exists(os.path.join(RUN_A, "storyline_b3", "annotation.json")), "run_pp_01 artifacts missing")
class TestArticleAReal(unittest.TestCase):
    """記事A実データ(API 0): Before入力の再現、構造diff、no-op。"""

    @classmethod
    def setUpClass(cls):
        cls.a = contract.validate_annotated_b3(RUN_A)
        cls.sc = cls.a.sidecar
        cls.story, cls.facts = w1.parse_brief_md(cls.a.annotated_md_text)

    def _judge(self, approx_c2=True):
        return {"decisions": [
            {"concept": "C1", "decision": "EXACT_REQUIRED", "surfaces": [{"surface": "11件", "approx_surface": None}], "reason": "", "basis_fact_ids": ["F04"], "approved_condition": ""},
            {"concept": "C2", "decision": "APPROXIMATE_OK" if approx_c2 else "EXACT_REQUIRED",
             "surfaces": [{"surface": "最大134,515人", "approx_surface": "最大約13万5千人"}, {"surface": "134,515人", "approx_surface": "約13万5千人"}],
             "reason": "", "basis_fact_ids": ["F04"], "approved_condition": ""},
            {"concept": "C4", "decision": "EXACT_REQUIRED", "surfaces": [{"surface": "3回以上", "approx_surface": None}], "reason": "", "basis_fact_ids": ["F07"], "approved_condition": ""},
            {"concept": "C5", "decision": "EXACT_REQUIRED", "surfaces": [{"surface": "0.0630", "approx_surface": None}], "reason": "", "basis_fact_ids": ["F08"], "approved_condition": ""}]}

    def test_before_prompt_reproduces_production_r0_prompt_sha(self):
        meta = json.load(open(os.path.join(RUN_A, "ja_writer", "factlock", "r0_meta.json"), encoding="utf-8"))
        p = w1.build_r0_prompt(self.story, self.a.news_field_text)
        self.assertEqual(sha(p), meta["r0_prompt_sha256"])

    def test_core_concepts_article_a(self):
        cs = ov.core_concepts(self.sc)
        self.assertEqual([c["concept"] for c in cs], ["C1", "C2", "C4", "C5"])
        self.assertEqual(cs[1]["surfaces"], ["最大134,515人", "134,515人"])

    def test_after_differs_from_before_only_by_added_lines(self):
        o = ov.build_overlay(self.sc, self._judge())
        self.assertEqual(o["violations"], [])
        self.assertEqual(o["n_approximate_ok"], 1)
        before_news = self.a.news_field_text
        after_news = ov.apply_to_news_field(self.a.facts_text, self.a.constraints_text, o, prod.CONS_HEADING, prod.compose_news_field)
        added_lines = ov.constraint_lines(o)
        self.assertEqual(len(added_lines), 2)
        self.assertEqual(after_news, before_news.rstrip("\n") + "\n" + "\n".join(added_lines) + "\n")
        bp = w1.build_r0_prompt(self.story, before_news)
        ap = ov.apply_rule8(w1.build_r0_prompt(self.story, after_news), o)
        # Fact本文部(【事実1】〜)は完全一致、差分は追記行+規則8のみ
        self.assertEqual(ap.replace(ov.RULE8_TEXT, "").replace("\n".join(added_lines) + "\n", ""), bp)

    def test_exact_only_prompt_byte_identical(self):
        o = ov.build_overlay(self.sc, self._judge(approx_c2=False))
        after_news = ov.apply_to_news_field(self.a.facts_text, self.a.constraints_text, o, prod.CONS_HEADING, prod.compose_news_field)
        self.assertEqual(after_news, self.a.news_field_text)
        bp = w1.build_r0_prompt(self.story, self.a.news_field_text)
        self.assertEqual(ov.apply_rule8(w1.build_r0_prompt(self.story, after_news), o), bp)


if __name__ == "__main__":
    unittest.main()


class TestV7Collision(unittest.TestCase):
    def test_equal_rounded_values_in_same_fact_are_blocked(self):
        sc = {"facts": [{"n": 1, "ledger_ids": ["F08"]}],
              "numbers": [{"surface": "0.0630", "kind": "magnitude", "class": "core", "concept": "C5", "ledger_ids": ["F08"], "role": ""},
                          {"surface": "0.0589", "kind": "magnitude", "class": "peripheral", "concept": "C6", "ledger_ids": ["F08"], "role": ""}]}
        j = {"decisions": [{"concept": "C5", "decision": "APPROXIMATE_OK", "surfaces": [{"surface": "0.0630", "approx_surface": "約0.06"}],
                            "reason": "", "basis_fact_ids": ["F08"], "approved_condition": ""}]}
        o = ov.build_overlay(sc, j)
        self.assertEqual(o["entries"][0]["final_decision"], "EXACT_REQUIRED")
        self.assertTrue(any(x.startswith("0.0630:V7") for x in o["entries"][0]["downgrade_reasons"]))

    def test_trailing_zero_drop_is_not_rounding(self):
        self.assertTrue(any(x.startswith("V3_not_ordinary") for x in ov.validate_surface_approx("0.0630", "約0.063")))
