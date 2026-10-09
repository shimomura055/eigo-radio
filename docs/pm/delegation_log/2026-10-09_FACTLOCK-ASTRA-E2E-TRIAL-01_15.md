# 委任_15 FACTLOCK-ASTRA-E2E-TRIAL-01(2026-10-09) ラベル集約・判定線の機械照合・評価文書・人間確認パック 委任文(要約)
- 範囲: (1)3 workerのラベルを `eval/labels_merged.jsonl`+`merge_labels_01.py` に統合(重複claimの解決規則を明記、label_source維持) (2)`eval/EVAL_E2E_01.md`(到達・費用、事前登録の判定線の機械照合表[Fable最終判定は空欄]、ラベル要約、STOP/B1/案B/M1/M3/Rewriteの妥当性、観察・仮説[Fableメモの検証]、限界、OPEN候補) (3)`eval/HUMAN_CHECK_E2E_01.md`(推奨3記事の旧腕対新腕JA最終本文の対と境界例の三択質問) (4)SSOT: REPORT §111、DECISION_LOG末尾1節、REPORT_LEDGER 1行、ACTIVE_TASK固定ヘッダ(OPEN_ITEMS/CURRENT_SPECは編集しない) (5)記録・commit/push。
- 予算: API支出¥0。
- 禁止: API、runs配下・ラベル原本の編集、VALIDATED/APPROVED宣言、判定線の最終判定の記入、未確認数値の確定値記載、CURRENT_SPEC.md/OPEN_ITEMS.md編集。
- Fableの突合メモ(暫定所見)を集約時に検証し、食い違えば指摘する(結果は EVAL_E2E_01.md 5-0節)。
- git: 今回の成果物だけを明示的に `git add`(git add -A禁止)。index.lock衝突時は10秒待って最大5回再試行。
