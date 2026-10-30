# -*- coding: utf-8 -*-
"""FAMILY-X-SELECTED-4 委任_09 案(未実行): ⑨Meta Adv(b1b) vocab_extra 第3項目「latter」英語音声のHuman Review承認反映。
ユーザーがHR page(user_test/family_x_meta_waddle_world_hr_02)でattempt4音声を試聴し採用を明示承認した後にだけ --apply --statement <原文file> で実行する。
既存HR承認経路(fx4g_hr_adopt_meta_part3_k2.py / er121_e1_hr_adopt_r0_01.apply と同型)のみ使用:
asm.record_human_approval(segment=kpv3_vocab_extra_english, canonical_text=latter) + review_lock RESOLVED/HUMAN_APPROVED + results注記 + er137.export_level再実行(API 0)。
新Gate/新閾値なし。--apply無しはdry-run(書込0)。API 0・TTS/ASR 0。status手書きなし(statusはSTOPPEDのまま正直に維持=_segment_gate_statusがapprovalsでHUMAN_APPROVED判定)。"""
import hashlib, json, os, shutil, sys, time
sys.path.insert(0, os.getcwd())
import er003_v1_n3_01_assemble as asm
import er137_vocab_extra_audio_01 as v3
RUN = os.environ.get("FX4_DATA_ROOT", ".") + "/er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01"
LV, N = "b1b", 3
SEG_KEY, LOCK_KEY = "kpv3_vocab_extra_english", "vocab_extra_3_en"
EXPECT = "1c033d171323c97e333e11a3e313552a957da1d9379eb90fb74743a58990e981"   # HR page掲載のattempt4 wav
TAG = "fx4h"
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def lj(p): return json.load(open(p, encoding="utf-8"))
def sj(p, d): json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
lv = f"{RUN}/{LV}"; narr = f"{lv}/narration"; kp_dir = f"{lv}/key_phrases"
wav = f"{narr}/vocab_extra_3_en.wav"
att4 = f"{narr}/attempts/vocab_extra_3_en_attempt4_custom31eb2f72.wav"
assert sha(wav) == EXPECT and sha(att4) == EXPECT, "HR page掲載の判断対象音声とsha不一致"
res_path, lock_path = f"{lv}/audit/tts_generation_results.json", f"{lv}/audit/review_lock_state.json"
res = lj(res_path); ent = res["vocab_extra"]["v3"]["vocab_extra_english"]; lock = lj(lock_path)
assert ent["status"] == "STOPPED" and ent["canonical_text"] == "latter" and lock[LOCK_KEY]["state"] == "HUMAN_REVIEW_REQUIRED"
assert ent.get("sha256") in (None, EXPECT), ("entry.sha256", ent.get("sha256"))
print("plan: approve", SEG_KEY, "canonical_text=latter wav_sha", EXPECT[:12], "-> record_human_approval + lock RESOLVED + export_level(b1b)")
if "--apply" not in sys.argv:
    print("dry-run ok (書込0)"); sys.exit(0)
STMT = sys.argv[sys.argv.index("--statement") + 1]          # ユーザー承認原文ファイル(必須)
assert os.path.isfile(STMT) and "latter" in open(STMT, encoding="utf-8").read(), "承認原文fileが無い/latterに言及なし"
for p in (res_path, lock_path):
    b = p.replace(".json", f".pre_{TAG}_adopt_backup.json")
    if not os.path.exists(b): shutil.copyfile(p, b)
now = time.strftime("%Y-%m-%dT%H:%M:%S")
asm.record_human_approval(lv, SEG_KEY, ent["canonical_text"], approved_by="user")
le = lock[LOCK_KEY]
le["prior_state"], le["prior_final_status"] = le.get("state"), le.get("final_status")
le["state"], le["final_status"], le["updated_at"] = "RESOLVED", "HUMAN_APPROVED", now
le["adopted_audio_sha256"] = EXPECT
le["reason"] = f"個別Human Approval({now}、FAMILY-X-SELECTED-4 委任_09)。ユーザーがHR pageの1音声(attempt4)を試聴し「latter」と確認、採用を承認。原文={STMT}。この1segment・1takeへの個別承認のみ(一般的なASR/QA検査免除ではない)。"
lock[LOCK_KEY] = le; sj(lock_path, lock)
ent["FX4H_HUMAN_APPROVAL_NOTE"] = f"[{now}] 個別Human Approval: attempt4採用(原文={STMT})。ASR NG記録は維持、status=STOPPEDは正直な記録として維持。TTS/ASR生成0。一般仕様ではない。"
ent["adopted_audio_sha256"] = EXPECT
sj(res_path, res)
sj(f"{lv}/audit/{TAG}_user_approval_record_{SEG_KEY}.json", {"segment": SEG_KEY, "level": LV, "approved_by": "user", "approved_at": now,
   "user_statement_source": STMT, "adopted_audio_sha256": EXPECT, "scope": "this single segment / this take only; NOT a general ASR/QA exemption; no API call"})
d = v3.export_level(lv, kp_dir, LV)
print("APPLIED; vocab_audio complete=", d["complete"], d["errors"])
