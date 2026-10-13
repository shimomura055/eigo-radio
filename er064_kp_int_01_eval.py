# ============================================================
# er064_kp_int_01_eval.py  (Round1 評価ヘルパ: アンカー照合・スコア。評価専用、Trial専用)
# アンカー(anchors_r1.json)は評価のためだけに読む。Prompt/shortlist builderからは参照しない(testで確認)。
# ============================================================
from __future__ import annotations

import json
import re

ANCHORS_PATH = "er064_output/kp_integrated_opt_01/round1/anchors_r1.json"
_A = json.load(open(ANCHORS_PATH, encoding="utf-8"))["anchors"]
LOW = {9, 10, 11, 12}


def weight(rank):
    return 13 - rank


def _norm(s):
    return (s or "").lower().replace("’", "'").strip()


def anchor_hits(text, mode="full"):
    """textに一致するアンカーrankのリスト。mode=full/fragment。"""
    t = _norm(text)
    out = []
    for a in _A:
        pat = a.get(mode)
        if pat and re.search(pat, t):
            out.append(a["rank"])
    return out


def in_article(article_text):
    t = _norm(article_text)
    # 活用/語形差を拾うfull正規表現を本文へ適用(ハイフン無し化は不要、patternが吸収)
    return sorted(a["rank"] for a in _A if re.search(a["full"], t))


def reach_in_shortlist(cands):
    """cands: [{surface_form,...}]。戻り: {rank: 'full'|'fragment'|None}"""
    res = {}
    for a in _A:
        r = None
        for c in cands:
            s = _norm(c["surface_form"])
            if re.search(a["full"], s):
                r = "full"
                break
            if a.get("fragment") and re.search(a["fragment"], s) and r is None:
                r = "fragment"
        res[a["rank"]] = r
    return res


def item_anchor(item):
    """選定itemのアンカー照合: display_phrase/source_span/candidate_surfaceのいずれか。戻り (rank, mode) または (None, None)。"""
    texts = [item.get("display_phrase"), item.get("source_span"), item.get("candidate_surface")]
    for mode in ("full", "fragment"):
        for t in texts:
            h = anchor_hits(t or "", mode)
            if h:
                return h[0], mode
    return None, None


def run_score(items):
    """最終5件(selected_items)のアンカー簡易スコア。重複rankは1回のみ。"""
    ranks = {}
    frags = []
    for it in items:
        r, m = item_anchor(it)
        if r is None:
            continue
        if m == "full":
            ranks.setdefault(r, it)
        else:
            frags.append(r)
    return {"score": sum(weight(r) for r in ranks), "full_ranks": sorted(ranks), "fragment_ranks": sorted(frags),
            "low_slots": sum(1 for r in ranks if r in LOW)}


def ceiling(article_ranks):
    """記事に実在するアンカーだけで作れる5件の上限スコア(top5 weight)。"""
    ws = sorted((weight(r) for r in article_ranks), reverse=True)[:5]
    return sum(ws)


_CREATIVE = json.load(open(ANCHORS_PATH, encoding="utf-8")).get("creative_metaphor_patterns", [])


def is_creative(item):
    for t in (item.get("display_phrase"), item.get("source_span"), item.get("candidate_surface")):
        tt = _norm(t)
        if tt and any(re.search(p, tt) for p in _CREATIVE):
            return True
    return False
