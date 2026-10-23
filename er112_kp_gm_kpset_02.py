# -*- coding: utf-8 -*-
"""委任_07 Trial: KP集合の構築(DEV専用、API 0)。既存Trial/census由来のreplay入力のみ。"""
import json, glob, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
CENSUS = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/census_items_03_unique.json"
A_MARK1 = "【記事本文(参考)】\n"
A_MARK2 = "【記事本文(参考、文脈確認用)】\n"
APOS = chr(0x2019)


def _article_from_run(run, level, sent):
    base = ROOT / run / level / "key_phrases"
    for fn, mk in (("gloss_alignment_prompt.txt", A_MARK1), ("canonicalization_prompt.txt", A_MARK2)):
        p = base / fn
        if p.exists():
            t = p.read_text(encoding="utf-8")
            if mk in t:
                a = t.split(mk, 1)[1].split("\n\n【Key Phrase候補", 1)[0]
                if sent[:40] in a.replace(APOS, "'") or sent[:40] in a:
                    return a
    return None


def build():
    out = {}
    # 1) 既存er112 units(32 unit、production item)
    for u in json.load(open(ROOT / "er112_output/kp_gm_trial_01/inputs/units.json", encoding="utf-8"))["units"]:
        if u["synthetic"]:
            continue
        for r, it in u["production"].items():
            k = it["used_form"]
            out.setdefault(k.lower(), dict(key=k, display=it.get("key_phrase", k), sent=it["source_sentence"], article=u["article_text"], family=u["family"], run=u["run"], src="er112_units", gloss=it.get("gloss")))
    for u in json.load(open(ROOT / "er112_output/kp_gm_trial_01/a3_verify/units_a3verify.json", encoding="utf-8")):
        for it in u["items"]:
            k = it["used_form"]
            if k.lower() in out:
                continue
            art = u.get("article_text") or _article_from_run(u["run"], "b1b", it["source_sentence"]) or _article_from_run(u["run"], "a2", it["source_sentence"])
            if art:
                out[k.lower()] = dict(key=k, display=it["display_phrase"], sent=it["source_sentence"], article=art, family=u["family"], run=u["run"], src="a3_verify", gloss=it.get("gloss"))
    # 2) census 42 run/level
    seen_rl = set()
    for x in json.load(open(CENSUS, encoding="utf-8")):
        rl = (x["run"], x["level"])
        if rl in seen_rl:
            continue
        seen_rl.add(rl)
        p = ROOT / x["run"] / x["level"] / "key_phrases" / "keywords_canonicalized.json"
        if not p.exists():
            continue
        for it in json.load(open(p, encoding="utf-8")).get("items") or []:
            k = it.get("used_form") or it["key_phrase"]
            if k.lower() in out or not it.get("source_sentence"):
                continue
            art = _article_from_run(x["run"], x["level"], it["source_sentence"])
            if art:
                out[k.lower()] = dict(key=k, display=it["display_phrase"], sent=it["source_sentence"], article=art, family=x["family"], run=x["run"], src="census", gloss=it.get("japanese_gloss"))
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    d = build()
    print(len(d))
    import collections
    print(collections.Counter((v["family"], v["src"]) for v in d.values()))
    print("; ".join(f"{v['key']}[{v['family']}]" for v in sorted(d.values(), key=lambda x: x['key'].lower())))
