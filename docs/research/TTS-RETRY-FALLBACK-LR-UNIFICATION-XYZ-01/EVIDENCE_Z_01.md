# EVIDENCE_Z_01 — Family Z runtime evidence(委任_03)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: 2026-10-27 00:45 JST / API実費を伴う実走evidence(実TTS・実ASR・実180秒待機・実LR[gpt-6-luna]・実Gate)

## 方式(全Family共通)

- driver: `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_run_01.py`(+`tru_ev_core_01.py`/`tru_ev_cases_01.py`/`tru_ev_aggregate_01.py`)。**正式のleaf生成関数・scope(`er109 run_scope`/`with_secondary_run`/`guarded_generate`)を直接呼ぶ**。実TTS・実ASR・実180秒`time.sleep`(`cooldown_core`)・実LR・実Gateは本物のまま。
- 強制NG: driver側monkeypatchで**判定結果のNG方向にだけ**上書き(Style・Prompt・Voice・速度・model・待機・回数・Gateは触らない)。上書きは`injected_override_count`と`injected_overrides[]`に全件記録。LR経路はPrimary転写の1語置換(NG方向のみ)で`identify_ng_span`を成立させた。正常系(E-N)は上書き0をassert。
- 環境: `TTS_EXECUTION_MODE=STANDARD`を環境変数とCLI引数の両方で明示。`TTS_BACKEND=speech_metadata_flash_lite` / `STYLE_PROFILE=fx_20261017`(X/Y/Z共通の承認済み)。
- 各case開始前に`tools/stop_scope_check_01.py --managed-id TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01`を実行(63ファイル`stop_check_*.json`、いずれもrc=3[停止]でない)。STOP/STOP_ALLは作成・削除していない(E-STOPはrun専用sentinel `<run>/STOP`のみ)。
- 強制NG由来のHRQ行・attempt_history・Master Audio Store・telemetryは各run dirの`_evidence_ledgers/`へ隔離(本番台帳を汚さない)。evidence専用・対応不要・開発費。
- 判定: `_aggregate_01.json`(case別の機械判定[check名・期待・実測])。PASS=期待どおり/DEVIATION_NATURAL=③等で本物のASRが自然にNGになり期待と異なる経路(フロー自体の検査は通過)/FAIL=不整合。
- 表の読み方: TTS=対象clipの実TTS回数、待機=実測秒(`+`区切り、E-S6はkill前+再開後)、Style列=attempt毎のStyle種別(A=元Style、B=Fallback Style、`[..]`=該当ラベル)、方針Gate=M3(X)/Y Style Gate/Z該当/Gate(当該segmentのみ。未生成の他segmentのNO_SEGMENT_RECORDは対象外)、共有Audio Gate=`asm._segment_gate_status`等のper-segment関数を当該segmentにだけ適用(API 0)。

## Zの判定集計

PASS=15(case数=15。supersededは含まない)

## 方針×シナリオの観測マトリクス(Z)

未観測=本委任で実走していない(Lean計画で除外/代表で固定)。

| 方針/Lv | E-N | E-S1 | E-S2a | E-S2b | E-S3 | E-S4 | E-STOP |
|---|---|---|---|---|---|---|---|
| EN_LR_ADV/b1b | Z-Adv-8[PASS] | 未観測 | Z-Adv-4[PASS] | Z-Adv-1[PASS] | 未観測 | 未観測 | 未観測 |
| EN_LR_STD/a2 | Z-Std-7[PASS] | 未観測 | Z-Std-6[PASS] | Z-Std-1[PASS] | 未観測 | 未観測 | Z-Std-8[PASS] |
| JA_STD/a2 | 未観測 | Z-Std-4[PASS] | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 |
| KP_EN/a2 | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 | Z-Std-5[PASS] | 未観測 |
| KP_EN/b1b | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 | Z-Adv-6[PASS] | 未観測 |
| KP_EXPL/b1b | 未観測 | Z-Adv-5[PASS] | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 |
| Z_DLG_CTX/a2 | 未観測 | Z-Std-2[PASS] | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 |
| Z_DLG_CTX/b1b | 未観測 | Z-Adv-2[PASS] | 未観測 | 未観測 | Z-Adv-3[PASS], Z-Adv-3b[PASS] | 未観測 | 未観測 |

## case別観測表(Z)

