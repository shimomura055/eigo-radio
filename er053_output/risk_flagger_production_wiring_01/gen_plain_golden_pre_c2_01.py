# -*- coding: utf-8 -*-
"""C2前(git commit f71dbb41 時点)の jaw.build_original_prompt(storyline, facts)(patchなし・must_fix=None既定)の出力を
注記済みbrief全件について保存する(RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2、課金API 0件)。

目的: C2で jaw.build_original_prompt から must_fix / full_ledger_text 引数と build_must_fix_block を削除した後も、
通常(must_fix=None)のR0 Prompt組立が**C2前と文字列完全一致**であることを機械証明する(DESIGN_03 15-2 #1、E5 golden比較)。
C2前のjawソースは `git show f71dbb41:er019_family_x_ja_writer_o_r1_r2_01.py` から取得する(作業ツリーの現jawは使わない)。

実行: .venv/Scripts/python.exe -X utf8 er053_output/risk_flagger_production_wiring_01/gen_plain_golden_pre_c2_01.py
出力: er053_output/risk_flagger_production_wiring_01/golden/w1_golden_plain_pre_c2_01.json
"""
import hashlib
import json
import os
import subprocess
import sys
import types

sys.dont_write_bytecode = True
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
os.chdir(REPO)

PRE_C2_COMMIT = "f71dbb41"
T = "er052_output/factlock_astra_e2e_trial_01"
SLUGS_FINAL = ["byd_recall", "central_bank_mortgage", "hormuz", "meta", "openai_copyright", "semiconductor_earnings", "small_bag",
               "space_weapons", "streaming_price"]
SLUGS_RUNS = ["byd_recall", "hormuz", "meta", "openai_copyright", "semiconductor_earnings", "small_bag", "space_weapons", "streaming_price"]


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_pre_c2_jaw():
    src = subprocess.check_output(["git", "show", f"{PRE_C2_COMMIT}:er019_family_x_ja_writer_o_r1_r2_01.py"]).decode("utf-8")
    mod = types.ModuleType("jaw_pre_c2")
    mod.__file__ = "jaw_pre_c2.py"
    exec(compile(src, "jaw_pre_c2.py", "exec"), mod.__dict__)
    return mod, sha(src)


def main():
    jaw_old, src_sha = load_pre_c2_jaw()
    import er053_family_x_factlock_ja_writer_01 as w1
    out = {"generated_for": "RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2", "pre_c2_commit": PRE_C2_COMMIT,
           "pre_c2_jaw_source_sha256": src_sha, "plain_original_prompt": {"annotation_final": {}, "new_arm_runs": {}}}

    def one(path):
        text = open(path, encoding="utf-8").read()
        storyline, facts = w1.parse_brief_md(text)
        p = jaw_old.build_original_prompt(storyline, facts)
        return {"md_path": path.replace("\\", "/"), "md_sha256": sha(text), "storyline": storyline, "plain_prompt": p, "plain_prompt_sha256": sha(p)}

    for s in SLUGS_FINAL:
        out["plain_original_prompt"]["annotation_final"][s] = one(f"{T}/annotation/final/{s}/selected_brief_factlock.md")
    for s in SLUGS_RUNS:
        out["plain_original_prompt"]["new_arm_runs"][s] = one(f"{T}/runs/{s}/new/storyline_b3/selected_brief.md")
    d = os.path.join(REPO, "er053_output", "risk_flagger_production_wiring_01", "golden")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "w1_golden_plain_pre_c2_01.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("written", p, len(out["plain_original_prompt"]["annotation_final"]), len(out["plain_original_prompt"]["new_arm_runs"]))


if __name__ == "__main__":
    main()
