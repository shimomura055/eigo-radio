# ============================================================
# er019_family_x_audio_production_runner_01_test_01.py
# NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 (Stage 1)
# ============================================================
# Unit test(モックのみ、API呼び出しなし、常に¥0)。
#   - 記事分割(3本文+In One Line、見出し数不一致時のエラー)
#   - segment_id -> narrative role解決(既存er020のresolve_narrative_
#     role()を単一の正として参照、経路ごとの個別ハードコードをしない)
#   - segment順序plan(Notification音が本文以降に無いこと、Point構造が
#     一切無いこと)
#   - Comment role文言(Point前提の除去確認)
#   - dry-run(--dry-run、API呼び出しなしでplan JSON出力)
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_audio_production_runner_01_test_01 -v

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import er019_family_x_audio_plan_01 as plan
import er019_family_x_audio_production_runner_01 as runner
import er020_tts_retry_local_rewrite_01 as retry_primitive

SAMPLE_ARTICLE_B1B = """# We Thought It Was AI—But There Was a Person Inside Meta’s Muse

Ring, ring. A call came from an AI agent—or so it seemed. As the conversation went on, the voice on the other end turned out not to be AI at all, but a person.

Meta had run a test that created exactly this kind of surprise.

### The hidden person behind the AI sign

Here was the reveal. The test began without enough clear notice that contract workers would make the calls.

It was a future-looking story, but the main question was very basic.

### Meta admits a mistake

A Meta executive admitted that starting the test without clearly telling users was a mistake. The human concierge feature has been rolled back for now.

## In one line
Before AI speaks for us, we need to know whether the voice belongs to AI or a person.
"""

SAMPLE_ARTICLE_MISSING_HEADING = """# Title Only

Paragraph one.

Paragraph two.

## In one line
Summary line.
"""

SAMPLE_ARTICLE_THREE_HEADINGS = """# Title

Intro paragraph.

### Heading One

Body one.

### Heading Two

Body two.

### Heading Three

Body three.

## In one line
Summary.
"""

SAMPLE_ARTICLE_EMPTY_PART1 = """# Title
### Heading One

Body one.

### Heading Two

Body two.

## In one line
Summary.
"""


class SplitFamilyXArticleTextTests(unittest.TestCase):
    def test_splits_into_title_part1_part2_part3_in_one_line(self):
        parts = plan.split_family_x_article_text(SAMPLE_ARTICLE_B1B)
        self.assertIn("Person Inside Meta", parts["title"])
        self.assertIn("Ring, ring", parts["part1"])
        self.assertIn("Meta had run a test", parts["part1"])
        # 本文2は見出し1テキストで始まる(DESIGN NOTE: 見出しをsegment先頭に含める)
        self.assertTrue(parts["part2"].startswith(parts["heading1"]))
        self.assertEqual(parts["heading1"], "The hidden person behind the AI sign")
        self.assertIn("Here was the reveal", parts["part2"])
        self.assertTrue(parts["part3"].startswith(parts["heading2"]))
        self.assertEqual(parts["heading2"], "Meta admits a mistake")
        self.assertIn("rolled back for now", parts["part3"])
        self.assertEqual(parts["in_one_line"],
                         "Before AI speaks for us, we need to know whether the voice belongs to AI or a person.")
        # 本文1自体には見出し2つの内容が混入していない(境界の正しさ確認)
        self.assertNotIn("The hidden person", parts["part1"])
        self.assertNotIn("Meta admits a mistake", parts["part1"])

    def test_word_counts_present_and_positive(self):
        parts = plan.split_family_x_article_text(SAMPLE_ARTICLE_B1B)
        wc = parts["word_counts"]
        for key in ("part1", "part2", "part3", "in_one_line"):
            self.assertGreater(wc[key], 0, f"{key} word count should be > 0")

    def test_missing_h3_headings_raises(self):
        with self.assertRaises(RuntimeError):
            plan.split_family_x_article_text(SAMPLE_ARTICLE_MISSING_HEADING)

    def test_three_h3_headings_raises(self):
        with self.assertRaises(RuntimeError):
            plan.split_family_x_article_text(SAMPLE_ARTICLE_THREE_HEADINGS)

    def test_missing_in_one_line_raises(self):
        text = SAMPLE_ARTICLE_B1B.replace("## In one line\n", "")
        with self.assertRaises(RuntimeError):
            plan.split_family_x_article_text(text)

    def test_empty_part1_raises(self):
        with self.assertRaises(RuntimeError):
            plan.split_family_x_article_text(SAMPLE_ARTICLE_EMPTY_PART1)

    def test_reconstruct_roundtrips_structure(self):
        parts = plan.split_family_x_article_text(SAMPLE_ARTICLE_B1B)
        reconstructed = plan.reconstruct_family_x_article_text(parts)
        re_parts = plan.split_family_x_article_text(reconstructed)
        self.assertEqual(re_parts["title"], parts["title"])
        self.assertEqual(re_parts["heading1"], parts["heading1"])
        self.assertEqual(re_parts["heading2"], parts["heading2"])
        self.assertEqual(re_parts["in_one_line"], parts["in_one_line"])


