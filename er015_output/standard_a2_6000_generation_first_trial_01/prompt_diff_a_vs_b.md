# prompt_diff_a_vs_b.md

STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01

A sha256(観測値, Production定数`STANDARD_A2_PROMPT_SHA256`とは正規化方式が異なる可能性があるため'観測値'と明記)=9051029d6c3bf561829dd5d4c2b3067b87650e5c79f7b8b2ecc626979084d972

B sha256=d43225c7c7c495c7e03d8b1de1eff90861f0062c569a542d3a80938ef6ce411d

## A(Control)全文

```text
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

Keep the same Markdown structure (the "# " title, the two "### " sections, and the final "## In one line" section); do not add or remove sections.

Output only the English title and the English body.

[Article]
{advanced_article}
```

## B(Trial、Generation-First)全文

```text
Rewrite this entire article for CEFR A2 learners.
Simplify the English, not the story.

Rebuild the sentences. Do not just replace difficult words. Write every sentence again using simpler grammar and shorter structures.
Aim for an average sentence length of about 9–11 words across the whole article. Some sentences may be longer or shorter; do not force every sentence to the same length.
Use mostly one main idea per sentence. Split long clauses. Do not pack a cause, an extra detail, an exception, and a result into one sentence.
As a basic principle, write naturally using words within roughly the top 6,000 most common English words. Do not generate a hard word first and then swap out only that one word afterward; instead, from the first draft, build the whole sentence around simpler words so its meaning is expressed naturally from the start (for example: instead of writing a hard word X and later replacing just X, restructure the entire sentence around easy words that already carry the same meaning).
Do not change the meaning: keep the same action, cause and effect, actor, object, quantity, time, and facts. A simplification that changes what actually happens (for example, turning "flush" into "use") is not allowed.
Do not escape one hard word by repeatedly adding long, unnatural explanatory phrases; that makes the writing heavy. Keep it light and direct, the way the rest of the article already reads.
Keep the storytelling: this is not a summary. Do not cut an interesting detail or part of the storyline, and do not mechanically remove a metaphor. Simplify only the wording, not the story.
A true proper noun, an official name, a name essential to the article's subject, or a word whose simpler natural alternative would clearly break meaning precision may stay even if it is outside the top 6,000 words.
Do not sort each word into fixed exception categories, and do not list candidate words or output a classification for each word. Writing one naturally good CEFR A2 article matters more than labeling exceptions.

Preserve the same story structure, the same interesting angle, the same surprise in the same place, the important metaphor or storytelling device, the same order of information, the same selection of facts, and the same ending logic.
Do not turn the article into a summary.
Do not remove an entertaining detail only because it is harder to express. Say it in simpler English instead.
Do not add new facts, new explanations, or new general observations.
Keep every fact exactly as it is: names, numbers, who did what, cause and effect, the order of events, negations, limitations, and words of scope such as "some" or "all".

The result must still sound natural when read aloud. Do not write like a children's book, and do not write a flat list of short sentences.

Keep the same Markdown structure (the "# " title, the two "### " sections, and the final "## In one line" section); do not add or remove sections.

Output only the English title and the English body.

[Article]
{advanced_article}
```

## 逐語diff(unified diff)

```diff
--- A (Control, Standard v5 Production Prompt, unchanged)
+++ B (Trial, Generation-First 6000)
@@ -4,13 +4,12 @@
 Rebuild the sentences. Do not just replace difficult words. Write every sentence again using simpler grammar and shorter structures.
 Aim for an average sentence length of about 9–11 words across the whole article. Some sentences may be longer or shorter; do not force every sentence to the same length.
 Use mostly one main idea per sentence. Split long clauses. Do not pack a cause, an extra detail, an exception, and a result into one sentence.
-Prefer words within roughly the 6,000 most common English words.
-If a word is clearly outside that range, replace it when a simpler natural alternative exists.
-Do not force a replacement if it makes the sentence less natural or changes the meaning.
-Proper names are excluded from this rule.
-Essential technical terms may remain when a simpler equivalent would lose important meaning.
-Do not add an explanation for a hard word; make the sentence around it simple instead.
-Keep the metaphor words when they are simple enough for A2 learners (for example, stage, backstage, lead role, curtain).
+As a basic principle, write naturally using words within roughly the top 6,000 most common English words. Do not generate a hard word first and then swap out only that one word afterward; instead, from the first draft, build the whole sentence around simpler words so its meaning is expressed naturally from the start (for example: instead of writing a hard word X and later replacing just X, restructure the entire sentence around easy words that already carry the same meaning).
+Do not change the meaning: keep the same action, cause and effect, actor, object, quantity, time, and facts. A simplification that changes what actually happens (for example, turning "flush" into "use") is not allowed.
+Do not escape one hard word by repeatedly adding long, unnatural explanatory phrases; that makes the writing heavy. Keep it light and direct, the way the rest of the article already reads.
+Keep the storytelling: this is not a summary. Do not cut an interesting detail or part of the storyline, and do not mechanically remove a metaphor. Simplify only the wording, not the story.
+A true proper noun, an official name, a name essential to the article's subject, or a word whose simpler natural alternative would clearly break meaning precision may stay even if it is outside the top 6,000 words.
+Do not sort each word into fixed exception categories, and do not list candidate words or output a classification for each word. Writing one naturally good CEFR A2 article matters more than labeling exceptions.
 
 Preserve the same story structure, the same interesting angle, the same surprise in the same place, the important metaphor or storytelling device, the same order of information, the same selection of facts, and the same ending logic.
 Do not turn the article into a summary.

```
