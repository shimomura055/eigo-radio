# -*- coding: utf-8 -*-
"""段階2 棚卸し(read-only、費用0)。60 run を 完了/再実行要/未開始 に分類。"""
import json, os, sys
B = "er052_output/open233_b3_trial_01"; R = f"{B}/runs"
SL = ["meta", "hormuz", "space_weapons"]; VS = ["V0", "V1", "V3", "V5", "V6"]

def bad_files(d):
    bad = []
    for r, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            try:
                if os.path.getsize(p) == 0:
                    bad.append((p, "zero")); continue
                if f.endswith((".json", ".jsonl")):
                    raw = open(p, "rb").read()
                    if b"\x00" in raw: bad.append((p, "NUL")); continue
                    txt = raw.decode("utf-8")
                    if f.endswith(".json"): json.loads(txt)
                    else:
                        for ln in txt.splitlines():
                            if ln.strip(): json.loads(ln)
            except Exception as e:
                bad.append((p, "parse:" + type(e).__name__))
    return bad

rows = []
for v in VS:
    for s in SL:
        for i in (1, 2, 3, 4):
            base = f"{R}/{s}/nb/{v}/b{i}"; w = f"{base}/w1"
            brief = os.path.exists(f"{base}/storyline_b3/selected_brief.md")
            art = os.path.exists(f"{w}/b1b/article.md")
            rev = os.path.exists(f"{w}/ja_writer/revision2.md")
            cost = None
            try: cost = json.load(open(f"{w}/cost.json", encoding="utf-8"))
            except Exception: pass
            bad = bad_files(w) if os.path.isdir(w) else []
            if not brief: st = "NO_BRIEF"
            elif not os.path.isdir(w): st = "NOT_STARTED"
            elif art and rev and cost is not None and not bad: st = "COMPLETE"
            else: st = "RERUN"
            rows.append(dict(slug=s, v=v, b=i, brief=brief, w1=os.path.isdir(w), rev2=rev, article=art, cost_ok=cost is not None, bad=[f"{p}:{k}" for p, k in bad], status=st))
json.dump(rows, open(sys.argv[1] if len(sys.argv) > 1 else "inventory.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(r["status"] for r in rows))
for r in rows:
    if r["status"] != "COMPLETE": print(r["status"], r["v"], r["slug"], f"b{r['b']}", "brief" if r["brief"] else "-", "rev2" if r["rev2"] else "-", "art" if r["article"] else "-", "cost" if r["cost_ok"] else "-", len(r["bad"]))
