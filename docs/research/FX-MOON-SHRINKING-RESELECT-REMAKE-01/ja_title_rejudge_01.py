# 月Std日本語題の保存転写を現行Production判定器(adapter)へ再注入する(API 0・費用0円・TTS/ASR呼出0)。
# FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03 調査2B。Azureは「保存済みsecondary_transcript」を返すstub(未記録ならNone=不呼出判定のため呼出回数を記録)。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_rejudge_01.py
import json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import er007_ja_secondary_asr_01 as sec
import er011_ja_asr_variant_layer_01 as VL
import er078_asr_unified_judge_01 as uj

CANON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
RUNS = {
  "reselect_01": "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/narration/attempts/",
  "ms_03": "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/narration/attempts/",
}
FILES = ["japanese_title_attempt1_customb8f0ff16.json", "japanese_title_attempt2_customb8f0ff16.json", "japanese_title_attempt3_minimalfallback.json"]
E.api0_guard_on()
consts = {"READING_MATCH_FINAL_GATE": getattr(uj, "READING_MATCH_FINAL_GATE", None),
          "CANDIDATE_E_FULL_DIFF_CHECK": getattr(VL, "CANDIDATE_E_FULL_DIFF_CHECK", None),
          "CANDIDATE_E_VALUE_GUARD_CHECK": getattr(VL, "CANDIDATE_E_VALUE_GUARD_CHECK", None),
          "CANDIDATE_E_CASCADE_DIFF_RETURN": getattr(VL, "CANDIDATE_E_CASCADE_DIFF_RETURN", None)}
out = {"constants": consts, "rows": []}
for run, d in RUNS.items():
    for f in FILES:
        a = json.load(open(d + f, encoding="utf-8"))
        prim = a["asr_text"]; sc = a.get("scg_info") or {}
        sec_t = sc.get("secondary_transcript")
        calls = {"n": 0}
        def stub(p, language="ja-JP", timeout_seconds=90, _t=sec_t, _c=calls):
            _c["n"] += 1
            return (_t, None) if _t is not None else (None, "api0_stub_no_recorded_secondary")
        orig = sec._azure_stt_strict; sec._azure_stt_strict = stub
        try:
            r = sec.evaluate_attempt_ja_with_cascade_detail(CANON, prim, E.dummy_wav(), cascade_enabled=True, attempt_ctx={"max_len": 400})
        finally:
            sec._azure_stt_strict = orig
        j = r["asr_judgement"]
        row = {"run": run, "file": f, "primary": prim, "secondary_recorded": sec_t,
               "recorded_state": sc.get("unified_judge_state"), "recorded_reason": sc.get("unified_reason_code"),
               "now_state": j.get("state"), "now_reason": j.get("reason_code"), "now_p3_entry": j.get("p3_entry"),
               "primary_label": (j.get("primary") or {}).get("label"), "secondary_label": (j.get("secondary") or {}).get("label"),
               "azure_called_by_judge": calls["n"], "vg_primary": ((j.get("value_guard") or {}).get("primary") or {}).get("kind"),
               "vg_secondary": ((j.get("value_guard") or {}).get("secondary") or {}).get("kind"),
               "candidate_e_full_diff": j.get("candidate_e_full_diff"), "candidate_e_cascade_return": j.get("candidate_e_cascade_return"),
               "final_gate": j.get("final_gate"), "warnings": j.get("warnings")}
        out["rows"].append(row)
        print(json.dumps(row, ensure_ascii=False))
E.api0_guard_off()
json.dump(out, open("docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_rejudge_01.out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
