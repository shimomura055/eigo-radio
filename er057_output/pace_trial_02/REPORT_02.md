# REPORT_02(FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-02 委任_01、2026-10-12、Trial限定)
使用モデル: Gemini TTS gemini-3.8-flash-lite-tts(応答model_version実測=同名、最新世代、Production同一)、voice Aoede、Standard同期。Primary ASR=gpt-4o-mini-transcribe(Production既定)+ local faster-whisper small/medium(費用0)。
試聴: https://shimomura055.github.io/eigo-radio/user_test/coffee_pace_trial_02/index.html

## 1. WPM(基準F5=208.6、目標 平均180前後/少なくとも190以下)
| 候補 | P1 | P2 | P3 | 合計WPM | 発話WPM(500) | 発話WPM(300) | 文間ポーズ(500ms) 数/計s | 最速10s窓 | 窓std | 文最大 | Part差 | 判定 | 警告 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PD8 | 169.8 | 192.5 | 185.3 | **183.2** | 193.6 | 210.0 | 14/8.12 | 228.0 | 17.9 | 284.5 | 22.7 | 最優先(175-185) | - |
| PD1 | 178.6 | 192.2 | 188.1 | **186.8** | 202.5 | 214.3 | 18/11.44 | 234.0 | 16.4 | 291.4 | 13.6 | 試聴候補(185-190) | - |
| PD6 | 184.3 | 207.3 | 194.5 | **196.2** | 209.2 | 222.8 | 15/8.83 | 246.0 | 18.6 | 320.4 | 23.0 | 目標未達(>190) | Part>200 |
| PD4 | 188.8 | 210.4 | 191.6 | **197.6** | 207.9 | 220.5 | 12/6.96 | 258.0 | 22.5 | 330.5 | 21.6 | 目標未達(>190) | Part>200,window>250 |
| PD7 | 194.9 | 198.9 | 201.3 | **198.5** | 207.9 | 221.3 | 11/6.28 | 252.0 | 18.2 | 326.9 | 6.4 | 目標未達(>190) | Part>200,window>250 |
| PD2 | 191.9 | 209.6 | 198.8 | **200.8** | 211.0 | 227.9 | 12/6.69 | 252.0 | 17.5 | 314.8 | 17.7 | 目標未達(>190) | Part>200,window>250 |
| PD3 | 187.5 | 209.9 | 204.5 | **201.4** | 209.1 | 221.3 | 9/5.08 | 252.0 | 18.0 | 347.4 | 22.4 | 目標未達(>190) | Part>200,window>250 |
| PD5 | 192.3 | 211.9 | 208.6 | **204.9** | 210.9 | 222.6 | 7/3.83 | 258.0 | 18.9 | 326.7 | 19.6 | 目標未達(>190) | Part>200,window>250 |
| F5 | 190.0 | 221.5 | 212.0 | **208.6** | 219.0 | 232.5 | 11/6.31 | 264.0 | 19.2 | 339.6 | 31.5 | 基準 | - |
- 175〜185(最優先): **PD8 183.2**。185超〜190(試聴候補): **PD1 186.8**。190超(目標未達・参考): PD6 196.2 / PD4 197.6 / PD7 198.5 / PD2 200.8 / PD3 201.4 / PD5 204.9。175未満の候補なし(Part1単独のPD8のみ169.8)。
- 警告: PD8/PD1は最速10秒窓がそれぞれ228/234(閾値250以下、F5 264より低い)、Part>200なし(最大Part2 192.5/192.2)。他6候補はPart>200(PD6〜PD5)かつ窓>250(PD6以外)。
- Part間ばらつき(max-min): PD1 13.6、PD8 22.7、PD7 6.4(最小)、F5 31.5。

## 2. 費用・条件
24 call(8候補x3Part、各1回、技術失敗0、regen 0)、所要66.1秒(6並列)。実費(推定、請求画面未確認): TTS 27.52 + Primary ASR 6.14 = **JPY 33.66**(上限40の84%)。model_version全24件 gemini-3.8-flash-lite-tts。`cost_actual_02.json`、`generation_log_02.jsonl`(prompt sha・text sha・wav sha含む)。

## 3. 機械品質指標(聴感評価ではない)
- Primary ASR: 24件中22件OK。NG 2件(再生成せず警告): **PD1 Part3**(buying->buy、1語。local whisper small/mediumは同箇所差なし)、PD2 Part1(want to->wanna、範囲外候補)。local whisperで **PD8 Part1 は want to->wanna(small/medium両方)**、つまりPD8は口語縮約で読んでいる可能性(Primary ASRはOK)。要試聴。
- local whisper差分は表記系(8.7%、US、2->two、9->nine、cafe->caf)が全候補共通。反復・言い直しの挿入は検出なし。PD1 Part3 medium `do->two`は要試聴。
- 異音検知(既存検知器・閾値不変): F5=6件(medium以上0)。PD8=10件(medium 1: Part3 1.444秒 click)、PD1=10件(0)、PD5 medium 1(Part3 6.89秒 click)、PD6 medium 1(Part2 39.53秒 click)、他medium以上0。自動検知のみを根拠とする再生成なし。
- 簡易ピッチ/強弱(自己相関F0、¥0、`prosody_02.json`): ピッチ幅(p10-p90)F5 10.3半音に対し PD1 10.27 / PD8 9.99 / PD3 11.11 他 9.99〜11.11、強弱幅 F5 19.3dB に対し 18.4〜20.2dB。**機械指標では抑揚の平板化は確認されない**(聴感未確認)。
- 文間ポーズ(500ms以上): F5 11個/6.3s、PD1 18/11.4s、PD8 14/8.1s、PD3 9/5.1s、PD5 7/3.8s。

## 4. 原因分析(どの指示が効き、どれが効かなかったか)
- 減速に効いた: PD8(unhurried+full vowels+richly expressive、-25.4 WPM)、PD1(落ち着いた報道キャスター+steady, measured、-21.8)。両者とも発話部分WPM(500ms)が F5 219.0 -> 193.6 / 202.5 と下がっており、**間(ポーズ)ではなく発声そのものの速度**が下がった。さらにPD8/PD1ともF5前半のupbeat/energy/livelyを全て落とし役割・発声品質へ置換している。
- 弱かった: 「間を置け・息継ぎ」系(PD3、PD7)は文間ポーズが増えず(PD3 9個<F5 11個)、減速も7〜10 WPMに留まる。「時間がたっぷりある」(PD5)は lively を残したこともあり最小(-3.7)。語の削除だけ(PD2)は-7.8。語りかけ+落ち着き(PD6、PD4)は-11〜-12。
- 示唆: (1)tempo語の削除だけでは約8 WPM、(2)ポーズ誘導指示は効きにくい、(3)役割+発声品質(unhurried/measured/full vowels)が最も効く。PD7はPart間差6.4と均一化には有効。
- 目標190以下はPD8/PD1の2件で達成、180前後(175〜185)はPD8のみ。「明るさ・F5の魅力の維持」は機械指標(抑揚幅同等)では劣化が見えないが、聴感は未確認。

## 5. Production不変確認
書込先は `er057_output/pace_trial_02/`・`user_test/coffee_pace_trial_02/`・`er057_pace_trial_02_*.py` のみ。Production runner不使用、Master Store/manifest/telemetry/queue/attempt_history書込なし。`production_sha_before_02.txt` と `production_sha_after_02.txt` 8件全て一致。新規scriptへのProduction側参照(grep)なし。CURRENT_SPEC/Prompt未編集。
