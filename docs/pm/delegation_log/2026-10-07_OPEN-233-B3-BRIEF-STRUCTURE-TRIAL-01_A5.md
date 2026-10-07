# 2026-10-07 OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 委任_A5(段階2: 2並列worker停止→単層4並列+自動降格で再開)

Management-ID: OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01(委任_A5)
管理ID: OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01(委任_A5)

## 管理ID・並行タスク(重要)
別のsonnet-worker(委任_A4、並列<=2で段階2を実行中)がまだ動いている可能性がある。本委任の最初の仕事はそのdriverを安全に止めること。委任_A4は docs/pm/ACTIVE_TASK.md/RESULT_PACKET.md/STAGE2_RUN_CHECK.md/cost.json を編集・commitする可能性があるため、本委任ではこれらを最後の工程でのみ編集し、編集直前に再読込する。git commit前に .git/index.lock の有無を確認し、あれば最大5分待って再試行。

## ユーザー決定(2026-10-07、原文)
> 1. B3 Writer段を5条件・60本の既存計画で、並列2以下にして再開するか -> YES
> 2. 承認なしでV5・Writer段を開始した件をPM Gate違反として正式記録し、承認記録必須の再発防止を入れるか -> 不要
> (追加)単層4並列+自動降格への切り替え -> yes

## 性質/到達上限Status/禁止事項
- 性質: Trial(DEV専用)。段階2(driver_stage2.py: V0/V1/V3/V5/V6 x 3テーマ x b1-b4=60 run、Writer 1本/brief、--no-checker、phase1->phase2)+追加B3 brief(未生成分)を単層4並列で完走させる。
- 到達上限Status: STAGE2_COMPLETE または予算/異常STOP。Production採用判断はしない。
- 予算: Trial累計(段階1 55.49円+クラッシュ前段階2約68.27円+委任_A4消費分+本委任)で500円上限、480円到達見込みでSTOP。1 run 15円超の異常runでSTOP。
- 並列ルール: 同時実行プロセスは合計4以下、単層のみ(xargs -Pとdriver内スレッドの二重並列禁止)。最初の4 run完了時点で1プロセス最大メモリと空きメモリ/コミットチャージを実測・記録。空きが「1プロセス最大x2」未満なら並列2へ降格。MemoryError/WinError 1455が再発したら即並列2へ降格、それでも再発なら並列1で1回だけ再試行、以後STOP。
- 禁止: Production変更(er019 B3本体・Production runner・CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・REPORT編集)、Checker有効化、条件・テーマ・brief本数の追加、V2追加、仮説・判定規則の実質変更、残11 run再開、git add -A、段階1成果物(brief)の削除。
- 固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(TTSなし)。

## 事前指定Read
driver_stage2.py, run_stage2_b3.sh, PLAN.md, cost.json, logs/driver_stage2.log末尾, PM-CRASH-DATA-INTEGRITY-CHECK-02_result.md, 委任_A4文, eval/STAGE2_RUN_CHECK.md(あれば), design_01.md 5/7節, blinding.md, make_blind_copies.py, eval_assignment.md, aggregate_b3.py

## 更新位置
(1)並列度を4に設定+降格ロジック(4->2->1)をdriver側に最小追加。(2)design_01.md 5節末尾の事前登録(A4が追記済みなら重複追記しない)。(3)make_blind_copies.py b1..4・w1対応(MAP_stage2.json別名)。(4)eval_assignment.md 60記事・20本/テーマ。(5)eval/STAGE2_RUN_CHECK.md に run分類表・メモリ実測・降格履歴。(6)cost.jsonに段階2費用を段階1と分離して追記。(7)ACTIVE_TASK.md固定ヘッダ更新+B3行末尾に結果1文。(8)RESULT_PACKET.md上書き(10行以内)。

## 実行手順
0. 旧driverの安全停止(STOPファイル/Stop-Process。他のpythonは触らない。停止時刻・方法・PID記録。STOPファイルは再開前に削除)。
1. 現状棚卸し(0円): 60 runを完了/再実行要/未開始に分類。再実行要はrun単位で削除し同枠再実行(削除前に一覧記録)。
2. 不足brief(V0/V1/V3/V6のb3/b4未生成分)を並列<=4で生成、sent_match確認。
3. 更新位置(1)-(4)準備。
4. 単層4並列でdriver再開(完了済みスキップ)。最初の4 run完了時にメモリ実測。10 runごとに累計費用確認。STOP条件: 累計480円見込み/異常run15円超/メモリ再発(降格後)/連続失敗3件。
5. 完走後: 内訳、実費、1 run平均・最大、累計(復元不能分は「不明(推定X円)」)、メモリ・降格履歴、cost.json整合、Production未変更確認。
6. Git: 個別add、commit(trailer Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>)、push origin main。競合・失敗時はSTOP。
7. 記事の評価・盲検レビューは開始しない。

## 報告
最終メッセージに18行以内: 旧driver停止方法・時刻、到達Status、60 run内訳、費用、メモリ実測・降格履歴、STOP有無、Production未変更根拠、事前登録追記1-2行、commit hash・push結果、check結果、raw URL一覧。
