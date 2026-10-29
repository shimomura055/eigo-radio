# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02A(Track B): er134_nuance_explanation_01 の単体test(API 0。LLMは全てmock)。
TEST_PLAN_01.md §2 U-1〜U-16 + Opus修正(M-4/M-8/M-9/R-2/R-8/R-9/R-10/R-15)該当。
実行: .venv\\Scripts\\python.exe -m unittest er134_nuance_explanation_01_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import glob
import hashlib
import importlib.util
import inspect
import json
import os
import re
import shutil
import tempfile
import unittest

import er006_model_routing_contract_01 as routing
import er120_part2_grammar_production_01 as g
import er134_nuance_explanation_01 as n

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = "gpt-6-luna"

P1 = "The team checked the old map. Then the guide said, “It can’t be helped.” They walked on."
P2 = "Maya felt nervous. At least, she was not alone. Nobody laughed at her plan."
P3 = "The guide made a detour near the river. It was a long walk. The weather stayed cold."
PARAS = [P1, P2, P3]


def _cand(cid, rank, used, kind="phrase", display=None):
    return {"candidate_id": cid, "ai_rank": rank, "used_form": used, "selection_phrase": display or used, "kind": kind, "japanese_gloss": f"{used}の訳",
            "auto_eligible": True, "gates": {"gloss": "ALIGNED"},      # 提示集合(仕様①2026-10-29 rv.presentable_candidates)を通る正式候補のfixture: QA PASS・gloss整合済み
            "item": {"display_phrase": display or used, "key_phrase": used, "qa_overall_status": "PASS"}}


def kp_doc():
    cs = [_cand("p_01", 1, "carry over"), _cand("p_02", 2, "take a detour", display="made a detour"), _cand("p_03", 3, "card to play"),
          _cand("p_04", 4, "worth paying attention to"), _cand("w_05", 5, "obstacle", "word"),
          _cand("p_06", 6, "weak link"), _cand("p_07", 7, "can't be helped"), _cand("w_08", 8, "separately", "word"), _cand("w_09", 9, "feature", "word")]
    return {"level": "b1b", "candidates": cs, "shortfall_detail": {"cap": 12, "cap_by_kind": {"phrase": 7, "word": 5}}, "candidates_sha256": "abc"}


GRAMMAR = [{"id": "gc_1", "rank": 1, "title": "比較級で比較対象が省略される文", "example": "The experienced group did better."},
           {"id": "gc_2", "rank": 2, "title": "仮定法過去", "example": "If I were you, I would go."}]


def inputs(level="b1b", grammar=True, doc=None):
    return n.build_inputs(family="X", article_id="t1", title="A Test Article", level=level, paragraphs=PARAS, kp_cands=doc or kp_doc(),
                          grammar_items=GRAMMAR if grammar else None)


def _rd(p, **kw):
    with open(p, encoding="utf-8", **kw) as fh:
        return fh.read()


def lab_of(inp, text):
    for k, m in n.labels_for(inp).items():
        if m["text"] == text:
            return k
    raise KeyError(text)


def gen_json(expression="at least vs just", quote="At least, she was not alone.", rating="high", explanation=None, extra=None, candidate=True):
    ex = explanation or ("ここでの at least は数の下限ではなく、少なくとも一人ではないという慰めを足す話し手の態度を表します。just とは違い、最悪の状況の中の救いに目を向けさせる含みがあります。" * 2)
    c = {"expression": expression, "focus": "at leastが慰めを添える語感", "quote_en": quote, "quote_ja": "少なくとも、彼女は一人ではなかった。", "explanation_ja": ex,
         "differs_from_kp_word_ja": "SECRET_DIFFERS_TEXT", "criteria_check": {"context_specific": "SECRET_CRITERIA", "jp_pitfall": "x", "level_fit": "y"},
         "learning_value_self_rating": rating, "learning_value_reason_ja": "SECRET_REASON"}
    if extra:
        c.update(extra)
    return json.dumps({"rejected_candidates": [], "candidate": c if candidate else None, "no_candidate_reason_ja": None if candidate else "価値のある候補がありません。"}, ensure_ascii=False)


def judge_json(inp, same=(), why="同じ焦点です", omit=(), dup=(), extra_verdict=None, nonbool=None, closest=True):
    items = []
    for lid, m in n.labels_for(inp).items():
        if lid in omit:
            continue
        it = {"id": lid, "same": (m["text"] in same or lid in same)}
        if it["same"]:
            it["why"] = why
        items.append(it)
    for d in dup:
        items.append({"id": d, "same": False})
    if nonbool:
        items[0]["same"] = nonbool
    j = {"items": items}
    if closest:
        j["closest"] = {"id": next(iter(n.labels_for(inp))), "why": "最も近いが別焦点"}
    if extra_verdict:
        j["verdict"] = extra_verdict      # LLMのverdict欄は無視される(決定論)ことの検証用
    return json.dumps(j, ensure_ascii=False)


class Fn:
    """mock call_fn。responsesを順に返す(尽きたら最後を繰り返す)。呼出回数・promptを記録。"""
    def __init__(self, *responses, model=MODEL, exc=None):
        self.responses, self.model, self.exc = list(responses), model, exc
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        if self.exc is not None:
            raise self.exc
        i = min(len(self.prompts) - 1, len(self.responses) - 1)
        return self.responses[i], self.model, {"input_tokens": 1000, "output_tokens": 500, "cached_input_tokens": 0}, f"resp_{len(self.prompts)}"

    @property
    def n(self):
        return len(self.prompts)


def run(inp, gen, judge=None, **kw):
    return n.run_candidate(inp, call_fn=gen, judge_fn=judge or Fn(judge_json(inp)), **kw)


