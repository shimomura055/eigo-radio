# OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01 報告書

管理ID: OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01(Gate 3、
Sonnet委任)。ユーザー正式決定(2026-09-09、A-UDR-20=(i))に基づき、
`FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05_REPORT.md`が確定した
「G1=実装漏れ(承認済み範囲内)」の判定へ従い、**改善施策ではなく承認済み
挙動(ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14)への回帰修正**として
Production正式経路へ配線した。

---

## Part 1: G1修正内容

### 対象・根拠

Trial-05のReconciliation Check(§1)が確定した通り、`er009_diagnostic_
full_retry_modules_12.py::build_diagnostic_section()`は前回Point One/Two
本文をハードコードされたプレースホルダー文字列("(Point One body from
previous attempt)"/"(Point Two body from previous attempt)")のまま
Writerへ渡していた。同一commit(`f46b6e1`)内で並行して作られた検証済み
script(`er009_n1_diagnostic_full_retry_production_12.py`、DECISION_LOG.md
`ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14`が引用する実runtime evidence
[3/3 PASS・Household実発火]の元になったscript)は、
`previous_point_one=previous_article["point_one_body"]`のように実テキスト
を正しく渡しており、module化時に配線が失われた実装漏れであることが
確定している。

### 修正差分(diff要旨)

1. **`er009_diagnostic_full_retry_modules_12.py::build_diagnostic_
   section()`**: シグネチャへ`previous_point_one_text: str`/
   `previous_point_two_text: str`(既定値なし、必須引数)を追加し、
   ハードコードされたプレースホルダー文字列2箇所をこれらの引数値へ
   置き換えた。`DIAGNOSTIC_SECTION_TEMPLATE`自体・`classify_overlap()`/
   `compose_diagnosis()`は無変更。
2. **`er003_v1_n3_01_articles_generate.py::build_diagnostic_retry_
   prompt()`**(唯一のProduction呼び出し元): `split_common_sections_for_
   point_qa()`が既に抽出していた`sections["point_one_body"]`/
   `["point_two_body"]`を、`build_diagnostic_section()`へ新規追加した
   2引数として渡すよう1箇所のみ変更(呼び出し元は抽出済みなのに未使用、
   という二重の配線漏れの解消)。
3. **他の呼び出し元grep結果**: `build_diagnostic_section()`を直接呼ぶ
   ファイルは、Production本体(上記2.)を除き2件のみ検出(`er009_n1_
   diagnostic_full_retry_verification_14.py`・`er009_n1_diagnostic_full_
   retry_integration_test_13.py`、いずれも過去のER-009 closeout検証用
   script)。前者は**git未追跡の既存ファイル(古い未追跡群)であり、本
   タスクのSTOP事項「触らない」に該当するため編集せず元のまま**(3引数
   呼び出しのまま、`run_project_regression.py`のunittest収集対象では
   ないため回帰へは影響しない)。後者は`git`追跡済みファイルであり、
   `build_diagnostic_retry_prompt()`(Production関数)を呼ぶテストは
   影響を受けないが、`build_diagnostic_section()`を直接呼ぶテスト関数
   1箇所のみ新シグネチャ(5引数)へ更新した。
   Prompt文言(`DIAGNOSTIC_SECTION_TEMPLATE`/`DIAGNOSTIC_RETRY_PROMPT_
   TEMPLATE`)・閾値(0.40)・`POINT_OVERLAP_ARTICLE_RETRY_MAX`(2)・retry
   判定ロジック(`lexical_flagged`/`still_flagged`)はいずれも無変更。
   G2(cross_point_overlapの診断promptへの追加)は実装していない
   (CURRENT_SPEC訂正のみ、Part 2参照)。

### テスト

新規`er011_open112_diagnostic_retry_point_body_regression_fix_01_test_
01.py`(6件、`python -m unittest`実行、全PASS):
- `test_real_point_body_text_is_embedded`: 実本文2件が診断section内に
  実際に含まれることを確認。
- `test_old_placeholder_strings_do_not_appear`: 旧プレースホルダー
  文字列2種が出力に一切残らないことを確認。
- `test_missing_required_arguments_raises_type_error`: 旧3引数呼び出し
  (新規引数を省略)が`TypeError`となること(既定値なし=暗黙の
  プレースホルダー復活を防ぐ設計)を確認。
- `test_empty_point_body_text_does_not_crash`: 本文抽出に失敗した場合
  相当の空文字列ケースでも例外を投げず、プレースホルダーへフォール
  バックしないことを確認。
