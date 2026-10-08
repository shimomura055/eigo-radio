# -*- coding: utf-8 -*-
# er052_gpt6_wiring_probe_01 の単体テスト(mock、API call無し)
import types

import pytest

import er006_model_routing_contract_01 as routing
import er052_gpt6_wiring_probe_01 as probe


def test_require_override_always_has_reason_and_restores():
    orig = routing.require_model
    state = probe.install_patches()
    try:
        probe.REQUIRE_LOG.clear()
        # 契約上5.6のprocessでも、probe中は6-lunaを理由付きoverrideで返す
        assert routing.require_model("B1_SUPPORT", "gpt-5.6-luna") == probe.PROBE_MODEL
        assert routing.require_model("VFL", None) == probe.PROBE_MODEL
        assert len(probe.REQUIRE_LOG) == 2
        assert all(r["override_reason"] and r["override_reason"].strip() for r in probe.REQUIRE_LOG)
        # 未知processはfail-closed(契約の挙動は維持)
        with pytest.raises(routing.ModelContractViolation):
            routing.require_model("NO_SUCH_PROCESS", "x")
    finally:
        probe.uninstall_patches(state)
    assert routing.require_model is orig


def test_production_files_unchanged_by_install_uninstall():
    before = {p: probe.sha256_file(p) for p in probe.PRODUCTION_FILES}
    state = probe.install_patches()
    probe.uninstall_patches(state)
    after = {p: probe.sha256_file(p) for p in probe.PRODUCTION_FILES}
    assert before == after


def test_summarize_response_cost_and_web_count():
    usage = types.SimpleNamespace(input_tokens=1_000_000, output_tokens=1_000_000,
                                  input_tokens_details=types.SimpleNamespace(cached_tokens=0))
    resp = types.SimpleNamespace(
        model="gpt-6-luna", id="r1", status="completed", incomplete_details=None, usage=usage,
        output=[types.SimpleNamespace(type="web_search_call"), types.SimpleNamespace(type="message")],
        output_text="{}", reasoning=types.SimpleNamespace(effort="medium"))
    rec = probe.summarize_response(resp, {"model": "gpt-6-luna", "reasoning": {"effort": "medium"},
                                          "text": {"format": {"type": "json_schema"}}}, 1.0)
    assert rec["web_search_call_count"] == 1
    assert rec["schema_ok"] is True
    # 0.10 + 0.50 + 0.01(web)
    assert abs(rec["cost_usd"] - 0.61) < 1e-9
