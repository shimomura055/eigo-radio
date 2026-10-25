# -*- coding: utf-8 -*-
"""FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_06 C-3: COMPARISON_05.md の集計表示不具合を保存済みartifactから決定論で修正して再生成する(API 0)。
 (1) 『rerun=None』= m1_result.json のキー名誤り(正: b3_rerun)による表示不具合。実データの b3_rerun と 1回目の違反理由/欄を表示する。
 (2) 『EN_Std/EN_Adv 数値トークン』= 単位なし数字『3』が『3D』に誤一致していた表示を、修正済みen_tokensで再計算。
 実行: py er115_fx_numeric_r5_comparison_fix_01.py  (COMPARISON_05.md を in-place 更新。修正前の行は変更記録に残す)"""
import json
import os
import re
import sys

import er115_fx_numeric_r5_score_01 as S

ROOT = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(ROOT, "docs", "research", "FX-CORE-NUMERIC-RETENTION-TRIAL-01", "COMPARISON_05.md")
HDR = re.compile(r"^### .*\(`(er115_output[^`]+)`\)")
NOTE_MARK = "<!-- 委任_06 C-3 修正 -->"


def main():
    lines = open(MD, encoding="utf-8").read().split("\n")
    out, cur, changes = [], None, []
    for ln in lines:
        m = HDR.match(ln)
        if m:
            cur = os.path.join(ROOT, m.group(1).replace("\\", os.sep))
        elif ln.startswith("### ") or ln.startswith("## "):
            cur = None
        if cur and "rerun=None" in ln and os.path.exists(os.path.join(cur, "m1_result.json")):
            m1 = json.load(open(os.path.join(cur, "m1_result.json"), encoding="utf-8"))
            att1 = m1["attempts"][0]
            extra = f"b3_rerun={m1['b3_rerun']}"
            if m1["b3_rerun"]:
                extra += (f"(1回目の欄={att1.get('field_items')} 違反={[(v['surface'], v['reason']) for v in att1['violations']]})")
            new = ln.replace("rerun=None", extra)
            changes.append(("rerun", os.path.relpath(cur, ROOT), ln, new))
            ln = new
        mt = re.match(r"^- (EN_Std|EN_Adv): 数値トークン=(.*)$", ln)
        if cur and mt:
            f = "a2/article.md" if mt.group(1) == "EN_Std" else "b1b/article.md"
            p = os.path.join(cur, f)
            if os.path.exists(p):
                toks = S.en_tokens(open(p, encoding="utf-8").read())
                new = f"- {mt.group(1)}: 数値トークン={toks}"
                if new != ln:
                    changes.append(("en_tokens", os.path.relpath(cur, ROOT), ln, new))
                    ln = new
        out.append(ln)
    text = "\n".join(out)
    if NOTE_MARK not in text:
        rec = [NOTE_MARK, "> 委任_06 C-3(Opus条件C)で表示不具合2件を修正して再生成(`er115_fx_numeric_r5_comparison_fix_01.py`、API 0): (1) 欄行の『rerun=None』はm1_result.jsonのキー名誤りによる表示不具合で、実データは`b3_rerun`(再実行あり=True、1回目の欄と違反理由を併記)。"
               " (2) EN数値トークンの単位なし『3』は『3D』への誤一致で、先読みで除外(修正前=ig r5b1 EN_Std ['3'] → 修正後 []。判定には使っておらず表示のみ)。", ""]
        text = text.replace("\n", "\n" + "\n".join(rec) + "\n", 1) if False else "\n".join(text.split("\n")[:1] + [""] + rec + text.split("\n")[1:])
    open(MD, "w", encoding="utf-8", newline="\n").write(text)
    print(json.dumps([{"kind": k, "dir": d, "before": b[:120], "after": a[:200]} for k, d, b, a in changes], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
