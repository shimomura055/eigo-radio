# ============================================================
# er016_topic_discovery_angle_integrated_3way_trial_01.py
# TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01 (Fable/ユーザー設計、2026-09-25)
# ============================================================
# 目的: 従来の「検索→Candidate Pool→別callでrerank」ではなく、各モデルに
# Search + Angle Discovery + 追加検索 + Topic Package化 + Selectionを
# **1つのResponses API call(web_searchツール付き、内部の複数tool callは
# 許容)**で行わせる新設計を、Luna/Terra/Solの完全同一条件(同一対象24時間
# 2026-09-18 JST・同一Prompt・同一schema・同一effort medium)で比較する
# Trial。**Production実装ではない。** Production正式path(daily runner・
# er003_*/er012_*等)は一切変更しない。
#
# 設計の核心(委任文より): モデルごとにCandidate Poolを固定して渡す方式に
# しない。各モデル自身がSearch+Angle Discovery+Selectionを1 callで行う。
#
# 費用上限¥200(3-way全体)。実行順: Luna→(実測から Sol/Terra を外挿)→
# Sol→Terra。estimateの時点で超過見込みならLuna実行前にSTOPする。
#
# 再利用: er002_ja_web_research_r3(extract_web_search_usage/extract_sources)、
# er005_cost_logger(install/logging_context)、
# er016_topic_selection_chatgpt_repro_01(_fetch/_extract_published_time/
# _classify_window、公開日時検証のみ)。既存scriptは一切変更しない。
#
# --step: estimate / run(--arm L|S|T) / verify-window / assemble
# 冪等性: raw_response.json等が既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import random
import time
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er005_cost_logger as cl
import er016_topic_selection_chatgpt_repro_01 as repro01

load_dotenv()

THEME_TAG = "TOPIC_DISCOVERY_ANGLE_INTEGRATED_3WAY_TRIAL_01"
JST = timezone(timedelta(hours=9))
UTC = timezone.utc

MODELS = {"L": "gpt-5.6-luna", "S": "gpt-5.6-sol", "T": "gpt-5.6-terra"}
ARM_ORDER = ["L", "S", "T"]  # 実行順(委任文指定): Luna→Sol→Terra
EFFORT = "medium"
BUDGET_JPY = 200.0
USD_TO_JPY = 160
SEARCH_CONTEXT_SIZE = "low"

WINDOW_START_JST = "2026-09-18T00:00:00+09:00"
WINDOW_END_JST = "2026-09-18T23:59:59+09:00"

TEACHER_57_PATH = "docs/pm/topic_selection_user_eval_dataset.json"

# 実測較正値(参考、cost_estimate.jpyで使用):
# TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01の compare_classify call
# (web_search無し、prompts/compare_classify.json)= developer+user合計
# 7498文字 / input_tokens=4375 → 約1.71文字/token(JA中心の混合テキスト)。
CHARS_PER_TOKEN_CALIBRATED = 7498 / 4375

# 同トライアルのsearch call実績(web_search_call_count, jpy)から線形回帰
# (最小二乗、n=20件、web_search_call_count>0の行のみ)で得た「internal
# search 1回あたりの限界費用」(Luna基準)。
#   a(切片)=0.2145 JPY, b(傾き)=1.9678 JPY/search
# (算出根拠: er016_output/topic_selection_reference_process_trial_01/
#  cost.json の by_stage 全21エントリ、Sonnetが本タスクで算出、
#  docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01.md
#  に算出コマンド記録)
REF_PROCESS_MARGINAL_JPY_PER_SEARCH = 1.9678
REF_PROCESS_INTERCEPT_JPY = 0.2145
REF_PROCESS_BASELINE_PROMPT_CHARS = 7498  # 上記compare_classifyのprompt長

ASSUMED_INTERNAL_SEARCH_RANGE = {"low": 20, "mid": 25, "high": 30}

