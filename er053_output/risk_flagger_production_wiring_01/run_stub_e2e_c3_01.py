# -*- coding: utf-8 -*-
"""C3 stub E2E: Writer(entertainment runner main) -> RF -> Queue -> audio runner(scaffold -> tts)。課金API 0件。
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C3 (2026-10-10)。

実コード: entertainment runner main / W-1 / RF module / Review Queue / audio runner main(scaffold sha記録・ensure_rf_record・
          compute_cost_jpy_so_far・cost logger[cl.install実物でaudio out_dirのraw_usage_log.jsonlへ記録])。
stub: Research/B3(DEV fixture adapter)/LLM API(W-1 client, 英訳, Standard, RF call_fn)、audio側のscaffold API群とTTS生成関数。

シナリオ(同一の記事 er019_output/_c3_stub_e2e_01/run_01 に対し audio を複数回駆動):
  S0 : Writer main(初回、Advanced RF + Standard RF -> Queue保存)
  S1 : audio --stage scaffold(scaffold時sha記録) -> audio --stage tts 単独: 三者一致 -> RF再実行なし -> TTSへ
  S2 : Queueを空にした状態で audio --stage tts 単独: Queueなし -> その場でRF実行(Level別、run_label/producer記録) -> TTSへ
  S3 : S2の後にもう一度 --stage tts: 三者一致(audio側で作ったQueueも照合対象) -> RF再実行なし
  S4 : a2/article.md をscaffold後に変更: scaffold sha != source sha -> a2だけRF実行(b1bは一致で実行なし)
  S5 : RF全滅(call_fnが例外)でも TTSへ進む(RF_UNAVAILABLE、Queueへ保存)
  S6 : 予算超過(audio側raw_usage_logに上限超過の実額レコード) -> RF予算ガードがSTOP(伝播)=安全装置は回避されない
出力: er053_output/risk_flagger_production_wiring_01/stub_e2e_c3_01/summary.json
実行: .venv/Scripts/python.exe -X utf8 er053_output/risk_flagger_production_wiring_01/run_stub_e2e_c3_01.py
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
from unittest import mock

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
os.chdir(REPO)

import run_stub_e2e_c2_01 as c2  # noqa: E402  (stub部品を再利用: ScriptedClient/fake_*/stub_rf_call)
import er003_v1_en_direct_vfl_01_generate as vfl01  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import er012_e_family_entertainment_two_level_runner_01 as efam  # noqa: E402
import er019_family_x_audio_production_runner_01 as audio  # noqa: E402
import er019_family_x_entertainment_production_runner_01 as ent  # noqa: E402
import er053_dev_b3_fixture_adapter_01 as adapter  # noqa: E402
import er053_review_queue_01 as rq  # noqa: E402
import er053_risk_flagger_production_01 as rf  # noqa: E402

EV = c2.EVENTS
SLUG, RUN = "_c3_stub_e2e_01", "run_01"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    work = tempfile.mkdtemp(prefix="c3_stub_e2e_")
    qroot = os.path.join(work, "queue_root")
    audio_out = os.path.join(work, "audio_out")
    src = os.path.join("er019_output", SLUG, RUN)
    shutil.rmtree(os.path.join("er019_output", SLUG), ignore_errors=True)
    os.makedirs(os.path.dirname(src), exist_ok=True)
    adapter.build_fixture("meta", src)
    orig_save = rq.save_queue
    summary = {"purpose": "C3 stub E2E (API 0)", "article_id": rq.derive_article_id(src), "scenarios": {}}

    # ---------------- S0: Writer main ----------------
    client = c2.ScriptedClient()

    def wrapped_research(client_, topic, ledger_dir):
        EV.append("research_ledger(reuse fixture ledger)")
        return {"ledger_text": open(os.path.join(ledger_dir, "verified_fact_ledger.txt"), encoding="utf-8").read()}

    patches = [
        mock.patch.object(sys, "argv", ["runner", "--theme", "stub theme", "--slug", SLUG, "--out-dir", src, "--run-label", "C3_STUB_E2E"]),
        mock.patch.object(ent.cl, "install"),
        mock.patch.object(ent.vfl01, "get_client", return_value=client),
        mock.patch.object(ent, "run_research_and_ledger", side_effect=wrapped_research),
        mock.patch.object(efam, "assert_budget_ok", return_value=0.0),
        mock.patch.object(efam.adv_gen, "generate_family_x_faithful_translation", side_effect=c2.fake_adv),
        mock.patch.object(efam.adv_gen, "generate_family_x_in_one_line", side_effect=c2.fake_iol),
        mock.patch.object(efam.std_gen, "generate_family_x_standard_a2_no_heading", side_effect=c2.fake_std),
        mock.patch.object(rf, "default_call_fn", c2.stub_rf_call),
        mock.patch.object(rf.cl, "record"),
        mock.patch.object(rq, "save_queue", side_effect=lambda r, out_dir=None: orig_save(r, out_dir=out_dir, root=qroot)),
        mock.patch.object(ent.vfl01, "run_deviation_check", side_effect=c2.old_checker),
        mock.patch.object(ent.w1.time, "sleep", lambda s: None),
    ]
    for p in patches:
        p.start()
    try:
        ent.main()
    finally:
        for p in reversed(patches):
            p.stop()
    s0_rows = rq.read_index(qroot)
    summary["scenarios"]["S0_writer_main"] = {"queue_rows": [(r["article_id"], r["article_level"], r["run_label"]) for r in s0_rows],
                                              "rf_calls": sum(1 for e in EV if e.startswith("rf_call"))}
    # ---------------- audio側の共通ドライバ ----------------
    stub_state = {"mode": "ok", "calls": []}

    def audio_rf_call(model_key, model_id, system, user):
        stub_state["calls"].append(model_key)
        if stub_state["mode"] == "down":
            raise RuntimeError("stub API down")
        return ('{"flags":[]}', {"input_tokens": 4000, "output_tokens": 800, "reasoning_tokens": 300, "cached_tokens": 0},
                "rid_audio", model_id)

    def drive_audio(stage, tag):
        events = []
        stub_state["calls"] = []
        argv = ["audio", "--slug", SLUG, "--run", RUN, "--stage", stage, "--out-dir", audio_out,
                "--tts-backend", "speech_metadata_flash_lite"]
        fake_kp = mock.Mock(return_value={"canonicalization": {"status": "OK"}, "selection": {"status": "OK", "kp_backend_used": "db_hybrid"}})
        orig_rf = rf.run_risk_flagger
        ps = [mock.patch.object(sys, "argv", argv),
              mock.patch.object(vfl01, "get_client", lambda: object()),
              mock.patch.object(rq, "QUEUE_ROOT", qroot),
              mock.patch.object(rf, "default_call_fn", audio_rf_call),
              mock.patch.object(rf.time, "sleep", lambda s: None),
              mock.patch.object(audio.sc, "run_key_phrases", fake_kp),
              mock.patch.object(audio, "run_family_x_b1_scaffold", lambda c, p, d: {}),
              mock.patch.object(audio, "run_family_x_a2_scaffold", lambda c, p, d: {}),
              mock.patch.object(audio, "derive_japanese_title", lambda sd: {"japanese_title": "題", "source": "stub"}),
              mock.patch.object(audio, "generate_family_x_b1_segments", lambda *a, **k: events.append("tts:b1b")),
              mock.patch.object(audio, "generate_family_x_a2_segments", lambda *a, **k: events.append("tts:a2")),
              mock.patch.object(rf, "run_risk_flagger", lambda **kw: (events.append("rf:%s" % kw["article_level"]), orig_rf(**kw))[1])]
        for p in ps:
            p.start()
        try:
            audio.main()
        finally:
            for p in reversed(ps):
                p.stop()
        g_path = os.path.join(audio_out, audio.RF_TTS_GUARD_RECORD)
        guard = json.load(open(g_path, encoding="utf-8")) if os.path.exists(g_path) else {}
        return {"events": events, "rf_api_calls": len(stub_state["calls"]),
                "guard": {lv: {k: g.get(k) for k in ("action", "match", "mismatch_reasons", "rf_status", "queue_saved", "run_label")}
                          for lv, g in guard.items()}}

    # S1
    drive_audio("scaffold", "S1a")
    scaf = json.load(open(os.path.join(audio_out, audio.SCAFFOLD_SHA_RECORD), encoding="utf-8"))
    r1 = drive_audio("tts", "S1b")
    r1["scaffold_sha_record_matches_source"] = {lv: scaf[lv]["article_sha256"] == sha(os.path.join(src, lv, "article.md")) for lv in scaf}
    summary["scenarios"]["S1_scaffold_then_tts_alone_verified"] = r1
    # S2: Queue を空に(新しい空のqroot)
    qroot_old = qroot
    qroot = os.path.join(work, "queue_root_empty")
    os.makedirs(qroot)
    r2 = drive_audio("tts", "S2")
    r2["queue_rows"] = [(r["article_id"], r["article_level"], r["run_label"], r["producer"]) for r in rq.read_index(qroot)]
    summary["scenarios"]["S2_no_queue_rf_runs_in_audio"] = r2
    # S3
    summary["scenarios"]["S3_tts_again_verified"] = drive_audio("tts", "S3")
    # S4: a2を scaffold後に変更
    with open(os.path.join(src, "a2", "article.md"), "a", encoding="utf-8", newline="") as f:
        f.write("\nExtra sentence added after scaffold.\n")
    summary["scenarios"]["S4_a2_changed_after_scaffold"] = drive_audio("tts", "S4")
    # S5: RF全滅でもTTSへ(a2を再度変えて不一致にし、API全滅)
    with open(os.path.join(src, "b1b", "article.md"), "a", encoding="utf-8", newline="") as f:
        f.write("\nAnother edit.\n")
    stub_state["mode"] = "down"
    summary["scenarios"]["S5_rf_down_still_tts"] = drive_audio("tts", "S5")
    stub_state["mode"] = "ok"
    # S6直前の費用(RF Gemini実記録のみ、cost_usd併記分がaudio側集計で採用される)
    cost_before_s6, byp_before_s6 = audio.compute_cost_jpy_so_far(os.path.join(audio_out, "raw_usage_log.jsonl"))
    # S6: 予算超過
    with open(os.path.join(audio_out, "raw_usage_log.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "cost_usd": 10.0, "stage": "tts"}) + "\n")
    with open(os.path.join(src, "a2", "article.md"), "a", encoding="utf-8", newline="") as f:
        f.write("\nYet another edit.\n")
    try:
        r6 = drive_audio("tts", "S6")
        r6["stopped"] = False
    except Exception as e:  # noqa: BLE001
        r6 = {"stopped": True, "exception": type(e).__name__, "detail": str(e)[:160]}
    summary["scenarios"]["S6_budget_exceeded_stops"] = r6
    # 費用: audio out_dirのraw_usage_logにRF Geminiレコード(cost_usd併記)が入り、audio側集計で採用される
    log = os.path.join(audio_out, "raw_usage_log.jsonl")
    recs = [json.loads(l) for l in open(log, encoding="utf-8") if l.strip()]
    gem = [r for r in recs if r.get("provider") == "gemini" and str(r.get("stage", "")).startswith("risk_flag")]
    jpy_total = None
    try:
        jpy_total, byp = audio.compute_cost_jpy_so_far(log)
    except Exception as e:  # noqa: BLE001
        byp = repr(e)
    summary["audio_cost"] = {"rf_gemini_records": len(gem),
                             "sample": {k: gem[0].get(k) for k in ("model_id", "stage", "input_tokens", "output_tokens", "cost_usd")} if gem else None,
                             "all_successful_have_cost_usd": all(r.get("cost_usd") is not None for r in gem if r.get("success")),
                             "failed_call_records_without_cost_usd": sum(1 for r in gem if not r.get("success")),
                             "compute_cost_jpy_before_s6_injection": round(cost_before_s6, 4), "by_provider_before_s6": byp_before_s6,
                             "compute_cost_jpy_so_far_incl_s6_injected_10usd": jpy_total, "by_provider_incl_injected": byp}
    summary["old_checker_called"] = "OLD_CHECKER_CALLED" in EV
    dst = os.path.join(HERE, "stub_e2e_c3_01")
    os.makedirs(dst, exist_ok=True)
    with open(os.path.join(dst, "summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    shutil.rmtree(os.path.join("er019_output", SLUG), ignore_errors=True)
    shutil.rmtree(work, ignore_errors=True)
    print(json.dumps(summary["scenarios"], ensure_ascii=False, indent=1)[:6000])
    print(json.dumps(summary["audio_cost"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
