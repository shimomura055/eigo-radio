# ============================================================
# er008_n8_qa_hardening_21_gate_test_01.py
# ER-008-N8-FINAL-QA-HARDENING-21 Item 1/7: Assemble Gateの
# disfluency QA必須evidence確認・asset hash staleness確認の回帰テスト。
# ============================================================
# No.8のA2 Key Phrase 2("uneven choice")が、disfluency QA配線(ER-18/19)
# より前に生成されたMaster Audio Store資産のまま、disfluency_checked
# フィールドを一切持たずにAssembleへ採用されていた実インシデントを、
# fixtureとして再現する。
import hashlib
import json
import os
import shutil
import tempfile
import unittest

import er003_v1_n3_01_assemble as asm


def _write_results(out_dir: str, segments: dict = None, key_phrases: dict = None) -> None:
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": segments or {}, "key_phrases": key_phrases or {}}, f, ensure_ascii=False, indent=2)


class MandatoryDisfluencyQaTests(unittest.TestCase):
    def test_non_mandatory_segment_is_never_flagged(self):
        self.assertFalse(asm._segment_missing_mandatory_disfluency_qa("full_story_part1", {"status": "OK"}, "B1"))

    def test_mandatory_segment_without_evidence_is_flagged(self):
        # No.8のkp2実例: attempts_logにdisfluency_checkedが無かった旧形式
        # (このfixtureはtop-levelにも無い、より古い形式を再現)。
        self.assertTrue(asm._segment_missing_mandatory_disfluency_qa("preview", {"status": "OK"}, "B1"))

    def test_mandatory_segment_with_false_evidence_is_flagged(self):
        self.assertTrue(asm._segment_missing_mandatory_disfluency_qa(
            "comment_1", {"status": "OK", "disfluency_checked": False}, "B1"))

    def test_mandatory_segment_with_true_evidence_is_not_flagged(self):
        self.assertFalse(asm._segment_missing_mandatory_disfluency_qa(
            "in_one_line", {"status": "OK", "disfluency_checked": True}, "B1"))

    def test_key_phrase_english_subentry_is_mandatory_on_both_levels(self):
        self.assertTrue(asm._segment_missing_mandatory_disfluency_qa("kp2_english", {"status": "OK"}, "A2"))
        self.assertTrue(asm._segment_missing_mandatory_disfluency_qa("kp2_english", {"status": "OK"}, "B1"))
        self.assertFalse(asm._segment_missing_mandatory_disfluency_qa(
            "kp2_english", {"status": "OK", "disfluency_checked": True}, "A2"))

    def test_key_phrase_japanese_subentry_is_not_mandatory(self):
        self.assertFalse(asm._segment_missing_mandatory_disfluency_qa("kp2_japanese", {"status": "OK"}, "B1"))

    def test_a2_preview_and_comments_are_japanese_and_not_mandatory(self):
        # disfluency QA(faster-whisper)は英語専用。A2のpreview/comment_1-4は
        # 日本語音声のため、disfluency_checkedは常にFalseで記録される
        # (設計上パス不能)。level非依存にすると恒久的にA2 Gateが通らなく
        # なるバグを実装中に発見・修正した(この回帰テストで固定する)。
        for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
            self.assertFalse(asm._segment_missing_mandatory_disfluency_qa(
                name, {"status": "OK", "disfluency_checked": False}, "A2"))

    def test_b1_preview_and_comments_are_english_and_mandatory(self):
        for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
            self.assertTrue(asm._segment_missing_mandatory_disfluency_qa(name, {"status": "OK"}, "B1"))

    def test_a2_point_headings_and_in_one_line_are_english_and_mandatory(self):
        for name in ("point_one_heading", "point_two_heading", "in_one_line"):
            self.assertTrue(asm._segment_missing_mandatory_disfluency_qa(name, {"status": "OK"}, "A2"))


class AssetHashStaleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="er008_hash_stale_test_")
        self.narration_dir = f"{self.tmp}/narration"
        os.makedirs(self.narration_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_wav(self, name: str, content: bytes) -> str:
        path = f"{self.narration_dir}/{name}"
        with open(path, "wb") as f:
            f.write(content)
        return path

    def test_no_path_or_hash_is_never_stale(self):
        self.assertFalse(asm._segment_asset_hash_stale({"status": "OK"}, self.narration_dir))

    def test_matching_hash_is_not_stale(self):
        path = self._write_wav("kp2_en.wav", b"actual audio bytes")
        sha = hashlib.sha256(b"actual audio bytes").hexdigest()
        self.assertFalse(asm._segment_asset_hash_stale({"path": path, "sha256": sha}, self.narration_dir))

    def test_mismatched_hash_is_stale(self):
        # 今回のセッション自体で発生した「.bakから手動でarticle.md/parts.
        # jsonを復元したがJSON記録は更新前のまま」に相当するケース。
        path = self._write_wav("kp2_en.wav", b"a different file was placed here later")
        stale_recorded_sha = hashlib.sha256(b"actual audio bytes").hexdigest()
        self.assertTrue(asm._segment_asset_hash_stale(
            {"path": path, "sha256": stale_recorded_sha}, self.narration_dir))


class No8Kp2IncidentReproductionTests(unittest.TestCase):
    """No.8実インシデントの再現: kp2_en(uneven choice)がdisfluency QA
    配線前に生成されたためdisfluency_checkedフィールドを持たず、
    status=="OK"だけでVALIDATED扱いになりAssembleへ到達しようとする
    ケースを、Gateがblockすることを確認する。"""

    def setUp(self):
        self.out_dir = tempfile.mkdtemp(prefix="er008_kp2_incident_test_")

    def tearDown(self):
        shutil.rmtree(self.out_dir, ignore_errors=True)

    def test_gate_blocks_key_phrase_missing_disfluency_evidence(self):
        _write_results(self.out_dir, key_phrases={
            "2": {"english": {"status": "OK", "text": "uneven choice"},
                  "japanese_meaning": {"status": "OK", "text": "不均衡な選択"}},
        })
        with self.assertRaises(RuntimeError) as ctx:
            asm.verify_episode_audio_validation_gate(self.out_dir, "A2")
        self.assertIn("kp2_english", str(ctx.exception))
        self.assertIn("MISSING_MANDATORY_DISFLUENCY_QA", str(ctx.exception))

    def test_gate_passes_once_disfluency_evidence_present(self):
        _write_results(self.out_dir, key_phrases={
            "2": {"english": {"status": "OK", "text": "uneven choice", "disfluency_checked": True},
                  "japanese_meaning": {"status": "OK", "text": "不均衡な選択"}},
        })
        asm.verify_episode_audio_validation_gate(self.out_dir, "A2")  # raiseしなければOK


if __name__ == "__main__":
    unittest.main()
