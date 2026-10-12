# prompts_aoede_style_03(FAMILY-X-COFFEE-AOEDE-STYLE-TRIAL-03、Trial限定)

送信方式: `generate_content`、`Part(text=<Coffee v3 Advanced Part1 原稿(tts_safe_news_en適用済み)>, speech_metadata=SpeechMetadata(style=<下記>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`、Standard同期。数値WPM・速度倍率はPromptに書かない。機械減速なし。
P1〜P8 = P0(PD8)の文を一字も変えず、末尾に差分句のみ追加。P0の速度指示(unhurried等)は全候補で維持。lively/energy等の速度を上げる語は使わない(Pace Trial-02でF5が最速だった知見の再利用)。

## P0(基準=現行Coffee v3 Advanced使用のPD8、既存音声を再利用・再生成なし)

文字数 166 / sha256 `329ff46a5ec3877f7dc23375e14ee8a806efeff7cfe27963492a3cf95d182226`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy.
```

## P1 抑揚 少し強め

文字数 222(P0 166、差 +56) / sha256 `e9f32b8b73c15beb14d83dde4f6b262dcb579220fde98692281f01358d24d05d`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Let the pitch rise and fall a little more on key words.
```

P0からの差分: 抑揚(音の上下)を少しだけ強める句を追加。追加句: Let the pitch rise and fall a little more on key words.

## P2 抑揚 中程度

文字数 285(P0 166、差 +119) / sha256 `cfa38ca0a04daceb1b93f56baa4ae77c1285a0871595c9c66b093f4b0fc95963`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Let the pitch rise and fall noticeably on key words and at the ends of phrases, with a clear, natural melodic contour.
```

P0からの差分: 抑揚を中程度に強める句を追加(語末・句末の上下も指定)。追加句: Let the pitch rise and fall noticeably on key words and at the ends of phrases, with a clear, natural melodic contour.

## P3 明るさ・活力 少し

文字数 255(P0 166、差 +89) / sha256 `b0626fa9646f3a7e922e671b762b0ee4f1931de4762268b6a95cc0341706b276`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Add a touch more brightness and a hint of a smile in the voice, while staying unhurried.
```

P0からの差分: 明るさ・笑顔感を少し足す句を追加(unhurried再掲)。追加句: Add a touch more brightness and a hint of a smile in the voice, while staying unhurried.

## P4 明るさ・活力 中程度

文字数 269(P0 166、差 +103) / sha256 `ae2d604b7506722f750b8c1f6b3e7a67e7ca9da4082eb841399b955db0c8e70b`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Bring a cheerful, sparkling warmth with a clearly audible smile in the voice, while staying unhurried.
```

P0からの差分: 明るさ・笑顔感を中程度に足す句を追加(unhurried再掲、lively等の速度誘発語は避ける)。追加句: Bring a cheerful, sparkling warmth with a clearly audible smile in the voice, while staying unhurried.

## P5 明瞭さ重点

文字数 257(P0 166、差 +91) / sha256 `ce7fc5b9e8aeceff7139441f14770d77b6dd7b40a884dc78c42991b312db73c8`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.
```

P0からの差分: 子音・語尾・音節の明瞭さを指定する句を追加。追加句: Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.

## P6 抑揚+明瞭

文字数 313(P0 166、差 +147) / sha256 `690584dea1762a71e70b2bb828a87bf99124d8f273dd658c6f646cbc6e959a63`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Let the pitch rise and fall a little more on key words. Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.
```

P0からの差分: P1の抑揚句+P5の明瞭句。追加句: Let the pitch rise and fall a little more on key words. / Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.

## P7 明るさ+明瞭

文字数 346(P0 166、差 +180) / sha256 `873e3f79dc8ce8a2602d6c1817673378126c018c3e0c4fa85f4a50eb29f4ff0e`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.
```

P0からの差分: P3の明るさ句+P5の明瞭句。追加句: Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. / Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.

## P8 抑揚+明るさ+明瞭 バランス型

文字数 402(P0 166、差 +236) / sha256 `3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Let the pitch rise and fall a little more on key words. Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.
```

P0からの差分: P1・P3・P5の各句を全て少しずつ(バランス型)。追加句: Let the pitch rise and fall a little more on key words. / Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. / Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.
