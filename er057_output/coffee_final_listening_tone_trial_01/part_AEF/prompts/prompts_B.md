# Prompt一覧 B: 共通Intro B(Preview導入)

送信方式: `generate_content`、`Part(text=<原稿逐語>, speech_metadata=SpeechMetadata(style=<下記style>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Charon`(Production `speech_metadata_flash_lite` 相当、Standard同期)。

原稿(逐語): `Here's a quick preview.`

## Baseline(現行Style)

`natural, clear, conversational`

## B1 落ち着いたMC

司会者がPreviewへ落ち着いて橋渡しする雰囲気。急がず滑らかで親しみのある声。

style(speech_metadata.style 逐語):

```
calm, relaxed host handing over to the preview; unhurried and smooth, with a friendly settled tone.
```

## B2 自然な会話

友人に話しかけるような自然な導入。無理のない、アナウンサーらしさを抑えた話し方。

style(speech_metadata.style 逐語):

```
natural, friendly conversational lead-in, as if saying it to a friend; easy and unforced, not announcer-like.
```

## B3 明瞭な案内

コーナー案内として一語ずつはっきり。速すぎず遅すぎず、安定した声。

style(speech_metadata.style 逐語):

```
clear, well-articulated segment announcement; each word distinct, steady and confident, neither rushed nor slow.
```

## B4 リズム重視

短いフレーズを一息で滑らかに。形容詞を軽く強調し、最後の語へ穏やかに持ち上げる。

style(speech_metadata.style 逐語):

```
smooth, even rhythm; the short phrase flows in one easy breath, with light emphasis on the adjective and a gentle lift into the final word.
```

## B5 文末処理重視

親しみのある導入が最後の語で柔らかく下がり、切れずに自然に収まる。

style(speech_metadata.style 逐語):

```
friendly lead-in that lands gently; the last word settles with a soft, natural falling close, not clipped or rushed at the end.
```
