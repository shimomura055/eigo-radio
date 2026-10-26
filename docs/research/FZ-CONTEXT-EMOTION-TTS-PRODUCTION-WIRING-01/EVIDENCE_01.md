# EVIDENCE_01 — FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_03 Phase 2 runtime evidence(2026-10-26)

**到達Status=EVIDENCE_COLLECTED(Fable照合待ち)。PRODUCTION_WIREDとは書かない。** 全6ケース(E-4はStd/Adv両方)で期待動作を観測、FAILは0件。
ただし**計画からの逸脱4件**(§5)があるため、Fableが逸脱の許容可否を判断すること。

## 0. 実行条件(共通)

- 正式runner `er026_family_z_fiction_production_runner_01.main()` を driver `er122_fzcw_runtime_evidence_01.py` から同一processで起動。`TTS_EXECUTION_MODE=STANDARD`。`.venv\Scripts\python.exe`。pages/page_verify stage不使用。公開dir・既存run(`run_sf_prod_01`等)は不変。
- **作品=melos(『走れメロス』)**。計画の猿の手ではない(理由=§5 D-1)。text資産は`melos/run_p2_evidence_r3`(seed sha一致の完成run)の許可リストcopy(`copy_reusable_run_assets`)+`<level>/key_phrases/keywords_canonicalized.json`+`study_text/`(非SUPERSEDED)。**音声・tts結果・audit・HR状態は一切持ち込まず、全dialogue clipを新規TTS生成**(REUSE_DENY、新規run dir)。
- run dir(全て`er026_output/family_z_production_e2e_01/melos/`配下): E-1=`run_fzcw_e1_01`(Std+Adv同一run)、E-2=`run_fzcw_e2_{a2,b1b}_01`、E-3=`run_fzcw_e3_a2_01`、E-4=`run_fzcw_e4_{a2,b1b}_01`、E-5=`run_fzcw_e5_a2_01`、E-6=`run_fzcw_e6_b1b_01`。
- 用語: a2=Standard、b1b=Advanced。強制NGは`repetition QA gate`(E-2〜E-5)または`減速後統一judge再検証`(E-6のみ)の戻り値をNG方向(verified True→False)にのみ上書き(driver既定、NG→OK方向なし)。上書きが無いattemptは完全に本物の判定。
- 並行実行: E-1が走る間にE-6/E-2/E-4/E-5/E-3を別run dirで並列起動(起動間隔150秒以上を維持、起動時刻は各run dirの`run_launch_log.jsonl`)。並行Y Voice Trialが同一TTS backendを使用していたが、**技術失敗(429/5xx/`technical_failure`)は0件**。minimal_fallback件数=0。
- 費用=合計 約¥40.3(COST_01.md)。Cap200に対し約20%。見積(期待49/保守62/天井80)以内。

## 1. 結論表(ケース×レベル)

出典=`evidence_01.json`、`RUNTIME_EVIDENCE_*.json`、各run `<lv>/audit/dialogue_ctx_attempt_state.json`。

