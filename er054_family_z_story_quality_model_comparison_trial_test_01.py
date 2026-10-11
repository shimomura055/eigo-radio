# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-QUALITY-MODEL-COMPARISON-TRIAL-01 委任_01 test(API呼出なし)。"""
import os
import re
import sys
import tempfile
import unittest

import er006_model_routing_contract_01 as routing
import er054_family_z_story_pool_trial_common_01 as common
import er054_family_z_story_quality_model_comparison_trial_01 as drv
import er054_family_z_story_quality_model_comparison_analysis_01 as ana

HERE = os.path.dirname(os.path.abspath(__file__))


class T(unittest.TestCase):
    def test_allowed_model_only_luna(self):
        self.assertEqual(drv.ALLOWED_MODELS, ("gpt-6-luna",))
        self.assertEqual(drv.PRIMARY_MODEL, "gpt-6-luna")
        for bad in ("gpt-6-astra", "gpt-6.1-sol", "gpt-5.6-luna"):
            with self.assertRaises(Exception):
                drv.run_task("A", "L01", 1, bad, drv.MockClient(), tempfile.mkdtemp(), True)

    def test_main_rejects_other_model(self):
        sys.argv = ["x", "--mode", "mock", "--models", "gpt-6-astra"]
        with self.assertRaises(SystemExit):
            drv.main()

    def test_real_refused_without_budget(self):
        for extra in ([], ["--approved-budget-jpy", "0"]):
            sys.argv = ["x", "--mode", "real"] + extra
            with self.assertRaises(SystemExit) as cm:
                drv.main()
            self.assertIn("STOP", str(cm.exception))

    def test_real_refused_when_cap_exceeds_budget(self):
        sys.argv = ["x", "--mode", "real", "--approved-budget-jpy", "1"]
        with self.assertRaises(SystemExit) as cm:
            drv.main()
        self.assertIn("超える", str(cm.exception))

    def test_sealed_deny(self):
        for p in ("er054_output/family_z_story_pool_trial_01/SEALED_PAST_RESULTS_L01_L06.json",
                  "er054_output/family_z_story_pool_trial_01/PHASE_C_RESULTS_02.md",
                  "er054_output/family_z_story_pool_trial_01/phase_c_eval/gpt-6-luna/L05.json"):
            with self.assertRaises(drv.SealedAccessError):
                drv.assert_not_sealed(p)
        drv.assert_not_sealed("er054_output/family_z_story_pool_trial_01/sources/L05/text_plain.txt")

    def test_prompt_has_no_past_results(self):
        for m in drv.METHODS:
            mm = drv.load_method(m)
            blob = mm["developer"] + mm["criteria"]
            self.assertNotIn("4/4", blob)
            self.assertNotIn("前回", blob)
            msgs = drv.build_messages(mm, drv.build_unit("L05"), "t")
            self.assertEqual(msgs[0]["role"], "developer")
            self.assertTrue(msgs[0]["content"].startswith(drv.DEVELOPER_BASE))  # 共通骨子
            self.assertIn(f"[方式{m}", msgs[1]["content"])

    def test_schema_axes_consistent(self):
        for m in drv.METHODS:
            sch = drv.load_method(m)["schema"]
            self.assertTrue(sch["strict"])
            props = sch["schema"]["properties"]
            for ax in drv.AXES[m]:
                self.assertIn(ax, props)
            self.assertEqual(set(sch["schema"]["required"]), set(props))

    def test_production_key_unchanged(self):
        self.assertIn(drv.ROUTING_KEY, common.TRIAL_KEYS)
        self.assertEqual(routing.PROCESS_MODEL_MAP[drv.ROUTING_KEY], "gpt-6-luna")
        for f in ("er054_family_z_story_quality_model_comparison_trial_01.py", "er054_family_z_story_quality_model_comparison_analysis_01.py"):
            src = open(os.path.join(HERE, f), encoding="utf-8").read()
            self.assertIsNone(re.search(r"PROCESS_MODEL_MAP\s*\[[^\]]+\]\s*=[^=]", src))

    def test_spearman_and_ranks(self):
        self.assertAlmostEqual(ana.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(ana.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertIsNone(ana.spearman([1, 1, 1], [1, 2, 3]))
        self.assertEqual(ana.ranks([0.9, 0.5, 0.5, 0.1]), [1.0, 2.5, 2.5, 4.0])
        self.assertAlmostEqual(ana.spearman([1, 2, 2, 4], [1, 3, 2, 4]), 0.9487, places=3)

    def _res(self, scores, reason="普通"):
        r = {"key_facts": {"central_event": "x", "main_characters": ["a"], "turning_point": "", "ending": ""},
             "overall": {"score": 3, "comment": ""}}
        for ax, s in zip(drv.AXES["A"], scores):
            r[ax] = {"score": s, "evidence_quotes": ["q"], "reason": reason}
        return r

    def test_contradiction_detection(self):
        r = self._res([4, 4, 4, 5], reason="文体が魅力の中心で短縮すると魅力が失われる")
        kinds = [c["kind"] for c in ana.detect_contradictions("A", r)]
        self.assertIn("weak_word_vs_high_score", kinds)
        low = ana.detect_contradictions("A", self._res([2, 2, 2, 2], reason="魅力が失われる"))
        self.assertEqual([c for c in low if c["kind"] == "weak_word_vs_high_score"], [])
        neg = ana.detect_contradictions("A", self._res([5, 5, 5, 5], reason="魅力は失われない。再現も困難ではない"))
        self.assertEqual([c for c in neg if c["kind"] == "weak_word_vs_high_score"], [])
        r2 = self._res([5, 5, 5, 5])
        r2["overall"]["score"] = 2
        self.assertIn("overall_axes_gap", [c["kind"] for c in ana.detect_contradictions("A", r2)])

    def test_contradiction_method_B_and_D(self):
        rb = {"overall": {"verdict": "PASS", "comment": ""},
              "consistency_check": {"self_reported_weaknesses": ["a"], "contradictions_found": ["x"], "verdicts_revised": False}}
        for ax in drv.AXES["B"]:
            rb[ax] = {"verdict": "PASS", "evidence_quotes": ["q"], "reason": "良い", "weakness": "なし"}
        rb["D"]["reason"] = "短縮すると消える"
        kinds = [c["kind"] for c in ana.detect_contradictions("B", rb)]
        self.assertIn("weak_word_vs_high_score", kinds)
        self.assertIn("self_reported_contradiction_not_revised", kinds)
        rd = {"overall": {"score": 5, "comment": ""},
              "lost_in_compression": [{"element": "a", "severity": "high"}, {"element": "b", "severity": "high"}]}
        for ax in drv.AXES["D"]:
            rd[ax] = {"score": 5, "evidence_quotes": ["q"], "reason": "良い"}
        kinds = [c["kind"] for c in ana.detect_contradictions("D", rd)]
        self.assertIn("lost_high_vs_loss_severity_score", kinds)
        self.assertIn("lost_high_vs_overall", kinds)

    def test_quote_mismatch_vs_near(self):
        src = "吾輩は猫である。名前はまだ無い。どこで生れたかとんと見当がつかぬ。"
        self.assertEqual(ana.classify_unverified("どこで生れたかとんと見当がつかない", src), "near")
        self.assertEqual(ana.classify_unverified("完全に無関係な文章がここにあります", src), "absent")

    def test_extreme_detection_and_normalization(self):
        full, floor = self._res([5, 5, 5, 5]), self._res([1, 1, 1, 1])
        self.assertTrue(ana.is_full("A", full))
        self.assertTrue(ana.is_floor("A", floor))
        self.assertEqual(ana.primary_norm("A", full), 1.0)
        self.assertEqual(ana.primary_norm("A", floor), 0.0)
        recs = []
        for w in ("L01", "L02", "L03"):
            for rep in (1, 2):
                recs.append({"method": "A", "work_id": w, "rep": rep, "result": self._res([5, 5, 5, 5]), "elapsed_sec": 1, "usage": None,
                             "quote_verification": {"quote_total": 4, "unverified_quote_count": 0,
                                                    "per_axis": {ax: [True] for ax in drv.AXES["A"]}}})
        A = ana.analyze(recs)
        self.assertTrue(any("天井" in f for f in A["extreme"]["A"]))
        self.assertTrue(any("分散ゼロ" in f for f in A["extreme"]["A"]))

    def test_budget_guard(self):
        g = drv.BudgetGuard(1.0)
        self.assertTrue(g.can_start(0.5))
        g.add(0.6)
        self.assertFalse(g.can_start(0.5))
        self.assertTrue(g.stopped)
        self.assertFalse(g.can_start(0.0))

    def test_mock_end_to_end_parallel(self):
        out = tempfile.mkdtemp()
        recs = drv.run_all(("A", "B", "C", "D"), ("L01", "L05"), 2, "gpt-6-luna", drv.MockClient(), out, 4, True)
        self.assertEqual(len(recs), 16)
        self.assertTrue(all("result" in r and r["quote_verification"]["all_verified"] for r in recs))
        files = {os.path.join(d, f) for d, _, fs in os.walk(out) for f in fs}
        self.assertEqual(len(files), 16)  # 方式×作品×rep別ファイル
        A = ana.analyze(ana.load_records(out), {w: drv.build_unit(w)["text"] for w in ("L01", "L05")})
        self.assertEqual(A["methods"], ["A", "B", "C", "D"])

    def test_model_mismatch_stops(self):
        class C(drv.MockClient):
            def create(self, **kw):
                r = super().create(**kw)

                class R2:
                    model = "gpt-6-astra"
                    id = "x"
                    output_text = r.output_text
                    usage = r.usage
                return R2()
        with self.assertRaises(drv.ModelMismatch):
            drv.run_task("A", "L01", 1, "gpt-6-luna", C(), tempfile.mkdtemp(), False)

    def test_budget_guard_stops_run_all(self):
        out = tempfile.mkdtemp()
        g = drv.BudgetGuard(0.5)  # 1 callの上限見積(約0.4円)は通るが2call目以降は止まる
        recs = drv.run_all(("A",), ("L01", "L02", "L03"), 1, "gpt-6-luna", drv.MockClient(), out, 1, True, g)
        self.assertTrue(g.stopped)
        self.assertTrue(any("skipped" in r for r in recs))

    def test_cost_estimate_consistent_with_prior(self):
        # 前回9call: 入力59,739tok・出力17,766tok → 約2.38円(実測)
        pr = drv.load_prices("gpt-6-luna")
        self.assertAlmostEqual(drv.cost_jpy(pr, sum(drv.MEASURED_INPUT_TOK.values()), 17766), 2.38, places=2)
        e2, e3 = drv.estimate(2), drv.estimate(3)
        self.assertEqual(e2["calls"], 72)
        self.assertEqual(e3["calls"], 108)
        self.assertAlmostEqual(e3["total_point_jpy"] / e2["total_point_jpy"], 1.5, places=3)


if __name__ == "__main__":
    unittest.main()
