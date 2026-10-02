## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_53)。並行タスク: 委任_51(SSOT記録・線引き・再分類。**SSOTを編集するのは委任_51だけ**。本委任はSSOTを編集しない)、委任_52(read-only調査、git操作なし)。本委任はrunner・テスト・Trial Prompt(runner内の追記ブロック)・新規スクリプトを編集・作成し、自分のファイルだけを明示addしてcommit/pushする。

## 性質/到達上限Status/禁止事項

- 性質: Checker引用への説明文混入12件の原因分類、対策(違反箇所フィールドに記事原文だけを入れ、説明・理由は別フィールドへ分離する=Trial専用の出力形式`violation_spans`)の検証用実装、限定確認(有料)。
- 到達上限Status: なし(Trial内の検証。`VALIDATED`判定・Production採用判断はFable/ユーザー)。
- 禁止事項:
  - Production正式pathの変更禁止。`er003_v1_en_direct_vfl_01_generate.py`は読むだけ(Checker本体のPrompt・schemaは編集しない)。Trial専用の追記・schema拡張はrunner側の既存の仕組み(`build_deviation_schema_with_enumeration`、`build_recheck_schema`、`run_recheck`のTrial追記、er051のV4Aブロックの方式)で行う。
  - **判定基準(何を逸脱とするか、severity、10種類のflagの基準)は変えない。変えるのは違反箇所の出力形式だけ。**
  - 新スイッチは既定OFF(現行の挙動のまま)。既存テスト・`HANDOFF_MODE=legacy`・固定fixtureが動き続けること。
  - 受け渡しの方針を変えない(再推測しない/複数文は複数文のまま/複数範囲は複数範囲のまま/類似度で縮小しない/最小修正優先: 語句→文→必要最小限。最初から文全体へ広げない)。
  - flow全体のTrial(複数周回のRewriteを含む実行)は回さない。限定確認はChecker呼び出し+オフライン集計に限る(下記)。
  - `git add -A`/`stash`/`amend`禁止。既存の未commit差分・並行タスクのファイルに触れない・addしない。SSOT(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`REPORT_LEDGER.md`/`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`)と既存の設計書・REPORTを編集しない(追記文案はRESULT_PACKETと最終メッセージに書く)。
