# -*- coding: utf-8 -*-
"""KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02A: 確定内容保護(共通核 er128 + er119フック + Y/Z stage_kp G1)の単体test。API 0。
LLM由来の関数は全てmock(er119_test_support_01のEnv。Z/Yはmock context+実API到達即失敗)。変更試行はBLOCK/例外/拒否を期待値とする
(不整合な出力を期待値としてassertしない)。DESIGN_02.md の M1〜M9 に対応。
実行: .venv\\Scripts\\python.exe -m unittest er128_kp_confirmed_content_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import contextlib
import copy
import io
import json
import os
import re
import shutil
import tempfile
import types
import unittest
from unittest import mock

import er119_kp_human_review_01 as rv
import er128_kp_confirmed_content_01 as cc
from er119_test_support_01 import ARTICLE, ARTICLE2, Env, KpTestCase, jd, jl, rd, wr

ROOT = os.path.dirname(os.path.abspath(__file__))


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **k)


class CCBase(KpTestCase):
    """b1b(Adv: KP3+単語2)を user select で確定するfixture。"""

    def setUp(self):
        super().setUp()
        self.uref = os.path.join(self.tmp, "user_ref.md")
        wr(self.uref, "ユーザー発言原文(test fixture)\n")

    def confirm_user(self, env, level="b1b", by="human"):
        kp_dir = self.kp_dir if level == "b1b" else self.kp_dir_a2
        self.ensure(env, level=level)
        rv.op_select(kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=([1, 2, 3, 4, 5] if level == "b1b" else None), by=by)
        return self.ensure(env, level=level)

    def confirm_auto(self, env, level="b1b"):
        self.ensure(env, level=level)
        self.declare()
        return self.ensure(env, level=level)

    def rec(self, kp_dir=None):
        return cc.load_record(kp_dir or self.kp_dir)

    def patch_art(self, fn, name="keywords_canonicalized.json", kp_dir=None):
        p = f"{kp_dir or self.kp_dir}/{name}"
        d = jl(p)
        fn(d)
        jd(p, d)

    def consume(self, level="b1b", **kw):
        return rv.require_final_consistent(self.kp_dir if level == "b1b" else self.kp_dir_a2, level=level, **kw)


# ============================================================
# T1 レコード生成(HR CLI/AUTO)・ミラー・sha・hash chain
# ============================================================
class TestRecordCreation(CCBase):
    def test_hr_cli_select_creates_record_and_mirror(self):
        with Env(self.tmp) as env:
            r = self.confirm_user(env)
        self.assertEqual(r["state"], "FINALIZED")
        rec = self.rec()
        self.assertEqual(rec["schema"], cc.SCHEMA)
        self.assertEqual(rec["state"], cc.STATE_LIVE)
        self.assertEqual(rec["confirmed_by"]["actor"], cc.ACTOR_USER)
        self.assertEqual(rec["origin"]["kind"], "hr_cli")
        self.assertEqual([(i["category"], i["slot"]) for i in rec["items"]], [(1, "kp")] * 3 + [(2, "vocab")] * 2)   # ①=kp ②=vocab\kp
        cm = {c["candidate_id"]: c for c in rv.load_candidates(self.kp_dir)["candidates"]}
        self.assertTrue(all(i["kind"] in ("phrase", "word") and i["kind"] == (cm[i["candidate_id"]].get("kind") or "phrase") for i in rec["items"]))   # kindは必須・候補docの値(7+5対応)
        self.assertEqual(cc.record_sha256(rec), rec["record_sha256"])
        self.assertEqual(cc.content_sha256(rec["items"]), rec["content_sha256"])
        self.assertEqual(cc._problems_self(rec), [])
        mirror = cc.paths_of(self.kp_dir)["mirror"]
        self.assertTrue(mirror.endswith(os.path.join("b1b", "audit", "confirmed_selection.json")))
        self.assertEqual(jl(mirror)["record_sha256"], rec["record_sha256"])
        self.assertEqual(rec["history"][0]["prev_entry_sha256"], None)
        self.assertEqual(rec["history"][0]["event"], "confirmed")
        self.consume()   # G1 PASS

    def test_values_come_from_candidate_doc(self):
        with Env(self.tmp) as env:
            self.confirm_user(env)
        cands = rv.load_candidates(self.kp_dir)
        cm = {c["candidate_id"]: c for c in cands["candidates"]}
        for it in self.rec()["items"]:
            self.assertEqual(it["japanese_gloss"], cm[it["candidate_id"]]["item"]["japanese_gloss"])
            self.assertEqual(it["used_form"], cm[it["candidate_id"]]["item"]["used_form"])
            self.assertEqual(it["derived"]["japanese_gloss_tts"], cm[it["candidate_id"]]["item"]["japanese_gloss_tts"])
            self.assertTrue(it["derived"]["converter_id"].startswith("convert_display_gloss_to_tts_text/"))

    def test_auto_declaration_creates_non_user_record(self):
        with Env(self.tmp) as env:
            self.confirm_auto(env)
        rec = self.rec()
        self.assertEqual(rec["confirmed_by"]["actor"], cc.ACTOR_AUTO)   # AUTOは『ユーザー確定ではない』
        self.assertEqual(rec["origin"]["kind"], "auto_declared")
        self.consume()

    def test_std_level_record_has_kp_only(self):
        with Env(self.tmp) as env:
            self.confirm_user(env, level="a2")
        rec = cc.load_record(self.kp_dir_a2)
        self.assertEqual([i["slot"] for i in rec["items"]], ["kp"] * 3)
        self.assertTrue(cc.paths_of(self.kp_dir_a2)["mirror"].endswith(os.path.join("a2", "audit", "confirmed_selection.json")))

    def test_idempotent_rerun_does_not_touch_record(self):
        with Env(self.tmp) as env:
            self.confirm_user(env)
            before = rd(cc.paths_of(self.kp_dir)["record"])
            self.ensure(env)
            self.ensure(env)
        self.assertEqual(rd(cc.paths_of(self.kp_dir)["record"]), before)


# ============================================================
# T3〜T6 G1: 改変BLOCK(英語・日本語訳・assets copy・ミラー・レコード・chain・コメント・payload原文)
# ============================================================
class TestG1Tamper(CCBase):
    def setUp(self):
        super().setUp()
        with Env(self.tmp) as env:
            self.confirm_user(env)

    def assertIntegrity(self, fn=None, **kw):
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation) as cm:
            self.consume(**kw)
        self.assertNotIsInstance(cm.exception, rv.KpReviewNotConfirmed)   # INTEGRITYは待機(rc=4)ではなくSTOP側
        self.assertIsInstance(cm.exception, rv.KpReviewInconsistent)
        self.assertTrue(os.path.exists(cc.paths_of(self.kp_dir)["issue_json"]))
        return cm.exception

    def test_english_tamper_blocks(self):
        self.patch_art(lambda d: d["items"][0].update(used_form=d["items"][0]["used_form"] + " x"))
        e = self.assertIntegrity()
        self.assertIn("restore", str(e))

    def test_gloss_replacement_blocks_for_user_confirmed(self):
        """現行は素通り(IDのみ比較)だった穴(R-06)の回帰test: 別訳への置換をBLOCK。"""
        self.patch_art(lambda d: d["items"][1].update(japanese_gloss="別の訳"))
        self.assertIntegrity()

    def test_tts_text_replacement_blocks_but_pure_conversion_is_derived_ok(self):
        self.patch_art(lambda d: d["items"][0].update(japanese_gloss_tts="全く別の読み上げ"))
        self.assertIntegrity()

    def test_derived_contract_allows_converter_output_of_confirmed_gloss(self):
        ri = {"candidate_id": "p_x", "slot": "kp", "used_form": "a b", "display_phrase": "a b", "key_phrase": "a b", "japanese_gloss": "～を意味する",
              "derived": {"japanese_gloss_tts": "旧変換結果"}}
        art = dict(ri, japanese_gloss_tts=cc.convert_gloss_tts("～を意味する"))
        b, w = cc._item_diffs(ri, art, "t", enforce_gloss=True)
        self.assertEqual((b, w), ([], []))                       # 現行converterの出力はOK(読み上げ規則の正当な改善を誤BLOCKしない=M2-a)
        art2 = dict(ri, japanese_gloss_tts="旧変換結果")
        self.assertEqual(cc._item_diffs(ri, art2, "t", enforce_gloss=True), ([], []))   # 記録済み派生値もOK
        art3 = dict(ri, japanese_gloss_tts="別訳")
        self.assertTrue(cc._item_diffs(ri, art3, "t", enforce_gloss=True)[0])             # 別訳への置換はBLOCK
        self.assertEqual(cc.convert_gloss_tts("～を意味する"), "なになにを意味する")

    def test_japanese_gloss_tts_is_not_in_protected_fields(self):
        self.assertNotIn("japanese_gloss_tts", cc.PROTECTED_ITEM_FIELDS)
        self.assertIn("japanese_gloss", cc.PROTECTED_ITEM_FIELDS)
        self.assertEqual(cc.content_sha256(self.rec()["items"]), self.rec()["content_sha256"])

    def test_assets_copy_gloss_divergence_blocks_and_missing_item_is_runner_side(self):
        asset = os.path.join(self.tmp, "assets", "keywords_canonicalized.json")
        os.makedirs(os.path.dirname(asset), exist_ok=True)
        shutil.copyfile(f"{self.kp_dir}/keywords_canonicalized.json", asset)
        self.consume(assets_json=asset)   # 一致=PASS
        d = jl(asset)
        d["items"][0]["japanese_gloss"] = "assetsだけ別訳"
        jd(asset, d)
        self.assertIntegrity(assets_json=asset)
        d = jl(asset)
        d["items"] = d["items"][1:]
        jd(asset, d)
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):   # 他itemのずれは検出
            d["items"][0]["japanese_gloss"] = "x"
            jd(asset, d)
            self.consume(assets_json=asset)

    def test_mirror_mismatch_blocks(self):
        m = cc.paths_of(self.kp_dir)["mirror"]
        d = jl(m)
        d["comment"] = "改変"
        jd(m, d)
        self.assertIntegrity()
        os.remove(m)
        self.assertIntegrity()

    def test_record_hand_edit_blocks(self):
        p = cc.paths_of(self.kp_dir)["record"]
        d = jl(p)
        d["items"][0]["japanese_gloss"] = "手編集"
        jd(p, d)
        self.assertIntegrity()

    def test_record_rewrite_with_recomputed_shas_still_blocks_via_candidate_doc_anchor(self):
        """M5b: AIがレコードを書換えてshaを再計算しても、候補doc(自己sha保護)の値と食い違えばBLOCK。"""
        p = cc.paths_of(self.kp_dir)["record"]
        d = jl(p)
        d["items"][0]["japanese_gloss"] = "再計算済みの偽の確定訳"
        d["content_sha256"] = cc.content_sha256(d["items"])
        d["history"][-1]["content_sha256"] = d["content_sha256"]
        d["history"][-1]["entry_sha256"] = cc._entry_sha(d["history"][-1])
        cc.save_record(self.kp_dir, d)   # record_sha256・ミラーも再計算して一致させる
        self.patch_art(lambda x: x["items"][0].update(japanese_gloss="再計算済みの偽の確定訳"))   # 成果物もレコードに合わせる
        e = self.assertIntegrity()
        self.assertIn("候補doc", str(e) + rd(cc.paths_of(self.kp_dir)["issue_json"]))

    def test_history_chain_break_blocks(self):
        p = cc.paths_of(self.kp_dir)["record"]
        d = jl(p)
        d["history"][0]["reason"] = "書換え"
        d["record_sha256"] = cc.record_sha256(d)
        jd(p, d)
        jd(cc.paths_of(self.kp_dir)["mirror"], d)
        self.assertIntegrity()

    def test_user_comment_tamper_detected_via_user_note_sha(self):
        p = cc.paths_of(self.kp_dir)["record"]
        d = jl(p)
        d["comment"] = "後から足したコメント"
        d["record_sha256"] = cc.record_sha256(d)
        jd(p, d)
        jd(cc.paths_of(self.kp_dir)["mirror"], d)
        self.assertIntegrity()

    def test_candidates_doc_swap_blocks(self):
        cp = rv.paths(self.kp_dir)["candidates"]
        c = jl(cp)
        c["candidates"][0]["item"]["japanese_gloss"] = "候補docの差替え"
        jd(cp, c)   # 自己shaが合わない→既存検査(KP_CANDIDATES_SIGNATURE_MISMATCH)でSTOP(確定内容保護の前段)
        with self.assertRaises(rv.KpReviewInconsistent):
            self.consume()

    def test_review_signature_changed_behind_record_blocks(self):
        rp = rv.paths(self.kp_dir)["review"]
        r = jl(rp)
        r["selection_signature"] = "0" * 64
        jd(rp, r)
        with self.assertRaises(rv.KpReviewInconsistent):   # 既存署名検査 or 確定レコード照合のどちらでも止まる
            self.consume()


class TestG1ActorAuto(CCBase):
    def test_auto_actor_english_change_blocks_but_gloss_change_is_warn_only(self):
        """AUTO(ユーザー確定ではない)は既存の人称整合repair等でglossが変わり得るため、gloss差はWARN(診断ファイル)。英語・区分は不変検査。"""
        with Env(self.tmp) as env:
            self.confirm_auto(env)
        self.patch_art(lambda d: d["items"][0].update(japanese_gloss="パイプライン内の修復後gloss"))
        self.consume()   # raiseしない
        self.assertTrue(os.path.exists(cc.paths_of(self.kp_dir)["legacy"]))
        self.patch_art(lambda d: d["items"][0].update(used_form="changed phrase"))
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            self.consume()


# ============================================================
# T7 操作ガード(M4)
# ============================================================
class TestOperationGuards(CCBase):
    def setUp(self):
        super().setUp()
        with Env(self.tmp) as env:
            self.confirm_user(env)

    def test_all_selection_rewriting_ops_refused_for_user_confirmed(self):
        k = self.kp_dir
        for name, fn in (("select", lambda: rv.op_select(k, kp_ranks=[4, 5, 6], vocab_ranks=[4, 5, 6, 7, 8], by="fable-ai")),
                         ("accept-ai", lambda: rv.op_select(k, kp_ranks=[], accept_ai=True, shown_candidates_sha256=rv.load_candidates(k)["candidates_sha256"], by="fable-ai")),
                         ("reselect", lambda: rv.op_reselect(k, by="fable-ai")),
                         ("ng", lambda: rv.op_ng(k, ng={4: "r"}, by="fable-ai")),
                         ("unng", lambda: rv.op_unng(k, rank=4, reason="r", by="fable-ai")),
                         ("resolve-gloss", lambda: rv.op_resolve_gloss(k, rank=1, gloss="x", by="fable-ai")),
                         ("declare-absent", lambda: rv.add_declaration(run_dirs=[self.run_dir], by="fable-ai", reason="r", user_ref="u"))):
            with self.subTest(name):
                with self.assertRaises(rv.ConfirmedContentLocked) as cm:
                    fn()
                self.assertIn("confirm-revise", str(cm.exception))
                self.assertIn("revoke", str(cm.exception))
        # 拒否後も状態不変
        self.assertEqual(rv.load_review(k)["status"], rv.ST_REVIEWED)
        self.assertEqual(self.rec()["revision"], 1)

    def test_revoke_requires_user_ref_and_unblocks(self):
        with self.assertRaises(cc.CliError):
            cc.cmd_revoke(self.run_dir, "b1b", "fable-ai", "", "理由")
        with self.assertRaises(cc.CliError):
            cc.cmd_revoke(self.run_dir, "b1b", "fable-ai", os.path.join(self.tmp, "nonexistent.md"), "理由")
        out = cc.cmd_revoke(self.run_dir, "b1b", "fable-ai", self.uref, "ユーザー指示で選び直し")
        self.assertTrue(out["revoked"])
        self.assertEqual(self.rec()["state"], cc.STATE_REVOKED)
        rv.op_reselect(self.kp_dir, by="human")   # 取消後は可能
        self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_RESELECT)

    def test_auto_record_does_not_block_human_select_and_upgrades_to_user(self):
        shutil.rmtree(self.tmp + "/run1")
        with Env(self.tmp) as env:
            self.confirm_auto(env)
            self.assertEqual(self.rec()["confirmed_by"]["actor"], cc.ACTOR_AUTO)
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3, 4, 5], by="human")   # 事後Review(許可)
            self.ensure(env)
        rec = self.rec()
        self.assertEqual((rec["confirmed_by"]["actor"], rec["revision"]), (cc.ACTOR_USER, 2))
        self.assertEqual([h["event"] for h in rec["history"]], ["auto_adopted", "confirmed"])
        self.assertEqual(cc._problems_self(rec), [])


# ============================================================
# M-3 例外クラス(ISSUE=rc=4待機系 / INTEGRITY=rc=3 STOP系)
# ============================================================
class TestExceptionClasses(unittest.TestCase):
    def test_hierarchy(self):
        self.assertTrue(issubclass(rv.ConfirmedContentIssue, rv.KpReviewNotConfirmed))
        self.assertTrue(issubclass(rv.ConfirmedContentIntegrityViolation, rv.KpReviewInconsistent))
        self.assertFalse(issubclass(rv.ConfirmedContentIntegrityViolation, rv.KpReviewNotConfirmed))
        self.assertTrue(issubclass(rv.ConfirmedContentLocked, rv.KpReviewError))

    def test_runner_mappings(self):
        import er026_family_z_fiction_production_runner_01 as z
        import er121_family_y_runner_01 as y
        yctx = types.SimpleNamespace(out_dir="Y_OUT")
        zctx = types.SimpleNamespace(out_dir="Z_OUT")
        issue = rv.ConfirmedContentIssue("x", kp_dir="d", issue_path="p")
        integ = rv.ConfirmedContentIntegrityViolation("y")
        with mock.patch.object(rv, "require_final_consistent", side_effect=issue):
            with self.assertRaises(y.YKpReviewPending):
                y._assert_kp_review_consistent(yctx, "b1b", "t")
            with self.assertRaises(z.FamilyZKpReviewPending):
                z._assert_kp_review_consistent(zctx, "b1b", "t")
        with mock.patch.object(rv, "require_final_consistent", side_effect=integ):
            with self.assertRaises(y.YE2EStop) as c1:
                y._assert_kp_review_consistent(yctx, "b1b", "t")
            self.assertNotIsInstance(c1.exception, y.YKpReviewPending)
            with self.assertRaises(z.FamilyZE2EStop) as c2:
                z._assert_kp_review_consistent(zctx, "b1b", "t")
            self.assertNotIsInstance(c2.exception, z.FamilyZKpReviewPending)


# ============================================================
# T2 フォーム経路 (confirm --from-form)
# ============================================================
class FormHelpers(CCBase):
    def _payload(self, cands, *, cat1, cat2=(), cat3=(), level="b1b", grammar=None, comment="コメント", **mods):
        cm = {c["candidate_id"]: c for c in cands["candidates"]}
        by_rank = {c["ai_rank"]: c["candidate_id"] for c in cands["candidates"]}

        def item(rank, cat):
            c = cm[by_rank[rank]]
            return {"term": c["item"]["used_form"], "category": cat, "category_label": f"c{cat}", "ja_gloss": c["item"]["japanese_gloss"], "ja_gloss_status": "official",
                    "candidate_id": c["candidate_id"], "kind": c.get("kind") or "phrase"}
        p = {"schema": "eigo_radio_selection_result_v2", "schema_version": 2, "schema_minor": 1,
             "article": {"slug": "coffee", "level": level, "text_sha256": cands["text_sha256"], "candidates_sha256": cands["candidates_sha256"]},
             "selection": {"key_phrase": [item(r, 1) for r in cat1], "extra_explanation": [item(r, 2) for r in cat2], "meaning_display": [item(r, 3) for r in cat3],
                           "grammar": grammar or []},
             "comment": comment, "ai_reference": {"for_reference_only": True, "items": []}}
        for k, v in mods.items():
            p["article"][k] = v
        return p

    def _write(self, payload, name="payload.json"):
        p = os.path.join(self.tmp, name)
        jd(p, payload)
        return p

    def _gen(self, env, level="b1b"):
        self.ensure(env, level=level)
        return rv.load_candidates(self.kp_dir if level == "b1b" else self.kp_dir_a2)



class TestFromForm(FormHelpers):
    def test_form_confirm_adv_with_unconsumed_and_payload_source(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], cat3=[6, 7])
            pp = self._write(pl)
            out = cc.cmd_from_form(self.run_dir, "b1b", pp, "human", self.uref)
            self.assertEqual(out["revision"], 1)
            self.assertEqual(sorted(u[1] for u in out["unconsumed"]), ["CATEGORY3_NO_CONSUMER"] * 2)   # ③は黙って捨てず保存・明示
            rec = self.rec()
            self.assertEqual(rec["origin"]["kind"], "form_submission")
            self.assertEqual(rec["confirmation_id"], "cf_" + rec["origin"]["form_payload_sha256"][:16])
            src = os.path.join(cc.paths_of(self.kp_dir)["source_dir"], "rev1_payload.json")
            self.assertEqual(rd(src), rd(pp))   # 原文逐語保存(M5a)
            self.assertEqual(rec["user_note_sha256"], cc.user_note_sha256("コメント"))
            self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_REVIEWED)
            self.ensure(env)   # runner: finalize(G0は既存レコードと照合)
            self.consume()
            self.assertEqual(self.rec()["revision"], 1)   # finalizeはレコードを作り直さない
            # payload原文の改変は検出
            wr(src, rd(src) + " ")
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
                self.consume()

    def test_form_std_category2_is_unconsumed(self):
        with Env(self.tmp) as env:
            cands = self._gen(env, level="a2")
            pl = self._payload(cands, cat1=[1, 2], cat2=[3], level="a2")
            out = cc.cmd_from_form(self.run_dir, "a2", self._write(pl), "human", self.uref)
        self.assertEqual([u[1] for u in out["unconsumed"]], ["STD_CATEGORY2_NO_SLOT"])
        rec = cc.load_record(self.kp_dir_a2)
        self.assertEqual([i["slot"] for i in rec["items"]], ["kp", "kp"])

    def test_gloss_mismatch_is_issue_nothing_recorded(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5])
            pl["selection"]["key_phrase"][0]["ja_gloss"] = "フォームだけ別訳"
            with self.assertRaises(rv.ConfirmedContentIssue) as cm:
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
        self.assertIsInstance(cm.exception, rv.KpReviewNotConfirmed)   # rc=4待機系
        self.assertIsNone(self.rec())
        self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)   # 黙って確定・置換していない
        self.assertTrue(os.path.exists(cc.paths_of(self.kp_dir)["issue_md"]))
        self.assertIn("確定内容の確認依頼", rd(cc.paths_of(self.kp_dir)["issue_md"]))

    def test_provisional_gloss_status_is_issue(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5])
            pl["selection"]["extra_explanation"][0]["ja_gloss_status"] = "provisional"
            with self.assertRaises(rv.ConfirmedContentIssue):
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
        self.assertIsNone(self.rec())

    def test_missing_or_stale_candidates_sha_is_issue(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            for mod in ({"candidates_sha256": None}, {"candidates_sha256": "0" * 64}):
                pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], **mod)
                with self.assertRaises(rv.ConfirmedContentIssue):
                    cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
        self.assertIsNone(self.rec())

    def test_term_only_matching_is_refused(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5])
            del pl["selection"]["key_phrase"][0]["candidate_id"]
            with self.assertRaises(cc.CliError):
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5])
            pl["selection"]["key_phrase"][0]["kind"] = "word"
            with self.assertRaises(cc.CliError):
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)

    def test_user_ref_is_required(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            pp = self._write(self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5]))
            with self.assertRaises(cc.CliError):
                cc.cmd_from_form(self.run_dir, "b1b", pp, "human", "")

    def test_existing_validation_still_applies_via_op_select(self):
        """既存の選択検証(KP件数上限等)は迂回しない: op_selectが拒否→何も書かない。"""
        with Env(self.tmp) as env:
            cands = self._gen(env)
            pl = self._payload(cands, cat1=[1, 2, 3, 4], cat2=[5])
            with self.assertRaises(rv.KpReviewError):
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
        self.assertIsNone(self.rec())
        self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)

    def test_grammar_sidecar_written_and_tamper_detected(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            sd = os.path.join(self.run_dir, "b1b", "study_text")
            os.makedirs(sd)
            wr(os.path.join(sd, "grammar_candidates.json"), "{}")   # discover_dirsが見つける最小fixture(文法候補の中身はG4=委任_02Bの対象)
            gram = [{"id": "g1", "title": "現在完了", "explanation_full": "解説全文【日本語訳】…", "explanation_status": "provided"}]
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=gram)
            cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
            rec = self.rec()
            side = os.path.join(sd, cc.FILE_GRAMMAR)
            self.assertEqual(jl(side)["confirmation_id"], rec["confirmation_id"])
            self.assertEqual(rec["grammar"]["explanation_source"], ["form_displayed"])
            self.ensure(env)
            self.consume()
            d = jl(side)
            d["items"][0]["explanation_full"] = "書換え"
            jd(side, d)
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
                self.consume()


# ============================================================
# confirm-revise / restore / revoke / reconfirm
# ============================================================
class TestReviseRestore(CCBase):
    def setUp(self):
        super().setUp()
        self.env = Env(self.tmp)
        self.env.__enter__()
        self.addCleanup(self.env.__exit__, None, None, None)
        self.confirm_user(self.env)

    def test_revise_gloss_chain_updates_candidate_doc_record_and_artifacts(self):
        rec0 = self.rec()
        cid = rec0["items"][0]["candidate_id"]
        with self.assertRaises(cc.CliError):
            cc.cmd_revise(self.run_dir, "b1b", "human", "", "理由", [f"{cid}=新しい訳"])
        out = cc.cmd_revise(self.run_dir, "b1b", "human", self.uref, "ユーザーが訳を修正", [f"{cid}=新しい訳～です"])
        self.assertEqual(out["revised"], [cid])
        self.assertTrue(out["refinalized"])   # final_qa PASS済み→API 0で再finalize
        rec = self.rec()
        self.assertEqual((rec["revision"], rec["history"][-1]["event"]), (2, "revised"))
        self.assertEqual(rec["history"][-1]["extra"]["gloss_before"][cid], rec0["items"][0]["japanese_gloss"])   # 旧値が履歴に残る
        self.assertEqual(cc._problems_self(rec), [])
        self.assertEqual(rec["items"][0]["japanese_gloss"], "新しい訳～です")
        self.assertEqual(rec["items"][0]["derived"]["japanese_gloss_tts"], "新しい訳なになにです")   # 派生物は決定論変換
        self.assertEqual(jl(f"{self.kp_dir}/keywords_canonicalized.json")["items"][0]["japanese_gloss"], "新しい訳～です")
        self.consume()   # G1 PASS(候補doc==レコード==artifact)
        self.ensure(self.env)
        self.assertEqual(self.rec()["revision"], 2)

    def test_restore_after_pipeline_tamper(self):
        self.patch_art(lambda d: d["items"][0].update(japanese_gloss="パイプラインが書換えた訳"))
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            self.consume()
        out = cc.cmd_restore(self.run_dir, "b1b", "fable-ai", "原因=パイプライン側の上書き")
        self.assertTrue(out["refinalized"])
        self.assertTrue(any(f[1] == "japanese_gloss" for f in out["restored_fields"]))   # 復元内容を列挙(黙って直さない)
        self.assertTrue(any("RESTORE_SUPERSEDED" in a for a in out["archived"]))
        self.consume()
        rec = self.rec()
        self.assertEqual(rec["history"][-1]["event"], "restored")
        self.assertEqual(cc._problems_self(rec), [])

    def test_restore_refused_when_human_op_in_review_history(self):
        r = rv.load_review(self.kp_dir)
        r["history"].append({"at": "9999-01-01T00:00:00+09:00", "event": "resolve_gloss", "by": "alice", "detail": {}})
        jd(rv.paths(self.kp_dir)["review"], r)
        self.patch_art(lambda d: d["items"][0].update(japanese_gloss="x"))
        with self.assertRaises(rv.ConfirmedContentIssue) as cm:   # 人間操作が原因の疑い→ISSUE(復元せずユーザーに聞く)
            cc.cmd_restore(self.run_dir, "b1b", "fable-ai", "r")
        self.assertIn("人間の操作", str(cm.exception))
        self.assertEqual(jl(f"{self.kp_dir}/keywords_canonicalized.json")["items"][0]["japanese_gloss"], "x")   # 触っていない

    def test_restore_refused_when_candidate_doc_changed(self):
        r = rv.load_review(self.kp_dir)
        r["candidates_sha256"] = r["candidates_sha256"]
        rec = self.rec()
        rec["origin"]["candidates_sha256"] = "f" * 64
        cc.save_record(self.kp_dir, rec)
        self.patch_art(lambda d: d["items"][0].update(japanese_gloss="x"))
        with self.assertRaises(rv.ConfirmedContentIssue):
            cc.cmd_restore(self.run_dir, "b1b", "fable-ai", "r")

    def test_redundancy_ng_marks_reconfirm_required_and_allows_user_reselect(self):
        shutil.rmtree(self.run_dir)
        env = Env(self.tmp, final_red_seq=["NG", "PASS", "PASS"])
        with env:
            self.ensure(env)
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3, 4, 5], by="human")
            cc.cmd_from_review(self.run_dir, "b1b", "human", self.uref)   # 確定をfinalize前にレコード化(フォーム経路は送信時点で作られる)
            r = self.ensure(env)
            self.assertEqual(r["state"], "PENDING")   # 既存挙動(PENDING差戻し)を維持
            rec = self.rec()
            self.assertEqual(rec["state"], cc.STATE_RECONFIRM)
            self.assertEqual(rec["history"][-1]["event"], "redundancy_ng_reconfirm_required")
            self.assertEqual(rec["items"][0]["used_form"], jl(rv.paths(self.kp_dir)["candidates"])["candidates"][0]["item"]["used_form"])   # 旧確定は履歴/レコードに保存
            self.assertTrue(rd(rv.paths(self.kp_dir)["request"]).startswith("# 確定内容の確認依頼"))   # 依頼書の先頭に『確定内容の確認依頼』節
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 4], vocab_ranks=[1, 2, 4, 5, 6], by="human")   # ユーザーの選び直し(ガード対象外)
            self.ensure(env)
            rec = self.rec()
            self.assertEqual((rec["state"], rec["revision"]), (cc.STATE_LIVE, 2))
            self.consume()


# ============================================================
# STALE precheck(本文変更)・legacy・kill switch・DefaultOn
# ============================================================
class TestStaleLegacyFlag(CCBase):
    def test_text_change_with_user_record_stops_before_paid_generation(self):
        with Env(self.tmp) as env:
            self.confirm_user(env)
            calls = dict(env.n)
            before = {f: rd(f"{self.kp_dir}/{f}") for f in ("kp_candidates.json", "kp_human_review.json", "keywords_canonicalized.json")}
            r = self.ensure(env, text=ARTICLE2)
            self.assertEqual(r["state"], "PENDING")
            self.assertEqual(r["pending"]["reason"], "confirmed_content_issue")
            self.assertEqual(dict(env.n), calls, "有料の候補再生成は走らない")
            for f, v in before.items():
                self.assertEqual(rd(f"{self.kp_dir}/{f}"), v, f)   # 退避・書換えなし
            self.assertTrue(rd(rv.paths(self.kp_dir)["request"]).startswith("# 確定内容の確認依頼"))
            self.assertEqual(self.rec()["revision"], 1)
            cc.cmd_revoke(self.run_dir, "b1b", "human", self.uref, "本文変更に伴う選び直し")
            self.assertFalse(os.path.exists(cc.paths_of(self.kp_dir)["issue_md"]))   # 解消済みISSUEは依頼書に残らない
            r2 = self.ensure(env, text=ARTICLE2)   # 取消後は従来どおり(STALE→再生成)
            self.assertEqual(r2["state"], "PENDING")
            self.assertGreater(env.n["call1"], calls["call1"])

    def test_text_change_with_auto_record_keeps_existing_stale_behavior(self):
        with Env(self.tmp) as env:
            self.confirm_auto(env)
            n = env.n["call1"]
            self.ensure(env, text=ARTICLE2)
            self.assertGreater(env.n["call1"], n)

    def test_legacy_run_without_record_is_read_only_warn(self):
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}):
            with Env(self.tmp) as env:
                self.confirm_user(env)
        self.assertIsNone(self.rec())   # 機能有効化前に確定したrun(レコード無し)
        self.consume()                   # 有効化後: 検証OK・遅延生成しない
        self.assertIsNone(self.rec())
        self.patch_art(lambda d: d["items"][0].update(japanese_gloss="確定後に変わった訳"))
        self.consume()                   # WARNのみ(BLOCKしない=M7)
        drift = jl(cc.paths_of(self.kp_dir)["legacy"])
        self.assertEqual(drift["kind"], "legacy_drift")
        self.assertEqual(drift["diffs"][0]["field"], "japanese_gloss")
        self.assertIsNone(self.rec())
        with Env(self.tmp) as env:
            self.ensure(env)   # idempotent再実行でもレコードを遅延生成しない
        self.assertIsNone(self.rec())

    def test_adopt_existing_dry_run_then_apply_then_integrity_then_restore(self):
        self.uref = os.path.join(self.tmp, "u.md")
        wr(self.uref, "x")
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}):
            with Env(self.tmp) as env:
                self.confirm_user(env)
        self.patch_art(lambda d: d["items"][0].update(japanese_gloss="ずれた訳"))
        dry = cc.cmd_from_review(self.run_dir, "b1b", "human", self.uref, adopt_existing=True, apply=False)
        self.assertTrue(dry["dry_run"])
        self.assertEqual([d["field"] for d in dry["artifact_drift"]], ["japanese_gloss"])   # 差分を提示
        self.assertIsNone(self.rec())
        out = cc.cmd_from_review(self.run_dir, "b1b", "human", self.uref, adopt_existing=True, apply=True)
        self.assertEqual(self.rec()["origin"]["kind"], "adopt_existing")
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):   # 保護下に置いた後はずれがBLOCK
            self.consume()
        cc.cmd_restore(self.run_dir, "b1b", "fable-ai", "adopt後の復元")
        self.consume()

    def test_kill_switch_off_disables_everything_with_warn(self):
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}):
            self.assertFalse(cc.protection_enabled())
            with Env(self.tmp) as env:
                self.confirm_user(env)
            self.assertIsNone(self.rec())                                        # レコードを作らない
            self.patch_art(lambda d: d["items"][0].update(used_form="changed"))
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.consume()                                                   # G1は何もしない(従来動作)
            self.assertIn("kill switch", err.getvalue())
            self.assertTrue(os.path.exists(cc.paths_of(self.kp_dir)["disabled"]))
            rv.op_reselect(self.kp_dir, by="human")                              # ガードも無効

    def test_default_is_on_and_single_reader(self):
        env = {k: v for k, v in os.environ.items() if k != cc.FLAG_NAME}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertTrue(cc.protection_enabled())
        for name in ("er119_kp_human_review_01.py", "er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py",
                     "er121_family_y_runner_01.py"):
            self.assertNotIn(cc.FLAG_NAME, open(os.path.join(ROOT, name), encoding="utf-8", errors="ignore").read(), name)   # flagの読取/迂回点はer128の1関数のみ
        src = open(os.path.join(ROOT, "er128_kp_confirmed_content_01.py"), encoding="utf-8").read()
        self.assertEqual(len(re.findall(r"os\.environ", src)), 1)
        self.assertEqual(len(re.findall(r"def protection_enabled\(", src)), 1)


# ============================================================
# status / 単一アクセサ / 隔離
# ============================================================
class TestStatusAndAccessor(CCBase):
    def test_status_and_load_verified_items(self):
        with Env(self.tmp) as env:
            self.confirm_user(env)
        st = cc.cmd_status(self.run_dir)
        self.assertTrue(st["flag_enabled"])
        self.assertEqual(st["levels"][0]["record"]["state"], cc.STATE_LIVE)
        self.assertEqual(len(cc.load_verified_items(self.kp_dir, level="b1b")), 3)
        self.assertEqual(len(cc.load_verified_items(self.kp_dir, level="b1b", which="vocab")), 5)
        self.patch_art(lambda d: d["items"][0].update(used_form="changed"))
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):   # 検証してから返す(改変済みは返さない)
            cc.load_verified_items(self.kp_dir, level="b1b")


class TestCli(FormHelpers):
    """CLI(run)の終了コード: 成功=0、拒否(REFUSED)=2、確定内容のISSUE=4(待機)。"""

    def test_cli_exit_codes(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5])
            pp = self._write(pl)
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cc.run(["status", "--run", self.run_dir]), 0)
                self.assertEqual(cc.run(["confirm", "--from-form", pp, "--run", self.run_dir, "--level", "b1b", "--by", "human"]), 2)   # --user-ref無し=拒否
                pl["selection"]["key_phrase"][0]["ja_gloss"] = "別訳"
                self.assertEqual(cc.run(["confirm", "--from-form", self._write(pl, "p2.json"), "--run", self.run_dir, "--level", "b1b", "--by", "human",
                                         "--user-ref", self.uref]), rv.EXIT_CODE_PENDING)   # ISSUE=rc4(待機)
                self.assertEqual(cc.run(["confirm", "--from-form", pp, "--run", self.run_dir, "--level", "b1b", "--by", "human", "--user-ref", self.uref]), 0)
                self.assertEqual(cc.run(["revoke", "--run", self.run_dir, "--level", "b1b", "--by", "human", "--reason", "x"]), 2)   # user-ref無し
                self.assertEqual(cc.run(["revoke", "--run", self.run_dir, "--level", "b1b", "--by", "human", "--reason", "x", "--user-ref", self.uref]), 0)
                self.assertEqual(cc.run(["restore", "--run", self.run_dir, "--level", "b1b", "--by", "human", "--reason", "x"]), 2)   # revoked後は復元対象なし


class TestIsolation(unittest.TestCase):
    def test_abc_and_shared_functions_do_not_import_er128(self):
        import glob
        offenders = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if "test" in b or b in ("er128_kp_confirmed_content_01.py", "er119_kp_human_review_01.py"):
                continue
            if re.search(r"^\s*(import|from)\s+er128_", open(p, encoding="utf-8", errors="ignore").read(), re.M):
                offenders.append(b)
        self.assertEqual(offenders, [])

    def test_core_calls_er128_only_lazily(self):
        src = open(os.path.join(ROOT, "er119_kp_human_review_01.py"), encoding="utf-8").read()
        self.assertEqual(len(re.findall(r"^import er128|^from er128", src, re.M)), 0)   # 循環import回避(関数内の遅延importのみ)
        self.assertNotIn("os.environ", src)


# ============================================================
# T9 M1: Z stage_kp の G1(確定後・有料の派生物生成の前)
# ============================================================
class TestZStageKpG1(unittest.TestCase):
    PRE = ["seed_check", "writer", "std_adjust", "plan", "support"]

    def setUp(self):
        import er026_family_z_fiction_production_runner_01 as z
        self.z = z
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        stack = contextlib.ExitStack()
        for target in ("er003_v1_en_direct_vfl_01_generate.get_client", "er003_v1_n3_01_scaffold_generate.run_key_phrases",
                       "er011_key_phrase_set_redundancy_qa_01.make_redundancy_qa_fn", "er105_kp_fulltext_selector_01.make_selector_fn",
                       "er119_kp_prompt_2v_01.make_vocab_selector_fn", "er003_key_words_canonicalization.make_canonicalization_fn",
                       "er003_key_words_gloss_alignment.make_alignment_fn"):
            stack.enter_context(mock.patch(target, side_effect=AssertionError(f"REAL API PATH CALLED: {target}")))
        stack.enter_context(mock.patch.object(rv, "STORE_ROOT", os.path.join(self.tmp, "store")))
        self.addCleanup(stack.close)
        self.ctx = z.build_mock_context(self.tmp)
        decl = rv.declarations_path(self.ctx.out_dir)
        if os.path.exists(decl):
            os.remove(decl)
        _quiet(z.run_stages, self.ctx, self.PRE)
        self.src = {lv: f"{self.ctx.out_dir}/key_phrases/{lv}" for lv in ("b1b", "a2")}

    def _calls(self):
        p = self.ctx.mock_api.path
        return len(rd(p).splitlines()) if os.path.exists(p) else 0

    def test_tamper_after_confirm_stops_at_stage_kp_before_paid_generation(self):
        import er119_grammar_review_01 as gr
        with self.assertRaises(self.z.FamilyZKpReviewPending):
            _quiet(self.z.run_stage, self.ctx, "kp")
        for lv in ("b1b", "a2"):
            rv.op_select(self.src[lv], kp_ranks=[1, 2, 3], vocab_ranks=([1, 2, 3, 4, 5] if lv == "b1b" else None), by="human")
        sd = self.z._part2_dir(self.ctx)
        gr.op_decide(sd, choice="top1", accept_ai=True, candidates_sha256=gr.load_candidates(sd)["candidates_sha256"], by="human")
        _quiet(self.z.run_stage, self.ctx, "kp")
        for lv in ("b1b", "a2"):
            self.assertEqual(cc.load_record(self.src[lv])["confirmed_by"]["actor"], cc.ACTOR_USER)
            self.assertEqual(rv.require_final_consistent(self.src[lv], level=lv, require_src_contract=True,
                                                         assets_json=f"{self.z._kp_assets_dir(self.ctx, lv)}/keywords_canonicalized.json")["status"], rv.ST_REVIEWED)
        # 確定後にartifact(src)の日本語訳を書換え → 再実行は stage_kp_post_install のG1で止まり、Adv解説LLM/Part 1/Part 2の呼出は増えない(M1)
        p = f"{self.src['b1b']}/keywords_canonicalized.json"
        d = jl(p)
        d["items"][0]["japanese_gloss"] = "確定後に別訳へ置換された"
        jd(p, d)
        n = self._calls()
        with self.assertRaises(self.z.FamilyZE2EStop) as cm:
            _quiet(self.z.run_stage, self.ctx, "kp")
        self.assertIn("CONFIRMED_CONTENT_INTEGRITY_VIOLATION", str(cm.exception))
        self.assertNotIsInstance(cm.exception, self.z.FamilyZKpReviewPending)
        self.assertEqual(self._calls(), n, "G1より後の有料生成(Adv解説・Part 1・Part 2)は呼ばれない")

    def test_stage_kp_g1_is_after_gates_and_install_in_source(self):
        src = open(os.path.join(ROOT, "er026_family_z_fiction_production_runner_01.py"), encoding="utf-8").read()
        body = src[src.index("def stage_kp(ctx)"):]
        i_person, i_src, i_inst = body.index("_gloss_person_gate(ctx, lv, text, prov)"), body.index("_src_gate(ctx, lv, text)"), body.index("dst = install_kp_assets(ctx, lv)")
        i_g1, i_expl = body.index('_assert_kp_review_consistent(ctx, lv, "stage_kp_post_install")'), body.index("sig_payload")
        self.assertTrue(i_person < i_src < i_inst < i_g1 < i_expl)


class TestYStageKpG1Source(unittest.TestCase):
    def test_y_stage_kp_g1_is_after_install_and_before_explanation(self):
        src = open(os.path.join(ROOT, "er121_family_y_runner_01.py"), encoding="utf-8").read()
        body = src[src.index("def stage_kp(ctx)"):]
        i_inst = body.index("        install_kp_assets(ctx, lv)\n")
        i_g1 = body.index('_assert_kp_review_consistent(ctx, lv, "stage_kp_post_install")')
        i_expl = body.index("import er019_family_x_kp_explanation_01 as kexp")
        self.assertTrue(i_inst < i_g1 < i_expl)

    def test_y_and_z_pass_assets_json_to_g1(self):
        for name in ("er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py"):
            s = open(os.path.join(ROOT, name), encoding="utf-8").read()
            self.assertRegex(s, r"require_final_consistent\(src, level=\w+, require_src_contract=(True|False), assets_json=")


if __name__ == "__main__":
    unittest.main()
