"""OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_11 非BLOCKING判定の再利用(`STAGE2_VERDICT_REUSE_NONBLOCKING`)の¥0 replay(Fable評価10)。

再利用の条件: キー=(箇所の正規化span集合, fact_id)が一致し、前の判定が2-of-2非BLOCKING(Stage 2とS1が両方非BLOCKING=`confirmed_downgrade`、floorなし)。
一致したら後cycleのStage 2(+S1) callを省き、前の非BLOCKINGを再利用する(span集合の完全一致のみ、文単位への分解は禁止)。
事前固定の採用条件: 「再利用により抑制される判定のうち、正解ラベル上の重大が0件」。満たさなければOFFのまま。
追加で、「抑制されたが記録上は後cycleでBLOCKINGだった判定(=再利用で見逃す)」も数える(ラベル重大でなくても記録する)。
対象: rep27/28/29全run(記録済み出力)。LLM callなし。
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er052_open233_self_recovery_flow_runner_01 as R  # noqa: E402

R.apply_kpi_trial_switches()
OUT = os.path.join("er052_output", "open233_kpi_recovery_02_offline_01", "replay_verdict_reuse_01.json")
REPS = {27: "open233_self_recovery_flow_runner_01_rep27", 28: "open233_self_recovery_flow_runner_01_rep28",
        29: "open233_self_recovery_flow_runner_01_rep29"}
INSTANCES = {i["instance_id"]: i for i in R.build_target_instances()}


def label_critical(iid: str, sr: dict) -> list:
    """正解ラベル上の重大(SAFETY_CRITICAL_CLAIM_DEFSの定義に、fact_idと逐語核心句が一致)。"""
    fid = (sr.get("related_fact_id") or "").strip()
    hits = []
    for d in R._safety_critical_defs(iid):
        if d["related_fact_id"] == fid and R.safety_def_matches(d, sr.get("claim_text") or "", False):
            hits.append(d["sub_id"])
    return hits


def main() -> None:
    rows, tot = [], Counter()
    for rep, dn in REPS.items():
        for f in sorted(glob.glob(os.path.join("er052_output", dn, "instances_s*", "*.json"))):
            d = json.load(open(f, encoding="utf-8"))
            iid = d["instance_id"]
            text0 = INSTANCES[iid]["fixture"]["article_text"]
            texts, cur = [], text0
            for c in d["cycles"]:
                texts.append(cur)
                cur = c.get("en_text_after_rewrite", cur)
            registry: dict = {}
            for k, c in enumerate(d["cycles"]):
                text = texts[k]
                new_reg: dict = {}
                for sr in c["stage2_results"]:
                    key = R.claim_materiality_key(sr.get("claim_text", ""), sr["dev"].get("related_fact_id") or "", text)
                    if key is None:
                        continue
                    if key in registry:  # 再利用で抑制される判定
                        prev = registry[key]
                        crit = label_critical(iid, sr)
                        flip = sr["materiality"] == "BLOCKING"
                        tot["suppressed_judgments"] += 1
                        tot["suppressed_label_critical"] += 1 if crit else 0
                        tot["suppressed_but_recorded_blocking(flip)"] += 1 if flip else 0
                        rows.append({"rep": rep, "instance_id": iid, "cycle": c["cycle"], "claim": sr["claim_text"][:90],
                                     "prev_cycle": prev, "recorded_materiality_now": sr["materiality"],
                                     "label_critical": crit, "flip_to_blocking": flip})
                    so = sr.get("second_opinion") or {}
                    if sr["materiality"] != "BLOCKING" and so.get("confirmed_downgrade") and not sr.get("floor_reason"):
                        new_reg.setdefault(key, c["cycle"])  # 登録はcycle終了後(同cycle内の同一キーは再利用しない=runnerと同じ)
                        tot["registered_2of2_nonblocking"] += 1
                for kk_, v_ in new_reg.items():
                    registry.setdefault(kk_, v_)
    ok = tot["suppressed_label_critical"] == 0
    out = {"totals": dict(tot), "condition": "再利用で抑制される判定のうち、正解ラベル上の重大が0件(事前固定)",
           "condition_met": ok, "decision_for_rep30": ("ON可(条件を満たす)" if ok else "OFFのまま(条件を満たさない)"),
           "note": ("flip_to_blockingは、再利用すると見逃す(記録上は後cycleでBLOCKINGと判定された)件数。ラベル重大でなくても記録する。"
                    "条件を満たしても、flipが>0ならFableが再確認する。"),
           "rows": rows}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"totals": out["totals"], "condition_met": ok, "decision": out["decision_for_rep30"]}, ensure_ascii=False))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
