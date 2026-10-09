# 委任_10 委任文全文(FACTLOCK-ASTRA-E2E-TRIAL-01、2026-10-09、Fable->Sonnet)
管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_10(運用明確化(c)=AMBIGUOUS台帳IDの紐付け許容を検査スクリプトへ反映、semiconductor_earningsの統合、統合済みテーマのrunner入力配線とG0実照合。API支出¥0)。日付 2026-10-09。並行して注記者subagent(hormuz/streaming_price/inbound_tourism のA/B再注記、`annotation/out/{A,B}/<slug>/reply.md` への書込みのみ)が走っている。それらの出力ファイルには触らない。git index.lock衝突時は10秒待って最大5回再試行。

## Fable判断(記録すること)
- (c) AMBIGUOUS台帳IDの扱い: B3がAMBIGUOUS記録を選ぶのはProduction挙動であり、AMBIGUOUS記録も「台帳由来」である。ユーザー固定の8項目(台帳由来のみ)に反しない。PREREGISTRATION v2.2 5-12(注記者はstatusで扱いを変えない、AMBIGUOUS由来NGは別集計)は注記開始前に事前登録済み。よって `b3_annotation_check_01.py` の「VERIFIED以外のIDへの紐付け=FAIL」は、事前登録と矛盾する検査側の規定として、AMBIGUOUSに限り許容+`ambiguous_fact` フラグ付与(WARN)へ改める。NOT_VERIFIED/REJECTED等は従来どおりFAIL。仕様v2本文の変更ではなく運用明確化(c)として `stage_r/SPEC_V2_CLARIFICATIONS.md` に追記(ユーザーが覆した場合は該当3テーマを除外する旨も記録)。
- (d) 注記者がWriteでなくBashの `cat >` で自分の reply.md を書いた件: 他パス接触0・隔離維持のため採用。監査スクリプトのVIOLATIONは「許可済みWrite/返却ツール」と「自プロンプトパスの禁止語該当」による誤判定で、補助監査(AUDIT_SUMMARY.md)の結果を正とする。
- (e) 「・」行頭への【事実N】挿入は検査PASS・仕様§2に反しないため許容(記録)。
- 仕様sha256はLF正規化後の値を正とし、CRLF生バイト値は併記。

## 作業
1. `b3_annotation_check_01.py` の該当規則を(c)どおりに修正(修正前を `annotation/prefix_scripts/` に保存済みなら追加保存)。既存テスト `test_non_verified_ledger_id_in_facts_fails` は「NOT_VERIFIEDはFAIL、AMBIGUOUSはWARN+flag」に分けて更新。テスト全件PASS。`annotation/AMBIGUOUS_FACT_MAP.json` との整合確認。
2. semiconductor_earnings: A/B再検査->統合->統合版再検査->`annotation/final/semiconductor_earnings/` 生成。一致率算出。
3. runner入力配線: `annotation/final/<slug>/` の7テーマ分(byd_recall, central_bank_mortgage, meta, openai_copyright, small_bag, space_weapons, semiconductor_earnings)を runner が読む `er052_output/factlock_astra_e2e_trial_01/inputs/<theme>/` へ配置(`selected_brief_annotated.md`、`annotation.json`、注記版 `fact_selection_evidence.json`、委任_05 result.md 4節の入力規約に従う。元B3・台帳は stage_r を参照)。runnerのG0照合(`er052_factlock_astra_e2e_runner_01.py` のG0サブコマンド)を実注記で7テーマに実行し、全PASSを確認(FAILなら原因と修正案を報告、runner側の修正は最小限・テスト付き)。整合検査スキップになっていた注記版JSONの検査も実施。
4. 残り3テーマ(hormuz/streaming_price/inbound_tourism)の再注記が `annotation/out/{A,B}/<slug>/reply.md` に揃っていれば、抽出->検査->統合->final->inputs配線->G0照合まで実施。揃っていなければスキップし報告、手順を `annotation/RUN_ANNOTATION.md` 末尾に追記(次委任で実行)。
5. `annotation/ANNOTATION_SUMMARY_01.md` を更新(10テーマ表、(c)(d)(e)の記録、Bash使用注記者の一覧)。
6. 記録: 委任文、check結果、`_10_result.md`(RESULT_PACKET.md は使わない)。`DECISION_LOG.md` 末尾に(c)(d)(e)のFable判断を1節追記。`docs/pm/REPORT_LEDGER.md` 1行。commit: 変更ファイルを明示的に `git add`、push、hash+raw URL報告。

## 禁止事項
API生成呼び出し禁止。Astra・Writer段以降禁止。注記の手直し禁止。仕様v2本文・テンプレート変更禁止。既存Productionコード・SSOT本体(`CURRENT_SPEC.md`/`OPEN_ITEMS.md`)編集禁止。

## 報告形式(result.md)
1. 成果物・commit hash・raw URL、テスト件数 2. (c)反映の差分と、影響を受けたテーマの検査結果の変化 3. inputs配線済みテーマ一覧とG0実照合の結果(テーマ別PASS/FAIL) 4. 残り3テーマの状態 5. 未確認・Fable判断要 6. 所要時間・API支出(¥0)
