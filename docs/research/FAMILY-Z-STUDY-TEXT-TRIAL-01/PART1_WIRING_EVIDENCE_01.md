# PART1_WIRING_EVIDENCE_01(Part 1「Vocabulary & Expressions」案α Production配線 runtime evidence)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_14 / 日付: 2026-10-25(JST 12:00〜12:30) / Status: Z=`WIRED_PENDING_FABLE`(描画停止中)・X=`WIRED_EXCEPT_USER_PAGE`(PRODUCTION_WIREDではない。Fable受入後)
設計=`PART1_WIRING_DESIGN_01.md`(§13〜§17が正)、Opus条件Aレビュー逐語=`PART1_WIRING_OPUS_REVIEW_01.md`、Production commit=本evidenceと同日の「委任_14 Step2」commit。
生ファイル=`part1_wiring_evidence_01/`(下記パス)。実公開ページは更新していない(公開dir・user_test/ 変更0)。

## 0. 実行条件・費用
| 項目 | 値 |
|---|---|
| 費用 | **実費合計 約1.32円**(Z 2 call=0.2687円[cost_log.jsonl]、X scaffold 0.97円[うちPart 1 0.1069円]+`--stage study_text`再生成 0.0875円)。委任上限10円・案件見積300円以下。再起動0、外部停止0 |
| 日次 | 着手時の当日(JST)開発費集計 790.5円(`daily_dev_cost_01.py`、他agent分を含む)+本件約1.3円=日次1,000円内 |
| STOP | 有料run前に`tools/stop_scope_check_01.py --managed-id FAMILY-Z-STUDY-TEXT-TRIAL-01`を各run-dirで実行、全てrc=0・stop=false(`scratchpad`の`stop_check_{z,z2,z3,x,x3}.json`) |
| モデル | **gpt-6-luna**(最新世代の推奨系=`routing.SUPPORT_MODEL`。Trial-04と同一・PM_GOVERNANCE 25節の最新モデル原則と整合。旧/下位モデルの使用なし) |

## 1. Z(Family Z)— 複製run `run_p1_evidence_01`(元=告げ口心臓 `run_sf_prod_02`、audio dirと費用ログを除いてコピー)
### 1-1 事前確認(Opus実装時必須10)
複製元の`kp_expl_b1b`がreuse・人称関所がCLEANになることを、有料前に読取だけで確認した(スクリプトで`select_person_mismatches=[]`、`collect_unevaluated=[]`、`collect_unresolved=[]`、`kp_expl`のsig再計算=provenance entryのinput_sha256と一致[6087db79bf1d]、used_form 3件全て`fulltext_source_ref`あり)。→`--stage kp`は`kp_expl_b1b`をreuseして`kp_part1_b1b`まで届く。
### 1-2 発火(`Z_stdout.txt`・`Z_stdout_regen.txt`)
- 1回目: `--mode real --story the_tell_tale_heart --slug the_tell_tale_heart --run run_p1_evidence_01 --stage kp --approved-budget-jpy 3`。`kp_part1_b1b`が**1 call**発火(`kp_b1b`/`kp_expl_b1b`はreuse=API 0、人称関所CLEAN=修復call・artifact書換なし)。実費0.1314円。
- 2回目(明示再生成): 同条件+`--regenerate-stage kp_part1_b1b`。1 call、実費0.1373円。
- 3回目(再実行=resume): 同条件(再生成指定なし)で`--stage kp`を再実行→`spent_jpy`が0.2687のまま増えず**API 0・reuse**(`Z_stdout_reuse.txt`、cost_log 2行のまま)。→`Z_kp_general_explanations.json`は2回目の結果。1回目の保存=`Z_kp_general_explanations_run1_before_regen.json`、費用=`Z_cost_log.jsonl`(stage=`kp`[1回目、コード改善前のタグ]/`kp_part1`[2回目])。
### 1-3 実測値(2回目、`Z_kp_general_explanations.json`の`audit`)
| 項目 | 値 |
|---|---|
| actual model_id | `gpt-6-luna`(要求と一致。応答modelを検証、不一致ならretryもfallbackもせずSTOP) |
| routing | process=`KEY_PHRASE_GENERAL_EXPLANATION` → `routing.PROCESS_MODEL_MAP`=`routing.SUPPORT_MODEL`=gpt-6-luna |
| prompt_template_sha256 | `4d7ae557190650650592ae5e6df09e1946d87c582e32187bb8dfd6d32cfaf694`(Trial-04 P1_HEAD+P1_BODY逐語、testで固定) |
| prompt_sha256(実送信Prompt) | `fe1c5966c22a11f3207758bfcb420838d576ae7e201d74283429a86f6f35b333` |
| input_sha256 / phrases | `ddf03b17…`=`["sharpen someone's senses","cloudy film","never stir"]`(**表現3件のみ**。gloss・引用文・本文・作品名は送っていない) |
| signature(再生成キー) | `fe4b187bc9adc077…`(rank昇順の表現+prompt sha+model。`provenance.json`のkp_part1_b1b entryのinput_sha256と一致) |
| retry/reuse | retried_for_parse=false、reused=false(3回目の再実行は`ensure_stage`がreused、API 0) |
| usage | input 685 / output 1,579(reasoning 1,034) tokens |
| 費用 / 時間 | 0.1373円(1回目0.1314円)/ 14.6秒(1回目15.6秒) |
| provenance | `writer/provenance.json`の`downstream_stages.kp_part1_b1b`にmodel/prompt_sha256/total_cost_jpy/retried_for_parse/response_idsを記録(`Z_provenance.json`)。`downstream_stale=[]` |
### 1-4 出力(解説全文)
`part1_wiring_evidence_01/Z_part1_vocabulary_expressions.md`(.jsonも同階層)。3表現とも核の意味が先頭に来て、本文(告げ口心臓)の場面・人物に引きずられていない(Trial-04と同じ観察: 入力が表現のみのため)。`source_sentence_ja: null`・`translation_status: PENDING_USER_DECISION`を明記。
`Z_render_demo_T2_NOT_PUBLISHED.html`=一時的なT2記録で描画した構造例(**ユーザー判断ではなく、公開物でもない**。`<section class='study'>`+`<h3>`+`<dl>`、HTMLエスケープ・`*`→`<i>`変換)。

