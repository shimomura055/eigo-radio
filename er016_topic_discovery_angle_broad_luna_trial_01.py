# ============================================================
# er016_topic_discovery_angle_broad_luna_trial_01.py
# TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01 (Fable/ユーザー設計、2026-09-25)
# ============================================================
# 目的: TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01と同じOne go方式
# (Search + Angle Discovery + 追加検索 + Topic Package化 + Selectionを
# 1つのResponses API call(web_searchツール付き、内部の複数tool callは
# 許容)で行う)をLuna単独(gpt-5.6-luna)で維持しつつ、前回Trialが
# AI/Techに偏った反省を踏まえ、探索の入口を「なぜ一般人が聞きたくなるか」
# を基準とした読者志向8系統へ明示的に広げるTrial。**Production実装
# ではない。** Production正式path(daily runner・er003_*/er012_*等)は
# 一切変更しない。
#
# 再利用方針(委任文指定): 公開日時HTTP実測(repro01)・web_search usage
# 抽出(r3)・cost logger(cl)・価格lookup(_price)・response_meta・
# prompt_sha256・Teacher57ロード関数は
# er016_topic_discovery_angle_integrated_3way_trial_01.py の実装を
# そのままimportして再利用する(3WAY script自体は一切変更しない)。
# Prompt本文・json_schema・Teacher Positive/Negativeの逐語リストは
# 本script固有(委任文の新Promptに合わせて新規に定義)。
#
# 追加要素(3WAY/前回LUNAトライアルに無い、本委任文固有の設計):
#  (1) max_tool_calls=40(暴走防止ガード。8系統×最低1回+深掘り分)。
#  (2) json_schema strict で topic_packages に minItems=maxItems=10、
#      dropped_candidates に minItems=8 を直接指定する(er003_key_words_
#      production.py の SELECTOR_JSON_SCHEMA で strict=True 併用の実績
#      あり。3WAY scriptのコメントは「非対応」としていたが、production
#      実績で反証されるため今回は委任文指定どおりminItems/maxItemsを使う。
#      Sonnetが本タスクで確認した既存実績のみに基づく判断であり、新規の
#      仕様判断・Production変更ではない)。
#  (3) --step check: 機械的にa)10件ちょうどb)seed_url重複なしc)JST窓内
#      (文字列判定のみ。HTTP実測は--step verify-windowで別途行う)d)8系統
#      カバレッジ(search_log.mdのqueryをヒューリスティックでcategory
#      1-8へ機械的に仮タグ付けし、各系統が最低1回ヒットしているかを見る。
#      最終的な系統対応付けの確定はSonnetがREPORT §4で目視再確認する)
#      を検証し、違反があれば同一条件で1回だけ追加callする(attempts/
#      attempt_2/)。2回目も違反が残る場合は追加callせず、STOPとして事実を
#      記録する(委任文のSTOP条件参照)。
#
# 費用上限¥100(暴走防止。前回実費¥4.62、max_tool_calls=30/ws_calls=8)。
# 1 callは途中停止できないため、実測が¥100を超えた場合は事実として報告する
# (checkでの再callも含め、追加callは1回までに制限)。
#
# --step: estimate / run / check / verify-window / assemble
# 冪等性: attempts/attempt_1/raw_response.json等が既に存在する場合、
# --forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import time
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

import er005_cost_logger as cl
import er016_topic_discovery_angle_integrated_3way_trial_01 as trial3way

load_dotenv()

THEME_TAG = "TOPIC_DISCOVERY_ANGLE_BROAD_LUNA_TRIAL_01"
JST = timezone(timedelta(hours=9))

MODEL_LUNA = trial3way.MODELS["L"]  # "gpt-5.6-luna"
EFFORT = trial3way.EFFORT  # "medium"
SEARCH_CONTEXT_SIZE = trial3way.SEARCH_CONTEXT_SIZE  # "low"
USD_TO_JPY = trial3way.USD_TO_JPY
BUDGET_JPY = 100.0
MAX_TOOL_CALLS_DEFAULT = 40  # 委任文指定(8系統×最低1回+深掘り分のガード)

WINDOW_START_JST = trial3way.WINDOW_START_JST  # "2026-09-18T00:00:00+09:00"
WINDOW_END_JST = trial3way.WINDOW_END_JST      # "2026-09-18T23:59:59+09:00"
ASSUMED_INTERNAL_SEARCH_RANGE = trial3way.ASSUMED_INTERNAL_SEARCH_RANGE

PREV_TRIAL_ACTUAL_JPY = 4.62  # TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01実績(比較用)
PREV_TRIAL_WS_CALLS = 8
PREV_TRIAL_MAX_TOOL_CALLS = 30

CATEGORY_LABELS = {
    1: "生活直結(仕事/お金/住宅ローン/物価/AI導入/スマホ/教育/結婚/健康/旅行)",
    2: "常識逆転(「え、そうなの？」)",
    3: "未来変化(AI/宇宙/6G/ロボット/医療/新技術/働き方)",
    4: "BigNews自分事化(米中/日銀/Trump/国際政治/大きな経済ニュース)",
    5: "社会変化・人の行動(結婚/若者/仕事観/消費行動/SNS/働き方/世代差)",
    6: "SNS・話題先行の軽い入口(X/TikTok/急上昇/Shareランキング/バズ)",
    7: "科学・身体・自然の不思議(恐竜/宇宙/脳/地形/身体/生物)",
    8: "エンタメ・スポーツ(広い知名度/大きな共有イベント限定)",
}


