# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_REPORT.md

管理ID: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03`
実行者: Sonnet(サンドイッチ委任、初回)
性質: Trial(音声Styleのみ)。到達上限Status: `USER_DECISION_REQUIRED`
(ユーザー試聴前、Production配線へ進まない)。Production採用・配線は
行っていない。

証跡格納先: `er042_output/key_phrase_advanced_english_explanation_audio_
style_trial_03/hormuz/`(`reused_audio_summary.json`,
`after_audio_summary.json`, `after_audio_raw_usage_log.jsonl`,
`audio/*.wav`)
確認ページ: `user_test/kp_advanced_explanation_audio_trial_03/index.html`
設計書: `docs/pm/design_key_phrase_advanced_english_explanation_audio_
style_trial_03.md`

---

## §1 前提

Advanced Key Phrase英語解説の**text仕様**はユーザーが正式採用済み
(`APPROVED_FOR_PRODUCTION`、KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-
TRIAL-02のB候補5件)。Production wiringは未実施(OPEN-221継続OPEN)。
本Trialは**音声Styleだけ**を比較する: Before=`clear, precise,
explanatory` / After=`clear, precise, unhurried`。Hormuz既存5 Key
Phrase・既存英語解説文を逐語使用し、再生成・再選定は一切行っていない。

## §2 実施内容

1. `cmd_reuse`: er041が実際に`style_prefix_used=="clear, precise,
   explanatory"`(BEFORE指定と完全一致、pronunciation resolverの
   augmentationも無し)で生成した5件の英語解説音声をコピー再利用
   (新規TTS callなし)。Phrase EN音声5件もHormuz既存artifactのコピー
   再利用。
2. `cmd_after_audio`: After(`clear, precise, unhurried`)を5件新規生成
   (Production同一関数`generate_narration_snippet_verified_strict`、
   Trial Store隔離、`TTS_EXECUTION_MODE=STANDARD`明示、既存ASR cascade
   `max_attempts=2`のまま)。5件とも`status=OK`、`retry_count=0`、
   `asr_verified=True`。
3. `er042_..._page_01.py`: wav→mp3変換(lameenc、既存precedent通り)+
   試聴ページ生成。

実行コマンド全文:
```
.venv/Scripts/python.exe er042_key_phrase_advanced_english_explanation_audio_style_trial_03.py \
    --source-dir "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz" \
    --out-dir "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz" \
    --skip-after

TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er042_key_phrase_advanced_english_explanation_audio_style_trial_03.py \
    --source-dir "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz" \
    --out-dir "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz" \
    --trial-store "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/master_store" \
    --tts-backend speech_metadata_flash_lite --budget-jpy 10 --skip-reuse

.venv/Scripts/python.exe er042_key_phrase_advanced_english_explanation_audio_style_trial_03_page_01.py
```

## §3 使用Prompt全文(実際にTTSへ渡した最終Style文字列)

- Before: `clear, precise, explanatory`(er041実測、augmentation無し)
- After : `clear, precise, unhurried`(本Trial実測、augmentation無し)

両方とも`en_pronunciation_resolver_info.hints_applied == False`
(5件×2条件=10件全て)であり、上記2文字列がそのままTTSへ渡された最終
instruction文字列である(接頭・接尾の追加なし)。

## §4 Candidate(5 Phrase、英語解説はTRIAL-02のB候補を逐語使用)

| # | phrase | 英語解説(共通) |
|---|---|---|
| 1 | give back | to lose some of an earlier gain |
| 2 | sea blockade | the act of stopping ships from entering or leaving by sea |
| 3 | stand at center stage | to be the main focus of attention |
| 4 | take a sharp turn | to change suddenly and significantly |
| 5 | recover the cost | to get back the money spent on something |

## §5 音声実測(After、新規生成分)

| # | phrase | status | retry | duration(s) | asr_verified |
|---|---|---|---|---|---|
| 1 | give back | OK | 0 | 3.22 | True |
| 2 | sea blockade | OK | 0 | 5.50 | True |
| 3 | stand at center stage | OK | 0 | 3.32 | True |
| 4 | take a sharp turn | OK | 0 | 3.78 | True |
| 5 | recover the cost | OK | 0 | 3.26 | True |

Before音声(reuse分)はer041実測値をそのまま流用(`KEY-PHRASE-ADVANCED-
ENGLISH-EXPLANATION-TRIAL-02_REPORT.md`参照、全件status=OK・
retry_count=0)。

## §6 費用

Afterの新規生成5件で合計`0.7286`円(`after_audio_summary.json`
`total_new_audio_cost_jpy`)。Beforeは新規call無しのため¥0。合計約
¥0.73(Guardrail ¥10以内)。

## §7 test / regression

- `.venv\Scripts\python.exe -m unittest er042_key_phrase_advanced_
  english_explanation_audio_style_trial_03_test_01 -v`: 16 tests、全PASS
  (`.venv`にpytestモジュールが未インストールのため、
  `run_project_regression.py`と同じunittest discoveryベースの
  `python -m unittest`で代替実行、結果は同一)。
- `.venv\Scripts\python.exe run_project_regression.py --pattern
  "er042*_test_*.py"`: `collected=16 passed=16 failed=0 errors=0
  skipped=0`。

## §8 Production無変更の証拠

```
git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er042
```
結果: `er006_output/master_audio_store_01/manifest.json`,
`reuse_telemetry.jsonl`の2件のみ(本タスク開始前からの既存未commit差分、
本タスク開始時点のgit statusスナップショットで既に`M`表示済み)。
diff本文をgrepしたところ本管理ID・`er042`への言及は0件であり、本タスク
による追記ではないことを確認した(他タスクの未commit差分)。

## §9 試聴ページ / GitHub Pages公開確認(7項目)

commit/push後に実施し、結果は`docs/pm/RESULT_PACKET_KA3.md`および
handbackへ記録する(本セクションは実施結果を追記)。

## §10 Trial Status

`USER_DECISION_REQUIRED`(ユーザー試聴待ち)。`VALIDATED`は自己宣言
しない。

## §11 SSOT追記案(文案のみ、編集権なし)

- REPORT_LEDGER新行: 本REPORTへのリンク追加。
- DECISION_LOG.md: 「Advanced Key Phrase英語解説text仕様=ユーザー正式
  採用`APPROVED_FOR_PRODUCTION`(既存決定の再確認)、Production wiring
  未実施」+本Trial(音声Style Before/After比較)記録。
- OPEN_ITEMS.md OPEN-221追記案: 「2026-09-28追記
  (`KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03`):
  音声StyleをBefore(`clear, precise, explanatory`)→After(`clear,
  precise, unhurried`)で比較実施。5件ともstatus=OK・retry=0・
  asr_verified=True。ユーザー意図(はっきり・正確に・急がず)に沿った
  Style候補として`clear, precise, unhurried`を確認したが、Production
  採用・`KEY_PHRASE_EXPLANATION_EN`実装自体は引き続き未実施、ユーザー
  試聴待ち。」
