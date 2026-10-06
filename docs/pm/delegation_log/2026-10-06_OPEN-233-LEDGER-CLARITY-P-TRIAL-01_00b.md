## 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01(委任_00b: Researcher/Verification実装調査とP'プロンプト・DEV限定経路の設計、Phase 0、¥0)

## 性質/到達上限Status/禁止事項
性質: 調査+設計案(read-only+設計ファイル1本)。到達上限: 設計案提示(実装はしない)。禁止: コード変更/prompt変更/有料API/Trial実行/Production変更/SSOT編集/git。「台帳生成処理(決定論部分)の変更が必要」と判明した場合は設計を進めず `STOP_RECOMMENDED` として報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1: 該当なし(¥0)。T-0: 本委任文を `docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00b.md` に逐語保存し `python docs/pm/tools/check_delegation_prompt.py --file <パス> --json-out <同名_check.json>`(FAILでも続行)。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
P'方式: 変更対象はWeb Researchそのものではなく、Researcherが調査結果をFactとして構造化・記述する部分。Research→Factとして構造化・記述(改善)→Verification→決定論によるFact Ledger生成→B3 brief→Writer→Checker。原則: 検索対象・Research方法を不用意に変えない/原資料にないFactを追加しない/主体・動作・対象・時系列・状態変化を明確にする/rollbackのような多義的表現を原資料が示す意味に基づき明確化/Verification側では明確化された意味が原資料と一致しているか確認/既存の決定論的な台帳生成処理は原則変更しない。もしP'実現のために台帳生成処理自体の仕様変更が必要と判明した場合は、勝手に変更せずSTOPして報告。有料API上限¥50(本委任は¥0)。

## 事前指定Read/Grep一覧、出力、実行コマンド、報告項目
(委任文の項目1〜8および報告(1)〜(8)に従う。出力: docs/pm/ledger_clarity_p_trial/00b_pprime_design.md、80行以内。)
- python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00b.md --json-out docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00b_check.json

## SSOT追記文/Git
なし/なし。
