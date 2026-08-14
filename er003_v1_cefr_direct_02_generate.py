# ============================================================
# er003_v1_cefr_direct_02_generate.py
# ER-003-CEFR-DIRECT-02: A02 V2 Full-Article Difficulty Calibration
# ============================================================
# ER-003-CEFR-DIRECT-01で有望だったVariation 2(Listening/Cognitive
# Load方式)に絞り、今回はMain Story/Point One/Point Two/In One Line
# を含む完全な記事構成で5版を比較する:
#   B2 V2 / B1 V2 / A2 V2 Original / A2 V2 改1(Cognitive Load
#   Reduction) / A2 V2 改2(Conceptual Rebuilding)
#
# 前回(CEFR-DIRECT-01)本文のみ出力ではPoint相当の情報が本文へ前倒し
# される問題が発生したため、今回は完全記事構成にすることで解消を試みる。
# Direct Generation方式(日本語阪神master + Verified Fact Ledger →
# 各CEFR記事を直接生成)。English MasterはCEFR-DIRECT-01の既存固定版を
# 再利用し、今回writerへは渡さない(比較Artifactでの参照表示のみ)。
#
# Production(CURRENT_SPEC.md、R4 Production prompt、VFL/spoken_first/
# cefr_direct_01関連スクリプト)は一切変更せず、この独立スクリプトから
# 関数を読み取り専用でimportするのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_cefr_direct_02_generate.py

from __future__ import annotations

import json
import os
import re
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_spoken_first_01_r1_generate as sf1r1

load_dotenv()

TOPIC_ID = "A02"
TOPIC = "英国の未成年向け夜間SNS設定"
LEDGER_TEXT_PATH = "er003_output/en_direct_vfl_01/A02/verified_fact_ledger.txt"
OUT_DIR = "er003_output/cefr_direct_02/A02"

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

POINT_TARGET_LOWER = 30
POINT_TARGET_UPPER = 60
POINT_TOLERANCE_LOWER = 25
POINT_TOLERANCE_UPPER = 70
TOTAL_SOFT_LOWER = 280
TOTAL_SOFT_UPPER = 420


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# 共通prompt block
# ============================================================
COMMON_BLOCK_TEMPLATE = """以下は、私が良いと評価している日本語記事です。

【マスター記事】

{hanshin_master_full_text}

【今回のテーマ】

{topic}

この阪神記事が良いのは、全体の概要を面白く展開し、ポイントでは本文とは別の切り口から解説し、
最後に一言でまとめることで、聞き手が飽きない設計になっている点です。

このセンスを活かして、今回のテーマの記事全文をMarkdownで書いてください。

阪神や野球固有の表現をコピーするのではなく、今回の題材に合う表現を使ってください。

【記事構成(重要)】
以下の構成で書いてください:
1. Title(#見出し)
2. Main Story(本文、複数段落)
3. ポイント部分: Markdownの「###」見出しをちょうど2つ置いてください(Point One相当、Point Two相当)
4. In One Line相当の結び(「## In one line…」のような見出しの後に1〜2文の結び)

【Main Storyの役割(重要)】
Main Storyでは、何が起きるのか・誰が対象か・どのような仕組みか・現在どういう状態か、という
ニュースの核心だけを伝えてください。以下は、Point One/Point Twoで扱うべき内容であり、Main
Storyへ必要以上に入れないでください:
- pilot調査の詳細
- 補助的な数値
- 別角度の解釈
- study limitations
- deeper implications
これらを詰め込むためにMain Storyを不自然に長くしないでください。

【Point One / Point Twoの役割(重要、Point Balance原則)】
Point One・Point Twoは、本文の再説明ではなく、以下のいずれかを短く提示する場所です:
- 本文とは別の切り口
- 示唆
- 背景
- 意味づけ
- 聞き手が「なるほど」と思える補助線

禁止:
- 本文の長い再説明
- Fact Ledgerの詳細を網羅的に再掲すること
- Point内で新しい第二のニュース本文を作ること
- 研究方法や制約を必要以上に列挙すること

Point One・Point Twoの長さの目標は、それぞれ30〜60語、許容範囲は25〜70語です(hard capでは
ありません)。この範囲から外れる場合、なぜその長さが必要か、targetへ収めると何を失うかを、
後で説明できるように意識して書いてください。語数合わせのために内容や自然さを壊さないでください。

【記事全体の長さについて】
記事全体の総語数は、280〜420語程度を観察用の目安としてよいですが、hard capではありません。
今回最も重要なのはCEFR難易度差を作ることであり、語数に合わせるための不自然な削除・追加は
しないでください。低いレベルでは、難しい概念を複数の簡単な文へ展開した方が理解しやすい場合が
あるため、語数が他レベルより多くなること自体は問題ありません。

【Spoken-first原則(数字の扱い)】
A. Fact Ledgerにある数字を恣意的に削らない。あなたが行うのは、聞いて理解しやすい形で数字を
   どう表面化するかという編集判断であり、Factを捨てることではない
B. 正確な数値そのものが本質でない場合、rose/fell/jumped/eased/remained high等、変化の方向性を
   優先してよい
C. Exactnessが不要な場合は丸めてよい(例: 9.59%→nearly 10%)。ただし丸めによって意味が
   変わらないこと
D. 一つの文、または一つの短い意味ブロックで、聞き手が同時に比較しなければならない主要数字は
   原則2つ以内とする(記事全体でのhard capではない)
E. 単位(million/billion、percent/percentage point等)を連続させすぎない

【今回のFact源について(重要)】
今回は、あなた自身によるWeb検索や新しい具体的事実の追加を行わないでください。
以下のVerified Fact Ledgerだけを事実源として使用してください。

{verified_ledger_text}

【Fact Ledger使用上の制約】
- Verified Fact Ledgerにない具体的Factを追加しないでください
- 数字を別のscopeへ結び付けないでください(例: 全体の参加者数を特定の条件群の人数として書かない)
- 時間条件を別の制度項目へ拡張しないでください
- [AMBIGUOUS]と印のあるFactは断定しないでください。曖昧さを保ったまま書くか、記事から省いてください
- 複数のFactを物語として自然にまとめてもかまいませんが、Fact同士の関係(誰が・何を・いつ・どの範囲で)を変えないでください
- Sourceにない導入の場面描写(scene-setting)自体は使ってかまいません。ただし、その場面描写に具体的なFact claim(数字・制度の適用条件等)を接続しないでください

【Fact Safety上、特に重要な区別(今回のFact safety共通ルール)】
- policyとpilotを混同しないでください。pilotは既に完了した別の研究であり、今回の政策案そのものが現在試験中であるかのように書かないでください
- 実施済みのpilot結果を、将来のpolicyの効果として断定しないでください
- correlation(相関)・reported result(報告された結果)・causation(因果)を区別してください
- default setting(初期設定でオン、変更可能)とaccess block(アクセス自体の遮断)を混同しないでください
- Ledgerにない因果関係や一般化を追加しないでください
"""


