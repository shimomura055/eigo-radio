# 委任_07 FACTLOCK-ASTRA-E2E-TRIAL-01 Stage R残り(委任文要旨)
管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_07。日付2026-10-09。API支出上限¥80(B3x2約¥1.2、research 2テーマ各上限¥35)。委任_05のファイルには触らない。git index.lock衝突時は10秒待って最大5回再試行。
1. openai_copyright・inbound_tourismのB3を凍結台帳から生成(research非実行)。
2. streaming_price・semiconductor_earningsのresearch→台帳→B3。topic文を1社・1イベントに絞る(旧案も残す)。1テーマ¥35で停止、補欠入替なし。
3. 台帳スキーマ点検・FROZEN_INPUTS_SHA256.json(LF正規化)を10テーマ分に更新、COST_STAGE_R.md更新。
4. 仕様v2運用明確化を stage_r/SPEC_V2_CLARIFICATIONS.md に記録: (a)個別記録に date_or_period/numeric_value欄が無い場合、その記録に限り代替規則(statement内主数字・日付)を適用 (b)丸め(hormuz「約25時間後」vs台帳「約24時間48分後」)はunmapped_claimsの「新数値(丸め)」とし、STOP該当は注記統合時に機械判定。
禁止: Astra呼出・Writer段以降・注記、既存コード/Prompt/SSOT本体編集、¥80超過、未確認数値の確定値記載。
記録: 本ファイル、_07_result.md、REPORT_LEDGER 1行、DECISION_LOG末尾1節。commitは stage_r/・委任記録・DECISION_LOG・REPORT_LEDGERのみ明示add。
