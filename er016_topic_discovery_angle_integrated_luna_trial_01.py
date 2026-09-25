# ============================================================
# er016_topic_discovery_angle_integrated_luna_trial_01.py
# TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01 (Fable/ユーザー設計、2026-09-25)
# ============================================================
# 目的: er016_topic_discovery_angle_integrated_3way_trial_01.py と同じ
# 設計(Search + Angle Discovery + 追加検索 + Topic Package化 + Selection
# を1つのResponses API call(web_searchツール付き、内部の複数tool call
# は許容)で行う)を、Luna単独(gpt-5.6-luna)で実行し、方式そのものの
# 品質と実コストを測るTrial。3-way(Luna/Sol/Terra)はcost_estimate.json
# の時点で予算¥200超過見込みとなりSTOPしたため、ユーザー判断により
# Sol/Terraは今回実行せず保留する(中止ではない)。**Production実装
# ではない。** Production正式path(daily runner・er003_*/er012_*等)は
# 一切変更しない。
#
# 再利用方針(委任文指定): Prompt本文・json_schema・Teacher Dataの
# 差し込みは3WAY scriptと逐語同一にするため、3WAY scriptを直接import
# して build_prompt/build_schema/prompt_sha256/response_meta/MODELS["L"]
# などをそのまま再利用する。**3WAY script自体は一切変更しない。**
# 本scriptが新規に追加する要素は、(1)暴走防止ガードとしての
# max_tool_calls(既定30、Responses APIのトップレベルパラメータ。
# er003_output配下の既存raw_response.json群で"max_tool_calls": null
# というフィールドが既に存在することを確認済み=有効なパラメータ名)、
# (2)Luna単独用の出力ディレクトリ構成(out_dir直下フラット、
# arms/{arm}/のネストなし)、(3)ユーザー評価一覧の列構成
# (元ニュース/事実の核/一般人との接点/疑問/Angle/追加検索した事実、
# の10列。3WAYの簡易6列とは異なる)のみ。
#
# 費用上限¥100(Luna単独、暴走防止)。1 callは途中停止できないため、
# 実測が¥100を超えた場合は事実として報告する(追加callはしない)。
#
# --step: estimate / run / verify-window / assemble
# 冪等性: raw_response.json等が既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import random
import time
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

import er005_cost_logger as cl
import er016_topic_discovery_angle_integrated_3way_trial_01 as trial3way

load_dotenv()

THEME_TAG = "TOPIC_DISCOVERY_ANGLE_INTEGRATED_LUNA_TRIAL_01"
JST = timezone(timedelta(hours=9))

MODEL_LUNA = trial3way.MODELS["L"]  # "gpt-5.6-luna"(3WAY scriptの定義を再利用)
EFFORT = trial3way.EFFORT  # "medium"
SEARCH_CONTEXT_SIZE = trial3way.SEARCH_CONTEXT_SIZE  # "low"
USD_TO_JPY = trial3way.USD_TO_JPY
BUDGET_JPY = 100.0
MAX_TOOL_CALLS_DEFAULT = 30  # 暴走防止ガード(委任文指定)。設計変更ではない。

WINDOW_START_JST = trial3way.WINDOW_START_JST
WINDOW_END_JST = trial3way.WINDOW_END_JST
ASSUMED_INTERNAL_SEARCH_RANGE = trial3way.ASSUMED_INTERNAL_SEARCH_RANGE


# ------------------------------------------------------------
# ヘルパー(3WAY scriptと同一パターン)
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def skip_if_exists(path: str, force: bool) -> bool:
    if os.path.exists(path) and not force:
        print(f"[SKIP] 既存出力あり(--forceなし): {path}")
        return True
    return False


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def get_client():
    from openai import OpenAI
    return OpenAI()


