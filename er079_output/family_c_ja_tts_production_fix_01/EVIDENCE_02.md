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
