# EXISTING_SPEC_CHECK_01 (FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 委任_01 Phase 1、API 0・Production変更0)

原文: `docs/pm/delegation_log/2026-10-25_FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_USER.md`。調査日2026-10-25。

## 0. 重要な前提訂正(委任文との差分)

- **Advancedの実体は `b1b` ディレクトリ(Aoede本文・Charon補助)であり、`a2` ではない。** 委任文は『Advanced(A2)』と書いていたが、
  公開ページ `user_test/uk_train_speaker_playback_e2e_02/index.html` は `Standard(通し約307秒)` = a2(assembled 307.05秒) /
  `Advanced(通し約281秒)` = b1b(`b1b/run_summary_assemble.json` duration_seconds=280.84)であり、a2はStandard。
  `er019_family_x_audio_production_runner_01.py:1236-1252`のコメントも『Standard(A2)/Advanced(B1B)』。
  よって本TrialのA側は **`er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/b1b/`**(以下 `A_LEVEL_DIR`)。
  ユーザー原文『Advancedのみ』を優先して b1b を対象にした(a2はStandardの6%減速post-processを持つため別条件)。
- 本文3 segment の段落構成: `b1b/parts.json` `paragraph_count=10, boundary_i=4, boundary_j=7` → part1=4段落 / part2=3段落 / part3=3段落(=chunk 10本)。段落間は空行(`\n\n`)。

## 1. Family Aの音量調整・接続処理 一覧(「Family A」固有ではなく、A/B/C/X/Z共有のAssembly/audio層)

| # | 処理 | 実装(ファイル:行) | 仕様正本 | 現在の正式Production仕様か | 段落Chunkへの再利用 |
|---|---|---|---|---|---|
| 1 | 各TTS生成関数内部の前後無音trim(発話区間検出 `find_speech_bounds`、前後に安全マージン残置) | `er003_b1_p3u_audio.py:186,224`、呼出 `er003_v1_sing01_news_tail_fix.py:167`、マージン0.35秒 `:47` | CURRENT_SPEC:2133(『silence trim[各TTS生成関数内部]』) | はい(A実測の残置: part1 前0.24/後0.28秒、part2/3 前0.28/後0.32秒) | **自動で再利用**(各chunkを同じ生成関数で作るため。追加実装不要) |
| 2 | scalar RMS正規化 `compute_gain_for_target_rms(max_peak=0.95)`、target_rms=(Preview RMS+Part1 RMS)/2、各独立TTS出力へ個別適用、Previewのみgain=1.0 | `er003_b1_p9a_audio.py:459`、`er019_family_x_audio_production_runner_01.py:1623(apply_family_x_b1_gain)` | CURRENT_SPEC:2099 | はい(A実測 target_rms=0.09149、part1/2/3 gain=1.1026/1.2960/1.1873、part2 peak_after=0.907) | **再利用**(chunkごと同一関数・同一target_rms=0.09149) |
| 3 | mono24k→stereo48k `resample_poly` | `p9a:180` | 同上 | はい | 再利用 |
| 4 | segment間の固定無音(0.4/0.5/0.65秒、Aoede↔Charon 1.0/0.8秒) | `runner:1686(build_family_x_b1_timeline)`、`er003_v1_n3_01_assemble.py:50-52` | CURRENT_SPEC Audio Assembly節 | はい | 段落間には**定義なし**(本文partは1 segmentで間無音を挟まない) |
| 5 | 結合=`np.concatenate`のみ(crossfade/重ね合わせなし) | `er003_v1_n3_01_assemble.py:948(assemble_with_timeline)`、p9a冒頭:26『crossfade等の加工はしない』 | CURRENT_SPEC:2079『Dynamics不使用(scalar gainのみ)』 | はい | 再利用(クロスフェード等は導入しない) |
| 6 | 完成ミックス最終段ヘッドルーム安全弁(peak>0.98で全体一律scalar) | `assemble:982,985` | CURRENT_SPEC:2100 | はい(A: peak 0.92499、未発動) | 再利用(B全体の再組立で同じ関数を通す) |
| 7 | **独立TTS clipを同一story内で連結する承認済み先例**: clipごとにtarget_rms gain(`gs`)→ 次clipとの間に `sil(0.5)`(narrator→narrator)/`sil(0.2)`(話者交代)を挿入 | `er013_family_c_production_runner_01.py:665-670`(Family Zは `er063_family_z_audio_01.py:1722 build_z_sequence` 経由で同builderを利用、`:1743 run_assembly`) | Family C/Z PRODUCTION_WIRED | はい(C/Z) | **段落chunk接続の最も近い承認済み先例**(下記3) |
| 8 | `SECTION_JOIN_PAUSE_SECONDS=0.8`(P-series chunk結合用) | `er002_common.py:58,351(assemble_audio)` | `HISTORICAL`(P-series専用) | いいえ(凍結) | 使わない |
| 9 | A2のみ 6%減速post-process(atempo) | `er008_a2_postprocess_slowdown_01.py`、CURRENT_SPEC:2083,2133 | A2(Standard)限定 | b1b(Advanced)には**適用なし** | 対象外(b1bは減速処理を持たない) |
| 10 | 速度Gate | X/Yに『wav/原音長さ比』Gateなし(Zのみ `verify_z_speed_profile`) | `docs/research/SHORT-CLIP-SPEED-GATE-01/CP_CHECK_01.md` | Xは該当Gateなし | 新Gateは追加しない |