class SegmentIdNarrativeRoleResolutionTests(unittest.TestCase):
    """要件3: segment_idはer020_tts_retry_local_rewrite_01.
    resolve_narrative_role()が既存5 role(+HEADING_READOUT/KEY_PHRASE)へ
    解決する命名に揃える。full_story_part3が実際に解決されることを
    コードで確認する(er020は編集していない、既存のハードコードのみで
    解決される)。"""

    def test_full_story_parts_resolve_to_full_story(self):
        for seg in ("full_story_part1", "full_story_part2", "full_story_part3"):
            with self.subTest(seg=seg):
                self.assertEqual(retry_primitive.resolve_narrative_role(seg), "FULL_STORY")

    def test_comments_resolve_to_comment(self):
        for seg in ("comment_1", "comment_2", "comment_3", "comment_4"):
            with self.subTest(seg=seg):
                self.assertEqual(retry_primitive.resolve_narrative_role(seg), "COMMENT")

    def test_preview_topic_intro_in_one_line(self):
        self.assertEqual(retry_primitive.resolve_narrative_role("preview"), "PREVIEW")
        self.assertEqual(retry_primitive.resolve_narrative_role("topic_intro"), "TOPIC_INTRO")
        self.assertEqual(retry_primitive.resolve_narrative_role("in_one_line"), "IN_ONE_LINE")

    def test_all_required_segments_are_connected_speech_enabled(self):
        for seg in ("full_story_part1", "full_story_part2", "full_story_part3",
                    "comment_1", "comment_2", "comment_3", "comment_4",
                    "preview", "topic_intro", "in_one_line"):
            with self.subTest(seg=seg):
                self.assertTrue(retry_primitive.connected_speech_enabled_for(seg))

    def test_no_point_segment_ids_used_anywhere_in_family_x_order(self):
        used_ids = {seg for _, seg, _ in plan.FAMILY_X_B1_SEGMENT_ORDER if seg} | \
                   {seg for _, seg, _ in plan.FAMILY_X_A2_SEGMENT_ORDER if seg}
        for seg in used_ids:
            self.assertNotIn("point", seg.lower())

    def test_heading_sub_segments_are_not_connected_speech_enabled(self):
        """Stage 3c: full_story_part2_heading/full_story_part3_heading は
        er020_tts_retry_local_rewrite_01.NON_APPLICABLE_SEGMENT_IDS(point_
        one_heading/point_two_headingのみハードコード)に含まれないため、
        resolve_narrative_role()はNoneを返す(er020編集禁止のため)。ただし
        connected_speech_enabled_for()の実効値はFamily Aのpoint_one_heading
        (HEADING_READOUT)と同じFalseであり、挙動差はないことを確認する。"""
        for seg in ("full_story_part2_heading", "full_story_part3_heading"):
            with self.subTest(seg=seg):
                self.assertIsNone(retry_primitive.resolve_narrative_role(seg))
                self.assertFalse(retry_primitive.connected_speech_enabled_for(seg))
                self.assertFalse(retry_primitive.connected_speech_enabled_for("point_one_heading"))


