# -*- coding: utf-8 -*-
"""STAGE2-01 委任_02 測定(3): ①構造要素Rewrite→4照合→Recheck再実行(Trial専用、有料API)。
対象=devの構造要素(title/hook/in_one_line)にBLOCKING findingがある単位(保存済みcycle1)+②新構成でBLOCKINGに転じた構造要素claim+
回帰確認枠qvqc rep2(タイトル・Hook)。各対象を n回(既定3)、規則ON(OPEN233_STRUCTURAL_REWRITE_RULES+W1+W2)とOFF(現行相当)で実Rewriteし、
ONのみRecheck(構造要素の前後対つき)へ渡す。サンプルが小さいため有意差は言わない(件数報告のみ)。
使い方: python rewrite_stage3.py --tag-from v1 --n 3 --budget-jpy 180"""
import argparse
import concurrent.futures as cf
import glob
import json
import os
import pathlib
import re
import time

import replay_lib as L
import replay_stage2 as R

runner, cap2, OUT = L.runner, L.cap2, L.OUT
STRUCT = ("title", "hook", "in_one_line")
QVQC = "er052_output/open233_control_checker_polysemy_trial_01/runs/meta/nb/rep2"


def collect_targets(tag_from, kind="dev"):
    t = []
    runs = L.dev_runs(kind) + ([QVQC] if kind == "dev" else [])
    for rd in runs:
        run, ledger, art = L.load_run(rd)
        c1 = run["cycles"][0]
        seen = set()
        for sr in c1["stage2_results"]:
            if sr.get("section_type") in STRUCT and sr.get("materiality") == "BLOCKING" and sr.get("stage2_route") != "precheck_floor_bypass":
                t.append({"run": rd, "source": "saved_blocking", "claim": sr})
                seen.add(sr["claim_text"])
        f = OUT / ("replay_heldout" if kind == "heldout" else "replay_dev") / tag_from / (R.slug(rd) + ".json")
        if f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            saved_by_text = {sr["claim_text"]: sr for sr in c1["stage2_results"]}
            for x in d["results"]:
                if x["new"].get("section_type") in STRUCT and x["new"]["materiality"] == "BLOCKING" and x["claim_text"] not in seen:
                    sr = dict(saved_by_text.get(x["claim_text"]) or {})
                    if sr:
                        sr["materiality"] = "BLOCKING"
                        sr["rewrite_kind"] = sr.get("rewrite_kind") or "replace_with_ledger_value"
                        blk = runner.floor_verify_fact_block(ledger, (sr.get("dev") or {}).get("related_fact_id"))
                        hint, _ = runner.downgrade_verify_rewrite_hint(sr.get("dev") or {}, blk)
                        sr["rewrite_hint"] = hint or sr.get("rewrite_hint") or ""
                        t.append({"run": rd, "source": "new_config_blocking", "claim": sr})
    return t


def diff_flags(before, after, vocab, body):
    c = cap2.four_checks("title" if before.lstrip().startswith("#") else "hook", before, after, vocab, body)
    return {"violations": c["violations"], "new_subjects": c["new_subjects"], "bad_numbers": c["bad_numbers"],
            "polarity_changed": "polarity" in c["violations"]}


