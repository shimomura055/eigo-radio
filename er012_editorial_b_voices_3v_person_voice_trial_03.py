# ============================================================
# er012_editorial_b_voices_3v_person_voice_trial_03.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-03
# ============================================================
# Lane: Lane B(並列稼働中: Reconciliation Gate[読取]、FACT-03再検証
# [er003_output/]、SSOT統合。いずれも本ファイルとは無関係)。
# **Trial(Production・Trial-07・registry・Contract・Prompt本体の編集禁止、
# SSOT・Git禁止)**。
#
# ユーザー決定(2026-09-09、Trial-02 Report §10のUSER_DECISION_REQUIRED
# [尺目標未達、497語/395.3秒]を受けたもの): 3V Trial-02(`EDITORIAL-B-
# FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02_REPORT.md`、最終版`er012_output/
# editorial_b_voices_3v_person_voice_trial_02/b1b_run01_attempt2/
# article.md`、497語/約395秒、Tension 132語)について、**Tensionだけを
# 75〜90語へ短縮する再生成を1回だけ実施**する。保持条件: 3 concrete human
# Voices / 賛否構図にしない / Analytical Leakage 0 / Fact A' PASS /
# Tensionでexternal constraints(fairness/bias/accountability/law/
# compliance)を統合 / Voices自身へ抽象軸を戻さない / Distinctnessを崩さない。
# 短縮後に実測尺(見積り)を確認。統合品質が維持されればcloseout分類
# (VALIDATED)。崩れた場合は無限retryせず、395秒許容案を含めUSER_DECISION_
# REQUIRED。
#
# 方式: Trial-02(`er012_editorial_b_voices_3v_person_voice_trial_02.py`、
# 無変更、モジュールとしてimportし経路を再利用する)の最終article.md
# (b1b_run01_attempt2)を読み取り専用の入力として、**Tension section本文
# だけ**をLLM 1回のみで圧縮再生成する。Hook・Voice 1〜3・Closing(見出し
# 含む)・Tension見出し自体は一切変更せず、単純文字列置換(`article_text.
# replace(old_tension_body, new_tension_body, 1)`)でTension本文のみを
# 差し替える(他sectionはbyte単位で不変であることをスクリプトで検証・
# 記録する)。
#
# Tension圧縮promptは、Trial-02のFocus Module Block(B_FAMILY_VOICES_3V_
# FOCUS_MODULE_BLOCK)がTensionへ課していた構造(共通前提→分岐点→
# 非対称性→外部制約の統合、この順序、地の文としてひとつづき)をそのまま
# 踏襲し、「新しい事実・数字・因果関係を追加しない」「既存Tension本文の
# 圧縮編集のみ」という制約を追加した専用promptを使う(Trial-02のTension
# roleテキストをベースに構成、新しいFocus Module全体は作らない)。
#
# 再生成後、記事全体に対して: Fact Checker A'(Production関数経由、
# `registry.build_voice_attribution_block()`→`b1prod.run_fact_checker()`、
# Trial-02と同一チェーン、無変更)、Ledger Deviation Checker+Local
# Rewrite(Trial-02と同一の`run_ledger_deviation_and_local_rewrite()`、
# 全文へ適用、既存安全装置[MAX_REWRITE_CYCLES=3]は維持・独自に回避しない)、
# Analytical Leakage Check 3V版(全section、`leak_tension_constraint_
# integration`・`leak_binary_camp_split`基準含む)、Pairwise Voice
# Distinctness Check(一括[主]+有向[診断]、Trial-02と同一関数)、Point
# Overlap QA monitoring(有向9値、記録のみ)、語数・尺見積り(Trial-02と
# 同一の`build_word_count_and_duration_estimate()`)を実行する。
#
# Ledger: Trial-02と同一(`er012_output/ai_screening_ledger_trial_01/
# research/verified_fact_ledger.txt`)、読み取り専用、無改変。
#
# 禁止: Tension以外の再生成、2回目以降のTension再生成(Leakage/Ledgerが
# 是正を要求した場合でも既存Local Rewrite[文単位]以外の全文再生成はしない)、
# Production/Trial-07/registry/Contract編集、Ledger改変、SSOT・Git、
# 音声生成、バックグラウンド待機(前面同期)、完了報告後の自動復帰。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
from __future__ import annotations

import itertools
import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er012_editorial_b_voices_3v_person_voice_trial_02 as t02  # Trial-02(先行Trial、無変更、経路再利用のためimport)

