# 現行Production英語Stage 1 実費集計(委任_11、¥0)

判定: **特定不能(Production 1記事分のStage 1実費として確定できない)**。推定で埋めない。

## 確定範囲(er003/er019のdeviation/vfl/ledger系stage)

| stage | n | 平均¥(own model) | 平均¥(gpt-6-luna単価換算) |
|---|---|---|---|
| advanced_deviation | 1 | 1.076 | 0.463 |
| deviation_check_after_a2 | 1 | 0.714 | 0.299 |
| deviation_check_after_b1b | 1 | 0.614 | 0.257 |
| ledger | 1 | 3.066 | 1.443 |

## 参考のみ(Production確定ではない: er012/er013)

| stage | n | 平均¥(own model) | 平均¥(gpt-6-luna換算) |
|---|---|---|---|
| deviation_check_a2_cycle0 | 5 | 0.504 | 0.231 |
| deviation_check_a2_cycle1 | 1 | 1.968 | 0.843 |
| deviation_check_b1_cycle0 | 6 | 0.545 | 0.248 |
| safety_layer1_deviation_check | 1 | 0.248 | 0.123 |

## 特定不能の理由
- er003_output配下にraw_usage_logなし
- er019の該当stageはfamily_x_section_segmentation_trial/b3 regression(Trial/回帰)で、n=1〜2、Production全記事run(hormuz等)のlogには英語deviation stageなし(ja_*のみ)
- Production英語生成+deviation checkのusageは別出力(er012/er013等)にstage名が異なって分散し、Production現行pathと一対一に対応づけられない

注記: stage名 ledger はLedger生成でありcheckではない(確定範囲の表から除外して読む)。deviation系はn=1〜6で、全て参考値。
