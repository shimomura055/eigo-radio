# TEST_PLAN_01 — Family Z 文脈・感情付きTTS Production Wiring(Phase 1 offline test / Phase 2 runtime evidence)

管理ID: FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01(Phase 0、本書は計画のみ。test未実行)。要求項目=`SPEC_LEDGER_01.md`、設計=`DESIGN_01.md`。

## 1. 実行環境・共通前提

- Phase 1 offline test: 新規ファイル `er122_fz_dialogue_ctx_tts_production_01_test_01.py`(+hook parity用 `er122_fz_hook_parity_test_01.py`)。実行は遮断harness下: `$env:PYTHONPATH="netblock_harness_01"; .venv\Scripts\python.exe -m pytest <files> -q`(前例=`er118_fz_full_episode_trial_01_test_01.py:3`)。**外部接続の試行0・cost log行数不変**を各test実行後に確認。Phase 0(本委任)ではtestを実行しない(`.venv`起動禁止)。
- TTS/ASR/LLMはfake backend(送信prompt・呼出回数を記録するstub)。時間は`clock`/`sleep_fn`注入でmock(実600秒は待たない)。STOP sentinelは一時dirの擬似ファイル。
- 既存test(`er063_family_z_audio_01_test_01.py`ほか)は全て無編集で実行し、PASS数を前後比較。
- 『不整合な出力を期待値としてassertするtestは書かない』: 期待値は仕様(ユーザー原文§2・§3)から直接導く。

## 2. Phase 1 offline test(必須。★=ユーザー原文§6受入表の必須6ケース)

