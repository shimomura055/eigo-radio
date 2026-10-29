# -*- coding: utf-8 -*-
"""FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B: Y Production runner の mock test(API 0・実client生成block・network遮断)。

遮断harness(KP HR案件でmock漏れにより実LLM到達事故があったため、新入口のtestは最初に遮断を張る):
  - socket.connect / create_connection / getaddrinfo を例外化、
  - vfl01.get_client / openai.OpenAI / google.genai.Client の生成を例外化(生成試行を数える)。
  testの終了時に『実client生成試行 0・network接続試行 0』を確認する。
"""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402
import er121_family_y_audio_01 as ya  # noqa: E402
from er119_test_support_01 import legacy_unmarked_class  # noqa: E402  (旧マーク無し記事の再現。SLOT-23 委任_05M)

BLOCK = {"net": 0, "client": 0}
_PATCHERS = []


def setUpModule():
    def net(*a, **k):
        BLOCK["net"] += 1
        raise RuntimeError("NETWORK_BLOCKED_BY_TEST")

    def client(*a, **k):
        BLOCK["client"] += 1
        raise RuntimeError("REAL_CLIENT_CREATION_BLOCKED_BY_TEST")

    targets = [(socket.socket, "connect", net), (socket, "create_connection", net), (socket, "getaddrinfo", net)]
    import er003_v1_en_direct_vfl_01_generate as vfl01
    targets.append((vfl01, "get_client", client))
    for modname, attr in (("openai", "OpenAI"), ("google.genai", "Client")):
        try:
            m = __import__(modname, fromlist=[attr])
            targets.append((m, attr, client))
        except Exception:  # noqa: BLE001  (未installなら生成されようがない)
            pass
    for obj, name, fn in targets:
        p = mock.patch.object(obj, name, fn)
        p.start()
        _PATCHERS.append(p)


def tearDownModule():
    for p in _PATCHERS:
        p.stop()