# 実測Sol/Luna費用比(価格比ではなく、同一プロンプトでの実測比、2件):
#  - NEWS-HOOK-MODEL-COMPARISON-01: Sol￥20.41 / Luna￥0.74 = 27.58x
#  - TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01: Sol￥25.2032 /
#    Luna(同一call相当)￥0.908 = 27.75x
# 委任文記載の「Luna比≈6.6倍」はこれらの実測値と一致しないため採用せず、
# 実測2件の平均(より安全側=高い方)を用いる。詳細はcost_estimate.jsonの
# ratio_note、およびRESULT_PACKET_TDに記録する。
EMPIRICAL_SOL_LUNA_RATIO = (27.58 + 27.75) / 2  # 27.665
DELEGATION_STATED_RATIO = 6.6  # 参考記録のみ(不採用)


# ------------------------------------------------------------
# ヘルパー
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
# Teacher Data(Positive/Negative、逐語。委任文本文より1行1件で抽出)
# ------------------------------------------------------------
TEACHER_POSITIVE = [
    "AI開発を遅らせるべきか",
    "欧州反発/Anthropicが実験室",
    "T. rexの体温",
    "日銀金利→住宅ローン・物価・生活",
    "能登地震で滝が770m移動",
    "AIで仕事9割減でも早く帰らない",
    "AIなりすまし面接",
    "米中会談→AIが国家間議題",
    "退職代行会社が続かない理由",
    "日本15歳OECDトップ",
    "詐欺容疑者スマホへの遠隔アクセス",
    "火星サンプル→有人火星・火星移住"
    "(元ニュース「2031年に火星衛星サンプルを地球へ」だけなら弱いが"
    "「月には行けたのに、なぜ火星にはまだ人間が行けない？」"
    "「火星有人着陸・火星移住まであと何が足りない？」まで広げると聞きたい)",
    "AI不正侵入→AI control",
    "DXで逆に負荷増",
    "若者3人に1人結婚意思なし",
    "Trump vs judiciary",
    "日本vsウルグアイもAngle次第",
]

TEACHER_NEGATIVE = [
    "彼岸花",
    "タンチョウ",
    "5G設備共有そのもの"
    "(「携帯4社が5G設備を共同利用」だけなら弱い。"
    "「5G→6Gになると、私たちの生活は何が変わる？」まで広げると可能性)",
    "農家が困る、だけの米価格",
    "一般的な健康ハウツー",
    "芸能人小ネタ",
    "限定スポーツ選手ニュース",
    "普通の混雑・災害続報",
    "教育的すぎる環境話",
]


def load_teacher_57() -> list:
    d = load_json(TEACHER_57_PATH)
    items = list(d["dataset_r"]) + list(d["dataset_a"]) + list(d["dataset_b"])
    return items


def format_teacher_57_block(items: list) -> str:
    lines = []
    for it in items:
        lines.append(
            f"{it['dataset_id']} / {it['topic_ja']} / {it['hook_ja']} / "
            f"score={it['user_score']}"
        )
    return "\n".join(lines)


# ------------------------------------------------------------
# 共通Prompt(3モデル逐語同一。委任文の共通Promptブロックをそのまま使用)
# ------------------------------------------------------------
DEVELOPER_MESSAGE = (
    "You are a topic scout for an English-learning news audio program for "
    "Japanese adult listeners. Your job is not to collect articles. Each "
    "article is only a starting point: find the angle that would make an "
    "ordinary listener want to keep listening."
)