def build_common_block(master_full_text: str, verified_ledger_text: str) -> str:
    return COMMON_BLOCK_TEMPLATE.format(
        hanshin_master_full_text=master_full_text, topic=TOPIC,
        verified_ledger_text=verified_ledger_text,
    )


B2_V2_INSTRUCTION = "Write this as a B2-level English news story for listening. Keep it close to the quality and richness of natural English written for adults. The listener should be able to follow normal news-style reasoning, some abstract ideas, and some idiomatic or expressive language without everything being explained. Simplify only where the expression would create unnecessary difficulty for an upper-intermediate learner. Preserve the article's personality, rhythm, and interesting turns of phrase as much as possible."

B1_V2_INSTRUCTION = "Write this as a B1-level English news story for listening. The listener should be able to understand the main story and the two key angles without having to unpack complicated sentences or infer too much from abstract wording. Keep the ideas adult and interesting, but make the path from one idea to the next more explicit. Prefer clear, direct explanations over compressed or highly idiomatic phrasing. If a difficult idea can be expressed more simply, simplify the idea itself, not just the vocabulary."

A2_ORIGINAL_INSTRUCTION = "Write this as an A2-level English news story for listening. The listener should be able to understand the main events and why they matter even if their English is still limited. Present information in a clear sequence, make relationships between events explicit, and avoid making the listener hold several ideas in mind at once. Use simple, natural English and explain difficult concepts in an everyday way. Rebuild difficult parts freely rather than trying to preserve sophisticated sentence structures or phrasing. Keep the story interesting and adult in subject matter."

A2_KAI1_INSTRUCTION = """Write this as an A2-level English news story for listening. The listener should be able to understand the main events and why they matter even if their English is still limited. Present information in a clear sequence, make relationships between events explicit, and avoid making the listener hold several ideas in mind at once. Use simple, natural English and explain difficult concepts in an everyday way. Rebuild difficult parts freely rather than trying to preserve sophisticated sentence structures or phrasing.

Keep each step of the story mentally light. Introduce one main idea at a time, and do not ask the listener to connect several facts, conditions, or contrasts inside the same sentence or short passage. When a sentence carries more than one important idea, separate those ideas and explain them in a simpler order. Prefer clear cause-and-result or before-and-after relationships over compressed explanation.

Keep the story interesting and adult in subject matter. It should sound like real spoken news, not children's English or a classroom exercise."""

