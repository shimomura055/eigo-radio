# -*- coding: utf-8 -*-
"""全声IDの逐語抜粋(quotes)が、保存した出典本文(sources/pages, sources/hatena_*.json = git管理外)に実在するかを機械照合する(API 0)。
見出しやAI回答ではなく本人発言の本文にあるかを確認する目的。空白は無視して照合。
使い方: python verify_voices_02.py [--write-json]  -> 不一致があれば終了コード1"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voices_data_02 as d  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "sources")


def norm(s: str) -> str:
    return re.sub(r"[\s　]+", "", s)


def load_page_text(base_url: str) -> str:
    out = []
    for f in glob.glob(os.path.join(SRC, "pages", "*.txt")):
        head = open(f, encoding="utf-8").readline()
        u = head[4:].strip().split("?")[0].split("#")[0]
        if u == base_url:
            out.append(open(f, encoding="utf-8").read())
    for f in glob.glob(os.path.join(SRC, "hatena_*.json")):
        j = json.load(open(f, encoding="utf-8"))
        if j["url"].split("?")[0] == base_url:
            out.append("\n".join(c["comment"] for c in j["comments"]))
    return "\n".join(out)


def cut_ai_and_sidebar(t: str) -> str:
    # AI回答・関連質問欄より前だけを根拠として扱う
    for cut in ["AIからのお助け回答", "あわせて知りたい"]:
        i = t.find(cut)
        if i > 0:
            t = t[:i]
    return t


def main() -> int:
    cache, bad, n_q = {}, [], 0
    for v in d.V:
        base = d.SOURCES[v["src"]]["url"]
        if base not in cache:
            cache[base] = norm(cut_ai_and_sidebar(load_page_text(base)))
        if not cache[base]:
            bad.append((v["id"], "PAGE_NOT_FOUND", base))
            continue
        for q in v["quotes"]:
            n_q += 1
            if norm(q) not in cache[base]:
                bad.append((v["id"], "QUOTE_NOT_FOUND", q[:40]))
    print(f"voices={len(d.V)} quotes={n_q} problems={len(bad)}")
    for b in bad:
        print("  ", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
