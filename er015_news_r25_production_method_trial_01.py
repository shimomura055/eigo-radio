# ============================================================
# er015_news_r25_production_method_trial_01.py
# NEWS-R25-PRODUCTION-METHOD-TRIAL-01 (Fable設計、2026-09-24)
# ============================================================
# 目的: NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01で得た「R2〜R3の中間
# (R2.5)」品質を、少ないAPI call数で再現できる量産方式を比較するTrial。
# Fableが絞った3方式(A: Lens→Writer 2call / B: 1-call自己編集 / F1:
# 既存草稿+目標Revision1回)を同一テーマ・同一Writer・同一effortで各1回
# 生成する。**Production実装ではない。Prompt文言は委任文の逐語を厳守し
# 改変・追加条件は一切行わない。**
#
# Production正式path(er011_*/er014_*等)は一切変更しない。本ファイルは
# er015_news_original_baseline_repro_01(repro01)からBaseline Prompt(P7)・
# developer message・model/effort定数をimport再利用し、
# er015_news_core_idea_editorial_trial_01(er015base)からresponse_meta・
# 価格計算ヘルパーを再利用する。er015_news_iterative_entertainment_
# trial_01(iterトライアル)から連鎖呼び出し(previous_response_id)実装を
# 再利用する。いずれも無変更。
#
# サブコマンド: run --method A|B|F1 --out-dir <OUT> [--force]
#              observe --out-dir <OUT> (字数・段落数等の機械集計)
#              cost --out-dir <OUT>
# 冪等性: 各方式の出力ファイルが既に存在する場合、--forceなしでは
# 再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_iterative_entertainment_trial_01 as itertrial
import er015_news_original_baseline_repro_01 as repro01

THEME_TAG = "NEWS_R25_PRODUCTION_METHOD_TRIAL_01"
WRITER_MODEL = repro01.WRITER_MODEL
WRITER_EFFORT = repro01.WRITER_EFFORT
DEVELOPER_MESSAGE = repro01.DEVELOPER_MESSAGE
P7 = repro01.R0_PROMPT  # Baseline Prompt(逐語再利用、変更なし)

THEME_LINE = "テーマ：老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討"

# ------------------------------------------------------------
# 方式A: Lens→Writer(2 call)
# ------------------------------------------------------------
A_LENS_PROMPT = (
    THEME_LINE
    + "\n\n"
    + "このニュースを、人が続きを聞きたくなる読み物にするなら、どんな「見方」が"
    "一番面白いか。その見方を1文で書いてください。見方だけを出力してください。"
)


def build_a_writer_prompt(lens_sentence: str) -> str:
    """P7の「テーマ：…」行の直後に「見方：<lens_sentence>」を1行挿入する(他は逐語)。"""
    lines = P7.splitlines()
    out_lines = []
    inserted = False
    for line in lines:
        out_lines.append(line)
        if not inserted and line.strip() == THEME_LINE:
            out_lines.append(f"見方：{lens_sentence}")
            inserted = True
    if not inserted:
        raise RuntimeError("P7内にテーマ行が見つからず、見方行を挿入できませんでした。")
    return "\n".join(out_lines)


# ------------------------------------------------------------
# 方式B: 1-call自己編集
# ------------------------------------------------------------
B_INSERT_PARAGRAPH = (
    "記事を組み立てたら、公開前の編集者として「もっと聞きたくなるか」を見直し、"
    "必要ならタイトル・冒頭・見方・比喩を直してから、最終稿だけを出力してください。"
)

OUTPUT_ONLY_LINE = "出力はタイトルと本文のみ。"


def build_b_prompt() -> str:
    """P7の末尾(「出力はタイトルと本文のみ。」の前)にB_INSERT_PARAGRAPHを挿入する。"""
    if OUTPUT_ONLY_LINE not in P7:
        raise RuntimeError("P7内に「出力はタイトルと本文のみ。」行が見つかりません。")
    return P7.replace(OUTPUT_ONLY_LINE, B_INSERT_PARAGRAPH + "\n\n" + OUTPUT_ONLY_LINE)


# ------------------------------------------------------------
# 方式F1: 既存草稿(Original) + 目標Revision 1回
# ------------------------------------------------------------
F1_INSTRUCTION = (
    "この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に"
    "修正してください。冒頭は暮らしの場面から入り、記事全体は一つの見方で通し、"
    "比喩や見立ては増やさないでください。"
)

