# -*- coding: utf-8 -*-
"""完走後の集計: Note到達(Meta)、cost集計、Checker発火概況、Gate STOP/再実行/infra、メモリ、RUN_CHECK.md生成(0円)。"""
import csv, glob, json, os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "er052_output/open233_allfact_note_e2e_02/tools"))
sys.path.insert(0, os.path.join(ROOT, "docs/pm/control_checker_polysemy_trial_01/tools"))
import check_brief_transfer as cbt
import driver_ccp as drv
B, RUNS = drv.B, drv.RUNS


def jl(p):
    return json.load(open(p, encoding="utf-8"))


def main():
    res = jl(f"{RUNS}/driver_result.json")
    rows, notes = [], {}
    for (s, v, k) in drv.tasks():
        d = drv.rep_dir(s, v, k)
        cost = jl(f"{d}/cost.json")
        by = cost["by_stage_jpy"]
        p1 = round(sum(x for n, x in by.items() if n != "advanced"), 4)
        en = round(by.get("advanced", 0.0), 4)
        ch = jl(glob.glob(f"{d}/checker/runs/*.json")[0])
        chc = ch.get("run_cost_jpy", 0.0)
        cyc = ch.get("cycles") or []
        nrw = sum(len(c.get("rewrite_records") or []) for c in cyc)
        rows.append({"run": f"{s}/{v}/rep{k}", "phase1_jpy": p1, "en_jpy": en, "checker_jpy": round(chc, 4),
                     "total_jpy": round(p1 + en + chc, 4), "checker_final_state": ch.get("final_state"),
                     "checker_cycles": len(cyc), "rewrite_records": nrw})
        if s == "meta":
            r = cbt.check(f"{d}/storyline_b3/selected_brief.md", f"{d}/research_ledger/verified_fact_ledger.txt")
            json.dump(r, open(f"{d}/brief_transfer_check.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            pf = r["per_fact"].get("MUSE-HC-012")
            prov = jl(f"{d}/nb_provenance_phase1.json")
            notes[f"{s}/{v}/rep{k}"] = {"HC-012_selected": pf is not None, "poly_note_reached": bool(pf and pf["poly_note"]),
                                        "existing_note_reached": bool(pf and pf["existing_note"]), "both": bool(pf and pf["PASS"]),
                                        "transfer_block_sha256": (prov.get("transfer_block_sha256") or "")[:12],
                                        "research_calls": prov.get("research_calls")}
    tot = [r["total_jpy"] for r in rows]
    disk_total, disk_max = drv_all = drv.all_costs()
    failed_dirs = sorted(glob.glob(f"{RUNS}/*/*/rep*_failed_*"))
    mem = list(csv.DictReader(open(f"{RUNS}/mem_samples.csv", encoding="utf-8")))
    maxws = max(int(m["max_ws_bytes"] or 0) for m in mem) / 1e6
    maxpv = max(int(m["max_private_bytes"] or 0) for m in mem) / 1e6
    minfree = min(int(m["free_phys_kb"] or 0) for m in mem) / 1024
    maxn = max(int(m["n_python"] or 0) for m in mem)
    attempts_summary = {k: [(a["phase"], a["attempt"], a["rc"], a.get("failure_class")) for a in c["attempts"] if a["rc"] != 0 or a.get("failure_class")]
                        for k, c in res["cells"].items()}
    out = {"rows": rows, "n_completed": len(rows), "total_jpy_completed": round(sum(tot), 3),
           "avg_jpy": round(sum(tot) / len(tot), 3), "max_jpy": round(max(tot), 3), "disk_total_jpy_incl_failed": round(disk_total, 3),
           "phase1_sum": round(sum(r["phase1_jpy"] for r in rows), 3), "en_sum": round(sum(r["en_jpy"] for r in rows), 3),
           "checker_sum": round(sum(r["checker_jpy"] for r in rows), 3), "note_reach": notes, "failed_dirs": failed_dirs,
           "driver_state": res["state"], "history": res["history"], "attempt_problems": attempts_summary,
           "mem": {"max_ws_mb": round(maxws), "max_private_mb": round(maxpv), "min_free_phys_mb": round(minfree), "max_python_procs": maxn}}
    json.dump(out, open(f"{RUNS}/cost_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# RUN_CHECK: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_02 実行記録", "",
         f"- 完了run: {len(rows)}/18、driver_result finished_at={res.get('finished_at')}、driver state={res['state']}",
         f"- 降格履歴(workers): {res['history']}",
         f"- Gate STOP(1回目)数={res['state'].get('gate_stops_first')}、再実行数={res['state'].get('reruns')}、infra連続失敗={res['state'].get('consec_fail')}、失敗dir={failed_dirs}",
         f"- 失敗/非0 attempt: { {k: v for k, v in attempts_summary.items() if v} }",
         f"- メモリ(memmon): python子プロセス最大WS={round(maxws)}MB、最大Private={round(maxpv)}MB、OS空き物理最小={round(minfree)}MB、python同時最大={maxn}。1455/MemoryError検知={'あり' if res['state'].get('mem_runs') or any(h.get('mem_runs') for h in res['history']) else 'なし'}",
         f"- 費用: phase1(B3+JA)={out['phase1_sum']}円、EN={out['en_sum']}円、Checker={out['checker_sum']}円、完了18本総額={out['total_jpy_completed']}円(平均{out['avg_jpy']}・最大{out['max_jpy']})、ディスク全体(失敗試行含む)={out['disk_total_jpy_incl_failed']}円",
         "", "## run別", "| run | phase1 | EN | Checker | 計 | final_state | cycles | Rewrite件数 |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['run']} | {r['phase1_jpy']} | {r['en_jpy']} | {r['checker_jpy']} | {r['total_jpy']} | {r['checker_final_state']} | {r['checker_cycles']} | {r['rewrite_records']} |")
    L += ["", f"Checker発火(Rewrite>0)run数={sum(1 for r in rows if r['rewrite_records'] > 0)}/18、Rewrite総件数={sum(r['rewrite_records'] for r in rows)}",
          "", "## Meta Note到達(brief転記、check_brief_transfer.py)", "| run | HC-012選択 | 多義Note到達 | 既存notes到達 | 両方 | transfer_block_sha | research_calls |", "|---|---|---|---|---|---|---|"]
    for k, n in notes.items():
        L.append(f"| {k} | {n['HC-012_selected']} | {n['poly_note_reached']} | {n['existing_note_reached']} | {n['both']} | {n['transfer_block_sha256']} | {n['research_calls']} |")
    L.append(f"\nHC-012選択={sum(n['HC-012_selected'] for n in notes.values())}/10、多義Note到達={sum(n['poly_note_reached'] for n in notes.values())}/10、両方到達={sum(n['both'] for n in notes.values())}/10")
    open(f"{RUNS}/RUN_CHECK.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
