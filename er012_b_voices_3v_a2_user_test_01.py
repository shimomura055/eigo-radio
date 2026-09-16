# ============================================================
# er012_b_voices_3v_a2_user_test_01.py
# 管理ID: USER-TEST-VOICES-A2-MINIMAL-01
# ============================================================
# ユーザー実検証用A2 artifactを最小Token・最小APIコストで作成するTrial
# driver(Priority 1が主対象)。Productionコード(er012_b_family_*_
# production_*.py / er012_b_family_production_runner_01.py / er003_*)は
# 一切改修しない。既存Production primitiveをimportして呼ぶだけ。
#
# Priority 1: B/Voices 3V「AI hiring」既存B1「When AI Sits Between a Job
# and a Person」からA2記事を翻案し、音声・Audio Validation・playerまで
# 完成させる(既存2V A2翻案原則を3V構造へ最小適用するTrial artifact
# 生成、3V A2の正式仕様化・Production wiringは行わない)。
#
# 構造非互換で2V専用のまま使えないもの(driverでのみ代替実装、Production
# 関数自体は無変更のまま温存):
#   - build_adapt_prompt/B_FAMILY_A2_TASK_INSTRUCTIONS(a2prod、2V=5見出し
#     hardcode) → 本ファイルのbuild_adapt_prompt_3v/
#     B_FAMILY_A2_TASK_INSTRUCTIONS_3V(3V=6見出しへ最小書き換え、他の
#     引用原則[A2_KAI1_INSTRUCTION_PARA1_PARA3/CORE_EXPLANATORY_LOGIC_
#     PRESERVATION/A2_TABLE_PRINCIPLES_JA]はa2prodから無変更のままimport)
#   - run_evidence_compression(a2prod、出力形式指示が2V=5見出し
#     hardcode) → 3Vでは構造破壊リスクがあるため実行しない(委任文
#     「既存経路で必須なら」の条件付き文言に基づき、必須ではないと判断)
#   - run_five_section_point_qa_monitoring/run_analytical_leakage_check
#     (a2prod、sections["voice_a_body"]/["voice_b_body"]と2V専用key名を
#     hardcode) → 非適用。代替としてrun_structure_check_3v()
#     (build_parts_3vの6区切り抽出+b1prod.run_content_integrity_check_3v
#     を使った3V構造チェック、3V B1のrequired_structure_3vと同種の検証)
#   - run_scaffold_a2(a2prod、point_one/two・tension_heading等2V専用key
#     参照) → 本ファイルのrun_scaffold_a2_3v(registry.COMMENT_ROLES/
#     a2gen.run_support_text/a2gen.PREVIEW_ROLEは無変更のままimport、
#     contextにVoice 3を追加しただけ)
#   - build_a2_voices_timeline/row_info_a2(a2prod、Voice A/Bのみ2V
#     hardcode) → 本ファイルのbuild_a2_voices_timeline_3v/row_info_a2_3v
#     (asm.build_b1_key_phrase_blocks/pause定数等は無変更のままimport、
#     B1 3V timeline[build_b1_voices_timeline_3v]のVoice C挿入パターンを
#     A2へ適用)
#   - load_a2_sources_for_b_family(a2prod、point_one/point_two名前で
#     2V専用hardcode) → 本ファイルのload_a2_sources_3v
#     (load_b1_sources_3vのsegment一覧パターンをA2ファイル名規約へ適用)
#   - check_required_segments_completeness/registry.B_FAMILY_A2_
#     JAPANESE_TITLES(registry改修回避のため、driverローカル定義で代替。
#     registry.py自体は一切変更していない)
#
# そのまま無変更でimportして使うProduction primitive: run_writer_adapt
# の下位API呼び出しパターン(client.responses.create)、run_fact_checker、
# run_ledger_deviation、generate_voice_body_wide_margin_with_a2_slowdown、
# reuse_key_phrases_a2、generate_a2_japanese_with_reading_safety、
# generate_a2_segment_with_slowdown、voice01.generate_charon_english、
# shared_narration.ensure_all_shared_narration_a2、b1prod.build_parts_3v、
# b1prod.run_content_integrity_check_3v、asm.apply_b1_gain、
# asm.assemble_with_timeline、asm.apply_headroom_safety_valve、
# asm.verify_episode_audio_validation_gate、runner.
# build_fact_attribution_block_if_enabled、runner.compute_cost_jpy_so_far。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re

import audio_review_player as player_common
import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_model_routing_contract_01 as routing
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_production_runner_01 as runner
import er012_b_family_voices_a2_production_01 as a2prod
import er012_b_family_voices_production_01 as b1prod

# ============================================================
# 固定入力(Priority 1: AI hiring 3V、変更禁止)
# ============================================================
ARTICLE_PATH_3V = ("er012_output/editorial_b_voices_3v_person_voice_trial_02/"
                    "b1b_run01_attempt2/article.md")
LEDGER_PATH_3V = "er012_output/ai_screening_ledger_trial_01/research/verified_fact_ledger.txt"
KP_SOURCE_DIR_3V = "er012_output/editorial_b_voices_3v_audio_trial_01/b1b"
VOICE_A_3V = "Algieba"
VOICE_B_3V = "Erinome"
VOICE_C_3V = "Schedar"

# TOPIC_JA: er012_editorial_b_voices_3v_person_voice_trial_02.py L146-163から
# 全文転記(Trialスクリプトはimportせず、テキスト定数のみ複製。同一Ledger・
# 同一テーマのFact Checker用テーマ説明、新しい主張・数字は含まない)。
TOPIC_JA_3V = (
    "2026年9月時点、多くの企業が採用選考の一部にAI(応募書類の自動スクリーニング、"
    "適性・性格の自動スコアリング、動画面接での表情・話し方の自動評価など)を"
    "取り入れつつある。この記事の中心テーマは、『企業は採用選考にAIを使うべきか』"
    "の賛否をどちらか一つに決めることではなく、この同じ状況について、全く異なる"
    "利害・責任・経験を持つ3人—実際にAIによって評価される応募者(Applicant)、"
    "実際にAIツールを業務で使う採用担当・人事責任者(Recruiter・Hiring Manager)、"
    "そして採用にかかるコスト・速度・会社の存続そのものに個人として責任を負う"
    "経営者(Business Owner)—が、それぞれ何を経験し、何を大切にし、何を心配し、"
    "何を守ろうとしているのかを、実在する調査・訴訟・事例に基づいて具体的に描く"
    "ことである。そのうえで、この3人の合理性を単純に足しても答えにはならない"
    "ことも示す。3人の外側には、応募者が不当に差別されていないかを監査・法規制"
    "を通じて事後に検証する仕組み(バイアス監査義務・AIの高リスク分類・過去の"
    "訴訟事例など)が既に存在しており、これが3人それぞれの選択肢を現実に制約"
    "している。この記事のねらいは、なぜ同じ状況が、それぞれが背負っているものに"
    "よって全く違う重みで見えるのか、そしてなぜ3人の言い分をただ足し合わせるだけ"
    "では答えが出ないのかを理解することである。"
)

