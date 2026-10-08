# -*- coding: utf-8 -*-
"""sweep 集計(委任_04b、決定論・API呼び出しなし)。
出力: sweep_01/MANIFEST.json(run別) / sweep_01/eval/CHECK_SUMMARY_SWEEP.md(照合(i)~(iv)の変種別)。
S5は既存v1 run(参照)を同じ集計で並べる。S0はタグ無しのため照合対象外。S8は事後タグ再付与ベース(参考値)。"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
import er052_factlock_writer_trial_01_run as fl  # noqa: E402  (strip_tags再利用、読み取りのみ)

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
BASE = "er052_output/factlock_writer_trial_01"
SW = f"{BASE}/sweep_01"
PRICE = {"gpt-5.6-luna": (0.20, 0.02, 1.20), "gpt-6-luna": (0.10, 0.01, 0.50)}
USD_JPY = 160.0
STAGES = ["r0", "r1", "r2"]
BRIEFS = [("meta", 2), ("hormuz", 4), ("space_weapons", 3)]


def jl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()] if os.path.exists(p) else []


def load(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def run_cost(d):
    t, by = 0.0, collections.Counter()
    for r in jl(f"{d}/raw_usage_log.jsonl"):
        pr = PRICE.get(r.get("model_id"))
        if not pr:
            continue
        c = (((r.get("input_tokens") or 0) - (r.get("cached_input_tokens") or 0)) * pr[0]
             + (r.get("cached_input_tokens") or 0) * pr[1] + (r.get("output_tokens") or 0) * pr[2]) / 1e6 * USD_JPY
        t += c
        by[r.get("model_id")] += 1
    chk = 0.0
    bs = f"{d}/checker/budget_state_checker_after_p01.json"
    if os.path.exists(bs):
        chk = (load(bs) or {}).get("cumulative_jpy", 0.0)
    return t, chk, dict(by)


def sweep_dirs():
    out = []
    for d in sorted(glob.glob(f"{SW}/runs/*/control/b*__S*__r1")):
        d = d.replace("\\", "/")
        if "_failed_a" in d:
            continue
        m = re.search(r"runs/(.+?)/control/b(\d+)__(S\d+)__r1$", d)
        out.append((m.group(3), m.group(1), int(m.group(2)), d))
    return out


def s5_dirs():
    return [("S5", s, b, f"{BASE}/runs/{s}/control/b{b}__factlock__r1") for s, b in BRIEFS]


def run_record(vid, slug, b, d):
    man = load(f"{d}/manifest.json") or {}
    t, chk, calls = run_cost(d)
    r = {"variant": vid, "slug": slug, "brief": b, "dir": d, "exit_reason": man.get("exit_reason"),
         "exit_code": man.get("exit_code"), "wall_sec": man.get("wall_sec"),
         "cost_writer_jpy": round(t, 2), "cost_checker_jpy": round(chk, 2),
         "cost_total_jpy": round(t + chk, 2), "calls_by_model": calls,
         "model_ids_actual": {k: v for k, v in (man.get("model_ids_actual") or {}).items() if not k.startswith("_")},
         "variants_json_sha256": man.get("variants_json_sha256"),
         "sweep_run_sha256": (man.get("harness_sha256") or {}).get("sweep_run"),
         "r3": man.get("r3") if isinstance(man.get("r3"), dict) else None,
         "chain_actual_cut_log_n": len(man.get("chain_actual_cut_log") or [])}
    ev = load(f"{d}/ja_writer/runtime_evidence.json") or {}
    fc = ev.get("fact_checks_summary", {})
    r["ja_fc"] = {k: {"final_status": v.get("final_status"), "must_fix_applied": v.get("must_fix_applied"),
                      "n_must_fix": len(v.get("must_fix_used") or [])} for k, v in fc.items()}
    ws = load(f"{d}/writer_run_summary.json") or {}
    adv = ws.get("advanced", {})
    r["en_regen"] = {"retried": adv.get("retried_for_deviation"), "status": adv.get("deviation_overall_status")}
    for f in glob.glob(f"{d}/checker/runs/*.json"):
        c = load(f) or {}
        r["checker"] = {"final_state": c.get("final_state"),
                        "stage1": len((c.get("all_deviations_raw") or {}).get("stage1") or []), "calls": c.get("total_calls")}
    r["has_article"] = os.path.exists(f"{d}/b1b/article.md")
    # phase2のJA再確認(案B)でJAが再生成されると、タグ除去後に書かれたタグ付きJAが最終ファイルになる(harnessの後処理はphase1後のみ)
    j2, jt = f"{d}/ja_writer/revision2.md", f"{d}/ja_writer/revision2_with_tags.md"
    r["final_ja_r2_has_tags"] = os.path.exists(j2) and ("【事実" in open(j2, encoding="utf-8").read())
    en = f"{d}/b1b/article.md"
    r["final_en_has_tags"] = os.path.exists(en) and bool(re.search("【(Fact|事実)", open(en, encoding="utf-8").read()))
    r["ja_regenerated_in_phase2"] = bool(os.path.exists(j2) and os.path.exists(jt) and fl.strip_tags(open(jt, encoding="utf-8").read()).strip() != open(j2, encoding="utf-8").read().strip())
    r["completed"] = r["exit_reason"] == "completed"
    return r


def agg_variant(rows):
    recs = []
    for _, slug, b, d in rows:
        x = {s: load(f"{d}/factlock_check_{s}.json") for s in STAGES}
        x["diff"] = load(f"{d}/factlock_diff.json")
        x["summ"] = load(f"{d}/factlock_summary.json")
        x["name"] = f"{slug}/b{b}"
        recs.append(x)
    R = {"n_runs": len(recs), "n_with_check_r2": sum(1 for x in recs if x["r2"])}
    for s in STAGES:
        rs = [x[s] for x in recs if x[s]]
        tg = sum(x["tagged_sentences"] for x in rs)
        c, cc, unk = collections.Counter(), collections.Counter(), 0
        for x in rs:
            ip = x.get("i_pairs") or {}
            c.update(ip.get("counts") or {})
            cc.update(ip.get("claim_counts") or {})
            unk += len(ip.get("unknown_tags") or [])
        n = len(rs)
        R[s] = {"n": n, "tagged": tg, "incons": c["不整合"], "undecid": c["判定不能"],
                "incons_rate": (c["不整合"] / tg) if tg else None,
                "unsupported_per_art": (cc["unsupported"] / n) if n else None, "unknown_tags": unk}
        lab, un = collections.Counter(), 0
        for x in rs:
            iu = x.get("ii_untagged") or {}
            lab.update(iu.get("counts") or {})
            un += iu.get("untagged_sentences", 0)
        R[s]["untagged"] = un
        R[s]["new_specific_per_art"] = (lab["new_specific_claim"] / n) if n else None
        R[s]["background_general_per_art"] = (lab["background_general"] / n) if n else None
        R[s]["hedged_speculation_per_art"] = (lab["hedged_speculation"] / n) if n else None
        nc, tot, cw, me = collections.Counter(), 0, 0, 0
        for x in rs:
            nn = x["iii_numbers"]
            nc.update(nn["counts"])
            tot += nn["total"]
            cw += len(nn["core_used_without_tag"])
            me += x["marks_echoed"]
        R[s]["num_tokens"] = tot
        R[s]["num_mismatch_per_art"] = ((nc["hedge_changed"] + nc["not_core"]) / n) if n else None
        R[s]["core_used_without_tag"] = cw
        R[s]["marks_echoed"] = me
    dc = collections.Counter()
    for x in recs:
        if x["diff"]:
            dc.update(x["diff"]["r0_to_r2"]["counts"])
    R["r0_to_r2"] = dict(dc)
    R["residual_r2"] = sum(((x["summ"] or {}).get("strip", {}).get("r2", {}).get("residual_brackets_after_strip", 0)) for x in recs)
    man_unexp = 0
    for _, slug, b, d in rows:
        m = load(f"{d}/manifest.json") or {}
        man_unexp += (m.get("residual_bracket_scan") or {}).get("unexpected_total", 0)
    R["manifest_residual_unexpected"] = man_unexp
    return R


def fmt(x, p=1):
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.{p}f}"
    return str(x)


def main():
    sd = sweep_dirs()
    allrows = sd + [r for r in s5_dirs() if os.path.exists(f"{r[3]}/manifest.json")]
    manifest = {"trial_id": "FACTLOCK-WRITER-REDESIGN-TRIAL-01", "delegation": "04b",
                "runs": [run_record(*r) for r in allrows if r[0] != "S5"],
                "s5_reference_runs": [run_record(*r) for r in allrows if r[0] == "S5"]}
    manifest["total_cost_jpy_sweep"] = round(sum(r["cost_total_jpy"] for r in manifest["runs"]), 2)
    json.dump(manifest, open(f"{SW}/MANIFEST.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    by = collections.defaultdict(list)
    for r in allrows:
        by[r[0]].append(r)
    order = sorted(by, key=lambda v: int(v[1:]))
    O = []
    P = O.append
    P("# CHECK_SUMMARY_SWEEP(照合指標の変種別集計、測定のみ。照合は6-luna自己判定で盲検rubricの代替ではない。委任_04b)")
    P("")
    P("S5=v1(Fact Lock v1)の既存3run(参照)。S0はタグ無しのため照合対象外。**S8は事後タグ再付与ベース(R1/R2のタグはWriterではなく6-lunaが後付け)で、(i)(iv)は参考値**。S1/S2/S7は数値規則を持たない。S11は中核数値も原則書かせない。N=3本/変種で有意性は主張しない。")
    P("")
    P("## 1. R2の主指標(変種別)")
    P("| 変種 | run数(照合あり) | タグ付き文(R2) | 不整合文 | 不整合率 | 判定不能 | unsupported主張/記事 | unknown_tags | タグなし文 | new_specific_claim/記事 | 数値トークン | 数値不一致/記事 | core_used_without_tag | marks_echoed | 残存【 |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    agg = {}
    for v in order:
        a = agg[v] = agg_variant(by[v])
        r2 = a["r2"]
        rate = None if r2["incons_rate"] is None else r2["incons_rate"] * 100
        P(f"| {v}{'(retag)' if v == 'S8' else ''} | {a['n_runs']}({a['n_with_check_r2']}) | {r2['tagged']} | {r2['incons']} | {fmt(rate)}% | {r2['undecid']} | {fmt(r2['unsupported_per_art'], 2)} | {r2['unknown_tags']} | {r2['untagged']} | {fmt(r2['new_specific_per_art'], 2)} | {r2['num_tokens']} | {fmt(r2['num_mismatch_per_art'], 2)} | {r2['core_used_without_tag']} | {r2['marks_echoed']} | {a['residual_r2']} |")
    P("")
    P("## 2. 段別の不整合率(R0 / R1 / R2、タグ付き文あたり)と new_specific_claim/記事・数値不一致/記事")
    P("| 変種 | R0 不整合率 | R1 | R2 | R0 new_specific/記事 | R1 | R2 | R0 数値不一致/記事 | R1 | R2 |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    for v in order:
        a = agg[v]

        def pc(s):
            return fmt(None if a[s]["incons_rate"] is None else a[s]["incons_rate"] * 100) + "%"
        P(f"| {v} | {pc('r0')} | {pc('r1')} | {pc('r2')} | " + " | ".join(fmt(a[s]["new_specific_per_art"], 2) for s in STAGES)
          + " | " + " | ".join(fmt(a[s]["num_mismatch_per_art"], 2) for s in STAGES) + " |")
    P("")
    P("## 3. (iv) R0→R2 タグ付き文の 維持/改変/削除/added/number_changed(合計)")
    P("| 変種 | 維持 | 改変 | 削除 | added | number_changed |")
    P("|---|---|---|---|---|---|")
    for v in order:
        c = agg[v]["r0_to_r2"]
        P(f"| {v} | {c.get('kept', 0)} | {c.get('modified', 0)} | {c.get('deleted', 0)} | {c.get('added', 0)} | {c.get('number_changed', 0)} |")
    P("")
    P("## 4. run別(不整合文/タグ付き文 R0・R1・R2、R2 unsupported主張、R2数値不一致トークン)")
    P("| run | R0 | R1 | R2 | R2 unsupported | R2 数値不一致 |")
    P("|---|---|---|---|---|---|")
    for vid, slug, b, d in allrows:
        row = []
        for s in STAGES:
            x = load(f"{d}/factlock_check_{s}.json")
            if not x:
                row.append("-")
                continue
            row.append(f"{((x.get('i_pairs') or {}).get('counts') or {}).get('不整合', 0)}/{x['tagged_sentences']}")
        x2 = load(f"{d}/factlock_check_r2.json")
        u2 = ((x2 or {}).get("i_pairs") or {}).get("claim_counts", {}).get("unsupported", "-") if x2 else "-"
        nm = "-"
        if x2:
            nm = sum(1 for t in x2["iii_numbers"]["tokens"] if t["status"] in ("hedge_changed", "not_core"))
        P(f"| {vid} {slug}/b{b} | " + " | ".join(row) + f" | {u2} | {nm} |")
    os.makedirs(f"{SW}/eval", exist_ok=True)
    open(f"{SW}/eval/CHECK_SUMMARY_SWEEP.md", "w", encoding="utf-8").write("\n".join(O) + "\n")
    json.dump(agg, open(f"{SW}/eval/CHECK_SUMMARY_SWEEP.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(O[:30]))
    print("sweep total cost", manifest["total_cost_jpy_sweep"])


if __name__ == "__main__":
    main()
