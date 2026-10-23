# -*- coding: utf-8 -*-
"""SC-4/SC-5/D1: HR queue 88実イベントを Ledger全除外(初見語)/現行Ledger で 原本 vs RET で再評価する。表は当該記事のTTS canonical和集合から gpt-6-luna で構築(cache)。
変種: V0=原本, V1=RET(literal OF-01: eligibleのみ), V2=RET(general_in_phrase=True)。RET-3は常時ON。"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
llm = cached_llm(0)
rows = [(i, r) for i, r, c in load_hr_rows() if not c]
groups = {}
for i, r in rows:
    k, segs, how = group_key_and_segments(r)
    groups.setdefault(k, {"segs": segs, "how": how, "rows": []})["rows"].append(i)
# HR-only群は群内HR canonicalの和集合
for k, g in groups.items():
    if g["segs"] is None:
        seen, segs = set(), []
        for i in g["rows"]:
            t = dict(rows)[i]["canonical_text"] if False else next(r for j, r in rows if j == i)["canonical_text"]
            if t not in seen:
                seen.add(t); segs.append(ret.Seg(text=t, role="FULL_STORY"))
        g["segs"] = segs
tables = {}
cov = collections.Counter()
for k, g in groups.items():
    tb = ret.build_entity_table(g["segs"], llm=llm, usage_log=USAGE_LOG, tag=k)
    tables[k] = tb
    cov[g["how"]] += len(g["rows"])
    print(k, g["how"], "segs", len(g["segs"]), tb.status, [(e.surface, e.grade) for e in tb.entries if e.usable][:8])
json.dump({k: tb.to_dict() for k, tb in tables.items()}, open(os.path.join(HERE, "entity_tables_hr_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
out = []
for i, r in rows:
    kw = inputs_for(r)
    if kw is None:
        continue
    k = next(k for k, g in groups.items() if i in g["rows"])
    base_tb = tables[k]
    rec = {"i": i, "group": k, "canon": r["canonical_text"][:160], "wav": r["wav_path"][-70:]}
    for lm, led in (("excl", ledger_tokens(True)), ("cur", ledger_tokens(False))):
        o = run_orig(kw, led)
        rec[lm] = {"orig": [o.accept, o.reason, o.detail if not o.accept else None, [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence) for x in o.diffs]]}
        for var, gip in (("V1", False), ("V2", True)):
            tb = ret.EntityTable(base_tb.entries, status=base_tb.status, meta=base_tb.meta, general_in_phrase=gip)
            d = run_trial(kw, led, tb)
            rec[lm][var] = [d.accept, d.reason, d.detail if not d.accept else {k2: v for k2, v in d.detail.items() if k2 != "secondary_only_noise"},
                            [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence, x.similarity_primary) for x in d.diffs]]
    out.append(rec)
json.dump(out, open(os.path.join(HERE, "sc4_hr_replay_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


def klass(acc, rsn):
    if acc: return "A_accepted"
    if rsn == "NO_PROPER_NOUN_EVIDENCE": return "B_no_evidence"
    if rsn == "SECONDARY_NOT_ENTITY_ONLY": return "C_secondary_span_merge"
    if rsn in ("ASR_SIDES_ALL_GENERAL_WORDS", "CANONICAL_TOKEN_IS_GENERAL_WORD"): return "D_general_word_block"
    if rsn == "SECONDARY_ONLY_NOISE_LIMIT": return "C2_secondary_noise"
    return "E_non_entity_cause"
for lm in ("cur", "excl"):
    for v in ("orig", "V1", "V2"):
        c = collections.Counter(klass(o[lm][v][0], o[lm][v][1]) for o in out)
        print(lm, v, dict(sorted(c.items())), "pool(A..D)=", sum(n for k2, n in c.items() if k2[0] in "ABCD"))
print("coverage (rows by table input)", dict(cov), "spend", ret.spend_so_far(USAGE_LOG))
