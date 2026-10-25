# -*- coding: utf-8 -*-
"""er119 KP Human Review testの共通fixture(API 0)。LLM由来の関数(選定1/選定2-V/canonicalization/gloss再整合/Redundancy QA)を
すべてmockし、呼出回数をcounterで数える(実API呼出が0であることの証明に使う)。"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import os
import re
import tempfile
import unittest
from unittest import mock

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga
import er003_v1_n3_01_scaffold_generate as sc
import er011_key_phrase_set_redundancy_qa_01 as rq
import er105_kp_fulltext_selector_01 as ft
import er119_kp_human_review_01 as rv
import er119_kp_prompt_2v_01 as p2v

ARTICLE = (
    "# Coffee prices\n\n"
    "Market insiders say a time lag is built in. Retail prices follow raw beans slowly.\n"
    "Cafes keep raw beans in stock, so they don't feel a spike at once. Before you know it, the bill rises.\n"
    "Some owners pushed prices up in May. Others took a sharp turn toward cheaper blends.\n"
    "The stage is set for more increases. Retail prices may stay high.\n"
)
ARTICLE2 = ARTICLE + "Many shops raised the stakes by cutting hours.\n"   # 本文変更(STALE)用

CALL1 = [{"phrase": "pushed prices up", "word_count": 3}, {"phrase": "took a sharp turn", "word_count": 4},
         {"phrase": "time lag", "word_count": 2}]
CALL2 = [{"phrase": "feel a spike", "reason_ja": "理由A", "word_count": 3}, {"phrase": "in stock", "reason_ja": "理由B", "word_count": 2},
         {"phrase": "built in", "reason_ja": "理由C", "word_count": 2}, {"phrase": "raw beans", "reason_ja": "理由D", "word_count": 2},
         {"phrase": "Before you know it", "reason_ja": "理由E", "word_count": 4}]
KANJI = "一二三四五六七八九"


def jl(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def jd(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def rd(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def wr(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _parse_items_json(user_message: str, marker: str):
    if marker not in user_message:
        raise AssertionError(f"fixture marker {marker!r} not in message head={user_message[:300]!r} type={type(user_message)}")
    tail = user_message.split(marker, 1)[1]
    obj, _ = json.JSONDecoder().raw_decode(tail.lstrip())
    return obj


class Counters(dict):
    def __missing__(self, k):
        return 0


class Env:
    """with Env(tmp, ...) as env: ... 。env.n[...]で各LLM由来関数の呼出回数。"""

    def __init__(self, tmp, *, call1=None, call2=None, bad_phrases=(), qa_fail_phrases=(), red_ng_pairs=None, final_red_seq=None,
                 gloss_fail_phrases=(), call1_seq=None, call2_seq=None):
        self.tmp = tmp
        self.call1_seq = call1_seq if call1_seq is not None else [call1 if call1 is not None else CALL1]
        self.call2_seq = call2_seq if call2_seq is not None else [call2 if call2 is not None else CALL2]
        self.bad_phrases = set(bad_phrases)
        self.qa_fail_phrases = set(qa_fail_phrases)
        self.red_ng_pairs = red_ng_pairs or []     # 候補全体QAでNGにするペア [(rank_a, rank_b)] -> 呼出順に1回目のみ。None=PASS
        self.final_red_seq = list(final_red_seq or [])   # 確定集合QAの結果列 ("PASS"/"NG")
        self.gloss_fail_phrases = set(gloss_fail_phrases)
        self.n = Counters()
        self.messages1, self.messages2 = [], []
        self.canon_inputs = []
        self.red_inputs = []
        self._patches = []

    # ---- fakes
    def _make1(self, msg, **kw):
        self.messages1.append(msg)
        i = self.n["call1_factory"]
        self.n["call1_factory"] += 1
        r = self.call1_seq[min(i, len(self.call1_seq) - 1)]

        def fn():
            self.n["call1"] += 1
            raw = r if isinstance(r, str) else json.dumps({"items": r}, ensure_ascii=False)
            return raw, "gpt-6-luna", f"resp1_{self.n['call1']}"
        return fn

    def _make2(self, msg, **kw):
        self.messages2.append(msg)
        i = self.n["call2_factory"]
        self.n["call2_factory"] += 1
        r = self.call2_seq[min(i, len(self.call2_seq) - 1)]

        def fn():
            self.n["call2"] += 1
            if isinstance(r, Exception):
                raise r
            raw = r if isinstance(r, str) else json.dumps({"items": r}, ensure_ascii=False)
            return raw, "gpt-6-luna", f"resp2_{self.n['call2']}"
        return fn

    def _canon(self, user_message, **kw):
        items = _parse_items_json(user_message, "【Key Phrase候補(JSON)】\n")
        self.canon_inputs.append([it["display_phrase"] for it in items])
        out = []
        for it in items:
            kp = "totally different" if it["display_phrase"] in self.bad_phrases else it["display_phrase"]
            row = {"rank": it["rank"], "key_phrase": kp, "changed_from_display_phrase": kp != it["display_phrase"],
                   "normalization_reason": "none", "reasoning": "r"}
            for f in kc.QA_FIELDS:
                row[f] = "PASS"
            if it["display_phrase"] in self.qa_fail_phrases:
                row["qa_standalone_natural_unit"] = "FAIL"
            out.append(row)

        def fn():
            self.n["canon"] += 1
            return json.dumps({"items": out}, ensure_ascii=False), "gpt-6-luna", "canon_resp"
        return fn

    def _gloss(self, msg, **kw):
        targets = _parse_items_json(msg, "【対象項目】\n")
        out = []
        for t in targets:
            ok = t.get("display_phrase_before_canonicalization") not in self.gloss_fail_phrases and t.get("key_phrase") not in self.gloss_fail_phrases
            out.append({"rank": t["rank"], "current_gloss_consistent": False,
                        "japanese_gloss": (f"意味{KANJI[(t['rank'] - 1) % 9]}" if ok else "アルファ(bad)"),
                        "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "r", "added_word_mappings": []})
        if isinstance(msg, ga.NewGenMessage):
            for o in out:
                o.update({"meaning_in_text_en": "meaning", "naive_ja": "字義訳", "naive_ja_conveys": "yes"})

        def fn():
            self.n["gloss"] += 1
            return json.dumps({"items": out}, ensure_ascii=False), "gpt-6-luna", "gloss_resp"
        fn.last_usage = None
        return fn

    def _red(self, msg, **kw):
        import itertools
        ranks = [int(x) for x in re.findall(r'"rank": (\d+)', msg.split("【Key Phrase", 1)[1])]
        self.red_inputs.append(ranks)
        is_final = self.n["red"] >= 1 and self._in_final
        seq_pos = self.n["red"]
        ng_pair = None
        if not self._in_final:
            if self.red_ng_pairs and self.n["red_cand"] == 0:
                ng_pair = self.red_ng_pairs[0]
            self.n["red_cand"] += 1
        else:
            st = self.final_red_seq.pop(0) if self.final_red_seq else "PASS"
            if st == "NG":
                ng_pair = (min(ranks), sorted(ranks)[1])
            self.n["red_final"] += 1
        pairs = [{"rank_a": a, "rank_b": b, "meaning_overlap": "PASS", "usage_context_overlap": "PASS",
                  "grammatical_teaching_value_overlap": "PASS", "conceptual_role_overlap": "PASS",
                  "is_near_duplicate": bool(ng_pair and (a, b) == tuple(ng_pair)), "reasoning": "r"}
                 for a, b in itertools.combinations(sorted(ranks), 2)]

        def fn():
            self.n["red"] += 1
            return json.dumps({"pairs": pairs}), "gpt-6-luna", "red_resp"
        return fn

    _in_final = False

    def __enter__(self):
        self._patches = [
            mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", os.path.join(self.tmp, "telemetry.jsonl")),
            mock.patch.object(rv, "STORE_ROOT", os.path.join(self.tmp, "store")),
            mock.patch.object(ft, "make_selector_fn", self._make1),
            mock.patch.object(p2v, "make_vocab_selector_fn", self._make2),
            mock.patch.object(kc, "make_canonicalization_fn", self._canon),
            mock.patch.object(ga, "make_alignment_fn", self._gloss),
            mock.patch.object(rq, "make_redundancy_qa_fn", self._red),
            mock.patch("time.sleep", lambda s: None),
        ]
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *a):
        for p in reversed(self._patches):
            p.stop()
        return False

    def total_llm_calls(self) -> int:
        return sum(self.n[k] for k in ("call1", "call2", "canon", "gloss", "red"))


class KpTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        # 共有NG registryのstoreは常にtmpへ(実リポジトリの`er119_output/`へ書かない。実storeのNGが当日の実runの候補に効くのを防ぐため、全testで隔離する)
        p = mock.patch.object(rv, "STORE_ROOT", os.path.join(self.tmp, "store"))
        p.start()
        self.addCleanup(p.stop)
        self.run_dir = os.path.join(self.tmp, "run1")
        self.kp_dir = os.path.join(self.run_dir, "b1b", "key_phrases")
        self.kp_dir_a2 = os.path.join(self.run_dir, "a2", "key_phrases")

    def ensure(self, env, kp_dir=None, level="b1b", text=ARTICLE, run_dir=None, slug="coffee", family="x"):
        """ensure_kp_reviewをEnv経由のmockで実行(実コードのgenerate/redundancyを通す)。"""
        import er119_kp_candidates_01 as kcand
        kp_dir = kp_dir or (self.kp_dir if level == "b1b" else self.kp_dir_a2)
        run_dir = run_dir or self.run_dir
        process = "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT"
        src_level = "B1" if level == "b1b" else "A2"
        gen = kcand.make_generate_fn(text, kp_dir, f"aid_{level}", src_level, level, process, stop_check_fn=None)

        def red(items, name):
            env._in_final = True
            try:
                return kcand.make_redundancy_fn(text, kp_dir, f"aid_{level}", process)(items, name)
            finally:
                env._in_final = False
        return rv.ensure_kp_review(kp_dir, run_dir=run_dir, family=family, slug=slug, level=level, text=text, generate_fn=gen,
                                   redundancy_fn=red, run_hint=run_dir)

    def declare(self, run_dir=None, by="tester", reason="test", rounds=(1,)):
        return rv.add_declaration(run_dirs=[run_dir or self.run_dir], by=by, reason=reason, rounds=list(rounds))


def declare_in_mock_contexts(runner_module):
    """test専用: 既存のZ mock E2E系testが『KP Human Review導入前と同じく最後まで進む』ように、runner_module.build_mock_contextを
    『Human不在を明示宣言済みのctx』を返すようにwrapする(宣言は通常のadd_declaration=宣言ファイル。runnerのProductionコードには暗黙のauto経路を作らない)。
    本番のbuild_mock_context(CLI --mode mock)は無変更で、宣言なし=待機のまま。"""
    if getattr(runner_module.build_mock_context, "_er119_wrapped", False):
        return
    orig = runner_module.build_mock_context

    def wrapped(*a, **k):
        ctx = orig(*a, **k)
        rv.add_declaration(run_dirs=[ctx.out_dir], by="test-fixture", reason="既存mock E2E testのfixture(Human不在を明示宣言)")
        return ctx
    wrapped._er119_wrapped = True
    runner_module.build_mock_context = wrapped


def declare_ctx(ctx):
    """test専用: mock ctxのrunについて『Human不在』を明示宣言する(add_declarationを呼ぶだけ。ctxを返す)。"""
    rv.add_declaration(run_dirs=[ctx.out_dir], by="test-fixture", reason="既存mock E2E testのfixture(Human不在を明示宣言)")
    return ctx
