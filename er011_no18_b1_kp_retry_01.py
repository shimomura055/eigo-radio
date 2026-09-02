# ============================================================
# er011_no18_b1_kp_retry_01.py
# ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01(補助)
# ============================================================
# No.18 B1のKey Phrase選定がSupport stage初回でKEY_WORDS_STRUCTURE_INVALID
# (ja_glossに括弧書き補足、Key Phrase括弧禁止仕様に抵触)。
# run_key_phrase_selection()はmax_attempts=1の単発gateであり(スコープ内で
# 複数回試すのではなく)、既存Production前例(er003_v1_iran01_a2_kp_retry.py、
# 「初回KEY_WORDS_STRUCTURE_INVALID対応」)と同一の手当て方法として、
# 実Production関数(er006_pool_pilot_01_support.sc.run_key_phrases、
# Trial専用scriptではない)をそのまま再呼び出しするだけの最小retry。
# 新しい仕様判断・hardcodeは一切行わない。

from __future__ import annotations

import json

import er005_cost_logger as cl
import er006_pool_pilot_01_support as support_mod

sc = support_mod.sc

THEME_ID = "pool_n18_notifications"
OUT_DIR = f"er006_output/pool_pilot_01/{THEME_ID}"
LABEL = "b1b"
MAX_RETRY = 3


def main():
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    level_out_dir = f"{OUT_DIR}/{LABEL}"
    with open(f"{level_out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    kp_dir = f"{level_out_dir}/key_phrases"
    article_id = f"ER006_{THEME_ID}_{LABEL}"

    for attempt in range(1, MAX_RETRY + 1):
        print(f"[ER-011-NO18-B1-KP-RETRY] attempt {attempt}/{MAX_RETRY}...")
        with cl.logging_context(THEME_ID, "support_b1_kp_retry"):
            kp = sc.run_key_phrases(article_text, kp_dir, article_id, "B1-B(N3-01, direct generation)",
                                     process="B1_SUPPORT")
        kp_status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else kp["selection"]["status"]
        print(f"[ER-011-NO18-B1-KP-RETRY] attempt {attempt} kp_status={kp_status}")
        if kp_status in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            break
    else:
        print("[ER-011-NO18-B1-KP-RETRY] 全attempt失敗。人手対応が必要。")
        return

    summary_path = f"{OUT_DIR}/scaffold_run_summary.json"
    summary = json.load(open(summary_path, encoding="utf-8"))
    summary[LABEL]["key_phrases_status"] = kp_status
    summary[LABEL]["key_phrases_count"] = len((kp.get("canonicalization") or {}).get("merged", {}).get("items", []))
    summary[LABEL]["key_phrases_retry_note"] = (
        f"Support stage初回はKEY_WORDS_STRUCTURE_INVALID(ja_glossの括弧書き補足)。"
        f"実Production関数run_key_phrases()の再呼び出しのみでattempt {attempt}にて{kp_status}。"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[ER-011-NO18-B1-KP-RETRY] scaffold_run_summary.json更新完了。final_status={kp_status}")


if __name__ == "__main__":
    main()