# 日本語タイトル(registry.B_FAMILY_A2_JAPANESE_TITLESへの新規登録は
# registry.py[Production設定]の改修になるため行わず、driverローカル定数と
# する。タイトル本文[英語、# 見出し]は入力B1と一字一句同じものを翻案でも
# 維持する規約のため、ここでは音声化用の日本語直訳のみを人手で用意する
# [新しい主張・数字の追加ではない])。
JAPANESE_TITLE_3V = "AIが仕事と人の間に立つとき"

OUT_DIR = "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2"
A2_DIR = f"{OUT_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
KP_DIR = f"{A2_DIR}/key_phrases"
AUDIT_DIR = f"{A2_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"
EPISODE_BASENAME = "AI_Hiring_3V_A2_User_Test_01.wav"
AUDIO_GATE_LEVEL = registry.get_editorial_type_a2()["audio_gate_level"]  # "B_FAMILY_A2"(既存registry読み取りのみ)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def assert_budget_ok(budget_jpy_cap: float, note: str = "") -> float:
    jpy, by_provider = runner.compute_cost_jpy_so_far(COST_LOG_PATH)
    print(f"[USER-TEST-3V-A2][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > budget_jpy_cap:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {budget_jpy_cap} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# Stage 1: 記事翻案(Writer)+Validator群(3V構造対応)
# ============================================================
# 2V専用B_FAMILY_A2_TASK_INSTRUCTIONS(a2prod、5見出しhardcode)を、3V
# (6見出し)構造へ最小書き換えしたもの。他の引用原則(A2_KAI1_INSTRUCTION_
# PARA1_PARA3/CORE_EXPLANATORY_LOGIC_PRESERVATION/A2_TABLE_PRINCIPLES_JA)
# はa2prodから無変更のままそのまま使う(下記build_adapt_prompt_3v参照)。
B_FAMILY_A2_TASK_INSTRUCTIONS_3V = """【本Trial専用の作業指示(2V A2翻案原則[ユーザー決定B-A2-1/B-A2-2/
B-A2-4/B-A2-5、2026-09-08承認]を3V構造へ最小適用、USER-TEST-VOICES-A2-
MINIMAL-01)】
これは新規記事の生成ではありません。以下に示す、承認済みのB1(CEFR-B1相当)記事本文を、
「同一人物・同一立場のまま」CEFR-A2レベルへ翻案(簡略化リライト)する作業です。

- 記事の物理構造(Markdown見出し6個: `## `見出し1つ→`### `見出し3つ→`## `見出し2つ、
  この順序・見出しレベルを厳守)は、入力と完全に同じ構成のまま維持してください。11パート構造への
  組み替えは行わないでください。
- タイトル(`# `見出し)は入力と一字一句同じものをそのまま使ってください。
- 一人称"I"による語り口は、3つの###見出し(Voice 1・Voice 2・Voice 3)すべてで維持してください。
- 3人の人物(Voice 1/2/3)の立場・価値観・具体的な経験・結論は、入力と完全に同じ
  内容を保ってください。新しいFact・新しい経験・新しい数字を追加しないでください。
- Tension(5つ目の見出し)・Closing(6つ目の見出し)も、入力と同じ役割・同じ結論を保ったまま
  A2レベルへ翻案してください(分量は入力とおおむね同じ比率を保つ)。
- 見出し文言自体は、内容が伝わる範囲で平易な言い方へ変えてよいですが、3つの###見出しには、
  「ここから別の人物の話が始まる」と分かる表現を必ず含めてください。

【出力形式】
入力と全く同じMarkdown構造(`# `Title、`## `見出し1つ、`### `見出し3つ、`## `見出し2つ、
合計6つの##/###見出し)で、翻案後の記事全文だけを出力してください。説明文やコメントは
付けないでください。"""


def build_adapt_prompt_3v(b1_article_text: str) -> str:
    return (
        B_FAMILY_A2_TASK_INSTRUCTIONS_3V
        + "\n\n【A2言語原則(CURRENT_SPEC.md CEFR-A2節からの引用)】\n"
        + a2prod.A2_KAI1_INSTRUCTION_PARA1_PARA3
        + "\n\n【Core Explanatory Logic Preservation(CURRENT_SPEC.md L266からの引用)】\n"
        + a2prod.CORE_EXPLANATORY_LOGIC_PRESERVATION
        + "\n\n" + a2prod.A2_TABLE_PRINCIPLES_JA
        + "\n\n【翻案対象のB1記事本文(そのまま、そっくりコピーしないでA2へ翻案すること)】\n"
        + b1_article_text
    )


def run_writer_adapt_3v(client, b1_article_text: str, model: str, reasoning_effort: str = "high") -> dict:
    """a2prod.run_writer_adapt()と同一の呼び出しパターン(client.responses.
    create、developer+userメッセージ)だが、promptだけbuild_adapt_prompt_3v
    (3V用)で組み立てる(a2prod.run_writer_adapt()自体はpromptを内部で
    2V用build_adapt_prompt()に固定しているため、そのままでは3Vへ使えない)。"""
    prompt = build_adapt_prompt_3v(b1_article_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "developer", "content": "指定されたB1記事本文をA2レベルへ翻案してください。"},
            {"role": "user", "content": prompt},
        ],
    )
    text = (response.output_text or "").strip()
    if not text:
        raise RuntimeError("[USER-TEST-3V-A2][Writer] A2翻案応答が空です")
    return {"status": "OK", "text": text, "model": response.model, "response_id": response.id,
            "prompt": prompt, "reasoning_effort": reasoning_effort}