def one(client, tgt, rep, rules_on, budget):
    rd = tgt["run"]
    run, ledger, art = L.load_run(rd)
    sr = tgt["claim"]
    os.environ[cap2.SW_STRUCT_RULES] = "1" if rules_on else "0"
    state, ce, call_log = L.new_state(), [0], []
    fixture = {"ledger_text": ledger, "article_text": art}
    claim_rec = {"claim_text": sr["claim_text"], "rewrite_kind": sr.get("rewrite_kind") or "replace_with_ledger_value",
                 "materiality": "BLOCKING", "basis": sr.get("basis") or "ledger_claim", "rewrite_hint": sr.get("rewrite_hint") or "",
                 "dev": sr.get("dev") or {}}
    res = runner.rewrite_ranges_ladder(client, state, ce, call_log, f"s3_{R.slug(rd)[:30]}_{rep}_{int(rules_on)}", fixture,
                                       "article_text", claim_rec)
    h = res.get("handoff") or {}
    before_sents = len(re.findall(r"[.!?](?:\s|$)", art))
    after_sents = len(re.findall(r"[.!?](?:\s|$)", res["updated_text"]))
    vocab = cap2.proper_noun_vocab(ledger, art)
    out = {"run": rd, "source": tgt["source"], "claim": sr["claim_text"], "section_type": sr.get("section_type"), "rep": rep,
           "rules_on": rules_on, "guard_ok": res["guard_ok"], "method": res["method"], "level": res["ladder_level_used"],
           "exhausted": bool(res.get("ladder_exhausted_without_full_rewrite")), "before_fragment": res.get("before_fragment"),
           "after_fragment": res.get("after_fragment"), "structural_rules": h.get("structural_rules"),
           "hook_last_resort_delete": bool(h.get("hook_last_resort_delete")),
           "deleted_sentences": max(0, before_sents - after_sents), "cost_jpy": round(state["cumulative_jpy"], 4),
           "n_calls": state["cumulative_calls"]}
    if res["guard_ok"] and res.get("before_fragment") and res.get("after_fragment"):
        out["diff_flags"] = diff_flags(res["before_fragment"], res["after_fragment"], vocab, art)
    out["_updated_text"] = res["updated_text"]
    out["_pair"] = h.get("structural_pair")
    out["_prior"] = [{"claim_in_article": sr["claim_text"]}]
    return out, art, ledger, state, ce, call_log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-from", default="v1")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--budget-jpy", type=float, default=180.0)
    ap.add_argument("--max-workers", type=int, default=4)
    ap.add_argument("--recheck", type=int, default=1)
    ap.add_argument("--reverse", type=int, default=0)
    ap.add_argument("--kind", default="dev")
    ap.add_argument("--only-on", type=int, default=0)
    a = ap.parse_args()
    for k, v in (("OPEN233_FIX_W1_TITLE_MARKUP", "1"), ("OPEN233_FIX_W2_STRUCTURAL_RECHECK", "1"), (cap2.SW_SAVE_R3, "1"),
                 (cap2.SW_READER_BELIEF, "1")):
        os.environ[k] = v
    client = L.setup(a.budget_jpy)
    targets = collect_targets(a.tag_from, a.kind)
    print("targets", len(targets), [(t["source"], t["run"].split("runs/")[-1], t["claim"]["section_type"]) for t in targets])
    odir = OUT / ("replay_heldout" if a.kind == "heldout" else "replay_dev") / "stage3_rewrite"
    odir.mkdir(parents=True, exist_ok=True)
    jobs = [(i, rep, on) for i in range(len(targets)) for rep in range(a.n) for on in ((True,) if a.only_on else (True, False))]
    if a.reverse:
        jobs = list(reversed(jobs))

    def work(job):
        i, rep, on = job
        f = odir / f"t{i}_r{rep}_{'on' if on else 'off'}.json"
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8"))
        if R.cost_total() >= a.budget_jpy:
            return {"skipped": "budget"}
        # 環境変数はprocess全体で共有されるため、ladderへ渡す規則スイッチはone()内で設定(同時実行すると競合する)。
        # → 規則ON/OFFをまたぐ並列は避け、ここでは直列lockで囲む(Rewriteは1 callずつで短い)。
        with R.lock:
            os.environ[cap2.SW_STRUCT_RULES] = "1" if on else "0"
            out, art, ledger, state, ce, call_log = one(client, targets[i], rep, on, a.budget_jpy)
        cost = out["cost_jpy"]
        if on and a.recheck and out["guard_ok"] and out["_pair"]:
            before = art
            after = out["_updated_text"]
            with R.lock:
                os.environ["OPEN233_FIX_W2_STRUCTURAL_RECHECK"] = "1"
                st2, ce2, cl2 = L.new_state(), [0], []
                rc = runner.run_recheck_coverage(client, st2, ce2, cl2, f"s3_rc_{i}_{rep}", {"ledger_text": ledger, "article_text": after},
                                                 after, out["_prior"], before,
                                                 structural_pairs=[{"before": out["_pair"]["before"], "after": out["_pair"]["after"]}])
            au = rc.get("recheck_coverage_audit") or {}
            out["recheck"] = {"overall_status": rc.get("overall_status"), "scope_ids": au.get("scope_ids"),
                              "n_deviations": len(rc.get("deviations") or []),
                              "deviations": [{"claim": (d.get("claim_in_article") or "")[:120], "issue": (d.get("issue") or "")[:160],
                                              "severity": d.get("severity")} for d in (rc.get("deviations") or [])][:8],
                              "all_prior_resolved": rc.get("all_prior_issues_resolved"), "api_failure": bool(rc.get("_recheck_api_failure")),
                              "cost_jpy": round(st2["cumulative_jpy"], 4)}
            cost += st2["cumulative_jpy"]
        out["updated_text"] = out.pop("_updated_text", None)  # 前後対の再構成(盲検読み比べペア・面白さ代理指標)に使う
        out.pop("_pair", None)
        out.pop("_prior", None)
        out["total_cost_jpy"] = round(cost, 4)
        f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        R.add_cost("stage3_rewrite", f"{'on' if on else 'off'}", f"t{i}_r{rep}", cost, out["n_calls"])
        return out
    # 環境変数競合のためworkers=1相当に直列化されるが、API待ちはlock外にならない点は許容(対象が小さい)
    with cf.ThreadPoolExecutor(max_workers=a.max_workers) as ex:
        res = list(ex.map(work, jobs))
    (OUT / "eval").mkdir(exist_ok=True, parents=True)
    (OUT / "eval" / ("stage3_targets.json" if a.kind == "dev" else "stage3_targets_heldout.json")).write_text(json.dumps(
        [{"i": i, "source": t["source"], "run": t["run"], "section_type": t["claim"].get("section_type"),
          "claim": t["claim"]["claim_text"]} for i, t in enumerate(targets)], ensure_ascii=False, indent=1), encoding="utf-8")
    print("done", len(res), "cost_total", R.cost_total())


if __name__ == "__main__":
    main()
