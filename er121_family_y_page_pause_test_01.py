# -*- coding: utf-8 -*-
"""FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_03: 試聴ページ(TTS分割/追加0.2秒の明示・Voice 1候補表の停止統計)の表示helperのtest。API 0・表示専用。
FAMILY-Y-STYLE-PROFILE-FIX-01 委任_08: 台本への実測ポーズ⏸重畳は撤去(ASR/音声解析ポーズは表示しない)。台本の⏸=実Chunk境界のみ・開発用限定=er_page_audience_marker_test_01.py。"""
import os
import unittest

import numpy as np

import er121_family_y_audio_01 as ya

SR = 24000


def _sig(spec):
    """spec=[(秒, 有音?)] -> float32 mono。有音=0.3の正弦、無音=0。"""
    out = []
    for sec, tone in spec:
        n = int(SR * sec)
        out.append((0.3 * np.sin(2 * np.pi * 220 * np.arange(n) / SR)) if tone else np.zeros(n))
    return np.concatenate(out).astype("float32")


class PauseScanTest(unittest.TestCase):
    def test_inner_pause_measured_lead_trail_excluded(self):
        sc = ya.pause_scan(_sig([(0.3, 0), (1.0, 1), (1.2, 0), (1.0, 1), (0.4, 0)]), SR)
        self.assertEqual(len(sc["pauses"]), 1)
        self.assertAlmostEqual(sc["pauses"][0]["dur_ms"], 1200, delta=30)
        self.assertAlmostEqual(sc["pauses"][0]["start_s"], 1.3, delta=0.05)
        self.assertEqual((sc["lead_ms"], sc["trail_ms"] > 0), (300, True))

    def test_blip_merge(self):
        sc = ya.pause_scan(_sig([(0.5, 1), (0.4, 0), (0.05, 1), (0.4, 0), (0.5, 1)]), SR)
        self.assertEqual(len(sc["pauses"]), 1)

    def test_stats_keys_and_align_marks_long_pause_after_word(self):
        text = "one two three, four five six seven eight nine ten"
        x = _sig([(1.0, 1), (1.5, 0), (3.0, 1)])
        st = ya.pause_stats(x, SR, text)
        self.assertEqual(st["ge1000"], 1)
        self.assertEqual(st["ge700"], 1)
        self.assertAlmostEqual(st["max_ms"], 1500, delta=30)
        al = ya.pause_align(ya.pause_scan(x, SR), text)
        self.assertEqual(len(al), 1)
        self.assertTrue(al[0]["at_punctuation"])          # 句読点直後を優先して割当(Voice 1候補表の停止統計用の解析。台本には重畳しない)

    def test_asr_pause_is_never_rendered_into_script(self):
        """実測ポーズ(1.5秒)があっても、台本ブロック(公開/開発とも)にポーズ由来の⏸は出ない(境界=実Chunk planのみ)。"""
        import er_user_listening_page_common_01 as cp
        text = "one two three, four five six seven eight nine ten"
        self.assertEqual(ya.pause_align(ya.pause_scan(_sig([(1.0, 1), (1.5, 0), (3.0, 1)]), SR), text)[0]["dur_ms"] // 100, 15)
        for aud in ("public", "dev"):
            self.assertEqual(cp.count_chunk_markers(cp.script_block(text, None, aud)), 0)
        self.assertFalse(hasattr(ya, "PAUSE_MARK_MIN_MS"))


class BadgeTest(unittest.TestCase):
    def test_std_and_adv_both_follow_the_decision_record(self):
        # 2026-10-26: Standardも分割対象(旧『Standardの本文は分割対象外』表示は撤去)。表示は判定記録(chunk_tts_decision.json)に従う。
        dec = {"segments": {"y_voice_1": {"chunked": False, "paragraphs": 1, "chunk_ids": []}}, "chunk_tts_applied_at_this_level": True}
        std = ya._tts_unit_badge("a2", dec, "y_voice_1")
        self.assertNotIn("分割対象外", std)
        self.assertIn("分割なし(段落=1)", std)
        decc = {"segments": {"y_voice_1": {"chunked": True, "paragraphs": 2, "chunk_ids": ["y_voice_1_k1", "y_voice_1_k2"]}}}
        self.assertIn("TTS 2分割", ya._tts_unit_badge("a2", decc, "y_voice_1"))
        old = {"chunk_tts_applicable": True, "chunk_tts_applied_at_this_level": False, "not_applied_reason": "Std(a2)本文はX同様chunk化しない"}
        self.assertIn("旧記録", ya._tts_unit_badge("a2", old, "y_voice_1"))                        # 2026-10-26以前のStd記録は旧記録と明示
        b = ya._tts_unit_badge("b1b", dec, "y_voice_1")
        self.assertIn("分割なし", b)
        self.assertIn("追加0.2秒ポーズ: なし", b)

    def test_chunked_shows_split(self):
        dec = {"segments": {"y_voice_1": {"chunked": True, "paragraphs": 2, "chunk_ids": ["y_voice_1_k1", "y_voice_1_k2"]}}}
        b = ya._tts_unit_badge("b1b", dec, "y_voice_1")
        self.assertIn("TTS 2分割", b)
        self.assertIn("あり", b)

    def test_legend_states_no_split_when_none(self):
        dec = {"advanced": {"segments": {"y_voice_1": {"chunked": False}}}, "standard": {"segments": {}}}
        lg = ya.page_legend_html(dec)
        self.assertIn("TTSの実分割: <b>なし", lg)
        self.assertIn("追加0.2秒ポーズ: <b>なし", lg)
        self.assertNotIn("&#9208;", lg)                     # 公開(既定)の凡例にマーカー/見本は無い
        self.assertNotIn("実測", lg)
        self.assertIn("&#9208;=TTS Chunk分割境界(開発確認用)", ya.page_legend_html(dec, "dev"))     # 開発用のみ1行

    def test_candidates_aux_empty_without_candidates(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(ya.voice1_candidates_aux_html(td, td, "audio"), "")


class AdoptedWavMatchesResearchToolTest(unittest.TestCase):
    RUN = "er121_output/family_y_production_01/redelivery_fee/run_01"

    def test_same_numbers_as_research_tool(self):
        wav = f"{self.RUN}/b1b/narration/y_voice_1.wav"
        if not os.path.exists(wav):
            self.skipTest("run_01 wav 無し")
        import json
        import soundfile as sf
        x, sr = sf.read(wav, dtype="float32")
        t = json.load(open(f"{self.RUN}/b1b/parts.json", encoding="utf-8"))["segments"]["y_voice_1"]
        st = ya.pause_stats(x, sr, t)
        # docs/research/.../PAUSE_MEASUREMENT_01.md の表(Adv V1採用 attempt6): 停止14・>=700ms 7・>=1000ms 3・最大1250ms・占有率19.9%
        self.assertEqual((st["pauses_total"], st["ge700"], st["ge1000"], st["max_ms"], st["pause_ratio_pct"]), (14, 7, 3, 1250, 19.9))


if __name__ == "__main__":
    unittest.main()
