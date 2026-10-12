# prompts_pace_01(FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-01 委任_02、Trial限定)

送信方式: `generate_content`、`Part(text=<Advanced Full Story Part原稿(tts_safe_news_en適用済み)>, speech_metadata=SpeechMetadata(style=<下記style>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`、Standard同期。数値WPM・速度倍率はPromptに書かない。機械減速なし。
全候補は F5 の共通前半(Baseline現行Style)を維持し、F5固有の後半1文(`Tell it like a short story to a friend, with a relaxed flow and a lively, natural rhythm; not hurried.`)を、別方向の1文へ**置換**(追記ではない)。

## F5(基準、既存音声を再利用・再生成なし)

文字数 246 / sha256 `9228209bec75c2e7684ca883715146ac7b5751d8d3c2b391e4f7517bcb668dad`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Tell it like a short story to a friend, with a relaxed flow and a lively, natural rhythm; not hurried.
```

## PC1 落ち着いたニュースナレーション方向

F5との差分: 後半1文を置換(F5後半 102字 -> 83字)。全体 227字(F5 246字、差 -19)。

sha256 `c2ef66560ec32e454662bd1ea41602dfcaee65d1fc651d6f2f22228ffa9c2d7b`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Deliver it like a calm, composed news narrator giving a measured, unhurried report.
```

## PC2 急がず自然な息継ぎ(文間の間)方向

F5との差分: 後半1文を置換(F5後半 102字 -> 116字)。全体 260字(F5 246字、差 +14)。

sha256 `096cbe099499e48fc69ed7a7171269a59550ac4a0ccda21af6d5a62599db7838`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Take your time, with a natural, unhurried breath between sentences, as if talking with a friend and nothing to rush.
```

## PC3 意味単位で区切る方向

F5との差分: 後半1文を置換(F5後半 102字 -> 91字)。全体 235字(F5 246字、差 -11)。

sha256 `ed96f55f0a35dd9155ddaa7789976c2b6153129166e1731bc82fd69c68d25605`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Phrase the story in meaningful chunks, letting each idea land before moving on to the next.
```

## PC4 文末を静かに収める方向

F5との差分: 後半1文を置換(F5後半 102字 -> 100字)。全体 244字(F5 246字、差 -2)。

sha256 `5bb1760bf75b4f5d11c4d85f3ad4d4e45bfbe943919b13e5c03c463e9192b82c`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Let each sentence settle softly at its end, with a gentle fall in pitch, before the next one begins.
```

## PC5 目の前の1人へ語りかける方向

F5との差分: 後半1文を置換(F5後半 102字 -> 103字)。全体 247字(F5 246字、差 +1)。

sha256 `7ad57705854871b113a87c16834dfb5632800f98f9cd3d0bc7961f9cf6883587`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Speak as if to one attentive listener sitting across from you, warm and conversational, easy to follow.
```

## PC6 重要語・数字を際立たせる方向

F5との差分: 後半1文を置換(F5後半 102字 -> 124字)。全体 268字(F5 246字、差 +22)。

sha256 `ed79779814ab66939732933e7ca1dc5d94e1a794af9d3e9d98cb3c9419398e72`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Give key words and numbers a little extra weight and clarity, with natural pauses around them, so the main points stand out.
```

## PC7 ゆとりある語り手(余白)方向

F5との差分: 後半1文を置換(F5後半 102字 -> 113字)。全体 257字(F5 246字、差 +11)。

sha256 `335631b34a737d9bda38873a2387ae3aa089112f889c300a68b2c8d894919b1c`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Tell it like a thoughtful storyteller, relaxed and spacious, with room to breathe between phrases; never hurried.
```

## PC8 丁寧で滑らかな運び方向(教材調は避ける)

F5との差分: 後半1文を置換(F5後半 102字 -> 120字)。全体 264字(F5 246字、差 +18)。

sha256 `91d09946b7dccbb31ccd5a3cd91750fbf487a0e5c4a635e2337836033859cb70`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Speak with a measured, deliberate cadence that lets each point land, yet stays smooth and connected; never word by word.
```