ITER_TRIAL_OUT_DIR = os.path.join("er015_output", "news_iterative_entertainment_trial_01")


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


def run_method_a(client, out_dir: str, force: bool) -> None:
    prompts_dir = out_path(out_dir, "prompts")
    lens_path = out_path(out_dir, "A_lens.md")
    article_path = out_path(out_dir, "A_article.md")
    meta_a1_path = out_path(out_dir, "api_meta_A1.json")
    meta_a2_path = out_path(out_dir, "api_meta_A2.json")

    save_text(out_path(prompts_dir, "A1_lens_prompt.txt"), A_LENS_PROMPT)

    if os.path.exists(lens_path) and not force:
        print(f"[SKIP] 既存出力あり(--forceなし): {lens_path}")
        lens_sentence = load_text(lens_path).strip()
    else:
        response = call_fresh(client, DEVELOPER_MESSAGE, A_LENS_PROMPT, WRITER_EFFORT, "A1_lens")
        lens_sentence = response.output_text.strip()
        meta = er015base.response_meta(
            response, A_LENS_PROMPT, DEVELOPER_MESSAGE,
            extra={"stage": "A1_lens", "effort_requested": WRITER_EFFORT},
        )
        save_text(lens_path, lens_sentence)
        save_json(meta_a1_path, meta)
        print(f"[OK] A1_lens: {len(lens_sentence)}字 model={meta['response_model_actual']} id={response.id}")

    writer_prompt = build_a_writer_prompt(lens_sentence)
    save_text(out_path(prompts_dir, "A2_writer_prompt.txt"), writer_prompt)

    if os.path.exists(article_path) and not force:
        print(f"[SKIP] 既存出力あり(--forceなし): {article_path}")
        return

    response = call_fresh(client, DEVELOPER_MESSAGE, writer_prompt, WRITER_EFFORT, "A2_writer")
    article = response.output_text.strip()
    meta = er015base.response_meta(
        response, writer_prompt, DEVELOPER_MESSAGE,
        extra={"stage": "A2_writer", "effort_requested": WRITER_EFFORT},
    )
    save_text(article_path, article)
    save_json(meta_a2_path, meta)
    print(f"[OK] A2_writer(A_article): {len(article)}字 model={meta['response_model_actual']} id={response.id}")


def run_method_b(client, out_dir: str, force: bool) -> None:
    prompts_dir = out_path(out_dir, "prompts")
    article_path = out_path(out_dir, "B_article.md")
    meta_path = out_path(out_dir, "api_meta_B.json")

    b_prompt = build_b_prompt()
    save_text(out_path(prompts_dir, "B_prompt.txt"), b_prompt)

    if os.path.exists(article_path) and not force:
        print(f"[SKIP] 既存出力あり(--forceなし): {article_path}")
        return

    response = call_fresh(client, DEVELOPER_MESSAGE, b_prompt, WRITER_EFFORT, "B")
    article = response.output_text.strip()
    meta = er015base.response_meta(
        response, b_prompt, DEVELOPER_MESSAGE,
        extra={"stage": "B", "effort_requested": WRITER_EFFORT},
    )
    save_text(article_path, article)
    save_json(meta_path, meta)
    print(f"[OK] B(B_article): {len(article)}字 model={meta['response_model_actual']} id={response.id}")


