# -*- coding: utf-8 -*-
"""RISK-FLAGGER-PRODUCTION-WIRING-01 委任_12: Opus条件Cレビュー是正(F1〜F8)のtest。API呼び出し0、費用0円。
実行: .venv/Scripts/python.exe -m pytest er053_c5_review_fixes_test_01.py -q
"""
from __future__ import annotations

import inspect
import json
import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import er019_family_x_audio_production_runner_01 as audio
import er019_family_x_entertainment_production_runner_01 as runner
import er053_b3_annotation_contract_01 as contract
import er053_b3_deterministic_producer_01 as prod
import er053_dev_b3_fixture_adapter_01 as ad
import er053_family_x_factlock_ja_writer_01 as w1
import er053_review_queue_01 as rq

HERE = os.path.dirname(os.path.abspath(__file__))
E9 = os.path.join(HERE, "er052_output", "b3_rootfix_trial_02", "e9")
E9_THEMES = ("semiconductor_earnings", "small_bag", "space_weapons", "hormuz", "central_bank_mortgage", "byd_recall")


def make_out(slug="central_bank_mortgage", producer=True):
    d = tempfile.mkdtemp(prefix="c5_fix_")
    ad.copy_inputs(slug, d)
    if producer:
        prod.produce_annotated_b3(d)
    return d


class F1ArticleId(unittest.TestCase):
    def test_slug_and_run_both_in_id_and_no_collision(self):
        a = rq.derive_article_id("er019_output/semiconductor_earnings/run_01")
        b = rq.derive_article_id("er019_output/byd_recall/run_01")
        self.assertEqual(a, "semiconductor_earnings__run_01")
        self.assertNotEqual(a, b)

    def test_writer_and_audio_use_the_same_function(self):
        self.assertIn("rq.derive_article_id(out_dir)", inspect.getsource(runner.run_post_en_risk_flag))
        self.assertIn("rq.derive_article_id(source_dir)", inspect.getsource(audio.ensure_rf_record))
        self.assertEqual(rq.derive_article_id("er019_output/x/run_9/"), rq.derive_article_id(os.path.abspath("er019_output/x/run_9")))


class F2EvidenceImmutable(unittest.TestCase):
    def test_original_field_untouched_and_manifest_sha_idempotent(self):
        d = make_out(producer=False)
        evp = os.path.join(d, "storyline_b3", "fact_selection_evidence.json")
        orig = json.load(open(evp, encoding="utf-8"))
        r1 = prod.produce_annotated_b3(d)
        ev1 = json.load(open(evp, encoding="utf-8"))
        self.assertEqual(ev1["selected_fact_brief_text"], orig["selected_fact_brief_text"])
        self.assertNotIn("b3_llm_selected_fact_brief_text", ev1)
        self.assertIn("deterministic_selected_fact_brief_text", ev1)
        r2 = prod.produce_annotated_b3(d)
        self.assertEqual(r1["input_shas"]["fact_selection_evidence_json"], r2["input_shas"]["fact_selection_evidence_json"])
        self.assertEqual(r1["manifest"]["annotated_md_sha256"], r2["manifest"]["annotated_md_sha256"])
        self.assertEqual(json.load(open(evp, encoding="utf-8")), ev1)
        shutil.rmtree(d, ignore_errors=True)

    def test_new_path_does_not_read_selected_fact_brief_text(self):
        src = open(os.path.join(HERE, "er053_family_x_factlock_ja_writer_01.py"), encoding="utf-8").read()
        self.assertNotIn('["selected_fact_brief_text"]', src)
        self.assertNotIn("fact_selection_evidence.json", src)


class F3StorylineStrip(unittest.TestCase):
    def test_whitespace_difference_is_ok_but_content_difference_is_not(self):
        d = make_out(producer=False)
        evp = os.path.join(d, "storyline_b3", "fact_selection_evidence.json")
        ev = json.load(open(evp, encoding="utf-8"))
        ev["selected_storyline"] = "  " + ev["selected_storyline"] + "\n"
        json.dump(ev, open(evp, "w", encoding="utf-8"), ensure_ascii=False)
        prod.produce_annotated_b3(d)
        ev["selected_storyline"] = ev["selected_storyline"].strip() + "x"
        json.dump(ev, open(evp, "w", encoding="utf-8"), ensure_ascii=False)
        with self.assertRaises(prod.AnnotationProducerError):
            prod.produce_annotated_b3(d)
        shutil.rmtree(d, ignore_errors=True)