- `test_retry_prompt_contains_actual_point_bodies`: Production呼び出し元
  `build_diagnostic_retry_prompt()`が実際に本文を伝播することを確認
  (合成article_text、API呼び出し無し)。
- `test_unparseable_article_structure_falls_back_to_original_prompt`:
  想定外構造の場合、既存挙動通りoriginal_promptをそのまま返すことを
  確認(新しいhard failureを追加しない)。

**project-wide regression**(`run_project_regression.py`、変更後):
`collected=2253, passed=2250, failed=3, errors=0, skipped=0`。failed 3件は
既知の無関係failure(`er003_test_p2j_investigate.py`、OPEN-77既知meta-test
集計3件、本タスク以前から存在)のみで、新規failureはゼロ。

### Runtime evidence(Gate 3)

Production正式初回path`er006_pool_pilot_01_writer.py::run_writer_for_
theme()`(mode指定なし[`editorial_mode=None`]、既存承認済みHanshin
Ledger[`er003_output/n3_01/hanshin/research/verified_fact_ledger.txt`]、
`er002_v1_2m_masters/hanshin_ja_master.txt`)を実際に呼び出した
(`er011_open112_diagnostic_retry_point_body_regression_fix_01_runtime_
evidence_01.py`、instrumentation: `er003_v1_n3_01_articles_generate.
build_diagnostic_retry_prompt`を薄いwrapperへ一時差し替え、元の関数を
そのまま1回呼び出し戻り値も無変更で返すのみ・retry判定/prompt内容へは
一切影響しない)。

**結果(1回目の実行で発火・検証完了、追加再実行は不要だった)**: attempt1
でB1B・A2とも`point_overlap_article_retry_attempts=2`(Loop Budget上限まで
retryしても解消せず`NG_REVIEW_REQUIRED`、ただしDiagnostic Full Retryは
2回とも実発火)。捕捉した診断prompt(`captured_diagnostic_prompt.txt`)を
検証した結果:
- `contains_old_placeholder_strings=False`(旧プレースホルダー文字列は
  一切残っていない)
- `contains_real_point_one_body=True`/`contains_real_point_two_body=True`
  (前回attemptの実際のPoint One/Two本文が診断prompt内にそのまま含まれる
  ことを、`split_common_sections_for_point_qa()`で抽出した本文の部分
  文字列一致で確認)
- 実例(`Previous Point One (overlap_ratio=0.5, flagged=True):`直後):
  "The 8-1 result did not mean Hiroshima was out of the game from the
  beginning. Montero's fifth-inning solo shot turned a 2-0 lead into a
  2-1 game..."という、Hanshin記事の実際の前回Point One本文がそのまま
  埋め込まれている(旧実装なら"(Point One body from previous attempt)"
  という固定文字列だったはずの箇所)。

費用: 累積¥24.1382(56 API call、cost cap ¥60以内)。うち最初の実行で
スクリプトのバグ(`run_writer_for_theme()`の戻り値`{"results":...,
"timing":...}`を誤って直接`results.items()`していたため、実際は発火
済みなのにloop制御上「未発火」と誤判定し、不要な追加attemptへ進んで
しまった)により想定より1往復分余分にコストを消費したが、上限¥60は
超過していない(該当バグは発見後修正し、修正版で正常に1回で完了・
検証済み)。

---

## Part 1: Gate 3表

