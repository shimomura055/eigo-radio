# -*- coding: utf-8 -*-
"""委任_03 Trial専用 数値監査・runner基本のunit test(API 0)。"""
import json
import os
import subprocess
import unittest
from decimal import Decimal as D

import er090_b3_core_number_rounding_trial_02_audit as au
import er090_b3_core_number_rounding_trial_02_labels as lab

SC = {"numbers": [
    {"class": "core", "surface": "最大134,515人", "concept": "C2"}, {"class": "core", "surface": "134,515人", "concept": "C2"},
    {"class": "core", "surface": "3回以上", "concept": "C4"}, {"class": "core", "surface": "0.0630", "concept": "C5"},
    {"class": "core", "surface": "295億9,100万ドル", "concept": "C6"},
    {"class": "peripheral", "surface": "0.0589", "concept": "P1"}]}
OV = {"entries": [{"final_decision": "APPROXIMATE_OK",
                   "surfaces": [{"surface": "最大134,515人", "approx": "最大約13万人"}, {"surface": "134,515人", "approx": "約13万人"}]}]}


class AuditTest(unittest.TestCase):
    def test_tokens_ja_composite(self):
        v = [t["value"] for t in au.tokens("295億9,100万ドルと13万5千人と3回")]
        self.assertEqual(v, [D(29591000000), D(135000), D(3)])

    def test_tokens_en_multiplier(self):
        v = [t["value"] for t in au.tokens("about 29.59 billion dollars and 134,515 people")]
        self.assertEqual(v, [D("29590000000"), D(134515)])

    def test_ja_designated_and_exact(self):
        al = au.build_allowed(SC, OV)
        r = au.classify("最大約13万人で、3回以上測り、相関は0.0630でした。", al, "ja")
        self.assertEqual(r["DESIGNATED_APPROX"], ["13万"])
        self.assertEqual(r["violations"], 0)
        self.assertEqual(sorted(r["EXACT_CORE"]), ["0.0630", "3"])

    def test_ja_undesignated_rounding_detected(self):
        al = au.build_allowed(SC, OV)
        r = au.classify("人数は約13万5千人でした。", al, "ja")
        self.assertEqual(r["UNDESIGNATED_ROUNDING"], ["13万5千"])
        self.assertEqual(r["violations"], 1)

    def test_no_overlay_rounded_value_is_violation(self):
        r = au.classify("約13万人", au.build_allowed(SC, None), "ja")
        self.assertEqual(r["violations"], 1)

    def test_peripheral_and_unauthorized(self):
        r = au.classify("0.0589と777", au.build_allowed(SC, OV), "ja")
        self.assertEqual(r["PERIPHERAL_USED"], ["0.0589"])
        self.assertEqual(r["UNAUTHORIZED"], ["777"])

    def test_en_display_precision(self):
        al = au.build_allowed(SC, OV)
        r = au.classify("revenue was $29.59 billion; up to about 130,000 people; 134,515 people; at least 3 times", al, "en")
        self.assertEqual(r["violations"], 0, r)
        self.assertEqual(au.classify("up to 135,000 people", al, "en")["violations"], 1)

    def test_en_not_in_ja(self):
        al = au.build_allowed(SC, OV)
        jset = au.ja_value_set("最大約13万人")
        r = au.classify("up to 130,000 people and 3 times", al, "en", jset)
        self.assertEqual(r["not_in_ja_r2"], ["3"])

    def test_designated_surface_verbatim(self):
        self.assertIn("最大約13万人", au.designated_surface_check("対象者は最大約13万人です。", OV)["designated_used_verbatim"])
        self.assertEqual(au.designated_surface_check("対象者は約13万人でした。", OV)["designated_used_verbatim"], ["約13万人"])

    def test_dropped_qualifier_detected(self):
        r = au.designated_surface_check("対象者は13万人でした。", OV)
        self.assertEqual(r["designated_number_without_verbatim_surface"], ["最大約13万人", "約13万人"])


class LabelsAndIsolationTest(unittest.TestCase):
    def test_labels_cover_dataset_and_values(self):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er090_output", "b3_core_number_rounding_trial_02")
        man = json.load(open(os.path.join(root, "dataset_manifest.json"), encoding="utf-8"))
        bym = {m["article_id"]: m for m in man}
        for (aid, s0), L in lab.LABELS.items():
            self.assertIn(L, ("A", "E", "B"))
            self.assertIn(aid, bym)
            self.assertIn(s0, [c["surfaces"][0] for c in bym[aid]["core"]], (aid, s0))
        for aid in {k[0] for k in lab.LABELS}:
            for c in bym[aid]["core"]:
                self.assertIn((aid, c["surfaces"][0]), lab.LABELS, "ラベル未登録の中核数値")

    def test_production_files_unchanged(self):
        here = os.path.dirname(os.path.abspath(__file__))
        files = ["er053_family_x_factlock_ja_writer_01.py", "er053_b3_deterministic_producer_01.py", "er053_risk_flagger_production_01.py",
                 "er019_family_x_entertainment_production_runner_01.py", "er006_model_routing_contract_01.py",
                 "er053_b3_annotation_contract_01.py"]
        out = subprocess.run(["git", "diff", "--quiet", "HEAD", "--"] + files, cwd=here)
        self.assertEqual(out.returncode, 0, "Production moduleに差分あり")


if __name__ == "__main__":
    unittest.main()
