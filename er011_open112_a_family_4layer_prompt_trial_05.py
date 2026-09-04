# ============================================================
# er011_open112_a_family_4layer_prompt_trial_05.py
# OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05
# ============================================================
# 目的: A Family Writer Promptを以下4層に整理して管理できる設計を作り、
# No.18(Discovery/Why)のArticle-only Trialで、現行品質・安全性・記事構造
# を損なわずに動作するかを検証する。
#   Layer 1: Common Writing Contract (Editorial Type非依存)
#   Layer 2: A Family Common Skeleton (Main Story/Point One/Point Two/
#            In One Lineの役割定義)
#   Layer 3: Discovery/Why Focus Module (今回新規ドラフト。現行Production
#            にはDiscovery固有のprompt文言が独立して存在しないため、今回
#            初めて明文化する)
#   Layer 4: Article-specific Inputs (Topic/Title/Verified Fact Ledger)
#
# 設計方針(リスク最小化): Layer 1・Layer 2に該当する既存prompt文言は、
# er003_v1_n3_01_articles_generate.COMMON_BLOCK_TEMPLATEを一切書き写さず、
# そのままインポートして使う。新規追加はLayer 3(Discovery Focus Module)
# の1ブロックのみとし、既存テンプレートの1箇所(アンカー文字列の直前)へ
# 挿入する。これにより「既存文言の欠落・重複・順序変更が絶対に起きない」
# ことをコード構造そのもので保証し、実際の差分はDiscovery Focus Module
# ブロックの追加1箇所だけになる(Phase Aでdifflibにより機械的に検証する)。
#
# Production変更: なし(er003_v1_n3_01_articles_generate.pyを含む既存
# ファイルは一切変更しない。gen.run_one_pattern()を無変更のまま呼び出す
# だけで、Writer/Evidence Compression/Point Overlap・Value QA/Diagnostic
# Full Retry/Fact Checker/Ledger Deviation Checker(+Local Rewrite)/
# Directional Fact Precheckという既存Production QAチェーン全体をそのまま
# 経由する)。出力先はProductionの出力ディレクトリを一切上書きしない、
# 新規のTrial専用ディレクトリ。
#
# Hookは独立slot化しない(タスク5節の禁止事項)。出力schema変更なし。
#
# 実行数: A2 x1, B1 x1(初回)。Loop Budgetに従い、Prompt構造上の問題と
# 生成揺らぎを切り分けられない場合のみ、各レベル追加1回まで許可。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
# APPROVED_FOR_PRODUCTION・PRODUCTION_WIRED・CURRENT_SPEC変更・
# Production Writerへの正式配線は一切行わない。
from __future__ import annotations

import difflib
import json
import os
import shutil
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
import er011_no18_specfix_v2_production_run_01 as driver

TOPIC_JA = driver.TOPIC_JA
BASELINE_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r"
NEW_THEME_ID = "open112_a_family_4layer_prompt_trial_05"
OUT_DIR = f"er011_output/{NEW_THEME_ID}"

LEVELS = {
    "a2": {"label": "A2", "instruction_attr": "A2_KAI1_INSTRUCTION"},
    "b1b": {"label": "B1B", "instruction_attr": "B1_B_DIRECT_INSTRUCTION"},
}

MAX_RUNS_PER_LEVEL = 2  # Loop Budget(タスク10節)

