# ============================================================
# er016_news_hook_model_comparison_01.py
# NEWS-HOOK-MODEL-COMPARISON-01 (Fable/ユーザー設計、2026-09-24)
# ============================================================
# 目的: Hook生成(2段: 面白い見方→短いHook)のModel差を、Luna/Terra/Solの
# 完全同一Prompt・同一schema・同一reasoning effort(medium)条件で比較する
# Trial。**Production実装ではない。** Production正式path(daily runner・
# er006_model_routing_contract_01・er011_*/er014_*等)は一切変更しない。
#
# 禁止事項(委任文より):
#  - REFERENCE_20の hook_ja / type_tags、ユーザー評価点、他モデルの生成
#    Hook、過去Hook Trial(CONT-02 hook_test_h3*)の回答例をPromptへ入れない。
#    各モデルの入力は reference_id と topic_ja のみ。
#  - 3モデルは互いに独立call(previous_response_id共有なし)。
#  - 3モデルで完全同一Prompt・同一schema・同一effort(medium)。
#  - 費用上限¥100。API callは各モデルStage1+Stage2の計6 callのみ
#    (JSON parse失敗時のみ1回retry)。
#
# 再利用: er016_topic_selection_chatgpt_repro_01.py (base)、
# er016_topic_selection_chatgpt_repro_01_cont02.py (cont02) をimportし、
# ヘルパー関数・スキーマ・REFERENCE_20/REFERENCE_MATERIALS_ONLY・
# call_model・response_metaを再利用する。両ファイル自体は変更しない。
#
# Stage1のdeveloper1・user1、Stage2(h3分岐)のdeveloper2・user2は、
# cont02.py の cmd_hook_test(which="h3") 内のPromptと逐語一致させている
# (複製元: er016_topic_selection_chatgpt_repro_01_cont02.py
#  行968-977[stage1]、行1000, 1016-1030[stage2 h3分岐])。
#
# モード: (引数なし)generate / --assemble-only / --contamination-check
# 冪等性: hooks_{model}_stage1.json / hooks_{model}.json が既に存在する
# 場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
from datetime import datetime

import er016_topic_selection_chatgpt_repro_01 as base
import er016_topic_selection_chatgpt_repro_01_cont02 as cont02

THEME_TAG = "NEWS_HOOK_MODEL_COMPARISON_01"
MODELS = {"luna": "gpt-5.6-luna", "terra": "gpt-5.6-terra", "sol": "gpt-5.6-sol"}
EFFORT = "medium"
COST_CEILING_JPY = 100

out_path = base.out_path
save_json = base.save_json
load_json = base.load_json
skip_if_exists = base.skip_if_exists

# Reference素材(id/topic_jaのみ。hook_ja/type_tagsは一切使わない)。
# cont02.REFERENCE_MATERIALS_ONLYと同一構築(= [{"reference_id": r["id"],
# "topic_ja": r["topic_ja"]} for r in base.REFERENCE_20])。
MATERIALS = cont02.REFERENCE_MATERIALS_ONLY


# ------------------------------------------------------------
# Prompt builders (cont02 h3分岐と逐語一致)
# ------------------------------------------------------------
def build_stage1_prompt():
    developer1 = "あなたはNews分析担当です。"
    user1 = f"""以下20件は、Newsの素材概要(見出し相当)だけです。各素材に
ついて、このニュースの最も面白い見方(人間にとって意外・身近・逆説的・
気になる点)を1文で書いてください。まだHookは作らないでください。

【素材一覧】
{json.dumps(MATERIALS, ensure_ascii=False, indent=2)}

各reference_idについてinteresting_angle_ja(1文)を返してください。全
reference_idについて出力してください。"""
    return developer1, user1


