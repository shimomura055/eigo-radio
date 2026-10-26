# IMPLEMENTATION_02A: 確定内容保護 共通核 第1段(KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02A、2026-10-27、API 0・JPY0)

設計=`DESIGN_02.md`(Opus M1〜M9反映)。到達上限=IMPLEMENTED(第1段)。PRODUCTION_WIRED/EVIDENCEDではない(Family別evidence・G2〜G4・02B項目は未)。

## 1. 変更ファイルと位置
| ファイル | 変更 |
|---|---|
| `er128_kp_confirmed_content_01.py`(新規) | 共通核。flag `protection_enabled():67`、レコードI/O `load_record:177`/`save_record:182`、構築 `build_items:228`/`_new_record:239`、自己整合 `_problems_self:151`(record_sha・hash chain・content_sha・user_note_sha)、診断+例外 `raise_integrity:291`/`raise_issue:300`/`request_notice:307`、突合 `_item_diffs:325`/`_artifact_diffs:353`/`_cand_diffs:379`/`_grammar_problems:395`/`_form_source_problems:412`、**G1** `verify_g1:424`、旧run `_legacy_drift:488`、**G0** `on_finalize_pre_write:514`/`on_finalize_post_write:554`/`on_final_redundancy_ng:566`、`stale_issue:589`、**操作ガード** `guard:608`/`guard_declaration:620`、単一アクセサ `load_verified_items:629`、CLI `cmd_from_form:672`/`cmd_from_review:773`(`--adopt-existing`)/`cmd_revoke:803`/`cmd_revise:819`/`cmd_restore:889`/`cmd_status:922`/`run:974` |
| `er119_kp_human_review_01.py` | 例外クラス `ConfirmedContentIssue/IntegrityViolation/Locked` と遅延import `_cc()`(:98-:121)。ガード: `add_declaration:426`・`op_select:638`・`op_reselect:714`・`op_ng:747`・`op_unng:778`・`op_resolve_gloss:844`。`finalize_kp`: QA NGフック`:1015`、G0 pre-write`:1036`(書込が必要な場合のみ=`fresh`)・post-write`:1060`。`require_final_consistent`: `assets_json`引数+G1呼出`:1131`。`ensure_kp_review`: STALE precheck`:1365`(退避・有料再生成より前)、依頼書へ確定内容の確認依頼節を前置`:1367,:1427,:1435` |
| `er121_family_y_runner_01.py` | `_assert_kp_review_consistent`が`assets_json`を渡す(`:520`)、stage_kpのinstall直後にG1 1行(`:615`、解説LLM前) |
| `er026_family_z_fiction_production_runner_01.py` | 同上(`:1519`、`:2062`。`_gloss_person_gate`/`_src_gate`/installの後・Adv解説LLM前) |
| `er119_isolation_test_01.py` | `ALLOWED`にer128を登録(core/CLIから遅延import。A/B/C非接触) |
| `er128_kp_confirmed_content_test_01.py`(新規) | 52件(TEST_PLAN_02.md) |
- X runner(`er019`)は無変更(`require_final_consistent`の既存呼出点がそのままG1を通る)。`er119_kp_candidates_01.py`・`er119_kp_human_review_cli_01.py`は無変更(7+5と競合なし)。

## 2. 動作要点
- **レコードを作る時点**: フォーム=`confirm --from-form`送信時、HR CLI/AUTO=finalizeの成果物書込み直前(G0)。既にfinalize済みのidempotent再実行ではレコードを作らない(旧run扱い=M7、遅延生成なし)。
- **G1**: 全消費者入口(X `:3537`、Y/Z `_assert_kp_review_consistent`、Y/Z stage_kp)でレコード自己整合→ミラー全文一致→payload原文sha→文法sidecar→`origin.*`==review→確定集合==review.selection(slot別)→**レコード==候補doc**→レコード==成果物(kp/vocab/assets copy。英語は常にBLOCK、glossはactor=userのみBLOCK、TTS用textは派生物契約)。
- **ガード**: live+actor=userのレコードがあれば上記7操作を拒否(`ConfirmedContentLocked`)。AUTO(actor=auto)は従来どおり事後Review可でuserへ更新(revision+1)。
- **ISSUE(rc=4)**: STALE precheck、フォームの訳/sha/非正式訳、restore時の人間操作痕跡・候補doc差替え、Redundancy QA NG(`reconfirm_required`)。**INTEGRITY(STOP)**: 上記G1/G0の不一致。
- **kill switch**: `EIGO_KP_CONFIRMED_PROTECTION=0`(stderr WARN+`confirmed_protection_disabled.json`)。運用ルール=ユーザー指示+user_refがある場合のみ。

## 3. 動作確認(runtime evidence)
- `er128_kp_confirmed_content_test_01.py` 52件 PASS(`run_project_regression.py --pattern "er128_*_test_*.py"`: collected=52 passed=52)。Z mock E2E(`TestZStageKpG1`): ユーザー確定(HR select)→`run_stage("kp")`完了→確定後にartifactの訳を書換え→再実行は`stage_kp_post_install`のG1で`CONFIRMED_CONTENT_INTEGRITY_VIOLATION`によりSTOP、mock API呼出数は不変(Adv解説・Part 1・Part 2の有料生成に到達しない)。
- 回帰: `er119_*_test_*.py` 203件中201 PASS(失敗2件=HEAD既存 OPEN-543: `er119_grammar_review_test_01.test_grammar_files_not_tracked_dirs`(`er119_output/`が10/25から存在)・`er119_isolation_test_01.test_only_x_z_runners_import_er119`(offenders=er121/er123/er124。er128は登録済みで対象外))。`er120_*` 14件PASS、`er121_*` 369件(1 skipped)PASS、`er026_*` 全件、`er019_*` 552件中551(失敗1=`er019_x_std_chunk_opus_test_01.R4HunkClassifierTest`=OPEN-543既存)、`er020_*` 92件中91(失敗1=`er020_..._fullseg_test_01.RegressionCorpusTest.test_recorded_candidates`: `er011_output/local_rewrite_recovery/coffee_prices__run_tru_ev_x_adv_3b/...`のworking tree状態(git statusで`er011_output`配下が変更/削除済み)に依存する既存失敗で、本件のコードは触れていない)。
- 変更したtestは`er119_isolation_test_01.py`のALLOWED登録のみ。既存testの期待値変更なし。

## 4. 02Bへの引継ぎ
M2-b(Y/Z Stdページ表示を`japanese_gloss`へ)・M6(Part 2凍結)・M8(自動再バインド)・G2〜G4・Z `_gloss_person_gate`のISSUE分岐(`FamilyZKpReviewPending`写像)・LR警告記録・`part1_items`/`public_study_html`の単一アクセサ経由化・Family別evidence(フォームpayload→`confirm --from-form`→後続のX/Y/Z通しE2E、公開URL版ページ、「～」含むgloss)。
