# FAMILY-C-JA-TTS-PRODUCTION-FIX-01 委任_02 証跡 (2026-10-16)

結論: 実装・test・0円検査・Run C'(0円)まで完了。**条件付きSTOP(b)に該当**したため有料Run A/Run Bは未実施(API 0、費用JPY 0)。`PRODUCTION_WIRED`は宣言しない。

## 1. 0円検査(`evidence_02/`)
| 項目 | 結果 | 証跡 |
|---|---|---|
| 記号Gate事前検査(R6、Layer-4 `detect_prohibited_symbols(.., "ja")`、Comment1-3・japanese_title・preview_ja) | 5文面 findings 0件、`requires_stop` 0件。条件付きSTOP(a)は非該当 | `symbol_gate_check.json` |
| reuse plan dry-run(R4)、`article_config.json`全走査 | 下記2節。**条件付きSTOP(b)該当** | `reuse_plan_dryrun.json` |
| Run C'(Memory A2=Trial-11出力をreuse_from、空出力dir、TTS/ASR関数は呼ばれたら例外) | clip 16中 採用7 / 非採用9。非採用9は全て「src wavあり・由来不明」=承認済み音声の偽陰性。実Production経路でも`story_001`で最初のTTS要求(例外で停止) | `run_c_prime/run_c_prime.json` |
| 由来連鎖探索(非採用9 wavのsha256を全`audit/tts_generation_results.json`から検索) | `reused`偽の新規生成記録は**どこにも無い**(各wavは3〜6個のauditに`reused`真または不一致で現れるのみ) | `provenance_chain_search.txt` |

## 2. reuse plan dry-run 要約(旧ルール=src wav存在のみで全再利用 / 新ルール=由来照合)
| reuse_from | clip | 新ルール再利用 | 再生成 | 備考 |
|---|---|---|---|---|
| `er013_output/family_c_episode_trial_11/memory_a2`(**ユーザー試聴承認済みepisode**。CURRENT_SPEC.md:1049-1050,1129-1130) | 16 | 7 | **9** | 再生成=story_001,002,003,004,006,007,comment_1〜3(Trial-11のauditは`reused:true`でmeta無し。承認済み音声の差替えになる) |
| 同(06d attempt0/1 config、japanese_titleも) | 16 | 6 | 10 | title文面が違うため |
| `evidence_06b/crun/c_out/a2`(Memory本番config文面で判定) | 16 | 3 | 13 | legacy-upgraded meta・`reused`真auditのため |
| `er013_output/family_c_production/memory/a2` | 16 | 0 | 16 | 同上 |
| `evidence_06d/cja/reuse_src` | 16 | 3 | 13 | 同上 |
digital_twins / home_robots の`article_config.json`には`reuse_from`が無い(対象外)。

汚染資産(バグ期出力dir、JA comment/title/previewのwav 11件、全て`legacy_upgraded` meta): `evidence_06d/cja_attempt1_reuse_from_legacy_ok_override/c_out/a2`、`evidence_06d/cja_attempt2_reuse_from_copy_no_meta/c_out/a2`、`evidence_06d/cja/reuse_src`(全一覧は`reuse_plan_dryrun.json`の`polluted_assets_06d_cja`)。新ルールではこれらをreuse_from元として使っても由来照合で不採用になる。

## 3. 条件付きSTOP判定
- (a) 記号Gate違反: 非該当(0件)。
- (b) **該当**: 承認済みepisode(Trial-11 Memory A2)の音声9clip(Story 6 + Comment 3)が、R1(`reused`真のaudit・legacy-upgraded metaを由来証拠にしない)を厳格適用すると再生成対象になる。Run A/Run Bは実行せず。
- 原因: Trial-11のauditはTrial-10等からのコピーclipを`reused:true`で記録し、metaも無い。コード上、これらの音声が「その原稿のために生成された」ことを機械的に証明する記録がリポジトリ内に存在しない(3節の連鎖探索)。R1の厳格適用=「承認済み音声の全面再生成」または「由来不明のまま再利用(=旧欠陥の温存)」の二者択一になる。
- 解決案(Fable判断。いずれも仕様判断を含むため未実装): (案1)承認済みepisodeのwav sha256を固定した「ユーザー承認済み資産マニフェスト」を由来証拠として追加する(ユーザー試聴承認=人間による由来保証。小改修、承認済み音声は不変、新規コードのため要ユーザー確認)。(案2)R1をそのまま適用し承認済み音声を再生成(費用 概算 EN story 6 + JA 3 clip=約JPY 4、ただし承認済み音声の差替え=ユーザー再試聴が必要)。(案3)reuse_from経由は「text sha256のみ一致(音声由来は未保証)」を再利用不可とし、承認済みepisode用に限り明示flagで例外許可(Production flag増加)。推奨=案1(承認済み資産を不変に保ちつつ、新原稿への誤紐づけは防げる)。

