# ============================================================
# er011_open112_trend_synthesis_minimal_prompt_trial_09.py
# OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09
# ============================================================
# 目的: News系(A Family)のTrend Synthesisモードについて、最小限の
# Focus Module Promptを作成し、実際のテーマ(米国・イラン、ホルムズ海峡の
# 長期膠着)で記事Trialを1本(A2・B1B各1回)行い、
#   - 複数Signalを列挙せず統合できるか
#   - Trendを作りすぎないか(overclaim)
#   - Counter-signal/limitationを適切に残せるか
#   - 既存Fact Safety/QAだけでどこまで安全に運用できるか
# を確認する。
#
# 設計方針(タスク5節「なるべく軽く」): 新Validator・新しい複雑なQAは
# 追加しない。既存Production Writer/QAチェーン(gen.run_one_pattern、
# 無変更)をそのまま経由させ、実際の記事を1本生成して影響を測定する。
#
# 構造: er011_open112_a_family_4layer_prompt_trial_05.py(Discovery/Why
# Focus Moduleの先行Trial)と同じ「Anchor 1箇所への単一Module挿入」設計を
# 踏襲する。Layer 1(Common Writing Contract)・Layer 2(A Family Common
# Skeleton)はDiscovery/Whyと完全共有、Layer 3にTrend Synthesis専用の
# Focus Moduleを新規追加する。
#
# Phase Aの位置づけ(trial_05と同じ): Phase Aの「単一clean insert」検証は
# No18(Discovery/Why)のbaseline prompt/ledgerを固定リファレンスとして
# 使う、テーマに依存しない機械的検証(テンプレート編集そのものが安全かの
# 確認)。Phase B(実際の記事生成)は本Trial専用の新しいテーマ・Ledger
# (Iran/Hormuz、2026年9月に実際にWeb検索で新規収集)を使う。この2つは
# 独立している。
#
# Production変更: なし。er003_v1_n3_01_articles_generate.pyを含む既存
# ファイルは一切変更しない。gen.run_one_pattern()を無変更のまま呼び出す
# だけで、Writer/Point Role Planning/Evidence Compression/Point Overlap・
# Value QA・Diagnostic Full Retry/Fact Checker/Ledger Deviation Checker/
# Directional Fact Precheckという既存Production QAチェーン全体をそのまま
# 経由する。出力先はProductionディレクトリを一切上書きしない、新規の
# Trial専用ディレクトリ。Topic Master(topic_package_*.py)への正式追加は
# 行わない(本ファイル内で新規テーマを完結させる)。
#
# 今回禁止(タスク16節): Production Prompt/code変更、News Focus Module
# 正式実装、Major/Daily News Trial、新Validator追加、Trend Memory実装、
# Personalization実装、Diagnostic Full Retry変更、Topic Master変更、
# APPROVED_FOR_PRODUCTION、PRODUCTION_WIRED。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
# VALIDATEDでもProduction採用を意味しない。
from __future__ import annotations

import json
import os
import shutil
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import difflib

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
import er011_no18_specfix_v2_production_run_01 as driver

# Phase A(機械的diff検証)専用の固定リファレンス。テーマ内容には無関係。
PHASE_A_BASELINE_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r"
PHASE_A_TOPIC_JA = driver.TOPIC_JA

NEW_THEME_ID = "open112_trend_synthesis_minimal_prompt_trial_09"
OUT_DIR = f"er011_output/{NEW_THEME_ID}"
TRIAL_RESEARCH_DIR = f"{OUT_DIR}/research"

