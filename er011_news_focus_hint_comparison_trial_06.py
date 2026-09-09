# ============================================================
# er011_news_focus_hint_comparison_trial_06.py
# FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06 (Lane A Step A3)
# ============================================================
# 目的(ユーザー決定 2026-09-09、A3-UDR-1=(i)): Point Role hint(Trial-03、
# VALIDATED)+ News Focus Module(Trial-01設計/Trial-02文言)+ G1修正済み
# Production(OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01、
# PRODUCTION_WIRED)の組み合わせで、Hanshin Ledger固定・N=3の再比較Trialを
# 実施する。VALIDATEDならFocus Module+hint接続をまとめて配線判断(ユーザー)。
# **Trial(Production実装ではない)**。Production/Prompt/SSOT編集・Git操作は
# 一切行わない。monkeypatch・グローバル書き換えなし。TTSは実行しない
# (text-onlyまで)。
#
# A3-UDR-2=(i): 当面は手動Mode判定+手動Ledger供給を正式initial pathとする
# (Trend Synthesisと同じ機構)。本Trialでも同じ機構(Gate 6項目チェックリスト
# の事後手動判定結果をrun_metadataへ記録)を踏襲する。A-UDR-17(mode名
# major_daily_newsの正式登録・文言確定)は本Trial結果後、ユーザー判断。
# 閾値0.40・Loop Budget 2は不変(変更していない)。
#
# ------------------------------------------------------------
# 再利用(import・無変更、コピー改変はしない):
# ------------------------------------------------------------
#   - er011_point_role_planning_focus_connection_trial_03(t3、既存
#     VALIDATED Trial、Fable受入済み): run_one_pattern_connected /
#     run_point_role_planning_connected / MAJOR_DAILY_NEWS_POINT_ROLE_
#     HINT_BLOCK / MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK / load_text /
#     HANSHIN_LEDGER_PATH / HANSHIN_TOPIC_JA / vfl01 / ab01 をそのまま
#     importする(再改変・再コピーはしない)。
#   - er011_daily_news_focus_layer_comparison_trial_04(t4、既存Trial、
#     Fable受入済み・USER_DECISION_REQUIRED): analyze_run / classify_
#     role_text / body_embodies_role / load_role_planning_used / LEVELS
#     をそのまま再利用する(役割分類・body一致判定のロジックをTrial-04と
#     完全同一にし、比較可能性を担保する。本Trイアルで再実装・再コピーは
#     しない)。
#   - er011_daily_news_focus_layer_comparison_trial_02(t2、既存Trial、
#     A-UDR-8でVALIDATED): MAJOR_DAILY_GATE_CHECKLIST(Gate 6項目の事後
#     手動判定記録)をそのまま再利用する(Trend Synthesis側run_metadata
#     パターンと同型)。
#   - er003_v1_n3_01_articles_generate(prod_gen): build_common_block /
#     build_prompt / A2_KAI1_INSTRUCTION / B1_B_DIRECT_INSTRUCTION /
#     compute_metrics / split_common_sections_for_point_qa /
#     build_diagnostic_retry_prompt(G1修正済み、2026-09-09)。無変更。
#   - er005_cost_logger(cl): install / logging_context。無変更。
#
# Gate 4根拠: 本ファイルは新規コード追加のみで、上記いずれのモジュール・
# 関数も編集していない(grep差分なし、import only)。t3.run_one_pattern_
# connected()は自身のコピー本体内で`prod_gen.build_diagnostic_retry_
# prompt(...)`を直接呼び出しており(該当関数自体を別途コピーしていない)、
# G1修正はimport時点のprod_genモジュールから常に最新のものが使われる
# (下記gate4_g1_freshness_check()で機械確認、runtime実行前に必ず1回実施し
# 結果をJSONへ保存する)。
#
# 費用上限: ¥150(超過見込みならN=2へ縮小し報告。それでも超過ならSTOP)。
# 冒頭で必ずcl.install()を有効化する(過去2回の未設置事故の再発防止、
# Trial-04 run2/3の運用ミスを踏まえた明示的チェックリスト)。
# ============================================================
from __future__ import annotations

