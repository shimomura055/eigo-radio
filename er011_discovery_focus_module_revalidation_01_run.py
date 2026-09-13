# ============================================================
# er011_discovery_focus_module_revalidation_01_run.py
# 管理ID: FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01
# ============================================================
# 目的(ユーザー決定 2026-09-13): Discovery/WhyのFocus Module Part A
# (er011_discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK、
# 一字一句不変)を、現在のProduction基盤・現在のLedger/QA条件で
# 再検証する。同一テーマ・同一Verified Fact Ledgerで baseline(Focus
# なし)/focus(Part Aあり)をA2/B1各1本ずつ、合計4記事生成し比較する。
# **Trial(Production実装ではない)。Production採用はしない**
# (Gate 1=VALIDATED相当までが上限)。Production registry登録・Focus
# ModuleのProduction配線・Point Role PlanningへのFocus接続・Audio/TTSは
# 一切行わない(記事生成→既存QA一式まで)。
#
# テーマ・Ledger選定(新規Research/Ledger作成はしない):
#   FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-TRIAL-12
#   (`er011_output/discovery_generalization_wake_before_alarm_trial_12`)の
#   research/verified_fact_ledger.txt・research/writer_topic.jsonを
#   read-onlyで再利用する。理由: (1) Towels Trial-11・Wake Trial-12は
#   いずれもledger_deviation overall_status="LEDGER_COMPLIANT"で検証済み、
#   (2) Wake Trial-12はTowels Trial-11より新しい(同日2026-09-13close)、
#   (3) Wake Trial-12の記事生成コスト実測(writer_a2=13.71円、
#   writer_b1=20.59円、1 arm分)がTowels Trial-11(writer_a2=28.30円、
#   writer_b1=33.94円)より低く、4 arm実行時の予算余裕が大きい。
#
# 設計: 条件差はeditorial_type_module_block(Focus Module Part Aの
# 有無)のみ。他パラメータ・モデル・Prompt・QAは現行Production
# (er003_v1_n3_01_articles_generate.run_one_pattern)のまま、無変更で
# 直接呼ぶ(Household最終候補/Towels Trial-11/Wake Trial-12と同じ
# 再利用パターン)。Point Role Planningへの新規接続は行わない
# (run_point_role_planningは既存シグネチャのまま、topic/ledgerのみ渡す)。
#
# 費用上限: 合計¥320(見込み: 2 arm x (a2+b1) x 約17円平均 = 概算¥70〜130、
# retry込みでも上限余裕あり)。同期実行のみ。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_discovery_focus_module_revalidation_01_run.py [stage ...]
#   stage: gate4 | a2_baseline | a2_focus | b1_baseline | b1_focus | evaluate | cost | all(省略時)
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
import er011_discovery_stage3_rule_adjustment_trial_09 as t9  # 読み取り専用の再利用(t9のOUT_DIRへは書き込まない)

THEME_ID = "discovery_focus_module_revalidation_01"
OUT_DIR = f"er011_output/{THEME_ID}"
BUDGET_JPY_CAP = 320.0

# 既存Wake Trial-12のLedger/topicをread-onlyで再利用(新規Research/Ledger作成なし)
SOURCE_TRIAL_DIR = "er011_output/discovery_generalization_wake_before_alarm_trial_12"
SOURCE_LEDGER_PATH = f"{SOURCE_TRIAL_DIR}/research/verified_fact_ledger.txt"
SOURCE_TOPIC_PATH = f"{SOURCE_TRIAL_DIR}/research/writer_topic.json"

# Part A本体のみ(t9.CURRENT_FOCUS_BLOCKを無変更でそのまま使う。Part B文言
# [cautionary_clause]は一切追加しない=Part A単独条件)。
DISCOVERY_FOCUS_MODULE_PART_A_BLOCK = t9.CURRENT_FOCUS_BLOCK

LEVELS = {
    "a2": {"label": "A2", "instruction": prod_gen.A2_KAI1_INSTRUCTION, "stage_tag": "writer_a2"},
    "b1b": {"label": "B1B", "instruction": prod_gen.B1_B_DIRECT_INSTRUCTION, "stage_tag": "writer_b1"},
}

ARMS = {
    "baseline": "",  # Focus Moduleなし(既存Production既定挙動)
    "focus": DISCOVERY_FOCUS_MODULE_PART_A_BLOCK,
}

