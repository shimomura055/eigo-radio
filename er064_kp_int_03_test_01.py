# Round3 test: (b1)の静的不変条件(Prompt/コードに評価語句なし・アンカー不参照)、M2との整合(noop時byte一致)、逐語surface/canonical経路、
# rank上位3・append位置・source非表示、Stage1仕様(38 job)、Round1/2資産不変。有料呼出なし。
# 使い方: PYTHONPATH=. .venv/Scripts/python.exe er064_kp_int_03_test_01.py
import ast
import hashlib
import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.getcwd())
import er064_kp_idiom_trial_01_extractor as EX  # noqa: E402
import er064_kp_int_01_eval as EV  # noqa: E402
import er064_kp_int_01_machine as MC  # noqa: E402
import er064_kp_int_01_test_01 as T1  # noqa: E402
import er064_kp_int_03_b1 as B  # noqa: E402
import er064_kp_int_03_run as RUN3  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402
import er064_kp_opt_01_upstream_core as U  # noqa: E402

R1 = "er064_output/kp_integrated_opt_01/round1"
ANCHORS = json.load(open(f"{R1}/anchors_r1.json", encoding="utf-8"))["anchors"]
B1_FILES = ["er064_kp_int_03_b1.py", "er064_kp_int_03_run.py"]
EXTRA_BAN = ["concierge", "hormuz", "meta", "smallbag", "semi"]


