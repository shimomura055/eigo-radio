# REUSE_CHECK_01 — 前回Trial音声の再利用判定(API 0、2026-10-26)

対象: `FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01`の`measure/samples_measured.json`(62 sample中、女性Zephyr=voice 2 を除く Algieba+Schedar のみ)。出典音声は`er121_output/family_y_voice_pause_trial_01/{a2,b1b}/`、`run_01`正式attempt、Voice 1候補take。

## 判定項目と結果
| 項目 | 前回(再利用側) | 今回(新規側) | 判定 |
|---|---|---|---|
| 本文 | sha `settings_*.json` text_sha256(例 Adv本文2 `a421590551e3…`、Std本文2 `1badfb7e10e4…`) | `ym7_generate_01.build_spec`の同sha(同じ`run_01/*/parts.json`) | 一致 |
| Style文sha | Std `9293e0c3b294…` / Adv `07d72dd67728…`(前回`settings_*.json`) | 同(testでassert: `ym7_tools_test_01.py::test_generation_settings_identical_across_voices`) | 一致 |
| モデル | attempt JSON `model`=`gemini-3.8-flash-lite-tts` | 同(fresh attempt JSON) | 一致 |
| route | Std `custom_53fd514d` / Adv `english_style_prefix_wide_margin` | 同 | 一致 |
| instruction_text sha(Std attempt JSON) | `9293e0c3b294`(Algieba/Schedar両方) | `9293e0c3b294`(新規6 Voiceすべて) | 一致 |
| 生成関数・減速 | `generate_a2_segment_with_slowdown`(6%)/`generate_news_narration_wide_margin` | 同(`er121_family_y_audio_01.py:454,560`と同一呼出し) | 一致 |
| backend/style_profile/実行モード | `speech_metadata_flash_lite` / `default` / `STANDARD` | 同 | 一致 |
| 計測条件 | −40 dBFS・≥150 ms・<120 ms結合・`yfb_pause_align_01` | 同tool(`yvp_measure_lib_01`経由で再利用) | 一致 |
| 生成日 | trial src: 2026-10-26(同日)。`run01_prod`・`v1cand`(Algieba本文1のみ): 過去日 | 2026-10-26 | trial src=同日。過去日分は**感度分析で除外**し、Algieba本文1は同一セッション対照4 takeを追加(DESIGN_01 §5-1) |
| Adv attempt JSONのinstruction_text | 未記録(None) | 未記録(None) | shaで直接比較不可→Style文shaは`settings_*.json`と`build_spec`の一致で代替確認 |

## 採否
- **採用(主解析に使用)**: Algieba 39 sample(前回trial 20 + run01_prod 11 + v1cand 12 − fallback除外後の main 数は集計表のn)、Schedar 19 sample。route=`minimal_fallback`(Std、Style簡略化)の4 sampleは別条件のため除外し、集計で件数を明示。
- **不採用**: Zephyr(女性。ユーザー指示で比較対象外)。
- **条件**: Voice名・生成日以外の条件が一致することを上表で確認(artifact上の直接一致: 本文sha・Style sha・モデル・route・Std instruction sha)。未確認事項: 過去日のrun_01 attempt生成時のバックエンド内部状態(モデル重みの更新有無)。→ 感度分析「過去日再利用を除外」と同一セッション対照で影響を開示する。
