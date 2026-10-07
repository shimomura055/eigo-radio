# 2026-10-07 OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 委任_C1(段階3 集計・事前登録に基づく仮説判定、¥0)

Management-ID: OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01(委任_C1)

## 管理ID・並行タスク
並行タスクなし(盲検評価者6本+brief_review 1本は全て完了・報告済み)。直前commit 2625244f。

## 性質/到達上限Status/禁止事項
- 性質: 盲検評価の出力(eval/articles 55件、eval/brief_review 60件)をMAP開封のうえ集計し、design_01.md 5/5-A4/5-A6 の事前登録どおり仮説判定する。API禁止(¥0)。
- 到達上限Status: EVALUATED(Trial判定の候補をFableへ提示。最終判定・SSOT反映はFable/ユーザー)。
- 禁止: 評価JSONの書き換え、判定規則・期待順位の変更、Production変更、SSOT編集、git add -A。
- 固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(TTS・APIなし)。

## 事前指定Read
design_01.md 5・5-A4・5-A6、aggregate_b3.py、eval_rubric.md、blinding.md、article_schema.json、eval/_private/MAP_stage2.json、eval/articles、eval/brief_review、eval/notes、writer_gate_stop_summary.md、runs/writer_gate_stop_final.json、brief_features.json、docs/pm/opus_l2_review_b3_trial_01.md。

## 事前指定Grep一覧+追記位置・更新位置
- Grep: aggregate_b3.pyの入出力パス・期待件数(55/60)・EXPECT。
- 更新位置: aggregate_stage2.json、SUMMARY_STAGE2.md(1)条件別x テーマ別、Gate STOP、brief_review、事前登録判定、重大NG0の意味、評価者間差、感度分析、制約、費用)、ACTIVE_TASK.md固定ヘッダ+B3行、RESULT_PACKET.md(12行以内)。

## 実行コマンド全文(要旨)
1. MAP開封を記録。2. aggregate_b3.py実行・件数検算(55/60/Gate STOP 5)。3. SUMMARY_STAGE2.md作成。4. 個別git add、commit、push origin main。

## SSOT追記先
なし(Fable判定後に別委任)。

## 報告
最終メッセージに到達Status、要点、検算結果、commit hash・push結果、check結果、raw URL一覧。25行以内。
