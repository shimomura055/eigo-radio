# -*- coding: utf-8 -*-
r"""KP-PHRASE7-WORD5-PRODUCTION-01 委任_02: Key Phrase最大7(P7)+Key Word最大5(W5')のProduction配線のtest(API 0、全LLM mock)。
Opus条件A M-1〜M-9・R-2〜R-6、Fable確定D1〜D6の機械的証拠。
  - Prompt pin(P7==Trial-02のP7、W5'==Trial-02のW5と補足1行だけ違う、旧Prompt 2/2-V不変、ProductionはTrial非import)
  - DefaultOn(新flagなし。環境変数・引数で旧3+5へ戻せない=D1 R0)
  - er105の既定値で従来動作がバイト同一(Prompt 2経路)
  - select_p7(再選定ループ維持・metadata・telemetry[M-9])、一般化run_vocab_selection(not_single_word[D3])
  - harnessのfail-closed(M-5)、D6(旧3+5のdocは再生成しない)、AUTO(D2)不変
実行: .venv\Scripts\python.exe -m unittest er119_kp_p7w5_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import glob
import hashlib
import json
import os
import re
import unittest
from unittest import mock

import er003_v1_n3_01_scaffold_generate as sc
import er105_kp_fulltext_selector_01 as ft
import er119_kp_backfill_01 as bf
import er119_kp_candidates_01 as kcand
import er119_kp_human_review_01 as rv
import er119_kp_p7w5_prompts_01 as p7w5
import er119_kp_prompt_2v_01 as p2v
from er119_test_support_01 import ARTICLE, CALL1, CALL2, Env, KpTestCase, jl

ROOT = os.path.dirname(os.path.abspath(__file__))
P2_SHA = "a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a"
P2V_SHA = "e1d5349ce2fda897b74f0350817ced0d7385842c170d066721eb3917f012f5ec"
P7_SHA = "2e93019300f960e5ff3070dd83b12a81566b8ceb87b44b335d554a7a711eb291"
USER_LINE = "すでに選定されたKey Phraseに含まれる単語は、Key Word候補から除外する。"       # ユーザー原文の逐語(正しい表記。Fable確定D4)


class TestPromptPins(unittest.TestCase):
    def test_old_prompts_unchanged_and_remain(self):
        self.assertEqual(ft.PROMPT_2_SHA256, P2_SHA)
        self.assertEqual(p2v.PROMPT_2V_SHA256, P2V_SHA)

    def test_p7_sha_pinned(self):
        self.assertEqual(p7w5.P7_SHA256, P7_SHA)
        self.assertEqual(hashlib.sha256(p7w5.P7_TEXT.encode("utf-8")).hexdigest(), P7_SHA)

    def test_w5p_sha_pinned_and_matches_text(self):
        self.assertEqual(hashlib.sha256(p7w5.W5P_TEXT.encode("utf-8")).hexdigest(), p7w5.W5P_SHA256)
        self.assertEqual(p7w5.W5P_SHA256, "12d3370876d189f016cc49e26b2abcbe2618f028b380fe7fcff479554fa693b8")   # D4逐語1文版(DESIGN_01の187f1b87…は旧2文案)

    def test_p7_equals_trial_p7_and_w5p_differs_from_trial_w5_by_exactly_one_line_M8(self):
        import er124_kp_phrase_word_trial_01 as t       # test専用import(Production moduleはTrialをimportしない。下のtestで固定)
        self.assertEqual(p7w5.P7_TEXT, t.P7_TEXT)
        a, b = t.W5_TEXT.split("\n"), p7w5.W5P_TEXT.split("\n")
        self.assertEqual(len(a), len(b))
        diff = [(x, y) for x, y in zip(a, b) if x != y]
        self.assertEqual(len(diff), 1, diff)
        self.assertIn("一律除外しない", diff[0][0])
        self.assertEqual(diff[0][1], "- " + USER_LINE)

    def test_w5p_conditions_order_and_text(self):
        t = p7w5.W5P_TEXT
        heads = ["1. **本文一致（絶対条件）**", "2. **1語（絶対条件）**", "3. **上級者向けの学習価値**", "4. **易しい語の除外**", "5. **単語単体の学習価値**"]
        pos = [t.index(h) for h in heads]
        self.assertEqual(pos, sorted(pos))                                # 記載順
        self.assertIn("ただし必須条件にはしない", t)                          # 条件5は必須でない
        self.assertIn("条件3・4を、条件5より必ず優先する", t)
        self.assertIn("- 条件1・2(本文一致と1語)は必須。", t)
        for s in ("最大5件", "数合わせはしない", "日本語で1文(40字以内)", "出力直前に各候補を本文と照合し", "語数も併記してください"):
            self.assertIn(s, t)
        self.assertEqual(t.count(USER_LINE), 1)
        self.assertNotIn("一律除外しない", t)                                # Trial W5の逆の文言が残っていない
        self.assertNotIn("評価してよい", t)

    def test_production_modules_do_not_import_trial_er124(self):
        for b in ("er119_kp_p7w5_prompts_01.py", "er119_kp_candidates_01.py", "er119_kp_backfill_01.py", "er119_kp_human_review_01.py",
                  "er119_kp_wiring_01.py", "er105_kp_fulltext_selector_01.py"):
            with open(os.path.join(ROOT, b), encoding="utf-8") as f:
                src = f.read()
            self.assertIsNone(re.search(r"^\s*(import|from)\s+er12[34]_", src, re.M), b)

    def test_candidate_total_is_12_and_matches_constants(self):
        self.assertEqual((p7w5.KP_PHRASE_MAX, p7w5.KP_WORD_MAX, p7w5.KP_CANDIDATE_TOTAL_MAX), (7, 5, 12))
        self.assertEqual((bf.PHRASE_CAP, bf.WORD_CAP), (7, 5))
        self.assertEqual(rv.KP_CANDIDATE_MAX, 12)

    def test_message_builders_keep_prompt_body_and_use_distinct_prefixes(self):
        m7 = p7w5.build_p7_message("ART")
        mw = p7w5.build_w5_message("ART", ["a b"])
        self.assertTrue(m7.startswith(p7w5.P7_TEXT + ft.BODY_DELIMITER + "ART"))
        self.assertTrue(mw.startswith(p7w5.W5P_TEXT + ft.BODY_DELIMITER + "ART"))
        self.assertTrue(mw.endswith(p2v.ALREADY_DELIMITER + "- a b"))
        self.assertFalse(p7w5.p7_prefix_intact(mw))
        self.assertFalse(p7w5.w5_prefix_intact(m7))
        self.assertFalse(p7w5.p7_prefix_intact(ft.build_user_message("ART")))          # 旧Prompt 2はP7ではない
        self.assertTrue(p7w5.build_p7_message("ART", shown_phrases=["x y"], diagnostic_note="N").endswith(ft.NOTE_DELIMITER + "N"))

    def test_wrapper_selector_rejects_wrong_prompt_fail_closed_M5(self):
        with self.assertRaises(ft.FulltextSelectionError):
            p7w5.make_p7_selector_fn(p7w5.build_w5_message("A", []))
        with self.assertRaises(ft.FulltextSelectionError):
            p7w5.make_w5_selector_fn(p7w5.build_p7_message("A"))


class TestIsolationNewModule(unittest.TestCase):
    def test_p7w5_module_is_imported_only_by_er119_candidates_and_tests(self):
        """A/B/C(strategy_l経路)・Y Trial・各runnerは新moduleをimportしない(runnerは`er119_kp_wiring_01`経由の共通配線のみ)。"""
        offenders = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if "test" in b or b == "er119_kp_p7w5_prompts_01.py":
                continue
            with open(p, encoding="utf-8", errors="ignore") as f:
                if re.search(r"^\s*(import|from)\s+er119_kp_p7w5_prompts_01", f.read(), re.M) and b != "er119_kp_candidates_01.py":
                    offenders.append(b)
        self.assertEqual(offenders, [])


class TestHarnessFailClosedM5(KpTestCase):
    def test_legacy_selectors_and_wrong_prompts_raise_in_harness(self):
        with Env(self.tmp) as env:
            with self.assertRaises(AssertionError):
                ft.make_selector_fn("x")
            with self.assertRaises(AssertionError):
                p2v.make_vocab_selector_fn("x")
            with self.assertRaises(AssertionError):
                env._make1(p7w5.build_w5_message("A", []))          # call1(P7)のmockにW5'が来たら失敗
            with self.assertRaises(AssertionError):
                env._make2(p7w5.build_p7_message("A"))              # call2(W5')のmockにP7が来たら失敗


class TestDefaultOnNoFlagD1(KpTestCase):
    def test_default_path_uses_p7_then_w5p_with_all_env_cleared(self):
        env_clear = {k: v for k, v in os.environ.items() if not k.startswith("EIGO_")}
        with Env(self.tmp) as env, mock.patch.dict(os.environ, env_clear, clear=True), mock.patch.dict(os.environ, {"EIGO_KP_RESCUE": "1"}):
            self.ensure(env)
        c = rv.load_candidates(self.kp_dir)
        self.assertTrue(env.messages1[0].startswith(p7w5.P7_TEXT + ft.BODY_DELIMITER))
        self.assertTrue(env.messages2[0].startswith(p7w5.W5P_TEXT + ft.BODY_DELIMITER))
        self.assertEqual(c["prompt_sha256"], {"call1": P7_SHA, "call2": p7w5.W5P_SHA256})
        self.assertEqual(c["model_id"], {"call1": "gpt-6-luna", "call2": "gpt-6-luna"})
        self.assertEqual((env.n["call1"], env.n["call2"]), (1, 1))

    def test_no_flag_exists_to_return_to_legacy_3plus5(self):
        """D1=R0: 旧3+5へ戻すruntime flagは作らない(git revertで戻す)。P7/W5'の選択に環境変数・設定dict・引数の分岐が無い。"""
        for b in ("er119_kp_p7w5_prompts_01.py", "er119_kp_candidates_01.py"):
            with open(os.path.join(ROOT, b), encoding="utf-8") as f:
                src = f.read()
            self.assertNotIn("os.environ", src, b)
            self.assertNotIn("getenv", src, b)
        hits = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            n = os.path.basename(p)
            if "test" in n or n.startswith(("er124", "er123")):
                continue
            with open(p, encoding="utf-8", errors="ignore") as f:
                if re.search(r"EIGO_KP_P7|EIGO_KP_WORD5|EIGO_KP_3PLUS5|EIGO_KP_LEGACY", f.read()):
                    hits.append(n)
        self.assertEqual(hits, [])

    def test_generate_candidates_default_select_fn_is_select_p7(self):
        import inspect
        self.assertIn("select_fn or select_p7", inspect.getsource(kcand._generate_candidates_impl))

    def test_old_prompts_not_referenced_from_new_production_path(self):
        with open(os.path.join(ROOT, "er119_kp_candidates_01.py"), encoding="utf-8") as f:
            src = f.read()
        body = src[src.index("def _generate_candidates_impl"):src.index("def _shortfall_detail")]
        self.assertNotIn("PROMPT_2_TEXT", body)
        self.assertNotIn("PROMPT_2V", body)
        self.assertNotIn("p2v.make_vocab_selector_fn", body)
        body_bf = src[src.index("def _run_backfill"):src.index("def make_generate_fn")]
        self.assertNotIn("p2v.PROMPT_2V", body_bf)
        self.assertNotIn("run_selection_gate", body_bf)           # M-3: 補完はer105の再選定ループを使わない


