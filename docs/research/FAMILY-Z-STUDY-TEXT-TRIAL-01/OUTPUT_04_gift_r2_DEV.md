# OUTPUT_04 DEV記録(開発者向け。ユーザー向け本文ではない) gift r2

ユーザー向け完成形: `OUTPUT_04_gift_r2_USER.md`

## Step A: 候補・選定理由(DEV専用。ユーザー向け本文へは渡していない)

```json
{
 "candidates_considered": [
  {
   "para": "P22",
   "note": "場所表現が文頭に置かれ、主語と動詞の語順が通常と異なるうえ、combsを修飾する関係詞節も含むため選定。"
  },
  {
   "para": "P30",
   "note": "場所表現による倒置に加え、with句、関係詞節、makeを用いた構造が重なっているため選定。"
  },
  {
   "para": "P14",
   "note": "imagining以下に分詞形と目的語の関係が含まれるが、文の中心構造は比較的追いやすいため不選定。"
  },
  {
   "para": "P29",
   "note": "短い節が並列されているものの、各節の主語・動詞関係は明瞭なため不選定。"
  },
  {
   "para": "P12",
   "note": "Like Jimの比較表現はあるが、文の構造自体は単純なため不選定。"
  }
 ],
 "selected": [
  {
   "para": "P22",
   "sentence": "Inside were the tortoise-shell combs she had so often admired in a shop window.",
   "construct_ja": "場所表現による倒置",
   "points_ja": [
    "文頭のInsideに続いて動詞were、主語the tortoise-shell combsの順に並ぶ",
    "she had so often admired in a shop windowはcombsを説明し、目的語の関係詞が省略されている",
    "Insideは包みの中を指す"
   ],
   "context_ja": "デラが店の窓でよく眺めていた櫛が、ジムからの包みの中にあったことを述べている。",
   "reason_dev": "場所表現を前置した倒置により、通常の語順でない主語・動詞の位置を捉える必要がある。さらに、combsを修飾する関係詞節が続き、文の骨格と修飾関係を整理する学習価値がある。",
   "sentence_llm_raw": "Inside were the tortoise-shell combs she had so often admired in a shop window.",
   "sentence_replaced_by_body": false,
   "prev": "Then he gave her a package.",
   "next": "She held them against her chest, smiling through tears."
  },
  {
   "para": "P30",
   "sentence": "Yet here, with gifts they could not use, sat two foolish young people whose love made them the wisest of all gift-givers.",
   "construct_ja": "場所表現による倒置と複合修飾",
   "points_ja": [
    "hereを含む場所表現に続いて動詞sat、主語two foolish young peopleの順に並ぶ",
    "with gifts they could not useが二人の状況を添え、giftsの後には目的語となる関係詞が省略されている",
    "whose loveはyoung peopleを説明し、made them the wisest of all gift-giversという構造につながる"
   ],
   "context_ja": "使えない贈り物を手にした二人を述べ、続けて二人を賢者と呼んでいる。",
   "reason_dev": "倒置された主節に、with句と複数の埋め込み構造が続き、節どうしのつながりを見極める必要がある。物語の結びに位置する文であり、構造を捉えることで語り手の対比も読み取れる。",
   "sentence_llm_raw": "Yet here, with gifts they could not use, sat two foolish young people whose love made them the wisest of all gift-givers.",
   "sentence_replaced_by_body": false,
   "prev": "The magi were wise men who brought gifts on the first Christmas.",
   "next": "They were the magi."
  }
 ],
 "none_reason_dev": ""
}
```

## usage

| tag | model | sec | in | cached | out | reasoning | 円(@160) |
|---|---|---|---|---|---|---|---|
| 04a_r2_p1_gift | gpt-6-luna | 11.4 | 686 | 0 | 772 | 240 | 0.0727 |
| 04_r2_stepA_gift | gpt-6-luna | 27.9 | 1579 | 1576 | 2024 | 1194 | 0.1645 |
| 04_r2_stepB_gift | gpt-6-luna | 18.9 | 1220 | 0 | 1749 | 845 | 0.1594 |
| 04_r2_p34_gift | gpt-6-luna | 9.3 | 2154 | 0 | 817 | 404 | 0.0998 |
