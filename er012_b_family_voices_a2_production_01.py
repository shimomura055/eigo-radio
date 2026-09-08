# ============================================================
# er012_b_family_voices_a2_production_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01
# ============================================================
# B-Family Voices A2(2026-09-09 ユーザー正式決定、APPROVED_FOR_PRODUCTION)の
# Production正式初回経路。Gate 3 item 1「Trial runner 3本(er012_editorial_
# b_voices_a2_trial02_writer.py / ..._trial02_runner.py /
# er012_b_voices_a2_cross_audit_fix_03_runner.py /
# er012_b_voices_a2_slowdown_keyphrase_regen_04_runner.py)に分散していた
# A2経路(翻案Writer呼び出し・Comment/Preview日本語生成・日本語タイトル・
# Key Phrase A2経路・Voice A/B slowdown付きTTS・A2用Assembly・player)」を
# 1箇所へ正式に統合したもの。Trialスクリプトは一切importしない(すべて
# Production primitiveから直接組み立てる、または承認済みテキスト定数を
# 転記する。Phase 1 registry[Comment Contract]と同じ手法)。
#
# 依存(すべてProduction primitive、無変更):
#   - er002_ja_web_research_r3(r3): Fact Checker
#   - er003_v1_en_direct_vfl_01_generate(vfl01): Ledger Deviation Check
#   - er003_v1_en_direct_ab_01_generate(ab01): 語数計測
#   - er003_v1_n3_01_evidence_compression_editor(ec_editor): Evidence
#     Compression編集ルール文言(引用のみ、run_lossless_editor()自体は
#     呼ばない。理由はTrial-02の判断を踏襲: 同関数の【出力形式】が11パート系
#     固定構造を要求し5区切り構造と非互換なため)
#   - er008_point_overlap_qa_18(overlap_qa): Point Overlap QA monitoring
#   - er011_point_role_value_planning_01(point_planning): Point Value QA
#     monitoring
#   - er003_v1_iran01_a2_generate(a2gen): 標準A2 Comment/Preview日本語生成
#     (run_support_text・PREVIEW_ROLE、無変更)
#   - er003_v1_n3_01_tts_generate(n3_tts): 標準A2 TTS関数一式(無変更)
#   - er006_audio_cost_pilot_02_shared_narration(shared_narration): Master
#     Audio Store経由の共有narration・Key Phrase英語Component(無変更)
#   - er012_b_family_voices_production_01(b1prod): 5区切りparser・Voice A/B
#     TTS(generate_voice_body_wide_margin、style_prefix_override引数込み、
#     無変更)
#   - er012_b_family_editorial_type_registry_01(registry): B-Family A2設定
#     (本タスクで追加)
#   - er003_v1_n3_01_assemble(asm): Assembly低レベルprimitive(無変更)
#
# Analytical Leakage Check(定数・プロンプトを含め全文転記、Trial-07 report
# 第9-5節記載の判定基準と同一内容)・Point Overlap/Value QA monitoringは、
# いずれも記事生成[Writer]自体に付随するmonitoring専用QAであり、Gate 3
# item1の統合対象7項目(翻案Writer呼び出し・Comment/Preview日本語生成・
# 日本語タイトル・Key Phrase A2経路・Voice A/B slowdown付きTTS・A2用
# Assembly・player)には明示列挙されていないが、「Trialスクリプトを
# importしない」という同項目の原則を徹底するため、本ファイルへ全文転記した
# (Trial07への依存を断つ)。
from __future__ import annotations

import hashlib
import json
import os
import re

import er002_ja_web_research_r3 as r3
import er003_b1_p9a_audio as p9a
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as n3_tts
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_model_routing_contract_01 as routing
import er008_point_overlap_qa_18 as overlap_qa
import er011_point_role_value_planning_01 as point_planning
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_voices_production_01 as b1prod

# ============================================================
# 5区切り構造parser(b1prod.split_five_voice_sections()をそのまま使う。
# Trial07にも同名関数があったが、b1prod側が既にProduction化済みのため
# ここではb1prodのものだけを使う。重複実装は追加しない)。
# ============================================================
split_five_voice_sections = b1prod.split_five_voice_sections


