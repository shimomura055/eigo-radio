# LISTEN_COMPARE_REPORT_04 (FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-LISTEN-COMPARE-01 委任_04, 2026-10-13)

Trial(VALIDATED上限)。採用判断なし。N01 Std Take4〜6を3call追加生成し、Take3の「原稿2周読み」破綻が再発するかを確認。モデル gemini-3.8-flash-lite-tts(要求=応答記録、最新世代)、voice Aoede。
Prompt sha d1956c91 / tts_input sha 13740eca / manuscript sha e7435a5c は Take1〜3と完全一致(assert済)。6%減速後処理適用。技術retry 0。

## N01 Std 6 take表 (Take1=round5, 2-3=委任_02, 4-6=今回。WPMは減速後実測)
| take | WPM実測 | raw WPM(117語/raw長) | 音声長 raw/減速後 s | 文末無音 平均/最大ms | 800ms+ | ASR | 異音med+ | ピッチ幅st/強弱幅dB | 判定 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 153.5 | 162.7 | 43.16/45.73 | 494/800 | 0 | NORMALIZED_MATCH | 0 | 12.41/17.7 | 暫定合格 |
| 2 | 150.6 | 159.6 | 44.12/46.61 | 573/810 | 1 | NORMALIZED_MATCH | 0 | 10.37/16.8 | 不合格(速度外、文末573>498) |
| 3 | 79.1 | 83.8 | 83.76/88.74 | 569/980 | 5 | TRUE_CONTENT_MISMATCH | 1 | 9.44/17.3 | 不合格(2周読み破綻) |
| 4 | 148.0 | 156.7 | 44.76/47.43 | 613/1170 | 1 | NORMALIZED_MATCH | 2 | 10.13/17.7 | 不合格(速度外148.0<151、文末613>498、異音med2: long_gap@34.4s / click@45.6s) |
| 5 | 148.1 | 156.7 | 44.76/47.40 | 559/810 | 1 | NORMALIZED_MATCH | 0 | 10.61/15.8 | 不合格(速度外148.1<151、文末559>498) |
| 6 | 142.1 | 149.5 | 46.92/49.40 | 749/1090 | 4 | NORMALIZED_MATCH | 0 | 10.85/15.9 | 不合格(速度外142.1<151、文末749>498、800ms+長無音4本) |

## 破綻再発判定 (collapse_rate_03の固定定義)
- Take4〜6とも 2周読み: なし(ASR語数119/120/121、原稿117語。ASR NORMALIZED_MATCH)。原稿外挿入: なし。
- 音声長比(raw長 / 他5take中央値44.12-44.76): Take4 1.01 / Take5 1.01 / Take6 1.06。いずれも1.3倍未満。raw WPM 149.5〜156.7で120未満なし。
- 結論(事実のみ): 追加3 take中、生成破綻の再発は0/3。6 take全体では破綻1/6(Take3のみ)。N01 Std累計(Take1〜6)では1/6。

## 6 take中の合格数・ばらつき
- 合格(暫定) 1/6(Take1のみ)。Take4〜6は3つとも不合格(速度が基準151-163の下に外れる点が共通: 148.0/148.1/142.1)。
- WPM(減速後): 破綻Take3除く5 take 142.1〜153.5(幅11.4)。Take3含め 79.1〜153.5。
- 文末平均無音: 494〜749ms(幅255ms、基準498ms以下を満たすのはTake1のみ)。文末最大: 800〜1170ms。
- 800ms+長無音: 0/1/5/1/1/4本。ピッチ幅 9.44〜12.41st、強弱幅 15.8〜17.7dB。
- Take4〜6はTake2/3に比べTake間の差(speed/文末)は小さくないが、Take1が最良で以降の take は速度がやや遅め・文末がやや長めの傾向(事実のみ、母数小)。

## ページ
https://shimomura055.github.io/eigo-radio/user_test/coffee_style_h_speed_05/ (N01 Std行にTake4〜6追加、合格数表示を「6 take中 1」に更新。他行は不変、行数22->25)。
Playwright実再生(公開URL): 25/25 mp3 HTTP200・再生OK、console error 0 (play_evidence_04.json)。

## evidence
generation: gen04/ (generation_log_04.jsonl, measurements_04.json, gen_summary_04.json, run_stdout_04.txt、attempts/*.wav はcommitしない) / n01_std_6take_04.json / audio_conversion_04.json / play_evidence_04.json / state_guard_04.json (all_unchanged=true) / cost_04.json

## 費用
3call: TTS JPY3.31 + ASR概算JPY0.67 = JPY3.98(上限5、ハードストップ6以内)。TRIAL累計 118.02 -> 122.00 / 300。価格定数出典は未確認(既存Trial定数流用)。
