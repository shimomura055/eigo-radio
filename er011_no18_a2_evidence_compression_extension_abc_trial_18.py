# ============================================================
# er011_no18_a2_evidence_compression_extension_abc_trial_18.py
# ER-011-NO18-A2-EVIDENCE-COMPRESSION-EXTENSION-ABC-TRIAL-18
# ============================================================
# 目的: 現行Evidence Compression Editor(方式C、Lossless Editor)の
# Prompt・安全思想を一切変更せず、末尾に「追加Compression rule」だけを
# 差し込んだ3パターン(A/B/C)を、No.18 A2の既存Writer出力(pre_editor_
# article.md、Fact-safe)を共通入力としてTrialする。Writerは再生成しない。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
# Production Prompt変更・CURRENT_SPEC変更・No.18 article.md上書き・
# TTS/Audio・OPEN-100 close・OPEN-112着手は一切行わない。
from __future__ import annotations

import json
import os
import re
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as artgen
import er003_v1_n3_01_evidence_compression_editor as ec_editor

load_dotenv()

SRC_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2"
OUT_DIR = "er011_output/no18_a2_evidence_compression_extension_abc_trial_18"
EDITOR_MODEL = "gpt-5.6-luna"  # No.18 A2の実production Editor callと同一モデル(evidence_compression_editor_raw.json確認済み)

TOPIC_EN = (
    "Why notification sounds -- and even a silent phone left nearby -- can affect a "
    "person's attention and processing speed, based on two peer-reviewed studies "
    "(Upshaw, Stevens, Ganis & Zabelina, 2022, PLOS ONE; Skowronek, Seifert & Lindberg, "
    "2023, Scientific Reports) and a 2018 Pew Research Center survey of U.S. teens' "
    "device-checking habits."
)

# ------------------------------------------------------------
# 共通目的文(§2、英語Promptとして実装)
# ------------------------------------------------------------
COMMON_PURPOSE_BLOCK_EN = """【Compression Purpose Clarification -- applies to every pattern below】
The purpose of Evidence Compression is not to reduce the number of digits for its own
sake. It is to make sure that, once heard aloud, a listener can still follow the meaning
of the Evidence. When, within the same study, survey, or comparison, multiple different
Facts or metrics point in the same direction, and listing every individual number raises
listening load, consider a way to keep the presence, meaning, and direction of comparison
of each Fact while retaining only the minimum numbers necessary.

Fact safety always takes priority over ease of listening."""

# ------------------------------------------------------------
# Pattern A: Representative Metric + Supporting Trend(§3)
# ------------------------------------------------------------
PATTERN_A_BLOCK_JA = """【追加ルール: Pattern A - Representative Metric + Supporting Trend】
同一の研究・調査・比較の中で、複数の異なる指標が同じ方向の結果を示している場合:
- すべての比較数値を列挙しなくてよい
- リスナーが結果の大きさを理解するために、最も代表性・説明力の高い指標を1つ選び、
  その指標の比較数値(絶対値)は保持してよい
- その他の指標についても、Factとしては本文に残すこと。ただし具体的な数値は省略し、
  "showed the same pattern" "was also lower" のようなtrend表現へ言い換えてよい
- 補助的な指標のFact自体を削除しないこと
- 2つ以上の異なるFactを、1つのFactであるかのように統合して書かないこと
- 相関を因果へ強めないこと
- 実際には「同じ傾向」と言えない指標同士を、同じ傾向として扱わないこと"""

# ------------------------------------------------------------
# Pattern B: Conclusion-First / Numeric Necessity Test(§4)
# ------------------------------------------------------------
PATTERN_B_BLOCK_JA = """【追加ルール: Pattern B - Conclusion-First / Numeric Necessity Test】
同一の研究・調査の複数の数値が同じ結論を裏付けている場合:
- まず、リスナーが理解すべき結論を簡潔に示す
- 個々の数値について、「その数値そのものが、結果の大きさ・意外性・実務的重要性を
  理解するために不可欠かどうか」を判定する
- 不可欠と判断した数値だけを残す
- 不可欠でないと判断した数値については、指標名・比較の方向・Factの存在は保持した
  まま、具体的な数値は省略してよい
- 数字をゼロにすることを目標にしないこと。必要であれば数字は残すこと
- Factの削除、比較条件の削除、因果表現への強化、certaintyの強化、Evidenceの意味を
  一般論へ広げることは、他のルールと同様に禁止"""

# ------------------------------------------------------------
# Pattern C: Listener-Friendly Numeric Re-expression(§5)
# ------------------------------------------------------------
PATTERN_C_BLOCK_JA = """【追加ルール: Pattern C - Listener-Friendly Numeric Re-expression】
複数の絶対値をそのまま読み上げるより、差・概数・比較幅などへ再表現した方が、一度
聞いて理解しやすい場合、元のEvidenceから機械的に検証可能な範囲でのみ数値を
再表現してよい(例: "99.71 vs 108.95" をそのまま読み上げる代わりに "about 9 points
lower" のように言い換える)。

必須条件:
- 元のVerified Fact Ledgerに書かれている数値だけから計算すること(新しい数値・
  新しいEvidenceを作らないこと)
- 丸め方を記事全体で一貫させること
- 異なるFactを1つのFactに統合しないこと。因果・certainty・条件は変えないこと
- 計算がどちらの数値を起点にすべきか一意に決まらない場合、または曖昧になる場合は、
  再表現せず元の数値をそのまま残すこと"""

