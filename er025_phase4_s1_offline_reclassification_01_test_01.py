# ============================================================
# er025_phase4_s1_offline_reclassification_01_test_01.py
# PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-
# LIKE-01 修正1回目(S1スクリプトのunit test)
# ============================================================
# API呼び出し: 0(read-only、実TTS/ASR/LLM呼び出しなし)。本番の
# er021_output/.../telemetry.jsonl、er006_output/.../human_review_
# queue.jsonlは一切読み書きしない(専用の一時fixtureファイルのみ使う)。
from __future__ import annotations

import json
import os
import shutil
import unittest

import er025_phase4_s1_offline_reclassification_01 as s1

_TMP_DIR = "er025_output/_test_phase4_s1_offline_tmp"
_TMP_TELEMETRY = f"{_TMP_DIR}/telemetry.jsonl"
_TMP_HUMAN_REVIEW = f"{_TMP_DIR}/human_review_queue.jsonl"


class S1OfflineReclassificationTests(unittest.TestCase):
    def setUp(self):
        os.makedirs(_TMP_DIR, exist_ok=True)
        self._orig_telemetry_path = s1.TELEMETRY_PATH
        self._orig_human_review_path = s1.HUMAN_REVIEW_PATH
        s1.TELEMETRY_PATH = _TMP_TELEMETRY
        s1.HUMAN_REVIEW_PATH = _TMP_HUMAN_REVIEW

    def tearDown(self):
        s1.TELEMETRY_PATH = self._orig_telemetry_path
        s1.HUMAN_REVIEW_PATH = self._orig_human_review_path
        if os.path.exists(_TMP_DIR):
            shutil.rmtree(_TMP_DIR)

    def _write_jsonl(self, path: str, records: list[dict]):
        with open(path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def test_missing_files_yield_zero_denominator(self):
        result = s1.reclassify_all()
        self.assertEqual(result["summary"]["denominator_total"], 0)
        self.assertEqual(result["flips"], [])

    def test_telemetry_flip_detected_via_loanword(self):
        # 記録当時(修正前コード相当)はTRUE_CONTENT_MISMATCHだったが、
        # 現行コード(loanword_flags)ではminaudiereがentity_likeとなり
        # ASR_VALIDATION_UNCERTAINへ反転するケース。
        self._write_jsonl(_TMP_TELEMETRY, [
            {"canonical": "Chanel showed a novelty minaudière at the event.",
             "asr": "Chanel showed a novelty minidier at the event.",
             "role": "COMMENT", "classification": "TRUE_CONTENT_MISMATCH", "sub_reason": "content_word"},
        ])
        result = s1.reclassify_all()
        self.assertEqual(result["summary"]["denominator_total"], 1)
        self.assertEqual(len(result["flips"]), 1)
        self.assertEqual(result["flips"][0]["entity_like_source"], ["loanword"])
        self.assertTrue(result["flips"][0]["loanword_only_flip_candidate"])
        self.assertEqual(result["summary"]["of_which_loanword_only_flip_candidate_hidden_general_word_risk"], 1)

    def test_true_negative_content_error_does_not_flip(self):
        # 一般語の内容誤り(increase/decrease)は反転しない(安全側回帰なし)。
        self._write_jsonl(_TMP_TELEMETRY, [
            {"canonical": "Prices tend to increase after the trial period.",
             "asr": "Prices tend to decrease after the trial period.",
             "role": "COMMENT", "classification": "TRUE_CONTENT_MISMATCH", "sub_reason": "content_word"},
        ])
        result = s1.reclassify_all()
        self.assertEqual(result["summary"]["denominator_total"], 1)
        self.assertEqual(result["flips"], [])

    def test_human_review_queue_steps_are_counted_individually(self):
        self._write_jsonl(_TMP_HUMAN_REVIEW, [
            {"canonical_text": "Chanel showed a novelty minaudière at the event.",
             "wav_path": "dummy.wav", "final_status": "HUMAN_REVIEW_REQUIRED",
             "steps": [
                 {"step": "primary_1", "provider": "openai_asr",
                  "text": "Chanel showed a novelty minidier at the event.",
                  "classification": "TRUE_CONTENT_MISMATCH"},
                 {"step": "primary_2", "provider": "openai_asr",
                  "text": None, "classification": "TTS_FAILURE"},
             ]},
        ])
        result = s1.reclassify_all()
        # "text": Noneのstep(primary_2)はスキップされ、primary_1のみ対象になる。
        self.assertEqual(result["summary"]["denominator_total"], 1)
        self.assertEqual(len(result["flips"]), 1)
        self.assertEqual(result["flips"][0]["source_step"], "primary_1")

    def test_read_only_does_not_modify_input_files(self):
        records = [
            {"canonical": "Chanel showed a novelty minaudière at the event.",
             "asr": "Chanel showed a novelty minidier at the event.",
             "role": "COMMENT", "classification": "TRUE_CONTENT_MISMATCH", "sub_reason": "content_word"},
        ]
        self._write_jsonl(_TMP_TELEMETRY, records)
        with open(_TMP_TELEMETRY, encoding="utf-8") as f:
            before = f.read()
        s1.reclassify_all()
        with open(_TMP_TELEMETRY, encoding="utf-8") as f:
            after = f.read()
        self.assertEqual(before, after, "S1スクリプトは入力ファイルを一切書き換えないこと(read-only)")

    def test_run_writes_only_to_own_output_dir(self):
        self._write_jsonl(_TMP_TELEMETRY, [
            {"canonical": "Prices tend to increase after the trial period.",
             "asr": "Prices tend to decrease after the trial period.",
             "role": "COMMENT", "classification": "TRUE_CONTENT_MISMATCH", "sub_reason": "content_word"},
        ])
        orig_out_dir = s1.OUT_DIR
        tmp_out_dir = f"{_TMP_DIR}/out"
        s1.OUT_DIR = tmp_out_dir
        try:
            s1.run()
            self.assertTrue(os.path.exists(os.path.join(tmp_out_dir, "summary.json")))
            self.assertTrue(os.path.exists(os.path.join(tmp_out_dir, "flips_detail.jsonl")))
        finally:
            s1.OUT_DIR = orig_out_dir


def run():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(S1OfflineReclassificationTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run()