USER_MESSAGE_TEMPLATE = """Target window: news published between 2026-09-18 00:00 and 2026-09-18 23:59 JST. Use web search to explore that day only. If a result is outside that day, do not use it as a seed (you may use it as supporting fact for an angle).

Explore at least two kinds of sources:
1. News lane: big news, Japan, world, economy, daily life, science, tech, AI, and others.
2. Social-signal lane: what people were talking about that day (trending on X, TikTok, share rankings, news reports about social media reactions). Treat social signals as a discovery sensor, not as a source of facts. If a topic starts from a social signal, confirm the facts with reliable news or primary sources.

For each promising seed article, do the following in your own reasoning:
- Identify the core fact of the article.
- Find the connection to ordinary people's lives (work, AI, smartphones, money, mortgages, marriage, alcohol, education, travel, health, daily life).
- Find the natural question that arises (Why? Really? Can that be done? Is it the opposite of what I thought?).
- Expand the story one or two steps into a wider, still concrete topic. Do not expand into a generic educational lesson.
- If the expanded angle needs facts that the seed article does not contain, search for them. Never invent facts.
- Decide whether the result could become an English-learning news audio piece that the listener wants to keep listening to.

This listener has given feedback. Read the examples and infer for yourself what separates the good ones from the weak ones. Do not reduce this to a checklist.

[Listener feedback: topics that worked]
{teacher_user_examples_positive}

[Listener feedback: topics that were weak]
{teacher_user_examples_negative}

[Additional rated examples (1 = would not listen, 10 = would definitely listen)]
{teacher_57}

Drop weak candidates. Then select exactly 10 topic packages. Return JSON only, following the schema. Every seed must have a real URL and its publication date/time. For each package give: seed_title, seed_url, seed_source_name, seed_published_jst, seed_lane ("news" or "social"), core_fact_ja, everyday_connection_ja, natural_question_ja, angle_expansion_ja, extra_search_facts (list of {{fact_ja, url}}, empty if none), final_topic_ja, tentative_title_ja, why_listener_wants_more_ja, and self_note_ja (why you kept it). Also return dropped_candidates: a list of {{seed_title, seed_url, reason_dropped_ja}} for candidates you considered but dropped (at least 5). Write all *_ja fields in Japanese."""


def build_prompt():
    teacher_57_items = load_teacher_57()
    teacher_57_block = format_teacher_57_block(teacher_57_items)
    positive_block = "\n".join(f"- {x}" for x in TEACHER_POSITIVE)
    negative_block = "\n".join(f"- {x}" for x in TEACHER_NEGATIVE)
    user = USER_MESSAGE_TEMPLATE.format(
        teacher_user_examples_positive=positive_block,
        teacher_user_examples_negative=negative_block,
        teacher_57=teacher_57_block,
    )
    return DEVELOPER_MESSAGE, user, teacher_57_items


def prompt_sha256(developer: str, user: str) -> str:
    return hashlib.sha256((developer + "\n" + user).encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# json_schema(strict)。OpenAI strict schemaはminItems/maxItems非対応の
# 既存実績(er016_topic_selection_chatgpt_repro_01._step_a_schema等)に
# 倣い、件数固定はPrompt側の指示("exactly 10" / "at least 5")のみで行う。
# ------------------------------------------------------------
EXTRA_SEARCH_FACT_SCHEMA = {
    "type": "object",
    "properties": {
        "fact_ja": {"type": "string"},
        "url": {"type": ["string", "null"]},
    },
    "required": ["fact_ja", "url"],
    "additionalProperties": False,
}

TOPIC_PACKAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "seed_title": {"type": "string"},
        "seed_url": {"type": "string"},
        "seed_source_name": {"type": "string"},
        "seed_published_jst": {"type": ["string", "null"]},
        "seed_lane": {"type": "string", "enum": ["news", "social"]},
        "core_fact_ja": {"type": "string"},
        "everyday_connection_ja": {"type": "string"},
        "natural_question_ja": {"type": "string"},
        "angle_expansion_ja": {"type": "string"},
        "extra_search_facts": {"type": "array", "items": EXTRA_SEARCH_FACT_SCHEMA},
        "final_topic_ja": {"type": "string"},
        "tentative_title_ja": {"type": "string"},
        "why_listener_wants_more_ja": {"type": "string"},
        "self_note_ja": {"type": "string"},
    },
    "required": [
        "seed_title", "seed_url", "seed_source_name", "seed_published_jst",
        "seed_lane", "core_fact_ja", "everyday_connection_ja",
        "natural_question_ja", "angle_expansion_ja", "extra_search_facts",
        "final_topic_ja", "tentative_title_ja", "why_listener_wants_more_ja",
        "self_note_ja",
    ],
    "additionalProperties": False,
}

