# ============================================================
# er003_v1_iran01_articles_generate.py
# ER-003-IRAN-A2-B1-01: IRAN01 B2/A2記事生成(共通Ledgerから)
# ============================================================
# ER-003-CEFR-DIRECT-02で確立したCOMMON_BLOCK_TEMPLATE(Hanshin
# masterによるスタイル参照+Verified Fact Ledgerのみを事実源とする
# Direct Generation方式)と、B2_V2_INSTRUCTION/A2_KAI1_INSTRUCTION
# (Cognitive Load Reduction)を、そのまま再利用する。新しい生成
# ロジック・instructionは作らない。1つの共通Ledgerから、B2とA2を
# それぞれ独立したWriter呼び出しで生成する(B1はB2をそのまま使うため
# 別生成しない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_articles_generate.py

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

TOPIC_ID = "IRAN01"
TOPIC = ("最新のイラン情勢: Trump大統領がホルムズ海峡を「米国の領土にするかもしれない」と発言する一方、"
         "実際にはイランとオマーンが海峡再開に向けた技術的な航行ルート合意を発表した(2026年8月15日)")
LEDGER_TEXT_PATH = "er003_output/novel_audio_02/IRAN01/research/verified_fact_ledger.txt"
OUT_DIR = "er003_output/novel_audio_02/IRAN01"

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
# 共通prompt block(ER-003-CEFR-DIRECT-02から無変更で継承)
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
- 背景にある広い戦争全体の経緯の詳細
- 補助的な数値
- 別角度の解釈
- 交渉の細部
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
- 戦争全体の経緯を必要以上に列挙すること

Point One・Point Twoの長さの目標は、それぞれ30〜60語、許容範囲は25〜70語です(hard capでは
ありません)。この範囲から外れる場合、なぜその長さが必要か、targetへ収めると何を失うかを、
後で説明できるように意識して書いてください。語数合わせのために内容や自然さを壊さないでください。

【記事全体の長さについて】
記事全体の総語数は、280〜420語程度を観察用の目安としてよいですが、hard capではありません。
今回最も重要なのは中心angle(Trump発言 対 イラン・オマーンの技術合意)を明確に伝えることで
あり、語数に合わせるための不自然な削除・追加はしないでください。

【Spoken-first原則(数字の扱い)】
A. Fact Ledgerにある数字を恣意的に削らない。あなたが行うのは、聞いて理解しやすい形で数字を
   どう表面化するかという編集判断であり、Factを捨てることではない
B. 正確な数値そのものが本質でない場合、rose/fell/collapsed/eased等、変化の方向性を優先してよい
C. Exactnessが不要な場合は丸めてよい(例: 84.11ドル→about 84 dollars)。ただし丸めによって
   意味が変わらないこと
D. 一つの文、または一つの短い意味ブロックで、聞き手が同時に比較しなければならない主要数字は
   原則2つ以内とする(記事全体でのhard capではない)
E. 単位を連続させすぎない
F. 船舶通航量の落差(開戦前後)は本記事のANCHOR数値であり、丸めすぎて対比が消えないよう注意する

【今回のFact源について(重要)】
今回は、あなた自身によるWeb検索や新しい具体的事実の追加を行わないでください。
以下のVerified Fact Ledgerだけを事実源として使用してください。

{verified_ledger_text}

【Fact Ledger使用上の制約】
- Verified Fact Ledgerにない具体的Factを追加しないでください
- [DISPUTED]と印のあるFactは、どちらか一方が正しいと断定しないでください。両者の主張として
  併記するか、対立がある事実として扱ってください
- [GOV_CLAIM]は、実際に起きた事実ではなく「その人物・政府がそう述べた」という発言の事実として
  書いてください
- [AGREEMENT_UNDER_NEGOTIATION]は、確定した合意内容であるかのように断定しないでください
- 「この記事で意図的に扱わない情報」に列挙された内容(死傷者数、核問題詳細、国内政治等)は、
  本記事の中心angleではないため、本文・Pointいずれにも詳しく書き込まないでください
- 複数のFactを物語として自然にまとめてもかまいませんが、Fact同士の関係(誰が・何を・いつ・
  どの範囲で)を変えないでください

【Fact Safety上、特に重要な区別(今回のFact safety共通ルール)】
- confirmed factと、政府・当事者の主張(claim)を混同しないでください。「Iran says」と
  「... happened」を同じ確からしさで書かないでください
