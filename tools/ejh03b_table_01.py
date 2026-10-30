# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03B: 公開dir x level x part の英日連動/Vocabulary音声の対応表(API 0)。使い方: python tools/ejh03b_table_01.py <公開dir>... [--md]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = ("preview", "comment", "story", "oneline")


def rows(pub):
    d = ROOT / pub / "enduser" / "data"
    art = json.loads((d / "article.json").read_text(encoding="utf-8"))
    out, voc = [], []
    for lv, L in art["levels"].items():
        sync = json.loads((d / f"sync_{lv}.json").read_text(encoding="utf-8"))
        sent_by_part = {}
        for s in sync["sentences"]:
            sent_by_part.setdefault(s["sid"].rsplit("-", 1)[0], []).append(s["sid"])
        for p in L["parts"]:
            if p["kind"] not in KINDS:
                continue
            sids = sent_by_part.get(p["key"], [])
            al = p.get("ja_align")
            linked = 0
            how = {}
            if al:
                for g in al:
                    if g.get("ja") is not None:
                        linked += len(g["sids"])
                        how[g.get("how", "v1")] = how.get(g.get("how", "v1"), 0) + len(g["sids"])
            out.append(dict(dir=Path(pub).name, level=lv, part=p["key"], kind=p["kind"], ja_source=p.get("ja_source") or ("na_ja_only" if p.get("ja") is None and False else p.get("ja_source")),
                            has_ja=bool(p.get("ja")), sentences=len(sids), linked=linked, how=how))
        n = len(L.get("vocab", []))
        a = sum(1 for v in L.get("vocab", []) if v.get("audio"))
        voc.append(dict(dir=Path(pub).name, level=lv, items=n, audio=a))
    return out, voc


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    allp, allv = [], []
    for pub in args:
        r, v = rows(pub)
        allp += r
        allv += v
    if "--md" in sys.argv:
        print("| dir | level | part | kind | 訳の出所 | 英文数 | 連動 | 連動率 | how |")
        print("|---|---|---|---|---|---|---|---|---|")
        for r in allp:
            rate = f"{100 * r['linked'] / r['sentences']:.1f}%" if r["sentences"] and r["has_ja"] else "-"
            print(f"| {r['dir']} | {r['level']} | {r['part']} | {r['kind']} | {r['ja_source'] or '訳なし(英語のみ)'} | {r['sentences']} | {r['linked']} | {rate} | {r['how']} |")
        print()
        print("| dir | level | Vocabulary掲載 | 音声あり |")
        print("|---|---|---|---|")
        for v in allv:
            print(f"| {v['dir']} | {v['level']} | {v['items']} | {v['audio']} |")
    else:
        print(json.dumps(dict(parts=allp, vocab=allv), ensure_ascii=False, indent=1))