DROPPED_CANDIDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "seed_title": {"type": "string"},
        "seed_url": {"type": ["string", "null"]},
        "reason_dropped_ja": {"type": "string"},
    },
    "required": ["seed_title", "seed_url", "reason_dropped_ja"],
    "additionalProperties": False,
}


def build_schema():
    return {
        "name": "topic_discovery_angle_integrated_3way",
        "schema": {
            "type": "object",
            "properties": {
                "topic_packages": {"type": "array", "items": TOPIC_PACKAGE_SCHEMA},
                "dropped_candidates": {"type": "array", "items": DROPPED_CANDIDATE_SCHEMA},
            },
            "required": ["topic_packages", "dropped_candidates"],
            "additionalProperties": False,
        },
        "strict": True,
    }


# ------------------------------------------------------------
# API呼び出し(TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01のcall_model
# パターンを本ファイルのTHEME_TAGで再実装。web_search + search_context_size
# 対応)。1回のみ技術的retryを許可する。
# ------------------------------------------------------------
def call_model(client, developer: str, user: str, schema: dict, model: str,
                stage: str, effort: str = EFFORT,
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
                           effort=effort, context_size=context_size, retried=True)
    if response.model != model:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={model}, actual={response.model})"
        )
    return response


def response_meta(response, developer: str, user: str) -> dict:
    meta = {
        "developer_message": developer,
        "user_message": user,
        "model_requested": response.model,
        "response_model_actual": response.model,
        "response_id": response.id,
    }
    usage = getattr(response, "usage", None)
    if usage is not None:
        out_details = getattr(usage, "output_tokens_details", None)
        meta["usage"] = {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
            "reasoning_tokens": getattr(out_details, "reasoning_tokens", None)
            if out_details is not None else None,
        }
    ws_usage = r3.extract_web_search_usage(response)
    meta["web_search_usage"] = ws_usage
    meta["sources"] = r3.extract_sources(response)
    return meta


# ------------------------------------------------------------
# step: estimate
# ------------------------------------------------------------
def _price(pricing, provider, model, meter):
    try:
        return next(p["price"] for p in pricing
                    if p["provider"] == provider and p["model"] == model
                    and p["meter"] == meter)
    except StopIteration:
        return None


