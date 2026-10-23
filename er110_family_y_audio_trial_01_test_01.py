# -*- coding: utf-8 -*-
"""er110_family_y_audio_trial_01 offline test(API 0)。実行: .venv\\Scripts\\python.exe -m pytest er110_family_y_audio_trial_01_test_01.py"""
from __future__ import annotations

import glob
import os
import re
import shutil
import tempfile
import unittest

import numpy as np

import er110_family_y_audio_trial_01 as y
import er020_tts_retry_local_rewrite_01 as retry_primitive

ROOT = os.path.dirname(os.path.abspath(__file__))


def _dummy(n=100):
    return np.zeros((n, 2), dtype=np.float32)


class TestParts(unittest.TestCase):
    def test_split_five_parts_and_map(self):
        text = "# T\n\n" + "\n\n".join(f"P{i} words here." for i in range(1, 6)) + "\n\n## In one line\nOne line."
        p = y.split_y_article(text)
        self.assertEqual([p[f"part{i}"] for i in range(1, 6)], [f"P{i} words here." for i in range(1, 6)])
        self.assertEqual(p["in_one_line"], "One line.")
        self.assertEqual(p["y_segment_map"]["part2"]["tts_voice"], "Algieba")
        self.assertEqual(p["y_segment_map"]["part3"]["tts_voice"], "Zephyr")
        self.assertEqual(p["y_segment_map"]["part4"]["tts_voice"], "Schedar")

    def test_split_rejects_wrong_paragraph_count(self):
        with self.assertRaises(y.YAudioStop):
            y.split_y_article("# T\n\nA\n\nB\n\n## In one line\nX")

    def test_fixed_voices_user_decision(self):
        self.assertEqual(y.FIXED_VOICE_SLOTS, {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"})
        self.assertEqual([v for _r, _s, v in y.Y_BODY], ["Aoede", "Algieba", "Zephyr", "Schedar", "Aoede"])


class TestParityWithX(unittest.TestCase):
    def test_all_body_segments_get_x_full_story_treatment(self):
        for sid in y.Y_BODY_IDS:
            self.assertEqual(retry_primitive.resolve_narrative_role(sid), "FULL_STORY", sid)
            self.assertTrue(retry_primitive.connected_speech_enabled_for(sid), sid)

    def test_ids_unique_and_five(self):
        self.assertEqual(len(set(y.Y_BODY_IDS)), 5)

    def test_no_pro_tts(self):
        src = open(os.path.join(ROOT, "er110_family_y_audio_trial_01.py"), encoding="utf-8").read()
        self.assertEqual(y.TTS_BACKEND, "speech_metadata_flash_lite")
        self.assertNotIn("pro-preview-tts", src)
        self.assertNotIn("bvoices", src)     # Pro model(2.5-pro)を使う旧Voice関数は使わない

    def test_no_comment4_in_y(self):
        src = open(os.path.join(ROOT, "er110_family_y_audio_trial_01.py"), encoding="utf-8").read()
        self.assertNotIn('"comment_3", "comment_4"', src)   # 生成loop・読込にcomment_4を持たない(gate filterの除外記述のみ許容)
        self.assertNotIn('seg["comment_4"]', src)


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
            "full_story_part2": {"status": "OK", "y_tts_voice_requested": "Algieba"},      # 一致 -> 再利用
            "full_story_part3": {"status": "OK", "y_tts_voice_requested": "Aoede"},        # 不一致 -> 外す
            "full_story_part3_c2": {"status": "OK"},                                       # 記録なし -> 外す
            "preview": {"status": "OK"}}}
        out = y.voice_guard_cached(cached)
        self.assertIn("full_story_part2", out["segments"])
        self.assertNotIn("full_story_part3", out["segments"])
        self.assertNotIn("full_story_part3_c2", out["segments"])
        self.assertIn("preview", out["segments"])
        self.assertEqual(sorted(out["y_m4_dropped_for_voice_mismatch"]), ["full_story_part3", "full_story_part3_c2"])
        self.assertIn("full_story_part3", cached["segments"])    # 元dictは変更しない
        self.assertIsNone(y.voice_guard_cached(None))