THEME_ID = "editorial_b_voices_3v_person_voice_trial_03"
OUT_DIR = "er012_output/editorial_b_voices_3v_person_voice_trial_03"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

LABEL = t02.LABEL  # "B1B"

TRIAL_02_FINAL_ARTICLE_PATH = (
    "er012_output/editorial_b_voices_3v_person_voice_trial_02/b1b_run01_attempt2/article.md")

TENSION_WORD_TARGET_LOWER = 75
TENSION_WORD_TARGET_UPPER = 90

# ============================================================
# Tension圧縮専用prompt(新規執筆ではなく、既存の承認済み内容[Trial-02
# 最終article.mdのTension本文、Fact A'・Ledger Deviation・Leakage
# Check全PASS済み]を圧縮するだけの編集タスクとして設計する。新しい事実・
# 数字を追加させないことで、Fact/Ledgerリスクを最小化する)。
# ============================================================
TENSION_COMPRESSION_DEVELOPER_MESSAGE = (
    "あなたは、英語ニュース解説記事のTensionセクション(3人の異なる立場の人物の物語を統合する"
    "段落)を担当する、経験豊富な英語エディターです。今回のタスクは新規執筆ではなく、既に承認済みの"
    "内容を、意味・構造・事実関係を変えずに、指定された語数まで圧縮する編集作業だけです。新しい"
    "事実・数字・因果関係・比較を追加してはいけません。"
)

TENSION_COMPRESSION_PROMPT_TEMPLATE = """以下は、あるニュース解説記事(3人の異なる立場の人物: (1) Applicant=AIスクリーニングを
受ける応募者, (2) Recruiter/Hiring Manager=採用担当者, (3) Business Owner=経営者)の記事です。

【記事の残りの部分(参考、変更しないでください。文脈理解のためだけに提示します)】
# {title}

## {hook_heading}
{hook_body}

### {voice1_heading}
{voice1_body}

### {voice2_heading}
{voice2_body}

### {voice3_heading}
{voice3_body}

## {closing_heading}
{closing_body}

【圧縮対象: Tensionセクション「## {tension_heading}」の本文(現在約{original_word_count}語、
目標{lower}〜{upper}語)】
現在のTension本文:
{original_tension}

【編集ルール(厳守)】
このTension本文を、**{lower}〜{upper}語**に圧縮してください。これは新規執筆ではなく、既存の
内容を削って凝縮する編集作業です。以下を必ず守ってください:

1. 以下の4要素を、この順序で、地の文としてひとつづきに保ってください(要素そのものを削除
   しないこと):
   (1) 共通前提: 3人とも本当は同じこと(適切な人が適切な仕事に就くこと)を望んでいるという
       出発点。
   (2) 分岐点: 3人がそれぞれ何を賭けているかの違い(3人の発言内容の要約・時系列の反復には
       しないこと)。
   (3) 非対称性: Applicantはプロセスに対する発言権を持たない、Recruiter/Hiring Managerは
       日々ツールを運用するが導入を決める側ではない、Business Ownerは導入を決め結果の責任を
       負う、というプロセス上の力関係の違い。
   (4) 外部制約の統合: 外部制約(ニューヨーク市の監査・通知義務、EU AI Actのhigh-risk分類、
       Amazonの事例のいずれか、現在の本文で使われているもの)が、3人それぞれの選択肢を
       具体的にどう制約しているために、3人の合理性の単純合計では答えにならないのかを、地の
       文の中で説明する(規制名の紹介・列挙だけで終わらせないこと)。
2. 新しい事実・数字・因果関係・比較を追加しないでください(元のTension本文に既に書かれている
   内容のみを使い、削る・言い換える・つなげ直すことだけを行ってください)。
3. 3人を単純に「応募者1人 vs 採用担当+経営者2人」のような2対1の陣営に分けないでください。
4. 文の主語がsurvey/research/data/percentageになる文を作らないでください。
5. 外部制約を含む文をすべて仮に削除したと想定した場合、「3人の合理性を単純に足しても答えに
   ならない」という結論が成立しなくなるように(=外部制約が結論に不可欠であるように)保って
   ください。単なる付け足しにしないでください。
6. Voice本文で使われている抽象的な立場のラベル(例: 「効率性」)へ逆戻りさせないでください。
7. 出力は、Tension本文のみにしてください(見出しは不要、地の文の1段落、Markdown記法不要、
   前置き・後書きの説明文も不要です)。

書き終えたら、語数がおおよそ{lower}〜{upper}語の範囲に収まっているか自分で確認してから
出力してください。
"""