def cmd_estimate(args):
    out_dir = args.out_dir
    budget = args.budget_jpy
    developer, user, teacher_57_items = build_prompt()
    sha = prompt_sha256(developer, user)
    prompt_chars = len(developer) + len(user)
    base_extra_chars = max(prompt_chars - REF_PROCESS_BASELINE_PROMPT_CHARS, 0)
    base_extra_tokens = base_extra_chars / CHARS_PER_TOKEN_CALIBRATED

    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]
    luna_in = _price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_out = _price(pricing, "openai", "gpt-5.6-luna", "output_tokens")
    sol_in = _price(pricing, "openai", "gpt-5.6-sol", "input_tokens")
    sol_out = _price(pricing, "openai", "gpt-5.6-sol", "output_tokens")
    terra_in = _price(pricing, "openai", "gpt-5.6-terra", "input_tokens")

    price_ratio_note = (
        f"pricing_snapshot.json直接比較: Sol/Luna input={sol_in}/{luna_in}="
        f"{round(sol_in / luna_in, 2)}x, output={sol_out}/{luna_out}="
        f"{round(sol_out / luna_out, 2)}x。Terra単価はpricing_snapshot.json"
        f"未収載(terra_in={terra_in})=UNKNOWN。"
        f"実測2件平均比(EMPIRICAL_SOL_LUNA_RATIO)={round(EMPIRICAL_SOL_LUNA_RATIO, 3)}x"
        f"を採用(委任文記載の{DELEGATION_STATED_RATIO}xは実測と不一致のため不採用)。"
        "Terra単価UNKNOWNのため、安全側判定としてSolと同額と仮置きする"
        "(委任文指定)。"
    )

    # 追加の本文サイズ差による入力コスト増分(Luna単価ベース、概算のみ)。
    base_extra_input_cost_luna_jpy = base_extra_tokens / 1_000_000 * luna_in * USD_TO_JPY

    scenarios = {}
    for label, n in ASSUMED_INTERNAL_SEARCH_RANGE.items():
        luna_from_ref_fit = REF_PROCESS_INTERCEPT_JPY + REF_PROCESS_MARGINAL_JPY_PER_SEARCH * n
        luna_est = round(luna_from_ref_fit + base_extra_input_cost_luna_jpy, 2)
        sol_est = round(luna_est * EMPIRICAL_SOL_LUNA_RATIO, 2)
        terra_est = sol_est  # UNKNOWN pricing → Solと同額と仮置き(安全側)
        total_est = round(luna_est + sol_est + terra_est, 2)
        scenarios[label] = {
            "assumed_internal_search_count": n,
            "luna_est_jpy": luna_est,
            "sol_est_jpy": sol_est,
            "terra_est_jpy_placeholder_same_as_sol": terra_est,
            "total_3way_est_jpy": total_est,
            "within_budget": total_est <= budget,
        }

    all_within_budget = all(s["within_budget"] for s in scenarios.values())
    decision = "GO" if all_within_budget else "STOP"

    result = {
        "budget_jpy": budget,
        "prompt_sha256": sha,
        "prompt_chars_developer_plus_user": prompt_chars,
        "reference_process_baseline_prompt_chars": REF_PROCESS_BASELINE_PROMPT_CHARS,
        "base_extra_chars_vs_baseline": base_extra_chars,
        "chars_per_token_calibrated": round(CHARS_PER_TOKEN_CALIBRATED, 4),
        "ref_process_linear_fit": {
            "intercept_jpy": REF_PROCESS_INTERCEPT_JPY,
            "marginal_jpy_per_search": REF_PROCESS_MARGINAL_JPY_PER_SEARCH,
            "source": "er016_output/topic_selection_reference_process_trial_01/"
                      "cost.json (by_stage, n=20 rows with web_search_call_count>0, "
                      "least squares fit computed by Sonnet in this task; command "
                      "recorded in delegation_log)",
        },
        "price_ratio_note": price_ratio_note,
        "empirical_sol_luna_ratio_used": round(EMPIRICAL_SOL_LUNA_RATIO, 3),
        "delegation_stated_ratio_not_used": DELEGATION_STATED_RATIO,
        "scenarios": scenarios,
        "decision": decision,
        "decision_note": (
            "3シナリオ(internal search 20/25/30)すべてでtotal_3way_est_jpyが"
            f"budget_jpy={budget}を超過するため、Sol/Terraはおろか3-way全体が"
            "予算上限内で完了できない見込み。委任文STOP条件『¥200超過見込み』"
            "に該当するため、Luna実行前にSTOPする。"
            if decision == "STOP" else
            "全シナリオでbudget内に収まる見込みのため、Luna実行に進む。"
        ),
        "computed_at_jst": datetime.now(JST).isoformat(),
    }
    save_json(out_path(out_dir, "cost_estimate.json"), result)
    print(f"[{'OK' if decision == 'GO' else 'STOP'}] estimate: decision={decision}")
    for label, s in scenarios.items():
        print(f"  {label}(n={s['assumed_internal_search_count']}): "
              f"Luna=JPY{s['luna_est_jpy']} Sol=JPY{s['sol_est_jpy']} "
              f"Terra(placeholder)=JPY{s['terra_est_jpy_placeholder_same_as_sol']} "
              f"total=JPY{s['total_3way_est_jpy']} within_budget={s['within_budget']}")

    if decision == "STOP":
        stop_reason = {
            "stopped": True,
            "stopped_at_step": "estimate",
            "reason": "cost_estimate.jsonのdecision=STOP(¥200超過見込み)。"
                      "Luna/Sol/Terraいずれも未実行(API課金は0円)。",
            "cost_estimate_summary": {
                label: s["total_3way_est_jpy"] for label, s in scenarios.items()
            },
            "budget_jpy": budget,
            "logged_at_jst": datetime.now(JST).isoformat(),
        }
        save_json(out_path(out_dir, "stop_condition.json"), stop_reason)
        print("[STOP] stop_condition.json を保存しました。API呼び出しは行いません。")


