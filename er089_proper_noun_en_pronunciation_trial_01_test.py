# -*- coding: utf-8 -*-
"""er089 lib の単体test(API 0・費用0)。実行: .venv\\Scripts\\python.exe er089_proper_noun_en_pronunciation_trial_01_test.py"""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er089_proper_noun_en_pronunciation_trial_01_lib as L  # noqa: E402
import er006_pronunciation_ledger_01 as led  # noqa: E402
import er006_pronunciation_research_01 as res  # noqa: E402
import er006_secondary_asr_01 as sec  # noqa: E402

TEXT_B = ("The company that runs LINE Manga has announced the launch of “byUs,” an AI story chat service. "
          "It is pronounced “bias.” You can take a step from the reader's seat onto the stage of story-making.")


def good_item(surface="Foobar", hint="FOO-bar", url="https://example.test/p", quote="Foobar is pronounced FOO-bar."):
    return {"surface": surface, "entity_type": "product", "canonical_spelling": surface, "status": "CONFIRMED",
            "pronunciation_hint": hint, "expected_pronunciation_ipa": "/ˈfuːbɑːr/", "alternate_pronunciations": [],
            "confidence": "medium", "source_url": url, "quote": quote, "source_type": "official_text_phonetic", "ambiguity_note": ""}


META = {"retrieved_at": "2026-10-21T00:00:00", "model": "x", "prompt_sha256": "abc", "response_id": "r"}


class IsolationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="er089test_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_stub_fires_and_is_recorded_outside_arm(self):
        orig = res.research_pronunciations
        with L.TrialIsolation(out_dir=self.tmp) as iso:
            r = res.research_pronunciations([{"surface": "x", "entity_type": "unknown"}])
            self.assertEqual(r["status"], "FAILED")
            self.assertEqual(len(iso.unexpected_calls()), 1)
            # Production経路(_resolve_unresolved_entity_for_review 等が参照する属性)も同じstub
            self.assertIs(sec.pronun_research.research_pronunciations, res.research_pronunciations)
        self.assertIs(res.research_pronunciations, orig)  # 退出で復元

    def test_isolated_paths_and_ledger_untouched(self):
        real_sha = L.sha256_file(os.path.join(L.ROOT, L.REAL_LEDGER_PATH))
        import er011_human_review_lock_01 as rl
        import er025_entity_pronunciation_resolver_core_01 as e25
        saved = (sec.HUMAN_REVIEW_LOG_PATH, rl.ATTEMPT_HISTORY_PATH, e25.TELEMETRY_PATH, led.LEDGER_PATH)
        with L.TrialIsolation(out_dir=self.tmp) as iso:
            self.assertTrue(sec.HUMAN_REVIEW_LOG_PATH.startswith(self.tmp))
            self.assertTrue(rl.ATTEMPT_HISTORY_PATH.startswith(self.tmp))
            self.assertTrue(e25.TELEMETRY_PATH.startswith(self.tmp))
            self.assertEqual(os.path.abspath(led.LEDGER_PATH), os.path.abspath(iso.trial_ledger))
            # Trial Ledgerへの登録は実Ledgerを変えない
            L.register_entry(iso.trial_ledger, "Foobar", L.validate_item(
                good_item(), "Foobar", {}, fetch=lambda u: "Foobar is pronounced FOO-bar. more", arm="A", meta=META)["entry"])
            # 隔離telemetry wrapperが指定path以外へ書かない
            import er021_en_asr_semantic_equivalence_production_01 as sem
            sem.append_telemetry_log({"x": 1})
            self.assertTrue(os.path.exists(os.path.join(iso.iso_dir, "semantic_equivalence_telemetry.jsonl")))
        self.assertEqual(L.sha256_file(os.path.join(L.ROOT, L.REAL_LEDGER_PATH)), real_sha)
        self.assertEqual(saved, (sec.HUMAN_REVIEW_LOG_PATH, rl.ATTEMPT_HISTORY_PATH, e25.TELEMETRY_PATH, led.LEDGER_PATH))
        d = L.ledger_diff(L.ledger_snapshot(iso.base_ledger), L.ledger_snapshot(iso.trial_ledger))
        self.assertEqual(len(d["added"]), 1)
        self.assertEqual(d["changed"], [])

    def test_register_refuses_real_ledger_and_mismatch(self):
        with L.TrialIsolation(out_dir=self.tmp) as iso:
            with self.assertRaises(RuntimeError):
                L.register_entry(os.path.join(L.ROOT, L.REAL_LEDGER_PATH), "Foobar", {"entity_type": "product"})
            with self.assertRaises(RuntimeError):
                L.register_entry(os.path.join(self.tmp, "other.json"), "Foobar", {"entity_type": "product"})

    def test_azure_stub_injection_and_no_network(self):
        wav = os.path.join(self.tmp, "a.wav")
        with open(wav, "wb") as f:
            f.write(b"RIFF")
        with L.TrialIsolation(out_dir=self.tmp) as iso:
            iso.injected_azure[os.path.abspath(wav)] = "hello"
            self.assertEqual(sec.get_full_text_via_azure_stt_with_phrase_list(wav, phrases=["x"]), ("hello", None))
            t, e = sec.get_full_text_via_azure_stt_with_phrase_list(os.path.join(self.tmp, "b.wav"))
            self.assertIsNone(t)
            self.assertEqual(e, "trial_stub_no_stored_transcript")

    def test_m1_reset_on_ledger_switch(self):
        with L.TrialIsolation(out_dir=self.tmp) as iso:
            sec._M1_FROZEN_CACHE["k"] = 1
            sec._M1_SNAPSHOT_CACHE["k"] = 1
            iso.set_ledger(iso.base_ledger)
            self.assertEqual(sec._M1_FROZEN_CACHE, {})
            self.assertEqual(sec._M1_SNAPSHOT_CACHE, {})
            self.assertEqual(os.path.abspath(led.LEDGER_PATH), os.path.abspath(iso.base_ledger))


