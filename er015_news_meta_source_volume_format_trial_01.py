# ============================================================
# er015_news_meta_source_volume_format_trial_01.py
# NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01 (ユーザー指示、2026-09-24)
# ============================================================
# 目的: MetaのAI電話代行(Muse「人間コンシェルジュ」実験)記事を対象に、
# Entertainment性低下の原因が「参照情報の量」か「Ledger形式そのもの」かを
# 切り分ける日本語限定Trial。4条件(1記事要点/前回Baseline/10記事要点/
# 10記事Ledger)×Original->R1->R2で比較する。
#
# Production実装ではない。Writer Prompt(P7)・developer message・
# Revision指示・model/effortは、既存VALIDATED Trial
# (er015_news_iterative_entertainment_trial_02.py Article A)と完全同一の
# ものをimport再利用し、本ファイルでは一切変更しない。R3は生成しない。
#
# 依存(いずれも無変更・import再利用のみ):
#   - er003_v1_en_direct_vfl_01_generate (vfl01): get_client, MODEL, REASONING_EFFORT
#   - er005_cost_logger (cl): usage log install/logging_context
#   - er015_news_core_idea_editorial_trial_01 (er015base): response_meta,
#     _load_pricing, _price, USD_TO_JPY
#   - er015_news_iterative_entertainment_trial_01 (trial01): REVISION_INSTRUCTIONS
#   - er015_news_iterative_entertainment_trial_02 (trial02): R0_PROMPT構築済み
#     THEME_LINE["A"]・MATERIAL_A(=前回Baseline逐語)・call_fresh/
#     call_with_previous_response_id・SOURCE_META["A"]
#   - er015_news_original_baseline_repro_01 (repro01): R0_PROMPT本体,
#     DEVELOPER_MESSAGE, WRITER_MODEL, WRITER_EFFORT
#   - er002_ja_web_research_r3 (r3): extract_sources, extract_web_search_usage
#
# ステップ(--step): baseline / sources / inputs / generate / assemble
# STOP条件に該当した場合、該当stepは非0終了し<out_dir>/stop_reason.json へ
# 理由を書き込む(委任文STOP条件節、全7項目)。
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_iterative_entertainment_trial_01 as trial01
import er015_news_iterative_entertainment_trial_02 as trial02
import er015_news_original_baseline_repro_01 as repro01

THEME_TAG = "NEWS_META_SOURCE_VOLUME_FORMAT_TRIAL_01"

WRITER_MODEL = repro01.WRITER_MODEL
WRITER_EFFORT = repro01.WRITER_EFFORT
DEVELOPER_MESSAGE = repro01.DEVELOPER_MESSAGE
R0_PROMPT = repro01.R0_PROMPT
REVISION_INSTRUCTIONS = dict(trial01.REVISION_INSTRUCTIONS)  # r1, r2, r3(未使用)

THEME_LINE = trial02.THEME_LINE["A"]
# 条件2(前回Baseline)= trial02 Article Aの[ニュース]欄と逐語同一。
BASELINE_MATERIAL = trial02.MATERIAL_A
BASELINE_SOURCE_URL = trial02.SOURCE_META["A"]["url"]
BASELINE_SOURCE_TOPIC = trial02.SOURCE_META["A"]["topic"]

SUMMARIZE_MODEL = WRITER_MODEL  # gpt-5.6-luna(要点生成・Ledger変換とも同一モデル)
SUMMARIZE_EFFORT = "medium"
SEARCH_EFFORT = "medium"

USER_AGENT = trial02.USER_AGENT

# 既存artifactから再利用する既知Source(いずれも同一事象=Meta Muse電話代行
# 「人間コンシェルジュ」実験を扱う)。
KNOWN_SOURCES = [
    {
        "id": "S01",
        "url": BASELINE_SOURCE_URL,
        "title": "Meta testing a 'human concierge' for its new personal AI agent, Muse | MarketScreener",
        "media": "MarketScreener(Reuters配信)",
        "reused_from": "er015_news_iterative_entertainment_trial_02.MATERIAL_A(逐語再利用)",
    },
    {
        "id": "S02",
        "url": "https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/",
        "title": "Introducing Muse: The World's First Personal AI Agent Built for Everyone",
        "media": "about.fb.com(Meta公式)",
        "reused_from": "er017_output/.../ledger/audit/researcher_full_record.json sources[0]",
    },
    {
        "id": "S03",
        "url": "https://www.404media.co/meta-tests-muse-ai-agent-calls-that-are-actually-made-by-humans-in-a-call-center/?utm_source=openai",
        "title": "Meta Tests Muse AI Agent Calls That Are Actually Made By Humans in a Call Center",
        "media": "404 Media",
        "reused_from": "er017_output/.../ledger/audit/researcher_full_record.json sources[2]",
    },
]

SEARCH_QUERIES = [
    "Meta Muse AI agent human concierge phone calls Reuters",
    "Meta Muse \"human concierge\" call center employees rolled back",
]

# 補充検索(fix01委任、前回2 callと異なる語彙。最大2 call、Fable判断)。
EXTRA_SEARCH_QUERIES = [
    "Meta Muse \"human concierge\" contractors phone calls Reuters",
    "Meta Muse 電話 代行 人間 コンシェルジュ 契約スタッフ",
]

ON_TOPIC_KEYWORDS = ["Muse", "concierge", "Meta"]

