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
             mock.patch.object(tg.en_validator, "classify_asr_match", wraps=tg.en_validator.classify_asr_match):
            # AUW 委任_05(J7): 減速後再検証は統一judge(EN adapter)経由になり、adapterのP-chainがclassifyの戻り値の構造
            # (protected等)を使うため、旧Mock(should_pass=True)では形が合わない。本testの主題(sha256の更新)は分類結果に
            # 依存しないので、実classify(原稿==転写でEXACT_MATCH -> Primary PASS、Secondary不呼出)へwrapsする。
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
             mock.patch.object(tg.en_validator, "classify_asr_match", wraps=tg.en_validator.classify_asr_match):
            # AUW 委任_05(J7): 減速後再検証は統一judge(EN adapter)経由になり、adapterのP-chainがclassifyの戻り値の構造
            # (protected等)を使うため、旧Mock(should_pass=True)では形が合わない。本testの主題(sha256の更新)は分類結果に
            # 依存しないので、実classify(原稿==転写でEXACT_MATCH -> Primary PASS、Secondary不呼出)へwrapsする。
            updated = tg.apply_a2_slowdown_postprocess(self.name, self.tmp_dir, "some text", result)
        self.assertIsNone(updated["sha256"])


class SlowdownJudgeLrRewrittenWarningTests(ApplyA2SlowdownPostprocessSha256Tests):
    """委任_05 F2(CURRENT_SPEC.md:2925): Std L4経路でLR採用(書換え後の文)のattemptは、減速後の最終judgeにも必ずLR_REWRITTEN警告が付く。
    判定結果(PASS/NG)は不変、警告付与のみ。LRなしは警告なし(従来どおり)。"""

    def _run(self, **kw):
        result = {"status": "OK", "sha256": self.pre_sha256, "duration_seconds": 10.0, "text": "some text"}
        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_apply_a2_slowdown),              mock.patch.object(tg.routing, "transcribe", return_value=("some text", None)):
            return tg.apply_a2_slowdown_postprocess(self.name, self.tmp_dir, "some text", result, **kw)

    def test_lr_block_attempt_final_judgement_has_lr_rewritten_warning(self):
        out = self._run(lock_text="original script text")        # LR block内: 送信文(書換え後)!=Lock key(元原稿)
        self.assertEqual(out["status"], "OK")                     # 判定結果は不変(PASS)
        j = out["asr_judgement"]
        self.assertIn("LR_REWRITTEN", j["warnings"])
        self.assertEqual(j["state"], "PASS_WITH_WARNING")

    def test_no_lr_has_no_lr_rewritten_warning(self):
        out = self._run()
        self.assertEqual(out["status"], "OK")
        self.assertNotIn("LR_REWRITTEN", (out["asr_judgement"] or {}).get("warnings") or [])

    def test_unified_judge_default_script_version_is_v0(self):
        import inspect
        self.assertEqual(inspect.signature(tg._post_slowdown_unified_judge).parameters["script_version"].default, "v0")


if __name__ == "__main__":
    unittest.main()
