# -*- coding: utf-8 -*-
"""SLOT-23-CONSUMER-DESIGN-01 委任_04B: 確定内容保護側の display_spec継承 / G1不変条件 / reconsume / ③訳の保護 / Std Part 1 vocab(level非依存化) のtest。API 0。
マーク発行(new_reviewでのstd_part1付与)は未接続(M14)。ここでは `issue_std_part1_mark` をnew_reviewへ被せるpatchで『接続後』を模擬し、未接続の既定もassertする。
実行: .venv\\Scripts\\python.exe -m unittest er128_kp_confirmed_content_slot23_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import contextlib
import inspect
import os
import re
import unittest
from unittest import mock

import er119_kp_human_review_01 as rv
import er128_kp_confirmed_content_01 as cc
import er128_kp_confirmed_content_test_01 as base
from er128_kp_confirmed_content_test_01 import legacy_unmarked_flow
from er119_test_support_01 import Env, jd, jl, rd, wr

ROOT = os.path.dirname(os.path.abspath(__file__))


@contextlib.contextmanager
def marks_connected():
    """M14(new_reviewへのマーク発行の接続)後の挙動を模擬する。"""
    orig = rv.new_review

    def wrapped(*a, **k):
        return rv.issue_std_part1_mark(orig(*a, **k))
    with mock.patch.object(rv, "new_review", wrapped):
        yield


class Slot23Base(base.FormHelpers):
    def kd(self, level):
        return self.kp_dir if level == "b1b" else self.kp_dir_a2

    def form(self, env, level, *, cat1, cat2=(), cat3=()):
        cands = self._gen(env, level=level)
        pl = self._payload(cands, cat1=cat1, cat2=cat2, cat3=cat3, level=level)
        return cc.cmd_from_form(self.run_dir, level, self._write(pl), "human", self.uref)


# ============================================================
# A. マーク発行は未接続(M14)・発行関数・署名・vocab_enabled
# ============================================================
class TestMarkAndVocabEnabled(Slot23Base):
    def test_M14_new_review_issues_mark_now_connected(self):
        # M14接続済み(委任_05M): 素のnew_review(patch無し)が新規KP reviewにstd_part1を付ける。呼出点はnew_review内の1箇所だけ
        with Env(self.tmp) as env:
            self._gen(env, level="a2")
            self._gen(env, level="b1b")
        self.assertTrue(rv.load_review(self.kp_dir_a2).get("std_part1"))
        self.assertTrue(rv.load_review(self.kp_dir).get("std_part1"))
        code_lines = [ln for ln in inspect.getsource(rv).splitlines() if "issue_std_part1_mark(" in ln and not ln.lstrip().startswith(("#", "def ", '"""', "**"))]
        self.assertEqual(len(code_lines), 1, code_lines)
        self.assertIn("issue_std_part1_mark", inspect.getsource(rv.new_review))

    def test_M14_display_spec_derived_for_both_a2_and_b1b(self):
        # B班判断(a): 素のnew_review→from_formで、a2/b1bとも確定レコードにdisplay_specが導出される(マーク無しならキー無し)
        with Env(self.tmp) as env:
            self.form(env, "a2", cat1=[1, 2, 3], cat2=[4], cat3=[5])
            self.form(env, "b1b", cat1=[1, 2, 3], cat2=[], cat3=[4])
        self.assertEqual(cc.display_spec_of(self.run_dir, "a2"), cc.DISPLAY_SPEC_V1)
        self.assertEqual(cc.display_spec_of(self.run_dir, "b1b"), cc.DISPLAY_SPEC_V1)

    def test_M14_prev_without_mark_is_not_retroactively_marked_by_cc(self):
        # 既に確定済みの旧(マーク無し)記事のrecord/reviewは、接続だけでは変わらない(遡及なし。移行はreconsume明示実行のみ)
        with mock.patch.object(rv, "issue_std_part1_mark", lambda r: r), Env(self.tmp) as env:
            self.form(env, "a2", cat1=[1, 2], cat2=[3], cat3=[4])
        before = (cc.load_record(self.kp_dir_a2), rv.load_review(self.kp_dir_a2))
        self.assertNotIn("display_spec", before[0])
        self.assertNotIn("std_part1", before[1])
        self.assertIsNone(cc.display_spec_of(self.run_dir, "a2"))
        self.assertEqual(cc.load_record(self.kp_dir_a2), before[0])   # 読むだけでは変わらない

    def test_connected_new_review_marks_kp_reviews_only(self):
        with marks_connected(), Env(self.tmp) as env:
            self._gen(env, level="a2")
            self._gen(env, level="b1b")
        self.assertTrue(rv.load_review(self.kp_dir_a2).get("std_part1"))
        self.assertTrue(rv.load_review(self.kp_dir).get("std_part1"))   # b1bは不問(vocabは常に有効)。displayマークとしてだけ使う

    def test_vocab_enabled_truth_table(self):
        self.assertTrue(rv.vocab_enabled("b1b"))
        self.assertTrue(rv.vocab_enabled("b1b", {}))
        self.assertFalse(rv.vocab_enabled("a2", {}))
        self.assertFalse(rv.vocab_enabled("a2", None))
        self.assertTrue(rv.vocab_enabled("a2", {"std_part1": True}))

    def test_selection_signature_unchanged_without_mark_and_differs_with_mark(self):
        r = {"kind": rv.KIND_KP, "text_sha256": "t", "candidates_sha256": "c", "selection": {"kp": ["a"], "vocab": ["a"]}, "ng": [], "status": "REVIEWED"}
        old = rv.jsha({"kind": rv.KIND_KP, "text_sha256": "t", "candidates_sha256": "c", "selection": {"kp": ["a"], "vocab": ["a"]}, "ng": [], "status": "REVIEWED"})
        self.assertEqual(rv.selection_signature(r), old)   # 旧署名不変
        self.assertNotEqual(rv.selection_signature(dict(r, std_part1=True)), old)
        self.assertEqual(rv.selection_signature(dict(r, std_part1=False)), old)

    def test_validate_selection_vocab_rules_are_level_independent_but_mark_gated(self):
        with Env(self.tmp) as env:
            c = self._gen(env, level="a2")
        ids = [x["candidate_id"] for x in sorted(c["candidates"], key=lambda z: z["ai_rank"])]
        kp, vocab = ids[:3], ids[:5]
        # マーク無しのa2: vocab指定は不可(遡及なし)・vocab無しは従来どおりOK
        self.assertTrue(rv.validate_selection(c, {"kp": kp, "vocab": vocab}, level="a2"))
        self.assertEqual(rv.validate_selection(c, {"kp": kp, "vocab": []}, level="a2"), [])
        # マーク付きa2: vocab必須・KP ⊂ vocab(Advと同一規則)
        self.assertEqual(rv.validate_selection(c, {"kp": kp, "vocab": vocab}, level="a2", std_part1=True), [])
        self.assertTrue(any("vocab" in e for e in rv.validate_selection(c, {"kp": kp, "vocab": []}, level="a2", std_part1=True)))
        self.assertTrue(any("KP ⊂ vocab" in e for e in rv.validate_selection(c, {"kp": kp, "vocab": ids[1:5]}, level="a2", std_part1=True)))
        # auto_select
        self.assertEqual(rv.auto_select(c, level="a2")["vocab"], [])
        self.assertEqual(len(rv.auto_select(c, level="a2", std_part1=True)["vocab"]), 5)

    @legacy_unmarked_flow
    def test_legacy_a2_flow_is_unchanged_and_no_removed_rename_remains(self):
        with Env(self.tmp) as env:
            self.confirm_user(env, level="a2")
        self.assertFalse(os.path.exists(rv.paths(self.kp_dir_a2)["vocab"]))   # マーク無しa2はvocab_confirmed.jsonを書かない(従来と同じ)
        self.assertNotIn(".removed", inspect.getsource(rv.finalize_kp))


