# 委任_09 委任文全文(FACTLOCK-ASTRA-E2E-TRIAL-01、2026-10-09、Fable->Sonnet)
管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_09(注記A/Bの抽出→検査→統合→監査、hormuz・streaming_priceのB3再生成1回とプロンプト再構築。API支出上限 ¥3[B3再生成2本、luna]。他は¥0)。日付 2026-10-09。並行して委任_05(runner実装、¥0)が走っている可能性あり。委任_05のファイルには触らない。git index.lock衝突時は10秒待って最大5回再試行。

## 前提
- 注記者A/Bの出力: `er052_output/factlock_astra_e2e_trial_01/annotation/out/{A,B}/<slug>/reply.md`(10テーマ×2)。手順書 `annotation/RUN_ANNOTATION.md`、監査設定 `annotation/audit_config.json`、スクリプト `b3_annotation_check_01.py`・`b3_annotation_merge_01.py`・`b3_annotator_audit_01.py`・`annotation/audit_strict_01.py`。
- 既知の状況(Fable観察、要検証): streaming_price B は `=== STOP ===`(§4(ii): Storylineの「3種」が台帳外の導出数)、A は周辺で続行。hormuz は新B3のSelected Facts節が箇条書きでなく「Storyline:」重複行+「素材:」段落のため facts=[](両者一致)。central_bank_mortgage は A/B で事実4のledger_ids(F007 vs F007,F006)と「30年」/「30年固定」の表記差。inbound_tourism は行頭「・」のまま【事実N】を挿入(A/B共通)。openai_copyright/semiconductor/byd は段落形式で1事実に多数IDが紐付く。
- Fable判断: (1) 注記者がSTOPした、または facts=[] で【事実N】が付かないテーマ(streaming_price、hormuz)は、**B3を1回だけ再生成**(凍結台帳から、Production B3段のみ、research非実行、委任_06/_07と同手順・証跡)し、再注記する。再生成後も同じ問題なら当該テーマは「注記不能」として記録し、Fableへ報告(入替判断)。(2) 統合の食い違いは統合スクリプトの規則で機械解決、手直し禁止。(3) 行頭「・」への【事実N】挿入は、harnessの `FACT_LINE_RE` が行頭 `- 【事実N】` しか読まない場合は検査FAILになる。その場合は「・」→「- 」置換を**許容差分として記録した上で機械変換**するか、FAILのままSTOPかを、仕様v2 §1/§5の文言に照らして判定し、判定根拠を報告(仕様変更はしない。仕様が許していなければSTOP記録)。

## 作業
1. 20件の reply.md から注記版md・サイドカーを抽出(RUN_ANNOTATION.md の手順)。STOP出力はそのまま記録。
2. 各A/B版に `b3_annotation_check_01.py` を実行(--spec、--ledger、--brief、--json[fact_selection_evidence]付き)。結果JSONを `annotation/check/{A,B}/<slug>.json` に保存。
3. `b3_annotation_merge_01.py` で統合→統合版に再検査。一致率(分割一致率・中核Jaccard)を記事ごとに算出、判定線(0.8/0.67)との照合。統合版を `annotation/final/<slug>/{selected_brief_factlock.md, annotation.json, fact_selection_evidence_factlock.json}` に保存(JSON側はmdと同じ規則で注記した `selected_fact_brief_text`)。
4. 事後監査: subagent transcript は `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\f2c17cf7-6207-4666-abec-016808eac6d3\tasks\*.output` にある(JSONL)。本日(2026-10-09)作成のファイルのうち、本文に `annotation\prompts\<slug>__{A,B}.md` のパスを含むものを当該注記者のtranscriptとして特定し、`b3_annotator_audit_01.py` と `annotation/audit_strict_01.py` の両方で監査(許可Read=自分のプロンプト1ファイル、許可Write=自分の reply.md のみ)。結果を `annotation/audit/<slug>__{A,B}.json` と要約 `annotation/AUDIT_SUMMARY.md` に。transcriptを特定できない場合は「監査不能」と記録。
5. hormuz・streaming_price: B3再生成(各1回、¥約0.4)→`stage_r/<slug>/storyline_b3_v2/` に保存(v1は残す)、`FROZEN_INPUTS_SHA256.json` に v2 を追記、`annotation/build_prompts_01.py` で当該2テーマのプロンプトを再構築(`annotation/prompts/<slug>__{A,B}.md` は v1 を `_v1` に退避し v2 を同名で作成、`PROMPT_SHA256.json` 更新)。再生成B3が同じ問題(箇条書きなし/台帳外の導出数)を持つかを事前に機械判定して報告(持っていればプロンプトは作るがFableへ「再注記しても無駄」と明記)。
6. `annotation/ANNOTATION_SUMMARY_01.md`: テーマ別の検査結果(PASS/FAIL/STOP)、事実数、中核/周辺数、cap_dropped、unmapped_claims種類別件数、A/B一致率、監査結果、B3形式の観察(箇条書き/段落/重複行の別、1事実あたりの台帳ID数)。
7. 記録: 委任文全文 `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_09.md`、check結果、`_09_result.md`(RESULT_PACKET.md は使わない)。`docs/pm/REPORT_LEDGER.md` 1行。commit: `annotation/`・`stage_r/`配下・委任記録を明示的に `git add`、push、hash+raw URL報告。

## 禁止事項
- Astra・Writer段以降の実行禁止。注記の手直し禁止(統合は機械)。仕様v2・テンプレート・スクリプトの規則変更禁止(バグ修正が必要な場合は修正内容を報告し、修正前後の結果を両方保存)。既存コード・SSOT本体編集禁止。上限¥3超過禁止。

## 報告形式(result.md)
1. 成果物パス・commit hash・raw URL 2. テーマ別表(check A/B/統合: PASS/FAIL/STOP、分割一致率、中核Jaccard、判定線超え、監査結果) 3. 問題テーマ(hormuz/streaming/他)の状況とB3 v2の機械判定結果、再注記の要否 4. 「・」行頭問題の判定と根拠 5. バグ修正があればその内容 6. 未確認・Fable判断要 7. 所要時間・API支出
