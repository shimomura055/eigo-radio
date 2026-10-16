## 管理ID

`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`(FXPW)委任_02A(Phase 2実装 トラックA: 既定Style profile `fx_20261016`・KP英語K2の2段key分離・P8-KP role分離・M3/M4 role別判定・Family Z推移的import smoke・CLI未指定test・Opus原文保存)。
**並行委任あり(重要)**: 同時に委任_02B(トラックB: In One Line 2文化=`er003_v1_n3_01_advanced_adaptation_generate.py`/`er003_v1_n3_01_standard_a2_generate.py`/`er020_tts_retry_local_rewrite_01.py`/`er019_family_x_entertainment_production_runner_01.py`/新module `er081_family_x_in_one_line_01.py`)と、DQI委任(`docs/pm/PM_GOVERNANCE.md`/`.claude/agents/*`/`docs/pm/tools/`)が同じ作業ツリーで動いている。**本委任はそれらのファイルを編集しない。git add/commit/pushは行わない**(indexが共有されるため。統合委任_04でFableがcommitを指示する)。SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/REGISTER/REPORT_LEDGER)も編集しない。

## 前委任の受入記録(Gate 7)
委任_01(commit `c0c35fc83`): `PHASE1_MATRIX_AND_DESIGN_COMPLETE`。Fable受入ACCEPTED(マトリクス33行、UDR候補なし、設計書)。設計書`WIRING_DESIGN_01.md`に対しOpus条件Aレビュー実施済み(総評「条件付き可」、所見FXPW-R-01〜R-12)。Fableは条件を全件採用した(下記)。ユーザー判断が新たに必要な所見はないとFableが判定(R-03はユーザー原文§4「1文を許容する旧経路を残さない」で既決と判断)。

## 性質/到達上限Status/禁止事項
- 性質: Production code実装+unit/regression test(API 0)。到達上限Status: `TRACK_A_IMPLEMENTED_TESTS_PASS`(PRODUCTION_WIRED判定はしない)。
- 禁止: 有料API、Coffee生成、トラックB/DQIのファイル編集、git add/commit/push、SSOT編集、Family A/B/Cの挙動変更(共有moduleは「既定引数=現行」のみ。golden testで同一性を証明)、Family Zの挙動変更、既存Gate(M2/M3/M4/review_lock/U-1/assert_budget_ok/HR)の緩和・迂回、新retry機構の追加、承認済みPrompt正本の改変(sha一致必須)、`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`のbump(R-12、理由を設計書に1行追記)。
- Opus独立技術レビューGate(11-3): 条件A実施済み(本委任はその条件反映)。設計から更に逸脱する場合は実装せず報告。
- 時間見込み: 150〜180分。
- 費用/日次: JPY0。承認区分: A(承認済み仕様の実装)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。(本委任はTTSなし)
T-3: 費用上限[Cap]なし(JPY0)。

T-0保存先: `docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_02A.md`(全文。python shimが壊れている場合は`py -3`または`.venv\Scripts\python.exe`)。

## ユーザー指示(原文)
`docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_USER.md` §4「TTS Style」(「6仕様をFamily Xの既定profileとして適用する。CLIによる特別指定を忘れた場合でも、承認済みStyleが自動適用されるようにする。Master Audio Storeでは、Style変更後の音声を旧Style音声として誤再利用しない。Role・Style ID・version・Prompt SHAを整合させる。特にP8は旧Full Story候補にも同名が存在するため、Roleを明確に分離する。」)、§2(Prompt正本・「Standard Full Storyの既存6%減速は維持し、PD06との併用を実証する。」)、§1-C相当の互換性維持(別指示`..._PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_USER.md` §1-C「共通基盤の変更がA／B／Cの挙動へ影響する場合、勝手に対象を拡張せず、互換性維持と変更範囲を確認すること」)。

