# -*- coding: utf-8 -*-
"""C2配線のstub E2E(課金API 0件、RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2)。

Production正式入口 er019_family_x_entertainment_production_runner_01.main() を **実コードのまま** 駆動し、外部APIだけをstub化する:
  - 注記済みB3: DEV fixture adapter(Trial成果物から契約ファイルを組立。producer="trial_fixture")
  - 契約検証(V1-V10)・W-1(R0 Luna -> R1/R2 Astra、client=scripted stub)・efam.run_writer_stage(adv/std生成関数だけstub)・
    Risk Flagger(実module、4条件逐次、API呼出関数だけstub)・Review Queue(実module、保存先は一時dir)は実コード。
  - vfl01.run_deviation_check は呼ばれたら失敗(旧Checker不到達の実行確認)。
出力: er053_output/risk_flagger_production_wiring_01/stub_e2e_c2_01/summary.json(イベント順・生成ファイル・sha・RF/Queue要約)
実行: .venv/Scripts/python.exe -X utf8 er053_output/risk_flagger_production_wiring_01/run_stub_e2e_c2_01.py
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
from types import SimpleNamespace
from unittest import mock

sys.dont_write_bytecode = True
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
os.chdir(REPO)

import er005_cost_logger as cl  # noqa: E402
import er012_e_family_entertainment_two_level_runner_01 as efam  # noqa: E402
import er019_family_x_entertainment_production_runner_01 as runner  # noqa: E402
import er053_dev_b3_fixture_adapter_01 as adapter  # noqa: E402
import er053_review_queue_01 as rq  # noqa: E402
import er053_risk_flagger_production_01 as rf  # noqa: E402

EVENTS = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


class FakeResp:
    def __init__(self, text, model, rid):
        self.output_text, self.model, self.id = text, model, rid
        self.usage = SimpleNamespace(input_tokens=100, output_tokens=50)


class ScriptedClient:
    """W-1のLuna R0 / Astra R1 / Astra R2 を順に返す。"""
    def __init__(self):
        self.responses = self
        self.n = 0
        self.scripts = [("メタの話\n人間が電話をしたというテストがありました。【事実1】\nこれは面白いですね。\n", "gpt-6-luna"),
                        ("# タイトル\n\n本文その1です。続きの文です。", "gpt-6-astra"),
                        ("# 新タイトル\n\n本文その2です。続きの文です。", "gpt-6-astra")]

    def create(self, **kw):
        EVENTS.append("w1_api_call:" + str(kw.get("model")))
        text, model = self.scripts[self.n]
        self.n += 1
        return FakeResp(text, model, "resp_%d" % self.n)


ADV_BODY = "Advanced paragraph one. It has two sentences.\n\nAdvanced paragraph two.\n\nAdvanced paragraph three."
STD_TEXT = "# Std Title\n\nSimple one.\n\nSimple two.\n\nSimple three.\n\n## In one line\nOne closing sentence."


def fake_adv(ja_text, client=None, must_fix=None, **kw):
    EVENTS.append("advanced_translation")
    return SimpleNamespace(title="Adv Title", body=ADV_BODY, model_id_actual="gpt-6-luna", model_id_requested="gpt-6-luna",
                           response_id="a1", usage={}, cost_usd=0.0, cost_jpy=0.0, attempts=1, retried=False, fallback_detected=False,
                           structure_status="STRUCTURE_PASS", elapsed_seconds=0.0)


def fake_iol(client, title, body, **kw):
    EVENTS.append("in_one_line(M1a ja_text=%s ledger_text=%s)" % (bool(kw.get("ja_text")), bool(kw.get("ledger_text"))))
    return {"text": "One closing sentence."}


def fake_std(advanced_text, client=None, must_fix=None, **kw):
    EVENTS.append("standard_level_adjust")
    return SimpleNamespace(text=STD_TEXT, model_id_actual="gpt-6-luna", model_id_requested="gpt-6-luna", response_id="s1", usage={},
                           cost_usd=0.0, cost_jpy=0.0, attempts=1, retried=False, fallback_detected=False,
                           structure_status="STRUCTURE_PASS", elapsed_seconds=0.0, checks={})


def stub_rf_call(model_key, model_id, system, user):
    EVENTS.append("rf_call:%s" % model_key)
    return ('{"flags":[]}', {"input_tokens": 10, "output_tokens": 5, "cached_tokens": 0}, "rid", model_id)


def old_checker(*a, **k):
    EVENTS.append("OLD_CHECKER_CALLED")
    raise AssertionError("old checker called")


def main():
    work = tempfile.mkdtemp(prefix="c2_stub_e2e_")
    out_dir = os.path.join(work, "article_stub")
    qroot = os.path.join(work, "queue_root")
    adapter.build_fixture("meta", out_dir)
    orig_save = rq.save_queue
    orig_assert = efam.assert_budget_ok
    summary = {"purpose": "C2 stub E2E (API 0)", "out_dir_is_temp": True}
    client = ScriptedClient()

    def wrapped_research(client_, topic, ledger_dir):
        EVENTS.append("research_ledger(reuse fixture ledger)")
        return {"ledger_text": open(os.path.join(ledger_dir, "verified_fact_ledger.txt"), encoding="utf-8").read()}

    def wrapped_budget(*a, **k):
        EVENTS.append("budget_check:%s" % (a[2] if len(a) > 2 else ""))
        return 0.0

    def drive(argv):
        patches = [
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(runner.cl, "install"),
            mock.patch.object(runner.vfl01, "get_client", return_value=client),
            mock.patch.object(runner, "run_research_and_ledger", side_effect=wrapped_research),
            mock.patch.object(efam, "assert_budget_ok", side_effect=wrapped_budget),
            mock.patch.object(efam.adv_gen, "generate_family_x_faithful_translation", side_effect=fake_adv),
            mock.patch.object(efam.adv_gen, "generate_family_x_in_one_line", side_effect=fake_iol),
            mock.patch.object(efam.std_gen, "generate_family_x_standard_a2_no_heading", side_effect=fake_std),
            mock.patch.object(rf, "default_call_fn", stub_rf_call),
            mock.patch.object(rf.cl, "record"),
            mock.patch.object(rq, "save_queue", side_effect=lambda r, out_dir=None: (EVENTS.append("queue_save:%s" % r["article_level"]),
                                                                                      orig_save(r, out_dir=out_dir, root=qroot))[1]),
            mock.patch.object(runner.vfl01, "run_deviation_check", side_effect=old_checker),
            mock.patch.object(runner.w1.time, "sleep", lambda s: None),
        ]
        for p in patches:
            p.start()
        try:
            runner.main()
        finally:
            for p in reversed(patches):
                p.stop()

    drive(["runner", "--theme", "stub theme", "--slug", "stub", "--out-dir", out_dir, "--run-label", "C2_STUB_E2E"])
    summary["main"] = "completed (Mandatory STOP reached)"
    EVENTS.append("--- second invocation: --stage standard (reuse ja_writer after provenance check) ---")
    drive(["runner", "--theme", "stub theme", "--slug", "stub", "--out-dir", out_dir, "--stage", "standard", "--run-label", "C2_STUB_E2E_RESUME"])
    summary["second_invocation"] = "completed (reuse path, no W-1 API call)"

    summary["events"] = EVENTS
    summary["w1_api_calls"] = [e for e in EVENTS if e.startswith("w1_api_call")]
    summary["old_checker_called"] = "OLD_CHECKER_CALLED" in EVENTS
    summary["files"] = {k: sha(os.path.join(out_dir, k)) for k in ("ja_writer/revision2.md", "b1b/article.md", "a2/article.md")
                        if os.path.exists(os.path.join(out_dir, k))}
    ev = json.load(open(os.path.join(out_dir, "ja_writer", "runtime_evidence.json"), encoding="utf-8"))
    summary["w1_runtime_evidence"] = {k: ev.get(k) for k in ("chain_method", "annotated_md_sha256", "annotation_manifest_producer")}
    ep = json.load(open(os.path.join(out_dir, "entry_point.json"), encoding="utf-8"))
    summary["entry_point_risk_flagger"] = ep.get("risk_flagger")
    summary["entry_point_run_label_of_last_invocation"] = ep["args"].get("run_label")
    summary["queue_index"] = rq.read_index(qroot)
    summary["a2_derived_from_advanced"] = json.load(open(os.path.join(out_dir, "a2", "audit", "derived_from_advanced_sha256.json"),
                                                          encoding="utf-8"))
    summary["no_old_checker_files"] = {
        "b1b/audit/deviation_check.json": os.path.exists(os.path.join(out_dir, "b1b", "audit", "deviation_check.json")),
        "a2/audit/deviation_check.json": os.path.exists(os.path.join(out_dir, "a2", "audit", "deviation_check.json")),
        "ja_writer/audit/deviation_checks": os.path.exists(os.path.join(out_dir, "ja_writer", "audit", "deviation_checks"))}
    dst = os.path.join(REPO, "er053_output", "risk_flagger_production_wiring_01", "stub_e2e_c2_01")
    os.makedirs(dst, exist_ok=True)
    with open(os.path.join(dst, "summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    shutil.rmtree(work, ignore_errors=True)
    print(json.dumps({k: summary[k] for k in ("main", "second_invocation", "old_checker_called", "w1_api_calls")}, ensure_ascii=False, indent=1))
    print("events:")
    for e in EVENTS:
        print("  ", e)


if __name__ == "__main__":
    main()
