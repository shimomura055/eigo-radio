"""OPEN-479 影響分析 replay (API 0). Z会話clip(clip_kind=dialogue)の保存済みjudgement入力を使い、
segment_id=None(現状) と segment_id=<clip id>(修正後) で判定を決定論的に再計算して差分を数える。
Level1: 全attempt(primary転写)に対し val.evaluate_attempt。
Level2: 最終attempt(asr_judgement保存あり)に対し evaluate_attempt_with_cascade_detail(Azure=保存済みSecondary転写に差替、
        CS等価層のlocal whisperは差替=到達したら記録、is_last_slot=False固定でHR/Perplexity呼出なし)。
usage: python open479_replay_01.py <out.json> [--after]   (--afterは修正後コードの再実行用ラベル)"""
import json, glob, sys, os, collections
sys.path.insert(0, os.getcwd())
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sa
import er078_asr_unified_judge_01 as uj

OUT = sys.argv[1]
SKIP = ("run_mock", "STALE", "pre_regen", "backup", "preserve", "evidence_0", "run_dsw_evidence", "smoke", "pnmh")
files = [f for f in glob.glob("er026_output/family_z_*/**/audit/tts_generation_results.json", recursive=True)
         if not any(s in f.replace("\\", "/") for s in SKIP)]

# --- patches (API 0) ---
_state = {"sec": None, "cs_reached": 0}
def _fake_call(self):
    t = _state["sec"]
    if t is None:
        return uj.SecondaryOutcome(None, error="replay_no_stored_secondary")
    return uj.SecondaryOutcome(t, error=None)
sa._AzureShared._call = _fake_call
_orig_cs = sa._connected_speech_equivalence_layer_attempt
def _fake_cs(*a, **k):
    _state["cs_reached"] += 1
    return None
sa._connected_speech_equivalence_layer_attempt = _fake_cs

def key_of(sid, e):
    return sid

l1 = {}
l2 = {}
for f in files:
    try: d = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    for cid, e in (d.get("segments") or {}).items():
        if not isinstance(e, dict) or e.get("clip_kind") != "dialogue": continue
        canon = e.get("canonical_text") or e.get("text")
        sid = e.get("segment_id") or cid
        if not canon: continue
        for a in e.get("attempts") or []:
            t = a.get("asr_text")
            if t is None: continue
            l1[(canon, t, sid)] = (f, cid, a.get("attempt"), a.get("audio_classification"), a.get("verified"))
        aj = e.get("asr_judgement")
        if aj and (aj.get("primary") or {}).get("text") is not None:
            sec = aj.get("secondary") or {}
            l2[(canon, aj["primary"]["text"], sec.get("text"), sid)] = (f, cid, e, aj)

def cls_sig(c):
    return {"classification": c.classification, "should_pass": bool(c.should_pass)}

res1 = []
for (canon, t, sid), meta in l1.items():
    v0, _, c0 = val.evaluate_attempt(canon, t, [], max_same_signature=3, segment_id=None)
    v1, _, c1 = val.evaluate_attempt(canon, t, [], max_same_signature=3, segment_id=sid)
    res1.append({"run": meta[0], "clip": meta[1], "attempt": meta[2], "canon": canon, "asr": t,
                 "stored_cls": meta[3], "none": [bool(v0), c0.classification], "sid": [bool(v1), c1.classification],
                 "changed": (bool(v0), c0.classification) != (bool(v1), c1.classification)})

def run_full(canon, ptext, stext, sid, e, aj):
    wav = e.get("path") or ""
    actx = {"slot": int(aj.get("slot", 1)), "script_version": aj.get("script_version", "v0"), "is_last_slot": False,
            "length_ok": True, "cache": uj.SecondaryCache(), "run_state": None}
    actx.pop("run_state")
    _state["sec"] = stext; _state["cs_reached"] = 0
    r = sa.evaluate_attempt_with_cascade_detail(
        canon, ptext, [], wav, language="en-US", ledger_phrases=[], cascade_enabled=True,
        enable_connected_speech_equivalence_layer=bool(e.get("connected_speech_enabled", True)),
        segment_id=sid, attempt_ctx=actx)
    ajr = r.get("asr_judgement") or {}
    return {"verified": bool(r["verified"]), "final_status": r.get("final_status"), "cls": r["classification"].classification,
            "state": ajr.get("state"), "reason_code": ajr.get("reason_code"), "role": ajr.get("role"),
            "warnings": sorted(str(w) for w in (ajr.get("warnings") or [])), "primary_warn": (ajr.get("primary") or {}).get("warning_labels"),
            "secondary_called": (ajr.get("secondary") or {}).get("called") or (ajr.get("secondary") or {}).get("cached"),
            "layers": (ajr.get("adapter") or {}).get("layers"), "cs_reached": _state["cs_reached"],
            "pnap_eval": (ajr.get("pronunciation_alarm_eval") or {}).get("reason"),
            "hr_required": bool(r.get("human_review_required")), "tech_stop": bool(r.get("technical_stop"))}

res2 = []
for (canon, ptext, stext, sid), (f, cid, e, aj) in l2.items():
    try:
        a = run_full(canon, ptext, stext, None, e, aj)
        b = run_full(canon, ptext, stext, sid, e, aj)
    except Exception as ex:
        res2.append({"run": f, "clip": cid, "error": f"{type(ex).__name__}: {ex}"}); continue
    cmp_keys = ("verified", "final_status", "cls", "state", "reason_code", "warnings", "primary_warn", "secondary_called", "layers", "hr_required", "tech_stop")
    diffs = [k for k in cmp_keys if a[k] != b[k]]
    res2.append({"run": f, "clip": cid, "canon": canon, "primary": ptext, "secondary": stext, "stored_state": aj.get("state"),
                 "stored_reason": aj.get("reason_code"), "none": a, "sid": b, "diff_keys": diffs,
                 "baseline_reproduces_stored": a["state"] == aj.get("state")})

summ = {"files": len(files), "l1_unique": len(res1), "l1_changed": sum(r["changed"] for r in res1),
        "l2_unique": len(res2), "l2_changed": sum(1 for r in res2 if r.get("diff_keys")),
        "l2_errors": sum(1 for r in res2 if "error" in r),
        "l2_baseline_reproduces": sum(1 for r in res2 if r.get("baseline_reproduces_stored")),
        "l1_change_kinds": collections.Counter(f'{tuple(r["none"])}->{tuple(r["sid"])}' for r in res1 if r["changed"]).most_common()}
json.dump({"summary": summ, "level1_changed": [r for r in res1 if r["changed"]],
           "level2": res2}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(summ, ensure_ascii=False, indent=1, default=str))
