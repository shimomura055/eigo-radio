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

    def _gate(self, per_attempt):
        import json
        import er105_kp_fulltext_selector_01 as ft
        sent = []

        def make_call_fn(msg):
            sent.append(msg)
            phrases = per_attempt[min(len(sent), len(per_attempt)) - 1]
            return lambda: (json.dumps({"items": [{"phrase": p, "word_count": len(p.split())} for p in phrases]}), "gpt-6-luna", f"r{len(sent)}")

        res = ft.run_selection_gate(self.ART, make_call_fn, sleep_fn=lambda s: None)
        return ft, res, sent

    def test_er105_gate_flow_retry_note_then_pass(self):
        """配線後のer105.run_selection_gateを実コードのまま回す(API 0・mock selector)。
        1回目=未登録語を含む選定 -> INVALID+機械診断note -> 2回目=登録語のみ -> PASS。"""
        ft, res, sent = self._gate([["novelty minaudière", "pump one's fist"], ["pump one's fist", "pushed up"]])
        self.assertEqual(res["status"], ft.STATUS_PASS)
        self.assertEqual(len(res["attempts_detail"]), 2)
        self.assertEqual(res["attempts_detail"][0]["status"], ft.STATUS_INVALID)
        self.assertIn("CMU", sent[1])
        self.assertIn("minaudière", sent[1])
        self.assertTrue(sent[1].startswith(ft.PROMPT_2_TEXT))     # Prompt 2本文は不変
        self.assertEqual([i["source_span"].lower() for i in res["items"]], ["pump one's fist", "pushed up"])
        self.assertTrue(res["shortfall"])    # 2件 < 3件 (数合わせしない)
        cg = res["cmu_gate"]
        self.assertTrue(cg["applied"] and cg["attempts_with_cmu_reason"] == [1] and cg["excluded"] == [])
        self.assertEqual(cg["lexicon"]["package_cmudict"], "1.1.3")      # OF-KPQ-P-05: 辞書versionをmetadataに固定

    def test_er105_gate_final_attempt_excludes_cmu_only_and_confirms_shortfall(self):
        ft, res, sent = self._gate([["novelty minaudière", "pump one's fist"], ["novelty minaudière", "pump one's fist"]])
        self.assertEqual(res["status"], ft.STATUS_PASS)
        self.assertEqual([i["source_span"].lower() for i in res["items"]], ["pump one's fist"])
        self.assertEqual(res["cmu_gate"]["excluded"][0]["phrase"], "novelty minaudière")
        self.assertEqual(res["cmu_gate"]["excluded"][0]["unregistered"], ["minaudière"])
        self.assertEqual([i["rank"] for i in res["items"]], [1])         # rankは1..nに振り直し

    def test_er105_gate_all_unregistered_is_invalid_not_empty(self):
        ft, res, sent = self._gate([["novelty minaudière"], ["novelty minaudière"]])
        self.assertEqual(res["status"], ft.STATUS_INVALID)
        self.assertIsNone(res["items"])

    def test_run_fulltext_selection_records_cmu_gate_in_metadata(self):
        import json
        import tempfile
        import er105_kp_fulltext_selector_01 as ft

        def make_call_fn(msg):
            return lambda: (json.dumps({"items": [{"phrase": "pump one's fist", "word_count": 3}]}), "gpt-6-luna", "r1")

        with tempfile.TemporaryDirectory() as d:
            ft.run_fulltext_selection(self.ART, d, "A", "a2", process=None, make_call_fn=make_call_fn, sleep_fn=lambda s: None)
            meta = json.load(open(os.path.join(d, "keywords_runtime_metadata.json"), encoding="utf-8"))
        self.assertTrue(meta["cmu_gate"]["applied"])
        self.assertEqual(meta["cmu_gate"]["lexicon"]["package_cmudict"], "1.1.3")


