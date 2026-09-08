# ============================================================
# er012_editorial_b_voices_a2_trial02_writer.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02(Lane B)
# ============================================================
# Step 1(A2記事生成)の実装。ユーザー承認済みB1本文
# (er012_output/editorial_b_family_production_phase1_02/b1b/article.md)
# を、5区切り構造(Hook/Voice A/Voice B/Tension/Closing)を維持したまま
# A2の言語・声規約(CURRENT_SPEC.md「CEFR-A2 構造・音声仕様」節)へ翻案
# (簡略化リライト)する。B-A2-1/B-A2-2/B-A2-4/B-A2-5(2026-09-08ユーザー
# 決定)に基づく。
#
# Writer Promptは、以下の既存確定原則を「引用」して組み立てる(新しい
# 原則文言は創作しない):
#   - CURRENT_SPEC.md CEFR-A2表の各セル(vocabulary/平均文長/最長文/
#     全体語数/1文1アイデア/等位接続・従属節/関係詞/受動態/完了形・進行形/
#     Spoken-first/本文品質要件、L217-238)
#   - A2_KAI1_INSTRUCTION(er003_v1_n3_01_articles_generate.py L541-547)の
#     第1・第3段落のみ(簡略化スタイル原則、genre非依存)。第2段落
#     (「Verified Fact Ledgerの…」)はCore Explanatory Logic Preservation
#     として別途引用する。第4段落("a genuinely different, separately-
#     optimized narrative from the B1 version…build it fresh from the
#     same Fact Ledger…")は、本Trialの前提(ユーザー決定B-A2-2: 承認済み
#     B1本文をそのまま翻案する)と正面から矛盾するため引用しない
#     (Ledgerから独立生成する標準A2方式ではなく、承認済みB1本文の翻案と
#     いう方式そのものがユーザー決定事項であるため)。
#   - Core Explanatory Logic Preservation原則(CURRENT_SPEC.md L266、
#     A2_KAI1_INSTRUCTIONへの追加原則として全文引用)
#
# Editor(Evidence Compression/Numeric Precision)は、
# er003_v1_n3_01_evidence_compression_editor.pyのルール文言ブロック
# (EVIDENCE_COMPRESSION_PURPOSE_BLOCK_EN・PATTERN_A_...・
# LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK・許可/禁止編集リスト)を
# 無変更のまま引用するが、同ファイルのrun_lossless_editor()自体は
# 呼ばない(その関数の【出力形式】指示が「###見出し2つ+In one line」
# というP-series/A2/B1共通11パート系の固定構造を明示的に要求しており、
# B-Familyの5区切り構造とは物理構造が異なるため、構造描写の一文だけを
# 本ファイル側で5区切り構造用に差し替える。編集ルール本文[許可される
# 編集・絶対に行ってはいけない編集]は一切変更しない)。
#
# Fact Checker(r3.build_fact_check_prompt/make_fact_checker_fn/
# run_fact_checker_with_gates)・Ledger Deviation Check
# (vfl01.run_deviation_check)は、既存Production primitiveを無変更で
# 呼ぶ。Deviation CheckはPhase 1と同じ「monitoring専用」(自動Local
# Rewriteループは行わない、Phase 1 runnerの用法と同一)。
#
# Point Overlap/Value QA・Analytical Leakage Checkは、Trial-06/07で
# 使われたB-Family専用QA関数(er012_editorial_b_voices_trial_07.py
# ::run_five_section_point_qa_monitoring/run_analytical_leakage_check)を
# 無変更のままimportして再利用する(Trial資産の再利用、Production
# ファイルへは一切書き込まない)。
#
# 触れないもの: CURRENT_SPEC.md、既存Production/Trialファイル本体
# (すべてimportのみ)、SSOT。
from __future__ import annotations

import json
import os
import re

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er006_model_routing_contract_01 as routing
import er012_b_family_voices_production_01 as b1prod
import er012_editorial_b_voices_trial_07 as trial07

# ============================================================
# 入出力パス
# ============================================================
B1_ARTICLE_PATH = "er012_output/editorial_b_family_production_phase1_02/b1b/article.md"
LEDGER_PATH = "er012_output/editorial_b_voices_trial_07/research/verified_fact_ledger.txt"
TOPIC_JA = trial07.TOPIC_JA  # Trial-07から無変更で流用(同一Ledger・同一テーマ、B-A2-2)

