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
# 委任_20(2026-10-24): A-1/課題②がProductionへ配線されたため、Production側4関数のhashを配線後の値へ更新した(DEV複製は配線前の状態のTrial記録として残す。
# 配線後のDEV installerはtemplate drift guardでfail-closed=二重適用しない。下のDefaultOffIsolation/TemplateEditで固定)。
# 委任_35(2026-10-24): X2p'(新規生成経路)がProductionへ配線されたため、ga.align_glosses / ga.make_alignment_fn のhashを配線後の値へ更新した
# (ga.build_user_message_corrected=旧builderは不変。Trialは凍結)。
PROD_SRC_HASH = {
    "kc._is_valid_fulltext_normalization": ("55dec0fc4327efe7", kc._is_valid_fulltext_normalization),
    "ft.is_valid_inflection_normalization": ("dd0ca4faf3cf389f", ft.is_valid_inflection_normalization),
    "ft._token_pair_ok": ("3616a7b8760bcc04", ft._token_pair_ok),
    "ga.build_user_message_corrected": ("32b12d9ceb965306", ga.build_user_message_corrected),
    "kx._header_for": ("c09cea1aa20d0e15", kx._header_for),
    "kx.build_explanation_user_message": ("2dd4eb620c826216", kx.build_explanation_user_message),
    "kc.run_canonicalization_gate": ("3902ffd14cda8093", kc.run_canonicalization_gate),
    "ga.align_glosses": ("4018dfb466aa0aa1", ga.align_glosses),
    "ga.person_generalization_pairs": ("056971b04e3fed77", ga.person_generalization_pairs),
    "kc.make_canonicalization_fn": ("7dbf318990504198", kc.make_canonicalization_fn),
    "ga.make_alignment_fn": ("0b50a84be2a257ce", ga.make_alignment_fn),
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

    def test_dev_installer_fails_closed_after_wiring(self):
        """委任_20: A-1がProductionへ配線済みのため、DEV installerは(同じ規則を二重適用せず)template drift guardでfail-closedする。"""
        before = {"load": kc.load_prompt_template, "make": kc.make_canonicalization_fn, "gate": kc.run_canonicalization_gate,
                  "valid": kc._is_valid_fulltext_normalization, "pairs": ga.person_generalization_pairs}
        with self.assertRaises(RuntimeError) as cm:
            t.install_dev_patches()
        self.assertIn("drift", str(cm.exception))
        self.assertFalse(t._INSTALLED)
        self.assertIs(kc.load_prompt_template, before["load"])
        self.assertIs(kc.make_canonicalization_fn, before["make"])
        self.assertIs(kc.run_canonicalization_gate, before["gate"])
        self.assertIs(kc._is_valid_fulltext_normalization, before["valid"])
        self.assertIs(ga.person_generalization_pairs, before["pairs"])
        # Production側は(DEV注入なしで)A-1を受理する
        self.assertTrue(kc._is_valid_fulltext_normalization("draw a line", "draw that line", "generalize_reference_word"))
        self.assertTrue(kc._is_valid_fulltext_normalization("pull someone under", "pulled him under", "generalize_person_dependent_reference"))
        self.assertTrue(kc._is_valid_fulltext_normalization("push prices up", "pushed prices up", "lemma_normalization"))

    def test_gloss_prompt_a2_not_wired(self):
        """A-2(gloss語義方針)は本配線の対象外(未採用)。Productionのgloss生成promptにA-2の文言は入っていない。"""
        targets = [{"rank": 1, "key_phrase": "draw a line", "display_phrase": "draw that line", "japanese_gloss": None, "source_sentence": "The words draw that line simply",
                    "fulltext_source_ref": "fulltext_exact_v1"}]
        m0 = ga.build_user_message_corrected(targets, "ART", rules="RULES")
        self.assertNotIn("語義の方針", m0)
        self.assertNotIn(t.A2_EXTRA, m0)


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
    def test_anchors_consumed_and_production_template_has_rule5(self):
        """委任_20: A-1のtemplate編集はProductionのtemplateへ適用済み。DEVの旧anchor(置換前の文)は残っていない(drift guardでfail-closed)。"""
        tpl = (ROOT / kc.FULLTEXT_PROMPT_TEMPLATE_PATH).read_text(encoding="utf-8")
        self.assertIn("5. 参照語の不定化", tpl)
        self.assertIn("generalize_reference_word", tpl)
        self.assertNotIn("him/her(目的格)/them/me/us/it等の目的格", tpl)   # 旧『目的格はそのまま残す』規則は置換済み
        self.assertIn("{article_text}", tpl)
        self.assertIn("{items_json}", tpl)
        with self.assertRaises(RuntimeError):
            t.build_a1_template(tpl)

    def test_production_fulltext_enum_has_reason_but_shared_enum_does_not(self):
        s = t._dev_schema()
        enum = s["schema"]["properties"]["items"]["items"]["properties"]["normalization_reason"]["enum"]
        self.assertIn("generalize_reference_word", enum)
        prod_enum = kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT["schema"]["properties"]["items"]["items"]["properties"]["normalization_reason"]["enum"]
        self.assertIn("generalize_reference_word", prod_enum)                       # fulltext専用enumに配線済み
        self.assertNotIn("generalize_reference_word", kc.NORMALIZATION_REASONS)     # A/B/C共有enumは不変


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
    def test_wired_production_files_carry_provenance_marker(self):
        """委任_20: DEV Trialの『Production無変更』guardは配線により陳腐化した。代わりに、配線した各Production fileが承認(UDR #169/#173)への
        参照を持つこと(provenance)と、A/B/C共有schemaがバイト同一であることを固定する(後者は er003_test_kp_fulltext_wiring_01 でも固定)。"""
        for rel in ("er003_key_words_canonicalization.py", "er105_kp_fulltext_selector_01.py", "er003_v1_n3_01_scaffold_generate.py",
                    "er003_key_words_gloss_alignment.py"):
            self.assertIn("FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_20", (ROOT / rel).read_text(encoding="utf-8"), rel)


if __name__ == "__main__":
    unittest.main()