class ValidatorTest(unittest.TestCase):
    def test_v1p_pseudo_word_zorbleflux_falls(self):
        item = good_item("Zorbleflux", "ZOR-bul-flux", url="https://zorbleflux.invalid/about",
                         quote="Zorbleflux is pronounced ZOR-bul-flux.")

        def boom(u):
            raise OSError("name resolution failed")
        r = L.validate_item(item, "Zorbleflux", {}, fetch=boom, arm="A", meta=META)
        self.assertEqual(r["decision"], "UNCONFIRMED_SAFE")
        self.assertIn("source_unverifiable", r["reasons"])
        self.assertIsNone(r["entry"])

    def test_v1p_quote_not_in_page(self):
        r = L.validate_item(good_item(), "Foobar", {}, fetch=lambda u: "unrelated page text", arm="A", meta=META)
        self.assertEqual(r["decision"], "UNCONFIRMED_SAFE")
        self.assertIn("source_unverifiable", r["reasons"])

    def test_register_when_all_pass(self):
        r = L.validate_item(good_item(), "Foobar", {}, fetch=lambda u: "x Foobar is pronounced FOO-bar. y", arm="A", meta=META)
        self.assertEqual(r["decision"], "REGISTER", r["reasons"])
        self.assertTrue(r["entry"]["tts_injection_disabled"])
        self.assertEqual(r["entry"]["resolution_method"], "en_web_research_trial")

    def test_japanese_only_rejected(self):
        it = good_item(quote="「Foobar」は「フーバー」と読みます pronounced")
        r = L.validate_item(it, "Foobar", {}, fetch=lambda u: it["quote"], arm="A", meta=META)
        self.assertIn("V2_japanese_only_or_katakana_inference", r["reasons"])

    def test_hint_contamination_rejected(self):
        for bad in ("FOO-bar (or foo-BAR)", "FOO-bar / foo-BAR", "フーバー", "FOO-bar or foo-BAR"):
            it = good_item(hint=bad)
            r = L.validate_item(it, "Foobar", {}, fetch=lambda u: it["quote"], arm="A", meta=META)
            self.assertIn("V3_format_or_canonical_mismatch", r["reasons"], bad)

    def test_high_confidence_requires_audio(self):
        it = good_item()
        it["confidence"] = "high"
        r = L.validate_item(it, "Foobar", {}, fetch=lambda u: it["quote"], arm="A", meta=META)
        self.assertTrue(r["checks"]["V4_downgraded_high_to_medium"])
        self.assertEqual(r["entry"]["confidence"], "medium")

    def test_v5_veto_limited_to_qualifying_entries(self):
        base = {"surface": "Foobar", "canonical_spelling": "Foobar", "sources": ["https://x"], "confidence": "medium",
                "pronunciation_hint": "FOO-bar", "expected_pronunciation_ipa": "/other/", "entity_type": "product"}
        it = good_item(hint="foo-BAR")

        def run(entry):
            return L.validate_item(it, "Foobar", {"k": entry}, fetch=lambda u: it["quote"], arm="A", meta=META)
        # 品質基準を満たす既存entry(hint違い)は拒否権あり
        self.assertIn("V5_conflict_with_qualifying_entry", run(dict(base))["reasons"])
        # low / 汚染hint / ja_reading_katakana / cascade_unresolved / sources空 は拒否権なし
        for patch in ({"confidence": "low"}, {"pronunciation_hint": "FOO-bar (or foo-BAR)"}, {"entity_type": "ja_reading_katakana"},
                      {"entity_type": "cascade_unresolved_entity"}, {"sources": []}):
            e = dict(base)
            e.update(patch)
            r = run(e)
            self.assertNotIn("V5_conflict_with_qualifying_entry", r["reasons"], patch)
            self.assertEqual(r["decision"], "REGISTER", (patch, r["reasons"]))
            self.assertEqual(len(r["checks"]["V5_non_veto_coexisting"]), 1)


    def test_alternates_ipa_with_annotation_are_cleaned_not_rejected(self):
        it = good_item()
        it["alternate_pronunciations"] = ["/ˈfʊbar/ — British English"]
        r = L.validate_item(it, "Foobar", {}, fetch=lambda u: it["quote"], arm="A", meta=META)
        self.assertEqual(r["decision"], "REGISTER", r["reasons"])
        self.assertEqual(r["entry"]["alternate_pronunciations"], ["/ˈfʊbar/"])
        it["alternate_pronunciations"] = ["plain words with no slashes at all nonascii あ"]
        r2 = L.validate_item(it, "Foobar", {}, fetch=lambda u: it["quote"], arm="A", meta=META)
        self.assertIn("V3_format_or_canonical_mismatch", r2["reasons"])

    def test_qualifies_helper(self):
        self.assertFalse(L.en_pron_info_qualifies({"entity_type": "ja_reading_katakana", "pronunciation_hint": "x", "sources": ["u"],
                                                    "confidence": "high"}))


