# SLOWDOWN_SCOPE_01(委任_01C §3、read-only調査、費用JPY 0)

管理ID: FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_01C / 2026-10-11。調査のみ。Production・Prompt・Validator・Routing・SSOTは変更していない。本Trialでは減速処理(6% time-stretch)を一切変更しない。
読んだコードは Coffee run を生成した `feature/coffee-new-tone-01`(worktree `eigo-radio-tone`)版(mainとは `fallback_style_prefix` 等が異なる)。証跡は `evidence_snapshot/`(sha256付き `SNAPSHOT_MANIFEST.json`)。

## 0. 結論(確定)
1. 6%機械減速(`atempo=1/1.06`、`er008_a2_postprocess_slowdown_01.py` L24 `A2_SLOWDOWN_PERCENT=6.0`、L36-60)は **Standard(A2)の英語本文4 role だけ**に適用される: `full_story_part1`・`full_story_part2`・`full_story_part3`・`in_one_line`(`er019_family_x_audio_production_runner_01.py` L988-1008 → `n3_tts.generate_a2_segment_with_slowdown`(`er003_v1_n3_01_tts_generate.py` L197-268)→ `apply_a2_slowdown_postprocess`(L117-194))。
2. それ以外の role(共通Intro shell・topic_intro・japanese_title・preview・comment_1〜4・KP英語・KP日本語意味・Advanced全role)には**適用されない**。Advanced(B1B)は経路自体に減速処理が無い。
3. **例外(確定・要注意)**: Coffee Standard の最終 `full_story_part2.wav`(Attempt 4=Local Rewrite再TTS)は**減速後処理が適用されていない**(詳細は下記 §2、`ATTEMPT4_CONDITIONS_01.md`)。part1・part3・in_one_line は実測 5.87〜5.98% 減速済みで、part2 だけ生のTTS音声。
4. OPEN-270(減速後再検証・外側ループの是正・追加TTS)とは別件。本調査は適用範囲の事実整理で、OPEN-270の是正案・採否には触れず、何も変更していない。

## 1. role別 適用範囲表(Standard / Advanced)

| role | Level | 経路(コード行、worktree版) | 6%減速 | 根拠(runtime evidence) |
|---|---|---|---|---|
| Intro / Notification 1-3 / Outro | 両方 | 固定mp3(TTSなし) | なし | TTS非経由 |
| 共通shell: welcome / preview_intro / key_phrases_intro / full_story_intro / num_one〜five / point_explanation | 両方 | `shared_narration.ensure_all_shared_narration_a2`(runner L934)→ Master Store | なし | `*_original.wav` 無し。Standard/Advancedで shell 9件が sha256 完全一致(委任_09 `shell_sha_compare_09.txt`) |
| topic_intro | Standard | runner L943-952 `crosslevel_common.generate_english_segment_with_fallback`(減速関数を経由しない) | なし | `topic_intro_original.wav` 無し、`tts_generation_results.json` に `slowdown_applied` 無し(snapshot) |
| japanese_title | Standard | runner L954-969 `generate_a2_japanese_with_reading_safety`(日本語) | なし | 同上 |
| preview / comment_1〜4 | Standard | runner L971-984 `generate_a2_japanese_with_reading_safety`(日本語) | なし | 同上(`preview.wav` 13.28秒等、`_original` 無し) |
| **full_story_part1** | Standard | runner L988-1008 → `generate_a2_segment_with_slowdown` | **あり** | `slowdown_info`: src 38.49s → dst 40.793s(実測5.984%)、`full_story_part1_original.wav` あり |
| **full_story_part2** | Standard | 同上 | **経路上は対象。最終wavは未適用** | 最終wav 52.6秒は生TTS(LR再TTSの `trim_info.raw_duration 52.68`)。`full_story_part2_original.wav`(50.32秒、sha `654fe3a3…`)は**初回TTS(減速前)の残骸**で最終wavとは別音声(§2) |
| **full_story_part3** | Standard | 同上 | **あり** | `slowdown_info`: 45.63s → 48.356s(5.975%)、`_original.wav` あり |
| **in_one_line** | Standard | 同上(style=IN_ONE_LINE+減速指示) | **あり** | 5.88s → 6.225s(5.873%)、`_original.wav` あり |
| KP英語 kp1〜5_en | Standard | `_generate_key_phrase_segments_a2`(L1034-)→ `ensure_key_phrase_english_component`(Master Store/英語Component) | なし | `kp*_en_original.wav` 無し |
| KP日本語意味 meaning_1〜5 | Standard | 同上 `generate_a2_japanese_with_reading_safety` | なし | `_original` 無し |
| Advanced全role(topic_intro/preview/comment/full_story_part1-3/in_one_line/KP英語・解説・phrase_repeat) | Advanced | `generate_family_x_b1_segments`(runner L567-)。減速関数・`apply_a2_slowdown`の参照なし | なし | b1b/narration に `_original.wav` 無し。Gateの減速検査も `level == "A2"` 限定(`er003_v1_n3_01_assemble.py` L485) |

