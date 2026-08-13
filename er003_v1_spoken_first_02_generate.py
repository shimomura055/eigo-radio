# ============================================================
# er003_v1_spoken_first_02_generate.py
# ER-003-SPOKEN-FIRST-02: A01・A02 Listening-first 横展開検証
# ============================================================
# ER-003-SPOKEN-FIRST-01-R1でADD03に対して成立したListening-first方式
# (Number Classification→Rewrite、Information Budget原則付き)を、A01
# (スポーツ)・A02(制度)へ展開する。新規Web researchは行わず、既存の
# Verified Fact Ledgerだけを事実源として使用する。
#
# R1との違い: 今回は語数のsoft target/上限を**プロンプトへ与えない**
# (観察目的のため、数値に合わせて削る・足す動機を作らない)。
# Listening-first原則とInformation Budget原則のみを適用し、結果として
# 自然に収束する語数を観察する。
#
# Production・VFL関連スクリプト・spoken_first_01/01_r1スクリプトは
# 変更せず、この独立スクリプトから関数を読み取り専用でimportする。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_spoken_first_02_generate.py

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er002_ja_free_markdown_restore_r2 as restore_r2
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_spoken_first_01_generate as sf1
import er003_v1_spoken_first_01_r1_generate as sf1r1

load_dotenv()

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

# Baseの選定理由(best-of選択ではない):
#   A01: ER-003-EN-DIRECT-VFL-02で唯一生成された版(1記事1回の方針、選択の余地なし)
#   A02: ER-003-EN-DIRECT-VFL-01でRun-1/Run-2の2版が存在。両方PASS・
#        deviation 0件で優劣を判断する材料がないため、生成順が早い方
#        (Run-1)を「先に確定した版」として機械的に採用する(内容比較に
#        よる選別=best-ofではなく、生成順という中立的な基準)
ARTICLES = {
    "A01": {
        "topic": "2026年ワールドカップ準決勝のイングランド対アルゼンチン",
        "base_article_path": "er003_output/en_direct_vfl_02/A01/article.md",
        "ledger_text_path": "er003_output/en_direct_vfl_02/A01/verified_fact_ledger.txt",
        "base_label": "VFL(ER-003-EN-DIRECT-VFL-02、唯一の生成版)",
        "focus_instructions": """【この記事(スポーツ)のListening-first重点観点】
- 得点順・決勝点が90+2分だったことなど、試合展開の物語上重要な数字は残す
- shots/shots on target/xG/possession/pass completionのような複数の
  試合統計を並べて読み上げず、「アルゼンチンが終始優勢だった」という
  核心を伝えるのに必要な最小限(1〜2個程度)に絞る。残りはLedgerに保持する
- Messiの年齢(39歳21日)のように、記事の切り口(無得点での試合支配)に
  直接関わる数字は残してよい
- Point Oneで統計をすべて列挙しない""",
    },
    "A02": {
        "topic": "英国の未成年向け夜間SNS設定",
        "base_article_path": "er003_output/en_direct_vfl_01/A02/run1_article.md",
        "ledger_text_path": "er003_output/en_direct_vfl_01/A02/verified_fact_ledger.txt",
        "base_label": "VFL Run-1(ER-003-EN-DIRECT-VFL-01、生成順により機械的に選定。best-ofではない)",
        "focus_instructions": """【この記事(制度)のListening-first重点観点】
- 対象年齢(16・17歳)、時間帯(午前0時〜6時)、施行時期(2027年春)など、
  制度理解に不可欠な数字は残す
- 309(パイロット全体)と81(夜間制限群)について、両方が音声記事の
  理解に本当に必要か検討する。両方残す場合も、聞き手が同時に処理する
  数字を最小限にする書き方を優先する
- "seven in ten"/"around half"のような行動変化の比較は、対比自体が
  記事の主張(初期設定の効果)を支えるため、対比構造は維持することを
  優先しつつ、必要なら丸めてよい
- サンプルの詳細(遵守内訳等)のうち、音声記事の核心理解に不要なものは
  Ledgerに保持したまま本文から省いてよい""",
    },
}

OUT_ROOT = "er003_output/spoken_first_02"


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Rewrite prompt: sf1の原則+sf1r1のInformation Budget原則を流用するが、
# 語数のsoft target/上限は与えない(観察目的のため)
# ============================================================
LISTENING_FIRST_PRINCIPLES_NO_LENGTH_TARGET = sf1.REWRITE_PRINCIPLES + """

【Information Budget原則(ER-003-SPOKEN-FIRST-01-R1から流用)】
- Listening-firstは、説明を追加して分かりやすくする工程ではなく、聞き手が処理しなくてよい情報を減らす工程である
- Base記事にない新しい説明論点を追加しない。Fact Ledgerに存在するという理由だけで詳細を書き足さない
- Pointの核心理解に不要な詳細(法的背景、網羅的な制度説明、因果否定の補足等)は、本文へ残さなくてよい(Ledgerには残るので情報は失われない)
- 数字密度はBase記事以下に維持する

【長さについて(重要)】
- 目標語数・上限語数は指定しません。語数を意識して削ったり足したりしないでください
- 上記の原則を自然に適用した結果として出てくる長さで構いません"""

