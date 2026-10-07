# 2026-10-07 OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 委任_B1(段階3=記事評価の準備、¥0)

Management-ID: OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01(委任_B1)

## 管理ID・並行タスク
並行タスクなし。直前commit 50c95733(段階2 STAGE2_COMPLETE: 完了55/WRITER_GATE_STOP 5、累計≈¥434.5/¥500)。

## 性質/到達上限Status/禁止事項
- 性質: 記事評価(段階3)を盲検で実施するための準備のみ。API呼び出し禁止(¥0)。記事の採点・順位付け・仮説判定は本委任では行わない(盲検性を守るため、準備担当は条件ラベルと記事内容の対応を評価者へ漏らさない)。
- 到達上限Status: `EVAL_READY`。
- 禁止: Production変更、SSOT編集、Trial条件・仮説・判定規則の変更(§5/§5-A4/§5-A6の事前登録は変更しない)、記事本文の編集、既存MAP(段階1盲検)の上書き、`git add -A`。
- 固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(TTS・APIなし。T-0=本委任文を `docs/pm/delegation_log/2026-10-07_OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01_B1.md` へ保存し `python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json` で検証。FAILなら見出しを補って再検証し、結果を報告)。

## 事前指定Read
- `docs/pm/b3_trial_01/design_01.md` §5・§5-A4・§5-A6、`eval_rubric.md`、`blinding.md`、`eval_assignment.md`、`human_review_pack_template.md`、`make_blind_copies.py`、`aggregate_b3.py`、`brief_features.py`、`article_schema.json`
- `er052_output/open233_b3_trial_01/eval/STAGE2_RUN_CHECK.md`(A5/A6/A6b節)、`eval/inventory_after_A6b.json`、`runs/writer_gate_stop_final.json`、`PLAN.md`、`eval/unprovided_checklist*`(3テーマ分)
- `docs/pm/opus_l2_review_b3_trial_01.md`(評価段に関する指摘M5/M6/O1/O2のみ)

## 事前指定Grep一覧+追記位置・更新位置
- Grep: `aggregate_b3.py` 内の本数前提(72/24/b1,b2/w1,w2)、`make_blind_copies.py` の `--stage2` 実装、`eval_assignment.md` の評価者割当・本数。
- 更新位置: (1) `make_blind_copies.py --stage2` で `eval/blind_stage2/<slug>/` に55記事を匿名IDでコピー、`MAP_stage2.json` を評価者が開かない場所に置き `blinding.md` に保管場所と開封条件を追記。WRITER_GATE_STOP 5件は `eval/writer_gate_stop_summary.md` に条件別件数(V0 0/V1 0/V3 1/V5 4/V6 0、Gate種別)を記録(非盲検の副次指標、§5-A6)。(2) `aggregate_b3.py` を60記事・b1〜b4・w1・欠損(Gate STOP)対応へ更新しダミー採点で確認(§5-A4の「b1〜b4多数同符号・同数は保留」、期待順位は既存EXPECTのまま)。(3) `eval_assignment.md` を最終化(評価者は条件ラベルを見ない、seed固定シャッフル)。(4) 評価パックを `eval/eval_pack_stage2/` に生成(rubric全文+未提示チェックリスト+匿名記事一覧+`scores_template.json`)。(5) `docs/pm/ACTIVE_TASK.md` 固定ヘッダ(Status=EVAL_READY、次アクション=評価委任)とB3行末尾に1文追記。(6) `docs/pm/RESULT_PACKET.md` 上書き(10行以内)。

## 実行コマンド全文(要旨)
1. `.venv/Scripts/python.exe er052_output/open233_b3_trial_01/tools/make_blind_copies.py --stage2` → 55記事・MAP生成の確認。
2. `aggregate_b3.py` 更新→ダミー採点でテスト(既存pytest実行、PASS件数を報告)。
3. 評価パック生成、`eval_assignment.md` 最終化。
4. Git: 個別add(eval配下の blind_stage2/eval_pack_stage2/writer_gate_stop_summary.md、docs/pm/b3_trial_01/*、本委任文+check.json)。MAP_stage2.jsonはcommitしてよいが評価者へ渡すファイル一覧には含めない。commit message例「OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 B1: 段階3評価準備...、¥0、Production変更なし」+ trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。push origin main。

## SSOT追記先
なし。

## 報告
最終メッセージに: 到達Status、盲検コピー件数・MAP所在、aggregate更新内容とテスト結果、評価割当、評価パックの所在、次に評価者インスタンスへ渡す最小委任内容、commit hash・push結果、check結果、raw URL一覧。18行以内。
