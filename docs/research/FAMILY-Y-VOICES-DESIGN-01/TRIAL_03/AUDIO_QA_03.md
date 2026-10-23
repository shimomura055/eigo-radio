# AUDIO_QA_03: Trial_03(it3)音声のQA(正式Gate結果、clip別)

証跡: `er110_output/family_y_persona_trial_01/audio/it3/{a2,b1b}/audit/`(tts_generation_results.json・review_lock_state.json・y_style_profile_gate.json・run_summary_assemble.json)、`.../audio/it3/raw_usage_log.jsonl`。すべて**新規生成**(it2の音声は、本文が修正稿と一致しないため再利用しない。見出しのみ同文だが、Voice/style/ASR証跡の再検証を省く利得[約1円]が小さく、再利用判定のリスクに見合わないため新規生成)。
凡例: calls/retry=TTS呼出数/再試行数。ASR=最終ASR照合(EXACT_MATCH/NORMALIZED_MATCH等)。Repetition QA=method A(n-gram)+D'(短ラグ)の結果。

## Advanced

| segment | Voice | status | calls/retry | ASR | Repetition QA | Disfluency | 備考 |
|---|---|---|---|---|---|---|---|
| topic_intro | Charon | OK | 1/None | NORMALIZED_MATCH(asr_verified) | 未実施 | - | - / fallback=None / 新規生成 / 5.0s  |
| preview | Charon | OK | 1/None | EXACT_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=None / 新規生成 / 12.5s  |
| comment_1 | Charon | OK | 1/None | EXACT_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=None / 新規生成 / 29.3s  |
| comment_2 | Charon | OK | 1/None | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=None / 新規生成 / 7.1s  |
| voice_heading_1 | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 3.1s  |
| voice_heading_2 | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 3.5s  |
| voice_heading_3 | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 4.0s  |
| full_story_part1 | Algieba | STOPPED | 3/None | None | 未実施 | - | - / fallback=None / 新規生成 / 0s  |
| full_story_part2 | Zephyr | OK | 1/None | NORMALIZED_MATCH(asr_verified) | PASS | - | - / fallback=None / 新規生成 / 51.3s  |
| full_story_part3 | Schedar | OK | 2/None | NORMALIZED_MATCH(asr_verified) | PASS | - | - / fallback=None / 新規生成 / 49.7s  |
| full_story_part3_c2 | Aoede | OK | 1/None | NORMALIZED_MATCH(asr_verified) | PASS | - | - / fallback=None / 新規生成 / 41.8s  |
| in_one_line | Aoede | OK | 1/None | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=None / 新規生成 / 14.2s  |
| kp1_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 1.5s  |
| kp1_explanation | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=None / 新規生成 / 2.4s  |
| kp1_phrase_repeat | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 1.5s  |
| kp2_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 1.6s  |
| kp2_explanation | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=None / 新規生成 / 4.2s  |
| kp2_phrase_repeat | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 1.6s  |
| kp3_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 1.5s  |
| kp3_explanation | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=None / 新規生成 / 3.5s  |
| kp3_phrase_repeat | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 1.5s  |

- Human Review Lock: 発火: full_story_part1
- Y style gate(M3+Y追加検査): 未実行

## Standard

| segment | Voice | status | calls/retry | ASR | Repetition QA | Disfluency | 備考 |
|---|---|---|---|---|---|---|---|
| topic_intro | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - | - / fallback=False / 新規生成 / 5.4s  |
| japanese_title | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - | - / fallback=False / 新規生成 / 4.6s  |
| preview | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - | - / fallback=False / 新規生成 / 12.4s  |
| comment_1 | Aoede | OK | 1/0 | PHONETIC_MATCH(asr_verified) | 未実施 | - | - / fallback=False / 新規生成 / 33.9s  |
| comment_2 | Aoede | OK | 1/0 | PHONETIC_MATCH(asr_verified) | 未実施 | - | - / fallback=False / 新規生成 / 8.5s  |
| voice_heading_1 | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | 6%減速 / fallback=False / 新規生成 / 3.2s  |
| voice_heading_2 | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | 6%減速 / fallback=False / 新規生成 / 4.0s  |
| voice_heading_3 | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | 6%減速 / fallback=False / 新規生成 / 4.2s  |
| full_story_part1 | Algieba | OK | 1/0 | None(asr_verified) | PASS | - | 6%減速 / fallback=True / 新規生成 / 56.4s  |
| full_story_part2 | Zephyr | OK | 1/0 | NUMERIC_EQUIVALENCE_MATCH(asr_verified) | PASS | - | 6%減速 / fallback=False / 新規生成 / 55.9s  |
| full_story_part3 | Schedar | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | PASS | - | 6%減速 / fallback=False / 新規生成 / 53.0s  |
| full_story_part3_c2 | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | PASS | - | 6%減速 / fallback=False / 新規生成 / 43.5s  |
| in_one_line | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | 6%減速 / fallback=False / 新規生成 / 13.7s  |
| kp1_english | Aoede | OK | 1/0 | EXACT_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 1.1s  |
| kp1_japanese_meaning | Aoede | OK | 1/0 | PHONETIC_MATCH(asr_verified) | 未実施 | - | - / fallback=False / 新規生成 / 2.0s  |
| kp2_english |  | OK | None/None | None(asr_verified) | 未実施 | 実施 | - / fallback=None / 新規生成 / 0s (Master Audio Store再利用[同一phrase/同一voiceの既存検証済みclip]と推定) |
| kp2_japanese_meaning | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - | - / fallback=False / 新規生成 / 2.8s  |
| kp3_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | 実施 | - / fallback=False / 新規生成 / 1.5s  |
| kp3_japanese_meaning | Aoede | OK | 1/0 | EXACT_MATCH(asr_verified) | 未実施 | - | - / fallback=False / 新規生成 / 2.5s  |

