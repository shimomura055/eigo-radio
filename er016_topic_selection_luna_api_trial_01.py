# ============================================================
# er016_topic_selection_luna_api_trial_01.py
# TOPIC-SELECTION-LUNA-API-TRIAL-01 (Fable設計、2026-09-24)
# ============================================================
# 目的: API経由gpt-5.6-luna(routing.WRITER_MODEL)が、直近24時間の話題から
# 「ユーザーが思わず聞きたくなるNews候補」を自力で発見(Discovery)→
# Hook生成(Hooks)→Ranking・20件選定(Rank)できるかを検証するTrial専用
# スクリプト。**Production実装ではない。** Production正式path(daily
# runner・er011_*/er014_*等)は一切変更しない。
#
# 禁止事項(委任文より): Topic発見・Hook生成・Ranking・最終20件選定は
# すべてLunaが行う。Sonnet側で候補追加・救済・Hook書き直し・順位手修正・
# 差し替えは一切行わない。Sonnetが行うのは (a) 複数レーンの生出力を
# candidate_idで機械的に結合する、(b) Luna自身が出したrank値でソートして
# 表示する、(c) スクリプトによるURL到達性・公開時刻検証(Phase 4)、
# (d) 集計(Phase 5)のみ。
#
# 再利用: er002_ja_web_research_r3(extract_web_search_usage/
# extract_sources)、er005_cost_logger(install/logging_context、
# monkeypatch方式でProduction呼び出しコードは無変更)、
# er006_model_routing_contract_01(WRITER_MODEL)を再利用する。
#
# サブコマンド: probe / discover --lane <general|everyday|scitech|light|sns>
#   / hooks / rank / verify / aggregate / cost
# 冪等性: 出力ファイルが既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing

load_dotenv()

THEME_TAG = "TOPIC_SELECTION_LUNA_API_TRIAL_01"
MODEL = routing.WRITER_MODEL  # "gpt-5.6-luna"
EFFORT = "medium"  # 全step medium固定(委任文§実行コマンド全文11番、費用抑制)
JST = timezone(timedelta(hours=9))
UTC = timezone.utc

LANES = {
    "general": "General/Hard News(日本国内・世界・経済・国際・社会)",
    "everyday": "Everyday/Curiosity(生活・Consumer・Food・Travel・Work・"
                "Education・Money・家庭・睡眠・健康)",
    "scitech": "Science/Technology(Science・Health・AI・Technology・"
               "Environment)",
    "light": "Light/Popular(Entertainment・Sports・Culture・Fashion・"
             "Lifestyle・商品・サービス・軽い話題・俗っぽいNews)",
    "sns": "Trend/SNS Discovery(Google Trends等急上昇、SNSで急速に注目、"
           "TikTok/X/Threads等で話題化、ネット上で議論・共有されている"
           "身近な話題)",
}
LANE_ORDER = ["general", "everyday", "scitech", "light", "sns"]

PURPOSE_SENTENCE = (
    "English Your Way = 日本人向け英語学習音声番組のNews候補選定Trial。"
    "派手さより『内容に裏づけられた知りたい問い』を作れる素材を探して"
    "います。"
)


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


def run_meta_path(out_dir: str) -> str:
    return out_path(out_dir, "run_meta.json")


def load_run_meta(out_dir: str) -> dict:
    path = run_meta_path(out_dir)
    if not os.path.exists(path):
        raise RuntimeError(
            f"run_meta.jsonが見つかりません({path})。先にprobeを実行してT_now/"
            "T_cutを確定してください。"
        )
    return load_json(path)


def call_luna(client, developer: str, user: str, schema=None, web_search=False,
               stage="", retried=False):
    """1回のAPI技術的retryのみを許可する(品質理由の再実行は禁止)。"""
    kwargs = dict(
        model=MODEL,
        reasoning={"effort": EFFORT},
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
        return call_luna(client, developer, user, schema=schema,
                          web_search=web_search, stage=stage, retried=True)
    if response.model != MODEL:
        raise RuntimeError(
            f"STOP条件該当: actual model_idがLunaでない(stage={stage}, "
            f"requested={MODEL}, actual={response.model})"
        )
    return response


def response_meta(response, prompt: str, developer: str, extra: dict = None) -> dict:
    meta = {
        "prompt": prompt,
        "developer_message": developer,
        "model_requested": MODEL,
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
    search_usage = r3.extract_web_search_usage(response)
    meta["web_search_usage"] = search_usage
    meta["sources"] = r3.extract_sources(response)
    if extra:
        meta.update(extra)
    return meta


# ------------------------------------------------------------
# probe (Phase 0)
# ------------------------------------------------------------
PROBE_SCHEMA = {
    "name": "sns_trend_probe",
    "schema": {
        "type": "object",
        "properties": {
            "accessible_themes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "theme_name": {"type": "string"},
                        "source_page": {"type": "string"},
                        "evidence_url": {"type": "string"},
                        "time_as_shown": {"type": ["string", "null"]},
                    },
                    "required": ["theme_name", "source_page", "evidence_url",
                                 "time_as_shown"],
                    "additionalProperties": False,
                },
            },
            "inaccessible_sources": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["accessible_themes", "inaccessible_sources"],
        "additionalProperties": False,
    },
    "strict": True,
}