# ------------------------------------------------------------
# step: estimate(Luna単独。3WAYのcmd_estimateと同じ線形回帰式を、
# Sol/Terra外挿なしでLunaのみに適用する)
# ------------------------------------------------------------
def cmd_estimate(args):
    out_dir = args.out_dir
    budget = args.budget_jpy
    developer, user, _ = trial3way.build_prompt()
    sha = trial3way.prompt_sha256(developer, user)
    prompt_chars = len(developer) + len(user)
    base_extra_chars = max(
        prompt_chars - trial3way.REF_PROCESS_BASELINE_PROMPT_CHARS, 0)
    base_extra_tokens = base_extra_chars / trial3way.CHARS_PER_TOKEN_CALIBRATED

    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]
    luna_in = trial3way._price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    base_extra_input_cost_luna_jpy = base_extra_tokens / 1_000_000 * luna_in * USD_TO_JPY

    scenarios = {}
    for label, n in ASSUMED_INTERNAL_SEARCH_RANGE.items():
        luna_from_ref_fit = (trial3way.REF_PROCESS_INTERCEPT_JPY
                              + trial3way.REF_PROCESS_MARGINAL_JPY_PER_SEARCH * n)
        luna_est = round(luna_from_ref_fit + base_extra_input_cost_luna_jpy, 2)
        scenarios[label] = {
            "assumed_internal_search_count": n,
            "luna_est_jpy": luna_est,
            "within_budget": luna_est <= budget,
        }

    all_within_budget = all(s["within_budget"] for s in scenarios.values())
    decision = "GO" if all_within_budget else "STOP"

    result = {
        "budget_jpy": budget,
        "prompt_sha256": sha,
        "prompt_chars_developer_plus_user": prompt_chars,
        "reference_process_baseline_prompt_chars": trial3way.REF_PROCESS_BASELINE_PROMPT_CHARS,
        "base_extra_chars_vs_baseline": base_extra_chars,
        "chars_per_token_calibrated": round(trial3way.CHARS_PER_TOKEN_CALIBRATED, 4),
        "ref_process_linear_fit": {
            "intercept_jpy": trial3way.REF_PROCESS_INTERCEPT_JPY,
            "marginal_jpy_per_search": trial3way.REF_PROCESS_MARGINAL_JPY_PER_SEARCH,
            "source": "3WAY trialのcost_estimate.jsonと同一の最小二乗fit"
                      "(er016_output/topic_selection_reference_process_trial_01/"
                      "cost.json由来)を再利用。本scriptでの再計算はしていない。",
        },
        "note": "Sol/Terra外挿は行わない(今回Luna単独Trialのため不要)。"
                "3WAY trialのcost_estimate.json(2026-09-25作成)における"
                "luna_est_jpy(low=39.57/mid=49.41/high=59.25)と同一の"
                "計算式で、本scriptが独立に再計算した値。",
        "scenarios": scenarios,
        "decision": decision,
        "decision_note": (
            f"internal search 20/25/30のいずれかのシナリオでluna_est_jpyが"
            f"budget_jpy={budget}を超過するため、Luna実行前にSTOPする。"
            if decision == "STOP" else
            "全シナリオでbudget内に収まる見込みのため、Luna実行に進む。"
        ),
        "computed_at_jst": datetime.now(JST).isoformat(),
    }
    save_json(out_path(out_dir, "cost_estimate.json"), result)
    print(f"[{'OK' if decision == 'GO' else 'STOP'}] estimate: decision={decision}")
    for label, s in scenarios.items():
        print(f"  {label}(n={s['assumed_internal_search_count']}): "
              f"Luna=JPY{s['luna_est_jpy']} within_budget={s['within_budget']}")

    if decision == "STOP":
        stop_reason = {
            "stopped": True,
            "stopped_at_step": "estimate",
            "reason": f"cost_estimate.jsonのdecision=STOP(budget_jpy={budget}超過見込み)。"
                      "Lunaは未実行(API課金は0円)。",
            "cost_estimate_summary": {
                label: s["luna_est_jpy"] for label, s in scenarios.items()
            },
            "budget_jpy": budget,
            "logged_at_jst": datetime.now(JST).isoformat(),
        }
        save_json(out_path(out_dir, "stop_condition.json"), stop_reason)
        print("[STOP] stop_condition.json を保存しました。API呼び出しは行いません。")


