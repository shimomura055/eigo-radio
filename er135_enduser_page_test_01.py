# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02B: er135_enduser_page_01.py のtest(API 0・音声/ASRはfake。同期の実体はmock)。

実行: .venv\\Scripts\\python.exe -m pytest er135_enduser_page_test_01.py -q
golden fixture=`er135_enduser_fixtures_01/`(現行builderの実dev HTML: X月reselect / Y再配達料fee_03 / Z走れメロスmelos_02 + OPEN-596閉じ無し引用行)。
中間データ(timeline・KP確定・承認済み日本語原稿)もfixtureに凍結済み。**mock同期(proportional)はコード経路検査用であり、実ASR同期の証拠ではない**。
"""
import copy
import hashlib
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import er135_enduser_dom_01 as D
import er135_enduser_page_01 as E
import er135_enduser_rules_01 as R

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "er135_enduser_fixtures_01"
MAN = json.load(open(FIX / "manifest_01.json", encoding="utf-8"))
ASSETS = ROOT / "enduser_page_assets"


def fx_html(name):
    return (FIX / MAN[name]["html"]).read_text(encoding="utf-8")


def mutate(html, old, new, count=1):
    assert html.count(old) >= 1, f"fixture mutate: '{old[:40]}' not found"
    return html.replace(old, new, count)


def sha_str(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class FakeAudio:
    """音声なしでprobe(sha/長さ)を返す。durはdev行の次のdata-tとの差(最後は+10秒)、mainはtotal。"""

    def __init__(self, rows_by_level, meta, root=None):
        self.dur, self.root = {}, root
        for lv, rows in rows_by_level.items():
            for i, r in enumerate(rows):
                nxt = rows[i + 1]["data_t"] if i + 1 < len(rows) else r["data_t"] + 10.0
                self.dur[r["audio_rel"]] = round(nxt - r["data_t"], 3)
            self.dur[meta["level_main"][lv]] = round(rows[-1]["data_t"] + 10.0, 3)
        self.override_sha = {}

    def __call__(self, rel):
        if rel not in self.dur:
            return None
        if rel in self.override_sha:
            return {"sha256": self.override_sha[rel], "duration": self.dur[rel]}
        if self.root is not None:
            p = Path(self.root) / rel
            if not p.is_file():
                return None
            return {"sha256": E.sha256_file(p), "duration": self.dur[rel]}
        return {"sha256": sha_str("fake:" + rel), "duration": self.dur[rel]}


def mock_sync(lv, rows, probe, with_kp=True, **over):
    """02A `enduser_sync_v1`と同形のmock(文字数比例・各行mp3内の秒=row_local_seconds)。コード経路検査用で、実ASR同期ではない。
    model/params/mp3_sha256/gate.statusは受け入れ検査を通すためのfixture値(02Aの実出力形式に合わせる)。"""
    out = []
    for r in rows:
        pr = probe(r["audio_rel"])
        if r["kind"] == "kp":
            if with_kp:
                out.append({"row_id": r["row_id"], "mp3_sha256": pr["sha256"], "sentences": [],
                            "kp_en": {"start": 1.42, "end": 2.55, "source": "silencedetect_block2", "blocks": 4, "token_match": 1.0}})
            continue
        if not r["sentences"]:
            continue
        tot = sum(max(1, len(s["text"])) for s in r["sentences"])
        t, ss = 0.0, []
        for s in r["sentences"]:
            d = pr["duration"] * 0.98 * max(1, len(s["text"])) / tot
            ss.append({"sid": s["sid"], "text": s["text"], "start": round(t, 3), "end": round(t + d - 0.01, 3)})
            t += d
        out.append({"row_id": r["row_id"], "mp3_sha256": pr["sha256"], "sentences": ss})
    j = {"schema": "enduser_sync_v1", "model": "medium",
         "params": {"engine": "faster-whisper", "device": "cpu", "compute_type": "int8", "beam_size": 5, "condition_on_previous_text": False,
                    "vad_filter": False, "word_timestamps": True, "time_base": "row_local_seconds"},
         "rows": out,
         "gate": {"status": "PASS", "token_match": {"min_row_ratio": 0.98}, "thresholds": {}, "warnings": []},
         "cost": {"api_calls": 0, "wall_s": 1.0, "asr_transcribed": 0, "cached_segments": 0, "model": "medium"}}
    j.update(over)
    return j


def kp_fake(rows_by_level):
    """compute_kp_audio相当の結果(syncにkp_enが無い場合のfallback。method付き)。"""
    return {r["row_id"]: {"start": 1.0, "end": 2.0, "method": E.KP_METHOD, "blocks": 4, "asr_text": r["kp_table"][0]["en"]}
            for rows in rows_by_level.values() for r in rows if r["kind"] == "kp"}


class Built:
    """fixtureからEnd Userデータまで(書込なし)を組み立てる。"""

    def __init__(self, name, html=None, ja_extra=None, use_ja=True, **kw):
        self.name = name
        cfg = MAN[name]
        self.family = cfg["family"]
        self.html = html if html is not None else fx_html(name)
        self.rows, self.study, self.meta = E.build_rows_from_dev_html(self.html, {"family": self.family, "dev_dir": None, "id": name})
        self.probe = FakeAudio(self.rows, self.meta)
        self.sync = {lv: mock_sync(lv, r, self.probe) for lv, r in self.rows.items()}
        self.ja = {}
        if use_ja and "ja_manuscript" in cfg:
            self.ja["x_manuscript"] = {"paragraphs": cfg["ja_manuscript"]["paragraphs_after_title"], "sha256": cfg["ja_manuscript"]["sha256"], "name": "revision2.md"}
        if use_ja and "y_segments" in cfg:
            self.ja["y_segments"] = cfg["y_segments"]["segments"]
        if ja_extra:
            self.ja.update(ja_extra)

    def data(self, **kw):
        return E.build_enduser_data(self.rows, self.sync, self.study, self.ja, self.meta, kp_audio=kp_fake(self.rows), probe=self.probe, **kw)


def stop_code(fn, *a, **k):
    try:
        fn(*a, **k)
    except E.EnduserPageStop as e:
        return e.code
    return None


# ============================================================
class T1_StructureContract(unittest.TestCase):
    """M1/T-ADP-1: X/Y/Zの現行builder出力をHTMLパーサで解析できる(構造契約)。中間データ(timeline/KP)と照合。"""

    def test_x_y_z_levels_rows_and_kinds(self):
        for name in ("x_moon", "y_fee03", "z_melos02"):
            b = Built(name)
            self.assertEqual(sorted(b.rows), ["adv", "std"], name)
            for lv, rows in b.rows.items():
                kinds = [r["kind"] for r in rows]
                self.assertTrue(set(kinds) <= {"sfx", "fixed", "topic", "jtitle", "preview", "kp", "comment", "story", "oneline"})
                self.assertIn("kp", kinds)
                self.assertGreaterEqual(kinds.count("story"), 3 if name != "y_fee03" else 8)
                self.assertEqual([r["idx"] if "idx" in r else i for i, r in enumerate(rows)], list(range(len(rows))))
                for r in rows:
                    if r["kind"] in R.TEXT_KINDS:
                        self.assertTrue(r["sentences"], f"{name} {lv} {r['label']}")
                    self.assertTrue(r["audio_rel"].endswith(".mp3"))

    def test_row_counts_and_start_times_match_timeline(self):
        for name in ("x_moon", "y_fee03", "z_melos02"):
            b = Built(name)
            for lv, sub in (("std", "std"), ("adv", "adv")):
                tl = MAN[name]["timeline"][lv]
                res = E.match_rows_to_timeline(lv, b.rows[lv], tl, strict_count=(name == "x_moon"))
                self.assertTrue(res["checked"])
                self.assertEqual(res["rows"], len(b.rows[lv]))

    def test_timeline_mismatch_is_stop(self):
        b = Built("x_moon")
        tl = copy.deepcopy(MAN["x_moon"]["timeline"]["adv"])
        tl[5]["start_seconds"] += 0.5
        self.assertEqual(stop_code(E.match_rows_to_timeline, "adv", b.rows["adv"], tl, True), "ENDUSER_TIMELINE_MISMATCH")
        self.assertEqual(stop_code(E.match_rows_to_timeline, "adv", b.rows["adv"], tl[:-1], True), "ENDUSER_TIMELINE_MISMATCH")

    def test_kp_match_intermediate_confirmed_selection(self):
        def norm(s):
            return [("*" if t in ("someone", "someone's", "your", "one's", "sb") else t) for t in E._kp_tokens(s)]
        for name in ("x_moon", "y_fee03", "z_melos02"):
            b = Built(name)
            for lv in ("std", "adv"):
                dev = [k["en"] for r in b.rows[lv] if r["kind"] == "kp" for k in r["kp_table"]]
                want = MAN[name]["kp"][lv]
                self.assertEqual([norm(x) for x in dev], [norm(x) for x in want], f"{name} {lv}")

    def test_titles_topic_and_family(self):
        b = Built("x_moon")
        self.assertTrue(b.meta["title_ja"].startswith("月のしわ"))
        self.assertTrue(b.meta["topic_en"].startswith("More Than 8,900 Wrinkles"))
        self.assertEqual(b.meta["family"], "X")
        self.assertEqual(Built("z_melos02").meta["title_ja"], "走れメロス")

    def test_y_levels_normalized_from_standard_advanced_ids(self):
        b = Built("y_fee03")
        self.assertEqual(sorted(b.meta["level_main"]), ["adv", "std"])

    def test_unknown_row_label_is_stop(self):
        h = mutate(fx_html("x_moon"), "<b>Full Story Part 1</b>", "<b>Mystery Part 1</b>")
        self.assertEqual(stop_code(E.build_rows_from_dev_html, h, {"family": "x", "dev_dir": None}), "ENDUSER_UNKNOWN_ROW_LABEL")
        h = mutate(fx_html("y_fee03"), "<b>Full Story: Voice 1</b>", "<b>Full Story: Voice A</b>")
        self.assertEqual(stop_code(E.build_rows_from_dev_html, h, {"family": "y", "dev_dir": None}), "ENDUSER_UNKNOWN_ROW_LABEL")

    def test_unknown_cell_content_and_markup_and_study_heading_are_stop(self):
        h = mutate(fx_html("x_moon"), "<td><div class='script'>As you listen", "<td><p>stray</p><div class='script'>As you listen")
        self.assertEqual(stop_code(E.build_rows_from_dev_html, h, {"family": "x", "dev_dir": None}), "ENDUSER_UNKNOWN_CELL_CONTENT")
        h = mutate(fx_html("x_moon"), "<div class='script'>As you listen", "<div class='script'><u>As</u> you listen")
        self.assertEqual(stop_code(E.build_rows_from_dev_html, h, {"family": "x", "dev_dir": None}), "ENDUSER_UNKNOWN_MARKUP")
        h = mutate(fx_html("x_moon"), "<h3>Grammar &amp; Sentence Structure</h3>", "<h3>Mystery corner</h3>")
        self.assertEqual(stop_code(E.build_rows_from_dev_html, h, {"family": "x", "dev_dir": None}), "ENDUSER_UNKNOWN_STUDY_HEADING")
        h = mutate(fx_html("x_moon"), "<section class='study'><h3>Vocabulary &amp; Expressions</h3>", "<section class='study'><h3>Vocabulary &amp; Expressions</h3></section><section class='study'><h3>Vocabulary &amp; Expressions</h3>")
        self.assertIn(stop_code(E.build_rows_from_dev_html, h, {"family": "x", "dev_dir": None}), ("ENDUSER_EMPTY_STUDY_SECTION", "ENDUSER_DEV_HTML_STRUCTURE"))


class T2_SentenceSplit(unittest.TestCase):
    """T-ADP-2: 文分割(引用符閉じ・略語・小文字継続・日本語・Z複数div・OPEN-596閉じ無し引用)。本文連結==dev行テキスト。"""

    def split(self, inner, n_div=1):
        root = D.parse_html("".join(f"<div class='script'>{x}</div>" for x in (inner if isinstance(inner, list) else [inner])))
        paras, n = D.paragraphs_of_divs(root.find_all("div"), 0, "t")
        return paras

    def texts(self, paras):
        return [[s["text"] for s in p] for p in paras]

    def test_quotes_abbreviation_lowercase_continuation(self):
        p = self.split("He said, “Go home.” She left. Mr. Smith arrived at 5 p.m. and sat. “Wait,” he said.")
        t = [s for pa in self.texts(p) for s in pa]
        self.assertEqual(t[0], "He said, “Go home.”")
        self.assertIn("Mr. Smith arrived at 5 p.m. and sat.", t)
        self.assertEqual(t[-1], "“Wait,” he said.")
        p = self.split('He said "go." then left. Next.')
        self.assertEqual(self.texts(p), [['He said "go." then left.', "Next."]])

    def test_japanese_sentences(self):
        p = self.split("月が縮みました。次はどうなるのか？答えは明日です！")
        self.assertEqual(self.texts(p), [["月が縮みました。", "次はどうなるのか？", "答えは明日です！"]])

    def test_paragraphs_from_blank_lines_and_chunk_mark_removed(self):
        p = self.split("One two. <span class='chunk-mark'>&#9208;</span>\n\nThree four.")
        self.assertEqual(self.texts(p), [["One two."], ["Three four."]])
        self.assertNotIn("\u23f8", json.dumps(p, ensure_ascii=False))

    def test_z_multiple_divs_are_not_merged(self):
        divs = ["Melos called across the hall,", "&quot;You kill men from fear. You never give them a chance to speak.&quot;", "Melos said."]
        p = self.split(divs)
        self.assertEqual(len(p), 3)
        self.assertEqual(self.texts(p)[0], ["Melos called across the hall,"])
        self.assertEqual(self.texts(p)[1], ['"You kill men from fear.', 'You never give them a chance to speak."'])
        for pa in p:
            for s in pa:
                self.assertTrue(s["sid"].startswith("t-s"))

    def test_inline_lk_spans_kept_and_not_split_into_empty_spans(self):
        p = self.split('The <span class="lk3" data-hl="p_1">radius</span>. Next <strong class="lk1" data-hl="p_2">one</strong>.')
        t = [s["html"] for pa in p for s in pa]
        self.assertEqual(t, ['The <span class="lk3" data-hl="p_1">radius</span>.', 'Next <strong class="lk1" data-hl="p_2">one</strong>.'])
        for h in t:
            self.assertEqual(len(D.lk_spans(h)), 1)

    def test_open596_unclosed_quote_rows_from_real_text(self):
        b = Built("z_open596_min", use_ja=False)
        rows = b.rows["std"]
        part = [r for r in rows if r["kind"] == "story"][0]
        self.assertGreaterEqual(len(part["paragraphs"]), 3)
        unclosed = [pa for pa in part["paragraphs"] if "".join(s["text"] for s in pa).count('"') % 2 == 1]
        self.assertTrue(unclosed, "閉じ無し引用符の行(OPEN-596)がfixtureに無い")
        # 本文連結==dev行テキスト(空白除去)・div境界をまたぐ文なし(各div=独立したparagraph群)
        self.assertEqual(E._ws("".join(s["text"] for pa in part["paragraphs"] for s in pa)), part["_ref_text"])
        n_div = MAN["z_open596_min"] and len(D.parse_html(b.html).find_all("div", cls="script")) - 2   # Topic/Japanese titleを除く
        self.assertGreaterEqual(len(part["paragraphs"]), n_div)
        d = b.data()
        self.assertIsNotNone(d)


class T3_DevOnlyRemoval(unittest.TestCase):
    """T-ADP-3: 開発者向け専用要素(⏸・LR赤・Fallback青・注記・TTS badge・制作情報・PWW)がEnd Userに出ない。本文テキストは不変。"""

    def test_marks_removed_text_unchanged(self):
        h = fx_html("x_moon")
        h = mutate(h, "<div class='script'>As you listen, notice how the team studied the Moon’s surface.</div>",
                   "<div class='script'>As you listen, notice how the team <span class='rpt-lr' style='color:#c00000;font-weight:700;text-decoration:underline'>studied</span> the Moon’s <span class='rpt-fb' style='color:#0a2a6b'>surface</span>. <span class='chunk-mark'>&#9208;</span></div><div class='rpt-notes'><div class='rpt-note rpt-note-lr'><b>Local Rewrite 適用</b> 変更前: x</div></div>")
        b = Built("x_moon", html=h)
        art, sp, bi = b.data()
        comment = [p for p in art["levels"]["adv"]["parts"] if p["label"] == "Comment 1"][0]
        self.assertEqual(" ".join(s["text"] for pa in comment["paragraphs"] for s in pa), "As you listen, notice how the team studied the Moon’s surface.")
        blob = json.dumps(art, ensure_ascii=False)
        for w in ("rpt-", "chunk-mark", "\u23f8", "Local Rewrite", "制作情報", "PASS_WITH_WARNING"):
            self.assertNotIn(w, blob)

    def test_y_tts_badge_and_z_aux_not_in_output(self):
        for name in ("y_fee03", "z_melos02"):
            art, sp, bi = Built(name).data()
            blob = json.dumps(art, ensure_ascii=False)
            for w in ("TTS 1回", "ASR警告", "制作情報", "補助情報", "詳細確認ページ", "preview_segments"):
                self.assertNotIn(w, blob, name)

    def test_x_pww_and_aux_not_parsed_as_levels(self):
        b = Built("x_moon")
        self.assertEqual(sorted(b.rows), ["adv", "std"])


class T4_EmphasisAndGlossary(unittest.TestCase):
    """T-ADP-4/5: 下線・太字対象の保持、glossary(display_spec付き=assert全通過 / 無し=生成なし+記録)。"""

    def test_lk_spans_preserved_equal_dev(self):
        b = Built("x_moon")
        art, sp, bi = b.data()
        for lv in ("std", "adv"):
            dev = sum(len(r["_ref_marks"]) for r in b.rows[lv] if "_ref_marks" in r)
            out = sum(len(D.lk_spans(s["html"])) for p in art["levels"][lv]["parts"] for pa in p.get("paragraphs", []) for s in pa)
            self.assertGreaterEqual(out, dev)
            self.assertGreater(out, 0)

    def test_glossary_applied_for_display_spec_levels(self):
        art, sp, bi = Built("x_moon").data()
        self.assertEqual(bi["glossary"], {"std": "applied", "adv": "applied"})
        for lv in ("std", "adv"):
            L = art["levels"][lv]
            glos = [g["en"] for p in L["parts"] for g in p.get("glossary", [])]
            self.assertEqual(len(glos), len(set(glos)))
            for p in L["parts"]:
                if p["kind"] == "kp":
                    for k in p["kp"]:
                        self.assertIn(k["en"], glos)
            for v in L["vocab"]:
                self.assertIn(v["heading"], glos)

    def test_glossary_not_applicable_without_display_spec_is_recorded(self):
        for name in ("y_fee03", "z_melos02"):
            art, sp, bi = Built(name).data()
            self.assertEqual(set(bi["glossary"].values()), {"not_applicable_no_display_spec"})
            self.assertFalse(any("glossary" in p for L in art["levels"].values() for p in L["parts"]))

    def test_level_level_meaning_list_is_pooled(self):
        """Y(highlight_meaning_html)は③本文中の意味一覧を行の外(level節の台本表の直後)に置く。行内一覧と同じ結果(glossary全通過)になること。"""
        h = fx_html("x_moon")
        ul = "<ul class=\"lk-meaning\"><li>radius ＝ 中心から外側までの長さ</li></ul>"
        self.assertEqual(h.count(ul), 1)
        i = h.index(ul)
        j = h.index("</tbody></table>", i) + len("</tbody></table>")
        moved = h[:i] + h[i + len(ul):j] + ul + h[j:]
        self.assertNotEqual(moved, h)
        art0, _s0, bi0 = Built("x_moon").data()
        art1, _s1, bi1 = Built("x_moon", html=moved).data()
        self.assertEqual(bi1["glossary"], bi0["glossary"])
        g0 = [g for L in art0["levels"].values() for p in L["parts"] for g in p.get("glossary", [])]
        g1 = [g for L in art1["levels"].values() for p in L["parts"] for g in p.get("glossary", [])]
        self.assertEqual(sorted(x["en"] for x in g0), sorted(x["en"] for x in g1))
        # 余分な項目(下線に対応しない)をpoolに足すとSTOP(黙って捨てない)
        extra = moved.replace(ul, ul.replace("</ul>", "<li>zzzunused ＝ 余分</li></ul>"))
        self.assertEqual(stop_code(Built("x_moon", html=extra).data), "ENDUSER_GLOSSARY_ASSERT")

    def test_glossary_assert_violations_are_stop(self):
        # (a) 本文中の意味一覧(ul.lk-meaning)の項目が欠けた
        h = mutate(fx_html("x_moon"), "<ul class=\"lk-meaning\"><li>radius ＝ 中心から外側までの長さ</li></ul>", "<ul class=\"lk-meaning\"></ul>")
        self.assertEqual(stop_code(Built("x_moon", html=h).data), "ENDUSER_GLOSSARY_ASSERT")
        # (b) Vocabulary項目が一覧に載らない(Vocabの本文の英文を壊す)
        h = mutate(fx_html("x_moon"), "<dt>本文の英文</dt><dd>The cliffs are a record of a huge \"shoving match\" cut into the Moon's surface", "<dt>本文の英文</dt><dd>ZZZ")
        self.assertEqual(stop_code(Built("x_moon", html=h).data), "ENDUSER_GLOSSARY_ASSERT")


class T5_KpEnglishAudio(unittest.TestCase):
    """T-ADP-6: KP英語区間(4ブロック/5ブロック(Z Adv KP2相当)/3ブロック=STOP/ASR不一致=STOP)。ffmpeg/ASRはfake。"""

    def setUp(self):
        self.b = Built("x_moon")
        self.rows = {"adv": [r for r in self.b.rows["adv"] if r["kind"] == "kp"][:1]}
        for r in self.rows["adv"]:
            r["audio_rel"] = r["audio_rel"]

    def run_kp(self, blocks, heard=None):
        kp = self.rows["adv"][0]["kp_table"][0]["en"]
        return E.compute_kp_audio(self.rows, ".", asr=lambda p, s, e: heard if heard is not None else kp, blocks_fn=lambda p: blocks)

    def test_four_blocks_second_is_english(self):
        r = self.run_kp([(0.0, 0.5), (1.5, 2.4), (3.0, 5.0), (6.0, 7.0)])
        v = list(r.values())[0]
        self.assertEqual((v["start"], v["end"], v["blocks"]), (1.42, 2.55, 4))

    def test_five_blocks_ok(self):
        r = self.run_kp([(0.0, 0.5), (1.5, 2.4), (3.0, 4.0), (4.5, 5.5), (6.0, 7.0)])
        self.assertEqual(list(r.values())[0]["blocks"], 5)

    def test_three_blocks_is_stop(self):
        self.assertEqual(stop_code(self.run_kp, [(0.0, 0.5), (1.5, 2.4), (3.0, 5.0)]), "ENDUSER_KP_BLOCKS")

    def test_asr_mismatch_is_stop(self):
        self.assertEqual(stop_code(self.run_kp, [(0.0, 0.5), (1.5, 2.4), (3.0, 5.0), (6.0, 7.0)], "completely different words"), "ENDUSER_KP_ASR_MISMATCH")

    def test_asr_match_tolerates_placeholders_and_case(self):
        self.assertTrue(E.kp_asr_matches("pull someone under", "Pull him under."))
        self.assertTrue(E.kp_asr_matches("in someone's place", "In someone's place"))
        self.assertFalse(E.kp_asr_matches("seize", "abandon"))

    def test_missing_kp_audio_is_stop(self):
        b = Built("x_moon")
        b.sync = {lv: mock_sync(lv, r, b.probe, with_kp=False) for lv, r in b.rows.items()}      # syncにkp_enが無く、compute_kp_audio結果も無い
        self.assertEqual(stop_code(E.build_enduser_data, b.rows, b.sync, b.study, b.ja, b.meta, kp_audio={}, probe=b.probe), "ENDUSER_KP_AUDIO_MISSING")


class T6_Translation(unittest.TestCase):
    """T-TR-1/2: 承認済み訳のみ。X段落割当(不一致=STOP)、Y details.ja(承認済み原稿と一致)、Z訳なし、英語Comment/In One Line等は訳なし(非表示)。"""

    def test_x_translation_assigned_and_only_approved_source(self):
        art, sp, bi = Built("x_moon").data()
        for lv in ("std", "adv"):
            for p in art["levels"][lv]["parts"]:
                if p["kind"] == "story":
                    self.assertEqual(p["ja_source"], "approved_ja_manuscript")
                    self.assertEqual(len(p["ja"]), len(p["paragraphs"]))
                else:
                    self.assertNotIn("ja", p)
                    self.assertNotIn("ja_source", p)
        cov = bi["translation_coverage"]["adv"]
        self.assertEqual(cov["story"], {"blocks": 3, "translated": 3, "source": "approved_ja_manuscript"})
        self.assertEqual(cov["comment"]["translated"], 0)
        self.assertEqual(cov["comment"]["source"], "none_approved_translation_hidden")
        self.assertEqual(bi["ja_manuscript"]["sha256"], MAN["x_moon"]["ja_manuscript"]["sha256"])

    def test_x_paragraph_mismatch_is_stop(self):
        b = Built("x_moon")
        b.ja["x_manuscript"]["paragraphs"] = b.ja["x_manuscript"]["paragraphs"][:-1]
        self.assertEqual(stop_code(b.data), "ENDUSER_JA_PARAGRAPH_MISMATCH")

    def test_x_without_manuscript_hides_translations(self):
        art, sp, bi = Built("x_moon", use_ja=False).data()
        self.assertFalse(any("ja" in p for L in art["levels"].values() for p in L["parts"]))
        self.assertIsNone(bi["ja_manuscript"])
        self.assertEqual(bi["translation_coverage"]["adv"]["story"]["translated"], 0)

    def test_y_ja_from_dev_page_matches_approved_article(self):
        art, sp, bi = Built("y_fee03").data()
        for lv in ("std", "adv"):
            stories = [p for p in art["levels"][lv]["parts"] if p["kind"] == "story"]
            self.assertEqual(len(stories), 8)
            for p in stories:
                self.assertEqual(p["ja_source"], "approved_ja_original_in_dev_page")
                self.assertTrue(p["ja"])
        segs = MAN["y_fee03"]["y_segments"]["segments"]
        lead = [p for p in art["levels"]["adv"]["parts"] if p["label"] == "Full Story: Lead"][0]
        self.assertEqual(E._ws("".join(lead["ja"])), E._ws(segs["y_lead"]))
        for p in art["levels"]["adv"]["parts"]:
            if p["kind"] in ("comment", "preview", "topic"):
                self.assertNotIn("ja", p)

    def test_y_ja_differs_from_approved_article_is_stop(self):
        b = Built("y_fee03")
        b.ja["y_segments"] = dict(b.ja["y_segments"], y_voice_1="別の文章です。")
        self.assertEqual(stop_code(b.data), "ENDUSER_JA_MISMATCH")

    def test_z_has_no_translation_at_all(self):
        art, sp, bi = Built("z_melos02").data()
        self.assertFalse(any("ja" in p or "ja_source" in p for L in art["levels"].values() for p in L["parts"]))
        self.assertEqual(bi["translation_coverage"]["std"]["story"]["source"], "none_approved_translation_hidden")

    def test_ja_source_values_are_only_the_two_approved(self):
        for name in ("x_moon", "y_fee03", "z_melos02"):
            art, _, _ = Built(name).data()
            srcs = {p["ja_source"] for L in art["levels"].values() for p in L["parts"] if "ja_source" in p}
            self.assertTrue(srcs <= set(R.JA_SOURCES), srcs)

    def test_forbidden_translation_markers_rejected(self):
        b = Built("x_moon")
        art, sp, bi = b.data()
        bad = copy.deepcopy(art)
        p = [p for p in bad["levels"]["adv"]["parts"] if p["kind"] == "comment"][0]
        p["ja"], p["ja_source"] = ["x"], "dev_translation_unapproved"
        self.assertEqual(stop_code(E.validate_output, bad, sp, bi, b.rows, b.study, b.meta, probe=b.probe), "ENDUSER_SCHEMA")


class T7_LearningCorners(unittest.TestCase):
    """T-LEARN: 文法/ニュアンスの採用・0件。0件はキーが空=見出し・空枠なし(UI側はverify CLIで確認)。ニュアンスは最大1。"""

    NUANCE = ("<section class='study'><h3>ニュアンス解説</h3><div class='study-item'><h4>keep heat in</h4><dl><dt>ポイント</dt><dd>熱を逃がさない</dd>"
              "<dt>解説</dt><dd><p>説明<b>keep</b>です。</p></dd><dt>本文の英文</dt><dd>It keeps heat in.</dd><dt>日本語訳</dt><dd>熱を保つ。</dd></dl></div></section>")

    def with_nuance(self, html, level_marker):
        """adv levelの最後のsection.studyの直後へニュアンスを足す。"""
        i = html.rindex("</section>", 0, html.index("<details class='aux'>", html.index("<h2 id='adv'>")))
        return html[: i + len("</section>")] + self.NUANCE + html[i + len("</section>"):]

    def test_no_nuance_or_grammar_means_empty_keys(self):
        art, _, _ = Built("y_fee03").data()
        std = art["levels"]["std"]
        self.assertEqual((std["vocab"], std["grammar"], std["nuance"]), ([], [], []))
        art, _, _ = Built("z_melos02").data()
        self.assertEqual(art["levels"]["adv"]["nuance"], [])

    def test_adopted_nuance_appears_only_for_that_level(self):
        h = self.with_nuance(fx_html("x_moon"), "adv")
        b = Built("x_moon", html=h)
        art, _, _ = b.data()
        self.assertEqual(len(art["levels"]["adv"]["nuance"]), 1)
        self.assertEqual(art["levels"]["adv"]["nuance"][0]["heading"], "keep heat in")
        self.assertEqual(art["levels"]["std"]["nuance"], [])
        self.assertEqual([f["label"] for f in art["levels"]["adv"]["nuance"][0]["fields"]], ["ポイント", "解説", "本文の英文", "日本語訳"])

    def test_two_nuance_sections_is_stop(self):
        h = self.with_nuance(self.with_nuance(fx_html("x_moon"), "adv"), "adv")
        self.assertEqual(stop_code(E.build_rows_from_dev_html, h, {"family": "x", "dev_dir": None}), "ENDUSER_DEV_HTML_STRUCTURE")

    def test_grammar_selected_vs_zero(self):
        art, _, _ = Built("x_moon").data()
        self.assertEqual(len(art["levels"]["adv"]["grammar"]), 1)
        self.assertEqual(len(art["levels"]["std"]["grammar"]), 1)
        art, _, _ = Built("y_fee03").data()
        self.assertEqual(len(art["levels"]["adv"]["grammar"]), 1)
        self.assertEqual(art["levels"]["std"]["grammar"], [])

    def test_app_hides_empty_corners_statically(self):
        js = (ASSETS / R.ASSET_BUILD_ID / "app.js").read_text(encoding="utf-8")
        for key in ("L.vocab && L.vocab.length", "L.grammar && L.grammar.length", "L.nuance && L.nuance.length"):
            self.assertIn(key, js)

    def test_dd_markup_preserved_and_quote_dd_exists(self):
        art, _, _ = Built("x_moon").data()
        v = art["levels"]["adv"]["vocab"][0]
        labels = [f["label"] for f in v["fields"]]
        self.assertIn("本文の英文", labels)
        self.assertTrue(any("<b>" in f["html"] for f in v["fields"]))


class T8_Notice(unittest.TestCase):
    """T-NOTICE: Voice説明文(Y)。devにある<=>End Userにある、文言==承認済み定数。X/Zは出ない。"""

    def test_y_notice_present_and_equal_to_approved_constant(self):
        import er121_family_y_structure_01 as ys
        art, _, _ = Built("y_fee03").data()
        self.assertEqual(art["notice"], ys.PAGE_NOTICE_JA)

    def test_x_z_have_no_notice(self):
        for name in ("x_moon", "z_melos02"):
            self.assertIsNone(Built(name).data()[0]["notice"])

    def test_notice_text_altered_is_stop(self):
        h = mutate(fx_html("y_fee03"), "AIが編集・再構成したものです。", "AIが編集したものです。")
        self.assertEqual(stop_code(Built("y_fee03", html=h).data), "ENDUSER_NOTICE_MISMATCH")

    def test_notice_on_non_y_page_is_stop(self):
        h = mutate(fx_html("x_moon"), "<div class='note'><b>状態:", "<div class='note y-ai-notice'>Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。</div><div class='note'><b>状態:")
        self.assertEqual(stop_code(Built("x_moon", html=h).data), "ENDUSER_NOTICE_MISMATCH")


class T9_SyncAcceptance(unittest.TestCase):
    """受け入れ検査(同期の実体はmock。形式は02A `enduser_sync_v1` の実出力と同じ)。ASR由来(model/params/mp3 sha)・gate・coverage・範囲・単調・ダミー拒否・KP区間。"""

    def setUp(self):
        self.b = Built("x_moon")
        self.lv = "adv"
        self.rows = self.b.rows[self.lv]

    def mk(self, **over):
        return mock_sync(self.lv, self.rows, self.b.probe, **over)

    def check(self, **over):
        return stop_code(E.check_sync, self.lv, self.rows, self.mk(**over), self.b.probe)

    def test_valid_passes_and_times_are_converted_to_episode_seconds(self):
        self.assertIsNone(self.check())
        r = E.check_sync(self.lv, self.rows, self.mk(), self.b.probe)
        self.assertEqual(r["gate_status"], "PASS")
        self.assertEqual(len(r["times"]), sum(len(x["sentences"]) for x in self.rows))
        first = [x for x in self.rows if x["sentences"]][0]
        self.assertAlmostEqual(r["times"][first["sentences"][0]["sid"]][0], first["data_t"], places=3)   # row_local 0.0 -> data_t
        self.assertEqual(set(r["kp_en"]), {x["row_id"] for x in self.rows if x["kind"] == "kp"})

    def test_rows_for_sync_contains_only_text_and_kp_rows_with_expected_keys(self):
        rs = E.rows_for_sync(self.rows)
        self.assertTrue(all(set(r) <= {"row_id", "kind", "audio_path", "sentences", "kp"} for r in rs))
        self.assertTrue(all(r["sentences"] or r["kind"] == "kp" for r in rs))
        self.assertTrue(all(isinstance(r["kp"], dict) and r["kp"]["expressions"] for r in rs if r["kind"] == "kp"))
        self.assertFalse(any(r["kind"] in ("sfx", "fixed") for r in rs))

    def test_dummy_and_proportional_rejected(self):
        self.assertEqual(self.check(kind="DUMMY_PROPORTIONAL"), "ENDUSER_SYNC_DUMMY")
        self.assertEqual(self.check(note="dummy sync"), "ENDUSER_SYNC_DUMMY")
        p = dict(self.mk()["params"], engine="proportional-dummy")
        self.assertEqual(self.check(params=p), "ENDUSER_SYNC_DUMMY")

    def test_missing_asr_provenance_rejected(self):
        base = self.mk()["params"]
        self.assertEqual(self.check(params=None), "ENDUSER_SYNC_PROVENANCE")
        self.assertEqual(self.check(params=dict(base, engine="difflib")), "ENDUSER_SYNC_PROVENANCE")
        self.assertEqual(self.check(model=""), "ENDUSER_SYNC_PROVENANCE")
        self.assertEqual(self.check(model=None), "ENDUSER_SYNC_PROVENANCE")
        self.assertEqual(self.check(params={}), "ENDUSER_SYNC_PROVENANCE")

    def test_schema_time_base_and_gate(self):
        self.assertEqual(self.check(schema="other"), "ENDUSER_SYNC_SCHEMA")
        self.assertEqual(self.check(params=dict(self.mk()["params"], time_base="unknown")), "ENDUSER_SYNC_SCHEMA")
        self.assertEqual(self.check(gate={"status": "FAIL"}), "ENDUSER_SYNC_GATE")
        self.assertEqual(self.check(gate=None), "ENDUSER_SYNC_GATE")
        self.assertEqual(self.check(cost={"api_calls": 3}), "ENDUSER_COST")

    def test_mp3_sha_mismatch_rejected(self):
        s = self.mk()
        s["rows"][0]["mp3_sha256"] = "0" * 64
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s, self.b.probe), "ENDUSER_SYNC_PROVENANCE")

    def test_coverage_missing_extra_and_sid_order(self):
        s = self.mk()
        s2 = copy.deepcopy(s)
        text_ids = [i for i, r in enumerate(s2["rows"]) if r["sentences"]]
        s2["rows"].pop(text_ids[-1])
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s2, self.b.probe), "ENDUSER_SYNC_COVERAGE")
        s3 = copy.deepcopy(s)
        s3["rows"][0]["sentences"].reverse()
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s3, self.b.probe), "ENDUSER_SYNC_COVERAGE")
        s4 = copy.deepcopy(s)
        s4["rows"][0]["row_id"] = "nope"
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s4, self.b.probe), "ENDUSER_SYNC_COVERAGE")
        s5 = copy.deepcopy(s)
        s5["rows"].append(copy.deepcopy(s5["rows"][0]))
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s5, self.b.probe), "ENDUSER_SYNC_SCHEMA")     # row_id重複

    def test_range_and_monotonic(self):
        s = self.mk()
        s1 = copy.deepcopy(s)
        s1["rows"][1]["sentences"][0]["start"] = 5000.0       # 行のmp3長を超える(row_local)
        s1["rows"][1]["sentences"][0]["end"] = 5001.0
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s1, self.b.probe), "ENDUSER_SYNC_RANGE")
        s2 = copy.deepcopy(s)
        a, b = s2["rows"][0]["sentences"][0], s2["rows"][0]["sentences"][1]
        b["start"] = a["start"] + 0.001                  # 行内で前の文と重なる
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s2, self.b.probe), "ENDUSER_SYNC_MONOTONIC")
        s3 = copy.deepcopy(s)
        s3["rows"][0]["sentences"][0]["end"] = s3["rows"][0]["sentences"][0]["start"]
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s3, self.b.probe), "ENDUSER_SYNC_RANGE")
        # 行をまたぐ逆行(row_localを episode秒へ換算した後に前の行へ食い込む)
        s4 = copy.deepcopy(s)
        text = [r for r in s4["rows"] if r["sentences"]]
        text[1]["sentences"][0]["start"] = -0.0  # 0は許容
        rows2 = copy.deepcopy(self.rows)
        tr = [r for r in rows2 if r["sentences"]]
        tr[1]["data_t"] = tr[0]["data_t"] + 0.1          # 次の行の開始がdevの時刻上、前の行の途中
        self.assertEqual(stop_code(E.check_sync, self.lv, rows2, s4, self.b.probe), "ENDUSER_SYNC_MONOTONIC")

    def test_kp_en_from_sync_is_used_and_validated(self):
        art, sp, bi = self.b.data()
        kp = [p for p in art["levels"]["adv"]["parts"] if p["kind"] == "kp"][0]
        ea = kp["kp"][0]["en_audio"]
        self.assertEqual((ea["start"], ea["end"], ea["blocks"]), (1.42, 2.55, 4))
        self.assertTrue(ea["method"].startswith("enduser_sync kp_en"))
        s = self.mk()
        k = [r for r in s["rows"] if "kp_en" in r][0]
        k["kp_en"]["end"] = 9999.0
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s, self.b.probe), "ENDUSER_SYNC_RANGE")
        s = self.mk()
        [r for r in s["rows"] if "kp_en" in r][0]["kp_en"]["blocks"] = 3
        self.assertEqual(stop_code(E.check_sync, self.lv, self.rows, s, self.b.probe), "ENDUSER_SYNC_RANGE")

    def test_kp_fallback_to_compute_kp_audio_when_sync_has_no_kp_rows(self):
        b = Built("x_moon")
        b.sync = {lv: mock_sync(lv, r, b.probe, with_kp=False) for lv, r in b.rows.items()}
        art, sp, bi = b.data()
        ea = [p for p in art["levels"]["adv"]["parts"] if p["kind"] == "kp"][0]["kp"][0]["en_audio"]
        self.assertEqual(ea["method"], E.KP_METHOD)
        self.assertIn("asr_text", ea)
        self.assertEqual(stop_code(E.build_enduser_data, b.rows, b.sync, b.study, b.ja, b.meta, kp_audio={}, probe=b.probe), "ENDUSER_KP_AUDIO_MISSING")

    def test_missing_level_sync_is_stop(self):
        b = Built("x_moon")
        b.sync.pop("std")
        self.assertEqual(stop_code(b.data), "ENDUSER_SYNC_COVERAGE")

    def test_low_conf_and_cost_are_recorded_in_build_info(self):
        b = Built("x_moon")
        b.sync["adv"]["gate"]["warnings"] = [{"row_id": "adv_14", "low_conf_boundaries": [1]}]
        b.sync["adv"]["cost"] = {"api_calls": 0, "wall_s": 12.5, "cached_segments": 7}
        art, sp, bi = b.data()
        self.assertEqual(bi["sync"]["adv"]["low_conf_rows"], 1)
        self.assertEqual(bi["sync"]["adv"]["min_row_ratio"], 0.98)
        self.assertEqual(bi["cost"]["cached_segments"], 7)
        self.assertEqual(bi["cost"]["api_calls"], 0)
        self.assertTrue(bi["warnings"])


class T10_ValidatorNegatives(unittest.TestCase):
    """T-VAL-NEG: DEV仮データ・未承認データの混入、schema逸脱、音声・本文の不一致を1つずつ注入し、すべてSTOP。"""

    @classmethod
    def setUpClass(cls):
        cls.b = Built("x_moon")
        cls.art, cls.sp, cls.bi = cls.b.data()

    def v(self, art=None, sp=None, bi=None, probe=None):
        return stop_code(E.validate_output, art or self.art, sp or self.sp, bi or self.bi, self.b.rows, self.b.study, self.b.meta, probe=probe or self.b.probe)

    def test_baseline_valid(self):
        self.assertIsNone(self.v())

    def test_forbidden_words_each_rejected(self):
        for w in ("placeholder_for_layout_check", "dev_translation_unapproved", "DEV訳", "仮データ", "未承認", "[DEV]", "phnote", "=====", "\u23f8", "chunk-mark", "rpt-", "Traceback", "confirmation_id", "制作情報"):
            a = copy.deepcopy(self.art)
            a["levels"]["adv"]["vocab"][0]["fields"][0]["html"] += w
            self.assertEqual(self.v(art=a), "ENDUSER_FORBIDDEN_WORD", w)

    def test_absolute_paths_rejected(self):
        for w in ("C:\\Users\\tensh\\x", "C:/Users/tensh/x", "/Users/tensh/er019_output", "er019_output/a"):
            a = copy.deepcopy(self.art)
            a["title_ja"] += " " + w
            self.assertEqual(self.v(art=a), "ENDUSER_FORBIDDEN_WORD", w)

    def test_unknown_and_missing_keys_rejected(self):
        a = copy.deepcopy(self.art)
        a["grammar_source"] = "placeholder_for_layout_check"
        self.assertEqual(self.v(art=a), "ENDUSER_SCHEMA")
        a = copy.deepcopy(self.art)
        a["levels"]["adv"]["nuance_source"] = "x"
        self.assertEqual(self.v(art=a), "ENDUSER_SCHEMA")
        a = copy.deepcopy(self.art)
        a["levels"]["adv"]["parts"][3]["devnote"] = "x"
        self.assertEqual(self.v(art=a), "ENDUSER_SCHEMA")
        a = copy.deepcopy(self.art)
        del a["levels"]["adv"]["total_sec"]
        self.assertEqual(self.v(art=a), "ENDUSER_SCHEMA")
        a = copy.deepcopy(self.art)
        a["audio_base"] = "../family_x_ai_island_form_01/"
        self.assertEqual(self.v(art=a), "ENDUSER_SCHEMA")
        bi = copy.deepcopy(self.bi)
        bi["extra"] = 1
        self.assertEqual(self.v(bi=bi), "ENDUSER_SCHEMA")
        sp = copy.deepcopy(self.sp)
        sp["adv"]["sentences"][0]["conf"] = 0.9
        self.assertEqual(self.v(sp=sp), "ENDUSER_SCHEMA")

    def test_text_mismatch_rejected(self):
        a = copy.deepcopy(self.art)
        s = [p for p in a["levels"]["adv"]["parts"] if p["kind"] == "story"][0]["paragraphs"][0][0]
        s["text"] = s["text"] + " extra"
        self.assertEqual(self.v(art=a), "ENDUSER_TEXT_MISMATCH")
        a = copy.deepcopy(self.art)
        a["levels"]["adv"]["parts"][8]["kp"][0]["en"] = "other"
        self.assertEqual(self.v(art=a), "ENDUSER_TEXT_MISMATCH")
        a = copy.deepcopy(self.art)
        a["levels"]["adv"]["parts"].pop()
        self.assertEqual(self.v(art=a), "ENDUSER_TEXT_MISMATCH")

    def test_lk_mark_mismatch_rejected(self):
        a = copy.deepcopy(self.art)
        for p in a["levels"]["adv"]["parts"]:
            for pa in p.get("paragraphs", []):
                for s in pa:
                    if 'class="lk3"' in s["html"]:
                        s["html"] = s["html"].replace('class="lk3"', 'class="lk1"', 1)
                        self.assertEqual(self.v(art=a), "ENDUSER_TEXT_MISMATCH")
                        return
        self.fail("lk3 not found")

    def test_study_mismatch_rejected(self):
        a = copy.deepcopy(self.art)
        a["levels"]["adv"]["vocab"].pop()
        self.assertEqual(self.v(art=a), "ENDUSER_STUDY_MISMATCH")

    def test_audio_missing_and_sha_mismatch_rejected(self):
        bad = FakeAudio(self.b.rows, self.b.meta)
        bad.override_sha["audio/adv_00.mp3"] = "f" * 64
        self.assertEqual(self.v(probe=bad), "ENDUSER_AUDIO_MISMATCH")
        gone = FakeAudio(self.b.rows, self.b.meta)
        gone.dur.pop("audio/adv_01.mp3")
        self.assertEqual(self.v(probe=gone), "ENDUSER_AUDIO_MISSING")
        bi = copy.deepcopy(self.bi)
        bi["audio_sha256"].pop("audio/adv_02.mp3")
        self.assertEqual(self.v(bi=bi), "ENDUSER_AUDIO_MISSING")

    def test_sync_sid_mismatch_rejected(self):
        sp = copy.deepcopy(self.sp)
        sp["adv"]["sentences"].pop()
        self.assertEqual(self.v(sp=sp), "ENDUSER_SYNC_COVERAGE")

    def test_cost_and_unexpected_html_rejected(self):
        bi = copy.deepcopy(self.bi)
        bi["cost"]["api_calls"] = 1
        self.assertEqual(self.v(bi=bi), "ENDUSER_COST")
        a = copy.deepcopy(self.art)
        a["levels"]["adv"]["vocab"][0]["fields"][0]["html"] += "<script>x</script>"
        self.assertEqual(self.v(art=a), "ENDUSER_FORBIDDEN_WORD")

    def test_ja_source_invalid_and_unpaired(self):
        a = copy.deepcopy(self.art)
        p = [p for p in a["levels"]["adv"]["parts"] if p["kind"] == "story"][0]
        p["ja_source"] = "machine"
        self.assertEqual(self.v(art=a), "ENDUSER_SCHEMA")
        a = copy.deepcopy(self.art)
        p = [p for p in a["levels"]["adv"]["parts"] if p["kind"] == "story"][0]
        del p["ja_source"]
        self.assertEqual(self.v(art=a), "ENDUSER_JA_SOURCE_INVALID")


class T11_Assets(unittest.TestCase):
    """M5: index.html/app.js/style.cssはproduction asset(DEV rev01-eの機械的派生)とsha256一致。除去は許可リスト固定。DEV試作の痕跡なし。"""

    def test_assets_match_manifest_and_have_no_forbidden_words(self):
        shas = E.check_assets()
        self.assertEqual(set(shas), {"index.html", "app.js", "style.css"})

    def test_assets_equal_dev_plus_allowlist_only(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("derive_assets_01", ASSETS / "derive_assets_01.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        derived = m.derive()
        for n, t in derived.items():
            self.assertEqual((ASSETS / R.ASSET_BUILD_ID / n).read_text(encoding="utf-8"), t, n)
        ids = [e["id"] for e in m.EDITS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(e["kind"] in ("REMOVE", "ADD") for e in m.EDITS))
        # 許可リストの除去対象が実際にassetから消えている
        js = derived["app.js"]
        for gone in ("dummy", "Q.get('a')", "[DEV]", "placeholder_for_layout_check", "dev_translation_unapproved", "syncIndex", "syncState"):
            self.assertNotIn(gone, js)

    def test_no_other_article_audio_base_or_dev_paths(self):
        for n in ("index.html", "app.js", "style.css"):
            t = (ASSETS / R.ASSET_BUILD_ID / n).read_text(encoding="utf-8")
            for w in R.FORBIDDEN_ASSET:
                self.assertNotIn(w, t, f"{n}: {w}")
            self.assertNotRegex(t, r"audio_base\s*[:=]\s*['\"][^'\"]*family_")

    def test_tampered_asset_sha_is_stop_and_nothing_written(self):
        with tempfile.TemporaryDirectory() as td:
            ad = Path(td) / "assets"
            shutil.copytree(ASSETS / R.ASSET_BUILD_ID, ad)
            (ad / "app.js").write_text((ad / "app.js").read_text(encoding="utf-8") + "\n// tampered\n", encoding="utf-8")
            self.assertEqual(stop_code(E.check_assets, ad), "ENDUSER_ASSET_MISMATCH")
            pub = Path(td) / "pub"
            pub.mkdir()
            b = Built("x_moon")
            art, sp, bi = b.data()
            self.assertEqual(stop_code(E.write_enduser_page, pub / "enduser", (art, sp, bi), ad), "ENDUSER_ASSET_MISMATCH")
            self.assertEqual(os.listdir(pub), [])

    def test_dummy_sync_remnant_in_asset_is_stop_even_if_manifest_updated(self):
        with tempfile.TemporaryDirectory() as td:
            ad = Path(td) / "assets"
            shutil.copytree(ASSETS / R.ASSET_BUILD_ID, ad)
            (ad / "app.js").write_text((ad / "app.js").read_text(encoding="utf-8") + "\nvar m = Q.get('sync') === 'dummy';\n", encoding="utf-8")
            man = json.load(open(ad / "ASSET_SHA256.json", encoding="utf-8"))
            man["files"]["app.js"] = E.sha256_file(ad / "app.js")
            json.dump(man, open(ad / "ASSET_SHA256.json", "w", encoding="utf-8"))
            self.assertEqual(stop_code(E.check_assets, ad), "ENDUSER_ASSET_MISMATCH")

    def test_dev_assets_unchanged_by_derivation(self):
        # deriveはDEVを読むだけ(DEV側のファイルは変更しない)。DEVのapp.jsがまだ旧機能を持つこと=不変の確認
        dev = (ROOT / "user_test" / "dev_enduser_page_01" / "app.js").read_text(encoding="utf-8")
        self.assertIn("Q.get('a')", dev)


class T12_AtomicWrite(unittest.TestCase):
    """M4: 一時dir→一括rename。失敗時にenduser/を書かない・既存enduser/を失敗時に削除しない・再実行で置換。"""

    def make_public(self, td, name="x_moon"):
        pub = Path(td) / "pub"
        pub.mkdir()
        (pub / "index.html").write_text(fx_html(name), encoding="utf-8")
        b = Built(name)
        for rel in list(b.probe.dur):
            p = pub / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(("audio:" + rel).encode())
        b.probe = FakeAudio(b.rows, b.meta, root=pub)
        b.sync = {lv: mock_sync(lv, r, b.probe) for lv, r in b.rows.items()}
        return pub, b

    def build(self, pub, b, **kw):
        return E.build_enduser(pub, b.family, b.sync, kp_audio=kp_fake(b.rows), probe=b.probe, ja_manuscript=None, **kw)

    def test_success_writes_all_files_and_build_info(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b = self.make_public(td)
            res = self.build(pub, b)
            ed = pub / "enduser"
            names = sorted(str(p.relative_to(ed)).replace("\\", "/") for p in ed.rglob("*") if p.is_file())
            self.assertEqual(names, ["app.js", "build_info.json", "data/article.json", "data/sync_adv.json", "data/sync_std.json", "index.html", "style.css"])
            bi = json.load(open(ed / "build_info.json", encoding="utf-8"))
            for rel, sha in bi["files"].items():
                self.assertEqual(E.sha256_text_file(ed / rel), sha)
            self.assertEqual(bi["cost"]["api_calls"], 0)
            self.assertEqual(bi["dev_index_sha256"], E.sha256_text_file(pub / "index.html"))
            self.assertEqual([p.name for p in pub.iterdir() if p.name.startswith(".enduser")], [])
            self.assertEqual(json.load(open(ed / "data" / "article.json", encoding="utf-8"))["audio_base"], "../")

    def test_validation_failure_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b = self.make_public(td)
            b.sync["adv"] = mock_sync("adv", b.rows["adv"], b.probe, gate={"status": "FAIL"})
            before = sorted(os.listdir(pub))
            self.assertEqual(stop_code(self.build, pub, b), "ENDUSER_SYNC_GATE")
            self.assertEqual(sorted(os.listdir(pub)), before)
            self.assertFalse((pub / "enduser").exists())

    def test_failure_keeps_existing_enduser_untouched_and_stale_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b = self.make_public(td)
            self.build(pub, b)
            before = {str(p.relative_to(pub)): E.sha256_file(p) for p in (pub / "enduser").rglob("*") if p.is_file()}
            # devが変わった上で、同期が失敗 -> 既存enduser/は消さない・変えない
            (pub / "index.html").write_text(fx_html("x_moon") + "\n<!-- changed -->", encoding="utf-8")
            b.sync["adv"] = mock_sync("adv", b.rows["adv"], b.probe, params=None)
            self.assertEqual(stop_code(self.build, pub, b), "ENDUSER_SYNC_PROVENANCE")
            after = {str(p.relative_to(pub)): E.sha256_file(p) for p in (pub / "enduser").rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            r = E.verify_consistency(pub)
            self.assertFalse(r["ok"])
            self.assertIn("ENDUSER_STALE_DEV_CHANGED", [v["code"] for v in r["violations"]])

    def test_rerun_replaces_atomically_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b = self.make_public(td)
            self.build(pub, b)
            a1 = (pub / "enduser" / "data" / "article.json").read_bytes()
            self.build(pub, b)
            self.assertEqual((pub / "enduser" / "data" / "article.json").read_bytes(), a1)
            self.assertEqual([p.name for p in pub.iterdir() if p.name.startswith(".enduser")], [])
            self.assertTrue(E.verify_consistency(pub)["ok"])

    def test_rename_failure_restores_old_and_cleans_tmp(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b = self.make_public(td)
            self.build(pub, b)
            before = {str(p.relative_to(pub)): E.sha256_file(p) for p in (pub / "enduser").rglob("*") if p.is_file()}
            real = os.rename
            calls = {"n": 0}

            def flaky(a, b_):
                calls["n"] += 1
                if calls["n"] == 2:          # 1回目=旧enduser退避、2回目=新dirの設置 -> 失敗させる
                    raise OSError("simulated rename failure")
                return real(a, b_)
            E.os.rename = flaky
            try:
                self.assertEqual(stop_code(self.build, pub, b), "ENDUSER_WRITE_FAILED")
            finally:
                E.os.rename = real
            after = {str(p.relative_to(pub)): E.sha256_file(p) for p in (pub / "enduser").rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertEqual([p.name for p in pub.iterdir() if p.name.startswith(".enduser")], [])

    def test_dev_index_and_audio_unchanged_by_build(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b = self.make_public(td)
            before = {str(p.relative_to(pub)): E.sha256_file(p) for p in pub.rglob("*") if p.is_file()}
            self.build(pub, b)
            after = {str(p.relative_to(pub)): E.sha256_file(p) for p in pub.rglob("*") if p.is_file() and "enduser" not in p.parts}
            self.assertEqual(before, after)
            self.assertFalse(any(p.suffix == ".mp3" for p in (pub / "enduser").rglob("*")))   # mp3複製0

    def test_no_extra_asr_when_sync_carries_kp_en(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b = self.make_public(td)
            real = E.compute_kp_audio

            def boom(*a, **k):
                raise AssertionError("compute_kp_audio must not run when sync has kp_en for every KP row")
            E.compute_kp_audio = boom
            try:
                E.build_enduser(pub, b.family, b.sync, probe=b.probe)
            finally:
                E.compute_kp_audio = real
            self.assertTrue((pub / "enduser" / "index.html").is_file())

    def test_three_families_build_and_consistent(self):
        for name in ("x_moon", "y_fee03", "z_melos02"):
            with tempfile.TemporaryDirectory() as td:
                pub, b = self.make_public(td, name)
                self.build(pub, b)
                r = E.verify_consistency(pub)
                self.assertTrue(r["ok"], (name, r["violations"]))


class T13_ConsistencyCheck(unittest.TestCase):
    """M6(検証): verify_consistency(公開dir): dev行=enduser本文、音声sha、asset sha、stale検出。"""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        t = T12_AtomicWrite()
        self.pub, self.b = t.make_public(self.td.name)
        t.build(self.pub, self.b)

    def tearDown(self):
        self.td.cleanup()

    def codes(self):
        return {v["code"] for v in E.verify_consistency(self.pub)["violations"]}

    def test_ok(self):
        r = E.verify_consistency(self.pub)
        self.assertTrue(r["ok"], r["violations"])
        self.assertEqual(r["checked"]["levels"], ["adv", "std"])

    def test_not_built(self):
        shutil.rmtree(self.pub / "enduser")
        self.assertEqual(self.codes(), {"ENDUSER_NOT_BUILT"})

    def test_dev_text_changed_is_stale_and_text_mismatch(self):
        h = (self.pub / "index.html").read_text(encoding="utf-8")
        (self.pub / "index.html").write_text(h.replace("As you listen, notice how the team studied", "As you listen, notice how the crew studied"), encoding="utf-8")
        c = self.codes()
        self.assertIn("ENDUSER_STALE_DEV_CHANGED", c)
        self.assertIn("ENDUSER_TEXT_MISMATCH", c)

    def test_audio_changed_or_missing(self):
        (self.pub / "audio" / "adv_00.mp3").write_bytes(b"changed")
        self.assertIn("ENDUSER_AUDIO_MISMATCH", self.codes())
        (self.pub / "audio" / "adv_00.mp3").unlink()
        self.assertIn("ENDUSER_AUDIO_MISSING", self.codes())

    def test_asset_tampered(self):
        p = self.pub / "enduser" / "app.js"
        p.write_text(p.read_text(encoding="utf-8") + "\n// x\n", encoding="utf-8")
        c = self.codes()
        self.assertIn("ENDUSER_FILE_SHA_MISMATCH", c)
        self.assertIn("ENDUSER_ASSET_MISMATCH", c)

    def test_article_json_tampered(self):
        p = self.pub / "enduser" / "data" / "article.json"
        j = json.load(open(p, encoding="utf-8"))
        j["levels"]["adv"]["parts"][14]["paragraphs"][0][0]["text"] += "!"
        json.dump(j, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        c = self.codes()
        self.assertIn("ENDUSER_FILE_SHA_MISMATCH", c)
        self.assertIn("ENDUSER_TEXT_MISMATCH", c)

    def test_crlf_checkout_does_not_cause_false_stale(self):
        """Windows(autocrlf)のcheckoutで公開dir・assetがCRLFになっても整合検査は偽陽性にならない(テキストは改行正規化shaで比較)。"""
        for p in [self.pub / "index.html"] + [q for q in (self.pub / "enduser").rglob("*") if q.is_file()]:
            p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        with tempfile.TemporaryDirectory() as td:
            ad = Path(td) / "assets"
            shutil.copytree(ASSETS / R.ASSET_BUILD_ID, ad)
            for p in ad.iterdir():
                p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
            r = E.verify_consistency(self.pub, assets_dir=ad)
        self.assertTrue(r["ok"], r["violations"])

    def test_stray_tmp_dir_reported(self):
        (self.pub / ".enduser.tmp.123.abcd").mkdir()
        self.assertIn("ENDUSER_STALE_TMP", self.codes())

    def test_forbidden_word_injected_into_article(self):
        p = self.pub / "enduser" / "data" / "article.json"
        j = json.load(open(p, encoding="utf-8"))
        j["levels"]["adv"]["vocab"][0]["fields"][0]["html"] += "placeholder_for_layout_check"
        json.dump(j, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        self.assertIn("ENDUSER_FORBIDDEN_WORD", self.codes())

    def test_schema_violation_reported(self):
        p = self.pub / "enduser" / "data" / "article.json"
        j = json.load(open(p, encoding="utf-8"))
        j["devonly"] = 1
        json.dump(j, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        self.assertIn("ENDUSER_SCHEMA", self.codes())

    def test_cli_exit_codes(self):
        self.assertEqual(E.main(["verify-consistency", "--public-dir", str(self.pub)]), 0)
        (self.pub / "index.html").write_text(fx_html("x_moon") + "<!--x-->", encoding="utf-8")
        self.assertEqual(E.main(["verify-consistency", "--public-dir", str(self.pub)]), 3)


class T14_StaticIsolation(unittest.TestCase):
    """M5: er135がDEV/Trial pathをimport・読込しない。同期moduleを呼ばない。API/ネットワークを使わない。"""

    SRC = ["er135_enduser_page_01.py", "er135_enduser_dom_01.py", "er135_enduser_page_verify_01.py"]

    def test_no_dev_or_trial_path_references(self):
        for f in self.SRC:
            t = (ROOT / f).read_text(encoding="utf-8")
            for w in R.FORBIDDEN_MODULE_REFERENCES:
                self.assertNotIn(w, t, f"{f}: {w}")
            self.assertNotRegex(t, r"user_test[\\/]+dev_")

    def test_no_sync_module_import_or_call(self):
        for f in self.SRC:
            t = (ROOT / f).read_text(encoding="utf-8")
            self.assertNotRegex(t, r"^\s*(import|from)\s+er135_enduser_sync", f)
            if f != "er135_enduser_page_01.py":   # ASR(faster_whisper)はKP区間確認の既定実装(本体のみ)。dom/verifyは使わない
                self.assertNotIn("faster_whisper", t, f)

    def test_no_api_clients(self):
        for f in self.SRC[:2]:
            t = (ROOT / f).read_text(encoding="utf-8")
            for w in ("openai", "anthropic", "google.genai", "import requests", "urlopen", "genai"):
                self.assertNotIn(w, t, f"{f}: {w}")

    def test_dev_html_parsed_by_parser_not_regex(self):
        t = (ROOT / "er135_enduser_page_01.py").read_text(encoding="utf-8")
        self.assertIn("parse_html(", t)
        # dev HTMLを正規表現で解析する呼出(re.findall/re.search/re.finditer を dev_html/dev_index_html へ)が無い
        self.assertNotRegex(t, r"re\.(findall|search|finditer|match|split)\([^\n]*(dev_html|dev_index_html|html_text)")

    def test_verify_module_imports(self):
        import er135_enduser_page_verify_01 as V
        self.assertTrue(callable(V.run))


class T15_Determinism(unittest.TestCase):
    def test_same_input_same_output(self):
        a1 = Built("y_fee03").data()
        a2 = Built("y_fee03").data()
        self.assertEqual(json.dumps(a1[0], sort_keys=True), json.dumps(a2[0], sort_keys=True))
        self.assertEqual(json.dumps(a1[1], sort_keys=True), json.dumps(a2[1], sort_keys=True))

    def test_sid_unique_per_level_and_sync_covers_all(self):
        for name in ("x_moon", "y_fee03", "z_melos02", "z_open596_min"):
            art, sp, bi = Built(name, use_ja=False).data() if name == "z_open596_min" else Built(name).data()
            for lv, L in art["levels"].items():
                sids = [s["sid"] for p in L["parts"] for pa in p.get("paragraphs", []) for s in pa]
                self.assertEqual(len(sids), len(set(sids)))
                self.assertEqual(set(sids), {s["sid"] for s in sp[lv]["sentences"]})
                starts = [s["start"] for s in sp[lv]["sentences"]]
                self.assertEqual(starts, sorted(starts))


class T16_ProperNounsForRun(unittest.TestCase):
    """FZ-DIALOGUE-LR-ADOPTION-01 委任_07: runから機械的に得る固有名詞(roster読取のみ)。"""

    def test_z_roster_capitalised_names_only(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            rd = Path(d)
            (rd / "writer").mkdir()
            (rd / "writer" / "r2.md").write_text("The woodcutter spoke. Tajomaru laughed. Then Masago and the monk left. A monk said Takehiro died.", encoding="utf-8")
            (rd / "voice_assignment.json").write_text(json.dumps({"speakers": [{"speaker": "woodcutter"}, {"speaker": "monk"}, {"speaker": "tajomaru"},
                                                                              {"speaker": "masago"}, {"speaker": "takehiro"}, {"speaker": "old_woman"}]}), encoding="utf-8")
            before = sorted(p.name for p in rd.rglob("*"))
            pn = E.proper_nouns_for_run(rd, "z")
            self.assertEqual(sorted(pn["en"]), ["Masago", "Tajomaru", "Takehiro"])
            self.assertEqual(before, sorted(p.name for p in rd.rglob("*")))          # 読み取りのみ

    def test_xy_title_and_kp(self):
        pn = E.proper_nouns_for_run(None, "x", {"std": [{"kp": {"expressions": ["make an effort"]}}, {"kind": "script"}]}, {"topic_en": "Wrinkles on the Moon"})
        self.assertEqual(pn["en"], ["Wrinkles", "Moon", "make an effort"])


class T17_GlossaryHeadingPreferred(unittest.TestCase):
    """FZLR委任_07: 下線語が他Vocabularyの例文にも含まれるとき、見出し語が対応する項目を優先(藪の中Std bandit/constable)。"""

    def test_underline_maps_to_vocab_with_matching_heading(self):
        def vocab(h, quote, ja):
            return {"heading": h, "fields": [{"label": "本文の英文", "html": quote}, {"label": "本文中の意味", "html": ja}]}
        v = [vocab("constable", "I caught the famous bandit Tajomaru, the constable said", "警官"),
             vocab("bandit", "I caught the famous bandit Tajomaru, the constable said", "盗賊")]
        sent = {"sid": "s1", "html": '<span class="lk2" data-hl="p_a">constable</span> and <span class="lk1" data-hl="p_b">bandit</span>', "text": "constable and bandit"}
        parts = [{"kind": "story", "label": "Part 1", "paragraphs": [[sent]], "meanings": []}]
        self.assertEqual(E.build_glossary("std", parts, v), "applied")
        self.assertEqual([g["en"] for g in parts[0]["glossary"]], ["constable", "bandit"])
        self.assertEqual([g["ja"] for g in parts[0]["glossary"]], ["警官", "盗賊"])


class T18_IrregularVerbEmphasis(unittest.TestCase):
    """委任_08: asset/DEV app.jsの不規則動詞表(IRR)とmatchPhraseの語形一致(nodeでJS実行。API 0)。"""

    @staticmethod
    def _run(js_path, heading, text):
        import subprocess
        src = Path(js_path).read_text(encoding="utf-8")
        a = src.index("var IRR = (function")
        b = src.index("function wrapRanges")
        code = "var out;" + src[a:b] + "\nprocess.stdout.write(JSON.stringify(matchPhrase(%s,%s,true)));" % (json.dumps(heading), json.dumps(text))
        r = subprocess.run(["node", "-e", code], capture_output=True, text=True, encoding="utf-8", timeout=60)
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout)

    def _both(self):
        return [ASSETS / "rev01-e" / "app.js", ROOT / "user_test" / "dev_enduser_page_01" / "app.js"]

    def test_sink_forms_bold(self):
        for js in self._both():
            r = self._run(js, "sink for ever", "I sank for ever into the darkness")
            self.assertEqual(r["n"], 1)
            self.assertEqual(len(r["ranges"]), 1)
            self.assertEqual(r["ranges"][0][1] - r["ranges"][0][0], len("sank for ever"))
            self.assertEqual(self._run(js, "sink", "the stone had sunk")["n"], 1)

    def test_table_size_and_common_verbs(self):
        src = (ROOT / "user_test" / "dev_enduser_page_01" / "app.js").read_text(encoding="utf-8")
        g = re.search(r"var g = '(.*?)'\.split", src).group(1).split("|")
        self.assertGreaterEqual(len(g), 100)
        for js in self._both():
            for base, past in [("swim", "swam"), ("steal", "stole"), ("throw", "threw"), ("understand", "understood"), ("wake", "woke")]:
                self.assertEqual(self._run(js, base, "He " + past + " away")["n"], 1, base)

    def test_failsafe_unchanged(self):
        for js in self._both():
            self.assertEqual(self._run(js, "sink", "no such word here")["ranges"], [])
            self.assertEqual(self._run(js, "one's", "something")["ranges"], [])  # placeholderのみ=特定不可
            self.assertEqual(self._run(js, "sink", "sank and sink")["ranges"], [])  # 複数候補=非強調


if __name__ == "__main__":
    unittest.main(verbosity=2)
