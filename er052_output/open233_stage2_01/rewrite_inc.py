# -*- coding: utf-8 -*-
"""STAGE2-01 委任_02 測定(2)補助=ライン6(削除文数): ②で新たにBLOCKINGへ転じた候補(現行[保存済み]では非BLOCKING、新構成でBLOCKING)に実際のRewriteラダー
(構造要素規則ON)を1回ずつ実行し、削除された文数(Rewrite前後の文数差)を数える。API有料(1件¥0.1〜0.3)。
rewrite_kind/rewrite_hintは、保存されている場合(heldout)はそれを使い、devの再判定出力には無いので`replace_with_ledger_value`+決定論hintで近似する
(削除を選ぶ入力を含まないため、devの削除文数は下限側の見積り)。使い方: python rewrite_inc.py --kind dev --tag v2 [--budget-jpy 180]"""
import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import re

import replay_lib as L
import replay_stage2 as R

runner, cap2, OUT = L.runner, L.cap2, L.OUT


def n_sents(t):
    return len(re.findall(r"[.!?](?:\s|$)", t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="dev")
    ap.add_argument("--tag", default="v2")
    ap.add_argument("--budget-jpy", type=float, default=180.0)
    ap.add_argument("--max-workers", type=int, default=4)
    ap.add_argument("--mode", default="added", help="added=新構成でBLOCKINGに転じた候補 / removed=保存済みBLOCKINGが新構成で非BLOCKINGへ(現行flowならRewriteされた分)")
    a = ap.parse_args()
    for k, v in ((cap2.SW_STRUCT_RULES, "1"), ("OPEN233_FIX_W1_TITLE_MARKUP", "1"), ("OPEN233_FIX_W2_STRUCTURAL_RECHECK", "1")):
        os.environ[k] = v
    client = L.setup(a.budget_jpy)
    base = OUT / ("replay_heldout" if a.kind == "heldout" else "replay_dev") / a.tag
    jobs = []
    for f in sorted(base.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for x in d.get("results", []):
            if a.mode == "added" and x["new"]["materiality"] == "BLOCKING" and x["saved"]["materiality"] != "BLOCKING":
                jobs.append((d["run"], x))
            if a.mode == "removed" and x["saved"]["materiality"] == "BLOCKING" and x["new"]["materiality"] != "BLOCKING":
                jobs.append((d["run"], x))
    print("jobs", len(jobs))
    odir = OUT / ("replay_heldout" if a.kind == "heldout" else "replay_dev") / ("rewrite_inc_" + a.tag + ("" if a.mode == "added" else "_removed"))
    odir.mkdir(parents=True, exist_ok=True)

    def work(ij):
        i, (run_dir, x) = ij
        f = odir / f"{i:03d}.json"
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8"))
        if R.cost_total() >= a.budget_jpy:
            return {"skipped": "budget"}
        run, ledger, art = L.load_run(run_dir)
        sr = next((s for s in run["cycles"][0]["stage2_results"] if s["claim_text"] == x["claim_text"]), None) or {}
        dev = sr.get("dev") or {}
        blk = runner.floor_verify_fact_block(ledger, dev.get("related_fact_id"))
        hint, _ = runner.downgrade_verify_rewrite_hint(dev, blk)
        kind = (sr.get("rewrite_kind") if a.mode == "removed" else x["new"].get("rewrite_kind")) or "replace_with_ledger_value"
        state, ce, cl = L.new_state(), [0], []
        claim_rec = {"claim_text": x["claim_text"], "rewrite_kind": kind, "materiality": "BLOCKING", "basis": x["new"].get("basis") or "ledger_claim",
                     "rewrite_hint": ((sr.get("rewrite_hint") if a.mode == "removed" else x["new"].get("rewrite_hint")) or hint or ""), "dev": dev}
        try:
            res = runner.rewrite_ranges_ladder(client, state, ce, cl, f"inc_{i}", {"ledger_text": ledger, "article_text": art}, "article_text", claim_rec)
        except Exception as e:  # noqa: BLE001
            return {"run": run_dir, "claim": x["claim_text"], "error": f"{type(e).__name__}: {e}"}
        out = {"run": run_dir, "claim": x["claim_text"], "section_type": x["new"].get("section_type"), "rewrite_kind_used": kind,
               "kind_source": "saved" if (a.mode == "removed" or x["new"].get("rewrite_kind")) else "approx_replace_with_ledger_value",
               "guard_ok": res["guard_ok"], "method": res["method"], "level": res["ladder_level_used"],
               "exhausted": bool(res.get("ladder_exhausted_without_full_rewrite")),
               "deleted_sentences": max(0, n_sents(art) - n_sents(res["updated_text"])), "before": res.get("before_fragment"),
               "after": res.get("after_fragment"), "cost_jpy": round(state["cumulative_jpy"], 4)}
        f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        R.add_cost("rewrite_inc", f"{a.kind}_{a.tag}", f"{i:03d}", state["cumulative_jpy"], state["cumulative_calls"])
        return out
    with cf.ThreadPoolExecutor(max_workers=a.max_workers) as ex:
        res = list(ex.map(work, list(enumerate(jobs))))
    ok = [r for r in res if "guard_ok" in r]
    n_art = len({j[0] for j in jobs}) if False else (22 if a.kind == "dev" else len(L.dev_runs("heldout")))
    summ = {"kind": a.kind, "tag": a.tag, "mode": a.mode, "n_jobs": len(jobs), "n_done": len(ok), "guard_ok": sum(r["guard_ok"] for r in ok),
            "exhausted": sum(r["exhausted"] for r in ok), "deleted_sentences_total": sum(r["deleted_sentences"] for r in ok),
            "n_articles": n_art, "deleted_per_article": round(sum(r["deleted_sentences"] for r in ok) / max(1, n_art), 4),
            "approx_kind_jobs": sum(1 for r in ok if r["kind_source"] != "saved"), "cost_jpy": round(sum(r["cost_jpy"] for r in ok), 3)}
    (OUT / "eval").mkdir(exist_ok=True, parents=True)
    (OUT / "eval" / f"rewrite_inc_{a.kind}_{a.tag}{'' if a.mode == 'added' else '_removed'}.json").write_text(json.dumps({"summary": summ, "rows": ok}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summ, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
