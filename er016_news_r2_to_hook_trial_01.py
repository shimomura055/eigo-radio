# ============================================================
# er016_news_r2_to_hook_trial_01.py
# NEWS-R2-TO-HOOK-TRIAL-01 (Fable/ユーザー設計、2026-09-24)
# ============================================================
# 目的: 「Hookを記事作成前ではなく、2回目revision完成記事(Trial呼称R2)の
# 後に作れば、Reference級Hookへ近づくのではないか」という仮説を検証する
# Trial。**Production実装ではない。** Production正式path(daily runner・
# er006_model_routing_contract_01・er011_*/er014_*・Topic Search・Writer・
# retry/fallback・CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS・Production prompt)
# は一切変更しない。既存 er015_*/er016_* scriptも変更しない(importのみ)。
#
# 禁止事項(委任文より):
#  - 新しく記事本文を生成しない。既存R2全文(sha256一致を確認済み)を
#    そのまま入力に使う。
#  - 生成Promptへ以下を一切入れない: Reference Hook(REFERENCE_20の
#    hook_ja)、過去のLuna/Terra/Sol Hook(news_hook_model_comparison_01の
#    hooks_*.json、topic_selection_chatgpt_repro_01_cont02のhook_test_*.json)、
#    ユーザー評価点(topic_selection_user_eval_dataset.json)、Fable評価、
#    他モデルの出力。
#  - 3モデルで完全同一Prompt・同一schema・同一effort(medium)。各callは
#    独立(previous_response_id不使用)。Prompt本文はFable固定の逐語を使用
#    し、追加条件(比喩を複数/逆転を必ず/驚き2回 等)を入れない。
#  - API callは3記事×3モデル=9 callのみ(JSON parse失敗時のretryは各1回
#    まで)。費用上限¥30。
#
# 再利用: er016_topic_selection_chatgpt_repro_01.py (base) をimportし、
# call_model / response_meta / out_path / save_json / load_json /
# skip_if_exists / _price / install_logger / get_client / JST / THEME_TAG /
# REFERENCE_20 を再利用する(baseファイル自体は無変更)。
#
# モード: (引数なし)generate / --assemble-only / --contamination-check
# 冪等性: hooks/{article}_{model}.json が既に存在する場合、--forceなし
# では再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
from datetime import datetime
from difflib import SequenceMatcher

import er016_topic_selection_chatgpt_repro_01 as base

THEME_TAG = "NEWS_R2_TO_HOOK_TRIAL_01"
MODELS = {"luna": "gpt-5.6-luna", "terra": "gpt-5.6-terra", "sol": "gpt-5.6-sol"}
EFFORT = "medium"
COST_CEILING_JPY = 30

out_path = base.out_path
save_json = base.save_json
load_json = base.load_json
skip_if_exists = base.skip_if_exists

INPUT_FILES = {
    "sewer": os.path.join("docs", "evidence", "news_iterative_r2_adoption_2026-09-24",
                           "articles", "sewer_revision2.md"),
    "ai_phone": os.path.join("docs", "evidence", "news_iterative_r2_adoption_2026-09-24",
                              "articles", "ai_phone_revision2.md"),
    "travel_bag": os.path.join("docs", "evidence", "news_iterative_r2_adoption_2026-09-24",
                                "articles", "travel_bag_revision2.md"),
}
ORIGIN_ARTIFACT_FILES = {
    "sewer": os.path.join("er015_output", "news_iterative_entertainment_trial_01", "revision2.md"),
    "ai_phone": os.path.join("er015_output", "news_iterative_entertainment_trial_02", "A_revision2.md"),
    "travel_bag": os.path.join("er015_output", "news_iterative_entertainment_trial_02", "B_revision2.md"),
}
TOPICS = {
    "sewer": "老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討",
    "ai_phone": "AIに電話を頼んだら、裏では人間スタッフが話していた",
    "travel_bag": "旅行の荷物はなぜ毎回バッグいっぱいになるのか",
}

HOOK_SCHEMA = {
    "name": "r2_hook",
    "schema": {
        "type": "object",
        "properties": {
            "hook_ja": {"type": "string"},
            "used_angle_ja": {"type": "string"},
        },
        "required": ["hook_ja", "used_angle_ja"],
        "additionalProperties": False,
    },
    "strict": True,
}


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ------------------------------------------------------------
# Prompt builder (Fable固定逐語。変更・追加禁止)
# ------------------------------------------------------------
DEVELOPER = "あなたはHook Writerです。"