import difflib
import inspect
import json
import os
import time

import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er011_daily_news_focus_layer_comparison_trial_02 as t2
import er011_daily_news_focus_layer_comparison_trial_04 as t4
import er011_point_role_planning_focus_connection_trial_03 as t3

THEME_ID = "news_focus_hint_comparison_trial_06"
OUT_DIR = f"er011_output/{THEME_ID}"

N_RUNS = 3  # ユーザー指定。費用超過見込みの場合はmain()内でN=2へ縮退する。
BUDGET_JPY = 150.0

# 必須2条件(出力先ディレクトリ名は委任文の指定どおり baseline/focus_hint)。
CONDITIONS = {
    "baseline": {
        "editorial_type_module_block": "",  # Production既定(Focus Moduleなし)
        "point_role_hint_block": "",  # Production既定(hintなし)
    },
    "focus_hint": {
        "editorial_type_module_block": t3.MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK,
        "point_role_hint_block": t3.MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK,
    },
}

# 予算に余裕がある場合のみ追加する任意の切り分け条件(hint単独、Focus
# Module本文注入なし)。委任文§3「hint単独条件を追加できる余裕があれば」
# に基づく。既定では実行しない(main()内の予算判定で決める)。
BONUS_CONDITIONS = {
    "hint_only": {
        "editorial_type_module_block": "",
        "point_role_hint_block": t3.MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK,
    },
}

LEVELS = t4.LEVELS  # [(label, instruction, level_dir, stage_tag), ...] Trial-04と完全同一

# 参考データ(OPEN-134観測、正式Production run扱いではない): Trial-04
# baseline(G1修正前)の実測値。本Trialの同条件baselineと比較するためだけの
# 定数(既存er011_output/daily_news_focus_layer_comparison_trial_04/analysis
# 群から転記した集計値、書き換え不可)。
TRIAL04_BASELINE_REFERENCE_PRE_G1_FIX = {
    "note": "FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04(G1修正前に実行)の"
            "baseline(N=6、A2+B1B各3本)実測値。参考データのみ。OPEN-134の正式観測ログ"
            "(er011_output/point_overlap_observation_log.jsonl)へは本Trialの結果を"
            "追記していない(本Trialはrun_writer_for_theme経由の正式Production run"
            "ではなくtrial harness実行のため、Exit条件の20 runカウントを汚染しない"
            "ようにするため)。",
        "ng_rate": "66.7%(4/6)",
        "retry_avg": 1.67,
        "point_one_overlap_avg": 0.389,
        "point_two_overlap_avg": 0.339,
        "source": "FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04_REPORT.md §2",
}


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Gate 4: G1修正の鮮度確認(機械チェック)。t3.run_one_pattern_connectedが
# build_diagnostic_retry_prompt自体を別途コピーしておらず、常に現在import
# されているprod_genモジュールのものを直接呼んでいることを確認する
# (=G1修正がProductionへ適用済みである限り、本Trialのretryにも自動的に
# 反映されることの根拠)。加えてrun_one_pattern本体(406行)とrun_one_
# pattern_connected(コピー)のunified diffを取得し、差分行がTrial-03
# ヘッダーコメントに記載済みの4種類の変更(関数名/新規引数/呼び出し置換/
# prod_gen.修飾)に由来するものだけであることを目視確認できるよう記録する
# (完全自動の意味解析ではなく、diff行数・パターンの記録による支援的確認)。
# ============================================================
def gate4_g1_freshness_check() -> dict:
    trial_src = inspect.getsource(t3.run_one_pattern_connected)
    calls_prod_fn_directly = "prod_gen.build_diagnostic_retry_prompt(" in trial_src
    no_local_redefinition = "def build_diagnostic_retry_prompt" not in trial_src
    prod_diag_src = inspect.getsource(prod_gen.build_diagnostic_retry_prompt)
    g1_fix_marker_present = "OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01" in prod_diag_src

    prod_src = inspect.getsource(prod_gen.run_one_pattern)
    diff_lines = list(difflib.unified_diff(
        prod_src.splitlines(), trial_src.splitlines(),
        fromfile="prod_gen.run_one_pattern", tofile="t3.run_one_pattern_connected", lineterm=""))

    pass_text = ("PASS(G1修正はProduction側で有効、Trialは常にimport時点の最新実装を"
                 "呼ぶため自動的に反映される)")
    fail_text = "FAIL_NEEDS_REVIEW"
    conclusion = pass_text if (calls_prod_fn_directly and no_local_redefinition
                                and g1_fix_marker_present) else fail_text

    result = {
        "calls_prod_gen_build_diagnostic_retry_prompt_directly": calls_prod_fn_directly,
        "no_local_redefinition_of_build_diagnostic_retry_prompt_in_trial_copy": no_local_redefinition,
        "g1_fix_marker_present_in_currently_imported_production_source": g1_fix_marker_present,
        "run_one_pattern_vs_connected_diff_line_count": len(diff_lines),
        "conclusion": conclusion,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/gate4_g1_freshness_check.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/gate4_run_one_pattern_diff.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(diff_lines))
    print(f"[{THEME_ID}] gate4_g1_freshness_check: {result['conclusion']}")
    if conclusion != pass_text:
        raise RuntimeError(f"Gate 4 G1鮮度チェック失敗: {result}")
    return result