# ------------------------------------------------------------
# Phase B用: 本Trial専用の新規テーマ(Iran/Hormuz、2026年9月)
# 実際にWebSearch/WebFetchで新規収集した信号に基づく(§3・§19記録参照)。
# Topic Masterへの正式追加ではなく、本スクリプト内で完結するTrial専用入力。
# ------------------------------------------------------------
TREND_TOPIC_JA = (
    "2026年2月末に米国とイスラエルがイランへの空爆を開始して始まった軍事衝突は、"
    "6月14日の停戦合意(memorandum of understanding)といったん解除された封鎖を経て、"
    "7月にイランが事前承認航路外の商船3隻を攻撃したことで7月14日に封鎖が再開された。"
    "8月には、イラン国内の石油化学プラント停止や天然ガス生産能力の喪失が報じられる一方、"
    "米海軍はホルムズ海峡の交通分離帯で100個以上の疑わしい機雷を発見・除去する作戦を行った。"
    "8月18日にはトランプ大統領がイランとの協議予定がないと述べ、60日間の交渉期限も合意なく"
    "過ぎた。民間政治リスク分析会社Eurasia Groupは、9月までの和平という従来の見通しを"
    "撤回し、緊張緩和の時期予測を年末へ先送りした。9月4日付のCNN報道は、約1か月の小康状態が"
    "終わり、地域が『持続不可能になりつつある』軍事的膠着状態へ戻りつつあると伝えている。"
    "他方で9月2日、米エネルギー長官Chris Wrightは、9月1日の原油通過量が1日1700万バレルを"
    "超え開戦後最高値を記録したとして、イランは海峡を妨害する能力を失いつつあると主張して"
    "おり、これは米エネルギー情報局(EIA)の四半期統計(開戦前平均2000万バレル超/日 → "
    "2026年第2四半期平均490万バレル/日)が示す落ち込みの大きさと、少なくとも表面的に"
    "対立する評価である。今回の記事は、この一つ一つの出来事ではなく、複数の独立した信号が"
    "積み重なって示す『長期化する経済的消耗戦』という変化そのものを扱う、Trend Synthesis"
    "タイプの記事である。"
)

with open(f"{TRIAL_RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as _f:
    TREND_VERIFIED_LEDGER_TEXT = _f.read()

LEVELS = {
    "a2": {"label": "A2", "instruction_attr": "A2_KAI1_INSTRUCTION"},
    "b1b": {"label": "B1B", "instruction_attr": "B1_B_DIRECT_INSTRUCTION"},
}

MAX_RUNS_PER_LEVEL = 2  # Loop Budget(タスク10節。初回1回、判別困難時のみ追加1回まで)

# ------------------------------------------------------------
# Layer 3: Trend Synthesis Focus Module(今回新規ドラフト、最小限)
# ------------------------------------------------------------
# 挿入位置はDiscovery Trial(trial_05)と同一Anchor。
ANCHOR = "【Spoken-first原則(数字の扱い)】"

TREND_SYNTHESIS_FOCUS_MODULE_BLOCK = """【Trend Synthesis Focus(今回のTrialで追加する、記事タイプ固有の焦点。\
OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09、Production未採用)】
この記事は、単発の出来事を報じる記事ではありません。複数の独立した材料(Signal)が
積み重なって示す「何が変化しつつあるのか」を、聞き手に伝えることを目的とする記事です。
これは、上記のMain Story/Point One/Point Twoの役割定義を置き換えるものではなく、
より具体的にする補足です。

Main Storyでは、個々のSignalを出典ごとに列挙しないでください。まず、複数のSignalに
共通して見える変化・方向性そのものを、代表的な材料を使って提示してください。Trendの
強さを、Verified Fact Ledgerが実際に支持する範囲より強く書かないでください。早い段階の
兆候(early signs)を、既に確立したTrend(established trend)であるかのように書かないで
ください。

Point One・Point Twoでは、それぞれ異なる役割を持たせてください(候補: 最も強い
Signal・主な変化の要因・仕組み、または反証Signal・限界・影響を受ける対象・今後の
分岐点・実生活上の意味)。Point One・Point Twoの両方が「Signal Aの紹介」「Signal Bの
紹介」のような、個々の材料の説明だけで終わらないでください。それぞれのPointが、その
材料が何を意味するのかという意味づけの違いを持つようにしてください。

Point Twoでは、counter-signal(反証Signal)またはlimitation(限界)のいずれかを、
既定の優先候補として検討してください。Verified Fact Ledgerにcounter-signalとして
明記された項目がある場合は、それを無視せず記事内に残してください。Evidenceの強さが
情報源によって異なる場合(例: 政府公式統計と、政治的立場を持つ媒体の報道、当事者の
発言)、それらを同列の証拠として扱わないでください。証拠が一部の当事者・一部の期間・
一部の地域にしか及ばない場合は、その範囲を実際より広く一般化しないでください。相関
関係や時間的な前後関係だけから、因果関係を断定しないでください。複数のSignalの評価が
互いに矛盾・対立している場合(mixed)は、無理にどちらかが正しいと結論づけず、対立して
いること自体を「mixed」として明示してください。

In One Lineでは、この変化がどちらの方向を向いているかと、その確からしさの度合い
(Evidenceの強さに見合った留保)の両方を、静かな一言として結びつけてください。単なる
要約にはしないでください。"""


def build_candidate_template() -> str:
    assert ANCHOR in gen.COMMON_BLOCK_TEMPLATE, (
        "アンカー文字列がgen.COMMON_BLOCK_TEMPLATE内に見つかりません。Production側のtemplateが"
        "本Trial設計時から変更されている可能性があるため、Phase Aを中断してください(STOP条件)。")
    return gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, TREND_SYNTHESIS_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)


