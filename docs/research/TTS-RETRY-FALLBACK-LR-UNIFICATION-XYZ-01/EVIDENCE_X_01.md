# EVIDENCE_X_01 — Family X runtime evidence(委任_03)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: 2026-10-27 00:45 JST / API実費を伴う実走evidence(実TTS・実ASR・実180秒待機・実LR[gpt-6-luna]・実Gate)

## 方式(全Family共通)

- driver: `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_run_01.py`(+`tru_ev_core_01.py`/`tru_ev_cases_01.py`/`tru_ev_aggregate_01.py`)。**正式のleaf生成関数・scope(`er109 run_scope`/`with_secondary_run`/`guarded_generate`)を直接呼ぶ**。実TTS・実ASR・実180秒`time.sleep`(`cooldown_core`)・実LR・実Gateは本物のまま。
- 強制NG: driver側monkeypatchで**判定結果のNG方向にだけ**上書き(Style・Prompt・Voice・速度・model・待機・回数・Gateは触らない)。上書きは`injected_override_count`と`injected_overrides[]`に全件記録。LR経路はPrimary転写の1語置換(NG方向のみ)で`identify_ng_span`を成立させた。正常系(E-N)は上書き0をassert。
- 環境: `TTS_EXECUTION_MODE=STANDARD`を環境変数とCLI引数の両方で明示。`TTS_BACKEND=speech_metadata_flash_lite` / `STYLE_PROFILE=fx_20261017`(X/Y/Z共通の承認済み)。
- 各case開始前に`tools/stop_scope_check_01.py --managed-id TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01`を実行(63ファイル`stop_check_*.json`、いずれもrc=3[停止]でない)。STOP/STOP_ALLは作成・削除していない(E-STOPはrun専用sentinel `<run>/STOP`のみ)。
- 強制NG由来のHRQ行・attempt_history・Master Audio Store・telemetryは各run dirの`_evidence_ledgers/`へ隔離(本番台帳を汚さない)。evidence専用・対応不要・開発費。
- 判定: `_aggregate_01.json`(case別の機械判定[check名・期待・実測])。PASS=期待どおり/DEVIATION_NATURAL=③等で本物のASRが自然にNGになり期待と異なる経路(フロー自体の検査は通過)/FAIL=不整合。
- 表の読み方: TTS=対象clipの実TTS回数、待機=実測秒(`+`区切り、E-S6はkill前+再開後)、Style列=attempt毎のStyle種別(A=元Style、B=Fallback Style、`[..]`=該当ラベル)、方針Gate=M3(X)/Y Style Gate/Z該当/Gate(当該segmentのみ。未生成の他segmentのNO_SEGMENT_RECORDは対象外)、共有Audio Gate=`asm._segment_gate_status`等のper-segment関数を当該segmentにだけ適用(API 0)。

## Xの判定集計

DEVIATION_NATURAL=3, PASS=26(case数=29。supersededは含まない)

## 方針×シナリオの観測マトリクス(X)

未観測=本委任で実走していない(Lean計画で除外/代表で固定)。

| 方針/Lv | E-N | E-S0 | E-S1 | E-S2a | E-S2b | E-S3 | E-S4 | E-S6 | E-S7 | E-C1 | E-X5 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EN_LR_ADV/b1b | X-Adv-13[PASS] | X-Adv-15[PASS] | X-Adv-1[PASS], X-Adv-14[DEVI], X-Adv-14b[PASS] | X-Adv-2[PASS] | X-Adv-3c[PASS], X-Adv-6[PASS] | 未観測 | 未観測 | X-Adv-12[PASS], X-Adv-16[PASS] | X-Adv-4[PASS] | 未観測 | 未観測 |
| EN_LR_STD/a2 | X-Std-11[PASS] | 未観測 | X-Std-1[DEVI], X-Std-1b[PASS], X-Std-4[PASS] | X-Std-2[PASS] | X-Std-3[PASS], X-Std-5[PASS] | 未観測 | 未観測 | X-Std-10[DEVI] | 未観測 | X-Std-12[PASS] | 未観測 |
| JA_STD/a2 | 未観測 | 未観測 | X-Std-6[PASS] | 未観測 | 未観測 | X-Std-7[PASS] | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 |
| KP_EN/a2 | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 | X-Std-8[PASS], X-Std-9[PASS] | 未観測 | 未観測 | 未観測 | 未観測 |
| KP_EN/b1b | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 | 未観測 | X-Adv-10[PASS], X-Adv-11[PASS] | 未観測 | 未観測 | 未観測 | 未観測 |
| KP_EXPL/b1b | 未観測 | 未観測 | X-Adv-7[PASS] | 未観測 | 未観測 | X-Adv-8[PASS] | 未観測 | 未観測 | 未観測 | 未観測 | X-Adv-9[PASS] |

