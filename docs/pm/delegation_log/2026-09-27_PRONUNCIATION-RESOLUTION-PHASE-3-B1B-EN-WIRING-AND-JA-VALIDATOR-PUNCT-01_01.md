# PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01 委任文(全文)

管理ID: PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01(新規、Phase 2 PRODUCTION_WIRED[commit 323a18a7]で明示的にdeferredされたOPEN-197/198と、OPEN-199の実装。**既存承認仕様(2026-09-27 APPROVED: Family X/Z全経路で読み解決; JA ASR Validatorの句読点正規化)の実装穴の是正であり新仕様ではない**)。**¥0: コード・test・fixtureのみ。TTS/ASR/LLM実行なし、Human Review Lock解除なし、共有ストア書込みなし。** 一時ファイル `docs/pm/ACTIVE_TASK_PRN5.md` / `docs/pm/RESULT_PACKET_PRN5.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_01.md` に保存しcommitに含める。本commit後にOpus L2レビュー(共有ASR/TTS層変更のため必須)を行うので、diffは最小・自己完結にする。

## 先出しRead
- `OPEN_ITEMS.md` OPEN-197/198/199(Grep)、`PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_REPORT.md` §21〜§22(OPEN-199の差分文字全件: 引用符脱落・全角「？」不再現・全角スペース脱落)、`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md` Stage 3d(small_bag B1B `full_story_part2/3` Human Review落ちの詳細)
- EN resolver配線の既存実装(A2英語経路): `er019_family_x_audio_production_runner_01.py` の `en_pronunciation_resolver_info` 付近、`er025_entity_pronunciation_resolver_core_01.py`、`er006_pronunciation_tts_injection_01.augment_style_prefix_with_pronunciation`
- B1B英語経路: `generate_charon_english`(定義元をGrep)と `generate_english_component_minimal_instruction`(B1 scaffold等)
- JA ASR Validator: `er007_ja_asr_validator_01.py` `_PUNCT_RE` / `normalize_ja()`、`er003_audio_tts_asr_safety.py` `_extract_numbers_ja` との関係、CURRENT_SPEC「日本語ASR」該当節

## 作業
1. **OPEN-197/198(EN resolver配線)**: A2英語経路と**同一のhook**(同じ関数・同じ引数・同じconfidence gate・同じtelemetry)を `generate_charon_english`(B1B)と `generate_english_component_minimal_instruction` の呼び出し側(Family X runner側で可能ならrunner側に置き、共有関数本体の変更は最小)へ配線。Family A(legacy)経路の挙動が変わらないこと(Family Aのrunner/testが同関数を呼ぶ場合、resolverはFamily X runnerからのみ有効化されるようopt-in引数にする)。unit test: hint注入あり/なし、Family A経路無変化、cache-only(web lookup禁止switch `ALLOW_PRONUNCIATION_WEB_LOOKUP` 使用)。
2. **OPEN-199(JA Validator句読点正規化)**: `normalize_ja()` の比較前正規化に、引用符(「」『』"" '' 等)・全角「？」「！」・全角スペース・中点(既存扱いを確認)を**既存の句読点除去と同じ層で**追加。数値・否定語検出(`_extract_numbers_ja`等)や意味比較のロジックは変えない。Phase 2 JA-1のMuse差分3件(REPORT §22に逐語あり)をfixture化し、正規化後に一致することをtestで示す。副作用チェック: 既存er007 test全件、`er011_ja_asr_variant_layer_01` test、Family X JA segmentの既存OK判定が反転しないこと(既存 `tts_generation_results.json` のcanonical/ASR組を数件fixtureに取り込み、OK→OK維持を確認)。
3. **Lock更新漏れ(Stage 3d副次発見)**: small_bag A2 `meaning_5` が `review_lock_state.json` 上STOPPEDのまま実結果OK。原因を `er011_human_review_lock_01` / runnerの更新経路で特定し、**修正は最小差分でコードのみ**(状態ファイルは書き換えない)。既存OPENに無ければOPEN_ITEMSへ登録案(RESULT_PACKETに記載、SSOTは本委任では編集しない)。
4. REPORT `PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_REPORT.md` 新設: 既存資産照合(分類A: 既存承認仕様の実装穴、根拠=CURRENT_SPEC該当行)、diff要約、test結果、runtime evidence計画(Lock解除承認後にHormuz/small_bag/Metaで実施する手順と見積り、Guardrail案)、SSOT記載案(編集はしない)。
5. 回帰: 変更モジュールのtest+`run_project_regression.py`(既知6件以外の失敗なし)。

Git: 変更コード・test・fixture・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agentのstageを外さない、index.lockリトライ)。トレーラー `Management-ID: PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETにcommit hash・変更ファイル・test件数・Opus L2向けに「変更点3つの要約と懸念」を記載。
