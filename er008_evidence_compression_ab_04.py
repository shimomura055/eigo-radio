# ============================================================
# er008_evidence_compression_ab_04.py
# ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04
# Part G: Evidence Compression 方式C(Lossless Editor)
# ============================================================
# BaselineのarticleをそのままLLMへ渡し、「意味を変えない範囲だけ」で
# spoken layerの負荷を軽量化する(新しいFact追加・因果関係の変更・
# scope拡張・構造変更は禁止)。方式B(Compression-aware Writer)は
# er008_evidence_compression_03.pyが担当済み(そちらを再実行して更新
# する)。ここでは方式Cのみを新規実装する。script-only、TTS/ASRは
# 実行しない。Production Writer既定は無変更。

from __future__ import annotations

import json
import re

import er008_n7_baseline_reset_01 as baseline

THEME_ID = baseline.THEME_ID
OUT_DIR = baseline.OUT_DIR
EDITOR_DIR = f"{OUT_DIR}/evidence_compression_editor"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    import os
    os.makedirs(__import__("os").path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


LOSSLESS_EDITOR_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioの記事Editorです。既に完成しているPodcast台本(Markdown)を、"
    "意味を一切変えない範囲だけで軽量に編集します。新しいFactの追加や、主張の強さを"
    "変えることは禁止です。"
)

LOSSLESS_EDITOR_PROMPT_TEMPLATE = """【編集対象のPodcast台本(Markdown、そのまま編集してください)】
{article_text}

【編集方針: Evidence Compression(Lossless Editing)】
方針: "Evidence is thick backstage, light on air." 以下の許可された編集だけを行い、
実際に読み上げられる文章(spoken layer)の負荷を軽くしてください。

【許可される編集】
- 不要な出典名の削除(企業名・調査会社名・研究機関名・メディア名・イベント名を、
  "a survey" "some companies" "one report" 等へ一般化する。ただし、その固有名詞を
  聞くこと自体がStory理解に必要な場合は残してよい)
- 近似・重複する数字の削減(意味が変わらない範囲で、複数の似た数値の並列を
  1つの傾向表現へ圧縮する。ただし、56% → 40% → 約1/3のような、トレンドの
  大きさ・方向そのものを理解するために必要な核心的な比較は残す)
- 冗長なEvidence説明の削減
- spoken wordingの簡素化(同じ意味をより自然に短く言い換える)

【絶対に行ってはいけない編集(Fact safety、最優先)】
- 新しいFactの追加
- 新しい因果関係を作ること、または相関(correlation)を因果(causation)へ変える
  こと("was associated with"を"causes"/"leads to"/"because"のような断定へ
  言い換えない)
- causal strength(主張の強さ)を変えること
- 不確実性の表現(hedging、例: "a connection, not proof")を削ること
- 主張が及ぶ範囲(scope)を広げること(「一部の企業」を「多くの企業」「企業全体」
  のように広げない)
- 比較の向き(どちらが大きい/多いか)を変えること
- 否定の有無を変えること
- 出来事の時系列の前後関係を変えること
- Point One/Point Twoの役割(本文とは別の切り口を示す、という役割)を変えること
- 記事全体の構成・段落の順序・見出しの数を変えること(Title・Main Story・
  ###見出し2つ・In One Lineの構成は維持する)

【出力形式】
編集後の記事全文を、入力と全く同じMarkdown構造(# Title、Main Story、###見出し
2つ、## In one lineの結び)で出力してください。説明文やコメントは付けず、
編集後の記事本文だけを出力してください。"""


def run_editor_for_level(client, level_key: str, article_text: str) -> dict:
    import er006_model_routing_contract_01 as routing

    prompt = LOSSLESS_EDITOR_PROMPT_TEMPLATE.format(article_text=article_text)
    resp = client.responses.create(
        model=routing.require_model("A2_WRITER", routing.WRITER_MODEL),
        reasoning={"effort": "medium"},
        input=[{"role": "developer", "content": LOSSLESS_EDITOR_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    edited_text = resp.output_text.strip()
    return {
        "prompt": prompt, "raw_text": edited_text, "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }


def run_editor() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er003_v1_n3_01_scaffold_generate as sc

    client = vfl01.get_client()
    results = {}
    for level_dir in ("a2", "b1b"):
        article_text = open(f"{OUT_DIR}/{level_dir}/article.md", encoding="utf-8").read()
        r = run_editor_for_level(client, level_dir, article_text)
        level_out = f"{EDITOR_DIR}/{level_dir}"
        import os
        os.makedirs(f"{level_out}/audit", exist_ok=True)
        with open(f"{level_out}/article.md", "w", encoding="utf-8") as f:
            f.write(r["raw_text"])
        save_json(f"{level_out}/audit/editor_raw.json", r)
        parts = sc.split_article_text(r["raw_text"])
        save_json(f"{level_out}/parts.json", parts)
        results[level_dir] = {"status": "OK", "response_id": r["response_id"],
                               "input_tokens": r["input_tokens"], "output_tokens": r["output_tokens"]}
        print(f"[{THEME_ID}] Editor({level_dir}) 完了。response_id={r['response_id']}")
    return results


def run_fact_and_ledger_check_for_editor() -> dict:
    """Baseline/Method Bと全く同じFact Check + Ledger Deviationの経路
    (er002_ja_web_research_r3/er003_v1_en_direct_vfl_01_generate)を、
    Method C(Lossless Editor)の出力へも適用する(比較可能性を保つ)。"""
    import time
    import er002_ja_web_research_r3 as r3
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_model_routing_contract_01 as routing

    client = vfl01.get_client()
    ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()
    topic = baseline.TOPIC_JA

    results = {}
    for level_dir, label in (("a2", "A2"), ("b1b", "B1B")):
        level_out = f"{EDITOR_DIR}/{level_dir}"
        article_text = open(f"{level_out}/article.md", encoding="utf-8").read()

        fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

        def make_fc_fn():
            return r3.make_fact_checker_fn(
                fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
            r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
        verdict = fc_result.get("verdict") if fc_result else None
        save_json(f"{level_out}/fact_qa.json", {
            "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
            "attempts": len(fc_attempts), "result": fc_result,
        })

        deviation_result = vfl01.run_deviation_check(
            client, ledger_text, article_text,
            model=routing.require_model("A2_WRITER", routing.WRITER_MODEL))
        save_json(f"{level_out}/ledger_deviation.json", deviation_result["parsed"])

        print(f"[{THEME_ID}] Editor({level_dir}) fact_check verdict={verdict} "
              f"ledger overall_status={deviation_result['parsed']['overall_status']} "
              f"deviations={len(deviation_result['parsed']['deviations'])}")
        results[level_dir] = {
            "fact_verdict": verdict, "ledger_status": deviation_result["parsed"]["overall_status"],
            "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        }
    return results


if __name__ == "__main__":
    import sys
    import er005_cost_logger as cl
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    if stage == "editor":
        run_editor()
    elif stage == "check":
        run_fact_and_ledger_check_for_editor()
    else:
        print("usage: er008_evidence_compression_ab_04.py [editor|check]")
