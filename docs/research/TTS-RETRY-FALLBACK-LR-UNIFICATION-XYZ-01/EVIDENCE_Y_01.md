# EVIDENCE_Y_01 — Family Y runtime evidence(委任_03)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: 2026-10-27 00:45 JST / API実費を伴う実走evidence(実TTS・実ASR・実180秒待機・実LR[gpt-6-luna]・実Gate)

## 方式(全Family共通)

- driver: `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_run_01.py`(+`tru_ev_core_01.py`/`tru_ev_cases_01.py`/`tru_ev_aggregate_01.py`)。**正式のleaf生成関数・scope(`er109 run_scope`/`with_secondary_run`/`guarded_generate`)を直接呼ぶ**。実TTS・実ASR・実180秒`time.sleep`(`cooldown_core`)・実LR・実Gateは本物のまま。
- 強制NG: driver側monkeypatchで**判定結果のNG方向にだけ**上書き(Style・Prompt・Voice・速度・model・待機・回数・Gateは触らない)。上書きは`injected_override_count`と`injected_overrides[]`に全件記録。LR経路はPrimary転写の1語置換(NG方向のみ)で`identify_ng_span`を成立させた。正常系(E-N)は上書き0をassert。
- 環境: `TTS_EXECUTION_MODE=STANDARD`を環境変数とCLI引数の両方で明示。`TTS_BACKEND=speech_metadata_flash_lite` / `STYLE_PROFILE=fx_20261017`(X/Y/Z共通の承認済み)。
- 各case開始前に`tools/stop_scope_check_01.py --managed-id TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01`を実行(63ファイル`stop_check_*.json`、いずれもrc=3[停止]でない)。STOP/STOP_ALLは作成・削除していない(E-STOPはrun専用sentinel `<run>/STOP`のみ)。
- 強制NG由来のHRQ行・attempt_history・Master Audio Store・telemetryは各run dirの`_evidence_ledgers/`へ隔離(本番台帳を汚さない)。evidence専用・対応不要・開発費。
- 判定: `_aggregate_01.json`(case別の機械判定[check名・期待・実測])。PASS=期待どおり/DEVIATION_NATURAL=③等で本物のASRが自然にNGになり期待と異なる経路(フロー自体の検査は通過)/FAIL=不整合。
- 表の読み方: TTS=対象clipの実TTS回数、待機=実測秒(`+`区切り、E-S6はkill前+再開後)、Style列=attempt毎のStyle種別(A=元Style、B=Fallback Style、`[..]`=該当ラベル)、方針Gate=M3(X)/Y Style Gate/Z該当/Gate(当該segmentのみ。未生成の他segmentのNO_SEGMENT_RECORDは対象外)、共有Audio Gate=`asm._segment_gate_status`等のper-segment関数を当該segmentにだけ適用(API 0)。

## Yの判定集計

DEVIATION_NATURAL=3, PASS=11(case数=14。supersededは含まない)

## 方針×シナリオの観測マトリクス(Y)

未観測=本委任で実走していない(Lean計画で除外/代表で固定)。

| 方針/Lv | E-N | E-S1 | E-S2a | E-S2b | E-S4 | E-STOP |
|---|---|---|---|---|---|---|
| EN_LR_ADV/b1b | Y-Adv-5[PASS] | 未観測 | Y-Adv-1[PASS], Y-Adv-4[DEVI], Y-Adv-4b[PASS] | 未観測 | 未観測 | 未観測 |
| EN_LR_STD/a2 | Y-Std-5[PASS] | Y-Std-4[DEVI], Y-Std-4b[PASS] | 未観測 | Y-Std-1[PASS] | 未観測 | Y-Std-6[PASS] |
| JA_STD/a2 | 未観測 | Y-Std-2[DEVI], Y-Std-2b[PASS] | 未観測 | 未観測 | 未観測 | 未観測 |
| KP_EN/a2 | 未観測 | 未観測 | 未観測 | 未観測 | Y-Std-3[PASS] | 未観測 |
| KP_EN/b1b | 未観測 | 未観測 | 未観測 | 未観測 | Y-Adv-3[PASS] | 未観測 |
| KP_EXPL/b1b | 未観測 | Y-Adv-2[PASS] | 未観測 | 未観測 | 未観測 | 未観測 |