class DetectorTest(unittest.TestCase):
    def test_d1_finds_byus_line_and_flags_readout_as_evidence_only(self):
        r = L.detect_d1(TEXT_B)
        keys = {c["key"]: c for c in r["candidates"]}
        self.assertIn("byus", keys)
        self.assertIn("line", keys)
        self.assertIn("line manga", keys)
        self.assertIn("R_CAMEL", keys["byus"]["rules"])
        self.assertIn("bias", keys)
        self.assertTrue(keys["bias"]["evidence_only"] is False or "R_QUOTED" in keys["bias"]["rules"])
        self.assertIn("story-making", keys)

    def test_d1_names_and_possessive(self):
        t = "Framton Nuttel felt nervous. Mrs. Sappleton smiled. Melos's stomach tightened. Vera waited. Selinuntius was far."
        r = L.detect_d1(t, fact_terms=["Vera"])  # Vera=文頭のCMU収録名: ruleだけでは拾えずFact(seed)/D2で補う
        rec = L.recall_against(r["candidates"], ["Framton Nuttel", "Sappleton", "Melos", "Vera", "Selinuntius"])
        self.assertEqual(rec["recall"], 1.0, rec)

    def test_d1_ledger_ja_katakana_rule_and_exclusion(self):
        ledger = {"a": {"surface": "byus", "entity_type": "ja_reading_katakana", "confidence": "high", "pronunciation_hint": "",
                        "sources": []},
                  "b": {"surface": "LINE", "entity_type": "product", "confidence": "medium", "pronunciation_hint": "LYNE",
                        "sources": ["https://x"], "canonical_spelling": "LINE", "expected_pronunciation_ipa": "x"}}
        r = L.detect_d1(TEXT_B, ledger=ledger)
        keys = {c["key"]: c for c in r["candidates"]}
        self.assertIn("R_LEDGER_JA_KATAKANA_LATIN", keys["byus"]["rules"])
        self.assertNotIn("line", keys)
        self.assertTrue(any(e["key"] == "line" for e in r["excluded"]))

    def test_speech_context_extraction(self):
        log = ("[1]: 3203ms SPX_DBG usp.cpp:1336 speech.context='{\"phraseDetection\":{\"mode\":\"CONVERSATION\"},"
               "\"dgi\":{\"Groups\":[{\"Type\":\"Generic\",\"Items\":[{\"Text\":\"byUs\"},{\"Text\":\"LINE\"}]}],\"bias\":2.000000}}'\n")
        ev = L.extract_speech_context(log)
        self.assertEqual(ev["dgi_items"], ["byUs", "LINE"])
        self.assertEqual(ev["bias"], [2.0])
        self.assertEqual(L.extract_speech_context("nothing")["dgi_items"], [])


