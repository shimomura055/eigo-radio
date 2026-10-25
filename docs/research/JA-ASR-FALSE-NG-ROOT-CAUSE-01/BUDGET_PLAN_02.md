# BUDGET_PLAN_02(Phase 3 有料部分。**本委任では未実行**。JST日付変更後にFableが別委任で起動)

承認枠: Cap=**¥60**(Fable自律範囲、案件300円以下・承認済みScope内=7-7)。日次1,000円の残が少ないため本日は実行しない。分割・日付分割で境界回避はしない(1案件=¥60以内)。
単価の根拠: Azure STT=¥0.0447/秒(月題記録 5.96秒=¥0.2667)。OpenAI gpt-4o-mini-transcribe≒¥0.0008/秒(公表$0.003/分の概算。実測は`usage_log.jsonl`で確認)。Gemini TTS flash-lite=1 clip ¥0.3〜1.0(月run全体音声費15.19円/約25 clip=平均0.6円)。`phase3_paid_runner_01.py plan`の出力と一致。
| # | stage | 内容 | 件数 | 中央値 | 上限 |
|---|---|---|---|---|---|
| 1 | A1_azure_moon | 月題attempt1/3既存wavにAzure(情報取得のみ。B-light保留) | 2 | ¥0.63 | ¥0.81 |
| 2 | A2_openai_moon_x3 | 月題3 wavをOpenAIで各3回再転写 | 9 | ¥0.05 | ¥0.5 |
| 3 | A3_azure_flip | v1 flipのうちAzure未呼出wav(Melos preview等、約12秒) | 〜3 | ¥1.61 | ¥2.09 |
| 4 | N3_tts | N-3誤読音声30 clip(TTS) | 30 | ¥19.5 | ¥30.0 |
| 5 | N3_asr | N-3 30 clipをOpenAI+Azureで転写(各約6秒) | 30×2 | ¥8.19 | ¥10.65 |
| 6 | O1_format_prompt | O1: 書式prompt・`gpt-4o-transcribe`並置(月題3 wav) | 6 | ¥0.03 | ¥0.5 |
| | **合計** | | | **¥30.0** | **¥44.6** |
旧BUDGET_PLAN_01からの変更: N-3 16→30 clip(M6、+約¥12〜20)、N-2のAzure(約¥5.4)を廃止(B-light保留かつN-2はテキストレベルでv1 flip 0のため新規APIは不要)、A-3を約10→約3 wavに縮小(M1でflipが減った)。ローカルWhisperは使わない(第3票として扱わない)。Cap ¥60に対し上限¥44.6で余裕あり。
使用モデル(開発・評価の最新モデル原則25節): TTS=Production JA Std経路(`gemini-3.1-flash-tts-preview`系、`p9a.generate_narration_snippet`のspeech_metadata_flash_lite)=本番検証のため本番モデルが目的。ASR=Production Primary `gpt-4o-mini-transcribe`/Secondary Azure ja-JP(本番判定の再現が目的)。O1のみ`gpt-4o-transcribe`(最新世代の並置)。評価対象判定はLLMを使わない。
量産単価への影響(採用時の見込み): 案A=API追加0(Primaryで通る件が増えるためAzure呼出はむしろ減。月題attempt2で¥0.267節約)。±0.01円/セット未満。削減効果: 1 JA segmentのHR回避で TTS 3回(¥0.9〜3)+ASR+Azure+人手確認を節約。

## 起動手順(Fable、GO発行後)
1. `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/PHASE3_GO.json` を作成: `{"managed_id":"JA-ASR-FALSE-NG-ROOT-CAUSE-01","cap_jpy":60,"stages":["A1_azure_moon","A2_openai_moon_x3","A3_azure_flip","N3_tts","N3_asr","O1_format_prompt"],"issued_by":"Fable","issued_at":"<JST>"}`。**無ければ全stageがrc=4で何も実行しない**(testで副作用0=ファイル作成0・API呼出0を確認済み)。
2. 1起動=1 stage(順序: A1→A2→A3→N3_tts→N3_asr→O1)。各stage冒頭で`tools/stop_scope_check_01.py --managed-id JA-ASR-FALSE-NG-ROOT-CAUSE-01 --run-dir docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/phase3_run`が自動実行され、rc=3ならAPI呼出0で停止。
3. コマンド(repo root、`.venv`のpython):
   - `PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/phase3_paid_runner_01.py plan`(API 0)
   - `... phase3_paid_runner_01.py run --stage A1_azure_moon` → `A2_openai_moon_x3` → `A3_azure_flip` → `N3_tts` → `N3_asr` → `O1_format_prompt`
4. 並列化: N3_ttsとA1〜A3は独立(clip単位の並列は可。ただしrate limitがあれば直列)。N3_asrはN3_tts完了後。runnerは1 stageを逐次実行する(独立stageを別processで同時起動してよい。同一stageの再起動・別名ラッパは作らない)。
5. 失敗時: エラーがあれば自動再試行せずSystemExit(Fableへ報告)。外部停止・原因不明rc≠0が2回で即STOP。再起動は委任文の明示許可のみ。
6. 結果の評価: `usage_log.jsonl`の転写を`eval_api0_v1_01.py`と同じ`primary_stage`/`secondary_accept_kind`に通し、`PHASE3_RESULT.md`に増分誤PASS/既存誤PASS/flip原因別/A4(a)(b)別を記録。Production変更0を`git status`で確認。
注意: runnerの実API経路(Azure/OpenAI/TTS呼出関数)は**API 0のためlive未検証**(GO方式・停止ロジックはtest済み)。最初のstage(A1、約¥0.6)がlive経路の疎通確認を兼ねる。