class SegmentOrderPlanTests(unittest.TestCase):
    def _labels(self, order):
        return [label for label, _seg, _role in order]

    def test_b1_order_has_no_point_labels_or_notification_after_body_start(self):
        labels = self._labels(plan.FAMILY_X_B1_SEGMENT_ORDER)
        joined = " ".join(labels)
        self.assertNotIn("Point", joined)
        # "Full story intro"以降("Notification 3"直後)にNotification/Point系
        # segmentが出現しないことを確認(本文以降に新しい効果音を追加しない)。
        idx_full_story_intro = labels.index("Full story intro (Charon)")
        tail = labels[idx_full_story_intro:]
        for label in tail:
            self.assertNotIn("Notification", label)
            self.assertNotIn("Point Notification", label)

    def test_a2_order_excludes_point_explanation_segment(self):
        labels = self._labels(plan.FAMILY_X_A2_SEGMENT_ORDER)
        joined = " ".join(labels)
        self.assertNotIn("Point", joined)
        self.assertNotIn("Point explanation", joined)

    def test_comment_body_alternation_order(self):
        for order in (plan.FAMILY_X_B1_SEGMENT_ORDER, plan.FAMILY_X_A2_SEGMENT_ORDER):
            seg_ids = [seg for _label, seg, _role in order if seg]
            expected = ["topic_intro", "preview", "comment_1", "full_story_part1",
                        "comment_2", "full_story_part2_heading", "full_story_part2",
                        "comment_3", "full_story_part3_heading", "full_story_part3",
                        "comment_4", "in_one_line"]
            # japanese_titleがA2にのみ挟まるため、共通部分のみ順序一致を確認する。
            filtered = [s for s in seg_ids if s != "japanese_title"]
            self.assertEqual(filtered, expected)

    def test_heading_sub_segment_immediately_precedes_its_body(self):
        """Stage 3c: 見出しsub-segmentは対応する本文の直前(同一スロット)に
        置かれ、間に他のsegment(SFX含む)を挟まないこと。"""
        for order in (plan.FAMILY_X_B1_SEGMENT_ORDER, plan.FAMILY_X_A2_SEGMENT_ORDER):
            seg_ids = [seg for _label, seg, _role in order]  # Noneも含む(SFX検知用)
            for body in ("full_story_part2", "full_story_part3"):
                heading = f"{body}_heading"
                idx_heading = seg_ids.index(heading)
                idx_body = seg_ids.index(body)
                self.assertEqual(idx_body, idx_heading + 1,
                                  f"{heading}の直後は{body}であるべき(実際: {seg_ids[idx_heading:idx_heading + 2]})")

    def test_heading_sub_segment_plan_role_is_heading_readout(self):
        for order in (plan.FAMILY_X_B1_SEGMENT_ORDER, plan.FAMILY_X_A2_SEGMENT_ORDER):
            by_id = {seg: role for _label, seg, role in order if seg}
            self.assertEqual(by_id["full_story_part2_heading"], "HEADING_READOUT")
            self.assertEqual(by_id["full_story_part3_heading"], "HEADING_READOUT")


class CommentRoleWordingTests(unittest.TestCase):
    """既存Family A(Point構造)のComment 3/4 role文言を、Family X用に
    Point前提を除去したものへ差し替えていることを確認する(pointless
    trialの`PointWordingAbsenceTest`踏襲)。"""

    def test_family_x_comment_roles_do_not_mention_point(self):
        for role_text in (plan.FAMILY_X_B1_COMMENT_3_ROLE, plan.FAMILY_X_B1_COMMENT_4_ROLE,
                           plan.FAMILY_X_A2_COMMENT_3_ROLE, plan.FAMILY_X_A2_COMMENT_4_ROLE):
            with self.subTest(role_text=role_text[:30]):
                self.assertNotIn("Point", role_text)
                self.assertNotIn("ポイント", role_text)

    def test_family_x_comment_roles_forbid_internal_labels_in_output(self):
        for role_text in (plan.FAMILY_X_B1_COMMENT_3_ROLE, plan.FAMILY_X_B1_COMMENT_4_ROLE,
                           plan.FAMILY_X_A2_COMMENT_3_ROLE, plan.FAMILY_X_A2_COMMENT_4_ROLE):
            self.assertIn("制作内部の構造ラベル", role_text)

    def test_detector_itself_would_catch_point_wording(self):
        """検出器自体が機能することの確認(意図的にPoint語を含む文字列でテスト)。"""
        contaminated = plan.FAMILY_X_B1_COMMENT_3_ROLE + "\nPoint One is great."
        self.assertIn("Point", contaminated)


