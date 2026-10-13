# 委任_02 3: attempt4(現行 full_story_part1_c5.wav)へ既存正式処理 apply_a2_slowdown_postprocess を1回適用(新規ロジックなし)。
import sys, os, json, shutil, hashlib
sys.path.insert(0, ".")
import er062_family_z_structure_01 as st
RUN = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
ND = f"{RUN}/a2/narration"; NAME = "full_story_part1_c5"; D = "er026_output/family_z_production_e2e_01/melos/evidence_14"
st.set_stop_run_dir(RUN)
st.check_stop_sentinel("evidence_14:apply_slowdown", RUN)
from dotenv import load_dotenv; load_dotenv()
import er005_cost_logger as cl
cl.install(f"{RUN}/cost_log.jsonl")
st.install_api_stop_guard()
import er026_family_z_fiction_production_runner_01 as r
before = r.make_real_spent_fn(f"{RUN}/cost_log.jsonl")()
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
shutil.copyfile(f"{ND}/{NAME}.wav", f"{D}/pre_slowdown_backup/{NAME}_attempt4.wav")
shutil.copyfile(f"{ND}/{NAME}_original.wav", f"{D}/pre_slowdown_backup/{NAME}_original_stale_attempt3.wav")
pre_sha = sha(f"{ND}/{NAME}.wav")
import er003_v1_n3_01_tts_generate as n3
import soundfile as sf
text = n3.tts_safe_news_en("Melos said.")
res = {"status": "OK", "sha256": pre_sha, "duration_seconds": round(sf.info(f"{ND}/{NAME}.wav").duration, 3)}
with cl.logging_context(r.E2E_THEME_TAG, "evidence_14_slowdown_c5"), cl.segment_context(NAME):
    res = n3.apply_a2_slowdown_postprocess(NAME, ND, text, res)
    import er011_human_review_lock_01 as rl
    rl.append_attempt_history_event(f"{ND}/{NAME}.wav", "A2_SLOWDOWN_REVERIFY", {
        "attempt": 1, "status": res.get("status"), "post_slowdown_classification": res.get("post_slowdown_classification"),
        "post_slowdown_asr_text": res.get("post_slowdown_asr_text"), "post_slowdown_cascade": res.get("post_slowdown_cascade"),
        "tts_generations_used_cumulative": 0, "note": "委任_02 evidence_14: HR承認済みattempt4へ既存正式6%減速+減速後QAを1回適用(TTS再生成なし)"})
after = r.make_real_spent_fn(f"{RUN}/cost_log.jsonl")()
res["_pre_slowdown_sha256"] = pre_sha; res["_post_slowdown_sha256"] = sha(f"{ND}/{NAME}.wav")
res["_spent_before"] = before; res["_spent_after"] = after
json.dump(res, open(f"{D}/slowdown_result_c5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
print(json.dumps({k: res.get(k) for k in ("status", "reason", "slowdown_applied", "post_slowdown_asr_text", "post_slowdown_classification", "post_slowdown_final_classification", "_pre_slowdown_sha256", "_post_slowdown_sha256", "_spent_before", "_spent_after")}, ensure_ascii=False, indent=1))
print(json.dumps(res.get("post_slowdown_cascade"), ensure_ascii=False, default=str)[:1500])
print(json.dumps(res.get("slowdown_info"), ensure_ascii=False))
