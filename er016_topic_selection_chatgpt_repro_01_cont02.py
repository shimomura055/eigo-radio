# ============================================================
# er016_topic_selection_chatgpt_repro_01_cont02.py
# TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02 (Fable設計、2026-09-24)
# ============================================================
# 目的: REPRO-01の続行。Reference 20件(ChatGPT側)との差分を「検索」
# 「選定」「Hook」に分離して検証するRound 1診断Trial。新Selector開発では
# ない。**Production実装ではない。** Production正式path(daily runner・
# er011_*/er014_*等)は一切変更しない。
#
# 禁止事項(委任文より): Reference 20件の素材・Hook・ユーザー評価点を
# Search/Selection/Hook生成のPromptに入れない(Hook Test H1/H2の入力は
# 「Reference素材の概要」のみ可、Hook・評価点は不可)。人間・Sonnetによる
# Topic追加・救済・Hook修正・順位差し替えは行わない。
#
# 再利用: er016_topic_selection_chatgpt_repro_01.py (base) をimportし、
# ヘルパー関数・スキーマ・REFERENCE_20定数等を再利用する。baseファイル
# 自体は変更しない。
#
# サブコマンド: interest_words / search_a --group 1..4 / feedback_round /
#   search_b --lane 1|2 / select --which sel1|sel2 / hooks_new / verify /
#   final_new / hook_test --which h1|h2 / aggregate / cost
# 冪等性: 出力ファイルが既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from urllib.parse import urlparse

import er016_topic_selection_chatgpt_repro_01 as base

THEME_TAG = "TOPIC_SELECTION_CHATGPT_REPRO_01_CONT02"
MODEL_LUNA = base.MODEL_LUNA
EFFORT_DEFAULT = "medium"
WEB_SEARCH_BUDGET = 7  # Search Test A=5(初回4+Feedback 1) + Search Test B=2
REPRO01_OUT_DIR = "er016_output/topic_selection_chatgpt_repro_01"

out_path = base.out_path
save_json = base.save_json
load_json = base.load_json
skip_if_exists = base.skip_if_exists


# ------------------------------------------------------------
# ヘルパー(base流用+CONT-02固有)
# ------------------------------------------------------------
def _ensure_run_meta(out_dir: str, window_start: str, window_end: str) -> dict:
    path = base.run_meta_path(out_dir)
    if os.path.exists(path):
        return load_json(path)
    os.makedirs(out_dir, exist_ok=True)
    meta = {
        "search_index_as_of_jst": datetime.now(base.JST).isoformat(),
        "window_start_jst": window_start,
        "window_end_jst": window_end,
        "model": MODEL_LUNA,
        "effort": EFFORT_DEFAULT,
        "note": "CONT-02: probeコマンドは無く、REPRO-01と同一の固定窓を"
                "window引数からそのままrun_meta.jsonへ書き込む。",
    }
    save_json(path, meta)
    return meta


def log_web_search_call(out_dir: str, stage: str) -> None:
    path = out_path(out_dir, "web_search_log.json")
    entries = []
    if os.path.exists(path):
        entries = load_json(path)
    entries.append({"stage": stage, "logged_at_jst": datetime.now(base.JST).isoformat()})
    save_json(path, entries)
    print(f"[web_search_log] total_explicit_calls={len(entries)} / budget={WEB_SEARCH_BUDGET}")


def call_model(client, developer: str, user: str, schema=None, web_search=False,
                stage="", model=None, effort=None, out_dir=None, retried=False):
    """1回のAPI技術的retryのみを許可する(品質理由の再実行は禁止)。"""
    model = model or MODEL_LUNA
    effort = effort or EFFORT_DEFAULT
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
        with base.cl.logging_context(THEME_TAG, stage):
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
    if web_search and out_dir is not None:
        log_web_search_call(out_dir, stage)
    return response


def _candidate_schema() -> dict:
    props = {
        "title": {"type": "string"},
        "source_name": {"type": "string"},
        "url": {"type": "string"},
        "published_time_as_shown": {"type": ["string", "null"]},
        "published_time_iso": {"type": ["string", "null"]},
        "time_uncertain": {"type": "boolean"},
        "summary_ja": {"type": "string"},
        "country_scope": {"type": "string"},
        "is_pr_or_ad": {"type": "boolean"},
        "query_used": {"type": "string"},
    }
    return {"type": "object", "properties": props, "required": list(props.keys()),
            "additionalProperties": False}


