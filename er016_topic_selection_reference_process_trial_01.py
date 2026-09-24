# ============================================================
# er016_topic_selection_reference_process_trial_01.py
# TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01(Fable設計、2026-09-24)
# ============================================================
# 目的: 固定Lane/固定Query方式(Trial-03)ではなく、Referenceを作った
# ときに近い「逐次探索・方向転換型」プロセス(広いSearch→読む→次の
# 探索方向を決める→Pool更新→途中レビュー→繰り返す)を再現し、
# Reference級の「聞きたくなるTopic」を最大20件集められるか検証する。
# Production実装ではない。Production正式path(daily runner・
# er011_*/er014_*等)は一切変更しない。
#
# 本Trialでは、探索中の判断(候補の拾い上げ・棄却・次の探索方向・
# Source差替え)はSonnet(このスクリプトを実行するエージェント)が行う。
# このスクリプト自体は「1回のSearch call実行」「機械signalによる
# Source Gate」「Pool更新(Sonnetが作った差分ファイルの適用)」
# 「cost集計」「公開日時検証」「5集合比較」「非混入検査」のみを担当し、
# Query設計・Pool取捨選択の判断ロジックは持たない(意図的)。
#
# 再利用: er002_ja_web_research_r3(extract_web_search_usage/
# extract_sources)、er005_cost_logger(install/logging_context)、
# er006_model_routing_contract_01(WRITER_MODEL)。
# er016_topic_selection_chatgpt_repro_01.pyはimportのみ(REFERENCE_20/
# REFERENCE_CONTAMINATION_KEYWORDS)。既存script(er016_topic_selection_
# search_trial_03.py含む)は一切変更しない。
#
# --step: search / cost-check / gate / pool / verify / compare /
#   contamination-check
# 冪等性: --forceなしでは既存の丸ごと上書きになりうる出力(pool.json等)を
# 意図的に許可するstepがある(pool applyは差分適用のため毎回実行が前提)。
# search/gate/verify/compareは出力ファイル存在チェックで--force必須。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er016_topic_selection_chatgpt_repro_01 as repro01

load_dotenv()

THEME_TAG = "TOPIC_SELECTION_REFERENCE_PROCESS_TRIAL_01"
MODEL_LUNA = routing.WRITER_MODEL  # "gpt-5.6-luna"
EFFORT_DEFAULT = "medium"
JST = timezone(timedelta(hours=9))
UTC = timezone.utc

WINDOW_START_JST = "2026-09-22T21:05:00+09:00"

BUDGET_JPY = 150.0
USD_TO_JPY = 160
MAX_SEARCH_CALLS_TOTAL = 20

EVAL_DATASET_PATH = "docs/pm/topic_selection_user_eval_dataset.json"
TRIAL03_FINAL20_PATH = "er016_output/topic_selection_search_trial_03/final20.json"

# UGCドメイン(委任文指定。Trial-03の機械PR signalに追加する)
UGC_DOMAIN_RE = re.compile(
    r"note\.com|reddit\.com|minkara|ameblo|hatenablog|x\.com|twitter\.com|"
    r"instagram\.com|gravity",
    re.IGNORECASE,
)
MACHINE_PR_SIGNAL_RE = re.compile(
    r"prtimes|/pr/|sponsored|PR|おすすめ|選|ランキング|セール|価格比較|"
    r"楽天|amazon|アフィリエイト|clip|kakaku",
    re.IGNORECASE,
)

# 非混入検査の対象stage prefix(compareのみ意図的な例外。理由はREPORTに明記)
CONTAMINATION_CHECK_PREFIXES = ("search_r", "gate_", "queries_")


# ------------------------------------------------------------
# ヘルパー(Trial-03パターン踏襲。既存scriptは変更せず、本ファイルに
# 同等ロジックを再実装する)
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


def run_meta_path(out_dir: str) -> str:
    return out_path(out_dir, "run_meta.json")


def ensure_run_meta(out_dir: str) -> dict:
    path = run_meta_path(out_dir)
    if os.path.exists(path):
        return load_json(path)
    now_jst = datetime.now(JST)
    meta = {
        "window_start_jst": WINDOW_START_JST,
        "window_end_jst": now_jst.isoformat(),
        "window_note": "公開日時2026-09-22 21:05 JST〜実行開始時刻(Trial-03と"
                       "同一窓の考え方)。",
        "created_at_jst": now_jst.isoformat(),
    }
    save_json(path, meta)
    print(f"[OK] run_meta作成: window_end_jst={meta['window_end_jst']}")
    return meta


