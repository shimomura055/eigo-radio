## 母集団(各armが実行済みのケース)
- PROD: 6ケース / 提示34件
- D: 6ケース / 提示32件
- E1L: 6ケース / 提示34件
- E4: 6ケース / 提示27件
- N1a: 6ケース / 提示33件
- N1: 6ケース / 提示33件
- N2: 6ケース / 提示34件
- N4: 6ケース / 提示34件
- N4d: 6ケース / 提示34件
- N5: 6ケース / 提示34件
- N5d: 6ケース / 提示34件

## 指標(分母は各arm自身の提示件数。0件でも『誤り率0』とは書かず95%上限を併記)
| arm | 提示n | 意味・用法NG(確定) | 境界例 | 軽微(訳の不対応) | 自由組合せ混入 | 自然さ等(N軸) | そのまま選べる率(確定NG・境界・軽微を除く) | 一般化適用 | 一般化成功率 | 戻し数(率) | 3件以上ケース |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PROD | 34 | 0/34 (0%, 95%上限8.4%) | 1 | 0 | 11/34 (32%, 95%上限47.8%) | 13 | 9/34 (26%, 95%上限41.6%) | 6 | 4/6 (67%, 95%上限93.7%) | 0/34 (0%, 95%上限8.4%) | 1/6 |
| D | 32 | 1/32 (3%, 95%上限14.0%) | 1 | 0 | 5/32 (16%, 95%上限30.1%) | 1 | 24/32 (75%, 95%上限86.9%) | 20 | 17/20 (85%, 95%上限95.8%) | 0/32 (0%, 95%上限8.9%) | 5/6 |
| E1L | 34 | 3/34 (9%, 95%上限21.3%) | 0 | 1 | 1/34 (3%, 95%上限13.2%) | 0 | 29/34 (85%, 95%上限94.0%) | 23 | 20/23 (87%, 95%上限96.3%) | 0/34 (0%, 95%上限8.4%) | 6/6 |
| E4 | 27 | 2/27 (7%, 95%上限21.5%) | 2 | 0 | 0/27 (0%, 95%上限10.5%) | 0 | 23/27 (85%, 95%上限94.8%) | 18 | 14/18 (78%, 95%上限92.0%) | 0/27 (0%, 95%上限10.5%) | 6/6 |
| N1a | 33 | 1/33 (3%, 95%上限13.6%) | 3 | 1 | 1/33 (3%, 95%上限13.6%) | 0 | 27/33 (82%, 95%上限91.8%) | 21 | 17/21 (81%, 95%上限93.2%) | 0/33 (0%, 95%上限8.7%) | 6/6 |
| N1 | 33 | 0/33 (0%, 95%上限8.7%) | 4 | 0 | 1/33 (3%, 95%上限13.6%) | 0 | 28/33 (85%, 95%上限93.8%) | 20 | 16/20 (80%, 95%上限92.9%) | 1/33 (3%, 95%上限13.6%) | 6/6 |
| N2 | 34 | 0/34 (0%, 95%上限8.4%) | 4 | 0 | 1/34 (3%, 95%上限13.2%) | 0 | 29/34 (85%, 95%上限94.0%) | 23 | 20/23 (87%, 95%上限96.3%) | 1/34 (3%, 95%上限13.2%) | 6/6 |
| N4 | 34 | 0/34 (0%, 95%上限8.4%) | 4 | 0 | 1/34 (3%, 95%上限13.2%) | 0 | 29/34 (85%, 95%上限94.0%) | 23 | 20/23 (87%, 95%上限96.3%) | 1/34 (3%, 95%上限13.2%) | 6/6 |
| N4d | 34 | 0/34 (0%, 95%上限8.4%) | 4 | 0 | 1/34 (3%, 95%上限13.2%) | 0 | 29/34 (85%, 95%上限94.0%) | 23 | 20/23 (87%, 95%上限96.3%) | 1/34 (3%, 95%上限13.2%) | 6/6 |
| N5 | 34 | 0/34 (0%, 95%上限8.4%) | 4 | 0 | 1/34 (3%, 95%上限13.2%) | 0 | 29/34 (85%, 95%上限94.0%) | 23 | 20/23 (87%, 95%上限96.3%) | 1/34 (3%, 95%上限13.2%) | 6/6 |
| N5d | 34 | 0/34 (0%, 95%上限8.4%) | 2 | 0 | 1/34 (3%, 95%上限13.2%) | 0 | 31/34 (91%, 95%上限97.6%) | 21 | 20/21 (95%, 95%上限99.8%) | 3/34 (9%, 95%上限21.3%) | 6/6 |

