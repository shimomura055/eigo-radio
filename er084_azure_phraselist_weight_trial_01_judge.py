# -*- coding: utf-8 -*-
"""Production判定(evaluate_attempt_with_cascade_detail)をoffline注入で呼ぶ薄いadapter(判定ロジックは無変更)。

v02(委任_02b、Opus_J M-1/M-2是正):
- M-1: 本番相当のsegment_idと`enable_connected_speech_equivalence_layer=connected_speech_enabled_for(segment_id)`を渡す。
  既定segment_id=ROLE_FULL_STORY_SEGMENT(FULL_STORY role、Tier3有効。Family Z narrator clip名型)。
  ROLE_NO_TIER3(=None)は「Tier3なしrole」(KP型、segment_id=None相当)。
  force_secondaryは本番既定と同じFalse(fallback minimal instruction経路のみTrue。引数で再現可)。
- M-2: judge内でsemantic_equivalence.append_telemetry_logをno-op化(telemetry非追記)。is_last_slot=False固定
  (HR packageの発音lookup[ledger書込の可能性]を呼ばない)。「最終slotならHR」はeval側で`ng_would_hr`として換算。
Primary転写(asr_text)は引数で注入。Secondary(Azure)は`er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list`
を**このprocess内だけ**で記録済み転写を返す関数に差し替える(Production fileは書換えない。API 0)。
"""
import er006_secondary_asr_01 as sec
import er020_tts_retry_local_rewrite_01 as role_gate

ROLE_FULL_STORY_SEGMENT = "full_story_part1_c1"  # FULL_STORY role(Tier3有効、CS層有効)。Family Z narrator clip名型
ROLE_NO_TIER3 = None  # Tier3なしrole(segment_id=None相当、KP型)


def judge_offline(canonical_text: str, primary_text: str, secondary_text, wav_path: str,
                  ledger_phrases=("Melos",), segment_id=ROLE_FULL_STORY_SEGMENT, force_secondary: bool = False) -> dict:
    calls = {"n": 0, "telemetry_noop": 0}

    def fake_azure(path, language="en-US", phrases=None, timeout_seconds=90.0):
        calls["n"] += 1
        if secondary_text is None:
            return None, "plw_trial: secondary text unavailable"
        return secondary_text, None

    def noop_telemetry(record, path=None):
        calls["telemetry_noop"] += 1

    cs_flag = bool(role_gate.connected_speech_enabled_for(segment_id))
    orig = sec.get_full_text_via_azure_stt_with_phrase_list
    orig_tel = sec.semantic_equivalence.append_telemetry_log
    sec.get_full_text_via_azure_stt_with_phrase_list = fake_azure
    sec.semantic_equivalence.append_telemetry_log = noop_telemetry
    try:
        sec.reset_secondary_cache()
        detail = sec.evaluate_attempt_with_cascade_detail(
            canonical_text, primary_text, [], wav_path, language="en-US",
            ledger_phrases=list(ledger_phrases), cascade_enabled=True, force_secondary=bool(force_secondary),
            enable_connected_speech_equivalence_layer=cs_flag, segment_id=segment_id,
            attempt_ctx={"is_last_slot": False})
    finally:
        sec.get_full_text_via_azure_stt_with_phrase_list = orig
        sec.semantic_equivalence.append_telemetry_log = orig_tel
    j = detail.get("asr_judgement")
    cls = detail.get("classification")
    state = j.get("state") if isinstance(j, dict) else str(j)[:60]
    verified = detail.get("verified")
    return {
        "verified": verified,
        "human_review_required": detail.get("human_review_required"),  # is_last_slot=False固定のため常にFalse
        "ng_would_hr": (not verified) and not str(state).startswith("PASS") and "UNAVAILABLE" not in str(state),
        "stop_retrying": detail.get("stop_retrying"),
        "classification": getattr(cls, "audio_classification", None) or getattr(cls, "classification", None) or str(cls)[:120],
        "final_status": detail.get("final_status"),
        "state": state,
        "reason_code": j.get("reason_code") if isinstance(j, dict) else None,
        "step_names": [s.get("step") for s in detail.get("steps", [])],
        "layers": ((j.get("adapter") or {}).get("layers") if isinstance(j, dict) else None),
        "segment_id": segment_id, "cs_flag": cs_flag, "force_secondary": bool(force_secondary),
        "fake_azure_calls": calls["n"], "telemetry_noop_calls": calls["telemetry_noop"],
    }


def reinject_phase_a(raw_path: str, design_path: str, out_path: str, old_result_json: str = None) -> dict:
    """Phase A raw(15行)を、v02 judge(FULL_STORY role=本番segment名 / Tier3なしrole)でAPI 0再注入する。"""
    import json
    import os
    import er084_azure_phraselist_weight_trial_01_lib as L
    design = json.load(open(design_path, encoding="utf-8"))
    a = design["phases"]["A"]["audio"][0]
    prim = json.load(open(os.path.join(L.ROOT, a["path"][:-4] + ".json"), encoding="utf-8"))
    rows = L.read_raw(raw_path)
    old = {}
    if old_result_json and os.path.exists(old_result_json):
        for j in json.load(open(old_result_json, encoding="utf-8")).get("judges", []):
            old[(j["cond"], j["rep"])] = j["state"]
    wav = os.path.join(L.ROOT, a["path"])
    out = []
    for r in rows:
        if r.get("phase") != "A":
            continue
        rec = {"cond": r["cond"], "rep": r["rep"], "azure_text_name_window": (r["text"] or "")[170:215],
               "old_v01_state": old.get((r["cond"], r["rep"]))}
        for label, seg in (("full_story", prim["segment_id"]), ("no_tier3", ROLE_NO_TIER3)):
            j = judge_offline(a["canonical_text"], prim["asr_text"], r["text"], wav, segment_id=seg)
            rec[label] = {k: j[k] for k in ("state", "reason_code", "classification", "final_status", "step_names", "layers", "ng_would_hr")}
        out.append(rec)
    res = {"note": "v02 judge(M-1/M-2是正)でPhase A raw 15行をAPI 0再注入。旧v01結果は PHASE_A_RESULT_01.md/.json に残置。",
           "primary_text_source": "run_e2e_04 attempt2 json asr_text", "segment_id_full_story": prim["segment_id"], "rows": out}
    json.dump(res, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--reinject", required=True, help="Phase A raw/azure_calls.jsonl")
    ap.add_argument("--design", required=True)
    ap.add_argument("--old-result", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = reinject_phase_a(a.reinject, a.design, a.out, a.old_result)
    for r in res["rows"]:
        print(r["cond"], r["rep"], "old=", r["old_v01_state"], "full_story=", r["full_story"]["state"], r["full_story"]["final_status"],
              "no_tier3=", r["no_tier3"]["state"])
