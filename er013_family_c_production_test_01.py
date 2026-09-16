# ============================================================
# er013_family_c_production_test_01.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01
#         (委任A: Family C 2仕様のProduction wiring)
# ============================================================
# `er013_family_c_production_01.py`(Family C Story TTS segmentation原則+
# A2 Comment理解ガイド型Contract)の決定的テスト(API呼び出しなし)。
#
# 差し戻し1回目(2026-09-16)で追加: `er013_family_c_production_runner_01.py`
# の全体生成経路(resume/regeneration/ASRキャッシュ/TTS cascade分岐/
# B1のA2 Contract非呼び出し)の決定的テスト(API呼び出しなし、モック使用)。
from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import unittest
from unittest import mock

import er013_family_c_production_01 as fam_c
import er013_family_c_production_runner_01 as runner


class PlanStorySegmentsUnitTests(unittest.TestCase):
    """plan_story_segmentsの単体テスト(承認原則: 同一Voice統合/Voice境界
    分割/Comment境界分割/目安超過分割/短segment許容理由付与/固定値上書き
    なし)。"""

    def test_same_voice_consecutive_paragraphs_merge(self):
        paragraphs = ["Hello there.", "This continues the same idea.", "And a third sentence."]
        flat = fam_c.build_flat_voice_chunks(paragraphs, {})
        segs = fam_c.plan_story_segments(flat)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0]["voice"], "narrator")
        self.assertEqual(segs[0]["source_paragraph_indices"], [0, 1, 2])

    def test_voice_change_forces_split(self):
        paragraphs = ['She said, "I am ready."', "He nodded."]
        flat = fam_c.build_flat_voice_chunks(paragraphs, {"robot": ["robot"]})
        # 引用符はwindowにkeywordが無いためdefault narrator扱いになるが、
        # override指定で強制的にvoice変化を作れることを確認する。
        flat2 = [(0, "narrator", 'She said, '), (0, "robot", '"I am ready."'), (1, "narrator", "He nodded.")]
        segs = fam_c.plan_story_segments(flat2)
        voices = [s["voice"] for s in segs]
        self.assertEqual(voices, ["narrator", "robot", "narrator"])
        # Voice境界による短segmentが理由付きで許容されること
        self.assertIn("分割不可避", segs[1]["split_reason"])

    def test_comment_or_scene_boundary_forces_split_even_if_same_voice(self):
        flat = [(0, "narrator", "Part one."), (1, "narrator", "Part two."), (2, "narrator", "Part three.")]
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={2})
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0]["source_paragraph_indices"], [0, 1])
        self.assertEqual(segs[1]["source_paragraph_indices"], [2])

    def test_word_guideline_auto_split_at_nearest_paragraph_boundary(self):
        long_word_para = " ".join(f"word{i}" for i in range(80))
        long_word_para2 = " ".join(f"term{i}" for i in range(80))
        flat = [(0, "narrator", long_word_para + "."), (1, "narrator", long_word_para2 + ".")]
        segs = fam_c.plan_story_segments(
            flat, target_words=100, soft_max_words=120, hard_avoid_words=150)
        self.assertEqual(len(segs), 2)
        for s in segs:
            self.assertIn("auto_split_hard_avoid_exceeded", s["warnings"][0])
            self.assertLessEqual(s["word_count"], 90)

    def test_hard_avoid_exceeded_unsplittable_single_paragraph_is_warning_only_no_block(self):
        one_giant_paragraph = " ".join(f"word{i}" for i in range(200))
        flat = [(0, "narrator", one_giant_paragraph)]
        segs = fam_c.plan_story_segments(flat, hard_avoid_words=150)
        self.assertEqual(len(segs), 1)
        self.assertTrue(any("hard_avoid_exceeded_unsplittable" in w for w in segs[0]["warnings"]))

    def test_soft_max_exceeded_records_warning_but_does_not_split(self):
        paragraph = " ".join(f"word{i}" for i in range(130))
        flat = [(0, "narrator", paragraph)]
        segs = fam_c.plan_story_segments(flat, soft_max_words=120, hard_avoid_words=150)
        self.assertEqual(len(segs), 1)
        self.assertTrue(any("soft_max_exceeded" in w for w in segs[0]["warnings"]))

    def test_caller_supplied_boundaries_are_not_overwritten_by_fixed_values(self):
        # force_split_before_paragraphsを変えると結果が追随することを確認
        # (固定値で上書きされていないことの確認)。
        flat = [(0, "narrator", "A."), (1, "narrator", "B."), (2, "narrator", "C.")]
        segs_no_force = fam_c.plan_story_segments(flat)
        segs_forced = fam_c.plan_story_segments(flat, force_split_before_paragraphs={1})
        self.assertEqual(len(segs_no_force), 1)
        self.assertEqual(len(segs_forced), 2)


