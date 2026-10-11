# FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_06(fallback経路での承認Style維持=案1)
- 日付: 2026-10-11 / 実行層: Sonnet / API課金0(LLM/TTS/ASR呼び出しなし、probeはsocket遮断で検証)
- worktree/branch: `C:\Users\tensh\eigo-radio-tone-fb` / `feature/coffee-new-tone-fallback-01`(起点 1b35eb90、mainや`feature/coffee-new-tone-01`へはmerge未実施)
- 根拠: ユーザー正式決定③(fallbackでも新Style維持必須・救済能力維持必須)+Opus条件AレビューGO with required fixes(B1〜B6+resume追加)
- 変更: crosslevel/repro01/n3_tts/voice01/news_tail_fix/er019 audio runner/styles(helper)に既定None引数`fallback_style_prefix`を新設し、runnerが対象segment(J2/E2_UPBEAT/F1_5)のみに渡す。証跡4項目記録、crosslevel model名是正、style_version v5 bump。
- test: `er003_fallback_style_retention_test_01.py`(28件)、probe: `er003_fallback_style_retention_probe_01.py`→`er053_output/coffee_new_tone_e2e_01/FALLBACK_MOCK_PROBE_01.md`(194行、style不一致0)
- 意図的な期待値更新: `er033_family_x_coffee_new_tone_wiring_01_test_01.VersionGuardTests.test_version_bumped`(v4→v5)のみ
- 設計書追記: `er053_output/coffee_new_tone_e2e_01/FALLBACK_STYLE_RETENTION_DESIGN_01.md` §10
- SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)は不変。Production採用(APPROVED_FOR_PRODUCTION)は人間ユーザー承認事項。
