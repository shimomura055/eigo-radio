# -*- coding: utf-8 -*-
"""er109 ②英米綴り層(UKUS、Production)のtest(API 0・費用0)。ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②UKUS 委任_04(WIRING_DESIGN_01 §6、OPUS_REVIEW_02 W-01〜W-12)。
構成: Behavior(Trial 27件相当の移植+固定expected) / Table(ライセンス・sha・失敗状態cache・OF-03/04) / Structure(P-06・W-12・AST隔離・W-10) /
      Hooks(T-E1〜E5: Primary/Secondary/KP/継承/Store guard、W-03の3ケース) / DefaultOnScope(T-I) / StoredRegression(保存データの固定expected)。
実行: .venv\\Scripts\\python.exe -m unittest er109_ukus_spelling_01_test_01 -v"""
from __future__ import annotations

import ast
import gzip
import hashlib
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg
import er078_reuse_value_guard_01 as rvg
import er019_family_x_validation_inheritance_01 as vi
import er104_kp_three_asr_vote_01 as kp3v
import er109_asr_orthographic_equivalence_01 as e109
import er109_ukus_spelling_01 as uk
import er109_ukus_spelling_01_test_cases_01 as C
import er109_xz_scope_01 as xz
import er109_xz_scope_01_test_01 as T

C12_C = "Inventing convincing stories at a moment's notice was Vera's speciality."
C12_A = "Inventing convincing stories at a moment's notice was Vera's specialty."
C12_FORTE = "Inventing convincing stories at a moment's notice was Vera's forte."


def ev(c, a):
    return e109.evaluate(c, a, ukus=True)


