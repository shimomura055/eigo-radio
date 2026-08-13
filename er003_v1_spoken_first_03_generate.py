# ============================================================
# er003_v1_spoken_first_03_generate.py
# ER-003-SPOKEN-FIRST-03: A02 Point Balance Test
# ============================================================
# ER-003-SPOKEN-FIRST-02のA02 Listening-first版(423語、Point One=144語・
# Point Two=85語)について、Point One/Twoを「本文とは別の切り口を短く
# 提示する」という本来の役割に合う長さ(target 30〜60語、tolerance
# 25〜70語)へ圧縮する。本編(Intro/Full Story)は原則そのまま維持し、
# Point削減分を埋め合わせて長くしない。新規Web researchは行わない。
#
# Production・VFL関連スクリプト・spoken_first_01/01_r1/02スクリプトは
# 変更せず、この独立スクリプトから関数を読み取り専用でimportする。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_spoken_first_03_generate.py

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

TOPIC = "英国の未成年向け夜間SNS設定"
BASE_ARTICLE_PATH = "er003_output/spoken_first_02/A02/version_l.md"
LEDGER_TEXT_PATH = "er003_output/en_direct_vfl_01/A02/verified_fact_ledger.txt"
OUT_DIR = "er003_output/spoken_first_03/A02"

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
# Rewrite: Point One/Twoの圧縮に特化。本編・In One Lineは維持方針
# ============================================================
REWRITE_DEVELOPER_MESSAGE = "英語の記事を作成してください。"

POINT_BALANCE_PRINCIPLES = """【Point One / Point Twoの役割】
Point One・Point Twoは、以下のいずれかを短く提示する場所であり、
本編(Full Story)の長い再説明をする場所ではありません。
- 本文とは別の切り口
- 本文Factの意味づけ
- 背景
- 意外な見方
- リスナー理解を一段深める補助線

禁止:
- 本文の長い再説明
- Fact Ledgerの詳細を網羅的に再掲
- Point内で新しい第二のニュース本文を作ること
- 研究方法や制約を必要以上に列挙すること

【Point Oneの核心(この核心を保ったまま圧縮する)】
「nighttime restrictionは実行しやすく、睡眠改善の兆しもあった。
ただし小規模・自己申告中心なのでproofではない」

【Point Twoの核心(この核心を保ったまま圧縮する)】
「nighttime restrictionはscreen timeそのものを消すのではなく、
時間や媒体を移す可能性がある」

【長さの目標】
- Point One: 目標30〜60語、許容範囲25〜70語
- Point Two: 目標30〜60語、許容範囲25〜70語
- 記事全体: 目標中心約350語、許容範囲280〜420語(hard capではない)
- 数値に合わせるための不自然な削除・追加は禁止。自然さを優先する
- 25語未満または70語超になる場合、それが必要な理由(核心を保つために
  どうしても必要な情報は何か)を自分自身で検討し、可能な限り目標範囲へ
  収める努力をした上で、なお範囲外が適切だと判断した場合はそのまま
  出力してよい(無理に不自然な文章にしない)

【本編(Intro/Full Story)について】
- 原則としてそのまま維持する。大きく書き変えない
- Point圧縮に伴い必要な橋渡し・重複解消のための最小限の修正のみ許可する
- Point削減分を埋め合わせるために本編を長くすることは禁止

【In One Lineについて】
- 新しい語数制約は設けない。短く印象的な結びを維持する

【禁止事項(既存のListening-first原則から継続)】
- Verified Fact Ledger外の具体的Factを追加しない
- 数字のscopeを変更しない
- 時系列を変更しない
- 因果関係を強化しない
- study limitations(小規模・自己申告・因果を証明しない等)を、Point One
  では圧縮しても完全に削除しない(核心の一部であるため)"""

POINT_BALANCE_PROMPT_TEMPLATE = """以下は、既にListening-first化されたA02の記事です(Before)。
本編(Intro/Full Story)とIn One Lineはそのまま維持し、Point One・
Point Twoだけを、本来の役割(本文とは別の短い切り口)に合う長さへ
圧縮してください。

新しい調査は行わず、以下のVerified Fact Ledgerの範囲内だけで
書き換えてください。

【Before(Listening-first版、423語。Point One=144語・Point Two=85語)】
{article_text}

【Verified Fact Ledger】
{ledger_text}

{principles}

【出力形式】
Before記事と同じMarkdown構造(Title、本文、###見出しをちょうど2つ持つ
Point、In One Line相当の結び)を維持してください。"""