NUMBER_RE = re.compile(r"\d+(?:[,\.]\d+)?")
PROPER_NOUNS = [
    "Meta", "Muse", "Reuters", "人間コンシェルジュ", "契約スタッフ", "プライバシー",
    "rolled back", "404 Media", "MarketScreener", "about.fb.com",
]
ECHO_PHRASE = "これ、ちょっと面白くない？"


# ------------------------------------------------------------
# 汎用ヘルパー
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def stop(out_dir: str, reason_code: str, detail: dict) -> None:
    save_json(out_path(out_dir, "stop_reason.json"), {
        "reason_code": reason_code,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    print(f"[STOP] {reason_code}: {json.dumps(detail, ensure_ascii=False)}")
    sys.exit(1)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# step: baseline (Step 0, STOP判定)
# ------------------------------------------------------------
def cmd_baseline(args):
    out_dir = args.out_dir
    sentences = [s for s in BASELINE_MATERIAL.split("。") if s.strip()]
    sentence_count = len(sentences)
    char_count = len(BASELINE_MATERIAL)

    # trial02 chain.jsonからArticle Aのresponse_id連鎖・chain_methodを確認
    chain_path = "er015_output/news_iterative_entertainment_trial_02/chain.json"
    if not os.path.exists(chain_path):
        stop(out_dir, "BASELINE_CHAIN_NOT_FOUND", {"expected_path": chain_path})
        return
    chain = load_json(chain_path)
    art_a_chain = chain.get("articles", {}).get("A")
    if not art_a_chain:
        stop(out_dir, "BASELINE_ARTICLE_A_CHAIN_NOT_FOUND", {"path": chain_path})
        return

    lines = [
        "# Baseline確認(NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01, Step 0)",
        "",
        "## 前回Baseline(条件2)の入力件数・形式(根拠付き)",
        "",
        f"- 根拠ファイル: `er015_news_iterative_entertainment_trial_02.py` "
        f"MATERIAL_A定数(行94-99)、`docs/evidence/news_iterative_r2_adoption_2026-09-24/"
        f"prompts.md` 2-B節(行41-62)",
        f"- Source数: 1件(URL: {BASELINE_SOURCE_URL})",
        f"- 文数: {sentence_count}文(句点「。」区切り)",
        f"- 文字数: {char_count}字",
        "- 粒度: 元記事本文の要約(直接引用ではなく2〜3文への要約パラフレーズ)",
        "- 形式: 段落形式のプレーンテキスト(箇条書きではない)、`[ニュース]`欄へ挿入",
        "",
        "### 逐語(MATERIAL_A、条件2でそのまま再利用する)",
        "",
        "```",
        BASELINE_MATERIAL,
        "```",
        "",
        "## Prompt(P7)・Revision指示・model/effort・連鎖方式の特定",
        "",
        f"- Original Prompt(P7)本体: `er015_news_original_baseline_repro_01.py` "
        f"R0_PROMPT定数(逐語、テーマ行のみ差し替え)",
        f"- テーマ行: `{THEME_LINE}`(trial02 THEME_LINE[\"A\"]と同一)",
        f"- developer message: `{DEVELOPER_MESSAGE}`",
        f"- R1指示(逐語): {REVISION_INSTRUCTIONS['r1']}",
        f"- R2指示(逐語): {REVISION_INSTRUCTIONS['r2']}",
        f"- model: {WRITER_MODEL} / effort: {WRITER_EFFORT}",
        f"- 連鎖方式: previous_response_id(trial02 chain.json Article A: "
        f"{json.dumps(art_a_chain, ensure_ascii=False)})",
        "",
        "## 判定",
        "",
        "STOP該当なし。条件2はMATERIAL_Aを逐語再現することでBaselineを再現する。",
    ]
    save_text(out_path(out_dir, "baseline_evidence.md"), "\n".join(lines))
    print(f"[OK] baseline_evidence.md written. sentence_count={sentence_count} char_count={char_count}")


# ------------------------------------------------------------
# step: sources --target 10
# ------------------------------------------------------------
def fetch_body_text(url: str) -> dict:
    """直接取得(BeautifulSoup本文抽出)、失敗時はreader proxy(r.jina.ai)。"""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 2000:
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "aside"]):
                tag.decompose()
            main = soup.find("article") or soup.find("main") or soup.body
            text = main.get_text(separator="\n", strip=True) if main else soup.get_text(separator="\n", strip=True)
            if len(text) > 500:
                return {"method": "direct", "http_status": resp.status_code, "text": text}
        raise RuntimeError(f"direct insufficient status={resp.status_code} len={len(resp.content)}")
    except Exception as e:  # noqa: BLE001
        direct_error = str(e)
    try:
        resp = requests.get(f"https://r.jina.ai/{url}", timeout=40)
        return {
            "method": "reader_proxy(r.jina.ai)", "http_status": resp.status_code,
            "text": resp.text, "direct_fetch_error": direct_error,
        }
    except Exception as e2:  # noqa: BLE001
        return {"method": None, "fetch_status": "FAILED",
                "direct_fetch_error": direct_error, "proxy_fetch_error": str(e2)}


