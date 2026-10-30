## 母集団(各armが実行済みのケース)
- PROD: 14ケース / 提示66件
- D: 14ケース / 提示71件
- E1L: 14ケース / 提示81件
- E4: 14ケース / 提示70件
- N1a: 6ケース / 提示33件
- N1: 14ケース / 提示80件
- N2: 14ケース / 提示80件
- N4: 14ケース / 提示80件
- N5: 14ケース / 提示80件

## 指標(分母は各arm自身の提示件数。0件でも『誤り率0』とは書かず95%上限を併記)
| arm | 提示n | 意味・用法NG(確定) | 境界例 | 軽微(訳の不対応) | 自由組合せ混入 | 自然さ等(N軸) | そのまま選べる率(確定NG・境界・軽微を除く) | 一般化適用 | 一般化成功率 | 戻し数(率) | 3件以上ケース |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PROD | 66 | 0/66 (0%, 95%上限4.4%) | 2 | 0 | 19/66 (29%, 95%上限39.3%) | 19 | 26/66 (39%, 95%上限50.3%) | 18 | 14/18 (78%, 95%上限92.0%) | 0/66 (0%, 95%上限4.4%) | 4/14 |
| D | 71 | 1/71 (1%, 95%上限6.5%) | 1 | 0 | 6/71 (8%, 95%上限16.0%) | 2 | 61/71 (86%, 95%上限92.2%) | 42 | 38/42 (90%, 95%上限96.7%) | 0/71 (0%, 95%上限4.1%) | 13/14 |
| E1L | 81 | 3/81 (4%, 95%上限9.3%) | 0 | 1 | 2/81 (2%, 95%上限7.6%) | 1 | 74/81 (91%, 95%上限95.9%) | 48 | 44/48 (92%, 95%上限97.1%) | 0/81 (0%, 95%上限3.6%) | 14/14 |
| E4 | 70 | 2/70 (3%, 95%上限8.7%) | 2 | 0 | 0/70 (0%, 95%上限4.2%) | 0 | 66/70 (94%, 95%上限98.0%) | 44 | 40/44 (91%, 95%上限96.8%) | 0/70 (0%, 95%上限4.2%) | 13/14 |
| N1a | 33 | 1/33 (3%, 95%上限13.6%) | 3 | 1 | 1/33 (3%, 95%上限13.6%) | 0 | 27/33 (82%, 95%上限91.8%) | 21 | 17/21 (81%, 95%上限93.2%) | 0/33 (0%, 95%上限8.7%) | 6/6 |
| N1 | 80 | 0/80 (0%, 95%上限3.7%) | 4 | 0 | 2/80 (2%, 95%上限7.7%) | 0 | 74/80 (92%, 95%上限96.7%) | 45 | 41/45 (91%, 95%上限96.9%) | 4/80 (5%, 95%上限11.1%) | 14/14 |
| N2 | 80 | 0/80 (0%, 95%上限3.7%) | 4 | 0 | 2/80 (2%, 95%上限7.7%) | 1 | 73/80 (91%, 95%上限95.8%) | 49 | 45/49 (92%, 95%上限97.2%) | 1/80 (1%, 95%上限5.8%) | 14/14 |
| N4 | 80 | 0/80 (0%, 95%上限3.7%) | 4 | 0 | 2/80 (2%, 95%上限7.7%) | 1 | 73/80 (91%, 95%上限95.8%) | 49 | 45/49 (92%, 95%上限97.2%) | 1/80 (1%, 95%上限5.8%) | 14/14 |
| N5 | 80 | 0/80 (0%, 95%上限3.7%) | 4 | 0 | 2/80 (2%, 95%上限7.7%) | 1 | 73/80 (91%, 95%上限95.8%) | 49 | 45/49 (92%, 95%上限97.2%) | 1/80 (1%, 95%上限5.8%) | 14/14 |

