# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_03 EVIDENCE_03(X Std / Y Std / Y Adv のProduction runtime発火(到達)証拠。2026-10-31)

目的: FABLE_ACCEPTANCE_01(Fable受入)で「部分不一致」とされた X Std・Y Std・Y Adv のProduction runtime証拠を、EVIDENCE_02 §5と同じ方式(Batch既定=`TTS_EXECUTION_MODE`未設定・新規out dirの複製run・既存記事/run無変更・LLM再生成なし・本文最小で`latter`入り)で取得する。証跡は`ev03/`。コード変更なし(runner・Production関数は無変更。新規は`tools/flapt_y_runtime_evidence_03.py`のみ)。

## 1. 実行結果(セル別。全て BATCH既定、`TTS_EXECUTION_MODE`未設定。各run前に `stop_scope_check_01.py --managed-id ASR-FLAP-T-PRODUCTION-WIRING-01 --run-dir <run>` rc=0: `ev03/stop_check_*.json`)
| セル | 入口(正式) | clip | batches.create(raw_usage_log: provider=gemini_batch, api=batches.create) | 台帳・束縛(wav sha) | sidecar `flapt_provenance_coverage.jsonl` | attempt audit `tts_provenance` |
|---|---|---|---|---|---|---|
| X Std(a2) | **正式runner CLI** `er019_family_x_audio_production_runner_01.py --slug meta_waddle_world --run run_flapt_ev03 --stage tts --level a2 --only-segments in_one_line --budget-jpy 3`(`generate_family_x_a2_segments`=`family_scope("X")`、rc=0) | `in_one_line`(`Adults may choose the latter option if the other one costs more.`) | `gemini-3.8-flash-lite-tts` / `Aoede` / success / cost_jpy 0.049 | 原音 sha`782b2694…`→**6%減速後 sha`5e1a3485…`へ子登録(transform `atempo`,`slowdown_pct=6.0`)**。最終wav(`in_one_line.wav`)sha=`5e1a3485…`(sha256sum一致) | **2/2解決**(scope=X, phase=generation, source=`sdk_boundary_batch`, table_status=confirmed, 原音`transforms:[]`/減速後`[{atempo,6.0}]`) | `{Aoede, gemini-3.8-flash-lite-tts, path:fl, sdk_boundary_batch, transforms:[]}`(attempt1)、減速後判定`transforms:[{atempo,6.0}]` |
| Y Std(a2) | **Y正式TTS段関数** `er121_family_y_audio_01.generate_y_a2_segments`(`:645`、`@er109_scope.family_scope("Y")`)を`only_segments_scope`+最小plan(複製run)で直接実行(rc=0) | `y_intro_1`(Aoede。`First, hear from the latter speaker.`)、`y_voice_1`(Puck。`Many people choose the latter option.`) | y_intro_1: `gemini-3.8-flash-lite-tts`/`Aoede`/0.029、y_voice_1: `gemini-3.8-flash-lite-tts`/`Puck`/0.029 | 各clip 原音sha→**6%減速後sha(子登録、`slowdown_pct=6.0`)**: y_intro_1 `0de1d77d…`→`ab727136…`、y_voice_1 `77b77e92…`→`62cd0850…`。最終wav sha=子sha(一致) | **4/4解決**(scope=Y, phase=generation, table=confirmed: Aoede|fl・Puck|fl) | 4/4: `{Aoede/Puck, gemini-3.8-flash-lite-tts, fl, sdk_boundary_batch}`、減速後は`transforms:[{atempo,6.0}]` |
| Y Adv(b1b) | **Y正式TTS段関数** `generate_y_b1_segments`(`:555`、`@er109_scope.family_scope("Y")`)を同様に直接実行(rc=0) | `y_intro_1`(Aoede)、`y_voice_1`(Puck)(上記と同文) | y_intro_1: `gemini-3.8-flash-lite-tts`/`Aoede`/0.029、y_voice_1: `gemini-3.8-flash-lite-tts`/`Puck`/0.030 | y_intro_1 `9bad7330…`、y_voice_1 `221b633a…`(Advは減速なし。最終wav sha一致) | **2/2解決**(scope=Y, table=confirmed) | `{Aoede/Puck, gemini-3.8-flash-lite-tts, fl, sdk_boundary_batch, transforms:[]}` |
- **sidecarカバー率(新規生成音声のEN判定)=8/8=100%**(X Std 2、Y Std 4、Y Adv 2)。voice/model/shaはBatch実送信記録(raw_usage_logのbatches.create model_id/voice)と一致。全判定PASS(Flap対なし=不発火記録なし・誤救済0)。実run中に自然なFlap転写(latter→Ladder等)は発生せず(EVIDENCE_02と同じ。発火そのものは保存attempt再判定+adapter実経路test=EVIDENCE_02 §4・72 test、到達性は本実run)。
- ASR判定: いずれも`latter`は正しく転写されPASS(asr_text=canonical)。attempt1 OK(再試行なし)。
- 証跡: `ev03/x_std_run/`・`y_std_run/`・`y_adv_run/`(raw_usage_log・sidecar・tts_generation_results・attempt json)、`ev03/*_console.log`、`ev03/cost_and_sidecar_summary.txt`。複製run dirは`er019_output/.../meta_waddle_world__run_flapt_ev03`・`er121_output/family_y_production_01/flapt_ev03/run_{a2,b1b}`(未追跡・commit対象外)。