class Behavior(unittest.TestCase):
    def test_c12_both_directions(self):
        for c, a in ((C12_C, C12_A), (C12_A, C12_C)):
            self.assertFalse(e109.evaluate(c, a).equivalent)                    # ukus=False(既定)は現行(v1)どおりNG
            self.assertFalse(e109.evaluate(c, a, ukus=False).equivalent)
            r = ev(c, a)
            self.assertTrue(r.equivalent, r.reason)
            self.assertIn(uk.RULE_NAME, r.rules)
            self.assertEqual(r.warnings, [])                                     # OF-05: warningsに入れない(PASS_WITH_WARNINGにしない)
            self.assertEqual(r.verdict, "PASS")
            self.assertEqual(r.reason, uk.REASON_WITH_UKUS)                      # W-01(3)
            self.assertEqual([(p["uk"], p["us"]) for p in r.ukus_pairs], [("speciality", "specialty")])
            self.assertTrue(r.ukus_pairs[0]["pron_differs"])                     # OF-06
            self.assertEqual(r.version, e109.LAYER_VERSION)
            a_ = r.audit()
            self.assertEqual((a_["ukus_pairs_n"], a_["pron_differs_n"], a_["ukus_active"]), (1, 1, True))
            self.assertEqual(a_["ukus_table_sha256"], uk.PAIRS_CANONICAL_SHA256)

    def test_layer_version_is_v2_ukus(self):
        self.assertTrue(e109.LAYER_VERSION.endswith("_v2_ukus01"))

    def test_representative_pairs_pass_both_directions(self):
        for u, s, cl in C.V1_PAIRS:
            for c, a in ((u, s), (s, u)):
                r = ev(C.CARRIER.format(w=c), C.CARRIER.format(w=a))
                self.assertTrue(r.equivalent, (u, s, c, a, r.reason))

    def test_forms_possessive_hyphen_plural(self):
        for c, a in C.V1_FORMS:
            self.assertTrue(ev(c, a).equivalent, (c, a))

    def test_amb_one_direction_only(self):
        self.assertTrue(ev("The tyre is flat.", "The tire is flat.").equivalent)
        self.assertFalse(ev("The tire is flat.", "The tyre is flat.").equivalent)

    def test_different_meaning_pairs_not_newly_passed(self):
        new = []
        for x, y in C.V2_PAIRS + C.V2_EXTRA_PAIRS:
            for c, a in ((x, y), (y, x)):
                cc, aa = C.CARRIER.format(w=c), C.CARRIER.format(w=a)
                if ev(cc, aa).equivalent and not e109.evaluate(cc, aa).equivalent:
                    new.append((c, a))
        self.assertEqual(sorted(new), [("tyre", "tire")])

    def test_extra_cases(self):
        for c, a, exp in C.V2_CASES + C.V3_CASES:
            self.assertEqual(ev(c, a).equivalent, exp, (c, a))

    def test_proper_noun_not_equalized_when_baseline_ng(self):
        for c, a in (("He visited Aluminium City last year.", "He visited Aluminum City last year."),
                     ("The Jewellery Quarter is famous.", "The Jewelry Quarter is famous."),
                     ("Speciality Coffee Roasters opened here.", "Specialty Coffee Roasters opened here."),
                     ("The Tyre Company opened.", "The Tire Company opened."),
                     ("ALUMINIUM prices rose.", "ALUMINUM prices rose.")):
            r = ev(c, a)
            self.assertFalse(r.equivalent, (c, a))
            self.assertEqual(r.ukus_pairs, [])

    def test_other_diff_in_same_sentence_stays_ng(self):
        self.assertFalse(ev("The speciality is cooking.", "The specialty is cooling.").equivalent)
        self.assertFalse(ev("It was her speciality.", "It was specialty.").equivalent)
        self.assertFalse(ev("It was her speciality.", "It was her very specialty.").equivalent)

    def test_ng_record_identical_to_ukus_false_when_not_rescued(self):
        """救済不成立のNG記録は ukus=False と完全同一(spans含む)。"""
        for c, a in (("He visited Aluminium City last year.", "He visited Aluminum City last year."), ("It was her speciality.", "It was specialty.")):
            x, y = e109.evaluate(c, a), ev(c, a)
            self.assertEqual((x.equivalent, x.reason, x.rules, x.warnings, x.audit()["spans"]), (y.equivalent, y.reason, y.rules, y.warnings, y.audit()["spans"]))
        # 別spanが不合格の文: 判定理由は同一(NG記録には先に救済された位置のspanが残る=監査のみ。NGなのでdecision()は常にNone)
        x, y = e109.evaluate("The speciality is cooking.", "The specialty is cooling."), ev("The speciality is cooking.", "The specialty is cooling.")
        self.assertEqual((x.equivalent, x.reason), (y.equivalent, y.reason))

    def test_tier2_inactive_fail_closed(self):
        d = json.load(open(uk.PAIRS_FILE, encoding="utf-8"))
        t2 = [x for x in d["inactive_T2_uk_us_level_dir"] if x[3] == "both"]
        self.assertGreater(len(t2), 1000)
        n = 0
        for u, s, lv, _ in t2[:3000]:
            if u.endswith("'s") or (u, s) in uk.table().p:
                continue
            cc, aa = f"She said the {u} was fine.", f"She said the {s} was fine."
            if not e109.evaluate(cc, aa).equivalent:
                self.assertFalse(ev(cc, aa).equivalent, (u, s))
                n += 1
        self.assertGreater(n, 100)

    def test_existing_pass_is_byte_identical(self):
        samples = [("one apple", "1 apple"), ("She said the colour was nice.", "She said the color was nice."), ("The grey cat", "The gray cat"),
                   ("take part in it", "take part in it"), ("It costs three dollars.", "It costs $3.")]
        for c, a in samples:
            b, t = e109.evaluate(c, a), ev(c, a)
            self.assertEqual((b.equivalent, b.reason, b.rules, b.warnings, b.verdict, b.audit()["spans"]), (t.equivalent, t.reason, t.rules, t.warnings, t.verdict, t.audit()["spans"]), (c, a))

    def test_monotonic_over_pairs_02(self):
        n = bad = 0
        for l in open(os.path.join(ROOT, "docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01", "pairs_02.jsonl"), encoding="utf-8"):
            d = json.loads(l)
            c, a = d["canonical"], d["asr"]
            b = e109.evaluate(c, a)
            if b.equivalent:
                t = ev(c, a)
                n += 1
                if (t.equivalent, t.reason, t.rules, t.warnings) != (b.equivalent, b.reason, b.rules, b.warnings):
                    bad += 1
        self.assertGreater(n, 50)
        self.assertEqual(bad, 0)

    # ---- W-01(4): positional条件(同数・全unitがword)。span粒度の構造差 ----
    def test_rescue_adjacent_v1_span_positional(self):
        """既存rule(their/there)と綴り差が隣接し単一n:n spanになる文: 位置別に分解して救済(同数・全word)。"""
        r = ev("Their speciality was fine at the time.", "There specialty was fine at the time.")
        self.assertTrue(r.equivalent, r.reason)
        self.assertEqual([(p["uk"], p["us"]) for p in r.ukus_pairs], [("speciality", "specialty")])
        self.assertIn(uk.RULE_NAME, r.rules)

    def test_non_positional_span_not_rescued(self):
        """語数が違うn:mのspan(contraction展開が隣接)は救済しない=従来どおりNG。"""
        r = ev("The speciality I'm sure about is here.", "The specialty I am sure about is here.")
        r0 = e109.evaluate("The speciality I'm sure about is here.", "The specialty I am sure about is here.")
        self.assertEqual((r.equivalent, r.reason), (r0.equivalent, r0.reason))

    def test_rescue_requires_at_least_one_pair_hit(self):
        """既存基準で全位置が合格するだけの(UKUS無関係な)NG->PASSは起こさない: ukus=Trueで新規PASSなら必ずukus_pairsを伴う。"""
        for c, a in (("Take part in it.", "Take apart in it."), ("I did not go.", "I did go."), ("We have two cats.", "We have one cats.")):
            r = ev(c, a)
            self.assertEqual(r.equivalent, e109.evaluate(c, a).equivalent, (c, a))
            if r.equivalent:
                self.assertEqual(r.ukus_pairs, [])

    def test_cmu_unregistered_position_only_with_exact_pair(self):
        # jewellery は CMU未登録位置: 対表の完全一致(jewellery/jewelry)のときだけ救済し、音素は注入しない
        self.assertTrue(ev("Her jewellery was lost.", "Her jewelry was lost.").equivalent)
        self.assertFalse(ev("Her jewellery was lost.", "Her jewelery was lost.").equivalent)      # 表に無い綴り
        self.assertFalse(ev("Her jewellery was lost.", "Her jewel was lost.").equivalent)


