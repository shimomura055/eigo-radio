# -*- coding: utf-8 -*-
"""ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01 harness単体テスト(mock、API無し)。"""
import types

import er052_all6_writer_trial_01_run as h
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er019_family_x_ja_writer_o_r1_r2_01 as jaw
import er006_model_routing_contract_01 as routing


def _fake_mods():
    calls = []

    def dev(client, ledger, article, model="gpt-mock-baseline", **k):
        calls.append(("dev", model)); return {"parsed": {}}

    def tr(ja, *a, client=None, model=None, **k):
        calls.append(("tr", model)); return None

    def iol(client, title, body, *a, model=None, **k):
        calls.append(("iol", model)); return None

    return calls, {
        "vfl01": types.SimpleNamespace(run_deviation_check=dev),
        "adv_gen": types.SimpleNamespace(generate_family_x_faithful_translation=tr,
                                         generate_family_x_in_one_line=iol),
        "jaw": types.SimpleNamespace(WRITER_MODEL="gpt-mock-baseline"),
    }


def test_all6_patches_all_targets_and_restore():
    calls, mods = _fake_mods()
    saved = h.apply_all6_patches(mods)
    assert mods["jaw"].WRITER_MODEL == "gpt-6-luna"
    mods["vfl01"].run_deviation_check(None, "L", "A")
    mods["vfl01"].run_deviation_check(None, "L", "A", hook_aware=False, include_related_fact_id=True)
    mods["adv_gen"].generate_family_x_faithful_translation("ja", client=None)
    mods["adv_gen"].generate_family_x_in_one_line(None, "t", "b")
    assert calls == [("dev", "gpt-6-luna"), ("dev", "gpt-6-luna"), ("tr", "gpt-6-luna"), ("iol", "gpt-6-luna")]
    # 明示指定されたmodelは尊重される
    mods["vfl01"].run_deviation_check(None, "L", "A", model="gpt-mock-baseline")
    assert calls[-1] == ("dev", "gpt-mock-baseline")
    h.restore_patches(saved)
    assert mods["jaw"].WRITER_MODEL == "gpt-mock-baseline"
    mods["vfl01"].run_deviation_check(None, "L", "A")
    assert calls[-1] == ("dev", "gpt-mock-baseline")


def test_baseline_leaves_real_modules_unchanged():
    before = (jaw.WRITER_MODEL, vfl01.run_deviation_check, adv_gen.generate_family_x_faithful_translation,
              adv_gen.generate_family_x_in_one_line)
    # baseline経路ではapply_all6_patchesは呼ばれない(main: saved=None)。呼ばない限り無変更であることを確認。
    assert jaw.WRITER_MODEL == routing.WRITER_MODEL  # WIRING-01以降: Production契約=gpt-6-luna
    assert before[1] is vfl01.run_deviation_check


def test_real_modules_patch_and_restore():
    orig = (jaw.WRITER_MODEL, vfl01.run_deviation_check, adv_gen.generate_family_x_faithful_translation,
            adv_gen.generate_family_x_in_one_line)
    saved = h.apply_all6_patches()
    try:
        assert jaw.WRITER_MODEL == "gpt-6-luna"
        assert vfl01.run_deviation_check is not orig[1]
        assert routing.WRITER_MODEL == "gpt-6-luna"         # Routing契約は不変(WIRING-01以降の契約値)
        assert vfl01.MODEL == routing.WRITER_MODEL           # Production定数は不変(routing参照)
    finally:
        h.restore_patches(saved)
    assert (jaw.WRITER_MODEL, vfl01.run_deviation_check, adv_gen.generate_family_x_faithful_translation,
            adv_gen.generate_family_x_in_one_line) == orig


def test_override_requires_reason():
    assert h.resolve_all6_model("B1_WRITER") == "gpt-6-luna"
    import pytest
    # WIRING-01以降: gpt-6-lunaは承認済みmodelのためreason無しでも通る。
    # 承認外(旧5.6)はreason無しだとfail-closed、reason付きのみ許可。
    assert routing.require_model_or_override("B1_WRITER", "gpt-6-luna") == "gpt-6-luna"
    with pytest.raises(Exception):
        routing.require_model_or_override("B1_WRITER", "gpt-5.6-luna")
    assert routing.require_model_or_override(
        "B1_WRITER", "gpt-5.6-luna", override_reason="旧Trial再現") == "gpt-5.6-luna"


def test_collect_models(tmp_path):
    d = tmp_path / "r"; d.mkdir()
    (d / "raw_usage_log.jsonl").write_text(
        '{"stage":"ja_original","model_id":"gpt-6-luna"}\n{"stage":"advanced","model_id":"gpt-6-luna"}\n', encoding="utf-8")
    m = h.collect_models(str(d))
    assert m["ja_original"] == ["gpt-6-luna"] and m["advanced"] == ["gpt-6-luna"]
