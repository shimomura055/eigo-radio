# ============================================================
# er016_topic_selection_search_trial_03.py
# TOPIC-SELECTION-SEARCH-TRIAL-03 (Fable設計、2026-09-24)
# ============================================================
# 目的: Reference級の「聞きたくなる素材」を自律的に発見できる検索・
# 選定方式の改善Trial(Hook改善ではなく、検索/Source Selection/最終
# Topic Selectionそのものの品質改善)。Production実装ではない。
# Production正式path(daily runner・er011_*/er014_*等)は一切変更しない。
#
# 方式: 5レーン(A Unexpected Reversal / B Everyday Why / C Personal
# Relevance / D Talkability・Casual / E Big Change in One Sentence)から
# Query生成→初期探索(最大20 call)→Source Quality Gate(OPEN-174統合)→
# 不足タイプ自己診断→追加探索(最大8 call)→Source Gate再適用→
# Selection Gate(Luna)→検証(公開時刻・到達性)→Selection model比較
# (Sol、Fable追加arm)→Reference/ChatGPT API-only/Luna APIとの型比較。
#
# 禁止事項(委任文より): ReferenceのタイトルやHook、評価dataset
# (docs/pm/topic_selection_user_eval_dataset.json)のtopic/hook文字列を
# Query・Prompt・Selection入力に入れない(teacherステップでの定性化目的の
# 使用のみ例外、以後は定性記述のみを使う)。Web Searchの大量反復禁止。
# 総費用上限\200(Main<=\130、Fable追加arm<=\40)。
#
# 再利用: er002_ja_web_research_r3(extract_web_search_usage/
# extract_sources)、er005_cost_logger(install/logging_context)、
# er006_model_routing_contract_01(WRITER_MODEL)。
# er016_topic_selection_chatgpt_repro_01.pyはimportのみ(REFERENCE_20/
# REFERENCE_CONTAMINATION_KEYWORDS)。同ファイル・cont02は変更しない。
#
# --step: teacher / queries1 / search1 / gate1 / diagnose / search2 /
#   gate2 / select / verify / compare / contamination-check
# 冪等性: 出力ファイルが既に存在する場合、--forceなしでは再実行しない。
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

THEME_TAG = "TOPIC_SELECTION_SEARCH_TRIAL_03"
MODEL_LUNA = routing.WRITER_MODEL  # "gpt-5.6-luna"
MODEL_SOL = "gpt-5.6-sol"
EFFORT_DEFAULT = "medium"
JST = timezone(timedelta(hours=9))
UTC = timezone.utc

WINDOW_START_JST = "2026-09-22T21:05:00+09:00"

MAIN_BUDGET_JPY = 130.0
MAIN_SOFT_STOP_JPY = 110.0  # このstepグループ(search1/search2)で新規callを
                             # 止める閾値。残り(~20円)はgate/diagnose/select/
                             # compare等の非search call用に確保する。
SOL_ARM_BUDGET_JPY = 40.0
TOTAL_BUDGET_JPY = 200.0
USD_TO_JPY = 160

EVAL_DATASET_PATH = "docs/pm/topic_selection_user_eval_dataset.json"

# ------------------------------------------------------------
# Search Lane定義(委任文より、意図を維持)
# ------------------------------------------------------------
LANES = {
    "A": ("Unexpected Reversal",
          "一見Aだが実はB/技術の裏に人間/便利になるはずが別の問題/"
          "常識の逆転が起きている話題"),
    "B": ("Everyday Why",
          "日常で自然に「そういえば、なんで？」と思える話"
          "(例: なぜ旅行バッグは毎回いっぱいになるのか/"
          "なぜ眠れないだけで病院へ行っていいのか/なぜ○○が最近増えているのか)"),
    "C": ("Personal Relevance",
          "「自分にも関係ありそう」と感じる話(生活・仕事・スマホ・買い物・"
          "睡眠・旅行・食事・家・通勤など)"),
    "D": ("Talkability・Casual",
          "友人に「これ知ってる？」と話しやすい話(SNS・小さな流行・"
          "ちょっと変な現象・身近な驚きなど。ただし単に軽いだけの記事は選ばない)"),
    "E": ("Big Change in One Sentence",
          "一文で「世の中が少し変わった」と感じられるニュース"
          "(AI・人間の役割・働き方・生活習慣・社会の変化など)"),
}
LANES_TEXT = "\n".join(
    f"Lane {k}: {v[0]} — {v[1]}" for k, v in LANES.items()
)

SOURCE_GATE_CATEGORIES = [
    "NEWS_FEATURE", "PRODUCT_PHENOMENON", "PR_ADVERTORIAL",
    "AFFILIATE_RANKING", "SALE_PRICE", "UNCLEAR",
]
SOURCE_GATE_EXCLUDE = {"PR_ADVERTORIAL", "AFFILIATE_RANKING", "SALE_PRICE"}

MACHINE_PR_SIGNAL_RE = re.compile(
    r"prtimes|/pr/|sponsored|PR|おすすめ|選|ランキング|セール|価格比較|"
    r"楽天|amazon|アフィリエイト|clip|kakaku",
    re.IGNORECASE,
)

SELECTION_CRITERIA_SENTENCE = (
    "聞き手が反応するのは、意外な逆転/答えを知りたくなる問い/自分事になる"
    "/日常の小さな謎/世界の変化を一言で理解できる切り口/人に話したくなる"
    "/少し俗っぽい/『そう言われると確かに気になる』。身近さだけを軸に"
    "しない。重要なニュースであることや、技術的に新しいことや、軽いこと"
    "は、それだけでは理由にならない。"
)