USER_TEMPLATE = """以下は、音声番組で読み上げる予定の完成記事です。この記事をまだ聞いていない人が、聞いた瞬間に「ちょっと知りたい」と思う短いHookを1つ作ってください。

記事タイトルの言い換えや要約ではなく、記事の中にすでにある一番面白い見方や、具体的な場面を使ってください。友人に話しかけるような短い一文の問いにし、目安は30字前後。「〜でしょうか」は使わず、「〜？」で終えてください。記事にない事実は加えず、誇張はしないでください。

【テーマ】
{topic}

【記事】
{article_full_text}

hook_ja(Hook 1文)と、used_angle_ja(記事のどの見方・場面を使ったか、1文)を返してください。"""


def build_prompt(article_key: str) -> str:
    topic = TOPICS[article_key]
    article_full_text = _read_text(INPUT_FILES[article_key])
    return USER_TEMPLATE.format(topic=topic, article_full_text=article_full_text)


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


def record_error(out_dir, article, key, exc):
    path = out_path(out_dir, "errors", f"{article}_{key}.json")
    save_json(path, {
        "article": article, "model_key": key, "model_id": MODELS[key],
        "error_type": type(exc).__name__, "error_message": str(exc),
        "logged_at_jst": datetime.now(base.JST).isoformat(),
    })
    print(f"[ERROR] {article}/{key}: {type(exc).__name__}: {exc}")


def record_stop(out_dir, article, key, message):
    path = out_path(out_dir, "stop_condition.json")
    save_json(path, {
        "stopped": True, "article": article, "model_key": key, "model_id": MODELS[key],
        "reason": message, "logged_at_jst": datetime.now(base.JST).isoformat(),
    })
    print(f"[STOP] {article}/{key}: {message}")


# ------------------------------------------------------------
# generate: 3記事×3モデル=9 call、独立
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

    for article in ("sewer", "ai_phone", "travel_bag"):
        for key in model_keys:
            if stop_triggered:
                print(f"[SKIP] {article}/{key}: 直前のSTOPのため未実行")
                continue
            model_id = MODELS[key]
            hooks_path = out_path(out_dir, "hooks", f"{article}_{key}.json")
            if skip_if_exists(hooks_path, args.force):
                continue

            user = build_prompt(article)
            save_json(out_path(out_dir, "prompts", f"{article}_{key}.json"),
                      {"developer": DEVELOPER, "user": user, "model_requested": model_id,
                       "effort": EFFORT, "article": article})
            stage_name = f"{article}_{key}"
            try:
                response, parsed = call_and_parse(client, DEVELOPER, user, HOOK_SCHEMA,
                                                    stage_name, model_id, out_dir)
            except RuntimeError as exc:
                if "STOP条件該当" in str(exc):
                    record_stop(out_dir, article, key, str(exc))
                    stop_triggered = True
                    continue
                record_error(out_dir, article, key, exc)
                continue
            except Exception as exc:
                record_error(out_dir, article, key, exc)
                continue
            meta = base.response_meta(response, user, DEVELOPER)
            save_json(hooks_path, {"article": article, "model_key": key,
                                    "hook_ja": parsed["hook_ja"],
                                    "used_angle_ja": parsed["used_angle_ja"]})
            save_json(out_path(out_dir, "raw_responses", f"{article}_{key}.json"), meta)
            print(f"[OK] {article}/{key}: hook_ja_len={len(parsed['hook_ja'])} "
                  f"model_actual={meta['response_model_actual']}")

    print("[DONE] generate phase 終了" f"{'(STOPあり)' if stop_triggered else ''}")


# ------------------------------------------------------------
# assemble-only: comparison_table.md / mechanical_stats.json / cost.json /
# r2_titles.json / run_meta.json(比較用Hookを生成完了後に読む)
# ------------------------------------------------------------
def _load_hook(out_dir, article, key):
    path = out_path(out_dir, "hooks", f"{article}_{key}.json")
    if not os.path.exists(path):
        return None
    return load_json(path)


def _r2_title(article_key: str) -> str:
    text = _read_text(INPUT_FILES[article_key])
    return text.splitlines()[0].strip()


# 旧方式(Topic概要→Hook)比較用: news_hook_model_comparison_01 の
# reference_id 1(AI電話/Meta Muse相当)・13(旅行荷物/圧縮ポーチ相当)の
# hooks_{model}.json。下水道は旧Trial対象外のため「旧方式なし」。
OLD_METHOD_REF_ID = {"ai_phone": 1, "travel_bag": 13, "sewer": None}
OLD_METHOD_DIR = os.path.join("er016_output", "news_hook_model_comparison_01")