class FakeResp:
    def __init__(self, text, model, rid):
        self.output_text, self.model, self.id = text, model, rid
        self.usage = SimpleNamespace(input_tokens=1, output_tokens=1)


class FakeClient:
    def __init__(self, scripts):
        self.scripts, self.calls = list(scripts), []
        self.responses = self

    def create(self, **kw):
        self.calls.append(kw)
        t, m = self.scripts.pop(0)
        return FakeResp(t, m, "r%d" % len(self.calls))


R0 = "メタの話\n人間が電話をしたというテストがありました。【事実1】\nこれは面白いですね。\n"


class F4F6W1(unittest.TestCase):
    def setUp(self):
        self.out = make_out()
        s = mock.patch.object(w1.time, "sleep", lambda x: None)
        s.start()
        self.addCleanup(s.stop)
        self.addCleanup(shutil.rmtree, self.out, True)

    def test_f4_r0_returned_model_mismatch_stops_as_provenance(self):
        c = FakeClient([(R0, "gpt-5-other")])
        with self.assertRaises(w1.ProvenanceViolation):
            w1.run_w1_writer(self.out, client=c)
        self.assertEqual(len(c.calls), 1)
        self.assertFalse(os.path.exists(os.path.join(self.out, "ja_writer", "revision2.md")))

    def test_f6_runtime_evidence_written_before_revision2(self):
        order = []
        real = w1.wt

        def spy(p, text):
            order.append(os.path.basename(p))
            return real(p, text)
        with mock.patch.object(w1, "wt", spy):
            w1.run_w1_writer(self.out, client=FakeClient([(R0, "gpt-6-luna"), ("# T\n本文です。", "gpt-6-astra"), ("# T2\n本文2です。", "gpt-6-astra")]))
        self.assertLess(order.index("runtime_evidence.json"), order.index("revision2.md"))
        self.assertEqual(order[-1], "revision2.md")


class F5GoldenR0Prompt(unittest.TestCase):
    def test_build_r0_prompt_equals_rootfix02_e9_r0_prompt_txt_6_themes(self):
        for th in E9_THEMES:
            d = make_out(th)
            try:
                a = contract.validate_annotated_b3(d)
                storyline, _ = w1.parse_brief_md(a.annotated_md_text)
                with open(os.path.join(E9, th, "Ddetv2", "r0_prompt.txt"), encoding="utf-8") as f:
                    golden = f.read()
                self.assertEqual(w1.build_r0_prompt(storyline, a.news_field_text), golden, th)
            finally:
                shutil.rmtree(d, ignore_errors=True)


class F7Message(unittest.TestCase):
    def test_provenance_mismatch_message_tells_to_regenerate_writer(self):
        d = make_out()
        try:
            os.makedirs(os.path.join(d, "ja_writer"))
            open(os.path.join(d, "ja_writer", "revision2.md"), "w", encoding="utf-8").write("x")
            json.dump({"chain_method": "W-1", "annotated_md_sha256": "0" * 64}, open(os.path.join(d, "ja_writer", "runtime_evidence.json"), "w"))
            with self.assertRaises(runner.LegacyWriterProvenanceStop) as cm:
                runner.load_reused_ja_text(d)
            self.assertIn("PROVENANCE_MISMATCH", str(cm.exception))
            self.assertIn("--regenerate-stage writer", str(cm.exception))
        finally:
            shutil.rmtree(d, ignore_errors=True)


class F8Annotator(unittest.TestCase):
    def test_production_accepts_only_deterministic(self):
        self.assertEqual(contract.ANNOTATORS, ("DETERMINISTIC",))
        d = make_out()
        try:
            p = os.path.join(d, "storyline_b3", "annotation.json")
            sc = json.load(open(p, encoding="utf-8"))
            for bad in ("A", "B", "MERGED"):
                sc["annotator"] = bad
                json.dump(sc, open(p, "w", encoding="utf-8"), ensure_ascii=False)
                with self.assertRaises(Exception):
                    contract.validate_annotated_b3(d)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
