# ============================================================
# er012_output/personalized_news_b1_rebuild_01/fix01_kp_retry.py
# 管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01
# ============================================================
# 目的: Key Phrase選定初回がKEY_WORDS_STRUCTURE_INVALID(rank1候補
# "the stakes are different"に有限助動詞"are"を含む、既存の方式L
# hard requirement違反)だったため、実Production関数
# er003_v1_n3_01_scaffold_generate.run_key_phrases()をそのまま
# 再呼び出しするだけの最小retryを行う。新しい仕様判断・hardcodeは
# 一切行わない(既存前例: er011_no18_b1_kp_retry_01.py、
# er003_v1_iran01_a2_kp_retry.py、「run_key_phrase_selection()は
# max_attempts=1の単発gateであり、既存Production前例と同一の手当て方法
# として実Production関数をそのまま再呼び出しするだけの最小retry」)。
from __future__ import annotations

import json
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
os.chdir(_REPO_ROOT)

import er003_v1_n3_01_scaffold_generate as sc
import er005_cost_logger as cl

BASE_DIR = "er012_output/personalized_news_b1_rebuild_01"
ARTICLE_PATH = f"{BASE_DIR}/b1_2v_new_theme_r8_attempt1/article.md"
OUT_BASE = f"{BASE_DIR}/audio/b1_2v_fix01"
KP_DIR = f"{OUT_BASE}/b1b/key_phrases"
SUMMARY_PATH = f"{OUT_BASE}/audit/key_phrase_generation_summary.json"
ARTICLE_ID = "personalized_news_b1_rebuild_01_r8"
SOURCE_LEVEL = "B1"
MAX_RETRY = 3


def main() -> None:
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    cl.install(f"{OUT_BASE}/cost_log_kp_retry.jsonl")
    with open(ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()

    kp_status = None
    result = None
    for attempt in range(1, MAX_RETRY + 1):
        print(f"[FIX-01-KP-RETRY] attempt {attempt}/{MAX_RETRY}...")
        result = sc.run_key_phrases(article_text, KP_DIR, ARTICLE_ID, SOURCE_LEVEL, process="B1_SUPPORT")
        kp_status = (result.get("canonicalization") or {}).get("status") if result.get("canonicalization") \
            else result["selection"]["status"]
        print(f"[FIX-01-KP-RETRY] attempt {attempt} kp_status={kp_status}")
        if kp_status in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            break
    else:
        print("[FIX-01-KP-RETRY] 全attempt失敗。人手対応が必要(STOP)。")
        return

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[FIX-01-KP-RETRY] DONE final_status={kp_status} -> {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
