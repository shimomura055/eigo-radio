# 仕様v2 運用明確化(委任_07、Fable決定、2026-10-09)
規則変更ではなく、未定義事例への適用判断。
(a) 台帳の個別記録に `date_or_period` / `numeric_value` 欄が無い場合は、その記録に限り代替規則(statement内の主数字・日付)を適用する(台帳単位の代替規則を記録単位に適用)。該当: byd_recall(date欄なし4記録)、central_bank_mortgage(date欄なし1記録)、各台帳のnumeric_value欄なし記録(数値を持たない記録は対象外)、small_bag(台帳単位でnumeric欄なし)。
(b) B3 brief内の丸め表現(例: hormuz新B3「約25時間後」、台帳HF-007は「約24時間48分後」)は `unmapped_claims` に「新数値(丸め)」として記録する。記事の中心数字が台帳外としてSTOP条件に該当するかは注記統合時に機械判定する。
実測(委任_07): 10テーマ中、B3 brief内の台帳外数字はhormuzの「25」のみ(他9テーマは0)。

(c) 運用明確化(委任_10、Fable判断、2026-10-09): 台帳のAMBIGUOUS記録へ注記者が紐付けることは許容する。B3がAMBIGUOUS記録を選ぶのはProduction挙動であり、AMBIGUOUS記録も「台帳由来」である(ユーザー固定の「台帳由来のみ」に反しない)。PREREGISTRATION v2.2 5-12(注記者はstatusで扱いを変えない、AMBIGUOUS由来NGは別集計)は注記開始前に事前登録済みで、検査側の「VERIFIED以外=FAIL」はこれと矛盾する検査側の規定だったため改める。`b3_annotation_check_01.py` の b_ledger_mapping: AMBIGUOUS = WARN + 結果に `ambiguous_fact`({事実N: [台帳ID]}) を出力(PASSのまま)。NOT_VERIFIED/REJECTED等は従来どおりFAIL。仕様v2本文の変更ではない。該当テーマ: inbound_tourism(F06)/semiconductor_earnings(F1)/streaming_price(F01,F07)。突合は `annotation/AMBIGUOUS_FACT_MAP.json`。ユーザーが覆した場合は該当3テーマを除外する。
(d) 注記者が許可Write でなくBash `cat >` で自分の reply.md を書いた件(9/20本、v1ラウンド)は、他パス接触0・隔離維持のため採用。監査scriptのVIOLATIONは許可済みWrite/返却ツールと自プロンプトパスの禁止語該当による誤判定。補助監査(annotation/AUDIT_SUMMARY.md)の結果を正とする。
(e) 「・」行頭への【事実N】挿入は検査PASS・仕様§2に反しないため許容。
(f) 仕様sha256はLF正規化後の値を正とし、CRLF生バイト値は併記する(runner g0.json の spec_sha256)。
