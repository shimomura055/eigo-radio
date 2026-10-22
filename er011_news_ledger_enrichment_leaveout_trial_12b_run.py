# ============================================================
# er011_news_ledger_enrichment_leaveout_trial_12b_run.py
# FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-LEAVEOUT-TRIAL-12B (Lane A, Sonnet委任)
# ============================================================
# 目的(Fable確認済み、委任文どおり): Trial-12(条件A=現行Ledger5件 vs
# 条件B=拡充Ledger12件)に対するOpus L2レビュー
# (FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-REVIEW-01)の
# 所見を検証するための追試。Opus優先1〜3を実施:
#   優先1: 効果が「fact数」ではなく特定fact(FACT-12=伊原の2打数2安打、
#     次いでFACT-09/13/14)の有無に帰属できるか、抜き取り対照で確認する。
#   優先2: 周辺fact2件(FACT-12/13)だけで条件Bに近い効果が出るか確認する。
#   優先3: 唯一の交絡なし・非トートロジーな有意差だった「初回attemptの
#     Point Value QA判定(PASS/NG)」を主要エンドポイントとして追跡する。
#
# 条件C(leaveout_c、抜き取り対照): 条件A全文(FACT-01〜07、無変更) +
#   条件Bの追加分からFACT-12とFACT-13を除いたFACT-08/09/10/11/14の5件
#   =usable 10件。
# 条件D(twofact_d、2件のみ追加): 条件A全文 + FACT-12/FACT-13の2件のみ
#   =usable 7件。
# 両条件のFACT-08〜14ブロックは、Trial-12で既に生成済みの
# `hanshin_ledger_condition_b_enriched.txt`(既存ファイル、無変更・
# 再利用のみ)から正規表現でブロック単位に抽出し、選択したブロックの
# 文言は一切変更せずそのまま連結する(機械的抜粋、新規WebSearchなし
# =このTrial-12bでは追加research費用は発生しない)。
#
# 両条件とも editorial_type_module_block="" / point_role_hint_block=""
# (Production既定のbaseline)に固定。Trial-12と同一harness・同一
# Production関数(無改変)を再利用する。
#
# **Trial(Production実装ではない)**。Production/Prompt/QA/Validator/retry
# コード・SSOT編集・Git操作は一切行わない。monkeypatch・グローバル書き換え
# なし。TTSは実行しない(text-onlyまで)。
#
# 書き込み範囲(委任文どおり): er011_output/news_ledger_enrichment_ab_
# trial_12/ 配下の新規サブディレクトリ leaveout_c/ / twofact_d/ /
# reaggregation/ のみ。既存Trial-12の成果物(a2/, b1b/, _combo_results/,
# hanshin_ledger_condition_b_enriched.txt, run_metadata.json,
# cost_summary.json, final_analysis_summary.json, all_results_so_far.json,
# raw_usage_log.jsonl, research_raw_result.json)は読み取り専用で一切
# 変更しない。
#
# 費用上限: ¥200(見込み¥90〜120、新規research不要のため主に記事生成
# 12本分。Trial-12の記事生成12本実測合計¥99.8を参考値とする)。
# 二重起動防止(前面同期のみ、バックグラウンド待機なし)。
# ============================================================
from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict

import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er011_daily_news_focus_layer_comparison_trial_04 as t4
import er011_point_role_planning_focus_connection_trial_03 as t3
import er011_news_ledger_enrichment_ab_trial_12_run as t12  # 既存Trial-12(import・無変更、再利用のみ)

THEME_ID = "news_ledger_enrichment_leaveout_trial_12b"
BASE_DIR = t12.OUT_DIR  # "er011_output/news_ledger_enrichment_ab_trial_12" (既存ディレクトリ、その下の新規サブディレクトリのみ書き込む)

N_PER_CONDITION = 3  # A2×3 + B1B×3 = 6 run/条件(Trial-12と同一定義)
BUDGET_JPY = 200.0

CONDITION_B_LEDGER_PATH = t12.CONDITION_B_LEDGER_PATH  # 既存ファイル、読み取り専用
CONDITION_A_LEDGER_PATH = t12.CONDITION_A_LEDGER_PATH  # 既存ファイル(現行Ledger)、読み取り専用

LEAVEOUT_C_DIR = f"{BASE_DIR}/leaveout_c"
TWOFACT_D_DIR = f"{BASE_DIR}/twofact_d"
REAGG_DIR = f"{BASE_DIR}/reaggregation"

LEDGER_C_PATH = f"{LEAVEOUT_C_DIR}/hanshin_ledger_condition_c_leaveout.txt"
LEDGER_D_PATH = f"{TWOFACT_D_DIR}/hanshin_ledger_condition_d_twofact.txt"

