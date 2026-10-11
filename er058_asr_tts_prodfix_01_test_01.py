# ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04A: 既存Production不具合是正の回帰test。
# (1) OPEN-270 TTS生成総回数上限(外側ループ共有)  (2) OPEN-271/275 Azure費用集計
# (3) 記録欠落(append-only)。APIは一切呼ばない(全てmock/一時ファイル)。
import json
import os
import re
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_tts_generate as tg
import er005_cost_logger as cl
import er011_human_review_lock_01 as review_lock

REPO = os.path.dirname(os.path.abspath(__file__))


def _inner_factory(gens_per_call, calls):
    """generate_english_segment_with_fallbackのmock。max_attemptsを尊重し、
    min(gens_per_call, max_attempts)回分のattempts_logを持つOKを返す。"""
    def fake(text, out_path, expected, **kw):
        n = min(gens_per_call, kw.get("max_attempts", 3))
        calls.append(dict(kw, _gens=n))
        return {"status": "OK", "attempts_log": [{"attempt": i + 1} for i in range(n)], "asr_text": "x"}
    return fake


def _stopped_slowdown(name, narration_dir, tts_input, result):
    result["status"] = "STOPPED"
    result["post_slowdown_asr_text"] = "slow asr text"
    result["post_slowdown_classification"] = "TRUE_CONTENT_MISMATCH"
    return result


class SlowdownGenerationCapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._old = review_lock.ATTEMPT_HISTORY_PATH
        review_lock.ATTEMPT_HISTORY_PATH = os.path.join(self.tmp, "attempt_history.jsonl")
        self.out = f"{self.tmp}/theme/a2/narration/full_story_part2.wav"

    def tearDown(self):
        review_lock.ATTEMPT_HISTORY_PATH = self._old

    def _run(self, gens_per_call):
        calls = []
        with mock.patch.object(tg.c, "generate_english_segment_with_fallback", _inner_factory(gens_per_call, calls)), \
             mock.patch.object(tg, "apply_a2_slowdown_postprocess", _stopped_slowdown):
            r = tg.generate_a2_segment_with_slowdown("text", self.out, "text")
        return r, calls

    def test_total_generation_never_exceeds_three_when_each_call_uses_two(self):
        # 旧実装: 2回x3周=6回(上限違反)。新: 2+1=3回で打ち切り。
        r, calls = self._run(2)
        self.assertLessEqual(sum(c["_gens"] for c in calls), review_lock.PRODUCTION_MAX_TTS_ATTEMPTS)
        self.assertEqual([c["max_attempts"] for c in calls], [3, 1])
        self.assertEqual(r["status"], "STOPPED")
        self.assertTrue(r["tts_generation_cap_reached"])
        self.assertEqual(r["tts_generations_used"], 3)

    def test_never_regenerates_after_budget_exhausted(self):
        r, calls = self._run(3)
        self.assertEqual(len(calls), 1)  # 1周で3回消費 -> 取り直し無し
        self.assertEqual(r["status"], "STOPPED")

    def test_single_generation_per_call_stops_at_three(self):
        r, calls = self._run(1)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sum(c["_gens"] for c in calls), 3)

    def test_inner_standard_attempts_capped_by_remaining(self):
        r, calls = self._run(2)
        self.assertLessEqual(calls[1]["standard_attempts"], calls[1]["max_attempts"])

    def test_post_slowdown_asr_text_preserved_per_iteration_append_only(self):
        r, calls = self._run(1)
        texts = [a["post_slowdown_asr_text"] for a in r["slowdown_attempts_log"]]
        self.assertEqual(texts, ["slow asr text"] * 3)
        with open(review_lock.ATTEMPT_HISTORY_PATH, encoding="utf-8") as f:
            events = [json.loads(line) for line in f if line.strip()]
        rev = [e for e in events if e["action"] == "A2_SLOWDOWN_REVERIFY"]
        self.assertEqual(len(rev), 3)
        self.assertEqual(rev[0]["segment_id"], "full_story_part2")
        self.assertEqual(rev[0]["post_slowdown_asr_text"], "slow asr text")

    def test_ok_path_unchanged(self):
        calls = []
        def ok_slowdown(name, d, t, result):
            result["slowdown_applied"] = True
            return result
        with mock.patch.object(tg.c, "generate_english_segment_with_fallback", _inner_factory(1, calls)), \
             mock.patch.object(tg, "apply_a2_slowdown_postprocess", ok_slowdown):
            r = tg.generate_a2_segment_with_slowdown("text", self.out, "text")
        self.assertEqual(r["status"], "OK")
        self.assertEqual(len(calls), 1)
        self.assertNotIn("tts_generation_cap_reached", r)


