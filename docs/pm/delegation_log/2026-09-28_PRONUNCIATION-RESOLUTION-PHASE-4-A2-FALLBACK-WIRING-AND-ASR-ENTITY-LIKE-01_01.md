# 委任文全文(PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01、01)

管理ID: PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01(新規。ユーザー承認 2026-09-28: 既承認仕様「初回/retry/fallback/regenerationを含む全Production経路でresolver適用」の未配線修正A-2と、ASR `entity_like` 判定の一般化A-1。Status APPROVED_FOR_PRODUCTIONのままGate 3 closeoutへ進めるが、**Opus L2/runtime evidence/Regression/SSOT/Git未完了でPRODUCTION_WIRED宣言しない**)。一時ファイル `docs/pm/ACTIVE_TASK_PRN8.md` / `docs/pm/RESULT_PACKET_PRN8.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-28_PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01_01.md` に保存しcommitに含める。Guardrail **¥15**(runtime evidenceのみ。コード・testは¥0)。`TTS_EXECUTION_MODE=STANDARD`、`ALLOW_PRONUNCIATION_WEB_LOOKUP=0`(cache-only)、コマンド逐語記録。APIキーは環境変数のみ。**Human Review Lockの解除は禁止**(small_bag 3 segmentの再実行はユーザー再承認後の別委任)。

## 先出しRead
`docs/pm/RESULT_PACKET_FXD1.md`(診断結果: 分類A-1/A-2、該当コード行)、`docs/pm/delegation_log/2026-09-27_NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_06.md`、`er006_preprod_hardening_01_validation.py`(L585付近 `entity_like`、`classify_asr_match`、数値/否定検出、cascade分岐)、`er003_v1_crosslevel_audio_02_common.py`(`_run_a2_minimal_fallback_attempt`、`generate_english_segment_with_fallback`)、`er003_v1_repro01_main_generate.py`(`generate_narration_snippet_verified_strict` のresolver配線、Phase 2)、`er025_entity_pronunciation_resolver_core_01.py`(`resolve_and_augment_en_style_prefix`、EN lookup上限)、`er006_pronunciation_ledger_01.py`(Ledger surface検索・`_surface_matches_text`・`tts_injection_disabled`・`cascade_unresolved_entity`)、Phase 3 REPORT(§8 Opus S1〜S3の配線パターン)、OPEN-203。

## A-2: A2 fallback経路へのEN resolver正式配線
- `_run_a2_minimal_fallback_attempt` に、標準経路と**同一hook**(`resolve_and_augment_en_style_prefix`、同confidence gate、cache-only switch、telemetry `en_pronunciation_resolver_info`)を配線し、fallback結果dictへinfoを伝播(OPEN-203解消)。initial/retry/fallback/regeneration(`approve_regenerate` 後の再生成)の4経路すべてが同じhookを通ることを呼び出しチェーン表で示す(Dangling Referenceなし)。legacy(Family A)呼び出しはopt-in既定Falseで不変(A2経路の既存opt-in有無を確認し、Phase 2でunconditional配線されている場合はその方針に合わせる。方針の根拠を記載)。

## A-1: ASR `entity_like` 判定の一般化(安全側classification/cascade対象の拡張。**自動acceptにしない**)
- 現行「本文中で大文字始まり」に加え、(a) Pronunciation Ledger登録済みsurface(語境界一致、`tts_injection_disabled` の有無に関係なく**分類目的では**登録事実を使ってよい。ただし `cascade_unresolved_entity` のTTS事前注入除外は変更しない)、(b) 小文字外来語(非ASCII文字を含む語、または既存の外来語判定資産があればそれ)を `entity_like` に含める。
- **禁止**: 数値/否定のhard safety変更、false accept増加、一般語と同形surfaceの無条件救済(例: Ledgerに "us"(OPEN-207) や一般語が誤登録されていても、CEFR-J/NGSL等の基本語彙表に載る一般語は `entity_like` にしない=同形ガード)、Ledger登録だけを理由にPASSさせること。効果は「entity不一致がTRUE_CONTENT_MISMATCHへ格上げされず、既存のentity_only→ASR_VALIDATION_UNCERTAIN→cascade/Human Review経路へ回る」まで。
- fixture: proper noun(Khaite/Altuzarra)、lowercase loanword(minaudière)、Ledger surface(語境界)、**non-entity negative control**(一般語・数値・否定を含む不一致は従来どおりTRUE_CONTENT_MISMATCH)、同形一般語ガード("us"、"mark" 等)、small_bag A2 fsp2の実ASR書き起こし(Stage 3e artifact)を使った再分類期待値。

## runtime evidence(evidenceモード、Guardrail ¥15、Lock解除なし)
- small_bag A2 `full_story_part2` のcanonical textを**別run dir**(例 `er025_output/phase4_evidence_01/`、Production artifact・Lock state非上書き)で、標準経路を強制失敗させてfallback経路へ入れる注入(既存test手法)により **A2 fallback resolver実発火**(hits/hints_applied/telemetry)を実測。ASRは実行し、新 `entity_like` により分類がTRUE_CONTENT_MISMATCH→ASR_VALIDATION_UNCERTAIN(またはentity cascade)へ変わるかを記録(retry予算は本evidenceで1 attemptに限定)。model_id/routing(TTS・ASR実モデル)を記録。
- 期待救済内容と、本番3 segment再実行時の見積(segment数×attempt上限×単価)・Guardrail案をRESULT_PACKETに記載(ユーザー承認用)。

## test/regression/SSOT
- unit test(A-1 fixture群、A-2 hook、legacy不変)、既存 er006/er007/er021/er011 関連test、`run_project_regression.py`(既知baseline以外なし。baseline件数の現状[failed=6/errors=2]を記録)。
- REPORT `PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01_REPORT.md` 新設: 既存資産照合(分類A)、A-1/A-2 diff要約、呼び出しチェーン表、fixture結果、runtime evidence、Gate 3チェックリスト(Opus L2=未、PRODUCTION_WIRED=Fable判定待ち)、Opus L2申し送り、再実行提案(対象segment・期待救済・見積・Guardrail)。
- SSOT: CURRENT_SPEC(読み解決節にPhase 4を APPROVED_FOR_PRODUCTION/WIRING IN PROGRESS で追記、`entity_like` 定義の更新案を明記)、DECISION_LOG(ユーザー承認エントリ)、OPEN_ITEMS(OPEN-203→本Phaseで解消予定、新規なし)、REPORT_LEDGER。SSOT編集直前に `git status` で他Agent(KP設計レビュー: docs/pm/design_kp_*)の未commit差分を確認。

Git: 変更コード・test・fixture・evidence・REPORT・SSOT 4点・delegation_logのみpath指定add(`git add -A`禁止、index.lockリトライ)。トレーラー `Management-ID: PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに費用・commit hash・変更ファイル・test件数・evidence結果・再実行提案・Opus申し送りを記載。
