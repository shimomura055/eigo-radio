# ER-003-IRAN-A2-B1-01: 手動でarticle.mdを微修正した後の再検証
# (writerは呼ばず、既存article.mdに対してmetrics再計算+Fact Checker+
# Ledger Deviation Checkのみを再実行する)

import json
import time

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_iran01_articles_generate as gen

OUT_DIR = gen.OUT_DIR


def recheck(label: str, out_dir: str, verified_ledger_text: str):
    with open(f"{out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()

    metrics = gen.compute_metrics(article_text)
    section_wc = gen.sf1r1.section_word_counts(article_text)
    print(f"[RECHECK] {label}: metrics={metrics} sections={section_wc}")
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"[RECHECK] {label}: fact checker再実行...")
    fc_prompt = r3.build_fact_check_prompt(gen.TOPIC, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[RECHECK] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)

    client = vfl01.get_client()
    print(f"[RECHECK] {label}: ledger逸脱チェック再実行...")
    deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text)
    print(f"[RECHECK] {label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)

    return {"label": label, "fact_verdict": verdict, "fact_status": fc_status,
            "ledger_status": deviation_result["parsed"]["overall_status"]}


def main():
    verified_ledger_text = gen.load_text(gen.LEDGER_TEXT_PATH)
    results = {}
    for label, out_dir in [("B2", f"{OUT_DIR}/b2"), ("A2", f"{OUT_DIR}/a2")]:
        results[label] = recheck(label, out_dir, verified_ledger_text)
    print("[RECHECK] 完了。", results)


if __name__ == "__main__":
    main()
