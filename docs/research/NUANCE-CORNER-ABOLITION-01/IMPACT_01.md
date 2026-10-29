# IMPACT_01 現行ニュアンス解説コーナー廃止の影響調査(NUANCE-CORNER-ABOLITION-01 委任_01、2026-10-30、API 0・Production code未編集)

原文=`docs/pm/delegation_log/2026-10-30_NUANCE-CORNER-ABOLITION-01_USER.md`。調査はgit管理下の`*.py/*.js/*.html/*.md`の`nuance|ニュアンス`全Grepに基づく(`_output`配下のrun成果物・`.claude/worktrees`・docs/research配下のTrial/evidence toolは別掲)。

**判別注意(Dangling Grepで誤検出しやすいが廃止対象外)**: (a)文法解説の見出し`意味・ニュアンス・表現効果`(`er120_part2_grammar_production_01.py:169-170` `EXPLANATION_HEADINGS/REQUIRED`)=文法Part 2の必須節、維持。(b)Family Y Writer/Judgeの`(nuance)`=「立場の中の迷い」の意味の英単語(`er012_b_family_voices_writer_generic_01.py:283,633,961,1039,1203`、`er121_family_y_text_core_01.py:404`、`er110_family_y_text_trial_01.py:464`)、維持。(c)`er009_n1_point_role_planning_11.py:64`・`er015_vocab_abcd_strict_exception_trial_01.py:272,282`・`er003_v1_cefr_direct_01_generate.py:137`・`er052_open233_self_recovery_flow_runner_01.py:2995,3575`(`nuance_only`)等の一般語、維持。

## 0. 設計を決める3つの事実
1. **既存のLEGACY経路(`nuance_spec.json`が無い)が「生成0・HR待機0・表示0・期待ブロック0」を既に全工程で実現している**(`er134_nuance_explanation_01.py:898-913 ensure_spec`、`n1_stage`のLEGACY即return、`finalize_stage`のNone返却、`er120_part2_wiring_01.py:462-466`)。廃止=この経路を唯一の経路にすること(新しい分岐・flagを作らない)。
2. **公開済み・完成承認済み記事でニュアンスが表示されているものは0件**。`user_test/*/enduser/data/article.json`のnuance件数: 月(family_x_moon_shrinking_reselect_01)=std0/adv0、再配達料(family_y_production_redelivery_fee_03)=0/0、メロス(family_z_melos_kphr_evidence_r3)=0/0、藪の中(family_z_in_a_grove_01、不採用)=0/0。**表示を含むのはY姓記事(`family_y_production_surname_choice_01`、最終完成承認保留の未承認候補)のみ**(article.json std1/adv1、`index.html`の`<h3>ニュアンス解説</h3>`が2個)。よって「過去公開物への遡及撤去」というユーザー判断事項は実在しない。論点はY姓候補ページの再生成(本文・音声不変)だけ。
3. **specを持つ進行中runは、Family X 4記事(run_fx4_01、HR待ち)とY姓(run_02、確定済み)**。雪女(Z)は新規run=KP review新規作成時にspecが発行されるので、廃止実装より先にKP stageへ進むと約¥0.47とHR項目2が発生する(スケジューリング論点)。

