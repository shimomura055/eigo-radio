# OUTPUT_04 DEV記録(開発者向け。ユーザー向け本文ではない) ig_nobel r1

ユーザー向け完成形: `OUTPUT_04_ig_nobel_r1_USER.md`

## Step A: 候補・選定理由(DEV専用。ユーザー向け本文へは渡していない)

```json
{
 "candidates_considered": [
  {
   "para": "P3",
   "note": "採用。分詞句と前置詞句が連なる名詞句で、修飾関係や取り出し元の係り先を整理する必要がある。"
  },
  {
   "para": "P7",
   "note": "不採用。命令文に続く and の結果表現と慣用句はあるが、文全体の構造は比較的追いやすい。"
  },
  {
   "para": "P9",
   "note": "不採用。動名詞句が suggest の目的語となる that 節の主語だが、基本的な節構造の範囲にとどまる。"
  },
  {
   "para": "P11",
   "note": "採用。rather than による対比に加え、目的を表す不定詞と young を修飾する関係節が重なっている。"
  },
  {
   "para": "P5",
   "note": "不採用。比較表現はあるものの、数量比較の基本構造を確認する内容が中心となる。"
  }
 ],
 "selected": [
  {
   "para": "P3",
   "sentence": "The researchers took out protein crystals containing nutrients from the gut of the unborn young.",
   "construct_ja": "分詞句の後置修飾と前置詞句の係り受け",
   "points_ja": [
    "containing nutrients は直前の protein crystals を修飾する",
    "from the gut of the unborn young は結晶を取り出した場所を示す",
    "the unborn young は、まだ生まれていない子を指す"
   ],
   "context_ja": "研究者が、体内で子を育てる種類のゴキブリの未出生の子の腸から、栄養を含むタンパク質結晶を取り出したことを述べている。",
   "reason_dev": "分詞句と場所を表す前置詞句が連続し、修飾先や句のまとまりを誤認しやすい。構造を整理することで、栄養を含むものと結晶の採取場所を正確に把握できる。",
   "sentence_llm_raw": "The researchers took out protein crystals containing nutrients from the gut of the unborn young.",
   "sentence_replaced_by_body": false,
   "prev": "The study looked at a kind of cockroach that raises its young inside its body.",
   "next": "You may have thought you were heading to the milk aisle, but instead you were shown the food store inside a body."
  },
  {
   "para": "P11",
   "sentence": "Rather than seeing this as a possible breakfast for people, see it as a way to deliver nutrients to young that have not yet been born.",
   "construct_ja": "rather than による対比と see A as B の構文",
   "points_ja": [
    "Rather than seeing ... は「…と見るのではなく」という対比を作る",
    "see it as ... は「それを…と見る」という命令文",
    "to deliver ... は way を説明し、that have not yet been born は young を修飾する"
   ],
   "context_ja": "本文の最後で、これを人の朝食候補ではなく、まだ生まれていない子に栄養を届ける方法として見るよう促している。",
   "reason_dev": "対比句の後に命令文が続き、さらに不定詞句と関係節が重なるため、文の骨格と修飾関係を分けて捉える学習価値がある。",
   "sentence_llm_raw": "Rather than seeing this as a possible breakfast for people, see it as a way to deliver nutrients to young that have not yet been born.",
   "sentence_replaced_by_body": false,
   "prev": "Behind the flashy number, you may find something else that is interesting.",
   "next": "You don’t need the courage to drink it."
  }
 ],
 "none_reason_dev": ""
}
```

## usage

| tag | model | sec | in | cached | out | reasoning | 円(@160) |
|---|---|---|---|---|---|---|---|
| 04a_r1_p1_ig_nobel | gpt-6-luna | 12.5 | 688 | 0 | 891 | 421 | 0.0823 |
| 04_r1_stepA_ig_nobel | gpt-6-luna | 20.2 | 1541 | 0 | 2439 | 1636 | 0.2198 |
| 04_r1_stepB_ig_nobel | gpt-6-luna | 13.3 | 1230 | 0 | 1339 | 638 | 0.1268 |
| 04_r1_p34_ig_nobel | gpt-6-luna | 6.5 | 2071 | 0 | 563 | 238 | 0.0782 |
