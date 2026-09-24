# ============================================================
# er015_news_iterative_entertainment_trial_02.py
# NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02 (Fable設計、2026-09-24)
# ============================================================
# 目的: er015_news_iterative_entertainment_trial_01(下水道テーマ)と**同一
# 方式**(Original Prompt→単純な修正指示のみをOriginal→R1→R2→R3の順で
# previous_response_idで会話連鎖)を、性質の異なる2記事(A: Meta AI電話代行の
# 「人間コンシェルジュ」実験/B: 旅行用圧縮ポーチ)で実行し、R2止め/R3までの
# Evidenceを増やすTrial専用スクリプト。**Production実装ではない。方式変更は
# 一切行わない。修正指示にHook・比喩・驚き等の追加条件は一切付けない。**
#
# Production正式path(er011_*/er014_*等)は一切変更しない。本ファイルは
# er015_news_original_baseline_repro_01(repro01)からOriginal Prompt本体
# (P7)・developer message・model/effort定数をimport再利用し、
# er015_news_core_idea_editorial_trial_01(er015base)からresponse_meta・
# 価格計算ヘルパーを再利用する。er015_news_iterative_entertainment_trial_01
# (trial01)からRevision指示文(逐語)を再利用する。いずれも無変更。
#
# 下水道Trial-01との条件差: Trial-01はテーマ1行のみ・素材なしだったが、
# 本Trialのテーマ(A: Meta Muse電話代行実験という特定の出来事、B: 旅行用
# 圧縮ポーチという実在商品カテゴリ)は素材なしではLunaが詳細を創作する
# 恐れが高いため、P7末尾([ニュース]欄、REPRO-01 T0と同じ挿入位置)に
# 実在の元記事(HTTP取得確認済み)に基づく中立的な素材(2〜3文)を追加している。
# これは下水道Trial-01との比較可能性に影響する差異であり、REPORTに明記する。
#
# 連鎖方式: trial01と同一(previous_response_idで直前応答に連鎖、userメッセージ
# として修正指示文のみを送る。previous_response_idが使えない場合のみ、直前
# 記事全文を「以下の記事」として貼るフォールバック方式に切り替え、chain.json
# へどちらを使ったか記録する)。
#
# サブコマンド: sources --out-dir <OUT> (元記事URLのHTTP取得確認・sources.md
#                書き出し。素材文自体はSonnetが手動確認して本ファイルへ定数
#                として記入済み)
#              run --article A|B --out-dir <OUT> [--force]
#              factdiff --out-dir <OUT> (機械抽出の補助。最終表はSonnetが
#                手動確認して記入する)
#              observe --out-dir <OUT> (字数・段落数等の機械集計)
#              latency --out-dir <OUT> (raw_usage_log.jsonlのelapsed_secondsを
#                stage別・記事別に集計、Original->R2/R3累計を算出)
#              cost --out-dir <OUT>
# 冪等性: 各段階のファイルが既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re

import requests

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_iterative_entertainment_trial_01 as trial01
import er015_news_original_baseline_repro_01 as repro01

THEME_TAG = "NEWS_ITERATIVE_ENTERTAINMENT_TRIAL_02"
WRITER_MODEL = repro01.WRITER_MODEL
WRITER_EFFORT = repro01.WRITER_EFFORT
DEVELOPER_MESSAGE = repro01.DEVELOPER_MESSAGE

