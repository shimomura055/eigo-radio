# WRITER_GATE_STOP 件数サマリ(非盲検の副次指標、design_01.md 5-A6)

段階2 60 run(5条件 x 3テーマ x b1〜b4、Writer1本/brief)のうち、Writer内部Gate(Production既存の安全装置。緩和・無効化していない)でSTOPし記事生成不能だったrun。記事評価の母数(盲検コピー55記事)から除外。評価者には渡さない(条件が分かるため)。

| 条件 | 生成不能 | 期待run | 評価対象記事 |
|---|---|---|---|
| V0 | 0 | 12 | 12 |
| V1 | 0 | 12 | 12 |
| V3 | 1 | 12 | 11 |
| V5 | 4 | 12 | 8 |
| V6 | 0 | 12 | 12 |
| 計 | 5 | 60 | 55 |

| run | Gate種別 |
|---|---|
| hormuz V3 b1 | Advanced deviation MAJOR未解決 -> JA_RECHECK_REQUIRED(2回試行) |
| meta V5 b2 | Advanced deviation MAJOR(A5で試行) |
| meta V5 b3 | JA_FACT_CHECK_STOP(2回試行) |
| hormuz V5 b1 | JA_FACT_CHECK_STOP(LEDGER_DEVIATION MAJOR、2回試行) |
| meta V5 b4 | A5でphase1後にGate停止(Gate種別は記録上不明)。ユーザー/Fable指示により再試行対象外 |

Gate種別別: Advanced deviation/JA_RECHECK系 2(+meta V5 b4不明1)、JA_FACT_CHECK_STOP 2。テーマ別欠: meta 3(全てV5)、hormuz 2(V3 b1, V5 b1)、space_weapons 0。
出典: er052_output/open233_b3_trial_01/eval/STAGE2_RUN_CHECK.md(A5/A6/A6b節)、eval/inventory_after_A6b.json、runs/writer_gate_stop_final.json。解釈(V5でGate停止が多い)は評価・集計後にFableが行う。
