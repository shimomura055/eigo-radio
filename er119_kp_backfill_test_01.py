# -*- coding: utf-8 -*-
r"""KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_02: Gate除外候補補完のtest(API 0、全LLM mock。TBFxx = TEST_PLAN_01の番号、M-x/R-x = OPUS_REVIEW_01)。
実行: .venv\Scripts\python.exe -m unittest er119_kp_backfill_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import glob
import json
import os
import re
import unittest
from unittest import mock

import er003_v1_n3_01_scaffold_generate as sc
import er105_kp_fulltext_selector_01 as ft
import er119_kp_backfill_01 as bf
import er119_kp_backfill_golden_01 as g
import er119_kp_candidates_01 as kcand
import er119_kp_human_review_01 as rv
import er119_kp_prompt_2v_01 as p2v
from er119_test_support_01 import ARTICLE, CALL1, CALL2, Env, KpTestCase, jd, jl, rd

ROOT = os.path.dirname(os.path.abspath(__file__))
ON = {"EIGO_KP_BACKFILL": "1"}
OFF = {"EIGO_KP_BACKFILL": "0"}
BF_STAY = {"phrase": "stay high", "reason_ja": "補完A", "word_count": 2}
BF_STAGE = {"phrase": "cheaper blends", "reason_ja": "補完B", "word_count": 2}
BF_WORD = {"phrase": "increases", "reason_ja": "補完W", "word_count": 1}
CALL2_WORD = CALL2[:4] + [{"phrase": "slowly", "reason_ja": "単語", "word_count": 1}]     # 単語1件を含む5件


def gen(env_kwargs, backfill="1", *, kp_dir_sfx="", **ens):
    """Env + 環境変数固定でensure_kp_reviewまで通す。returns (env, doc)。"""
    class _R:
        pass
    return env_kwargs, backfill, ens


class BfCase(KpTestCase):
    def run_gen(self, backfill="1", text=ARTICLE, level="b1b", **env_kw):
        env_kw.setdefault("rescue_env", "0")           # 救済前の挙動で固定(救済は別test)。必要なtestは明示
        with Env(self.tmp, **env_kw) as env, mock.patch.dict(os.environ, {"EIGO_KP_BACKFILL": backfill}):
            r = self.ensure(env, level=level, text=text)
        self.assertEqual(r["state"], "PENDING")
        kp_dir = self.kp_dir if level == "b1b" else self.kp_dir_a2
        return env, rv.load_candidates(kp_dir)

    def direct(self, env_kw=None, backfill="1", ng_entries=None, **gkw):
        env_kw = dict(env_kw or {})
        env_kw.setdefault("rescue_env", "0")
        kp_dir = os.path.join(self.tmp, "direct", "key_phrases")
        with Env(self.tmp, **env_kw) as env, mock.patch.dict(os.environ, {"EIGO_KP_BACKFILL": backfill}):
            r = kcand.generate_candidates(ARTICLE, kp_dir, "aid_direct", "B1", "b1b", 1, ng_entries or [], process="B1_SUPPORT", **gkw)
        return env, r, kp_dir


# ============================================================ 純粋部品(LLM 0)
class TestPureParts(unittest.TestCase):
    def test_flag_default_on_and_single_reader_TBF20(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("EIGO_KP_BACKFILL", None)
            self.assertTrue(bf.backfill_enabled())            # 未設定=ON(承認済み仕様)
        for v, exp in (("0", False), ("1", True), ("", True), (" 0 ", False)):
            with mock.patch.dict(os.environ, {"EIGO_KP_BACKFILL": v}):
                self.assertEqual(bf.backfill_enabled(), exp, v)

    def test_flag_name_read_only_in_backfill_module_TBF20(self):
        """flag名(環境変数)を読むのは er119_kp_backfill_01.backfill_enabled の1箇所だけ。他のProduction .pyに実装側の参照がない。"""
        hits = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if "test" in b or b.startswith("er119_kp_backfill_golden"):
                continue
            with open(p, encoding="utf-8", errors="ignore") as f:
                src = f.read()
            if re.search(r"(environ|getenv).*EIGO_KP_BACKFILL", src) and b != "er119_kp_backfill_01.py":
                hits.append(b)
        self.assertEqual(hits, [])
        with open(os.path.join(ROOT, "er119_kp_backfill_01.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertEqual(len(re.findall(r"os\.environ\.get\(", src)), 1)
        self.assertEqual(len(re.findall(r"def backfill_enabled\(", src)), 1)

    def test_phrase_key_and_count_words_equivalent_to_er105(self):
        for t in ("Time  Lag", "it’s  fine", "“Quoted”  Phrase", "  A b  ", "ＡＢ c"):
            self.assertEqual(bf.rv.phrase_key(t), ft.phrase_key(t), t)
            self.assertEqual(bf.kind_of_phrase(t) == "word", ft.count_words(t) == 1, t)

    def test_kind_by_word_count_R1(self):
        self.assertEqual(bf.kind_of_phrase("increases"), "word")
        self.assertEqual(bf.kind_of_phrase("stay high"), "phrase")
        self.assertEqual(bf.kind_of_phrase("  slowly "), "word")

    def test_count_exclusions_rules_R4_R1_overflow_dup(self):
        dropped = [
            {"phrase": "a b", "stage": "validate", "origin": "call2"},
            {"phrase": "A  B", "stage": "cmu", "origin": "call2"},               # R-4: phrase_key重複は1件
            {"phrase": "word", "stage": "canonicalization", "origin": "call1"},
            {"phrase": "x y z", "stage": "overflow", "origin": "call2"},          # 数えない
            {"phrase": "h n", "stage": "human_ng", "origin": "call2"},
            {"phrase": "e x", "stage": "excluded", "origin": "call2"},
            {"phrase": "kept one", "stage": "symbol", "origin": "call2"},          # 現存候補と同じ句(二重防御)=数えない
            {"phrase": "dup top", "stage": "duplicate_of_top3", "origin": "call2"},
        ]
        cands = [{"selection_phrase": "kept one", "candidate_id": "p_1"}]
        c = bf.count_exclusions(dropped, cands)
        self.assertEqual((c["total"], c["phrase"], c["word"]), (5, 4, 1))
        self.assertEqual((c["human_ng"], c["excluded"]), (1, 1))
        self.assertEqual(c["by_stage"]["validate"], 1)
        self.assertNotIn("overflow", c["by_stage"])

    def test_count_excludes_rescued_originals_double_defense(self):
        cands = [{"selection_phrase": "catches their interest", "rescue": {"selection": {"original_phrase": "catch their interest"}}}]
        c = bf.count_exclusions([{"phrase": "catch their interest", "stage": "validate"}], cands)
        self.assertEqual(c["total"], 0)

    def test_plan_quota_and_pick_by_kind_R1(self):
        counts = {"phrase": 1, "word": 1, "total": 2}
        plan = bf.plan_quota(counts, n_cands=6, cap=8)
        self.assertEqual((plan["room"], plan["total"]), (2, 2))
        new = [{"kind": "phrase", "used_form": "a b"}, {"kind": "phrase", "used_form": "c d"}, {"kind": "word", "used_form": "e"}]
        taken, surplus = bf.pick_backfill(new, counts, plan)
        self.assertEqual([t["used_form"] for t in taken], ["a b", "e"])
        self.assertEqual([s["used_form"] for s in surplus], ["c d"])
        # 単語が無ければ単語枠は不足のまま(フレーズで数合わせしない)
        taken2, _ = bf.pick_backfill([{"kind": "phrase", "used_form": "a b"}, {"kind": "phrase", "used_form": "c d"}], counts, plan)
        self.assertEqual([t["used_form"] for t in taken2], ["a b"])

    def test_plan_quota_room_and_cap5(self):
        self.assertEqual(bf.plan_quota({"phrase": 3, "word": 0, "total": 3}, 8, 8)["total"], 0)
        self.assertEqual(bf.plan_quota({"phrase": 7, "word": 0, "total": 7}, 1, 8)["total"], 5)

    def test_count_deterministic_TBF25(self):
        import random
        dropped = [{"phrase": f"p{i} q{i}", "stage": s, "origin": "call2"} for i, s in enumerate(["validate", "cmu", "symbol", "human_ng", "excluded", "src_d1"] * 2)]
        base = bf.count_exclusions(dropped, [])
        for seed in range(3):
            d2 = list(dropped)
            random.Random(seed).shuffle(d2)
            c = bf.count_exclusions(d2, [])
            self.assertEqual((c["total"], c["phrase"], c["word"], c["by_stage"]), (base["total"], base["phrase"], base["word"], base["by_stage"]))

    def test_propagating_exceptions_R8(self):
        self.assertTrue(bf.is_propagating_exception(ft.FulltextSelectionError("x")))
        self.assertTrue(bf.is_propagating_exception(type("FamilyZStopSentinel", (Exception,), {})("stop")))
        self.assertFalse(bf.is_propagating_exception(RuntimeError("net")))
        self.assertFalse(bf.is_propagating_exception(ValueError("v")))


# ============================================================ M-5/M-7: 2-Vの入力構成
class TestVocabSelectionInputs(unittest.TestCase):
    ART = ARTICLE

    def _call(self, items, **kw):
        import er030_key_phrase_db_hybrid_core_01 as core
        units = core.build_sentence_units(self.ART)
        msgs = []

        def make(msg):
            msgs.append(msg)
            return lambda: (json.dumps({"items": items}), "gpt-6-luna", "r")
        out = kcand.run_vocab_selection(self.ART, units, [{"display_phrase": "pushed prices up"}], [], make_call_fn=make,
                                        sleep_fn=lambda s: None, **kw)
        return out, msgs

    def test_shown_and_containment_refs_are_separate_M5(self):
        items = [{"phrase": "time lag", "reason_ja": "x", "word_count": 2}, {"phrase": "pushed prices up", "reason_ja": "y", "word_count": 3}]
        out, msgs = self._call(items, shown_phrases=["pushed prices up", "time lag"])
        # 表示用に増やした『すでに選ばれた表現』はGateの比較先にならない(duplicate_of_top3の意味を変えない)。比較先は従来どおりcall1の3件
        self.assertEqual([k["resolved"]["phrase"] for k in out["kept"]], ["time lag"])
        self.assertEqual([(d["phrase"], d["stage"]) for d in out["dropped"]], [("pushed prices up", "duplicate_of_top3")])
        self.assertIn("- time lag", msgs[0])

    def test_default_shown_equals_already_items_backward_compat(self):
        out, msgs = self._call([{"phrase": "time lag", "reason_ja": "x", "word_count": 2}])
        self.assertTrue(msgs[0].endswith(p2v.ALREADY_DELIMITER + "- pushed prices up"))
        self.assertEqual(len(out["kept"]), 1)

    def test_note_is_appended_after_already_and_prompt_body_unchanged_M7(self):
        note = ft.build_exclusion_note([{"phrase": "feel a spike", "reasons": ["CMU未登録"]}])
        out, msgs = self._call([{"phrase": "time lag", "reason_ja": "x", "word_count": 2}], note=note)
        m = msgs[0]
        self.assertTrue(p2v.prompt_prefix_intact(m))
        self.assertTrue(m.startswith(p2v.PROMPT_2V_TEXT + ft.BODY_DELIMITER))
        self.assertTrue(m.endswith(ft.NOTE_DELIMITER + note))
        self.assertEqual(p2v.PROMPT_2V_SHA256, p2v.PROMPT_2V_SHA256_PINNED)
        self.assertEqual(ft.PROMPT_2_SHA256, "a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a")
        self.assertNotRegex(note, r"補完|あと\d+件|\d+件追加")      # 件数文言を足していない


# ============================================================ M-6: _gate_chainの制御構造
class TestGateChainContract(unittest.TestCase):
    def test_gate_chain_returns_status_without_loop_control_M6(self):
        def bad_canon(text, items, work, aid, process=None):
            return {"status": "CANONICALIZATION_INVALID"}      # item_reasonsなし=全体失敗
        d = []
        stages = {}
        with mock.patch.object(kcand, "_canon_item_failures", lambda w: {}):
            out = kcand._gate_chain("t", "w", "a", None, [{"display_phrase": "x"}], [{"origin": "call1", "raw_rank": 1, "reason_ja": "", "selection_phrase": "x"}],
                                    [0], d, ng_entries=[], canon_fn=bad_canon, src_fn=None, person_repair_fn=None, stages=stages)
        self.assertEqual(out, {"status": "CANON_FAILED", "canon_fail": "CANONICALIZATION_INVALID"})
        self.assertEqual(stages, {"canonicalization_0": "CANONICALIZATION_INVALID"})


# ============================================================ 補完の発動・件数・規則(生成経路を通す)
class TestBackfillFlow(BfCase):
    def test_E0_no_backfill_no_call_TBF01(self):
        env, doc = self.run_gen()
        self.assertEqual(env.n["call2"], 1)
        self.assertFalse(doc["backfill"]["triggered"])
        self.assertEqual(doc["backfill"]["reason"], "E=0")
        self.assertEqual(len(doc["candidates"]), 8)
        self.assertFalse(os.path.exists(f"{self.kp_dir}/kp_candidates/round_1/work/backfill_1"))

    def test_below_cap_without_exclusion_does_not_trigger_TBF02(self):
        env, doc = self.run_gen(call2=CALL2[:4])
        self.assertEqual(env.n["call2"], 1)
        self.assertFalse(doc["backfill"]["triggered"])
        self.assertEqual(len(doc["candidates"]), 7)              # AI島Adv型: 7件で補完しない(上限8までの差は補完しない)

    def test_below_cap_with_one_exclusion_backfills_only_E_TBF03(self):
        bad = {"phrase": "this phrase is not in the article", "reason_ja": "x", "word_count": 6}
        env, doc = self.run_gen(call2_seq=[CALL2[:3] + [bad], [BF_STAY, BF_STAGE]])
        b = doc["backfill"]
        self.assertTrue(b["triggered"])
        self.assertEqual((b["E"]["total"], b["N"]["total"]), (1, 1))
        self.assertEqual(len(doc["candidates"]), 3 + 3 + 1)      # 5-3の不足分(2件)や上限8までは補完しない=Eの1件のみ
        self.assertEqual(env.n["call2"], 2)

    def test_E2_takes_first_two_and_logs_surplus_TBF04_TBF05(self):
        env, doc = self.run_gen(bad_phrases=["feel a spike", "in stock"], call2_seq=[CALL2, [BF_STAY, BF_STAGE, BF_WORD]])
        b = doc["backfill"]
        self.assertEqual((b["E"]["total"], b["E"]["phrase"], b["E"]["word"]), (2, 2, 0))
        self.assertEqual([a["used_form"] for a in b["added"]], ["stay high", "cheaper blends"])
        self.assertEqual([s["used_form"] for s in b["surplus"]], ["increases"])        # 単語はE_word=0なので採らない(種類別)
        self.assertEqual(len(doc["candidates"]), 6 + 2)
        self.assertLessEqual(len(doc["candidates"]), rv.KP_CANDIDATE_MAX)
        self.assertEqual([c["ai_rank"] for c in doc["candidates"]], list(range(1, 9)))
        self.assertEqual([c["origin"] for c in doc["candidates"]][-2:], ["backfill", "backfill"])

    def test_word_exclusion_is_backfilled_with_word_not_phrase_R1(self):
        env, doc = self.run_gen(call2=CALL2_WORD, bad_phrases=["slowly"], call2_seq=[CALL2_WORD, [BF_STAY, BF_WORD]])
        b = doc["backfill"]
        self.assertEqual((b["E"]["phrase"], b["E"]["word"]), (0, 1))
        self.assertEqual([a["used_form"] for a in b["added"]], ["increases"])
        self.assertEqual([c["kind"] for c in doc["candidates"]][-1], "word")
        self.assertEqual(b["surplus"][0]["used_form"], "stay high")
        self.assertEqual(doc["shortfall_detail"]["unfilled_by_kind"], {"phrase": 0, "word": 0})

    def test_word_shortfall_is_not_padded_with_phrases_R1(self):
        env, doc = self.run_gen(call2_seq=[CALL2_WORD, [BF_STAY]], bad_phrases=["slowly"])
        self.assertEqual(doc["backfill"]["added"], [])
        self.assertEqual(doc["shortfall_detail"]["unfilled_by_kind"], {"phrase": 0, "word": 1})
        self.assertTrue(doc["shortfall"])

    def test_dup_of_top3_counts_and_gate_unchanged_TBF08(self):
        call2 = [{"phrase": "time lag", "reason_ja": "dup", "word_count": 2}] + CALL2[:2]
        bf_resp = [{"phrase": "time lag", "reason_ja": "dup", "word_count": 2}, BF_STAY]
        env, doc = self.run_gen(call2_seq=[call2, bf_resp])
        self.assertEqual(doc["backfill"]["E"]["by_stage"], {"duplicate_of_top3": 1})
        self.assertEqual([a["used_form"] for a in doc["backfill"]["added"]], ["stay high"])
        self.assertEqual(sum(1 for c in doc["candidates"] if c["selection_phrase"] == "time lag"), 1)

    def test_overflow_is_not_counted_TBF09(self):
        env, doc = self.run_gen(call2=CALL2 + [BF_STAY])             # 6件返答 -> 最大5件で切り捨て
        self.assertIn("overflow", [d["stage"] for d in doc["dropped"]])
        self.assertFalse(doc["backfill"]["triggered"])
        self.assertEqual(env.n["call2"], 1)

    def test_only_once_even_if_all_backfill_fail_TBF10(self):
        bad = [{"phrase": "nothing like this in text", "reason_ja": "x", "word_count": 5}]
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, bad, [BF_STAY]])
        self.assertEqual(env.n["call2"], 2)                           # 再補完しない(3回目のcallなし)
        self.assertEqual(doc["backfill"]["status"], "OK")
        self.assertEqual(doc["backfill"]["added"], [])
        self.assertEqual(len(doc["candidates"]), 7)                   # 上限未達を許容

    def test_same_gates_apply_to_backfill_items_TBF11(self):
        resp = [{"phrase": "a six word phrase for sure", "reason_ja": "x", "word_count": 6}, {"phrase": "not in the article text", "reason_ja": "x", "word_count": 5}, BF_STAY]
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, resp])
        stages = [(d["origin"], d["stage"]) for d in doc["dropped"] if d["origin"] == "backfill"]
        self.assertEqual(stages, [("backfill", "validate"), ("backfill", "validate")])
        self.assertEqual([a["used_form"] for a in doc["backfill"]["added"]], ["stay high"])

    def test_duplicates_of_existing_or_excluded_are_discarded_TBF12(self):
        resp = [{"phrase": "Built  In", "reason_ja": "x", "word_count": 2},          # 現存候補(phrase_key一致)
                {"phrase": "feel a spike", "reason_ja": "x", "word_count": 3},        # 除外された句
                BF_STAY]
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, resp])
        self.assertEqual([a["used_form"] for a in doc["backfill"]["added"]], ["stay high"])
        self.assertEqual(env.n["call2"], 2)                                           # 捨てたことで再callしない
        self.assertEqual(sum(1 for c in doc["candidates"] if c["selection_phrase"].lower() == "built in"), 1)

    def test_backfill_message_composition_TBF13(self):
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY]])
        m = env.messages2[1]
        self.assertTrue(p2v.prompt_prefix_intact(m))
        self.assertIn("- pushed prices up", m)                       # 現存候補が『選ばない』一覧に入る
        self.assertIn("- built in", m)
        self.assertIn("次の語句は、これまでの検証で不適合と確定しています", m)    # 既存exclusion note(新しい文言を作らない)
        self.assertIn("「feel a spike」", m)
        self.assertIsNone(re.search(r"\d+件(追加|補完)|あと\d", m.split(ft.BODY_DELIMITER, 1)[1].split(p2v.ALREADY_DELIMITER, 1)[1]))

    def test_initial_candidates_are_unchanged_and_backfill_appended_TBF14(self):
        env_on, on = self.run_gen("1", bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY]])
        import tempfile
        with tempfile.TemporaryDirectory() as t2:
            old_tmp, old_kp = self.tmp, self.kp_dir
            self.tmp = t2
            self.kp_dir = os.path.join(t2, "run1", "b1b", "key_phrases")
            self.run_dir = os.path.join(t2, "run1")
            _, off = self.run_gen("0", bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY]])
            self.tmp, self.kp_dir = old_tmp, old_kp
        n = len(off["candidates"])
        self.assertEqual(len(on["candidates"]), n + 1)
        for a, b in zip(on["candidates"][:n], off["candidates"]):
            self.assertEqual({k: v for k, v in a.items() if k != "kind"}, {k: v for k, v in b.items() if k != "kind"})   # 初回候補は完全不変
        self.assertEqual(on["candidates"][-1]["origin"], "backfill")
        # 初回のcanonicalization出力を上書きしていない(補完は別work dir)
        main = jl(f"{self.kp_dir}/kp_candidates/round_1/work/keywords_canonicalized.json")
        self.assertEqual(len(main["items"]), n)
        bfc = jl(f"{self.kp_dir}/kp_candidates/round_1/work/backfill_1/keywords_canonicalized.json")
        self.assertEqual(len(bfc["items"]), 1)

    def test_human_ng_phrase_returned_by_backfill_is_dropped_TBF15(self):
        ng = [rv.make_ng_entry({"candidate_id": rv.candidate_id_for("stay high"), "selection_phrase": "stay high", "used_form": "stay high"}, "NG", "tester")]
        env, r, _ = self.direct(dict(bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY, BF_STAGE]]), ng_entries=ng)
        doc = r["doc"]
        self.assertEqual([a["used_form"] for a in doc["backfill"]["added"]], ["cheaper blends"])
        self.assertNotIn("stay high", [c["selection_phrase"] for c in doc["candidates"]])
        self.assertIn("stay high", [d["phrase"] for d in doc["dropped"] if d["origin"] == "backfill"])

    def test_human_ng_counts_in_E_separately_P2(self):
        ng = [rv.make_ng_entry({"candidate_id": rv.candidate_id_for("in stock"), "selection_phrase": "in stock", "used_form": "in stock"}, "NG", "tester")]
        env, r, _ = self.direct(dict(call2_seq=[CALL2, [BF_STAY]]), ng_entries=ng)
        b = r["doc"]["backfill"]
        self.assertEqual((b["E"]["total"], b["E"]["human_ng"]), (1, 1))
        self.assertEqual([a["used_form"] for a in b["added"]], ["stay high"])


class TestMetadataCall1Exclusions(BfCase):
    """M-1: call1(Prompt 2)の最終attemptでitem単位に除外された句をEに数える(er105は無変更でmetadataから読む)。"""

    def test_call1_final_attempt_drops_are_counted_and_backfilled(self):
        def select_with_cmu_exclusion(text, work, article_id, source_level, **kw):
            res = sc.run_key_phrase_selection(text, work, article_id, source_level, **kw)
            p = f"{work}/keywords_runtime_metadata.json"
            meta = jl(p)
            meta["attempts_detail"][-1]["cmu_excluded"] = [{"index": 3, "phrase": "zzyzx word", "unregistered": ["zzyzx"]}]
            meta["attempts_detail"][-1]["exclusion_dropped"] = [{"index": 4, "phrase": "oldword", "prior_reasons": ["理由X"]}]
            jd(p, meta)
            return res
        env, r, _ = self.direct(dict(call2_seq=[CALL2[:3], [BF_STAY, BF_STAGE, BF_WORD]]), select_fn=select_with_cmu_exclusion)
        doc = r["doc"]
        b = doc["backfill"]
        self.assertEqual((b["E"]["total"], b["E"]["phrase"], b["E"]["word"]), (2, 1, 1))
        self.assertEqual(b["E"]["by_stage"], {"cmu": 1, "excluded": 1})
        c1 = [d for d in doc["dropped"] if d["origin"] == "call1"]
        self.assertEqual([(d["phrase"], d["stage"], d["raw_rank"]) for d in c1], [("zzyzx word", "cmu", 4), ("oldword", "excluded", 5)])
        self.assertEqual([a["used_form"] for a in b["added"]], ["stay high", "increases"])      # 種類別: フレーズ1+単語1

    def test_metadata_absent_is_safe_and_cleared_between_attempts(self):
        self.assertEqual(bf.read_call1_dropped("/nonexistent/dir"), [])
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            jd(f"{t}/keywords_runtime_metadata.json", {"attempts_detail": [{"cmu_excluded": [{"index": 0, "phrase": "x y", "unregistered": ["y"]}]}]})
            self.assertEqual(len(bf.read_call1_dropped(t)), 1)
            bf.clear_call1_metadata(t)
            self.assertEqual(bf.read_call1_dropped(t), [])
            bf.clear_call1_metadata(t)         # 無くても例外なし

    def test_off_does_not_read_or_clear_metadata(self):
        env, r, _ = self.direct(dict(), backfill="0")
        self.assertEqual(r["doc"]["backfill"], {"enabled": False, "triggered": False, "status": "DISABLED"})


# ============================================================ 外側retry(M-2/M-3)・失敗時続行(M-6)・伝播(R-8)・STOP(M-4)
class TestOuterRetryAndFailures(BfCase):
    def test_gate_drop_with_auto_lt3_no_longer_retries_on_TBF18a(self):
        call1b = [{"phrase": "Before you know it", "word_count": 4}, {"phrase": "stay high", "word_count": 2}]
        kw = dict(call1_seq=[CALL1, call1b], call2_seq=[[{"phrase": "in stock", "reason_ja": "x", "word_count": 2}], [BF_STAGE]],
                  bad_phrases=["pushed prices up", "took a sharp turn"])
        env_on, doc_on = self.run_gen("1", **kw)
        self.assertEqual(env_on.n["call1"], 1)                                   # 初回合格候補(in stock/time lag)を入れ替える全件再生成はしない
        phrases = [c["selection_phrase"] for c in doc_on["candidates"]]
        self.assertEqual(phrases[:2], ["time lag", "in stock"])                    # 初回合格候補は保持
        self.assertEqual(doc_on["outer_attempts"], 1)
        self.assertEqual(doc_on["backfill"]["E"]["total"], 2)

    def test_gate_drop_retry_leg_remains_when_off_TBF20(self):
        call1b = [{"phrase": "Before you know it", "word_count": 4}, {"phrase": "stay high", "word_count": 2}]
        env, doc = self.run_gen("0", call1_seq=[CALL1, call1b], call2_seq=[[{"phrase": "in stock", "reason_ja": "x", "word_count": 2}], CALL2[3:5]],
                                bad_phrases=["pushed prices up", "took a sharp turn"])
        self.assertEqual(env.n["call1"], 2)

    def test_rescued_not_auto_leg_removed_on_TBF18c(self):
        art = g.ART_R
        call1 = g.CALL1_C
        with Env(self.tmp, call1=call1, call2=[], canon_keys={"pushed prices up": "totally different"}, qa_mismatch={"pushed prices up"}) as env, \
                mock.patch.dict(os.environ, ON):
            self.ensure(env, text=art)
        doc = rv.load_candidates(self.kp_dir)
        c = next(x for x in doc["candidates"] if x["selection_phrase"] == "pushed prices up")
        self.assertFalse(c["auto_eligible"])
        self.assertEqual(env.n["call1"], 1)                                      # 救済済み(HR限定)候補を含む初回候補を捨てて作り直さない
        self.assertEqual(doc["outer_attempts"], 1)
        self.assertEqual(len(doc["candidates"]), 3)
        self.assertFalse(doc["backfill"]["triggered"])                           # 救済済みは除外に数えない(TBF06)

    def test_technical_failure_and_zero_candidates_still_retry_TBF18b(self):
        env, doc = None, None
        with Env(self.tmp, bad_phrases=[p["phrase"] for p in CALL1] + [p["phrase"] for p in CALL2], rescue_env="0") as env, mock.patch.dict(os.environ, ON):
            r = self.ensure(env)
        self.assertEqual(r["state"], "FAILED")
        self.assertEqual(env.n["call1"], sc.KP_OUTER_RETRY_MAX)                  # canonicalization全体失敗=技術失敗retryは存続(最大回数まで)

    def test_backfill_call_failure_keeps_initial_candidates_TBF19(self):
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, RuntimeError("net down")])
        b = doc["backfill"]
        self.assertEqual(b["status"], "FAILED")
        self.assertEqual(b["failure"], "call2_selection_failed")
        self.assertEqual(len(doc["candidates"]), 7)
        self.assertEqual(env.n["call1"], 1)                                      # 外側retryは起動しない
        self.assertEqual(doc["outer_attempts"], 1)

    def test_backfill_chain_technical_exception_is_caught_but_initial_kept_M6(self):
        real = sc.run_key_phrase_canonicalization

        def canon(text, items, work, aid, process=None, **kw):
            if work.endswith("backfill_1"):
                raise RuntimeError("canon api down")
            return real(text, items, work, aid, process=process, **kw)
        env, r, _ = self.direct(dict(bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY]]), canon_fn=canon)
        b = r["doc"]["backfill"]
        self.assertEqual(b["status"], "FAILED")
        self.assertIn("technical:RuntimeError", b["failure"])
        self.assertEqual(len(r["doc"]["candidates"]), 7)

    def test_routing_violation_in_backfill_propagates_R8(self):
        def vocab_call(msg):
            if "feel a spike" in msg:                                            # 補完call(noteにNG句が入る)だけ失敗させる
                def fn():
                    raise ft.FulltextSelectionError("routing violation")
                return fn
            return lambda: (json.dumps({"items": CALL2}), "gpt-6-luna", "r")
        with self.assertRaises(ft.FulltextSelectionError):
            self.direct(dict(bad_phrases=["feel a spike"]), vocab_call_fn=vocab_call)

    def test_stop_check_is_called_before_backfill_api_and_propagates_M4(self):
        class StopX(Exception):
            pass
        seen = []

        def stop(where):
            seen.append(where)
            if where.startswith("kp_backfill"):
                raise StopX(where)
        with Env(self.tmp, bad_phrases=["feel a spike"], rescue_env="0", call2_seq=[CALL2, [BF_STAY]]) as env, mock.patch.dict(os.environ, ON):
            kp_dir = os.path.join(self.tmp, "direct", "key_phrases")
            with self.assertRaises(StopX):
                kcand.generate_candidates(ARTICLE, kp_dir, "aid", "B1", "b1b", 1, [], process="B1_SUPPORT", stop_check_fn=stop)
            self.assertEqual(env.n["call2"], 1)                                   # 補完のAPI呼出は行われていない
        self.assertEqual([w for w in seen if w.startswith("kp_backfill")], ["kp_backfill:aid:round1:attempt1"])

    def test_stop_check_not_called_when_not_triggered(self):
        seen = []
        env, r, _ = self.direct(dict(), stop_check_fn=lambda w: seen.append(w))
        self.assertFalse([w for w in seen if w.startswith("kp_backfill")])


# ============================================================ resume・再生成・Family配線
class TestResumeRegenerateWiring(BfCase):
    def test_resume_reads_back_backfilled_doc_with_zero_api_TBF16(self):
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY]])
        n_after = env.total_llm_calls()
        sha = doc["candidates_sha256"]
        with Env(self.tmp, bad_phrases=["feel a spike"], rescue_env="0", call2_seq=[CALL2, [BF_STAY]]) as env2, mock.patch.dict(os.environ, ON):
            r2 = self.ensure(env2)
        self.assertEqual(r2["state"], "PENDING")
        self.assertEqual(env2.total_llm_calls(), 0)
        self.assertEqual(rv.load_candidates(self.kp_dir)["candidates_sha256"], sha)
        self.assertGreater(n_after, 0)

    def test_reselect_starts_from_initial_selection_and_backfills_once_per_round_TBF17(self):
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY], CALL2, [BF_STAGE]])
        self.assertEqual(env.n["call2"], 2)
        rv.op_reselect(self.kp_dir, ng={4: "x"}, by="human")
        with Env(self.tmp, bad_phrases=["feel a spike"], rescue_env="0", call2_seq=[CALL2, [BF_STAGE]]) as env2, mock.patch.dict(os.environ, ON):
            self.ensure(env2)
        doc2 = rv.load_candidates(self.kp_dir)
        self.assertEqual(doc2["round"], 2)
        self.assertEqual(env2.n["call1"], 1)                                      # 初回選定からやり直し
        self.assertEqual(env2.n["call2"], 2)                                      # round内で補完は1回
        self.assertTrue(doc2["backfill"]["triggered"])

    def test_x_y_z_use_single_wiring_point_and_no_family_branch_TBF21(self):
        for b in ("er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py", "er121_family_y_runner_01.py",
                  "er119_kp_wiring_01.py"):
            with open(os.path.join(ROOT, b), encoding="utf-8", errors="ignore") as f:
                src = f.read()
            self.assertNotIn("backfill", src.lower(), b)                          # Family別の補完分岐なし(共通経路_generate_candidates_implだけ)
        with open(os.path.join(ROOT, "er119_kp_candidates_01.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertEqual(len(re.findall(r"_run_backfill\(", src)), 2)             # 定義1+呼出1(_generate_candidates_impl)

    def test_z_src_d1_and_person_repair_apply_to_backfill_items_R5(self):
        calls = []

        def src_fn(items):
            drop = {it["rank"]: ["SRC D1: stub"] for it in items if "cheaper blends" in (it.get("used_form") or "")}
            return {it["rank"]: dict(it, source_sentence_id="S1") for it in items}, drop

        def person_fn(merged):
            calls.append(len(merged["items"]))
            return merged
        env, r, _ = self.direct(dict(bad_phrases=["feel a spike", "in stock"], call2_seq=[CALL2, [BF_STAGE, BF_STAY]]),
                                src_fn=src_fn, person_repair_fn=person_fn)
        doc = r["doc"]
        self.assertEqual([a["used_form"] for a in doc["backfill"]["added"]], ["stay high"])
        self.assertIn(("backfill", "src_d1"), [(d["origin"], d["stage"]) for d in doc["dropped"]])
        self.assertEqual(len(calls), 2)                                            # 初回(6件)と補完(2件)の両方に人称整合がかかる
        self.assertEqual(doc["candidates"][-1]["gates"]["src_d1"], "PASS")

    def test_person_repair_out_dir_is_separated_for_backfill_even_with_runner_closure_R5(self):
        """er026のrunnerは person_fn の中で毎回 make_person_repair_fn(...)(merged) を呼ぶ形。補完中だけ出力先を別dirにする。"""
        outs = []

        real_align = kcand.ga.align_glosses

        def fake_align(merged, text, factory, out_dir=None, article_id="", enabled=None, only_ranks=None, **kw):
            if "gloss_person_repair" not in (out_dir or ""):
                return real_align(merged, text, factory, out_dir=out_dir, article_id=article_id, enabled=enabled, only_ranks=only_ranks, **kw)
            outs.append(out_dir)
            return {"merged": merged}
        with mock.patch.object(kcand.ga, "select_person_mismatches", lambda items: list(items)), mock.patch.object(kcand.ga, "align_glosses", fake_align):
            def person_fn(merged):
                return kcand.make_person_repair_fn("t", lambda m: None, "/w/kp", "aid")(merged)
            env, r, _ = self.direct(dict(bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY]]), person_repair_fn=person_fn)
        self.assertEqual(outs, ["/w/kp/gloss_person_repair", "/w/kp/gloss_person_repair_backfill"])
        self.assertIsNone(kcand._person_repair_subdir.get())                       # 補完後は必ず元へ戻る

    def test_person_repair_subdir_reset_even_on_exception_R5(self):
        def boom(merged):
            raise RuntimeError("x")
        calls = []

        def person_fn(merged):
            calls.append(1)
            if len(calls) > 1:
                return boom(merged)
            return merged
        env, r, _ = self.direct(dict(bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY]]), person_repair_fn=person_fn)
        self.assertEqual(r["doc"]["backfill"]["status"], "FAILED")
        self.assertIsNone(kcand._person_repair_subdir.get())

    def test_abc_modules_do_not_import_backfill_module_TBF22(self):
        offenders = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if b.startswith("er119_") or "test" in b:
                continue
            with open(p, encoding="utf-8", errors="ignore") as f:
                if re.search(r"^\s*(import|from)\s+er119_kp_backfill_01", f.read(), re.M):
                    offenders.append(b)
        self.assertEqual(offenders, [])
        with open(os.path.join(ROOT, "er119_kp_backfill_01.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotRegex(src, r"^\s*(import|from)\s+(er003|er062|er019|er026|er121)", )   # 共有生成module・runnerをimportしない(純粋部品)


# ============================================================ F-2 データ契約・HR依頼書
class TestDataContractAndRequestMd(BfCase):
    def test_data_contract_fields_F2_TBF26(self):
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY]])
        for c in doc["candidates"]:
            for k in ("candidate_id", "kind", "origin", "ai_rank", "auto_eligible", "flags", "human_selectable", "used_form", "japanese_gloss", "source_sentence"):
                self.assertIn(k, c, k)
            self.assertIn(c["kind"], ("phrase", "word"))
            self.assertIn(c["origin"], ("call1", "call2", "backfill"))
            for fk in ("qa_fail", "gloss_hr_pending", "similar_to_ng", "redundant_with"):
                self.assertIn(fk, c["flags"])
        b = doc["backfill"]
        for k in ("enabled", "triggered", "status", "E", "N", "added", "surplus", "dropped_by_stage", "prompt_id", "prompt_sha256", "model_id", "response_id", "attempts"):
            self.assertIn(k, b, k)
        for k in ("total", "phrase", "word", "human_ng", "excluded", "by_stage", "items"):
            self.assertIn(k, b["E"], k)
        self.assertEqual(b["prompt_sha256"], p2v.PROMPT_2V_SHA256)
        self.assertEqual(b["model_id"], "gpt-6-luna")
        sd = doc["shortfall_detail"]
        self.assertEqual((sd["n_candidates"], sd["cap"], sd["missing"], sd["E_total"], sd["backfilled"]), (8, 8, 0, 1, 1))
        # 保存済みfileにも含まれ、sha対象(candidates_sha256はbackfill込みの文書全体)
        saved = rv.load_candidates(self.kp_dir)
        self.assertEqual(saved["backfill"]["status"], "OK")
        self.assertEqual(saved["candidates_sha256"], rv.candidates_sha256(saved))

    def test_request_md_shows_backfill_summary_and_flag(self):
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, [BF_STAY]])
        md = rd(f"{self.kp_dir}/kp_human_review_request.md")
        self.assertIn("補完候補 1件を末尾に追加しました", md)
        self.assertIn("補完候補(Gate除外の代替)", md)
        self.assertIn("stay high", md)

    def test_request_md_unchanged_when_not_triggered(self):
        env, doc = self.run_gen()
        md = rd(f"{self.kp_dir}/kp_human_review_request.md")
        self.assertNotIn("補完", md)

    def test_request_md_shows_failure_when_backfill_failed(self):
        env, doc = self.run_gen(bad_phrases=["feel a spike"], call2_seq=[CALL2, RuntimeError("x")])
        md = rd(f"{self.kp_dir}/kp_human_review_request.md")
        self.assertIn("補完は失敗しました", md)

    def test_auto_select_works_with_backfilled_candidates_tail(self):
        env, doc = self.run_gen(bad_phrases=["feel a spike", "pushed prices up", "took a sharp turn", "time lag"],
                                call2_seq=[CALL2, [BF_STAY, BF_STAGE, BF_WORD]])
        sel = rv.auto_select(doc, level="b1b", ng_entries=[])
        self.assertEqual(len(sel["kp"]), 3)                                       # 補完候補もai_rank順にAUTO対象(auto_eligible)
        self.assertLessEqual(len(sel["vocab"]), 5)


# ============================================================ 純リファクタgolden(R-6 / TBF24, TBF20, TBF01)
class TestGoldenPureRefactorTBF24(unittest.TestCase):
    def _golden(self, name):
        with open(g.golden_path(name), encoding="utf-8") as f:
            return json.load(f)

    def test_off_candidate_docs_equal_pre_extraction_golden_TBF20(self):
        """EIGO_KP_BACKFILL=0: 全scenarioで抽出前goldenと完全一致(候補・dropped・外側retry挙動とも現行へ完全復帰)。"""
        for name in g.SCENARIOS:
            with self.subTest(name):
                self.assertEqual(g.strip_additive(g.run_scenario(name, OFF)), self._golden(name))

    def test_on_candidate_docs_equal_golden_when_E0_TBF01(self):
        """既定ON: 除外0(E=0)のscenarioは補完が発動せず、追記専用項目を除いて抽出前goldenと完全一致。"""
        for name in g.ON_EQUAL_SCENARIOS:
            with self.subTest(name):
                doc = g.run_scenario(name, ON)
                self.assertFalse(doc["backfill"]["triggered"])
                self.assertEqual(g.strip_additive(doc), self._golden(name))


if __name__ == "__main__":
    unittest.main()
