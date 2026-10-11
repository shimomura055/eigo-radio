# ANOMALY_CANDIDATES_01(委任_01C §5 Phase 1、無料ローカル解析、候補の確定はユーザーが行う)

検知スクリプト `er057_audio_anomaly_detect_trial_01.py`(numpy 2.5.1 / scipy 1.18.0 / soundfile 0.14.0 / local faster-whisper 1.2.1 `small`、API不使用、費用JPY 0)。生データ: `ANOMALY_CANDIDATES_01.json`(全候補96件、うち掲載60件)。
人間確認ページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/anomaly/index.html (候補ごとの前後3秒mp3+スペクトログラム+全編へのジャンプ)

## 重点箇所(ユーザー指定)

- **FOCUS-STD-P3-coffee**: Standard Full Story Part 3「A coffee price tag may have its own hidden clock」の coffee 付近 — ローカルfaster-whisper(small)のword timestampで coffee = 43.30〜43.56秒(セグメント内)、episode上 265.45〜265.71秒。前後を含め5秒クリップ。 検知器の候補は ±1.0秒以内に**0件**(下記「重点箇所の所見」参照)。
- **FOCUS-ADV-P3-coffee**: (参考・対照)Advanced Full Story Part 3 の同じ文 coffee 付近 — local whisper(small) coffee = 39.02〜39.30秒、episode上 260.85〜261.13秒。 検知器の候補は ±1.0秒以内に**0件**(下記「重点箇所の所見」参照)。

## 掲載候補(60件。症状の優先順→信頼度→時刻)

