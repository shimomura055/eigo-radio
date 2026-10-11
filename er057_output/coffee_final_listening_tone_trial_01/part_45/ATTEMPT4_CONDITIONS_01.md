# ATTEMPT4_CONDITIONS_01(委任_01C §4、read-only調査、費用JPY 0、新規TTS・Part 2再生成なし)

管理ID: FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_01C / 2026-10-11。ユーザー判断: Part 2音声は最終承認済みとして扱わない/簡略化したTTS PromptはNG。今回は調査のみ。
証跡(`evidence_snapshot/`、sha256付き): `a2/attempts/full_story_part2_*.json|wav`、`a2/local_rewrite_recovery_full_story_part2.json`、`a2/tts_generation_results.pre_adopt_backup.json`、`a2/part2_attempt4_adoption_record_09.json`。raw_usage_log・attempt_history・queueはworktree/main原本(read-only)。実送信Promptの再構成全文: `attempt4_reconstructed_prompt_01.txt`、検証結果: `attempt4_style_verify_01.txt`。

## 0. 結論
- **「Attempt 4」の呼称が資料により2種類ある(混同注意・確定)**: `part2_review`ページ/採用記録の「attempt 4」= **Local Rewrite後の再TTS(TTS通算5回目、最終 `narration/full_story_part2.wav`、sha `3231abd8…`、52.6秒)**。一方 `attempts/` フォルダの `full_story_part2_attempt4_minimalfallback.wav`(47.72秒)は part2_review 上の「attempt 3(fallback)」で、**別の音声**。ユーザーが採用承認したのは前者(LR再TTS)。
- Attempt 4(LR再TTS)は **「Local Rewriteによる原稿変更」と「minimal fallback関数経由の再TTS」の両方に該当する(確定)** が、**Promptは簡略化されていない(確定)**: Styleは通常のAttempt 1(標準経路)と**逐語で同一**(F1.5+減速指示、327字)、minimal instruction wrapperの文言は加わっていない。「minimal」は呼び出された関数名とログの固定ラベル(`instruction: minimal (not ENGLISH_STYLE_PREFIX)`、`er003_v1_repro01_main_generate.py` L622のハードコード文字列)だけで、**実送信Promptの簡略化は無い**。
- 原稿変更はLRによる**1箇所だけ**: `US data` → `data from the United States`。「2 numbers」「9 months」「引用符除去」はLRではなく、全attemptに共通のTTS入力正規化(`tts_safe_news_en`)で、Attempt 1〜3も同じ文面を読んでいる(委任_09記録の「差分: …two numbers→2 numbers、nine months→9 months、引用符除去」は LR由来の差分ではない)。
- **減速処理(6%)はAttempt 4に適用されていない(確定)**。詳細は `SLOWDOWN_SCOPE_01.md` §2。