# 条件Cで採用するfact ID(FACT-12/13を除いた5件)、条件Dで採用するfact ID
# (FACT-12/13の2件のみ)。Fable委任文の指定どおり。
CONDITION_C_FACT_IDS = ["08", "09", "10", "11", "14"]
CONDITION_D_FACT_IDS = ["12", "13"]

USABLE_FACT_COUNT_C = 5 + len(CONDITION_C_FACT_IDS)  # 10
USABLE_FACT_COUNT_D = 5 + len(CONDITION_D_FACT_IDS)  # 7

CONDITIONS = {
    "leaveout_c": {
        "ledger_path": LEDGER_C_PATH,
        "usable_fact_count": USABLE_FACT_COUNT_C,
        "out_subdir": LEAVEOUT_C_DIR,
        "label_ja": "条件C: 抜き取り対照(条件A5件+FACT-08/09/10/11/14の5件=10件、"
                     "FACT-12/13を除外)",
        "included_fact_ids": CONDITION_C_FACT_IDS,
    },
    "twofact_d": {
        "ledger_path": LEDGER_D_PATH,
        "usable_fact_count": USABLE_FACT_COUNT_D,
        "out_subdir": TWOFACT_D_DIR,
        "label_ja": "条件D: 2件のみ追加(条件A5件+FACT-12/13の2件=7件)",
        "included_fact_ids": CONDITION_D_FACT_IDS,
    },
}

LEVELS = t4.LEVELS  # [("B1B", instruction, "b1b", "writer_b1"), ("A2", ..., "a2", "writer_a2")] (無改変で再利用)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Stage 0: Ledger C/D構築(新規research・API呼び出しなし、既存
# hanshin_ledger_condition_b_enriched.txtからの正規表現抽出のみ、
# ¥0)。抽出したFACTブロックの文言は一切変更しない(機械的抜粋)。
# ============================================================
FACT_BLOCK_RE = re.compile(r"\n\[CONFIRMED_FACT\] FACT-(\d{2}):")


def _extract_fact_blocks(condition_b_text: str) -> dict:
    """条件Bのテキストから、FACT-08以降の各ブロック本文(次のFACTブロック
    または次のセクション見出しの直前まで)をfact_id -> テキスト の辞書で
    返す。ブロックの文言はそのまま(strip()のみ、内容の書き換えなし)。"""
    matches = list(FACT_BLOCK_RE.finditer(condition_b_text))
    blocks = {}
    for i, m in enumerate(matches):
        fact_id = m.group(1)
        start = m.start() + 1  # 先頭の"\n"を除く
        end = matches[i + 1].start() if i + 1 < len(matches) else \
            condition_b_text.find("追加Fact参照情報源一覧")
            # 追加Fact参照情報源一覧セクションの手前まで(見出し"=== "の直前
            # の改行込みで検索しているため、多少の空白差はstrip()で吸収する)
        block_text = condition_b_text[start:end]
        # セクション見出し文字列が万一混入していたら手前で打ち切る(安全側)
        cut = block_text.find("\n===")
        if cut != -1:
            block_text = block_text[:cut]
        blocks[fact_id] = block_text.strip()
    return blocks