## case別観測表(X)

| case | Lv | 方針/leaf | シナリオ | TTS | 待機(秒) | LR | HRQ行 | Style列 | 最終 | 方針Gate(M3/Y/Z、当該seg) | 共有Audio Gate(Assemble、当該seg) | 判定 | 実費(円) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X-Adv-1 | b1b | EN_LR_ADV/L1 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.759 |
| X-Adv-2 | b1b | EN_LR_ADV/L1 | E-S2a | 4 | 180 | 1 | 0 | AABA | OK | BLOCKなし | PASS | PASS | 1.304 |
| X-Adv-3c | b1b | EN_LR_ADV/L1 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(comment_1=STOPPED) | PASS | 2.021 |
| X-Adv-4 | b1b | EN_LR_ADV/L1 | E-S7 | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCKなし | BLOCK(comment_1=STOPPED) | PASS | 0.973 |
| X-Adv-6 | b1b | EN_LR_ADV/L2 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(in_one_line=STOPPED) | PASS | 1.789 |
| X-Adv-7 | b1b | KP_EXPL/L5 | E-S1 | 3 | 180 | 0 | 0 | A,A,B[MINIMAL_INSTRUCTION_PREFIX] | OK | BLOCK(kp1_explanation:FINAL_STYLE_SHA_MISMATCH_NO_HINT) | PASS | PASS | 0.684 |
| X-Adv-8 | b1b | KP_EXPL/L5 | E-S3 | 3 | 180 | 0 | 1 | A,A,B[MINIMAL_INSTRUCTION_PREFIX] | STOPPED | BLOCK(kp1_explanation:KP_EXPLANATION_STATUS_NOT_OK+FINAL_STYLE_SHA_MISMATCH_NO_HINT) | BLOCK(kp1_explanation=STOPPED) | PASS | 0.695 |
| X-Adv-9 | b1b | KP_EXPL/L5 | E-X5 | 1 | - | 0 | 0 | A[MINIMAL_INSTRUCTION_PREFIX] | OK | BLOCK(kp1_explanation:STYLE_BASE_SHA_MISMATCH_OR_MISSING+FINAL_STYLE_SHA_MISMATCH_NO_HINT) | PASS | PASS | 0.413 |
| X-Adv-10 | b1b | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | BLOCKなし WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | PASS | PASS | 0.324 |
| X-Adv-11 | b1b | KP_EN/L6 | E-S4 | 4 | 180 | 0 | 1 | A,A,B[ENGLISH_LOCK],B[ENGLISH_LOCK] | STOPPED | BLOCK(kp1_english:KP_EN_STATUS_NOT_OK) WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | BLOCK(kp1_english=STOPPED) | PASS | 0.414 |
| X-Adv-12 | b1b | EN_LR_ADV/L1 | E-S6 | 3 | 60+0 | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.746 |
| X-Adv-13 | b1b | EN_LR_ADV/L1 | E-N | 1 | - | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.36 |
| X-Adv-14 | b1b | EN_LR_ADV/L1 | E-S1(Opus4-c b: Voice=Charon) | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCK(preview:FINAL_STYLE_RECORD_MISSING+PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED) | BLOCK(preview=STOPPED) | DEVIATION_NATURAL | 1.607 |
| X-Adv-14b | b1b | EN_LR_ADV/L1 | E-S1(Opus4-c b: Voice=Charon・再実行) | 3 | 180 | 0 | 0 | AAB | OK | BLOCK(preview:FINAL_STYLE_SHA_MISMATCH_NO_HINT+PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED+PREVIEW_MINIMAL_FALLBACK) | PASS | PASS | 1.672 |
| X-Adv-15 | b1b | EN_LR_ADV/L1 | E-S0(②PASS・待機なし) | 2 | - | 0 | 0 | AA | OK | BLOCKなし | PASS | PASS | 0.343 |
| X-Adv-16 | b1b | EN_LR_ADV/L2 | E-S6(R-5: LR block内kill) | 6 | 255+12 | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 1.851 |
| X-Std-1 | a2 | EN_LR_STD/L3 | E-S1 | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCKなし | BLOCK(topic_intro=STOPPED) | DEVIATION_NATURAL | 0.767 |
| X-Std-1b | a2 | EN_LR_STD/L3 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.471 |
| X-Std-2 | a2 | EN_LR_STD/L3 | E-S2a | 4 | 180 | 1 | 0 | AABA | OK | BLOCKなし | PASS | PASS | 1.142 |
| X-Std-3 | a2 | EN_LR_STD/L3 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(topic_intro=STOPPED) | PASS | 2.203 |
| X-Std-4 | a2 | EN_LR_STD/L4 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.804 |
| X-Std-5 | a2 | EN_LR_STD/L4 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(in_one_line=STOPPED) | PASS | 1.868 |
| X-Std-6 | a2 | JA_STD/L7 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.238 |
| X-Std-7 | a2 | JA_STD/L7 | E-S3 | 3 | 180 | 0 | 0 | AAB | STOPPED | BLOCKなし | BLOCK(japanese_title=STOPPED) | PASS | 0.237 |
| X-Std-8 | a2 | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | BLOCKなし WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | PASS | PASS | 0.393 |
| X-Std-9 | a2 | KP_EN/L6 | E-S4 | 4 | 180 | 0 | 1 | A,A,B[ENGLISH_LOCK],B[ENGLISH_LOCK] | STOPPED | BLOCK(kp1_english:KP_EN_STATUS_NOT_OK) WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | BLOCK(kp1_english=STOPPED) | PASS | 0.523 |
| X-Std-10 | a2 | EN_LR_STD/L3 | E-S6 | 3 | 60+30 | 1 | 1 | A | STOPPED | BLOCKなし | BLOCK(topic_intro=STOPPED) | DEVIATION_NATURAL | 0.744 |
| X-Std-11 | a2 | EN_LR_STD+JA_STD/L3+L7 | E-N | 1 | - | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.265 |
| X-Std-12 | a2 | EN_LR_STD/L4 | E-C1(Opus4-c a) | 2 | - | 0 | 0 | AA | OK | BLOCKなし 減速Gate当該chunk違反なし | PASS | PASS | 1.175 |