## Fable決定(Opus条件の反映。設計書`WIRING_DESIGN_01.md` §A/§B/§D/§F/§Gを土台に、以下を上書き)
1. **K2 fallback音声のkey分離(R-01採用)**: KP英語(K2)の生成は、Master Audio Storeのkeyを2つに分ける。key A=`instruction_path="primary"`(`style_instruction_id`をK2用に分離、`version`にK2文のsha12)でK2 primaryの2回のみ→非OKならkey B=`instruction_path="english_lock_fallback"`(versionにENGLISH_LOCK文のsha12)でENGLISH_LOCKの2回。既存`EQUALITY_FIELDS`の`instruction_path`を使い、`er006_master_audio_store_01.py`は無変更を目標。Family Zの`_kp_en_two_stage`(`er063_family_z_audio_01.py` L691-728付近)と同じ構成でstrict関数を直接呼ぶ案を優先し、可能なら`er003_v1_repro01_main_generate.py`への`primary_style_override`追加を不要にする。review_lockの会計(`@guarded_generate`1回・slot_offset 0/2・total 4)は外側wrapperで維持。採れない場合は理由と残リスクを報告(実装は止めない=設計案のfallback_used方式+事前manifest非再利用で代替し、その旨明記)。**「K2が通らないときは旧MINIMAL+LOCKで代替生成される」事実を報告に明記**。
2. **M3/M4 role別判定表(R-02採用)**: KP_EN=base sha+`master_audio_key.style_instruction_id/version/instruction_path`で判定、final style判定は新規生成かつ非fallbackのときのみ。KP_JA_MEANING(P8-KP)=base sha+`fallback_used is False`必須(SUPPORT_JAの`JA_FALLBACK_USED_OR_UNKNOWN`と同等分岐)。KP_EXPLANATION_EN(P7)=現行P3と同じ判定。M3戻り値に`warnings`を設ける場合はrunner(AR:1634付近)の扱いを明記・test。設計書§Dへ判定表を追記。
3. **Family Z smoke(R-06採用)**: Zは`x_runner.generate_key_phrase_explanation_en_verified`をlazy importし、x_runner先頭importで`_verify_constants()`が走る。新4定数のsha/長さ検証を追加した上で、Z側test(新規test file、Z本体は無変更)に「x_runnerのimportと当該関数のmock呼出が成功する」smokeを追加。設計書§A-4の根拠記述を訂正。
4. **CLI未指定の自動適用(R-07採用)**: `source=="record"`かつprofileが`DEFAULT_NEW_RUN_PROFILE`でないとき`[WARN][STYLE-PROFILE] 旧profileでresume中`を出す。`--tts-backend`既定値の変更は**既存testに影響せず、非Family X経路のfail-closedを変えない場合に限り**Family X runnerで承認済みbackend(flash-lite統一)を既定にしてよい(採った/採らなかったと理由を報告)。
5. **test追加(R-08採用、§Fに加え)**: (1)main()単位でCLI未指定(`--stage plan --tts-backend speech_metadata_flash_lite`、`--style-profile`なし)→entry_pointの`style_profile_source`・record 6role・`style_profile_plan.roles_sha256`確認 (2)旧n01/`coffee_n01_r2_p3_e1`記録のout_dirでresume→KP英語が従来`ensure_key_phrase_english_component`経路(K2 key不使用)・KP日本語意味がJ3のまま (3)`--only-segments kp1_english`等の再生成でprofileとK2 keyが同一 (4)`_generate_key_phrase_segments_a2`(AR:1355付近)への`style_profile`引数threadingのtest (5)Store再利用K2 entryでM3 PASS、fallback entryがkeyで識別されwarning、P8-KP fallbackがBLOCK (6)Z smoke (7)`qa_evidence.fallback_used`の既存consumer(`er003_v1_n3_01_tts_generate.py`/crosslevel_common/voice01等)をGrepし、KP英語再利用entryを読むconsumerの有無を確定(additive追加の副作用なしをtestで固定) (8)A/B/C共有関数のgolden test(既定引数で送信Prompt/呼出引数がバイト同一)。
6. **P8名称(R-10採用)**: KP日本語意味は`P8_KP_JA_TEXT`(別定数・別role `KP_JA_MEANING`)。AR:1637付近のBLOCK文言「P8対象segmentがP8で生成されていません」を「profile対象segment…」へ、`compute_ledger_hits`既定値/`augmented_startswith_p8`互換キーは残しコメントで「Full Story用の旧P8」と明示。
7. **Std PD06方式(R-11採用)**: Std Full StoryはPD06を逐語(A2減速instruction非連結、`std_append_slower_instruction=False`)で用い、生成後6%減速(既存)を維持。設計書§A-1とCOFFEE_E2E_PLANの試聴確認項目に明記。
8. **R-09**(日本語roleのM4は意図shaのみ): 設計書§Dに既知制約として記録(将来migrate設計の条件)。**R-12**: bumpしない理由を§Aに1行。
9. sha正本(委任_01で再計算済み、再度一致確認してからコードへ): PD06 `3a680861…`(177字)/R2 `625826c1…`(168字)/E1 `8862317f…`(68字)/P7 `05180006…`(136字)/K2 `9d905cfe…`(332字)/P8-KP `b12c8721…`(93字)。フルshaは`WIRING_DESIGN_01.md` §A-1。