def run_structure_check_3v(article_text: str, parts: dict, kp_merged: dict) -> dict:
    """2V専用run_five_section_point_qa_monitoring/run_analytical_leakage_
    check(sections["voice_a_body"]/["voice_b_body"]を2V専用keyでhardcode)
    は3V(6見出し、voice_1/2/3)には構造上使えないため非適用。代替として、
    (a) build_parts_3v()による6区切り抽出が全section非空で成功したこと、
    (b) b1prod.run_content_integrity_check_3v()(Production、無変更)による
    3人の本文・Tension・Closingの逐語抽出一致、の2点を検証する(3V B1の
    audit/required_structure_3v.jsonと同種の構造チェック)。"""
    six = parts.get("_six_section_headings") or {}
    presence_checks = {
        "voice_1_heading": bool(parts.get("point_one_heading")),
        "voice_1_body": bool(parts.get("point_one_body")),
        "voice_2_heading": bool(parts.get("point_two_heading")),
        "voice_2_body": bool(parts.get("point_two_body")),
        "voice_3_heading": bool(parts.get("point_three_heading")),
        "voice_3_body": bool(parts.get("point_three_body")),
        "tension_heading": bool(parts.get("tension_heading")),
        "tension_body": bool(parts.get("tension_body")),
        "in_one_line": bool(parts.get("in_one_line")),
        "six_headings_extracted": len(six) == 6,
    }
    integrity = b1prod.run_content_integrity_check_3v(article_text, parts, kp_merged)
    all_ok = all(presence_checks.values()) and integrity["all_section_bodies_verbatim_from_article"]
    return {
        "status": "OK" if all_ok else "NG",
        "presence_checks": presence_checks,
        "content_integrity_check_3v": integrity,
        "note": ("2V専用run_five_section_point_qa_monitoring/run_analytical_leakage_checkは"
                 "section名hardcode(voice_a_body/voice_b_body等)のため3V(6見出し)に非適用。"
                 "代替として3V6区切り構造チェック(build_parts_3v成功+3人の本文/Tension/Closing"
                 "の逐語抽出一致)を実施した。"),
    }


def detect_new_numbers(b1_article_text: str, a2_article_text: str) -> list:
    nb = set(re.findall(r"\d[\d,.%]*", b1_article_text))
    na = set(re.findall(r"\d[\d,.%]*", a2_article_text))
    return sorted(na - nb)


def run_scaffold_a2_3v(parts: dict, article_text: str, ledger_text: str) -> dict:
    """a2prod.run_scaffold_a2()(2V専用、point_one/two・tension_heading等の
    2V専用key参照)の3V版。registry.COMMENT_ROLES(役割定義そのもの、Voice数
    非依存へ既に一般化済み)・a2gen.run_support_text/PREVIEW_ROLEは無変更の
    まま使い、contextにVoice 3を追加しただけ。"""
    client = a2gen.get_client()
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    comment_roles = registry.get_editorial_type("b_family_voices")["comment_roles"]

    c1_context = f"【これから聞く本文(The Question)】\n{parts['part1']}\n{parts['part2']}"
    c1 = a2gen.run_support_text(client, comment_roles["comment_1"], c1_context, model=model)

    c2_context = (f"【すでに聞いた本文(The Question)】\n{parts['part1']}\n{parts['part2']}\n\n"
                  f"【これから聞く声の見出しのみ(内容は伏せる、この時点でこの文言を言わないこと)】\n"
                  f"Voice 1 heading: {parts['point_one_heading']}\n"
                  f"Voice 2 heading: {parts['point_two_heading']}\n"
                  f"Voice 3 heading: {parts['point_three_heading']}")
    c2 = a2gen.run_support_text(client, comment_roles["comment_2"], c2_context, model=model)

    c3_context = (f"【Voice 1(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Voice 2(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                  f"【Voice 3(聞き終えた内容)】\n{parts['point_three_heading']}\n{parts['point_three_body']}\n\n"
                  f"【これから聞く内容の見出しのみ(内容は伏せる)】\n{parts['tension_heading']}")
    c3 = a2gen.run_support_text(client, comment_roles["comment_3"], c3_context, model=model)

    c4_context = (f"【聞き終えた内容(視点の違いの深掘り)】\n{parts['tension_body']}\n\n"
                  f"【これから聞く結びの見出しのみ(内容は伏せる)】\nClosing")
    c4 = a2gen.run_support_text(client, comment_roles["comment_4"], c4_context, model=model)

    preview_role = a2gen.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = a2gen.run_support_text(client, preview_role, preview_context, model=model)

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(AUDIT_DIR, exist_ok=True)
    save_json(f"{A2_DIR}/a2_support_texts.json", {k: v.get("text") for k, v in results.items()})
    save_json(f"{AUDIT_DIR}/a2_support_generation.json", results)

    support_concat = "\n\n".join(t for t in (v.get("text") for v in results.values()) if t)
    import er003_v1_en_direct_vfl_01_generate as vfl01
    deviation = vfl01.run_deviation_check(client, ledger_text, support_concat)
    save_json(f"{AUDIT_DIR}/support_ledger_deviation.json", deviation["parsed"])

    return {"support": results, "support_status": {k: v.get("status") for k, v in results.items()},
            "deviation": deviation["parsed"]}


