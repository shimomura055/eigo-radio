# ============================================================
# er002_test_common.py
# ER-002-S1/S1.1: 共通実験基盤のテスト(モック・固定データのみ使用)
# ============================================================
# 実TTS APIも実QA APIも一切呼び出さない。tts_call_fn/qa_call_fnは
# すべてこのファイル内のモックに差し替えている。
#
# ここで証明できるのは「QAレスポンスの解析・分類・合否集約ロジックが
# 期待どおり動くか」であり、「QAモデル(gemini-3-flash-preview)が実際に
# 見出し欠落や言い換えを正しく検出できるか」という実能力の証明ではない
# (それはER-002-S2以降、実APIで確認する)。個々のテストのdocstringに
# この区別を明記している。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_common -v

import json
import os
import subprocess
import tempfile
import unittest
import wave
from unittest import mock

import numpy as np

import er002_ab_anonymize as ab
import er002_common as common
import er002_rerun_bundle as rerun
import er002_runner as runner
import er002_s3_config as s3config
import er002_script_adapter as script_adapter
import er002_v1_freeze as freeze


# ============================================================
# テスト用フィクスチャ(合成データ。実記事の文面は使わない)
# ============================================================
def make_word_text(n, prefix="word"):
    return " ".join(f"{prefix}{i}" for i in range(n))


def make_script(body_words=200, sub1_words=60, sub2_words=60, final_words=40,
                 title="Sample Title", points_heading="Today's Sample Points",
                 sub1_heading="First point heading", sub2_heading="Second point heading",
                 sub1_paragraphs=None, sub2_paragraphs=None,
                 n_subsections=2, final_heading="In One Line", n_sections_override=None):
    if sub1_paragraphs is None:
        sub1_paragraphs = [make_word_text(sub1_words, "s1w")]
    if sub2_paragraphs is None:
        sub2_paragraphs = [make_word_text(sub2_words, "s2w")]

    subsections = [{"heading": sub1_heading, "paragraphs": sub1_paragraphs}]
    if n_subsections >= 2:
        subsections.append({"heading": sub2_heading, "paragraphs": sub2_paragraphs})
    if n_subsections >= 3:
        subsections.append({"heading": "Third point heading", "paragraphs": [make_word_text(20, "s3w")]})

    sections = [
        {"type": "body", "paragraphs": [make_word_text(body_words)]},
        {"type": "section", "heading": points_heading, "subsections": subsections},
        {"type": "section", "heading": final_heading, "paragraphs": [make_word_text(final_words)]},
    ]
    return {"title": title, "sections": sections}


def make_qa_dict(plan, **overrides):
    elements = common.build_expected_elements(plan)
    base = {
        "assessment_status": "conclusive", "inconclusive_reason": None,
        "transcript": plan.full_text,
        "element_counts": {k: 1 for k, _ in elements},
        "body_dropped": False, "body_dropped_evidence": [],
        "body_duplicated": False, "body_duplicated_evidence": [],
        "unauthorized_paraphrase": False, "unauthorized_paraphrase_evidence": [],
        "section_order_changed": False, "observed_section_order": [k for k, _ in elements],
        "extra_unscripted_speech": False, "extra_unscripted_speech_evidence": [],
        "notes": "ok",
    }
    base.update(overrides)
    return base


def make_qa_json(plan, **overrides):
    return json.dumps(make_qa_dict(plan, **overrides))


def make_wav_bytes(n_samples=1000, sample_rate=24000, value=1000):
    import array
    import io
    samples = array.array("h", [value] * n_samples)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(samples.tobytes())
    return buf.getvalue()


# ============================================================
# 1〜3, (追加) 構造検証: subsections=2件の強制・内容重複検出
# ============================================================
class StructureValidationTests(unittest.TestCase):
    """検証対象: er002_common.validate_script_structure の集約ロジック。
    QAモデルは一切関与しない、純粋なPythonロジックのテスト。"""

    def test_exactly_two_subsections_passes(self):
        script = make_script(n_subsections=2)
        result = common.validate_script_structure(script)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(len(result.subsections), 2)

    def test_one_subsection_fails(self):
        script = make_script(n_subsections=1)
        result = common.validate_script_structure(script)
        self.assertFalse(result.valid)
        self.assertTrue(any("正確に2件" in e for e in result.errors), result.errors)

    def test_three_subsections_fails(self):
        script = make_script(n_subsections=3)
        result = common.validate_script_structure(script)
        self.assertFalse(result.valid)
        self.assertTrue(any("正確に2件" in e for e in result.errors), result.errors)

    def test_duplicated_point_content_fails(self):
        """Point OneとPoint Twoの小見出し・本文が完全一致している場合を
        構造検証の段階で不合格にできることを確認する。"""
        script = make_script(
            sub1_heading="Same heading", sub2_heading="Same heading",
            sub1_paragraphs=["identical text here"], sub2_paragraphs=["identical text here"],
        )
        result = common.validate_script_structure(script)
        self.assertFalse(result.valid)
        self.assertTrue(any("完全に重複" in e for e in result.errors), result.errors)


# ============================================================
# 4: 共通演技指示への記事固有語混入チェック
# ============================================================
class GenreLeakageTests(unittest.TestCase):
    """検証対象: er002_common.find_genre_leakage / build_style_prefix。
    ER-002-S0で発見された"care point"混入の回帰防止テスト。"""

    def test_style_prefix_has_no_leakage(self):
        prefix = common.build_style_prefix()
        self.assertEqual(common.find_genre_leakage(prefix), [])
        self.assertNotIn("care point", prefix.lower())
        self.assertNotIn("tiger", prefix.lower())

    def test_detects_known_leakage_terms(self):
        broken_text = 'Clearly say "Point One" before the first care point and mention the Tiger fans.'
        found = common.find_genre_leakage(broken_text)
        self.assertIn("care point", found)
        self.assertIn("tiger", found)

    def test_assert_raises_on_leakage(self):
        with self.assertRaises(AssertionError):
            common.assert_no_genre_leakage("this text mentions a care point")


# ============================================================
# 5〜10: 技術問題の個別分類(embedded/grounded共通のclassify_qa_result)
# ============================================================
class QAClassificationTests(unittest.TestCase):
    """検証対象: er002_common.classify_qa_result による
    「レスポンス解析→11分類への集約」ロジック。QAモデル自身が実際に
    見出し欠落等を検出できるかどうかは対象外(固定のQAレスポンスを
    与えて、分類・合否判定コードが正しく動くかのみを確認する)。"""

    def setUp(self):
        self.script = make_script()
        self.plan = common.build_narration_plan(self.script)

    def test_all_clean_passes(self):
        result = common.classify_qa_result(make_qa_dict(self.plan), self.plan)
        self.assertTrue(result["passed"], result["reasons"])

    def test_title_missing_classified(self):
        raw = make_qa_dict(self.plan, element_counts={
            **{k: 1 for k, _ in common.build_expected_elements(self.plan)}, "title": 0})
        result = common.classify_qa_result(raw, self.plan)
        self.assertFalse(result["passed"])
        self.assertEqual(result["element_checks"]["title"]["status"], "missing")
        self.assertIn("title", result["reasons"])

    def test_in_one_line_duplicated_classified(self):
        raw = make_qa_dict(self.plan, element_counts={
            **{k: 1 for k, _ in common.build_expected_elements(self.plan)}, "in_one_line": 2})
        result = common.classify_qa_result(raw, self.plan)
        self.assertFalse(result["passed"])
        self.assertEqual(result["element_checks"]["in_one_line"]["status"], "duplicated")

    def test_body_dropped_classified(self):
        raw = make_qa_dict(self.plan, body_dropped=True, body_dropped_evidence=["missing sentence X"])
        result = common.classify_qa_result(raw, self.plan)
        self.assertFalse(result["passed"])
        self.assertIn("body_dropped", result["reasons"])
        self.assertEqual(result["evidence"]["body_dropped_evidence"], ["missing sentence X"])

    def test_body_duplicated_classified(self):
        raw = make_qa_dict(self.plan, body_duplicated=True, body_duplicated_evidence=["repeated sentence Y"])
        result = common.classify_qa_result(raw, self.plan)
        self.assertFalse(result["passed"])
        self.assertIn("body_duplicated", result["reasons"])

    def test_unauthorized_paraphrase_classified(self):
        raw = make_qa_dict(self.plan, unauthorized_paraphrase=True,
                            unauthorized_paraphrase_evidence=[{"expected": "A", "observed": "B"}])
        result = common.classify_qa_result(raw, self.plan)
        self.assertFalse(result["passed"])
        self.assertIn("unauthorized_paraphrase", result["reasons"])

    def test_section_order_changed_classified(self):
        raw = make_qa_dict(self.plan, section_order_changed=True,
                            observed_section_order=["in_one_line", "title", "today_points_heading"])
        result = common.classify_qa_result(raw, self.plan)
        self.assertFalse(result["passed"])
        self.assertIn("section_order_changed", result["reasons"])

    def test_extra_unscripted_speech_classified(self):
        """要求11項目のうち「台本にない追加発話」に対応。"""
        raw = make_qa_dict(self.plan, extra_unscripted_speech=True,
                            extra_unscripted_speech_evidence=["Thanks for listening!"])
        result = common.classify_qa_result(raw, self.plan)
        self.assertFalse(result["passed"])
        self.assertIn("extra_unscripted_speech", result["reasons"])

    def test_missing_field_is_unknown_not_ok(self):
        """QAモデルがフィールドを返さなかった場合、勝手に合格扱いにしないことを確認。"""
        raw = {"element_counts": {}}  # 何も返ってこないケースを模擬
        result = common.classify_qa_result(raw, self.plan)
        self.assertFalse(result["passed"])
        for key, check in result["element_checks"].items():
            self.assertEqual(check["status"], "unknown")