SELECTION_GATE_TEXT = """【Selection Gate(7観点)】
1. 聞きたくなるか(タイトルを聞いただけで「続きが少し気になる」となるか)
2. 一般性(一部専門家だけではなく比較的広い人に届くか)
3. 自分事性(生活・仕事・人間関係・社会変化などとの接点)
4. 意外性/Reversal(単なる新情報ではなく「そうなの？」があるか)
5. Talkability(人に話したくなるか)
6. Audio適性(数字・固有名詞・統計・専門説明が大量に必要にならないか)
7. Source品質(PR・広告・販促記事ではないか)

【注意(混同しない)】
- 社会的重要性が高い ≠ 聞きたい
- 技術的に新しい ≠ 面白い
- 軽い話題 ≠ 面白い
- 有名企業の記事 ≠ 広く聞きたい

「広い人が聞きたくなるか」(Selection Gate 1+2)を独立した観点として
最も重視してください。"""

# 非混入検査の対象stage prefix(teacher/compareは意図的な例外として除外。
# 理由はREPORTに明記する)。
CONTAMINATION_CHECK_PREFIXES = (
    "queries1", "search1_", "gate1", "diagnose", "queries2",
    "search2_", "gate2", "select_luna", "select_sol", "solarm_",
)


# ------------------------------------------------------------
# ヘルパー(base scriptパターン踏襲)
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
        "window_note": "公開日時2026-09-22 21:05 JST〜実行開始時刻(Reference窓"
                       "[09-22 21:05→09-23 21:05]を含む直近窓)。",
        "created_at_jst": now_jst.isoformat(),
    }
    save_json(path, meta)
    print(f"[OK] run_meta作成: window_end_jst={meta['window_end_jst']}")
    return meta


def call_model(client, developer: str, user: str, schema=None, web_search=False,
                stage="", model=MODEL_LUNA, effort=EFFORT_DEFAULT, out_dir=None,
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
    if web_search:
        kwargs["tools"] = [{"type": "web_search"}]
    try:
        with cl.logging_context(THEME_TAG, stage):
            response = client.responses.create(**kwargs)
    except Exception as exc:
        if retried:
            raise
        print(f"[RETRY] {stage}: 技術的retry 1回目 ({exc})")
        time.sleep(2)
        return call_model(client, developer, user, schema=schema,
                           web_search=web_search, stage=stage, model=model,
                           effort=effort, out_dir=out_dir, retried=True)
    if response.model != model:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={model}, actual={response.model})"
        )
    return response


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
# cost集計(base scriptの既知バグ[e.get("model")→存在しないキー]を修正し、
# 実フィールド名model_idを使う。main/sol armを分離集計する)
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
    total_usd_main = 0.0
    total_usd_sol_arm = 0.0
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
        if stage.startswith("solarm_"):
            total_usd_sol_arm += usd
        else:
            total_usd_main += usd
        total_calls += 1
        total_ws_calls += ws

    by_stage_jpy = {
        stage: {**vals, "jpy": round(vals["usd"] * USD_TO_JPY, 2)}
        for stage, vals in by_stage.items()
    }
    result = {
        "by_stage": by_stage_jpy,
        "total_main_jpy": round(total_usd_main * USD_TO_JPY, 2),
        "total_solarm_jpy": round(total_usd_sol_arm * USD_TO_JPY, 2),
        "total_jpy": round((total_usd_main + total_usd_sol_arm) * USD_TO_JPY, 2),
        "total_openai_calls": total_calls,
        "total_web_search_call_count": total_ws_calls,
        "usd_to_jpy": USD_TO_JPY,
        "main_budget_jpy": MAIN_BUDGET_JPY,
        "main_soft_stop_jpy": MAIN_SOFT_STOP_JPY,
        "solarm_budget_jpy": SOL_ARM_BUDGET_JPY,
        "total_budget_jpy": TOTAL_BUDGET_JPY,
        "within_main_budget": round(total_usd_main * USD_TO_JPY, 2) <= MAIN_BUDGET_JPY,
        "within_solarm_budget": round(total_usd_sol_arm * USD_TO_JPY, 2) <= SOL_ARM_BUDGET_JPY,
        "within_total_budget": round((total_usd_main + total_usd_sol_arm) * USD_TO_JPY, 2) <= TOTAL_BUDGET_JPY,
    }
    save_json(out_path(out_dir, "cost.json"), result)
    return result


def main_cost_so_far(out_dir: str) -> float:
    return compute_cost(out_dir)["total_main_jpy"]


# ------------------------------------------------------------
# 非混入検査キーワード集合(REFERENCE_CONTAMINATION_KEYWORDS + dataset A/Bの
# topic_ja/hook_ja全文)
# ------------------------------------------------------------
def contamination_keywords() -> list:
    kws = list(repro01.REFERENCE_CONTAMINATION_KEYWORDS)
    ds = load_json(EVAL_DATASET_PATH)
    for key in ("dataset_a", "dataset_b"):
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
            if fname.startswith("teacher") or fname.startswith("compare"):
                excluded_by_design.append(fname)
                continue
            if not fname.startswith(CONTAMINATION_CHECK_PREFIXES):
                continue
            checked.append(fname)
            for kw in check_contamination_in_text(content, keywords):
                hits.append({"file": fname, "keyword": kw})
    result = {
        "keyword_count": len(keywords),
        "checked_files": checked,
        "excluded_by_design_files": excluded_by_design,
        "excluded_by_design_reason": (
            "teacher_*: Teacher Data定性化のためdataset全文を意図的に投入する"
            "唯一のstage(出力は定性記述のみ、以後のPromptには使わない)。"
            "compare_*: 4集合比較のため委任文で明示的に許可されたstage"
            "(Reference/A/BのTopic文字列を型分類のためだけに使用し、"
            "Query/Selection入力へは投入しない)。"
        ),
        "contamination_hits": hits,
        "contaminated": len(hits) > 0,
    }
    save_json(path, result)
    print(f"[OK] contamination-check: checked_files={len(checked)} "
          f"keywords={len(keywords)} hits={len(hits)} contaminated={result['contaminated']}")


# ============================================================
# step: teacher
# ============================================================
TEACHER_SCHEMA = {
    "name": "teacher_summary",
    "schema": {
        "type": "object",
        "properties": {
            "ge5_vs_lt5_pattern_ja": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
            "reference_strong_patterns_ja": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
            "ab_failure_patterns_ja": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        },
        "required": ["ge5_vs_lt5_pattern_ja", "reference_strong_patterns_ja", "ab_failure_patterns_ja"],
        "additionalProperties": False,
    },
    "strict": True,
}


