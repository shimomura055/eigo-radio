# ============================================================
# er003_v1_n3_01_articles_regenerate.py
# ER-003-A2-B1-N3-01: Fact Checker FAIL/REVIEW_REQUIRED後の再生成
# ============================================================
# 初回生成で問題が見つかった4件(hanshin/a2, health/b1b, health/a2,
# household/b1b)のみを、訂正済みLedger(v2)から再生成する。
# 正常だった2件(hanshin/b1b, household/a2)は再生成しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_n3_01_articles_regenerate.py
from __future__ import annotations

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_n3_01_articles_generate as gen

TARGETS = [
    ("hanshin", "A2", gen.A2_KAI1_INSTRUCTION, "a2"),
    ("health", "B1B", gen.B1_B_DIRECT_INSTRUCTION, "b1b"),
    ("health", "A2", gen.A2_KAI1_INSTRUCTION, "a2"),
    ("household", "B1B", gen.B1_B_DIRECT_INSTRUCTION, "b1b"),
]


def main():
    client = gen.vfl01.get_client()
    master_full_text = ab01.load_master_full_text()

    theme_by_id = {t["theme_id"]: t for t in gen.THEMES}
    results = {}
    for theme_id, label, instruction, subdir in TARGETS:
        theme = theme_by_id[theme_id]
        verified_ledger_text = gen.load_text(theme["ledger_path"])
        common_block = gen.build_common_block(master_full_text, theme["topic"], verified_ledger_text)
        prompt = gen.build_prompt(common_block, instruction)
        out_dir = f"{theme['out_dir']}/{subdir}"
        result = gen.run_one_pattern(client, theme_id, label, prompt, verified_ledger_text, theme["topic"], out_dir)
        results[f"{theme_id}/{label}"] = result
        print(f"[N3-01-REGEN] {theme_id}/{label}: status={result.get('status')} "
              f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')}")

    print("[N3-01-REGEN] 完了。")


if __name__ == "__main__":
    main()
