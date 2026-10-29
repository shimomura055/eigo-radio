# TEST_PLAN_01 テスト計画(仕様①②、X/Y/Z x Std/Adv)

対象設計=WIRING_DESIGN_01.md。pythonは`.venv\Scripts\python.exe`+`PYTHONUTF8=1`。単体・統合はAPI 0(mock、er119_test_support_01.Env流用)。

## 1. 単体test(新規。X/Y/Z x Std/Adv は共通moduleのため `level in (a2,b1b)` x `std_part1 in (有,無)` でパラメタ化し、family別はrunner配線testで確認)
仕様①
- U1 `_gate_chain`: qa_overall_status=REVIEW_REQUIRED -> dropped(stage=canonicalization_qa)・candsに無い。PASSは従来どおり提示。status欠落/未知値 -> drop(fail-closed)。flags.qa_failは常にFalse。
- U2 backfill連携: qa除外がgate_droppedに数えられ、補完が1回だけ発動(E計算)。補完候補のQA FAILも除外・再帰補完なし。backfill OFF時は既存外側retry条件が働く(新しい上限なし)。
- U3 `presentable_candidates`: 旧doc(flags.qa_fail=True/human_selectable)を除外。render_request_md・exporter・auto_selectが同一関数を使う(関数参照のGrep/mock呼出検査=二重定義なし)。
- U4 exporter: 旧docのqa_fail候補をdataに出さず`data_warnings.qa_fail_excluded`に記録。新docはデータ変更なし(バイト比較で出力不変=Regression)。
- U5 validate_selection: 提示セット外(qa_fail)候補の選択は従来どおり拒否(安全網)。`--accept-qa-fail`は旧doc救済として動作。
- U6 rescue: QA再判定PASSの救済候補は提示、FAILは除外。
仕様②
- U7 validate_selection: 重複pairを含む選択が**errsを返さない**(Std/Adv、KP/vocab)。他のerr(件数/KP⊂vocab/NG/gloss HR/Gate)は従来どおり。
- U8 `redundancy_alarms`: 候補docのduplicate_pairs(reasoning・4観点)から対象表現・理由・slotを返す。決定論・API 0。
- U9 op_select: 重複選択を受理し`review.redundancy_alarms`+historyに記録。
- U10 finalize(人間選定): 確定集合QAが`REDUNDANCY_NG`でもPENDINGへ巻戻さず確定続行、final_qa.status=REDUNDANCY_ALARM、kp_selection_final.jsonにpairs。確定レコードはRECONFIRMにならない・ISSUEファイルなし。
- U11 キャッシュ: ALARM確定後の再finalize/resumeでRedundancy QAを再呼出しない(call数0)。選定変更でkey不一致 -> 再実行。
- U12 判定不能(INVALID等): 従来どおりKpReviewError(fail-closed)。
- U13 AUTO: 重複回避・繰上げ・尽きたSTOPは**不変**(既存test維持)。
- U14 派生`redundancy_alarm.json`: 書込失敗(権限/IOError mock)でも確定成功・warningのみ。欠落時は決定論で再生成。
- U15 `on_final_redundancy_alarm`: レコード状態不変・historyに注記。
- U16 完了報告ブロック: 0件でも「0件」表示、アラーム有無で停止しない(X/Y/Z各runnerの節生成関数)。

## 2. 旧testの書換え(反転。期待値を非ブロッキングへ)
- er119_kp_human_review_01_test_01.py:236(重複選択が拒否される)、:293-302 `test_final_redundancy_ng_on_human_selection_returns_to_pending_M8`、:161-170 `test_review_required_item_gets_qa_fail_flag_and_not_auto`(旗->除外へ)、:265-270 `test_qa_fail_requires_explicit_accept`(旧docで継続)。
- er128_kp_confirmed_content_test_01.py:582-593 `test_redundancy_ng_marks_reconfirm_required_and_allows_user_reselect`、er128_kp_confirmed_content_slot23_test_01.py:329(重複メッセージのモック)。
- 変更しない: auto系(:322,:343)、er119_kp_backfill_test_01.py(旗キー検査は新docで常にFalse値のため整合要確認)。

