# ============================================================
# er003_v1_spoken_first_01_r1_generate.py
# ER-003-SPOKEN-FIRST-01-R1: ADD03 Listening-first 長文化是正
# ============================================================
# ER-003-SPOKEN-FIRST-01のVersion L(472語、Version Vの418語から+13%)を、
# 数字簡略化の方針は維持したまま、Information Budget(Version Vにない
# 新規説明論点を増やさない)と長さ条件(soft target 375〜418語、原則
# 上限418語、正当な理由がある場合のみ+5%程度まで許容)を適用して
# Version L2へ圧縮する。新規Web researchは行わない。
#
# Production・VFL関連スクリプト・spoken_first_01スクリプトは変更せず、
# この独立スクリプトから関数を読み取り専用でimportする。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_spoken_first_01_r1_generate.py

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

load_dotenv()

TOPIC = sf1.TOPIC
VERSION_V_PATH = sf1.BASE_ARTICLE_PATH
VERSION_L_PATH = "er003_output/spoken_first_01/ADD03/version_l.md"
LEDGER_TEXT_PATH = sf1.VERIFIED_LEDGER_TEXT_PATH
OUT_DIR = "er003_output/spoken_first_01_r1/ADD03"

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

VERSION_V_WORD_COUNT = 418
SOFT_TARGET_LOWER = 375
SOFT_TARGET_UPPER = 418
HARD_CEILING_WITH_JUSTIFICATION = round(418 * 1.05)  # 439


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# セクション別語数(診断用。V/L/L2どこで語数が増減したか報告するため)
# ============================================================
def split_sections(text: str) -> dict:
    lines = text.split("\n")
    sections = {"title": "", "intro": [], "point_one": [], "point_two": [], "in_one_line": []}
    current = "intro"
    h3_count = 0
    for line in lines:
        if line.startswith("# ") and not line.startswith("##"):
            sections["title"] = line
            continue
        if line.startswith("## ") and not line.startswith("###"):
            current = "in_one_line" if "in one line" in line.lower() else "header_skip"
            continue
        if line.startswith("### "):
            h3_count += 1
            current = "point_one" if h3_count == 1 else "point_two"
            continue
        if current != "header_skip":
            sections[current].append(line)
    return sections


def section_word_counts(text: str) -> dict:
    secs = split_sections(text)
    return {key: ab01.compute_word_count("\n".join(secs[key])) for key in ("intro", "point_one", "point_two", "in_one_line")}


# ============================================================
# Rewrite(L2): Information BudgetとLength条件を明示
# ============================================================
REWRITE_DEVELOPER_MESSAGE = "英語の記事を作成してください。"

L2_PRINCIPLES = sf1.REWRITE_PRINCIPLES + """

【今回追加するInformation Budget原則(ER-003-SPOKEN-FIRST-01-R1)】
- Listening-firstは、説明を追加して分かりやすくする工程ではなく、聞き手が処理しなくてよい情報を減らす工程である
- Version V(下記)にない新しい説明論点を追加しない。Fact Ledgerに存在するという理由だけで詳細を書き足さない
- 20%案の制度未確定要素(collector/payer/valuation/currency/exemptions/enforcement/legal basis)を、個別に列挙するのではなく「具体的な仕組みはほぼ示されていなかった」という核心を簡潔に伝える形にまとめる
- Point Twoについて、法的背景・IMOの説明・因果否定の補足など、Pointの核心理解に不要な詳細は本文へ残さなくてよい(Ledgerには残っているので情報は失われない)。Pointとしての切り口・面白さは維持しながら圧縮する
- 数字密度は前回のVersion L以下に維持する(前回の丸め・方向化の方針をそのまま使う。数字をさらに増やさない)

【長さ条件】
- Baseとなる原文(Version V)は{v_word_count}語
- soft target: {lower}〜{upper}語
- 原則の上限: {upper}語
- どうしても超える合理的理由がある場合のみ最大{ceiling}語まで許容するが、その場合は本文とは別に理由を一言添えてもよい
- 語数を合わせるために不自然な英文へ削ることは禁止。自然さを優先しつつ、上記のInformation Budgetを守れば自然に長さも収まるはずである"""

