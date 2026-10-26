# EVIDENCE_02 — runtime evidence(委任_02。Std[EVIDENCE_01]+Adv+再起動API 0+Gate+組立)
run dir: `er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01`。公開dir・run_01・pages: 無変更/未実行。コード編集なし。
## 1. STOPの再確認と解除
- stop_check_02.json: rc=3(RUN_STOP+RESTART_STORM_LOCK)。`RESTART_STORM_LOCK.json`=created 17:25:10, launches_in_window=3, window 300s。3起動(run_launch_log.jsonl): 17:20:24(`--theme-package`省略、rc=2、API 0)/17:22:34(Std成功)/17:25:10(`--stage tts_b1b`、rc=3、API 0)。=自己発動、課金異常なし。
- 解除(Fable許可、17:29:12): `py er121_family_y_runner_01.py --clear-stop --slug redelivery_fee --run run_voice_puck_ev_01 --reason "FABLE_AUTHORIZED: ..."` → removed=[STOP, RESTART_STORM_LOCK.json]、STOP_ALL無し。run_launch_log.jsonlに`CLEARED`イベント記録。
## 2. 起動(環境 TTS_EXECUTION_MODE=STANDARD、共通引数 `--slug redelivery_fee --run run_voice_puck_ev_01 --mode real --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 20 --tts-execution-mode STANDARD --only-segments y_voice_1`)
| 起動 | 開始 | 間隔 | stage引数 | rc | API |
|---|---|---|---|---|---|
| A | 17:30:38 | (解除後) | `--stage tts_b1b` | 0 | TTS 1+ASR 1 |
| B | 17:33:25 | 167秒 | `--stages tts_b1b,tts_a2,gate,assemble` | 2 | 0 |
| C | 17:36:26 | 181秒 | 同上 | 0 | 0 |
(注: 委任文の`--level b1b`/`--budget-jpy`は実在せず、実名`--stage`/`--approved-budget-jpy`を使用。)
B rc=2の原因: assemble時のAudio Validation Gateが`a2 preview=STOPPED`でBLOCK。`preview`はrun_01時点で既にSTOPPED(ASR不合格)→user承認(`run_01/a2/audit/human_approved_segments.json` preview, sha dc4068f8…)で通っていた既存segment。前委任のrun dir複製で`human_approved`が除外されていたため。対処=承認記録のうち`preview`の1件だけをrun_01から複製(canonical text sha照合付き、本文不変)。y_voice_1の承認は複製せず(Puck新音声はstatus=OKでVALIDATED、承認不要)。複製後Cで解消。
## 3. Adv(b1b) y_voice_1
- actual voice=Puck(`voice`/`y_tts_voice_requested`)、model=gemini-3.8-flash-lite-tts(cost_log)、backend=speech_metadata_flash_lite、STANDARD。attempt=1(attempts_log長1、cost_log TTS 1回/ASR 1回)。
- ASR: asr_judgement=PASS/primary_pass/EXACT_MATCH。Repetition QA flagged=False(method_a_ngram空)。長さ39.52秒。b1bにslowdownなし(A2のみ)。
- Style prefix(Adv): `calm, steady news narration with natural emphasis at key points and turns; not dramatic.`
- (参考 Std/A2) attempt 1、NUMERIC_EQUIVALENCE_MATCH、slowdown 5.967%、41.698秒、prefix=上記+「Speak at a slightly slower, relaxed pace…」(EVIDENCE_01)。
## 4. 再起動API 0
B(rc=2)・C(rc=0)ともcost_log.jsonl 5行不変(A直後と同数)、spent_jpy=2.511不変。results: y_voice_1 call_count=1/attempts 1のまま。
## 5. Gate・組立
- Y style profile gate: a2/b1b=PASS(y_voice_1 violations=[]。以前の`LOCAL_REWRITE_RECOVERY`はrun_01複製の古い値で、再計算で消えた)。key_phrase_source_gate PASS(3/3)。
- 共有Audio Validation Gate(assemble内`verify_episode_audio_validation_gate`): C起動でPASS(assemble到達)。
- 組立: a2 `Family_Y_REDELIVERY_FEE_A2.wav` 342.261秒 peak 0.866 clipping無し/b1b `…_B1.wav` 315.85秒 peak 0.867 clipping無し。pronunciation alarm 0。pages/page_verifyは未実行(禁止)。
## 6. §6 9項目チェックリスト
1 承認仕様一致=OK(Voice 1=Puck、候補表男5女5、前委任test)。
2 正式初回経路実装=OK(`Y_DIALOGUE_VOICE_POOL`/`FIXED_VOICE_SLOTS`、commit 31c41ea76)。
3 retry/fallback/regeneration/resume整合=OK:再起動API 0(§4)、旧Algieba cache非復活=`er121_family_y_audio_01.py:191-212 voice_guard_cached`が`y_tts_voice_requested`不一致entry(chunk含む)をpopして再生成。run_01の旧entryは`y_tts_voice_requested`無し/Algiebaのため再利用されない。
4 正式runtime発火証拠=OK(Std/Adv actual voice=Puck、正式CLI)。
5 Regression/Validator/integration test=前委任でer121回帰306 PASS/1 skip、新規9件(本委任はコード変更なし)。
6 actual model_id・routing=gemini-3.8-flash-lite-tts/STANDARD/speech_metadata_flash_lite。
7 CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新=本委任はSSOT編集権なし。Fable sync待ち(RESULT_PACKET_YVT2 (9)に文案)。
8 Git反映=commit(本委任分は後記)+前委任31c41ea76。
9 未承認仕様・Dangling Reference=なし(コード変更なし、flag新設なし)。
