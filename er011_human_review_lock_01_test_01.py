# ============================================================
# er011_human_review_lock_01_test_01.py
# ER-011-HUMAN-REVIEW-COST-GUARD-01: Part H 受入テスト(5ケース)
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

import er011_human_review_lock_01 as review_lock


class Er011AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_test_")
        self.theme_dir = os.path.join(self.tmp_dir, "pool_test_theme", "b1b")
        self.narration_dir = os.path.join(self.theme_dir, "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "full_story_part1.wav").replace("\\", "/")
        self.canonical_text = "This is the canonical text for the test segment."

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _make_fn(self, results_sequence):
        """呼ばれるたびにresults_sequenceから次の結果を返すfake generate関数。
        呼び出し回数もtracking用リストへ記録する。"""
        calls = []

        def fn(text, out_path, *args, **kwargs):
            calls.append((text, out_path))
            idx = len(calls) - 1
            return results_sequence[min(idx, len(results_sequence) - 1)]

        return fn, calls

    # ------------------------------------------------------------
    # Fixture 1: Primary/Secondaryで解決せずHuman Reviewへ到達 -> STOP
    # ------------------------------------------------------------
    def test_1_human_review_reached_locks_segment(self):
        fn, calls = self._make_fn([
            {"status": "ASR_VALIDATION_UNCERTAIN", "reason": "entity-only mismatch",
             "attempts_log": [{"attempt": 1, "asr_text": "x"}]},
        ])
        guarded = review_lock.guarded_generate("en")(fn)
        result = guarded(self.canonical_text, self.out_path)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], "ASR_VALIDATION_UNCERTAIN")

        level_out_dir = review_lock._level_out_dir_from_out_path(self.out_path)
        store = review_lock._load_store(level_out_dir)
        entry = store["full_story_part1"]
        self.assertEqual(entry["state"], "HUMAN_REVIEW_REQUIRED")

    # ------------------------------------------------------------
    # Fixture 2: 同じsegmentを再実行 -> TTS/ASR call 0、既存状態を返す
    # ------------------------------------------------------------
    def test_2_reexecution_makes_zero_calls(self):
        fn1, calls1 = self._make_fn([{"status": "STOPPED", "reason": "6回試行しても不合格", "attempts_log": []}])
        guarded1 = review_lock.guarded_generate("en")(fn1)
        guarded1(self.canonical_text, self.out_path)
        self.assertEqual(len(calls1), 1)

        # 同じsegment・同じcanonical_textで、別の(呼ばれたら失敗する)fnを使って再実行する。
        def fn_should_not_be_called(text, out_path, *args, **kwargs):
            raise AssertionError("この関数は呼ばれてはならない(0 API call制約違反)")

        guarded2 = review_lock.guarded_generate("en")(fn_should_not_be_called)
        result = guarded2(self.canonical_text, self.out_path)
        self.assertEqual(result["status"], "HUMAN_REVIEW_LOCKED")
        self.assertEqual(result["human_review_lock_status"], "HUMAN_REVIEW_REQUIRED")

    # ------------------------------------------------------------
    # Fixture 3: 明示的REGENERATE_APPROVED -> 初めて再生成可能
    # ------------------------------------------------------------
    def test_3_explicit_regenerate_approval_allows_one_more_call(self):
        fn1, _ = self._make_fn([{"status": "STOPPED", "reason": "fail", "attempts_log": []}])
        review_lock.guarded_generate("en")(fn1)(self.canonical_text, self.out_path)

        # 承認前: ブロックされる。
        def fn_blocked(text, out_path, *args, **kwargs):
            raise AssertionError("承認前に呼ばれてはならない")
        result_blocked = review_lock.guarded_generate("en")(fn_blocked)(self.canonical_text, self.out_path)
        self.assertEqual(result_blocked["status"], "HUMAN_REVIEW_LOCKED")

        # 明示的承認。
        review_lock.approve_regenerate(self.out_path, self.canonical_text, approved_by="test_user")

        # 承認後: 1回だけ通常通り呼ばれる。
        fn2, calls2 = self._make_fn([{"status": "OK", "reason": None, "attempts_log": [{"attempt": 1, "asr_text": "y"}]}])
        result2 = review_lock.guarded_generate("en")(fn2)(self.canonical_text, self.out_path)
        self.assertEqual(len(calls2), 1)
        self.assertEqual(result2["status"], "OK")

    # ------------------------------------------------------------
    # Fixture 4: 再生成後またHuman Review -> 再びlock
    # ------------------------------------------------------------
    def test_4_regeneration_failing_again_relocks(self):
        fn1, _ = self._make_fn([{"status": "STOPPED", "reason": "fail", "attempts_log": []}])
        review_lock.guarded_generate("en")(fn1)(self.canonical_text, self.out_path)
        review_lock.approve_regenerate(self.out_path, self.canonical_text, approved_by="test_user")

        fn2, calls2 = self._make_fn([{"status": "ASR_VALIDATION_UNCERTAIN", "reason": "still bad", "attempts_log": []}])
        review_lock.guarded_generate("en")(fn2)(self.canonical_text, self.out_path)
        self.assertEqual(len(calls2), 1)

        level_out_dir = review_lock._level_out_dir_from_out_path(self.out_path)
        entry = review_lock._load_store(level_out_dir)["full_story_part1"]
        self.assertEqual(entry["state"], "HUMAN_REVIEW_REQUIRED")

        # 3回目: 再承認なしでは再びブロックされる(「もう一度実行しただけ」では解除されない)。
        def fn3(text, out_path, *args, **kwargs):
            raise AssertionError("再承認なしに呼ばれてはならない")
        result3 = review_lock.guarded_generate("en")(fn3)(self.canonical_text, self.out_path)
        self.assertEqual(result3["status"], "HUMAN_REVIEW_LOCKED")

    # ------------------------------------------------------------
    # Fixture 5: queue重複防止
    # ------------------------------------------------------------
    def test_5_queue_deduplication(self):
        queue_path = os.path.join(self.tmp_dir, "human_review_queue.jsonl")
        wav_path = self.out_path
        text = self.canonical_text

        def append_if_new(qpath, wpath, ctext):
            if review_lock.is_duplicate_queue_entry(qpath, wpath, ctext):
                return False
            os.makedirs(os.path.dirname(qpath), exist_ok=True)
            with open(qpath, "a", encoding="utf-8") as f:
                f.write(json.dumps({"canonical_text": ctext, "wav_path": wpath}, ensure_ascii=False) + "\n")
            return True

        self.assertTrue(append_if_new(queue_path, wav_path, text))
        self.assertFalse(append_if_new(queue_path, wav_path, text))  # 重複は追記されない
        self.assertFalse(append_if_new(queue_path, wav_path, text))

        with open(queue_path, encoding="utf-8") as f:
            lines = [l for l in f.read().splitlines() if l.strip()]
        self.assertEqual(len(lines), 1)

        # 異なるcanonical_text(台本修正後)は新規entryとして扱う。
        self.assertTrue(append_if_new(queue_path, wav_path, text + " (revised)"))
        with open(queue_path, encoding="utf-8") as f:
            lines = [l for l in f.read().splitlines() if l.strip()]
        self.assertEqual(len(lines), 2)


