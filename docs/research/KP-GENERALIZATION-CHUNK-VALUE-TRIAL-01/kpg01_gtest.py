# -*- coding: utf-8 -*-
"""一般化段だけの単体test(選定と独立): ユーザー提示の一般化5例を、現行候補の本文・文のまま一般化段に通す。"""
import json, os, sys
import kpg01_llm as L, kpg01_methods as M, kpg01_validate as V
HERE = os.path.dirname(os.path.abspath(__file__))
corpus = {c["id"]: c for c in json.load(open(os.path.join(HERE, "kpg01_work", "corpus.json"), encoding="utf-8"))}
CASES = [("untidi_a2", "take points away from"), ("untidi_a2", "make life work"), ("meta_w_a2", "At the time of writing"),
         ("jwst_m_a2", "narrow down the source"), ("jwst_m_a2", "turned the usual steps around")]
def sent_of(cid, span):
    for c in corpus[cid]["before"]["candidates"]:
        if c["selection_phrase"].lower() == span.lower(): return c["sentence"]
def run(model, eff, tag):
    out = []
    for cid, span in CASES:
        sel = [{"span": span, "sentence": sent_of(cid, span), "chunk_type": "n/a", "chunk_reason_ja": "(一般化段の単体test)"}]
        o, m = L.call(model, M.prompt_B3(corpus[cid]["text"], sel), M.B3_SCHEMA, effort=eff, tag=f"gtest:{tag}:{cid}")
        x = o["items"][0]
        df = V.strip_trailing_slot(x["display_form"])
        ok, why = V.display_check(df, span)
        out.append(dict(case=cid, span=span, display_form=df, raw=x["display_form"], gloss_ja=x["gloss_ja"], sense_note_ja=x["sense_note_ja"], note=x["generalization_note_ja"], validator_ok=ok, why=why, cost=m["cost_jpy"]))
    return out
if __name__ == "__main__":
    res = {}
    for model, eff, tag in [("gpt-6-luna", None, "luna")]:
        res[tag] = run(model, eff, tag)
        print("==", tag, "¥", round(sum(r["cost"] for r in res[tag]), 2))
        for r in res[tag]: print(f"  {r['span']:34s} -> {r['display_form']:28s} | {r['gloss_ja']} | {r['sense_note_ja']} | ok={r['validator_ok']} {r['why']}")
    json.dump(res, open(os.path.join(HERE, "kpg01_work", "gtest_results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
