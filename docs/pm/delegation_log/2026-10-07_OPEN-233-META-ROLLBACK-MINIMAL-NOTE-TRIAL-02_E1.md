# 委任_E1 簡略保存 (OPEN-233-META-ROLLBACK-MINIMAL-NOTE-TRIAL-02、上限JPY60)
## 管理ID
OPEN-233-META-ROLLBACK-MINIMAL-NOTE-TRIAL-02 委任_E1。前回と同条件で追加N=10を並列実行し累積集計。
## 性質/到達上限Status/禁止事項
Trial実行(有料)+評価+Closeout。到達上限USER_DECISION_REQUIRED。Note/prompt/runner変更、Production変更、git add -A禁止。
## 固定ブロック
E-1 上限JPY60。D-1 cost.jsonにtrial02_*追記。G-1 Trial限定。F-1 fail-closed、失敗は代替追加。T-0簡略保存。T-2 TTSなし。T-3 対象外。
## ユーザー指示(原文、要点)
前回と完全同条件で追加N=10、同時並列、rollback段落を全文保存し正しい/曖昧/重大誤読の3分類、累積N=15集計、Control参考と比較、統計断定なし。
## 事前指定Read一覧
runs/manifest.json、eval/E_rollback_minimal_note.md、ledger/FREEZE.json。
## 事前指定Grep一覧+追記位置・更新位置の手順
rep7〜16同時起動、失敗は代替rep17〜、provenance確認、評価ファイルtrial02、REPORT §92、DECISION_LOG、OPEN-237、ACTIVE_TASK。
## 実行コマンド全文
OPEN233_RUNS_ROOT/OPEN233_B3_VARIANT=nb、er052_open233_polysemy_nb_dev_01.py --phase phase1 --slug meta --theme ... --ledger-txt nb --out-dir rep<k> --budget-jpy 8 --yes-run-paid。T-0 check_delegation_prompt.py。
## SSOT追記文
REPORT §92、DECISION_LOG 1エントリ、OPEN-237追記、ACTIVE_TASK行。
## Git
個別git add、commit、push origin main。
## 報告
有効N=9、累積N=14、実費約JPY62(上限超過推定)。
