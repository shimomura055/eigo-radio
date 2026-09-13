# tool_uses_trial_log.md

管理ID: PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-TRIAL-DESIGN-01(施策1 Trial)。
Fableが各Trial arm委任の完了後に1行ずつ追記する記録ファイル(新規、テンプレのみ)。
Sonnetはこのファイルへ書き込まない(Fable専用の観測記録)。

## 記入ルール
- 1委任1行。列は`|`区切り(Markdown table)。
- 「見落とし・手戻り」列の定義(固定、変更しない):
  - `gate_reject`: Fableのgate-checkで差し戻しになった回数(0以上の整数)
  - `accept_criteria_miss`: 受入条件未達で発覚した件数
  - `fixup_commit`: 当該タスクのcommit後に必要になった修正commit件数
  - `scope_leak`: 対象外ファイル混入件数(意図しないファイルがcommitに混入)
  - `ssot_error`: SSOT記載誤り件数(DECISION_LOG/OPEN_ITEMS等への誤記載)
- `tool_uses`/`cumulative_usage`/`final_context_size`等は
  `docs/pm/tools/measure_delegation_task.py --task-id <taskId>`の出力値を転記する。
- pairing_before_taskはBefore母集団からペアリングした比較対象タスクの
  管理ID(規模が近いConsolidation系タスク)を記す。

## 記録テーブル

| No | taskId | 管理ID | pairing_before_task | tool_uses | cumulative_usage | final_context_size | tool_result_total_chars | same_file_reread_rate | full_read_rate_by_chars | duration_seconds | gate_reject | accept_criteria_miss | fixup_commit | scope_leak | ssot_error | 備考 |
|----|--------|--------|----------------------|-----------|-------------------|----------------------|---------------------------|--------------------------|----------------------------|--------------------|--------------|--------------------------|----------------|--------------|--------------|------|
| 1  | a9215801a1916cb64 | PM-CLOSEOUT-CONSOLIDATION-110 |                      | 51        | 2836320          | 88748               | 66552                    | 0.8512                  | 0.1706                    | 384.558           | 0            | 0                        | 0              | 0            | 0            | 施策1 Trial arm #1完了。Fable委任文設計不備2件(Grep指定不足/必須引数漏れ)、差し戻し0、修正commit0、混入0、SSOT誤り0 |
| 2  | a5cf1652284b4b7a4 | PM-CLOSEOUT-CONSOLIDATION-109 |                      | 28        | 1777291          | 89212               | 75859                    | 0.5664                  | 0.0192                    | 348.437           |              |                          |                |              |              | Trial前参考値(施策1導入前、read-only計測、¥0) |
| 3  | a70739bbeab141030 | PM-CLOSEOUT-CONSOLIDATION-111 |                      | 18        | 989618            | 75967               | 74741                    | 0.5655                  | 0.1221                    | 177.162            | 0            | 0                        | 0              | 0            | 0            | 施策1 Trial arm #2完了。差し戻し0、修正commit0、混入0、SSOT誤り0(arm#1の57/51不一致は計測定義差、112で訂正記録)、一覧外Read0 |
| 4  | a25dc971bdbbe4aff | PM-CLOSEOUT-CONSOLIDATION-112 |                      | 26        | 1198422          | 61044               | 47828                    | 0.3046                  | 0.7010(chars)/0.25(calls) | 328.756            | 0            | 0                        | 0              | 0            | 0            | 施策1 Trial arm #3完了。差し戻し0、修正commit0、混入0、SSOT誤り0、一覧外Read1(Fable委任文の引数実値省略が原因) |
| 5  | a74ed969499b27048 | PM-CLOSEOUT-CONSOLIDATION-113 |                      | 22        | 1444172           | 88482               | 97328                    | 0.6044                  | 0.1814(chars)/0.4(calls)  | 190.574            | 0            | 0                        | 0              | 0            | 0            | 施策1 Trial arm #4完了(前回計測未了分をCONSOLIDATION-114内で記入)。差し戻し0、修正commit0、混入0、SSOT誤り0、一覧外Read0 |
| 6  | a44bcff14a2a4d9a3 | PM-CLOSEOUT-CONSOLIDATION-114 |                      | 36        | 1795848           | 89986               | 90037                    | 0.5943                  | 0.2137(chars)/0.1429(calls) | 250.071            | 0            | 0                        | 0              | 0            | 0            | 施策1 Trial arm #5完了。差し戻し0、修正commit0、混入0、SSOT誤り0、一覧外操作1(Fable委任文の引数名誤り) |
| 7  | 次回記入 | PM-CLOSEOUT-CONSOLIDATION-115 |                      |           |                   |                      |                           |                          |                            |                    |              |                          |                |              |              | 施策1 Trial arm #6(本委任、計測は次回委任で記入) |

(以下、Trial実行のたびに行を追加する。N=6到達時点でPM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-TRIAL-DESIGN-01_REPORT.mdの判定基準に照らして評価する。N=3時点で中間判断を行う場合は同REPORTの中間判断基準を参照する。)
