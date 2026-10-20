# Phase結果(自動生成: er084_azure_phraselist_weight_trial_01_eval.py、raw全行を対象・除外なし)

raw行数: 15

## 条件別集計(audio x 条件)

| audio | 条件 | n | err | Melos正認識/期待 | 誤Melos(負例) | 異なり転写数 | 誤認識variant | 送信bias(wire) | dgi有 | name直後窓 |
|---|---|---|---|---|---|---|---|---|---|---|
| rec2_att2 | no_pl | 3 | 0 | 0/3 | 0 | 1 | {'mellows': 3} | [] | [False] | Mellows drank, got onto his knees  |
| rec2_att2 | pl_unspecified | 3 | 0 | 0/3 | 0 | 1 | {'mellows': 3} | ['1.000000'] | [True] | Mellows drank, got onto his knees  |
| rec2_att2 | pl_w1.0 | 3 | 0 | 0/3 | 0 | 1 | {'mellows': 3} | ['1.000000'] | [True] | Mellows drank, got onto his knees  |
| rec2_att2 | pl_w1.5 | 3 | 0 | 3/3 | 0 | 1 | {} | ['1.500000'] | [True] | Melos drank, got onto his knees an |
| rec2_att2 | pl_w2.0 | 3 | 0 | 3/3 | 0 | 1 | {} | ['2.000000'] | [True] | Melos drank, got unto his knees, a |

## 条件別率(正例=Melos正認識率、負例=誤Melos率)

| 条件 | 正例 正認識 | 正例率 | 負例 誤Melos | 負例率 |
|---|---|---|---|---|
| no_pl | 0/3 | 0.00 | 0/0 | - |
| pl_unspecified | 0/3 | 0.00 | 0/0 | - |
| pl_w1.0 | 0/3 | 0.00 | 0/0 | - |
| pl_w1.5 | 3/3 | 1.00 | 0/0 | - |
| pl_w2.0 | 3/3 | 1.00 | 0/0 | - |

## Production判定offline注入(Primary=既存OpenAI転写、Secondary=各条件のAzure転写。判定ロジック無変更)

| audio | 条件 | rep | 状態 | reason_code | verified | classification | HR要 |
|---|---|---|---|---|---|---|---|
| rec2_att2 | no_pl | 1 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | pl_unspecified | 1 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | pl_w1.0 | 1 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | pl_w1.5 | 1 | PASS_WITH_WARNING | secondary_confirmed | True | NORMALIZED_MATCH | False |
| rec2_att2 | pl_w2.0 | 1 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | no_pl | 2 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | pl_unspecified | 2 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | pl_w1.0 | 2 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | pl_w1.5 | 2 | PASS_WITH_WARNING | secondary_confirmed | True | NORMALIZED_MATCH | False |
| rec2_att2 | pl_w2.0 | 2 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | no_pl | 3 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | pl_unspecified | 3 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | pl_w1.0 | 3 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |
| rec2_att2 | pl_w1.5 | 3 | PASS_WITH_WARNING | secondary_confirmed | True | NORMALIZED_MATCH | False |
| rec2_att2 | pl_w2.0 | 3 | NG_BOTH | secondary_not_accepted | False | ASR_VALIDATION_UNCERTAIN | False |

## 転写全文(raw、除外なし)

- rec2_att2 / no_pl / r1: name窓=`Mellows drank, got onto his knees ` err=None
- rec2_att2 / pl_unspecified / r1: name窓=`Mellows drank, got onto his knees ` err=None
- rec2_att2 / pl_w1.0 / r1: name窓=`Mellows drank, got onto his knees ` err=None
- rec2_att2 / pl_w1.5 / r1: name窓=`Melos drank, got onto his knees an` err=None
- rec2_att2 / pl_w2.0 / r1: name窓=`Melos drank, got unto his knees, a` err=None
- rec2_att2 / no_pl / r2: name窓=`Mellows drank, got onto his knees ` err=None
- rec2_att2 / pl_unspecified / r2: name窓=`Mellows drank, got onto his knees ` err=None
- rec2_att2 / pl_w1.0 / r2: name窓=`Mellows drank, got onto his knees ` err=None
- rec2_att2 / pl_w1.5 / r2: name窓=`Melos drank, got onto his knees an` err=None
- rec2_att2 / pl_w2.0 / r2: name窓=`Melos drank, got unto his knees, a` err=None
- rec2_att2 / no_pl / r3: name窓=`Mellows drank, got onto his knees ` err=None
- rec2_att2 / pl_unspecified / r3: name窓=`Mellows drank, got onto his knees ` err=None
- rec2_att2 / pl_w1.0 / r3: name窓=`Mellows drank, got onto his knees ` err=None
- rec2_att2 / pl_w1.5 / r3: name窓=`Melos drank, got onto his knees an` err=None
- rec2_att2 / pl_w2.0 / r3: name窓=`Melos drank, got unto his knees, a` err=None

## v02 再注入(委任_02b、Opus_J M-1/M-2是正後のjudge。API 0。上記の旧v01結果は変更せず残置)

