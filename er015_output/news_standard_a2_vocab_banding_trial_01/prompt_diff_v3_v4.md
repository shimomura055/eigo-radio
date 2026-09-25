# prompt_diff_v3_v4.md — Standard Prompt v3 -> v4 差分(頻度帯思想+自然さ優先のみ)

developerはv3と一字も変えていない。変更したのはuser template内の次の5行のみで、それ以外の本文(段落順・改行含む、比喩語保持の行を含む)は一字も変えていない(機械assertで確認済み)。

## v3の該当5行(置換対象、逐語)

```
Use common, everyday words whenever a simpler word can express the same meaning.
Do not keep a difficult word just because it appears in the original article.
Keep a word above A2 level only if replacing it would lose an important fact or meaning (for example, a name, or a technical term with no simple equivalent).
Do not add an explanation for a hard word; make the sentence around it simple instead.
Before you finish, check every difficult word in your draft and replace each non-essential one with simpler English.
```

## v4の置換後7行(逐語)

```
Use common, everyday words whenever a simpler word can express the same meaning.
Do not keep a difficult word just because it appears in the original article.
Think about how common a word is: very common words are fine; fairly common words may stay if they sound natural; uncommon words should usually be replaced when a clearly simpler natural choice exists; rare words should be replaced unless they are names, essential technical terms, or a key metaphor.
Do not replace a difficult word if the replacement sounds less natural or is not clearly easier. Prefer natural, simple English over forced simplification.
When simplifying vocabulary, prefer a common natural phrase over an awkward one-word replacement.
Do not add an explanation for a hard word; make the sentence around it simple instead.
Before you finish, check every difficult word in your draft. Replace it only if a clearly simpler and natural choice exists.
```

## v4 developer(逐語、v3と同一文)

```
You are an editor who rewrites English feature articles for learners of English at CEFR A2 level, while keeping the article just as enjoyable as the original.
```

## v4 user template全文(逐語)

```
Rewrite this entire article for CEFR A2 learners.
Simplify the English, not the story.

Rebuild the sentences. Do not just replace difficult words. Write every sentence again using simpler grammar and shorter structures.
Aim for an average sentence length of about 9–11 words across the whole article. Some sentences may be longer or shorter; do not force every sentence to the same length.
Use mostly one main idea per sentence. Split long clauses. Do not pack a cause, an extra detail, an exception, and a result into one sentence.
Use common, everyday words whenever a simpler word can express the same meaning.
Do not keep a difficult word just because it appears in the original article.
Think about how common a word is: very common words are fine; fairly common words may stay if they sound natural; uncommon words should usually be replaced when a clearly simpler natural choice exists; rare words should be replaced unless they are names, essential technical terms, or a key metaphor.
Do not replace a difficult word if the replacement sounds less natural or is not clearly easier. Prefer natural, simple English over forced simplification.
When simplifying vocabulary, prefer a common natural phrase over an awkward one-word replacement.
Do not add an explanation for a hard word; make the sentence around it simple instead.
Before you finish, check every difficult word in your draft. Replace it only if a clearly simpler and natural choice exists.
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

## 変更意図

- v3は「簡単な語で同じ意味を表せるなら簡単な語を使う」という二値的な判断基準のみで、頻度の高低による段階的な扱いの違いを与えていなかった(結果としてinstallation->putting in、collects->gathers、distant->farawayのような不自然な一語置換が発生した)。
- v4では「very common/fairly common/uncommon/rare」という4段階の頻度感覚を言語化し、頻度帯が下がるほど置換寄りにする一方、「置換後が自然でない・明確に簡単でないなら置換しない」という歯止めを明示した。
- 「一語での不自然な置換より、自然な言い換えフレーズを優先する」行を追加し、awkward one-word replacement(putting inのような不自然置換)を狙って抑制する。
- 最後のself-check行を「非本質的な難語を全て置換する」から「明確に簡単で自然な代替がある場合のみ置換する」に変更し、無理な置換の強制を弱めた。
- 追加した行数は2行(5行->7行)。Promptを過剰に長くしないため、既存のmetaphor保持指示・Story保持指示・Fact保持指示には触れていない。