# ------------------------------------------------------------
# ヘルパー(3WAY/前回LUNAスクリプトと同一パターン)
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
# Teacher Data(Positive/Negative、逐語。委任文本文より1行1件で抽出。
# 「X → A / B / C」形式は1件として扱う=前回LUNAトライアル・3WAY script
# のTEACHER_POSITIVE/NEGATIVEと同じ抽出方針)
# ------------------------------------------------------------
TEACHER_POSITIVE = [
    "AI開発減速 vs 欧州反発",
    "Anthropic実験室",
    "T. rex体温",
    "日銀金利 → 住宅ローン / 輸入品 / 生活",
    "能登地震で滝が移動",
    "AIで仕事9割減でも早く帰れない",
    "AIなりすまし面接",
    "退職代行会社が続かない理由",
    "日本15歳OECDトップ",
    "特殊詐欺スマホ遠隔アクセス",
    "火星サンプル → 火星有人 / 移住",
    "AI不正侵入 → AI control",
    "DXで負荷増",
    "若者の結婚意思",
    "Trump vs judiciary",
    "日本 vs ウルグアイもAngle次第",
]

TEACHER_NEGATIVE = [
    "彼岸花",
    "タンチョウ",
    "5G設備共有そのもの",
    "農家が困るだけの米価格",
    "一般健康ハウツー",
    "普通の災害続報",
    "限定芸能ネタ",
    "限定スポーツネタ",
    "教育的すぎる環境話",
]


def load_teacher_57() -> list:
    return trial3way.load_teacher_57()


def format_teacher_57_block(items: list) -> str:
    return trial3way.format_teacher_57_block(items)


# ------------------------------------------------------------
# 共通Prompt(委任文の逐語Promptをそのまま使用。{positive}/{negative}/
# {teacher_57}のみ差し込む)
# ------------------------------------------------------------
DEVELOPER_MESSAGE = (
    "You are a topic scout for an English-learning news audio program for "
    "Japanese adult listeners. Your job is not to collect articles. Each "
    "article is only a starting point: find the angle that would make an "
    "ordinary listener want to keep listening."
)

USER_MESSAGE_TEMPLATE = """Target window: news published between 2026-09-18 00:00 and 2026-09-18 23:59 Japan Standard Time (JST, UTC+9). Convert every publication time to JST before deciding. An article published on 18 September in US time that falls on 19 September in JST is OUTSIDE the window and must not be used as a seed. You may use out-of-window articles only as supporting facts for an angle. Record the JST publication time for every seed.

Explore by "why would an ordinary listener want to hear this", not by media genre. Search each of the following eight categories at least once before you go deeper anywhere. Do not concentrate on one category (for example AI or tech) before you have looked at all eight.
1. Directly connected to my life and work: work, money, mortgages, prices, AI adoption at work, smartphones, education, marriage, health, travel.
2. "Wait, really?" — common sense turned upside down: gaps between what people believe and reality, surprising research results, things that turn out to be the opposite.
3. How the future will change: AI, space, 6G, robots, medicine, new technology, ways of working — not the tech news itself, but what changes for ordinary people.
4. Big news made personal: US–China, the Bank of Japan, Trump, international politics, big economic news — only if it can be connected to daily life, AI, money, freedom, or work.
5. Social change and human behaviour: marriage, young people, attitudes to work, consumer behaviour, social media, ways of working, generation gaps.
6. Social buzz as a light entry point: trending on X, TikTok, share rankings, viral topics. Treat social media as a discovery sensor, never as a source of facts. Confirm facts with primary sources or reliable news.
7. Wonders of science, the body and nature: dinosaurs, space, the brain, landforms, the body, living things — prefer surprise, a connection to the listener, or a gap with common sense over an educational explanation.
8. Entertainment and sports: usually too narrow. Keep only if the subject has very wide name recognition (Ohtani-level), it is a very big shared event (World Cup-level), or it opens naturally into a general theme. Minor celebrity news and single-team or single-player news are low priority.

Include both news sources and social-signal sources. Include Japanese-language sources as well as English ones.

For each promising seed article, do the following in your own reasoning:
- Identify the core fact of the article.
- Find the connection to ordinary people's lives.
- Find the curiosity gap (Why? Really? Can that be done? Is it the opposite of what I thought?).
- Expand the story one or two steps into a wider, still concrete topic. Do not expand into a generic educational lesson.
- If the expanded angle needs facts that the seed article does not contain, search for them. Never invent facts.
- Decide whether the result could become an English-learning news audio piece that the listener wants to keep listening to.

This listener has given feedback. Read the examples and infer for yourself what separates the good ones from the weak ones. Do not reduce this to a checklist.

[Listener feedback: topics that worked]
{positive}

[Listener feedback: topics that were weak]
{negative}

[Additional rated examples (1 = would not listen, 10 = would definitely listen)]
{teacher_57}

Select exactly 10 topic packages. Each package must come from a different seed article; do not keep two angles from the same seed. Return JSON only, following the schema. For each package give: seed_title, seed_url, seed_source_name, seed_published_jst, seed_lane ("news" or "social"), category (1–8 from the list above), core_fact_ja, everyday_connection_ja, curiosity_gap_ja, angle_expansion_ja, extra_search_facts (list of {{fact_ja, url}}, empty if none), final_topic_ja, tentative_title_ja, why_selected_ja. Also return dropped_candidates: a list of {{seed_title, seed_url, category, reason_dropped_ja}} (at least 8, covering more than one category). Write all *_ja fields in Japanese."""