class StoredRegression(unittest.TestCase):
    """保存済みrowsに対する固定expected(Trial撤去後の回帰化、W-01)。expected = WIRING/stored_regression_expected_01.jsonl.gz"""
    EXP = os.path.join(ROOT, "er109_output", "ukus_wiring_01", "stored_regression_expected_01.jsonl.gz")

    def test_fixed_expected_equals_current(self):
        self.assertTrue(os.path.exists(self.EXP), self.EXP)
        n = bad = 0
        for l in gzip.open(self.EXP, "rt", encoding="utf-8"):
            d = json.loads(l)
            r = ev(d["c"], d["a"])
            got = {"equivalent": r.equivalent, "reason": r.reason if r.equivalent else None, "rules": sorted(r.rules) if r.equivalent else None,
                   "warnings": sorted(r.warnings) if r.equivalent else None, "ukus_pairs": [[p["uk"], p["us"]] for p in r.ukus_pairs]}
            n += 1
            if got != d["expected"]:
                bad += 1
        self.assertGreater(n, 500)
        self.assertEqual(bad, 0)

    def test_sweep_result_saved_no_diff(self):
        base = os.path.join(ROOT, "docs", "research", "ASR-QUALITY-2ITEMS-COMPREHENSIVE-01", "UKUS", "WIRING")
        for nm, key in (("DIFF_TEST_RESULT_pairs_01.json", "pairs_sweep"), ("DIFF_TEST_RESULT_stored_01.json", "stored_rows")):
            p = os.path.join(base, nm)
            self.assertTrue(os.path.exists(p), p)
            st = json.load(open(p, encoding="utf-8"))[key]["stats"]
            self.assertEqual(st.get("PASS_to_NG", 0), 0)
            self.assertEqual(st.get("NG_to_PASS_without_ukus", 0), 0)
            self.assertEqual(st.get("off_vs_head_DIFF", 0), 0)
            self.assertEqual(st.get("off_pass_output_changed", 0), 0)


