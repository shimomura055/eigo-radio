"""OPEN-238 deterministic regression (JPY 0, no API). Same-process before/after with the DEV wrapper installed
on the RUNNING precheck/runner modules. Writes regression/precheck_after_fix.json, REGRESSION.md.
O2: bit-identical check of L322 (changed_number_is_natural_rounding_only), L2838/L475-type loose extraction,
and all non-number_mismatch findings. O3: 'percentage point(s)' scan."""
import importlib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import precheck_baseline as pb
pb.install_stub()
pre = importlib.import_module("er052_open233_self_recovery_precheck_01")
runner = importlib.import_module("er052_open233_self_recovery_flow_runner_01")
fix = importlib.import_module("er052_open238_precheck_fix_dev_01")
OUT = os.path.join(ROOT, "er052_output", "open238_precheck_fix_trial_01", "regression")
ER = os.path.join(ROOT, "er052_output")


def snapshot(run):
    en, led = run["en"], run["ledger"]
    sents = pb.split_sentences(en)
    findings = pre.run_precheck(led, en)
    fires = []
    for f in findings:
        if f.get("kind") != "number_mismatch":
            continue
        s, m = runner.resolve_precheck_target_sentence(en, f)
        fires.append({"fact_id": f["field"], "foreign_values": f.get("foreign_values"), "sentence": s, "method": m})
    other = [f for f in findings if f.get("kind") != "number_mismatch"]
    nm = [{k: f[k] for k in ("field", "foreign_values") if k in f} for f in findings if f.get("kind") == "number_mismatch"]
    # O2: loose-path outputs (runner L2838 / coverage_checker L475 / precheck L322/L666 use these)
    loose_sent = [sorted(pre.extract_percentages(s) | set(pre.extract_counts(s))) for s in sents]
    loose_ledger = sorted(pre.extract_percentages(led) | set(pre.extract_counts(led)))
    facts = pre.parse_ledger_text(led)
    l322 = [[f["fact_id"], s_i, pre.changed_number_is_natural_rounding_only(s, f["fact_id"], led)]
            for f in facts for s_i, s in enumerate(sents)]
    return {"fires": fires, "number_mismatch_all_raw": nm, "other_findings_json": json.dumps(other, sort_keys=True, ensure_ascii=False),
            "loose_sent": loose_sent, "loose_ledger": loose_ledger, "l322": l322}


def strict_values(run):
    out = []
    for i, s in enumerate(pb.split_sentences(run["en"])):
        loose = sorted(pre.extract_percentages(s))
        strict = sorted(fix.extract_percentages_strict(s, pre))
        if loose != strict:
            out.append({"sentence_index": i, "loose": loose, "strict": strict, "sentence": s})
    return out


