## 母集団(各armが実行済みのケース)
- E1L: 6ケース / 提示33件
- N2: 6ケース / 提示30件
- N4: 6ケース / 提示30件
- N5: 6ケース / 提示30件

## 指標(分母は各arm自身の提示件数。0件でも『誤り率0』とは書かず95%上限を併記)
| arm | 提示n | 意味・用法NG(確定) | 境界例 | 軽微(訳の不対応) | 自由組合せ混入 | 自然さ等(N軸) | そのまま選べる率(確定NG・境界・軽微を除く) | 一般化適用 | 一般化成功率 | 戻し数(率) | 3件以上ケース |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1L | 33 | 0/33 (0%, 95%上限8.7%) | 0 | 0 | 0/33 (0%, 95%上限8.7%) | 1 | 32/33 (97%, 95%上限99.8%) | 19 | 18/19 (95%, 95%上限99.7%) | 0/33 (0%, 95%上限8.7%) | 6/6 |
| N2 | 30 | 0/30 (0%, 95%上限9.5%) | 1 | 0 | 0/30 (0%, 95%上限9.5%) | 0 | 29/30 (97%, 95%上限99.8%) | 14 | 13/14 (93%, 95%上限99.6%) | 0/30 (0%, 95%上限9.5%) | 6/6 |
| N4 | 30 | 0/30 (0%, 95%上限9.5%) | 1 | 0 | 0/30 (0%, 95%上限9.5%) | 0 | 29/30 (97%, 95%上限99.8%) | 14 | 13/14 (93%, 95%上限99.6%) | 0/30 (0%, 95%上限9.5%) | 6/6 |
| N5 | 30 | 0/30 (0%, 95%上限9.5%) | 1 | 0 | 0/30 (0%, 95%上限9.5%) | 0 | 29/30 (97%, 95%上限99.8%) | 14 | 13/14 (93%, 95%上限99.6%) | 0/30 (0%, 95%上限9.5%) | 6/6 |

## 意味・用法NG(確定)の内訳
- E1L: なし
- N2: なし / 境界: melos_b1b:instead of ordering something[GLOSS_MISMATCH]
- N4: なし / 境界: melos_b1b:instead of ordering something[GLOSS_MISMATCH]
- N5: なし / 境界: melos_b1b:instead of ordering something[GLOSS_MISMATCH]

## 良質候補の維持(基準=E1Lで○だった候補)
- N2: 脱落 7/32 (22%, 95%上限37.2%) ['keep someone busy', 'be to blame', 'on the other hand', 'too soon to say', 'move away', 'stop thinking about', 'speak in favor'] / 一般化維持 13/14 (93%, 95%上限99.6%) 失った一般化 [('tesla_a2', 'brake lights come on', 'come on', 'the brake lights come on')]
- N4: 脱落 7/32 (22%, 95%上限37.2%) ['keep someone busy', 'be to blame', 'on the other hand', 'too soon to say', 'move away', 'stop thinking about', 'speak in favor'] / 一般化維持 13/14 (93%, 95%上限99.6%) 失った一般化 [('tesla_a2', 'brake lights come on', 'come on', 'the brake lights come on')]
- N5: 脱落 7/32 (22%, 95%上限37.2%) ['keep someone busy', 'be to blame', 'on the other hand', 'too soon to say', 'move away', 'stop thinking about', 'speak in favor'] / 一般化維持 13/14 (93%, 95%上限99.6%) 失った一般化 [('tesla_a2', 'brake lights come on', 'come on', 'the brake lights come on')]

## 費用(円/レベル。台帳のcache原価を含む『全課金した場合』の見積。1記事セット=2レベル)
- E1L: 平均¥1.00/レベル → 約¥2.01/記事セット(70円比 2.9%) (6レベル)
- N2: 平均¥1.27/レベル → 約¥2.54/記事セット(70円比 3.6%) (6レベル)
- N4: 平均¥2.72/レベル → 約¥5.45/記事セット(70円比 7.8%) (6レベル)
- N5: 平均¥2.72/レベル → 約¥5.45/記事セット(70円比 7.8%) (6レベル)
