# OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01 実行報告

管理ID: OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01
背景: `NUMERIC-PRECISION-RETROACTIVE-AUDIT-01_REPORT.md`でTheme 2 A2完成本文
(`rerun_02/a2`)Main Storyに「24.1%」残存を発見。ユーザー指示により
(1)共通配線確認(2)実データでの圧縮確認のみ実施し、確認できればclose、
かつ承認済みB1方式と同一手順でArtifact最小修正まで実施。

## Part 1: 仕様確認

### (1) 共通配線の根拠(A2/B1で分岐なし)

`er003_v1_n3_01_evidence_compression_editor.py::run_lossless_editor(client,
article_text, model)`(226行目〜)はlevel/genre引数を一切持たない。
`EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE`(既定強化ブロック
`NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK`121行目〜、218-219行目
で連結)も単一テンプレート。呼び出しチェーン:
`er003_v1_n3_01_articles_generate.py::run_one_pattern()`(1096-1097行目で
`label="B1B"`/`label="A2"`双方から共通で呼ばれる)→
`_generate_and_compress_article()`(633-675行目、`apply_evidence_
compression`既定True)→658行目`ec_editor.run_lossless_editor(client,
article_text, model=model)`。`label`はWriter instruction選択
(`_writer_process()`55行目)にのみ影響し、Editor呼び出しには一切渡らない。
分岐コードは存在しない(grep・目視両方で確認)。

### (2) 実データでの圧縮確認

対象草稿: `er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/a2_run01/
audit/pre_editor_article.md`(Theme 2 A2 rerun_02/a2/article.mdと
byte-for-byte一致することをdiffで確認済み、= 実際に完成音声化された原文)。
現行Production `run_lossless_editor()`を無変更のまま1回実行
(`er011_output/open112_trend_theme2_a2_numeric_check_01/run_editor_check.py`、
model=gpt-5.6-luna=A2_WRITER routing)。

結果: `"It was chosen by 24.1%."` → `"About 24% chose it."`
(`editor_output.md`。24.1%は完全に消滅、about 24%へ丸められることを確認)。
同一草稿を対象にした2026-09-07配線タスク自身のruntime evidence
(`er011_output/preview_role_numeric_precision_wiring_01/
numeric_precision_evidence.json`)でも独立に同一結果("It was chosen by
about 24%")を確認済み、2回とも一致(judgment ruleのため文言は非決定的だが
丸め自体は一貫)。コスト: input 3269 output 797 tokens ≒ ¥0.26。

### 結論

共通配線あり(分岐なし)+実データで24.1%が圧縮されることを確認。
**仕様問題としてclose可能**(A2専用patch・A2専用ルールは不要、Production
仕様への追加変更なし)。

## Part 2: Artifact最小修正(B1 rerun_04と同一手順)

出力先: `er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2/`
(B1のrerun_04と同一親ディレクトリ、rerun_04/b1b・player.htmlは無変更)。

- 置換: `er011_open112_theme2_a2_numeric_minimal_fix_rerun_04.py`で
  article.md/parts.json[part1]の"24.1%"→"about 24%"を決定的置換(置換前に
  本文中ちょうど1回であることをassert、article.md/parts.json両方で確認)。
  他箇所への残存は`audit/tts_generation_results.json`(後続で上書き)と
  Key Phrase生成時prompt logの3件のみ(既存Key Phrase出力・Preview・
  Comment本文には0件、grepで確認、B1と同一パターンの非STOP事由)。
- TTS再生成(`full_story_part1`のみ、Production関数
  `generate_a2_segment_with_slowdown(style_prefix_override=
  A2_ENGLISH_STYLE_PREFIX_SLOWER, enable_connected_speech_equivalence_
  layer=True, enable_repetition_qa=True)`、TTS_EXECUTION_MODE=STANDARD):
  1回目の試行でPASS(asr_verified=True、audio_classification=
  HIGH_SIMILARITY_SAFE、repetition_qa flagged=False、Human Review Lock
  発動なし)。sha256旧`89c254d0...682036`→新`bd82e1f6...4c57a`。
  費用: Gemini TTS + OpenAI ASR(2回)≒ ¥3.55(上限¥100に対し実費)。
