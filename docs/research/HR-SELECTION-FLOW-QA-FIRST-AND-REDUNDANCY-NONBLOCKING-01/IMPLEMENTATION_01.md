# IMPLEMENTATION_01 実装記録(HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01 委任_02r)

実装日2026-10-29。API 0(testはすべてmock。実LLM呼出なし・費用0)。設計=WIRING_DESIGN_01.md、Opus条件Aレビュー=OPUS_REVIEW_01.md(逐語)、Fable判断(M1-M9回答)に従う。
仕様①②はユーザー`APPROVED_FOR_PRODUCTION`(原文§1)のため新flagなし(11-7の限定例外は不使用)。X/Y/Z共通経路のみ(`er119_kp_wiring_01.run_kp_with_review` -> `er119_kp_human_review_01.ensure_kp_review` -> `er119_kp_candidates_01.generate_candidates`)。旧経路A/B/C・凍結ラインは無変更。範囲外(別Worker担当)のer120(OPEN-591第2段)・user_test/dev_enduser_page_01は触っていない。form_logic.jsは変更不要(Production dataに仮訳/未確定候補が出なくなるため)。

## 1. 変更file:line
| file | 内容 |
|---|---|
| `er119_kp_human_review_01.py:506-640` | 提示集合の唯一の定義: `PRESENTABLE_FILTER_VERSION`/`presentation_blockers`(:513)/`presentable_candidates`(:549)/`excluded_from_presentation`(:555)。仕様②: `redundancy_alarms`(:572、③含む)/`final_qa_to_alarm`(:607) |
| 同:705 | `auto_select`はKPのみ`presentable_candidates`を通す(文法kindは別構造=対象外) |
| 同:771-,848-851 | `op_select(meaning_display_ids=)`: 重複はアラームとして`review.redundancy_alarms`+history`redundancy_alarm`に記録(拒否しない)。`validate_selection`のpair検査は撤去(他の候補単位検査は不変) |
| 同:1115-1120 | 判定不能(INVALID等)は従来どおり`KpReviewError`(fail-closed)。メッセージに「重複の判定結果ではなく判定器の故障」「resumeで判定のみ再試行」を明記 |
| 同:1120-1160 | `redundancy_telemetry`/`write_alarm_file_safe`(`<kp_dir>/redundancy_alarm.json`。0件でも書く・書込失敗はwarningのみ) |
| 同:1182-1215 | `finalize_kp`: キャッシュ条件=key一致 and (PASS or (ALARM and review!=AUTO))(M5)。人間選定の確定集合NGは差戻さず`final_qa_to_alarm`で保存して続行(`_run_final_qa`は不変)。AUTO分岐(繰上げ・枯渇STOP)不変 |
| 同:1247-1248 | `kp_selection_final.json`に`redundancy_alarms`/`redundancy_telemetry` |
| 同:1455-,1499 | `render_request_md`は提示可能な候補のみ表に載せ、除外した候補は「提示から除外した候補」節に理由付きで表示。旧旗文言(QA FAIL/gloss HR待ちの`--accept-qa-fail`案内)は撤去、重複は「アラームのみ・選んでも止まりません」 |
| 同(ensure_kp_review) | finalizeの`except KpReviewPending`(死にコード)撤去(M7) |
| `er119_kp_candidates_01.py:258-303` | `_gate_chain`: 候補組立後に`rv.presentation_blockers`で除外(`dropped`の`canonicalization_qa`/`gloss_unresolved`、`blocker_codes`付き)。Gate除外として既存の補完(backfill)が代替を補う(新しいretry/上限なし)。stagesに`presentable_filter`telemetry |
| 同:506,513-,707 | doc`presentable_filter`(version/checked/canonicalization_qa_dropped/gloss_unresolved_dropped/dropped_by_code/presentable/n_candidates)。`candidate_doc_from_items`(mock/hook専用)は`qa_overall_status`未設定のitemをPASS受理済みとして扱う(正式経路は`_gate_chain`) |
| `er128_kp_confirmed_content_01.py:1407-1413,1484,1502-1503,1519` | `cmd_from_form(attestation=, origin_extra=)`(既定None=従来どおり)。`op_select(meaning_display_ids=cat3)`。戻り値に`redundancy_alarms`。`origin.transcription`に由来 |
| 同:694-696 | `on_final_redundancy_ng`/`raise_issue_nowait`/`STATE_RECONFIRM`/G1 RECONFIRM ISSUE/`auto_adopted_after_reconfirm_required`を撤去(M7、ディスク上reconfirm_requiredは0件) |
| `er119_kp_wiring_01.py:43` | `_shape_final`: KP stage通過時に`redundancy_alarm.json`へ`reached_next_stage=runner_kp_stage_passed`を記録 |
| `er134_nuance_explanation_01.py:284-285` | `presented_pool`は`rv.presentable_candidates`の後にcap(M2、exporterとparity) |
| `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py:71-77,249-250,289-` | フォームdataは`rv.presentable_candidates`のみ。除外は`data_warnings[presentation_excluded]`に記録(除外0件のdocはキー自体なし=従来とバイト同一)。QA不合格/意味確認待ちの旧注記は到達不能のため撤去 |
| `er119_kp_human_review_cli_01.py` | `select`出力に`redundancy_alarms`。`--accept-qa-fail`のhelpを「旧doc専用」と明記(残置) |
| `docs/research/HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01/tools/apply_user_decision_surname_choice_01.py` | M4の使い捨てtool(run_02 a2・`old-fashioned about it`->`old-fashioned`限定)。**適用は委任_03**(下記6) |
| test | `er119_hr_selection_flow_test_01.py`(新規43+1 test)、`er119_test_support_01.py`(`make_legacy_flagged`)、`er119_kp_backfill_golden_01.py`(`--write <scenario>`、追記専用keyのstrip)、他は2の表 |

