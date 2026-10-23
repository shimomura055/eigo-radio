# -*- coding: utf-8 -*-
"""er095_b3_core_number_rounding_01 の単体test(API 0、費用0円。Luna実呼出なし=C-2)。
実行: .venv/Scripts/python.exe -m pytest er095_b3_core_number_rounding_01_test_01.py -q
構成: (A) Trial_01 test 移植(V1〜V7・overlay・規則原文一致・記事A実データ) (B) V8/V8b + 保存済みLuna判断90件の回帰
      (C) 永続化・読込(resume/regeneration/stale/改ざん/flag OFF) (D) judge call(モックclient: model_id/effort/fail-closed)
      (E) DefaultOffIsolation(未配線: Production .pyからimportされない、flag OFF/overlay無でバイト一致)
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import types
import unittest
from decimal import Decimal

import er095_b3_core_number_rounding_01 as m
import er053_family_x_factlock_ja_writer_01 as w1
import er053_b3_deterministic_producer_01 as prod
import er053_b3_annotation_contract_01 as contract

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_A = os.path.join(HERE, "er019_output", "paycheck_personality", "run_pp_01")
V8_FIXTURE = os.path.join(HERE, "er090_output", "b3_core_number_rounding_trial_02", "evidence", "v8_regression_90.json")


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


# ===================== (A) Trial_01 test 移植 =====================
class TestRounding(unittest.TestCase):
    def test_ordinary_rounding_ok(self):
        self.assertEqual(m.validate_surface_approx("最大134,515人", "最大約13万5千人"), [])
        self.assertEqual(m.validate_surface_approx("134,515人", "約13万5000人"), [])
        self.assertEqual(m.validate_surface_approx("134,515人", "約13万人"), [])
        self.assertEqual(m.validate_surface_approx("1,332", "約1,300"), [])
        self.assertEqual(m.validate_surface_approx("295億9,100万ドル", "約296億ドル"), [])

    def test_not_ordinary_rounding(self):
        self.assertTrue(any(x.startswith("V3_not_ordinary") for x in m.validate_surface_approx("134,515人", "約13万4千人")))
        self.assertTrue(any(x.startswith("V3_not_ordinary") for x in m.validate_surface_approx("134,515人", "約14万人")))

    def test_qualifier_unit_hedge(self):
        self.assertIn("V4_qualifier_dropped(最大)", m.validate_surface_approx("最大134,515人", "約13万5千人"))
        self.assertTrue(any(x.startswith("V4_unit") for x in m.validate_surface_approx("134,515人", "約13万5千件")))
        self.assertIn("V5_no_hedge_word", m.validate_surface_approx("134,515人", "13万5千人"))
        self.assertIn("V5_approx_missing", m.validate_surface_approx("134,515人", None))
        self.assertIn("V3_approx_equals_exact", m.validate_surface_approx("約134,515人", "約134,515人"))

    def test_single_digit_cannot_be_rounded(self):
        self.assertNotEqual(m.validate_surface_approx("3回以上", "約3回以上"), [])


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
        self.assertEqual([c["concept"] for c in m.core_concepts(self.SIDECAR)], ["C1", "C2"])
        self.assertEqual(m.core_concepts(self.SIDECAR)[1]["surfaces"], ["最大134,515人", "134,515人"])

    def test_accept_valid(self):
        o = m.build_overlay(self.SIDECAR, self.judge())
        self.assertEqual([e["final_decision"] for e in o["entries"]], ["EXACT_REQUIRED", "APPROXIMATE_OK"])
        self.assertEqual(o["violations"], [])
        self.assertEqual(len(m.constraint_lines(o)), 2)
        self.assertTrue(all("事実2について：【概数表記】" in l for l in m.constraint_lines(o)))

    def test_downgrade_invalid_rounding(self):
        j = self.judge()
        j["decisions"][1]["surfaces"][0]["approx_surface"] = "最大約14万人"
        o = m.build_overlay(self.SIDECAR, j)
        self.assertEqual(o["entries"][1]["final_decision"], "EXACT_REQUIRED")
        self.assertTrue(o["entries"][1]["downgrade_reasons"])
        self.assertEqual(m.constraint_lines(o), [])

    def test_concept_set_mismatch_fail_closed(self):
        j = self.judge()
        j["decisions"].append({"concept": "C9", "decision": "APPROXIMATE_OK", "surfaces": [], "reason": "", "basis_fact_ids": [], "approved_condition": ""})
        o = m.build_overlay(self.SIDECAR, j)
        self.assertTrue(o["violations"])
        self.assertTrue(all(e["final_decision"] == "EXACT_REQUIRED" for e in o["entries"]))
        j2 = self.judge()
        j2["decisions"].reverse()
        self.assertTrue(m.build_overlay(self.SIDECAR, j2)["violations"])

    def test_garbage_judge_json_fail_closed(self):
        for bad in (None, [], {"decisions": "x"}, {"decisions": [None]}):
            o = m.build_overlay(self.SIDECAR, bad)
            self.assertEqual(o["n_approximate_ok"], 0)

    def test_no_op_when_exact_only(self):
        j = self.judge()
        j["decisions"][1]["decision"] = "EXACT_REQUIRED"
        o = m.build_overlay(self.SIDECAR, j)
        self.assertEqual(o["n_approximate_ok"], 0)
        cons = "Writerへの注意(事実ではありません)：\n- 事実2について：x\n"
        self.assertEqual(m.apply_to_constraints(cons, o, "H"), cons)
        self.assertEqual(m.apply_rule8("PROMPT", o), "PROMPT")
        self.assertEqual(m.apply_rule8("PROMPT", None), "PROMPT")

    def test_basis_fact_id_mismatch_downgrades(self):
        j = self.judge()
        j["decisions"][1]["basis_fact_ids"] = ["F99"]
        self.assertEqual(m.build_overlay(self.SIDECAR, j)["entries"][1]["final_decision"], "EXACT_REQUIRED")


class TestApprovedRuleText(unittest.TestCase):
    def test_spoken_first_text_matches_current_spec(self):
        with open(os.path.join(HERE, "CURRENT_SPEC.md"), encoding="utf-8") as f:
            line = next(l for l in f if l.startswith("| Spoken-first Number Treatment |"))
        self.assertIn(m.SPOKEN_FIRST_NUMBER_TREATMENT_TEXT, line)

    def test_judge_prompt_embeds_verbatim_rules(self):
        p = m.build_judge_user_prompt(storyline="S", facts_text="- 【事実1】a", constraints_text="", sidecar=TestOverlayLogic.SIDECAR,
                                      ledger_records={"F04": "[VERIFIED] F04: x"})
        self.assertIn(m.LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK, p)
        self.assertIn(m.NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK, p)
        self.assertIn(m.SPOKEN_FIRST_NUMBER_TREATMENT_TEXT, p)
        self.assertNotIn("期待ラベル", p)

    def test_judge_prompt_identical_to_validated_trial_prompt(self):
        """Trial_02で検証済みPrompt v2とバイト一致(Production移植でPromptを変えていない証拠)。"""
        import er090_b3_core_number_rounding_trial_01_overlay as t1
        kw = dict(storyline="S", facts_text="- 【事実1】a", constraints_text="C", sidecar=TestOverlayLogic.SIDECAR,
                  ledger_records={"F04": "[VERIFIED] F04: x", "F08": "[VERIFIED] F08: y"})
        self.assertEqual(m.build_judge_user_prompt(**kw), t1.build_judge_user_prompt(**kw))
        self.assertEqual(m.JUDGE_DEVELOPER_MESSAGE, t1.JUDGE_DEVELOPER_MESSAGE)
        self.assertEqual(m.JUDGE_JSON_SCHEMA, t1.JUDGE_JSON_SCHEMA)
        self.assertEqual(m.RULE8_TEXT, t1.RULE8_TEXT)


@unittest.skipUnless(os.path.exists(os.path.join(RUN_A, "storyline_b3", "annotation.json")), "run_pp_01 artifacts missing")
class TestArticleAReal(unittest.TestCase):
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
        self.assertEqual(sha(w1.build_r0_prompt(self.story, self.a.news_field_text)), meta["r0_prompt_sha256"])

    def test_core_concepts_article_a(self):
        cs = m.core_concepts(self.sc)
        self.assertEqual([c["concept"] for c in cs], ["C1", "C2", "C4", "C5"])
        self.assertEqual(cs[1]["surfaces"], ["最大134,515人", "134,515人"])

    def test_after_differs_from_before_only_by_added_lines(self):
        o = m.build_overlay(self.sc, self._judge())
        self.assertEqual(o["violations"], [])
        self.assertEqual(o["n_approximate_ok"], 1)
        after_news = m.apply_to_news_field(self.a.facts_text, self.a.constraints_text, o, prod.CONS_HEADING, prod.compose_news_field)
        added = m.constraint_lines(o)
        self.assertEqual(len(added), 2)
        self.assertEqual(after_news, self.a.news_field_text.rstrip("\n") + "\n" + "\n".join(added) + "\n")
        bp = w1.build_r0_prompt(self.story, self.a.news_field_text)
        ap = m.apply_rule8(w1.build_r0_prompt(self.story, after_news), o)
        self.assertEqual(ap.replace(m.RULE8_TEXT, "").replace("\n".join(added) + "\n", ""), bp)

    def test_exact_only_prompt_byte_identical(self):
        o = m.build_overlay(self.sc, self._judge(approx_c2=False))
        after_news = m.apply_to_news_field(self.a.facts_text, self.a.constraints_text, o, prod.CONS_HEADING, prod.compose_news_field)
        self.assertEqual(after_news, self.a.news_field_text)
        self.assertEqual(m.apply_rule8(w1.build_r0_prompt(self.story, after_news), o), w1.build_r0_prompt(self.story, self.a.news_field_text))

    def test_ledger_exact_values_untouched(self):
        """Ledgerの正確な数値はoverlay処理で変更されない(overlayはLedgerを読むだけ。入力文字列とsha不変)。"""
        lp = os.path.join(RUN_A, "research_ledger", "verified_fact_ledger.txt")
        before = sha(open(lp, encoding="utf-8").read())
        m.build_overlay(self.sc, self._judge())
        m.parse_ledger_records(open(lp, encoding="utf-8").read())
        self.assertEqual(sha(open(lp, encoding="utf-8").read()), before)
        self.assertIn("134,515", open(lp, encoding="utf-8").read())


class TestV7Collision(unittest.TestCase):
    def test_equal_rounded_values_in_same_fact_are_blocked(self):
        sc = {"facts": [{"n": 1, "ledger_ids": ["F08"]}],
              "numbers": [{"surface": "0.0630", "kind": "magnitude", "class": "core", "concept": "C5", "ledger_ids": ["F08"], "role": ""},
                          {"surface": "0.0589", "kind": "magnitude", "class": "peripheral", "concept": "C6", "ledger_ids": ["F08"], "role": ""}]}
        j = {"decisions": [{"concept": "C5", "decision": "APPROXIMATE_OK", "surfaces": [{"surface": "0.0630", "approx_surface": "約0.06"}],
                            "reason": "", "basis_fact_ids": ["F08"], "approved_condition": ""}]}
        o = m.build_overlay(sc, j)
        self.assertEqual(o["entries"][0]["final_decision"], "EXACT_REQUIRED")
        self.assertTrue(any(x.startswith("0.0630:V7") for x in o["entries"][0]["downgrade_reasons"]))

    def test_trailing_zero_drop_is_not_rounding(self):
        self.assertTrue(any(x.startswith("V3_not_ordinary") for x in m.validate_surface_approx("0.0630", "約0.063")))


# ===================== (B) V8 / V8b =====================
class TestV8(unittest.TestCase):
    def test_boundary_inclusive_10pct(self):
        # 100 -> 110 はちょうど10%(以内=通る)。有効数字の丸めとして成立する例を使う: 1,050人 -> 約1,100人 (4.76%) / 14 -> 約10 (28.6%)
        self.assertEqual([x for x in m.validate_surface_approx("1,050人", "約1,100人") if x.startswith("V8")], [])
        self.assertTrue(any(x.startswith("V8_relative_error_over_10pct") for x in m.validate_surface_approx("14", "約10")))
        self.assertTrue(m.relative_error("100", "約110") == Decimal("0.1"))
        self.assertEqual([x for x in m.validate_surface_approx("100", "約110") if x.startswith("V8")], [])    # 境界は含む(10%以内)
        self.assertTrue(any(x.startswith("V8_rel") for x in m.validate_surface_approx("100", "約111")))

    def test_decimal_percent_rounding_default_passes(self):
        # 承認済み既定: 25.2%->約25%、44.7%->約45%、89.6%->約90%(er003_v1_n3_01_evidence_compression_editor.py:121-131)
        for ex, ap in (("25.2%", "約25%"), ("44.7%", "約45%"), ("89.6%", "約90%")):
            self.assertEqual(m.validate_surface_approx(ex, ap), [], (ex, ap))

    def test_over_10pct_known_cases_rejected(self):
        self.assertTrue(any(x.startswith("V8_rel") for x in m.validate_surface_approx("約2.6％", "約3％")))
        self.assertTrue(any(x.startswith("V8_rel") for x in m.validate_surface_approx("14", "約10")))

    def test_already_approximate_not_rerounded(self):
        self.assertIn("V8b_already_approximate_not_rerounded", m.validate_surface_approx("約348億ドル", "約350億ドル"))
        self.assertIn("V8b_already_approximate_not_rerounded", m.validate_surface_approx("およそ1,332人", "約1,300人"))
        self.assertNotIn("V8b_already_approximate_not_rerounded", m.validate_surface_approx("最大134,515人", "最大約13万5千人"))

    def test_v8_unavailable_is_fail_closed(self):
        self.assertIn("V8_relative_error_unavailable", m.validate_surface_approx("数十人", "約30人"))

    def test_v8_in_overlay_downgrades_to_exact(self):
        sc = {"facts": [{"n": 1, "ledger_ids": ["F02"]}],
              "numbers": [{"surface": "14", "kind": "magnitude", "class": "core", "concept": "C1", "ledger_ids": ["F02"], "role": ""}]}
        j = {"decisions": [{"concept": "C1", "decision": "APPROXIMATE_OK", "surfaces": [{"surface": "14", "approx_surface": "約10"}],
                            "reason": "", "basis_fact_ids": ["F02"], "approved_condition": ""}]}
        o = m.build_overlay(sc, j)
        self.assertEqual(o["entries"][0]["final_decision"], "EXACT_REQUIRED")
        self.assertTrue(any("V8_relative_error_over_10pct" in r for r in o["entries"][0]["downgrade_reasons"]))
        self.assertEqual(m.constraint_lines(o), [])


@unittest.skipUnless(os.path.exists(V8_FIXTURE), "v8_regression_90.json missing")
class TestV8Regression90(unittest.TestCase):
    """保存済みLuna判断90件(Trial_02 judge_eval.json由来)の回帰: V8=6件拒否、V8b=11件拒否(うち5件はV8と重複)=合計12件拒否(全て事前登録ラベルE)、事前登録ラベルA(正しい丸め)の誤拒否0。"""

    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(V8_FIXTURE, encoding="utf-8"))

    def test_fixture_shape(self):
        self.assertEqual(self.d["n"], 90)
        self.assertEqual(self.d["n_expected_reject"], 6)
        self.assertEqual(self.d["n_expected_reject_v8b"], 11)      # 約348億x6 + 約2.6％x5(後者はV8とも重複)
        self.assertEqual(self.d["n_expected_reject_label_A"], 0)

    def test_v8_rejects_exactly_the_expected_6(self):
        rej = [i for i in self.d["items"] if any(x.startswith("V8_") for x in m.validate_surface_approx(i["surface"], i["approx"]))]
        exp = [i for i in self.d["items"] if i["expected_v8"] == "REJECT"]
        self.assertEqual(len(rej), 6)
        self.assertEqual([(i["run"], i["article"], i["concept"]) for i in rej], [(i["run"], i["article"], i["concept"]) for i in exp])

    def test_v8b_rejects_exactly_the_expected_11(self):
        rej = [i for i in self.d["items"] if "V8b_already_approximate_not_rerounded" in m.validate_surface_approx(i["surface"], i["approx"])]
        exp = [i for i in self.d["items"] if i["expected_v8b_already_approx"] == "REJECT"]
        self.assertEqual(len(rej), 11)
        self.assertEqual([(i["run"], i["article"], i["concept"]) for i in rej], [(i["run"], i["article"], i["concept"]) for i in exp])

    def test_union_of_v8_and_v8b_rejects_12_all_label_E(self):
        rej = [i for i in self.d["items"] if any(x.startswith("V8") for x in m.validate_surface_approx(i["surface"], i["approx"]))]
        self.assertEqual(len(rej), 12)
        self.assertEqual({i["label_prereg"] for i in rej}, {"E"})

    def test_no_correct_rounding_blocked(self):
        for i in self.d["items"]:
            if i["label_prereg"] == "A":
                iss = m.validate_surface_approx(i["surface"], i["approx"])
                self.assertFalse([x for x in iss if x.startswith("V8")], (i["surface"], i["approx"], iss))


# ===================== (C) 永続化・読込 =====================
class _FakeAnnotated:
    def __init__(self, sidecar, md_sha="SHA_A", md="## Storyline\nS\n\n## Selected Facts\n- 【事実1】a\n", constraints=""):
        self.sidecar, self.annotated_md_sha256, self.annotated_md_text, self.constraints_text = sidecar, md_sha, md, constraints


def _judge_ok(client, prompt, tag):
    return {"parsed": TestOverlayLogic().judge(), "model_requested": "gpt-6-luna", "model_returned": "gpt-6-luna-2026-10-01",
            "response_id": "resp_x", "sec": 1.0, "effort": "low", "usage": {"input_tokens": 1, "output_tokens": 1, "reasoning_tokens": 0}}


class TestPersistenceAndResume(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.d = tempfile.mkdtemp()
        self.ann = _FakeAnnotated(TestOverlayLogic.SIDECAR)
        self.parse = lambda md: ("S", "- 【事実1】a")

    def run_it(self, judge=_judge_ok, ann=None):
        return m.run_core_number_rounding(None, self.d, ann or self.ann, self.parse, "[VERIFIED] F04: x\n", judge=judge)

    def test_first_run_writes_overlay_with_provenance(self):
        r = self.run_it()
        self.assertEqual((r["status"], r["api_calls"], r["n_approximate_ok"]), ("OK", 1, 1))
        ov = json.load(open(m.overlay_path(self.d), encoding="utf-8"))
        self.assertEqual(ov["judge"]["model_returned"], "gpt-6-luna-2026-10-01")
        self.assertEqual((ov["requested_model"], ov["requested_effort"], ov["role_key"]), ("gpt-6-luna", "low", m.ROLE_KEY))
        for k in ("user_prompt_sha256", "developer_message_sha256", "json_schema_sha256", "response_id", "usage"):
            self.assertIn(k, ov["judge"])
        self.assertEqual(ov["overlay_sha256"], m.overlay_canonical_sha(ov))

    def test_resume_and_writer_regeneration_reuse_without_api(self):
        self.run_it()
        calls = []
        r2 = self.run_it(judge=lambda *a, **k: calls.append(1) or _judge_ok(*a))
        self.assertEqual((r2["reused"], r2["api_calls"], calls), (True, 0, []))
        ov, ev = m.load_overlay_for_writer(self.d, "SHA_A")      # Writer初回/retry/symbol再生成/resumeはすべてこの入口
        self.assertTrue(ev["applied"])
        self.assertEqual(len(m.constraint_lines(ov)), 2)

    def test_stale_overlay_ignored_and_rejudged_when_b3_regenerated(self):
        self.run_it()
        ov, ev = m.load_overlay_for_writer(self.d, "SHA_B")      # B3再生成後の別注記sha
        self.assertIsNone(ov)
        self.assertEqual(ev["reason"], "stale_annotated_md_sha_mismatch")
        r = self.run_it(ann=_FakeAnnotated(TestOverlayLogic.SIDECAR, md_sha="SHA_B"))
        self.assertEqual((r["reused"], r["api_calls"]), (False, 1))

    def test_tampered_overlay_ignored(self):
        self.run_it()
        p = m.overlay_path(self.d)
        ov = json.load(open(p, encoding="utf-8"))
        ov["entries"][1]["surfaces"][0]["approx"] = "最大約99万人"
        json.dump(ov, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        o, ev = m.load_overlay_for_writer(self.d, "SHA_A")
        self.assertIsNone(o)
        self.assertEqual(ev["reason"], "overlay_sha_mismatch")

    def test_judge_api_error_fail_closed_continues(self):
        def boom(*a, **k):
            raise OSError("api down")
        r = self.run_it(judge=boom)
        self.assertEqual((r["status"], r["n_approximate_ok"]), (m.STATUS_API_ERROR, 0))
        o, ev = m.load_overlay_for_writer(self.d, "SHA_A")
        self.assertIsNone(o)           # 丸めなし=従来と同一出力
        self.assertTrue(ev["reason"].startswith("status_"))

    def test_json_parse_error_is_api_error_status(self):
        def bad_json(*a, **k):
            json.loads("not json")
        self.assertEqual(self.run_it(judge=bad_json)["status"], m.STATUS_API_ERROR)

    def test_structure_error_is_internal_error_status_separate_from_api_error(self):
        def keyerr(*a, **k):
            raise KeyError("decisions")
        r = self.run_it(judge=keyerr)
        self.assertEqual(r["status"], m.STATUS_INTERNAL_ERROR)
        self.assertNotEqual(m.STATUS_INTERNAL_ERROR, m.STATUS_API_ERROR)

    def test_unexpected_exception_types_are_not_swallowed(self):
        """P-03: 捕捉対象はAPI/通信・JSON・model不一致・構造不正に絞る。想定外の例外型(例: RuntimeError)は握りつぶさず伝播。"""
        def boom(*a, **k):
            raise RuntimeError("something else")
        with self.assertRaises(RuntimeError):
            self.run_it(judge=boom)
        self.assertFalse(os.path.exists(m.overlay_path(self.d)))

    def test_routing_misconfiguration_stops_before_api_and_is_not_swallowed(self):
        """P-03: require_model(ROLE_KEY)はtryの外。設定ミス(ModelContractViolation)はAPI call前にSTOPし、overlayも書かない。"""
        import er006_model_routing_contract_01 as routing
        calls = []

        def bad_require(role, model):
            raise routing.ModelContractViolation("unregistered")
        with self.assertRaises(routing.ModelContractViolation):
            m.run_core_number_rounding(None, self.d, self.ann, self.parse, "[VERIFIED] F04: x\n",
                                       judge=lambda *a, **k: calls.append(1), require_model=bad_require)
        self.assertEqual(calls, [])
        self.assertFalse(os.path.exists(m.overlay_path(self.d)))

    def test_api_error_overlay_is_final_for_same_b3_version_and_reused(self):
        """P-01: 同一B3版のoverlayはstatusに関わらず確定値。JUDGE_API_ERRORでも再実行時にAPI call 0で再利用(再judgeしない)。"""
        def boom(*a, **k):
            raise OSError("down")
        self.run_it(judge=boom)
        calls = []
        r2 = self.run_it(judge=lambda *a, **k: calls.append(1) or _judge_ok(*a))
        self.assertEqual((r2["reused"], r2["api_calls"], r2["status"], calls), (True, 0, m.STATUS_API_ERROR, []))

    def test_force_rejudge_for_regenerate_writer(self):
        """P-01: --regenerate-stage writer は再判断する(force_rejudge=True)。"""
        self.run_it()
        calls = []
        r2 = m.run_core_number_rounding(None, self.d, self.ann, self.parse, "[VERIFIED] F04: x\n",
                                        judge=lambda *a, **k: calls.append(1) or _judge_ok(*a), force_rejudge=True)
        self.assertEqual((r2["reused"], r2["api_calls"], calls), (False, 1, [1]))

    def test_reuse_path_never_judges_new(self):
        """P-02: JA再利用経路(allow_judge=False)は新規判断をしない。overlay不在でもAPI 0・overlay書込0。有効な既存overlayは検査のみ。"""
        calls = []
        r = m.run_core_number_rounding(None, self.d, self.ann, self.parse, "[VERIFIED] F04: x\n",
                                       judge=lambda *a, **k: calls.append(1), allow_judge=False)
        self.assertEqual((r["status"], r["api_calls"], calls), ("NOT_JUDGED_REUSE_PATH", 0, []))
        self.assertFalse(os.path.exists(m.overlay_path(self.d)))
        self.run_it()
        r2 = m.run_core_number_rounding(None, self.d, self.ann, self.parse, "[VERIFIED] F04: x\n",
                                        judge=lambda *a, **k: calls.append(1), allow_judge=False)
        self.assertEqual((r2["status"], r2["reused"], r2["api_calls"], calls), ("OK", True, 0, []))

    def test_summarize_for_run_statuses(self):
        self.assertEqual(m.summarize_for_run(self.d)["status"], "OVERLAY_ABSENT")
        self.run_it()
        s = m.summarize_for_run(self.d)
        self.assertEqual((s["status"], s["n_approximate_ok"], s["warn"], s["effort"]), ("OK", 1, False, "low"))
        self.assertTrue(s["model_returned"].startswith("gpt-6-luna"))
        os.remove(m.overlay_path(self.d))
        self.run_it(judge=lambda *a, **k: (_ for _ in ()).throw(OSError("x")))
        s2 = m.summarize_for_run(self.d)
        self.assertEqual((s2["status"], s2["warn"]), (m.STATUS_API_ERROR, True))

    def test_check_resume_provenance_cases(self):
        """W5/P-01: legacy(キー無し)許容 / 一致OK(status不問) / 不一致STOP / 両方有効でない(flag切替)はSTOPせず記録のみ。"""
        self.assertEqual(m.check_resume_provenance(self.d, None)["mode"], "legacy_no_rounding_key")
        self.run_it()
        cur = m.current_overlay_sha(self.d)
        self.assertTrue(m.check_resume_provenance(self.d, {"enabled": True, "overlay_sha256": cur})["ok"])
        bad = m.check_resume_provenance(self.d, {"enabled": True, "overlay_sha256": "deadbeef"})
        self.assertEqual((bad["ok"], bad["mode"]), (False, "overlay_sha_mismatch"))
        sw = m.check_resume_provenance(self.d, {"enabled": False, "overlay_sha256": "deadbeef"})
        self.assertEqual((sw["ok"], sw["mode"]), (True, "flag_switch_not_compared"))
        m.B3_CORE_NUMBER_ROUNDING_ENABLED = False
        try:
            self.assertTrue(m.check_resume_provenance(self.d, {"enabled": True, "overlay_sha256": "deadbeef"})["ok"])   # rollback時はSTOPしない
        finally:
            m.B3_CORE_NUMBER_ROUNDING_ENABLED = True
        # status!=OK のoverlayでも照合対象(status不問)
        os.remove(m.overlay_path(self.d))
        self.run_it(judge=lambda *a, **k: (_ for _ in ()).throw(OSError("x")))
        cur2 = m.current_overlay_sha(self.d)
        self.assertTrue(m.check_resume_provenance(self.d, {"enabled": True, "overlay_sha256": cur2})["ok"])
        # overlay改ざんは INVALID: として検出(記録値と一致しない)
        p = m.overlay_path(self.d)
        ov = json.load(open(p, encoding="utf-8"))
        ov["note"] = "tampered"
        json.dump(ov, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        self.assertFalse(m.check_resume_provenance(self.d, {"enabled": True, "overlay_sha256": cur2})["ok"])

    def test_model_mismatch_fail_closed(self):
        def wrong(*a, **k):
            r = _judge_ok(*a)
            r["model_returned"] = "gpt-6.1-sol"
            return r
        self.assertEqual(self.run_it(judge=wrong)["status"], m.STATUS_API_ERROR)

    def test_no_core_numbers_no_api_call(self):
        sc = {"facts": [], "numbers": [{"surface": "x", "kind": "magnitude", "class": "peripheral", "concept": "P", "ledger_ids": ["F01"], "role": ""}]}
        calls = []
        r = self.run_it(judge=lambda *a, **k: calls.append(1), ann=_FakeAnnotated(sc))
        self.assertEqual((r["status"], r["api_calls"], calls), ("OK", 0, []))

    def test_flag_off_no_api_and_overlay_ignored(self):
        self.run_it()
        m.B3_CORE_NUMBER_ROUNDING_ENABLED = False
        try:
            calls = []
            r = self.run_it(judge=lambda *a, **k: calls.append(1))
            self.assertEqual((r["status"], r["api_calls"], calls), ("DISABLED", 0, []))
            o, ev = m.load_overlay_for_writer(self.d, "SHA_A")
            self.assertIsNone(o)
            self.assertEqual(ev["reason"], "flag_off")
        finally:
            m.B3_CORE_NUMBER_ROUNDING_ENABLED = True

    def test_overlay_absent_is_noop(self):
        o, ev = m.load_overlay_for_writer(self.d, "SHA_A")
        self.assertEqual((o, ev["reason"]), (None, "overlay_absent"))


# ===================== (D) judge call(モックclient。実API呼出なし) =====================
class TestJudgeCallMock(unittest.TestCase):
    def test_model_effort_schema_sent_and_provenance_returned(self):
        seen = {}

        class R:
            output_text = json.dumps({"decisions": []})
            model = "gpt-6-luna-2026-10-01"
            id = "resp_1"
            usage = types.SimpleNamespace(input_tokens=10, output_tokens=5, output_tokens_details=types.SimpleNamespace(reasoning_tokens=2))

        class C:
            class responses:
                @staticmethod
                def create(**kw):
                    seen.update(kw)
                    return R()
        guard = []
        import contextlib
        r = m.judge_call(C, "PROMPT", "tag", cost_logging_context=lambda t: contextlib.nullcontext(),
                         require_model=lambda role, model: guard.append((role, model)) or model)
        self.assertEqual(guard, [("FAMILY_X_B3_CORE_NUMBER_ROUNDING", "gpt-6-luna")])
        self.assertEqual((seen["model"], seen["reasoning"]), ("gpt-6-luna", {"effort": "low"}))
        self.assertEqual(seen["text"]["format"]["name"], "core_number_rounding_decision")
        self.assertEqual(seen["input"][1]["content"], "PROMPT")
        self.assertEqual((r["model_returned"], r["effort"], r["usage"]["reasoning_tokens"]), ("gpt-6-luna-2026-10-01", "low", 2))

    def test_routing_role_registration_is_unconditionally_asserted(self):
        """C-2 P-03: routing contractへの新role登録を無条件にassert(未登録なら即FAIL=設定ミスを黙認しない)。"""
        import er006_model_routing_contract_01 as routing
        self.assertEqual(routing.PROCESS_MODEL_MAP[m.ROLE_KEY], "gpt-6-luna")
        self.assertEqual(routing.require_model(m.ROLE_KEY, "gpt-6-luna"), "gpt-6-luna")
        with self.assertRaises(routing.ModelContractViolation):
            routing.require_model(m.ROLE_KEY, "gpt-6.1-sol")


# ===================== (E) DefaultOffIsolation(C-1: 未配線) =====================
class TestIsolation(unittest.TestCase):
    PROD_ALLOWED_C2 = {"er019_family_x_entertainment_production_runner_01.py", "er053_family_x_factlock_ja_writer_01.py"}

    def test_not_imported_by_any_production_py_in_c1(self):
        hits = []
        for p in glob.glob(os.path.join(HERE, "*.py")):
            b = os.path.basename(p)
            # FAMILY-Y-VOICES-DESIGN-01 委任_04: er110_(Family Y Trial harness=DEV/Trial専用、読み取りimportのみ、Production配線ではない)もer090_と同型に除外(test側のみ)
            if b.startswith("er095_") or b.startswith("er090_") or b.startswith("er110_"):
                continue
            if "er095_b3_core_number_rounding_01" in open(p, encoding="utf-8", errors="replace").read():
                hits.append(b)
        # C-2配線後: importするProductionファイルは Family X runner と Writer(w1)のみ(Family Z・他Familyのrunnerは不許可)。
        self.assertEqual(set(hits), self.PROD_ALLOWED_C2, hits)

    def test_family_z_runners_never_reference_module(self):
        for p in glob.glob(os.path.join(HERE, "er02[6-9]*.py")) + glob.glob(os.path.join(HERE, "*family_z*.py")):
            self.assertNotIn("er095_b3_core_number_rounding_01", open(p, encoding="utf-8", errors="replace").read(), p)

    def test_default_flag_is_true_and_documented(self):
        self.assertIs(m.B3_CORE_NUMBER_ROUNDING_ENABLED, True)

    def test_production_validators_unchanged_in_c1_or_s5_only(self):
        # S5(C-2)適用後は概数表記を含む。未適用なら含まない。いずれでも他のタグ語は従来どおり。
        for word in ("事実", "中核数値", "周辺数値"):
            self.assertIn(word, w1.TAG_LEAK_RE.pattern)


if __name__ == "__main__":
    unittest.main()