def main():
    runs = pb.discover_dir_runs(ER) + pb.discover_prod_runs(ER)
    runs = [r for r in runs if "skipped" not in r]
    before = {r["run_id"]: snapshot(r) for r in runs}
    fix.install(runner, pre)
    fix.reset_counters()
    try:
        after = {r["run_id"]: snapshot(r) for r in runs}
        diffs_strict = {r["run_id"]: strict_values(r) for r in runs}
        cnt = dict(fix.counters)
    finally:
        fix.uninstall()
    # sanity: saved baseline (pre-fix) fires equal in-process 'before'
    base = json.load(open(os.path.join(ER, "open238_precheck_fix_trial_01", "baseline", "precheck_baseline.json"), encoding="utf-8"))
    base_ok = all([(f["fact_id"], f["foreign_values"]) for f in b["fires"]] ==
                  [(f["fact_id"], f["foreign_values"]) for f in before[b["run_id"]]["fires"]] for b in base["runs"])
    rows, changed, bitwise = [], [], {"loose_sent": True, "loose_ledger": True, "l322": True, "other_findings": True}
    for r in runs:
        rid = r["run_id"]; b, a = before[rid], after[rid]
        if b["loose_sent"] != a["loose_sent"]: bitwise["loose_sent"] = False
        if b["loose_ledger"] != a["loose_ledger"]: bitwise["loose_ledger"] = False
        if b["l322"] != a["l322"]: bitwise["l322"] = False
        if b["other_findings_json"] != a["other_findings_json"]: bitwise["other_findings"] = False
        same = b["fires"] == a["fires"]
        if not same: changed.append(rid)
        rows.append((rid, len(b["fires"]), len(a["fires"]), same, len(diffs_strict[rid])))
    # O3
    texts = [r["en"] for r in runs]
    import glob
    for f in sorted(glob.glob(os.path.join(ER, "open233_prod_e2e_02/runs/*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
            for c in d.get("cycles", []):
                for k in ("en_text_before_rewrite", "en_text_after_rewrite"):
                    if c.get(k): texts.append(c[k])
        except Exception:
            pass
    pp = re.compile(r"percentage\s+points?", re.I)
    hits = []
    for t in texts:
        for s in pb.split_sentences(t):
            if pp.search(s):
                hits.append(s)
    json.dump({"runs": [{"run_id": r["run_id"], "before_fires": before[r["run_id"]]["fires"], "after_fires": after[r["run_id"]]["fires"],
                         "strict_vs_loose_diff_sentences": diffs_strict[r["run_id"]]} for r in runs],
               "changed_runs": changed, "bitwise_unchanged": bitwise, "counters": cnt, "baseline_json_matches_in_process_before": base_ok,
               "o3_percentage_point_texts_scanned": len(texts), "o3_percentage_point_sentences": hits},
              open(os.path.join(OUT, "precheck_after_fix.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# OPEN-238 決定論Regression(修正前/後、¥0、同一プロセス、実行中モジュールへinstall)", "",
         "runs=%d / 修正前fires合計=%d / 修正後fires合計=%d / 差分run=%d" % (len(runs), sum(x[1] for x in rows), sum(x[2] for x in rows), len(changed)),
         "保存済ベースライン(precheck_baseline.json)のfires == 本実行の修正前fires: %s" % base_ok,
         "bit単位不変(O2): loose抽出(runner L2838/coverage L475型,文別)=%s / 台帳loose抽出=%s / L322(changed_number_is_natural_rounding_only 全fact×全文)=%s / number_mismatch以外の全finding=%s" %
         (bitwise["loose_sent"], bitwise["loose_ledger"], bitwise["l322"], bitwise["other_findings"]),
         "カウンタ(修正後実行): %s" % cnt, "",
         "## run別", "", "| run_id | 修正前fires | 修正後fires | 同一 | strict≠looseの文数 |", "|---|---|---|---|---|"]
    for x in rows:
        L.append("| %s | %d | %d | %s | %d |" % x)
    L += ["", "## 差分run", ""]
    for rid in changed:
        L.append("- %s" % rid)
        L.append("  - 修正前: %s" % json.dumps(before[rid]["fires"], ensure_ascii=False))
        L.append("  - 修正後: %s" % json.dumps(after[rid]["fires"], ensure_ascii=False))
    L += ["", "## strict抽出がlooseと異なる文(全run)", ""]
    for r in runs:
        for d in diffs_strict[r["run_id"]]:
            L.append("- %s #%d loose=%s strict=%s | %s" % (r["run_id"], d["sentence_index"], d["loose"], d["strict"], d["sentence"]))
    L += ["", "## O3: 'percentage point(s)' 走査(報告のみ・修正しない)", "",
          "走査テキスト数=%d(全run EN + prod_e2e_02 cycles の en_text_before/after_rewrite、重複含む)、該当文=%d件" % (len(texts), len(hits))]
    for s in hits:
        L.append("- " + s)
    open(os.path.join(OUT, "REGRESSION.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("runs", len(runs), "before", sum(x[1] for x in rows), "after", sum(x[2] for x in rows), "changed", changed)
    print("bitwise", bitwise, "base_ok", base_ok, "counters", cnt, "o3", len(texts), len(hits))


if __name__ == "__main__":
    main()
