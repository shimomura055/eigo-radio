# ============================================================
# er005_stage2_articles_generate.py
# ER-005-COST-BASELINE-01: Stage 2(A2/B1記事生成+Fact QA)
# ============================================================
# er003_v1_n3_01_articles_generate.py の gen.run_theme() をそのまま再利用する
# (Writer/Fact Checker/Ledger Deviation Checkのロジック・prompt・retry回数は
# 一切変更しない)。THEMES一覧だけをER-005用の2テーマに差し替える。
#
# 実行方法:
#   .venv/Scripts/python.exe er005_stage2_articles_generate.py <theme_id>

from __future__ import annotations

import sys

import er005_cost_logger as cl
import er003_v1_n3_01_articles_generate as gen

THEMES = {
    "akb48": {
        "theme_id": "akb48",
        "topic": (
            "AKB48の68thシングル『好きish』(2026年8月19日発売)。センターを務める"
            "伊藤百花は前作『名残り桜』に続く2作連続センターで、同一メンバーの2作連続"
            "単独センターは2014年の渡辺麻友以来12年ぶり。同シングルでは20期研究生・"
            "近藤沙樹(14歳)がAKB48最年少で初選抜入りした(グループ史上最年少ではない)。"
        ),
        "ledger_path": "er005_output/cost_baseline_01/akb48/research/verified_fact_ledger.txt",
        "out_dir": "er005_output/cost_baseline_01/akb48",
    },
    "parenting": {
        "theme_id": "parenting",
        "topic": (
            "2026年のChild Development誌に掲載されたDunedin Studyのコホート追跡研究。"
            "719人の参加者が親になった時点で、親自身の社会階層の世代間変化(社会移動)と、"
            "3歳の子どもへの養育の質(sensitivity・cognitive stimulation)との関連を検証。"
            "上昇移動した親は安定低位の親より養育の質が高かったが、安定高位の親には及ばず、"
            "その差の一部は親自身の子ども時代の養育・認知能力で説明された。"
        ),
        "ledger_path": "er005_output/cost_baseline_01/parenting/research/verified_fact_ledger.txt",
        "out_dir": "er005_output/cost_baseline_01/parenting",
    },
}


def run(theme_id: str) -> None:
    # gen.run_theme()の本体をそのまま踏襲する(B1B→A2の順でrun_one_patternを呼ぶ)が、
    # Cost計測でB1/A2のWriter+Fact QAコストを分離集計できるよう、labelごとに
    # logging_contextを切り替える。run_one_pattern自体・instruction定数・
    # build_prompt/build_common_blockは無改変のまま呼び出す。
    cl.install("er005_output/cost_baseline_01/raw_usage_log.jsonl")
    client = gen.vfl01.get_client()
    master_full_text = gen.ab01.load_master_full_text()
    theme = THEMES[theme_id]
    verified_ledger_text = gen.load_text(theme["ledger_path"])
    common_block = gen.build_common_block(master_full_text, theme["topic"], verified_ledger_text)

    results = {}
    for label, instruction, out_dir, stage_name in [
        ("B1B", gen.B1_B_DIRECT_INSTRUCTION, f"{theme['out_dir']}/b1b", "b1_writer_and_fact_qa"),
        ("A2", gen.A2_KAI1_INSTRUCTION, f"{theme['out_dir']}/a2", "a2_writer_and_fact_qa"),
    ]:
        prompt = gen.build_prompt(common_block, instruction)
        with cl.logging_context(theme_id, stage_name):
            result = gen.run_one_pattern(client, theme_id, label, prompt, verified_ledger_text,
                                          theme["topic"], out_dir)
        results[label] = result

    import json
    with open(f"{theme['out_dir']}/articles_run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2, default=str)

    for label, r in results.items():
        print(f"[Stage2][{theme_id}] {label}: status={r.get('status')} "
              f"fact_verdict={r.get('fact_verdict')} ledger_status={r.get('ledger_status')}")


if __name__ == "__main__":
    run(sys.argv[1])
