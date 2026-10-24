FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_04(Fableから、API 0): Trial-02(commit 144b3fd47/c9c820d27)のFable独立評価とStatusを記録、UDR登録、DECISION_LOG、commit/push。

## Fable独立評価(逐語で `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/FABLE_EVAL_02.md` に記録、EVAL_02.md §8にも転記)
- Part 1: 実用性重視への転換は成功(文法解説の混入0、追加例文0、3件とも「使える場面」+「何が伝わるか」を含む)。参考例との比較: catch sight of=同程度 / hand down=下回る(伝統・知識までは触れたが、技術・先輩→後輩の仕事場面がない) / catch one's breath=下回る(身体的な息切れのみで、忙しさから一息つく比喩用法がない)。分量は参考例の約半分。学習者が「自分でも使える」と感じる最低線は満たすが、参考例の豊かさには2/3で未達。
- Part 2: `whose`関係詞節。正確だがTrial-01の場所の倒置より基礎的で、読み解きの助けとしてはやや劣る。許容。
- Part 3: `foolish`↔`wisest`の対比。Trial-01でFableが上位候補に挙げたテーマであり、皮肉の読み取りは英語学習上の価値がある。ただし説明は物語解釈寄りで語法の深掘りは薄い。許容(worthy/worthより題材は良い、掘り下げは同程度)。
- Part 4: 同型・同等。
- 正確性: 引用6件逐語一致、誤訳・文法誤り・創作なし。「髪用品店」は日本語としてやや不自然(ヘア用品店)だが意味は正しい(軽微)。
- 再現性: 同一Prompt・同一本文でもPart 2/3の選定対象が生成ごとに変わる(N=2で確認)。品質の上下は小さいが、Part 3は物語解釈に寄る揺れがある。
- 費用0.171円/16.8秒(Trial-01 0.230円/24.7秒)。
- **Status(Fable): VALIDATED(限定)** — 限定=(a)Part 1の方針有効性のみの検証(N=1)、(b)参考例水準にはhand down/catch one's breathで未達(仕事・社会場面と比喩用法の欠落)、(c)Part 2/3の選定は生成ごとに揺れる、(d)Production採用・Prompt固定は未承認。
- 次工程の選択肢(Fable推奨=A): (A)Part 1指示に「日常と仕事・社会の場面を各1つ以上」「比喩的・拡張的な用法があれば触れる」を加え、別作品(『猿の手』『二十年後』)を含むN=3で再現性を確認(約1円、Prompt変更はPart 1のみ) / (B)現Promptのまま採用判断へ進む(Production化設計: Prompt固定・引用逐語照合Gate・人手確認フロー) / (C)中止。推奨理由: 費用は無視でき、残る差分がPart 1指示の具体性に帰着する見込みが高く、Part 2/3の揺れもN=3で把握できる。

## 作業
1. FABLE_EVAL_02.md作成、EVAL_02.md §8転記。
2. `docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR(件名=学習テキスト解説Trial-02後の次工程、選択肢A/B/C、Fable推奨A)。OPEN-497にStatusとUDR番号を追記。`DECISION_LOG.md` 1エントリ(Trial-02実施・Fable評価・UDR)。
3. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_04.md`(Nは先頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_04」を含むAgent呼出の0始まり通番、直近477以降)。
4. Git: `git status`→`git commit --only`→`git push origin HEAD:main`(他agent差分を巻き込まない=一時index、禁止操作なし、secret grep 0件)。
5. handback: UDR番号、commit hash、raw URL。