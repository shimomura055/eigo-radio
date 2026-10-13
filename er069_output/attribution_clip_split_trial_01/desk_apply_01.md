# P1-3 机上適用 before/after (JPY0, API呼出なし)

lintしきい値(試作): 固有名詞を含む引用隣接narrator chunk>=4語 / それ以外>=3語(最終値はUSER_DECISION候補)

## a2
- 保存済みclip計画の再現: True
- clip数 before=23 after=23
- lint指摘 before=[{"id": "full_story_part1_c5", "text": "Melos said.", "wc": 2, "n_required": 4, "has_proper_noun": true}]
- lint指摘 after =[]
- 固有名詞歯擦音境界 before=[('full_story_part1_c5', 'Melos', 'said', 2)] after=[]
- 自然さ(決定論): before={'words': 408, 'sentences': 46, 'avg_sentence_len': 8.87, 'speech_verbs': {'replied': 1, 'called': 1, 'said': 4, 'asked': 1}} / after={'words': 413, 'sentences': 46, 'avg_sentence_len': 8.98, 'speech_verbs': {'replied': 1, 'called': 1, 'said': 3, 'asked': 1, 'answered': 1}}
- BEFORE本文: “Give me three days to see my sister’s wedding,” Melos said. “Then I will return to you.”
- AFTER 本文: “Give me three days to see my sister’s wedding,” Melos answered, looking straight at the ruler. “Then I will return to you.”
- AFTERで変化したclip:
  - full_story_part1_c5 [narrator] (7語): Melos answered, looking straight at the ruler.

## b1b
- 保存済みclip計画の再現: True
- clip数 before=25 after=25
- lint指摘 before=[{"id": "full_story_part1_c5", "text": "Melos said.", "wc": 2, "n_required": 4, "has_proper_noun": true}, {"id": "full_story_part3_c5", "text": "he whispered.", "wc": 2, "n_required": 3, "has_proper_noun": false}]
- lint指摘 after =[]
- 固有名詞歯擦音境界 before=[('full_story_part1_c5', 'Melos', 'said', 2), ('full_story_part2_c1', 'Melos', 'struck', 124)] after=[('full_story_part2_c1', 'Melos', 'struck', 124)]
- 自然さ(決定論): before={'words': 387, 'sentences': 57, 'avg_sentence_len': 6.79, 'speech_verbs': {'answered': 1, 'said': 2, 'asked': 1, 'whispered': 1}} / after={'words': 394, 'sentences': 57, 'avg_sentence_len': 6.91, 'speech_verbs': {'replied': 1, 'whispered': 1, 'said': 1, 'asked': 1, 'answered': 1}}
- BEFORE本文: “Give me three days,” Melos said. “My sister is getting married.
- AFTER 本文: “Give me three days,” Melos replied, holding the ruler’s gaze. “My sister is getting married.
- BEFORE本文: “I nearly abandoned you,” he whispered.
- AFTER 本文: “I nearly abandoned you,” he whispered, his voice breaking.
- AFTERで変化したclip:
  - full_story_part1_c5 [narrator] (6語): Melos replied, holding the ruler's gaze.
  - full_story_part3_c5 [narrator] (5語): he whispered, his voice breaking.
