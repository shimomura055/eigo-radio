# EVIDENCE_Z_01 — Z Standard(a2) Chunk TTS 正式runtime evidence

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03(2026-10-26)。到達上限=EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。使用model: TTS=`gemini-3.8-flash-lite-tts`(Production現行、`tts_backend=speech_metadata_flash_lite`)、ASR=既存Production(OpenAI transcribe + 統一judge)。最新モデル原則の対象外(評価ではなく既存Productionラインの動作確認)。

## 1. 実行
- 対象: melos(Family Z) Std(a2) `full_story_part2_c1`(narrator 134語)。run=`er026_output/family_z_production_e2e_01/melos/run_stdchunk_ev_01`(`run_fzcw_e1_01`のtext資産+同runの既存TTS cache[dialogue・shell・KP・comment]を複製。cost/launch/stage logは持ち込まず新規。元runは無変更。公開run・公開pageなし)。
- 正式runner: `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story melos --slug melos --run run_stdchunk_ev_01 --stages tts_a2,provision_shell,gate,assemble --only-clips full_story_part2_c1 --mode real --approved-budget-jpy 30 --tts-execution-mode STANDARD`(stop_scope_check rc=0を各起動前に確認:`../stop_check_z_2.json`/`z_3.json`)。
- 起動1=2026-10-26 16:36:58(JST) / 起動2=16:39:38(間隔160秒)。起動1の前に事前確認(`measure_z/precheck_cache_01.py`、偽generator、API 0): 呼ばれるのはchunk 2件のみ・dialogue 10件は温存。runner dry-run 1回(課金・run書込なし)。**課金前に落ちた起動=0回**、実起動2回(5分内)。

## 2. 発火証拠(分割位置・Chunk数・追加ポーズ)
| 項目 | 値 |
|---|---|
|親/語数|`full_story_part2_c1` / 134語(`measure_z/run_artifacts/chunk_plan_a2.json`)|
|Chunk数/分割位置|2 chunk: k1=76語・k2=58語、境界=段落境界(`boundary_kind=paragraph`)。B_r1: k=ceil(134/100)=2(≒67語×2を目安に、段落境界優先で76/58)。Adv同一記事(b1b)=74/50語|
|chunk別6%減速|k1: src 26.68s→dst 28.274s(比1.0597)/ k2: 22.63s→23.969s(比1.0592)。Gate範囲[1.03,1.09]内。`slowdown_applied=True`、通算TTS各1回(取り直し0)|
|0.2秒位置|親wav内 28.2742〜28.4743s(4800サンプル、全サンプル0=`parent_equals_chunks_plus_exact_4800_zero_samples: true`)、エピソード内 199.8322〜200.0323s(`timeline.chunk_tts`)。pad端peak=9→0、段差4/0(クリックなし)|
|境界の可聴無音|0.5689s(k1末尾0.1557+0.2+k2先頭0.2132)。`_original.wav`×1.06+0.2からの推定0.5743sに対し−0.0054s(減速でmarginが6%伸びる分は承認範囲内=Opus論点1)。Adv同記事の境界=0.7234s(参考。`z_adv_reference_melos_b1b.json`)|
|chunk別gain/peak|gain 1.3594/1.271、peak_after 0.95(cap)/0.8889。エピソード全体のheadroom: peak 0.9688、safety valve未発動(applied=False)|
|親wav|減速後chunk wav+0.2秒の生連結、整数サンプル一致(`verify_raw_parent`)。長さ52.4437s|
|Gate|`M1`: chunk id 2件とも厳格検査PASS(`strict: chunk`)。共有Audio Validation Gate=PASS(a2/b1b)。`z_speed_profile`: 24 clip PASS(dialogue=`std_dialogue_none`、chunk=`std_narrator_slow6`)|
|組立|a2エピソード309.256秒(`a2/assembly/Family_Z_melos_a2.wav`、wavはcommit対象外)。b1b組立も同起動で再実行しGate PASS|

## 3. dialogue TTS 0回・再利用0回(再開時)
- 起動1のAPI呼出(cost_log 7件): TTS 2(chunk k1,k2のみ)、ASR 4(chunk×2回ずつ=減速前+減速後)、responses.create 1(`ret_entity_ner_A`=固有名詞表構築の既存hook、実費は下記)。**dialogue(`full_story_part*_c*` の話者clip)のAPI呼出0**(`--only-clips`の選択外=cache温存、`story_clips_from_plan`同一によりreuse_key不変)。
- 起動2(同引数): cost_log 7件のまま(新規API 0)、`spent_jpy`不変(1.6653)、chunk 2件とも `reused_from_previous_run=True`・TTS 0回(chunk再利用)。
- 比較: 旧Std melos part2_c1は親1 clip(TTS 1回相当)。chunk化後の追加TTS=+1回(2 chunk)/追加ASR+2回。

## 4. Adv/既存の不変(Z Adv回帰なし)
- Z Adv 2 run(melos e1_01 b1b / tell_tale run_chunk_01 b1b)のplan・chunk plan・親display・chunk meta・reuse_keyが実装前HEAD golden(`measure_z/z_adv_golden_01.json`)とバイト一致(`er063_z_std_chunk_test_01.py::AdvInvarianceGoldenTests`)。
- 本evidence run内のb1b: `chunk_plan_b1b.json` は元runとバイト一致、results差分は `path`(run dir)とshell entryの`path`のみ(`full_story_part2_c1`親の内容は同一)。Adv既存evidence=`the_tell_tale_heart/run_chunk_01/runtime_evidence_chunk_z.json` ほか(FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01)。
- Std X/Zの旧非chunk結果は`effective_plan`で従来経路(`test_non_chunk_std_result_still_gates`)。

## 5. 不足・注意(Fable向け)
- tell_tale(Std narrator 129/139語)での実runは未実施(同じコード経路。plan上は60/69・68/71語の段落境界2分割をgoldenで確認)。1作品で発火・Gate・再開0回を取得。必要ならtell_tale追加は後続委任の判断。
- Local Rewrite(R7)は実runでは未発火(正常経路)。offline testで『LR経由chunkに減速記録あり/漏れは厳格Gateが止める』を固定。強制NG fallback/resume/exhaust のZ Std実run証拠は未取得(Adv側は既存E-1〜E-6参照)。
- 事前複製したdialogue cacheに依存(本番の新規runは全clip新規生成)。dialogueの新規生成経路(ctx方式)は本委任の変更範囲外で、reuse_keyが不変であることをtestとgoldenで確認済み。
