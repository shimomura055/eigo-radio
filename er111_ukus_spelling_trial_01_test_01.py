# -*- coding: utf-8 -*-
"""er111 英米綴りTrial層(DEV/Trial専用)のtest(API 0・費用0)。ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②UKUS 委任_02。
固定する内容:
  (A) 判定の正しさ: c12・代表英米対・異常系(意味/発音が違う対を新規PASSさせない)・固有名詞・AMB一方向・Tier-2非同値・warningsに入れない・既存PASSは完全不変
  (B) 固定対表: ライセンス表記・入力hash・denylist・OF-03(Av=米変異をUK側に入れない)/OF-04(mum/mom)の反映・ビルドの決定性
  (C) 隔離(Opus OF-07): Production module(er006/er020/er078/er104/runner/er109/scope)はTrial moduleをimportしない / Trial・builderはer109へ代入しない・env/flag/argparse読取なし /
      import方向はTrial->er109のみ / Trial importだけではProduction判定は変わらない(scope X内でもc12のdecisionはNone) / 正式経路は未配線
実行: .venv\\Scripts\\python.exe -m unittest er111_ukus_spelling_trial_01_test_01 -v"""
from __future__ import annotations

import ast
import glob
import hashlib
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er109_asr_orthographic_equivalence_01 as e109
import er111_ukus_spelling_trial_01 as T
import er111_ukus_trial_cases_01 as C

C12_C = "Inventing convincing stories at a moment's notice was Vera's speciality."
C12_A = "Inventing convincing stories at a moment's notice was Vera's specialty."


def eq(c, a):
    return T.evaluate_trial(c, a)


class Behavior(unittest.TestCase):
    def test_c12_both_directions(self):
        for c, a in ((C12_C, C12_A), (C12_A, C12_C)):
            self.assertFalse(e109.evaluate(c, a).equivalent)            # 現行(er109 v1)はNG
            r = eq(c, a)
            self.assertTrue(r.equivalent, r.reason)
            self.assertIn(T.RULE_NAME, r.rules)
            self.assertEqual(r.warnings, [])                             # OF-05: warningsに入れない(PASS_WITH_WARNINGにしない)
            self.assertEqual(r.verdict, "PASS")
            self.assertEqual([(p["uk"], p["us"]) for p in r.ukus_pairs], [("speciality", "specialty")])
            self.assertTrue(r.ukus_pairs[0]["pron_differs"])             # OF-06: 発音差ありを記録
            self.assertEqual(r.version, e109.LAYER_VERSION)              # production hookの version検査(eq.version)を通る

    def test_representative_pairs_pass_both_directions(self):
        for uk, us, cl in C.V1_PAIRS:
            for c, a in ((uk, us), (us, uk)):
                r = eq(C.CARRIER.format(w=c), C.CARRIER.format(w=a))
                self.assertTrue(r.equivalent, (uk, us, c, a, r.reason))

    def test_forms_possessive_hyphen_plural(self):
        for c, a in C.V1_FORMS:
            self.assertTrue(eq(c, a).equivalent, (c, a))

    def test_amb_one_direction_only(self):
        r = eq("The tyre is flat.", "The tire is flat.")
        self.assertTrue(r.equivalent)
        self.assertFalse(eq("The tire is flat.", "The tyre is flat.").equivalent)
        self.assertFalse(eq("They license it.", "They licence it.").equivalent and not e109.evaluate("They license it.", "They licence it.").equivalent)

    def test_different_meaning_pairs_not_newly_passed(self):
        new = []
        for x, y in C.V2_PAIRS + C.V2_EXTRA_PAIRS:
            for c, a in ((x, y), (y, x)):
                cc, aa = C.CARRIER.format(w=c), C.CARRIER.format(w=a)
                if eq(cc, aa).equivalent and not e109.evaluate(cc, aa).equivalent:
                    new.append((c, a))
        self.assertEqual(sorted(new), [("tyre", "tire")])      # 意図したAMB一方向(UK形->US形)のみ

    def test_mum_mom_excluded(self):
        self.assertFalse(eq("Mum said hello to us.", "Mom said hello to us.").equivalent)

    def test_extra_cases(self):
        for c, a, exp in C.V2_CASES + C.V3_CASES:
            self.assertEqual(eq(c, a).equivalent, exp, (c, a))

    def test_proper_noun_not_equalized_when_baseline_ng(self):
        self.assertFalse(eq("He visited Aluminium City last year.", "He visited Aluminum City last year.").equivalent)
        self.assertFalse(eq("The Jewellery Quarter is famous.", "The Jewelry Quarter is famous.").equivalent)

    def test_other_diff_in_same_sentence_stays_ng(self):
        self.assertFalse(eq("The speciality is cooking.", "The specialty is cooling.").equivalent)
        self.assertFalse(eq("It was her speciality.", "It was specialty.").equivalent)        # 欠落
        self.assertFalse(eq("It was her speciality.", "It was her very specialty.").equivalent)  # 付加

    def test_tier2_inactive_fail_closed(self):
        d = json.load(open(T.PAIRS_FILE, encoding="utf-8"))
        t2 = [x for x in d["inactive_T2_uk_us_level_dir"] if x[3] == "both"]
        self.assertGreater(len(t2), 1000)
        n = 0
        for uk, us, lv, _ in t2[:3000]:
            if uk.endswith("'s"):
                continue
            if (uk, us) in T.table().p:
                continue
            cc, aa = f"She said the {uk} was fine.", f"She said the {us} was fine."
            if not e109.evaluate(cc, aa).equivalent:
                self.assertFalse(eq(cc, aa).equivalent, (uk, us))
                n += 1
        self.assertGreater(n, 100)

    def test_existing_pass_is_byte_identical(self):
        samples = [("one apple", "1 apple"), ("She said the colour was nice.", "She said the color was nice."), ("The grey cat", "The gray cat"),
                   ("take part in it", "take part in it"), ("It costs three dollars.", "It costs $3.")]
        for c, a in samples:
            b, t = e109.evaluate(c, a), eq(c, a)
            self.assertEqual((b.equivalent, b.reason, b.rules, b.warnings, b.verdict), (t.equivalent, t.reason, t.rules, t.warnings, t.verdict), (c, a))

    def test_monotonic_over_stored_pairs(self):
        """既存er109がPASSの行は、Trialでも同一結果(PASS->NG 0)。pairs_02の全行で確認。"""
        n = bad = 0
        for l in open(os.path.join(ROOT, "docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01", "pairs_02.jsonl"), encoding="utf-8"):
            d = json.loads(l)
            c, a = d["canonical"], d["asr"]
            b = e109.evaluate(c, a)
            if b.equivalent:
                t = eq(c, a)
                n += 1
                if (t.equivalent, t.reason, t.rules, t.warnings) != (b.equivalent, b.reason, b.rules, b.warnings):
                    bad += 1
        self.assertGreater(n, 50)
        self.assertEqual(bad, 0)


