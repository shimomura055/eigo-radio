# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_02: 英語文<->日本語訳の対応づけ(er135_enduser_align_01)のゴールド評価(API 0)。

ゴールド = docs/research/ENDUSER-EN-JA-LINKED-HIGHLIGHT-01/gold/gold_{moon,fee,sur}.txt
  (既公開3記事 X月/Y再配達/Y姓 x Std/Adv=50段落・EN 265文・218群。原文を読んで人手で作成=アルゴリズム出力を見ずに作成)
埋め込み = gold/ja_align_embed_v1.jsonl(text-embedding-3-large 1024次元の実埋め込みを凍結。評価はAPI 0)
文章 = user_test/<公開dir>/enduser/data/article.json の paragraphs と ja(ja_alignが付いても本文は不変)

評価:
  - emit群の誤対応: 採用(ja非null)した群(S,R)が、あるゴールド群(S_g,R_g)について S<=S_g かつ R<=R_g を満たさなければ誤対応
  - 合成ずらし: ゴールドの隣接2群の境界でEN文を1つ隣へ移した候補(両方向)をscreen()に通し、採用されたらNG(棄却率100%が合格)
  - coverage: 採用群に含まれるEN文数 / 全EN文数(Std/Adv別・記事別)
  - 段落取り違え(別段落のJAと組合せ): 採用された群数
使い方: .venv\\Scripts\\python.exe tools\\ejh02_gold_eval_01.py [--json out.json]
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import er135_enduser_align_01 as AL  # noqa: E402

GD = ROOT / "docs" / "research" / "ENDUSER-EN-JA-LINKED-HIGHLIGHT-01" / "gold"
ARTS = {"moon": "user_test/family_x_moon_shrinking_reselect_01", "fee": "user_test/family_y_production_redelivery_fee_03",
        "sur": "user_test/family_y_production_surname_choice_01"}


def load_gold(pattern: str = "gold_[mfs][oeu][oer]*.txt") -> dict:
    """pattern既定=パラメータ決定に使った3記事(gold_moon/fee/sur)。未見データは gold_unseen_*.txt"""
    G = {}
    files = [str(GD / n) for n in ("gold_moon.txt", "gold_fee.txt", "gold_sur.txt")] if pattern.startswith("gold_[mfs]") else sorted(glob.glob(str(GD / pattern)))
    for f in files:
        for line in open(f, encoding="utf-8"):
            if line.startswith("#") or "|" not in line:
                continue
            head, spec = line.split("|")
            art, lv, key, pi = head.split()
            key = key if art in ARTS else f"{art}|{lv}|{key}|{pi}"
            pi = pi if art in ARTS else 0
            groups = []
            for tok in spec.split():
                e, j = tok.split(":")

                def rng(s):
                    a = s.split("-")
                    return list(range(int(a[0]), int(a[-1]) + 1))
                groups.append((rng(e), [] if j == "x" else rng(j)))
            G[(art, lv, key, int(pi))] = groups
    return G


def load_unseen_texts() -> dict:
    """未見データ(既存X記事 Paycheck Personality / manga byUs。パラメータ決定に不使用)。キー=(art, lv, 'art|lv|part|n', 0)"""
    raw = json.load(open(GD / "unseen_texts.json", encoding="utf-8"))
    T = {}
    for k, v in raw.items():
        art, lv, part, n = k.split("|")
        T[(art, lv, k, 0)] = (v["en"], v["ja"])
    return T


def load_texts() -> dict:
    T = {}
    for art, d in ARTS.items():
        a = json.load(open(ROOT / d / "enduser" / "data" / "article.json", encoding="utf-8"))
        for lv, L in a["levels"].items():
            for p in L["parts"]:
                if not p.get("ja"):
                    continue
                for pi, (pa, ja) in enumerate(zip(p["paragraphs"], p["ja"])):
                    T[(art, lv, p["key"], pi)] = ([s["text"] for s in pa], [ja[x:y].strip() for x, y in AL.split_ja(ja)])
    return T


def _store():
    td = tempfile.mkdtemp()
    shutil.copy(GD / AL.EMBED_CACHE_NAME, Path(td) / AL.EMBED_CACHE_NAME)
    return AL.EmbedStore(td, allow_api=False), td


def _gold_map(gr: list) -> dict:
    m = {}
    for es, js in gr:
        for e in es:
            m[e] = set(js)
    return m