class T01Generation(unittest.TestCase):
    def test_u1_two_candidates_rejected(self):   # U-1
        inp = inputs()
        two = json.dumps({"candidate": [json.loads(gen_json())["candidate"], json.loads(gen_json())["candidate"]]}, ensure_ascii=False)
        gen, jd = Fn(two), Fn("x")
        d = run(inp, gen, jd)
        self.assertEqual(d["status"], n.ST_FAILED_TECHNICAL)
        self.assertEqual(d["failed_technical"]["kind"], n.F_GEN_INVALID)
        self.assertEqual(gen.n, 2)      # 初回+技術retry1回
        self.assertEqual(jd.n, 0)
        self.assertIsNone(d["candidate"])
        three = json.dumps({"candidate": json.loads(gen_json())["candidate"], "candidates": [{}, {}]}, ensure_ascii=False)
        self.assertEqual(run(inp, Fn(three))["status"], n.ST_FAILED_TECHNICAL)

    def test_u2_null_candidate_skips_judge(self):   # U-2
        inp = inputs()
        gen, jd = Fn(gen_json(candidate=False)), Fn("x")
        d = run(inp, gen, jd)
        self.assertEqual(d["status"], n.ST_NO_CANDIDATE)
        self.assertEqual(d["no_candidate_reason"], n.R_MODEL_NONE)
        self.assertEqual((gen.n, jd.n), (1, 0))
        self.assertEqual(d["generation"]["model_reason_ja"], "価値のある候補がありません。")

    def test_r9_mid_rating_is_zero_deterministically(self):   # R-9/R-15
        inp = inputs()
        gen, jd = Fn(gen_json(rating="mid")), Fn("x")
        d = run(inp, gen, jd)
        self.assertEqual((d["status"], d["no_candidate_reason"]), (n.ST_NO_CANDIDATE, n.R_SELF_RATING))
        self.assertEqual(jd.n, 0)
        self.assertEqual(d["rejected_candidate_audit"]["candidate"]["expression"], "at least vs just")
        for r in ("High", " high "):   # 大小/空白は吸収。high以外は全て0件
            self.assertEqual(run(inp, Fn(gen_json(rating=r)), Fn(judge_json(inp)))["status"], n.ST_CANDIDATE)
        self.assertEqual(run(inp, Fn(gen_json(rating="")), Fn("x"))["status"], n.ST_NO_CANDIDATE)

    def test_u9_quote_mismatch_retry_then_failed(self):   # U-9/M-9
        inp = inputs()
        bad = gen_json(quote="This sentence is not in the article.")
        gen = Fn(bad)
        d = run(inp, gen, Fn("x"))
        self.assertEqual((d["status"], d["failed_technical"]["kind"]), (n.ST_FAILED_TECHNICAL, n.F_QUOTE))
        self.assertEqual(gen.n, 2)
        gen2 = Fn(bad, gen_json())     # retryで直れば候補になる
        self.assertEqual(run(inp, gen2, Fn(judge_json(inp)))["status"], n.ST_CANDIDATE)
        # 3文・段落またぎも技術失敗
        self.assertEqual(run(inp, Fn(gen_json(quote="Maya felt nervous. At least, she was not alone. Nobody laughed at her plan.")), Fn("x"))["failed_technical"]["kind"], n.F_QUOTE)
        self.assertEqual(run(inp, Fn(gen_json(quote="They walked on.\n\nMaya felt nervous.")), Fn("x"))["failed_technical"]["kind"], n.F_QUOTE)

    def test_gen_structure_errors(self):
        inp = inputs()
        for bad in ("not json", "{}", json.dumps({"candidate": "str"}), gen_json(explanation="短い"), gen_json(extra={"expression": ""})):
            d = run(inp, Fn(bad), Fn("x"))
            self.assertEqual(d["status"], n.ST_FAILED_TECHNICAL, bad[:30])

    def test_u10_model_mismatch_stops_without_retry_or_fallback(self):   # U-10
        inp = inputs()
        gen = Fn(gen_json(), model="gpt-6.1-sol")
        with self.assertRaises(n.NuanceModelContractError):
            run(inp, gen, Fn("x"))
        self.assertEqual(gen.n, 1)     # retryしない
        jd = Fn(judge_json(inp), model="gpt-6-astra")
        with self.assertRaises(n.NuanceModelContractError):
            run(inp, Fn(gen_json()), jd)
        self.assertEqual(jd.n, 1)

    def test_routing_contract(self):
        self.assertEqual(routing.PROCESS_MODEL_MAP["NUANCE_EXPLANATION"], MODEL)
        self.assertEqual(routing.PROCESS_MODEL_MAP["NUANCE_OVERLAP_JUDGE"], MODEL)
        self.assertEqual(n.MODEL, routing.SUPPORT_MODEL)
        with self.assertRaises(routing.ModelContractViolation):
            routing.require_model("NUANCE_EXPLANATION", "gpt-6.1-sol")
        src = inspect.getsource(n)
        self.assertEqual(len(re.findall(r"routing\.require_model\(", src)), 3)   # generate_candidate / judge_overlap / _call_with_retry

    def test_r15_failed_technical_is_non_blocking_and_stop_errors_propagate(self):
        inp = inputs()
        d = run(inp, Fn("x", exc=RuntimeError("API down")), Fn("x"))      # API障害 -> 例外にせずFAILED_TECHNICAL
        self.assertEqual((d["status"], d["failed_technical"]["kind"]), (n.ST_FAILED_TECHNICAL, n.F_API))
        self.assertNotEqual(d["status"], n.ST_NO_CANDIDATE)               # 本物の0件と区別
        self.assertEqual(d["usage"]["n_calls"], 2)
        with self.assertRaises(routing.ModelContractViolation):
            run(inp, Fn("x", exc=routing.ModelContractViolation("x")), Fn("x"))
        def guard(process, prompt, attempt):
            raise RuntimeError("BUDGET_STOP")
        with self.assertRaises(RuntimeError):
            run(inp, Fn(gen_json()), Fn("x"), budget_guard=guard)