def run_method_f1(client, out_dir: str, force: bool) -> None:
    prompts_dir = out_path(out_dir, "prompts")
    article_path = out_path(out_dir, "F1_article.md")
    meta_path = out_path(out_dir, "api_meta_F1.json")

    save_text(out_path(prompts_dir, "F1_instruction.txt"), F1_INSTRUCTION)

    if os.path.exists(article_path) and not force:
        print(f"[SKIP] 既存出力あり(--forceなし): {article_path}")
        return

    draft_path = os.path.join(ITER_TRIAL_OUT_DIR, "original.md")
    chain_path = os.path.join(ITER_TRIAL_OUT_DIR, "chain.json")
    draft_text = load_text(draft_path)
    chain = json.loads(load_text(chain_path))
    original_response_id = None
    for stage in chain.get("stages", []):
        if stage.get("stage") == "original":
            original_response_id = stage.get("response_id")
            break

    used_method = None
    response = None
    if original_response_id:
        try:
            response = itertrial.call_with_previous_response_id(
                client, F1_INSTRUCTION, WRITER_EFFORT, original_response_id, "F1",
            )
            used_method = "previous_response_id"
        except Exception as e:  # noqa: BLE001 - 技術的失敗時のみフォールバック
            print(f"[WARN] previous_response_id失敗、フォールバックへ切替(F1): {e}")
            response = None

    if response is None:
        fallback_user = f"以下の記事:\n\n{draft_text}\n\n{F1_INSTRUCTION}"
        save_text(out_path(prompts_dir, "F1_fallback_full_user.txt"), fallback_user)
        response = call_fresh(client, DEVELOPER_MESSAGE, fallback_user, WRITER_EFFORT, "F1")
        used_method = "fallback_full_text"

    article = response.output_text.strip()
    meta = er015base.response_meta(
        response, F1_INSTRUCTION, DEVELOPER_MESSAGE,
        extra={
            "stage": "F1",
            "effort_requested": WRITER_EFFORT,
            "chain_method": used_method,
            "previous_response_id_used": original_response_id if used_method == "previous_response_id" else None,
        },
    )
    save_text(article_path, article)
    save_json(meta_path, meta)
    print(f"[OK] F1(F1_article): {len(article)}字 model={meta['response_model_actual']} chain_method={used_method}")


METHOD_RUNNERS = {
    "A": run_method_a,
    "B": run_method_b,
    "F1": run_method_f1,
}


def cmd_run(args):
    out_dir = args.out_dir
    install_logger(out_dir)
    client = vfl01.get_client()
    runner = METHOD_RUNNERS[args.method]
    runner(client, out_dir, args.force)


# ------------------------------------------------------------
# observe (機械集計。最終評価はFableが行う)
# ------------------------------------------------------------
STAGE_FILES = {
    "A": "A_article.md",
    "B": "B_article.md",
    "F1": "F1_article.md",
}

KEYWORDS = list(repro01.KEYWORDS)
NUMBER_RE = re.compile(r"\d+(?:[,\.]\d+)?")


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
    texts = {}
    for key, fname in STAGE_FILES.items():
        p = out_path(out_dir, fname)
        if os.path.exists(p):
            texts[key] = load_text(p)

    original_path = os.path.join(ITER_TRIAL_OUT_DIR, "original.md")
    orig_numbers = set()
    orig_keywords = set()
    if os.path.exists(original_path):
        orig_text = load_text(original_path)
        orig_numbers = set(NUMBER_RE.findall(orig_text))
        orig_keywords = {kw for kw in KEYWORDS if orig_text.count(kw) > 0}

    result = {}
    for key, text in texts.items():
        numbers = NUMBER_RE.findall(text)
        kw_hits = sum(text.count(kw) for kw in KEYWORDS)
        new_numbers = sorted(set(numbers) - orig_numbers)
        new_keywords = sorted({kw for kw in KEYWORDS if text.count(kw) > 0} - orig_keywords)
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
            "numbers_not_in_original": new_numbers,
            "keywords_not_in_original": new_keywords,
        }
    save_json(out_path(out_dir, "observation_machine.json"), result)
    for key, r in result.items():
        print(
            f"[OK] {key}: {r['char_count']}字 paragraphs={r['paragraph_count']} "
            f"questions={r['question_count']} numbers={r['number_token_count']} "
            f"new_numbers={r['numbers_not_in_original']} new_keywords={r['keywords_not_in_original']}"
        )


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
    # F1はitertrial.call_with_previous_response_id経由でlogging_contextが
    # itertrial自身のTHEME_TAGを使うため、本OUT_DIR内のログでも
    # theme=itertrial.THEME_TAG・stage="F1"として記録される。同一出力先
    # ファイル内のためentriesはこのTrialのみを含み、他Trialの混入はない。
    entries = [
        e for e in entries
        if e.get("theme") == THEME_TAG
        or (e.get("theme") == itertrial.THEME_TAG and e.get("stage") == "F1")
    ]

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
    p_run.add_argument("--method", required=True, choices=["A", "B", "F1"])
    p_run.add_argument("--force", action="store_true")
    p_run.set_defaults(func=cmd_run)

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