class PostCanonOuterRetry(unittest.TestCase):
    """M2(OF-KPQ-P-02): run_kp_with_outer_retryがcanonicalization後のCMU未登録をINVALID扱いし、keywords_canonicalized.jsonを即退避して次周へnoteを渡す。"""

    def _run(self, tmp, merged_per_attempt, max_outer=3):
        import json
        import er003_v1_n3_01_scaffold_generate as sc
        notes = []
        n = {"sel": 0, "canon": 0}

        def select_fn(text, kp_dir, article_id, level, process=None, diagnostic_note=None):
            n["sel"] += 1
            notes.append(diagnostic_note)
            return {"status": "KEY_WORDS_STRUCTURE_PASS", "original_items": [{"rank": 1}], "parsed": {"items": [{"display_phrase": "x"}]}}

        def canon_fn(text, items, kp_dir, article_id, process=None):
            n["canon"] += 1
            merged = {"items": merged_per_attempt[min(n["canon"], len(merged_per_attempt)) - 1]}
            with open(os.path.join(kp_dir, "keywords_canonicalized.json"), "w", encoding="utf-8") as f:
                json.dump(merged, f)
            return {"status": "CANONICALIZATION_PASS", "merged": merged}

        red = lambda *a, **k: {"status": "REDUNDANCY_PASS", "duplicate_pairs": []}
        res = sc.run_kp_with_outer_retry("text", tmp, "A", "a2", select_fn=select_fn, canon_fn=canon_fn, redundancy_fn=red,
                                         max_outer=max_outer)
        return sc, res, notes, n

    def test_cmu_ng_after_canon_retires_artifact_and_passes_note_to_next_round(self):
        import tempfile
        bad = [{"rank": 1, "used_form": "novelty minaudière"}]
        good = [{"rank": 1, "used_form": "pump one's fist"}]
        with tempfile.TemporaryDirectory() as d:
            sc, res, notes, n = self._run(d, [bad, good])
            self.assertNotIn("status", res)                                  # 2周目でPASS
            self.assertEqual(n["sel"], 2)
            self.assertIn("minaudière", notes[1])                            # CMU診断noteが次周へ
            self.assertIn("CMU", notes[1])
            self.assertEqual(res["outer_retry_log"][0]["canonicalization_status"], "CMU_POST_CANON_INVALID")
            self.assertTrue(res["outer_retry_log"][0]["stale_artifact"].endswith(".json"))
            self.assertTrue(os.path.exists(res["outer_retry_log"][0]["stale_artifact"]))
            self.assertTrue(os.path.exists(os.path.join(d, "keywords_canonicalized.json")))   # 2周目のPASS成果物

    def test_cmu_ng_every_round_exhausts_and_no_keywords_file_remains(self):
        import tempfile
        bad = [{"rank": 1, "used_form": "novelty minaudière"}]
        with tempfile.TemporaryDirectory() as d:
            sc, res, notes, n = self._run(d, [bad], max_outer=3)
            self.assertEqual(res["status"], "OUTER_RETRY_EXHAUSTED")
            self.assertEqual(n["sel"], 3)
            self.assertFalse(os.path.exists(os.path.join(d, "keywords_canonicalized.json")))   # 本名のまま残さない(TTS段が読まない)

    def test_registered_used_form_unchanged_flow(self):
        import tempfile
        good = [{"rank": 1, "used_form": "pump one's fist"}]
        with tempfile.TemporaryDirectory() as d:
            sc, res, notes, n = self._run(d, [good])
            self.assertNotIn("status", res)
            self.assertEqual(n["sel"], 1)
            self.assertTrue(res["outer_retry_log"][0]["cmu_post_canon"]["ok"])


class Importers(unittest.TestCase):
    ALLOWED = {"er105_kp_fulltext_selector_01.py", "er003_v1_n3_01_scaffold_generate.py",
               "er119_kp_candidates_01.py",   # KP Human Review(2026-10-25 APPROVED_FOR_PRODUCTION): X/Z共通の候補生成でCMU gateを適用
               "er125_kp_rescue_production_01.py"}   # 救済方式(2026-10-26 APPROVED_FOR_PRODUCTION): 救済後keyもCMU検査(分解救済しない)。generate_candidates経由のX/Y/Z共通経路

    def test_cmu_gate_is_imported_only_by_x_z_shared_kp_path(self):
        """A/B/Cの量産経路(er003 v1 main/N3 tts, er013, er006 shared narration等)はCMU gateを使わない。許可=全文選定(M1)と共通外側retry(M2)のみ。"""
        offenders = []
        for f in glob.glob(os.path.join(ROOT, "*.py")):
            base = os.path.basename(f)
            if base.startswith("er108_") or "_test" in base:
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
                if any(n.startswith("er108_kp_cmu_lexicon_gate_01") for n in names) and base not in self.ALLOWED:
                    offenders.append(base)
        self.assertEqual(sorted(set(offenders)), [], f"許可外のimporter: {offenders}")

    def test_legacy_strategy_l_path_does_not_call_cmu(self):
        """A/B/Cの`_run_key_phrases_impl`(strategy_l)にはCMU呼出が無い。"""
        src = open(os.path.join(ROOT, "er003_v1_n3_01_scaffold_generate.py"), encoding="utf-8").read()
        a = src.index("def _run_key_phrases_impl")
        self.assertNotIn("cmu.", src[a:a + 6000])


if __name__ == "__main__":
    unittest.main()