# ユーザー指示原文の逐語(trial01と完全同一文言、Fable/Sonnetは一切の追加条件
# を付けない)。
REVISION_INSTRUCTIONS = dict(trial01.REVISION_INSTRUCTIONS)

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# ------------------------------------------------------------
# 元記事(REPRO-01 phase4診断(a)で特定済みURL。今回Sonnetが実際にHTTP取得
# して確認した)
# ------------------------------------------------------------
SOURCE_META = {
    "A": {
        "topic": "Meta Muse AI電話代行「人間コンシェルジュ」実験",
        "url": "https://www.marketscreener.com/news/meta-testing-a-human-concierge-for-its-new-personal-ai-agent-muse-ce785ad8de8cf025",
        "published_time_as_shown": "NEW YORK, Sept 22 (Reuters); reader-proxy取得時のPublished Timeメタ情報: 2026-09-22T12:02:39-04:00",
        "reference_source": "er016_output/topic_selection_chatgpt_repro_01/phase4_diag_a.json reference_id=1",
        "fetch_note": "直接requests.get()はAkamai Access Denied(403相当)で本文非取得。"
                       "reader proxy(https://r.jina.ai/<url>)経由でReuters配信本文を取得・確認した。",
    },
    "B": {
        "topic": "旅行用圧縮ポーチ(トラベルポーチ)人気ランキング",
        "url": "https://kenja-monosashi.com/travel-packing-cube",
        "published_time_as_shown": "2026年9月23日 更新",
        "reference_source": "er016_output/topic_selection_chatgpt_repro_01/phase4_diag_a.json reference_id=13",
        "fetch_note": "直接requests.get()で本文取得成功(200)。",
    },
}

# Sonnetが元記事本文(HTTP取得結果)のみから作成した中立的な素材(2〜3文、
# 推測・脚色なし、出典URL・公開時刻はsources.md参照)。
MATERIAL_A = (
    "Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、"
    "一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、"
    "Reutersが確認した社内投稿で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、"
    "Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。"
)
MATERIAL_B = (
    "「賢者のモノサシ」の旅行用圧縮ポーチ特集(2026年9月23日更新)によると、"
    "圧縮トラベルポーチを使うと衣類の厚みが1〜2段階薄くなり、スーツケースの容量を10〜20%削減できるとされる。"
    "圧縮方式にはファスナー式と真空圧縮袋式の2種類があり、楽天ランキング上位の売れ筋4点セットは700円〜1,190円前後で販売されている。"
)
MATERIAL = {"A": MATERIAL_A, "B": MATERIAL_B}

# P7の「テーマ：」行の差し替え文言(Fable設計、元記事の事実に合わせてSonnetが
# 最小限調整。Hook文言をそのまま書かない)。
THEME_LINE = {
    "A": "テーマ：MetaのAI電話代行が、通話の一部を裏で人間スタッフに担当させる実験を行っている",
    "B": "テーマ：旅行用の圧縮ポーチが人気、荷物はなぜ毎回バッグいっぱいになるのか",
}

# factdiffで使う記事別keyword一覧(素材文中の固有名詞・専門語)。
KEYWORDS = {
    "A": ["Meta", "Muse", "人間コンシェルジュ", "Reuters", "契約スタッフ", "プライバシー",
          "ロールバック", "rolled back", "人種", "Superintelligence", "Facebook", "Instagram"],
    "B": ["賢者のモノサシ", "圧縮ポーチ", "トラベルポーチ", "ファスナー式", "真空圧縮袋",
          "楽天", "スーツケース", "YKK"],
}

NUMBER_RE = re.compile(r"\d+(?:[,\.]\d+)?")


def build_prompt(article: str) -> str:
    base = repro01.R0_PROMPT
    lines = base.split("\n")
    new_lines = [THEME_LINE[article] if l.startswith("テーマ：") else l for l in lines]
    prompt = "\n".join(new_lines)
    prompt += "\n\n[ニュース]\n" + MATERIAL[article]
    return prompt


PROMPTS = {"A": build_prompt("A"), "B": build_prompt("B")}


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


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def call_fresh(client, developer: str, user: str, effort: str, stage: str):
    """developerメッセージ付きの新規会話としてcall(Original・フォールバック用)。"""
    kwargs = dict(
        model=WRITER_MODEL,
        reasoning={"effort": effort},
        input=[
            {"role": "developer", "content": developer},
            {"role": "user", "content": user},
        ],
    )
    with cl.logging_context(THEME_TAG, stage):
        response = client.responses.create(**kwargs)
    return response