L_PROMPT_TEMPLATE = """以下は、Fact精度を確認済みの既存記事(Base)です。これをListening-first
(耳で一度聞いて理解しやすい)版へ書き換えてください。

新しい調査は行わず、以下のVerified Fact Ledgerの範囲内だけで書き換えてください。

【Base記事】
{article_text}

【Verified Fact Ledger】
{ledger_text}

【数字分類の結果(参考情報)】
{classification_summary}

{principles}

【出力形式】
Base記事と同じMarkdown構造(Title、本文、###見出しをちょうど2つ持つPoint、
In One Line相当の結び)を維持してください。"""


def build_l_prompt(article_text: str, ledger_text: str, classification_summary: str, focus_instructions: str) -> str:
    principles = LISTENING_FIRST_PRINCIPLES_NO_LENGTH_TARGET + "\n\n" + focus_instructions
    return L_PROMPT_TEMPLATE.format(
        article_text=article_text, ledger_text=ledger_text,
        classification_summary=classification_summary, principles=principles,
    )


def run_rewrite_with_technical_retry(client, prompt: str, max_attempts: int = 2) -> dict:
    attempts = []
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.responses.create(
                model=MODEL,
                reasoning={"effort": REASONING_EFFORT},
                input=[
                    {"role": "developer", "content": sf1.REWRITE_DEVELOPER_MESSAGE},
                    {"role": "user", "content": prompt},
                ],
            )
            text = response.output_text
            if not text or not text.strip():
                raise RuntimeError("rewrite応答が空です")
            model_id, response_id = response.model, response.id
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}"})
            if attempt < max_attempts:
                time.sleep(2)
                continue
            return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}
        structure = restore_r2.validate_point_structure(text)
        attempts.append({
            "attempt": attempt, "status": structure.status, "model": model_id,
            "response_id": response_id, "h3_count": structure.h3_count,
            "headings": structure.headings, "raw_text": text,
        })
        if structure.status == "STRUCTURE_PASS":
            return {"status": "STRUCTURE_PASS", "attempts": attempts, "raw_text": text,
                    "model": model_id, "response_id": response_id}
        if attempt < max_attempts:
            continue
        return {"status": "STRUCTURE_INVALID", "attempts": attempts, "raw_text": text,
                "model": model_id, "response_id": response_id}
    return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}


def run_one_article(client, topic_id: str):
    cfg = ARTICLES[topic_id]
    out_dir = f"{OUT_ROOT}/{topic_id}"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)

    article_text = load_text(cfg["base_article_path"])
    ledger_text = load_text(cfg["ledger_text_path"])
    base_wc = ab01.compute_word_count(article_text)

    # --- Step 1: Number Classification(sf1のスキーマ・呼び出しロジックを再利用) ---
    print(f"[SF2:{topic_id}] Step1: Number Classification呼び出し開始...")
    classification_result = sf1.run_classification(client, article_text, ledger_text)
    print(f"[SF2:{topic_id}] Step1完了: numbers={len(classification_result['parsed']['numbers'])}")
    with open(f"{out_dir}/number_classification.json", "w", encoding="utf-8") as f:
        json.dump(classification_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/classification_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in classification_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    classification_summary = sf1.build_classification_summary(classification_result["parsed"])

    # --- Step 2: Rewrite(語数目標なし) ---
    prompt = build_l_prompt(article_text, ledger_text, classification_summary, cfg["focus_instructions"])
    with open(f"{out_dir}/audit/rewrite_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"[SF2:{topic_id}] Rewrite呼び出し開始...")
    rewrite_result = run_rewrite_with_technical_retry(client, prompt)
    with open(f"{out_dir}/audit/rewrite_attempts.json", "w", encoding="utf-8") as f:
        json.dump(rewrite_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if rewrite_result["status"] != "STRUCTURE_PASS" or not rewrite_result.get("raw_text"):
        print(f"[SF2:{topic_id}] rewrite失敗 status={rewrite_result['status']}")
        return {"topic_id": topic_id, "status": rewrite_result["status"]}

    version_l = rewrite_result["raw_text"]
    with open(f"{out_dir}/version_l.md", "w", encoding="utf-8") as f:
        f.write(version_l)

    l_wc = ab01.compute_word_count(version_l)
    base_sections = sf1r1.section_word_counts(article_text)
    l_sections = sf1r1.section_word_counts(version_l)
    print(f"[SF2:{topic_id}] word_count base={base_wc} L={l_wc} (diff {l_wc - base_wc:+d})")

    # --- 独立fact checker ---
    print(f"[SF2:{topic_id}] fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(cfg["topic"], version_l, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[SF2:{topic_id}] fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    # --- Ledger逸脱チェック ---
    print(f"[SF2:{topic_id}] ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(client, ledger_text, version_l)
    print(f"[SF2:{topic_id}] deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    summary = {
        "topic_id": topic_id, "base_label": cfg["base_label"],
        "base_word_count": base_wc, "l_word_count": l_wc, "diff": l_wc - base_wc,
        "base_section_word_counts": base_sections, "l_section_word_counts": l_sections,
        "rewrite_technical_attempts": len(rewrite_result["attempts"]),
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
    }
    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def main():
    os.makedirs(OUT_ROOT, exist_ok=True)
    client = vfl01.get_client()
    summary = {}
    for topic_id in ("A01", "A02"):
        summary[topic_id] = run_one_article(client, topic_id)
    print("[SF2] 完了。summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    with open(f"{OUT_ROOT}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