# ============================================================
# A3-UDR-2=(i): Gate 6項目の判定結果(Trend Synthesisと同じ機構)。
# t2.MAJOR_DAILY_GATE_CHECKLISTをそのまま再確認・記録する(新規判定は
# しない、既にTrial-02で手動判定済みの同一Hanshin Ledgerを再利用)。
# ============================================================
def build_run_metadata() -> dict:
    return {
        "management_id": "FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06",
        "mode_supply_path": "A3-UDR-2=(i) 手動Mode判定+手動Ledger供給(Trend Synthesisと同じ"
                            "機構、自動化は後段の課題)。",
        "major_daily_gate_checklist_source": "er011_daily_news_focus_layer_comparison_trial_02"
                                              ".MAJOR_DAILY_GATE_CHECKLIST(再確認、再判定なし)",
        "major_daily_gate_checklist": t2.MAJOR_DAILY_GATE_CHECKLIST,
        "editorial_mode_determination": "MAJOR_DAILY(t2の既存手動判定を再利用、本Trialで新規判定は行っていない)",
    }


# ============================================================
# 費用実測ヘルパー(Trial-04 cost_computeと同一の参照元・同一ロジックを
# このTrial専用ログパス向けに再実装。budget監視のためrun中に呼び出す)。
# ============================================================
USD_JPY = 160.0
PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter):
    return next(p["price"] for p in PRICING if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


_LUNA_IN, _LUNA_CACHED, _LUNA_OUT = _price("openai", "gpt-5.6-luna", "input_tokens"), \
    _price("openai", "gpt-5.6-luna", "cached_input_tokens"), _price("openai", "gpt-5.6-luna", "output_tokens")
_SOL_IN, _SOL_CACHED, _SOL_OUT = _price("openai", "gpt-5.6-sol", "input_tokens"), \
    _price("openai", "gpt-5.6-sol", "cached_input_tokens"), _price("openai", "gpt-5.6-sol", "output_tokens")
_WEB_SEARCH_CALL = _price("openai", "N/A (tool, all models)", "web_search_call")


def _call_cost_usd(r: dict) -> float:
    provider, model = r["provider"], r.get("model_id")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    if provider != "openai":
        raise ValueError(f"unpriced provider (text-only trial, no TTS/ASR expected): {provider}")
    billable_in = max(it - ct, 0)
    if model == "gpt-5.6-luna":
        cost = (billable_in / 1e6) * _LUNA_IN + (ct / 1e6) * _LUNA_CACHED + (ot / 1e6) * _LUNA_OUT
    elif model == "gpt-5.6-sol":
        cost = (billable_in / 1e6) * _SOL_IN + (ct / 1e6) * _SOL_CACHED + (ot / 1e6) * _SOL_OUT
    else:
        raise ValueError(f"unpriced openai model: {model}")
    web_search_calls = r.get("web_search_call_count") or 0
    cost += (web_search_calls / 1000) * _WEB_SEARCH_CALL
    return cost


def compute_cost_so_far_jpy() -> float:
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    if not os.path.exists(log_path):
        return 0.0
    total_usd = 0.0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_usd += _call_cost_usd(json.loads(line))
    return total_usd * USD_JPY


def write_cost_summary() -> dict:
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    records = [json.loads(l) for l in open(log_path, encoding="utf-8")] if os.path.exists(log_path) else []
    for r in records:
        r["_cost_usd"] = _call_cost_usd(r)
    from collections import defaultdict
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    by_condition, by_level, by_run = defaultdict(float), defaultdict(float), defaultdict(float)
    for theme, cost in by_theme.items():
        rest = theme[len(THEME_ID) + 1:]
        parts = rest.rsplit("_run", 1)
        if len(parts) == 2:
            cond_level, run_idx = parts
            cond_parts = cond_level.rsplit("_", 1)
            if len(cond_parts) == 2:
                condition, level = cond_parts
                by_run[f"run{run_idx}"] += cost
                by_condition[condition] += cost
                by_level[level] += cost
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-04 cost_computeと同一"
                       "参照元・同一ロジック)。text-onlyのためprovider=openaiのみを想定。",
        "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
        "by_run_jpy": {k: round(v * USD_JPY, 1) for k, v in by_run.items()},
        "by_condition_jpy": {k: round(v * USD_JPY, 1) for k, v in by_condition.items()},
        "by_level_jpy": {k: round(v * USD_JPY, 1) for k, v in by_level.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
        "total_calls": len(records),
    }
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def run_one_combo(client, master_full_text: str, verified_ledger_text: str,
                   condition_name: str, cond: dict, run_idx: int, label: str, instruction: str,
                   level_dir: str, stage_tag: str) -> dict:
    out_dir = f"{OUT_DIR}/{level_dir}/{condition_name}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, t3.HANSHIN_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=cond["editorial_type_module_block"])
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = t3.run_one_pattern_connected(
            client, theme_tag, label, prompt, verified_ledger_text, t3.HANSHIN_TOPIC_JA, out_dir,
            point_role_hint_block=cond["point_role_hint_block"])
    elapsed = round(time.time() - t0, 2)
    analysis = t4.analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = condition_name
    analysis["level"] = label
    analysis["run"] = run_idx
    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] run{run_idx} {condition_name} {label}: status={result.get('status')} "
          f"retry={analysis['retry_attempts']} p1_overlap={analysis['point_one_overlap_ratio']} "
          f"p2_overlap={analysis['point_two_overlap_ratio']} elapsed={elapsed}s")
    return analysis


