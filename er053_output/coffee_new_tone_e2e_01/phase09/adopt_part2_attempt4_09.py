# -*- coding: utf-8 -*-
"""委任_09 Step1: Standard full_story_part2 の Attempt 4(Local Rewrite後の再TTS、narration/full_story_part2.wav)を
ユーザー試聴PASS(2026-10-11)に基づき既存の人間承認API record_human_approval() で個別承認として記録する。
wav手コピー/lock・manifest直接編集なし(wavは既に最終パスに存在。API呼出0)。
実行はworktree root、main .venv python、PYTHONUTF8=1。"""
import hashlib, json, os, shutil, time
import er003_v1_n3_01_assemble as asm

A2 = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/a2"
OUT = "er053_output/coffee_new_tone_e2e_01/phase09"
WAV = A2 + "/narration/full_story_part2.wav"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
h = lambda t: hashlib.sha256(t.encode()).hexdigest()

parts = json.load(open(A2 + "/parts.json", encoding="utf-8"))
res_path = A2 + "/audit/tts_generation_results.json"
if not os.path.exists(OUT + "/tts_generation_results.pre_adopt_backup.json"):
    shutil.copyfile(res_path, OUT + "/tts_generation_results.pre_adopt_backup.json")
canon = json.load(open(res_path, encoding="utf-8"))["segments"]["full_story_part2"]["canonical_text"]
assert canon == parts["part2"]
q = [json.loads(l) for l in open("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", encoding="utf-8")]
lr = q[-1]
assert lr["timestamp"].startswith("2026-10-11T15:35") and lr["wav_path"].endswith("a2/narration/full_story_part2.wav")

rec = {
    "task": "FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 delegation_09",
    "decision": "ユーザー試聴PASS・採用承認 (2026-10-11)。Standard full_story_part2 の Attempt 4 (Local Rewrite後の再TTS)。記事全体の音声品質承認ではない(Standard/Advanced完成版の最終試聴で別途判断)。",
    "adopted_attempt_id": "attempt4 (part2_review通し番号) = Local Rewrite後の再TTS = narration/full_story_part2.wav (15:35)",
    "adopted_wav_path": WAV, "adopted_wav_sha256": sha(WAV),
    "mechanism": "er003_v1_n3_01_assemble.record_human_approval(out_dir=a2, segment_key='full_story_part2', canonical_text=parts.part2) -> audit/human_approved_segments.json",
    "approved_canonical_text_sha256(parts.part2)": h(canon),
    "spoken_text_note": "実際に読まれた文面はLocal Rewrite後(queue 15:35:44 canonical_text, sha %s)。差分: US data->data from the United States、two numbers->2 numbers、nine months->9 months、引用符除去。" % h(lr["canonical_text"]),
    "spoken_text_local_rewrite": lr["canonical_text"],
    "asr_history": {"final_status_queue": lr.get("final_status"), "steps": lr.get("steps")},
    "other_attempt_wav_sha256": {n: sha(A2 + "/narration/attempts/full_story_part2_" + n + ".wav") for n in
        ("attempt1_customf1837a73", "attempt2_customf1837a73", "attempt3_customf1837a73", "attempt4_minimalfallback")},
    "review_lock_note": "review_lock_state.json は HUMAN_REVIEW_REQUIRED のまま不変(RESOLVEDにするとguardがproceedして再生成するため触らない)。"
                        "guard入力text(tts_safe_news_en, sha ebeffd..)は不一致のまま lock が 0 API call でブロックする。",
    "approved_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "approved_by": "user_2026-10-11_listening_PASS(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01)",
}
asm.record_human_approval(A2, "full_story_part2", canon, approved_by=rec["approved_by"])
json.dump(rec, open(OUT + "/part2_attempt4_adoption_record_09.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps({k: rec[k] for k in ("adopted_wav_sha256", "approved_canonical_text_sha256(parts.part2)")}, indent=1))
print(open(A2 + "/audit/human_approved_segments.json", encoding="utf-8").read())
