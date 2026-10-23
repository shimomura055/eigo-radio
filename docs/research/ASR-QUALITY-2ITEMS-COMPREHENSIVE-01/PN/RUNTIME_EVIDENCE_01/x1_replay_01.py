# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS PN 委任_04 X-1: 保存済みの実誤読wav(HR queue由来の人名誤読)を、**正式hook[XProvider]+正式adapter[evaluate_attempt_with_cascade]+実ASR**へ通す。
証拠区分=『保存wavのreplay(隔離run_dir)』。runner本体の新規生成経路ではない(新規生成経路の証拠はX-2/予備策)。
隔離: 隔離run_dir(本dir配下)/Ledger upsert・Perplexityはstub(呼出は記録)/HR queue書込はstub(件数のみ記録)/Store書込なし/cost logは本dir内。
実ASR: Primary=OpenAI gpt-4o-mini-transcribe(routing.transcribe)、Secondary=Azure STT(adapter内)。NER=gpt-6-luna(正式hook内、cl.install後)。"""
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))
EXCL = "--excl-ledger" in sys.argv           # 『初見の固有名詞』(Ledger未登録)を模擬: 受理判定のLedger語集合を空にする(Trial D1の『Ledger全除外』と同じ前提)
RUN = os.path.join(HERE, "x1_run_excl" if EXCL else "x1_run")
os.makedirs(RUN, exist_ok=True)

import er005_cost_logger as cl
cl.install(os.path.join(RUN, "raw_usage_log.jsonl"))
import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as sec
import er103_pnap_runner_hooks_01 as hooks
import er103_proper_noun_alarm_policy_01 as pol
import er103_run_entity_table_01 as ret

HR = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
CASES = [
    dict(id="n8_point_two", wav="er006_output/pool_pilot_01/pool_n8_airport_line/b1b/narration/point_two.wav", seg="full_story_part2"),
    dict(id="cafes_part1", wav="er006_output/pool_pilot_01/pool_n5_cafes/b1b/narration/full_story_part1.wav", seg="full_story_part1"),
]
only = [a for a in sys.argv[1:] if not a.startswith("-")]
if EXCL:
    pol.ledger_surface_tokens = lambda ledger=None: frozenset()
rows = [json.loads(l) for l in open(HR, encoding="utf-8") if l.strip()]
hr_calls, stage1_calls = [], []
sec._log_human_review = lambda d: hr_calls.append({"segment": d.get("segment_id"), "reason": d.get("reason") or d.get("review_reason")})
sec._resolve_unresolved_entity_for_review = lambda span: stage1_calls.append(span) or {"pronunciation_hint": "(stub: Ledger upsert/Perplexity not executed in isolated replay)", "confidence": "stub", "sources": []}

summary = []
for c in CASES:
    if only and c["id"] not in only:
        continue
    row = next(r for r in reversed(rows) if r["wav_path"].replace(chr(92), "/") == c["wav"])
    canon = row["canonical_text"]
    theme = os.path.join(RUN, c["id"])
    os.makedirs(os.path.join(theme, "b1b"), exist_ok=True)
    json.dump({"title": "Evidence replay", "part1": canon, "part2": "", "part3": "", "in_one_line": ""}, open(os.path.join(theme, "b1b", "parts.json"), "w", encoding="utf-8"))
    level_dir = os.path.join(theme, "b1b")
    out = {"case": c["id"], "wav": c["wav"], "canonical_text": canon[:200], "evidence_class": "stored_misread_wav_replay_isolated_run_dir" + ("+ledger_excluded_first_seen_name_simulation" if EXCL else ""), "ledger_excluded": EXCL}
    t0 = time.time()

    def fn():
        out["scope"] = pol.current_scope()
        tb = ret.current_table()
        out["table_at_run"] = None if tb is None else {"status": tb.status, "n_entries": len(tb.entries), "usable": [e.surface for e in tb.usable_entries()],
                                                       "grades": {e.surface: e.grade for e in tb.entries}, "meta_calls": tb.meta.get("calls"), "model": tb.meta.get("model")}
        asr_text, err = routing.transcribe(c["wav"], language="en-US")
        out["primary_asr"] = {"text": asr_text, "error": err}
        detail = {}
        ok, stop, cls = sec.evaluate_attempt_with_cascade(canon, asr_text, [], c["wav"], cascade_enabled=True, segment_id=c["seg"],
                                                          attempt_ctx={"slot": 1, "is_last_slot": True}, detail_out=detail)
        aj = detail.get("asr_judgement") or {}
        out["adapter"] = {"ok": ok, "technical_stop": bool(stop), "classification": cls.classification, "human_review_required": detail.get("human_review_required"),
                          "state": aj.get("state"), "azure_real_calls": (aj.get("adapter") or {}).get("azure_real_calls"),
                          "pronunciation_alarm_eval": detail.get("pronunciation_alarm_eval") or (detail.get("asr_judgement") or {}).get("pronunciation_alarm_eval"),
                          "reason_code": aj.get("reason_code")}
        pa = aj.get("pronunciation_alarm") or {}
        out["pronunciation_alarm"] = {"entity_table": pa.get("entity_table"), "nouns": pa.get("nouns")}
        out["alarm_records"] = [{"proper_noun": r.get("proper_noun"), "evidence": r["mismatch"].get("proper_noun_evidence"), "entity_table_basis": r.get("entity_table_basis"),
                                 "pronunciation_basis_hint": (r.get("pronunciation_basis") or {}).get("pronunciation_hint")} for r in aj.get("pronunciation_alarm_records") or []]
        out["asr_judgement"] = aj
        return ok

    hooks.run_with_alarm_hook("X", level_dir, fn, _ret_provider=lambda: ret.XProvider(theme))
    out["seconds"] = round(time.time() - t0, 1)
    out["hr_stub_calls"] = list(hr_calls)
    out["stage1_stub_calls"] = list(stage1_calls)
    et_path = os.path.join(theme, "audit", "entity_table.json")
    saved = json.load(open(et_path, encoding="utf-8")) if os.path.exists(et_path) else None
    out["entity_table_json"] = None if saved is None else {"schema": saved["schema"], "builder_version": saved["builder_version"], "status": saved["status"],
                                                          "n_covered": len(saved["covered_text_sha256"]), "raw": saved["raw"], "builds": saved["builds"]}
    rep = os.path.join(level_dir, "audit", "operator_alarm_report.md")
    out["operator_report_has_entity_section"] = os.path.exists(rep) and "実体表" in open(rep, encoding="utf-8").read()
    # --- 同一入力の再実行 = NER 0 call (coverage)
    n_before = len(json.load(open(et_path, encoding="utf-8"))["builds"]) if saved else 0
    llm_calls = []
    _orig = ret.default_llm
    ret.default_llm = lambda **k: (lambda text, pid: llm_calls.append(pid) or (_ for _ in ()).throw(RuntimeError("must not be called")))
    try:
        with pol.run_scope("X"):
            t2 = ret.ensure_table_safe(ret.XProvider(theme))
    finally:
        ret.default_llm = _orig
    out["rebuild_same_input"] = {"ner_calls": len(llm_calls), "status": t2.status if t2 else None, "covered_all_current": (t2.meta or {}).get("covered_all_current") if t2 else None}
    # --- X/Z-3: 保存entryからの継承再判定(API 0)
    aj = out.pop("asr_judgement")
    if aj.get("state") == pol.STATE_ALARM:
        import er019_family_x_validation_inheritance_01 as vi
        entry = {"status": "OK", "text": canon, "asr_text": out["primary_asr"]["text"], "sha256": "x1", "path": c["wav"], "asr_judgement": aj}
        with pol.run_scope("X"):
            r = vi.rejudge_with_current_judge(entry, "b1b", c["seg"])
        out["inheritance_rejudge"] = {"ok": r.get("ok"), "state": r.get("unified_state"), "alarm_rejudge": r.get("alarm_rejudge"), "secondary_new_calls": r.get("secondary_new_calls"),
                                      "api_calls": (r.get("asr_judgement_inherited", {}).get("inherited") or {}).get("api_calls"),
                                      "entity_table_updated": bool(((r.get("asr_judgement_inherited") or {}).get("pronunciation_alarm") or {}).get("entity_table"))}
        # rules_version不一致 -> 再判定NG
        old = ret.BUILDER_RULES_CONSTANT
        ret.BUILDER_RULES_CONSTANT = "changed_for_evidence"
        try:
            with pol.run_scope("X"):
                r2 = vi.rejudge_with_current_judge(entry, "b1b", c["seg"])
        finally:
            ret.BUILDER_RULES_CONSTANT = old
        out["inheritance_rejudge_rules_mismatch_ok"] = r2.get("ok")
        # Store guard: RET flag False(rollback) -> blocked
        import er078_reuse_value_guard_01 as g
        entry2 = dict(entry)
        entry2["asr_judgement_inherited"] = aj
        with pol.run_scope("X"):
            ok_g = g.guard_entry(entry2, canonical_text=canon, level="b1b", label=c["seg"])
        ret.RUN_ENTITY_TABLE_ENABLED = False
        try:
            with pol.run_scope("X"):
                bad_g = g.guard_entry(entry2, canonical_text=canon, level="b1b", label=c["seg"])
        finally:
            ret.RUN_ENTITY_TABLE_ENABLED = True
        out["store_guard"] = {"active": {"blocked": ok_g["blocked"], "reason": ok_g["reason"]}, "ret_flag_false": {"blocked": bad_g["blocked"], "reason": bad_g["reason"]}}
    summary.append(out)
    print(json.dumps({k: out.get(k) for k in ("case", "adapter", "table_at_run", "rebuild_same_input", "inheritance_rejudge", "store_guard", "seconds")}, ensure_ascii=False, default=str))
json.dump(summary, open(os.path.join(HERE, "x1_replay_01_result_%s%s.json" % ("_".join(only) or "all", "_excl" if EXCL else "_ledger_live")), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
