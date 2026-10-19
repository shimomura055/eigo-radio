"""不具合判定テスト(PM_GOVERNANCE 11-8)の文言整合check
(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_04, 2026-10-19).

文書のみを検査する(API呼出0・Production runtime非接触)。非ブロッキングの整合検査であり、
運用Gateではない。検査:
 (1) 11-8の存在と必須語句(T1〜T3、新設/拡大、ラベル運用、維持する境界、停止根拠)
 (2) 11-8が参照する節(11-1/11-6/21/27-3/29-3/14-7)の存在
 (3) 29-3にC-14〜C-18があり、いずれも「明確化」(実質変更でない)
 (4) 委任テンプレートに修正範囲の線引き文言があり、D-1欄に書く場合も同じ語で書く旨がある
 (5) 旧い包括禁止文言(方式変更・閾値変更を一括で範囲外とする書き方)が常設文書に残っていない
 (6) sandwich-pm.mdに手順3の線引き・手順4-2の停止根拠照合・STOP節の注記がある
 (7) 14-7にHR依頼の4要素がある
 (8) USER_DECISION_REGISTERにOPEN-330とOPEN-283の個別行がある
 (9) Charter 8原則の本文(CLAUDE.md)に触れていない(check_charter_references_01.pyを別途実行)
使い方: python -I check_defect_vs_spec_rule_01.py [--root DIR] [--json-out PATH]
終了コード: 全PASSで0、1件でも失敗で1。
"""
import argparse
import json
import re
import sys
from pathlib import Path

GOV = "docs/pm/PM_GOVERNANCE.md"
TPL = "docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md"
SPM = ".claude/agents/sandwich-pm.md"
REG = "docs/pm/USER_DECISION_REGISTER_01.md"
# 常設文書(履歴であるdelegation_log・research・OPEN/DECISION台帳は対象外)
STANDING = [GOV, TPL, SPM, ".claude/agents/sonnet-worker.md", "docs/pm/PM_BRIEF.md",
            "docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md"]
OLD_BROAD = re.compile(r"方式変更.{0,3}閾値変更")


def rd(root, rel):
    return (root / rel).read_text(encoding="utf8").replace("\r\n", "\n")


def section(text, head_regex, next_regex):
    m = re.search(head_regex, text, flags=re.M)
    if not m:
        return ""
    n = re.search(next_regex, text[m.end():], flags=re.M)
    return text[m.start(): m.end() + (n.start() if n else len(text))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()
    root = Path(a.root)
    res = []

    def chk(name, ok, detail=""):
        res.append({"check": name, "ok": bool(ok), "detail": detail})

    gov = rd(root, GOV)
    s118 = section(gov, r"^### 11-8\. ", r"^## 12\. ")
    chk("11-8_exists", bool(s118))
    for key in ["不具合判定テスト", "(T1)", "(T2)", "(T3)", "受理面・閾値・方式の新設/拡大",
                "仕様候補", "不具合・是正待ち", "維持する境界", "停止根拠", "Human Review Lockの解除",
                "27-3", "技術部分", "コードを承認済み仕様へ合わせる"]:
        chk("11-8_has:" + key, key in s118)
    chk("11-8_not_new_gate", "新しいGate・STOP条件・承認境界は作らず" in s118)
    # 参照先の節の存在
    for ref, rx in [("11-1", r"^### 11-1\. "), ("11-6", r"^### 11-6\. "), ("21", r"^## 21\. "),
                    ("27-3", r"^### 27-3\. "), ("29-3", r"^### 29-3\. "), ("14-7", r"^### 14-7\. ")]:
        chk("ref_section_exists:" + ref, re.search(rx, gov, flags=re.M) is not None)
    # 29-3
    s293 = section(gov, r"^### 29-3\. ", r"^### 29-4\. ")
    for cid in ["C-14", "C-15", "C-16", "C-17", "C-18"]:
        row = [l for l in s293.split("\n") if l.startswith("| " + cid + " |")]
        chk("29-3_row:" + cid, len(row) == 1)
        chk("29-3_clarification_only:" + cid, bool(row) and row[0].rstrip().endswith("| 明確化 |"))
    # テンプレート
    tpl = rd(root, TPL)
    chk("template_line_drawing", "修正範囲の線引き" in tpl and "受理面・閾値・方式の新設/拡大" in tpl)
    tpl1 = tpl.replace(chr(10), "")
    chk("template_d1_same_wording", "D-1欄に修正範囲を" in tpl1 and "同じ語で書く" in tpl1)
    chk("template_refs_11-8", "11-8" in tpl)
    # 旧い包括禁止文言の残存0(常設文書)
    for rel in STANDING:
        p = root / rel
        if p.exists():
            hits = OLD_BROAD.findall(rd(root, rel))
            chk("old_broad_phrase_absent:" + rel, not hits, str(hits))
    # sandwich-pm
    spm = rd(root, SPM)
    s3 = section(spm, r"^3\. タスク内容", r"^4\. ")
    chk("spm_step3_line_drawing", "11-8" in s3 and "新設/拡大" in s3)
    s42 =section(spm, r"^4-2\. ", r"^5\. ")
    chk("spm_4-2_stop_basis", "停止根拠の照合" in s42 and "11-8" in s42 and "自己申告" in s42 and "新Gateではない" in s42)
    chk("spm_stop_section_note", "承認済み仕様との矛盾の是正は仕様変更ではない" in spm.replace("\n  ", ""))
    # 14-7
    s147 = section(gov, r"^### 14-7\. ", r"^## 15\. ")
    for key in ["何を疑っているか", "具体箇所", "機械判定結果", "何が確定し"]:
        chk("14-7_has:" + key, key in s147)
    # REGISTER
    reg = rd(root, REG)
    for oid in ["OPEN-330", "OPEN-283"]:
        own = [l for l in reg.split("\n") if re.match(r"^- #\d+\(.*" + oid, l)]
        chk("register_entry:" + oid, len(own) >= 1, str(len(own)))
    ok = all(r["ok"] for r in res)
    out = {"all_ok": ok, "n": len(res), "failed": [r for r in res if not r["ok"]], "results": res}
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    for r in res:
        if not r["ok"]:
            print("FAIL", r["check"], r["detail"])
    print("all_ok=%s n=%d failed=%d" % (ok, len(res), len(out["failed"])))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
