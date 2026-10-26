# -*- coding: utf-8 -*-
"""FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01 委任_01: Family Y 段落分割(Chunk TTS)の「複数段落入力」定常回帰(API 0・TTS 0・偽TTS・合成入力)。
目的: 実Y記事は各Voice 1段落(承認済み本文契約)のため分割は不発火。実記事の本文を改変せずに、複数段落の合成入力で
「planner発火→chunk別6%減速(Std)→0.2秒無音→連結→Gate」が毎回の回帰で動くことを担保する(OPEN-527 Closeout、PRODUCTION_WIRED判定の代替ではない)。
既存: er121_family_y_std_chunk_test_01.py(Std 14件) / er121_family_y_audio_chunk_test_01.py(Adv) / er121_family_y_std_chunk_opus_test_01.py。本ファイルは境界・全8segment・Std/Adv同値・回帰網羅の穴埋め。
実行: PYTHONPATH=netblock_harness_01 .venv/Scripts/python.exe -m pytest er121_family_y_multiparagraph_regression_test_01.py -q
"""
from __future__ import annotations

import glob
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from er121_family_y_std_chunk_test_01 import BaseStd, setUpModule, tearDownModule, BLOCK  # noqa: E402,F401
import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402
import er117_chunk_tts_production_01 as chunk_tts  # noqa: E402


def _para(n: int, sid: str) -> list:
    return [f"This is synthetic paragraph {i} of {sid} for the offline chunk regression only." for i in range(1, n + 1)]


class TestPlannerBoundary(unittest.TestCase):
    """発火境界: 段落1=不発火(従来の1 call) / 2以上=段落単位chunk。全8 segment、区切りの空白ゆれ、segment内閉じ込め。"""

    def test_boundary_one_paragraph_never_fires_two_or_more_always_fires_for_every_y_segment(self):
        for n, fires in ((1, False), (2, True), (3, True), (5, True)):
            parts = {"segments": {sid: "\n\n".join(_para(n, sid)) for sid in ys.Y_SEGMENT_IDS}}
            plans = ya.plan_y_chunks(parts)
            self.assertEqual(list(plans), list(ys.Y_SEGMENT_IDS))
            for sid, pl in plans.items():
                self.assertIs(pl["chunked"], fires, (n, sid))
                if fires:
                    self.assertEqual([c["chunk_id"] for c in pl["chunks"]], [f"{sid}_k{i}" for i in range(1, n + 1)])
                    self.assertTrue(all(c["boundary_kind"] == "paragraph" for c in pl["chunks"]))
                    self.assertEqual(pl["extra_pause_seconds"], 0.2)
                    self.assertEqual(pl["split_method"], ys.CHUNK_TTS_Y_METHOD)
                    self.assertTrue(all(ys.parse_y_chunk_id(c["chunk_id"]) == (sid, c["index"]) for c in pl["chunks"]))
                else:
                    self.assertEqual(pl["chunks"], [])

    def test_blank_line_variants_split_but_a_single_newline_does_not(self):
        sid = "y_voice_2"
        a, b = _para(2, sid)
        for sep in ("\n\n", "\n \n", "\n\n\n"):
            parts = {"segments": {s: "One short line." for s in ys.Y_SEGMENT_IDS}}
            parts["segments"][sid] = a + sep + b
            self.assertTrue(ya.plan_y_chunks(parts)[sid]["chunked"], repr(sep))
        parts = {"segments": {s: "One short line." for s in ys.Y_SEGMENT_IDS}}
        parts["segments"][sid] = a + "\n" + b                               # 単一改行=段落ではない(X規則どおり)
        self.assertFalse(ya.plan_y_chunks(parts)[sid]["chunked"])

    def test_plan_is_level_independent_and_planner_version_is_pinned(self):
        parts = {"segments": {sid: "\n\n".join(_para(2, sid)) for sid in ys.Y_SEGMENT_IDS}}
        self.assertEqual(ya.plan_y_chunks(parts), ya.plan_y_chunks(parts))   # 決定論(Std/Adv共通のplan関数)
        self.assertEqual(ys.CHUNK_TTS_Y_LEVELS, ("b1b", "a2"))
        self.assertEqual(ys.CHUNK_TTS_Y_METHOD, "X_paragraph_0.2s")
        self.assertEqual(chunk_tts.CHUNK_PLANNER_VERSION, "chunk_tts_v1_x_paragraph_z_r1_20261025")  # 規則変更時は版更新(意図せぬ変更の検知)