def build_prompt(article_text: str, ledger_text: str) -> str:
    return POINT_BALANCE_PROMPT_TEMPLATE.format(
        article_text=article_text, ledger_text=ledger_text, principles=POINT_BALANCE_PRINCIPLES,
    )


def run_rewrite_with_technical_retry(client, prompt: str, max_attempts: int = 2) -> dict:
    attempts = []
    for attempt in range(1, max_attempts + 1):
        try:
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


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    client = vfl01.get_client()

    article_text = load_text(BASE_ARTICLE_PATH)
    ledger_text = load_text(LEDGER_TEXT_PATH)
    before_wc = ab01.compute_word_count(article_text)
    before_sections = sf1r1.section_word_counts(article_text)

    prompt = build_prompt(article_text, ledger_text)
    with open(f"{OUT_DIR}/audit/rewrite_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print("[SF3] Rewrite呼び出し開始...")
    rewrite_result = run_rewrite_with_technical_retry(client, prompt)
    with open(f"{OUT_DIR}/audit/rewrite_attempts.json", "w", encoding="utf-8") as f:
        json.dump(rewrite_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if rewrite_result["status"] != "STRUCTURE_PASS" or not rewrite_result.get("raw_text"):
        print(f"[SF3] rewrite失敗 status={rewrite_result['status']}")
        return

    after_text = rewrite_result["raw_text"]
    with open(f"{OUT_DIR}/version_after.md", "w", encoding="utf-8") as f:
        f.write(after_text)

    after_wc = ab01.compute_word_count(after_text)
    after_sections = sf1r1.section_word_counts(after_text)
    print(f"[SF3] word_count before={before_wc} after={after_wc}")
    print(f"[SF3] before_sections={before_sections}")
    print(f"[SF3] after_sections={after_sections}")

    length_report = {
        "before_total": before_wc, "after_total": after_wc,
        "before_sections": before_sections, "after_sections": after_sections,
        "point_target_lower": POINT_TARGET_LOWER, "point_target_upper": POINT_TARGET_UPPER,
        "point_tolerance_lower": POINT_TOLERANCE_LOWER, "point_tolerance_upper": POINT_TOLERANCE_UPPER,
        "total_soft_lower": TOTAL_SOFT_LOWER, "total_soft_upper": TOTAL_SOFT_UPPER,
        "point_one_within_target": POINT_TARGET_LOWER <= after_sections["point_one"] <= POINT_TARGET_UPPER,
        "point_one_within_tolerance": POINT_TOLERANCE_LOWER <= after_sections["point_one"] <= POINT_TOLERANCE_UPPER,
        "point_two_within_target": POINT_TARGET_LOWER <= after_sections["point_two"] <= POINT_TARGET_UPPER,
        "point_two_within_tolerance": POINT_TOLERANCE_LOWER <= after_sections["point_two"] <= POINT_TOLERANCE_UPPER,
        "total_within_soft_range": TOTAL_SOFT_LOWER <= after_wc <= TOTAL_SOFT_UPPER,
        "intro_unchanged": before_sections["intro"] == after_sections["intro"],
        "in_one_line_unchanged": before_sections["in_one_line"] == after_sections["in_one_line"],
    }
    with open(f"{OUT_DIR}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print("[SF3] length_report:", json.dumps(length_report, ensure_ascii=False))

    # --- 独立fact checker ---
    print("[SF3] fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, after_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[SF3] fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{OUT_DIR}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    # --- Ledger逸脱チェック ---
    print("[SF3] ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(client, ledger_text, after_text)
    print(f"[SF3] deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{OUT_DIR}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    summary = {
        "before_total": before_wc, "after_total": after_wc,
        "rewrite_technical_attempts": len(rewrite_result["attempts"]),
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
    }
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("[SF3] 完了。summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
