# BUDGET_LOG_01 (委任_07 Trial、出典=er112_output/kp_gm_trial_02/paid_calls.jsonl)
- 開始時: 当日累計(daily_dev_cost_01 adopted) 632.59円 / 当日上限1,400円。残767円。他案件予約(Family Y残334.25円+ASR②/B工程<=25円)を引いても約408円残り、本Trial上限70円(目標60円)は収まる。
- STOP確認: stop_check_07.json rc=0(非停止)。
- 段階別費用(出典=er112_output/kp_gm_trial_02/paid_calls.jsonl): Sol gloss 14call 18.24円 / luna gloss 60call 5.37円 / Adv説明生成413call 6.43円 / E2E(Production関数DEV注入)61call 1.89円 / Judge Sonnet 21バッチ 31.63円 / Judge Sol 4バッチ 5.40円 / 台帳repair 0.03円(他processとの書込み交錯で2断片を除去、results.jsonlのcall_cost_jpy合計との差0.025円を補正記録)。合計68.98円(上限70円、目標60円超過だが上限内)。
- 55円到達(Judge Sonnet完了時55.75円)での再計算: 残作業=Sol Judge約5.4円+P判定約2円+E2E約1.9円+E4追加0.6円=約10円 → 完成見込み約66〜69円(<70円)と判断し続行。70円超過見込みではないためFable報告の停止条件には非該当。実績68.98円。
- Sol 1call実測: 1.1338円(2048in/299out)。Sol合計18.24円(上限25円内)。
- 終了時の当日累計(daily_dev_cost_01 adopted): 710.32円/1,400円(本Trial 68.98円を含む)。他案件予約枠(Family Y残334.25円+ASR②/B工程≤25円)を差引いても収まる。
- 有料run終了: 2026-10-23 JST 19:33頃。再起動なし。外部STOP/異常終了なし(rc=0)。