| ID | 内容 | 期待 | 対応R |
|---|---|---|---|
| TEST-01★ | 1回目PASS(Std・Adv各)。fake TTS 1回でPASS | attemptはn=1の1回のみ。送信promptのSTYLE区画にCONTEXT blockあり、`entry.dialogue_tts.final_mode=="ctx"`。Trial 53 clip(猿の手Std15/Adv17、メロスStd10/Adv11)について、新moduleの `extract_context`・`validate_emotion_items`(Trialのemotion_notes.jsonのraw_outputを入力)・`build_context_block`・ctx styleの**sha256が、Trial `gen/<cid>/result.json` の `style_sha256` と全53件一致**。`emotion_prompt_sha`がTrialと一致 | R1-1,R1-3,R2-1,R3-1,R3-2,R6-1 |
| TEST-02★ | 1回目NG→2回目PASS(Std・Adv各) | 待機0(`sleep_fn`呼出0)、n=2もctx style、`final_mode=="ctx"`、TTS call 2 | R2-1,R2-2,R6-2 |
| TEST-03★ | 1・2回目NG→3回目PASS(Std・Adv各) | n=2のNG後にcooldown 600.0秒(`sleep_fn`の総和、5秒刻み)→n=3、`final_mode=="legacy_fallback"`、TTS call 3。cooldownは2回目NGの後・3回目の前の1回のみ。`COOLDOWN_SECONDS`を短縮するコードパスが無い(定数一致) | R2-2,R2-3,R6-3 |
| TEST-04★ | 3回ともNG(Std・Adv各) | TTS call総数3(4回目なし)、最終`STOPPED`→`record_outcome`→HUMAN_REVIEW_REQUIRED(Lock+attempt_history)、Gate(`assert_tts_results_complete`/`run_audio_gate`)がBLOCK。LRを起動しない(J-1既定)。Advは減速後NGが3回目なら`finalize_a2_slowdown_final_ng`+HR queue 1行 | R2-4,R2-5,R6-4 |
| TEST-05 | Style完全除外 | `before_attempt(3)` が `style_prefix_override is None`。attempt 3に送られたprompt全体が HEAD の旧`generate_voice_body_wide_margin`(`git show HEAD:…`をtemp moduleとして読込)でstyle無指定の呼出が送るpromptとバイト一致。CONTEXT_HEAD/TAIL/`CONTEXT FOR THIS ONE LINE`/話者・前後セリフ・manner wordsがpromptに1文字も含まれない。Voice・model・max_len・ASR呼出順が同一 | R3-7,R3-8,R3-9 |
| TEST-06 | Std/Adv分岐 | Std=外側ループなし・atempo後処理なし、Adv=`generate_with_a2_slowdown_outer_loop`+atempo 1.06。両者で同一policy。Adv: n=1がASR OK→減速後NG→外側ループ再call→n=2(ctx)になる(nがpassをまたいで継続) | R1-3,R3-8 |
| TEST-07★ | retry途中で中断・再開(Std・Adv各) | (a)n=1 NG後に落とす→再開でn=2から(n=1は再実行されない、TTS call総数=1+再開後分)。(b)n=2 NG後・cooldown中に落とす→再開でcooldown残り時間のみ待機(`started_epoch`基準、≤0なら待たない)→n=3のみ実行(ctx再生成0、TTS call総数=3)。(c)明示再生成(DONE/TERMINAL state、`approve_regenerate`、本文変更)は新規開始。stateは`os.replace`で原子書込(途中書込のtmpが読まれない) | R3-4〜R3-6,R6-5 |
| TEST-08 | STOP | 各attempt前とcooldownの5秒刻みで`_check_stop_sentinel`が呼ばれる。cooldown中にSTOP→即例外、stateは`started_epoch`保持(後でresume可) | R3-4 |
| TEST-09 | 上限3の構造保証 | started-but-unfinished(TTS中に中断)=消費済み。state `n_started==3`でresume→`before_attempt`が`stop`(TTS 0)。Adv外側ループの会計がずれても(`remaining`が大きくても)policyが3を超えない。`record_outcome`の累積はcarried_log込みで実消費と一致 | R2-5,R3-6 |
| TEST-10 | HR Lock・Local Rewrite上限維持 | HUMAN_REVIEW_REQUIRED済みの同一text=0 API(`_blocked_result`)。Z dialogueにLR関数が呼ばれない(monkeypatchで例外化して通る)。`MAX_CUMULATIVE_TTS_ATTEMPTS`=15不変 | R2-6,R3-4 |
| TEST-11 | Trial非依存 | 新moduleと変更したer063/er012_b/runnerのソースに `er118` のimportが0(Grep)。`use_case`/`configure_case`/`setattr(t,`が0。Trial moduleはgit diff 0 | R3-3 |
| TEST-12★ | X/Y/B/C/narrator/KP不変 | (a)hook=Noneの`generate_voice_body_wide_margin`を、HEADの旧関数と新関数で同一fake backendに対し呼び、送信prompt列・`attempt_ctx`相当の引数・attempts_log・戻り値dictが完全一致(成功/失敗/技術失敗/minimal_fallback/stop_retryingの各シナリオ)。(b)`real_generators()`の`narrator/topic_intro/preview/comment/japanese_title/kp_en/kp_ja/kp_expl_en`のsource sha不変。(c)policy=`legacy`のdialogue()が旧と同一promptを送る。(d)X/Y runner(`er019`/`er121`)のsource sha不変・importに新moduleなし。(e)`style_text_for`・`build_reuse_key`(dialogue以外)の戻り値不変 | R1-4,R3-10,R6-6 |
| TEST-13 | ASR表記揺れで再生成しない | 表記違い/同音/Secondary救済でPASSとなるfake ASRを与えたとき、再生成0・leakage観測が走ってもNG理由にならない。leakage flagged時もattemptを消費しない | R3-10,R3-11 |
| TEST-14 | 感情情報の再利用 | `prepare`を2回呼んでもLLM call 1回(notes cache hit)。`--only-clips`・resumeでLLM再call 0。前後台本が変わったclipだけ中立note(追加call 0)。LLM失敗→1回再試行→全clip中立note+`ctx_notes_status`記録(TTS/他は続行)。dry_runでは書込0・call 0 | R5-3 |
| TEST-15 | Dangling Reference | §Gの表の旧方式参照点が全て残存(Grep)。entry/evidence/reuse_key/style_recordの新キーはadditive(旧reader=新キー無し入力で`assert_tts_results_complete`・`verify_z_speed_profile`・`_evidence_row`・試聴ページ生成が動く)。policy=legacyのrunで`inspect_run_style_record`=RECORD_MATCH。新キー付きrecordを旧コードが読んでも不一致にならない(rolesのみ比較) | R7-3 |
| TEST-16 | 自動受理(決定論) | `validate_emotion_items`にACCEPTED/NO_EXPLICIT_CUE/DISCARDED(逐語引用不一致・語数超過・新規固有名詞・強度語・rule 10違反)の各fixtureを与え、3値それぞれのCONTEXT block(state/scene/reaction行の有無)が設計どおり。許可語(story別data)の不足は誤DISCARD=中立化(失敗モードが安全側)。fallback表示名(Trial未検証story)の evidence 記録 | R3-1,R3-2 |

