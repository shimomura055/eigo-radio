# -*- coding: utf-8 -*-
"""Part 2(er120)のmock/dry-run用call_fn(API 0)。Z mockコンテキスト(er026 build_mock_context)とtestが共有する。
Production経路では使われない(realでは hooks 未指定=実client)。LLMの代わりに本文から決定論で候補/解説を作る。
call_fnの契約: prompt -> (text, response_model, usage, response_id)  (er120._run_llm)"""
from __future__ import annotations

import json
import re

import er006_model_routing_contract_01 as routing

MODEL = routing.SUPPORT_MODEL
_PARA_RE = re.compile(r"(?m)^\[P(\d+)\] (.+?)(?=\n\n\[P\d+\] |\Z)", re.S)
_SENT_RE = re.compile(r".+?[.!?…]+[”\"’']?(?=\s|$)")
_CLASSES = ["CLEFT", "SPEC", "INV"]


def _usage(n=1):
    return {"input_tokens": 1000 * n, "output_tokens": 400 * n, "cached_input_tokens": 0}


def mock_extract_call_fn(prompt: str):
    """Step A''の代わり: 本文の先頭付近の段落から、最大3件(CLEFT/SPEC/INV)の特徴を返す。文は本文の逐語。"""
    body = prompt.split("# 本文", 1)[-1]
    paras = [(int(n), t.strip()) for n, t in _PARA_RE.findall(body)]
    feats, used = [], 0
    for n, t in paras:
        if used >= 3:
            break
        m = _SENT_RE.match(t) or None
        sent = (m.group(0) if m else t).strip()
        if len(sent.split()) < 4:
            continue
        cls = _CLASSES[used]
        feats.append({"para": f"P{n}", "sentence": sent, "feature_class": cls, "front_kind": "", "misread_target": "SUBJECT",
                      "misread_quote": sent.split()[0], "misread_ja": "mockの読み違え", "omitted_words": "", "basic_only": False,
                      "teaching_value": "HIGH", "teaching_value_ja": "mockの読みどころ", "construct_ja": f"mock構文{cls}",
                      "points_ja": ["mockポイント"], "context_ja": "mock文脈"})
        used += 1
    return json.dumps({"features": feats, "no_feature_paras": []}, ensure_ascii=False), MODEL, _usage(), "mock_p2_extract"


STEPB_MOCK = ("=====ITEM 1=====\n【日本語訳】\nこれはmockの日本語訳です。\n【文法・構文の仕組み】\n**mock** の構文を説明します。\n"
              "【通常の表現・語順との比較】\n比較用：**mock sentence.**\n【意味・ニュアンス・表現効果】\nmockのニュアンスです。\n")


def mock_explain_call_fn(prompt: str):
    return STEPB_MOCK, MODEL, _usage(), "mock_p2_explain"


# ------------------------------------------------------------
# test用: X/Z runnerの `client` 経路(er120._resolve_call_fn)をAPI 0で置き換える。呼出は CALLS に積む(回数の証明に使う)
# ------------------------------------------------------------
CALLS = []


def factory(client, model, max_out):
    """er120._default_call_fn_factory と同じ(client, model, max_out)->call_fn。max_outでStep A''/Step Bを判別する。実clientは使わない。"""
    import er120_part2_grammar_production_01 as g

    def call_fn(prompt):
        kind = "extract" if max_out == g.MAXOUT_EXTRACT else "explain"
        CALLS.append(kind)
        return (mock_extract_call_fn if kind == "extract" else mock_explain_call_fn)(prompt)
    return call_fn