## 事前指定Read一覧(D-1厳守)
- `WIRING_DESIGN_01.md` §A・§B・§D・§F・§G・§H(自分の設計の土台)。`COFFEE_E2E_PLAN_01.md`の試聴確認項目節(R-11追記先)。
- `er019_family_x_style_profile_01.py` L40-176, 196, 233, 323, 339-351, 416-449, 463-534, 597-617。`er019_family_x_audio_production_runner_01.py` L60, 97-103, 440-720, 811-1120, 1180-1405, 1616-1638, 2219-2250, 2486-2644。`er006_master_audio_store_01.py` L25-205。`er006_audio_cost_pilot_02_shared_narration.py` L40-290。`er003_v1_repro01_main_generate.py` L677-848。`er063_family_z_audio_01.py` L110-219, 691-729。`er019_family_x_validation_inheritance_01.py` L170-200。既存test: `er019_family_x_audio_production_runner_01_test_01.py`(構造)、`er019_family_x_new_structure_wiring_01_test_01.py`(見出しGrep)。
- Prompt正本(sha再計算): `er057_output/pace_trial_02/prompts/prompts_pace_02.md` PD6、`er080_coffee_kp_pacing_trial_01.py:35`、`er057_std_kp_ja_style_trial_02.py:25`、`er057_tone_trial_kp_ja_gen_01.py:33,38-39`、E1/R2正本(設計書§A-1記載path)。

## 事前指定Grep一覧+手順
1. Opus原文保存: `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a1c04b70da76025ea.jsonl`(無ければ`...\tasks\a1c04b70da76025ea.output`)から`.venv\Scripts\python.exe -I`スクリプトで、SubagentHandback引数またはassistant textの「# FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 Opus独立レビュー所見(条件A)」を含む最後のものを抽出→`docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/OPUS_REVIEW_A_01_VERBATIM.md`(sha256・文字数)。**Read toolで開かない**。
2. `fallback_used` consumer: Grep `fallback_used` を`*.py`(testを除く)で列挙。
3. 実装→test作成→`.venv\Scripts\python.exe -m pytest <新test file> er019_family_x_audio_production_runner_01_test_01.py er019_family_x_new_structure_wiring_01_test_01.py er019_family_x_style_profile*test*.py er063_family_z*test*.py er003_v1_repro01*test*.py -q`(存在するもの)。全PASS必須。失敗は原因を直す(Gateを緩めない)。
4. 設計書`WIRING_DESIGN_01.md`に「§J 委任_02A実装記録(Opus条件反映)」を追記(R-01〜R-12の採否・実装箇所・テスト結果・採らなかった選択肢と理由)。
5. `git status --short`で変更ファイル一覧を取得(add/commitしない)。secret scan(`--paths` 変更ファイル)結果を記録。

## 実行コマンド全文
手順0: `cd C:\Users\tensh\eigo-radio; git status --short | Measure-Object -Line`(並行委任の未commit変更が見えるのは正常。触らない)。
手順1〜5: 上記。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FXPW2A.md`: 1 T-0・Opus原文sha256 / 2 実装一覧(file:line範囲、各Fable決定1〜9との対応) / 3 K2 2段key(採用方式、key A/Bの実値、fallback時の挙動の明記) / 4 M3/M4 role別判定表(最終) / 5 test結果(新規test数・既存test PASS数、コマンド全文) / 6 A/B/C・Zの非影響証拠(golden test・smoke) / 7 変更ファイル一覧(未commit)・secret scan / 8 逸脱・採らなかった選択肢 / 9 費用JPY0・所要 / 10 受入記録5項目(当初目的=原文§4「TTS Style」逐語/最終成果物/証拠/一致・不一致/判定) / 11 P1判定整合行(重大NG/主因/是正対象/STOP理由/提示: 不一致なしなら1行)。

(注: 本ファイルは委任文の保存コピー。システム側の共通指示・Attribution等は含まない。)
