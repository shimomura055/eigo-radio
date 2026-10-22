# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02 (OF-X9 / OF-X11 / OF-X12): 明示的無効化CLI・stage関数統合test。
TTSはmock(wavを書き、実entry形式を返す)のみ。API呼出なし。Gate(asm.verify_episode_audio_validation_gate)は無変更。"""
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
import wave
from unittest import mock

import er003_v1_n3_01_assemble as asm
import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_segment_invalidate_01 as inv
import er019_family_x_validation_inheritance_01 as vi
from er019_family_x_style_profile_01_test_01 import FL, _make_a2_dir

PROFILE = "coffee_n01_r2_p3"


def _wavbytes(tag=0, secs=0.5, rate=8000):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((tag.to_bytes(2, "little", signed=True)) * int(rate * secs))
    return buf.getvalue()


def _sha(b):
    return hashlib.sha256(b).hexdigest()


class _StageBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="comp02_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        _make_a2_dir(self.tmp)
        self.calls = []
        self.counter = 0

    def _mk(self, out, text, **extra):
        self.counter += 1
        data = _wavbytes(self.counter)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as f:
            f.write(data)
        self.calls.append(os.path.basename(out))
        e = {"status": "OK", "asr_verified": True, "text": text, "canonical_text": text, "path": out,
             "sha256": _sha(data), "duration_seconds": 0.5, "disfluency_checked": True,
             "trim_info": {"trimmed_duration_seconds": 0.5}}
        e.update(extra)
        return e

    def run_a2(self, only=None):
        self.calls = []

        def en_fallback(text, out, *a, **k):
            return self._mk(out, text)

        def ja(text, out, *a, **k):
            return self._mk(out, text)

        def slowdown(text, out, *a, **k):
            return self._mk(out, text, slowdown_applied=True)

        with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2", return_value={}), \
             mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback", side_effect=en_fallback), \
             mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety", side_effect=ja), \
             mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=slowdown), \
             mock.patch.object(runner, "_ONLY_SEGMENTS", only):
            runner.generate_family_x_a2_segments(self.tmp, "タイトル", tts_backend=FL, style_profile=PROFILE)
        return json.load(open(f"{self.tmp}/a2/audit/tts_generation_results.json", encoding="utf-8"))


class StageIntegrationTest(_StageBase):
    def test_only_segments_keeps_whole_results_and_regenerates_only_target(self):
        res1 = self.run_a2()
        self.assertEqual(len(res1["segments"]), 11)
        part2_sha_before = res1["segments"]["full_story_part2"]["sha256"]
        inv.plan_and_apply(f"{self.tmp}/a2", ["full_story_part2"], "test", apply=True)  # cache OKのままでは再利用されるため明示無効化
        res2 = self.run_a2(only={"full_story_part2"})
        self.assertEqual(self.calls, ["full_story_part2.wav"])  # 対象のみ生成
        self.assertEqual(sorted(res2["segments"]), sorted(res1["segments"]))  # results全体保持
        self.assertNotEqual(res2["segments"]["full_story_part2"]["sha256"], part2_sha_before)
        for name, e in res2["segments"].items():
            self.assertEqual(e["status"], "OK", name)
            if name != "full_story_part2":
                self.assertEqual(e["validation_inheritance"]["label"], "REUSED_VALIDATED", name)
                self.assertEqual(e["sha256"], res1["segments"][name]["sha256"], name)
        # canonical_textは現行textで上書きされる(引継ぎ時にtext一致を確認済みのため矛盾しない)/style_profileは元entryのまま保持
        self.assertEqual(res2["segments"]["preview"]["canonical_text"], "プレビュー。")
        self.assertEqual(res2["segments"]["preview"]["style_profile"], res1["segments"]["preview"]["style_profile"])
        self.assertIn("style_profile", res2["segments"]["full_story_part2"])  # 再生成segmentには現行profile記録
        self.assertEqual(res2["only_segments"], ["full_story_part2"])

    def test_text_change_disables_inheritance(self):
        self.run_a2()
        json.dump({"preview": "新プレビュー。", "comment_1": "コメント1。", "comment_2": "コメント2。",
                   "comment_3": "コメント3。", "comment_4": "コメント4。"},
                  open(f"{self.tmp}/a2/a2_support_texts.json", "w", encoding="utf-8"))
        res = self.run_a2(only={"full_story_part2"})
        self.assertEqual(res["segments"]["preview"]["status"], "SKIPPED_NOT_SELECTED")  # 古い文面は引継がない
        self.assertEqual(res["segments"]["comment_1"]["status"], "OK")

    def test_invalidate_then_runner_regenerates_target(self):
        """OF-X9: 無効化後は(cache OKによる再利用ではなく)再生成経路へ入る。Gateは無効化entryをUNVALIDATED扱い。"""
        res1 = self.run_a2()
        # 無効化なしで--only-segments指定: cache OKのため旧takeが再利用され生成は呼ばれない(OF-X9の問題の再現)
        self.run_a2(only={"full_story_part2"})
        self.assertEqual(self.calls, [])
        self.run_a2()
        self.assertEqual(self.calls, [])  # 通常reuseでも全segment再利用(生成0)
        # 無効化
        rep = inv.plan_and_apply(f"{self.tmp}/a2", ["full_story_part2"], "test reason", apply=True)
        self.assertTrue(rep["labels"]["full_story_part2"]["ok"])
        moved = rep["labels"]["full_story_part2"]["moved_to"]
        self.assertTrue(all(os.path.exists(m) for m in moved))
        self.assertFalse(os.path.exists(f"{self.tmp}/a2/narration/full_story_part2.wav"))
        cur = json.load(open(f"{self.tmp}/a2/audit/tts_generation_results.json", encoding="utf-8"))
        e = cur["segments"]["full_story_part2"]
        self.assertEqual(e["status"], "INVALIDATED_FOR_REGENERATION")
        self.assertEqual(e["original_sha256"], res1["segments"]["full_story_part2"]["sha256"])
        self.assertEqual(e["reason"], "test reason")
        with self.assertRaises(RuntimeError) as cm:  # Gate: fail-closed
            asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")
        self.assertIn("full_story_part2", str(cm.exception))
        # runner(通常reuse経路)は無効化segmentだけを再生成し、他はcacheを再利用する
        res3 = self.run_a2()
        self.assertEqual(self.calls, ["full_story_part2.wav"])
        self.assertEqual(res3["segments"]["full_story_part2"]["status"], "OK")
        asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")  # 再生成後はGate通過

    def test_invalidate_dry_run_changes_nothing_and_missing_label_reported(self):
        self.run_a2()
        before = open(f"{self.tmp}/a2/audit/tts_generation_results.json", "rb").read()
        rep = inv.plan_and_apply(f"{self.tmp}/a2", ["full_story_part2", "nope"], "r", apply=False)
        self.assertEqual(rep["labels"]["nope"]["reason"], "ENTRY_NOT_FOUND")
        self.assertEqual(open(f"{self.tmp}/a2/audit/tts_generation_results.json", "rb").read(), before)
        self.assertTrue(os.path.exists(f"{self.tmp}/a2/narration/full_story_part2.wav"))

    def test_invalidate_kp_label(self):
        d = f"{self.tmp}/a2"
        os.makedirs(f"{d}/audit", exist_ok=True)
        os.makedirs(f"{d}/narration", exist_ok=True)
        open(f"{d}/narration/kp1_en.wav", "wb").write(_wavbytes(3))
        json.dump({"segments": {}, "key_phrases": {"1": {"english": {"status": "OK", "path": f"{d}/narration/kp1_en.wav"}}}},
                  open(f"{d}/audit/tts_generation_results.json", "w", encoding="utf-8"))
        rep = inv.plan_and_apply(d, ["kp1_english"], "r", apply=True)
        self.assertTrue(rep["labels"]["kp1_english"]["ok"])
        cur = json.load(open(f"{d}/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertEqual(cur["key_phrases"]["1"]["english"]["status"], "INVALIDATED_FOR_REGENERATION")

    def test_mandatory_a2_slowdown_still_enforced_for_inherited_entry(self):
        self.run_a2()
        res = self.run_a2(only={"in_one_line"})
        asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")  # slowdown_applied付きの引継ぎentryは通る
        e = res["segments"]["full_story_part1"]
        del e["slowdown_applied"]
        json.dump(res, open(f"{self.tmp}/a2/audit/tts_generation_results.json", "w", encoding="utf-8"))
        with self.assertRaises(RuntimeError) as cm:
            asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")
        self.assertIn("MISSING_MANDATORY_A2_SLOWDOWN", str(cm.exception))

    def test_missing_disfluency_qa_blocks_inherited_entry(self):
        res = self.run_a2()
        res["segments"]["in_one_line"]["disfluency_checked"] = False
        json.dump(res, open(f"{self.tmp}/a2/audit/tts_generation_results.json", "w", encoding="utf-8"))
        res2 = self.run_a2(only={"full_story_part2"})  # in_one_lineは引継ぎ(元entryのdisfluency_checked=Falseをそのまま保持)
        self.assertEqual(res2["segments"]["in_one_line"]["validation_inheritance"]["label"], "REUSED_VALIDATED")
        with self.assertRaises(RuntimeError) as cm:
            asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")
        self.assertIn("MISSING_MANDATORY_DISFLUENCY_QA", str(cm.exception))

    def test_stopped_entry_carried_over_and_blocks(self):
        """OF-X11: STOPPED(+人間承認の前提)entryは--only-segmentsで消えず、statusはGateが判定する。"""
        res = self.run_a2()
        res["segments"]["comment_2"]["status"] = "STOPPED"
        json.dump(res, open(f"{self.tmp}/a2/audit/tts_generation_results.json", "w", encoding="utf-8"))
        res2 = self.run_a2(only={"full_story_part2"})
        self.assertEqual(res2["segments"]["comment_2"]["status"], "STOPPED")
        self.assertTrue(res2["segments"]["comment_2"]["carried_over_unchanged"])
        self.assertNotIn("validation_inheritance", res2["segments"]["comment_2"])
        with self.assertRaises(RuntimeError):
            asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")


class KpInheritanceTest(unittest.TestCase):
    def test_kp_used_form_change_not_inherited(self):
        d = tempfile.mkdtemp(prefix="comp02kp_")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        wav = f"{d}/kp1_en.wav"
        open(wav, "wb").write(_wavbytes(4))
        sv = runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION
        cached_en = {"status": "OK", "asr_verified": True, "canonical_text": "based on", "text": "based on",
                     "path": wav, "sha256": _sha(_wavbytes(4)), "disfluency_checked": True,
                     # KPDUAL-PROD-D2(UDR #139): KP英語phraseの引継ぎは両Provider PASSの保存証跡を要する(fail-closed)
                     "kp_dual_check": {"version": "kp_dual_check_v1", "ok": True, "canonical_text": "based on",
                                       "wav_sha256": _sha(_wavbytes(4)), "primary": {"text": "based on", "pass": True},
                                       "secondary": {"text": "based on", "pass": True}}}
        cached_ja = dict(cached_en, canonical_text="〜に基づいて", text="〜に基づいて")
        cached = {"style_version": sv, "key_phrases": {"1": {"english": cached_en, "japanese_meaning": cached_ja}}}
        with mock.patch.object(runner, "_ONLY_SEGMENTS", {"full_story_part1"}):
            same = runner._generate_or_reuse_kp(cached, 1, "english", wav, lambda: 1 / 0, expected_text="based on")
            self.assertEqual(same["validation_inheritance"]["label"], "REUSED_VALIDATED")
            changed_en = runner._generate_or_reuse_kp(cached, 1, "english", wav, lambda: 1 / 0,
                                                      expected_text="based on interviews")
            self.assertEqual(changed_en["status"], "SKIPPED_NOT_SELECTED")
            changed_ja = runner._generate_or_reuse_kp(cached, 1, "japanese_meaning", wav, lambda: 1 / 0,
                                                      expected_text="〜に基づいた")
            self.assertEqual(changed_ja["status"], "SKIPPED_NOT_SELECTED")


if __name__ == "__main__":
    unittest.main()