# ============================================================
# Step A: 翻案Writer(承認済みB1本文をA2へ翻案する)。
# Prompt文言は既存確定原則の引用のみ(新規原則文言は創作しない)。出典は
# EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02_REPORT.md
# 第1-1節に明記済みの各出典と同一。
# ============================================================
A2_KAI1_INSTRUCTION_PARA1_PARA3 = (
    "Write this as an A2-level English news story for listening. The listener should be able to "
    "understand the main events and why they matter even if their English is still limited. Present "
    "information in a clear sequence, make relationships between events explicit, and avoid making "
    "the listener hold several ideas in mind at once. Use simple, natural English and explain "
    "difficult concepts in an everyday way. Rebuild difficult parts freely rather than trying to "
    "preserve sophisticated sentence structures or phrasing.\n\n"
    "Keep each step of the story mentally light. Introduce one main idea at a time, and do not ask "
    "the listener to connect several facts, conditions, or contrasts inside the same sentence or "
    "short passage. When a sentence carries more than one important idea, separate those ideas and "
    "explain them in a simpler order. Prefer clear cause-and-result or before-and-after relationships "
    "over compressed explanation."
)
# 出典: er003_v1_n3_01_articles_generate.py A2_KAI1_INSTRUCTION 第1・第3段落。

CORE_EXPLANATORY_LOGIC_PRESERVATION = (
    "Preserve the core explanatory logic and decision rule established by the Verified Fact Ledger. "
    "You may simplify wording, sentence structure, examples, and presentation order, but do not "
    "replace the Ledger's underlying mechanism or decision rule with an easier shortcut, category, "
    "causal explanation, or rule of thumb that the Ledger does not support or explicitly rejects. "
    "Simplify how the listener understands the idea, not what the idea means."
)
# 出典: CURRENT_SPEC.md「Core Explanatory Logic Preservation」原則(全文引用)。

A2_TABLE_PRINCIPLES_JA = """【CURRENT_SPEC.md「CEFR-A2 構造・音声仕様」節からの引用(vocabulary/文長等)】
- vocabulary: 可能な範囲で平易な一般語を優先(定性的方針)。厳密なCEFR語彙数上限・wordlistは意図的に設けない
- 平均文長: 11語以下(生成方針)
- 最長文: 18語以下(生成方針)
- 全体語数: 上限なし。総語数を意図的に削らない(B1と同等程度の主要情報量を保持)
- 1文1アイデア: 原則1文1メッセージ
- 等位接続・従属節: 関係詞節は原則回避、分詞構文を避ける、複雑な受動態を避ける
- 関係詞: 原則回避
- 受動態: 複雑な受動態は避ける(単純な受動態は許容)
- 完了形・進行形: 完了形等の複雑構造は必要最小限
- Spoken-first: 主語・動詞を早く出す、長い前置詞句・名詞句を文頭に置きすぎない、文末まで聞かないと
  意味が確定しない構造を避ける。厳格なsyntax validatorにはしない(style原則として運用)
- 本文品質要件: Simple AND Natural(平易さと自然さを両立、どちらかを犠牲にしない)"""

B_FAMILY_A2_TASK_INSTRUCTIONS = """【本Trial専用の作業指示(ユーザー決定B-A2-1/B-A2-2/B-A2-4/B-A2-5、2026-09-08承認)】
これは新規記事の生成ではありません。以下に示す、承認済みのB1(CEFR-B1相当)記事本文を、
「同一人物・同一立場のまま」CEFR-A2レベルへ翻案(簡略化リライト)する作業です。

- 記事の物理構造(Markdown見出し5個: `## `見出し1つ→`### `見出し2つ→`## `見出し2つ、
  この順序・見出しレベルを厳守)は、入力と完全に同じ構成のまま維持してください。11パート構造への
  組み替えは行わないでください。
- タイトル(`# `見出し)は入力と一字一句同じものをそのまま使ってください。
- 一人称"I"による語り口は、One Voice(1つ目の###見出し)・Another Voice(2つ目の###見出し)の
  両方で維持してください。
- 2人の人物(One Voice/Another Voice)の立場・価値観・具体的な経験・結論は、入力と完全に同じ
  内容を保ってください。新しいFact・新しい経験・新しい数字を追加しないでください。
- Tension(3つ目の見出し)・Closing(4つ目の見出し)も、入力と同じ役割・同じ結論を保ったまま
  A2レベルへ翻案してください(分量は入力とおおむね同じ比率を保つ)。
- 見出し文言自体は、内容が伝わる範囲で平易な言い方へ変えてよいですが、2つ目・3つ目の見出しには、
  「ここから別の人物の話が始まる」と分かる表現("One Voice:"/"Another Voice:"のような形)を
  必ず含めてください。

【出力形式】
入力と全く同じMarkdown構造(`# `Title、`## `見出し1つ、`### `見出し2つ、`## `見出し2つ、
合計5つの##/###見出し)で、翻案後の記事全文だけを出力してください。説明文やコメントは
付けないでください。"""


def build_adapt_prompt(b1_article_text: str) -> str:
    return (
        B_FAMILY_A2_TASK_INSTRUCTIONS
        + "\n\n【A2言語原則(CURRENT_SPEC.md CEFR-A2節からの引用)】\n"
        + A2_KAI1_INSTRUCTION_PARA1_PARA3
        + "\n\n【Core Explanatory Logic Preservation(CURRENT_SPEC.md L266からの引用)】\n"
        + CORE_EXPLANATORY_LOGIC_PRESERVATION
        + "\n\n" + A2_TABLE_PRINCIPLES_JA
        + "\n\n【翻案対象のB1記事本文(そのまま、そっくりコピーしないでA2へ翻案すること)】\n"
        + b1_article_text
    )