def build_tension_compression_prompt(sections: dict, title: str, original_word_count: int) -> str:
    return TENSION_COMPRESSION_PROMPT_TEMPLATE.format(
        title=title,
        hook_heading=sections["hook_heading"], hook_body=sections["hook_body"],
        voice1_heading=sections["point_one_heading"], voice1_body=sections["point_one_body"],
        voice2_heading=sections["point_two_heading"], voice2_body=sections["point_two_body"],
        voice3_heading=sections["point_three_heading"], voice3_body=sections["point_three_body"],
        closing_heading=sections["closing_heading"], closing_body=sections["closing_body"],
        tension_heading=sections["tension_heading"], original_tension=sections["tension_body"],
        original_word_count=original_word_count,
        lower=TENSION_WORD_TARGET_LOWER, upper=TENSION_WORD_TARGET_UPPER,
    )


def regenerate_tension_only(client, sections: dict, title: str, model: str, reasoning_effort: str,
                             out_dir: str) -> dict:
    """Tension本文だけをLLM 1回のみ(retryなし)で圧縮再生成する。"""
    original_tension = sections["tension_body"]
    original_word_count = ab01.compute_word_count(original_tension)
    prompt = build_tension_compression_prompt(sections, title, original_word_count)
    with open(f"{out_dir}/audit/tension_compression_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"[3V-PERSON-VOICE-TRIAL-03] Tension圧縮再生成開始(1回のみ、retryなし)。"
          f"original_word_count={original_word_count}")
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "developer", "content": TENSION_COMPRESSION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    if response.model != model:
        raise RuntimeError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    new_tension_body = (getattr(response, "output_text", None) or "").strip()
    if not new_tension_body:
        raise RuntimeError("Tension圧縮再生成の応答が空です")
    new_word_count = ab01.compute_word_count(new_tension_body)

    result = {
        "model": response.model, "response_id": response.id,
        "original_tension_body": original_tension, "original_word_count": original_word_count,
        "new_tension_body": new_tension_body, "new_word_count": new_word_count,
        "word_count_within_target": TENSION_WORD_TARGET_LOWER <= new_word_count <= TENSION_WORD_TARGET_UPPER,
        "target_range": [TENSION_WORD_TARGET_LOWER, TENSION_WORD_TARGET_UPPER],
    }
    with open(f"{out_dir}/audit/tension_regeneration_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[3V-PERSON-VOICE-TRIAL-03] Tension圧縮再生成完了。new_word_count={new_word_count} "
          f"within_target={result['word_count_within_target']}")
    return result


NON_TENSION_KEYS_FOR_BYTE_CHECK = (
    "hook_heading", "hook_heading_level", "hook_body",
    "point_one_heading", "point_one_heading_level", "point_one_body",
    "point_two_heading", "point_two_heading_level", "point_two_body",
    "point_three_heading", "point_three_heading_level", "point_three_body",
    "tension_heading", "tension_heading_level",  # Tension見出し自体は変更しない
    "closing_heading", "closing_heading_level", "closing_body",
    "unexpected_preamble_before_first_heading",
)


def check_byte_identity_vs_trial_02(original_sections: dict, new_sections: dict) -> dict:
    per_key = {}
    all_identical = True
    for key in NON_TENSION_KEYS_FOR_BYTE_CHECK:
        identical = original_sections[key] == new_sections[key]
        per_key[key] = identical
        if not identical:
            all_identical = False
    return {"all_non_tension_sections_byte_identical": all_identical, "per_key": per_key}


def reassemble_article_with_new_tension(article_text: str, original_tension_body: str,
                                         new_tension_body: str) -> str:
    occurrences = article_text.count(original_tension_body)
    if occurrences != 1:
        raise RuntimeError(
            f"元のTension本文が記事全文中に一意に見つかりません(occurrences={occurrences})。"
            "単純文字列置換による安全な差し替えができないため中断します(STOP条件)。")
    return article_text.replace(original_tension_body, new_tension_body, 1)


