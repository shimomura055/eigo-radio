# ============================================================
# er011_news_ledger_canonical_spelling_trial_15_run.py
# FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15
# ============================================================
# 目的(委任文どおり): 「日本語情報源由来のLedgerに日本語表記しかない
# 固有名詞を、Writerが実行ごとに推測でローマ字化し、Fact Checkerに
# 到達しなければ検出されない」というfailure modeに対し、Trial-14条件E
# Ledger(A+FACT-11/14、usable 7件)を基準(対照群、既存結果を再利用し
# 再生成しない)とし、その全固有名詞にWeb検索で確認した公式英語表記
# (canonical_en_spelling)を追記した改訂Ledger(条件F)を作成、N=6
# (A2×3+B1B×3)で条件Eと比較する。
#
# **Trial(Production実装ではない)**。Production/Prompt/QA/Validator/
# retryコード・Production Ledger・SSOTは無変更。monkeypatch・グローバル
# 書き換えなし。ユーザー承認2026-09-12「(a) Ledgerに公式英語表記を追加
# するTrialを実施」に基づく。
#
# 費用上限: このスクリプト単独で¥200(Web検索での表記確認+記事6本+
# Fact Checker、TTSは実行しない)。combo単位で逐次実行し、実行前に都度
# compute_cost_so_far_jpy()で確認する。
#
# 書き込み範囲: er011_output/news_ledger_canonical_spelling_trial_15/
# のみ(新規ディレクトリ)。既存Trial-12/12b/14の成果物
# (er011_output/news_ledger_enrichment_ab_trial_12/配下)は読み取り専用
# で一切変更しない(Trial-14のbuild_ledger_e_stage()を再実行すると
# 既存twofact_e/ディレクトリへの再書き込みが発生してしまうため、本
# スクリプトでは同関数を呼ばず、条件Eの既存出力ファイルを直接読み込む
# 形で「再利用」する。差異の理由はREPORTに明記する)。
#
# 再利用方針: Production関数(er003_v1_n3_01_articles_generate.
# build_common_block/build_prompt、er002_ja_web_research_r3.
# build_fact_check_prompt/make_fact_checker_fn/run_fact_checker_with_
# gates/make_writer_research_fn、er011_point_role_planning_focus_
# connection_trial_03.run_one_pattern_connected)はすべて無改変で直接
# 呼び出す。Trial-14 harness(er011_news_ledger_enrichment_
# disambiguation_trial_14_run.py)のcompute_cost_so_far_jpyと同一ロジック
# (t12._call_cost_usd/USD_JPY)を再利用し、本スクリプト自身のログ
# ファイルに対して適用する(t14.run_one_factcheck/combo_e_stageは
# ディレクトリ構造がCONDITION_ARTICLE_DIR/BASE_DIRに固定されており、
# 本Trialの新規出力ディレクトリにそのまま適用できないため、同一の
# Production呼び出し列を保ったまま出力先だけを一般化した関数を新規に
# 書いた。呼び出しているProduction関数自体は完全に同一)。
# ============================================================
from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict

import er002_ja_web_research_r3 as r3
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er011_daily_news_focus_layer_comparison_trial_04 as t4
import er011_news_ledger_enrichment_ab_trial_12_run as t12
import er011_news_ledger_enrichment_disambiguation_trial_14_run as t14
import er011_news_ledger_enrichment_leaveout_trial_12b_run as t12b
import er011_point_role_planning_focus_connection_trial_03 as t3

THEME_ID = "news_ledger_canonical_spelling_trial_15"
OUT_BASE = "er011_output/news_ledger_canonical_spelling_trial_15"
LOG_PATH = f"{OUT_BASE}/raw_usage_log.jsonl"
BUDGET_JPY = 200.0

TOPIC = t3.HANSHIN_TOPIC_JA

# 条件E(対照群)は既存Trial-14出力を読み取り専用で参照するのみ
# (再生成しない)。
CONDITION_E_LEDGER_PATH = t14.LEDGER_E_PATH
CONDITION_E_COMBO_RESULTS_DIR = f"{t14.TWOFACT_E_DIR}/_combo_results"
USABLE_FACT_COUNT_F = t14.USABLE_FACT_COUNT_E  # 7件、条件Fは表記注記のみ追加(新規factなし)

