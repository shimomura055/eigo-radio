# AUDIO_QA_04: 委任_10 V1再生成(言い換え案B)の正式Gate結果

証跡: `er110_output/family_y_persona_trial_01/audio/it3/{b1b,a2}/audit/{tts_generation_results,review_lock_state,y_style_profile_gate}.json`、`.../audio/it3/raw_usage_log.jsonl`。言い換え内容=`V1_REWRITE_DIFF_01.md`。V1以外の全segmentは本文不変のため`_generate_or_reuse`で再利用(AUDIO_QA_03.mdの正式OK結果を継承。再生成0)。Gate・閾値・HR Lockは無変更(本文のSHA変更により従来設計どおり新バージョン扱い=`er011_human_review_lock_01.py`冒頭のtext変更時無効化)。

## Advanced(b1b)full_story_part1(V1、Algieba)
| 試行 | ASR | Repetition QA | 結果 |
|---|---|---|---|
| 1 | NUMERIC_EQUIVALENCE_MATCH(asr_verified) | method A通過、method D'(短ラグ)run長0.47s(閾値0.6s、flagなし) | **OK(1テイクで確定)** review_lock=RESOLVED/OK、cumulative_tts_attempts=1 |
- 旧: 4試行で未確定(D'境界flag 0.62/0.60/0.63s、ASR can/could)。言い換え後は1テイクでPASS(正規経路。fallback不使用、`instruction_type=english_style_prefix_wide_margin`)。
- Y style gate: PASS(`y_style_profile_gate.json`)。Assembly: OK 342.07秒 `.../b1b/assembled/Family_Y_Persona_Trial_B1_IT3.wav`。

## Standard(a2)full_story_part1(V1)
| 試行 | 経路 | ASR | Repetition QA / 結果 |
|---|---|---|---|
| 1 | 標準 | NORMALIZED_MATCH | method D' flagged: run長0.67s、time_a 6.58s、lag 1.45s -> 再試行 |
| 2 | 標準 | TRANSCRIPT_STYLE_NORMALIZED_MATCH | method D' flagged: run長0.64s、time_a 31.53s、lag 1.6s -> 再試行 |
| 3 | minimal_fallback(代替指示) | primary=NORMALIZED_MATCH(「the school」を「school」と転写)、secondary(Azure)=TRUE_CONTENT_MISMATCH -> unified judge NG_BOTH(secondary_not_accepted) | 上限3回到達 -> **HUMAN_REVIEW_REQUIRED / STOPPED** |
- 4テイク目は実施していない(委任上限)。Std V1は未確定のため通し音声は未組立(Assembly対象外)。HR Lock・Y style gateは迂回していない。
- 原因仮説(観測値): Stdは語数176・17文で短文が連続し、D'が「語句が約1.5秒間隔で似る区間」を境界値(0.64〜0.67s、閾値0.6s)で再びflag。flag位置は6.58s(文頭付近:`I get home late…Fighting about phones…`)と31.5s(`Her words left me speechless. A promise is a promise…`付近、語数比の推定)でテイクごとに異なる。言い換え後のAdvは0.47sで通過、Stdは通過せず。Adv V1(長文・従属節多)よりStd V1(短文の連続・反復語`I`・`phone(s)`)のほうがD'が反応しやすい可能性。3回目のfallback(代替指示)ではRepetition QAが走らず、ASRのsecondary不一致で止まった。
- 次の一手(いずれもFable判断): A=人間がStd V1のテイク(`narration/full_story_part1.wav`の最終テイク、または`narration/attempts/`)を聴いて承認(API 0)。B2=Std V1の英文をさらに平易化・文の結合で変更し再生成(委任_10の上限と「Bが不成功なら再試行せず停止」に反するため未実施。見込み: 改善見込み中〜低、費用約3〜5円)。
