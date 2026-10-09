# -*- coding: utf-8 -*-
"""FACTLOCK-ASTRA-E2E-TRIAL-01 委任_13: 最終集計(API 0、読取専用)。
既存 er052_factlock_astra_e2e_aggregate_01.py (§81行立て) を再利用し、全テーマ・旧4/新5層別・テーマ別/段別/腕別費用・
到達状態表・B3由来/台帳AMBIGUOUS由来の機械的候補を追加して AGGREGATE.md を作る。判定線の評価はしない。
使い方: .venv/Scripts/python.exe -X utf8 er052_factlock_astra_e2e_final_aggregate_01.py --root <runs> --out-dir <runs>/final_aggregate
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import er052_factlock_astra_e2e_aggregate_01 as A
import er052_factlock_astra_e2e_runner_01 as R

OLD4 = ["meta", "hormuz", "space_weapons", "small_bag"]
NEW5 = ["byd_recall", "central_bank_mortgage", "openai_copyright", "semiconductor_earnings", "streaming_price"]
ASTRA_STAGES = ("new_r1", "new_r2")


def ledger(root):
    out = []
    for fn in sorted(os.listdir(root)):
        if fn.startswith("ledger_costs_worker") and fn.endswith(".jsonl"):
            out += R.read_jsonl(f"{root}/{fn}")
    return out


def cost_tables(root):
    es = [e for e in ledger(root) if e["kind"] == "settle"]
    tot = {"raw": 0.0, "guard": 0.0}
    by = {"arm": {}, "theme": {}, "stage": {}, "theme_arm": {}}
    astra = {"raw": 0.0, "guard": 0.0}
    for e in es:
        tot["raw"] += e["jpy_raw"]
        tot["guard"] += e["jpy_guard"]
        for k, key in (("arm", e["arm"]), ("theme", e["theme"]), ("stage", e["stage"]), ("theme_arm", f"{e['theme']}/{e['arm']}")):
            d = by[k].setdefault(key, {"raw": 0.0, "guard": 0.0})
            d["raw"] += e["jpy_raw"]
            d["guard"] += e["jpy_guard"]
        if e["stage"] in ASTRA_STAGES:
            astra["raw"] += e["jpy_raw"]
            astra["guard"] += e["jpy_guard"]
    # B1再支出(推定): b1_recovery event 以降の同テーマ new 腕の再実行段(new_r0..new_shadow)の確定額
    b1 = {"raw": 0.0, "guard": 0.0, "detail": []}
    resets = {"new_r0", "new_r1", "new_r2", "new_ii", "new_en_adv", "new_en_std", "new_shadow"}
    for t in sorted(os.listdir(root)):
        p = f"{root}/{t}/new/state.jsonl"
        if not os.path.exists(p):
            continue
        evs = R.read_jsonl(p)
        for i, ev in enumerate(evs):
            if ev["ev"] == "b1_recovery":
                nxt = next((x for x in evs[i + 1:] if x["ev"] == "reset"), None)
                ts0 = ev["ts"]
                sub = [e for e in es if e["theme"] == t and e["arm"] == "new" and e["stage"] in resets and e["ts"] >= ts0]
                r, g = sum(e["jpy_raw"] for e in sub), sum(e["jpy_guard"] for e in sub)
                b1["raw"] += r
                b1["guard"] += g
                b1["detail"].append({"theme": t, "trigger": ev.get("trigger"), "after_ts": ts0, "raw": round(r, 2), "guard": round(g, 2)})
    rnd = lambda d: {k: (round(v, 2) if isinstance(v, float) else v) for k, v in d.items()}   # noqa: E731
    return {"total": rnd(tot), "astra": rnd(astra), "b1_estimated": rnd(b1),
            **{k: {kk: rnd(vv) for kk, vv in sorted(v.items())} for k, v in by.items()}}


def run_table(root, themes):
    rows = []
    for t in themes:
        for arm in ("new", "old"):
            if not os.path.isdir(f"{root}/{t}/{arm}"):
                rows.append({"theme": t, "arm": arm, "missing": True})
                continue
            rec = A.arm_record(root, t, arm)
            ad = f"{root}/{t}/{arm}"
            amb = R.rj(f"{root}/{t}/shared/annotation.json") if os.path.exists(f"{root}/{t}/shared/annotation.json") else {}
            rec["n_unmapped_b3"] = len(amb.get("unmapped_claims", []))
            rec["_dir"] = ad
            rows.append(rec)
    return rows


def status_of(rec, stage_candidates):
    for s in stage_candidates:
        if s in rec["stages"]:
            return rec["stages"][s]
    return "-"


def reach_row(rec):
    arm = rec["arm"]
    ja = status_of(rec, ["new_r2"] if arm == "new" else ["old_ja"])
    if arm == "new" and rec["stages"].get("new_r0") == "stop":
        ja = "stop(R0)"
    fc = rec["ja_fc"]
    out = {"JA": ja, "JA_FC_major(R2)": fc.get("n_major")}
    for lvl, _, short in A.LEVELS:
        stg = f"new_en_{short}" if arm == "new" else f"old_{short}"
        c = rec["checker"].get(lvl)
        out[lvl] = {"EN": rec["stages"].get(stg, "-"), "Checker": (c or {}).get("final_state", "-")}
    sh = "new_shadow" if arm == "new" else "old_shadow"
    out["shadow"] = rec["stages"].get(sh, "-")
    return out


def b3_candidates(root, rows):
    """機械的な「候補」: (1) 台帳AMBIGUOUS由来=Checker cycle1 stage2 MAJOR で related_fact_id が当該テーマのambiguous_selected、
    (2) B3由来=テーマに unmapped_claims がある場合の cycle1 stage2 MAJOR で related_fact_id が空 or unsupported_new_claim=True。
    EN/JA言語差で本文照合はできないため確定ではない(要Fable/人手突合)。"""
    amap = R.rj("er052_output/factlock_astra_e2e_trial_01/annotation/AMBIGUOUS_FACT_MAP.json")
    out = []
    for rec in rows:
        if rec.get("missing"):
            continue
        t, arm = rec["theme"], rec["arm"]
        amb = set((amap.get(t) or {}).get("ambiguous_selected", []))
        for lvl, c in rec["checker"].items():
            cj = A._safe(f"{rec['_dir']}/checker/{lvl}.json") or {}
            cyc = cj.get("cycles") or []
            if not cyc:
                continue
            majors = [s for s in (cyc[0].get("stage2_results") or []) if (s.get("dev") or {}).get("severity") == "MAJOR"]
            n_amb = sum(1 for s in majors if s.get("related_fact_id") in amb)
            n_b3 = sum(1 for s in majors if rec["n_unmapped_b3"] and ((not s.get("related_fact_id")) or (s.get("dev") or {}).get("unsupported_new_claim")))
            out.append({"theme": t, "arm": arm, "level": lvl, "cycle1_stage2_major": len(majors), "ambiguous_candidate": n_amb, "b3_candidate": n_b3,
                        "theme_unmapped_claims": rec["n_unmapped_b3"], "theme_ambiguous_selected": sorted(amb)})
    return out


def shadow_txt(r):
    m1a, m1b = r["shadow"].get("m1a"), r["shadow"].get("m1b")
    if not m1a and not m1b:
        return "-"
    alt = ((m1a or {}).get("alt_check") or {}).get("overall_status")
    return f"alt={alt}({(m1a or {}).get('alt_rule')}) / m1b_fired={(m1b or {}).get('fired_in_arm')}"


def md_table(head, rows):
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.chdir(R.HERE)
    root = a.root
    all_themes = [t for t in OLD4 + NEW5 if os.path.isdir(f"{root}/{t}/shared")]
    agg_all = A.aggregate(root)
    agg_old = A.aggregate(root, OLD4)
    agg_new = A.aggregate(root, NEW5)
    rows = run_table(root, all_themes)
    ct = cost_tables(root)
    b3c = b3_candidates(root, rows)
    es = ledger(root)
    ts = sorted(e["ts"] for e in es)
    out = {"themes": all_themes, "cost": ct, "aggregate_all": agg_all, "aggregate_old4": agg_old, "aggregate_new5": agg_new,
           "reach": {f"{r['theme']}/{r['arm']}": (reach_row(r) if not r.get("missing") else "missing") for r in rows},
           "b3_ambiguous_candidates": b3c, "first_ledger_ts": ts[0] if ts else None, "last_ledger_ts": ts[-1] if ts else None}
    R.wj(f"{a.out_dir}/aggregate_final.json", out)

    L = ["# E2E 最終集計(委任_13、自動生成・判定線評価なし)", "", f"root: `{root}` / テーマ({len(all_themes)}): {', '.join(all_themes)}",
         f"予定run数 = 9テーマ x 2腕 x 2レベル = 36 run(旧4=16、新5=20)。分母は予定run数、STOPは独立カテゴリ。", ""]
    L += ["## 1. 到達状態表(JA / EN / Checker最終状態)", ""]
    hd = ["テーマ", "腕", "JA", "JA FC MAJOR(R2)", "shadow", "Adv EN", "Adv Checker", "Std EN", "Std Checker"]
    tr = []
    for r in rows:
        if r.get("missing"):
            tr.append([r["theme"], r["arm"], "(未実行)", "", "", "", "", "", ""])
            continue
        x = reach_row(r)
        tr.append([r["theme"], r["arm"], x["JA"], x["JA_FC_major(R2)"], x["shadow"], x["advanced"]["EN"], x["advanced"]["Checker"], x["standard"]["EN"], x["standard"]["Checker"]])
    L += md_table(hd, tr) + [""]

    def sect(title, agg):
        n, o = agg["arms"].get("new"), agg["arms"].get("old")
        L.append(f"## {title}")
        L.append("")
        L.append(f"テーマ: {', '.join(agg['themes'])}(各腕予定run {agg['planned_runs_per_arm']})")
        L.append("")
        tmp = A.to_markdown(agg).split("\n")
        # 指標表のみ抜粋
        L.extend([l for l in tmp if l.startswith("|")])
        L.append("")
        if n and o:
            L.append("追加(段別EN内訳・M1/影・shadow):")
            L.append("")
            for arm, x in (("新腕", n), ("旧腕", o)):
                L.append(f"- {arm}: EN adv STOP {x['H_en']['advanced']['stop']} / EN std STOP {x['H_en']['standard']['stop']} / "
                         f"ja_source MAJOR(adv,std)={x['H_en']['advanced']['ja_source_major_total']},{x['H_en']['standard']['ja_source_major_total']} / "
                         f"M1発火(adv,std)={x['H_en']['advanced']['m1_fired']},{x['H_en']['standard']['m1_fired']} / 人手介入内訳={x['L_human_intervention']} / "
                         f"shadow初回STOP={x['N_shadow_stop_b1']['shadow_stop_initial']} 最終={x['N_shadow_stop_b1']['shadow_stop_final']} / B1回復={x['N_shadow_stop_b1']['b1_recoveries']} 拒否={x['N_shadow_stop_b1']['b1_denied']} / "
                         f"M3保護={x['I_m3']['protected_keys_total']} 影={x['I_m3']['m3_would_protect_changed_actor_total(旧腕での影の対照)']} / R0 echo残存={x['R0_echo_remaining_in_final']}")
            L.append("")
        return

    sect("2. 全9テーマ(§81行立て+追加指標)", agg_all)
    sect("3. 層別: 旧4テーマ(meta/hormuz/space_weapons/small_bag)", agg_old)
    sect("4. 層別: 新5テーマ(byd_recall/central_bank_mortgage/openai_copyright/semiconductor_earnings/streaming_price)", agg_new)

    L += ["## 5. 新規具体主張(ii)・JA字数(テーマ別)", ""]
    hd = ["テーマ", "腕", "(ii)最終", "(ii)差vs R0", "JA字数", "初回JA_RECHECK", "M1発火(adv/std)", "影の対照(m1a alt判定 / m1b)"]
    tr = []
    for r in rows:
        if r.get("missing"):
            continue
        tr.append([r["theme"], r["arm"], r["ii_new_specific_final"], r["ii_delta_vs_r0"], r["ja"].get("chars"), r["first_ja_recheck"],
                   f"{r['en']['advanced'].get('m1_fired')}/{r['en']['standard'].get('m1_fired')}", shadow_txt(r)])
    L += md_table(hd, tr) + [""]

    L += ["## 6. B3由来 / 台帳AMBIGUOUS由来(機械的候補、確定ではない)", "",
          "注: Checker cycle1 stage2 MAJOR を母集団とし、AMBIGUOUS候補=related_fact_idが当該テーマのAMBIGUOUS選択ID、B3候補=B3 unmapped_claimsを持つテーマで"
          "related_fact_id空 or unsupported_new_claim。EN/JA言語差のため本文照合は未実施、確定は人手/Fable突合。", ""]
    L += md_table(["テーマ", "腕", "レベル", "cycle1 stage2 MAJOR", "AMBIGUOUS候補", "B3候補", "テーマunmapped数", "テーマAMBIGUOUS選択"],
                  [[x["theme"], x["arm"], x["level"], x["cycle1_stage2_major"], x["ambiguous_candidate"], x["b3_candidate"], x["theme_unmapped_claims"], x["theme_ambiguous_selected"]] for x in b3c]) + [""]
    L += [f"合計(候補): AMBIGUOUS 新{sum(x['ambiguous_candidate'] for x in b3c if x['arm']=='new')}/旧{sum(x['ambiguous_candidate'] for x in b3c if x['arm']=='old')} / "
          f"B3 新{sum(x['b3_candidate'] for x in b3c if x['arm']=='new')}/旧{sum(x['b3_candidate'] for x in b3c if x['arm']=='old')}", ""]

    L += ["## 7. 費用(円。raw=登録単価xトークン、guard=astra分x1.5)", "",
          f"- 本台帳合計(G1+G2): raw {ct['total']['raw']} / guard {ct['total']['guard']}",
          f"- Astra段(new_r1+new_r2): raw {ct['astra']['raw']} / guard {ct['astra']['guard']}",
          f"- B1回復の再支出(推定、b1_recovery以降の同テーマ新腕再実行段): raw {ct['b1_estimated']['raw']} / guard {ct['b1_estimated']['guard']} 内訳 {ct['b1_estimated']['detail']}",
          f"- Trial累計(Stage R raw 178.99込み): raw {round(ct['total']['raw'] + 178.99, 2)}", "", "腕別:", ""]
    L += md_table(["腕", "raw", "guard"], [[k, v["raw"], v["guard"]] for k, v in ct["arm"].items()]) + ["", "テーマ別:", ""]
    L += md_table(["テーマ", "raw", "guard"], [[k, v["raw"], v["guard"]] for k, v in ct["theme"].items()]) + ["", "テーマ/腕別:", ""]
    L += md_table(["テーマ/腕", "raw", "guard"], [[k, v["raw"], v["guard"]] for k, v in ct["theme_arm"].items()]) + ["", "段別:", ""]
    L += md_table(["段", "raw", "guard"], [[k, v["raw"], v["guard"]] for k, v in ct["stage"].items()]) + [""]
    L += [f"台帳の最初/最後のts: {out['first_ledger_ts']} - {out['last_ledger_ts']}", "",
          "盲検ラベル・Fable突合が必要な欄(真に重大/不要/F重大軽微)は未計測(None)。判定線の評価は本書では行わない。"]
    R.wt(f"{a.out_dir}/AGGREGATE.md", "\n".join(L) + "\n")
    print("written", a.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