def summarize_body(client, media: str, url: str, body_text: str, stage_tag: str) -> dict:
    body_trunc = body_text[:8000]
    prompt = (
        "以下は、あるニュース記事の本文(自動抽出)です。本文にある事実だけを使って、"
        "日本語で2〜3文の要点にまとめてください。推測や本文にない情報を加えないでください。"
        "出力は要点の文章のみ(前置き・見出し不要)。\n\n"
        f"[記事本文({media})]\n{body_trunc}"
    )
    kwargs = dict(
        model=SUMMARIZE_MODEL,
        reasoning={"effort": SUMMARIZE_EFFORT},
        input=[
            {"role": "developer", "content": "あなたはFact要約担当です。本文にない情報を加えません。"},
            {"role": "user", "content": prompt},
        ],
    )
    with cl.logging_context(THEME_TAG, stage_tag):
        response = client.responses.create(**kwargs)
    text = response.output_text.strip()
    meta = er015base.response_meta(response, prompt, "あなたはFact要約担当です。本文にない情報を加えません。",
                                    extra={"stage": stage_tag, "url": url, "media": media,
                                           "effort_requested": SUMMARIZE_EFFORT})
    return {"summary": text, "meta": meta}


def search_candidates(client, query: str, stage_tag: str) -> dict:
    kwargs = dict(
        model=SUMMARIZE_MODEL,
        reasoning={"effort": SEARCH_EFFORT},
        tools=[{"type": "web_search"}],
        input=[
            {"role": "developer", "content": "あなたはNews Source調査担当です。検索結果のURL・タイトルのみを扱い、本文は書きません。"},
            {"role": "user", "content": f"次のニュース事象について報じている記事を検索してください: {query}\n"
                                          "関連記事のタイトルとURLを箇条書きで挙げてください。"},
        ],
    )
    with cl.logging_context(THEME_TAG, stage_tag):
        response = client.responses.create(**kwargs)
    sources = r3.extract_sources(response)
    search_usage = r3.extract_web_search_usage(response)
    meta = er015base.response_meta(response, query, "あなたはNews Source調査担当です。",
                                    extra={"stage": stage_tag, "query": query})
    return {"sources": sources, "search_usage": search_usage, "meta": meta}


def cmd_sources(args):
    out_dir = args.out_dir
    target = args.target
    install_logger(out_dir)
    client = vfl01.get_client()
    fetched_dir = out_path(out_dir, "fetched")
    os.makedirs(fetched_dir, exist_ok=True)

    sources_path = out_path(out_dir, "sources_10.json")
    search_log_path = out_path(out_dir, "search_log.json")
    stop_reason_path = out_path(out_dir, "stop_reason.json")
    excluded_path = out_path(out_dir, "excluded_candidates.json")

    resumed = os.path.exists(sources_path)
    if resumed:
        collected = load_json(sources_path)
        search_log = load_json(search_log_path) if os.path.exists(search_log_path) else []
        excluded = load_json(excluded_path) if os.path.exists(excluded_path) else []
        # 前回STOP(SOURCE_COUNT_INSUFFICIENT等)は今回の補充結果次第で解消され得るため、
        # 今回のstep実行結果で上書きする(stale STOPを残さない)。
        if os.path.exists(stop_reason_path):
            os.remove(stop_reason_path)
        print(f"[OK] resumed {len(collected)} previously collected sources from {sources_path}")
    else:
        collected = []  # list of dict: id, url, media, title, summary, method, sha256
        search_log = []
        excluded = []

    if resumed:
        known_urls = {c["url"] for c in collected}
        candidate_pool = []
    else:
        collected, search_log, excluded, known_urls, candidate_pool = _collect_initial(
            args, client, out_dir, fetched_dir, target, collected, search_log, excluded)

    # --- 追加検索(fix01委任: 前回と異なる語彙、最大 --extra-search-calls call) ---
    if len(collected) < target and args.extra_search_calls > 0:
        used = 0
        extra_candidate_pool = []
        for q in EXTRA_SEARCH_QUERIES:
            if used >= args.extra_search_calls or len(collected) >= target:
                break
            used += 1
            sres = search_candidates(client, q, f"search_extra_{used}")
            save_json(out_path(out_dir, f"api_meta_search_extra_{used}.json"), sres["meta"])
            search_log.append({"query": q, "phase": "extra_vocab_fix01", "sources_found": sres["sources"],
                                "search_usage": sres["search_usage"]})
            for s in sres["sources"]:
                u = s.get("url")
                if u and u not in known_urls and u not in [c["url"] for c in extra_candidate_pool]:
                    extra_candidate_pool.append({"url": u, "title": s.get("title"), "from_query": q,
                                                  "phase": "extra_vocab_fix01"})

        next_id_num = len(collected) + 1
        for cand in extra_candidate_pool:
            if len(collected) >= target:
                break
            url = cand["url"]
            body = fetch_body_text(url)
            body_text = body.get("text", "")
            if not body_text:
                print(f"[SKIP] candidate fetch failed: {url}")
                excluded.append({"url": url, "title": cand.get("title"), "reason": "fetch_failed",
                                  "detail": body, "phase": "extra_vocab_fix01"})
                continue
            if not any(kw in body_text for kw in ON_TOPIC_KEYWORDS):
                print(f"[SKIP] off-topic (keyword check failed): {url}")
                excluded.append({"url": url, "title": cand.get("title"), "reason": "off_topic",
                                  "phase": "extra_vocab_fix01"})
                continue
            sid = f"S{next_id_num:02d}"
            save_text(out_path(fetched_dir, f"{sid}.txt"), body_text)
            media = cand.get("title") or url
            result = summarize_body(client, media, url, body_text, f"summarize_{sid}")
            collected.append({
                "id": sid, "url": url, "media": media, "title": cand.get("title"),
                "summary": result["summary"], "method": "luna_summarize_effort_medium",
                "fetch_method": body.get("method"), "sha256": sha256_text(body_text),
                "phase": "extra_vocab_fix01",
            })
            save_json(out_path(out_dir, f"api_meta_summarize_{sid}.json"), result["meta"])
            known_urls.add(url)
            print(f"[OK] {sid}: fetched({body.get('method')}) + summarized (extra search)")
            next_id_num += 1

    save_json(search_log_path, search_log)
    save_json(excluded_path, excluded)
    save_json(sources_path, collected)

    reached = len(collected)
    lines = ["# Source一覧(NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01)", "",
             f"目標件数: {target} / 到達件数: {reached}", ""]
    if reached < target:
        lines += [f"**注記(fix01委任): 目標{target}記事に対し補充検索後も{reached}記事にとどまった。"
                  f"委任文により10未満でもSTOPとせず、条件3・条件4は『{reached}記事(目標{target}、到達{reached})』"
                  f"として続行する。**", ""]
    for c in collected:
        lines += [
            f"## {c['id']}: {c['media']}", "",
            f"- URL: {c['url']}",
            f"- 取得方法(要点作成の元本文): {c.get('fetch_method')}",
            f"- 要点作成方法: {c['method']}",
            f"- sha256(本文): {c.get('sha256')}",
            "",
            "### 要点(2〜3文)", "",
            c["summary"], "",
        ]
    save_text(out_path(out_dir, "sources_10.md"), "\n".join(lines))

    if reached < target:
        if args.allow_partial and reached >= 8:
            print(f"[OK] sources: partial reached {reached}/{target} (--allow-partial, fix01委任により続行)")
        else:
            stop(out_dir, "SOURCE_COUNT_INSUFFICIENT", {
                "target": target, "reached": reached,
                "collected_ids": [c["id"] for c in collected],
            })
            return
    else:
        print(f"[OK] sources: reached {reached}/{target}")


