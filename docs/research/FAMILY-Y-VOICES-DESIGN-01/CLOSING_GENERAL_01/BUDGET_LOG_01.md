# BUDGET_LOG_01 (委任_30 Step 2: 有料実行の費用記録。途中停止)

- 承認: 個別Cap 60円(Fable委任_30、7-7自律範囲)。`er110_output/family_y_closing_general_01/BUDGET_APPROVED.json`。テーマ別Cap=30円ずつ。起動前の日次累計(daily_dev_cost_01 adopted_jpy)=894.03円、STOP確認 rc=0(`stop_check_start.json`)。
- 実行: 2テーマ別process並列(`.venv`、gpt-6.1-sol、effort=high、判定=gpt-6-luna)。
| call | model | input tok | output tok(うちreasoning) | 経過秒 |
|---|---|---|---|---|
| redelivery_fee gen1 | gpt-6.1-sol | 3,982 | 11,370 (9,283) | 159.8 |
| redelivery_fee gen1 Leakage判定 | gpt-6-luna | 943 | 2,201 | 22.0 |
| sns_age_limit gen1 | gpt-6.1-sol | 3,739 | 11,560 | 155.6 |
| sns_age_limit gen1 Leakage判定 | gpt-6-luna | 944 | 1,065 | 11.7 |
- 実費(予約guardの集計値): redelivery_fee 19.657円、sns_age_limit 19.793円、**合計 約39.45円**(1生成+判定 ≈ 19.7円)。再生成は0回(両生成とも決定論検査1回目で合格)。
- **見積の乖離**: GEN_EST_JPY=12円(委任_29の見積。出力4.5〜7k tok想定)に対し、実際は出力約11.4k tok(reasoningが約9.3k)で1生成≈19.5円(約1.6倍)。
- **停止**: 各テーマのgen2直前で予約guardが `BUDGET_RESERVE_STOP`(spent 19.657/19.793 + est 12 > テーマCap 30)。API呼出なしで正常停止(想定どおりの安全装置)。**Cap 60円内で4生成は不可能**(4生成≈79円、3生成でも≈59円で再生成の余地なし)。
- 結果: 実行済みは各テーマ1生成(計2生成)。gen_2は未実行(Cap不足によるSTOP)。Capの引き上げ・生成数の変更はFable判断。