def call_model(client, developer: str, user: str, schema=None, web_search=False,
                context_size=None, stage="", model=MODEL_LUNA, effort=EFFORT_DEFAULT,
                retried=False):
    """1回のAPI技術的retryのみを許可する(品質理由の再実行は禁止)。"""
    kwargs = dict(
        model=model,
        reasoning={"effort": effort},
        input=[
            {"role": "developer", "content": developer},
            {"role": "user", "content": user},
        ],
    )
    if schema is not None:
        kwargs["text"] = {"format": {"type": "json_schema", **schema}}
    context_size_accepted = None
    if web_search:
        tool = {"type": "web_search"}
        if context_size:
            tool["search_context_size"] = context_size
        kwargs["tools"] = [tool]
        try:
            with cl.logging_context(THEME_TAG, stage):
                response = client.responses.create(**kwargs)
            context_size_accepted = bool(context_size)
        except Exception as exc:
            if context_size and not retried:
                print(f"[RETRY] {stage}: search_context_size='{context_size}'が"
                      f"拒否された可能性 ({exc})。省略して再試行します。")
                del kwargs["tools"]
                kwargs["tools"] = [{"type": "web_search"}]
                try:
                    with cl.logging_context(THEME_TAG, stage):
                        response = client.responses.create(**kwargs)
                    context_size_accepted = False
                except Exception as exc2:
                    raise exc2
            else:
                raise
    else:
        try:
            with cl.logging_context(THEME_TAG, stage):
                response = client.responses.create(**kwargs)
        except Exception as exc:
            if retried:
                raise
            print(f"[RETRY] {stage}: 技術的retry 1回目 ({exc})")
            time.sleep(2)
            return call_model(client, developer, user, schema=schema,
                               web_search=web_search, context_size=context_size,
                               stage=stage, model=model, effort=effort, retried=True)
    if response.model != model:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={model}, actual={response.model})"
        )
    return response, context_size_accepted