def _collect_initial(args, client, out_dir, fetched_dir, target, collected, search_log, excluded):
    # --- 既知Source(条件2の再利用込み) ---
    for src in KNOWN_SOURCES:
        sid, url, media, title = src["id"], src["url"], src["media"], src["title"]
        if sid == "S01":
            # 条件2=BASELINE_MATERIALを逐語再利用(再取得・再要約はしない)
            body = fetch_body_text(url)
            body_text = body.get("text", "")
            save_text(out_path(fetched_dir, f"{sid}.txt"), body_text)
            collected.append({
                "id": sid, "url": url, "media": media, "title": title,
                "summary": BASELINE_MATERIAL, "method": "reused_verbatim_trial02_MATERIAL_A",
                "fetch_method": body.get("method"), "sha256": sha256_text(body_text) if body_text else None,
            })
            print(f"[OK] {sid}: reused verbatim baseline material")
            continue
        body = fetch_body_text(url)
        body_text = body.get("text", "")
        if not body_text:
            print(f"[WARN] {sid} fetch failed: {body}")
            excluded.append({"url": url, "title": title, "reason": "fetch_failed", "detail": body,
                              "phase": "known_source"})
            continue
        save_text(out_path(fetched_dir, f"{sid}.txt"), body_text)
        result = summarize_body(client, media, url, body_text, f"summarize_{sid}")
        collected.append({
            "id": sid, "url": url, "media": media, "title": title,
            "summary": result["summary"], "method": "luna_summarize_effort_medium",
            "fetch_method": body.get("method"), "sha256": sha256_text(body_text),
        })
        save_json(out_path(out_dir, f"api_meta_summarize_{sid}.json"), result["meta"])
        print(f"[OK] {sid}: fetched({body.get('method')}) + summarized")

    known_urls = {s["url"] for s in collected}

    # --- 不足時のみ検索で補充(Luna web_search 最大2 call、初回語彙) ---
    candidate_pool = []
    if len(collected) < target:
        for i, q in enumerate(SEARCH_QUERIES, start=1):
            if len(collected) >= target:
                break
            sres = search_candidates(client, q, f"search_{i}")
            save_json(out_path(out_dir, f"api_meta_search_{i}.json"), sres["meta"])
            search_log.append({"query": q, "phase": "initial", "sources_found": sres["sources"],
                                "search_usage": sres["search_usage"]})
            for s in sres["sources"]:
                u = s.get("url")
                if u and u not in known_urls and u not in [c["url"] for c in candidate_pool]:
                    candidate_pool.append({"url": u, "title": s.get("title"), "from_query": q})

    # --- 候補を本文取得・on-topic判定・要約(targetに達するまで) ---
    next_id_num = len(collected) + 1
    for cand in candidate_pool:
        if len(collected) >= target:
            break
        url = cand["url"]
        body = fetch_body_text(url)
        body_text = body.get("text", "")
        if not body_text:
            print(f"[SKIP] candidate fetch failed: {url}")
            excluded.append({"url": url, "title": cand.get("title"), "reason": "fetch_failed",
                              "detail": body, "phase": "initial"})
            continue
        if not any(kw in body_text for kw in ON_TOPIC_KEYWORDS):
            print(f"[SKIP] off-topic (keyword check failed): {url}")
            excluded.append({"url": url, "title": cand.get("title"), "reason": "off_topic", "phase": "initial"})
            continue
        sid = f"S{next_id_num:02d}"
        save_text(out_path(fetched_dir, f"{sid}.txt"), body_text)
        media = cand.get("title") or url
        result = summarize_body(client, media, url, body_text, f"summarize_{sid}")
        collected.append({
            "id": sid, "url": url, "media": media, "title": cand.get("title"),
            "summary": result["summary"], "method": "luna_summarize_effort_medium",
            "fetch_method": body.get("method"), "sha256": sha256_text(body_text),
        })
        save_json(out_path(out_dir, f"api_meta_summarize_{sid}.json"), result["meta"])
        print(f"[OK] {sid}: fetched({body.get('method')}) + summarized (searched)")
        next_id_num += 1

    known_urls = {s["url"] for s in collected}
    return collected, search_log, excluded, known_urls, candidate_pool


