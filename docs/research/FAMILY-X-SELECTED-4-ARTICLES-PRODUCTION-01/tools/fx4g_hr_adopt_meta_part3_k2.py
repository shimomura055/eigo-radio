# -*- coding: utf-8 -*-
"""FAMILY-X-SELECTED-4 委任_07: ⑨Meta Std(a2) full_story_part3_k2 のHuman Review承認(ユーザー原文=docs/pm/delegation_log/2026-10-30_..._USER_HR_02.md:3-5)を
既存HR承認経路(er121_e1_hr_adopt_r0_01.apply と同型: wav配置+asm.record_human_approval+review_lock RESOLVED/HUMAN_APPROVED+results注記)で反映する。API 0。
採用音声=HR pageの判断対象 full_story_part3_k2_attempt2_postslowdown.wav(sha 529a7aa0...)と一致をassert。status手書きなし。--apply無しはdry-run。"""
import hashlib, json, os, shutil, sys, time
import er003_v1_n3_01_assemble as asm
import er008_a2_postprocess_slowdown_01 as slow
RUN = "er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01"
LV, SEG = "a2", "full_story_part3_k2"
EXPECT = "529a7aa01bbb2ee4ee9c56f435bf477056e29dee2c1ebd6c0b43a84e4241229c"
STMT = "docs/pm/delegation_log/2026-10-30_FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01_USER_HR_02.md"
TAG = "fx4g"
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
def lj(p):
    return json.load(open(p, encoding="utf-8"))
def sj(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
lv = f"{RUN}/{LV}"; narr = f"{lv}/narration"; att = f"{narr}/attempts"
adopt_wav = f"{att}/{SEG}_attempt2_postslowdown.wav"
src_wav = f"{att}/{SEG}_attempt1_customa3c4625e.wav"      # 減速前(試行1のTTS原音)。減速後=adopt_wav(決定的: 同入力->同sha)
assert sha(adopt_wav) == EXPECT, "HR page掲載の判断対象音声とsha不一致"
assert lj(f"{att}/{SEG}_attempt2_postslowdown.json")["sha256"] == EXPECT
assert os.path.isfile(STMT) and "APPROVED_FOR_PRODUCTION" in open(STMT, encoding="utf-8").read()
res_path, lock_path = f"{lv}/audit/tts_generation_results.json", f"{lv}/audit/review_lock_state.json"
res = lj(res_path); ent = res["segments"][SEG]; lock = lj(lock_path)
assert ent["status"] == "STOPPED" and lock[SEG]["state"] == "HUMAN_REVIEW_REQUIRED", (ent["status"], lock[SEG]["state"])
print("plan: adopt", adopt_wav, "->", f"{narr}/{SEG}.wav", "orig:", src_wav, "cur_dst_sha", sha(f"{narr}/{SEG}.wav")[:12])
if "--apply" not in sys.argv:
    print("dry-run ok"); sys.exit(0)
for p in (res_path, lock_path):
    b = p.replace(".json", f".pre_{TAG}_adopt_backup.json")
    if not os.path.exists(b): shutil.copyfile(p, b)
dst = f"{narr}/{SEG}.wav"; orig = dst.replace(".wav", "_original.wav")
prev = dst.replace(".wav", f".pre_{TAG}_adopt.wav")
if not os.path.exists(prev): shutil.copyfile(dst, prev)
if os.path.exists(orig) and not os.path.exists(orig.replace(".wav", f".pre_{TAG}_adopt.wav")):
    shutil.copyfile(orig, orig.replace(".wav", f".pre_{TAG}_adopt.wav"))
shutil.copyfile(src_wav, orig)
info = slow.apply_a2_slowdown(orig, dst)
assert sha(dst) == EXPECT, "減速後wavが採用音声とsha不一致"
now = time.strftime("%Y-%m-%dT%H:%M:%S")
a2j = lj(f"{att}/{SEG}_attempt2_postslowdown.json")
asm.record_human_approval(lv, SEG, ent["canonical_text"], approved_by="user")
le = lock[SEG]
le["prior_state"], le["prior_final_status"] = le.get("state"), le.get("final_status")
le["state"], le["final_status"], le["updated_at"] = "RESOLVED", "HUMAN_APPROVED", now
le["adopted_attempt_audio_path"], le["adopted_audio_sha256"] = adopt_wav, EXPECT
le["reason"] = f"個別Human Approval({now}、FAMILY-X-SELECTED-4 委任_07)。ユーザーがHR pageの1音声(減速後attempt2)を試聴し's発音を確認、採用を承認。原文={STMT}。この1segment・1takeへの個別承認のみ(一般的なASR/QA検査免除ではない)。"
lock[SEG] = le; sj(lock_path, lock)
ent["FX4G_HUMAN_APPROVAL_NOTE"] = f"[{now}] 個別Human Approval: ユーザー試聴・減速後attempt2を採用(原文={STMT})。ASR NG記録(attempts_log等)は維持、status=STOPPEDは正直な記録として維持。TTS/ASR生成0。一般仕様ではない。"
ent["adopted_attempt_audio_path"], ent["adopted_audio_sha256"], ent["sha256"] = adopt_wav, EXPECT, EXPECT
ent["asr_text"] = a2j.get("post_slowdown_asr_text")
ent["slowdown_applied"], ent["slowdown_info"], ent["original_path"] = True, info, orig
ent["duration_seconds"] = info["dst_duration_seconds"]
res["segments"][SEG] = ent; sj(res_path, res)
sj(f"{lv}/audit/{TAG}_user_approval_record_{SEG}.json", {"segment": SEG, "level": LV, "approved_by": "user", "approved_at": now,
   "user_statement_source": STMT, "adopted_audio_sha256": EXPECT, "slowdown_info": info, "replaced_audio": prev,
   "scope": "this single segment / this take only; NOT a general ASR/QA exemption; no API call"})
print("APPLIED", EXPECT[:12], info["src_duration_seconds"], info["dst_duration_seconds"])
