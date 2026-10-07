"""Unit tests for er052_open238_precheck_fix_dev_01 (JPY 0, no API). Run: python test_precheck_fix_dev_01.py"""
import importlib, os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "er052_output", "open238_precheck_fix_trial_01", "tools"))
import precheck_baseline as pb
pb.install_stub()
pre = importlib.import_module("er052_open233_self_recovery_precheck_01")
runner = importlib.import_module("er052_open233_self_recovery_flow_runner_01")
fix = importlib.import_module("er052_open238_precheck_fix_dev_01")

S = fix.extract_percentages_strict


def ledger(*pairs):
    return "\n\n".join("[VERIFIED] %s: claim %s\n  numeric_value: %s\n" % (fid, fid, nv) for fid, nv in pairs)


class T(unittest.TestCase):
    def tearDown(self):
        fix.uninstall()
        fix.reset_counters()

    # ---- negatives (not extracted)
    def test_negatives(self):
        for t in ["It was set up by a third party.", "Two third parties joined.", "a third-party vendor",
                  "a half-hour delay", "in the first half of 2025", "the second half of the year",
                  "the third act ended", "The third is unclear.", "half an hour later", "a quarter century ago",
                  "half a million users", "half-life of the isotope", "a third option"]:
            self.assertEqual(S(t), set(), t)

    # ---- positives (extracted)
    def test_positives(self):
        cases = {"one third of voters": 33.3, "a third of them agreed": 33.3, "half of the respondents": 50.0,
                 "two-thirds of the votes": 66.7, "nearly half of firms": 50.0, "a quarter of the budget": 25.0,
                 "fell by half.": 50.0, "up by a third.": 33.3, "one-third more": 33.3, "three quarters of firms": 75.0}
        for t, v in cases.items():
            self.assertIn(v, S(t), t)

    # ---- known residual false positives (documented expectations, not bugs of this test)
    def test_residual_false_positives(self):
        self.assertEqual(S("They are seeking a third."), {33.3})   # ordinal elided; residual FP
        self.assertEqual(S("It works half the time."), {50.0})     # idiom; residual FP

    def test_percent_regex_unchanged(self):
        self.assertEqual(S("up 12.5% and 7 percent"), {12.5, 7.0})

    # ---- check_number_mismatch_v2
    def test_party_fp_removed_but_current_fires(self):
        led = ledger(("F-1", "50%"), ("F-2", "84%"))
        art = "A group set up by a third party said 84%."
        cur = pre.check_number_mismatch(pre.parse_ledger_text(led)[0], art, {50.0, 84.0}, set())
        self.assertEqual(cur["foreign_values"], [33.3])
        self.assertEqual([f for f in pre.run_precheck(led, art) if f["kind"] == "number_mismatch"][0]["foreign_values"], [33.3])
        fix.install(runner, pre)
        self.assertEqual([f for f in pre.run_precheck(led, art) if f["kind"] == "number_mismatch"], [])

    def test_true_mismatch_still_fires(self):
        led = ledger(("F-1", "50%"), ("F-2", "84%"))
        art = "About a third of firms said 84%."
        fix.install(runner, pre)
        fs = [f for f in pre.run_precheck(led, art) if f["kind"] == "number_mismatch"]
        self.assertEqual(len(fs), 1)
        self.assertEqual(fs[0]["foreign_values"], [33.3])
        self.assertEqual(fs[0]["field"], "F-1")

    def test_M1_ledger_check_stays_loose(self):
        led = ledger(("F-1", "about half"), ("F-2", "84%"))
        art = "Half said so. Another 84% agreed."
        before = pre.run_precheck(led, art)
        fix.install(runner, pre)
        after = pre.run_precheck(led, art)
        self.assertEqual(before, after)  # strict 'Half said' alone would have changed the gate; M1 keeps it identical
        self.assertEqual([f for f in after if f["kind"] == "number_mismatch"], [])

    def test_M1_other_percent_foreign_same(self):
        led = ledger(("F-1", "50%"), ("F-2", "84%"))
        art = "Support was 33% and 84%."
        before = pre.run_precheck(led, art)
        fix.install(runner, pre)
        self.assertEqual(before, pre.run_precheck(led, art))

    def test_M1_count_kind_untouched(self):
        led = ledger(("F-1", "3 million users"), ("F-2", "84%"))
        art = "It had 5 million users and 84% growth."
        before = pre.run_precheck(led, art)
        fix.install(runner, pre)
        self.assertEqual(before, pre.run_precheck(led, art))

    # ---- M2: locate
    def test_M2_locate_uses_strict(self):
        art = "A panel was set up by a third party. One third of firms agreed."
        finding = {"kind": "number_mismatch", "foreign_values": [33.3]}
        s0, _ = runner.resolve_precheck_target_sentence(art, finding)
        self.assertIn("third party", s0)  # current behaviour (the original incident type)
        fix.install(runner, pre)
        s1, m = runner.resolve_precheck_target_sentence(art, finding)
        self.assertEqual(s1, "One third of firms agreed.")
        self.assertEqual(m, "precheck_number_locate")
        # non-number kinds delegate to original
        self.assertEqual(runner.resolve_precheck_target_sentence(art, {"kind": "negation_marker"}), (None, "not_locatable"))

    # ---- counters: strict only at foreign calc and locate
    def test_counters(self):
        led = ledger(("F-1", "50%"), ("F-2", "84%"))
        art = "About a third of firms said 84%. A group set up by a third party."
        fix.install(runner, pre)
        fix.reset_counters()
        fs = pre.run_precheck(led, art)
        self.assertEqual(fix.counters["strict_foreign"], 1)
        self.assertEqual(fix.counters["strict_locate"], 0)
        self.assertGreater(fix.counters["loose_extract_percentages"], 0)
        runner.resolve_precheck_target_sentence(art, [f for f in fs if f["kind"] == "number_mismatch"][0])
        self.assertGreaterEqual(fix.counters["strict_locate"], 1)
        # L322 / runner L2838 / coverage checker paths keep calling the loose function (observable: unchanged outputs, loose counter rises, strict counters do not)
        sf, sl = fix.counters["strict_foreign"], fix.counters["strict_locate"]
        loose0 = fix.counters["loose_extract_percentages"]
        self.assertEqual(pre.changed_number_is_natural_rounding_only("a third party", "F-1", led), False)
        self.assertEqual(pre.extract_percentages("a third party"), {33.3})
        self.assertGreater(fix.counters["loose_extract_percentages"], loose0)
        self.assertEqual((sf, sl), (fix.counters["strict_foreign"], fix.counters["strict_locate"]))

    def test_default_noop_and_uninstall(self):
        self.assertTrue(pre.extract_percentages.__name__ == "extract_percentages")
        orig_chk = pre.check_number_mismatch
        fix.install(runner, pre)
        self.assertIsNot(pre.check_number_mismatch, orig_chk)
        fix.uninstall()
        self.assertIs(pre.check_number_mismatch, orig_chk)
        self.assertTrue(pre.extract_percentages.__name__ == "extract_percentages")


if __name__ == "__main__":
    unittest.main(verbosity=2)