## case別観測表(Y)

| case | Lv | 方針/leaf | シナリオ | TTS | 待機(秒) | LR | HRQ行 | Style列 | 最終 | 方針Gate(M3/Y/Z、当該seg) | 共有Audio Gate(Assemble、当該seg) | 判定 | 実費(円) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Y-Adv-1 | b1b | EN_LR_ADV/L1 | E-S2a | 4 | 180 | 1 | 0 | AABA | OK | BLOCKなし | PASS | PASS | 1.152 |
| Y-Adv-2 | b1b | KP_EXPL/L5 | E-S1 | 3 | 180 | 0 | 0 | A,A,B[MINIMAL_INSTRUCTION_PREFIX] | OK | BLOCKなし | PASS | PASS | 0.409 |
| Y-Adv-3 | b1b | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | BLOCKなし | PASS | PASS | 0.411 |
| Y-Adv-4 | b1b | EN_LR_ADV/L2 | E-S2a+YGate | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCK(y_voice_1:FINAL_STYLE_RECORD_MISSING+ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED) | BLOCK(y_voice_1=STOPPED) | DEVIATION_NATURAL | 7.058 |
| Y-Adv-4b | b1b | EN_LR_ADV/L2 | E-S2a+YGate | 4 | 180 | 1 | 0 | AABA | OK | BLOCK(y_voice_1:LOCAL_REWRITE_RECOVERY) | PASS | PASS | 8.558 |
| Y-Adv-5 | b1b | EN_LR_ADV/L1 | E-N | 1 | - | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.282 |
| Y-Std-1 | a2 | EN_LR_STD/L3 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(topic_intro=STOPPED) | PASS | 1.323 |
| Y-Std-2 | a2 | JA_STD/L7 | E-S1 | 3 | 180 | 0 | 1 | AAB | STOPPED | BLOCKなし | BLOCK(japanese_title=STOPPED) | DEVIATION_NATURAL | 0.325 |
| Y-Std-2b | a2 | JA_STD/L7 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.494 |
| Y-Std-3 | a2 | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | BLOCKなし | PASS | PASS | 0.318 |
| Y-Std-4 | a2 | EN_LR_STD/L4 | E-S1+YGate | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCK(y_voice_1:FINAL_STYLE_SHA_MISMATCH_NO_HINT+STD_FALLBACK_USED_OR_UNKNOWN;y_voice_1:Y_MISSING_MANDATORY_A2_SLOWDOWN) | BLOCK(y_voice_1=STOPPED) | DEVIATION_NATURAL | 4.827 |
| Y-Std-4b | a2 | EN_LR_STD/L4 | E-S1+YGate | 3 | 180 | 0 | 0 | AAB | OK | BLOCK(y_voice_1:FINAL_STYLE_SHA_MISMATCH_NO_HINT+STD_FALLBACK_USED_OR_UNKNOWN) | PASS | PASS | 6.539 |
| Y-Std-5 | a2 | EN_LR_STD+JA_STD/L3+L7 | E-N | 1 | - | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.218 |
| Y-Std-6 | a2 | EN_LR_STD/L3 | E-STOP | 2 | - | 0 | 0 | AA | None | 結果未保存(STOP中断のためGate対象なし) | 対象なし(結果未保存) | PASS | 0.255 |

## 実測モデル(raw_usage_log。Yのrun dir合算)

| provider | model_id(実測) | API | 呼出回数 |
|---|---|---|---|
| azure | azure-speech-stt | azure_stt_strict_scg | 3 |
| azure | azure-speech-stt | get_full_text_via_azure_stt_with_phrase_list | 17 |
| gemini | gemini-3.8-flash-lite-tts | models.generate_content(TTS) | 44 |
| openai | gpt-6-luna | responses.create | 25 |
| openai_asr | gpt-4o-mini-transcribe | audio.transcriptions.create | 45 |

