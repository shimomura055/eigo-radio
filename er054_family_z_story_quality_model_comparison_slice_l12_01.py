# -*- coding: utf-8 -*-
"""比較Trial委任_02: L12『夢十夜』全体から『第一夜』のみを決定論で切り出す(LLM不使用・Trial専用)。
全体は text_plain_full.txt に残し、評価対象 text_plain.txt は第一夜のみ。範囲根拠は slice_manifest.json。"""
import hashlib, json, os, re
ROOT = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ROOT, "er054_output", "family_z_story_pool_trial_01", "sources", "L12")
full_p = os.path.join(D, "text_plain_full.txt")
src_p = os.path.join(D, "text_plain.txt")
if not os.path.exists(full_p):  # 初回のみ全体を退避(2回目以降は全体から切る)
    os.replace(src_p, full_p)
t = open(full_p, encoding="utf-8").read()
heads = [(m.group(0), m.start()) for m in re.finditer(r"^第[一二三四五六七八九十]夜$", t, re.M)]
assert heads[0][0] == "第一夜" and heads[1][0] == "第二夜", heads[:2]
s, e = heads[0][1], heads[1][1]
part = t[s:e].strip()
open(src_p, "w", encoding="utf-8", newline="\n").write(part)
man = {"work_id": "L12", "scope": "第一夜のみ", "method": "regex ^第[一二三四五六七八九十]夜$ の見出し行で分割し、第一夜見出し行〜第二夜見出し直前までを切出し",
       "headings_found": [{"heading": h, "char_offset": o} for h, o in heads],
       "start_heading": "第一夜", "start_offset": s, "end_heading_exclusive": "第二夜", "end_offset": e,
       "full_chars": len(t), "full_chars_no_ws": len(re.sub(r"\s", "", t)), "full_sha256": hashlib.sha256(t.encode("utf-8")).hexdigest(),
       "part_chars": len(part), "part_chars_no_ws": len(re.sub(r"\s", "", part)), "part_sha256": hashlib.sha256(part.encode("utf-8")).hexdigest(),
       "first_line": part.splitlines()[0], "last_100_chars": part[-100:], "ten_nights_count": len(heads)}
json.dump(man, open(os.path.join(D, "slice_manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps({k: man[k] for k in ("part_chars", "part_chars_no_ws", "start_offset", "end_offset", "ten_nights_count", "last_100_chars")}, ensure_ascii=False))