LEDGER_F_PATH = f"{OUT_BASE}/hanshin_ledger_condition_f_canonical_spelling.txt"
CONDITION_F_DIR = f"{OUT_BASE}/condition_f"
CENSORED_F_DIR = f"{OUT_BASE}/factcheck_censored_f"

USD_JPY = t12.USD_JPY
_call_cost_usd = t12._call_cost_usd

LEVELS = t4.LEVELS
LABEL_LOOKUP_F = {label: (label, instruction, level_dir, stage_tag)
                  for (label, instruction, level_dir, stage_tag) in LEVELS}

# ============================================================
# 段階0: 対照群(条件E)の既存結果読み込み(読み取り専用、再生成なし)
# ============================================================
def load_condition_e_baseline() -> list:
    results = []
    for fname in sorted(os.listdir(CONDITION_E_COMBO_RESULTS_DIR)):
        with open(f"{CONDITION_E_COMBO_RESULTS_DIR}/{fname}", encoding="utf-8") as f:
            results.append(json.load(f))
    return results


# ============================================================
# 段階1: 固有名詞の公式英語表記confirmation(Web検索、1回のAPI呼び出しで
# 全件をまとめて確認する。委任文の「1件1回」を、1回のAPI実行内でモデルが
# 各固有名詞ごとに個別クエリを発行する形で満たす=モデル自身の検索回数は
# extract_web_search_usageで実測記録する)。
# ============================================================
PROPER_NOUNS = [
    {"ja": "佐藤輝明", "context": "阪神タイガース内野手(2026年8月16日の広島戦で本塁打を打った選手)"},
    {"ja": "伊原陵人", "context": "阪神タイガース投手(同試合の先発投手)"},
    {"ja": "森翔平", "context": "広島東洋カープ投手(同試合の敗戦投手)"},
    {"ja": "坂本誠志郎", "context": "阪神タイガース捕手"},
    {"ja": "伏見寅威", "context": "阪神タイガース捕手(同試合で代打起用)"},
    {"ja": "森下翔太", "context": "阪神タイガース外野手"},
    {"ja": "E・モンテロ(エレウリス・モンテロ)", "context": "広島東洋カープ内野手(同試合でソロ本塁打)"},
    {"ja": "阪神タイガース", "context": "NPBセ・リーグ球団"},
    {"ja": "広島東洋カープ", "context": "NPBセ・リーグ球団"},
    {"ja": "マツダスタジアム", "context": "広島東洋カープ本拠地球場"},
]

RESEARCH_INSTRUCTION_TEMPLATE = """あなたはプロ野球の英語表記調査担当です。以下の日本語の固有名詞
それぞれについて、NPB公式サイト・球団公式サイト(英語版があれば優先)・
MLB公式(該当する場合)などの一次情報源をWeb検索で確認し、英語圏の
報道・公式表記で実際に使われている公式な英語表記(ローマ字表記)を
1件ずつ特定してください。

対象一覧:
{entity_list}

出力形式(厳守、他の説明文は書かない): 対象1件につき1行、以下の形式
のみで出力してください。

CANONICAL: <日本語表記> = <English Spelling> | SOURCE: <確認したURL>

複数の情報源で表記が割れている場合は、最も公式性の高い情報源
(球団公式・NPB公式)を優先し、その理由をSOURCE列の後に括弧書きで
簡潔に添えてください。
"""


def build_research_instruction() -> str:
    entity_list = "\n".join(f"- {p['ja']}({p['context']})" for p in PROPER_NOUNS)
    return RESEARCH_INSTRUCTION_TEMPLATE.format(entity_list=entity_list)


CANONICAL_LINE_RE = re.compile(
    r"CANONICAL:\s*(?P<ja>.+?)\s*=\s*(?P<en>.+?)\s*\|\s*SOURCE:\s*(?P<rest>.+)$")