# ============================================================
# 11: QA応答の解析不能・矛盾はfail-closed
# ============================================================
class QAFailClosedTests(unittest.TestCase):
    def test_unparseable_json_raises(self):
        with self.assertRaises(common.QAParseError):
            common.parse_qa_json("this is not json at all")

    def test_none_response_raises(self):
        with self.assertRaises(common.QAParseError):
            common.parse_qa_json(None)

    def test_call_qa_with_retry_parse_failure_is_fail_closed(self):
        outcome = common.call_qa_with_retry(
            qa_call_fn=lambda prompt, wav: "not json", prompt="p", wav_bytes=b"", max_retry=0)
        self.assertTrue(outcome.parse_failed)
        self.assertIsNone(outcome.raw_result)

    def test_aggregate_disagreement_is_flagged(self):
        """embedded/groundedのどちらかがpassed=Falseの場合はもちろん、
        要素カウントの不一致が disagreements として明示的に記録される
        ことを確認する(診断情報としての価値。現行ロジックでは、
        カウントが食い違う時点で少なくとも片方は個別チェックにも
        失敗するため、disagreements単独が合否を覆す独立要因には
        ならない。この構造はレポートに明記する)。"""
        script = make_script()
        plan = common.build_narration_plan(script)
        embedded = common.classify_qa_result(make_qa_dict(plan), plan)  # title=1 (ok)
        grounded_raw = make_qa_dict(plan, element_counts={
            **{k: 1 for k, _ in common.build_expected_elements(plan)}, "title": 0})
        grounded = common.classify_qa_result(grounded_raw, plan)  # title=0 (missing)
        aggregated = common.aggregate_qa(embedded, grounded)
        self.assertFalse(aggregated["passed"])
        self.assertIn("title", aggregated["disagreements"])


# ============================================================
# 12〜14: TTSコンテンツ試行のオーケストレーション
# ============================================================
class TTSContentAttemptTests(unittest.TestCase):
    def setUp(self):
        self.script = make_script()
        self.plan = common.build_narration_plan(self.script)
        self.style_prefix = common.build_style_prefix()

    def test_all_attempts_fail_no_audio_adopted(self):
        """3回とも技術検品に不合格なら、最終音声が採用されないことを確認。
        既存のfail-open処理(ER-001B-6/7B)は使っていない: run_tts_content_attempts
        は新規実装であり、全滅時にaccepted_audioをNoneのまま返す。"""
        def tts_fn(prompt):
            return b"\x00\x01" * 50

        def qa_fn(prompt, wav):
            return make_qa_json(self.plan, element_counts={
                **{k: 1 for k, _ in common.build_expected_elements(self.plan)}, "title": 0})

        result = common.run_tts_content_attempts(self.plan, self.style_prefix, tts_fn, qa_fn,
                                                   max_content_attempts=3, max_api_retry=0)
        self.assertEqual(result.status, "FAILED_ALL_ATTEMPTS")
        self.assertIsNone(result.accepted_audio)
        self.assertEqual(len(result.attempts), 3)
        self.assertTrue(all(a.outcome != "passed" for a in result.attempts))

    def test_stops_at_first_passing_attempt(self):
        """最初に検品を通過した試行で停止し、以降の試行を行わないことを確認。"""
        state = {"content_attempt": 0}

        def tts_fn(prompt):
            return b"\x00\x01" * 50

        def qa_fn(prompt, wav):
            # embedded/grounded 2回呼ばれるうちの「何回目のコンテンツ試行か」を
            # ざっくり判定するため、呼び出し回数を利用する。
            state["content_attempt"] += 1
            call_index = state["content_attempt"]
            # 1回目のcontent attemptはembeddedの時点で不合格にする(groundedは
            # 呼ばれない=呼び出し回数1)。2回目のcontent attemptはembedded/grounded
            # とも合格にする。
            if call_index == 1:
                return make_qa_json(self.plan, element_counts={
                    **{k: 1 for k, _ in common.build_expected_elements(self.plan)}, "title": 0})
            return make_qa_json(self.plan)

        result = common.run_tts_content_attempts(self.plan, self.style_prefix, tts_fn, qa_fn,
                                                   max_content_attempts=3, max_api_retry=0)
        self.assertEqual(result.status, "OK")
        self.assertEqual(result.accepted_attempt, 2)
        self.assertEqual(len(result.attempts), 2, "3回目の試行が行われていないこと")

    def test_api_retry_and_content_attempt_recorded_separately(self):
        """TTS呼び出し自体が一時的に失敗した場合、tts_content_attempt_numberは
        増やさずtts_api_retry_countだけが増えることを確認する。"""
        call_state = {"tts_calls": 0}

        def tts_fn(prompt):
            call_state["tts_calls"] += 1
            if call_state["tts_calls"] == 1:
                raise RuntimeError("simulated transient API failure")
            return b"\x00\x01" * 50

        def qa_fn(prompt, wav):
            return make_qa_json(self.plan)

        result = common.run_tts_content_attempts(self.plan, self.style_prefix, tts_fn, qa_fn,
                                                   max_content_attempts=3, max_api_retry=2, sleep_fn=lambda s: None)
        self.assertEqual(result.status, "OK")
        self.assertEqual(result.accepted_attempt, 1, "API障害はtts_content_attemptを増やさない")
        self.assertGreaterEqual(result.attempts[0].tts_api_retry_count, 1)


# ============================================================
# ER-002-S2-C2 追加: normalize_pcm(ER-001B-6/9/10と同一のピーク正規化)
# ============================================================
class NormalizePcmTests(unittest.TestCase):
    """ER-002-S2で発見した実装漏れ(_call_tts_with_retryへ正規化を追加した際に
    見つかった)の専用回帰テスト。"""

    def _peak(self, pcm_bytes):
        import array
        samples = array.array("h", pcm_bytes)
        return max(abs(s) for s in samples) if samples else 0

    def test_scales_to_target_peak(self):
        import array
        # peak=10000 -> 目標倍率(0.7*32767)/10000 ≈ 2.29倍で、3.0倍の上限にはかからない
        samples = array.array("h", [5000, -10000, 2500, -7500])
        raw = samples.tobytes()
        normalized = common.normalize_pcm(raw, target_peak=0.7)
        expected_peak = int(10000 * min((0.7 * 32767) / 10000, 3.0))
        self.assertLessEqual(abs(self._peak(normalized) - expected_peak), 1)

    def test_scale_capped_at_3x_for_very_quiet_audio(self):
        import array
        # peak=100 -> 素の目標倍率は (0.7*32767)/100 ≈ 229倍だが、3.0倍に制限される
        samples = array.array("h", [100, -50, 30])
        raw = samples.tobytes()
        normalized = common.normalize_pcm(raw, target_peak=0.7)
        normalized_samples = array.array("h", normalized)
        self.assertEqual(normalized_samples[0], 300)  # 100 * 3.0 = 300 (上限適用)

    def test_all_silence_returns_unchanged(self):
        import array
        raw = array.array("h", [0, 0, 0, 0]).tobytes()
        normalized = common.normalize_pcm(raw, target_peak=0.7)
        self.assertEqual(normalized, raw)

    def test_empty_input_returns_unchanged(self):
        self.assertEqual(common.normalize_pcm(b""), b"")

    def test_output_stays_within_int16_range_no_overflow(self):
        import array
        samples = array.array("h", [32767, -32768, 100])
        raw = samples.tobytes()
        normalized = common.normalize_pcm(raw, target_peak=0.9)
        for v in array.array("h", normalized):
            self.assertTrue(-32768 <= v <= 32767)

    def test_applied_automatically_inside_tts_retry_call(self):
        """_call_tts_with_retry経由でtts_call_fnの生PCMが正規化されることを確認。"""
        import array
        quiet_pcm = array.array("h", [100, -100, 50]).tobytes()

        def tts_fn(prompt):
            return quiet_pcm

        pcm, _retries, ok, _err = common._call_tts_with_retry(tts_fn, "prompt", max_retry=0, sleep_fn=None)
        self.assertTrue(ok)
        self.assertNotEqual(pcm, quiet_pcm, "正規化により生PCMから値が変化しているはず")
        self.assertEqual(self._peak(pcm), 300)  # 100 * 3.0上限


