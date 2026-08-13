# ============================================================
# er003_v1_cefr_direct_01_generate.py
# ER-003-CEFR-DIRECT-01: A02 3-Level x 3-Variation Direct Difficulty Test
# ============================================================
# 目的: 語彙リスト・平均文長・禁止構文等の機械的制約ではなく、自然言語
# による難易度指示だけで、A2/B1/B2の自然かつ明確なレベル差を作れるかを
# 検証する。比較Volume削減のため、記事の「本文部分のみ」(Point One/
# Point Two/In One Lineを除く)を対象とする。
#
# 3方式:
#   V1 Reader Profile     — 英語マスターをwriterへ見せない
#   V2 Listening/Cognitive Load — 同上
#   V3 English Master Distance  — 固定の英語マスター本文をwriterへ入力
#
# 英語マスター(本文のみ)は1版だけ生成し、全比較で共有する(Variation
# ごとに作り直さない)。
#
# Production(CURRENT_SPEC.md、R4 Production prompt、VFL/spoken_first関連
# スクリプト)は一切変更せず、この独立スクリプトから関数を読み取り専用で
# importするのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_cefr_direct_01_generate.py

from __future__ import annotations

import json
import os
import re
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01

load_dotenv()

TOPIC_ID = "A02"
TOPIC = "英国の未成年向け夜間SNS設定"
LEDGER_TEXT_PATH = "er003_output/en_direct_vfl_01/A02/verified_fact_ledger.txt"
OUT_DIR = "er003_output/cefr_direct_01/A02"

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

WRITER_DEVELOPER_MESSAGE = vfl01.WRITER_DEVELOPER_MESSAGE  # "英語の記事を作成してください。"

LEVELS = ["A2", "B1", "B2"]
VARIATIONS = ["v1", "v2", "v3"]


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# 共通prompt blockの構築
# ============================================================
COMMON_BLOCK_TEMPLATE = """以下は、私が良いと評価している日本語記事です。

【マスター記事】

{hanshin_master_full_text}

【今回のテーマ】

{topic}

この阪神記事が良いのは、全体の概要を面白く展開し、ポイントでは本文とは別の切り口から解説し、
最後に一言でまとめることで、聞き手が飽きない設計になっている点です。

このセンスを活かして、今回のテーマの記事を書いてください。

阪神や野球固有の表現をコピーするのではなく、今回の題材に合う表現を使ってください。

【今回、出力するのは本文部分のみです(重要)】
通常であれば、この記事は「本文(Intro/Full Story)→Point One→Point Two→In One Line」という
完全な構成を持ちます。今回は比較のため、本文部分だけを出力してください。ただしこれは
「Pointが存在しない短縮記事」を新たに設計することではありません。あなたは、通常通り
Point One・Point Two・In One Lineが後に続くことを前提として本文を書き、その本文部分だけを
出力してください。

具体的に、以下は禁止します:
- Pointで扱う予定だった補足Factを本文へ前倒しすること
- Pointが無い分、本文を情報過多にすること
- In One Lineの結論を本文末尾へ無理に統合すること
- 本文だけで記事を完全完結させようとして説明を増やすこと

Markdownの見出し(#/##/###)やタイトル行、Point相当の段落は書かないでください。本文部分の
段落だけをMarkdownのプレーンな段落として出力してください。

【今回のFact源について(重要)】
今回は、あなた自身によるWeb検索や新しい具体的事実の追加を行わないでください。
以下のVerified Fact Ledgerだけを事実源として使用してください。

{verified_ledger_text}

【Fact Ledger使用上の制約】
- Verified Fact Ledgerにない具体的Factを追加しないでください
- 数字を別のscopeへ結び付けないでください(例: 全体の参加者数を特定の条件群の人数として書かない)
- 時間条件を別の制度項目へ拡張しないでください(例: ある制度がmidnight-6amに限定されるとしても、別の制度項目まで同じ時間帯に限定されるとは書かない)
- [AMBIGUOUS]と印のあるFactは断定しないでください。曖昧さを保ったまま書くか、記事から省いてください
- 複数のFactを物語として自然にまとめてもかまいませんが、Fact同士の関係(誰が・何を・いつ・どの範囲で)を変えないでください
- Sourceにない導入の場面描写(scene-setting)自体は使ってかまいません。ただし、その場面描写に具体的なFact claim(数字・制度の適用条件等)を接続しないでください
"""


def build_common_block(master_full_text: str, verified_ledger_text: str) -> str:
    return COMMON_BLOCK_TEMPLATE.format(
        hanshin_master_full_text=master_full_text, topic=TOPIC,
        verified_ledger_text=verified_ledger_text,
    )