def run_writer_adapt(client, b1_article_text: str, model: str, reasoning_effort: str = "high") -> dict:
    prompt = build_adapt_prompt(b1_article_text)
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
        raise RuntimeError("[A2-PROD][Writer] A2翻案応答が空です")
    return {"status": "OK", "text": text, "model": response.model, "response_id": response.id,
            "prompt": prompt, "reasoning_effort": reasoning_effort}


# ============================================================
# Step B: Evidence Compression Editor(方式C、ルール文言は無変更引用。
# 【出力形式】の構造描写のみ5区切り用に差し替え、他は一切変更しない)。
# ============================================================
_B_FAMILY_STRUCTURE_OUTPUT_FORMAT = """【出力形式】
編集後の記事全文を、入力と全く同じMarkdown構造(# Title、## 見出し1つ、### 見出し2つ、
## 見出し2つ、この順序・見出しレベル)で出力してください。説明文やコメントは付けず、
編集後の記事本文だけを出力してください。"""


def build_evidence_compression_prompt(article_text: str) -> str:
    base = ec_editor.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text=article_text)
    marker = "【出力形式】"
    idx = base.rindex(marker)
    return base[:idx] + _B_FAMILY_STRUCTURE_OUTPUT_FORMAT


def run_evidence_compression(client, article_text: str, model: str) -> dict:
    prompt = build_evidence_compression_prompt(article_text)
    resp = client.responses.create(
        model=model,
        reasoning={"effort": "medium"},
        input=[{"role": "user", "content": prompt}],
    )
    text = (resp.output_text or "").strip()
    if not text:
        raise RuntimeError("[A2-PROD][Evidence-Compression] 応答が空です")
    return {"status": "OK", "text": text, "model": resp.model, "response_id": resp.id, "prompt": prompt}


# ============================================================
# Step C: Fact Checker(既存Production primitive、無変更)
# ============================================================
# OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01:
# voice_attribution_block(既定""、後方互換)。呼び出し元(production
# runner)がregistry.is_fact_attribution_mode_enabled()==Trueの場合のみ
# 非空文字列を渡す。既定""のときはr3.build_fact_check_prompt()の戻り値が
# 本引数追加以前とbyte単位で同一のため、この関数自体の出力もOFF時は無変更。
def run_fact_checker(topic: str, article_text: str, voice_attribution_block: str = "") -> dict:
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [], voice_attribution_block=voice_attribution_block)

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn)
    return {
        "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result, "attempts_detail": fc_attempts,
    }


# ============================================================
# Step D: Ledger Deviation Check(vfl01.run_deviation_check、monitoring専用。
# 自動Local Rewriteループは行わない、Phase 1と同じ用法)
# ============================================================
def run_ledger_deviation(client, ledger_text: str, article_text: str, model: str) -> dict:
    result = vfl01.run_deviation_check(client, ledger_text, article_text, model=model, hook_aware=True)
    return result["parsed"]


# ============================================================
# Step E: Point Overlap/Value QA monitoring(Trial-07 run_five_section_
# point_qa_monitoring()の全文転記。monitoring専用、flaggedでもretry・
# 早期returnせず、本文も変更しない。Production primitive自体
# [overlap_qa.flag_possible_paraphrase/point_planning.run_point_value_qa]は
# 無変更のまま個別呼び出しする)。
# ============================================================
def run_five_section_point_qa_monitoring(client, sections: dict, writer_model: str, out_dir: str) -> dict:
    hook = sections["hook_body"]
    voice_a = sections["voice_a_body"]
    voice_b = sections["voice_b_body"]

    voice_a_vs_hook = overlap_qa.flag_possible_paraphrase(voice_a, hook)
    voice_b_vs_hook = overlap_qa.flag_possible_paraphrase(voice_b, hook)
    voice_a_vs_voice_b = overlap_qa.flag_possible_paraphrase(voice_a, voice_b)
    voice_b_vs_voice_a = overlap_qa.flag_possible_paraphrase(voice_b, voice_a)
    lexical_flagged = any(r["flagged"] for r in
                           (voice_a_vs_hook, voice_b_vs_hook, voice_a_vs_voice_b, voice_b_vs_voice_a))

    value_qa_result = point_planning.run_point_value_qa(
        client, hook, voice_a, voice_b, model=writer_model, reasoning_effort=vfl01.REASONING_EFFORT)
    value_qa_flagged = value_qa_result["status"] == "NG"

    monitoring_summary = {
        "qa_status": "OK",
        "lexical_flagged": lexical_flagged,
        "value_qa_flagged": value_qa_flagged,
        "note": ("EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01: Trial-07由来のmonitoring専用QA "
                 "(全文転記、Trialスクリプトは一切importしない)。flaggedであっても記事全体retry・"
                 "Point-only regenerationは一切発生させず、本文は変更せずそのままFact Checker以降へ"
                 "進める。"),
        "voice_a_vs_hook": voice_a_vs_hook,
        "voice_b_vs_hook": voice_b_vs_hook,
        "voice_a_vs_voice_b": voice_a_vs_voice_b,
        "voice_b_vs_voice_a": voice_b_vs_voice_a,
        "value_qa_status": value_qa_result["status"],
        "value_qa_result": value_qa_result,
    }
    with open(f"{out_dir}/point_overlap_value_qa_monitoring.json", "w", encoding="utf-8") as f:
        json.dump(monitoring_summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[A2-PROD][Point-QA] monitoring(5区切り専用) lexical_flagged={lexical_flagged} "
          f"value_qa_flagged={value_qa_flagged}(gateにはしない)")
    return monitoring_summary


