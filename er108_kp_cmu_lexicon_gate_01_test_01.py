# -*- coding: utf-8 -*-
"""er108_kp_cmu_lexicon_gate_01 のtest(API 0)。実行: .venv\\Scripts\\python.exe -m unittest er108_kp_cmu_lexicon_gate_01_test_01 -v
辞書は本番と同じ`pronouncing`(cmudict)を使う。一部は注入lookupで辞書非依存に固定する。"""
from __future__ import annotations

import ast
import glob
import os
import unittest

import er108_kp_cmu_lexicon_gate_01 as g

ROOT = os.path.dirname(os.path.abspath(__file__))


class RegisteredAndUnregistered(unittest.TestCase):
    def test_pump_ones_fist_passes(self):
        pc = g.check_phrase("pump one's fist")
        self.assertTrue(pc.ok, pc.unregistered)
        self.assertEqual(pc.unregistered, [])

    def test_novelty_minaudiere_excluded_with_accent_kept(self):
        pc = g.check_phrase("novelty minaudière")
        self.assertFalse(pc.ok)
        self.assertEqual(pc.unregistered, ["minaudière"])    # 表記はアクセントのまま報告(綴り正規化で救済しない)
        self.assertEqual(pc.words[0].ok, True)                     # noveltyは登録語=Key Phrase全体でなく語単位

    def test_accent_not_folded_to_ascii(self):
        self.assertFalse(g.check_word("café", lookup=lambda w: w == "cafe").ok)     # 辞書にcafeがあってもcaféは救済しない
        self.assertFalse(g.check_word("résumé", lookup=lambda w: w == "resume").ok)

    def test_nonlexicon_oov_words_excluded(self):
        for w in ("blitzscaling", "healthspan", "Xzqwtrlk", "grogginess"):
            self.assertFalse(g.check_word(w).ok, w)

    def test_inflected_unregistered_not_rescued(self):
        """concierges(conciergeは登録語)も未登録のまま=語形変化の自動救済はしない(仕様外。CMUに無い語を推測で合格にしない)。"""
        self.assertFalse(g.check_word("concierges", lookup=lambda w: w == "concierge").ok)


class NormalizationNoFalseExclusion(unittest.TestCase):
    def test_case_insensitive(self):
        for p in ("Pump One's Fist", "PUMP ONE'S FIST", "pump one's fist"):
            self.assertTrue(g.check_phrase(p).ok, p)

    def test_edge_punctuation(self):
        for p in ("Don't Look Back,", '"pump" one\'s fist.', "(pump) fist;", "pump—fist", "pump, one's fist!"):
            pc = g.check_phrase(p)
            self.assertTrue(pc.ok, (p, pc.unregistered))

    def test_curly_apostrophe(self):
        self.assertTrue(g.check_phrase("pump one’s fist").ok)
        self.assertTrue(g.check_phrase("don’t").ok)

    def test_apostrophe_words_whole(self):
        for p in ("one's", "don't", "someone's", "o'clock", "he'll go"):
            self.assertTrue(g.check_phrase(p).ok, p)
        self.assertEqual(g.check_word("don't").route, "whole")

    def test_apostrophe_clitic_decomposition_requires_registered_base(self):
        reg = {"pump": True}
        self.assertTrue(g.check_word("pump's", lookup=lambda w: reg.get(w, False)).ok)
        self.assertEqual(g.check_word("pump's", lookup=lambda w: reg.get(w, False)).route, "clitic_decomposed")
        self.assertFalse(g.check_word("xyzzy's", lookup=lambda w: reg.get(w, False)).ok)
        # cliticは閉集合(s/d/m/re/ve/ll/t)のみ。それ以外の接尾での分解は不可
        self.assertFalse(g.check_word("pump'xyz", lookup=lambda w: reg.get(w, False)).ok)

    def test_trailing_apostrophe_and_leading_apostrophe(self):
        self.assertTrue(g.check_word("players'").ok)
        self.assertTrue(g.check_word("'bout").ok)

    def test_hyphen_whole_first_then_parts(self):
        self.assertTrue(g.check_word("well-being").ok)
        self.assertTrue(g.check_word("state-of-the-art").ok)
        lex = {"five", "minute"}
        wc = g.check_word("five-minute", lookup=lambda w: w in lex)
        self.assertTrue(wc.ok)
        self.assertEqual(wc.route, "hyphen_parts")
        wc = g.check_word("five-xyzzy", lookup=lambda w: w in lex)
        self.assertFalse(wc.ok)
        self.assertEqual(wc.unregistered_parts, ["xyzzy"])
        self.assertFalse(g.check_word("-").ok)

    def test_digits_and_symbols_are_not_words(self):
        for t in ("2", "30", "$", "100%", "—"):
            wc = g.check_word(t)
            self.assertFalse(wc.ok, t)
        self.assertFalse(g.check_phrase("a 3 day trip").ok)
        self.assertEqual(g.check_phrase("30 percent").unregistered, ["30"])
        self.assertEqual(g.check_word("covid-19").ok, False)

    def test_abbreviation_with_period(self):
        self.assertTrue(g.check_phrase("U.S. policy").ok)

    def test_empty_and_whitespace(self):
        self.assertFalse(g.check_phrase("").ok)
        self.assertFalse(g.check_phrase("   ").ok)

    def test_multiple_spaces_tokenize_like_prompt2(self):
        self.assertEqual(len(g.split_words(" pump   one's  fist ")), 3)


