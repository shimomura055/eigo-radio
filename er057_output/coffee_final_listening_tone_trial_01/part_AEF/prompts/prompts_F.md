# Prompt一覧 F: Full Story Part1冒頭(Standard/Advanced共通Style)

送信方式: `generate_content`、`Part(text=<原稿逐語>, speech_metadata=SpeechMetadata(style=<下記style>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`(Production `speech_metadata_flash_lite` 相当、Standard同期)。

原稿(逐語): `"Beans have gotten cheaper!" At that news, your wallet pumps its fist. In your mind, the price of your usual cup has already come down, too. But the price tag in a shop may not change right away. When you see a price tag that makes you want to say, "Haven't you heard the news?", it seems there is a time lag.`

## Baseline(現行Style)

`warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration.`

## F1 発話テンポ重視

現行の明るい抑揚を保ち、話し言葉として心地よい自然なテンポ(急がず間延びもしない)。

style(speech_metadata.style 逐語):

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Keep a comfortable, natural storytelling tempo, neither rushed nor dragging.
```

## F2 意味のまとまり重視

現行の抑揚を保ちつつ、意味の塊ごとに短く自然な間を置いて聞き取りやすく。

style(speech_metadata.style 逐語):

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Group the words by meaning, with brief natural pauses between ideas so each one is easy to take in.
```

## F3 自然な間重視

現行の抑揚を保ち、引用の前後や話の転換点に小さな自然な間を置く。

style(speech_metadata.style 逐語):

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Leave a small natural beat before and after quoted lines and at turns in the story.
```

## F4 文末の収まり重視

現行の抑揚を保ち、各文が文末で自然に収まってから次の文へ進む。

style(speech_metadata.style 逐語):

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Let each sentence settle naturally at its end before the next one begins.
```

## F5 Storytellingリズム重視

現行の表情を保ち、友人に短い話を聞かせるような、ゆったり流れる躍動感のあるリズム。

style(speech_metadata.style 逐語):

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Tell it like a short story to a friend, with a relaxed flow and a lively, natural rhythm; not hurried.
```

## F0 現行F1.5(同一原稿で再生成)(参考baseline再生成)

現行Production Style F1.5そのまま(Advanced相当)。候補との公平比較用に同一原稿で再生成。

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration.
```

## F0S 現行Standard方式(F1.5+減速指示+6%減速)(参考baseline再生成)

現行Standard再現: F1.5に既承認の減速指示を連結して生成し、後段で6%減速(atempo)を適用。

```
warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration.
Speak at a slightly slower, relaxed pace than natural adult narration, while keeping the delivery smooth, conversational, and natural. Do not exaggerate pauses or sound instructional.
```

## Standard相当6%減速(各F候補)

Production既存処理 `er008_a2_postprocess_slowdown_01.apply_a2_slowdown`(FFmpeg `atempo`=1/1.06, pitch保持, A2_SLOWDOWN_PERCENT=6.0)を候補の生成wavへローカル適用。Standard専用の減速指示文は候補では付けない(F0Sのみ現行再現として付与)。