def run_batch(run_idx: int, client, master_full_text: str, verified_ledger_text: str,
              condition_names: list) -> list:
    batch_results = []
    for condition_name in condition_names:
        cond = CONDITIONS.get(condition_name) or BONUS_CONDITIONS[condition_name]
        for label, instruction, level_dir, stage_tag in LEVELS:
            analysis = run_one_combo(
                client, master_full_text, verified_ledger_text, condition_name, cond, run_idx,
                label, instruction, level_dir, stage_tag)
            batch_results.append(analysis)
    return batch_results


# ============================================================
# CLI分割実行用ヘルパー(前面同期実行の1コマンドがタイムアウトを超えない
# よう、combo単位でプロセスを分けて逐次実行するため。cl.install()はappend
# モードのためプロセスをまたいでも既存raw_usage_log.jsonlへ追記される
# (er005_cost_logger.init_loggerはファイル存在時に上書きしない、下記
# setup_stage()実行時に既存ログを一度だけ確認)。
# ============================================================
def setup_stage() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")  # 冒頭で必ず有効化(未設置事故の再発防止)
    gate4_result = gate4_g1_freshness_check()
    unit_test_result = t3.test_default_hint_is_byte_identical_to_production()
    if unit_test_result["status"] != "PASS":
        raise RuntimeError(f"既定値バイト一致テスト失敗: {unit_test_result}")
    run_metadata = build_run_metadata()
    with open(f"{OUT_DIR}/run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] setup_stage完了: gate4={gate4_result['conclusion']}, "
          f"unit_test={unit_test_result['status']}")
    return {"gate4_result": gate4_result, "unit_test_result": unit_test_result, "run_metadata": run_metadata}


