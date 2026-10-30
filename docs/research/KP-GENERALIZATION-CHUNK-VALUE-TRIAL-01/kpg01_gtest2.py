# -*- coding: utf-8 -*-
import json, os, sys
import kpg01_llm as L, kpg01_gen2 as G, kpg01_validate as V
from kpg01_gtest import CASES, corpus, sent_of
HERE = os.path.dirname(os.path.abspath(__file__))
def run(model, eff, tag):
    out = []
    for cid, span in CASES:
        sel = [{"span": span, "sentence": sent_of(cid, span), "chunk_type": "n/a", "chunk_reason_ja": "(一般化段の単体test)"}]
        o, m = L.call(model, G.prompt_G2(corpus[cid]["text"], sel), G.G2_SCHEMA, effort=eff, tag=f"gtest2:{tag}:{cid}")
        x = o["items"][0]
        df, err = G.assemble(span, x["tokens"])
        ok, why = V.display_check(df, span) if df else (False, [err])
        out.append(dict(case=cid, span=span, display_form=df, err=err, gloss_ja=x["gloss_ja"], sense_note_ja=x["sense_note_ja"], note=x["note_ja"], validator_ok=ok, why=why, cost=m["cost_jpy"]))
    return out
if __name__ == "__main__":
    model, eff, tag = sys.argv[1], (sys.argv[2] if sys.argv[2] != "none" else None), sys.argv[3]
    r = run(model, eff, tag)
    print("==", tag, "¥", round(sum(x["cost"] for x in r), 2))
    for x in r: print(f"  {x['span']:34s} -> {str(x['display_form']):28s} | {x['gloss_ja']} | {x['sense_note_ja']} | ok={x['validator_ok']} {x['why']} {x['err'] or ''}")
    json.dump(r, open(os.path.join(HERE, "kpg01_work", f"gtest2_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
