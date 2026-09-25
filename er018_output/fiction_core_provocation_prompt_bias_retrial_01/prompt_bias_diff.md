# prompt_bias_diff.md
管理ID: FICTION-CORE-PROVOCATION-PROMPT-BIAS-RETRIAL-01
Step1: 前回スクリプト(`er018_fiction_core_provocation_random_dna_trial_01.py`)
の全文精査結果。「特定の世界設定の選択肢を列挙する文言」を洗い出し、除去対象/
維持対象を分類する。

## 全文grep結果(前回スクリプト、対象語: future/unreal/speculative/imagined/
fantastical/real world/realistic)
```
5:  # 目的: 旧Future(er013_family_c_future_provocation_08.py /
6:  # er013_family_c_future_writer_08.py、Trial-08)の良かった設計 --
9:  # ("about the future"/"imagined-future story"等)を外してFictionへ拡張する。
14: # 既存er013_family_c_future_*.py・er013_output/family_c_future_trial_*/は
27: from __future__ import annotations
87:  ("a near future", "少し先の未来"),
88:  ("a greatly changed future", "大きく変わった未来"),
90:  ("a supernatural or fantastical world", "超自然・幻想的な世界"),
196: "in the real world, the future, an unreal/fantastical setting, or an "
197: "imagined/speculative world -- that would make a reader feel 'I want to know what "
313: "The setting can be realistic, near-future, far-future, or entirely "
314: "unreal/speculative -- whatever fits the Core Provocation best. Do not force the "
337: setting fits it best (real, future, unreal, or an imagined/speculative world). Make \
707: "ref_trial08_memory": "er013_output/family_c_future_trial_08/memory/reader_facing_article.txt",
```

## 分類

| # | 行番号(前回スクリプト) | 文言(逐語) | 判定 |
|---|---|---|---|
| 1 | 5-9, 14 | コメント(設計意図の説明文、コード外) | 対象外(Promptではない。コメントのみ、新スクリプトでは経緯説明として書き換える) |
| 2 | 27 | `from __future__ import annotations`(Python標準構文、themeとは無関係) | 対象外(Promptではない) |
| 3 | 87-90 | `AXIS_DEFS["E"]["values"]`内の"a near future"/"a greatly changed future"/"a supernatural or fantastical world"等 | **維持**(Story DNA E軸の値そのもの。DNAブロック経由でLLMへ渡る部分であり、委任文により変更禁止) |
| 4 | 196-197 | `CORE_PROVOCATION_DEVELOPER_MESSAGE`内: "A Core Provocation is a single central idea or question -- regardless of whether the story takes place in the real world, the future, an unreal/fantastical setting, or an imagined/speculative world -- that would make a reader feel..." | **除去対象**(旧Future由来の世界設定列挙。全Run共通のdeveloper messageであり、E軸を持たないRunにも技術/未来系の連想を与えていた可能性がある) |
| 5 | 313-314 | `WRITER_DEVELOPER_MESSAGE`内: "The setting can be realistic, near-future, far-future, or entirely unreal/speculative -- whatever fits the Core Provocation best." | **除去対象**(同上。Writer developer message、全Run共通) |
| 6 | 337 | `WRITER_PROMPT_TEMPLATE`の[Your single job]内: "Write a short story built around the Core Provocation above, in whatever kind of setting fits it best (real, future, unreal, or an imagined/speculative world)." | **除去対象**(同上。Writer prompt、全Run共通) |
| 7 | 707 | `REFERENCE_DOCS`の参照ファイルpath文字列(`er013_output/family_c_future_trial_08/...`) | 対象外(既存Trial-08成果物への参照パス。Promptではなく分析用の外部参照であり、旧Trial-08 read-onlyのため変更しない) |

4共通原則ブロック(`COMMON_PRINCIPLES`)・Story DNAナッジブロック(`DNA_BLOCK_TEMPLATE`)
には、世界設定を列挙する文言は含まれていなかった(grep該当なし)。したがって
「要判断」に該当する箇所はなし。

## Before/After(逐語、該当#4-6のみ変更)

### #4: CORE_PROVOCATION_DEVELOPER_MESSAGE

**Before(前回スクリプト 192-204行、逐語)**
```
"You are brainstorming Core Provocations for a short fiction story in an "
"English-learning magazine's Fiction article family. A Core Provocation is a "
"single central idea or question -- regardless of whether the story takes place "
"in the real world, the future, an unreal/fantastical setting, or an "
"imagined/speculative world -- that would make a reader feel 'I want to know what "
"happens next' and 'I have never thought about it this way before'. Come up with 1 "
"to 3 promising central ideas for the given theme (fewer, stronger ideas are "
"better than three weak ones -- do not pad to 3 just to fill the list). Do NOT "
"classify ideas by scale (intimate/personal vs societal vs radical) or by any "
"other fixed category -- just judge which idea is most genuinely interesting and "
"story-worthy. Then pick the single most interesting one to write as the article."
```

