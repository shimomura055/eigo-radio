# ============================================================
# er108_kp_guard_exposure_01.py  (API 0 / 費用0 / 読み取りのみ。研究用script)
# KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_01: 『数値・否定保護の解除』で偽PASSが増える余地があるか(露出)を、保存済みKP(distinct used_form)に
# 合成した誤転写(数詞置換・否定語の脱落/付加)を通して見積もる。判定は票の分類器(kp3v._classify=classify_asr_match+同音救済)だけ
# (保護解除後に票を決めるのは分類器のみ)。値ガード(DIFF)/否定ガードが旧来これを止めていた件数と、分類器が単独で止める件数を分ける。
# 使い方: .venv\Scripts\python.exe er108_kp_guard_exposure_01.py --out docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/guard_exposure_01.json
# ============================================================
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, ".")
import er078_asr_unified_judge_01 as uj
import importlib

kp3v = importlib.import_module("er104_kp_three_asr_vote_01")   # `import er104_`字面を避ける理由はer108_kp_vote_noguard_01.py参照

NUM = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "twenty", "thirty", "hundred", "thousand", "million", "half"]
NEG = {"not", "no", "never", "without", "none", "nothing", "nobody", "nowhere", "neither", "nor", "cannot", "n't"}
NEGRE = re.compile(r"\b(not|no|never|without|none|nothing|nobody|nowhere|neither|nor|cannot)\b|n't\b", re.I)


def variants(canon):
    toks = canon.split()
    out = []
    for i, t in enumerate(toks):
        tl = re.sub(r"[^\w']", "", t.lower())
        if tl in NUM:
            alt = NUM[(NUM.index(tl) + 3) % len(NUM)]
            out.append(("num_swap", " ".join(toks[:i] + [alt] + toks[i + 1:])))
        if re.fullmatch(r"\d+", tl):
            out.append(("digit_swap", " ".join(toks[:i] + [str(int(tl) + 3)] + toks[i + 1:])))
        if tl in NEG or tl.endswith("n't"):
            out.append(("neg_drop", " ".join(toks[:i] + toks[i + 1:])))
    if not NEGRE.search(canon):
        out.append(("neg_add", "not " + canon))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    phrases = {}
    for f in glob.glob("**/keywords_canonicalized.json", recursive=True):
        try:
            d = json.load(open(f, encoding="utf8"))
        except Exception:
            continue
        for it in d.get("items") or []:
            t = (it.get("used_form") or it.get("key_phrase") or "").strip()
            if t:
                phrases.setdefault(t.lower(), t)
    rows, by = [], {}
    for canon in phrases.values():
        has_num = bool(re.search(r"\d", canon)) or any(re.sub(r"[^\w']", "", t.lower()) in NUM for t in canon.split())
        has_neg = bool(NEGRE.search(canon))
        for kind, hyp in variants(canon):
            vgr, neg = uj._protected(canon, hyp, "en")
            guard_old = bool(vgr.kind == uj.vg.DIFF or neg)
            ok, label = kp3v._classify(canon, hyp)
            rows.append({"canon": canon, "kind": kind, "hyp": hyp, "classifier_pass": bool(ok), "label": label, "old_guard_blocks": guard_old,
                         "has_num": has_num, "has_neg": has_neg})
            s = by.setdefault(kind, {"n": 0, "classifier_pass": 0, "old_guard_blocks": 0, "classifier_pass_and_old_guard_blocks": 0})
            s["n"] += 1
            s["classifier_pass"] += int(bool(ok))
            s["old_guard_blocks"] += int(guard_old)
            s["classifier_pass_and_old_guard_blocks"] += int(bool(ok) and guard_old)
    out = {"generated_by": "er108_kp_guard_exposure_01.py", "api_calls": 0, "cost_jpy": 0, "distinct_phrases": len(phrases),
           "phrases_with_number": len({r["canon"] for r in rows if r["has_num"]}), "phrases_with_negation": len({r["canon"] for r in rows if r["has_neg"]}),
           "by_kind": by, "false_accept_examples": [r for r in rows if r["classifier_pass"]][:60], "rows": rows}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("distinct_phrases", "phrases_with_number", "phrases_with_negation", "by_kind")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