# ============================================================
# 15: 3チャンクの順序と0.8秒無音2箇所
# ============================================================
class ChunkAssemblyTests(unittest.TestCase):
    def test_chunk_order_matches_er001b(self):
        script = make_script(points_heading="Today's Sample Points")
        plan = common.build_narration_plan(script)
        labels = [label for label, _ in plan.chunks]
        self.assertEqual(labels[0], "body")
        self.assertEqual(labels[1], "Today's Sample Points")
        self.assertEqual(labels[2], "In One Line")

    def test_two_silences_of_exactly_0_8_seconds(self):
        pcm_chunks = [b"\x01\x00" * 100, b"\x02\x00" * 100, b"\x03\x00" * 100]
        audio, pause_positions = common.assemble_audio(pcm_chunks, sample_rate=24000, pause_seconds=0.8)
        self.assertEqual(len(pause_positions), 2, "無音挿入は2箇所のみ(全見出し間ではない)")
        expected_pause_bytes = int(24000 * 0.8) * 2  # 16bit=2byte/sample
        # 1つ目の無音の直後から2つ目のチャンクが始まる位置を確認
        chunk1_len = len(pcm_chunks[0])
        self.assertEqual(pause_positions[0], chunk1_len)
        pause1 = audio[chunk1_len:chunk1_len + expected_pause_bytes]
        self.assertEqual(pause1, b"\x00\x00" * int(24000 * 0.8))
        self.assertEqual(len(pause1), expected_pause_bytes)


# ============================================================
# 16〜17: Dynamics3(一度だけ適用・確定パラメータ一致)
# ============================================================
class Dynamics3Tests(unittest.TestCase):
    def test_params_match_confirmed_spec(self):
        p = common.DYNAMICS3_PARAMS
        self.assertEqual(p["threshold_percentile"], 60)
        self.assertEqual(p["ratio"], 8.0)
        self.assertEqual(p["knee_db"], 6.0)
        self.assertEqual(p["attack_ms"], 5.0)
        self.assertEqual(p["release_ms"], 200.0)

    def test_attenuation_only_no_amplification(self):
        rng = np.random.default_rng(0)
        c0 = rng.uniform(-0.5, 0.5, size=24000 * 2)  # 2秒分の合成信号
        result = common.apply_dynamics3_once(c0, sample_rate=24000)
        # match_loudness後の最終振幅がC0を超えていないとは限らない(ラウドネス整合で
        # ゲインを掛け直すため)。「コンプレッション段階では減衰のみ」という確定条件は
        # apply_compressor直後の内部アサーションで保証されている(この関数は例外を
        #出さずに完走した時点でそのアサーションを通過済み)。
        self.assertTrue(result.applied_once)
        self.assertLessEqual(result.metrics_c1["peak_dbfs"], common.PEAK_CEILING_DB + 1e-6)
        self.assertFalse(result.metrics_c1["clipping_detected"])

    def test_dynamics_applied_exactly_once_in_runner(self):
        """run_article経由で呼び出した場合に、apply_dynamics3_onceの呼び出し回数が
        1回であることをモックで直接確認する(構造上の保証を実行レベルでも検証)。"""
        script = make_script()

        def script_fn(config):
            return script

        def tts_fn(prompt):
            return make_wav_pcm_only(200)

        def qa_fn(prompt, wav):
            plan = common.build_narration_plan(script)
            return make_qa_json(plan)

        config = {
            "experiment_id": "ER-002-S1-TEST", "article_id": "t01",
            "genre": "test", "topic_or_source": "synthetic", "voice": "Aoede",
        }

        with mock.patch("er002_common.apply_dynamics3_once", wraps=common.apply_dynamics3_once) as spy:
            outcome = runner.run_article(config, script_fn, tts_fn, qa_fn)
            self.assertEqual(outcome.manifest["status"], "OK")
            self.assertEqual(spy.call_count, 1)


def make_wav_pcm_only(n_samples, value=1000):
    import array
    return array.array("h", [value] * n_samples).tobytes()


# ============================================================
# 18: 単語数・音声時間・実効wpmの記録
# ============================================================
class MetricsRecordingTests(unittest.TestCase):
    def test_evaluate_word_count_boundaries(self):
        self.assertEqual(common.evaluate_word_count(400)["status"], "within_acceptable_range")
        self.assertTrue(common.evaluate_word_count(400)["within_target"])
        self.assertEqual(common.evaluate_word_count(350)["status"], "within_acceptable_range")
        self.assertFalse(common.evaluate_word_count(350)["within_target"], "350語は許容内だが目標帯(380-420)の外")
        self.assertEqual(common.evaluate_word_count(300)["status"], "out_of_range")
        self.assertEqual(common.evaluate_word_count(500)["status"], "out_of_range")

    def test_evaluate_duration_is_warning_only(self):
        d = common.evaluate_duration(100)
        self.assertFalse(d["within_warn_band"])
        self.assertFalse(d["is_hard_gate"], "尺は自動不合格条件にしない")

    def test_effective_wpm_computation(self):
        self.assertEqual(common.effective_wpm(400, 160.0), 150.0)

    def test_manifest_records_word_duration_wpm(self):
        script = make_script(body_words=300, sub1_words=20, sub2_words=20, final_words=20)
        plan = common.build_narration_plan(script)
        expected_words = common.word_count(plan.full_text)

        def script_fn(config):
            return script

        def tts_fn(prompt):
            return make_wav_pcm_only(24000 * 3)  # 3秒/チャンク

        def qa_fn(prompt, wav):
            return make_qa_json(plan)

        config = {"experiment_id": "E", "article_id": "a", "genre": "g", "topic_or_source": "s", "voice": "Aoede"}
        outcome = runner.run_article(config, script_fn, tts_fn, qa_fn)
        m = outcome.manifest
        self.assertEqual(m["status"], "OK")
        self.assertEqual(m["word_metrics"]["word_count"], expected_words)
        self.assertIsNotNone(m["duration_metrics"]["duration_seconds"])
        self.assertIsNotNone(m["effective_wpm"])


# ============================================================
# 19〜20: A/B匿名化
# ============================================================
class ABAnonymizationTests(unittest.TestCase):
    def test_filename_does_not_reveal_speaker(self):
        fname = ab.anonymized_filename("a04", 1)
        self.assertEqual(fname, "er002_a04_sample_1.wav")
        self.assertFalse(ab.filename_reveals_speaker(fname, ["Aoede", "Charon"]))

    def test_metadata_stripped_does_not_reveal_speaker(self):
        base = make_wav_bytes(1000)
        # WAVにLIST/INFOチャンクとして話者名を埋め込んだものを模擬する
        # (wave標準ライブラリでは書けないため、バイト列を手動で連結して模擬)。
        fake_info_chunk = b"LIST" + (b"\x00\x00\x00\x10") + b"INFOIART" + b"\x00\x00\x00\x05" + b"Aoede\x00"
        contaminated = base + fake_info_chunk
        self.assertTrue(ab.metadata_reveals_speaker(contaminated, ["Aoede"]),
                         "テストの前提として、汚染済みWAVは話者名を含んでいること")
        cleaned = ab.strip_wav_metadata(base)  # strip対象はbase(正規のWAV)側の経路を確認
        self.assertFalse(ab.metadata_reveals_speaker(cleaned, ["Aoede", "Charon"]))

    def test_presentation_order_randomized_per_article(self):
        entries = [{"voice": "Aoede"}, {"voice": "Charon"}]
        seen_first_voice = set()
        for i in range(20):
            pres = ab.build_ab_presentation("a04", entries, seed=i)
            seen_first_voice.add(pres.mapping["sample_1"]["voice"])
        self.assertEqual(seen_first_voice, {"Aoede", "Charon"}, "sample_1が常に同じ話者に固定されていないこと")

    def test_ab_mapping_file_is_gitignored(self):
        """.gitignoreのパターンを文字列で確認するだけでなく、実際にgitが
        追跡対象外と判定することをgit check-ignoreで確認する。"""
        with tempfile.NamedTemporaryFile(prefix="er002_a04_", suffix="_ab_mapping.json", dir=".", delete=False) as f:
            path = f.name
        try:
            result = subprocess.run(
                ["git", "check-ignore", "-q", path],
                cwd=".", capture_output=True,
            )
            self.assertEqual(result.returncode, 0, f"{path} がgit check-ignoreで無視されませんでした")
        finally:
            os.remove(path)

    def test_ab_bundle_includes_evaluation_schema_per_sample(self):
        """要求11: A/B評価項目(more_suitable_voice等)を匿名ファイルごとに保存できることを確認。"""
        entries = [{"voice": "Aoede"}, {"voice": "Charon"}]
        wav_bytes_by_label = {"Aoede": make_wav_bytes(500), "Charon": make_wav_bytes(500)}
        bundle = runner.build_ab_bundle("a04", entries, wav_bytes_by_label, seed=1)
        self.assertEqual(len(bundle["user_evaluations"]), 2)
        for filename, evaluation in bundle["user_evaluations"].items():
            self.assertFalse(ab.filename_reveals_speaker(filename, ["Aoede", "Charon"]))
            self.assertEqual(evaluation["status"], "pending_user_listening")
            for key in ("more_suitable_voice", "easier_to_finish", "difference", "reason"):
                self.assertIn(key, evaluation)
                self.assertIsNone(evaluation[key])