def parse_canonical_lines(text: str) -> list:
    parsed = []
    for line in text.splitlines():
        line = line.strip()
        m = CANONICAL_LINE_RE.match(line)
        if not m:
            continue
        rest = m.group("rest").strip()
        url_match = re.match(r"(\S+)", rest)
        url = url_match.group(1) if url_match else rest
        note = rest[len(url):].strip() if url_match else ""
        parsed.append({"ja": m.group("ja").strip(), "en": m.group("en").strip(),
                        "url": url, "note": note})
    return parsed


def run_canonical_spelling_research(client) -> dict:
    os.makedirs(OUT_BASE, exist_ok=True)
    cl.install(LOG_PATH)
    user_message = build_research_instruction()
    # Production共通関数(make_writer_research_fn)を無改変で再利用。
    # reasoning_effortのみ、この単純な表記確認タスク向けに"medium"へ
    # 引数で明示指定する(関数のデフォルトはWRITER_REASONING_EFFORT=
    # "high"のまま、関数定義自体は無変更)。
    research_fn = r3.make_writer_research_fn(user_message, client=client, reasoning_effort="medium")
    theme_tag = f"{THEME_ID}_canonical_spelling_research"
    t0 = time.time()
    with cl.logging_context(theme_tag, "canonical_spelling_research"):
        text, model, response_id, search_usage, sources = research_fn()
    elapsed = round(time.time() - t0, 2)
    parsed = parse_canonical_lines(text)
    record = {
        "raw_text": text, "model": model, "response_id": response_id,
        "search_usage": search_usage, "sources": sources, "parsed": parsed,
        "elapsed_seconds": elapsed,
    }
    with open(f"{OUT_BASE}/canonical_spelling_research_raw.json", "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] research完了: {len(parsed)}/{len(PROPER_NOUNS)}件パース成功、"
          f"web_search_call_count={search_usage['web_search_call_count']} elapsed={elapsed}s")
    return record


# ============================================================
# 段階2: 条件F Ledger構築(条件Eの既存ファイルを読み取り専用で参照し、
# canonical_en_spelling注記+Trial harness側のWriter向け1文を追記する。
# Production関数build_common_block/build_promptは無改変。追記した文言は
# Ledgerテキスト[データ]の一部としてverified_ledger_text引数へそのまま
# 渡るだけであり、共通ブロックのテンプレート構造自体は変更していない)。
# ============================================================
HARNESS_INSTRUCTION_SENTENCE = (
    "\n\n=== 固有名詞の英語表記について(Trial-15、Ledger内での伝達) ===\n"
    "このLedgerに`canonical_en_spelling: <日本語表記> = <English>`という形式で\n"
    "記載がある固有名詞は、必ずこの英語表記をそのまま使用すること。自己判断で\n"
    "別のローマ字表記を作らないこと。\n"
)


def build_condition_f_ledger(canonical_entries: list) -> dict:
    os.makedirs(OUT_BASE, exist_ok=True)
    with open(CONDITION_E_LEDGER_PATH, encoding="utf-8") as f:
        condition_e_text = f.read()
    lines = ["\n\n=== 固有名詞の公式英語表記(Trial-15、Web確認済み) ===",
             "管理ID: FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15",
             "作成方法: 条件E Ledger(無変更、上記本文)本文から機械抽出+目視で網羅した"
             "固有名詞に対し、Web検索(WRITER_MODELのweb_searchツール、1回のAPI実行)で"
             "公式英語表記を確認し追記した。以下は日本語表記=公式英語表記の対応のみを"
             "機械的に転記したもの(出典URLはcanonical_spelling_research_raw.json参照)。",
             ""]
    for entry in canonical_entries:
        lines.append(f"canonical_en_spelling: {entry['ja']} = {entry['en']}")
    lines.append("")
    full_text = condition_e_text + "\n".join(lines) + HARNESS_INSTRUCTION_SENTENCE
    with open(LEDGER_F_PATH, "w", encoding="utf-8") as f:
        f.write(full_text)
    assert full_text.startswith(condition_e_text)
    print(f"[{THEME_ID}] build_condition_f_ledger完了: {len(full_text)}文字"
          f"(条件Eからの追加{len(full_text) - len(condition_e_text)}文字)")
    return {"condition_f_chars": len(full_text), "canonical_entries": len(canonical_entries)}


