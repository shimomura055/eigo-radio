# BUDGET_POLICY_CHANGE_01(PM-FAMILY-Y-BUDGET-CONSOLIDATION-01 委任_01、2026-10-24)

ユーザー決定: Family Y固有の累計開発予算上限(600円/650円等)を撤廃、日次1,000円(JST・全体)で一元管理。原文=docs/pm/delegation_log/2026-10-24_PM-FAMILY-Y-BUDGET-CONSOLIDATION-01_USER.md。API 0・Production変更0。

## 実行制御・STOP判定の残存確認(Grep: er110_*.py / docs/research/FAMILY-Y-VOICES-DESIGN-01/** / docs/pm/ACTIVE_TASK.md / er110_output)

| 対象 | 内容 | 実行制御に効くか | 措置 |
|---|---|---|---|
| er110_*.py 全件 | `600`/`650`/`Y累計`/累計チェックして停止する処理をGrep | 該当0件(Y累計を参照するコード・定数なし) | 変更なし |
| er110_family_y_persona_pipeline_01_run.py:46 `TREE_CAP_JPY=245.0` | 委任_14+15のrun(tree)単位の歯止め(`:70-71` BUDGET_GUARD) | 効く(run単位)。Y累計ではない | 維持。「Y累計上限ではない」旨のコメントを追記(値・ロジック無変更) |
| er110_family_y_opinion_based_01.py:44 `BUDGET_STOP_JPY=27.0` | 委任_17/18のPhase 2 run単位 | 効く(run単位)。Y累計ではない | 維持 |
| er110_family_y_text_trial_01_run.py:35 `BUDGET=215.0` | 委任_04のrun dir単位保険 | 効く(run単位) | 維持 |
| er110_family_y_audio_trial_01.py:602 / persona_audio_trial_01.py:586 `--budget-jpy` | 音声段のraw_usage_log累計(候補単位) | 効く(候補単位) | 維持 |
| BUDGET_PLAN_PHASE_B_01 / TRIAL_03 BUDGET_PLAN_01〜03 | 「Y累計600円」記載(過去の計画書) | 文書のみ | 冒頭に「撤廃(2026-10-24)」注記追加 |
| REDESIGN_02 DESIGN_PROPOSAL_05 / FABLE_JUDGMENT_PHASE_B_01 / PHASE_B_RESULT_01・02 / TRIAL_03 RESULT_01〜02 / FABLE_EVAL_03 | 当時の実績記録(Y累計xxx/600円) | 歴史的記録 | 改変せず(撤廃はPM_GOVERNANCE 7-9・DECISION_LOGに記録) |
| docs/pm/ACTIVE_TASK.md 24行台のY行(委任_14/15) | 「[Y累計600円内]」 | 文書のみ(gitignored一時ファイル) | 「旧Y累計600円内=2026-10-24撤廃」へ置換。固定ヘッダに予算行を追加(Y累計は実績のみ) |
| OPEN_ITEMS OPEN-463 / USER_DECISION_REGISTER #176 | Y上限600→650/830/800円の記述 | 文書のみ | 撤廃・解消を追記(#176の旧題材再現検証等の選択肢は未回答維持) |

結論: 旧Y累計600/650円を参照して停止するコード・STOP条件は存在しなかった(実行制御はrun単位Capのみ)。今後のSTOP/報告は日次1,000円(`docs/pm/tools/daily_dev_cost_01.py`)基準。