class BuildSegmentPlanTests(unittest.TestCase):
    def setUp(self):
        self.parts = plan.split_family_x_article_text(SAMPLE_ARTICLE_B1B)

    def test_plan_without_support_marks_comment_text_unavailable(self):
        result = runner.build_segment_plan("b1b", self.parts, support=None)
        by_id = {r["segment_id"]: r for r in result["segments"] if r["segment_id"]}
        self.assertIsNone(by_id["comment_1"]["text_available"])
        self.assertTrue(by_id["full_story_part1"]["text_available"])
        self.assertIn("estimated_seconds", by_id["full_story_part1"])

    def test_plan_with_support_marks_comment_text_available(self):
        support = {"preview": "A short preview.", "comment_1": "Listen for the reveal.",
                   "comment_2": "Recap.", "comment_3": "Bridge.", "comment_4": "Wrap up."}
        result = runner.build_segment_plan("b1b", self.parts, support=support)
        by_id = {r["segment_id"]: r for r in result["segments"] if r["segment_id"]}
        self.assertTrue(by_id["comment_1"]["text_available"])
        self.assertIn("estimated_seconds", by_id["comment_1"])

    def test_plan_flags_no_point_structure_and_no_new_sfx(self):
        result = runner.build_segment_plan("b1b", self.parts, support=None)
        self.assertTrue(result["no_point_structure"])
        self.assertTrue(result["no_new_sfx_after_body_start"])

    def test_plan_role_resolution_matches_er020_for_full_story_and_comments(self):
        result = runner.build_segment_plan("a2", self.parts, support=None)
        for row in result["segments"]:
            if row["segment_id"] in ("full_story_part1", "full_story_part2", "full_story_part3"):
                self.assertEqual(row["resolved_narrative_role"], "FULL_STORY")
            if row["segment_id"] in ("comment_1", "comment_2", "comment_3", "comment_4"):
                self.assertEqual(row["resolved_narrative_role"], "COMMENT")

    def test_plan_heading_sub_segments_use_heading_text_and_english_estimate(self):
        """Stage 3c: 見出しsub-segmentのtextはheading1/heading2(見出しのみ、
        本文を含まない)であり、A2でも(日本語ではなく)英語CPMで見積もること。"""
        for level in ("a2", "b1b"):
            result = runner.build_segment_plan(level, self.parts, support=None)
            by_id = {r["segment_id"]: r for r in result["segments"] if r["segment_id"]}
            self.assertEqual(by_id["full_story_part2_heading"]["plan_role"], "HEADING_READOUT")
            self.assertTrue(by_id["full_story_part2_heading"]["text_available"])
            self.assertIn("estimated_seconds", by_id["full_story_part2_heading"])
            self.assertGreater(by_id["full_story_part2_heading"]["estimated_seconds"], 0.0)
            # full_story_part2本文の見積り(body2のみ)は、heading+body合算の
            # part2見積りより短い(見出し語が二重計上されていないことの間接確認)。
            body_seconds = by_id["full_story_part2"]["estimated_seconds"]
            combined_seconds = plan.estimate_seconds_english(self.parts["part2"])
            self.assertLess(body_seconds, combined_seconds)