def cmd_teacher(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "teacher_summary.json")
    if skip_if_exists(path, args.force):
        return
    ds = load_json(EVAL_DATASET_PATH)
    install_logger(out_dir)
    client = get_client()

    def compact(items):
        return [{"topic_ja": it["topic_ja"], "hook_ja": it.get("hook_ja"),
                  "user_score": it["user_score"]} for it in items]

    developer = (
        "あなたはNews Topic選定の教師データ分析担当です。このstepに限り、"
        "ユーザー評価済みの実データ(Topic・Hook・スコア)を見て、傾向を"
        "定性的に要約してください。出力には、個別の話題名・Hook文言・"
        "点数・固有名詞を一切含めないでください(以後の検索・選定工程では"
        "この要約だけを使い、元データは使いません)。"
    )
    user = f"""以下はユーザーが1〜10で評価した3つのデータセットです
(5以上=現時点で採用可能相当。ただし5未満でもHookの付け方で点数が上がる
可能性があるため「Topic自体が完全に悪い」とは限りません。評価対象は
Topic+Sourceの素材としての強さです)。

【データセットR: Reference(ChatGPT作成、20件、平均{ds['summary_observed_facts_only']['dataset_r']['mean_score']}、5以上{ds['summary_observed_facts_only']['dataset_r']['count_score_ge_5']}/20)】
{json.dumps(compact(ds['dataset_r']), ensure_ascii=False, indent=2)}

【データセットA: ChatGPT API-only(20件、平均{ds['summary_observed_facts_only']['dataset_a']['mean_score']}、5以上{ds['summary_observed_facts_only']['dataset_a']['count_score_ge_5']}/20)】
{json.dumps(compact(ds['dataset_a']), ensure_ascii=False, indent=2)}

【データセットB: Luna API(17件、平均{ds['summary_observed_facts_only']['dataset_b']['mean_score']}、5以上{ds['summary_observed_facts_only']['dataset_b']['count_score_ge_5']}/17)】
{json.dumps(compact(ds['dataset_b']), ensure_ascii=False, indent=2)}

これらを分析し、以下3点をそれぞれ5行以内で要約してください。
**重要: 出力には個別の話題名・Hook文言・固有名詞・点数を書かず、
一般化した性質の記述だけにしてください。**

1. ge5_vs_lt5_pattern_ja: スコア5以上と5未満を分ける性質は何か
2. reference_strong_patterns_ja: Reference(R)に多く、A/Bに少ない型は何か
3. ab_failure_patterns_ja: A/Bに多い失敗の型は何か"""

    response = call_model(client, developer, user, schema=TEACHER_SCHEMA,
                           web_search=False, stage="teacher", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)
    save_json(path, parsed)
    save_prompt_and_response(out_dir, "teacher", developer, user, meta)
    compute_cost(out_dir)
    print(f"[OK] teacher: model={meta['response_model_actual']} "
          f"ge5patterns={len(parsed['ge5_vs_lt5_pattern_ja'])}")


# ============================================================
# step: queries1 (Step 1 Query生成)
# ============================================================
def _queries_schema(name: str) -> dict:
    return {
        "name": name,
        "schema": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "lane": {"type": "string", "enum": ["A", "B", "C", "D", "E"]},
                            "query_ja": {"type": "string"},
                            "rationale_ja": {"type": "string"},
                        },
                        "required": ["lane", "query_ja", "rationale_ja"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["queries"],
            "additionalProperties": False,
        },
        "strict": True,
    }


QUERY_DEVELOPER = (
    "あなたはNews Discoveryのクエリ設計担当です。実際にweb検索に使う"
    "日本語検索クエリを考えます。カテゴリ名(例:「AI」「健康」「旅行」)"
    "だけの検索語ではなく、人が『なぜ？』『え、本当に？』『それ自分にも"
    "ある』と感じる構造を持つクエリを作ってください。特定の既知記事の"
    "タイトルや見出しをそのまま検索語に埋め込む「カンニング」は絶対に"
    "しないでください。"
)


def _build_queries_user(teacher: dict, extra_note: str = "") -> str:
    return f"""【5つのSearch Lane】
{LANES_TEXT}

【教師データからの定性的傾向(具体話題・Hook・点数は含まない一般化した
記述。参考にしてよいが、これを直接検索語にしないこと)】
- 5以上と5未満を分ける性質: {json.dumps(teacher['ge5_vs_lt5_pattern_ja'], ensure_ascii=False)}
- Referenceに多い型: {json.dumps(teacher['reference_strong_patterns_ja'], ensure_ascii=False)}
- A/Bに多い失敗型: {json.dumps(teacher['ab_failure_patterns_ja'], ensure_ascii=False)}

【制約】
- カテゴリ名単独のクエリは禁止(例:「AI ニュース」のような語だけの
  クエリは不可)。
- 「なぜ」「本当に」「自分にも」等、人の疑問・関心の構造を反映すること。
- 既知記事のタイトル・見出しの一部を検索語に埋め込まないこと。
- 国内生活系(Lane B/C/D)は、日本国内の媒体が実際にヒットしやすい
  日本語語彙にすること。
{extra_note}

各レーン(A〜E)について4本ずつ、合計20本の検索クエリを作成してください。
各クエリにlane・query_ja(実際に検索エンジンに入力する日本語クエリ)・
rationale_ja(このクエリで何を狙うか、40字程度)を付けてください。"""