def call_with_previous_response_id(client, user: str, effort: str, previous_response_id: str, stage: str):
    """previous_response_idで直前応答に連鎖させ、修正指示文のみを送る。"""
    kwargs = dict(
        model=WRITER_MODEL,
        reasoning={"effort": effort},
        previous_response_id=previous_response_id,
        input=[
            {"role": "user", "content": user},
        ],
    )
    with cl.logging_context(THEME_TAG, stage):
        response = client.responses.create(**kwargs)
    return response


# ------------------------------------------------------------
# sources: 元記事URLのHTTP取得確認・sources.md書き出し
# ------------------------------------------------------------
def fetch_url_evidence(url: str) -> dict:
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 2000:
            return {
                "url": url, "method": "direct", "http_status": resp.status_code,
                "content_length_bytes": len(resp.content),
            }
        raise RuntimeError(f"direct fetch insufficient(status={resp.status_code}, "
                            f"len={len(resp.content)})")
    except Exception as e:  # noqa: BLE001 - 技術的失敗時のみproxyへ
        direct_error = str(e)
    try:
        resp = requests.get(f"https://r.jina.ai/{url}", timeout=40)
        return {
            "url": url, "method": "reader_proxy(r.jina.ai)", "http_status": resp.status_code,
            "content_length_bytes": len(resp.content), "direct_fetch_error": direct_error,
        }
    except Exception as e2:  # noqa: BLE001
        return {"url": url, "method": None, "fetch_status": "FAILED",
                "direct_fetch_error": direct_error, "proxy_fetch_error": str(e2)}


def cmd_sources(args):
    out_dir = args.out_dir
    evidence = {}
    for article in ("A", "B"):
        meta = SOURCE_META[article]
        ev = fetch_url_evidence(meta["url"])
        evidence[article] = ev
        save_json(out_path(out_dir, f"fetch_evidence_{article}.json"), ev)
        print(f"[OK] fetch {article}: method={ev.get('method')} status={ev.get('http_status')}")

    lines = ["# 元記事・素材(NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02)", ""]
    for article in ("A", "B"):
        meta = SOURCE_META[article]
        ev = evidence[article]
        lines += [
            f"## Article {article}: {meta['topic']}",
            "",
            f"- URL: {meta['url']}",
            f"- 公開時刻(表示のまま): {meta['published_time_as_shown']}",
            f"- 出典特定元: {meta['reference_source']}",
            f"- 取得方法: {meta['fetch_note']}",
            f"- 本タスクでの再取得確認(evidence): method={ev.get('method')} "
            f"http_status={ev.get('http_status')} bytes={ev.get('content_length_bytes')}",
            "",
            "### 素材文(2〜3文、[ニュース]欄へ挿入。元記事本文の事実のみ、推測・脚色なし)",
            "",
            MATERIAL[article],
            "",
        ]
    save_text(out_path(out_dir, "sources.md"), "\n".join(lines))
    save_text(out_path(out_dir, "prompt_A.txt"), PROMPTS["A"])
    save_text(out_path(out_dir, "prompt_B.txt"), PROMPTS["B"])
    print(f"[OK] sources.md / prompt_A.txt / prompt_B.txt written")