OUT_DIR = "er012_output/editorial_b_voices_a2_free_address_02"
A2_DIR = f"{OUT_DIR}/a2"
AUDIT_DIR = f"{A2_DIR}/audit"

MODEL_PROCESS = "A2_WRITER"  # er006_model_routing_contract_01.PROCESS_MODEL_MAP


def get_client():
    return vfl01.get_client()


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


# ============================================================
# Writer Prompt(既存確定原則の引用のみ、新規原則文言は創作しない)
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
# 出典: er003_v1_n3_01_articles_generate.py A2_KAI1_INSTRUCTION 第1・第3段落
# (第2段落[Ledger mechanism]は下記CORE_EXPLANATORY_LOGIC_PRESERVATIONとして
# 別途引用、第4段落["build it fresh from the Fact Ledger"]はB-A2-2の
# 「B1本文の翻案」方針と矛盾するため不採用)。

CORE_EXPLANATORY_LOGIC_PRESERVATION = (
    "Preserve the core explanatory logic and decision rule established by the Verified Fact Ledger. "
    "You may simplify wording, sentence structure, examples, and presentation order, but do not "
    "replace the Ledger's underlying mechanism or decision rule with an easier shortcut, category, "
    "causal explanation, or rule of thumb that the Ledger does not support or explicitly rejects. "
    "Simplify how the listener understands the idea, not what the idea means."
)
# 出典: CURRENT_SPEC.md L266(Core Explanatory Logic Preservation原則、全文引用)。
# 本Trialでは「Ledger」を「翻案元であるB1本文(既にVerified Fact Ledgerに基づき
# Fact Checker/Ledger Deviation Checkを通過済みの承認済み記事)」と読み替える。

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
        raise RuntimeError("[WRITER] A2翻案応答が空です")
    return {"status": "OK", "text": text, "model": response.model, "response_id": response.id,
            "prompt": prompt, "reasoning_effort": reasoning_effort}


# ============================================================
# Evidence Compression Editor(方式C、ルール文言は無変更引用。
# 【出力形式】の構造描写のみ5区切り用に差し替え)
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
        raise RuntimeError("[EVIDENCE-COMPRESSION] 応答が空です")
    return {"status": "OK", "text": text, "model": resp.model, "response_id": resp.id, "prompt": prompt}


# ============================================================
# Fact Checker(既存Production primitive、無変更)
# ============================================================
def run_fact_checker(topic: str, article_text: str) -> dict:
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

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
# Ledger Deviation Check(vfl01.run_deviation_check、Phase 1と同じ
# monitoring専用の用法。自動Local Rewriteループは行わない)
# ============================================================
def run_ledger_deviation(client, ledger_text: str, article_text: str, model: str) -> dict:
    result = vfl01.run_deviation_check(client, ledger_text, article_text, model=model, hook_aware=True)
    return result["parsed"]


