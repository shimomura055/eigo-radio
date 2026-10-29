# ARTICLE_PICK_01(END-USER-LISTENING-PAGE-PROTOTYPE-01 委任_01a、2026-10-29)

## 結論
- **主記事(Std/Adv切替・全機能の検証用)= AI島「島はリセット!でもAIには『攻略メモ』がある」(Family X、Std A2 + Adv B1B)**
- **補助記事(Grammar 1件表示の検証用・Advのみ)= 月のしわ「月のしわ、8,900本超!その奥に潜む『岩の上着』の秘密」(Family X reselect、Adv B1Bのみ)**

## 選定理由(全Family X完成ページを user_test/*/index.html で機能スキャン、スキャン script=scratchpad scan.py)
| 記事 | Std | Adv | Preview | Comment1-4 | In One Line | KP+本文ハイライト(data-hl) | Grammar採用件数 | 状態 |
|---|---|---|---|---|---|---|---|---|
| AI島 `user_test/family_x_ai_island_form_01/` | 完成 | 完成 | あり | あり | あり | あり(lk1/lk2/lk3、Std5/Adv5) | **0件(Std/Adv両方。ユーザー正式決定 2026-10-27 USER_03 §1-A で0件確定)** | **公開済み(FX-AI-ISLAND-FINAL-PUBLISH-01 ACCEPTED、記事単位APPROVED_FOR_PRODUCTION、commit 9a2fb4b52)** |
| 月 reselect `user_test/family_x_moon_shrinking_reselect_01/` | **未完成(M3 Gate停止、ページ未収載)** | 完成 | あり | あり | あり | あり(11) | **1件(疑似分裂文)** | ユーザー最終試聴待ち |
| Word Gacha / Paycheck / Moon_02 / Prix / Tesla / Coffee | 完成 | 完成 | あり | あり | あり | なし(旧形式、data-hl 0) | 0件(Grammar節自体なし) | 旧形式 |

- 「Std/Adv両方完成 かつ Grammar≥1」のFamily X記事は**存在しない**(AI島は両レベル0件確定、月はAdvのみ1件)。委任文の「Grammar採用1件以上」は単一記事では満たせないため、2記事構成にした(判断候補ではなく承認範囲内の自己解決=B。理由: ユーザー原文§3「対象レベルのみ」「機能・項目は実際の承認済み仕様に合わせる」)。
- 主記事にAI島を選ぶ根拠: Std/Adv両完成・公開済みで音声が最終版(sha固定)、最新のChunk TTS(paragraph chunk)・KP本文ハイライト(lk1-3)・Comment Z方式C3・Preview・In One Lineを全て備え、Grammar節の「0件」表示状態(0件非表示へ変更中)を実データで検証できる。
- 補助に月Advを選ぶ根拠: Grammar 1件(`items[0]`: id=g33c163c321 「疑似分裂文」)の表示実データとして唯一。同期データも生成する(Adv約314秒、ASR費用は軽微)。
- 注意: 月Std版は未完成(音声segmentはあるがassemble未)。ページ公開版は触らない。

## Asset一覧(全て既存・改変しない。repo相対path)
### 主記事 AI島
- run_dir(音声生成・assemble): `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/{a2,b1b}/`(a2=Std、b1b=Adv)
- run_dir(本文生成): `er019_output/ai_island_temple/run_form_prod_01/{a2,b1b}/`(`article.md`・`parts.json`)
- 公開ページ(正本の表示): `user_test/family_x_ai_island_form_01/index.html`(公開URL=https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_form_01/index.html)
- mp3(公開済み): `user_test/family_x_ai_island_form_01/audio/ai_island_temple_standard.mp3`(通し327秒)・`ai_island_temple_advanced.mp3`(309秒)、segment別 `audio/std_00..22.mp3`(23本)・`audio/adv_00..21.mp3`(22本)
- segment時間: `<run>/{a2,b1b}/audit/timeline.json`(part/start_seconds/duration_seconds。全編内の開始位置)、`audit/chunk_tts_assembly_*.json`(`part_start_in_episode_s`・`gap_offsets_in_part_s`・`chunk_samples`)、`audit/tts_generation_results.json`(segmentごとのtext・duration・ASR転写 asr_text)
- 本文: `parts.json`・`article.md`・`{a2,b1b}/a2_support_texts.json`/`b1_support_texts.json`(Preview/Comment1-4/In One Line等)
- KP/Word: `<run>/{a2,b1b}/key_phrases/{confirmed_selection.json,kp_selection_final.json,kp_general_explanations.json,vocab_confirmed.json,kp_source_sentence_ja.json}`
- Grammar: `<run>/{a2,b1b}/study_text/{confirmed_grammar.json,grammar_explanations.json,part2_grammar_sentence_structure.md}`(Std/Adv ともitems=[]、presented_ids 2件・max_select 1、ユーザー0件確定)
- Vocabulary: `<run>/{a2,b1b}/study_text/part1_vocabulary_expressions.{json,md}`
### 補助記事 月(Adv)
- run_dir: `er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/b1b/`(同上構成。Grammar=`b1b/study_text/confirmed_grammar.json` items 1件)
- 本文: `er019_output/moon_shrinking/run_reselect_01/b1b/{article.md,parts.json}`
- 公開ページ(候補): `user_test/family_x_moon_shrinking_reselect_01/index.html`、mp3 `audio/moon_shrinking_advanced.mp3`(314秒)・`audio/adv_00..21.mp3`

## segment構成(例: AI島Std、timeline.jsonより。Advも同型でKP=英語+英語解説、Comment/Previewは英語)
Intro / Welcome / Topic intro(英) / Japanese title / Notification 1 / Preview intro / Preview / Notification 2 / Key phrases intro / KP1-3 / Notification 3 / Full story intro / Comment1 / Full Story Part1(3 chunk) / Comment2 / Part2(2 chunk) / Comment3 / Part3(3 chunk) / Comment4 / In One Line / Outro。Stdの Preview・Comment・Japanese title は日本語、Advは英語。

## 同期データ(追記、委任_01a C項、2026-10-29)
- 場所: `docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync/std/`(AI島Std)・`sync/adv/`(AI島Adv)・`sync/moon_adv/`(月Adv)。各dirに `<part>.sentences.json`(topic_intro/preview/comment_1..4/full_story_part1..3/in_one_line、Stdはjapanese_titleも)と `index.json`・`VERIFY.json`。
- 時刻の基準: **そのsegment mp3の先頭からの秒**(`audio`フィールドが公開ページの`audio/std_NN.mp3`等を指す)。全編mp3再生中は `part_start_in_episode_s + start`(全31 segmentで相互相関により位置一致を検証済み)。
- 各文: `sentence_id/chunk_id/text(TTS入力)/display_text(公開ページの表示本文。文数が31/31 segmentで一致)/start/end/confidence/source/asr_raw`。
- 使い方: 現在文=`start<=t`の最後の文。文間の無音(0.08〜1.2秒)は直前文のハイライトを保持し次文の`start`で切替。詳細=`SYNC_METHOD_01.md`。