# ============================================================
# 段階3: 条件F記事生成(N=6、A2×3+B1B×3)。既存Trial-14
# run_one_combo_eと同一のProduction呼び出し列(build_common_block/
# build_prompt/run_one_pattern_connected、無改変)を、出力先だけ本Trial
# 専用ディレクトリへ変えて再利用する。
# ============================================================
def run_one_combo_f(client, master_full_text: str, run_idx: int, label: str, instruction: str,
                     level_dir: str, stage_tag: str) -> dict:
    ledger_text = t12b.load_text(LEDGER_F_PATH)
    out_dir = f"{CONDITION_F_DIR}/{level_dir}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, TOPIC, ledger_text, editorial_type_module_block="")
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_condition_f_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = t3.run_one_pattern_connected(
            client, theme_tag, label, prompt, ledger_text, TOPIC, out_dir,
            point_role_hint_block="")
    elapsed = round(time.time() - t0, 2)
    analysis = t4.analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = "condition_f"
    analysis["level"] = label
    analysis["run"] = run_idx
    analysis.update(t12b.load_initial_flag(out_dir))
    analysis.update(t12b.load_initial_attempt0_qa(out_dir))
    analysis["evidence_allocation"] = t12b.evidence_allocation_metrics(
        out_dir, analysis["retry_attempts"], USABLE_FACT_COUNT_F)
    if analysis["point_one_overlap_ratio"] is not None and analysis["point_two_overlap_ratio"] is not None:
        analysis["gate_indicator_max_overlap"] = max(
            analysis["point_one_overlap_ratio"], analysis["point_two_overlap_ratio"])
    else:
        analysis["gate_indicator_max_overlap"] = None
    analysis["final_ng"] = result.get("status") != "OK"
    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] condition_f run{run_idx} {label}: status={result.get('status')} "
          f"retry={analysis['retry_attempts']} initial_value_qa={analysis['initial_value_qa_label']} "
          f"fact_verdict={analysis.get('fact_verdict')} elapsed={elapsed}s")
    return analysis


def compute_cost_so_far_jpy() -> float:
    if not os.path.exists(LOG_PATH):
        return 0.0
    total_usd = 0.0
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_usd += _call_cost_usd(json.loads(line))
    return total_usd * USD_JPY