## 1. 番号の対応(確定、raw_usage_log・attempts json・queue・review page build script照合)
| TTS通算 | JST(実時刻) | ファイル | part2_review表記 | 経路 | 長さ | sha256先頭 |
|---|---|---|---|---|---|---|
| #1 | 15:13:02 | `attempts/…attempt1_customf1837a73.wav` | 参考「減速前の初回」 | 標準(減速ループ1周目の標準1回目) | 50.32 | 654fe3a3 |
| #2 | 15:16:25 | `…attempt2_customf1837a73.wav` | attempt 1(標準・1回目) | 標準 | 49.07 | 12e53926 |
| #3 | 15:18:22 | `…attempt3_customf1837a73.wav` | attempt 2(標準・2回目) | 標準 | 48.75 | e97fd075 |
| #4 | 15:31:42 | `…attempt4_minimalfallback.wav` | attempt 3(fallback) | `_run_a2_minimal_fallback_attempt` | 47.72 | 3083ef48 |
| #5 | 15:35:18 | `narration/full_story_part2.wav`(最終) | **attempt 4(Local Rewrite後の再TTS)** | LR `_retts_fn` → `_run_a2_minimal_fallback_attempt` | 52.60 | 3231abd8 |
(#2〜#4の間に標準2回目後の10分cool-down 15:19:10〜15:29:10。TTS通算5回はOPEN-270既出の事象。)

## 2. 条件比較表(Prompt・Style・原稿・速度処理)
STYLE(通常=Attempt 1相当、STYLE_CHECK_09の定数): `FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]`(F1.5)+ `"\n"` + `A2_SLOWER_PACE_INSTRUCTION.strip()`。全文(327字):
> warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration.
> Speak at a slightly slower, relaxed pace than natural adult narration, while keeping the delivery smooth, conversational, and natural. Do not exaggerate pauses or sound instructional.

| 項目 | #1 減速前初回 | #2 標準1回目 | #3 標準2回目 | #4 fallback | **#5 Attempt 4(LR再TTS)** |
|---|---|---|---|---|---|
| 呼出関数 | `generate_narration_snippet_verified_strict`(標準) | 同 | 同 | `generate_english_component_minimal_instruction`(fallback) | 同左(LR `_retts_fn` 経由) |
| Style送信先 | `speech_metadata.style` | 同 | 同 | 同 | 同 |
| Style内容 | F1.5+減速指示(327字、json `instruction_text` に全文) | 同(同一) | 同 | 同(`fallback_style_prefix`で逐語。json `style_prefix`先頭200字・`style_source=approved_role_style:EN_FULLSTORY_F1_5`) | **同(逐語、327字)**。LR結果 `retts_result.style_prefix` 先頭200字一致、`style_source` 同上 |
| minimal wrapper文言 | なし | なし | なし | **なし**(`instruction_prefix = fallback_style_prefix`、L572-573) | **なし** |
| 発音hint追記 | なし | なし | なし | `hints_applied=False` | `hints_applied=False`(Styleへの追記なし) |
| TTS入力text | `tts_safe_news_en(part2)`(833字) | 同 | 同 | 同 | **LR後(853字)**: `US data`→`data from the United States` の1箇所のみ |
| モデル | gemini-3.8-flash-lite-tts | 同 | 同 | 同 | 同(raw_usage_log `model_id`) |
| Voice | Aoede | Aoede | Aoede | Aoede | Aoede |
| backend / 実行方式 | `speech_metadata_flash_lite` / Batch | 同 | 同 | 同 | 同 |
| API入力トークン(raw_usage_log) | 191 | 191 | 191 | 191 | 194(Styleは同一、textが+3トークン) |
| 6%減速 | 適用(後でASR UNCERTAINで破棄、`slowdown_attempts_log` 1件。減速出力は上書きされ未保存) | なし(減速はstatus=OK後のみ) | なし | なし | **なし** |
| 自動ASR | Primary NORMALIZED_MATCH → 減速後Primary-only再検証 UNCERTAIN | Primary TRUE_CONTENT_MISMATCH(showed→show) | Primary UNCERTAIN×2 + Azure TCM×2 | Primary PASS / Azure forced TCM | Primary PASS(NORMALIZED_MATCH) / Azure forced TCM(`raw bean`→`Robbing`) |
| 長さ(s) / 語/秒 | 50.32 / 3.26(減速前) | 49.07 / 3.34 | 48.75 / 3.36 | 47.72 / 3.44 | 52.60 / 3.14 |

- **確定**(コード+実行記録): Styleがf1.5+減速指示のまま・minimal wrapper無しは、(1) コード `er019` L997-1004 が標準経路の `style_prefix_override` と `fallback_style_prefix` に**同一文字列** `_role_style_slower("FULL_STORY")` を渡す、(2) `generate_english_component_minimal_instruction` L572-573 が `fallback_style_prefix` を逐語で `instruction_prefix` にする、(3) `attempt4_style_verify_01.txt`: attempt1 jsonの全文instruction_textと再構成327字が完全一致、fallback/LR各jsonの200字切詰め値も一致、(4) 入力トークン数 191(#1〜#4)/194(#5)で、短い `natural, clear, conversational`(main版のfallback style)に置き換わっていれば30トークン以上減るはずが減っていない、の4点で裏付けた。
- **確定**: `main` ブランチのコードには `fallback_style_prefix` 引数が無く、fallback/LR再TTSのStyleは短い `natural, clear, conversational`(`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`)に簡略化される(OPEN-274)。今回のCoffee runは `feature/coffee-new-tone-01`(委任_06のfallback style維持)で動いたため簡略化されなかった。もし main のコードでAttempt 4を再現すると、ユーザーが「NG」とした簡略化Promptになる。
- **再構成(推定でなく、コード由来)**: ログは先頭200字切詰め(`style_prefix[:200]`、raw_usage_logも200字)のため実送信全文は保存されていない。上記の全文Styleは、attempt1 jsonの全文instruction_textとの一致と、同一オブジェクトを渡すコード経路から再構成した。実際の `Part(text=…, speech_metadata=SpeechMetadata(style=…))` の構築は `er033_tts_flash_lite_backend_wiring_01.py` L254-276。
- **未確認**: (a) Style全文がAPIに送信された時点のバイト列そのもの(200字切詰めログのみ)。(b) #5のAzure `raw bean`→`Robbing` が真の読み違いかAzure誤認かは試聴判断待ち(ローカルwhisper smallも `robbing` と転写)。

## 3. 原稿の差分(全件、`attempt4_reconstructed_prompt_01.txt` に全文)
記事原稿 parts.part2(843字)→TTS入力(833字)[全attempt共通、決定論的]: `“`削除/`”`削除/`’`→`'`×2/`two`→`2`/`nine`→`9`/段落区切り`\n\n`×3→半角スペース。TTS入力→Local Rewrite後(853字)[#5のみ]: `US data`→`data from the United States` の1箇所のみ(`unchanged_ratio=0.9937`、全7 Gate pass、候補#2採用)。両方を通した最終差分は上記の和集合。
Local Rewrite の NG span 選定は Primary 転写 `us`↔`u s` を根拠にしており、実際にAzureがNGにした箇所(`raw bean(s)`)とは別の箇所を書き換えている(OPEN-274)。#5の書換え後文面でもAzureのNGは `raw bean`→`Robbing`(LRで変更していない箇所)で解消していない。

## 4. 「LRによる原稿変更」と「minimal fallbackによるPrompt簡略化」の切り分け
| 軸 | Attempt 4 |
|---|---|
| Local Rewriteによる原稿変更 | **該当(確定)**: `US data`→`data from the United States` |
| minimal fallback経由の再TTS | **該当(確定)**: `_retts_fn → _run_a2_minimal_fallback_attempt → generate_english_component_minimal_instruction` |
| minimal fallbackによるPrompt(Style)簡略化 | **非該当(確定・branch版)**。Styleは通常のAttempt 1と逐語同一。ただしmain版コードなら該当する(OPEN-274) |
| 6%減速 | **非該当(確定)**:適用なし |

## 5. 補足の観察(提案のみ・未実装)
- ログ表示の `instruction: minimal (not ENGLISH_STYLE_PREFIX)` は実Promptを反映しない固定文字列(branch版のfallback_style_prefix使用時も同じ文字列が残る)ため、運用者が「簡略化された」と誤認し得る。ラベルの実態反映は別管理IDで検討対象(本調査では変更しない)。
- 全attemptで段落区切りが1スペースに潰れてTTSへ渡る(`tts_safe_news_en`)。ASR転写に `\n\n` が入るのはTTS側が自然な段落ポーズを付けたため。
- Attempt 4の自動ASR不合格(Azureのみ)はOPEN-270/274/275の範囲。本調査はこれらの是正案に触れない。