## 3. 統合test(API 0 mock)
- I1 X/Y/Z runner配線(er119_x_wiring_test_01.py、er119_z_wiring_test_01.py、Y相当)x Std/Adv: 候補生成(QA FAIL混在mock)-> 提示セットにQA FAIL無し -> 人間選定(重複pair含む)-> confirm -> finalize -> アラーム記録 -> runnerの後続(study_text以降mock)が**停止せず進む**。他Gate(NG/gloss HR/件数/G0)は従来通り停止することも1件ずつ確認。
- I2 resume: 確定済み(ALARM)状態で同コマンド再実行 -> API 0・選定保持・アラーム保持。
- I3 retry/regeneration: op_reselect -> 新roundでアラーム引継ぎなし。本文変更(REBOUND)-> 選定同一ならアラーム保持。
- I4 `confirm --from-readable`(er128_form_readable_restore): 重複pair含むreadableが確定される(Y Adv再現fixture)。旧doc+qa_fail候補を含むreadable(提示外)は従来どおり拒否。
- I5 DefaultOffIsolation不要(通常Production変更、新flagなし)。ただし**旧経路A/B/C(run_key_phrases)無変更**をimport/呼出Grep+既存test実行で確認。
- I6 Y適用op(`op_requalify_candidate`): 差替えは`old-fashioned`限定・本文連続一致検証・PENDING中のみ・candidates_sha更新・historyにuser_ref。任意文字列/確定済み/不連続はエラー。

## 4. Regression(既存test群)
実行対象(全部PASS): er119_kp_human_review_01_test_01.py / er119_kp_human_review_cli_01_test_01.py / er119_kp_human_review_outputs_test_01.py / er119_kp_backfill_test_01.py / er119_kp_p7w5_test_01.py / er119_kp_p7w5_e2e_test_01.py / er119_kp_rescue_wiring_test_01.py / er119_x_wiring_test_01.py / er119_z_wiring_test_01.py / er119_isolation_test_01.py / er119_grammar_review_test_01.py / er128_*_test_01.py(全8本) / er128_form_readable_restore_test_01.py(form_logic.js同一性) / フォームJS test(node)。加えて、凍結ライン(A/B/C)関連の既存testが無影響であること(`git diff --stat`が共通moduleのみ)。実行は変更前baselineを先に取得し差分比較(既存失敗とのbaseline差分を区別)。

## 5. Runtime evidence計画(X/Y/Z x Std/Adv の6組合せ)
目的: 正式Production経路で①②が発火する実証。**copy-run**(既存runの複製dir、本番出力・公開ページ・SSOTの確定物を汚さない)で、実LLMを最小回数のみ使用。
- R1 ①の発火(候補生成): QA FAILが自然発生した既存candidate doc(Y run_02 a2 rank5)を入力に、新`_gate_chain`相当の判定(API 0、保存済みitem.qaを再判定)でdrop・補完要否を確認(再生成は不要=API 0)。X/Zは既存run docから同様(QA FAIL有無を確認し、無ければmock fixtureをunit/integrationの証拠とし「実データ該当なし」と明記)。
- R2 ②の発火(確定): Y姓テーマAdv(b1b)copy-runで `confirm --from-readable readable_b1b.txt` -> finalize(最終Redundancy QA実LLM 1 call/集合、`gpt-6-luna`)-> `REDUNDANCY_ALARM`記録 -> **runnerを後続stage(gate/assembleまで、音声生成はしない)** へ進めて停止しないこと。X/Zは各1 copy-run(Std/Adv)でfinalizeのみ(重複が自然に出る保証がないため、確実に重複するペアのmock redundancy_fnとの併用を明記)。
- R3 Y適用: Std copy-runで方式P(op)-> exporter再生成 -> form_logic.js(node)とPython build_readableのバイト一致 -> `confirm --from-readable`。
- 取得物: 各手順のrc・stdout・生成/更新ファイルのsha・alarm.json・final.json・history(`docs/research/.../evidence/`、既存の証跡構造に従う)。音声生成なし。
- 費用見込み: 最終Redundancy QA 約¥1-2/集合 x 実LLM回数(Y Adv KP+vocab=2集合、Y Std=1-2集合)、qa再判定/gloss整合 約¥1-3 -> **runtime evidence全体で約¥5以内**(X/Zは既存確定済みcandidate docの再利用/mockで実LLM追加なし)。7-7: 案件見積300円以下・承認済みScope内、日次1,000円内。実行前にstop_scope_checkを実行。

## 6. 完了条件(原文§7と対応)
Family X/Y/Z x Std/Adv全6組合せのU/I test PASS、R1-R3の実行証拠、旧test反転の理由記録、Grep(Dangling: `final_redundancy_ng`等0件または意図残置)、SSOT更新、Git、Fable独立受入。