class T02Overlap(unittest.TestCase):
    def test_u3_stage1_exact_duplicate_of_provisional(self):   # U-3
        inp = inputs()
        for expr in ("carry over", "Carry Over", "'carry over'", "carry over vs pass on", "pass on vs carry over", "take a detour", "made a detour"):
            jd = Fn("x")
            d = run(inp, Fn(gen_json(expression=expr)), jd)
            self.assertEqual((d["status"], d["no_candidate_reason"]), (n.ST_NO_CANDIDATE, n.R_OVERLAP_NG), expr)
            self.assertEqual(jd.n, 0, expr)    # 段1 failなら判定callを省く
            self.assertIn("overlap_check", d["rejected_candidate_audit"])
            self.assertEqual(d["rejected_candidate_audit"]["candidate"]["expression"], expr)

    def test_r2_possessive_and_inflection_normalization(self):
        kp = kp_doc()
        kp["candidates"][0] = _cand("p_01", 1, "make one's blood run cold")
        inp = inputs(doc=kp)
        for expr in ("make his blood run cold", "making your blood run cold", "make someone's blood run cold"):
            s1 = n.structural_check(expr, inp["pool"])
            self.assertEqual(s1["verdict"], "fail", expr)

    def test_r2_contains_rule_multiword_kp_inside_expression(self):   # Opus F-2: KP can't be helped ⊂ I guess it can't be helped
        inp = inputs()
        s1 = n.structural_check("I guess it can't be helped", inp["pool"])
        hit = [a for a in s1["auto_ng"] if a["item_id"] == "p_07"]
        self.assertEqual(hit[0]["relation"], "contains")
        self.assertFalse(hit[0]["provisional"])          # p_07は非暫定(pool)
        self.assertEqual(s1["verdict"], "fail" if False else "pass")   # poolへの一致は必須NG(fail)にはしない
        # 暫定選定への丸ごと包含 -> fail
        s2 = n.structural_check("worth paying attention to details vs something else", inp["pool"])
        self.assertEqual(s2["verdict"], "fail")
        # 単語1語のKPが長い表現の中にあるだけ -> 自動NGにしない(複数語のみ)
        s3 = n.structural_check("obstacle course", inp["pool"])
        self.assertEqual(s3["auto_ng"], [])
        self.assertEqual(s3["verdict"], "pass")
        self.assertEqual([x["shared"] for x in s3["shared"] if x["item_id"] == "w_05"], [["obstacle"]])

    def test_r2_word_sharing_only_goes_to_stage2_with_hint(self):   # was linked to vs weak link
        inp = inputs()
        s1 = n.structural_check("was linked to", inp["pool"])
        self.assertEqual((s1["verdict"], s1["auto_ng"]), ("pass", []))
        self.assertEqual([(x["item_id"], x["shared"]) for x in s1["shared"]], [("p_06", ["linked"])])
        # 段2 pass -> 自動NGでない段1ヒットに優先して pass。shared_termsは記録(HR表示用)
        d = run(inp, Fn(gen_json(expression="was linked to")), Fn(judge_json(inp)))
        self.assertEqual(d["status"], n.ST_CANDIDATE)
        st = d["candidate"]["shared_terms"]
        self.assertEqual([(x["item_id"], x["shared"], x["stage2_pass"]) for x in st], [("p_06", ["linked"], True)])
        # ヒントはjudge promptへ渡る
        jd = Fn(judge_json(inp))
        run(inp, Fn(gen_json(expression="was linked to")), jd)
        self.assertIn("構造ヒント: 語『linked』を共有", jd.prompts[0])
        # 段2 fail優先: 語共有 + 段2 same(暫定でない pool item) -> pool_conflicts。暫定なら fail
        d2 = run(inp, Fn(gen_json(expression="was linked to")), Fn(judge_json(inp, same=("weak link",))))
        self.assertEqual((d2["status"], d2["candidate"]["pool_conflicts"]), (n.ST_CANDIDATE, ["p_06"]))
        kp = kp_doc()
        kp["candidates"][5]["ai_rank"] = 2.5    # weak linkを暫定選定へ
        inp3 = inputs(doc=kp)
        self.assertIn("p_06", inp3["provisional_ids"])
        d3 = run(inp3, Fn(gen_json(expression="was linked to")), Fn(judge_json(inp3, same=("weak link",))))
        self.assertEqual((d3["status"], d3["no_candidate_reason"]), (n.ST_NO_CANDIDATE, n.R_OVERLAP_NG))

    def test_decide_auto_ng_is_absolute_even_if_stage2_says_false(self):
        inp = inputs()
        s1 = n.structural_check("carry over", inp["pool"])
        judge = {"ok": True, "per": {e["id"]: {"same_focus": False, "why": "", "label": "", "kind": e["kind"], "provisional": e["provisional"]} for e in inp["pool"]}, "calls": [], "model": MODEL}
        for gi in inp["grammar"]:
            judge["per"][gi["id"]] = {"same_focus": False, "why": ""}
        oc = n.decide(inp, {"expression": "carry over"}, s1, judge)
        self.assertEqual(oc["verdict"], "fail")
        self.assertEqual(oc["required_conflicts"], ["p_01"])

    def test_u4_stage2_same_focus_fails_even_if_strings_differ(self):   # U-4
        inp = inputs()
        d = run(inp, Fn(gen_json(expression="pass on")), Fn(judge_json(inp, same=("carry over",))))
        self.assertEqual((d["status"], d["no_candidate_reason"]), (n.ST_NO_CANDIDATE, n.R_OVERLAP_NG))
        oc = d["rejected_candidate_audit"]["overlap_check"]
        self.assertEqual(oc["required_conflicts"], ["p_01"])
        self.assertTrue(any(a["item_id"] == "p_01" and a["same_focus"] and a["source"] == "stage2" for a in oc["against"]))

    def test_u5_mention_only_is_pass(self):   # U-5
        inp = inputs()
        d = run(inp, Fn(gen_json()), Fn(judge_json(inp)))
        self.assertEqual(d["status"], n.ST_CANDIDATE)
        self.assertEqual(d["candidate"]["overlap_check"]["verdict"], "pass")
        self.assertEqual(d["candidate"]["pool_conflicts"], [])

    def test_u6_pool_conflict_recorded(self):   # U-6
        inp = inputs()
        d = run(inp, Fn(gen_json()), Fn(judge_json(inp, same=("separately", "weak link"))))
        c = d["candidate"]
        self.assertEqual(d["status"], n.ST_CANDIDATE)
        self.assertEqual(sorted(c["pool_conflicts"]), ["p_06", "w_08"])
        self.assertEqual(c["overlap_check"]["verdict"], "pass")

    def test_u7_grammar_conflict_is_warning_not_hard_ng(self):   # U-7(F-1/R-1: 文法はハードNGにしない)
        inp = inputs()
        d = run(inp, Fn(gen_json()), Fn(judge_json(inp, same=("G1", "G2"))))
        c = d["candidate"]
        self.assertEqual(d["status"], n.ST_CANDIDATE)
        self.assertEqual(c["grammar_conflicts"], ["gc_1", "gc_2"])
        self.assertEqual(c["overlap_check"]["verdict"], "pass")
        self.assertEqual(c["pool_conflicts"], [])

    def test_u8_judge_invalid_twice_is_overlap_unverified(self):   # U-8
        inp = inputs()
        jd = Fn("not json at all")
        d = run(inp, Fn(gen_json()), jd)
        self.assertEqual((d["status"], d["failed_technical"]["kind"]), (n.ST_FAILED_TECHNICAL, n.F_OVERLAP_UNVERIFIED))
        self.assertIsNone(d["candidate"])
        self.assertEqual(jd.n, 2)
        self.assertEqual(d["rejected_candidate_audit"]["overlap_check"]["verdict"], "unverified")

    def test_m4_per_item_must_cover_all_ids(self):   # M-4
        inp = inputs()
        all_labels = list(n.labels_for(inp))
        self.assertEqual(len(all_labels), 9 + 2)       # 提示pool全件(9) + 文法Top2
        # 欠落 -> retry -> それでも欠落 -> overlap_unverified
        jd = Fn(judge_json(inp, omit=("K3",)))
        d = run(inp, Fn(gen_json()), jd)
        self.assertEqual((d["status"], d["failed_technical"]["kind"]), (n.ST_FAILED_TECHNICAL, n.F_OVERLAP_UNVERIFIED))
        self.assertEqual(jd.n, 2)
        # 文法の欠落も不可
        self.assertEqual(run(inp, Fn(gen_json()), Fn(judge_json(inp, omit=("G2",))))["status"], n.ST_FAILED_TECHNICAL)
        # 重複id
        self.assertEqual(run(inp, Fn(gen_json()), Fn(judge_json(inp, dup=("K1",))))["status"], n.ST_FAILED_TECHNICAL)
        # sameがboolでない
        self.assertEqual(run(inp, Fn(gen_json()), Fn(judge_json(inp, nonbool="yes")))["status"], n.ST_FAILED_TECHNICAL)
        # 1回目が欠落でも2回目(retry)で全件揃えば成立
        jd2 = Fn(judge_json(inp, omit=("K3",)), judge_json(inp))
        d2 = run(inp, Fn(gen_json()), jd2)
        self.assertEqual((d2["status"], jd2.n), (n.ST_CANDIDATE, 2))
        # 余分なid
        extra = json.loads(judge_json(inp))
        extra["items"].append({"id": "K99", "same": False})
        self.assertEqual(run(inp, Fn(gen_json()), Fn(json.dumps(extra)))["status"], n.ST_FAILED_TECHNICAL)

    def test_m4_verdict_is_deterministic_not_from_llm_field(self):   # M-4
        inp = inputs()
        d = run(inp, Fn(gen_json(expression="pass on")), Fn(judge_json(inp, same=("carry over",), extra_verdict="pass")))   # LLMが"pass"と書いても無視
        self.assertEqual(d["no_candidate_reason"], n.R_OVERLAP_NG)
        d = run(inp, Fn(gen_json()), Fn(judge_json(inp, extra_verdict="fail")))                                             # LLMが"fail"と書いても無視
        self.assertEqual(d["status"], n.ST_CANDIDATE)

    def test_m4_against_covers_full_presented_pool_plus_grammar(self):
        inp = inputs()
        d = run(inp, Fn(gen_json()), Fn(judge_json(inp)))
        ids = [a["item_id"] for a in d["candidate"]["overlap_check"]["against"]]
        self.assertEqual(ids, [e["id"] for e in inp["pool"]] + [x["id"] for x in inp["grammar"]])
        self.assertEqual(d["kp_word_basis"]["pool_ids"], [{"id": e["id"], "kind": e["kind"]} for e in inp["pool"]] + [{"id": x["id"], "kind": "grammar"} for x in inp["grammar"]])

    def test_m4_pool_matches_exporter_function(self):   # exporterと同じ算出(DEFAULT_CAP=12, 7+5)
        p = os.path.join(HERE, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py")
        spec = importlib.util.spec_from_file_location("export_form_data_01_parity", p)
        ex = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ex)
        self.assertEqual(ex.DEFAULT_CAP, n.DEFAULT_CAP)
        self.assertEqual(ex.DEFAULT_CAP_BY_KIND, n.DEFAULT_CAP_BY_KIND)
        docs = [kp_doc()]
        big = {"candidates": [_cand(f"p_{i:02d}", i, f"phrase number {i}") for i in range(1, 11)] + [_cand(f"w_{i:02d}", 10 + i, f"word{i}", "word") for i in range(1, 9)]}
        docs.append(big)
        capdoc = dict(kp_doc(), shortfall_detail={"cap": 8, "cap_by_kind": {"phrase": 4, "word": 4}})
        docs.append(capdoc)
        nokind = {"candidates": [dict(_cand("a", 1, "one"), kind=None), dict(_cand("b", 2, "two words"), kind=None)]}
        docs.append(nokind)
        for doc in docs:
            doc = {k: v for k, v in doc.items() if k != "candidates_sha256"}    # exporterは自己shaを検証する。合成docはshaを持たせない
            out = ex.convert(doc, slug="s", level="b1b", name="n", family="X", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
            exp = sorted([e["id"] for e in out["phrases"]] + [e["id"] for e in out["words"]])
            self.assertEqual(sorted(c["candidate_id"] for c in n.presented_pool(doc)), exp)
        # 実run(存在すれば)でも一致
        real = os.path.join(HERE, "er019_output", "family_x_audio_production_wiring_01", "ai_island_temple__run_form_prod_01", "a2", "key_phrases", "kp_candidates.json")
        if os.path.exists(real):
            doc = json.load(open(real, encoding="utf-8"))
            out = ex.convert(doc, slug="s", level="a2", name="n", family="X", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
            self.assertEqual(sorted(c["candidate_id"] for c in n.presented_pool(doc)), sorted([e["id"] for e in out["phrases"]] + [e["id"] for e in out["words"]]))

    def test_r8_judge_prompt_independence_and_instructions(self):   # R-8
        inp = inputs()
        gen, jd = Fn(gen_json()), Fn(judge_json(inp))
        run(inp, gen, jd)
        jp = jd.prompts[0]
        for secret in ("SECRET_DIFFERS_TEXT", "SECRET_CRITERIA", "SECRET_REASON", "learning_value_self_rating", "differs_from_kp_word_ja", "criteria_check"):
            self.assertNotIn(secret, jp)
        self.assertIn("入れ替えテスト", jp)
        self.assertIn("最も焦点が近い項目", jp)
        self.assertNotEqual(n.PROMPT_JUDGE, n.PROMPT_GEN)
        self.assertNotEqual(gen.prompts[0], jp)
        # 圧縮形: 出力例にid->bool、trueだけwhy
        self.assertIn('"same": true, "why"', jp)
        self.assertIn("全件", jp)

    def test_closest_item_recorded(self):
        inp = inputs()
        d = run(inp, Fn(gen_json()), Fn(judge_json(inp)))
        cl = d["candidate"]["overlap_check"]["stage2_llm"]["closest"]
        self.assertEqual(cl["item_id"], inp["pool"][0]["id"])

    def test_no_pool_no_grammar_skips_judge(self):
        inp = n.build_inputs(family="X", article_id="t", title="T", level="a2", paragraphs=PARAS, kp_cands={"candidates": []}, grammar_items=None)
        jd = Fn("x")
        d = run(inp, Fn(gen_json()), jd)
        self.assertEqual((d["status"], jd.n), (n.ST_CANDIDATE, 0))
        self.assertEqual(d["candidate"]["overlap_check"]["stage2_llm"]["verdict"], "skipped")


class T03InputsPromptsQuote(unittest.TestCase):
    def test_build_inputs_shape(self):
        inp = inputs()
        self.assertEqual(len(inp["pool"]), 9)
        self.assertEqual(inp["provisional_ids"], ["p_01", "p_02", "p_03", "p_04", "w_05"])   # rv.auto_select(vocab最大5件)
        self.assertEqual([x["id"] for x in inp["grammar"]], ["gc_1", "gc_2"])
        self.assertEqual(inp["text_sha256"], g.text_sha256(PARAS))
        self.assertEqual(inp["level_name"], "Advanced")
        self.assertEqual(inputs("a2")["level_name"], "Standard")
        one_g = n.build_inputs(family="X", article_id="t", title="T", level="b1b", paragraphs=PARAS, kp_cands=kp_doc(), grammar_items=GRAMMAR + [{"id": "gc_3", "rank": 3, "title": "x", "example": "y"}])
        self.assertEqual([x["id"] for x in one_g["grammar"]], ["gc_1", "gc_2"])   # Top2のみ
        with self.assertRaises(n.NuanceInputError):
            n.build_inputs(family="X", article_id="t", title="T", level=None, paragraphs=PARAS, kp_cands=kp_doc())
        with self.assertRaises(n.NuanceInputError):
            n.build_inputs(family="X", article_id="t", title="T", level="b1b", paragraphs=PARAS, kp_cands=kp_doc(), provisional_ids=["nope"])

    def test_m8_prompt_has_provisional_pool_and_grammar_but_not_focus_terms(self):   # M-8
        inp = inputs()
        pr = n.build_gen_prompt(inp)
        self.assertIn("暫定選定(5件", pr)
        self.assertIn("その他の提示候補(4件", pr)
        self.assertIn("文法・文構造コーナーの候補(上位2件", pr)
        self.assertIn("比較級で比較対象が省略される文", pr)
        self.assertIn("K6. weak link", pr)
        self.assertIn("(本文中の形: made a detour)", pr)
        for ex in ("focus_terms", "Part 4", "Think & Express", "Deeper Understanding", "思考・表現"):
            self.assertNotIn(ex, pr)
        self.assertEqual(n.SECTION_HEADING_JA, "ニュアンス解説")
        self.assertEqual(n.derive_focus_terms("quite vs rather"), ["quite", "rather"])
        # 入力にpool/grammarが無ければ節ごと出ない
        inp0 = n.build_inputs(family="X", article_id="t", title="T", level="a2", paragraphs=PARAS, kp_cands={"candidates": [_cand("p_1", 1, "x y")]}, grammar_items=None)
        pr0 = n.build_gen_prompt(inp0)
        self.assertNotIn("## その他の提示候補(", pr0)
        self.assertNotIn("文法・文構造コーナーの候補", pr0)

    def test_derive_focus_terms(self):
        d = n.derive_focus_terms
        self.assertEqual(d("at least"), ["at least"])
        self.assertEqual(d("'at least' vs 'just'"), ["at least", "just"])
        self.assertEqual(d("A vs. B"), ["A", "B"])
        self.assertEqual(d("pass on / carry over"), ["pass on", "carry over"])
        self.assertEqual(d("You should have seen ..."), ["You should have seen"])
        self.assertEqual(d("quite vs rather vs quite"), ["quite", "rather"])
        self.assertEqual(d("   "), [])
        self.assertEqual(d("more or less"), ["more or less"])      # 'or'では分割しない(句の破壊を避ける)
        # generate_candidateが保存するfocus_termsはexpressionから決定論で導出されたもの(LLM出力ではない)
        inp = inputs()
        d2 = run(inp, Fn(gen_json(extra={"focus_terms": ["INJECTED"]})), Fn(judge_json(inp)))
        self.assertEqual(d2["candidate"]["focus_terms"], ["at least", "just"])

    def test_r9_level_fit_wording(self):   # R-9
        pr = n.PROMPT_GEN
        self.assertNotIn("A2までに学ぶ基礎文法の対比", pr)
        self.assertNotIn("must と have to", pr)
        self.assertIn("文法・文構造のコーナーの領域", pr)
        self.assertIn("機能語(副詞・前置詞・助動詞など)や頻出表現が持つ語用的な含み(誇張・婉曲・確信度・範囲の限定など)は、StandardでもAdvancedでも対象にしてよい", pr)
        self.assertIn("助動詞や構文を含む表現でも、焦点が文の仕組みではなく語用的な含みなら対象にしてよい", pr)
        self.assertIn("midの場合は候補にせず0件", pr)

    def test_u12_prompt_forbidden_content_and_sha(self):   # U-12
        for pr in (n.PROMPT_GEN, n.PROMPT_JUDGE):
            for ex in ("Part 4", "Think & Express", "Deeper Understanding", "複数テーマ"):
                self.assertNotIn(ex, pr)
        self.assertEqual(n.PROMPT_GEN_SHA256, hashlib.sha256(n.PROMPT_GEN.encode("utf-8")).hexdigest())
        self.assertEqual(n.PROMPT_JUDGE_SHA256, hashlib.sha256(n.PROMPT_JUDGE.encode("utf-8")).hexdigest())
        d = run(inputs(), Fn(gen_json()), Fn(judge_json(inputs())))
        self.assertEqual((d["prompt_sha"], d["judge_prompt_sha"]), (n.PROMPT_GEN_SHA256, n.PROMPT_JUDGE_SHA256))
        self.assertIn("連続する1〜2文", n.PROMPT_GEN)

    def test_m9_quote_rules(self):   # M-9
        body = "\n\n".join(PARAS)
        q = n.quote_check
        self.assertTrue(q("At least, she was not alone.", body)["ok"])
        two = q("Maya felt nervous. At least, she was not alone.", body)
        self.assertEqual((two["ok"], two["n_sentences"]), (True, 2))
        three = q("Maya felt nervous. At least, she was not alone. Nobody laughed at her plan.", body)
        self.assertEqual((three["ok"], three["reason"]), (False, "sentences_3"))
        self.assertEqual(q("They walked on.\n\nMaya felt nervous.", body)["reason"], "spans_paragraphs")
        self.assertEqual(q("Maya felt nervous.  At  least,\nshe was not alone.", body)["ok"], True)   # 空白差は吸収
        self.assertEqual(q("Maya was not nervous.", body)["reason"], "not_in_body")
        self.assertEqual(q("", body)["reason"], "empty")
        # 引用符正規化: 本文が曲がった引用符、quoteが直線 -> 本文側の逐語文字列を返す
        s = q('Then the guide said, "It can\'t be helped."', body)
        self.assertTrue(s["ok"])
        self.assertEqual(s["verbatim"], "Then the guide said, “It can’t be helped.”")
        # 部分文字列(断片)も逐語であれば可
        self.assertTrue(q("not alone", body)["ok"])

    def test_m9_quote_is_replaced_with_body_verbatim_in_doc(self):
        inp = inputs()
        d = run(inp, Fn(gen_json(quote='Then the guide said, "It can\'t be helped." They walked on.')), Fn(judge_json(inp)))
        self.assertEqual(d["status"], n.ST_CANDIDATE)
        self.assertEqual(d["candidate"]["quote_en"], "Then the guide said, “It can’t be helped.” They walked on.")

    def test_m9_same_normalization_as_grammar(self):   # 文法(er120)とparity
        for s in ("It’s “fine”, isn’t it?", "‘quoted’ text", "plain 'x' \"y\""):
            self.assertEqual(n._qn(s), g._qn(s))
        for t in ("One. Two! Three?", "He said, “Go.” Then left.", "No end here"):
            self.assertEqual(n._sents(t), g._sents(t))
        self.assertEqual(n.LEVELS, g.LEVELS)

    def test_u11_candidate_sha(self):   # U-11
        base = {"expression": "at least", "focus": "f", "explanation_ja": "解説 です", "quote_en": "He said “hi”.", "quote_ja": "彼は言った", "focus_terms": ["at least"]}
        s0 = n.candidate_sha256(base)
        self.assertEqual(s0, n.candidate_sha256(dict(base, explanation_ja="解説  です", quote_en="He said \"hi\".")))   # 空白/引用符差は同一
        self.assertEqual(s0, n.candidate_sha256(dict(base, differs_from_kp_word_ja="x", overlap_check={"a": 1})))      # 照合キー外の項目は無関係
        for k in ("expression", "focus", "explanation_ja", "quote_en", "quote_ja"):
            self.assertNotEqual(s0, n.candidate_sha256(dict(base, **{k: base[k] + "x"})), k)
        self.assertNotEqual(s0, n.candidate_sha256(dict(base, focus_terms=["at least", "just"])))
        d = run(inputs(), Fn(gen_json()), Fn(judge_json(inputs())))
        self.assertEqual(d["candidate"]["candidate_sha256"], n.candidate_sha256(d["candidate"]))

    def test_r10_usage_aggregation_covers_both_processes(self):   # R-10
        inp = inputs()
        d = run(inp, Fn(gen_json()), Fn(judge_json(inp)))
        procs = [c["process"] for c in d["usage"]["calls"]]
        self.assertEqual(procs, [n.PROCESS_GEN, n.PROCESS_JUDGE])
        self.assertEqual(d["usage"]["n_calls"], 2)
        self.assertEqual(d["usage"]["input_tokens"], 2000)
        self.assertIsNotNone(d["usage"]["cost_jpy"])
        self.assertGreater(d["usage"]["cost_jpy"], 0)
        self.assertEqual(d["model"], MODEL)
        self.assertEqual(d["candidate"]["overlap_check"]["stage2_llm"]["model"], MODEL)
        self.assertNotIn("differs_from_kp_word_ja", d["candidate"])      # 生成側の自己申告は候補本体に出ない(generation_metaに隔離)
        self.assertIn("generation_meta", d["candidate"])

    def test_schema_fields(self):   # WIRING_DESIGN §3 + §3.3 + Opus修正
        inp = inputs()
        d = run(inp, Fn(gen_json()), Fn(judge_json(inp, same=("separately",), ))).copy()
        for k in ("schema", "family", "article_id", "level", "level_key", "generated_at", "candidate", "no_candidate_reason", "kp_word_basis", "model", "prompt_sha", "usage", "status", "text_sha256"):
            self.assertIn(k, d)
        self.assertEqual((d["schema"], d["level"], d["level_key"], d["status"]), ("nuance_candidate_v1", "Advanced", "b1b", n.ST_CANDIDATE))
        b = d["kp_word_basis"]
        for k in ("status", "items", "candidates_sha256", "provisional_ids", "pool_ids", "pool_identity_sha", "grammar_identity_sha"):
            self.assertIn(k, b)
        self.assertEqual(b["status"], "provisional")
        c = d["candidate"]
        for k in ("expression", "focus", "explanation_ja", "quote_en", "quote_ja", "overlap_check", "focus_terms", "pool_conflicts", "grammar_conflicts", "shared_terms", "candidate_sha256"):
            self.assertIn(k, c)
        oc = c["overlap_check"]
        for k in ("verdict", "stage1_structural", "stage2_llm", "reason", "against"):
            self.assertIn(k, oc)
        self.assertIn(oc["verdict"], ("pass", "fail", "unverified"))
        json.dumps(d, ensure_ascii=False)   # JSON直列化可能
        # pool_identity_shaはgloss等の変更で動かず、used_form/idの変更で動く(M-3)
        k2 = kp_doc()
        k2["candidates"][0]["japanese_gloss"] = "別の訳"
        k2["candidates_sha256"] = "zzz"
        self.assertEqual(inputs(doc=k2)["pool_identity_sha"], inp["pool_identity_sha"])
        k3 = kp_doc()
        k3["candidates"][0]["used_form"] = "carry on"
        self.assertNotEqual(inputs(doc=k3)["pool_identity_sha"], inp["pool_identity_sha"])


class T04StageSpecResume(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="er134_")
        self.sd = os.path.join(self.d, "b1b", "study_text")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_u16_spec_issued_only_for_new_review_and_idempotent(self):   # U-16/M-2
        r = n.ensure_spec(self.sd, level="b1b", new_review=False)       # KP確定済み/既存runの再開など = 発行しない
        self.assertEqual((r["state"], r["issued_now"]), (n.ST_LEGACY, False))
        self.assertFalse(os.path.exists(os.path.join(self.sd, n.SPEC_FILENAME)))
        r = n.ensure_spec(self.sd, level="b1b", new_review=True)
        self.assertEqual((r["state"], r["issued_now"]), ("SPEC_ISSUED", True))
        before = open(os.path.join(self.sd, n.SPEC_FILENAME), "rb").read()
        r = n.ensure_spec(self.sd, level="b1b", new_review=True)        # 冪等(不変)
        self.assertFalse(r["issued_now"])
        self.assertEqual(open(os.path.join(self.sd, n.SPEC_FILENAME), "rb").read(), before)
        r = n.ensure_spec(self.sd, level="b1b", new_review=False)       # 発行済みは常に有効
        self.assertEqual(r["state"], "SPEC_ISSUED")
        with self.assertRaises(n.NuanceInputError):
            n.ensure_spec(self.sd, level="a2", new_review=False)        # level不一致
        with self.assertRaises(n.NuanceInputError):
            n.ensure_spec(self.sd, level=None, new_review=True)

    def test_u15_legacy_makes_no_calls_and_no_files(self):   # U-15
        inp = inputs()
        gen = Fn(gen_json())
        r = n.candidate_stage(self.sd, inp, call_fn=gen, judge_fn=Fn("x"))
        self.assertEqual((r["state"], r["api_calls"], gen.n), (n.ST_LEGACY, 0, 0))
        self.assertFalse(os.path.exists(self.sd))

    def test_u14_auto_adopted_makes_no_calls(self):   # U-14
        n.ensure_spec(self.sd, level="b1b", new_review=True)
        inp = inputs()
        gen = Fn(gen_json())
        r = n.candidate_stage(self.sd, inp, call_fn=gen, judge_fn=Fn("x"), auto_adopted=True)
        self.assertEqual((gen.n, r["api_calls"]), (0, 0))
        self.assertEqual((r["doc"]["status"], r["doc"]["no_candidate_reason"]), (n.ST_NO_CANDIDATE, n.R_AUTO_ADOPTED))
        self.assertIsNone(r["doc"]["candidate"])

    def test_resume_reuse_and_stale_archive(self):
        n.ensure_spec(self.sd, level="b1b", new_review=True)
        inp = inputs()
        gen, jd = Fn(gen_json()), Fn(judge_json(inp))
        r1 = n.candidate_stage(self.sd, inp, call_fn=gen, judge_fn=jd)
        self.assertEqual((r1["reused"], r1["api_calls"], r1["doc"]["status"]), (False, 2, n.ST_CANDIDATE))
        gen2, jd2 = Fn(gen_json()), Fn("x")
        r2 = n.candidate_stage(self.sd, inp, call_fn=gen2, judge_fn=jd2)      # 同入力のresume = API 0
        self.assertEqual((r2["reused"], r2["api_calls"], gen2.n, jd2.n), (True, 0, 0, 0))
        self.assertEqual(r2["doc"]["candidate"]["candidate_sha256"], r1["doc"]["candidate"]["candidate_sha256"])
        # confirm-revise相当(candidates_sha256のみ変化・pool同一) -> 再利用(M-3: shaに頼らない)
        k = kp_doc()
        k["candidates_sha256"] = "changed"
        r3 = n.candidate_stage(self.sd, inputs(doc=k), call_fn=Fn(gen_json()), judge_fn=Fn("x"))
        self.assertTrue(r3["reused"])
        # 本文変更 -> stale: 旧docを退避(削除しない)して再生成
        inp_b = n.build_inputs(family="X", article_id="t1", title="A Test Article", level="b1b", paragraphs=PARAS[:2] + [P3 + " Extra."], kp_cands=kp_doc(), grammar_items=GRAMMAR)
        r4 = n.candidate_stage(self.sd, inp_b, call_fn=Fn(gen_json()), judge_fn=Fn(judge_json(inp_b)))
        self.assertFalse(r4["reused"])
        stale = glob.glob(os.path.join(self.sd, "nuance_candidate.STALE_*.json"))
        self.assertEqual(len(stale), 1)
        self.assertEqual(json.load(open(stale[0], encoding="utf-8"))["text_sha256"], inp["text_sha256"])
        # pool変更 -> stale
        k2 = kp_doc()
        k2["candidates"][5]["used_form"] = "weak point"
        inp_c = inputs(doc=k2)
        r5 = n.candidate_stage(self.sd, inp_c, call_fn=Fn(gen_json()), judge_fn=Fn(judge_json(inp_c)))
        self.assertFalse(r5["reused"])
        self.assertEqual(len(glob.glob(os.path.join(self.sd, "nuance_candidate.STALE_*.json"))), 2)

    def test_failed_technical_resume_retries_once_then_sticks(self):   # R-5
        n.ensure_spec(self.sd, level="b1b", new_review=True)
        inp = inputs()
        r1 = n.candidate_stage(self.sd, inp, call_fn=Fn("garbage"), judge_fn=Fn("x"))
        self.assertEqual(r1["doc"]["status"], n.ST_FAILED_TECHNICAL)
        self.assertTrue(os.path.exists(os.path.join(self.sd, n.FAILED_FILENAME)))
        r2 = n.candidate_stage(self.sd, inp, call_fn=Fn("garbage"), judge_fn=Fn("x"))   # resume: 自動再試行1回
        self.assertEqual((r2["reused"], r2["api_calls"], r2["doc"]["resume_attempts"]), (False, 2, 1))
        g3 = Fn(gen_json())
        r3 = n.candidate_stage(self.sd, inp, call_fn=g3, judge_fn=Fn("x"))               # それ以降は自動再試行しない
        self.assertEqual((r3["reused"], g3.n), (True, 0))
        self.assertEqual(r3["doc"]["status"], n.ST_FAILED_TECHNICAL)

    def test_no_human_review_substitute_functions(self):   # A-7: 再生成・次点繰上げ・自動補充の関数/引数が無い
        names = [x for x in dir(n) if not x.startswith("_")]
        for bad in ("regenerate", "backfill", "autofill", "next_candidate", "fallback"):
            self.assertFalse([x for x in names if bad in x.lower()], bad)
        self.assertEqual(inspect.signature(n.generate_candidate).parameters.get("max_candidates"), None)


class T05Isolation(unittest.TestCase):
    def test_u13_module_isolation(self):   # U-13
        src = _rd(os.path.join(HERE, "er134_nuance_explanation_01.py"))
        imports = re.findall(r"^\s*(?:import|from)\s+(\S+)", src, re.M)
        allowed_er = {"er006_model_routing_contract_01", "er119_kp_human_review_01", "er120_part2_grammar_production_01", "er009_n1_routing_governance_10_actual_model_cost",
                      "er003_v1_b1_scaffold_01_generate"}
        self.assertEqual({i for i in imports if re.match(r"er\d+_", i)} - allowed_er, set())
        self.assertNotIn("docs.research", src.replace("docs/research配下", ""))   # DEV/Trial資産をimportしない(コメント中の語は除く)
        self.assertNotIn("run_trial_", src)
        self.assertNotIn("os.environ", src)
        self.assertNotIn("getenv", src)
        # Family A/B/C の既存moduleはer134をimportしない
        offenders = []
        for p in glob.glob(os.path.join(HERE, "*.py")):
            b = os.path.basename(p)
            if b.startswith("er134_") or "test" in b:
                continue
            if re.search(r"^\s*(import|from)\s+er134_", _rd(p, errors="ignore"), re.M):
                offenders.append(b)
        # 配線(Track A/02B)でimportしてよいのはX/Y/Zのrunner・HR/確定/文法配線module(er019 family_x / er026 family_z / er121 family_y / er119 / er120 / er128)のみ。
        # Family A/B/C(旧経路)や他moduleはimportしない。
        self.assertEqual([b for b in offenders if not re.match(r"^(er019_family_x|er026_family_z|er121_family_y|er119_|er120_|er128_)", b)], [])
        # er119 isolation testの許可リストに載っている
        iso = _rd(os.path.join(HERE, "er119_isolation_test_01.py"))
        self.assertIn("er134_nuance_explanation_01.py", iso)

    def test_default_off_isolation_no_api_without_explicit_call(self):
        """import時・build_inputs時にAPI/clientを触らない(call_fn未注入でclient取得するのは generate_candidate/judge_overlap 実行時のみ)。"""
        src = inspect.getsource(n.build_inputs) + inspect.getsource(n.structural_check) + inspect.getsource(n.decide) + inspect.getsource(n.quote_check)
        self.assertNotIn("client", src)
        self.assertNotIn("call_fn", src)

    def test_production_results_untouched_by_tests(self):
        # 本testは一時dirのみ使用。実output dirへ書かない
        src = _rd(os.path.join(HERE, "er134_nuance_explanation_01_test_01.py"))
        self.assertEqual(len(re.findall(r"er0\d\d_output|er1\d\d_output", src.replace("er019_output", "").replace("er134_output", "x"))), 0)


if __name__ == "__main__":
    unittest.main()
