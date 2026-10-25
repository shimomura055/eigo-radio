# -*- coding: utf-8 -*-
"""FAMILY-Y-PRODUCTION-LAUNCH-01 委任_04: Family Y の Chunk TTS(X方式=段落単位chunk+0.2秒ポーズ。ユーザー正式決定2026-10-25 USER_02 ①)のtest。

API 0・実client生成block・network遮断(runner testと同じharness)。偽TTSは er121_family_y_mock_01.fake_tts。
検査: 段落分割がsegment境界(話者切替)をまたがない / 0.2秒ポーズ / chunkごとのVoice / Chunk Gate(親集約 CHUNKS_NOT_ALL_VALIDATED・chunk単位Style検査) /
      整合検査(欠落・改ざん) / resume再利用 / Std非chunk / role未解決はSTOP(課金前) / X方式の共通module(er117)を再実装していないこと。
注: Yのchunk idをFULL_STORYへ解決するのは共通er020(委任_04の要求事項=未反映)。test内では resolve_narrative_role に同等の解決を足したpatchを当てて
    『要求どおりer020が更新された後の挙動』を検証し、未更新のままだと課金前にSTOPすること(fail-closed)も別testで固定する。
"""
from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from er121_family_y_runner_01_test_01 import setUpModule, tearDownModule, BLOCK, _ctx, _declare, _quiet  # noqa: E402,F401  (遮断harnessを共有)
import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_mock_01 as mk  # noqa: E402
import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402
import er117_chunk_tts_production_01 as chunk_tts  # noqa: E402
import er020_tts_retry_local_rewrite_01 as retry_primitive  # noqa: E402
import er019_family_x_audio_production_runner_01 as xr  # noqa: E402

V2 = ("I wait all morning for the bell to ring, but the van never comes at that hour.\n\n"
      "When it finally comes, I am already late for work and I cannot open the door in time.")
CLOSING3 = ("Maybe the fee is only one small lever in a much larger system.\n\n"
            "Who decides when a parcel arrives, and who can really change that choice?\n\n"
            "What would you want from the service if you were the one waiting?")

_ORIG_RESOLVE = retry_primitive.resolve_narrative_role


def _resolve_with_y_chunks(segment_id):
    """要求(共通er020の_FAMILY_Y_SEGMENT_PATTERNへ chunk接尾辞を追加)と同等の解決。"""
    if ys.parse_y_chunk_id(segment_id or ""):
        return "FULL_STORY"
    return _ORIG_RESOLVE(segment_id)


def _patch_resolve():
    return mock.patch.object(retry_primitive, "resolve_narrative_role", _resolve_with_y_chunks)


def _have_er020_y_chunk_support() -> bool:
    return _ORIG_RESOLVE("y_voice_2_k1") == "FULL_STORY"