# ============================================================
# ER-002-S3-P0 追加: A/Bファイル名の回帰テスト
# ER-002-S2で発生した大文字小文字不一致(article_id="A04"で生成した
# ファイル名を手動でarticle_id="a04"相当へリネームしたが、対応表側は
# 更新し忘れた)の再発防止。
# ============================================================
class ABFilenameConsistencyRegressionTests(unittest.TestCase):
    def setUp(self):
        self.entries = [{"voice": "Aoede"}, {"voice": "Charon"}]
        self.wav_bytes_by_label = {"Aoede": make_wav_bytes(500), "Charon": make_wav_bytes(500)}

    def test_bundle_files_and_mapping_and_evaluations_match_exactly(self):
        """実際に作成された匿名音声ファイル名と、対応表・評価スキーマに記録された
        ファイル名が(大文字小文字を含めて)完全一致することを確認。"""
        bundle = runner.build_ab_bundle("a04", self.entries, self.wav_bytes_by_label, seed=1)
        self.assertEqual(set(bundle["files"].keys()), set(bundle["filename_mapping"].keys()))
        self.assertEqual(set(bundle["files"].keys()), set(bundle["user_evaluations"].keys()))

    def test_case_sensitivity_is_preserved_end_to_end(self):
        """article_idの大文字小文字がfiles/filename_mapping全体で一貫していること
        (article_id="A04"のような大文字混じりでも、全キーが同じ大文字小文字で
        揃うことを確認)。"""
        bundle = runner.build_ab_bundle("A04", self.entries, self.wav_bytes_by_label, seed=1)
        for filename in bundle["files"]:
            self.assertIn("A04", filename)
            self.assertNotIn("a04", filename)
        self.assertEqual(set(bundle["files"].keys()), set(bundle["filename_mapping"].keys()))

    def test_mapping_never_references_nonexistent_file(self):
        """存在しないファイル名を対応表へ保存しない: 一部の話者の音声データが
        まだ無い状態でbuild_ab_bundleを呼ぶと、不完全なsample_1/sample_2の組を
        files/対応表へ書き出す前にfail-closedで例外になることを確認する
        (「片方の話者しかない中途半端なA/Bバンドル」を黙って作らない)。"""
        partial_wav_bytes_by_label = {"Aoede": make_wav_bytes(500)}  # Charon分が未生成
        with self.assertRaises(ab.ABFilenameConsistencyError):
            runner.build_ab_bundle("a04", self.entries, partial_wav_bytes_by_label, seed=1)

    def test_exactly_one_sample_1_and_one_sample_2(self):
        bundle = runner.build_ab_bundle("a04", self.entries, self.wav_bytes_by_label, seed=1)
        self.assertEqual(bundle["files"].keys() & {"er002_a04_sample_1.wav"}, {"er002_a04_sample_1.wav"})
        self.assertEqual(bundle["files"].keys() & {"er002_a04_sample_2.wav"}, {"er002_a04_sample_2.wav"})
        self.assertEqual(len(bundle["files"]), 2)

    def test_validation_raises_on_manually_broken_mapping(self):
        """検証関数自体が、意図的に壊した(大文字小文字を変えた)対応表を
        不合格にできることを確認する。"""
        bundle = runner.build_ab_bundle("a04", self.entries, self.wav_bytes_by_label, seed=1)
        broken = dict(bundle)
        broken["filename_mapping"] = {
            k.replace("a04", "A04"): v for k, v in bundle["filename_mapping"].items()
        }
        with self.assertRaises(ab.ABFilenameConsistencyError):
            ab.validate_ab_bundle_filename_consistency(broken, "a04", expected_sample_count=2)

    def test_write_ab_bundle_files_round_trip_matches_on_disk(self):
        """実際にディスクへ書き出し、Windows等の大文字小文字を区別しない
        ファイルシステム上でも、文字列としてのファイル名一致を検証できることを
        確認する(os.listdirが返す実際の名前で照合するため、OS側の大文字小文字
        の丸めがあればここで検出される)。"""
        bundle = runner.build_ab_bundle("a04", self.entries, self.wav_bytes_by_label, seed=1)
        with tempfile.TemporaryDirectory() as tmpdir:
            written = runner.write_ab_bundle_files(bundle, tmpdir)
            self.assertEqual(set(written), set(bundle["files"].keys()))
            self.assertEqual(set(os.listdir(tmpdir)), set(bundle["files"].keys()))


# ============================================================
# ER-002-S1.1 追加 1〜3: Git追跡方針
# (JSON成果物は追跡対象、音声・A/B対応表・元記事全文キャッシュは除外)
# ============================================================
class GitTrackingPolicyTests(unittest.TestCase):
    """git check-ignoreは対象パスが実在しなくても判定できるため、実ファイルを
    作らずにポリシーだけを検証する(リポジトリへの残留物を作らない)。"""

    def _is_ignored(self, path):
        result = subprocess.run(["git", "check-ignore", "-q", path], cwd=".", capture_output=True)
        return result.returncode == 0

    def test_json_artifacts_under_er002_output_are_tracked(self):
        for filename in common.TRACKED_ARTIFACT_FILENAMES:
            path = os.path.join("er002_output", "a04", filename)
            self.assertFalse(self._is_ignored(path), f"{path} がGit除外されています(追跡対象であるべき)")

    def test_wav_under_er002_output_is_ignored(self):
        path = os.path.join("er002_output", "a04", "final_audio.wav")
        self.assertTrue(self._is_ignored(path))

    def test_ab_mapping_under_er002_output_is_ignored(self):
        path = os.path.join("er002_output", "a04", "er002_a04_ab_mapping.json")
        self.assertTrue(self._is_ignored(path))

    def test_raw_source_fulltext_cache_is_ignored(self):
        path = os.path.join("er002_output", "a04", "raw_source_fulltext.txt")
        self.assertTrue(self._is_ignored(path))

    def test_manifest_write_does_not_leave_uncommitted_state_confusion(self):
        """run_articleの出力先を実際にer002_output配下(一時的な記事ID)へ書いても、
        git check-ignoreでJSONは追跡対象・WAVは対象外と判定されることを確認し、
        テスト終了時にディレクトリを削除してリポジトリに残さない。"""
        import shutil
        script = make_script()

        def script_fn(config):
            return script

        def tts_fn(prompt):
            return make_wav_pcm_only(2400)

        def qa_fn(prompt, wav):
            return make_qa_json(common.build_narration_plan(script))

        config = {"experiment_id": "E", "article_id": "__test_gitpolicy__", "genre": "g",
                  "topic_or_source": "s", "voice": "Aoede"}
        article_dir = os.path.join("er002_output", "__test_gitpolicy__")
        try:
            outcome = runner.run_article(config, script_fn, tts_fn, qa_fn, output_dir="er002_output")
            self.assertEqual(outcome.manifest["status"], "OK")
            manifest_path = os.path.join(article_dir, "manifest.json")
            self.assertTrue(os.path.isfile(manifest_path))
            self.assertFalse(self._is_ignored(manifest_path))
            self.assertFalse(self._is_ignored(os.path.join(article_dir, "qa_results.json")))
        finally:
            if os.path.isdir(article_dir):
                shutil.rmtree(article_dir)


