# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep16_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_30 Part3: 重大誤解原則runner既定化
# 後の実記事代表5ケースend-to-end確認)
# ============================================================
# 目的: 委任_30 Part2で既定化した重大誤解原則(Stage1[V4A+enum]・Stage2
# body[V4]・Hook専用Stage2[V4]、`runner.ENABLE_MISCONCEPTION_PRINCIPLE_
# DEFAULT`=True)を使って、実記事5代表ケース(hormuz_run03_standard/
# neg1_meta_b3prod_a2/neg3_hormuz_prodrunner_b1b/meta_run03_standard/
# bgroup_B3)をn=2・Stage1 fresh(既存reuse fixtureの`stage1_mode`を本
# 委任限定で明示的に上書き)で再実行する。
#
# 設計制約(既存er052系rep7〜rep15と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜7・rep7〜15の出力(OUT_DIR_ITER1〜7/OUT_DIR_REP7〜15)は
#   変更しない。本ファイルはrunner.OUT_DIR(=OUT_DIR_REP16、本委任でrunner
#   本体に新設済み)のみへ書く。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 5 instanceとも`stage1_mode`を"fresh"へ明示的に上書きする(reuse元の
#   既存Stage1出力は重大誤解原則配線前のV4Aであり、本委任の確認目的
#   [既定化後の挙動確認]には使えないため)。stage1_cacheはsample1/sample2
#   間で共有する(既存rep方式と同一、二重課金防止)。
from __future__ import annotations

import json
import os

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

REP16_INSTANCE_IDS = [
    "hormuz_run03_standard",
    "neg1_meta_b3prod_a2",
    "meta_run03_standard",
    "bgroup_B3",
    "neg3_hormuz_prodrunner_b1b",
]
# 委任_30 Part3続き(sample2再開時の順序決定、design書記載): neg3は既に
# 単体検証[er052_open233_self_recovery_flow_runner_01_rep16_neg3_fix_
# verify_01.py]でFAIL是正を確認済み(¥0.0758)かつコストが最も高い
# (sample1で¥3.104)ため、残り予算を優先してSafety関連2件(meta_run03_
# standard/bgroup_B3)をsample2で先に完走させ、neg3は最後に回す(予算が
# 尽きた場合、meta/bgroup_B3のn=2が優先的に確保される)。

EXPECTED_RESULTS = {
    "hormuz_run03_standard": {
        "expect": "no_rewrite_or_noun_phrase_substitution_only",
        "detail": "oil prices型の一般化・数値丸めは重大誤解原則V4で許容される"
                   "ことを期待(Rewrite 0、またはあっても名詞句置換[解決]のみ)。"
                   "Stage4到達0件を期待。",
    },
    "neg1_meta_b3prod_a2": {
        "expect": "no_rewrite_hook_and_users_claim_both",
        "detail": "Hook claim(委任_30 Part1でV4により非BLOCKING確認済み)・"
                   "users claim(委任_29/30で重大誤解原則配線後はLEDGER_"
                   "COMPLIANT、Stage1非検出)とも、実記事のcycle1からRewrite"
                   "なしで完結することを期待。",
    },
    "neg3_hormuz_prodrunner_b1b": {
        "expect": "resolved_with_one_word_deletion",
        "detail": "floor+LLM独立一致のBLOCK候補「継続→戻った」パターンが、"
                   "1語削除(接続詞・時間語等)で解消することを期待"
                   "(rep9〜rep12と同様の挙動、悪化がないことを確認)。",
    },
    "meta_run03_standard": {
        "expect": "stage4_zero_false_pass_zero",
        "detail": "Stage4到達0・false PASS(本来BLOCKINGのclaimがPASS扱い"
                   "されること)0を期待(Safety非回帰の確認)。",
    },
    "bgroup_B3": {
        "expect": "resolved_via_causal_connective_fix_safety_critical_maintained",
        "detail": "因果(\"so\")の接続詞修正で解消することを期待し、"
                   "Safety-criticalとして引き続きBLOCKING経由で検出される"
                   "こと(誤降格が無いこと)を維持することを期待。",
    },
}


def _extract_ladder_levels(result: dict) -> list:
    levels = []
    for cycle in result.get("cycles", []):
        for rec in cycle.get("rewrite_records", []):
            levels.append(rec.get("ladder_level_used"))
    return levels


def _extract_hook_stage2_calls(result: dict) -> dict:
    hook_calls = [c for c in result.get("call_log", []) if c.get("stage2_variant") == "hook"]
    body_calls = [c for c in result.get("call_log", []) if c.get("stage2_variant") == "body"]
    local_qa_calls = [c for c in result.get("call_log", []) if c.get("recovery_stage") == "local_qa"]
    recheck_calls = [c for c in result.get("call_log", []) if c.get("recovery_stage") == "stage1_recheck"]
    return {
        "hook_call_count": len(hook_calls),
        "body_call_count": len(body_calls),
        "local_qa_call_count": len(local_qa_calls),
        "stage1_recheck_call_count": len(recheck_calls),
    }


def _extract_stage2_materialities(result: dict) -> list:
    return [
        {"claim_text": sr.get("claim_text"), "materiality": sr.get("materiality"),
         "section_type": sr.get("section_type"), "stage2_route": sr.get("stage2_route"),
         "floor_reason": sr.get("floor_reason")}
        for cycle in result.get("cycles", []) for sr in cycle.get("stage2_results", [])
    ]


