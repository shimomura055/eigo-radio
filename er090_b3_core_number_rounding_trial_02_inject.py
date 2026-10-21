# -*- coding: utf-8 -*-
"""委任_03 既知NG注入テスト(ユーザー§5-4「本来NGにすべき数値変更をCheckerが見逃したか」の測定。Trial専用)。

Luna丸め版(After)のAdvanced英語記事に、**事前定義した意図的な誤り**を1箇所ずつ注入した合成記事を作り、
現行Production Risk Flagger(rf.run_risk_flagger、Review Queue保存なし)と旧LDC(Trial専用の追加参考)で検出できるかを測る。
検出基準(事前定義): 注入した文(置換後の文字列を含む文)にRFがflagを立てれば検出。基線(未注入After記事のRF)にも同文のflagが
あった場合は『基線既存』として検出に数えない。
使い方: .venv/Scripts/python.exe er090_b3_core_number_rounding_trial_02_inject.py
"""
from __future__ import annotations

import hashlib
import os

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er053_risk_flagger_production_01 as rf
import er090_b3_core_number_rounding_trial_02_p2 as p2
import er090_b3_core_number_rounding_trial_02_run as r2

ROOT = r2.ROOT
# (id, article, find, replace, 区分)  区分: 丸め誤り(値ずれ)/限定語・変動の欠落(scope)/指定外丸め/方向反転/閾値反転/対照(Control記事ではない無変更)
MUTATIONS = [
    ("M1_pay_value_drift", "art_a31992b5", "up to about 135,000 people", "up to about 150,000 people", "丸め値ずれ(+11%)"),
    ("M2_pay_qualifier_drop", "art_a31992b5", "up to about 135,000 people, though the number varied depending on the personality trait being studied",
     "about 135,000 people in every analysis", "限定語・変動の欠落(最大/解析ごとに異なる)"),
    ("M3_pay_count_rounded", "art_a31992b5", "data from 11 studies", "data from about 10 studies", "指定外丸め(厳密な件数)"),
    ("M4_pay_threshold_flip", "art_a31992b5", "at least three times", "at most three times", "閾値方向反転"),
    ("M5_hormuz_value_drift", "art_9bd6834e", "rose about 10%", "rose about 20%", "丸め値ずれ(約2倍、20%料と混同)"),
    ("M6_hormuz_direction_flip", "art_9bd6834e", "rose about 10%", "fell about 10%", "方向反転"),
    ("M7_hormuz_exact_changed", "art_9bd6834e", "the 20% bill", "the 30% bill", "厳密値の変更"),
]


def main():
    cl.install(os.path.join(ROOT, "inject", "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    out = {"mutations": [], "baseline": {}}
    base = {}
    for aid in ("art_a31992b5", "art_9bd6834e"):
        d = p2.p2_dir(aid, "after")
        base[aid] = r2.load_json(os.path.join(d, "rf_b1b.json"))
        out["baseline"][aid] = [{"sid": i["sentence_id"], "text": i["sentence_text"][:160]} for i in base[aid]["issues"]]
    for mid, aid, find, rep, cat in MUTATIONS:
        d = p2.p2_dir(aid, "after")
        art = open(os.path.join(d, "b1b", "article.md"), encoding="utf-8").read()
        assert art.count(find) == 1, (mid, art.count(find))
        mut = art.replace(find, rep)
        md = os.path.join(ROOT, "inject", mid)
        os.makedirs(os.path.join(md, "b1b"), exist_ok=True)
        ap = os.path.join(md, "b1b", "article.md")
        open(ap, "w", encoding="utf-8", newline="\n").write(mut)
        ledger_path = os.path.join(d, "research_ledger", "verified_fact_ledger.txt")
        r2.guard(f"before inject {mid}")
        res = rf.run_risk_flagger(article_path=ap, ledger_path=ledger_path, article_id=f"d03_inject_{mid}", article_level="b1b",
                                  out_dir=os.path.join(md, "rf"), producer="deterministic_v2", run_label=r2.THEME_TAG, record_entry_point=False,
                                  budget_check=lambda: r2.guard("rf inject"))
        base_texts = {i["sentence_text"].strip() for i in base[aid]["issues"]}
        # 注入文: 置換後文字列を含む文
        hit = [i for i in res["issues"] if rep.split(",")[0] in i["sentence_text"] or rep in i["sentence_text"]]
        hit_new = [i for i in hit if i["sentence_text"].strip() not in base_texts]
        r2.guard(f"before ldc {mid}")
        with cl.logging_context(r2.THEME_TAG, f"inject_ldc_{mid}"):
            ldc = vfl01.run_deviation_check(client, open(ledger_path, encoding="utf-8").read(), mut, hook_aware=True)
        devs = ldc["parsed"].get("deviations", [])
        ldc_hit = [x for x in devs if rep.split(",")[0] in x["claim_in_article"] or x["claim_in_article"] in mut and rep in x["claim_in_article"]]
        row = {"id": mid, "article": aid, "category": cat, "find": find, "replace": rep, "rf_status": res["status"], "rf_total_issues": len(res["issues"]),
               "rf_detected_injected_sentence": bool(hit_new), "rf_flag_on_injected_sentence_already_in_baseline": bool(hit and not hit_new),
               "rf_hits": [{"sid": i["sentence_id"], "text": i["sentence_text"][:200], "conf": i["confidence"],
                            "question": [f["question"][:200] for f in i["flag_reasons"]][:2]} for i in hit],
               "ldc_overall": ldc["parsed"].get("overall_status"), "ldc_n_dev": len(devs), "ldc_detected_injected_sentence": bool(ldc_hit),
               "ldc_changed_number_any": any(x.get("changed_number") for x in devs),
               "ldc_devs": [{"claim": x["claim_in_article"][:160], "sev": x["severity"], "changed_number": x.get("changed_number")} for x in devs]}
        out["mutations"].append(row)
        print(mid, "RF detect=", row["rf_detected_injected_sentence"], "LDC detect=", row["ldc_detected_injected_sentence"], "RF total", len(res["issues"]), "LDC", row["ldc_overall"], len(devs))
    r2.save_json(os.path.join(ROOT, "evidence", "injection_test.json"), out)


if __name__ == "__main__":
    main()