def response_meta(response, prompt: str, developer: str, extra: dict = None) -> dict:
    meta = {
        "prompt": prompt,
        "developer_message": developer,
        "model_requested": response.model,
        "response_model_actual": response.model,
        "response_id": response.id,
    }
    usage = getattr(response, "usage", None)
    if usage is not None:
        meta["usage"] = {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
    meta["web_search_usage"] = r3.extract_web_search_usage(response)
    meta["sources"] = r3.extract_sources(response)
    if extra:
        meta.update(extra)
    return meta


def save_prompt_and_response(out_dir: str, stage: str, developer: str, user: str,
                              meta: dict) -> None:
    save_json(out_path(out_dir, "prompts", f"{stage}.json"),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", f"{stage}.json"), meta)


# ------------------------------------------------------------
# cost集計
# ------------------------------------------------------------
def _price(pricing, provider, model, meter):
    return next(p["price"] for p in pricing
                if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter)


def compute_cost(out_dir: str) -> dict:
    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]
    ws_price = _price(pricing, "openai", "N/A (tool, all models)", "web_search_call")

    def model_prices(model_name):
        return (
            _price(pricing, "openai", model_name, "input_tokens"),
            _price(pricing, "openai", model_name, "cached_input_tokens"),
            _price(pricing, "openai", model_name, "output_tokens"),
        )

    price_cache = {}
    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    entries = [e for e in entries if e.get("theme") == THEME_TAG]

    by_stage = {}
    total_usd = 0.0
    total_calls = 0
    total_ws_calls = 0
    for e in entries:
        if e.get("provider") != "openai" or not e.get("success", True):
            continue
        stage = e.get("stage") or "unknown"
        model_name = e.get("model_id") or MODEL_LUNA
        if model_name not in price_cache:
            try:
                price_cache[model_name] = model_prices(model_name)
            except StopIteration:
                price_cache[model_name] = model_prices(MODEL_LUNA)
        p_in, p_cached, p_out = price_cache[model_name]
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        ws = e.get("web_search_call_count") or 0
        billable_in = max(it - ct, 0)
        usd = (billable_in / 1_000_000) * p_in + (ct / 1_000_000) * p_cached \
            + (ot / 1_000_000) * p_out + (ws / 1000) * ws_price
        s = by_stage.setdefault(stage, {"calls": 0, "input_tokens": 0,
                                         "cached_input_tokens": 0, "output_tokens": 0,
                                         "web_search_call_count": 0, "usd": 0.0,
                                         "model": model_name})
        s["calls"] += 1
        s["input_tokens"] += it
        s["cached_input_tokens"] += ct
        s["output_tokens"] += ot
        s["web_search_call_count"] += ws
        s["usd"] += usd
        total_usd += usd
        total_calls += 1
        total_ws_calls += ws

    by_stage_jpy = {
        stage: {**vals, "jpy": round(vals["usd"] * USD_TO_JPY, 2)}
        for stage, vals in by_stage.items()
    }
    result = {
        "by_stage": by_stage_jpy,
        "total_jpy": round(total_usd * USD_TO_JPY, 2),
        "total_openai_calls": total_calls,
        "total_web_search_call_count": total_ws_calls,
        "usd_to_jpy": USD_TO_JPY,
        "budget_jpy": BUDGET_JPY,
        "within_budget": round(total_usd * USD_TO_JPY, 2) <= BUDGET_JPY,
    }
    save_json(out_path(out_dir, "cost.json"), result)
    return result


def count_search_calls_so_far(out_dir: str) -> int:
    cost = compute_cost(out_dir)
    return sum(v["calls"] for k, v in cost["by_stage"].items() if k.startswith("search_r"))


# ------------------------------------------------------------
# 非混入検査キーワード集合
# ------------------------------------------------------------
def contamination_keywords() -> list:
    kws = list(repro01.REFERENCE_CONTAMINATION_KEYWORDS)
    ds = load_json(EVAL_DATASET_PATH)
    for key in ("dataset_r", "dataset_a", "dataset_b"):
        for item in ds[key]:
            if item.get("topic_ja"):
                kws.append(item["topic_ja"])
            if item.get("hook_ja"):
                kws.append(item["hook_ja"])
    return kws


def check_contamination_in_text(text: str, keywords: list) -> list:
    return [kw for kw in keywords if kw and kw in text]


def cmd_contamination_check(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "contamination_check.json")
    if skip_if_exists(path, args.force):
        return
    keywords = contamination_keywords()
    prompts_dir = out_path(out_dir, "prompts")
    checked = []
    hits = []
    excluded_by_design = []
    if os.path.exists(prompts_dir):
        for fname in sorted(os.listdir(prompts_dir)):
            fpath = os.path.join(prompts_dir, fname)
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
            if fname.startswith("compare"):
                excluded_by_design.append(fname)
                continue
            if not fname.startswith(CONTAMINATION_CHECK_PREFIXES):
                continue
            checked.append(fname)
            for kw in check_contamination_in_text(content, keywords):
                hits.append({"file": fname, "keyword": kw})
    # queries_round*.json(Sonnetが作成したQueryファイル)も検査対象に含める
    for fname in sorted(os.listdir(out_dir)):
        if fname.startswith("queries_round") and fname.endswith(".json"):
            fpath = os.path.join(out_dir, fname)
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
            checked.append(fname)
            for kw in check_contamination_in_text(content, keywords):
                hits.append({"file": fname, "keyword": kw})
    result = {
        "keyword_count": len(keywords),
        "checked_files": checked,
        "excluded_by_design_files": excluded_by_design,
        "excluded_by_design_reason": (
            "compare_*: 5集合比較のため委任文で明示的に許可されたstage"
            "(Reference/A/B/Trial-03のTopic文字列を型分類のためだけに使用し、"
            "Query/Search入力へは投入しない)。"
        ),
        "contamination_hits": hits,
        "contaminated": len(hits) > 0,
    }
    save_json(path, result)
    print(f"[OK] contamination-check: checked_files={len(checked)} "
          f"keywords={len(keywords)} hits={len(hits)} contaminated={result['contaminated']}")


# ============================================================
# step: search(Sonnetが作った queries_round{n}.json を1件ずつ実行)
# ============================================================
def _candidate_item_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "source_name": {"type": "string"},
            "url": {"type": "string"},
            "published_time_as_shown": {"type": ["string", "null"]},
            "published_time_iso": {"type": ["string", "null"]},
            "time_uncertain": {"type": "boolean"},
            "summary_2sent_ja": {"type": "string"},
            "why_interesting_ja": {"type": "string"},
            "country_scope": {"type": "string"},
            "is_pr_or_ad_guess": {"type": "boolean"},
        },
        "required": ["title", "source_name", "url", "published_time_as_shown",
                     "published_time_iso", "time_uncertain", "summary_2sent_ja",
                     "why_interesting_ja", "country_scope", "is_pr_or_ad_guess"],
        "additionalProperties": False,
    }