class DryRunEndToEndTests(unittest.TestCase):
    """--dry-runがAPI呼び出しなしでplan(segment表・順序・想定秒数)を
    JSON出力することを、実際にCLIをsubprocessで起動して確認する。

    多くの既存moduleがcwd相対path(例: er002_v1_2m_length_spec.json)を
    importチェーンの途中でロードするため、cwdはリポジトリroot(本テスト
    ファイルの場所)に固定する。fixtureはリポジトリ配下の使い捨てslug名
    (er019_output/_unit_test_family_x_audio_dryrun_01/)へ作成し、
    テスト後に必ず削除する(既存の他ファイルには一切触れない)。"""

    REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        self.slug = "_unit_test_family_x_audio_dryrun_01"
        self.run = "run_01"
        self.source_dir = os.path.join(self.REPO_ROOT, "er019_output", self.slug, self.run)
        self.out_dir = os.path.join(self.REPO_ROOT, "er019_output",
                                     "family_x_audio_production_wiring_01", f"{self.slug}__{self.run}")
        for level in ("a2", "b1b"):
            level_dir = os.path.join(self.source_dir, level)
            os.makedirs(level_dir, exist_ok=True)
            with open(os.path.join(level_dir, "article.md"), "w", encoding="utf-8") as f:
                f.write(SAMPLE_ARTICLE_B1B)

    def tearDown(self):
        shutil.rmtree(os.path.join(self.REPO_ROOT, "er019_output", self.slug), ignore_errors=True)
        shutil.rmtree(self.out_dir, ignore_errors=True)

    def _run_dry_run(self):
        return subprocess.run(
            [sys.executable,
             os.path.join(self.REPO_ROOT, "er019_family_x_audio_production_runner_01.py"),
             "--slug", self.slug, "--run", self.run, "--level", "both", "--dry-run"],
            cwd=self.REPO_ROOT, capture_output=True, text=True, timeout=60)

    def test_dry_run_produces_plan_json_without_api_calls(self):
        proc = self._run_dry_run()
        self.assertEqual(proc.returncode, 0, msg=f"stdout={proc.stdout}\nstderr={proc.stderr}")

        plan_result_path = os.path.join(self.out_dir, "plan_run_result.json")
        self.assertTrue(os.path.exists(plan_result_path))
        with open(plan_result_path, encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(result["a2"]["status"], "OK")
        self.assertEqual(result["b1b"]["status"], "OK")

        for level in ("a2", "b1b"):
            seg_plan_path = os.path.join(self.out_dir, level, "segment_plan.json")
            self.assertTrue(os.path.exists(seg_plan_path))
            with open(seg_plan_path, encoding="utf-8") as f:
                seg_plan = json.load(f)
            self.assertTrue(seg_plan["no_point_structure"])
            self.assertTrue(seg_plan["no_new_sfx_after_body_start"])
            segment_ids = [r["segment_id"] for r in seg_plan["segments"] if r["segment_id"]]
            self.assertIn("full_story_part3", segment_ids)
            self.assertIn("full_story_part2_heading", segment_ids)
            self.assertIn("full_story_part3_heading", segment_ids)
            self.assertNotIn("point_one", segment_ids)
            self.assertNotIn("point_two", segment_ids)

    def test_dry_run_writes_no_wav_or_raw_usage_log(self):
        """API呼び出しゼロの間接確認: cost logのraw_usage_log.jsonlや
        音声ファイル(.wav)がdry-run実行では一切生成されないこと。"""
        proc = self._run_dry_run()
        self.assertEqual(proc.returncode, 0, msg=f"stdout={proc.stdout}\nstderr={proc.stderr}")
        for root, _dirs, files in os.walk(self.out_dir):
            for name in files:
                self.assertFalse(name.endswith(".wav"), f"unexpected wav file: {name}")
                self.assertNotEqual(name, "raw_usage_log.jsonl")


class GenerateOrReuseTextSafetyTests(unittest.TestCase):
    """Stage 3c: full_story_part2/3のcanonical textが見出し分離により
    変わったにもかかわらず、旧run(見出しを含む音声)がstatus=="OK"のまま
    誤って再利用されないことを回帰確認する(実データ[Hormuz b1b]で発見した
    問題、runtime evidence詳細はRESULT_PACKET/REPORT参照)。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="generate_or_reuse_safety_")
        self.wav_path = os.path.join(self.tmpdir, "full_story_part3.wav")
        with open(self.wav_path, "wb") as f:
            f.write(b"RIFF____WAVEfmt ")  # 実在すればよい(中身は使わない)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_reuses_when_cached_canonical_text_matches(self):
        cached = {"segments": {"full_story_part3": {"status": "OK", "canonical_text": "old body only"}}}
        called = {"n": 0}

        def generate_fn():
            called["n"] += 1
            return {"status": "OK", "canonical_text": "old body only"}

        result = runner._generate_or_reuse(cached, "full_story_part3", self.wav_path, generate_fn,
                                            expected_text="old body only")
        self.assertEqual(called["n"], 0)
        self.assertTrue(result.get("reused_from_previous_run"))

    def test_regenerates_when_cached_canonical_text_differs(self):
        """見出しを含んでいた旧canonical_text(heading+body)と、見出し分離後の
        期待text(bodyのみ)が食い違う場合、必ず再生成する(古い音声の
        使い回し=見出し二重読み上げバグを防ぐ)。"""
        cached = {"segments": {"full_story_part3": {
            "status": "OK", "canonical_text": "The chart refuses to stay down\n\nOn July 14, ..."}}}
        called = {"n": 0}

        def generate_fn():
            called["n"] += 1
            return {"status": "OK", "canonical_text": "On July 14, ..."}

        result = runner._generate_or_reuse(cached, "full_story_part3", self.wav_path, generate_fn,
                                            expected_text="On July 14, ...")
        self.assertEqual(called["n"], 1)
        self.assertNotIn("reused_from_previous_run", result)

    def test_legacy_callers_without_expected_text_keep_old_behavior(self):
        """expected_text省略時は既存呼び出し元の挙動(status==OKのみで判定)
        を変えない(後方互換)。"""
        cached = {"segments": {"preview": {"status": "OK", "canonical_text": "anything"}}}
        called = {"n": 0}

        def generate_fn():
            called["n"] += 1
            return {"status": "OK"}

        result = runner._generate_or_reuse(cached, "preview", self.wav_path, generate_fn)
        self.assertEqual(called["n"], 0)
        self.assertTrue(result.get("reused_from_previous_run"))


class SourceArticleMissingTests(unittest.TestCase):
    def test_plan_stage_reports_missing_article_gracefully(self):
        tmp = tempfile.mkdtemp(prefix="family_x_audio_missing_")
        try:
            out_dir = os.path.join(tmp, "out")
            result = runner.run_plan_stage(os.path.join(tmp, "does_not_exist"), out_dir, ["a2", "b1b"])
            self.assertEqual(result["a2"]["status"], "SOURCE_ARTICLE_NOT_FOUND")
            self.assertEqual(result["b1b"]["status"], "SOURCE_ARTICLE_NOT_FOUND")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class ArticleTextGateWiringTests(unittest.TestCase):
    """OPEN-193/OPEN-204(2026-09-27起票、NEWS-FAMILY-X-AUDIO-PRODUCTION-
    WIRING-01 Stage 3f修正)の回帰防止: load_family_x_a2_sources/
    load_family_x_b1_sourcesが、source_dir/{level}/article.mdを読み込み
    article_textとしてasm.verify_episode_audio_validation_gateへ転送する
    こと(KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01 commit 8f197a74/1d69aa97への
    Family X runner側の追従漏れを解消)。asm.verify_episode_audio_
    validation_gate自体はmonkeypatchで差し替え、Gate呼び出し直後に例外を
    投げて以降の実wav読み込みへは進ませない(音声fixtureが無いため)。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="family_x_article_text_gate_")
        self.source_dir = os.path.join(self.tmpdir, "source")
        self.theme_out_dir = os.path.join(self.tmpdir, "out")
        os.makedirs(os.path.join(self.source_dir, "a2"), exist_ok=True)
        os.makedirs(os.path.join(self.source_dir, "b1b"), exist_ok=True)
        with open(os.path.join(self.source_dir, "a2", "article.md"), "w", encoding="utf-8") as f:
            f.write("A2 ARTICLE TEXT MARKER")
        with open(os.path.join(self.source_dir, "b1b", "article.md"), "w", encoding="utf-8") as f:
            f.write("B1B ARTICLE TEXT MARKER")

        self.captured = {}
        self.original_gate = runner.asm.verify_episode_audio_validation_gate

        def fake_gate(out_dir, level, required_structure=None, article_text=None):
            self.captured["out_dir"] = out_dir
            self.captured["level"] = level
            self.captured["article_text"] = article_text
            raise RuntimeError("STOP_AFTER_GATE_FOR_TEST")

        runner.asm.verify_episode_audio_validation_gate = fake_gate

    def tearDown(self):
        runner.asm.verify_episode_audio_validation_gate = self.original_gate
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_load_family_x_a2_sources_forwards_article_text_from_source_dir(self):
        with self.assertRaises(RuntimeError) as ctx:
            runner.load_family_x_a2_sources(self.theme_out_dir, source_dir=self.source_dir)
        self.assertEqual(str(ctx.exception), "STOP_AFTER_GATE_FOR_TEST")
        self.assertEqual(self.captured["article_text"], "A2 ARTICLE TEXT MARKER")
        self.assertEqual(self.captured["level"], "A2")

    def test_load_family_x_b1_sources_forwards_article_text_from_source_dir(self):
        with self.assertRaises(RuntimeError) as ctx:
            runner.load_family_x_b1_sources(self.theme_out_dir, source_dir=self.source_dir)
        self.assertEqual(str(ctx.exception), "STOP_AFTER_GATE_FOR_TEST")
        self.assertEqual(self.captured["article_text"], "B1B ARTICLE TEXT MARKER")
        self.assertEqual(self.captured["level"], "B1")

    def test_source_dir_omitted_keeps_legacy_fallback_behavior(self):
        """source_dir省略時(既存呼び出し元との後方互換)はarticle_text=Noneの
        まま渡し、既存Gate内fallback解決(out_dir直下のarticle.md等)に委ねる
        (挙動を変えない)。"""
        with self.assertRaises(RuntimeError) as ctx:
            runner.load_family_x_a2_sources(self.theme_out_dir)
        self.assertEqual(str(ctx.exception), "STOP_AFTER_GATE_FOR_TEST")
        self.assertIsNone(self.captured["article_text"])

    def test_missing_article_file_at_source_dir_keeps_article_text_none_fail_closed(self):
        """source_dirは渡されたがarticle.mdがまだ存在しない場合(異常系)は、
        article_text=Noneのまま渡す(黙って本文ありと偽装しない)。以降の
        fail-closed判定[KEY_PHRASE_SOURCE_GATE_ARTICLE_TEXT_UNAVAILABLE等]は
        既存Gate側の責務のまま変えない。"""
        empty_source_dir = os.path.join(self.tmpdir, "empty_source")
        os.makedirs(os.path.join(empty_source_dir, "a2"), exist_ok=True)
        with self.assertRaises(RuntimeError) as ctx:
            runner.load_family_x_a2_sources(self.theme_out_dir, source_dir=empty_source_dir)
        self.assertEqual(str(ctx.exception), "STOP_AFTER_GATE_FOR_TEST")
        self.assertIsNone(self.captured["article_text"])


class AssembledFilenameThemeComponentTests(unittest.TestCase):
    """Stage 3f実行時に発見した既存バグ(サブディレクトリ区切り"/"を含む
    --slug[例: Hormuz/small_bag]でAssembly出力filenameがFileNotFoundError
    になる)の回帰防止。"""

    def test_slash_in_theme_id_is_sanitized_for_filename(self):
        self.assertEqual(
            runner._assembled_filename_theme_component("family_x_b3_diversity_trial_01/hormuz"),
            "FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ")

    def test_theme_id_without_slash_is_unchanged_aside_from_uppercasing(self):
        self.assertEqual(
            runner._assembled_filename_theme_component("family_x_b3_production_wiring_01"),
            "FAMILY_X_B3_PRODUCTION_WIRING_01")


if __name__ == "__main__":
    unittest.main()