class ApprovedEpisodeReproductionTests(unittest.TestCase):
    """承認済み4 episode(Memory A2/B1、Digital Twins A2/B1)のsegmentationを
    plan_story_segmentsで再現できることを確認する(approved成果物との
    segment数・最長語数一致)。記事本文はProduction module化前のTrial
    出力物(reader_facing_article*.txt)を読むが、本テストはTrial scriptを
    import・実行しない(article_config.jsonの値をここに複製し、production
    moduleのみを検証する)。"""

    def _load_paragraphs(self, path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        return fam_c.split_into_paragraphs(text)

    def test_memory_a2_reproduces_approved_10_segments_max89(self):
        paragraphs = self._load_paragraphs(
            "er013_output/family_c_future_trial_08/memory/reader_facing_article.txt")
        self.assertEqual(len(paragraphs), 29)
        flat = fam_c.build_flat_voice_chunks(
            paragraphs, {"device": ["screen", "device", "robot", "storage unit"], "brother": ["brother"]},
            quote_voice_override_paragraphs={2: "device", 4: "device", 14: "brother"})
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={9, 20, 24})
        self.assertEqual(len(segs), 10)
        self.assertEqual(max(s["word_count"] for s in segs), 89)
        reconstructed = fam_c.reconstruct_article_from_segments(segs, paragraphs)
        self.assertEqual(reconstructed, "\n\n".join(paragraphs))

    def test_memory_b1_reproduces_approved_10_segments_max91(self):
        paragraphs = self._load_paragraphs(
            "er013_output/family_c_episode_trial_10/memory_b1/reader_facing_article_b1.txt")
        self.assertEqual(len(paragraphs), 26)
        flat = fam_c.build_flat_voice_chunks(
            paragraphs, {"device": ["screen", "device", "robot", "storage unit"], "brother": ["brother"]})
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={11, 13, 21})
        self.assertEqual(len(segs), 10)
        self.assertEqual(max(s["word_count"] for s in segs), 91)

    def test_digital_twins_a2_reproduces_approved_22_segments_max99(self):
        paragraphs = self._load_paragraphs(
            "er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt")
        self.assertEqual(len(paragraphs), 33)
        override = {i: "twin" for i in (3, 5, 11, 13, 19, 21, 25)}
        flat = fam_c.build_flat_voice_chunks(
            paragraphs, {"twin": ["echo", "twin", "digital twin"]},
            quote_voice_override_paragraphs=override,
            display_paragraph_voice={16: "twin"},
            restrict_quote_splitting_to_paragraphs=override.keys())
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={23})
        self.assertEqual(len(segs), 22)
        self.assertEqual(max(s["word_count"] for s in segs), 99)
        narrator_n = sum(1 for s in segs if s["voice"] == "narrator")
        twin_n = sum(1 for s in segs if s["voice"] == "twin")
        self.assertEqual((narrator_n, twin_n), (12, 10))

    def test_digital_twins_b1_reproduces_approved_24_segments_max97(self):
        paragraphs = self._load_paragraphs(
            "er013_output/family_c_episode_trial_10/twins_b1/reader_facing_article_b1.txt")
        self.assertEqual(len(paragraphs), 34)
        flat = fam_c.build_flat_voice_chunks(paragraphs, {"twin": ["echo", "twin", "digital twin"]})
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={9})
        self.assertEqual(len(segs), 24)
        self.assertEqual(max(s["word_count"] for s in segs), 97)
        narrator_n = sum(1 for s in segs if s["voice"] == "narrator")
        twin_n = sum(1 for s in segs if s["voice"] == "twin")
        self.assertEqual((narrator_n, twin_n), (13, 11))


