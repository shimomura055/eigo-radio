# ============================================================
# er009_n1_routing_governance_10_legacy_scan_test.py
# ER-009-N1-POINT-RETRY-ROUTING-GOVERNANCE-10: Routing恒久対策 Regression Test
# ============================================================
# 検証項目:
#   1. Legacy Sol Hardcode Validator(er009_n1_routing_governance_10_legacy_scan)
#      が新パイプライン内で違反0件を報告すること
#   2. Trial-08で実際に問題を起こした根本チェーン(vfl01.MODEL)が、現在
#      Routing SSOT(Luna)へ直接一致していること(この一致が崩れたら
#      Trial-08と同じ回帰が起きる、という直接的な回帰guard)
#   3. Runtime Guard(require_model_or_override)がoverride_reasonなしでは
#      fail-closed、override_reasonありでのみ非Approved Modelを通すこと
from __future__ import annotations

import er003_v1_en_direct_vfl_01_generate as vfl01
import er006_model_routing_contract_01 as routing
import er009_n1_routing_governance_10_legacy_scan as legacy_scan


def run():
    failures = []

    print("=== 1. Legacy Sol Hardcode Validator: 新パイプライン内で違反0件 ===")
    result = legacy_scan.scan_repository()
    ok = len(result["violations"]) == 0 and result["scanned_files"] > 0
    print(f"[{'OK' if ok else 'FAIL'}] scanned={result['scanned_files']} "
          f"violations={len(result['violations'])}")
    for v in result["violations"]:
        print(f"    -> {v['file']}:{v['line']}: {v['text']}")
    if not ok:
        failures.append("legacy_scan violations")

    print("\n=== 2. vfl01.MODEL(Trial-08根本原因チェーン)がRouting SSOT(Luna)と一致 ===")
    ok = (vfl01.MODEL == routing.WRITER_MODEL == "gpt-5.6-luna")
    print(f"[{'OK' if ok else 'FAIL'}] vfl01.MODEL={vfl01.MODEL!r} "
          f"routing.WRITER_MODEL={routing.WRITER_MODEL!r}")
    if not ok:
        failures.append("vfl01.MODEL != routing.WRITER_MODEL (regression: Trial-08と同じ経路が再発する)")

    print("\n=== 3a. require_model_or_override: override_reasonなしはfail-closed ===")
    try:
        routing.require_model_or_override("A2_WRITER", "gpt-5.6-sol")
        ok = False
    except routing.ModelContractViolation:
        ok = True
    print(f"[{'OK' if ok else 'FAIL'}] override_reason省略時、Sol指定はModelContractViolation")
    if not ok:
        failures.append("require_model_or_override should fail-closed without override_reason")

    print("\n=== 3b. require_model_or_override: override_reasonありなら明示的に許可 ===")
    try:
        resolved = routing.require_model_or_override(
            "A2_WRITER", "gpt-5.6-sol", override_reason="単体テスト: override機構自体の確認")
        ok = resolved == "gpt-5.6-sol"
    except routing.ModelContractViolation:
        ok = False
    print(f"[{'OK' if ok else 'FAIL'}] override_reason明示時のみ非Approved Modelを許可")
    if not ok:
        failures.append("require_model_or_override should allow override when reason given")

    print("\n=== 3c. require_model_or_override: override_reasonが空文字なら通常通りfail-closed ===")
    try:
        routing.require_model_or_override("A2_WRITER", "gpt-5.6-sol", override_reason="   ")
        ok = False
    except routing.ModelContractViolation:
        ok = True
    print(f"[{'OK' if ok else 'FAIL'}] 空白のみのoverride_reasonは無効")
    if not ok:
        failures.append("blank override_reason should not bypass fail-closed check")

    print("\n=== 3d. require_model_or_override: Approved Model一致時はoverride_reason有無に関係なくPASS ===")
    try:
        resolved = routing.require_model_or_override("A2_WRITER", routing.WRITER_MODEL)
        ok = resolved == routing.WRITER_MODEL
    except routing.ModelContractViolation:
        ok = False
    print(f"[{'OK' if ok else 'FAIL'}] Approved Model一致時はPASS")
    if not ok:
        failures.append("require_model_or_override should pass approved model without override_reason")

    print("\n" + "=" * 60)
    if failures:
        print(f"FAIL: {len(failures)}件の失敗")
        for f in failures:
            print(f"  - {f}")
        raise SystemExit(1)
    print("ALL PASS")


if __name__ == "__main__":
    run()
