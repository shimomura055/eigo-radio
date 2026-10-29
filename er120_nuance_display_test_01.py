# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02B Track A: 表示(ニュアンス解説の独立コーナー・文法0件の完全非表示)とpage_verify一般化のtest。全てmock・API 0。

対象(ユーザー正式決定2026-10-29 §2A-5/6・§2C・Opus M-5/M-6/M-7/R-6/R-13):
  - ニュアンス{採用/不採用/候補なし/技術失敗/結果ファイルなし} x 文法{採用/0件} x Part 1{あり/なし} x X/Y/Zのstudy_dir配置 x Std/Adv の合成結果
    (見出し・空枠・固定文面・プレースホルダー・二重CSSが無い。Part 1 -> 文法 -> ニュアンス解説の順)
  - verify_outputs(節単位の一致検証。期待ブロック数0/1・ニュアンス節単位一致・ページ非表示語)
  - 既存0件runの旧md(固定文面)は決定論で退避してから検証(削除しない)
  - compose_page_htmlのnuanceは必須keyword(R-6)、runner呼出元は全てnuanceを渡す
実行: .venv/Scripts/python.exe -m pytest er120_nuance_display_test_01.py -q
"""
import test_state_isolation_01  # noqa: F401  (Production監査ログ汚染防止)

import inspect
import json
import os
import re
import unittest

import er003_kp_general_explanation_01 as p1
import er120_part2_grammar_production_01 as g
import er120_part2_wiring_01 as p2w
from er120_part2_pregen_test_01 import PCase, PARAS, LABEL

ROOT = os.path.dirname(os.path.abspath(__file__))
PARAS2 = ["The short story begins here. It was a calm night.", "It was in March that the plan changed. People cheered.", "Nothing else happened that day."]
PART1_BLOCK = (p1.STUDY_CSS + "<section class='study'><h3>Vocabulary &amp; Expressions</h3><div class='study-item'><h4>stood before</h4>"
               "<dl><dt>解説</dt><dd><p>説明</p></dd></dl></div></section>")
OLD_ZERO_TEXT = "今回の本文には、このPartで特に取り上げる難所となる構文はありませんでした。"
PLACEHOLDERS = ("（なし）", "(なし)", "候補なし", "Deeper Understanding", "特に取り上げる難所", "このPartで")


def nuance_result(level, status="ADOPTED", **kw):
    cand = {"expression": "at least", "focus": "at least が示す『最低限』という語感", "explanation_ja": "**at least** は『少なくとも』という最低ラインを示します。\n\nここでは話し手の安堵が出ています。",
            "quote_en": "At least she was safe.", "quote_ja": "少なくとも彼女は無事だった。"}
    cand.update(kw)
    return {"schema": "nuance_result_v1", "level_key": level, "status": status, "candidate": cand if status in ("ADOPTED", "REJECTED") else None}


def write_nuance(sd, res):
    os.makedirs(sd, exist_ok=True)
    with open(f"{sd}/{g.NUANCE_RESULT_FILENAME}", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False)


def clear_nuance(sd):
    p = f"{sd}/{g.NUANCE_RESULT_FILENAME}"
    if os.path.exists(p):
        os.remove(p)


class _Fx(PCase):
    def make(self, family, level, gmode):
        """study_dir_for(family, out, level) の配置で文法を確定する。gmode=selected|zero。戻り: (sd, paras, grammar result)"""
        out = f"{self.run_dir}/{family}_{gmode}"
        sd = p2w.study_dir_for(family, out, level)
        paras = PARAS if level == "b1b" else PARAS2
        self.prepare(level=level, sd=sd, paras=paras, slug=f"{family}{gmode}{level}")
        if gmode == "selected":
            self.decide("pick", sd=sd, ids=[self.ids(sd)[0]], accept_ai=True)
        else:
            self.decide("omit", sd=sd, reason="今回は解説を出さない")
        return sd, paras, self.final(level=level, sd=sd, paras=paras)["result"]


class T1_Matrix(_Fx):
    NUANCE_MODES = ("adopted", "rejected", "none", "failed_technical", "absent")

    def _set_mode(self, sd, level, mode):
        clear_nuance(sd)
        if mode == "adopted":
            write_nuance(sd, nuance_result(level, "ADOPTED"))
        elif mode == "rejected":
            write_nuance(sd, nuance_result(level, "REJECTED"))
        elif mode == "none":
            write_nuance(sd, nuance_result(level, "NONE"))
        elif mode == "failed_technical":
            write_nuance(sd, nuance_result(level, "FAILED_TECHNICAL"))

    def test_four_combinations_on_all_six_paths_have_no_heading_empty_box_placeholder_or_double_css(self):
        n_cases = 0
        for family in ("x", "y", "z"):
            for level in ("b1b", "a2"):
                for gmode in ("selected", "zero"):
                    sd, paras, gres = self.make(family, level, gmode)
                    md = f"{sd}/{g.PART2_FILE_STEM}.md"
                    for mode in self.NUANCE_MODES:
                        self._set_mode(sd, level, mode)
                        nuance = p2w.nuance_for_display(sd, level=level)
                        for part1 in ("", PART1_BLOCK):
                            tag = f"{family}/{level}/{gmode}/{mode}/part1={'y' if part1 else 'n'}"
                            html = p2w.compose_page_html(part1, gres, nuance=nuance)
                            exp_g, exp_n = (1 if gmode == "selected" else 0), (1 if mode == "adopted" else 0)
                            self.assertEqual(g.count_grammar_blocks(html), exp_g, tag)
                            self.assertEqual(g.count_nuance_blocks(html), exp_n, tag)
                            self.assertEqual(g.count_empty_study_sections(html), 0, tag)             # 空枠(見出しだけ)が無い
                            for ph in PLACEHOLDERS:
                                self.assertNotIn(ph, html, f"{tag}: {ph}")
                            self.assertNotIn("<h3></h3>", html, tag)
                            nonempty = bool(part1 or exp_g or exp_n)
                            self.assertEqual(html == "", not nonempty, tag)                           # 3ブロックとも空なら空文字(CSSも出さない)
                            self.assertEqual(html.count("<style>"), 1 if nonempty else 0, tag)       # CSSは最初の非空ブロックが1回だけ持つ
                            if html:
                                self.assertTrue(html.startswith("<style>"), tag)
                            pos = [html.index(m) for m in ("Vocabulary &amp; Expressions", "Grammar &amp; Sentence Structure", f"<h3>{g.NUANCE_HEADING}</h3>") if m in html]
                            self.assertEqual(pos, sorted(pos), tag)                                   # Part 1 -> 文法 -> ニュアンス解説
                            # 節単位の一致検証(page_verifyが使う関数)も同じ期待で通る
                            self.assertEqual(os.path.exists(md), gmode == "selected", tag)           # 0件はmdを書かない
                            exp = p2w.verify_outputs(sd, paras, LABEL, level=level, next_command="x", md_path=md, html_text=f"<div>{html}</div>")
                            self.assertEqual(exp, {"grammar_blocks": exp_g, "nuance_blocks": exp_n}, tag)
                            n_cases += 1
        self.assertEqual(n_cases, 3 * 2 * 2 * 5 * 2)

    def test_display_order_is_heading_expression_quote_translation_point_explanation(self):
        """ユーザー正式決定2026-10-29(NUANCE-DISPLAY-ORDER-AND-HR-PRECHECK-01 ①): 見出し->学習表現->本文の英文->日本語訳->ポイント->解説(全Family・全level共通builder)。"""
        for fam in ("x", "y", "z"):
            for level in ("a2", "b1b"):
                sd, paras, gres = self.make(fam, level, "selected")
                write_nuance(sd, nuance_result(level))
                html = p2w.compose_page_html(PART1_BLOCK, gres, nuance=p2w.nuance_for_display(sd, level=level))
                blk = html[html.index(f"<h3>{g.NUANCE_HEADING}</h3>"):]
                marks = [f"<h3>{g.NUANCE_HEADING}</h3>", "<h4>at least</h4>", "<dt>本文の英文</dt>", "<dt>日本語訳</dt>", "<dt>ポイント</dt>", "<dt>解説</dt>"]
                pos = [blk.index(m) for m in marks]
                self.assertEqual(pos, sorted(pos), (fam, level))
                self.assertEqual(len(set(pos)), 6)

    def test_adopted_block_is_a_separate_corner_with_the_approved_heading_only(self):
        sd, paras, gres = self.make("x", "b1b", "selected")
        write_nuance(sd, nuance_result("b1b"))
        html = p2w.compose_page_html(PART1_BLOCK, gres, nuance=p2w.nuance_for_display(sd, level="b1b"))
        blk = html[html.index(f"<h3>{g.NUANCE_HEADING}</h3>") - len("<section class='study'>"):]
        self.assertTrue(blk.startswith("<section class='study'>") and blk.endswith("</section>"))
        self.assertEqual(blk.count("<section"), 1)                                                   # 独立したsection(文法ブロックに混ぜない)
        for must in ("<h4>at least</h4>", "<b>at least</b>", "At least she was safe.", "少なくとも彼女は無事だった。", "<dt>ポイント</dt>"):
            self.assertIn(must, blk)
        self.assertEqual(g.NUANCE_HEADING, "ニュアンス解説")
        self.assertIsNone(g.PAGE_FORBIDDEN_RE.search(blk))
        # 決定論(同入力で同一HTML)・LLM関数を取らない
        self.assertEqual(html, p2w.compose_page_html(PART1_BLOCK, gres, nuance=p2w.nuance_for_display(sd, level="b1b")))
        self.assertEqual(list(inspect.signature(g.render_nuance_html_block).parameters), ["nuance", "include_css"])


class T2_NuanceSectionVerification(_Fx):
    def test_std_adv_swap_count_mismatch_forbidden_word_and_empty_section_are_detected(self):
        sd_b, paras_b, gres_b = self.make("z", "b1b", "selected")
        sd_a, paras_a, gres_a = self.make("z", "a2", "selected")
        write_nuance(sd_b, nuance_result("b1b", expression="at least"))
        write_nuance(sd_a, nuance_result("a2", expression="should have", quote_en="You should have seen it.", quote_ja="見ておくべきだったね。"))
        html_b = p2w.compose_page_html(PART1_BLOCK, gres_b, nuance=p2w.nuance_for_display(sd_b, level="b1b"))
        html_a = p2w.compose_page_html("", gres_a, nuance=p2w.nuance_for_display(sd_a, level="a2"))
        md_b, md_a = f"{sd_b}/{g.PART2_FILE_STEM}.md", f"{sd_a}/{g.PART2_FILE_STEM}.md"
        ok = lambda sd, paras, lv, md, h: p2w.verify_outputs(sd, paras, LABEL, level=lv, next_command="x", md_path=md, html_text=h)   # noqa: E731
        ok(sd_b, paras_b, "b1b", md_b, html_b)
        ok(sd_a, paras_a, "a2", md_a, html_a)
        nb = g.render_nuance_html_block(p2w.nuance_for_display(sd_b, level="b1b"), include_css=False)
        na = g.render_nuance_html_block(p2w.nuance_for_display(sd_a, level="a2"), include_css=False)
        self.assertNotEqual(nb, na)
        with self.assertRaises(g.Part2Stale):                                                         # Std/Advのニュアンスを取り違えた節
            ok(sd_b, paras_b, "b1b", md_b, html_b.replace(nb, na))
        with self.assertRaises(g.Part2Stale):
            ok(sd_a, paras_a, "a2", md_a, html_a.replace(na, nb))
        with self.assertRaises(g.Part2Stale):                                                         # 採用なのに節に無い(欠落)
            ok(sd_a, paras_a, "a2", md_a, html_a.replace(na, ""))
        with self.assertRaises(g.Part2Stale):                                                         # 節に2個
            ok(sd_a, paras_a, "a2", md_a, html_a + na)
        with self.assertRaises(g.Part2Stale):                                                         # 本文改変(描画不一致)
            ok(sd_a, paras_a, "a2", md_a, html_a.replace("見ておくべきだったね。", "見ておくべきだったよ。"))
        with self.assertRaises(g.Part2Stale):                                                         # 空枠(見出しだけの学習ブロック)
            ok(sd_a, paras_a, "a2", md_a, html_a + f"<section class='study'><h3>{g.NUANCE_HEADING}</h3></section>")
        # 採用以外(不採用)に変えたのに節に残っている
        write_nuance(sd_a, nuance_result("a2", "REJECTED", expression="should have"))
        with self.assertRaises(g.Part2Stale):
            ok(sd_a, paras_a, "a2", md_a, html_a)
        # 採用の表示文にページ非表示語(M-7)
        write_nuance(sd_a, nuance_result("a2", expression="should have", explanation_ja="これは (A2) の説明です。"))
        bad = p2w.compose_page_html("", gres_a, nuance=p2w.nuance_for_display(sd_a, level="a2"))
        with self.assertRaisesRegex(g.Part2Stale, "ページ非表示語"):
            ok(sd_a, paras_a, "a2", md_a, bad)

    def test_nuance_result_loader_is_fail_closed(self):
        sd, paras, gres = self.make("y", "b1b", "selected")
        self.assertIsNone(p2w.nuance_for_display(sd, level="b1b"))                                    # 結果ファイル無し=ニュアンス解説なし(LEGACY/未実施)
        p = f"{sd}/{g.NUANCE_RESULT_FILENAME}"
        with open(p, "w", encoding="utf-8") as f:
            f.write("{broken")
        with self.assertRaises(g.Part2Stale):                                                         # 壊れた結果を黙って『なし』にしない
            p2w.nuance_for_display(sd, level="b1b")
        write_nuance(sd, nuance_result("a2"))
        with self.assertRaises(g.Part2Stale):                                                         # Std結果がAdvのdirにある
            p2w.nuance_for_display(sd, level="b1b")
        write_nuance(sd, nuance_result("b1b", expression=""))
        with self.assertRaises(g.Part2Stale):                                                         # 採用なのに必須項目が欠落=黙って非表示にしない
            g.render_nuance_html_block(p2w.nuance_for_display(sd, level="b1b"))
        with open(p, "w", encoding="utf-8") as f:
            f.write("[]")
        with self.assertRaises(g.Part2Stale):
            p2w.nuance_for_display(sd, level="b1b")


class T3_LegacyZeroMdRetirement(_Fx):
    def test_old_fixed_text_md_is_retired_deterministically_then_verification_requires_no_md(self):
        sd, paras, gres = self.make("z", "b1b", "zero")
        self.assertEqual(g.render_markdown(gres), "")
        md = f"{sd}/{g.PART2_FILE_STEM}.md"
        legacy = "\n".join(["# Grammar & Sentence Structure", "", OLD_ZERO_TEXT, ""])
        with open(md, "w", encoding="utf-8", newline="\n") as f:                                       # 旧仕様が書いていた0件md(バイト一致)
            f.write(legacy)
        out = p2w.verify_outputs(sd, paras, LABEL, level="b1b", next_command="x", md_path=md, html_text="<div></div>")
        self.assertEqual(out, {"grammar_blocks": 0, "nuance_blocks": 0})
        self.assertFalse(os.path.exists(md))
        retired = f"{sd}/{g.PART2_FILE_STEM}{g.LEGACY_ZERO_GRAMMAR_MD_SUFFIX}"
        self.assertEqual(g.LEGACY_ZERO_GRAMMAR_MD_SUFFIX, ".legacy_zero_p2.md")
        with open(retired, encoding="utf-8", newline="") as f:
            self.assertEqual(f.read(), legacy)                                                         # 削除せず逐語で残す
        p2w.verify_outputs(sd, paras, LABEL, level="b1b", next_command="x", md_path=md, html_text="<div></div>")   # 冪等(再検証・ページ再構築を繰り返せる)
        self.assertTrue(os.path.exists(retired))

    def test_non_legacy_md_for_a_zero_result_is_not_hidden_and_fails_verification(self):
        sd, paras, gres = self.make("z", "b1b", "zero")
        md = f"{sd}/{g.PART2_FILE_STEM}.md"
        with open(md, "w", encoding="utf-8", newline="\n") as f:
            f.write("# Grammar & Sentence Structure\n\n手書きの別文面\n")
        with self.assertRaises(g.Part2Stale):                                                          # 0件=md不在を要求(旧固定文面と一致しないmdは退避せず不一致として止める)
            p2w.verify_outputs(sd, paras, LABEL, level="b1b", next_command="x", md_path=md, html_text="<div></div>")
        self.assertTrue(os.path.exists(md))
        os.remove(md)
        # SELECTED結果でmdが無い(欠落)はFileNotFoundErrorではなくPart2Stale
        sd2, paras2, gres2 = self.make("z", "a2", "selected")
        os.remove(f"{sd2}/{g.PART2_FILE_STEM}.md")
        with self.assertRaises(g.Part2Stale):
            p2w.verify_outputs(sd2, paras2, LABEL, level="a2", next_command="x", md_path=f"{sd2}/{g.PART2_FILE_STEM}.md",
                               html_text=f"<div>{g.render_html_block(gres2, include_css=False)}</div>")

    def test_finalize_of_a_zero_result_retires_a_leftover_md_and_never_writes_one(self):
        sd, paras, gres = self.make("x", "b1b", "selected")
        md = f"{sd}/{g.PART2_FILE_STEM}.md"
        self.assertTrue(os.path.exists(md))
        r = g.write_artifacts(sd, None, {"status": "ZERO", "zero_reason": "no_candidate"})            # 0件結果の書出し
        self.assertNotIn("md", r)
        self.assertFalse(os.path.exists(md))
        self.assertTrue(os.path.exists(f"{sd}/{g.PART2_FILE_STEM}.superseded_by_zero.md"))             # SELECTED時代の残骸は退避(削除しない)
        self.assertIsNone(p2w.write_md(sd, {"status": "ZERO"}))                                        # Zのmd書出しも0件は書かない
        self.assertFalse(os.path.exists(md))


class T4_StaticContracts(unittest.TestCase):
    PROD = ("er120_part2_grammar_production_01.py", "er120_part2_wiring_01.py", "er019_family_x_audio_production_runner_01.py", "er019_family_x_listening_page_01.py",
            "er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py", "er128_kp_confirmed_content_01.py", "er128_form_readable_restore_01.py")

    def _src(self, name):
        with open(os.path.join(ROOT, name), encoding="utf-8") as f:
            return f.read()

    def test_zero_p2_fixed_text_is_gone_from_production_modules(self):
        for n in self.PROD:
            s = self._src(n)
            self.assertNotIn("ZERO_P2", s, n)                                                          # R-G3: 撤去(Production module限定)
        # 旧固定文面は『既存0件runの旧mdの退避判定(M-6)』専用の読取定数としてer120 prodに1か所だけ残す
        total = sum(self._src(n).count("特に取り上げる難所") for n in self.PROD)
        self.assertEqual(total, 1)
        self.assertEqual(self._src("er120_part2_grammar_production_01.py").count("特に取り上げる難所"), 1)

    def test_compose_page_html_nuance_is_a_required_keyword_and_every_callsite_passes_it(self):
        sig = inspect.signature(p2w.compose_page_html)
        prm = sig.parameters["nuance"]
        self.assertEqual((prm.kind, prm.default), (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.empty))      # R-6
        self.assertIsNone(inspect.signature(g.compose_study_html).parameters["nuance"].default)                   # 旧testのためNone既定は残す
        for n in ("er019_family_x_audio_production_runner_01.py", "er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py", "er120_part2_wiring_01.py"):
            s = self._src(n)
            calls = [m.start() for m in re.finditer(r"compose_page_html\(", s)]
            for i in calls:
                line = s[i: s.index("\n", i)]
                if "def compose_page_html" in s[max(0, i - 4): i + 40]:
                    continue
                self.assertIn("nuance=", line, f"{n}: {line[:100]}")                                       # R-G4: 渡し漏れ0

    def test_page_verifiers_use_expected_counts_not_exactly_one(self):
        for n in ("er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py"):
            s = self._src(n)
            self.assertNotIn("if n2 != 1", s, n)
            self.assertIn('expect["grammar_blocks"]', s, n)
            self.assertIn('expect["nuance_blocks"]', s, n)
        y = self._src("er121_family_y_runner_01.py")
        self.assertNotIn("section.index(PART2_MARKER)", y)                                              # M-5: 文法0件でValueErrorになる位置比較を撤去
        self.assertIn("_blocks_in_page_order", y)

    def test_y_relative_order_helper_handles_missing_blocks(self):
        import er121_family_y_runner_01 as y
        nm = f"<h3>{g.NUANCE_HEADING}</h3>"
        p1m, p2m = y.PART1_MARKER, y.PART2_MARKER
        self.assertTrue(y._blocks_in_page_order(f"{p1m} {p2m} {nm}", nm))
        self.assertTrue(y._blocks_in_page_order(f"{p1m} {nm}", nm))                                     # 文法0件でも例外にならない
        self.assertTrue(y._blocks_in_page_order(f"{nm}", nm))
        self.assertTrue(y._blocks_in_page_order("", nm))
        self.assertFalse(y._blocks_in_page_order(f"{p2m} {p1m}", nm))
        self.assertFalse(y._blocks_in_page_order(f"{nm} {p2m}", nm))


if __name__ == "__main__":
    unittest.main()
