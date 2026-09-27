# PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01 委任文(全文、Fable修正指示1回目)

管理ID: PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01(Fable修正指示1回目。**¥0、TTS/ASR/LLM実行なし、Lock解除なし、SSOT編集なし**)。一時ファイル `docs/pm/ACTIVE_TASK_PRN6.md` / `docs/pm/RESULT_PACKET_PRN6.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_02.md` に保存しcommitに含める。直後にOpus L2レビューを行うため、diffは最小・自己完結。

## 前提
初回(commit b3cb2308)のREPORT `PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_REPORT.md` §2〜§7を読む。Fable判定: 初回の範囲指定(2関数)が狭すぎた。承認済み仕様は「Family X/Z全経路で読み解決」であり、実際のsmall_bag B1B `full_story_part2/3` STOPは `generate_news_narration_wide_margin` の**標準ENGLISH_STYLE_PREFIX分岐**で起きている。これは新仕様判断ではなく同じ実装穴の残り。

## 修正
1. **標準分岐への配線**: `er003_v1_sing01_news_tail_fix.py` `generate_news_narration_wide_margin()` の標準分岐(ENGLISH_STYLE_PREFIX経由)へ、初回と同じ opt-in引数 `enable_pronunciation_resolver`(既定False)で同一hook(A2英語標準経路と同じ関数・引数・confidence gate・telemetry・`en_pronunciation_resolver_info` 記録)を配線。Family X runner(`er019_family_x_audio_production_runner_01.py`)のB1B生成呼び出しからのみTrue。Family A/B/C legacyの呼び出し(既定False)は挙動不変であることをtestで示す(呼び出し元をGrepで全列挙しREPORTに記載)。
2. **EN側Lock記録の同型ギャップ**: `generate_english_segment_with_fallback()`(定義元をGrep)へ、JA側(`generate_a2_japanese_with_fallback` に `@review_lock.guarded_generate("ja")`)と同じ最小差分で `guarded_generate("en")` を適用。reentrancy guardが二重記録を防ぐことをtest(temp narration layoutでRESOLVED/HUMAN_REVIEW_REQUIRED両方)で確認。状態ファイルは書き換えない。
3. test: 既存 `er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01.py` へ標準分岐のhint注入あり/なし・legacy不変・cache-only(`ALLOW_PRONUNCIATION_WEB_LOOKUP` 禁止switch)を追加、Lock test追加。関連既存test個別実行+`run_project_regression.py`(既知失敗以外なし。初回で報告したflake 1件は単独実行PASSを再確認し記録のみ)。
4. REPORT §8「修正1回目」: 変更点、呼び出し元一覧、test結果、Opus L2申し送り(初回3点+本修正2点を1表に統合)。§5 OPEN_ITEMS記載案から「標準分岐未配線」「EN Lock同型」を削除(解消済み)し、残る記載案(必要なら)を更新。§6 runtime evidence計画を更新(Lock解除対象6 segment+small_bag B1B fsp2/3+Meta A2 japanese_title+small_bag B1B KP再選定1 call、見積・Guardrail ¥150)。

Git: 変更コード・test・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agent[er029_*]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに commit hash・変更ファイル・test件数・Opus L2申し送り表を記載。
