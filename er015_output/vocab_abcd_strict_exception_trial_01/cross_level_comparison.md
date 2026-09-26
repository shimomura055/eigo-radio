# cross_level_comparison.md

目的: 同一(または実質同一)本文のStandard版/Advanced版で、同じ語に閾値差以外の判定差が出ていないかを確認する(B/C/D定義文言は両Levelで完全同一のため、判定差があれば閾値をまたいだ結果、またはモデルの非決定性のいずれかを疑うべき)。


## Meta

| word | Standard rank(候補入力時) | Standard判定 | Advanced rank(候補入力時) | Advanced判定 | 対照所見 |
|---|---|---|---|---|---|
| backstage | 12,912 | KEEP-A | - | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| concierges | > 20,000 (zipf=1.70, extremely rare) | KEEP-C | > 20,000 (zipf=1.70, extremely rare) | KEEP-C | 同一判定 |
| curtain | 8,776 | KEEP-B | 8,776 | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| leak | 6,160 | KEEP-B | - | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| onstage | 15,670 | KEEP-A | 15,670 | KEEP-A | 同一判定 |
| pause | 7,166 | SIMPLIFY | 7,166 | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| paused | 7,166 | SIMPLIFY | - | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| performer | 9,646 | KEEP-A | 9,646 | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| reuters | 8,719 | KEEP-C | 8,719 | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| understandable | 10,629 | KEEP-A | 10,629 | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |

## Sewer

| word | Standard rank(候補入力時) | Standard判定 | Advanced rank(候補入力時) | Advanced判定 | 対照所見 |
|---|---|---|---|---|---|
| artery | 12,006 | SIMPLIFY | 12,006 | SIMPLIFY | 同一判定 |
| faraway | > 20,000 (zipf=2.99, extremely rare) | KEEP-A | - | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| flush | 9,610 | SIMPLIFY | 9,610 | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| invisible | 6,153 | SIMPLIFY | 6,153 | (not an Advanced candidate) | 片方のLevelのみ候補(閾値差により候補セット自体が異なる可能性) |
| septic | > 20,000 (zipf=3.21, extremely rare) | SIMPLIFY | > 20,000 (zipf=3.21, extremely rare) | SIMPLIFY | 同一判定 |
| sewer | 12,324 | SIMPLIFY | 12,324 | SIMPLIFY | 同一判定 |
| sewers | 12,324 | SIMPLIFY | 12,324 | SIMPLIFY | 同一判定 |
| wastewater | 18,216 | KEEP-A | 18,216 | KEEP-A | 同一判定 |