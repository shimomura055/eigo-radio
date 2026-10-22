# RUNTIME_EVIDENCE_02: 固有名詞アラーム受理+TTS発音供給のX/Z配線(委任_02、2026-10-22、実費JPY11.15)

管理ID: PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_02 / Status: `WIRED_PENDING_FABLE`(PRODUCTION_WIRED宣言はFable)。設計=`IMPLEMENTATION_DESIGN_01.md` §15。

## 1. Xの実発火(正式Production TTS段関数・新run dir・旧run無変更)
- 素材: Khaite/Toteme/Altuzarra/ELLEを含む既存Family X記事(`er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/small_bag__run_02`)のb1b scaffold(parts/support/segment_plan)を新run dir `er019_output/family_x_audio_production_wiring_01/pnap_evidence_01__small_bag__run_02` へコピー(旧run無変更)。
- 実行: `docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/runtime_evidence_x_01.py <out_dir> full_story_part2,full_story_part3`(1回のみ・再起動なし)。runner mainではなく同runnerのTTS段関数`generate_family_x_b1_segments`を`_ONLY_SEGMENTS`(`--only-segments`相当)で直接呼出(main内のRisk Flagger[`review_queue/post_en`追記]・scaffold・assembleは固有名詞アラームと無関係で、費用/共有ファイル書込を避けるため除外)。decorator(`secondary_run_scope`/`fx_iol`/`pnap_hooks.family_scope("X","b1b")`)・Production判定器・Ledger・Master Storeは正式のもの。`TTS_EXECUTION_MODE=STANDARD`、style profile=`fx_20261017`(新規run既定)、tts_backend=`speech_metadata_flash_lite`。STOP確認=`tools/stop_scope_check_01.py` rc=0。
- 結果: `full_story_part2`が **attempt1=TRUE_CONTENT_MISMATCH**(ELLE->"L"等の非固有名詞差+Khaite->Kite+minaudiere)で再試行 -> **attempt2で`PASS_WITH_PRONUNCIATION_ALARM`**(`audit.state`、`reason_code=pronunciation_alarm_accept`、slot=2、layers=[tier3]、Secondaryはキャッシュ(Tier3層で取得済み)を利用=追加Azure呼出なし)。アラーム対象=`khaite`(Primary転写 `Kate`、原稿に対し類似度0.80、固有名詞根拠=Ledger)。`full_story_part3`(Toteme/Altuzarra)は`SECONDARY_ASR_CORROBORATED_MATCH`でPASS_WITH_WARNING(既存救済層で解決、アラーム不要)。
- (a) HR Lock: 両segmentとも`review_lock_state`=**RESOLVED**、`human_review_required=False`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`への追記**0行**(grep `pnap_evidence_01`)、`approve_regenerate`不要で完成。
- (b) 掲載: `<run>/b1b/audit/pronunciation_alarms.json`(count=1、consistency match=true)・`operator_alarm_report.md`(固有名詞・音声箇所[wav/文脈/目安8.1秒]・検出した不一致[原稿/Primary/Secondary]・発音の根拠[階層=UNVERIFIED_AI_OUTPUT/確信度medium/hint=KAYT]・TTS発音改善[供給なし:EVIDENCE_NOT_VERIFIED_ESTIMATED]・最終状態[アラーム付き完成]・使用モデル)。runnerの標準出力にも同報告を出力(コンソールログ=`pnap_run_console.log`)。
- (c) 公開ページ非露出: 生成物は`audit/`のみ。公開ページbuilder(Z `build_pages`/X `build_player_html`)の関数ソース及び`user_test/**/*.html`にアラーム語なし(test `test_page_builder_functions_do_not_reference_alarm_terms`/`test_generated_public_pages_do_not_contain_alarm_terms`)。PASS_WITH_WARNING試聴リスト(`pass_with_warning_listening_list.json`)にはアラームは載らない。
- (d) KP非適用: KP(`dual_required`)はunit/adapter wiring testとON/OFF差分(下記)で差分0。本runはKP segmentを含まない(`kp_scaffold_status=KP_SCAFFOLD_JSON_MISSING`)。
- 実使用モデル: TTS=`gemini-3.8-flash-lite-tts`(voice Aoede)、Primary ASR=`gpt-4o-mini-transcribe`(`routing.ASR_ROUTING["en"]`)、Secondary=`azure-speech-stt`。費用 JPY7.93(gemini 2.62/openai_asr 0.52/azure 4.79、`raw_usage_log.jsonl`)。Stage 1調査(Perplexity)は対象語がLedger/否定記録済みで0回。

## 2. Zの実行(Melos、新run dir `er026_output/family_z_production_e2e_01/melos/run_pnap_01`、正式CLI)
- 実行: `er026_family_z_fiction_production_runner_01.py --story melos --run run_pnap_01 --stage tts_a2 --mode real --approved-budget-jpy 45 --only-clips full_story_part1_c1,full_story_part1_c5,full_story_part3_c3` と `--stage tts_b1b --only-clips full_story_part1_c1,c5,c9,c11,full_story_part3_c1,c3`(異なる素材/stage。再起動ではない)。`run_e2e_06`の入力(plan/support/KP)をコピー(旧run無変更)。STOP確認rc=0。
- 結果: 9 clip全てが既存救済層(Tier3等)で`PASS_WITH_WARNING`(Primary転写 `Mellows`/`Mello`等でも救済)= **アラーム0件(自然発火せず)**。Zのscope(Z)・finally hook・`audit/pronunciation_alarms.json`・`operator_alarm_report.md`(「0件」と明記)・stage結果への埋込は実run上で動作。**Z実発火の代替証跡**: `er103_pnap_wiring_test_01.py` の `TestZRunTtsStageHook`(Z正式関数`run_tts_stage`をfake generatorで通し、ALARM entryがaudit/とreportに出る・途中失敗でもfinallyで『集計失敗』報告・scope解除・flag OFFで副作用0)と `test_scope_on_accepts_alarm_no_hr[Z]`(adapter、scope Z)。費用 JPY3.22(`cost_log.jsonl`)。
- Z clip IDのrole解決: `full_story_part*_c*`->FULL_STORY、`comment_*`->COMMENT、`preview`->PREVIEW(test)。`topic_intro_en`はroleなし=対象外のまま。

## 3. ON/OFF差分(`onoff_differential_02.py` / `onoff_differential_02_result.json`、API 0、保存4,032ペア=3,041英語+991日本語)
- OFF(flag OFF・scope無し)に対し、flag ON・scope無し(Family A/B/C・単体相当)= **差分0**、flag ON・X scope・KP `dual_required`= **差分0**、flag ON・X scope・日本語text(`ja-JP`)= **差分0**。
- X英語本文(`full_story_part1`)のみ**260件がHR(`ASR_VALIDATION_UNCERTAIN`/`human_review_required=True`) -> `PASS_WITH_PRONUNCIATION_ALARM`**。内訳は全て固有名詞の聞き違い(khaite/toteme/melos/gruen/mimoun/minaudiere/altuzarra/bisnow/triangeln/dionysius等)で、数値・否定・非固有名詞差のflipは0。注: この差分試験のSecondary=Primary転写のmockゆえ実運用より受理に寄る(上限寄り)。HR queue書込 spy 0件・Stage 1調査はmock(2,825回、API 0)。

## 4. Regression(2026-10-22実行、新規失敗0)
`run_project_regression.py`: er006 61/61、er019 560/560、er063 84/84、er026 155(153 PASS・2 skip)、er011 321/321、er103 52/52、er096 16(12 PASS・4 skip)、er007 111、er012 231、er013 323、er021 102、er094 37、er010 105、er020 86(1 fail)、er008 145(2 fail)。pytest形式: er078全ファイル 459 PASS、er097 2ファイル+新規`er103_pnap_wiring_test_01.py`(71) = 137+ PASS。**既存失敗4件**(er008 pricing 2件・er020 `RegressionCorpusTest`1件・er007 JA `test_single_engine_repetition...`1件)は、配線前のHEAD(`e6a96883d`)のclean worktreeでも同一に失敗=本件由来でない。pytestでの`er012` subprocess 2件の見かけの失敗は`PYTHONIOENCODING=utf-8`をこちらが付けたことによるcp932デコード差(通常実行では231/231 PASS)。

## 5. P-09集計(0円、`p09_slot_resolution_stats_01.py`)
全run保存`attempts_log`(2,544segment)+HR queue未解消45segmentから、固有名詞のみ不一致の最初のNG後に次slotで解消した率: 全体 **3/55=5.5%**(保存のみ3/10=30%は生存者バイアス: 未解消はHR queueにだけ残る)。Fable規則(>=25%なら2)に従い **`ALARM_ACCEPT_MIN_SLOT=1`**(初回attempt受理)。X=2/3(n=3)は母数小。

## 6. 校正(`calibrate_replay_02.py`、保存HR queue 88イベント)
受理45->40。差分5件=Muse->use系4件(`ASR_SIDES_ALL_GENERAL_WORDS`)+Khaite->Kate1件(両ASRともKateと書いた=正しい発音の可能性が高い語。一般語化ガードで不受理=HR側。供給(B階層承認)で解消される型)。

## 7. 供給の実発火
実Ledger38件はA階層(引用検証済み・公式host)0件・人承認B階層0件のため **供給対象0件**(Khaite=B階層は人承認待ち)。供給機構のunit/wiring evidence: 承認CLI・`supply_for_tts`(flag/scope/KP恒等、Reicher->Rikerの`supply_map`登録、失敗時恒等)・A階層条件・大文字小文字区別・継承再判定での供給後TTS入力保存は`er103_pnap_wiring_test_01.py`/`er103_proper_noun_alarm_policy_test_01.py`で検証。

## 8. 完成報告のアラーム表示例(Xの実run出力)
```
## 固有名詞発音アラーム(運営責任者向け・一般リスナー非表示)
1箇所。最終状態=**アラーム付き完成**。制作は停止せずHuman Reviewにも回していません。確認・承認操作は完成の条件ではありません。
- **khaite** × 1箇所
  - [X/b1b/full_story_part2] .../b1b/narration/full_story_part2.wav / 文脈 `...ter 2026 styling. Its examples included [[khaite]]'s palm-sized evening clutch and Chanel'...` / 目安8.1秒
    - 検出した不一致: 原稿 `khaite` -> Primary `kate` / Secondary `(原稿どおり)`
    - 発音の根拠: 階層=UNVERIFIED_AI_OUTPUT / 確信度=medium / hint=KAYT
    - TTS発音改善: 供給なし(EVIDENCE_NOT_VERIFIED_ESTIMATED)
    - 最終状態: アラーム付き完成 / 使用モデル: ASR=gpt-4o-mini-transcribe, Secondary=azure-speech-stt, TTS=gemini-3.8-flash-lite-tts
```