# ------------------------------------------------------------
# step: inputs (条件1-4の入力確定)
# ------------------------------------------------------------
LEDGER_CONVERT_PROMPT_TEMPLATE = """以下は、同一のニュース事象(Meta Museの電話代行機能をめぐる「人間コンシェルジュ」実験)
について、{n}件の記事から抽出した本文です。この本文にある事実だけを使って、Verified Fact Ledger形式で
列挙してください。本文にない事実・推測・数字・固有名詞を一切追加しないでください。別のSourceを追加しないでください。
検証(Web再照合)は行っていないため、各Factの末尾に status: TRIAL_UNVERIFIED と明記してください。

【出力形式(1Factにつき1ブロック)】
[TRIAL_UNVERIFIED] <fact_id>: <claim> (出典: <識別子。下記S01〜S{n:02d}のいずれか>)
  scope: <対象範囲、不明ならnull>
  conditions: <適用条件、不明ならnull>
  date_or_period: <時期、不明ならnull>
  numeric_value: <数値、なければnull>
  causal_strength: <OBSERVED_REPORTED / CORRELATIONAL / CAUSAL_STATED_BY_SOURCE / NOT_APPLICABLE>
  notes_for_writer: <writer向け注意、不明ならnull>
  status: TRIAL_UNVERIFIED

出典の識別子は、必ず下記リストのS01〜S{n:02d}のいずれかを使ってください。リストにない識別子・URLを作らないでください。

【記事本文一覧】
{bodies}
"""


COND3_HEADER_RE = re.compile(r"^\[N記事\(目標\d+、到達\d+\)\]\n?")


def strip_cond3_header(material: str) -> str:
    """cond3.md冒頭のドキュメント用注記(fix01委任)をWriter入力から除去する。
    Writerへ渡す実素材は4条件で書式(注記の有無)を揃えるため、この注記は
    ファイル内の記録用のみとし、build_prompt/機械集計へは渡さない。"""
    return COND3_HEADER_RE.sub("", material, count=1)


def build_prompt(material: str) -> str:
    lines = R0_PROMPT.split("\n")
    new_lines = [THEME_LINE if l.startswith("テーマ：") else l for l in lines]
    prompt = "\n".join(new_lines)
    prompt += "\n\n[ニュース]\n" + material
    return prompt