class NoSubstitutes(unittest.TestCase):
    def test_lookup_is_only_the_injected_or_cmu_lexicon(self):
        """合否は辞書(lookup)だけで決まる: lookupを全拒否にすれば登録語でも不合格、全許可にすれば英字を含む語は合格(LLM/台帳/外部経路が無いことの確認)。"""
        self.assertFalse(g.check_phrase("pump one's fist", lookup=lambda w: False).ok)
        self.assertTrue(g.check_phrase("zzqx blorp", lookup=lambda w: True).ok)

    def test_module_source_has_no_llm_or_ledger_or_network_imports(self):
        with open(os.path.join(ROOT, "er108_kp_cmu_lexicon_gate_01.py"), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add((n.module or "").split(".")[0])
        allowed = {"__future__", "re", "unicodedata", "dataclasses", "typing", "importlib", "os", "cmudict", "pronouncing"}
        self.assertLessEqual(mods, allowed, mods - allowed)


class ItemLevelApis(unittest.TestCase):
    def test_reasons_for_phrase(self):
        self.assertEqual(g.reasons_for_phrase("pump one's fist"), [])
        r = g.reasons_for_phrase("novelty minaudière")
        self.assertEqual(len(r), 1)
        self.assertIn("minaudière", r[0])
        self.assertIn("CMU", r[0])

    def test_partition_items_for_shortfall(self):
        keep, drop = g.partition_items(["pump one's fist", "novelty minaudière", "push prices up"])
        self.assertEqual(keep, [0, 2])
        self.assertEqual(drop, [(1, ["minaudière"])])

    def test_canonicalized_check(self):
        ok = g.canonicalized_check([{"rank": 1, "used_form": "pump one's fist"}, {"rank": 2, "used_form": "push prices up"}])
        self.assertTrue(ok["ok"])
        bad = g.canonicalized_check([{"rank": 1, "used_form": "pump one's fist"}, {"rank": 2, "used_form": "novelty minaudière"}])
        self.assertFalse(bad["ok"])
        self.assertEqual(bad["bad"], [{"rank": 2, "used_form": "novelty minaudière", "unregistered": ["minaudière"]}])
        note = g.build_canonicalized_note(bad)
        self.assertIn("minaudière", note)
        self.assertEqual(g.build_canonicalized_note(ok), "")

    def test_lexicon_info(self):
        info = g.lexicon_info()
        self.assertEqual(info["package_cmudict"], "1.1.3")
        self.assertGreater(info["entries"], 100000)


class ApplyToValidation(unittest.TestCase):
    """er105(read-only import)の実機械検証結果にCMU条件を重ねる。選定->除外->再選定->shortfallの流れ(配線後のer105挙動の写し)。"""
    ART = ("The brand launched a novelty minaudière last week. Critics said it would pump one's fist in delight. "
           "Prices pushed up again as demand rose steadily.")

    def _v(self, phrases):
        import er030_key_phrase_db_hybrid_core_01 as core
        import er105_kp_fulltext_selector_01 as ft
        units = core.build_sentence_units(self.ART)
        return ft.validate_and_resolve([{"phrase": p, "declared_word_count": len(p.split())} for p in phrases], units)

    def test_unregistered_item_makes_selection_invalid_with_reason(self):
        v = self._v(["novelty minaudière", "pump one's fist"])
        self.assertTrue(v["ok"])    # er105の既存検証だけでは通る(=CMU条件が新規に必要)
        w = g.apply_cmu_to_validation(v, final_attempt=False)
        self.assertFalse(w["ok"])
        self.assertEqual([ir["phrase"] for ir in w["item_reasons"]], ["novelty minaudière"])
        self.assertIn("minaudière", w["item_reasons"][0]["reasons"][0])
        self.assertEqual(w["cmu_excluded"], [])

    def test_final_attempt_excludes_cmu_only_items_and_keeps_rest_as_shortfall(self):
        v = self._v(["novelty minaudière", "pump one's fist"])
        w = g.apply_cmu_to_validation(v, final_attempt=True)
        self.assertTrue(w["ok"])
        self.assertEqual([r["phrase"] for r in w["resolved"]], ["pump one's fist"])
        self.assertEqual(w["cmu_excluded"], [{"index": 0, "phrase": "novelty minaudière", "unregistered": ["minaudière"]}])
        self.assertEqual(w["item_reasons"], [])

    def test_all_items_unregistered_stays_invalid_even_on_final_attempt(self):
        v = self._v(["novelty minaudière"])
        w = g.apply_cmu_to_validation(v, final_attempt=True)
        self.assertFalse(w["ok"])     # 0件確定は不可(条件緩和で数合わせしない/空で通さない)

    def test_other_hard_failures_are_never_dropped(self):
        v = self._v(["novelty minaudière", "pump one's fist", "totally invented phrase"])   # 3つ目は本文に無い
        w = g.apply_cmu_to_validation(v, final_attempt=True)
        self.assertFalse(w["ok"])

    def test_registered_only_selection_unchanged(self):
        v = self._v(["pump one's fist", "pushed up"])
        w = g.apply_cmu_to_validation(v, final_attempt=False)
        self.assertTrue(w["ok"])
        self.assertEqual(w["cmu_excluded"], [])
        self.assertEqual(w["resolved"], v["resolved"])

    def test_input_not_mutated(self):
        v = self._v(["novelty minaudière", "pump one's fist"])
        snap = repr(v)
        g.apply_cmu_to_validation(v, final_attempt=True)
        self.assertEqual(repr(v), snap)

    def test_er105_gate_flow_retry_note_then_pass(self):
        """er105.run_selection_gateを実コードのまま回し(API 0・mock selector)、validate結果にCMU条件を重ねる配線後の挙動を再現する。
        1回目=未登録語を含む選定 -> INVALID+機械診断note -> 2回目=登録語のみ -> PASS。"""
        import er105_kp_fulltext_selector_01 as ft
        orig = ft.validate_and_resolve
        calls = {"n": 0}

        def wired(selected, units):
            calls["n"] += 1
            return g.apply_cmu_to_validation(orig(selected, units), final_attempt=(calls["n"] >= ft.MAX_ATTEMPTS))

        sent = []

        def make_call_fn(msg):
            sent.append(msg)
            phrases = (["novelty minaudière", "pump one's fist"] if len(sent) == 1 else ["pump one's fist", "pushed up"])
            import json
            return lambda: (json.dumps({"items": [{"phrase": p, "word_count": len(p.split())} for p in phrases]}), "gpt-6-luna", f"r{len(sent)}")

        ft.validate_and_resolve = wired
        try:
            res = ft.run_selection_gate(self.ART, make_call_fn, sleep_fn=lambda s: None)
        finally:
            ft.validate_and_resolve = orig
        self.assertEqual(res["status"], ft.STATUS_PASS)
        self.assertEqual(len(res["attempts_detail"]), 2)
        self.assertEqual(res["attempts_detail"][0]["status"], ft.STATUS_INVALID)
        self.assertIn("CMU", sent[1])
        self.assertIn("minaudière", sent[1])
        self.assertTrue(sent[1].startswith(ft.PROMPT_2_TEXT))     # Prompt 2本文は不変
        self.assertEqual([i["source_span"].lower() for i in res["items"]], ["pump one's fist", "pushed up"])
        self.assertTrue(res["shortfall"])    # 2件 < 3件 (数合わせしない)


class Isolation(unittest.TestCase):
    def test_no_production_module_imports_er108_cmu(self):
        offenders = []
        for f in glob.glob(os.path.join(ROOT, "*.py")):
            base = os.path.basename(f)
            if base.startswith("er108_"):
                continue
            try:
                with open(f, encoding="utf-8") as fh:
                    tree = ast.parse(fh.read())
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                if any(n.startswith("er108_kp_cmu_lexicon_gate_01") for n in names):
                    offenders.append(base)
        self.assertEqual(offenders, [], f"未配線moduleをimportするfile: {offenders}")


if __name__ == "__main__":
    unittest.main()
