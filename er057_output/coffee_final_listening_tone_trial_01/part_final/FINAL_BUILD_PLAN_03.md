# FINAL_BUILD_PLAN_03(委任_03、2026-10-12、Trial専用・Production非経由)

管理ID: FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_03。ユーザー選択(2026-10-12)はCoffee最終試聴版への採用候補であり、全記事共通Styleの正式採用ではない(`APPROVED_FOR_PRODUCTION`にしない)。

## 0. 事前確認で判明した、依頼前提との差(要報告)
1. **StandardとAdvancedでKey Phraseが異なる**(`keywords_canonicalized.json`実測): Standard=`raw bean / push prices up / take time / right away / on a regular basis`、Advanced=`lag / price tag / show up / come down / come with`。委任_01Bで生成したK2×5はStandardの5フレーズ分のみ。依頼文の「K2×5(両レベルKP英語)」は**Advancedには当てはまらない**。Advanced KP英語へのK2適用には新規TTS 5 call(短フレーズ、概算約JPY0.3)が必要だが、本委任の指示範囲外のため**実装せず、Advanced KP英語は既存音声(K2未適用)で組み立てる**。K2適用は要判断事項として報告する(assemblerはK2差替えを受け付ける作りにしておく)。
2. 6%減速適用範囲(SLOWDOWN_SCOPE_01、既確定)=Standardの full_story_part1/2/3・in_one_line のみ。本Trialでは Standard part1/2/3(F5生成分)へ適用。in_one_lineは既存音声(既に減速済み)を再利用。
3. Production assembleはworktree(`eigo-radio-tone`)版と`main`版で `er003_v1_n3_01_assemble.py`・`er003_b1_p9a_audio.py`が完全同一(diff 0行)。`er019`runnerのgain/timeline関数はmain版(`apply_family_x_a2_gain`等、純関数)を呼ぶ(差分は委任_06のfallback style配線のみで、assemble/gain/timelineと無関係)。

## 1. role別 構成表
由来: **T**=Trial生成済み音声(再利用、委任_01A/01B) / **P**=既存承認音声(Production run dir、read-only、再利用) / **R**=本委任でF5再生成。

| role | Standard | Advanced | 適用Style(Prompt) |
|---|---|---|---|
| 共通Intro A(Welcome) | T: part_AEF/raw/A5.wav(Charon) | 同左 | A5 |
| 共通Intro B(Preview intro) | T: B5.wav(Charon) | 同左 | B5 |
| Intro/Notification1-3/Outro(固定mp3) | P(固定音源、TTSなし) | 同左 | - |
| topic_intro | P(Aoede、既存) | P(Charon、既存) | 既存承認(変更なし)。※異音対処で1回再生成する場合あり(§4) |
| japanese_title | P(既存) | なし | 既存承認 |
| in_one_line | P(既存、減速済み) | P(既存、Aoede) | 既存承認 |
| Preview(英語/日本語) | T: part_BCD/raw/P2_preview.wav(日本語Aoede、P2) | T: part_AEF/raw/E1.wav(英語Charon、E1) | P2 / E1 |
| Comment 1-4 | T: P2_comment_1〜4(P2) | P: 既存(E2_UPBEAT、Charon) | P2 / 既存E2_UPBEAT |
| Key phrases intro / num_one〜five / full_story_intro | P(共通shell、Master Store由来) | 同左(Charonバリアント、既存) | 既存承認(変更なし) |
| KP英語(kp1〜5_en、初回・繰返し同一) | T: part_BCD/raw/K2_kp1〜5(Aoede) | **P: 既存**(K2未適用、フレーズ違いのためK2音声なし、§0-1) | K2 / 既存 |
| KP日本語意味(meaning_1〜5) | T: M2_kp1〜5 | なし(Advancedは英語解説) | M2 |
| KP英語解説(explanation_en) | なし | P: 既存 | 既存承認 |
| Full Story Part1/2/3 | **R: F5再生成 + 既存6%減速** | **R: F5再生成(減速なし)** | **F5**(F1.5逐語+末尾1文) |