## 1. 領域別 影響表
### 1-A 生成(LLM呼出)
| 対象 | file:line | 内容 | 処置 |
|---|---|---|---|
| 共通核 | `er134_nuance_explanation_01.py`(1177行): 定数:34-67、PROMPT_GEN:90、PROMPT_JUDGE:167、`build_inputs`:319、`structural_check`:423、`quote_check`:477、`generate_candidate`:660、`judge_overlap`:731、`decide`:758、`run_candidate`:848、`ensure_spec`:898、`candidate_stage`:933、`n1_stage`:1052、`retry_failed_candidate`、`finalize_stage`:1118、`render_request_md` | N0 spec発行/N1候補生成+重複判定/N3確定 | **撤去**(ファイル削除) |
| ルーティング | `er006_model_routing_contract_01.py:138-141` `NUANCE_EXPLANATION`/`NUANCE_OVERLAP_JUDGE` | process登録 | 撤去(依存testの列挙も更新: `er009_n1_routing_governance_10_pricing_table_open251_test.py:12`、`er053_cost_aggregate_01_test_01.py:76`、`er054_family_z_story_pool_trial_02_test_01.py:37`) |
| Xランナー | `er019_family_x_audio_production_runner_01.py`:793-811(`run_nuance_candidates_x`/`finalize_nuance_x`)、:925(`nuance_call_fn/nuance_judge_fn/nuance_enabled`引数)、:1021-1067(N1呼出・`result[level]["nuance"]`・`nuance_pending`)、:3951(`_nz_pend`=rc=4待機に載せる)、:4110-4132(player入口finalize・`compose_page_html(…nuance=…)`) | 呼出し | 撤去 |
| Yランナー | `er121_family_y_runner_01.py`:35(`STAGE_EST_JPY["nuance"]`)、:594-619(`_nuance_cand_step`/`_assert_nuance_final`)、:659-663(N1呼出・pending)、:1061-1102(`_blocks_in_page_order`のnuance、`count_nuance_blocks`==期待、`FAMILY_Y_NUANCE_OUTPUT_MISMATCH`)、:1325・1336(stage_pagesのfinalize/compose) | 呼出し・検査 | 撤去(page検査は「ニュアンスブロック0」ガードへ置換) |
| Zランナー | `er026_family_z_fiction_production_runner_01.py`:1238(`E2E_STAGE_EST_JPY["nuance"]`)、:1897-1929(期待数・`FAMILY_Z_NUANCE_OUTPUT_MISMATCH`・dev detail pageにニュアンスが載らない検査)、:2233-2258(`_nuance_cand_step`/`_assert_nuance_final`)、:2307-2311(N1呼出)、:2729-2731(compose) | 同上 | 撤去。**雪女がplan段実行中=runner挙動を変える編集の時期はDESIGN §7** |
| 費用上限見積 | er121:35 / er026:1238 | `nuance: 1.0`円/level/stage | 撤去(E2E予算見積が約¥2/記事減) |

### 1-B Human Review
| 対象 | file:line | 処置 |
|---|---|---|
| フォームdata出力 | `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`:12,238-243,248,276-281,321,352-360(`--nuance-study-dir`、`nuance_spec/nuance/nuance_note_ja`出力。※Production exporter) | 引数・出力撤去 |
| フォームdata生成(wiring) | `er120_part2_wiring_01.py:553-600 form_nuance_bundle` | 撤去 |
| V3フォームUI | `user_test/selection_form_v3/index.html:10,33,81,84-104,134`(`renderNuance`、採否ラジオ、未決定ブロック) | 撤去 |
| フォーム論理 | `user_test/selection_form_v3/form_logic.js`:53-75(`hasNuanceSpec/nuanceOf/nuanceDecision/chooseNuance/nuanceConflicts/nuanceBlocked/nuanceBodyText`)、:219-223(structured: `schema_minor=2`+`selection.nuance`)、:294-302(AIF2 `n8`)、:328-340(readable `【ニュアンス全文】`)、:374-380(検査)、:409(export) | 撤去(AIF1のみ) |
| フォームdata(実データ) | `user_test/selection_form_v3/data/{ai_chat_sponsored_persuasion,jwst_mystery_emission_line,meta_waddle_world,untidiness_family_resource}__{a2,b1b}__prod.json`(8ファイル、`nuance_spec`+候補本文を含む=Family X 4記事HR待ち) | 再出力(API 0)でニュアンス欄を除去。`nuance_spec`無し=従来AIF1 |
| 取込み(Python) | `er128_kp_confirmed_content_01.py`:63-73(定数・ファイル名)、:301-302(`prev["nuance"]`引継ぎ)、:525-572(`_nuance_problems`→確定検証に組込み)、:767-804(`_nuance_quotes`=revise/rebind時の採用引用保全)、:1478・1517(`cmd_from_form`のnuance検証・sidecar書込)、:1667-1710(`nuance_id_of/pool_identity_sha/presented_ids/_nuance_text_sha_of_grammar/nuance_redundancy_alarms`)、:1712-1870(`_validate_form_nuance/_archive_prior_nuance_files/_write_nuance_sidecar/nuance_state/previous_nuance_decision/guard_nuance`)、:1961-2100(CLI本体`cmd_nuance_show/select/issue_spec`) | 撤去。**既存の確定record(`rec["nuance"]`あり、Y姓run_02)は読取互換=存在しても無視**(DESIGN §3) |
| readable復元 | `er128_form_readable_restore_01.py`:52-53,117-141(`has_nuance_spec/nuance_of/nuance_decision/nuance_body_text/nuance_n8`)、:168(`make_code`のnuance_sel)、:555-590(payload schema_minor=2) | 撤去(AIF2コードは明示エラーで拒否) |
| CLI | `er119_kp_human_review_cli_01.py`:24-28,150-162,211-214,238-253(`nuance-show/select/issue-spec/retry`) | 撤去 |
| 待機(rc=4)の統合依頼書 | `er119_kp_wiring_01.py:114,135-141`(pending kind=`nuance`) | kind分岐撤去 |
| 重複アラーム表示 | `er119_kp_human_review_01.py`:512(コメント)、:1166-1250(`NUANCE_ALARM_FILENAME`/`_alarm_nuance_candidates`、`nuance`列、`ニュアンス解説 x …`行) | ニュアンス列のみ撤去(KP/Word/追加解説/本文意味アラームは維持=HR-SELECTION-FLOW仕様②のKP側は不変) |
| X 4記事HR作業tools | `docs/research/FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01/tools/{gen_hr.py,form_node_check.js,export_form.sh}` | 次回HR再出力時に`--nuance-study-dir`を外す(docs配下の作業tool) |

