# ============================================================
# er011_discovery_focus_role_planning_connection_trial_01_run.py
# 管理ID: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01
# (Fable修正指示1回目、STOP解除、手順3)
# ============================================================
# 目的(ユーザー確定判断、FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-
# TRIAL-01_REPORT.md冒頭原文): Discovery Focus Module Part A(er011_
# discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK)に加えて、
# Point Role Planningへ短いPoint役割hint(案2のみ、案2'は対象外)を接続した
# 場合の効果を、focus単独(接続なし)と比較する。**Trial(Production実装
# ではない)。Production採用の承認ではない**(Gate 1=VALIDATED相当までが
# 上限)。Production registry登録・Focus ModuleのProduction配線・Point
# Role PlanningへのProduction接続・Audio/TTSは一切行わない(記事生成→
# 既存QA一式まで)。
#
# 接続関数: er011_point_role_planning_focus_connection_trial_04.
# run_one_pattern_connected(Fable修正指示によりtrial_03からtrial_04へ
# 差し替え済み。現行Production run_one_pattern[OPEN-141差分QA込み]と
# hint注入以外の差分ゼロであることをtrial_04_test_01.pyのGate 4テストで
# 機械確認済み)。
#
# 案2 hint文言: `er011_discovery_focus_role_planning_connection_draft_01.md`
# (FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-DESIGN-01で設計、
# 未配線draft)のDISCOVERY_WHY_POINT_ROLE_HINT_BLOCKをそのまま転記
# (新規文言をここで創作しない)。案2'(Main Story逆方向注記)は使用しない
# (ユーザー確定判断)。
#
# テーマ・Ledger: FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01が既に
# 使用したwake-before-alarm Ledger(`er011_output/discovery_generalization_
# wake_before_alarm_trial_12`)をread-onlyで再利用(新規Research/Ledger
# 作成はしない、ユーザー確定判断)。
#
# 4記事構成:
#   - focus単独(接続なし)A2/B1B: 再利用(`er011_output/discovery_focus_
#     module_revalidation_01/{a2_focus,b1b_focus}`、再生成しない、¥0)
#   - focus+接続 A2/B1B: 新規生成(本ドライバ、run_one_pattern_connected)
#
# 費用上限: ¥300(ユーザー確定)。実費はcost_summary.jsonに記録し、
# 上限到達時は例外を送出して以降のstageを実行しない。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_discovery_focus_role_planning_connection_trial_01_run.py [stage ...]
#   stage: gate4 | a2_connected | b1_connected | evaluate | cost | all(省略時)
# ============================================================
from __future__ import annotations

import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er011_discovery_stage3_rule_adjustment_trial_09 as t9  # 読み取り専用の再利用
import er011_point_role_planning_focus_connection_trial_04 as t4

THEME_ID = "discovery_focus_role_planning_connection_trial_01"
OUT_DIR = f"er011_output/{THEME_ID}"
BUDGET_JPY_CAP = 300.0

# 既存Wake Trial-12のLedger/topicをread-onlyで再利用(新規Research/Ledger作成なし、
# discovery_focus_module_revalidation_01と同一のLedger/topicを使う)
SOURCE_TRIAL_DIR = "er011_output/discovery_generalization_wake_before_alarm_trial_12"
SOURCE_LEDGER_PATH = f"{SOURCE_TRIAL_DIR}/research/verified_fact_ledger.txt"
SOURCE_TOPIC_PATH = f"{SOURCE_TRIAL_DIR}/research/writer_topic.json"

# focus単独(接続なし)baselineの再利用元(再生成しない)
FOCUS_ONLY_BASELINE_DIR = "er011_output/discovery_focus_module_revalidation_01"

# Part A本体のみ(t9.CURRENT_FOCUS_BLOCKを無変更でそのまま使う)
DISCOVERY_FOCUS_MODULE_PART_A_BLOCK = t9.CURRENT_FOCUS_BLOCK

# 案2 hint文言(er011_discovery_focus_role_planning_connection_draft_01.md
# からの転記、新規文言はここで創作しない)
DISCOVERY_WHY_POINT_ROLE_HINT_BLOCK = (
    "This is a Discovery/Why article (Main Story presents a phenomenon without "
    "fully resolving why it happens). When planning Point One and Point Two, prefer roles the Ledger actually supports "
    "from among: a distinct causal mechanism Main Story left unresolved, an unexpected contributing factor from a "
    "different angle (psychological, environmental/design-related, or social/contextual) than the other Point, or a "
    "limitation on what the evidence actually explains. Do not assign both Points the same causal angle, and do not "
    "let either Point simply restate the phenomenon already described in Main Story."
)

