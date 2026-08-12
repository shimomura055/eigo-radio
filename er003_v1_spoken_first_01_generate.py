# ============================================================
# er003_v1_spoken_first_01_generate.py
# ER-003-SPOKEN-FIRST-01: ADD03 Listening-first小規模検証
# ============================================================
# ER-003-EN-DIRECT-VFL-02でFact Check PASSとなったADD03 VFL English
# Article(Version V)を、新規Web researchなしに、既存のVerified Fact
# Ledgerだけを事実源としてListening-first rewrite(Version L)する。
#
# 2段階:
#   Step1: Number Classification(構造化出力)。Version V中の主要数字を
#          ANCHOR/SUPPORTING/DISPENSABLE、EXACT_REQUIRED/APPROXIMATE_OK/
#          DIRECTION_ONLYへ分類し、listening-first treatment案と理由を出す。
#   Step2: Rewrite(Web検索なし)。Version V + Verified Fact Ledger +
#          分類結果 + Listening-first原則を入力し、Version Lを生成する。
# 生成後、独立Fact Checker(Web検索あり、r3ロジック再利用)とLedger
# Deviation Check(vfl01ロジック再利用)をVersion Lに対して実行する。
#
# Production(er002_ja_article_generation.py等)・VFL関連スクリプトは
# 一切変更せず、この独立スクリプトから関数を読み取り専用でimportする。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_spoken_first_01_generate.py

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01

load_dotenv()

TOPIC = "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応"
BASE_ARTICLE_PATH = "er003_output/en_direct_vfl_02/ADD03/article.md"
VERIFIED_LEDGER_TEXT_PATH = "er003_output/en_direct_vfl_02/ADD03/verified_fact_ledger.txt"
OUT_DIR = "er003_output/spoken_first_01/ADD03"

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT


def get_client():
    return vfl01.get_client()


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Step 1: Number Classification(構造化出力、Web検索なし。既存の
# Version V本文とVerified Fact Ledgerだけを読んで分類する)
# ============================================================
CLASSIFICATION_JSON_SCHEMA = {
    "name": "number_classification",
    "schema": {
        "type": "object",
        "properties": {
            "numbers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "original": {"type": "string"},
                        "classification": {"type": "string", "enum": ["ANCHOR", "SUPPORTING", "DISPENSABLE"]},
                        "exactness": {"type": "string", "enum": ["EXACT_REQUIRED", "APPROXIMATE_OK", "DIRECTION_ONLY"]},
                        "listening_first_treatment": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": ["original", "classification", "exactness", "listening_first_treatment", "reason"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["numbers"],
        "additionalProperties": False,
    },
    "strict": True,
}

CLASSIFICATION_DEVELOPER_MESSAGE = (
    "あなたはListening-first編集のための数字分類担当です。記事を書き直さず、"
    "既存記事中の数字だけを分類してください。"
)

CLASSIFICATION_PROMPT_TEMPLATE = """以下の記事本文(Version V)中の主要な数字を分類してください。

【対象記事(Version V)】
{article_text}

【この記事のVerified Fact Ledger(数字のscope・正確な出所)】
{ledger_text}

【分類の観点】
各数字について:

1. classification:
   - ANCHOR: ニュース理解に不可欠
   - SUPPORTING: 理解を補強するが必須ではない
   - DISPENSABLE: Factとして正しいが、耳で理解する記事には不要

2. exactness:
   - EXACT_REQUIRED: 正確な数値そのものが重要
   - APPROXIMATE_OK: 概数で意味が変わらない
   - DIRECTION_ONLY: 正確な数値よりも変化の方向(上昇/下落等)が重要

3. listening_first_treatment: 音声原稿でどう扱うべきかの具体案
   (例: "nearly 10 percent"、"about $85"、"prices still finished higher"、
   "on the following day"等。丸め・方向化・省略のいずれでもよい)

4. reason: なぜその分類・扱いにしたかの理由

対象は記事本文中に実際に登場する数字表現(パーセント・金額・時刻・経過時間等)
とし、Verified Fact Ledgerに存在しない数字を新たに作らないでください。"""


def run_classification(client, article_text: str, ledger_text: str) -> dict:
    prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(article_text=article_text, ledger_text=ledger_text)
    response = client.responses.create(
        model=MODEL,
        reasoning={"effort": REASONING_EFFORT},
        text={"format": {"type": "json_schema", **CLASSIFICATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": CLASSIFICATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model, "response_id": response.id}


# ============================================================
# Step 2: Listening-first Rewrite(Web検索なし)
# ============================================================
REWRITE_DEVELOPER_MESSAGE = "英語の記事を作成してください。"

REWRITE_PRINCIPLES = """【Listening-first原則】
A. Fact Ledgerは削らない。あなたが行うのは、音声本文で何を表面化するかを選ぶ編集であり、Factを捨てることではない
B. 数字はANCHOR(必須)/SUPPORTING(補強)/DISPENSABLE(不要)に分けて扱う(下記の分類結果を参照)
C. 数字ごとにEXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLYの扱いを踏まえる(下記の分類結果を参照)
D. 正確な数値そのものが本質でない場合、rose/fell/jumped/eased/remained high/briefly dropped/finished higher等、変化の方向性を優先する
E. Exactnessが不要な場合は丸めてよい(例: 9.59%→nearly 10%、$84.73→about $85)。ただし丸めによって意味が変わらないこと
F. 数字を直感的な比喩・換算表現へ変換してよいが、元の数字より理解が簡単になる場合だけ使う。無理な比喩は禁止。換算結果は新しいFactになるため、Verified Fact Ledgerで裏付けられる範囲に限る
G. 一つの文、または一つの短い意味ブロックで、聞き手が同時に比較しなければならない主要数字は原則2つ以内とする(記事全体でのhard capではない)
H. million/billion、percent/percentage point等の単位を連続させすぎない。必要なら単位を揃える・丸める・relative changeへ変換する

【禁止事項】
- Verified Ledger外の具体的Factを追加しない
- 数字のscopeを変更しない(例: 全体の数字を特定条件の数字であるかのように書き換えない)
- 時系列を変更しない(7/13が先、7/14が後)
- 因果関係を強化しない(Ledgerが因果を明示していない箇所に因果を持ち込まない)
- Sourceにない比喩的Factを創作しない
- Fact accuracyのために記事を無味乾燥にしない(阪神マスター由来の勢い・切り口・締めの印象は維持する)"""

REWRITE_PROMPT_TEMPLATE = """以下は、Fact精度を確認済みの既存記事(Version V)です。これをListening-first
(耳で一度聞いて理解しやすい)版(Version L)へ書き換えてください。

新しい調査は行わず、以下のVerified Fact Ledgerの範囲内だけで書き換えてください。

【Version V(書き換え対象)】
{article_text}

【Verified Fact Ledger】
{ledger_text}

【数字分類の結果(Step1の分析、書き換えの参考にすること)】
{classification_summary}

{principles}

【出力形式】
Version Vと同じMarkdown構造(Title、本文、###見出しをちょうど2つ持つPoint、
In One Line相当の結び)を維持してください。Point部分の見出しは、Version Vの
内容と対応させてください。"""


def build_classification_summary(classification_parsed: dict) -> str:
    lines = []
    for n in classification_parsed["numbers"]:
        lines.append(
            f"- {n['original']} | {n['classification']} | {n['exactness']} | "
            f"提案: {n['listening_first_treatment']} | 理由: {n['reason']}"
        )
    return "\n".join(lines)


def run_rewrite(client, article_text: str, ledger_text: str, classification_summary: str) -> dict:
    prompt = REWRITE_PROMPT_TEMPLATE.format(
        article_text=article_text, ledger_text=ledger_text,
        classification_summary=classification_summary, principles=REWRITE_PRINCIPLES,
    )
    response = client.responses.create(
        model=MODEL,
        reasoning={"effort": REASONING_EFFORT},
        input=[
            {"role": "developer", "content": REWRITE_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("rewrite応答が空です")
    return {"prompt": prompt, "raw_text": text, "model": response.model, "response_id": response.id}


def run_rewrite_with_technical_retry(client, article_text: str, ledger_text: str,
                                      classification_summary: str, max_attempts: int = 2) -> dict:
    import er002_ja_free_markdown_restore_r2 as restore_r2
    attempts = []
    for attempt in range(1, max_attempts + 1):
        try:
            result = run_rewrite(client, article_text, ledger_text, classification_summary)
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}"})
            if attempt < max_attempts:
                time.sleep(2)
                continue
            return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}
        structure = restore_r2.validate_point_structure(result["raw_text"])
        attempts.append({
            "attempt": attempt, "status": structure.status, "model": result["model"],
            "response_id": result["response_id"], "h3_count": structure.h3_count,
            "headings": structure.headings, "raw_text": result["raw_text"],
        })
        if structure.status == "STRUCTURE_PASS":
            return {"status": "STRUCTURE_PASS", "attempts": attempts, **result}
        if attempt < max_attempts:
            continue
        return {"status": "STRUCTURE_INVALID", "attempts": attempts, **result}
    return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    client = get_client()

    version_v = load_text(BASE_ARTICLE_PATH)
    ledger_text = load_text(VERIFIED_LEDGER_TEXT_PATH)

    # --- Step 1: Number Classification ---
    print("[SF1] Step1: Number Classification呼び出し開始...")
    classification_result = run_classification(client, version_v, ledger_text)
    print(f"[SF1] Step1完了: numbers={len(classification_result['parsed']['numbers'])}")
    with open(f"{OUT_DIR}/number_classification.json", "w", encoding="utf-8") as f:
        json.dump(classification_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/classification_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in classification_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    classification_summary = build_classification_summary(classification_result["parsed"])

    # --- Step 2: Rewrite ---
    print("[SF1] Step2: Rewrite呼び出し開始...")
    rewrite_result = run_rewrite_with_technical_retry(client, version_v, ledger_text, classification_summary)
    with open(f"{OUT_DIR}/audit/rewrite_attempts.json", "w", encoding="utf-8") as f:
        json.dump(rewrite_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if rewrite_result["status"] != "STRUCTURE_PASS" or not rewrite_result.get("raw_text"):
        print(f"[SF1] rewrite失敗 status={rewrite_result['status']}")
        return

    version_l = rewrite_result["raw_text"]
    with open(f"{OUT_DIR}/version_l.md", "w", encoding="utf-8") as f:
        f.write(version_l)

    v_word_count = ab01.compute_word_count(version_v)
    l_word_count = ab01.compute_word_count(version_l)
    print(f"[SF1] Version V word_count={v_word_count}  Version L word_count={l_word_count}")

    # --- 独立fact checker(Version Lに対して。r3ロジックをそのまま再利用) ---
    print("[SF1] fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, version_l, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[SF1] fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{OUT_DIR}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    # --- Ledger逸脱チェック(vfl01ロジックをそのまま再利用) ---
    print("[SF1] ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(client, ledger_text, version_l)
    print(f"[SF1] deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{OUT_DIR}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    summary = {
        "version_v_word_count": v_word_count, "version_l_word_count": l_word_count,
        "rewrite_technical_attempts": len(rewrite_result["attempts"]),
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
    }
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("[SF1] 完了。summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