class TestTrialStoreNamespace(unittest.TestCase):
    def test_trial_store_copy_and_path_override_leaves_production_untouched(self):
        import er006_master_audio_store_01 as mas
        saved = (mas.STORE_DIR, mas.AUDIO_DIR, mas.MANIFEST_PATH, mas.TELEMETRY_PATH)
        tmp = tempfile.mkdtemp()
        try:
            prod = os.path.join(tmp, "prod")
            os.makedirs(os.path.join(prod, "audio"))
            open(os.path.join(prod, "manifest.json"), "w").write("{}")
            trial = os.path.join(tmp, "trial")
            info = y.use_trial_master_store(trial, prod)
            self.assertTrue(os.path.exists(os.path.join(trial, "manifest.json")))
            self.assertEqual(mas.MANIFEST_PATH, f"{trial}/manifest.json")
            self.assertNotEqual(mas.STORE_DIR, prod)
            self.assertIn("snapshot copy", info["method"])
        finally:
            mas.STORE_DIR, mas.AUDIO_DIR, mas.MANIFEST_PATH, mas.TELEMETRY_PATH = saved
            shutil.rmtree(tmp, ignore_errors=True)


class TestTimeline(unittest.TestCase):
    def _labels(self, level):
        import er003_b1_p9a_audio as p9a
        seg = {n: _dummy() for n in (*y.Y_BODY_IDS, "comment_1", "comment_2", "comment_3", "in_one_line")}
        if level == "b1b":
            seg["preview"] = _dummy()
            parts = {k: _dummy() for k in ("intro", "welcome", "topic_intro", "notification", "preview_intro", "key_phrases_intro",
                                           "full_story_intro", "outro")}
            parts["b1_segments"] = seg
            import er003_v1_n3_01_assemble as asm
            orig = asm.build_b1_key_phrase_blocks
            asm.build_b1_key_phrase_blocks = lambda p: [_dummy(), _dummy(), _dummy()]
            try:
                seq = y.build_y_b1_timeline(parts)
            finally:
                asm.build_b1_key_phrase_blocks = orig
        else:
            parts = {k: _dummy() for k in ("intro", "welcome", "topic_intro", "notification", "preview_intro", "key_phrases_intro",
                                           "full_story_intro", "outro", "japanese_title", "preview")}
            parts["a2_segments"] = seg
            import er003_v1_n3_01_assemble as asm
            orig = asm.build_a2_key_phrase_blocks
            asm.build_a2_key_phrase_blocks = lambda p: [_dummy(), _dummy(), _dummy()]
            try:
                seq = y.build_y_a2_timeline(parts)
            finally:
                asm.build_a2_key_phrase_blocks = orig
        return [lab for lab, _ in seq]

    def test_order_and_no_interleaved_comment_between_voices(self):
        for level in ("b1b", "a2"):
            labs = [l for l in self._labels(level) if not l.startswith("pause")]
            self.assertFalse(any("Comment 4" in l for l in labs))
            i1 = labs.index(next(l for l in labs if "Voice 1" in l))
            i3 = labs.index(next(l for l in labs if "Voice 3" in l))
            self.assertEqual(i3 - i1, 2)
            self.assertIn("Voice 2", labs[i1 + 1])       # Voice1→Voice2→Voice3は連続(間にComment/SFXなし)
            order = [l for l in labs if l.startswith("Comment") or l.startswith("Full Story") or l.startswith("In One")]
            self.assertEqual([o.split(" (")[0] for o in order],
                             ["Comment 1", "Full Story: Lead", "Comment 2", "Full Story: Voice 1", "Full Story: Voice 2",
                              "Full Story: Voice 3", "Comment 3", "Full Story: Closing", "In One Line"])


class TestGateFailClosed(unittest.TestCase):
    def test_empty_results_block(self):
        tmp = tempfile.mkdtemp()
        try:
            theme = os.path.join(tmp, "t")
            os.makedirs(f"{theme}/a2/audit")
            y.save_json(f"{theme}/a2/audit/tts_generation_results.json", {"segments": {}, "key_phrases": {}})
            y.save_json(f"{theme}/audit/style_profile.json", {})   # recordは使わない(gateはprofile固定で直接判定)
            res = y.y_style_gate(theme, "a2")
            self.assertEqual(res["status"], "BLOCK")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestProductionIsolation(unittest.TestCase):
    def test_no_production_reference(self):
        self_names = {"er110_family_y_audio_trial_01", "er110_family_y_audio_report_01", "er110_family_y_audio_page_01"}
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if b.startswith("er110_") or "_test" in b or b.startswith("test_"):
                continue
            try:
                src = open(p, encoding="utf-8").read()
            except Exception:
                continue
            for n in self_names:
                self.assertNotIn(n, src, f"{b} references {n}")

    def test_no_env_or_flag_switch(self):
        src = open(os.path.join(ROOT, "er110_family_y_audio_trial_01.py"), encoding="utf-8").read()
        self.assertNotIn("os.environ", src)
        self.assertIsNone(re.search(r"ENABLED\s*=", src))


if __name__ == "__main__":
    unittest.main()