def cmd_inputs(args):
    out_dir = args.out_dir
    install_logger(out_dir)
    sources_path = out_path(out_dir, "sources_10.json")
    if not os.path.exists(sources_path):
        stop(out_dir, "SOURCES_NOT_FOUND", {"expected_path": sources_path})
        return
    sources = load_json(sources_path)
    # fix01委任: 補充検索後もN記事(8以上)ならSTOPせず「N記事(目標10、到達N)」として続行する。
    MIN_N_FIX01 = 8
    if len(sources) < MIN_N_FIX01:
        stop(out_dir, "SOURCE_COUNT_INSUFFICIENT_AT_INPUTS", {"reached": len(sources), "min_required": MIN_N_FIX01})
        return
    sources = sources[:args.target]
    n_sources = len(sources)
    inputs_dir = out_path(out_dir, "inputs")
    os.makedirs(inputs_dir, exist_ok=True)

    # --- 条件1: 中心記事(S01)の中心要点のみ(条件2より少ない文数) ---
    baseline_sentences = [s.strip() for s in BASELINE_MATERIAL.split("。") if s.strip()]
    cond1_material = baseline_sentences[0].strip() + "。"
    save_text(out_path(inputs_dir, "cond1.md"), cond1_material)

    # --- 条件2: 前回Baseline逐語 ---
    save_text(out_path(inputs_dir, "cond2.md"), BASELINE_MATERIAL)

    # --- 条件3: N記事要点(媒体名付き)。fix01委任によりN=8〜10(目標10) ---
    cond3_header = f"[N記事(目標{args.target}、到達{n_sources})]" if n_sources < args.target else ""
    cond3_lines = []
    if cond3_header:
        cond3_lines.append(cond3_header)
    for s in sources:
        cond3_lines.append(f"・({s['media']}) {s['summary']}")
    cond3_material = "\n".join(cond3_lines)
    save_text(out_path(inputs_dir, "cond3.md"), cond3_material)

    diff_note = (
        f"条件1は条件2(2文)のうち第1文のみ({len(cond1_material)}字)。"
        f"条件2は{len(BASELINE_MATERIAL)}字・{len(baseline_sentences)}文。"
        f"条件3は{n_sources}記事(目標{args.target}、到達{n_sources})・{len(cond3_material)}字。"
    )
    save_text(out_path(inputs_dir, "diff_note.md"), diff_note)

    # --- 条件4: 条件3と同一10記事の本文からLedger変換(別Source追加禁止) ---
    fetched_dir = out_path(out_dir, "fetched")
    bodies_parts = []
    for s in sources:
        body_path = out_path(fetched_dir, f"{s['id']}.txt")
        body_text = load_text(body_path) if os.path.exists(body_path) else ""
        bodies_parts.append(f"[{s['id']}] {s['media']} ({s['url']})\n{body_text[:6000]}")
    bodies_joined = "\n\n---\n\n".join(bodies_parts)
    ledger_prompt = LEDGER_CONVERT_PROMPT_TEMPLATE.format(n=len(sources), bodies=bodies_joined)

    client = vfl01.get_client()
    kwargs = dict(
        model=WRITER_MODEL,
        reasoning={"effort": SUMMARIZE_EFFORT},
        input=[
            {"role": "developer", "content": "あなたはFact Researcherです。与えられた本文以外の情報を使いません。"},
            {"role": "user", "content": ledger_prompt},
        ],
    )
    with cl.logging_context(THEME_TAG, "ledger_cond4"):
        response = client.responses.create(**kwargs)
    ledger_text = response.output_text.strip()
    meta = er015base.response_meta(response, ledger_prompt, "あなたはFact Researcherです。",
                                    extra={"stage": "ledger_cond4", "effort_requested": SUMMARIZE_EFFORT,
                                           "web_search_tool_used": False})
    save_text(out_path(inputs_dir, "ledger_cond4.txt"), ledger_text)
    save_json(out_path(out_dir, "api_meta_ledger_cond4.json"), meta)

    # 機械確認: Ledger中の出典識別子集合 が S01..S10 の部分集合であること(新Source追加なし)
    cited_ids = set(re.findall(r"S\d{2}", ledger_text))
    allowed_ids = {s["id"] for s in sources}
    extra_ids = sorted(cited_ids - allowed_ids)
    missing_ids = sorted(allowed_ids - cited_ids)
    id_check = {
        "allowed_ids": sorted(allowed_ids), "cited_ids": sorted(cited_ids),
        "extra_ids_not_allowed": extra_ids, "missing_ids_not_cited": missing_ids,
        "no_new_source_added": len(extra_ids) == 0,
    }
    save_json(out_path(out_dir, "ledger_source_id_check.json"), id_check)
    if extra_ids:
        stop(out_dir, "LEDGER_NEW_SOURCE_ADDED", id_check)
        return

    # info_set_diff: 条件3の要点とLedgerの数字・固有名詞の機械差分(観察事実のみ)
    cond3_numbers = set(NUMBER_RE.findall(cond3_material))
    ledger_numbers = set(NUMBER_RE.findall(ledger_text))
    cond3_nouns = {n for n in PROPER_NOUNS if n in cond3_material}
    ledger_nouns = {n for n in PROPER_NOUNS if n in ledger_text}
    diff = {
        "numbers_in_ledger_not_in_cond3": sorted(ledger_numbers - cond3_numbers),
        "numbers_in_cond3_not_in_ledger": sorted(cond3_numbers - ledger_numbers),
        "proper_nouns_in_ledger_not_in_cond3": sorted(ledger_nouns - cond3_nouns),
        "proper_nouns_in_cond3_not_in_ledger": sorted(cond3_nouns - ledger_nouns),
        "fact_block_count_ledger": len(re.findall(r"^\[TRIAL_UNVERIFIED\]", ledger_text, flags=re.M)),
    }
    save_json(out_path(out_dir, "info_set_diff.json"), diff)
    save_text(out_path(out_dir, "info_set_diff.md"),
              "# 条件3要点 vs 条件4 Ledger 情報集合差(機械抽出、観察事実のみ)\n\n" +
              json.dumps(diff, ensure_ascii=False, indent=2))

    print(f"[OK] inputs: cond1={len(cond1_material)}字 cond2={len(BASELINE_MATERIAL)}字 "
          f"cond3={len(cond3_material)}字 ledger_cond4={len(ledger_text)}字 "
          f"no_new_source_added={id_check['no_new_source_added']}")


# ------------------------------------------------------------
# step: generate --conditions 1,2,3,4 --stages 0,1,2
# ------------------------------------------------------------
STAGE_KEY = {0: "original", 1: "r1", 2: "r2"}
STAGE_SUFFIX = {0: "original", 1: "revision1", 2: "revision2"}


