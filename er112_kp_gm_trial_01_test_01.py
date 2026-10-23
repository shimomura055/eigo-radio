# -*- coding: utf-8 -*-
"""er112_kp_gm_trial_01 のテスト(API 0、DefaultOffIsolation型)。実行: .venv\\Scripts\\python.exe -m pytest er112_kp_gm_trial_01_test_01.py -q"""
import hashlib
import inspect
import json
import re
import subprocess
import unittest
from pathlib import Path

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga
import er019_family_x_kp_explanation_01 as kx
import er105_kp_fulltext_selector_01 as ft
import er112_kp_gm_trial_01 as t

ROOT = Path(__file__).resolve().parent

# Production関数のsource hash(先頭16桁)。DEV側で複製・ラップしている関数が変わったらこのtestが落ち、DEV側の再レビューを強制する(drift guard)。
PROD_SRC_HASH = {
    "kc._is_valid_fulltext_normalization": ("ce19f2ce2cb554e4", kc._is_valid_fulltext_normalization),
    "ft.is_valid_inflection_normalization": ("e794d650688f1bdb", ft.is_valid_inflection_normalization),
    "ft._token_pair_ok": ("3616a7b8760bcc04", ft._token_pair_ok),
    "ga.build_user_message_corrected": ("32b12d9ceb965306", ga.build_user_message_corrected),
    "kx._header_for": ("c09cea1aa20d0e15", kx._header_for),
    "kx.build_explanation_user_message": ("2dd4eb620c826216", kx.build_explanation_user_message),
    "kc.run_canonicalization_gate": ("4f482fafa4342d70", kc.run_canonicalization_gate),
    "ga.align_glosses": ("cbb5a74e7d3ae0a5", ga.align_glosses),
    "ga.person_generalization_pairs": ("d1d869fabb81444d", ga.person_generalization_pairs),
    "kc.make_canonicalization_fn": ("7dbf318990504198", kc.make_canonicalization_fn),
    "ga.make_alignment_fn": ("94fd639bd6d9e22e", ga.make_alignment_fn),
    "kc.load_prompt_template": ("1f6714df01309fbe", kc.load_prompt_template),
}


class DefaultOffIsolation(unittest.TestCase):
    """import・未install・ctx無しでは、Production関数の挙動・API呼出・副作用ファイルが一切変わらない。"""

    def test_import_does_not_patch(self):
        self.assertFalse(t._INSTALLED)
        for name, (h, fn) in PROD_SRC_HASH.items():
            self.assertEqual(hashlib.sha256(inspect.getsource(fn).encode()).hexdigest()[:16], h, f"{name}: Production source drift (DEV複製の再レビューが必要)")

    def test_no_production_module_imports_er112(self):
        hits = []
        for f in ROOT.glob("*.py"):
            if f.name.startswith("er112_"):
                continue
            try:
                txt = f.read_text(encoding="utf-8")
            except Exception:
                continue
            if re.search(r"^\s*(import|from)\s+er112_kp_gm", txt, re.M):
                hits.append(f.name)
        self.assertEqual(hits, [])

    def test_installed_but_no_ctx_is_passthrough(self):
        t.install_dev_patches()
        try:
            t._TL.ctx = None
            # 参照語置換はctx無し(=baseline)では受理されない(Production挙動)
            self.assertFalse(kc._is_valid_fulltext_normalization("draw a line", "draw that line", "generalize_reference_word"))
            self.assertFalse(kc._is_valid_fulltext_normalization("pull someone under", "pulled him under", "generalize_person_dependent_reference"))
            self.assertTrue(kc._is_valid_fulltext_normalization("push prices up", "pushed prices up", "lemma_normalization"))
            tpl = kc.load_prompt_template(kc.FULLTEXT_PROMPT_TEMPLATE_PATH)
            self.assertNotIn("generalize_reference_word", tpl)
            # baseline armでも素通し
            t._TL.ctx = t.ArmCtx("base", 1, "u")
            self.assertFalse(kc._is_valid_fulltext_normalization("draw a line", "draw that line", "generalize_reference_word"))
            self.assertNotIn("generalize_reference_word", kc.load_prompt_template(kc.FULLTEXT_PROMPT_TEMPLATE_PATH))
            self.assertEqual(kx._header_for(5), t._ORIG["kx._header_for"](5))
            # a1 arm のときだけ有効
            t._TL.ctx = t.ArmCtx("a1", 1, "u")
            self.assertTrue(kc._is_valid_fulltext_normalization("draw a line", "draw that line", "generalize_reference_word"))
            self.assertIn("generalize_reference_word", kc.load_prompt_template(kc.FULLTEXT_PROMPT_TEMPLATE_PATH))
            self.assertEqual(kx._header_for(5), t._ORIG["kx._header_for"](5))   # a3未指定なら説明Promptは不変
            t._TL.ctx = t.ArmCtx("a123s", 1, "u")
            self.assertIn("Use the sense the phrase has in the source sentence", kx._header_for(5))
            self.assertEqual(kx.PROMPT_SHA256, kx.PROMPT_SHA256)   # 本番定数(逐語性hash)はDEV注入で変わらない
        finally:
            t._TL.ctx = None
            t.uninstall_dev_patches()
        self.assertFalse(t._INSTALLED)
        self.assertFalse(kc._is_valid_fulltext_normalization("draw a line", "draw that line", "generalize_reference_word"))

    def test_gloss_prompt_a2_only_when_flagged(self):
        t.install_dev_patches()
        try:
            targets = [{"rank": 1, "key_phrase": "draw a line", "display_phrase": "draw that line", "japanese_gloss": None, "source_sentence": "The words draw that line simply",
                        "fulltext_source_ref": "fulltext_exact_v1"}]
            t._TL.ctx = t.ArmCtx("a1", 1, "u")
            m1 = ga.build_user_message_corrected(targets, "ART", rules="RULES")
            t._TL.ctx = t.ArmCtx("a12", 1, "u")
            m2 = ga.build_user_message_corrected(targets, "ART", rules="RULES")
            t._TL.ctx = None
            m0 = ga.build_user_message_corrected(targets, "ART", rules="RULES")
            self.assertEqual(m0, m1)
            self.assertNotIn("語義の方針", m1)
            self.assertIn("語義の方針", m2)
            self.assertEqual(m2.replace(t.A2_EXTRA, ""), m1)
        finally:
            t._TL.ctx = None
            t.uninstall_dev_patches()