class TestEr105DefaultsByteIdenticalPrompt2Path(unittest.TestCase):
    def test_build_message_and_prefix_defaults(self):
        self.assertEqual(ft.build_user_message("ART"), ft.PROMPT_2_TEXT + ft.BODY_DELIMITER + "ART")
        self.assertEqual(ft.build_user_message("ART", "N"), ft.PROMPT_2_TEXT + ft.BODY_DELIMITER + "ART" + ft.NOTE_DELIMITER + "N")
        self.assertTrue(ft.prompt_prefix_intact(ft.build_user_message("ART")))
        self.assertFalse(ft.prompt_prefix_intact(p7w5.build_p7_message("ART")))
        self.assertTrue(ft.prompt_prefix_intact(p7w5.build_p7_message("ART"), prompt_text=p7w5.P7_TEXT))

    def test_exclusion_note_default_wording_unchanged(self):
        n = ft.build_exclusion_note([{"phrase": "a b", "reasons": ["r"]}])
        self.assertEqual(n, "次の語句は、これまでの検証で不適合と確定しています。同じ語句、または同じ理由で不適合になる語句は選ばないでください"
                            "(条件を満たす別の語句がなければ、無理に3件に揃えず、適切な語句だけを選んでください)。\n- 「a b」: r")
        self.assertIn("無理に7件に揃えず", ft.build_exclusion_note([{"phrase": "a b", "reasons": ["r"]}], limit=7))

    def test_validate_default_max_is_3(self):
        import er030_key_phrase_db_hybrid_core_01 as core
        units = core.build_sentence_units(ARTICLE)
        four = [{"phrase": p, "declared_word_count": None} for p in ("time lag", "pushed prices up", "took a sharp turn", "built in")]
        v = ft.validate_and_resolve(four, units)
        self.assertFalse(v["ok"])
        self.assertTrue(any("件数が1〜3の範囲外" in x for x in v["reasons"]))
        v7 = ft.validate_and_resolve(four, units, max_items=7)
        self.assertTrue(v7["ok"], v7)
        self.assertNotIn("reason_ja", v["resolved"][0])           # reason_jaはキーが存在する時だけ(Prompt 2経路はバイト同一)
        self.assertNotIn("reason_ja", ft.build_original_items(v7["resolved"])[0])

    def test_reason_ja_passthrough_only_when_present(self):
        import er030_key_phrase_db_hybrid_core_01 as core
        units = core.build_sentence_units(ARTICLE)
        v = ft.validate_and_resolve([{"phrase": "time lag", "declared_word_count": 2, "reason_ja": "遅れ"}], units, max_items=7)
        self.assertEqual(ft.build_original_items(v["resolved"])[0]["reason_ja"], "遅れ")

    def test_run_fulltext_selection_default_metadata_is_prompt2(self):
        import tempfile
        items = [{"phrase": "time lag", "word_count": 2}]
        with tempfile.TemporaryDirectory() as t, mock.patch("time.sleep", lambda s: None):
            r = ft.run_fulltext_selection(ARTICLE, t, "a", "B1", make_call_fn=lambda m: (lambda: (json.dumps({"items": items}), "gpt-6-luna", "r1")))
            meta = jl(f"{t}/keywords_runtime_metadata.json")
        self.assertEqual(r["status"], ft.STATUS_PASS)
        self.assertEqual((meta["prompt_id"], meta["prompt_sha256"], meta["kp_count_max"]), ("kp_prompt_2", P2_SHA, 3))
        self.assertTrue(r["shortfall"])


