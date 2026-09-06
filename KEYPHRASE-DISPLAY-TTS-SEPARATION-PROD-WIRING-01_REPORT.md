# KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01

管理ID: KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-AND-JA-GLOSS-DIAGNOSTIC-01 /
サブタスク A+B(Production配線)

対象: Key Phrase日本語glossの「表示用/TTS用分離」(仕様A)と「数値
placeholder型の選定側回避」(仕様B)。ユーザーが2026-09-06に
`APPROVED_FOR_PRODUCTION`と正式決定した2件を、Production正式初回経路へ
`PRODUCTION_WIRED`まで配線した。

## 0. 全Checklist完了サマリ

| チェック | 結果 |
|---|---|
| Production正式初回経路への実装(Trial/DEV専用のままにしない) | 完了(下記1・2節) |
| Dangling Reference Check | 完了・問題なし(下記6節) |
| 回帰(既存+新規) | 完了・PASS(下記3節) |
| プロジェクト全体回帰 | 完了・既知の無関係failureのみ(下記3節) |
| Runtime evidence(Standard同期) | 完了・取得済み(下記4・5節) |
| SSOT更新 | 完了(下記7節) |
| approved specとProduction挙動の一致確認 | 完了(下記8節) |

**PRODUCTION_WIRED可否の自己判定: 可(仕様A・仕様Bとも)。**

## 1. 仕様A(表示用/TTS用分離)の実装

- **選定Prompt**(`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`、
  A2/B1共有): 規約Bのgloss側「日本語グロスには「～」「〜」「…」のような
  プレースホルダー記号を一切使わないでください」を撤回し、「日本語グロスは、
  辞書的な表記として自然な範囲であれば「～」「〜」を使ってもかまいません
  …ただし「…」のようなプレースホルダー記号はこれまでどおり使わないで
  ください」へ書き換えた。規約A(漢数字)は無変更。canonicalization prompt
  (`b1_p2_keywords_canonicalization_prompt_template.txt`)側のkey_phrase
  (英語)に対する「～」「〜」「…」禁止は無変更。
- **Schema拡張**(`er003_key_words_canonicalization.py`): 新規関数
  `convert_display_gloss_to_tts_text(display_gloss)`(正規表現
  `(?:^|(?<=、))[～〜]` → 「なになに」、LLM不使用、決定論的)を追加。
  `merge_canonicalization_result()`が返すitemへ、既存`japanese_gloss`
  (表示用、無変更)に加え新フィールド`japanese_gloss_tts`(TTS用)を追加した。
- **TTS呼び出し**(`er003_v1_n3_01_tts_generate.py`、B1/A2両方の正式経路):
  新規関数`resolve_key_phrase_ja_gloss_tts(item)`を追加(`japanese_gloss_tts`
  があればそれを使用、無ければ表示用`japanese_gloss`から同じ規則でその場
  導出するfallback、`japanese_gloss_tts_fallback_derived`として記録)。
  `generate_b1_segments()`/`generate_a2_segments()`のKey Phrase日本語
  meaning生成部を、`generate_charon_japanese_with_reading_safety()`/
  `generate_a2_japanese_with_reading_safety()`へ渡すテキストを表示用から
  TTS用へ切替、`expected_substring_ja()`もTTS用テキストから計算するよう
  変更。結果dictへ`display_gloss`(表示用)を追加記録し、TTS用と表示用の
  両方をartifactへ残す。
- **既存gate**(`er003_audio_tts_asr_safety.detect_gloss_placeholder_notation`)は
  無変更。変換対象外(数値placeholder型・範囲表記・「…」)は無変換のまま
  従来どおりゲートでブロックされる。

## 2. 仕様B(数値placeholder型の選定側回避)の実装

選定Prompt(`b1_p2_keywords_l_prompt_template.txt`)へ「『ソロ旅行を～％と
する』のように、数値を補わないと意味が成立しない句・日本語グロス(数値の
穴埋めを必要とする不完全な表現)は選ばないでください。それ単体で意味が
成立する句・グロスを選んでください」の1文を追加した。canonicalization
promptは`japanese_gloss`を生成しないため変更していない。retry(Key Phrase
Set Redundancy QA)でも同じ選定Promptが使われるため整合する。

