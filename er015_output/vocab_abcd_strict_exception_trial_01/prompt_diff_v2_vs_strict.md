# prompt_diff_v2_vs_strict.md

## 目的

前回Trial(ADVANCED-VOCAB-RULE-TRIAL-01 v2 / STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01が流用したv2のRULE_BLOCK_EN_V2)と、本Trialの厳格版RULE_BLOCK_EN_STRICTの差分を、閾値を12,000に揃えたうえで逐語diffとして示す(数字の違いによる差分ノイズを除去するため)。

## 結論

- 一般原則(閾値超は原則平易化候補、機械的禁止リストではない)とAの定義は実質変更なし。

- Bの定義に、「カタカナ語が存在するだけでは不十分」「英語語形との対応が分かりにくい/専門領域限定/文中で理解しにくい場合はBにしない」という否定条件と、leak/pause/curtainの再判定指示を明示的に追加した。

- Cの定義から、v2で追加した「記事中で引用符に入っている語は(固有名詞と同列に)事実として保護する」という一般化された条件を削除し、「本当の固有名詞・公式名称・固有の引用名称」のみに限定した。「一般名詞が引用符に入っているだけ」「一般的な技術用語」「記事中で引用されているだけ」「Writerが強調のため引用符を付けただけ」は明示的にCの否定条件とした(個別語名septicはPromptに書かず、定義文のみで導けるかを検証する)。

- Dの定義に、「専門用語だから/元記事で使われているから/比喩として少し自然だから/Writerの表現として気に入っているから/置換すると少し雰囲気が変わるから」は理由にしない、という否定条件と、artery/sewer(s)/flush/septicの再評価指示を明示的に追加した。


## RULE_BLOCK_EN diff (v2 -> strict、閾値は両方12,000に揃えて比較)