- 他segment reuse: `verify_reuse_sha256_a2.py`でrerun_02/a2全体と突合、
  **69ファイルがbyte-for-byte一致**(意図的変更対象[article.md/
  parts.json/audit/tts_generation_results.json/audit/review_lock_state.json
  /narration/full_story_part1(_original).wav/再Assembly出力[gain_report.
  json・timeline.json・headroom_report.json・run_summary_assemble.json・
  assembled/*.wav、full_story_part1の音声長・gain変化に伴い実測値が
  変わるのは正常挙動]を除く)。`review_lock_state.json`は10→11エントリ、
  既存10件は無変更・新規`full_story_part1`1件追記のみ(append-only、
  目視確認済み)。
- 再Assembly: 既存`stage_assemble_a2()`(無変更)実行、Gate通過
  (`verify_episode_audio_validation_gate`例外なし)。duration
  358.175s→355.599s(-2.576s)、peak 0.98/headroom safety valve適用
  (peak_before=1.0350189、cause_piece="Point One"、rerun_02と完全同値、
  無関係な既存事象)、clipping=False。
- player_a2.html(標準フォーマット、既存rerun_04/player.htmlとは別名):
  `file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_04/player_a2.html`
  Gate 7機械チェック: ヘッダー4列・Source列なし=PASS、全31行が4
  `<td>`+seekボタン=PASS、SFX行7件は`<audio>`0個かつ効果音/ジングル文言
  含む=PASS、全31行に`<small>voice=...</small>`=PASS、CSS
  min-width 360px/width 400px存在=PASS。unresolved=1件
  (`Japanese title`、実読み上げテキストが実データとして未保存のため
  正直に「未取得」表記、推測補完せず)。

## 費用合計

Part 1(Editor) ¥0.26 + Part 2(TTS/ASR) ¥3.55 ≒ **¥3.81**
(上限: Part 1 ¥50、Part 2 ¥100、いずれも大幅に下回る)。

## 変更ファイル一覧

- 新規(root): `er011_open112_theme2_a2_numeric_minimal_fix_rerun_04.py`
- 新規: `er011_output/open112_trend_theme2_a2_numeric_check_01/`
  (`run_editor_check.py`・`editor_check_result.json`・`editor_output.md`)
- 新規: `er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2/`
  (rerun_02/a2の全コピー、実質変更はarticle.md/parts.json/
  audit/tts_generation_results.json/audit/review_lock_state.json/
  narration/full_story_part1[_original].wavのみ、他74ファイルはbyte-for-
  byte reuse)
- 新規: `er011_output/open112_trend_theme2_b_final_audio_rerun_04/`直下の
  `assemble_a2_runtime_evidence.py`・`build_player_a2_runtime_evidence.py`・
  `full_story_part1_a2_regen_runtime_evidence.py`・
  `verify_reuse_sha256_a2.py`・`numeric_minimal_fix_diff_a2.json`・
  `reuse_sha256_verification_a2.json`・
  `full_story_part1_a2_regen_run_summary.json`・`raw_usage_log_a2.jsonl`・
  `player_a2.html`
- 不変(確認済み): `rerun_04/b1b/`・`rerun_04/player.html`(git diff/mtime
  変化なし)、Production Editor/TTS/Assembly/Validatorコード全て無変更
- 副作用(既存Production関数の共有台帳、自動更新): `er006_output/
  master_audio_store_01/manifest.json`・`reuse_telemetry.jsonl`・
  `er006_output/pronunciation_ledger_01/ledger.json`・`er006_output/
  audio_retry_cascade_prod_01/human_review_queue.jsonl`・
  `er011_output/attempt_history.jsonl`

## 未確認事項

- 到達Statusは`USER_FINAL_AUDIO_REVIEW_REQUIRED`(ユーザー最終試聴待ち、
  `APPROVED_FOR_PRODUCTION`は本タスクでは判定しない)。
- `DECISION_LOG.md`/`OPEN_ITEMS.md`への正式転記は本タスク範囲外(禁止事項
  どおり未実施、後続の統合タスクでFable/ユーザーが本Reportを根拠に転記)。
- player_a2.htmlの"Japanese title"行のみ実読み上げ日本語テキストが未保存
  (音声自体は提示、正直に未取得表記)。
- n3_01他3テーマ・他ジャンルへの遡及調査は本タスク範囲外(監査Report既述)。
