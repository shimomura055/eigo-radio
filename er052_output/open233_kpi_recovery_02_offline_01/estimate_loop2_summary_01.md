# ループ2 有料Trial見積(委任_11、`--stage estimate`のみ・¥0、推測を含む)

コマンド: `er052_open233_stage1_stageA_01.py --stage estimate --plan {stageA|g_arm} --r5-mode ... --r3-reasoning ... --r5-reasoning ... [--reuse-r3-from er052_output/open233_stage1_stageA_01] --estimate-out <本ディレクトリ>/estimate_loop2_*.json`(有料実行オプションなし)。
前提: reasoning=段階A実測平均(r3 3,465 / r5 7,674 token)xeffort倍率(high 1 / medium 0.5 / low 0.25、**未検証の仮定**)x帯(0.6 / 1.0 / 1.5)。入力=文字数x0.66token、r5-Vの推論は同effortの5-lite同等と仮定(保守側)。較正確認: g_arm(full/high/high)のmid ¥48.25/33 run=¥1.46/run、段階A実測平均¥1.52/runと整合。

| 試験 | run数 | 構成 | low | mid | high |
|---|---|---|---|---|---|
| r5-V on 保存r3(r3再実行なし) | 42 | r5-V medium | 15.73 | **20.79** | 27.10 |
| r5-V on 保存r3 | 42 | r5-V low | 11.94 | **14.46** | 17.62 |
| G arm基準(参考) | 33 | 5-lite high / r3 high | 36.72 | 48.25 | 62.67 |
| G arm | 33 | r3 medium+5-lite medium | 28.07 | 33.83 | 41.04 |
| G arm(別案1) | 33 | r3 medium+r5-V medium | 25.57 | **31.34** | 38.54 |
| G arm(別案1) | 33 | r3 medium+r5-V low | 22.59 | **26.37** | 31.10 |

注意: (1) 保存r3出力の再利用は、保存r3がhigh・旧否定検査での出力である点を引き継ぐ(r5-V単体の効果測定用、r3のeffort効果は測れない)。(2) G armのr5-V対象数は保存r3(同instance・同sample)のSUPPORTED+関係単位数で代理(fresh r3の結果とは異なりうる)。(3) 委任_12で全て実測に置き換える。予算上限・段階停止は委任_12で設定。
