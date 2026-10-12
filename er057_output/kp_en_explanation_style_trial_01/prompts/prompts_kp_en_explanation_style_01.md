# prompts_kp_en_explanation_style_01(FAMILY-X-COFFEE-KP-EN-EXPLANATION-STYLE-TRIAL-01、Trial限定)

送信方式: `generate_content`、`Part(text=<解説原稿(tts_safe_en適用済み)>, speech_metadata=SpeechMetadata(style=<下記>))`、model=`gemini-3.8-flash-lite-tts`(Production同一、例外種別2: 測定対象=Production使用モデル)、voice=`Aoede`、Standard同期(Production実行はBATCH、モデル・voice・Style経路は同一)。trim=KEY_PHRASE_TRIM_SAFETY_MARGIN 0.30s(Production同一)。数値WPM・速度倍率・速度を上げる語(fast/quick/brisk/lively)はPromptに書かない。機械減速・機械無音除去なし。
P1〜P8 = P0の文を一字も変えず末尾に差分句のみ追加。P0は現行Variant B(`KEY_PHRASE_EXPLANATION_EN`)。P0r2/P0r3はP0と同一Promptの再生成(TTS生成ごとのばらつき=ノイズ基準)。

## 解説原稿(v4使用clipの逐語)

- KP4: `to become lower in amount or level` (tts_input sha256 `e23158101825fa6f3111353376405c045bf77d6e97bdde063650e4831b47d876`)
- KP1: `a delay between one event and another` (tts_input sha256 `558a3605a9044a7696564bddb430b5d9376e340955df6a17f58b26d919c24ba0`)

## P0(基準=現行Variant B) 文字数 52 / sha256 `f44ef4e2f7a7dc7910d370b00f87c4203505bcc9a0fb1de27750ad503a60621c`

```
clear, precise, at a measured pace, without dragging
```

## 差分表

| 候補 | 狙い | P0への追加句 | 文字数 | sha256 |
|---|---|---|---|---|
| P0 | 現行 | (なし) | 52 | `f44ef4e2f7a7` |
| P1 | 文中ポーズ抑制 | Say the whole definition as one smooth, continuous phrase, without long pauses in the middle. | 146 | `133a006ed2a1` |
| P2 | 句のつながり | Link the words together naturally, with only the briefest natural breaths between phrases. | 143 | `ab5d10b60378` |
| P3 | 文頭から文末まで途切れない流れ | Let the sentence flow from its first word to its last, without stopping partway through. | 141 | `a8aaec591ef6` |
| P4 | 文末処理 | Finish the last word cleanly and naturally, without trailing off or lingering. | 131 | `c9c9202364d3` |
| P5 | 自然な説明口調 | Sound like a friendly teacher giving a short, natural definition. | 118 | `e240703e3d1a` |
| P6 | P1+P4 連続性+文末 | Say the whole definition as one smooth, continuous phrase, without long pauses in the middle. Finish the last word cleanly and naturally, without trailing off or lingering. | 225 | `66071a8f9818` |
| P7 | P2+P5 つながり+説明口調 | Link the words together naturally, with only the briefest natural breaths between phrases. Sound like a friendly teacher giving a short, natural definition. | 209 | `b75cc2316454` |
| P8 | P1+P4+P5 バランス型 | Say the whole definition as one smooth, continuous phrase, without long pauses in the middle. Finish the last word cleanly and naturally, without trailing off or lingering. Sound like a friendly teacher giving a short, natural definition. | 291 | `de52c8db0345` |

## P1 文中ポーズ抑制

文字数 146(P0 52、差 +94) / sha256 `133a006ed2a131ebc8ebecf6b9ab4ac487e18d1251df9531971dfdfc3bce6310`

```
clear, precise, at a measured pace, without dragging Say the whole definition as one smooth, continuous phrase, without long pauses in the middle.
```

## P2 句のつながり

文字数 143(P0 52、差 +91) / sha256 `ab5d10b603786a8b8b7ab62768d20111d3539d252615cea992e81b1e68eb1b5c`

```
clear, precise, at a measured pace, without dragging Link the words together naturally, with only the briefest natural breaths between phrases.
```

## P3 文頭から文末まで途切れない流れ

文字数 141(P0 52、差 +89) / sha256 `a8aaec591ef6d9acb42532cc0c84b6edfb2f75991e713d413c565b7e27677acc`

```
clear, precise, at a measured pace, without dragging Let the sentence flow from its first word to its last, without stopping partway through.
```

## P4 文末処理

文字数 131(P0 52、差 +79) / sha256 `c9c9202364d36e422c0edd3f0fe20eea20644d205bc14c6500b9388e013e8d98`

```
clear, precise, at a measured pace, without dragging Finish the last word cleanly and naturally, without trailing off or lingering.
```

## P5 自然な説明口調

文字数 118(P0 52、差 +66) / sha256 `e240703e3d1a62e8fa5e3d1a4bfe4a9d88601d4d67db76f868195049acae4df6`

```
clear, precise, at a measured pace, without dragging Sound like a friendly teacher giving a short, natural definition.
```

## P6 P1+P4 連続性+文末

文字数 225(P0 52、差 +173) / sha256 `66071a8f9818844de10d0a88971e36674cea856e0bd38b7de204a326e858efa7`

```
clear, precise, at a measured pace, without dragging Say the whole definition as one smooth, continuous phrase, without long pauses in the middle. Finish the last word cleanly and naturally, without trailing off or lingering.
```

## P7 P2+P5 つながり+説明口調

文字数 209(P0 52、差 +157) / sha256 `b75cc2316454bde01c15865c99a959b00f2d8dc873f49d4922c096dff8801fad`

```
clear, precise, at a measured pace, without dragging Link the words together naturally, with only the briefest natural breaths between phrases. Sound like a friendly teacher giving a short, natural definition.
```

## P8 P1+P4+P5 バランス型

文字数 291(P0 52、差 +239) / sha256 `de52c8db0345922452debe324f5d0b0360fa855214c4abe3bfbf5130dc592c98`

```
clear, precise, at a measured pace, without dragging Say the whole definition as one smooth, continuous phrase, without long pauses in the middle. Finish the last word cleanly and naturally, without trailing off or lingering. Sound like a friendly teacher giving a short, natural definition.
```
