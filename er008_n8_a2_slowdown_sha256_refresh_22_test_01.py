# ============================================================
# er008_n8_a2_slowdown_sha256_refresh_22_test_01.py
# ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22: apply_a2_slowdown_
# postprocess()がtime-stretchでout_pathの中身を差し替えた後もsha256を
# 再計算していなかったbugの回帰テスト。No.8実データ(A2 full_story_
# part1/part2の再生成)で、Assemble Gateの_segment_asset_hash_stale()が
# 常にASSET_HASH_MISMATCHでblockしてしまう実害として発見した。
# 実TTS/ASR/FFmpegは呼ばず、a2_slowdown.apply_a2_slowdown/routing.
# transcribe/en_validator.classify_asr_matchをmockする。
# ============================================================
import hashlib
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_tts_generate as tg


class ApplyA2SlowdownPostprocessSha256Tests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er008_a2_slowdown_sha256_test_")
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)
        self.name = "full_story_part1"
        self.out_path = f"{self.tmp_dir}/{self.name}.wav"
        with open(self.out_path, "wb") as f:
            f.write(b"PRE_SLOWDOWN_FAKE_WAV_BYTES")
        with open(self.out_path, "rb") as f:
            self.pre_sha256 = hashlib.sha256(f.read()).hexdigest()

    def _fake_apply_a2_slowdown(self, src_path, dst_path):
        # time-stretch後は実際に音声の中身(バイト列)が変わる。ここでは
        # 実FFmpegを呼ばず、別内容を書き込むことで同じ効果を再現する。
        with open(dst_path, "wb") as f:
            f.write(b"POST_SLOWDOWN_FAKE_WAV_BYTES_DIFFERENT_CONTENT")
        return {"src_duration_seconds": 10.0, "dst_duration_seconds": 10.6}

    def test_sha256_is_refreshed_to_match_post_slowdown_file(self):
        result = {"status": "OK", "sha256": self.pre_sha256, "duration_seconds": 10.0,
                  "trim_info": {"raw_duration_seconds": 10.0, "trimmed_duration_seconds": 9.8,
                                 "leading_margin_retained_seconds": 0.1, "trailing_margin_retained_seconds": 0.1,
                                 "raw_leading_silence_seconds": 0.05, "raw_trailing_silence_seconds": 0.05}}
        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_apply_a2_slowdown), \
             mock.patch.object(tg.routing, "transcribe", return_value=("some text", None)), \
             mock.patch.object(tg.en_validator, "classify_asr_match") as mock_classify:
            mock_classify.return_value = mock.Mock(should_pass=True, classification="EXACT_MATCH")
            updated = tg.apply_a2_slowdown_postprocess(self.name, self.tmp_dir, "some text", result)

        self.assertEqual(updated["status"], "OK")
        with open(self.out_path, "rb") as f:
            actual_file_sha256 = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(updated["sha256"], actual_file_sha256,
                          "post-process後のsha256は実際のout_pathの中身と一致していなければならない")
        self.assertNotEqual(updated["sha256"], self.pre_sha256,
                             "slowdown前のsha256のまま取り残されてはならない(ASSET_HASH_MISMATCH bugの再発防止)")

    def test_sha256_stays_none_when_not_previously_set(self):
        # sha256が元々記録されていない(=呼び出し元がNoneのまま)場合は、
        # このpost-process層で新規にsha256計算ロジックを増やさない
        # (既存のNone許容パターン[Assemble Gate側でNoneは"証跡なし"として
        # スキップ]を変えない、最小差分の修正であることを保証する)。
        result = {"status": "OK", "sha256": None, "duration_seconds": 10.0}
        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_apply_a2_slowdown), \
             mock.patch.object(tg.routing, "transcribe", return_value=("some text", None)), \
             mock.patch.object(tg.en_validator, "classify_asr_match") as mock_classify:
            mock_classify.return_value = mock.Mock(should_pass=True, classification="EXACT_MATCH")
            updated = tg.apply_a2_slowdown_postprocess(self.name, self.tmp_dir, "some text", result)
        self.assertIsNone(updated["sha256"])


if __name__ == "__main__":
    unittest.main()
