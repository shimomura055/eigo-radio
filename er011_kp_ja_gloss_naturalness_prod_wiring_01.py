# ============================================================
# er011_kp_ja_gloss_naturalness_prod_wiring_01.py
# KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01: Runtime evidence
# ============================================================
# 目的: Gate 3チェックリストのRuntime evidence要件を満たす。
# Theme 2 B1とA2の記事(Trial-12 article.md)をそれぞれ1回、Production
# 正式選定経路(sc.run_key_phrases、無変更のProduction関数、選定→
# canonicalization→Key Phrase Set Redundancy QA)へ入力し、選定5件×2
# レベルの英語Key Phrase・表示用gloss(japanese_gloss)・TTS用gloss
# (japanese_gloss_tts)を、直前配線(KEYPHRASE-DISPLAY-TTS-SEPARATION-
# PROD-WIRING-01)の出力と並べて比較できる形で保存する。
#
# LLM小額のみ(選定+canonicalization+redundancy QA)、TTSは一切呼ばない。
# Production関数(sc.run_key_phrases)は無変更のまま直接呼び出す
# (monkeypatchなし)。

from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_n3_01_scaffold_generate as sc
import er005_cost_logger as cl

OUT_DIR = "er011_output/kp_ja_gloss_naturalness_prod_wiring_01"

RUNS = [
    {
        "label": "b1b",
        "article_id": "THEME2_B1_KPJAGLOSSNATURALNESS01",
        "source_level": "B1-B(N3-01, direct generation)",
        "process": "B1_SUPPORT",
        "article_path": "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/b1b_run01/article.md",
    },
    {
        "label": "a2",
        "article_id": "THEME2_A2_KPJAGLOSSNATURALNESS01",
        "source_level": "A2(N3-01, direct generation)",
        "process": "A2_SUPPORT",
        "article_path": "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/a2_run01/article.md",
    },
]


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def run_one(run: dict) -> dict:
    label = run["label"]
    theme_out_dir = f"{OUT_DIR}/{label}"
    kp_dir = f"{theme_out_dir}/key_phrases"
    os.makedirs(f"{theme_out_dir}/audit", exist_ok=True)

    article_text = load_text(run["article_path"])
    print(f"[EVIDENCE] [{label}] Production Key Phrase選定→canonicalization→"
          "redundancy QA (sc.run_key_phrases, 無変更のProduction関数)...")
    with cl.logging_context("kp_ja_gloss_naturalness_prod_wiring_01", f"keyphrase_{label}"):
        kp_result = sc.run_key_phrases(article_text, kp_dir, run["article_id"], run["source_level"],
                                        process=run["process"])

    sel_status = kp_result["selection"]["status"]
    canon_status = kp_result["canonicalization"]["status"] if kp_result["canonicalization"] else None
    redundancy_status = kp_result["redundancy_qa"]["status"] if kp_result.get("redundancy_qa") else None
    print(f"[EVIDENCE] [{label}] selection={sel_status} canonicalization={canon_status} "
          f"redundancy_qa={redundancy_status}")

    with open(f"{theme_out_dir}/audit/run_key_phrases_result_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "selection_status": sel_status, "canonicalization_status": canon_status,
            "redundancy_qa_status": redundancy_status,
            "redundancy_retry_log": kp_result.get("redundancy_retry_log"),
        }, f, ensure_ascii=False, indent=2, default=str)

    assert sel_status == "KEY_WORDS_STRUCTURE_PASS", f"[{label}] 選定失敗: {sel_status}"
    assert canon_status in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"), \
        f"[{label}] canonicalization失敗: {canon_status}"

    merged_items = kp_result["canonicalization"]["merged"]["items"]
    print(f"[EVIDENCE] [{label}] 選定5件の表示用/TTS用gloss:")
    comparison_rows = []
    for it in sorted(merged_items, key=lambda x: x["rank"]):
        row = {
            "rank": it["rank"], "used_form": it["used_form"],
            "japanese_gloss": it["japanese_gloss"],
            "japanese_gloss_tts": it.get("japanese_gloss_tts"),
        }
        comparison_rows.append(row)
        print(f"  rank{it['rank']} used_form={it['used_form']!r} "
              f"japanese_gloss={it['japanese_gloss']!r} japanese_gloss_tts={it.get('japanese_gloss_tts')!r}")

    canon_artifact_path = f"{kp_dir}/keywords_canonicalized.json"
    assert os.path.exists(canon_artifact_path), f"[{label}] canonicalization artifactが見つかりません"

    return {
        "label": label, "article_id": run["article_id"], "article_path": run["article_path"],
        "selection_status": sel_status, "canonicalization_status": canon_status,
        "redundancy_qa_status": redundancy_status,
        "canonicalization_artifact_path": canon_artifact_path,
        "comparison_rows": comparison_rows,
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    results = [run_one(r) for r in RUNS]

    summary = {"runs": results}
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[EVIDENCE] 完了。summary:", json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
