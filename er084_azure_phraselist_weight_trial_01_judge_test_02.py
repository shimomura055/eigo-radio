# -*- coding: utf-8 -*-
"""委任_02b judge是正(Opus_J M-1/M-2)のtest。API 0。
M-1: golden replay = 本番記録(run_e2e_04 part3_c1 attempt2 / run_e2e_05 part3_c1減速後)をoffline注入して、
     記録どおりのstep/状態が再現されること。実走前Gate(PASSしなければPhase B Azure実走禁止)。
M-2: judge呼出しが本番の副作用ファイル(telemetry/ledger/attempt_history/HR queue/HR log)を変えないこと(size+mtime不変)。
"""
import json
import os

import pytest

import er006_secondary_asr_01 as sec
import er084_azure_phraselist_weight_trial_01_judge as J
import er084_azure_phraselist_weight_trial_01_lib as L

MELOS = os.path.join(L.ROOT, "er026_output", "family_z_production_e2e_01", "melos")
ATT4 = os.path.join(MELOS, "run_e2e_04", "a2", "narration", "attempts", "full_story_part3_c1_attempt2_customa3c4625e.json")
RES5 = os.path.join(MELOS, "run_e2e_05", "a2", "audit", "tts_generation_results.json")
DESIGN = os.path.join(L.ROOT, "docs", "research", "FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01", "design_matrix_01.json")

SIDE_EFFECT_FILES = [
    "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
    "er006_output/pronunciation_ledger_01/ledger.json",
    "er011_output/attempt_history.jsonl",
    "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
]


def _snap(paths):
    out = {}
    for p in paths:
        ap = p if os.path.isabs(p) else os.path.join(L.ROOT, p)
        out[p] = (os.path.getsize(ap), os.stat(ap).st_mtime_ns) if os.path.exists(ap) else None
    return out


def _golden1():
    att = json.load(open(ATT4, encoding="utf-8"))
    design = json.load(open(DESIGN, encoding="utf-8"))
    canon = design["phases"]["A"]["audio"][0]["canonical_text"]
    t3 = [s for s in att["cascade_steps"] if s["step"] == "tier3_corroboration_secondary"][0]
    return att, canon, t3["text"]


def test_golden1_run_e2e_04_part3_c1_attempt2_tier3_step_and_NG_BOTH():
    att, canon, az_text = _golden1()
    assert att["segment_id"] == "full_story_part3_c1" and "Mello drank" in att["asr_text"] and "Mellows drank" in az_text
    r = J.judge_offline(canon, att["asr_text"], az_text, "x.wav", segment_id=att["segment_id"])
    rec_steps = [s["step"] for s in att["cascade_steps"]]
    assert rec_steps == ["primary_1", "tier3_corroboration_secondary", "secondary_1"]
    assert r["step_names"] == rec_steps  # 記録どおりtier3 stepが出る(M-1の核)
    assert r["layers"] == ["tier3"] and r["cs_flag"] is True
    assert r["state"] == "NG_BOTH" and r["verified"] is False
    assert r["classification"] == att["cascade_steps"][0]["classification"] == "ASR_VALIDATION_UNCERTAIN"
    assert r["telemetry_noop_calls"] >= 1  # telemetry追記点を通り、no-opで中和された(M-2)


def test_golden1_old_judge_path_without_role_does_not_reproduce_tier3():
    """旧judge(segment_id='plw_trial'=role None)ではtier3 stepが出ない=M-1の欠陥の実証(旧挙動を再現して検出力を示す)。"""
    att, canon, az_text = _golden1()
    r = J.judge_offline(canon, att["asr_text"], az_text, "x.wav", segment_id="plw_trial")
    assert "tier3_corroboration_secondary" not in r["step_names"] and r["cs_flag"] is False
    r2 = J.judge_offline(canon, att["asr_text"], az_text, "x.wav", segment_id=J.ROLE_NO_TIER3)
    assert "tier3_corroboration_secondary" not in r2["step_names"] and r2["state"] == "NG_BOTH"


def test_golden2_run_e2e_05_std_part3_c1_after_slowdown_corroborated_match():
    res = json.load(open(RES5, encoding="utf-8"))
    seg = res["full_story_part3_c1"] if "full_story_part3_c1" in res else None
    if seg is None:  # トップ階層が違う場合は探索
        def find(o):
            if isinstance(o, dict):
                if "full_story_part3_c1" in o and isinstance(o["full_story_part3_c1"], dict) and "asr_judgement" in o["full_story_part3_c1"]:
                    return o["full_story_part3_c1"]
                for v in o.values():
                    r = find(v)
                    if r:
                        return r
            return None
        seg = find(res)
    assert seg and "Mellos drank" in seg["asr_text"]
    canon = seg["canonical_text"]
    # 記録されたAzure転写は無い(Tier3のsecondaryはcache内)ため、Azureはcanonical(Melos drank)と仮定=Opus_J/Fable指定のgolden条件
    r = J.judge_offline(canon, seg["asr_text"], canon, "x.wav", segment_id=seg["segment_id"])
    assert r["state"] == seg["asr_judgement"]["state"] == "PASS_WITH_WARNING"
    assert r["classification"] == "SECONDARY_ASR_CORROBORATED_MATCH" or r["final_status"] == "SECONDARY_ASR_CORROBORATED_MATCH"
    assert seg["asr_judgement"]["primary"]["label"] == "SECONDARY_ASR_CORROBORATED_MATCH"
    assert r["layers"] == seg["asr_judgement"]["adapter"]["layers"] == ["tier3"]
    assert "tier3_corroboration_secondary" in r["step_names"]


