# WPM_MEASUREMENT_01(FAMILY-X-COFFEE-ADVANCED-FULLSTORY-WPM-MEASUREMENT-01 委任_01、2026-10-12)

測定・分析のみ。API費用 JPY 0(ローカル faster-whisper small/medium のみ)。音声・Prompt・Production・試聴ページ・Master Store は変更していない。Trial 隔離。
使用モデル(評価用途): Gemini TTS は委任_03 で生成済み音声を測定しただけ(新規生成なし)。ASR は local faster-whisper(Systran small / medium、int8、CPU)。最新世代上位モデルではない例外理由=費用 JPY 0 指定のため。

## 0. 対象音声(sha256 一致確認済み)
最終版(委任_03/04 の `assembly_manifest_03_final.json` 記載)Advanced Full Story。`part_final/segments/` 配下(完成版へ無加工で組込まれる segment、F5 Style、Aoede、gemini-3.8-flash-lite-tts、Standard 同期):

| Part | wav | sha256 先頭16 | manifest との一致 |
|---|---|---|---|
| 1 | adv_part1_f5.wav | 5b711b91e99a89f4 | 一致 |
| 2 | adv_part2_f5.wav | 2d7c291b5abb6bd9 | 一致 |
| 3 | adv_part3_f5.wav | fa1f978f68eaef81 | 一致 |

原稿: `eigo-radio-tone/.../coffee_prices__run_e_tone_01/b1b/parts.json` の part1〜3(`manuscript_sha256` が generation_log_03.jsonl と一致を確認)。TTS 入力は `tts_safe_news_en(原稿)` 適用後(`tts_input_sha256` 一致の sha12: 627f1c7f7771 / 1eebc2971940 / 677de1413bc2)。見出し(`###`)・In one line は parts.json の part1〜3 に含まれず、読み上げ用の追加テキストもない(Part 本文のみ)。