# ------------------------------------------------------------
# run: Original -> R1 -> R2 -> R3 (記事ごと)
# ------------------------------------------------------------
def cmd_run(args):
    out_dir = args.out_dir
    article = args.article
    install_logger(out_dir)
    client = vfl01.get_client()
    prompt = PROMPTS[article]
    save_text(out_path(out_dir, f"prompt_{article}.txt"), prompt)

    chain_path = out_path(out_dir, "chain.json")
    chain = {"articles": {}}
    if os.path.exists(chain_path):
        chain = json.loads(load_text(chain_path))
    chain.setdefault("articles", {})
    art_chain = chain["articles"].get(article, {"chain_method": None, "stages": []})

    # --- Original ---
    original_path = out_path(out_dir, f"{article}_original.md")
    original_meta_path = out_path(out_dir, f"api_meta_{article}_original.json")
    if os.path.exists(original_path) and not args.force:
        print(f"[SKIP] 既存出力あり(--forceなし): {original_path}")
        prev_meta = json.loads(load_text(original_meta_path))
        prev_id = prev_meta["response_id"]
    else:
        response = call_fresh(client, DEVELOPER_MESSAGE, prompt, WRITER_EFFORT, f"{article}_original")
        text = response.output_text.strip()
        meta = er015base.response_meta(
            response, prompt, DEVELOPER_MESSAGE,
            extra={"article": article, "stage": "original", "effort_requested": WRITER_EFFORT},
        )
        save_text(original_path, text)
        save_json(original_meta_path, meta)
        art_chain["stages"] = [s for s in art_chain["stages"] if s["stage"] != "original"]
        art_chain["stages"].append({"stage": "original", "response_id": response.id, "model": response.model})
        chain["articles"][article] = art_chain
        save_json(chain_path, chain)
        prev_id = response.id
        print(f"[OK] {article}_original: {len(text)}字 model={meta['response_model_actual']} id={response.id}")

    prev_text = load_text(original_path)
    chain_method = art_chain.get("chain_method")

    for stage_key in ["r1", "r2", "r3"]:
        num = stage_key[1]
        stage_path = out_path(out_dir, f"{article}_revision{num}.md")
        meta_path = out_path(out_dir, f"api_meta_{article}_{stage_key}.json")
        instruction = REVISION_INSTRUCTIONS[stage_key]

        if os.path.exists(stage_path) and not args.force:
            print(f"[SKIP] 既存出力あり(--forceなし): {stage_path}")
            prev_text = load_text(stage_path)
            if os.path.exists(meta_path):
                m = json.loads(load_text(meta_path))
                prev_id = m.get("response_id", prev_id)
                chain_method = m.get("chain_method", chain_method)
            continue

        response = None
        used_method = None
        if chain_method != "fallback_full_text":
            try:
                response = call_with_previous_response_id(
                    client, instruction, WRITER_EFFORT, prev_id, f"{article}_{stage_key}",
                )
                used_method = "previous_response_id"
            except Exception as e:  # noqa: BLE001 - 技術的失敗時のみフォールバック
                print(f"[WARN] previous_response_id失敗、フォールバックへ切替({article}_{stage_key}): {e}")
                response = None

        if response is None:
            fallback_user = f"以下の記事:\n\n{prev_text}\n\n{instruction}"
            response = call_fresh(client, DEVELOPER_MESSAGE, fallback_user, WRITER_EFFORT, f"{article}_{stage_key}")
            used_method = "fallback_full_text"

        chain_method = used_method
        text = response.output_text.strip()
        meta = er015base.response_meta(
            response, instruction, DEVELOPER_MESSAGE,
            extra={
                "article": article, "stage": stage_key, "effort_requested": WRITER_EFFORT,
                "chain_method": used_method,
                "previous_response_id_used": prev_id if used_method == "previous_response_id" else None,
            },
        )
        save_text(stage_path, text)
        save_json(meta_path, meta)
        art_chain["stages"] = [s for s in art_chain["stages"] if s["stage"] != stage_key]
        art_chain["stages"].append({
            "stage": stage_key, "response_id": response.id, "model": response.model,
            "chain_method": used_method,
        })
        art_chain["chain_method"] = chain_method
        chain["articles"][article] = art_chain
        save_json(chain_path, chain)

        prev_id = response.id
        prev_text = text
        print(f"[OK] {article}_{stage_key}: {len(text)}字 model={meta['response_model_actual']} chain_method={used_method}")

    art_chain["chain_method"] = chain_method
    chain["articles"][article] = art_chain
    save_json(chain_path, chain)


STAGE_SUFFIX = {"original": "original", "r1": "revision1", "r2": "revision2", "r3": "revision3"}