def build_candidate_prompt(candidate_template: str, master_full_text: str, topic: str,
                            verified_ledger_text: str, instruction: str) -> str:
    common_block = candidate_template.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block="", evidence_compression_block="")
    return gen.build_prompt(common_block, instruction)


# ------------------------------------------------------------
# Phase A: 静的差分確認(テーマ非依存、trial_05と同じ機械的検証)
# ------------------------------------------------------------
def run_phase_a(master_full_text: str, phase_a_ledger_text: str) -> dict:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    candidate_template = build_candidate_template()

    with open(f"{OUT_DIR}/audit/trend_synthesis_focus_module_block.txt", "w", encoding="utf-8") as f:
        f.write(TREND_SYNTHESIS_FOCUS_MODULE_BLOCK)

    results = {}
    for level, meta in LEVELS.items():
        instruction = getattr(gen, meta["instruction_attr"])
        candidate_prompt = build_candidate_prompt(
            candidate_template, master_full_text, PHASE_A_TOPIC_JA, phase_a_ledger_text, instruction)
        baseline_path = f"{PHASE_A_BASELINE_DIR}/{level}/audit/prompt.txt"
        with open(baseline_path, encoding="utf-8") as f:
            baseline_prompt = f.read()

        with open(f"{OUT_DIR}/audit/phase_a_candidate_prompt_{level}.txt", "w", encoding="utf-8") as f:
            f.write(candidate_prompt)

        sm = difflib.SequenceMatcher(a=baseline_prompt, b=candidate_prompt, autojunk=False)
        opcodes = sm.get_opcodes()
        non_equal = [op for op in opcodes if op[0] != "equal"]
        unexpected = [op for op in non_equal if op[0] != "insert"]
        insert_ops = [op for op in non_equal if op[0] == "insert"]
        reconstructed = baseline_prompt.replace(
            ANCHOR, TREND_SYNTHESIS_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)
        clean_single_insert = (
            len(unexpected) == 0 and len(insert_ops) == 1
            and reconstructed == candidate_prompt
        )

        diff_lines = list(difflib.unified_diff(
            baseline_prompt.splitlines(keepends=True),
            candidate_prompt.splitlines(keepends=True),
            fromfile=f"baseline_{level}", tofile=f"candidate_{level}", n=2))
        with open(f"{OUT_DIR}/audit/phase_a_diff_{level}.txt", "w", encoding="utf-8") as f:
            f.writelines(diff_lines)

        results[level] = {
            "baseline_len": len(baseline_prompt),
            "candidate_len": len(candidate_prompt),
            "op_counts": {tag: sum(1 for o in opcodes if o[0] == tag) for tag in
                          ("equal", "insert", "delete", "replace")},
            "unexpected_op_count": len(unexpected),
            "clean_single_insert_confirmed": clean_single_insert,
        }
        print(f"[TRIAL-09][Phase A][{level}] op_counts={results[level]['op_counts']} "
              f"clean_single_insert_confirmed={clean_single_insert}")

    phase_a_pass = all(r["clean_single_insert_confirmed"] for r in results.values())
    with open(f"{OUT_DIR}/audit/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "phase_a_pass": phase_a_pass}, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-09][Phase A] phase_a_pass={phase_a_pass}")
    return {"results": results, "phase_a_pass": phase_a_pass, "candidate_template": candidate_template}