def _extract_before_after(result: dict) -> list:
    out = []
    for cycle in result.get("cycles", []):
        before = cycle.get("en_text_before_rewrite")
        after = cycle.get("en_text_after_rewrite")
        ja_before = cycle.get("ja_text_before_rewrite")
        ja_after = cycle.get("ja_text_after_rewrite")
        if before is not None or after is not None or ja_before is not None:
            out.append({
                "cycle": cycle.get("cycle"),
                "en_text_before_rewrite": before, "en_text_after_rewrite": after,
                "ja_text_before_rewrite": ja_before, "ja_text_after_rewrite": ja_after,
            })
    return out


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

    all_instances = {inst["instance_id"]: inst for inst in runner.build_target_instances()}
    for iid in REP16_INSTANCE_IDS:
        assert iid in all_instances, f"unknown instance_id: {iid}"
        all_instances[iid]["stage1_mode"] = "fresh"
        all_instances[iid]["stage1_source"] = None

    stage1_cache: dict = {}
    sample_results: list = []
    stopped, stop_reason = False, None

    for sample_idx in (1, 2):
        subdir = f"instances_s{sample_idx}"
        results = []
        for iid in REP16_INSTANCE_IDS:
            inst = all_instances[iid]
            cache_path = f"{runner.OUT_DIR}/{subdir}/{iid}.json"
            # 委任_30 Part3続き(neg3 FAIL是正[paired_rewrite片側locate
            # delegation]反映後、budget超過で中断したsample2残り4 instance
            # を再開する): 既に保存済みのinstance jsonがあれば再実行せず
            # 再利用する(main()の--resumeと同一原則、二重課金防止)。
            if os.path.exists(cache_path):
                with open(cache_path, encoding="utf-8") as f:
                    results.append(json.load(f))
                continue
            try:
                result = runner.run_instance(client, state, consecutive_errors, inst,
                                              enable_s1u=False, stage1_cache=stage1_cache,
                                              instances_subdir=subdir)
                results.append(result)
            except runner.TrialAbort as e:
                stopped = True
                stop_reason = str(e)
                break
        sample_results.append(results)
        # 委任_30 Part3続き: resumeで読み込んだ(=run_instance未実行の)
        # instanceについても、stage1_cacheへ再構成したStage1結果を補充する
        # (sample2のStage1がsha256一致で再利用され、resume時でも二重課金を
        # 避ける)。cycle0のstage2_results各行の"dev"は元のStage1
        # deviationsそのもの(委任_20 W2のenumerationフィールド含む)であり、
        # 再構成の忠実度は高い(既知の限界: cycle0が存在しないACCEPTABLE_
        # STAGE1 instanceは本rep16の5 instanceには該当しない)。
        import hashlib
        for iid, r in zip(REP16_INSTANCE_IDS, results):
            fx = all_instances[iid]["fixture"]
            cache_key = hashlib.sha256(
                (fx["ledger_text"] + "␟" + fx["article_text"] + "␟"
                 + (fx.get("source_article_text") or "")).encode("utf-8")
            ).hexdigest()
            if cache_key in stage1_cache:
                continue
            cycles = r.get("cycles") or []
            if not cycles:
                stage1_cache[cache_key] = {"overall_status": "ACCEPTABLE_LLM", "deviations": []}
                continue
            devs = [sr["dev"] for sr in cycles[0].get("stage2_results", [])]
            stage1_cache[cache_key] = {
                "overall_status": "LEDGER_DEVIATION" if devs else "ACCEPTABLE_LLM",
                "deviations": devs,
            }
        if stopped:
            break

    by_id_per_sample = [{r["instance_id"]: r for r in results} for results in sample_results]
    per_case = []
    for iid in REP16_INSTANCE_IDS:
        entry = {"instance_id": iid, "expected": EXPECTED_RESULTS[iid]}
        for si, by_id in enumerate(by_id_per_sample, start=1):
            r = by_id.get(iid)
            if r is None:
                entry[f"sample{si}"] = None
                continue
            entry[f"sample{si}"] = {
                "final_state": r["final_state"], "stage4_reason": r.get("stage4_reason"),
                "total_cost_jpy": r["total_cost_jpy"],
                "ladder_levels_used": _extract_ladder_levels(r),
                "call_breakdown": _extract_hook_stage2_calls(r),
                "stage2_materialities": _extract_stage2_materialities(r),
                "before_after_by_cycle": _extract_before_after(r),
            }
        per_case.append(entry)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_instances_completed_per_sample": [len(r) for r in sample_results],
        "n_instances_planned": len(REP16_INSTANCE_IDS),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "per_case": per_case,
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_rep16.json", {
        "summary": summary,
        "instance_results_sample1": [
            {k: v for k, v in r.items() if k != "call_log"} for r in sample_results[0]
        ] if sample_results else [],
        "instance_results_sample2": (
            [{k: v for k, v in r.items() if k != "call_log"} for r in sample_results[1]]
            if len(sample_results) >= 2 else None
        ),
    })
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str)[:6000])


if __name__ == "__main__":
    main()