### 1-C 表示・検査
| 対象 | file:line | 処置 |
|---|---|---|
| 共通HTML builder | `er120_part2_grammar_production_01.py`:164-166(`NUANCE_HEADING/RESULT_FILENAME/ADOPTED`)、:1497-1595(`NUANCE_REQUIRED_FIELDS`、`nuance_is_adopted`、`expected_nuance_blocks`、`nuance_candidate_of`、`nuance_text_fields`、`render_nuance_html_block`、`compose_study_html(…, nuance)`、`count_nuance_blocks`、`verify_nuance_in_section`) | `render/compose引数/is_adopted/fields/required/expected`撤去。**`count_nuance_blocks`+`NUANCE_HEADING`は「ニュアンス節が出ていないこと」のガードとして最小限残す**(逆流防止) |
| 表示配線 | `er120_part2_wiring_01.py`:439-506(`_LOAD_NUANCE`/`nuance_for_display`/`finalize_nuance`/`expected_blocks`のnuance/`verify_outputs`のnuance引数)、:624-628(`compose_page_html(…, *, nuance)`=必須keyword R-6)、:658-659 | 撤去(`nuance`引数削除。`expected_blocks`は`nuance_blocks:0`固定) |
| X公開ページ/試聴 | `er019_family_x_listening_page_01.py:238`(`p2w.verify_outputs`)、`er120_part2_wiring_01.py:636-659 public_study_html` | 引数変更に追随のみ |
| End User adapter | `er135_enduser_page_01.py`:291,841-843,904(schema `nuance`),1035-1043(`ENDUSER_STUDY_MISMATCH`のnuance件数),1256; `er135_enduser_rules_01.py:43`(見出し→kind); `er135_enduser_page_verify_01.py`:197,215-234(`vocab_nuance_quotes_have_bold`含むcorner検査),350 | schemaからnuance撤去。dev index.htmlに「ニュアンス解説」節があればSTOP(廃止ガード)。corner検査はvocab/grammarのみ |
| End Userアセット | `enduser_page_assets/rev01-e/app.js`:105-108,174-181、`enduser_page_assets/derive_assets_01.py`:62-69(J9-J11) | 撤去。DEV `user_test/dev_enduser_page_01/{app.js,style.css,data/*.json}`(仮データ)の扱いはDESIGN §6 |
| 公開済みenduserスナップショット | `user_test/{family_x_moon_shrinking_reselect_01,family_y_production_redelivery_fee_03,family_y_production_surname_choice_01,family_z_in_a_grove_01,family_z_melos_kphr_evidence_r3}/enduser/app.js`(各`NUANCE`分岐5行) | 過去成果物=**変更しない**(データ0件の分岐は不活性)。Y姓のみ再生成対象 |

### 1-D 記録・resume・費用
| 対象 | file:line | 処置 |
|---|---|---|
| runの記録 | run直下 `study_text/nuance_spec.json`/`nuance_candidate.json`/`nuance_failed.json`/`confirmed_nuance.json`/`nuance_result.json`/`nuance_redundancy_alarm.json`、確定record `rec["nuance"]`(`er128:301`) | **読取互換: 存在しても読まない・検査しない・表示しない**。既存ファイルは削除しない |
| manifest/article.json | `user_test/*/enduser/data/article.json`の`levels.*.nuance`配列 | スキーマから撤去。既存5ファイルは過去成果物として不変(Y姓のみ再生成) |
| resume summary | er121:660 `summary["nuance_cand_{lv}"]`、er019:1042・1067 `result[level]["nuance"]` | キー自体が出なくなる。旧summaryの当該キーは読まれない |
| 費用 | `nuance_candidate.json.usage.cost_jpy`実測: X4記事8level=¥0.20-0.33(平均0.23)、Y姓2level=¥0.17/0.21(gpt-6-luna、生成1回/level)。+判定(¥0.02-0.03/level見込み)=約¥0.47/記事セット | 削減約¥0.47/記事(量産単価70円の約0.7%)+E2E予算見積約¥2/記事 |

