# EMOTION_CANDIDATES_01 — 感情情報8件(Fableレビュー用。TTS前に accept / discard を `llm/emotion_review.json` へ)

- LLM: 要求 `gpt-6-luna` / 返却 `gpt-6-luna`、1 call、実費 0.0975 円(raw_usage_log.jsonl)。EMOTION_DEVELOPER+schema sha256 = `8bc8c816d5187ff060c438bce09b03e21492c7e44806241763631e55db291dce`。
- 決定論検査の結果: ACCEPTED 3 / NO_EXPLICIT_CUE 5 / DISCARDED 0。
- NO_EXPLICIT_CUE(LLMが has_explicit_cue=false)の行は、Opus M2により『Speaker's state of mind』行を出さない(sceneとreactionは保持)。DISCARDEDは状態・場面・返答すべて出さない。
- 決定論検査: 根拠引用の逐語一致 / 語数 / 新規固有名詞 / 強度語deny(語幹)。根拠の出どころ(本人の台詞・地の文・他者の台詞)は目視補助。

## 1. `full_story_part2_c2` — Della(Voice Zephyr) / 悲しみ・不安 / ためらい・戸惑い

- セリフ(英): "Will you buy my hair?"
- 場面(日本語・選定時): クリスマス前日。夫Jimへの贈り物を買うお金がなく、自慢の長い髪を売ろうと髪飾り店の前で息を整え、店の女主人に切り出す場面。
- 前のセリフ: なし
- 後のセリフ: the hair-shop owner: Twenty dollars.
- 直前の地の文: Outside a hair-goods shop, she paused just long enough to catch her breath.
- 直後の地の文: The owner lifted the heavy waves.
- 決定論の manner_words: breath, paused

**LLM出力**(status = `NO_EXPLICIT_CUE`)
- speaker_state: She is making a direct request; no specific emotion is stated.
- scene: Outside a hair-goods shop, she asks the owner if they will buy her hair.
- reaction_to_previous: (空)
- 根拠引用(出どころ):
  - 「"Will you buy my hair?"」 — 本人の台詞
  - 「Outside a hair-goods shop, she paused just long enough to catch her breath.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Scene: Outside a hair-goods shop, she asks the owner if they will buy her hair.
Narration just before: "Outside a hair-goods shop, she paused just long enough to catch her breath."
Spoken line after (said by the hair-shop owner; not part of this line): Twenty dollars.
Narration just after: "The owner lifted the heavy waves."
Manner words from the narration: breath, paused
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

## 2. `full_story_part2_c4` — the hair-shop owner(Voice Kore) / 相手の発言を受けた返答 / 感情を抑えた事務的な発言(対照)

- セリフ(英): "Twenty dollars."
- 場面(日本語・選定時): 女主人がDellaの豊かな髪を持ち上げ、買い取り額を告げる場面。
- 前のセリフ: Della: Will you buy my hair?
- 後のセリフ: Della: Cut it quickly, please.
- 直前の地の文: The owner lifted the heavy waves.
- 直後の地の文: なし
- 決定論の manner_words: なし

**LLM出力**(status = `NO_EXPLICIT_CUE`)
- speaker_state: The owner gives a direct, matter-of-fact offer; no specific emotion is stated.
- scene: At the hair-goods shop, the owner names the price after lifting Della’s hair.
- reaction_to_previous: The owner answers Della’s question about buying her hair with a price.
- 根拠引用(出どころ):
  - 「"Twenty dollars."」 — 本人の台詞
  - 「The owner lifted the heavy waves.」 — 地の文
  - 「"Will you buy my hair?"」 — 他者の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: the hair-shop owner.
Scene: At the hair-goods shop, the owner names the price after lifting Della’s hair.
Spoken line before (said by Della; not part of this line): Will you buy my hair?
Narration just before: "The owner lifted the heavy waves."
Spoken line after (said by Della; not part of this line): Cut it quickly, please.
How this line answers the previous one: The owner answers Della’s question about buying her hair with a price.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

