# prompt_band_template.md

NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01

共通テンプレート(3条件でBand数値のみ差異。他の文言は一字一句同一であることをコードでassert済み: `_assert_template_band_only_diff()`)。

DEVELOPER message:

```text
You are an editor who rewrites English feature articles so that their vocabulary stays within a specific word-frequency band, while keeping the article's facts, storyline, and enjoyment intact.
```

## テンプレート全文(`{band}`/`{advanced_article}`はプレースホルダのまま)

```text
Rewrite this entire article using, as a firm principle, only words within roughly the top {band:,} most common English words.

Do not first write a hard word and then swap out only that one word afterward. Instead, from the first draft, build the whole sentence around words within this band so the full meaning is expressed naturally from the start.

The following are the only three kinds of words allowed to fall outside the top {band:,} words:
(1) A true proper noun: a person's name, a place name, an organization's name, a product or service name, or an official title (for example: Meta, Muse, Reuters).
(2) A derived or compound word whose meaning a learner can easily guess from a simpler word they already know, through a clear prefix, suffix, or a transparent compound (for example: wastewater = waste + water; surprisingly = surprise + -ingly). Do not use this exception for a word that can be split into parts but whose meaning is not easy to predict from those parts.
(3) A word that is a common loanword already established in Japanese, one that a Japanese learner of English would naturally connect to its meaning just from its English form (for example: piano, curtain). Do not use this exception just because a katakana spelling exists for the word; a technical or specialist term, or a word whose English form and Japanese pronunciation do not clearly match each other, is not covered by this exception.

Do not sort each word into a fixed exception category, and do not list or output any candidate words or a classification for each word. Output only the article itself.

Keep every fact exactly as it is: the same actions, cause and effect, who did what, who or what it happened to, quantities, points in time, and the same storyline and central details. Do not turn the article into a summary and do not remove an interesting detail.

Some loss of naturalness is acceptable in service of the vocabulary band above. However, the result must not become grammatically broken, must not change the meaning, must not become too unnatural to use as learning material, must not turn into a pile of clumsy explanatory phrases, and must not repeat the same simple word or phrase in an unnatural way.

Keep the same Markdown structure (the "# " title, the two "### " sections, and the final "## In one line" section); do not add or remove sections.

Output only the English title and the English body.

[Article]
{advanced_article}
```

## Band別 sha256(advanced_articleプレースホルダは`{advanced_article}`のまま計算)

- band=6000: sha256=941b3dfe3ee556f4ee28be0ea1b25561cc27cb2205fc2ceb0d0b6750c9065470
- band=10000: sha256=f04529d27d291708cf6fac6b61eeb547abbbac3048adf2298407888addaf0059
- band=14000: sha256=703c6345c045b4cac0b9d6ab953b1203a1ca1cd2af47eeb6726659def5d05602
