# -*- coding: utf-8 -*-
"""prompt_lint_p04: 単一仕様の機械確認(DEV/Trial専用、API非呼出)。
各patternの*_prompt.txtについて、(1)【出力】が1か所 (2)必須プレースホルダが各1回(MAX_CHARSは1回以上)で未使用・未知なし
(3)同一行(空白除く10字以上)の重複なし (4)stage1がpatterns/_common/stage1_prompt.txtと同一内容、
(5)examples/ダミーfactを埋めた組立後promptでも(1)(3)を満たす、を検査する。PASS/FAILを出力。"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

REQUIRED = {  # prompt種別 -> {placeholder: 最小回数, 最大回数}
    "stage1_prompt.txt": {"EXAMPLES": (1, 1), "LEDGER_FACTS": (1, 1)},
    "stage2_prompt.txt": {"MAX_CHARS": (1, 9), "EXAMPLES": (0, 1), "CANDIDATES": (1, 1), "LEDGER_FACTS": (1, 1)},
    "cover_prompt.txt": {"COVER_INPUT": (1, 1)},
    "stage1_5_prompt.txt": {"S15_INPUT": (1, 1)},
    "headline_prompt.txt": {"HEADLINE_INPUT": (1, 1)},
}
PH = re.compile(r"\{([A-Z][A-Z0-9_]*)\}")
MIN_DUP_LEN = 10


def dup_lines(text):
    c = Counter(ln.strip() for ln in text.splitlines() if len(ln.strip()) >= MIN_DUP_LEN)
    return [ln for ln, n in c.items() if n >= 2]


def lint_text(name, text):
    """1つのprompt本文を検査し、問題のリストを返す。"""
    errs = []
    n_out = text.count("【出力】")
    if n_out != 1:
        errs.append("【出力】が%d か所(1か所必須)" % n_out)
    req = REQUIRED.get(name)
    found = Counter(PH.findall(text))
    if req is None:
        errs.append("未知のprompt種別: %s" % name)
        req = {}
    for k, (lo, hi) in req.items():
        if not (lo <= found.get(k, 0) <= hi):
            errs.append("プレースホルダ{%s}の出現回数=%d (期待%d〜%d)" % (k, found.get(k, 0), lo, hi))
    for k in found:
        if k not in req:
            errs.append("未知のプレースホルダ{%s}" % k)
    for ln in dup_lines(text):
        errs.append("重複行: %s" % ln[:40])
    return errs


def lint_assembled_stage1(text, examples):
    """examples・ダミーfactを埋めた後でも【出力】1か所・重複行なしであること。"""
    t = text.replace("{EXAMPLES}", examples or "").replace("{LEDGER_FACTS}", '[{"fact_id": "D-1", "claim": "dummy"}]')
    errs = []
    if t.count("【出力】") != 1:
        errs.append("組立後【出力】が%d か所" % t.count("【出力】"))
    errs += ["組立後 重複行: %s" % ln[:40] for ln in dup_lines(t)]
    return errs


def load_forbidden(path):
    """eval/forbidden_terms.txt(1行1語、#始まりはコメント)。ファイルが無ければ空。"""
    p = Path(path) if path else None
    if p is None or not p.exists():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]


def forbidden_hits(text, terms):
    low = text.lower()
    return [t for t in terms if t in text or t.lower() in low]


def prompt_hashes(pdir):
    """patterns/<name>/*.txt の sha256(prompt原文)。"""
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(Path(pdir).glob("*_prompt.txt"))}


def lint_pattern(pdir, common=None, forbidden=None):
    pdir = Path(pdir)
    meta_p = pdir / "pattern.json"
    if common is not None and meta_p.exists():  # patternが独自のstage1単一仕様ファイル(_common配下)を宣言していればそれと比較する
        cs = json.loads(meta_p.read_text(encoding="utf-8")).get("common_stage1")
        if cs:
            common = Path(common).parent / cs
    res = {}
    files = sorted(pdir.glob("*_prompt.txt"))
    if not any(f.name == "stage1_prompt.txt" for f in files):
        res["(dir)"] = ["stage1_prompt.txt がない"]
    for f in files:
        text = f.read_text(encoding="utf-8")
        errs = lint_text(f.name, text)
        errs += ["禁止語(forbidden_terms): %s" % h for h in forbidden_hits(text, forbidden or [])]
        if f.name == "stage1_prompt.txt":
            ex = pdir / "examples.txt"
            errs += lint_assembled_stage1(text, ex.read_text(encoding="utf-8").strip("\n") if ex.exists() else "")
            if common is not None and common.exists() and text != common.read_text(encoding="utf-8"):
                errs.append("patterns/_common/stage1_prompt.txtと内容が異なる(単一仕様違反)")
        res[f.name] = errs
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", nargs="+", required=True, help="pattern dir(複数可)")
    ap.add_argument("--forbidden", default=str(Path(__file__).resolve().parents[1] / "eval" / "forbidden_terms.txt"))
    ap.add_argument("--runs-dir", default=str(Path(__file__).resolve().parents[1] / "runs"), help="prompt_hashes.jsonの保存先(runs/<pattern>/)")
    ap.add_argument("--no-write-hashes", action="store_true")
    a = ap.parse_args(argv)
    terms = load_forbidden(a.forbidden)
    bad = 0
    for d in a.patterns:
        pd = Path(d)
        res = lint_pattern(pd, pd.parent / "_common" / "stage1_prompt.txt", terms)
        if not a.no_write_hashes:
            hd = Path(a.runs_dir) / pd.name
            hd.mkdir(parents=True, exist_ok=True)
            (hd / "prompt_hashes.json").write_text(json.dumps(prompt_hashes(pd), ensure_ascii=False, indent=1), encoding="utf-8")
        for fn, errs in res.items():
            print("%s/%s: %s" % (pd.name, fn, "OK" if not errs else "NG"))
            for e in errs:
                print("   - " + e)
                bad += 1
    print("PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
