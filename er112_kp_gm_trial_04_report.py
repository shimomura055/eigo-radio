# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14: 課題① 盲検表(arm伏せ・key分離)と集計 (DEV専用、API 0。Sonnet参考Judgeは別サブコマンド)。
サブコマンド:
  blind   : Fable盲検表 fable_blind_04.md + fable_blind_04_key.json を生成(未ラベルの文字列だけ)
  report  : --labels <json> で集計(Fableラベル or Sonnet参考)。labels形式 {"<row#>:<col>": "PASS|THIN|FAIL|FAIL_LIT"}。
"""
from __future__ import annotations

import argparse, collections, json, os, random, sys
os.environ.setdefault("KP04_INSPECT_VERSION", "v2")
os.environ.setdefault("KP04_INSPECT_EFFORT", "low")
import er112_kp_gm_trial_04 as X                      # noqa: E402
import er112_kp_gm_trial_04_gen as G                  # noqa: E402
import er112_kp_gm_trial_04_c as C                    # noqa: E402

OUT = X.OUT
sys.stdout.reconfigure(encoding="utf-8")
RANK = {"PASS": 2, "THIN": 1, "FAIL": 0, "FAIL_LIT": 0}


def preloaded():
    """Trial_02/03のFable確定ラベル(string単位)。{(kp, sent, gloss): PASS/THIN/FAIL/FAIL_LIT}"""
    out = {}
    for r in X.phase0_cells():
        out[(r["key_phrase"], r["source_sentence"], r["gloss"])] = {"PASS": "PASS", "THIN": "THIN", "OTHER_NG": "FAIL", "LITERAL_NG": "FAIL_LIT"}[r["cls"]]
    return out


def cells():
    """全arm出力 {(arm,key,rep): gloss}。C=B0でflagされたものだけ再生成後のgloss、未flagはB0と同一(バイト同一)。"""
    b0, A = C.b0_rows()
    cc = C.arm_outputs("C")
    out = {}
    for (k, rep), r in b0.items():
        out[("B0", k, rep)] = r["gloss"]
        out[("C", k, rep)] = cc[(k, rep)]["gloss"] if (k, rep) in cc else r["gloss"]
    for arm in ("M", "Cp"):
        for (k, rep), r in C.arm_outputs(arm).items():
            out[(arm, k, rep)] = r["gloss"]
    return out, A


def cmd_blind(a):
    out, A = cells()
    pre = preloaded()
    keys = json.load(open(OUT / "strata_04.json", encoding="utf-8"))["trial_set"]
    lines = ["# fable_blind_04: Std日本語gloss盲検表(委任_14 課題①。arm伏せ)\n",
             "行=Key Phrase、列A〜=この表で初めて見る日本語glossの**文字列**(同じ文字列は1列。arm・repの帰属は`fable_blind_04_key.json`に分離)。**判定してからkeyを開くこと。**",
             "判定: PASS / 薄(△=意味は誤りでないがフレーズ全体より弱い・含意欠落) / FAIL(用法取り違え・字義訳・別義・誤訳)。FAILのうち字義訳(比喩・慣用を字義の像で訳したもの)は `FAIL_LIT` と書く。",
             "難例(draw a line, take the wheel 等)は`GOLD_LABELS_FINAL_01.md`のgold、通常は本文文の用法とフレーズ全体の意味への一致が基準。",
             "Trial_02/03で既にFable確定済みの文字列(B0の旧出力)は表に含めない(ラベル継承)。\n",
             "| # | 層/型 | key_phrase | 本文の文 | " + " | ".join(chr(65 + i) for i in range(8)) + " |", "|---|---|---|---|" + "---|" * 8]
    keymap = {}
    n = 0
    for k in sorted(keys, key=lambda x: (x not in json.load(open(OUT / "strata_04.json", encoding="utf-8"))["F_layer"], x)):
        kp = A[k]
        by = collections.OrderedDict()
        for (arm, kk, rep), g in sorted(out.items()):
            if kk != k or not g:
                continue
            if (kp["key"], kp["sent"], g) in pre:
                continue
            by.setdefault(g, []).append("%s/rep%d" % (arm, rep))
        if not by:
            continue
        n += 1
        strs = list(by)
        random.Random("blind04-" + k).shuffle(strs)
        keymap[str(n)] = {"key": k, "cols": {chr(65 + i): dict(gloss=s, cells=by[s]) for i, s in enumerate(strs)}}
        layer = "F" if k in json.load(open(OUT / "strata_04.json", encoding="utf-8"))["F_layer"] else "N"
        lines.append("| %d | %s/%s/%s | %s | %s | %s |" % (n, layer, kp["tier"], kp["family"], kp["key"], kp["sent"].replace("|", "/")[:160],
                                                         " | ".join(s.replace("|", "/") for s in strs + [""] * (8 - len(strs)))))
    (OUT / "fable_blind_04.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "fable_blind_04_key.json").write_text(json.dumps(keymap, ensure_ascii=False, indent=1), encoding="utf-8")
    print("blind rows", n, "cols max", max(len(v["cols"]) for v in keymap.values()), "cells", sum(len(c["cells"]) for v in keymap.values() for c in v["cols"].values()))


def label_table(labels):
    """labels: {"<row#>:<col>": label} -> {(kp,sent,gloss): label}(+ preloaded)"""
    A = C.X.all_kps()
    keymap = json.load(open(OUT / "fable_blind_04_key.json", encoding="utf-8"))
    tab = dict(preloaded())
    for rk, v in keymap.items():
        for col, c in v["cols"].items():
            lab = labels.get("%s:%s" % (rk, col))
            if lab:
                kp = A[v["key"]]
                tab[(kp["key"], kp["sent"], c["gloss"])] = lab
    return tab


def cmd_report(a):
    labels = json.load(open(a.labels, encoding="utf-8"))
    tab = label_table(labels)
    out, A = cells()
    st = json.load(open(OUT / "strata_04.json", encoding="utf-8"))
    F = set(st["F_layer"])
    anchors = set(st["anchors"])
    lines = ["# 課題① 集計(ラベル=%s)\n" % a.labels]
    def lab(arm, k, rep):
        g = out.get((arm, k, rep))
        return tab.get((A[k]["key"], A[k]["sent"], g)) if g else None
    for layer, ks in (("F層", [k for k in st["trial_set"] if k in F]), ("N標本", [k for k in st["trial_set"] if k not in F]), ("全体", st["trial_set"])):
        lines.append("## %s (KP=%d)\n" % (layer, len(ks)))
        lines.append("| arm | n出力 | PASS | 薄 | FAIL(字義 FAIL_LIT/その他) | 未ラベル | FAIL_LIT KP数 |")
        lines.append("|---|---|---|---|---|---|---|")
        for arm in ("B0", "C", "M", "Cp"):
            c = collections.Counter()
            lit_kp = set()
            for k in ks:
                for rep in (1, 2):
                    l = lab(arm, k, rep)
                    if out.get((arm, k, rep)) is None:
                        continue
                    c[l or "unlabeled"] += 1
                    if l == "FAIL_LIT":
                        lit_kp.add(k)
            n = sum(c.values())
            lines.append("| %s | %d | %d | %d | %d (%d/%d) | %d | %d |" % (arm, n, c["PASS"], c["THIN"], c["FAIL"] + c["FAIL_LIT"], c["FAIL_LIT"], c["FAIL"], c["unlabeled"], len(lit_kp)))
        lines.append("")
    # C vs B0(出力単位 flip)
    flips = collections.Counter()
    detail = []
    for k in st["trial_set"]:
        for rep in (1, 2):
            gb, gc = out.get(("B0", k, rep)), out.get(("C", k, rep))
            if gb is None or gb == gc:
                continue
            lb, lc = lab("B0", k, rep), lab("C", k, rep)
            if lb is None or lc is None:
                flips["unlabeled"] += 1
                continue
            d = RANK[lc] - RANK[lb]
            flips["improve" if d > 0 else "worse" if d < 0 else "same"] += 1
            detail.append((k, rep, gb, lb, gc, lc))
    lines.append("## C(flag項目のみ再生成)の flag項目内 Before->After (出力単位)\n")
    lines.append("flag(再生成)された出力 %d件: %s\n" % (sum(flips.values()), dict(flips)))
    lines.append("| KP | rep | Before | label | After | label |\n|---|---|---|---|---|---|")
    for d in detail:
        lines.append("| %s | %d | %s | %s | %s | %s |" % d)
    # gold PASS->FAIL 0 / 未flag不変
    lines.append("")
    reg = [d for d in detail if d[3] == "PASS" and d[5] in ("FAIL", "FAIL_LIT")]
    lines.append("- PASS->FAIL(新規悪化、flag項目内): %d件 %s" % (len(reg), [(d[0], d[1]) for d in reg]))
    # 検査器の recall/precision (B0出力)
    im = C.inspect_map()
    tp = fp = fn = tn = 0
    for k in st["trial_set"]:
        for rep in (1, 2):
            g = out.get(("B0", k, rep))
            if g is None:
                continue
            l = lab("B0", k, rep)
            if l is None:
                continue
            o = im.get((A[k]["key"], A[k]["sent"], g))
            f = C.is_flag(o)
            ng = l == "FAIL_LIT"
            tp += f and ng
            fp += f and not ng
            fn += (not f) and ng
            tn += (not f) and not ng
    lines.append("- 検査器(V2_inv) vs ラベル(FAIL_LIT): TP=%d FP=%d FN=%d TN=%d (recall=%s, precision=%s)" % (tp, fp, fn, tn, "%d/%d" % (tp, tp + fn), "%d/%d" % (tp, tp + fp)))
    (OUT / ("report1_%s.md" % os.path.basename(a.labels).replace(".json", ""))).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--labels", default="")
    a = ap.parse_args()
    {"blind": cmd_blind, "report": cmd_report}[a.cmd](a)