- 変更点: judgeへ本番相当の`segment_id`(`full_story_part3_c1`=FULL_STORY role)と`enable_connected_speech_equivalence_layer=connected_speech_enabled_for(segment_id)`を渡す(旧v01は`segment_id="plw_trial"`=role None、Tier3不発)。telemetry追記はno-op、`is_last_slot=False`固定。
- 比較軸2条件: **FULL_STORY role**(Tier3あり、本番の本文clip相当) / **Tier3なしrole**(`segment_id=None`相当、KP型。旧v01と同じ経路)。
- Primary転写=run_e2e_04 attempt2のProduction記録(`Mello drank`)。Azure転写=Phase A rawの各行。再注入結果json=`er084_output/azure_phraselist_weight_trial_01/phase_a_reinject_v02.json`(commit対象)。
- golden replay test(`er084_azure_phraselist_weight_trial_01_judge_test_02.py`): run_e2e_04 part3_c1 attempt2記録(Primary`Mello`/Azure`Mellows`)で記録どおり`primary_1,tier3_corroboration_secondary,secondary_1`の順で`NG_BOTH`、run_e2e_05 Std減速後(Primary`Mellos`/Azure`Melos`相当)で`SECONDARY_ASR_CORROBORATED_MATCH`/`PASS_WITH_WARNING`が再現(PASS)。

| 条件 | rep | 旧v01状態 | v02 FULL_STORY role | v02 Tier3なしrole |
|---|---|---|---|---|
| no_pl | 1 | NG_BOTH | NG_BOTH(ASR_VALIDATION_UNCERTAIN) | NG_BOTH |
| pl_unspecified | 1 | NG_BOTH | NG_BOTH(ASR_VALIDATION_UNCERTAIN) | NG_BOTH |
| pl_w1.0 | 1 | NG_BOTH | NG_BOTH(ASR_VALIDATION_UNCERTAIN) | NG_BOTH |
| pl_w1.5 | 1 | PASS_WITH_WARNING | PASS_WITH_WARNING(SECONDARY_ASR_CORROBORATED_MATCH) | PASS_WITH_WARNING |
| pl_w2.0 | 1 | NG_BOTH | PASS_WITH_WARNING(SECONDARY_ASR_CORROBORATED_MATCH) | NG_BOTH |
| no_pl | 2 | NG_BOTH | NG_BOTH(ASR_VALIDATION_UNCERTAIN) | NG_BOTH |
| pl_unspecified | 2 | NG_BOTH | NG_BOTH(ASR_VALIDATION_UNCERTAIN) | NG_BOTH |
| pl_w1.0 | 2 | NG_BOTH | NG_BOTH(ASR_VALIDATION_UNCERTAIN) | NG_BOTH |
| pl_w1.5 | 2 | PASS_WITH_WARNING | PASS_WITH_WARNING(SECONDARY_ASR_CORROBORATED_MATCH) | PASS_WITH_WARNING |
| pl_w2.0 | 2 | NG_BOTH | PASS_WITH_WARNING(SECONDARY_ASR_CORROBORATED_MATCH) | NG_BOTH |
| no_pl | 3 | NG_BOTH | NG_BOTH(ASR_VALIDATION_UNCERTAIN) | NG_BOTH |
| pl_unspecified | 3 | NG_BOTH | NG_BOTH(ASR_VALIDATION_UNCERTAIN) | NG_BOTH |
| pl_w1.0 | 3 | NG_BOTH | NG_BOTH(ASR_VALIDATION_UNCERTAIN) | NG_BOTH |
| pl_w1.5 | 3 | PASS_WITH_WARNING | PASS_WITH_WARNING(SECONDARY_ASR_CORROBORATED_MATCH) | PASS_WITH_WARNING |
| pl_w2.0 | 3 | NG_BOTH | PASS_WITH_WARNING(SECONDARY_ASR_CORROBORATED_MATCH) | NG_BOTH |

**新旧の差(w2.0)**: 旧v01では`pl_w2.0`は3/3 NG_BOTH(`unto`揺れ)だったが、v02 FULL_STORY roleでは3/3 PASS_WITH_WARNING(`SECONDARY_ASR_CORROBORATED_MATCH`、Tier3がdiff位置1語の`Melos`だけを見るため`onto→unto`の揺れは判定に効かない)。Tier3なしroleでは旧結果どおりNG_BOTH。したがって**w2.0の評価はrole条件(Tier3の有無)で逆転する**。w1.5は両roleでPASS系(FULL_STORYはTier3、Tier3なしはSecondary確認)、w1.0/unspecified/no_plは両roleでNG_BOTH(変化なし)。Opus_J M-1の予測(推測)が実機再注入で確認された。
- 本番の判定flip(NG→PASS系)数、録音2(Phase A基準wav): FULL_STORY role: w1.5=3/3, w2.0=3/3 / Tier3なしrole: w1.5=3/3, w2.0=0/3。録音2は選択バイアスがあるため確認集計から除外し参考値とする(設計書v02 §3)。

M1凍結の注記(Opus_J補足): judge内のM1凍結は**現在のPronunciation Ledgerを読むread-only経路**(`er006_secondary_asr_01.py:233-237`)で、本番run時点のsnapshotとは異なる。「今後の本番挙動を見る」目的では現在のLedgerで妥当。
