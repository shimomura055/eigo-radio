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