**現在の正式Production仕様(連結に関わる部分)** = 『各独立TTS出力を同一target_rmsへscalar gain(peak≤0.95)→ stereo48k → 固定無音を挟んで`np.concatenate` → 完成ミックス最終段ヘッドルーム弁』。
段落chunk接続への適用(DESIGN_01 §4): 独立TTS出力の単位=段落chunk、段落間無音=Family C/Z先例の**0.5秒**(B)。追加無音なし版(B0=参考)も同じ音声から無料で作る。

## 2. Family X Advanced(b1b)本文が現に適用している処理(A側の後処理一覧)

| 段 | 内容 | 関数(ファイル:行) |
|---|---|---|
| 入力整形 | `tts_safe_news_en(part全体)` → `_pnap_supply`(固有名詞供給、A実績 supply_applied=[]) | `runner:1003-1009`, `:880` |
| 重要事実 | `tts_safe_news_en`は**段落改行を半角空白へ畳む**(出力に`\n`なし)。**Aの入力は段落区切り情報のない1続き文**。段落ごとに掛けて' 'で連結すると全体適用と完全一致(test `test_tts_safe_news_en_is_paragraph_local`、3 part全て) | `er003_v1_n3_01_tts_generate.py::tts_safe_news_en` |
| TTS | `news_tail_fix.generate_news_narration_wide_margin`、model `gemini-3.8-flash-lite-tts`、voice Aoede、backend `speech_metadata_flash_lite`、mode STANDARD(raw_usage_log) | `news_tail_fix:63`、`runner:1009-1017` |
| Style | style_profile `fx_20261017` のFULL_STORY: 『Speak directly to one listener with warmth and a smile in your voice; calm, steady and reassuring, like a favorite morning radio host, while keeping the news clear and credible.』(WPM数値指定なし、速度指示なし)。`tts_generation_results.json`のstyle_prefixとstyle_base_sha256(3a680861e4d9…)で確認 | `er019_family_x_style_profile_01.py:186` |
| trim | 上記#1 | |
| ASR・Gate | primary OpenAI ASR(`gpt-4o-mini-transcribe`)→必要時Azure secondary、`evaluate_attempt_with_cascade`、`apply_repetition_qa_gate`(本文のみ`enable_repetition_qa=True`)、Connected Speech Equivalence(role=FULL_STORY)、固有名詞resolver、retry最大`PRODUCTION_MAX_TTS_ATTEMPTS=3` | `news_tail_fix:63-345`、`er011_human_review_lock_01.py:80` |
| 速度後処理 | **なし**(b1b) | |
| Assembly | #2〜#6 | `runner:2007近傍 stage_assemble_family_x_b1(:1794)` |