## 4. test
- 新規 `er079_family_c_ja_tts_fix_02_test_01.py` 21件 + 既存 `er013_family_c_production_test_01.py` 39件 = 60 passed(netguard、API 0)。`evidence_02/pytest_new_and_er013.txt`
- 静的監査 `er078_asr_unified_wiring_static_audit_01.py` + 06d + 06c + 05 test: 113 passed。静的監査CLIの差分は空(`unlisted_new_calls`/`vanished`/`count_changed` 全て[])。`evidence_02/pytest_static_06d_06c_05.txt`、`static_audit_cli.txt`

## 5. B-4 完了条件9項目の充足表
| 項目 | 状態 | 理由/証拠 |
|---|---|---|
| Family C日本語Commentの新規TTS成功 | 未達(未実施) | 有料Run A未実施(条件付きSTOP(b))。コード上は`language="ja"`伝達をtestで確認 |
| 必要な日本語Sectionの生成・ASR確認 | 未達(未実施) | 同上。JA Validator到達はtest(mock)のみ |
| 英語Sectionの回帰なし | 部分達成 | 既存39 test + 英語再利用test(API 0)。実音声Run未実施 |
| 原稿変更時の誤音声再利用なし | 達成(test/0円) | `ProvenanceCheckTests`/`CommentStageTests`、Run C' |
| Production実行でruntime evidence | 未達 | Run C'(0円・TTS例外差替え)のみ。有料Run未実施 |
| Validator/Regression/integration test PASS | 達成 | 上記4節 |
| SSOT/Open Item/Git反映 | SSOT・OPEN・Git反映済み(commit hashはRESULT_PACKET) | |
| Dangling Reference Check | 達成 | RUNTIME_EVIDENCE_06.md L370付近に注記追記。runner内の旧参照(`_copy_with_ok`の3呼出点)はGrepで置換確認。固定asset用3呼出は意図的に残置 |
| 実成果物が既存Family C仕様を満たす | 未確認 | 実音声未生成 |

費用: JPY 0(API呼出0)。使用モデル/Voice: 該当なし(音声生成せず)。

## 6. 委任_03 Run A/B 実音声evidence(2026-10-16、隔離dir `evidence_03/`、Production正式entry=`er013_family_c_production_runner_01.py main`)
結論: **Run A/Bとも完走(stage `OK`)**。JA 5 clip(Comment 1-3・japanese_title・preview_ja)がProduction正式経路で新規TTS成功・JA ASR判定PASS(Secondary呼出0)。英語Story 6 clipも新規生成されPASS(回帰なし)。原稿変更(Run B)では変更した1 clipだけ再生成、他15 clipは再利用(API 0)。**承認済み資産dirのsha256は実行前後で完全一致(138 file)**。費用 実測 JPY 12.65(Run A 11.00 + Run B 1.65、見積8を超過、Guardrail 14内)。`PRODUCTION_WIRED`は宣言しない。

**重要な逸脱(test fixture): story_001のコロン**。attempt0(API 0)で`story_001`のtts_text(`...too many times: rain on the window...`)がLayer-4記号Gate(`RESIDUAL_PLACEHOLDER_OR_PAUSE_SYMBOL`)でTTS前にSTOP(`evidence_03/run_a/runner_execute_attempt0_pre_api_gate_stop.json`、費用0)。Gateは迂回せず、隔離dirの複製記事で当該1か所のコロンをカンマにしたtest fixtureで実行(`--fixture-colon-fix`、`run_a/fixture/reader_facing_article.txt`、元記事は無変更)。したがって**Run Aの入力は「承認済み原稿と同一」ではなくstory_001のみ1文字違い**。これは新ルール(R1)により承認済みepisodeのstory_001が再利用できず、かつ再生成するとGateに止まる=Memory記事は現行Productionで全面再実行できない、という**新規発見(OPEN-387、Fable報告)**。
- 運用差: Run Aのreuse_fromは承認済みdir本体ではなくその**複製**(`run_a/reuse_src`、title/preview wavだけ除外。承認済みdir本体は無変更)。理由: 正式configのまま承認済みdirを使うとtitle/previewは`audit_fresh_generation`で採用され、JA新規clipが3本にしかならず5 clip evidenceにならないため。

