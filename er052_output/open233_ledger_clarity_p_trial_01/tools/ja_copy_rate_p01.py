#!/usr/bin/env python3
"""ja_copy_rate_p01: JA原稿md vs 台帳txt の12文字連続一致率(00c定義: 空白除去後、原稿の文字のうち台帳に現れる12-gramに含まれる文字の割合)。判定はしない。"""
import argparse, json, re
from pathlib import Path


def copy_ja(article, ledger, n=12):
    a = re.sub(r"\s", "", article)
    l = re.sub(r"\s", "", ledger)
    grams = {l[i:i + n] for i in range(len(l) - n + 1)}
    cov = [0] * len(a)
    for i in range(len(a) - n + 1):
        if a[i:i + n] in grams:
            for j in range(i, i + n):
                cov[j] = 1
    return len(a), sum(cov) / max(1, len(a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ja", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--out", help="任意: JSON出力パス")
    a = ap.parse_args()
    nc, r = copy_ja(Path(a.ja).read_text(encoding="utf-8"), Path(a.ledger).read_text(encoding="utf-8"), a.n)
    res = {"ja": a.ja, "ledger": a.ledger, "n_chars": nc, "ngram": a.n, "ledger_verbatim_copy_rate_charngram": round(r, 4), "judgement": "none"}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
