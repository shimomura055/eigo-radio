# OPEN-112-THEME2-B1-REASSEMBLY-POST-WIRING-03_REPORT

Lane A、ユーザー承認2026-09-07。Theme 2「若者の旅行:ゆっくり滞在」B1の
既存完成音声(`er011_output/open112_trend_theme2_b_final_audio_rerun_02/`)に
実在したFull Story Part 1のfalse startを、OPEN-121 Production配線後の
新PASS音声へ差し替え、既存Production関数(無変更)で新しい出力ディレクトリ
(`er011_output/open112_trend_theme2_b_final_audio_rerun_03/`)へ再Assembly
した。rerun_02は上書きしていない。新規TTS/ASR呼び出しは0件(既存音声の
再利用+ローカル計算のmonitoringのみ)。Git操作なし(Fableが統合)。

## 1. 入力確認

| 項目 | 旧(rerun_02採用) | 新(rerun_03採用) |
|---|---|---|
| sha256 | `54bfd035f3327a9824f81f1d9a06fbb2400b32d85b76887df13df2b20fb2a47f` | `a598c2342abfd758e2c009b978ca6d8d1d33c00b3582e2b8e460661724cd891b` |
| duration | 40.9419秒 | 42.011秒 |
| 生成元 | Trial-13(rerun_02がreview_lock RESOLVED確認のうえ再利用) | `er011_output/open121_tts_repetition_qa_production_wiring_01/theme2_b1_fsp1_regen/`(attempt1、TTS_EXECUTION_MODE=STANDARD) |
| canonical_text sha256 | `b042b098d2f3ab9d15cc0a4f725dc28e2c1761729ac645f46ce919fe1da743e9` | `b042b098d2f3ab9d15cc0a4f725dc28e2c1761729ac645f46ce919fe1da743e9`(**完全一致**、article.md冒頭4段落と照合済み) |
| status/asr_verified | OK / true | OK / true |
| audio_classification | NORMALIZED_MATCH | NORMALIZED_MATCH |
| repetition_qa | 未配線(記録なし) | flagged=**False**(方式A: matches無し、方式D best_run=0.03秒、方式D' best_run=**0.33秒**[判定閾値0.6秒未満、既知の陽性0.75秒[本タスクでOPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01実測を再確認]と明確に区別]) |
| review_lock | RESOLVED/OK(Trial-13経由) | RESOLVED/OK(`theme2_b1_fsp1_regen/audit/review_lock_state.json`) |

false startの既知事例は`OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01_REPORT.md`
§3で改めてFLAG_D_PRIME(d'=0.75秒、lag=0.97秒)として再確認済み。

## 2. 再Assembly

`er003_v1_n3_01_assemble.py::stage_assemble_b1`(無変更)を、`rerun_02/b1b/`
全体をコピーした`rerun_03/b1b/`(narration/audit/key_phrases/article.md等)に
対して実行。`narration/full_story_part1.wav`のみ新音声へ差し替え、旧音声は
`narration/full_story_part1_old_false_start.wav`として保全。`audit/
tts_generation_results.json`のfull_story_part1エントリを新attemptの実データ
(path/asr_text/attempts_log/repetition_qa_evidence/sha256)へ更新(Gate自体は
このsegmentにsha256記録が元々無く影響しないが、監査記録の正確性のため)。

| 項目 | rerun_02 | rerun_03 |
|---|---|---|
| duration | 341.975秒 | 343.044秒(+1.069秒) |
| peak | 0.80806(原因piece=Intro) | 0.75511(原因piece=新Full Story Part 1) |
| clipping | false | false |
| headroom safety valve | 不適用(peak_before=0.8080582) | 不適用(peak_before=0.7551106、閾値0.98未満) |
| target_rms(gain基準) | 0.07992 | 0.07389(新FSP1のRMSが旧よりやや低いため) |

Audio Validation Gate(`verify_episode_audio_validation_gate`)は例外を投げず
通過(全segment VALIDATED、ASSET_HASH_MISMATCH/MISSING_MANDATORY_DISFLUENCY_QA
無し)。全segment review_lock状態はOK/RESOLVED(reused 12segment + Key Phrase
10件 + 新Full Story Part 1、いずれも確認済み)。

## 3. OPEN-121 monitoring(read-only、再生成なし)

`er011_open121_repetition_qa_production_01.py::evaluate_repetition_qa()`を
本文4segmentへ適用(新規API課金0円、faster-whisper local + numpy spectral)。

| segment | flagged | 方式A | 方式D best_run | 方式D' best_run |
|---|---|---|---|---|
| full_story_part1(新) | False | False | 0.03秒 | 0.33秒(生成時の記録と一致、再現確認) |
| full_story_part2(旧流用) | False | False | 0.05秒 | 0.27秒 |
| point_one(旧流用) | False | False | 0.05秒 | 0.25秒 |
| point_two(旧流用) | False | False | 0.04秒 | 0.41秒 |

OPEN-122(Connected Speech Equivalence Layer)/OPEN-123(Transcript Style
Normalization)は、本episodeのどのsegmentにも発火した記録が無い
(`audio_classification`は4segmentとも一貫してNORMALIZED_MATCH。旧11
segmentはrerun_02生成当時[OPEN-121/122/123のいずれも未配線]の音声を
そのまま再利用しており記録自体が存在しない。新Full Story Part1は
OPEN-121配線後に生成されたがOPEN-122/123のいずれの特別classificationも
記録されていない)。事実の記録のみで、追加検証・再生成は行っていない。

## 4. Gate 7 checklist照合

| 項目 | 状態 |
|---|---|
| (a) 完成episode構造 | player.html上部にB1完成音声(assembled wav)を配置 |
| (b) Preview | timeline行あり |
| (c) Comment全件 | comment_1〜4すべて掲載 |
| (d) 本文全section | full_story_part1/2・point_one/two・in_one_line掲載 |
| (e) Key Phrase英日gloss | KP表(rerun_02から無変更、10件)掲載 |
| (f) Intro/Outro/SFX | 読み上げ有無を明記(音楽ジングル/効果音) |
| (g) segment順・開始秒・click-seek | timeline.json実測値でSeekボタン実装 |
| (h) 使用voice名 | 各segment名に(Charon)/(Aoede)併記 |
| (i) レベル別分離 | 本タスクはB1のみ(A2は対象外、既存rerun_02のまま) |
| (j) 未取得テキスト | 該当なし(全segmentテキスト取得済み) |
| (k) TTS方式明記 | 新FSP1=Standard同期(記録確認)、本タスクは新規TTS呼び出し0件と明記 |
| (l) 再生ボタン+voice名+scriptを同一行 | timeline表・比較表とも同一行に配置 |

## 5. コスト

新規TTS/ASR呼び出し: **0件**(既存OPEN-121 regen音声の再利用のみ)。
monitoringはfaster-whisper local(小型モデル、CPU)+numpy spectral計算のみで
API課金なし。想定上限(Standard同期、上限¥100)に対し実費**¥0**。

## 6. 変更ファイル一覧

- 新規: `er011_output/open112_trend_theme2_b_final_audio_rerun_03/`
  (b1b/一式のコピー+full_story_part1.wav差し替え+
  full_story_part1_old_false_start.wav保全+tts_generation_results.json
  更新+新規assembled wav・gain_report.json・timeline.json・
  headroom_report.json・run_summary_assemble.json・
  open121_monitoring_result.json・player.html)
- 更新: `OPEN_ITEMS.md`(OPEN-112行へ2026-09-07追記1件)
- 不変: `er011_output/open112_trend_theme2_b_final_audio_rerun_02/`
  (一切変更していない)

## 7. 試聴

`file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_03/player.html`

完成episode(B1、343.044秒)のtimeline試聴に加え、旧Full Story Part 1
(false startあり)と新Full Story Part 1(OPEN-121 PASS)の単体比較行を
同一UIで用意した。

## 8. USER_DECISION_REQUIRED

なし(本タスク範囲内では新規の未決事項は発生していない)。到達Status
は`USER_FINAL_AUDIO_REVIEW_REQUIRED`(ユーザー最終試聴待ち、
`APPROVED_FOR_PRODUCTION`は本タスクでは判定しない)。