def build_ledgers_stage() -> dict:
    os.makedirs(LEAVEOUT_C_DIR, exist_ok=True)
    os.makedirs(TWOFACT_D_DIR, exist_ok=True)
    condition_a_text = load_text(CONDITION_A_LEDGER_PATH).rstrip("\n")
    condition_b_text = load_text(CONDITION_B_LEDGER_PATH)
    fact_blocks = _extract_fact_blocks(condition_b_text)
    # 抽出できたブロック数の健全性チェック(FACT-08〜14の7件が揃っているか)
    expected_ids = {"08", "09", "10", "11", "12", "13", "14"}
    missing = expected_ids - set(fact_blocks.keys())
    if missing:
        raise RuntimeError(f"条件Bから抽出できなかったFACTブロックがあります: {missing}")
    for fact_id in expected_ids:
        if not fact_blocks[fact_id].startswith(f"[CONFIRMED_FACT] FACT-{fact_id}:"):
            raise RuntimeError(f"FACT-{fact_id}ブロックの抽出結果が不正です(先頭不一致): "
                                f"{fact_blocks[fact_id][:60]!r}")

    def build_condition_ledger(cond_key: str, out_path: str) -> str:
        cond = CONDITIONS[cond_key]
        included = cond["included_fact_ids"]
        header_note = (
            f"\n\n=== 追加Fact(Trial-12B {cond['label_ja']}、機械的抜粋) ===\n"
            f"管理ID: FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-LEAVEOUT-TRIAL-12B\n"
            f"作成方法: 新規Web調査は行っていない(追加research費用¥0)。\n"
            f"既存のTrial-12条件B用Ledger(hanshin_ledger_condition_b_enriched.txt、\n"
            f"2026-09-09作成、無変更のまま参照元として使用)から、FACT-"
            f"{'/'.join(included)}のブロックのみを正規表現で機械的に抽出し、\n"
            f"文言を一切変更せずそのまま連結したものである。各FACTブロックの\n"
            f"内容・confidence・source記載・限界に関する注記は、条件Bと完全に\n"
            f"同一である(条件Bの研究方法の限界に関する注記も条件Bファイル\n"
            f"本体を参照のこと)。\n\n"
        )
        blocks_text = "\n\n".join(fact_blocks[fid] for fid in included)
        summary = (
            f"\n\n=== {cond['label_ja']} usable fact数の集計(Trial実施者による機械集計) ===\n"
            f"条件A由来(ANCHOR+SUPPORTING、FACT-01〜05): 5件\n"
            f"条件B由来(このLedgerで採用したSUPPORTING、FACT-{'/'.join(included)}): "
            f"{len(included)}件\n"
            f"usable(ANCHOR+SUPPORTING)合計 = {5 + len(included)}件\n"
        )
        full_text = condition_a_text + header_note + blocks_text + summary
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        return full_text

    ledger_c_text = build_condition_ledger("leaveout_c", LEDGER_C_PATH)
    ledger_d_text = build_condition_ledger("twofact_d", LEDGER_D_PATH)

    # 健全性チェック: 条件A全文を含むこと、除外すべきFACTが含まれていないこと
    assert ledger_c_text.startswith(condition_a_text), "条件Cの先頭が条件A全文と不一致"
    assert ledger_d_text.startswith(condition_a_text), "条件Dの先頭が条件A全文と不一致"
    # ブロック見出し("[CONFIRMED_FACT] FACT-XX:")の有無で厳密に検査する
    # (説明文中の「FACT-12/13を除外」等のprose言及とは区別する)。
    for fid in ("12", "13"):
        assert f"[CONFIRMED_FACT] FACT-{fid}:" not in ledger_c_text, f"条件CにFACT-{fid}のブロックが混入しています"
    for fid in ("08", "09", "10", "11", "14"):
        assert f"[CONFIRMED_FACT] FACT-{fid}:" not in ledger_d_text, f"条件DにFACT-{fid}のブロックが混入しています"
    for fid in CONDITION_C_FACT_IDS:
        assert f"[CONFIRMED_FACT] FACT-{fid}:" in ledger_c_text, f"条件CにFACT-{fid}のブロックが欠落しています"
    for fid in CONDITION_D_FACT_IDS:
        assert f"[CONFIRMED_FACT] FACT-{fid}:" in ledger_d_text, f"条件DにFACT-{fid}のブロックが欠落しています"
    print(f"[{THEME_ID}] build_ledgers_stage完了: 条件C={len(ledger_c_text)}文字, "
          f"条件D={len(ledger_d_text)}文字")
    return {"condition_c_chars": len(ledger_c_text), "condition_d_chars": len(ledger_d_text)}


# ============================================================
# Stage 1: setup(Gate相当の事前確認、Trial-12と同一の既定値バイト一致
# テストを再確認)
# ============================================================
def setup_stage() -> dict:
    os.makedirs(REAGG_DIR, exist_ok=True)
    unit_test_result = t3.test_default_hint_is_byte_identical_to_production()
    if unit_test_result["status"] != "PASS":
        raise RuntimeError(f"既定値バイト一致テスト失敗: {unit_test_result}")
    if not os.path.exists(LEDGER_C_PATH) or not os.path.exists(LEDGER_D_PATH):
        raise RuntimeError("条件C/D Ledgerファイルが未作成です。先に build_ledgers を実行すること。")
    run_metadata = {
        "management_id": "FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-LEAVEOUT-TRIAL-12B",
        "parent_trial": "FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12",
        "opus_review": "FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-REVIEW-01",
        "n_per_condition": N_PER_CONDITION,
        "n_definition": "N=6は条件ごとのrun数(A2×3+B1B×3)。条件C/D合計で12 run(新規生成)。"
                        "条件A/Bは既存Trial-12の12 runを¥0で再集計する(新規生成なし)。",
        "conditions": {k: {"ledger_path": v["ledger_path"], "usable_fact_count": v["usable_fact_count"],
                            "label_ja": v["label_ja"], "included_fact_ids": v["included_fact_ids"]}
                       for k, v in CONDITIONS.items()},
        "editorial_type_module_block": "常に空文字(Production既定、Focus Moduleなし)",
        "point_role_hint_block": "常に空文字(Production既定、hintなし)",
        "loop_budget_point_overlap_article_retry_max": prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX,
        "primary_endpoint": "初回attempt(attempt=0)のPoint Value QA判定(PASS/NG)。"
                            "point_overlap_article_retry_log.json[0].value_qa_flagged"
                            "(True=NG, False=PASS)を条件間で比較する。",
    }
    with open(f"{REAGG_DIR}/run_metadata_12b.json", "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] setup_stage完了: unit_test={unit_test_result['status']}, "
          f"条件C/D Ledger確認OK")
    return {"unit_test_result": unit_test_result, "run_metadata": run_metadata}


