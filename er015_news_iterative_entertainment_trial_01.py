# ============================================================
# er015_news_iterative_entertainment_trial_01.py
# NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01 (Fable設計、2026-09-24)
# ============================================================
# 目的: er015_news_original_baseline_repro_01と同一条件のOriginal Promptで
# 記事を1本生成し、そこへ「もっとエンターテインメント性を高めて」という
# 単純な修正指示のみを3回連鎖させ(Original→R1→R2→R3)、記事がどう変化
# するかを観察するTrial専用スクリプト。**Production実装ではない。改善は
# 一切行わない。修正指示にHook・比喩・驚き等の追加条件は一切付けない。**
#
# Production正式path(er011_*/er014_*等)は一切変更しない。本ファイルは
# er015_news_original_baseline_repro_01(repro01)からOriginal Prompt・
# developer message・model/effort定数をimport再利用し、
# er015_news_core_idea_editorial_trial_01(er015base)からresponse_meta・
# 価格計算ヘルパーを再利用する。両ファイルとも無変更。
#
# 連鎖方式: Responses APIのprevious_response_idで直前応答に連鎖させ、
# userメッセージとして修正指示文のみを送る(developerメッセージは会話
# 文脈に既に含まれるため再送しない)。previous_response_idが使えない
# 場合のみ、直前記事全文を「以下の記事」として同じ修正指示文の前に貼る
# フォールバック方式に切り替え、chain.jsonへどちらを使ったか記録する。
#
# サブコマンド: run --out-dir <OUT> [--force]
#              factdiff --out-dir <OUT> (機械抽出の補助。最終表はSonnetが
#                手動確認して記入する)
#              observe --out-dir <OUT> (字数・段落数等の機械集計)
#              cost --out-dir <OUT>
# 冪等性: 各段階のファイルが既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_original_baseline_repro_01 as repro01

THEME_TAG = "NEWS_ITERATIVE_ENTERTAINMENT_TRIAL_01"
WRITER_MODEL = repro01.WRITER_MODEL
WRITER_EFFORT = repro01.WRITER_EFFORT
DEVELOPER_MESSAGE = repro01.DEVELOPER_MESSAGE
R0_PROMPT = repro01.R0_PROMPT

# ユーザー指示原文の逐語(Fable設計を変更しない)。Sonnet/Fableは一切の
# 追加条件を付けない。
REVISION_INSTRUCTIONS = {
    "r1": "この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。",
    "r2": "この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。",
    "r3": "この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。",
}


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


def cmd_run(args):
    out_dir = args.out_dir
    install_logger(out_dir)
    client = vfl01.get_client()
    save_text(out_path(out_dir, "prompt_original.txt"), R0_PROMPT)

    chain_path = out_path(out_dir, "chain.json")
    chain = {"chain_method": None, "stages": []}
    if os.path.exists(chain_path) and not args.force:
        chain = json.loads(load_text(chain_path))

    # --- Original ---
    original_path = out_path(out_dir, "original.md")
    original_meta_path = out_path(out_dir, "api_meta_original.json")
    if os.path.exists(original_path) and not args.force:
        print(f"[SKIP] 既存出力あり(--forceなし): {original_path}")
        prev_meta = json.loads(load_text(original_meta_path))
        prev_id = prev_meta["response_id"]
    else:
        response = call_fresh(client, DEVELOPER_MESSAGE, R0_PROMPT, WRITER_EFFORT, "original")
        article = response.output_text.strip()
        meta = er015base.response_meta(
            response, R0_PROMPT, DEVELOPER_MESSAGE,
            extra={"stage": "original", "effort_requested": WRITER_EFFORT},
        )
        save_text(original_path, article)
        save_json(original_meta_path, meta)
        chain["stages"] = [s for s in chain["stages"] if s["stage"] != "original"]
        chain["stages"].append({"stage": "original", "response_id": response.id, "model": response.model})
        save_json(chain_path, chain)
        prev_id = response.id
        print(f"[OK] original: {len(article)}字 model={meta['response_model_actual']} id={response.id}")

    prev_text = load_text(original_path)
    chain_method = chain.get("chain_method")

    # --- Revisions (r1 -> r2 -> r3, 直前記事を必ず修正対象にする連鎖) ---
    for stage_key in ["r1", "r2", "r3"]:
        num = stage_key[1]
        stage_path = out_path(out_dir, f"revision{num}.md")
        meta_path = out_path(out_dir, f"api_meta_{stage_key}.json")
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
                    client, instruction, WRITER_EFFORT, prev_id, stage_key,
                )
                used_method = "previous_response_id"
            except Exception as e:  # noqa: BLE001 - 技術的失敗時のみフォールバック
                print(f"[WARN] previous_response_id失敗、フォールバックへ切替({stage_key}): {e}")
                response = None

        if response is None:
            fallback_user = f"以下の記事:\n\n{prev_text}\n\n{instruction}"
            response = call_fresh(client, DEVELOPER_MESSAGE, fallback_user, WRITER_EFFORT, stage_key)
            used_method = "fallback_full_text"

        chain_method = used_method
        article = response.output_text.strip()
        meta = er015base.response_meta(
            response, instruction, DEVELOPER_MESSAGE,
            extra={
                "stage": stage_key,
                "effort_requested": WRITER_EFFORT,
                "chain_method": used_method,
                "previous_response_id_used": prev_id if used_method == "previous_response_id" else None,
            },
        )
        save_text(stage_path, article)
        save_json(meta_path, meta)
        chain["stages"] = [s for s in chain["stages"] if s["stage"] != stage_key]
        chain["stages"].append({
            "stage": stage_key, "response_id": response.id, "model": response.model,
            "chain_method": used_method,
        })
        chain["chain_method"] = chain_method
        save_json(chain_path, chain)

        prev_id = response.id
        prev_text = article
        print(f"[OK] {stage_key}: {len(article)}字 model={meta['response_model_actual']} chain_method={used_method}")

    chain["chain_method"] = chain_method
    save_json(chain_path, chain)


