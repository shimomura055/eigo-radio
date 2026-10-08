# -*- coding: utf-8 -*-
"""V3 集計: changed_actor 保護(OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor)ありの再生 vs 保存済み実run(保護なし)。"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import v3_reclassify_replay as V3  # noqa: E402
import er052_open233_stage1_reclassify_01 as reclf  # noqa: E402
import er052_open233_stage1_coverage_checker_01 as cov  # noqa: E402


def norm(s):
    return cov.norm_sentence(s or "")


def main():
    excl = [json.loads(l) for l in open(f"{C.OUT}/s0_excluded_candidates.jsonl", encoding="utf-8")]
    out = []
    summary = {"runs": 0, "protected": 0, "blocking": 0, "quality": 0, "acceptable": 0, "missing": 0, "cost": 0.0,
               "reclass_cost": 0.0, "stage2_cost": 0.0, "retained_protected": 0}
    rows = []
    for name, run_dir in V3.TARGETS.items():
        p = f"{V3.V3}/{name}.json"
        if not os.path.exists(p):
            out.append(f"{name}: (未実行)")
            continue
        d = json.load(open(p, encoding="utf-8"))
        dump = json.load(open(f"{run_dir}/checker/runs/meta_run03_advanced.json", encoding="utf-8"))
        a = dump["provenance"]["args"]
        ledger = open(a["ledger_path"], encoding="utf-8").read()
        blocks = cov.ledger_fact_blocks(ledger)
        pr = dump["stage1_coverage"]["per_route"]
        pre = [c for k in ("r3", "r5") for c in pr[k]["candidates"]]
        prot_claims = {}
        for c in pre:
            if reclf.is_model(c) and (c.get("flags") or {}).get("changed_actor"):
                prot_claims.setdefault(reclf.ckey(c), c)
        old_rows = {r["key"]: r for r in excl if r["file"].startswith(run_dir) and "changed_actor" in (r.get("stage1_flags") or [])}
        # 保存済み実runの cycle1 Stage 2
        old_c1 = {}
        for r in (dump.get("cycles") or [{}])[0].get("stage2_results", []):
            old_c1[norm(r.get("claim_text"))] = r
        s2 = d.get("stage2_results") or []
        s2_by = {norm(r["claim_text"]): r for r in s2}
        summary["runs"] += 1
        summary["cost"] += d["total_cost_jpy"]
        summary["reclass_cost"] += d["reclassify_cost_jpy"]
        summary["stage2_cost"] += d["stage2_cost_jpy"]
        out.append(f"\n### {name} ({run_dir.split('er052_output/')[1]})  費用 ¥{d['total_cost_jpy']} (再分類 ¥{d['reclassify_cost_jpy']} + Stage2/第2意見 ¥{d['stage2_cost_jpy']})  error={d['error']}")
        ri = d["reclassify_info"]
        out.append(f"再分類: targets={ri.get('n_targets')} protected_by_flags={ri.get('n_protected_by_flags')} excluded_claims={ri.get('n_excluded_claims')} (保存実run: 除外{dump['stage1_coverage']['candidate_filter']['n_excluded_claims']})")
        for k, c in prot_claims.items():
            r = s2_by.get(norm(c["claim_text"]))
            o = old_rows.get(k)
            final = (o or {}).get("in_final_text")
            verdict = "STAGE2に出ず" if r is None else r["materiality"]
            if o is not None:  # 保存実runの再分類で除外されていた changed_actor 候補(=保護の効果対象)
                if r is None:
                    summary["missing"] += 1
                else:
                    summary["protected"] += 1
                    summary[r["materiality"].lower()] += 1
                if final:
                    summary["retained_protected"] += 1
                    if r is not None:
                        summary["retained_" + r["materiality"].lower()] = summary.get("retained_" + r["materiality"].lower(), 0) + 1
            else:
                summary["already_candidate_changed_actor"] = summary.get("already_candidate_changed_actor", 0) + 1
            fids = c.get("related_fact_ids") or []
            led = " / ".join((blocks.get(f) or {}).get("text", "")[:160] if isinstance(blocks.get(f), dict) else str(blocks.get(f))[:160] for f in fids)
            row = {"run": name, "key": k, "claim": c["claim_text"], "old_reclass": (o or {}).get("verdict"), "old_actor_match": (o or {}).get("actor_match"),
                   "old_reason": (o or {}).get("reclass_reason"), "in_final_text_old": final, "stage1_issue": "; ".join(c.get("issues") or []),
                   "replay_materiality": verdict, "llm_materiality": (r or {}).get("llm_materiality"), "basis": (r or {}).get("basis"),
                   "floor_reason": (r or {}).get("floor_reason"), "second_opinion_split": ((r or {}).get("second_opinion") or {}).get("split"),
                   "rewrite_hint": (r or {}).get("rewrite_hint"), "related": fids, "ledger_excerpt": led,
                   "old_cycle1_materiality_same_claim": (old_c1.get(norm(c["claim_text"])) or {}).get("materiality")}
            rows.append(row)
            out.append(f"- [{k}] {'【旧で除外→保護】' if o is not None else '(旧でも候補)'} 旧再分類={row['old_reclass']}/actor={row['old_actor_match']} 最終本文に残存={final} -> 再生 Stage2={verdict} (一次={row['llm_materiality']}, 第2意見split={row['second_opinion_split']}, floor={row['floor_reason']}) | 旧実runのcycle1同文={row['old_cycle1_materiality_same_claim']}")
            out.append(f"    文: {c['claim_text'][:150]}")
            out.append(f"    Stage1 issue: {row['stage1_issue'][:200]}")
            out.append(f"    旧再分類reason: {(row['old_reason'] or '')[:160]}")
        # BLOCKINGの差(保護以外)
        blk_new = {norm(r["claim_text"]) for r in s2 if r["materiality"] == "BLOCKING"}
        blk_old = {k for k, r in old_c1.items() if r.get("materiality") == "BLOCKING"}
        out.append(f"BLOCKING件数: 再生={len(blk_new)}  旧実run cycle1={len(blk_old)}  再生のみ={len(blk_new - blk_old)}  旧のみ={len(blk_old - blk_new)}")
        for k in sorted(blk_new - blk_old):
            out.append(f"    再生のみBLOCKING: {k[:100]}")
    json.dump(rows, open(f"{V3.V3}/protected_rows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out.append("\n## 集計")
    out.append(json.dumps(summary, ensure_ascii=False))
    txt = "\n".join(out)
    open(f"{V3.V3}/V3_RESULTS.txt", "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