| case | Lv | 方針/leaf | シナリオ | TTS | 待機(秒) | LR | HRQ行 | Style列 | 最終 | 方針Gate(M3/Y/Z、当該seg) | 共有Audio Gate(Assemble、当該seg) | 判定 | 実費(円) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Z-Adv-1 | b1b | EN_LR_ADV/L2 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:full_story_part1_c14=STOPPED) | BLOCK(full_story_part1_c14=STOPPED) | PASS | 1.065 |
| Z-Adv-2 | b1b | Z_DLG_CTX/L8 | E-S1(L8 ctx,減速後NG) | 3 | 180 | 0 | 0 |  | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 1.22 |
| Z-Adv-3 | b1b | Z_DLG_CTX/L8 | E-S3(L8 ctx) | 3 | 180 | 0 | 0 |  | STOPPED | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:full_story_part1_c15=STOPPED) | BLOCK(full_story_part1_c15=STOPPED) | PASS | 1.282 |
| Z-Adv-3b | b1b | Z_DLG_CTX/L8 | E-S3(L8 ctx・減速後NG×3でHRQ) | 3 | 180 | 0 | 1 |  | STOPPED | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:full_story_part1_c15=STOPPED) | BLOCK(full_story_part1_c15=STOPPED) | PASS | 1.512 |
| Z-Adv-4 | b1b | EN_LR_ADV/L1 | E-S2a(U-06) | 4 | 180 | 1 | 0 | AABA | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.633 |
| Z-Adv-5 | b1b | KP_EXPL/L5 | E-S1 | 3 | 180 | 0 | 0 | A,A,B[MINIMAL_INSTRUCTION_PREFIX] | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.464 |
| Z-Adv-6 | b1b | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.452 |
| Z-Adv-8 | b1b | EN_LR_ADV/L1 | E-N | 1 | - | 0 | 0 | A | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.218 |
| Z-Std-1 | a2 | EN_LR_STD/L4 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:full_story_part1_c14=STOPPED) | BLOCK(full_story_part1_c14=STOPPED) | PASS | 2.499 |
| Z-Std-2 | a2 | Z_DLG_CTX/L8 | E-S1(L8 ctx) | 3 | 180 | 0 | 0 |  | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 1.513 |
| Z-Std-4 | a2 | JA_STD/L7 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.199 |
| Z-Std-5 | a2 | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.377 |
| Z-Std-6 | a2 | EN_LR_STD/L3 | E-S2a(U-06) | 4 | 180 | 1 | 0 | AABA | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.702 |
| Z-Std-7 | a2 | EN_LR_STD+JA_STD/L3+L7 | E-N | 1 | - | 0 | 0 | A | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.133 |
| Z-Std-8 | a2 | EN_LR_STD/L3 | E-STOP | 2 | - | 0 | 0 | AA | None | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:結果ファイル未生成) | 対象なし(結果未保存) | PASS | 0.169 |

## 実測モデル(raw_usage_log。Zのrun dir合算)

| provider | model_id(実測) | API | 呼出回数 |
|---|---|---|---|
| azure | azure-speech-stt | azure_stt_strict_scg | 1 |
| azure | azure-speech-stt | get_full_text_via_azure_stt_with_phrase_list | 13 |
| gemini | gemini-2.5-pro-preview-tts | models.generate_content(TTS) | 12 |
| gemini | gemini-3.8-flash-lite-tts | models.generate_content(TTS) | 38 |
| openai | gpt-6-luna | responses.create | 20 |
| openai_asr | gpt-4o-mini-transcribe | audio.transcriptions.create | 55 |

## 達成状況と主要観測(Z: er063/er026、Std=a2 / Adv=b1b)

1. **Zセリフ(L8) ctx×2→実180秒→従来(legacy) ③**: Z-Std-2(ctx①②NG→180秒→`legacy_fallback`③PASS)、Z-Adv-2(減速後NG含む通算3)。`results.json`の`dialogue_tts`に`policy=fz_ctx_v1`・attempt毎の`mode`(ctx,ctx,legacy_fallback)・`final_mode=legacy_fallback`・`n_started=3`・待機記録を確認。実モデルは既存仕様どおりZ会話の`gemini-2.5-pro-preview-tts`(multi-speaker。flash-liteではない=本件で不変更)。
2. **Zセリフ終端**: Z-Adv-3(判定戻り値のNG注入×3)/Z-Adv-3b(**減速後NG×3でHRQ行**)。TTS=3・待機1・Lock=HUMAN_REVIEW_REQUIRED。Z-Adv-3bでHRQ 1行を観測(Z-Adv-3は判定器注入の限界でHRQ行0=driver側の限界)。**Z Gate(`assert_tts_results_complete`)=BLOCK**(`FamilyZTtsResultsIncompleteStop`: 未採択=`..._c15=STOPPED`)=従来のrc=2相当の停止。
3. **冒頭英語(U-06: topic_intro_en)の共通化**: Z-Std-6(Std)・Z-Adv-4(Adv)。③NG→実LR(gpt-6-luna)→④PASS、TTS=4・待機1・HRQ 0 = **Z冒頭英語に新たにLRと待機が有効になること**を実証。
4. **narrator chunk E-S2b**: Z-Std-1(L4)・Z-Adv-1(L2)。TTS=6・待機2回・LR=1(再入0)・HRQ 1行・Z Gate BLOCK(`..._c14=STOPPED`)・Lock=HUMAN_REVIEW_REQUIRED。
5. **E-S1/E-S4/E-N**: Z-Std-4(JA)、Z-Std-5・Z-Adv-6(KP英語 ENGLISH_LOCK)、Z-Adv-5(KP解説)、Z-Std-7・Z-Adv-8(正常系)。
6. **E-STOP**: Z-Std-8。待機40秒時点でrun専用STOP設置→待機中に`FamilyZStopSentinel`→TTS 2回で停止・結果ファイル未生成(`assert_tts_results_complete`=BLOCK `tts_generation_results.json が存在しません`)・resume可。

### 逸脱と是正
- Z-Adv-2(旧): ctx slotの意味(全attemptがNG化され③まで強制NGで終端)をdriverが誤解(`_superseded/`)。`by_count`(dialogue_ttsのattempt回数別注入)に修正して再実行。
- Z-Std-2(旧): clip idが`full_story_part1_c15`(a2のplanに無い)で実TTS 0 → `c13`へ変更して再実行。Z-Std-4(旧): JA判定wrapperの引数シグネチャ(`wav_path`)不一致でTypeError → `*args`へ修正して再実行。

### 未観測
- Z-Std-3(Std L8 終端NG→rc=2): Lean計画で★除外。同leaf・同コードをZ-Adv-3/3bで実走(Std/Advはplan差のみ)。
- Z-Adv-7(preview/comment E-S1): ★除外。同leaf(L1 EN_LR_ADV)はX-Adv-1/Z-Adv-4で実走。