## 2. Full Story再生成(R)の条件
- 原稿: 既存run dirの確定原稿 `a2/parts.json`・`b1b/parts.json` の `part1/part2/part3` を逐語使用(part2はLocal Rewrite前の元原稿、Attempt 4のLR文面`data from the United States`は不使用)。TTS入力は Production同様に `er003_v1_n3_01_tts_generate.tts_safe_news_en()` を適用(引用符除去・`two→2`等の数字語正規化・段落区切り→空白。全attempt共通の既存正規化、Style/文意は不変)。適用事実・入力text sha256は`generation_log_03.jsonl`に記録。
- Prompt: `part_AEF/prompts/prompts_F.md` の F5 style を逐語(F1.5逐語+" Tell it like a short story to a friend, with a relaxed flow and a lively, natural rhythm; not hurried.")。prompts_F.md/`er057_tone_trial_tts_gen_01.py` SPECS["F"]["items"]["F5"]との一致をassertし、sha256を記録。Standard専用の減速指示文(A2_SLOWER_PACE_INSTRUCTION)は付けない。
- 生成: model=`gemini-3.8-flash-lite-tts`(最新世代、現行Production同一固定)、voice=Aoede、`generate_content`+`Part.speech_metadata.style`(speech_metadata_flash_lite相当、Standard同期=DEV)。Trial専用script `er057_tone_trial_final_build_03.py`。Production runner・Master Store・manifest・telemetry・human_review_queue・attempt_history・cost_loggerは不使用。Production既存のtrim(NARRATION_BODY_TRIM_SAFETY_MARGIN 0.35s)・duration anomaly検知を同じ関数で適用。
- 内容QA: Primary ASR(`routing.transcribe`=`gpt-4o-mini-transcribe`)+既存validator `val.evaluate_attempt`(`er006_preprod_hardening_01_validation`、segment_id=role名でrole gating適用)+長さ条件(`len(asr)<=len(text)+15`)。Secondary ASR/cascade/Local Rewrite/minimal fallbackは使わない(`evaluate_attempt_with_cascade`はHuman Review queueへ書込むため不使用)。validatorがtelemetryへ追記する経路(`semantic_equivalence.append_telemetry_log`)はプロセス内でTrial専用ファイルへ差替え(Production telemetry不変)。
- NG時: **同一Promptで最大2回まで再生成**。それでもNGなら生成を止めてSTOP報告(候補音声保存)。
- Standardは生成OK後に`er008_a2_postprocess_slowdown_01.apply_a2_slowdown`(FFmpeg atempo=1/1.06)を適用し、前後duration/比率を記録。減速後wavにもPrimary ASRラベルを参考記録(再生成の根拠にはしない)。

## 3. 組立て
`er019`runnerの `apply_family_x_{a2,b1}_gain` / `build_family_x_{a2,b1}_timeline`(純関数)と `asm.assemble_with_timeline` / `asm.apply_headroom_safety_valve` をそのまま呼ぶ Trial assembler(`er057_tone_trial_final_build_03.py assemble`)。Gate(`verify_episode_audio_validation_gate`)はProductionのrun dir/audit書込形式に依存するため呼ばず、同等のチェック(peak/clipping/headroom/無音/長さ/timeline整合)を計算して記録。回帰確認として、**差替え前(既存音声のみ)で組み立てた結果が既存完成版wavとサンプル一致すること**を先に確認する。

## 4. 異音確認(ユーザー試聴結果に基づく)
FOCUS1=Std part3 coffee付近(part3はF5で再生成→新音声で再検証)、STD-02/STD-20=Std part2(同、再生成)、STD-24=Std Topic intro(**再利用segment**→元segment wav単体か assembled側かを切り分け、TTS由来なら既存承認Style(変更なし)で1回だけ再生成、上限3 segment)、STD-06=軽微(許容、part2に属し再生成される)。FOCUS2・他Std候補=なし。自動検知のみを根拠に再生成しない。

## 5. 費用概算(Standard単価、USD/JPY=160)
| 項目 | 見込み |
|---|---|
| Full Story TTS 6 call(合計約273秒、25tok/s×$6/M+入力) | 約JPY6.7 |
| Primary ASR(6 call + Std減速後3 call、gpt-4o-mini-transcribe $1.25/$5 per M) | 約JPY2.4 |
| retry余地(2 segment×1回再生成を想定) | 約JPY2.6 |
| 異音対処 topic_intro 1 segment再生成+ASR(最大3 segmentでも各JPY0.1程度) | 約JPY0.3 |
| **概算合計** | **約JPY12(全6 segmentが最大回数再生成した理論上限は約JPY22だが、実行時に累計JPY20超でSTOPするガードを置く)** |
判定: 概算合計JPY20以内のため実行可。累計がJPY20を超えた時点で停止する。