def _search_call_schema(name: str) -> dict:
    return {
        "name": name,
        "schema": {
            "type": "object",
            "properties": {
                "candidates": {"type": "array", "items": _candidate_item_schema(), "maxItems": 10},
            },
            "required": ["candidates"],
            "additionalProperties": False,
        },
        "strict": True,
    }


SEARCH_DEVELOPER = (
    "あなたはNews Discovery担当です。web_searchツールで実際に見つけた"
    "記事・話題・投稿だけを報告してください。存在しない記事やURLを作らない"
    "でください。候補のurlは検索結果の引用に実際に現れたURLのみを使用し、"
    "記憶や推測でURLを組み立てないでください。"
    "候補のurlは、必ず個別記事の本文ページ(permalink)にしてください。"
    "一覧・カテゴリ・タグ・キーワードページ(例: /topics/category/…、"
    "/topics/keyword/…、/fringe/ のような一覧URL)は候補として使わない"
    "でください。個別記事URLが検索結果に見つからない場合は、その候補は"
    "報告しないでください。"
    "検索は必要最小限(1〜2回)にしてください。1回のクエリで幅広い候補を"
    "見つけ、見つかった記事の中から最大10件、多様な話題を返してください"
    "(同じニュースの重複掲載は避けてください)。"
)


def _search_one_query(client, out_dir, meta_run, query_rec, stage, round_no, context_size):
    user = f"""対象窓(JST、固定): {meta_run['window_start_jst']} 〜 {meta_run['window_end_jst']}
以下の検索クエリを使って、この窓内に公開・話題化した記事・話題を探して
ください。

【検索クエリ】
{query_rec['query_ja']}
(このクエリを設計した意図: {query_rec.get('rationale_ja', '')})

窓より前や後に公開された記事は候補にしないでください。公開時刻が確認
できない場合は無理に断定せず、time_uncertain: trueとしてください。

最大10件、JSONで返してください。該当が少なければ無理に埋めず、実際に
見つかった件数だけ返してください。各候補にtitle・source_name・url
(検索結果の引用に実際に現れたURLのみ)・published_time_as_shown・
published_time_iso・time_uncertain・summary_2sent_ja(1〜2文)・
why_interesting_ja(なぜ気になるか1文。専門性・重要性だけでなく、
具体性・自分事性・意外性・話したくなるかという観点で書くこと)・
country_scope(日本/世界/特定国名)・is_pr_or_ad_guess(PR・広告・
アフィリエイト・個人ブログ・SNS投稿一覧らしいか)を埋めてください。"""

    response, context_size_accepted = call_model(
        client, SEARCH_DEVELOPER, user, schema=_search_call_schema(stage),
        web_search=True, context_size=context_size, stage=stage)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, SEARCH_DEVELOPER,
                          extra={"context_size_requested": context_size,
                                 "context_size_accepted": context_size_accepted})
    save_prompt_and_response(out_dir, stage, SEARCH_DEVELOPER, user, meta)
    candidates = []
    for c in parsed["candidates"]:
        c = dict(c)
        c["query_ja"] = query_rec["query_ja"]
        c["rationale_ja"] = query_rec.get("rationale_ja", "")
        c["round"] = round_no
        candidates.append(c)
    return candidates, meta