def stage_article(budget_jpy_cap: float) -> dict:
    os.makedirs(AUDIT_DIR, exist_ok=True)
    cl.install(COST_LOG_PATH)

    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    writer_model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)

    b1_article_text = load_text(ARTICLE_PATH_3V)
    ledger_text = load_text(LEDGER_PATH_3V)

    print("[USER-TEST-3V-A2][Writer] A2翻案(3V) 開始...")
    writer_result = run_writer_adapt_3v(client, b1_article_text, writer_model)
    with open(f"{AUDIT_DIR}/writer_prompt.txt", "w", encoding="utf-8") as f:
        f.write(writer_result["prompt"])
    save_json(f"{AUDIT_DIR}/writer_result.json", {k: v for k, v in writer_result.items() if k != "prompt"})
    article_text = writer_result["text"]
    assert_budget_ok(budget_jpy_cap, "after Writer")

    try:
        parts = b1prod.build_parts_3v(article_text)
    except RuntimeError as e:
        save_json(f"{AUDIT_DIR}/structure_check_failed.json", {"article_text": article_text, "error": str(e)})
        raise RuntimeError(f"[STRUCTURE_MISMATCH] Writer出力が6区切り構造(3V)として解析できません: {e}")

    with open(f"{A2_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)
    save_json(f"{A2_DIR}/parts.json", parts)

    print("[USER-TEST-3V-A2] Evidence Compressionは3V(6見出し)構造と2V専用出力形式指示"
          "(a2prod._B_FAMILY_STRUCTURE_OUTPUT_FORMAT)の不整合リスクのため実行しない"
          "(委任文の「既存経路で必須なら」の条件付き文言に基づく判断、Writer出力をそのまま採用)。")

    print("[USER-TEST-3V-A2][Fact Checker] 開始(Web検索あり、voice attribution block付き)...")
    fc_block = runner.build_fact_attribution_block_if_enabled(ledger_text)
    fc_result = a2prod.run_fact_checker(TOPIC_JA_3V, article_text, voice_attribution_block=fc_block)
    save_json(f"{AUDIT_DIR}/fact_check.json", fc_result)
    print(f"[USER-TEST-3V-A2][Fact Checker] final_status={fc_result['final_status']} "
          f"verdict={(fc_result['result'] or {}).get('verdict')}")
    assert_budget_ok(budget_jpy_cap, "after Fact Checker")

    print("[USER-TEST-3V-A2][Ledger Deviation] 開始(monitoring専用)...")
    deviation = a2prod.run_ledger_deviation(client, ledger_text, article_text, writer_model)
    save_json(f"{AUDIT_DIR}/ledger_deviation.json", deviation)
    print(f"[USER-TEST-3V-A2][Ledger Deviation] overall_status={deviation.get('overall_status')} "
          f"deviations={len(deviation.get('deviations', []))}")

    print("[USER-TEST-3V-A2][QA] Key Phrase reuse(3V B1 Audio Trial-01選定を再利用、新規選定なし)...")
    kp = a2prod.reuse_key_phrases_a2(KP_SOURCE_DIR_3V, KP_DIR, NARRATION_DIR)
    save_json(f"{AUDIT_DIR}/kp_tts_results.json", kp)
    kp_merged = load_json(f"{KP_DIR}/keywords_canonicalized.json")
    assert_budget_ok(budget_jpy_cap, "after Key Phrase reuse")

    print("[USER-TEST-3V-A2][QA] 3V構造チェック(2V専用QAの代替)...")
    structure_check = run_structure_check_3v(article_text, parts, kp_merged)
    save_json(f"{AUDIT_DIR}/structure_check_3v.json", structure_check)
    if structure_check["status"] != "OK":
        raise RuntimeError(f"[3V_STRUCTURE_CHECK_FAILED] {structure_check}")

    new_numbers = detect_new_numbers(b1_article_text, article_text)
    save_json(f"{AUDIT_DIR}/new_numbers_check.json", {"new_numbers": new_numbers})
    print(f"[USER-TEST-3V-A2] NEW_NUMBERS={new_numbers}")

    print("[USER-TEST-3V-A2][Scaffold] Comment 1-4・Preview(日本語、3V context)...")
    scaffold = run_scaffold_a2_3v(parts, article_text, ledger_text)
    assert_budget_ok(budget_jpy_cap, "after Scaffold")

    print("[USER-TEST-3V-A2][Title] 日本語タイトル生成...")
    title_result = n3_tts.generate_a2_japanese_with_reading_safety(
        JAPANESE_TITLE_3V, f"{NARRATION_DIR}/japanese_title.wav",
        n3_tts.expected_substring_ja(JAPANESE_TITLE_3V), max_extra_chars=30)
    title_result["canonical_text"] = JAPANESE_TITLE_3V
    save_json(f"{AUDIT_DIR}/japanese_title_generation.json", title_result)
    assert_budget_ok(budget_jpy_cap, "after Japanese title")

    summary = {
        "b1_article_path": ARTICLE_PATH_3V,
        "writer_model": writer_result["model"],
        "word_count_a2": sum(len(re.findall(r"[A-Za-z']+", parts[k])) for k in
                              ("part1", "part2", "point_one_body", "point_two_body", "point_three_body",
                               "tension_body", "in_one_line")),
        "fact_check_final_status": fc_result["final_status"],
        "fact_check_verdict": (fc_result["result"] or {}).get("verdict"),
        "ledger_deviation_overall_status": deviation.get("overall_status"),
        "ledger_deviation_count": len(deviation.get("deviations", [])),
        "structure_check_status": structure_check["status"],
        "new_numbers": new_numbers,
        "scaffold_support_status": scaffold["support_status"],
        "scaffold_deviation_overall_status": scaffold["deviation"].get("overall_status"),
        "voice_a": VOICE_A_3V, "voice_b": VOICE_B_3V, "voice_c": VOICE_C_3V,
        "title": parts["title"], "japanese_title": JAPANESE_TITLE_3V,
    }
    save_json(f"{A2_DIR}/article_stage_summary.json", summary)
    print(f"[USER-TEST-3V-A2] Article stage完了。summary={summary}")
    return summary


# ============================================================
# Stage 2: 音声化(TTS)+Assembly+Gate+player
# ============================================================
def run_tts_3v_a2(parts: dict, support_texts: dict, budget_jpy_cap: float) -> dict:
    results = {}

    topic_intro_text = f"Today's topic is {parts['title']}."
    print("[USER-TEST-3V-A2][TTS] topic_intro生成(Charon)...")
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = voice01.generate_charon_english(
            n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_text)),
            f"{NARRATION_DIR}/topic_intro.wav")
    results["topic_intro"]["canonical_text"] = topic_intro_text
    assert_budget_ok(budget_jpy_cap, "after topic_intro")

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support_texts[name]
        print(f"[USER-TEST-3V-A2][TTS] {name}生成(Aoede日本語)...")
        with cl.segment_context(name):
            results[name] = n3_tts.generate_a2_japanese_with_reading_safety(
                text, f"{NARRATION_DIR}/{name}.wav", n3_tts.expected_substring_ja(text))
        results[name]["canonical_text"] = text
    assert_budget_ok(budget_jpy_cap, "after preview/comment TTS")

    for name in ("point_one_heading", "point_two_heading", "point_three_heading"):
        text = parts[name]
        sc.assert_no_point_number_label(text, name)
        tts_input = n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text))
        print(f"[USER-TEST-3V-A2][TTS] {name}生成(Aoede英語、A2 slowdown)...")
        with cl.segment_context(name):
            results[name] = n3_tts.generate_a2_segment_with_slowdown(
                tts_input, f"{NARRATION_DIR}/{name}.wav", n3_tts.first_words(text, 3), max_extra_chars=20,
                style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER, disfluency_qa=True)
        results[name]["canonical_text"] = text
    assert_budget_ok(budget_jpy_cap, "after Narrator heading TTS")

    for name, text, voice_name in (
        ("point_one", parts["point_one_body"], VOICE_A_3V),
        ("point_two", parts["point_two_body"], VOICE_B_3V),
        ("point_three", parts["point_three_body"], VOICE_C_3V),
    ):
        sc.assert_no_point_number_label(text, name)
        print(f"[USER-TEST-3V-A2][TTS] {name}生成({voice_name}、A2 slowdown)...")
        with cl.segment_context(name):
            results[name] = a2prod.generate_voice_body_wide_margin_with_a2_slowdown(
                name, n3_tts.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav", voice_name)
        results[name]["canonical_text"] = text
    assert_budget_ok(budget_jpy_cap, "after Voice A/B/C TTS")

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        (b1prod.EXTRA_SEGMENT_NAME, parts["tension_body"]), ("in_one_line", parts["in_one_line"]),
    ):
        tts_input = n3_tts.tts_safe_news_en(text)
        print(f"[USER-TEST-3V-A2][TTS] {name}生成(Aoede英語、A2 slowdown)...")
        with cl.segment_context(name):
            results[name] = n3_tts.generate_a2_segment_with_slowdown(
                tts_input, f"{NARRATION_DIR}/{name}.wav", n3_tts.first_words(text),
                style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                disfluency_qa=(name == "in_one_line"),
                enable_connected_speech_equivalence_layer=(name in ("full_story_part1", "full_story_part2")),
                enable_repetition_qa=(name in ("full_story_part1", "full_story_part2")))
        results[name]["canonical_text"] = text
    assert_budget_ok(budget_jpy_cap, "after Hook/Tension/Closing TTS")

    print("[USER-TEST-3V-A2][TTS] 共通固定narration(welcome/preview_intro/key_phrases_intro/"
          "full_story_intro/num_one-five)をMaster Audio Store経由でreuse...")
    shared_narration.ensure_all_shared_narration_a2(NARRATION_DIR)
    assert_budget_ok(budget_jpy_cap, "after shared narration reuse")

    return results


