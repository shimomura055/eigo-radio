# -*- coding: utf-8 -*-
"""FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_10: ユーザーが試聴して『試行Nを採用』と判断した場合の個別Human Approval手続き(API 0)。**未実行・既定dry-run**。
先例(既存機構の呼出のみ。新Gate/flag/迂回なし): er019_fx_moon_title_individual_approval_01.py:39-95 / er121_e1_hr_adopt_r0_01.py:95-140
使い方: python docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/hr_adopt_01.py --segment comment_3 --attempt 2 --user-statement-ref <ユーザー原文file> [--apply]
承認の主体はユーザーのみ: --apply はユーザー発言を逐語保存したfileに segment名が書かれている場合のみ働く(AI/Fableは代行しない)。"""
import argparse, glob, hashlib, json, os, shutil, sys, time, wave
sys.path.insert(0, os.getcwd())
import er003_v1_n3_01_assemble as asm
RUN = "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01"; LV = RUN + "/a2"
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def lj(p): return json.load(open(p, encoding="utf-8"))
def sj(p, d): json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
ap = argparse.ArgumentParser(); ap.add_argument("--segment", required=True, choices=["comment_3", "full_story_part1_c3"])
ap.add_argument("--attempt", type=int, required=True, choices=[1, 2, 3]); ap.add_argument("--user-statement-ref", required=True); ap.add_argument("--apply", action="store_true")
a = ap.parse_args(); seg = a.segment
stmt = open(a.user_statement_ref, encoding="utf-8").read()
if seg not in stmt: sys.exit(f"[REFUSED] ユーザー発言fileに {seg} の記載がありません")
cand = sorted(glob.glob(f"{LV}/narration/attempts/{seg}_attempt{a.attempt}_*.wav")); assert len(cand) == 1, cand
src = cand[0]; dst = f"{LV}/narration/{seg}.wav"
res_p, lock_p = f"{LV}/audit/tts_generation_results.json", f"{LV}/audit/review_lock_state.json"
res = lj(res_p); ent = res["segments"][seg]; canon = ent["canonical_text"]
with wave.open(src) as w: dur = round(w.getnframes() / w.getframerate(), 3)
print("plan:", {"segment": seg, "attempt": a.attempt, "src": src, "src_sha": sha(src), "dst_now_sha": sha(dst), "dur": dur, "apply": a.apply})
if not a.apply: sys.exit(0)
now = time.strftime("%Y-%m-%dT%H:%M:%S")
for p in (res_p, lock_p):
    b = p.replace(".json", ".pre_fzig10_adopt_backup.json")
    if not os.path.exists(b): shutil.copyfile(p, b)
prev = dst.replace(".wav", ".pre_fzig10_adopt.wav")
if not os.path.exists(prev): shutil.copyfile(dst, prev)
shutil.copyfile(src, dst); new = sha(dst)
asm.record_human_approval(LV, seg, canon, approved_by=f"user(listening, {seg} attempt {a.attempt} adopted)")  # er003_v1_n3_01_assemble.py:96。keyはcanonical_text(元原稿)
lock = lj(lock_p); le = lock[seg]
le.update({"prior_state": le.get("state"), "prior_final_status": le.get("final_status"), "state": "RESOLVED", "final_status": "HUMAN_APPROVED", "updated_at": now,
           "adopted_attempt_audio_path": src, "adopted_audio_sha256": new,
           "reason": f"個別Human Approval({now}、FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_10)。ユーザーが試聴しattempt{a.attempt}を採用。この1segment・1attemptのみ(一般的なASR/QA検査免除ではない)。原文={a.user_statement_ref}"})
sj(lock_p, lock)
ent["sha256"], ent["duration_seconds"] = new, dur            # assemble.py:206-222のstale検査(記録sha vs 実wav)に合わせる
ent["z_adoption"] = "human_review_adopted"
ent["FZIG10_HUMAN_APPROVAL_NOTE"] = f"[{now}] 個別Human Approval: attempt{a.attempt}採用。status={ent['status']}とASR/QAのNG記録は維持。置換前={os.path.basename(prev)}。TTS/ASR 0。原文={a.user_statement_ref}"
res["segments"][seg] = ent; sj(res_p, res); print("applied", new)
