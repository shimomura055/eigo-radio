# USER_EAR_CHECK_RESULT_01 (FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01 / OPEN-444 / UDR #148)

記録日: 2026-10-22。費用0円・API呼出0・Production/Prompt/仕様変更なし・新Trialなし(記録のみ)。
ユーザー原文(逐語): `docs/pm/delegation_log/2026-10-22_FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01_EAR-CHECK_USER.md`

## 1. 既存ASR証拠とユーザー試聴結果の対応表
出典: `mapping_01.json`(items/take_part)、`user_test/byus_kp_asr_listen_01/index.html:19-20`、`KP-THREE-ASR-MAJORITY-PRODUCTION-01/stored_audio_reeval_01.json`(take_part_good / take_part_problem_13)。Whisperは保存済みlocal faster-whisper(small/medium)。

| 音声 | Store key / sha256 | 音声ファイル | Primary(OpenAI) | Secondary(Azure) | Whisper small / medium | 3-ASR多数決 | ユーザー試聴 |
|---|---|---|---|---|---|---|---|
| think up | master_audio_id `55cd6f202c8ff584b563b41e` / wav sha `694c0962...f48e9` | `er006_output/master_audio_store_01/audio/55cd6f202c8ff584b563b41e.wav`(ページ: `audio/kp_1_think_up.mp3`) | 「ThinkUp.」PASS | 「Think.」NG | 「Think up.」PASS / 「Think up.」PASS | 2/3 PASS | PASS(正しく聞こえる) |
| blurt | master_audio_id `0c527a56ad772429e5d2ffa8` / wav sha `2ecabcfa...2ac68` | `er006_output/master_audio_store_01/audio/0c527a56ad772429e5d2ffa8.wav`(ページ: `audio/kp_6_blurt.mp3`) | 「Blur.」NG | 「Blurt.」PASS | 「Blurt」PASS / 「Blurt」PASS | 2/3 PASS(3系統中Primaryのみ語末tなしと転写) | t音が聞こえない・発音に懸念 |
| take part A(現行採用・合格音声) | master_audio_id `0714639d351b47c34b4d4103` / wav sha `e4405501...0466f`(`e4405501`) | `er006_output/master_audio_store_01/audio/0714639d351b47c34b4d4103.wav`(run内 `.../manga_ai_chat_byus__run_byus_01/a2/narration/kp4_en.wav`、ページ: `audio/take_part_PASSED_e4405501.mp3`) | 「Take part.」PASS | 「Take part.」PASS | 「Take part.」PASS / 「Take part.」PASS | 3/3 PASS | PASS |
| take part B(旧問題音声) | Store外(`er088_output/...` の1ファイル) / wav sha `675cd6b1...72186` | `er088_output/kp_asr_dual_pass_trial_01/kp4_en.wav`(同sha複製 `.../a2/narration/kp4_en.invalid_20261021.wav`、ページ: `audio/take_part_PROBLEM_old_675cd6b1.mp3`) | 10回中 Take tart x6 / Take part x3 / Take heart x1(Production再判定3回は全て Take tart) | 「Take Tart.」x13(10+3)全NG | small「Take Tarte.」NG / medium「Take Tart.」NG(保存済み2026-10-21も Take Tarte.) | 全13試行NG(Primary PASSの3試行もWhisper NGで多数決NG) | NG |

## 2. blurtの「2/3 ASRがPASS」裏付け
一致。mapping_01.json の blurt: Primary「Blur.」pass=false、Azure「Blurt.」pass=true、Whisper small/medium「Blurt」pass=true。OPEN-444本体記載(Primary「Blur.」NG/Azure PASS/Whisper PASS)とも一致。差異なし。補足: 旧dual判定(Primary+Secondary両方PASS必須)ではNG_DUAL_PRIMARY_NOT_PASS、承認済み3-ASR多数決ではPASSに変わる音声。think upも同様(旧NG_BOTH→多数決PASS、人間はPASS)。

## 3. ユーザー結論(2026-10-22)
- think up: PASS。take part A(現行採用音声): PASS。take part B(旧問題音声): NG。blurt: 語末のt音が聞こえず発音に懸念。
- 承認済みの3-ASR多数決方式を変更・撤回しない。Family X/Z Production配線は承認済み仕様のまま継続。新Trial・品質基準変更・追加のユーザー判断要求は不要(ユーザー明示)。

## 4. 品質知見
- blurt(byUs): ASR多数決PASS(2/3、Azure・Whisperが「Blurt」)でも、人間には語末tが聞こえなかった事例。多数決方式の限界を示す品質上の知見として記録する(仕様変更・Trial・UDR不要)。
- take part: 旧問題音声(sha 675cd6b1)はNG、現行Production採用音声(sha e4405501)はPASS。現行採用音声が正しいことの人間確認。旧問題音声は多数決で全13試行NG(既存結論どおり)。
- think up: 旧dual判定でNG_BOTHだった音声が、人間でも正しく聞こえ、多数決PASSの妥当性を支持。
