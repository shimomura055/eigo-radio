# LISTEN_COMPARE_REPORT_02 (FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-LISTEN-COMPARE-01 委任_02, 2026-10-13)

Trial(VALIDATED上限)。採用判断なし。N01・N02のTake2/Take3をStd/Advで追加生成(8call)し、比較試聴ページへ追加。

## 3 take表 (Take1はround5既存、Take2/3は今回。Std=6%減速後実測)
| Prompt | Lv | take | WPM実測 | raw換算 | 文末無音 平均/最大ms | 800ms+ | ASR | 異音med+ | ピッチ幅st/強弱幅dB | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| N01 | std | 1 | 153.5 | 163.3 | 494/800 | 0 | NORMALIZED_MATCH | 0 | 12.41/17.7 | 暫定合格 |
| N01 | std | 2 | 150.6 | 160.2 | 573/810 | 1 | NORMALIZED_MATCH | 0 | 10.37/16.8 | 不合格: 速度外(150.6WPM,基準151-163); 文末平均573ms>498 |
| N01 | std | 3 | 79.1 | 84.1 | 569/980 | 5 | TRUE_CONTENT_MISMATC | 1 | 9.44/17.3 | 不合格: 速度外(79.1WPM,基準151-163); 文末平均569ms>498; 800ms+長無音5本; ASR不一致(TRUE_CONTENT_MISMATCH); 異音med+1 |
| N01 | adv | 1 | 167.1 | - | 627/830 | 1 | NORMALIZED_MATCH | 0 | 9.35/16.5 | 不合格: 文末平均627ms>593 |
| N01 | adv | 2 | 174.7 | - | 539/660 | 0 | NORMALIZED_MATCH | 0 | 9.58/17.3 | 不合格: 速度外(174.7WPM,基準161-173) |
| N01 | adv | 3 | 159.4 | - | 607/730 | 0 | NORMALIZED_MATCH | 0 | 11.1/16.7 | 不合格: 速度外(159.4WPM,基準161-173); 文末平均607ms>593 |
| N02 | std | 1 | 161.3 | 171.6 | 514/800 | 1 | NORMALIZED_MATCH | 0 | 9.77/17.1 | 不合格: 文末平均514ms>498 |
| N02 | std | 2 | 146.9 | 156.3 | 621/870 | 3 | NORMALIZED_MATCH | 0 | 10.26/17.5 | 不合格: 速度外(146.9WPM,基準151-163); 文末平均621ms>498; 800ms+長無音3本 |
| N02 | std | 3 | 160.2 | 170.4 | 494/790 | 0 | NORMALIZED_MATCH | 0 | 9.98/17.6 | 暫定合格 |
| N02 | adv | 1 | 170.9 | - | 600/850 | 1 | NORMALIZED_MATCH | 0 | 10.6/16.9 | 不合格: 文末平均600ms>593 |
| N02 | adv | 2 | 179.3 | - | 476/740 | 0 | NORMALIZED_MATCH | 0 | 10.67/16.1 | 不合格: 速度外(179.3WPM,基準161-173) |
| N02 | adv | 3 | 172.1 | - | 447/670 | 0 | NORMALIZED_MATCH | 0 | 11.9/17.3 | 暫定合格 |

## 3 take中の合格数
{"N01_std": 1, "N01_adv": 0, "N02_std": 1, "N02_adv": 1}

## ばらつき(事実のみ)
- N01 Std: WPM 153.5 / 150.6 / 79.1。Take3はTTSが約84秒出力(ASR不一致TRUE_CONTENT_MISMATCH、長無音5本、異音med+1)で破綻。生成1callのコストも約2倍(JPY2.02)。
- N01 Adv: WPM 167.1 / 174.7 / 159.4 (幅15.3)。文末平均 627 / 539 / 607ms。
- N02 Std: WPM 161.3 / 146.9 / 160.2。Take2は遅く文末621ms・800ms+長無音3本。
- N02 Adv: WPM 170.9 / 179.3 / 172.1。Take2は速すぎ(基準外)、Take3のみ合格。
- 合格は各Prompt・各Levelで最大1/3。2 take連続で合格したものはない。

## ページ
https://shimomura055.github.io/eigo-radio/user_test/coffee_style_h_speed_05/ (N01/N02行にTake2/3を追加、各Promptに「3 take中の合格数」表示。他候補・H0・v5の行は不変)

## evidence
- 生成: er057_output/coffee_tts_style_h_speed_05_listen/gen02/ (generation_log_02.jsonl, measurements_02.json, attempts/*.wav[commitしない])
- mp3化: audio_conversion_02.json / 再生: play_evidence_02.json / 状態: state_guard_02.json / 費用: cost_02.json
- モデル gemini-3.8-flash-lite-tts(要求=応答記録)、voice Aoede、Prompt/tts_input shaはRound5と一致(assert済)。技術retry 0。

## 費用
8call: TTS JPY9.66 + ASR概算JPY2.04 = JPY11.70(上限12以内)。TRIAL-03/04累計 106.32 -> 118.02 / 300。価格定数出典は未確認(既存Trial定数流用)。
