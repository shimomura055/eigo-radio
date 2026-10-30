# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03B: M8(対応づけのLLM確認)をgold/未見/held-outで評価する(実LLM: gpt-6-luna)。

 A. 実運用と同じ呼出: align_paragraph(judge=本番judge)。LLMが追加採用した群(how=judge)がゴールドに照らして誤りでないか(誤対応0が合格)。coverageの変化。
 B. 陰性対照: ゴールド隣接2群の境界でEN文を1つ移した『誤った』候補(合成ずらし)を、そのまま本番judgeへ渡し、LLMが ok=true と答えた数(0が合格)。
    judgeが実運用で見る候補(DP候補)より厳しい=LLMの識別力の下限評価。段落ごとに最大 --neg-per-para 件(1 call/段落)。
使い方(環境shim経由、.env読込): python ejh_run_script.py <WT> <MAIN> tools/ejh03b_judge_gold_eval_01.py --out out.json [--neg-per-para N] [--sets train,unseen,ig]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import ejh02_gold_eval_01 as G  # noqa: E402
import er135_enduser_align_01 as AL  # noqa: E402
import er135_enduser_align_judge_01 as JU  # noqa: E402


def sets(names):
    out = {}
    if "train" in names:
        out["train"] = (G.load_gold(), G.load_texts())
    if "unseen" in names or "ig" in names:
        g, t = G.load_gold("gold_unseen_*.txt"), G.load_unseen_texts()
        if "unseen" in names:
            out["unseen"] = ({k: v for k, v in g.items() if k[0] != "ig"}, t)
        if "ig" in names:
            out["ig"] = ({k: v for k, v in g.items() if k[0] == "ig"}, t)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache-dir", required=True, help="judge応答キャッシュdir(再実行API 0)")
    ap.add_argument("--neg-per-para", type=int, default=0)
    ap.add_argument("--sets", default="train,unseen,ig")
    ap.add_argument("--max-calls", type=int, default=400)
    a = ap.parse_args(argv)
    llm = JU.DefaultLLM()
    judge = JU.make_judge(llm, cache_dir=a.cache_dir)
    st, td = G._store()
    P = dict(AL.PARAMS)
    report = {"sets": {}, "model": JU.MODEL, "prompt_sha256": JU.PROMPT_SHA256}
    for name, (Gd, T) in sets(a.sets.split(",")).items():
        rec = {"paragraphs": len(Gd), "en_sentences": 0, "plain_linked": 0, "judge_linked": 0, "judge_added_groups": 0, "judge_added_wrong": [],
               "wrong_total_groups": [], "neg_pairs": 0, "neg_ok": [], "pending_paragraphs": 0}
        for k, gr in Gd.items():
            en, ja = T[k]
            gm = G._gold_map(gr)
            plain = AL.align_paragraph(en, ja, st, P)
            before = judge.stats["calls"] + judge.stats["cache_hits"]
            res = AL.align_paragraph(en, ja, st, P, judge=judge)
            if judge.stats["calls"] + judge.stats["cache_hits"] > before:
                rec["pending_paragraphs"] += 1
            rec["en_sentences"] += len(en)
            rec["plain_linked"] += sum(len(g["en"]) for g in plain if g["ja"] is not None)
            rec["judge_linked"] += sum(len(g["en"]) for g in res if g["ja"] is not None)
            for g in res:
                if g["ja"] is None:
                    continue
                R = set(range(*g["ja"]))
                wrong = not all(R <= gm[e] for e in g["en"])
                if g.get("how") == "judge":
                    rec["judge_added_groups"] += 1
                    if wrong:
                        rec["judge_added_wrong"].append({"key": list(k), "en": g["en"], "ja": list(g["ja"])})
                if wrong:
                    rec["wrong_total_groups"].append({"key": list(k), "en": g["en"], "ja": list(g["ja"]), "how": g.get("how")})
            if a.neg_per_para and judge.stats["calls"] < a.max_calls:
                pairs = []
                for t in range(len(gr) - 1):
                    (e1, j1), (e2, j2) = gr[t], gr[t + 1]
                    if not j1 or not j2:
                        continue
                    for ens, jas in (([e1[-1]] + e2, j2), (e1 + [e2[0]], j1)):
                        R = set(range(jas[0], jas[-1] + 1))
                        if all(R <= gm[e] for e in ens):
                            continue
                        pairs.append((ens, (jas[0], jas[-1] + 1)))
                pairs = pairs[:a.neg_per_para]
                if pairs:
                    got = judge(en, ja, pairs)
                    rec["neg_pairs"] += len(pairs)
                    rec["neg_ok"] += [{"key": list(k), "en": p[0], "ja": list(p[1])} for p, ok in zip(pairs, got) if ok]
        rec["coverage_plain"] = round(rec["plain_linked"] / rec["en_sentences"], 4) if rec["en_sentences"] else None
        rec["coverage_with_judge"] = round(rec["judge_linked"] / rec["en_sentences"], 4) if rec["en_sentences"] else None
        report["sets"][name] = rec
    report["judge_stats"] = judge.stats
    report["llm_calls"] = len(llm.calls)
    report["cost_jpy"] = round(sum(c.get("cost_jpy") or 0 for c in llm.calls), 4)
    Path(a.out).write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: (v if k != "sets" else {n: {kk: vv for kk, vv in s.items() if not isinstance(vv, list)} for n, s in v.items()}) for k, v in report.items()}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