def build_stage2_prompt(stage1_results: list):
    angle_by_id = {r["reference_id"]: r["interesting_angle_ja"] for r in stage1_results}
    topic_by_id = {m["reference_id"]: m["topic_ja"] for m in MATERIALS}
    stage2_input = [
        {"reference_id": rid, "topic_ja": topic_by_id[rid], "interesting_angle_ja": angle_by_id[rid]}
        for rid in sorted(angle_by_id)
    ]
    developer2 = "あなたはHook Writerです。"
    user2 = f"""以下は各Newsの素材概要と、Stage 1で見つけた「最も面白い見方」
です。それぞれの見方を、友人に話しかけるような短い一文の問いにして
ください。目安は30字前後。「〜でしょうか」は使わず、「〜？」で終える
形にしてください。

{json.dumps(stage2_input, ensure_ascii=False, indent=2)}

【絶対条件】
(1) 釣りタイトル・誇張を禁止する。
(2) 素材概要では答えられない疑問を作らない。
(3) Fact以上の断定をしない。

各reference_idについてhook_ja・hook_en・answer_in_source(素材概要の
内容で実質的に答えられる部分の要約。答えられない場合は"NOT_IN_SOURCE")
を返してください。全reference_idについて出力してください。"""
    return developer2, user2, stage2_input


# ------------------------------------------------------------
# API call + JSON parse retry(1回まで)
# ------------------------------------------------------------
def call_and_parse(client, developer, user, schema, stage, model_id, out_dir, retried=False):
    response = base.call_model(client, developer, user, schema=schema, web_search=False,
                                stage=stage, model=model_id, effort=EFFORT, out_dir=out_dir)
    try:
        parsed = json.loads(response.output_text)
    except json.JSONDecodeError as exc:
        if retried:
            raise
        print(f"[RETRY] {stage}: JSON parse失敗のため1回retry ({exc})")
        return call_and_parse(client, developer, user, schema, stage, model_id, out_dir, retried=True)
    return response, parsed


def record_error(out_dir, key, stage, exc):
    path = out_path(out_dir, "errors", f"{key}_{stage}.json")
    save_json(path, {
        "model_key": key, "model_id": MODELS[key], "stage": stage,
        "error_type": type(exc).__name__, "error_message": str(exc),
        "logged_at_jst": datetime.now(base.JST).isoformat(),
    })
    print(f"[ERROR] {key}/{stage}: {type(exc).__name__}: {exc}")


def record_stop(out_dir, key, stage, message):
    path = out_path(out_dir, "stop_condition.json")
    save_json(path, {
        "stopped": True, "model_key": key, "model_id": MODELS[key], "stage": stage,
        "reason": message, "logged_at_jst": datetime.now(base.JST).isoformat(),
    })
    print(f"[STOP] {key}/{stage}: {message}")