# ============================================================
# Evidence allocation指標(Trial-12のevidence_allocation_metricsを再利用、
# 無改変でimportして呼び出す)。
# ============================================================
def evidence_allocation_metrics(out_dir: str, retry_attempts: int, usable_fact_count: int) -> dict | None:
    return t12.evidence_allocation_metrics(out_dir, retry_attempts, usable_fact_count)


def load_initial_flag(out_dir: str) -> dict:
    return t12.load_initial_flag(out_dir)


def load_initial_attempt0_qa(out_dir: str) -> dict:
    """主要エンドポイント: attempt=0(初回attempt)のPoint Value QA判定・
    lexical flag・Gate指標(Point対Full Story overlap)を、
    point_overlap_article_retry_log.jsonのattempt=0エントリから直接読む
    (Trial-12のinitial_attempt_flagged[lexical OR value_qa の合成値]とは
    別に、value_qa単体を切り出す。Opus指摘の「本Trial唯一の交絡なし・
    非トートロジー差」を再現するための主要エンドポイント)。"""
    path = f"{out_dir}/point_overlap_article_retry_log.json"
    if not os.path.exists(path):
        return {
            "initial_lexical_flagged": None, "initial_value_qa_flagged": None,
            "initial_value_qa_status": None, "initial_value_qa_label": "NO_LOG",
            "initial_gate_indicator_max_overlap": None,
        }
    with open(path, encoding="utf-8") as f:
        log = json.load(f)
    if not log:
        return {
            "initial_lexical_flagged": None, "initial_value_qa_flagged": None,
            "initial_value_qa_status": None, "initial_value_qa_label": "EMPTY_LOG",
            "initial_gate_indicator_max_overlap": None,
        }
    a0 = log[0]
    value_qa_status = a0.get("value_qa_status")
    if value_qa_status in ("PASS", "NG"):
        label = value_qa_status
    else:
        label = "NOT_EVALUATED"  # split_common_sections_for_point_qaが構造を認識できなかった等
    report = a0.get("report") or {}
    p1 = report.get("point_one", {}).get("before_overlap", {}).get("overlap_ratio")
    p2 = report.get("point_two", {}).get("before_overlap", {}).get("overlap_ratio")
    gate = max(v for v in (p1, p2) if v is not None) if (p1 is not None or p2 is not None) else None
    return {
        "initial_lexical_flagged": a0.get("lexical_flagged"),
        "initial_value_qa_flagged": a0.get("value_qa_flagged"),
        "initial_value_qa_status": value_qa_status,
        "initial_value_qa_label": label,
        "initial_gate_indicator_max_overlap": gate,
    }


# ============================================================
# 費用実測ヘルパー(Trial-12と同一ロジック、このTrial-12b専用ログパス
# [leaveout_c/raw_usage_log.jsonl, twofact_d/raw_usage_log.jsonl]向けに
# 再利用)。
# ============================================================
USD_JPY = t12.USD_JPY
_call_cost_usd = t12._call_cost_usd  # 無改変で再利用(同一pricing_snapshot参照)


def compute_cost_so_far_jpy() -> float:
    total_usd = 0.0
    for log_path in (f"{LEAVEOUT_C_DIR}/raw_usage_log.jsonl", f"{TWOFACT_D_DIR}/raw_usage_log.jsonl"):
        if not os.path.exists(log_path):
            continue
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_usd += _call_cost_usd(json.loads(line))
    return total_usd * USD_JPY


