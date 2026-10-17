# -*- coding: utf-8 -*-
"""Family Z SRC D1方式(z_sentence_id_posthoc_v1)の正式Gateのtest(委任_16、ユーザー#109)。API呼出 0。
runner(stage_kp)の初回・再利用(reuse)・--regenerate-stage kp_*・resume・下流共有入力でGateが通ることをmock経路で確認する。"""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest

import er026_family_z_fiction_production_runner_01 as r
import er026_family_z_src_posthoc_01 as srcz

TEXT = ("The ruler smiled and said, “Your friend must stay here. Return late, and he will die in your place.”\n\n"
        "Melos ran on through the night. Rain fell hard all night.\n\n"
        "Melos said. He ran on.\n\n"
        "Melos said. The sun rose.")


def _item(rank, span, sentence, **kw):
    d = {"rank": rank, "source_span": span, "source_sentence": sentence, "display_phrase": span, "used_form": span,
         "japanese_gloss": "x"}
    d.update(kw)
    return d


class ResolveTest(unittest.TestCase):
    def test_unique_resolution_methods(self):
        kp = {"items": [_item(1, "Rain fell hard all night", "Rain fell hard all night."),         # exact
                        _item(2, "ran on through", "Melos ran on through the night. Rain fell hard all night."),  # containment
                        _item(3, "The sun rose", "")]}                                               # unique_span
        rep = srcz.apply_to_kp(kp, TEXT, "a2")
        self.assertEqual(rep["status"], "PASS")
        self.assertEqual([x["resolution_method"] for x in rep["items"]], ["exact", "unique_containment", "unique_span"])
        n = rep["new_items"]
        self.assertTrue(all(i["source_reference_contract"] == srcz.LABEL for i in n))
        self.assertEqual(n[1]["source_sentence"], "Melos ran on through the night")   # 終端句読点は正規化で落ちる(元値はsource_sentence_llm)
        self.assertEqual(n[1]["source_sentence_llm"], "Melos ran on through the night. Rain fell hard all night.")
        self.assertEqual(n[1]["source_span"], "ran on through")                      # spanは保存

    def test_ambiguous_is_not_guessed(self):
        kp = {"items": [_item(1, "Melos said", "Melos said.")]}   # 2箇所に同一文
        rep = srcz.apply_to_kp(kp, TEXT, "a2")
        self.assertEqual(rep["status"], "STOP")
        self.assertEqual(rep["ambiguous"], [1])
        self.assertEqual(rep["new_items"], [])
        self.assertEqual(rep["items"][0]["candidate_sentence_ids"], ["S5", "S7"])    # 勝手に採用箇所を決めない

    def test_unresolved_is_not_guessed(self):
        rep = srcz.apply_to_kp({"items": [_item(1, "never appears", "never appears here.")]}, TEXT, "a2")
        self.assertEqual((rep["status"], rep["unresolved"]), ("STOP", [1]))

    def test_quote_boundary_truncated_telemetry_adopts_span_sentence_only(self):
        kp = {"items": [_item(1, "Return late", "The ruler smiled and said, “Your friend must stay here. Return late, and he will die in your place.”")]}
        rep = srcz.apply_to_kp(kp, TEXT, "a2")
        it = rep["new_items"][0]
        self.assertEqual(it["source_sentence"], "Return late, and he will die in your place")   # spanを含む1文のみ
        self.assertTrue(it["quote_boundary_truncated"])
        self.assertTrue(rep["items"][0]["quote_signals"]["starts_inside_open_quote"])
        self.assertEqual(rep["quote_boundary_truncated_count"], 1)

    def test_normalization_differences_curly_quotes_and_case(self):
        kp = {"items": [_item(1, "Rain fell hard", "“RAIN fell hard all night”")]}
        rep = srcz.apply_to_kp(kp, TEXT, "a2")
        self.assertEqual(rep["items"][0]["resolution_method"], "exact")
        self.assertFalse(rep["new_items"][0]["quote_boundary_truncated"])

    def test_gate_idempotent_and_writes_audit(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        p = os.path.join(d, "keywords_canonicalized.json")
        json.dump({"items": [_item(1, "Rain fell hard all night", "Rain fell hard all night.")], "overall_status": "PASS"},
                  open(p, "w", encoding="utf-8"), ensure_ascii=False)
        srcz.gate(p, TEXT, "a2", d)
        b1 = open(p, "rb").read()
        srcz.gate(p, TEXT, "a2", d)
        self.assertEqual(b1, open(p, "rb").read())
        self.assertTrue(srcz.has_contract(json.load(open(p, encoding="utf-8"))))
        a = json.load(open(os.path.join(d, srcz.AUDIT_REL), encoding="utf-8"))
        self.assertEqual(a["label"], srcz.LABEL)
        self.assertEqual(a["levels"]["a2"]["status"], "PASS")

    def test_gate_stop_leaves_artifact_unchanged_and_audits(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        p = os.path.join(d, "k.json")
        json.dump({"items": [_item(1, "Melos said", "Melos said.")]}, open(p, "w", encoding="utf-8"))
        before = open(p, "rb").read()
        with self.assertRaises(srcz.FamilyZSourceReferenceStop):
            srcz.gate(p, TEXT, "a2", d)
        self.assertEqual(before, open(p, "rb").read())
        self.assertEqual(json.load(open(os.path.join(d, srcz.AUDIT_REL), encoding="utf-8"))["levels"]["a2"]["status"], "STOP")


class RunnerWiringTest(unittest.TestCase):
    """stage_kp(正式runner)の全経路でGateが呼ばれること。monkeypatchで呼出回数を確認する。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.ctx = r.build_mock_context(self.tmp)
        self.calls = []
        orig = r._src_gate

        def spy(ctx, lv, text):
            self.calls.append(lv)
            return orig(ctx, lv, text)
        self._p = unittest.mock.patch.object(r, "_src_gate", spy)
        self._p.start()
        self.addCleanup(self._p.stop)

    def _run(self, stages):
        with contextlib.redirect_stdout(io.StringIO()):
            return r.run_stages(self.ctx, stages)

    def test_all_paths_call_the_same_gate(self):
        pre = ["seed_check", "writer", "std_adjust", "plan", "support", "kp"]
        self._run(pre)
        self.assertEqual(sorted(self.calls), ["a2", "b1b"])                     # 初回
        kp = json.load(open(f"{self.ctx.out_dir}/b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
        self.assertTrue(srcz.has_contract(kp))                                  # installed asset(下流が読む)にも付与
        self.assertTrue(os.path.exists(f"{self.ctx.out_dir}/audit/src_z_posthoc_01.json"))
        self.calls.clear()
        self._run(["kp"])                                                       # resume / provenance reuse
        self.assertEqual(sorted(self.calls), ["a2", "b1b"])
        self.calls.clear()
        self.ctx.regenerate_stage = "kp_a2"                                     # --regenerate-stage kp_a2
        self._run(["kp"])
        self.assertEqual(sorted(self.calls), ["a2", "b1b"])
        self.ctx.regenerate_stage = None

    def test_gate_stop_blocks_install_and_downstream(self):
        pre = ["seed_check", "writer", "std_adjust", "plan", "support"]
        self._run(pre)
        # KP選定結果の出典が本文中に存在しない(不一致)場合: 実Gateが推測補完せずSTOPし、install_kp_assetsへ進まない
        def bad_kp(text, kp_dir, article_id, source_level, process=None, **kw):
            os.makedirs(kp_dir, exist_ok=True)
            span = "this phrase never appears in the story"
            items = [{"rank": i, "source_span": span, "source_sentence": span, "display_phrase": span, "key_phrase": span,
                      "used_form": span, "japanese_gloss": f"g{i}"} for i in range(1, 6)]
            json.dump({"items": items, "overall_status": "CANONICALIZATION_PASS", "article_id": article_id,
                       "canonicalization_version": "mock", "source_level": source_level},
                      open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False)
            return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"}, "canonicalization": {"status": "CANONICALIZATION_PASS"},
                    "redundancy_qa": {"status": "REDUNDANCY_OK"}, "redundancy_retry_log": []}
        self.ctx.hooks["kp_fn"] = bad_kp
        with self.assertRaises(r.FamilyZE2EStop) as cm:
            self._run(["kp"])
        self.assertIn("FAMILY_Z_SRC_UNRESOLVED", str(cm.exception))
        self.assertFalse(os.path.exists(f"{self.ctx.out_dir}/b1b/key_phrases/keywords_canonicalized.json"))   # install前に停止
        a = json.load(open(f"{self.ctx.out_dir}/audit/src_z_posthoc_01.json", encoding="utf-8"))
        self.assertEqual(a["levels"]["b1b"]["status"], "STOP")

    def test_load_level_inputs_rejects_kp_without_contract(self):
        pre = ["seed_check", "writer", "std_adjust", "plan", "support", "kp"]
        self._run(pre)
        r.load_level_inputs(self.ctx, "b1b")   # 付与済み: OK
        p = f"{self.ctx.out_dir}/b1b/key_phrases/keywords_canonicalized.json"
        kp = json.load(open(p, encoding="utf-8"))
        for it in kp["items"]:
            it.pop("source_reference_contract", None)
        json.dump(kp, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        with self.assertRaises(r.FamilyZE2EStop) as cm:
            r.load_level_inputs(self.ctx, "b1b")
        self.assertIn("FAMILY_Z_SRC_CONTRACT_MISSING", str(cm.exception))

    def test_kp_expl_signature_includes_source_sentence(self):
        self._run(["seed_check", "writer", "std_adjust", "plan", "support", "kp"])
        prov = json.load(open(f"{self.ctx.out_dir}/writer/provenance.json", encoding="utf-8"))
        kp = json.load(open(f"{self.ctx.out_dir}/b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
        items = sorted(kp["items"], key=lambda x: x["rank"])
        base = [it["display_phrase"] for it in items]
        has_gloss = any(it.get("gloss_alignment_status") for it in items)
        payload = {"display": base, "gloss": [it.get("japanese_gloss", "") for it in items]} if has_gloss else {"display": base}
        without = r._sha(json.dumps(payload if has_gloss else base, ensure_ascii=False))
        payload["src"] = [[it["source_sentence_id"], it["source_sentence"]] for it in items]
        with_src = r._sha(json.dumps(payload, ensure_ascii=False))
        self.assertNotEqual(without, with_src)
        blob = json.dumps(prov)
        self.assertIn(with_src, blob)       # 記録されたsigはsource_sentenceを含む版
        self.assertNotIn(without, blob)


class PromptAndCandidateSupplyUnchangedTest(unittest.TestCase):
    def test_runner_does_not_reference_x_candidate_id_method(self):
        src = open(r.__file__, encoding="utf-8").read()
        for banned in ("M2P0", "candidate_id_v1", "source_candidate_id", "SUPPORTED_FAMILY_PROFILES"):
            self.assertNotIn(banned, src.split("def _src_gate")[1].split("def stage_kp")[0])
        mod = open(srcz.__file__, encoding="utf-8").read()
        self.assertNotIn("import er030_key_phrase_db_hybrid_source_reference_contract_01", mod)


import unittest.mock  # noqa: E402

if __name__ == "__main__":
    unittest.main()