def cmd_generate(args):
    out_dir = args.out_dir
    install_logger(out_dir)
    client = vfl01.get_client()
    inputs_dir = out_path(out_dir, "inputs")

    materials = {
        1: load_text(out_path(inputs_dir, "cond1.md")),
        2: load_text(out_path(inputs_dir, "cond2.md")),
        3: strip_cond3_header(load_text(out_path(inputs_dir, "cond3.md"))),
        4: load_text(out_path(inputs_dir, "ledger_cond4.txt")),
    }

    conditions = [int(c) for c in args.conditions.split(",")]
    stages = [int(s) for s in args.stages.split(",")]

    for cond in conditions:
        prompt = build_prompt(materials[cond])
        save_text(out_path(out_dir, f"prompt_cond{cond}.txt"), prompt)
        prev_id = None
        prev_text = None
        for stage in stages:
            stage_key = STAGE_KEY[stage]
            suffix = STAGE_SUFFIX[stage]
            article_path = out_path(out_dir, f"cond{cond}_{suffix}.md")
            meta_path = out_path(out_dir, f"api_meta_cond{cond}_stage{stage}.json")
            if os.path.exists(article_path) and not args.force:
                print(f"[SKIP] existing: {article_path}")
                prev_text = load_text(article_path)
                if os.path.exists(meta_path):
                    prev_id = load_json(meta_path).get("response_id", prev_id)
                continue
            if stage == 0:
                response = trial02.call_fresh(client, DEVELOPER_MESSAGE, prompt, WRITER_EFFORT,
                                               f"cond{cond}_original")
            else:
                instruction = REVISION_INSTRUCTIONS[stage_key]
                response = trial02.call_with_previous_response_id(client, instruction, WRITER_EFFORT,
                                                                    prev_id, f"cond{cond}_{stage_key}")
            text = response.output_text.strip()
            meta = er015base.response_meta(
                response, prompt if stage == 0 else REVISION_INSTRUCTIONS[stage_key], DEVELOPER_MESSAGE,
                extra={"condition": cond, "stage": stage_key, "effort_requested": WRITER_EFFORT,
                       "chain_method": "fresh" if stage == 0 else "previous_response_id"},
            )
            save_text(article_path, text)
            save_json(meta_path, meta)
            prev_id = response.id
            prev_text = text
            print(f"[OK] cond{cond}_{suffix}: {len(text)}字 model={meta['response_model_actual']} "
                  f"id={response.id}")


# ------------------------------------------------------------
# step: assemble (titles / mechanical_stats / fact_diff / blind / comparison)
# ------------------------------------------------------------
def _load_stage_texts(out_dir: str, cond: int) -> dict:
    texts = {}
    for stage, suffix in STAGE_SUFFIX.items():
        p = out_path(out_dir, f"cond{cond}_{suffix}.md")
        if os.path.exists(p):
            texts[STAGE_KEY[stage]] = load_text(p)
    return texts


def _first_line_title(text: str) -> str:
    for line in text.split("\n"):
        if line.strip():
            return line.strip()
    return ""


