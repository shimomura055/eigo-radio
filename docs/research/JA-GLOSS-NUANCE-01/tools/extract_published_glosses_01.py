# -*- coding: utf-8 -*-
"""JA-GLOSS-NUANCE-01: origin/main の公開済みX/Y/Z記事(user_test/*/enduser/data/article.json)から
学習項目(vocab)の『本文中の意味』(=gloss_ja)・本文の英文・解説冒頭を抽出する(読取専用・API 0)。"""
import json, subprocess, sys, re, os
REPO = os.environ.get("JAG_REPO", r"C:\Users\tensh\eigo-radio")
OUT = sys.argv[1]
def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, check=True).stdout
names = git("ls-tree", "-r", "origin/main", "--name-only").decode("utf-8").splitlines()
paths = [n for n in names if re.match(r"^user_test/[^/]+/enduser/data/article\.json$", n)]
rows = []
for p in paths:
    art = p.split("/")[1]
    d = json.loads(git("show", f"origin/main:{p}").decode("utf-8"))
    fam = art.split("_")[1].upper()
    for lvname, lv in d["levels"].items():
        for idx, v in enumerate(lv.get("vocab", [])):
            f = {x["label"]: re.sub(r"<[^>]+>", "", x["html"]) for x in v.get("fields", [])}
            rows.append({"article": art, "family": fam, "level": lvname, "idx": idx, "heading": v.get("heading"),
                         "gloss_ja": f.get("本文中の意味"), "sentence_en": f.get("本文の英文"),
                         "sentence_ja": f.get("日本語訳"), "explain_head": (f.get("解説") or "")[:160]})
json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(paths), "articles", len(rows), "rows")