## 2. 撤去・反転したtest(4件+関連)の識別子と理由
| test | 理由 |
|---|---|
| `er119_kp_human_review_01_test_01.test_final_redundancy_ng_on_human_selection_returns_to_pending_M8` -> `..._is_alarm_and_finalizes_spec2` | 旧期待値=人間選定の確定集合NGをPENDINGへ差戻し。仕様②が置換(アラームのみ・確定続行・選定維持) |
| 同`test_select_validation_errors`(重複pair拒否の1ブロックを撤去) | 重複選択の拒否は仕様②で廃止。他の検証エラー(件数/KP⊂vocab/NG理由/選択とNGの矛盾)は維持。重複受理は`TestRedundancyAlarms`/`test_u9...` |
| `er128_kp_confirmed_content_test_01.test_redundancy_ng_marks_reconfirm_required_and_allows_user_reselect` -> `test_redundancy_ng_is_alarm_only_record_stays_live_and_finalizes_spec2` | 旧=確定レコードをreconfirm_requiredへ・ISSUE停止。撤去(M7) |
| `er119_kp_human_review_01_test_01.test_review_required_item_gets_qa_fail_flag_and_not_auto`/`test_gloss_hr_pending_flag` -> `..._is_excluded_before_presentation_spec1`/`..._M1` | 旧=QA FAIL/gloss HR待ちを旗付きで提示。仕様①+M1で除外 |
| `er119_kp_backfill_test_01.test_rescued_not_auto_leg_removed_on_TBF18c` -> `test_rescued_unverified_excluded_not_presented_and_no_outer_retry_M8`、`er119_kp_rescue_wiring_test_01.test_w6_m3_rescued_but_not_auto_triggers_outer_retry_without_f1_exclusion` -> `..._is_excluded_and_counts_as_gate_drop_for_outer_retry_spec1` | 旧=未検査の救済候補をHR限定で提示。M8で除外(fail-closed) |
| goldenを意図的に更新(`docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/golden_03/` s04/s06/s07/s10)、`ON_EQUAL_SCENARIOS`からs06/s07を除外、`test_call1_portion_equals_legacy_...`のs06/s07を新test`test_qa_fail_and_gloss_hr_candidates_excluded_before_presentation_spec1`へ | 仕様①でQA不合格/gloss HR待ち/未検査救済の候補が除外になった結果(E>0となり補完発動)。差分はこれらの候補の除外のみ(git diff参照)。`--write`は指定scenarioのみ再生成 |
| `er119_kp_human_review_cli_01_test_01.test_resolve_gloss_cli`、`test_qa_fail_requires_explicit_accept`、`test_gloss_hr_pending_not_selectable_until_resolved`、`test_auto_skips_qa_fail_and_redundant_pair`、`test_auto_zero_eligible_stops` | 旧doc(旗付き保存済み)を`make_legacy_flagged`で再現して継続(旧doc救済・安全網・AUTO枯渇STOPの残置を固定)。`test_all_candidates_qa_fail_at_generation_fails_closed...`を追加 |
| `er134_nuance_explanation_01_test_01._cand`、`er128_kp_confirmed_content_slot23_test_01`のmock文言 | fixtureを提示可能候補(QA PASS・gloss ALIGNED)に。重複文言を期待するmockは実在する検査文言へ |