# ============================================================
# Step F: Analytical Leakage Check(Trial-07の定数・プロンプト・JSON
# schemaを全文転記。判定基準・文言は一切変更していない)。
# ============================================================
VOICE_LEAKAGE_FIELDS = (
    "leak_evidence_subject", "leak_numbers_foreground", "leak_narrator_analysis",
    "leak_unknowable_analysis", "leak_discovery_syntax", "leak_evidence_memorable",
)
TENSION_LEAKAGE_FIELDS = (
    "leak_evidence_subject", "leak_numbers_foreground", "leak_discovery_syntax",
    "leak_evidence_memorable", "leak_tension_reverts_to_research",
)
CLOSING_LEAKAGE_FIELDS = ("leak_closing_simple_summary",)
_LEAKAGE_SECTION_FIELDS = {
    "voice_a": VOICE_LEAKAGE_FIELDS, "voice_b": VOICE_LEAKAGE_FIELDS,
    "tension": TENSION_LEAKAGE_FIELDS, "closing": CLOSING_LEAKAGE_FIELDS,
}

LEAKAGE_CHECK_DEVELOPER_MESSAGE = (
    "あなたは'Voices/Perspective'型記事のVoice section・Tension section・Closing sectionを"
    "審査する、厳格なEditorial QA判定者です。それぞれのsectionが、実在する当事者(人)の"
    "経験・価値観・必要・心配として書かれているか、あるいは調査結果・データを整理して"
    "説明する文章、単なる要約、Writer自身の解決策提案に戻っていないかを、各section指定の"
    "基準についてPASS/FAILで判定してください。各基準についてPASSは『問題なし』、FAILは"
    "『その問題が実際に本文に存在する』ことを意味します。FAILの場合は、該当する原文の一節を"
    "quoted_evidenceにそのまま引用してください(複数箇所ある場合は代表的な1〜2箇所)。PASSの"
    "場合はquoted_evidenceを空文字列にしてください。"
)


def _leakage_item_schema(fields: tuple) -> dict:
    props = {f: {"type": "string", "enum": ["PASS", "FAIL"]} for f in fields}
    props["reasoning"] = {"type": "string"}
    props["quoted_evidence"] = {"type": "string"}
    return {"type": "object", "properties": props, "required": list(props.keys()),
            "additionalProperties": False}


ANALYTICAL_LEAKAGE_JSON_SCHEMA = {
    "name": "analytical_leakage_check",
    "schema": {
        "type": "object",
        "properties": {
            "voice_a": _leakage_item_schema(VOICE_LEAKAGE_FIELDS),
            "voice_b": _leakage_item_schema(VOICE_LEAKAGE_FIELDS),
            "tension": _leakage_item_schema(TENSION_LEAKAGE_FIELDS),
            "closing": _leakage_item_schema(CLOSING_LEAKAGE_FIELDS),
        },
        "required": ["voice_a", "voice_b", "tension", "closing"],
        "additionalProperties": False,
    },
    "strict": True,
}

