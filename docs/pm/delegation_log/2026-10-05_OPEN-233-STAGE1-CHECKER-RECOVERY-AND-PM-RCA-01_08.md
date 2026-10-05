# 委任_08 全文(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01、PM RCA軸の後処理)

## 管理ID
`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_08)。並行タスクあり: 委任_07b(段階A有料実行。er052_output/・OPEN_ITEMS.md・REPORT・REPORT_LEDGER.md・スクリプトを編集・commit)。本委任は`docs/pm/OPUS_FINDINGS_LEDGER.md`と自分の委任ログのみ編集し、他ファイルに触れない。gitは自分の2〜3ファイルのみ明示add(index.lockは10秒待ち最大3回再試行)。報告はhandback本文。

## 性質/禁止事項
- 性質: ¥0・read-only照合+台帳更新。委任_04でbackfillしたOpus指摘台帳のうち「Fable採否=未確認(UNVERIFIED_BACKFILL)」15件(OF-003〜OF-018のうち該当分)について、各Opusレビュー(#9〜#15)の指摘に対するFableの採否・反映・Evidenceを、設計書の採否小節・DECISION_LOG・委任ログ・REPORTから特定し、台帳のStatus・採否・反映・Evidence列を更新する。記録が見つからない項目は「記録なし(未判断)」と明記し、推測で埋めない。
- 参照先(Grep→範囲Read、全文Read禁止): opus_l2_review_open233_self_recovery_0{8,9,10}.md、opus_l2_review_open233_kpi_recovery_02_1{1,2,3,4}.md、opus_l2_review_open233_production_wiring_15.md(各「Safety hole」「結論」節)。採否: design_open233_span_sentence_restore_01.md §6(Opus#9)、design_open233_stage2_safety_downgrade_01.md §7〜§8(Opus#10)、design_open233_kpi_recovery_02.md §13(#12後)・§15(#13後)・§18(#14後)、production_wiring_gap_open233_01.md §7(#15後)、design_open233_floor_alignment_01.md §8〜§9(#8)。DECISION_LOG: Grep `Opus#(8|9|1[0-5])|Opus #1[0-5]`の行のみ。REPORT §63のOpus対応表。
- 禁止: コード変更・有料API禁止。上記以外のファイル編集禁止。`git add -A`/`stash`/`amend`禁止。1回の書き込み2,500文字以下。

## T-0
委任ログ(本ファイル)に全文保存(分割)、check実行・結果をhandbackに1行。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## 作業
1. T-0。
2. 台帳の15件を1件ずつ: 指摘要旨→Opus原文箇所(行番号)→Fable採否の記録箇所(文書・§・行番号、採用/不採用/修正採用/記録なし)→反映(委任#・commit)→Evidence(テスト・replay・rep結果のパス)→Closeout確認(rep30 Closeout §63)→Status(CLOSEOUT_CONFIRMED/EVIDENCED/IMPLEMENTED/FABLE_DECIDED/OPEN/記録なし)。
3. 台帳末尾に「照合メモ(委任_08)」: 記録なし件数、OPENのまま残る件数と内容(特にSafety hole系)、Fableへ判断を求める項目。
4. commit/push(明示add: 台帳、委任ログ+check.json)。メッセージ: `OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: Opus指摘台帳の採否未確認15件を設計書・DECISION_LOGと照合し更新【記録なしn件・OPEN m件】(委任_08、¥0)`

## 事前指定Read一覧 / 事前指定Grep一覧+追記位置・更新位置の手順
上記参照先のとおり。台帳はOF-003〜018の行と末尾のみ編集。

## 実行コマンド全文
T-0 check: .venv python docs/pm/tools/check_delegation_prompt.py --file <本ファイル> --json-out <本ファイル>_check.json
Git: git status --porcelain→明示add(台帳・委任ログ・check.json)→commit→git push origin main→git log --oneline -1。

## 報告(handback、短く)
(1)15件のStatus分布、(2)OPENまたは記録なしの項目一覧(ID・Opus#・要旨20字)、(3)T-0・commit・push・raw URL、一覧外Read、確認/推測。

## SSOT追記先
`docs/pm/OPUS_FINDINGS_LEDGER.md`のみ(OF-003〜018の行と末尾の照合メモ)。他SSOTは編集しない。