```diff
--- RULE_BLOCK_EN (v2, threshold=12,000)
+++ RULE_BLOCK_EN (strict, threshold=12,000)
@@ -1,21 +1,15 @@
-Candidate difficulty rule (draft, under evaluation):
+Candidate difficulty rule (STRICT definitions, user-confirmed 2026-09-26):
 
-Words that rank below roughly the top 12,000 most frequent general English words are, in principle, candidates for simplification. This is NOT a mechanical ban list. As with the existing Standard-level vocabulary policy, simplification should be strongly preferred only when a simpler, natural expression exists without harming meaning or naturalness; it must not be forced when it would.
+Words that rank below roughly the top 12,000 most frequent general English words are, in principle, candidates for simplification. This is NOT a mechanical ban list: simplification must not be a forced, automatic replacement, but whenever a simpler and more natural expression exists without harming meaning, simplification should be strongly preferred. The definitions of exceptions B, C, and D below are identical for both the Standard and the Advanced level; only the threshold number differs between levels.
 
-A word ranked beyond ~12,000 may still be KEPT (not simplified) if one of these applies:
-A. Its meaning can easily be guessed from an already-easy word it is built from (for example: "onstage" = on + stage, "wastewater" = waste + water, "understandable" = understand + -able). Do not exclude a word just because it LOOKS decomposable if the meaning cannot actually be guessed that way.
-B. It is a word that has become well established in Japanese, and its meaning can easily be guessed from its English pronunciation (for example: piano, curtain, privacy). Simply having a katakana spelling is not enough -- the word must be an established, commonly understood Japanese word, easily connected to its English sound.
-C. It is a proper noun (a person's name, a company or product name, a place name).
-D. Replacing it with an easier word would clearly hurt meaning precision or the naturalness of the English -- it is indispensable. Do not keep a word only because "it is a technical term" -- if a simple, natural, meaning-preserving substitute exists, simplify it.
+A word ranked beyond ~12,000 may still be KEPT (not simplified) only if one of these STRICT conditions applies. Treat B, C, and D narrowly: each is a strict exception, not a convenient escape hatch.
 
-Words that appear inside quotation marks in the article, and titles, designations, or nicknames that a specific person or organization is reported to have actually used (for example, if the article states that Meta called certain workers "human concierges", the word "concierges" here is part of that reported fact, not an ordinary vocabulary choice) are facts of the article. Do not simplify such a word even if it appears in the candidate list below; treat it under exception C (a proper noun / quoted designation) and mark it "KEEP -- proper noun", explaining in reasoning that it is a quoted designation that must be kept exactly as reported.
+A (KEEP -- predictable morphology/compound). The word is a form or compound built from an already-easy, already-known word or word part, such that an English learner can naturally guess its meaning from that structure (for example: "onstage" = on + stage, "wastewater" = waste + water, "understandable" = understand + -able). Being decomposable into morphemes is NOT enough by itself to KEEP a word; the learner must actually be able to guess the meaning that way.
 
-Do NOT use "it is part of a fixed expression / idiom" as its own exception category. (For example, if "curtain" in "behind the curtain" is kept, the reason must be B [established Japanese loanword], never "it is part of an idiom.") A word inside a fixed expression that is still hard to guess should be judged normally, exactly like any other word.
+B (KEEP -- established Japanese loanword, STRICT). It is NOT enough that the word happens to be used in Japanese somewhere. This is B only when, on seeing or hearing this English word's form and pronunciation, a Japanese English learner naturally and almost unambiguously connects it to a word they already know in Japanese, and understands its meaning with little doubt. Do NOT use reason B when any of the following is true: the correspondence between the English word-form and the Japanese loanword is hard to recognize; the word is established in Japanese only within a narrow specialist/technical field, not in everyday Japanese; the word is hard to understand when it is actually read here in this English sentence, even though a loanword exists; or the only support you can offer is that "a katakana spelling of this word exists." In particular, re-judge the words "leak", "pause", and "curtain" carefully against this strict standard rather than assuming that a katakana form is automatically enough.
 
-For each candidate word listed below, decide:
-- "KEEP -- predictable morphology/compound" (reason A)
-- "KEEP -- established Japanese loanword" (reason B)
-- "KEEP -- proper noun" (reason C)
-- "KEEP -- indispensable / natural replacement unavailable" (reason D)
-- "SIMPLIFY" (replace it with a simpler, natural word or phrase)
-- "BORDERLINE" (only if you are genuinely unsure; explain why in notes_on_ambiguous_cases)
+C (KEEP -- proper noun / genuine quoted designation, STRICT). Use this ONLY for a genuine proper noun or an official/specific quoted designation: a real person's name, a real place name, a real organization's name, a specific product or service name, an official name, or a specific quoted designation that is itself reported as a fact of the article (for example, if the article reports that Meta actually called certain workers "human concierges", the phrase "human concierges" is that reported fact and must be kept exactly). Do NOT use reason C when any of the following is true: the word is simply a common noun that happens to appear inside quotation marks in the article; it is an ordinary general or technical term, even if quoted; it is merely quoted somewhere in the article (for example, quoting how a news report phrased something) without being a specific person's or organization's own name or designation; or the writer added quotation marks only for emphasis or to introduce a term to the reader. A common, general technical term is never C merely because it appears inside quotation marks.
+
+D (KEEP -- indispensable / natural replacement unavailable, STRICT). KEEP under D ONLY when replacing the word with an easier, natural word or expression would clearly and demonstrably break the article's core meaning, factual precision, or a nuance that a reader actually needs in order to understand the point. Do NOT use reason D merely because: the word is a technical term; it was the word used in the source article; it works reasonably well as part of a metaphor or storytelling image; you (the model) like it as a stylistic choice; or replacing it would only slightly change the mood or flavor of the sentence. If a simpler, natural, meaning-preserving word or phrase is available, SIMPLIFY is strongly preferred over D. In particular, re-evaluate the words "artery", "sewer"/"sewers", "flush", and "septic" carefully against this strict standard; keep them under D only if you can demonstrate that a simpler alternative would truly break meaning, factual precision, or a nuance the reader needs -- not merely because they are the precise technical term or part of a metaphor.
+
+Do NOT use "it is part of a fixed expression / idiom" as its own exception category. A word inside a fixed expression that is still hard to guess should be judged normally under A/B/C/D above, exactly like any other word.
```
