# -*- coding: utf-8 -*-
r"""KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 委任_02: N5の正式配線(er119_kp_candidates_01経由・X/Y/Z共通の1配線点)のtest(API 0、LLMは全てmock)。
er138は**実コード**を通し、低水準の送信関数(n5._send)だけをscriptedに差し替える(既存のer119 testはN5をidentity stubにしており、N5自体はここで検証する)。
確認項目: 既定ON(flag/env不要)・工程順(L1=call1とcall2の間、L3=canon直後)・データ受渡し(used_form=key_phrase=N5形、source_span/selection_phrase=本文根拠)・
E計数(n5_select非計数/n5_verify・n5_check計数)・補完/外側retry/再選定/resumeで同じ関数を通る・N5段失敗=外側retry(N5なし候補を出さない)・STOP伝播・
既存kill switch(EIGO_KP_RESCUE/GLOSS_ALIGNMENT/BACKFILL=0)で迂回されない・単語はN5対象外・X/Yの人称整合・旧到達不能経路の静的到達性・後続工程(finalize/exporter/er128人称検査)。
実行: .venv\Scripts\python.exe -m unittest er138_wiring_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import glob
import importlib.util
import json
import logging
import os
import re
import unittest
from unittest import mock

import er003_key_words_gloss_alignment as ga
import er003_v1_n3_01_scaffold_generate as sc
import er119_kp_backfill_01 as bf
import er119_kp_candidates_01 as kcand
import er119_kp_human_review_01 as rv
import er138_kp_n5_generalization_01 as n5
from er119_test_support_01 import ARTICLE, CALL1, CALL2, Env, KpTestCase

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_CLEAN = {"EIGO_KP_RESCUE": "1", "EIGO_KP_BACKFILL": "1", "EIGO_KP_GLOSS_ALIGNMENT": "1"}


def _spans(user, marker):
    return re.findall(marker, user, re.M)


class SmartSend:
    """n5._sendの差替え。stageごとのhandler(user, self)->dict。既定=素通し(全keep・一般化なし・VER5 OK・CHK5 SAME)。呼出記録を持つ。"""

    def __init__(self, **handlers):
        self.h = handlers
        self.calls = []

    def stage_calls(self, stage):
        return [c for c in self.calls if c[0] == stage]

    def __call__(self, stage, model, user, schema, max_out):
        self.calls.append((stage, model, user))
        h = self.h.get(stage)
        out = h(user, self) if h is not None else getattr(self, "default_" + stage)(user)
        if isinstance(out, Exception):
            raise out
        raw = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
        return raw, {"model_req": model, "model_id": model, "model_version": None, "in": 100, "out": 50, "cached": 0, "sec": 0.0, "cost_jpy": 0.01}

    # ---- 既定handler
    def default_b1(self, user):
        return {"candidates": []}

    def default_sel(self, user):
        spans = _spans(user, r"^(\d+)\. (.*?) \[WordNet複合語見出し")
        return {"judgements": [{"id": int(i), "cls": "C", "chunk_type": "phrasal_verb", "reason_ja": f"理由{i}", "difficulty": "upper_intermediate", "keep": True,
                                "passive_fragment": False} for i, _ in spans]}

    def default_gen5(self, user):
        items = []
        for m in re.finditer(r"^(\d+)\. 語句: (.*)\n   トークン: (.*)$", user, re.M):
            i, span, tk = int(m.group(1)), m.group(2), m.group(3)
            toks = [(int(n), w) for n, w in re.findall(r"\[(\d+)\]([^\s\[]+)", tk)]
            tl = [{"n": n, "label": "CORE", "lemma": re.sub(r"[^\w'\-]", "", w.lower())} for n, w in toks]
            hw = " ".join(t["lemma"] for t in tl)
            items.append({"id": i, "source_sense_ja": f"本文語義{span}", "arg_notes": [], "headword_frame": hw, "frame_change": ["NONE"], "tokens": tl,
                          "gloss_ja": f"N5訳{span}", "sense_note_ja": "s", "note_ja": "n"})
        return {"items": items}

    def default_ver5(self, user):
        n = len(re.findall(r"^\d+\. 本文の語句:", user.split("【検査対象】")[-1], re.M))
        return {"verdicts": [{"id": i, "verdict": "OK", "meaning_preserved": True, "gloss_consistent": True, "natural_headword": True, "issue": "", "fix_display_form": "",
                              "fix_gloss_ja": "", "source_sense_ja": "s", "argument_type_ok": True, "frame_preserved": "SAME"} for i in range(1, n + 1)]}

    def default_chk5(self, user):
        n = len(re.findall(r"^\d+\. 本文の語句:", user.split("【検査対象】")[-1], re.M))
        return {"checks": [{"id": i, "context_sense_ja": "c", "example_en": "e", "relation": "SAME", "fix_display_form": "", "fix_gloss_ja": "", "reason_ja": ""}
                           for i in range(1, n + 1)]}


def gen_tokens(span_to_labels):
    """GEN5 handler: {span: ([(label, lemma)...], headword_frame, gloss)}。指定のspan以外は素通し。"""
    base = SmartSend()

    def handler(user, self):
        out = base.default_gen5(user)
        for m in re.finditer(r"^(\d+)\. 語句: (.*)\n", user, re.M):
            i, span = int(m.group(1)), m.group(2)
            if span in span_to_labels:
                labels, hw, gloss = span_to_labels[span]
                row = next(x for x in out["items"] if x["id"] == i)
                row["tokens"] = [{"n": n, "label": lb, "lemma": lem} for n, (lb, lem) in enumerate(labels, 1)]
                row["headword_frame"] = hw
                row["gloss_ja"] = gloss
        return out
    return handler


class N5Case(KpTestCase):
    def run_gen(self, send, *, env_kw=None, environ=None, ng_entries=None, person_gloss=None, **gkw):
        env_kw = dict(env_kw or {})
        env_kw.setdefault("rescue_env", "1")
        env_kw["n5_stub"] = False
        kp_dir = os.path.join(self.tmp, "direct", "key_phrases")
        envv = dict(ENV_CLEAN)
        envv.update(environ or {})
        with Env(self.tmp, **env_kw) as env, mock.patch.dict(os.environ, envv), mock.patch.object(n5, "_send", send):
            if person_gloss is not None:
                # 既存のgloss整合(alignment) mock: 具体人称語『彼』を含む現glossの対象にだけ人称語なしの訳を返す(それ以外はEnvの既定mock)
                from er119_test_support_01 import _parse_items_json

                def wrapped(msg, **kw):
                    targets = _parse_items_json(msg, "【対象項目】\n")
                    if not any("彼" in (t.get("current_japanese_gloss") or "") for t in targets):
                        return env._gloss(msg, **kw)
                    out = [{"rank": t["rank"], "current_gloss_consistent": False, "japanese_gloss": person_gloss, "qa_reflects_all_key_phrase_words": "PASS",
                            "reasoning": "r", "added_word_mappings": []} for t in targets]

                    def fn():
                        env.n["gloss_person"] += 1
                        return json.dumps({"items": out}, ensure_ascii=False), "gpt-6-luna", "person_resp"
                    fn.last_usage = None
                    return fn
                with mock.patch.object(ga, "make_alignment_fn", wrapped):
                    r = kcand.generate_candidates(ARTICLE, kp_dir, "aid_n5", "B1", "b1b", 1, ng_entries or [], process="B1_SUPPORT", **gkw)
            else:
                r = kcand.generate_candidates(ARTICLE, kp_dir, "aid_n5", "B1", "b1b", 1, ng_entries or [], process="B1_SUPPORT", **gkw)
        if r.get("ok"):   # 実運用の保存/署名はsort_keys=True(rv._sha)。dict keyにNone等が混じると本番だけ落ちる(2026-10-30 X実run所見)ので全scenarioで検査
            json.dumps(r["doc"], ensure_ascii=False, sort_keys=True)
        return env, r, kp_dir

    def doc(self, send, **kw):
        env, r, kp_dir = self.run_gen(send, **kw)
        self.assertTrue(r["ok"], r)
        return env, r["doc"], kp_dir


class TestDefaultOnAndOrder(N5Case):
    def test_default_on_without_any_flag_all_stages_fire(self):
        s = SmartSend(b1=lambda u, me: {"candidates": [{"span": "raw beans in stock", "sentence": "Cafes keep raw beans in stock, so they don't feel a spike at once."}]})
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in ENV_CLEAN:
                os.environ.pop(k, None)
            env, doc, _ = self.doc(s, environ={})
        stages = {c[0] for c in s.calls}
        self.assertEqual(stages, {"b1", "sel", "gen5", "ver5", "chk5"})
        g = doc["generalization"]
        self.assertEqual(g["method"], "N5@T3-2026-10-30")
        self.assertEqual(g["models_requested"]["ver5"], "gemini-3.8-flash")
        self.assertEqual(g["prompt_sha16"]["B1"], "97dd3c281a2858f3")
        self.assertGreaterEqual(g["n_llm_calls"], 5)
        phrases = [c for c in doc["candidates"] if c["kind"] == "phrase"]
        self.assertTrue(phrases and all("n5" in c["item"] for c in phrases))
        self.assertTrue(all(c["item"]["n5"]["method"] == n5.METHOD_ID for c in phrases))

    def test_n5_module_has_no_env_or_flag_reader(self):
        with open(os.path.join(ROOT, "er138_kp_n5_generalization_01.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("os.environ.get(", src)
        self.assertNotIn("getenv", src)
        self.assertIsNone(re.search(r"EIGO_KP_N5|N5_ENABLED|N5_OFF", src))
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if "test" in b or b.startswith("er138"):
                continue
            with open(p, encoding="utf-8", errors="ignore") as f:
                t = f.read()
            self.assertIsNone(re.search(r"EIGO_KP_N5", t), b)

    def test_L1_between_call1_and_call2_and_picked_phrases_feed_w5(self):
        sel_keep = {"pushed prices up": True, "took a sharp turn": True, "time lag": False}

        def sel(user, me):
            rows = SmartSend().default_sel(user)
            for r in rows["judgements"]:
                span = re.findall(r"^%d\. (.*?) \[WordNet" % r["id"], user, re.M)[0]
                if not sel_keep.get(span, True):
                    r["cls"], r["keep"] = "F", False
            return rows
        s = SmartSend(sel=sel)
        env, doc, _ = self.doc(s)
        used = [c["selection_phrase"] for c in doc["candidates"] if c["kind"] == "phrase"]
        self.assertEqual(sorted(used), ["pushed prices up", "took a sharp turn"])
        # W5'(call2)へ渡るalready_items/shown = N5が選んだフレーズ集合(SELで落ちたtime lagは含まれない)
        shown = env.messages2[0]
        self.assertIn("pushed prices up", shown)
        self.assertNotIn("time lag", shown.split("【記事本文】")[0].split("選ばれた")[-1] if "選ばれた" in shown else "")
        self.assertEqual(doc["generalization"]["attempts"][-1]["l1"][0]["n_picked"], 2)
        # n5_selectで落ちたP7候補はdroppedに残るがEに数えない(補完を誘発しない)
        self.assertIn("time lag", [d["phrase"] for d in doc["dropped"] if d["stage"] == "n5_select"])
        self.assertFalse(doc["backfill"]["triggered"])
        self.assertEqual(env.n["call1"], 1)

    def test_L3_after_canon_before_cmu_post_canon_order(self):
        order = []
        real_cmu = kcand.cmu.canonicalized_check
        real_run = n5.run_l3

        def spy_l3(text, targets, ctx):
            order.append("n5_l3")
            return real_run(text, targets, ctx)

        def spy_cmu(items):
            order.append("cmu_post_canon")
            return real_cmu(items)
        s = SmartSend()
        with mock.patch.object(kcand.cmu, "canonicalized_check", spy_cmu), mock.patch.object(n5, "run_l3", spy_l3):
            self.doc(s)
        self.assertEqual(order[:2], ["n5_l3", "cmu_post_canon"])

    def test_B1_candidate_enters_through_existing_gates_and_origin_recorded(self):
        b1 = {"candidates": [{"span": "raw beans in stock", "sentence": "x"},          # 本文一致・有効
                             {"span": "not in the article at all", "sentence": "x"},      # 本文不一致 -> n5_pool
                             {"span": "Retail prices follow", "sentence": "x"}]}          # 本文一致
        s = SmartSend(b1=lambda u, me: b1)
        env, doc, _ = self.doc(s)
        l1 = doc["generalization"]["attempts"][-1]["l1"][0]
        self.assertEqual(l1["n_b1_returned"], 3)
        rej_reasons = [r["reasons"][0] for r in l1["pool_rejected"]]
        self.assertTrue(any("本文に連続一致しない" in r for r in rej_reasons))
        self.assertGreaterEqual(l1["picked_origin"]["B1"], 1)
        b1c = [c for c in doc["candidates"] if c["item"].get("n5", {}).get("origin") == "B1"]
        self.assertTrue(b1c)
        # B1由来にはPROD_GLOSS(P7由来のcanon・ga後gloss)が無い(Opus M4a)
        self.assertNotIn("PROD_GLOSS", json.dumps(b1c[0]["item"]["n5"].get("gloss_source")))

    def test_N5_form_flows_to_used_form_and_source_span_untouched(self):
        s = SmartSend(gen5=gen_tokens({"pushed prices up": ([("CORE", "push"), ("SLOT_THING", ""), ("CORE", "up")], "push something up", "物を押し上げる")}))
        env, doc, _ = self.doc(s)
        c = next(c for c in doc["candidates"] if c["selection_phrase"] == "pushed prices up")
        it = c["item"]
        self.assertEqual(c["used_form"], "push something up")
        self.assertEqual(it["used_form"], it["key_phrase"])
        self.assertEqual(c["japanese_gloss"], "物を押し上げる")
        self.assertEqual(it["source_span"], "pushed prices up")                       # 本文根拠
        self.assertEqual(it["display_phrase"], "pushed prices up")
        self.assertEqual(c["word_count"], 3)
        self.assertEqual(c["kind"], "phrase")
        self.assertEqual(it["n5"]["canon_pre"]["key_phrase"], "pushed prices up")      # canon形は退避
        self.assertEqual(it["n5"]["canon_key_phrase_pre"], "pushed prices up")
        self.assertTrue(it["n5"]["source_span_matches_item"])
        self.assertEqual(it["gloss_alignment_status"], "ALIGNED")
        self.assertEqual(c["gates"]["gloss"], "ALIGNED")
        self.assertEqual(it["qa_overall_status"], "PASS")                              # QA12は canon形の判定として保持(β′)
        self.assertEqual(rv.presentation_blockers(c), [])                                # presentable filterの契約を満たす

    def test_words_are_not_n5_targets(self):
        s = SmartSend()
        env, doc, _ = self.doc(s)
        words = [c for c in doc["candidates"] if c["kind"] == "word"]
        self.assertTrue(words)
        self.assertTrue(all("n5" not in w["item"] for w in words))
        chk_prompts = " ".join(c[2] for c in s.stage_calls("chk5"))
        for w in words:
            self.assertNotIn(f"本文の語句: {w['selection_phrase']}\n", chk_prompts)


class TestEAccountingAndBackfill(N5Case):
    def test_n5_verify_drop_counts_as_E_and_backfill_runs_L1_and_L3_again(self):
        rej = {"done": False}

        def ver(user, me):
            out = SmartSend().default_ver5(user)
            if not rej["done"]:
                rej["done"] = True
                out["verdicts"][0].update(verdict="REJECT", meaning_preserved=False, issue="語義が変わる")
            return out
        bf_phrase = {"phrase": "stay high", "reason_ja": "補完", "word_count": 2}
        s = SmartSend(ver5=ver)
        env, doc, _ = self.doc(s, env_kw=dict(call1_seq=[CALL1, [bf_phrase]]))
        self.assertTrue(doc["backfill"]["triggered"])
        self.assertEqual(doc["backfill"]["E"]["by_stage"].get("n5_verify"), 1)
        self.assertEqual(doc["backfill"]["status"], "OK")
        added = [a["used_form"] for a in doc["backfill"]["added"]]
        self.assertEqual(added, ["stay high"])
        att = doc["generalization"]["attempts"][-1]
        self.assertEqual(len(att["l1"]), 2)                                              # 初回L1 + 補完L1(SEL+pickのみ)
        self.assertFalse(att["l1"][1]["include_b1"])
        self.assertEqual([x["prefix"] for x in att["l3"]], ["initial", "backfill_"])    # 補完も同じL3を通る
        bf_c = next(c for c in doc["candidates"] if c["origin"] == "backfill")
        self.assertEqual(bf_c["item"]["n5"]["method"], n5.METHOD_ID)
        tags = {m["tag"] for m in doc["generalization"]["attempts"][-1]["llm_calls"]}
        self.assertTrue(any(t.endswith("initial") for t in tags) and any(t.endswith("backfill") for t in tags))
        self.assertEqual(len(s.stage_calls("b1")), 1)                                     # B1過剰生成は初回のみ

    def test_n5_select_drop_does_not_trigger_backfill(self):
        def sel(user, me):
            rows = SmartSend().default_sel(user)
            rows["judgements"][0].update(cls="F", keep=False)
            return rows
        env, doc, _ = self.doc(SmartSend(sel=sel), env_kw=dict(call1_seq=[CALL1, [{"phrase": "stay high", "reason_ja": "補", "word_count": 2}]]))
        self.assertFalse(doc["backfill"]["triggered"])
        self.assertEqual(doc["backfill"]["status"], "NOT_TRIGGERED")
        self.assertEqual(env.n["call1_factory"], 1)                                      # 候補数を満たすための補充(P7再call)をしない

    def test_n5_check_drop_counts_as_E(self):
        done = {"x": False}

        def chk(user, me):
            out = SmartSend().default_chk5(user)
            if not done["x"]:
                done["x"] = True
                return {"checks": out["checks"][1:]}                  # 項目1の判定欠落 -> 欠落分のみ再呼出 -> なお欠落 -> n5_check除外
            return {"checks": []}
        s = SmartSend(chk5=chk)
        env, doc, _ = self.doc(s, env_kw=dict(call1_seq=[CALL1, [{"phrase": "stay high", "reason_ja": "補", "word_count": 2}]]))
        by = doc["backfill"]["E"]["by_stage"]
        self.assertGreaterEqual(by.get("n5_check", 0), 1)

    def test_seen_keys_prevent_rejudging_in_backfill(self):
        def ver(user, me):
            out = SmartSend().default_ver5(user)
            out["verdicts"][0].update(verdict="REJECT", meaning_preserved=False, issue="x")
            return out
        # 補完のP7が初回と同じ句(time lag)を再び返しても、SELの再判定をしない(seen)
        s = SmartSend(ver5=ver)
        env, doc, _ = self.doc(s, env_kw=dict(call1_seq=[CALL1, [{"phrase": "time lag", "reason_ja": "再", "word_count": 2}]]))
        self.assertEqual(len(s.stage_calls("sel")), 1)


class TestRetryAndFailure(N5Case):
    def test_outer_retry_runs_N5_again_not_old_method(self):
        state = {"n": 0}
        real = sc.run_key_phrase_canonicalization

        def canon(text, items, work, article_id, process=None, **kw):
            state["n"] += 1
            if state["n"] == 1:
                return {"status": "CANONICALIZATION_INVALID"}
            return real(text, items, work, article_id, process=process, **kw)
        s = SmartSend()
        env, doc, _ = self.doc(s, canon_fn=canon, env_kw=dict(call1_seq=[CALL1, CALL1]))
        self.assertEqual(doc["outer_attempts"], 2)
        atts = doc["generalization"]["attempts"]
        self.assertEqual(len(atts), 2)
        self.assertTrue(atts[0]["l1"] and atts[1]["l1"])
        self.assertTrue(all("n5" in c["item"] for c in doc["candidates"] if c["kind"] == "phrase"))

    def test_n5_technical_failure_exhausts_outer_retry_and_emits_no_candidates(self):
        s = SmartSend(gen5=lambda u, me: RuntimeError("network down"))
        env, r, _ = self.run_gen(s, env_kw=dict(call1_seq=[CALL1, CALL1, CALL1]))
        self.assertFalse(r["ok"])
        self.assertEqual(r["status"], "OUTER_RETRY_EXHAUSTED")
        self.assertTrue(any("N5_TECHNICAL_FAILURE" in (e.get("failure") or "") for e in r["outer_retry_log"]))

    def test_n5_L1_failure_is_outer_retry(self):
        s = SmartSend(sel=lambda u, me: RuntimeError("down"))
        env, r, _ = self.run_gen(s, env_kw=dict(call1_seq=[CALL1, CALL1, CALL1]))
        self.assertFalse(r["ok"])
        self.assertTrue(any(e.get("failure") == "n5_select_failed" for e in r["outer_retry_log"]))

    def test_sel_deferred_rejudge_technical_failure_is_outer_retry_and_emits_no_n5less_candidates(self):
        """委任_04(J2是正のSEL再判定call): 再判定(SEL_DEFERRED)が技術失敗(retry上限)したらN5TechnicalFailure -> 外側retry。N5なし候補は出さない。
        collect_poolが包含dedupeで落としたB1候補を返す条件(defer_out)だけ複製条件として与え、SEL/call_llm/retry/外側retryは正式関数。"""
        real_collect = n5.collect_pool
        sel_n = {"n": 0}

        def collect_with_defer(text, base, b1, **kw):
            pool, rej = real_collect(text, base, b1, **kw)
            if kw.get("defer_out") is not None:
                kw["defer_out"].append({"cand": {"span": "stay high", "sentence": ""}, "blocked_by": "retail prices"})
            return pool, rej

        def sel(user, me):
            sel_n["n"] += 1
            if "stay high" in user and sel_n["n"] >= 2:      # 再判定call(2回目以降のsel)のみ技術失敗
                return RuntimeError("network down in SEL_DEFERRED")
            return SmartSend().default_sel(user)
        s = SmartSend(sel=sel)
        with mock.patch.object(n5, "collect_pool", collect_with_defer):
            env, r, _ = self.run_gen(s, env_kw=dict(call1_seq=[CALL1, CALL1, CALL1]))
        self.assertTrue(any("stay high" in c[2] for c in s.stage_calls("sel")))                 # 再判定callが実際に発行された
        self.assertFalse(r["ok"])
        self.assertEqual(r["status"], "OUTER_RETRY_EXHAUSTED")
        self.assertTrue(all(e.get("failure") == "n5_select_failed" for e in r["outer_retry_log"]))
        self.assertNotIn("doc", r)                                                              # 候補docを返さない(N5なし候補なし)
        self.assertEqual(s.stage_calls("gen5"), [])                                              # L1で止まり、N5なしでL3(GEN5)・後段へ進まない

    def test_contract_error_in_initial_chain_propagates_as_stop(self):
        s = SmartSend(ver5=lambda u, me: n5.N5ContractError("model mismatch"))
        with self.assertRaises(n5.N5ContractError):
            self.run_gen(s)

    def test_contract_error_in_backfill_propagates_not_swallowed(self):
        calls = {"v": 0}

        def ver(user, me):
            calls["v"] += 1
            if calls["v"] == 1:
                out = SmartSend().default_ver5(user)
                out["verdicts"][0].update(verdict="REJECT", meaning_preserved=False, issue="x")
                return out
            return n5.N5ContractError("model mismatch in backfill")
        s = SmartSend(ver5=ver)
        with self.assertRaises(n5.N5ContractError):
            self.run_gen(s, env_kw=dict(call1_seq=[CALL1, [{"phrase": "stay high", "reason_ja": "補", "word_count": 2}]]))

    def test_stop_check_is_called_for_n5_stages(self):
        seen = []
        s = SmartSend()
        self.doc(s, stop_check_fn=lambda where: seen.append(where))
        self.assertTrue(any(w.startswith("kp_n5_sel") for w in seen))
        self.assertTrue(any(w.startswith("kp_n5_chk5") for w in seen))


class TestKillSwitchesDoNotBypassN5(N5Case):
    def test_each_existing_kill_switch_off_still_runs_n5(self):
        for k in ("EIGO_KP_RESCUE", "EIGO_KP_BACKFILL", "EIGO_KP_GLOSS_ALIGNMENT"):
            with self.subTest(switch=k):
                s = SmartSend()
                env_kw = dict(rescue_env="0") if k == "EIGO_KP_RESCUE" else {}
                env, doc, _ = self.doc(s, environ={k: "0"}, env_kw=env_kw)
                self.assertEqual({c[0] for c in s.calls}, {"b1", "sel", "gen5", "ver5", "chk5"})
                self.assertEqual(doc["generalization"]["method"], n5.METHOD_ID)
                self.assertTrue(all("n5" in c["item"] for c in doc["candidates"] if c["kind"] == "phrase"))


class TestPersonAlignmentOnN5Pair(N5Case):
    def test_xy_default_repair_runs_when_n5_gloss_has_concrete_person(self):
        """X/Y(person_repair_fnなし): N5の組(someone形 + 『彼』入りの訳)に既存の人称整合が適用され、修復がn5記録に残る。"""
        s = SmartSend(gen5=gen_tokens({"pushed prices up": ([("CORE", "push"), ("SLOT_PERSON", ""), ("CORE", "up")], "push someone up", "彼を押し上げる")}))
        env, doc, _ = self.doc(s, person_gloss="誰かを押し上げる")
        c = next(c for c in doc["candidates"] if c["selection_phrase"] == "pushed prices up")
        self.assertEqual(c["used_form"], "push someone up")
        self.assertEqual(env.n["gloss_person"], 1)                                      # 既存のgloss整合(alignment)が修復に使われた(不整合のitemだけ)
        self.assertEqual(c["japanese_gloss"], "誰かを押し上げる")
        self.assertNotIn("彼", c["japanese_gloss"])
        self.assertIn("person_repair", c["item"]["n5"])
        self.assertEqual(c["item"]["n5"]["person_repair"]["gloss_before"], "彼を押し上げる")

    def test_z_person_repair_fn_used_and_rewrite_count_recorded(self):
        called = []

        def person_fn(merged):
            called.append(1)
            items = []
            for it in merged["items"]:
                it = dict(it)
                if ga.person_reference_mismatch(it.get("key_phrase"), it.get("japanese_gloss")):
                    it["japanese_gloss"] = "誰かを押し上げる"
                items.append(it)
            return {"items": items}
        s = SmartSend(gen5=gen_tokens({"pushed prices up": ([("CORE", "push"), ("SLOT_PERSON", ""), ("CORE", "up")], "push someone up", "彼を押し上げる")}))
        env, doc, _ = self.doc(s, person_repair_fn=person_fn)
        c = next(c for c in doc["candidates"] if c["selection_phrase"] == "pushed prices up")
        self.assertEqual(c["japanese_gloss"], "誰かを押し上げる")
        self.assertEqual(c["item"]["n5"]["person_repair"]["gloss_before"], "彼を押し上げる")
        self.assertEqual(doc["generalization"]["attempts"][-1]["person_repair"][0]["n5_gloss_rewritten"], 1)
        self.assertTrue(called)                                                           # Zはrunner渡しのfnを使う(X/Y既定の修復fnは作らない)


class TestResumeAndReselect(N5Case):
    def test_resume_is_api0_and_keeps_n5_marker_reselect_runs_n5_again(self):
        s = SmartSend()
        with Env(self.tmp, n5_stub=False, rescue_env="1", call1_seq=[CALL1, CALL1]) as env, mock.patch.dict(os.environ, ENV_CLEAN), mock.patch.object(n5, "_send", s):
            r1 = self.ensure(env)
            self.assertEqual(r1["state"], "PENDING")
            n_calls = len(s.calls)
            n_llm = env.total_llm_calls()
            r2 = self.ensure(env)                                                      # resume: 保存済み候補の読戻しのみ
            self.assertEqual(r2["state"], "PENDING")
            self.assertEqual(len(s.calls), n_calls)                                    # N5のAPI 0
            self.assertEqual(env.total_llm_calls(), n_llm)
            cands = rv.load_candidates(self.kp_dir)
            self.assertEqual(cands["generalization"]["method"], n5.METHOD_ID)
            # Human NG 1件を与えて再選定round(round 2) -> 旧方式へ戻らず同じN5を通る
            ng_cand = next(c for c in cands["candidates"] if c["kind"] == "phrase")
            rv.op_reselect(self.kp_dir, ng={ng_cand["ai_rank"]: "不適切"}, by="human")
            r3 = self.ensure(env)
            self.assertEqual(r3["state"], "PENDING")
            self.assertGreater(len(s.calls), n_calls)
            c2 = rv.load_candidates(self.kp_dir)
            self.assertEqual(c2["round"], 2)
            self.assertEqual(c2["generalization"]["method"], n5.METHOD_ID)
            phr = [c for c in c2["candidates"] if c["kind"] == "phrase"]
            self.assertTrue(phr and all("n5" in c["item"] for c in phr))
            self.assertNotIn(ng_cand["selection_phrase"], [c["selection_phrase"] for c in phr])      # NG句は除外(プール・Gateに効く)

    def test_pre_n5_doc_resume_logs_warning_and_does_not_regenerate(self):
        s = SmartSend()
        with Env(self.tmp, n5_stub=True, rescue_env="1") as env, mock.patch.dict(os.environ, ENV_CLEAN), mock.patch.object(n5, "_send", s):
            self.ensure(env)                                                           # stub(=N5前と同形)で生成 -> generalization記録は付くが、markerを消して旧docを再現
            cands = rv.load_candidates(self.kp_dir)
            cands.pop("generalization", None)
            rv.save_candidates(self.kp_dir, cands)
            review = rv.load_review(self.kp_dir)
            review["candidates_sha256"] = rv.load_candidates(self.kp_dir)["candidates_sha256"]
            rv.save_review(self.kp_dir, review, expected_revision=review["revision"])
            n_llm = env.total_llm_calls()
            with self.assertLogs(rv._log, level="WARNING") as cm:
                self.ensure(env)
            self.assertTrue(any("N5 marker missing" in m for m in cm.output))
            self.assertEqual(env.total_llm_calls(), n_llm)                             # 再生成しない(API 0)
            self.assertEqual(len(s.calls), 0)


class TestStaticReachability(unittest.TestCase):
    def _src(self, name):
        with open(os.path.join(ROOT, name), encoding="utf-8") as f:
            return f.read()

    def test_gate_chain_call_sites_always_pass_n5_ctx(self):
        src = self._src("er119_kp_candidates_01.py")
        calls = re.findall(r"_gate_chain\(((?:[^()]|\([^()]*\))*)\)", src)
        calls = [c for c in calls if "originals, meta, live" in c]
        self.assertEqual(len(calls), 2)                                                # 初回(_generate_candidates_impl)と補完(_run_backfill)
        for c in calls:
            self.assertIn("n5_ctx=", c)
            self.assertIn("n5_l3_fn=", c)

    def test_formal_runners_reach_kp_only_through_run_kp_with_review(self):
        for name in ("er019_family_x_audio_production_runner_01.py", "er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py"):
            src = self._src(name)
            self.assertIn("run_kp_with_review(", src, name)
            self.assertNotIn("run_kp_stage(", src, name)                                  # er062の旧KP stage(旧canon)を呼ばない
            self.assertNotIn("sc.run_key_phrase_canonicalization(", src, name)
            self.assertNotIn("sc.run_key_phrase_selection(", src, name)
        # Xの非Production互換分岐(旧canon): kp_backend!=fulltext_p2 のときだけ到達。既定はfulltext_p2
        x = self._src("er019_family_x_audio_production_runner_01.py")
        self.assertIn('if kp_backend == "fulltext_p2":', x)
        self.assertRegex(x, r'kp_backend[^\n]*=\s*"fulltext_p2"')
        # Z: 旧『_kp_fn_for_ctx』(w62.run_kp_with_outer_retry_fulltext=旧canon)は定義のみで呼出元が無い(到達不能)
        z = self._src("er026_family_z_fiction_production_runner_01.py")
        self.assertEqual(len(re.findall(r"_kp_fn_for_ctx\(", z)), 1)
        self.assertEqual(len(re.findall(r"run_kp_with_outer_retry", z)), 2)                # def内のdocstringと戻り値の2か所のみ
        # Y/Zにはsc.run_key_phrases呼出が無い
        for name in ("er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py"):
            self.assertNotIn("sc.run_key_phrases(", self._src(name), name)

    def test_only_candidates_module_imports_er138_in_production(self):
        offenders = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if "test" in b or b == "er138_kp_n5_generalization_01.py":
                continue
            with open(p, encoding="utf-8", errors="ignore") as f:
                t = f.read()
            if re.search(r"^\s*import er138_kp_n5_generalization_01|from er138_kp_n5_generalization_01", t, re.M):
                offenders.append(b)
        self.assertEqual(offenders, ["er119_kp_candidates_01.py"])

    def test_trial_code_not_referenced_by_production(self):
        offenders = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if "test" in b:
                continue
            with open(p, encoding="utf-8", errors="ignore") as f:
                t = f.read()
            if re.search(r"^\s*(import|from)\s+kpg0[1-4]|KP-GENERALIZATION-CHUNK-VALUE-TRIAL|KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03/kpg", t, re.M):
                if b not in ("er138_kp_n5_generalization_01.py", "er119_kp_candidates_01.py"):       # er138は『出典』のdocstring/コメントとして記載
                    offenders.append(b)
        self.assertEqual(offenders, [])

    def test_injection_args_are_test_only_no_production_caller_passes_them(self):
        for name in ("er019_family_x_audio_production_runner_01.py", "er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py", "er119_kp_wiring_01.py"):
            src = self._src(name)
            for k in ("n5_pool_fn", "n5_l3_fn", "n5_ctx"):
                self.assertNotIn(k, src, f"{name}: {k}")


class TestDownstream(N5Case):
    def _export_module(self):
        p = os.path.join(ROOT, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py")
        spec = importlib.util.spec_from_file_location("export_form_data_01_n5test", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_exporter_shows_n5_form_with_selection_phrase_and_difficulty(self):
        s = SmartSend(gen5=gen_tokens({"pushed prices up": ([("CORE", "push"), ("SLOT_THING", ""), ("CORE", "up")], "push something up", "物を押し上げる")}))
        env, doc, _ = self.doc(s)
        ex = self._export_module()
        c = next(c for c in doc["candidates"] if c["selection_phrase"] == "pushed prices up")
        e = ex.entry(c)
        self.assertEqual(e["term"], "push something up")
        self.assertEqual(e["selection_phrase"], "pushed prices up")                       # 本文根拠を併記
        self.assertEqual(e["meaning_ja"], "物を押し上げる")
        self.assertIn(e["difficulty"]["level"], ("easy", "medium", "hard", "rare", "unknown"))        # 難易度4段階表示はN5形に対して維持

    def test_finalize_writes_n5_pair_and_downstream_fields(self):
        s = SmartSend(gen5=gen_tokens({"pushed prices up": ([("CORE", "push"), ("SLOT_THING", ""), ("CORE", "up")], "push something up", "物を押し上げる")}))
        with Env(self.tmp, n5_stub=False, rescue_env="1") as env, mock.patch.dict(os.environ, ENV_CLEAN), mock.patch.object(n5, "_send", s):
            self.ensure(env)
            rv.add_declaration(run_dirs=[self.run_dir], by="tester", reason="n5 wiring test", rounds=[1])
            r = self.ensure(env)
        self.assertEqual(r["state"], "FINALIZED")
        fin = json.load(open(os.path.join(self.kp_dir, "keywords_canonicalized.json"), encoding="utf-8"))
        it = next(i for i in fin["items"] if i["source_span"] == "pushed prices up")
        self.assertEqual(it["used_form"], "push something up")                              # 音声(tts_safe_kp_en(used_form))・KP一般解説が参照する表示形
        self.assertEqual(it["key_phrase"], it["used_form"])
        self.assertEqual(it["japanese_gloss"], "物を押し上げる")
        self.assertEqual(it["source_span"], "pushed prices up")                              # ハイライト・出典検査が参照する本文根拠
        self.assertIn("n5", it)
        # 人称検査(er128 :1203 が使う決定論check)がsomething/someone形で破綻しない
        self.assertIsNone(ga.person_reference_mismatch(it["key_phrase"], it["japanese_gloss"]))

    def test_kind_of_phrase_keeps_multiword_n5_forms_as_phrase(self):
        for form in ("push something up", "hear someone out", "set a limit", "keep one's eye on", "take a turn", "work something out"):
            self.assertEqual(bf.kind_of_phrase(form), "phrase", form)


class TestSummarySerializable(unittest.TestCase):
    def test_l3_summary_keys_are_sortable_even_when_chk5_target_absent(self):
        """revert済みitem等はcheckを持たない(relation=None)。summaryのdict keyにNoneを入れるとsort_keys=Trueの署名/保存で本番だけ落ちる(X実run所見)。"""
        kept = {1: {"check": None, "reconcile": None, "reverted": True, "flags": ["X"], "display_form": "a b", "span": "a b"},
                2: {"check": {"relation": "SAME"}, "reconcile": "SAME", "flags": [], "display_form": "a c", "span": "a b"}}
        out = kcand._n5_l3_summary({"kept": kept, "dropped": [], "log": {}}, [1, 2])
        json.dumps(out, ensure_ascii=False, sort_keys=True)
        self.assertEqual(out["check_relation"], {"NONE": 1, "SAME": 1})
        self.assertEqual(out["reconcile"], {"NONE": 1, "SAME": 1})


if __name__ == "__main__":
    unittest.main()