class AzureCostAggregationTest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        os.chdir(REPO)

    def tearDown(self):
        os.chdir(self._cwd)

    def _log(self, records):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "raw_usage_log.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        return p

    AZURE = {"provider": "azure", "api": "get_full_text_via_azure_stt_with_phrase_list",
             "model_id": "azure-speech-stt", "success": True,
             "usage_source": "LOCAL_WAV_HEADER_EXACT", "audio_duration_submitted_seconds": 231.83}

    def test_er019_counts_azure_not_zero(self):
        import er019_family_x_audio_production_runner_01 as r19
        jpy, by = r19.compute_cost_jpy_so_far(self._log([self.AZURE]))
        self.assertAlmostEqual(jpy, 231.83 / 3600 * 1.0 * 160.0, places=4)  # 約10.30円
        self.assertGreater(by["azure"], 10.2)

    def test_er012_e_counts_azure_not_zero(self):
        import er012_e_family_entertainment_two_level_runner_01 as e
        jpy, by = e.compute_cost_jpy_so_far(self._log([self.AZURE]))
        self.assertAlmostEqual(jpy, 231.83 / 3600 * 160.0, places=4)

    def test_er012_b_counts_azure_not_zero(self):
        import er012_b_family_production_runner_01 as b
        jpy, by = b.compute_cost_jpy_so_far(self._log([self.AZURE]))
        self.assertAlmostEqual(jpy, 231.83 / 3600 * 160.0, places=4)

    def test_helper_fail_closed_on_missing_price(self):
        def no_price(provider, model, meter):
            raise StopIteration
        with self.assertRaises(RuntimeError):
            cl.azure_stt_cost_usd(self.AZURE, no_price)

    def test_helper_zero_without_duration(self):
        self.assertEqual(cl.azure_stt_cost_usd({"provider": "azure"}, lambda *a: 1.0), 0.0)

    def test_all_eleven_duplicated_aggregators_use_common_helper(self):
        names = ["er012_b_family_production_runner_01", "er012_e_family_entertainment_two_level_runner_01",
                 "er012_editorial_b_voices_3v_audio_trial_01", "er012_editorial_b_voices_a2_trial02_runner",
                 "er012_editorial_b_voices_comment1_contract_finalize_11", "er012_editorial_b_voices_trial_08_audio",
                 "er012_editorial_b_voices_trial_09_audio", "er012_editorial_b_voices_trial_10_comment1",
                 "er012_editorial_b_voices_trial_10_comment1_reproducibility",
                 "er012_personalized_news_b1_rebuild_01_audio", "er019_family_x_audio_production_runner_01"]
        for n in names:
            with open(os.path.join(REPO, n + ".py"), encoding="utf-8") as f:
                src = f.read()
            self.assertIn("cl.azure_stt_cost_usd(rec, price)", src, n)
            self.assertIsNone(re.search(r'^\s*if provider in \("gemini", "openai", "openai_asr"\) and model:',
                                         src, re.M), n)


class RecordAppendOnlyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._old_hist = review_lock.ATTEMPT_HISTORY_PATH
        review_lock.ATTEMPT_HISTORY_PATH = os.path.join(self.tmp, "attempt_history.jsonl")

    def tearDown(self):
        review_lock.ATTEMPT_HISTORY_PATH = self._old_hist

    def _history(self):
        with open(review_lock.ATTEMPT_HISTORY_PATH, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def _check_queue_dup(self, module, attr):
        qpath = os.path.join(self.tmp, "queue.jsonl")
        wav = f"{self.tmp}/t/a2/narration/full_story_part1.wav"
        with mock.patch.object(module, attr, qpath):
            d1 = {"canonical_text": "Some Muse calls", "wav_path": wav, "cost_guard_triggered": False,
                  "final_status": "HUMAN_REVIEW_REQUIRED",
                  "steps": [{"step": "primary_1", "text": "Some US calls"}]}
            d2 = dict(d1, steps=[{"step": "primary_1", "text": "Some US calls"},
                                  {"step": "secondary_1", "provider": "azure", "text": "Some use calls"}])
            module._log_human_review(d1)
            module._log_human_review(d2)
        with open(qpath, encoding="utf-8") as f:
            self.assertEqual(len([line for line in f if line.strip()]), 1)  # queue表示は重複抑止
        ev = [e for e in self._history() if e["action"] == "HUMAN_REVIEW_QUEUE_DUPLICATE_SUPPRESSED"]
        self.assertEqual(len(ev), 1)  # 転写は消えずhistoryへ残る
        self.assertEqual(ev[0]["steps"][1]["text"], "Some use calls")

    def test_en_queue_duplicate_suppressed_but_transcript_kept(self):
        import er006_secondary_asr_01 as m
        self._check_queue_dup(m, "HUMAN_REVIEW_LOG_PATH")

    def test_ja_queue_duplicate_suppressed_but_transcript_kept(self):
        import er007_ja_secondary_asr_01 as m
        self._check_queue_dup(m, "HUMAN_REVIEW_LOG_PATH_JA")

    def test_prior_tts_results_archived_append_only(self):
        p = os.path.join(self.tmp, "tts_generation_results.json")
        prior = {"segments": {"full_story_part2": {"status": "STOPPED", "standard_attempts_log": [
            {"attempt": 1, "asr_text": "first run transcript"}], "slowdown_attempts_log": [
            {"attempt": 1, "post_slowdown_asr_text": "slow"}]}},
            "key_phrases": {"1": {"english": {"status": "OK", "attempts_log": [{"attempt": 1, "asr_text": "kp"}]}}}}
        with open(p, "w", encoding="utf-8") as f:
            json.dump(prior, f)
        review_lock.archive_prior_tts_results(p)
        review_lock.archive_prior_tts_results(p)  # 追記のみ(2行になる、上書きしない)
        h = self._history()
        self.assertEqual(len(h), 2)
        snap = h[0]["prior_attempts"]
        self.assertEqual(snap["segments/full_story_part2"]["standard_attempts_log"][0]["asr_text"],
                         "first run transcript")
        self.assertEqual(snap["segments/full_story_part2"]["slowdown_attempts_log"][0]["post_slowdown_asr_text"], "slow")
        self.assertEqual(snap["key_phrases/1/english"]["attempts_log"][0]["asr_text"], "kp")
        review_lock.archive_prior_tts_results(os.path.join(self.tmp, "missing.json"))  # 例外にしない
        self.assertEqual(len(self._history()), 2)

    def test_style_prefix_record_and_attempts_detail(self):
        long = "S" * 500
        rec = review_lock.style_prefix_record(long)
        self.assertEqual(rec["len"], 500)
        self.assertEqual(len(rec["head200"]), 200)
        self.assertEqual(len(rec["sha256"]), 64)
        self.assertIsNone(review_lock.style_prefix_record(None))
        result = {"standard_attempts_log": [{"attempt": 1, "asr_text": "a", "audio_classification": "X",
                                             "verified": False, "style_prefix": rec,
                                             "cascade_steps": [{"step": "secondary_1", "text": "az"}]}],
                  "fallback_attempts_log": [{"attempt": 1, "asr_text": "b", "instruction_label": "MINIMAL_INSTRUCTION_PREFIX"}]}
        d = review_lock.build_attempts_detail(result)
        self.assertEqual([x["route"] for x in d], ["standard", "fallback"])
        self.assertEqual(d[0]["cascade_steps"][0]["text"], "az")
        self.assertEqual(d[0]["style_prefix"]["sha256"], rec["sha256"])
        self.assertEqual(d[1]["instruction_label"], "MINIMAL_INSTRUCTION_PREFIX")

    def test_fixed_misleading_label_removed(self):
        with open(os.path.join(REPO, "er003_v1_repro01_main_generate.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn('"instruction": "minimal (not ENGLISH_STYLE_PREFIX)"', src)
        self.assertIn('"instruction_label": _instruction_source', src)


if __name__ == "__main__":
    unittest.main()
