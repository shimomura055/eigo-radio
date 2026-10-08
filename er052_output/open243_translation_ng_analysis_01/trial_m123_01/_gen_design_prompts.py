# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C
import difflib
a = C.adv_gen; v = C.vfl01
out = []
out.append("## P1. 要約 In one line プロンプト(M1)\n")
out.append("### 変更前(FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE、全文。{article_text}を差し込む)\n```text\n" + a.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE + "\n```\n")
out.append("### 変更後(OPEN243_M1、FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1、全文。再生成時は末尾に build_must_fix_block(既存関数、無変更)の出力を追加)\n```text\n" + a.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1 + "\n```\n")
out.append("### build_must_fix_block の出力例(既存、無変更。再生成時のみ末尾に付く)\n```text\n" + a.build_must_fix_block([{"fact_id":"<fact_id>","claim_in_article":"<要約の該当文>","issue":"<指摘>","explanation":"<説明>"}]) + "\n```\n")
out.append("### 差分(unified diff)\n```diff\n" + "\n".join(difflib.unified_diff(a.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE.splitlines(), a.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1.splitlines(), "before", "after", lineterm="")) + "\n```\n")
out.append("## P2. EN deviation check プロンプト(M2)\n")
out.append("### 変更前(DEVIATION_PROMPT_TEMPLATE、全文)\n```text\n" + v.DEVIATION_PROMPT_TEMPLATE + "\n```\n")
new = v.apply_open243_m2_to_prompt_template(v.DEVIATION_PROMPT_TEMPLATE)
out.append("### 変更後(OPEN243_M2、全文)\n```text\n" + new + "\n```\n")
out.append("### 差分(unified diff)\n```diff\n" + "\n".join(difflib.unified_diff(v.DEVIATION_PROMPT_TEMPLATE.splitlines(), new.splitlines(), "before", "after", lineterm="")) + "\n```\n")
out.append("### origin 判定の追加指示 変更前(ORIGIN_INSTRUCTION_TEMPLATE、全文)\n```text\n" + v.ORIGIN_INSTRUCTION_TEMPLATE + "\n```\n")
out.append("### origin 判定の追加指示 変更後(ORIGIN_INSTRUCTION_TEMPLATE_M2、全文)\n```text\n" + v.ORIGIN_INSTRUCTION_TEMPLATE_M2 + "\n```\n")
open(os.path.join(C.TRIAL, "_prompts_before_after.md"), "w", encoding="utf-8").write("\n".join(out))
print("ok")
