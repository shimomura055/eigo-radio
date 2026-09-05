# OPEN-112-TREND-THEME2-B-A2-PEAK-MEASUREMENT-16

**管理ID**: OPEN-112-TREND-THEME2-B-A2-PEAK-MEASUREMENT-16
**種別**: 読み取り専用の追加計測(Production変更0・有償API呼び出し0)
**目的**: Trial-13 A2 Assemblyで`er002_common.py::write_wav_float`の
assert(`peak=1.0350188975890593`)が発火した原因を、Opus診断
(OPEN-112-TREND-THEME2-B-A2-CLIPPING-ASSERT-DIAGNOSTIC-14)提示の
2仮説(A: Preview経路 / B: ゲイン済みsegmentのリサンプルオーバーシュート)
のどちらで確定するか、実測で判定する。

## 結論

**仮説B確定**。assertを発火させたpieceは`Point One`(`a2_point_one`)
segmentであり、`preview`ではない。Previewのpeakは常に0.70前後で、
1.0への接近は一切していない。

- 発火piece: **`Point One`**、peak=**1.0350188975890593**
  (assertログの値と**完全一致、ビット単位で同一**)
- `a2_point_one`は`compute_gain_for_target_rms(..., max_peak=0.95)`の
  上限に張り付いていた(`rms_before=0.07131`が静かすぎ、必要gain=1.3721
  だがpeak上限0.95でcapされ、`rms_after=0.09785`はtarget_rms=0.10325
  に届いていない)。
- この0.95(24kHz mono、gain適用直後)が、`mono_24k_to_stereo_target()`
  内の`resample_poly(1, 2)`(24kHz→48kHz)を通過した後、
  **overshoot比1.08949倍**(+8.949%)となり、0.95→1.03502へ増加して
  assertを発火させた。
- Previewの生wav(リサンプル前、24kHz mono)peakは0.6999207で、
  リサンプル後も0.70105(overshoot比1.00162、+0.162%)にとどまり、
  1.0へは遠く及ばない。Previewはgain=1.0のまま無調整で通されるが、
  そもそもTTS生成時点のpeakが0.70程度と低く、クリッピングの実害には
  至っていない。

## 計測結果表(Trial-13、peak降順top10)

| piece | peak(完成前、resample後) | duration(秒) |
|---|---|---|
| Point One | **1.0350189** | 37.225 |
| Point Two | 0.9593891 | 42.695 |
| Intro | 0.9500000 | 10.736 |
| In One Line | 0.9181547 | 21.337 |
| Full Story Part 2 | 0.8715332 | 36.886 |
| Point Two semantic heading | 0.8690094 | 3.938 |
| Comment 3 | 0.8542612 | 25.750 |
| Full Story Part 1 | 0.8362163 | 43.752 |
| Topic intro | 0.8006169 | 6.091 |
| Comment 2 | 0.7754928 | 16.270 |

A2は`np.concatenate`のみで重ね合わせが無いため、完成wavのpeak = 全piece中の
最大peak。上記の通り最大は`Point One`であり、`assembled_would_be_peak`
(計測script内で算出)は**1.0350188975890593**でassertログの値と完全一致
(`d['trial13']['assembled_would_be_peak'] == 1.0350188975890593` → `True`
を実測確認)。

### リサンプル前後のovershoot比(Trial-13、上位)

| piece | before(gain後,24kHz mono) | after(resample後,48kHz stereo) | overshoot比 |
|---|---|---|---|
| **Point One** | 0.95000 | **1.03502** | **1.08949**(+8.9%) |
| In One Line | 0.90105 | 0.91815 | 1.01898(+1.9%) |
| Point Two | 0.95000 | 0.95939 | 1.00988(+1.0%) |
| Key phrases intro | 0.56582 | 0.56975 | 1.00694 |
| Full Story Part 1 | 0.83237 | 0.83622 | 1.00462 |
| (他多数) | - | - | 1.0005前後 |

**重要な発見**: `Point Two`も`Point One`と同じく0.95上限にcapされていた
(gain_report: `a2_point_two.peak_after = 0.95`)にもかかわらず、そちらの
overshoot比は1.00988(+1.0%)にとどまり1.0を超えなかった。同じ0.95という
出発点でも、overshoot比は**同一runの中でも0.05%〜8.9%まで内容依存で
大きくばらつく**ことが実測で確認できた。これは`resample_poly`の
ポリフェーズFIRフィルタがオーバーシュートを起こす量が、各音声の
高周波成分・過渡特性(語頭の破裂音等)に依存するためと考えられる
(本タスクでは原因の周波数解析までは行っていない)。

## No.18・No.9・過去14本との比較