class TestAllSegmentsMultiParagraphStd(BaseStd):
    """全8 segmentが複数段落のStd入力: 全chunkが6%減速され、親は0.2秒ちょうどの無音で連結、Gate PASS、組立OK。"""

    def _all_multi(self, n: int = 2):
        pj = f"{self.a2}/parts.json"
        parts = self.rj(pj)
        for sid in ys.Y_SEGMENT_IDS:
            parts["segments"][sid] = "\n\n".join(_para(n, sid))
        self.wj(pj, parts)
        for p in (f"{self.a2}/audit/tts_generation_results.json", f"{self.a2}/audit/chunk_plan_a2.json"):
            if os.path.exists(p):
                os.remove(p)
        for sid in ys.Y_SEGMENT_IDS:
            w = f"{self.a2}/narration/{sid}.wav"
            if os.path.exists(w):
                os.remove(w)

    def test_all_eight_segments_chunk_slow_down_join_and_gate_pass(self):
        self._all_multi(2)
        self.generate()
        segs = self.results()["segments"]
        for sid in ys.Y_SEGMENT_IDS:
            for i in (1, 2):
                e = segs[f"{sid}_k{i}"]
                self.assertEqual(e["status"], "OK", (sid, i))
                self.assertIs(e["slowdown_applied"], True, (sid, i))
            self.assertEqual(segs[sid]["status"], "OK")
            self.assertEqual(segs[sid]["chunk_tts"]["extra_pause_seconds"], 0.2)
            nd = f"{self.a2}/narration"
            k1, k2 = (chunk_tts.read_pcm16(f"{nd}/{sid}_k{i}.wav") for i in (1, 2))
            self.assertEqual(len(chunk_tts.read_pcm16(f"{nd}/{sid}.wav")), len(k1) + len(k2) + 4800)   # 24kHz*0.2s
        gate = ya.y_style_gate(self.out, "a2", ya.Y_APPROVED_STYLE_PROFILE)
        self.assertEqual(gate["status"], "PASS", gate)
        self.assertEqual(len([x for x in gate["y_body_checks"] if ys.parse_y_chunk_id(x["segment"])]), 16)
        s = self.assemble()
        self.assertEqual(s["status"], "OK", s)
        self.assertEqual(sorted(s["chunk_tts"]["parents"]), sorted(ys.Y_SEGMENT_IDS))
        for p in s["chunk_tts"]["parents"].values():
            self.assertEqual(len(p["gap_offsets_in_segment_s"]), 1)
            a, b = p["gap_offsets_in_segment_s"][0]
            self.assertAlmostEqual(b - a, 0.2, places=3)

    def test_one_failed_chunk_among_many_blocks_parent_and_assembly(self):
        self._all_multi(3)
        self.generate()
        res = self.results()
        res["segments"]["y_voice_3_k3"]["status"] = "STOPPED"
        self.save_results(res)
        with self.assertRaises(RuntimeError) as e:
            self.assemble()
        self.assertIn("EPISODE_BLOCKED_BY_AUDIO_VALIDATION", str(e.exception))
        self.assertEqual(self.results()["segments"]["y_voice_3"]["status"], chunk_tts.PARENT_STATUS_NOT_ALL_VALIDATED)


class TestRegressionCoverageGuard(unittest.TestCase):
    """Y複数段落の回帰が標準の発見パターン(er121*_test_*.py)から外れていないこと(OPEN-527 Closeout: 回帰体制の定常化)。"""

    def test_chunk_regression_files_are_discoverable_by_the_standard_pattern(self):
        found = {os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "er121*_test_*.py"))}
        for need in ("er121_family_y_std_chunk_test_01.py", "er121_family_y_audio_chunk_test_01.py",
                     "er121_family_y_std_chunk_opus_test_01.py", "er121_family_y_multiparagraph_regression_test_01.py"):
            self.assertIn(need, found)

    def test_this_suite_makes_no_network_or_real_client_attempts(self):
        self.assertEqual((BLOCK["net"], BLOCK["client"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
