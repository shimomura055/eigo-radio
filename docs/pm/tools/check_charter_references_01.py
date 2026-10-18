"""Charter 8原則 参照整合check (PM-COMMON-CHARTER-REVISION-02, 2026-10-18).

文書のみを検査する(API呼出0・Production runtime非接触)。
検査: (1) CLAUDE.mdのCharter節がユーザー指示原文(USER.md)の8原則本文と逐語一致
(2) 優先順位文の存在 (3) 旧Charter要約文(【8原則】等)の残存なし
(4) Agent定義4本/PM_BRIEF/委任テンプレートがCharter正本(CLAUDE.md)と29節を参照し、8原則見出しを複製していない
(5) PM_GOVERNANCE 29節の存在。
"""
import argparse, json, re, sys
from pathlib import Path

USER = "docs/pm/delegation_log/2026-10-18_PM-COMMON-CHARTER-REVISION-02_USER.md"
REF_FILES = [
    ".claude/agents/sandwich-pm.md", ".claude/agents/sonnet-worker.md",
    ".claude/agents/opus-consultant.md", ".claude/agents/haiku-worker.md",
    "docs/pm/PM_BRIEF.md", "docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md",
]
PRIORITY = "品質（Q）＞納期・速度（D）＞量産単価（C）≫開発費用"
OLD_PATTERNS = [r"【8原則】", r"^1 必要十分な品質で止める。過剰な磨き込みはしない", r"^6 人間には重要な判断だけを求める。$"]


def rd(root, rel):
    return (root / rel).read_text(encoding="utf8").replace("\r\n", "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root = Path(a.root)
    res = []

    def chk(name, ok, detail=""):
        res.append({"check": name, "ok": bool(ok), "detail": detail})

    user = rd(root, USER)
    s = user.index("#### 1."); e = user.index("### 実装・文書整備")
    principles = user[s:e].strip()
    blocks = re.split(r"^#### ", principles, flags=re.M)[1:]
    chk("user_principles_count_8", len(blocks) == 8, str(len(blocks)))
    cl = rd(root, "CLAUDE.md")
    b = cl.index("<!-- CHARTER_BEGIN -->"); en = cl.index("<!-- CHARTER_END -->")
    charter = cl[b:en]
    chk("priority_sentence", PRIORITY in charter)
    chk("quality_no_unilateral", "AIが独断で引き上げたり引き下げたりしてはならない" in charter)
    for blk in blocks:
        title, _, body = blk.partition("\n")
        body = body.strip()
        chk("verbatim_title:" + title[:12], ("**" + title.strip() + "**") in charter)
        chk("verbatim_body:" + title[:12], body in charter)
    for pat in OLD_PATTERNS:
        chk("old_charter_absent:" + pat[:20], not re.search(pat, charter, flags=re.M))
    heads = [blk.partition("\n")[0].strip() for blk in blocks]
    for rel in REF_FILES:
        t = rd(root, rel)
        chk("ref_charter:" + rel, "CLAUDE.md" in t and "共通Charter" in t and "29節" in t)
        dup = [h for h in heads if ("**" + h + "**") in t]
        chk("no_principle_copy:" + rel, not dup, ",".join(dup))
    gov = rd(root, "docs/pm/PM_GOVERNANCE.md")
    chk("gov_section_29", re.search(r"^## 29\. 共通Charter 8原則", gov, flags=re.M) is not None)
    chk("gov_table_substantive_zero", "実質変更=**0件**" in gov)
    out = {"all_ok": all(r["ok"] for r in res), "n": len(res), "failed": [r for r in res if not r["ok"]], "results": res}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    print("all_ok=%s n=%d failed=%d" % (out["all_ok"], len(res), len(out["failed"])))
    for f in out["failed"]:
        print("FAIL", f)
    return 0 if out["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