def finalize_tts_results_3v_a2(new_results: dict, kp_merged: dict) -> dict:
    segments = dict(new_results)
    # japanese_titleは既にstage_articleで生成済み(audit/japanese_title_generation.json)。
    title_entry = load_json(f"{AUDIT_DIR}/japanese_title_generation.json")
    segments["japanese_title"] = title_entry

    # 実際のKey Phrase TTS結果(status/sha256等を含む、reuse_key_phrases_a2()の
    # 戻り値をstage_articleがaudit/kp_tts_results.jsonへ保存済み)を読み込み、
    # そのまま使う(pathのみのダミーdictではGate側のstatus検証を通過できない)。
    kp_tts_results = load_json(f"{AUDIT_DIR}/kp_tts_results.json")
    key_phrases = {str(rank): entry for rank, entry in kp_tts_results.items()}

    data = {"segments": segments, "key_phrases": key_phrases}
    save_json(f"{AUDIT_DIR}/tts_generation_results.json", data)
    all_status = {k: v.get("status") for k, v in segments.items()}
    save_json(f"{A2_DIR}/run_summary_tts.json", {"segment_status": all_status})

    required_names = (
        "topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
        "point_one_heading", "point_two_heading", "point_three_heading", "point_one", "point_two", "point_three",
        "full_story_part1", "full_story_part2", b1prod.EXTRA_SEGMENT_NAME, "in_one_line",
    )
    missing = [n for n in required_names if all_status.get(n) != "OK"]
    completeness = {
        "expected_segment_count": len(required_names), "actual_present_count": len(required_names) - len(missing),
        "missing_or_not_ok": missing, "complete": not missing,
        "voice_a": VOICE_A_3V, "voice_b": VOICE_B_3V, "voice_c": VOICE_C_3V,
    }
    save_json(f"{AUDIT_DIR}/required_segments_completeness.json", completeness)
    print(f"[USER-TEST-3V-A2] TTS完了。segment_status={all_status}")
    print(f"[USER-TEST-3V-A2] 3V required segments completeness: {completeness}")
    return data