| case | level | path | 期待動作 | 観測 | 判定 |
|---|---|---|---|---|---|
| E-1 | Std(a2) | normal(注入0) | 全dialogue TTS promptにCONTEXT含有・notes保存・attempt1でPASS・policy=fz_ctx_v1 | dialogue 10 clip全てmode=ctx、`dialogue_ctx_notes.json`保存(gpt-6-luna、¥0.119)、`dialogue_tts_policy.json`=fz_ctx_v1。attempt1 PASSは**9/10**。`full_story_part3_c10`のattempt1は**自然発生NG**(ASR=PASS、repetition QAのmethod_d'短lag flag。注入ではない)→attempt2(ctx・待機0)でPASS。ctx prompt実送信=10 clip+retry1=11件(CONTEXT marker有) | PASS(注1) |
| E-1 | Adv(b1b) | normal(注入0) | 同上 | dialogue 11 clip全てmode=ctx・attempt1でPASS 11/11、notes保存(¥0.149)、fz_ctx_v1。ctx prompt送信=11件 | PASS |
| E-1 | 共通 | normal | 注入0 | `injected_override_count=0`、`forced_ng_injection=false`、rep/post wrapperを入れない構造(driver)。rc=0。非dialogue 56 TTS requestはCONTEXT marker 0。`gate_result_04C.shared_gate=PASS`(a2/b1b)・assemble成功 | PASS |
| E-2 | Std | forced_ng_fallback | n1,n2=ctx(待機0)、cooldown実測>=600s、n3は従来方式(CONTEXT/話者/前後セリフ/manner 0)、PASS時mode=legacy_fallback | n1 15:47:21-34(ctx,強制NG)→n2 15:47:34-43(ctx,強制NG,待機0)→cooldown 15:47:43-15:57:43(通算600.001s)→n3 15:57:43-54 legacy_fallback PASS(verified=True)。n3 promptのsha256が従来builder出力(`build_tts_prompt(text, ENGLISH_STYLE_PREFIX)`)とバイト一致(`legacy_prompt_check_01.json`)、CONTEXT marker無。TTS総3回 | PASS |
| E-2 | Adv | forced_ng_fallback | 同上 | n1 15:39:32-45→n2 15:39:45-55(待機0)→cooldown 15:39:55-15:49:55(600.001s)→n3 15:49:55-15:50:05 legacy_fallback PASS。n3 promptはlegacy builderとバイト一致。TTS総3回 | PASS |
| E-3 | Std | forced_ng_resume | cooldown中kill→再起動で再開、n1・n2を再実行しない(TTS呼出増0)、cooldown残りのみ待機、総10分未満にならない、3回上限内 | n1,n2強制NG後、cooldown開始15:55:37の30秒後(15:56:07)に自起動PID(35868)を`os._exit(137)`。再開(15:58:50起動)は**TTS 1回のみ(n3)**。cooldown `resumed=true,process_starts=2,waited_seconds_this_process=403.41,total_elapsed_since_ref_seconds=600.0`。n3 16:05:37-50 legacy_fallback PASS。TTS総3回(kill前2+再開後1)。n3 promptはlegacy builderとバイト一致 | PASS |
| E-4 | Std | forced_ng_exhaust | 3回強制NG→総TTS3回(4回目なし)・STOPPED→HR Lock・最終成果物=STOP。ASR由来HR queue行を期待に含めない | n1 15:52:34-45→n2 15:52:45-55(ctx)→cooldown 600.002s→n3 16:02:55-16:03:10 legacy_fallback(強制NG)。TTS総3回(cost_log=3、4回目なし)。`review_lock_state`=HUMAN_REVIEW_REQUIRED(cumulative_tts_attempts=3)、clip state=TERMINAL_NG、runner rc=2=`FamilyZTtsClipFailedStop(FAMILY_Z_TTS_CLIPS_NOT_OK(a2): full_story_part1_c2=STOPPED)`。HR queue(er006/er007)への追記0。run dirにSTOP sentinelファイルは生成されない(stage例外のSTOP。runnerの既存仕様) | PASS |
| E-4 | Adv | forced_ng_exhaust | 同上 | n1 15:42:05-17→n2 15:42:17-27→cooldown 600.002s→n3 15:52:27-36 legacy_fallback(強制NG)。TTS総3回、HUMAN_REVIEW_REQUIRED、TERMINAL_NG、rc=2 FamilyZTtsClipFailedStop(b1b)。HR queue追記0 | PASS |
| E-5 | Std | forced_ng_first_only | n1のみ強制NG→kill→再開でn2はctx即時PASS(待機0)・TTS総2回・再開でn1重複なし | n1 15:44:48-59 ctx強制NG→n1のstate永続化直後(15:44:59)に自起動PIDを`os._exit(137)`。再開(15:49:31起動)はn2 15:49:37-48 ctx PASS(cooldown=None=待機0)。TTS総2回(kill前1+再開後1、cost_log=2)。n1再実行0 | PASS |
| E-6 | Adv | forced_ng_adv_post_slowdown | 減速後判定でn1をNG→外側ループ継続・通算n2もctx・二重計上なし・総3回上限 | 注入=`post`ordinal1(減速後再検証)の1件のみ。n1 15:36:39-52(ctx,減速後NG,`final_ng_epoch`記録)→n2 15:36:54-15:37:06(ctx,待機0)でPASS。TTS総2回(両方CONTEXT有)、`post_slowdown_calls=2`。3回上限内、HR/STOPなし | PASS |
| 全6ケース | 両 | — | ASR表記違いのみ理由の再生成0・費用が見積内 | 強制NG由来以外の再生成はE-1 a2 part3_c10の1件(repetition QA、ASR表記由来ではない)のみ。ASR表記違い理由の再生成0。合計約¥40.3 | PASS |

注1: 計画E-1の「attempt1でPASS」に対し、a2の1/10 clipは自然発生のrepetition QA NGでattempt2のctxでPASS(2回上限内・待機0)。注入ではなく、通常発生するretryがctx方式で想定どおり動いた**追加の正常経路証拠**。計画文言の厳密適用ではattempt1 PASS 20/21。

## 2. E-1 正常経路の詳細(ctx方式の実発火証拠)

- 実送信prompt: ctx prompt 22件(Std 11・Adv 11=dialogue 21 clip+natural retry 1)がCONTEXT FOR THIS ONE LINE marker有。非dialogue 56件はmarker無。TTS request計78件。
- dialogue clipのTTS model=`gemini-2.5-pro-preview-tts`(従来から同一。ctxでmodel変更なし、cost_log)。非dialogue=`gemini-3.8-flash-lite-tts`。
- 各clipのctx style sha256(先頭12桁)は下表。clipごとに固有=前後文脈由来のnotesが実際にpromptへ入っている。
- 組立: Std `headroom.scalar=1.0`(applied=false, peak_before=0.9505)、Adv `headroom.scalar=1.0`(applied=false, peak_before=0.95)。`gate_result_04C.shared_gate=PASS`。最終音声: `er026_output/family_z_production_e2e_01/melos/run_fzcw_e1_01/a2/assembly/Family_Z_melos_a2.wav`、`.../b1b/assembly/Family_Z_melos_b1b.wav`(+`timeline.json`)。
- Adv減速後処理: b1b dialogue wavに`_original.wav`が付く(Z速度v2のAdv約6%高速化=既存挙動)。
- notes LLM(`dialogue_ctx_notes.json`): Std accepted 8 / no_explicit_cue 2 / discarded 0、Adv accepted 5 / no_explicit_cue 6 / discarded 0。

### E-1 clipごと(path=normal)

| level | clip | attempt数 | mode列 | verified列 | ASR判定 | ctx style sha256(先頭12) | instruction_type |
|---|---|---|---|---|---|---|---|
| a2 | full_story_part1_c2 | 1 | ctx | True | PASS | 97aa6a5091f4 | english_style_prefix_wide_margin |
| a2 | full_story_part1_c4 | 1 | ctx | True | PASS | 87a276e7b9dd | english_style_prefix_wide_margin |
| a2 | full_story_part1_c6 | 1 | ctx | True | PASS | e86b5b441e38 | english_style_prefix_wide_margin |
| a2 | full_story_part1_c8 | 1 | ctx | True | PASS | dd3e7b082999 | english_style_prefix_wide_margin |
| a2 | full_story_part1_c10 | 1 | ctx | True | PASS | ce16c7350e65 | english_style_prefix_wide_margin |
| a2 | full_story_part3_c2 | 1 | ctx | True | PASS | 4e5dab3e89ab | english_style_prefix_wide_margin |
| a2 | full_story_part3_c4 | 1 | ctx | True | PASS | e7b3cd1ec13e | english_style_prefix_wide_margin |
| a2 | full_story_part3_c6 | 1 | ctx | True | PASS | 03223d2811d2 | english_style_prefix_wide_margin |
| a2 | full_story_part3_c8 | 1 | ctx | True | PASS | 2240bd36ba91 | english_style_prefix_wide_margin |
| a2 | full_story_part3_c10 | 2 | ctx/ctx | False/True | PASS/PASS | 7741795fbdea | english_style_prefix_wide_margin |
| b1b | full_story_part1_c2 | 1 | ctx | True | PASS | e7b368285dce | english_style_prefix_wide_margin |
| b1b | full_story_part1_c4 | 1 | ctx | True | PASS | cd6b290a8ce3 | english_style_prefix_wide_margin |
| b1b | full_story_part1_c6 | 1 | ctx | True | PASS | da4ad7d99241 | english_style_prefix_wide_margin |
| b1b | full_story_part1_c8 | 1 | ctx | True | PASS | c86528e9ff93 | english_style_prefix_wide_margin |
| b1b | full_story_part1_c10 | 1 | ctx | True | PASS | 3ebbda23e09c | english_style_prefix_wide_margin |
| b1b | full_story_part3_c2 | 1 | ctx | True | PASS | e82ea91eda67 | english_style_prefix_wide_margin |
| b1b | full_story_part3_c4 | 1 | ctx | True | PASS | 2dab98ee8b30 | english_style_prefix_wide_margin |
| b1b | full_story_part3_c6 | 1 | ctx | True | PASS | cb27311700ce | english_style_prefix_wide_margin |
| b1b | full_story_part3_c8 | 1 | ctx | True | PASS | f4d9b38df2e6 | english_style_prefix_wide_margin |
| b1b | full_story_part3_c10 | 1 | ctx | True | PASS | 3537fb92d2ae | english_style_prefix_wide_margin |
| b1b | full_story_part3_c12 | 1 | ctx | True | PASS | 85c4ec4634bc | english_style_prefix_wide_margin |

### E-2〜E-6 attempt表

| run | case | level | n | mode | effective_mode | verified | ASR判定 | 開始 | 終了 | final_ng_epoch有 |
|---|---|---|---|---|---|---|---|---|---|---|
| run_fzcw_e2_a2_01 | E-2 | a2 | 1 | ctx | ctx | False | PASS | 2026-10-26T15:47:21 | 2026-10-26T15:47:34 | False |
| run_fzcw_e2_a2_01 | E-2 | a2 | 2 | ctx | ctx | False | PASS | 2026-10-26T15:47:34 | 2026-10-26T15:47:43 | False |
| run_fzcw_e2_a2_01 | E-2 | a2 | 3 | legacy_fallback | legacy_fallback | True | PASS | 2026-10-26T15:57:43 | 2026-10-26T15:57:54 | False |
| run_fzcw_e2_b1b_01 | E-2 | b1b | 1 | ctx | ctx | False | PASS | 2026-10-26T15:39:32 | 2026-10-26T15:39:45 | False |
| run_fzcw_e2_b1b_01 | E-2 | b1b | 2 | ctx | ctx | False | PASS | 2026-10-26T15:39:45 | 2026-10-26T15:39:55 | False |
| run_fzcw_e2_b1b_01 | E-2 | b1b | 3 | legacy_fallback | legacy_fallback | True | PASS | 2026-10-26T15:49:55 | 2026-10-26T15:50:05 | False |
| run_fzcw_e3_a2_01 | E-3 | a2 | 1 | ctx | ctx | False | PASS_WITH_WARNING | 2026-10-26T15:55:14 | 2026-10-26T15:55:28 | False |
| run_fzcw_e3_a2_01 | E-3 | a2 | 2 | ctx | ctx | False | PASS | 2026-10-26T15:55:28 | 2026-10-26T15:55:37 | False |
| run_fzcw_e3_a2_01 | E-3 | a2 | 3 | legacy_fallback | legacy_fallback | True | PASS | 2026-10-26T16:05:37 | 2026-10-26T16:05:50 | False |
| run_fzcw_e4_a2_01 | E-4 | a2 | 1 | ctx | ctx | False | PASS | 2026-10-26T15:52:34 | 2026-10-26T15:52:45 | False |
| run_fzcw_e4_a2_01 | E-4 | a2 | 2 | ctx | ctx | False | PASS | 2026-10-26T15:52:45 | 2026-10-26T15:52:55 | False |
| run_fzcw_e4_a2_01 | E-4 | a2 | 3 | legacy_fallback | legacy_fallback | False | PASS | 2026-10-26T16:02:55 | 2026-10-26T16:03:10 | False |
| run_fzcw_e4_b1b_01 | E-4 | b1b | 1 | ctx | ctx | False | PASS | 2026-10-26T15:42:05 | 2026-10-26T15:42:17 | False |
| run_fzcw_e4_b1b_01 | E-4 | b1b | 2 | ctx | ctx | False | PASS | 2026-10-26T15:42:17 | 2026-10-26T15:42:27 | False |
| run_fzcw_e4_b1b_01 | E-4 | b1b | 3 | legacy_fallback | legacy_fallback | False | PASS | 2026-10-26T15:52:27 | 2026-10-26T15:52:36 | False |
| run_fzcw_e5_a2_01 | E-5 | a2 | 1 | ctx | ctx | False | PASS | 2026-10-26T15:44:48 | 2026-10-26T15:44:59 | False |
| run_fzcw_e5_a2_01 | E-5 | a2 | 2 | ctx | ctx | True | PASS | 2026-10-26T15:49:37 | 2026-10-26T15:49:48 | False |
| run_fzcw_e6_b1b_01 | E-6 | b1b | 1 | ctx | ctx | True | PASS | 2026-10-26T15:36:39 | 2026-10-26T15:36:52 | True |
| run_fzcw_e6_b1b_01 | E-6 | b1b | 2 | ctx | ctx | True | PASS | 2026-10-26T15:36:54 | 2026-10-26T15:37:06 | False |

## 3. 遷移表(cooldown実経過秒・再開復元・HR Lock/STOP)

| case | 起動 | cooldown起点(NG確定) | 待機した秒(各process) | 通算経過秒 | 終了時の状態 |
|---|---|---|---|---|---|
| E-2 Std | 1起動 | 15:47:43 | 599.981 | 600.001 | n3 PASS legacy_fallback、lock RESOLVED |
| E-2 Adv | 1起動 | 15:39:55 | 599.972 | 600.001 | 同上 |
| E-3 Std | 起動1(kill)→起動2(再開) | 15:55:37 | 起動1=30.0(kill) / 起動2=403.41 | **600.0**(resumed=true, process_starts=2) | n3 PASS legacy_fallback |
| E-4 Std | 1起動 | 15:52:55 | 599.976 | 600.002 | n3強制NG→TERMINAL_NG→HUMAN_REVIEW_REQUIRED→rc=2 STOP |
| E-4 Adv | 1起動 | 15:42:27 | 599.978 | 600.002 | 同上 |
| E-5 Std | 起動1(kill)→起動2(再開) | なし(ctx→ctxは待機0) | 0 | — | n2 ctx PASS、RESOLVED |
| E-6 Adv | 1起動 | なし | 0 | — | n2 ctx PASS、RESOLVED |

- 再開時の復元内容: E-3は`dialogue_ctx_attempt_state.json`から`n_started=2`とcooldown起点(`ref_epoch`)を復元し、(1)n1・n2を再実行せず(再開process内TTS request=1件=n3のみ)、(2)残り分(403.41秒)のみ待機して通算600.0秒、(3)n1・n2のctx style sha256はstate保持のまま。E-5は`n_started=1`とn1のstate(`verified=False, finished=true`)を復元し、n2を待機0で開始。
- 4回目: E-4でTTS呼出3回(cost_log `gemini-2.5-pro-preview-tts` 3件)。4回目なし。
- HR Lock/STOP: E-4 Std/Adv共に`review_lock_state.json`=`HUMAN_REVIEW_REQUIRED`、reasonは「最終status=STOPPED。…通算3回の試行でASR検証に合格しませんでした」。runnerのSTOPは`FamilyZTtsClipFailedStop`(rc=2、`--only-clips`での人手再実行案内)。**run dirにSTOP/STOP_ALL sentinelファイルは作られない**(`ls`で確認)。解除操作は一切していない。lockはrun dir限定(`run_fzcw_e4_a2_01`/`run_fzcw_e4_b1b_01`)で、共有HR queue(er006/er007)への自runの追記は0(SHARED_LEDGER_01.md)。

## 4. 各attempt表の読み方

`verified`はpolicyが記録した最終判定。強制NGは`verified=False`でASR判定は`PASS`(repetition QA段階の上書き。Opus M-10(d)どおりASR由来HRなし)。E-3のn1は実ASRが`PASS_WITH_WARNING`(強制NG前の本物の判定)。E-6 n1の`verified=True`は減速前の判定で、`final_ng_epoch`が減速後NG(注入)の確定時刻を保持している(`final_ng_epoch有=True`の列)。

## 5. 逸脱履歴(EVIDENCE_PLAN_02からの変更。同内容をEVIDENCE_PLAN_02.md末尾にも追記)

- **D-1 作品を猿の手→melosに変更**: 猿の手のseed.json(`seed_sha256 8f76316068e7`)は2026-10-25 commit 53ce7b397(5作品Seed補完)で更新済みで、既存`run_sf_prod_01`/`run_kpgm35_01`の`writer/provenance.json`(`8f1128b925c8`)と不一致。`FamilyZProvenanceMismatchStop`で課金前にSTOP(API 0)。猿の手のtext資産を新規run用に得るにはwriter/std_adjust/plan/support/kpの再生成(過去実績の約¥21+KP Human Review待機が必要)が要る。seed shaが現行一致する完成run(`melos/run_p2_evidence_r3`、Part1/Part2/KP有)のtext資産を許可リストcopyし、**全dialogue TTSは新規生成**した。dialogue方式の発火・遷移の証拠価値は作品非依存。melosはmelos/king/friend等の複数話者を含む(dialogue_attribution)。猿の手固有のctx品質確認は未実施。
- **D-2 driver bug修正(Production経路は不変)**: (a) TTS prompt捕捉wrapperが`prompt`が非str(tuple)の経路で`.encode`に失敗(E-1初回、API 0で停止)→記録用にstr化(送信promptは不変)。(b) 再開起動(新process)で強制NGのordinalが1に戻り再注入される欠陥→`--ordinal-offset N`を追加(再開後のordinalを消費済みattempt数から数える)。testを1件追加し20 PASS。**再開起動commandは「同一args」ではなく、killフラグを外して`--ordinal-offset`を付けた**(E-3=`--ordinal-offset 2`、E-5=`--ordinal-offset 1`)。killフラグを残すと再開直後に自己killする/強制NGが再注入されるため。
- **D-3 起動回数とRESTART_STORM**: 準備段階で課金前に落ちる起動(API 0、rc=2)を重ね、猿の手`run_fzcw_e1_01`でrunnerの`RESTART_STORM`(5分内3起動、`STOP`+`RESTART_STORM_LOCK.json`)を発動させた。**`the_monkeys_paw/run_fzcw_e1_01/STOP`は解除していない(Fable権限)。run dir限定で他runに影響しない**。以降はmelosの別run dirで、同一run dirの5分内起動を2回以下に抑えた(各run dirの`run_launch_log.jsonl`で確認可)。猿の手`run_fzcw_e1_02`(API 0、空の準備dir)も残置。
- **D-4 `--budget-jpy`**: E-1=60(計画値。委任文形式例の40ではなく計画値)、他=15。実費は全て上限内。
- **D-5 melos E-1のtext資産準備**: `study_text/`と`<lv>/key_phrases/keywords_canonicalized.json`は`copy_reusable_run_assets`の許可リスト外のため追加copy(text資産のみ。runnerが要求したため。音声・状態は含まず)。

## 6. 判定材料(Fable向け。PRODUCTION_WIRED判定はFable)

- 充足: ユーザー受入表6ケース(正常/強制NG fallback/resume/exhaust/Adv外側ループ)のStd・Adv実発火、正式初回生成・retry・fallback・resume・QA・実音声・費用の実測。Mock無し(実TTS/実ASR/実Gate)。
- 不足/要判断: (a)作品がmelos(猿の手でない、D-1)。(b)E-4のSTOP形態=stage例外(rc=2)とHR Lock(sentinel無し)で、計画の「最終成果物=STOP」の文言と一致するかFable確認。(c)Adv既定でminimal_fallbackは発生せず(0件)、M-3(i)の併発シナリオ(Advのminimal_fallback併発)は未観測=設計上の安全側STOPのまま。(d)実音声の聴取評価(ctx音声が従来より自然か)は本委任の範囲外(自動QAのみ)。(e)J-1(LR未配線)はE-4が示す現行動作どおり3回NG→人手HR。
