# FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_01B(2026-10-12、課金JPY0、実装なし)

## SSOT記載行
- DECISION_LOG.md: 末尾(L20589)にP8採用エントリ(APPROVED_FOR_PRODUCTION、Coffee Full Story限定、PD8置換、Production未配線)。
- OPEN_ITEMS.md: OPEN-311 L814(P8採用、残=配線)、OPEN-300 L803(設計書作成、Opus条件A待ち)。いずれも既存行末へ追記。
- CURRENT_SPEC.md: L2609(Coffee限定Style節の直後に追記、Full Story PD8->P8、未配線)。

## 設計書
docs/pm/design/2026-10-12_COFFEE-P8-PRODUCTION-WIRING-DESIGN-01.md
- 重要な現状所見: 現行ProductionのFULL_STORYのStyleは「calm, steady news narration…」でPD8ではない。Style解決はb1/a2各関数のローカル`_role_style`、Std経路は基本Style+減速指示連結(Coffee v3はPD8逐語+生成後6%減速)。Full StoryはMaster Store対象外、reuseは`style_version`(グローバル)+canonical_text。minimal_fallbackは内部別文字列でoverride不可。
- 案1 slug表(自動)/ 案2 明示CLI`--style-profile`+out_dir固定記録 / 案3 sidecar。**推奨=案2、Phase 1=Full Storyのみ**。非影響保証=default素通しでバイト同一、共通定数・グローバルstyle_version・Master Storeキー無変更。
- Opus論点: (1)Phase分割の妥当性 (2)Std逐語+6%減速とA2 Gate/OPEN-270の整合 (3)fallbackはP8非適用(安全装置不変更)で妥当か (4)発音hint追記 (5)固定記録の責務とcache比較フィールド。
- P8原典sha256とWPM guard通過を再計算で確認(402文字)。

## 状態
PRODUCTION_WIRED未達。コード変更・API呼出なし。Opus条件Aレビュー待ち。