| 表示ID | level | segment | seg内(s) | episode(s) | 症状 | 信頼度 | 指標値 | 近傍の語 |
|---|---|---|---|---|---|---|---|---|
| STD-01 | Standard | Key Phrase 3(英語) | 0.214 | - | クリック/ポップ(瞬間的な波形の飛び) | high | ratio=107.6, abs_d2=0.1149, isolation=0.983 | [Take] time. |
| STD-02 | Standard | Full Story Part 2 | 40.94 | 195.19 | クリック/ポップ(瞬間的な波形の飛び) | medium | ratio=81.1, abs_d2=0.0866, isolation=0.957 | roast coffee keep [robbings] in stock. Roasting |
| STD-03 | Standard | Full Story Part 2 | 30.344 | 184.594 | クリック/ポップ(瞬間的な波形の飛び) | low | ratio=40.8, abs_d2=0.0734, isolation=0.939 | Reuters. They estimate [robbing] prices take at |
| STD-04 | Standard | Full Story Part 3 | 27.549 | 249.699 | クリック/ポップ(瞬間的な波形の飛び) | low | ratio=45.8, abs_d2=0.1523, isolation=0.881 | pay, and buying [beans.] Even if bean |
| STD-05 | Standard | Comment 2 | 5.75 | 146.44 | 不自然に長い無音 | low | gap_seconds=0.8, silence_thr_db=-52.3 | ない よう です。 [です。] では、 豆 の |
| STD-06 | Standard | Full Story Part 2 | 8.35 | 162.6 | 音量の急変(階段状) | low | step_db=-10.9, before_db=-22.6, after_db=-33.5 | month a year [earlier.] You might wonder, |
| STD-07 | Standard | Full Story Part 2 | 20.275 | 174.525 | 音量の急変(階段状) | low | step_db=11.2, before_db=-31.6, after_db=-20.5 | a cafe. Don't [Don't put] the two numbers |
| STD-08 | Standard | Full Story Part 2 | 25.7 | 179.95 | 音量の急変(階段状) | low | step_db=-12.1, before_db=-26.2, after_db=-38.3 | to reach a [price tag?] tag? People in |
| STD-09 | Standard | Full Story Part 2 | 44.2 | 198.45 | 音量の急変(階段状) | low | step_db=-11.0, before_db=-22.5, after_db=-33.5 | the beans also [take] time. These companies |
| STD-10 | Standard | Full Story Part 3 | 19.575 | 241.725 | 音量の急変(階段状) | low | step_db=11.1, before_db=-32.3, after_db=-21.2 | just beans. A [person] who runs a |
| STD-11 | Standard | Full Story Part 3 | 9.989 | 232.139 | スペクトルの急変 | low | flux_z=8.1 | that prices will [fall] in nine months. |
| STD-12 | Standard | Full Story Part 3 | 27.045 | 249.195 | スペクトルの急変 | low | flux_z=8.4 | cups, workers pay, [and] buying beans. Even |
| STD-13 | Standard | In One Line | 0.363 | 286.149 | スペクトルの急変 | low | flux_z=10.1 | [Falling] coffee bean prices |
| STD-14 | Standard | Full Story Part 1 | 1.52 | 100.416 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=now, whisper=no | Beans cost less, [no.] When you hear |
| STD-15 | Standard | Full Story Part 1 | 15.4 | 114.296 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=there is, whisper=there's | It feels like [there's] a delay. The |
| STD-16 | Standard | Full Story Part 1 | 21.69 | 120.586 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=8.7%, whisper=8 7 | It fell 8 [.7] % from the |
| STD-17 | Standard | Full Story Part 1 | 26.99 | 125.886 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=insert, script=, whisper=it | reached the market. [market. it.] It also expected |
| STD-18 | Standard | Full Story Part 2 | 5.45 | 159.7 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=6.1%, whisper=6 1 | coffee cost 6 [.1] % more than |
| STD-19 | Standard | Full Story Part 2 | 30.22 | 184.47 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=raw bean, whisper=robbing | Reuters. They estimate [robbing] prices take at |
| STD-20 | Standard | Full Story Part 2 | 41.07 | 195.32 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=raw beans, whisper=robbings | roast coffee keep [robbings] in stock. Roasting |
| STD-21 | Standard | Full Story Part 3 | 37.78 | 259.93 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=do, whisper=2 | than how much [two] beans costs now. |
| STD-22 | Standard | Full Story Part 3 | 38.21 | 260.36 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=cost, whisper=costs | much two beans [costs] now. Also ask, |
| STD-23 | Standard | Full Story Part 3 | 45.12 | 267.27 | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=hidden, whisper=hitting | have its own [hitting] clock, separate from |
| STD-24 | Standard | Topic intro | 1.44 | 14.566 | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=Coffee, whisper_prob=0.458 | Today's topic is [Coffee] Bean Prices Fall. |
| STD-25 | Standard | Full Story Part 1 | 17.19 | 116.086 | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=International, whisper_prob=0.475 | a delay. The [International] Coffee Organization shared |
| STD-26 | Standard | Full Story Part 2 | 33.63 | 187.88 | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=U, whisper_prob=0.472 | to appear in [U] .S. shop prices. |
| STD-27 | Standard | Full Story Part 3 | 28.56 | 250.71 | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=Even, whisper_prob=0.434 | and buying beans. [Even] if bean prices |
| STD-28 | Standard | Full Story Part 3 | 38.21 | 260.36 | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=costs, whisper_prob=0.404 | much two beans [costs] now. Also ask, |
| STD-29 | Standard | In One Line | 4.76 | 290.546 | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=U, whisper_prob=0.445 | months to affect [U] .S. shop prices. |
| STD-30 | Standard | Key Phrase 1(英語) | 0.47 | - | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=Robbing, whisper_prob=0.204 | [Robbing] |
| ADV-01 | Advanced | Full Story Part 1 | 12.82 | - | クリック/ポップ(瞬間的な波形の飛び) | medium | ratio=70.0, abs_d2=0.07, isolation=0.967 | a price tag [tag that] makes you want |
| ADV-02 | Advanced | Full Story Part 1 (Aoede) | 17.627 | 117.493 | クリック/ポップ(瞬間的な波形の飛び) | low | ratio=40.8, abs_d2=0.1183, isolation=0.921 |  |
| ADV-03 | Advanced | Comment 4 (Charon) | 5.926 | 272.762 | クリック/ポップ(瞬間的な波形の飛び) | low | ratio=46.6, abs_d2=0.1202, isolation=0.962 |  |
| ADV-04 | Advanced | Comment 3 | 10.956 | - | クリック/ポップ(瞬間的な波形の飛び) | low | ratio=43.5, abs_d2=0.1447, isolation=0.953 | か る こと [が] で きます。 次 |
| ADV-05 | Advanced | Comment 4 | 5.926 | - | クリック/ポップ(瞬間的な波形の飛び) | low | ratio=57.6, abs_d2=0.364, isolation=0.96 | いる の が、 [2] 年 間 に |
| ADV-06 | Advanced | Comment 4 | 9.836 | - | クリック/ポップ(瞬間的な波形の飛び) | low | ratio=41.2, abs_d2=0.1465, isolation=0.977 | います。 この お [店] は、 3 年 |
| ADV-07 | Advanced | Full Story Part 1 | 22.62 | - | クリック/ポップ(瞬間的な波形の飛び) | low | ratio=48.9, abs_d2=0.1335, isolation=0.934 | % from the [the previous] month. The reason, |
| ADV-08 | Advanced | Full Story Part 3 | 36.424 | - | クリック/ポップ(瞬間的な波形の飛び) | low | ratio=51.7, abs_d2=0.0726, isolation=0.956 | now, but also [when] does the price |
| ADV-09 | Advanced | Preview (Charon) | 2.244 | 26.1 | 音量の急変(階段状) | low | step_db=-10.7, before_db=-21.4, after_db=-32.1 |  |
| ADV-10 | Advanced | pause_0.5 | 0.149 | 35.975 | 音量の急変(階段状) | low | step_db=10.2, before_db=-30.1, after_db=-19.8 |  |
| ADV-11 | Advanced | Full Story Part 1 (Aoede) | 7.759 | 107.625 | 音量の急変(階段状) | low | step_db=-16.4, before_db=-19.0, after_db=-35.4 |  |
| ADV-12 | Advanced | Comment 2 (Charon) | 5.564 | 147.95 | 音量の急変(階段状) | low | step_db=11.4, before_db=-33.4, after_db=-22.0 |  |
| ADV-13 | Advanced | Full Story Part 2 (Aoede) | 17.194 | 168.55 | 音量の急変(階段状) | low | step_db=-14.4, before_db=-27.1, after_db=-41.5 |  |
| ADV-14 | Advanced | Full Story Part 2 (Aoede) | 23.794 | 175.15 | 音量の急変(階段状) | low | step_db=-10.8, before_db=-25.8, after_db=-36.6 |  |
| ADV-15 | Advanced | Outro (Charon) | 4.634 | 289.75 | 音量の急変(階段状) | low | step_db=-14.6, before_db=-30.6, after_db=-45.2 |  |
| ADV-16 | Advanced | Full Story Part 1 | 7.775 | - | 音量の急変(階段状) | low | step_db=-11.2, before_db=-19.4, after_db=-30.6 | has already come [down to.] to. But the |
| ADV-17 | Advanced | Full Story Part 2 | 8.925 | - | 音量の急変(階段状) | low | step_db=-10.8, before_db=-18.1, after_db=-28.9 | leave you wondering, [] did prices go |
| ADV-18 | Advanced | Full Story Part 2 | 17.2 | - | 音量の急変(階段状) | low | step_db=-14.0, before_db=-28.8, after_db=-42.9 | cup at a [cafe.] Hold on before |
| ADV-19 | Advanced | Full Story Part 2 | 23.775 | - | 音量の急変(階段状) | low | step_db=-11.7, before_db=-28.3, after_db=-40.0 | reach a price [price tag?] According to estimates |
| ADV-20 | Advanced | Preview | 2.225 | - | 音量の急変(階段状) | low | step_db=-10.2, before_db=-22.7, after_db=-33.0 | ス は 数 [々] な 理 由 |
| ADV-21 | Advanced | Key Phrase 2 | 3.155 | 53.051 | スペクトルの急変 | low | flux_z=8.1 |  |
| ADV-22 | Advanced | Key Phrase 3 | 0.361 | 59.467 | スペクトルの急変 | low | flux_z=8.1 |  |
| ADV-23 | Advanced | Full Story Part 1 | 7.88 | - | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=too, whisper=to | already come down [to.] But the price |
| ADV-24 | Advanced | Full Story Part 1 | 21.34 | - | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=8.7%, whisper=8 7 | Organization fell 8 [.7] % from the |
| ADV-25 | Advanced | Full Story Part 1 | 27.86 | - | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=insert, script=, whisper=it | entered the market [market it,] and a good |
| ADV-26 | Advanced | Full Story Part 2 | 4.23 | - | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=replace, script=6.1%, whisper=6 1 | coffee was 6 [.1] % higher than |
| ADV-27 | Advanced | Full Story Part 2 | 28.55 | - | ローカルASR転写が原稿と異なる語(読み違い・不明瞭の可能性) | low | op=insert, script=, whisper=it | interviewed by Reuters, [it] It takes at |
| ADV-28 | Advanced | Full Story Part 1 | 27.86 | - | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=it,, whisper_prob=0.481 | entered the market [market it,] and a good |
| ADV-29 | Advanced | Full Story Part 2 | 21.02 | - | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=how, whisper_prob=0.468 | the ring. So [how] long does it |
| ADV-30 | Advanced | Key Phrase 1(英語) | 0.27 | - | ローカルASRの信頼度が低い語(聞き取りにくい可能性) | low | word=Lag, whisper_prob=0.413 | [Lag] |
