# violence_death_tags.md

管理ID: FICTION-STORY-DNA-E-AXIS-REDESIGN-01
タグ定義: `retrial_design.md`(目的B)の基準どおり。
- `violence`: none / threat / injury / killing
- `death_role`: none / 背景 / 中心
- keyword_hits: `why_interesting`/`reason_for_choice`中の
  tension/danger/kill/death/threat(部分文字列、大文字小文字無視)。

観察のみ、因果は断定しない。Sonnetによる目視分類(参考指標)。

## A. 新Trial(FICTION-STORY-DNA-E-AXIS-REDESIGN-01、新E軸)

### A-1. Core Provocation候補(5 Run合計14案、3+3+3+3+2)

| Run | Cand# | 選択 | E値(DNA) | violence | death_role | why keyword | reason keyword |
|---|---|---|---|---|---|---|---|
| 1 | 0 | ○ | realistic-socially-unusual | none | none | - | - |
| 1 | 1 |  | (同上) | threat | none | - | - |
| 1 | 2 |  | (同上) | none | none | tension, danger | - |
| 2 | 0 | ○ | (E軸なし) | none | none | - | - |
| 2 | 1 |  | (同上) | none | none | danger | - |
| 2 | 2 |  | (同上) | none | none | - | - |
| 3 | 0 | ○ | reality-one-changed-rule | injury(示唆、事故隠蔽) | none | - | - |
| 3 | 1 |  | (同上) | none | none | - | - |
| 3 | 2 |  | (同上) | none | none | danger | - |
| 4 | 0 | ○ | future | threat(ロボット事故未遂) | none | danger | danger |
| 4 | 1 |  | (同上) | **killing**(office murder) | **中心** | - | - |
| 4 | 2 |  | (同上) | none | none | - | - |
| 5 | 0 | ○ | future | none | 背景(亡き娘) | - | - |
| 5 | 1 |  | (同上) | none | **中心**(妻の死の真相) | - | tension |

**候補14案の集計**: violence=killing 1/14、injury 1/14、threat 2/14、
none 10/14。death_role=中心 2/14(いずれも非選択案)、背景 1/14(選択案)、
none 11/14。**選択された5案(chosen_index=0が全Run)には`killing`タグが
1つも含まれない**(唯一の`killing`候補はRun4 C1で、選ばれなかった)。

### A-2. Story本文(5本、実際に書かれた記事)

| Run | タイトル | violence | death_role | 備考 |
|---|---|---|---|---|
| 1 | The Brass Key | none | none | 認知症の男の矛盾した回想、暴力・死の明示なし |
| 2 | The Memory Test | none | none | 謎の少女、暴力・死の明示なし |
| 3 | The Memory She Left Behind | injury(示唆) | none | 安全報告書の改ざん・事故の濡れ衣(警備員への責任転嫁)、死の明言なし |
| 4 | The Memory Trade | threat | none | ロボット暴走の危険、実際の負傷は回避される |
| 5 | The Borrowed Memory | none | 背景 | 亡き娘(12年前)が前提設定、暴力描写なし |

**Story5本の集計**: `killing`0/5、`injury`1/5(示唆のみ)、`threat`1/5、
`none`3/5。`death_role`=`中心`0/5、`背景`1/5、`none`4/5。

## B. 前回Trial(FICTION-CORE-PROVOCATION-PROMPT-BIAS-RETRIAL-01、旧E軸)との比較

### B-1. Core Provocation候補(5 Run合計13案、2+3+3+2+3)

| Run | Cand# | 選択 | E値(DNA) | violence | death_role |
|---|---|---|---|---|---|
| 1 | 0 | ○ | a near future | **killing** | **中心** |
| 1 | 1 |  | (同上) | **killing** | **中心** |
| 2 | 0 | ○ | (E軸なし) | none | none |
| 2 | 1 |  | (同上) | none | none |
| 2 | 2 |  | (同上) | none | none |
| 3 | 0 |  | 超自然 | none | none |
| 3 | 1 | ○ | 超自然 | none | 背景(母がゴースト) |
| 3 | 2 |  | 超自然 | none | 中心(未来の死の予告) |
| 4 | 0 | ○ | 技術・制度世界 | **killing** | **中心** |
| 4 | 1 |  | (同上) | none | 中心(同僚の死) |
| 5 | 0 |  | 技術・制度世界 | **killing** | **中心** |
| 5 | 1 |  | (同上) | threat(死の予告) | 中心 |
| 5 | 2 | ○ | (同上) | **killing** | **中心** |

**候補13案の集計**: `killing` 4/13、`threat` 1/13、`none` 8/13。
`death_role`=`中心` 6/13、`背景` 1/13、`none` 6/13。**選択された5案のうち
3案(Run1/4/5)が`killing`タグ**(新Trialの選択5案は0/5)。

### B-2. Story本文(5本)

| Run | タイトル | violence | death_role |
|---|---|---|---|
| 1 | The Last Memory | killing | 中心 |
| 2 | The Missing Face | none | 中心(生徒の水難死・学校の隠蔽) |
| 3 | The Last Memory | none | 背景(母がゴースト) |
| 4 | The Borrowed First Day | killing | 中心 |
| 5 | The Sealed Memory | killing | 中心 |

**Story5本の集計**: `killing` 3/5、`none` 2/5。`death_role`=`中心` 4/5、
`背景` 1/5。

## C. 新旧比較の観察(因果は断定しない)

- 選択されたCore Provocation候補5本のうち`killing`タグは、旧Trial3/5→
  新Trial0/5。Story本文も旧3/5→新0/5。
- ただし`killing`を含む候補自体は新Trialにも存在した(Run4 C1「office
  murderの記憶」)。旧Trialとの違いは「候補が生成されなくなった」ことでは
  なく、「候補が選ばれなくなった」ことである(観察、因果断定なし)。
- `death_role=背景`(亡くなった家族などが前提設定として存在するが中心の
  謎ではない)は新旧とも1/5で変化なし(新: Run5亡き娘、旧: Run3亡き母)。
- E軸が非現実系(旧: 技術/未来系、新: future/one-changed-rule)のRunで
  `killing`が発生する傾向は旧Trialで顕著だったが(旧Run1/4/5全てE軸が
  技術・未来系かつ`killing`)、新Trialでは同じくE軸が非現実系のRun3/4/5の
  うちkillingを選んだRunは0(Run3=injury示唆、Run4=threatのみ、Run5=
  背景死のみ)。E軸が現実系または欠如のRun(新Run1/2、旧Run2)はいずれの
  Trialでもkillingなし(一貫)。
- `why_interesting`/`reason_for_choice`中の"tension"/"danger"の出現数は
  新Trial: tension3件・danger5件(旧Trialは本タグ付け対象外、旧REPORT未集計
  のためTrial間比較はしない、新Trial内の観察のみ)。"kill"/"death"/
  "threat"の文字列自体はwhy_interesting/reason_for_choiceには一度も出現
  しなかった(新Trial、candidates全14件・reason5件を確認)。killing/threat
  タグは本文の内容から判定したものであり、要約文の語彙とは独立している。
