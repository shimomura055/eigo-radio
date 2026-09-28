# ============================================================
# er021_output/coverage_review_02/offline_telemetry_reclassify_01.py
# 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(Phase 2)
# ============================================================
# 性質: read-only・¥0(API呼び出しなし)。既存telemetry.jsonl
# (er021_output/en_asr_semantic_equivalence_production_wiring_01/
# telemetry.jsonl、role適用segmentでTier1 early-exitに入らず
# baselineへフォールバックした実運用NG記録)を、strict版Tier1合成規則
# 実装後のer021_en_asr_semantic_equivalence_production_01.
# tier1_numeric_equivalence()で再判定する。Production側のtelemetry.jsonl
# 自体・SSOT・Production挙動には一切書き込まない(read-only)。
#
# 実行方法(手動実行、Sonnet不要のread-only集計のためhaiku-worker委任可):
#   .venv/Scripts/python.exe er021_output/coverage_review_02/
#     offline_telemetry_reclassify_01.py
#   > er021_output/coverage_review_02/offline_telemetry_reclassify_01_result.json
#
# 出力: 母数・反転件数・カテゴリ別内訳・反転した各recordのcanonical/asr
# (false accept監査用、目視確認できるよう全件列挙)。

from __future__ import annotations

import json
import sys

sys.path.insert(0, ".")
import er021_en_asr_semantic_equivalence_production_01 as tier1  # noqa: E402

TELEMETRY_PATH = "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl"


def main() -> None:
    total = 0
    reversed_records = []
    sub_reason_totals: dict[str, int] = {}
    sub_reason_reversed: dict[str, int] = {}

    with open(TELEMETRY_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            total += 1
            sub_reason = rec.get("sub_reason", "unknown")
            sub_reason_totals[sub_reason] = sub_reason_totals.get(sub_reason, 0) + 1

            canonical = rec.get("canonical")
            asr = rec.get("asr")
            result = tier1.tier1_numeric_equivalence(canonical, asr)
            if result is not None:
                sub_reason_reversed[sub_reason] = sub_reason_reversed.get(sub_reason, 0) + 1
                reversed_records.append({
                    "canonical": canonical,
                    "asr": asr,
                    "prior_classification": rec.get("classification"),
                    "prior_sub_reason": sub_reason,
                    "prior_role": rec.get("role"),
                    "absorbed_ops": result.get("absorbed_ops"),
                    "diff_anchored": result.get("diff_anchored"),
                })

    summary = {
        "telemetry_path": TELEMETRY_PATH,
        "total_records": total,
        "reversed_to_tier1_match_count": len(reversed_records),
        "sub_reason_totals": sub_reason_totals,
        "sub_reason_reversed": sub_reason_reversed,
        "reversed_records": reversed_records,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