| 項目 | 内容 | 状態 |
|---|---|---|
| Production正式初回path | `run_writer_for_theme()`(mode指定なし)から`run_one_pattern()`経由で実行、Trial専用関数は一切importしない | 確認済み |
| retry・regeneration整合 | Human Review再生成経路(`REGENERATE_APPROVED`等)でも同一`run_one_pattern()`/`build_diagnostic_retry_prompt()`を経由するため同一修正が適用される(別経路の存在なし、grep確認) | 確認済み |
| Trial専用でない | Production module(`er009_diagnostic_full_retry_modules_12.py`)・唯一の呼び出し元(`er003_v1_n3_01_articles_generate.py`)本体を直接修正、Trialのコピー関数(`er011_point_overlap_gap_fix_trial_05.py`)は一切importしない | 確認済み |
| runtime発火 | Hanshin Ledger実行attempt1でB1B・A2とも発火(retry 2回、実Point本文が診断promptへ埋め込まれprompt内容で確認、旧プレースホルダー文字列0件) | PASS |
| Regression | `run_project_regression.py`: collected=2253/passed=2250/failed=3(既知3件のみ)/errors=0 | PASS |
| 承認内容(ER-009-N1-14)との一致 | 検証済みscript`er009_n1_diagnostic_full_retry_production_12.py`の実装(実Point本文をWriterへ渡す)と同一ロジックへ復元。Prompt文言・閾値・Loop Budgetは無変更 | 確認済み |
| Cost影響 | retry発火時のinput token増(前回Point本文の実テキスト分、旧プレースホルダーより長い)のみ。初回生成(retryなし)には一切影響しない。量産時の継続コスト増分は軽微(1 retry あたり数百〜数千token程度) | 確認済み(実測は下記runtime evidence参照) |
| SSOT | `CURRENT_SPEC.md`ER-011-NO18節・Diagnostic Full Retry節へ本修正のcommit参照を追記(Part 2参照) | 実施済み |
| Git | 未実施(本Reportの後、Fable/ユーザーが確認したうえでcommit・push、下記参照) | Sonnetは`PRODUCTION_WIRED`を宣言しない |
| Dangling Reference | 本修正が参照する管理ID(ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14、FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05)はいずれも既存SSOTに既出。新規追加はOPEN-133/OPEN-134(SSOT担当分、Part 2参照) | PASS |

**Sonnetからは`PRODUCTION_WIRED`を宣言しない**(Fable/ユーザーの最終受入待ち)。

**重要な留保**: G1修正後も「Point Overlap問題が解決した」とは扱わない。
`FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05`の実データでも、G1相当の修正
(gapfix条件)がbaseline条件より系統的に優れているとは確認できておらず
(NG率・retry回数とも非単調)、NG 12本中5本(42%)はG1の対象外原因
(Value QA単独FAIL・Fact Checker FAIL)であることが既に確認されている。
残存failure modeの観測は`OPEN_ITEMS.md`OPEN-134行のExit条件(Part 2参照)
へ統合し継続する。

---

## Part 2: SSOT・Exit条件

`docs/pm/PM-CLOSEOUT-CONSOLIDATION-33`(SSOT・Git担当)により、以下を
反映した:

1. `CURRENT_SPEC.md`: 「Point One対Point Twoのlexical overlap検査
   (追加ペア)」行(ER-011-NO18)を、cross_point_overlapのstill_flagged
   統合は「未実装・`DEFERRED`」(2026-09-09、A-UDR-21、OPEN-133)へ訂正
   (記載の履歴は保持)。Diagnostic Full Retry節へG1修正のcommit参照を
   追記(changelog 1件)。
2. `OPEN_ITEMS.md`: OPEN-112行(G1配線=候補・Fable受入待ち+commit参照)、
   OPEN-133行(A-UDR-21反映=CURRENT_SPEC訂正済み、実装は別途判断)、
   OPEN-134行(A-UDR-22=観測Exit条件全文記録)、OPEN-120行(4V Trialユーザー
   中断)。`DECISION_LOG.md`新規エントリ1件。`docs/pm/PM_GOVERNANCE.md`
   3節へ観測Exit条件確認の1行追加。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`
   本委任2件+4V Trial中断記録を追記。
3. 観測Exit条件の記録先雛形: `er011_output/point_overlap_observation_
   log.jsonl`(空ファイル)+`er011_output/point_overlap_observation_log_
   README.md`(schema・Exit条件全文)。実際のrecord追記は今後の別タスク。

---

## Git

G1(本修正): `er009_diagnostic_full_retry_modules_12.py`・
`er003_v1_n3_01_articles_generate.py`・`er009_n1_diagnostic_full_retry_
integration_test_13.py`・`er011_open112_diagnostic_retry_point_body_
regression_fix_01_test_01.py`・`er011_open112_diagnostic_retry_point_
body_regression_fix_01_runtime_evidence_01.py`・本Report・
`er011_output/open112_diagnostic_retry_point_body_regression_fix_01_
runtime_evidence_01/`(evidence一式)。G2(SSOT): `CURRENT_SPEC.md`・
`OPEN_ITEMS.md`・`DECISION_LOG.md`・`docs/pm/PM_GOVERNANCE.md`・
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`・`er011_output/point_overlap_
observation_log.jsonl`・`er011_output/point_overlap_observation_log_
README.md`。

触らなかったもの: `er012_output/editorial_b_voices_4v_article_trial_01/`
(4V Trial部分成果物)、`er006_output/`、`er011_output/attempt_history.
jsonl`、`er009_n1_diagnostic_full_retry_verification_14.py`(git未追跡の
既存ファイル、古い未追跡群)。
