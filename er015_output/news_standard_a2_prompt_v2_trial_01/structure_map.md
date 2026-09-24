# structure_map.md — 段落対応・Reveal/比喩/Ending保持確認・比喩語保持有無

## 段落数対応

- 下水道: Advanced 8段落 / v1 8段落 / v2 8段落
- Meta: Advanced 10段落 / v1 10段落 / v2 未生成(budget STOP、下水道v2の1call完了時点で累計¥1.0828が上限¥1を超過したため2call目[Meta]は実行していない)

## Reveal / 比喩 / Ending 位置(手動確認、○×)

| 記事 | Reveal維持 | 中心比喩維持 | Ending logic維持 |
|---|---|---|---|
| 下水道 v2 | ○(「登場するのが合併浄化槽」の切り替え段落がAdvanced/v2とも同じ順序で存在) | ○(洗濯機の比喩"small washing machine"/"one huge washing machine"がv2でも同一段落・同一語で保持) | ○(最終段落の"The future of sewers may arrive in a surprisingly familiar place"がv2でも同一文で保持) |
| Meta v2 | 未生成(budget STOP) | 未生成(budget STOP) | 未生成(budget STOP) |

## 比喩語保持有無(語単位、大小無視の部分一致)

| 語 | 下水道Advanced | 下水道v1 | 下水道v2 | MetaAdvanced | Metav1 | Metav2 |
|---|---|---|---|---|---|---|
| stage | - | - | - | ○ | ○ | 未生成 |
| backstage | - | - | - | ○ | ○ | 未生成 |
| lead role | - | - | - | ○ | - | 未生成 |
| curtain | - | - | - | ○ | ○ | 未生成 |
| main artery | ○ | ○ | ○ | - | - | 未生成 |
| washing machine | ○ | ○ | ○ | - | - | 未生成 |
| understudy | - | - | - | ○ | ○ | 未生成 |

## Meta「通話の一部」(some parts of the calls)の扱い(事実列挙、修正しない)

- Advanced Baseline(改変禁止): "contract workers—not AI—handled **some parts of the calls**."
- Standard v1: "contract workers—not AI—handled some parts of the calls." と同一(未変更)
- Standard v2: 未生成(budget STOP)
- 上記の曖昧さ(全体か一部かの一次情報未確認)自体はOPEN_ITEMS既存項目として保持し、本Trialでは修正しない。