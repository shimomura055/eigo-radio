# 委任_12 FACTLOCK-ASTRA-E2E-TRIAL-01(2026-10-09) G2 round1 委任文(要約)
- 範囲: 旧4テーマ[meta/hormuz/space_weapons/small_bag]を両腕・2レベルで実API実行(1テーマ1プロセス4並列、worker 1-4、--arms new,old、--until なし=最終段まで)。cap: --cap-jpy 820 --alert-jpy 650(Stage R ¥178.99は台帳外)。本委任の目安 raw ¥200前後。
- 前処理: G1軽微欠陥2件の最小修正(theme_summary/run_summaryの上書き、m3_protected.jsonl空ファイル)+テスト、空き物理メモリ確認。
- Fable判断: runner欠陥(例外・経路不通・provenance違反)なら全worker即停止。品質起因STOPは停止理由にしない。meta旧腕JA STOPは再実行しない。round2起動禁止。
- 成果物: runs/ROUND1_MIDCHECK.md、g2_round1_logs/、round1_aggregate/、_12_result.md、RESULT_PACKET。
- 禁止: round2、TTS、Prompt変更、品質STOP再実行(cherry-picking)、Production/SSOT本体編集。