def run_tension_stage() -> dict:
    if not os.path.exists(TRIAL_02_FINAL_ARTICLE_PATH):
        raise SystemExit(f"{TRIAL_02_FINAL_ARTICLE_PATH} が見つかりません(Trial-02成果物が前提)。")
    with open(TRIAL_02_FINAL_ARTICLE_PATH, encoding="utf-8") as f:
        original_article_text = f.read()
    original_sections = t02.split_six_voice_sections(original_article_text)
    if original_sections is None:
        raise SystemExit("Trial-02最終article.mdが6区切り構造を満たしていません(STOP条件)。")
    title_match_line = original_article_text.splitlines()[0]
    title = title_match_line.lstrip("#").strip()

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_3v_trial_03.jsonl")

    writer_model = routing.require_model(gen._writer_process(LABEL), routing.WRITER_MODEL)
    with cl.logging_context(THEME_ID, "tension_regeneration"):
        regen_result = regenerate_tension_only(
            client, original_sections, title, writer_model, gen.REASONING_EFFORT, OUT_DIR)

    new_article_text = reassemble_article_with_new_tension(
        original_article_text, regen_result["original_tension_body"], regen_result["new_tension_body"])
    new_article_text = gen.normalize_article_formatting(new_article_text)
    with open(f"{OUT_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(new_article_text)

    new_sections = t02.split_six_voice_sections(new_article_text)
    if new_sections is None:
        raise SystemExit("Tension差し替え後のarticle.mdが6区切り構造を満たしていません(STOP条件)。")

    byte_check_post_tension = check_byte_identity_vs_trial_02(original_sections, new_sections)
    with open(f"{OUT_DIR}/byte_identity_check_post_tension_regen.json", "w", encoding="utf-8") as f:
        json.dump(byte_check_post_tension, f, ensure_ascii=False, indent=2)
    print(f"[3V-PERSON-VOICE-TRIAL-03] Tension差し替え直後のbyte一致確認: "
          f"{byte_check_post_tension['all_non_tension_sections_byte_identical']}")

    with open(f"{OUT_DIR}/tension_stage_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "regen_result": {k: v for k, v in regen_result.items()},
            "byte_check_post_tension_regen": byte_check_post_tension,
            "original_article_path": TRIAL_02_FINAL_ARTICLE_PATH,
        }, f, ensure_ascii=False, indent=2, default=str)

    return {
        "original_article_text": original_article_text, "original_sections": original_sections,
        "article_text": new_article_text, "sections": new_sections,
        "regen_result": regen_result, "byte_check_post_tension_regen": byte_check_post_tension,
        "title": title,
    }