## 3. `full_story_part2_c5` — Della(Voice Zephyr) / ためらい・戸惑い / 感情が変化する場面 / 相手の発言を受けた返答

- セリフ(英): "Cut it quickly, please."
- 場面(日本語・選定時): 金額を聞いたDellaが、迷う前に決めてしまおうと、すぐ切ってほしいと頼む場面。
- 前のセリフ: Della: Will you buy my hair? / the hair-shop owner: Twenty dollars.
- 後のセリフ: なし
- 直前の地の文: なし
- 直後の地の文: At the first touch of the scissors, Della shut her eyes. For two hours afterward, she hurried from shop to shop.
- 決定論の manner_words: hurried, shut her eyes

**LLM出力**(status = `NO_EXPLICIT_CUE`)
- speaker_state: She sounds ready to proceed, though no specific emotion is stated.
- scene: At the hair-goods shop, Della asks the owner to cut her hair after hearing the offer.
- reaction_to_previous: She accepts the offer by asking the owner to cut her hair.
- 根拠引用(出どころ):
  - 「"Cut it quickly, please."」 — 本人の台詞
  - 「"Twenty dollars."」 — 他者の台詞
  - 「At the first touch of the scissors, Della shut her eyes.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Scene: At the hair-goods shop, Della asks the owner to cut her hair after hearing the offer.
Spoken line before (said by Della; not part of this line): Will you buy my hair?
Spoken line before (said by the hair-shop owner; not part of this line): Twenty dollars.
Narration just after: "At the first touch of the scissors, Della shut her eyes. For two hours afterward, she hurried from shop to shop."
Manner words from the narration: hurried, shut her eyes
How this line answers the previous one: She accepts the offer by asking the owner to cut her hair.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

## 4. `full_story_part2_c7` — Della(Voice Zephyr) / ささやき・静かな発言 / 悲しみ・不安

- セリフ(英): "Please let him still think I'm pretty,"
- 場面(日本語・選定時): 髪を売って贈り物の鎖を買い、帰宅。短くなった髪を気にして鏡に戻りながら、Jimが帰る前に小さく祈る場面(直後の地の文に『ささやいた』)。
- 前のセリフ: なし
- 後のセリフ: Della: I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!
- 直前の地の文: By seven, dinner was nearly ready. Della had curled her short hair, but she kept returning to the mirror.
- 直後の地の文: she whispered.
- 決定論の manner_words: kept returning, whispered

**LLM出力**(status = `ACCEPTED`)
- speaker_state: She is a little worried about whether he will still find her pretty.
- scene: At home by the mirror, Della whispers to herself after curling her short hair.
- reaction_to_previous: (空)
- 根拠引用(出どころ):
  - 「"Please let him still think I'm pretty,"」 — 本人の台詞
  - 「Della had curled her short hair, but she kept returning to the mirror.」 — 地の文
  - 「she whispered.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Speaker's state of mind: She is a little worried about whether he will still find her pretty.
Scene: At home by the mirror, Della whispers to herself after curling her short hair.
Narration just before: "By seven, dinner was nearly ready. Della had curled her short hair, but she kept returning to the mirror."
Spoken line after (said by Della; not part of this line): I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!
Manner words from the narration: kept returning, whispered
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

## 5. `full_story_part3_c2` — Della(Voice Zephyr) / 感情が変化する場面 / 悲しみ・不安 / 喜び・驚き

- セリフ(英): "I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!"
- 場面(日本語・選定時): 帰ってきたJimが短い髪を見て立ち尽くす。Dellaは駆け寄り、髪を売った理由を打ち明ける場面。
- 前のセリフ: Della: Please let him still think I'm pretty,
- 後のセリフ: Della: My hair grows quickly.
- 直前の地の文: His eyes stayed on her hair. Della rushed toward him.
- 直後の地の文: He put his arms around her. Then he gave her a package.
- 決定論の manner_words: eyes stayed, rushed

