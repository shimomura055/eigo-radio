# HUMAN_APPROVAL_CASE_B_01: 『宅配の再配達』案Bの個別Human承認(ユーザー正式承認 USER_03 §1・選択肢Ⅱ)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_05 / 2026-10-25(JST)。Status=`APPROVED_FOR_PRODUCTION`(ユーザー承認)・実装済み・offline test PASS。**`PRODUCTION_WIRED`ではない**(Production runtime evidenceで本経路が発火した記録は未取得。案Bが判定1〜2回目でPASSする限り発火しない)。
原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_03.md` §1(取得元jsonlで一部文字化け。無改変保存)。API 0・実費0円(本節の実装・test)。

## 1. 承認内容(ユーザー原文の要点)

- 対象=『宅配の再配達は有料にすべきか？』の承認済み案B。品質Gateの`leak_evidence_memorable`がFAILしても、**既存のHuman個別承認記録**を用いて当該本文を採用できるようにする。
- 厳守: 承認済み案B本文と**完全一致**の場合のみ / 対象Gate項目は`leak_evidence_memorable`のみ / 他のGate項目のFAILは救済しない / Gate判定結果・FAIL理由・Human承認記録をすべて保持 / 過去のFAIL記録を削除・改変しない / 他記事・他Closingへ拡大しない / 本文変更・再生成・局所書換え後の文章には自動適用しない / 新たな汎用例外機構を増やさない。

## 2. 実装(`er121_family_y_text_core_01.py`)と適用条件

適用可否は**1関数 `evaluate_case_b_human_approval(slug, text, gate_result)`** だけが判断する(副作用なし)。全条件が「かつ」で、1つでも欠けると従来どおり`FIXED_CLOSING_RESIDUAL_FAIL`でSTOP(公開しない)。

| # | 条件 | 欠けたときの理由コード |
|---|---|---|
| 1 | registryにその`slug`の`human_approval`がある(現状は`redelivery_fee`の1件のみ) | `NO_HUMAN_APPROVAL_FOR_SLUG` |
| 2 | 本文がregistryの承認本文と**byte一致**(UTF-8バイト列+sha256) | `TEXT_NOT_BYTE_IDENTICAL_TO_APPROVED_CASE_B` |
| 3 | Gate結果が`kind=tension`・`status=LEAKAGE_RESIDUAL_STOP` | `GATE_NOT_RESIDUAL_FAIL` |
| 4 | 書換えなし(`rewritten=false`・履歴に`rewritten`/`rewrite_calls`なし) | `REWRITTEN` |
| 5 | 判定が上限(3回)すべてFAIL | `NOT_ALL_JUDGEMENTS_FAILED` |
| 6 | 全判定の本文shaが承認本文のshaと同一 | `JUDGED_TEXT_NOT_APPROVED_TEXT` |
| 7 | FAIL項目の集合(**全判定を通じた和集合**)が`{leak_evidence_memorable}`と完全一致(他項目が1回でもFAILしたら救済しない) | `FAIL_ITEMS_NOT_EXACTLY_APPROVED_ITEMS` |
| 8 | FAILしたsectionが`tension`のみ | `UNEXPECTED_SECTION_FLAGGED` |

- 一般化Closing(`general_prompt_02`)の経路からは**呼ばれない**(コード上`ent is not None`の案B分岐のみ)。env・CLI・設定dictでONにできる経路はない(registry定数の`human_approval`のみ)。
- 判定の途中(1〜2回目)でPASSした場合は承認不要(`status=PASS`)。承認が使われるのは「3回すべてFAILかつFAILが`leak_evidence_memorable`のみ」のときだけ。

## 3. 記録(保持するもの)

| 記録 | 場所 | 内容 |
|---|---|---|
| 元のGate判定 | `<out>/closing/gate/leak_check_{1,2,3}.json`・`gate_result.json` | **改変なし**(`status=LEAKAGE_RESIDUAL_STOP`のまま。Gate PASSの印`final_texts.json`は作らない) |
| 元判定のsnapshot | `<out>/closing/human_approval_gate_snapshot/<gate_result_sha12>/` | 判定3件+gate_resultの複写(上書き禁止`xb`)。path+sha256を承認記録に保持 |
| Human承認記録 | `<out>/closing/human_approved_closing.json` | 既存`record_human_approval`と同形のキー(`canonical_text_sha256`・`approved_at`・`approved_by`)+`approval_ref`(USER_03 §1)・`approved_items`・`fail_items_union`・各判定の`fail_fields`/`reasoning`/`quoted_evidence`/snapshot path+sha・`original_gate_status`・`registry_sha256`。再実行時は旧記録を`previous_entries`へ積み、消さない |
| closing_record | `<out>/closing/closing_record.json` | `status=PASS_BY_HUMAN_APPROVAL`・`human_approval_ref`・`human_approval_record(_sha256)`・`original_gate_result`・`judgements[]`(元の判定結果) |
| 過去run(再実行時) | `<out>/closing/gate_prior_runs/<内容sha12>/` | 再実行(retry/resume/regenerate)で`leak_check_N.json`が上書きされる前に退避(同内容は二重に作らず、既存は上書きしない) |

## 4. 検証(検証項目①の6点。`er121_family_y_text_core_01_test_01.py` `TestCaseBHumanApproval`+`er121_family_y_text_core_article_test_01.py`)

| 要求 | test | 結果 |
|---|---|---|
| 承認済み案Bの本文・対象項目に限り救済される | `test_memorable_only_fail_three_times_is_accepted_by_human_approval_with_all_records_kept`、article `test_plan_b_memorable_only_fail_is_accepted_by_human_approval_end_to_end_and_cached_resume_reverifies`(記事組立まで進む) | PASS |
| 他のGate項目がFAILした場合はSTOP | `test_other_item_fail_in_any_judgement_stops`(4系列: 3回目に混入/1回目に別項目/別項目のみ/Tension専用項目混入)、`test_applicability_function_each_condition`(`leak_numbers_foreground`・`leak_discovery_syntax`等) | PASS |
| 本文が変更された場合は承認が適用されない | `test_applicability_function_each_condition`(+「。」/1字違い)、`test_changed_text_registry_or_voice_is_never_covered`(registry本文改変→`FIXED_CLOSING_TEXT_SHA_MISMATCH`、Voice R0違い→`FIXED_CLOSING_PROVENANCE_MISMATCH`。いずれもAPI前に停止)、`test_verify_rejects_tampered_or_stale_approval` | PASS |
| 他記事・他Closingに適用されない | `test_other_slug_and_missing_registry_approval_never_apply`(4 slug+registryから承認を除くとSTOP+承認付きslugは`redelivery_fee`の1件のみ)、`test_general_path_never_uses_human_approval`(一般化経路は`LEAKAGE_RESIDUAL_STOP`のまま・承認記録なし) | PASS |
| 承認記録と元のGate結果の両方が保存される | 1行目のtest(gate_result=FAIL保持・承認記録・snapshot sha一致・`quoted_evidence`保持)。`test_rejudge_pass_before_third_needs_no_approval`(途中PASSは承認記録を作らない) | PASS |
| retry・resume・regenerationで適用範囲が変わらない | `test_retry_resume_regeneration_keep_scope_and_preserve_past_fail_records`(同out_dir再実行→同結果・過去FAIL退避・旧承認記録を`previous_entries`保持・再実行で他項目FAILなら承認を使い回さずSTOP)、article test(cache再利用でも`verify_human_approval_record`で来歴再検査、snapshot改変→`HUMAN_APPROVAL_PROVENANCE_MISMATCH`でSTOP) | PASS |

## 5. 注意・限界(隠さない事実)

- 本経路は**案B本文×`leak_evidence_memorable`のFAIL**だけの個別例外で、Gateの緩和ではない。M-1較正(GATE_CALIBRATION_01 §3)では案Bの`leak_evidence_memorable`単発FAILは2/7回、Lead/人物紹介側は別扱い(OT-28、`leak_evidence_memorable`非適用)。
- 委任_03 Part B(E-1、commit 381dd569a)では案Bの実Gate判定は1回でPASSしており、本経路は発火していない。発火は「3回連続で`leak_evidence_memorable`のみFAIL」時に限られ、その場合に限りHuman承認記録つきで記事が進む。
- 承認記録は「ユーザーが事前に出した個別承認(USER_03 §1)」を機械的に記録するものであり、各runで人間が改めて何かをするわけではない。承認の根拠・範囲はregistryの`human_approval`(`approval_ref`・`items`・`scope`)に固定されている。範囲を広げる(別項目・別記事・本文変更後)にはユーザーの新規承認とregistry変更が必要。
- runner(`er121_family_y_runner_01.py`、委任_03所有)は`closing_record.source`と`final_sha256`だけを読むため無改変で動く。`status=PASS_BY_HUMAN_APPROVAL`を最終manifest/EVIDENCEへ転記する要求は報告のrunnerへの要求を参照(編集は委任_03)。
