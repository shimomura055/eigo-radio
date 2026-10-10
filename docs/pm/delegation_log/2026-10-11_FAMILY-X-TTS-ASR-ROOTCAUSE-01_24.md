# FAMILY-X-TTS-ASR-ROOTCAUSE-01 委任_24 (OPEN-258 設計・リスク評価のみ)

- 日付: 2026-10-11 / 到達点: DESIGN_READY_FOR_REVIEW(Production未承認・未実装)
- 課金API: 0(ローカルfaster-whisper tiny/small/mediumと純粋関数のみ。medium modelは無料DL)
- 成果物: er053_output/family_x_tts_asr_rootcause_01/OPEN258_DESIGN_01.md、OPEN258_OFFLINE_EVIDENCE_01.json
- 要点: Primary NG(TRUE_CONTENT_MISMATCH)時にAzure Secondaryを1回だけ独立確認(SCG)。挿入点 er007_ja_secondary_asr_01.py L128直前。PASSはSecondaryがEXACT/NORMALIZED一致のみ、Phrase List禁止、数字/否定/助詞/日付は除外。
- offline検証: META 3 attemptをwhisper 3モデルで転写 -> attempt2/3は全モデル「出演」、attempt1は「出面」。「出現」は0。
- 影響試算: JA 630 attempt/468群、現行コード再判定でTCM 48件/34群、V1で再生成16回回避・Azure44回約$0.075(約¥11)、費用純増約¥10、時間約32-45分短縮。
- 変更なし: Productionコード/Prompt/SSOT/er020_*/OPEN256_*
- 残る判断: SCG方針V1/V2/V3、誤PASS許容水準(14件試聴)、Azure検証承認(約¥0.3-0.8)、whisper 2-of-3採否、助詞/日付除外
