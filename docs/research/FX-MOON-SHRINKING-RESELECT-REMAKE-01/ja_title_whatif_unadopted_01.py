# 未採用候補(v2読み規則[は→わ]・②B-light β)を、今回3attempt+run_ms_03 3attemptの保存転写へ当てた what-if(API 0・費用0円・検証のみ。Production変更0)。
# FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03 調査2B。βもv2もProduction未採用(USER_03 §1・DECISION_LOG:22499-22501)。結果は判断候補の根拠であり採用ではない。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_whatif_unadopted_01.py
import json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import b_light_proto_02 as B
CANON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
RUNS = {"reselect_01": "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/narration/attempts/",
        "ms_03": "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/narration/attempts/"}
FILES = ["japanese_title_attempt1_customb8f0ff16.json", "japanese_title_attempt2_customb8f0ff16.json", "japanese_title_attempt3_minimalfallback.json"]
rows = []
for run, d in RUNS.items():
    for f in FILES:
        a = json.load(open(d + f, encoding="utf-8")); sc = a.get("scg_info") or {}
        p, s = a["asr_text"], sc.get("secondary_transcript")
        row = {"run": run, "attempt": a["attempt_number"], "primary": p, "secondary": s}
        if not s:
            row["note"] = "Secondary未記録(当時P1がAzureを呼ばず打切り)。β評価には追加Azure呼出が必要(本what-ifでは実施せず)"
            rows.append(row); print(json.dumps(row, ensure_ascii=False)); continue
        meta = {"engine": "azure", "wav_sha256": a["sha256"], "model_id": "azure-speech-stt"}
        for name, kw in (("beta_v2_reading", {}), ("beta_strict_reading", {"reading_rule": "strict"}), ("beta_veto_secondary_conflict", {"secondary_reading_conflict": "veto"})):
            r = B.composite_judge(CANON, p, s, meta, **kw)
            row[name] = {"equal": r.equal, "why": r.why[:200], "blocked_by": r.blocked_by, "warnings": list(r.warnings), "listen_required": r.listen_required}
        sb, a4a, a4b, _ = E.secondary_accept_kind(CANON, s)
        row["secondary_accept_kind"] = {"current_exact_or_normalized": sb, "A4a_value_only": a4a, "A4b_pron_match_new_spec": a4b}
        rows.append(row); print(json.dumps(row, ensure_ascii=False))
json.dump(rows, open("docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_whatif_unadopted_01.out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- 追加: v2(Primary層のみ。proto_reading_compare_02 = 助詞は→わ/へ→え発音等価 + c2_blocked + A4(a))を現行Production(F1+F2済み)に重ねたwhat-if(Secondary不使用) ----
from itertools import product
E.api0_guard_on()
v2rows = []
for run, d in RUNS.items():
    for f in FILES:
        a = json.load(open(d + f, encoding="utf-8")); p = a["asr_text"]
        base = E.primary_stage(CANON, p, False); v2 = E.primary_stage(CANON, p, True)
        r = {"run": run, "attempt": a["attempt_number"], "primary": p, "production_now": [base["state"], base["reason"]], "v2_primary_layer": [v2["state"], v2["reason"], v2.get("warnings")]}
        v2rows.append(r); print(json.dumps(r, ensure_ascii=False))
E.api0_guard_off()
json.dump(v2rows, open("docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_whatif_v2_primary_01.out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
