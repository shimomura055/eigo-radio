# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_stage1_coverage_dryrun_01.py
# OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_06 作業4(b): fixture dry-run(¥0、LLM呼び出しなし・決定論のみ)。
# 全Trial fixtureで文ID分割を実行し、(1)正式gold(`SAFETY_CRITICAL_CLAIM_DEFS`のexpected=BLOCKING 6 claim)の文が単位IDに
# 対応するか、(2)neg5で「continued on July 14.」+「So the flashy 20% plan...」の関係単位が生成されるか、(3)単位数/記事・
# 同文グループ数・prompt文字数(段階A費用概算の入力)を集計し、json/mdへ保存する。gold・fixture・定義は変更しない(読むだけ)。
# 出力: er052_output/open233_stage1_coverage_dryrun_01/{dryrun_result.json,dryrun_report.md}
# ============================================================
from __future__ import annotations

import json
import os
import re

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov

OUT_DIR = "er052_output/open233_stage1_coverage_dryrun_01"
GOLD_INSTANCE_IDS = ["bgroup_B3", "safety_A2A3", "safety_A4", "safety_A5", "bgroup_B4", "neg5_hormuz_div_a2"]


def split_for(fixture: dict) -> dict:
    return cov.split_units(fixture["article_text"], runner.vs_sentence_segments_l6, runner.CAUSAL_SENTENCE_INITIAL_EN)


def match_gold_def(d: dict, units: list) -> dict:
    """gold定義1件(text_substring/任意でtext_pattern)に対応する単位ID(文・見出し・タイトル)と、その文を当該文とする関係単位ID。"""
    sub = runner._norm_for_residual(d["text_substring"]).lower()
    pat = re.compile(d["text_pattern"], re.I) if d.get("text_pattern") else None
    sent_hits = []
    for u in units:
        if u["type"] not in ("sentence", "heading", "title"):
            continue
        t = runner._norm_for_residual(u["text"])
        if sub in t.lower() or (pat is not None and pat.search(t)):
            sent_hits.append(u["id"])
    rel = [u["id"] for u in units if u["type"] == "relation" and u["cur_id"] in sent_hits]
    pat_hits = [i for i in sent_hits if pat is not None and pat.search(runner._norm_for_residual(
        next(u for u in units if u["id"] == i)["text"]))]
    return {"sub_id": d["sub_id"], "related_fact_id": d["related_fact_id"], "text_substring": d["text_substring"],
            "matched_unit_ids": sent_hits, "pattern_matched_unit_ids": pat_hits, "relation_unit_ids_covering": rel,
            "mapped": bool(sent_hits)}