# ------------------------------------------------------------
# Phase A: 4層への責務マッピング(報告用の構造化データ)
# ------------------------------------------------------------
# 分類根拠: 実コード(gen.COMMON_BLOCK_TEMPLATE)上でtopic/ledger引数に
# 依存する汎用テキストか、theme(hanshin/health/household/No.18)を問わず
# 適用されているかをもとに分類する。「No.18で使われたから」という理由
# だけでは分類しない(OPEN-112-04の既存結論を踏襲)。
LAYER_MAPPING = [
    {"segment": "マスター記事(阪神)によるスタイル参照導入文",
     "layer": "1_common_writing_contract",
     "reason": "全theme共通(hanshin/health/household/No.18)で同一文言が使われる、記事の書き方全体の参照指示"},
    {"segment": "Storytelling First",
     "layer": "1_common_writing_contract",
     "reason": "ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06でPRODUCTION_WIRED、Type非依存"},
    {"segment": "No Jargon",
     "layer": "1_common_writing_contract",
     "reason": "同上。learner-facing本文全体が対象で、記事タイプに依存しない"},
    {"segment": "Evidence-bounded Interpretation",
     "layer": "1_common_writing_contract",
     "reason": "ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09でPRODUCTION_WIRED、Type非依存"},
    {"segment": "記事構成(Title/Main Story/###x2/In One Line、物理slot数)",
     "layer": "2_a_family_common_skeleton",
     "reason": "Main Story/Point One/Point Two/In One Lineという4slotの物理構造そのもの。現行実装では"
               "全theme共通で適用されているが、概念上はA Family(Discovery+News/Trend)の骨格を定義する"
               "ものであり、Skeleton層として扱う。Hookは独立slotとして存在しない(既知のギャップ、OPEN-"
               "112-04で報告済み。今回も独立slot化しない)"},
    {"segment": "Formatting requirements(emoji・装飾bold禁止)",
     "layer": "1_common_writing_contract",
     "reason": "ER-010-NO9-FORMAT-PRODUCTION-AND-FACT-REVIEW-11でPRODUCTION_WIRED、記事構造に依存しない出力規則"},
    {"segment": "Main Storyの役割(中心ストーリーの核心のみ、背景/補助数値/別角度解釈/deeper implicationsを入れない)",
     "layer": "2_a_family_common_skeleton",
     "reason": "Main StoryというSkeleton slotの役割定義そのもの"},
    {"segment": "Point One/Point Twoの役割(Point Balance原則、切り口/示唆/背景/心理/社会的含意等のリスト)",
     "layer": "2_a_family_common_skeleton",
     "reason": "Point One/Two slotの役割定義。News/Trendでも同じ選択肢リストが転用可能(OPEN-112-04 10節で確認済み)"},
    {"segment": "言い換えによる重複禁止 + 生成手順(推奨)",
     "layer": "2_a_family_common_skeleton",
     "reason": "Main StoryとPointの意味的重複を禁止する、Skeleton構造上の制約(ER-008-N8-FINAL-CLOSEOUT-24)"},
    {"segment": "Pointが実際に新しい価値を持つこと",
     "layer": "2_a_family_common_skeleton",
     "reason": "ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01で発見されたが、topic/ledger非依存の汎用ルールとして"
               "全theme共通で配線済み(コード確認済み、No.18固有語のhardcodeなし)"},
    {"segment": "Point One/Twoの長さ目標(30-60/25-70語)、記事全体の長さ(280-420語)",
     "layer": "2_a_family_common_skeleton",
     "reason": "Skeleton各slotの分量ガイドライン"},
    {"segment": "[NEW] Discovery/Why Focus Module",
     "layer": "3_discovery_why_focus_module",
     "reason": "現行Productionには存在しない新規ブロック。Discovery性は現在、Topic文面・Verified Fact Ledger・"
               "Point Role Planningの生成結果を通じて暗黙的にのみ発生しており、明文化されたprompt文言が"
               "存在しない。今回のTrialで初めて明文化し、既存の暗黙的挙動を壊さず補強できるかを検証する"},
    {"segment": "Spoken-first原則(数字の扱い、A-G)",
     "layer": "1_common_writing_contract",
     "reason": "記事タイプに依存しない数字表現の編集原則"},
    {"segment": "今回のFact源について + Fact Ledger使用上の制約",
     "layer": "4_article_specific_inputs / 1_common_writing_contract",
     "reason": "制約文言自体はCommon(Type非依存)。verified_ledger_textの中身(F-001〜F-012等)はArticle-"
               "specific Input"},
    {"segment": "CEFR難易度指示(A2_KAI1_INSTRUCTION / B1_B_DIRECT_INSTRUCTION)",
     "layer": "1_common_writing_contract",
     "reason": "Editorial Type軸と直交する別軸(難易度軸)。全themeで共通のA2/B1指示文をそのまま使用"},
    {"segment": "Point Role Planning block(role/new_listener_takeaway/evidence_anchor/why_it_matters/"
               "重複禁止の計画結果)",
     "layer": "1_common_writing_contract",
     "reason": "topic/verified_ledger_textを引数に取る汎用モジュール(er011_point_role_value_planning_01."
               "py)。コード確認済み、No.18固有のhardcodeなし"},
    {"segment": "Topic本文・Title・Verified Fact Ledger本体(F-001〜F-012等の具体的Fact・数値・出典)",
     "layer": "4_article_specific_inputs",
     "reason": "No.18固有の入力。Layer1〜3のいずれのコード・テキストにもhardcodeされていないことを確認済み"},
]

# ------------------------------------------------------------
# Layer 3: Discovery/Why Focus Module(新規ドラフト)
# ------------------------------------------------------------
# 挿入位置: COMMON_BLOCK_TEMPLATE中の「【Spoken-first原則(数字の扱い)】」
# の直前(Skeleton役割定義がすべて終わった直後、数字の編集原則より前)。
# 既存文言は一切書き換えず、この1ブロックを追加するだけ。
ANCHOR = "【Spoken-first原則(数字の扱い)】"