## 3. M1〜M9・D節 対応表
| 項目 | 対応 | 証拠 |
|---|---|---|
| M1 単独で確定できる提示集合 | `presentation_blockers`: human_selectable and not qa_fail and not gloss_hr_pending and gloss official。外れた候補は生成時に`dropped`し補完 | `TestPresentationBlockers`、性質test`test_property_every_presentable_candidate_passes_candidate_level_checks_when_selected_alone`/`..._freshly_generated_mixed_doc` |
| M2 er134 pool | `presented_pool`も同関数(cap後ではなくcap前にフィルタ=除外が枠を消費しない)。parity維持 | `test_m2_er134_presented_pool_parity...`、棚卸し4-2 |
| M3 cap | 上限(フレーズ7・単語5)=AIが人間へ提示する候補poolの上限(CURRENT_SPEC.md:2039-2040「候補上限=12」、DESIGN_01.md:57「UI上限=Production slotと別層」)。確定集合の規則は`SLOT_RULES`(er119_kp_human_review_01.py:63-66 kp<=3/vocab<=5)。toolは確定集合を直接記録しcapを再計算しない。確定集合の規則に反しない(①adopted/relative+old-fashioned=3件、①+②=5件) | `test_confirm_dry_run_replaces_only_the_one_item...`(`perhaps`が残る) |
| M4 差替えtool | 6節 | `TestSurnameChoiceTool`(9 test) |
| M5 `_run_final_qa`不変 | 人間選定分岐でのみALARM形へ変換。キャッシュ=key一致 and (PASS or (ALARM and not AUTO)) | `test_m5_...`、`test_u11_...`、`test_u13_...` |
| M6 ③を含むアラーム | `redundancy_alarms`(cmd_from_formが`meaning_display_ids`を渡す)。確定集合QA(kp/vocab)は現状維持 | `test_u8_alarms_from_candidate_doc_include_meaning_display_slot_M6`、`test_y_adv_user_readable_confirms...` |
| M7 RECONFIRM | 棚卸し=reconfirm_requiredレコード0件(confirmed_selection.json 58件すべてstate=live、review historyに`final_redundancy_ng`0件) -> 全撤去。`except KpReviewPending`も撤去 | `TestNoDanglingAndCommonPath` |
| M8 救済未検査 | `rescue.canonicalization`ありで`qa.status!=PASS`または`gloss.status!=REALIGNED`は除外 | `test_u6_m8_...`。**棚卸し4-3の影響に注意** |
| M9 qa_overall_status欠落 | 棚卸し=正式経路の全候補にPASS/REVIEW_REQUIREDが入っている(欠落16件はsmoke_a_mockの2 docのみ) | `test_m9_normal_generation_...` |
| D1 INVALIDはfail-closed | 維持。メッセージ明示・resume再試行をtest固定 | `test_u12_...` |
| D2 backfill除外入力 | dropped句が`bf.rejected_entries`に入りbackfillの除外入力になる | `test_u2_...` |
| D4 `--accept-qa-fail` | 残置(旧doc専用)。撤去時期の判断材料=旧docで未確定のrun数(4-1) | |
| D6 AUTO | 重複回避・繰上げ・枯渇STOPは維持。**範囲外として意図的に残す既存動作**(AIの自動選定=人間選定ではない)。残課題として報告 | `test_u13_...`、`test_auto_zero_eligible_stops` |
| D7 案β | 不採用(別承認事項。再canonical化はPrompt入力が変わる) | |
| D8 掲載 | 実装済み=run監査(`redundancy_alarm.json`/`kp_selection_final.json`)・confirm/select CLI出力。**未実装(範囲外)**=user_test事後確認節・各runnerの完了報告ブロック(7節) | |
| REBOUND | 確定集合QAのキャッシュkeyは選定ID集合のみ(candidates_shaを含まない)=既存挙動のまま(変更なし) | |