LEVELS = {
    "a2": {"label": "A2", "instruction": prod_gen.A2_KAI1_INSTRUCTION, "stage_tag": "writer_a2"},
    "b1b": {"label": "B1B", "instruction": prod_gen.B1_B_DIRECT_INSTRUCTION, "stage_tag": "writer_b1"},
}

# 保険文検出regex(discovery_focus_module_revalidation_01_run.pyと同一定義、
# read-onlyで転記して再利用)。
_VERB = r"(?:check|consult|ask|see|refer to|look at|read|follow)"
_SOURCE = r"(?:instructions?|manuals?|guides?|guidelines?|manufacturers?|makers?|professionals?|experts?|labels?|packagings?|packages?)"
INSURANCE_RE = re.compile(_VERB + r"[^.!?]{0,80}" + _SOURCE, re.IGNORECASE)


def detect_insurance_sentences(article_text: str) -> list:
    return [m.group(0) for m in INSURANCE_RE.finditer(article_text or "")]


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 費用実測(discovery_focus_module_revalidation_01_run.pyと同一ロジック、
# read-onlyで転記して再利用)。
# ============================================================
USD_JPY = 160.0
_PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter, tier="Standard"):
    for p in _PRICING:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter and p.get("tier", "Standard") == tier:
            return p["price"]
    raise KeyError((provider, model, meter, tier))


def _call_cost_usd(r: dict) -> tuple:
    provider = r.get("provider")
    model = r.get("model_id") or r.get("model")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    try:
        if provider == "openai":
            billable_in = max(it - ct, 0)
            cost = (billable_in / 1e6) * _price("openai", model, "input_tokens") \
                + (ct / 1e6) * _price("openai", model, "cached_input_tokens") \
                + (ot / 1e6) * _price("openai", model, "output_tokens")
            wsc = r.get("web_search_call_count") or 0
            cost += (wsc / 1000) * _price("openai", "N/A (tool, all models)", "web_search_call")
            return cost, False
        return 0.0, True
    except KeyError:
        return 0.0, True


def compute_cost_jpy_so_far() -> dict:
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    if not os.path.exists(log_path):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "by_stage_jpy": {}, "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, by_stage, unpriced = 0.0, {}, {}, 0
    n = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cost, up = _call_cost_usd(rec)
            total_usd += cost
            by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + cost
            stage_key = rec.get("theme_id") or rec.get("stage")
            by_stage[stage_key] = by_stage.get(stage_key, 0.0) + cost * USD_JPY
            unpriced += int(up)
            n += 1
    return {
        "total_jpy": round(total_usd * USD_JPY, 2),
        "by_provider_jpy": {k: round(v * USD_JPY, 2) for k, v in by_provider.items()},
        "by_stage_jpy": {k: round(v, 2) for k, v in by_stage.items()},
        "unpriced_records": unpriced, "total_records": n,
    }


def cost_stage() -> dict:
    result = compute_cost_jpy_so_far()
    save_json(f"{OUT_DIR}/cost_summary.json", result)
    print(f"[{THEME_ID}][cost] 実測合計={result['total_jpy']} JPY (上限{BUDGET_JPY_CAP}) "
          f"by_provider={result['by_provider_jpy']}")
    if result["total_jpy"] > BUDGET_JPY_CAP:
        raise RuntimeError(f"費用上限超過(実測{result['total_jpy']}円 > 上限{BUDGET_JPY_CAP}円)。STOP。")
    return result


