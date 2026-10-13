# -*- coding: utf-8 -*-
"""委任_03 OF-Y7: 過去のCANONICALIZATION_INVALID attemptの正確な内訳(API 0円)。"""
import glob, json, os, collections
found = {}
def walk(o, path):
    if isinstance(o, dict):
        if o.get("status") == "CANONICALIZATION_INVALID" and o.get("item_reasons"):
            key = json.dumps(o["item_reasons"], sort_keys=True, ensure_ascii=False)
            found.setdefault(key, []).append(path)
        for v in o.values():
            walk(v, path)
    elif isinstance(o, list):
        for v in o:
            walk(v, path)
for p in glob.glob("er0*_output/**/*.json", recursive=True):
    if os.path.getsize(p) > 20_000_000: continue
    try:
        raw = open(p, encoding="utf-8").read()
    except Exception: continue
    if "CANONICALIZATION_INVALID" not in raw: continue
    try: walk(json.loads(raw), p)
    except Exception: pass
lines = ["# invalid_census_03 (OF-Y7、API 0円)", "", f"ユニークなINVALID理由パターン(item_reasons単位): {len(found)}件。", "",
         "| # | 出現ファイル数 | 理由(要約) | 代表ファイル |", "|---|---|---|---|"]
tot_files = set()
for i, (k, ps) in enumerate(sorted(found.items(), key=lambda kv: -len(kv[1])), 1):
    tot_files.update(ps)
    lines.append(f"| {i} | {len(set(ps))} | {k[:260].replace('|','/')} | {ps[0]} |")
lines += ["", f"出現ファイル総数(ユニーク): {len(tot_files)}"]
open("er071_output/m2p0_n01_production_wiring_01/completion_03/invalid_census_03.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(len(found), len(tot_files))