## 実測モデル(raw_usage_log。Xのrun dir合算)

| provider | model_id(実測) | API | 呼出回数 |
|---|---|---|---|
| azure | azure-speech-stt | get_full_text_via_azure_stt_with_phrase_list | 39 |
| gemini | gemini-3.8-flash-lite-tts | models.generate_content(TTS) | 102 |
| openai | gpt-6-luna | responses.create | 36 |
| openai_asr | gpt-4o-mini-transcribe | audio.transcriptions.create | 106 |

## 達成状況と主要観測(X: er019、Std=a2 / Adv=b1b)

1. **E-S1(①②同Style→実180秒→③Fallback Style)**: X-Std-1b(topic_intro: ①②=`brief, clear, engaging news topic...`[96字]→③=`natural, clear, conversational`[30字])、X-Std-4(body_s[減速対象]: ③も30字)、X-Adv-1(comment_1 Charon: ①②=`calm, conversational`[20字]→③=30字)、X-Std-6(JA: ①②=65字→③=`次の文章だけを、...`[60字])。実待機は`cooldown_core`の実`sleep`で179.972〜180.000秒。Voice・model(`gemini-3.8-flash-lite-tts`)は全attemptで同一(X-Adv系はCharon、Std/他はAoede)。
2. **E-S2a(③NG→LR 1回→LR block①'実PASS)**: X-Std-2、X-Adv-2。実LR(`gpt-6-luna`)が書換え→④(=①')は**元role Style**(Adv=`calm, conversational`、Std=①②のStyle)で再TTS→PASS。TTS=4、待機1回、HRQ 0。
3. **E-S2b(①〜⑥全NG→HR)**: X-Std-3、X-Std-5、X-Adv-6、X-Adv-3c。TTS=6(**それ以上なし**)、待機2回(179.999秒×2)、LR=1(**再入0**)、①②④⑤=元Style・③⑥=Fallback Style、最終`STOPPED`、Lock=`HUMAN_REVIEW_REQUIRED`、**HRQ 1行**、共有Audio Gate=BLOCK(`STOPPED`)。
4. **E-S7(U-03: ASR一致+disfluency単独NG)**: X-Adv-4。①②→180秒→③を実行(TTS=3)、③NG後に**LR LLM呼出0・LR block 0**で即HR、HRQ 1行(`register_terminal_hr`)。
5. **E-S3(LRなし部位の③NG→HR)**: X-Std-7(JA)、X-Adv-8(KP解説)。TTS=3・待機1・LR=0・Lock=HUMAN_REVIEW_REQUIRED・共有Gate BLOCK。**HRQ行の限界**: X-Std-7(JA)は判定戻り値のNG注入のためJA ASR判定器自身が最終slotで書くHRQ行が出ない(driver側の限界、Lock/最終STOPPED/Gate BLOCKは観測済み)。X-Adv-8(KP解説)はHRQ 1行を観測。**OPEN候補**: `generate_a2_japanese_with_fallback`の終端(STOPPED)に`register_terminal_hr`呼出が無く、JAのHRQ行は判定器の最終slot書込に依存する(EN側・KP側は`register_terminal_hr`でjudge外終端も保証)。JAにjudge外の終端NG経路があるかは未確認=Fableへ報告(分類: 修正へ進む候補/実害は要確認)。
6. **E-S4(KP英語 2回+180秒+ENGLISH_LOCK 2回)**: X-Std-8・X-Adv-10(PASS: TTS=3、③=`ENGLISH_LOCK`、待機1)、X-Std-9・X-Adv-11(4回NG: TTS=4、HRQ 1行=slot4のみ、Gate BLOCK `KP_EN_STATUS_NOT_OK`)。③④採用時のGateはWARNING(`KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2`、非ブロッキング)のみ。
7. **E-X5(S-06: KP解説の短文Style適合性)**: X-Adv-9。既存3 explanation textを③と同じminimal Style(`Speak the following text aloud naturally...`)で1 take: ASR=3件ともNORMALIZED_MATCH・disfluency NGなし・追加TTS 0・待機0 → **`style_seq`縮退は不要**。X-Adv-7(E-S1): ①②=`Speak clearly at a slightly relaxed...`[136字]→③=minimal[129字]でPASS。
8. **E-S6(kill→resume)**: 自分が起動したPIDだけをdriver内の`os._exit`で終了(外部kill・image名killなし)。
   - X-Adv-12(待機60秒でself-kill): ①②のTTS=2をkill前に記録→同一argsで再起動(開始から約3分後)。**①②の再生成0**、③は1回のみ(TTS総数3)。再起動時点で起点から196秒経過=待機は壁時計基準で既に満了(残り0秒、`total_elapsed_since_ref`=196.0)。
   - X-Std-10(待機60秒でself-kill): 再起動時の**残り待機のみ29.5秒**(総経過180.001秒)、①②再生成0、③1回。③が実ASRで自然NG→LR→候補QA不合格→HR(最終STOPPED、判定=DEVIATION_NATURAL。resume機構の検査は全通過)。
   - X-Adv-16(**R-5: LR block内kill**): ①②③+LR+④⑤の5 TTSを完了後、LR blockの待機中(sleep_total=255秒)でself-kill→再起動。**①〜⑤の再生成0・LR再呼出0**、残り待機12.4秒(⑤NGから総経過180.001秒)、⑥(Fallback Style)1回、TTS総数6、attempt sidecar 6本(二重なし)、最終OK。
