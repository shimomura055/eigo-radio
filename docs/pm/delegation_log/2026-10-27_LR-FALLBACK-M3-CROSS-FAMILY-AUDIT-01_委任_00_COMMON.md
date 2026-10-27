# 委任共通事項(LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01、2026-10-27、Fable→sonnet-worker)

ユーザー原文: `docs/pm/delegation_log/2026-10-27_LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01_USER.md`(必読)。共通Charter=`CLAUDE.md`冒頭、実行層規則=`.claude/agents/sonnet-worker.md`。

## 全委任共通の制約(Phase 1)
- **読取専用・API 0・JPY 0**。TTS/ASR/LLMの有料呼出禁止、有料runの起動・再開・再現禁止。既存の保存データ・ログ・コード・SSOT・docsのみで調査する。
- **編集禁止**: `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/ACTIVE_TASK.md`/Productionコード/Prompt/test。Git操作禁止。AI島の原稿・確定内容(`confirmed_selection.json`等)を変更しない。
- **成果物は指定ファイル1つ**(`docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/` 配下、新規作成)。他ファイルを作らない。
- `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`は全文読込禁止(Grep+該当行のみ)。
- 事実は必ず`file:line`または保存データのパス+キーで裏付ける。**「コード配線」「単体/結合test」「実runtime発火(保存evidence)」「未観測」を列ごとに区別**し、未観測を実証済みと書かない。
- 歴史的記述(旧「標準2回+Minimal Fallback 1回」「600秒cooldown」「LR後1回」等)と、2026-10-26ユーザー決定の**統一仕様**(`CURRENT_SPEC.md:3148-3220`、`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/`)を混同しない。X/Y/Z正式経路の現行正本は統一仕様。
- 所見は **A=承認済み仕様からの実装逸脱 / B=承認済み仕様同士の矛盾 / C=仕様どおりだが品質問題が残る** に分類し、根拠(承認原文の`file:line`)を付ける。ユーザー判断が要りそうな事項は`判断候補`と表記(`USER_DECISION_REQUIRED`ラベルはFableのみ)。判断候補にはA既判断/B承認範囲内で自己解決/C現タスクと独立/D真に新しい判断の別を添える(PM_GOVERNANCE 27-3)。
- 修正案は**提案のみ**(実装しない)。案ごとに影響範囲・QCD影響・必要な承認区分を書く。
- 最後に「Fableへの報告(要約10行以内)」節を置く。

## 共通参照(所在)
- 統一仕様: `CURRENT_SPEC.md:3148-3220`。ユーザー決定原文 `docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_USER.md`。設計 `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/{DESIGN_01,DESIGN_02,ROW_MAPPING_01,SPEC_LEDGER_01,IMPLEMENTATION_01,OPUS_REVIEW_01,HR_IMPACT_01,EVIDENCE_01,EVIDENCE_X_01,EVIDENCE_Y_01,EVIDENCE_Z_01,FOLLOWUP_01,FOLLOWUP_02}.md`。
- LR承認(2026-09-26 `APPROVED_FOR_PRODUCTION`、`RESOLVED_BY_LOCAL_REWRITE`の定義): `CURRENT_SPEC.md:2214`。原文は`docs/pm/delegation_log/`を`2026-09-26`+`Local Rewrite`でGrepして特定。
- LR基本フロー・書換え後の文を正解原稿とする再検証・HR Lock keyは元原稿(2026-10-19ユーザー決定): `CURRENT_SPEC.md:2925`。原文 `docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md`。
- Fallback採用=M3正規承認による個別判断(2026-10-21ユーザー決定)+AI島適用例: `CURRENT_SPEC.md:2857-2858`。
- 統一仕様におけるGate検知(③/LR採用音声をfail-closed GateがBLOCK、Gate条件無変更): `CURRENT_SPEC.md:3166`付近。
- 前回横断監査(2026-10-26 AUDITED): `docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/{REPORT_01,FAMILY_X_01,FAMILY_Y_01,FAMILY_Z_01,COMMON_CORE_01}.md`、`DECISION_LOG.md:22591`付近。
- AI島: `docs/research/AI-ISLAND-FORM-PRODUCTION-01/{HR_ROOT_CAUSE_01,DIAG_SLOWDOWN_ASR_01,HR_PACKET_02,PREP_06}.md`。run=`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/{a2,b1b}/audit/tts_generation_results.json`(segment `full_story_part1_k2`、キー`canonical_text_before_local_rewrite`/`text`/`local_rewrite_recovery`)、`<run>/audit/hr_packet_data_01.json`。本文=`er019_output/ai_island_temple/run_ai_01/{a2,b1b}/article.md`、確定=同`confirmed_selection.json`。公開=`user_test/family_x_ai_island_form_01/`。
- コード: `er020_tts_retry_local_rewrite_01.py`(`run_local_rewrite_recovery`、`resolve_expected_text_after_local_rewrite` L858前後)、`er127_tts_block_policy_01.py`(`PROFILES`、`save_lr_text` L352、`lr_recover` L627-710)、`er019_family_x_style_profile_01.py`(M3 `_approved` L629-634、`m3_assembly_gate` L685-760、`LOCAL_REWRITE_RECOVERY` L742)、`er121_family_y_audio_01.py:929`(Y gate)、`er063_family_z_audio_01.py`/`er117_chunk_tts_production_01.py`(Z)、`er003_v1_crosslevel_audio_02_common.py`(A2経路、`_merge` L477付近)、`er003_v1_sing01_news_tail_fix.py`/`er003_v1_sing01_voice01_generate.py`(B1経路)、`er019_family_x_audio_production_runner_01.py`、`er128_kp_confirmed_content_01.py`(KP確定保護G0〜G4)。
- OPEN_ITEMS(Grep): OPEN-312(LR再TTSのStyle脱落、M3検知)、OPEN-274(LR再TTSがminimal fallbackに依存)、OPEN-499(Word Gacha Adv part3 LR個別承認の先例)、OPEN-561/563/564(AI島)、OPEN-540(統一)、OPEN-528(Zセリフ)、OPEN-371(Secondary障害)。`docs/pm/USER_DECISION_REGISTER_01.md` #6・#183。
