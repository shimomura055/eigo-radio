# ============================================================
# er011_kp_ja_gloss_no_parenthetical_prod_wiring_01.py
# KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01
# ============================================================
# 目的: gloss生成Prompt(er003_v1_translator_briefs/
# b1_p2_keywords_l_prompt_template.txt、A2/B1共有・Production本体)へ
# 追加した「日本語グロスに括弧内の別訳・専門用語・補足を併記しない」
# 趣旨の1句が、実際のProduction経路(sc.run_key_phrases、無変更)で
# 効果を持つかをruntime evidenceとして確認する。
#
# 対象: Theme 2(若者の旅行、B条件)A2/B1のTrial-12 article.md
# (er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/{level}_run01/
# article.md、OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01で使用した
# Trial-13 article.mdと内容一致をdiffで確認済み)。
#
# 実行内容: Key Phrase選定→canonicalization(→Redundancy QA)を
# Production関数sc.run_key_phrases()でA2・B1各1回実行する(無変更、
# TTS/ASR/Assemblyは対象外)。
#
# 実費: 選定・canonicalization(・Redundancy QA)のLLM call実費のみ
# (小額、TTS/ASRなし)。

from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_n3_01_scaffold_generate as sc
import er005_cost_logger as cl

THEME_ID = "kp_ja_gloss_no_parenthetical_prod_wiring_01"
OUT_DIR = f"er011_output/{THEME_ID}"

TRIAL12_DIR = "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12"

LEVELS = {
    "b1b": {
        "article_path": f"{TRIAL12_DIR}/b1b_run01/article.md",
        "source_level": "B1-B(N3-01, direct generation)",
        "process": "B1_SUPPORT",
        "article_id": "THEME2_B1_GLOSSFIX01",
    },
    "a2": {
        "article_path": f"{TRIAL12_DIR}/a2_run01/article.md",
        "source_level": "A2(V2改1, N3-01)",
        "process": "A2_SUPPORT",
        "article_id": "THEME2_A2_GLOSSFIX01",
    },
}

_PAREN_CHARS = "（）()"


def _has_parenthetical(text: str) -> bool:
    return any(c in text for c in "（）()")


def run_level(level: str) -> dict:
    meta = LEVELS[level]
    level_out_dir = f"{OUT_DIR}/{level}"
    os.makedirs(f"{level_out_dir}/key_phrases", exist_ok=True)

    with open(meta["article_path"], encoding="utf-8") as f:
        article_text = f.read()

    kp_dir = f"{level_out_dir}/key_phrases"
    print(f"[GLOSSFIX01][{level}] Key Phrase選定+Canonicalization(+Redundancy QA) "
          "(Production経路、sc.run_key_phrases、無変更)開始...")
    with cl.logging_context(THEME_ID, f"keyphrase_{level}"):
        kp = sc.run_key_phrases(article_text, kp_dir, meta["article_id"], meta["source_level"],
                                 process=meta["process"])

    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    print(f"[GLOSSFIX01][{level}] 結果: selection={sel_status} canonicalization={canon_status} "
          f"redundancy={redundancy_status} overall_status={kp.get('status')}")

    original_items = kp["selection"].get("original_items") or []
    gloss_rows = []
    for it in original_items:
        gloss = it.get("ja_gloss", "")
        gloss_rows.append({
            "rank": it.get("rank"), "display_phrase": it.get("display_phrase"),
            "ja_gloss": gloss, "contains_parenthetical": _has_parenthetical(gloss),
        })

    summary = {
        "level": level, "article_path": meta["article_path"],
        "selection_status": sel_status, "canonicalization_status": canon_status,
        "redundancy_qa_status": redundancy_status,
        "overall_status": kp.get("status"),
        "gloss_rows": gloss_rows,
        "any_parenthetical_in_selection": any(r["contains_parenthetical"] for r in gloss_rows),
    }
    with open(f"{level_out_dir}/gloss_evidence_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    return summary


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    results = {}
    for level in ("b1b", "a2"):
        results[level] = run_level(level)
    with open(f"{OUT_DIR}/overall_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return results


if __name__ == "__main__":
    out = main()
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
