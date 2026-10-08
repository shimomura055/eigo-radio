# -*- coding: utf-8 -*-
"""V1(M1): 要約MAJOR 14世代(S0 §3)+EV-28 を fixture に、保存済み英語本文・JA R2・台帳・attempt1指摘を入力として
要約だけを新方式(OPEN243_M1相当、runnerのopen243_m1_summary_only_retryをそのまま呼ぶ)で再生成→EN deviation checkを実行する。
全体生成はしない。使用model=gpt-6-luna(登録済み単価)のみ。

実行: .venv/Scripts/python.exe er052_output/open243_translation_ng_analysis_01/trial_m123_01/v1_summary_regen.py [--phase A|B] [--only G01,G02]
  phase A: 旧check(OPEN243_M2未設定)で 腕F(初回=JA+台帳入力・must-fixなし)と腕R(attempt1指摘付き最大2回、本番と同じ関数)
  phase B: 腕Rの最終本文をOPEN243_M2=1のcheckで再判定(M1+M2併用)
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import er012_e_family_entertainment_two_level_runner_01 as runner  # noqa: E402

R = "er052_output/"
GENS = [
    ("G01", R + "all6_writer_redesign_necessity_01/runs/meta/control/b1__all6__r2", "b1b"),
    ("G02", R + "all6_writer_redesign_necessity_01/runs/meta/control/b2__all6__r2", "b1b"),
    ("G03", R + "all6_writer_redesign_necessity_01/runs/meta/control/b3__all6__r1", "b1b"),
    ("G04", R + "all6_writer_redesign_necessity_01/runs/meta/control/b3__all6__r2", "b1b"),
    ("G05", R + "all6_writer_redesign_necessity_01/runs/space_weapons/control/b3__baseline__r1", "a2"),
    ("G06", R + "factlock_writer_trial_01/runs/hormuz/control/b1__factlock__r2", "b1b"),
    ("G07", R + "factlock_writer_trial_01/runs/meta/control/b1__factlock__r1", "b1b"),
    ("G08", R + "factlock_writer_trial_01/runs/meta/control/b1__factlock__r2", "b1b"),
    ("G09", R + "factlock_writer_trial_01/runs/meta/control/b4__factlock__r1", "b1b"),
    ("G10", R + "factlock_writer_trial_01/sweep_01/runs/hormuz/control/b4__S2__r1", "b1b"),
    ("G11", R + "factlock_writer_trial_01/sweep_01/runs/meta/control/b2__S11__r1", "b1b"),
    ("G12", R + "factlock_writer_trial_01/sweep_01/runs/meta/control/b2__S3__r1", "b1b"),
    ("G13", R + "factlock_writer_trial_01/sweep_01/runs/space_weapons/control/b3__S10__r1", "b1b"),
    ("G14", R + "gpt6_wiring_e2e_01/run_01", "b1b"),
    ("EV28", R + "all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1", "b1b"),
]
# 従来方式(本文ごとのmust-fix再生成1回)の結果(S0_AUDIT §3-1: 解消=attempt2でCOMPLIANT)
CONVENTIONAL_RESOLVED = {"G01": True, "G04": True, "G05": True, "G10": True, "G11": True, "G13": True,
                         "G02": False, "G03": False, "G06": False, "G07": False, "G08": False, "G09": False,
                         "G12": False, "G14": False}
V1_DIR = f"{C.TRIAL}/v1"


def load_fixture(gen, run, sub):
    ad = f"{run}/{sub}/audit"
    a1 = sorted(glob.glob(f"{ad}/deviation_checks/*attempt1.json"))
    fx = {"gen": gen, "run": run, "sub": sub}
    if a1:
        d = json.load(open(a1[0], encoding="utf-8"))
        parts = C.parse_attempt_prompt(d["prompt"])
        fx.update(parts)
        fx["attempt1_file"] = a1[0]
        fx["attempt1_status"] = d["parsed"]["overall_status"]
        fx["attempt1_majors"] = [x for x in d["parsed"]["deviations"] if x.get("severity") == "MAJOR"]
        fx["attempt1_all"] = d["parsed"]["deviations"]
    else:  # EV-28: attempt1ファイル無し(COMPLIANT)。台帳・JA・EN本文を保存物から直接読む
        fx["ledger"] = open(f"{run}/research_ledger/verified_fact_ledger.txt", encoding="utf-8").read()
        fx["article"] = open(f"{run}/{sub}/article.md", encoding="utf-8").read()
        fx["ja"] = open(f"{run}/ja_writer/revision2.md", encoding="utf-8").read()
        fx["attempt1_file"] = None
        fx["attempt1_status"] = "LEDGER_COMPLIANT(stored deviation_check.json)"
        fx["attempt1_majors"] = []
        fx["attempt1_all"] = json.load(open(f"{ad}/deviation_check.json", encoding="utf-8")).get("deviations", [])
    sp = C.split_article(fx["article"])
    assert sp, f"{gen}: article split failed"
    fx.update({"title": sp["title"], "body": sp["body"], "summary_attempt1": sp["summary"]})
    return fx


def phase_a(client, fx):
    gen = fx["gen"]
    out = {"gen": gen, "run": fx["run"], "attempt1_status": fx["attempt1_status"],
           "attempt1_summary": fx["summary_attempt1"],
           "attempt1_majors": [{"claim": d.get("claim_in_article"), "issue": d.get("issue"), "origin": d.get("origin"),
                                "flags": [k for k in vfl01_keys() if d.get(k)]} for d in fx["attempt1_majors"]],
           "attempt1_summary_only": runner.open243_majors_only_in_summary(
               fx["attempt1_majors"], fx["summary_attempt1"], fx["body"]) if fx["attempt1_majors"] else None}
    # ---- 腕F: 初回生成(JA+台帳入力、must-fixなし) -> 旧check ----
    C.check_budget()
    iol = C.adv_gen.generate_family_x_in_one_line(client, fx["title"], fx["body"], ja_text=fx["ja"], ledger_text=fx["ledger"])
    iol_cost = C.record_spend(f"v1.{gen}.F.iol", iol["model"], iol["usage"])
    textF = f"# {fx['title']}\n\n{fx['body']}\n\n## In one line\n{iol['text']}"
    devF = C.checked_deviation(client, fx["ledger"], textF, fx["ja"], f"v1.{gen}.F.check")
    out["armF"] = {"summary": iol["text"], "prompt": iol.get("prompt"), "iol_cost_jpy": iol_cost,
                   "check_cost_jpy": devF["cost_jpy"], "status": devF["parsed"]["overall_status"],
                   "deviations": C.dev_summary(devF), "n_major": sum(1 for d in devF["parsed"]["deviations"] if d["severity"] == "MAJOR")}
    # ---- 腕R: attempt1のMAJOR指摘をmust-fixとして渡す要約だけ再生成(最大2回、本番と同じ関数) ----
    if fx["attempt1_majors"]:
        must_fix = runner._must_fix_from_deviations(fx["attempt1_majors"])

        def dev_check_fn(text, prior):
            n = len(out.setdefault("_chk", []))
            out["_chk"].append(1)
            return C.checked_deviation(client, fx["ledger"], text, fx["ja"], f"v1.{gen}.R.check{n + 1}", prior_issues=prior)

        res = runner.open243_m1_summary_only_retry(client, ledger_text=fx["ledger"], ja_text=fx["ja"], title=fx["title"],
                                                    body=fx["body"], must_fix=must_fix, max_attempts=2, dev_check_fn=dev_check_fn)
        out.pop("_chk", None)
        atts = []
        for a in res["attempts"]:
            ic = C.record_spend(f"v1.{gen}.R.iol{a['attempt']}", a["iol"]["model"], a["iol"]["usage"])
            atts.append({"attempt": a["attempt"], "summary": a["summary"], "iol_cost_jpy": ic,
                         "check_cost_jpy": a["deviation"]["cost_jpy"], "status": a["overall_status"],
                         "all_prior_issues_resolved": a["all_prior_issues_resolved"], "n_major": a["n_major"],
                         "deviations": C.dev_summary(a["deviation"]), "prompt": a["iol"].get("prompt")})
        out["armR"] = {"success": res["success"], "reason": res["reason"], "attempts": atts,
                       "final_summary": res["attempts"][-1]["summary"], "final_text": res["final_text"],
                       "must_fix": must_fix}
    out["conventional_resolved"] = CONVENTIONAL_RESOLVED.get(gen)
    C.jdump(f"{V1_DIR}/{gen}_phaseA.json", out)
    return out


def vfl01_keys():
    return C.vfl01.DEVIATION_FLAG_KEYS


def phase_b(client, fx):
    gen = fx["gen"]
    pa = json.load(open(f"{V1_DIR}/{gen}_phaseA.json", encoding="utf-8"))
    out = {"gen": gen}
    if "armR" in pa:
        text = pa["armR"]["final_text"]
        dev = C.checked_deviation(client, fx["ledger"], text, fx["ja"], f"v1.{gen}.R.M2check")
        out["armR_M2"] = {"status": dev["parsed"]["overall_status"], "deviations": C.dev_summary(dev),
                          "n_major": sum(1 for d in dev["parsed"]["deviations"] if d["severity"] == "MAJOR"),
                          "check_cost_jpy": dev["cost_jpy"]}
    C.jdump(f"{V1_DIR}/{gen}_phaseB.json", out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["A", "B"], required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--threads", type=int, default=4)
    args = ap.parse_args()
    if args.phase == "B":
        os.environ["OPEN243_M2"] = "1"
    else:
        os.environ.pop("OPEN243_M2", None)
    only = set(x for x in args.only.split(",") if x)
    fxs = [load_fixture(*g) for g in GENS if not only or g[0] in only]
    client = C.vfl01.get_client()
    fn = phase_a if args.phase == "A" else phase_b
    with cf.ThreadPoolExecutor(max_workers=args.threads) as ex:
        futs = {ex.submit(fn, client, fx): fx["gen"] for fx in fxs}
        for f in cf.as_completed(futs):
            try:
                f.result()
                print("done", futs[f], "spend", round(C.total_spend(), 3), flush=True)
            except Exception as e:  # noqa: BLE001
                print("ERROR", futs[f], type(e).__name__, e, flush=True)
    print("TOTAL SPEND JPY", round(C.total_spend(), 3))


if __name__ == "__main__":
    main()
