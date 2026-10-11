# Prompt一覧 B: Key Phrase英語Phrase(Standard/Advanced共通・Aoede)

送信方式: `generate_content`、`Part(text=<原稿逐語>, speech_metadata=SpeechMetadata(style=<下記style>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`、language_code=ja-JP(Production同一)、Standard同期(DEV)。

原稿(逐語、tts_safe_kp_en後): `raw bean` / `push prices up` / `take time` / `right away` / `on a regular basis`

## Baseline(現行Production Style = KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX、逐語)

```
Speak the following short phrase aloud naturally and clearly, in a warm podcast announcer voice, exactly once. Say only this phrase — do not add explanations, examples, introductions, or any other commentary, and do not add, omit, or change any words. Say it as one natural phrase, not as separate words read one at a time. Make sure the very last sound of the phrase is actually spoken, not trailed off into silence, and do not over-emphasize or exaggerate any single sound.

In natural spoken English, short function words such as articles ("a", "an", "the") are usually spoken briefly and without stress, connecting smoothly into the word that follows, while the main content word carries the natural stress of the phrase. If the phrase contains such a function word, keep it light and unstressed, and let it flow naturally into the following word, rather than pronouncing it as its own separate, stressed beat. Do not omit or drop the function word — only make it light and unstressed, not silent, and do not let this affect how clearly the rest of the phrase is spoken.


```

## K1 短い語句の自然なアクセント

style(逐語):

```
Read this as a short vocabulary phrase in natural spoken English. Put the natural stress on the main content word and keep small function words light and unstressed, so the phrase has the same accent pattern it would have inside a real sentence. Say only this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final sound is actually spoken.
```

## K2 意味のまとまり(1つのかたまり)

style(逐語):

```
Say the phrase as one single, smoothly connected chunk of meaning, as if the words belong together and are not read one by one. Keep the pitch movement small and continuous across the whole phrase. Say only this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final sound is actually spoken.
```

## K3 文末の安定(語尾を上げない)

style(逐語):

```
Calm and steady. Let the phrase end with a settled, naturally falling pitch, as a finished statement. Do not raise the pitch at the end, and do not sound like a question or an unfinished list item. Say only this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final sound is actually spoken.
```

## K4 過剰強調の抑制(淡々と自然に)

style(逐語):

```
Plain, understated and natural, like a teacher quietly reading one vocabulary item to a learner. No special emphasis on any word, no dramatic intonation, no exaggerated energy. Say only this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final sound is actually spoken.
```

## K5 学習者向けの明瞭なモデル発音

style(逐語):

```
A clear model pronunciation for English learners: each sound distinctly articulated, natural native rhythm, an even and gentle tone, and a crisp, clean finish on the last sound. Say only this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final sound is actually spoken.
```