## 1. 語数の数え方
- 基本(採用): 空白区切りトークンのうち英数字を1文字以上含むもの。ハイフン語・縮約形(haven't)・「6.1%」「U.S.」は 1 語、引用符・句読点は語数に含めない。
- 代替(感度): ハイフン/ダッシュ/スラッシュでも分割。今回の3 Part にはハイフン語がなく、基本と同数。
- `tts_safe_news_en` 適用前後: 文字列は変わる(適用前後で sha 相違。US→U.S. 等)が、語数は3 Part とも同一。採用は「TTS が実際に読んだ入力=適用後」。
- 参考: 委任_03 plan の `word_counts`(正規表現 `[A-Za-z']+` 方式、数字語を数えない)では Part1=131 / Part2=178 / Part3=152。Part2 のみ数え方の違いで 1 語差(本測定は「6.1%」を 1 語と数える)。

## 2. 主表(Advanced Full Story、全体WPM と 発話部分WPM)
発話部分WPM=語数 ÷(再生時間 − 長いポーズ合計)。ポーズ=RMS(20ms窓・10ms刻み)が -40 dBFS 未満の連続区間。主定義は 500ms 以上、感度確認として 300ms 以上も併記。先頭/末尾の無音もポーズとして差引く(500ms では該当なし、300ms では Part1・Part2 先頭 0.34s 等)。

| 区間 | 語数 | 再生時間(s) | 全体WPM | 発話部分WPM(500ms) | 発話部分WPM(300ms) |
|---|---|---|---|---|---|
| Part 1 | 131 | 41.36 | 190.0 | 200.7 | 212.5 |
| Part 2 | 179 | 48.49 | 221.5 | 230.3 | 244.1 |
| Part 3 | 152 | 43.01 | 212.0 | 223.9 | 238.4 |
| 合計(3 Part) | 462 | 132.86 | 208.6 | 219.0 | 232.5 |

発話時間(秒): 500ms 閾値で 39.17 / 46.64 / 40.74(合計 126.55)、300ms 閾値で 36.99 / 44.00 / 38.26(合計 119.25)。
閾値を 300ms→500ms にすると発話部分WPMは約 6〜14 WPM 変わる。どの閾値でも Part 1 < Part 3 < Part 2 の順は不変。

### 参考列: Standard(F5 + 6% 減速)の同Part 全体WPM(対象外・比較用)
Standard は別原稿(a2、語数が異なる)。

| Part | Std 語数 | Std 再生時間(s) | Std 全体WPM | Adv 全体WPM |
|---|---|---|---|---|
| 1 | 117 | 41.62 | 168.7 | 190.0 |
| 2 | 161 | 52.59 | 183.7 | 221.5 |
| 3 | 134 | 42.14 | 190.8 | 212.0 |
| 合計 | 412 | 136.36 | 181.3 | 208.6 |

(Standard は 6% 減速適用済み segment を使用。発話部分WPM は Standard 対象外のため未測定。)

## 3. ポーズ表(閾値 500ms、全て Part 内部の文間)
前後の語は faster-whisper(medium)の語タイミングによる。

| Part | 位置(s) | 長さ(s) | 直前 | 直後 |
|---|---|---|---|---|
| 1 | 8.62 | 0.52 | come down too. | But the price |
| 1 | 17.46 | 0.53 | a time lag. | The price measure |
| 1 | 23.47 | 0.50 | the previous month. | The reason, it |
| 1 | 30.25 | 0.64 | expected to continue. | The U.S. |
| 2 | 7.38 | 0.63 | a year earlier. | It may leave |
| 2 | 16.40 | 0.71 | at a café. | Hold on before |
| 2 | 31.36 | 0.51 | U.S. retail prices. | The road to |
| 3 | 13.19 | 0.65 | on your calendar. | And a cup |
| 3 | 24.57 | 0.50 | behind price increases. | Even if bean |
| 3 | 28.91 | 0.59 | fall with them. | If you are |
| 3 | 37.40 | 0.53 | beans reach here? | A coffee price |

集計(500ms): Part1 4 回 2.19s / Part2 3 回 1.85s / Part3 4 回 2.27s、合計 11 回 6.31s(最長 0.71s)。1 秒以上のポーズは 0 回。
300ms 感度: Part1 10 回(うち先頭・末尾 2)4.37s / Part2 10 回(先頭 1)4.49s / Part3 11 回(末尾 1)4.75s。合計 31 回 13.61s(Part 内部の純ポーズ 27 回)。300ms 版の個別位置は `wpm_results_01.json`(`pause_sens.300.pauses`)に前後語つきで保存。
所見: ポーズは全て 0.5〜0.7s の文間で、文中の長い休止や無音の異常はない。人間のナレーションの文間ポーズ(概ね 0.5〜1 秒超)より短めで、全 Part の語数あたり・時間あたりのポーズ比は 5% 前後(500ms 基準で 4.7%)にとどまる。

## 4. 音声と原稿の一致確認(local faster-whisper、¥0)
委任_03 の Primary ASR(gpt-4o-mini-transcribe)判定: Part1 NORMALIZED_MATCH、Part2 NORMALIZED_MATCH、Part3 HIGH_SIMILARITY_SAFE(既存 validator)。
今回の local 転写(正規化: 小文字化・記号除去・ハイフン分割。推測補正はしていない。差異は全てそのまま列挙):

| Part | model | 比較対象 | ratio | 差異(原稿側 → ASR側) |
|---|---|---|---|---|
| 1 | medium | TTS入力 | 0.974 | `8.7%`→`8 7 %`、`US`→`u s`(表記形式のみ) |
| 1 | small | TTS入力 | 0.970 | 上記 2 件 + `brazil` 挿入(1 語、small のみ) |
| 2 | medium | TTS入力 | 0.948 | `US`→`u s` ×3、`6.1%`→`6 1 percent`、`cafe`→`caf`(アクセント除去の正規化副作用)、`2`→`two`、`9`→`nine` |
| 2 | small | TTS入力 | 0.961 | `6.1%`→`6 1 %`、`2`→`two`、`9`→`nine`、`US`→`u s` ×2 |
| 3 | medium | TTS入力 | 0.984 | `9`→`nine` ×2、`along` 欠落(1 語、medium のみ。small は欠落なし) |
| 3 | small | TTS入力 | 0.987 | `9`→`nine` ×2(数字表記のみ) |

読み: 差異は数字・%・略語の書き分け(表記ゆれ)と、モデル間で一致しない 1 語(medium の `along` 欠落 / small の `brazil` 挿入)のみ。一致しない 1 語は片方のモデルだけで出ており、音声側の欠落・脱落と断定できないため「未確定の差異」として記録する(WPM への影響は ±1 語=約 ±0.5%、結論に影響しない)。語の欠落・追加は ASR 側のため語数は原稿(TTS入力)基準を維持。

## 5. Part 間・Part 内のばらつき
10 秒窓(1 秒刻み、ASR 語タイミングで語数カウント)の「窓内 WPM」と、8 語以上の文単位 WPM:

| Part | 窓 全体WPM 中央値 / 最小〜最大 | 最速窓(開始s、全体WPM / 発話部分WPM) | 文単位WPM 中央値(8語以上の文数) | 最速文 |
|---|---|---|---|---|
| 1 | 198 / 180〜240 | 9.0s: 240 / 276、5.0s: 240 / 261 | 215(8文) | 12.4〜15.6s `When you see a price tag that makes you want to say, haven't you heard the news?` 17語 321 WPM |
| 2 | 234 / 198〜264 | 27.0s: 264 / 290、14.0s: 252 / 300(発話部分最大) | 269(12文) | 44.9〜48.1s `The price tag in a shop does not flash to a new price the moment the market moves.` 18語 340 WPM |
| 3 | 216 / 192〜240 | 27.0s: 240 / 274、29.0s: 234 / 281(発話部分最大) | 239(8文) | 11.1〜13.2s `It is too soon to mark the date on your calendar.` 11語 314 WPM |

- Part 間: 発話部分WPM(500ms)は Part1 200.7 → Part2 230.3 → Part3 223.9。Part2 が Part1 より約 30 WPM(約 15%)速い。同じ F5 Style・同じ voice でも Part ごとに速度が揺れる(TTS の確率的な生成のため)。
- 最速区間: Part2 の約 13〜23 秒(「But the data covers a different month …」〜「So, how long does it take …」付近)、Part2 末尾(約 44.9〜48.1s、340 WPM 相当)、Part1 の約 9〜19s(「But the price tag …」〜「It seems there is a time lag.」)。
- 注意: 文単位WPM は語タイミングの精度(±0.1〜0.2s)と文頭/文末の無音の扱いで数十 WPM 揺れる。短い文(8 語未満)は除外した。ASR が `U.S.` を `U .S.` と分割するため、略語を含む文境界はずれる(`retail prices.` 単独断片など)。窓 WPM のほうが安定。

## 6. 参考比較(一般的なレンジ、出典はいずれも既知の文献・基準からの記憶引用で、今回 Web で再取得していない)
- 米国の放送ニュース/ラジオ: おおむね 150〜170 WPM(Tauroza & Allison 1990 ほか、ラジオ約 160 WPM)。
- オーディオブック: 一般に 150〜160 WPM を標準とする(Audible/ACX のナレーター向けガイダンス)。
- 日常会話: 約 120〜180 WPM、話者・場面で幅が広い。
- ESL/英語学習者向け教材: 概ね 100〜140 WPM、初級〜中級向けでは 100 前後も多い(VOA Special English は約 90 WPM)。
- 速い話者(討論・実況・早口の読み上げ): 200 WPM 超も珍しくなく、聞き取りは話題の難度・ポーズ配置・熟練度に依存する。

比較: Advanced は全体 190〜222 WPM、発話部分 201〜230(500ms 基準)で、ニュース/オーディオブックの一般レンジ(約 150〜170)の上端を約 20〜30% 以上超え、最速窓では約 260〜300 WPM。Standard(減速後)でも全体 169〜191。
WPM は聞き取りやすさの代理指標のひとつにすぎず、本測定だけで「速すぎる」とは断定しない(Advanced は上級者向けで高速が許容される可能性、ポーズの短さ、語の長さ、文の複雑さ、ユーザーの実際の聴感も要判断)。ただし「速い区間が Part 内に偏在し(Part2 の 13〜23s、44.9〜48s)、ポーズが文間 0.5〜0.7s と短い」点は、ユーザー試聴時の確認観点になり得る。判断・調整は本タスクの範囲外(速度調整・再生成は未実施、ユーザー判断待ち)。

## 7. 非エンジニア向け説明: 全体WPM と 発話部分WPM の違い
- 全体WPM: 「ファイルの全長」で語数を割った速さ。文の間の休みも時間に含むので、休みが多いほど数字は小さくなる。リスナーが体感する「1 分あたりに耳に入る語数」に近い。
- 発話部分WPM: 「しゃべっている時間だけ」で割った速さ。休み(今回は 0.5 秒以上の無音)を取り除くので、数字は大きくなる。話し手が口を動かす速さそのものを表す。
- 例(Part 2): 48.5 秒のうち 1.85 秒が長めの休み。全体では 221 WPM、休みを除くと 230 WPM(0.3 秒以上を休みと数えるともっと厳しく見て 244 WPM)。
- 2 つの差が小さい=休みがほとんどなく、ずっと同じ速さで読み続けている音声ということ。差が大きい音声は「速く読んで、間でゆっくり休む」タイプ。今回の Advanced は差が約 9〜12 WPM と小さく、速さが休みで和らげられていない。
- 閾値(何秒以上を休みと数えるか)を決め直すと発話部分WPM は変わる。そのため 300ms/500ms の 2 通りを併記した。

## 8. 再現手順
```
cd C:\Users\tensh\eigo-radio
set PYTHONUTF8=1
.venv\Scripts\python.exe er057_output\coffee_final_listening_tone_trial_01\wpm_measurement_01\measure_wpm_01.py
```
- 入力: 上記 sha 一致の segments wav(スクリプト内で sha を assert)、`eigo-radio-tone/.../b1b/parts.json`(Advanced)と `a2/parts.json`(Standard 参考)、`er003_v1_n3_01_tts_generate.tts_safe_news_en`。
- 語数: 空白区切り+英数字を含むトークン(ハイフン語・縮約形・%・略語は 1 語)。TTS入力(tts_safe 適用後)を採用。
- 無音: モノラル化、20ms 窓・10ms 刻みの RMS を dBFS 換算、-40 dBFS 未満の連続が 300ms または 500ms 以上でポーズ。先頭/末尾も含め、発話時間 = 全長 − ポーズ合計(300ms 未満の短い休みは引かない)。
- ASR: faster-whisper small/medium(CPU int8、beam 5、word timestamps、VAD 無効)。差異判定は小文字化・記号除去・ハイフン分割後の difflib(推測補正なし)。
- 窓 WPM: 10 秒窓・1 秒刻み、窓内に中心が入る ASR 語を数える。発話部分は窓内の 300ms 以上ポーズを差引く。
- 出力: `wpm_results_01.json`(全数値、ポーズ位置・前後語、ASR 語タイミング、窓/文単位)。

## 9. 限界・未決事項
- 語・ポーズ位置は ASR 語タイミング(±0.1〜0.2s)依存。ポーズの検出自体は音声波形(-40 dBFS)なので ASR 非依存。
- -40 dBFS 閾値は一般的な目安であり、BGM・ノイズのないクリーンな TTS 音声前提。
- 「どの WPM が適切か」「減速・再生成するか」はユーザー判断(USER_DECISION_REQUIRED)。本タスクでは提案・実装しない。