STAGE_FILES = {
    "original": "original.md",
    "r1": "revision1.md",
    "r2": "revision2.md",
    "r3": "revision3.md",
}

# repro01のkeyword一覧を再利用(Ledger上の固有名詞・数字と対応)。
KEYWORDS = list(repro01.KEYWORDS)
NUMBER_RE = re.compile(r"\d+(?:[,\.]\d+)?")


def _load_stage_texts(out_dir: str) -> dict:
    texts = {}
    for key, fname in STAGE_FILES.items():
        p = out_path(out_dir, fname)
        if os.path.exists(p):
            texts[key] = load_text(p)
    return texts


def cmd_factdiff(args):
    out_dir = args.out_dir
    texts = _load_stage_texts(out_dir)
    result = {}
    for key, text in texts.items():
        numbers = sorted(set(NUMBER_RE.findall(text)))
        kw_counts = {kw: text.count(kw) for kw in KEYWORDS if text.count(kw) > 0}
        result[key] = {
            "char_count": len(text),
            "numbers_found": numbers,
            "keyword_counts": kw_counts,
        }
    if "original" in result:
        orig_numbers = set(result["original"]["numbers_found"])
        orig_keywords = set(result["original"]["keyword_counts"].keys())
        for key in ("r1", "r2", "r3"):
            if key not in result:
                continue
            new_numbers = sorted(set(result[key]["numbers_found"]) - orig_numbers)
            new_keywords = sorted(set(result[key]["keyword_counts"].keys()) - orig_keywords)
            result[key]["numbers_not_in_original"] = new_numbers
            result[key]["keywords_not_in_original"] = new_keywords
    save_json(out_path(out_dir, "fact_diff_machine.json"), result)
    for key, r in result.items():
        extra = ""
        if "numbers_not_in_original" in r:
            extra = f" new_numbers={r['numbers_not_in_original']} new_keywords={r['keywords_not_in_original']}"
        print(f"[OK] {key}: {r['char_count']}字{extra}")


def _paragraph_count(text: str) -> int:
    paras = [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    return len(paras)


def _question_count(text: str) -> int:
    return text.count("？") + text.count("?")


def _first_sentence(text: str) -> str:
    body = text.strip()
    # タイトル行(先頭行)を除いた本文の最初の一文を取り出す
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
    texts = _load_stage_texts(out_dir)
    result = {}
    for key, text in texts.items():
        numbers = NUMBER_RE.findall(text)
        kw_hits = sum(text.count(kw) for kw in KEYWORDS)
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
    save_json(out_path(out_dir, "observation_machine.json"), result)
    for key, r in result.items():
        print(f"[OK] {key}: {r['char_count']}字 paragraphs={r['paragraph_count']} "
              f"questions={r['question_count']} numbers={r['number_token_count']}")


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

    p_run = sub.add_parser("run")
    p_run.add_argument("--out-dir", required=True)
    p_run.add_argument("--force", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_fd = sub.add_parser("factdiff")
    p_fd.add_argument("--out-dir", required=True)
    p_fd.set_defaults(func=cmd_factdiff)

    p_ob = sub.add_parser("observe")
    p_ob.add_argument("--out-dir", required=True)
    p_ob.set_defaults(func=cmd_observe)

    p_cost = sub.add_parser("cost")
    p_cost.add_argument("--out-dir", required=True)
    p_cost.set_defaults(func=cmd_cost)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
