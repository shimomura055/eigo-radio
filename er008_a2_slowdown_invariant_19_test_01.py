# ============================================================
# er008_a2_slowdown_invariant_19_test_01.py
# ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19 Item 5-A: A2 6% slowdown
# 必須post-processのAssemble前invariant gateの回帰テスト。
# ============================================================
# No.8のpoint_one_headingが、Human Review Lock経由の承認により6%
# slowdownという必須post-processを一度も受けないままVALIDATED扱いで
# Assembleへ到達していた実際の事故を、fixtureとして再現する。
import json
import os
import shutil
import tempfile
import unittest

import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_tts_generate as n3_tts


def _write_results(out_dir: str, segments: dict) -> None:
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": segments, "key_phrases": {}}, f, ensure_ascii=False, indent=2)


class SegmentMissingMandatoryA2SlowdownTests(unittest.TestCase):
    def test_non_target_segment_is_never_flagged(self):
        self.assertFalse(asm._segment_missing_mandatory_a2_slowdown("comment_1", {"status": "OK"}))

    def test_target_segment_without_slowdown_evidence_is_flagged(self):
        self.assertIn("point_one_heading", n3_tts.A2_SLOWDOWN_TARGET_SEGMENTS)
        self.assertTrue(asm._segment_missing_mandatory_a2_slowdown("point_one_heading", {"status": "OK"}))

    def test_target_segment_with_slowdown_evidence_is_not_flagged(self):
        self.assertFalse(asm._segment_missing_mandatory_a2_slowdown(
            "point_one_heading", {"status": "OK", "slowdown_applied": True}))

    def test_target_segment_with_slowdown_applied_false_is_flagged(self):
        self.assertTrue(asm._segment_missing_mandatory_a2_slowdown(
            "point_one_heading", {"status": "OK", "slowdown_applied": False}))

    def test_target_segment_falls_back_to_original_wav_evidence(self):
        # No.8実データ横断調査で発見: 「resume」系scriptが結果を引き継いだ
        # segmentは、実際にはslowdownを受けていてもslowdown_appliedを
        # 記録していない場合がある。{name}_original.wavの現存を第二の
        # evidenceとして受け入れ、既存の正しい音声を誤ってblockしない。
        tmp = tempfile.mkdtemp(prefix="er008_a2_invariant_fallback_test_")
        try:
            os.makedirs(f"{tmp}/narration", exist_ok=True)
            open(f"{tmp}/narration/full_story_part1_original.wav", "wb").close()
            self.assertFalse(asm._segment_missing_mandatory_a2_slowdown(
                "full_story_part1", {"status": "OK", "resumed_from_existing_file": True}, f"{tmp}/narration"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_target_segment_with_neither_evidence_is_flagged(self):
        tmp = tempfile.mkdtemp(prefix="er008_a2_invariant_no_evidence_test_")
        try:
            os.makedirs(f"{tmp}/narration", exist_ok=True)
            self.assertTrue(asm._segment_missing_mandatory_a2_slowdown(
                "full_story_part1", {"status": "OK"}, f"{tmp}/narration"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class AssembleGateNo8IncidentReproductionTests(unittest.TestCase):
    """No.8実インシデントの再現: point_one_headingがHuman Review Lock
    経由で承認され(status書き換えなしでcanonical_text一致による承認)、
    slowdown_appliedフィールドが無いままVALIDATED扱いでAssembleへ
    到達しようとするケースを、A2レベルのgateがblockすることを確認する。"""

    def setUp(self):
        self.out_dir = tempfile.mkdtemp(prefix="er008_a2_invariant_test_")

    def tearDown(self):
        shutil.rmtree(self.out_dir, ignore_errors=True)

    def test_a2_gate_blocks_validated_segment_missing_slowdown_evidence(self):
        _write_results(self.out_dir, {
            "point_one_heading": {"status": "OK", "canonical_text": "First point."},
            "comment_1": {"status": "OK"},
        })
        with self.assertRaises(RuntimeError) as ctx:
            asm.verify_episode_audio_validation_gate(self.out_dir, "A2")
        self.assertIn("MISSING_MANDATORY_A2_SLOWDOWN", str(ctx.exception))
        self.assertIn("point_one_heading", str(ctx.exception))

    def test_a2_gate_passes_when_slowdown_applied_is_true(self):
        _write_results(self.out_dir, {
            "point_one_heading": {"status": "OK", "canonical_text": "First point.", "slowdown_applied": True},
            "full_story_part1": {"status": "OK", "slowdown_applied": True},
            "comment_1": {"status": "OK"},
        })
        asm.verify_episode_audio_validation_gate(self.out_dir, "A2")  # raiseしなければOK

    def test_b1_gate_does_not_apply_slowdown_invariant(self):
        # B1にはA2の6% slowdownという概念自体が存在しない(CURRENT_SPEC.md
        # 「B1にはこの追加指示を一切渡さない」)ため、B1レベルのgateは
        # slowdown_appliedの有無を一切見ない。
        _write_results(self.out_dir, {"point_one_heading": {"status": "OK", "canonical_text": "First point."}})
        asm.verify_episode_audio_validation_gate(self.out_dir, "B1")  # raiseしなければOK

    def test_human_approved_segment_missing_slowdown_is_still_blocked(self):
        # No.8の実際のインシデント形: status=ASR_VALIDATION_UNCERTAINだが
        # record_human_approval()による承認記録があり、HUMAN_APPROVED
        # 扱いになる場合でも、slowdown_appliedが無ければblockされること。
        canonical = "First point."
        _write_results(self.out_dir, {
            "point_one_heading": {"status": "ASR_VALIDATION_UNCERTAIN", "canonical_text": canonical},
        })
        asm.record_human_approval(self.out_dir, "point_one_heading", canonical)
        with self.assertRaises(RuntimeError) as ctx:
            asm.verify_episode_audio_validation_gate(self.out_dir, "A2")
        self.assertIn("MISSING_MANDATORY_A2_SLOWDOWN", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
