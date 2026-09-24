# prompt_diff_a1.md — A-1 Prompt Meta固有列挙 -> 下水道用列挙 置換差分

DEVELOPER / ARM3_BLOCK / COMMON_BLOCKの冒頭2文・末尾2文・全体構成は一字も変えていない。変更したのはCOMMON_BLOCK内の "Preserve the Japanese article's editorial angle, structure, and sense of surprise:" に続く6項目の箇条書きのみ。

## 置換前(Meta固有、NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 arm3 逐語)

```
Adapt the Japanese article below into English.

Do not rewrite the article from scratch. Do not add new ideas, claims, background, general observations, examples, or facts that are not in the Japanese article. Preserve the Japanese article's editorial angle, structure, and sense of surprise:
- the opening expectation of a convenient "AI makes the phone call" future;
- the reversal that a human was actually working behind the scenes;
- the framing of lead role / backstage / understudy;
- the theme fixed on "there was a human behind the AI phone call";
- privacy treated as necessary later information, not as the main theme;
- the ending that returns to the image of the stage and what is behind the curtain.
Keep every fact exactly as in the Japanese article. Use short, simple English that a learner could understand by listening once.

Output only the English title and the English body.
```

## 置換後(下水道用、本Trialで使用)

```
Adapt the Japanese article below into English.

Do not rewrite the article from scratch. Do not add new ideas, claims, background, general observations, examples, or facts that are not in the Japanese article. Preserve the Japanese article's editorial angle, structure, and sense of surprise:
- the opening expectation triggered by the word "merger," that towns or municipalities might be the ones merging;
- the reversal that it is not towns merging, but a household's own toilet, kitchen, and bath water that are being treated together, near the home;
- the framing of the sewer as the town's invisible main artery, versus the shift to small, household-level water treatment;
- the theme fixed on "you can protect convenience without making the system bigger, by moving water treatment closer to home";
- installation, inspection, and cleaning treated as necessary later information, not as the main theme;
- the ending that returns to the idea that the future of sewers may arrive in a surprisingly familiar, nearby place.
Keep every fact exactly as in the Japanese article. Use short, simple English that a learner could understand by listening once.

Output only the English title and the English body.
```

## 対応関係

| Meta(元) | 下水道(置換後) |
|---|---|
| opening expectation of "AI makes the phone call" | opening expectation triggered by the word "merger" (towns merging) |
| reversal: a human was working behind the scenes | reversal: it's not towns merging, but household toilet/kitchen/bath water treated together near the home |
| framing: lead role / backstage / understudy | framing: sewer as invisible main artery vs. small household-level treatment |
| theme: "a human behind the AI phone call" | theme: "protect convenience without making the system bigger, by moving treatment closer to home" |
| privacy as necessary later information | installation/inspection/cleaning as necessary later information |
| ending: stage / behind the curtain | ending: sewer's future may arrive in a surprisingly familiar, nearby place |