## 意味・用法NG(確定)の内訳
- PROD: なし / 境界: meta_w_b1b:make room for[GLOSS_SENSE]; meta_w_a2:make room for[GLOSS_SENSE]
- D: untidi_a2:hear something out[ARG_TYPE] / 境界: untidi_b1b:hear someone out[ARG_TYPE]
- E1L: untidi_a2:hear something out[ARG_TYPE]; untidi_a2:take away from[SENSE_SHIFT]; untidi_b1b:hear something out[ARG_TYPE]
- E4: untidi_a2:hear something out[ARG_TYPE]; untidi_b1b:hear something out[ARG_TYPE] / 境界: untidi_a2:take something away from[SENSE_SHIFT]; untidi_a2:take up[FRAME_SHIFT]
- N1a: untidi_a2:hear something out[ARG_TYPE] / 境界: untidi_a2:take something away from[SENSE_SHIFT]; jwst_m_b1b:pick up[FRAME_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]
- N1: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_a2:take something away from[SENSE_SHIFT]; jwst_m_b1b:pick up[FRAME_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]
- N2: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_a2:take something away from[SENSE_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]; untidi_b1b:take points away[GLOSS_SENSE]
- N4: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_a2:take something away from[SENSE_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]; untidi_b1b:take points away[GLOSS_SENSE]
- N5: なし / 境界: untidi_a2:hear someone out[ARG_TYPE]; untidi_a2:take something away from[SENSE_SHIFT]; untidi_b1b:hear someone out[ARG_TYPE]; untidi_b1b:take points away[GLOSS_SENSE]

## 良質候補の維持(基準=E1Lで○だった候補)
- D: 脱落 26/74 (35%, 95%上限45.3%) ['make something work', 'turn something into', 'sales pitch', 'open for business', 'show up', 'rely on', 'show up', 'pick up', 'turn into', 'take something away'] / 一般化維持 28/28 (100%, 95%上限100.0%) 失った一般化 []
- E4: 脱落 18/74 (24%, 95%上限33.9%) ['make something work', 'put the brakes on', 'or so it seems', 'take a turn', 'set a limit', 'take a turn', 'show up', 'on the scale of', 'take something seriously', 'sales pitch'] / 一般化維持 32/32 (100%, 95%上限100.0%) 失った一般化 []
- N1a: 脱落 1/29 (3%, 95%上限15.3%) ['show up'] / 一般化維持 18/19 (95%, 95%上限99.7%) 失った一般化 [('ai_cha_b1b', 'or so it seemed', 'or so it seems', 'or so it seemed')]
- N1: 脱落 2/74 (3%, 95%上限8.3%) ['show up', 'for once'] / 一般化維持 40/43 (93%, 95%上限98.1%) 失った一般化 [('jwst_m_b1b', 'set a lower limit', 'set a limit', 'set a lower limit'), ('untidi_b1b', 'taking points away', 'take something away', 'take points away'), ('aiisland_b1b', 'one way around it', 'one way around', 'one way around it')]
- N2: 脱落 2/74 (3%, 95%上限8.3%) ['let go of', 'for once'] / 一般化維持 43/44 (98%, 95%上限99.9%) 失った一般化 [('untidi_b1b', 'taking points away', 'take something away', 'take points away')]
- N4: 脱落 2/74 (3%, 95%上限8.3%) ['let go of', 'for once'] / 一般化維持 43/44 (98%, 95%上限99.9%) 失った一般化 [('untidi_b1b', 'taking points away', 'take something away', 'take points away')]
- N5: 脱落 2/74 (3%, 95%上限8.3%) ['let go of', 'for once'] / 一般化維持 43/44 (98%, 95%上限99.9%) 失った一般化 [('untidi_b1b', 'taking points away', 'take something away', 'take points away')]

## 費用(円/レベル。台帳のcache原価を含む『全課金した場合』の見積。1記事セット=2レベル)
- D: 平均¥0.98/レベル → 約¥1.95/記事セット(70円比 2.8%) (14レベル)
- E1L: 平均¥1.07/レベル → 約¥2.14/記事セット(70円比 3.1%) (14レベル)
- E4: 平均¥3.14/レベル → 約¥6.29/記事セット(70円比 9.0%) (14レベル)
- N1a: 平均¥1.09/レベル → 約¥2.18/記事セット(70円比 3.1%) (6レベル)
- N1: 平均¥1.31/レベル → 約¥2.62/記事セット(70円比 3.7%) (14レベル)
- N2: 平均¥1.42/レベル → 約¥2.84/記事セット(70円比 4.1%) (14レベル)
- N4: 平均¥2.71/レベル → 約¥5.42/記事セット(70円比 7.7%) (14レベル)
- N5: 平均¥3.14/レベル → 約¥6.28/記事セット(70円比 9.0%) (14レベル)