DISCOVERY_FOCUS_MODULE_BLOCK = """【Discovery/Why Focus(今回のTrialで追加する、記事タイプ固有の焦点。\
OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05、Production未採用)】
この記事は、ある現象や結果が実際になぜ起こるのかを、聞き手に理解してもらうことを中心的な
目的とする記事です。これは、上記のMain Story/Point One/Point Twoの役割定義を置き換える
ものではなく、より具体的にする補足です。

Main Storyでは、まず「何が観察されたか」という現象そのものを伝えてください。「なぜそれが
起こるのか」という答えをMain Storyだけで説明しきってしまわないでください。

Point One・Point Twoでは、その現象が実際に起こる理由・仕組み・意外な詳細のうち、異なる
角度をそれぞれ一つずつ深掘りしてください(例: 心理的な理由、環境や設計上の要因、社会的・
日常的な文脈)。両方が同じ角度から「なぜ」を説明しないでください。

Evidenceが支持する範囲を超えて、「なぜ起こるか」の説明を断定しないでください。Verified
Fact Ledgerのある項目が、著者の解釈である旨をwriter_guidance等で明記している場合は、記事
内でも「研究者らはこう解釈している」という形で書き、直接測定された結果と著者の解釈を混同
しないでください。Ledgerが直接支持していない限り、「自動的」「不随意的」「必ず」のような
断定表現は使わないでください。

In One Lineでは、Main Storyで伝えた現象と、Point One・Point Twoで深掘りした理由・示唆を
結びつけ、聞き手が持ち帰れる静かな一言として締めてください。単なる要約にはしないで
ください。"""


def build_candidate_template() -> str:
    assert ANCHOR in gen.COMMON_BLOCK_TEMPLATE, (
        "アンカー文字列がgen.COMMON_BLOCK_TEMPLATE内に見つかりません。Production側のtemplateが"
        "本Trial設計時から変更されている可能性があるため、Phase Aを中断してください(STOP条件)。")
    return gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, DISCOVERY_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)


def build_candidate_prompt(candidate_template: str, master_full_text: str, topic: str,
                            verified_ledger_text: str, instruction: str) -> str:
    common_block = candidate_template.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block="", evidence_compression_block="")
    return gen.build_prompt(common_block, instruction)


