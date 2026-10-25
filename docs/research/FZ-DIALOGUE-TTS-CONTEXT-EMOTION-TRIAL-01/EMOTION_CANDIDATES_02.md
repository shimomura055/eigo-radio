# EMOTION_CANDIDATES_02 — 追加2作品の感情情報(Fableレビュー用。TTS前に各作品の emotion_review.json へ accept / discard)

## 作品: 開いた窓(The Open Window) / work key `open_window`

## open_window — 感情情報8件(Fableレビュー用。TTS前に accept / discard を `er118_output/fz_dialogue_context_tts_trial_02/open_window/llm/emotion_review.json` へ)

- LLM: 要求 `gpt-6-luna` / 返却 `gpt-6-luna`、1 call、実費 0.095 円(raw_usage_log.jsonl)。EMOTION_DEVELOPER+schema sha256 = `c239930fe6be06508df3de7cc619c2ef37439fe88a185172f658e66aa61f27ba`。
- 決定論検査の結果: ACCEPTED 6 / NO_EXPLICIT_CUE 2 / DISCARDED 0。
- NO_EXPLICIT_CUE(LLMが has_explicit_cue=false)の行は、Opus M2により『Speaker's state of mind』行を出さない(sceneとreactionは保持)。DISCARDEDは状態・場面・返答すべて出さない。
- 決定論検査: 根拠引用の逐語一致 / 語数 / 新規固有名詞 / 強度語deny(語幹)。根拠の出どころ(本人の台詞・地の文・他者の台詞)は目視補助。

### 1. `full_story_part1_c7` — Vera(Voice Zephyr) / 不安・緊張 / 静かな告白

- セリフ(英): "Her great tragedy happened three years ago today."
- 場面(日本語・選定時): 客のFramtonに、Veraが叔母の『悲劇』を切り出す場面。Veraは開け放たれたフランス窓を見やってから話し始める。
- 前のセリフ: Vera: Do you know much about her? / Framton: Almost nothing,
- 後のセリフ: Vera: Her husband and her two young brothers went out shooting through that window. Their little brown spaniel went with them. They tried to cross a bog, but the ground gave way beneath them. They all disappeared. Their bodies were never found.
- 直前の地の文: he admitted. Vera glanced towards the French window, which stood wide open to the lawn.
- 直後の地の文: Framton stopped turning the letter.
- 決定論の manner_words: stopped

**LLM出力**(status = `NO_EXPLICIT_CUE`)
- speaker_state: Vera is matter-of-factly explaining the tragedy. Her glance toward the open window connects the story to the room.
- scene: Vera speaks in the room after Framton says he knows almost nothing about her aunt.
- reaction_to_previous: She answers Framton's admission that he knows almost nothing about her aunt.
- 根拠引用(出どころ):
  - 「"Almost nothing,"」 — 他者の台詞
  - 「Vera glanced towards the French window, which stood wide open to the lawn.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Vera.
Scene: Vera speaks in the room after Framton says he knows almost nothing about her aunt.
Spoken line before (said by Vera; not part of this line): Do you know much about her?
Spoken line before (said by Framton; not part of this line): Almost nothing,
Narration just before: "Vera glanced towards the French window, which stood wide open to the lawn."
Spoken line after (said by Vera; not part of this line): Her husband and her two young brothers went out shooting through that window. Their little brown spaniel went with them. They tried to cross a bog, but the ground gave way beneath them. They all disappeared. Their bodies were never found.
Narration just after: "Framton stopped turning the letter."
Manner words from the narration: stopped
How this line answers the previous one: She answers Framton's admission that he knows almost nothing about her aunt.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 2. `full_story_part1_c10` — Framton(Voice Algieba) / 驚き・同情 / ささやき・静かな発言

- セリフ(英): "How terrible,"
- 場面(日本語・選定時): 窓の外へ出て行方不明になった叔母の家族の話を聞き、Framtonが小声で『なんと恐ろしい』とつぶやく場面(地の文に『murmured』)。
- 前のセリフ: Vera: Her great tragedy happened three years ago today. / Vera: Her husband and her two young brothers went out shooting through that window. Their little brown spaniel went with them. They tried to cross a bog, but the ground gave way beneath them. They all disappeared. Their bodies were never found.
- 後のセリフ: Vera: My aunt still thinks they'll come back. She keeps the window open until dark, waiting for them.
- 直前の地の文: なし
- 直後の地の文: Framton murmured.
- 決定論の manner_words: なし