| 出力先 | 完成peak | Preview生peak(リサンプル前) | 最大piece |
|---|---|---|---|
| Trial-13(本件) | **1.0350189**(assert発火) | 0.6999207 | Point One |
| No.18 specfix_v2(成功例) | 0.8544359 | 0.6999207 | Intro |
| No.9 tip_screens(成功例、FINAL USER APPROVED) | 0.8414446 | 0.6999207 | Key Phrase 4 |

3件ともPreview生peakは**完全に同一の0.6999207**(異なるwavファイル、
異なるハッシュ・サイズ・生成日だが数値は一致)。これはTTS生成エンジン側の
出力振幅がテキスト内容によらず概ね一定であることを示唆するが、本タスクの
範囲外のため深掘りしていない(参考情報として記載のみ)。

過去のA2 assemble完了14本(`run_summary_assemble.json`、
`completed_peak`昇順ではなく実行順一覧):

| a2_dir | completed_peak | clipping_detected |
|---|---|---|
| pool_benches | 0.90603 | false |
| pool_benches_luna | 0.92503 | false |
| pool_benches_pilot_02 | 0.94287 | false |
| pool_n18_notifications | 0.83891 | false |
| pool_n18_notifications_specfix_v2 | 0.85444 | false |
| pool_n18_notifications_specfix_v2_ec_a_precision_21r | 0.93346 | false |
| pool_n4_supermarket | **0.95000** | false |
| pool_n5_cafes | 0.95534 | false |
| pool_n6_delivery | **0.95000** | false |
| pool_n7_assigned_desks | 0.92865 | false |
| pool_n8_airport_line | 0.90634 | false |
| pool_n9_tip_screens | 0.77795 | false |
| pool_startups | 0.78764 | false |
| pool_subscriptions | 0.88271 | false |
| no18_tight_speech_only_removal_trial_15 | 0.85444 | false |

Opus診断が指摘した「0.78〜0.955、3本が0.95上限」を実測で再確認: 実際に
`pool_n4_supermarket`(0.95000)・`pool_n6_delivery`(0.95000)・
`pool_n5_cafes`(0.95534、上限をわずかに超過)の3本が0.95上限付近に
達していた。これらは**assert未発火のまま既にheadroomがほぼ0だった**
ことを意味する。すなわちTrial-13は「初めて閾値を超えた特異な事故」では
なく、「以前から繰り返し発生していた0.95上限張り付き」が、たまたま
resample overshootの大きいsegment(語頭に強い破裂音・強勢を持つ
Point One本文)に当たって顕在化した、**構造的に再発しうる状態**である。

## 確定した原因

1. `apply_a2_gain()`内の`compute_gain_for_target_rms(max_peak=0.95)`は、
   「24kHz mono、gain適用直後」の時点でのみpeakを0.95以下に制限する。
2. その後`mono_24k_to_stereo_target()`が`resample_poly`で24kHz→48kHzへ
   アップサンプリングするが、この処理はゲイン制御・peak制限を一切
   経由しない(単純な補間フィルタ)。
3. `resample_poly`のオーバーシュートは音声内容に依存し、実測で
   0.05%〜8.9%まで変動する。0.95という上限は「オーバーシュート
   ゼロ」を前提にしており、5%の余裕しかないため、8.9%のような
   大きめのオーバーシュートが起きると1.0を超える。
4. `write_wav_float()`(`er002_common.py:411-421`)は`assert peak <= 1.0
   + 1e-9`の**直後**に`np.clip(samples, -1.0, 1.0)`を実行する構造になって
   おり、assertが無ければ無警告のまま静かにクリップされていたはずである
   (`er002_common.py`414〜415行を実コードで確認済み)。assertは
   「無音のクリッピング事故を検知する安全装置」として正しく機能した。

### SPEC記述との乖離(確認事項)

`CURRENT_SPEC.md`283行目「音量調整 | scalar RMS基準(**Preview/Bodyは
無調整のアンカー**、他要素は平均RMSへ、OutroはIntro基準RMSへ一致)」との
記述に対し、実装(`er003_v1_n3_01_assemble.py::apply_a2_gain`)を確認した
結果:

- **Preview**は実際にgain=1.0で無調整(`gain_report["preview"] =
  {"gain": 1.0, "note": "無加工(新規Preview音声を保持)"}`)。SPEC記述と一致。
- **Body(`full_story_part1`)**は、target_rms算出の平均元(anchor)の
  一つとして使われるが、その後`a2_segments`ループ内で他のsegmentと
  同様に`gain_to_rms()`が適用され、実際にgain=1.1907(Trial-13の例)
  など1.0以外の値でスケーリングされている。SPECの「Bodyは無調整の
  アンカー」という記述は、実装(Bodyもgainされる)と一致していない。