def test_no_tier3_role_requires_exact_secondary():
    _, canon, _ = _golden1()
    prim = canon.replace("Melos", "Mello")
    ok = J.judge_offline(canon, prim, canon, "x.wav", segment_id=J.ROLE_NO_TIER3)
    ng = J.judge_offline(canon, prim, canon.replace("Melos", "Mellows"), "x.wav", segment_id=J.ROLE_NO_TIER3)
    assert ok["state"] == "PASS_WITH_WARNING" and ng["state"] == "NG_BOTH" and ok["cs_flag"] is False


def test_judge_has_no_production_side_effects_size_and_mtime():
    paths = list(SIDE_EFFECT_FILES)
    hr = getattr(sec, "HUMAN_REVIEW_LOG_PATH", None)
    if hr:
        paths.append(hr)
    before = _snap(paths)
    orig_az = sec.get_full_text_via_azure_stt_with_phrase_list
    orig_tel = sec.semantic_equivalence.append_telemetry_log
    att, canon, az_text = _golden1()
    for seg in (att["segment_id"], J.ROLE_FULL_STORY_SEGMENT, J.ROLE_NO_TIER3):
        J.judge_offline(canon, att["asr_text"], az_text, "x.wav", segment_id=seg)
        J.judge_offline(canon, att["asr_text"], canon, "x.wav", segment_id=seg)
        J.judge_offline(canon, att["asr_text"], None, "x.wav", segment_id=seg)  # Secondary取得不能経路
    assert _snap(paths) == before
    assert sec.get_full_text_via_azure_stt_with_phrase_list is orig_az  # 差替えは復元される
    assert sec.semantic_equivalence.append_telemetry_log is orig_tel
    # is_last_slot固定False: HR要=Falseで、ng_would_hrはeval側換算用の別キー
    r = J.judge_offline(canon, att["asr_text"], att["asr_text"], "x.wav", segment_id=att["segment_id"])
    assert r["human_review_required"] in (False, None)


def test_connected_speech_flag_follows_production_function():
    import er020_tts_retry_local_rewrite_01 as g
    for seg in ("full_story_part3_c1", "full_story_part1_c1", None, "kp1_en"):
        r = J.judge_offline("Melos drank.", "Melos drank.", "Melos drank.", "x.wav", segment_id=seg)
        assert r["cs_flag"] == g.connected_speech_enabled_for(seg)


def test_criteria_json_v02_matches_design_document_section_3_v02():
    d = os.path.join(L.ROOT, "docs", "research", "FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01")
    md = open(os.path.join(d, "TRIAL_DESIGN_01.md"), encoding="utf-8").read()
    c = json.load(open(os.path.join(d, "criteria_thresholds_01.json"), encoding="utf-8"))
    sec = md.split("## 3-v02")[1].split("\n## 4.")[0]
    v = c["v02"]
    assert c["version"] == "02"
    assert "R<6 なら`INCONCLUSIVE`" in sec and "up ≥ 3 かつ up ≥ 0.30×R" in sec
    assert f"主1.5: {v['alpha_primary']}" in sec and f"副2.0: {v['alpha_secondary']}" in sec
    assert "3種以上" in sec and v["min_clusters"] == 3
    assert "33wav" in sec and v["valid_negative_expected_n"] == 33
    assert c["min_R_for_identifiability"] == 6 and c["fixed_min_abs"] == 3 and c["fixed_min_fraction_of_R"] == 0.30
    assert c["negative_false_melos_increase_max"] == 0 and c["degraded_max_abs"] == 1
    assert v["primary_weight_cond"] == "pl_w1.5" and v["secondary_weight_cond"] == "pl_w2.0"
    assert "Tier3なしroleでdown ≤ up" in sec and v["secondary_role_down_le_up"] is True
    assert "v02" in md.split("## 9.")[1]


def test_design_matrix_v02_negatives_and_production_rule_match_design():
    d = os.path.join(L.ROOT, "docs", "research", "FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01")
    dm = json.load(open(os.path.join(d, "design_matrix_01.json"), encoding="utf-8"))
    v = dm["phases"]["B"]["v02"]
    assert v["conditions_B"] == ["no_pl", "pl_unspecified", "pl_w1.5", "pl_w2.0"]
    assert v["negatives_v02"]["expected"] == {"n_tts": 18, "n_slow": 9, "n_wav": 27}
    assert len(v["negatives_v02"]["contexts"]) * len(v["negatives_v02"]["variants"]) * 2 == 18
    assert v["production_takes"]["max_takes"] == 20 and v["spot_check"]["n_wav"] == 9