MASTER_DIFFICULTY_INSTRUCTION = """【難易度について】
今回は特定のCEFRレベルを狙わず、制約のない自然な英語記事として書いてください。読者は英語
ニュースを日常的に読む成人とします。語彙・構文・比喩表現を難易度のために抑制する必要は
ありません。これは今回の比較における基準版(English Master)として使います。"""


VARIATION_1_INSTRUCTIONS = {
    "B2": "Write the article in natural English for an upper-intermediate English learner. Keep the tone, energy, and editorial quality of a normal adult news feature as much as possible. The reader should feel that this is real English, not simplified textbook English. You may use some sophisticated vocabulary, idiomatic phrasing, and varied sentence structures when they sound natural, as long as the meaning remains easy to follow from context.",
    "B1": "Write the article in natural English for an intermediate English learner. It should still feel like an engaging news article for adults, but make the ideas easier to follow than in the original natural-English version. Prefer direct wording, familiar expressions, and clear sentence structures. When an idea is complex, explain it in a simpler way rather than preserving the original phrasing. Keep the article lively and natural, not textbook-like.",
    "A2": "Write the article in natural English for a learner who can understand everyday English but may struggle with complex news language. Make the story easy to follow on the first listen. Express one idea clearly before moving to the next, use familiar and concrete language where possible, and explain difficult ideas in simple English. Do not simply replace difficult words in complex sentences; rebuild the explanation when necessary. The result should still sound like a real, interesting news story, not children's English or a language exercise.",
}

VARIATION_2_INSTRUCTIONS = {
    "B2": "Write this as a B2-level English news story for listening. Keep it close to the quality and richness of natural English written for adults. The listener should be able to follow normal news-style reasoning, some abstract ideas, and some idiomatic or expressive language without everything being explained. Simplify only where the original expression would create unnecessary difficulty for an upper-intermediate learner. Preserve the article's personality, rhythm, and interesting turns of phrase as much as possible.",
    "B1": "Write this as a B1-level English news story for listening. The listener should be able to understand the main story without having to unpack complicated sentences or infer too much from abstract wording. Keep the ideas adult and interesting, but make the path from one idea to the next more explicit. Prefer clear, direct explanations over compressed or highly idiomatic phrasing. If a difficult idea can be expressed more simply, simplify the idea itself, not just the vocabulary.",
    "A2": "Write this as an A2-level English news story for listening. The listener should be able to understand the main events and why they matter even if their English is still limited. Present information in a clear sequence, make relationships between events explicit, and avoid making the listener hold several ideas in mind at once. Use simple, natural English and explain difficult concepts in an everyday way. Rebuild difficult parts freely rather than trying to preserve sophisticated sentence structures or phrasing. Keep the story interesting and adult in subject matter.",
}

VARIATION_3_INSTRUCTIONS = {
    "B2": "Create the B2 version so that it stays very close to the natural English master in tone, sophistication, and editorial style. Simplify only the parts that would be unnecessarily difficult for an upper-intermediate learner. Keep much of the natural phrasing, sentence variety, nuance, and expressive quality. The B2 version should feel like lightly adapted authentic English, not a simplified rewrite.",
    "B1": "Create the B1 version as a clearly easier retelling of the same news story, not as a sentence-by-sentence simplification of the English master. Preserve the facts, interest, and editorial angle, but reorganize or re-explain difficult passages when that makes the story easier to understand. Use natural adult English, but reduce the amount of inference, abstraction, and linguistic complexity required from the listener.",
    "A2": "Create the A2 version as a fresh, simple retelling of the same news story. Do not try to preserve the sentence structure or sophisticated phrasing of the English master. Preserve the important facts and the article's interesting viewpoint, but rebuild the explanation in the clearest natural English you can. The listener should rarely need to decode a difficult sentence before understanding the story. Keep the subject matter suitable for adults, even though the English itself is much easier."
}

VARIATION_INSTRUCTION_MAP = {"v1": VARIATION_1_INSTRUCTIONS, "v2": VARIATION_2_INSTRUCTIONS, "v3": VARIATION_3_INSTRUCTIONS}

MASTER_REFERENCE_BLOCK_TEMPLATE = """【英語マスター本文(参考。この文体からの距離を、レベルに応じて調整してください)】

{master_article_text}

"""


def build_master_prompt(common_block: str) -> str:
    return common_block + "\n" + MASTER_DIFFICULTY_INSTRUCTION