LEAKAGE_CHECK_PROMPT_TEMPLATE = """以下は、あるVoices/Perspective型記事の4つのsection本文
(One Voice/Another Voice/Tension/Closing)です。それぞれについて、指定された項目を判定
してください(それぞれPASS/FAIL)。

【One Voice(Voice A)・Another Voice(Voice B)に適用する6項目】
- leak_evidence_subject: 文の主語がsurvey/research/data/percentage(調査・報告・データ)に
  なっている文が無い場合PASS(例: "A survey found...", "Research shows...", "X% of
  workers said..."のような文が無い場合PASS)
- leak_numbers_foreground: 具体的な数字・比較結果(パーセント・人数比較等)が、その人の
  経験の描写より前面に出ていない場合PASS(数字が0個、または1個だけがその人の実感として
  自然に織り込まれている場合はPASS。複数の数字が連続して比較されている場合はFAIL)
- leak_narrator_analysis: Narrator(語り手)が、Voiceの人物を外側から分析・要約していない
  場合PASS(例: "For a worker who..."のような紹介・要約文で始まっていたり、"This suggests
  that..."のような分析者の言い回しが無い場合PASS)
- leak_unknowable_analysis: その人物自身が実際に考え・言いそうにない、外部の分析的視点
  (第三者の解決策・比較の含意等)を、その人のPerspectiveとして書いていない場合PASS
- leak_discovery_syntax: 「調査結果を整理して説明する」Discovery/Trend記事のような文構造
  (reported/showed the same pattern/compared with等)へ戻っていない場合PASS
- leak_evidence_memorable: このsectionを読み終えたときに、Evidence(数字・出典)よりも
  その人物の経験・感情の方が記憶に残る書き方になっている場合PASS

【Tensionに適用する5項目】
- leak_evidence_subject / leak_numbers_foreground / leak_discovery_syntax /
  leak_evidence_memorable: 上記と同じ意味(Tension本文に対して判定)
- leak_tension_reverts_to_research: Tensionの中心が、2人がなぜ違う答えに至るのか
  (価値観・経験・制約・何を優先するか・問題をどう定義しているか)の掘り下げになっており、
  survey/研究データそのものの説明・比較へ戻っていない場合PASS。survey/研究結果の紹介・
  数字比較がTensionの主たる内容になっている場合FAIL

【Closingに適用する1項目】
- leak_closing_simple_summary: Closingが、単なる要約や「両方に良い点がある」「人による」
  という結び方だけで終わっておらず、かつWriter自身の解決策・妥協案の提案(例: 半固定席の
  導入等)になっていない場合PASS。単純要約または解決策提案になっている場合FAIL

reasoningには、判定理由を1〜2文の日本語で書いてください。FAILの場合はquoted_evidenceに
該当する原文を引用してください(英語本文をそのまま引用してよい)。PASSの場合quoted_evidence
は空文字列にしてください。

【One Voice(Voice A)本文】
{voice_a_body}

【Another Voice(Voice B)本文】
{voice_b_body}

【Tension本文】
{tension_body}

【Closing本文】
{closing_body}
"""


class LeakageCheckModelMismatchError(RuntimeError):
    pass


