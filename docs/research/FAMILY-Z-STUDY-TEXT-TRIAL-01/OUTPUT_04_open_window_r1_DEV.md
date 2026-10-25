# OUTPUT_04 DEV記録(開発者向け。ユーザー向け本文ではない) open_window r1

ユーザー向け完成形: `OUTPUT_04_open_window_r1_USER.md`

## Step A: 候補・選定理由(DEV専用。ユーザー向け本文へは渡していない)

```json
{
 "candidates_considered": [
  {
   "para": "P23",
   "note": "「the＋形容詞」が人々を表す名詞句になる用法があり、誰が主語なのかをつかむ助けになるため採用。"
  },
  {
   "para": "P29",
   "note": "動名詞句が主語だが、基本的な動名詞の用法にとどまるため不採用。"
  },
  {
   "para": "P15",
   "note": "現在分詞句が主語の動作と同時の様子を表すが、基本的な分詞句の用法のため不採用。"
  },
  {
   "para": "P4",
   "note": "関係詞節が直前の名詞を説明する基本的な構造のため不採用。"
  }
 ],
 "selected": [
  {
   "para": "P23",
   "sentence": "The dead were coming towards the house.",
   "construct_ja": "the＋形容詞の名詞化",
   "points_ja": [
    "the dead は「死んだ人々」を表し、dead の後に people などの名詞は置かれていない",
    "文の主語は the dead 全体である",
    "were coming は、彼らが家に向かって来る動きを表す"
   ],
   "context_ja": "芝生を渡ってくる三人の姿を見たフラムトンが、死者たちが家に向かっていると受け止める場面の文。",
   "reason_dev": "短い文ながら、the＋形容詞が人々を指す名詞句になる用法を押さえることで主語の解釈が明確になる。物語の誤解が生じる場面にも直結する表現である。",
   "sentence_llm_raw": "The dead were coming towards the house.",
   "sentence_replaced_by_body": false,
   "prev": "Framton could scarcely breathe.",
   "next": "He grabbed his hat and stick and rushed out."
  }
 ],
 "none_reason_dev": ""
}
```

## usage

| tag | model | sec | in | cached | out | reasoning | 円(@160) |
|---|---|---|---|---|---|---|---|
| 04a_r1_p1_open_window | gpt-6-luna | 13.5 | 688 | 0 | 974 | 431 | 0.0889 |
| 04_r1_stepA_open_window | gpt-6-luna | 29.5 | 1582 | 1579 | 2320 | 1855 | 0.1882 |
| 04_r1_stepB_open_window | gpt-6-luna | 6.5 | 976 | 0 | 569 | 179 | 0.0611 |
| 04_r1_p34_open_window | gpt-6-luna | 11.6 | 2087 | 0 | 793 | 500 | 0.0968 |