class Table(unittest.TestCase):
    def setUp(self):
        self.d = json.load(open(uk.PAIRS_FILE, encoding="utf-8"))
        self.P = {(p["uk"], p["us"]): p for p in self.d["pairs"]}

    def test_sha_matches_constant(self):
        self.assertEqual(uk.pairs_canonical_sha256(self.d["pairs"]), uk.PAIRS_CANONICAL_SHA256)
        self.assertEqual(uk.table().sha256, uk.PAIRS_CANONICAL_SHA256)
        self.assertEqual(uk.table().size, 6361)

    def test_sha_mismatch_raises_and_failure_state_is_cached(self):
        with self.assertRaises(RuntimeError):
            uk.PairTable(expected_sha="0" * 64)
        calls = {"n": 0}

        class Bad:
            def __init__(self, *a, **k):
                calls["n"] += 1
                raise RuntimeError("ukus_pairs_sha256_mismatch(test)")
        saved = dict(uk._TABLE_STATE)
        try:
            uk.reset_table_cache_for_test()
            with mock.patch.object(uk, "PairTable", Bad):
                for _ in range(3):
                    with self.assertRaises(RuntimeError):
                        uk.table()
            self.assertEqual(calls["n"], 1)                       # W-07: 失敗状態をcache=毎回再ロードしない
        finally:
            uk._TABLE_STATE.clear()
            uk._TABLE_STATE.update(saved)

    def test_table_failure_is_fail_closed_to_v1(self):
        with mock.patch.object(uk, "table", side_effect=RuntimeError("table boom")):
            r = ev(C12_C, C12_A)
        self.assertFalse(r.equivalent)
        self.assertIn("table boom", r.ukus_error)
        self.assertIn("ukus_error", r.audit())
        # decision(): scope内でもNG->None、sinkへ記録
        sink = {}
        with xz.run_scope("X"):
            with mock.patch.object(uk, "table", side_effect=RuntimeError("table boom")):
                xz._evaluate_cached.cache_clear()
                self.assertIsNone(xz.decision(C12_C, C12_A, sink=sink))
                xz._evaluate_cached.cache_clear()
        self.assertTrue(any("table boom" in x for x in sink.get("orthographic_equivalence_errors", [])))

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
        for w in ("nite", "thruway", "analog", "color", "organize", "center"):
            self.assertNotIn(w, uk_words, w)

    def test_of04_excluded_mum_mom_and_analyses(self):
        self.assertNotIn(("mum", "mom"), self.P)
        self.assertNotIn(("analyses", "analyzes"), self.P)
        self.assertIn(("mum", "mom"), {(x["uk"], x["us"]) for x in self.d["excluded"]})

    def test_amb_directions(self):
        for k in (("tyre", "tire"), ("licence", "license"), ("practise", "practice"), ("programme", "program"), ("dependant", "dependent")):
            self.assertEqual(self.P[k]["dir"], "uk2us", k)
        self.assertEqual(self.P[("speciality", "specialty")]["dir"], "both")

    def test_denylist_applied(self):
        for k in (("arse", "ass"), ("saki", "sake"), ("onwards", "onward"), ("matt", "mat"), ("forego", "forgo"), ("premiss", "premise")):
            self.assertNotIn(k, self.P, k)

    def test_build_is_deterministic(self):
        import er109_ukus_pairs_build_01 as B
        res = B.build()
        self.assertEqual(json.dumps(res["pairs"], sort_keys=True), json.dumps(self.d["pairs"], sort_keys=True))
        self.assertEqual(res["meta"]["counts"], self.d["meta"]["counts"])

    def test_no_transitive_pairs(self):
        self.assertIsNone(uk.table().direct("colour", "colour"))
        self.assertIsNone(uk.table().word_pair("centre", "theatre"))