自然言語の「わずかに遅く」指示(`A2_SLOWER_PACE_INSTRUCTION`)は別物(TTS Promptへの指示)。runner `_role_style_slower`(L890-904)がStandardの FULL_STORY/IN_ONE_LINE のStyleにのみ連結する。6%機械減速とは独立で、Advancedのstyleには連結されない。

## 2. 実測: 発話速度と part2 の未適用(確定/推定の区分付き)
単語数/秒(原稿語数÷最終wav長。part2原稿はLR後165語、他は `parts.json`):

| segment | 語数 | 最終長(s) | 語/秒 | 生TTS長(s) | 生語/秒 |
|---|---|---|---|---|---|
| Standard part1 | 119 | 40.793 | 2.917 | 38.49 | 3.092 |
| Standard part2(最終=LR再TTS、未減速) | 165 | 52.60 | 3.137 | 52.68(生) | 3.133 |
| Standard part3 | 134 | 48.356 | 2.771 | 45.63 | 2.937 |
| Advanced part1 / part2 / part3(減速なし) | 132 / 179 / 152 | 41.72 / 51.64 / 44.21 | 3.164 / 3.466 / 3.438 | - | - |

- **確定**: part2最終wavに減速が掛かっていない根拠は3つ。(a) `local_rewrite_recovery_full_story_part2.json` の `retts_result` に `slowdown_info` が無く、`trim_info.raw_duration 52.68 → trimmed 52.6` の差は trim のみ(比例配分なし)。(b) 減速後処理は `generate_a2_segment_with_slowdown` が `status=="OK"` の結果にのみ適用する(`apply_a2_slowdown_postprocess` L117-125)が、LR再TTSは Azure forced で NG(`ASR_VALIDATION_UNCERTAIN`)のまま Human Review に送られ、OK にならなかった。(c) `part2_original.wav`(50.32秒)の sha256 は初回TTS `attempts/…attempt1_customf1837a73.wav` と一致し、最終wavとは別音声。
- **確定(Gateの穴)**: Audio Validation Gate の `_segment_missing_mandatory_a2_slowdown`(`er003_v1_n3_01_assemble.py` L232-290)を実データで呼ぶと part2 は `False`(=減速済み扱い)を返した(本調査で実行、snapshotの `tts_generation_results.json` と narration を使用、コードは変更せず)。原因は「`slowdown_applied` が無い場合、`_original.wav` が存在し 最終長/original長 が [1.03, 1.09] なら減速済みとみなす」弱い証拠規則に、初回TTSの残骸 `part2_original.wav`(比 52.6/50.32 = 1.0453)が合致したため。
- **確定(Gateの穴その2)**: `full_story_part3` は `A2_SLOWDOWN_TARGET_SEGMENTS`(`er003_v1_n3_01_tts_generate.py` L111-114、point_one_heading / point_two_heading / full_story_part1 / full_story_part2 / point_one / point_two / in_one_line)に**含まれない**ため、Gateは part3 の減速有無を一切検査しない(Family X新構造で追加された part3 がタプル更新されていない)。今回の part3 は実際には減速済み(上表)なので実害なし。
- **推定(聴感)**: Standard part2 は part1/part3 より約6%速い(減速なし)。ただし生TTSの速度自体が take ごとに 47.7〜52.7 秒(±5%)ばらつくため、聴感で6%差がどう効くかは人間試聴が必要(part2だけ速く聞こえるかは未確認)。
- ユーザー判断が必要な論点(本Trialでは実装しない): part2を減速するか(再処理=別TTSなし・音声ファイルへの後処理のみで可能だが、Part 2音声は最終承認済みとして扱わない方針のため今回は何も変更しない)。

## 3. 本Trialで変更していないこと
Production経路(`er019_*`、`er003_*`)・減速処理・Gate・Prompt・Style・Routingは無変更。`OPEN-270` の是正案(外側ループ、減速後検証の経路)は本調査の対象外で一切触れていない。