## 達成状況と主要観測(Y: er121、Std=a2 / Adv=b1b)

1. **E-S2b(topic_intro)**: Y-Std-1。TTS=6・待機179.999秒×2・LR=1(再入0)・HRQ 1行・Lock=HUMAN_REVIEW_REQUIRED・共有Audio Gate BLOCK。
2. **E-S1(JA)**: Y-Std-2b(PASS)。①②=65字→③=60字Style。初回Y-Std-2は③が実ASRで自然NG→HR(DEVIATION_NATURAL。HRQ 1行は判定器が最終slotで実際に書いた行=JA終端の実書込を観測)。
3. **E-S4(KP英語)**: Y-Std-3、Y-Adv-3。3 TTS・待機1・③=ENGLISH_LOCK、Gate=WARNING(`KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2`)のみ。
4. **E-S1(KP解説 Adv)**: Y-Adv-2。①②=Adv Style→③=minimal。TTS=3・待機1。
5. **E-S2a(Adv comment)**: Y-Adv-1。③NG→LR→④(元Style)PASS。TTS=4。
6. **Y本文Voice(Y Gate)**:
   - **Y-Std-4b**(L4 y_voice_1、Std ①②NG→180秒→③PASS): 本文Voiceを全attemptで保持。**Y Style Gate = BLOCK**(`FINAL_STYLE_SHA_MISMATCH_NO_HINT`+`STD_FALLBACK_USED_OR_UNKNOWN`) = Std本文③採用はY Gate対象(HR承認待ち)。OPEN-537のfail-closed設計どおり(Gate自体は不変更)。
   - **Y-Adv-4b**(L2 y_voice_1、Adv ①②③NG→LR→④PASS): ④=**元role Style(Puck/`Speak directly to one listener...`[177字])を保持**(③のみ30字短文)。Voiceも不変。**Y Style Gate = BLOCK**(`LOCAL_REWRITE_RECOVERY`) = LR採用本文はY Gate対象(HR承認待ち)。
   - 初回 Y-Std-4 / Y-Adv-4 は③等が実ASRで自然NG→LRが候補QA不合格→HR(DEVIATION_NATURAL)。Y-Std-4b / Y-Adv-4bで意図シナリオを取得。
7. **E-STOP**: Y-Std-6。待機40秒時点でrun専用`<run>/STOP`を設置→runnerが待機中の5秒刻み確認で`FamilyZStopSentinel`を送出→**TTS 2回で停止・③未実行・結果ファイル未保存(Assemble不可)・BlockProgress=IN_PROGRESS(resume可)・HRQ 0**。全run共通のSTOP/STOP_ALLは作成していない。
8. **E-N**: Y-Std-5、Y-Adv-5(上書き0・TTS 1/clip・待機0)。

### 不具合の発見と是正(11-8: 委任範囲内の軽微修正)
- **Y generator decoratorの位置ずれ**(`er121_family_y_audio_01.py`): `@secondary_run_scope.with_secondary_run`と`@y_family_scope("b1b")`が`_register_y_stop_check`(helper)側に付き、`generate_y_b1_segments`本体が**scope外**になっていた(このためb1b生成がX/Y/Z統一flowの`unified_flow_active()`判定外=旧flowになりうる)。両decoratorを`generate_y_b1_segments`へ戻し(順序: `with_secondary_run`→`y_family_scope("b1b")`→`family_scope("Y")`)。回帰test `er121_y_generator_decorator_test_01.py`(2件)を追加。evidence実走中に発見したため、修正後に全Y caseを新run dirで実走(旧dirは`*_aborted*`へ退避、費用計上のみ)。

### 未観測
- Y-Std/Y-AdvのE-S3(LRなし終端): Lean計画に無し(同leaf・同共通核はX/Zで実走)。
- Y chunk経路(`only_segments_scope`のchunk化): 本委任のY caseは短文+body 1 segment。chunk分割のLR/resumeは共通核のoffline test側で固定。