class BudgetGuardTests(unittest.TestCase):
    """Part F: 累積TTS/ASR呼び出し数が閾値を超えた場合、REGENERATE_
    APPROVED中であっても強制的にHUMAN_REVIEW_REQUIREDへ固定する。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "pool_test_theme", "b1b", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "full_story_part2.wav").replace("\\", "/")
        self.text = "Budget guard test segment canonical text."

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_cumulative_attempts_over_threshold_forces_lock_even_on_ok(self):
        # 大量のattempts_logを持つ「成功」結果を模擬し、1回の呼び出しだけで
        # 累積上限(MAX_CUMULATIVE_TTS_ATTEMPTS=15)を超えさせる。
        big_attempts_log = [{"attempt": i, "asr_text": "x"} for i in range(1, 20)]

        def fn(text, out_path, *a, **k):
            return {"status": "OK", "attempts_log": big_attempts_log}

        result = review_lock.guarded_generate("en")(fn)(self.text, self.out_path)
        self.assertEqual(result["status"], "OK")  # この回のresult自体はOKのまま返す

        level_out_dir = review_lock._level_out_dir_from_out_path(self.out_path)
        entry = review_lock._load_store(level_out_dir)["full_story_part2"]
        self.assertTrue(entry["budget_guard_triggered"])
        self.assertEqual(entry["state"], "HUMAN_REVIEW_REQUIRED")

        # 次回呼び出しはブロックされる(REGENERATE_APPROVEDを経ない限り)。
        def fn2(text, out_path, *a, **k):
            raise AssertionError("budget guard発火後は承認なしに呼ばれてはならない")
        result2 = review_lock.guarded_generate("en")(fn2)(self.text, self.out_path)
        self.assertEqual(result2["status"], "HUMAN_REVIEW_LOCKED")


class DeriveSegmentKeyTests(unittest.TestCase):
    def test_derives_theme_level_segment_from_narration_path(self):
        theme, level, segment = review_lock.derive_segment_key(
            "er006_output/pool_pilot_01/pool_n5_cafes/b1b/narration/full_story_part1.wav")
        self.assertEqual((theme, level, segment), ("pool_n5_cafes", "b1b", "full_story_part1"))

    def test_derives_with_windows_style_backslashes(self):
        theme, level, segment = review_lock.derive_segment_key(
            "er006_output\\pool_pilot_01\\pool_n4_supermarket\\a2\\narration\\comment_2.wav")
        self.assertEqual((theme, level, segment), ("pool_n4_supermarket", "a2", "comment_2"))


class TextChangeInvalidatesLockTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "pool_test_theme", "a2", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "comment_2.wav").replace("\\", "/")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_changed_canonical_text_bypasses_stale_lock(self):
        old_text = "Part 1 では、店が売り場の配置を変えました。"
        new_text = "物語の前半では、店が売り場の配置を変えました。"

        def fn_fail(text, out_path, *a, **k):
            return {"status": "STOPPED", "reason": "fail", "attempts_log": []}
        review_lock.guarded_generate("ja")(fn_fail)(old_text, self.out_path)

        # 台本を修正した新しいテキストでは、古いlockに縛られず通常通り
        # 呼び出される(No.4 comment_2の実例と同じシナリオ)。
        def fn_ok(text, out_path, *a, **k):
            return {"status": "OK", "reason": None, "attempts_log": [{"attempt": 1, "asr_text": "z"}]}
        result = review_lock.guarded_generate("ja")(fn_ok)(new_text, self.out_path)
        self.assertEqual(result["status"], "OK")


# ============================================================
# ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part B/L: regression
# ============================================================
class ProductionMaxAttemptsAndAttemptsLogTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "pool_test_theme", "a2", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "kp_1.wav").replace("\\", "/")
        self.text = "Retry limit test segment."

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_production_max_tts_attempts_is_3(self):
        self.assertEqual(review_lock.PRODUCTION_MAX_TTS_ATTEMPTS, 3)

    def test_key_phrase_fallback_budget_is_zero_when_standard_used_all_attempts(self):
        # Part B: standard経路が既にmax_attempts(3)回を使い切っている場合、
        # fallback経路は1回も追加で呼ばれてはならない(標準+fallback合計が
        # 3回を超えないこと)。
        import er003_v1_repro01_main_generate as repro01
        orig_standard = repro01.generate_narration_snippet_verified_strict
        orig_fallback = repro01.generate_english_component_minimal_instruction
        fallback_calls = {"n": 0}

        def fake_standard(text, language, out_path, expected_substring, **kwargs):
            return {"status": "STOPPED", "reason": "3回不合格",
                    "attempts_log": [{"attempt": i, "asr_text": "x"} for i in range(1, 4)]}

        def fake_fallback(*a, **k):
            fallback_calls["n"] += 1
            raise AssertionError("standardで既に上限3回を使い切っているため、fallbackは1回も呼ばれてはならない")

        repro01.generate_narration_snippet_verified_strict = fake_standard
        repro01.generate_english_component_minimal_instruction = fake_fallback
        try:
            result = repro01.generate_key_phrase_component_verified(
                "opt out", self.out_path, max_attempts=review_lock.PRODUCTION_MAX_TTS_ATTEMPTS)
            self.assertEqual(result["status"], "STOPPED")
            self.assertEqual(fallback_calls["n"], 0)
        finally:
            repro01.generate_narration_snippet_verified_strict = orig_standard
            repro01.generate_english_component_minimal_instruction = orig_fallback

    def test_key_phrase_fallback_gets_remaining_budget_only(self):
        # standardが1回だけ使った場合、fallbackの残り予算は2回(3-1)で
        # あるべき(3+3=6回になってはならない)。
        import er003_v1_repro01_main_generate as repro01
        orig_standard = repro01.generate_narration_snippet_verified_strict
        orig_fallback = repro01.generate_english_component_minimal_instruction
        fallback_calls = {"n": 0}

        def fake_standard(text, language, out_path, expected_substring, **kwargs):
            return {"status": "STOPPED", "reason": "1回で不合格",
                    "attempts_log": [{"attempt": 1, "asr_text": "x"}]}

        def fake_fallback(*a, **k):
            fallback_calls["n"] += 1
            return {"status": "STOPPED", "reason": "fallbackも失敗"}

        repro01.generate_narration_snippet_verified_strict = fake_standard
        repro01.generate_english_component_minimal_instruction = fake_fallback
        try:
            repro01.generate_key_phrase_component_verified(
                "opt out", self.out_path, max_attempts=review_lock.PRODUCTION_MAX_TTS_ATTEMPTS)
            self.assertEqual(fallback_calls["n"], 2, "fallbackはmax_attempts(3)-standard消費(1)=2回までのはず")
        finally:
            repro01.generate_narration_snippet_verified_strict = orig_standard
            repro01.generate_english_component_minimal_instruction = orig_fallback

    def test_attempts_log_preserved_after_human_review_lock(self):
        # Part L: Human Review Lock発動後、_blocked_result()が返す
        # attempts_logが空配列で上書きされず、record_outcome()時点の
        # 実際の履歴(ASR文字起こし等)を保持していること。
        real_attempts_log = [{"attempt": 1, "asr_text": "weight"}, {"attempt": 2, "asr_text": "weight"},
                              {"attempt": 3, "asr_text": "weight"}]

        def fn(text, out_path, *a, **k):
            return {"status": "STOPPED", "reason": "3回試行しても不合格", "attempts_log": real_attempts_log}

        review_lock.guarded_generate("en")(fn)(self.text, self.out_path)

        level_out_dir = review_lock._level_out_dir_from_out_path(self.out_path)
        entry = review_lock._load_store(level_out_dir)["kp_1"]
        self.assertEqual(entry["state"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(entry["last_attempts_log"], real_attempts_log)

        # 2回目呼び出し(ブロックされる)でも、実際の履歴が復元されること
        # (従来は空配列[]で上書きされてしまっていた、No.8監査での発見)。
        def fn_should_not_be_called(text, out_path, *a, **k):
            raise AssertionError("ブロック中に呼ばれてはならない")
        result2 = review_lock.guarded_generate("en")(fn_should_not_be_called)(self.text, self.out_path)
        self.assertEqual(result2["status"], "HUMAN_REVIEW_LOCKED")
        self.assertEqual(result2["attempts_log"], real_attempts_log)


if __name__ == "__main__":
    unittest.main()
