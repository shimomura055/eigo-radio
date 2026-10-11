# Prompt一覧 E: Advanced Preview(英語)

送信方式: `generate_content`、`Part(text=<原稿逐語>, speech_metadata=SpeechMetadata(style=<下記style>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Charon`(Production `speech_metadata_flash_lite` 相当、Standard同期)。

原稿(逐語): `Coffee prices can change for several reasons, and the news can be hard to make sense of. In this episode, we'll look at what is behind the latest coffee price story and what the news can tell us.`

## Baseline(現行Style)

`warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.`

## E1 落ち着いたニュースキャスター

落ち着きのあるキャスター調。急がず、明瞭で自然。

style(speech_metadata.style 逐語):

```
calm, composed news anchor; steady and unhurried, clear and natural.
```

## E2 少しゆったりした自然会話

普段より少しゆったりした会話的ペース。温かく自然で、間延びしない。

style(speech_metadata.style 逐語):

```
relaxed conversational pace, slightly slower than usual; warm and natural, without dragging.
```

## E3 意味のまとまり重視

意味の区切りごとに短い自然な間を置き、無理のない速さで聞き取りやすく。

style(speech_metadata.style 逐語):

```
clear news narration grouped by meaning; short natural pauses at clause boundaries, comfortably paced.
```

## E4 低めで落ち着いたVoice

エネルギーを抑えた、地に足のついた安心感のある声。抑揚は滑らかで自然。

style(speech_metadata.style 逐語):

```
softer, lower-energy and grounded; calm and reassuring tone, smooth natural intonation, easy to follow.
```

## E5 文末の収まり重視

各文が文末で収まってから次へ進む。落ち着いて明瞭。

style(speech_metadata.style 逐語):

```
unhurried news narration; each sentence lands gently and settles before the next begins; calm and clear.
```