## 4. 棚卸し結果(read-only)
### 4-1 候補doc109件(`**/kp_candidates.json`、round_*除く)
- `qa_overall_status`: PASS 747 / REVIEW_REQUIRED 13 / 欠落16(smoke_a_mock 2 docのmock fixtureのみ)。M9: 正式経路(通常・救済・backfill)に欠落経路なし。
- gloss gate: ALIGNED 776(全候補)。`gloss_hr_pending`=0件(M1: 正式docでの発生頻度0/776)。
- REVIEW_REQUIRED旗付き(旧doc)のdoc: melos run_kcp4_ev_z_01_s23f b1b・melos run_kprescue_ev_01 a2・tell_tale_heart x3 a2・sns_age_limit run_01 b1b・surname_choice run_02 a2。確定レコードの無い(未確定=旧doc救済が必要になり得る)のは **melos run_kprescue_ev_01 a2 / sns_age_limit run_01 b1b / surname_choice run_02 a2 の3 run**(他は確定済み=影響なし)。`--accept-qa-fail`撤去判断はこの数が0になった時点。
### 4-2 M2: ニュアンス仕様マーク
- `nuance_spec.json`はNUANCE-EXPLANATION-PRODUCTION-WIRING-01のevidence配下のみ。X/Y/Zの正式output(`er019_output`/`er026_output`/`er121_output`)には0件 -> 「ニュアンス仕様マークあり・qa_fail候補あり・未確定run」=**0件(遡及してよい)**。
### 4-3 M8(重要な影響)
- 救済(canonicalization段)候補16件のうち**11件が`NOT_REJUDGED`(error=`key_mismatch_or_invalid_fields`)**、5件がPASS。最新のY surname_choice run_02 b1b(rank1 `taking offense`、REVERT_SURFACE)もNOT_REJUDGED。M8により以後の新規生成ではこれらは除外され補完で埋まる(救済REVERT_SURFACEの約7割が提示されなくなる)。QA再判定のkey不一致の原因調査(救済の価値を保つ)は別論点 -> 8節。run_02 b1bの既存docは再生成しないため影響なし(ユーザーのAdv選定は維持される: 4節`test_y_adv_...`)。
### 4-4 M7
- `confirmed_selection.json` 58件すべて`state=live`。`reconfirm_required`/`redundancy_ng_reconfirm_required`/`final_redundancy_ng`は0件。

## 5. 撤去・残置・Dangling Grep
- 撤去: `validate_selection`のpair検査、`finalize_kp`人間選定NG->PENDING巻戻し(`final_redundancy_ng`イベント)、`ensure_kp_review`の`except KpReviewPending`、`on_final_redundancy_ng`、`raise_issue_nowait`、`STATE_RECONFIRM`、G1のRECONFIRM ISSUE、`auto_adopted_after_reconfirm_required`、依頼書/exporterの旧QA FAIL・gloss HR待ち旗文言。
- 残置(意図): `--accept-qa-fail`/`accepted_qa_fail`/`human_accepted_qa_fail`/`REVIEW_REQUIRED_HUMAN_ACCEPTED`(旧doc救済)、`flags.qa_fail`/`flags.gloss_hr_pending`/`flags.redundant_with`(スキーマ互換・旗)、`REDUNDANCY_NG`判定そのもの、AUTOの重複回避・繰上げ・枯渇STOP、`op_resolve_gloss`(旧doc救済)、旧経路A/B/C(`er003_v1_n3_01_scaffold_generate.py`の`REDUNDANCY_NG` retry、27-7により対象外・`TestNoDanglingAndCommonPath`で無変更を固定)。
- Grep(照合リスト `STATE_RECONFIRM`・`reconfirm_required`・`raise_issue_nowait`・`on_final_redundancy_ng`・`REDUNDANCY_NG`・旧pair検査名)の結果は`TestNoDanglingAndCommonPath`で固定し、末尾(9節)に実行結果を記録。

