## 管理ID

OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02(委任_01: 再分類用AIの問いを精緻化し、既存42 run候補を比較可能条件で再分類する追加Trial。ユーザー承認済み)。並行タスクなし。本委任がgit・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ。

## 性質/到達上限Status/禁止事項

- 性質: Trial。到達上限 **VALIDATED**(Production採用ではない)。最終分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)はFableが行うため、Sonnetは事実とラベル付き所見のみ報告する。
- 変更範囲: **再分類用AIの問い(prompt)の精緻化だけ**。以下は禁止: 「Ledgerに明記されていない」だけでの候補化/比喩・つなぎ・一般論・修辞文の再候補化/機械Checker(決定論ルール)変更/後段AI判定(Stage 2等)変更/機械Safetyルール変更/KPI変更/E2E残11 run再開/Production Checkerへの実装/gold定義変更/runner `er052_open233_self_recovery_flow_runner_01.py`・coverage_checker・Stage 1本体の変更/新しい数値KPIの設定/前回Trial(01)の出力の上書き。
- モデル・effort・temperature・入力構成(Ledger全文+記事本文+候補一覧、run単位1 call)は前回(01: gpt-6-luna、effort=medium)と**同一**にする(比較可能性)。変えるのはprompt本文のみ。
- 費用: **ユーザー承認済み想定¥10〜12。¥12を超える見込みが出た時点で実行せずSTOPして報告。Fable/Sonnet判断で予算枠を拡大しない。** `--budget-jpy 12`。T-3定型の「継続条件での超過継続」は本委任では**適用しない**(ユーザーが明示的に¥12上限を指示)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: **非該当**(Trial用分類promptの精緻化のみ、構造変更なし)。
- `git add -A`・`stash`・`amend`禁止。`ACTIVE_TASK.md`・`RESULT_PACKET.md`のadd禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-2追記/T-3は委任文本文のとおり。本ファイルでは省略せず要点のみ: 同一ファイル再読禁止、Grep→範囲Read、git出力最小化、transcript退避不要、本委任文の逐語保存+check_delegation_prompt.py実行、TTSなし、T-3は本委任では¥12超過見込み時点で実行前STOP。)

## ユーザー指示(原文)

> 管理ID：OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02
> 目的: 前回Trialで、通常記事の候補数を 24.2件→9.8件/記事まで削減できた一方、重大Fact基準例A4-0を3回中1回見逃した。今回は、候補を何でも拾う旧設計へ戻さず、A4-0型の「主体・相手先・対象範囲の取り違え」だけを狙って補強できるかを確認する。ユーザーはこの追加Trialを承認済み。Production採用の承認ではない。
> 今回変更すること: 記事→Ledger側のAI判定に、既存の「Ledgerと食い違っているか」「Ledgerにない具体的新事実を追加しているか」という問いに加えて、具体的Factについて以下の一致を明示的に確認させる。誰が行ったか／誰／何に対して行ったか／対象範囲が広がっていないか／限定条件が落ちたり変わったりしていないか。特にA4-0の、Ledger：契約スタッフが電話の相手先である企業・店舗とやり取り／記事：契約スタッフがMuseのユーザーとやり取り、という相手先の取り違えを確実に候補として残せるかを見る。
> やってはいけないこと: 「Ledgerに明記されていない」という理由だけで候補化する／比喩・つなぎ・一般論・修辞文を再び大量に候補化する／機械Checkerのルール変更／後段AI判定の変更／機械Safetyルールの変更／KPI変更／E2E残11 runの再開／Production Checkerへの実装／gold定義の変更。今回の変更範囲は、再分類用AIの問いの精緻化だけ。
> Trial方法: 前回と同じ既存42 runを使い、比較可能な条件で再分類する。最低限確認すること: A4-0：3/3で候補として残るか／正式gold 6種類：すべて落とさないか／hold-out 9種類：維持できるか／K19 / neg5等、前回維持できていた重大ケースを落とさないか／通常記事の候補数がどこまで増減するか／AI由来候補数が、前回の5.3件/記事からどう変わるか／2方向和集合での結果。候補数を減らすためにSafetyを緩めたり、Safety確保のために旧24件/記事へ戻したりしないこと。
> 費用: 今回ユーザー承認済みの想定費用は ¥10〜12。¥12を超える見込みが出た時点でSTOPして報告すること。Claude/Fable判断で予算枠を拡大しない。
> 受入条件: 1. A4-0が3/3残存 2. 正式gold 6種類をすべて維持 3. 既存の重大見逃し検証セットを悪化させない 4. 候補数削減効果が大きく失われていない。ただし候補数について新しい数値KPIは設定しない。実測結果をそのまま報告し、ユーザーが判断する。
> STOP条件: goldを1件でも落とす／A4-0が安定して残らない／候補数が大きく旧過剰仕様側へ戻る／新しいSafety問題を発見／¥12超過見込み／Trial中に新しい仕様変更が必要になる。その場合は勝手に次の改善案を実装せず、USER_DECISION_REQUIREDとして報告する。
> Closeout: 結果を受けて REJECTED / VALIDATED / USER_DECISION_REQUIRED のいずれかに分類すること。VALIDATEDでもProduction採用ではない。Production Checker、後段Safety、E2Eは変更・再開しない。また、前回修正済みのHuman Review誤発生バグについては、今回の変更で回帰していないことだけ確認する。新たな仕様変更は行わない。

## KPI provenance欄

- Before(比較基準): reuse(段階A 42 run保存候補 `er052_output/open233_stage1_stageA_01/`)および前回Trial01結果(`er052_output/open233_reclassify_01/reclassify_aggregate.json`、frozen)。
- After: fresh(精緻化promptによる分類call 42回)をreuse候補集合へ適用。Checker本体再実行なし。
- E2E自己確認: No。
- 判定単位: run別・instance群別(SC 6x3/B2_hormuz n=3/NORMAL 6x2/hold-out 9)。gold 6件xsample別。

## Opus台帳更新

OF-027(EVIDENCED)に本Trial02の結果を追記(状態は変えない)。他は該当なし。

## 事前指定Read/Grep一覧、実行コマンド、SSOT追記文、Git、報告項目

委任文本文の手順1〜8(T-0 check実行、scriptコピー+prompt変更のみ、見積較正、見積mid>¥12ならSTOP、`--stage run --yes-run-paid --budget-jpy 12`、agg、LastResort回帰+`run_project_regression.py --pattern "er052*_test_*.py"`(基準863件)、記録、明示add→commit→push)、集計必須項目、SSOT追記文(OPEN_ITEMS RECLASSIFY-01行末尾/REPORT_LEDGER/REPORT §78/DECISION_LOG)、Git明示add対象(`er052_output/open233_reclassify_02/`配下、`docs/pm/reclassify_open233_checker_selectivity_02.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、REPORT、本ファイル+_check.json)、RESULT_PACKET報告項目1〜13は、受領した委任文のとおり。

prompt精緻化の内容(委任文より): 既存3択と既存基準は維持。SUPPORTED判定前に具体的Factごとに(i)主体(ii)相手先・対象(iii)対象範囲(iv)限定条件の4点をLedgerと照合し、1つでも不一致ならCANDIDATE。出力に`actor_match/counterpart_match/scope_match/qualifier_match`(match/mismatch/n_a)と1行理由を追加。A4-0名指し・instance固有語(Muse/users/企業・店舗等)はpromptに入れない(抽象例は1つまで可)。見積器は01実測のreasoning token実測比で較正する。