# ============================================================
# 語数・文長の機械チェック(5区切り版、新規計測コード。原則の新規創作
# ではなく、既存A2数値目標[11語/18語]に対する実測レポート)
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
# main: Step 1一括実行
# ============================================================
def main() -> dict:
    os.makedirs(AUDIT_DIR, exist_ok=True)
    client = get_client()
    writer_model = routing.require_model(MODEL_PROCESS, routing.WRITER_MODEL)

    b1_article_text = load_text(B1_ARTICLE_PATH)
    ledger_text = load_text(LEDGER_PATH)
    b1_sections = trial07.split_five_voice_sections(b1_article_text)
    b1_stats = compute_section_stats(b1_sections)
    save_json(f"{AUDIT_DIR}/b1_source_stats.json", b1_stats)

    print("[A2-TRIAL02][Writer] A2翻案 開始...")
    writer_result = run_writer_adapt(client, b1_article_text, writer_model)
    with open(f"{AUDIT_DIR}/writer_prompt.txt", "w", encoding="utf-8") as f:
        f.write(writer_result["prompt"])
    save_json(f"{AUDIT_DIR}/writer_result.json",
              {k: v for k, v in writer_result.items() if k != "prompt"})
    article_text = writer_result["text"]

    sections = trial07.split_five_voice_sections(article_text)
    if sections is None:
        save_json(f"{AUDIT_DIR}/structure_check_failed.json",
                  {"article_text": article_text})
        raise RuntimeError(
            "[STRUCTURE_MISMATCH] Writer出力が5区切り構造(##見出し1つ→###見出し2つ→"
            "##見出し2つ)として解析できません。USER_DECISION_REQUIREDとして報告します。")

    print("[A2-TRIAL02][Editor] Evidence Compression(Lossless Editing)適用...")
    ec_result = run_evidence_compression(client, article_text, writer_model)
    with open(f"{AUDIT_DIR}/evidence_compression_prompt.txt", "w", encoding="utf-8") as f:
        f.write(ec_result["prompt"])
    save_json(f"{AUDIT_DIR}/evidence_compression_result.json",
              {k: v for k, v in ec_result.items() if k != "prompt"})
    ec_sections = trial07.split_five_voice_sections(ec_result["text"])
    if ec_sections is not None:
        article_text = ec_result["text"]
        sections = ec_sections
        print("[A2-TRIAL02][Editor] Evidence Compression適用後も5区切り構造を維持(採用)。")
    else:
        print("[A2-TRIAL02][Editor] Evidence Compression出力が5区切り構造として解析できな"
              "かったため、Editor適用前のWriter出力をそのまま採用します(Editorはoptionalな"
              "軽量化工程のため、構造破壊時は不採用としてfail-safeに倒す)。")

    with open(f"{A2_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)
    save_json(f"{A2_DIR}/parts.json", b1prod.build_parts(article_text))

    stats = compute_section_stats(sections)
    save_json(f"{A2_DIR}/section_stats.json", stats)
    print(f"[A2-TRIAL02] section_stats={ {k: v['word_count'] for k, v in stats.items()} }")

    print("[A2-TRIAL02][Fact Checker] 開始(Web検索あり)...")
    fc_result = run_fact_checker(TOPIC_JA, article_text)
    save_json(f"{AUDIT_DIR}/fact_check.json", fc_result)
    print(f"[A2-TRIAL02][Fact Checker] final_status={fc_result['final_status']} "
          f"verdict={(fc_result['result'] or {}).get('verdict')}")

    print("[A2-TRIAL02][Ledger Deviation] 開始(monitoring専用、Phase 1と同じ用法)...")
    deviation = run_ledger_deviation(client, ledger_text, article_text, writer_model)
    save_json(f"{AUDIT_DIR}/ledger_deviation.json", deviation)
    print(f"[A2-TRIAL02][Ledger Deviation] overall_status={deviation.get('overall_status')} "
          f"deviations={len(deviation.get('deviations', []))}")

    print("[A2-TRIAL02][QA] Point Overlap/Value QA monitoring(Trial-07関数を無変更で再利用)...")
    qa_monitoring = trial07.run_five_section_point_qa_monitoring(client, sections, writer_model, AUDIT_DIR)

    print("[A2-TRIAL02][QA] Analytical Leakage Check(Trial-07関数を無変更で再利用)...")
    leakage = trial07.run_analytical_leakage_check(client, sections, writer_model, "medium", AUDIT_DIR, attempt=1)

    summary = {
        "b1_article_path": B1_ARTICLE_PATH,
        "writer_model": writer_result["model"],
        "evidence_compression_adopted": (ec_sections is not None),
        "b1_stats": {k: v["word_count"] for k, v in b1_stats.items()},
        "a2_stats": {k: v["word_count"] for k, v in stats.items()},
        "fact_check_final_status": fc_result["final_status"],
        "fact_check_verdict": (fc_result["result"] or {}).get("verdict"),
        "ledger_deviation_overall_status": deviation.get("overall_status"),
        "ledger_deviation_count": len(deviation.get("deviations", [])),
        "point_overlap_lexical_flagged": qa_monitoring["lexical_flagged"],
        "point_value_qa_flagged": qa_monitoring["value_qa_flagged"],
        "analytical_leakage_any_flagged": leakage["any_flagged"],
    }
    save_json(f"{A2_DIR}/step1_summary.json", summary)
    print(f"[A2-TRIAL02] Step 1完了。summary={summary}")
    return summary


if __name__ == "__main__":
    main()
