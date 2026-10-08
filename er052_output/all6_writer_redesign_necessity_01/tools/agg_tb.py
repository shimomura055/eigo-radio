# -*- coding: utf-8 -*-
import glob, json, os, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
B = "er052_output/all6_writer_redesign_necessity_01/T-B"
items = {i["item_id"]: i for i in json.load(open(f"{B}/items.json", encoding="utf-8"))["items"]}
recs = [json.load(open(f, encoding="utf-8")) for f in glob.glob(f"{B}/results/*.json")]
M = ["gpt-5.6-luna", "gpt-6-luna"]
out = []
def P(s=""): out.append(s)

def rate(kind, model, rep, key):
    rs = [r for r in recs if r["kind"] == kind and r["model_requested"] == model and (rep is None or r["rep"] == rep)]
    n = len(rs)
    if key == "matched_major": k = sum(r["matched_severity"] == "MAJOR" for r in rs)
    elif key == "matched_any": k = sum(r["matched_severity"] in ("MAJOR", "MINOR") for r in rs)
    elif key == "article_major": k = sum(r["article_max_severity"] == "MAJOR" for r in rs)
    elif key == "article_any": k = sum(r["article_max_severity"] in ("MAJOR", "MINOR") for r in rs)
    return k, n

P("# T-B 集計(既知NG記事の再判定、n=2/モデル)")
P(f"記録数: {len(recs)}(items={len(items)} x 2モデル x 2反復)。Fact Check=vfl01.run_deviation_check(同一prompt/schema)。")
P("")
P("## 1. 検出率(試行単位=item x 反復)")
P("| 区分 | 指標 | gpt-5.6-luna | gpt-6-luna |")
P("|---|---|---|---|")
for kind, label in (("major", "重大"), ("minor", "軽微")):
    for key, kl in (("matched_major", "NG文に対応する逸脱がMAJOR"), ("matched_any", "NG文に対応する逸脱がMAJOR/MINOR"),
                    ("article_major", "記事内にMAJORが1件でもある(記事単位)"), ("article_any", "記事内に逸脱が1件でもある(記事単位)")):
        a = rate(kind, M[0], None, key); b = rate(kind, M[1], None, key)
        P(f"| {label}({a[1]//2 if a[1] else 0}件x2) | {kl} | {a[0]}/{a[1]} ({100*a[0]/max(a[1],1):.0f}%) | {b[0]}/{b[1]} ({100*b[0]/max(b[1],1):.0f}%) |")
P("")
P("## 2. 反復別(matched_major / matched_any)")
P("| 区分 | 反復 | gpt-5.6-luna major | gpt-6-luna major | gpt-5.6-luna any | gpt-6-luna any |")
P("|---|---|---|---|---|---|")
for kind, label in (("major", "重大"), ("minor", "軽微")):
    for rep in (1, 2):
        c = [rate(kind, m, rep, k) for k in ("matched_major", "matched_any") for m in M]
        P(f"| {label} | r{rep} | " + " | ".join(f"{x[0]}/{x[1]}" for x in c) + " |")
P("")
P("## 3. item別(r1,r2の順。MAJ=MAJOR対応/MIN=MINOR対応/-=対応なし。括弧内=記事全体の最大severity)")
P("| item | 種別 | 型 | 5.6 r1 | 5.6 r2 | 6 r1 | 6 r2 |")
P("|---|---|---|---|---|---|---|")
sym = {"MAJOR": "MAJ", "MINOR": "MIN", "NONE": "-"}
def cell(iid, m, r):
    x = [q for q in recs if q["item_id"] == iid and q["model_requested"] == m and q["rep"] == r]
    return f"{sym[x[0]['matched_severity']]}({x[0]['article_max_severity'][:3]})" if x else "?"
for iid, it in items.items():
    P(f"| {iid} | {it['kind']} | {it['ng_type']} | " + " | ".join(cell(iid, m, r) for m in M for r in (1, 2)) + " |")
P("")
P("## 4. MINOR->MAJOR非対称(6-lunaが5.6より重く判定/軽く判定した件数、item x 反復の同一rep比較)")
up = down = same = 0
for iid in items:
    for r in (1, 2):
        a = [q for q in recs if q["item_id"] == iid and q["model_requested"] == M[0] and q["rep"] == r]
        b = [q for q in recs if q["item_id"] == iid and q["model_requested"] == M[1] and q["rep"] == r]
        if not (a and b): continue
        o = {"NONE": 0, "MINOR": 1, "MAJOR": 2}
        da, db = o[a[0]["matched_severity"]], o[b[0]["matched_severity"]]
        up += db > da; down += db < da; same += db == da
P(f"6-luna がより重い判定: {up} / より軽い判定: {down} / 同じ: {same}(item x rep比較)")
# 誤検出(参考): MAJOR逸脱のうちitemのNG文と無関係なもの
extra = collections.Counter()
for r in recs:
    for d in r["deviations"]:
        if d.get("severity") == "MAJOR" and not any(abs(1) for m in r["matched"] if m["claim"] == d.get("claim_in_article")):
            extra[r["model_requested"]] += 1
P(f"参考: NG文に対応しないMAJOR逸脱の延べ数(記事内の別箇所の指摘。真偽は未確認): 5.6={extra[M[0]]}, 6={extra[M[1]]}")
P("")
cj = json.load(open(f"{B}/cost.json", encoding="utf-8")) if os.path.exists(f"{B}/cost.json") else None
P(f"cost.json(既存集計関数、gpt-6-lunaはpricing表に無く0円計上の可能性あり): {cj}")
open(f"{B}/TB_SUMMARY.md", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