# ============================================================
# G3 Std Part 1照合のlevel化(委任_05M)
# ============================================================
class TestG3StdPart1Level(Slot23Base):
    def _pages(self, rec, *, drop_gloss=False):
        d = self.tmp
        body = "".join(f"<li>{it['used_form']} {'' if drop_gloss and it is rec['items'][0] else it['japanese_gloss']}</li>" for it in rec["items"])
        pg = os.path.join(d, "std_part1.html")
        wr(pg, "<html>" + body + "</html>")
        return pg

    def test_display_spec_a2_checks_part1_rows_and_page(self):
        with Env(self.tmp) as env:
            self.form(env, "a2", cat1=[1, 2, 3], cat2=[4, 5], cat3=[6])
            self.ensure(env, level="a2")
        rec = cc.load_record(self.kp_dir_a2)
        self.assertEqual(rec["display_spec"], cc.DISPLAY_SPEC_V1)
        rows = [{"english_expression": it["used_form"], "meaning_in_text_ja": it["japanese_gloss"]} for it in rec["items"]]
        st = os.path.join(self.tmp, "p1.json")
        jd(st, {"rows": rows})
        good = self._pages(rec)
        cc.verify_outputs(self.kp_dir_a2, "a2", study_text_json=st, vocab_page_paths=[good], page_paths=[good])   # PASS
        bad_rows = [dict(r) for r in rows]
        bad_rows[0]["meaning_in_text_ja"] = "改変された訳"
        jd(st, {"rows": bad_rows})
        with self.assertRaises(Exception):
            cc.verify_outputs(self.kp_dir_a2, "a2", study_text_json=st, vocab_page_paths=[good], page_paths=[good])
        jd(st, {"rows": rows})
        bad_page = self._pages(rec, drop_gloss=True)
        with self.assertRaises(Exception):
            cc.verify_outputs(self.kp_dir_a2, "a2", study_text_json=st, vocab_page_paths=[bad_page], page_paths=[good])

    @legacy_unmarked_flow
    def test_a2_without_display_spec_is_unchanged(self):
        with Env(self.tmp) as env:
            self.confirm_user(env, level="a2")
        rec = cc.load_record(self.kp_dir_a2)
        self.assertNotIn("display_spec", rec)
        empty = os.path.join(self.tmp, "x.html")
        wr(empty, "<html>none of the glosses</html>")
        st = os.path.join(self.tmp, "p1.json")
        jd(st, {"rows": [{"english_expression": rec["items"][0]["used_form"], "meaning_in_text_ja": "違う"}]})
        good = os.path.join(self.tmp, "g.html")
        wr(good, "<html>" + "".join(it["used_form"] + it["japanese_gloss"] for it in rec["items"]) + "</html>")
        cc.verify_outputs(self.kp_dir_a2, "a2", study_text_json=st, vocab_page_paths=[empty], page_paths=[good])   # Part 1検査は走らない(従来どおり)