# ============================================================
# Gate 4相当の静的確認(実行直前の再確認。Trial-03実施時点[d79a9f9a]からの
# Production 3ファイルの無編集をgit diffで再確認し、trial_04が現行
# run_one_patternと差分ゼロ[hint注入除く]であることも再確認する)。
# ============================================================
def gate4_check_stage() -> dict:
    import inspect
    import subprocess

    diff_stat = subprocess.run(
        ["git", "diff", "--stat", "d79a9f9a..HEAD", "--",
         "er003_v1_n3_01_articles_generate.py", "er011_point_role_value_planning_01.py",
         "er006_pool_pilot_01_writer.py"],
        capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)) or ".",
    ).stdout.strip()
    only_n3_01_changed = (
        "er003_v1_n3_01_articles_generate.py" in diff_stat
        and "er011_point_role_value_planning_01.py" not in diff_stat
        and "er006_pool_pilot_01_writer.py" not in diff_stat
    )

    used_names = ["build_common_block", "build_prompt", "A2_KAI1_INSTRUCTION",
                  "B1_B_DIRECT_INSTRUCTION", "run_one_pattern", "POINT_OVERLAP_ARTICLE_RETRY_MAX"]
    not_reassigned = all(name in vars(prod_gen) for name in used_names)
    placeholder_present = "{editorial_type_module_block}" in prod_gen.COMMON_BLOCK_TEMPLATE

    part_a_block_byte_identical_to_t9 = DISCOVERY_FOCUS_MODULE_PART_A_BLOCK == t9.CURRENT_FOCUS_BLOCK

    trial04_hint_param_present = "point_role_hint_block" in inspect.signature(
        t4.run_one_pattern_connected).parameters

    result = {
        "git_diff_stat_since_trial03_baseline_d79a9f9a": diff_stat,
        "only_n3_01_articles_generate_changed_since_trial03": only_n3_01_changed,
        "prod_gen_used_names_present_and_not_reassigned": not_reassigned,
        "common_block_template_has_editorial_type_module_block_placeholder": placeholder_present,
        "part_a_block_byte_identical_to_t9_current_focus_block": part_a_block_byte_identical_to_t9,
        "trial04_run_one_pattern_connected_has_hint_param": trial04_hint_param_present,
        "trial04_gate4_mechanical_proof_location": (
            "er011_point_role_planning_focus_connection_trial_04_test_01.py::"
            "Gate4SourceReconstructionTests(実行毎にProduction run_one_patternとの"
            "差分がhint注入関連4点のみであることを機械確認済み)"
        ),
        "conclusion": "PASS" if (only_n3_01_changed and not_reassigned and placeholder_present
                                  and part_a_block_byte_identical_to_t9 and trial04_hint_param_present)
        else "FAIL_NEEDS_REVIEW",
    }
    save_json(f"{OUT_DIR}/audit/gate4_check.json", result)
    print(f"[{THEME_ID}] gate4_check_stage: {result['conclusion']}")
    if result["conclusion"] != "PASS":
        raise RuntimeError(f"Gate 4静的確認失敗: {result}")
    return result


def load_reused_ledger_and_topic() -> tuple:
    if not os.path.exists(SOURCE_LEDGER_PATH):
        raise RuntimeError(f"再利用元Ledgerが見つかりません: {SOURCE_LEDGER_PATH}")
    verified_ledger_text = open(SOURCE_LEDGER_PATH, encoding="utf-8").read()
    topic_ja = load_json(SOURCE_TOPIC_PATH)["topic_ja"]
    return verified_ledger_text, topic_ja


# ============================================================
# Step 1: 「focus+接続」記事生成(level x connected、新規生成)。
# ============================================================
def generate_connected_article_stage(level: str) -> dict:
    meta = LEVELS[level]
    arm_tag = f"{level}_connected"
    out_dir = f"{OUT_DIR}/{arm_tag}"
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    verified_ledger_text, topic_ja = load_reused_ledger_and_topic()
    common_block = prod_gen.build_common_block(
        master_full_text, topic_ja, verified_ledger_text,
        editorial_type_module_block=DISCOVERY_FOCUS_MODULE_PART_A_BLOCK)
    prompt = prod_gen.build_prompt(common_block, meta["instruction"])

    t0 = time.time()
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    theme_tag_for_cost = f"{THEME_ID}_{arm_tag}"
    with cl.logging_context(theme_tag_for_cost, meta["stage_tag"]):
        result = t4.run_one_pattern_connected(
            client, theme_tag_for_cost, meta["label"], prompt, verified_ledger_text, topic_ja, out_dir,
            point_role_hint_block=DISCOVERY_WHY_POINT_ROLE_HINT_BLOCK)
    elapsed = round(time.time() - t0, 2)

    article_text = result.get("article_text")
    insurance_hits = detect_insurance_sentences(article_text) if article_text else []
    summary = {k: v for k, v in result.items() if k != "article_text"}
    summary["arm"] = "focus_connected"
    summary["level"] = level
    summary["editorial_type_module_block_used"] = True
    summary["point_role_hint_block_used"] = True
    summary["elapsed_seconds"] = elapsed
    summary["word_count"] = len((article_text or "").split())
    summary["insurance_sentence_hits_broad_regex"] = insurance_hits
    summary["insurance_sentence_hit_count"] = len(insurance_hits)
    save_json(f"{out_dir}/run_summary.json", summary)
    with open(f"{out_dir}/point_role_hint_block_used.txt", "w", encoding="utf-8") as f:
        f.write(DISCOVERY_WHY_POINT_ROLE_HINT_BLOCK)
    print(f"[{THEME_ID}][{arm_tag}] article: status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
          f"word_count={summary['word_count']} insurance_hits={len(insurance_hits)} elapsed={elapsed}s")
    return summary