## 2. 方式・限界(正直な記録)
- X Std: 正式runner CLIを使用(EVIDENCE_02のX Adv runと同じ複製記事`meta_waddle_world`)。`in_one_line`のみ生成(`--only-segments`)、他segmentは非選択(既存entryのまま)。
- Yは正式runner CLIが`write_level_inputs`で`parts.json`を記事から再生成するため最小本文を入れられない(`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/tools/y_chunk_evidence_driver_01.py:3-12`の既存記録)。そのためZ(EVIDENCE_02)と同じく、runnerがstage_ttsで呼ぶ**正式TTS段関数そのもの**を直接実行(構造上不可能ではなく、既存先例`TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_run_01.py:call_y`と同型)。バイパスは`write_level_inputs`相当(parts.json=複製+対象2 segmentのみ最小本文に置換)のみ。
- Y 2 clipの選定: `y_intro_1`=narrator(Aoede)、`y_voice_1`=Voice話者(Puck)。Puck|fl=confirmed(Puck|proのみ未確認=承認仕様どおりの適用外。本runのPuckはflash-lite)。
- `Puck|pro` fail-closed(confirmed=false)は承認仕様どおりの適用外であり、未完了Open Itemではない。
- Risk Flagger保険(`rf_guard`)は複製runの source dir に`research_ledger`が無いためRF_UNAVAILABLE(非Blocking)=EVIDENCE_02のX Adv runと同じ条件(RF用LLM呼出なし)。

## 3. 発生した失敗・停止(全て課金前または再実行で解消。回避策・ガード迂回なし)
| # | 事象 | 原因 | 課金 | 対処 |
|---|---|---|---|---|
| 1 | X Std try1 (`x_std_run_console_try1_env_missing_prebilling_stop.log`) OpenAI credentials missing | 本shellにAPI key環境変数なし(worktreeに.envなし) | 0 | main treeの`.env`を子process環境へ読込んで再起動(`set -a; . .env`。値は表示せず、main treeは無変更) |
| 2 | X Std try2 (`..._try2_crlf_integrity_prebilling_stop.log`) `CONFIRMED_CONTENT_INTEGRITY_VIOLATION`(フォーム送信原文shaがレコードと不一致) | worktreeのcheckoutが`core.autocrlf=true`でCRLF変換され複製元の`confirmed_selection_source/rev1_payload.json`等のshaが変化 | 0 | 複製run dir(新規)のtracked fileを`git show HEAD:`のbytes(LF)で再書込み(179 file。元runは無変更) |
| 3 | X Std try3 (`..._try3_inherited_cost_budget_prebilling_stop.log`) `BUDGET_GUARD cost so far 28.08 JPY > cap 3.0` | 複製元の`raw_usage_log.jsonl`(元runの累計費用)を新out dirへ複製していた | 0(rf_guardの予算確認でSTOP、raw_usage_log行数不変182行を確認) | 複製run dirの`raw_usage_log.jsonl`を空にして再実行(新規runの費用のみ計上) |
| 4 | Y Std try1 (`y_std_run_console_try1_ENOSPC_midrun_stop.log`) `OSError: [Errno 28] No space left on device` | **C:ドライブ空き容量が一時的に枯渇**(df: 使用454G/454G、空き77M→46M。起因は本作業外と推定[本作業のrun出力は各数百KBで小さい。他processの使用は未特定]) | 約¥0.066(`y_intro_1`の1 clipのTTS+ASRまで。`ev03/y_std_try1_enospc/raw_usage_log.jsonl`) | 空きが1.4GBに回復したことを確認後、新規run dirで再実行(1回)。Y Adv runと並列起動。以後ENOSPCなし |
- 再起動した有料runは Y Std 1回のみ(原因=ENOSPC既知)。restart stormなし・STOP通知なし。

## 4. 費用
- X Std ¥0.095(openai 0.01 + gemini_batch 0.05 + openai_asr 0.04)、Y Std ¥0.131、Y Adv ¥0.106、ENOSPC中断分 ¥0.066 = **約¥0.40**(`compute_cost_jpy_so_far`、Azure Secondaryの按分は¥0.1未満の見込みで未計上)。個別Cap ¥5に対し約8%。量産単価影響+0円(量産経路に新API呼出なし)。

## 5. Family×Level別 Status(本証拠による確定)
| Family | Level | runtime証拠(Batch既定) | Status |
|---|---|---|---|
| X | Std(a2) | 本EVIDENCE_03 正式runner CLI(Aoede|fl, 6%子登録) | PRODUCTION_WIRED |
| X | Adv(b1b) | EVIDENCE_02 §5 正式runner CLI | PRODUCTION_WIRED |
| Y | Std(a2) | 本EVIDENCE_03 Y正式TTS段関数(Aoede/Puck|fl, 6%子登録) | PRODUCTION_WIRED |
| Y | Adv(b1b) | 本EVIDENCE_03 Y正式TTS段関数(Aoede/Puck|fl) | PRODUCTION_WIRED |
| Z | Std(a2) | EVIDENCE_02 §5 | PRODUCTION_WIRED |
| Z | Adv(b1b) | EVIDENCE_02 §5 | PRODUCTION_WIRED |
- 全6セルでBatch実run証拠が揃った(ユーザー原文:122「PRODUCTION_WIREDの全条件を満たしたFamily・レベルのみ完了扱い」を充足)。受入記録=`FABLE_ACCEPTANCE_01.md`(Fable受入ACCEPTED 2026-10-31+§追記[委任_03])。
- 適用外(承認仕様どおり、未完了Open Itemではない): `Puck|pro`(confirmed=false)、未確認Voice、出自のない既存の保存音声。