**After(新スクリプト、除去方式: 列挙句を単純削除)**
```
"You are brainstorming Core Provocations for a short fiction story in an "
"English-learning magazine's Fiction article family. A Core Provocation is a "
"single central idea or question that would make a reader feel 'I want to know "
"what happens next' and 'I have never thought about it this way before'. Come up "
"with 1 to 3 promising central ideas for the given theme (fewer, stronger ideas "
"are better than three weak ones -- do not pad to 3 just to fill the list). Do "
"NOT classify ideas by scale (intimate/personal vs societal vs radical) or by "
"any other fixed category -- just judge which idea is most genuinely interesting "
"and story-worthy. Then pick the single most interesting one to write as the "
"article."
```
差分: `-- regardless of whether the story takes place in the real world, the
future, an unreal/fantastical setting, or an imagined/speculative world --` を
削除しただけ。新しい誘導語は追加していない。

### #5: WRITER_DEVELOPER_MESSAGE

**Before(前回スクリプト 307-318行、逐語)**
```
"You are the Writer for an English-learning magazine's Fiction article family. "
"Your single most important job is to make the reader genuinely feel the Core "
"Provocation given to you -- excitement, a little tension, and a question that "
"stays with them, so they want to keep reading. Write it as a story: a vivid scene "
"built around the Core Provocation, not a summary of studies or an abstract essay. "
"The setting can be realistic, near-future, far-future, or entirely "
"unreal/speculative -- whatever fits the Core Provocation best. Do not force the "
"story into any fixed template, fixed number of scenes, fixed number of emotional "
"turns, or a fixed ending shape -- choose whatever shape makes this particular Core "
"Provocation land most strongly."
```

**After(新スクリプト、除去方式: 世界設定列挙の1文を単純削除)**
```
"You are the Writer for an English-learning magazine's Fiction article family. "
"Your single most important job is to make the reader genuinely feel the Core "
"Provocation given to you -- excitement, a little tension, and a question that "
"stays with them, so they want to keep reading. Write it as a story: a vivid scene "
"built around the Core Provocation, not a summary of studies or an abstract essay. "
"Do not force the story into any fixed template, fixed number of scenes, fixed "
"number of emotional turns, or a fixed ending shape -- choose whatever shape makes "
"this particular Core Provocation land most strongly."
```
差分: `The setting can be realistic, near-future, far-future, or entirely
unreal/speculative -- whatever fits the Core Provocation best.` の1文を削除
しただけ。新しい誘導語は追加していない。

### #6: WRITER_PROMPT_TEMPLATE [Your single job]

**Before(前回スクリプト 335-341行、逐語)**
```
[Your single job]
Write a short story built around the Core Provocation above, in whatever kind of \
setting fits it best (real, future, unreal, or an imagined/speculative world). Make \
a reader genuinely feel something, want to keep reading, and feel some excitement and \
a little tension along the way. Do not follow any fixed structure, fixed number of \
scenes, fixed number of emotional turns, or a fixed ending shape -- choose whatever \
narrative shape makes THIS Core Provocation land most strongly.
```

**After(新スクリプト、除去方式: 世界設定列挙の括弧句を単純削除)**
```
[Your single job]
Write a short story built around the Core Provocation above. Make a reader \
genuinely feel something, want to keep reading, and feel some excitement and a \
little tension along the way. Do not follow any fixed structure, fixed number of \
scenes, fixed number of emotional turns, or a fixed ending shape -- choose whatever \
narrative shape makes THIS Core Provocation land most strongly.
```
差分: `, in whatever kind of setting fits it best (real, future, unreal, or an
imagined/speculative world)` を削除しただけ(文末の"above"の後にピリオドを
付けて文を閉じる、句読点調整のみ)。新しい誘導語は追加していない。

## 変更しない箇所(確認)
- `AXIS_DEFS`(5軸の定義・値)・`select_dna`/`build_dna_log`(乱数選定ロジック)・
  `seed_base=20260925`・各Run seed(20260926-20260930)・`COVERAGE_RUN_NUMBER=5`・
  `E_FUTURE_VALUE_INDICES`・`COMMON_PRINCIPLES`・`DNA_BLOCK_TEMPLATE`・
  `MAX_CHARACTERS`・`WORD_TARGET`/`WORD_ACCEPTABLE_RANGE`(280-420)は一切変更しない。
- 前回スクリプト`er018_fiction_core_provocation_random_dna_trial_01.py`と出力
  `er018_output/fiction_core_provocation_random_dna_trial_01/`は変更しない。