class PromptHygiene(unittest.TestCase):
    def test_prompt_has_no_eval_words(self):
        t = EX.prompt_template().lower()
        for w in T1.BAN_PROMPT:
            self.assertNotIn(w, t, w)
        for a in ANCHORS:
            self.assertNotIn(a["label"].lower(), t, a["label"])
            self.assertIsNone(re.search(a["full"], t), a["label"])

    def test_prompt_examples_not_in_eval_articles(self):
        t = EX.prompt_template()
        ex = re.findall(r"外れ|out of the blue|a blessing in disguise|a cup of tea|go to school", t)
        self.assertTrue(ex)
        for k in MC.ARTICLE_KEYS:
            art = U.read_article(k).lower()
            for e in ("out of the blue", "a blessing in disguise", "a cup of tea", "go to school"):
                self.assertNotIn(e, art, (k, e))

    def test_prompt_is_phase_d_v3(self):
        self.assertTrue(EX.PROMPT_PATH.endswith("extractor_prompt_v3.txt"))
        self.assertEqual(EX.MIN_WORDS, 2)
        self.assertEqual(EX.MAX_WORDS, 5)
        self.assertEqual(B.ROUND3_CAP, 3)

    def test_code_has_no_eval_words(self):
        for f in B1_FILES:
            tree = ast.parse(open(f, encoding="utf-8").read())
            strs = [n.value.lower() for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
            for s in strs:
                for w in T1.BAN_CODE_STR:
                    if f.endswith("b1.py"):
                        self.assertNotIn(w, s, (f, w))

    def test_builder_does_not_read_anchors(self):
        src = open("er064_kp_int_03_b1.py", encoding="utf-8").read()
        self.assertNotIn("anchors_r1", src)
        self.assertNotIn("er064_kp_int_01_eval", src)


class B1Mechanics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        R._init()
        cls.key = "coffee_adv"
        cls.base, cls.st0, cls.ex = B.existing_for(cls.key)
        cls.units = cls.st0["sentence_units"]
        cls.art = U.read_article(cls.key)

    def test_noop_rows_identical_to_m2(self):
        out = B.build_pattern_m2b(self.key, [])
        self.assertTrue(out["noop_vs_M2"])
        self.assertEqual(out["rows_text"], self.base["rows_text"])

    def test_verbatim_check(self):
        self.assertTrue(B.is_verbatim("been behind price increases", self.units))
        self.assertTrue(B.is_verbatim("Been Behind Price Increases", self.units))
        self.assertFalse(B.is_verbatim("been behind the price increases", self.units))
        self.assertFalse(B.is_verbatim("behind increases price", self.units))

    def _parsed(self):
        return {"items": [
            {"rank": 3, "span": "waiting for the price", "core_span": "waiting for the price", "transparency": "semi", "kind": "nontransparent_collocation_or_phrasal", "reason_en": "x"},
            {"rank": 1, "span": "been behind price increases", "core_span": "been behind price increases", "transparency": "opaque", "kind": "figurative_or_metaphorical_use", "reason_en": "x"},
            {"rank": 2, "span": "made up words here", "core_span": "made up words here", "transparency": "semi", "kind": "idiom_or_fixed_expression", "reason_en": "x"},
            {"rank": 4, "span": "roasting and packing the beans", "core_span": "roasting and packing the beans", "transparency": "semi", "kind": "idiom_or_fixed_expression", "reason_en": "x"},
        ]}

    def test_rank_cap_verbatim_and_canonical_path(self):
        built = B.build_b1(self._parsed(), self.units, set(), self.art)
        acc = built["accepted"]
        self.assertLessEqual(len(acc), 3)
        self.assertEqual([c["llm_rank"] for c in acc], sorted(c["llm_rank"] for c in acc))
        self.assertTrue(any(v["verbatim"] is False for v in built["verbatim"]))
        c = next(c for c in acc if c["surface_form"].lower() == "been behind price increases")
        # M3: surface_formは逐語、canonical_formは(b2)ルール候補と同じ関数
        self.assertEqual(c["canonical_form"], B.EX.ext._normalize_key(c["surface_form"]))
        self.assertEqual(c["source_span"], c["surface_form"])
        self.assertEqual(c["evidence"], B.SHORT_EVID)
        self.assertIn("made up words here", [r.get("span") for r in built["rejected"]])

    def test_narrow_guard_keeps_closed_class_start(self):
        p = {"items": [{"rank": 1, "span": "figures in the ring", "core_span": "in the ring", "transparency": "semi", "kind": "figurative_or_metaphorical_use", "reason_en": "x"}]}
        gp, hits = B.guard_narrowing(p)
        self.assertEqual(len(hits), 1)
        self.assertEqual(gp["items"][0]["core_span"], "figures in the ring")
        p2 = {"items": [{"rank": 1, "span": "your wallet pumps its fist", "core_span": "pumps its fist", "transparency": "semi", "kind": "x", "reason_en": "x"}]}
        gp2, hits2 = B.guard_narrowing(p2)
        self.assertEqual(hits2, [])
        self.assertEqual(gp2["items"][0]["core_span"], "pumps its fist")

    def test_append_after_reserved_same_format_and_source_hidden(self):
        built = B.build_b1(self._parsed(), self.units, set(self.ex), self.art)
        out = B.build_pattern_m2b(self.key, built["accepted"])
        rows = out["rows_text"]
        self.assertNotIn("llm_aux", rows)
        self.assertNotIn(B.SHORT_EVID, rows)
        lines = [l for l in rows.splitlines() if l.startswith("- id:")]
        evid = [l for l in lines if "evidence: rule_poss_pattern" in l]
        b1_canon = [c["canonical_form"] for c in out["shortlist"] if c.get("evidence") == B.SHORT_EVID]
        self.assertTrue(b1_canon)
        order = [c["canonical_form"] for c in out["shortlist"]]
        last_base = max(order.index(c["canonical_form"]) for c in self.base["shortlist"] if c["canonical_form"] in order)
        self.assertTrue(all(order.index(b) > last_base for b in b1_canon), "b1は(c)予約枠の直後(末尾)にappend")
        for l in evid:
            self.assertIn("| type: phrase |", l)
        # 追加後のTier H再計算が記録される
        self.assertIn("tier_h_deleted_existing", out)
        self.assertIn("tier_h_recompute_base", out)

    def test_b1_candidate_not_deleted_silently(self):
        built = B.build_b1(self._parsed(), self.units, set(self.ex), self.art)
        out = B.build_pattern_m2b(self.key, built["accepted"])
        acc = {c["canonical_form"] for c in built["accepted"]}
        present = {c["canonical_form"] for c in out["shortlist"]}
        self.assertEqual(acc - present, set(out["tier_h_deleted_b1"]))


class RunSpec(unittest.TestCase):
    def test_stage1_specs_38_jobs_and_breakdown(self):
        s = RUN3.stage1_specs()
        self.assertEqual(len(s), 38)
        from collections import Counter
        c = Counter((a, lv, cn) for a, lv, cn, k in s)
        self.assertEqual(c[("coffee", "adv", "M2BP0")], 5)
        self.assertEqual(c[("coffee", "adv", "M2BP5")], 5)
        self.assertEqual(c[("coffee", "std", "M2BP0")], 5)
        self.assertEqual(c[("coffee", "std", "M2BP5")], 3)
        self.assertEqual(c[("coffee", "std", "M2P0")] + c[("coffee", "adv", "M2P0")], 4)
        self.assertEqual(sum(v for (a, lv, cn), v in c.items() if a == "meta" and cn in ("M2P0", "M2P5")), 8)
        self.assertEqual(sum(v for (a, lv, cn), v in c.items() if cn == "M2BP0" and a in ("meta", "hormuz")), 8)
        self.assertFalse(any(cn == "M2P3" for a, lv, cn, k in s))
        self.assertFalse(any(a == "hormuz" and cn == "M2BP5" for a, lv, cn, k in s))
        self.assertEqual(len(set(s)), len(s))

    def test_stage0_calls_18(self):
        s = RUN3.stage0_specs()
        self.assertEqual(len(s), 18)  # 10 key x run1 + Coffee 2level x run2,3 + 負対照4

    def test_budget_constants(self):
        self.assertEqual((RUN3.BUDGET_R3, RUN3.HARD_STOP_R3), (60.0, 65.0))
        self.assertAlmostEqual(RUN3.TRIAL_PRIOR + RUN3.HARD_STOP_R3, 164.0)
        self.assertEqual(RUN3.RUN.JOB_CAP, 2.5)

    def test_neg_control_files_exist(self):
        for k, (p, lv) in B.NEG_CONTROLS.items():
            self.assertTrue(os.path.exists(p), p)

    def test_combos(self):
        self.assertEqual(RUN3.RUN.COMBOS["M2BP0"], ("M2B", "P0"))
        self.assertEqual(RUN3.RUN.COMBOS["M2BP5"], ("M2B", "P5"))


class AssetsUnchanged(unittest.TestCase):
    def test_round1_shortlists_sha(self):
        a = open(f"{R1}/shortlists_r1.sha256.txt").read().split()[0]
        self.assertEqual(a, hashlib.sha256(open(f"{R1}/shortlists_r1.json", "rb").read()).hexdigest())

    def test_state_guard_if_present(self):
        p = "er064_output/kp_integrated_opt_01/round3/state_guard_r3.json"
        if not os.path.exists(p):
            self.skipTest("state_guard未作成")
        g = json.load(open(p))
        # TEST-HYGIENE-02(2026-10-22): 旧testは「Round3開始時のstate hashが現在も同一」を要求していたが、stateファイル
        # (ledger/telemetry/master store等)はProduction runで正当に更新され続けるため、時間経過で必ず陳腐化する。
        # 本guardの意図(Round3 Trial自身がstateを変更していないこと)は、記録済みguardの内部整合
        # (before == after_stage0 かつ unchanged_after_stage0)で検証する。
        self.assertTrue(g["unchanged_after_stage0"])
        self.assertEqual(g["before"], g["after_stage0"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