# ============================================================
# QA stage: Fact Checker A'(先) → Ledger Deviation+Local Rewrite(既存
# 安全装置、Trial-02と同一関数)→ Leakage Check 3V版 → Distinctness →
# Overlap monitoring → 語数/尺見積り。Trial-02のrun_voices_pattern_3v()と
# 同じ順序(Fact A'が先、Ledger Deviationが後)を踏襲する。
# ============================================================
def run_qa_and_gates_stage(tension_stage_result: dict) -> dict:
    article_text = tension_stage_result["article_text"]
    sections = tension_stage_result["sections"]
    original_sections = tension_stage_result["original_sections"]

    if not os.path.exists(t02.LEDGER_PATH):
        raise SystemExit(f"Ledger not found at {t02.LEDGER_PATH}. STOP条件(Ledger未確定)。")
    with open(t02.LEDGER_PATH, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_3v_trial_03.jsonl")
    writer_model = routing.require_model(gen._writer_process(LABEL), routing.WRITER_MODEL)

    # --- Fact Checker A'(Production関数経由、Trial-02と同一チェーン) ---
    with cl.logging_context(THEME_ID, "fact_checker_a_prime"):
        fc_record = t02.run_fact_check_a_prime_3v(article_text, verified_ledger_text, OUT_DIR)
    fact_status = fc_record.get("final_status")
    fact_verdict = (fc_record.get("result") or {}).get("verdict")

    if fact_verdict == "FAIL":
        print("[3V-PERSON-VOICE-TRIAL-03] Fact CheckerがFAIL。Tension以外への再生成・2回目のTension"
              "再生成は行わず、NG_REVIEW_REQUIREDとして結果を確定します。")
        return {
            "status": "NG_REVIEW_REQUIRED_FACT_FAIL", "article_text": article_text, "sections": sections,
            "fact_status": fact_status, "fact_verdict": fact_verdict, "fact_check_result": fc_record,
        }

    # --- Ledger Deviation Checker + Local Rewrite(既存安全装置、全文へ適用) ---
    ledger_model = routing.require_model(gen._writer_process(LABEL), routing.WRITER_MODEL)
    with cl.logging_context(THEME_ID, "ledger_deviation_and_local_rewrite"):
        ledger_result = t02.run_ledger_deviation_and_local_rewrite(
            client, THEME_ID, LABEL, article_text, verified_ledger_text, OUT_DIR, ledger_model)
    article_text = ledger_result["article_text"]
    with open(f"{OUT_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)
    sections = t02.split_six_voice_sections(article_text)

    byte_check_post_ledger = check_byte_identity_vs_trial_02(original_sections, sections)
    with open(f"{OUT_DIR}/byte_identity_check_post_ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(byte_check_post_ledger, f, ensure_ascii=False, indent=2)
    print(f"[3V-PERSON-VOICE-TRIAL-03] Ledger Deviation/Local Rewrite後のbyte一致確認: "
          f"{byte_check_post_ledger['all_non_tension_sections_byte_identical']}")

    if ledger_result["remaining_major_count"] or ledger_result["any_human_review_required"]:
        print("[3V-PERSON-VOICE-TRIAL-03] Local Rewrite cycle(既存上限3)を尽くしてもLedger MAJOR残存/"
              "human_review_required。NG_REVIEW_REQUIREDとして結果を確定します。")
        return {
            "status": "NG_REVIEW_REQUIRED_LEDGER", "article_text": article_text, "sections": sections,
            "fact_status": fact_status, "fact_verdict": fact_verdict,
            "ledger_status": ledger_result["ledger_status"],
            "ledger_deviation_count": ledger_result["ledger_deviation_count"],
            "local_rewrite_cycles": ledger_result["local_rewrite_cycles"],
            "byte_check_post_ledger_deviation": byte_check_post_ledger,
        }

    # --- Analytical Leakage Check 3V版(全section、1回のみ、retryなし) ---
    with cl.logging_context(THEME_ID, "analytical_leakage_check"):
        leakage = t02.run_analytical_leakage_check_3v(
            client, sections, writer_model, gen.REASONING_EFFORT, OUT_DIR, attempt=1)

    # --- Pairwise Voice Distinctness Check(一括[主]+有向[診断]) ---
    qa_out_dir = f"{OUT_DIR}/qa"
    os.makedirs(qa_out_dir, exist_ok=True)
    with cl.logging_context(THEME_ID, "distinctness_check"):
        distinctness = t02.run_distinctness_check_full(client, sections, qa_out_dir)

    # --- Point Overlap QA monitoring(有向9値、rule-based、¥0、記録のみ) ---
    overlap_summary = t02.run_overlap_monitoring_3v(sections, qa_out_dir)

    # --- 語数・尺見積り(Trial-02と同一のmonitoring専用関数、無変更) ---
    duration_estimate = t02.build_word_count_and_duration_estimate(sections, qa_out_dir)
    six_report = t02.six_section_length_report(article_text)

    return {
        "status": "OK", "article_text": article_text, "sections": sections,
        "fact_status": fact_status, "fact_verdict": fact_verdict, "fact_check_result": fc_record,
        "ledger_status": ledger_result["ledger_status"],
        "ledger_deviation_count": ledger_result["ledger_deviation_count"],
        "local_rewrite_cycles": ledger_result["local_rewrite_cycles"],
        "byte_check_post_ledger_deviation": byte_check_post_ledger,
        "leakage_check": leakage,
        "distinctness": {k: v for k, v in distinctness.items() if k not in ("directed_results", "batch_result")},
        "overlap_monitoring": overlap_summary,
        "duration_estimate": duration_estimate,
        "six_section_length_report": six_report,
    }


# ============================================================
# Gate 1分類(Fable指定基準):
# VALIDATED = 保持条件すべて維持(3 concrete voices/賛否構図にしない/
#   Analytical Leakage 0/Fact A' PASS/Tension外部制約統合/Voices抽象軸
#   なし/Distinctness維持)かつ尺が目標325〜355秒内または近傍。
# USER_DECISION_REQUIRED = 統合品質が崩れた、または尺が依然超過(395秒
#   許容案(a)を併記)。
# REJECTED = 上記いずれでもない重大な失敗(構造・Gate突破不能等)。
# ============================================================
def classify_gate1(qa_result: dict, tension_stage_result: dict) -> dict:
    gate_blocked = qa_result["status"] != "OK"  # Fact CheckerまたはLedger Deviation CheckerがNG
    if "leakage_check" not in qa_result:
        return {"classification": "USER_DECISION_REQUIRED", "reason": qa_result["status"],
                "details": "Fact CheckerまたはLedger Deviation Checkerでブロックされ、Leakage/"
                           "Distinctness/Durationの補助diagnosticsも実行できなかった。"}

    leakage = qa_result["leakage_check"]
    tension_item = next((x for x in leakage["flagged_items"] if x["voice"] == "tension"), None)
    tension_fail_fields = tension_item["fail_fields"] if tension_item else []
    binary_camp_split_fail = "leak_binary_camp_split" in tension_fail_fields
    constraint_integration_fail = "leak_tension_constraint_integration" in tension_fail_fields
    any_flagged = leakage["any_flagged"]

    distinctness = qa_result["distinctness"]
    direction_agreement_rate = distinctness["direction_agreement_rate"]
    method_agreement_rate = distinctness["method_agreement_rate"]
    # Trial-02実測(1.0/0.933)を下回る場合はDistinctnessが崩れた可能性ありとして扱う。
    distinctness_maintained = direction_agreement_rate >= 0.9 and method_agreement_rate >= 0.85

    fact_pass = qa_result.get("fact_verdict") != "FAIL"
    fact_review_required = qa_result.get("fact_verdict") == "REVIEW_REQUIRED"
    ledger_compliant = qa_result.get("ledger_status") == "LEDGER_COMPLIANT"
    ledger_human_review_required = bool(qa_result.get("status") == "NG_REVIEW_REQUIRED_LEDGER")
    byte_identical = (qa_result.get("byte_check_post_ledger_deviation") or {}).get(
        "all_non_tension_sections_byte_identical", True)

    duration_estimate = qa_result["duration_estimate"]["estimate"]
    estimated_seconds = duration_estimate["estimated_total_seconds_3v"] if duration_estimate else None
    within_target = duration_estimate["within_3v_target_range"] if duration_estimate else None
    near_target = (estimated_seconds is not None and 355 < estimated_seconds <= 365)  # 「近傍」の目安(+10秒以内)

    tension_word_count_within_target = tension_stage_result["regen_result"]["word_count_within_target"]

    integration_quality_maintained = (
        not any_flagged and not binary_camp_split_fail and not constraint_integration_fail
        and fact_pass and not fact_review_required and ledger_compliant
        and not ledger_human_review_required and distinctness_maintained and byte_identical
    )

    if integration_quality_maintained and (within_target or near_target):
        classification = "VALIDATED"
    elif not integration_quality_maintained:
        classification = "USER_DECISION_REQUIRED"
    elif estimated_seconds is not None and estimated_seconds > 365:
        classification = "USER_DECISION_REQUIRED"
    else:
        classification = "USER_DECISION_REQUIRED"

    return {
        "classification": classification,
        "integration_quality_maintained": integration_quality_maintained,
        "any_flagged": any_flagged, "binary_camp_split_fail": binary_camp_split_fail,
        "constraint_integration_fail": constraint_integration_fail,
        "fact_pass": fact_pass, "fact_review_required": fact_review_required,
        "ledger_compliant": ledger_compliant, "ledger_human_review_required": ledger_human_review_required,
        "distinctness_maintained": distinctness_maintained,
        "byte_identical_non_tension_sections": byte_identical,
        "tension_word_count_within_target": tension_word_count_within_target,
        "estimated_seconds": estimated_seconds, "within_target_325_355": within_target,
        "near_target_up_to_365": near_target,
        "fallback_option_a_395s_note": ("整合品質は維持されているが尺が365秒を超えて残存した場合、"
                                         "Trial-02実測395.3秒を『許容案(a)』として併記する(実装はしない、"
                                         "USER_DECISION_REQUIREDとしてユーザー判断を仰ぐ)。"),
    }


def build_diff_table_vs_trial_02(tension_stage_result: dict, qa_result: dict, gate1: dict, cost_jpy: float) -> dict:
    six = qa_result.get("six_section_length_report") or {}
    duration_estimate = qa_result.get("duration_estimate") or {}
    estimate = duration_estimate.get("estimate") or {}
    leakage = qa_result.get("leakage_check") or {}
    distinctness = qa_result.get("distinctness") or {}
    return {
        "tension_word_count": {"trial_02": 132, "trial_03": tension_stage_result["regen_result"]["new_word_count"]},
        "total_word_count_six_sections": {"trial_02": 497, "trial_03": six.get("total_of_six_sections")},
        "estimated_duration_seconds": {"trial_02": 395.3, "trial_03": estimate.get("estimated_total_seconds_3v")},
        "leak_tension_constraint_integration": {
            "trial_02": "PASS(2/2)", "trial_03": "FAIL" if gate1.get("constraint_integration_fail") else "PASS"},
        "leak_binary_camp_split": {
            "trial_02": "PASS(FAILなし)", "trial_03": "FAIL" if gate1.get("binary_camp_split_fail") else "PASS"},
        "analytical_leakage_any_flagged": {"trial_02": False, "trial_03": leakage.get("any_flagged")},
        "fact_checker_a_prime": {"trial_02": "PASS(2/2)",
                                  "trial_03": qa_result.get("fact_verdict")},
        "ledger_status": {"trial_02": "LEDGER_COMPLIANT", "trial_03": qa_result.get("ledger_status")},
        "distinctness_direction_agreement_rate": {"trial_02": 1.0,
                                                    "trial_03": distinctness.get("direction_agreement_rate")},
        "distinctness_method_agreement_rate": {"trial_02": 0.933,
                                                "trial_03": distinctness.get("method_agreement_rate")},
        "cost_jpy": {"trial_02": 20.57, "trial_03": round(cost_jpy, 2) if cost_jpy is not None else None},
        "gate1_classification": {"trial_02": "USER_DECISION_REQUIRED", "trial_03": gate1["classification"]},
    }


def compute_cost_jpy() -> dict:
    """既存pricing snapshotを用いた実測費用計算(Trial-02 cost_compute補助
    スクリプトと同一パターン、推測priceは使わない)。"""
    pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model and p["meter"] == meter)

    luna_in = price("openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = price("openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = price("openai", "gpt-5.6-luna", "output_tokens")
    usd_jpy = 155.0  # Trial-02と同一レート

    log_path = f"{OUT_DIR}/raw_usage_log_3v_trial_03.jsonl"
    if not os.path.exists(log_path):
        return {"found": False, "call_count": 0, "cost_usd": 0.0, "cost_jpy": 0.0}
    records = [json.loads(l) for l in open(log_path, encoding="utf-8") if l.strip()]
    total_usd = 0.0
    for r in records:
        if r.get("provider") != "openai":
            continue
        it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
        ct = r.get("cached_input_tokens") or 0
        billable_in = max(it - ct, 0)
        total_usd += (billable_in / 1e6) * luna_in + (ct / 1e6) * luna_cached + (ot / 1e6) * luna_out
    result = {
        "found": True, "call_count": len(records), "usd_jpy_rate": usd_jpy,
        "cost_usd": round(total_usd, 4), "cost_jpy": round(total_usd * usd_jpy, 2),
        "web_search_call_count_total": sum(r.get("web_search_call_count") or 0 for r in records),
    }
    with open(f"{OUT_DIR}/cost_compute_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


# ============================================================
# 補助ステージ(NG_REVIEW_REQUIRED_LEDGER等でrun_qa_and_gates_stage()が
# 早期returnした場合の追加実行用): Fact Checker A'・Ledger Deviation
# Checkerは既存Gate(安全装置)としての判定を変えない(再実行しない、
# 既に確定した status/ledger_status/fact_verdictをそのまま使う)。
# Leakage Check・Distinctness・Overlap monitoring・語数/尺見積りは、
# 既存Gateをbypassする判定材料ではなく追加のmonitoring/報告用情報として、
# 現在のarticle.md(Local Rewrite適用後の最終状態)に対して実行する。
# Gate 1分類はledger_status/fact_verdictを引き続き反映するため、この
# 補助ステージの実行結果によってNG判定がOKへ変わることはない。
# ============================================================
def run_remaining_diagnostics_for_reporting(qa_result: dict) -> dict:
    article_text = qa_result["article_text"]
    sections = t02.split_six_voice_sections(article_text)
    if sections is None:
        print("[3V-PERSON-VOICE-TRIAL-03][補助diagnostics] 6区切り構造が検出できないためスキップします。")
        return qa_result

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_3v_trial_03.jsonl")
    writer_model = routing.require_model(gen._writer_process(LABEL), routing.WRITER_MODEL)

    with cl.logging_context(THEME_ID, "analytical_leakage_check_supplementary"):
        leakage = t02.run_analytical_leakage_check_3v(
            client, sections, writer_model, gen.REASONING_EFFORT, OUT_DIR, attempt=1)

    qa_out_dir = f"{OUT_DIR}/qa"
    os.makedirs(qa_out_dir, exist_ok=True)
    with cl.logging_context(THEME_ID, "distinctness_check_supplementary"):
        distinctness = t02.run_distinctness_check_full(client, sections, qa_out_dir)

    overlap_summary = t02.run_overlap_monitoring_3v(sections, qa_out_dir)
    duration_estimate = t02.build_word_count_and_duration_estimate(sections, qa_out_dir)
    six_report = t02.six_section_length_report(article_text)

    qa_result = dict(qa_result)
    qa_result.update({
        "leakage_check": leakage,
        "distinctness": {k: v for k, v in distinctness.items() if k not in ("directed_results", "batch_result")},
        "overlap_monitoring": overlap_summary,
        "duration_estimate": duration_estimate,
        "six_section_length_report": six_report,
        "sections": sections,
        "note_supplementary_diagnostics": (
            "run_qa_and_gates_stage()がNG判定で早期returnしたため、Leakage/Distinctness/Overlap/"
            "Duration見積りは本補助ステージで別途実行した(Fact Checker A'・Ledger Deviation Checkerの"
            "判定自体は再実行していない、既存Gateの判定結果をそのまま使用)。"),
    })
    return qa_result


def load_state_from_prior_run() -> tuple[dict, dict]:
    """既に1回のTension再生成・Fact Checker A'・Ledger Deviation Checkerが
    完了済みの状態から、追加のTension再生成やFact/Ledger再判定を一切行わず
    (=2回目以降の再生成禁止を厳守)、summary.json・article.mdから状態を
    再構築する(`stage=finish`専用、補助diagnostics実行のみを目的とする)。"""
    with open(f"{OUT_DIR}/tension_stage_result.json", encoding="utf-8") as f:
        tsr_raw = json.load(f)
    with open(f"{OUT_DIR}/summary.json", encoding="utf-8") as f:
        prior_summary = json.load(f)
    with open(f"{OUT_DIR}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    tension_stage_result = {"regen_result": tsr_raw["regen_result"],
                             "byte_check_post_tension_regen": tsr_raw["byte_check_post_tension_regen"]}
    qa_result = {
        "status": prior_summary["qa_status"], "article_text": article_text,
        "fact_verdict": prior_summary.get("fact_verdict"), "ledger_status": prior_summary.get("ledger_status"),
        "byte_check_post_ledger_deviation": prior_summary.get("byte_check_post_ledger_deviation"),
    }
    return tension_stage_result, qa_result


def main() -> None:
    t0 = time.time()
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "finish":
        tension_stage_result, qa_result = load_state_from_prior_run()
    else:
        tension_stage_result = run_tension_stage()
        qa_result = run_qa_and_gates_stage(tension_stage_result)
    if qa_result["status"] != "OK" and qa_result.get("article_text") and "leakage_check" not in qa_result:
        qa_result = run_remaining_diagnostics_for_reporting(qa_result)
    gate1 = classify_gate1(qa_result, tension_stage_result)
    cost_result = compute_cost_jpy()
    diff_table = build_diff_table_vs_trial_02(
        tension_stage_result, qa_result, gate1, cost_result.get("cost_jpy"))

    summary = {
        "theme_id": THEME_ID,
        "tension_regen": tension_stage_result["regen_result"],
        "byte_check_post_tension_regen": tension_stage_result["byte_check_post_tension_regen"],
        "qa_status": qa_result["status"],
        "byte_check_post_ledger_deviation": qa_result.get("byte_check_post_ledger_deviation"),
        "fact_verdict": qa_result.get("fact_verdict"),
        "ledger_status": qa_result.get("ledger_status"),
        "leakage_any_flagged": (qa_result.get("leakage_check") or {}).get("any_flagged"),
        "distinctness": qa_result.get("distinctness"),
        "duration_estimate": qa_result.get("duration_estimate"),
        "six_section_length_report": qa_result.get("six_section_length_report"),
        "gate1": gate1,
        "diff_table_vs_trial_02": diff_table,
        "cost": cost_result,
        "elapsed_seconds": round(time.time() - t0, 1),
    }
    with open(f"{OUT_DIR}/summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[3V-PERSON-VOICE-TRIAL-03] 完了。qa_status={qa_result['status']} "
          f"gate1_classification={gate1['classification']} cost_jpy={cost_result.get('cost_jpy')}")


if __name__ == "__main__":
    main()
