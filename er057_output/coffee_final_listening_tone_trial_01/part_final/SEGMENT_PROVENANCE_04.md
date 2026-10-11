# SEGMENT_PROVENANCE_04(委任_04、Advanced分の差分)
Advanced完成版を再組立(委任_03 assemblerを無改変で再利用、`adv_overrides`のextraへK2 5件を追加)。長さ: 288.45秒 → 288.45秒(KP部の合計が偶然一致、各KP block長は±0.2秒内で変動)、peak 0.95941 → 0.95941。
変更role(5件): kp1_en〜kp5_en のみ(由来=委任_04 K2新規生成、Trial)。他24 roleのsha256は委任_03と完全一致(`adv_provenance_diff_04.json`)。

| role | 委任_03 sha先頭12(既存承認音声) | 委任_04 sha先頭12(K2) |
|---|---|---|
| kp1_en `lag` | adb32702fd9c | 20b8b303e860 |
| kp2_en `price tag` | 3a3add6db793 | a2f5660de5bb |
| kp3_en `show up` | 1a72df7d1100 | 197f7afff745 |
| kp4_en `come down` | 2f92321ba8b0 | e7a616366bbf |
| kp5_en `come with` | 0de94a5104fa | 58602a650987 |

Standard完成版: 委任_03のまま(音声・manifest不変。再生成・再組立なし)。繰返しKP英語(初回/繰返し)は同一音声(assemblerが同一component配列を使用)。
