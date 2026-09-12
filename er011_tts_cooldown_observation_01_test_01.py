#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
er011_tts_cooldown_observation_01_test_01.py

管理ID: TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01

Offline test(API呼び出し0件、¥0)。TTS/ASRは一切呼ばず、`single_attempt_fn`は
すべてモック関数に差し替える。待機は`sleep_fn`を差し替えて時間短縮する
(`TTS_COOLDOWN_SECONDS=1`相当をテスト内で明示的に渡す/環境変数経由の両方を
検証する)。

pin対象:
  1. 既定OFF(TTS_COOLDOWN_OBSERVATION未設定)ではno-op(4回目もsleepも実行しない)
  2. 3回連続NG以外は対象外(INELIGIBLE、no-op)
  3. パラメータ同一性検証: 待機前後で変化なし -> 4回目実行、変化あり -> 4回目スキップ
  4. 4回目結果PASSでも自動採用しない(auto_adopted_to_production=Falseを常に記録)
  5. 観測レコードがobservations.jsonlへ追記されること
  6. run_batch_observations()が複数segmentを並列に処理し、直列実行より
     wall time が短いこと(独立待機の裏付け)
"""

from __future__ import annotations

import json
import os
import shutil
import time
import unittest
from unittest import mock

import er011_tts_cooldown_observation_01 as m

TEST_OUT_DIR = "er011_output/tts_cooldown_observation_01/_test_scratch"
TEST_OBS_PATH = f"{TEST_OUT_DIR}/observations.jsonl"


def _three_ng_records():
    return [
        {"verified": False, "audio_classification": "TRUE_CONTENT_MISMATCH", "asr_text": f"ng text {i}",
         "route": "standard", "model": "gemini-2.5-pro-preview-tts", "voice": "Aoede"}
        for i in range(3)
    ]


class TtsCooldownObservationTest(unittest.TestCase):
    def setUp(self):
        self._orig_out_dir = m.OUT_DIR
        self._orig_obs_path = m.OBSERVATIONS_PATH
        m.OUT_DIR = TEST_OUT_DIR
        m.OBSERVATIONS_PATH = TEST_OBS_PATH
        if os.path.exists(TEST_OUT_DIR):
            shutil.rmtree(TEST_OUT_DIR)
        self._env_patch = mock.patch.dict(os.environ, {}, clear=False)
        self._env_patch.start()
        os.environ.pop("TTS_COOLDOWN_OBSERVATION", None)
        os.environ.pop("TTS_COOLDOWN_SECONDS", None)

    def tearDown(self):
        self._env_patch.stop()
        m.OUT_DIR = self._orig_out_dir
        m.OBSERVATIONS_PATH = self._orig_obs_path
        if os.path.exists(TEST_OUT_DIR):
            shutil.rmtree(TEST_OUT_DIR)

    def _read_last_record(self):
        with open(TEST_OBS_PATH, encoding="utf-8") as f:
            lines = [line for line in f if line.strip()]
        return json.loads(lines[-1])

    # 1. 既定OFF -> no-op
    def test_default_off_is_noop(self):
        calls = {"single_attempt": 0, "sleep": 0}

        def fake_single_attempt():
            calls["single_attempt"] += 1
            return {"status": "OK", "asr_verified": True}

        def fake_sleep(seconds):
            calls["sleep"] += 1

        record = m.observe_after_three_consecutive_ng(
            level_dir="er003_output/dummy/b1b", segment_id="point_one",
            canonical_text="hello world", language="en",
            three_attempt_records=_three_ng_records(),
            params={"voice": "Aoede", "model": "gemini-2.5-pro-preview-tts"},
            single_attempt_fn=fake_single_attempt,
            sleep_fn=fake_sleep,
        )
        self.assertEqual(record["status"], "SKIPPED_DISABLED")
        self.assertFalse(record["fourth_attempt_executed"])
        self.assertEqual(calls["single_attempt"], 0)
        self.assertEqual(calls["sleep"], 0)
        self.assertEqual(self._read_last_record()["status"], "SKIPPED_DISABLED")

    # 2. 3回連続NG以外は対象外
    def test_ineligible_when_not_exactly_three_ng(self):
        os.environ["TTS_COOLDOWN_OBSERVATION"] = "1"
        two_ng_and_one_pass = _three_ng_records()[:2] + [{"verified": True}]
        calls = {"single_attempt": 0}

        def fake_single_attempt():
            calls["single_attempt"] += 1
            return {"status": "OK"}

        record = m.observe_after_three_consecutive_ng(
            level_dir="d", segment_id="seg", canonical_text="t", language="en",
            three_attempt_records=two_ng_and_one_pass,
            params={"voice": "Aoede"},
            single_attempt_fn=fake_single_attempt,
            sleep_fn=lambda s: None,
        )
        self.assertEqual(record["status"], "INELIGIBLE_NOT_EXACTLY_THREE_CONSECUTIVE_NG")
        self.assertEqual(calls["single_attempt"], 0)

    # 3a. パラメータ不変 -> 4回目実行、PASS
    def test_enabled_params_unchanged_fourth_pass(self):
        os.environ["TTS_COOLDOWN_OBSERVATION"] = "1"
        calls = {"single_attempt": 0, "sleep_seconds": []}

        def fake_single_attempt(out_path):
            calls["single_attempt"] += 1
            return {"status": "OK", "asr_verified": True, "audio_classification": None}

        def fake_sleep(seconds):
            calls["sleep_seconds"].append(seconds)

        live_params = {"model_const": "gemini-2.5-pro-preview-tts", "voice_const": "Aoede"}

        record = m.observe_after_three_consecutive_ng(
            level_dir="er003_output/dummy/b1b", segment_id="point_one",
            canonical_text="hello world", language="en",
            three_attempt_records=_three_ng_records(),
            params={"voice": "Aoede", "model": "gemini-2.5-pro-preview-tts", "route": "standard"},
            single_attempt_fn=fake_single_attempt,
            single_attempt_kwargs={"out_path": "er011_output/tts_cooldown_observation_01/trial_only/point_one.wav"},
            capture_live_params_fn=lambda: dict(live_params),
            cooldown_seconds=1,
            sleep_fn=fake_sleep,
        )
        self.assertEqual(record["status"], "OBSERVED")
        self.assertTrue(record["fourth_attempt_executed"])
        self.assertEqual(record["fourth_attempt_result_status"], "PASS")
        self.assertTrue(record["params_unchanged_verified"])
        self.assertEqual(calls["single_attempt"], 1)
        self.assertEqual(calls["sleep_seconds"], [1])
        # 4回目PASSでも自動採用しない
        self.assertFalse(record["auto_adopted_to_production"])
        self.assertFalse(record["production_state_modified"])
        self.assertTrue(record["no_human_intervention"])
        self.assertIn("review_lock.approve_regenerate", record["adoption_note"])

    # 3b. パラメータ不変 -> 4回目実行、NG
    def test_enabled_params_unchanged_fourth_ng(self):
        os.environ["TTS_COOLDOWN_OBSERVATION"] = "1"

        def fake_single_attempt_ng():
            return {"status": "STOPPED", "asr_verified": False, "reason": "still mismatched",
                     "audio_classification": "TRUE_CONTENT_MISMATCH"}

        record = m.observe_after_three_consecutive_ng(
            level_dir="d", segment_id="seg2", canonical_text="t", language="en",
            three_attempt_records=_three_ng_records(),
            params={"voice": "Aoede"},
            single_attempt_fn=fake_single_attempt_ng,
            cooldown_seconds=1,
            sleep_fn=lambda s: None,
        )
        self.assertEqual(record["status"], "OBSERVED")
        self.assertEqual(record["fourth_attempt_result_status"], "NG")
        self.assertFalse(record["auto_adopted_to_production"])

    # 4. パラメータ変化(live params)ありなら4回目スキップ・観測無効化
    def test_param_change_invalidates_observation_and_skips_fourth_attempt(self):
        os.environ["TTS_COOLDOWN_OBSERVATION"] = "1"
        calls = {"single_attempt": 0}
        live_calls = {"n": 0}

        def fake_single_attempt():
            calls["single_attempt"] += 1
            return {"status": "OK"}

        def changing_live_params():
            live_calls["n"] += 1
            # 1回目(待機前)と2回目(待機後)で異なる値を返す -> 変更検知させる
            return {"model_const": f"model-v{live_calls['n']}"}

        record = m.observe_after_three_consecutive_ng(
            level_dir="d", segment_id="seg3", canonical_text="t", language="en",
            three_attempt_records=_three_ng_records(),
            params={"voice": "Aoede"},
            single_attempt_fn=fake_single_attempt,
            capture_live_params_fn=changing_live_params,
            cooldown_seconds=1,
            sleep_fn=lambda s: None,
        )
        self.assertEqual(record["status"], "OBSERVATION_INVALIDATED_PARAM_CHANGE")
        self.assertFalse(record["fourth_attempt_executed"])
        self.assertEqual(calls["single_attempt"], 0)
        self.assertFalse(record["params_unchanged_verified"])

    # 環境変数TTS_COOLDOWN_SECONDS経由でも待機秒数を制御できること
    def test_cooldown_seconds_from_env_var(self):
        os.environ["TTS_COOLDOWN_OBSERVATION"] = "1"
        os.environ["TTS_COOLDOWN_SECONDS"] = "2"
        sleep_calls = []

        def fake_single_attempt():
            return {"status": "OK"}

        m.observe_after_three_consecutive_ng(
            level_dir="d", segment_id="seg4", canonical_text="t", language="en",
            three_attempt_records=_three_ng_records(),
            params={"voice": "Aoede"},
            single_attempt_fn=fake_single_attempt,
            sleep_fn=lambda s: sleep_calls.append(s),
        )
        self.assertEqual(sleep_calls, [2.0])

    # 5. observations.jsonlへの追記(複数回呼んでも上書きされず追記されること)
    def test_appends_to_observations_jsonl(self):
        os.environ["TTS_COOLDOWN_OBSERVATION"] = "1"

        def fake_single_attempt():
            return {"status": "OK"}

        for i in range(3):
            m.observe_after_three_consecutive_ng(
                level_dir="d", segment_id=f"seg_append_{i}", canonical_text="t", language="en",
                three_attempt_records=_three_ng_records(),
                params={"voice": "Aoede"},
                single_attempt_fn=fake_single_attempt,
                cooldown_seconds=0,
                sleep_fn=lambda s: None,
            )
        with open(TEST_OBS_PATH, encoding="utf-8") as f:
            lines = [line for line in f if line.strip()]
        self.assertEqual(len(lines), 3)
        segment_ids = [json.loads(line)["segment_id"] for line in lines]
        self.assertEqual(segment_ids, ["seg_append_0", "seg_append_1", "seg_append_2"])

    # 6. run_batch_observations: 独立並列待機(直列実行より明確に速いこと)
    def test_run_batch_observations_runs_concurrently(self):
        os.environ["TTS_COOLDOWN_OBSERVATION"] = "1"
        n_jobs = 4
        wait_seconds = 0.5

        def fake_single_attempt():
            return {"status": "OK"}

        jobs = [
            dict(
                level_dir="d", segment_id=f"parallel_seg_{i}", canonical_text="t", language="en",
                three_attempt_records=_three_ng_records(),
                params={"voice": "Aoede"},
                single_attempt_fn=fake_single_attempt,
                cooldown_seconds=wait_seconds,
                sleep_fn=time.sleep,
            )
            for i in range(n_jobs)
        ]
        t0 = time.time()
        results = m.run_batch_observations(jobs)
        elapsed = time.time() - t0

        self.assertEqual(len(results), n_jobs)
        for r in results:
            self.assertEqual(r["status"], "OBSERVED")
        # 直列なら n_jobs*wait_seconds(=2.0秒)程度かかるはずだが、並列実行なら
        # wait_secondsの数倍未満(生成時間分の余裕を持たせた閾値)で終わること。
        self.assertLess(elapsed, wait_seconds * (n_jobs - 1))


if __name__ == "__main__":
    unittest.main()