def main() -> None:
    insts = runner.build_target_instances()
    per_inst, gold_rows = [], []
    for inst in insts:
        fx = inst["fixture"]
        sp = split_for(fx)
        units = sp["units"]
        blocks = cov.ledger_fact_blocks(fx["ledger_text"])
        r3p = cov.build_r3_prompt(fx["ledger_text"], units, sp["judged_ids"])
        r5p = cov.build_r5_prompt(fx["ledger_text"], units, list(blocks))
        per_inst.append({
            "instance_id": inst["instance_id"], "group": inst["group"], "article_chars": len(fx["article_text"]),
            "n_units": len(units), "n_judged_units": len(sp["judged_ids"]),
            "n_sentence_units": sum(1 for u in units if u["type"] == "sentence"),
            "n_relation_units": len(sp["relation_ids"]), "relation_ids": sp["relation_ids"],
            "n_same_sentence_groups": len(sp["same_sentence_groups"]), "same_sentence_groups": sp["same_sentence_groups"],
            "n_facts": len(blocks), "r3_prompt_chars": len(r3p), "r5_prompt_chars": len(r5p),
            "verbatim_offsets_ok": all(fx["article_text"][u["start"]:u["end"]] == u["text"]
                                       for u in units if u["type"] != "relation")})
        for d in runner._safety_critical_defs(inst["instance_id"]):
            row = match_gold_def(d, units)
            gold_rows.append({"instance_id": inst["instance_id"], **row})
    neg5 = next(i for i in insts if i["instance_id"] == "neg5_hormuz_div_a2")
    sp5 = split_for(neg5["fixture"])
    by5 = {u["id"]: u for u in sp5["units"]}
    rel5 = [by5[r] for r in sp5["relation_ids"]
            if "continued on July 14." in by5[r]["text"] and by5[r]["claim_text"].startswith("So the flashy 20% plan")]
    n = len(per_inst)
    gold_mapped = sum(1 for g in gold_rows if g["mapped"])
    summary = {
        "n_instances": n, "gold_claims_total": len(gold_rows), "gold_claims_mapped_to_unit_ids": gold_mapped,
        "gold_claim_ids": [g["sub_id"] for g in gold_rows],
        "neg5_relation_unit_generated": bool(rel5), "neg5_relation_unit_ids": [r["id"] for r in rel5],
        "avg_judged_units_per_article": round(sum(p["n_judged_units"] for p in per_inst) / n, 1),
        "min_max_judged_units": [min(p["n_judged_units"] for p in per_inst), max(p["n_judged_units"] for p in per_inst)],
        "total_relation_units": sum(p["n_relation_units"] for p in per_inst),
        "articles_with_relation_units": sum(1 for p in per_inst if p["n_relation_units"]),
        "total_same_sentence_groups": sum(p["n_same_sentence_groups"] for p in per_inst),
        "articles_with_same_sentence_groups": sum(1 for p in per_inst if p["n_same_sentence_groups"]),
        "all_offsets_verbatim": all(p["verbatim_offsets_ok"] for p in per_inst),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    result = {"summary": summary, "gold": gold_rows, "per_instance": per_inst, "prompt_sha256": cov.PROMPT_SHA256}
    with open(f"{OUT_DIR}/dryrun_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    L = ["# Stage 1 coverage_union fixture dry-run(委任_06、¥0・決定論・LLM呼び出しなし)", "",
         f"- instance数: {n} / 正式gold(expected=BLOCKING): {len(gold_rows)} claim -> 単位IDへ対応: **{gold_mapped}/{len(gold_rows)}**",
         f"- neg5の関係単位(「continued on July 14.」+「So the flashy 20% plan...」): **{'有' if rel5 else '無'}** {summary['neg5_relation_unit_ids']}",
         f"- 判定対象単位数/記事: 平均{summary['avg_judged_units_per_article']}(最小{summary['min_max_judged_units'][0]}、最大{summary['min_max_judged_units'][1]})",
         f"- 関係単位: 計{summary['total_relation_units']}件({summary['articles_with_relation_units']}記事) / 同文グループ: 計{summary['total_same_sentence_groups']}件({summary['articles_with_same_sentence_groups']}記事)",
         f"- 全単位のoffsetが本文と逐語一致: {summary['all_offsets_verbatim']}", "", "## 正式gold 6 claim -> 単位ID", "",
         "| instance | sub_id | fact | 対応単位ID | 関係単位(当該文) | mapped |", "|---|---|---|---|---|---|"]
    for g in gold_rows:
        L.append(f"| {g['instance_id']} | {g['sub_id']} | {g['related_fact_id']} | {', '.join(g['matched_unit_ids'])} | "
                 f"{', '.join(g['relation_unit_ids_covering']) or '-'} | {g['mapped']} |")
    L += ["", "## instance別", "", "| instance | group | 文字数 | 判定単位 | 関係単位 | 同文G | fact数 | R3 prompt字 | R5 prompt字 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for p in per_inst:
        L.append(f"| {p['instance_id']} | {p['group']} | {p['article_chars']} | {p['n_judged_units']} | {p['n_relation_units']} | "
                 f"{p['n_same_sentence_groups']} | {p['n_facts']} | {p['r3_prompt_chars']} | {p['r5_prompt_chars']} |")
    with open(f"{OUT_DIR}/dryrun_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