### 6-1 Run A clip表(`evidence_03/clip_table_run_a.json`、`clip_table.md`)
| clip | 新規/再利用 | language実値 | 秒 | state/reason | Secondary | 備考 |
|---|---|---|---|---|---|---|
| story_001,003,006 | 新規 | en | 18.64/3.09/17.15 | PASS/primary_pass | 呼出0 | narrator、gemini-2.5-pro-preview-tts |
| story_002,004,007 | 新規 | (device/brother voice、en固定) | 1.33/1.29/4.25 | PASS/primary_pass | 0 | 同上 |
| story_005,008,009,010、topic_intro_en | 再利用 | - | 35.58/28.05/20.25/23.84/3.40 | - | 0 | 由来=`audit_fresh_generation`(複製元のaudit新規生成記録) |
| comment_1_ja | **新規** | **ja** | 17.20 | PASS/primary_pass | 0 | gemini-3.1-flash-tts-preview |
| comment_2_ja | **新規** | **ja** | 15.12 | PASS/`primary_pass_approved_equivalence:READING_MATCH` | 0 | 読み一致の承認済み同値 |
| comment_3_ja | **新規** | **ja** | 16.84 | PASS/primary_pass | 0 | |
| japanese_title | **新規** | **ja** | 1.78 | PASS/primary_pass | 0 | |
| preview_ja | **新規** | **ja** | 16.16 | PASS/`primary_pass_approved_equivalence:READING_MATCH` | 0 | |
- 全体: stage `OK`、`audio_validation.json` status=PASS、assembled episode 313.97秒(承認済みは316.569秒、Story 6 clip再生成のため一致しない=想定)、mp3化・player・web_delivery生成、segment 35。
- JA clipの長さ15〜17秒は06d `cja`の失敗時(英語固定で`16.9/15.3/16.4秒`が見積上限5.5秒超過で破棄)と同一帯。`language="ja"`伝達後は破棄されず`OK`(旧欠陥の解消を実音声で確認)。閾値は変更していない。
- Secondary(Azure)呼出0(全clip Primary PASS)、Azure重複0。隔離dir側の`human_review_queue`/`attempt_history`/`foreign_token_hr_queue`は未生成=追記0行(retry/HR投入なし)。`pass_with_warning_listening_list.json` count=0(試聴リスト登録0)。
- TTS 12 call(Story 6 + JA 6)。JA 6 callのうち1 callはcomment_1の最初の呼出で出力token無し(音声なし、JPY0.078)で、`verified_strict`内部の既存retryで成功(無限loopなし)。費用meter(token実測、`evidence_03/run_a/usage_log.jsonl`): TTS 12 call + OpenAI ASR 20 call = **JPY 10.996**。ASR 20のうち英語Story 6とJA 3 clipは『TTS内検証』と『consistency stage』で同一wavに各2回(prev_auditのsha不一致のため再ASR=既存挙動、費用影響約JPY0.4)。
- 使用モデル: TTS=gemini-2.5-pro-preview-tts(EN)/gemini-3.1-flash-tts-preview(JA)、ASR=gpt-4o-mini-transcribe(Primary)。Production既定モデル(評価用の別モデル比較ではない)。voice名はusage_logに記録されない(narrator固定voice、コード上)。LLM 0 call。