def build_prompt():
    teacher_57_items = load_teacher_57()
    teacher_57_block = format_teacher_57_block(teacher_57_items)
    positive_block = "\n".join(f"- {x}" for x in TEACHER_POSITIVE)
    negative_block = "\n".join(f"- {x}" for x in TEACHER_NEGATIVE)
    user = USER_MESSAGE_TEMPLATE.format(
        positive=positive_block,
        negative=negative_block,
        teacher_57=teacher_57_block,
    )
    return DEVELOPER_MESSAGE, user, teacher_57_items


def prompt_sha256(developer: str, user: str) -> str:
    return hashlib.sha256((developer + "\n" + user).encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# json_schema(strict)。委任文指定どおり topic_packages に
# minItems=maxItems=10、dropped_candidates に minItems=8、
# category は integer enum 1-8 を直接指定する(er003_key_words_
# production.py SELECTOR_JSON_SCHEMA でのstrict+minItems/maxItems併用の
# 既存production実績に基づく)。
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

CATEGORY_SCHEMA = {"type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7, 8]}

TOPIC_PACKAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "seed_title": {"type": "string"},
        "seed_url": {"type": "string"},
        "seed_source_name": {"type": "string"},
        "seed_published_jst": {"type": ["string", "null"]},
        "seed_lane": {"type": "string", "enum": ["news", "social"]},
        "category": CATEGORY_SCHEMA,
        "core_fact_ja": {"type": "string"},
        "everyday_connection_ja": {"type": "string"},
        "curiosity_gap_ja": {"type": "string"},
        "angle_expansion_ja": {"type": "string"},
        "extra_search_facts": {"type": "array", "items": EXTRA_SEARCH_FACT_SCHEMA},
        "final_topic_ja": {"type": "string"},
        "tentative_title_ja": {"type": "string"},
        "why_selected_ja": {"type": "string"},
    },
    "required": [
        "seed_title", "seed_url", "seed_source_name", "seed_published_jst",
        "seed_lane", "category", "core_fact_ja", "everyday_connection_ja",
        "curiosity_gap_ja", "angle_expansion_ja", "extra_search_facts",
        "final_topic_ja", "tentative_title_ja", "why_selected_ja",
    ],
    "additionalProperties": False,
}

DROPPED_CANDIDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "seed_title": {"type": "string"},
        "seed_url": {"type": ["string", "null"]},
        "category": CATEGORY_SCHEMA,
        "reason_dropped_ja": {"type": "string"},
    },
    "required": ["seed_title", "seed_url", "category", "reason_dropped_ja"],
    "additionalProperties": False,
}


def build_schema():
    return {
        "name": "topic_discovery_angle_broad_luna",
        "schema": {
            "type": "object",
            "properties": {
                "topic_packages": {
                    "type": "array",
                    "minItems": 10,
                    "maxItems": 10,
                    "items": TOPIC_PACKAGE_SCHEMA,
                },
                "dropped_candidates": {
                    "type": "array",
                    "minItems": 8,
                    "items": DROPPED_CANDIDATE_SCHEMA,
                },
            },
            "required": ["topic_packages", "dropped_candidates"],
            "additionalProperties": False,
        },
        "strict": True,
    }


