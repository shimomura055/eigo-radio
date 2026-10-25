# FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16 T1翻訳の確認(DEV。Production module er003_kp_source_sentence_ja_01 を呼ぶだけの検証script)。
# Trial-03/04の3作品9文(INPUT_04.json)を T1(引用英文のみ入力)で訳し、既存の03d由来訳と並べて PART1_T1_CHECK_01.md を作る。
# 使い方: py run_t1_check_01.py   (有料: 3 call、gpt-6-luna。約0.2円)
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import er003_kp_source_sentence_ja_01 as ja  # noqa: E402

inp = json.load(open(os.path.join(BASE, "INPUT_04.json"), encoding="utf-8"))
out, total, calls = {}, 0.0, []
for work, rows in inp.items():
    sents = [r["sentence"] for r in rows]
    res = ja.generate_translations(sents)
    a = res["audit"]
    total += a["total_cost_jpy"] or 0
    calls.append({"work": work, "model": a["model"], "prompt_sha256": a["prompt_sha256"], "input_sha256": a["input_sha256"],
                  "response_ids": a["response_ids"], "retried": a["retried_for_parse"], "cost_jpy": a["total_cost_jpy"],
                  "elapsed_sec": [c["elapsed_sec"] for c in a["calls"]]})
    out[work] = [{"sentence": s, "existing_ja": r["sentence_ja"], "t1_ja": x["source_sentence_ja"]} for s, r, x in zip(sents, rows, res["items"])]
json.dump({"calls": calls, "total_cost_jpy": round(total, 4), "pairs": out}, open(os.path.join(BASE, "part1_t1_check_01_raw.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("calls", len(calls), "total_cost_jpy", round(total, 4))
for work, rs in out.items():
    for r in rs:
        print(work, "|", r["sentence"], "\n  existing:", r["existing_ja"], "\n  T1      :", r["t1_ja"])
