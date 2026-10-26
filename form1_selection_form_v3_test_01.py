# -*- coding: utf-8 -*-
"""LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_01 のtest(接続0・API 0・Production経路非依存)。
nodeでform_logic.jsの単体testを実行し、データ・参照HTML保全・Production非接続を検証する。"""
import hashlib
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(ROOT, "user_test", "selection_form_v3")
RD = os.path.join(ROOT, "docs", "research", "LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01")
REF = os.path.join(ROOT, "docs", "pm", "Phrase_Form", "eigo_radio_selection_form_reference.html")
REF_SHA256 = "13ef9085f625ea1618e63500793ffcbe959552c8ac0325484c623b1edb4fce79"   # 受領時の参照HTML(無改変)


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class SelectionFormV3Test(unittest.TestCase):
    def test_reference_html_unmodified(self):
        with open(REF, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), REF_SHA256)

    def test_node_logic_suite(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "node が必要(form_logic.jsの単体test)")
        r = subprocess.run([node, os.path.join(RD, "selection_form_logic_test_01.js")], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("ALL PASS", r.stdout)

    def test_monkeys_paw_data_matches_trial02_result(self):
        d = _j(os.path.join(FD, "data", "monkeys_paw__b1b.json"))
        with open(os.path.join(ROOT, "docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/RESULT_02.md"), encoding="utf-8") as f:
            md = f.read()
        sec = md[md.index("## monkeys_paw:b1b"):]
        for it in d["phrases"] + d["words"]:
            self.assertIn("| " + it["term"] + " |", sec, it["term"])
        self.assertEqual((len(d["phrases"]), len(d["words"])), (7, 4))
        self.assertEqual(d["source"]["kind"], "DEV_TRIAL")
        self.assertEqual(d["grammar"], [])        # 正式文法候補なし。仮データを入れない
        self.assertNotIn("interferes", [x["term"] for x in d["phrases"] + d["words"]])   # Gate除外語は出さない

    def test_no_placeholder_grammar_in_formal_data(self):
        for fn in os.listdir(os.path.join(FD, "data")):
            if fn.startswith("ui_check_dummy") or fn == "articles.json":
                continue
            s = open(os.path.join(FD, "data", fn), encoding="utf-8").read()
            self.assertNotIn("過去完了形", s)
            self.assertNotIn("分詞による名詞の後置修飾", s)

    def test_form_not_connected_to_production(self):
        """フォームはProduction Pythonを一切importしない/参照しない(静的HTML+JSのみ)。"""
        for fn in ("index.html", "form_logic.js"):
            s = open(os.path.join(FD, fn), encoding="utf-8").read()
            for bad in ("er119_", "er105_", "er003_", "er125_", "OPENAI_API_KEY", "api_key"):
                self.assertNotIn(bad, s, fn)

    def test_index_html_references_exist(self):
        s = open(os.path.join(FD, "index.html"), encoding="utf-8").read()
        for ref in ("form_logic.js", "data/articles.json"):
            self.assertIn(ref, s)
            self.assertTrue(os.path.exists(os.path.join(FD, ref)))


if __name__ == "__main__":
    unittest.main()