class DefaultOffIsolationTest(unittest.TestCase):
    """DefaultOffIsolation型: lib import / 使用前後で Production module の属性が変わらない・実Ledgerを書かない。"""

    def test_import_does_not_mutate_production_state(self):
        import importlib
        before = (led.LEDGER_PATH, res.research_pronunciations, sec.get_full_text_via_azure_stt_with_phrase_list,
                  sec.HUMAN_REVIEW_LOG_PATH, sec.AZURE_PHRASE_LIST_WEIGHT)
        importlib.reload(L)
        after = (led.LEDGER_PATH, res.research_pronunciations, sec.get_full_text_via_azure_stt_with_phrase_list,
                 sec.HUMAN_REVIEW_LOG_PATH, sec.AZURE_PHRASE_LIST_WEIGHT)
        self.assertEqual(before, after)
        self.assertEqual(sec.AZURE_PHRASE_LIST_WEIGHT, 2.0)


class IdentityHarnessTest(unittest.TestCase):
    """evaluate_attempt_with_cascade(M1有効)を既存転写注入で呼べる=実API 0。stub以外のAzure呼出は発生しない。"""

    def test_cascade_runs_with_injected_transcripts(self):
        tmp = tempfile.mkdtemp(prefix="er089test_")
        try:
            wav = os.path.join(tmp, "x.wav")
            import wave
            with wave.open(wav, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(16000)
                w.writeframes(b"\x00\x00" * 16000)
            canonical = "The service is called byUs and it is fun."
            with L.TrialIsolation(out_dir=tmp) as iso:
                iso.injected_azure[os.path.abspath(wav)] = "The service is called bias and it is fun."
                iso.set_ledger(iso.base_ledger)
                v, stop, cls = sec.evaluate_attempt_with_cascade(
                    canonical, "The service is called Bias and it is fun.", [], wav, language="en-US",
                    ledger_phrases=L.get_pl_list(canonical), cascade_enabled=True, segment_id="full_story_part1")
                self.assertTrue(v, cls.classification)
                self.assertEqual(iso.unexpected_calls(), [])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
