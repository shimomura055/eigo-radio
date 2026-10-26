# -*- coding: utf-8 -*-
notes = {}
notes["X"] = """
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
"""
notes["Y"] = """
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
"""
notes["Z"] = """
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
"""