def run_analytical_leakage_check(client, sections: dict, model: str, reasoning_effort: str,
                                  out_dir: str, attempt: int) -> dict:
    prompt = LEAKAGE_CHECK_PROMPT_TEMPLATE.format(
        voice_a_body=sections["voice_a_body"], voice_b_body=sections["voice_b_body"],
        tension_body=sections["tension_body"], closing_body=sections["closing_body"])
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **ANALYTICAL_LEAKAGE_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": LEAKAGE_CHECK_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    if response.model != model:
        raise LeakageCheckModelMismatchError(
            f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Analytical Leakage Check応答が空です")
    parsed = json.loads(text)

    flagged_items = []
    for section_key in ("voice_a", "voice_b", "tension", "closing"):
        item = parsed[section_key]
        fields = _LEAKAGE_SECTION_FIELDS[section_key]
        fail_fields = [f for f in fields if item[f] == "FAIL"]
        if fail_fields:
            flagged_items.append({
                "voice": section_key, "fail_fields": fail_fields,
                "reasoning": item["reasoning"], "quoted_evidence": item["quoted_evidence"],
            })
    result = {
        "model": response.model, "response_id": response.id, "prompt": prompt, "parsed": parsed,
        "flagged_items": flagged_items, "any_flagged": bool(flagged_items),
    }
    with open(f"{out_dir}/analytical_leakage_check_attempt{attempt}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[A2-PROD][Leakage-Check] attempt{attempt}: any_flagged={result['any_flagged']} "
          f"flagged_items={[(x['voice'], x['fail_fields']) for x in flagged_items]}")
    return result


# ============================================================
# 語数・文長の機械チェック(5区切り版。既存A2数値目標[11語/18語]に対する
# 実測レポート、新規原則の創作ではない)
# ============================================================
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def _sentence_word_lengths(text: str) -> list:
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    return [len(re.findall(r"[A-Za-z']+", s)) for s in sentences]


def compute_section_stats(sections: dict) -> dict:
    stats = {}
    for label in ("hook_body", "voice_a_body", "voice_b_body", "tension_body", "closing_body"):
        text = sections[label]
        lengths = _sentence_word_lengths(text)
        stats[label] = {
            "word_count": ab01.compute_word_count(text),
            "sentence_count": len(lengths),
            "avg_sentence_len_words": round(sum(lengths) / len(lengths), 2) if lengths else 0,
            "max_sentence_len_words": max(lengths) if lengths else 0,
            "sentences_over_11_words": sum(1 for n in lengths if n > 11),
            "sentences_over_18_words": sum(1 for n in lengths if n > 18),
        }
    total_words = sum(v["word_count"] for v in stats.values())
    all_lengths = []
    for label in ("hook_body", "voice_a_body", "voice_b_body", "tension_body", "closing_body"):
        all_lengths.extend(_sentence_word_lengths(sections[label]))
    stats["_total"] = {
        "word_count": total_words,
        "sentence_count": len(all_lengths),
        "avg_sentence_len_words": round(sum(all_lengths) / len(all_lengths), 2) if all_lengths else 0,
        "max_sentence_len_words": max(all_lengths) if all_lengths else 0,
        "sentences_over_11_words": sum(1 for n in all_lengths if n > 11),
        "sentences_over_18_words": sum(1 for n in all_lengths if n > 18),
    }
    return stats


# ============================================================
# Step G: Comment 1-4・Preview(registry Comment Contract + 標準A2日本語
# 経路[a2gen.run_support_text/PREVIEW_ROLE、無変更])
# ============================================================
def run_scaffold_a2(parts: dict, article_text: str, ledger_text: str, out_a2_dir: str, audit_dir: str) -> dict:
    client = a2gen.get_client()
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    comment_roles = registry.get_editorial_type("b_family_voices")["comment_roles"]

    c1_context = f"【これから聞く本文(The Question)】\n{parts['part1']}\n{parts['part2']}"
    c1 = a2gen.run_support_text(client, comment_roles["comment_1"], c1_context, model=model)

    c2_context = (f"【すでに聞いた本文(The Question)】\n{parts['part1']}\n{parts['part2']}\n\n"
                  f"【これから聞く声の見出しのみ(内容は伏せる、この時点でこの文言を言わないこと)】\n"
                  f"One Voice heading: {parts['point_one_heading']}\n"
                  f"Another Voice heading: {parts['point_two_heading']}")
    c2 = a2gen.run_support_text(client, comment_roles["comment_2"], c2_context, model=model)

    c3_context = (f"【One Voice(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Another Voice(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
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
    os.makedirs(audit_dir, exist_ok=True)
    with open(f"{out_a2_dir}/a2_support_texts.json", "w", encoding="utf-8") as f:
        json.dump({k: v.get("text") for k, v in results.items()}, f, ensure_ascii=False, indent=2)
    with open(f"{audit_dir}/a2_support_generation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    support_concat = "\n\n".join(t for t in (v.get("text") for v in results.values()) if t)
    deviation = vfl01.run_deviation_check(client, ledger_text, support_concat)
    with open(f"{audit_dir}/support_ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation["parsed"], f, ensure_ascii=False, indent=2, default=str)

    return {"support": results, "support_status": {k: v.get("status") for k, v in results.items()},
            "deviation": deviation["parsed"]}


# ============================================================
# Step H: 日本語タイトル(標準A2既存規約と同一関数、無変更)。テキストは
# registry.B_FAMILY_A2_JAPANESE_TITLESから記事キー経由で取得する(標準A2の
# JAPANESE_TITLESと同じ「記事ごとに人手で直訳を用意する」パターン)。
# ============================================================
def generate_japanese_title(theme_key: str, out_path: str) -> dict:
    a2_config = registry.get_editorial_type_a2()
    text = a2_config["japanese_titles"][theme_key]
    result = n3_tts.generate_a2_japanese_with_reading_safety(
        text, out_path, n3_tts.expected_substring_ja(text), max_extra_chars=30)
    result["canonical_text"] = text
    return result


# ============================================================
# Step I: Key Phrase A2経路(選定はB1 Phase 1と同一、英語Componentは既存
# Master Audio Store cache経由[voice=Aoede]、日本語glossのみ標準A2 Aoede
# 経路で新規生成)
# ============================================================
def reuse_key_phrases_a2(kp_source_dir: str, kp_dir: str, narration_dir: str) -> dict:
    import shutil
    os.makedirs(kp_dir, exist_ok=True)
    os.makedirs(narration_dir, exist_ok=True)
    shutil.copyfile(f"{kp_source_dir}/key_phrases/keywords_canonicalized.json",
                     f"{kp_dir}/keywords_canonicalized.json")
    with open(f"{kp_dir}/keywords_canonicalized.json", encoding="utf-8") as f:
        kp = json.load(f)

    results = {}
    for item in kp["items"]:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts, ja_gloss_tts_fallback = n3_tts.resolve_key_phrase_ja_gloss_tts(item)

        with cl.segment_context(f"kp{rank}_english"):
            en_r = shared_narration.ensure_key_phrase_english_component(
                n3_tts.tts_safe_kp_en(used_form), f"{narration_dir}/kp{rank}_en.wav")
        en_r["used_form"] = used_form

        with cl.segment_context(f"kp{rank}_japanese"):
            ja_r = n3_tts.generate_a2_japanese_with_reading_safety(
                ja_gloss_tts, f"{narration_dir}/kp{rank}_ja_aoede.wav", n3_tts.expected_substring_ja(ja_gloss_tts),
                max_extra_chars=30, known_key_phrase_terms=[used_form])
        ja_r["display_gloss"] = ja_gloss
        ja_r["japanese_gloss_tts_fallback_derived"] = ja_gloss_tts_fallback
        results[rank] = {"english": en_r, "japanese": ja_r}
    return results


# ============================================================
# Step J: Voice A/B本文(point_one/point_two相当)へ標準A2の既存6%
# slowdownを適用する合成関数。既存関数2つを順に呼ぶだけ(新規TTS/ASR/
# time-stretchロジックなし)。EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-
# KEYPHRASE-REGEN-04で確立した実装をそのまま正式Production化。
# ============================================================
def generate_voice_body_wide_margin_with_a2_slowdown(name: str, tts_input: str, out_path: str,
                                                       voice_name: str) -> dict:
    result = b1prod.generate_voice_body_wide_margin(
        tts_input, out_path, voice_name,
        style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER,
        enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)
    return n3_tts.apply_a2_slowdown_postprocess(name, out_path.rsplit("/", 1)[0], tts_input, result)


# ============================================================
# Step K: Assembly(A2版ローダー+timeline builder。asm.pyの低レベル
# primitiveは無変更のまま再利用する。asm.load_b1_sources()自体はB1固定の
# ファイル名規約[_charon suffix・"b1b"サブディレクトリ]にhard-codeされ
# A2命名と非互換なため、新規ローダーをここへ追加する[asm.py自体は無変更])。
# ============================================================
def load_a2_sources_for_b_family(kp: dict, a2_dir: str, narration_dir: str, audio_gate_level: str) -> dict:
    asm.verify_episode_audio_validation_gate(a2_dir, audio_gate_level)

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    point_notification = p9a.load_and_resample_to_target(asm.POINT_NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    import er002_common as common

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
    for name in ("full_story_part1", "full_story_part2", "point_one", "point_two",
                  b1prod.EXTRA_SEGMENT_NAME, "in_one_line",
                  "comment_1", "comment_2", "comment_3", "comment_4", "preview",
                  "point_one_heading", "point_two_heading"):
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


def build_a2_voices_timeline(parts: dict, voice_a: str, voice_b: str) -> list:
    """b1prod.build_b1_voices_timeline()と同じ順序・同じpause定数を使うが、
    Comment/Preview/Key Phrase日本語glossがCharonではなくAoede(日本語)に
    なったことを反映し、ラベル文言のみ差し替えた関数(既存build_b1_voices_
    timeline()自体は無変更)。pause秒数は標準A2の「Comment、英語→日本語」
    1.0秒・「日本語→英語」0.8秒(CURRENT_SPEC.md L356-357)と同じ値のため、
    asm.AOEDE_TO_CHARON_PAUSE_SECONDS/CHARON_TO_AOEDE_PAUSE_SECONDSの数値を
    そのまま流用する(値は変更しない、ラベル名の意味だけがA2文脈では
    「Aoede英語→Aoede日本語」に読み替わる)。"""
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
        ("Point Notification (Voice A cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: One Voice heading (Aoede, English, A2 slowdown)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice A body ({voice_a}, A2 slowdown)", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice B cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Another Voice heading (Aoede, English, A2 slowdown)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice B body ({voice_b}, A2 slowdown)", b1["point_two"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Aoede, Japanese, A2)", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Tension: Where the Difference Comes From (Aoede, English, A2 slowdown, no heading)",
         b1[b1prod.EXTRA_SEGMENT_NAME]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Aoede, Japanese, A2)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Closing: What the Seat Really Means (Aoede, English, A2 slowdown, no heading, In One Line)",
         b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


# ============================================================
# Step L: OPEN-129整合 — 完全性チェック(Lane B runner側専用、共有Gateは
# 変更しない)。registry.B_FAMILY_A2_REQUIRED_SEGMENTSの段数・役割が実際の
# segment_status/voice解決結果と一致するかを検証する。
# ============================================================
def check_required_segments_completeness(segment_status: dict, voice_a: str, voice_b: str) -> dict:
    a2_config = registry.get_editorial_type_a2()
    required = a2_config["required_segments"]
    missing = []
    role_mismatch = []
    for name, role in required:
        if name not in segment_status:
            missing.append(name)
            continue
        if segment_status[name] != "OK":
            missing.append(f"{name}(status={segment_status[name]})")
    extra = [name for name in segment_status if name not in {n for n, _ in required}]
    result = {
        "expected_segment_count": len(required),
        "actual_present_count": sum(1 for n, _ in required if n in segment_status),
        "missing_or_not_ok": missing,
        "unexpected_extra_segments": extra,
        "voice_a": voice_a, "voice_b": voice_b,
        "complete": not missing,
    }
    return result


# ============================================================
# player.html用の行情報(Step Kのtimelineラベルに対応する表示情報)
# ============================================================
def row_info_a2(label: str, parts: dict, support_texts: dict, voice_a: str, voice_b: str,
                 kp_by_rank: dict, narration_dir: str) -> dict:
    charon = "Charon"
    if label == "Intro":
        return {"text": "音楽ジングル(ナレーションなし)。", "voice": None, "audio": None, "sfx": True}
    if label == "Outro (Charon)":
        return {"text": "音楽ジングル(ナレーションなし)。outro.mp3、固定音源。", "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification ") or label.startswith("Point Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["welcome"], "voice": charon,
                "audio": f"{narration_dir}/welcome.wav", "sfx": False}
    if label == "Topic intro (Charon)":
        return {"text": f"Today's topic is {parts['title']}.", "voice": charon,
                "audio": f"{narration_dir}/topic_intro.wav", "sfx": False}
    if label.startswith("Japanese title"):
        return {"text": support_texts.get("japanese_title", ""), "voice": "Aoede(JA)",
                "audio": f"{narration_dir}/japanese_title.wav", "sfx": False}
    if label == "Preview intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"], "voice": charon,
                "audio": f"{narration_dir}/preview_intro.wav", "sfx": False}
    if label.startswith("Preview "):
        return {"text": support_texts["preview"], "voice": "Aoede(JA)",
                "audio": f"{narration_dir}/preview.wav", "sfx": False}
    if label == "Key phrases intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], "voice": charon,
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
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], "voice": charon,
                "audio": f"{narration_dir}/full_story_intro.wav", "sfx": False}
    if label.startswith("Comment 1 "):
        return {"text": support_texts["comment_1"], "voice": "Aoede(JA)", "audio": f"{narration_dir}/comment_1.wav", "sfx": False}
    if label.startswith("Comment 2 "):
        return {"text": support_texts["comment_2"], "voice": "Aoede(JA)", "audio": f"{narration_dir}/comment_2.wav", "sfx": False}
    if label.startswith("Comment 3 "):
        return {"text": support_texts["comment_3"], "voice": "Aoede(JA)", "audio": f"{narration_dir}/comment_3.wav", "sfx": False}
    if label.startswith("Comment 4 "):
        return {"text": support_texts["comment_4"], "voice": "Aoede(JA)", "audio": f"{narration_dir}/comment_4.wav", "sfx": False}
    if label.startswith("Hook Part 1"):
        return {"text": parts["part1"], "voice": "Aoede(EN, A2 slowdown)", "audio": f"{narration_dir}/full_story_part1.wav", "sfx": False}
    if label.startswith("Hook Part 2"):
        return {"text": parts["part2"], "voice": "Aoede(EN, A2 slowdown)", "audio": f"{narration_dir}/full_story_part2.wav", "sfx": False}
    if label.startswith("Narrator: One Voice heading"):
        return {"text": parts["point_one_heading"], "voice": "Aoede (Narrator, A2 slowdown)",
                "audio": f"{narration_dir}/point_one_heading.wav", "sfx": False}
    if label.startswith("Voice A body"):
        return {"text": parts["point_one_body"], "voice": voice_a, "audio": f"{narration_dir}/point_one.wav", "sfx": False}
    if label.startswith("Narrator: Another Voice heading"):
        return {"text": parts["point_two_heading"], "voice": "Aoede (Narrator, A2 slowdown)",
                "audio": f"{narration_dir}/point_two_heading.wav", "sfx": False}
    if label.startswith("Voice B body"):
        return {"text": parts["point_two_body"], "voice": voice_b, "audio": f"{narration_dir}/point_two.wav", "sfx": False}
    if label.startswith("Tension:"):
        return {"text": parts["tension_body"], "voice": "Aoede(EN, A2 slowdown)",
                "audio": f"{narration_dir}/{b1prod.EXTRA_SEGMENT_NAME}.wav", "sfx": False}
    if label.startswith("Closing:"):
        return {"text": parts["in_one_line"], "voice": "Aoede(EN, A2 slowdown)", "audio": f"{narration_dir}/in_one_line.wav", "sfx": False}
    return {"text": "【未取得】このラベルに対応するscript textを本モジュールのマッピングで特定できませんでした。",
            "voice": None, "audio": None, "sfx": False}
