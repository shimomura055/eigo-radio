# -*- coding: utf-8 -*-
"""er110_family_y_persona_audio_trial_01 offline test(API 0)。M3/M4 parity(4パート+Comment/見出しsegment ID)・隔離。"""
from __future__ import annotations

import glob
import os
import re
import shutil
import tempfile
import unittest

import numpy as np

import er110_family_y_persona_audio_trial_01 as y
import er020_tts_retry_local_rewrite_01 as retry_primitive

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(ROOT, "er110_family_y_persona_audio_trial_01.py"), encoding="utf-8").read()


def _dummy(n=100):
    return np.zeros((n, 2), dtype=np.float32)


class TestParts(unittest.TestCase):
    def test_split_four_parts_and_map(self):
        text = "# T\n\n" + "\n\n".join(f"P{i} words here." for i in range(1, 5)) + "\n\n## In one line\nOne line."
        p = y.split_y_article(text)
        self.assertEqual([p[f"part{i}"] for i in range(1, 5)], [f"P{i} words here." for i in range(1, 5)])
        self.assertEqual(p["in_one_line"], "One line.")
        self.assertEqual([p["y_segment_map"][f"part{i}"]["tts_voice"] for i in range(1, 5)], ["Algieba", "Zephyr", "Schedar", "Aoede"])

    def test_split_rejects_five_or_three_paragraphs(self):
        for n in (3, 5):
            text = "# T\n\n" + "\n\n".join(f"P{i}." for i in range(n)) + "\n\n## In one line\nX"
            with self.assertRaises(y.YAudioStop):
                y.split_y_article(text)

    def test_fixed_voices_and_headings_narrator(self):
        self.assertEqual(y.FIXED_VOICE_SLOTS, {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"})
        self.assertEqual([v for _r, _s, v in y.Y_BODY], ["Algieba", "Zephyr", "Schedar", "Aoede"])
        self.assertEqual(y.HEADING_VOICE, "Aoede")
        self.assertEqual(len(y.HEADING_IDS), 3)


class TestParityWithX(unittest.TestCase):
    def test_all_body_segments_get_x_full_story_treatment(self):
        for sid in y.Y_BODY_IDS:
            self.assertEqual(retry_primitive.resolve_narrative_role(sid), "FULL_STORY", sid)
            self.assertTrue(retry_primitive.connected_speech_enabled_for(sid), sid)

    def test_ids_unique_and_four(self):
        self.assertEqual(len(set(y.Y_BODY_IDS)), 4)
        self.assertEqual(len(set(y.Y_BODY_IDS) | set(y.HEADING_IDS)), 7)

    def test_no_pro_tts_no_comment3_4(self):
        self.assertEqual(y.TTS_BACKEND, "speech_metadata_flash_lite")
        self.assertNotIn("pro-preview-tts", SRC)
        self.assertNotIn("bvoices", SRC)
        self.assertNotIn('seg["comment_3"]', SRC)
        self.assertNotIn('seg["comment_4"]', SRC)
        self.assertNotIn('"comment_3", "comment_4"):\n', SRC.split("def y_style_gate")[0])    # 生成/読込loopに持たない

    def test_heading_paths_documented_and_distinct(self):
        # Std=既存A2減速関数、Adv=減速なし経路(generate_english_segment_with_fallback)。いずれもdisfluency_qa=True・先頭3語アンカー
        std = SRC.split("def generate_y_a2_segments")[1]
        adv = SRC.split("def generate_y_b1_segments")[1].split("def generate_y_a2_segments")[0]
        self.assertIn("generate_a2_segment_with_slowdown(\n                        tts_in", std)
        self.assertIn("generate_english_segment_with_fallback(\n                        tts_in", adv)
        for blk in (std.split("body = [")[0], adv.split("body = [")[0]):
            self.assertIn("first_words(text, 3)", blk)
            self.assertIn("disfluency_qa=True", blk)


class TestVoiceOverride(unittest.TestCase):
    def test_voice_restored_after_exception(self):
        before = y.xr.p9a.VOICE_NAME
        with self.assertRaises(RuntimeError):
            with y.tts_voice("Schedar"):
                self.assertEqual(y.xr.p9a.VOICE_NAME, "Schedar")
                raise RuntimeError("x")
        self.assertEqual(y.xr.p9a.VOICE_NAME, before)
        self.assertEqual(before, "Aoede")

    def test_import_does_not_change_default_voice_or_store(self):
        import er006_master_audio_store_01 as mas
        self.assertEqual(y.xr.p9a.VOICE_NAME, "Aoede")
        self.assertEqual(mas.STORE_DIR, "er006_output/master_audio_store_01")


class TestM4VoiceGuard(unittest.TestCase):
    def test_voice_mismatch_or_missing_voice_not_reused(self):
        cached = {"segments": {
            "full_story_part1": {"status": "OK", "y_tts_voice_requested": "Algieba"},      # 一致
            "full_story_part2": {"status": "OK", "y_tts_voice_requested": "Aoede"},        # 不一致 -> 外す
            "full_story_part3": {"status": "OK"},                                          # 記録なし -> 外す
            "voice_heading_1": {"status": "OK", "y_tts_voice_requested": "Aoede"},          # 一致
            "voice_heading_2": {"status": "OK", "y_tts_voice_requested": "Charon"},         # 不一致 -> 外す
            "preview": {"status": "OK"}}}
        out = y._guard_cached(cached)
        self.assertIn("full_story_part1", out["segments"])
        self.assertIn("voice_heading_1", out["segments"])
        self.assertIn("preview", out["segments"])
        self.assertEqual(sorted(out["y_m4_dropped_for_voice_mismatch"]), ["full_story_part2", "full_story_part3", "voice_heading_2"])
        self.assertIn("full_story_part2", cached["segments"])
        self.assertIsNone(y._guard_cached(None))


class TestTimeline(unittest.TestCase):
    def _labels(self, level):
        import er003_v1_n3_01_assemble as asm
        seg = {n: _dummy() for n in y.SEG_IN_SOURCES}
        base = {k: _dummy() for k in ("intro", "welcome", "topic_intro", "notification", "preview_intro", "key_phrases_intro", "full_story_intro", "outro")}
        if level == "b1b":
            seg["preview"] = _dummy()
            base["b1_segments"] = seg
            orig = asm.build_b1_key_phrase_blocks
            asm.build_b1_key_phrase_blocks = lambda p: [_dummy(), _dummy(), _dummy()]
            try:
                seq = y.build_y_b1_timeline(base)
            finally:
                asm.build_b1_key_phrase_blocks = orig
        else:
            base.update({"japanese_title": _dummy(), "preview": _dummy()})
            base["a2_segments"] = seg
            orig = asm.build_a2_key_phrase_blocks
            asm.build_a2_key_phrase_blocks = lambda p: [_dummy(), _dummy(), _dummy()]
            try:
                seq = y.build_y_a2_timeline(base)
            finally:
                asm.build_a2_key_phrase_blocks = orig
        return [lab for lab, _ in seq]

    def test_order_comment12_then_heading_voice_pairs_then_tension(self):
        for level in ("b1b", "a2"):
            labs = [l for l in self._labels(level) if not l.startswith("pause")]
            self.assertFalse(any("Comment 3" in l or "Comment 4" in l for l in labs))
            order = [l for l in labs if l.startswith("Comment") or l.startswith("Full Story:") or l.startswith("Narrator:") or l.startswith("In One")]
            self.assertEqual([o.split(" (")[0] for o in order],
                             ["Comment 1", "Comment 2", "Narrator: One Voice heading", "Full Story: Voice 1", "Narrator: Another Voice heading",
                              "Full Story: Voice 2", "Narrator: A Third Voice heading", "Full Story: Voice 3", "Full Story: Tension + Closing",
                              "In One Line"])


class TestGateFailClosed(unittest.TestCase):
    def test_empty_results_block(self):
        tmp = tempfile.mkdtemp()
        try:
            theme = os.path.join(tmp, "t")
            os.makedirs(f"{theme}/a2/audit")
            y.save_json(f"{theme}/a2/audit/tts_generation_results.json", {"segments": {}, "key_phrases": {}})
            res = y.y_style_gate(theme, "a2")
            self.assertEqual(res["status"], "BLOCK")
            self.assertTrue(any(c["segment"] in y.HEADING_IDS for c in res["y_body_checks"]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestProductionIsolation(unittest.TestCase):
    def test_no_production_reference(self):
        mine = ("er110_family_y_persona_",)
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if b.startswith("er110_") or "_test" in b or b.startswith("test_"):
                continue
            try:
                src = open(p, encoding="utf-8").read()
            except Exception:
                continue
            for n in mine:
                self.assertNotIn(n, src, f"{b} references {n}")

    def test_no_env_or_flag_switch(self):
        self.assertNotIn("os.environ", SRC)
        self.assertIsNone(re.search(r"ENABLED\s*=", SRC))


if __name__ == "__main__":
    unittest.main()
