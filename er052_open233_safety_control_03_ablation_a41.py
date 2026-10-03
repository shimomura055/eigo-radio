# -*- coding: utf-8 -*-
# OPEN-233-SELF-RECOVERY-TRIAL-01 委任_55 作業4: A4-1の2/2誤降格(V7)の原因切り分け用の診断(rubric修正ではない)。
# V7からどの文が効いたかを見るため、A4グループ(A4-0/A4-1/A4-2)のStage 2のみを、V7の2変種(診断専用、
# どちらも本番rubricにはしない)でn=1ずつ実行する。想定費用 約¥0.3(Guardrail ¥15の範囲内)。
#   abl1: V7から(2)自然な推論の段落を除いたもの
#   (--set2) abl3: V7から判定済みの例3行を除いたもの / abl4: V7から(3)判断に迷う場合の段落を除いたもの
#   abl2: V7の(2)から「この場合、上記の『他者の内心を断定する記述』のBLOCKING条件は…適用しません」を除いたもの
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_element_trial_safety_control_02 as sc02
import er052_open233_self_recovery_r3dprime_calibration_01 as r3d
import er052_open233_self_recovery_stage2_calibration_01 as s2c

OUT = "er052_output/open233_safety_control_03/ablation_a41"
V7 = s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7
NL2 = chr(10) * 2


def variants() -> dict:
    i2 = V7.index("(2) 自然な推論")
    i3 = V7.index("(3) 判断に迷う場合")
    abl1 = V7[:i2] + V7[i3:]
    sent_start = V7.index("この場合、上記の「他者の内心を断定する記述」の")
    sent_end = V7.index("適用しません。", sent_start) + len("適用しません。")
    abl2 = V7[:sent_start].rstrip() + "\n\n" + V7[sent_end:].lstrip("\n")
    assert abl1 != V7 and abl2 != V7
    import sys
    if "--set3" in sys.argv:
        # 加算方式(V6にV7の一部だけを足す): abl5=ヘッダ(3区分の定義)のみ / abl6=(2)の段落のみ / abl7=(3)の段落のみ
        i1 = V7.index("(1) 条件つき")
        base = V7[:V7.index("【線引きの正式採用")].rstrip()
        hdr = V7[V7.index("【線引きの正式採用"):i1].rstrip()
        p2 = V7[i2:i3].rstrip()
        p3 = V7[i3:V7.index("判定済みの例")].rstrip()
        return {"abl5_V6_plus_header_only": base + NL2 + hdr,
                "abl6_V6_plus_para2_only": base + NL2 + p2,
                "abl7_V6_plus_para3_only": base + NL2 + p3}
    if "--set2" in sys.argv:
        ex = V7.index("判定済みの例")
        abl3 = V7[:ex].rstrip()
        abl4 = V7[:i3] + V7[ex:]
        assert abl3 != V7 and abl4 != V7
        return {"abl3_no_examples": abl3, "abl4_no_para3": abl4}
    return {"abl1_no_para2": abl1, "abl2_no_mental_state_override": abl2}


def main():
    sc02.OUT_DIR = OUT
    sc02.BUDGET_STATE_PATH = f"{OUT}/budget_state.json"
    sc02.TOTAL_BUDGET_JPY = 3.0
    client = vfl01.get_client()
    state = sc02.load_budget_state()
    ce = [0]
    group = next(g for g in sc02.safety_critical_groups() if g["group_id"] == "A4")
    claims = s2c.build_claim_records_for_group(group)
    rows = {}
    for name, v7txt in variants().items():
        rubric = s2c.RUBRIC_R3_TRIPLE_PRIME + "\n" + s2c.MISCONCEPTION_PRINCIPLE_TEXT_V6 + v7txt[len(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V6):]
        res = sc02.guarded_batch_call(
            state, ce, f"abl_{name}", f"{OUT}/{name}.json",
            client=client, verified_ledger_text=group["fixture"]["ledger_text"],
            source_article_text=group["fixture"].get("source_article_text"),
            claims=claims, rubric_text=rubric)
        rows[name] = [{"sub_id": c["sub_id"], "claim_text": c["claim_text"],
                       "materiality": next((j["materiality"] for j in res["parsed"]["judgments"]
                                            if j["claim_index"] == i), None)}
                      for i, c in enumerate(claims)]
    out = {"cost_jpy": round(state["cumulative_jpy"], 4), "ledger_text": group["fixture"]["ledger_text"],
           "rows": rows}
    import sys
    sc02.save_json(f"{OUT}/result{'_set3' if '--set3' in sys.argv else ('_set2' if '--set2' in sys.argv else '')}.json", out)
    print(json.dumps({"cost_jpy": out["cost_jpy"],
                      "rows": {k: [(r["sub_id"], r["materiality"]) for r in v] for k, v in rows.items()}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
