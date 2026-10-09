# -*- coding: utf-8 -*-
"""委任_03 P4(保留セット最終評価、1回のみ)集計。ラベルを読むのはこの集計だけ。
構成はP3で確定したものを変更しない: C_main = D0rollback ∪ D2(casebank=D2 1rep / 記事=D2rank)、副 = D1v2(D0ゲート+因果創作)、和集合。
出力: results/P4_RESULT_01.md / P4_RESULT_01.json
Recall_human(主)はユーザー確認の重大(保留はK01/K02/K11)。K01(rf_y84g5r)は D0語彙設計時に参照した汚染済み回帰として別掲(除外版も併記)。"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate_flagger_01 as AG  # noqa: E402
import p3_run_01 as PR  # noqa: E402

RES = os.path.join(HERE, "results")
CB = os.path.join(HERE, "..", "casebank")
MODEL = "gpt-6.1-sol"
CONTAM = "rf_y84g5r"


def rows_of(name):
    p = os.path.join(RES, name + ".jsonl")
    return AG.load_rows(p) if os.path.exists(p) else []


def hits_of(labels, rows, split, exclude_gate_only=False):
    out = set()
    for r in rows:
        u = r["unit_id"]
        if u in labels and labels[u].get("split") == split:
            if any(f.get("severity") == "重大" and not (exclude_gate_only and f.get("gate_only")) for f in r["flags"]):
                out.add(u)
    return out


def configs(split):
    s = split + "_p4"
    sp = {"holdout": "holdout_p4", "synthetic_holdout": "synthetic_holdout_p4"}[split]
    return [
        ("D0(rollbackのみ)", rows_of("d0_none_" + sp), True),
        ("D2 1rep", rows_of("d2_%s_%s" % (MODEL, sp)), False),
        ("D1v2 gate+因果", rows_of("d1v2_%s_%s" % (MODEL, sp)), False),
        ("C_main = D0rb ∪ D2", rows_of("d3_d0rb_d2_%s_%s" % (MODEL, sp)), False),
        ("D0rb ∪ D1v2", rows_of("d3_d0rb_d1v2_%s_%s" % (MODEL, sp)), False),
        ("D0rb ∪ D2 ∪ D1v2", rows_of("d3_all_%s_%s" % (MODEL, sp)), False),
    ]


def main():
    labels = json.load(open(os.path.join(CB, "casebank_01_labels.json"), encoding="utf-8"))
    chk = {c["case_id"]: c for c in json.load(open(os.path.join(CB, "checker_reference_01.json"), encoding="utf-8"))["cases"]}
    out = {}
    L = ["# P4_RESULT_01: 保留セット最終評価(1回のみ。構成はP3で確定したものを変更していない)", "",
         "- モデル gpt-6.1-sol。casebank: 保留37件(重大11/非重大26) + 合成保留7件。構成: C_main=D0rollback ∪ D2(1rep)、副=D1v2(D0ゲート+因果創作 各Flag上限3)、和集合。",
         "- **K01(rf_y84g5r)は D0 の方向語彙設計時に参照した『汚染済み回帰』**。Recall_human(主)は3件(K01/K02/K11)だが、K01を除いた2件版も併記し、K01は別掲する。",
         "- D1v2はD0ゲートで呼ぶタイプを絞り、因果創作は常に呼ぶ。ゲートで呼ばなかったタイプは未測定扱い。", ""]
    for split in ("holdout", "synthetic_holdout"):
        cf = configs(split)
        table = []
        for name, rows, ex in cf:
            if not rows:
                continue
            table.append((name, AG.aggregate(labels, rows, split=split, exclude_gate_only=ex)))
        out[split] = {n: r for n, r in table}
        L += ["## %s" % ("1. 保留(実記事37件)" if split == "holdout" else "2. 合成保留(7件、全て重大)"), "", AG.to_markdown(table), ""]
        L += ["### Flag精度(KPI2: Flagされた(unit,sent,type)のうち重大ケース上のFlagの割合)と、参考: severity無視版(事前登録のKPI定義はseverity=重大のFlagのみ。以下は定義外の参考)", "",
              "| 検出器 | Flag精度(重大のみFlag) | 参考: Recall_all(severity無視) | 参考: FPR_clear(severity無視) | FPR_boundary(同) | FPR_hardneg(同) |", "|---|---|---|---|---|---|"]
        for name, rows, ex in cf:
            if not rows:
                continue
            r1 = AG.aggregate(labels, rows, split=split, exclude_gate_only=ex)
            r2 = AG.aggregate(labels, rows, severe_only=False, split=split, exclude_gate_only=ex)
            fp = r1["flag_precision"]
            L.append("| %s | %s | %s | %s | %s | %s |" % (name, "-" if fp is None else "%.0f%%" % (100 * fp), AG.fr(r2["recall_all"]), AG.fr(r2["fpr_clear"]), AG.fr(r2["fpr_boundary"]), AG.fr(r2["fpr_hard_negative"])))
            out.setdefault(split + "_sev_agnostic", {})[name] = dict(flag_precision=fp, recall_all=r2["recall_all"], fpr_clear=r2["fpr_clear"], fpr_boundary=r2["fpr_boundary"], fpr_hardneg=r2["fpr_hard_negative"], missed=r2["missed_severe"])
        L.append("")
        if split == "holdout":
            lab2 ={k: v for k, v in labels.items() if k != CONTAM}
            t2 = [(n + " [K01除外]", AG.aggregate(lab2, rows, split=split, exclude_gate_only=ex)) for n, rows, ex in cf if rows]
            L += ["### K01(汚染済み回帰)を除外した版", "", "| 検出器 | Recall_human(主、K01除外) | Recall_all(K01除外) | FPR_clear | FPR_boundary | FPR_hardneg |", "|---|---|---|---|---|---|"]
            for n, r in t2:
                L.append("| %s | %s | %s | %s | %s | %s |" % (n, AG.fr(r["recall_human"]), AG.fr(r["recall_all"]), AG.fr(r["fpr_clear"]), AG.fr(r["fpr_boundary"]), AG.fr(r["fpr_hard_negative"])))
            out["holdout_noK01"] = {n: r for n, r in t2}
            L += ["", "### K01 の扱い(別掲)", ""]
            for n, rows, ex in cf:
                if rows:
                    h = hits_of(labels, rows, "holdout", ex)
                    L.append("- %s: K01(%s) = %s" % (n, CONTAM, "Flag" if CONTAM in h else "見逃し"))
            L.append("")
            # 閾値曲線(C_main)
            cm = next((rows for n, rows, ex in cf if n.startswith("C_main")), [])
            if cm:
                sw = AG.conf_sweep(labels, cm, (0.0, 0.3, 0.5, 0.7, 0.9), split=split)
                L += [AG.sweep_markdown("C_main (D0rb ∪ D2) 保留", sw), ""]
    # ---- 記事モード(保留側の既知重大元記事)
    man = {m["article_id"]: m for m in PR.load_manifest()}
    d0a, d2a = {}, {}
    for r in rows_of("d0_none_p4"):
        d0a[r["unit_id"]] = r
    for r in rows_of("d2rank_%s_p4" % MODEL):
        d2a[r["unit_id"]] = r
    cases = {c["case_id"]: c for c in json.load(open(os.path.join(CB, "casebank_01.json"), encoding="utf-8"))["cases"]}
    art_cases = {"holdout_meta_refresh_run03_b1b": ["rf_y84g5r"], "holdout_ai_control_jb9k_b1b": ["rf_emcgyx"], "holdout_space_p2rep2_ja": ["rf_hdr8y4"],
                 "holdout_ai_control_p2rep1_b1b": ["rf_7suvyn", "rf_qupxd4"], "holdout_hormuz_T0M0rep2_b1b": ["rf_665ga9"],
                 "holdout_hormuz_an3_b1b": ["rf_t9nxuv"], "holdout_hormuz_b3div_run02_b1b": ["rf_p4mtyd"]}
    import p3_aggregate_01 as P3
    L += ["## 3. 記事モード(保留側の既知重大元記事7本、C_main = D0rb ∪ D2rank上位3、Recall@top3=文脈内)", "",
          "| 記事 | 既知重大(case) | ラベル根拠/分割 | 文の位置 | D2rank順位(top3) | ±2文窓内 | D0 rollback Flag | C_main Flag固有文数 | Checker(Production単一run) |",
          "|---|---|---|---|---|---|---|---|---|"]
    a_rec = []
    for aid, cids in art_cases.items():
        if aid not in d2a:
            continue
        u = PR.build_unit(man[aid])
        texts = [s["text"] for s in u["sentences"]]
        fl = P3.cmain_flags(d0a.get(aid), d2a[aid])
        sid = lambda e: P3.sid_num(e["sentence_id"]) - 1  # noqa: E731
        d2pos = {P3.sid_num(f["sentence_id"]) - 1: f["rank"] for f in d2a[aid]["flags"]}
        d0pos = {P3.sid_num(e["sentence_id"]) - 1 for e in fl if "d0rb" in e["src"]}
        for cid in cids:
            pos = AG.locate_sentence(texts, cases[cid]["sentence"])
            lab = labels[cid]
            win = None
            if pos is not None:
                win = any(abs(sid(e) - pos) <= 2 for e in fl)
            a_rec.append(dict(article=aid, case=cid, basis=lab["label_basis"], split=lab["split"], pos=pos, d2rank=d2pos.get(pos) if pos is not None else None,
                              in_top3=(pos in d2pos) if pos is not None else None, window=win, d0=(pos in d0pos) if pos is not None else None,
                              n_flags=len(fl), checker=chk[cid]["outcome"]))
            L.append("| %s | %s | %s/%s | %s | %s | %s | %s | %d | %s |" % (aid, cid, lab["label_basis"], lab["split"], "s%d" % (pos + 1) if pos is not None else "未特定",
                     d2pos.get(pos, "-") if pos is not None else "-", "YES" if win else ("NO" if win is not None else "-"), "あり" if (pos is not None and pos in d0pos) else "なし", len(fl), chk[cid]["outcome"]))
    hold_recs = [r for r in a_rec if r["split"] == "holdout" and r["pos"] is not None]
    k = sum(1 for r in hold_recs if r["in_top3"])
    kw = sum(1 for r in hold_recs if r["window"])
    k_noK01 = [r for r in hold_recs if r["case"] != CONTAM]
    L += ["", "- **保留重大の記事モード Recall@top3(D2rank上位3、位置特定できた保留重大 %d件) = %d/%d**、±2文窓 %d/%d。K01除外 %d/%d。" % (
        len(hold_recs), k, len(hold_recs), kw, len(hold_recs), sum(1 for r in k_noK01 if r["in_top3"]), len(k_noK01)),
        "- rf_qupxd4 はdev分割の重大だが、同じ記事に保留重大 rf_7suvyn があるため保留側として評価した(devとしてはP3で使っていない)。上の分母は保留分割(split=holdout)のみ。",
        "- unlocated(記事ファイル未保存): rf_nck2y6/rf_fmu3aa/rf_tcdxe4/rf_vph9nb は記事モードでは測れない(casebankモードのみ)。", ""]
    out["article_mode"] = a_rec
    out["article_flag_counts"] = {aid: len(P3.cmain_flags(d0a.get(aid), d2a[aid])) for aid in d2a}
    # ---- Checker比較(保留重大11件、非重大26件)
    def checker_detect(cid):
        c = chk[cid]
        o = c["outcome"]
        if o == "BLOCKING":
            return True
        if o in ("NONBLOCKING", "NOT_CANDIDATE", "DEVCHECK_MAJOR_STOP"):
            return False if o != "DEVCHECK_MAJOR_STOP" else True
        ts = c.get("trial_summary") or {}
        if isinstance(ts, dict) and ts.get("runs"):
            return ts["blocking_any_cycle"] / float(ts["runs"]) >= 0.5
        return None  # 比較対象外(JA/未実行)
    L += ["## 4. Checker参考との並置(保留重大)", "",
          "- Checker検出の定義: Production単一run BLOCKING=検出 / NONBLOCKING・NOT_CANDIDATE=見逃し / Trial多runのみは blocking_any_cycle/runs >= 50% なら検出 / JA・Checker未実行は比較対象外(n/a)。",
          "- 注意(選択バイアス): casebankの重大はCheckerが浮上させた文に偏る(CHECKER_REFERENCE §0)。Checker側のRecallは有利に出る。", "",
          "| case | 型 | 根拠 | Checker | C_main(D0rb∪D2) | D1v2 | 全合算(+D1v2) |", "|---|---|---|---|---|---|---|"]
    sp = "holdout_p4"
    h_cm = hits_of(labels, rows_of("d3_d0rb_d2_%s_%s" % (MODEL, sp)), "holdout")
    h_d1 = hits_of(labels, rows_of("d1v2_%s_%s" % (MODEL, sp)), "holdout")
    h_all = hits_of(labels, rows_of("d3_all_%s_%s" % (MODEL, sp)), "holdout")
    sev = [k for k, v in labels.items() if v["split"] == "holdout" and v["label"].startswith("重大")]
    cat = {"cm": {"both": 0, "flagger_only": 0, "checker_only": 0, "neither": 0, "na": 0}, "all": {"both": 0, "flagger_only": 0, "checker_only": 0, "neither": 0, "na": 0}}
    for cid in sev:
        cd = checker_detect(cid)
        for key, h in (("cm", h_cm), ("all", h_all)):
            if cd is None:
                cat[key]["na"] += 1
            else:
                f = cid in h
                cat[key]["both" if (f and cd) else "flagger_only" if f else "checker_only" if cd else "neither"] += 1
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (cid, labels[cid].get("accident_type"), labels[cid]["label_basis"], {True: "検出", False: "見逃し", None: "n/a"}[cd],
                 "Flag" if cid in h_cm else "-", "Flag" if cid in h_d1 else "-", "Flag" if cid in h_all else "-"))
    L += ["", "| 集合 | 両方拾った | Flaggerだけ | Checkerだけ | どちらも拾えず | 比較対象外 |", "|---|---|---|---|---|---|"]
    for key, nm in (("cm", "C_main(D0rb∪D2)"), ("all", "全合算(D0rb∪D2∪D1v2)")):
        c = cat[key]
        L.append("| %s | %d | %d | %d | %d | %d |" % (nm, c["both"], c["flagger_only"], c["checker_only"], c["neither"], c["na"]))
    out["checker_compare_severe"] = cat
    neg = [k for k, v in labels.items() if v["split"] == "holdout" and v["label"].startswith("非重")]
    nc = {"cm": 0, "all": 0, "chk": 0, "chk_n": 0, "n": len(neg)}
    for cid in neg:
        nc["cm"] += int(cid in h_cm)
        nc["all"] += int(cid in h_all)
        cd = checker_detect(cid)
        if cd is not None:
            nc["chk_n"] += 1
            nc["chk"] += int(cd)
    L += ["", "- 非重大(保留26件)の誤検出: C_main %d/%d、全合算 %d/%d、Checker(参考、比較可能%d件中) %d。Checkerの『誤検出』は**BLOCKING/MAJOR STOP**で、Flaggerの『Flag』とは意味が異なる(Flaggerは人間確認依頼で、合否に使わない)。" % (
        nc["cm"], nc["n"], nc["all"], nc["n"], nc["chk_n"], nc["chk"]), ""]
    out["checker_compare_nonsevere"] = nc
    # ---- Recall@Flag数の費用
    # ---- S0反転時の再計算(事前登録規則)
    L += ["## 5. S0_USER_CHECK 反転時の再計算(ユーザー回答待ち。S0-1=rf_aennw4[保留]、S0-2=rf_xyw4mp[dev]、S0-3=rf_8fbz5r[保留])", "",
          "| 反転対象 | 対象分割 | 構成 | Recall_all | Recall_human | FPR_boundary |", "|---|---|---|---|---|---|"]
    s0 = {}
    for flip, label in ((("S0-1",), "S0-1のみ"), (("S0-3",), "S0-3のみ"), (("S0-1", "S0-3"), "S0-1+S0-3"), (("S0-1", "S0-2", "S0-3"), "全て")):
        for name, rows, ex in configs("holdout"):
            if name.startswith(("C_main", "D0rb ∪ D2 ∪")) and rows:
                r = AG.aggregate(labels, rows, split="holdout", s0_flip=flip, exclude_gate_only=ex)
                L.append("| %s | holdout | %s | %s | %s | %s |" % (label, name, AG.fr(r["recall_all"]), AG.fr(r["recall_human"]), AG.fr(r["fpr_boundary"])))
                s0[label + "|" + name] = r
    L.append("")
    out["s0"] = {k: {kk: v[kk] for kk in ("recall_all", "recall_human", "fpr_boundary", "missed_severe")} for k, v in s0.items()}
    # ---- 費用
    tot = {}
    for line in open(os.path.join(HERE, "cost_ledger.jsonl"), encoding="utf-8"):
        if not line.strip():
            continue
        e = json.loads(line)
        if str(e.get("set", "")).endswith("p4") or e.get("set") in ("p4",):
            tot[e["detector"]] = tot.get(e["detector"], 0) + (e.get("cost_jpy") or 0)
    L += ["## 6. 費用(P4、台帳)", ""] + ["- %s: ¥%.2f" % (k, v) for k, v in sorted(tot.items())] + ["- P4合計 ¥%.2f" % sum(tot.values())]
    out["cost_p4"] = tot
    open(os.path.join(RES, "P4_RESULT_01.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(out, open(os.path.join(RES, "P4_RESULT_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("\n".join(L))


if __name__ == "__main__":
    main()