9. **E-N**: X-Std-11・X-Adv-13。上書き0・TTS 1/clip・待機0・LR 0。
10. **E-C1(Opus 4-c a: Std chunk「①減速後NG→②PASS→Gate PASS」)**: X-Std-12(chunk `full_story_part1_k1`)。①=減速後再検証NG(注入1回)→②PASS、待機0(③に入らない)、①②同Style。**Std chunk減速Gate: 当該chunkはviolationなし/M3 profile Gate: 当該chunkの誤BLOCKなし**。(Gate全体のBLOCKは未生成の他chunkの`STD_CHUNK_MISSING_MANDATORY_A2_SLOWDOWN`によるもので、本case対象外)
11. **Opus 4-c b(Adv L1 ③ Voice=Charon)**: X-Adv-14b(preview)および X-Adv-1/2/3c/4(comment_1)。全attemptで`Charon`、③のStyleのみ短文30字へ切替。**M3 Gate**: preview③採用=BLOCK(`PREVIEW_MINIMAL_FALLBACK`+`FINAL_STYLE_SHA_MISMATCH_NO_HINT`+`PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED`)=Adv preview③はGate対象でHR承認待ち。comment_1③(X-Adv-1)はBLOCKなし。KP解説③(X-Adv-7)はBLOCK(`FINAL_STYLE_SHA_MISMATCH_NO_HINT`)。