# ============================================================
# B. マーク付きa2: ②がitemsへ・vocab_confirmed.jsonはfinalizeだけ・G1
# ============================================================
class TestMarkedStd(Slot23Base):
    def test_marked_a2_form_puts_category2_in_items_and_finalize_is_single_writer(self):
        with marks_connected(), Env(self.tmp) as env:
            out = self.form(env, "a2", cat1=[1, 2, 3], cat2=[4, 5], cat3=[6])
            rec = cc.load_record(self.kp_dir_a2)
            self.assertEqual(rec["display_spec"], cc.DISPLAY_SPEC_V1)
            self.assertEqual([(i["category"], i["slot"]) for i in rec["items"]], [(1, "kp")] * 3 + [(2, "vocab")] * 2)
            self.assertEqual([u["reason"] for u in rec["unconsumed"]], [cc.REASON_C3_HIGHLIGHT])
            self.assertNotIn(cc.REASON_C2_NO_SLOT, [u[1] for u in out["unconsumed"]])
            self.assertFalse(os.path.exists(rv.paths(self.kp_dir_a2)["vocab"]))   # CLIはvocab_confirmed.jsonを書かない
            r = self.ensure(env, level="a2")
            self.assertEqual(r["state"], "FINALIZED")
            self.assertEqual(len(jl(rv.paths(self.kp_dir_a2)["vocab"])["items"]), 5)   # finalize_kpだけが書く
            self.assertEqual(len(rv.part1_items(self.kp_dir_a2)), 5)
            self.consume("a2")   # G1 PASS
            self.assertEqual(cc.display_spec_of(self.run_dir, "a2"), cc.DISPLAY_SPEC_V1)

    @legacy_unmarked_flow
    def test_unmarked_a2_form_keeps_legacy_behavior(self):
        with Env(self.tmp) as env:
            out = self.form(env, "a2", cat1=[1, 2], cat2=[3], cat3=[4])
        self.assertEqual(sorted(u[1] for u in out["unconsumed"]), sorted([cc.REASON_C2_NO_SLOT, cc.REASON_C3_NO_CONSUMER]))
        rec = cc.load_record(self.kp_dir_a2)
        self.assertNotIn("display_spec", rec)   # キー自体を作らない
        self.assertIsNone(cc.display_spec_of(self.run_dir, "a2"))

    def test_g1_invariant_display_spec_iff_std_part1_and_no_legacy_reasons(self):
        with marks_connected(), Env(self.tmp) as env:
            self.form(env, "a2", cat1=[1, 2, 3], cat2=[4, 5], cat3=[6])
            self.ensure(env, level="a2")
            self.consume("a2")
            good = cc.load_record(self.kp_dir_a2)
            # (1) display_specを消す(再署名しても)=不一致
            bad = {k: v for k, v in good.items() if k != "display_spec"}
            cc.save_record(self.kp_dir_a2, bad)
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation) as cm:
                self.consume("a2")
            self.assertIn("display_spec", str(cm.exception) + rd(cc.paths_of(self.kp_dir_a2)["issue_json"]))
            # (2) 旧reason(STD_CATEGORY2_NO_SLOT)を戻す
            bad2 = dict(good, unconsumed=good["unconsumed"] + [{"candidate_id": "x", "category": 2, "reason": cc.REASON_C2_NO_SLOT}])
            cc.save_record(self.kp_dir_a2, bad2)
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
                self.consume("a2")
            # (3) 戻せば通る
            cc.save_record(self.kp_dir_a2, good)
            self.consume("a2")

    def test_g1_does_not_check_unmarked_legacy_records(self):
        with Env(self.tmp) as env:
            self.form(env, "a2", cat1=[1, 2, 3], cat2=[4])
            self.ensure(env, level="a2")
            self.consume("a2")   # 旧run: STD_CATEGORY2_NO_SLOT付きでもPASS(遡及なし)
        self.assertEqual(cc._display_spec_diffs(cc.load_record(self.kp_dir_a2), "a2", rv.load_review(self.kp_dir_a2)), [])

    def test_display_spec_is_inherited_and_not_part_of_content_sha(self):
        with marks_connected(), Env(self.tmp) as env:
            self.form(env, "a2", cat1=[1, 2, 3], cat2=[4, 5], cat3=[6])
            self.ensure(env, level="a2")
            rec = cc.load_record(self.kp_dir_a2)
            cid = rec["items"][0]["candidate_id"]
            cc.cmd_revise(self.run_dir, "a2", "human", self.uref, "訳の修正", [f"{cid}=新しい訳"])
            rec2 = cc.load_record(self.kp_dir_a2)
        self.assertEqual(rec2["display_spec"], cc.DISPLAY_SPEC_V1)   # 継承
        self.assertEqual(rec2["revision"], 2)
        self.assertNotIn("display_spec", cc.PROTECTED_ITEM_FIELDS)