# ------------------------------------------------------------
# Phase A: 静的差分確認
# ------------------------------------------------------------
def run_phase_a(master_full_text: str, verified_ledger_text: str) -> dict:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    candidate_template = build_candidate_template()

    with open(f"{OUT_DIR}/audit/layer_mapping.json", "w", encoding="utf-8") as f:
        json.dump(LAYER_MAPPING, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/discovery_focus_module_block.txt", "w", encoding="utf-8") as f:
        f.write(DISCOVERY_FOCUS_MODULE_BLOCK)

    results = {}
    for level, meta in LEVELS.items():
        instruction = getattr(gen, meta["instruction_attr"])
        candidate_prompt = build_candidate_prompt(
            candidate_template, master_full_text, TOPIC_JA, verified_ledger_text, instruction)
        baseline_path = f"{BASELINE_DIR}/{level}/audit/prompt.txt"
        with open(baseline_path, encoding="utf-8") as f:
            baseline_prompt = f.read()

        with open(f"{OUT_DIR}/audit/candidate_prompt_{level}.txt", "w", encoding="utf-8") as f:
            f.write(candidate_prompt)

        sm = difflib.SequenceMatcher(a=baseline_prompt, b=candidate_prompt, autojunk=False)
        opcodes = sm.get_opcodes()
        non_equal = [op for op in opcodes if op[0] != "equal"]
        # 期待する差分は「1箇所のinsert(Discovery Focus Module追加)」のみ。
        # replace/delete、または2箇所以上のinsertが出た場合は意図しない変更。
        unexpected = [op for op in non_equal if op[0] != "insert"]
        insert_ops = [op for op in non_equal if op[0] == "insert"]
        # difflibのSequenceMatcherは、同一文字列("ください。\n\n"等)が複数箇所に
        # 現れる場合、equal/insertの境界を(内容として等価な複数の分割のうち)
        # どれか1つへ非決定的にずらすことがある(算出されるop数・total insert文字数
        # 自体は変わらない)。このため、ここでは「baseline_promptのANCHOR直前へ
        # DISCOVERY_FOCUS_MODULE_BLOCKを機械的に1回だけ挿入した文字列」と
        # candidate_promptが完全一致するかを直接検証する、境界のずれに影響
        # されない、より厳密な再構成一致テストを用いる。
        reconstructed = baseline_prompt.replace(
            ANCHOR, DISCOVERY_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)
        clean_single_insert = (
            len(unexpected) == 0 and len(insert_ops) == 1
            and reconstructed == candidate_prompt
        )

        diff_lines = list(difflib.unified_diff(
            baseline_prompt.splitlines(keepends=True),
            candidate_prompt.splitlines(keepends=True),
            fromfile=f"baseline_{level}", tofile=f"candidate_{level}", n=2))
        with open(f"{OUT_DIR}/audit/diff_{level}.txt", "w", encoding="utf-8") as f:
            f.writelines(diff_lines)

        results[level] = {
            "baseline_len": len(baseline_prompt),
            "candidate_len": len(candidate_prompt),
            "op_counts": {tag: sum(1 for o in opcodes if o[0] == tag) for tag in
                          ("equal", "insert", "delete", "replace")},
            "unexpected_op_count": len(unexpected),
            "clean_single_insert_confirmed": clean_single_insert,
        }
        print(f"[TRIAL-05][Phase A][{level}] op_counts={results[level]['op_counts']} "
              f"clean_single_insert_confirmed={clean_single_insert}")

    phase_a_pass = all(r["clean_single_insert_confirmed"] for r in results.values())
    with open(f"{OUT_DIR}/audit/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "phase_a_pass": phase_a_pass}, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-05][Phase A] phase_a_pass={phase_a_pass}")
    return {"results": results, "phase_a_pass": phase_a_pass, "candidate_template": candidate_template}


# ------------------------------------------------------------
# Phase B: No.18 Article-only Trial(実Production関数を無変更のまま使用)
# ------------------------------------------------------------
def prepare_research_dir() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    new_research_dir = f"{OUT_DIR}/research"
    if not os.path.isdir(new_research_dir):
        shutil.copytree(f"{BASELINE_DIR}/research", new_research_dir)
        print(f"[TRIAL-05] research/ を {BASELINE_DIR} から {OUT_DIR} へコピーしました(Ledger自体は無変更)。")


def run_level(client, candidate_template: str, master_full_text: str, verified_ledger_text: str,
              level: str, run_idx: int) -> dict:
    meta = LEVELS[level]
    instruction = getattr(gen, meta["instruction_attr"])
    candidate_prompt = build_candidate_prompt(
        candidate_template, master_full_text, TOPIC_JA, verified_ledger_text, instruction)
    level_out_dir = f"{OUT_DIR}/{level}_run{run_idx:02d}"

    print(f"[TRIAL-05][Phase B] {meta['label']} run{run_idx}: gen.run_one_pattern()(実Production関数、"
          f"無変更)開始...")
    t0 = time.time()
    with cl.logging_context(NEW_THEME_ID, f"writer_{level}_run{run_idx:02d}"):
        result = gen.run_one_pattern(
            client, NEW_THEME_ID, meta["label"], candidate_prompt, verified_ledger_text, TOPIC_JA,
            level_out_dir)
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

    print(f"[TRIAL-05][Phase B] {meta['label']} run{run_idx}: 完了。status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
          f"directional_fact_precheck_status={result.get('directional_fact_precheck_status')} "
          f"writer_model={writer_model} elapsed={result['elapsed_seconds']}s")
    return result


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    master_full_text = ab01.load_master_full_text()
    with open(f"{BASELINE_DIR}/research/verified_fact_ledger.txt", encoding="utf-8") as f:
        verified_ledger_text = f.read()

    phase_a = run_phase_a(master_full_text, verified_ledger_text)
    if not phase_a["phase_a_pass"]:
        print("[TRIAL-05] Phase Aで意図しない差分を検出したため、Phase Bへ進まずSTOPします。")
        return {"phase_a": phase_a, "phase_b": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    prepare_research_dir()
    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial05_articles.jsonl")

    phase_b = {}
    for level in ["a2", "b1b"]:
        phase_b[level] = [run_level(client, phase_a["candidate_template"], master_full_text,
                                     verified_ledger_text, level, 1)]

    with open(f"{OUT_DIR}/trial05_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "phase_a": phase_a["results"],
            "phase_b": {lvl: [{k: v for k, v in r.items() if k != "article_text"} for r in runs]
                        for lvl, runs in phase_b.items()},
        }, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TRIAL-05] 完了。summary -> {OUT_DIR}/trial05_summary.json")
    return {"phase_a": phase_a, "phase_b": phase_b, "status": "DONE"}


if __name__ == "__main__":
    main()
