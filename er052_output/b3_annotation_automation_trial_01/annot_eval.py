# -*- coding: utf-8 -*-
"""B3-ANNOTATION-AUTOMATION-TRIAL-01 評価スクリプト(決定論・LLM不使用・API無し)。
候補注記版 vs Ground Truth(既存Trialのmerged/final注記版)をタグ単位で比較する。位置合わせは既存 b3_annotation_check_01.align_md を再利用。
usage:  annot_eval.py selftest        GT同士(=1.0)と意図的摂動で指標コードを検証
        annot_eval.py compare --brief B --gt-annotated G [--gt-sidecar S] --cand-annotated C [--cand-sidecar S] [--out J]"""
import sys, os, re, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "factlock_astra_e2e_trial_01"))
import b3_annotation_check_01 as chk

def events(brief, ann):
    r = chk.align_md(brief, ann)
    if not r["ok"]:
        return None, r["reason"]
    ev = []
    for off, kind, txt in r["events"]:
        if kind == "tag": ev.append((off, "fact"))
        else: ev.append((off, "core" if "中核" in txt else "peripheral"))
    return ev, ""

def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None; r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else (0.0 if (p is not None and r is not None) else None)
    return dict(tp=tp, fp=fp, fn=fn, precision=p, recall=r, f1=f)

def compare(brief, gt_ann, cand_ann, gt_side=None, cand_side=None):
    out = {}
    g, why_g = events(brief, gt_ann); c, why_c = events(brief, cand_ann)
    out["gt_body_unmodified"] = g is not None
    out["cand_body_unmodified"] = c is not None   # 本文非改変(定義済み挿入以外の差分なし)
    if c is None or g is None:
        out["reason"] = why_c or why_g; return out
    G, C = set(g), set(c)
    for t in ("fact", "core", "peripheral"):
        gs = {e for e in G if e[1] == t}; cs = {e for e in C if e[1] == t}
        out[t] = prf(len(gs & cs), len(cs - gs), len(gs - cs))
    gn = {e[0]: e[1] for e in G if e[1] != "fact"}; cn = {e[0]: e[1] for e in C if e[1] != "fact"}
    both = set(gn) & set(cn)
    out["number_presence"] = prf(len(both), len(set(cn) - set(gn)), len(set(gn) - set(cn)))  # 位置のみ(中核/周辺を問わない)
    out["core_peripheral_class_agreement"] = (sum(gn[k] == cn[k] for k in both) / len(both)) if both else None
    out["n_gt_marks"] = len(gn); out["n_cand_marks"] = len(cn)
    if gt_side and cand_side:   # Fact ID対応: 位置が一致した【事実N】どうしでledger_ids集合が同一か
        def fmap(ann, side):
            ev, _ = events(brief, ann); offs = [o for o, t in ev if t == "fact"]
            ids = [set(f.get("ledger_ids", [])) for f in side.get("facts", [])]
            return {o: ids[i] for i, o in enumerate(offs) if i < len(ids)}
        gm, cm = fmap(gt_ann, gt_side), fmap(cand_ann, cand_side); m = set(gm) & set(cm)
        out["fact_ledger_id_exact_match"] = (sum(gm[k] == cm[k] for k in m) / len(m)) if m else None
    return out

def selftest():
    inv = json.load(open(os.path.join(HERE, "gt_inventory.json"), encoding="utf-8"))
    res = []
    for r in inv:
        if not r.get("final"): continue
        b = open(r["brief"], encoding="utf-8", newline="").read(); a = open(r["final"], encoding="utf-8", newline="").read()
        s = json.load(open(r["final_sidecar"], encoding="utf-8"))
        same = compare(b, a, a, s, s)
        ok_same = same["cand_body_unmodified"] and all(same[t]["f1"] in (1.0, None) for t in ("fact", "core", "peripheral")) and same["core_peripheral_class_agreement"] in (1.0, None)
        # 摂動1: 最初の【中核数値】を削除 -> core recall 低下
        pert = a.replace("【中核数値】", "", 1) if "【中核数値】" in a else a
        p1 = compare(b, a, pert); detect1 = ("【中核数値】" not in a) or (p1["core"]["recall"] is not None and p1["core"]["fp"] + p1["core"]["fn"] > 0)
        # 摂動2: 本文を1文字改変 -> 非改変FAIL
        i = a.find("。"); bad = a[:i] + "、" + a[i + 1:] if i > 0 else a + "x"
        p2 = compare(b, a, bad); detect2 = p2["cand_body_unmodified"] is False
        res.append(dict(theme=r["theme"], identity_ok=bool(ok_same), perturb_tag_drop_detected=bool(detect1), perturb_body_edit_detected=bool(detect2)))
        print(res[-1])
    allok = all(x["identity_ok"] and x["perturb_tag_drop_detected"] and x["perturb_body_edit_detected"] for x in res)
    json.dump(dict(all_pass=allok, results=res), open(os.path.join(HERE, "annot_eval_selftest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("SELFTEST", "ALL_PASS" if allok else "FAIL"); return 0 if allok else 1

if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]: sys.exit(selftest())
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--brief"); ap.add_argument("--gt-annotated"); ap.add_argument("--gt-sidecar")
    ap.add_argument("--cand-annotated"); ap.add_argument("--cand-sidecar"); ap.add_argument("--out"); a = ap.parse_args()
    rd = lambda p: open(p, encoding="utf-8", newline="").read()
    js = lambda p: json.load(open(p, encoding="utf-8")) if p else None
    r = compare(rd(a.brief), rd(a.gt_annotated), rd(a.cand_annotated), js(a.gt_sidecar), js(a.cand_sidecar))
    if a.out: json.dump(r, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(r, ensure_ascii=False, indent=1))
