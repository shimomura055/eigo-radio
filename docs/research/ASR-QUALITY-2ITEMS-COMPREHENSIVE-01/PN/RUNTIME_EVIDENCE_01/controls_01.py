# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS PN 委任_04 X/Z-3(一部)・X/Z-4・対照(API 0)。
 (1) 対照: X-2で実ASRが返した転写(Primary/Secondary)を、RETなし(=従来)・RETあり(Ledger全除外=初見名)で判定 -> 従来はNO_PROPER_NOUN_EVIDENCE(HR行き)だった事実
 (2) rollback(RUN_ENTITY_TABLE_ENABLED=False)・scope外(A/B/C相当)・dry_run相当: 判定が従来と一致(adapter_table()=None、hookはNER 0)
 (3) baseline署名(RET実装前に凍結した1516件)と、RETなし/空表/無関係表/rollbackでバイト一致
 (4) operator報告: 表の根拠と発音の根拠が別欄"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))
import er006_preprod_hardening_01_validation as val
import er103_pnap_runner_hooks_01 as hooks
import er103_proper_noun_alarm_policy_01 as pol
import er103_ret_baseline_signature_01 as base
import er103_run_entity_table_01 as ret

out = {}
theme = os.path.join(HERE, "x2_run", "theme_n8")
tr = json.load(open(os.path.join(theme, "b1b", "audit", "tts_generation_results.json"), encoding="utf-8"))
seg = tr["segments"]["full_story_part2"]
aj = seg.get("asr_judgement") or seg.get("asr_judgement_inherited") or {}
canon = (aj.get("pronunciation_alarm") or {}).get("tts_input_text") or seg["canonical_text"]
prim, sec_ = (aj.get("primary") or {}).get("text"), (aj.get("secondary") or {}).get("text")
out["transcripts"] = {"canonical": canon[:120], "primary": prim[:120], "secondary": (sec_ or "")[:120]}
kw = dict(canonical_text=canon, primary_cls=val.classify_asr_match(canon, prim), secondary_cls=val.classify_asr_match(canon, sec_), primary_text=prim, secondary_text=sec_,
          judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role="FULL_STORY", p3_entry="p3_primary_ng", enabled=True)
tb = ret.restore_from_audit_block  # noqa
et_entries = (aj.get("pronunciation_alarm") or {}).get("entity_table", {}).get("entries_used") or (seg.get("asr_judgement_inherited") or {}).get("pronunciation_alarm", {}).get("entity_table", {}).get("entries_used")
table = ret.table_from_saved_entries(et_entries)
d0 = pol.evaluate_alarm_eligibility(ledger_surfaces=frozenset(), **kw)
d1 = pol.evaluate_alarm_eligibility(ledger_surfaces=frozenset(), entity_table=table, **kw)
out["control_first_seen_name"] = {"without_RET(従来)": [d0.accept, d0.reason, d0.detail if not d0.accept else None], "with_RET": [d1.accept, d1.reason, [x.evidence for x in d1.diffs]]}

# rollback / scope外 / adapter_table
with pol.run_scope("X"):
    active = ret.adapter_table(), ret.is_active_for_run()
    ret.RUN_ENTITY_TABLE_ENABLED = False
    try:
        rb = ret.adapter_table(), ret.is_active_for_run()
    finally:
        ret.RUN_ENTITY_TABLE_ENABLED = True
with ret.run_table(table):
    outside = ret.adapter_table(), ret.is_active_for_run()
    with pol.run_scope("X"):
        inside = ret.adapter_table() is table, ret.is_active_for_run()
out["scope_matrix"] = {"scope内・holderなし": [active[0], active[1]], "scope内・flag False(rollback)": [rb[0], rb[1]], "scope外・holderあり(A/B/C相当)": [outside[0], outside[1]], "scope内・holderあり": list(inside)}

# hook: scope外/flag OFF/rollback は NER 0
calls = []
_orig = ret.default_llm
ret.default_llm = lambda **k: (lambda t, p: calls.append(p) or {"entities": []})
try:
    pol.PROPER_NOUN_ALARM_POLICY_ENABLED = False
    hooks.run_with_alarm_hook("X", os.path.join(HERE, "x_ctrl_unused"), lambda: None, _ret_provider=lambda: ret.XProvider(theme))
    pol.PROPER_NOUN_ALARM_POLICY_ENABLED = True
    ret.RUN_ENTITY_TABLE_ENABLED = False
    hooks.run_with_alarm_hook("X", os.path.join(HERE, "x_ctrl_unused"), lambda: None, _ret_provider=lambda: ret.XProvider(theme))
finally:
    ret.RUN_ENTITY_TABLE_ENABLED = True
    pol.PROPER_NOUN_ALARM_POLICY_ENABLED = True
    ret.default_llm = _orig
out["hook_ner_calls_when_pnap_off_or_ret_rollback"] = len(calls)
import shutil
shutil.rmtree(os.path.join(HERE, "x_ctrl_unused"), ignore_errors=True)   # hookが書いた報告dir(PNAP ON+rollback分)は対照のため破棄

# baseline署名
b = base.load()
sigs = {}
for name, tbl in (("None", None), ("empty", ret.EntityTable([])), ("unrelated", ret.EntityTable([ret.Entry("Zzyzx Qwertyuiop", ["zzyzx", "qwertyuiop"], "person", "confirmed", ["t"], ["zzyzx", "qwertyuiop"], [])]))):
    sigs[name] = [s for _d, s in base.recompute(entity_table=tbl)] == b["signatures"]
ret.RUN_ENTITY_TABLE_ENABLED = False
try:
    sigs["rollback(flag False, None)"] = [s for _d, s in base.recompute()] == b["signatures"]
finally:
    ret.RUN_ENTITY_TABLE_ENABLED = True
out["baseline_signature"] = {"n": b["n"], "groups": b["groups"], "byte_identical": sigs, "frozen_total_sha256": b["total_sha256"]}
json.dump(out, open(os.path.join(HERE, "controls_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:3500])
