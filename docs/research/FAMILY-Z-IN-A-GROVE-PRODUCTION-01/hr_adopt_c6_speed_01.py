# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 委任_05(使い捨て): hr_adopt_c6_01.py の続き。③採用wav(raw、ユーザーが聴いた音)へ、Production必須の速度仕様v2
(Adv会話=約6%高速化 atempo=1.06、er063.verify_z_speed_profile)を正式経路と同じ関数(apply_a2_slowdown_postprocess、slowdown_pct=Z_ADV_DIALOGUE_SLOWDOWN_PCT)
で適用し、高速化後の音声をASR再検証(1回、Primary OK想定)する。成功時のみ narration へ配置(失敗時は何も書かない)。先例=er121_e1_slowed_asr_recheck_01.py。"""
import hashlib, json, os, shutil, sys, time
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv()
RUN = "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01"; LV = RUN + "/b1b"; SEG = "full_story_part3_c6"; NAR = LV + "/narration"
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def lj(p): return json.load(open(p, encoding="utf-8"))
def sj(p, d): json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
import er003_v1_n3_01_tts_generate as n3
import er005_cost_logger as cl
import er063_family_z_audio_01 as z63
import er109_xz_scope_01 as scope
import er078_secondary_run_scope_01 as srs
att = lj(f"{NAR}/attempts/{SEG}_attempt4_englishstyleprefixwidemargin.json")
raw = f"{NAR}/attempts/{SEG}_attempt4_englishstyleprefixwidemargin.wav"
assert sha(raw) == att["sha256"] == sha(f"{NAR}/{SEG}.wav"), "narration/c6.wav は③(raw)であること(hr_adopt_c6_01.py適用済み)"
res_p, lock_p = f"{LV}/audit/tts_generation_results.json", f"{LV}/audit/review_lock_state.json"
res = lj(res_p); ent = res["segments"][SEG]; canon = ent["canonical_text"]
work = f"{LV}/audit/fzlr05_speed_work"; os.makedirs(work, exist_ok=True)
shutil.copyfile(raw, f"{work}/{SEG}.wav")
cl.init_logger(f"{RUN}/cost_log.jsonl")
tts_input = z63._pnap_supply(canon, n3.tts_safe_news_en(canon))   # = er063._norm_for_tts(dialogue)
result = {"status": "OK", "sha256": sha(raw), "duration_seconds": ent.get("duration_seconds")}
@srs.with_secondary_run
@scope.family_scope("Z")
def go():
    with cl.logging_context("run_sf_prod_01", "c6_hr_adopt_speed_recheck"):
        return n3.apply_a2_slowdown_postprocess(SEG, work, tts_input, result, is_last_slot=True, log_human_review=False,
                                                slowdown_pct=z63.Z_ADV_DIALOGUE_SLOWDOWN_PCT)
r = go()
rec = {k: r.get(k) for k in ("status", "asr_verified", "post_slowdown_classification", "post_slowdown_final_classification", "post_slowdown_asr_text", "reason", "slowdown_info")}
print(json.dumps(rec, ensure_ascii=False, default=str)[:1500])
if not (r.get("status") == "OK" and r.get("asr_verified") is True):
    sj(f"{LV}/audit/fzlr05_speed_recheck_FAILED.json", rec); sys.exit("[STOP] 高速化後ASR再検証が不合格。何も配置していません")
now = time.strftime("%Y-%m-%dT%H:%M:%S")
for p in (res_p, lock_p):
    b = p.replace(".json", ".pre_fzlr05_speed_backup.json")
    if not os.path.exists(b): shutil.copyfile(p, b)
orig = f"{NAR}/{SEG}_original.wav"
if os.path.exists(orig) and not os.path.exists(orig.replace(".wav", ".pre_fzlr05.wav")): shutil.copyfile(orig, orig.replace(".wav", ".pre_fzlr05.wav"))
shutil.copyfile(f"{work}/{SEG}_original.wav", orig); shutil.copyfile(f"{work}/{SEG}.wav", f"{NAR}/{SEG}.wav")
new = sha(f"{NAR}/{SEG}.wav"); sd = r["slowdown_info"]
assert sha(orig) == sha(raw)
dur = round(sd["dst_duration_seconds"], 3)
ent.update({"sha256": new, "duration_seconds": dur, "slowdown_applied": True, "slowdown_ratio": round(sd["dst_duration_seconds"] / sd["src_duration_seconds"], 4),
            "adopted_audio_sha256": new, "adopted_attempt_wav_sha256": sha(raw), "original_path": orig,
            "speed_profile": {"version": z63.Z_SPEED_PROFILE_VERSION, "profile": "adv_dialogue_fast6", "applied": True, "tempo": round(1.0 / (1.0 + sd["slowdown_pct_target"] / 100.0), 6),
                              "slowdown_pct_target": sd["slowdown_pct_target"], "original_sha256": sha(orig), "source": "generated"},
            "post_slowdown_final_classification": r.get("post_slowdown_final_classification"), "post_slowdown_classification": r.get("post_slowdown_classification"),
            "post_slowdown_asr_text": r.get("post_slowdown_asr_text")})
ent["FZLR05_SPEED_NOTE"] = f"[{now}] 採用③(raw)へ速度仕様v2の高速化(1.06)を適用し高速化後ASR再検証PASS({r.get('post_slowdown_final_classification')})。ユーザーが聴いた音=速度適用前のraw ③、Production必須の高速化は正式関数で後処理。"
res["segments"][SEG] = ent; sj(res_p, res)
lock = lj(lock_p); lock[SEG]["adopted_audio_sha256"] = new; lock[SEG]["adopted_attempt_wav_sha256"] = sha(raw); sj(lock_p, lock)
sj(f"{LV}/audit/fzlr05_speed_recheck.json", {**rec, "final_wav_sha256": new, "raw_wav_sha256": sha(raw), "duration_seconds": dur, "recorded_at": now})
print("applied", new, dur)