def combo_f_stage(label: str, run_idx: int) -> dict:
    os.makedirs(CONDITION_F_DIR, exist_ok=True)
    cl.install(LOG_PATH)
    cost_so_far = compute_cost_so_far_jpy()
    if cost_so_far > BUDGET_JPY:
        raise RuntimeError(f"費用上限超過見込み(実測¥{cost_so_far:.1f} > 上限¥{BUDGET_JPY})。STOPします。")
    client = t3.vfl01.get_client()
    master_full_text = t3.ab01.load_master_full_text()
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP_F[label]
    analysis = run_one_combo_f(client, master_full_text, run_idx, label, instruction, level_dir, stage_tag)
    combo_results_dir = f"{OUT_BASE}/_combo_results_f"
    os.makedirs(combo_results_dir, exist_ok=True)
    with open(f"{combo_results_dir}/{level_dir}_run{run_idx}.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    return analysis


def aggregate_f_stage() -> list:
    all_results = []
    combo_results_dir = f"{OUT_BASE}/_combo_results_f"
    if os.path.isdir(combo_results_dir):
        for fname in sorted(os.listdir(combo_results_dir)):
            with open(f"{combo_results_dir}/{fname}", encoding="utf-8") as f:
                all_results.append(json.load(f))
    with open(f"{OUT_BASE}/all_results_f.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] aggregate_f_stage: {len(all_results)}本を集約しました。")
    return all_results


# ============================================================
# 段階4: 打ち切りバイアス対策(委任文どおり)。Point Overlap GateでNGの
# ままFact Checkerへ未到達だった記事(final_ng=True かつ
# fact_verdict=None)に、Trial-14 run_one_factcheck()と同一の
# Production呼び出し列(r3.build_fact_check_prompt/make_fact_checker_fn/
# run_fact_checker_with_gates、無改変・パラメータ同一)を単独適用する。
# t14.run_one_factcheckはCONDITION_ARTICLE_DIR/BASE_DIRが固定されており
# 本Trialの出力ディレクトリに使えないため、出力先だけを一般化した関数と
# して新規に書いた(呼び出しているProduction関数・パラメータは同一)。
# ============================================================
def identify_censored_targets_f(all_results_f: list) -> list:
    return [r for r in all_results_f if r.get("final_ng") is True and r.get("fact_verdict") is None]


def run_standalone_factcheck(level_dir: str, run_idx: int) -> dict:
    article_path = f"{CONDITION_F_DIR}/{level_dir}/run{run_idx}/article.md"
    with open(article_path, encoding="utf-8") as f:
        article_text = f.read()
    out_dir = f"{CENSORED_F_DIR}/condition_f_{level_dir}_run{run_idx}"
    os.makedirs(out_dir, exist_ok=True)

    fc_prompt = r3.build_fact_check_prompt(TOPIC, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    theme_tag = f"{THEME_ID}_censored_condition_f_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, "fact_check_censored"):
        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
            r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    elapsed = round(time.time() - t0, 2)
    verdict = fc_result.get("verdict") if fc_result else None

    fact_qa_record = {
        "condition": "condition_f", "level_dir": level_dir, "run": run_idx,
        "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "verdict": verdict, "result": fc_result,
        "elapsed_seconds": elapsed,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] censored condition_f {level_dir} run{run_idx}: status={fc_status} "
          f"verdict={verdict} elapsed={elapsed}s")
    return fact_qa_record


def censored_stage_f(level_dir: str, run_idx: int) -> dict:
    os.makedirs(CENSORED_F_DIR, exist_ok=True)
    cl.install(LOG_PATH)
    cost_so_far = compute_cost_so_far_jpy()
    if cost_so_far > BUDGET_JPY:
        raise RuntimeError(f"費用上限超過見込み(実測¥{cost_so_far:.1f} > 上限¥{BUDGET_JPY})。STOPします。")
    return run_standalone_factcheck(level_dir, run_idx)


def write_cost_summary() -> dict:
    records = []
    if os.path.exists(LOG_PATH):
        records = [json.loads(l) for l in open(LOG_PATH, encoding="utf-8")]
    for r in records:
        r["_cost_usd"] = _call_cost_usd(r)
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-12/12b/14と同一参照元・"
                       "同一ロジック)。",
        "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
        "total_calls": len(records),
    }
    with open(f"{OUT_BASE}/cost_summary_15.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "help"
    if which == "research":
        client = t3.vfl01.get_client()
        run_canonical_spelling_research(client)
    elif which == "build_ledger_f":
        with open(f"{OUT_BASE}/canonical_spelling_research_raw.json", encoding="utf-8") as f:
            record = json.load(f)
        build_condition_f_ledger(record["parsed"])
    elif which == "combo_f":
        combo_f_stage(sys.argv[2], int(sys.argv[3]))
    elif which == "aggregate_f":
        aggregate_f_stage()
    elif which == "censored_f":
        censored_stage_f(sys.argv[2], int(sys.argv[3]))
    elif which == "cost":
        r = write_cost_summary()
        print(f"[{THEME_ID}] 費用実測合計: ¥{r['total_jpy']}")
    elif which == "list_targets_f":
        with open(f"{OUT_BASE}/all_results_f.json", encoding="utf-8") as f:
            all_results_f = json.load(f)
        for t in identify_censored_targets_f(all_results_f):
            print(t["level"], t["run"])
    else:
        print("usage: python er011_news_ledger_canonical_spelling_trial_15_run.py "
              "[research|build_ledger_f|combo_f <A2|B1B> <run>|aggregate_f|"
              "list_targets_f|censored_f <a2|b1b> <run>|cost]")