# ============================================================
# Step 2: 評価(t9.analyze_runを無変更で流用、focus単独baselineは再利用元
# ディレクトリを直接参照)。
# ============================================================
def evaluate_stage() -> dict:
    analysis_all = {}
    for level in ("a2", "b1b"):
        # focus単独(接続なし、再利用)
        baseline_out_dir = f"{FOCUS_ONLY_BASELINE_DIR}/{level}_focus"
        baseline_summary_path = f"{baseline_out_dir}/run_summary.json"
        if os.path.exists(baseline_summary_path):
            baseline_result = load_json(baseline_summary_path)
            baseline_analysis = t9.analyze_run(baseline_out_dir, baseline_result)
            baseline_analysis["insurance_sentence_hit_count"] = baseline_result.get("insurance_sentence_hit_count")
            baseline_analysis["insurance_sentence_hits_broad_regex"] = baseline_result.get(
                "insurance_sentence_hits_broad_regex")
            baseline_analysis["reused_from"] = baseline_out_dir
            analysis_all[f"{level}_focus"] = baseline_analysis
        else:
            print(f"[{THEME_ID}][evaluate] {level}_focus: 再利用元run_summary.jsonが見つかりません"
                  f"({baseline_summary_path})。スキップします。")

        # focus+接続(新規生成)
        connected_out_dir = f"{OUT_DIR}/{level}_connected"
        connected_summary_path = f"{connected_out_dir}/run_summary.json"
        if os.path.exists(connected_summary_path):
            connected_result = load_json(connected_summary_path)
            connected_analysis = t9.analyze_run(connected_out_dir, connected_result)
            connected_analysis["insurance_sentence_hit_count"] = connected_result.get("insurance_sentence_hit_count")
            connected_analysis["insurance_sentence_hits_broad_regex"] = connected_result.get(
                "insurance_sentence_hits_broad_regex")
            analysis_all[f"{level}_connected"] = connected_analysis
        else:
            print(f"[{THEME_ID}][evaluate] {level}_connected: run_summary.jsonが無く、"
                  f"analyze_runをスキップします。")

    save_json(f"{OUT_DIR}/comparison_summary.json", analysis_all)
    print(f"[{THEME_ID}] evaluate_stage完了。arms={list(analysis_all.keys())}")
    return analysis_all


def main() -> dict:
    stages = sys.argv[1:] or ["all"]
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    if stages == ["all"]:
        results = {}
        results["gate4"] = gate4_check_stage()
        for level in ("a2", "b1b"):
            tag = f"{level}_connected"
            try:
                results[tag] = generate_connected_article_stage(level)
            except (RuntimeError, AssertionError) as e:
                results[tag] = {"level": level, "arm": "focus_connected", "status": "STOP", "error": str(e)}
                print(f"[{THEME_ID}][{tag}] STOP: {e}")
            cost_stage()
        results["evaluate"] = evaluate_stage()
        save_json(f"{OUT_DIR}/e2e_run_summary.json", results)
        print(f"[{THEME_ID}] 完了。")
        return results

    result = {}
    for s in stages:
        if s == "gate4":
            result["gate4"] = gate4_check_stage()
        elif s in ("a2_connected", "b1_connected", "b1b_connected"):
            level = "b1b" if s.startswith("b1") else "a2"
            result[f"{level}_connected"] = generate_connected_article_stage(level)
        elif s == "evaluate":
            result["evaluate"] = evaluate_stage()
        elif s == "cost":
            result["cost"] = cost_stage()
        else:
            print(f"unknown stage: {s}")
    save_json(f"{OUT_DIR}/e2e_run_summary_partial_{'_'.join(stages)}.json", result)
    return result


if __name__ == "__main__":
    main()
