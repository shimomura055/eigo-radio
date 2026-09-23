# ============================================================
# er015_news_original_baseline_repro_01.py
# NEWS-ORIGINAL-BASELINE-REPRO-01 (Fable設計、2026-09-24)
# ============================================================
# 目的: docs/pm/news_entertainment_prompt_trials_falbe_handoff.md §7の
# ベースラインPrompt(ChatGPT UIで生成されたオリジナル記事、§8)を、
# API経由のgpt-5.6-luna(Production Writerモデル)で同一条件・逐語
# Promptを用いて再現できるか確認するTrial専用スクリプト。
# **Production実装ではない。改善は一切行わない。**
#
# Production正式path(er011_*/er014_*等)は一切変更しない。本ファイルは
# er015_news_core_idea_editorial_trial_01(er015base)からcall_luna相当の
# 呼び出し構造(response_meta/save_text/save_json/load_text/out_path)を
# 再利用するが、theme tag・出力先は本Trial専用に分離する。er015base自体は
# import利用のみで無変更。
#
# 重要な設計判断(委任文の禁止事項に基づく):
#   - Writer入力には、引き継ぎ資料§7に逐語で存在するPromptのみを使う。
#     [ニュース]セクション(素材本文)は資料の§7に存在しないため付与しない
#     (T0はSource Note Sを{news}へ埋め込んでいたが、資料には無いため今回
#     は使わない)。
#   - developer(system)メッセージは、資料にChatGPT側の設定記録が無いため
#     「なし」との比較を避け、er015 T0と同一の最小メッセージ
#     ("あなたは日本語のニュースを分かりやすく面白く伝える書き手です。")
#     を使う。この選択はRESULT_PACKET/REPORTに明記する。
#   - model=gpt-5.6-luna固定、reasoning effort="high"(T0と同一=Production
#     Writer既定)。tools・web_searchは使わない。
#
# サブコマンド: run --n 5 --out-dir <OUT> [--force]
#              compare --out-dir <OUT>
# 冪等性: run1..runN/article.md が既に存在する場合、--forceなしでは
# 再実行しない(恣意的な良い出力の選別を防ぐガード)。
# ============================================================
from __future__ import annotations

import argparse
import json
import os

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base

THEME_TAG = "NEWS_ORIGINAL_BASELINE_REPRO_01"
WRITER_MODEL = vfl01.MODEL  # "gpt-5.6-luna" (= routing.WRITER_MODEL)
WRITER_EFFORT = vfl01.REASONING_EFFORT  # "high" (T0と同一値)

# 引き継ぎ資料 §7 (146-162行) の逐語コピー。[ニュース]セクションは付与しない
# (資料に素材本文が記録されていないため)。
R0_PROMPT = """以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。

ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。

語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。

遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。

事実関係は厳守し、架空の出来事や発言は加えません。

テーマ：老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討

長さ：800～1000字

出力はタイトルと本文のみ。"""

DEVELOPER_MESSAGE = "あなたは日本語のニュースを分かりやすく面白く伝える書き手です。"


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


def call_luna(client, developer: str, user: str, effort: str, stage: str):
    """er015base.call_lunaと同一構造(schema=None, web_search=False)。
    THEME_TAGのみ本Trial専用に分離する。"""
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


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def cmd_run(args):
    out_dir = args.out_dir
    n = args.n
    install_logger(out_dir)
    client = vfl01.get_client()
    save_text(out_path(out_dir, "prompt.txt"), R0_PROMPT)

    for i in range(1, n + 1):
        run_dir = out_path(out_dir, f"run{i}")
        article_path = out_path(run_dir, "article.md")
        if os.path.exists(article_path) and not args.force:
            print(f"[SKIP] 既存出力あり(--forceなし): {article_path}")
            continue
        response = call_luna(
            client, DEVELOPER_MESSAGE, R0_PROMPT,
            effort=WRITER_EFFORT, stage=f"run{i}",
        )
        article = response.output_text.strip()
        meta = er015base.response_meta(
            response, R0_PROMPT, DEVELOPER_MESSAGE,
            extra={"run": i, "effort_requested": WRITER_EFFORT},
        )
        save_text(article_path, article)
        save_json(out_path(out_dir, f"run{i}_api_meta.json"), meta)
        save_text(out_path(out_dir, f"run{i}.md"), article)
        print(f"[OK] run{i}: {len(article)}字 model={meta['response_model_actual']}")


KEYWORDS = [
    "南伊豆町", "入間地区", "66件", "32市町村", "54区域", "70市町村",
    "154区域", "平成30年度", "令和5年度", "令和7年度", "浄化槽",
    "下水道", "撤去費", "補助金", "合併処理浄化槽",
]


def _keyword_counts(text: str) -> dict:
    return {kw: text.count(kw) for kw in KEYWORDS if text.count(kw) > 0}


def cmd_compare(args):
    out_dir = args.out_dir
    rows = []
    for i in range(1, 6):
        run_path = out_path(out_dir, f"run{i}.md")
        if not os.path.exists(run_path):
            continue
        text = load_text(run_path)
        rows.append({
            "id": f"run{i}",
            "char_count": len(text),
            "keyword_counts": _keyword_counts(text),
        })
    result = {"runs": rows}
    save_json(out_path(out_dir, "compare_machine_metrics.json"), result)
    for r in rows:
        print(f"[OK] {r['id']}: {r['char_count']}字 keywords={r['keyword_counts']}")


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
        total_usd += usd
        total_input += it
        total_output += ot
        total_cached += ct

    result = {
        "theme": THEME_TAG,
        "total_calls": len(entries),
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
    p_run.add_argument("--n", type=int, default=5)
    p_run.add_argument("--out-dir", required=True)
    p_run.add_argument("--force", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_cmp = sub.add_parser("compare")
    p_cmp.add_argument("--out-dir", required=True)
    p_cmp.set_defaults(func=cmd_compare)

    p_cost = sub.add_parser("cost")
    p_cost.add_argument("--out-dir", required=True)
    p_cost.set_defaults(func=cmd_cost)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