# ------------------------------------------------------------
# generate: 各モデルについてStage1→Stage2(独立call)
# ------------------------------------------------------------
def cmd_generate(args):
    out_dir = args.out_dir
    model_keys = args.models.split(",")
    for key in model_keys:
        if key not in MODELS:
            raise ValueError(f"未知のmodel key: {key} (許可: {list(MODELS)})")
    base.install_logger(out_dir)
    client = base.get_client()

    stop_triggered = False

    for key in model_keys:
        if stop_triggered:
            print(f"[SKIP] {key}: 直前のSTOPのため未実行")
            continue
        model_id = MODELS[key]

        # --- Stage 1 ---
        stage1_path = out_path(out_dir, f"hooks_{key}_stage1.json")
        if skip_if_exists(stage1_path, args.force):
            stage1_results = load_json(stage1_path)["results"]
        else:
            developer1, user1 = build_stage1_prompt()
            save_json(out_path(out_dir, "prompts", f"{key}_stage1.json"),
                      {"developer": developer1, "user": user1, "model_requested": model_id,
                       "effort": EFFORT})
            stage_name = f"{key}_stage1"
            try:
                response1, parsed1 = call_and_parse(client, developer1, user1,
                                                      cont02.H2_STAGE1_SCHEMA, stage_name,
                                                      model_id, out_dir)
            except RuntimeError as exc:
                if "STOP条件該当" in str(exc):
                    record_stop(out_dir, key, "stage1", str(exc))
                    stop_triggered = True
                    continue
                record_error(out_dir, key, "stage1", exc)
                continue
            except Exception as exc:
                record_error(out_dir, key, "stage1", exc)
                continue
            meta1 = base.response_meta(response1, user1, developer1)
            stage1_results = parsed1["results"]
            save_json(stage1_path, {"results": stage1_results})
            save_json(out_path(out_dir, "raw_responses", f"{key}_stage1.json"), meta1)
            print(f"[OK] {key}-stage1: results={len(stage1_results)} "
                  f"model_actual={meta1['response_model_actual']}")

        # --- Stage 2 ---
        stage2_path = out_path(out_dir, f"hooks_{key}.json")
        if skip_if_exists(stage2_path, args.force):
            continue
        developer2, user2, stage2_input = build_stage2_prompt(stage1_results)
        save_json(out_path(out_dir, "prompts", f"{key}_stage2.json"),
                  {"developer": developer2, "user": user2, "model_requested": model_id,
                   "effort": EFFORT})
        stage_name = f"{key}_stage2"
        try:
            response2, parsed2 = call_and_parse(client, developer2, user2,
                                                  cont02.H2_STAGE2_SCHEMA, stage_name,
                                                  model_id, out_dir)
        except RuntimeError as exc:
            if "STOP条件該当" in str(exc):
                record_stop(out_dir, key, "stage2", str(exc))
                stop_triggered = True
                continue
            record_error(out_dir, key, "stage2", exc)
            continue
        except Exception as exc:
            record_error(out_dir, key, "stage2", exc)
            continue
        meta2 = base.response_meta(response2, user2, developer2)
        save_json(stage2_path, {"results": parsed2["results"], "stage1_input_used": stage2_input})
        save_json(out_path(out_dir, "raw_responses", f"{key}_stage2.json"), meta2)
        print(f"[OK] {key}-stage2: results={len(parsed2['results'])} "
              f"model_actual={meta2['response_model_actual']}")

    print("[DONE] generate phase 終了"
          f"{'(STOPあり)' if stop_triggered else ''}")


# ------------------------------------------------------------
# assemble-only: comparison_table.md / mechanical_stats.json / cost.json /
# run_meta.json
# ------------------------------------------------------------
def _load_hooks(out_dir, key):
    path = out_path(out_dir, f"hooks_{key}.json")
    if not os.path.exists(path):
        return None
    return {r["reference_id"]: r for r in load_json(path)["results"]}


def _mechanical_stats_for_model(hooks_by_id):
    if not hooks_by_id:
        return None
    lengths = [len(r["hook_ja"]) for r in hooks_by_id.values()]
    q_end = sum(1 for r in hooks_by_id.values() if r["hook_ja"].strip().endswith("？"))
    deshou = sum(1 for r in hooks_by_id.values() if "でしょうか" in r["hook_ja"])
    not_in_source = sorted(
        rid for rid, r in hooks_by_id.items() if r.get("answer_in_source") == "NOT_IN_SOURCE"
    )
    return {
        "n": len(hooks_by_id),
        "hook_ja_len_avg": round(statistics.mean(lengths), 2),
        "hook_ja_len_max": max(lengths),
        "hook_ja_len_min": min(lengths),
        "ends_with_question_mark_count": q_end,
        "contains_deshouka_count": deshou,
        "not_in_source_count": len(not_in_source),
        "not_in_source_reference_ids": not_in_source,
    }