## 2. X(Family X)— 複製source `er019_output/part1_wiring_evidence/run_ev_01`(元=word_gacha `run_wg_01`のb1b/article.md)
### 2-1 主経路(`run_theme_scaffold`内)の発火(`X_scaffold_stdout.txt`)
- `--slug part1_wiring_evidence --run run_ev_01 --level b1b --stage scaffold --budget-jpy 10`。b1bのscaffold(Preview/Comment+KP選定)→`key phrase status=CANONICALIZATION_PASS`→**KP PASS後に`generate_part1_for_b1b`が1 call発火**(`[cost] so far=0.86 JPY (before kp_part1)` → `0.97 JPY`、Part 1=0.1069円)→`study_text/`保存。a2は対象外(今回`--level b1b`のみ)。scaffold全体の実費0.97円。
- `--stage study_text`(1回目): signature一致で**API 0・reused=true**(`X_study_text_stdout.txt`)。
- `--stage study_text`(再生成、保存済みを削除して実行): 1 call、0.0875円、stageタグ=`kp_part1`(`X_study_text_regen_stdout.txt`、`X_raw_usage_log.jsonl`)。→`X_kp_general_explanations.json`は再生成結果。1回目の保存=`X_kp_general_explanations_run1_scaffold.json`。
### 2-2 実測値(`X_kp_general_explanations.json`)
model=gpt-6-luna、process=KEY_PHRASE_GENERAL_EXPLANATION、prompt_template_sha256=Zと同一、prompt_sha256=`535a5a34…`、input=`["send someone's mind off track","on the dull side","spark curiosity"]`、signature=`ac3b301efe5877b7`、retried_for_parse=false、input 689 / output 956(reasoning 456) tokens、9.7秒、0.0875円(scaffold内の1回目は12.3秒・0.1069円)。
### 2-3 出力
`X_part1_vocabulary_expressions.md`(.json同階層)。`translation_status: PENDING_USER_DECISION`。player.htmlへの描画は判断記録なしのため行わない(§4)。

