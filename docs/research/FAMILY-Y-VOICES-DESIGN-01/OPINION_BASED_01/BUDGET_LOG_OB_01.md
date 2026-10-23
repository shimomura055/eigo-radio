# BUDGET_LOG_OB_01 (委任_18 Phase 2 予算台帳。OF-Y6-08)

- Phase 2累計(新規API呼出)が **27円に達したら新規呼出を止める**(runnerの`Run.guard`が各call直前に累計を実測して強制)。Family Y残額は委任_18開始時点で約30.4円。
- 10-24日次累計(委任_17までの記録): 239.87円 / 1,000円。本Phase 2の実費を加算した値は末尾に記載。
- 使用モデル: 生成=gpt-6.1-sol(最新世代最上位系)、付番・構造タグ・Leakage判定=gpt-6-luna(理由=低コストで足りる機械照合/判定のみ)。
- 記録方法: runner`er110_family_y_opinion_based_01.py`が各段階の直後に、raw_usage_log由来のstage別費用差分を下表へ自動追記する(手書きではない)。

| 段階 | stage(call) | 増分(円) | run累計(円) |
|---|---|---|---|
| gen | ypl_ob_voice_1 | 4.0 | 10.923 |
| gen | ypl_ob_voice_2 | 4.03 | 10.923 |
| gen | ypl_ob_voice_3 | 2.893 | 10.923 |
| map1 | ypl_ob_map_voice_1_m1 | 0.2 | 11.432 |
| map1 | ypl_ob_map_voice_2_m1 | 0.155 | 11.432 |
| map1 | ypl_ob_map_voice_3_m1 | 0.154 | 11.432 |
| unmapped_regen | ypl_ob_voice_1_unmapregen | 4.311 | 19.074 |
| unmapped_regen | ypl_ob_voice_3_unmapregen | 3.331 | 19.074 |
| map2 | ypl_ob_map_voice_1_m2 | 0.201 | 19.436 |
| map2 | ypl_ob_map_voice_3_m2 | 0.161 | 19.436 |
| structure1 | ypl_ob_structure1 | 0.094 | 19.53 |
| gate | ypl_ob_voices_gate_leak1 | 0.196 | 19.726 |
| final_map | ypl_ob_map_voice_1_final | 0.201 | 20.197 |
| final_map | ypl_ob_map_voice_2_final | 0.128 | 20.197 |
| final_map | ypl_ob_map_voice_3_final | 0.142 | 20.197 |

## 集計(runner終了時点。実測)
- Phase 2 新規API費用: **20.197円**(上限27円の74.8%。27円到達なし・停止なし)。内訳: Voice生成(初回3本)10.923円 / UNMAPPED再生成(One Voice・A Third Voice各1回)7.642円 / 出典付番(luna、初回・再生成後・最終の計8call)約1.3円 / 構造タグ0.094円 / Leakage Gate判定0.196円(PASS、書換なし)。構造再生成0回・Tension Gate省略・有料run起動1回(再起動0)。
- 10-24 JST 日次累計: 239.87円(委任_17まで)+ 20.197円 = **約260.07円 / 1,000円**(同日の他agent分は別。本台帳はFamily Y委任_18分のみ)。
- Family Y残額: 約30.4円 − 20.197円 = **約10.2円**(追加のTrial・再現runにはユーザー判断が要る額)。
- 使用モデル: 生成=gpt-6.1-sol(最新世代の最上位系=最新)/ 付番・構造タグ・Leakage判定=gpt-6-luna(最新世代の低コスト系。理由=機械照合用の付番と判定のみで足りる)。
