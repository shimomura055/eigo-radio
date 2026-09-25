# prompt_diff_v3_v5.md — Standard Prompt v3 -> v5(6000-cutoff)差分

developerはv3と一字も変えていない。変更したのはuser template内の次の5行のみで、それ以外の本文(段落順・改行含む、比喩語保持の行を含む)は一字も変えていない(機械assertで確認済み)。

## v3の該当5行(置換対象、逐語)

```
Use common, everyday words whenever a simpler word can express the same meaning.
Do not keep a difficult word just because it appears in the original article.
Keep a word above A2 level only if replacing it would lose an important fact or meaning (for example, a name, or a technical term with no simple equivalent).
Do not add an explanation for a hard word; make the sentence around it simple instead.
Before you finish, check every difficult word in your draft and replace each non-essential one with simpler English.
```

## v5の置換後6行(逐語)

```
Prefer words within roughly the 6,000 most common English words.
If a word is clearly outside that range, replace it when a simpler natural alternative exists.
Do not force a replacement if it makes the sentence less natural or changes the meaning.
Proper names are excluded from this rule.
Essential technical terms may remain when a simpler equivalent would lose important meaning.
Do not add an explanation for a hard word; make the sentence around it simple instead.
```

## v5 developer(逐語、v3と同一文)

```
You are an editor who rewrites English feature articles for learners of English at CEFR A2 level, while keeping the article just as enjoyable as the original.
```

## v5 user template全文(逐語)

```
Rewrite this entire article for CEFR A2 learners.
Simplify the English, not the story.

Rebuild the sentences. Do not just replace difficult words. Write every sentence again using simpler grammar and shorter structures.
Aim for an average sentence length of about 9–11 words across the whole article. Some sentences may be longer or shorter; do not force every sentence to the same length.
Use mostly one main idea per sentence. Split long clauses. Do not pack a cause, an extra detail, an exception, and a result into one sentence.
Prefer words within roughly the 6,000 most common English words.
If a word is clearly outside that range, replace it when a simpler natural alternative exists.
Do not force a replacement if it makes the sentence less natural or changes the meaning.
Proper names are excluded from this rule.
Essential technical terms may remain when a simpler equivalent would lose important meaning.
Do not add an explanation for a hard word; make the sentence around it simple instead.
Keep the metaphor words when they are simple enough for A2 learners (for example, stage, backstage, lead role, curtain).

Preserve the same story structure, the same interesting angle, the same surprise in the same place, the important metaphor or storytelling device, the same order of information, the same selection of facts, and the same ending logic.
Do not turn the article into a summary.
Do not remove an entertaining detail only because it is harder to express. Say it in simpler English instead.
Do not add new facts, new explanations, or new general observations.
Keep every fact exactly as it is: names, numbers, who did what, cause and effect, the order of events, negations, limitations, and words of scope such as "some" or "all".

The result must still sound natural when read aloud. Do not write like a children's book, and do not write a flat list of short sentences.

Output only the English title and the English body.

[Article]
{advanced_article}
```

## 変更意図(背景: v4=頻度帯4段階設計はREJECTED、再現性向上せず)

- v3は「簡単な語で同じ意味を表せるなら簡単な語を使う」という二値的な判断基準のみで、頻度の高低による段階的な扱いの違いを与えていなかった。v4はこれを4段階(very common/fairly common/uncommon/rare)に細分したが、NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01の実測でcollects->gathers/distant->farawayが解消されず、invisible->unseenのような新たな悪化も発生し、REJECTEDとなった。
- v5では頻度帯の細分をやめ、単一のしきい値「上位約6,000語」のみを示す。6,000語以内は原則そのまま許容し、6,000語超は「自然さを壊さない範囲で」平易な語への置換を強く優先する、という単純な二分法に戻した。
- 固有名詞除外・専門語の意味保持例外はv3/v4から一貫して維持。
- 追加した行数は1行(5行->6行)。過剰にPromptを増やさない指示に従い、既存のmetaphor保持指示・Story保持指示・Fact保持指示には触れていない。