class A2CommentQualityCheckTests(unittest.TestCase):
    def test_banned_phrase_detected(self):
        ok, reasons = fam_c.check_a2_comment_quality(
            "さあ、これから始まる物語を聞いてみましょう。" + "あ" * 40)
        self.assertFalse(ok)
        self.assertIn("banned_phrase_found", reasons)

    def test_empty_text_rejected(self):
        ok, reasons = fam_c.check_a2_comment_quality("")
        self.assertFalse(ok)
        self.assertEqual(reasons, ["empty_text"])

    def test_clean_text_within_range_passes(self):
        text = "レナは小さな箱を持っています。" * 3
        ok, reasons = fam_c.check_a2_comment_quality(text, min_chars=10, max_chars=200)
        self.assertTrue(ok)
        self.assertEqual(reasons, [])

    def test_too_short_flagged(self):
        ok, reasons = fam_c.check_a2_comment_quality("短い。", min_chars=40)
        self.assertFalse(ok)
        self.assertTrue(any("too_short" in r for r in reasons))

    def test_prompt_uses_contract_constants(self):
        prompt = fam_c.build_family_c_a2_comment_prompt(1, "テスト事実")
        self.assertIn("テスト事実", prompt)
        self.assertIn("聞いてみましょう", prompt)  # 禁止語句の説明自体は含む(指示文なので正常)


class GenerateFamilyCA2CommentRetryTests(unittest.TestCase):
    """retry/regeneration経路が同一関数(generate_family_c_a2_comment)を
    呼ぶことをモックで確認する(禁止語句が出た場合に同一Contractで
    自動的に再生成し、2回目で合格すれば成功として返すことの確認)。"""

    def test_retries_on_banned_phrase_and_succeeds_with_same_contract(self):
        calls = []

        def fake_run_support_text(client, role_instruction, context_block, model=None):
            calls.append(role_instruction)
            if len(calls) == 1:
                return {"status": "OK", "text": "さあ聞いてみましょう。" + "あ" * 40}
            return {"status": "OK", "text": "レナは小さな銀色の箱を大切に持っています。" * 2}

        result = fam_c.generate_family_c_a2_comment(
            client=None, comment_num=1, article_text="dummy", content_facts="事実X",
            max_retries=1, run_support_text_fn=fake_run_support_text, model="dummy-model")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], calls[1])  # 同一prompt(同一Contract)で再試行
        self.assertTrue(result["ok"])
        self.assertEqual(result["contract"], "FAMILY_C_A2_COMMENT_ROLE_JA_1")

    def test_raises_after_exhausting_retries(self):
        def always_banned(client, role_instruction, context_block, model=None):
            return {"status": "OK", "text": "耳を澄ませてください。" + "い" * 40}

        with self.assertRaises(RuntimeError):
            fam_c.generate_family_c_a2_comment(
                client=None, comment_num=2, article_text="dummy", content_facts="事実Y",
                max_retries=1, run_support_text_fn=always_banned, model="dummy-model")

    def test_b1_comment_not_provided_by_this_contract(self):
        # B1 CommentはこのContractに存在しない(B1誤適用防止の構造的ガード)。
        with self.assertRaises(RuntimeError):
            fam_c.guard_a2_only("b1")
        # 例外を投げない(＝A2は許可)
        fam_c.guard_a2_only("a2")


