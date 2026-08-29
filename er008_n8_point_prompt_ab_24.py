# ============================================================
# er008_n8_point_prompt_ab_24.py
# ER-008-N8-FINAL-CLOSEOUT-24 Item 2 実証:
# Writer Point Balance prompt強化(前/後)で、実Writer APIを使い、
# Point-Full Story lexical overlap率がどう変わるかを比較する。
# No.8(pool_n8_airport_line)の実Topic/実Verified Fact Ledgerをそのまま
# 使うが、No.8の承認済み完成稿(article.md等)は一切上書きしない
# (別の使い捨てdirへ保存するだけ)。
# ============================================================
from __future__ import annotations

import importlib.util
import json
import os

import er002_ja_web_research_r3 as r3  # noqa: F401 (未使用でも依存解決のため)
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen_new
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_point_overlap_qa_18 as overlap_qa

SCRATCH = ("C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/"
           "4559ebbb-f749-4719-a4c4-1a5c91891e44/scratchpad")
N8_LEDGER_PATH = "er006_output/pool_pilot_01/pool_n8_airport_line/research/verified_fact_ledger.txt"
TOPIC_JA_TEXT = (
    "空港の搭乗ゲートでは、自分の搭乗グループがまだ呼ばれていないのに、多くの乗客が"
    "早くからゲート前に並んでしまう。この行動は客室乗務員の間で「gate lice」と呼ばれ、"
    "広く知られている。心理学者は、この行動を単なる非合理な行動としてではなく、"
    "リスクの非対称性(乗り遅れる小さな可能性の代償が、無駄に立って待つことの代償より"
    "はるかに大きい)への合理的な反応として説明する。また、頭上の荷物棚の空き容量を"
    "めぐる競争、周囲の人が並び始めると自分も並んでしまう同調行動、順番を守らないと"
    "恥をかくという社会的なプレッシャーも背景にある。一方で航空会社側もこの問題への"
    "対応を強めており、American Airlinesは2026年夏からダラス・フォートワース空港で、"
    "搭乗券を自動確認し乗客の流れを規制する電子搭乗ゲートの本格導入を始める。"
)
N_TRIALS_PER_CONDITION = 4


def _load_old_module():
    old_path = f"{SCRATCH}/old_articles_generate.py"
    assert os.path.exists(old_path), "git show HEAD:... で強化前のarticles_generate.pyを先に書き出してください"
    spec = importlib.util.spec_from_file_location("gen_old_24", old_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_trials(client, writer_model: str, master_full_text: str, ledger_text: str,
               common_block_fn, label: str) -> list[dict]:
    trials = []
    for i in range(N_TRIALS_PER_CONDITION):
        common_block = common_block_fn(master_full_text, TOPIC_JA_TEXT, ledger_text)
        prompt = gen_new.build_prompt(common_block, gen_new.A2_KAI1_INSTRUCTION)
        print(f"[N8-POINT-AB-24][{label}] trial {i + 1}/{N_TRIALS_PER_CONDITION} writer呼び出し...")
        writer_result = vfl01.run_writer_with_technical_retry(client, prompt, model=writer_model)
        if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
            trials.append({"trial": i, "status": writer_result["status"]})
            continue
        article_text = writer_result["raw_text"].strip()
        sections = gen_new.split_common_sections_for_point_qa(article_text)
        if sections is None:
            trials.append({"trial": i, "status": "SECTION_SPLIT_FAILED", "article_text": article_text})
            continue
        p1 = overlap_qa.flag_possible_paraphrase(sections["point_one_body"], sections["full_story"])
        p2 = overlap_qa.flag_possible_paraphrase(sections["point_two_body"], sections["full_story"])
        trials.append({
            "trial": i, "status": "OK",
            "article_text": article_text,
            "point_one_heading": sections["point_one_heading"],
            "point_one_body": sections["point_one_body"],
            "point_one_overlap": p1,
            "point_two_heading": sections["point_two_heading"],
            "point_two_body": sections["point_two_body"],
            "point_two_overlap": p2,
            "any_flagged": p1["flagged"] or p2["flagged"],
        })
        print(f"[N8-POINT-AB-24][{label}] trial {i + 1}: point_one_overlap={p1['overlap_ratio']} "
              f"point_two_overlap={p2['overlap_ratio']} any_flagged={p1['flagged'] or p2['flagged']}")
    return trials


def summarize(trials: list[dict]) -> dict:
    ok = [t for t in trials if t["status"] == "OK"]
    if not ok:
        return {"n_ok": 0, "n_total": len(trials)}
    ratios = [t["point_one_overlap"]["overlap_ratio"] for t in ok] + \
             [t["point_two_overlap"]["overlap_ratio"] for t in ok]
    flagged_count = sum(1 for t in ok if t["any_flagged"])
    return {
        "n_ok": len(ok), "n_total": len(trials),
        "mean_overlap_ratio": round(sum(ratios) / len(ratios), 3),
        "max_overlap_ratio": max(ratios),
        "articles_with_any_flagged_point": flagged_count,
        "flagged_rate": round(flagged_count / len(ok), 3),
    }


def main():
    cl.install(f"{SCRATCH}/er24_point_prompt_ab_raw_usage_log.jsonl")
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_text = open(N8_LEDGER_PATH, encoding="utf-8").read()
    writer_model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)

    gen_old = _load_old_module()

    print("[N8-POINT-AB-24] === 強化前(OLD) trials ===")
    old_trials = run_trials(client, writer_model, master_full_text, ledger_text,
                             gen_old.build_common_block, "OLD")
    print("[N8-POINT-AB-24] === 強化後(NEW) trials ===")
    new_trials = run_trials(client, writer_model, master_full_text, ledger_text,
                             gen_new.build_common_block, "NEW")

    summary = {
        "old_prompt_summary": summarize(old_trials),
        "new_prompt_summary": summarize(new_trials),
        "old_trials": old_trials,
        "new_trials": new_trials,
    }
    with open(f"{SCRATCH}/er24_point_prompt_ab_result.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[N8-POINT-AB-24] OLD summary:", json.dumps(summary["old_prompt_summary"], ensure_ascii=False))
    print("[N8-POINT-AB-24] NEW summary:", json.dumps(summary["new_prompt_summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