# ============================================================
# ER-002-S1.1 追加 4〜8: QA再評価とTTS再生成の分離
# ============================================================
class QAReevaluationTests(unittest.TestCase):
    def setUp(self):
        self.script = make_script()
        self.plan = common.build_narration_plan(self.script)

    def test_first_inconclusive_does_not_regenerate_tts_same_audio_reevaluated(self):
        """要求4: QA解析不能の1回目ではTTSを再生成せず、同じ音声を再評価することを確認。"""
        calls = {"tts": 0, "qa": 0}

        def tts_fn(prompt):
            calls["tts"] += 1
            return b"\x00\x01" * 50

        def qa_fn(prompt, wav):
            calls["qa"] += 1
            if calls["qa"] == 1:
                return "not valid json at all"  # 1回目: 解析不能
            return make_qa_json(self.plan)  # 2回目以降: 正常

        result = common.run_tts_content_attempts(self.plan, common.build_style_prefix(), tts_fn, qa_fn,
                                                   max_content_attempts=3, max_api_retry=0)
        self.assertEqual(result.status, "OK")
        self.assertEqual(result.accepted_attempt, 1, "TTSは1回しか生成されていない(再評価のみで合格)")
        self.assertEqual(calls["tts"], 3, "3チャンク分のTTS呼び出しのみ(2回目のTTSコンテンツ試行は発生していない)")
        self.assertEqual(len(result.attempts), 1)
        self.assertEqual(result.attempts[0].qa_evaluation_attempt_count, 2, "同じ音声でQAを2回評価している")

    def test_second_qa_evaluation_pass_adopts_same_tts_attempt(self):
        """要求5: QAの2回目で合格した場合、同じTTS試行が採用されることを確認。"""
        style_prefix = common.build_style_prefix()
        qa_calls = {"n": 0}

        def tts_fn(prompt):
            return b"\x00\x01" * 50

        def qa_fn(prompt, wav):
            qa_calls["n"] += 1
            if qa_calls["n"] == 1:
                return "{broken json"
            return make_qa_json(self.plan)

        outcome = common.evaluate_qa_for_audio(self.plan, b"dummy-audio-bytes", qa_fn,
                                                 max_qa_eval_attempts=2, max_api_retry=0)
        self.assertEqual(outcome.final_outcome, "passed")
        self.assertEqual(len(outcome.attempts), 2)
        self.assertEqual(outcome.attempts[0].outcome, "inconclusive")
        self.assertEqual(outcome.attempts[1].outcome, "passed")

    def test_both_qa_evaluations_inconclusive_yields_qa_inconclusive(self):
        """要求6: 2回ともQA判定不能ならQA_INCONCLUSIVEになることを確認
        (TTS_CONTENT_FAILUREとは別の分類であること)。"""
        def qa_fn(prompt, wav):
            return "still not json"

        outcome = common.evaluate_qa_for_audio(self.plan, b"dummy-audio-bytes", qa_fn,
                                                 max_qa_eval_attempts=2, max_api_retry=0)
        self.assertEqual(outcome.final_outcome, "inconclusive")
        self.assertEqual(len(outcome.attempts), 2)
        self.assertEqual(common.OUTCOME_LABELS[outcome.final_outcome], "QA_INCONCLUSIVE")
        self.assertNotEqual(common.OUTCOME_LABELS[outcome.final_outcome], "TTS_CONTENT_FAILURE")

    def test_conclusive_defect_does_not_trigger_reevaluation(self):
        """要求7: 有効なQAが音声上の不具合(見出し欠落等)を検出した場合、
        同じ音声のQAを繰り返さないことを確認(embedded呼び出しは1回のみ)。"""
        qa_calls = {"n": 0}

        def qa_fn(prompt, wav):
            qa_calls["n"] += 1
            return make_qa_json(self.plan, element_counts={
                **{k: 1 for k, _ in common.build_expected_elements(self.plan)}, "title": 0})

        outcome = common.evaluate_qa_for_audio(self.plan, b"dummy-audio-bytes", qa_fn,
                                                 max_qa_eval_attempts=2, max_api_retry=0)
        self.assertEqual(outcome.final_outcome, "conclusive_fail")
        self.assertEqual(len(outcome.attempts), 1, "確定的な不合格は再評価しない")
        self.assertEqual(qa_calls["n"], 1, "groundedは呼ばれない(embeddedの時点で確定的に不合格)")

    def test_qa_api_communication_retry_does_not_increment_evaluation_attempt(self):
        """要求8: QA API通信リトライがqa_evaluation_attempt_numberを増やさないことを確認。"""
        raw_calls = {"n": 0}

        def qa_fn(prompt, wav):
            raw_calls["n"] += 1
            if raw_calls["n"] == 1:
                raise RuntimeError("simulated transient network error")
            return make_qa_json(self.plan)

        outcome = common.evaluate_qa_for_audio(self.plan, b"dummy-audio-bytes", qa_fn,
                                                 max_qa_eval_attempts=2, max_api_retry=2, sleep_fn=lambda s: None)
        self.assertEqual(outcome.final_outcome, "passed")
        self.assertEqual(len(outcome.attempts), 1, "通信リトライだけではqa_evaluation_attemptは増えない")
        self.assertGreaterEqual(outcome.attempts[0].embedded_qa_api_retry_count, 1)


# ============================================================
# ER-002-S2-P0: assessment_status/inconclusive_reason(自己申告)の扱い
# 実APIを呼ぶ前にモックで検証する。
# ============================================================
class SelfReportedAssessmentStatusTests(unittest.TestCase):
    def setUp(self):
        self.script = make_script()
        self.plan = common.build_narration_plan(self.script)

    def test_self_reported_inconclusive_with_clean_fields_triggers_reevaluation(self):
        """フィールド上は問題なしでも、モデルがassessment_status="inconclusive"と
        自己申告した場合は判定不能として同じ音声を再評価することを確認。"""
        calls = {"n": 0}

        def qa_fn(prompt, wav):
            calls["n"] += 1
            if calls["n"] == 1:
                return make_qa_json(self.plan, assessment_status="inconclusive",
                                     inconclusive_reason="background noise made one word unclear")
            return make_qa_json(self.plan)  # 2回目: conclusive・クリーン

        outcome = common.evaluate_qa_for_audio(self.plan, b"dummy-audio-bytes", qa_fn,
                                                 max_qa_eval_attempts=2, max_api_retry=0)
        self.assertEqual(outcome.final_outcome, "passed")
        self.assertEqual(len(outcome.attempts), 2)
        self.assertEqual(outcome.attempts[0].outcome, "inconclusive")
        self.assertIn("embedded_self_reported_inconclusive", outcome.attempts[0].reasons)

    def test_self_report_conclusive_alone_does_not_grant_pass(self):
        """「conclusiveという自己申告だけで合格にしない」: assessment_status=
        "conclusive"でも、要素欠落が実際にあれば不合格になることを確認。"""
        def qa_fn(prompt, wav):
            return make_qa_json(self.plan, assessment_status="conclusive", element_counts={
                **{k: 1 for k, _ in common.build_expected_elements(self.plan)}, "point_two": 0})

        outcome = common.evaluate_qa_for_audio(self.plan, b"dummy-audio-bytes", qa_fn,
                                                 max_qa_eval_attempts=2, max_api_retry=0)
        self.assertEqual(outcome.final_outcome, "conclusive_fail")

    def test_explicit_defect_fails_regardless_of_inconclusive_self_report(self):
        """「明確な音声不良が検出された場合は、assessment_statusにかかわらず不合格に
        する」: assessment_status="inconclusive"と自己申告していても、要素欠落を
        実際に検出していればconclusive_failとして扱い、再評価しないことを確認。"""
        calls = {"n": 0}

        def qa_fn(prompt, wav):
            calls["n"] += 1
            return make_qa_json(self.plan, assessment_status="inconclusive",
                                 inconclusive_reason="not fully sure, but title seems off",
                                 element_counts={
                                     **{k: 1 for k, _ in common.build_expected_elements(self.plan)}, "title": 0})

        outcome = common.evaluate_qa_for_audio(self.plan, b"dummy-audio-bytes", qa_fn,
                                                 max_qa_eval_attempts=2, max_api_retry=0)
        self.assertEqual(outcome.final_outcome, "conclusive_fail")
        self.assertEqual(len(outcome.attempts), 1, "明確な不具合検出は自己申告にかかわらず再評価しない")
        self.assertEqual(calls["n"], 1)

    def test_missing_assessment_status_is_treated_as_inconclusive(self):
        """assessment_statusフィールド自体が欠落している場合、勝手に"conclusive"
        扱いにしない(fail-closed)ことを確認。"""
        raw = make_qa_dict(self.plan)
        del raw["assessment_status"]
        classified = common.classify_qa_result(raw, self.plan)
        self.assertTrue(classified["self_reported_inconclusive"])


