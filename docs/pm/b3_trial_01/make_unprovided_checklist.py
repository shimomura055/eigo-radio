#!/usr/bin/env python3
"""未提示事項チェックリスト(M6)を台帳から決定論で作成。対象=factの本文行とnumeric_value行(numeric_scope)に
「未提示/不明/示されていない/確認できない/明記されていない」とある事項のみ。notes_for_writer(「〜とは書かない」型)は対象外。
usage: python make_unprovided_checklist.py   -> docs/pm/b3_trial_01/unprovided_checklist_<slug>.md"""
import re, os
LED = "er052_output/open233_polysemy_trial_02/ledgers/%s/control/research_ledger/verified_fact_ledger.txt"
KW = ("未提示", "不明", "示されていない", "確認できない", "明記されていない", "示されなかった")
for slug in ("meta", "hormuz", "space_weapons"):
    items, cur = [], None
    for ln in open(LED % slug, encoding="utf-8").read().splitlines():
        m = re.match(r"^\[[A-Z_]+\]\s+([A-Z]+-\d+):\s*(.*)$", ln)
        if m:
            cur = m.group(1)
            if any(k in m.group(2) for k in KW):
                items.append((cur, "本文", m.group(2)))
            continue
        t = ln.strip()
        if cur and t.startswith("numeric_value:") and any(k in t for k in KW):
            items.append((cur, "numeric_scope", t))
    out = ["# 未提示事項チェックリスト: %s (決定論生成: make_unprovided_checklist.py)" % slug, "",
           "対象: fact本文/numeric_scopeに「%s」とある事項のみ。notes_for_writerの「〜とは書かない」型は対象外。" % "/".join(KW),
           "brief_review(別インスタンス)は各項目について、briefが当該事項を「示されていない/不明/未提示」等で明記しているか(stated: true/false)を記録する。", ""]
    for i, (fid, where, txt) in enumerate(items, 1):
        out.append("%d. [%s] (%s) %s" % (i, fid, where, txt))
    if not items:
        out.append("(該当事項なし -> unprovided_checklist_hits は空配列)")
    p = "docs/pm/b3_trial_01/unprovided_checklist_%s.md" % slug
    open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print(slug, len(items))