- Human Review Lock: なし(全segment final_status=OK)
- Y style gate(M3+Y追加検査): BLOCK
- Assembly: status=BLOCKED_STYLE_PROFILE_GATE duration=None clipping=None peak=None out=None

## 人物1(V1・Algieba)の停止と原因仮説(Fable報告用)
| level | 試行 | ASR | Repetition QA | 結果 |
|---|---|---|---|---|
| Adv(b1b) | 1 | NORMALIZED_MATCH | method D'(短ラグ)flagged: run長0.62s>=閾値0.6s、time_a 36.53s、lag 0.88s(method D長ラグ・Aは通過) | 再試行 |
| Adv | 2 | NORMALIZED_MATCH | D' flagged: run長0.60s、time_a 37.84s、lag 1.19s | 再試行 |
| Adv | 3 | TRUE_CONTENT_MISMATCH(原稿の「can」[43語目、If I **can** say]をASRが「could」と転写。1語のみの差、Repetition QAは未実施) | - | 既存のLocal Rewrite recovery(単語置換1回)へ |
| Adv | 4(Local Rewrite recovery) | 「can」->「just」の単語置換版でNORMALIZED_MATCH | D' flagged: run長0.63s、time_a 21.89s、lag 1.05s | **HUMAN_REVIEW_LOCKED_RETTS_FAILED -> HUMAN_REVIEW_REQUIRED / STOPPED**(証跡=er011_output/local_rewrite_recovery/it3/b1b/local_rewrite_recovery_full_story_part1.json) |
| Std(a2) | 1 | TRUE_CONTENT_MISMATCH(原稿の「it」をASRが「i」と転写。1語のみの差) | - | 再試行 |
| Std | 2 | NORMALIZED_MATCH | D' flagged: run長0.60s、time_a 33.35s、lag 1.79s | 再試行 |
| Std | 3 | NORMALIZED_MATCH(asr_verified) | D' 0.56s(flagなし) | OKだが**minimal_fallback(代替指示)**で生成 -> Y style gate: `FINAL_STYLE_SHA_MISMATCH_NO_HINT`+`STD_FALLBACK_USED_OR_UNKNOWN` -> **BLOCKED_STYLE_PROFILE_GATE**(Std組立不可) |
- 原因仮説(根拠): V1は**7試行(Adv4[Local Rewrite recovery含む]+Std3)のうち6試行で何らかの停止**。Repetition QA method D'(短ラグ・スペクトル)の境界flagが4回(Adv 0.62/0.60/0.63秒、Std 0.60秒、閾値0.6秒)、ASRの1語差が2回(can/could、it/i)。他の本文segmentの試行数(cumulative_tts_attempts): Adv V2=1/V3=2/Tension=1、Std V2=2/V3=1/Tension=2(いずれも正式な形で3回以内にOK)で、V1だけが両levelとも正式な形で確定できなかった。flag位置はテイクごとに違う(語数比の推定: Adv 21.9秒=「in the charging basket in the living room」、36.5〜37.8秒=「I want her to… I don't want to yell…」、Std 33.4秒=「I had no answer. I want her to…」)。共通点は**短い機能語句が約1〜2秒の間隔で反復する区間**(in the … in the / I want … I don't want)。ASR照合は(1語差を除き)原稿どおり、method A(n-gram)は通過しており、実音声の重複(TTSの言い直し)ではない可能性が高い。OPEN-469と同系の偽陽性。V1は最も長く(Adv 181語/Std 176語、約51〜56秒)、境界flagや1語差の機会も多い。Phase B it2のV1もAdvで同系のflag(別の区間=命令文の連続)。単一の区間を直せば確実に通るとは言えず、直接の修復は成功保証なし。
- 修正案(未実施、Fable判断。詳細=V1_REPAIR_PLAN_01.md): 英語V1で反復する短い語句(in the…in the、I want…I don't want、I + 動詞の連続)の文頭・語順を変え、ASRで揺れやすい「If I can say, ...」の引用形を避ける。V1のみ再生成(両level)。
- 未検証: 実際に聴いて重複でないことの人間確認。区間の特定は語数比による推定(単語タイムスタンプなし)。
- 迂回していない: HR Lock・Y style gate・Repetition QAの閾値は無変更。Adv V1は再生成せず停止、Std V1はfallbackテイクのまま組立を保留。

