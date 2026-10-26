# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02: Y側のOpus R1/R2/R3(c)/R5反映test(API 0・偽TTS)。
実行: PYTHONPATH=netblock_harness_01 .venv/Scripts/python.exe -m pytest er121_family_y_std_chunk_opus_test_01.py -q
"""
from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er121_family_y_std_chunk_test_01 as base  # noqa: E402
from er121_family_y_std_chunk_test_01 import setUpModule, tearDownModule  # noqa: E402,F401  (遮断harnessを共有)
import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402


class TestOpusR1R2R3R5(base.BaseStd):
    def test_r1_load_y_body_chunks_a2_blocks_missing_slowdown_even_if_parent_aggregate_is_forged(self):
        self.multi_para_parts()
        self.generate()
        res = self.results()
        del res["segments"]["y_closing_k2"]["slowdown_applied"]                 # chunk2だけ減速証跡なし
        res["segments"]["y_closing"]["slowdown_applied"] = True                 # 親の集約値だけ偽装(共有Gateは通る)
        self.save_results(res)
        with self.assertRaises(ya.YAudioStop) as e:
            ya._load_y_body_chunks(self.a2, "a2")                               # stage関数(y_style_gate)を通さない直接呼び出し
        self.assertIn("FAMILY_Y_STD_CHUNK_SLOWDOWN_GATE", str(e.exception))
        self.assertIn("y_closing_k2", str(e.exception))

    def test_r1_adv_default_level_does_not_apply_std_check_and_std_pass_case_loads(self):
        self.multi_para_parts()
        self.generate()
        body, used = ya._load_y_body_chunks(self.a2, "a2")
        self.assertEqual(sorted(body), ["y_closing", "y_voice_2"])
        body_adv_default, _ = ya._load_y_body_chunks(self.a2)                   # 既定levelはAdv相当(Std検査なし=Adv不変)
        self.assertEqual(sorted(body_adv_default), ["y_closing", "y_voice_2"])

    def test_r2_missing_duration_record_blocks_in_load(self):
        self.multi_para_parts()
        self.generate()
        res = self.results()
        del res["segments"]["y_voice_2_k1"]["slowdown_info"]["src_duration_seconds"]
        self.save_results(res)
        with self.assertRaises(ya.YAudioStop) as e:
            ya._load_y_body_chunks(self.a2, "a2")
        self.assertIn("DURATION_RECORD_MISSING", str(e.exception))
        g = ya.y_style_gate(self.out, "a2", r.STYLE_PROFILE)
        self.assertEqual(g["status"], "BLOCK")

    def test_r3c_unknown_chunk_id_in_only_segments_is_rejected_before_billing(self):
        self.multi_para_parts()
        before = len(self.api_lines())
        old = ya.xr._ONLY_SEGMENTS
        try:
            ya.xr._ONLY_SEGMENTS = {"y_voice_2_k9"}
            with self.assertRaises(ya.YAudioStop) as e:
                self.generate()
        finally:
            ya.xr._ONLY_SEGMENTS = old
        self.assertIn("FAMILY_Y_CHUNK_ID_NOT_IN_PLAN", str(e.exception))
        self.assertEqual([c for c in self.api_lines()[before:] if c["kind"] == "tts"], [])

    def test_r5_legend_last_sentence_is_conditional_on_chunk_count(self):
        none = ya.page_legend_html({"standard": {"segments": {"y_voice_1": {"chunked": False}}}})
        self.assertIn("今回はありません", none)
        some = ya.page_legend_html({"standard": {"segments": {"y_voice_2": {"chunked": True}}}})
        self.assertNotIn("今回はありません", some)
        self.assertIn("1 segmentで分割", some)


class TestAdvDecisionGolden(unittest.TestCase):
    """Opus R4(c): b1bのchunk_tts_decision.jsonをgolden化。旧(bb578265c)との差分は注記文言(approval_ref/note)だけであることを固定する。"""
    GOLDEN = os.path.join(ROOT, "docs", "research", "CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01", "golden", "y_b1b_chunk_tts_decision_golden_01.json")

    def _g(self):
        import json
        with open(self.GOLDEN, encoding="utf-8") as f:
            return json.load(f)

    def test_adv_decision_record_matches_golden_except_run_specific_keys(self):
        g = self._g()["new_decision"]
        rec = ys.chunk_decision_record("b1b")
        for k, v in rec.items():
            self.assertEqual(g[k], v, k)                      # 判定記録の静的部分はgoldenと完全一致
        run_specific = {"segments", "planner_version", "extra_pause_seconds"}   # runごとに入る部分(_record_chunk_decisionが追加)
        self.assertEqual(set(g) - set(rec), run_specific)

    def test_golden_old_vs_new_differ_only_in_note_text(self):
        g = self._g()
        old, new = g["old_decision_bb578265c"], g["new_decision"]
        diff = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        self.assertEqual(diff, sorted(g["allowed_text_only_diff_keys"]))
        self.assertTrue(all(isinstance(old[k], str) and isinstance(new[k], str) for k in diff))


if __name__ == "__main__":
    unittest.main()
