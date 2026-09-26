# dna_diff.md

管理ID: FICTION-STORY-DNA-E-AXIS-REDESIGN-01
比較: 乾式(APIコールなし)`--step dna --seed-base 20260925`の出力
(`er018_output/fiction_story_dna_e_axis_redesign_01/dna_log.json`、新E軸)と、
前回Trial(FICTION-CORE-PROVOCATION-PROMPT-BIAS-RETRIAL-01、旧E軸)の
`er018_output/fiction_core_provocation_prompt_bias_retrial_01/dna_log.json`
(同一seed_base=20260925)。

## Run1(A=strangers, E軸あり、非Coverage)

- axes: 旧`[A, E]` → 新`[A, E]`(不変)
- A値: 旧`strangers` → 新`strangers`(不変)
- E値: 旧`a near future`(index1) → 新`realistic but socially unusual
  situation`(index1)。**同じindex(1)が選ばれており、値リストの入れ替え以外
  の挙動変化なし**。

## Run2(C=a secret, D=school、E軸なし)

- axes: 旧`[C, D]` → 新`[C, D]`(不変)
- C値: 旧`a secret` → 新`a secret`(不変)
- D値: 旧`school` → 新`school`(不変)
- **E軸を参照しないRunのため、完全一致(byte単位で同一)。E軸の値リスト変更
  の影響を一切受けないことを確認。**

## Run3(A=colleagues, B=bittersweet, E軸あり、非Coverage)

- axes: 旧`[A, B, E]` → 新`[A, B, E]`(不変)
- A値: 旧`colleagues` → 新`colleagues`(不変)
- B値: 旧`bittersweet` → 新`bittersweet`(不変)
- E値: 旧`a supernatural or fantastical world`(index4) → 新`reality with
  one changed rule`(index4)。**同じindex(4)。**

## Run4(C=an exchange, D=a workplace, E軸あり、非Coverage)

- axes: 旧`[C, D, E]` → 新`[C, D, E]`(不変)
- C値: 旧`an exchange` → 新`an exchange`(不変)
- D値: 旧`a workplace` → 新`a workplace`(不変)
- E値: 旧`a world with technology or institutions that do not exist in
  reality`(index3) → 新`future`(index3)。**同じindex(3)。**

## Run5(Coverage Run、E軸強制)

- axes: 旧`[C, D, E]` → 新`[C, D, E]`(軸の集合自体は不変)
- E値: 旧`a world with technology or institutions that do not exist in
  reality`(旧`rng.choice([1,2,3])`の結果index3) → 新`future`(新
  `rng.choice([3])`の結果、常にindex3)。E値自体は今回のseedではたまたま
  同じindex(3)に対応する結果だった。
- **C値: 旧`a reversal` → 新`a loss`(変化)**
- **D値: 旧`a hospital` → 新`a public space`(変化)**

**原因(e_axis_redesign_notes.md参照)**: `random.Random.choice()`は要素数に
応じて内部で消費する乱数ビット数(`_randbelow`のbit_length)が異なるため、
`rng.choice([1,2,3])`(3要素)と`rng.choice([3])`(1要素)は同じ`rng`インス
タンス・同じseedでも、呼び出し後の内部状態が異なる。その結果、Run5内で
E軸選択の**後に**行われるC/D軸の値選択(`rng.sample`/`rng.randrange`)が
異なる乱数列を消費し、選ばれる値が変わった。これはE軸の値リストの個数を
変えたこと(6→6で同数だが、Coverage母集団のリスト長を3→1にしたこと)に
起因する副作用であり、Run5以外には波及しない(Run1-4はCoverage分岐を
通らないため無関係)。

## まとめ

- **E軸を持たないRun(Run2)は完全不変**(byte単位で一致)。
- **E軸を持つ非Coverage Run(Run1/3/4)は、選択されるindexが旧新で一致し、
  値ラベルのみが新E軸に変わった**(値リストの要素数が旧新とも6で同じため)。
- **Coverage Run(Run5)のみ、E軸のindex自体は同じ(3)だが、母集団リストの
  長さを3→1に変更した副作用でC/D軸の値が変化した**。これはE軸の値リスト
  変更に伴う設計判断(e_axis_redesign_notes.md参照)の直接的帰結であり、
  想定内の変化として本Trialに含める。
