# VERIFICATION_01: 『告げ口心臓』Std KP#2差替え(旧`catch of one's lantern`→新`louder and louder`)

## 再生成内訳・費用(実測)
- LLM: KP固定選定→canonicalization(Luna)×(失敗周回: `growing louder and louder`のINVALID 3周=約0.4円)+成功周回、gloss再整合、Redundancy QA、解説(Adv側は再利用): run_chunk_01 cost_log差分
- TTS+ASR: 3 clipのみ生成(kp1_en[`make one's`→`make someone's`、canonicalizationの語形が現行Adv規約`someone's`に揃った副作用]、kp2_en、kp2_ja)。その他の本文・KP clipは reuse(reused=True)。
- run実費: 累計16.6657→18.0874円 = **+1.42円**(Cap 10円内)。日次(JST 2026-10-25)972.57円(<1,000)。
- 起動: 失敗1(growing louder and louder INVALID、再起動ではなく固定語句の修正)+kp成功1+tts~assemble 1+pages/page_verify 1 =4起動(各起動>=150秒間隔)。

## 検証
| 項目 | 結果 | 根拠 |
|---|---|---|
| 新KPが本文に逐語存在 | PASS | std.md S44 "growing louder and louder"内、occurrence_count=1 |
| 5語以下 | PASS | 3語 |
| 他KPと重複なし | PASS | Redundancy QA PASS(key_phrases/a2/keyphrase_redundancy_qa.json) |
| gloss | PASS | 「だんだん大きく」ALIGNED、qa_overall PASS |
| KP音声ASR一致 | PASS | kp2_en "Louder and louder." / kp2_ja "だんだん大きく" / kp1_en "Make someone's blood turn cold." 全てstatus OK、attempt1 |
| Gate | PASS | a2/audit/gate_result_04C.json shared_gate=PASS、HR無し |
| 公開ページ表示 | PASS | standard.htmlに`louder and louder / だんだん大きく`、KP表2列 |
| 旧KP文字列が公開物に0件 | PASS | user_test/family_z_tell_tale_heart_01 に `catch of one`/`人のランタンの留め具` 0件(本文中の`catch of my lantern`は物語本文として残る) |
| Advanced/Part 1無変更 | PASS | advanced.html・audio_advanced差分0 |
| page_verify | PASS(console_errors 0、plays_failed 0、http_ge400 0) | page_verify_local.json。seek_ok_all=falseは差替え前と同一(既存の計測仕様) |
| Pages 200 | push後確認(RESULT_PACKET参照) | |
| 旧版の退避 | 完了 | scratchpad backup+git履歴 |

## Status
USER_LISTENING_PENDING(ユーザー最終試聴待ち。PASSは先取りしない)。