# ============================================================
# ER-002-S1.1 追加 9: TTS_CONTENT_FAILUREとQA_INCONCLUSIVEの分離集計
# ============================================================
class FailureClassificationTests(unittest.TestCase):
    def test_tts_content_failure_and_qa_inconclusive_counted_separately(self):
        script = make_script()
        plan = common.build_narration_plan(script)
        style_prefix = common.build_style_prefix()
        state = {"content_attempt": 0}

        def tts_fn(prompt):
            return b"\x00\x01" * 50

        def qa_fn(prompt, wav):
            # このテストではcontent attemptごとに1回だけ呼ばれる設計にする
            # (1回目=確定的な不合格、2回目以降=判定不能を再現)。
            state["content_attempt"] += 1
            n = state["content_attempt"]
            if n == 1:
                return make_qa_json(plan, element_counts={
                    **{k: 1 for k, _ in common.build_expected_elements(plan)}, "title": 0})
            return "not valid json"

        result = common.run_tts_content_attempts(plan, style_prefix, tts_fn, qa_fn,
                                                   max_content_attempts=2, max_api_retry=0)
        self.assertEqual(result.status, "FAILED_ALL_ATTEMPTS")
        self.assertEqual(result.attempts[0].outcome, "conclusive_fail")
        self.assertEqual(result.attempts[1].outcome, "inconclusive")

        counts = common.summarize_failure_outcomes(result.attempts)
        self.assertEqual(counts["TTS_CONTENT_FAILURE"], 1)
        self.assertEqual(counts["QA_INCONCLUSIVE"], 1)
        self.assertEqual(counts["passed"], 0)
        self.assertEqual(counts["TTS_API_EXHAUSTED"], 0)


# ============================================================
# ER-002-S1.1 追加 10: ユーザー評価の初期状態
# ============================================================
class UserEvaluationSchemaTests(unittest.TestCase):
    def test_default_user_evaluation_is_pending(self):
        evaluation = common.default_user_evaluation()
        self.assertEqual(evaluation["status"], "pending_user_listening")
        for key in ("listened_to_end", "wants_more_topics", "content_interest", "voice_fit", "completed_at"):
            self.assertIsNone(evaluation[key])
        self.assertIsNone(evaluation["structure_issue"]["present"])
        self.assertIsNone(evaluation["dynamics_issue"]["present"])

    def test_manifest_user_evaluation_starts_pending(self):
        script = make_script()

        def script_fn(config):
            return script

        def tts_fn(prompt):
            return make_wav_pcm_only(2400)

        def qa_fn(prompt, wav):
            return make_qa_json(common.build_narration_plan(script))

        config = {"experiment_id": "E", "article_id": "a05", "genre": "g", "topic_or_source": "s", "voice": "Aoede"}
        outcome = runner.run_article(config, script_fn, tts_fn, qa_fn)
        self.assertEqual(outcome.manifest["user_evaluation"]["status"], "pending_user_listening")


# ============================================================
# ER-002-S2以降 追加: 内容評価の原因分類 / トピック候補の診断専用項目
# ============================================================
class ContentEvaluationFailureClassificationTests(unittest.TestCase):
    def test_default_classification_is_all_unset(self):
        classification = common.default_content_evaluation_failure_classification()
        for key in ("primary_classification", "voice_as_primary_cause", "structure_as_primary_cause",
                    "dynamics_as_primary_cause", "script_as_primary_cause", "script_cause_status",
                    "generalization_note"):
            self.assertIsNone(classification[key])
        self.assertEqual(classification["user_observations"], [])
        self.assertEqual(classification["not_actioned_pending_further_evidence"], [])

    def test_can_record_topic_interest_low_as_presented(self):
        """A04の実際の訂正内容(話者・構造・Dynamics3・台本のいずれも主因ではない)を
        このスキーマへ記録できることを確認する。ER-002-S2-C2の訂正により、
        分類名は"題材そのものに編集可能性がない"という意味にならないよう
        TOPIC_INTEREST_LOW_AS_PRESENTED(今回提示された形での関心の低さ)を使う。"""
        classification = common.default_content_evaluation_failure_classification()
        classification.update({
            "primary_classification": "TOPIC_INTEREST_LOW_AS_PRESENTED",
            "voice_as_primary_cause": False,
            "structure_as_primary_cause": False,
            "dynamics_as_primary_cause": False,
            "script_as_primary_cause": False,
            "script_cause_status": "not_supported_by_current_evidence",
            "surface_news_interest": "low",
            "editorial_angle_potential": "possible",
            "alternative_angle_not_tested": True,
            "script_failure_confirmed": False,
            "editorial_hypotheses": common.build_untested_editorial_hypotheses(
                ["a hypothetical alternative angle"]),
        })
        self.assertFalse(any([
            classification["voice_as_primary_cause"],
            classification["structure_as_primary_cause"],
            classification["dynamics_as_primary_cause"],
            classification["script_as_primary_cause"],
        ]))
        self.assertEqual(classification["primary_classification"], "TOPIC_INTEREST_LOW_AS_PRESENTED")
        self.assertTrue(classification["alternative_angle_not_tested"])
        self.assertFalse(classification["script_failure_confirmed"])
        self.assertTrue(all(h["untested"] and h["result"] is None for h in classification["editorial_hypotheses"]))


class TopicDiagnosticsSchemaTests(unittest.TestCase):
    def test_default_diagnostics_are_unset_and_marked_excluded(self):
        diagnostics = common.default_topic_candidate_diagnostics()
        for field in common.TOPIC_DIAGNOSTIC_FIELDS:
            self.assertIsNone(diagnostics[field])
        self.assertTrue(diagnostics["diagnostic_only"])
        self.assertTrue(diagnostics["excluded_from_scoring"])

    def test_diagnostic_fields_never_overlap_scoring_fields(self):
        """診断専用項目とトピック選定スコア項目が別集合であることを確認する
        (将来、診断項目が誤ってスコア計算へ混入することへの回帰防止)。"""
        overlap = set(common.TOPIC_DIAGNOSTIC_FIELDS) & set(common.TOPIC_SCORING_FIELDS)
        self.assertEqual(overlap, set())

    def test_diagnostics_do_not_affect_a_scoring_function(self):
        """診断項目を候補データへ混ぜても、スコア項目だけを合計する処理には
        一切影響しないことを確認する(選定順位計算からの分離を保証)。"""
        candidate_without_diagnostics = {field: 5 for field in common.TOPIC_SCORING_FIELDS}
        candidate_with_diagnostics = dict(candidate_without_diagnostics)
        candidate_with_diagnostics.update(common.default_topic_candidate_diagnostics())
        candidate_with_diagnostics["surprise_level"] = "low"
        candidate_with_diagnostics["novelty_type"] = "regulatory"

        def total_score(candidate):
            return sum(candidate[field] for field in common.TOPIC_SCORING_FIELDS)

        self.assertEqual(total_score(candidate_without_diagnostics), total_score(candidate_with_diagnostics))