### 自然発生した逸脱と是正(隠さず記録)
- X-Std-1・X-Adv-14: ③が実ASRで自然にNG→実LR→「候補QA不合格」でHR(`HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA`)。期待(③PASS)と異なるが、LR=1・再入0・HRQ 1行・最終STOPPEDの終端処理は仕様どおり(判定=DEVIATION_NATURAL)。同条件の再実行 X-Std-1b(PASS)・X-Adv-14b(PASS)で意図シナリオを取得。
- X-Adv-3/3b(comment_1, E-S2b): 置換語を先頭語`Listen`にしたためLRが`NO_CANDIDATE_PASSED_QA`(命令文の書換え候補がQA不合格)でLR block不成立(TTS=3)。置換語を文中語`compares`に変更したX-Adv-3cでE-S2b成立。旧2本は`evidence_runs/_superseded/`へ移し、費用はCOST_01に計上。
- X-Adv-16(初回、comment_1): 同様にLR不成立で`_superseded/`へ。leafをL2(in_one_line)に変更して再実行し成立。
- X-Adv-7/8/10/11・X-Std-8/9: 初回は`xr._ONLY_SEGMENTS`のlabel不一致で実TTS 0のno-op、2回目は正式runner後処理の`style_profile`記録(M4/S3)をdriverが付けなかったためGateの`STYLE_BASE_SHA_MISMATCH_OR_MISSING`が出る**driver側の不備**。driverで正式runnerと同じ`attach_segment_profile_record`を付与して再実行(`_superseded/`に旧版を保存、費用計上)。

### 発見(Production code。修正せず報告)
- **BlockProgressのdepth別instance上書き**(`er127_tts_block_policy_01.py` `BlockProgress`/`BlockRun.finish`): depth 0とLR block(depth 1)が同一progress fileを別のin-memory stateで書くため、depth 0の`mark_done`が`blocks["1"]`(LR blockのattempt/待機記録)を上書き消去する(X-Adv-6/X-Std-3の最終progressは`blocks`に`"0"`のみ、X-Adv-16 resume後は`blocks["1"]`のattempt3・cooldownが欠落)。再開の正当性(②消費済み判定・待機基準)には影響しない(DONE後の監査記録のみ欠落)。分類: 修正へ進む(軽微。次委任でmark_doneを再読込・merge方式へ)。

### 未観測(本委任で実走していない)
- X-Adv-5(L2 in_one_line E-S1): Lean計画で★除外。同leafはX-Adv-6(E-S2b)で実走済み。