class Structure(unittest.TestCase):
    def test_p06_table_words_have_no_digits_negation_or_value_atoms(self):
        """T-D / W-12: 表のactive語は数字・否定語・値atomを持たない=UKUS spanは値DIFF/否定差を説明(解除)できない。"""
        words = set()
        for p in uk.table().p.values():
            words.add(p["uk"])
            words.add(p["us"])
        self.assertGreater(len(words), 10000)
        for w in words:
            self.assertFalse(any(ch.isdigit() for ch in w), w)
            self.assertFalse(uj.negation_counter(w), w)
            self.assertEqual(vg.extract_atoms_en(w), [], w)
        self.assertIn(("nought", "naught"), uk.table().p)              # W-12: activeだが上の検査を通る

    def test_p06_ukus_span_cannot_explain_value_or_negation_diff(self):
        c, a = "She bought 3 colourful flavours.", "She bought 4 colorful flavors."
        r = ev(c, a)
        self.assertFalse(e109.evaluate(c, a).equivalent)
        self.assertFalse(r.equivalent)                                # 実数値差(3->4)は従来どおりNG
        c2, a2 = "He did not like the colour.", "He did like the color."
        self.assertFalse(ev(c2, a2).equivalent)
        # 説明関数にUKUS span(数字/否定を含まない)だけを渡しても値DIFF/否定差は解除されない
        ok = ev("The speciality costs 3 pounds.", "The specialty costs 3 pounds.")
        self.assertTrue(ok.equivalent)
        dec = xz.OrthoDecision("The speciality costs 3 pounds.", "The specialty costs 3 pounds.", ok)
        vgr, neg = uj._protected("The speciality costs 3 pounds.", "The specialty costs 4 pounds.", "en")
        ex = xz.explain_protected(dec, vgr, neg, "The speciality costs 3 pounds.", "The specialty costs 4 pounds.")
        self.assertFalse(ex.explained)

    def test_proper_nouns_and_numbers_negation_cohabit_stay_ng(self):
        self.assertFalse(ev("The speciality costs 3 pounds.", "The specialty costs 4 pounds.").equivalent)
        self.assertFalse(ev("He did not see the colour.", "He did see the color.").equivalent)

    def test_no_dev_or_old_design_in_production_modules(self):
        for b in ("er109_ukus_spelling_01.py", "er109_asr_orthographic_equivalence_01.py", "er109_xz_scope_01.py"):
            src = open(os.path.join(ROOT, b), encoding="utf-8").read()
            tree = ast.parse(src)
            mods = {n.module if isinstance(n, ast.ImportFrom) else a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
                    for a in (n.names if isinstance(n, ast.Import) else [None])}
            self.assertFalse({m for m in mods if m and (m.startswith("er111") or m in ("wordfreq", "breame"))}, b)
            self.assertNotIn("import wordfreq", src)
            self.assertNotIn("import breame", src)
            self.assertNotIn("er111_ukus", src)

    def test_ukus_module_has_no_env_cli_network(self):
        src = open(os.path.join(ROOT, "er109_ukus_spelling_01.py"), encoding="utf-8").read()
        for w in ("os.environ", "getenv", "argparse", "sys.argv", "requests", "urllib", "socket", "subprocess"):
            self.assertNotIn(w, src, w)

    def test_evaluate_ukus_kwarg_only_passed_by_evaluate_cached(self):
        """W-10: Production(非test・非研究script)で evaluate(ukus=...) を渡してよいのは er109_xz_scope_01._evaluate_cached のみ。"""
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.py"], cwd=ROOT, capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout.split("\n")
        files = [f.strip().replace("\\", "/") for f in out if f.strip().endswith(".py")]
        offenders = []
        for rel in files:
            b = os.path.basename(rel)
            if "_test" in b or b.startswith("test_") or b == "conftest.py" or ".venv" in rel.split("/") or rel.startswith(("docs/", "mfa_tool/")):
                continue
            try:
                tree = ast.parse(open(os.path.join(ROOT, rel), encoding="utf-8").read())
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            for fn in ast.walk(tree):
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for n in ast.walk(fn):
                        if isinstance(n, ast.Call) and any(k.arg == "ukus" for k in n.keywords):
                            if not (b == "er109_xz_scope_01.py" and fn.name == "_evaluate_cached"):
                                offenders.append((rel, fn.name, n.lineno))
            for n in tree.body:       # module level
                if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and any(k.arg == "ukus" for k in n.value.keywords):
                    offenders.append((rel, "<module>", n.lineno))
        self.assertEqual(offenders, [])

    def test_ukus_flag_assigned_only_in_definition(self):
        for rel in ("er109_xz_scope_01.py", "er109_ukus_spelling_01.py", "er078_reuse_value_guard_01.py", "er078_asr_unified_judge_01.py",
                    "er006_secondary_asr_01.py", "er104_kp_three_asr_vote_01.py", "er019_family_x_validation_inheritance_01.py"):
            tree = ast.parse(open(os.path.join(ROOT, rel), encoding="utf-8").read())
            for n in ast.walk(tree):
                if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                    for t in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                        nm = t.id if isinstance(t, ast.Name) else getattr(t, "attr", "")
                        self.assertNotEqual(nm, "UKUS_SPELLING_EQUIVALENCE_ENABLED", f"{rel}:{n.lineno}")
        src = open(os.path.join(ROOT, "er109_asr_orthographic_equivalence_01.py"), encoding="utf-8").read()
        self.assertEqual(src.count("UKUS_SPELLING_EQUIVALENCE_ENABLED = True"), 1)
        self.assertNotIn("UKUS_SPELLING_EQUIVALENCE_ENABLED = False", src)

    def test_flag_defaults_and_single_reader(self):
        self.assertIs(e109.UKUS_SPELLING_EQUIVALENCE_ENABLED, True)
        self.assertTrue(e109.ukus_is_enabled())
        with mock.patch.object(e109, "ORTHOGRAPHIC_EQUIVALENCE_ENABLED", False):
            self.assertFalse(e109.ukus_is_enabled())              # 親flag従属
        with mock.patch.object(e109, "UKUS_SPELLING_EQUIVALENCE_ENABLED", False):
            self.assertFalse(e109.ukus_is_enabled())

    def test_evaluate_default_is_ukus_false(self):
        import inspect
        self.assertIs(inspect.signature(e109.evaluate).parameters["ukus"].default, False)
        self.assertFalse(e109.evaluate(C12_C, C12_A).equivalent)

    def test_cache_key_includes_flag(self):
        xz._evaluate_cached.cache_clear()
        a = xz._evaluate_cached(C12_C, C12_A, True)
        b = xz._evaluate_cached(C12_C, C12_A, False)
        self.assertTrue(a.equivalent)
        self.assertFalse(b.equivalent)
        self.assertIsNot(a, b)

    def test_run_evidence_summary(self):
        with xz.run_scope("Z"):
            s = xz.ukus_run_evidence()
        self.assertEqual((s["scope"], s["ukus_active"], s["layer_version"]), ("Z", True, e109.LAYER_VERSION))
        self.assertEqual(s["ukus_table_sha256"], uk.PAIRS_CANONICAL_SHA256)
        self.assertFalse(xz.ukus_run_evidence()["ukus_active"])


