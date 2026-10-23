# -*- coding: utf-8 -*-
"""SC-1 同値性(DefaultOffIsolation相当): 表なし/空/無関係表 のとき trial版 == er103原本(D1 HR queue 88 + D2 保存EN pair)。API 0。"""
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
PAIRS = "docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/pairs_02.jsonl"
import re
JA = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")
unrelated = ret.EntityTable([ret.Entry("Zzyzx Qwertyuiop", ["zzyzx", "qwertyuiop"], "person", "confirmed", ["t"], ["zzyzx", "qwertyuiop"], [])])
empty = ret.EntityTable([])
res = {"d1": {"n": 0, "mismatch": 0, "accept_orig": 0}, "d2": {"pairs": 0, "en": 0, "evaluated": 0, "mismatch": 0, "accept_orig": 0}}
for ledger_mode in ("current", "excluded"):
    led = ledger_tokens(exclude_all=(ledger_mode == "excluded"))
    for i, r, cont in load_hr_rows():
        if cont:
            continue
        kw = inputs_for(r)
        if kw is None:
            continue
        o = run_orig(kw, led)
        res["d1"]["n"] += 1
        res["d1"]["accept_orig"] += o.accept
        for tb in (None, empty, unrelated):
            if dec_sig(run_trial(kw, led, tb), strip_diag=(tb is unrelated)) != dec_sig(o):
                res["d1"]["mismatch"] += 1
                print("MISMATCH d1", i, ledger_mode)
pairs = [json.loads(l) for l in open(PAIRS, encoding="utf-8") if l.strip()]
res["d2"]["pairs"] = len(pairs)
led = ledger_tokens()
for p in pairs:
    canon, asr = p["canonical"], p["asr"]
    if JA.search(canon):
        continue
    res["d2"]["en"] += 1
    cp = val.classify_asr_match(canon, asr)
    if cp.should_pass:
        continue
    cs = val.classify_asr_match(canon, asr)
    kw = dict(canonical_text=canon, primary_cls=cp, secondary_cls=cs, primary_text=asr, secondary_text=asr, judge_state="NG_BOTH",
              judge_reason_code="secondary_not_accepted", role="FULL_STORY", p3_entry="p3_primary_ng")
    o = run_orig(kw, led)
    res["d2"]["evaluated"] += 1
    res["d2"]["accept_orig"] += o.accept
    for tb in (None, empty, unrelated):
        if dec_sig(run_trial(kw, led, tb), strip_diag=(tb is unrelated)) != dec_sig(o):
            res["d2"]["mismatch"] += 1
            print("MISMATCH d2", canon[:60])
# 原本ソースhash
res["drift_guard_equal"] = ev.source_hashes() == ev.ORIG_SOURCE_SHA256
res["PASS"] = res["d1"]["mismatch"] == 0 and res["d2"]["mismatch"] == 0 and res["drift_guard_equal"]
json.dump(res, open(os.path.join(HERE, "sc1_equivalence_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
