# -*- coding: utf-8 -*-
"""検出器候補の費用見積(登録単価 x 見積トークン)。python estimate_cost_01.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flagger_lib as L
import prompts_flagger as P

SYS_D1 = L.estimate_tokens(P.d1_system("rollback反転"))
SYS_D2 = L.estimate_tokens(P.d2_system())
# 記事: 25文 x 約35token + 台帳 Fact 10/30件 x 約70token
SENT = 25 * 35
OUT = {"low": 600, "high": 4000}  # 推論token込みの出力/呼び出し


def art(model, det, facts_n):
    p = L.load_prices(model)
    if det == "d2":
        calls, sysm, fk = 1, SYS_D2, facts_n
    elif det == "d1full":
        calls, sysm, fk = 5, SYS_D1, facts_n
    else:  # d1map: 文ごと上位3件の和集合 ~ 最大min(facts, 3*?)→ 見積は facts の 40%(最低6件)
        calls, sysm, fk = 5, SYS_D1, max(6, int(facts_n * 0.4))
    inp = calls * (sysm + SENT + fk * 70)
    lo = L.cost_yen(p, inp, calls * OUT["low"])
    hi = L.cost_yen(p, inp, calls * OUT["high"])
    return calls, inp, lo, hi


def case(model, det):
    p = L.load_prices(model)
    calls = 1 if det == "d2" else 5
    sysm = SYS_D2 if det == "d2" else SYS_D1
    inp = calls * (sysm + 250)  # 1ケース=1文+Fact1件+前後文
    return calls, L.cost_yen(p, inp, calls * OUT["low"]), L.cost_yen(p, inp, calls * OUT["high"])


print("sys tokens D1=%d D2=%d" % (SYS_D1, SYS_D2))
print("## 1記事(25文) 見積 JPY (出力%d-%d tok/呼び出し)" % (OUT["low"], OUT["high"]))
for model in ("gpt-6.1-sol", "gpt-6-astra", "deepseek-v4-pro"):
    for det in ("d2", "d1map", "d1full"):
        for fn in (10, 30):
            c, i, lo, hi = art(model, det, fn)
            print("%-16s %-7s facts=%-2d calls=%d in=%d JPY %.1f - %.1f" % (model, det, fn, c, i, lo, hi))
print("## 1ケース(casebank) 見積 JPY")
for model in ("gpt-6.1-sol", "gpt-6-astra", "deepseek-v4-pro"):
    for det in ("d2", "d1"):
        c, lo, hi = case(model, det)
        print("%-16s %-3s calls=%d JPY %.2f - %.2f" % (model, det, c, lo, hi))
