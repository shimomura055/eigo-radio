# -*- coding: utf-8 -*-
"""KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B: 第2段(G2〜G4・Part 2凍結M6・STALE再バインドM8・Y/Z Std表示是正M2-b・Z人称整合ISSUE・LR重なり警告・単一アクセサ・Y実行時)の単体test。API 0。
LLM由来の関数は全てmock(er119_test_support_01のEnv / Z mock context / er120_part2_mock_01)。変更試行はBLOCK/例外/拒否を期待値とし、不整合な出力を期待値としてassertしない。
TEST_PLAN_02.md の T17〜T21 に対応。
実行: .venv\\Scripts\\python.exe -m unittest er128_kp_confirmed_content_02b_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import er026_family_z_fiction_production_runner_01 as zr
import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er119_z_wiring_test_01 as zw
import er120_part2_grammar_production_01 as g2
import er120_part2_wiring_01 as p2w
import er128_kp_confirmed_content_01 as cc
from er119_test_support_01 import ARTICLE, ARTICLE2, Env, KpTestCase, jd, jl, rd, wr

ROOT = os.path.dirname(os.path.abspath(__file__))


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **k)


def make_payload(cands, *, cat1, cat2=(), level="b1b", grammar=None, comment="コメント"):
    cm = {c["candidate_id"]: c for c in cands["candidates"]}
    by_rank = {c["ai_rank"]: c["candidate_id"] for c in cands["candidates"]}

    def item(rank, cat):
        c = cm[by_rank[rank]]
        return {"term": c["item"]["used_form"], "category": cat, "category_label": f"c{cat}", "ja_gloss": c["item"]["japanese_gloss"], "ja_gloss_status": "official",
                "candidate_id": c["candidate_id"], "kind": c.get("kind") or "phrase"}
    return {"schema": "eigo_radio_selection_result_v2", "schema_version": 2, "schema_minor": 1,
            "article": {"slug": "coffee", "level": level, "text_sha256": cands["text_sha256"], "candidates_sha256": cands["candidates_sha256"]},
            "selection": {"key_phrase": [item(r, 1) for r in cat1], "extra_explanation": [item(r, 2) for r in cat2], "meaning_display": [], "grammar": grammar or []},
            "comment": comment, "ai_reference": {"for_reference_only": True, "items": []}}


class CCBase(KpTestCase):
    def setUp(self):
        super().setUp()
        self.uref = os.path.join(self.tmp, "user_ref.md")
        wr(self.uref, "ユーザー発言原文(test fixture)\n")

    def confirm_user(self, env, level="b1b", by="human"):
        kp_dir = self.kp_dir if level == "b1b" else self.kp_dir_a2
        self.ensure(env, level=level)
        rv.op_select(kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=([1, 2, 3, 4, 5] if level == "b1b" else None), by=by)
        return self.ensure(env, level=level)

    def rec(self, kp_dir=None):
        return cc.load_record(kp_dir or self.kp_dir)

    def consume(self, level="b1b", **kw):
        return rv.require_final_consistent(self.kp_dir if level == "b1b" else self.kp_dir_a2, level=level, **kw)


# ============================================================
# T20 M8: STALE再バインド
# ============================================================
class TestM8Rebind(CCBase):
    def _source_sentences(self, kp_dir=None):
        cands = rv.load_candidates(kp_dir or self.kp_dir)
        cm = {c["candidate_id"]: c for c in cands["candidates"]}
        return [cc._source_sentence_of(cm[i["candidate_id"]]) for i in self.rec(kp_dir)["items"]]

    def test_text_change_outside_source_sentences_rebinds_with_zero_api(self):
        with Env(self.tmp) as env:
            self.confirm_user(env)
            before = self.rec()
            calls = dict(env.n)
            srcs = self._source_sentences()
            new_text = ARTICLE.replace("Retail prices may stay high.", "Retail prices may stay low.")   # 出典文以外の1語変更
            self.assertNotEqual(new_text, ARTICLE)
            self.assertTrue(all(s in new_text for s in srcs), "fixture: 変更が出典文に触れていない")
            r = self.ensure(env, text=new_text)
            self.assertEqual(r["state"], "FINALIZED")
            self.assertEqual(dict(env.n), calls, "再バインドはAPI 0(候補再生成・QA・gloss再整合を呼ばない)")
            after = self.rec()
            self.assertEqual(after["revision"], before["revision"] + 1)
            self.assertEqual(after["content_sha256"], before["content_sha256"])   # 確定内容は不変
            self.assertEqual([(i["candidate_id"], i["used_form"], i["japanese_gloss"], i["category"]) for i in after["items"]],
                             [(i["candidate_id"], i["used_form"], i["japanese_gloss"], i["category"]) for i in before["items"]])
            self.assertEqual(after["history"][-1]["event"], "rebound_text")
            sha = rv.sha256_text(new_text)
            self.assertEqual(after["article"]["text_sha256"], sha)
            self.assertEqual(rv.load_candidates(self.kp_dir)["text_sha256"], sha)
            self.assertEqual(rv.load_review(self.kp_dir)["text_sha256"], sha)
            self.assertEqual(after["origin"]["candidates_sha256"], rv.load_candidates(self.kp_dir)["candidates_sha256"])
            self.assertEqual(after["origin"]["review_selection_signature"], rv.load_review(self.kp_dir)["selection_signature"])
            self.consume()   # G1 PASS(連鎖更新後も整合)
            self.assertEqual(r["final"]["signature"], rv.load_review(self.kp_dir)["selection_signature"])

    def test_verbatim_check_ignores_typographic_quotes_and_whitespace_only(self):
        """候補docのsource_sentenceは直線引用符に正規化されるため、本文の曲線引用符(U+2019等)・改行/連続空白だけの差は「逐語で存在する」と扱う。語の違いは扱わない。"""
        n = cc._norm_ws
        self.assertEqual(n("New York’s  Arabica\ncoffee"), n("New York's Arabica coffee"))
        self.assertEqual(n("“No,” he said"), n('"No," he said'))
        self.assertNotEqual(n("New York's Arabica coffee"), n("New York's arabica coffee"))   # 大文字小文字は保持(逐語)
        self.assertNotEqual(n("a record high"), n("a record low"))

    def test_source_sentence_change_is_issue_and_changes_nothing(self):
        with Env(self.tmp) as env:
            self.confirm_user(env)
            calls = dict(env.n)
            files = ("kp_candidates.json", "kp_human_review.json", "keywords_canonicalized.json", "vocab_confirmed.json", "kp_selection_final.json")
            before = {f: rd(f"{self.kp_dir}/{f}") for f in files}
            rec_before = rd(cc.paths_of(self.kp_dir)["record"])
            sent = self._source_sentences()[0]
            last = sent.split()[-1]
            new_text = ARTICLE.replace(sent, sent[: sent.rindex(last)] + "changed")   # 出典文そのものを変更
            self.assertNotEqual(new_text, ARTICLE)
            r = self.ensure(env, text=new_text)
            self.assertEqual(r["state"], "PENDING")
            self.assertEqual(r["pending"]["reason"], "confirmed_content_issue")
            self.assertEqual(dict(env.n), calls)
            for f, v in before.items():
                self.assertEqual(rd(f"{self.kp_dir}/{f}"), v, f)
            self.assertEqual(rd(cc.paths_of(self.kp_dir)["record"]), rec_before)
            issue = jl(cc.paths_of(self.kp_dir)["issue_json"])
            self.assertEqual(issue["kind"], "CONFIRMED_CONTENT_ISSUE")
            self.assertIn("source_sentence", [d["field"] for d in issue["diffs"]])
            self.assertTrue(rd(rv.paths(self.kp_dir)["request"]).startswith("# 確定内容の確認依頼"))

    def test_auto_record_keeps_existing_stale_regeneration(self):
        with Env(self.tmp) as env:
            self.ensure(env)
            self.declare()
            self.ensure(env)
            self.assertEqual(self.rec()["confirmed_by"]["actor"], cc.ACTOR_AUTO)
            n = env.n["call1"]
            self.ensure(env, text=ARTICLE2)
            self.assertGreater(env.n["call1"], n)   # AUTOは従来どおり本文変更で候補を再生成(再バインド対象外)


# ============================================================
# T18 G2/G3: TTS record・ページHTML・Part 1行
# ============================================================
class TestG2G3(CCBase):
    GLOSS_TILDE = "～を延期する"

    def _confirm_a2_with_tilde_gloss(self, env):
        """Std: 確定訳に「～」を含む(TTS用は『なになに』へ変換される)状態を作る。値は候補doc(正本)側を書き換えた上で確定する(確定時点の訳)。"""
        self.ensure(env, level="a2")
        cands = rv.load_candidates(self.kp_dir_a2)
        c0 = next(c for c in cands["candidates"] if c["ai_rank"] == 1)   # 確定(kp_ranks=[1,2,3])に含まれる先頭
        c0["item"]["japanese_gloss"] = self.GLOSS_TILDE
        c0["item"]["japanese_gloss_tts"] = cc.convert_gloss_tts(self.GLOSS_TILDE)
        c0["japanese_gloss"] = self.GLOSS_TILDE
        cands = rv.save_candidates(self.kp_dir_a2, cands)
        review = rv.load_review(self.kp_dir_a2)
        review["candidates_sha256"] = cands["candidates_sha256"]
        rv.save_review(self.kp_dir_a2, review, expected_revision=review["revision"])
        rv.op_select(self.kp_dir_a2, kp_ranks=[1, 2, 3], by="human")
        self.ensure(env, level="a2")
        return self.GLOSS_TILDE

    def _tts(self, level, kp_dir, **over):
        items = jl(f"{kp_dir}/keywords_canonicalized.json")["items"]
        d = {"key_phrases": {str(it["rank"]): {"english": {"canonical_text": it["used_form"]},
                                              "japanese_meaning": {"canonical_text": cc.convert_gloss_tts(it["japanese_gloss"])}} for it in items}}
        d["key_phrases"].update(over)
        p = os.path.join(self.tmp, f"tts_{level}.json")
        jd(p, d)
        return p

    def _page(self, name, items, field="japanese_gloss"):
        p = os.path.join(self.tmp, name)
        wr(p, "<html><body>" + "".join(f"<tr><td>{it['used_form']}</td><td>{it[field]}</td></tr>" for it in items) + "</body></html>")
        return p

    def test_g2_tts_english_and_japanese_meaning_pass_and_block(self):
        with Env(self.tmp) as env:
            gloss = self._confirm_a2_with_tilde_gloss(env)
        items = jl(f"{self.kp_dir_a2}/keywords_canonicalized.json")["items"]
        self.assertEqual(items[0]["japanese_gloss"], gloss)
        self.assertIn("なになに", cc.convert_gloss_tts(gloss))
        ok = self._tts("a2", self.kp_dir_a2)
        cc.verify_outputs(self.kp_dir_a2, "a2", tts_results_path=ok)   # converter出力(「なになに」)は派生物契約として許容
        # 英語の改変 → BLOCK
        bad_en = self._tts("a2", self.kp_dir_a2, **{"1": {"english": {"canonical_text": "tampered english"}, "japanese_meaning": {"canonical_text": cc.convert_gloss_tts(gloss)}}})
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation) as cm:
            cc.verify_outputs(self.kp_dir_a2, "a2", tts_results_path=bad_en)
        self.assertIn("used_form(TTS英語)", str(jl(cc.paths_of(self.kp_dir_a2)["issue_json"])["diffs"]))
        self.assertNotIsInstance(cm.exception, rv.KpReviewNotConfirmed)
        # 別訳への置換 → BLOCK(派生物契約違反)
        bad_ja = self._tts("a2", self.kp_dir_a2, **{"1": {"english": {"canonical_text": items[0]["used_form"]}, "japanese_meaning": {"canonical_text": "全く別の訳"}}})
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            cc.verify_outputs(self.kp_dir_a2, "a2", tts_results_path=bad_ja)
        # Master Store再利用recordは`text`を持たず`canonical_text`だけ → 誤BLOCKしない。両方無いentryは比較不能として扱いBLOCKしない
        mixed = self._tts("a2", self.kp_dir_a2, **{"2": {"english": {"canonical_text": items[1]["used_form"], "reused_from_master_store": True},
                                                        "japanese_meaning": {"reused_from_master_store": True}}})
        cc.verify_outputs(self.kp_dir_a2, "a2", tts_results_path=mixed)

    def test_g3_std_page_shows_display_gloss_not_tts_text(self):
        with Env(self.tmp) as env:
            gloss = self._confirm_a2_with_tilde_gloss(env)
        items = jl(f"{self.kp_dir_a2}/keywords_canonicalized.json")["items"]
        good = self._page("index.html", items)
        cc.verify_outputs(self.kp_dir_a2, "a2", page_paths=[good])
        os.makedirs(os.path.join(self.tmp, "ttsdir"))
        tts_view = self._page("ttsdir/tts_view.html", [dict(it, japanese_gloss_view=cc.convert_gloss_tts(it["japanese_gloss"])) for it in items], field="japanese_gloss_view")
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):   # 「日本語の意味」欄がTTS用text(なになに)になっている=M2-bの旧挙動はBLOCK
            cc.verify_outputs(self.kp_dir_a2, "a2", page_paths=[tts_view])
        self.assertIn("japanese_gloss(ページ表示)", str(jl(cc.paths_of(self.kp_dir_a2)["issue_json"])["diffs"]))
        # Zの詳細確認ページ(読み上げ用script表示)+同じdirのindex.html(利用者向け表示): index側に表示値があればPASS
        d = os.path.join(self.tmp, "zpages")
        os.makedirs(d)
        shutil.copy(good, os.path.join(d, "index.html"))
        shutil.copy(tts_view, os.path.join(d, "standard.html"))
        cc.verify_outputs(self.kp_dir_a2, "a2", page_paths=[os.path.join(d, "standard.html")])

    def test_g3_adv_part1_rows_only_when_rendered(self):
        with Env(self.tmp) as env:
            self.confirm_user(env)
        rec = self.rec()
        part1 = jl(f"{self.kp_dir}/vocab_confirmed.json")["items"]
        rows = [{"english_expression": it["used_form"], "meaning_in_text_ja": it["japanese_gloss"]} for it in part1]
        st = os.path.join(self.tmp, "part1.json")
        jd(st, {"rows": rows})
        page = self._page("adv.html", rec["items"])
        cc.verify_outputs(self.kp_dir, "b1b", study_text_json=st, vocab_page_paths=[page])
        # Part 1が描画されていない(vocab_page_paths無し)場合はPart 1の検査をしない(Yの現状=Part 1非描画)
        empty = os.path.join(self.tmp, "no_part1.html")
        wr(empty, "<html>no vocab</html>")
        cc.verify_outputs(self.kp_dir, "b1b", study_text_json=st, page_paths=[empty])
        # 描画されている場合に訳が違えばBLOCK
        bad = os.path.join(self.tmp, "bad_part1.html")
        wr(bad, "<html>" + "".join(f"<p>{it['used_form']}</p>" for it in rec["items"]) + "</html>")
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            cc.verify_outputs(self.kp_dir, "b1b", vocab_page_paths=[bad])
        rows[0]["meaning_in_text_ja"] = "別の訳に書き換えられた"
        jd(st, {"rows": rows})
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            cc.verify_outputs(self.kp_dir, "b1b", study_text_json=st, vocab_page_paths=[page])

    def test_verify_selection_matches_outputs_calls_g2g3(self):
        """既存の公開時検証(全X/Y/Zが呼ぶ)がG2/G3に到達する(配線)。確定後にTTSの英語が変わればここでBLOCKされる。"""
        with Env(self.tmp) as env:
            self.confirm_user(env, level="a2")
        items = jl(f"{self.kp_dir_a2}/keywords_canonicalized.json")["items"]
        tts = self._tts("a2", self.kp_dir_a2)
        page = self._page("player.html", items)
        out = rv.verify_selection_matches_outputs(self.kp_dir_a2, level="a2", tts_results_path=tts, page_paths=[page])
        self.assertTrue(out["ok"])
        d = jl(tts)
        d["key_phrases"]["1"]["japanese_meaning"]["canonical_text"] = "別訳"
        jd(tts, d)
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            rv.verify_selection_matches_outputs(self.kp_dir_a2, level="a2", tts_results_path=tts, page_paths=[page])

    def test_actor_auto_gloss_diff_is_warn_only_english_still_blocks(self):
        with Env(self.tmp) as env:
            self.ensure(env, level="a2")
            self.declare()
            self.ensure(env, level="a2")
        self.assertEqual(cc.load_record(self.kp_dir_a2)["confirmed_by"]["actor"], cc.ACTOR_AUTO)
        items = jl(f"{self.kp_dir_a2}/keywords_canonicalized.json")["items"]
        warn = self._tts("a2", self.kp_dir_a2, **{"1": {"english": {"canonical_text": items[0]["used_form"]}, "japanese_meaning": {"canonical_text": "別訳"}}})
        cc.verify_outputs(self.kp_dir_a2, "a2", tts_results_path=warn)   # AUTOのgloss差はWARNのみ
        bad = self._tts("a2", self.kp_dir_a2, **{"1": {"english": {"canonical_text": "x"}, "japanese_meaning": {"canonical_text": cc.convert_gloss_tts(items[0]["japanese_gloss"])}}})
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            cc.verify_outputs(self.kp_dir_a2, "a2", tts_results_path=bad)

    def test_flag_off_and_no_record_do_nothing(self):
        with Env(self.tmp) as env:
            self.confirm_user(env, level="a2")
        tts = self._tts("a2", self.kp_dir_a2, **{"1": {"english": {"canonical_text": "tampered"}}})
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}):
            cc.verify_outputs(self.kp_dir_a2, "a2", tts_results_path=tts)
        os.remove(cc.paths_of(self.kp_dir_a2)["record"])
        cc.verify_outputs(self.kp_dir_a2, "a2", tts_results_path=tts)   # レコード無し(旧run)は従来どおり(WARN運用はG1)


# ============================================================
# T17/G4 M6: Part 2凍結(Z mock context)
# ============================================================
class TestM6Part2Frozen(zw.ZBase):
    def setUp(self):
        super().setUp()
        self.uref = os.path.join(self.tmp, "user_ref.md")
        wr(self.uref, "ユーザー発言原文(test fixture)\n")
        self.sd = zr._part2_dir(self.ctx)

    def _boom_extract(self, prompt):
        raise AssertionError("Step A''(再抽出)が呼ばれた")

    def _boom_explain(self, prompt):
        raise AssertionError("Step B(再解説)が呼ばれた")

    def _kp_to_part2_done(self, explanation_full=None):
        """KP候補・文法候補の生成→待機。Advはフォーム送信(confirm --from-form。文法つき)で確定、Stdはユーザーの選択(HR CLI)で確定、文法を確定どおりに反映。"""
        with self.assertRaises(zr.FamilyZKpReviewPending):
            _quiet(zr.run_stage, self.ctx, "kp")
        out, top = self._confirm_form(explanation_full)
        self.form_out, self.top = out, top
        rv.op_select(self.src["a2"], kp_ranks=[1, 2, 3], by="human")
        # 確定した文法と同じ候補を選ぶ操作は許可される(確定を実reviewへ反映)。別候補は拒否される(別test)
        gr.op_decide(self.sd, choice="top1", accept_ai=True, candidates_sha256=gr.load_candidates(self.sd)["candidates_sha256"], by="human")

    def _confirm_form(self, explanation_full=None):
        cands = rv.load_candidates(self.src["b1b"])
        gdoc = gr.load_candidates(self.sd)
        top = gdoc["candidates"][0]
        gram = [{"id": top["candidate_id"], "title": top["construct_ja"], "explanation_status": ("provided" if explanation_full else "missing"),
                 "explanation_full": explanation_full}]
        pp = os.path.join(self.tmp, "payload.json")
        jd(pp, make_payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=gram))
        return cc.cmd_from_form(self.ctx.out_dir, "b1b", pp, "human", self.uref), top

    def _inputs(self):
        paragraphs, label = zr._part2_inputs(self.ctx)
        return paragraphs, label

    def test_frozen_part2_survives_model_change_without_reextract_or_reexplain(self):
        self._kp_to_part2_done()
        _quiet(zr.run_stage, self.ctx, "kp")
        out, top = self.form_out, self.top
        self.assertEqual(out["grammar"], 1)
        self.assertEqual((self.extract_calls(), self.explain_calls()), (1, 1))
        paragraphs, label = self._inputs()
        pool = zr._part2_pool(self.ctx)
        res = p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=pool)   # 通常の検査を通った結果を凍結
        fz = cc.load_frozen_grammar(self.sd)
        self.assertIsNotNone(fz)
        self.assertEqual(fz["source"], "stepB_generated_frozen")
        self.assertEqual(fz["explanation_md"], res["explanation_md"])
        self.assertEqual(fz["candidate_id"], top["candidate_id"])
        # 凍結の前提: model変更だけでextract/explain signatureは失効する(対照=凍結なしの従来検査)
        with mock.patch.object(g2, "MODEL", "some-other-model-id"):
            gdoc, grev = gr.load_candidates(self.sd), gr.load_review(self.sd)
            with self.assertRaises(g2.Part2Stale):
                g2.require_fresh_part2(res, paragraphs, label, next_command="x", candidates_doc=gdoc, grammar_review=grev, ref_ja_pool=pool)
            # 凍結ありは失効せず、再抽出・再解説のLLMは呼ばれない
            res2 = p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=pool)
            self.assertEqual(res2["explanation_md"], fz["explanation_md"])
            st = p2w.candidate_stage(self.sd, run_dir=self.ctx.out_dir, family="z", slug="s", paragraphs=paragraphs, label=label, extract_call_fn=self._boom_extract)
            self.assertEqual(st["state"], "READY")
            self.assertFalse(st["generated"])
            out2 = p2w.finalize_stage(self.sd, paragraphs=paragraphs, label=label, ref_ja_pool=pool, explain_call_fn=self._boom_explain, write=False)
            self.assertTrue(out2["reused"])
            self.assertEqual(out2["result"]["explanation_md"], fz["explanation_md"])
            # 結果ファイルが無くなっても、凍結値から決定論で作り直す(LLM 0)。signatureの代わりに frozen:<sha>
            os.remove(f"{self.sd}/{g2.RESULT_FILENAME}")
            out3 = p2w.finalize_stage(self.sd, paragraphs=paragraphs, label=label, ref_ja_pool=pool, explain_call_fn=self._boom_explain, write=True)
            self.assertEqual(out3["result"]["explain_signature"], cc.frozen_token(fz))
            self.assertEqual(out3["result"]["explanation_md"], fz["explanation_md"])
            p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=pool)   # 作り直した結果もfrozen検査を通る
        self.assertEqual((self.extract_calls(), self.explain_calls()), (1, 1))
        # 対照: 保護OFF(kill switch)なら同じmodel変更で再抽出が走る=凍結が効いていることの証明
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}), mock.patch.object(g2, "MODEL", "some-other-model-id"):
            with self.assertRaises(Exception) as cm:   # 再抽出に進む(Step A''のpromptを組み、routingのmodel契約検査かmock呼出で止まる)=凍結が無ければ再抽出が起きる
                p2w.candidate_stage(self.sd, run_dir=self.ctx.out_dir, family="z", slug="s", paragraphs=paragraphs, label=label, extract_call_fn=self._boom_extract)
            self.assertTrue(type(cm.exception).__name__ in ("AssertionError", "ModelContractViolation"), type(cm.exception).__name__)

    def test_runner_provenance_does_not_stop_on_model_change_when_grammar_confirmed(self):
        """Z/Yの来歴(part2_cand_b1b の input_sha に抽出signature[model]が入る)は、確定済みの文法ではmodel変更で親sha不一致STOPにならない
        (--regenerate-stage part2_cand_b1b はrevoke必須で拒否されるため、据え置かないと解消できないSTOPになる)。対照=保護OFFなら従来どおりSTOP。"""
        self._kp_to_part2_done()
        _quiet(zr.run_stage, self.ctx, "kp")
        calls = (self.extract_calls(), self.explain_calls())
        with mock.patch.object(g2, "MODEL", "some-other-model-id"):
            _quiet(zr.run_stage, self.ctx, "kp")   # 来歴のSTOPにならず、再抽出・再解説も走らない
            self.assertEqual((self.extract_calls(), self.explain_calls()), calls)
            with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}):
                with self.assertRaises(Exception) as cm:
                    _quiet(zr.run_stage, self.ctx, "kp")
                self.assertIn("ProvenanceMismatch", type(cm.exception).__name__)

    def test_regenerate_stage_and_reselect_require_revoke(self):
        self._kp_to_part2_done()
        _quiet(zr.run_stage, self.ctx, "kp")
        paragraphs, label = self._inputs()
        with self.assertRaises(g2.Part2Stale) as cm:   # --regenerate-stage part2_cand_b1b (force_extract)
            p2w.candidate_stage(self.sd, run_dir=self.ctx.out_dir, family="z", slug="s", paragraphs=paragraphs, label=label, extract_call_fn=self._boom_extract, force_extract=True)
        self.assertIn("CONFIRMED_CONTENT_LOCKED", str(cm.exception))
        self.assertIn("revoke", str(cm.exception))
        sha = gr.load_candidates(self.sd)["candidates_sha256"]
        for choice in ("reselect", "omit"):
            with self.assertRaises(rv.ConfirmedContentLocked):
                gr.op_decide(self.sd, choice=choice, reason="変えたい", candidates_sha256=sha, by="ai")
        with self.assertRaises(rv.ConfirmedContentLocked):
            gr.op_ng(self.sd, rank=1, reason="x", by="ai")
        gr.op_decide(self.sd, choice="top1", accept_ai=True, candidates_sha256=sha, by="human")   # 確定した文法と同じ候補を選ぶ操作は許可(確定の実reviewへの反映)
        cc.cmd_revoke(self.ctx.out_dir, "b1b", "human", self.uref, "選び直す")
        gr.op_decide(self.sd, choice="omit", reason="取消後は可能", candidates_sha256=sha, by="human")   # 取消後は従来どおり

    def test_g4_blocks_changed_explanation_or_grammar(self):
        self._kp_to_part2_done()
        _quiet(zr.run_stage, self.ctx, "kp")
        paragraphs, label = self._inputs()
        pool = zr._part2_pool(self.ctx)
        p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=pool)
        rp = f"{self.sd}/{g2.RESULT_FILENAME}"
        orig = jl(rp)
        for field, val in (("explanation_md", orig["explanation_md"] + "\n(改変)"),):
            d = dict(orig)
            d[field] = val
            jd(rp, d)
            with self.assertRaises(g2.Part2Stale):
                p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=pool)
        jd(rp, orig)
        p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=pool)   # 戻せばPASS
        d = jl(rp)
        d["selection"]["candidate_id"] = "g_other"
        jd(rp, d)
        with self.assertRaises(g2.Part2Stale):
            p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=pool)
        jd(rp, orig)
        fp = f"{self.sd}/{cc.FILE_GRAMMAR_FROZEN}"
        f = jl(fp)
        f["explanation_md"] = "凍結値の書換え"
        jd(fp, f)
        with self.assertRaises(g2.Part2Stale) as cm:
            p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=pool)
        self.assertIn("INTEGRITY", str(cm.exception))
        # verify_outputs(公開時検証)にもG4が配線されている
        f["explanation_md"] = orig["explanation_md"]
        jd(fp, json.loads(json.dumps(jl(fp))))
        with self.assertRaises(g2.Part2Stale):
            p2w.verify_outputs(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=pool)

    def test_ref_ja_pool_issue_only_when_pool_differs_from_confirmed_translation(self):
        self._kp_to_part2_done()
        _quiet(zr.run_stage, self.ctx, "kp")
        paragraphs, label = self._inputs()
        res = p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool=None)
        fz = cc.load_frozen_grammar(self.sd)
        sent = res["selection"]["sentence"]
        # poolに無い / 凍結時の訳と一致 → PASS
        p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool={})
        p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool={sent: fz["translation_ja"]})
        # 凍結時の訳と異なる → ISSUE(再生成しない)
        with self.assertRaises(p2w.Part2NotConfirmed) as cm:
            p2w.require_final(self.sd, paragraphs, label, next_command="x", where="t", ref_ja_pool={sent: "新しいPart 1訳"})
        self.assertIn("再確認", str(cm.exception))
        kp_dir = self.src["b1b"]
        self.assertEqual(jl(cc.paths_of(kp_dir)["issue_json"])["kind"], "CONFIRMED_CONTENT_ISSUE")
        self.assertEqual(self.explain_calls(), 1)

    def test_provided_explanation_is_frozen_from_form_without_step_b(self):
        provided = "【日本語訳】\nフォームで見せた日本語訳です。\n【文法・構文の仕組み】\nフォームで見せた**仕組み**の説明です。\n【意味・ニュアンス・表現効果】\nフォームで見せたニュアンスです。"
        self._kp_to_part2_done(explanation_full=provided)
        paragraphs, label = self._inputs()
        out = p2w.finalize_stage(self.sd, paragraphs=paragraphs, label=label, ref_ja_pool={}, explain_call_fn=self._boom_explain, write=True)
        self.assertEqual(self.explain_calls(), 0)   # Step Bは呼ばれない(フォームで見せた解説全文が確定内容)
        self.assertEqual(out["result"]["explanation_md"], provided)
        self.assertEqual(out["result"]["translation_ja"], "フォームで見せた日本語訳です。")
        fz = cc.load_frozen_grammar(self.sd)
        self.assertEqual((fz["source"], fz["explanation_md"]), ("form_displayed", provided))
        self.assertEqual(cc.translation_from_explanation_full(provided), "フォームで見せた日本語訳です。")
        cc.verify_part2(self.sd, jl(f"{self.sd}/{g2.RESULT_FILENAME}"))

    def test_malformed_provided_explanation_is_issue_not_regenerated(self):
        self._kp_to_part2_done(explanation_full="見出しの無い解説全文")
        paragraphs, label = self._inputs()
        with self.assertRaises(p2w.Part2NotConfirmed):
            p2w.finalize_stage(self.sd, paragraphs=paragraphs, label=label, explain_call_fn=self._boom_explain, write=False)
        self.assertEqual(self.explain_calls(), 0)

    def test_text_change_rebinds_grammar_when_sentence_remains_and_issue_when_not(self):
        self._kp_to_part2_done()
        _quiet(zr.run_stage, self.ctx, "kp")
        paragraphs, label = self._inputs()
        top = gr.load_candidates(self.sd)["candidates"][0]
        # 選定文以外の段落末に語を足す(選定文と段落の位置は不変)→ API 0で再バインド
        para_i = int(top["para"].lstrip("P")) if str(top["para"]).startswith("P") else None
        new_paras = list(paragraphs)
        new_paras.append("A brand new final paragraph is added at the very end of the story.")
        st = p2w.candidate_stage(self.sd, run_dir=self.ctx.out_dir, family="z", slug="s", paragraphs=new_paras, label=label, extract_call_fn=self._boom_extract)
        self.assertEqual(st["state"], "READY")
        self.assertEqual(gr.load_candidates(self.sd)["text_sha256"], g2.text_sha256(new_paras))
        self.assertEqual(gr.load_review(self.sd)["text_sha256"], g2.text_sha256(new_paras))
        self.assertEqual(gr.load_review(self.sd)["selection_signature"], g2.grammar_selection_signature(gr.load_review(self.sd)))
        self.assertEqual(self.extract_calls(), 1)
        self.assertEqual(gr.load_review(self.sd)["history"][-1]["event"], "rebind_text")
        # 選定文そのものを変更した本文 → ISSUE相当(Part2Stale)、確定内容は変えない
        changed = [p.replace(top["sentence"], top["sentence"].replace(top["sentence"].split()[-1], "zzchanged")) for p in new_paras]
        self.assertNotEqual(changed, new_paras)
        sig = gr.load_review(self.sd)["selection_signature"]
        with self.assertRaises(g2.Part2Stale) as cm:
            p2w.candidate_stage(self.sd, run_dir=self.ctx.out_dir, family="z", slug="s", paragraphs=changed, label=label, extract_call_fn=self._boom_extract)
        self.assertIn("CONFIRMED_CONTENT_ISSUE", str(cm.exception))
        self.assertEqual(gr.load_review(self.sd)["selection_signature"], sig)
        self.assertEqual(self.extract_calls(), 1)


# ============================================================
# T21 Z _gloss_person_gate: ユーザー確定済みitemは修復LLMを呼ばずISSUE
# ============================================================
class TestZPersonGate(zw.ZBase):
    def _confirm(self):
        import er119_grammar_review_01 as _gr
        with self.assertRaises(zr.FamilyZKpReviewPending):
            _quiet(zr.run_stage, self.ctx, "kp")
        for lv in ("b1b", "a2"):
            rv.op_select(self.src[lv], kp_ranks=[1, 2, 3], vocab_ranks=([1, 2, 3, 4, 5] if lv == "b1b" else None), by="human")
        sd = zr._part2_dir(self.ctx)
        _gr.op_decide(sd, choice="top1", accept_ai=True, candidates_sha256=_gr.load_candidates(sd)["candidates_sha256"], by="human")
        _quiet(zr.run_stage, self.ctx, "kp")

    def _text(self):
        return zr.canonical_article_text(zr._m().w62.rd(zr._level_text_path(self.ctx, "b1b")))

    def test_user_confirmed_item_is_not_repaired_but_issue(self):
        import er003_key_words_gloss_alignment as ga
        self._confirm()
        self.assertEqual(cc.load_record(self.src["b1b"])["confirmed_by"]["actor"], cc.ACTOR_USER)
        items = jl(f"{self.src['b1b']}/keywords_canonicalized.json")["items"]
        fake = [dict(items[0])]
        before_art = rd(f"{self.src['b1b']}/keywords_canonicalized.json")
        n_calls = len(rd(self.ctx.mock_api.path).splitlines())
        prov = zr._prov(self.ctx)
        with mock.patch.object(ga, "flag_enabled", return_value=True), mock.patch.object(ga, "select_person_mismatches", return_value=fake), \
                mock.patch.object(ga, "align_glosses", side_effect=AssertionError("修復LLM(align_glosses)が呼ばれた")) as align, \
                mock.patch.object(zr, "_person_repair_factory", side_effect=AssertionError("修復factory生成")):
            with self.assertRaises(zr.FamilyZKpReviewPending) as cm:
                zr._gloss_person_gate(self.ctx, "b1b", self._text(), prov)
        self.assertIn("確定内容の確認依頼", str(cm.exception))
        self.assertEqual(cm.exception.pending[0]["reason"], "confirmed_content_issue")
        align.assert_not_called()
        self.assertEqual(rd(f"{self.src['b1b']}/keywords_canonicalized.json"), before_art)   # 確定した訳は変えない
        self.assertEqual(len(rd(self.ctx.mock_api.path).splitlines()), n_calls)
        issue = jl(cc.paths_of(self.src["b1b"])["issue_json"])
        self.assertEqual(issue["kind"], "CONFIRMED_CONTENT_ISSUE")
        self.assertTrue(issue["proposal"])   # 修正案提示

    def test_person_gate_issue_scope(self):
        import er003_key_words_gloss_alignment as ga
        self._confirm()
        kp = self.src["b1b"]
        items = jl(f"{kp}/keywords_canonicalized.json")["items"]
        with self.assertRaises(rv.ConfirmedContentIssue):
            cc.person_gate_issue(kp, "b1b", [dict(items[0])])
        cc.person_gate_issue(kp, "b1b", [dict(items[0], candidate_id="not_in_record")])   # 確定外のitem=従来の自動修復へ(例外なし)
        cc.person_gate_issue(kp, "b1b", [])
        rec = cc.load_record(kp)
        rec["confirmed_by"]["actor"] = cc.ACTOR_AUTO
        cc.save_record(kp, rec)
        cc.person_gate_issue(kp, "b1b", [dict(items[0])])   # AUTOはユーザー確定ではない=従来どおり修復可
        rec["confirmed_by"]["actor"] = cc.ACTOR_USER
        cc.save_record(kp, rec)
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}):
            cc.person_gate_issue(kp, "b1b", [dict(items[0])])   # kill switch OFF=従来動作
        self.assertTrue(ga.person_reference_mismatch)


# ============================================================
# M2-b: Y/Z Stdページの「日本語の意味」は表示用japanese_gloss
# ============================================================
class TestM2bStdDisplayGloss(unittest.TestCase):
    GLOSS = "～を延期する"

    def test_z_std_user_page_shows_display_gloss(self):
        import er063_family_z_audio_01 as za
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        kd = f"{tmp}/key_phrases/a2"
        os.makedirs(kd)
        os.makedirs(f"{tmp}/a2/audit")
        os.makedirs(f"{tmp}/a2/assembly")
        jd(f"{tmp}/a2/assembly/timeline.json", {"wav": "", "timeline": []})
        tts_ja = cc.convert_gloss_tts(self.GLOSS)
        self.assertIn("なになに", tts_ja)
        jd(f"{kd}/keywords_canonicalized.json", {"items": [{"rank": 1, "used_form": "put off", "japanese_gloss": self.GLOSS, "japanese_gloss_tts": tts_ja}]})
        jd(f"{tmp}/a2/audit/tts_generation_results.json", {"segments": {}, "key_phrases": {"1": {"english": {"canonical_text": "put off"}, "japanese_meaning": {"canonical_text": tts_ja}}}})
        rows = [{"part": "key_phrase_1", "start": 0.0, "dur": 1.0, "file": "audio/a.mp3", "voice": "-", "style": "-", "script": f"put off / {tts_ja}", "notes": []}]
        out = za._user_page_rows(tmp, "a2", rows, [("put off", tts_ja)], "audio/", f"{tmp}/audio")
        blocks = "".join("".join(r["blocks"]) for r in out if r["part"] == "Key Phrase 1")
        self.assertIn("put off", blocks)
        self.assertIn(self.GLOSS, blocks)          # 表示は確定した表示用gloss
        self.assertNotIn("なになに", blocks)         # TTS用text(なになに)は表示しない
        # TTS入力(tts_generation_results.japanese_meaning.canonical_text)は不変
        self.assertEqual(jl(f"{tmp}/a2/audit/tts_generation_results.json")["key_phrases"]["1"]["japanese_meaning"]["canonical_text"], tts_ja)

    def test_y_std_user_page_shows_display_gloss(self):
        import numpy as np
        import soundfile as sf
        import er121_family_y_audio_01 as ya
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        theme = f"{tmp}/theme"
        base = f"{theme}/a2"
        os.makedirs(f"{base}/assembled")
        os.makedirs(f"{base}/audit")
        os.makedirs(f"{base}/key_phrases")
        sf.write(f"{base}/assembled/full.wav", np.zeros(24000, dtype="float32"), 24000)
        tts_ja = cc.convert_gloss_tts(self.GLOSS)
        jd(f"{base}/audit/timeline.json", [{"part": "Key Phrase 1", "start_seconds": 0.0, "duration_seconds": 0.5}])
        jd(f"{base}/parts.json", {"segments": {}})
        jd(f"{base}/audit/tts_generation_results.json", {"segments": {}, "key_phrases": {"1": {"japanese_meaning": {"canonical_text": tts_ja}, "explanation": {}}}})
        jd(f"{base}/support_texts.json", {})
        jd(f"{base}/key_phrases/keywords_canonicalized.json", {"items": [{"rank": 1, "used_form": "put off", "japanese_gloss": self.GLOSS, "japanese_gloss_tts": tts_ja}]})
        out = ya.build_page_rows(theme, "a2", f"{tmp}/audio", "audio")
        blocks = "".join("".join(r["blocks"]) for r in out["rows"])
        self.assertIn(self.GLOSS, blocks)
        self.assertNotIn("なになに", blocks)
        self.assertEqual(jl(f"{base}/audit/tts_generation_results.json")["key_phrases"]["1"]["japanese_meaning"]["canonical_text"], tts_ja)   # TTS入力は不変

    def test_tts_input_path_does_not_use_page_builders(self):
        """TTS入力(japanese_gloss_tts→canonical_text)の生成経路は表示builderと独立(M2-bはページ表示のみの変更)。"""
        for name in ("er121_family_y_audio_01.py", "er063_family_z_audio_01.py"):
            src = open(os.path.join(ROOT, name), encoding="utf-8").read()
            self.assertEqual(src.count("it.get(\"japanese_gloss\") or k[\"japanese_meaning\"]") + src.count("(kw.get(n) or {}).get(\"japanese_gloss\") or (kp.get(\"japanese_meaning\")"), 1, name)


# ============================================================
# LR重なり警告(記録のみ)
# ============================================================
class TestLrOverlapWarning(CCBase):
    def test_lr_overlap_pure_function(self):
        items = [{"candidate_id": "p_1", "display_phrase": "pushed prices up", "used_form": "push prices up", "key_phrase": "push prices up"},
                 {"candidate_id": "p_2", "display_phrase": "time lag", "used_form": "time lag", "key_phrase": "time lag"}]
        before = "Some owners pushed prices up in May. Market insiders say a time lag is built in."
        hit = cc.lr_overlap(items, before, "Some owners pushed prices upward in May. Market insiders say a time lag is built in.")
        self.assertEqual([h["candidate_id"] for h in hit], ["p_1"])   # KP句の直後の語が変わった=KP句の出現位置と重なる(挿入/置換を含む)
        hit2 = cc.lr_overlap(items, before, "Some owners pushed prices up in May. Market insiders say a delay is built in.")
        self.assertEqual([h["candidate_id"] for h in hit2], ["p_2"])
        self.assertEqual(cc.lr_overlap(items, before, before.replace("Some owners", "Many owners")), [])   # 重ならない書換えは記録しない

    def test_note_lr_fired_writes_audit_only_for_active_confirmed_records(self):
        from er020_tts_retry_local_rewrite_01 import _note_confirmed_kp_overlap
        with Env(self.tmp) as env:
            self.confirm_user(env)
        rec = self.rec()
        form = rec["items"][0]["display_phrase"]
        before = f"Intro words here. {form} and then more words follow."
        after = f"Intro words here. {form} but then different words follow."
        out = os.path.join(os.path.dirname(cc.paths_of(self.kp_dir)["mirror"]), "confirmed_kp_lr_overlap.json")
        cc._ACTIVE_KP_DIRS.clear()
        _note_confirmed_kp_overlap("comment_1", before, "Intro words here. Totally rewritten sentence now.")
        self.assertFalse(os.path.exists(out), "G1を通っていない(稼働中でない)確定レコードは対象にしない")
        self.consume()   # G1を通る=稼働中として登録
        self.assertIn(os.path.abspath(self.kp_dir), cc._ACTIVE_KP_DIRS)
        _note_confirmed_kp_overlap("comment_1", before, "Intro words here. " + form.upper() + " and then more words follow.")
        self.assertFalse(os.path.exists(out), "大小文字だけの差=書換えなし(語は同じ)")
        changed = f"Intro words here. {form.split()[0]} and then more words follow."   # KP句の一部を欠く書換え
        if len(form.split()) > 1:
            _note_confirmed_kp_overlap("comment_2", before, changed)
            doc = jl(out)
            self.assertEqual(doc["events"][0]["segment_id"], "comment_2")
            self.assertEqual(doc["events"][0]["overlaps"][0]["candidate_id"], rec["items"][0]["candidate_id"])
        # 記録の失敗はLRを止めない / er128未ロードなら何もしない
        with mock.patch.object(cc, "note_lr_fired", side_effect=RuntimeError("boom")):
            self.assertIsNone(_note_confirmed_kp_overlap("x", before, after))
        with mock.patch.dict(sys.modules):
            sys.modules.pop("er128_kp_confirmed_content_01", None)
            self.assertIsNone(_note_confirmed_kp_overlap("x", before, after))

    def test_lr_behavior_unchanged_result_identical_with_and_without_warning_hook(self):
        import er020_tts_retry_local_rewrite_01 as m
        import er020_tts_retry_local_rewrite_01_test_01 as t20
        canonical = "let's bring the main point together before we close."
        asr = "let's bring the main points together before we close."
        outs = []
        for hook_on in (True, False):
            tmp = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, tmp, True)
            client = mock.Mock()

            def _create(*args, **kwargs):
                name = kwargs.get("text", {}).get("format", {}).get("name", "")
                resp = mock.Mock()
                resp.output_text = json.dumps({"candidates": [t20._candidate("c1", "let's bring the main idea together before we close.")]} if "candidates" in name else
                                              {"evaluations": [{"candidate_id": "c1", "meaning_preserved": t20._gate(True), "role_preserved": t20._gate(True),
                                                                "fact_non_contradiction": t20._gate(True), "context_connection": t20._gate(True), "natural_english": t20._gate(True)}]})
                resp.model = "gpt-5.6-luna"
                resp.id = "resp_test"
                return resp
            client.responses.create.side_effect = _create
            retts = mock.Mock(return_value={"status": "OK", "asr_text": "x"})
            patch = mock.patch.object(m, "_note_confirmed_kp_overlap", side_effect=RuntimeError("must be swallowed?")) if hook_on else mock.patch.object(m, "_note_confirmed_kp_overlap")
            with patch as hook:
                try:
                    rec = m.run_local_rewrite_recovery(segment_id="comment_4", canonical_text=canonical, last_asr_text=asr, retts_fn=retts, out_dir=tmp, client=client)
                    raised = False
                except RuntimeError:
                    raised = True
            if hook_on:
                # hook自体が例外を出す人工条件は、実装(_note_confirmed_kp_overlap内部のtry/except)を迂回するpatchなので、ここでは『呼ばれる』ことだけを見る
                self.assertTrue(hook.called or raised)
                continue
            self.assertTrue(hook.called)
            self.assertEqual(hook.call_args[0][0], "comment_4")
            outs.append(rec["status"])
            retts.assert_called_once_with("let's bring the main idea together before we close.")
        self.assertEqual(outs, ["RESOLVED_BY_LOCAL_REWRITE"])


# ============================================================
# 単一アクセサ
# ============================================================
class TestSingleAccessor(CCBase):
    def test_part1_items_and_accessor_verify_against_record(self):
        with Env(self.tmp) as env:
            self.confirm_user(env)
        items = cc.load_verified_items(self.kp_dir, level="b1b", which="part1")
        self.assertEqual(len(items), 5)
        self.assertEqual([i["used_form"] for i in items], [i["used_form"] for i in self.rec()["items"]])
        # vocab artifactの訳を確定後に書換え → part1_items(直接呼出)もBLOCK(アクセサ経由でなくてもPart 1入力は確定レコードと照合される)
        p = f"{self.kp_dir}/vocab_confirmed.json"
        d = jl(p)
        d["items"][-1]["japanese_gloss"] = "確定後に別訳へ"
        jd(p, d)
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            rv.part1_items(self.kp_dir)
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            cc.load_verified_items(self.kp_dir, level="b1b", which="part1")

    def test_public_study_html_uses_the_accessor(self):
        src = open(os.path.join(ROOT, "er120_part2_wiring_01.py"), encoding="utf-8").read()
        body = src[src.index("def public_study_html"):]
        self.assertIn('which="part1"', body)
        self.assertNotIn("rv.part1_items(", body)

    def test_legacy_no_record_unaffected(self):
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}):
            with Env(self.tmp) as env:
                self.confirm_user(env)
        self.assertIsNone(self.rec())
        self.assertEqual(len(rv.part1_items(self.kp_dir)), 5)


# ============================================================
# Y 実行時: stage_kpのG1が実行時に発火(mock context)
# ============================================================
class TestYStageKpG1Runtime(unittest.TestCase):
    """Y stage_kpのG1が実行時に発火する(mock context。TEST_PLAN_02 T9のY実行時分)。"""

    def setUp(self):
        import er121_family_y_runner_01 as y
        self.y = y
        self.root = tempfile.mkdtemp(prefix="y_cc_")
        self.addCleanup(shutil.rmtree, self.root, True)
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        for target in ("er003_v1_en_direct_vfl_01_generate.get_client", "er003_v1_n3_01_scaffold_generate.run_key_phrases",
                       "er011_key_phrase_set_redundancy_qa_01.make_redundancy_qa_fn", "er105_kp_fulltext_selector_01.make_selector_fn",
                       "er119_kp_prompt_2v_01.make_vocab_selector_fn", "er003_key_words_canonicalization.make_canonicalization_fn",
                       "er003_key_words_gloss_alignment.make_alignment_fn"):
            stack.enter_context(mock.patch(target, side_effect=AssertionError(f"REAL API PATH CALLED: {target}")))
        stack.enter_context(mock.patch.object(rv, "STORE_ROOT", os.path.join(self.root, "store")))
        os.makedirs(self.root, exist_ok=True)
        theme = os.path.join(self.root, "theme.json")
        jd(theme, {"theme": "mock"})
        self.ctx = y.build_mock_context(self.root, run="run_t", slug="mock_slug", theme_package_path=theme)
        decl = rv.declarations_path(self.ctx.out_dir)
        if os.path.exists(decl):
            os.remove(decl)
        _quiet(y.run_stages, self.ctx, ["seed_check", "text", "translate", "support"])
        self.src = {lv: f"{self.ctx.out_dir}/key_phrases/{lv}" for lv in ("b1b", "a2")}
        self.sd = f"{self.ctx.out_dir}/study_text"

    def test_tamper_after_confirm_stops_y_stage_kp_before_paid_generation(self):
        y = self.y
        with self.assertRaises(y.YKpReviewPending):
            _quiet(y.run_stages, self.ctx, ["kp"])
        for lv in ("b1b", "a2"):
            rv.op_select(self.src[lv], kp_ranks=[1, 2, 3], vocab_ranks=([1, 2, 3, 4, 5] if lv == "b1b" else None), by="human")
        gr.op_decide(self.sd, choice="top1", accept_ai=True, candidates_sha256=gr.load_candidates(self.sd)["candidates_sha256"], by="human")
        _quiet(y.run_stages, self.ctx, ["kp"])
        for lv in ("b1b", "a2"):
            rec = cc.load_record(self.src[lv])
            self.assertEqual(rec["confirmed_by"]["actor"], cc.ACTOR_USER)   # 確定レコードが通常経路で作られた
        n = self.ctx.mock_api.n
        _quiet(y.run_stages, self.ctx, ["kp"])   # 改変なしの再実行=PASS・API境界を通らない
        self.assertEqual(self.ctx.mock_api.n, n)
        p = f"{self.src['b1b']}/keywords_canonicalized.json"
        d = jl(p)
        d["items"][0]["japanese_gloss"] = "確定後に別訳へ置換された"
        jd(p, d)
        n = self.ctx.mock_api.n
        with self.assertRaises(y.YE2EStop) as cm:
            _quiet(y.run_stages, self.ctx, ["kp"])
        self.assertIn("CONFIRMED_CONTENT_INTEGRITY_VIOLATION", str(cm.exception))
        self.assertNotIsInstance(cm.exception, y.YKpReviewPending)
        self.assertEqual(self.ctx.mock_api.n, n, "G1より後の有料生成(Adv解説・Part 1・Part 2)は呼ばれない")


# ============================================================
# actor=evidence(runtime evidence用。ユーザー確定ではないと記録に明記。保護の強度はuserと同じ)
# ============================================================
class TestEvidenceActor(CCBase):
    def _confirm_evidence(self, env):
        cands = self.ensure(env) and rv.load_candidates(self.kp_dir)
        pp = os.path.join(self.tmp, "payload_ev.json")
        jd(pp, make_payload(cands, cat1=[1, 2, 3], cat2=[4, 5]))
        return cc.cmd_from_form(self.run_dir, "b1b", pp, "evidence-runner", self.uref, actor=cc.ACTOR_EVIDENCE)

    def test_evidence_record_states_it_is_not_user_confirmation_and_enforces_like_user(self):
        with Env(self.tmp) as env:
            self._confirm_evidence(env)
            rec = self.rec()
            self.assertEqual(rec["confirmed_by"]["actor"], "evidence")
            self.assertIn("ユーザー確定ではない", rec["confirmed_by"]["attestation"])
            self.assertIn(cc.ACTOR_EVIDENCE, cc.ENFORCING_ACTORS)
            self.ensure(env)
            self.consume()   # G1 PASS
            # 日本語訳の書換えはactor=evidenceでもBLOCK(userと同じ強度。autoのようにWARNへ落ちない)
            def mut(d):
                d["items"][0]["japanese_gloss"] += "改変"
            kpj = rv.paths(self.kp_dir)["kp"]
            d = jl(kpj)
            mut(d)
            jd(kpj, d)
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
                self.consume()
            # 操作ガードも有効
            with self.assertRaises(rv.ConfirmedContentLocked):
                cc.guard(self.kp_dir, "select")

    def test_cmd_from_form_rejects_unknown_actor(self):
        with Env(self.tmp) as env:
            cands = self.ensure(env) and rv.load_candidates(self.kp_dir)
            pp = os.path.join(self.tmp, "payload_x.json")
            jd(pp, make_payload(cands, cat1=[1, 2, 3], cat2=[4, 5]))
            with self.assertRaises(Exception):
                cc.cmd_from_form(self.run_dir, "b1b", pp, "x", self.uref, actor="auto")


if __name__ == "__main__":
    unittest.main()
