# Prompt一覧 A: 共通Intro A(Welcome)

送信方式: `generate_content`、`Part(text=<原稿逐語>, speech_metadata=SpeechMetadata(style=<下記style>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Charon`(Production `speech_metadata_flash_lite` 相当、Standard同期)。

原稿(逐語): `Welcome to English Your Way.`

## Baseline(現行Style)

`natural, clear, conversational`

## A1 落ち着いたMC

番組の司会者が落ち着いて迎え入れる雰囲気。急がず、温かく安定した声。

style(speech_metadata.style 逐語):

```
calm, relaxed show host; warm and unhurried, with a settled, welcoming tone.
```

## A2 自然な会話

友人を迎えるような自然な挨拶。アナウンサーらしさを抑えた、無理のない話し方。

style(speech_metadata.style 逐語):

```
natural, friendly conversational greeting, as if welcoming a friend; easy and unforced, not announcer-like.
```

## A3 明瞭な案内

番組案内として一語ずつはっきり。速すぎず遅すぎず、安定した自信のある声。

style(speech_metadata.style 逐語):

```
clear, well-articulated program announcement; each word distinct, steady and confident, neither rushed nor slow.
```

## A4 リズム重視

最初の語を軽く持ち上げ、番組名の前に自然な一拍を置き、番組名を一続きで流す。

style(speech_metadata.style 逐語):

```
smooth, even rhythm with a light lift on the first word and a brief natural beat before the show name; the show name flows as one connected phrase.
```

## A5 文末処理重視

温かい挨拶が文末で急に切れず、番組名が柔らかく下がって自然に収まる。

style(speech_metadata.style 逐語):

```
warm greeting that lands gently; the show name finishes with a soft, natural falling close, not clipped or rushed at the end.
```