**LLM出力**(status = `ACCEPTED`)
- speaker_state: Framton expresses sympathy for the loss Vera has described.
- scene: Framton responds in the room after hearing Vera's account of the tragedy.
- reaction_to_previous: He reacts to Vera's account of the family disappearing and their bodies never being found.
- 根拠引用(出どころ):
  - 「"They all disappeared. Their bodies were never found."」 — 他者の台詞
  - 「Framton murmured.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Framton.
Speaker's state of mind: Framton expresses sympathy for the loss Vera has described.
Scene: Framton responds in the room after hearing Vera's account of the tragedy.
Spoken line before (said by Vera; not part of this line): Her great tragedy happened three years ago today.
Spoken line before (said by Vera; not part of this line): Her husband and her two young brothers went out shooting through that window. Their little brown spaniel went with them. They tried to cross a bog, but the ground gave way beneath them. They all disappeared. Their bodies were never found.
Spoken line after (said by Vera; not part of this line): My aunt still thinks they'll come back. She keeps the window open until dark, waiting for them.
Narration just after: "Framton murmured."
How this line answers the previous one: He reacts to Vera's account of the family disappearing and their bodies never being found.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 3. `full_story_part1_c12` — Vera(Voice Zephyr) / 不気味さ・悲しみ / 静かな語り