## 3. 回帰

- 新規単体テスト18件全PASS: `er003_test_key_words_canonicalization.py`
  (`convert_display_gloss_to_tts_text`9件+`merge_canonicalization_result`の
  `japanese_gloss_tts`出力3件)、`er003_test_v1_n3_01_tts_generate.py`
  (`resolve_key_phrase_ja_gloss_tts`5件)、`er003_test_b1_p2.py`(規約B撤回
  確認1件[既存1件を置換]+規約B新設確認1件)。
- 既存Key Phrase canonicalization・選定Prompt・placeholderゲート・JA
  Validator・TTS retry関連の既存テストは全て無変化でPASS(125件、
  `er003_test_key_words_canonicalization.py`+`er003_test_v1_n3_01_tts_
  generate.py`+`er003_test_b1_p2.py`+`er006_kp5_canonical_bug_01_test.py`)。
- プロジェクト全体回帰(`run_project_regression.py`): collected=2103、
  2100 PASS・3 failed。残り3件は`git stash`で本タスクの変更ファイル
  (`er003_key_words_canonicalization.py`・`er003_test_b1_p2.py`・
  `er003_test_key_words_canonicalization.py`・`er003_test_v1_n3_01_tts_
  generate.py`・`er003_v1_n3_01_tts_generate.py`・選定Prompt)を除去した
  baselineでも同一の3件failure(`er003_test_p2j_investigate`のOPEN-77
  既知meta-test集計バグ、`er003_test_bad.FixtureTests.test_case_0`の
  意図的self-check fixture)が再現することを確認済み(本タスクと無関係)。

## 4. Runtime evidence(仕様A: 変換発火)

TTS Standard同期(`TTS_EXECUTION_MODE=STANDARD`)、Theme 2 B1
(Trial-12記事`er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/
b1b_run01/article.md`)を入力に、Production正式経路(`sc.run_key_phrases`
→選定・canonicalization・Key Phrase Set Redundancy QA、いずれも無変更の
Production関数を直接呼び出し)を1回実行(`er011_kp_display_tts_
separation_prod_wiring_01.py`)。

- 選定`KEY_WORDS_STRUCTURE_PASS`・canonicalization`CANONICALIZATION_PASS`・
  redundancy QA`REDUNDANCY_PASS`。選定5件(median/中央値、two different
  speeds/二つの異なる進み方、self-directed travel/自分主導の旅行、
  interest-led plans/興味に沿った計画、emerging preference/形成されつつ
  ある志向)はいずれも「～」「〜」を含まなかった(`natural_conversion_
  fired_in_selection=false`)。
- 選定結果内で自然発火しなかったため、既知gloss「～と完全には一致しない」
  (Phase 2 TrialでA2 rank5として実際に選定された値)を同じProduction関数
  経路(`resolve_key_phrase_ja_gloss_tts`→`generate_charon_japanese_with_
  reading_safety`)へ直接投入し発火を実証: TTS用テキスト「なになにと完全
  には一致しない」に変換、attempt1はASRが「〜と完全には一致しない」と
  記号読みしてTRUE_CONTENT_MISMATCHだったが、attempt2で「何々と完全には
  一致しない」とPHONETIC_MATCH・`verified=true`(既存retry cascade内で
  正常に解決、標準予算2回以内)。
- model_id=`gemini-3.1-flash-tts-preview`、`tts_execution_mode=STANDARD`を
  `raw_usage_log.jsonl`(公式cost logger)で確認。
- 選定5件全てのcanonicalization artifact(`keywords_canonicalized.json`)に
  `japanese_gloss`(表示用)と`japanese_gloss_tts`(TTS用)の両方が保存
  されていることを確認。

## 5. Runtime evidence(仕様B: 数値placeholder型のブロック)

