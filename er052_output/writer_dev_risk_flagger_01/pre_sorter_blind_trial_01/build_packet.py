# -*- coding: utf-8 -*-
"""Phase1 (JPY0): Blind packet固定。POST-EN-TRIAL-01のflags/A3,A4(読み取りのみ)からUnion29件を機械抽出。
除外: confidence/type/severity/Known-New/旧Checker/Humanコメント/他モデル回答/稿のstatus・route。"""
import json, glob, os, hashlib, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "post_en_trial_01")
man = json.load(open(os.path.join(SRC, "manifest_post_en_01.json"), encoding="utf-8"))
THEME = {"meta": "Meta Muse AI agent", "hormuz": "Hormuz / oil", "space_weapons": "Space weapons", "small_bag": "Small bag",
         "byd_recall": "BYD recall", "streaming_price": "Streaming price", "openai_copyright": "OpenAI copyright lawsuits",
         "semiconductor_earnings": "Semiconductor earnings"}
cnt = {}
for u in man["units"]: cnt[u["theme"]] = cnt.get(u["theme"], 0) + 1
seen = {}
sk = lambda s: int(s[1:])
items = []
for u in man["units"]:
    uid = u["unit"]; th = u["theme"]
    seen[th] = seen.get(th, 0) + 1
    tname = THEME[th] + (" (draft %d/%d)" % (seen[th], cnt[th]) if cnt[th] > 1 else "")
    F = {lv: json.load(open(glob.glob(os.path.join(SRC, "flags", "A%d" % lv, uid + "_*.json"))[0], encoding="utf-8")) for lv in (3, 4)}
    a3 = {f["sentence_id"]: f for f in F[3]["flags"]}; a4 = {f["sentence_id"]: f for f in F[4]["flags"]}
    sents = F[3]["sentences"]; assert sents == F[4]["sentences"]; facts = F[3]["facts"]; assert facts == F[4]["facts"]
    order = sorted(sents, key=sk)
    for s in sorted(set(a3) | set(a4), key=sk):
        i = order.index(s)
        ctx_b = [(x, sents[x]) for x in order[max(0, i - 2):i]]
        ctx_a = [(x, sents[x]) for x in order[i + 1:i + 3]]
        ids = sorted(set((a3.get(s) or {"fact_ids": []})["fact_ids"]) | set((a4.get(s) or {"fact_ids": []})["fact_ids"]))
        if ids:
            fx = [dict(fact_id=k, text=facts[k]) for k in ids]; fnote = None
        else:
            fx = [dict(fact_id=k, text=facts[k]) for k in facts]   # 全件同一規則: Fact未指定の場合は台帳の全Factを渡す
            fnote = "The flagger did not specify a corresponding Fact. The full Fact ledger of this article is given instead."
        reasons = {}
        if s in a3: reasons["A3"] = a3[s]["question"]
        if s in a4: reasons["A4"] = a4[s]["question"]
        items.append(dict(id="%s-%s" % (uid, s), theme=tname, flagged_sentence=dict(sid=s, text=sents[s]),
                          context_before=[dict(sid=a, text=b) for a, b in ctx_b], context_after=[dict(sid=a, text=b) for a, b in ctx_a],
                          facts=fx, facts_note=fnote, flag_reasons=reasons))
assert len(items) == 29, len(items)
print("items", len(items), "factless", sum(1 for x in items if x["facts_note"]))
batches = [items[:10], items[10:20], items[20:]]
assert [len(b) for b in batches] == [10, 10, 9]
pk = dict(packet_id="blind_packet_01", n_items=29, batches=[[x["id"] for x in b] for b in batches], items=items)
raw = json.dumps(pk, ensure_ascii=False, indent=1)
open(os.path.join(HERE, "blind_packet_01.json"), "w", encoding="utf-8", newline="\n").write(raw)
def render(x):
    L = ["## ITEM %s | Theme: %s" % (x["id"], x["theme"]), "", "Flagged sentence (%s): %s" % (x["flagged_sentence"]["sid"], x["flagged_sentence"]["text"]), "", "Context before:"]
    L += ["- (%s) %s" % (c["sid"], c["text"]) for c in x["context_before"]] or ["- (none)"]
    L += ["Context after:"] + (["- (%s) %s" % (c["sid"], c["text"]) for c in x["context_after"]] or ["- (none)"]) + [""]
    L += ["Corresponding Fact(s)" + (" [%s]" % x["facts_note"] if x["facts_note"] else "") + ":"]
    L += ["- [%s] %s" % (f["fact_id"], f["text"].replace("\n", " ")) for f in x["facts"]] + ["", "Reason(s) given by the flagger(s):"]
    L += ["- %s: %s" % (k, v) for k, v in x["flag_reasons"].items()] + [""]
    return "\n".join(L)
def batch_text(i): return "\n".join(render(x) for x in batches[i])
for i in range(3): open(os.path.join(HERE, "batch_text_%d.txt" % (i + 1)), "w", encoding="utf-8", newline="\n").write(batch_text(i))
md = ["# BLIND_PACKET_01 (人間可読。blind_packet_01.json と同内容。Trial/DEV)", "", "29件(ID順、バッチ10/10/9)。除外済み: confidence・type・severity・旧Checker・Known/Newラベル・Humanコメント・他モデル回答。", ""]
for i in range(3): md += ["# BATCH %d" % (i + 1), "", batch_text(i)]
open(os.path.join(HERE, "BLIND_PACKET_01.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md))