**LLM出力**(status = `ACCEPTED`)
- speaker_state: She sounds eager to explain and reassure Jim about selling her hair.
- scene: After Jim looks at her hair, Della rushes toward him and explains why she sold it.
- reaction_to_previous: She follows her private worry about being thought pretty by explaining the sale and its purpose.
- 根拠引用(出どころ):
  - 「"I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!"」 — 本人の台詞
  - 「His eyes stayed on her hair. Della rushed toward him.」 — 地の文
  - 「"Please let him still think I'm pretty,"」 — 他者の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Speaker's state of mind: She sounds eager to explain and reassure Jim about selling her hair.
Scene: After Jim looks at her hair, Della rushes toward him and explains why she sold it.
Spoken line before (said by Della; not part of this line): Please let him still think I'm pretty,
Narration just before: "His eyes stayed on her hair. Della rushed toward him."
Spoken line after (said by Della; not part of this line): My hair grows quickly.
Narration just after: "He put his arms around her. Then he gave her a package."
Manner words from the narration: eyes stayed, rushed
How this line answers the previous one: She follows her private worry about being thought pretty by explaining the sale and its purpose.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

## 6. `full_story_part3_c4` — Della(Voice Zephyr) / 悲しみ・不安 / 喜び・驚き / 感情が変化する場面

- セリフ(英): "My hair grows quickly."
- 場面(日本語・選定時): Jimから贈られたのは、ずっと欲しかった櫛。髪を売った今は使えない櫛を胸に抱き、涙ながらに微笑んで言う場面(直前の地の文に『smiling through tears』)。
- 前のセリフ: Della: I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!
- 後のセリフ: Della: Look! Isn't it perfect? Give me your watch.
- 直前の地の文: Inside were the tortoise-shell combs she had so often admired in a shop window. She held them against her chest, smiling through tears.
- 直後の地の文: Suddenly remembering, she brought out the chain.
- 決定論の manner_words: smiling, suddenly, tears

**LLM出力**(status = `NO_EXPLICIT_CUE`)
- speaker_state: She is reassuring Jim that her hair will grow back.
- scene: After opening Jim’s package of combs, Della holds them against her chest and says her hair grows quickly.
- reaction_to_previous: She adds reassurance that her hair will grow quickly after explaining that she sold it.
- 根拠引用(出どころ):
  - 「"My hair grows quickly."」 — 本人の台詞
  - 「She held them against her chest, smiling through tears.」 — 地の文
  - 「"I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!"」 — 他者の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Scene: After opening Jim’s package of combs, Della holds them against her chest and says her hair grows quickly.
Spoken line before (said by Della; not part of this line): I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!
Narration just before: "Inside were the tortoise-shell combs she had so often admired in a shop window. She held them against her chest, smiling through tears."
Spoken line after (said by Della; not part of this line): Look! Isn't it perfect? Give me your watch.
Narration just after: "Suddenly remembering, she brought out the chain."
Manner words from the narration: smiling, suddenly, tears
How this line answers the previous one: She adds reassurance that her hair will grow quickly after explaining that she sold it.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

## 7. `full_story_part3_c6` — Della(Voice Zephyr) / 喜び・驚き

- セリフ(英): "Look! Isn't it perfect? Give me your watch."
- 場面(日本語・選定時): 気を取り直したDellaが、Jimのために買った時計の鎖を見せ、時計を貸してほしいと言う場面。
- 前のセリフ: Della: My hair grows quickly.
- 後のセリフ: Jim: I sold the watch to buy your combs.
- 直前の地の文: Suddenly remembering, she brought out the chain.
- 直後の地の文: Jim sat down and smiled gently.
- 決定論の manner_words: gently, smiled, suddenly