## 意味・用法NG(確定)の内訳
- PROD: なし / 境界: meta_w_b1b:make room for[GLOSS_SENSE]
- D: untidi_a2:hear something out[ARG_TYPE] / 境界: untidi_b1b:hear someone out[ARG_TYPE]
- E1L: untidi_a2:hear something out[ARG_TYPE]; untidi_a2:take away from[SENSE_SHIFT]; untidi_b1b:hear something out[ARG_TYPE]
- E4: untidi_a2:hear something out[ARG_TYPE]; untidi_b1b:hear something out[ARG_TYPE] / 境界: untidi_a2:take something away from[SENSE_SHIFT]; untidi_a2:take up[FRAME_SHIFT]
- N1a: untidi_a2:hear something out[ARG_TYPE] / 境界: untidi_a2:take something away from[SENSE_SHIFT]; jwst_m_b1b:pick up[FRAME_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]
- N1: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_a2:take something away from[SENSE_SHIFT]; jwst_m_b1b:pick up[FRAME_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]
- N2: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_a2:take something away from[SENSE_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]; untidi_b1b:take points away[GLOSS_SENSE]
- N4: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_a2:take something away from[SENSE_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]; untidi_b1b:take points away[GLOSS_SENSE]
- N4d: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_a2:take something away from[SENSE_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]; untidi_b1b:take points away[GLOSS_SENSE]
- N5: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_a2:take something away from[SENSE_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]; untidi_b1b:take points away[GLOSS_SENSE]
- N5d: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_b1b:take points away[GLOSS_SENSE]

## 良質候補の維持(基準=E1Lで○だった候補)
- D: 脱落 12/29 (41%, 95%上限58.3%) ['make something work', 'turn something into', 'sales pitch', 'open for business', 'show up', 'rely on', 'show up', 'pick up', 'turn into', 'take something away'] / 一般化維持 11/11 (100%, 95%上限100.0%) 失った一般化 []
- E4: 脱落 9/29 (31%, 95%上限47.9%) ['make something work', 'put the brakes on', 'or so it seems', 'take a turn', 'set a limit', 'take a turn', 'show up', 'on the scale of', 'take something seriously'] / 一般化維持 12/12 (100%, 95%上限100.0%) 失った一般化 []
- N1a: 脱落 1/29 (3%, 95%上限15.3%) ['show up'] / 一般化維持 18/19 (95%, 95%上限99.7%) 失った一般化 [('ai_cha_b1b', 'or so it seemed', 'or so it seems', 'or so it seemed')]
- N1: 脱落 1/29 (3%, 95%上限15.3%) ['show up'] / 一般化維持 17/19 (89%, 95%上限98.1%) 失った一般化 [('jwst_m_b1b', 'set a lower limit', 'set a limit', 'set a lower limit'), ('untidi_b1b', 'taking points away', 'take something away', 'take points away')]
- N2: 脱落 0/29 (0%, 95%上限9.8%) [] / 一般化維持 19/20 (95%, 95%上限99.7%) 失った一般化 [('untidi_b1b', 'taking points away', 'take something away', 'take points away')]
- N4: 脱落 0/29 (0%, 95%上限9.8%) [] / 一般化維持 19/20 (95%, 95%上限99.7%) 失った一般化 [('untidi_b1b', 'taking points away', 'take something away', 'take points away')]
- N4d: 脱落 0/29 (0%, 95%上限9.8%) [] / 一般化維持 19/20 (95%, 95%上限99.7%) 失った一般化 [('untidi_b1b', 'taking points away', 'take something away', 'take points away')]
- N5: 脱落 0/29 (0%, 95%上限9.8%) [] / 一般化維持 19/20 (95%, 95%上限99.7%) 失った一般化 [('untidi_b1b', 'taking points away', 'take something away', 'take points away')]
- N5d: 脱落 0/29 (0%, 95%上限9.8%) [] / 一般化維持 19/20 (95%, 95%上限99.7%) 失った一般化 [('untidi_b1b', 'taking points away', 'take something away', 'take points away')]

## 費用(円/レベル。台帳のcache原価を含む『全課金した場合』の見積。1記事セット=2レベル)
- D: 平均¥1.04/レベル → 約¥2.08/記事セット(70円比 3.0%) (6レベル)
- E1L: 平均¥1.08/レベル → 約¥2.16/記事セット(70円比 3.1%) (6レベル)
- E4: 平均¥3.14/レベル → 約¥6.28/記事セット(70円比 9.0%) (6レベル)
- N1a: 平均¥1.09/レベル → 約¥2.18/記事セット(70円比 3.1%) (6レベル)
- N1: 平均¥1.31/レベル → 約¥2.62/記事セット(70円比 3.7%) (6レベル)
- N2: 平均¥1.47/レベル → 約¥2.94/記事セット(70円比 4.2%) (6レベル)
- N4: 平均¥2.18/レベル → 約¥4.35/記事セット(70円比 6.2%) (6レベル)
- N4d: 平均¥1.77/レベル → 約¥3.54/記事セット(70円比 5.1%) (6レベル)
- N5: 平均¥3.18/レベル → 約¥6.36/記事セット(70円比 9.1%) (6レベル)
- N5d: 平均¥2.06/レベル → 約¥4.12/記事セット(70円比 5.9%) (6レベル)
