# -*- coding: utf-8 -*-
"""委任_09: build_prompts_01.py のロジックを一切変えずに、hormuz・streaming_price だけ B3 v2 (storyline_b3_v2) から再構築する薄いラッパ。
v1プロンプトは <slug>__<A|B>_v1.md に退避、v2を従来名で出力。PROMPT_SHA256.json / AMBIGUOUS_FACT_MAP.json は該当テーマのみ更新(v1の値は *_v1 キーに保存)。"""
import json, os, re, shutil, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "build_prompts_01.py"), encoding="utf-8").read()
SL2 = ["hormuz", "streaming_price"]
# 退避
for s in SL2:
    for a in "AB":
        p = os.path.join(HERE, "prompts", f"{s}__{a}.md"); q = os.path.join(HERE, "prompts", f"{s}__{a}_v1.md")
        if not os.path.exists(q): shutil.copyfile(p, q)
old_sha = json.load(open(os.path.join(HERE, "PROMPT_SHA256.json"), encoding="utf-8"))
old_amb = json.load(open(os.path.join(HERE, "AMBIGUOUS_FACT_MAP.json"), encoding="utf-8"))
src = re.sub(r"SLUGS = \[.*?\]\n", f"SLUGS = {SL2!r}\n", src, count=1, flags=re.S)
assert '"storyline_b3"' in src
src = src.replace('"storyline_b3"', '"storyline_b3_v2"')
# 出力先を一時ファイルへ(本体は後で統合更新)
src = src.replace('"PROMPT_SHA256.json"', '"PROMPT_SHA256_v2_tmp.json"').replace('"AMBIGUOUS_FACT_MAP.json"', '"AMBIGUOUS_FACT_MAP_v2_tmp.json"')
exec(compile(src, "build_prompts_01(v2)", "exec"), {"__file__": os.path.join(HERE, "build_prompts_01.py"), "__name__": "__main__"})
new_sha = json.load(open(os.path.join(HERE, "PROMPT_SHA256_v2_tmp.json"), encoding="utf-8"))
new_amb = json.load(open(os.path.join(HERE, "AMBIGUOUS_FACT_MAP_v2_tmp.json"), encoding="utf-8"))
for s in SL2:
    for a in "AB":
        fn = f"{s}__{a}.md"
        old_sha["prompts"][f"{s}__{a}_v1.md"] = old_sha["prompts"][fn]
        old_sha["prompts"][fn] = new_sha["prompts"][fn]
    row = [r for r in new_sha["themes"] if r["slug"] == s][0]
    for i, r in enumerate(old_sha["themes"]):
        if r["slug"] == s:
            old_sha["themes"][i] = dict(row, b3_version="v2", v1_brief_sha256=r["brief_sha256"])
    old_amb[s + "_v1"] = old_amb[s]; old_amb[s] = new_amb[s]
old_sha["ab_all_identical"] = all(r["ab_identical_after_normalization"] for r in old_sha["themes"])
old_sha["note_委任_09"] = "hormuz・streaming_price はB3 v2から再構築(v1は *_v1.md / *_v1 キー)"
json.dump(old_sha, open(os.path.join(HERE, "PROMPT_SHA256.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(old_amb, open(os.path.join(HERE, "AMBIGUOUS_FACT_MAP.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
os.remove(os.path.join(HERE, "PROMPT_SHA256_v2_tmp.json")); os.remove(os.path.join(HERE, "AMBIGUOUS_FACT_MAP_v2_tmp.json"))
print("done", old_sha["ab_all_identical"])