## 3. Phase 2 runtime evidence(正式Production runtime。実費あり。実行は別委任・Opus条件Aレビュー後)

共通: 各起動前に `py tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run> --out <json>`(rc=3なら中止)、`TTS_EXECUTION_MODE=STANDARD` を明示、起動PIDを記録、プロセス終了は自PIDのみ、再起動は委任文が許可した回数のみ。強制NGはdriver(`er122_fzcw_runtime_evidence_01.py`)でのみ。

| ID | path記録値 | 内容 | 合格条件 |
|---|---|---|---|
| E-1 | `normal` | 猿の手 Std+Adv を正式runnerで1起動(`--stages tts_b1b,tts_a2,provision_shell,gate,assemble`)。新run dir。注入なし | 全dialogue clipで送信promptに`CONTEXT FOR THIS ONE LINE`が存在(request捕捉をdriver側patchでsha/文字列記録)。`entry.dialogue_tts`が全clipにある。Gate PASS。headroom.scalar/gain_report記録。provider別実費。X/Y/narrator/KPのprompt不変(同一promptと比較) |
| E-2 | `forced_ng_fallback` | Std 1 clip・Adv 1 clip(別run dir、`--only-clips`)。attempt 1・2を強制NG→実cooldown 600秒→attempt 3(従来) | 送信prompt: attempt 1・2=CONTEXTあり、attempt 3=CONTEXTなし・従来promptとsha一致。cooldown `actual_seconds≥600`。attempt 3は本物の判定でPASS。TTS call総数3 |
| E-3 | `forced_ng_resume` | E-2と同形でcooldown中に**自起動PID**をterminate→同一argsで再起動(1 run dirあたり起動2回) | 再起動後にattempt 1・2が再実行されない(TTS call総数=3、state `n_started`の履歴で確認)。cooldownは残り時間のみ。最終mode=`legacy_fallback`。上限3超過なし |
| E-4 | `forced_ng_exhaust` | Std(可能ならAdv)で attempt 1〜3 を強制NG | TTS call総数3、STOPPED→HR Lock(+Adv減速後NGなら`finalize_a2_slowdown_final_ng`)、Gate BLOCK、attempt_history/HR queue行。LR起動なし(J-1) |

証拠の置き場=既存構造: `er026_output/family_z_production_e2e_01/<story>/<新run dir>/`(runの正規出力)と `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_*.md`(新しい置き場は作らない)。完了報告雛形=OPEN_TRACKING_01 §完了報告雛形。

## 4. Phase 2 並列化・時間

E-1とE-2〜E-4は別run dir・別processで並列。E-2〜E-4のcooldown(600秒×最長)が支配的で壁時間は約12〜15分(E-1の約20〜25分と重なる)。RESTART_STORM(5分に3起動)回避のため、1 run dirへの起動は2回まで。
