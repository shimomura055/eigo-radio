# -*- coding: utf-8 -*-
"""OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 M5: 評価用の匿名コピー作成(決定論・標準ライブラリのみ・API/生成なし)。
手順の定義は docs/pm/b3_trial_01/blinding.md。
  記事: runs/<slug>/nb/<V>/b<i>/w<j>/{ja_writer/original.md,revision1.md,revision2.md, b1b/article.md}
        -> eval/blind/<slug>/<code>/{ja_writer/*.md, b1b/article.md}
  brief: runs/<slug>/nb/<V>/b<i>/storyline_b3/selected_brief.md (なければ w1配下)
        -> eval/blind/<slug>/_briefs/<bcode>/selected_brief.md
  対応表: eval/blind/MAP.json (集計まで評価者に渡さない)
codeは sha256(seed|キー) 由来の固定乱数(4文字、衝突時のみ延長)。同じseed・同じ入力なら常に同じ結果(再実行しても変わらない)。
usage: python make_blind_copies.py [--seed 20261007] [--what briefs|articles|both]"""
import argparse, hashlib, json, os, shutil, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUNS = "er052_output/open233_b3_trial_01/runs"
BLIND = "er052_output/open233_b3_trial_01/eval/blind"
SLUGS = ("meta", "hormuz", "space_weapons")
VARIANTS = ("V0", "V1", "V2", "V3", "V5", "V6")
ART_FILES = ["ja_writer/original.md", "ja_writer/revision1.md", "ja_writer/revision2.md", "b1b/article.md"]
ALPHA = "abcdefghjkmnpqrstuvwxyz23456789"  # 紛らわしい文字(i,l,o,0,1)を除く


def code_for(seed, key, taken):
    h = hashlib.sha256(("%s|%s" % (seed, key)).encode("utf-8")).digest()
    n = 4
    while True:
        c = "".join(ALPHA[b % len(ALPHA)] for b in h[:n])
        if c not in taken:
            return c
        n += 1  # 衝突時のみ延長(キー順固定なので決定論)
        h = hashlib.sha256(h).digest() if n > len(h) else h


def main():
    os.chdir(ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="20261007")
    ap.add_argument("--what", default="both", choices=("briefs", "articles", "both"))
    ns = ap.parse_args()
    mp = {"seed": ns.seed, "articles": {}, "briefs": {}, "note": "集計まで評価者に渡さない(M5)。"}
    taken_a, taken_b = {}, {}
    for s in SLUGS:
        taken_a[s], taken_b[s] = set(), set()
        for v in VARIANTS:
            for i in (1, 2):
                bdir = "%s/%s/nb/%s/b%d" % (RUNS, s, v, i)
                bkey = "%s|%s|b%d" % (s, v, i)
                bc = code_for(ns.seed, "brief|" + bkey, taken_b[s])
                taken_b[s].add(bc)
                bsrc = None
                for c in (bdir + "/storyline_b3/selected_brief.md", bdir + "/w1/storyline_b3/selected_brief.md"):
                    if os.path.isfile(c):
                        bsrc = c
                        break
                if bsrc is not None:
                    mp["briefs"]["%s/%s" % (s, bc)] = {"variant": v, "b3_rep": i, "src": bsrc}
                    if ns.what in ("briefs", "both"):
                        d = "%s/%s/_briefs/%s" % (BLIND, s, bc)
                        os.makedirs(d, exist_ok=True)
                        shutil.copyfile(bsrc, d + "/selected_brief.md")
                for j in (1, 2):
                    adir = "%s/w%d" % (bdir, j)
                    akey = "%s|%s|b%d|w%d" % (s, v, i, j)
                    ac = code_for(ns.seed, "article|" + akey, taken_a[s])
                    taken_a[s].add(ac)
                    if not all(os.path.isfile(adir + "/" + f) for f in ART_FILES):
                        continue
                    mp["articles"]["%s/%s" % (s, ac)] = {"variant": v, "b3_rep": i, "writer_rep": j, "bcode": bc}
                    if ns.what in ("articles", "both"):
                        for f in ART_FILES:
                            dst = "%s/%s/%s/%s" % (BLIND, s, ac, f)
                            os.makedirs(os.path.dirname(dst), exist_ok=True)
                            shutil.copyfile(adir + "/" + f, dst)
    os.makedirs(BLIND, exist_ok=True)
    with open(BLIND + "/MAP.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(mp, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print("briefs=%d articles=%d map=%s/MAP.json" % (len(mp["briefs"]), len(mp["articles"]), BLIND))


if __name__ == "__main__":
    sys.exit(main())