class TestSelectP7(KpTestCase):
    def _run(self, items, **kw):
        import tempfile
        t = tempfile.mkdtemp(dir=self.tmp)
        seen = []

        def make(msg):
            seen.append(msg)
            return lambda: (json.dumps({"items": items}), "gpt-6-luna", "r1")
        with mock.patch("time.sleep", lambda s: None), mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", os.path.join(self.tmp, "tel.jsonl")):
            res = kcand.select_p7(ARTICLE, t, "aid", "B1", process="B1_SUPPORT", make_call_fn=make, **kw)
        return res, t, seen

    def test_seven_items_pass_with_reason_and_metadata_and_telemetry_M9(self):
        seven = [{"phrase": p, "reason_ja": f"理由{n}", "word_count": len(p.split())} for n, p in enumerate(
            ["time lag", "pushed prices up", "took a sharp turn", "built in", "feel a spike", "in stock", "raw beans"])]
        res, t, seen = self._run(seven)
        self.assertEqual(res["status"], "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(len(res["original_items"]), 7)
        self.assertEqual(res["original_items"][0]["reason_ja"], "理由0")
        self.assertEqual(res["kp_backend_used"], "fulltext_p2")
        self.assertEqual(len(seen), 1)
        meta = jl(f"{t}/keywords_runtime_metadata.json")
        self.assertEqual((meta["prompt_id"], meta["prompt_sha256"], meta["kp_count_max"], meta["kp_backend"]), ("kp_prompt_p7", P7_SHA, 7, "fulltext_p2"))
        with open(os.path.join(self.tmp, "tel.jsonl"), encoding="utf-8") as f:
            lines = [json.loads(x) for x in f if x.strip()]
        self.assertEqual(len(lines), 1)                                                   # M-9: telemetryを1行(scを経由しないため欠落させない)
        self.assertEqual((lines[0]["prompt_sha256"], lines[0]["prompt_id"], lines[0]["requested_backend"]), (P7_SHA, "kp_prompt_p7", "fulltext_p2"))
        self.assertNotEqual(lines[0]["prompt_sha256"], ft.PROMPT_2_SHA256)

    def test_four_items_are_not_a_nonconformance_no_retry(self):
        four = [{"phrase": p, "reason_ja": "x", "word_count": 2} for p in ("time lag", "pushed prices up", "took a sharp turn", "built in")]
        res, t, seen = self._run(four)
        self.assertEqual(res["status"], "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(len(seen), 1)                                                    # 件数不足(7未満)は不適合でない=再選定しない
        self.assertTrue(res["shortfall"])

    def test_eight_items_invalid_and_reselection_loop_kept_attempts_2(self):
        eight = [{"phrase": p, "reason_ja": "x", "word_count": 1} for p in ("time", "lag", "pushed", "prices", "took", "sharp", "turn", "built")]
        res, t, seen = self._run(eight)
        self.assertEqual(res["status"], ft.STATUS_INVALID)
        self.assertEqual(len(seen), ft.MAX_ATTEMPTS)                                      # 再選定ループ(MAX_ATTEMPTS=2)は承認済み仕様のまま維持
        self.assertTrue(all(p7w5.p7_prefix_intact(m) for m in seen))
        self.assertIn("件数が1〜7の範囲外", seen[1])                                         # 2回目のnote(件数の上限はP7の7)

    def test_item_noncompliance_triggers_reselection_with_note_limit_7(self):
        bad = [{"phrase": "not in the article", "reason_ja": "x", "word_count": 4}, {"phrase": "time lag", "reason_ja": "x", "word_count": 2}]
        res, t, seen = self._run(bad)
        self.assertEqual(len(seen), 2)
        self.assertEqual(res["status"], ft.STATUS_INVALID)
        self.assertIn("本文に連続一致しない", seen[1])

    def test_wrong_backend_rejected_and_routing_required(self):
        with self.assertRaises(ValueError):
            kcand.select_p7(ARTICLE, self.tmp, "a", "B1", process="B1_SUPPORT", kp_backend="strategy_l", make_call_fn=lambda m: None)
        with self.assertRaises(ft.FulltextSelectionError):
            kcand.select_p7(ARTICLE, self.tmp, "a", "B1", process="WRITER")           # Lunaのprocess以外は即停止(独自model指定を許さない)


class TestGeneralizedVocabSelectionW5(unittest.TestCase):
    def _call(self, items, already=None, **kw):
        import er030_key_phrase_db_hybrid_core_01 as core
        units = core.build_sentence_units(ARTICLE)
        msgs = []

        def make(msg):
            msgs.append(msg)
            return lambda: (json.dumps({"items": items}), "gpt-6-luna", "r")
        out = kcand.run_vocab_selection(ARTICLE, units, already or [{"display_phrase": "time lag"}], [], make_call_fn=make,
                                        sleep_fn=lambda s: None, spec=kw.pop("spec", p7w5.SPEC_W5P), **kw)
        return out, msgs

    def test_not_single_word_gate_and_order_validate_then_single_then_dup_D3(self):
        items = [{"phrase": "pushed prices up", "reason_ja": "x", "word_count": 3},      # 複数語 → not_single_word
                 {"phrase": "lag", "reason_ja": "x", "word_count": 1},                    # KP含有語 → duplicate_of_top3
                 {"phrase": "not there", "reason_ja": "x", "word_count": 2},              # 本文なし → validate(not_single_wordより先)
                 {"phrase": "spike", "reason_ja": "x", "word_count": 1}]
        out, msgs = self._call(items)
        self.assertEqual([(d["phrase"], d["stage"]) for d in out["dropped"]],
                         [("pushed prices up", "not_single_word"), ("lag", "duplicate_of_top3"), ("not there", "validate")])
        self.assertEqual([k["resolved"]["phrase"] for k in out["kept"]], ["spike"])
        self.assertTrue(p7w5.w5_prefix_intact(msgs[0]))

    def test_word_cap_5_overflow(self):
        words = [{"phrase": w, "reason_ja": "x", "word_count": 1} for w in ("spike", "stock", "insiders", "blends", "increases", "slowly")]
        out, _ = self._call(words)
        self.assertEqual(len(out["kept"]), 5)
        self.assertEqual([d["stage"] for d in out["dropped"]], ["overflow"])

    def test_p7_spec_has_no_single_word_gate_and_max_7(self):
        phr = [{"phrase": p, "reason_ja": "x", "word_count": len(p.split())} for p in ("time lag", "pushed prices up")]
        out, msgs = self._call(phr, already=[{"display_phrase": "took a sharp turn"}], spec=p7w5.SPEC_P7, shown_phrases=["took a sharp turn"])
        self.assertEqual(len(out["kept"]), 2)
        self.assertTrue(p7w5.p7_prefix_intact(msgs[0]))
        self.assertTrue(msgs[0].endswith(p2v.ALREADY_DELIMITER + "- took a sharp turn"))
        self.assertEqual(p7w5.SPEC_P7.max_items, 7)

    def test_default_spec_none_is_legacy_2v_unchanged(self):
        import er030_key_phrase_db_hybrid_core_01 as core
        units = core.build_sentence_units(ARTICLE)
        msgs = []

        def make(msg):
            msgs.append(msg)
            return lambda: (json.dumps({"items": [{"phrase": "built in", "reason_ja": "x", "word_count": 2}]}), "gpt-6-luna", "r")
        out = kcand.run_vocab_selection(ARTICLE, units, [{"display_phrase": "time lag"}], [], make_call_fn=make, sleep_fn=lambda s: None)
        self.assertTrue(p2v.prompt_prefix_intact(msgs[0]))
        self.assertEqual(len(out["kept"]), 1)               # 旧2-Vは複数語もkeep(単語1語Gateは新経路のspecだけ)


class TestD6LegacyDocIsNotRegenerated(KpTestCase):
    def test_resume_of_saved_3plus5_doc_does_not_call_generate_fn(self):
        """D6: 進行中の旧(3+5)候補docは、P7/W5'配線後もresumeで再生成されない(provenanceはdocのshaで追える)。"""
        from unittest import mock as _m
        import er119_kp_candidates_01 as kc
        items = [{"display_phrase": p, "source_span": p, "used_form": p, "key_phrase": p, "japanese_gloss": "意味", "source_sentence": "S.",
                  "source_sentence_id": "S1"} for p in ("time lag", "built in", "spike")]
        legacy = kc.candidate_doc_from_items(items, "b1b")
        legacy["prompt_ids"] = {"call1": "kp_prompt_2", "call2": "kp_prompt_2v"}
        legacy["prompt_sha256"] = {"call1": P2_SHA, "call2": P2V_SHA}
        calls = []

        def gen(round_no, ng):
            calls.append(round_no)
            return {"ok": True, "doc": legacy}
        kw = dict(run_dir=self.run_dir, family="x", slug="coffee", level="b1b", text=ARTICLE, generate_fn=gen, redundancy_fn=None, run_hint=self.run_dir)
        r1 = rv.ensure_kp_review(self.kp_dir, **kw)
        self.assertEqual(r1["state"], "PENDING")
        self.assertEqual(calls, [1])
        r2 = rv.ensure_kp_review(self.kp_dir, **dict(kw, generate_fn=lambda *a: (_ for _ in ()).throw(AssertionError("再生成された"))))
        self.assertEqual(r2["state"], "PENDING")
        saved = rv.load_candidates(self.kp_dir)
        self.assertEqual(saved["prompt_sha256"]["call1"], P2_SHA)      # 旧docのまま


class TestAutoSelectUnchangedD2(KpTestCase):
    def test_auto_takes_first_three_by_ai_rank_and_adv_vocab_first_five(self):
        with Env(self.tmp, call1=CALL1 + [{"phrase": "built in", "word_count": 2}, {"phrase": "feel a spike", "word_count": 3}]) as env:
            self.ensure(env)
        doc = rv.load_candidates(self.kp_dir)
        sel_std = rv.auto_select(doc, level="a2", ng_entries=[])
        sel_adv = rv.auto_select(doc, level="b1b", ng_entries=[])
        ids = [c["candidate_id"] for c in doc["candidates"]]
        self.assertEqual(sel_std["kp"], ids[:3])
        self.assertEqual(sel_adv["kp"], ids[:3])
        self.assertEqual(sel_adv["vocab"][:5], ids[:5])               # AUTOのvocab5は現行維持(単語組入れは新仕様なので導入しない)


if __name__ == "__main__":
    unittest.main()