class Base(unittest.TestCase):
    base_root = None
    base_ctx = None

    @classmethod
    def setUpClass(cls):
        cls.base_root = tempfile.mkdtemp(prefix="y_chunk_base_")
        cls.base_ctx = _ctx(cls.base_root)
        with _quiet():
            r.run_stages(cls.base_ctx, ["seed_check", "text", "translate", "support"])
            _declare(cls.base_ctx)
            r.run_stages(cls.base_ctx, ["kp", "tts_b1b"])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base_root, ignore_errors=True)

    def setUp(self):
        self.work = tempfile.mkdtemp(prefix="y_chunk_work_")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.out = os.path.join(self.work, "run")
        shutil.copytree(self.base_ctx.out_dir, self.out)
        self.b1 = f"{self.out}/b1b"

    # ---- helpers ----
    @staticmethod
    def rj(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def wj(p, d):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    def multi_para_parts(self):
        pj = f"{self.b1}/parts.json"
        parts = self.rj(pj)
        parts["segments"]["y_voice_2"] = V2
        parts["segments"]["y_closing"] = CLOSING3
        self.wj(pj, parts)
        # 旧(1段落)の生成結果は捨てて、複数段落本文でTTS段をやり直す
        for p in (f"{self.b1}/audit/tts_generation_results.json", f"{self.b1}/audit/chunk_plan_b1b.json"):
            if os.path.exists(p):
                os.remove(p)
        for sid in ys.Y_SEGMENT_IDS:
            w = f"{self.b1}/narration/{sid}.wav"
            if os.path.exists(w):
                os.remove(w)
        return parts

    def api(self):
        return mk.MockApi(self.out)

    def generate(self, api=None, patch_role=True):
        api = api or self.api()
        stack = contextlib.ExitStack()
        stack.enter_context(mk.fake_tts(api))
        if patch_role:
            stack.enter_context(_patch_resolve())
        with stack, _quiet():
            return ya.generate_y_b1_segments(self.out, style_profile=r.STYLE_PROFILE), api

    def results(self):
        return self.rj(f"{self.b1}/audit/tts_generation_results.json")

    def save_results(self, d):
        self.wj(f"{self.b1}/audit/tts_generation_results.json", d)

    def article_text(self):
        with open(r._level_text_path(self.base_ctx, "b1b").replace(self.base_ctx.out_dir, self.out), encoding="utf-8") as f:
            return ys.canonical_body(f.read())

    def assemble(self):
        with mk.fake_tts(self.api()), _quiet():
            return ya.assemble_level(self.out, "b1b", style_profile=r.STYLE_PROFILE, slug="mock_slug", article_text=self.article_text())


class TestPlan(Base):
    def test_single_paragraph_segments_are_not_chunked(self):
        parts = self.rj(f"{self.b1}/parts.json")
        plans = ya.plan_y_chunks(parts)
        self.assertEqual(list(plans), list(ys.Y_SEGMENT_IDS))
        self.assertTrue(all(p["chunked"] is False for p in plans.values()), "Y本文は1段落契約=X規則どおり従来の1 call")

    def test_split_only_inside_a_segment_never_across_speaker_switch(self):
        parts = self.multi_para_parts()
        plans = ya.plan_y_chunks(parts)
        self.assertEqual([c["chunk_id"] for c in plans["y_voice_2"]["chunks"]], ["y_voice_2_k1", "y_voice_2_k2"])
        self.assertEqual([c["chunk_id"] for c in plans["y_closing"]["chunks"]], ["y_closing_k1", "y_closing_k2", "y_closing_k3"])
        for sid in ys.Y_SEGMENT_IDS:
            if plans[sid]["chunked"]:
                for c in plans[sid]["chunks"]:
                    self.assertEqual(ys.parse_y_chunk_id(c["chunk_id"])[0], sid)      # chunkは自segmentの内側のみ
                self.assertEqual(" ".join(c["text"] for c in plans[sid]["chunks"]), re.sub(r"\n\s*\n", " ", parts["segments"][sid]))   # 欠落/重複/順序なし
        self.assertFalse(plans["y_intro_2"]["chunked"] or plans["y_intro_3"]["chunked"] or plans["y_voice_1"]["chunked"] or plans["y_voice_3"]["chunked"])
        # 話者切替境界(intro→voice, voice→次のintro)は別segment=別chunk集合。隣接segmentのtextが同じchunkに入ることはない
        texts = [c["text"] for pl in plans.values() for c in pl["chunks"]]
        self.assertEqual(len(texts), len(set(texts)))

    def test_planner_is_the_shared_x_planner(self):
        parts = self.multi_para_parts()
        direct = chunk_tts.plan_x_part(parts["segments"]["y_voice_2"], "y_voice_2")
        got = ya.plan_y_chunks(parts)["y_voice_2"]
        self.assertEqual([(c["chunk_id"], c["text"], c["words"], c["boundary_kind"]) for c in got["chunks"]],
                         [(c["chunk_id"], c["text"], c["words"], c["boundary_kind"]) for c in direct["chunks"]])
        self.assertEqual(got["planner_version"], chunk_tts.CHUNK_PLANNER_VERSION)
        self.assertEqual(chunk_tts.EXTRA_PAUSE_SECONDS, 0.2)
        self.assertTrue(all(c["boundary_kind"] == "paragraph" for c in got["chunks"]))        # Zのsentence境界(B_r1)ではない

    def test_a2_is_not_chunked_and_chunk_only_segments_rejected(self):
        os.makedirs(f"{self.out}/a2/audit", exist_ok=True)
        plans = ya._record_chunk_decision(f"{self.out}/a2", "a2")
        self.assertEqual(plans, {})
        dec = self.rj(f"{self.out}/a2/audit/chunk_tts_decision.json")
        self.assertTrue(dec["chunk_tts_applicable"] and dec["chunk_tts_applied_at_this_level"] is False)
        sel, err = ya.validate_only_segments("y_voice_2_k1", "a2")
        self.assertIsNone(sel)
        self.assertIn("b1b", err)
        sel, err = ya.validate_only_segments("y_voice_2,y_voice_2_k1", "b1b")
        self.assertIsNone(err)
        self.assertEqual(sel, {"y_voice_2", "y_voice_2_k1"})

    def test_only_segments_expands_to_chunk_ids_and_restores(self):
        plans = ya.plan_y_chunks(self.multi_para_parts())
        with ya.only_segments_scope({"y_voice_2"}):
            with ya._only_includes_chunks(plans):
                self.assertEqual(xr._ONLY_SEGMENTS, {"y_voice_2", "y_voice_2_k1", "y_voice_2_k2"})
                self.assertIsNone(xr._only_segments_skip("y_voice_2_k1"))
                self.assertIsNotNone(xr._only_segments_skip("y_closing_k1"))
            self.assertEqual(xr._ONLY_SEGMENTS, {"y_voice_2"})
        self.assertIsNone(xr._ONLY_SEGMENTS)


class TestGenerateAndAssemble(Base):
    def test_role_unresolved_stops_before_any_tts_call(self):
        """共通er020が未更新(Y chunk idがFULL_STORYへ解決されない)なら、課金前にSTOP。更新後はこのtestはskip(別testが正常系を固定)。"""
        if _have_er020_y_chunk_support():
            self.skipTest("er020がY chunk idを解決済み")
        self.multi_para_parts()
        api = self.api()
        with mk.fake_tts(api), _quiet():
            with self.assertRaises(ya.YAudioStop) as e:
                ya.generate_y_b1_segments(self.out, style_profile=r.STYLE_PROFILE)
        self.assertIn("FAMILY_Y_CHUNK_ID_ROLE_UNRESOLVED", str(e.exception))
        self.assertEqual(api.n, 0)                                                  # 共有narration含め1回も生成していない

    def test_generate_chunks_with_voice_per_segment_and_parent_aggregate(self):
        self.multi_para_parts()
        summary, api = self.generate()
        res = self.results()
        segs = res["segments"]
        vm = ya.segment_voice_map()
        for cid in ("y_voice_2_k1", "y_voice_2_k2", "y_closing_k1", "y_closing_k2", "y_closing_k3"):
            e = segs[cid]
            self.assertEqual(e["status"], "OK", cid)
            self.assertEqual(e["y_tts_voice_requested"], vm[ys.parse_y_chunk_id(cid)[0]], cid)       # voice_2=Zephyr / closing=ナレーター
            self.assertEqual(e["chunk_tts"]["parent_id"], ys.parse_y_chunk_id(cid)[0])
        self.assertEqual(segs["y_voice_2_k1"]["y_tts_voice_requested"], "Zephyr")
        for pid in ("y_voice_2", "y_closing"):
            p = segs[pid]
            self.assertEqual(p["status"], "OK")
            self.assertEqual(p["chunk_tts"]["chunk_ids"], [f"{pid}_k{i}" for i in range(1, len(p["chunk_tts"]["chunk_ids"]) + 1)])
            self.assertEqual(p["y_tts_voice_requested"], vm[pid])
            self.assertEqual(p["chunk_tts"]["extra_pause_seconds"], 0.2)
        self.assertNotIn("chunk_tts", segs["y_voice_1"])                             # 1段落segmentは従来の1 call
        self.assertEqual(sum(1 for k in segs if k.startswith("y_") and ys.parse_y_chunk_id(k)), 5)
        # 親wav == chunk wavの生連結(0.2秒=4800サンプル/24kHz)
        nd = f"{self.b1}/narration"
        pcm = [chunk_tts.read_pcm16(f"{nd}/y_voice_2_k{i}.wav") for i in (1, 2)]
        parent = chunk_tts.read_pcm16(f"{nd}/y_voice_2.wav")
        self.assertEqual(len(parent), len(pcm[0]) + len(pcm[1]) + 4800)
        self.assertTrue((parent[len(pcm[0]):len(pcm[0]) + 4800] == 0).all())
        dec = self.rj(f"{self.b1}/audit/chunk_tts_decision.json")
        self.assertEqual((dec["decision"], dec["method"], dec["approval"], dec["z_b_r1_adopted"]), ("applied_X_method", "X_paragraph_0.2s", "APPROVED_FOR_PRODUCTION", False))
        self.assertEqual(dec["segments"]["y_voice_2"]["paragraphs"], 2)
        ev = self.rj(f"{self.b1}/audit/chunk_tts_evidence_b1b.json")
        self.assertEqual(sorted(ev["parents"]), ["y_closing", "y_voice_2"])
        self.assertEqual(ev["parents"]["y_closing"]["chunk_count"], 3)

    def test_gate_and_assemble_with_0_2s_pause_and_unmerged_speaker_switches(self):
        self.multi_para_parts()
        self.generate()
        gate = ya.y_style_gate(self.out, "b1b", r.STYLE_PROFILE)
        self.assertEqual(gate["status"], "PASS", gate)
        names = [x["segment"] for x in gate["y_body_checks"]]
        self.assertIn("y_voice_2_k1", names)
        self.assertNotIn("y_voice_2", names)                                         # 親ではなく全chunkを検査
        s = self.assemble()
        self.assertEqual(s["status"], "OK", s)
        ct = s["chunk_tts"]
        for sid, n in (("y_voice_2", 2), ("y_closing", 3)):
            p = ct["parents"][sid]
            self.assertEqual(len(p["gap_offsets_in_segment_s"]), n - 1)
            for a, b in p["gap_offsets_in_segment_s"]:
                self.assertAlmostEqual(b - a, 0.2, places=3)
            self.assertEqual(len(p["gains"]), n)
            self.assertIsNotNone(p["segment_start_in_episode_s"])
        tl = self.rj(f"{self.b1}/audit/timeline.json")
        labels = [e["part"] for e in tl]
        i = labels.index(ys.PAGE_LABEL["y_intro_2"])
        self.assertEqual(labels[i:i + 5], [ys.PAGE_LABEL["y_intro_2"], "pause_intro_to_voice", ys.PAGE_LABEL["y_voice_2"], "pause_voice_gap", ys.PAGE_LABEL["y_intro_3"]])
        # timelineのvoice_2の長さ == chunk別gain後の長さ合計 + 0.2秒(結合はsegment内のみ。話者切替pauseは従来値のまま)
        e = next(x for x in tl if x["part"] == ys.PAGE_LABEL["y_voice_2"])
        self.assertGreater(e["duration_seconds"], 0.2)
        self.assertTrue(os.path.exists(f"{self.b1}/audit/chunk_tts_assembly_b1b.json"))

    def _api_lines(self):
        p = f"{self.out}/mock_api_calls.jsonl"
        with open(p, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]

    def test_resume_reuses_ok_chunks_with_zero_tts_calls(self):
        self.multi_para_parts()
        self.generate()
        before = self._api_lines()
        self.assertTrue([c for c in before if c["label"].startswith("y_voice_2_k")])
        self.generate()
        added = self._api_lines()[len(before):]
        self.assertEqual([c["label"] for c in added if c["kind"] == "tts" and c["label"].startswith("y_")], [])      # OK chunk/segmentは再利用(再課金なし)

    def test_failed_chunk_makes_parent_not_all_validated_and_blocks_assembly(self):
        self.multi_para_parts()
        self.generate()
        res = self.results()
        res["segments"]["y_closing_k2"]["status"] = "STOPPED"
        self.save_results(res)
        with self.assertRaises(RuntimeError) as e:
            self.assemble()
        self.assertIn("EPISODE_BLOCKED_BY_AUDIO_VALIDATION", str(e.exception))
        res = self.results()      # assembleの入口で親が再構築されている
        self.assertEqual(res["segments"]["y_closing"]["status"], chunk_tts.PARENT_STATUS_NOT_ALL_VALIDATED)
        self.assertIn("y_closing_k2", json.dumps(res["segments"]["y_closing"]["chunk_tts"]["chunk_gate_statuses"]))

    def test_style_gate_inspects_every_chunk_not_only_the_first(self):
        self.multi_para_parts()
        self.generate()
        res = self.results()
        res["segments"]["y_voice_2_k2"]["local_rewrite_recovery"] = {"mock": True}      # chunk2だけがLocal Rewrite recoveryで生成された
        self.save_results(res)
        g = ya.y_style_gate(self.out, "b1b", "default")
        self.assertEqual(g["status"], "BLOCK")
        blocked = {x["segment"] for x in g["y_body_blocked"]}
        self.assertEqual(blocked, {"y_voice_2_k2"})                                  # chunk1ではなくchunk2が止まる(親へchunk1の値を写して素通りさせない)
        res["segments"]["y_voice_2_k2"].pop("local_rewrite_recovery")
        self.save_results(res)
        # 欠落chunkは必ずBLOCK
        res = self.results()
        del res["segments"]["y_voice_2_k2"]
        self.save_results(res)
        g = ya.y_style_gate(self.out, "b1b", "default")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("y_voice_2_k2", {x["segment"] for x in g["y_body_blocked"]})

    def test_tampered_or_missing_chunk_audio_stops_assembly(self):
        self.multi_para_parts()
        self.generate()
        w = f"{self.b1}/narration/y_voice_2_k1.wav"
        pcm = chunk_tts.read_pcm16(w)
        chunk_tts.write_pcm16(w, pcm[: len(pcm) // 2])           # 親wav(生連結)とずれる
        with self.assertRaises(Exception) as e:
            self.assemble()
        self.assertTrue("FAMILY_Y_CHUNK_INTEGRITY" in str(e.exception) or "ASSET_HASH_MISMATCH" in str(e.exception), str(e.exception)[:300])

    def test_voice_mismatch_drops_chunk_cache(self):
        cached = {"segments": {"y_voice_2_k1": {"y_tts_voice_requested": "Algieba"}, "y_voice_2_k2": {"y_tts_voice_requested": "Zephyr"},
                               "y_closing_k1": {}}}
        out = ya.voice_guard_cached(cached)
        self.assertEqual(sorted(out["segments"]), ["y_voice_2_k2"])
        self.assertEqual(sorted(out["y_dropped_for_voice_mismatch"]), ["y_closing_k1", "y_voice_2_k1"])

    def test_scope_reverted_fails_closed_before_billing(self):
        with mock.patch.dict(ys.CHUNK_TTS_SCOPE, {"Y": False}):
            with self.assertRaises(ya.YAudioStop) as e:
                ya._record_chunk_decision(self.b1, "b1b")
        self.assertIn("FAMILY_Y_CHUNK_TTS_SCOPE_REVERTED", str(e.exception))


class TestIsolation(unittest.TestCase):
    def test_no_network_or_real_client_attempts(self):
        self.assertEqual((BLOCK["net"], BLOCK["client"]), (0, 0))

    def test_y_audio_imports_only_shared_er117_not_dev_trial_or_z_planner(self):
        with open(os.path.join(ROOT, "er121_family_y_audio_01.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotRegex(src, r"import er110_|import er114_|import er113_|plan_z_clip|plan_z_level|paragraph_texts_for_clip")
        self.assertIn("import er117_chunk_tts_production_01 as chunk_tts", src)


if __name__ == "__main__":
    unittest.main()