A2_KAI2_INSTRUCTION = """Write this as an A2-level English news story for listening. The listener should be able to understand the main events and why they matter even if their English is still limited. Present information in a clear sequence and use simple, natural English.

Do not keep a difficult idea just because it is expressed with easy words. If an idea, comparison, policy detail, or explanation would still be hard for an A2 listener to follow, rebuild it in a simpler form. Explain what is happening first, then explain why it matters. Prefer concrete actions and everyday explanations over abstract summaries. Make important relationships explicit instead of expecting the listener to infer them. It is acceptable to simplify the way an idea is presented, as long as the important facts and meaning remain correct.

The listener should rarely need to stop and decode a sentence before understanding the story. Keep the subject matter adult and the writing engaging, but make comprehension noticeably easier than the B1 version."""

PATTERNS = [
    ("B2_v2", B2_V2_INSTRUCTION),
    ("B1_v2", B1_V2_INSTRUCTION),
    ("A2_original", A2_ORIGINAL_INSTRUCTION),
    ("A2_kai1", A2_KAI1_INSTRUCTION),
    ("A2_kai2", A2_KAI2_INSTRUCTION),
]


def build_prompt(common_block: str, instruction: str) -> str:
    return common_block + "\n【難易度指示】\n" + instruction


# ============================================================
# Metrics(参考値のみ)
# ============================================================
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")


def compute_metrics(text: str) -> dict:
    # コードフェンス等は本記事では使わないため単純split
    flat = " ".join(line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
    word_count = ab01.compute_word_count(flat)
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(flat) if s.strip()]
    sentence_count = len(sentences) if sentences else 1
    sentence_lengths = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences] or [word_count]
    avg_len = round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0
    max_len = max(sentence_lengths) if sentence_lengths else 0
    return {
        "word_count": word_count, "sentence_count": sentence_count,
        "avg_sentence_length": avg_len, "max_sentence_length": max_len,
    }


# ============================================================
# 1版のFull pipeline(writer -> fact check -> ledger deviation)
# ============================================================
def run_one_pattern(client, label: str, prompt: str, verified_ledger_text: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"[CEFR-DIRECT-02] {label}: writer呼び出し開始...")
    writer_result = vfl01.run_writer_with_technical_retry(client, prompt)
    with open(f"{out_dir}/audit/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(writer_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
        print(f"[CEFR-DIRECT-02] {label}: writer失敗 status={writer_result['status']}")
        return {"label": label, "status": writer_result["status"], "article_text": None}

    article_text = writer_result["raw_text"].strip()
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    metrics = compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": POINT_TARGET_LOWER <= section_wc["point_one"] <= POINT_TARGET_UPPER,
        "point_one_within_tolerance": POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= POINT_TOLERANCE_UPPER,
        "point_two_within_target": POINT_TARGET_LOWER <= section_wc["point_two"] <= POINT_TARGET_UPPER,
        "point_two_within_tolerance": POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= POINT_TOLERANCE_UPPER,
        "total_within_soft_range": TOTAL_SOFT_LOWER <= metrics["word_count"] <= TOTAL_SOFT_UPPER,
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print(f"[CEFR-DIRECT-02] {label}: metrics={metrics} sections={section_wc}")

    print(f"[CEFR-DIRECT-02] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[CEFR-DIRECT-02] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    print(f"[CEFR-DIRECT-02] {label}: ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text)
    print(f"[CEFR-DIRECT-02] {label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "writer_technical_attempts": len(writer_result["attempts"]),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    client = vfl01.get_client()

    master_ja_full_text = vfl01.load_master_full_text()
    verified_ledger_text = load_text(LEDGER_TEXT_PATH)
    common_block = build_common_block(master_ja_full_text, verified_ledger_text)

    summary = {}
    for label, instruction in PATTERNS:
        prompt = build_prompt(common_block, instruction)
        out_dir = f"{OUT_DIR}/{label}"
        result = run_one_pattern(client, label, prompt, verified_ledger_text, out_dir)
        summary[label] = {k: v for k, v in result.items() if k != "article_text"}

    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[CEFR-DIRECT-02] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
