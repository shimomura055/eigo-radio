# FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_02b (要約保存)

## 管理ID
FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_02b: 生成・照合・盲検評価・集計)

## 性質/到達上限Status/禁止事項
- 性質: Trial(6-luna x Fact Lock vs 6-luna x 現行 vs 5.6 x 現行)。到達上限Status: MEASURED。VALIDATED/APPROVED_FOR_PRODUCTION宣言禁止。しきい値なし。
- 開始条件: all6 MANIFEST.json 48 run全exit記録 または RESULT.md存在。5分polling最大180分、未達ならAPI実行せず待機タイムアウト記録。
- 隔離: 書込は er052_output/factlock_writer_trial_01/ 、docs/pm/RESULT_PACKET_FACTLOCK.md、本委任ログのみ。git add/commit/push禁止。SSOT・RESULT_PACKET.md・ACTIVE_TASK.md編集禁止。
- 費用上限 JPY150 Guardrail(暴走疑い時のみSTOP)。
- STOP条件: smokeでタグ残存未解消/記号Gate波ダッシュ2連続/R0タグ無し。再実行1枠1回、全体6回まで。
- Opus Gate: 条件A実施済み。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2(TTS禁止)/T-3(Cap=Guardrail)

## ユーザー指示
「CでOK。それ以外も貴殿提案ベースでよいので進めてください。」/名称内番号「Aで良いです」(2026-10-08)

## KPI provenance
Fact Lockセル: fresh。brief: reuse。比較セル: reuse。

## 事前指定Read/Grep、実行コマンド、SSOT追記文、Git、報告
(原委任文の手順0〜7、RESULT_PACKET_FACTLOCK.md報告項目1〜10に従う。git操作禁止。)