def cmd_probe(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "phase0_probe.json")
    if skip_if_exists(path, args.force):
        return
    os.makedirs(out_dir, exist_ok=True)
    install_logger(out_dir)
    client = get_client()

    t_now = datetime.now(JST)
    t_cut = t_now - timedelta(hours=24)
    save_json(run_meta_path(out_dir), {
        "t_now_jst": t_now.isoformat(),
        "t_cut_jst": t_cut.isoformat(),
        "model": MODEL,
        "effort": EFFORT,
    })

    developer = (
        "あなたはTrend/SNS Discoveryの調査担当です。実際にweb_searchツールで"
        "アクセスできたページの情報だけを報告してください。アクセスできな"
        "かった・確認できなかったsourceについて推測で埋めることは禁止です。"
    )
    user = f"""現在の日時は {t_now.isoformat()}(JST)です。

日本で直近24時間({t_cut.isoformat()} 〜 {t_now.isoformat()}、JST)に
急上昇・話題化しているテーマを、実際にアクセスできるページ
(例: Google Trends日本、Yahoo!リアルタイム検索の話題ページ、
Togetter/ねとらぼ/ITmedia等のSNS話題まとめ、X/TikTok/Threadsの
公開ページ等)から取得してください。

各テーマについて、テーマ名(theme_name)・アクセスしたページ名
(source_page)・根拠URL(evidence_url)・そのページに表示されている
時刻表記そのまま(time_as_shown、無ければnull)をJSONで返してください。

実際にアクセスできなかったsource(試みたが失敗した、またはアクセス手段が
無かったもの)は、inaccessible_sourcesにその名前を列挙してください。
推測でテーマを作らないでください。"""

    response = call_luna(client, developer, user, schema=PROBE_SCHEMA,
                          web_search=True, stage="phase0_probe")
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    verdict = "PASS" if len(parsed["accessible_themes"]) >= 3 else "FAIL"
    result = {
        "t_now_jst": t_now.isoformat(),
        "t_cut_jst": t_cut.isoformat(),
        "accessible_themes": parsed["accessible_themes"],
        "inaccessible_sources": parsed["inaccessible_sources"],
        "accessible_theme_count": len(parsed["accessible_themes"]),
        "verdict": verdict,
    }
    save_json(path, result)
    save_json(out_path(out_dir, "prompts", "phase0_probe.json"),
               {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "phase0_probe.json"), meta)
    print(f"[OK] probe: accessible_theme_count={result['accessible_theme_count']} "
          f"verdict={verdict} model={meta['response_model_actual']}")
    if verdict == "FAIL":
        print("[STOP] Phase 0判定NG(3件未満)。Phase 1以降は実行しないこと。")


# ------------------------------------------------------------
# discover (Phase 1)
# ------------------------------------------------------------
def _candidate_schema(lane: str) -> dict:
    base_props = {
        "title": {"type": "string"},
        "source_name": {"type": "string"},
        "url": {"type": "string"},
        "published_time_as_shown": {"type": ["string", "null"]},
        "published_time_iso": {"type": ["string", "null"]},
        "time_uncertain": {"type": "boolean"},
        "summary_ja": {"type": "string"},
        "lane": {"type": "string"},
        "country_scope": {"type": "string"},
        "is_pr_or_ad": {"type": "boolean"},
    }
    base_required = list(base_props.keys())
    if lane == "sns":
        base_props.update({
            "signal_source": {"type": "string"},
            "signal_time_as_shown": {"type": ["string", "null"]},
            "confirm_source_url": {"type": ["string", "null"]},
        })
        base_required += ["signal_source", "signal_time_as_shown",
                           "confirm_source_url"]
    return {
        "type": "object",
        "properties": base_props,
        "required": base_required,
        "additionalProperties": False,
    }


