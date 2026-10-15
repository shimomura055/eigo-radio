# [2026-10-16 AUW 委任_07 注記: 撤去済み関数参照・履歴保存]
# 本scriptが呼ぶ er003_v1_n3_01_tts_generate._post_slowdown_cascade_rescue は 委任_06c(OF-AUW-C-13)で撤去済み。
# 現行の減速後判定は統一ASR judge(apply_a2_slowdown_postprocess -> _post_slowdown_unified_judge)。
# よって本scriptは現行コードでは実行不能(AttributeError)。当時の再評価手順と結果(同ディレクトリの *.json)を残す履歴保存のみ。
"""FAMILY-Z-MELOS-PROPER-NOUN-ASR-ROOT-CAUSE-01 委任_01 runtime evidence。
run_e2e_02の既存wav(read-only)に対し、是正A(減速後再検証への共有Cascade配線)後の判定を再評価する。
TTS再生成なし。ASR(OpenAI/Azure)のみ。単発実行(ラッパ/ループ無し)。
副作用抑止: telemetry書込とLedger research(Perplexity)は無効化(局所mock)。
"""
import json, sys, time
from unittest import mock

sys.path.insert(0, ".")
import er003_v1_n3_01_tts_generate as tg
import er006_secondary_asr_01 as sec
import er006_preprod_hardening_01_validation as val
import er006_asr_provider_routing_01 as routing

OUT = "er026_output/family_z_production_e2e_01/melos/asr_root_cause_01/reeval_post_slowdown_01.json"
R = "er026_output/family_z_production_e2e_01/melos/run_e2e_02/"
A2 = R + "a2/narration/"
B1 = R + "b1b/narration/"

CASES = [
    # (id, kind, wav, segment_id, canonical, trials)
    ("P1_a2_part1_c1", "positive", A2 + "full_story_part1_c1.wav", "full_story_part1_c1", "Melos called across the hall,", 3),
    ("P2_a2_part1_c5", "positive", A2 + "full_story_part1_c5.wav", "full_story_part1_c5", "Melos said.", 3),
    ("P3_a2_part3_c3", "positive", A2 + "full_story_part3_c3.wav", "full_story_part3_c3", "His friend turned around, and Melos fell against him.", 3),
    ("P4_b1b_part1_c5", "positive", B1 + "full_story_part1_c5.wav", "full_story_part1_c5", "Melos said.", 3),
    ("CE1_other_name_Marcus", "counter", A2 + "full_story_part1_c1.wav", "full_story_part1_c1", "Marcus called across the hall,", 2),
    ("CE2_other_name_Philon", "counter", A2 + "full_story_part3_c3.wav", "full_story_part3_c3", "His friend turned around, and Philon fell against him.", 2),
    ("CE3_other_name_Selinuntius", "counter", A2 + "full_story_part1_c5.wav", "full_story_part1_c5", "Selinuntius said.", 2),
    ("CE4_content_word_shouted", "counter", A2 + "full_story_part1_c1.wav", "full_story_part1_c1", "Melos shouted across the hall,", 2),
]

import er005_cost_logger as cl
COST_LOG = "er026_output/family_z_production_e2e_01/melos/asr_root_cause_01/reeval_cost_log.jsonl"
cl.install(COST_LOG)  # ASRコストの記録先(evidence dir、run_e2e_02のcost_logには書かない)
tele = []
def fake_tele(rec, path=None):
    tele.append(rec)

rows = []
with cl.logging_context("melos_asr_rootcause_01", "reeval"), \
     mock.patch.object(sec.semantic_equivalence, "append_telemetry_log", side_effect=fake_tele), \
     mock.patch.object(sec, "_resolve_unresolved_entity_for_review", return_value=None):
    for cid, kind, wav, seg, canon, n in CASES:
        for t in range(1, n + 1):
            asr, err = routing.transcribe(wav, language="en-US")
            cls = val.classify_asr_match(canon, asr, segment_id=seg) if asr is not None else None
            row = {"case": cid, "kind": kind, "trial": t, "wav": wav, "canonical": canon, "primary_asr": asr, "err": err,
                   "primary_classification": cls.classification if cls else None,
                   "primary_should_pass": cls.should_pass if cls else None}
            result = {}
            rescued = False
            if cls is not None and not cls.should_pass and not sec.is_homophone_candidate_mismatch(cls):
                rescued = tg._post_slowdown_cascade_rescue(result, canon, asr, cls, wav, seg)
            pc = result.get("post_slowdown_cascade")
            row["cascade_invoked"] = bool(pc and pc.get("invoked"))
            row["rescued_pass"] = bool(rescued) or bool(cls and (cls.should_pass or sec.is_homophone_candidate_mismatch(cls)))
            row["final_status"] = (pc or {}).get("final_status") or (cls.classification if cls else None)
            row["steps"] = [{"step": s.get("step"), "provider": s.get("provider"), "text": s.get("text"),
                             "classification": s.get("classification")} for s in ((pc or {}).get("steps") or [])]
            row["semantic_equivalence_info"] = (pc or {}).get("semantic_equivalence_info")
            rows.append(row)
            print(cid, t, row["primary_asr"], "|", row["primary_classification"], "|", row["final_status"], "| PASS" if row["rescued_pass"] else "| NOT_PASS", flush=True)
json.dump({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "telemetry_captured": tele}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