def cmd_queries1(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "queries_round1.json")
    if skip_if_exists(path, args.force):
        return
    teacher = load_json(out_path(out_dir, "teacher_summary.json"))
    install_logger(out_dir)
    client = get_client()
    keywords = contamination_keywords()

    attempt = 1
    user = _build_queries_user(teacher)
    while True:
        stage = "queries1" if attempt == 1 else f"queries1_retry{attempt}"
        response = call_model(client, QUERY_DEVELOPER, user,
                               schema=_queries_schema("queries_round1"),
                               web_search=False, stage=stage, out_dir=out_dir)
        parsed = json.loads(response.output_text)
        meta = response_meta(response, user, QUERY_DEVELOPER)
        save_prompt_and_response(out_dir, stage, QUERY_DEVELOPER, user, meta)

        all_text = json.dumps(parsed["queries"], ensure_ascii=False)
        hits = check_contamination_in_text(all_text, keywords)
        if not hits:
            break
        print(f"[CONTAMINATION] queries1 attempt={attempt} hits={hits}")
        if attempt >= 2:
            save_json(out_path(out_dir, "stop_reason.json"), {
                "stage": "queries1",
                "reason": "REFERENCE_CONTAMINATION: 2回目のQuery生成でも"
                          "汚染キーワードを検出したためSTOP",
                "hits": hits,
            })
            raise RuntimeError(f"STOP条件該当: queries1 contamination after 2 attempts: {hits}")
        attempt += 1
        user = _build_queries_user(
            teacher,
            extra_note="\n(前回の出力に既知データの語句が混入していたため、"
                       "一般化した検索クエリに作り直してください。)")

    lane_counts = {}
    for q in parsed["queries"]:
        lane_counts[q["lane"]] = lane_counts.get(q["lane"], 0) + 1
    save_json(path, {"queries": parsed["queries"], "lane_counts": lane_counts,
                      "attempts": attempt})
    compute_cost(out_dir)
    print(f"[OK] queries1: total={len(parsed['queries'])} lane_counts={lane_counts} "
          f"attempts={attempt} model={meta['response_model_actual']}")


# ============================================================
# search1 / search2 共通: 各queryごとに1 web_search call
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
            "summary_ja": {"type": "string"},
            "country_scope": {"type": "string"},
            "is_pr_or_ad_guess": {"type": "boolean"},
        },
        "required": ["title", "source_name", "url", "published_time_as_shown",
                     "published_time_iso", "time_uncertain", "summary_ja",
                     "country_scope", "is_pr_or_ad_guess"],
        "additionalProperties": False,
    }