**LLM出力**(status = `ACCEPTED`)
- speaker_state: She sounds pleased with the chain and asks Jim to show her his watch.
- scene: At home, Della brings out the chain and shows it to Jim after receiving the combs.
- reaction_to_previous: She shifts from saying her hair will grow back to showing Jim the chain and asking for his watch.
- 根拠引用(出どころ):
  - 「"Look! Isn't it perfect? Give me your watch."」 — 本人の台詞
  - 「Suddenly remembering, she brought out the chain.」 — 地の文
  - 「Jim sat down and smiled gently.」 — 地の文

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Speaker's state of mind: She sounds pleased with the chain and asks Jim to show her his watch.
Scene: At home, Della brings out the chain and shows it to Jim after receiving the combs.
Spoken line before (said by Della; not part of this line): My hair grows quickly.
Narration just before: "Suddenly remembering, she brought out the chain."
Spoken line after (said by Jim; not part of this line): I sold the watch to buy your combs.
Narration just after: "Jim sat down and smiled gently."
Manner words from the narration: gently, smiled, suddenly
How this line answers the previous one: She shifts from saying her hair will grow back to showing Jim the chain and asking for his watch.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

## 8. `full_story_part3_c8` — Jim(Voice Algieba) / ささやき・静かな発言 / ためらい・戸惑い / 相手の発言を受けた返答

- セリフ(英): "I sold the watch to buy your combs."
- 場面(日本語・選定時): Jimが腰を下ろして穏やかに微笑み、Dellaの『時計を貸して』に応えて、櫛を買うために時計を売ったと静かに告げる場面。
- 前のセリフ: Della: My hair grows quickly. / Della: Look! Isn't it perfect? Give me your watch.
- 後のセリフ: なし
- 直前の地の文: Jim sat down and smiled gently.
- 直後の地の文: Della sat beside him and took his hand. Her hair was gone; the combs could not hold it.
- 決定論の manner_words: gently, smiled

**LLM出力**(status = `NO_EXPLICIT_CUE`)
- speaker_state: He explains calmly why he no longer has his watch.
- scene: At home, Jim explains that he sold his watch to buy Della’s combs.
- reaction_to_previous: He answers Della’s request for his watch by explaining that he sold it to buy her combs.
- 根拠引用(出どころ):
  - 「"I sold the watch to buy your combs."」 — 本人の台詞
  - 「Jim sat down and smiled gently.」 — 地の文
  - 「"Look! Isn't it perfect? Give me your watch."」 — 他者の台詞

実際に送られるCONTEXTブロック(accept時):
```text
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Jim.
Scene: At home, Jim explains that he sold his watch to buy Della’s combs.
Spoken line before (said by Della; not part of this line): My hair grows quickly.
Spoken line before (said by Della; not part of this line): Look! Isn't it perfect? Give me your watch.
Narration just before: "Jim sat down and smiled gently."
Narration just after: "Della sat beside him and took his hand. Her hair was gone; the combs could not hold it."
Manner words from the narration: gently, smiled
How this line answers the previous one: He answers Della’s request for his watch by explaining that he sold it to buy her combs.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
```

## レビューの付け方

`er118_output/fz_dialogue_context_tts_trial_01/llm/emotion_review.json` の各 `fable_decision` を `accept` か `discard` にする。discardはLLM由来の項目(状態・場面・返答)を全て外して中立にする。`summary_ja` は試聴ページ用の日本語要約(Sonnet下書き入り。accept時のみ表示)。全8件が埋まるまで ctx arm の有料生成は起動しない。

## Fableレビュー結果(2026-10-25)
8件すべて accept。ACCEPTED 3件(part2_c7/part3_c2/part3_c6)は原文(whispered・kept returning to the mirror / rushed toward him・It'll grow again! / Look! Isn't it perfect?)から妥当に導ける穏当な表現で創作なし。NO_EXPLICIT_CUE 5件(part2_c2/c4/c5、part3_c4/c8)は仕様どおり状態行を出さず、scene・reaction・manner_words・地の文引用で演出を伝える形を採用(結果後の検査ルール変更・LLM再呼出なし=事前登録遵守)。summary_jaはFable確認済み。