- 米国側・イラン側それぞれの「自分が海峡を支配している」という主張は、どちらも「そう主張して
  いる」という事実としてのみ扱い、実際にどちらが正しいかを記事内で判定しないでください
- 交渉中の合意・提案を、確定した停戦・協定であるかのように書かないでください
- 単一情報源のみに基づく数字を、唯一の確定値であるかのように断定しないでください(FACT-06の
  ように複数の集計が存在する場合は、幅を持たせるか出典を示してください)
"""


def build_common_block(master_full_text: str, verified_ledger_text: str) -> str:
    return COMMON_BLOCK_TEMPLATE.format(
        hanshin_master_full_text=master_full_text, topic=TOPIC,
        verified_ledger_text=verified_ledger_text,
    )


# ER-003-CEFR-DIRECT-02から無変更で継承
B2_V2_INSTRUCTION = ("Write this as a B2-level English news story for listening. Keep it close to the "
                     "quality and richness of natural English written for adults. The listener should be "
                     "able to follow normal news-style reasoning, some abstract ideas, and some idiomatic "
                     "or expressive language without everything being explained. Simplify only where the "
                     "expression would create unnecessary difficulty for an upper-intermediate learner. "
                     "Preserve the article's personality, rhythm, and interesting turns of phrase as much "
                     "as possible.")

A2_KAI1_INSTRUCTION = """Write this as an A2-level English news story for listening. The listener should be able to understand the main events and why they matter even if their English is still limited. Present information in a clear sequence, make relationships between events explicit, and avoid making the listener hold several ideas in mind at once. Use simple, natural English and explain difficult concepts in an everyday way. Rebuild difficult parts freely rather than trying to preserve sophisticated sentence structures or phrasing.

Keep each step of the story mentally light. Introduce one main idea at a time, and do not ask the listener to connect several facts, conditions, or contrasts inside the same sentence or short passage. When a sentence carries more than one important idea, separate those ideas and explain them in a simpler order. Prefer clear cause-and-result or before-and-after relationships over compressed explanation.

Keep the story interesting and adult in subject matter. It should sound like real spoken news, not children's English or a classroom exercise."""


def build_prompt(common_block: str, instruction: str) -> str:
    return common_block + "\n【難易度指示】\n" + instruction


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")


def compute_metrics(text: str) -> dict:
    flat = " ".join(line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
    word_count = ab01.compute_word_count(flat)
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(flat) if s.strip()]
    sentence_count = len(sentences) if sentences else 1
    sentence_lengths = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences] or [word_count]
    avg_len = round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0
    max_len = max(sentence_lengths) if sentence_lengths else 0
    return {"word_count": word_count, "sentence_count": sentence_count,
            "avg_sentence_length": avg_len, "max_sentence_length": max_len}


def run_one_pattern(client, label: str, prompt: str, verified_ledger_text: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"[IRAN01-ARTICLES] {label}: writer呼び出し開始...")
    writer_result = vfl01.run_writer_with_technical_retry(client, prompt)
    with open(f"{out_dir}/audit/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(writer_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
        print(f"[IRAN01-ARTICLES] {label}: writer失敗 status={writer_result['status']}")
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
    print(f"[IRAN01-ARTICLES] {label}: metrics={metrics} sections={section_wc}")

    print(f"[IRAN01-ARTICLES] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[IRAN01-ARTICLES] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    print(f"[IRAN01-ARTICLES] {label}: ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text)
    print(f"[IRAN01-ARTICLES] {label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
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
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    client = vfl01.get_client()

    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = load_text(LEDGER_TEXT_PATH)
    common_block = build_common_block(master_full_text, verified_ledger_text)

    results = {}
    for label, instruction, out_dir in [
        ("B2", B2_V2_INSTRUCTION, f"{OUT_DIR}/b2"),
        ("A2", A2_KAI1_INSTRUCTION, f"{OUT_DIR}/a2"),
    ]:
        prompt = build_prompt(common_block, instruction)
        result = run_one_pattern(client, label, prompt, verified_ledger_text, out_dir)
        results[label] = result

    with open(f"{OUT_DIR}/articles_run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2, default=str)
    print("[IRAN01-ARTICLES] 完了。")
    for label, r in results.items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')}")


if __name__ == "__main__":
    main()