class Hooks(T.Base):
    """T-E1〜E5: 正式hook経由でc12が OFF=NG -> ON=PASS(rules=ukus、warnings空、retry/LR/HR 0=API 0のmock)。"""

    def _ukus_off(self):
        return mock.patch.object(e109, "UKUS_SPELLING_EQUIVALENCE_ENABLED", False)

    def test_e1_primary_adapter(self):
        d = self.adapter(C12_C, C12_A)
        self.assertTrue(d["verified"], d["asr_judgement"].get("reason_code"))
        aj = d["asr_judgement"]
        self.assertEqual((aj["state"], aj["warnings"]), ("PASS", []))
        site = aj["orthographic_equivalence"]["sites"][0]["er109"]
        self.assertIn("ukus_spelling_variant", site["rules"])
        self.assertEqual(site["ukus_pairs"][0]["us"], "specialty")
        self.assertTrue(site["ukus_pairs"][0]["pron_differs"])
        self.assertEqual(aj["orthographic_equivalence"]["version"], e109.LAYER_VERSION)
        with self._ukus_off():
            off = self.adapter(C12_C, C12_A)
        self.assertFalse(off["verified"])
        none = self.adapter(C12_C, C12_A, scope=None)
        self.assertFalse(none["verified"])
        self.assertNotIn("orthographic_equivalence", none["asr_judgement"])

    def test_e2_secondary_path(self):
        d = self.adapter(C12_C, C12_FORTE, azure=C12_A)      # Primaryは別語(NG)、Secondary(Azure)が綴り差のみ
        self.assertTrue(d["verified"])
        sites = d["asr_judgement"]["orthographic_equivalence"]["sites"]
        self.assertEqual([(x["site"], "ukus_spelling_variant" in x["er109"]["rules"]) for x in sites], [("secondary", True)])
        with self._ukus_off():
            off = self.adapter(C12_C, C12_FORTE, azure=C12_A)
        self.assertFalse(off["verified"])

    def test_e3_kp_vote(self):
        c, a = "Her speciality", "Her specialty"
        with xz.run_scope("X"):
            v = kp3v.make_voter("whisper", c, a, lang="en")
        self.assertTrue(v.passed)
        self.assertEqual(v.label, xz.ORTHO_LABEL)
        with xz.run_scope("X"), self._ukus_off():
            v2 = kp3v.make_voter("whisper", c, a, lang="en")
        self.assertFalse(v2.passed)
        self.assertIsNone(xz.current_scope())

    def test_e4_inheritance_rejudge(self):
        rec = {"text": C12_C, "asr_text": C12_A, "sha256": "x"}
        with xz.run_scope("X"):
            ok = vi.rejudge_with_current_judge(dict(rec), "b1b", "full_story_part1", force_lang="en")
        self.assertTrue(ok.get("ok"), ok.get("reason"))
        with xz.run_scope("X"), self._ukus_off():
            off = vi.rejudge_with_current_judge(dict(rec), "b1b", "full_story_part1", force_lang="en")
        self.assertFalse(off.get("ok"))

    # ---- E5: Store guard(W-03、UKUS flagだけOFFのrollback時の唯一の防壁) ----
    def _aj(self):
        d = self.adapter(C12_C, C12_A)
        self.assertTrue(d["verified"])
        return d["asr_judgement"]

    def test_e5_store_guard_ukus_flag_off_blocks(self):
        aj = self._aj()
        for key in ("asr_judgement", "asr_judgement_inherited"):                  # W-03(1): inheritedのみ
            e = {"text": C12_C, "asr_text": C12_A, key: aj}
            with xz.run_scope("X"):
                g = rvg.guard_entry(dict(e), label="t", canonical_text=C12_C)
            self.assertFalse(g["blocked"], (key, g))                               # UKUS有効: 再利用可
            with xz.run_scope("X"), self._ukus_off():
                g = rvg.guard_entry(dict(e), label="t", canonical_text=C12_C)
            self.assertTrue(g["blocked"], key)
            self.assertEqual(g["reason"], xz.UKUS_OUT_OF_SCOPE_BLOCK_REASON)
            for follows in (True,):                                                # early-returnより前
                with xz.run_scope("X"), self._ukus_off():
                    g = rvg.guard_entry(dict(e), label="t", canonical_text=C12_C, kp_vote_gate_follows=follows)
                self.assertTrue(g["blocked"])
            g = rvg.guard_entry(dict(e), label="t", canonical_text=C12_C)          # scope外: 既存ortho防壁
            self.assertEqual(g["reason"], xz.OUT_OF_SCOPE_BLOCK_REASON)

    def test_e5_kp_vote_site_detected(self):
        aj = {"state": "PASS", "warnings": [], "orthographic_equivalence": {"applied": True, "version": e109.LAYER_VERSION, "sites": [
            {"site": "primary", "er109": {"rules": []}}, {"site": "kp_whisper", "er109": {"rules": ["ukus_spelling_variant"], "ukus_pairs": [{"uk": "a"}]}}]}}
        self.assertTrue(xz.ukus_contributed(aj))
        aj["orthographic_equivalence"]["sites"][1]["er109"] = {"rules": ["homophone"]}
        self.assertFalse(xz.ukus_contributed(aj))                                  # 旧v1相当(UKUS無関係)は寄与なし
        # ukus_pairs だけ(rulesに印が無い)でも寄与とみなす(判定キー統一)
        aj["orthographic_equivalence"]["sites"][1]["er109"] = {"rules": [], "ukus_pairs": [{"uk": "a"}]}
        self.assertTrue(xz.ukus_contributed(aj))

    def test_e5_audit_missing_is_fail_closed(self):
        base = {"orthographic_equivalence": {"applied": True, "version": "er109_orthographic_equivalence_v2_ukus01", "sites": []}}
        self.assertTrue(xz.ukus_contributed(base))                                  # ukus version・site auditなし -> UKUS寄与あり
        base["orthographic_equivalence"]["sites"] = [{"site": "primary"}]
        self.assertTrue(xz.ukus_contributed(base))
        v1 = {"orthographic_equivalence": {"applied": True, "version": "er109_orthographic_equivalence_v1_proto_aho02", "sites": []}}
        self.assertFalse(xz.ukus_contributed(v1))                                   # 旧v1 entryの再利用可否は変えない
        self.assertFalse(xz.ukus_contributed({"state": "PASS"}))
        self.assertFalse(xz.ukus_contributed(None))
        e = {"text": "x", "asr_text": "x", "asr_judgement_inherited": base}
        with xz.run_scope("X"), mock.patch.object(e109, "UKUS_SPELLING_EQUIVALENCE_ENABLED", False):
            self.assertEqual(rvg.guard_entry(e, label="t", canonical_text="x")["reason"], xz.UKUS_OUT_OF_SCOPE_BLOCK_REASON)

    def test_e5_non_ukus_ortho_entries_unaffected_by_ukus_flag(self):
        d = self.adapter("Pump one's fist.", "Pump 1's fist.")
        aj = d["asr_judgement"]
        self.assertFalse(xz.ukus_contributed(aj))
        with xz.run_scope("X"), self._ukus_off():
            g = rvg.guard_entry({"text": "Pump one's fist.", "asr_text": "Pump 1's fist.", "asr_judgement": aj}, label="t", canonical_text="Pump one's fist.")
        self.assertNotEqual(g.get("reason"), xz.UKUS_OUT_OF_SCOPE_BLOCK_REASON)


