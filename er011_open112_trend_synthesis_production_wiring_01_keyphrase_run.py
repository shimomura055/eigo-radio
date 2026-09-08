from __future__ import annotations
import er005_cost_logger as cl
import er003_v1_n3_01_scaffold_generate as scaffold
import er011_open112_trend_synthesis_production_wiring_01_run as base

OUT_DIR = f"{base.OUT_DIR}/b1b/key_phrases"


def run():
    with open(f"{base.OUT_DIR}/b1b/article.md", encoding="utf-8") as f:
        article_text = f.read()
    result = scaffold.run_key_phrases(article_text, OUT_DIR, base.THEME_ID, "b1", process="B1_SUPPORT")
    sel = result.get("selection") or {}
    canon = result.get("canonicalization") or {}
    redundancy = result.get("redundancy_qa") or {}
    print(f"selection_status={sel.get('status')} canonicalization_status={canon.get('status')} "
          f"redundancy_status={redundancy.get('status')} overall_status={result.get('status')}")
    return result


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    run()
