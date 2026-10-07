# -*- coding: utf-8 -*-
"""T-B items.json builder (Trial専用、API無し)。"""
import json, os, collections, random, re, sys
sys.stdout.reconfigure(encoding="utf-8")
B = "er052_output/"
OUT = B + "all6_writer_redesign_necessity_01/T-B/items.json"
rows = [json.loads(l) for l in open(B + "open233_stage0_01/reclass/known_relation_ng.jsonl", encoding="utf-8")]
past = {r["item_id"]: r for r in rows if r["record"] == "past_major"}
inset = [r for r in rows if r["record"] == "in_set"]
excluded = []
items = []

def rd(p):
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None

def add(item_id, kind, run_dir, article_rel, ledger_path, ng_text, ng_type, stage, source_rel=None, extra=None):
    ap = f"{run_dir}/{article_rel}"
    art = rd(ap)
    if art is None or not os.path.exists(ledger_path):
        excluded.append({"item_id": item_id, "reason": "article_or_ledger_missing", "path": ap}); return
    items.append({"item_id": item_id, "kind": kind, "article_path": ap, "ledger_path": ledger_path,
                  "source_article_path": f"{run_dir}/{source_rel}" if source_rel else None,
                  "ng_text": ng_text, "ng_type": ng_type, "stage": stage, **(extra or {})})

E2E = B + "open233_allfact_note_e2e_02/runs/%s/nb/p2/%s"
def led(d): return d + "/research_ledger/verified_fact_ledger.txt"
# --- 重大 ---
majors = [
    ("PAST-meta-p2r2-02", E2E % ("meta", "rep2"), "ja_writer/revision2.md", "主体(対象)", "R2"),
    ("PAST-ai-p2r1-01", E2E % ("ai_control", "rep1"), "ja_writer/revision2.md", "未提示断定/比喩", "R2"),
    ("PAST-sw-p2r2-01", E2E % ("space_weapons", "rep2"), "ja_writer/revision2.md", "主体(発表内容)", "R2"),
    ("PAST-sw-p2r2-02", E2E % ("space_weapons", "rep2"), "ja_writer/revision2.md", "範囲(初めての対象)", "R2"),
]
for iid, d, rel, typ, st in majors:
    add(iid, "major", d, rel, led(d), past[iid]["text"], typ, st)
# EN-only majors (EN本文 + JA R2をsource)
add("PAST-ai-p2r1-02", "major", E2E % ("ai_control", "rep1"), "b1b/article.md", led(E2E % ("ai_control", "rep1")),
    past["PAST-ai-p2r1-02"]["text"], "主体(入替)", "EN", source_rel="ja_writer/revision2.md")
hd = B + "open233_note_transfer_matrix_01/runs/hormuz/nb/T0M0/rep2"
add("PAST-hormuz-T0M0r2-01", "major", hd, "b1b/article.md", led(hd), past["PAST-hormuz-T0M0r2-01"]["text"],
    "範囲(20%の対象)", "EN", source_rel="ja_writer/revision2.md")
# jb9k-03 (ccp ai_control rep1, R0由来)
jd = B + "open233_control_checker_polysemy_trial_01/runs/ai_control/control/rep1"
add("PAST-jb9k-03", "major", jd, "ja_writer/revision2.md", led(jd), past["PAST-jb9k-03"]["text"], "否定/未提示断定", "R0->R2")
excluded.append({"item_id": "PAST-ai-p2r2-07", "reason": "Rewrite工程が生成した一時的EN文で最終記事に残らず入力記事が存在しない"})
# --- 軽微20 ---
m2 = json.load(open(B + "open233_b3_trial_01/eval/_private/MAP_stage2.json", encoding="utf-8"))["articles"]
def b3_dir(a):
    v = m2.get(a)
    return None if not v else f"{B}open233_b3_trial_01/runs/{a.split('/')[0]}/nb/{v['variant']}/b{v['b3_rep']}/w1"
def tclass(r):
    t = r["sentence_type"]
    if "比喩" in (r.get("reason") or "") : return "比喩"
    if t in ("否定・不在", "多義語方向"): return "方向/極性"
    if t == "主語新規出現・置換": return "主体"
    if t in ("限定語消失", "全称"): return "範囲"
    if t in ("その他", "数値") and r.get("ledger_correspondence", "").startswith("新しい世界主張"): return "未提示断定"
    return None
cands = [r for r in inset if r["set"] == "open233_b3_trial_01" and r["list"] == "ng" and r["severity_eval"] == "minor"
         and r["grep"].get("R2") is True and tclass(r) and b3_dir(r["article"])]
random.Random(20261008).shuffle(cands)
cnt = collections.Counter(); picked = []
for r in cands:
    c = tclass(r)
    if cnt[c] >= 4: continue
    d = b3_dir(r["article"])
    if not os.path.exists(d + "/ja_writer/revision2.md"): continue
    lp = B + f"open233_polysemy_trial_02/ledgers/{r['article'].split('/')[0]}/control/research_ledger/verified_fact_ledger.txt"
    cnt[c] += 1
    add(r["item_id"], "minor", d, "ja_writer/revision2.md", lp, r["text"], c, "R2", extra={"reason": r.get("reason")})
    if sum(cnt.values()) >= 20: break
json.dump({"items": items, "excluded": excluded, "minor_type_counts": dict(cnt),
           "n_major": sum(i["kind"] == "major" for i in items), "n_minor": sum(i["kind"] == "minor" for i in items)},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), dict(cnt), excluded)
