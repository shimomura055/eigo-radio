# BUDGET_LOG_01 (FZ-TELL-TALE-HEART-RESELECT-REMAKE-01)
| 時刻(JST) | 事象 | stop_scope_check | 実費(円) / run累計 |
|---|---|---|---|
| 2026-10-27 着手 | 作業開始 | `stop_check_00.json` rc=0 stop=false | 0 |
| 20:07 | kp stage 起動#1: system pythonに`google.genai`無しでimport前に失敗(rc=2、API呼出0・原因既知=.venv未使用)。 | `stop_check_kp.json` rc=0 | 0 |
| 20:07-20:15 | kp stage 起動#2(`.venv`、`--approved-budget-jpy 30`): 両level Part2候補抽出+Top1/2事前生成(候補0件)+KP候補生成→rc=4 `KP_REVIEW_PENDING`(正常停止) | 同上 | **4.08** (cost_log、openai 4.08) |
| 20:2x | フォーム登録・commit/push・公開URL確認 | - | 0(API 0) |
累計: **4.08円 / Cap 150円(残145.92円)**。日次(JST 2026-10-27): 他案件分約111円(ACTIVE_TASK記載)+本案件4.08円=約115円/1,000円。起動は同一run 5分内2回(RESTART_STORM閾値3回未満、うち1回はAPI前の失敗)。
