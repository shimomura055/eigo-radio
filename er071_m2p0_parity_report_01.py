# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02: M2供給のParity Gate結果レポート(¥0・ネットワークなし・Trial snapshot再生)。
出力: er071_output/m2p0_n01_production_wiring_01/parity_02.json
- 10記事(Std/Adv) x M2: Production版 rows sha256 == Trial `shortlists_r1.json` M2 rows_sha256
- 6記事: Production経路 `build_production_selection_message` の最終メッセージsha256 == Trial prep `M2P0 msg_sha256`(Opus必須3)
- demoted_allow(B'方式) == Trial `_mw_survivors(現行60窓)` (Opus必須1)
- P0無変更sha
usage: PYTHONUTF8=1 .venv/Scripts/python.exe er071_m2p0_parity_report_01.py
(Trial moduleはこの評価scriptでのみimportする。Production moduleは一切Trialをimportしない)"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er003_b1_p2_keywords as bk  # noqa: E402
import er030_key_phrase_db_hybrid_core_01 as core  # noqa: E402
import er030_key_phrase_db_hybrid_m2_supply_01 as m2  # noqa: E402
import er030_key_phrase_db_hybrid_selector_01 as sel  # noqa: E402
import er030_key_phrase_db_hybrid_source_reference_contract_01 as contract  # noqa: E402
import er030_key_phrase_db_hybrid_m2_supply_01_test_01 as T  # noqa: E402  (test helper: snapshot再生)
import er064_kp_opt_01_phase2_run_03 as TR  # noqa: E402
import er064_kp_opt_01_upstream_core as TU  # noqa: E402

OUT = "er071_output/m2p0_n01_production_wiring_01/parity_02.json"


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    r1 = json.load(open(T.R1_PATH, encoding="utf-8"))
    expected_msg = {}
    for p in T.PREP_PATHS:
        for k, v in json.load(open(p, encoding="utf-8"))["prompts"].items():
            if k.endswith("_M2P0"):
                expected_msg[k[:-5]] = v["msg_sha256"]
    static = sel.extract_static_instructions(bk.load_prompt_template())
    rows = {}
    ok_all = True
    for key in T.ARTICLE_KEYS:
        text, title, r = T.build_production_m2(key)
        rows_text = T.rows_text_for(r, title)
        exp = r1["articles"][key]
        d = {"title_match": title == exp["title"], "rows_sha256_production": sha(rows_text), "rows_sha256_trial_m2": exp["M2"]["rows_sha256"],
             "rows_sha256_match": sha(rows_text) == exp["M2"]["rows_sha256"], "n_candidates": len(r["shortlist_info"]["shortlist"]),
             "n_candidates_trial": exp["M2"]["n_candidates"], "reserved": r["m2_meta"]["reserved"], "reserved_trial": exp["M2"]["reserved"],
             "overflow_beyond_cap": r["m2_meta"]["overflow_beyond_cap"], "fragment_risk_candidates": r["m2_meta"]["fragment_risk_candidates"]}
        if key in expected_msg:
            built = sel.build_production_selection_message(title, r["shortlist_info"], static, "family_x",
                                                           containment_pairs=r["containment_pairs"])
            d["final_prompt_sha256_production"] = sha(built["message"])
            d["final_prompt_sha256_trial_m2p0"] = expected_msg[key]
            d["final_prompt_sha256_match"] = sha(built["message"]) == expected_msg[key]
        # demoted_allow (B') vs Trial current-window survivors
        st0 = core.run_stage1_for_article(text, T.dbs())
        plan = m2.compute_lookup_plan(st0)
        p1, p2 = T._snapshot_lookups()
        with p1, p2:
            exp_run = core.run_stage1_and_shortlist(text, T.dbs(), title, wiktionary_multiword_lookup_budget=plan["expanded_budget"])
        allow = m2.compute_demoted_allow(st0, plan, exp_run["results"], T.dbs())
        TR._init()
        cur = TR._replay(key, "default", 10, 60)
        d["demoted_allow_match"] = allow == TR._mw_survivors(cur["stage1"])
        d["demoted_allow_count"] = len(allow)
        d["n2"], d["expanded_budget"] = plan["n2"], plan["expanded_budget"]
        ok_all = ok_all and d["rows_sha256_match"] and d["demoted_allow_match"] and d.get("final_prompt_sha256_match", True)
        rows[key] = d
        print(key, d["rows_sha256_match"], d.get("final_prompt_sha256_match", "-"), d["demoted_allow_match"], flush=True)
    res = {"purpose": "M2供給 Parity Gate(Opus必須1/3、¥0、Trial snapshot再生、ネットワークなし)", "all_pass": ok_all,
           "p0": {"template_file_sha256": hashlib.sha256(open(bk.PROMPT_TEMPLATE_PATH, "rb").read()).hexdigest(),
                  "static_instructions_sha256": sha(static),
                  "guidance_sha256": sha(contract._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE),
                  "expected": {"template": T.P0_TEMPLATE_FILE_SHA, "static": T.P0_STATIC_SHA, "guidance": T.P0_GUIDANCE_SHA}},
           "snapshot": {"path": TU.SNAPSHOT_PATH, "sha256": TU.sha256_file(TU.SNAPSHOT_PATH)},
           "m1_params": m2.M1_PARAMS, "reserved_cap": m2.RESERVED_CAP, "threegram_cap": m2.THREEGRAM_CAP,
           "articles": rows}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ALL_PASS" if ok_all else "MISMATCH", OUT)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