class DefaultOnScope(T.Base):
    """T-I: scope無し/親flag OFF/UKUS flag OFF -> UKUSは不活性(従来署名)、ON -> UKUS。version文字列を除き従来と同一。"""

    def _sig(self, d):
        aj = d["asr_judgement"]
        return (d["verified"], aj["state"], aj["reason_code"], d["final_status"], json.dumps(aj.get("warnings")))

    def test_scope_none_inactive(self):
        self.assertFalse(xz.is_ukus_active_for_run())
        self.assertIsNone(xz.decision(C12_C, C12_A))
        d = self.adapter(C12_C, C12_A, scope=None)
        self.assertFalse(d["verified"])

    def test_parent_flag_off_inactive(self):
        with xz.run_scope("X"):
            with mock.patch.object(e109, "ORTHOGRAPHIC_EQUIVALENCE_ENABLED", False):
                self.assertFalse(xz.is_ukus_active_for_run())
                self.assertIsNone(xz.decision(C12_C, C12_A))

    def test_ukus_flag_off_equals_pre_ukus_v1_signature(self):
        cases = [("Pump one's fist.", "Pump 1's fist."), ("I said no.", "I said know."), ("I said no.", "I sed no.", "I said know."), (C12_C, C12_A)]
        for c in cases:
            with mock.patch.object(e109, "UKUS_SPELLING_EQUIVALENCE_ENABLED", False):
                off = self.adapter(*c)
            on = self.adapter(*c)
            if c[0] == C12_C:
                self.assertFalse(off["verified"])
                self.assertTrue(on["verified"])
            else:
                self.assertEqual(self._sig(off), self._sig(on), c)                  # UKUS無関係の行は ON/OFF で不変(T-K ②側)

    def test_on_in_scope(self):
        with xz.run_scope("Z"):
            self.assertTrue(xz.is_ukus_active_for_run())
            d = xz.decision(C12_C, C12_A)
        self.assertIsNotNone(d)
        self.assertEqual(d.verdict, "PASS")
        self.assertEqual(d.scope, "Z")


if __name__ == "__main__":
    unittest.main()
