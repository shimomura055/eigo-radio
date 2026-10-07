# 2026-10-07 OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 委任_A6(段階2 残run再開: Writer内部Gate STOPを結果として記録し、infra障害のみguard対象へ)

Management-ID: OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01(委任_A6)

## 管理ID・並行タスク
並行タスクなし(委任_A4/A5は終了。pythonプロセス0件を再確認してから開始)。直前commit 094bd2b3。

## ユーザー決定(2026-10-07、原文。変更なし)
> 1. B3 Writer段を5条件・60本の既存計画で再開 → YES(単層4並列+自動降格 → yes)
> 2. 承認なしで開始した件の違反記録・再発防止 → 不要

## Fable判断(本委任の根拠)
A5で driver が「連続失敗3件」guardでSTOPしたが、失敗の中身は infra ではなく Writer内部Gate(Advanced deviation MAJOR未解決→JA_RECHECK_REQUIRED、JA_FACT_CHECK_STOP)の発火であり、これは本Trialの観測対象となる結果である。よって (i) Writer内部GateによるSTOPは「失敗」ではなく run結果 `WRITER_GATE_STOP` として記録し、既に2回試行済みのrunはそれ以上再試行しない、(ii) 連続失敗guardは infra由来(Python例外・MemoryError/WinError・API error/timeout・rc≠0 かつ Gate記録なし)のみをカウントする、(iii) 予算上限¥500・¥480見込みSTOP・1 run ¥15超STOPは維持。ユーザー承認済み範囲(60 run・¥500)内の運用変更であり、仮説・条件・判定規則の変更は含まない。

## 性質/到達上限Status/禁止事項
- 性質: Trial(DEV専用)。残25 run(未着手21、再実行要4=V3 hormuz b1、V5 meta b2/b3/b4)の処理。
- 到達上限Status: `STAGE2_COMPLETE`(60 run全てが 完了 または WRITER_GATE_STOP として確定)または予算/infra STOP。
- 予算: 開始時CUM_BASE=オンディスク実測≈¥299+推定不明分¥20≈¥319(A5の二重計上は廃止)。累計¥480見込みでSTOP。1 run ¥15超でSTOP。
- 並列: 単層4並列、A5と同じ自動降格(4→2→1)とメモリ監視(memmon.py)を継続。
- 禁止: Production変更、Checker有効化、条件/テーマ/brief追加、仮説・判定規則変更、Writer内部Gateの緩和・無効化(`--no-checker`は既定どおり)、既に2回試行済みの4 runの再試行、`git add -A`、記事評価の開始。
- 固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(TTSなし)。

## 更新位置
(1) driver_stage2.py: 失敗分類(infra vs WRITER_GATE_STOP)、連続失敗はinfraのみ、スキップ4 runを `runs/writer_gate_stop_final.json` に記録、CUM_BASE置換。(2) design_01.md §5-A4 末尾へ WRITER_GATE_STOP 事前登録追記のみ。(3) eval/STAGE2_RUN_CHECK.md にA6節。(4) cost.json に stage2_A6 キー。(5) ACTIVE_TASK.md 更新。(6) RESULT_PACKET.md 上書き。

## 実行・報告
実行コマンド: STAGE2_WORKERS=4 driver_stage2.py(memmon併用)→ inventory_stage2.py → 集計 → Production未変更確認 → 個別add/commit/push。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT)は編集しない。最終報告は20行以内(到達Status、60 run内訳表、Gate種別件数、費用、メモリ・降格、infra失敗有無、Production未変更根拠、事前登録1〜2行、commit/push、check結果、raw URL)。