# ------------------------------------------------------------
# step: run --arm {L,S,T}
# ------------------------------------------------------------
def compute_actual_cost_jpy(out_dir: str) -> dict:
    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]

    def model_prices(model_name):
        return (
            _price(pricing, "openai", model_name, "input_tokens"),
            _price(pricing, "openai", model_name, "cached_input_tokens"),
            _price(pricing, "openai", model_name, "output_tokens"),
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
        model_name = e.get("model_id") or MODELS["L"]
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


def cmd_run(args):
    out_dir = args.out_dir
    arm = args.arm
    if arm not in MODELS:
        raise ValueError(f"未知のarm: {arm}(許可: {list(MODELS)})")
    model = MODELS[arm]
    arm_dir = out_path(out_dir, "arms", arm)
    raw_path = out_path(arm_dir, "raw_response.json")
    if skip_if_exists(raw_path, args.force):
        return

    # 予算ガード: これまでの実績costを確認する。cost_estimate.jsonのdecision
    # がSTOPの場合はrunを許可しない(estimateでSTOPしたら本stepは実行禁止)。
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
            f"budget={args.budget_jpy} JPY(arm={arm}実行前)"
        )

    client = get_client()
    developer, user, _ = build_prompt()
    schema = build_schema()
    sha = prompt_sha256(developer, user)
    save_json(out_path(arm_dir, "prompt.json"),
              {"developer": developer, "user": user, "sha256": sha,
               "model_requested": model, "effort": EFFORT,
               "search_context_size": SEARCH_CONTEXT_SIZE})

    stage = f"arm_{arm}"
    t0 = time.time()
    response = call_model(client, developer, user, schema, model, stage)
    elapsed_ms = round((time.time() - t0) * 1000, 1)

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
        t0 = time.time()
        response = call_model(client, developer, user, schema, model, stage + "_retry")
        elapsed_ms = round((time.time() - t0) * 1000, 1)
        parsed = json.loads(response.output_text)

    meta = response_meta(response, developer, user)
    meta["elapsed_ms"] = elapsed_ms
    meta["arm"] = arm

    ws_calls = [item for item in response.output
                if getattr(item, "type", None) == "web_search_call"]
    search_log_lines = [f"# search_log ({arm} / {model})", ""]
    for i, call in enumerate(ws_calls, 1):
        action = getattr(call, "action", None)
        q = None
        if action is not None:
            q = getattr(action, "query", None) or getattr(action, "queries", None)
        search_log_lines.append(f"{i}. {q}")
    save_json(out_path(arm_dir, "raw_response.json"), meta)
    save_json(out_path(arm_dir, "topic_packages.json"), parsed)
    with open(out_path(arm_dir, "search_log.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(search_log_lines) + "\n")
    save_json(out_path(arm_dir, "api_meta.json"), {
        "arm": arm, "model_requested": model,
        "response_model_actual": response.model,
        "usage": meta.get("usage"),
        "web_search_call_count": len(ws_calls),
        "elapsed_ms": elapsed_ms,
    })
    compute_actual_cost_jpy(out_dir)  # 更新のみ(cost.json保存はassembleで実施)
    print(f"[OK] run arm={arm}: model_actual={response.model} "
          f"packages={len(parsed.get('topic_packages', []))} "
          f"ws_calls={len(ws_calls)} elapsed_ms={elapsed_ms}")


# ------------------------------------------------------------
# step: verify-window(公開日時検証。既存verify関数を流用、選定には使わない)
# ------------------------------------------------------------
def cmd_verify_window(args):
    out_dir = args.out_dir
    result = {}
    for arm in ARM_ORDER:
        pkg_path = out_path(out_dir, "arms", arm, "topic_packages.json")
        if not os.path.exists(pkg_path):
            print(f"[SKIP] arm={arm}: topic_packages.jsonなし(未実行)")
            continue
        packages = load_json(pkg_path)["topic_packages"]
        arm_result = []
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
            arm_result.append(entry)
        result[arm] = arm_result
    save_json(out_path(out_dir, "window_compliance.json"), result)
    print(f"[OK] verify-window: arms={list(result.keys())}")


# ------------------------------------------------------------
# step: assemble(重複統合ブラインド一覧・集計資料)
# ------------------------------------------------------------
def _norm_url(u: str) -> str:
    if not u:
        return ""
    return u.split("?")[0].rstrip("/").lower()


def _similar(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a or "", b or "").ratio()


def cmd_assemble(args):
    out_dir = args.out_dir
    all_items = []  # {arm, index, package}
    for arm in ARM_ORDER:
        pkg_path = out_path(out_dir, "arms", arm, "topic_packages.json")
        if not os.path.exists(pkg_path):
            print(f"[SKIP] arm={arm}: topic_packages.jsonなし(未実行のためassembleから除外)")
            continue
        packages = load_json(pkg_path)["topic_packages"]
        for i, pkg in enumerate(packages):
            all_items.append({"arm": arm, "index": i, "package": pkg})

    if not all_items:
        print("[SKIP] assemble: 実行済みarmが0件のため何も生成しません"
              "(STOPのため未実行と想定)。")
        save_json(out_path(out_dir, "assemble_skipped.json"), {
            "reason": "no arm outputs found (likely STOP at estimate step)",
            "checked_at_jst": datetime.now(JST).isoformat(),
        })
        return

    # 重複統合(URL正規化 + タイトル類似度>=0.6)。機械的な一次判定のみ。
    # 最終的な統合判定はSonnet目視によるmerge_log.md追記が必要(委任文指定)。
    groups = []
    used = [False] * len(all_items)
    for i, item in enumerate(all_items):
        if used[i]:
            continue
        group = [item]
        used[i] = True
        url_i = _norm_url(item["package"].get("seed_url"))
        title_i = item["package"].get("seed_title", "")
        for j in range(i + 1, len(all_items)):
            if used[j]:
                continue
            other = all_items[j]
            url_j = _norm_url(other["package"].get("seed_url"))
            title_j = other["package"].get("seed_title", "")
            same_url = bool(url_i) and url_i == url_j
            similar_title = _similar(title_i, title_j) >= 0.6
            if same_url or similar_title:
                group.append(other)
                used[j] = True
        groups.append(group)

    random.seed(42)  # 再現可能なランダム順(内部監査用。ユーザー提示順の乱数種)
    order = list(range(len(groups)))
    random.shuffle(order)

    blind_map = {}
    blind_rows = []
    merge_log_lines = ["# merge_log", "", "機械一次判定(URL正規化一致 または "
                        "difflib類似度>=0.6)。最終統合はSonnet目視。", ""]
    for display_no, gi in enumerate(order, 1):
        group = groups[gi]
        rep = group[0]["package"]
        blind_map[str(display_no)] = {
            "arms": [g["arm"] for g in group],
            "packages": [{"arm": g["arm"], "index": g["index"]} for g in group],
        }
        blind_rows.append({
            "no": display_no,
            "tentative_title_ja": rep.get("tentative_title_ja"),
            "seed_source_and_date": f"{rep.get('seed_source_name')}"
                                     f"({rep.get('seed_published_jst')})",
            "angle_ja": rep.get("angle_expansion_ja"),
            "why_listener_ja": rep.get("why_listener_wants_more_ja"),
        })
        if len(group) > 1:
            arms_str = "/".join(g["arm"] for g in group)
            merge_log_lines.append(
                f"- #{display_no}: arms=[{arms_str}] 統合根拠="
                f"{'URL一致' if _norm_url(group[0]['package'].get('seed_url')) == _norm_url(group[1]['package'].get('seed_url')) else 'タイトル類似'}"
            )

    save_json(out_path(out_dir, "blind_map.json"), blind_map)
    with open(out_path(out_dir, "merge_log.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(merge_log_lines) + "\n")

    md_lines = [
        "# USER_EVAL_TOPIC_DISCOVERY_3WAY",
        "",
        "モデル名・score・self_noteは非表示(ユーザー評価前ブラインド一覧)。",
        "評価: ○(採用したい)/△(どちらとも)/×(採用しない)をコメントで記入してください。",
        "",
        "| # | 仮タイトル | 元ニュース(媒体・日付) | Angle(1〜2段の広げ方) | "
        "なぜ一般人が聞きたくなる可能性があるか | 評価(○/△/×) | コメント |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in blind_rows:
        md_lines.append(
            f"| {row['no']} | {row['tentative_title_ja']} | "
            f"{row['seed_source_and_date']} | {row['angle_ja']} | "
            f"{row['why_listener_ja']} | | |"
        )
    with open("USER_EVAL_TOPIC_DISCOVERY_3WAY.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    # model_overlap.md
    pair_overlap_lines = ["# model_overlap", ""]
    for a1 in ARM_ORDER:
        for a2 in ARM_ORDER:
            if a1 >= a2:
                continue
            both = sum(1 for g in groups if a1 in [x["arm"] for x in g]
                       and a2 in [x["arm"] for x in g])
            pair_overlap_lines.append(f"- {a1}×{a2}: 統合グループ内で両方出現={both}件")
    with open(out_path(out_dir, "model_overlap.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(pair_overlap_lines) + "\n")

    # lane_ratio.md
    lane_lines = ["# lane_ratio", ""]
    for arm in ARM_ORDER:
        items = [x for x in all_items if x["arm"] == arm]
        if not items:
            continue
        news_n = sum(1 for x in items if x["package"].get("seed_lane") == "news")
        social_n = sum(1 for x in items if x["package"].get("seed_lane") == "social")
        extra_n = sum(1 for x in items if x["package"].get("extra_search_facts"))
        lane_lines.append(f"- {arm}: news={news_n} social={social_n} "
                           f"extra_search_facts非空={extra_n}/{len(items)}")
    with open(out_path(out_dir, "lane_ratio.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lane_lines) + "\n")

    # qcd_comparison.md
    qcd_lines = ["# qcd_comparison", "",
                 "| arm | model | total_calls | web_search_calls | input_tokens | "
                 "output_tokens | reasoning_tokens | latency_ms | JPY | "
                 "JPY/package |", "|---|---|---|---|---|---|---|---|---|---|"]
    for arm in ARM_ORDER:
        meta_path = out_path(out_dir, "arms", arm, "api_meta.json")
        if not os.path.exists(meta_path):
            continue
        meta = load_json(meta_path)
        usage = meta.get("usage") or {}
        n_pkg = len([x for x in all_items if x["arm"] == arm])
        qcd_lines.append(
            f"| {arm} | {meta.get('response_model_actual')} | 1 | "
            f"{meta.get('web_search_call_count')} | {usage.get('input_tokens')} | "
            f"{usage.get('output_tokens')} | {usage.get('reasoning_tokens')} | "
            f"{meta.get('elapsed_ms')} | (cost.json参照) | "
            f"(cost.json参照/{n_pkg}件) |"
        )
    with open(out_path(out_dir, "qcd_comparison.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(qcd_lines) + "\n")

    print(f"[OK] assemble: groups={len(groups)} blind_rows={len(blind_rows)}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["estimate", "run", "verify-window", "assemble"])
    parser.add_argument("--arm", choices=list(MODELS.keys()))
    parser.add_argument("--budget-jpy", type=float, default=BUDGET_JPY)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.step == "estimate":
        cmd_estimate(args)
    elif args.step == "run":
        if not args.arm:
            raise ValueError("--step run には --arm が必須です")
        cmd_run(args)
    elif args.step == "verify-window":
        cmd_verify_window(args)
    elif args.step == "assemble":
        cmd_assemble(args)


if __name__ == "__main__":
    main()