## 3. M2(使う側のfail-closed確認)・M1・失敗系のtest証跡
全て`part1_wiring_evidence_01/tests_run_final.txt`(`pytest -v`の結果、**64 passed**)。主なtest:
| 観点 | test(`er003_kp_general_explanation_01_runner_integration_test_01.py`) |
|---|---|
| Z: KP確定後・TTS前に`kp_part1_b1b`、provenance entry、TTS未着手 | `ZPart1Tests::test_kp_stage_generates_part1_after_kp_before_tts_with_provenance` |
| Z: resumeでreuse(API 0) | `test_resume_reuses_without_new_call` |
| Z: 失敗=技術retry1回→fail-closed→TTS未着手・空欄続行なし・次コマンド付きSTOP | `test_failure_is_fail_closed_before_tts_with_next_command` |
| Z: mockでhook無し=実APIへ出さずSTOP(必須6) | `test_mock_without_hook_stops_without_real_api` |
| **M2** Z: 欠落/signature不一致で`load_level_inputs`・`stage_pages`・`--stage tts_b1b`がSTOP(次コマンド付き)、a2は対象外 | `test_tts_and_pages_entrances_stop_when_part1_missing_or_stale` |
| Z: KP表現変更→`kp_expl_b1b`停止→`kp_part1_b1b`停止の2段再生成と各次コマンド(必須9) | `test_kp_expression_change_needs_two_step_regeneration_with_hints` |
| **M3(ii)** 判断記録なし→ページ描画なし・`build_pages`に`study_html`を渡さない・index.htmlが従来出力とバイト同一・`study_text/`は保存 | `test_pages_do_not_render_study_block_without_decision_record_and_are_byte_identical`、`test_stage_pages_does_not_pass_study_html_without_decision_record` |
| 判断記録あり(T2)→Advanced節のみ描画・標準適合check PASS・Standard非表示 | `test_pages_render_advanced_only_study_block_after_decision_and_pass_standard_check` |
| T1記録で訳が未生成→描画せずSTOP | `test_t1_record_without_translations_stops_pages` |
| X: b1bのみ・a2は呼ばない・保存 | `XPart1ScaffoldTests::test_scaffold_runs_part1_only_for_b1b_after_kp_pass_and_saves` |
| X: 入力にgloss/引用文/display_phraseが無い | `test_input_never_contains_gloss_quote_or_display_phrase` |
| **M1** X: Part 1失敗は専用marker`kp_part1_failed.json`、`kp_stage_failed.json`は作らない、案内=`--stage study_text`、scaffold再実行非推奨、rc=3、tts/assembleも停止 | `test_part1_failure_uses_dedicated_marker_not_kp_failure`、`XPart1MainTests::test_scaffold_part1_failure_rc3_message_points_to_study_text_not_scaffold_and_blocks_tts` |
| M1: `--stage study_text`でKP再選定なしに復旧→marker削除→再実行はAPI 0・保存済み不変 | `test_study_text_stage_recovers_without_scaffold_rerun_then_marker_removed` |
| M1: study_text前提(KP失敗marker/KP成果物なしでSTOP) | `test_study_text_stage_requires_kp_pass_no_kp_failed_marker` |
| **M2** X: tts/assemble/playerの入口で欠落・STALEをSTOP(次コマンド付き) | `test_tts_assemble_player_entrances_stop_when_part1_missing_or_stale` |
| X: 表現変更で自動再生成 | `test_x_regenerates_automatically_when_expression_changes_via_study_text` |
| X: player描画は判断記録なしで空・従来html不変 / T2で描画 | `test_player_has_no_study_block_without_decision_and_default_html_is_unchanged`、`test_player_renders_study_block_in_advanced_section_after_decision` |
| 他Familyで呼ばれない・旧KPは入力拒否(M4) | `OtherFamiliesUnchangedTests` |
module単体(`er003_kp_general_explanation_01_test_01.py` 40件): Prompt byte一致(Trial-04 3作品)、実出力6件のparse(括弧付き見出し・曲がったアポストロフィ)、実データ1,792件のused_form全通過、入力隔離、signature、retry上限、model不一致STOP、audit、routing、組立5項、逐語assert、描画停止(環境変数・引数・不正記録で有効化されない)。

## 4. 描画停止の確認(M3 (ii))
- `docs/pm/decisions/part1_translation_decision.json`は**存在しない**(`translation_decision_record()`=None、`study_text_render_enabled()`=False、`render_html_block(rows)`=空文字を実行確認)。環境変数`STUDY_TEXT_RENDER_ENABLED`等を設定しても有効化されない(test)。
- 有効化手順(Fable): ユーザーのT1/T2判断後、同ファイルを`{"decision":"T1"|"T2","source":"<ユーザー原文path>","decided_at":"<日時>"}`で作成してcommit。T2=訳欄なしで描画。T1=訳call未実装のため全行`source_sentence_ja`が揃うまで描画せずSTOP(T1採用時は訳callの実装委任が先に必要)。

## 5. 既存仕様との整合・撤去
旧Part 1生成コード/Promptは存在せず撤去対象0(PART1_WIRING_SPEC_CHECK_01)。`kp_expl_b1b`(音声用英語解説)は無変更で並存。fixture更新(旧strategy_l相当のmock KPに`fulltext_source_ref`を付与、解説sig期待値を実装どおり`explanation_phrase`へ、X assemble mainのM2確認を直交test内で無効化)は、Production KPが全て全文選定でありPart 1が厳格入力を要求するための追随で、検査の緩和ではない。