class TrialScriptIndependenceTests(unittest.TestCase):
    """Production module/runnerがTrial script(er013_family_c_episode_
    trial_1[012]_*.py)をimport・参照しないことのGrepベース確認。"""

    def test_no_trial_script_import_in_production_module(self):
        with open("er013_family_c_production_01.py", encoding="utf-8") as f:
            content = f.read()
        hits = re.findall(r"import\s+er013_family_c_episode_trial|from\s+er013_family_c_episode_trial",
                           content)
        self.assertEqual(hits, [])

    def test_no_trial_script_import_in_runner(self):
        with open("er013_family_c_production_runner_01.py", encoding="utf-8") as f:
            content = f.read()
        hits = re.findall(r"import\s+er013_family_c_episode_trial|from\s+er013_family_c_episode_trial",
                           content)
        self.assertEqual(hits, [])

    def test_no_b1_comment_contract_constants_exist(self):
        """B1 Comment用のFAMILY_C_B1_COMMENT系定数が存在しないこと
        (誤適用防止をコード構造で担保しているという設計の確認)。"""
        with open("er013_family_c_production_01.py", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("FAMILY_C_B1_COMMENT", content)


# ============================================================
# 差し戻し1回目(2026-09-16): runner全体生成経路(resume/regeneration/
# ASRキャッシュ/TTS cascade分岐/B1のA2 Contract非呼び出し)のテスト。
# ============================================================
class RunnerResumableReuseTests(unittest.TestCase):
    """sha256一致時のみresume(skip)し、不一致(本文変更)なら再生成させる
    ことの確認(resumeの正しさそのもの)。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_wav(self, path):
        with open(path, "wb") as f:
            f.write(b"RIFF....WAVEfmt dummy-audio-bytes")

    def test_reuse_when_ok_and_no_meta_upgrades_and_returns_reused(self):
        path = os.path.join(self.tmp, "story_001.wav")
        self._make_wav(path)
        with open(runner._ok_marker_path(path), "w", encoding="utf-8") as f:
            f.write("ok")  # レガシー.ok(Trial由来コピー相当、meta無し)
        result = runner.resumable_reuse(path, runner._sha256_text("hello world"))
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "REUSED_EXISTING_FILE")
        self.assertTrue(os.path.exists(runner._ok_meta_path(path)))

    def test_no_reuse_when_wav_or_ok_missing(self):
        path = os.path.join(self.tmp, "story_002.wav")
        self.assertIsNone(runner.resumable_reuse(path, runner._sha256_text("x")))
        self._make_wav(path)
        self.assertIsNone(runner.resumable_reuse(path, runner._sha256_text("x")))  # .ok無し

    def test_no_reuse_when_text_sha256_mismatches_recorded_meta(self):
        path = os.path.join(self.tmp, "story_003.wav")
        self._make_wav(path)
        with open(runner._ok_marker_path(path), "w", encoding="utf-8") as f:
            f.write("ok")
        with open(runner._ok_meta_path(path), "w", encoding="utf-8") as f:
            json.dump({"tts_text_sha256": runner._sha256_text("original text")}, f)
        # 本文が変わった(sha256が変わった)ケース: resumeしてはいけない。
        result = runner.resumable_reuse(path, runner._sha256_text("changed text"))
        self.assertIsNone(result)


class RunnerPurgeSegmentOutputsTests(unittest.TestCase):
    """`--only-segments`regenerationが対象segmentのみを削除し、他segmentの
    resumeへ影響しないことの確認。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_purge_removes_only_target_segment_files(self):
        for seg_id in ("story_001", "story_002"):
            base = os.path.join(self.tmp, f"{seg_id}.wav")
            with open(base, "wb") as f:
                f.write(b"dummy")
            for suffix in (".ok", ".ok.meta.json", ".debug.json"):
                with open(base + suffix, "w", encoding="utf-8") as f:
                    f.write("x")
        runner.purge_segment_outputs(self.tmp, "story_001")
        for suffix in ("", ".ok", ".ok.meta.json", ".debug.json"):
            self.assertFalse(os.path.exists(os.path.join(self.tmp, f"story_001.wav{suffix}")))
        for suffix in ("", ".ok", ".ok.meta.json", ".debug.json"):
            self.assertTrue(os.path.exists(os.path.join(self.tmp, f"story_002.wav{suffix}")))


class RunnerAsrCacheTests(unittest.TestCase):
    """ASRキャッシュはwav sha256一致時のみ再利用し、不一致・キャッシュ無し
    時は必ず現物ASRを実行すること(名前のみキャッシュを使わないことの確認)。"""

    def test_cache_hit_when_sha256_matches_skips_transcribe(self):
        budget = runner.BudgetTracker(10.0, os.path.join(tempfile.mkdtemp(), "log.jsonl"))
        prev = {"story_001": {"sha256": "abc123", "asr_text": "cached text"}}
        with mock.patch.object(runner.asr_routing, "transcribe",
                                side_effect=AssertionError("must not call transcribe on cache hit")):
            text, cache_hit = runner.get_or_run_asr("story_001", "dummy.wav", "en", budget, prev, "abc123")
        self.assertTrue(cache_hit)
        self.assertEqual(text, "cached text")
        self.assertEqual(budget.spent, 0.0)

    def test_cache_miss_when_sha256_differs_calls_transcribe(self):
        budget = runner.BudgetTracker(10.0, os.path.join(tempfile.mkdtemp(), "log.jsonl"))
        prev = {"story_001": {"sha256": "old_sha", "asr_text": "stale cached text"}}
        with mock.patch.object(runner.asr_routing, "transcribe", return_value=("fresh text", None)) as m:
            text, cache_hit = runner.get_or_run_asr("story_001", "dummy.wav", "en", budget, prev, "new_sha")
        m.assert_called_once()
        self.assertFalse(cache_hit)
        self.assertEqual(text, "fresh text")
        self.assertGreater(budget.spent, 0.0)

    def test_cache_miss_when_no_prev_entry_calls_transcribe(self):
        budget = runner.BudgetTracker(10.0, os.path.join(tempfile.mkdtemp(), "log.jsonl"))
        with mock.patch.object(runner.asr_routing, "transcribe", return_value=("t", None)) as m:
            text, cache_hit = runner.get_or_run_asr("story_009", "dummy.wav", "ja", budget, {}, "sha")
        m.assert_called_once()
        self.assertFalse(cache_hit)


class RunnerTtsCallDispatchTests(unittest.TestCase):
    """既存Production TTS関数への分岐(narrator/device/その他voice_tts_names
    指定voice)が正しいことの確認(cascade自体は各関数の内部実装、ここでは
    「どの既存関数が呼ばれるか」だけをモックで確認する)。"""

    def _budget(self):
        return runner.BudgetTracker(100.0, os.path.join(tempfile.mkdtemp(), "log.jsonl"))

    def test_narrator_calls_verified_strict(self):
        with mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict",
                                return_value={"status": "OK", "path": "p", "sha256": "s"}) as m:
            r = runner.tts_call_for_voice("narrator", "Hello.", "out.wav", "story_001", self._budget(), {})
        m.assert_called_once()
        self.assertEqual(r["status"], "OK")

    def test_device_calls_generate_charon_english(self):
        with mock.patch.object(runner.voice01, "generate_charon_english",
                                return_value={"status": "OK", "path": "p", "sha256": "s"}) as m:
            r = runner.tts_call_for_voice("device", '"Return date?"', "out.wav", "story_002", self._budget(), {})
        m.assert_called_once()
        self.assertEqual(r["status"], "OK")

    def test_custom_voice_uses_voice_tts_names_mapping(self):
        with mock.patch.object(runner.bvoices, "generate_voice_body_wide_margin",
                                return_value={"status": "OK", "path": "p", "sha256": "s"}) as m:
            runner.tts_call_for_voice("brother", "text", "out.wav", "story_007", self._budget(),
                                       {"brother": "Algieba"})
        m.assert_called_once_with("text", "out.wav", "Algieba")

    def test_unknown_voice_without_mapping_raises(self):
        with self.assertRaises(RuntimeError):
            runner.tts_call_for_voice("mystery_voice", "text", "out.wav", "seg", self._budget(), {})