## 3. 21節 Existing Spec / Prior Trial Check Gate 分類

検索: `DECISION_LOG.md` / `DECISION_LOG_HISTORY.md` / `OPEN_ITEMS.md` / `OPEN_ITEMS_HISTORY.md` / `CURRENT_SPEC.md` / `docs/research/` / `er003_output/b1_p*`(キーワード chunk, 段落, paragraph, 分割, split, concat, crossfade, gap, Macrochunk)。

**分類: B(過去Trialあり・不採用/凍結) + 部分的にA(承認済みの連結先例あり)**。新規(C)ではない。

| 先例 | 内容 | 結論 | 本Trialとの関係 |
|---|---|---|---|
| ER-003-B1-P4D〜P6B(`CURRENT_SPEC.md:2052,2065,2074`、`er003_output/b1_p7a/A01/audio_validation.md:5-8,123`) | P-series: 日本語Full Storyを3chunk(P4D)/2-Macrochunk(P6B)で別TTS callにして結合。ユーザー試聴で**P6B不合格**: 『Macrochunk AとBで声質差があり接続が不自然』『独立したGemini TTS callを自然な連続ナレーションとして接続できなかった』。以降 **単一TTS call(chunk分割なし)** へ移行しN3以降の凍結仕様(`CURRENT_SPEC.md:2052`)。 | **不採用**(日本語・`gemini-2.5-pro-preview-tts`・Dynamics処理前のP-series) | 本TrialのBは『英語・`gemini-3.8-flash-lite-tts`・段落(意味の切れ目)単位・chunkごとRMS正規化・Z/C接続』で**条件が異なり**、無断再導入ではなく**ユーザー原文で明示された新Trial**。ただし『chunk間の声質差・接続の不自然さ』は過去の不採用理由そのもの → 評価の最重要観点にする(DESIGN §6)。Opus review論点(e) |
| Family C/Z story clip連結(`er013_family_c_production_runner_01.py:665-670`) | 独立TTS clipごとにRMS gain + narrator→narrator 0.5秒gapで連結(Production承認済み) | **A(承認済み・Production運用中)** | 接続方式として再利用(Bの本命) |
| `docs/research/FAMILY-X-COFFEE-ADVANCED-FULLSTORY-WPM-MEASUREMENT-01`系(`er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/`) | Advanced本文のWPM・ポーズ計測定義(-40dB/20ms、≥300/500ms無音) | 計測定義として再利用 | 速度計測 |
| `er057_coffee_tts_style_h_speed_03/04` ほか | Style文言による速度調整Trial(chunk化ではない) | 本件と無関係 | Styleはfx_20261017固定のまま |

過去不採用方式の無断再導入: **なし**(P-seriesの2-Macrochunkは日本語・別モデル・別接続。Fable/Opusへ論点として明示)。

## 4. 結論

1. 再利用する承認済み方式: (a)各TTS生成関数内trim(自動) (b)scalar RMS正規化(chunk単位、target_rms=A値0.09149固定) (c)C/Z先例の段落間0.5秒gap (d)`np.concatenate`のみ・crossfadeなし (e)ヘッドルーム弁 (f)A全体=B全体の同一組立(本文3 segmentのみ差替え)。
2. 新しい音声加工は導入しない(EQ・コンプ・独自crossfade・独自LUFS なし)。
3. 注意点: ①Aの入力は段落改行が畳まれた1続き文 → Bは同じテキストを段落で切るだけ(整形差なし)。②chunkごとのpeak上限0.95で、gainが頭打ちになるchunkはRMSがtargetに届かない(A part2でもpeak_after=0.907)→ chunkごとのpost-RMSを必ず記録。③『ASR一致・Repetition QA・Connected Speech』のrole適用は `segment_id` が正確に `full_story_part{1,2,3}` であることに依存(`er020_tts_retry_local_rewrite_01.py:resolve_narrative_role`)→ DESIGN §3の出力dir構造で担保。④A側 `b1b/audit` 等のProduction dirは読み取り専用。