# ============================================================
# Assembly: 3V用ローダー+timeline builder(a2prod.load_a2_sources_for_
# b_family/build_a2_voices_timelineの3V拡張、driverローカル実装)
# ============================================================
def load_a2_sources_3v(kp: dict, a2_dir: str, narration_dir: str, audio_gate_level: str) -> dict:
    asm.verify_episode_audio_validation_gate(a2_dir, audio_gate_level)

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    point_notification = p9a.load_and_resample_to_target(asm.POINT_NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("num_one", "num_two", "num_three", "num_four", "num_five"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/topic_intro.wav")
    assert sr == common.SAMPLE_RATE
    narration["topic_intro"] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/japanese_title.wav")
    assert sr == common.SAMPLE_RATE
    narration["japanese_title"] = mono

    b1_segments = {}
    for name in ("full_story_part1", "full_story_part2", "point_one", "point_two", "point_three",
                  b1prod.EXTRA_SEGMENT_NAME, "in_one_line",
                  "comment_1", "comment_2", "comment_3", "comment_4", "preview",
                  "point_one_heading", "point_two_heading", "point_three_heading"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono

    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    key_phrase_components, key_phrase_meanings = {}, {}
    for item in kp_items:
        rank = item["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_en.wav")
        assert sr == common.SAMPLE_RATE
        key_phrase_components[rank] = mono
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_ja_aoede.wav")
        assert sr == common.SAMPLE_RATE
        key_phrase_meanings[rank] = mono

    return {"intro": intro, "notification": notification, "point_notification": point_notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments,
            "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings,
            "kp_items": kp_items}


def build_a2_voices_timeline_3v(parts: dict, voice_a: str, voice_b: str, voice_c: str) -> list:
    """a2prod.build_a2_voices_timeline()(2V、Voice A/Bのみ)に、B1 3V
    timeline(b1prod.build_b1_voices_timeline_3v())と同一パターンのVoice C
    ブロック(Point Notification+heading+body)を1段追加した3V版。Pause秒数
    はasm.*_PAUSE_SECONDS定数(既存、無変更)をそのまま流用する。"""
    key_phrase_blocks = asm.build_b1_key_phrase_blocks(parts)
    b1 = parts["b1_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome (Charon)", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro (Charon)", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Japanese title (Aoede, Japanese, A2)", parts["japanese_title"]),
        ("pause_0.5_title", p9a.silence_stereo(0.5)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro (Charon)", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Preview (Aoede, Japanese, A2)", b1["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro (Charon)", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i}" for i in range(1, len(key_phrase_blocks) + 1))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro (Charon)", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 1 (Aoede, Japanese, A2)", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Hook Part 1: The Question (Aoede, English, A2 slowdown, no heading)", b1["full_story_part1"]),
        ("pause_0.25_hook_internal", p9a.silence_stereo(0.25)),
        ("Hook Part 2: The Question (Aoede, English, A2 slowdown, no heading)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Aoede, Japanese, A2, bridge to Voices)", b1["comment_2"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice 1 cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Voice 1 heading (Aoede, English, A2 slowdown)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice 1 body ({voice_a}, A2 slowdown)", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice 2 cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Voice 2 heading (Aoede, English, A2 slowdown)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice 2 body ({voice_b}, A2 slowdown)", b1["point_two"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice 3 cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Voice 3 heading (Aoede, English, A2 slowdown)", b1["point_three_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice 3 body ({voice_c}, A2 slowdown)", b1["point_three"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Aoede, Japanese, A2)", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Tension: Why They See It Differently (Aoede, English, A2 slowdown, no heading)",
         b1[b1prod.EXTRA_SEGMENT_NAME]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Aoede, Japanese, A2)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Closing: What This Question Really Means (Aoede, English, A2 slowdown, no heading, In One Line)",
         b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


def run_assembly_3v_a2() -> dict:
    os.makedirs(f"{A2_DIR}/assembled", exist_ok=True)
    kp = load_json(f"{KP_DIR}/keywords_canonicalized.json")

    try:
        sources = load_a2_sources_3v(kp, A2_DIR, NARRATION_DIR, AUDIO_GATE_LEVEL)
    except RuntimeError as e:
        print(f"[USER-TEST-3V-A2] Assembly GATE_BLOCKED(override無し、報告のみ): {e}")
        summary = {"status": "GATE_BLOCKED", "error": str(e)}
        save_json(f"{A2_DIR}/run_summary_assemble.json", summary)
        return summary

    parts = asm.apply_b1_gain(sources)
    seq = build_a2_voices_timeline_3v(parts, VOICE_A_3V, VOICE_B_3V, VOICE_C_3V)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    out_path = f"{A2_DIR}/assembled/{EPISODE_BASENAME}"
    save_json(f"{AUDIT_DIR}/gain_report.json", parts["gain_report"])
    save_json(f"{AUDIT_DIR}/timeline.json", result["timeline"])
    save_json(f"{AUDIT_DIR}/headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
        "voice_a": VOICE_A_3V, "voice_b": VOICE_B_3V, "voice_c": VOICE_C_3V,
    }
    save_json(f"{A2_DIR}/run_summary_assemble.json", summary)
    print(f"[USER-TEST-3V-A2] Assembly status={summary['status']} duration={summary['duration_seconds']} "
          f"peak={summary['peak']} clipping={summary['clipping_detected']}")
    return summary


def row_info_a2_3v(label: str, parts: dict, support_texts: dict, kp_by_rank: dict, narration_dir: str) -> dict:
    """a2prod.row_info_a2()(2V、Voice A/Bのみ)の3V拡張。ラベル文字列は
    build_a2_voices_timeline_3v()のものと1対1で対応させてある。"""
    charon = "Charon"
    if label == "Intro":
        return {"text": "音楽ジングル(ナレーションなし)。", "voice": None, "audio": None, "sfx": True}
    if label == "Outro (Charon)":
        return {"text": "音楽ジングル(ナレーションなし)。outro.mp3、固定音源。", "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification ") or label.startswith("Point Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome (Charon)":
        import er006_audio_cost_pilot_02_shared_narration as sn
        return {"text": sn.FIXED_ENGLISH_TEXTS["welcome"], "voice": charon,
                "audio": f"{narration_dir}/welcome.wav", "sfx": False}
    if label == "Topic intro (Charon)":
        return {"text": f"Today's topic is {parts['title']}.", "voice": charon,
                "audio": f"{narration_dir}/topic_intro.wav", "sfx": False}
    if label.startswith("Japanese title"):
        return {"text": support_texts.get("japanese_title", ""), "voice": "Aoede(JA)",
                "audio": f"{narration_dir}/japanese_title.wav", "sfx": False}
    if label == "Preview intro (Charon)":
        import er006_audio_cost_pilot_02_shared_narration as sn
        return {"text": sn.FIXED_ENGLISH_TEXTS["preview_intro"], "voice": charon,
                "audio": f"{narration_dir}/preview_intro.wav", "sfx": False}
    if label.startswith("Preview "):
        return {"text": support_texts["preview"], "voice": "Aoede(JA)",
                "audio": f"{narration_dir}/preview.wav", "sfx": False}
    if label == "Key phrases intro (Charon)":
        import er006_audio_cost_pilot_02_shared_narration as sn
        return {"text": sn.FIXED_ENGLISH_TEXTS["key_phrases_intro"], "voice": charon,
                "audio": f"{narration_dir}/key_phrases_intro.wav", "sfx": False}
    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        kp = kp_by_rank[rank]
        en = kp["used_form"]
        ja = kp["japanese_gloss"]
        ja_tts = kp.get("japanese_gloss_tts", ja)
        text = f"EN: {en}<br>JA(表示): {ja}" + ("" if ja_tts == ja else f"<br>JA(TTS用): {ja_tts}")
        return {"text": text, "voice": "Aoede(EN)/Aoede(JA)",
                "audio": (f"{narration_dir}/kp{rank}_en.wav", f"{narration_dir}/kp{rank}_ja_aoede.wav"),
                "sfx": False}
    if label == "Full story intro (Charon)":
        import er006_audio_cost_pilot_02_shared_narration as sn
        return {"text": sn.FIXED_ENGLISH_TEXTS["full_story_intro"], "voice": charon,
                "audio": f"{narration_dir}/full_story_intro.wav", "sfx": False}
    for i in (1, 2, 3, 4):
        if label.startswith(f"Comment {i} "):
            return {"text": support_texts[f"comment_{i}"], "voice": "Aoede(JA)",
                    "audio": f"{narration_dir}/comment_{i}.wav", "sfx": False}
    if label.startswith("Hook Part 1"):
        return {"text": parts["part1"], "voice": "Aoede(EN, A2 slowdown)",
                "audio": f"{narration_dir}/full_story_part1.wav", "sfx": False}
    if label.startswith("Hook Part 2"):
        return {"text": parts["part2"], "voice": "Aoede(EN, A2 slowdown)",
                "audio": f"{narration_dir}/full_story_part2.wav", "sfx": False}
    if label.startswith("Narrator: Voice 1 heading"):
        return {"text": parts["point_one_heading"], "voice": "Aoede (Narrator, A2 slowdown)",
                "audio": f"{narration_dir}/point_one_heading.wav", "sfx": False}
    if label.startswith("Voice 1 body"):
        return {"text": parts["point_one_body"], "voice": VOICE_A_3V,
                "audio": f"{narration_dir}/point_one.wav", "sfx": False}
    if label.startswith("Narrator: Voice 2 heading"):
        return {"text": parts["point_two_heading"], "voice": "Aoede (Narrator, A2 slowdown)",
                "audio": f"{narration_dir}/point_two_heading.wav", "sfx": False}
    if label.startswith("Voice 2 body"):
        return {"text": parts["point_two_body"], "voice": VOICE_B_3V,
                "audio": f"{narration_dir}/point_two.wav", "sfx": False}
    if label.startswith("Narrator: Voice 3 heading"):
        return {"text": parts["point_three_heading"], "voice": "Aoede (Narrator, A2 slowdown)",
                "audio": f"{narration_dir}/point_three_heading.wav", "sfx": False}
    if label.startswith("Voice 3 body"):
        return {"text": parts["point_three_body"], "voice": VOICE_C_3V,
                "audio": f"{narration_dir}/point_three.wav", "sfx": False}
    if label.startswith("Tension:"):
        return {"text": parts["tension_body"], "voice": "Aoede(EN, A2 slowdown)",
                "audio": f"{narration_dir}/{b1prod.EXTRA_SEGMENT_NAME}.wav", "sfx": False}
    if label.startswith("Closing:"):
        return {"text": parts["in_one_line"], "voice": "Aoede(EN, A2 slowdown)",
                "audio": f"{narration_dir}/in_one_line.wav", "sfx": False}
    return {"text": "【未取得】このラベルに対応するscript textを本モジュールのマッピングで特定できませんでした。",
            "voice": None, "audio": None, "sfx": False}


# ============================================================
# Web配信用mp3変換(既存前例er014_output/four_type_observation_01/trend/
# run_trend_audio_completion.py::wav_to_mp3()と同一方式[soundfile]。
# player.htmlをraw.githack等のCDN経由で公開試聴できるよう、file:///
# 絶対パス[player_common.abs_file_url、ローカルレビュー専用]ではなく
# 相対パス+mp3で配信する(委任文のWeb到達確認要件に対応)。
# ============================================================
def wav_to_mp3(src_wav_path: str, out_path: str) -> None:
    import soundfile as sf
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    data, sr = sf.read(src_wav_path)
    sf.write(out_path, data, sr, format="MP3")


WEB_SEGMENT_NAMES = (
    "topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
    "point_one_heading", "point_two_heading", "point_three_heading",
    "point_one", "point_two", "point_three",
    "full_story_part1", "full_story_part2", "in_one_line",
    "welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
)


def build_web_delivery_3v_a2(assemble_summary: dict) -> dict:
    web_dir = f"{A2_DIR}/web"
    seg_dir = f"{web_dir}/segments"
    os.makedirs(seg_dir, exist_ok=True)

    episode_mp3 = f"{web_dir}/episode.mp3"
    wav_to_mp3(assemble_summary["out_path"], episode_mp3)

    names = list(WEB_SEGMENT_NAMES) + [b1prod.EXTRA_SEGMENT_NAME]
    for name in names:
        src = f"{NARRATION_DIR}/{name}.wav"
        if os.path.exists(src):
            wav_to_mp3(src, f"{seg_dir}/{name}.mp3")

    kp = load_json(f"{KP_DIR}/keywords_canonicalized.json")
    for item in kp["items"]:
        rank = item["rank"]
        for suffix in (f"kp{rank}_en", f"kp{rank}_ja_aoede"):
            src = f"{NARRATION_DIR}/{suffix}.wav"
            if os.path.exists(src):
                wav_to_mp3(src, f"{seg_dir}/{suffix}.mp3")

    mp3_paths = [episode_mp3] + [f"{seg_dir}/{fn}" for fn in os.listdir(seg_dir)]
    manifest, over_50mb = [], []
    for p in mp3_paths:
        size_bytes = os.path.getsize(p)
        rel = os.path.relpath(p, OUT_DIR).replace("\\", "/")
        manifest.append({"path": rel, "size_bytes": size_bytes})
        if size_bytes > 50 * 1024 * 1024:
            over_50mb.append(rel)

    web_delivery = {
        "episode_mp3": os.path.relpath(episode_mp3, OUT_DIR).replace("\\", "/"),
        "player_path": "player.html",
        "mp3_files": manifest, "all_under_50mb": not over_50mb,
    }
    save_json(f"{OUT_DIR}/web_delivery.json", web_delivery)
    print(f"[USER-TEST-3V-A2] web_delivery.json: episode_mp3={web_delivery['episode_mp3']} "
          f"mp3_count={len(manifest)} all_under_50mb={web_delivery['all_under_50mb']}")
    return web_delivery


def _rel_seg_url(wav_path: str) -> str:
    """narration_dir配下の{name}.wavパスを、player.html(OUT_DIR直下)から見た
    相対mp3パス(a2/web/segments/{name}.mp3)へ変換する。"""
    name = os.path.basename(wav_path).rsplit(".", 1)[0]
    return f"a2/web/segments/{name}.mp3"


def build_player_html_3v_a2(assemble_summary: dict, timeline: list, parts: dict, support_texts: dict) -> str:
    kp_data = load_json(f"{KP_DIR}/keywords_canonicalized.json")
    kp_by_rank = {item["rank"]: item for item in kp_data["items"]}

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue
        info = row_info_a2_3v(label, parts, support_texts, kp_by_rank, NARRATION_DIR)
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"]:
            audio_html = "—"
        elif isinstance(info["audio"], tuple):
            audio_html = player_common.render_single_audio_html(tuple(_rel_seg_url(p) for p in info["audio"]))
        elif info["audio"]:
            audio_html = player_common.render_single_audio_html(_rel_seg_url(info["audio"]))
        else:
            audio_html = "—"
        rows.append(player_common.render_timeline_row(
            sec, label, voice_disp, info["text"], audio_html, missing="未取得" in info["text"]))
    timeline_table = player_common.render_timeline_table(rows)

    kp_rows = []
    for rank in sorted(kp_by_rank):
        kp = kp_by_rank[rank]
        kp_rows.append(f'<tr><td>{rank}</td><td>{kp["used_form"]}</td><td>{kp["japanese_gloss"]}</td>'
                        f'<td>{kp.get("japanese_gloss_tts", kp["japanese_gloss"])}</td>'
                        f'<td>{kp.get("qa_overall_status")}</td></tr>')
    kp_table = ('<table class="kp"><thead><tr><th>#</th><th>English(used_form)</th><th>表示用gloss</th>'
                '<th>TTS用テキスト</th><th>redundancy QA</th></tr></thead>'
                f'<tbody>{"".join(kp_rows)}</tbody></table>')

    episode_audio_url = "a2/web/episode.mp3"
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>USER-TEST-VOICES-A2-MINIMAL-01 (Priority 1: AI hiring 3V A2) player</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>USER-TEST-VOICES-A2-MINIMAL-01(B-Family Voices 3V A2、Trial artifact、
ユーザー実検証用。3V A2正式仕様化・Production wiringではない)</h1>
<p class="note">
完成episode(1本化wav、Standard同期、B-Family 3V A2版)。既存B1(3V)記事
「{parts['title']}」からのA2翻案。duration={assemble_summary['duration_seconds']}s
peak={assemble_summary['peak']} clipping={assemble_summary['clipping_detected']}
headroom_safety_valve_applied={assemble_summary['headroom_safety_valve']['applied']}。
voice_1={VOICE_A_3V} / voice_2={VOICE_B_3V} / voice_3={VOICE_C_3V}
(Voice本文・Narrator見出し・Hook・Tension・Closingは全てAoede英語A2 slowdown)。
Comment 1-4・Preview・日本語タイトルはAoede日本語(標準A2規約)。
各行に「Seek」「Segment名+voice」「実際に読み上げられたscript」「個別音声」を
同一行に配置(標準player形式)。
</p>

<h2>Episode audio</h2>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_audio_url}"></audio>

<h2>タイムライン・全スクリプト(収録順、同一行にSeek+voice+script)</h2>
{timeline_table}

<h2>Key Phrase表(詳細、英語+日本語gloss)</h2>
{kp_table}

</body></html>
"""
    out_path = f"{OUT_DIR}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def stage_audio(budget_jpy_cap: float) -> dict:
    os.makedirs(AUDIT_DIR, exist_ok=True)
    cl.install(COST_LOG_PATH)

    parts = load_json(f"{A2_DIR}/parts.json")
    support_texts = load_json(f"{A2_DIR}/a2_support_texts.json")
    support_texts["japanese_title"] = JAPANESE_TITLE_3V
    kp_merged = load_json(f"{KP_DIR}/keywords_canonicalized.json")

    new_results = run_tts_3v_a2(parts, support_texts, budget_jpy_cap)
    finalize_tts_results_3v_a2(new_results, kp_merged)

    assemble_summary = run_assembly_3v_a2()

    if assemble_summary.get("status") == "OK":
        build_web_delivery_3v_a2(assemble_summary)
        timeline = load_json(f"{AUDIT_DIR}/timeline.json")
        player_path = build_player_html_3v_a2(assemble_summary, timeline, parts, support_texts)
        print(f"[USER-TEST-3V-A2] player.html: {os.path.abspath(player_path)}")
    else:
        print(f"[USER-TEST-3V-A2] Assembly未完了(status={assemble_summary.get('status')})のためplayer.htmlは"
              "生成しません。")

    jpy, by_provider = runner.compute_cost_jpy_so_far(COST_LOG_PATH)
    print(f"[USER-TEST-3V-A2] Audio stage完了。累積cost={jpy:.2f} JPY by_provider={by_provider}")
    return assemble_summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["article", "audio", "all"], default="all")
    parser.add_argument("--budget-jpy", type=float, default=180.0)
    parser.add_argument("--theme", choices=["ai_hiring_3v"], default="ai_hiring_3v")
    parser.add_argument("--only-segments", nargs="*", default=None)
    args = parser.parse_args()
    print(f"[USER-TEST-3V-A2] args={args}")

    if args.stage in ("article", "all"):
        stage_article(args.budget_jpy)
    if args.stage in ("audio", "all"):
        stage_audio(args.budget_jpy)


if __name__ == "__main__":
    main()
