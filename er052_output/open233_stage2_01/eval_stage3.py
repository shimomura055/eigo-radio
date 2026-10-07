# -*- coding: utf-8 -*-
"""STAGE2-01 委任_02 測定(3)の集計(ライン1/6、構造要素由来STOP、Checker由来の新規NG)。入力: replay_dev/stage3_rewrite/*.json。出力: eval/stage3_eval.json"""
import glob
import json
import pathlib

import replay_lib as L

OUT = L.OUT


def main(n_articles=23):
    rows = []
    for f in sorted(glob.glob(str(OUT / "replay_dev" / "stage3_rewrite" / "*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        if "guard_ok" in d:
            d["_file"] = pathlib.Path(f).name
            rows.append(d)
    out = {"n_jobs": len(rows)}
    for key, on in (("rules_on", True), ("rules_off", False)):
        rs = [r for r in rows if r["rules_on"] == on]
        ok = [r for r in rs if r["guard_ok"]]
        viol = [r for r in ok if (r.get("diff_flags") or {}).get("violations")]
        title_markup_missing = [r for r in ok if r.get("section_type") == "title" and r.get("after_fragment")
                                and not r["after_fragment"].lstrip().startswith("#")]
        rc = [r.get("recheck") for r in ok if r.get("recheck")]
        out[key] = {
            "n": len(rs), "guard_ok": len(ok), "exhausted_structural_stop": sum(1 for r in rs if r["exhausted"]),
            "regen_calls": sum(((r.get("structural_rules") or {}).get("regen_calls") or 0) for r in rs),
            "rejected_levels": sum(len((r.get("structural_rules") or {}).get("rejected_levels") or []) for r in rs),
            "hook_last_resort_delete": sum(1 for r in rs if r["hook_last_resort_delete"]),
            "deleted_sentences_total": sum(r["deleted_sentences"] for r in rs),
            "deleted_sentences_per_job": round(sum(r["deleted_sentences"] for r in rs) / len(rs), 3) if rs else None,
            "violations_in_accepted_outputs": len(viol), "violation_rows": [
                {"file": r["_file"], "section": r["section_type"], "before": (r.get("before_fragment") or "")[:90],
                 "after": (r.get("after_fragment") or "")[:90], "flags": r["diff_flags"]} for r in viol],
            "title_markup_missing": len(title_markup_missing),
            "recheck_n": len(rc), "recheck_status": {s: sum(1 for x in rc if x["overall_status"] == s) for s in {x["overall_status"] for x in rc}},
            "recheck_new_deviations": sum(x["n_deviations"] for x in rc),
            "cost_jpy": round(sum(r.get("total_cost_jpy") or 0 for r in rs), 3),
        }
    on_rs = [r for r in rows if r["rules_on"]]
    # 記事単位のSTOP率: rep(0..2)ごとに、構造要素ladder枯渇を1件でも出した記事数 / 対象記事数
    arts_with_stop = {}
    for r in on_rs:
        if r["exhausted"]:
            arts_with_stop.setdefault(r["rep"], set()).add(r["run"])
    out["structural_stop_rate_per_rep"] = {str(k): round(len(v) / n_articles, 4) for k, v in arts_with_stop.items()}
    out["structural_stop_articles"] = {str(k): sorted(v) for k, v in arts_with_stop.items()}
    out["n_articles_denominator"] = n_articles
    off = {(r["run"], r["claim"], r["rep"]): r for r in rows if not r["rules_on"]}
    delta = []
    for r in on_rs:
        o = off.get((r["run"], r["claim"], r["rep"]))
        if o:
            delta.append(r["deleted_sentences"] - o["deleted_sentences"])
    out["deleted_sentences_delta_on_minus_off_total"] = sum(delta)
    out["deleted_sentences_delta_per_article"] = round(sum(delta) / (3 * n_articles), 4)  # 3rep平均を記事数で割る近似(対象外記事は0)
    (OUT / "eval").mkdir(exist_ok=True, parents=True)
    (OUT / "eval" / "stage3_eval.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: (v if k not in ("rules_on", "rules_off") else {kk: vv for kk, vv in v.items() if kk != "violation_rows"})
                      for k, v in out.items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
