# -*- coding: utf-8 -*-
"""ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01 委任_03 / ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_05: 全公開dir x level x part の最終対応表(API 0)。
列: 訳の出所(承認済み / 生成 / 日本語パートのため対象外 / 不成立[英語のみ=要是正]) / 英文数 / 連動文数 / 連動率 / asset版 / Vocabulary音声件数。
使い方: python tools/ech03_table_final_01.py <公開dir>... > table_final.md   (不成立が1件でもあれば終了コード3)"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = ("preview", "comment", "story", "oneline")
CJK = re.compile(r"[぀-ヿ一-鿿]")


def rows(pub):
    d = ROOT / pub / "enduser"
    art = json.loads((d / "data" / "article.json").read_text(encoding="utf-8"))
    bi = json.loads((d / "build_info.json").read_text(encoding="utf-8"))
    out, voc = [], []
    for lv, L in art["levels"].items():
        for p in L["parts"]:
            if p["kind"] not in KINDS:
                continue
            paras = p.get("paragraphs") or []
            n = len(paras)
            txt = " ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in paras)
            linked = sum(len(g["sids"]) for g in (p.get("ja_align") or []) if g.get("ja") is not None)
            if CJK.search(txt):
                src = "日本語パートのため対象外"
            elif p.get("ja"):
                src = {"generated": "生成訳"}.get(p.get("ja_source"), "承認済み訳" if str(p.get("ja_source", "")).startswith("approved") else f"?{p.get('ja_source')}")
            else:
                src = "不成立(英語のみ)"
            out.append(dict(dir=Path(pub).name, level=lv, part=p["key"], kind=p["kind"], src=src, n=n, linked=linked))
        vv = L.get("vocab", [])
        voc.append(dict(dir=Path(pub).name, level=lv, items=len(vv), audio=sum(1 for v in vv if v.get("audio"))))
    return out, voc, bi.get("asset_build")


if __name__ == "__main__":
    P, V, A, bad = [], [], {}, 0
    for pub in sys.argv[1:]:
        r, v, a = rows(pub)
        P += r
        V += v
        A[Path(pub).name] = a
    print("| dir | level | part | kind | 訳の出所 | 英文数 | 連動文数 | 連動率 | asset版 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in P:
        tr = r["src"] in ("承認済み訳", "生成訳")
        bad += r["src"].startswith("不成立")
        rate = f"{100 * r['linked'] / r['n']:.0f}%" if tr and r["n"] else "-"
        print(f"| {r['dir']} | {r['level']} | {r['part']} | {r['kind']} | {r['src']} | {r['n']} | {r['linked'] if tr else '-'} | {rate} | {A[r['dir']]} |")
    print()
    print("| dir | level | 連動率(訳あり英文の合計) | Vocabulary掲載 | 音声あり | asset版 |")
    print("|---|---|---|---|---|---|")
    for v in V:
        ps = [r for r in P if r["dir"] == v["dir"] and r["level"] == v["level"] and r["src"] in ("承認済み訳", "生成訳")]
        n, l = sum(r["n"] for r in ps), sum(r["linked"] for r in ps)
        print(f"| {v['dir']} | {v['level']} | {l}/{n} ({100 * l / n:.1f}%) | {v['items']} | {v['audio']} | {A[v['dir']]} |" if n else f"| {v['dir']} | {v['level']} | - | {v['items']} | {v['audio']} | {A[v['dir']]} |")
    print()
    cnt = {}
    for r in P:
        cnt[r["src"]] = cnt.get(r["src"], 0) + 1
    print("集計(part数): " + " / ".join(f"{k}={c}" for k, c in sorted(cnt.items())) + f" / 不成立={bad}")
    sys.exit(3 if bad else 0)