### 1-E test・fixture
| 対象 | 規模 | 処置 |
|---|---|---|
| ニュアンス専用test | `er134_nuance_explanation_01_test_01.py`(694行/45件)、`er134_nuance_runner_wiring_test_01.py`(586/31)、`er134_nuance_y_mock_e2e_test_01.py`(237/4)、`er134_nuance_z_mock_e2e_test_01.py`(181/4)、`er128_nuance_hr_test_01.py`(623/38)、`er120_nuance_display_test_01.py`(300/12) | 撤去(計約2,600行・134件)。代わりに「廃止ガード」test新設(DESIGN §8) |
| 混在test(nuance行のみ編集) | `er135_enduser_page_test_01.py`(16行)、`er121_y_highlight_wiring_test_01.py`(10)、`er119_grammar_review_test_01.py`(4)、`er052_open233_self_recovery_flow_runner_01_test_01.py`(3、語の用途要確認)、`er003_kp_general_explanation_01_runner_integration_test_01.py`(2)、`er026_z_highlight_wiring_test_01.py`(2)、`er120_part2_grammar_production_01_test_01.py`(2)、`er119_hr_selection_flow_test_01.py`(1)、`er119_redundancy_alarm_display_test_01.py`(1)、`er120_public_study_html_level_test_01.py`(1) | 該当assertのみ編集 |
| 隔離test | `er119_isolation_test_01.py:43`(A/B/C非接触対象に`er134_nuance_explanation_01.py`) | er134削除に伴い行削除 |

### 1-F Trial/evidence/docs(Production外・維持)
`docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/**`・`NUANCE-QUALITY-IMPROVEMENT-TRIAL-01/**`・`HR-SELECTION-FLOW-*/tools/nuance_evidence_hrq3a_01.py`・`user_test/nuance_quality_trial_01/`・`tools/osf01_*.py`/`osf02_*`(One Step Furtherが現行ニュアンスを比較参照=Trial専用)・`user_test/one_step_further_trial_01/`は**変更しない**(過去Trial記録・並行Worker(OSF)のファイル)。docs/research配下のnuance参照tool(`issue_nuance_spec_surname_01.py`等)は歴史記録として残置し、廃止後は実行不能でも害なし。

## 2. 公開物・承認状態一覧
| 公開ページ | ニュアンス表示 | 承認状態 | 処置案 |
|---|---|---|---|
| 月(family_x_moon_shrinking_reselect_01) | 0件 | APPROVED_FOR_PRODUCTION(UDR #217) | 不変 |
| メロス(family_z_melos_kphr_evidence_r3 ほか) | 0件 | 完成承認済み | 不変 |
| 再配達料(family_y_production_redelivery_fee_03) | 0件 | 完成承認済み | 不変 |
| 藪の中(family_z_in_a_grove_01) | 0件 | 不採用・お蔵入り(UDR #226) | 不変 |
| **Y姓(family_y_production_surname_choice_01)** | **std1/adv1、index.htmlにブロック2個** | **未承認候補・最終完成承認保留(OSF採否確定まで)** | 撤去実装後に`--stage pages`再実行でブロック0へ(本文・音声不変、API 0)。承認保留中だが「ニュアンス暫定反映は廃止対象」(OPEN-598追記)なので再生成の可否はFable判断 |
| X 4記事 | フォームのみ(HR待ち。公開ページ未生成) | HR待ち | フォームdata再出力(API 0)、ニュアンス欄なしで再提示 |
| 雪女(Z) | 未生成 | 制作中 | 廃止実装後にKP stageへ(さもなくば1記事約¥0.47+HR2項目) |
| dev_enduser_page_01(DEV仮データ) | 仮データ | DEV専用 | DESIGN §6 |

## 3. 削減見込み
費用: 約¥0.47/記事セット(生成+判定、gpt-6-luna)+E2E予算見積約¥2/記事。HR項目: 1記事あたり最大2件(Std/Adv各1)減。検査: N1(構造・引用・重複判定)・N3確定・page_verifyの期待数/順序/dev detail載り検査・End User corner検査・HR validators・重複アラーム(ニュアンス分)・AIF2照合。コード: 本体1,177行+配線約700行(推定)+test約2,600行。時間: LLM呼出2回/level+HR判断1項目/level(実測は委任_02で収集)。
