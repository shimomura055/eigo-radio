# -*- coding: utf-8 -*-
r"""KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_02: _gate_chain抽出(R-6)のgolden生成・比較support(API 0、全LLM mock)。

抽出前(HEAD)のコードで生成した候補docを docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/golden_02a/<scenario>.json に固定し、
抽出後(および補完機能追加後のOFF時・E=0時)の候補docが一致することを er119_kp_backfill_test_01 が検査する。
生成: .venv\Scripts\python.exe er119_kp_backfill_golden_01.py --write   (抽出前のコードでのみ実行する。以後は上書きしない)
"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import os
import re
import sys
import tempfile
from unittest import mock

import er119_kp_candidates_01 as kcand
import er119_kp_human_review_01 as rv
from er119_test_support_01 import ARTICLE, CALL1, CALL2, Env

ROOT = os.path.dirname(os.path.abspath(__file__))
GOLDEN_DIR = os.path.join(ROOT, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "golden_02a")

ART_R = ("# Wiring test\n\nThe owner pushed prices up in May. They let people try whatever catches their interest. "
         "The cafe keeps raw beans in stock. Her laughter rose above the other voices. Nobody knew the plan, and I guess it can’t be helped. "
         "In the end, the band took a sharp turn.\n")
CALL1_R = [{"phrase": "catch their interest", "word_count": 3}, {"phrase": "pushed prices up", "word_count": 3}, {"phrase": "in stock", "word_count": 2}]
CALL2_R = [{"phrase": "rose above", "reason_ja": "M1", "word_count": 2}, {"phrase": "it can’t be helped", "reason_ja": "idiom", "word_count": 4},
           {"phrase": "took a sharp turn", "reason_ja": "plain", "word_count": 4}]
CALL1_C = [{"phrase": "pushed prices up", "word_count": 3}, {"phrase": "in stock", "word_count": 2}, {"phrase": "took a sharp turn", "word_count": 4}]

_VOLATILE = ("generated_at", "candidates_sha256")


def normalize(doc: dict, tmp: str) -> dict:
    d = json.loads(json.dumps(doc, ensure_ascii=False))
    for k in _VOLATILE:
        d.pop(k, None)
    s = json.dumps(d, ensure_ascii=False, sort_keys=True)
    s = s.replace(tmp.replace("\\", "\\\\"), "<TMP>").replace(tmp, "<TMP>").replace(tmp.replace("\\", "/"), "<TMP>")
    return json.loads(s)


def _ensure(tmp: str, env, **kw) -> dict:
    from er119_test_support_01 import KpTestCase
    case = KpTestCase("run")
    case.tmp = tmp
    case.run_dir = os.path.join(tmp, "run1")
    case.kp_dir = os.path.join(case.run_dir, "b1b", "key_phrases")
    case.kp_dir_a2 = os.path.join(case.run_dir, "a2", "key_phrases")
    with mock.patch.object(rv, "STORE_ROOT", os.path.join(tmp, "store")):
        case.ensure(env, **kw)
        return rv.load_candidates(case.kp_dir)


def _direct(tmp: str, env, **kw) -> dict:
    kp_dir = os.path.join(tmp, "direct", "key_phrases")
    r = kcand.generate_candidates(ARTICLE, kp_dir, "aid_direct", "B1", "b1b", 1, kw.pop("ng_entries", []), process="B1_SUPPORT", **kw)
    return r["doc"] if r["ok"] else r


def _z_stubs():
    def src_fn(items):
        new = {it["rank"]: dict(it, source_sentence_id="S1") for it in items}
        drop = {}
        for it in items:
            if "raw beans" in (it.get("used_form") or ""):
                drop[it["rank"]] = ["SRC D1: stub"]
        return new, drop

    def person_fn(merged):
        return merged
    return src_fn, person_fn


# name -> (Env kwargs, runner, runner kwargs)。Env kwargsはrescue_envを含め明示固定(シェル非依存)
SCENARIOS = {
    "s01_default_8": (dict(), "ensure", dict()),
    "s02_canon_drop_rescue_off": (dict(bad_phrases=["feel a spike"], rescue_env="0"), "ensure", dict()),
    "s03_call1_all_bad_rescue_off": (dict(bad_phrases=[p["phrase"] for p in CALL1], rescue_env="0"), "ensure", dict()),
    "s04_outer_retry_replace": (dict(call1_seq=[CALL1, [{"phrase": "Before you know it", "word_count": 4}, {"phrase": "stay high", "word_count": 2}]],
                                     call2_seq=[[{"phrase": "in stock", "reason_ja": "x", "word_count": 2}], CALL2[3:5]],
                                     bad_phrases=["pushed prices up", "took a sharp turn"]), "ensure", dict()),
    "s05_shortfall_no_drop": (dict(call2=[{"phrase": "in stock", "reason_ja": "x", "word_count": 2}]), "ensure", dict()),
    "s06_qa_fail": (dict(qa_fail_phrases=["pushed prices up"]), "ensure", dict()),
    "s07_gloss_hr": (dict(gloss_fail_phrases=["time lag"]), "ensure", dict()),
    "s08_redundancy_pair": (dict(red_ng_pairs=[(1, 2)]), "ensure", dict()),
    "s09_dup_top3": (dict(call2=[{"phrase": "time lag", "reason_ja": "dup", "word_count": 2}] + CALL2[:2]), "ensure", dict()),
    "s10_rescued_not_auto": (dict(call1=CALL1_C, call2=[], canon_keys={"pushed prices up": "totally different"}, qa_mismatch={"pushed prices up"}),
                             "ensure", dict(text=ART_R)),
    "s11_rescue_selection_stage": (dict(call1=CALL1_R, call2=CALL2_R, canon_keys={"rose above": "rise above the other voices"}), "ensure", dict(text=ART_R)),
    "s12_direct_z_stubs": (dict(), "direct_z", dict()),
    "s13_direct_human_ng": (dict(), "direct_ng", dict()),
}


def run_scenario(name: str, extra_env: dict | None = None) -> dict:
    env_kw, runner, kw = SCENARIOS[name]
    with tempfile.TemporaryDirectory() as tmp:
        with Env(tmp, **env_kw) as env, mock.patch.dict(os.environ, dict(extra_env or {})):
            if runner == "ensure":
                doc = _ensure(tmp, env, **kw)
            elif runner == "direct_z":
                src_fn, person_fn = _z_stubs()
                doc = _direct(tmp, env, src_fn=src_fn, person_repair_fn=person_fn)
            else:
                ng = [rv.make_ng_entry({"candidate_id": rv.candidate_id_for("in stock"), "selection_phrase": "in stock", "used_form": "in stock"}, "NG", "tester")]
                doc = _direct(tmp, env, ng_entries=ng)
        return normalize(doc, tmp)


def strip_additive(doc: dict) -> dict:
    """golden比較用: 補完機能が加えた追記専用の項目(委任_02b以降)を除く。既存項目の値は一切触らない。"""
    d = json.loads(json.dumps(doc, ensure_ascii=False))
    for k in ADDITIVE_DOC_KEYS:
        d.pop(k, None)
    for c in d.get("candidates", []):
        for k in ADDITIVE_CAND_KEYS:
            c.pop(k, None)
    return d


ADDITIVE_DOC_KEYS = ("backfill", "shortfall_detail")
ADDITIVE_CAND_KEYS = ("kind",)


def golden_path(name: str) -> str:
    return os.path.join(GOLDEN_DIR, name + ".json")


if __name__ == "__main__":
    if "--write" in sys.argv:
        os.makedirs(GOLDEN_DIR, exist_ok=True)
        for n in SCENARIOS:
            d = run_scenario(n)
            with open(golden_path(n), "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1, sort_keys=True)
            print(n, "cands=", len(d.get("candidates", [])), "dropped=", len(d.get("dropped", [])), "outer=", d.get("outer_attempts"))