既知gloss「ソロ旅行を～％とする」(Phase 2 TrialでB1 rank2として実際に
選定された値)を`convert_display_gloss_to_tts_text()`へ投入した結果、
変換対象外の位置(数値の直前)にある「～」は無変換のまま(「ソロ旅行を
～％とする」で不変)、`generate_charon_japanese_with_reading_safety()`へ
渡した結果`status=STOPPED`(`reason: canonical_textに未発話のplaceholder
記号が残っています: ['～']`)。TTS API呼び出し自体が発生していないこと
(wavファイル未生成、review_lock_state.jsonにもエントリなし)を確認した。

## 6. Dangling Reference Check

- 撤回した規約B旧文言(「日本語グロスには「～」「〜」「…」のような
  プレースホルダー記号を一切使わないでください」)は、現行の選定Prompt
  ファイルからは削除済み。リポジトリ内の残存箇所は(a)本タスクの新規
  test(`assertNotIn`で不在を確認するためのリテラル)、(b)Phase 2 Trial
  script(`er011_open117_keyphrase_display_tts_separation_trial_02.py`)の
  `_ORIGINAL_GLOSS_RULE_LINE`定数(当時のProduction文言を記録する
  historical record、Trial-only scriptでありProduction経路からは一切
  参照されない)、(c)過去タスクの保存済みruntime evidence artifact
  (`er011_output/kp_validator_numeric_homophone_gloss_production_
  wiring_03/attempt_*/selector_prompt.txt`、実行時点のスナップショット)
  のみで、いずれもProduction実行時には使われない。
- `japanese_gloss_tts`フィールドを参照する箇所(`resolve_key_phrase_ja_
  gloss_tts`)は後方互換fallbackを持ち、フィールド不在でもクラッシュしない
  ことをテストで確認済み(未実装フィールド前提のdangling referenceなし)。
- 選定Prompt・canonicalization Prompt・Production code(すべて本タスクで
  変更したファイル)の間で、フィールド名・関数名の不整合は無し(grep・
  regression・runtime evidenceで確認)。

## 7. SSOT更新箇所

- `CURRENT_SPEC.md`: 「Key Phrase」節の「日本語グロス(`ja_gloss`)の
  Prompt規約A/B」行へ規約Bのgloss側撤回を追記、新規行「Key Phrase日本語
  gloss 表示用/TTS用分離」「Key Phrase 数値placeholder型の回避(選定
  Prompt)」を追加(いずれも`PRODUCTION_WIRED`)。ファイル冒頭の「最終
  更新」チェーンにも要約を追加。
- `DECISION_LOG.md`: 新規エントリ
  `## KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01`を追加(背景・仕様
  A/Bの実装詳細・Master Audio Store確認・retry/fallback整合・回帰・
  Runtime evidence・状態・今回実施しなかったこと)。ファイル冒頭の「最終
  更新」チェーンにも要約を追加。
- `OPEN_ITEMS.md`: OPEN-117行を`RESOLVED / PRODUCTION_WIRED`へ更新
  (旧状態`VALIDATED`は履歴として保持)。日本語gloss自然さ(サブタスクC)は
  別Open Item候補として結果待ちである旨を明記。ファイル冒頭の「最終更新」
  チェーンにも要約を追加。

## 8. approved specとProduction挙動の一致確認

- 仕様A: 表示用glossの「～/〜」許容(規約B撤回)・TTS用フィールドの新設・
  変換規則(文頭/読点直後のみ)・TTS呼び出しがTTS用フィールドを使うこと・
  後方互換fallback・Master Audio Store非干渉、いずれもコード・
  テスト・Runtime evidenceで一致を確認した。
- 仕様B: 数値placeholder型を変換対象外のまま既存ゲートでブロックし続け、
  選定Prompt側でのみ回避誘導する設計を、コード(変換対象外のまま無変換)・
  Runtime evidence(実際にゲートでSTOPPED)で確認した。

## 9. Master Audio Store確認