def _discover_schema(lane: str) -> dict:
    return {
        "name": f"topic_discovery_{lane}",
        "schema": {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": _candidate_schema(lane),
                },
            },
            "required": ["candidates"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def cmd_discover(args):
    out_dir = args.out_dir
    lane = args.lane
    path = out_path(out_dir, f"phase1_{lane}.json")
    if skip_if_exists(path, args.force):
        return
    meta_run = load_run_meta(out_dir)
    install_logger(out_dir)
    client = get_client()

    lane_all_text = "\n".join(f"- {k}: {v}" for k, v in LANES.items())
    sns_note = ""
    if lane == "sns":
        sns_note = (
            "\n\nこのレーンはTrend/SNS Discoveryです。SNS・Trendページは"
            "Factの出典としてではなく、『今、日本人が何に反応しているか』を"
            "見つけるためのSignalとして使ってください。signal_source(どこで"
            "話題を検知したか・URL)、signal_time_as_shown(そこに表示されて"
            "いた時刻表記)に加え、可能な限り別の信頼できるsourceで実体を"
            "確認し、確認できたURLをconfirm_source_urlに入れてください。"
            "確認できなければconfirm_source_urlはnullのままにし、捏造しない"
            "でください。"
        )

    developer = (
        "あなたはNews Discovery担当です。web_searchツールで実際に見つけた"
        "記事・話題だけを報告してください。存在しない記事を作らないで"
        "ください。"
    )
    user = f"""現在の日時は {meta_run['t_now_jst']}(JST)です。
直近24時間の基準時刻(T_cut)は {meta_run['t_cut_jst']}(JST)です。
T_cutより前に公開された記事は候補にしないでください。公開時刻が
確認できない場合は無理に断定せず、time_uncertain: trueと正直に記して
ください。

【今回探索するレーン】
{lane}: {LANES[lane]}

【全レーン一覧(参考、今回はこのレーンだけを探索してください)】
{lane_all_text}

【目的】
{PURPOSE_SENTENCE}
{sns_note}

検索しやすい大手英語媒体だけに偏らず、日本語媒体・専門媒体・地方媒体も
対象にしてください。

このレーンで、直近24時間以内に公開・話題化した候補を10〜15件、JSONで
返してください。各候補について、title(原題)・source_name・url・
published_time_as_shown(ページ表示の時刻表記そのまま)・
published_time_iso(推定ISO8601、不明ならnull)・time_uncertain(bool)・
summary_ja(記事内容に基づく2〜3文)・lane(このレーン名 "{lane}" を
入れる)・country_scope(日本/世界/特定国名など)・is_pr_or_ad(広告/PR
記事らしければtrue)を埋めてください。"""

    response = call_luna(client, developer, user, schema=_discover_schema(lane),
                          web_search=True, stage=f"phase1_{lane}")
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    save_json(path, {"lane": lane, "candidates": parsed["candidates"]})
    save_json(out_path(out_dir, "prompts", f"phase1_{lane}.json"),
               {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", f"phase1_{lane}.json"), meta)
    print(f"[OK] discover[{lane}]: candidates={len(parsed['candidates'])} "
          f"model={meta['response_model_actual']}")


# ------------------------------------------------------------
# hooks (Phase 2)
# ------------------------------------------------------------
HOOKS_SCHEMA = {
    "name": "topic_hooks",
    "schema": {
        "type": "object",
        "properties": {
            "hooks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "hook_ja": {"type": "string"},
                        "hook_en": {"type": "string"},
                        "answer_sketch": {"type": "string"},
                        "beyond_article": {"type": "boolean"},
                        "beyond_evidence_url": {"type": ["string", "null"]},
                        "category": {
                            "type": "string",
                            "enum": ["AI/Tech", "Lifestyle", "Health", "Science",
                                     "Entertainment", "Sports", "Consumer",
                                     "Hard News", "Business/Economy",
                                     "Environment", "Other"],
                        },
                        "distance_to_japan": {
                            "type": "string",
                            "enum": ["近い", "中", "遠い"],
                        },
                        "distance_to_japan_reason": {"type": "string"},
                        "dedupe_group": {"type": "string"},
                    },
                    "required": ["candidate_id", "hook_ja", "hook_en",
                                 "answer_sketch", "beyond_article",
                                 "beyond_evidence_url", "category",
                                 "distance_to_japan",
                                 "distance_to_japan_reason", "dedupe_group"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["hooks"],
        "additionalProperties": False,
    },
    "strict": True,
}


def _merge_candidates_raw(out_dir: str) -> list:
    """5レーンのphase1_<lane>.jsonを機械的に結合し、candidate_idを連番で
    付与する(内容の取捨選択は行わない、重複URLもそのまま残す)。"""
    raw_path = out_path(out_dir, "candidates_raw.json")
    if os.path.exists(raw_path):
        return load_json(raw_path)["candidates"]
    merged = []
    cid = 0
    for lane in LANE_ORDER:
        lane_path = out_path(out_dir, f"phase1_{lane}.json")
        if not os.path.exists(lane_path):
            raise RuntimeError(f"phase1_{lane}.jsonが見つかりません。discover "
                                f"--lane {lane} を先に実行してください。")
        lane_data = load_json(lane_path)
        for c in lane_data["candidates"]:
            cid += 1
            c = dict(c)
            c["candidate_id"] = f"C{cid:03d}"
            merged.append(c)
    save_json(raw_path, {"candidates": merged, "total": len(merged)})
    return merged


def cmd_hooks(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "phase2_hooks.json")
    if skip_if_exists(path, args.force):
        return
    raw_candidates = _merge_candidates_raw(out_dir)
    install_logger(out_dir)
    client = get_client()

    # Lunaへ渡す簡潔な候補一覧(候補ごとの主要フィールドのみ)
    compact = [
        {
            "candidate_id": c["candidate_id"],
            "title": c["title"],
            "source_name": c["source_name"],
            "url": c["url"],
            "lane": c["lane"],
            "summary_ja": c["summary_ja"],
            "published_time_as_shown": c["published_time_as_shown"],
            "time_uncertain": c["time_uncertain"],
        }
        for c in raw_candidates
    ]

    developer = (
        "あなたはHook Writerです。記事に対応していないHookは禁止です。"
        "以下の4つの絶対条件を守ってください: "
        "(1) 釣りタイトル・誇張を禁止する。"
        "(2) 元記事では答えられない疑問を作らない。"
        "(3) Fact以上の断定をしない。"
        "(4) Hookの問いに対して、元News+追加Evidenceから実質的に答えられる"
        "必要がある。"
    )
    user = f"""以下は直近24時間の候補記事一覧です(candidate_idごとに1件)。
各候補について、日本人ユーザーが一瞬目を止め、聞きたくなるHookを作成して
ください。

【候補一覧】
{json.dumps(compact, ensure_ascii=False, indent=2)}

各候補(candidate_id)について、以下を埋めてJSONで返してください:
- hook_ja: 日本人が思わず聞きたくなる1文(問いの形でもよい)
- hook_en: 同内容の英語Hook
- answer_sketch: そのHookに記事内容で実質的に答えられることを示す
  1〜2文(記事に無い事実は書かない)
- beyond_article: Hookの答えに元記事以外のEvidenceが必要か(bool)
- beyond_evidence_url: 必要な場合、上記候補一覧のurlの中から選ぶ
  (無ければnull)
- category: AI/Tech・Lifestyle・Health・Science・Entertainment・Sports・
  Consumer・Hard News・Business/Economy・Environment・Otherのいずれか
- distance_to_japan: 近い/中/遠いのいずれか
- distance_to_japan_reason: そう判断した理由1文
- dedupe_group: 同一話題を指す候補には同じグループID文字列を付ける
  (話題が異なる場合は候補ごとに異なるID)

全candidate_idについて出力してください。"""

    response = call_luna(client, developer, user, schema=HOOKS_SCHEMA,
                          web_search=False, stage="phase2_hooks")
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    raw_by_id = {c["candidate_id"]: c for c in raw_candidates}
    hooks_by_id = {h["candidate_id"]: h for h in parsed["hooks"]}
    enriched = []
    not_covered = []
    for cid, raw in raw_by_id.items():
        if cid not in hooks_by_id:
            not_covered.append(cid)
            continue
        merged = dict(raw)
        merged.update(hooks_by_id[cid])
        enriched.append(merged)

    save_json(path, {"candidates": enriched, "not_covered_candidate_ids": not_covered,
                      "total_raw": len(raw_candidates), "total_hooked": len(enriched)})
    save_json(out_path(out_dir, "prompts", "phase2_hooks.json"),
               {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "phase2_hooks.json"), meta)
    print(f"[OK] hooks: total_raw={len(raw_candidates)} hooked={len(enriched)} "
          f"not_covered={len(not_covered)} model={meta['response_model_actual']}")


# ------------------------------------------------------------
# rank (Phase 3)
# ------------------------------------------------------------
RANK_SCHEMA = {
    "name": "topic_ranking",
    "schema": {
        "type": "object",
        "properties": {
            "selections": {
                "type": "array",
                "maxItems": 20,
                "items": {
                    "type": "object",
                    "properties": {
                        "rank": {"type": "integer"},
                        "candidate_id": {"type": "string"},
                        "selection_reason_ja": {"type": "string"},
                        "expected_listener_reaction": {"type": "string"},
                    },
                    "required": ["rank", "candidate_id", "selection_reason_ja",
                                 "expected_listener_reaction"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["selections"],
        "additionalProperties": False,
    },
    "strict": True,
}


def cmd_rank(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "phase3_ranked.json")
    if skip_if_exists(path, args.force):
        return
    hooks_data = load_json(out_path(out_dir, "phase2_hooks.json"))
    candidates = hooks_data["candidates"]
    install_logger(out_dir)
    client = get_client()

    compact = [
        {
            "candidate_id": c["candidate_id"],
            "title": c["title"],
            "source_name": c["source_name"],
            "lane": c["lane"],
            "summary_ja": c["summary_ja"],
            "hook_ja": c["hook_ja"],
            "hook_en": c["hook_en"],
            "category": c["category"],
            "distance_to_japan": c["distance_to_japan"],
            "distance_to_japan_reason": c["distance_to_japan_reason"],
            "beyond_article": c["beyond_article"],
            "beyond_evidence_url": c["beyond_evidence_url"],
            "time_uncertain": c["time_uncertain"],
            "dedupe_group": c["dedupe_group"],
            "is_pr_or_ad": c["is_pr_or_ad"],
            "country_scope": c["country_scope"],
        }
        for c in candidates
    ]

    developer = (
        "あなたはFinal Editorです。以下の条件をすべて守って最大20件を"
        "順位付きで選んでください。20件に満たない場合は無理に埋めず、"
        "実際に選べる数だけ返してください。"
    )
    user = f"""以下は各候補のHook付き情報です。

【選定条件】
- 日本人との距離: 特定国の国内事情だけで完結し、日本人との接点が薄い話題は
  優先度を下げる。ただし米中AI競争・世界的Technology変化・Energy・
  Climate・Science・国際的Consumer Trendなど、日本にも波及しうる大きな
  構図は積極的に残してよい。
- 求める特徴: 身近/生活に関係/実生活で少し役立つ/純粋に答えを知りたい/
  人に話したくなる/「へえ」/一瞬目が止まる/音声で説明しやすい/日本人との
  心理的距離が近い。政治・戦争・外交Newsばかりにしない。
- 俗っぽい・軽い話題も意図的に含める。広告・PR記事をそのまま英語化した
  だけのようなものは避ける(背景に一般化できる問いがあるものを優先)。
- Trend/SNS起点の話題は、今日新しく伸びたものを優先する。
- dedupe_groupが同じ候補は1件だけ選ぶこと。
- beyond_article: trueでbeyond_evidence_urlがnullの候補は選ばないこと。
- time_uncertain: trueの候補は選んでもよいが、選ぶ場合はその旨を
  selection_reason_jaに残すこと。

【候補一覧】
{json.dumps(compact, ensure_ascii=False, indent=2)}

上記条件に基づき、最大20件をrank(1が最上位)付きで選び、各選定について
candidate_id・selection_reason_ja(2〜3文)・expected_listener_reaction
(1文)を返してください。"""

    response = call_luna(client, developer, user, schema=RANK_SCHEMA,
                          web_search=False, stage="phase3_rank")
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    selections = sorted(parsed["selections"], key=lambda s: s["rank"])
    by_id = {c["candidate_id"]: c for c in candidates}
    resolved = []
    unresolved_ids = []
    for s in selections:
        c = by_id.get(s["candidate_id"])
        if c is None:
            unresolved_ids.append(s["candidate_id"])
            continue
        merged = dict(c)
        merged.update(s)
        resolved.append(merged)

    save_json(path, {
        "selections_raw": selections,
        "resolved": resolved,
        "unresolved_candidate_ids": unresolved_ids,
        "selected_count": len(resolved),
    })
    save_json(out_path(out_dir, "prompts", "phase3_rank.json"),
               {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "phase3_rank.json"), meta)
    print(f"[OK] rank: selected_count={len(resolved)} "
          f"unresolved={len(unresolved_ids)} model={meta['response_model_actual']}")


# ------------------------------------------------------------
# verify (Phase 4、スクリプトのみ、LLMなし)
# ------------------------------------------------------------
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; EigoRadioTopicTrialBot/1.0; "
                  "+research trial, non-production)"
}
HTTP_TIMEOUT = 15


def _fetch(url: str):
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT,
                             allow_redirects=True)
        return resp, None
    except Exception as exc:
        return None, str(exc)[:300]


def _extract_published_time(html: str):
    soup = BeautifulSoup(html, "html.parser")
    # 1) meta property=article:published_time / og:article:published_time
    for prop in ("article:published_time", "og:article:published_time",
                 "article:published"):
        tag = soup.find("meta", attrs={"property": prop})
        if tag and tag.get("content"):
            return tag["content"], f"meta[property={prop}]"
    # 2) meta name=pubdate/date/publish-date/sailthru.date
    for name in ("pubdate", "date", "publish-date", "sailthru.date",
                  "parsely-pub-date"):
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"], f"meta[name={name}]"
    # 3) JSON-LD datePublished
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
    # 4) <time datetime="...">
    time_tag = soup.find("time", attrs={"datetime": True})
    if time_tag and time_tag.get("datetime"):
        return time_tag["datetime"], "time[datetime]"
    return None, None


def _classify_time(verified_iso, t_cut_jst_iso, t_now_jst_iso):
    from dateutil import parser as dtparser
    t_cut = dtparser.isoparse(t_cut_jst_iso).astimezone(UTC)
    t_now = dtparser.isoparse(t_now_jst_iso).astimezone(UTC)
    tz_assumed = False
    try:
        dt = dtparser.parse(verified_iso)
    except Exception:
        return None, None, None, "unverifiable"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
        tz_assumed = True
    dt_utc = dt.astimezone(UTC)
    buffer = timedelta(hours=1)
    if dt_utc > t_now + buffer:
        return dt_utc.isoformat(), tz_assumed, None, "unverifiable"
    if dt_utc < t_cut:
        return dt_utc.isoformat(), tz_assumed, None, "older_than_24h"
    return dt_utc.isoformat(), tz_assumed, None, "within_24h"


def _check_url(url: str):
    resp, err = _fetch(url)
    if err is not None or resp is None:
        return {"reachable": False, "http_status": None, "error": err}
    return {"reachable": resp.status_code == 200, "http_status": resp.status_code,
            "error": None}


def cmd_verify(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "phase4_verify.json")
    if skip_if_exists(path, args.force):
        return
    ranked = load_json(out_path(out_dir, "phase3_ranked.json"))
    meta_run = load_run_meta(out_dir)
    t_cut_jst = meta_run["t_cut_jst"]
    t_now_jst = meta_run["t_now_jst"]

    results = []
    for c in ranked["resolved"]:
        url = c["url"]
        resp, err = _fetch(url)
        entry = {
            "candidate_id": c["candidate_id"],
            "rank": c["rank"],
            "url": url,
            "published_time_as_shown": c.get("published_time_as_shown"),
            "published_time_iso_declared": c.get("published_time_iso"),
            "time_uncertain_declared": c.get("time_uncertain"),
        }
        if err is not None or resp is None:
            entry.update({
                "http_status": None, "fetch_error": err,
                "published_time_verified": None, "verified_source_method": None,
                "tz_assumed_utc_for_naive": None,
                "classification": "http_error",
                "disqualified": True,
                "disqualify_reason": f"fetch_failed: {err}",
            })
        elif resp.status_code != 200:
            entry.update({
                "http_status": resp.status_code, "fetch_error": None,
                "published_time_verified": None, "verified_source_method": None,
                "tz_assumed_utc_for_naive": None,
                "classification": "http_error",
                "disqualified": True,
                "disqualify_reason": f"http_status={resp.status_code}",
            })
        else:
            raw_time, method = _extract_published_time(resp.text)
            if raw_time is None:
                entry.update({
                    "http_status": resp.status_code, "fetch_error": None,
                    "published_time_verified": None, "verified_source_method": None,
                    "tz_assumed_utc_for_naive": None,
                    "classification": "unverifiable",
                    "disqualified": False,
                    "disqualify_reason": None,
                })
            else:
                verified_iso, tz_assumed, _, classification = _classify_time(
                    raw_time, t_cut_jst, t_now_jst)
                disqualified = classification == "older_than_24h"
                entry.update({
                    "http_status": resp.status_code, "fetch_error": None,
                    "published_time_verified": verified_iso,
                    "verified_source_method": method,
                    "tz_assumed_utc_for_naive": tz_assumed,
                    "classification": classification,
                    "disqualified": disqualified,
                    "disqualify_reason": "older_than_24h" if disqualified else None,
                })

        # beyond_evidence_url到達性
        beyond_url = c.get("beyond_evidence_url")
        if c.get("beyond_article") and beyond_url:
            chk = _check_url(beyond_url)
            entry["beyond_evidence_url"] = beyond_url
            entry["beyond_evidence_reachable"] = chk["reachable"]
            entry["beyond_evidence_http_status"] = chk["http_status"]
        else:
            entry["beyond_evidence_url"] = beyond_url
            entry["beyond_evidence_reachable"] = None
            entry["beyond_evidence_http_status"] = None

        # confirm_source_url到達性(SNSレーン起点候補のみ存在)
        confirm_url = c.get("confirm_source_url")
        if confirm_url:
            chk = _check_url(confirm_url)
            entry["confirm_source_url"] = confirm_url
            entry["confirm_source_reachable"] = chk["reachable"]
            entry["confirm_source_http_status"] = chk["http_status"]
        else:
            entry["confirm_source_url"] = confirm_url
            entry["confirm_source_reachable"] = None
            entry["confirm_source_http_status"] = None
        entry["unconfirmed_sns_entity"] = bool(
            c.get("lane") == "sns" and not confirm_url)

        results.append(entry)

    disqualified_count = sum(1 for r in results if r["disqualified"])
    unverifiable_count = sum(1 for r in results if r["classification"] == "unverifiable")
    passed_count = sum(1 for r in results if not r["disqualified"])

    save_json(path, {
        "results": results,
        "total_checked": len(results),
        "disqualified_count": disqualified_count,
        "unverifiable_count": unverifiable_count,
        "passed_count": passed_count,
    })
    print(f"[OK] verify: checked={len(results)} disqualified={disqualified_count} "
          f"unverifiable={unverifiable_count} passed={passed_count}")


# ------------------------------------------------------------
# aggregate (Phase 5、スクリプトのみ)
# ------------------------------------------------------------
SOURCE_CLASSIFICATION_RULES = [
    ("海外通信社", ["Reuters", "AP", "Associated Press", "AFP", "Bloomberg"]),
    ("海外一般媒体", ["New York Times", "NYT", "BBC", "CNN", "Guardian",
                     "WSJ", "Wall Street Journal", "Washington Post",
                     "TechCrunch", "The Verge", "Forbes", "CNBC",
                     "Al Jazeera", "NPR", "Time", "USA Today"]),
    ("国内一般媒体", ["朝日新聞", "読売新聞", "毎日新聞", "日本経済新聞",
                     "日経", "NHK", "産経新聞", "時事通信", "共同通信",
                     "Kyodo", "ライブドアニュース", "TBS", "日テレ",
                     "フジテレビ", "テレビ朝日", "テレ朝", "ABEMA",
                     "ORICON"]),
    ("国内専門/業界媒体", ["ITmedia", "Impress", "Response", "GIGAZINE",
                          "日経クロステック", "日経XTECH", "ねとらぼ",
                          "Engadget", "ASCII", "Impress Watch",
                          "ハフポスト", "Business Insider Japan"]),
]


def classify_source(source_name: str, lane: str) -> str:
    import re
    name = source_name or ""
    for category, keywords in SOURCE_CLASSIFICATION_RULES:
        for kw in keywords:
            if re.search(r"[A-Za-z]", kw):
                # 英字キーワードは単語境界で厳密一致させる(例: "AP"が
                # "Japan.co.jp"へ部分一致してしまう誤分類を防ぐ)。
                if re.search(r"(?<![A-Za-z0-9])" + re.escape(kw) +
                             r"(?![A-Za-z0-9])", name, flags=re.IGNORECASE):
                    return category
            elif kw in name:
                return category
    if lane == "sns":
        return "SNS起点"
    return "その他"


def cmd_aggregate(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "phase5_aggregate.json")
    if skip_if_exists(path, args.force):
        return
    raw = load_json(out_path(out_dir, "candidates_raw.json"))
    hooks = load_json(out_path(out_dir, "phase2_hooks.json"))
    ranked = load_json(out_path(out_dir, "phase3_ranked.json"))
    verify = load_json(out_path(out_dir, "phase4_verify.json"))

    phase1_total = raw["total"]
    dedupe_groups = {c["dedupe_group"] for c in hooks["candidates"]}
    phase2_dedupe_count = len(dedupe_groups)
    phase3_selected_count = ranked["selected_count"]
    phase4_passed_count = verify["passed_count"]

    lane_distribution_raw = {}
    for c in raw["candidates"]:
        lane_distribution_raw[c["lane"]] = lane_distribution_raw.get(c["lane"], 0) + 1

    final = ranked["resolved"]
    verify_by_id = {r["candidate_id"]: r for r in verify["results"]}

    source_dist = {}
    category_dist = {}
    lane_dist_final = {}
    distance_dist = {}
    time_uncertain_count = 0
    beyond_article_count = 0
    unconfirmed_sns_count = 0

    for c in final:
        src_cat = classify_source(c.get("source_name", ""), c.get("lane", ""))
        source_dist[src_cat] = source_dist.get(src_cat, 0) + 1
        category_dist[c["category"]] = category_dist.get(c["category"], 0) + 1
        lane_dist_final[c["lane"]] = lane_dist_final.get(c["lane"], 0) + 1
        distance_dist[c["distance_to_japan"]] = distance_dist.get(
            c["distance_to_japan"], 0) + 1
        if c.get("time_uncertain"):
            time_uncertain_count += 1
        if c.get("beyond_article"):
            beyond_article_count += 1
        v = verify_by_id.get(c["candidate_id"], {})
        if v.get("unconfirmed_sns_entity"):
            unconfirmed_sns_count += 1

    result = {
        "funnel": {
            "phase1_total_raw": phase1_total,
            "phase2_dedupe_group_count": phase2_dedupe_count,
            "phase3_selected_count": phase3_selected_count,
            "phase4_passed_count": phase4_passed_count,
        },
        "lane_distribution_raw_phase1": lane_distribution_raw,
        "final_selection": {
            "source_distribution": source_dist,
            "category_distribution": category_dist,
            "lane_distribution": lane_dist_final,
            "distance_to_japan_distribution": distance_dist,
            "time_uncertain_count": time_uncertain_count,
            "beyond_article_count": beyond_article_count,
            "unconfirmed_sns_entity_count": unconfirmed_sns_count,
            "total_final": len(final),
        },
        "source_classification_rules": SOURCE_CLASSIFICATION_RULES,
    }
    save_json(path, result)
    print(f"[OK] aggregate: funnel={result['funnel']}")


# ------------------------------------------------------------
# cost
# ------------------------------------------------------------
def _price(pricing, provider, model, meter):
    return next(p["price"] for p in pricing
                if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter)


def cmd_cost(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "cost.json")
    if skip_if_exists(path, args.force):
        return
    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]
    luna_in = _price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = _price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = _price(pricing, "openai", "gpt-5.6-luna", "output_tokens")
    ws_price = _price(pricing, "openai", "N/A (tool, all models)", "web_search_call")
    usd_to_jpy = 160

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
    total_input = 0
    total_cached = 0
    total_output = 0
    for e in entries:
        if e.get("provider") != "openai" or not e.get("success", True):
            continue
        stage = e.get("stage") or "unknown"
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        ws = e.get("web_search_call_count") or 0
        billable_in = max(it - ct, 0)
        usd = (billable_in / 1_000_000) * luna_in + (ct / 1_000_000) * luna_cached \
            + (ot / 1_000_000) * luna_out + (ws / 1000) * ws_price
        s = by_stage.setdefault(stage, {"calls": 0, "input_tokens": 0,
                                          "cached_input_tokens": 0,
                                          "output_tokens": 0,
                                          "web_search_call_count": 0, "usd": 0.0})
        s["calls"] += 1
        s["input_tokens"] += it
        s["cached_input_tokens"] += ct
        s["output_tokens"] += ot
        s["web_search_call_count"] += ws
        s["usd"] += usd
        total_usd += usd
        total_calls += 1
        total_ws_calls += ws
        total_input += it
        total_cached += ct
        total_output += ot

    by_stage_jpy = {
        stage: {**vals, "jpy": round(vals["usd"] * usd_to_jpy, 1)}
        for stage, vals in by_stage.items()
    }
    result = {
        "by_stage": by_stage_jpy,
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * usd_to_jpy, 1),
        "total_openai_calls": total_calls,
        "total_internal_web_search_call_count": total_ws_calls,
        "total_input_tokens": total_input,
        "total_cached_input_tokens": total_cached,
        "total_output_tokens": total_output,
        "usd_to_jpy": usd_to_jpy,
        "note": "web_search明示呼び出し回数(Sonnetが発行したresponses.create"
                "呼び出し数)はraw_responses/配下のファイル数から数える。"
                "internal_web_search_call_countはモデルが自律的に行った"
                "内部検索回数(制御不能、記録のみ)。",
    }
    save_json(path, result)
    print(f"[OK] cost: total_jpy={result['total_jpy']} calls={total_calls} "
          f"internal_ws={total_ws_calls}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe")
    p_probe.add_argument("--out-dir", required=True)
    p_probe.add_argument("--max-calls", type=int, default=2)
    p_probe.add_argument("--force", action="store_true")
    p_probe.set_defaults(func=cmd_probe)

    p_discover = sub.add_parser("discover")
    p_discover.add_argument("--out-dir", required=True)
    p_discover.add_argument("--lane", required=True, choices=list(LANES.keys()))
    p_discover.add_argument("--force", action="store_true")
    p_discover.set_defaults(func=cmd_discover)

    p_hooks = sub.add_parser("hooks")
    p_hooks.add_argument("--out-dir", required=True)
    p_hooks.add_argument("--force", action="store_true")
    p_hooks.set_defaults(func=cmd_hooks)

    p_rank = sub.add_parser("rank")
    p_rank.add_argument("--out-dir", required=True)
    p_rank.add_argument("--force", action="store_true")
    p_rank.set_defaults(func=cmd_rank)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("--out-dir", required=True)
    p_verify.add_argument("--force", action="store_true")
    p_verify.set_defaults(func=cmd_verify)

    p_aggregate = sub.add_parser("aggregate")
    p_aggregate.add_argument("--out-dir", required=True)
    p_aggregate.add_argument("--force", action="store_true")
    p_aggregate.set_defaults(func=cmd_aggregate)

    p_cost = sub.add_parser("cost")
    p_cost.add_argument("--out-dir", required=True)
    p_cost.add_argument("--force", action="store_true")
    p_cost.set_defaults(func=cmd_cost)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