# ============================================================
# C. reconsume
# ============================================================
class TestReconsume(Slot23Base):
    def _legacy_a2(self, env):
        self.form(env, "a2", cat1=[1, 2, 3], cat2=[4, 5], cat3=[6])
        self.ensure(env, level="a2")
        return cc.load_record(self.kp_dir_a2), rv.load_review(self.kp_dir_a2)

    @legacy_unmarked_flow
    def test_reconsume_a2_moves_category2_to_items_keeps_user_selection(self):
        with Env(self.tmp) as env:
            rec0, rv0 = self._legacy_a2(env)
            self.assertEqual(len(rec0["items"]), 3)
            self.assertEqual(sorted(u["reason"] for u in rec0["unconsumed"]), sorted([cc.REASON_C2_NO_SLOT] * 2 + [cc.REASON_C3_NO_CONSUMER]))
            no_slot_ids = sorted(u["candidate_id"] for u in rec0["unconsumed"] if u["reason"] == cc.REASON_C2_NO_SLOT)
            out = cc.cmd_reconsume(self.run_dir, "a2", "human", self.uref)
            self.assertTrue(out["reconsumed"])
            self.assertEqual(sorted(out["category2_moved_to_items"]), no_slot_ids)
            self.assertIn("Redundancy QA", out["next"])   # 確定Redundancy QA(LLM)は次回起動で走ることを明記
            rec = cc.load_record(self.kp_dir_a2)
            rvw = rv.load_review(self.kp_dir_a2)
            # ユーザー選定(候補ID・区分・件数)は不変
            self.assertEqual(rec["confirmation_id"], rec0["confirmation_id"])
            self.assertEqual(rec["origin"]["kind"], rec0["origin"]["kind"])
            self.assertEqual(rec["origin"]["form_payload_sha256"], rec0["origin"]["form_payload_sha256"])
            self.assertEqual([i["candidate_id"] for i in rec["items"] if i["slot"] == "kp"], [i["candidate_id"] for i in rec0["items"]])
            self.assertEqual(sorted(i["candidate_id"] for i in rec["items"] if i["category"] == 2), no_slot_ids)
            self.assertEqual([u["reason"] for u in rec["unconsumed"]], [cc.REASON_C3_HIGHLIGHT])
            self.assertEqual(rec["display_spec"], cc.DISPLAY_SPEC_V1)
            self.assertEqual(rec["revision"], 2)
            self.assertEqual(rec["history"][-1]["event"], "reconsumed")
            self.assertEqual(rec["history"][-1]["user_ref"], self.uref)
            self.assertEqual(cc._problems_self(rec), [])   # hash chain継続
            self.assertEqual(rec["history"][0]["entry_sha256"], rec0["history"][0]["entry_sha256"])
            self.assertEqual(rec["origin"]["review_selection_signature"], rvw["selection_signature"])
            self.assertTrue(rvw["std_part1"])
            self.assertEqual(rvw["selection"]["kp"], rv0["selection"]["kp"])
            self.assertEqual(sorted(rvw["selection"]["vocab"]), sorted(rvw["selection"]["kp"] + no_slot_ids))
            # CLIはvocab_confirmed.jsonを直接書かない(退避+次回finalizeのみ)
            self.assertFalse(os.path.exists(rv.paths(self.kp_dir_a2)["vocab"]))
            self.assertFalse(out["refinalized"])
            self.assertTrue(any("RECONSUME_SUPERSEDED" in a for a in out["archived"]))
            # 次回runner起動(finalize+確定Redundancy QA)で①+②が確定物になる
            r = self.ensure(env, level="a2")
            self.assertEqual(r["state"], "FINALIZED")
            self.assertEqual(len(jl(rv.paths(self.kp_dir_a2)["vocab"])["items"]), 5)
            self.assertIsNotNone(rv.load_review(self.kp_dir_a2)["final_qa"])
            self.consume("a2")
            self.assertEqual(cc.load_record(self.kp_dir_a2)["revision"], 2)   # finalizeはレコードを作り直さない

    def test_reconsume_is_idempotent(self):
        with Env(self.tmp) as env:
            self._legacy_a2(env)
            cc.cmd_reconsume(self.run_dir, "a2", "human", self.uref)
            self.ensure(env, level="a2")
            before = rd(cc.paths_of(self.kp_dir_a2)["record"])
            out = cc.cmd_reconsume(self.run_dir, "a2", "human", self.uref)
        self.assertFalse(out["reconsumed"])
        self.assertTrue(out["unchanged"])
        self.assertEqual(rd(cc.paths_of(self.kp_dir_a2)["record"]), before)

    def test_reconsume_requires_user_ref_and_live_record(self):
        with Env(self.tmp) as env:
            self._legacy_a2(env)
            with self.assertRaises(cc.CliError):
                cc.cmd_reconsume(self.run_dir, "a2", "human", "")
            with self.assertRaises(cc.CliError):
                cc.cmd_reconsume(self.run_dir, "a2", "", self.uref)
            self.assertEqual(cc.run(["reconsume", "--run", self.run_dir, "--level", "a2", "--by", "human"]), 2)   # CLIも--user-ref無しは拒否
            cc.cmd_revoke(self.run_dir, "a2", "human", self.uref, "x")
            with self.assertRaises(cc.CliError):
                cc.cmd_reconsume(self.run_dir, "a2", "human", self.uref)

    def test_reconsume_refuses_broken_hash_chain(self):
        with Env(self.tmp) as env:
            rec0, _ = self._legacy_a2(env)
            p = cc.paths_of(self.kp_dir_a2)["record"]
            d = jl(p)
            d["history"][0]["reason"] = "tampered"
            jd(p, d)
            with self.assertRaises(cc.CliError):
                cc.cmd_reconsume(self.run_dir, "a2", "human", self.uref)

    @legacy_unmarked_flow
    def test_reconsume_validation_failure_is_issue_and_changes_nothing(self):
        with Env(self.tmp) as env:
            rec0, rv0 = self._legacy_a2(env)
            with mock.patch.object(rv, "validate_selection", return_value=["候補5と候補1は意味・用法が重複しています(Redundancy QA)"]):
                with self.assertRaises(rv.ConfirmedContentIssue):
                    cc.cmd_reconsume(self.run_dir, "a2", "human", self.uref)
            self.assertEqual(cc.load_record(self.kp_dir_a2), rec0)
            self.assertEqual(rv.load_review(self.kp_dir_a2)["selection_signature"], rv0["selection_signature"])
            self.assertNotIn("std_part1", rv.load_review(self.kp_dir_a2))

    @legacy_unmarked_flow
    def test_reconsume_b1b_is_record_only(self):
        with Env(self.tmp) as env:
            self.form(env, "b1b", cat1=[1, 2, 3], cat2=[4, 5], cat3=[6, 7])
            self.ensure(env)
            rec0, rv0 = cc.load_record(self.kp_dir), rv.load_review(self.kp_dir)
            arts0 = {k: rd(v) for k, v in rv.paths(self.kp_dir).items() if k in ("kp", "vocab", "final")}
            out = cc.cmd_reconsume(self.run_dir, "b1b", "human", self.uref)
            rec = cc.load_record(self.kp_dir)
            self.assertTrue(out["reconsumed"])
            self.assertIsNone(out["refinalized"])
            self.assertEqual(rec["content_sha256"], rec0["content_sha256"])   # itemsは不変(Advは②が既にitems)
            self.assertEqual(rec["display_spec"], cc.DISPLAY_SPEC_V1)
            self.assertEqual(sorted(u["reason"] for u in rec["unconsumed"]), [cc.REASON_C3_HIGHLIGHT] * 2)
            self.assertEqual(rv.load_review(self.kp_dir)["selection_signature"], rv0["selection_signature"])   # reviewは不変
            self.assertEqual({k: rd(rv.paths(self.kp_dir)[k]) for k in arts0}, arts0)   # 成果物も不変
            self.consume("b1b")
            self.assertEqual(cc.display_spec_of(self.run_dir, "b1b"), cc.DISPLAY_SPEC_V1)
            self.assertFalse(cc.cmd_reconsume(self.run_dir, "b1b", "human", self.uref)["reconsumed"])