- 費用上限: 上限¥30(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥515.0181、総枠はユーザー決定で¥900(2026-10-03)。ユーザー指示: 「予算は使い切る目標ではありません。不要な再測定・全文Recheck・不要Rewrite・同じEvidence取得・惰性的retryは禁止」。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 条件A(Checker出力構造の変更)に該当するが、この設計(配列`violation_spans`を唯一の情報源にし、`claim_in_article`はコードが組み立てる、`same_fact_id_locations`は別のまま、空配列は人間確認)は設計書`docs/pm/design_open233_countermeasures_after_handoff_01.md` §3としてOpus独立レビュー#6(`docs/pm/opus_l2_review_open233_self_recovery_06.md` 論点6)でレビュー済み(Opusは形に同意、時期は「今は入れない」と述べたが、ユーザーが2026-10-03に検討・限定確認を指示)。**設計書§3と異なる形にする場合は実装せず報告する**(再レビューが必要になるため)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する)。
T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。(本委任はTTSを伴わない。)
T-3: 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_53.md`。一時ファイルはリポジトリ外(`%TEMP%`配下)。`RESULT_PACKET.md`は委任_51が終わるまで使用中なので、本委任の報告は最終メッセージに書き、`RESULT_PACKET.md`は作業の最後に上書きする(addしない)。

## ユーザー指示(原文、2026-10-03)

### 4-2. Checker説明文混入12件

次工程で、**原因調査だけでなく、対策検討・必要なら実施・確認まで**行ってください。

最低限、12件それぞれで何が混入したか/なぜ違反箇所フィールドへ説明文が入ったか/Prompt起因か/出力形式起因か/後段処理起因か を分類してください。

有力案として、**違反箇所フィールドには記事原文だけを入れ、説明・理由は別フィールドに分離する**方式を検討してください。必要なら検証用Prompt/出力形式で限定確認して構いません。

確認項目: 特定不能率が下がるか/検出漏れが増えないか/false PASSが増えないか/Human Reviewが増えないか/コストが悪化しないか

および「判定基準そのものは変えず、**違反範囲の出力形式だけを変える**こと。」(2026-10-02)、「最初から文全体Rewriteへ広げないでください。」、「Production正式pathは変更禁止です。」

## 作業1: 12件の原因分類(¥0)

委任_45の分類(`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_45_result.md` §2、`er052_output/open233_handoff_log_aggregation_01/unverified35_classification_01.csv`)のC3=12行/9種類(U01・U02・U06・U08・U09・U10・U11・U12・U13)について、1行ずつ表にする: Checker文字列(逐語)、混入したもの、なぜ違反箇所フィールドへ入ったか(推定と根拠)、起因の分類(Prompt/出力形式/後段処理、主因1つ)、新しい出力形式(配列)で解消する見込み(見込める/条件付き/見込めない)と理由、固定fixtureの再生か実LLM出力か。

## 作業2: 検証用の出力形式の実装(Trial専用、既定OFF)

設計書§3-1〜§3-5の形で実装。スイッチ名 `CHECKER_SPANS_MODE`(既定`"legacy"`、`"violation_spans"`)。
2-1. Trial側schema(Stage 1初回とRecheck両方)に`violation_spans`(文字列配列)を追加し、Trial追記ブロックで書き方を指示。文案は設計書§3-2を土台に、「文の一部だけが問題でも、その語句を含む文全体を引用」の行は使わない。「問題の語句だけを引用してよい。ただし記事内でちょうど1箇所に定まる長さにする(短すぎて複数箇所に一致する場合は、一致が1箇所になるまで前後へ広げる)」とする。引用は英語記事本文から。位置の説明・理由・接続語は`issue`/`explanation`へ。指せない場合は空配列。
2-2. 受け取り側: `violation_spans`が非空なら各要素を既存の照合(`resolve_violation_spans`の各レベル。`VS_MATCH_EXT`がONならL5・単語境界も)で要素ごとに確定し、全要素確定した場合だけ確定(1つでも確定不能なら全体を確定不能→人間確認、理由コードに要素番号)。`claim_in_article`はコードが配列から組み立て(改行区切り)、Stage 2表示・`prior_issues`・同一判定は確定範囲から作る(委任_42の仕組みそのまま)。空配列→確定不能(`violation_spans_empty`)。`same_fact_id_locations`は別のまま。
2-3. 固定fixture(配列が無い)は既存の`claim_in_article`経路で読む(アダプタ)。`legacy`では一切挙動不変。
2-4. テスト: U01〜U13の実文字列で、配列として返った場合に各要素が確定すること/説明文混入要素が確定不能になること/空配列が人間確認になること/legacyで既存と同じこと。既存テスト(406件)全PASS、er052回帰、プロジェクト全体回帰(既存失敗11件以外に新規なし)。

## 作業3: 限定確認(有料、Guardrail ¥30。Checker呼び出し+オフライン集計のみ)

目的: 確認項目5つを、対照(現行形式)と処置(`violation_spans`)で同じ記事・同じLedger・同時期に比べる。flowは回さない。
- 記事: `hormuz_run03_standard`、`neg1_meta_b3prod_a2`、`bgroup_B4`、`safety_A4`+`meta_run03_standard`+Safety対照`safety_er009_changed_number`。計6記事。cycle1の本文・Ledger・日本語原文。
- 腕: 対照=現行Stage 1相当(`prior_issues`なし)、処置=`CHECKER_SPANS_MODE=violation_spans`。モデル・effort等はStage 1と同一。
- 回数: 6記事×2腕×n=3=36 call。単価約¥0.61/回、約¥22。最初に1記事×2腕×1回(probe)で形式と単価を確認し、見込みが¥30超ならn=2。
- 集計(オフライン): 1.特定不能率(MAJORのみ、VS_MATCH_EXT=ON、処置は要素ごとも) 2.検出漏れ(正解ラベル、`meta_run03_standard`のMUSE-HC-010は軽微のためBLOCKING除外・参考別掲) 3.false PASS 4.Human Review影響 5.コスト 6.出力失敗 7.対照どうしの揺れ幅。
- 結論は書かず数値と当てはめだけ。回数が少ないことを明記。

## 作業4: SSOT・設計書への追記文案(本文は編集しない)

最終メッセージに、`DECISION_LOG.md`、`OPEN_ITEMS.md` OPEN-233行の次Action、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §38、設計書§3への追補(12-2. 委任_53の結果)の案文を書く。

## 事前指定Read一覧

(委任文原本のとおり: 委任_45 result §2/§5、unverified35_classification_01.csv C3行、design_open233_countermeasures_after_handoff_01.md 288〜362/494〜520行、opus_l2_review_open233_self_recovery_06.md 論点6、runner各Grep、er051 V4A、er003 DEVIATION_PROMPT_TEMPLATE(読むだけ)、er052_open233_detector_direct_compare_01.py、check_rep22_01.py、design_open233_self_recovery_flow_01.md 正解ラベル)

## 実行コマンド(要旨)

runnerのテスト: `.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01`
er052回帰: `run_project_regression.py --pattern "er052*_test_*.py"`、全体回帰1回。
限定確認: `er052_open233_checker_spans_format_compare_01.py --stage probe` / `--stage main --n 3 --budget-jpy 30` / `--stage agg`。出力先 `er052_output/open233_checker_spans_format_compare_01/`。予算stateは専用ファイル。回帰後に`git status --porcelain`で意図しない変更を確認、あれば`git checkout -- <file>`。

## Git

- SSOT編集権なし。
- 1回目commit(実装・テスト・回帰後、測定前): runner、runnerテスト、本委任文、`_check.json`。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: Checker違反箇所の出力形式(violation_spans配列、説明は別フィールド)をTrial専用スイッチで実装(既定OFF、判定基準は不変、Production未変更)(委任_53)`
- 2回目commit(測定後): `er052_open233_checker_spans_format_compare_01.py`と結果ファイル。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 違反箇所の出力形式の限定確認(6記事×2腕、Checker呼び出しのみ)を実施し結果を記録(委任_53)`
- 各commit前に`git status --porcelain`確認。fetch後fast-forwardのみ。競合等は報告して止まる。`git push origin main`まで。

## 報告項目

(1)結論10行以内、(2)作業1の表と起因集計、(3)実装の要点(スイッチ、関数、Prompt追記ブロック逐語、`claim_in_article`読み取り箇所対応)、設計書§3と異なる点、(4)テスト件数、回帰、(5)作業3集計表7項目、probe単価、実行回数、費用(今回・Phase累計・残額)、(6)作業4案文、(7)ユーザーへ戻す条件の有無、(8)T-0・commit hash・push・raw URL、一覧外Read、確認事実と推測の区別。

(注: 本保存ファイルは長大な固定文の一部を要旨化している。実行層が受領した原文の詳細は上記のとおり。)
