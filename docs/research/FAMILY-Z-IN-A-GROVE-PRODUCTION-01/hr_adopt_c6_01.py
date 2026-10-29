# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 委任_05(使い捨て、由来=docs/pm/delegation_log/2026-10-29_FZ-DIALOGUE-LR-ADOPTION-01_USER_02.md §1)。
藪の中 Advanced(b1b) full_story_part3_c6 の ③(=attempt4、LR前本文・従来Dialogue Style)を採用する個別Human Approval(API 0)。
hr_adopt_01.py(a2/Std固定)のb1b・c6・attempt4版。既存機構の呼出のみ(asm.record_human_approval / review_lock RESOLVED / wav置換)。新Gate・flagなし。
承認の主体はユーザー: --user-statement-ref のfileに segment名とb1bが書かれていなければrc=2。既定dry-run。"""
import argparse, hashlib, json, os, shutil, sys, time, wave
sys.path.insert(0, os.getcwd())
import er003_v1_n3_01_assemble as asm
import er020_tts_retry_local_rewrite_01 as er020
RUN = "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01"; LV = RUN + "/b1b"; SEG = "full_story_part3_c6"
ATT = f"{LV}/narration/attempts/{SEG}_attempt4_englishstyleprefixwidemargin"
TAG = "fzlr05"
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def lj(p): return json.load(open(p, encoding="utf-8"))
def sj(p, d): json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
ap = argparse.ArgumentParser(); ap.add_argument("--user-statement-ref", required=True); ap.add_argument("--apply", action="store_true")
a = ap.parse_args()
stmt = open(a.user_statement_ref, encoding="utf-8").read()
if SEG.replace("full_story_", "") not in stmt and SEG not in stmt: sys.exit(f"[REFUSED] ユーザー発言fileに {SEG}(part3_c6) の記載がありません")
if "③" not in stmt: sys.exit("[REFUSED] ユーザー発言fileに③の採用記載がありません")
src, aj = ATT + ".wav", lj(ATT + ".json"); dst = f"{LV}/narration/{SEG}.wav"
assert sha(src) == aj["sha256"], "試聴時の記録とsha不一致"
assert aj["tts_mode"] == "legacy_fallback" and aj["overall_attempt_n"] == 3, "attempt4は③(従来Dialogue)でない"
res_p, lock_p, st_p = f"{LV}/audit/tts_generation_results.json", f"{LV}/audit/review_lock_state.json", f"{LV}/audit/dialogue_ctx_attempt_state.json"
res = lj(res_p); ent = res["segments"][SEG]; canon = ent["canonical_text"]
assert "An unseen hand" in canon and "Some unseen" not in canon, "原文はLR前本文(An unseen hand)であること"
with wave.open(src) as w: dur = round(w.getnframes() / w.getframerate(), 3)
print("plan:", json.dumps({"src": src, "src_sha": sha(src), "dst_now_sha": sha(dst), "dur": dur, "apply": a.apply}))
if not a.apply: sys.exit(0)
now = time.strftime("%Y-%m-%dT%H:%M:%S")
for p in (res_p, lock_p, st_p):
    b = p.replace(".json", f".pre_{TAG}_adopt_backup.json")
    if not os.path.exists(b): shutil.copyfile(p, b)
prev = dst.replace(".wav", f".pre_{TAG}_adopt.wav")
if not os.path.exists(prev): shutil.copyfile(dst, prev)       # ⑥のwavを退避保持
shutil.copyfile(src, dst); new = sha(dst)
asm.record_human_approval(LV, SEG, canon, approved_by="user(listening, part3_c6 ③=attempt4 adopted; USER_02 §1)")
lock = lj(lock_p); le = lock[SEG]
le.update({"prior_state": le.get("state"), "prior_final_status": le.get("final_status"), "state": "RESOLVED", "final_status": "HUMAN_APPROVED", "updated_at": now,
           "adopted_attempt_audio_path": src, "adopted_audio_sha256": new,
           "reason": f"個別Human Approval({now}、FZ-DIALOGUE-LR-ADOPTION-01 委任_05)。ユーザーがHRで③(LR前本文・従来Dialogue、attempt4)を採用。この1segment・1attemptのみ(一般的なASR/QA検査免除ではない)。cumulative_tts_attempts={le.get('cumulative_tts_attempts')}は保持。原文={a.user_statement_ref}"})
sj(lock_p, lock)
ent["sha256"], ent["duration_seconds"] = new, dur
ent["adopted_attempt_audio_path"], ent["adopted_audio_sha256"] = src, new
ent["asr_text"] = aj.get("asr_text"); ent["text"] = canon
ent["z_adoption"] = "human_review_adopted"
ent[er020.HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG] = True    # LR(An->Some)はこのclipでは不採用。期待テキストは常に原文(er020:905,921)
ent["FZLR05_HUMAN_APPROVAL_NOTE"] = (f"[{now}] 個別Human Approval: ③(attempt4・LR前本文・従来Dialogue)を採用。LR後本文(Some unseen hand)は最終本文に不採用。status={ent['status']}とASR/QA/LR試行記録は維持。"
                                    f"置換前(⑥)={os.path.basename(prev)}。TTS/ASR 0。原文={a.user_statement_ref}")
res["segments"][SEG] = ent; sj(res_p, res)
st = lj(st_p); c = st["clips"][SEG]
c["human_adoption"] = {"at": now, "adopted_n": 3, "adopted_attempt_file": 4, "adopted_mode": "legacy_fallback", "lr_adopted": False, "lr_depth": 0,
                       "audio_sha256": new, "authorization_ref": a.user_statement_ref, "note": "status(TERMINAL_NG)・attempts・lr履歴は不変。LR後本文は不採用"}
sj(st_p, st)
sj(f"{LV}/audit/{TAG}_user_approval_record_{SEG}.json", {"segment": SEG, "level": "b1b", "approved_at": now, "adopted_attempt_file": 4, "adopted_attempt_n": 3,
   "adopted_audio_sha256": new, "duration_seconds": dur, "replaced_audio": prev, "lock": "RESOLVED/HUMAN_APPROVED", "lr_adopted": False,
   "user_statement_source": a.user_statement_ref, "scope": "this single segment / this attempt only; no TTS/ASR API call"})
print("applied", new, dur)