def _old_method_hook(article_key: str, model_key: str, read_log: list) -> str:
    rid = OLD_METHOD_REF_ID.get(article_key)
    if rid is None:
        return "旧方式なし(下水道は旧Hook比較Trial対象外)"
    path = os.path.join(OLD_METHOD_DIR, f"hooks_{model_key}.json")
    if not os.path.exists(path):
        return "N/A(旧方式ファイル無し)"
    data = load_json(path)
    read_log.append({"file": path, "read_at_jst": datetime.now(base.JST).isoformat()})
    for r in data.get("results", []):
        if r.get("reference_id") == rid:
            return r.get("hook_ja", "")
    return "N/A(該当reference_id無し)"


# Existing/Reference Hook比較用: REFERENCE_20の id1(AI電話)・id13(旅行荷物)。
# 下水道はReferenceなし(既存Trialで比較可能なReference Hookが存在しない)。
EXISTING_REF_ID = {"ai_phone": 1, "travel_bag": 13, "sewer": None}


def _existing_reference_hook(article_key: str, read_log: list) -> str:
    rid = EXISTING_REF_ID.get(article_key)
    if rid is None:
        return "Referenceなし(下水道は既存Trialに対応するReference Hookが存在しない。R2タイトルを比較対象とする)"
    read_log.append({"source": "base.REFERENCE_20", "reference_id": rid,
                      "read_at_jst": datetime.now(base.JST).isoformat()})
    for r in base.REFERENCE_20:
        if r["id"] == rid:
            return r["hook_ja"]
    return "N/A(該当id無し)"


def _mechanical_stats(article_key: str, model_key: str, hook_ja: str, r2_title: str) -> dict:
    article_text = _read_text(INPUT_FILES[article_key])
    topic_text = TOPICS[article_key]
    ends_q = hook_ja.strip().endswith("？")
    has_deshouka = "でしょうか" in hook_ja
    title_ratio = round(SequenceMatcher(None, hook_ja, r2_title).ratio(), 3)
    # 数字・カタカナ語(3文字以上)候補を機械抽出し、記事本文またはテーマ文に
    # 部分一致するかを機械検査する(主観判定なし)。
    import re
    numbers = re.findall(r"\d+", hook_ja)
    katakana_words = re.findall(r"[゠-ヿ]{3,}", hook_ja)
    candidates = numbers + katakana_words
    haystack = article_text + topic_text
    unmatched = [c for c in candidates if c not in haystack]
    return {
        "hook_ja": hook_ja,
        "hook_ja_len": len(hook_ja),
        "ends_with_question_mark": ends_q,
        "contains_deshouka": has_deshouka,
        "r2_title_similarity_ratio": title_ratio,
        "numeric_katakana_candidates": candidates,
        "candidates_not_found_in_article_or_topic": unmatched,
        "fact_machine_match_ok": len(unmatched) == 0,
    }


