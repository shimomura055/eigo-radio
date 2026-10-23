# RUNTIME_EVIDENCE_04(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_04、OPEN-459、2026-10-23)

Status: `WIRED_PENDING_FABLE`(PRODUCTION_WIREDはFable受入後)。対象=er109 v1(正式採用APPROVED_FOR_PRODUCTION、Family X/Zのみ)。
実行前確認: STOPセンチネル rc=0(`er109_output/aho4_runtime_evidence_01/stop_check_*.json`、run dirごと)、`TTS_EXECUTION_MODE=STANDARD`、使用モデルは本番既定(TTS=gemini-3.8-flash-lite-tts[Aoede]、ASR=OpenAI Primary[保存転写]/Azure STT[実呼出]/ローカルWhisper small int8、KP選定=本番既定)。評価用モデルの新規選定なし。
証跡置き場: `er109_output/aho4_runtime_evidence_01/`(invariance_compare_*.json、live/、h1/、h3/、hr_rejudge_scan_summary.json、regression_*)。実行script=`er109_runtime_evidence_04_01.py`(本番adapterを`run_scope`内で呼ぶ。monkeypatchなし)。

## 1. 判定表(X/Z別・①②別)
| # | 項目 | X | Z | 根拠 |
|---|---|---|---|---|
| H1 ① 実音声+実Azure | `pump one's fist`(保存wav)を配線後の本番KP voteへ。**自然発火**: Azure実呼出が`Pump 1's fist.`→label=`ORTHOGRAPHIC_EQUIVALENT_MATCH`(`ortho_applied=true`、warnings=[])。case X_kp_h1b_stored_wav: P=`Pump one's fist.`(PASS)+S(ortho PASS)=`PASS`行P+S、`orthographic_equivalence{applied:true, scope:"X", label, sites:[secondary]}`、vote audit `ortho_layer_version`/`ortho_scope=X`。case X_kp_jre_a1/a2(HR Lock済みattemptの音声。P=`Pump one fist.`はNG): S(ortho)+Whisper(`Pump One's Fist`/`Pump Ones Fist`)=`PASS_WITH_WARNING`行S+W(従来はNG_BOTHでHR Lock) | (該当表記差の音声なし)=**未観測** | `live/live_results.json`、`live/run.log` |
| H1 ① 判定の健全性 | 偽PASS: Z_kp1(`Sentenced to death.`、P/S両方NG)はNG_BOTHのまま・orthoなし。X body(small_bag part2 attempt2)はNG_BOTH・ortho null(誤転写をorthoで救済しない) | 同左(Z_kp1_a1 NG_BOTH) | 同上 |
| H2 X本文 | 本文1 segment(small_bag b1b part2 attempt2、実Azure)を本番adapterへ: scope=X有効、`orthographic_equivalence`は付与されない(表記差がないため)=従来判定と同じNG_BOTH。**本文でorthoが自然発火する保存音声・`no`を含むsegmentは存在せず未観測**(決定的ケースH5とtestで補完) | — | `live/live_results.json` |
| H3 Z | KP段(`--stage kp`、新run dir `run_aho4_z_h3`、費用1.0506円): 選定=a2[pulled him under/in someone's place/For once]・b1b[sentence him to death/rise above the other voices/earn such trust]。**`seize`は選定されず、表記差ケースの新規生成は未観測**。Z保存wav 3件(kp1/kp3)を`run_scope("Z")`内で本番adapterに通した: scope=Z、vote auditに`ortho_layer_version`/`ortho_scope=Z`、`sees`/`Seas.`は既存の同音救済(HOMOPHONE_EQUIVALENT)でPASS(ortho非関与=`orthographic_equivalence`なし、従来どおり)。`tts_b1b`のKP3clip生成は**restart storm sentinel**(300秒に3回起動=私の`kp`stage失敗1回+kp+tts)で`STOP`が自動作成され停止(費用0)。sentinelは削除・`--clear-stop`せず(解除はFable/ユーザーのみ)=**Zの新規TTS生成runtime=未観測** | `live/live_results.json`、`h3/kp_stage.log`、`h3/tts_b1b_kp.log`、`er026_output/.../run_aho4_z_h3/STOP` |
| H1b X正式入口の新規生成 | `er019_family_x_audio_production_runner_01 --stage tts --only-segments kp1_english,kp2_english,kp3_english`(新run dir `coffee_prices__run_aho4_h1b`、`family_scope("X")`装飾の本番入口): KP3件ともMaster Audio Store再利用(`reused:true`)、継承記録 `asr_judgement_inherited`=PASS(kp1=`vote_2of3:primary+whisper`、ortho非関与)→Store guard(M1)は**ortho非関与なので再利用を許可**。費用0.00(新規API呼出0)。KP選定は新規scaffoldで`on a regular basis/in stock/push prices up`となり`pump one's fist`は再選定されなかったため、**X正式入口の新規生成でortho自然発火は未観測**(選定が非決定的。scaffold費用0.37円) | — | `h1/tts_kp.log`、`h1/`、`coffee_prices__run_aho4_h1b/a2/audit/tts_generation_results.json` |
| H4 保存wavの継承経路(0円) | 保存9,003行×5経路(adapter/adapter_kp/guard/rejudge/voter)=43,033署名: flag ON×X scope: PASS->NG **0**、NG->PASS=adapter 30/adapter_kp 38/rejudge 113/guard 4(blocked->not blocked)。Zも同数(同一judge)。no scope・flag False(rollback)は43,033/43,033が配線前とバイト一致 | 同左 | `invariance_compare_{none,X,Z}.json`、`main_after_log_*.txt`、署名sha `752072fd…` |
| H5 決定的ケース(0円) | `one`↔`1`・`one's`↔`1's`・`ten`↔`10`・`too`↔`to`(Marcus/Markus型)ほか: `er109_xz_scope_01_test_01`(56)・`er109_xz_isolation_01_test_01`(14)・`er109_hr_lock_rejudge_01_test_01`(7)・`er109_wiring_golden_test_01`(6)でPASS。②`no`↔`know`=`PASS_WITH_WARNING`+`ORTHO_NEGATION_WORD_HOMOPHONE`+registry記録(test) | 同左 | test出力 |
| ② 実音声 | `no`↔`know`の保存音声・新規生成は**未観測**(testのみ)。 | **未観測** | — |

## 2. 費用(出典付き)
- X scaffold(`coffee_prices__run_aho4_h1_kpselect_nohit`)0.37円(runner出力`cost so far=0.37 JPY`)。X tts(h1b)0.00円(runner出力)。Z kp stage 1.0506円(runner出力`spent_jpy`)。
- 実Azure STT 7呼出=送信音声39.781秒(`live/cost_log.jsonl`の`audio_duration_submitted_seconds`合計)。単価=`er005_output/cost_baseline_01/pricing_snapshot.json`(azure audio_hour 1.0 USD/hour)→0.0110 USD。換算レートは150円/USDと仮定して約1.7円(**試算**、実請求ではない)。OpenAIはPrimary保存転写使用で0、Whisperはローカル0。
- 合計約3.1円(上限40円内、見積13.5円内)。再起動した有料runなし(h1のscaffold-onlyは前提不足のRuntimeErrorで費用0の1回失敗、その後の再実行は別run dir)。

## 3. 開示
- Z `tts_b1b` は restart storm sentinel で停止(上記)。私の起動回数(失敗した1回を含む3回/300秒)が原因。**STOPを削除・回避していない**。Zの新規TTS生成は未観測。
- `three`↔`3:00`(rule `number_spoken_form`、pairs_02 pair2664)が既存の判定でPASSする: 音声が「three o'clock」でも正解`three`に合格し得る。er109内部の既承認ルールで、本タスクの再レビュー対象外。Fable判断材料として開示。