`er006_audio_cost_pilot_02_shared_narration.py::ensure_key_phrase_english_
component()`のキーは`canonical_text=used_form`(英語Key Phraseそのもの)の
みであり、日本語gloss分離の影響を受けないことをコード再確認した。日本語
Key Phrase glossはMaster Audio Store非対象(`generate_charon_japanese_
with_reading_safety`/`generate_a2_japanese_with_reading_safety`は
Store経由ではなく都度生成)のため、cache identity設計との矛盾はない。

## 10. retry/fallback/regeneration整合

- 選定retry(Key Phrase Set Redundancy QA、最大2回)は選定Promptを経由する
  ため仕様A/Bとも自動的に一貫する。
- TTS標準/fallback retry cascade(`generate_charon_japanese_with_reading_
  safety`/`generate_a2_japanese_with_reading_safety`内部)は
  `resolve_key_phrase_ja_gloss_tts()`が解決した`japanese_gloss_tts`を
  受け取ってから動作するため一貫している。
- review_lock・Assembly側Audio Validation Gate・REGENERATE_APPROVED
  経路はいずれも無変更。

## 11. 表示側確認

player.html等の記事表示コンポーネントで`japanese_gloss`を表示に使う既存
Production固定コンポーネントは存在しない(表示は各Trial/Reportスクリプト
が都度生成するため、表示用フィールドをそのまま使い続けられることを
コード確認した)。

## 12. 今回実施しなかったこと

数値placeholder型の変換規則拡張(ゲート・変換対象範囲は無変更のまま)、
Batch TTSの使用、Theme 2の完成episode音声再実行(Key Phrase単体のTTS/ASR
evidenceのみ取得、Assembly・完成音声化は範囲外)、既存artifact(旧
`keywords_canonicalized.json`)の一括再生成(fallback導出により後方互換は
確保済み、遡及的な音声再生成は別タスクの判断)、B2レベルの選定Prompt
(`b2_key_words_production_l_prompt_template.txt`)への変更(指示範囲外)。

## 13. 証跡

- `er011_output/kp_display_tts_separation_prod_wiring_01/run_summary.json`
- `er011_output/kp_display_tts_separation_prod_wiring_01/b1b/key_phrases/keywords_canonicalized.json`
  (表示用/TTS用両フィールド)
- `er011_output/kp_display_tts_separation_prod_wiring_01/b1b/audit/kp_ja_tts_results.json`
- `er011_output/kp_display_tts_separation_prod_wiring_01/b1b/audit/forced_leading_tilde_conversion_result.json`
  (変換発火の実例)
- `er011_output/kp_display_tts_separation_prod_wiring_01/b1b/audit/numeric_placeholder_gate_check_result.json`
  (数値placeholder型ブロックの実例)
- `er011_output/kp_display_tts_separation_prod_wiring_01/b1b/audit/review_lock_state.json`
- `er011_output/kp_display_tts_separation_prod_wiring_01/raw_usage_log.jsonl`
  (model_id・tts_execution_mode)
- Key Phrase日本語gloss wav(試聴用):
  `file:///C:/Users/tensh/eigo-radio/er011_output/kp_display_tts_separation_prod_wiring_01/b1b/narration/kp1_ja_charon.wav`
  〜`kp5_ja_charon.wav`、
  `file:///C:/Users/tensh/eigo-radio/er011_output/kp_display_tts_separation_prod_wiring_01/b1b/narration/forced_leading_tilde_ja_charon.wav`
  (変換発火の実際の音声、「なになにと完全には一致しない」)

## 14. 懸念・未充足

- 選定5件には「～」「〜」を含むglossが自然には現れなかったため、変換発火
  の実証は既知gloss(Phase 2 Trial実データ)による直接駆動で行った(同じ
  Production関数経路を使っており、選定結果に含まれる場合と技術的な扱いは
  同一)。将来Theme 2以降の実記事で「～」を含む表示用glossが選定された
  際、追加確認は不要と判断するが、継続監視は妨げない。
- 日本語gloss自然さの主観評価(サブタスクC)は本タスクの範囲外のまま。
