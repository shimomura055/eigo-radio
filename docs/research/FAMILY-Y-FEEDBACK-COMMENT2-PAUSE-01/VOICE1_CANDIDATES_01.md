# VOICE1_CANDIDATES_01 — 『宅配』E-1 Voice 1の代替候補(Std/Adv各3 take、未採用)

管理ID: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_03 B(2026-10-26)。**候補はすべて未採用**(現行採用音声は差し替えていない。採用はユーザー試聴後、既存の`er121_e1_hr_adopt_r0_01.py`系手続き=`approved_by="user"`のみ)。

## 生成方法(Production関数と同一設定、run_01のnarration/audit/review_lockは未変更)
- script: `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/tools/yfb_voice1_candidates_01.py`(Production関数のy_voice_1の`_gen`と同一呼出し: Voice=Algieba、Std=`generate_a2_segment_with_slowdown`[『ゆっくり』instruction+6%減速+減速後ASR再検証を内蔵]、Adv=`generate_news_narration_wide_margin`[ASR判定+repetition QA])。同じ本文(`parts.json`のy_voice_1)、同じstyle、同じ速度処理。
- 出力先: `er121_output/family_y_production_01/redelivery_fee/run_01/{a2,b1b}/hr_adopt_prep/voice1_candidates/take{1,2,3}/`(wavは不追跡。公開mp3は`user_test/family_y_production_redelivery_fee_01/audio/v1cand_*.mp3`)。
- 起動: Std 09:14:33(JST) / Adv 09:26:03(JST)(間隔11.5分、起動直前に`stop_scope_check_01.py` rc=0)。`TTS_EXECUTION_MODE=STANDARD`。各processは3 takeを直列生成。
- 正式経路の挙動をそのまま通した結果、3回の試行(標準2+fallback1)でASR/QAを通らなかったtakeは `STOPPED`(=Human Review対象)で終わる。E-1の現行採用(Std attempt5/Adv attempt6)も同じ経路でHR承認されたもの。STOPPEDのtakeは最後のattempt音声を候補として提示(Stdは採用時と同じ6%減速[API 0]を適用した音)。
- 停止統計: 委任_02 tools(`yfb_silence_scan_01.py`→`yfb_pause_stats_01.py`、10msフレームRMS<-40dBFS/150ms以上、無音間の有音120ms未満は統合)。「文中停止(500ms以上)」=統合後の停止のうち句読点直後でない割当てのもの(位置は推定±2〜3語)。ページ表示は`er121_family_y_audio_01.pause_stats`(同手順のnumpy実装、現行採用wavで数値が一致することをtestで固定)。

## 比較表(Voice 1)
| level | 音声 | 状態 | 秒 | 停止(統合後) | ≥700ms | ≥1000ms | 文中≥500ms | 最長ms | 停止占有率 | wav(不追跡) |
|---|---|---|---|---|---|---|---|---|---|---|
| Std | 現行採用(attempt5+6%減速) | 採用済み(HR承認) | 46.46 | 20 | 8 | 1 | 3 | 1880 | 25.6% | `er121_output/family_y_production_01/redelivery_fee/run_01/a2/narration/y_voice_1.wav` |
| Std | 候補take1 | STOPPED(ASR=-, attempts=3) | 36.1 | 10 | 1 | 0 | 2 | 890 | 15.9% | `er121_output/family_y_production_01/redelivery_fee/run_01/a2/hr_adopt_prep/voice1_candidates\take1/narration/y_voice_1_slowed6pct.wav` |
| Std | 候補take2 | OK(ASR=PASS, attempts=1) | 43.18 | 12 | 6 | 2 | 1 | 1340 | 20.6% | `er121_output/family_y_production_01/redelivery_fee/run_01/a2/hr_adopt_prep/voice1_candidates/take2/narration/y_voice_1.wav` |
| Std | 候補take3 | OK(ASR=PASS, attempts=2) | 40.65 | 12 | 7 | 1 | 1 | 1370 | 21.1% | `er121_output/family_y_production_01/redelivery_fee/run_01/a2/hr_adopt_prep/voice1_candidates/take3/narration/y_voice_1.wav` |
| Adv | 現行採用(attempt6) | 採用済み(HR承認) | 44.36 | 14 | 7 | 3 | 0 | 1250 | 19.9% | `er121_output/family_y_production_01/redelivery_fee/run_01/b1b/narration/y_voice_1.wav` |
| Adv | 候補take1 | OK(ASR=PASS, attempts=1) | 43.04 | 13 | 6 | 1 | 0 | 1000 | 17.9% | `er121_output/family_y_production_01/redelivery_fee/run_01/b1b/hr_adopt_prep/voice1_candidates/take1/narration/y_voice_1.wav` |
| Adv | 候補take2 | STOPPED(ASR=-, attempts=3) | 42.48 | 13 | 4 | 1 | 0 | 1060 | 17.5% | `er121_output/family_y_production_01/redelivery_fee/run_01/b1b/hr_adopt_prep/voice1_candidates/take2/narration/y_voice_1.wav` |
| Adv | 候補take3 | STOPPED(ASR=-, attempts=3) | 42.76 | 14 | 5 | 0 | 0 | 920 | 17.8% | `er121_output/family_y_production_01/redelivery_fee/run_01/b1b/hr_adopt_prep/voice1_candidates/take3/narration/y_voice_1.wav` |

計測JSON: `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/measure/v1cand/`・`v1cand_aligned/`・`_v1cand_stats.json`。

## 読み取り(事実のみ。採否の判定ではない)
- 現行採用はStd 25.6%/最長1.88秒、Adv 19.9%/最長1.25秒。候補はStd 15.9〜21.1%(最長0.89〜1.37秒)、Adv 17.5〜17.9%(最長0.92〜1.06秒)で、**6 takeすべてが現行採用より停止占有率・最長停止とも小さい**(標本は同一本文の各3 takeのみ=Voice 1の揺れの範囲を示す参考値)。
- Std take1は他より約7秒短い(36.1秒、減速後)。本文は全文読まれているが、速い読みのため同じ「ゆっくり」指示でもペースが異なる(聴いて判断する材料)。
- 停止量が少ないtakeは、ASRを通らなかった(STOPPED/HR対象)ものを含む。停止量の指標は選別基準に存在しない(新Gateは新仕様=ユーザー判断)。

## 採用手続き(参考。実行しない)
ユーザーが候補を選んだ場合のみ、承認発言の逐語保存(`--user-statement-ref`)を伴う既存の採用手続き(`er121_e1_hr_adopt_r0_01.py`の`hr_adopt_prep`形式)で採用する。Stdは減速後ASR再検証PASSが採用条件。