# ------------------------------------------------------------
# API呼び出し(3WAYのcall_modelと同一パターン + max_tool_callsガードを追加)
# ------------------------------------------------------------
def call_model(client, developer: str, user: str, schema: dict, model: str,
                stage: str, max_tool_calls: int, effort: str = EFFORT,
                context_size: str = SEARCH_CONTEXT_SIZE, retried: bool = False):
    kwargs = dict(
        model=model,
        reasoning={"effort": effort},
        input=[
            {"role": "developer", "content": developer},
            {"role": "user", "content": user},
        ],
        text={"format": {"type": "json_schema", **schema}},
        tools=[{"type": "web_search", "search_context_size": context_size}],
        max_tool_calls=max_tool_calls,
    )
    try:
        with cl.logging_context(THEME_TAG, stage):
            response = client.responses.create(**kwargs)
    except Exception as exc:
        if retried:
            raise
        print(f"[RETRY] {stage}: 技術的retry 1回目 ({exc})")
        time.sleep(2)
        return call_model(client, developer, user, schema, model, stage,
                           max_tool_calls, effort=effort, context_size=context_size,
                           retried=True)
    if response.model != model:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={model}, actual={response.model})"
        )
    return response


# ------------------------------------------------------------
# 実測費用集計(3WAYのcompute_actual_cost_jpyと同一ロジック、
# THEME_TAGのみ本script用に変更)
# ------------------------------------------------------------
def compute_actual_cost_jpy(out_dir: str) -> dict:
    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]

    def model_prices(model_name):
        return (
            trial3way._price(pricing, "openai", model_name, "input_tokens"),
            trial3way._price(pricing, "openai", model_name, "cached_input_tokens"),
            trial3way._price(pricing, "openai", model_name, "output_tokens"),
        )

    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    entries = [e for e in entries if e.get("theme") == THEME_TAG]

    by_model = {}
    total_jpy = 0.0
    for e in entries:
        if e.get("provider") != "openai" or not e.get("success", True):
            continue
        model_name = e.get("model_id") or MODEL_LUNA
        prices = model_prices(model_name)
        if any(p is None for p in prices):
            by_model.setdefault(model_name, {"calls": 0, "jpy": "UNKNOWN_PRICING"})
            by_model[model_name]["calls"] += 1
            continue
        p_in, p_cached, p_out = prices
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        billable_in = max(it - ct, 0)
        usd = (billable_in / 1_000_000) * p_in + (ct / 1_000_000) * p_cached \
            + (ot / 1_000_000) * p_out
        jpy = usd * USD_TO_JPY
        entry = by_model.setdefault(model_name, {"calls": 0, "jpy": 0.0})
        if entry["jpy"] == "UNKNOWN_PRICING":
            continue
        entry["calls"] += 1
        entry["jpy"] += jpy
        total_jpy += jpy

    return {"total_jpy_known_models_only": round(total_jpy, 2), "by_model": by_model}