# 保険文検出regex(Trial-10/Towels Trial-11/Wake Trial-12と同一定義、
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
# 費用実測(全provider対応、Towels Trial-11/Wake Trial-12の
# compute_cost_jpy_so_farと同一ロジック、read-onlyで転記して再利用)。
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
# Gate 4相当の静的確認(Production関数の再定義・monkeypatchをしていない
# ことの機械確認。Towels Trial-11/Wake Trial-12と同一ロジック)。
# ============================================================
def gate4_check_stage() -> dict:
    used_names = ["build_common_block", "build_prompt", "A2_KAI1_INSTRUCTION",
                  "B1_B_DIRECT_INSTRUCTION", "run_one_pattern", "POINT_OVERLAP_ARTICLE_RETRY_MAX"]
    not_reassigned = all(name in vars(prod_gen) for name in used_names)
    placeholder_present = "{editorial_type_module_block}" in prod_gen.COMMON_BLOCK_TEMPLATE

    part_a_block_byte_identical_to_t9 = DISCOVERY_FOCUS_MODULE_PART_A_BLOCK == t9.CURRENT_FOCUS_BLOCK
    part_b_clause_absent = "取扱説明書" not in DISCOVERY_FOCUS_MODULE_PART_A_BLOCK

    # 論点C観察用: run_point_role_planningのシグネチャにeditorial_type_module_block
    # 引数が存在しないことを機械確認する(接続実装は行わない、観察のみ)。
    import inspect
    import er011_point_role_value_planning_01 as point_planning
    role_planning_params = list(inspect.signature(point_planning.run_point_role_planning).parameters)
    role_planning_lacks_focus_param = "editorial_type_module_block" not in role_planning_params

    result = {
        "prod_gen_used_names_present_and_not_reassigned": not_reassigned,
        "common_block_template_has_editorial_type_module_block_placeholder": placeholder_present,
        "part_a_block_byte_identical_to_t9_current_focus_block": part_a_block_byte_identical_to_t9,
        "part_b_cautionary_clause_absent_from_block": part_b_clause_absent,
        "point_overlap_article_retry_max_loop_budget": prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX,
        "run_point_role_planning_signature_params": role_planning_params,
        "role_planning_lacks_focus_param_observation_only": role_planning_lacks_focus_param,
        "focus_module_source": ("er011_discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK"
                                 "(read-only reuse, unmodified, Part A only)"),
        "conclusion": "PASS" if (not_reassigned and placeholder_present and part_a_block_byte_identical_to_t9
                                  and part_b_clause_absent) else "FAIL_NEEDS_REVIEW",
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
# Step 1: 記事生成(level x arm、既存経路そのまま。再抽選[N追加]は行わない)。
# ============================================================
def generate_article_stage(level: str, arm: str) -> dict:
    meta = LEVELS[level]
    editorial_block = ARMS[arm]
    arm_tag = f"{level}_{arm}"
    out_dir = f"{OUT_DIR}/{arm_tag}"
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    verified_ledger_text, topic_ja = load_reused_ledger_and_topic()
    common_block = prod_gen.build_common_block(
        master_full_text, topic_ja, verified_ledger_text,
        editorial_type_module_block=editorial_block)
    prompt = prod_gen.build_prompt(common_block, meta["instruction"])

    t0 = time.time()
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    theme_tag_for_cost = f"{THEME_ID}_{arm_tag}"
    with cl.logging_context(theme_tag_for_cost, meta["stage_tag"]):
        result = prod_gen.run_one_pattern(
            client, theme_tag_for_cost, meta["label"], prompt, verified_ledger_text, topic_ja, out_dir)
    elapsed = round(time.time() - t0, 2)

    article_text = result.get("article_text")
    insurance_hits = detect_insurance_sentences(article_text) if article_text else []
    summary = {k: v for k, v in result.items() if k != "article_text"}
    summary["arm"] = arm
    summary["level"] = level
    summary["editorial_type_module_block_used"] = bool(editorial_block)
    summary["elapsed_seconds"] = elapsed
    summary["word_count"] = len((article_text or "").split())
    summary["insurance_sentence_hits_broad_regex"] = insurance_hits
    summary["insurance_sentence_hit_count"] = len(insurance_hits)
    save_json(f"{out_dir}/run_summary.json", summary)
    print(f"[{THEME_ID}][{arm_tag}] article: status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
          f"word_count={summary['word_count']} insurance_hits={len(insurance_hits)} elapsed={elapsed}s")
    return summary


# ============================================================
# Step 2: 評価(t9.analyze_runを無変更で流用)。
# ============================================================
def evaluate_stage() -> dict:
    analysis_all = {}
    for level in ("a2", "b1b"):
        for arm in ("baseline", "focus"):
            arm_tag = f"{level}_{arm}"
            out_dir = f"{OUT_DIR}/{arm_tag}"
            run_summary_path = f"{out_dir}/run_summary.json"
            if not os.path.exists(run_summary_path):
                print(f"[{THEME_ID}][evaluate] {arm_tag}: run_summary.jsonが無く、analyze_runをスキップします。")
                continue
            result = load_json(run_summary_path)
            analysis = t9.analyze_run(out_dir, result)
            analysis["insurance_sentence_hit_count"] = result.get("insurance_sentence_hit_count")
            analysis["insurance_sentence_hits_broad_regex"] = result.get("insurance_sentence_hits_broad_regex")
            save_json(f"{out_dir}/analysis.json", analysis)
            analysis_all[arm_tag] = analysis

    save_json(f"{OUT_DIR}/comparison_summary.json", analysis_all)
    print(f"[{THEME_ID}] evaluate_stage完了。arms={list(analysis_all.keys())}")
    return analysis_all


def main() -> dict:
    stages = sys.argv[1:] or ["all"]
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    arm_tags = [("a2", "baseline"), ("a2", "focus"), ("b1b", "baseline"), ("b1b", "focus")]

    if stages == ["all"]:
        results = {}
        results["gate4"] = gate4_check_stage()
        for level, arm in arm_tags:
            arm_tag = f"{level}_{arm}"
            try:
                results[arm_tag] = generate_article_stage(level, arm)
            except (RuntimeError, AssertionError) as e:
                results[arm_tag] = {"level": level, "arm": arm, "status": "STOP", "error": str(e)}
                print(f"[{THEME_ID}][{arm_tag}] STOP: {e}")
            cost_stage()
        results["evaluate"] = evaluate_stage()
        save_json(f"{OUT_DIR}/e2e_run_summary.json", results)
        print(f"[{THEME_ID}] 完了。")
        return results

    result = {}
    for s in stages:
        if s == "gate4":
            result["gate4"] = gate4_check_stage()
        elif s in ("a2_baseline", "a2_focus", "b1_baseline", "b1_focus", "b1b_baseline", "b1b_focus"):
            level, arm = (s.replace("b1_", "b1b_")).split("_", 1)
            result[f"{level}_{arm}"] = generate_article_stage(level, arm)
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
