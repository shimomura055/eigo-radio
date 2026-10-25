# OUTPUT_04 DEV記録(開発者向け。ユーザー向け本文ではない) open_window r2

ユーザー向け完成形: `OUTPUT_04_open_window_r2_USER.md`

## Step A: 候補・選定理由(DEV専用。ユーザー向け本文へは渡していない)

```json
{
 "candidates_considered": [
  {
   "para": "P1",
   "note": "採用。文頭の動名詞句が主語となる構造と、hardlyの意味を説明できる。"
  },
  {
   "para": "P29",
   "note": "不採用。動名詞句が主語となる点は有用だが、P1と解説内容が重なる。"
  },
  {
   "para": "P4",
   "note": "不採用。which以下は基本的な関係詞節である。"
  },
  {
   "para": "P28",
   "note": "不採用。with them snarling above himは基本的なwith＋目的語＋分詞の形である。"
  }
 ],
 "selected": [
  {
   "para": "P1",
   "sentence": "His doctor had recommended peace and country air, but visiting strangers was hardly peaceful.",
   "construct_ja": "動名詞句主語を含む等位接続文",
   "points_ja": [
    "visiting strangersは動名詞句で、後半の節の主語になっている",
    "butが前後の二つの節を対比している",
    "hardly peacefulは「ほとんど平穏ではない」という意味"
   ],
   "context_ja": "医師は平穏と田舎の空気を勧めたが、フラムトンは見知らぬ人を訪ねることは平穏とは言いがたいと述べている。",
   "reason_dev": "動名詞句を主語として読む必要があり、hardlyを「難しい」と取り違えず「ほとんど〜ない」と捉える点も押さえられる。短い文ながら、前後の節の対比を含めて構造と意味を説明する価値がある。",
   "sentence_llm_raw": "His doctor had recommended peace and country air, but visiting strangers was hardly peaceful.",
   "sentence_replaced_by_body": false,
   "prev": "Framton sat on the edge of his chair, turning his letter of introduction between his fingers.",
   "next": "“My aunt will be down soon,” said Vera, her fifteen-year-old niece."
  }
 ],
 "none_reason_dev": ""
}
```

## usage

| tag | model | sec | in | cached | out | reasoning | 円(@160) |
|---|---|---|---|---|---|---|---|
| 04a_r2_p1_open_window | gpt-6-luna | 10.8 | 688 | 0 | 743 | 264 | 0.0704 |
| 04_r2_stepA_open_window | gpt-6-luna | 24.4 | 1582 | 0 | 1894 | 1430 | 0.1768 |
| 04_r2_stepB_open_window | gpt-6-luna | 10.9 | 1006 | 0 | 779 | 452 | 0.0784 |
| 04_r2_p34_open_window | gpt-6-luna | 11.9 | 2040 | 0 | 826 | 516 | 0.0987 |