def cmd_assemble(args):
    out_dir = args.out_dir
    inputs_dir = out_path(out_dir, "inputs")
    materials = {
        1: load_text(out_path(inputs_dir, "cond1.md")),
        2: load_text(out_path(inputs_dir, "cond2.md")),
        3: strip_cond3_header(load_text(out_path(inputs_dir, "cond3.md"))),
        4: load_text(out_path(inputs_dir, "ledger_cond4.txt")),
    }

    titles = {}
    mechanical = {}
    fact_diff = {}
    all_texts = {}
    for cond in (1, 2, 3, 4):
        texts = _load_stage_texts(out_dir, cond)
        all_texts[cond] = texts
        titles[f"cond{cond}"] = {k: _first_line_title(v) for k, v in texts.items()}
        stat_entry = {}
        material_numbers = set(NUMBER_RE.findall(materials[cond]))
        material_nouns = {n for n in PROPER_NOUNS if n in materials[cond]}
        for stage_key, text in texts.items():
            char_count = len(text)
            paragraph_count = len([p for p in text.split("\n\n") if p.strip()])
            numbers = sorted(set(NUMBER_RE.findall(text)))
            nouns = sorted({n for n in PROPER_NOUNS if n in text})
            echo = ECHO_PHRASE in text
            stat_entry[stage_key] = {
                "char_count": char_count, "paragraph_count": paragraph_count,
                "number_count": len(numbers), "numbers": numbers,
                "proper_noun_count": len(nouns), "proper_nouns": nouns,
                "prompt_echo_phrase_present": echo,
            }
            fact_diff.setdefault(f"cond{cond}", {})[stage_key] = {
                "numbers_not_in_input": sorted(set(numbers) - material_numbers),
                "proper_nouns_not_in_input": sorted(set(nouns) - material_nouns),
            }
        mechanical[f"cond{cond}"] = stat_entry

    save_json(out_path(out_dir, "titles.json"), titles)
    save_json(out_path(out_dir, "mechanical_stats.json"), mechanical)
    save_json(out_path(out_dir, "fact_diff_machine.json"), fact_diff)

    # --- blind_r2.md / blind_key.json ---
    conds_with_r2 = [c for c in (1, 2, 3, 4) if "r2" in all_texts[c]]
    labels = ["A", "B", "C", "D"][:len(conds_with_r2)]
    shuffled = list(conds_with_r2)
    rnd = random.Random(20260924)
    rnd.shuffle(shuffled)
    blind_key = {label: f"cond{cond}" for label, cond in zip(labels, shuffled)}
    blind_lines = ["# Blind R2比較(NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01)",
                   "", "条件名は伏せてある。対応表は blind_key.json 参照。", ""]
    for label, cond in zip(labels, shuffled):
        blind_lines += [f"## 記事{label}", "", all_texts[cond]["r2"], ""]
    save_text(out_path(out_dir, "blind_r2.md"), "\n".join(blind_lines))
    save_json(out_path(out_dir, "blind_key.json"), blind_key)

    # --- comparison_all.md ---
    ref_path = "docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_revision2.md"
    ref_text = load_text(ref_path) if os.path.exists(ref_path) else "(参照ファイルなし)"
    comp_lines = ["# 全条件・全段階 比較(NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01)", ""]
    comp_lines += ["## 参照: 前回R2(trial_02 Article A、Baseline品質の基準)", "", ref_text, "", "---", ""]
    for cond in (1, 2, 3, 4):
        comp_lines += [f"## 条件{cond}", "", "### 入力", "```", materials[cond][:3000], "```", ""]
        for stage_key in ("original", "r1", "r2"):
            if stage_key in all_texts[cond]:
                comp_lines += [f"### 条件{cond} - {stage_key}", "", all_texts[cond][stage_key], ""]
        comp_lines += ["---", ""]
    save_text(out_path(out_dir, "comparison_all.md"), "\n".join(comp_lines))

    print(f"[OK] assemble complete: titles/mechanical_stats/fact_diff_machine/blind_r2/comparison_all written")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def cmd_cost(args):
    """fix01委任: 累計費用(¥40上限)確認用。raw_usage_log.jsonl(theme=THEME_TAG)を集計。"""
    out_dir = args.out_dir
    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    pricing = er015base._load_pricing()
    luna_in = er015base._price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = er015base._price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = er015base._price(pricing, "openai", "gpt-5.6-luna", "output_tokens")
    ws_price_per_1000 = er015base._price(pricing, "openai", "N/A (tool, all models)", "web_search_call")

    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    # 注: trial02.call_fresh/call_with_previous_response_id(cmd_generateがimport再利用)は
    # 内部でtrial02自身のTHEME_TAG("NEWS_ITERATIVE_ENTERTAINMENT_TRIAL_02")を
    # cl.logging_contextへ渡すため、cond{n}系12 callはそのthemeでこのファイルに記録される。
    # <out_dir>/raw_usage_log.jsonlは本Trial専用ファイルのため、themeで絞らず全行を集計する。
    entries = [e for e in entries if e.get("theme") in (THEME_TAG, trial02.THEME_TAG)]

    by_stage = {}
    total_usd = 0.0
    total_ws_calls = total_input = total_output = total_cached = 0
    for e in entries:
        stage = e.get("stage") or "UNKNOWN"
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        ws = e.get("web_search_call_count") or 0
        billable_in = max(it - ct, 0)
        usd = 0.0
        if luna_in is not None:
            usd += (billable_in / 1_000_000) * luna_in
        if luna_cached is not None:
            usd += (ct / 1_000_000) * luna_cached
        if luna_out is not None:
            usd += (ot / 1_000_000) * luna_out
        if ws_price_per_1000 is not None:
            usd += (ws / 1000) * ws_price_per_1000
        s = by_stage.setdefault(stage, {"calls": 0, "input_tokens": 0, "cached_input_tokens": 0,
                                         "output_tokens": 0, "web_search_call_count": 0, "usd": 0.0})
        s["calls"] += 1
        s["input_tokens"] += it
        s["cached_input_tokens"] += ct
        s["output_tokens"] += ot
        s["web_search_call_count"] += ws
        s["usd"] += usd
        total_usd += usd
        total_ws_calls += ws
        total_input += it
        total_output += ot
        total_cached += ct

    for s in by_stage.values():
        s["jpy"] = round(s["usd"] * er015base.USD_TO_JPY, 2)

    result = {
        "theme": THEME_TAG,
        "by_stage": by_stage,
        "total_calls": len(entries),
        "total_input_tokens": total_input,
        "total_cached_input_tokens": total_cached,
        "total_output_tokens": total_output,
        "total_web_search_call_count": total_ws_calls,
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * er015base.USD_TO_JPY, 2),
        "usd_to_jpy": er015base.USD_TO_JPY,
        "pricing_source": "er005_output/cost_baseline_01/pricing_snapshot.json",
        "budget_jpy": 40,
        "within_budget": round(total_usd * er015base.USD_TO_JPY, 2) <= 40,
    }
    save_json(out_path(out_dir, "cost.json"), result)
    print(f"[OK] cost.json: total_calls={len(entries)} total_jpy={result['total_jpy']} "
          f"within_budget={result['within_budget']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["baseline", "sources", "inputs", "generate", "assemble", "cost"])
    parser.add_argument("--target", type=int, default=10)
    parser.add_argument("--conditions", default="1,2,3,4")
    parser.add_argument("--stages", default="0,1,2")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--extra-search-calls", type=int, default=0,
                         help="fix01委任: 前回と異なる語彙での補充検索の最大call数")
    parser.add_argument("--allow-partial", action="store_true",
                         help="fix01委任: 到達数が target 未満でも8以上ならSTOPせず続行する")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    if args.step == "baseline":
        cmd_baseline(args)
    elif args.step == "sources":
        cmd_sources(args)
    elif args.step == "inputs":
        cmd_inputs(args)
    elif args.step == "generate":
        cmd_generate(args)
    elif args.step == "assemble":
        cmd_assemble(args)
    elif args.step == "cost":
        cmd_cost(args)


if __name__ == "__main__":
    main()