class ValidatorDev(unittest.TestCase):
    CASES = [
        ("draw a line", "draw that line", True), ("draw the line", "draw that line", False), ("float an idea", "float that idea", True),
        ("float a idea", "float that idea", False), ("take a step", "take that step", True), ("take that advice", "take that advice", False),
        ("take an advice", "take that advice", False), ("cost a much", "cost that much", False), ("so a nobody noticed", "so that nobody noticed", False),
        ("a time", "that time", False), ("pull someone under", "pulled him under", True), ("sentence someone to death", "sentenced him to death", True),
        ("tell someone the truth", "told her the truth", True), ("lose someone job", "lose her job", False), ("lose someone's job", "lose her job", True),
        ("close around someone", "close around me", True), ("give someone a hand", "gave him a hand", True), ("make a call", "make that call", True),
        ("bind to the protein", "bound to the protein", False), ("push prices up", "pushed prices up", True),
    ]

    def test_cases(self):
        for k, d, exp in self.CASES:
            self.assertEqual(t.dev_is_valid_inflection_normalization(k, d), exp, (k, d))

    def test_reason_gate(self):
        self.assertTrue(t.dev_is_valid_fulltext_normalization("draw a line", "draw that line", "generalize_reference_word"))
        self.assertTrue(t.dev_is_valid_fulltext_normalization("pull someone under", "pulled him under", "generalize_person_dependent_reference"))
        self.assertFalse(t.dev_is_valid_fulltext_normalization("draw a line", "draw that line", "none"))
        self.assertFalse(t.dev_is_valid_fulltext_normalization("draw a line", "draw that line", "other"))

    def test_an_agreement_uses_cmu(self):
        self.assertTrue(t.starts_with_vowel_sound("idea"))
        self.assertTrue(t.starts_with_vowel_sound("hour"))
        self.assertFalse(t.starts_with_vowel_sound("line"))
        self.assertFalse(t.starts_with_vowel_sound("university"))


class TemplateEdit(unittest.TestCase):
    def test_anchors_unique_and_edit_applied(self):
        tpl = (ROOT / kc.FULLTEXT_PROMPT_TEMPLATE_PATH).read_text(encoding="utf-8")
        for old, _new in t._A1_EDITS:
            self.assertEqual(tpl.count(old), 1, old[:30])
        out = t.build_a1_template(tpl)
        self.assertIn("5. 参照語の不定化", out)
        self.assertIn("generalize_reference_word", out)
        self.assertNotIn("him/her(目的格)/them/me/us/it等の目的格", out)   # 旧『目的格はそのまま残す』規則は置換済み
        self.assertIn("{article_text}", out)
        self.assertIn("{items_json}", out)

    def test_dev_schema_adds_reason_only_in_dev(self):
        s = t._dev_schema()
        enum = s["schema"]["properties"]["items"]["items"]["properties"]["normalization_reason"]["enum"]
        self.assertIn("generalize_reference_word", enum)
        prod_enum = kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT["schema"]["properties"]["items"]["items"]["properties"]["normalization_reason"]["enum"]
        self.assertNotIn("generalize_reference_word", prod_enum)


class ShareArm(unittest.TestCase):
    def test_share_replaces_gloss_only_for_same_used_form(self):
        t._TL.ctx = t.ArmCtx("a123s", 1, "u")
        try:
            items = [{"rank": 1, "used_form": "draw a line", "gloss": "その線を引く"}, {"rank": 2, "used_form": "give way", "gloss": "崩れる"}]
            a2 = {"items": [{"used_form": "Draw a line", "gloss": "境界線を設ける"}, {"used_form": "other", "gloss": "x"}]}
            rec = {}
            t._apply_share({"level": "b1b"}, items, a2, rec)
            self.assertEqual(items[0]["gloss"], "境界線を設ける")
            self.assertEqual(items[1]["gloss"], "崩れる")
            self.assertEqual(len(rec["shared"]), 1)
            # a2 unit・shareなしarmでは変えない
            t._TL.ctx = t.ArmCtx("a12", 1, "u")
            items2 = [{"rank": 1, "used_form": "draw a line", "gloss": "A"}]
            rec2 = {}
            t._apply_share({"level": "b1b"}, items2, a2, rec2)
            self.assertEqual(items2[0]["gloss"], "A")
        finally:
            t._TL.ctx = None


class ProductionUnchanged(unittest.TestCase):
    def test_git_diff_has_no_production_file_change(self):
        out = subprocess.run(["git", "diff", "--name-only", "--"] + t.PROD_FILES, cwd=ROOT, capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "", f"Production file modified: {out}")


if __name__ == "__main__":
    unittest.main()