def _load_stage_texts(out_dir: str, article: str) -> dict:
    texts = {}
    for key, suffix in STAGE_SUFFIX.items():
        p = out_path(out_dir, f"{article}_{suffix}.md")
        if os.path.exists(p):
            texts[key] = load_text(p)
    return texts


def cmd_factdiff(args):
    out_dir = args.out_dir
    all_result = {}
    for article in ("A", "B"):
        material = MATERIAL[article]
        keywords = KEYWORDS[article]
        mat_numbers = set(NUMBER_RE.findall(material))
        mat_keywords = {kw for kw in keywords if kw in material}
        texts = _load_stage_texts(out_dir, article)
        result = {}
        for key, text in texts.items():
            numbers = sorted(set(NUMBER_RE.findall(text)))
            kw_counts = {kw: text.count(kw) for kw in keywords if text.count(kw) > 0}
            result[key] = {
                "char_count": len(text),
                "numbers_found": numbers,
                "keyword_counts": kw_counts,
                "numbers_not_in_material": sorted(set(numbers) - mat_numbers),
                "keywords_not_in_material": sorted(set(kw_counts.keys()) - mat_keywords),
            }
        if "original" in result:
            orig_numbers = set(result["original"]["numbers_found"])
            orig_keywords = set(result["original"]["keyword_counts"].keys())
            for key in ("r1", "r2", "r3"):
                if key not in result:
                    continue
                result[key]["numbers_not_in_original"] = sorted(set(result[key]["numbers_found"]) - orig_numbers)
                result[key]["keywords_not_in_original"] = sorted(set(result[key]["keyword_counts"].keys()) - orig_keywords)
        all_result[article] = result
        save_json(out_path(out_dir, f"fact_diff_machine_{article}.json"), result)
        for key, r in result.items():
            print(f"[OK] {article}/{key}: {r['char_count']}字 "
                  f"not_in_material_numbers={r['numbers_not_in_material']} "
                  f"not_in_material_keywords={r['keywords_not_in_material']}")


