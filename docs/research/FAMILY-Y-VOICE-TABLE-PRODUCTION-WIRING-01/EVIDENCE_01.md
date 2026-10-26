# EVIDENCE_01 — runtime evidence(PARTIAL。Std取得済み、Adv以降は自己発動RESTART_STORMで停止)
run dir: `er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01`(run_01の入力[text/translate/support/kp/study等]を複製、音声assembled・review_lock・human_approved・ログは除外)。公開dir・run_01は無変更。
コマンド(全て `TTS_EXECUTION_MODE=STANDARD`): `.venv\Scripts\python.exe er121_family_y_runner_01.py --slug redelivery_fee --run run_voice_puck_ev_01 --mode real --stage tts_a2 --only-segments y_voice_1 --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 60 --tts-execution-mode STANDARD`
起動: ①17:20:24 rc=2(`--theme-package`省略によるseed不一致STOP、API 0) ②17:22:34 rc=0 ③17:25:10 `--stage tts_b1b` → rc=3 FAMILY_Z_RESTART_STORM(同run 300秒内3起動。①のrc=2起動も数えられた**私の起動計画ミス**。API 0。`STOP`/`RESTART_STORM_LOCK.json`は削除せず保全)。
## Std(a2) y_voice_1 結果
- actual voice=**Puck**(results `voice`/`y_tts_voice_requested`)、model=`gemini-3.8-flash-lite-tts`(cost_log model_id)、backend=`speech_metadata_flash_lite`、STANDARD。
- attempt数=**1**(call_count=1, retry_count=0, fallback_used=False)。ASR=PASS(NORMALIZED_MATCH / primary_pass)、Repetition QA flagged=False、slowdown_applied=True、duration 41.698秒。
- 範囲限定: cost_logはy_voice_1のTTS 1回+ASR 2回のみ。他segment(voice_2/3、narrator)は再生成されず(cost_log 3行)。
- 費用: **1.3459円**(Std)。
## 未取得(STORM STOPで未実行)
Adv(b1b) Voice 1、同引数再起動のAPI 0確認、gate、assemble。`--clear-stop`は解除権限がFable/ユーザーのため実行せず。
## Puck vs Algieba(OPEN-533記録との対比)
Algieba: Repetition旗率72%・take OK率38%(OPEN-533)。Puck: Trial fresh 24/24・平均1.21 attempt/take。本evidence Std: **1 attempt、Repetition非旗**。Advは未取得。
