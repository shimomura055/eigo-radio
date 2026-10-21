"""PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01 S5: API 0。
保存済みrun(X: run_mey_02 / run_fxpw_01 / run_pp_01 / run_byus_01、Z: run_e2e_06)の全EN segmentについて
 (1) Phrase List供給(get_hint_for_text(min_confidence='low')のcanonical_spelling)をLedger是正前(backup)/後(現行)で再計算
 (2) 保存済みPrimary転写+保存済みAzure転写を注入し evaluate_attempt_with_cascade_detail(M1有効)で再判定(_reset_m1_freeze_cache)
Azure/外部APIは一切呼ばない(Azure関数は保存済み転写を返すmockに差替え)。
使い方: .venv/Scripts/python.exe docs/research/.../supply_and_golden_replay.py <before_ledger_path> <out_json>"""
import glob, json, os, re, sys
sys.path.insert(0, ".")
import er006_pronunciation_ledger_01 as L
import er006_secondary_asr_01 as sec

BEFORE = sys.argv[1]
OUT = sys.argv[2]
AFTER = L.LEDGER_PATH
RUNS = {
    "X_mey_02": "er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02",
    "X_fxpw_01": "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01",
    "X_pp_01": "er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01",
    "X_byus_01": "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01",
    "Z_e2e_06": "er026_output/family_z_production_e2e_01/melos/run_e2e_06",
}
sec.semantic_equivalence.append_telemetry_log = lambda *a, **k: None
STEP_SEC = ("secondary_1", "tier3_corroboration_secondary", "non_latin_secondary", "connected_speech_equivalence_secondary")


def seg_texts(run_dir):
    out = {}
    for lvl in ("a2", "b1b"):
        p = f"{run_dir}/{lvl}/audit/tts_generation_results.json"
        if not os.path.exists(p):
            p2 = f"{run_dir}/{lvl}/audit/tts_generation_results.json"
            continue
        o = json.load(open(p, encoding="utf-8"))
        for sid, v in (o.get("segments") or {}).items():
            if isinstance(v, dict) and v.get("text"):
                out[(lvl, sid)] = v["text"]
    return out


def phrases_for(text, path):
    L.LEDGER_PATH = path
    return [h["canonical_spelling"] for h in L.get_hint_for_text(text, min_confidence="low")]


def judge(text, att, seg, path):
    L.LEDGER_PATH = path
    sec._reset_m1_freeze_cache()
    steps = att.get("cascade_steps") or []
    az = None
    for st in steps:
        if st.get("step") in STEP_SEC:
            az = st.get("text"); break
    sec.get_full_text_via_azure_stt_with_phrase_list = (
        lambda t: (lambda *a, **k: (t, None) if t else (None, "no_stored_secondary")))(az)
    phr = [h["canonical_spelling"] for h in L.get_hint_for_text(text, min_confidence="low")]
    r = sec.evaluate_attempt_with_cascade_detail(
        text, att.get("asr_text"), [], "no_such.wav", ledger_phrases=phr or None, cascade_enabled=True, segment_id=seg)
    aj = r["asr_judgement"]
    return {"verified": bool(r["verified"]), "final_status": r["final_status"], "state": aj.get("state"),
            "reason": aj.get("reason_code"), "azure_real_calls": aj["adapter"]["azure_real_calls"],
            "m1": bool(r.get("m1_multi_candidate"))}


rows, supply = [], []
for rk, rd in RUNS.items():
    texts = seg_texts(rd)
    for (lvl, sid), t in sorted(texts.items()):
        if not re.search(r"[A-Za-z]{3}", t) or re.search(r"[぀-ヿ一-鿿]", t):
            continue
        pb, pa = phrases_for(t, BEFORE), phrases_for(t, AFTER)
        supply.append({"run": rk, "level": lvl, "seg": sid, "before": pb, "after": pa})
    for ap in sorted(glob.glob(f"{rd}/*/narration/attempts/*.json")):
        att = json.load(open(ap, encoding="utf-8"))
        lvl = ap.replace("\\", "/").split("/")[-4]
        base = att.get("segment_id")
        t = texts.get((lvl, base))
        if not t or att.get("asr_text") is None or att.get("language", "en") != "en":
            continue
        try:
            b = judge(t, att, base, BEFORE)
            a = judge(t, att, base, AFTER)
        except Exception as ex:  # 記録して継続
            rows.append({"run": rk, "level": lvl, "seg": base, "file": os.path.basename(ap), "error": repr(ex)[:200]})
            continue
        rows.append({"run": rk, "level": lvl, "seg": base, "file": os.path.basename(ap),
                     "stored_verified": att.get("verified"), "stored_class": att.get("audio_classification"),
                     "before": b, "after": a, "changed": (b["verified"], b["final_status"], b["state"]) != (a["verified"], a["final_status"], a["state"])})
L.LEDGER_PATH = AFTER
json.dump({"supply": supply, "judge": rows}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print("supply segs", len(supply), "judge rows", len(rows), "errors", sum(1 for r in rows if "error" in r))
bad = Counter(p for s in supply for p in s["before"] if p.lower() in ("unknown", "cascade", "asr cascade", "one voice unknown"))
bad_a = Counter(p for s in supply for p in s["after"] if p.lower() in ("unknown", "cascade", "asr cascade", "one voice unknown"))
print("bad phrases before", dict(bad), "after", dict(bad_a))
print("changed judgments", [r for r in rows if r.get("changed")])