def cmd_search(args):
    out_dir = args.out_dir
    round_no = args.round
    raw_path = out_path(out_dir, f"search_round{round_no}_raw.json")
    if skip_if_exists(raw_path, args.force):
        return
    queries_data = load_json(args.queries_file)
    queries = queries_data["queries"]
    meta_run = ensure_run_meta(out_dir)
    install_logger(out_dir)
    client = get_client()

    calls_used = count_search_calls_so_far(out_dir)
    remaining = MAX_SEARCH_CALLS_TOTAL - calls_used
    if remaining <= 0:
        raise RuntimeError(
            f"STOP条件該当: 総Search call上限{MAX_SEARCH_CALLS_TOTAL}に既に到達"
            f"(calls_used={calls_used})")
    max_calls = min(len(queries), remaining)

    all_candidates = []
    calls_made = 0
    stop_reason = None
    for i, q in enumerate(queries[:max_calls], start=1):
        cost_so_far = compute_cost(out_dir)["total_jpy"]
        if cost_so_far >= BUDGET_JPY:
            stop_reason = (f"budget_guard: cost so far={cost_so_far} JPY >= "
                            f"budget={BUDGET_JPY} JPY, stopped after "
                            f"{calls_made}/{max_calls} calls in round{round_no}")
            print(f"[STOP] {stop_reason}")
            break
        stage = f"search_r{round_no}_{i:02d}"
        try:
            cands, meta = _search_one_query(client, out_dir, meta_run, q, stage,
                                             round_no, args.context_size)
        except Exception as exc:
            print(f"[WARN] {stage} failed: {exc}")
            continue
        all_candidates.extend(cands)
        calls_made += 1
        print(f"[OK] {stage}: candidates={len(cands)} model={meta['response_model_actual']} "
              f"ws_calls={meta['web_search_usage']['web_search_call_count']} "
              f"context_size_accepted={meta.get('context_size_accepted')}")

    # dedup by URL(このラウンド内)
    seen = set()
    deduped = []
    for c in all_candidates:
        url = c.get("url")
        if url and url in seen:
            continue
        if url:
            seen.add(url)
        deduped.append(c)
    for idx, c in enumerate(deduped, start=1):
        c["candidate_id"] = f"R{round_no}_{idx:03d}"

    result = {
        "round": round_no,
        "queries_available": len(queries),
        "calls_made": calls_made,
        "queries_used": max_calls,
        "raw_candidate_count": len(all_candidates),
        "deduped_candidate_count": len(deduped),
        "stop_reason": stop_reason,
        "candidates": deduped,
    }
    save_json(raw_path, result)
    if stop_reason:
        save_json(out_path(out_dir, f"stop_reason_round{round_no}.json"),
                   {"stage": f"search_round{round_no}", "reason": stop_reason})
    compute_cost(out_dir)
    print(f"[OK] search round{round_no}: calls_made={calls_made}/{max_calls} "
          f"raw={len(all_candidates)} deduped={len(deduped)} "
          f"total_calls_used={count_search_calls_so_far(out_dir)}/{MAX_SEARCH_CALLS_TOTAL}")


# ============================================================
# step: cost-check(Round 1終了時の継続判断用)
# ============================================================
def cmd_cost_check(args):
    out_dir = args.out_dir
    cost = compute_cost(out_dir)
    search_stages = {k: v for k, v in cost["by_stage"].items() if k.startswith("search_r")}
    calls = sum(v["calls"] for v in search_stages.values())
    jpy = sum(v["jpy"] for v in search_stages.values())
    per_call = round(jpy / calls, 3) if calls else None
    projected_total = round(per_call * args.planned_calls, 2) if per_call is not None else None
    recommend_stop = projected_total is not None and projected_total > args.budget_jpy
    result = {
        "search_calls_so_far": calls,
        "search_jpy_so_far": jpy,
        "per_call_jpy": per_call,
        "planned_calls": args.planned_calls,
        "projected_total_jpy": projected_total,
        "budget_jpy": args.budget_jpy,
        "recommend_stop": recommend_stop,
    }
    save_json(out_path(out_dir, "cost_projection.json"), result)
    print(f"[OK] cost-check: calls={calls} jpy_so_far={jpy} per_call={per_call} "
          f"projected_total(@{args.planned_calls}calls)={projected_total} "
          f"budget={args.budget_jpy} recommend_stop={recommend_stop}")


# ============================================================
# step: gate(機械signalのみ。LLM呼び出しなし=無料)
# ============================================================
def cmd_gate(args):
    out_dir = args.out_dir
    round_no = args.round
    raw_path = out_path(out_dir, f"search_round{round_no}_raw.json")
    gate_path = out_path(out_dir, f"gate_round{round_no}.json")
    if skip_if_exists(gate_path, args.force):
        return
    raw = load_json(raw_path)
    signals = []
    for c in raw["candidates"]:
        url_title = f"{c.get('url', '')} {c.get('title', '')} {c.get('source_name', '')}"
        machine_pr_signal = bool(MACHINE_PR_SIGNAL_RE.search(url_title))
        machine_ugc_signal = bool(UGC_DOMAIN_RE.search(c.get("url", "") or ""))
        signals.append({
            "candidate_id": c["candidate_id"],
            "title": c["title"],
            "url": c["url"],
            "source_name": c["source_name"],
            "machine_pr_signal": machine_pr_signal,
            "machine_ugc_signal": machine_ugc_signal,
            "is_pr_or_ad_guess_model": c.get("is_pr_or_ad_guess"),
            "machine_exclude_recommended": machine_pr_signal or machine_ugc_signal,
        })
    result = {
        "round": round_no,
        "total": len(signals),
        "machine_exclude_recommended_count": sum(1 for s in signals if s["machine_exclude_recommended"]),
        "signals": signals,
        "note": "機械signalのみ(LLM呼び出しなし)。最終kept/dropped判断はSonnetが"
                "pool step適用時に行う(--step poolのupdates-fileに記録)。",
    }
    save_json(gate_path, result)
    print(f"[OK] gate round{round_no}: total={len(signals)} "
          f"machine_exclude_recommended={result['machine_exclude_recommended_count']}")