L2_PROMPT_TEMPLATE = """以下は、同じニュースについて書かれた2つの版です。

【Version V(元のVFL記事、Fact精度確認済み、{v_word_count}語)】
{version_v}

【Version L(前回のListening-first rewrite、{l_word_count}語。Version Vより
数字は聞きやすくなったが、Version Vにはなかった説明が増えて語数が
約13%増加した)】
{version_l}

【Verified Fact Ledger】
{ledger_text}

上記を踏まえて、Version L2を作成してください。Version Lの数字の聞きやすさ
(丸め・方向化・重複排除)は維持しながら、Version Vにはなかった新しい
説明・補足を削り、Information Budgetと長さ条件を守ってください。

{principles}

【出力形式】
Version V/Lと同じMarkdown構造(Title、本文、###見出しをちょうど2つ持つ
Point、In One Line相当の結び)を維持してください。"""


def build_l2_prompt(version_v: str, version_l: str, ledger_text: str) -> str:
    principles = L2_PRINCIPLES.format(
        v_word_count=VERSION_V_WORD_COUNT, lower=SOFT_TARGET_LOWER, upper=SOFT_TARGET_UPPER,
        ceiling=HARD_CEILING_WITH_JUSTIFICATION,
    )
    return L2_PROMPT_TEMPLATE.format(
        version_v=version_v, v_word_count=ab01.compute_word_count(version_v),
        version_l=version_l, l_word_count=ab01.compute_word_count(version_l),
        ledger_text=ledger_text, principles=principles,
    )


def run_l2_rewrite(client, prompt: str) -> dict:
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
    return {"raw_text": text, "model": response.model, "response_id": response.id}


def run_l2_with_technical_retry(client, prompt: str, max_attempts: int = 2) -> dict:
    attempts = []
    for attempt in range(1, max_attempts + 1):
        try:
            result = run_l2_rewrite(client, prompt)
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
    client = vfl01.get_client()

    version_v = load_text(VERSION_V_PATH)
    version_l = load_text(VERSION_L_PATH)
    ledger_text = load_text(LEDGER_TEXT_PATH)

    prompt = build_l2_prompt(version_v, version_l, ledger_text)
    with open(f"{OUT_DIR}/audit/l2_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print("[SF1R1] Version L2 rewrite呼び出し開始...")
    rewrite_result = run_l2_with_technical_retry(client, prompt)
    with open(f"{OUT_DIR}/audit/rewrite_attempts.json", "w", encoding="utf-8") as f:
        json.dump(rewrite_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if rewrite_result["status"] != "STRUCTURE_PASS" or not rewrite_result.get("raw_text"):
        print(f"[SF1R1] rewrite失敗 status={rewrite_result['status']}")
        return

    version_l2 = rewrite_result["raw_text"]
    with open(f"{OUT_DIR}/version_l2.md", "w", encoding="utf-8") as f:
        f.write(version_l2)

    v_wc = ab01.compute_word_count(version_v)
    l_wc = ab01.compute_word_count(version_l)
    l2_wc = ab01.compute_word_count(version_l2)
    print(f"[SF1R1] word_count V={v_wc} L={l_wc} L2={l2_wc}")

    length_report = {
        "version_v_word_count": v_wc, "version_l_word_count": l_wc, "version_l2_word_count": l2_wc,
        "l2_vs_v_pct": round((l2_wc - v_wc) / v_wc * 100, 1),
        "l2_vs_l_pct": round((l2_wc - l_wc) / l_wc * 100, 1),
        "soft_target_lower": SOFT_TARGET_LOWER, "soft_target_upper": SOFT_TARGET_UPPER,
        "hard_ceiling_with_justification": HARD_CEILING_WITH_JUSTIFICATION,
        "within_soft_target": SOFT_TARGET_LOWER <= l2_wc <= SOFT_TARGET_UPPER,
        "within_hard_ceiling": l2_wc <= HARD_CEILING_WITH_JUSTIFICATION,
        "section_word_counts": {
            "V": section_word_counts(version_v),
            "L": section_word_counts(version_l),
            "L2": section_word_counts(version_l2),
        },
    }
    with open(f"{OUT_DIR}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print("[SF1R1] length_report:", json.dumps(length_report, ensure_ascii=False))

    # --- 独立fact checker ---
    print("[SF1R1] fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, version_l2, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[SF1R1] fact_check status={fc_status} verdict={verdict}")
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
    print("[SF1R1] ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(client, ledger_text, version_l2)
    print(f"[SF1R1] deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{OUT_DIR}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    summary = {
        "word_counts": {"V": v_wc, "L": l_wc, "L2": l2_wc},
        "rewrite_technical_attempts": len(rewrite_result["attempts"]),
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
    }
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("[SF1R1] 完了。summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