LABEL_LOOKUP = {label: (label, instruction, level_dir, stage_tag)
                for (label, instruction, level_dir, stage_tag) in LEVELS}
COMBO_RESULTS_DIR = f"{OUT_DIR}/_combo_results"


def combo_stage(condition_name: str, label: str, run_idx: int) -> dict:
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    client = t3.vfl01.get_client()
    master_full_text = t3.ab01.load_master_full_text()
    verified_ledger_text = t3.load_text(t3.HANSHIN_LEDGER_PATH)
    cond = CONDITIONS.get(condition_name) or BONUS_CONDITIONS[condition_name]
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP[label]
    analysis = run_one_combo(client, master_full_text, verified_ledger_text, condition_name, cond,
                              run_idx, label, instruction, level_dir, stage_tag)
    os.makedirs(COMBO_RESULTS_DIR, exist_ok=True)
    with open(f"{COMBO_RESULTS_DIR}/{condition_name}_{level_dir}_run{run_idx}.json", "w",
              encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    return analysis


def cost_stage() -> dict:
    result = write_cost_summary()
    print(f"[{THEME_ID}] 費用実測合計: ¥{result['total_jpy']}(N={N_RUNS}見込み計算はcombo実行ログ参照)")
    return result


def aggregate_stage() -> list:
    all_results = []
    if os.path.isdir(COMBO_RESULTS_DIR):
        for fname in sorted(os.listdir(COMBO_RESULTS_DIR)):
            with open(f"{COMBO_RESULTS_DIR}/{fname}", encoding="utf-8") as f:
                all_results.append(json.load(f))
    with open(f"{OUT_DIR}/all_results_so_far.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] aggregate_stage: {len(all_results)}本を集約しました。")
    return all_results


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")  # 冒頭で必ず有効化(未設置事故の再発防止)

    gate4_result = gate4_g1_freshness_check()

    # API呼び出し前の無料バイト一致再確認(Trial-03単体テストの再実行、費用ゼロ)。
    unit_test_result = t3.test_default_hint_is_byte_identical_to_production()
    if unit_test_result["status"] != "PASS":
        raise RuntimeError(f"既定値バイト一致テスト失敗: {unit_test_result}")

    run_metadata = build_run_metadata()
    with open(f"{OUT_DIR}/run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, ensure_ascii=False, indent=2)

    client = t3.vfl01.get_client()
    master_full_text = t3.ab01.load_master_full_text()
    verified_ledger_text = t3.load_text(t3.HANSHIN_LEDGER_PATH)

    all_results = []
    planned_n = N_RUNS
    stop_early = False
    for run_idx in range(1, N_RUNS + 1):
        if run_idx > planned_n:
            break
        batch = run_batch(run_idx, client, master_full_text, verified_ledger_text,
                           ["baseline", "focus_hint"])
        all_results.extend(batch)
        with open(f"{OUT_DIR}/all_results_so_far.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
        cost_so_far = compute_cost_so_far_jpy()
        avg_per_run_idx = cost_so_far / run_idx
        projected_full_n3 = avg_per_run_idx * N_RUNS
        print(f"[{THEME_ID}] === run{run_idx} 完了(累計{len(all_results)}本、"
              f"費用実測¥{cost_so_far:.1f}、N=3見込み¥{projected_full_n3:.1f}) ===")
        if run_idx < N_RUNS and projected_full_n3 > BUDGET_JPY:
            projected_n2 = avg_per_run_idx * 2
            if projected_n2 <= BUDGET_JPY and run_idx < 2:
                planned_n = 2
                print(f"[{THEME_ID}] 費用超過見込み(N=3で¥{projected_full_n3:.1f}> ¥{BUDGET_JPY})。"
                      f"N=2へ縮小します(N=2見込み¥{projected_n2:.1f})。")
            else:
                planned_n = run_idx
                stop_early = True
                print(f"[{THEME_ID}] 費用超過見込みがN=2でも解消しません。ここでSTOPします"
                      f"(完了済みrun_idx={run_idx}まで、STOP条件該当)。")
                break

    cost_summary = write_cost_summary()
    print(f"[{THEME_ID}] 費用実測合計: ¥{cost_summary['total_jpy']}")

    bonus_results = []
    remaining_budget = BUDGET_JPY - cost_summary["total_jpy"]
    per_combo_avg_jpy = cost_summary["total_jpy"] / max(len(all_results), 1)
    # bonus条件(hint_only)はA2/B1B各1本(計2本)。追加分の見込み費用が
    # 残予算に安全マージン(1.5倍)を掛けても収まる場合のみ実施する。
    if not stop_early and planned_n == N_RUNS and remaining_budget > per_combo_avg_jpy * 2 * 1.5:
        print(f"[{THEME_ID}] 残予算¥{remaining_budget:.1f}のためhint_only条件(A2/B1B各1本)を追加実施します。")
        bonus_results = run_batch(1, client, master_full_text, verified_ledger_text, ["hint_only"])
        with open(f"{OUT_DIR}/bonus_hint_only_results.json", "w", encoding="utf-8") as f:
            json.dump(bonus_results, f, ensure_ascii=False, indent=2, default=str)
        cost_summary = write_cost_summary()
        print(f"[{THEME_ID}] hint_only追加後 費用実測合計: ¥{cost_summary['total_jpy']}")
    else:
        print(f"[{THEME_ID}] hint_only bonus条件は実施しません"
              f"(stop_early={stop_early}, planned_n={planned_n}, 残予算¥{remaining_budget:.1f})。")

    with open(f"{OUT_DIR}/run_config.json", "w", encoding="utf-8") as f:
        json.dump({
            "planned_n": planned_n, "stop_early": stop_early, "n_runs_target": N_RUNS,
            "bonus_hint_only_executed": bool(bonus_results),
            "budget_jpy": BUDGET_JPY,
            "trial04_baseline_reference_pre_g1_fix": TRIAL04_BASELINE_REFERENCE_PRE_G1_FIX,
        }, f, ensure_ascii=False, indent=2)

    return {"all_results": all_results, "bonus_results": bonus_results, "cost_summary": cost_summary,
            "gate4_result": gate4_result, "planned_n": planned_n, "stop_early": stop_early}


if __name__ == "__main__":
    import sys

    # 実行環境の制約(前面同期実行、1コマンドあたりのタイムアウト)により、
    # main()(単一プロセスでN=3ループを最後まで実行する版、上記に定義済み・
    # 参考実装として保持)ではなく、combo単位でプロセスを分けて逐次実行する
    # CLIを実際の実行経路として使う。cl.install()はappendモードのため
    # プロセスをまたいでも既存raw_usage_log.jsonlへ正しく追記される。
    which = sys.argv[1] if len(sys.argv) > 1 else "setup"
    if which == "setup":
        setup_stage()
    elif which == "combo":
        # 例: python er011_news_focus_hint_comparison_trial_06.py combo focus_hint A2 1
        condition_name, label, run_idx = sys.argv[2], sys.argv[3], int(sys.argv[4])
        combo_stage(condition_name, label, run_idx)
    elif which == "cost":
        cost_stage()
    elif which == "aggregate":
        aggregate_stage()
    else:
        print("usage: python er011_news_focus_hint_comparison_trial_06.py "
              "[setup|combo <condition> <A2|B1B> <run_idx>|cost|aggregate]")
