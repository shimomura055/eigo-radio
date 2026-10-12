# prompts_pace_02(FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-02 委任_01、Trial限定)

送信方式: `generate_content`、`Part(text=<Advanced Full Story Part原稿(tts_safe_news_en適用済み)>, speech_metadata=SpeechMetadata(style=<下記style>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`、Standard同期。数値WPM・速度倍率はPromptに書かない。機械減速なし。
今回は F5 の前半・後半を含む **Prompt全体** を、調整思想の異なる8方向へ再構成(追記ではなく置換・統合・削除)。分析は `PROMPT_ANALYSIS_02.md`。

## F5(基準、既存音声を再利用・再生成なし)

文字数 246 / sha256 `9228209bec75c2e7684ca883715146ac7b5751d8d3c2b391e4f7517bcb668dad`

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Tell it like a short story to a friend, with a relaxed flow and a lively, natural rhythm; not hurried.
```

## PD1 ニュースナレーション指示の全体再構成

文字数 181(F5 246、差 -65)

sha256 `427fdb6177c41c0d5fdc40a060d6caf10572b1f6cc3038ba52f3f4183d2147e3`

```
Read this as a warm, composed news presenter would on a friendly daytime program: clear, credible and approachable, with a steady, measured delivery and a gentle smile in the voice.
```

F5からの主要変更点: 共通前半(gently upbeat / light sense of energy)と後半(short story to a friend / lively rhythm)を全削除し、「昼の番組の落ち着いた報道キャスター」役割+steady, measured delivery+gentle smileへ全面置換。

## PD2 テンポ誘導語の除去+表情維持

文字数 112(F5 246、差 -134)

sha256 `3e44ea1894095fd2786906f7671d32401b0cfa0c8037eb19b7dffc6dd8903a4d`

```
Warm, friendly and expressive, with natural intonation and a smile in the voice; clear, credible news narration.
```

F5からの主要変更点: テンポ/エネルギー系の語(gently upbeat, light sense of energy, lively, rhythm, relaxed flow, not hurried)を全削除。表情語(warm, friendly, expressive, natural intonation, smile)と信頼性(credible news narration)のみ残す。最短(削除型)。

## PD3 意味単位での間(全体再構成)

文字数 182(F5 246、差 -64)

sha256 `e22b11372793e349e8f802d1e11c86ada8bf717f24895c056c363500cd75a9f0`

```
Friendly, expressive news storytelling. Pause briefly where an idea ends, at commas and between sentences, so each thought is easy to take in, then continue with a bright, warm tone.
```

F5からの主要変更点: エネルギー語と友人への語り口を削除し、「意味が終わる所・コンマ・文間で短く間を置く」指示+bright, warm toneへ置換。

## PD4 Podcastホスト調

文字数 181(F5 246、差 -65)

sha256 `b20137dde189a4e3d58810cbc54e7a6753d4537459057951ed0f52704177032d`

```
A warm, easygoing podcast host sharing an interesting news story with listeners: smiling, relaxed and confident, savoring the surprising moments instead of rushing to the next line.
```

F5からの主要変更点: ニュースナレーション指定を外し、Podcastホスト役割(smiling, relaxed, confident)+「驚きの場面を味わい、次の行へ急がない」へ置換。

## PD5 余裕のある語り(明るさ維持)

文字数 161(F5 246、差 -85)

sha256 `ee8c74611950be32fdea071308933527313bb50b2b74a2942159a4a3b69413e1`

```
Bright, warm and expressive, with the ease of a speaker who has plenty of time; let the key moments breathe, and keep the tone lively rather than slow or sleepy.
```

F5からの主要変更点: lively/rhythmを外し、「時間がたっぷりある話し手の余裕」+key momentsを呼吸させる+「slow/sleepyにしない」明示ガードへ置換。

## PD6 聞き手への語りかけ+落ち着き

文字数 177(F5 246、差 -69)

sha256 `3a680861e4d9d1bc46ddba4dc1fc91f26c68f9f9c5e5e450a85fcba7fda43c2d`

```
Speak directly to one listener with warmth and a smile in your voice; calm, steady and reassuring, like a favorite morning radio host, while keeping the news clear and credible.
```

F5からの主要変更点: ニュース調を従に回し、特定1人の聞き手への語りかけ+calm, steady, reassuring(朝のラジオホスト像)へ置換。

## PD7 文間の自然な呼吸+引用・数字で少し緩める

文字数 172(F5 246、差 -74)

sha256 `a32aab8d5f70821fb42686ab9d4b7c98c482ac2704bcb87add1d7f32e0303928`

```
Warm, friendly news narration. Take a natural breath between sentences and ease slightly on quoted words and key numbers, then carry on brightly with expressive intonation.
```

F5からの主要変更点: エネルギー語を削除し、「文間で自然に息継ぎ+引用語・重要数字で少し緩め、その後は明るく再開」の局所的な緩急指示へ置換。

## PD8 ラジオ・フィーチャー調(温かく豊かな表現)

文字数 166(F5 246、差 -80)

sha256 `329ff46a5ec3877f7dc23375e14ee8a806efeff7cfe27963492a3cf95d182226`

```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy.
```

F5からの主要変更点: ニュース調を外し、「愛されるラジオ・フィーチャー」調(unhurried, richly expressive, full vowels, gentle emphasis)+flat/sleepy防止へ置換。母音を十分に響かせる発声寄り。
