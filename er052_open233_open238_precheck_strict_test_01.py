"""OPEN-238-PRECHECK-FALSE-POSITIVE-PRODUCTION-WIRING-01: Production版 precheck 厳格抽出のunit test(¥0、API無し)。
DEVラッパではなくProductionモジュールを直接テストする。
Run: python er052_open233_open238_precheck_strict_test_01.py  (dotenv等の外部依存が無い環境ではstubを入れる)"""
import importlib, os, sys, unittest
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "er052_output", "open238_precheck_fix_trial_01", "tools"))
try:
    import dotenv  # noqa: F401
except ImportError:
    import precheck_baseline as _pb
    _pb.install_stub()
pre = importlib.import_module("er052_open233_self_recovery_precheck_01")
runner = importlib.import_module("er052_open233_self_recovery_flow_runner_01")

S = pre.extract_percentages_strict


def ledger(*pairs):
    return "\n\n".join("[VERIFIED] %s: claim %s\n  numeric_value: %s\n" % (fid, fid, nv) for fid, nv in pairs)


def nm(findings):
    return [f for f in findings if f["kind"] == "number_mismatch"]


class T(unittest.TestCase):
    def test_negatives(self):
        for t in ["It was set up by a third party.", "Two third parties joined.", "a third-party vendor",
                  "a half-hour delay", "in the first half of 2025", "the second half of the year",
                  "the third act ended", "The third is unclear.", "half an hour later", "a quarter century ago",
                  "half a million users", "half-life of the isotope", "a third option"]:
            self.assertEqual(S(t), set(), t)

    def test_positives(self):
        cases = {"one third of voters": 33.3, "a third of them agreed": 33.3, "half of the respondents": 50.0,
                 "two-thirds of the votes": 66.7, "nearly half of firms": 50.0, "a quarter of the budget": 25.0,
                 "fell by half.": 50.0, "up by a third.": 33.3, "one-third more": 33.3, "three quarters of firms": 75.0}
        for t, v in cases.items():
            self.assertIn(v, S(t), t)

    def test_residual_false_positives_documented(self):
        self.assertEqual(S("They are seeking a third."), {33.3})
        self.assertEqual(S("It works half the time."), {50.0})

    def test_percent_regex_unchanged(self):
        self.assertEqual(S("up 12.5% and 7 percent"), {12.5, 7.0})
        self.assertEqual(S(None), set())

    def test_loose_extract_percentages_unchanged(self):
        self.assertEqual(pre.extract_percentages("a third party"), {33.3})
        self.assertEqual(pre.extract_percentages("in the first half of 2025"), {50.0})

    def test_party_fp_removed(self):
        led = ledger(("F-1", "50%"), ("F-2", "84%"))
        art = "A group set up by a third party said 84%."
        self.assertEqual(nm(pre.run_precheck(led, art)), [])
        self.assertIsNone(pre.check_number_mismatch(pre.parse_ledger_text(led)[0], art, {50.0, 84.0}, set()))

    def test_true_mismatch_still_fires(self):
        led = ledger(("F-1", "50%"), ("F-2", "84%"))
        fs = nm(pre.run_precheck(led, "About a third of firms said 84%."))
        self.assertEqual(len(fs), 1)
        self.assertEqual(fs[0]["foreign_values"], [33.3])
        self.assertEqual(fs[0]["field"], "F-1")

    def test_percent_foreign_still_fires(self):
        led = ledger(("F-1", "50%"), ("F-2", "84%"))
        fs = nm(pre.run_precheck(led, "Support was 33% and 84%."))
        self.assertEqual(fs[0]["foreign_values"], [33.0])

    def test_M1_ledger_check_stays_loose(self):
        # 台帳値確認はlooseのまま: 'Half said so'は台帳"about half"(50)の一致として扱われmismatchにならない
        led = ledger(("F-1", "about half"), ("F-2", "84%"))
        self.assertEqual(nm(pre.run_precheck(led, "Half said so. Another 84% agreed.")), [])

    def test_M1_count_kind_untouched(self):
        led = ledger(("F-1", "3 million users"), ("F-2", "84%"))
        fs = nm(pre.run_precheck(led, "It had 5 million users and 84% growth."))
        self.assertEqual(len(fs), 1)
        self.assertTrue(fs[0]["article_evidence"].startswith("count"))

    def test_M2_locate_uses_strict(self):
        art = "A panel was set up by a third party. One third of firms agreed."
        s, m = runner.resolve_precheck_target_sentence(art, {"kind": "number_mismatch", "foreign_values": [33.3]})
        self.assertEqual((s, m), ("One third of firms agreed.", "precheck_number_locate"))
        self.assertEqual(runner.resolve_precheck_target_sentence("A third party.", {"kind": "number_mismatch", "foreign_values": [33.3]}),
                         (None, "not_locatable"))
        self.assertEqual(runner.resolve_precheck_target_sentence(art, {"kind": "negation_marker"}), (None, "not_locatable"))

    def test_other_paths_stay_loose(self):
        # L322(changed_number_is_natural_rounding_only)は現行のまま(loose)
        led = ledger(("F-1", "50%"), ("F-2", "84%"))
        self.assertEqual(pre.changed_number_is_natural_rounding_only("a third party", "F-1", led), False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