### 6-2 Run B(誤再利用防止の実体確認、**test fixture(Comment Contract未経由)**)
- 入力: reuse_from=`run_a/a2`、出力側`run_b/a2/comments_ja.md`のComment 1のみ手で1か所変更(`箱を両手で`→`箱を、そっと両手で`)。reuse元側は無変更。T-2事前記録: 再生成予定=`comment_1_ja.wav`のみ(想定外0)。
- 結果: **再生成はcomment_1_ja 1 clipのみ**(language ja、17.51秒、PASS/primary_pass)。他15 clip(Story 10・topic_intro_en・comment_2/3・japanese_title・preview_ja)は`provenance_basis=src_meta`で再利用(API 0)。API: TTS 1 call + ASR 2 call、JPY **1.653**(`run_b/usage_log.jsonl`)。新wavのmeta `tts_text_sha256`が新文面のsha(`clip_table_run_b.json`)、旧Comment 1 wavは出力dirに残らない。
- 共有state: Run Bは`shared_state_unchanged=true`。Run Aは`false`だが、差分ファイル(`er011_output/attempt_history.jsonl`、`er021_output/.../telemetry.jsonl`)の追記行は並行実行中のAUW 委任_10のtest(theme `wiring_theme_auw5`/`dummy_out.wav`、07:57:45-50)で、本runのlabel/path/themeを含む行は0(grep確認)。本runの書込先(attempt_history/HR queue/Master Store/er025・er021 telemetry/cost log)は`evidence_03/<run>/`へ隔離されていた。
- STOPセンチネル: 各run前に`stop_scope_check` rc=0(`run_a/stop_check_pre*.json`、`run_b/stop_check_pre.json`)、`stop_files_present=[]`。

### 6-3 承認済み資産dirの不変確認
`approved_assets_before.csv`/`approved_assets_after.csv`(対象: `er013_output/family_c_episode_trial_11/memory_a2`・`memory_b1`、`family_c_episode_trial_12/digital_twins_a2`・`digital_twins_b1`、計138 file、path/sha256/size)を`cmp`で比較: **完全一致(差分0)**。harnessに承認済みdir配下への出力を例外にするガード(`assert_not_approved_asset`)を実装。

### 6-4 B-4 完了条件9項目 最終充足表
| 項目 | 状態 | 証拠 |
|---|---|---|
| Family C日本語Commentの新規TTS成功 | **達成** | Run A comment_1-3 `ja`新規生成・PASS(17.20/15.12/16.84秒) |
| 必要な日本語Sectionの生成・ASR確認 | **達成** | title/preview含むJA 5 clipがJA ASR(gpt-4o-mini-transcribe, lang ja)でPASS、Secondary 0 |
| 英語Sectionの回帰なし | **達成(fixture付き)** | Story 6 clip新規生成・PASS、再利用5 clipも整合。ただしstory_001はコロン回避fixture |
| 原稿変更時の誤音声再利用なし | **達成** | Run B: 変更1 clipのみ再生成、metaのtext sha更新、旧wav不使用 |
| Production実行でruntime evidence | **達成** | Production正式entry `main()`、`evidence_03/run_a,run_b` |
| Validator/Regression/integration test PASS | 達成 | test 60 passed(`evidence_03/pytest_after_runs.txt`) |
| SSOT/Open Item/Git反映 | 達成 | 本節・OPEN-372/385/387・DECISION_LOG・CURRENT_SPEC(commit hashはRESULT_PACKET_FCJ3) |
| Dangling Reference Check | 達成(委任_02) | 変更なし |
| 実成果物が既存Family C仕様を満たす | **部分達成** | JA 5 clip+Story+assembled episodeは完走(`audio_validation` PASS)。ただし(i)story_001が承認済み原稿と1文字違うfixture、(ii)Story 6 clipが新規生成で承認済み音声と別物(隔離dirのため承認済みepisodeは不変)。ユーザー試聴は未実施 |

### 6-5 新規発見(Fable報告、実装せず)
1. **story_001のコロン x 記号Gate x 新R1 = Memory記事の全面再実行不能**(OPEN-387)。選択肢: (a)記事本文のコロン修正(承認済み原稿の変更=ユーザー判断)、(b)OPEN-385案1のsha固定マニフェストで承認済みstory_001を再利用、(c)Writer/Normalizer側でコロン自動変換(Production挙動変更)。
2. ASRが同一wavに『TTS内検証』と『consistency stage』で2回走る(既存挙動、1 episode約JPY0.4)。改善候補だがscope外。
3. 実費JPY12.65は見積8を超過。TTS実測は1 clip約JPY1.4〜1.6(Gemini token実測)で、見積単価(0.062/clip)は過小(06d実測0.46/attemptよりも高い)。