def _theme(root):
    os.makedirs(root, exist_ok=True)
    p = os.path.join(root, "theme.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"theme": "mock", "sheets": {f"voice_{i}": {"experiences": [{"id": f"E{i}", "kind": "O", "source_ids": [f"RV-{i}"], "text_ja": "x"}]} for i in (1, 2, 3)}}, f)
    return p      # 実投稿に基づく記事(全Voiceの経験に非空source_ids)=Voice説明文が出る。委任_08


def _declare(ctx):
    import er119_kp_wiring_01 as kw
    kw.declare_from_runner_args(ctx.out_dir, by="test", reason="mock test", user_ref="mock")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def _ctx(root, run="run_t", **kw):
    ctx = r.build_mock_context(root, run=run, slug="mock_slug", theme_package_path=_theme(root), **kw)
    return ctx


def _res(title, body, actual, requested):
    import types
    return types.SimpleNamespace(text="# " + title + "\n\n" + body, title=title, body=body, model_id_actual=actual, model_id_requested=requested, response_id="x",
                                 usage={}, cost_usd=0.0, cost_jpy=0.0, attempts=1, retried=False, fallback_detected=actual != requested, elapsed_seconds=0.0)


def _calls(ctx):
    return ctx.mock_api.n


class FullMockRun(unittest.TestCase):
    """一度だけ全stageを通し、成果物を複数のtestで検査する。"""

    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="y_runner_")
        cls.ctx = _ctx(cls.root)
        with _quiet():
            r.run_stages(cls.ctx, ["seed_check", "text", "translate", "support"])
            _declare(cls.ctx)
            r.run_stages(cls.ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"])
        cls.out = cls.ctx.out_dir
        cls.calls_after_first = _calls(cls.ctx)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_all_stages_completed_and_manifest(self):
        man = json.load(open(f"{self.out}/final_manifest.json", encoding="utf-8"))
        self.assertEqual(man["entry_status"], "FAMILY_Y_PRODUCTION")
        self.assertEqual(man["chunk_tts"], "applied_X_method")     # OT-44(b): USER_02 ①でX方式Chunkを正式採用した後の表記
        self.assertEqual(man["core_numeric_v4_j2"], "not_applicable_Y")
        self.assertTrue(man["closing_record"]["routing_key"])           # closing_record(実model/routing/prompt sha)が最終成果物に残る
        self.assertTrue(man["closing_record"]["prompt_sha256"])
        for lv in ("b1b", "a2"):
            self.assertTrue(man["assembled"][lv] and os.path.exists(man["assembled"][lv]))
        self.assertTrue(os.path.exists(f"{self.out}/pages/index.html"))
        self.assertTrue(json.load(open(f"{self.out}/page_verify_local.json", encoding="utf-8"))["ok"])

    def test_translate_entries_record_actual_model_and_routing(self):
        prov = json.load(open(f"{self.out}/provenance.json", encoding="utf-8"))
        for unit, key in (("translate_b1b", "FAMILY_Y_TRANSLATE_ADV"), ("translate_a2", "FAMILY_Y_TRANSLATE_STD")):
            e = prov["downstream_stages"][unit]
            self.assertEqual(e["routing_key"], key)
            self.assertTrue(e["actual_model_id"].startswith(e["requested_model"]))
            self.assertTrue(e["response_id"])

    def test_api_boundary_only_mock_kinds_and_no_real_client(self):
        kinds = {json.loads(l)["kind"] for l in open(f"{self.out}/mock_api_calls.jsonl", encoding="utf-8")}
        self.assertTrue(kinds <= {"llm", "text_core", "kp", "kp_expl", "kp_part1", "kp_part1_ja", "part2_extract", "part2_explain", "tts", "tts_shared", "tts_kp"}, kinds)
        self.assertEqual(BLOCK["client"], 0)
        self.assertEqual(BLOCK["net"], 0)

    def test_resume_is_api0_and_reuses(self):
        before = _calls(self.ctx)
        with _quiet():
            res = r.run_stages(self.ctx, ["text", "translate", "support", "kp", "tts_b1b", "tts_a2"])
        self.assertEqual(_calls(self.ctx), before, "resumeでAPI境界を通った(再利用が効いていない)")
        self.assertEqual(res["text"]["status"], "reused")
        self.assertEqual(res["tts_b1b"]["status"], "reused")
        self.assertEqual(res["translate"], {"b1b": "reused", "a2": "reused"})

    def test_timeline_has_all_y_segments_in_play_order(self):
        want = [ys.PAGE_LABEL[s] for s in ys.Y_SEGMENT_IDS]
        for lv in ("b1b", "a2"):
            tl = json.load(open(f"{self.out}/{lv}/audit/timeline.json", encoding="utf-8"))
            parts = [e["part"] for e in tl if not e["part"].startswith("pause")]
            got = [p for p in parts if p in want]
            self.assertEqual(got, want, lv)
            i = parts.index
            self.assertEqual(parts[i("Full story intro"):i("Full story intro") + 3], ["Full story intro", "Comment 1", want[0]])
            if lv == "b1b":      # 2026-10-26ユーザー承認: Advanced Comment 2削除(導入→Voice1紹介→Voice1→…)。Standardは現状維持
                self.assertNotIn("Comment 2", parts)
                self.assertEqual(parts[i(want[0]) + 1], want[1])
            else:
                self.assertLess(i("Comment 2"), i(want[1]))
                self.assertLess(i(want[0]), i("Comment 2"))
            self.assertEqual(parts[i(want[6]) + 1:i(want[6]) + 3], ["Comment 3", want[7]])      # Voice3 → Comment 3 → Closing
            self.assertEqual(parts[-1], "Outro")
            self.assertNotIn("Comment 4", parts)
            self.assertFalse([p for p in parts if "one line" in p.lower()])

    def test_advanced_has_no_comment2_anywhere_but_standard_keeps_it(self):
        """Advanced(b1b)のComment 2は初回生成・TTS結果・音声ファイル・support_texts・ページから消え、Standard(a2)は現状維持。"""
        adv, std = f"{self.out}/b1b", f"{self.out}/a2"
        sup_adv = json.load(open(f"{self.out}/support/b1b_support.json", encoding="utf-8"))
        sup_std = json.load(open(f"{self.out}/support/a2_support.json", encoding="utf-8"))
        self.assertNotIn("comment_2", sup_adv)
        self.assertIn("comment_2", sup_std)
        self.assertEqual(sup_adv["_meta"]["removed_by_spec"], {"comment_2": ys.COMMENT2_REMOVED_SPEC})
        self.assertNotIn("removed_by_spec", sup_std["_meta"])
        self.assertEqual(sorted(k for k in json.load(open(f"{adv}/support_texts.json", encoding="utf-8"))), ["comment_1", "comment_3", "preview"])
        self.assertEqual(sorted(k for k in json.load(open(f"{std}/support_texts.json", encoding="utf-8"))), ["comment_1", "comment_2", "comment_3", "preview"])
        self.assertEqual(json.load(open(f"{adv}/parts.json", encoding="utf-8"))["removed_by_spec"], {"comment_2": ys.COMMENT2_REMOVED_SPEC})
        self.assertNotIn("removed_by_spec", json.load(open(f"{std}/parts.json", encoding="utf-8")))
        res_adv = json.load(open(f"{adv}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
        res_std = json.load(open(f"{std}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
        self.assertNotIn("comment_2", res_adv)
        man = json.load(open(f"{self.out}/final_manifest.json", encoding="utf-8"))
        self.assertEqual(man["support_segments"], {"b1b": ["preview", "comment_1", "comment_3"], "a2": ["preview", "comment_1", "comment_2", "comment_3"]})
        self.assertEqual(man["removed_by_spec"], {"b1b": {"comment_2": ys.COMMENT2_REMOVED_SPEC}})
        self.assertIn("comment_2", res_std)
        self.assertFalse(os.path.exists(f"{adv}/narration/comment_2.wav"))
        self.assertTrue(os.path.exists(f"{std}/narration/comment_2.wav"))
        for k in ("comment_1", "comment_3", "preview"):
            self.assertIn(k, res_adv)
        tl = json.load(open(f"{adv}/audit/timeline.json", encoding="utf-8"))
        self.assertFalse([e for e in tl if "comment 2" in e["part"].lower()])
        gr = json.load(open(f"{adv}/audit/gain_report.json", encoding="utf-8")) if os.path.exists(f"{adv}/audit/gain_report.json") else {}
        self.assertNotIn("comment_2", json.dumps(gr))
        html = open(f"{self.out}/pages/index.html", encoding="utf-8").read()
        self.assertEqual(html.count(">Comment 2<"), 1, "Comment 2の行はStandardの1行だけ(Advancedには無い)")

    def test_legacy_comment2_artifacts_are_ignored_on_reassemble(self):
        """旧run(comment_2のsupport/TTS結果/wavが残るAdvanced)を再組立しても、Comment 2は組立・timelineに入らない(旧成果物は無視。削除はしない)。"""
        import er121_family_y_audio_01 as ya
        tmp = tempfile.mkdtemp(prefix="y_legacy_c2_")
        try:
            dst = os.path.join(tmp, "run")
            shutil.copytree(self.out, dst)
            adv = f"{dst}/b1b"
            sup = json.load(open(f"{adv}/support_texts.json", encoding="utf-8"))
            sup["comment_2"] = "legacy comment two text."
            json.dump(sup, open(f"{adv}/support_texts.json", "w", encoding="utf-8"))
            shutil.copy(f"{adv}/narration/comment_1.wav", f"{adv}/narration/comment_2.wav")
            resp = f"{adv}/audit/tts_generation_results.json"
            res = json.load(open(resp, encoding="utf-8"))
            res["segments"]["comment_2"] = dict(res["segments"]["comment_1"])
            json.dump(res, open(resp, "w", encoding="utf-8"))
            before = [e["part"] for e in json.load(open(f"{self.out}/b1b/audit/timeline.json", encoding="utf-8"))]
            with _quiet():
                s = ya.assemble_level(dst, "b1b", style_profile=ya.Y_APPROVED_STYLE_PROFILE, slug="mock_slug",
                                      article_text=ys.canonical_body(r._rd(r._level_text_path(self.ctx, "b1b"))))
            self.assertEqual(s["status"], "OK", s)
            after = [e["part"] for e in json.load(open(f"{adv}/audit/timeline.json", encoding="utf-8"))]
            self.assertEqual(after, before)
            self.assertNotIn("Comment 2", after)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_tts_results_cover_segment_ids_with_voices(self):
        import er121_family_y_audio_01 as ya
        vm = ya.segment_voice_map()
        self.assertEqual(vm["y_voice_1"], "Puck")
        self.assertEqual(vm["y_voice_2"], "Leda")
        self.assertEqual(vm["y_voice_3"], "Schedar")
        narrator = ya.narrator_voice()
        for sid in ys.Y_NARRATOR_IDS:
            self.assertEqual(vm[sid], narrator, sid)
        for lv in ("b1b", "a2"):
            res = json.load(open(f"{self.out}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
            for sid in ys.Y_SEGMENT_IDS:
                e = res["segments"][sid]
                self.assertEqual(e["status"], "OK")
                self.assertEqual(e["y_tts_voice_requested"], vm[sid])
            self.assertFalse({"full_story_part1", "comment_4", "in_one_line"} & set(res["segments"]))
            dec = json.load(open(f"{self.out}/{lv}/audit/chunk_tts_decision.json", encoding="utf-8"))
            self.assertIs(dec.get("chunk_tts_applicable"), True)      # 委任_04: USER_02 ①でX方式Chunkを正式採用(APPROVED_FOR_PRODUCTION)
            self.assertEqual((dec.get("method"), dec.get("approval"), dec.get("z_b_r1_adopted")), ("X_paragraph_0.2s", "APPROVED_FOR_PRODUCTION", False))

    def test_std_slowdown_for_all_y_body_segments(self):
        res = json.load(open(f"{self.out}/a2/audit/tts_generation_results.json", encoding="utf-8"))
        for sid in ys.Y_SEGMENT_IDS:
            self.assertIs(res["segments"][sid].get("slowdown_applied"), True, sid)

    def test_page_rows_labels_and_notice_outside_body(self):
        html = open(f"{self.out}/pages/index.html", encoding="utf-8").read()
        for sid in ys.Y_SEGMENT_IDS:
            self.assertIn(ys.PAGE_LABEL[sid], html)
        for sid in ys.Y_SEGMENT_IDS:                                    # 内部IDを画面に出さない
            self.assertNotIn(sid, html)
        chk = ys.check_y_page_notice(html)
        self.assertTrue(chk["ok"], chk)
        self.assertEqual(html.count(ys.PAGE_NOTICE_CLASS), 1)
        self.assertLess(html.index(ys.PAGE_NOTICE_CLASS), html.index("<table"))
        self.assertIn('name="robots" content="noindex', html)
        self.assertNotIn("In one line", html)
        self.assertIn(ys.PAGE_NOTICE_JA, html)                            # 承認文言(実投稿に基づく記事=mock themeは全Voiceにsource_idsあり)
        self.assertIn("Voice 1〜3は実在人物の発言をそのまま再現したものではなく", html)
        import er_user_listening_page_common_01 as cp
        self.assertEqual(cp.count_chunk_markers(html), 0)                  # 公開用(既定)にChunk境界マーカーは出ない

    def test_notice_omitted_when_theme_package_has_no_source_ids(self):
        """実投稿に基づかない記事(source_ids無し)では出典主張の説明文を出さず、page_verifyも『説明文なし』を正とする。"""
        orig = self.ctx.theme_package_path
        alt = os.path.join(self.root, "theme_no_source.json")
        with open(alt, "w", encoding="utf-8") as f:
            json.dump({"theme": "mock", "sheets": {f"voice_{i}": {"experiences": [{"id": f"E{i}", "kind": "O", "source_ids": [], "text_ja": "x"}]} for i in (1, 2, 3)}}, f)
        try:
            self.ctx.theme_package_path = alt
            with _quiet():
                r.stage_pages(self.ctx)
            html = open(f"{self.out}/pages/index.html", encoding="utf-8").read()
            self.assertNotIn(ys.PAGE_NOTICE_CLASS, html)
            self.assertNotIn(ys.PAGE_NOTICE_JA, html)
            self.assertEqual(r.evaluate_page_verify(html, f"{self.out}/pages", expect_notice=False), [])
            self.assertTrue(r.evaluate_page_verify(html, f"{self.out}/pages", expect_notice=True))      # 説明文が必要と判定される記事なら欠落はNG
            self.ctx.theme_package_path = None
            with self.assertRaises(r.YE2EStop) as e:                       # 判定不能(Theme Package無し)=黙って落とさずSTOP
                r.stage_pages(self.ctx)
            self.assertIn("FAMILY_Y_THEME_PACKAGE_MISSING_FOR_NOTICE", str(e.exception))
        finally:
            self.ctx.theme_package_path = orig
            with _quiet():
                r.stage_pages(self.ctx)                                    # 共有fixtureを元の公開用ページへ戻す

    def test_dev_pages_marker_count_equals_real_chunk_boundaries_and_public_untouched(self):
        """mock runは全segmentが1段落(実Chunk境界0)のため、audit/chunk_plan_<level>.jsonへ『y_voice_1を2 chunkに分けた』planを一時的に置き、
        devページの⏸が実plan境界と一致(各level1個=計2個)・公開用は0・公開用index.html非上書きを確認する(置いたplanは元に戻す。音声・TTSは不変)。"""
        import er_user_listening_page_common_01 as cp
        pub_before = open(f"{self.out}/pages/index.html", encoding="utf-8").read()
        saved = {}
        for lv in ("b1b", "a2"):
            pp = f"{self.out}/{lv}/audit/chunk_plan_{lv}.json"
            saved[pp] = open(pp, encoding="utf-8").read() if os.path.exists(pp) else None
            doc = json.loads(saved[pp]) if saved[pp] else {"plans": {}}
            text = json.load(open(f"{self.out}/{lv}/parts.json", encoding="utf-8"))["segments"]["y_voice_1"]
            cut = text.rfind(" ", 0, len(text) // 2)
            doc.setdefault("plans", {})["y_voice_1"] = {"parent_id": "y_voice_1", "chunked": True,
                                                         "chunks": [{"chunk_id": "y_voice_1_k1", "index": 1, "text": text[:cut].strip(), "boundary_kind": "paragraph"},
                                                                    {"chunk_id": "y_voice_1_k2", "index": 2, "text": text[cut:].strip(), "boundary_kind": "paragraph"}]}
            json.dump(doc, open(pp, "w", encoding="utf-8"), ensure_ascii=False)
        self.ctx.page_audience = "dev"
        try:
            with _quiet():
                res = r.stage_pages(self.ctx)
            dev = open(f"{self.out}/pages/index_dev.html", encoding="utf-8").read()
            self.assertTrue(res["page"].endswith("index_dev.html"))
            self.assertEqual(cp.count_boundary_marker_spans(dev), 2)                # 実plan境界(各level1)と一致。ASRポーズ由来の⏸は出ない
            self.assertEqual(cp.count_chunk_markers(dev), 4)                        # +2=開発用ページ冒頭の凡例(開発確認用の1行+委任_11の報告表示凡例1行。記号のみ)
            self.assertEqual(res["chunk_markers"], 4)
            self.assertEqual(open(f"{self.out}/pages/index.html", encoding="utf-8").read(), pub_before)    # 公開用index.htmlは上書きされない
            with self.assertRaises(r.YE2EStop) as e:                       # devページは公開用検証/final manifestの対象外
                r.stage_page_verify(self.ctx)
            self.assertIn("FAMILY_Y_PAGE_VERIFY_DEV_PAGE", str(e.exception))
            self.ctx.page_audience = "public"
            with _quiet():
                r.stage_pages(self.ctx)                                         # 委任_11: 試聴ページはaudience無関係に実Chunk境界を⏸表示する
            self.assertEqual(cp.count_boundary_marker_spans(open(f"{self.out}/pages/index.html", encoding="utf-8").read()), 2)
        finally:
            self.ctx.page_audience = "public"
            for pp, txt in saved.items():
                if txt is None:
                    os.remove(pp)
                else:
                    open(pp, "w", encoding="utf-8").write(txt)
            if os.path.exists(f"{self.out}/pages/index_dev.html"):
                os.remove(f"{self.out}/pages/index_dev.html")
            with _quiet():
                r.stage_pages(self.ctx)
        self.assertEqual(cp.count_boundary_marker_spans(pub_before), 0)    # plan注入前の公開ページは境界0

    def test_y_provider_collects_scripts(self):
        import er121_family_y_audio_01 as ya
        segs, extra = ya.YProvider(self.out).collect()
        ids = {s.segment_id for s in segs}
        for lv in ("b1b", "a2"):
            for sid in ys.Y_SEGMENT_IDS:
                self.assertIn(f"{lv}:{sid}", ids)
        self.assertEqual(extra, [])

    def test_study_text_slots_recorded_as_connected(self):
        d = json.load(open(f"{self.out}/study_text_slots.json", encoding="utf-8"))          # 委任_06でPart 1/Part 2を接続(旧『未接続』の記録は撤去)
        self.assertIn("接続済み", d["part2_grammar"])
        self.assertIn("接続済み", d["part1_vocabulary_expressions"])
        self.assertNotIn("未接続", json.dumps(d, ensure_ascii=False))


class StageFramework(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="y_runner_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _through_support(self, ctx):
        with _quiet():
            r.run_stages(ctx, ["text", "translate", "support"])

    def test_regenerate_marks_descendants_stale_and_stops_without_explicit_regenerate(self):
        ctx = _ctx(self.root)
        self._through_support(ctx)
        ctx.regenerate_stage = "translate_b1b"
        w62 = r._m().w62
        with self.assertRaises(w62.FamilyZProvenanceMismatchStop):      # b1bは明示再生成される。同一起動内のa2はstaleのため自動再生成せずSTOP
            with _quiet():
                r.stage_translate(ctx)
        prov = json.load(open(f"{ctx.out_dir}/provenance.json", encoding="utf-8"))
        self.assertIn("translate_a2", prov["downstream_stale"])
        self.assertIn("support_b1b", prov["downstream_stale"])
        # 明示 --regenerate-stage の無い次のstageは自動再生成せずSTOP
        ctx.regenerate_stage = None
        with self.assertRaises(w62.FamilyZProvenanceMismatchStop):
            with _quiet():
                r.stage_translate(ctx)
        with self.assertRaises(w62.FamilyZProvenanceMismatchStop):
            with _quiet():
                r.stage_support(ctx)

    def test_text_change_makes_downstream_input_sha_mismatch_stop(self):
        ctx = _ctx(self.root)
        self._through_support(ctx)
        ctx.regenerate_stage = "text"
        with _quiet():
            r.stage_text(ctx)
        ctx.regenerate_stage = None
        prov = json.load(open(f"{ctx.out_dir}/provenance.json", encoding="utf-8"))
        self.assertIn("translate_b1b", prov["downstream_stale"])

    def test_unknown_regenerate_unit_rejected_by_parser(self):
        with self.assertRaises(SystemExit):
            with _quiet():
                r.build_parser().parse_args(["--regenerate-stage", "no_such_unit"])

    def test_stop_sentinel_stops_before_any_api(self):
        ctx = _ctx(self.root)
        os.makedirs(ctx.out_dir, exist_ok=True)
        open(f"{ctx.out_dir}/STOP", "w").write("{}")
        st = r._m().st
        with self.assertRaises(st.FamilyZStopSentinel):
            with _quiet():
                r.run_stages(ctx, ["text"])
        self.assertEqual(_calls(ctx), 0)
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/text/article_ja.md"))

    def test_stop_sentinel_via_main_returns_rc3_and_no_api(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            run_dir = f"{self.root}/mock_slug/run_x_mock"
            os.makedirs(run_dir, exist_ok=True)
            open(f"{run_dir}/STOP", "w").write("{}")
            with _quiet():
                rc = r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_x", "--stage", "text", "--theme-package", _theme(self.root)])
        self.assertEqual(rc, 3)
        self.assertFalse(os.path.exists(f"{run_dir}/mock_api_calls.jsonl"))

    def test_run_lock_refuses_double_launch_rc4(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            run_dir = f"{self.root}/mock_slug/run_l_mock"
            os.makedirs(run_dir, exist_ok=True)
            holder = os.getppid()                                         # 別の生存process(PIDが生きている)
            json.dump({"pid": holder, "started_ts": 0, "argv": []}, open(f"{run_dir}/RUN_LOCK.json", "w"))
            with mock.patch.object(r._m().st, "pid_alive", lambda pid: True):
                with _quiet():
                    rc = r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_l", "--stage", "text", "--theme-package", _theme(self.root)])
        self.assertEqual(rc, r._m().st.LOCK_EXIT_CODE)
        self.assertFalse(os.path.exists(f"{run_dir}/mock_api_calls.jsonl"))

    def test_restart_storm_stops_with_rc3_and_creates_stop(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            rcs = []
            for _ in range(3):
                with _quiet():
                    rcs.append(r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_s", "--stage", "seed_check", "--theme-package", _theme(self.root)]))
        self.assertEqual(rcs[:2], [0, 0])
        self.assertEqual(rcs[2], r._m().st.STOP_EXIT_CODE)
        self.assertTrue(os.path.exists(f"{self.root}/mock_slug/run_s_mock/STOP"))

    def test_kp_pending_returns_rc4_with_marker_and_stops_before_paid_stages(self):
        out = io.StringIO()
        with mock.patch.object(r, "RUN_ROOT", self.root):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_k", "--stages", "text,translate,support,kp,tts_b1b,tts_a2",
                             "--theme-package", _theme(self.root)])
        self.assertEqual(rc, 4)
        self.assertIn("[KP_REVIEW_PENDING]", out.getvalue())
        run_dir = f"{self.root}/mock_slug/run_k_mock"
        self.assertTrue(os.path.exists(f"{run_dir}/kp_review_pending.json"))
        self.assertFalse(os.path.exists(f"{run_dir}/b1b/audit/tts_generation_results.json"), "KP待機中にTTSへ進んだ")
        kinds = [json.loads(l)["kind"] for l in open(f"{run_dir}/mock_api_calls.jsonl", encoding="utf-8")]
        self.assertFalse([k for k in kinds if k.startswith("tts")])

    def test_kp_auto_requires_by_and_reason(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_a", "--stage", "seed_check", "--kp-review", "auto",
                             "--theme-package", _theme(self.root)])
        self.assertEqual(rc, 2)

    def test_dry_run_has_zero_side_effects(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            before = sorted(os.listdir(self.root))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = r.main(["--mode", "dry-run", "--slug", "mock_slug", "--run", "run_d"])
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(os.listdir(self.root)), before)
        plan = json.loads(out.getvalue())
        self.assertEqual(plan["api_calls"], 0)
        self.assertEqual(plan["side_effects"], 0)
        self.assertEqual([s["stage"] for s in plan["stages"]], list(r.STAGES))

    def test_default_mode_is_dry_run_and_real_needs_budget_before_any_client(self):
        self.assertEqual(r.build_parser().parse_args([]).mode, "dry-run")
        with mock.patch.object(r, "RUN_ROOT", self.root):
            with _quiet():
                rc = r.main(["--mode", "real", "--slug", "mock_slug", "--run", "run_r", "--stage", "seed_check", "--theme-package", _theme(self.root)])
        self.assertEqual(rc, 2)                                         # 予算未承認 → clientもcost_logもdirも作らずSTOP
        self.assertEqual(BLOCK["client"], 0)
        self.assertFalse(os.path.exists(f"{self.root}/mock_slug/run_r"))

    def test_budget_cap_and_guard(self):
        with self.assertRaises(r.YBudgetStop):
            r.E2EBudget(r.APPROVED_BUDGET_MAX_JPY + 1)
        with self.assertRaises(r.YBudgetStop):
            r.E2EBudget(0)
        ctx = _ctx(self.root)
        ctx.budget = r.E2EBudget(10, 5, spent_fn=lambda: 4.9)            # 警告閾値5円: 4.9+見積(text 45)は超過
        with self.assertRaises(r.YBudgetStop):
            with _quiet():
                r.run_stages(ctx, ["text"])
        self.assertEqual(_calls(ctx), 0, "予算超過見込みなのに新規API境界を通った")

    def test_text_core_not_connected_stops_without_artifact(self):
        ctx = _ctx(self.root, hooks={"text_core": object()})
        with self.assertRaises(r.YTextCoreNotConnected):
            with _quiet():
                r.stage_text(ctx)
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/text/article_ja.md"))
        self.assertEqual(_calls(ctx), 0)

    def test_text_core_without_closing_record_stops(self):
        class TC:
            def produce_article(self, client, **kw):
                return {"title": "t", "lead": "l", "intros": {}, "voices": {}, "closing": "c"}
        ctx = _ctx(self.root, hooks={"text_core": TC()})
        with self.assertRaises(r.YE2EStop):
            with _quiet():
                r.stage_text(ctx)
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/text/article_ja.md"))

    def test_text_requires_theme_package(self):
        ctx = r.build_mock_context(self.root, run="run_np", slug="mock_slug", theme_package_path=None)
        with self.assertRaises(r.YE2EStop):
            with _quiet():
                r.stage_text(ctx)

    def test_ja_ai_announce_in_text_stops(self):
        class TC:
            def produce_article(self, client, **kw):
                return {"title": "t", "lead": "実在する人々の声を組み立てました。", "intros": {"voice_1": "a", "voice_2": "b", "voice_3": "c"},
                        "voices": {"voice_1": "私は", "voice_2": "私は", "voice_3": "私は"}, "closing": "終わり", "closing_record": {"source": "x"}}
        ctx = _ctx(self.root, hooks={"text_core": TC()})
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_text(ctx)
        self.assertIn("AI_ANNOUNCE", str(cm.exception))

    def _bad_adv_fn(self, calls):
        def fn(ja, *, client=None, model=None, must_fix=None, **kw):
            calls.append(must_fix)
            body = "p1\n\np2\n\np3"
            return _res("T", body, model, model)
        return fn

    def test_translate_structure_violation_retries_once_then_stops(self):
        calls = []
        try:
            fn = self._bad_adv_fn(calls)
        except TypeError:
            self.skipTest("result dataclass fields changed")
        ctx = _ctx(self.root, hooks={"translate_adv_fn": fn})
        with _quiet():
            r.run_stages(ctx, ["text"])
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_translate(ctx)
        self.assertIn("FAMILY_Y_EN_CONTRACT_VIOLATION", str(cm.exception))
        self.assertEqual(len(calls), 2, "再試行は構造違反につき1回だけ(初回+再試行1)")
        self.assertFalse(os.path.exists(r._level_text_path(ctx, "b1b")), "契約違反の英訳を成果物として残した")

    def test_translate_model_drift_stops(self):
        import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
        def fn(ja, *, client=None, model=None, must_fix=None, **kw):
            import er121_family_y_mock_01 as mk
            body = mk.EN_ADV.split("\n\n", 1)[1]
            return _res(mk.SAMPLE_TITLE_EN, body, "other-model", model)
        ctx = _ctx(self.root, hooks={"translate_adv_fn": fn})
        with _quiet():
            r.run_stages(ctx, ["text"])
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_translate(ctx)
        self.assertIn("MODEL_DRIFT", str(cm.exception))

    def test_tts_without_mock_patch_stops_before_any_tts(self):
        ctx = _ctx(self.root)
        with _quiet():
            r.run_stages(ctx, ["text", "translate", "support"])
            _declare(ctx)
            r.run_stages(ctx, ["kp"])
        ctx.hooks.pop("tts_patch")
        n = _calls(ctx)
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_tts(ctx, "b1b")
        self.assertIn("NO_MOCK_TTS", str(cm.exception))
        self.assertEqual(_calls(ctx), n)

    def test_gate_and_assemble_refuse_stale_or_missing_tts(self):
        ctx = _ctx(self.root)
        with _quiet():
            r.run_stages(ctx, ["text", "translate", "support"])
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_gate(ctx)
        self.assertIn("NOT_FRESH", str(cm.exception))
        with self.assertRaises(r.YE2EStop):
            with _quiet():
                r.stage_assemble(ctx)

    def test_seed_check_fail_closed_on_unregistered_key(self):
        import er006_model_routing_contract_01 as routing
        ctx = _ctx(self.root)
        saved = routing.PROCESS_MODEL_MAP.pop("FAMILY_Y_LEAD_GENERATE")
        try:
            with self.assertRaises(r.YE2EStop):
                r.stage_seed_check(ctx)
        finally:
            routing.PROCESS_MODEL_MAP["FAMILY_Y_LEAD_GENERATE"] = saved
        self.assertEqual(r.stage_seed_check(ctx)["voice_assignment"]["y_fixed_slots"]["voice_1"], "Puck")

    def test_clear_stop_requires_reason(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            with _quiet():
                self.assertEqual(r.main(["--clear-stop", "--slug", "mock_slug", "--run", "run_c"]), 2)



def _kinds(ctx):
    p = f"{ctx.out_dir}/mock_api_calls.jsonl"
    if not os.path.exists(p):
        return []
    return [json.loads(l)["kind"] for l in open(p, encoding="utf-8")]


def _html(ctx):
    return open(f"{ctx.out_dir}/pages/index.html", encoding="utf-8").read()


@legacy_unmarked_class
class StudyTextWiring(unittest.TestCase):
    """委任_06: Part 1(Vocabulary & Expressions)/Part 2(文法)/文法HRのY runner接続(X/Zと同形。API 0・遮断harness)。"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="y_study_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _upto_support(self, ctx):
        with _quiet():
            r.run_stages(ctx, ["seed_check", "text", "translate", "support"])

    def _grammar_dir(self, ctx, level="b1b"):
        return r._part2_dir(ctx, level)

    def _decide_grammar(self, ctx, by="test-human", level="b1b"):
        import er119_grammar_review_01 as gr
        sd = self._grammar_dir(ctx, level)
        doc = gr.load_candidates(sd)
        return gr.op_decide(sd, choice="top1", candidates_sha256=doc["candidates_sha256"], by=by, accept_ai=True)

    def test_single_wait_for_kp_and_grammar_with_no_paid_call_after(self):
        ctx = _ctx(self.root)
        self._upto_support(ctx)
        n0 = _kinds(ctx).count("llm")
        with self.assertRaises(r.YKpReviewPending) as cm:
            with _quiet():
                r.run_stages(ctx, ["kp"])
        kinds_pending = sorted({(p.get("kind") or "kp") for p in cm.exception.pending})
        self.assertEqual(kinds_pending, ["grammar", "kp"])                                  # KP(b1b/a2)と文法(Adv/Std)が1つの待機にまとまる
        self.assertEqual(sum(1 for p in cm.exception.pending if p.get("kind") == "grammar"), 2)
        k = _kinds(ctx)
        self.assertEqual(k.count("part2_extract"), 2)                                       # 候補抽出はKP候補生成と同じ待機点で両levelに1回ずつ
        self.assertGreater(k.count("part2_explain"), 0)                                     # 全候補の解説は待機の前に事前生成(解説全文を見せてから選ばせる)
        for banned in ("kp_part1", "kp_part1_ja", "kp_expl", "tts", "tts_shared", "tts_kp"):
            self.assertNotIn(banned, k, f"確定前に{banned}の有料呼出に進んだ")               # 確定前のPart 1・TTSは0 call
        self.assertEqual(k.count("llm"), n0)
        # 同じ起動で統合依頼書(1ファイル)にKPと文法が両方入る
        out = io.StringIO()
        with mock.patch.object(r, "RUN_ROOT", self.root):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_w", "--stages", "text,translate,support,kp,tts_b1b",
                             "--theme-package", _theme(self.root)])
        self.assertEqual(rc, 4)
        self.assertIn("[KP_REVIEW_PENDING]", out.getvalue())
        self.assertIn("文法(Part 2)", out.getvalue())
        req = open(f"{self.root}/mock_slug/run_w_mock/review_request.md", encoding="utf-8").read()
        self.assertIn("文法(Part 2)", req)
        self.assertIn("KP(level=b1b)", req)
        self.assertFalse(os.path.exists(f"{self.root}/mock_slug/run_w_mock/b1b/audit/tts_generation_results.json"))

    def test_hr_path_resume_calls_step_b_once_and_part1_once_then_resume_is_api0(self):
        ctx = _ctx(self.root)
        self._upto_support(ctx)
        with self.assertRaises(r.YKpReviewPending):
            with _quiet():
                r.run_stages(ctx, ["kp"])
        n_expl = _kinds(ctx).count("part2_explain")
        self._decide_grammar(ctx)                       # HRあり: Advancedの文法をHumanがAI推奨のまま了承(REVIEWED)
        _declare(ctx)                                   # KP側とStandardの文法は不在宣言(Advancedの文法はすでに確定済み)
        with _quiet():
            res = r.run_stages(ctx, ["kp"])
        k = _kinds(ctx)
        # 確定後のfinalizeはLLM 0: 解説は待機の前の事前生成のみ(再開で増えない)。Part 1は確定後に1回ずつ
        self.assertEqual((k.count("part2_extract"), k.count("part2_explain"), k.count("kp_part1"), k.count("kp_part1_ja")), (2, n_expl, 1, 1))
        self.assertEqual(res["kp"][r.PART2_FINAL_STAGE], "generated")
        self.assertEqual(res["kp"][r.PART2_STAGES["a2"]["final"]], "generated")
        rev = json.load(open(f"{self._grammar_dir(ctx)}/grammar_human_review.json", encoding="utf-8"))
        self.assertEqual(rev["status"], "REVIEWED")
        before = _calls(ctx)
        with _quiet():
            res2 = r.run_stages(ctx, ["kp"])
        self.assertEqual(_calls(ctx), before, "再開(resume)でAPI境界を通った")
        self.assertEqual((res2["kp"][r.PART1_STAGES["b1b"]["gen"]], res2["kp"][r.PART1_STAGES["b1b"]["ja"]], res2["kp"][r.PART2_FINAL_STAGE], res2["kp"][r.PART2_STAGES["a2"]["final"]]),
                         ("reused", "reused", "reused", "reused"))

    def test_d1_user_confirmation_after_auto_adoption_rebinds_kp_provenance_without_stop_or_api(self):
        """KCP3所見D1: 自動採用runへ後からユーザー確定を入れても kp_<lv> 来歴の親sha不一致STOPにならず、API 0で再バインド(子孫staleなし)。"""
        import er119_kp_human_review_01 as rv
        ctx = _ctx(self.root)
        self._upto_support(ctx)
        _declare(ctx)
        with _quiet():
            r.run_stages(ctx, ["kp"])
        prov0 = json.load(open(f"{ctx.out_dir}/provenance.json", encoding="utf-8"))
        e0 = dict(prov0["downstream_stages"]["kp_b1b"])
        src = r._kp_src_dir(ctx, "b1b")
        rev = rv.load_review(src)
        self.assertEqual(rev["status"], rv.ST_AUTO)
        doc = rv.load_candidates(src)
        rank_of = {c["candidate_id"]: c["ai_rank"] for c in doc["candidates"]}
        rv.op_select(src, kp_ranks=[rank_of[i] for i in rev["selection"]["kp"]], vocab_ranks=[rank_of[i] for i in rev["selection"]["vocab"]], by="human")
        before = _calls(ctx)
        with _quiet():
            r.run_stages(ctx, ["kp"])                                              # 以前は kp_b1b の親sha不一致STOP
        self.assertEqual(_calls(ctx), before, "再バインドでAPI境界を通った")
        prov1 = json.load(open(f"{ctx.out_dir}/provenance.json", encoding="utf-8"))
        e1 = prov1["downstream_stages"]["kp_b1b"]
        self.assertNotEqual(e1["input_sha256"], e0["input_sha256"])
        self.assertEqual(e1["output_sha256"], e0["output_sha256"])
        self.assertEqual([x["api_calls"] for x in e1["rebinds"]], [0])
        self.assertEqual([x for x in prov1["downstream_stale"] if x.startswith(("tts_", "kp_expl", "kp_part1"))], [])   # TTS等の子孫はstale化しない
        # 明示regenerate指定時は付け替えない(従来の経路)
        self.assertNotIn("rebinds", prov1["downstream_stages"].get("kp_a2", {}))

    def test_no_hr_declaration_auto_adopts_grammar_and_records_it(self):
        ctx = _ctx(self.root)
        self._upto_support(ctx)
        _declare(ctx)
        with _quiet():
            r.run_stages(ctx, ["kp"])
        rev = json.load(open(f"{self._grammar_dir(ctx)}/grammar_human_review.json", encoding="utf-8"))
        self.assertEqual(rev["status"], "UNREVIEWED_AUTO_ADOPTED")                          # 未レビュー自動採用(REVIEWED/NGと区別)
        self.assertTrue(rev["mode_declaration"]["declaration_id"])
        self.assertIsNone(rev.get("last_human_op_at"))

    def test_page_shows_part2_in_both_sections_part1_only_in_advanced_and_vocab_is_five_adv_only(self):
        ctx = _ctx(self.root)
        self._upto_support(ctx)
        _declare(ctx)
        with _quiet():
            r.run_stages(ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"])
        html = _html(ctx)
        i_adv = html.index("id='advanced'")
        std_part, adv_part = html[:i_adv], html[i_adv:]
        self.assertNotIn(r.PART1_MARKER, std_part, "StandardにPart 1が出ている(Part 1はAdvancedのみ)")
        self.assertEqual(std_part.count(r.PART2_MARKER), 1, "Standardの節にPart 2(文法)が1個ない")      # 全level化: Standardにも同じテンプレートで載る
        for mk in (r.PART1_MARKER, r.PART2_MARKER):
            self.assertEqual(adv_part.count(mk), 1, mk)
        self.assertTrue(r._blocks_in_page_order(adv_part, "<h3>ニュアンス解説</h3>"))      # Part 1→文法→ニュアンス解説(存在するブロック同士の相対順。文法0件でも成立。M-5)
        p1 = json.load(open(f"{ctx.out_dir}/study_text/part1_vocabulary_expressions.json", encoding="utf-8"))
        rows = p1 if isinstance(p1, list) else (p1.get("rows") or p1.get("items") or [])
        self.assertLessEqual(len(rows), 5)
        self.assertGreaterEqual(len(rows), 3)
        self.assertTrue(json.load(open(f"{ctx.out_dir}/page_verify_local.json", encoding="utf-8"))["ok"])
        v = json.load(open(f"{ctx.out_dir}/page_verify_local.json", encoding="utf-8"))
        self.assertEqual((v["part2_verified"]["b1b"]["part2_blocks"], v["part2_verified"]["a2"]["part2_blocks"]), (1, 1))     # 節単位の4者一致
        self.assertEqual(set(v["kp_selection_verified"]), {"b1b", "a2"})
        slots = json.load(open(f"{ctx.out_dir}/study_text_slots.json", encoding="utf-8"))
        self.assertIn("接続済み", slots["part2_grammar"])
        self.assertNotIn("未接続", json.dumps(slots, ensure_ascii=False))

    def test_zero_candidates_uses_fixed_text_without_waiting(self):
        import er120_part2_grammar_production_01 as g

        def zero_extract(prompt):
            import er006_model_routing_contract_01 as routing
            return json.dumps({"features": [], "no_feature_paras": []}), routing.SUPPORT_MODEL, {"input_tokens": 1, "output_tokens": 1, "cached_input_tokens": 0}, "mock_zero"
        ctx = _ctx(self.root)
        ctx.hooks["part2_extract_call_fn"] = ctx.mock_api.wrap("part2_extract", zero_extract)
        self._upto_support(ctx)
        _declare(ctx)
        with _quiet():
            r.run_stages(ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"])
        rev = json.load(open(f"{self._grammar_dir(ctx)}/grammar_human_review.json", encoding="utf-8"))
        self.assertEqual(rev["status"], "NO_CANDIDATE_UNREVIEWED")                         # 適格0件=待たずに確定(REVIEWEDにしない)
        _h = _html(ctx).replace("&#x27;", "'")
        self.assertNotIn("特に取り上げる難所", _h)                                          # 固定文面は撤去(0件確定はコーナー全体を非表示。2026-10-29 §2C)
        self.assertEqual(_h.count(r.PART2_MARKER), 0)                                       # 見出し・空枠も出さない(Std+Adv)
        self.assertEqual(_h.count("<section class='study'>"), 1)                            # Advanced の Part 1 のみ
        rev_std = json.load(open(f"{self._grammar_dir(ctx, 'a2')}/grammar_human_review.json", encoding="utf-8"))
        self.assertEqual(rev_std["status"], "NO_CANDIDATE_UNREVIEWED")

    def test_two_items_adopted_in_standard_render_in_one_block_and_pass_section_verification(self):
        """O-4(OPEN-543の新仕様へ更新: 文法は1levelあたり0〜1件[GRAMMAR_MAX=1]): Standardで2件選択は拒否され、1件採用が節内の1ブロックに載り、節単位の4者一致検査(page_verify)を通る。"""
        import er120_part2_grammar_production_01 as g0
        import er119_grammar_review_01 as gr
        ctx = _ctx(self.root)
        self._upto_support(ctx)
        with self.assertRaises(r.YKpReviewPending):
            with _quiet():
                r.run_stages(ctx, ["kp"])
        sd_std = self._grammar_dir(ctx, "a2")
        doc = gr.load_candidates(sd_std)
        self.assertGreaterEqual(len(doc["candidates"]), 2)
        with self.assertRaises(g0.Part2ReviewError):      # 2件選択は禁止(新仕様: 最大1件)
            gr.op_decide(sd_std, choice="pick", ids=[doc["candidates"][1]["candidate_id"], doc["candidates"][0]["candidate_id"]], reason="2件採用(test)",
                         candidates_sha256=doc["candidates_sha256"], by="test-human")
        gr.op_decide(sd_std, choice="pick", ids=[doc["candidates"][1]["candidate_id"]], reason="1件採用(test)",
                     candidates_sha256=doc["candidates_sha256"], by="test-human")
        self._decide_grammar(ctx)
        _declare(ctx)
        with _quiet():
            r.run_stages(ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"])
        res = json.load(open(f"{sd_std}/part2_result.json", encoding="utf-8"))
        import er120_part2_grammar_production_01 as g
        items = g.result_items(res)
        self.assertEqual(len(items), 1)
        v = json.load(open(f"{ctx.out_dir}/page_verify_local.json", encoding="utf-8"))
        self.assertEqual((v["part2_verified"]["a2"]["part2_blocks"], v["part2_verified"]["b1b"]["part2_blocks"]), (1, 1))

    def test_consumer_entrances_fail_closed_when_part1_or_part2_missing(self):
        ctx = _ctx(self.root)
        self._upto_support(ctx)
        # (a) 未確定(待機)中は全consumerがrc=4相当の待機で止まり、TTS/組立/ページへ進まない
        for fn in (lambda: r.stage_tts(ctx, "b1b"), lambda: r.stage_gate(ctx), lambda: r.stage_assemble(ctx), lambda: r.stage_pages(ctx),
                   lambda: r.stage_page_verify(ctx)):
            with self.assertRaises((r.YKpReviewPending, r.YE2EStop)):
                with _quiet():
                    fn()
        _declare(ctx)
        with _quiet():
            r.run_stages(ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"])
        sd = self._grammar_dir(ctx)
        # (b) Part 2結果が消えた/古い → 使う側の入口でSTOP
        res_path = f"{sd}/part2_result.json"
        keep = open(res_path, encoding="utf-8").read()
        os.remove(res_path)
        for name, fn in (("tts_b1b", lambda: r.stage_tts(ctx, "b1b")), ("gate", lambda: r.stage_gate(ctx)), ("assemble", lambda: r.stage_assemble(ctx)),
                         ("pages", lambda: r.stage_pages(ctx)), ("page_verify", lambda: r.stage_page_verify(ctx))):
            with self.assertRaises((r.YE2EStop, r.YKpReviewPending), msg=name):
                with _quiet():
                    fn()
        open(res_path, "w", encoding="utf-8").write(keep)
        # (b') Standard(a2)のPart 2結果が消えた → ページ専用: pages/page_verifyだけSTOP。tts_a2/gate/assembleの前提にはしない(音声はPart 2に依存しない)
        res_std = f"{self._grammar_dir(ctx, 'a2')}/part2_result.json"
        keep_std = open(res_std, encoding="utf-8").read()
        os.remove(res_std)
        for name, fn in (("pages", lambda: r.stage_pages(ctx)), ("page_verify", lambda: r.stage_page_verify(ctx))):
            with self.assertRaises((r.YE2EStop, r.YKpReviewPending), msg=name):
                with _quiet():
                    fn()
        r._assert_study_ready(ctx, "gate")        # Advanced側は無傷=gate/assembleの入口は通る(Standardの文法欠落で止まらない)
        open(res_std, "w", encoding="utf-8").write(keep_std)
        # (c) Part 1の解説が消えた → STOP(次コマンド付き)
        p1 = f"{ctx.out_dir}/key_phrases/b1b/kp_general_explanations.json"
        keep1 = open(p1, encoding="utf-8").read()
        os.remove(p1)
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_pages(ctx)
        self.assertIn("PART1", str(cm.exception))
        self.assertIn("--regenerate-stage", str(cm.exception))
        open(p1, "w", encoding="utf-8").write(keep1)
        with _quiet():
            r.stage_pages(ctx)                                                                # 復元後は通る(回帰)

    def test_part2_regenerate_marks_final_stale_and_text_change_marks_part2_stale(self):
        ctx = _ctx(self.root)
        self._upto_support(ctx)
        _declare(ctx)
        with _quiet():
            r.run_stages(ctx, ["kp"])
        ctx.regenerate_stage = "translate_b1b"
        w62 = r._m().w62
        with self.assertRaises(w62.FamilyZProvenanceMismatchStop):
            with _quiet():
                r.stage_translate(ctx)
        prov = json.load(open(f"{ctx.out_dir}/provenance.json", encoding="utf-8"))
        self.assertIn("part2_cand_b1b", prov["downstream_stale"])
        self.assertIn("part2_b1b", prov["downstream_stale"])
        self.assertIn("part2_a2", prov["downstream_stale"])                          # 既存の依存辺 translate_b1b -> translate_a2 を経由してStandardの文法もstale(葉のまま・新しい辺なし)
        self.assertIn("part2_cand_a2", prov["downstream_stale"])                     # Standardの文法候補・finalも葉としてstale(TTS等への新しい依存辺なし)

    def test_study_units_are_regenerate_choices(self):
        for u in (*[r.PART1_STAGES[lv][k] for lv in ("b1b", "a2") for k in ("gen", "ja")], r.PART2_CAND_STAGE, r.PART2_FINAL_STAGE, "part2_cand_a2", "part2_a2"):
            self.assertIn(u, r.UNIT_NAMES)
            r.build_parser().parse_args(["--regenerate-stage", u])


class StudyTextStructureMatchWithXZ(unittest.TestCase):
    """Part 1/Part 2の共通呼出しがZ runner(er026)と一致すること(許可リストは台帳ID付き。Zに共通呼出しが増えたらYも追従する)。"""

    ZFUNCS = ("_part2_cand_step", "_part2_final_step", "_part2_pool", "_assert_part2_final", "_verify_part2_outputs", "_stage_kp_part1", "_stage_kp_part1_ja",
              "_assemble_study_rows", "_require_part1_fresh", "_require_part1_ja_fresh", "_part1_items_b1b", "_stage_precheck")
    Y_RENAMED = {"_part1_items_b1b": "_part1_items"}     # SLOT-23 委任_04D: Y側はlevel引数化した _part1_items(ctx, level)。Z(er026)は従来名のまま
    ALLOWED_Z_ONLY = {
        "m._m": "Y-DIFF-MODULE-ALIAS(Zのm=_m()の別名参照。Yは_m()を直接呼ぶ)",
        "m.w62.rj": "Y-DIFF-MODULE-ALIAS", "_m().w62.rj": "Y-DIFF-MODULE-ALIAS",
        "canonical_article_text": "Y-DIFF-TEXT-INPUT(Yはys.canonical_body)", "_m().w62.rd": "Y-DIFF-MODULE-ALIAS",
        "_part1_cli_hint": "Y-DIFF-CLI-HINT(Yは_cli_hint)", "FamilyZE2EStop": "Y-DIFF-EXC(YE2EStop)", "FamilyZKpReviewPending": "Y-DIFF-EXC(YKpReviewPending)",
        "STORY_REGISTRY": "Y-DIFF-LABEL(Zは作品名label、Yはタイトル行)",
        "w62.FamilyZProvenanceMismatchStop": "Y-DIFF-MODULE-ALIAS", "w62.ensure_stage": "Y-DIFF-ENSURE(Yは_ensure経由またはw62.ensure_stage)",
        "m.w62.FamilyZProvenanceMismatchStop": "Y-DIFF-MODULE-ALIAS",
        "_m().w62.rj_or": "unused",
    }

    @staticmethod
    def _callees(path, names):
        tree = ast.parse(open(os.path.join(ROOT, path), encoding="utf-8").read())
        out = set()
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in names]:
            for c in ast.walk(fn):
                if isinstance(c, ast.Call):
                    f, parts = c.func, []
                    while isinstance(f, ast.Attribute):
                        parts.append(f.attr)
                        f = f.value
                    if isinstance(f, ast.Name):
                        parts.append(f.id)
                    out.add(".".join(reversed(parts)))
        return out

    def test_common_core_calls_match_z(self):
        z = self._callees("er026_family_z_fiction_production_runner_01.py", set(self.ZFUNCS))
        y_funcs = {n for n in self.ZFUNCS} | set(self.Y_RENAMED.values()) | {"stage_pages", "stage_kp", "_assert_study_ready", "_assert_std_study_ready"}
        y = self._callees("er121_family_y_runner_01.py", y_funcs)
        core = {n for n in z if n.split(".")[0] in ("p2w", "g", "p1", "ja", "khr", "gr", "_p1", "_p2w", "_p1ja", "_khr") or n.startswith(("p2w.", "g.", "p1.", "ja.", "_p1().", "_p2w().", "_p1ja().", "_khr()."))}
        core = {n.replace("_p2w().", "p2w.").replace("_p1().", "p1.").replace("_p1ja().", "ja.").replace("_khr().", "khr.") for n in core}
        y_norm = {n.replace("_p2w().", "p2w.").replace("_p1().", "p1.").replace("_p1ja().", "ja.").replace("_khr().", "khr.") for n in y}
        missing = {n for n in core if n not in y_norm and n not in self.ALLOWED_Z_ONLY}
        self.assertEqual(missing, set(), f"Zの共通核(er119/er120/er003_kp_*)呼出しがYに無い: {sorted(missing)}")
        for must in ("p2w.candidate_stage", "p2w.finalize_stage", "p2w.require_final", "p2w.verify_outputs", "compose_page_html", "p2w.part1_ref_ja_pool",
                     "p1.generate_for_kp_items", "ja.generate_for_kp_items", "p1.assemble_part1", "p1.write_study_text", "render_html_block", "khr.part1_items"):
            self.assertIn(must, y_norm, must)

    def test_stage_names_match_the_shared_core_for_both_levels(self):
        """YのPART2_STAGES(level別 cand/expl/final)は共通核 er120_part2_wiring_01.stage_names と一致(Zも同じ)。UNIT_NAMESに cand/final が両levelある。"""
        import er120_part2_wiring_01 as p2w
        import er026_family_z_fiction_production_runner_01 as z
        for lv in ("b1b", "a2"):
            self.assertEqual(r.PART2_STAGES[lv], p2w.stage_names(lv))
            self.assertEqual(z.PART2_STAGES[lv], p2w.stage_names(lv))
            self.assertIn(p2w.stage_names(lv)["cand"], r.UNIT_NAMES)
            self.assertIn(p2w.stage_names(lv)["final"], r.UNIT_NAMES)
        # 文法のstageは葉(TTS等への依存辺を張らない)
        for lv in ("b1b", "a2"):
            self.assertNotIn(p2w.stage_names(lv)["cand"], sum([v for k, v in r.DEPENDENTS.items() if k.startswith("tts_")], []))
            self.assertEqual(r.DEPENDENTS.get(p2w.stage_names(lv)["final"]), None)

    def test_consumer_entrances_call_assert_study_ready(self):
        src = open(os.path.join(ROOT, "er121_family_y_runner_01.py"), encoding="utf-8").read()
        tree = ast.parse(src)
        want = {"stage_tts": 1, "stage_gate": 1, "stage_assemble": 1, "stage_pages": 1, "stage_page_verify": 1}
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in want]:
            calls = [c for c in ast.walk(fn) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "_assert_study_ready"]
            self.assertGreaterEqual(len(calls), 1, f"{fn.name}の入口で_assert_study_readyを呼んでいない(Part 1/2のfail-closed確認漏れ)")


class ManifestModelTransfer(unittest.TestCase):
    def test_unit_models_are_transferred_from_cost_log_tags(self):
        by_tag = {"yp_voice_voice_1": {"gpt-6.1-sol": 1}, "yp_vmap_voice_1_m1": {"gpt-6-luna": 1}, "support": {"gpt-6-luna": 8}, "kp": {"gpt-6-luna": 12},
                  "tts_b1b": {"gpt-6-luna": 1, "gemini-3.8-flash-lite-tts": 20}, "kp_part1": {"gpt-6-luna": 1},
                  "part2_cand_b1b": {"gpt-6-luna": 1}, "part2_expl_b1b": {"gpt-6-luna": 2}, "part2_cand_a2": {"gpt-6-luna": 1}, "part2_expl_a2": {"gpt-6-luna": 3}}
        self.assertEqual(r._unit_models("text", by_tag), {"gpt-6.1-sol": 1, "gpt-6-luna": 1})
        self.assertEqual(r._unit_models("support_b1b", by_tag), {"gpt-6-luna": 8})
        self.assertEqual(r._unit_models("kp_b1b", by_tag), {"gpt-6-luna": 12})
        self.assertEqual(r._unit_models("kp_part1_b1b", by_tag), {"gpt-6-luna": 1})
        self.assertEqual(r._unit_models("part2_cand_b1b", by_tag), {"gpt-6-luna": 3})     # 候補抽出+解説の事前生成(Step Bの唯一の呼出点)
        self.assertEqual(r._unit_models("part2_cand_a2", by_tag), {"gpt-6-luna": 4})
        self.assertEqual(r._unit_models("part2_b1b", by_tag), {})                          # finalizeはLLM 0
        self.assertEqual(r._unit_models("translate_a2", by_tag), {})

    def test_final_manifest_has_model_fields_for_support_kp_when_cost_log_exists(self):
        root = tempfile.mkdtemp(prefix="y_man_")
        try:
            ctx = _ctx(root)
            with _quiet():
                r.run_stages(ctx, ["text", "translate", "support"])
                _declare(ctx)
                r.run_stages(ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages"])
            with open(f"{ctx.out_dir}/cost_log.jsonl", "w", encoding="utf-8") as f:
                for tag, mid in (("support", "gpt-6-luna"), ("kp", "gpt-6-luna"), ("yp_closing_gen", "gpt-6.1-sol"), ("yp_closing_leak1", "gpt-6-luna")):
                    f.write(json.dumps({"stage": tag, "model_id": mid}) + "\n")
            with _quiet():
                r.write_final_manifest(ctx)
            man = json.load(open(f"{ctx.out_dir}/final_manifest.json", encoding="utf-8"))
            for u in ("support_b1b", "support_a2", "kp_b1b", "kp_a2", "kp_expl_b1b"):
                self.assertEqual(man["stage_entries"][u]["actual_model_id"], "gpt-6-luna", u)
            self.assertIsNone(man["stage_entries"]["text"]["actual_model_id"])               # textは複数model(sol+luna)=単一値にしない
            self.assertEqual(man["stage_entries"]["text"]["models_used"], {"gpt-6.1-sol": 1, "gpt-6-luna": 1})
            self.assertIn("closing", man["stage_entries"]["text"]["routes"])
            self.assertTrue(man["stage_entries"]["kp_part1_b1b"]["actual_model_id"])          # Part 1はentryのmodelを転記
        finally:
            shutil.rmtree(root, ignore_errors=True)


class SelfConsistency(unittest.TestCase):
    def test_dependents_only_reference_known_units(self):
        for k, v in r.DEPENDENTS.items():
            self.assertIn(k, r.UNIT_NAMES)
            for x in v:
                self.assertIn(x, r.UNIT_NAMES)

    def test_no_er110_import_and_no_chunk_or_core_numeric_import(self):
        banned_prefix = ("er110_", "er095_", "er118_")      # 委任_04: er117(X方式Chunk共通module)はUSER_02 ①で採用。importしてよいのはaudit moduleのみ(下で固定)
        for fn in ("er121_family_y_runner_01.py", "er121_family_y_audio_01.py", "er121_family_y_structure_01.py", "er121_family_y_mock_01.py"):
            tree = ast.parse(open(os.path.join(ROOT, fn), encoding="utf-8").read())
            for n in ast.walk(tree):
                mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module] if isinstance(n, ast.ImportFrom) and n.module else [])
                for m in mods:
                    self.assertFalse(m.startswith(banned_prefix), f"{fn} が {m} をimportしている(DEV Trial/Chunk/中核数値の混入禁止)")

    def test_stage_names_include_kp_review_and_no_part_stage(self):
        self.assertIn("kp", r.STAGES)
        self.assertFalse([s for s in r.STAGES if "part2" in s or "in_one_line" in s])


if __name__ == "__main__":
    unittest.main()