class RunnerB1DoesNotUseA2CommentContractTests(unittest.TestCase):
    """B1経路がA2 Comment理解ガイド型Contract(fam_c.generate_family_c_a2_
    comment)を一切呼ばないことの構造的確認(2箇所のみ存在し、いずれも
    level=="a2"経路[run_comments_only(guard_a2_only)/run_comments_stage_a2
    (run_full_generationのif level == "a2"分岐からのみ呼ばれる)]でのみ
    到達可能であること)。"""

    def test_generate_family_c_a2_comment_called_only_from_a2_only_functions(self):
        with open("er013_family_c_production_runner_01.py", encoding="utf-8") as f:
            content = f.read()
        hits = re.findall(r"fam_c\.generate_family_c_a2_comment\(", content)
        self.assertEqual(len(hits), 2)
        # 呼び出し元関数名の確認(run_comments_only, run_comments_stage_a2のみ)。
        self.assertIn("def run_comments_only(", content)
        self.assertIn("def run_comments_stage_a2(", content)
        run_comments_only_body = content.split("def run_comments_only(", 1)[1].split("\ndef ", 1)[0]
        run_comments_stage_a2_body = content.split("def run_comments_stage_a2(", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("fam_c.generate_family_c_a2_comment(", run_comments_only_body)
        self.assertIn("fam_c.generate_family_c_a2_comment(", run_comments_stage_a2_body)

    def test_run_comments_stage_a2_only_called_from_a2_branch_in_run_full_generation(self):
        with open("er013_family_c_production_runner_01.py", encoding="utf-8") as f:
            content = f.read()
        body = content.split("def run_full_generation(", 1)[1]
        # `if level == "a2":`ブロックの直後にrun_comments_stage_a2呼び出しがあり、
        # b1側(同じインデント段の`    else:`節)には存在しないことを確認する
        # (無関係な内側のif/elseに引っかからないよう、インデント込みで分割する)。
        after_if = body.split('if level == "a2":', 1)[1]
        a2_branch, b1_branch = after_if.split("\n    else:\n", 1)
        # b1_branchはさらに次のトップレベルStageコメントの手前までに絞る
        # (以降の共通stage(assetプロビジョニング等)を誤って含めないため)。
        b1_branch = b1_branch.split("# === Stage: 非Story固定asset", 1)[0]
        self.assertIn("run_comments_stage_a2(", a2_branch)
        self.assertNotIn("run_comments_stage_a2(", b1_branch)
        # コメント中の説明的な言及(誤適用しない、という設計意図の記述)は許容し、
        # 実際の呼び出し(括弧付き)のみが無いことを確認する。
        self.assertNotIn("generate_family_c_a2_comment(", b1_branch)


class RunnerEpisodeSequenceCompositionTests(unittest.TestCase):
    """Family C episode timeline構築(build_family_c_episode_sequence)の
    構造テスト(実wav使用、TTS/ASR API呼び出しなし)。B1相当(Japanese title
    無し)でJapanese titleが出現しないこと、Comment 4が一切出現しないこと、
    Comment 2/3が指定segment直後に挿入されることを確認する。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.audio_dir = os.path.join(self.tmp, "audio")
        os.makedirs(self.audio_dir)
        import er002_common as common
        import numpy as np
        self.common = common
        self.np = np
        for name in ("welcome.wav", "topic_intro_en.wav", "japanese_title.wav", "preview_intro.wav",
                     "preview_ja.wav", "key_phrases_intro.wav", "full_story_intro.wav",
                     "kp1_number.wav", "kp1_english.wav", "kp1_japanese.wav",
                     "story_001.wav", "story_002.wav", "story_003.wav",
                     "comment_1_ja.wav", "comment_2_ja.wav", "comment_3_ja.wav"):
            common.write_wav_float(os.path.join(self.audio_dir, name),
                                    np.zeros(240, dtype=np.float64), runner.MONO_SR, 1)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gs(self, mono, label):
        return self.np.stack([mono, mono], axis=-1) if mono.ndim == 1 else mono

    def _build(self, has_japanese_title, preview_asset_name="preview_ja.wav"):
        import er003_b1_p9a_audio as p9a
        story_segments = [
            {"id": "story_001", "voice": "narrator", "audio_path": f"{self.audio_dir}/story_001.wav"},
            {"id": "story_002", "voice": "device", "audio_path": f"{self.audio_dir}/story_002.wav"},
            {"id": "story_003", "voice": "narrator", "audio_path": f"{self.audio_dir}/story_003.wav"},
        ]
        comment_wavs = {1: f"{self.audio_dir}/comment_1_ja.wav", 2: f"{self.audio_dir}/comment_2_ja.wav",
                        3: f"{self.audio_dir}/comment_3_ja.wav"}
        stereo_silence = p9a.silence_stereo(0.01)
        return runner.build_family_c_episode_sequence(
            audio_dir=self.audio_dir, target_rms=0.05, gs=self._gs, gs_already_stereo=self._gs,
            intro_gained=stereo_silence, notification_gained=stereo_silence, outro_gained=stereo_silence,
            kp_blocks=[(1, f"{self.audio_dir}/kp1_number.wav", f"{self.audio_dir}/kp1_english.wav",
                        f"{self.audio_dir}/kp1_japanese.wav")],
            story_segments=story_segments, comment_wavs=comment_wavs,
            comment_after_segment_id={"2": "story_001", "3": "story_002"},
            has_japanese_title=has_japanese_title, preview_asset_name=preview_asset_name)

    def test_japanese_title_present_when_flag_true(self):
        seq = self._build(has_japanese_title=True)
        labels = [name for name, _ in seq]
        self.assertIn("Japanese title", labels)

    def test_japanese_title_absent_when_flag_false_b1_style(self):
        seq = self._build(has_japanese_title=False)
        labels = [name for name, _ in seq]
        self.assertNotIn("Japanese title", labels)

    def test_comment_4_never_appears(self):
        seq = self._build(has_japanese_title=True)
        labels = [name for name, _ in seq]
        self.assertNotIn("Comment 4", labels)
        self.assertEqual(sum(1 for l in labels if l.startswith("Comment ")), 3)

    def test_comment_2_and_3_inserted_after_configured_segments(self):
        seq = self._build(has_japanese_title=True)
        labels = [name for name, _ in seq]
        idx_story1 = labels.index("story_001")
        idx_comment2 = labels.index("Comment 2")
        idx_story2 = labels.index("story_002")
        idx_comment3 = labels.index("Comment 3")
        self.assertLess(idx_story1, idx_comment2)
        self.assertLess(idx_comment2, idx_story2)
        self.assertLess(idx_story2, idx_comment3)


if __name__ == "__main__":
    unittest.main()