def _search_call_schema(name: str) -> dict:
    return {
        "name": name,
        "schema": {
            "type": "object",
            "properties": {
                "candidates": {"type": "array", "items": _candidate_item_schema(), "maxItems": 6},
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
)


def _search_one_query(client, out_dir, meta_run, query_rec, stage, round_no):
    lane = query_rec["lane"]
    lane_name, lane_desc = LANES[lane]
    user = f"""対象窓(JST、固定): {meta_run['window_start_jst']} 〜 {meta_run['window_end_jst']}
以下の検索クエリを使って、この窓内に公開・話題化した候補を探してください。

【検索クエリ】
{query_rec['query_ja']}
(このクエリを設計した意図: {query_rec['rationale_ja']}。
Lane {lane}: {lane_name} — {lane_desc})

窓より前や後に公開された記事は候補にしないでください。公開時刻が確認
できない場合は無理に断定せず、time_uncertain: trueとしてください。

最大6件、JSONで返してください。該当が少なければ無理に6件埋めず、実際に
見つかった件数だけ返してください。各候補にtitle・source_name・url
(検索結果の引用に実際に現れたURLのみ)・published_time_as_shown・
published_time_iso・time_uncertain・summary_ja(1〜2文)・country_scope
(日本/世界/特定国名)・is_pr_or_ad_guess(PR・広告・アフィリエイト記事
らしいか)を埋めてください。"""

    response = call_model(client, SEARCH_DEVELOPER, user,
                           schema=_search_call_schema(stage),
                           web_search=True, stage=stage, out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, SEARCH_DEVELOPER)
    save_prompt_and_response(out_dir, stage, SEARCH_DEVELOPER, user, meta)
    candidates = []
    for c in parsed["candidates"]:
        c = dict(c)
        c["lane"] = lane
        c["query_ja"] = query_rec["query_ja"]
        c["round"] = round_no
        candidates.append(c)
    return candidates, meta


def _run_search_round(args, queries_path_key, round_no, pool_out_name, call_prefix):
    out_dir = args.out_dir
    pool_path = out_path(out_dir, pool_out_name)
    if skip_if_exists(pool_path, args.force):
        return
    queries_data = load_json(out_path(out_dir, queries_path_key))
    queries = queries_data["queries"]
    meta_run = ensure_run_meta(out_dir)
    install_logger(out_dir)
    client = get_client()

    max_calls = min(args.max_calls, len(queries))
    all_candidates = []
    calls_made = 0
    stop_reason = None
    for i, q in enumerate(queries[:max_calls], start=1):
        cost_so_far = main_cost_so_far(out_dir)
        if cost_so_far >= MAIN_SOFT_STOP_JPY:
            stop_reason = (
                f"budget_guard: main cost so far={cost_so_far} JPY >= soft_stop="
                f"{MAIN_SOFT_STOP_JPY} JPY, stopped after {calls_made}/{max_calls} calls "
                f"in round{round_no}"
            )
            print(f"[STOP] {stop_reason}")
            break
        stage = f"{call_prefix}{q['lane']}_{i:02d}"
        try:
            cands, meta = _search_one_query(client, out_dir, meta_run, q, stage, round_no)
        except Exception as exc:
            print(f"[WARN] {stage} failed: {exc}")
            continue
        all_candidates.extend(cands)
        calls_made += 1
        print(f"[OK] {stage}: candidates={len(cands)} model={meta['response_model_actual']} "
              f"ws_calls={meta['web_search_usage']['web_search_call_count']}")

    # dedup by URL
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

    lane_counts_raw = {}
    for c in all_candidates:
        lane_counts_raw[c["lane"]] = lane_counts_raw.get(c["lane"], 0) + 1

    result = {
        "round": round_no,
        "calls_made": calls_made,
        "queries_available": len(queries),
        "queries_used": max_calls,
        "raw_candidate_count": len(all_candidates),
        "deduped_candidate_count": len(deduped),
        "lane_counts_raw": lane_counts_raw,
        "stop_reason": stop_reason,
        "candidates": deduped,
    }
    save_json(pool_path, result)
    if stop_reason:
        save_json(out_path(out_dir, f"stop_reason_round{round_no}.json"),
                   {"stage": f"search{round_no}", "reason": stop_reason})
    compute_cost(out_dir)
    print(f"[OK] search round{round_no}: calls_made={calls_made}/{max_calls} "
          f"raw={len(all_candidates)} deduped={len(deduped)}")


def cmd_search1(args):
    _run_search_round(args, "queries_round1.json", 1, "pool_round1.json", "search1_")


def cmd_search2(args):
    _run_search_round(args, "queries_round2.json", 2, "pool_round2.json", "search2_")


# ============================================================
# Source Quality Gate (機械signal + 1 Luna分類call)
# ============================================================
def _gate_classify_schema(name: str) -> dict:
    return {
        "name": name,
        "schema": {
            "type": "object",
            "properties": {
                "classifications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "candidate_id": {"type": "string"},
                            "category": {"type": "string", "enum": SOURCE_GATE_CATEGORIES},
                            "reason_ja": {"type": "string"},
                        },
                        "required": ["candidate_id", "category", "reason_ja"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["classifications"],
            "additionalProperties": False,
        },
        "strict": True,
    }


GATE_DEVELOPER = (
    "あなたはNews SourceのQuality Gate担当です。各候補のSourceが、"
    "ニュース・特集記事なのか、それとも広告・PR・アフィリエイト・"
    "販促目的の記事なのかを分類してください。商品・サービスを扱う記事"
    "自体は禁止ではありません(新しい生活習慣/消費者行動の変化/新サービス"
    "の社会的影響/なぜ売れているかという現象は許容カテゴリです)。"
    "問題にすべきなのは、Topicが商品を扱っているかどうかではなく、"
    "Source自体が広告・販促・アフィリエイト記事になっているかどうかです。"
)


def _gate_user(candidates: list) -> str:
    items = [{"candidate_id": c["candidate_id"], "title": c["title"],
              "source_name": c["source_name"], "summary_ja": c["summary_ja"],
              "url": c["url"], "machine_pr_signal": c["machine_pr_signal"],
              "is_pr_or_ad_guess": c.get("is_pr_or_ad_guess")}
             for c in candidates]
    return f"""以下の候補一覧を分類してください。machine_pr_signalは、URL/
タイトルに広告・PR・アフィリエイト・ランキング・セール関連語が機械的に
検出されたかどうかのヒントです(参考情報。最終判断はSource全体の性質で
行ってください)。

【分類カテゴリ】
- NEWS_FEATURE: ニュース・特集記事
- PRODUCT_PHENOMENON: 商品・サービスを扱うが、社会的な現象・消費者行動の
  変化・なぜ売れているか等を扱う記事(除外しない)
- PR_ADVERTORIAL: PR記事・広告・Sponsored・Advertorial
- AFFILIATE_RANKING: アフィリエイト記事・「おすすめ○選」・EC/売れ筋
  ランキング中心
- SALE_PRICE: セール訴求・価格比較・購買誘導が中心
- UNCLEAR: 上記のいずれか判断がつかない

【候補一覧】
{json.dumps(items, ensure_ascii=False, indent=2)}

全候補についてcandidate_id・category・reason_ja(1行)を返してください。"""


def _run_gate(args, pool_key, stage, gate_out_name):
    out_dir = args.out_dir
    gate_path = out_path(out_dir, gate_out_name)
    if skip_if_exists(gate_path, args.force):
        return
    pool = load_json(out_path(out_dir, pool_key))
    candidates = pool["candidates"]
    for c in candidates:
        url_title = f"{c.get('url', '')} {c.get('title', '')}"
        c["machine_pr_signal"] = bool(MACHINE_PR_SIGNAL_RE.search(url_title))

    if not candidates:
        save_json(gate_path, {"total": 0, "classifications": [], "kept": [], "excluded": [],
                               "kept_count": 0, "excluded_count": 0,
                               "category_counts": {}, "exclude_rate": 0.0,
                               "diversity_risk": False})
        print(f"[OK] {stage}: 候補0件のためGate skip")
        return

    install_logger(out_dir)
    client = get_client()
    user = _gate_user(candidates)
    response = call_model(client, GATE_DEVELOPER, user,
                           schema=_gate_classify_schema(stage),
                           web_search=False, stage=stage, out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, GATE_DEVELOPER)
    save_prompt_and_response(out_dir, stage, GATE_DEVELOPER, user, meta)

    by_id = {c["candidate_id"]: c for c in candidates}
    cls_by_id = {c["candidate_id"]: c for c in parsed["classifications"]}
    category_counts = {}
    kept = []
    excluded = []
    for cid, cand in by_id.items():
        cls = cls_by_id.get(cid)
        category = cls["category"] if cls else "UNCLEAR"
        reason = cls["reason_ja"] if cls else "分類結果なし(UNCLEAR扱い)"
        category_counts[category] = category_counts.get(category, 0) + 1
        entry = dict(cand)
        entry["source_gate_category"] = category
        entry["source_gate_reason_ja"] = reason
        if category in SOURCE_GATE_EXCLUDE:
            excluded.append(entry)
        else:
            kept.append(entry)

    exclude_rate = len(excluded) / len(candidates) if candidates else 0.0
    result = {
        "total": len(candidates),
        "category_counts": category_counts,
        "kept_count": len(kept),
        "excluded_count": len(excluded),
        "exclude_rate": round(exclude_rate, 3),
        "diversity_risk": exclude_rate > 0.5,
        "kept": kept,
        "excluded": [{"candidate_id": e["candidate_id"], "title": e["title"],
                      "source_name": e["source_name"], "url": e["url"],
                      "category": e["source_gate_category"],
                      "reason_ja": e["source_gate_reason_ja"]} for e in excluded],
    }
    save_json(gate_path, result)
    compute_cost(out_dir)
    print(f"[OK] {stage}: total={len(candidates)} kept={len(kept)} "
          f"excluded={len(excluded)} exclude_rate={result['exclude_rate']} "
          f"diversity_risk={result['diversity_risk']} category_counts={category_counts}")


def cmd_gate1(args):
    _run_gate(args, "pool_round1.json", "gate1_classify", "source_gate_round1.json")


def cmd_gate2(args):
    _run_gate(args, "pool_round2.json", "gate2_classify", "source_gate_round2.json")
    # gate2完了後、round1 kept + round2 keptを統合してpool_finalを作る
    out_dir = args.out_dir
    final_path = out_path(out_dir, "pool_final.json")
    if skip_if_exists(final_path, args.force):
        return
    gate1 = load_json(out_path(out_dir, "source_gate_round1.json"))
    gate2 = load_json(out_path(out_dir, "source_gate_round2.json"))
    merged = list(gate1["kept"]) + list(gate2["kept"])
    seen = set()
    deduped = []
    for c in merged:
        url = c.get("url")
        if url and url in seen:
            continue
        if url:
            seen.add(url)
        deduped.append(c)
    save_json(final_path, {
        "kept_count": len(deduped),
        "from_round1": len(gate1["kept"]),
        "from_round2": len(gate2["kept"]),
        "candidates": deduped,
    })
    print(f"[OK] pool_final: kept_count={len(deduped)} "
          f"(round1={len(gate1['kept'])}, round2={len(gate2['kept'])})")


# ============================================================
# step: diagnose (Step 4 自己診断 + 追加Query生成、1 call)
# ============================================================
def _reference_type_distribution() -> dict:
    counts = {}
    total_tags = 0
    for item in repro01.REFERENCE_20:
        tags = [t.strip() for t in re.split(r"[・/、,]", item["type_tags"]) if t.strip()]
        for t in tags:
            counts[t] = counts.get(t, 0) + 1
            total_tags += 1
    return {"tag_counts": counts, "total_tags": total_tags,
            "tag_ratio": {k: round(v / total_tags, 3) for k, v in counts.items()}}


DIAGNOSE_SCHEMA = {
    "name": "diagnosis",
    "schema": {
        "type": "object",
        "properties": {
            "diagnosis_ja": {"type": "string"},
            "missing_types": {"type": "array", "items": {"type": "string"}},
            "additional_queries": {
                "type": "array",
                "maxItems": 8,
                "items": {
                    "type": "object",
                    "properties": {
                        "lane": {"type": "string", "enum": ["A", "B", "C", "D", "E"]},
                        "query_ja": {"type": "string"},
                        "rationale_ja": {"type": "string"},
                    },
                    "required": ["lane", "query_ja", "rationale_ja"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["diagnosis_ja", "missing_types", "additional_queries"],
        "additionalProperties": False,
    },
    "strict": True,
}

DIAGNOSE_DEVELOPER = (
    "あなたは調査の自己診断担当です。この工程では検索は行わず、既に"
    "得られた候補一覧(Source Gate通過分)だけを見て、Referenceの型分布と"
    "比較し、不足しているタイプを診断してください。"
)


def cmd_diagnose(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "diagnosis.json")
    if skip_if_exists(path, args.force):
        return
    gate1 = load_json(out_path(out_dir, "source_gate_round1.json"))
    kept = gate1["kept"]
    ref_dist = _reference_type_distribution()
    install_logger(out_dir)
    client = get_client()
    keywords = contamination_keywords()

    pool_view = [{"candidate_id": c["candidate_id"], "title": c["title"],
                  "summary_ja": c["summary_ja"], "lane": c["lane"]} for c in kept]

    def build_user(extra_note=""):
        return f"""【Source Gate通過後の候補一覧(点数なし)】
{json.dumps(pool_view, ensure_ascii=False, indent=2)}

【Reference 20件の型タグ分布(機械集計、話題名は含まない比率表)】
{json.dumps(ref_dist['tag_ratio'], ensure_ascii=False, indent=2)}

【5つのSearch Lane】
{LANES_TEXT}

上記候補一覧のタイプ構成を、Referenceの型分布と比較し、不足していると
考えられるタイプを診断してください(例: Everyday Whyが少ない/人間的な
逆転が少ない/国内生活系が少ない/俗っぽいTopicが少ない/技術ニュースに
偏っている/硬い社会ニュースが多すぎる、等)。

diagnosis_ja(2〜4文)に診断内容を書き、missing_typesに不足していると
考えるタイプを短い語で列挙し、additional_queriesにその不足を埋めるため
の具体的な検索クエリを最大8本作ってください(各lane・query_ja・
rationale_jaを付ける。カテゴリ名単独禁止、既知記事タイトルの埋め込み
禁止は queries1 と同じ制約です)。{extra_note}"""

    attempt = 1
    user = build_user()
    while True:
        stage = "diagnose" if attempt == 1 else f"diagnose_retry{attempt}"
        response = call_model(client, DIAGNOSE_DEVELOPER, user, schema=DIAGNOSE_SCHEMA,
                               web_search=False, stage=stage, out_dir=out_dir)
        parsed = json.loads(response.output_text)
        meta = response_meta(response, user, DIAGNOSE_DEVELOPER)
        save_prompt_and_response(out_dir, stage, DIAGNOSE_DEVELOPER, user, meta)

        q_text = json.dumps(parsed["additional_queries"], ensure_ascii=False)
        hits = check_contamination_in_text(q_text, keywords)
        if not hits:
            break
        print(f"[CONTAMINATION] diagnose attempt={attempt} hits={hits}")
        if attempt >= 2:
            save_json(out_path(out_dir, "stop_reason.json"), {
                "stage": "diagnose", "reason": "REFERENCE_CONTAMINATION after 2 attempts",
                "hits": hits})
            raise RuntimeError(f"STOP条件該当: diagnose contamination after 2 attempts: {hits}")
        attempt += 1
        user = build_user(extra_note="\n(前回のadditional_queriesに既知データの語句が"
                                      "混入していたため、一般化したクエリに作り直して"
                                      "ください。)")

    save_json(path, {
        "diagnosis_ja": parsed["diagnosis_ja"],
        "missing_types": parsed["missing_types"],
        "reference_type_distribution": ref_dist,
        "pool_size_evaluated": len(pool_view),
        "attempts": attempt,
    })
    save_json(out_path(out_dir, "queries_round2.json"),
              {"queries": parsed["additional_queries"]})
    compute_cost(out_dir)
    print(f"[OK] diagnose: missing_types={parsed['missing_types']} "
          f"additional_queries={len(parsed['additional_queries'])} attempts={attempt}")


# ============================================================
# step: select (Selection Gate、Luna/Sol)
# ============================================================
def _selection_schema(name: str) -> dict:
    return {
        "name": name,
        "schema": {
            "type": "object",
            "properties": {
                "selections": {
                    "type": "array", "maxItems": 20,
                    "items": {
                        "type": "object",
                        "properties": {
                            "rank": {"type": "integer"},
                            "candidate_id": {"type": "string"},
                            "topic_ja": {"type": "string"},
                            "why_ja": {"type": "string"},
                        },
                        "required": ["rank", "candidate_id", "topic_ja", "why_ja"],
                        "additionalProperties": False,
                    },
                },
                "reserve": {
                    "type": "array", "maxItems": 5,
                    "items": {
                        "type": "object",
                        "properties": {
                            "rank": {"type": "integer"},
                            "candidate_id": {"type": "string"},
                            "topic_ja": {"type": "string"},
                            "why_ja": {"type": "string"},
                        },
                        "required": ["rank", "candidate_id", "topic_ja", "why_ja"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["selections", "reserve"],
            "additionalProperties": False,
        },
        "strict": True,
    }


SELECT_DEVELOPER = (
    "あなたはAudio News番組のTopic Selection担当です。候補一覧から、"
    "聞き手が実際に「聞きたくなる」20件を選んでください(内部の点数付けは"
    "不要です)。"
)


def _select_user(pool_view: list) -> str:
    return f"""【候補一覧(Source Gate通過分、点数なし)】
{json.dumps(pool_view, ensure_ascii=False, indent=2)}

{SELECTION_GATE_TEXT}

{SELECTION_CRITERIA_SENTENCE}

上記候補から20件を選び、rankを1〜20で付けてください。さらに、20件に
入らなかった中から予備5件を選び、rank21〜25として reserve に入れて
ください。各候補について、topic_ja(短い日本語の内容説明、1〜2文)と
why_ja(なぜ聞きたくなる候補なのか、1文)を書いてください。"""


def cmd_select(args):
    out_dir = args.out_dir
    model_key = args.model
    model = MODEL_LUNA if model_key == "luna" else MODEL_SOL
    is_sol_arm = model_key == "sol"
    stage = "solarm_select_sol" if is_sol_arm else "select_luna"
    out_name = "selection_sol.json" if is_sol_arm else "selection_luna.json"
    path = out_path(out_dir, out_name)
    if skip_if_exists(path, args.force):
        return

    if is_sol_arm:
        sol_cost_so_far = compute_cost(out_dir)["total_solarm_jpy"]
        if sol_cost_so_far >= SOL_ARM_BUDGET_JPY:
            print(f"[STOP] solarm budget reached ({sol_cost_so_far} >= {SOL_ARM_BUDGET_JPY}), skip select sol")
            return

    pool_final = load_json(out_path(out_dir, "pool_final.json"))
    pool_view = [{"candidate_id": c["candidate_id"], "title": c["title"],
                  "source_name": c["source_name"], "summary_ja": c["summary_ja"],
                  "lane": c["lane"], "source_gate_category": c["source_gate_category"],
                  "country_scope": c.get("country_scope")}
                 for c in pool_final["candidates"]]

    install_logger(out_dir)
    client = get_client()
    user = _select_user(pool_view)
    response = call_model(client, SELECT_DEVELOPER, user,
                           schema=_selection_schema(f"selection_{model_key}"),
                           web_search=False, stage=stage, model=model, out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, SELECT_DEVELOPER)
    save_prompt_and_response(out_dir, stage, SELECT_DEVELOPER, user, meta)

    by_id = {c["candidate_id"]: c for c in pool_final["candidates"]}

    def enrich(sel):
        out = []
        for s in sel:
            cand = by_id.get(s["candidate_id"], {})
            out.append({**s, "lane": cand.get("lane"), "source_name": cand.get("source_name"),
                        "url": cand.get("url"), "source_gate_category": cand.get("source_gate_category")})
        return out

    save_json(path, {"model": model, "model_key": model_key,
                      "selections": enrich(parsed["selections"]),
                      "reserve": enrich(parsed["reserve"])})
    compute_cost(out_dir)
    print(f"[OK] select[{model_key}]: model={meta['response_model_actual']} "
          f"selections={len(parsed['selections'])} reserve={len(parsed['reserve'])}")


# ============================================================
# step: verify (script only, 公開時刻・到達性)
# ============================================================
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; EigoRadioTopicSearchTrialBot/1.0; "
                  "+research trial, non-production)"
}
HTTP_TIMEOUT = 15


def _fetch(url: str):
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT, allow_redirects=True)
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
    path = out_path(out_dir, "final20.json")
    if skip_if_exists(path, args.force):
        return
    sel = load_json(out_path(out_dir, "selection_luna.json"))
    meta_run = ensure_run_meta(out_dir)

    results = []
    kept = []
    for s in sel["selections"]:
        v = _verify_url(s.get("url") or "", meta_run)
        entry = {**s, **v}
        results.append(entry)
        if not v["disqualified"]:
            kept.append(entry)
        time.sleep(0.2)

    disqualified_count = len(sel["selections"]) - len(kept)
    reserve_used = []
    if len(kept) < 20:
        for r in sel["reserve"]:
            if len(kept) >= 20:
                break
            v = _verify_url(r.get("url") or "", meta_run)
            entry = {**r, **v}
            if not v["disqualified"]:
                kept.append(entry)
                reserve_used.append(entry)
            time.sleep(0.2)

    save_json(path, {
        "window_start_jst": meta_run["window_start_jst"],
        "window_end_jst": meta_run["window_end_jst"],
        "checked_count": len(sel["selections"]),
        "disqualified_count": disqualified_count,
        "reserve_used_count": len(reserve_used),
        "final_count": len(kept),
        "verify_results": results,
        "final20": kept[:20],
        "reserve_used": reserve_used,
    })
    print(f"[OK] verify: checked={len(sel['selections'])} disqualified={disqualified_count} "
          f"reserve_used={len(reserve_used)} final_count={len(kept)}")


# ============================================================
# step: compare (4集合の型比較、1 call)
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
    final20 = load_json(out_path(out_dir, "final20.json"))
    source_gate1 = load_json(out_path(out_dir, "source_gate_round1.json"))
    source_gate2 = load_json(out_path(out_dir, "source_gate_round2.json"))

    items = []
    for it in repro01.REFERENCE_20:
        items.append({"item_id": f"R_{it['id']}", "set_label": "Reference(R)", "topic_ja": it["topic_ja"]})
    for it in ds["dataset_a"]:
        items.append({"item_id": f"A_{it['item_no']}", "set_label": "ChatGPT API-only(A)", "topic_ja": it["topic_ja"]})
    for it in ds["dataset_b"]:
        items.append({"item_id": f"B_{it['item_no']}", "set_label": "Luna API(B)", "topic_ja": it["topic_ja"]})
    for i, it in enumerate(final20["final20"], start=1):
        items.append({"item_id": f"T3_{i}", "set_label": "Trial-03(T3)", "topic_ja": it["topic_ja"]})

    install_logger(out_dir)
    client = get_client()
    user = f"""【Topicの型タグ】
{', '.join(COMPARE_TYPE_TAGS)}
(Everyday=日常のなぜ/Personal=自分事/Reversal=意外な逆転/Talkability=
話したくなる俗っぽさ/BigChange=一文で世の中が変わった/HardSocial=硬い
社会・政治・国際ニュース/Tech=技術中心/Product=商品・サービス中心/
Entertainment=芸能・スポーツ・エンタメ)

【分類対象(4集合、計{len(items)}件)】
{json.dumps([{"item_id": it["item_id"], "topic_ja": it["topic_ja"]} for it in items], ensure_ascii=False, indent=2)}

各item_idについて、あてはまる型タグ(複数可、最低1つ)とdomestic_or_intl
を返してください。"""

    response = call_model(client, COMPARE_DEVELOPER, user, schema=COMPARE_SCHEMA,
                           web_search=False, stage="compare_classify", out_dir=out_dir)
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

    pr_mix_t3 = None
    if source_gate1["total"] + source_gate2["total"] > 0:
        total_excl = source_gate1["excluded_count"] + source_gate2["excluded_count"]
        total_all = source_gate1["total"] + source_gate2["total"]
        pr_mix_t3 = round(total_excl / total_all, 3)

    ref_topics = {it["id"]: it["topic_ja"] for it in repro01.REFERENCE_20}
    overlap_hits = []
    for t3i, it in enumerate(final20["final20"], start=1):
        t3_words = set(re.findall(r"[一-龥ぁ-んァ-ヶA-Za-z0-9]{2,}", it["topic_ja"]))
        for rid, rtopic in ref_topics.items():
            r_words = set(re.findall(r"[一-龥ぁ-んァ-ヶA-Za-z0-9]{2,}", rtopic))
            if not t3_words or not r_words:
                continue
            jac = len(t3_words & r_words) / len(t3_words | r_words)
            if jac >= 0.3:
                overlap_hits.append({"trial03_item": it["topic_ja"], "reference_id": rid,
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
    lines += ["", f"## PR/広告混入率(Trial-03のみ、Source Gate結果に基づく機械算出)",
              f"Trial-03 PR/広告除外率: {pr_mix_t3} (source_gate_round1+2, "
              f"exclude={source_gate1['excluded_count']+source_gate2['excluded_count']}"
              f"/total={source_gate1['total']+source_gate2['total']})",
              "R/A/Bはこの分類callにSource品質項目を含めておらず、機械算出のPR混入率は"
              "無い(N/A、必要ならFable判断で別途目視確認)。", "",
              "## Referenceとの話題重複候補(機械ヒューリスティック、Jaccard>=0.3の単語一致のみ、目視推奨)",
              f"件数: {len(overlap_hits)}"]
    for h in overlap_hits:
        lines.append(f"- Trial-03「{h['trial03_item']}」 <-> Reference#{h['reference_id']}"
                      f"「{h['reference_topic']}」 jaccard={h['jaccard']}")
    save_json(out_path(out_dir, "comparison_sets_raw.json"),
              {"sets": sets, "pr_mix_t3": pr_mix_t3, "overlap_hits": overlap_hits})
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    compute_cost(out_dir)
    print(f"[OK] compare: sets={list(sets.keys())} pr_mix_t3={pr_mix_t3} overlap_hits={len(overlap_hits)}")


# ============================================================
# main
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["teacher", "queries1", "search1", "gate1", "diagnose",
                                  "search2", "gate2", "select", "verify", "compare",
                                  "contamination-check"])
    parser.add_argument("--max-calls", type=int, default=20)
    parser.add_argument("--model", choices=["luna", "sol"], default="luna")
    parser.add_argument("--arm", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    dispatch = {
        "teacher": cmd_teacher,
        "queries1": cmd_queries1,
        "search1": cmd_search1,
        "gate1": cmd_gate1,
        "diagnose": cmd_diagnose,
        "search2": cmd_search2,
        "gate2": cmd_gate2,
        "select": cmd_select,
        "verify": cmd_verify,
        "compare": cmd_compare,
        "contamination-check": cmd_contamination_check,
    }
    dispatch[args.step](args)


if __name__ == "__main__":
    main()