def cmd_assemble(args):
    out_dir = args.out_dir
    model_keys = args.models.split(",")

    hooks_by_model = {key: _load_hooks(out_dir, key) for key in model_keys}

    # --- comparison_table.md ---
    topic_by_id = {m["reference_id"]: m["topic_ja"] for m in MATERIALS}
    ref_hook_by_id = {r["id"]: r["hook_ja"] for r in base.REFERENCE_20}
    lines = [
        "# comparison_table (NEWS-HOOK-MODEL-COMPARISON-01)",
        "",
        "| # | 素材(topic_ja) | Original Reference Hook(hook_ja) | Luna | Terra | Sol |",
        "|---|---|---|---|---|---|",
    ]
    for rid in sorted(topic_by_id):
        row = [str(rid), topic_by_id[rid], ref_hook_by_id.get(rid, "")]
        for key in ("luna", "terra", "sol"):
            hm = hooks_by_model.get(key)
            if hm and rid in hm:
                row.append(hm[rid]["hook_ja"])
            elif key in model_keys:
                row.append("N/A(生成失敗/未生成)")
            else:
                row.append("N/A(対象外)")
        lines.append("| " + " | ".join(c.replace("|", "\\|") for c in row) + " |")

    stats = {key: _mechanical_stats_for_model(hooks_by_model.get(key)) for key in ("luna", "terra", "sol")}
    lines.append("")
    lines.append("## 機械統計(観察事実のみ)")
    lines.append("")
    lines.append("| model | n | hook_ja文字数 平均 | 最大 | 最小 | 「？」終端件数 | 「でしょうか」含有件数 | NOT_IN_SOURCE件数 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for key in ("luna", "terra", "sol"):
        s = stats.get(key)
        if s is None:
            lines.append(f"| {key} | - | - | - | - | - | - | - |")
        else:
            lines.append(f"| {key} | {s['n']} | {s['hook_ja_len_avg']} | {s['hook_ja_len_max']} | "
                          f"{s['hook_ja_len_min']} | {s['ends_with_question_mark_count']} | "
                          f"{s['contains_deshouka_count']} | {s['not_in_source_count']} |")

    with open(out_path(out_dir, "comparison_table.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    save_json(out_path(out_dir, "mechanical_stats.json"), stats)
    print(f"[OK] comparison_table.md / mechanical_stats.json 生成 (out_dir={out_dir})")

    # --- cost.json ---
    _cmd_cost(out_dir, model_keys)

    # --- run_meta.json (追記更新) ---
    meta_path = out_path(out_dir, "run_meta.json")
    meta = load_json(meta_path) if os.path.exists(meta_path) else {}
    meta.update({
        "assembled_at_jst": datetime.now(base.JST).isoformat(),
        "models_requested": model_keys,
        "model_ids": {k: MODELS[k] for k in model_keys},
        "effort": EFFORT,
    })
    save_json(meta_path, meta)


def _resolve_terra_price(pricing):
    """gpt-5.6-terraの単価をpricing_snapshot.jsonから探す。無ければUNKNOWN。"""
    for p in pricing:
        if p.get("provider") == "openai" and p.get("model") == "gpt-5.6-terra":
            return True
    return False


# 事前指定Grep手順1のフォールバック(2026-09-24実行): curl -sL
# https://platform.openai.com/docs/pricing でHTMLを1回取得したところ、
# "gpt-5.6-terra" 文字列自体は複数箇所(4パターンの数値セット)に存在した。
# ただし、同ページ内の"gpt-5.6-sol"/"gpt-5.6-luna"の数値(4候補セットの
# いずれも)が、既存er005_output/cost_baseline_01/pricing_snapshot.json
# (checked_date 2026-08-17、OFFICIAL_SOURCE、gpt-5.6-sol input/cached/
# output=5.00/0.50/30.00、gpt-5.6-luna=0.20/0.02/1.20 USD/1M tokens)と
# 一致しなかった(各候補: sol=[4,0.4,5,20]/[2,0.2,2.5,10]/[8,0.8,10,40]、
# 3列目の意味も不明[4列あり、既存snapshotは3列])。どの候補がStandard
# tier・per-1M-token換算の正しい表かを機械的に確定できなかったため、
# 単価を確定値として採用せず(捏造回避)、参考情報としてのみ記録する。
TERRA_PRICE_PROBE_EVIDENCE = {
    "attempted": True,
    "fetch_url": "https://platform.openai.com/docs/pricing",
    "fetched_at_jst_note": "2026-09-24 (本タスク実行時、curl -sLで1回取得)",
    "resolution_status": "AMBIGUOUS_NOT_ADOPTED",
    "reason": "ページ内に'gpt-5.6-terra'を含む数値セットが複数(4パターン)存在し、"
              "同時に含まれるgpt-5.6-sol/gpt-5.6-lunaの数値がどの候補も既存"
              "pricing_snapshot.json(OFFICIAL_SOURCE)の値と一致しなかった"
              "(tier/列構成が不明)。誤った単価を確定値として記録するリスクを"
              "避けるため、terra_price_status=UNKNOWNのまま採用しない。",
    "raw_candidate_number_sets_usd_per_1M_tokens": {
        "note": "各セット=[terra_input, terra_cached_input, terra_col3_unknown, terra_output]"
                "(該当行の同時掲載sol/luna数値も既存snapshotと不一致だったため出典比較不能)",
        "candidate_1": [2, 0.2, 2.5, 12],
        "candidate_2": [1, 0.1, 1.25, 6],
        "candidate_3": [1, 0.1, 1.25, 6],
        "candidate_4": [4, 0.4, 5, 24],
    },
}


def _cmd_cost(out_dir, model_keys):
    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]
    usd_to_jpy = 160

    def model_prices(model_name):
        return (
            base._price(pricing, "openai", model_name, "input_tokens"),
            base._price(pricing, "openai", model_name, "cached_input_tokens"),
            base._price(pricing, "openai", model_name, "output_tokens"),
        )

    terra_price_known = _resolve_terra_price(pricing)

    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    # 注記(重要): base.call_model()は内部でcl.logging_context(THEME_TAG, stage)を
    # 呼ぶが、そのTHEME_TAGはbaseモジュール自身のグローバル定数
    # "TOPIC_SELECTION_CHATGPT_REPRO_01"であり、本スクリプト独自のTHEME_TAGでは
    # ない(baseファイルは無変更のため変更不可)。そのためtheme値ではなく、
    # 本スクリプトが発行したstage名(例: "luna_stage1")で該当callを絞り込む。
    expected_stages = {f"{key}_stage{n}" for key in model_keys for n in (1, 2)}
    entries = [e for e in entries if e.get("theme") == base.THEME_TAG
               and e.get("stage") in expected_stages]

    by_model_key = {}
    key_by_model_id = {v: k for k, v in MODELS.items()}
    for e in entries:
        if e.get("provider") != "openai" or not e.get("success", True):
            continue
        model_id = e.get("model_id")
        key = key_by_model_id.get(model_id)
        if key is None or key not in model_keys:
            continue
        # 注記: er005_cost_logger.record()は usage dict を **usage で
        # トップレベルへ展開して書き込む(nested "usage" キーは存在しない)。
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        rt = e.get("reasoning_tokens") or 0
        latency = e.get("elapsed_seconds") or 0.0
        stage = e.get("stage") or "unknown"
        s = by_model_key.setdefault(key, {
            "model_id_requested": MODELS[key], "actual_model_ids": set(),
            "calls": 0, "input_tokens": 0, "cached_input_tokens": 0,
            "output_tokens": 0, "reasoning_tokens": 0,
            "latency_seconds_by_stage": {}, "latency_seconds_total": 0.0,
        })
        s["actual_model_ids"].add(model_id)
        s["calls"] += 1
        s["input_tokens"] += it
        s["cached_input_tokens"] += ct
        s["output_tokens"] += ot
        s["reasoning_tokens"] += rt
        s["latency_seconds_by_stage"][stage] = s["latency_seconds_by_stage"].get(stage, 0.0) + latency
        s["latency_seconds_total"] += latency

    result = {"usd_to_jpy": usd_to_jpy, "cost_ceiling_jpy": COST_CEILING_JPY, "by_model": {}}
    total_jpy_all = 0.0
    for key in model_keys:
        s = by_model_key.get(key)
        model_id = MODELS[key]
        if s is None:
            result["by_model"][key] = {
                "model_id_requested": model_id, "actual_model_ids": [],
                "calls": 0, "note": "raw_usage_log.jsonlに該当call無し(生成未実行/失敗)。",
            }
            continue
        entry = {
            "model_id_requested": model_id,
            "actual_model_ids": sorted(s["actual_model_ids"]),
            "calls": s["calls"],
            "input_tokens": s["input_tokens"],
            "cached_input_tokens": s["cached_input_tokens"],
            "output_tokens": s["output_tokens"],
            "reasoning_tokens": s["reasoning_tokens"],
            "latency_seconds_by_stage": s["latency_seconds_by_stage"],
            "latency_seconds_total": round(s["latency_seconds_total"], 3),
        }
        price_known = True
        if key == "terra" and not terra_price_known:
            price_known = False
        if price_known:
            try:
                p_in, p_cached, p_out = model_prices(model_id)
                billable_in = max(s["input_tokens"] - s["cached_input_tokens"], 0)
                usd = (billable_in / 1_000_000) * p_in + (s["cached_input_tokens"] / 1_000_000) * p_cached \
                    + (s["output_tokens"] / 1_000_000) * p_out
                jpy = round(usd * usd_to_jpy, 2)
                per_hook_jpy = round(jpy / 20, 3) if s["calls"] else None
                entry.update({
                    "price_status": "KNOWN",
                    "price_source": "er005_output/cost_baseline_01/pricing_snapshot.json",
                    "total_usd": round(usd, 5),
                    "total_jpy": jpy,
                    "per_hook_jpy": per_hook_jpy,
                    "monthly_estimate_jpy_20_hooks_x_30days": round(per_hook_jpy * 20 * 30, 1)
                        if per_hook_jpy is not None else None,
                })
                total_jpy_all += jpy
            except StopIteration:
                entry.update({"price_status": "UNKNOWN",
                               "price_note": "pricing_snapshot.jsonに単価行が無い(予期せぬ欠落)。"})
        else:
            entry.update({
                "price_status": "UNKNOWN",
                "price_note": "gpt-5.6-terraの単価がpricing_snapshot.jsonに無い。"
                               "token数のみ記録(単価を捏造しない)。",
                "price_probe_evidence": TERRA_PRICE_PROBE_EVIDENCE if key == "terra" else None,
            })
        result["by_model"][key] = entry

    result["total_jpy_known_models_only"] = round(total_jpy_all, 2)
    result["within_cost_ceiling_known_models_only"] = total_jpy_all <= COST_CEILING_JPY
    save_json(out_path(out_dir, "cost.json"), result)
    print(f"[OK] cost.json: total_jpy(known models only)={round(total_jpy_all, 2)} "
          f"ceiling={COST_CEILING_JPY}")


# ------------------------------------------------------------
# contamination-check: Reference Hook等の非混入検査 + actual model一致検査
# ------------------------------------------------------------
def cmd_contamination_check(args):
    out_dir = args.out_dir
    model_keys = args.models.split(",")

    forbidden_strings = []
    for r in base.REFERENCE_20:
        forbidden_strings.append(("reference_hook_ja", r["id"], r["hook_ja"]))
        forbidden_strings.append(("reference_type_tags", r["id"], r["type_tags"]))

    # ユーザー評価点表の行(docs/pm/topic_selection_user_eval_dataset.json、
    # 存在すればそこから読む。Step2実行前でも委任文原文のDataset A/B/Rの
    # hook_ja文字列は下でCONT-02の既存出力と合わせて別途検査する)
    eval_dataset_path = os.path.join("docs", "pm", "topic_selection_user_eval_dataset.json")
    if os.path.exists(eval_dataset_path):
        eval_data = load_json(eval_dataset_path)
        for ds_key in ("dataset_r", "dataset_a", "dataset_b"):
            for item in eval_data.get(ds_key, []):
                forbidden_strings.append((f"{ds_key}_hook_ja", item.get("item_no"), item.get("hook_ja", "")))

    # CONT-02 hook_test_h3 / hook_test_h3_sol の既存回答例
    cont02_dir = os.path.join("er016_output", "topic_selection_chatgpt_repro_01_cont02")
    for fname in ("hook_test_h3.json", "hook_test_h3_sol.json"):
        fpath = os.path.join(cont02_dir, fname)
        if os.path.exists(fpath):
            data = load_json(fpath)
            for r in data.get("results", []):
                forbidden_strings.append((f"cont02_{fname}", r.get("reference_id"), r.get("hook_ja", "")))

    forbidden_strings = [(src, rid, text) for src, rid, text in forbidden_strings if text]

    prompts_dir = out_path(out_dir, "prompts")
    checked_files = []
    detections = []
    if os.path.isdir(prompts_dir):
        for fname in sorted(os.listdir(prompts_dir)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(prompts_dir, fname)
            checked_files.append(fpath)
            content = json.dumps(load_json(fpath), ensure_ascii=False)
            for src, rid, text in forbidden_strings:
                if text and text in content:
                    detections.append({"file": fpath, "source": src, "reference_id": rid, "text": text})

    # actual model一致検査(前方一致可)
    model_id_checks = []
    all_match = True
    for key in model_keys:
        model_id = MODELS[key]
        for stage in ("stage1", "stage2"):
            raw_path = out_path(out_dir, "raw_responses", f"{key}_{stage}.json")
            if not os.path.exists(raw_path):
                continue
            meta = load_json(raw_path)
            actual = meta.get("response_model_actual")
            matched = bool(actual) and actual.startswith(model_id)
            if not matched:
                all_match = False
            model_id_checks.append({
                "model_key": key, "stage": stage, "requested": model_id,
                "actual": actual, "matched": matched,
            })

    result = {
        "checked_at_jst": datetime.now(base.JST).isoformat(),
        "forbidden_strings_checked_count": len(forbidden_strings),
        "prompts_files_checked": checked_files,
        "detections_count": len(detections),
        "detections": detections,
        "contamination_free": len(detections) == 0,
        "model_id_checks": model_id_checks,
        "model_id_all_match": all_match,
    }
    save_json(out_path(out_dir, "contamination_check.json"), result)
    print(f"[OK] contamination_check.json: forbidden_strings={len(forbidden_strings)} "
          f"files_checked={len(checked_files)} detections={len(detections)} "
          f"model_id_all_match={all_match}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def _script_sha() -> str:
    try:
        out = subprocess.run(["git", "hash-object", __file__], capture_output=True,
                              text=True, check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        return out.stdout.strip()
    except Exception:
        with open(__file__, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--models", default="luna,terra,sol")
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--assemble-only", action="store_true")
    parser.add_argument("--contamination-check", action="store_true")
    args = parser.parse_args()

    if args.effort != EFFORT:
        raise ValueError(f"effortは{EFFORT}固定(委任文条件)。--effort={args.effort}は不許可。")

    os.makedirs(args.out_dir, exist_ok=True)
    meta_path = out_path(args.out_dir, "run_meta.json")
    if not os.path.exists(meta_path):
        save_json(meta_path, {
            "created_at_jst": datetime.now(base.JST).isoformat(),
            "script_sha256_or_git_hash": _script_sha(),
            "theme_tag": THEME_TAG,
        })

    if args.contamination_check:
        cmd_contamination_check(args)
    elif args.assemble_only:
        cmd_assemble(args)
    else:
        cmd_generate(args)


if __name__ == "__main__":
    main()
