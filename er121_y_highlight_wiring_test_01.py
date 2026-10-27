# -*- coding: utf-8 -*-
"""SLOT-23-CONSUMER-DESIGN-01 委任_04D: Family Y の本文ハイライト(①太字+二重下線/②太字+下線/③下線)・③訳リスト・Std Part 1 level化・Validator置換・page_verify G3 の配線test。

API 0(mock KP/TTS/LLM。遮断harnessは既存 er121_family_y_runner_01_test_01 のものを再利用)。マーク発行(new_reviewへの接続)は本委任の範囲外(B班・M14)なので、
マーク付きの状況は『new_reviewがissue_std_part1_markを呼ぶ=接続後』を test 内で一時的に模擬して作る(Productionコードは変更しない)。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er121_family_y_runner_01_test_01 as base  # noqa: E402  (遮断harness・mock context helperを再利用)
import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_audio_01 as ya  # noqa: E402
import er119_kp_human_review_01 as rv  # noqa: E402
import er_learning_highlight_01 as hl  # noqa: E402
import er_user_listening_page_common_01 as cp  # noqa: E402
from er119_test_support_01 import legacy_unmarked_class  # noqa: E402  (旧マーク無し記事の再現。SLOT-23 委任_05M)

_quiet, _ctx, _declare = base._quiet, base._ctx, base._declare
ALL_STAGES = ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"]
GOLDEN = os.path.join(ROOT, "docs", "research", "SLOT-23-CONSUMER-DESIGN-01", "fixtures", "y_golden_run_style_fix_01.json")


def setUpModule():
    base.setUpModule()


def tearDownModule():
    base.tearDownModule()


class _marks_connected:
    """M14接続後(new_reviewがマークを発行する)の挙動を、この test の間だけ模擬する(Productionコードは未接続のまま)。"""

    def __enter__(self):
        orig = rv.new_review
        self._p = mock.patch.object(rv, "new_review", lambda *a, **k: rv.issue_std_part1_mark(orig(*a, **k)))
        self._p.start()
        return self

    def __exit__(self, *exc):
        self._p.stop()


def _run(root, marked: bool):
    ctx = _ctx(root)
    with _quiet():
        r.run_stages(ctx, ["seed_check", "text", "translate", "support"])
        _declare(ctx)
        if marked:
            with _marks_connected():
                r.run_stages(ctx, ALL_STAGES)
        else:
            r.run_stages(ctx, ALL_STAGES)
    return ctx


def _page(ctx, name="index.html"):
    with open(f"{ctx.out_dir}/pages/{name}", encoding="utf-8") as f:
        return f.read()


def _sec(page, lv):
    return cp.level_section_html(page, r.PAGE_SECTION_IDS[lv])


def _hl_ids(section):
    return re.findall(r'data-hl="([^"]+)"', section)


class MarkedPipeline(unittest.TestCase):
    """マーク付き(display_spec付き)の新規記事: Advanced/Standard両levelでPart 1(ちょうど1個)+本文ハイライトがページに載り、page_verifyのG3を通る。"""

    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="y_hl_marked_")
        cls.ctx = _run(cls.root, marked=True)
        cls.out = cls.ctx.out_dir

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_display_spec_present_on_both_levels_and_std_part1_enabled(self):
        import er128_kp_confirmed_content_01 as cc
        for lv in r.LEVELS:
            self.assertEqual(cc.display_spec_of(self.out, lv), cc.DISPLAY_SPEC_V1)
            self.assertTrue(r._part1_level_enabled(self.ctx, lv))

    def test_each_level_section_has_exactly_one_part1_before_part2(self):
        page = _page(self.ctx)
        for lv in r.LEVELS:
            sec = _sec(page, lv)
            self.assertEqual(sec.count(r.PART1_MARKER), 1, lv)
            self.assertEqual(sec.count(r.PART2_MARKER), 1, lv)
            self.assertLess(sec.index(r.PART1_MARKER), sec.index(r.PART2_MARKER), lv)       # Part 1 → Part 2
        v = json.load(open(f"{self.out}/page_verify_local.json", encoding="utf-8"))
        self.assertTrue(v["ok"])
        self.assertEqual(v["part2_verified"]["a2"]["part1_blocks"], 1)

    def test_std_part1_uses_level_specific_stage_dir_and_provenance(self):
        self.assertTrue(os.path.exists(f"{self.out}/key_phrases/a2/{r._p1().EXPLANATIONS_FILENAME}"))
        self.assertTrue(os.path.exists(f"{self.out}/a2/study_text/{r._p1().PART1_FILE_STEM}.json"))      # Std Part 1のstudy_text(Part 2と同じlevel別dir)
        self.assertTrue(os.path.exists(f"{self.out}/study_text/{r._p1().PART1_FILE_STEM}.json"))         # Advは従来の場所
        doc = json.load(open(f"{self.out}/key_phrases/a2/{r._p1().EXPLANATIONS_FILENAME}", encoding="utf-8"))
        self.assertEqual(doc.get("level"), "a2")
        doc_b = json.load(open(f"{self.out}/key_phrases/b1b/{r._p1().EXPLANATIONS_FILENAME}", encoding="utf-8"))
        self.assertNotEqual(doc_b.get("level"), "a2")                                                       # Advの保存JSONにlevel印は付かない(従来と同一)
        prov = r._prov(self.ctx)
        for lv in r.LEVELS:
            for k in ("gen", "ja"):
                self.assertIsNotNone(prov.stage_entry(r.PART1_STAGES[lv][k]), r.PART1_STAGES[lv][k])
        rows = json.load(open(f"{self.out}/a2/study_text/{r._p1().PART1_FILE_STEM}.json", encoding="utf-8"))
        self.assertEqual(rows.get("level"), "Standard")

    def test_resume_of_kp_is_api0_and_reuses_std_part1(self):
        before = base._calls(self.ctx)
        with _quiet():
            res = r.run_stages(self.ctx, ["kp"])
        self.assertEqual(base._calls(self.ctx), before)
        self.assertEqual(res["kp"][r.PART1_STAGES["a2"]["gen"]], "reused")
        self.assertEqual(res["kp"][r.PART1_STAGES["a2"]["ja"]], "reused")

    def test_highlights_resolved_each_candidate_once_per_level_and_g3_passed(self):
        page = _page(self.ctx)
        v = json.load(open(f"{self.out}/page_verify_local.json", encoding="utf-8"))["highlight_verified"]
        for lv in r.LEVELS:
            sec = _sec(page, lv)
            ids = _hl_ids(sec)
            self.assertEqual(len(ids), 5, lv)                                    # ①3+②2 を各1出現(mock record)
            self.assertEqual(len(set(ids)), 5, lv)
            self.assertEqual(sec.count('class="lk1"'), 3, lv)
            self.assertEqual(sec.count('class="lk2"'), 2, lv)
            self.assertEqual(v[lv]["status"], "PASS", lv)
            self.assertFalse(v[lv]["disabled_marker"])
            audit = json.load(open(f"{self.out}/audit/highlight_resolution_{lv}.json", encoding="utf-8"))
            self.assertEqual(audit["status"], "OK")
            self.assertEqual(audit["issues"], [])

    def test_body_text_unchanged_by_decoration(self):
        page = _page(self.ctx)
        for lv in r.LEVELS:
            sec = _sec(page, lv)
            stripped = hl.strip_decoration(sec)
            segs = json.load(open(f"{self.out}/{lv}/parts.json", encoding="utf-8"))["segments"]
            for sid, text in segs.items():
                from html import escape
                self.assertIn(f"<div class='script'>{escape(text)}</div>", stripped, (lv, sid))      # 装飾を剥がすと従来の台本文字列と完全一致

    def test_legend_and_css_present_once_and_no_forbidden_words(self):
        page = _page(self.ctx)
        self.assertEqual(page.count('class="lk-legend"'), 1)
        self.assertEqual(page.count(hl.HIGHLIGHT_CSS), 1)
        body = page[page.index("<body>"):]
        for bad in ("英語:", "日本語:", "EN:", "JA:", "(A2)"):
            self.assertNotIn(bad, body)
        self.assertNotIn("title=", " ".join(re.findall(r"<(?:strong|span) class=\"lk[123]\"[^>]*>", page)))       # ③含め装飾にtitle属性なし

    def test_public_page_has_no_chunk_marker_and_standard_check_passes(self):
        page = _page(self.ctx)
        self.assertEqual(cp.count_chunk_markers(page), 0)
        self.assertEqual(r.evaluate_page_verify(page, f"{self.out}/pages", expect_notice=True), [])

    def test_voice_notice_and_audience_marker_behaviour_unchanged(self):
        page = _page(self.ctx)
        self.assertEqual(page.count(ya.ys.PAGE_NOTICE_CLASS), 1)               # Voice説明文は1回・本文外
        self.assertLess(page.index(ya.ys.PAGE_NOTICE_CLASS), page.index("<table"))
        self.assertIn('name="robots" content="noindex', page)

    def test_validator_part1_must_be_exactly_one_in_vocab_levels(self):
        idx = f"{self.out}/pages/index.html"
        orig = open(idx, encoding="utf-8").read()
        try:
            self.assertEqual(r._verify_part2_outputs(self.ctx)["a2"]["part1_blocks"], 1)
            for lv in r.LEVELS:
                head = f"<h2 id='{r.PAGE_SECTION_IDS[lv]}'>"
                sec = _sec(orig, lv)
                # 0個(Std/Adv)
                zero = orig.replace(sec, sec.replace(r.PART1_MARKER, "Vocabulary and Expressions"))
                open(idx, "w", encoding="utf-8").write(zero)
                with self.assertRaises(r.YE2EStop) as e:
                    r._verify_part2_outputs(self.ctx)
                self.assertIn("FAMILY_Y_PART1_OUTPUT_MISMATCH", str(e.exception))
                self.assertIn("0個", str(e.exception))
                # 2個
                two = orig.replace(sec, sec.replace(r.PART1_MARKER, r.PART1_MARKER + " " + r.PART1_MARKER))
                open(idx, "w", encoding="utf-8").write(two)
                with self.assertRaises(r.YE2EStop) as e:
                    r._verify_part2_outputs(self.ctx)
                self.assertIn("2個", str(e.exception))
                self.assertTrue(head in orig)
        finally:
            open(idx, "w", encoding="utf-8").write(orig)
        r._verify_part2_outputs(self.ctx)

    def test_g3_detects_missing_extra_and_wrong_kind_decoration(self):
        page = _page(self.ctx)
        sec = _sec(page, "a2")
        first = re.search(r'<strong class="lk1" data-hl="([^"]+)">([^<]*)</strong>', sec)
        self.assertIsNotNone(first)
        # 欠落(装飾を1つ剥がす)
        bad = page.replace(sec, sec.replace(first.group(0), first.group(2), 1))
        with self.assertRaises(r.YE2EStop) as e:
            r._verify_highlights_on_page(self.ctx, bad)
        self.assertIn("G3HL_MISSING", str(e.exception))
        # 区分違い(lk1→lk2)
        bad = page.replace(sec, sec.replace('class="lk1" data-hl="%s"' % first.group(1), 'class="lk2" data-hl="%s"' % first.group(1), 1))
        with self.assertRaises(r.YE2EStop) as e:
            r._verify_highlights_on_page(self.ctx, bad)
        self.assertIn("G3HL_WRONG_KIND", str(e.exception))
        # 余剰(期待に無いcandidate_id)
        bad = page.replace(sec, sec + '<strong class="lk2" data-hl="p_unknown">x</strong>')
        with self.assertRaises(r.YE2EStop) as e:
            r._verify_highlights_on_page(self.ctx, bad)
        self.assertIn("G3HL_EXTRA", str(e.exception))
        # public混入(⏸)
        bad = page.replace(sec, sec + cp._CHUNK_MARKER_HTML)
        with self.assertRaises(r.YE2EStop) as e:
            r._verify_highlights_on_page(self.ctx, bad)
        self.assertIn("G3HL_PUBLIC_MARKER", str(e.exception))
        # 正常は通る
        self.assertEqual(r._verify_highlights_on_page(self.ctx, page)["a2"]["status"], "PASS")

    def test_issue_stops_before_page_generation_with_cause_code(self):
        idx = f"{self.out}/pages/index.html"
        before = open(idx, "rb").read()
        issue = {"status": "ISSUE", "highlights": [], "meanings": [], "notices": [], "stats": {},
                 "issues": [{"code": "HL_SENTENCE_NOT_IN_DISPLAY", "candidate_id": "p_x", "detail": "テスト"}]}
        with mock.patch.object(ya, "resolve_y_highlights", lambda out, lv: dict(issue, level=lv)):
            with self.assertRaises(r.YE2EStop) as e:
                with _quiet():
                    r.stage_pages(self.ctx)
        msg = str(e.exception)
        self.assertIn("FAMILY_Y_HIGHLIGHT_ISSUE", msg)
        self.assertIn("HL_SENTENCE_NOT_IN_DISPLAY", msg)
        self.assertEqual(open(idx, "rb").read(), before)                          # ページを書き換えない(生成前STOP)
        self.assertTrue(os.path.exists(f"{self.out}/audit/highlight_resolution_a2.json"))      # 原因を記録

    def test_issue_stops_before_paid_tts_with_zero_api_calls(self):
        """TTS費用前の事前STOP: display_spec付きlevelで解決がISSUEなら、有料TTS(stage_tts)の入口でAPI 0のままSTOPする。"""
        issue = {"status": "ISSUE", "highlights": [], "meanings": [], "notices": [], "stats": {},
                 "issues": [{"code": "HL_TEXT_SHA_MISMATCH", "candidate_id": None, "detail": "テスト"}]}
        n0 = base._calls(self.ctx)
        with mock.patch.object(ya, "resolve_y_highlights", lambda out, lv: dict(issue, level=lv)):
            for lv in r.LEVELS:
                with self.assertRaises(r.YE2EStop) as e:
                    with _quiet():
                        r.stage_tts(self.ctx, lv)
                self.assertIn("FAMILY_Y_HIGHLIGHT_ISSUE", str(e.exception))
                self.assertIn(f"tts_{lv}", str(e.exception))
                self.assertIn("HL_TEXT_SHA_MISMATCH", str(e.exception))
        self.assertEqual(base._calls(self.ctx), n0)

    def test_display_units_match_parts_json_segments_in_publication_order(self):
        for lv in r.LEVELS:
            parts = json.load(open(f"{self.out}/{lv}/parts.json", encoding="utf-8"))
            units = ya.y_highlight_display_units(self.out, lv)
            self.assertEqual([u["key"] for u in units], [s for s in parts["y_segment_order"] if s in parts["segments"]])
            for u in units:
                self.assertEqual(u["texts"], [parts["segments"][u["key"]]])
            self.assertEqual(hashlib.sha256(ya.y_highlight_article_text(self.out, lv).encode("utf-8")).hexdigest(),
                             json.load(open(f"{self.out}/key_phrases/{lv}/kp_candidates.json", encoding="utf-8"))["text_sha256"])     # 候補生成に使った本文とsha一致(M1)

    def test_meaning_list_for_category3_sits_outside_table_and_script_and_passes_g3(self):
        """③(下線のみ+下の一覧)を含む状況: 確定itemsに③を1件足した解決結果で、訳リストがlevel節のtable/div.scriptの外(台本表の直後・Part 1の前)に出てG3を通る。"""
        cands = json.load(open(f"{self.out}/key_phrases/a2/kp_candidates.json", encoding="utf-8"))
        chosen = {c["candidate_id"] for c in hl.items_from_record(__import__("er128_kp_confirmed_content_01").load_record(f"{self.out}/key_phrases/a2"))}
        extra = [c for c in cands["candidates"] if c["candidate_id"] not in chosen][0]
        real_items = hl.items_from_record

        def with_c3(rec):
            return real_items(rec) + [{"candidate_id": extra["candidate_id"], "category": 3, "used_form": extra["used_form"], "japanese_gloss": "テスト訳"}]
        with mock.patch.object(hl, "items_from_record", with_c3):
            with _quiet():
                r.stage_pages(self.ctx)
            page = _page(self.ctx)
            sec = _sec(page, "a2")
            self.assertEqual(sec.count('class="lk-meaning"'), 1)
            self.assertIn(f"{extra['used_form']} ＝ テスト訳", sec)
            i_ul = sec.index('<ul class="lk-meaning">')
            self.assertGreater(i_ul, sec.rindex("</table>", 0, i_ul))              # 台本表(table)の外・直後
            self.assertLess(i_ul, sec.index(r.PART1_MARKER))                       # Part 1の前
            self.assertEqual(sec.count('class="lk3"'), 1)
            self.assertEqual(r.evaluate_page_verify(page, f"{self.out}/pages", expect_notice=True), [])
            self.assertEqual(r._verify_highlights_on_page(self.ctx, page)["a2"]["status"], "PASS")
        with _quiet():
            r.stage_pages(self.ctx)                                                 # 元の状態へ戻す

    def test_dev_markers_coexist_outside_highlights_and_public_stays_zero(self):
        saved = {}
        for lv in r.LEVELS:
            pp = f"{self.out}/{lv}/audit/chunk_plan_{lv}.json"
            saved[pp] = open(pp, encoding="utf-8").read() if os.path.exists(pp) else None
            doc = json.loads(saved[pp]) if saved[pp] else {"plans": {}}
            text = json.load(open(f"{self.out}/{lv}/parts.json", encoding="utf-8"))["segments"]["y_voice_1"]
            # y_voice_1 は『a small fee』『pick it up』等を含む。ハイライト内部を跨ぐ位置(語句の途中の空白)で2 chunkに分ける
            hl_start = None
            for h in json.load(open(f"{self.out}/audit/highlight_resolution_{lv}.json", encoding="utf-8"))["highlights"]:
                if "y_voice_1" in h["units"] and " " in h["surface"]:
                    hl_start = text.find(h["surface"])
                    cut = hl_start + h["surface"].index(" ") + 1
                    break
            if hl_start is None:
                cut = text.rfind(" ", 0, len(text) // 2)
            doc.setdefault("plans", {})["y_voice_1"] = {"parent_id": "y_voice_1", "chunked": True,
                                                         "chunks": [{"chunk_id": "y_voice_1_k1", "index": 1, "text": text[:cut].strip(), "boundary_kind": "paragraph"},
                                                                    {"chunk_id": "y_voice_1_k2", "index": 2, "text": text[cut:].strip(), "boundary_kind": "paragraph"}]}
            json.dump(doc, open(pp, "w", encoding="utf-8"), ensure_ascii=False)
        pub_before = _page(self.ctx)
        self.ctx.page_audience = "dev"
        try:
            with _quiet():
                r.stage_pages(self.ctx)
            dev = _page(self.ctx, "index_dev.html")
            self.assertEqual(cp.count_boundary_marker_spans(dev), 2)                # 実plan境界(各level1)
            self.assertEqual(len(re.findall(r'<(?:strong|span) class="lk[123]"[^>]*>[^<]*(?:⏸|chunk-mark)[^<]*</(?:strong|span)>', dev)), 0)      # ⏸は装飾の外
            for lv in r.LEVELS:                                                      # devでも装飾は各候補ちょうど1出現(片に分かれても同一data-hl)
                self.assertEqual(len(set(_hl_ids(_sec(dev, lv)))), 5)
            self.assertEqual(_page(self.ctx), pub_before)                            # 公開用は上書きされない
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
        self.assertEqual(cp.count_chunk_markers(_page(self.ctx)), 0)


@legacy_unmarked_class
class UnmarkedPipeline(unittest.TestCase):
    """マーク無し(display_spec無し)=従来とバイト同一の挙動: ハイライト・凡例・CSS・訳リスト・Std Part 1が一切出ない(遡及なし)。"""

    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="y_hl_unmarked_")
        cls.ctx = _run(cls.root, marked=False)
        cls.out = cls.ctx.out_dir

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_no_decoration_no_css_no_legend_and_std_has_no_part1(self):
        page = _page(self.ctx)
        for tok in ("data-hl", "lk1", "lk2", "lk3", "lk-meaning", "lk-legend", hl.HIGHLIGHT_CSS):
            self.assertNotIn(tok, page, tok)
        self.assertEqual(_sec(page, "a2").count(r.PART1_MARKER), 0)
        self.assertEqual(_sec(page, "b1b").count(r.PART1_MARKER), 1)               # Advは従来どおり常にPart 1
        self.assertFalse(r._part1_level_enabled(self.ctx, "a2"))
        self.assertTrue(r._part1_level_enabled(self.ctx, "b1b"))
        v = json.load(open(f"{self.out}/page_verify_local.json", encoding="utf-8"))
        self.assertEqual(v["highlight_verified"], {"a2": {"status": "NOT_MARKED"}, "b1b": {"status": "NOT_MARKED"}})
        self.assertFalse(os.path.exists(f"{self.out}/audit/highlight_resolution_a2.json"))
        self.assertIsNone(r._prov(self.ctx).stage_entry(r.PART1_STAGES["a2"]["gen"]))     # Std Part 1は生成されない(API 0・費用0)

    def test_resolve_returns_none_without_display_spec(self):
        for lv in r.LEVELS:
            self.assertIsNone(ya.resolve_y_highlights(self.out, lv))

    def test_std_part1_block_in_unmarked_std_is_rejected_by_validator(self):
        idx = f"{self.out}/pages/index.html"
        orig = open(idx, encoding="utf-8").read()
        sec = _sec(orig, "a2")
        try:
            open(idx, "w", encoding="utf-8").write(orig.replace(sec, sec + "<h3>" + r.PART1_MARKER + "</h3>"))
            with self.assertRaises(r.YE2EStop) as e:
                r._verify_part2_outputs(self.ctx)
            self.assertIn("FAMILY_Y_PART1_OUTPUT_MISMATCH(a2)", str(e.exception))
        finally:
            open(idx, "w", encoding="utf-8").write(orig)

    def test_unmarked_page_with_decoration_is_rejected_by_g3(self):
        page = _page(self.ctx)
        sec = _sec(page, "a2")
        with self.assertRaises(r.YE2EStop) as e:
            r._verify_highlights_on_page(self.ctx, page.replace(sec, sec + '<strong class="lk1" data-hl="p_x">x</strong>'))
        self.assertIn("FAMILY_Y_HIGHLIGHT_UNEXPECTED", str(e.exception))


class GoldenAndRenderDefaults(unittest.TestCase):
    def test_golden_existing_run_without_mark_pages_html_byte_identical(self):
        """既存run(run_style_fix_01・マーク無し)の build_page_rows+render_y_page 出力が配線変更前(fixture記録のsha256)とバイト同一(public/dev)。"""
        if not os.path.exists(GOLDEN):
            self.skipTest("golden fixtureなし")
        want = json.load(open(GOLDEN, encoding="utf-8"))
        run = os.path.join(ROOT, want["run"])
        if not os.path.isdir(run):
            self.skipTest("既存run dirなし")
        sys.path.insert(0, os.path.join(ROOT, "docs", "research", "SLOT-23-CONSUMER-DESIGN-01", "tools"))
        import y_golden_capture_01 as gc
        got = gc.capture(run)
        for aud in ("public", "dev"):
            self.assertEqual(got[aud]["sha256"], want[aud]["sha256"], aud)
            self.assertEqual(got[aud]["len"], want[aud]["len"], aud)

    def test_render_y_page_default_has_no_highlight_artifacts_and_flag_adds_legend_and_css(self):
        lv = {"id": "standard", "label": "Standard", "full_src": "a.mp3", "duration": 3.0,
              "rows": [{"part": "Full Story: Lead (Narrator)", "start": 0.0, "dur": 1.0, "src": "a0.mp3", "blocks": [cp.script_block("One two three.")]}]}
        plain = ya.render_y_page("t", [lv], show_notice=False)
        self.assertNotIn("lk-legend", plain)
        self.assertNotIn(hl.HIGHLIGHT_CSS, plain)
        on = ya.render_y_page("t", [lv], show_notice=False, highlight=True)
        self.assertEqual(on.count("lk-legend"), 2)                                    # 凡例<p>のclass 1個 + CSS内の p.lk-legend 1個
        self.assertEqual(on.count(hl.HIGHLIGHT_CSS), 1)
        self.assertEqual(on.replace(hl.legend_html(), "").replace(f"<style>{hl.HIGHLIGHT_CSS}</style>", ""), plain)    # 差分は凡例とCSSだけ

    def test_script_block_default_unchanged_without_highlights(self):
        self.assertEqual(cp.script_block("A b."), "<div class='script'>A b.</div>")
        self.assertEqual(cp.script_block("A b.", None, "public", None, None), cp.script_block("A b."))


class NoLegacyAdvOnlyLiterals(unittest.TestCase):
    def test_part1_functions_have_no_hardcoded_level_literal_except_defaults(self):
        """Part 1系関数に 'b1b' / 'a2' のリテラル直書きが無い(既定引数はADV_LEVEL定数)。旧 PART1_STAGE/_part1_items_b1b/_assert_std_part2_ready は撤去済み。"""
        import ast
        src = open(os.path.join(ROOT, "er121_family_y_runner_01.py"), encoding="utf-8").read()
        tree = ast.parse(src)
        names = {"_part1_level_enabled", "_part1_items", "_part1_path", "_part1_ja_path", "_part1_cost_tag", "_require_part1_fresh", "_require_part1_ja_fresh",
                 "_assemble_study_rows", "_stage_kp_part1", "_stage_kp_part1_ja", "_assert_study_ready", "_assert_std_study_ready", "_part2_pool",
                 "_resolve_highlights_or_stop", "_verify_highlights_on_page"}
        found = set()
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in names]:
            found.add(fn.name)
            for c in ast.walk(fn):
                if isinstance(c, ast.Constant) and c.value in ("b1b", "a2"):
                    self.fail(f"{fn.name}にlevelリテラル {c.value!r} (line {c.lineno})")
        self.assertEqual(found, names)
        code_names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}      # コメント/文字列は対象外(コード上の識別子のみ)
        for old in ("PART1_STAGE", "PART1_JA_STAGE", "_part1_items_b1b", "_assert_std_part2_ready"):
            self.assertNotIn(old, code_names, old)


if __name__ == "__main__":
    unittest.main()
