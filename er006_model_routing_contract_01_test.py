# ============================================================
# er006_model_routing_contract_01_test.py
# ER-006-MODEL-ROUTING-CONTRACT-01: Model Contract Regression Test
# ============================================================
from __future__ import annotations

import er006_model_routing_contract_01 as routing

POSITIVE_PROCESSES = [
    "QUERY_PLANNING", "TOPIC_SELECTION", "EVIDENCE_PACK", "VFL", "VERIFICATION",
    "B1_WRITER", "A2_WRITER", "WRITER_FACT_CHECK", "B1_SUPPORT", "A2_SUPPORT",
    "SUPPORT_FACT_CHECK",
]


def run():
    failures = []

    print("=== Positive: 各processのApproved Model(Luna)がPASSすること ===")
    for process in POSITIVE_PROCESSES:
        approved = routing.PROCESS_MODEL_MAP[process]
        try:
            result = routing.require_model(process, approved)
            ok = (result == approved) and approved == "gpt-5.6-luna"
        except routing.ModelContractViolation as e:
            ok = False
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {process} -> {approved}")
        if not ok:
            failures.append(f"{process} positive check")

    print("\n=== Negative: Solを渡すとAPI call前にFAILすること ===")
    for process in POSITIVE_PROCESSES:
        try:
            routing.require_model(process, "gpt-5.6-sol")
            ok = False  # 例外が飛ばなかった = 失敗
        except routing.ModelContractViolation:
            ok = True
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {process} + gpt-5.6-sol -> ModelContractViolation")
        if not ok:
            failures.append(f"{process} negative(sol) check")

    print("\n=== Negative: 未知modelを渡すとFAILすること ===")
    for process in POSITIVE_PROCESSES[:3]:
        try:
            routing.require_model(process, "gpt-99-mystery")
            ok = False
        except routing.ModelContractViolation:
            ok = True
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {process} + gpt-99-mystery -> ModelContractViolation")
        if not ok:
            failures.append(f"{process} negative(unknown) check")

    print("\n=== Negative: model未指定(None/空文字)もFAILすること ===")
    for process in POSITIVE_PROCESSES[:3]:
        for bad_value in (None, ""):
            try:
                routing.require_model(process, bad_value)
                ok = False
            except routing.ModelContractViolation:
                ok = True
            status = "OK" if ok else "FAIL"
            print(f"[{status}] {process} + {bad_value!r} -> ModelContractViolation")
            if not ok:
                failures.append(f"{process} negative(unspecified={bad_value!r}) check")

    print("\n=== Provider: Search/TTS/ASR ===")
    provider_cases = [
        ("EXCEPTION_SEARCH", "perplexity", True),
        ("EXCEPTION_SEARCH", "google", False),
        ("TTS", "gemini-2.5-pro-preview-tts", True),
        ("TTS", "openai-tts", False),
        ("ASR", "azure", True),
        ("ASR", "google-stt", False),
    ]
    for process, provider, should_pass in provider_cases:
        try:
            routing.require_provider(process, provider)
            passed = True
        except routing.ModelContractViolation:
            passed = False
        ok = (passed == should_pass)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {process} + {provider} -> {'PASS' if should_pass else 'FAIL'}(expected)")
        if not ok:
            failures.append(f"{process}/{provider} provider check")

    print("\n=== Fallback: modelが変わらないことの確認(vfl01の関数シグネチャ) ===")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import inspect
    for fn_name in ("run_writer_no_search", "run_writer_with_technical_retry", "run_deviation_check"):
        fn = getattr(vfl01, fn_name)
        params = inspect.signature(fn).parameters
        ok = "model" in params
        status = "OK" if ok else "FAIL"
        print(f"[{status}] vfl01.{fn_name} accepts explicit model= override")
        if not ok:
            failures.append(f"vfl01.{fn_name} missing model param")

    if failures:
        raise AssertionError(f"{len(failures)}件の契約テストが失敗した: {failures}")
    print(f"\nOK: 全テストPASS")


if __name__ == "__main__":
    run()