# ------------------------------------------------------------
# step: estimate(前回実績[LUNA-TRIAL-01, ¥4.62, max_tool_calls=30,
# ws_calls=8]をベースに、今回max_tool_calls=40への引き上げとPrompt文字数
# 差分を加味した線形fit概算。3WAY scriptの同一fit式を再利用)
# ------------------------------------------------------------
def cmd_estimate(args):
    out_dir = args.out_dir
    budget = args.budget_jpy
    developer, user, _ = build_prompt()
    sha = prompt_sha256(developer, user)
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

    # check step が1回追加callする可能性があるため、最悪ケース(2 call合計)も
    # 別途計算して記録する(暴走防止上限¥100との比較用。GO/STOP判定自体は
    # 1 call分のシナリオで行う。委任文は「実行前概算で¥100超ならSTOP」であり
    # checkでの追加callはSTOP条件を満たした場合の事後対応のため)。
    worst_case_2calls = {
        label: round(s["luna_est_jpy"] * 2, 2) for label, s in scenarios.items()
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
            "source": "3WAY trial / 前回LUNA-TRIAL-01のcost_estimate.jsonと同一の"
                      "最小二乗fit(er016_output/topic_selection_reference_process_"
                      "trial_01/cost.json由来)を再利用。本scriptでの再計算はしていない。",
        },
        "prev_trial_actual": {
            "management_id": "TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01",
            "actual_jpy": PREV_TRIAL_ACTUAL_JPY,
            "max_tool_calls": PREV_TRIAL_MAX_TOOL_CALLS,
            "web_search_call_count": PREV_TRIAL_WS_CALLS,
            "note": "前回実績を参考値として記録(今回はmax_tool_calls=40・"
                    "Prompt文字数が異なるため、そのままの外挿ではなく別途"
                    "線形fitで再計算している)。",
        },
        "note": "8系統探索によりweb_search呼び出し回数が前回(8回)より増える"
                "可能性があるため、ASSUMED_INTERNAL_SEARCH_RANGE(20/25/30)の"
                "シナリオで判定する。",
        "scenarios": scenarios,
        "worst_case_2calls_jpy_if_check_retries_once": worst_case_2calls,
        "decision": decision,
        "decision_note": (
            f"internal search 20/25/30のいずれかのシナリオでluna_est_jpyが"
            f"budget_jpy={budget}を超過するため、Luna実行前にSTOPする。"
            if decision == "STOP" else
            "全シナリオでbudget内に収まる見込みのため、Luna実行に進む"
            "(checkでの追加1 callまで含めても2call合計の最悪ケースは"
            f"{max(worst_case_2calls.values())}JPY)。"
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
# API呼び出し(3WAY/前回LUNAスクリプトと同一パターン + max_tool_calls)
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
# 実測費用集計(3WAY/前回LUNAスクリプトと同一ロジック、THEME_TAGのみ本
# script用に変更。attempt_1/attempt_2どちらのcallも同一THEME_TAGでログ
# されるため、累計費用として自動的に合算される)
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
    by_stage = {}
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
        stage = e.get("stage") or "unknown"
        s_entry = by_stage.setdefault(stage, {"calls": 0, "jpy": 0.0})
        s_entry["calls"] += 1
        s_entry["jpy"] += jpy

    for entry in by_model.values():
        if isinstance(entry.get("jpy"), float):
            entry["jpy"] = round(entry["jpy"], 4)
    for entry in by_stage.values():
        entry["jpy"] = round(entry["jpy"], 4)

    return {"total_jpy_known_models_only": round(total_jpy, 2),
            "by_model": by_model, "by_stage": by_stage}


# ------------------------------------------------------------
# 1回分のAPI呼び出し実行(attempt_1 / attempt_2 共通処理)
# ------------------------------------------------------------
def _run_one_attempt(client, out_dir: str, attempt_name: str, developer: str,
                      user: str, schema: dict, max_tool_calls: int) -> dict:
    attempt_dir = out_path(out_dir, "attempts", attempt_name)
    raw_path = out_path(attempt_dir, "raw_response.json")

    stage = f"luna_{attempt_name}"
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
        print(f"[RETRY] {stage}: 空出力/schema不一致のため同一条件で1回のみ再実行"
              "(技術的retry。委任文のcontent-violation再実行とは別)")
        retried_flag = True
        t0 = time.time()
        response = call_model(client, developer, user, schema, MODEL_LUNA,
                               stage + "_techretry", max_tool_calls)
        elapsed_ms = round((time.time() - t0) * 1000, 1)
        parsed = json.loads(response.output_text)

    meta = trial3way.response_meta(response, developer, user)
    meta["elapsed_ms"] = elapsed_ms
    meta["max_tool_calls"] = max_tool_calls
    meta["technical_schema_retry_occurred"] = retried_flag

    ws_calls = [item for item in response.output
                if getattr(item, "type", None) == "web_search_call"]
    # NOTE(バグ修正): 当初はweb_search_callアイテムごとに action.query/queries を
    # 1件だけ拾っていたが、実際には1つのweb_search_callアイテムに複数の
    # queryが action.queries(複数形)としてまとめて入る場合がある
    # (er002_ja_web_research_r3.extract_web_search_usage の実装と同じ
    # パターン)。meta["web_search_usage"]["queries"]は同関数で正しく
    # 展開済みの全query文字列リストのため、こちらを正とする
    # (web_search_call_count=ws_calls件数はツールcall単位の件数として
    # 別途維持し、8系統カバレッジ判定にはqueries全件を使う)。
    query_list = meta.get("web_search_usage", {}).get("queries", [])
    search_log_lines = [
        f"# search_log ({attempt_name} / Luna / {MODEL_LUNA})",
        "",
        f"web_search_call_count(ツールcall件数)={len(ws_calls)} / "
        f"query件数(1 callに複数queryが含まれる場合あり)={len(query_list)}",
        "",
    ]
    for i, q in enumerate(query_list, 1):
        search_log_lines.append(f"{i}. {q}")

    save_json(raw_path, meta)
    save_json(out_path(attempt_dir, "topic_packages.json"), parsed)
    with open(out_path(attempt_dir, "search_log.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(search_log_lines) + "\n")
    api_meta = {
        "attempt": attempt_name,
        "model_requested": MODEL_LUNA,
        "response_model_actual": response.model,
        "usage": meta.get("usage"),
        "web_search_call_count": len(ws_calls),
        "elapsed_ms": elapsed_ms,
        "max_tool_calls": max_tool_calls,
        "technical_schema_retry_occurred": retried_flag,
        "query_list": query_list,
    }
    save_json(out_path(attempt_dir, "api_meta.json"), api_meta)
    print(f"[OK] {attempt_name}: model_actual={response.model} "
          f"packages={len(parsed.get('topic_packages', []))} "
          f"ws_calls={len(ws_calls)} elapsed_ms={elapsed_ms}")
    return {"attempt_dir": attempt_dir, "parsed": parsed, "api_meta": api_meta,
            "search_log_lines": search_log_lines, "query_list": query_list}


def _adopt_attempt(out_dir: str, attempt_result: dict) -> None:
    """attempt_dirの内容をout_dir直下へコピーし、verify-window/assembleが
    従来どおりout_dir直下のファイルを読めるようにする。"""
    attempt_dir = attempt_result["attempt_dir"]
    save_json(out_path(out_dir, "topic_packages.json"), attempt_result["parsed"])
    save_json(out_path(out_dir, "api_meta.json"), attempt_result["api_meta"])
    with open(out_path(attempt_dir, "search_log.md"), encoding="utf-8") as f:
        search_log_text = f.read()
    with open(out_path(out_dir, "search_log.md"), "w", encoding="utf-8") as f:
        f.write(search_log_text)
    with open(out_path(attempt_dir, "raw_response.json"), encoding="utf-8") as f:
        raw_meta = json.load(f)
    save_json(out_path(out_dir, "raw_response.json"), raw_meta)


# ------------------------------------------------------------
# step: run(attempt_1のみ実行。content-violation再実行はcheckで行う)
# ------------------------------------------------------------
def cmd_run(args):
    out_dir = args.out_dir
    attempt1_pkg_path = out_path(out_dir, "attempts", "attempt_1", "topic_packages.json")
    if skip_if_exists(attempt1_pkg_path, args.force):
        # 既存attempt_1をout_dir直下へ採用済みでなければ採用する
        if not os.path.exists(out_path(out_dir, "topic_packages.json")):
            parsed = load_json(attempt1_pkg_path)
            api_meta = load_json(out_path(out_dir, "attempts", "attempt_1", "api_meta.json"))
            _adopt_attempt(out_dir, {
                "attempt_dir": out_path(out_dir, "attempts", "attempt_1"),
                "parsed": parsed, "api_meta": api_meta,
            })
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
    developer, user, _ = build_prompt()
    schema = build_schema()
    sha = prompt_sha256(developer, user)
    max_tool_calls = args.max_tool_calls
    save_json(out_path(out_dir, "prompt.json"), {
        "developer": developer, "user": user, "sha256": sha,
        "model_requested": MODEL_LUNA, "effort": EFFORT,
        "search_context_size": SEARCH_CONTEXT_SIZE,
        "max_tool_calls": max_tool_calls,
    })

    result = _run_one_attempt(client, out_dir, "attempt_1", developer, user,
                               schema, max_tool_calls)
    _adopt_attempt(out_dir, result)

    actual_cost = compute_actual_cost_jpy(out_dir)
    save_json(out_path(out_dir, "cost.json"), actual_cost)
    over_budget = actual_cost["total_jpy_known_models_only"] > args.budget_jpy
    print(f"[OK] run(attempt_1採用): actual_jpy_cumulative="
          f"{actual_cost['total_jpy_known_models_only']} over_budget={over_budget}")
    if over_budget:
        print(f"[NOTE] 実測費用が budget_jpy={args.budget_jpy} を超過しました"
              "(1 callは途中停止不可のため事実として報告)。")


# ------------------------------------------------------------
# 機械チェック本体(check step / 再実行判定の両方で使う共通ロジック)
# ------------------------------------------------------------
def _norm_url(u: str) -> str:
    return trial3way._norm_url(u)


CATEGORY_KEYWORDS = {
    1: ["住宅ローン", "mortgage", "物価", "price", "prices", "家計", "仕事", "work",
        "給料", "salary", "教育", "education", "結婚", "marriage", "健康",
        "health", "旅行", "travel", "スマホ", "smartphone", "iphone",
        "adoption"],
    2: ["常識", "意外", "驚き", "本当に", "really", "surprising", "gap", "誤解",
        "逆転"],
    3: ["未来", "future", "6g", "ロボット", "robot", "医療", "medicine", "新技術",
        "technology", "働き方", "宇宙", "space", " ai ", "\"ai\"", "ai agent",
        "aiエージェント"],
    4: ["米中", "us-china", "日銀", "boj", "bank of japan", "trump", "政治",
        "politics", "経済", "economy", "国際"],
    5: ["若者", "young", "世代", "generation", "消費", "consumer", "sns",
        "働き方", "結婚", "marriage"],
    6: ["site:x.com", "twitter", "tiktok", "トレンド", "trending", "バズ",
        "viral", "share ranking", "話題", "sns"],
    7: ["恐竜", "dinosaur", "宇宙", "space", "脳", "brain", "地形", "landform",
        "身体", "body", "生物", "study", "研究", "science", "科学"],
    8: ["スポーツ", "sports", "芸能", "celebrity", "world cup", "ワールドカップ",
        "大谷", "ohtani"],
}


def classify_query_categories(query_text) -> set:
    """ヒューリスティック機械タグ付け(概算のみ)。短い曖昧トークン(例: 単独
    の"ai")による過検出を避けるため、英数字キーワードは単語境界つき正規表現、
    日本語キーワードは部分一致で判定する。最終的な系統対応付けの確定は
    REPORT §4でSonnetが実際のquery文字列を目視して行う(本関数はcheck
    step の自動再実行トリガー用の一次判定に過ぎない)。"""
    if not query_text:
        return set()
    text = str(query_text).lower()
    hits = set()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            kw_l = kw.lower().strip()
            if not kw_l:
                continue
            if kw_l.isascii() and kw_l.replace(" ", "").isalnum():
                if re.search(rf"(?<![a-z0-9]){re.escape(kw_l)}(?![a-z0-9])", text):
                    hits.add(cat)
                    break
            else:
                if kw_l in text:
                    hits.add(cat)
                    break
    return hits


def _window_string_ok(seed_published_jst) -> str:
    """文字列判定のみ(HTTP実測はverify-windowで別途)。
    'within' / 'outside' / 'unknown' を返す。"""
    if not seed_published_jst:
        return "unknown"
    s = str(seed_published_jst)
    if "2026-09-18" in s:
        return "within"
    if "2026-09-17" in s or "2026-09-19" in s:
        return "outside"
    return "unknown"


def compute_check(packages: list, query_list: list) -> dict:
    violations = []

    n = len(packages)
    if n != 10:
        violations.append({"type": "count_not_10", "detail": f"n={n}"})

    urls = [_norm_url(p.get("seed_url")) for p in packages]
    seen = {}
    dup_details = []
    for i, u in enumerate(urls):
        if not u:
            continue
        if u in seen:
            dup_details.append({"url": u, "indices": [seen[u], i]})
        else:
            seen[u] = i
    if dup_details:
        violations.append({"type": "duplicate_seed_url", "detail": dup_details})

    window_results = [
        {"seed_title": p.get("seed_title"), "seed_published_jst": p.get("seed_published_jst"),
         "classification": _window_string_ok(p.get("seed_published_jst"))}
        for p in packages
    ]
    outside = [w for w in window_results if w["classification"] == "outside"]
    if outside:
        violations.append({"type": "window_violation_string", "detail": outside})

    category_hits = {c: [] for c in range(1, 9)}
    for q in query_list:
        for c in classify_query_categories(q):
            category_hits[c].append(q)
    missing_categories = [c for c in range(1, 9) if not category_hits[c]]
    if missing_categories:
        violations.append({"type": "category_coverage_missing",
                            "detail": missing_categories})

    category_distribution = {}
    for p in packages:
        c = p.get("category")
        category_distribution[str(c)] = category_distribution.get(str(c), 0) + 1

    return {
        "n_packages": n,
        "duplicate_seed_urls": dup_details,
        "window_results_string_based": window_results,
        "category_query_coverage": {str(c): len(v) for c, v in category_hits.items()},
        "category_query_hits_detail": {str(c): v for c, v in category_hits.items()},
        "final_package_category_distribution": category_distribution,
        "violations": violations,
        "status": "PASS" if not violations else "VIOLATIONS_FOUND",
    }


def _load_query_list(out_dir: str, attempt_name: str) -> list:
    """raw_response.json(trial3way.response_metaが保存する
    web_search_usage.queries、1 web_search_callに複数queryが含まれる
    ケースを正しく展開済み)を正として読む。存在しない場合のみ
    api_meta.json の query_list(旧バグ版と同じ形。後方互換用)へ
    fallbackする。"""
    raw_path = out_path(out_dir, "attempts", attempt_name, "raw_response.json")
    if os.path.exists(raw_path):
        raw_meta = load_json(raw_path)
        queries = (raw_meta.get("web_search_usage") or {}).get("queries")
        if queries is not None:
            return queries
    meta_path = out_path(out_dir, "attempts", attempt_name, "api_meta.json")
    if os.path.exists(meta_path):
        return load_json(meta_path).get("query_list", [])
    return []


# ------------------------------------------------------------
# step: check(機械チェック。違反があれば同一条件で1回だけattempt_2を実行)
# ------------------------------------------------------------
def cmd_check(args):
    out_dir = args.out_dir
    attempt1_pkg_path = out_path(out_dir, "attempts", "attempt_1", "topic_packages.json")
    if not os.path.exists(attempt1_pkg_path):
        print("[SKIP] check: attempts/attempt_1/topic_packages.jsonなし(未実行)")
        save_json(out_path(out_dir, "check_result.json"), {
            "reason": "attempt_1 topic_packages.json not found (likely STOP at estimate step)",
        })
        return

    # 安全装置: check_result.jsonが既にretried=trueで保存済みなら、
    # --forceの有無にかかわらずAPIを一切呼ばず、既存attempt_1/attempt_2の
    # データのみで再計算する(委任文の「1回だけ再実行」上限を、operatorの
    # フラグ指定ミスからも構造的に守るため。2026-09-25、本スクリプトの
    # 開発中に--forceがcheck stepの意図しない3回目の実call を誘発した
    # バグの再発防止として追加)。
    existing_check_path = out_path(out_dir, "check_result.json")
    retry_already_used = False
    if os.path.exists(existing_check_path):
        existing_check = load_json(existing_check_path)
        retry_already_used = bool(existing_check.get("retried"))

    query_list_1 = _load_query_list(out_dir, "attempt_1")
    packages_1 = load_json(attempt1_pkg_path)["topic_packages"]
    check_1 = compute_check(packages_1, query_list_1)

    result = {
        "attempt_1": check_1,
        "retried": False,
        "adopted_attempt": "attempt_1",
        "final_status": check_1["status"],
    }

    retry_marker = out_path(out_dir, "attempts", "attempt_2", "topic_packages.json")
    if check_1["status"] != "PASS":
        if os.path.exists(retry_marker) or retry_already_used:
            print("[SKIP] attempt_2は既に存在する、または再実行枠を使用済みです"
                  "(--forceであってもAPIは呼びません)。既存データのみで再判定します。")
            if not os.path.exists(retry_marker):
                raise SystemExit(
                    "STOP: retried=trueが記録済みだがattempts/attempt_2/"
                    "topic_packages.jsonが存在しません(不整合)。手動確認が必要です。"
                )
            packages_2 = load_json(retry_marker)["topic_packages"]
            attempt2_meta = load_json(out_path(out_dir, "attempts", "attempt_2", "api_meta.json"))
            query_list_2 = _load_query_list(out_dir, "attempt_2")
            check_2 = compute_check(packages_2, query_list_2)
            _adopt_attempt(out_dir, {
                "attempt_dir": out_path(out_dir, "attempts", "attempt_2"),
                "parsed": {"topic_packages": packages_2,
                           "dropped_candidates": load_json(retry_marker).get("dropped_candidates", [])},
                "api_meta": attempt2_meta,
            })
        else:
            print("[RETRY] check: 機械チェックで違反を検出したため、同一条件で1回だけ"
                  "attempt_2を実行します(委任文STOP条件の再実行ルール)。")
            install_logger(out_dir)
            client = get_client()
            developer, user, _ = build_prompt()
            schema = build_schema()
            max_tool_calls = args.max_tool_calls
            attempt2_result = _run_one_attempt(client, out_dir, "attempt_2", developer,
                                                user, schema, max_tool_calls)
            _adopt_attempt(out_dir, attempt2_result)
            packages_2 = attempt2_result["parsed"]["topic_packages"]
            query_list_2 = attempt2_result["query_list"]
            check_2 = compute_check(packages_2, query_list_2)

        result["attempt_2"] = check_2
        result["retried"] = True
        result["adopted_attempt"] = "attempt_2"
        result["final_status"] = check_2["status"]
        if check_2["status"] != "PASS":
            result["stop_reason"] = (
                "1回の再実行後も機械チェック違反が残存。委任文の指示により"
                "追加の再実行は行わず、事実として報告しSTOP扱いとする。"
                "attempt_2の出力を最終採用(直近の結果)として全成果物を生成する。"
            )
            print("[STOP] check: attempt_2でも違反が残存。追加callは行わず"
                  "STOP扱いとして事実を記録します。")
        else:
            print("[OK] check: attempt_2で違反が解消しました(採用: attempt_2)。")
    else:
        print("[OK] check: attempt_1で違反なし(採用: attempt_1)。")

    actual_cost = compute_actual_cost_jpy(out_dir)
    save_json(out_path(out_dir, "cost.json"), actual_cost)
    result["cumulative_cost_jpy"] = actual_cost["total_jpy_known_models_only"]
    save_json(out_path(out_dir, "check_result.json"), result)
    print(f"[{'OK' if result['final_status'] == 'PASS' else 'STOP'}] check: "
          f"final_status={result['final_status']} retried={result['retried']} "
          f"cumulative_jpy={result['cumulative_cost_jpy']}")


# ------------------------------------------------------------
# step: verify-window(公開日時HTTP実測。checkの文字列判定とは別、参考情報。
# 既存repro01関数を3WAY module経由で流用、選定には使わない)
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
        entry = {"seed_title": pkg.get("seed_title"), "seed_url": url,
                  "seed_published_jst_reported": pkg.get("seed_published_jst")}
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
# step: assemble(ユーザー評価一覧・落選候補・系統分布・QCD)
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
    blind_map_compat = {}
    rows = []
    for display_no, idx in enumerate(order, 1):
        pkg = packages[idx]
        eval_map[str(display_no)] = {"index": idx, "category": pkg.get("category")}
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
            "curiosity_gap_ja": pkg.get("curiosity_gap_ja"),
            "angle_expansion_ja": pkg.get("angle_expansion_ja"),
            "extra_search_facts_ja": "; ".join(
                f"{x.get('fact_ja')}({x.get('url')})"
                for x in (pkg.get("extra_search_facts") or [])
            ) or "(なし)",
        })
    save_json(out_path(out_dir, "eval_map.json"), eval_map)
    save_json(out_path(out_dir, "blind_map.json"), blind_map_compat)

    md_lines = [
        "# USER_EVAL_TOPIC_DISCOVERY_BROAD",
        "",
        f"TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01。Luna単独実行の"
        f"Topic Package {len(packages)}件(schemaでminItems=maxItems=10を強制)。"
        f"内部評価(why_selected_ja・category)は非表示。",
        "評価: ○(採用したい)/△(どちらとも)/×(採用しない)をコメントで記入してください。",
        "",
        "| # | 仮タイトル | 元ニュース(媒体・JST日時・URL) | 事実の核 | "
        "一般人との接点 | Curiosity gap | Angle(1〜2段) | 追加検索した事実 | "
        "評価(○/△/×) | コメント |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        md_lines.append(
            f"| {row['no']} | {row['tentative_title_ja']} | "
            f"{row['seed_source_date_url']} | {row['core_fact_ja']} | "
            f"{row['everyday_connection_ja']} | {row['curiosity_gap_ja']} | "
            f"{row['angle_expansion_ja']} | {row['extra_search_facts_ja']} | | |"
        )
    with open("USER_EVAL_TOPIC_DISCOVERY_BROAD.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    # dropped_candidates.md
    dc_lines = ["# dropped_candidates", "",
                f"モデルが検討して落とした候補: {len(dropped)}件", ""]
    for d in dropped:
        cat = d.get("category")
        cat_label = CATEGORY_LABELS.get(cat, "不明")
        dc_lines.append(f"- [{cat}:{cat_label}] {d.get('seed_title')} "
                         f"({d.get('seed_url')}): {d.get('reason_dropped_ja')}")
    with open(out_path(out_dir, "dropped_candidates.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(dc_lines) + "\n")

    # category_distribution.md(8系統の探索有無 + 最終10件の系統分布)
    check_path = out_path(out_dir, "check_result.json")
    check_result = load_json(check_path) if os.path.exists(check_path) else {}
    # 手動curation(process_deviation発生時にSonnetがattempt_1を最終採用に
    # 切り替えた場合など)があれば優先する。check_result.json自体の
    # attempt_1/attempt_2/adopted_attemptフィールドは機械判定の履歴として
    # 変更しない(2026-09-25、TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01)。
    manual = check_result.get("manually_adopted_for_deliverables")
    adopted_attempt = (manual.get("adopted") if manual
                        else check_result.get("adopted_attempt", "attempt_1"))
    adopted_check = check_result.get(adopted_attempt, {})
    coverage = adopted_check.get("category_query_coverage", {})
    final_dist = {}
    for p in packages:
        c = str(p.get("category"))
        final_dist[c] = final_dist.get(c, 0) + 1
    dropped_dist = {}
    for d in dropped:
        c = str(d.get("category"))
        dropped_dist[c] = dropped_dist.get(c, 0) + 1

    cat_lines = ["# category_distribution", "",
                 "## 探索カバレッジ(search_log.mdのqueryへのヒューリスティック"
                 "機械タグ付け。最終確定はREPORT §4でSonnetが目視再確認)",
                 "", "| category | label | query_hit_count |", "|---|---|---|"]
    for c in range(1, 9):
        cat_lines.append(f"| {c} | {CATEGORY_LABELS[c]} | {coverage.get(str(c), 0)} |")
    cat_lines += ["", "## 最終10件のcategory分布", "", "| category | label | count |",
                  "|---|---|---|"]
    for c in range(1, 9):
        cat_lines.append(f"| {c} | {CATEGORY_LABELS[c]} | {final_dist.get(str(c), 0)} |")
    cat_lines += ["", "## dropped_candidatesのcategory分布", "",
                  "| category | label | count |", "|---|---|---|"]
    for c in range(1, 9):
        cat_lines.append(f"| {c} | {CATEGORY_LABELS[c]} | {dropped_dist.get(str(c), 0)} |")
    news_n = sum(1 for p in packages if p.get("seed_lane") == "news")
    social_n = sum(1 for p in packages if p.get("seed_lane") == "social")
    extra_n = sum(1 for p in packages if p.get("extra_search_facts"))
    ja_source_n = sum(1 for p in packages if any(
        ord(ch) > 0x3000 for ch in (p.get("seed_source_name") or "")))
    cat_lines += ["", "## news/social比率・追加検索・日本語source",
                  f"- news={news_n} social={social_n} "
                  f"extra_search_facts非空={extra_n}/{len(packages)} "
                  f"日本語source(推定,seed_source_nameにCJK含む)={ja_source_n}/{len(packages)}"]
    with open(out_path(out_dir, "category_distribution.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(cat_lines) + "\n")

    # lane_ratio.md(前回scriptとの互換のため維持)
    lane_lines = ["# lane_ratio", "",
                  f"- news={news_n} social={social_n} "
                  f"extra_search_facts非空={extra_n}/{len(packages)}"]
    with open(out_path(out_dir, "lane_ratio.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lane_lines) + "\n")

    # qcd.md(前回LUNA-TRIAL-01との比較列つき)
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
            "| metric | 今回(BROAD) | 前回(LUNA-TRIAL-01実績) |",
            "|---|---|---|",
            f"| model_requested | {api_meta.get('model_requested')} | gpt-5.6-luna |",
            f"| response_model_actual | {api_meta.get('response_model_actual')} | gpt-5.6-luna |",
            f"| max_tool_calls (guard) | {api_meta.get('max_tool_calls')} | {PREV_TRIAL_MAX_TOOL_CALLS} |",
            f"| web_search_call_count | {api_meta.get('web_search_call_count')} | {PREV_TRIAL_WS_CALLS} |",
            f"| input_tokens | {usage.get('input_tokens')} | 80825 |",
            f"| output_tokens | {usage.get('output_tokens')} | 10588 |",
            f"| reasoning_tokens | {usage.get('reasoning_tokens')} | 2107 |",
            f"| total_tokens | {usage.get('total_tokens')} | 91413 |",
            f"| elapsed_ms | {api_meta.get('elapsed_ms')} | 133864.0 |",
            f"| retried(check step) | {check_result.get('retried')} | N/A(この機構自体が新設) |",
            f"| total_jpy(cumulative) | {total_jpy} | {PREV_TRIAL_ACTUAL_JPY} |",
            f"| topic_packages_count | {n_pkg} | 12(前回はminItems/maxItems未指定のため12件返却) |",
            f"| jpy_per_topic_package | {jpy_per_package} | 0.385 |",
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
                         choices=["estimate", "run", "check", "verify-window", "assemble"])
    parser.add_argument("--budget-jpy", type=float, default=BUDGET_JPY)
    parser.add_argument("--max-tool-calls", type=int, default=MAX_TOOL_CALLS_DEFAULT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.step == "estimate":
        cmd_estimate(args)
    elif args.step == "run":
        cmd_run(args)
    elif args.step == "check":
        cmd_check(args)
    elif args.step == "verify-window":
        cmd_verify_window(args)
    elif args.step == "assemble":
        cmd_assemble(args)


if __name__ == "__main__":
    main()
