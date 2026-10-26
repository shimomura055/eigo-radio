# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01: Family Y Standard(a2)本文のChunk分割(+0.2秒)×6%減速のProduction配線test(API 0・TTS 0・偽TTS)。
ユーザー正式承認2026-10-26(APPROVED_FOR_PRODUCTION: Std/Adv双方、Standard除外は認めない。Yはfamily Xと同じ段落境界方式。文境界分割/本文契約変更は承認していない)。
実行: PYTHONPATH=netblock_harness_01 .venv/Scripts/python.exe -m pytest er121_family_y_std_chunk_test_01.py -q

重要: 実Y記事は各Voice 1段落のため分割0(不発火=正常)。本testは『複数段落の入力に対して正式経路が発火する』ことを示す(合成入力。公開物には触れない)。
"""
from __future__ import annotations

import contextlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from er121_family_y_runner_01_test_01 import setUpModule, tearDownModule, BLOCK, _ctx, _declare, _quiet  # noqa: E402,F401  (遮断harnessを共有)
import er003_v1_n3_01_assemble as asm  # noqa: E402
import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_mock_01 as mk  # noqa: E402
import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402
import er117_chunk_tts_production_01 as chunk_tts  # noqa: E402

V2 = ("I wait all morning for the bell to ring, but the van never comes at that hour.\n\n"
      "When it finally comes, I am already late for work and I cannot open the door in time.")
CLOSING3 = ("Maybe the fee is only one small lever in a much larger system.\n\n"
            "Who decides when a parcel arrives, and who can really change that choice?\n\n"
            "What would you want from the service if you were the one waiting?")


class BaseStd(unittest.TestCase):
    base_root = None
    base_ctx = None

    @classmethod
    def setUpClass(cls):
        cls.base_root = tempfile.mkdtemp(prefix="y_stdchunk_base_")
        cls.base_ctx = _ctx(cls.base_root)
        with _quiet():
            r.run_stages(cls.base_ctx, ["seed_check", "text", "translate", "support"])
            _declare(cls.base_ctx)
            r.run_stages(cls.base_ctx, ["kp", "tts_a2"])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base_root, ignore_errors=True)

    def setUp(self):
        self.work = tempfile.mkdtemp(prefix="y_stdchunk_work_")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.out = os.path.join(self.work, "run")
        shutil.copytree(self.base_ctx.out_dir, self.out)
        self.a2 = f"{self.out}/a2"

    @staticmethod
    def rj(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def wj(p, d):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    def multi_para_parts(self):
        pj = f"{self.a2}/parts.json"
        parts = self.rj(pj)
        parts["segments"]["y_voice_2"] = V2
        parts["segments"]["y_closing"] = CLOSING3
        self.wj(pj, parts)
        for p in (f"{self.a2}/audit/tts_generation_results.json", f"{self.a2}/audit/chunk_plan_a2.json"):
            if os.path.exists(p):
                os.remove(p)
        for sid in ys.Y_SEGMENT_IDS:
            w = f"{self.a2}/narration/{sid}.wav"
            if os.path.exists(w):
                os.remove(w)
        return parts

    def api(self):
        return mk.MockApi(self.out)

    def generate(self, api=None, slow_fn=None):
        api = api or self.api()
        stack = contextlib.ExitStack()
        stack.enter_context(mk.fake_tts(api))
        if slow_fn is not None:
            stack.enter_context(mock.patch.object(ya.n3_tts, "generate_a2_segment_with_slowdown", side_effect=slow_fn))
        with stack, _quiet():
            return ya.generate_y_a2_segments(self.out, "日本語タイトル", style_profile=r.STYLE_PROFILE), api

    def results(self):
        return self.rj(f"{self.a2}/audit/tts_generation_results.json")

    def save_results(self, d):
        self.wj(f"{self.a2}/audit/tts_generation_results.json", d)

    def article_text(self):
        with open(r._level_text_path(self.base_ctx, "a2").replace(self.base_ctx.out_dir, self.out), encoding="utf-8") as f:
            return ys.canonical_body(f.read())

    def assemble(self):
        with mk.fake_tts(self.api()), _quiet():
            return ya.assemble_level(self.out, "a2", style_profile=r.STYLE_PROFILE, slug="mock_slug", article_text=self.article_text())

    def api_lines(self):
        with open(f"{self.out}/mock_api_calls.jsonl", encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]


class TestStdScopeAndPlan(BaseStd):
    def test_std_is_in_scope_and_real_single_paragraph_article_is_not_chunked(self):
        self.assertEqual(ys.CHUNK_TTS_Y_LEVELS, ("b1b", "a2"))                          # Std対象外は認めない(2026-10-26)
        plans = ya._record_chunk_decision(self.a2, "a2")
        self.assertEqual(list(plans), list(ys.Y_SEGMENT_IDS))
        self.assertTrue(all(p["chunked"] is False for p in plans.values()))            # 実Y記事=各Voice 1段落: 不発火(正常。配線漏れではない)
        dec = self.rj(f"{self.a2}/audit/chunk_tts_decision.json")
        self.assertTrue(dec["chunk_tts_applicable"] and dec["chunk_tts_applied_at_this_level"] is True)
        self.assertEqual(dec["std_slowdown_composition"], "per_chunk_slowdown_then_pad_0.2s")
        self.assertTrue(all(sg["chunked"] is False and sg["paragraphs"] == 1 for sg in dec["segments"].values()))
        self.assertNotIn("not_applied_reason", dec)

    def test_only_segments_k_is_accepted_for_std_and_rejected_for_unknown_level(self):
        sel, err = ya.validate_only_segments("y_voice_2,y_voice_2_k1", "a2")
        self.assertIsNone(err)
        self.assertEqual(sel, {"y_voice_2", "y_voice_2_k1"})
        sel, err = ya.validate_only_segments("y_voice_2_k1", "both")
        self.assertIsNone(sel)

    def test_single_paragraph_std_generation_is_unchanged_one_call_per_segment(self):
        summary, api = self.generate()
        segs = self.results()["segments"]
        self.assertTrue(all(not ys.parse_y_chunk_id(k) for k in segs))
        self.assertTrue(all(segs[s]["slowdown_applied"] is True for s in ys.Y_SEGMENT_IDS))
        self.assertFalse(os.path.exists(f"{self.a2}/audit/chunk_tts_evidence_a2.json"))
        self.assertEqual(ya.check_std_slowdown(self.results(), ya.plan_y_chunks(self.rj(f"{self.a2}/parts.json"))), [])


class TestStdChunkGeneration(BaseStd):
    def test_multi_paragraph_input_fires_the_formal_path_per_chunk_with_slowdown(self):
        self.multi_para_parts()
        n_before = len(self.api_lines())                                                  # 基底run(1段落)のAPI記録は除く
        summary, api = self.generate()
        segs = self.results()["segments"]
        vm = ya.segment_voice_map()
        for cid in ("y_voice_2_k1", "y_voice_2_k2", "y_closing_k1", "y_closing_k2", "y_closing_k3"):
            e = segs[cid]
            self.assertEqual(e["status"], "OK", cid)
            self.assertIs(e["slowdown_applied"], True, cid)                             # chunkごとに既存の6%減速
            self.assertEqual(e["chunk_tts"]["level"], "a2")
            self.assertEqual(e["y_tts_voice_requested"], vm[ys.parse_y_chunk_id(cid)[0]], cid)
        for pid in ("y_voice_2", "y_closing"):
            p = segs[pid]
            self.assertEqual(p["status"], "OK")
            self.assertIs(p["slowdown_applied"], True)                                  # 親=全chunk減速済みの集約
            self.assertEqual(p["chunk_tts"]["extra_pause_seconds"], 0.2)
        self.assertNotIn("chunk_tts", segs["y_voice_1"])                                # 1段落segmentは従来の1 call
        self.assertIs(segs["y_voice_1"]["slowdown_applied"], True)
        calls = [c["label"] for c in self.api_lines()[n_before:] if c["kind"] == "tts" and c["label"].startswith("y_")]
        self.assertIn("y_voice_2_k1.wav", calls)
        self.assertIn("y_closing_k3.wav", calls)
        self.assertNotIn("y_voice_2.wav", calls)                                        # 親は生成しない(chunkの生連結)
        nd = f"{self.a2}/narration"
        pcm = [chunk_tts.read_pcm16(f"{nd}/y_voice_2_k{i}.wav") for i in (1, 2)]       # chunk wav=減速後(1.06倍)
        orig = [chunk_tts.read_pcm16(f"{nd}/y_voice_2_k{i}_original.wav") for i in (1, 2)]
        for a, b in zip(pcm, orig):
            self.assertAlmostEqual(len(a) / len(b), 1.06, places=2)
        parent = chunk_tts.read_pcm16(f"{nd}/y_voice_2.wav")
        self.assertEqual(len(parent), len(pcm[0]) + len(pcm[1]) + 4800)                # ポーズは減速されない: ちょうど0.2秒
        self.assertTrue((parent[len(pcm[0]):len(pcm[0]) + 4800] == 0).all())
        ev = self.rj(f"{self.a2}/audit/chunk_tts_evidence_a2.json")
        self.assertEqual(sorted(ev["parents"]), ["y_closing", "y_voice_2"])
        self.assertTrue(all(r_["slowdown_applied"] is True for r_ in ev["parents"]["y_closing"]["chunks"]))
        dec = self.rj(f"{self.a2}/audit/chunk_tts_decision.json")
        self.assertEqual(dec["segments"]["y_voice_2"]["paragraphs"], 2)
        self.assertEqual(dec["segments"]["y_closing"]["chunk_ids"], ["y_closing_k1", "y_closing_k2", "y_closing_k3"])

    def test_adv_decision_file_and_adv_chunk_paths_untouched_by_std_run(self):
        self.multi_para_parts()
        self.generate()
        self.assertFalse(os.path.exists(f"{self.a2}/audit/chunk_tts_evidence_b1b.json"))
        self.assertTrue(os.path.exists(f"{self.a2}/audit/chunk_plan_a2.json"))

    def test_gate_checks_every_chunk_and_assembly_has_exact_0_2s_gaps(self):
        self.multi_para_parts()
        self.generate()
        gate = ya.y_style_gate(self.out, "a2", r.STYLE_PROFILE)
        self.assertEqual(gate["status"], "PASS", gate)
        names = [x["segment"] for x in gate["y_body_checks"]]
        self.assertIn("y_voice_2_k2", names)
        self.assertNotIn("y_voice_2", names)
        s = self.assemble()
        self.assertEqual(s["status"], "OK", s)
        ct = s["chunk_tts"]
        self.assertEqual((ct["level"], ct["composition"]), ("a2", "per_chunk_slowdown_then_pad_0.2s"))
        for sid, n in (("y_voice_2", 2), ("y_closing", 3)):
            p = ct["parents"][sid]
            self.assertEqual(len(p["gap_offsets_in_segment_s"]), n - 1)
            for a, b in p["gap_offsets_in_segment_s"]:
                self.assertAlmostEqual(b - a, 0.2, places=3)
        self.assertTrue(os.path.exists(f"{self.a2}/audit/chunk_tts_assembly_a2.json"))
        self.assertFalse(os.path.exists(f"{self.a2}/audit/chunk_tts_assembly_b1b.json"))

    def test_chunk_missing_slowdown_is_blocked_by_y_gate_even_though_the_parent_says_nothing(self):
        self.multi_para_parts()
        self.generate()
        res = self.results()
        del res["segments"]["y_closing_k2"]["slowdown_applied"]                          # chunk2だけ減速証跡なし
        self.save_results(res)
        g = ya.y_style_gate(self.out, "a2", r.STYLE_PROFILE)
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn(("y_closing_k2", "STD_CHUNK_MISSING_MANDATORY_A2_SLOWDOWN"),
                      [(x["segment"], v) for x in g["y_body_blocked"] for v in x["violations"]])
        s = ya.assemble_level(self.out, "a2", style_profile=r.STYLE_PROFILE, slug="mock_slug", article_text=self.article_text())
        self.assertEqual(s["status"], "BLOCKED_STYLE_PROFILE_GATE")                       # 組み立てない(回避しない)
        res = self.results()                                                              # assembleの入口で親が再構築され、減速集約はFalse
        self.assertIs(res["segments"]["y_closing"]["slowdown_applied"], False)

    def test_failed_std_chunk_makes_parent_not_all_validated_and_blocks_assembly(self):
        self.multi_para_parts()
        self.generate()
        res = self.results()
        res["segments"]["y_closing_k2"]["status"] = "STOPPED"
        self.save_results(res)
        with self.assertRaises(RuntimeError) as e:
            self.assemble()
        self.assertIn("EPISODE_BLOCKED_BY_AUDIO_VALIDATION", str(e.exception))
        self.assertEqual(self.results()["segments"]["y_closing"]["status"], chunk_tts.PARENT_STATUS_NOT_ALL_VALIDATED)

    def test_resume_reuses_ok_chunks_and_regenerates_chunks_without_slowdown_evidence(self):
        self.multi_para_parts()
        self.generate()
        before = len(self.api_lines())
        self.generate()
        added = [c["label"] for c in self.api_lines()[before:] if c["kind"] == "tts" and c["label"].startswith("y_")]
        self.assertEqual(added, [])                                                       # OK chunkは再利用(再課金なし)
        res = self.results()
        del res["segments"]["y_voice_2_k1"]["slowdown_applied"]
        self.save_results(res)
        before = len(self.api_lines())
        self.generate()
        added = [c["label"] for c in self.api_lines()[before:] if c["kind"] == "tts" and c["label"].startswith("y_")]
        self.assertEqual(added, ["y_voice_2_k1.wav"])                                     # 証跡なしchunkだけ再生成
        self.assertIs(self.results()["segments"]["y_voice_2_k1"]["slowdown_applied"], True)

    def test_replan_guard_and_scope_revert_fail_closed_before_billing(self):
        self.multi_para_parts()
        self.generate()
        p = f"{self.a2}/audit/chunk_plan_a2.json"
        d = self.rj(p)
        d["plans"]["y_voice_2"]["chunks"][0]["text"] += " tampered"
        self.wj(p, d)
        api = self.api()
        with self.assertRaises(ya.YAudioStop) as e:
            self.generate(api=api)
        self.assertIn("FAMILY_Y_CHUNK_PLAN_RECONCILE", str(e.exception))
        with mock.patch.dict(ys.CHUNK_TTS_SCOPE, {"Y": False}):
            with self.assertRaises(ya.YAudioStop):
                ya._record_chunk_decision(self.a2, "a2")

    def test_tampered_chunk_audio_stops_std_assembly(self):
        self.multi_para_parts()
        self.generate()
        w = f"{self.a2}/narration/y_voice_2_k1.wav"
        pcm = chunk_tts.read_pcm16(w)
        chunk_tts.write_pcm16(w, pcm[: len(pcm) // 2])
        with self.assertRaises(Exception) as e:
            self.assemble()
        self.assertTrue("FAMILY_Y_CHUNK_INTEGRITY" in str(e.exception) or "ASSET_HASH_MISMATCH" in str(e.exception), str(e.exception)[:300])

    def test_check_std_slowdown_without_plans_is_the_legacy_parent_check(self):
        res = {"segments": {sid: {"slowdown_applied": True} for sid in ys.Y_SEGMENT_IDS}}
        self.assertEqual(ya.check_std_slowdown(res), [])
        res["segments"]["y_lead"]["slowdown_applied"] = False
        self.assertEqual([b["segment"] for b in ya.check_std_slowdown(res)], ["y_lead"])


class TestIsolationStd(unittest.TestCase):
    def test_no_network_or_real_client_attempts(self):
        self.assertEqual((BLOCK["net"], BLOCK["client"]), (0, 0))

    def test_y_std_uses_shared_er117_and_existing_slowdown_function_not_a_reimplementation(self):
        with open(os.path.join(ROOT, "er121_family_y_audio_01.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("n3_tts.generate_a2_segment_with_slowdown(", src)
        self.assertIn("chunk_tts.std_chunk_slowdown_violations", src)
        self.assertNotRegex(src, r"atempo")                                         # 減速処理を再実装していない(既存関数を呼ぶだけ。ページ用の既存呼出は対象外)
        self.assertNotRegex(src, r"import er110_|import er114_|import er113_|plan_z_clip|plan_z_level")


if __name__ == "__main__":
    unittest.main()