## 6. M4 差替えtool(`tools/apply_user_decision_surname_choice_01.py`)
- 範囲固定: run_02 / level=a2 / 旧句`old-fashioned about it` / 新句`old-fashioned` / user-refは原文file。任意文字列・他記事・他level・PENDING以外・確定レコード有りは拒否。
- `requalify`: 全ゲート再適用(`kc.validate_canonicalization_item`全文選定用引数+左端guard / 出典文連続一致 / `cmu.canonicalized_check` / 記号 / Human NG / `ft._recompute_item_fields` / word_count・kind / `er125.force_gloss_realign` / `er125.qa_rejudge` 12項目すべてPASS / 候補全体Redundancy QA再実行[redundant_with再計算、旧結果は`requalify_provenance`に保存] / `rv.presentation_blockers`が空)。1つでも不合格なら**何も書かず**ToolRefused(ユーザー意図と不一致=Fableへ報告。再選定はしない)。review_lock・candidates_sha・history(`requalify_user_decision`、user_ref・原文節)更新。
- `confirm`: 旧`readable_a2.txt`を`restore`(d6はgit履歴から復元)-> rank5のterm/kind/gloss/status**だけ**差替え(差分を列挙し他に差があれば拒否)-> `cmd_from_form`(同じ内部関数・同じ検査、`attestation="user_instruction_transcription"`、actor=ACTOR_USER、`origin.transcription`に旧readable sha・旧新candidates_sha・差分・原文節)。capは再計算しない(`form_data_regenerated=false`/`cap_recomputed=false`を記録)。
- 検証(本委任): 実run_02に対するdry-run(`requalify --dry-run`)は決定論ゲートPASS(出力: `gates`全PASS)。複製run上でfake LLMによる全工程(requalify+confirm+attestation記録)をtest。**実LLM(gloss整合/QA再判定/Redundancy QA)は未実行**(委任_03)。
- 費用見込み(委任_03): gloss整合1 call+QA再判定1 call+候補全体Redundancy QA 1 call+(finalizeのKP/vocab集合Redundancy QA)=約¥3-6。

## 7. telemetry仕様
- 候補生成ごと: doc`presentable_filter`={version, checked(初回+補完で品質検査した件数), canonicalization_qa_dropped, gloss_unresolved_dropped, dropped_by_code, presentable, n_candidates}。各attemptのstagesにも`presentable_filter`/`backfill_presentable_filter`。0件でも記録。
- finalizeごと: `kp_selection_final.json.redundancy_telemetry`={final_qa_status, final_qa_alarm_pairs, candidate_qa_alarm_pairs, alarm_count, nonblocking=true, review_status, filter_version}。`redundancy_alarm.json.telemetry.reached_next_stage`(=KP stageを通過しrunnerへ戻った時点で`runner_kp_stage_passed`)。0件でも書く。
- 後続stage(gate/assemble/音声)到達の証跡はrunnerのstage logで取得(委任_03のcopy-run evidence)。