class Table(unittest.TestCase):
    def setUp(self):
        self.d = json.load(open(T.PAIRS_FILE, encoding="utf-8"))
        self.P = {(p["uk"], p["us"]): p for p in self.d["pairs"]}

    def test_license_and_input_hashes(self):
        m = self.d["meta"]
        self.assertIn("Kevin Atkinson", m["license"])
        self.assertIn("Permission to use, copy, modify, distribute and sell", m["license"])
        for k in ("varcon", "scowl_subsets"):
            f = os.path.join(ROOT, m["inputs"][k]["file"])
            self.assertEqual(hashlib.sha256(open(f, "rb").read()).hexdigest(), m["inputs"][k]["sha256"])
        self.assertIn("not adopted", m["policy"]["breame"])
        self.assertFalse(m["policy"]["T2_active"])

    def test_active_only_t1_or_rule_and_t2_inactive(self):
        self.assertTrue(all(p["tier"] in ("T1", "R") and p["active"] for p in self.d["pairs"]))
        self.assertGreater(len(self.d["inactive_T2_uk_us_level_dir"]), 1000)

    def test_of03_av_variant_not_uk_side(self):
        uk_words = {p["uk"] for p in self.d["pairs"]}
        for w in ("nite", "thruway", "analog", "color", "organize", "center"):      # US形・米変異綴りがUK側に居ない(analogは別項でUK側にAMB復活しないこと)
            self.assertNotIn(w, uk_words, w)

    def test_of04_excluded_mum_mom_and_analyses(self):
        self.assertNotIn(("mum", "mom"), self.P)
        self.assertNotIn(("analyses", "analyzes"), self.P)
        ex = {(x["uk"], x["us"]) for x in self.d["excluded"]}
        self.assertIn(("mum", "mom"), ex)

    def test_amb_directions(self):
        for k in (("tyre", "tire"), ("licence", "license"), ("practise", "practice"), ("programme", "program"), ("dependant", "dependent")):
            self.assertEqual(self.P[k]["dir"], "uk2us", k)
        self.assertEqual(self.P[("speciality", "specialty")]["dir"], "both")

    def test_denylist_applied(self):
        for k in (("arse", "ass"), ("saki", "sake"), ("onwards", "onward"), ("matt", "mat"), ("forego", "forgo"), ("premiss", "premise")):
            self.assertNotIn(k, self.P, k)

    def test_build_is_deterministic(self):
        import er111_ukus_pairs_build_01 as B
        res = B.build()
        self.assertEqual(json.dumps(res["pairs"], sort_keys=True), json.dumps(self.d["pairs"], sort_keys=True))
        self.assertEqual(res["meta"]["counts"], self.d["meta"]["counts"])

    def test_no_transitive_pairs(self):
        self.assertIsNone(T.table().direct("colour", "colour"))
        # 直接対のみ(推移しない): UK形->別のUK形、US形->別のUS形は不可
        self.assertIsNone(T.table().word_pair("centre", "theatre"))


