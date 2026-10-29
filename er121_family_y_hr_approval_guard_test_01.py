# -*- coding: utf-8 -*-
"""FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01 委任_01(OPEN-535): 旧Human Review承認のVoice/Style不一致流用の防止test。

API 0・実client生成block・network遮断(er121 runner testと同じharness)。承認scope=『this single segment / this attempt only』を、
照合キーにVoice(+Style)を含めて守る。検査: 旧承認+Voice不一致→不適用で再生成 / Voice一致→適用(正常再利用・resume) / 記録欠落→不適用 /
a2 preview等の非Voice承認は影響なし / resume・再実行で重複生成なし / stamp不正刻印のSTOP / X・Z(共有er011)の既定挙動不変。
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from er121_family_y_runner_01_test_01 import setUpModule, tearDownModule, BLOCK  # noqa: E402,F401
from er121_family_y_audio_chunk_test_01 import Base as _ChunkBase  # noqa: E402
import er003_v1_n3_01_assemble as asm  # noqa: E402
import er011_human_review_lock_01 as lock  # noqa: E402
import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_runner_01 as r  # noqa: E402


def sha(t):
    return hashlib.sha256((t or "").encode("utf-8")).hexdigest()


class Base(_ChunkBase):
    def seed(self, voice="Algieba", stamp="same", approve=("y_voice_1",), extra_approvals=None):
        """先にPuck要求で通常生成(mock)→ y_voice_1の既存entryを『旧Voiceで生成され人間承認された』状態に書換える。"""
        self.generate()
        res = self.results()
        e = res["segments"]["y_voice_1"]
        if voice is None:
            e.pop("voice", None)
            e.pop("y_tts_voice_requested", None)
        else:
            e["voice"] = voice
            e["y_tts_voice_requested"] = voice if stamp == "same" else stamp
        self.save_results(res)
        appr = {k: {"canonical_text_sha256": sha(res["segments"][k]["canonical_text"]), "approved_at": "2026-10-26T06:45:15", "approved_by": "user"}
                for k in approve}
        appr.update(extra_approvals or {})
        self.wj(asm.human_approval_path(self.b1), appr)
        return res

    def approvals(self):
        p = asm.human_approval_path(self.b1)
        return self.rj(p) if os.path.exists(p) else {}

    def quarantine(self):
        p = f"{self.b1}/audit/{ya.HR_APPROVAL_QUARANTINE_FILE}"
        return self.rj(p) if os.path.exists(p) else None

    def tts_labels(self):
        p = f"{self.out}/mock_api_calls.jsonl"
        with open(p, encoding="utf-8") as f:
            rows = [json.loads(x) for x in f if x.strip()]
        return [x["label"] for x in rows if x["kind"] == "tts"]

    def reconcile(self, **kw):
        return ya.reconcile_hr_approvals_for_request(self.b1, "b1b", ya.Y_APPROVED_STYLE_PROFILE, **kw)


class TestVoiceBinding(Base):
    def test_old_approval_with_voice_mismatch_is_not_applied_and_segment_is_regenerated(self):
        self.seed(voice="Algieba")
        out = f"{self.b1}/narration/y_voice_1.wav"
        text = self.results()["segments"]["y_voice_1"]["canonical_text"]
        # 修正前の挙動(根拠): 承認のみで照合する共有ゲートは旧声のまま『人間承認済み』で再生成を阻止する
        self.assertFalse(lock.check_before_generation(out, text, "en")["proceed"])
        before = len(self.tts_labels())
        self.generate()                                    # 正式のgenerate関数(Puck要求)
        self.assertNotIn("y_voice_1", self.approvals())    # 旧承認は退避(不適用)
        q = self.quarantine()["events"][0]["quarantined"][0]
        self.assertEqual((q["segment"], q["reason"], q["approval_voice"], q["requested_voice"]), ("y_voice_1", "Y_HR_APPROVAL_VOICE_MISMATCH", "Algieba", "Puck"))
        self.assertEqual(q["approval_record"]["approved_by"], "user")      # 承認recordは削除せず保全
        e = self.results()["segments"]["y_voice_1"]
        self.assertEqual(e["y_tts_voice_requested"], "Puck")
        self.assertTrue([x for x in self.tts_labels()[before:] if x.startswith("y_voice_1")])             # 実際に再生成が要求された
        self.assertTrue(lock.check_before_generation(out, e["canonical_text"], "en")["proceed"])   # 承認が無いので生成ゲートは通常どおり進む

    def test_matching_voice_approval_is_kept_and_resume_makes_no_duplicate_generation(self):
        self.seed(voice="Puck")
        self.generate()
        self.assertIn("y_voice_1", self.approvals())       # 正常な再利用: 一致する承認は触らない
        self.assertIsNone(self.quarantine())
        before = self.tts_labels()
        self.generate()
        self.assertEqual(self.tts_labels(), before)        # resume: 重複生成なし
        self.assertIsNone(self.quarantine())

    def test_missing_voice_record_is_fail_closed(self):
        self.seed(voice=None)
        res = self.reconcile()
        self.assertEqual([m["reason"] for m in res["quarantined"]], ["Y_HR_APPROVAL_VOICE_UNDETERMINABLE"])
        self.assertNotIn("y_voice_1", self.approvals())

    def test_conflicting_voice_and_stamp_is_undeterminable(self):
        self.seed(voice="Puck", stamp="Algieba")
        self.assertEqual([m["reason"] for m in self.reconcile()["quarantined"]], ["Y_HR_APPROVAL_VOICE_UNDETERMINABLE"])

    def test_reconcile_is_idempotent(self):
        self.seed(voice="Algieba")
        self.assertEqual(len(self.reconcile()["quarantined"]), 1)
        self.assertEqual(self.reconcile()["quarantined"], [])
        self.assertEqual(len(self.quarantine()["events"]), 1)

    def test_non_voice_approvals_are_untouched_even_if_voice_changed(self):
        pv = {"canonical_text_sha256": "x" * 64, "approved_at": "t", "approved_by": "user"}
        self.seed(voice="Algieba", extra_approvals={"preview": pv, "full_story_part1": pv, "kp1_english": pv})
        self.reconcile()
        ap = self.approvals()
        self.assertEqual(sorted(ap), ["full_story_part1", "kp1_english", "preview"])
        self.assertEqual(ap["preview"], pv)

    def test_new_format_y_binding_voice_and_style(self):
        res = self.seed(voice="Puck", approve=())
        text = res["segments"]["y_voice_1"]["canonical_text"]
        cur = ya.current_style_record("b1b", ya.Y_APPROVED_STYLE_PROFILE)
        ya.record_y_human_approval(self.b1, "y_voice_1", text, tts_voice="Puck", style_profile=cur, tts_model="m")
        self.assertEqual(self.reconcile()["quarantined"], [])                      # Voice・Style一致→適用
        self.assertEqual(self.approvals()["y_voice_1"]["y_binding"]["tts_voice"], "Puck")
        self.assertEqual(self.approvals()["y_voice_1"]["canonical_text_sha256"], sha(text))   # 既存形式と上位互換
        self.assertTrue(lock._human_approved(self.b1, "y_voice_1", text))
        ya.record_y_human_approval(self.b1, "y_voice_1", text, tts_voice="Algieba", style_profile=cur, tts_model="m")
        self.assertEqual([m["reason"] for m in self.reconcile()["quarantined"]], ["Y_HR_APPROVAL_VOICE_MISMATCH"])
        other = {"profile_id": "other", "expected_base_sha256": "a", "style_base_sha256": "b"} if cur is None else dict(cur, style_base_sha256="zzz")
        ya.record_y_human_approval(self.b1, "y_voice_1", text, tts_voice="Puck", style_profile=other, tts_model="m")
        self.assertEqual([m["reason"] for m in self.reconcile()["quarantined"]], ["Y_HR_APPROVAL_STYLE_MISMATCH"])

    def test_chunk_approval_is_checked_against_parent_voice(self):
        self.multi_para_parts()
        self.generate()
        res = self.results()
        res["segments"]["y_voice_2_k1"]["voice"] = "Algieba"
        res["segments"]["y_voice_2_k1"]["y_tts_voice_requested"] = "Algieba"
        res["segments"]["y_voice_2_k2"]["voice"] = "Leda"
        self.save_results(res)
        ap = {"y_voice_2_k1": {"canonical_text_sha256": "x", "approved_at": "t", "approved_by": "user"},
              "y_voice_2_k2": {"canonical_text_sha256": "x", "approved_at": "t", "approved_by": "user"}}
        self.wj(asm.human_approval_path(self.b1), ap)
        got = {m["segment"]: m["reason"] for m in self.reconcile()["quarantined"]}
        self.assertEqual(got, {"y_voice_2_k1": "Y_HR_APPROVAL_VOICE_MISMATCH"})   # k2はLeda一致で残る
        self.assertEqual(sorted(self.approvals()), ["y_voice_2_k2"])

    def test_gate_does_not_honor_old_approval_after_voice_change(self):
        self.seed(voice="Algieba")
        res = self.results()
        res["segments"]["y_voice_1"]["status"] = "STOPPED"                   # 旧attempt: ASR NGを人間承認で通した状態
        self.save_results(res)
        entry = self.results()["segments"]["y_voice_1"]
        self.assertEqual(asm._segment_gate_status(entry, "y_voice_1", self.approvals()), "HUMAN_APPROVED")   # 修正前の挙動
        ya.y_style_gate(self.out, "b1b", ya.Y_APPROVED_STYLE_PROFILE)
        self.assertNotIn("y_voice_1", self.approvals())
        self.assertEqual(asm._segment_gate_status(entry, "y_voice_1", self.approvals()), "STOPPED")


class TestStampGuard(unittest.TestCase):
    def test_actual_voice_mismatch_never_gets_the_requested_label(self):
        with self.assertRaises(ya.YAudioStop) as e:
            ya.stamp_requested_voice({"voice": "Algieba"}, "Puck", None, "y_voice_1")
        self.assertIn("Y_VOICE_STAMP_MISMATCH", str(e.exception))

    def test_matching_or_unrecorded_voice_is_stamped_as_before(self):
        self.assertEqual(ya.stamp_requested_voice({"voice": "Puck"}, "Puck")["y_tts_voice_requested"], "Puck")
        self.assertEqual(ya.stamp_requested_voice({"attempts_log": []}, "Puck")["y_tts_voice_requested"], "Puck")

    def test_approval_skipped_result_with_mismatched_approval_voice_stops(self):
        d = tempfile.mkdtemp(prefix="y_hrg_")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        os.makedirs(f"{d}/audit")
        with open(f"{d}/audit/human_approved_segments.json", "w", encoding="utf-8") as f:
            json.dump({"y_voice_1": {"canonical_text_sha256": "x", "y_binding": {"tts_voice": "Algieba", "style_profile": None}}}, f)
        blocked = {"status": "HUMAN_REVIEW_LOCKED", "human_review_lock_status": "HUMAN_APPROVED"}
        with self.assertRaises(ya.YAudioStop) as e:
            ya.stamp_requested_voice(dict(blocked), "Puck", d, "y_voice_1")
        self.assertIn("Y_HR_APPROVAL_VOICE_MISMATCH", str(e.exception))
        self.assertEqual(ya.stamp_requested_voice(dict(blocked), "Algieba", d, "y_voice_1")["y_tts_voice_requested"], "Algieba")


class TestSharedModuleUnchanged(unittest.TestCase):
    """X/Z(共有er011)の既定挙動不変: 本修正はY経路(er121)だけで完結し、共有check_before_generationの署名・承認照合は無変更。"""

    def test_er011_signature_and_text_only_approval_check_unchanged(self):
        self.assertEqual(list(inspect.signature(lock.check_before_generation).parameters), ["out_path", "text", "language"])
        self.assertEqual(list(inspect.signature(lock._human_approved).parameters), ["level_out_dir", "segment_id", "text"])
        d = tempfile.mkdtemp(prefix="xz_hrg_")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        os.makedirs(f"{d}/audit")
        with open(f"{d}/audit/human_approved_segments.json", "w", encoding="utf-8") as f:
            json.dump({"full_story_part1": {"canonical_text_sha256": sha("hello")}}, f)
        # X/Z segment: 従来どおりtext shaのみで承認が効く(voice情報を要求しない)
        self.assertTrue(lock._human_approved(d, "full_story_part1", "hello"))
        self.assertFalse(lock._human_approved(d, "full_story_part1", "changed text"))

    def test_y_guard_is_not_in_shared_modules(self):
        for mod in ("er011_human_review_lock_01.py", "er019_family_x_audio_production_runner_01.py", "er063_family_z_audio_01.py", "er003_v1_n3_01_assemble.py"):
            with open(os.path.join(ROOT, mod), encoding="utf-8") as f:
                self.assertNotIn("y_binding", f.read(), mod)

    def test_y_scope_covers_only_y_body_segments(self):
        self.assertEqual(ya._y_approval_scope_key("y_voice_1"), "y_voice_1")
        self.assertEqual(ya._y_approval_scope_key("y_voice_1_k2"), "y_voice_1")
        for k in ("preview", "comment_1", "kp1_english", "full_story_part1", "topic_intro"):
            self.assertIsNone(ya._y_approval_scope_key(k), k)

    def test_no_network_or_real_client_attempts(self):
        self.assertEqual((BLOCK["net"], BLOCK["client"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