- セリフ(英): "My aunt still thinks they'll come back. She keeps the window open until dark, waiting for them."
- 場面(日本語・選定時): Framtonがつぶやいた後、Veraが『叔母は今もみんなが帰ってくると思っていて、暗くなるまで窓を開けて待っている』と静かに続ける場面(直後の地の文に『Vera's voice grew quieter』)。
- 前のセリフ: Vera: Her husband and her two young brothers went out shooting through that window. Their little brown spaniel went with them. They tried to cross a bog, but the ground gave way beneath them. They all disappeared. Their bodies were never found. / Framton: How terrible,
- 後のセリフ: Vera: Her husband had his white coat over his arm. Her youngest brother was singing, 'Bertie, why do you bound?' He always sang it to tease her.
- 直前の地の文: Framton murmured.
- 直後の地の文: Vera's voice grew quieter.
- 決定論の manner_words: なし

**LLM出力**(status = `ACCEPTED`)
- speaker_state: Vera speaks quietly about her aunt's continued expectation that the family will return.
- scene: Vera speaks in the room after Framton expresses sympathy for the tragedy.
- reaction_to_previous: She adds that her aunt still waits for the family to return.
- 根拠引用(出どころ):
  - 「"My aunt still thinks they'll come back."」 — 本人の台詞
  - 「Vera's voice grew quieter.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Vera.
Speaker's state of mind: Vera speaks quietly about her aunt's continued expectation that the family will return.
Scene: Vera speaks in the room after Framton expresses sympathy for the tragedy.
Spoken line before (said by Vera; not part of this line): Her husband and her two young brothers went out shooting through that window. Their little brown spaniel went with them. They tried to cross a bog, but the ground gave way beneath them. They all disappeared. Their bodies were never found.
Spoken line before (said by Framton; not part of this line): How terrible,
Narration just before: "Framton murmured."
Spoken line after (said by Vera; not part of this line): Her husband had his white coat over his arm. Her youngest brother was singing, 'Bertie, why do you bound?' He always sang it to tease her.
Narration just after: "Vera's voice grew quieter."
How this line answers the previous one: She adds that her aunt still waits for the family to return.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 4. `full_story_part2_c4` — Vera's aunt(Voice Kore) / 喜び・驚き / 感情が変化する場面

- セリフ(英): "I hope Vera has kept you company! You don't mind the open window? My husband and brothers will be back soon. They've been shooting. Their boots will be covered in mud, of course!"
- 場面(日本語・選定時): 叔母が急いで部屋に入ってきて、Framtonに話しかけ、開けた窓のこと、もうすぐ帰る夫と弟たちのことをにこやかに話す場面(直前の地の文に『hurried into the room』)。
- 前のセリフ: Vera: Her husband had his white coat over his arm. Her youngest brother was singing, 'Bertie, why do you bound?' He always sang it to tease her. / Vera: Sometimes, on evenings like this, I almost expect to see them.
- 後のセリフ: なし
- 直前の地の文: Before Framton could reply, her aunt hurried into the room.
- 直後の地の文: Framton felt a chill. So she really was waiting.
- 決定論の manner_words: hurried

**LLM出力**(status = `ACCEPTED`)
- speaker_state: The aunt sounds welcoming and speaks as though her husband and brothers will return soon.
- scene: The aunt enters the room while Framton is with Vera and speaks before he can reply.
- reaction_to_previous: She follows Vera's account of expecting to see them by speaking as if they are about to return.
- 根拠引用(出どころ):
  - 「"You don't mind the open window?"」 — 本人の台詞
  - 「"My husband and brothers will be back soon."」 — 本人の台詞
  - 「Before Framton could reply, her aunt hurried into the room.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Vera's aunt.
Speaker's state of mind: The aunt sounds welcoming and speaks as though her husband and brothers will return soon.
Scene: The aunt enters the room while Framton is with Vera and speaks before he can reply.
Spoken line before (said by Vera; not part of this line): Her husband had his white coat over his arm. Her youngest brother was singing, 'Bertie, why do you bound?' He always sang it to tease her.
Spoken line before (said by Vera; not part of this line): Sometimes, on evenings like this, I almost expect to see them.
Narration just before: "Before Framton could reply, her aunt hurried into the room."
Narration just after: "Framton felt a chill. So she really was waiting."
Manner words from the narration: hurried
How this line answers the previous one: She follows Vera's account of expecting to see them by speaking as if they are about to return.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 5. `full_story_part2_c6` — Vera's aunt(Voice Kore) / 喜び・驚き

- セリフ(英): "Here they are at last!"
- 場面(日本語・選定時): 窓の外を気にしていた叔母の顔がぱっと明るくなり、『やっと帰ってきた』と声を上げる場面(直前の地の文に『her face brightened』)。
- 前のセリフ: なし
- 後のセリフ: なし
- 直前の地の文: Again and again, she looked past him towards the lawn. Then her face brightened.
- 直後の地の文: Vera stared outside, her eyes wide with horror. Framton turned.
- 決定論の manner_words: stared

**LLM出力**(status = `ACCEPTED`)
- speaker_state: The aunt appears pleased to see the returning men.
- scene: The aunt looks toward the lawn and announces that the men have arrived.
- reaction_to_previous: (空)
- 根拠引用(出どころ):
  - 「Then her face brightened.」 — 地の文
  - 「"Here they are at last!"」 — 本人の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Vera's aunt.
Speaker's state of mind: The aunt appears pleased to see the returning men.
Scene: The aunt looks toward the lawn and announces that the men have arrived.
Narration just before: "Again and again, she looked past him towards the lawn. Then her face brightened."
Narration just after: "Vera stared outside, her eyes wide with horror. Framton turned."
Manner words from the narration: stared
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 6. `full_story_part3_c8` — Vera's aunt(Voice Kore) / 戸惑い / 日常の会話(対照)

- セリフ(英): "He talked about his nerves, then suddenly ran away."
- 場面(日本語・選定時): 逃げるように帰った客のことを、叔母が帰宅した家族に『神経の話をしたかと思ったら急に走って行った』と何気なく話す場面。
- 前のセリフ: one of the returning men: Who was that? / Vera's aunt: A most peculiar visitor,
- 後のセリフ: Vera: It was the spaniel,
- 直前の地の文: his wife said.
- 直後の地の文: なし
- 決定論の manner_words: なし

**LLM出力**(status = `NO_EXPLICIT_CUE`)
- speaker_state: The aunt matter-of-factly describes the visitor's sudden departure.
- scene: After a returning man asks who the visitor was, the aunt answers him.
- reaction_to_previous: She answers the man's question about the visitor.
- 根拠引用(出どころ):
  - 「"Who was that?"」 — 他者の台詞
  - 「"A most peculiar visitor,"」 — 他者の台詞
  - 「"He talked about his nerves, then suddenly ran away."」 — 本人の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Vera's aunt.
Scene: After a returning man asks who the visitor was, the aunt answers him.
Spoken line before (said by one of the returning men; not part of this line): Who was that?
Spoken line before (said by Vera's aunt; not part of this line): A most peculiar visitor,
Spoken line after (said by Vera; not part of this line): It was the spaniel,
How this line answers the previous one: She answers the man's question about the visitor.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 7. `full_story_part3_c9` — Vera(Voice Zephyr) / 落ち着いた嘘 / 相手の発言を受けた返答

- セリフ(英): "It was the spaniel,"
- 場面(日本語・選定時): 客が逃げた理由を問われ、Veraが落ち着いて『犬のせい』と答える場面(直後の地の文に『Vera said calmly』)。
- 前のセリフ: Vera's aunt: A most peculiar visitor, / Vera's aunt: He talked about his nerves, then suddenly ran away.
- 後のセリフ: Vera: He told me he was terrified of dogs. In India, a pack chased him into an empty grave. He spent the whole night there, with them snarling above him.
- 直前の地の文: なし
- 直後の地の文: Vera said calmly.
- 決定論の manner_words: なし

**LLM出力**(status = `ACCEPTED`)
- speaker_state: Vera speaks calmly as she offers an explanation about the spaniel.
- scene: Vera speaks after her aunt describes the visitor running away.
- reaction_to_previous: She supplies an explanation for the visitor's sudden departure.
- 根拠引用(出どころ):
  - 「"He talked about his nerves, then suddenly ran away."」 — 他者の台詞
  - 「Vera said calmly.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Vera.
Speaker's state of mind: Vera speaks calmly as she offers an explanation about the spaniel.
Scene: Vera speaks after her aunt describes the visitor running away.
Spoken line before (said by Vera's aunt; not part of this line): A most peculiar visitor,
Spoken line before (said by Vera's aunt; not part of this line): He talked about his nerves, then suddenly ran away.
Spoken line after (said by Vera; not part of this line): He told me he was terrified of dogs. In India, a pack chased him into an empty grave. He spent the whole night there, with them snarling above him.
Narration just after: "Vera said calmly."
How this line answers the previous one: She supplies an explanation for the visitor's sudden departure.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 8. `full_story_part3_c11` — Vera(Voice Zephyr) / 落ち着いた嘘 / 作り話の語り

- セリフ(英): "He told me he was terrified of dogs. In India, a pack chased him into an empty grave. He spent the whole night there, with them snarling above him."
- 場面(日本語・選定時): 逃げた客について、Veraが落ち着いたまま、インドで犬の群れに追われ墓穴で一晩過ごしたという作り話をすらすらと語る場面(直前の地の文に『Vera said calmly』、直後の地の文でそれが作り話だと明かされる)。
- 前のセリフ: Vera's aunt: He talked about his nerves, then suddenly ran away. / Vera: It was the spaniel,
- 後のセリフ: なし
- 直前の地の文: Vera said calmly.
- 直後の地の文: Inventing convincing stories at a moment's notice was Vera's speciality.
- 決定論の manner_words: なし

**LLM出力**(status = `ACCEPTED`)
- speaker_state: Vera calmly gives an account of Framton's fear of dogs and a past encounter.
- scene: Vera speaks after saying the spaniel explains the visitor's departure.
- reaction_to_previous: She expands on her explanation by describing his fear of dogs.
- 根拠引用(出どころ):
  - 「"It was the spaniel,"」 — 他者の台詞
  - 「Vera said calmly.」 — 地の文
  - 「Inventing convincing stories at a moment's notice was Vera's speciality.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Vera.
Speaker's state of mind: Vera calmly gives an account of Framton's fear of dogs and a past encounter.
Scene: Vera speaks after saying the spaniel explains the visitor's departure.
Spoken line before (said by Vera's aunt; not part of this line): He talked about his nerves, then suddenly ran away.
Spoken line before (said by Vera; not part of this line): It was the spaniel,
Narration just before: "Vera said calmly."
Narration just after: "Inventing convincing stories at a moment's notice was Vera's speciality."
How this line answers the previous one: She expands on her explanation by describing his fear of dogs.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### レビューの付け方

`er118_output/fz_dialogue_context_tts_trial_02/open_window/llm/emotion_review.json` の各 `fable_decision` を `accept` か `discard` にする。discardはLLM由来の項目(状態・場面・返答)を全て外して中立にする。`summary_ja` は試聴ページ用の日本語要約(Sonnet下書き入り。accept時のみ表示)。全8件が埋まるまで ctx arm の有料生成は起動しない。

## 作品: 猿の手(The Monkey's Paw) / work key `monkeys_paw`

## monkeys_paw — 感情情報8件(Fableレビュー用。TTS前に accept / discard を `er118_output/fz_dialogue_context_tts_trial_02/monkeys_paw/llm/emotion_review.json` へ)

- LLM: 要求 `gpt-6-luna` / 返却 `gpt-6-luna`、1 call、実費 0.0988 円(raw_usage_log.jsonl)。EMOTION_DEVELOPER+schema sha256 = `7e845a3bfb653f04e6f7ef5f5ca21e0f2357a7a38e42624362d5a6c7792d3e35`。
- 決定論検査の結果: ACCEPTED 6 / NO_EXPLICIT_CUE 1 / DISCARDED 1。
- NO_EXPLICIT_CUE(LLMが has_explicit_cue=false)の行は、Opus M2により『Speaker's state of mind』行を出さない(sceneとreactionは保持)。DISCARDEDは状態・場面・返答すべて出さない。
- 決定論検査: 根拠引用の逐語一致 / 語数 / 新規固有名詞 / 強度語deny(語幹)。根拠の出どころ(本人の台詞・地の文・他者の台詞)は目視補助。

### 1. `full_story_part1_c4` — the retired sergeant-major(Voice Algieba) / 不吉な警告 / 静かな語り

- セリフ(英): "but brings sorrow to anyone who interferes with fate."
- 場面(日本語・選定時): 元軍曹が暖炉のそばで猿の手の由来を語り、『運命に手を出す者には悲しみをもたらす』と続ける場面。
- 前のセリフ: the retired sergeant-major: It grants three wishes,
- 後のセリフ: Mr. White: Have you used it?
- 直前の地の文: he said,
- 直後の地の文: なし
- 決定論の manner_words: なし

**LLM出力**(status = `ACCEPTED`)
- speaker_state: He is warning that the paw brings sorrow to those who interfere with fate.
- scene: He explains the paw's danger after saying that it grants three wishes.
- reaction_to_previous: He adds a warning to his claim that the paw grants three wishes.
- 根拠引用(出どころ):
  - 「"It grants three wishes,"」 — 他者の台詞
  - 「"but brings sorrow to anyone who interferes with fate."」 — 本人の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: the retired sergeant-major.
Speaker's state of mind: He is warning that the paw brings sorrow to those who interfere with fate.
Scene: He explains the paw's danger after saying that it grants three wishes.
Spoken line before (said by the retired sergeant-major; not part of this line): It grants three wishes,
Spoken line after (said by Mr. White; not part of this line): Have you used it?
How this line answers the previous one: He adds a warning to his claim that the paw grants three wishes.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 2. `full_story_part1_c13` — Herbert(Voice Fenrir) / 喜び / 冗談めかした提案

- セリフ(英): "Ask for two hundred pounds, Father. Enough to pay off the house!"
- 場面(日本語・選定時): 訪問者が帰ったあと、Herbertが笑いながら、父に『200ポンドを願って家のローンを払おう』と促す場面(直前の地の文に『Herbert laughed』)。
- 前のセリフ: the retired sergeant-major: Burn it, / the retired sergeant-major: And don't blame me if you keep it.
- 後のセリフ: Mr. White: I wish for two hundred pounds.
- 直前の地の文: After their visitor left, Herbert laughed.
- 直後の地の文: Mr. White raised the paw with a smile.
- 決定論の manner_words: laughed, smile

**LLM出力**(status = `ACCEPTED`)
- speaker_state: Herbert is amused and encouraging his father to make a wish.
- scene: After their visitor leaves, Herbert speaks as Mr. White raises the paw.
- reaction_to_previous: He counters the sergeant-major's warning to burn the paw by urging his father to wish for money.
- 根拠引用(出どころ):
  - 「After their visitor left, Herbert laughed.」 — 地の文
  - 「"Burn it,"」 — 他者の台詞
  - 「"Ask for two hundred pounds, Father. Enough to pay off the house!"」 — 本人の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Herbert.
Speaker's state of mind: Herbert is amused and encouraging his father to make a wish.
Scene: After their visitor leaves, Herbert speaks as Mr. White raises the paw.
Spoken line before (said by the retired sergeant-major; not part of this line): Burn it,
Spoken line before (said by the retired sergeant-major; not part of this line): And don't blame me if you keep it.
Narration just before: "After their visitor left, Herbert laughed."
Spoken line after (said by Mr. White; not part of this line): I wish for two hundred pounds.
Narration just after: "Mr. White raised the paw with a smile."
Manner words from the narration: laughed, smile
How this line answers the previous one: He counters the sergeant-major's warning to burn the paw by urging his father to wish for money.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 3. `full_story_part1_c15` — Mr. White(Voice Schedar) / 期待と半信半疑 / 願い事

- セリフ(英): "I wish for two hundred pounds."
- 場面(日本語・選定時): Mr. Whiteが微笑みながら猿の手を掲げ、『200ポンドが欲しい』と願う場面(直前の地の文に『with a smile』、直後に手がねじれて叫ぶ)。
- 前のセリフ: the retired sergeant-major: And don't blame me if you keep it. / Herbert: Ask for two hundred pounds, Father. Enough to pay off the house!
- 後のセリフ: なし
- 直前の地の文: Mr. White raised the paw with a smile.
- 直後の地の文: It twisted in his hand. He cried out and dropped it.
- 決定論の manner_words: cried, smile

**LLM出力**(status = `ACCEPTED`)
- speaker_state: Mr. White is willing to make the wish, with a smile noted in the narration.
- scene: At home, he makes a wish while holding the paw.
- reaction_to_previous: He follows Herbert's suggestion to wish for two hundred pounds.
- 根拠引用(出どころ):
  - 「"Ask for two hundred pounds, Father. Enough to pay off the house!"」 — 他者の台詞
  - 「Mr. White raised the paw with a smile.」 — 地の文
  - 「"I wish for two hundred pounds."」 — 本人の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Mr. White.
Speaker's state of mind: Mr. White is willing to make the wish, with a smile noted in the narration.
Scene: At home, he makes a wish while holding the paw.
Spoken line before (said by the retired sergeant-major; not part of this line): And don't blame me if you keep it.
Spoken line before (said by Herbert; not part of this line): Ask for two hundred pounds, Father. Enough to pay off the house!
Narration just before: "Mr. White raised the paw with a smile."
Narration just after: "It twisted in his hand. He cried out and dropped it."
Manner words from the narration: cried, smile
How this line answers the previous one: He follows Herbert's suggestion to wish for two hundred pounds.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 4. `full_story_part2_c2` — the stranger from the firm(Voice Orus) / 悲しみ / 重い知らせ

- セリフ(英): "Your son was caught in the machinery,"
- 場面(日本語・選定時): 工場から来た見知らぬ男が、Whiteさん夫妻に息子の事故を切り出す場面。
- 前のセリフ: なし
- 後のセリフ: the stranger from the firm: He is dead.
- 直前の地の文: White cleared the table. Later, a stranger from the firm arrived.
- 直後の地の文: he said.
- 決定論の manner_words: なし

**LLM出力**(status = `NO_EXPLICIT_CUE`)
- speaker_state: The stranger from the firm is delivering news about the accident in a neutral manner.
- scene: Later, after Mr. White clears the table, the stranger from the firm tells the family what happened.
- reaction_to_previous: (空)
- 根拠引用(出どころ):
  - 「Your son was caught in the machinery,」 — 本人の台詞
  - 「A stranger from the firm arrived.」 — 地の文
  - 「he said.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: the stranger from the firm.
Scene: Later, after Mr. White clears the table, the stranger from the firm tells the family what happened.
Narration just before: "White cleared the table. Later, a stranger from the firm arrived."
Spoken line after (said by the stranger from the firm; not part of this line): He is dead.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 5. `full_story_part2_c6` — the stranger from the firm(Voice Orus) / 事務的な発言(対照)

- セリフ(英): "The firm accepts no responsibility, but offers you two hundred pounds in compensation."
- 場面(日本語・選定時): 息子の死を告げたあと、会社は責任を負わないが見舞金として200ポンドを出すと、男が事務的に伝える場面。
- 前のセリフ: the stranger from the firm: Your son was caught in the machinery, / the stranger from the firm: He is dead.
- 後のセリフ: Mrs. White: The paw! We have two wishes left. Wish him alive again!
- 直前の地の文: Mr. White reached for his wife's hand.
- 直後の地の文: Mr. White fell from his chair.
- 決定論の manner_words: なし

**LLM出力**(status = `DISCARDED`、破棄理由 ['new_proper_noun:scene:Whites'])
- speaker_state: The stranger from the firm is explaining the firm's position and offering compensation.
- scene: He speaks to the Whites after telling them their son died.
- reaction_to_previous: He follows the news of the death by stating the firm's position and its offer.
- 根拠引用(出どころ):
  - 「"Your son was caught in the machinery,"」 — 他者の台詞
  - 「"He is dead."」 — 他者の台詞
  - 「"The firm accepts no responsibility, but offers you two hundred pounds in compensation."」 — 本人の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: the stranger from the firm.
Spoken line before (said by the stranger from the firm; not part of this line): Your son was caught in the machinery,
Spoken line before (said by the stranger from the firm; not part of this line): He is dead.
Narration just before: "Mr. White reached for his wife's hand."
Spoken line after (said by Mrs. White; not part of this line): The paw! We have two wishes left. Wish him alive again!
Narration just after: "Mr. White fell from his chair."
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 6. `full_story_part2_c8` — Mrs. White(Voice Zephyr) / 悲しみ / 必死の頼み / 感情が変化する場面

- セリフ(英): "The paw! We have two wishes left. Wish him alive again!"
- 場面(日本語・選定時): 埋葬の1週間後、涙で顔を濡らしたMrs. Whiteが夫を揺り起こし、猿の手に残った願いで息子を生き返らせてと迫る場面(直前の地の文に『Her face was wet with tears』)。
- 前のセリフ: the stranger from the firm: He is dead. / the stranger from the firm: The firm accepts no responsibility, but offers you two hundred pounds in compensation.
- 後のセリフ: Mr. White: You didn't see him. I'm afraid of what might come back.
- 直前の地の文: White shook her husband awake. Her face was wet with tears.
- 直後の地の文: He turned away.
- 決定論の manner_words: tears

**LLM出力**(status = `ACCEPTED`)
- speaker_state: Mrs. White is distressed and urgently insists they use the paw to bring her son back.
- scene: After hearing the compensation offer, she speaks as she wakes her husband, her face wet with tears.
- reaction_to_previous: She responds to the compensation offer by insisting that they use the paw to wish their son alive again.
- 根拠引用(出どころ):
  - 「Her face was wet with tears.」 — 地の文
  - 「"The paw! We have two wishes left. Wish him alive again!"」 — 本人の台詞
  - 「"He is dead."」 — 他者の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Mrs. White.
Speaker's state of mind: Mrs. White is distressed and urgently insists they use the paw to bring her son back.
Scene: After hearing the compensation offer, she speaks as she wakes her husband, her face wet with tears.
Spoken line before (said by the stranger from the firm; not part of this line): He is dead.
Spoken line before (said by the stranger from the firm; not part of this line): The firm accepts no responsibility, but offers you two hundred pounds in compensation.
Narration just before: "White shook her husband awake. Her face was wet with tears."
Spoken line after (said by Mr. White; not part of this line): You didn't see him. I'm afraid of what might come back.
Narration just after: "He turned away."
Manner words from the narration: tears
How this line answers the previous one: She responds to the compensation offer by insisting that they use the paw to wish their son alive again.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 7. `full_story_part2_c10` — Mr. White(Voice Schedar) / 恐れ / ためらい

- セリフ(英): "You didn't see him. I'm afraid of what might come back."
- 場面(日本語・選定時): 夫が顔をそむけ、『お前は息子の姿を見ていない。何が戻ってくるのか怖い』と答える場面(直前の地の文に『He turned away』)。
- 前のセリフ: the stranger from the firm: The firm accepts no responsibility, but offers you two hundred pounds in compensation. / Mrs. White: The paw! We have two wishes left. Wish him alive again!
- 後のセリフ: Mrs. White: He's our son!
- 直前の地の文: He turned away.
- 直後の地の文: なし
- 決定論の manner_words: なし

**LLM出力**(status = `ACCEPTED`)
- speaker_state: Mr. White is afraid of what might return if they wish his son alive again.
- scene: After turning away, he answers his wife's demand to wish their son alive again.
- reaction_to_previous: He responds to her demand by warning that he fears the result of bringing their son back.
- 根拠引用(出どころ):
  - 「"The paw! We have two wishes left. Wish him alive again!"」 — 他者の台詞
  - 「He turned away.」 — 地の文
  - 「"You didn't see him. I'm afraid of what might come back."」 — 本人の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Mr. White.
Speaker's state of mind: Mr. White is afraid of what might return if they wish his son alive again.
Scene: After turning away, he answers his wife's demand to wish their son alive again.
Spoken line before (said by the stranger from the firm; not part of this line): The firm accepts no responsibility, but offers you two hundred pounds in compensation.
Spoken line before (said by Mrs. White; not part of this line): The paw! We have two wishes left. Wish him alive again!
Narration just before: "He turned away."
Spoken line after (said by Mrs. White; not part of this line): He's our son!
How this line answers the previous one: He responds to her demand by warning that he fears the result of bringing their son back.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### 8. `full_story_part3_c1` — Mr. White(Voice Schedar) / 恐れと決意 / 震え声

- セリフ(英): "I wish Herbert alive again."
- 場面(日本語・選定時): 階下で猿の手を見つけたMr. Whiteが、震える声で『息子を生き返らせてほしい』と最後に近い願いを口にする場面(直前の地の文に『His voice shook』)。
- 前のセリフ: Mr. White: You didn't see him. I'm afraid of what might come back. / Mrs. White: He's our son!
- 後のセリフ: Mrs. White: Herbert!
- 直前の地の文: His wife followed. His voice shook.
- 直後の地の文: It fell from his hand. They waited in the dark, listening to the clock.
- 決定論の manner_words: なし

**LLM出力**(status = `ACCEPTED`)
- speaker_state: Mr. White is apprehensive as he makes the wish; the narration says his voice shook.
- scene: In the dark, he makes the wish after his wife insists their son is still their son.
- reaction_to_previous: He makes the wish in response to his wife's insistence that their son be brought back.
- 根拠引用(出どころ):
  - 「"He's our son!"」 — 他者の台詞
  - 「His voice shook.」 — 地の文
  - 「"I wish Herbert alive again."」 — 本人の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Mr. White.
Speaker's state of mind: Mr. White is apprehensive as he makes the wish; the narration says his voice shook.
Scene: In the dark, he makes the wish after his wife insists their son is still their son.
Spoken line before (said by Mr. White; not part of this line): You didn't see him. I'm afraid of what might come back.
Spoken line before (said by Mrs. White; not part of this line): He's our son!
Narration just before: "His wife followed. His voice shook."
Spoken line after (said by Mrs. White; not part of this line): Herbert!
Narration just after: "It fell from his hand. They waited in the dark, listening to the clock."
How this line answers the previous one: He makes the wish in response to his wife's insistence that their son be brought back.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

### レビューの付け方

`er118_output/fz_dialogue_context_tts_trial_02/monkeys_paw/llm/emotion_review.json` の各 `fable_decision` を `accept` か `discard` にする。discardはLLM由来の項目(状態・場面・返答)を全て外して中立にする。`summary_ja` は試聴ページ用の日本語要約(Sonnet下書き入り。accept時のみ表示)。全8件が埋まるまで ctx arm の有料生成は起動しない。

