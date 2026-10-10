# 委任_01: Phase 1 設計・事前登録案・見積(B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02、2026-10-10)

範囲: 設計のみ。課金API 0件(JPY0)。git操作なし(add/commit/checkout/stash 未実行)。Production code・Production Prompt・CURRENT_SPEC・SSOT・ACTIVE_TASK/RESULT_PACKET 未編集。Lane A C2編集中の er012_e/jaw/er019 entertainment runner・audio runner は未読・未触。
モデル: 実行層=Sonnet。Trial設計上のB3/R0=gpt-6-luna(最新世代・最上位系かは未確認、Production同一条件のため)。

## 実施
1. 現行B3 call仕様の把握(読取りのみ)・ROOTFIX-01の cost_ledger / raw_usage から実測(平均JPY0.455/call、input 3,643/output 4,955 token、latency 43.6秒)。
2. 設計レビュー(6観点)・候補構成・数値ランク構造・Separate-call設計・Lane A interface: `er052_output/b3_rootfix_trial_02/DESIGN_REVIEW_01.md`。
3. Trial専用モジュール(新規・API不使用): `b3r2_rank_01.py`(表記抽出/規則導出/検証/タグ挿入)、`b3r2_make_dplus_01.py`→`b3r2_b3_dplus_01.py`+`PROMPT_DIFF_01.md`(Production Promptからの置換12箇所をassert・追加のみ)、`b3r2_sepcall_01.py`、`b3r2_driver_01.py`(dry-run/estimate/selftest)。
4. 検証(¥0): selftest ALL_PASS(`selftest_result_01.json`)、dry-run 9テーマのpayload生成・台帳ID抽出整合(`dry_run/`)、Production B3 file未変更(git status clean)。
5. ¥0ベースライン実測: Storyline混入(IMP 0/27)・選択Fact Jaccardノイズ床(C1 r1 vs r2 平均0.698)・D-det予備プローブ(GT一致36/38、GT中核再現20/25)。
6. PREREGISTRATION_01.md(案)、ESTIMATE_01.json(本線JPY16.0/23.5/34.5、cap案JPY50)。

## 結果を見ての基準変更について
D-det予備プローブはGT(C0 brief注記)との比較を事前に1回だけ実施したもの。合格基準(M5)はLane B仕様と常識的水準(0.90/0.80)で設定し、プローブ値は参考併記にとどめた。Phase 2のPrompt・基準はFable確認後に確定。

## 成果物
`er052_output/b3_rootfix_trial_02/`(DESIGN_REVIEW_01.md, PREREGISTRATION_01.md, PROMPT_DIFF_01.md, ESTIMATE_01.json, b3r2_*.py, dry_run/, baseline_*.json, ddet_preliminary_probe_01.txt, selftest_result_01.json)。報告=docs/pm/RESULT_PACKET_B3SEP2_01.md。