# ============================================================
# step: pool(Sonnetが作ったupdatesファイルをpool.jsonへ適用)
# ============================================================
POOL_PATH_NAME = "pool.json"


def cmd_pool(args):
    out_dir = args.out_dir
    pool_path = out_path(out_dir, POOL_PATH_NAME)
    updates = load_json(args.updates_file)
    pool = load_json(pool_path) if os.path.exists(pool_path) else {"candidates": {}}
    for u in updates["candidates"]:
        cid = u["candidate_id"]
        pool["candidates"][cid] = u
    kept = [c for c in pool["candidates"].values() if c["status"] == "kept"]
    dropped = [c for c in pool["candidates"].values() if c["status"] == "dropped"]
    replaced = [c for c in pool["candidates"].values() if c["status"] == "replaced"]
    pool["summary"] = {
        "total": len(pool["candidates"]),
        "kept_count": len(kept),
        "dropped_count": len(dropped),
        "replaced_count": len(replaced),
        "last_round_applied": args.round,
    }
    save_json(pool_path, pool)
    print(f"[OK] pool round{args.round} applied: total={pool['summary']['total']} "
          f"kept={len(kept)} dropped={len(dropped)} replaced={len(replaced)}")


# ============================================================
# step: verify(公開日時のHTTP検証。pool.jsonのkept対象)
# ============================================================
def _fetch(url: str):
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; eigo-radio-topic-research/1.0)"})
        return resp, None
    except Exception as exc:
        return None, str(exc)[:300]


