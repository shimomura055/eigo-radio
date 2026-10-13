# EVIDENCE_01 Regressionと既存runtime記録の引用(FAMILY-Z-KP-STRATEGY-L-DECISION-CLOSEOUT-01)

**本委任でruntime evidenceは新規取得していない。以下のStrategy L稼働実績は既存記録の引用(reuse)。新規run・有料APIなし(JPY0)。**

## Regression(`run_project_regression.py`、全PASS、ログは同ディレクトリ)
| pattern | 結果 | ログ |
|---|---|---|
| er062*_test*.py | 64/64 PASS | regression_er062.txt |
| er063*_test*.py | 59/59 PASS | regression_er063.txt |
| er026_family_z_fiction*_test*.py | 21/21 PASS | regression_er026_family_z_fiction.txt |
| er030*_test*.py | 108/108 PASS | regression_er030.txt |
(stop_sentinel test等の共有ファイル追記testは実行していない)

## Strategy L稼働実績(引用)
- `er026_output/family_z_production_e2e_01/melos/run_e2e_02/key_phrases/a2_result.json`(更新2026-10-12 17:46)と`b1b_result.json`(同17:38)の`"kp_backend_used": "strategy_l"`(各L230)。
- `run_e2e_02/e2e_stage_log.jsonl`: `{"stage":"kp","mode":"real",...,"spent_jpy_cumulative":22.325}`。
- `run_e2e_02/key_phrases/a2/outer_retry_log.json` scope=「Z限定・暫定(OPEN-310回避策)」=外側retry稼働。
- 注: `er030_output/kp_backend_telemetry_01/telemetry.jsonl`のMelos行(`KP_SRC_REF_CONTRACT_EVIDENCE_01_MELOS_*`)は`family_x`プロファイルのContract evidence(Trial/検証)でありZ正式経路ではない。Z正式経路の証跡は上記run_e2e_02。

## Status
Strategy Lの既存稼働実績と、コード上のStrategy L固定・DB Hybrid分岐なし・Regression PASSにより「Z KP=Strategy L維持」は実態と一致。ただしZ全体の`PRODUCTION_WIRED`ではない(Z E2Eは別管理IDでSTOP継続)。