PATTERNS = {
    "baseline": {"label": "Baseline(既存方式Cのまま、追加ルールなし)", "extra": None},
    "A": {"label": "Pattern A: Representative Metric + Supporting Trend", "extra": PATTERN_A_BLOCK_JA},
    "B": {"label": "Pattern B: Conclusion-First / Numeric Necessity Test", "extra": PATTERN_B_BLOCK_JA},
    "C": {"label": "Pattern C: Listener-Friendly Numeric Re-expression", "extra": PATTERN_C_BLOCK_JA},
}

CAUSAL_MARKERS = [
    "because", "due to", "caused", "causes", "causing", "leads to", "led to",
    "results in", "resulted in", "so that", "which made", "which causes",
    "as a result", "therefore", "thus", " so it ",
]


def build_prompt(article_text: str, extra_block: str | None) -> str:
    base_prompt = ec_editor.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text=article_text)
    if extra_block is None:
        return base_prompt
    marker = "【絶対に行ってはいけない編集(Fact safety、最優先)】"
    insertion = COMMON_PURPOSE_BLOCK_EN + "\n\n" + extra_block + "\n\n"
    assert marker in base_prompt, "既存Editor Promptの構造が変わっています(marker not found)"
    return base_prompt.replace(marker, insertion + marker)


def run_editor_variant(client, article_text: str, extra_block: str | None) -> dict:
    prompt = build_prompt(article_text, extra_block)
    resp = client.responses.create(
        model=EDITOR_MODEL,
        reasoning={"effort": "medium"},
        input=[
            {"role": "developer", "content": ec_editor.EVIDENCE_COMPRESSION_EDITOR_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    edited_text = resp.output_text.strip()
    return {
        "prompt": prompt, "raw_text": edited_text, "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }


def count_numbers(text: str) -> int:
    return len(re.findall(r"\d[\d,]*\.?\d*\s*%?", text))


def scan_causal_markers(text: str) -> list[str]:
    lower = text.lower()
    return [m for m in CAUSAL_MARKERS if m in lower]


def find_ledger_fact_lines(verified_ledger_text: str, fact_ids: list[str]) -> dict:
    out = {}
    for line in verified_ledger_text.splitlines():
        for fid in fact_ids:
            if line.strip().startswith(f"[{fid}]"):
                out[fid] = line.strip()
    return out


def run_fact_checker(client, topic: str, article_text: str) -> dict:
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt, client=client, model="gpt-5.6-luna")

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    return {
        "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    with open(f"{SRC_DIR}/a2/audit/pre_editor_article.md", encoding="utf-8") as f:
        baseline_article_text = f.read()
    with open(f"{SRC_DIR}/research/verified_fact_ledger.txt", encoding="utf-8") as f:
        verified_ledger_text = f.read()

    client = vfl01.get_client()
    ledger_model = "gpt-5.6-luna"

    fact_lines = find_ledger_fact_lines(verified_ledger_text, ["F-005", "F-006"])

    summary = {"input_article": baseline_article_text, "fact_lines_F005_F006": fact_lines, "variants": {}}

    for key, cfg in PATTERNS.items():
        print(f"[TRIAL-18] variant={key}: Evidence Compression Editor呼び出し開始...")
        editor_result = run_editor_variant(client, baseline_article_text, cfg["extra"])
        variant_text = editor_result["raw_text"]
        with open(f"{OUT_DIR}/audit/editor_raw_{key}.json", "w", encoding="utf-8") as f:
            json.dump(editor_result, f, ensure_ascii=False, indent=2, default=str)
        with open(f"{OUT_DIR}/article_{key}.md", "w", encoding="utf-8") as f:
            f.write(variant_text)

        print(f"[TRIAL-18] variant={key}: Ledger Deviation Check(hook_aware=True)開始...")
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, variant_text, model=ledger_model, hook_aware=True)
        with open(f"{OUT_DIR}/audit/ledger_deviation_{key}.json", "w", encoding="utf-8") as f:
            json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)

        print(f"[TRIAL-18] variant={key}: Fact Checker呼び出し開始...")
        fact_qa = run_fact_checker(client, TOPIC_EN, variant_text)
        with open(f"{OUT_DIR}/audit/fact_qa_{key}.json", "w", encoding="utf-8") as f:
            json.dump(fact_qa, f, ensure_ascii=False, indent=2, default=str)

        metrics = artgen.compute_metrics(variant_text)
        causal_markers_found = scan_causal_markers(variant_text)
        causal_markers_baseline = scan_causal_markers(baseline_article_text)
        new_causal_markers = [m for m in causal_markers_found if m not in causal_markers_baseline]

        variant_summary = {
            "label": cfg["label"],
            "response_id": editor_result["response_id"],
            "metrics": metrics,
            "number_count": count_numbers(variant_text),
            "ledger_overall_status": deviation_result["parsed"]["overall_status"],
            "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
            "ledger_deviations": deviation_result["parsed"]["deviations"],
            "fact_checker_status": fact_qa["final_status"],
            "fact_checker_verdict": (fact_qa["result"] or {}).get("verdict") if fact_qa["result"] else None,
            "causal_markers_found": causal_markers_found,
            "new_causal_markers_vs_baseline_input": new_causal_markers,
        }
        summary["variants"][key] = variant_summary
        print(f"[TRIAL-18] variant={key}: 完了。ledger_status="
              f"{variant_summary['ledger_overall_status']} "
              f"fact_verdict={variant_summary['fact_checker_verdict']} "
              f"new_causal_markers={new_causal_markers}")

    with open(f"{OUT_DIR}/trial_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[TRIAL-18] 完了。summary -> {OUT_DIR}/trial_summary.json")


if __name__ == "__main__":
    main()