def write_cost_summary() -> dict:
    records = []
    for log_path in (f"{LEAVEOUT_C_DIR}/raw_usage_log.jsonl", f"{TWOFACT_D_DIR}/raw_usage_log.jsonl"):
        if os.path.exists(log_path):
            records.extend(json.loads(l) for l in open(log_path, encoding="utf-8"))
    for r in records:
        r["_cost_usd"] = _call_cost_usd(r)
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-12と同一参照元・"
                       "同一ロジック)。新規research呼び出しなし(条件C/D Ledgerは既存"
                       "条件Bファイルからの機械的抜粋のみ)。",
        "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
        "total_calls": len(records),
    }
    os.makedirs(REAGG_DIR, exist_ok=True)
    with open(f"{REAGG_DIR}/cost_summary_12b.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


# ============================================================
# combo実行(CLI分割実行用、前面同期・逐次実行。バックグラウンド待機なし)
# ============================================================
LABEL_LOOKUP = {label: (label, instruction, level_dir, stage_tag)
                for (label, instruction, level_dir, stage_tag) in LEVELS}


def run_one_combo(client, master_full_text: str, condition_name: str, run_idx: int,
                   label: str, instruction: str, level_dir: str, stage_tag: str) -> dict:
    cond = CONDITIONS[condition_name]
    ledger_text = load_text(cond["ledger_path"])
    out_dir = f"{cond['out_subdir']}/{level_dir}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, t3.HANSHIN_TOPIC_JA, ledger_text, editorial_type_module_block="")
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = t3.run_one_pattern_connected(
            client, theme_tag, label, prompt, ledger_text, t3.HANSHIN_TOPIC_JA, out_dir,
            point_role_hint_block="")
    elapsed = round(time.time() - t0, 2)
    analysis = t4.analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = condition_name
    analysis["level"] = label
    analysis["run"] = run_idx
    analysis.update(load_initial_flag(out_dir))
    analysis.update(load_initial_attempt0_qa(out_dir))
    analysis["evidence_allocation"] = evidence_allocation_metrics(
        out_dir, analysis["retry_attempts"], cond["usable_fact_count"])
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
    print(f"[{THEME_ID}] run{run_idx} {condition_name} {label}: status={result.get('status')} "
          f"retry={analysis['retry_attempts']} initial_value_qa={analysis['initial_value_qa_label']} "
          f"initial_lexical_flagged={analysis['initial_lexical_flagged']} elapsed={elapsed}s")
    return analysis


def combo_stage(condition_name: str, label: str, run_idx: int) -> dict:
    cond = CONDITIONS[condition_name]
    cl.install(f"{cond['out_subdir']}/raw_usage_log.jsonl")
    cost_so_far = compute_cost_so_far_jpy()
    if cost_so_far > BUDGET_JPY:
        raise RuntimeError(f"費用上限超過見込み(実測¥{cost_so_far:.1f} > 上限¥{BUDGET_JPY})。STOPします。")
    client = t3.vfl01.get_client()
    master_full_text = t3.ab01.load_master_full_text()
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP[label]
    analysis = run_one_combo(client, master_full_text, condition_name, run_idx, label, instruction,
                              level_dir, stage_tag)
    combo_results_dir = f"{cond['out_subdir']}/_combo_results"
    os.makedirs(combo_results_dir, exist_ok=True)
    with open(f"{combo_results_dir}/{level_dir}_run{run_idx}.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    return analysis


def cost_stage() -> dict:
    result = write_cost_summary()
    print(f"[{THEME_ID}] 費用実測合計(条件C+D): ¥{result['total_jpy']}")
    return result


def aggregate_stage() -> list:
    all_results = []
    for cond_name, cond in CONDITIONS.items():
        combo_results_dir = f"{cond['out_subdir']}/_combo_results"
        if os.path.isdir(combo_results_dir):
            for fname in sorted(os.listdir(combo_results_dir)):
                with open(f"{combo_results_dir}/{fname}", encoding="utf-8") as f:
                    all_results.append(json.load(f))
    os.makedirs(REAGG_DIR, exist_ok=True)
    with open(f"{REAGG_DIR}/all_results_cd.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] aggregate_stage: {len(all_results)}本を集約しました。")
    return all_results


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "build_ledgers"
    if which == "build_ledgers":
        build_ledgers_stage()
    elif which == "setup":
        setup_stage()
    elif which == "combo":
        # 例: python er011_news_ledger_enrichment_leaveout_trial_12b_run.py combo leaveout_c A2 1
        condition_name, label, run_idx = sys.argv[2], sys.argv[3], int(sys.argv[4])
        combo_stage(condition_name, label, run_idx)
    elif which == "cost":
        cost_stage()
    elif which == "aggregate":
        aggregate_stage()
    else:
        print("usage: python er011_news_ledger_enrichment_leaveout_trial_12b_run.py "
              "[build_ledgers|setup|combo <leaveout_c|twofact_d> <A2|B1B> <run_idx>|cost|aggregate]")
