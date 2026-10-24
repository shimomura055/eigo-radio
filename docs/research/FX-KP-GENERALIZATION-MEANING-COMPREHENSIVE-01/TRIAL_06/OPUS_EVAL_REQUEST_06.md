# OPUS_EVAL_REQUEST_06: 補強Trial_06 新規出力の独立評価依頼(委任_31)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 評価対象=`TRIAL_06/blind_06b.md`(51行・100文字列)。arm・既存ラベルは伏せてある。

## 依頼
1. `TRIAL_06/blind_06b.md` の各セルにPASS/THIN/FAIL/FAIL_LITを付け、JSON `{"<行>:<列>": "LABEL"}` で返す(例 `"3:B":"THIN"`)。THINには理由1語(持ち込み:否定/主語/時制/対象/場面、狭い、説明的、字義)。
2. 判定基準は `TRIAL_05/fable_blind_06.md` の「判定基準」節(範囲を超えた持ち込み=THIN、迷えば厳しい側)。**ラベル付け前に key JSON を開かない**。
3. 再照合対象を明示: `add up`(否定の持ち込み疑い)、`reach for someone's wallet`(過去ユーザー判断『見出し語忠実でPASS』との整合を理由付きで)。
4. 過剰解釈の確認: 字義が正解のKP(`sheltered from the rain`/`smile through one's tears`/`keep one's eyes on them`等)で、解釈訳へ書き換えた文字列があれば理由に書く。
5. 評価はarmを推測せず文字列のみで行う。

## 集計(Fable側)
`py er112_kp_gm_trial_06_blind2.py agree --labels2 <opus.json> --labels1 <fable.json>`(labels1省略時は継承ラベルのみ)。