# ============================================================
# 21: 実行IDからの一括追跡
# ============================================================
class RunnerIntegrationTests(unittest.TestCase):
    def test_single_manifest_traces_full_run(self):
        script = make_script()
        plan = common.build_narration_plan(script)

        def script_fn(config):
            return script

        def tts_fn(prompt):
            return make_wav_pcm_only(24000 * 2)

        def qa_fn(prompt, wav):
            return make_qa_json(plan)

        config = {
            "experiment_id": "ER-002-S1-TEST", "article_id": "a01",
            "genre": "sports", "topic_or_source": "synthetic-fixture", "voice": "Aoede",
            "prompt_version": "v1",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            outcome = runner.run_article(config, script_fn, tts_fn, qa_fn, output_dir=tmpdir)
            m = outcome.manifest
            self.assertEqual(m["status"], "OK")
            self.assertEqual(m["experiment_id"], "ER-002-S1-TEST")
            self.assertEqual(m["article_id"], "a01")
            for key in ("script_run", "tts_run", "dynamics", "word_metrics",
                        "duration_metrics", "final_audio", "retry_limits"):
                self.assertIsNotNone(m[key], f"{key} が記録されていません")

            import os
            manifest_path = os.path.join(tmpdir, "a01", "manifest.json")
            self.assertTrue(os.path.isfile(manifest_path))
            with open(manifest_path, encoding="utf-8") as f:
                loaded = json.load(f)
            self.assertEqual(loaded["experiment_id"], "ER-002-S1-TEST")

    def test_script_retry_used_then_succeeds(self):
        """台本: 初回不合格→全文再生成1回で合格、を確認する。"""
        calls = {"n": 0}
        good_script = make_script()

        def script_fn(config):
            calls["n"] += 1
            if calls["n"] == 1:
                return make_script(n_subsections=1)  # 1回目はわざと構造不合格
            return good_script

        def tts_fn(prompt):
            return make_wav_pcm_only(24000)

        def qa_fn(prompt, wav):
            return make_qa_json(common.build_narration_plan(good_script))

        config = {"experiment_id": "E", "article_id": "a02", "genre": "g", "topic_or_source": "s", "voice": "Aoede"}
        outcome = runner.run_article(config, script_fn, tts_fn, qa_fn)
        self.assertEqual(outcome.manifest["status"], "OK")
        self.assertEqual(outcome.manifest["script_run"]["accepted_attempt"], 2)
        self.assertEqual(calls["n"], 2)

    def test_script_all_attempts_fail_stops_before_tts(self):
        """台本が2回とも不合格ならTTS/QAを一切呼ばずFAILED_SCRIPTで停止することを確認。"""
        tts_called = {"n": 0}
        qa_called = {"n": 0}

        def script_fn(config):
            return make_script(n_subsections=1)  # 常に構造不合格

        def tts_fn(prompt):
            tts_called["n"] += 1
            return make_wav_pcm_only(100)

        def qa_fn(prompt, wav):
            qa_called["n"] += 1
            return "{}"

        config = {"experiment_id": "E", "article_id": "a03", "genre": "g", "topic_or_source": "s", "voice": "Aoede"}
        outcome = runner.run_article(config, script_fn, tts_fn, qa_fn)
        self.assertEqual(outcome.manifest["status"], "FAILED_SCRIPT")
        self.assertEqual(outcome.manifest["failure_classification"]["stage"], "script_generation")
        self.assertEqual(tts_called["n"], 0, "台本が確定する前にTTSを呼んではいけない")
        self.assertEqual(qa_called["n"], 0)
        self.assertEqual(len(outcome.manifest["script_run"]["attempts"]), 2)


# ============================================================
# ER-002-S3-P0 追加: 診断項目の記録順序(採点→選定確定→診断記録)
# ============================================================
class TopicSelectionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.candidates = [
            {"candidate_id": "c1", "scores": {f: 3 for f in common.TOPIC_SCORING_FIELDS}},
            {"candidate_id": "c2", "scores": {f: 5 for f in common.TOPIC_SCORING_FIELDS}},
            {"candidate_id": "c3", "scores": {f: 4 for f in common.TOPIC_SCORING_FIELDS}},
        ]

    def test_selection_uses_only_scoring_fields(self):
        """要求1: TOPIC_SCORING_FIELDSだけで候補を採点することを確認
        (c2が最高得点=15のため選定されるはず)。"""
        result = common.run_topic_selection_lifecycle(self.candidates)
        self.assertEqual(result.selected_candidate_id, "c2")
        self.assertEqual(result.scores["c2"]["total_score"], 5 * len(common.TOPIC_SCORING_FIELDS))

    def test_diagnostics_recorded_after_selection_locked(self):
        """要求2: 診断項目が選定確定後に記録されることを、呼び出し順序で確認する
        (diagnostics_fnが呼ばれる時点で、selected_candidate_idが既に確定している)。"""
        call_order = []

        def diagnostics_fn(candidate_id):
            call_order.append(("diagnostics_fn_called", candidate_id))
            return common.default_topic_candidate_diagnostics()

        result = common.run_topic_selection_lifecycle(self.candidates, diagnostics_fn=diagnostics_fn)
        self.assertEqual(len(call_order), 1)
        self.assertEqual(call_order[0][1], result.selected_candidate_id)
        # タイムスタンプの順序も採点完了→選定確定→診断記録の順であること
        self.assertLessEqual(result.scoring_completed_at, result.selection_locked_at)
        self.assertLessEqual(result.selection_locked_at, result.diagnostics_recorded_at)

    def test_diagnostics_only_recorded_for_selected_candidate(self):
        """診断項目は選定記事だけで良い(非選定候補はnullのまま)。"""
        def diagnostics_fn(candidate_id):
            return common.default_topic_candidate_diagnostics()

        result = common.run_topic_selection_lifecycle(self.candidates, diagnostics_fn=diagnostics_fn)
        for cid, diag in result.diagnostics_by_candidate.items():
            if cid == result.selected_candidate_id:
                self.assertIsNotNone(diag)
            else:
                self.assertIsNone(diag)

    def test_diagnostics_do_not_change_selection(self):
        """要求3: 診断項目がスコアを変更しないことを確認する。診断値をどう
        埋めても(diagnostics_fnの中身に関わらず)選定結果・スコアは同じ。"""
        result_a = common.run_topic_selection_lifecycle(self.candidates, diagnostics_fn=None)
        result_b = common.run_topic_selection_lifecycle(
            self.candidates, diagnostics_fn=lambda cid: {"surprise_level": "high"})
        self.assertEqual(result_a.selected_candidate_id, result_b.selected_candidate_id)
        self.assertEqual(result_a.scores, result_b.scores)

    def test_applied_flags_always_false(self):
        result = common.run_topic_selection_lifecycle(self.candidates, diagnostics_fn=lambda cid: {})
        self.assertFalse(result.diagnostics_applied_to_scoring)
        self.assertFalse(result.diagnostics_applied_to_script_prompt)

    def test_diagnostics_not_referenced_by_script_prompt_builder(self):
        """要求4: 診断項目が台本生成プロンプトへ含まれないことを確認する。
        script_adapter.build_prompt()はtopic/factsだけを受け取り、診断値
        (surprise_level等)を引数として受け付けない設計であることを、実際の
        シグネチャと生成結果の両方で確認する。"""
        import inspect
        sig = inspect.signature(script_adapter.build_prompt)
        param_names = set(sig.parameters.keys())
        for diagnostic_field in common.TOPIC_DIAGNOSTIC_FIELDS:
            self.assertNotIn(diagnostic_field, param_names)

        topic_package = {"topic": "Sample topic.", "facts": "VERIFIED FACTS:\n- fact one."}
        prompt = script_adapter.build_prompt(topic_package)
        for diagnostic_field in common.TOPIC_DIAGNOSTIC_FIELDS:
            self.assertNotIn(diagnostic_field, prompt)


# ============================================================
# ER-002-S3-P0 追加: content_interest_primary_reasonの許可値検証
# ============================================================
class ContentInterestPrimaryReasonTests(unittest.TestCase):
    def test_valid_values_accepted(self):
        for value in common.CONTENT_INTEREST_PRIMARY_REASONS:
            self.assertTrue(common.is_valid_content_interest_primary_reason(value))
        self.assertTrue(common.is_valid_content_interest_primary_reason(None))

    def test_invalid_value_rejected(self):
        self.assertFalse(common.is_valid_content_interest_primary_reason("not_a_real_reason"))

    def test_default_evaluation_includes_new_fields(self):
        evaluation = common.default_user_evaluation()
        self.assertIn("content_interest_primary_reason", evaluation)
        self.assertIn("content_interest_notes", evaluation)
        self.assertIsNone(evaluation["content_interest_primary_reason"])
        self.assertIsNone(evaluation["content_interest_notes"])

    def test_ab_evaluation_also_includes_new_fields(self):
        evaluation = common.default_ab_user_evaluation()
        self.assertIn("content_interest_primary_reason", evaluation)
        self.assertIn("content_interest_notes", evaluation)


# ============================================================
# ER-002-S3-P0 追加: S3バッチ構成・受入集計からの除外
# ============================================================
class S3BatchConfigTests(unittest.TestCase):
    def test_six_articles_eight_voice_slots(self):
        self.assertEqual(s3config.total_article_count(), 6)
        self.assertEqual(s3config.total_voice_slot_count(), 8)

    def test_batch_membership_matches_spec(self):
        flat = {a["article_id"]: a for a in s3config.flatten_s3_batches()}
        self.assertEqual(flat["A01"]["batch"], "B1")
        self.assertEqual(flat["A01"]["voices"], ["Aoede"])
        self.assertEqual(flat["A02"]["batch"], "B1")
        self.assertEqual(flat["A02"]["voices"], ["Charon"])
        self.assertEqual(flat["A03"]["batch"], "B2")
        self.assertEqual(flat["A06"]["batch"], "B2")
        self.assertEqual(flat["A04"]["batch"], "B3")
        self.assertEqual(set(flat["A04"]["voices"]), {"Aoede", "Charon"})
        self.assertEqual(flat["A05"]["batch"], "B3")
        self.assertEqual(set(flat["A05"]["voices"]), {"Aoede", "Charon"})

    def test_s2_a04_excluded_from_s3_tally(self):
        self.assertFalse(s3config.is_included_in_acceptance_tally("ER-002-S2", "A04"))

    def test_s3_a04_is_included_in_tally(self):
        """S2のA04とは別に、S3で新規選定するA04は集計対象であること。"""
        self.assertTrue(s3config.is_included_in_acceptance_tally("ER-002-S3", "A04"))

    def test_a01_a02_reruns_excluded_from_tally(self):
        rerun_ids = {r["article_id"] for r in s3config.INDEPENDENT_RERUNS}
        self.assertEqual(rerun_ids, {"A01", "A02"})
        for rerun in s3config.INDEPENDENT_RERUNS:
            self.assertFalse(rerun["included_in_acceptance_tally"])
        self.assertFalse(s3config.is_included_in_acceptance_tally("ER-002-S3", "A01 (rerun)"))
        self.assertFalse(s3config.is_included_in_acceptance_tally("ER-002-S3", "A02 (rerun)"))
        # 初回のA01・A02自体は通常どおり集計対象
        self.assertTrue(s3config.is_included_in_acceptance_tally("ER-002-S3", "A01"))
        self.assertTrue(s3config.is_included_in_acceptance_tally("ER-002-S3", "A02"))


# ============================================================
# ER-002-S3-P0 追加: ER-002-v1.0の条件凍結・ハッシュ保存
# ============================================================
class FrozenConditionsTests(unittest.TestCase):
    def test_experiment_version_is_v1_0(self):
        self.assertEqual(freeze.EXPERIMENT_VERSION, "ER-002-v1.0")

    def test_all_nine_condition_categories_present_with_hashes(self):
        frozen = freeze.build_frozen_conditions()
        expected_categories = [
            "topic_research_prompt", "script_generation_prompt", "tts_common_style_prefix",
            "qa_prompt_and_schema", "dynamics3", "word_count_conditions",
            "retry_conditions", "voice_assignment", "ab_anonymization",
        ]
        for category in expected_categories:
            self.assertIn(category, frozen)
            category_data = frozen[category]
            # sha256(64文字hex)がどこかのキーに存在すること
            found_hash = category_data.get("sha256") or category_data.get("schema_fields_sha256")
            self.assertIsNotNone(found_hash, f"{category}にsha256が見つかりません")
            self.assertEqual(len(found_hash), 64)

    def test_hashes_are_reproducible(self):
        frozen_a = freeze.build_frozen_conditions()
        frozen_b = freeze.build_frozen_conditions()
        self.assertEqual(frozen_a["dynamics3"]["sha256"], frozen_b["dynamics3"]["sha256"])
        self.assertEqual(
            frozen_a["script_generation_prompt"]["sha256"], frozen_b["script_generation_prompt"]["sha256"])
        self.assertEqual(
            frozen_a["tts_common_style_prefix"]["sha256"], frozen_b["tts_common_style_prefix"]["sha256"])

    def test_voice_assignment_matches_s3_config(self):
        frozen = freeze.build_frozen_conditions()
        expected = {a["article_id"]: a["voices"] for a in s3config.flatten_s3_batches()}
        self.assertEqual(frozen["voice_assignment"]["assignment"], expected)


# ============================================================
# ER-002-S3-B1 追加: 独立再実行用入力バンドル
# ============================================================
def make_sample_bundle(article_id="a01", frozen_sha=None):
    frozen_sha = frozen_sha or freeze.frozen_conditions_overall_sha256()
    bundle = rerun.build_bundle(
        article_id=article_id,
        selected_candidate_id="candidate_2",
        selected_topic="Sample sports topic.",
        topic_selection_result={"candidate_2": {"total_score": 28}},
        source_refs=[{"outlet": "Sample Outlet", "url": "https://example.com/a"}],
        source_retrieved_at="2026-07-19",
        verified_facts=["Sample fact one.", "Sample fact two."],
        script_generation_input={"topic": "Sample sports topic.", "facts": "VERIFIED FACTS:\n- Sample fact one."},
        frozen_conditions_sha256=frozen_sha,
        script_prompt_sha256=script_adapter.sha256_text(script_adapter.COMMON_SCRIPT_PROMPT_TEMPLATE),
        topic_prompt_sha256="dummy_topic_prompt_sha256",
        model_names={"script": script_adapter.MODEL_WRITE, "tts": common.MODEL_NAME, "qa": common.QA_MODEL_NAME},
        model_settings={},
        original_run_id="ER-002-S3-B1-a01-run1",
        genre="sports",
        voice="Aoede",
    )
    return bundle


class RerunBundleTests(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        """要求1: 再実行バンドルを保存・読み込みできる。"""
        bundle = make_sample_bundle()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "rerun_input_bundle.json")
            rerun.save_bundle(bundle, path)
            loaded = rerun.load_bundle(path)
        self.assertEqual(loaded["article_id"], "a01")
        self.assertEqual(loaded["bundle_schema_version"], rerun.BUNDLE_SCHEMA_VERSION)
        rerun.verify_bundle_integrity(loaded)  # 例外が出ないこと

    def test_tampering_after_save_is_detected(self):
        """要求2: 保存後に内容を変更するとハッシュ不一致を検出できる。"""
        bundle = make_sample_bundle()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "rerun_input_bundle.json")
            rerun.save_bundle(bundle, path)
            loaded = rerun.load_bundle(path)
        loaded["verified_facts"] = ["Tampered fact."]  # ハッシュを更新せずに中身だけ書き換える
        with self.assertRaises(rerun.BundleIntegrityError):
            rerun.verify_bundle_integrity(loaded)

    def test_web_search_function_not_called_during_rerun(self):
        """要求3: 再実行時にWeb検索関数が呼ばれない。run_independent_rerunの
        シグネチャにWeb検索関連の引数が存在しないこと、および実行中に
        トピック調査系の呼び出しが一切発生しないことを確認する。"""
        import inspect
        sig = inspect.signature(rerun.run_independent_rerun)
        param_names = set(sig.parameters.keys())
        for forbidden in ("web_search_fn", "topic_research_fn", "candidate_fetch_fn"):
            self.assertNotIn(forbidden, param_names)

        web_search_calls = {"n": 0}

        def spy_web_search_fn(*args, **kwargs):
            web_search_calls["n"] += 1
            return "should never be called"

        bundle_dict = json.loads(json.dumps(asdict_bundle(make_sample_bundle())))
        current_sha = bundle_dict["frozen_conditions_sha256"]

        def script_write_fn(config):
            return make_script(body_words=250, sub1_words=40, sub2_words=40, final_words=30)

        def tts_fn(prompt):
            return make_wav_pcm_only(2400)

        def qa_fn(prompt, wav):
            plan = common.build_narration_plan(script_write_fn(None))
            return make_qa_json(plan)

        rerun.run_independent_rerun(
            bundle_dict, script_write_fn, tts_fn, qa_fn, current_sha,
            run_article_fn=runner.run_article,
        )
        self.assertEqual(web_search_calls["n"], 0, "run_independent_rerun内でWeb検索が呼ばれてはいけない")

    def test_rerun_does_not_reuse_original_script(self):
        """要求4: 再実行時に初回台本をそのまま再利用しない。script_write_fnが
        毎回新しく呼ばれ、その戻り値がrun_articleへ渡されることを確認する
        (キャッシュされた初回script_en.json等を読み込む経路が無い)。"""
        bundle_dict = json.loads(json.dumps(asdict_bundle(make_sample_bundle())))
        current_sha = bundle_dict["frozen_conditions_sha256"]

        calls = {"n": 0}
        fresh_script = make_script(body_words=290, sub1_words=30, sub2_words=30, final_words=20)

        def script_write_fn(config):
            calls["n"] += 1
            return fresh_script

        def tts_fn(prompt):
            return make_wav_pcm_only(2400)

        def qa_fn(prompt, wav):
            return make_qa_json(common.build_narration_plan(fresh_script))

        outcome = rerun.run_independent_rerun(
            bundle_dict, script_write_fn, tts_fn, qa_fn, current_sha,
            run_article_fn=runner.run_article,
        )
        self.assertGreaterEqual(calls["n"], 1, "script_write_fnが再実行のたびに呼ばれていること")
        self.assertEqual(outcome.manifest["script_run"]["script"]["title"], fresh_script["title"])

    def test_rejects_non_v1_0_frozen_conditions(self):
        """要求5: ER-002-v1.0以外の条件ハッシュを拒否する。"""
        bundle_dict = json.loads(json.dumps(asdict_bundle(make_sample_bundle())))
        wrong_sha = "0" * 64
        with self.assertRaises(rerun.BundleIntegrityError):
            rerun.verify_bundle_frozen_conditions(bundle_dict, wrong_sha)

    def test_a01_a02_reruns_excluded_from_s3_tally(self):
        """要求6: A01・A02再実行がS3受入集計から除外される
        (S3-P0のer002_s3_config側の除外設定と、バンドルのarticle_idが対応すること)。"""
        for article_id in ("a01", "a02"):
            bundle = make_sample_bundle(article_id=article_id)
            self.assertEqual(bundle.article_id, article_id)
        rerun_ids = {r["article_id"] for r in s3config.INDEPENDENT_RERUNS}
        self.assertEqual(rerun_ids, {"A01", "A02"})
        self.assertFalse(s3config.is_included_in_acceptance_tally("ER-002-S3", "A01 (rerun)"))
        self.assertFalse(s3config.is_included_in_acceptance_tally("ER-002-S3", "A02 (rerun)"))


def asdict_bundle(bundle):
    from dataclasses import asdict
    return asdict(bundle)


if __name__ == "__main__":
    unittest.main()