## 8. 委任_03 申し送り
1. **evidence手順(X/Y/Z x Std/Adv の6組合せ、copy-run)**: 本文固定(既存run複製)・実LLMで候補生成(P7+W5'+canon+gloss+QA+Redundancy)を各1件以上 -> doc`presentable_filter`を採取(0件除外でも可)。ALARM分岐は実記事のY Adv(`readable_b1b.txt`をcopy-runで`cmd_from_readable`->finalize)で採取し、X/Zはmock redundancy_fnで代替(実装済みtestで確認済み)。費用見込み: 候補生成1 level あたり約¥2(7+5実測平均¥1.88、DESIGN_01.md:96)x 6 level-run=約¥12 + 最終Redundancy QA約¥1-2/集合=合計約¥15以内(7-7の300円以下)。実行前に`stop_scope_check`。
2. **Y Adv(b1b)**: 本物のreadable_b1b.txt(AIF1コード有効)を`confirm --from-readable`へ(フォーム再生成なし)。本委任の複製run testで、拒否されず③を含むアラーム2件が記録されることを確認済み。finalizeの最終Redundancy QA(実LLM約¥1-2/集合)でALARMを記録して続行。
3. **Y Std(a2)**: `tools/apply_user_decision_surname_choice_01.py requalify`(実LLM、約¥3)-> 成功なら`confirm --readable er121_output/.../hr/readable_a2.txt`。`requalify`がQA不合格/gloss未解決で拒否した場合=『old-fashioned』を提示可能にできない=ユーザー決定の実現不能。Fableへ報告(判断候補D相当)。
4. **未実装(本委任の範囲外)**: user_test事後確認節への重複アラーム掲載、各runner完了報告ブロックの「重複アラーム(確認用・非停止)」節 -> 別Worker編集中のuser_test/dev_enduser_page_01・runner。本委任は正本(run監査JSON)とCLI出力まで。
5. **M8の影響(4-3)**: REVERT_SURFACE救済の約7割が提示されなくなる。救済のQA再判定が`key_mismatch_or_invalid_fields`で失敗する原因の調査は救済機能(承認済み)を活かす観点で別論点(修正へ進む候補)。
6. SSOT更新(CURRENT_SPEC:1987/1995の置換追記・DECISION_LOG・OPEN_ITEMS[`--accept-qa-fail`撤去時期、AUTO枯渇STOP残置])はFable/委任_03。

## 9. テスト結果・Dangling Grep(2026-10-29実行、API 0)
実行: `PYTHONUTF8=1 .venv\Scripts\python.exe -m unittest <module>`。
- **新規** `er119_hr_selection_flow_test_01`: 44 test OK(U1-U15・I1-I3・M1/M2/M5/M6/M8/M9・性質test2本・Dangling・M4 tool 9 test[複製run上の全工程・Y Adv実readable確定]。I6=toolのkind/全ゲート/cap非再計算/不合格時no-write)。
- 反転・更新済みの既存: `er119_kp_human_review_01_test_01`(57 OK)/`_cli_`(9 OK)/`_outputs_`(7 OK)/`er119_kp_backfill_test_01`(66 OK、golden4件更新)/`er119_kp_p7w5_test_01`(31 OK)/`_e2e_`(8 OK)/`er119_kp_rescue_wiring_test_01`(15 OK)/`er119_x_wiring_test_01`(12 OK)/`er125_kp_rescue_production_test_01`(58 OK)/`er128_form_readable_restore_test_01`(55 OK)/`er128_kp_confirmed_content_02b`(34)/`_03`(2)/`_grammar_pending`(10)/`_grammar_v2`(48)/`_slot23`(25)/`er128_kp_highlight`(7)/`er128_nuance_hr`(37)/`er134_nuance_explanation_01`(45)/`er134_nuance_runner_wiring`(29)/`er134_nuance_y_mock_e2e`(4) すべてOK。他に `er019_family_x_kp_stage_fail_closed`(8)/`er019_x_highlight`(30)/`er026_z_highlight`(47)/`er121_family_y_runner_01`(54)/`er121_y_highlight`(25)/`er120_nuance_display`(11)/`er120_part2_pregen`(37)/`er120_part2_wiring_integration`(20)/`er_learning_highlight`(22)/`er003_test_kp_fulltext_wiring_runners_01`(6)/`er003_test_kp_gloss_alignment_wiring`(20) OK。
- **既存失敗(変更前HEADでも同一に失敗=本変更と無関係。baseline差分で確認)**: `er119_z_wiring_test_01.test_part1_items_follow_vocab_confirmed_five`(1)、`er119_isolation_test_01.test_only_x_z_runners_import_er119`(1)、`er119_grammar_review_test_01`(`test_grammar_files_not_tracked_dirs`、`test_public_builder_and_standard_never_call_part2`)、`er128_kp_confirmed_content_test_01.test_abc_and_shared_functions_do_not_import_er128`(`er129_lr_display_reflection_01.py`)、`er003_kp_general_explanation_01_runner_integration_test_01.test_kp_expression_change_needs_two_step_regeneration_with_hints`(HEAD版の本番codeに差し戻して同一失敗を確認)、`form1_selection_form_v3_test_01`の4件(`restore_roundtrip...`/`candidate_id_kind...`[data file数18!=10]/`kp75_form_data...`/`node_logic_suite`。HEAD版exporter等へ差し戻しても同一)、`er105_kp_fulltext_selector_01_test_01.test_no_production_file_references_er105`、`er124_kp_phrase_word5_trial_test_02.test_kp_candidate_max_untouched_by_import`(12!=8)。いずれもOPEN-588/TRACK_AC_EVIDENCE:70-76系の既知失敗または他Workerのdata変更。
- **commit前は失敗/commit後に解消するもの**: `er124_kp_phrase_word5_trial_test_02.test_production_files_not_modified_vs_head`(『Production fileがHEADから未変更』の隔離test。本変更のcommit後は変更0になり通る)。
- 追加修正したfixture: `form1_selection_form_v3_test_01.test_reason_missing_warning_only_for_p7w5_docs`の`mk`(提示可能な候補=gates.gloss=ALIGNED/item.qa_overall_status=PASS)、`er134_nuance_explanation_01_test_01._cand`、`candidate_doc_from_items`(mock/hook専用)。
- Dangling Grep(`er019_*/er026_*/er119_*/er120_*/er121_*/er125_*/er128_*/er134_*.py`・exporter・`form_logic.js`、test除く): `STATE_RECONFIRM`/`reconfirm_required`/`raise_issue_nowait`/`on_final_redundancy_ng`=er128:694-696の撤去を説明するコメントのみ(コード参照0)。`final_redundancy_ng`=`auto_advance_final_redundancy_ng`(AUTOの繰上げイベント。残置)のみ。`意味・用法が重複しています`=0件。`TestNoDanglingAndCommonPath`で固定。