def _py_files():
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.py"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout.split("\n")
    files = [f.strip() for f in out if f.strip().endswith(".py")]
    if not files:
        files = [os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "*.py"))]
    return [f.replace("\\", "/") for f in files if os.path.exists(os.path.join(ROOT, f)) and ".venv" not in f.split("/") and "mfa_tool" not in f.split("/")]


def _imports(tree):
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module)
    return mods


TRIAL_FILES = ("er111_ukus_spelling_trial_01.py", "er111_ukus_pairs_build_01.py")
ER111_OK_IMPORTERS = {"er111_ukus_spelling_trial_01.py", "er111_ukus_pairs_build_01.py", "er111_ukus_trial_cases_01.py", "er111_ukus_trial_eval_01.py",
                      "er111_ukus_spelling_trial_01_test_01.py"}


class Isolation(unittest.TestCase):
    def test_no_production_module_imports_trial_modules(self):
        offenders = []
        for rel in _py_files():
            b = os.path.basename(rel)
            if b in ER111_OK_IMPORTERS:
                continue
            try:
                tree = ast.parse(open(os.path.join(ROOT, rel), encoding="utf-8").read())
            except (SyntaxError, UnicodeDecodeError):
                continue
            if any(m.startswith("er111_ukus") for m in _imports(tree)):
                offenders.append(rel)
        self.assertEqual(offenders, [], "Trial moduleを参照するProduction/他moduleがある(隔離違反)")

    def test_production_modules_do_not_mention_trial_names(self):
        for b in ("er006_secondary_asr_01.py", "er020_tts_retry_local_rewrite_01.py", "er078_asr_unified_judge_01.py", "er104_kp_three_asr_vote_01.py",
                  "er019_family_x_audio_production_runner_01.py", "er063_family_z_audio_01.py", "er109_asr_orthographic_equivalence_01.py", "er109_xz_scope_01.py",
                  "er006_preprod_hardening_01_validation.py"):
            src = open(os.path.join(ROOT, b), encoding="utf-8").read()
            self.assertNotIn("er111_ukus", src, b)
            self.assertNotIn("ukus_spelling_variant", src, b)

    def test_trial_and_builder_have_no_assignment_to_er109_or_scope(self):
        for b in TRIAL_FILES:
            tree = ast.parse(open(os.path.join(ROOT, b), encoding="utf-8").read())
            for n in ast.walk(tree):
                targets = []
                if isinstance(n, ast.Assign):
                    targets = n.targets
                elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
                    targets = [n.target]
                for t in targets:
                    if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id in ("e109", "xz", "val", "_hp", "ortho_scope"):
                        self.fail(f"{b}:{n.lineno} が {t.value.id}.{t.attr} へ代入している")

    def test_trial_has_no_env_flag_or_cli_reads(self):
        for b in ("er111_ukus_spelling_trial_01.py",):
            src = open(os.path.join(ROOT, b), encoding="utf-8").read()
            tree = ast.parse(src)
            self.assertNotIn("os.environ", src)
            self.assertNotIn("getenv", src)
            self.assertNotIn("argparse", src)
            mods = _imports(tree)
            allowed = {"__future__", "difflib", "functools", "json", "os", "re", "unicodedata", "er109_asr_orthographic_equivalence_01", "er006_preprod_hardening_01_validation"}
            self.assertTrue(mods <= allowed, mods - allowed)                  # import方向は Trial -> er109(とvalidationの読取)のみ

    def test_no_new_flag_in_production(self):
        # 11-7のflagを作らない: Production moduleに ukus 系flag名が無い
        for b in ("er109_asr_orthographic_equivalence_01.py", "er109_xz_scope_01.py"):
            src = open(os.path.join(ROOT, b), encoding="utf-8").read().lower()
            self.assertNotIn("ukus", src)

    def test_importing_trial_does_not_change_production_decision(self):
        """DefaultOffIsolation型: Trial module(import済み)でも、scope X内の正式hook decision() は現行どおり(c12はNG=None、API 0)。"""
        import er109_xz_scope_01 as xz
        before = xz._evaluate_cached
        with xz.run_scope("X"):
            self.assertIsNone(xz.decision(C12_C, C12_A))
        self.assertIs(xz._evaluate_cached, before)                    # Trial importはhookを差し替えていない
        self.assertIs(e109.evaluate, T._BASE_EVALUATE)               # er109.evaluateも無変更

    def test_scope_outside_trial_hook_inactive(self):
        import er109_xz_scope_01 as xz
        self.assertIsNone(xz.current_scope())
        self.assertIsNone(xz.decision(C12_C, C12_A))                  # scope外


if __name__ == "__main__":
    unittest.main()