def evaluate(params: dict | None = None, unseen: bool = False, arts: tuple | None = None) -> dict:
    P = dict(params or AL.PARAMS)
    if unseen:
        G, T = load_gold("gold_unseen_*.txt"), load_unseen_texts()
    else:
        G, T = load_gold(), load_texts()
    if arts:
        G = {k: v for k, v in G.items() if k[0] in arts}
    st, td = _store()
    try:
        tot = {}
        wrong, syn_total, syn_acc, ngroups = [], 0, 0, 0
        per_art, per_lv = {}, {}
        for k, gr in G.items():
            en, ja = T[k]
            gm = _gold_map(gr)
            res = AL.align_paragraph(en, ja, st, P)
            for g in res:
                n = len(g["en"])
                for d, key in ((per_art, k[0]), (per_lv, k[1])):
                    c = d.setdefault(key, {"total": 0, "linked": 0, "groups": 0})
                    c["total"] += n
                if g["ja"] is not None:
                    ngroups += 1
                    R = set(range(*g["ja"]))
                    for d, key in ((per_art, k[0]), (per_lv, k[1])):
                        d[key]["linked"] += n
                        d[key]["groups"] += 1
                    if not all(R <= gm[e] for e in g["en"]):
                        wrong.append({"key": list(k), "en": g["en"], "ja": list(g["ja"]), "why": g["why"]})
            # 合成: 隣接2群の境界でEN文を1つ移した候補
            px = AL._Para(en, ja, st, P)
            for t in range(len(gr) - 1):
                (e1, j1), (e2, j2) = gr[t], gr[t + 1]
                if not j1 or not j2:
                    continue
                for ens, jas in (([e1[-1]] + e2, j2), (e1 + [e2[0]], j1)):
                    i0, i1, a, b = ens[0], ens[-1] + 1, jas[0], jas[-1] + 1
                    R = set(range(a, b))
                    if all(R <= gm[e] for e in range(i0, i1)):
                        continue
                    syn_total += 1
                    why, _f = px.screen(i0, i1, a, b)
                    if why is None:
                        syn_acc += 1
        # 文数一致の段落: 隣接する誤ったペア(E_i, J_(i+1))を1:1経路の採否(screen_equal)に通して棄却率を見る
        eq_total, eq_acc = 0, 0
        for k, gr in G.items():
            en, ja = T[k]
            if len(en) != len(ja):
                continue
            px = AL._Para(en, ja, st, P)
            for i in range(len(en) - 1):
                eq_total += 1
                why, _f = px.screen_equal(i, None, i + 1)
                eq_acc += 1 if why is None else 0
        # 段落取り違え(同記事・同level内の別段落JAと組合せ)
        cross_emitted, cross_total = 0, 0
        for a in G:
            for b in G:
                if a == b or a[0] != b[0] or a[1] != b[1]:
                    continue
                res = AL.align_paragraph(T[a][0], T[b][1], st, P)
                cross_total += 1
                cross_emitted += sum(1 for g in res if g["ja"] is not None)
        tt = sum(v["total"] for v in per_lv.values())
        ll = sum(v["linked"] for v in per_lv.values())
        cov = lambda v: round(v["linked"] / v["total"], 4) if v["total"] else None   # noqa: E731
        return {"params": P, "paragraphs": len(G), "en_sentences": tt, "gold_groups": sum(len(g) for g in G.values()), "emitted_groups": ngroups,
                "wrong_groups": wrong, "synthetic_total": syn_total, "synthetic_accepted": syn_acc, "equal_mode_wrong_pairs_total": eq_total, "equal_mode_wrong_pairs_accepted": eq_acc,
                "coverage": round(ll / tt, 4), "coverage_by_level": {k: cov(v) for k, v in per_lv.items()}, "coverage_by_article": {k: cov(v) for k, v in per_art.items()},
                "counts_by_article": per_art, "counts_by_level": per_lv, "cross_pairs": cross_total, "cross_emitted": cross_emitted}
    finally:
        shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    if "--holdout" in sys.argv:          # 完全な未見(ig)のみ
        r = evaluate(unseen=True, arts=("ig",))
        print(json.dumps({k: v for k, v in r.items() if k not in ("params", "counts_by_article", "counts_by_level")}, ensure_ascii=False, indent=1))
        sys.exit(0)
    if "--unseen" in sys.argv:
        r = evaluate(unseen=True)
        print(json.dumps({k: v for k, v in r.items() if k not in ("params", "counts_by_article", "counts_by_level")}, ensure_ascii=False, indent=1))
        sys.exit(0)
    r = evaluate()
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k not in ("params", "counts_by_article", "counts_by_level")}, ensure_ascii=False, indent=1))