def _candidates_schema(name: str) -> dict:
    return {
        "name": name,
        "schema": {
            "type": "object",
            "properties": {"candidates": {"type": "array", "items": _candidate_schema()}},
            "required": ["candidates"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def _merge_pool_new(out_dir: str) -> list:
    path = out_path(out_dir, "pool_new.json")
    if os.path.exists(path):
        return load_json(path)["candidates"]
    merged = []
    cid = 0
    stage_files = [
        ("a1", "a1.json"), ("a2", "a2.json"), ("a3", "a3.json"), ("a4", "a4.json"),
        ("a5", "a5_feedback.json"), ("b1", "b1.json"), ("b2", "b2.json"),
    ]
    for stage, fname in stage_files:
        fpath = out_path(out_dir, fname)
        if not os.path.exists(fpath):
            raise RuntimeError(f"{fpath}が見つかりません。先に{stage}系コマンドを実行してください。")
        data = load_json(fpath)
        meta_stage = "a5_search" if stage == "a5" else stage
        meta_path = out_path(out_dir, "raw_responses", f"{meta_stage}.json")
        cited = set()
        if os.path.exists(meta_path):
            meta = load_json(meta_path)
            cited = {s["url"] for s in meta.get("sources", []) if s.get("url")}
        for c in data["candidates"]:
            cid += 1
            c = dict(c)
            c["candidate_id"] = f"D{cid:03d}"
            c["source_stage"] = stage
            c["url_in_citations"] = c.get("url") in cited
            merged.append(c)
    save_json(path, {"candidates": merged, "total": len(merged)})
    return merged


LIFE_DOMAIN_HINT = (
    "日本人の関心は、食べ物/コンビニ/睡眠/バッグ/旅行荷物/美容/香り/"
    "働き方/家庭/SNS流行/新商品/変わったサービス/若者文化等、具体的な"
    "生活領域に宿っていることが多く、抽象的なカテゴリ語(例:「AI」"
    "「経済」)で検索すると上位大手媒体の記事に寄りがちです。"
)

SELECTION_CRITERIA_SENTENCE = (
    "聞き手が反応するのは、意外な逆転/答えを知りたくなる問い/自分事になる"
    "/日常の小さな謎/世界の変化を一言で理解できる切り口/人に話したくなる"
    "/少し俗っぽい/『そう言われると確かに気になる』。身近さだけを軸に"
    "しない。重要なニュースであることや、技術的に新しいことや、軽いこと"
    "は、それだけでは理由にならない。"
)

HOOK_INSTRUCTION_MIKATA = """【Hookの作り方】
記事見出しをそのまま疑問形にしないでください。まず、この出来事のどこが
人間にとって意外・身近・逆説的・気になるのかを考えてください。その
「面白い見方」からHookを作ってください。

【絶対条件】
(1) 釣りタイトル・誇張を禁止する。
(2) 元記事では答えられない疑問を作らない。
(3) Fact以上の断定をしない。
(4) Hookの問いに対して、元News内容から実質的に答えられる必要がある。
answer_in_sourceには、そのHookに記事内容で実質的に答えられる箇所の要約を
1〜2文で書いてください。記事内容で答えられない場合は、answer_in_source
に文字列 "NOT_IN_SOURCE" とだけ書いてください。"""

REFERENCE_MATERIALS_ONLY = [
    {"reference_id": r["id"], "topic_ja": r["topic_ja"]} for r in base.REFERENCE_20
]


# ------------------------------------------------------------
# interest_words (A-0)
# ------------------------------------------------------------
A0_SCHEMA = {
    "name": "a0_interest_words",
    "schema": {
        "type": "object",
        "properties": {
            "words": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "word": {"type": "string"},
                        "why_now_ja": {"type": "string"},
                    },
                    "required": ["word", "why_now_ja"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["words"],
        "additionalProperties": False,
    },
    "strict": True,
}


def cmd_interest_words(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "a0_interest_words.json")
    if skip_if_exists(path, args.force):
        return
    os.makedirs(out_dir, exist_ok=True)
    base.install_logger(out_dir)
    client = base.get_client()

    developer = (
        "あなたは日本の生活者の関心を洞察する調査担当です。この工程では"
        "検索は行わず、関心語のリストだけを作成してください。"
    )
    user = f"""2026年9月23日の日本で、人が「ちょっと知りたい」と思いそうな、
具体的な生活語・関心語を40個作ってください。

固定辞書やカテゴリを均等に埋めることが目的ではありません。次の考え方を
"思想"として持ってください。

{LIFE_DOMAIN_HINT}

その具体レベルまで掘り下げた語を作ってください。各語について、
word(その関心語自体、具体的な名詞句)と、why_now_ja(なぜ今それを
知りたいと思われるか、1文)を、JSONでちょうど40件返してください。"""

    response = call_model(client, developer, user, schema=A0_SCHEMA, web_search=False,
                           stage="a0_interest_words", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = base.response_meta(response, user, developer)
    words = parsed["words"]
    save_json(path, {"words": words, "count": len(words)})
    save_json(out_path(out_dir, "prompts", "a0.json"), {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "a0.json"), meta)
    print(f"[OK] interest_words: count={len(words)} model={meta['response_model_actual']}")


# ------------------------------------------------------------
# search_a --group 1..4 (A-1〜A-4)
# ------------------------------------------------------------
def cmd_search_a(args):
    out_dir = args.out_dir
    group = args.group
    path = out_path(out_dir, f"a{group}.json")
    if skip_if_exists(path, args.force):
        return
    words = load_json(out_path(out_dir, "a0_interest_words.json"))["words"]
    start = (group - 1) * 10
    group_words = words[start:start + 10]
    meta_run = _ensure_run_meta(out_dir, args.window_start, args.window_end)
    base.install_logger(out_dir)
    client = base.get_client()

    developer = (
        "あなたはNews/話題のDiscovery担当です。web_searchツールで実際に"
        "見つけた記事・話題・商品ページ・投稿だけを報告してください。"
        "存在しない記事やURLを作らないでください。候補のurlは検索結果の"
        "引用に実際に現れたURLのみを使用してください。"
    )
    user = f"""対象窓(JST、固定): {meta_run['window_start_jst']} 〜 {meta_run['window_end_jst']}
この窓に公開・話題化した記事・商品ページ・投稿を、以下の関心語を手がかり
に探してください。関心語ごとに検索し、見つかった候補にはquery_used
(実際に使った検索語)を記録してください。

【今回の関心語(グループ{group}、なぜ今知りたいかの理由付き)】
{json.dumps(group_words, ensure_ascii=False, indent=2)}

窓より前や後に公開されたものは候補にしないでください。公開時刻が確認
できない場合はtime_uncertain: trueとしてください。日本語媒体を優先し、
英語媒体も含めてかまいません。

12〜15件、JSONで返してください。各候補についてtitle・source_name・url
(検索結果の引用に現れたURLのみ)・published_time_as_shown・
published_time_iso(不明ならnull)・time_uncertain・summary_ja(2〜3文)・
country_scope・is_pr_or_ad・query_usedを埋めてください。"""

    response = call_model(client, developer, user, schema=_candidates_schema(f"step_a{group}"),
                           web_search=True, stage=f"a{group}", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = base.response_meta(response, user, developer)
    save_json(path, {"group": group, "words": group_words, "candidates": parsed["candidates"]})
    save_json(out_path(out_dir, "prompts", f"a{group}.json"), {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", f"a{group}.json"), meta)
    print(f"[OK] search_a[group={group}]: candidates={len(parsed['candidates'])} "
          f"model={meta['response_model_actual']}")


# ------------------------------------------------------------
# feedback_round (A-5: 自己診断1回+追加検索1回)
# ------------------------------------------------------------
A5_DIAG_SCHEMA = {
    "name": "a5_feedback_diagnosis",
    "schema": {
        "type": "object",
        "properties": {
            "diagnosis_ja": {"type": "string"},
            "missing_types": {"type": "array", "items": {"type": "string"}},
            "additional_queries": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["diagnosis_ja", "missing_types", "additional_queries"],
        "additionalProperties": False,
    },
    "strict": True,
}


def cmd_feedback_round(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "a5_feedback.json")
    if skip_if_exists(path, args.force):
        return
    all_candidates = []
    for g in range(1, 5):
        data = load_json(out_path(out_dir, f"a{g}.json"))
        for c in data["candidates"]:
            all_candidates.append({
                "title": c["title"], "source_name": c["source_name"],
                "summary_ja": c["summary_ja"], "query_used": c["query_used"], "group": g,
            })
    meta_run = _ensure_run_meta(out_dir, args.window_start, args.window_end)
    base.install_logger(out_dir)
    client = base.get_client()

    diag_developer = (
        "あなたは調査の自己診断担当です。この工程では検索は行わず、既に"
        "得られた候補一覧だけを見て、不足しているタイプを診断してください。"
    )
    diag_user = f"""以下は先ほどの検索(4グループ)で得られた候補一覧です。

【候補一覧】
{json.dumps(all_candidates, ensure_ascii=False, indent=2)}

これらの候補のタイプ(例: 意外な逆転が起きている話題、日常の小さな謎、
新商品・新サービス、SNS発の話題、俗っぽい話題、その他)を見て、不足して
いると考えられるタイプがあれば診断してください。

diagnosis_ja(2〜4文)に診断内容を書き、missing_typesに不足していると
考えるタイプを短い語で列挙し、additional_queriesにその不足を埋めるため
の具体的な検索語を10個作ってください。"""

    diag_response = call_model(client, diag_developer, diag_user, schema=A5_DIAG_SCHEMA,
                                web_search=False, stage="a5_diagnosis", out_dir=out_dir)
    diag_parsed = json.loads(diag_response.output_text)
    diag_meta = base.response_meta(diag_response, diag_user, diag_developer)
    save_json(out_path(out_dir, "prompts", "a5_diagnosis.json"),
              {"developer": diag_developer, "user": diag_user})
    save_json(out_path(out_dir, "raw_responses", "a5_diagnosis.json"), diag_meta)

    queries = diag_parsed["additional_queries"][:10]
    search_developer = (
        "あなたはNews/話題のDiscovery担当です。web_searchツールで実際に"
        "見つけた記事・話題・商品ページ・投稿だけを報告してください。"
        "存在しない記事やURLを作らないでください。"
    )
    search_user = f"""対象窓(JST、固定): {meta_run['window_start_jst']} 〜 {meta_run['window_end_jst']}
先ほどの自己診断で不足していると判断した以下の検索語で、この窓内の候補
を追加で探してください。

【追加検索語】
{json.dumps(queries, ensure_ascii=False, indent=2)}

窓より前や後に公開されたものは候補にしないでください。12〜15件、JSONで
返してください。各候補にtitle・source_name・url・published_time_as_shown
・published_time_iso・time_uncertain・summary_ja・country_scope・
is_pr_or_ad・query_usedを埋めてください。"""

    search_response = call_model(client, search_developer, search_user,
                                  schema=_candidates_schema("a5_search"),
                                  web_search=True, stage="a5_search", out_dir=out_dir)
    search_parsed = json.loads(search_response.output_text)
    search_meta = base.response_meta(search_response, search_user, search_developer)
    save_json(out_path(out_dir, "prompts", "a5_search.json"),
              {"developer": search_developer, "user": search_user})
    save_json(out_path(out_dir, "raw_responses", "a5_search.json"), search_meta)

    save_json(path, {
        "diagnosis_ja": diag_parsed["diagnosis_ja"],
        "missing_types": diag_parsed["missing_types"],
        "additional_queries": queries,
        "candidates": search_parsed["candidates"],
    })
    print(f"[OK] feedback_round: missing_types={diag_parsed['missing_types']} "
          f"new_candidates={len(search_parsed['candidates'])} "
          f"model={search_meta['response_model_actual']}")


# ------------------------------------------------------------
# search_b --lane 1|2
# ------------------------------------------------------------
def cmd_search_b(args):
    out_dir = args.out_dir
    lane = args.lane
    path = out_path(out_dir, f"b{lane}.json")
    if skip_if_exists(path, args.force):
        return
    meta_run = _ensure_run_meta(out_dir, args.window_start, args.window_end)
    base.install_logger(out_dir)
    client = base.get_client()

    if lane == 1:
        lane_desc = "SNSで話題になった出来事を記事にしている国内媒体、または生活・消費・商品を扱う国内媒体"
    else:
        lane_desc = "新商品・新サービス・プレスリリース・変わったサービス"

    developer = (
        "あなたはNews/話題のDiscovery担当です。web_searchツールで実際に"
        "見つけた記事・話題・投稿だけを報告してください。特定の媒体名を"
        "あらかじめ想定せず、幅広く探索してください。"
    )
    user = f"""対象窓(JST、固定): {meta_run['window_start_jst']} 〜 {meta_run['window_end_jst']}
この窓に公開・話題化した、{lane_desc}を対象に探してください。

12〜15件、JSONで返してください。各候補にtitle・source_name・url
(検索結果の引用に現れたURLのみ)・published_time_as_shown・
published_time_iso(不明ならnull)・time_uncertain・summary_ja(2〜3文)・
country_scope・is_pr_or_ad・query_used(実際に使った検索語)を埋めて
ください。"""

    response = call_model(client, developer, user, schema=_candidates_schema(f"step_b{lane}"),
                           web_search=True, stage=f"b{lane}", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = base.response_meta(response, user, developer)
    save_json(path, {"lane": lane, "candidates": parsed["candidates"]})
    save_json(out_path(out_dir, "prompts", f"b{lane}.json"), {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", f"b{lane}.json"), meta)
    print(f"[OK] search_b[lane={lane}]: candidates={len(parsed['candidates'])} "
          f"model={meta['response_model_actual']}")


# ------------------------------------------------------------
# select --which sel1|sel2
# ------------------------------------------------------------
SEL1_SCHEMA = {
    "name": "sel1_selection",
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
                        "reason_ja": {"type": "string"},
                    },
                    "required": ["rank", "candidate_id", "reason_ja"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["selections"],
        "additionalProperties": False,
    },
    "strict": True,
}

SEL2_SCHEMA = {
    "name": "sel2_selection",
    "schema": {
        "type": "object",
        "properties": {
            "selections": {
                "type": "array",
                "maxItems": 40,
                "items": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "dedupe_group": {"type": "string"},
                        "reason_ja": {"type": "string"},
                    },
                    "required": ["candidate_id", "dedupe_group", "reason_ja"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["selections"],
        "additionalProperties": False,
    },
    "strict": True,
}


def cmd_select(args):
    out_dir = args.out_dir
    which = args.which
    path = out_path(out_dir, f"{which}.json")
    if skip_if_exists(path, args.force):
        return
    base.install_logger(out_dir)
    client = base.get_client()

    if which == "sel1":
        prev_hooks = load_json(out_path(REPRO01_OUT_DIR, "stepC_hooks.json"))["candidates"]
        compact = [{
            "candidate_id": c["candidate_id"], "title": c["title"], "source_name": c["source_name"],
            "summary_ja": c["summary_ja"], "hook_ja": c["hook_ja"], "category": c["category"],
            "distance_to_japan": c["distance_to_japan"], "dedupe_group": c["dedupe_group"],
            "is_pr_or_ad": c["is_pr_or_ad"], "country_scope": c["country_scope"],
        } for c in prev_hooks]
        developer = "あなたはNews素材の選定担当です。以下の基準だけで判断してください。"
        user = f"""以下は前回のTrialで得られた40件の候補(Hook付き)です。

【選定基準】
{SELECTION_CRITERIA_SENTENCE}

【候補一覧】
{json.dumps(compact, ensure_ascii=False, indent=2)}

この基準で20件を順位付き(rank、1が最上位)で選んでください。
dedupe_groupが同じ候補は1件だけ選んでください。各選定についてrank・
candidate_id・reason_ja(1〜2文)を返してください。"""

        response = call_model(client, developer, user, schema=SEL1_SCHEMA, web_search=False,
                               stage="sel1", out_dir=out_dir)
        parsed = json.loads(response.output_text)
        meta = base.response_meta(response, user, developer)
        selections = sorted(parsed["selections"], key=lambda s: s["rank"])
        new_ids = {s["candidate_id"] for s in selections}
        prev_final = load_json(out_path(REPRO01_OUT_DIR, "stepE_final_fix01.json"))["resolved"]
        prev_ids = {c["candidate_id"] for c in prev_final}
        added = sorted(new_ids - prev_ids)
        removed = sorted(prev_ids - new_ids)
        kept = sorted(new_ids & prev_ids)
        save_json(path, {
            "selections": selections, "selected_count": len(selections),
            "swap_vs_fix01": {
                "added": added, "removed": removed, "kept": kept,
                "added_count": len(added), "removed_count": len(removed), "kept_count": len(kept),
            },
        })
        save_json(out_path(out_dir, "prompts", "sel1.json"), {"developer": developer, "user": user})
        save_json(out_path(out_dir, "raw_responses", "sel1.json"), meta)
        print(f"[OK] select[sel1]: selected={len(selections)} swap_added={len(added)} "
              f"swap_removed={len(removed)} model={meta['response_model_actual']}")

    elif which == "sel2":
        pool = _merge_pool_new(out_dir)
        compact = [{
            "candidate_id": c["candidate_id"], "title": c["title"], "source_name": c["source_name"],
            "summary_ja": c["summary_ja"], "country_scope": c["country_scope"],
            "is_pr_or_ad": c["is_pr_or_ad"], "source_stage": c["source_stage"],
        } for c in pool]
        developer = (
            "あなたはNews素材の選定担当です。以下の基準だけで『素材として"
            "面白くなり得るか』を判断してください。"
        )
        user = f"""以下は今回のSearch Test A・Bで見つかった全候補です(重複含む)。

【選定基準】
{SELECTION_CRITERIA_SENTENCE}

【候補一覧】
{json.dumps(compact, ensure_ascii=False, indent=2)}

上記基準で『素材として面白くなり得る』候補を最大40件選んでください。
同一の話題・出来事を指す候補には同じdedupe_group文字列を、話題が異なる
候補には異なるdedupe_groupを付けてください。各選定についてcandidate_id
・dedupe_group・reason_jaを返してください。"""

        response = call_model(client, developer, user, schema=SEL2_SCHEMA, web_search=False,
                               stage="sel2", out_dir=out_dir)
        parsed = json.loads(response.output_text)
        meta = base.response_meta(response, user, developer)
        save_json(path, {"selections": parsed["selections"], "selected_count": len(parsed["selections"]),
                          "total_raw": len(pool)})
        save_json(out_path(out_dir, "prompts", "sel2.json"), {"developer": developer, "user": user})
        save_json(out_path(out_dir, "raw_responses", "sel2.json"), meta)
        print(f"[OK] select[sel2]: total_raw={len(pool)} selected={len(parsed['selections'])} "
              f"model={meta['response_model_actual']}")
    else:
        raise ValueError(f"unknown --which: {which}")


# ------------------------------------------------------------
# hooks_new
# ------------------------------------------------------------
def cmd_hooks_new(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "hooks_new.json")
    if skip_if_exists(path, args.force):
        return
    pool = {c["candidate_id"]: c for c in _merge_pool_new(out_dir)}
    sel2 = load_json(out_path(out_dir, "sel2.json"))["selections"]
    base.install_logger(out_dir)
    client = base.get_client()

    compact = []
    for s in sel2:
        c = pool.get(s["candidate_id"])
        if c is None:
            continue
        compact.append({
            "candidate_id": c["candidate_id"], "title": c["title"], "source_name": c["source_name"],
            "url": c["url"], "summary_ja": c["summary_ja"],
            "published_time_as_shown": c["published_time_as_shown"], "time_uncertain": c["time_uncertain"],
        })

    developer = "あなたはHook Writerです。記事に対応していないHookは禁止です。"
    user = f"""以下はSelection Test(SEL-2)で選ばれた候補一覧です。各候補に
ついて、日本人ユーザーが一瞬目を止め、聞きたくなるHookを作成してください。

{HOOK_INSTRUCTION_MIKATA}

【候補一覧】
{json.dumps(compact, ensure_ascii=False, indent=2)}

各候補(candidate_id)についてhook_ja・hook_en・answer_in_source・
category(AI/Tech・Lifestyle・Health・Science・Entertainment・Sports・
Consumer・Hard News・Business/Economy・Environment・Otherのいずれか)・
distance_to_japan(近い/中/遠いのいずれか)・distance_to_japan_reason
(1文)を埋めてJSONで返してください。全candidate_idについて出力して
ください。"""

    response = call_model(client, developer, user, schema=base.STEP_C_SCHEMA, web_search=False,
                           stage="hooks_new", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = base.response_meta(response, user, developer)

    sel_by_id = {s["candidate_id"]: s for s in sel2}
    hooks_by_id = {h["candidate_id"]: h for h in parsed["hooks"]}
    enriched = []
    not_covered = []
    for cid, sel in sel_by_id.items():
        raw = pool.get(cid)
        hook = hooks_by_id.get(cid)
        if raw is None or hook is None:
            not_covered.append(cid)
            continue
        merged = dict(raw)
        merged["dedupe_group"] = sel["dedupe_group"]
        merged["select_reason_ja"] = sel["reason_ja"]
        merged.update(hook)
        enriched.append(merged)

    save_json(path, {"candidates": enriched, "not_covered_candidate_ids": not_covered,
                      "total_selected": len(sel2), "total_hooked": len(enriched)})
    save_json(out_path(out_dir, "prompts", "hooks_new.json"), {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "hooks_new.json"), meta)
    print(f"[OK] hooks_new: total_selected={len(sel2)} hooked={len(enriched)} "
          f"not_covered={len(not_covered)} model={meta['response_model_actual']}")


# ------------------------------------------------------------
# verify (verify_new、スクリプトのみ、LLMなし。base._classify_*を流用)
# ------------------------------------------------------------
def cmd_verify(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "verify_new.json")
    if skip_if_exists(path, args.force):
        return
    apply_citation_rule = not args.no_citation_rule
    hooked = load_json(out_path(out_dir, "hooks_new.json"))["candidates"]
    meta_run = _ensure_run_meta(out_dir, args.window_start, args.window_end)
    w_start = meta_run["window_start_jst"]
    w_end = meta_run["window_end_jst"]

    results = []
    for c in hooked:
        url = c["url"]
        reach = base._classify_reachability(url)
        entry = {
            "candidate_id": c["candidate_id"], "url": url,
            "url_in_citations": c.get("url_in_citations"),
            "http_status": reach["http_status"], "status_class": reach["status_class"],
            "fetch_error": reach["error"], "answer_in_source": c.get("answer_in_source"),
        }
        window_classification = "unverifiable"
        published_time_verified = None
        verified_source_method = None
        if reach["status_class"] == "ok":
            raw_time, method = base._extract_published_time(reach["resp"].text)
            if raw_time is not None:
                verified_iso, tz_assumed, window_classification = base._classify_window(
                    raw_time, w_start, w_end)
                published_time_verified = verified_iso
                verified_source_method = method
        entry["published_time_verified"] = published_time_verified
        entry["verified_source_method"] = verified_source_method
        entry["window_classification"] = window_classification

        reasons = []
        if reach["status_class"] == "not_found":
            reasons.append("not_found_404")
        if window_classification == "outside_window":
            reasons.append("outside_window")
        if c.get("answer_in_source") == "NOT_IN_SOURCE":
            reasons.append("answer_not_in_source")
        if apply_citation_rule and c.get("url_in_citations") is False:
            reasons.append("url_not_in_citations")
        entry["disqualified"] = len(reasons) > 0
        entry["disqualify_reasons"] = reasons
        entry["note"] = None
        if reach["status_class"] == "forbidden_bot_block":
            entry["note"] = "到達不能(bot拒否の可能性、403)。失格にはしない。"
        elif window_classification == "unverifiable":
            entry["note"] = ((entry["note"] or "") +
                              " 公開時刻メタ情報を取得できずunverifiable。失格にはしない。")
        if not apply_citation_rule and c.get("url_in_citations") is False:
            entry["note"] = ((entry["note"] or "") +
                              " url_in_citations=false(除外ルール適用外、記録のみ)。")
        results.append(entry)

    disqualified_count = sum(1 for r in results if r["disqualified"])
    passed = [r["candidate_id"] for r in results if not r["disqualified"]]
    by_id = {c["candidate_id"]: c for c in hooked}
    passed_candidates = []
    for cid in passed:
        merged = dict(by_id[cid])
        v = next(r for r in results if r["candidate_id"] == cid)
        merged["url_in_citations"] = v["url_in_citations"]
        merged["http_status"] = v["http_status"]
        merged["status_class"] = v["status_class"]
        merged["published_time_verified"] = v["published_time_verified"]
        merged["window_classification"] = v["window_classification"]
        passed_candidates.append(merged)

    reason_counts = {}
    for r in results:
        for reason in r["disqualify_reasons"]:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    save_json(path, {
        "results": results, "passed_candidates": passed_candidates,
        "total_checked": len(results), "disqualified_count": disqualified_count,
        "passed_count": len(passed_candidates), "disqualify_reason_counts": reason_counts,
    })
    print(f"[OK] verify: checked={len(results)} disqualified={disqualified_count} "
          f"passed={len(passed_candidates)} reasons={reason_counts}")


# ------------------------------------------------------------
# final_new
# ------------------------------------------------------------
def cmd_final_new(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "final_new.json")
    if skip_if_exists(path, args.force):
        return
    passed = load_json(out_path(out_dir, "verify_new.json"))["passed_candidates"]
    base.install_logger(out_dir)
    client = base.get_client()

    compact = [{
        "candidate_id": c["candidate_id"], "title": c["title"], "source_name": c["source_name"],
        "summary_ja": c["summary_ja"], "hook_ja": c["hook_ja"], "hook_en": c["hook_en"],
        "category": c["category"], "distance_to_japan": c["distance_to_japan"],
        "distance_to_japan_reason": c["distance_to_japan_reason"], "dedupe_group": c["dedupe_group"],
        "is_pr_or_ad": c["is_pr_or_ad"], "country_scope": c["country_scope"],
        "window_classification": c["window_classification"], "source_stage": c.get("source_stage"),
        "query_used": c.get("query_used"),
    } for c in passed]

    developer = (
        "あなたはFinal Editorです。以下の基準をすべて守って最大20件を"
        "順位付きで選んでください。20件に満たない場合は無理に埋めず、"
        "実際に選べる数だけ返してください。"
    )
    user = f"""以下はStep D(整合・実在検証)を通過した候補のHook付き情報です。

【選定基準】
{SELECTION_CRITERIA_SENTENCE}

【機械的制約】
- dedupe_groupが同じ候補は1件だけ選んでください。
- Hookの文言(hook_ja/hook_en)は書き換えないでください。rank・
  candidate_id・selection_reason_jaのみを決めてください。

【候補一覧】
{json.dumps(compact, ensure_ascii=False, indent=2)}

上記基準に基づき、最大20件をrank(1が最上位)付きで選び、各選定について
candidate_id・selection_reason_ja(2〜3文)を返してください。"""

    response = call_model(client, developer, user, schema=base.STEP_E_SCHEMA, web_search=False,
                           stage="final_new", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = base.response_meta(response, user, developer)

    selections = sorted(parsed["selections"], key=lambda s: s["rank"])
    by_id = {c["candidate_id"]: c for c in passed}
    resolved = []
    unresolved_ids = []
    for s in selections:
        c = by_id.get(s["candidate_id"])
        if c is None:
            unresolved_ids.append(s["candidate_id"])
            continue
        merged = dict(c)
        merged["rank"] = s["rank"]
        merged["selection_reason_ja"] = s["selection_reason_ja"]
        resolved.append(merged)

    save_json(path, {
        "selections_raw": selections, "resolved": resolved,
        "unresolved_candidate_ids": unresolved_ids, "selected_count": len(resolved),
    })
    save_json(out_path(out_dir, "prompts", "final_new.json"), {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "final_new.json"), meta)
    print(f"[OK] final_new: selected_count={len(resolved)} unresolved={len(unresolved_ids)} "
          f"model={meta['response_model_actual']}")


# ------------------------------------------------------------
# hook_test --which h1|h2
# ------------------------------------------------------------
H1_SCHEMA = {
    "name": "hook_test_h1",
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "reference_id": {"type": "integer"},
                        "hook_ja": {"type": "string"},
                        "hook_en": {"type": "string"},
                        "answer_in_source": {"type": "string"},
                    },
                    "required": ["reference_id", "hook_ja", "hook_en", "answer_in_source"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
    "strict": True,
}

H2_STAGE1_SCHEMA = {
    "name": "hook_test_h2_stage1",
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "reference_id": {"type": "integer"},
                        "interesting_angle_ja": {"type": "string"},
                    },
                    "required": ["reference_id", "interesting_angle_ja"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
    "strict": True,
}

H2_STAGE2_SCHEMA = {
    "name": "hook_test_h2_stage2",
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "reference_id": {"type": "integer"},
                        "hook_ja": {"type": "string"},
                        "hook_en": {"type": "string"},
                        "answer_in_source": {"type": "string"},
                    },
                    "required": ["reference_id", "hook_ja", "hook_en", "answer_in_source"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
    "strict": True,
}


def cmd_hook_test(args):
    out_dir = args.out_dir
    which = args.which
    # Round 2追加(既存h1/h2の挙動は変更しない): --modelはNone/未指定なら
    # 従来通りcall_model側のMODEL_LUNAデフォルトを使う。--out-suffixは
    # 出力ファイル名にのみ影響し、未指定なら従来のファイル名と完全一致する。
    model = getattr(args, "model", None)
    out_suffix = getattr(args, "out_suffix", "") or ""
    suffix_tag = f"_{out_suffix}" if out_suffix else ""
    base.install_logger(out_dir)
    client = base.get_client()

    if which == "h1":
        path = out_path(out_dir, "hook_test_h1.json")
        if skip_if_exists(path, args.force):
            return
        developer = "あなたはHook Writerです。"
        user = f"""以下20件は、Newsの素材概要(見出し相当)だけです。各素材に
ついて、日本人ユーザーが一瞬目を止め、聞きたくなるHookを作成してください。

{HOOK_INSTRUCTION_MIKATA}

【素材一覧】
{json.dumps(REFERENCE_MATERIALS_ONLY, ensure_ascii=False, indent=2)}

各reference_idについてhook_ja・hook_en・answer_in_source(素材概要の
内容で実質的に答えられる部分の要約。答えられない場合は"NOT_IN_SOURCE")
を返してください。全reference_idについて出力してください。"""

        response = call_model(client, developer, user, schema=H1_SCHEMA, web_search=False,
                               stage="hook_test_h1", out_dir=out_dir)
        parsed = json.loads(response.output_text)
        meta = base.response_meta(response, user, developer)
        save_json(path, {"results": parsed["results"]})
        save_json(out_path(out_dir, "prompts", "hook_test_h1.json"), {"developer": developer, "user": user})
        save_json(out_path(out_dir, "raw_responses", "hook_test_h1.json"), meta)
        print(f"[OK] hook_test[h1]: results={len(parsed['results'])} model={meta['response_model_actual']}")

    elif which in ("h2", "h3"):
        # h3はRound 2追加(Fable設計): Stage 1はh2と同一Prompt(独立call)、
        # Stage 2のみ言い回し指定を変えた別Prompトにする。
        stage1_name = f"hook_test_{which}{suffix_tag}_stage1"
        stage1_path = out_path(out_dir, f"{stage1_name}.json")
        if not skip_if_exists(stage1_path, args.force):
            developer1 = "あなたはNews分析担当です。"
            user1 = f"""以下20件は、Newsの素材概要(見出し相当)だけです。各素材に
ついて、このニュースの最も面白い見方(人間にとって意外・身近・逆説的・
気になる点)を1文で書いてください。まだHookは作らないでください。

【素材一覧】
{json.dumps(REFERENCE_MATERIALS_ONLY, ensure_ascii=False, indent=2)}

各reference_idについてinteresting_angle_ja(1文)を返してください。全
reference_idについて出力してください。"""

            response1 = call_model(client, developer1, user1, schema=H2_STAGE1_SCHEMA,
                                    web_search=False, stage=stage1_name, model=model, out_dir=out_dir)
            parsed1 = json.loads(response1.output_text)
            meta1 = base.response_meta(response1, user1, developer1)
            save_json(stage1_path, {"results": parsed1["results"]})
            save_json(out_path(out_dir, "prompts", f"{stage1_name}.json"),
                      {"developer": developer1, "user": user1})
            save_json(out_path(out_dir, "raw_responses", f"{stage1_name}.json"), meta1)
            print(f"[OK] hook_test[{which}{suffix_tag}-stage1]: results={len(parsed1['results'])} "
                  f"model={meta1['response_model_actual']}")

        stage2_path = out_path(out_dir, f"hook_test_{which}{suffix_tag}.json")
        if skip_if_exists(stage2_path, args.force):
            return
        stage1_results = load_json(stage1_path)["results"]
        angle_by_id = {r["reference_id"]: r["interesting_angle_ja"] for r in stage1_results}
        topic_by_id = {m["reference_id"]: m["topic_ja"] for m in REFERENCE_MATERIALS_ONLY}
        stage2_input = [
            {"reference_id": rid, "topic_ja": topic_by_id[rid], "interesting_angle_ja": angle_by_id[rid]}
            for rid in sorted(angle_by_id)
        ]
        developer2 = "あなたはHook Writerです。"
        if which == "h2":
            user2 = f"""以下は各Newsの素材概要と、Stage 1で見つけた「最も面白い見方」
です。その見方を、答えを知りたくなる一文のHookにしてください。

{json.dumps(stage2_input, ensure_ascii=False, indent=2)}

【絶対条件】
(1) 釣りタイトル・誇張を禁止する。
(2) 素材概要では答えられない疑問を作らない。
(3) Fact以上の断定をしない。

各reference_idについてhook_ja・hook_en・answer_in_source(素材概要の
内容で実質的に答えられる部分の要約。答えられない場合は"NOT_IN_SOURCE")
を返してください。全reference_idについて出力してください。"""
        else:  # h3: Stage 2の言い回し指定のみFable委任文の指示に置換
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

        stage2_name = f"hook_test_{which}{suffix_tag}_stage2"
        response2 = call_model(client, developer2, user2, schema=H2_STAGE2_SCHEMA, web_search=False,
                                stage=stage2_name, model=model, out_dir=out_dir)
        parsed2 = json.loads(response2.output_text)
        meta2 = base.response_meta(response2, user2, developer2)
        save_json(stage2_path, {"results": parsed2["results"], "stage1_input_used": stage2_input})
        save_json(out_path(out_dir, "prompts", f"{stage2_name}.json"),
                  {"developer": developer2, "user": user2})
        save_json(out_path(out_dir, "raw_responses", f"{stage2_name}.json"), meta2)
        print(f"[OK] hook_test[{which}{suffix_tag}-stage2]: results={len(parsed2['results'])} "
              f"model={meta2['response_model_actual']}")
    else:
        raise ValueError(f"unknown --which: {which}")


# ------------------------------------------------------------
# aggregate(スクリプトのみ。ドメイン分布・query_used集計・Reference到達率
# ヒューリスティックを出力する。同一/類似の最終1語根拠判定はREPORT側で
# Sonnetが手動記載する)
# ------------------------------------------------------------
PR_DOMAINS = ["prtimes.jp", "atpress.ne.jp", "value-press.com", "kyodonewsprwire.jp", "dreamnews.jp"]
SNS_ARTICLE_DOMAINS = ["itmedia.co.jp", "nlab.itmedia.co.jp", "togetter.com", "buzzfeed.jp",
                        "hamusoku.com", "logsoku.com", "otakomu.jp", "jin115.com"]
LIFESTYLE_DOMAINS = ["mi-mollet.com", "precious.jp", "esse-online.jp", "locari.jp", "macaro-ni.jp",
                      "tabi-labo.com", "lifehacker.jp", "roomie.jp", "kufura.jp", "otonasalone.jp",
                      "hugkum.sho.jp", "folk-media.com", "4meee.com", "joshi-spa.jp", "sirabee.com",
                      "mynavi.jp"]
DOMESTIC_GENERAL_DOMAINS = ["nhk.or.jp", "asahi.com", "mainichi.jp", "yomiuri.co.jp", "nikkei.com",
                             "jiji.com", "sankei.com", "fnn.jp", "ntv.co.jp", "tbs.co.jp", "news24.jp",
                             "kyodo.co.jp", "tv-asahi.co.jp", "yahoo.co.jp", "jprime.jp", "oricon.co.jp",
                             "nikkansports.com", "sponichi.co.jp", "hochi.news", "tokyo-sports.co.jp",
                             "jcast.com"]


def classify_domain(url: str) -> str:
    try:
        netloc = urlparse(url or "").netloc.lower()
    except Exception:
        return "unclassified"
    if not netloc:
        return "unclassified"
    for d in PR_DOMAINS:
        if d in netloc:
            return "PR・リリース"
    for d in SNS_ARTICLE_DOMAINS:
        if d in netloc:
            return "SNS記事化"
    for d in LIFESTYLE_DOMAINS:
        if d in netloc:
            return "国内Lifestyle・Consumer"
    for d in DOMESTIC_GENERAL_DOMAINS:
        if d in netloc:
            return "国内一般"
    if netloc.endswith(".jp"):
        return "国内一般(未分類ドメイン)"
    return "海外/その他"


def _domain_distribution(candidates: list) -> dict:
    dist = {}
    for c in candidates:
        d = classify_domain(c.get("url"))
        dist[d] = dist.get(d, 0) + 1
    return dist


def _query_used_counts(candidates: list) -> dict:
    counts = {}
    for c in candidates:
        q = c.get("query_used") or "(none)"
        counts[q] = counts.get(q, 0) + 1
    return counts


def _pool_inclusion(pool: list, ref_list: list) -> list:
    results = []
    for r in ref_list:
        ref_tokens = base._tokenize_noun_like(r["topic_ja"])
        best = 0.0
        matched = None
        for c in pool:
            text = (c.get("title", "") or "") + " " + (c.get("summary_ja", "") or "")
            cand_tokens = base._tokenize_noun_like(text)
            if not ref_tokens:
                continue
            overlap = len(ref_tokens & cand_tokens) / len(ref_tokens)
            if overlap > best:
                best = overlap
                matched = c
        results.append({
            "reference_id": r["id"], "topic_ja": r["topic_ja"],
            "best_overlap_ratio": round(best, 3), "found_heuristic": best > 0.3,
            "matched_candidate_id": matched.get("candidate_id") if matched and best > 0.3 else None,
            "matched_title": matched.get("title") if matched and best > 0.3 else None,
        })
    return results


# Round 2追加: 前回(b)列は`RESULT_PACKET_TSCR.md`254-283行由来で
# Round 1 REPORT §Eの表(TOPIC-SELECTION-CHATGPT-REPRO-01_REPORT.md
# 525-544行)に既に転記済みの値をそのまま再利用する(再Readしない、
# スクリプト内では新規に導出しない静的な前Round確定値)。
PREV_B_HOOKS = {
    1: "AIに店への電話を頼んだら、裏では人間が話している？",
    2: "AIが人間の制御を超える可能性を、各国はどう議論している？",
    3: "AIはなぜ、米中首脳会談で貿易や安全保障と並ぶ議題になった？",
    4: "癌治療を変えるAIに、医師たちが慎重な見方を示すのはなぜ？",
    5: "宇宙でX線撮影ができると、診断の可能性はどう広がる？",
    6: "避妊の選択肢に、将来は男性向けの方法も加わる？",
    7: "季節の変わり目に、いびきの増加を感じる人は多い？",
    8: "睡眠の悩みを専門に診る「睡眠障害科」が、病院に増える？",
    9: "大谷翔平は、約2週間の離脱を経ていつ復帰する？",
    10: "18年前のカレンダーが、なぜ今になって14万回以上見られた？",
    11: "おかずが一種類だけの弁当は、なぜ賛否を呼ぶ？",
    12: "小さな保冷バッグが、無印良品の人気商品になった理由は？",
    13: "旅行の荷物は、圧縮ポーチでどこまで小さくできる？",
    14: "帝国ホテルのエコバッグは、なぜ高級品のように注目されている？",
    15: "意思決定に特化したAI「Jev」は、なぜ急速に話題になった？",
    16: "日本の香文化は、パリでどんな香水として世界に広がる？",
    17: "スマホ版『アニモ』は、異なる端末のプレイヤーとも遊べる？",
    18: "指パッチンは、ギネス記録になるほどの技なのか？",
    19: "旅行先は、安さだけでは選ばれない時代になった？",
    20: "職場に人工クラゲの水槽を置くサービスは、何を生み出す？",
}


def _hook_ja_by_id(out_dir: str, filename: str) -> dict:
    data = load_json(out_path(out_dir, filename))
    return {r["reference_id"]: r["hook_ja"] for r in data["results"]}


def cmd_aggregate_round2(out_dir: str, force: bool) -> None:
    path_md = out_path(out_dir, "round2_compare.md")
    if skip_if_exists(path_md, force):
        return
    ref = {r["id"]: r["hook_ja"] for r in base.REFERENCE_20}
    h1 = _hook_ja_by_id(out_dir, "hook_test_h1.json")
    h2_luna = _hook_ja_by_id(out_dir, "hook_test_h2.json")
    h3_luna = _hook_ja_by_id(out_dir, "hook_test_h3.json")
    h2_sol = _hook_ja_by_id(out_dir, "hook_test_h2_sol.json")
    h3_sol = _hook_ja_by_id(out_dir, "hook_test_h3_sol.json")

    columns = [
        ("Reference Hook", ref),
        ("前回(b)", PREV_B_HOOKS),
        ("H1", h1),
        ("H2(Luna)", h2_luna),
        ("H3(Luna)", h3_luna),
        ("H2(Sol)", h2_sol),
        ("H3(Sol)", h3_sol),
    ]

    lines = ["# CONT-02 Round 2 比較表(8列×20行、観察事実のみ・評価なし)", "",
             "| # | " + " | ".join(name for name, _ in columns) + " |",
             "|---|" + "|".join(["---"] * len(columns)) + "|"]
    for rid in range(1, 21):
        row = [str(rid)] + [str(d.get(rid, "N/A")) for _, d in columns]
        lines.append("| " + " | ".join(row) + " |")

    lines += ["", "## 形式集計(観察事実、評価はしない)", "",
              "| 列 | 「でしょうか」件数 | 疑問文でない件数(文末が「？」でない) | 平均字数 |",
              "|---|---|---|---|"]
    for name, d in columns:
        texts = [str(d.get(rid, "")) for rid in range(1, 21)]
        # 「でしょうか」件数: 文末の句読点(。？?)を除いた末尾が「でしょうか」で
        # 終わるかで判定(H2系は「でしょうか。」のように句点で終わるため、
        # 句読点を剥がしてから判定する)。
        deshou = sum(1 for t in texts if t.rstrip("。？?").endswith("でしょうか"))
        not_question = sum(1 for t in texts if not (t.endswith("？") or t.endswith("?")))
        avg_len = round(sum(len(t) for t in texts) / len(texts), 1) if texts else 0.0
        lines.append(f"| {name} | {deshou} | {not_question} | {avg_len} |")

    with open(path_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] aggregate --round2: rows=20 columns={len(columns)} -> {path_md}")


def cmd_aggregate(args):
    if getattr(args, "round2", False):
        cmd_aggregate_round2(args.out_dir, args.force)
        return
    out_dir = args.out_dir
    path_json = out_path(out_dir, "aggregate.json")
    if skip_if_exists(path_json, args.force):
        return
    pool_new = _merge_pool_new(out_dir)
    old_pool = load_json(out_path(REPRO01_OUT_DIR, "candidates_raw.json"))["candidates"]

    new_domain_dist = _domain_distribution(pool_new)
    old_domain_dist = _domain_distribution(old_pool)
    new_query_counts = _query_used_counts(pool_new)

    a1_4_titles = set()
    for g in range(1, 5):
        data = load_json(out_path(out_dir, f"a{g}.json"))
        for c in data["candidates"]:
            a1_4_titles.add(c["title"])
    a5_data = load_json(out_path(out_dir, "a5_feedback.json"))
    a5_new_count = sum(1 for c in a5_data["candidates"] if c["title"] not in a1_4_titles)

    new_pool_inclusion = _pool_inclusion(pool_new, base.REFERENCE_20)
    old_pool_inclusion = _pool_inclusion(old_pool, base.REFERENCE_20)

    result = {
        "new_pool_domain_distribution": new_domain_dist,
        "old_pool_domain_distribution": old_domain_dist,
        "new_pool_query_used_counts": new_query_counts,
        "feedback_round_new_topic_count_heuristic": a5_new_count,
        "new_pool_reference_inclusion_heuristic": new_pool_inclusion,
        "old_pool_reference_inclusion_heuristic": old_pool_inclusion,
        "new_pool_size": len(pool_new),
        "old_pool_size": len(old_pool),
        "domain_classification_method": "urlのnetlocを固定ドメインリスト(script内定数、"
                                          "Promptには使用していない)と照合するヒューリスティック。",
        "reference_inclusion_method": "reference topic_jaとcandidate title+summary_jaの"
                                        "noun-likeトークン重複率(reference側トークン数分の分母)"
                                        "が0.3超の場合found_heuristic=trueとする簡易判定"
                                        "(base scriptのcompareと同一ロジック)。同一/類似の最終"
                                        "判定(1語根拠)はSonnetがREPORT/aggregate.mdで手動記載する。",
    }
    save_json(path_json, result)

    lines = ["# CONT-02 aggregate", "",
             f"- new_pool_size={len(pool_new)} old_pool_size={len(old_pool)}",
             f"- feedback_round_new_topic_count_heuristic={a5_new_count}",
             "", "## domain distribution (new pool)", ""]
    for k, v in sorted(new_domain_dist.items(), key=lambda x: -x[1]):
        lines.append(f"- {k}: {v}")
    lines += ["", "## domain distribution (old REPRO-01 pool)", ""]
    for k, v in sorted(old_domain_dist.items(), key=lambda x: -x[1]):
        lines.append(f"- {k}: {v}")
    lines += ["", "## reference inclusion heuristic (new pool)", ""]
    for r in new_pool_inclusion:
        lines.append(f"- #{r['reference_id']} {r['topic_ja'][:30]}: "
                      f"overlap={r['best_overlap_ratio']} found={r['found_heuristic']}")
    lines += ["", "## reference inclusion heuristic (old pool)", ""]
    for r in old_pool_inclusion:
        lines.append(f"- #{r['reference_id']} {r['topic_ja'][:30]}: "
                      f"overlap={r['best_overlap_ratio']} found={r['found_heuristic']}")
    with open(out_path(out_dir, "aggregate.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] aggregate: new_pool_size={len(pool_new)} old_pool_size={len(old_pool)}")


# ------------------------------------------------------------
# 汚染検査(hook_test系は「素材概要」の使用が許可されているため対象外)
# ------------------------------------------------------------
CONTAMINATION_CHECK_PREFIXES = ("a0", "a1", "a2", "a3", "a4", "a5", "b1", "b2",
                                 "sel1", "sel2", "hooks_new", "final_new")


def check_reference_contamination(out_dir: str) -> dict:
    prompts_dir = out_path(out_dir, "prompts")
    checked = []
    hits = []
    if os.path.exists(prompts_dir):
        for fname in sorted(os.listdir(prompts_dir)):
            if fname.startswith("hook_test"):
                continue
            if not fname.startswith(CONTAMINATION_CHECK_PREFIXES):
                continue
            fpath = os.path.join(prompts_dir, fname)
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
            checked.append(fname)
            for kw in base.REFERENCE_CONTAMINATION_KEYWORDS:
                if kw in content:
                    hits.append({"file": fname, "keyword": kw})
    return {"checked_files": checked, "contamination_hits": hits, "contaminated": len(hits) > 0}


# ------------------------------------------------------------
# cost
# ------------------------------------------------------------
def cmd_cost(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "cost.json")
    if skip_if_exists(path, args.force):
        return
    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]
    usd_to_jpy = 160
    ws_price = base._price(pricing, "openai", "N/A (tool, all models)", "web_search_call")

    def model_prices(model_name):
        return (
            base._price(pricing, "openai", model_name, "input_tokens"),
            base._price(pricing, "openai", model_name, "cached_input_tokens"),
            base._price(pricing, "openai", model_name, "output_tokens"),
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
        # 実装上の注記(バグ修正、評価対象外): raw_usage_log.jsonlの実フィールド名は
        # "model_id"であり、"model"キーは存在しない。従来コード(base script含む)は
        # e.get("model")がNoneになりMODEL_LUNAへ常にフォールバックしていたため、
        # Sol call混在時に誤ってLuna単価で計算する不具合があった。Round 2でSol call
        # を導入したため本ファイル内でのみ修正する(baseファイル自体は無変更)。
        model_name = e.get("model_id") or e.get("model") or MODEL_LUNA
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
        s = by_stage.setdefault(stage, {"calls": 0, "input_tokens": 0, "cached_input_tokens": 0,
                                         "output_tokens": 0, "web_search_call_count": 0, "usd": 0.0,
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

    ws_log_path = out_path(out_dir, "web_search_log.json")
    explicit_ws_calls = len(load_json(ws_log_path)) if os.path.exists(ws_log_path) else 0

    by_stage_jpy = {
        stage: {**vals, "jpy": round(vals["usd"] * usd_to_jpy, 1)} for stage, vals in by_stage.items()
    }
    result = {
        "by_stage": by_stage_jpy,
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * usd_to_jpy, 1),
        "total_openai_calls": total_calls,
        "total_internal_web_search_call_count": total_ws_calls,
        "explicit_web_search_call_count": explicit_ws_calls,
        "explicit_web_search_budget": WEB_SEARCH_BUDGET,
        "explicit_web_search_within_budget": explicit_ws_calls <= WEB_SEARCH_BUDGET,
        "usd_to_jpy": usd_to_jpy,
        "cost_ceiling_jpy": 200,
        "within_cost_ceiling": round(total_usd * usd_to_jpy, 1) <= 200,
    }
    save_json(path, result)
    print(f"[OK] cost: total_jpy={result['total_jpy']} calls={total_calls} "
          f"explicit_ws={explicit_ws_calls}/{WEB_SEARCH_BUDGET} "
          f"within_ceiling={result['within_cost_ceiling']}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_iw = sub.add_parser("interest_words")
    p_iw.add_argument("--out-dir", required=True)
    p_iw.add_argument("--force", action="store_true")
    p_iw.set_defaults(func=cmd_interest_words)

    p_sa = sub.add_parser("search_a")
    p_sa.add_argument("--out-dir", required=True)
    p_sa.add_argument("--group", required=True, type=int, choices=[1, 2, 3, 4])
    p_sa.add_argument("--window-start", required=True)
    p_sa.add_argument("--window-end", required=True)
    p_sa.add_argument("--force", action="store_true")
    p_sa.set_defaults(func=cmd_search_a)

    p_fb = sub.add_parser("feedback_round")
    p_fb.add_argument("--out-dir", required=True)
    p_fb.add_argument("--window-start", required=True)
    p_fb.add_argument("--window-end", required=True)
    p_fb.add_argument("--force", action="store_true")
    p_fb.set_defaults(func=cmd_feedback_round)

    p_sb = sub.add_parser("search_b")
    p_sb.add_argument("--out-dir", required=True)
    p_sb.add_argument("--lane", required=True, type=int, choices=[1, 2])
    p_sb.add_argument("--window-start", required=True)
    p_sb.add_argument("--window-end", required=True)
    p_sb.add_argument("--force", action="store_true")
    p_sb.set_defaults(func=cmd_search_b)

    p_sel = sub.add_parser("select")
    p_sel.add_argument("--out-dir", required=True)
    p_sel.add_argument("--which", required=True, choices=["sel1", "sel2"])
    p_sel.add_argument("--force", action="store_true")
    p_sel.set_defaults(func=cmd_select)

    p_hn = sub.add_parser("hooks_new")
    p_hn.add_argument("--out-dir", required=True)
    p_hn.add_argument("--force", action="store_true")
    p_hn.set_defaults(func=cmd_hooks_new)

    p_v = sub.add_parser("verify")
    p_v.add_argument("--out-dir", required=True)
    p_v.add_argument("--window-start", required=True)
    p_v.add_argument("--window-end", required=True)
    p_v.add_argument("--no-citation-rule", action="store_true")
    p_v.add_argument("--force", action="store_true")
    p_v.set_defaults(func=cmd_verify)

    p_fn = sub.add_parser("final_new")
    p_fn.add_argument("--out-dir", required=True)
    p_fn.add_argument("--force", action="store_true")
    p_fn.set_defaults(func=cmd_final_new)

    p_ht = sub.add_parser("hook_test")
    p_ht.add_argument("--out-dir", required=True)
    p_ht.add_argument("--which", required=True, choices=["h1", "h2", "h3"])
    p_ht.add_argument("--model", default=None,
                       help="Round 2追加: 省略時はMODEL_LUNA(既存挙動を維持)")
    p_ht.add_argument("--out-suffix", default="",
                       help="Round 2追加: 出力ファイル名末尾に付与(例: sol)")
    p_ht.add_argument("--force", action="store_true")
    p_ht.set_defaults(func=cmd_hook_test)

    p_agg = sub.add_parser("aggregate")
    p_agg.add_argument("--out-dir", required=True)
    p_agg.add_argument("--round2", action="store_true",
                        help="Round 2追加: round2_compare.md(8列比較表+形式集計)を生成する")
    p_agg.add_argument("--force", action="store_true")
    p_agg.set_defaults(func=cmd_aggregate)

    p_cost = sub.add_parser("cost")
    p_cost.add_argument("--out-dir", required=True)
    p_cost.add_argument("--force", action="store_true")
    p_cost.set_defaults(func=cmd_cost)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