def build_v1_or_v2_prompt(common_block: str, level: str, variation: str) -> str:
    instr = VARIATION_INSTRUCTION_MAP[variation][level]
    return common_block + "\n【難易度指示】\n" + instr


def build_v3_prompt(common_block: str, level: str, master_article_text: str) -> str:
    instr = VARIATION_3_INSTRUCTIONS[level]
    master_block = MASTER_REFERENCE_BLOCK_TEMPLATE.format(master_article_text=master_article_text)
    return common_block + "\n" + master_block + "【難易度指示】\n" + instr


# ============================================================
# 本文のみ構造の検証(見出し行が無いことを確認)
# ============================================================
def validate_body_only_structure(text: str) -> dict:
    heading_lines = [line for line in text.splitlines() if re.match(r"^\s*#{1,6}\s", line)]
    status = "STRUCTURE_PASS" if not heading_lines else "STRUCTURE_INVALID_HEADINGS_PRESENT"
    return {"status": status, "heading_lines": heading_lines}


def run_writer_with_technical_retry(client, prompt: str, max_attempts: int = 2) -> dict:
    attempts = []
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.responses.create(
                model=MODEL,
                reasoning={"effort": REASONING_EFFORT},
                input=[
                    {"role": "developer", "content": WRITER_DEVELOPER_MESSAGE},
                    {"role": "user", "content": prompt},
                ],
            )
            text = response.output_text
            if not text or not text.strip():
                raise RuntimeError("writer応答が空です")
            model_id, response_id = response.model, response.id
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}"})
            if attempt < max_attempts:
                time.sleep(2)
                continue
            return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}
        structure = validate_body_only_structure(text)
        attempts.append({
            "attempt": attempt, "status": structure["status"], "model": model_id,
            "response_id": response_id, "heading_lines": structure["heading_lines"], "raw_text": text,
        })
        if structure["status"] == "STRUCTURE_PASS":
            return {"status": "STRUCTURE_PASS", "attempts": attempts, "raw_text": text,
                    "model": model_id, "response_id": response_id}
        if attempt < max_attempts:
            continue
        return {"status": "STRUCTURE_INVALID", "attempts": attempts, "raw_text": text,
                "model": model_id, "response_id": response_id}
    return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}


# ============================================================
# Metrics(参考値のみ、合否判定には使わない)
# ============================================================
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")


def compute_metrics(text: str) -> dict:
    word_count = ab01.compute_word_count(text)
    flat = " ".join(line.strip() for line in text.splitlines() if line.strip())
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

    print(f"[CEFR-DIRECT] {label}: writer呼び出し開始...")
    writer_result = run_writer_with_technical_retry(client, prompt)
    with open(f"{out_dir}/audit/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(writer_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
        print(f"[CEFR-DIRECT] {label}: writer失敗 status={writer_result['status']}")
        return {"label": label, "status": writer_result["status"], "article_text": None}

    article_text = writer_result["raw_text"].strip()
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    metrics = compute_metrics(article_text)
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"[CEFR-DIRECT] {label}: {metrics}")

    print(f"[CEFR-DIRECT] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[CEFR-DIRECT] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    print(f"[CEFR-DIRECT] {label}: ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text)
    print(f"[CEFR-DIRECT] {label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    return {
        "label": label, "status": "OK", "article_text": article_text, "metrics": metrics,
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

    # --- English Master(本文のみ、難易度制約なし、1版のみ) ---
    master_prompt = build_master_prompt(common_block)
    master_out_dir = f"{OUT_DIR}/english_master"
    master_result = run_one_pattern(client, "ENGLISH_MASTER", master_prompt, verified_ledger_text, master_out_dir)
    summary["english_master"] = {k: v for k, v in master_result.items() if k != "article_text"}

    if master_result["status"] != "OK":
        print("[CEFR-DIRECT] English Master生成に失敗したため中断します。")
        with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
        return

    master_article_text = master_result["article_text"]

    # --- 9パターン(A2/B1/B2 x v1/v2/v3) ---
    for level in LEVELS:
        summary[level] = {}
        for variation in VARIATIONS:
            label = f"{level}_{variation}"
            out_dir = f"{OUT_DIR}/{level}/{variation}"
            if variation == "v3":
                prompt = build_v3_prompt(common_block, level, master_article_text)
            else:
                prompt = build_v1_or_v2_prompt(common_block, level, variation)
            result = run_one_pattern(client, label, prompt, verified_ledger_text, out_dir)
            summary[level][variation] = {k: v for k, v in result.items() if k != "article_text"}

    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[CEFR-DIRECT] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