def _extract_published_time(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for prop in ("article:published_time", "og:article:published_time", "article:published"):
        tag = soup.find("meta", attrs={"property": prop})
        if tag and tag.get("content"):
            return tag["content"], f"meta[property={prop}]"
    for name in ("pubdate", "date", "publish-date", "sailthru.date", "parsely-pub-date"):
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"], f"meta[name={name}]"
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
        except Exception:
            continue
        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            nodes = item.get("@graph", [item]) if isinstance(item.get("@graph"), list) else [item]
            for node in nodes:
                if isinstance(node, dict) and node.get("datePublished"):
                    return node["datePublished"], "json-ld:datePublished"
    time_tag = soup.find("time", attrs={"datetime": True})
    if time_tag and time_tag.get("datetime"):
        return time_tag["datetime"], "time[datetime]"
    return None, None


def _classify_window(raw_time: str, window_start_iso: str, window_end_iso: str):
    from dateutil import parser as dtparser
    w_start = dtparser.isoparse(window_start_iso).astimezone(UTC)
    w_end = dtparser.isoparse(window_end_iso).astimezone(UTC)
    try:
        dt = dtparser.parse(raw_time)
    except Exception:
        return None, "unverifiable"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    dt_utc = dt.astimezone(UTC)
    if w_start <= dt_utc <= w_end:
        return dt_utc.isoformat(), "within_window"
    return dt_utc.isoformat(), "outside_window"


def _verify_url(url: str, meta_run: dict) -> dict:
    resp, err = _fetch(url)
    if err is not None or resp is None:
        return {"http_status": None, "status_class": "unreachable_error", "error": err,
                "published_time_verified": None, "window_classification": "unverifiable",
                "disqualified": False}
    code = resp.status_code
    if code == 200:
        cls = "ok"
    elif code == 403:
        cls = "forbidden_bot_block"
    elif code == 404:
        cls = "not_found"
    else:
        cls = f"http_error_{code}"
    published_time_verified = None
    window_classification = "unverifiable"
    if cls == "ok":
        raw_time, _method = _extract_published_time(resp.text)
        if raw_time is not None:
            published_time_verified, window_classification = _classify_window(
                raw_time, meta_run["window_start_jst"], meta_run["window_end_jst"])
    disqualified = cls == "not_found" or window_classification == "outside_window"
    return {"http_status": code, "status_class": cls, "error": None,
            "published_time_verified": published_time_verified,
            "window_classification": window_classification, "disqualified": disqualified}


def cmd_verify(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "verify_results.json")
    if skip_if_exists(path, args.force):
        return
    pool = load_json(out_path(out_dir, POOL_PATH_NAME))
    meta_run = ensure_run_meta(out_dir)
    kept = [c for c in pool["candidates"].values() if c["status"] == "kept"]

    results = []
    for c in kept:
        v = _verify_url(c.get("url") or "", meta_run)
        entry = {**c, **v}
        results.append(entry)
        time.sleep(0.2)

    disqualified = [r for r in results if r["disqualified"]]
    final_ok = [r for r in results if not r["disqualified"]]
    save_json(path, {
        "window_start_jst": meta_run["window_start_jst"],
        "window_end_jst": meta_run["window_end_jst"],
        "checked_count": len(results),
        "disqualified_count": len(disqualified),
        "final_ok_count": len(final_ok),
        "verify_results": results,
    })
    print(f"[OK] verify: checked={len(results)} disqualified={len(disqualified)} "
          f"final_ok={len(final_ok)}")


# ============================================================
# step: compare(5集合の型比較、1 call)
# ============================================================
COMPARE_TYPE_TAGS = ["Everyday", "Personal", "Reversal", "Talkability", "BigChange",
                      "HardSocial", "Tech", "Product", "Entertainment"]

COMPARE_SCHEMA = {
    "name": "compare_classify",
    "schema": {
        "type": "object",
        "properties": {
            "classifications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string"},
                        "type_tags": {"type": "array", "items": {"type": "string", "enum": COMPARE_TYPE_TAGS}},
                        "domestic_or_intl": {"type": "string", "enum": ["domestic", "international", "unclear"]},
                    },
                    "required": ["item_id", "type_tags", "domestic_or_intl"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["classifications"],
        "additionalProperties": False,
    },
    "strict": True,
}

COMPARE_DEVELOPER = (
    "あなたはNews Topicの型分類担当です。与えられたTopicの短い説明文だけ"
    "を見て、あてはまる型タグ(複数可)と国内/海外を分類してください。"
    "面白いかどうかの評価はしないでください(分類のみ)。"
)


def cmd_compare(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "comparison_sets.md")
    if skip_if_exists(path, args.force):
        return
    ds = load_json(EVAL_DATASET_PATH)
    final_candidates = load_json(out_path(out_dir, "final_candidates.json"))
    trial03_final20 = load_json(TRIAL03_FINAL20_PATH)

    items = []
    for it in repro01.REFERENCE_20:
        items.append({"item_id": f"R_{it['id']}", "set_label": "Reference(R)", "topic_ja": it["topic_ja"]})
    for it in ds["dataset_a"]:
        items.append({"item_id": f"A_{it['item_no']}", "set_label": "ChatGPT API-only(A)", "topic_ja": it["topic_ja"]})
    for it in ds["dataset_b"]:
        items.append({"item_id": f"B_{it['item_no']}", "set_label": "Luna API(B)", "topic_ja": it["topic_ja"]})
    for i, it in enumerate(trial03_final20["final20"], start=1):
        items.append({"item_id": f"T3_{i}", "set_label": "Trial-03(T3, 17件)", "topic_ja": it["topic_ja"]})
    for i, it in enumerate(final_candidates["final_candidates"], start=1):
        items.append({"item_id": f"RP_{i}", "set_label": "RefProcess(今回)", "topic_ja": it["topic_ja"]})

    install_logger(out_dir)
    client = get_client()
    user = f"""【Topicの型タグ】
{', '.join(COMPARE_TYPE_TAGS)}
(Everyday=日常のなぜ/Personal=自分事/Reversal=意外な逆転/Talkability=
話したくなる俗っぽさ/BigChange=一文で世の中が変わった/HardSocial=硬い
社会・政治・国際ニュース/Tech=技術中心/Product=商品・サービス中心/
Entertainment=芸能・スポーツ・エンタメ)

【分類対象(5集合、計{len(items)}件)】
{json.dumps([{"item_id": it["item_id"], "topic_ja": it["topic_ja"]} for it in items], ensure_ascii=False, indent=2)}

各item_idについて、あてはまる型タグ(複数可、最低1つ)とdomestic_or_intl
を返してください。"""

    response, _ = call_model(client, COMPARE_DEVELOPER, user, schema=COMPARE_SCHEMA,
                              web_search=False, stage="compare_classify")
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, COMPARE_DEVELOPER)
    save_prompt_and_response(out_dir, "compare_classify", COMPARE_DEVELOPER, user, meta)
    cls_by_id = {c["item_id"]: c for c in parsed["classifications"]}

    sets = {}
    for it in items:
        label = it["set_label"]
        cls = cls_by_id.get(it["item_id"], {"type_tags": [], "domestic_or_intl": "unclear"})
        s = sets.setdefault(label, {"n": 0, "tag_counts": {}, "domestic": 0, "international": 0, "unclear": 0})
        s["n"] += 1
        for t in cls["type_tags"]:
            s["tag_counts"][t] = s["tag_counts"].get(t, 0) + 1
        s[cls["domestic_or_intl"]] = s.get(cls["domestic_or_intl"], 0) + 1

    ref_topics = {it["id"]: it["topic_ja"] for it in repro01.REFERENCE_20}
    overlap_hits = []
    for i, it in enumerate(final_candidates["final_candidates"], start=1):
        rp_words = set(re.findall(r"[一-龥ぁ-んァ-ヶA-Za-z0-9]{2,}", it["topic_ja"]))
        for rid, rtopic in ref_topics.items():
            r_words = set(re.findall(r"[一-龥ぁ-んァ-ヶA-Za-z0-9]{2,}", rtopic))
            if not rp_words or not r_words:
                continue
            jac = len(rp_words & r_words) / len(rp_words | r_words)
            if jac >= 0.3:
                overlap_hits.append({"refproc_item": it["topic_ja"], "reference_id": rid,
                                      "reference_topic": rtopic, "jaccard": round(jac, 3)})

    lines = ["# comparison_sets.md (機械集計、観察のみ、評価はFable/ユーザー)", "",
              f"分類model: {meta['response_model_actual']} / 対象件数: {len(items)}", "",
              "## 型タグ比率(集合別、%)", "",
              "| 集合 | n | " + " | ".join(COMPARE_TYPE_TAGS) + " | domestic | international | unclear |",
              "|---|---|" + "---|" * len(COMPARE_TYPE_TAGS) + "---|---|---|"]
    for label, s in sets.items():
        n = s["n"]
        row = [label, str(n)]
        for t in COMPARE_TYPE_TAGS:
            pct = round(100 * s["tag_counts"].get(t, 0) / n, 1) if n else 0
            row.append(f"{pct}")
        row.append(str(s.get("domestic", 0)))
        row.append(str(s.get("international", 0)))
        row.append(str(s.get("unclear", 0)))
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Referenceとの話題重複候補(機械ヒューリスティック、"
              "Jaccard>=0.3の単語一致のみ、目視推奨。組織的重複は『到達できた』"
              "という肯定的観察であり、Referenceを直接検索した結果ではない"
              "限り問題ではない)",
              f"件数: {len(overlap_hits)}"]
    for h in overlap_hits:
        lines.append(f"- RefProcess「{h['refproc_item']}」 <-> Reference#{h['reference_id']}"
                      f"「{h['reference_topic']}」 jaccard={h['jaccard']}")
    save_json(out_path(out_dir, "comparison_sets_raw.json"),
              {"sets": sets, "overlap_hits": overlap_hits})
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    compute_cost(out_dir)
    print(f"[OK] compare: sets={list(sets.keys())} overlap_hits={len(overlap_hits)}")


# ============================================================
# main
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["search", "cost-check", "gate", "pool", "verify",
                                  "compare", "contamination-check"])
    parser.add_argument("--round", type=int, default=None)
    parser.add_argument("--queries-file", default=None)
    parser.add_argument("--updates-file", default=None)
    parser.add_argument("--context-size", default=None)
    parser.add_argument("--budget-jpy", type=float, default=BUDGET_JPY)
    parser.add_argument("--planned-calls", type=int, default=MAX_SEARCH_CALLS_TOTAL)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    dispatch = {
        "search": cmd_search,
        "cost-check": cmd_cost_check,
        "gate": cmd_gate,
        "pool": cmd_pool,
        "verify": cmd_verify,
        "compare": cmd_compare,
        "contamination-check": cmd_contamination_check,
    }
    dispatch[args.step](args)


if __name__ == "__main__":
    main()