# ------------------------------------------------------------
# step: run(Luna固定、out_dir直下フラット構成)
# ------------------------------------------------------------
def cmd_run(args):
    out_dir = args.out_dir
    raw_path = out_path(out_dir, "raw_response.json")
    if skip_if_exists(raw_path, args.force):
        return

    est_path = out_path(out_dir, "cost_estimate.json")
    if os.path.exists(est_path):
        est = load_json(est_path)
        if est.get("decision") == "STOP":
            raise SystemExit(
                "STOP: cost_estimate.jsonのdecision=STOPのため、runを実行しない"
                "(先にestimateをやり直すか、予算上限の見直しが必要)。"
            )

    install_logger(out_dir)
    cost_so_far = compute_actual_cost_jpy(out_dir)["total_jpy_known_models_only"]
    if cost_so_far >= args.budget_jpy:
        raise SystemExit(
            f"STOP: budget_guard: cost_so_far={cost_so_far} JPY >= "
            f"budget={args.budget_jpy} JPY(run実行前)"
        )

    client = get_client()
    developer, user, _ = trial3way.build_prompt()
    schema = trial3way.build_schema()
    sha = trial3way.prompt_sha256(developer, user)
    max_tool_calls = args.max_tool_calls
    save_json(out_path(out_dir, "prompt.json"), {
        "developer": developer, "user": user, "sha256": sha,
        "model_requested": MODEL_LUNA, "effort": EFFORT,
        "search_context_size": SEARCH_CONTEXT_SIZE,
        "max_tool_calls": max_tool_calls,
    })

    stage = "luna_run"
    t0 = time.time()
    response = call_model(client, developer, user, schema, MODEL_LUNA, stage,
                           max_tool_calls)
    elapsed_ms = round((time.time() - t0) * 1000, 1)

    retried_flag = False
    try:
        parsed = json.loads(response.output_text)
        empty_or_bad = (
            not parsed.get("topic_packages")
            or len(parsed.get("topic_packages", [])) == 0
        )
    except json.JSONDecodeError:
        parsed = None
        empty_or_bad = True

    if empty_or_bad:
        print(f"[RETRY] {stage}: 空出力/schema不一致のため同一条件で1回のみ再実行")
        retried_flag = True
        t0 = time.time()
        response = call_model(client, developer, user, schema, MODEL_LUNA,
                               stage + "_retry", max_tool_calls)
        elapsed_ms = round((time.time() - t0) * 1000, 1)
        parsed = json.loads(response.output_text)

    meta = trial3way.response_meta(response, developer, user)
    meta["elapsed_ms"] = elapsed_ms
    meta["max_tool_calls"] = max_tool_calls
    meta["schema_retry_occurred"] = retried_flag

    ws_calls = [item for item in response.output
                if getattr(item, "type", None) == "web_search_call"]
    search_log_lines = [f"# search_log (Luna / {MODEL_LUNA})", ""]
    for i, call in enumerate(ws_calls, 1):
        action = getattr(call, "action", None)
        q = None
        if action is not None:
            q = getattr(action, "query", None) or getattr(action, "queries", None)
        search_log_lines.append(f"{i}. {q}")
    save_json(raw_path, meta)
    save_json(out_path(out_dir, "topic_packages.json"), parsed)
    with open(out_path(out_dir, "search_log.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(search_log_lines) + "\n")
    save_json(out_path(out_dir, "api_meta.json"), {
        "model_requested": MODEL_LUNA,
        "response_model_actual": response.model,
        "usage": meta.get("usage"),
        "web_search_call_count": len(ws_calls),
        "elapsed_ms": elapsed_ms,
        "max_tool_calls": max_tool_calls,
        "schema_retry_occurred": retried_flag,
    })
    actual_cost = compute_actual_cost_jpy(out_dir)
    save_json(out_path(out_dir, "cost.json"), actual_cost)
    over_budget = actual_cost["total_jpy_known_models_only"] > args.budget_jpy
    print(f"[OK] run: model_actual={response.model} "
          f"packages={len(parsed.get('topic_packages', []))} "
          f"ws_calls={len(ws_calls)} elapsed_ms={elapsed_ms} "
          f"actual_jpy={actual_cost['total_jpy_known_models_only']} "
          f"over_budget={over_budget}")
    if over_budget:
        print(f"[NOTE] 実測費用が budget_jpy={args.budget_jpy} を超過しました"
              "(1 callは途中停止不可のため事実として報告。追加callは行いません)。")


# ------------------------------------------------------------
# step: verify-window(公開日時検証。既存repro01関数を3WAY module経由で
# 流用、選定には使わない)
# ------------------------------------------------------------
def cmd_verify_window(args):
    out_dir = args.out_dir
    pkg_path = out_path(out_dir, "topic_packages.json")
    if not os.path.exists(pkg_path):
        print(f"[SKIP] {pkg_path}なし(未実行)")
        save_json(out_path(out_dir, "window_compliance.json"), {})
        return
    packages = load_json(pkg_path)["topic_packages"]
    repro01 = trial3way.repro01
    result = []
    for pkg in packages:
        url = pkg.get("seed_url")
        entry = {"seed_title": pkg.get("seed_title"), "seed_url": url}
        resp, err = repro01._fetch(url) if url else (None, "no_url")
        if err is not None or resp is None:
            entry.update({"window_classification": "unreachable",
                           "http_status": None, "error": err})
        else:
            raw_time, method = repro01._extract_published_time(resp.text)
            if raw_time is None:
                entry.update({"window_classification": "unverifiable",
                               "http_status": resp.status_code})
            else:
                verified_iso, tz_assumed, cls = repro01._classify_window(
                    raw_time, WINDOW_START_JST, WINDOW_END_JST)
                entry.update({
                    "published_time_raw": raw_time,
                    "published_time_verified": verified_iso,
                    "extraction_method": method,
                    "window_classification": cls,
                    "http_status": resp.status_code,
                })
        result.append(entry)
    save_json(out_path(out_dir, "window_compliance.json"), {"L": result})
    print(f"[OK] verify-window: n={len(result)}")


# ------------------------------------------------------------
# step: assemble(ユーザー評価一覧・落選候補・lane比率・QCD)
# ------------------------------------------------------------
def cmd_assemble(args):
    out_dir = args.out_dir
    pkg_path = out_path(out_dir, "topic_packages.json")
    if not os.path.exists(pkg_path):
        print("[SKIP] assemble: topic_packages.jsonなし(未実行のためassembleから除外。"
              "STOPのため未実行と想定)。")
        save_json(out_path(out_dir, "assemble_skipped.json"), {
            "reason": "topic_packages.json not found (likely STOP at estimate step)",
            "checked_at_jst": datetime.now(JST).isoformat(),
        })
        return

    data = load_json(pkg_path)
    packages = data["topic_packages"]
    dropped = data.get("dropped_candidates", [])

    random.seed(42)  # 再現可能なランダム順(内部監査用)
    order = list(range(len(packages)))
    random.shuffle(order)

    eval_map = {}
    # er016_topic_discovery_eval_01.py(3WAY用の既存評価script、未変更)を
    # 単一arm(L)でもそのまま流用できるよう、同スクリプトが期待する
    # blind_map.json形式(arms/packages)も併せて保存する。
    blind_map_compat = {}
    rows = []
    for display_no, idx in enumerate(order, 1):
        pkg = packages[idx]
        eval_map[str(display_no)] = {"index": idx}
        blind_map_compat[str(display_no)] = {
            "arms": ["L"], "packages": [{"arm": "L", "index": idx}],
        }
        rows.append({
            "no": display_no,
            "tentative_title_ja": pkg.get("tentative_title_ja"),
            "seed_source_date_url": f"{pkg.get('seed_source_name')}"
                                     f"({pkg.get('seed_published_jst')}) "
                                     f"{pkg.get('seed_url')}",
            "core_fact_ja": pkg.get("core_fact_ja"),
            "everyday_connection_ja": pkg.get("everyday_connection_ja"),
            "natural_question_ja": pkg.get("natural_question_ja"),
            "angle_expansion_ja": pkg.get("angle_expansion_ja"),
            "extra_search_facts_ja": "; ".join(
                f"{x.get('fact_ja')}({x.get('url')})"
                for x in (pkg.get("extra_search_facts") or [])
            ) or "(なし)",
        })
    save_json(out_path(out_dir, "eval_map.json"), eval_map)
    save_json(out_path(out_dir, "blind_map.json"), blind_map_compat)

    md_lines = [
        "# USER_EVAL_TOPIC_DISCOVERY_LUNA",
        "",
        f"TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01。Luna単独実行の"
        f"Topic Package {len(packages)}件(Promptでは「exactly 10」を指示したが"
        f"schemaにminItems/maxItemsはなくPrompt指示のみのため、実際には"
        f"{len(packages)}件返ってきた。事実として記録)。self_note・内部判断は非表示。",
        "評価: ○(採用したい)/△(どちらとも)/×(採用しない)をコメントで記入してください。",
        "",
        "| # | 仮タイトル | 元ニュース(媒体・日付・URL) | 事実の核 | "
        "一般人との接点 | 疑問 | Angle(1〜2段) | 追加検索した事実(あれば) | "
        "評価(○/△/×) | コメント |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        md_lines.append(
            f"| {row['no']} | {row['tentative_title_ja']} | "
            f"{row['seed_source_date_url']} | {row['core_fact_ja']} | "
            f"{row['everyday_connection_ja']} | {row['natural_question_ja']} | "
            f"{row['angle_expansion_ja']} | {row['extra_search_facts_ja']} | | |"
        )
    with open("USER_EVAL_TOPIC_DISCOVERY_LUNA.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    # dropped_candidates.md
    dc_lines = ["# dropped_candidates", "",
                f"モデルが検討して落とした候補: {len(dropped)}件", ""]
    for d in dropped:
        dc_lines.append(f"- {d.get('seed_title')} ({d.get('seed_url')}): "
                         f"{d.get('reason_dropped_ja')}")
    with open(out_path(out_dir, "dropped_candidates.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(dc_lines) + "\n")

    # lane_ratio.md
    news_n = sum(1 for p in packages if p.get("seed_lane") == "news")
    social_n = sum(1 for p in packages if p.get("seed_lane") == "social")
    extra_n = sum(1 for p in packages if p.get("extra_search_facts"))
    lane_lines = ["# lane_ratio", "",
                  f"- news={news_n} social={social_n} "
                  f"extra_search_facts非空={extra_n}/{len(packages)}"]
    with open(out_path(out_dir, "lane_ratio.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lane_lines) + "\n")

    # qcd.md
    api_meta_path = out_path(out_dir, "api_meta.json")
    cost_path = out_path(out_dir, "cost.json")
    qcd_lines = ["# qcd", ""]
    if os.path.exists(api_meta_path):
        api_meta = load_json(api_meta_path)
        usage = api_meta.get("usage") or {}
        cost = load_json(cost_path) if os.path.exists(cost_path) else {}
        total_jpy = cost.get("total_jpy_known_models_only")
        n_pkg = len(packages)
        jpy_per_package = round(total_jpy / n_pkg, 3) if (
            isinstance(total_jpy, (int, float)) and n_pkg) else None
        qcd_lines += [
            f"- model_requested: {api_meta.get('model_requested')}",
            f"- response_model_actual: {api_meta.get('response_model_actual')}",
            f"- max_tool_calls (guard): {api_meta.get('max_tool_calls')}",
            f"- web_search_call_count: {api_meta.get('web_search_call_count')}",
            f"- input_tokens: {usage.get('input_tokens')}",
            f"- output_tokens: {usage.get('output_tokens')}",
            f"- reasoning_tokens: {usage.get('reasoning_tokens')}",
            f"- total_tokens: {usage.get('total_tokens')}",
            f"- elapsed_ms: {api_meta.get('elapsed_ms')}",
            f"- schema_retry_occurred: {api_meta.get('schema_retry_occurred')}",
            f"- total_jpy: {total_jpy}",
            f"- topic_packages_count: {n_pkg}",
            f"- jpy_per_topic_package: {jpy_per_package}",
        ]
    else:
        qcd_lines.append("- api_meta.jsonなし(未実行)")
    with open(out_path(out_dir, "qcd.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(qcd_lines) + "\n")

    print(f"[OK] assemble: packages={len(packages)} dropped={len(dropped)}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["estimate", "run", "verify-window", "assemble"])
    parser.add_argument("--budget-jpy", type=float, default=BUDGET_JPY)
    parser.add_argument("--max-tool-calls", type=int, default=MAX_TOOL_CALLS_DEFAULT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.step == "estimate":
        cmd_estimate(args)
    elif args.step == "run":
        cmd_run(args)
    elif args.step == "verify-window":
        cmd_verify_window(args)
    elif args.step == "assemble":
        cmd_assemble(args)


if __name__ == "__main__":
    main()
