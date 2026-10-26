# TEST_PLAN_02: 確定内容の不変性 test計画 改訂版(KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02A、2026-10-27)

方針: 受入=「確定後に英語・日本語訳(表示値)・区分が不変」。全て決定論・API 0。変更試行はBLOCK/例外/拒否を期待値とし、不整合な出力を期待値としてassertしない。TEST_PLAN_01(T1〜T22)を、Opus M1〜M9で改訂し、第1段(02A)と第2段(02B)に振り分けた。新規test: `er128_kp_confirmed_content_test_01.py`(第1段 51件、`.venv\Scripts\python.exe -m unittest er128_kp_confirmed_content_test_01`)。

| ID | 目的 | 段 | test識別子(`er128_kp_confirmed_content_test_01`) / 備考 |
|---|---|---|---|
| T1 | レコード生成(HR CLI/AUTO)・正本+ミラー・sha・hash chain・kind/category | 02A | TestRecordCreation(hr_cli / values_come_from_candidate_doc / auto / std / idempotent) |
| T2 | フォーム経路(v2 payload→候補doc照合→op_select→レコード+payload原文+sidecar) | 02A | TestFromForm(adv_with_unconsumed_and_payload_source / std_category2 / gloss_mismatch_is_issue / provisional / missing_or_stale_sha / term_only_refused / user_ref_required / existing_validation / grammar_sidecar) |
| T3 | G1: 英語改変 | 02A | TestG1Tamper.test_english_tamper_blocks |
| T4 | G1: 日本語訳改変(現行は素通り=R-06の回帰)・TTS用textの別訳置換 | 02A | test_gloss_replacement_blocks_for_user_confirmed / test_tts_text_replacement_blocks... |
| T4b | M2-a: 派生物契約(convert出力はOK、別訳はBLOCK。protectedに`japanese_gloss_tts`を含めない) | 02A | test_derived_contract_allows_converter_output_of_confirmed_gloss / test_japanese_gloss_tts_is_not_in_protected_fields |
| T5 | G1: assets copy乖離(copyに無いitemはrunner側KP_ASSETS_STALE担当) | 02A | test_assets_copy_gloss_divergence_blocks_and_missing_item_is_runner_side |
| T6 | G1: ミラー・レコード手編集・shaを再計算した書換え(M5b候補docの錨)・hash chain・user_note・payload原文・候補doc差替え・review署名 | 02A | test_mirror_mismatch / test_record_hand_edit / test_record_rewrite_with_recomputed_shas... / test_history_chain_break / test_user_comment_tamper / test_candidates_doc_swap / test_review_signature_changed...; TestFromForm(payload原文改変) |
| T6b | actor=autoのgloss差はWARNのみ、英語差はBLOCK | 02A | TestG1ActorAuto |
| T7 | M4: 操作ガード(select/accept-ai/reselect/ng/unng/resolve-gloss/declare-absent)拒否、revise/revokeの`--user-ref`必須、AUTO→user更新は許可 | 02A | TestOperationGuards |
| T8 | M3: 例外クラス階層・Y/Z `_assert_kp_review_consistent`の写像(ISSUE→Pending rc=4、INTEGRITY→Stop) | 02A | TestExceptionClasses |
| T9 | M1: Z stage_kp G1(確定後artifact書換え→Adv解説/Part 1/Part 2の呼出が増えない)、Y/Zソース順序(install後・解説前、Zはperson gate/SRC gateの後)、`assets_json`受渡し | 02A | TestZStageKpG1 / TestYStageKpG1Source。Yの実行時test(mock context)は02Bで追加(Y runnerの既存mock E2Eが全stageでG1を通ることはer121回帰で確認) |
| T10 | confirm-revise(候補doc→review→レコード→確定物→再finalize連鎖、旧訳がhistoryに残る)/restore(条件i〜iii)/revoke | 02A | TestReviseRestore |
| T11 | Redundancy QA NG→`reconfirm_required`・依頼書先頭に確認依頼節・ユーザー選び直し可 | 02A | test_redundancy_ng_marks_reconfirm_required_and_allows_user_reselect |
| T12 | M8 precheck: 本文変更+ユーザー確定レコード→退避・有料再生成の前にISSUE待機(API/ファイル不変)、revoke後は従来STALE。AUTOは従来どおり | 02A | TestStaleLegacyFlag.test_text_change_* |
| T13 | M7: 旧run(レコード無し)はread-only WARN+legacy_drift、遅延生成しない、adopt-existing(dry-run→apply→INTEGRITY→restore) | 02A | TestStaleLegacyFlag.test_legacy_* / test_adopt_existing_* |
| T14 | flag: 既定ON・kill switch(OFF時WARN+disabled.json・ガード/検査/レコード作成が全て無効=従来動作)・読取点は`protection_enabled()`の1箇所、core/runnerに環境変数読取なし | 02A | test_kill_switch_off_disables_everything_with_warn / test_default_is_on_and_single_reader |
| T15 | 隔離: A/B/C・共有moduleがer128をimportしない、coreはer128を遅延importのみ、`er119_isolation_test_01`にer128登録 | 02A | TestIsolation + er119_isolation_test_01 |
| T16 | status/単一アクセサ`load_verified_items`(検証してから返す) | 02A | TestStatusAndAccessor |
| T17 | M6: Part 2凍結(MODEL/routing/prompt patchでも再抽出されない、reextractはrevoke必須、`ref_ja`はpool≠`translation_ja`のみISSUE、`translation_ja`は【日本語訳】節から抽出) | 02B | (02B) |
| T18 | G2/G3: TTS record(`japanese_meaning`をcanonical_text側で比較、Master Store再利用recordの欠落は誤BLOCKしない)・Part 1行(描画時のみ)・ページHTML(公開URL版含む) | 02B | (02B) |
| T19 | M2-b: Y/Z Stdページの「日本語の意味」が`japanese_gloss`(「～」含むglossの回帰) | 02B | (02B) |
| T20 | M8: STALE再バインド(出典文以外の1語変更=再バインド成立/出典文変更=ISSUE、候補doc→署名→再finalizeの連鎖) | 02B | (02B) |
| T21 | Z `_gloss_person_gate`: user確定済みitemは修復せずISSUE(FamilyZKpReviewPending)、レコード無し/AUTOは従来どおり | 02B | (02B) |
| T22 | 既存test回帰: `er119_*`・`er121_*`・`er026_*`・`er120_*`・`er019_*`・`er020_*`。変更したtest=`er119_isolation_test_01`(ALLOWEDにer128登録のみ)。既存失敗(HEAD既存、OPEN-543)は本件起因でない | 02A | `run_project_regression.py --pattern "<prefix>_*_test_*.py"` |

HR CLI test等の識別子: 本委任では既存testの期待値を変更していない(M4のガードは「ユーザー確定レコードがある状態でのAI/CLI操作」に限られ、既存testはレコードの無い状態、または`confirm --from-review`を経ていない状態で操作するため影響なし。回帰=er119 203件中の失敗は既存2件のみ)。

撤去/残置: 現行のcandidate_id集合比較(`require_final_consistent`)は残置(新検査はAND追加のみ)。旧ルール撤去対象0。`pinned_items`(DESIGN_01 §4-8)はM9で設計から削除(コード無し)。