def _paragraph_count(text: str) -> int:
    paras = [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    return len(paras)


def _question_count(text: str) -> int:
    return text.count("？") + text.count("?")


def _first_sentence(text: str) -> str:
    body = text.strip()
    lines = [l for l in body.splitlines() if l.strip()]
    if not lines:
        return ""
    body_text = "\n".join(lines[1:]) if len(lines) > 1 else lines[0]
    body_text = body_text.strip()
    m = re.search(r"^(.*?[。！？!?])", body_text, re.DOTALL)
    return (m.group(1) if m else body_text[:60]).replace("\n", "")


def _last_sentence(text: str) -> str:
    body = text.strip()
    sentences = re.split(r"(?<=[。！？!?])", body)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences[-1] if sentences else ""


def _title_line(text: str) -> str:
    lines = [l for l in text.strip().splitlines() if l.strip()]
    return lines[0] if lines else ""


def cmd_observe(args):
    out_dir = args.out_dir
    for article in ("A", "B"):
        keywords = KEYWORDS[article]
        texts = _load_stage_texts(out_dir, article)
        result = {}
        for key, text in texts.items():
            numbers = NUMBER_RE.findall(text)
            kw_hits = sum(text.count(kw) for kw in keywords)
            result[key] = {
                "char_count": len(text),
                "title": _title_line(text),
                "first_sentence": _first_sentence(text),
                "last_sentence": _last_sentence(text),
                "paragraph_count": _paragraph_count(text),
                "question_count": _question_count(text),
                "reservation_markers": {
                    "もちろん": text.count("もちろん"),
                    "ただし": text.count("ただし"),
                },
                "number_token_count": len(numbers),
                "keyword_hit_count": kw_hits,
            }
        save_json(out_path(out_dir, f"observation_machine_{article}.json"), result)
        for key, r in result.items():
            print(f"[OK] {article}/{key}: {r['char_count']}字 paragraphs={r['paragraph_count']} "
                  f"questions={r['question_count']} numbers={r['number_token_count']}")


def cmd_latency(args):
    out_dir = args.out_dir
    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    entries = [e for e in entries if e.get("theme") == THEME_TAG]

    result = {"per_call": [], "by_article": {}}
    for article in ("A", "B"):
        stages_order = ["original", "r1", "r2", "r3"]
        by_stage = {}
        for e in entries:
            stage = e.get("stage") or ""
            prefix = f"{article}_"
            if not stage.startswith(prefix):
                continue
            key = stage[len(prefix):]
            by_stage[key] = e.get("elapsed_seconds")
            result["per_call"].append({
                "article": article, "stage": key, "elapsed_seconds": e.get("elapsed_seconds"),
                "timestamp": e.get("timestamp"), "model_id": e.get("model_id"),
            })
        cum = 0.0
        cum_by_stage = {}
        for key in stages_order:
            v = by_stage.get(key)
            if v is None:
                cum_by_stage[key] = None
                continue
            cum += v
            cum_by_stage[key] = round(cum, 3)
        result["by_article"][article] = {
            "elapsed_seconds_by_stage": by_stage,
            "cumulative_seconds_by_stage": cum_by_stage,
            "cumulative_to_r2": cum_by_stage.get("r2"),
            "cumulative_to_r3": cum_by_stage.get("r3"),
        }
    save_json(out_path(out_dir, "latency.json"), result)
    for article, r in result["by_article"].items():
        print(f"[OK] {article}: to_r2={r['cumulative_to_r2']}s to_r3={r['cumulative_to_r3']}s")


def cmd_cost(args):
    out_dir = args.out_dir
    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    pricing = er015base._load_pricing()
    luna_in = er015base._price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = er015base._price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = er015base._price(pricing, "openai", "gpt-5.6-luna", "output_tokens")

    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    entries = [e for e in entries if e.get("theme") == THEME_TAG]

    per_call = []
    total_usd = 0.0
    total_input = total_output = total_cached = 0
    for e in entries:
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        billable_in = max(it - ct, 0)
        usd = 0.0
        if luna_in is not None:
            usd += (billable_in / 1_000_000) * luna_in
        if luna_cached is not None:
            usd += (ct / 1_000_000) * luna_cached
        if luna_out is not None:
            usd += (ot / 1_000_000) * luna_out
        per_call.append({
            "stage": e.get("stage"), "input_tokens": it, "cached_input_tokens": ct,
            "output_tokens": ot, "usd": round(usd, 6),
        })
        total_usd += usd
        total_input += it
        total_output += ot
        total_cached += ct

    result = {
        "theme": THEME_TAG,
        "total_calls": len(entries),
        "per_call": per_call,
        "total_input_tokens": total_input,
        "total_cached_input_tokens": total_cached,
        "total_output_tokens": total_output,
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * er015base.USD_TO_JPY, 2),
        "usd_to_jpy": er015base.USD_TO_JPY,
    }
    save_json(out_path(out_dir, "cost.json"), result)
    print(f"[OK] cost: total_jpy={result['total_jpy']} total_calls={result['total_calls']}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_src = sub.add_parser("sources")
    p_src.add_argument("--out-dir", required=True)
    p_src.set_defaults(func=cmd_sources)

    p_run = sub.add_parser("run")
    p_run.add_argument("--out-dir", required=True)
    p_run.add_argument("--article", required=True, choices=["A", "B"])
    p_run.add_argument("--force", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_fd = sub.add_parser("factdiff")
    p_fd.add_argument("--out-dir", required=True)
    p_fd.set_defaults(func=cmd_factdiff)

    p_ob = sub.add_parser("observe")
    p_ob.add_argument("--out-dir", required=True)
    p_ob.set_defaults(func=cmd_observe)

    p_lat = sub.add_parser("latency")
    p_lat.add_argument("--out-dir", required=True)
    p_lat.set_defaults(func=cmd_latency)

    p_cost = sub.add_parser("cost")
    p_cost.add_argument("--out-dir", required=True)
    p_cost.set_defaults(func=cmd_cost)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
