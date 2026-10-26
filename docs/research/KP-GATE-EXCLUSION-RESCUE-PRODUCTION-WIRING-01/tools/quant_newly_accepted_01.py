# -*- coding: utf-8 -*-
"""KPRW1 委任_01: 量化詞guard是正による『新規受理』の列挙(API 0)。HEAD版er105(量化詞前)と現worktreeを同一入力(実データ315表示句x全候補+敵対的)で比較。
単調性(旧受理は新も受理)と、新規受理が全て『直後が量化詞』であることを確認する。"""
import glob, importlib, importlib.util, json, os, socket, subprocess, sys, tempfile
def _b(*a, **k): raise RuntimeError("net blocked")
socket.socket.connect = _b; socket.create_connection = _b
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02", "tools"))
import prod_vs_dev_parity_01 as P
import er105_kp_fulltext_selector_01 as new
tmp = tempfile.mkdtemp(prefix="qhead_")
blob = subprocess.run(["git", "show", "HEAD:er105_kp_fulltext_selector_01.py"], cwd=ROOT, capture_output=True, check=True).stdout
spec = importlib.util.spec_from_file_location("er105_head", os.path.join(tmp, "er105_head.py"))
open(os.path.join(tmp, "er105_head.py"), "wb").write(blob)
old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
for k, v in new.IRR.items():
    for f in v: P._IRR_LEMMAS_BY_FORM.setdefault(f, set()).add(k)
displays, pairs = P._real_displays()
cand = P._candidate_keys(new, displays)
rows = {"viol_monotonic": [], "newly": [], "n": len(cand)}
for d, k in cand:
    o = old.find_inflection_window(k, d) is not None; n = new.find_inflection_window(k, d) is not None
    if o and not n: rows["viol_monotonic"].append([d, k])
    if n and not o: rows["newly"].append([d, k])
rows["newly_not_quant_next"] = [r for r in rows["newly"] if not any(t.lower() in new._QUANT_DET for t in new._norm_tokens(r[1]))]
json.dump(rows, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(rows["n"], len(rows["viol_monotonic"]), len(rows["newly"]), len(rows["newly_not_quant_next"]), rows["newly"][:10])
