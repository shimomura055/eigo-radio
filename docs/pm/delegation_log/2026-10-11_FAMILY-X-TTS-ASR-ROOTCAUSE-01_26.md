# FAMILY-X-TTS-ASR-ROOTCAUSE-01 委任_26 (2026-10-11)
SSOT記録+read-only確認のみ。課金API・コード変更なし。

## SSOT変更
- DECISION_LOG.md: ユーザー決定逐語(5課題表+受入条件8点)+OPEN-256 Fable Gate判定逐語を追記
- CURRENT_SPEC.md: Local Rewrite行にPRODUCTION_WIRED(範囲=英語TTS role、日本語=OPEN-260)追記
- OPEN_ITEMS.md: OPEN-256 CLOSED(PRODUCTION_WIRED)、OPEN-258 DESIGN_READY_FOR_REVIEW/USER_DECISION_REQUIRED、OPEN-257へrun1事例追記

## run1 read-only確認 (case a)
証跡: er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl 5014行目、er053_output/family_x_tts_asr_rootcause_01/open256_runtime_01/run1/
- primary asr(gpt-4o-mini-transcribe)= "Some US calls were transferred over to human workers, ..." (retts_asr_verified=True)
- 5013行目(baseline): classification=ASR_VALIDATION_UNCERTAIN, sub_reason=entity_only, diff_span={canonical_word:"muse", asr_word:"us"}
- 5014行目(最終): classification=SECONDARY_ASR_CORROBORATED_MATCH, sub_reason=entity_only, corroborated_by=["secondary"], step=tier3_corroboration
- raw_usage_log: azure get_full_text_via_azure_stt_with_phrase_list(en-US, phrase_list_size=1) 2回
- Azure転写全文は記録なし(メタのみ)。判定コード=er021_en_asr_semantic_equivalence_trial_01.py(Tier3: _corroboration_supports)
- 結論: 既存仕様どおり(誤PASS経路ではない)。Azure転写の永続化可否はFable判断。
