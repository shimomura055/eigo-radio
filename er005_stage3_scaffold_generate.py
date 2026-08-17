# ============================================================
# er005_stage3_scaffold_generate.py
# ER-005-COST-BASELINE-01: Stage 3(Scaffold: Preview/Comments/Key Phrases)
# ============================================================
# er003_v1_n3_01_scaffold_generate.py の run_theme_scaffold(client, theme) を
# そのまま再利用する(内部のrun_b1_scaffold/run_a2_scaffold/run_key_phrasesは
# 無改変)。THEMES一覧だけをER-005用の2テーマに差し替える。
#
# 実行方法:
#   .venv/Scripts/python.exe er005_stage3_scaffold_generate.py <theme_id>

from __future__ import annotations

import sys

import er005_cost_logger as cl
import er003_v1_n3_01_scaffold_generate as sc
from er005_stage2_articles_generate import THEMES


def run(theme_id: str) -> None:
    # run_theme_scaffold()の本体をそのまま踏襲するが、B1/A2のSupport生成+Key Phrase
    # 選定コストを分離集計できるよう、labelごとにlogging_contextを切り替える。
    # run_b1_scaffold/run_a2_scaffold/run_key_phrases自体は無改変のまま呼び出す。
    import json
    import os

    cl.install("er005_output/cost_baseline_01/raw_usage_log.jsonl")
    client = sc.get_client()
    theme = THEMES[theme_id]

    result = {}
    for label, run_fn, source_level, stage_prefix in [
        ("b1b", sc.run_b1_scaffold, "B1-B(N3-01, direct generation)", "b1"),
        ("a2", sc.run_a2_scaffold, "A2(V2改1, N3-01)", "a2"),
    ]:
        out_dir = f"{theme['out_dir']}/{label}"
        os.makedirs(f"{out_dir}/audit", exist_ok=True)
        with open(f"{out_dir}/article.md", encoding="utf-8") as f:
            article_text = f.read()
        parts = sc.split_article_text(article_text)
        with open(f"{out_dir}/parts.json", "w", encoding="utf-8") as f:
            json.dump(parts, f, ensure_ascii=False, indent=2)

        with cl.logging_context(theme_id, f"{stage_prefix}_support"):
            support = run_fn(client, parts, out_dir, article_text)

        kp_dir = f"{out_dir}/key_phrases"
        article_id = f"ER005_{theme_id}_{label}"
        with cl.logging_context(theme_id, f"{stage_prefix}_key_phrase"):
            kp = sc.run_key_phrases(article_text, kp_dir, article_id, source_level)
        kp_status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else kp["selection"]["status"]
        print(f"[Stage3][{theme_id}/{label}] key phrase status={kp_status}")

        result[label] = {"parts": parts, "support": {k: v.get("status") for k, v in support.items()},
                          "key_phrases_status": kp_status}

    with open(f"{theme['out_dir']}/scaffold_run_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Stage3][{theme_id}] done. status={ {k: v['key_phrases_status'] for k, v in result.items()} }")


if __name__ == "__main__":
    run(sys.argv[1])
