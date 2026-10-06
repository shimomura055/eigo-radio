#!/usr/bin/env python3
"""ent_metrics_p01: EN記事md+台帳txt -> 文数/平均文長/type-token比/台帳逐語コピー率(8語以上連続一致に含まれる語の割合)。"""
import argparse, json, re
from pathlib import Path

N = 8


def words(s):
    return re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", s.lower().replace("’", "'"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    art = Path(a.article).read_text(encoding="utf-8")
    body = "\n".join(x for x in art.split("\n") if not x.lstrip().startswith("#"))
    sents = [s for s in re.split(r"(?<=[.!?])\s+|\n+", body) if words(s)]
    w = words(body)
    lw = words(Path(a.ledger).read_text(encoding="utf-8"))
    grams = {tuple(lw[i:i + N]) for i in range(len(lw) - N + 1)}
    cov = [False] * len(w)
    for i in range(len(w) - N + 1):
        if tuple(w[i:i + N]) in grams:
            for j in range(i, i + N):
                cov[j] = True
    r = {"article": a.article, "ledger": a.ledger, "n_sentences": len(sents), "n_words": len(w),
         "avg_sentence_len_words": round(len(w) / len(sents), 3) if sents else 0,
         "type_token_ratio": round(len(set(w)) / len(w), 4) if w else 0,
         "verbatim_copy_rate_8gram": round(sum(cov) / len(w), 4) if w else 0, "verbatim_n": N,
         "note": "台帳がJA主体のため英語記事では8語連続一致が0に近くなりやすい(英語併記/URL等のみ一致)。見出し(#行)は除外"}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
