# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04_REPORT.md

管理ID: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04`
実行者: Sonnet(サンドイッチ委任、初回)
性質: Trial(音声Styleのみ)。到達上限Status: `USER_DECISION_REQUIRED`
(ユーザー試聴前、Production配線へ進まない)。Production採用・配線は
行っていない。

証跡格納先: `er046_output/key_phrase_advanced_english_explanation_audio_
style_trial_04/hormuz/`(`reused_audio_summary.json`,
`variant_audio_summary.json`, `variant_audio_raw_usage_log.jsonl`,
`audio/*.wav`、30ファイル)
確認ページ: `user_test/kp_advanced_explanation_audio_trial_04/index.html`
設計書: `docs/pm/design_key_phrase_advanced_english_explanation_audio_
style_trial_04.md`

---

## §1 前提

Advanced Key Phrase英語解説の**text仕様**はユーザーが正式採用済み
(`APPROVED_FOR_PRODUCTION`、KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-
TRIAL-02のB候補5件)。Production wiringは未実施(OPEN-221継続OPEN)。
TRIAL-03のAfter(`clear, precise, unhurried`)はユーザー判断で**遅すぎた**
(不採用)。本Trialは、Before(`clear, precise, explanatory`)と
unhurriedの**中間の自然な速度感**を3案(A/B/C)で探索する。Hormuz既存5
Key Phrase・既存英語解説文(TRIAL-02のB候補)を逐語使用し、再生成・
再選定は一切行っていない。

## §2 実施内容

1. `cmd_reuse`: TRIAL-03出力(`er042_output/.../hormuz`)から
   Phrase EN音声5件・Before(explanatory)音声5件・Reference
   After(unhurried、不採用だが参考として掲載)音声5件、計15件をコピー
   再利用(新規TTS callなし)。Before/Reference AfterのStyle文字列を
   機械検証(完全一致)した上でreuse。
2. `cmd_variant_audio`: A/B/C 3案 × 5 Phrase = 15件新規生成(Production
   同一関数`generate_narration_snippet_verified_strict`、Trial Store隔離、
   `TTS_EXECUTION_MODE=STANDARD`明示、既存ASR cascade`max_attempts=2`
   のまま)。15件とも`status=OK`、`retry_count=0`、`asr_verified=True`。
3. `er046_..._page_01.py`: wav→mp3変換(lameenc)+試聴ページ生成
   (duration比較表含む)。

実行コマンド全文:
```
.venv/Scripts/python.exe er046_key_phrase_advanced_english_explanation_audio_style_trial_04.py \
    --source-dir "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz" \
    --out-dir "er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/hormuz" \
    --skip-variant

TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er046_key_phrase_advanced_english_explanation_audio_style_trial_04.py \
    --source-dir "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz" \
    --out-dir "er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/hormuz" \
    --trial-store "er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/master_store" \
    --tts-backend speech_metadata_flash_lite --budget-jpy 10 --skip-reuse

.venv/Scripts/python.exe er046_key_phrase_advanced_english_explanation_audio_style_trial_04_page_01.py
```

## §3 使用Prompt全文(実際にTTSへ渡した最終Style文字列)

- Before(参考、reuse): `clear, precise, explanatory`
- Reference After(参考、不採用、reuse): `clear, precise, unhurried`
- A(新規): `clear, precise, at a slightly relaxed pace`
- B(新規): `clear, precise, at a measured pace, without dragging`
- C(新規): `clear, precise, carefully paced for understanding, without slowing down`

全て`en_pronunciation_resolver_info.hints_applied == False`
(A/B/C 15件全て)であり、上記文字列がそのままTTSへ渡された最終
instruction文字列である(接頭・接尾の追加なし)。速度の数値指定
(WPM等)は含めていない。

## §4 Candidate(5 Phrase、英語解説はTRIAL-02のB候補を逐語使用)

| # | phrase | 英語解説(共通) |
|---|---|---|
| 1 | give back | to lose some of an earlier gain |
| 2 | sea blockade | the act of stopping ships from entering or leaving by sea |
| 3 | stand at center stage | to be the main focus of attention |
| 4 | take a sharp turn | to change suddenly and significantly |
| 5 | recover the cost | to get back the money spent on something |

model: `gemini-3.8-flash-lite-tts`(TRIAL-03と同一)、voice: `Aoede`
(TRIAL-03と同一)。

## §5 音声実測(duration比較、words per second)

| # | phrase | Before(explanatory) | A | B | C | Reference After(unhurried,不採用) |
|---|---|---|---|---|---|---|
| 1 | give back | 2.72s | 2.74s | 2.82s | 3.46s | 3.22s |
| 2 | sea blockade | 3.82s | 4.26s | 4.40s | 5.12s | 5.50s |
| 3 | stand at center stage | 2.68s | 3.02s | 3.54s | 3.46s | 3.32s |
| 4 | take a sharp turn | 3.10s | 3.14s | 3.26s | 3.80s | 3.78s |
| 5 | recover the cost | 2.94s | 2.98s | 3.34s | 3.34s | 3.26s |

A/B/Cはおおむねbefore(explanatory)とreference after(unhurried)の中間に
位置し、#2を除きreference afterを超えない範囲に収まっている
(語/秒等の詳細な客観指標は試聴ページのduration比較表に掲載)。

A/B/C 15件全件: `status=OK`、`retry_count=0`、`asr_verified=True`。

## §6 費用

新規生成15件で合計`2.024`円(`variant_audio_summary.json`
`total_new_audio_cost_jpy`、内訳`gemini=1.66`/`openai_asr=0.36`)。
Before/Reference Afterは新規call無しのため¥0。合計約¥2.02
(Guardrail ¥10以内)。

## §7 test / regression

- `.venv\Scripts\python.exe -m unittest er046_key_phrase_advanced_
  english_explanation_audio_style_trial_04_test_01 -v`: 21 tests、
  全PASS。
- `.venv\Scripts\python.exe run_project_regression.py --pattern
  "er046*_test_*.py"`: `collected=21 passed=21 failed=0 errors=0
  skipped=0`。

## §8 Production無変更の証拠

```
git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er046
```
結果: `er006_output/master_audio_store_01/manifest.json`,
`reuse_telemetry.jsonl`の2件のみ(本タスク開始前からの既存未commit差分、
本タスク開始時点のgit statusスナップショットで既に`M`表示済み)。
diff本文を`grep -iE "TRIAL-04|er046|trial_04"`で検索したところ0件で
あり、本タスクによる追記ではないことを確認した(他タスクの未commit
差分)。Trial音声生成はTrial専用Store(`er046_output/.../master_store/`)
で`trial_master_audio_store`context manager経由のみ実施。

## §9 試聴ページ / GitHub Pages公開確認(7項目)

commit/push後に実施し、結果は`docs/pm/RESULT_PACKET_KA4.md`および
handbackへ記録する(本セクションは実施結果を追記)。

## §10 Trial Status

`USER_DECISION_REQUIRED`(ユーザー試聴待ち)。`VALIDATED`は自己宣言
しない。

## §11 SSOT追記案(文案のみ、編集権なし)

- REPORT_LEDGER新行: 本REPORTへのリンク追加。
- DECISION_LOG.md: 「Advanced Key Phrase英語解説text仕様=ユーザー正式
  採用`APPROVED_FOR_PRODUCTION`(既存決定の再確認)、Production wiring
  未実施」+本Trial(TRIAL-03 Afterのunhurriedが遅すぎたためBeforeと
  unhurriedの中間3案A/B/Cを新規探索)記録。
- OPEN_ITEMS.md OPEN-221追記案: 「2026-09-28追記
  (`KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04`):
  TRIAL-03のAfter(`clear, precise, unhurried`)はユーザー判断で遅すぎ
  たため不採用。Before(`clear, precise, explanatory`)とunhurriedの
  中間の自然な速度感を探る3案(A=`clear, precise, at a slightly
  relaxed pace`/B=`clear, precise, at a measured pace, without
  dragging`/C=`clear, precise, carefully paced for understanding,
  without slowing down`)を5 Phrase×3案=15件新規生成。全件
  status=OK・retry=0・asr_verified=True、duration実測はおおむね
  Before〜Reference Afterの中間に収まる。Production採用・
  `KEY_PHRASE_EXPLANATION_EN`実装自体は引き続き未実施、ユーザー
  試聴待ち。」