# ------------------------------------------------------------
# Phase B: Iran/Hormuz Trend Synthesis Trial(実Production関数を無変更のまま使用)
# ------------------------------------------------------------
def run_level(client, candidate_template: str, master_full_text: str, level: str, run_idx: int) -> dict:
    meta = LEVELS[level]
    instruction = getattr(gen, meta["instruction_attr"])
    candidate_prompt = build_candidate_prompt(
        candidate_template, master_full_text, TREND_TOPIC_JA, TREND_VERIFIED_LEDGER_TEXT, instruction)
    level_out_dir = f"{OUT_DIR}/{level}_run{run_idx:02d}"

    print(f"[TRIAL-09][Phase B] {meta['label']} run{run_idx}: gen.run_one_pattern()(実Production関数、"
          f"無変更)開始...")
    t0 = time.time()
    with cl.logging_context(NEW_THEME_ID, f"writer_{level}_run{run_idx:02d}"):
        result = gen.run_one_pattern(
            client, NEW_THEME_ID, meta["label"], candidate_prompt, TREND_VERIFIED_LEDGER_TEXT,
            TREND_TOPIC_JA, level_out_dir)
    elapsed = time.time() - t0
    result["elapsed_seconds"] = round(elapsed, 1)

    with open(f"{level_out_dir}/audit/candidate_prompt_used.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    writer_model = None
    try:
        with open(f"{level_out_dir}/audit/writer_attempts.json", encoding="utf-8") as f:
            attempts = json.load(f)
        pass_attempt = next((a for a in attempts if a["status"] == "STRUCTURE_PASS"), None)
        writer_model = pass_attempt.get("model") if pass_attempt else None
    except FileNotFoundError:
        pass
    result["writer_model_actual"] = writer_model

    print(f"[TRIAL-09][Phase B] {meta['label']} run{run_idx}: 完了。status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
          f"directional_fact_precheck_status={result.get('directional_fact_precheck_status')} "
          f"writer_model={writer_model} elapsed={result['elapsed_seconds']}s")
    return result


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    master_full_text = ab01.load_master_full_text()
    with open(f"{PHASE_A_BASELINE_DIR}/research/verified_fact_ledger.txt", encoding="utf-8") as f:
        phase_a_ledger_text = f.read()

    phase_a = run_phase_a(master_full_text, phase_a_ledger_text)
    if not phase_a["phase_a_pass"]:
        print("[TRIAL-09] Phase Aで意図しない差分を検出したため、Phase Bへ進まずSTOPします。")
        return {"phase_a": phase_a, "phase_b": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial09.jsonl")

    phase_b = {}
    for level in ["a2", "b1b"]:
        phase_b[level] = [run_level(client, phase_a["candidate_template"], master_full_text, level, 1)]

    with open(f"{OUT_DIR}/trial09_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "phase_a": phase_a["results"],
            "phase_b": {lvl: [{k: v for k, v in r.items() if k != "article_text"} for r in runs]
                        for lvl, runs in phase_b.items()},
        }, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TRIAL-09] 完了。summary -> {OUT_DIR}/trial09_summary.json")
    return {"phase_a": phase_a, "phase_b": phase_b, "status": "DONE"}


if __name__ == "__main__":
    main()