# ============================================================
# D. ③訳の保護 / display_spec_of
# ============================================================
class TestCategory3AndAccessor(Slot23Base):
    def test_cand_diffs_protect_category3_gloss_only_for_display_spec_records(self):
        with marks_connected(), Env(self.tmp) as env:
            self.form(env, "b1b", cat1=[1, 2, 3], cat2=[4, 5], cat3=[6])
            self.ensure(env)
            rec = cc.load_record(self.kp_dir)
            cands = rv.load_candidates(self.kp_dir)
        self.assertEqual(cc._cand_diffs(rec, cands), [])
        c3 = rec["unconsumed"][0]["candidate_id"]
        import copy as _copy
        bad = _copy.deepcopy(cands)
        for c in bad["candidates"]:
            if c["candidate_id"] == c3:
                c["item"]["japanese_gloss"] = "別の訳"
        d = cc._cand_diffs(rec, bad)
        self.assertEqual([x["field"] for x in d], ["japanese_gloss(category3)"])
        legacy = {k: v for k, v in rec.items() if k != "display_spec"}
        self.assertEqual(cc._cand_diffs(legacy, bad), [])   # マーク無しは従来どおり(遡及なし)

    def test_confirm_revise_can_fix_category3_gloss(self):
        with marks_connected(), Env(self.tmp) as env:
            self.form(env, "b1b", cat1=[1, 2, 3], cat2=[4, 5], cat3=[6])
            self.ensure(env)
            rec0 = cc.load_record(self.kp_dir)
            c3 = rec0["unconsumed"][0]["candidate_id"]
            out = cc.cmd_revise(self.run_dir, "b1b", "human", self.uref, "③の訳を修正", [f"{c3}=修正後の訳"])
            self.assertEqual(out["revised"], [c3])
            rec = cc.load_record(self.kp_dir)
            self.assertEqual(rec["unconsumed"][0]["japanese_gloss"], "修正後の訳")
            self.assertEqual(rec["history"][-1]["extra"]["gloss_before"][c3], rec0["unconsumed"][0]["japanese_gloss"])
            self.assertEqual(cc._problems_self(rec), [])
            self.assertEqual(rec["content_sha256"], rec0["content_sha256"])   # ①②のitemsは不変
            self.ensure(env)
            self.consume("b1b")   # G1 PASS(候補docの新訳=レコード)
            with self.assertRaises(cc.CliError):
                cc.cmd_revise(self.run_dir, "b1b", "human", self.uref, "x", ["p_nonexistent=訳"])

    def test_display_spec_of_is_a_pure_flag_independent_reader(self):
        self.assertIsNone(cc.display_spec_of(self.run_dir, "a2"))   # レコード無し
        with marks_connected(), Env(self.tmp) as env:
            self.form(env, "a2", cat1=[1, 2, 3], cat2=[4, 5])
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}):
            self.assertFalse(cc.protection_enabled())
            self.assertEqual(cc.display_spec_of(self.run_dir, "a2"), cc.DISPLAY_SPEC_V1)   # kill switchの影響を受けない
        before = rd(cc.paths_of(self.kp_dir_a2)["record"])
        cc.display_spec_of(self.run_dir, "a2")
        self.assertEqual(rd(cc.paths_of(self.kp_dir_a2)["record"]), before)   # 書込みなし
        self.assertIsNone(cc.display_spec_of(self.run_dir, "b1b"))
        src = inspect.getsource(cc.display_spec_of)
        self.assertNotIn("protection_enabled", src.split('"""')[2])   # 本体はflagを読まない
        d = jl(cc.paths_of(self.kp_dir_a2)["record"])
        d["display_spec"] = "UNKNOWN_V9"
        jd(cc.paths_of(self.kp_dir_a2)["record"], d)
        with self.assertRaises(ValueError):
            cc.display_spec_of(self.run_dir, "a2")

    def test_kill_switch_semantics_unchanged(self):
        self.assertEqual(cc.FLAG_NAME, "EIGO_KP_CONFIRMED_PROTECTION")
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "0"}):
            self.assertFalse(cc.protection_enabled())
        with mock.patch.dict(os.environ, {cc.FLAG_NAME: "1"}):
            self.assertTrue(cc.protection_enabled())


if __name__ == "__main__":
    unittest.main()