この乖離は本タスクの範囲では**確認のみ**とし、SPEC修正・実装変更は
行っていない(`USER_DECISION_REQUIRED`として報告する)。

## 再発条件の再評価

- 0.95上限に張り付くsegment(RMSが元々静かで、必要gainが大きい
  segment)は過去14本中、少なくとも3本(pool_n4_supermarket、
  pool_n6_delivery、pool_n5_cafes)で発生済み。
- 0.95上限張り付き自体は珍しくない(21%程度の頻度で観測)。
- そのsegmentの`resample_poly`オーバーシュートが約5.3%
  (`1.0/0.95 - 1 ≈ 5.26%`)を超えると1.0を突破する。実測レンジ
  (0.05%〜8.9%)はこの閾値を上回る場合がある。
- したがって、**同種のassert発火は今後も理論上再発しうる**
  (Preview経路ではなく、0.95上限に達したBody/KP等のsegmentが
  resample_poly通過後に閾値を超えるケース)。

## 対策案の絞り込み(実装はしていません)

本タスクのprompt内で言及された2案について、計測結果に基づき評価する
(Opus診断本体の全文は本リポジトリ内では確認できなかったため、
prompt文中に明記された2案のみを対象とする):

- **「Preview経路にpeak上限を追加する」案**: 今回の実測ではPreviewの
  peakは常に0.70前後でリスクが無いため、**この案は今回のassert原因を
  解消しない**(仮説A不成立のため不適合)。
- **「最終段の全体ヘッドルーム安全弁」案**: 実測は、0.95上限に達した
  segmentのresample overshootが内容依存で0.05%〜8.9%まで変動する
  ことを示しており、どのsegment・どの程度のオーバーシュートが起きるかを
  事前に特定するのは困難である。個別segmentへの対処(例: max_peakを
  下げる)は根本原因(resample_polyがgain制御の外側にある)を解消せず、
  かつ音量バランスへ副作用を及ぼす可能性がある。**完成assembled配列
  全体に対する最終ヘッドルーム安全弁(最終peakが閾値を超えた場合のみ
  全体を安全にスケールダウンする、またはassert発火前に検知して
  依頼者へ報告する等)の方が、今回の実測結果と整合する**。

上記はいずれも**設計候補の評価のみ**であり、本タスクでは一切実装して
いない。採用判断はユーザー承認(`APPROVED_FOR_PRODUCTION`)を要する。

## Production変更なし・API呼び出し0・書き込み範囲の確認

- 有償API呼び出し: 0件(TTS/ASR呼び出しは一切行っていない)。
- Production変更: 0件。`er003_v1_n3_01_assemble.py`・`er002_common.py`
  ・`er003_b1_p9a_audio.py`はすべて無変更でimportして呼び出しただけ
  (`load_a2_sources`/`apply_a2_gain`/`build_a2_timeline`のみ呼び出し、
  `stage_assemble_a2`は呼んでいない=wavファイルは一切書き出していない)。
- 書き込み範囲: `er011_output/open112_trend_theme2_b_a2_peak_measurement_16/`
  配下のみ(計測script・stdout・JSON結果・本Reportのみ)。
  `er011_output/open112_trend_theme2_b_full_audio_trial_13/`・
  `er006_output/`配下・`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`
  への書き込みは一切行っていない(実測で確認: `git status`は本タスク
  終了後に別途確認可能)。
- Git操作: 行っていない(統合commitは別途実施予定)。
- 他Agent/Subagentの起動: 行っていない。

## 参照ファイル

- 計測script: `er011_output/open112_trend_theme2_b_a2_peak_measurement_16/er011_open112_a2_peak_measurement_16.py`
- 計測stdoutログ: `er011_output/open112_trend_theme2_b_a2_peak_measurement_16/measurement_stdout_16.txt`
- 計測結果JSON: `er011_output/open112_trend_theme2_b_a2_peak_measurement_16/measurement_result_16.json`
- assert発火時のエラーログ(既存、読み取りのみ): `er011_output/open112_trend_theme2_b_full_audio_trial_13/resume_run3_assemble_only_stdout.log`
- Production該当関数: `er003_v1_n3_01_assemble.py`(`load_a2_sources`486行目〜、
  `apply_a2_gain`547行目〜、`build_a2_timeline`624行目〜)、
  `er003_b1_p9a_audio.py`(`mono_24k_to_stereo_target`180行目、
  `compute_gain_for_target_rms`410行目)、`er002_common.py`
  (`write_wav_float`411〜421行目)
- SPEC該当箇所: `CURRENT_SPEC.md` 283行目(「Preview/Bodyは無調整の
  アンカー」)
- No.9承認記録: `ER-010_NO9_FINAL_CLOSEOUT.md`