def cmd_assemble(args):
    out_dir = args.out_dir
    model_keys = args.models.split(",")
    read_log = []

    r2_titles = {a: _r2_title(a) for a in ("sewer", "ai_phone", "travel_bag")}
    save_json(out_path(out_dir, "r2_titles.json"), r2_titles)

    hooks = {}
    for a in ("sewer", "ai_phone", "travel_bag"):
        for key in model_keys:
            hooks[(a, key)] = _load_hook(out_dir, a, key)

    existing_ref = {a: _existing_reference_hook(a, read_log) for a in ("sewer", "ai_phone", "travel_bag")}
    old_method = {(a, key): _old_method_hook(a, key, read_log)
                  for a in ("sewer", "ai_phone", "travel_bag") for key in ("luna", "terra", "sol")}

    # --- comparison_table.md 表1 ---
    lines = ["# comparison_table (NEWS-R2-TO-HOOK-TRIAL-01)", "",
             "## 表1: R2タイトル / Existing・Reference Hook / 旧方式(Topic概要→Hook) / 新方式(R2記事→Hook)",
             "",
             "| Article | R2タイトル | Existing/Reference Hook | 旧方式Luna | 旧方式Terra | 旧方式Sol | "
             "Luna from R2 | Terra from R2 | Sol from R2 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for a in ("sewer", "ai_phone", "travel_bag"):
        row = [a, r2_titles[a], existing_ref[a],
               old_method[(a, "luna")], old_method[(a, "terra")], old_method[(a, "sol")]]
        for key in ("luna", "terra", "sol"):
            h = hooks.get((a, key))
            row.append(h["hook_ja"] if h else "N/A(生成失敗/未生成)")
        lines.append("| " + " | ".join(c.replace("|", "\\|") for c in row) + " |")

    # --- 表2: used_angle_ja ---
    lines += ["", "## 表2: used_angle_ja", "", "| Article | Model | used_angle_ja |", "|---|---|---|"]
    for a in ("sewer", "ai_phone", "travel_bag"):
        for key in ("luna", "terra", "sol"):
            h = hooks.get((a, key))
            angle = h["used_angle_ja"] if h else "N/A"
            lines.append(f"| {a} | {key} | {angle.replace('|', chr(92) + '|')} |")

    # --- 表3: 機械統計 ---
    stats_all = {}
    lines += ["", "## 表3: 機械統計(観察事実のみ)", "",
              "| Article | Model | 文字数 | ？終端 | でしょうか含有 | R2タイトル一致率 | Fact機械一致 |",
              "|---|---|---|---|---|---|---|"]
    for a in ("sewer", "ai_phone", "travel_bag"):
        for key in ("luna", "terra", "sol"):
            h = hooks.get((a, key))
            if h is None:
                lines.append(f"| {a} | {key} | - | - | - | - | - |")
                continue
            s = _mechanical_stats(a, key, h["hook_ja"], r2_titles[a])
            stats_all[f"{a}_{key}"] = s
            lines.append(f"| {a} | {key} | {s['hook_ja_len']} | {s['ends_with_question_mark']} | "
                          f"{s['contains_deshouka']} | {s['r2_title_similarity_ratio']} | "
                          f"{s['fact_machine_match_ok']} |")

    with open(out_path(out_dir, "comparison_table.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    save_json(out_path(out_dir, "mechanical_stats.json"), stats_all)
    print(f"[OK] comparison_table.md / mechanical_stats.json 生成 (out_dir={out_dir})")

    # --- cost.json ---
    _cmd_cost(out_dir, model_keys)

    # --- run_meta.json (追記更新) ---
    meta_path = out_path(out_dir, "run_meta.json")
    meta = load_json(meta_path) if os.path.exists(meta_path) else {}
    input_sha = {a: {"input_file": INPUT_FILES[a], "input_sha256": _sha256(INPUT_FILES[a]),
                      "origin_artifact_file": ORIGIN_ARTIFACT_FILES[a],
                      "origin_artifact_sha256": _sha256(ORIGIN_ARTIFACT_FILES[a]),
                      "sha256_match": _sha256(INPUT_FILES[a]) == _sha256(ORIGIN_ARTIFACT_FILES[a])}
                 for a in ("sewer", "ai_phone", "travel_bag")}
    meta.update({
        "assembled_at_jst": datetime.now(base.JST).isoformat(),
        "models_requested": model_keys,
        "model_ids": {k: MODELS[k] for k in model_keys},
        "effort": EFFORT,
        "input_files_sha256": input_sha,
        "comparison_hook_reads_after_generation": read_log,
    })
    save_json(meta_path, meta)
    print(f"[OK] run_meta.json 更新: comparison_hook_reads={len(read_log)}件("
          "全て生成完了後)")


def _resolve_terra_price(pricing):
    for p in pricing:
        if p.get("provider") == "openai" and p.get("model") == "gpt-5.6-terra":
            return True
    return False


# 参考情報(単価を確定値として採用しない。er016_news_hook_model_comparison_01.py
# の同名調査結果を踏襲。捏造回避のためtoken数のみ記録)。
TERRA_PRICE_PROBE_EVIDENCE = {
    "attempted": True,
    "fetch_url": "https://platform.openai.com/docs/pricing",
    "resolution_status": "AMBIGUOUS_NOT_ADOPTED",
    "reason": "前タスク(NEWS-HOOK-MODEL-COMPARISON-01, 2026-09-24)と同一調査結果を踏襲。"
              "ページ内にgpt-5.6-terraを含む数値セットが複数存在し、tier/列構成が"
              "機械的に確定できないため、誤った単価を確定値として記録するリスクを"
              "避け、terra_price_status=UNKNOWNのまま採用しない。",
    "reused_from": "er016_output/news_hook_model_comparison_01/cost.json (by_model.terra.price_probe_evidence)",
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
    # 注記: base.call_model()はcl.logging_context(THEME_TAG, stage)を呼ぶが、
    # そのTHEME_TAGはbaseモジュール自身のグローバル定数
    # "TOPIC_SELECTION_CHATGPT_REPRO_01"(baseファイルは無変更のため変更不可)。
    # そのためtheme値ではなく、本スクリプトが発行したstage名
    # (例: "sewer_luna")で該当callを絞り込む。
    expected_stages = {f"{a}_{key}" for a in ("sewer", "ai_phone", "travel_bag") for key in model_keys}
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
            "latency_seconds_by_call": {}, "latency_seconds_total": 0.0,
        })
        s["actual_model_ids"].add(model_id)
        s["calls"] += 1
        s["input_tokens"] += it
        s["cached_input_tokens"] += ct
        s["output_tokens"] += ot
        s["reasoning_tokens"] += rt
        s["latency_seconds_by_call"][stage] = s["latency_seconds_by_call"].get(stage, 0.0) + latency
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
            "latency_seconds_by_call": s["latency_seconds_by_call"],
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
                per_hook_jpy = round(jpy / s["calls"], 3) if s["calls"] else None
                entry.update({
                    "price_status": "KNOWN",
                    "price_source": "er005_output/cost_baseline_01/pricing_snapshot.json",
                    "total_usd": round(usd, 5),
                    "total_jpy": jpy,
                    "per_hook_jpy": per_hook_jpy,
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

    old_hooks_dir = os.path.join("er016_output", "news_hook_model_comparison_01")
    for key in ("luna", "terra", "sol"):
        fpath = os.path.join(old_hooks_dir, f"hooks_{key}.json")
        if os.path.exists(fpath):
            data = load_json(fpath)
            for r in data.get("results", []):
                forbidden_strings.append((f"old_method_hooks_{key}", r.get("reference_id"),
                                           r.get("hook_ja", "")))

    cont02_dir = os.path.join("er016_output", "topic_selection_chatgpt_repro_01_cont02")
    for fname in ("hook_test_h3.json", "hook_test_h3_sol.json"):
        fpath = os.path.join(cont02_dir, fname)
        if os.path.exists(fpath):
            data = load_json(fpath)
            for r in data.get("results", []):
                forbidden_strings.append((f"cont02_{fname}", r.get("reference_id"), r.get("hook_ja", "")))

    eval_dataset_path = os.path.join("docs", "pm", "topic_selection_user_eval_dataset.json")
    if os.path.exists(eval_dataset_path):
        eval_data = load_json(eval_dataset_path)
        for ds_key in ("dataset_r", "dataset_a", "dataset_b"):
            for item in eval_data.get(ds_key, []):
                forbidden_strings.append((f"{ds_key}_hook_ja", item.get("item_no"), item.get("hook_ja", "")))

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

    model_id_checks = []
    all_match = True
    for a in ("sewer", "ai_phone", "travel_bag"):
        for key in model_keys:
            model_id = MODELS[key]
            raw_path = out_path(out_dir, "raw_responses", f"{a}_{key}.json")
            if not os.path.exists(raw_path):
                continue
            meta = load_json(raw_path)
            actual = meta.get("response_model_actual")
            matched = bool(actual) and actual.startswith(model_id)
            if not matched:
                all_match = False
            model_id_checks.append({
                "article": a, "model_key": key, "requested": model_id,
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
        input_sha = {a: {"input_file": INPUT_FILES[a], "input_sha256": _sha256(INPUT_FILES[a]),
                          "origin_artifact_file": ORIGIN_ARTIFACT_FILES[a],
                          "origin_artifact_sha256": _sha256(ORIGIN_ARTIFACT_FILES[a]),
                          "sha256_match": _sha256(INPUT_FILES[a]) == _sha256(ORIGIN_ARTIFACT_FILES[a])}
                     for a in ("sewer", "ai_phone", "travel_bag")}
        save_json(meta_path, {
            "created_at_jst": datetime.now(base.JST).isoformat(),
            "script_sha256_or_git_hash": _script_sha(),
            "theme_tag": THEME_TAG,
            "input_files_sha256": input_sha,
        })

    if args.contamination_check:
        cmd_contamination_check(args)
    elif args.assemble_only:
        cmd_assemble(args)
    else:
        cmd_generate(args)


if __name__ == "__main__":
    main()
