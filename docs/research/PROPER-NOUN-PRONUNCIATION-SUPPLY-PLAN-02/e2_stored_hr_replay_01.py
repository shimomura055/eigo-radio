# -*- coding: utf-8 -*-
"""保存HR queue行(最終slot NG)の保存転写(Primary/Secondary)を実関数 evaluate_attempt_with_cascade_detail で再判定し、Stage 1 ON/OFFの判定出力が一致することを確認(API 0・実HTTP 0)。
research(Perplexity)は常に401相当の失敗を返すstub(=Ledger/sidecarへ何も書かない)。Ledger/sidecar/HR pathは一時dirへ隔離。"""
import json, os, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
import er006_asr_provider_routing_01 as routing
import er006_pronunciation_ledger_01 as L
import er006_secondary_asr_01 as sec

HRQ = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
rows = [json.loads(l) for l in open(HRQ, encoding="utf-8") if l.strip()]
rows = [r for r in rows if "Temp" not in r["wav_path"] and "tmp" not in r["wav_path"].lower() and r.get("steps")]
tmp = tempfile.mkdtemp()
shutil.copyfile("er006_output/pronunciation_ledger_01/ledger.json", os.path.join(tmp, "ledger.json"))
L.LEDGER_PATH = os.path.join(tmp, "ledger.json")
sec.HUMAN_REVIEW_LOG_PATH = os.path.join(tmp, "hr.jsonl")
sec.pronun_research.research_pronunciations = lambda *a, **k: {"status": "FAILED", "http_status": 401}
sec._pron_supply_fetch = lambda *a, **k: None

def judge(r, enabled):
    sec.PRON_SUPPLY_STAGE1_ENABLED = enabled
    steps = r["steps"]
    prim = next((s.get("text") for s in steps if str(s.get("step", "")).startswith("primary")), None) or ""
    secs = [s.get("text") or "" for s in steps if str(s.get("step", "")).startswith("secondary")]
    routing.transcribe = lambda *a, **k: (prim, None)
    sec.get_full_text_via_azure_stt_with_phrase_list = lambda *a, **k: ((secs[0] if secs else ""), None)
    d = sec.evaluate_attempt_with_cascade_detail(r["canonical_text"], prim, [], r["wav_path"], cascade_enabled=True, attempt_ctx={"slot": 3, "is_last_slot": True})
    return {k: d.get(k) for k in ("verified", "final_status", "stop_retrying", "human_review_required", "cascade_invoked")} | {
        "classification": getattr(d.get("classification"), "classification", None),
        "steps": json.dumps(d.get("steps"), ensure_ascii=False, default=str, sort_keys=True)}, d

n = diff = with_lookups = errs = 0
actions = {}
for r in rows:
    try:
        a, da = judge(r, True)
        b, db = judge(r, False)
    except Exception as e:
        errs += 1
        continue
    n += 1
    diff += (a != b)
    for sp, v in (da.get("pronunciation_lookups") or {}).items():
        with_lookups += 1
        actions[v.get("lookup_action")] = actions.get(v.get("lookup_action"), 0) + 1
    # OFF側にStage 1の追加キーが無いこと
    for v in (db.get("pronunciation_lookups") or {}).values():
        assert "lookup_action" not in v
print(json.dumps({"rows_replayed": n, "errors": errs, "judgement_diff_ON_vs_OFF": diff, "spans_with_lookups_ON": with_lookups, "lookup_actions_ON": actions}, ensure_ascii=False))
