# -*- coding: utf-8 -*-
"""evidence_01.json -> 表(markdown断片)を標準出力へ。read-only。"""
import json, sys
D = "docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01"
S = json.load(open(f"{D}/evidence_01.json", encoding="utf-8"))
R = {r["run"]: r for r in S["runs"]}
print("### E-1 clipごと(path=normal)\n")
print("| level | clip | attempt数 | mode列 | verified列 | ASR判定 | ctx style sha256(先頭12) | instruction_type |")
print("|---|---|---|---|---|---|---|---|")
for lv in ("a2", "b1b"):
    for cid, c in R["run_fzcw_e1_01"]["levels"][lv]["clips"].items():
        a = c["attempts"]
        print(f"| {lv} | {cid} | {len(a)} | {'/'.join(x['mode'] for x in a)} | {'/'.join(str(x['verified']) for x in a)} | "
              f"{'/'.join(','.join(str(s) for s in x['asr_states']) for x in a)} | {(c['ctx_style_sha256'] or '')[:12]} | {a[0]['instruction_type']} |")
print("\n### E-2〜E-6 attempt表\n")
print("| run | case | level | n | mode | effective_mode | verified | ASR判定 | 開始 | 終了 | final_ng_epoch有 |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for run, r in R.items():
    if run == "run_fzcw_e1_01":
        continue
    lv = "b1b" if "b1b" in run else "a2"
    c = r["levels"][lv]["clips"]["full_story_part1_c2"]
    for a in c["attempts"]:
        print(f"| {run} | {run.split('_')[2].upper().replace('E','E-')} | {lv} | {a['n']} | {a['mode']} | {a['effective_mode']} | {a['verified']} | "
              f"{','.join(str(s) for s in a['asr_states'])} | {a['started_at']} | {a['finished_at']} | {a.get('final_ng_epoch') is not None} |")
